from pathlib import Path

from fastapi.testclient import TestClient

from agentops_control_plane.config import Settings
from agentops_control_plane.main import create_app


def make_client(tmp_path: Path) -> TestClient:
    app = create_app(Settings(database_path=tmp_path / "agentops.sqlite3"))
    return TestClient(app)


def test_health_endpoint(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_runs_are_seeded(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/runs")

    assert response.status_code == 200
    runs = response.json()
    assert len(runs) == 4
    assert {run["status"] for run in runs} >= {"completed", "failed", "retried"}


def test_run_detail_contains_trace_tools_and_evaluations(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    run_id = client.get("/api/runs").json()[0]["id"]

    response = client.get(f"/api/runs/{run_id}")

    assert response.status_code == 200
    detail = response.json()
    assert detail["run"]["id"] == run_id
    assert detail["trace"]
    assert detail["evaluations"]


def test_missing_run_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/runs/not-a-run")

    assert response.status_code == 404


def test_metrics_summary_rolls_up_demo_data(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/metrics/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["run_count"] == 4
    assert summary["failed_count"] == 1
    assert summary["total_cost_usd"] > 0
    assert 0 <= summary["tool_failure_rate"] <= 1


def test_demo_reset_restores_seed_data(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post("/api/demo/reset")

    assert response.status_code == 200
    assert response.json()["run_count"] == 4
