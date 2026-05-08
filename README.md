# AgentOps Control Plane

Local-first dashboard for inspecting AI agent runs, trace timelines, tool calls, evaluation scores, retries, and cost/latency metrics.

This project is designed as a portfolio-grade AI engineering system: it demonstrates observability boundaries for agentic software without requiring paid model APIs for the demo path.

## What Works Today

- FastAPI backend with typed API responses
- SQLite repository seeded with deterministic demo agent runs
- Run detail API with trace events, tool calls, and evaluation scores
- Metrics API for cost, latency, failure-rate, and quality-score rollups
- CI with Ruff, formatting, compile checks, pytest, and coverage

## Quick Start

```bash
uv sync --extra dev
uv run uvicorn agentops_control_plane.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to inspect the API.

## API Surface

- `GET /api/health`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/metrics/summary`
- `POST /api/demo/reset`

## Current Limits

- Demo data is deterministic and local-only.
- No real provider keys are required or used.
- The first implementation focuses on observability data and API boundaries; the browser GUI is added in a follow-up PR.
