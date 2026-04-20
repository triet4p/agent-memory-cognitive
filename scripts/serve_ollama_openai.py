"""OpenAI-compatible proxy for Ollama — pure thin host layer for CogMem.

Responsibilities:
  - Forward requests to local Ollama instance(s) with round-robin load balancing
  - Forward Ollama usage stats (prompt_eval_count / eval_count) as OpenAI-style usage

NOT responsible for (handled by CogMem source):
  - Prompt hints / task classification
  - JSON repair of malformed SLM output
  - Temporal hallucination sanitization
  - Fact-type restrictions
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import requests, json, time
import asyncio

app = FastAPI()

OLLAMA_PORTS = [11434]
OLLAMA_INDEX = 0
OLLAMA_LOCK = asyncio.Lock()


async def get_next_ollama_api() -> str:
    global OLLAMA_INDEX
    async with OLLAMA_LOCK:
        port = OLLAMA_PORTS[OLLAMA_INDEX]
        OLLAMA_INDEX = (OLLAMA_INDEX + 1) % len(OLLAMA_PORTS)
        return f"http://127.0.0.1:{port}/api"


@app.get("/v1/models")
async def list_models():
    try:
        ollama_api = await get_next_ollama_api()
        resp = requests.get(f"{ollama_api}/tags", timeout=10)
        models = [
            {"id": m["name"], "object": "model", "created": int(time.time()), "owned_by": "ollama"}
            for m in resp.json().get("models", [])
        ]
        return {"object": "list", "data": models}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model", "llama3")
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    max_tokens = body.get("max_tokens") or body.get("max_completion_tokens") or 4096

    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {
            "num_predict": max_tokens,
            "num_ctx": 32000,
            "temperature": 0.1,
        },
    }

    ollama_api = await get_next_ollama_api()
    print(f"[{time.strftime('%H:%M:%S')}] model={model} max_tokens={max_tokens}")

    if not stream:
        try:
            resp = requests.post(f"{ollama_api}/chat", json=payload, timeout=1800)
            full_content = ""
            prompt_eval_count = 0
            eval_count = 0

            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        full_content += chunk["message"]["content"]
                    if chunk.get("done"):
                        prompt_eval_count = chunk.get("prompt_eval_count", 0)
                        eval_count = chunk.get("eval_count", 0)

            print(full_content)

            return {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": full_content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_eval_count,
                    "completion_tokens": eval_count,
                    "total_tokens": prompt_eval_count + eval_count,
                },
            }
        except Exception as e:
            print(f"[ERROR] {e}")
            return JSONResponse(status_code=500, content={"error": str(e)})
    else:
        def event_stream():
            resp = requests.post(f"{ollama_api}/chat", json=payload, stream=True, timeout=1800)
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        out = {"choices": [{"delta": {"content": chunk["message"]["content"]}}]}
                        yield f"data: {json.dumps(out)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/v1/completions")
async def completions(request: Request):
    body = await request.json()
    model = body.get("model", "llama3")
    prompt = body.get("prompt", "")
    max_tokens = body.get("max_tokens", 4096)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "num_ctx": 32000},
    }
    ollama_api = await get_next_ollama_api()
    try:
        resp = requests.post(f"{ollama_api}/generate", json=payload, timeout=1800)
        content = "".join([json.loads(l).get("response", "") for l in resp.iter_lines() if l])
        return {
            "id": f"cmpl-{int(time.time())}",
            "object": "text_completion",
            "model": model,
            "choices": [{"text": content, "index": 0, "finish_reason": "stop"}],
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
