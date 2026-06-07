# Technical Design Document (TDD)

## Project
Offline local text-to-text LLM backend for Apple Silicon (M5), callable by local apps via localhost API.

## Goal
- Run fully offline after initial setup.
- Provide stable local API for other local apps.
- Keep implementation simple and reliable.

## Scope
In scope:
- Local model runtime
- Local API endpoint layer
- Model routing (primary + fallback)
- Reliability, logging, health checks

Out of scope:
- Frontend UI
- Cloud APIs
- Remote hosting

## Architecture
Local App -> Local API Service -> Local Model Runtime -> Response

- API is localhost only.
- No internet calls during inference.

## Runtime and Models
- Primary runtime: Ollama
- Primary model: 7B to 8B instruct model
- Fallback model: smaller fast instruct model

Selection criteria:
- Quality on real prompts
- Low latency
- Stable structured outputs

## API Design
Core endpoint:
- POST /v1/txt2txt

Supporting endpoints:
- GET /health
- GET /models

Request essentials:
- input text
- model override optional
- max tokens
- temperature

Response essentials:
- output text
- model used
- latency
- token usage
- status

## Reliability
- Request timeout
- Limited retries for transient failures
- One-step fallback model routing
- Queue limit and overload response

## Offline Enforcement
- Pre-download all model artifacts
- Localhost-only API binding
- No remote endpoint config
- Offline validation test with Wi-Fi off

## Security
- Keep service local only
- Do not expose ports externally
- Minimal log retention
- Redact sensitive data in logs

## Observability
Track:
- p50 and p95 latency
- error rate
- timeout rate
- fallback rate
- request volume

## Testing
- Functional: response quality and format
- Non-functional: latency and concurrency
- Failure tests: timeout, runtime crash, overload
- Offline tests: full flow with network disabled

## Milestones
1. Baseline MVP with one model and local API
2. Add reliability controls and health checks
3. Add fallback model routing
4. Complete offline validation and benchmark pass
5. Finalize API contract for multi-app usage

## Risks
- Model quality mismatch for domain tasks
- Latency spikes under parallel requests
- Memory pressure with larger models

Mitigation:
- Keep fallback model
- Cap concurrency
- Use benchmark gate before model changes

## Success Criteria
- 100% local inference with internet disabled
- Stable API responses for target prompts
- Meets defined p95 latency target
- No cloud dependency at runtime
