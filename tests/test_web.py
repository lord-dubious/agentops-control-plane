from pathlib import Path

from fastapi.testclient import TestClient

from agentops_control_plane.config import Settings
from agentops_control_plane.main import create_app


def test_dashboard_renders_shell(tmp_path: Path) -> None:
    client = TestClient(create_app(Settings(database_path=tmp_path / "agentops.sqlite3")))

    response = client.get("/")

    assert response.status_code == 200
    assert "AgentOps Control Plane" in response.text
    assert "metrics-grid" in response.text


def test_static_assets_are_served(tmp_path: Path) -> None:
    client = TestClient(create_app(Settings(database_path=tmp_path / "agentops.sqlite3")))

    css = client.get("/static/styles.css")
    js = client.get("/static/app.js")

    assert css.status_code == 200
    assert "mission" in css.text.lower() or "signal-card" in css.text
    assert js.status_code == 200
    assert "loadDashboard" in js.text
