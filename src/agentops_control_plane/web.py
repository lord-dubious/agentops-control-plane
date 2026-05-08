"""Browser dashboard routes for the AgentOps Control Plane."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

ASSET_ROOT = Path(__file__).parent / "web_assets"


@router.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse((ASSET_ROOT / "index.html").read_text())
