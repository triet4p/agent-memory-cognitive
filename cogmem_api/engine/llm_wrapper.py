"""Lightweight LLM wrapper utilities for CogMem retain/search paths."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx

from .response_models import TokenUsage


def sanitize_llm_output(text: str | None) -> str | None:
    """Remove control/surrogate characters that can break JSON decoding."""
    if text is None:
        return None
    if not text:
        return text
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\ud800-\udfff]", "", text)


class OutputTooLongError(Exception):
    """Raised when provider reports generation stopped by length limit."""



def parse_llm_json(raw: str) -> Any:
    """Parse JSON with tolerance for fenced blocks and control chars."""
    text = raw.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", text)
        return json.loads(cleaned)


@dataclass(slots=True)
class LLMConfig:
    """OpenAI-compatible async caller used by retain and search helpers."""

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str | None = None
    timeout: float = 120.0

    async def call(
        self,
        messages: list[dict[str, str]],
        response_format: type | None = None,
        scope: str | None = None,
        temperature: float = 0.1,
        max_completion_tokens: int | None = None,
        return_usage: bool = False,
        skip_validation: bool = False,
        **_: Any,
    ) -> Any:
        """Call chat completions endpoint and optionally parse JSON schema output."""
        del scope

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens

        if response_format is not None and hasattr(response_format, "model_json_schema"):
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "facts",
                    "schema": response_format.model_json_schema(),
                },
            }

        response_json = await self._post_chat_completions(payload)
        usage_json = response_json.get("usage") or {}
        usage = TokenUsage(
            input_tokens=int(usage_json.get("prompt_tokens") or 0),
            output_tokens=int(usage_json.get("completion_tokens") or 0),
            total_tokens=int(usage_json.get("total_tokens") or 0),
        )

        choices = response_json.get("choices") or []
        if not choices:
            parsed: Any = ""
        else:
            choice = choices[0]
            finish_reason = str(choice.get("finish_reason") or "")
            if finish_reason == "length":
                raise OutputTooLongError("LLM output exceeded token limits")

            content = sanitize_llm_output((choice.get("message") or {}).get("content", "")) or ""
            if response_format is None:
                parsed = content
            else:
                parsed_json = parse_llm_json(content)
                if skip_validation:
                    parsed = parsed_json
                elif hasattr(response_format, "model_validate"):
                    parsed = response_format.model_validate(parsed_json).model_dump()
                else:
                    parsed = parsed_json

        if return_usage:
            return parsed, usage
        return parsed

    async def _post_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.base_url:
            raise ValueError("LLM base_url is required for LLMConfig.call")

        base = self.base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            endpoint = base
        elif base.endswith("/v1"):
            endpoint = f"{base}/chat/completions"
        else:
            endpoint = f"{base}/v1/chat/completions"

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
