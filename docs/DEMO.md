# Demo Guide

This guide uses deterministic local data. It does not require paid model APIs or external services.

## Run Locally

```bash
uv sync --extra dev
uv run uvicorn agentops_control_plane.main:app --reload
```

Open these URLs:

- Dashboard: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

## Suggested Portfolio Walkthrough

1. Start on the dashboard and point out that the UI is served by the same FastAPI app as the JSON API.
2. Open the metrics cards and explain the aggregate view: cost, latency, failures, and quality score.
3. Select the failed `Data Analyst Agent` run and show how trace events, tool calls, and evaluation scores make the failure reviewable.
4. Select the retried `Policy Evaluation Agent` run and explain how retries and tool errors are visible without reading logs.
5. Use `/docs` to show the typed API surface and the local-first reset endpoint.
6. Click reset in the dashboard to restore deterministic demo data.

## Screenshot Provenance

The screenshot in `docs/assets/dashboard.png` was captured from the real local dashboard running from this repository. It is not a mockup or generated marketing image.

## Useful Commands

```bash
uv run --extra dev ruff check src tests
uv run --extra dev ruff format --check src tests
uv run python -m compileall -q src tests
uv run --extra dev pytest tests/ --cov=agentops_control_plane --cov-report=term-missing
```

## Current Limits

- Seeded traces represent realistic operational shapes but are not collected from a live provider.
- There is no authentication layer yet.
- The dashboard does not persist new runs from the browser.
- The next meaningful extension would be an ingestion endpoint for external agent frameworks plus tenant-aware storage controls.
