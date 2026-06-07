# Local Offline Txt2Txt API

Lightweight FastAPI service for text-to-text generation using locally hosted models via Ollama.

This project is designed for offline-first usage on a local machine or private server:
- No cloud API dependency for inference
- No external LLM endpoint required
- Local HTTP API for easy integration with other applications

## Features

- FastAPI backend for local text generation
- Ollama integration with localhost safety validation
- Primary/fallback model routing
- Retry and timeout handling
- Input and token limits
- Health and model discovery endpoints
- Basic pytest coverage for API behavior

## How It Works

Application client -> FastAPI service -> Ollama runtime -> Local model

Default runtime endpoints:
- Ollama: `http://127.0.0.1:11434`
- API service: `http://127.0.0.1:8000`

## Requirements

- Python 3.9+
- Ollama installed and running
- At least one local instruct model pulled in Ollama

Install Ollama (example on macOS):

```bash
brew install ollama
```

Start Ollama:

```bash
ollama serve
```

Pull models (example):

```bash
ollama pull qwen2.5:7b-instruct
ollama pull qwen2.5:3b-instruct
```

## Quick Start

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

4. Test generation:

```bash
curl -s http://127.0.0.1:8000/v1/txt2txt \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Explain the benefits of running LLMs offline in 3 concise points"
  }'
```

## API Endpoints

### `POST /v1/txt2txt`

Generate text from input.

Request body:
- `input_text` (required)
- `model` (optional)
- `max_tokens` (optional)
- `temperature` (optional)
- `system_prompt` (optional)

Response includes:
- `output_text`
- `model_used`
- `fallback_used`
- `latency_ms`
- token usage fields

### `GET /health`

Returns API health and Ollama reachability.

### `GET /models`

Returns locally available models from Ollama.

## Configuration

Environment variables:

- `OLLAMA_BASE_URL` (default: `http://127.0.0.1:11434`)
- `PRIMARY_MODEL` (default: `qwen2.5:7b-instruct`)
- `FALLBACK_MODEL` (default: `qwen2.5:3b-instruct`)
- `REQUEST_TIMEOUT_SECONDS` (default: `45`)
- `RETRY_ATTEMPTS` (default: `1`)
- `MAX_INPUT_CHARS` (default: `12000`)
- `DEFAULT_MAX_TOKENS` (default: `512`)
- `MAX_ALLOWED_TOKENS` (default: `2048`)
- `DEFAULT_TEMPERATURE` (default: `0.2`)
- `MAX_CONCURRENT_REQUESTS` (default: `4`)

Important:
- `OLLAMA_BASE_URL` is validated to allow localhost-only hosts (`localhost` or `127.0.0.1`) for safer local deployment defaults.

## Offline / Air-Gapped Usage

After initial setup and model download, inference can run fully offline.

Checklist:
1. Install dependencies and pull model(s) while online.
2. Verify models exist with `ollama list`.
3. Disconnect external network.
4. Confirm local generation still works via CLI and API.

## Deployment Notes (Local Server)

- Keep Ollama and this API on private network or localhost when possible.
- If exposed beyond localhost, add authentication, TLS, and network controls.
- For internal server use, run behind a reverse proxy and process supervisor.

## Development

Run tests:

```bash
pytest -q
```

Useful commands are documented in [cmd.md](cmd.md).

## Project Structure

- `app/main.py`: FastAPI app and routes
- `app/service.py`: generation orchestration, retries, fallback
- `app/ollama_client.py`: Ollama HTTP client
- `app/config.py`: environment-driven settings and validation
- `app/schemas.py`: request and response schemas
- `tests/test_api.py`: API tests

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
