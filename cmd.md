# Command Reference (Local Offline Txt2Txt)

Use these commands from:
/Users/shyam/Projects/Local_AI/txt2txt

## 1) Environment

Activate venv:
source .venv/bin/activate

Deactivate venv:
deactivate

## 2) Ollama Runtime

Check Ollama version:
ollama --version

Start Ollama server (foreground):
ollama serve

Start Ollama as background service on login:
brew services start ollama

Stop Ollama background service:
brew services stop ollama

Check Ollama API health:
curl -sS http://127.0.0.1:11434/api/version

List local models:
ollama list

Pull models:
ollama pull qwen2.5:7b-instruct
ollama pull qwen2.5:3b-instruct

## 3) App API Server (FastAPI)

Start API server:
source .venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000

Start API server with auto-reload (dev):
source .venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Health check API:
curl -s http://127.0.0.1:8000/health | jq

List available models via API:
curl -s http://127.0.0.1:8000/models | jq

## 4) Test Input -> Response

Run txt2txt request:
curl -s http://127.0.0.1:8000/v1/txt2txt \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Explain local offline LLM backend in 3 short points",
    "max_tokens": 120,
    "temperature": 0.2
  }' | jq

## 5) Stop / Kill Commands

Find process using Ollama port:
lsof -nP -iTCP:11434 -sTCP:LISTEN

Find process using API port:
lsof -nP -iTCP:8000 -sTCP:LISTEN

Kill process by PID:
kill <PID>

Force kill process by PID:
kill -9 <PID>

Kill any running Uvicorn app instance:
pkill -f "uvicorn app.main:app"

Kill all Ollama processes:
pkill ollama

## 6) End-to-End Restart (Clean)

1. Stop API server:
pkill -f "uvicorn app.main:app"

2. Stop Ollama (if running in background service):
brew services stop ollama

3. Start Ollama:
ollama serve

4. In another terminal, start API server:
cd /Users/shyam/Projects/Local_AI/txt2txt
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000

5. Test request:
curl -s http://127.0.0.1:8000/v1/txt2txt \
  -H "Content-Type: application/json" \
  -d '{"input_text":"Say hello in one line"}' | jq

## 7) Useful Troubleshooting

If ollama command not found:
command -v ollama
hash -r

If API says address already in use:
lsof -nP -iTCP:8000 -sTCP:LISTEN
kill <PID>

If Ollama says address already in use:
lsof -nP -iTCP:11434 -sTCP:LISTEN
kill <PID>

Run tests:
source .venv/bin/activate && pytest -q
