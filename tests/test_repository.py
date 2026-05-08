from pathlib import Path

from agentops_control_plane.repository import AgentOpsRepository


def test_repository_seed_is_idempotent(tmp_path: Path) -> None:
    repository = AgentOpsRepository(tmp_path / "agentops.sqlite3")

    repository.ensure_seeded()
    repository.ensure_seeded()

    assert len(repository.list_runs()) == 4


def test_repository_returns_full_run_detail(tmp_path: Path) -> None:
    repository = AgentOpsRepository(tmp_path / "agentops.sqlite3")
    repository.reset_demo_data()
    run = repository.list_runs()[0]

    detail = repository.get_run_detail(run.id)

    assert detail is not None
    assert detail.run.id == run.id
    assert detail.trace
    assert detail.evaluations


def test_metrics_include_failed_tool_rate(tmp_path: Path) -> None:
    repository = AgentOpsRepository(tmp_path / "agentops.sqlite3")
    repository.reset_demo_data()

    summary = repository.metrics_summary()

    assert summary.run_count == 4
    assert summary.tool_failure_rate > 0
    assert summary.average_latency_ms > 0
