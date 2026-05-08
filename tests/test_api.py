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
    assert len(runs) == 14
    assert {run["status"] for run in runs} >= {"completed", "failed", "retried"}
    assert any(run["agent_name"] == "Semantic Video Search Agent" for run in runs)


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
    assert summary["run_count"] == 14
    assert summary["failed_count"] == 1
    assert summary["total_cost_usd"] > 0
    assert 0 <= summary["tool_failure_rate"] <= 1


def test_import_run_persists_trace_payload(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    payload = {
        "run": {
            "id": "run_langgraph_import_001",
            "agent_name": "LangGraph Import Agent",
            "task": "Replay a real trace export through the AgentOps importer",
            "status": "completed",
            "started_at": "2026-05-08T10:00:00Z",
            "ended_at": "2026-05-08T10:01:12Z",
            "total_cost_usd": 0.012,
            "total_latency_ms": 72_000,
            "retry_count": 0,
            "error_count": 0,
            "score": 0.91,
        },
        "trace": [
            {
                "id": "trace_langgraph_001",
                "timestamp": "2026-05-08T10:00:04Z",
                "event_type": "tool_call",
                "message": "Called repository search node",
                "metadata": {"framework": "langgraph", "node": "research"},
            }
        ],
        "tool_calls": [
            {
                "id": "tool_langgraph_001",
                "tool_name": "repo_search",
                "input_summary": "Search risk-related code paths",
                "output_summary": "Found config and API boundaries",
                "latency_ms": 820,
                "status": "success",
                "error_message": None,
            }
        ],
        "evaluations": [
            {
                "id": "eval_langgraph_correctness",
                "criterion": "correctness",
                "score": 0.91,
                "explanation": "Grounded in imported trace evidence.",
            }
        ],
    }

    response = client.post("/api/runs/import", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["run_id"] == "run_langgraph_import_001"
    assert result["trace_events"] == 1
    assert result["tool_calls"] == 1
    assert result["evaluations"] == 1
    assert result["summary"]["run_count"] == 15

    detail = client.get("/api/runs/run_langgraph_import_001").json()
    assert detail["trace"][0]["metadata"] == {"framework": "langgraph", "node": "research"}
    assert detail["tool_calls"][0]["tool_name"] == "repo_search"


def test_import_run_replaces_existing_payload(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    payload = {
        "run": {
            "id": "run_replace_001",
            "agent_name": "Import Agent",
            "task": "First import",
            "status": "running",
            "started_at": "2026-05-08T10:00:00Z",
            "ended_at": None,
            "total_cost_usd": 0,
            "total_latency_ms": 0,
            "retry_count": 0,
            "error_count": 0,
            "score": 0.5,
        },
        "trace": [],
        "tool_calls": [],
        "evaluations": [],
    }

    assert client.post("/api/runs/import", json=payload).status_code == 200
    payload["run"]["task"] = "Replacement import"
    payload["trace"] = [
        {
            "id": "trace_replace_001",
            "timestamp": "2026-05-08T10:00:03Z",
            "event_type": "thought",
            "message": "Replacement trace",
            "metadata": {},
        }
    ]

    response = client.post("/api/runs/import", json=payload)

    assert response.status_code == 200
    detail = client.get("/api/runs/run_replace_001").json()
    assert detail["run"]["task"] == "Replacement import"
    assert len(detail["trace"]) == 1


def test_import_run_rejects_invalid_status(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    response = client.post(
        "/api/runs/import",
        json={
            "run": {
                "id": "run_bad_001",
                "agent_name": "Broken Import",
                "task": "Use an invalid state",
                "status": "unknown",
                "started_at": "2026-05-08T10:00:00Z",
                "ended_at": None,
                "total_cost_usd": 0,
                "total_latency_ms": 0,
                "retry_count": 0,
                "error_count": 0,
                "score": 0.5,
            }
        },
    )

    assert response.status_code == 422


def test_demo_reset_restores_seed_data(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post("/api/demo/reset")

    assert response.status_code == 200
    assert response.json()["run_count"] == 14
