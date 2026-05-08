"""Application entry point for the AgentOps Control Plane."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from agentops_control_plane.api import router as api_router
from agentops_control_plane.config import Settings
from agentops_control_plane.repository import AgentOpsRepository


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    repository = AgentOpsRepository(resolved_settings.database_path)
    repository.ensure_seeded()

    app = FastAPI(
        title="AgentOps Control Plane",
        summary="Inspect AI agent runs, traces, tool calls, evaluations, and cost metrics.",
        version="0.1.0",
    )
    app.state.repository = repository
    app.include_router(api_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run("agentops_control_plane.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run()
