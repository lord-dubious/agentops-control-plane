"""SQLite-backed repository for deterministic AgentOps demo data."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from agentops_control_plane import demo_data
from agentops_control_plane.models import (
    AgentRun,
    EvaluationScore,
    MetricsSummary,
    RunDetail,
    ToolCall,
    TraceEvent,
)


class AgentOpsRepository:
    """Small repository layer around SQLite for agent observability data."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    total_cost_usd REAL NOT NULL,
                    total_latency_ms INTEGER NOT NULL,
                    retry_count INTEGER NOT NULL,
                    error_count INTEGER NOT NULL,
                    score REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS trace_events (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(id),
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(id),
                    tool_name TEXT NOT NULL,
                    input_summary TEXT NOT NULL,
                    output_summary TEXT NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT
                );
                CREATE TABLE IF NOT EXISTS evaluations (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(id),
                    criterion TEXT NOT NULL,
                    score REAL NOT NULL,
                    explanation TEXT NOT NULL
                );
                """
            )

    def reset_demo_data(self) -> None:
        self.initialize()
        with self.connect() as conn:
            for table in ("evaluations", "tool_calls", "trace_events", "runs"):
                conn.execute(f"DELETE FROM {table}")
            self._insert_runs(conn, demo_data.demo_runs())
            self._insert_trace_events(conn, demo_data.demo_trace_events())
            self._insert_tool_calls(conn, demo_data.demo_tool_calls())
            self._insert_evaluations(conn, demo_data.demo_evaluations())

    def import_run_detail(self, detail: RunDetail) -> None:
        """Replace one run and its child rows in a single local transaction."""
        self.initialize()
        run_id = detail.run.id
        with self.connect() as conn:
            for table in ("evaluations", "tool_calls", "trace_events"):
                conn.execute(f"DELETE FROM {table} WHERE run_id = ?", (run_id,))
            conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
            self._insert_runs(conn, [detail.run.model_dump()])
            self._insert_trace_events(conn, [event.model_dump() for event in detail.trace])
            self._insert_tool_calls(conn, [tool.model_dump() for tool in detail.tool_calls])
            self._insert_evaluations(conn, [score.model_dump() for score in detail.evaluations])

    def ensure_seeded(self) -> None:
        self.initialize()
        with self.connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        if count == 0:
            self.reset_demo_data()

    def list_runs(self) -> list[AgentRun]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM runs ORDER BY started_at DESC").fetchall()
        return [self._run_from_row(row) for row in rows]

    def get_run(self, run_id: str) -> AgentRun | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return self._run_from_row(row) if row else None

    def get_run_detail(self, run_id: str) -> RunDetail | None:
        run = self.get_run(run_id)
        if run is None:
            return None
        return RunDetail(
            run=run,
            trace=self.trace_for_run(run_id),
            tool_calls=self.tool_calls_for_run(run_id),
            evaluations=self.evaluations_for_run(run_id),
        )

    def trace_for_run(self, run_id: str) -> list[TraceEvent]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM trace_events WHERE run_id = ? ORDER BY timestamp ASC", (run_id,)
            ).fetchall()
        return [self._trace_from_row(row) for row in rows]

    def tool_calls_for_run(self, run_id: str) -> list[ToolCall]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tool_calls WHERE run_id = ? ORDER BY latency_ms DESC", (run_id,)
            ).fetchall()
        return [ToolCall(**dict(row)) for row in rows]

    def evaluations_for_run(self, run_id: str) -> list[EvaluationScore]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM evaluations WHERE run_id = ? ORDER BY criterion ASC", (run_id,)
            ).fetchall()
        return [EvaluationScore(**dict(row)) for row in rows]

    def metrics_summary(self) -> MetricsSummary:
        runs = self.list_runs()
        all_tools: list[ToolCall] = []
        for run in runs:
            all_tools.extend(self.tool_calls_for_run(run.id))
        run_count = len(runs)
        completed_count = sum(run.status == "completed" for run in runs)
        failed_count = sum(run.status == "failed" for run in runs)
        average_score = round(sum(run.score for run in runs) / run_count, 2) if run_count else 0
        total_cost = round(sum(run.total_cost_usd for run in runs), 3)
        average_latency = (
            int(sum(run.total_latency_ms for run in runs) / run_count) if run_count else 0
        )
        failed_tools = sum(tool.status == "failed" for tool in all_tools)
        tool_failure_rate = round(failed_tools / len(all_tools), 2) if all_tools else 0
        return MetricsSummary(
            run_count=run_count,
            completed_count=completed_count,
            failed_count=failed_count,
            average_score=average_score,
            total_cost_usd=total_cost,
            average_latency_ms=average_latency,
            tool_failure_rate=tool_failure_rate,
        )

    def _insert_runs(self, conn: sqlite3.Connection, rows: Iterable[dict[str, Any]]) -> None:
        for row in rows:
            payload = row.copy()
            payload["started_at"] = payload["started_at"].isoformat()
            payload["ended_at"] = payload["ended_at"].isoformat() if payload["ended_at"] else None
            conn.execute(
                """
                INSERT INTO runs VALUES (
                    :id, :agent_name, :task, :status, :started_at, :ended_at,
                    :total_cost_usd, :total_latency_ms, :retry_count, :error_count, :score
                )
                """,
                payload,
            )

    def _insert_trace_events(
        self, conn: sqlite3.Connection, rows: Iterable[dict[str, Any]]
    ) -> None:
        for row in rows:
            payload = row.copy()
            payload["timestamp"] = payload["timestamp"].isoformat()
            payload["metadata_json"] = json.dumps(payload.pop("metadata"), sort_keys=True)
            conn.execute(
                """
                INSERT INTO trace_events VALUES (
                    :id, :run_id, :timestamp, :event_type, :message, :metadata_json
                )
                """,
                payload,
            )

    def _insert_tool_calls(self, conn: sqlite3.Connection, rows: Iterable[dict[str, Any]]) -> None:
        for row in rows:
            conn.execute(
                """
                INSERT INTO tool_calls VALUES (
                    :id, :run_id, :tool_name, :input_summary, :output_summary,
                    :latency_ms, :status, :error_message
                )
                """,
                row,
            )

    def _insert_evaluations(self, conn: sqlite3.Connection, rows: Iterable[dict[str, Any]]) -> None:
        for row in rows:
            conn.execute(
                "INSERT INTO evaluations VALUES (:id, :run_id, :criterion, :score, :explanation)",
                row,
            )

    def _run_from_row(self, row: sqlite3.Row) -> AgentRun:
        payload = dict(row)
        payload["started_at"] = datetime.fromisoformat(payload["started_at"])
        payload["ended_at"] = (
            datetime.fromisoformat(payload["ended_at"]) if payload["ended_at"] else None
        )
        return AgentRun(**payload)

    def _trace_from_row(self, row: sqlite3.Row) -> TraceEvent:
        payload = dict(row)
        payload["timestamp"] = datetime.fromisoformat(payload["timestamp"])
        payload["metadata"] = json.loads(payload.pop("metadata_json"))
        return TraceEvent(**payload)
