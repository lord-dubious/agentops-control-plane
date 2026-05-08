"""Application entry point for the AgentOps Control Plane."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from agentops_control_plane.api import router as api_router
from agentops_control_plane.config import Settings
from agentops_control_plane.repository import AgentOpsRepository
from agentops_control_plane.web import router as web_router


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
    asset_root = Path(__file__).parent / "web_assets"
    app.mount("/static", StaticFiles(directory=asset_root), name="static")
    app.include_router(web_router)
    app.include_router(api_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run("agentops_control_plane.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run()
