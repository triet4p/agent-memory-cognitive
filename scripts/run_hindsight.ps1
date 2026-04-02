# 1. Gán URL Ngrok (Đảm bảo có /v1 ở cuối để khớp với script FastAPI trên Kaggle)
$NGROK_URL="https://unvacillating-braden-worriless.ngrok-free.dev/v1"

# 2. Chạy Docker Hindsight
docker run --rm -it --pull always -p 8888:8888 -p 9999:9999 `
  -e HINDSIGHT_API_LLM_PROVIDER=openai `
  -e HINDSIGHT_API_LLM_BASE_URL=$NGROK_URL `
  -e HINDSIGHT_API_LLM_API_KEY=ollama `
  -e HINDSIGHT_API_LLM_MODEL="ministral3-3b" `
  -e HINDSIGHT_API_RETAIN_MAX_COMPLETION_TOKENS=13000 `
  -e HINDSIGHT_API_LLM_TIMEOUT=600 `
  -e HINDSIGHT_API_RETAIN_LLM_TIMEOUT=600 `
  -e HINDSIGHT_API_LOG_LEVEL=info `
  -v "${HOME}/.hindsight-docker:/home/hindsight/.pg0" `
  ghcr.io/vectorize-io/hindsight:latest