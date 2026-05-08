"""Deterministic demo data for offline AgentOps portfolio walkthroughs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

BASE_TIME = datetime(2026, 5, 8, 9, 0, tzinfo=UTC)


def demo_runs() -> list[dict[str, Any]]:
    return [
        {
            "id": "run_soc_triage_001",
            "agent_name": "SOC Triage Agent",
            "task": "Investigate suspicious PowerShell alert and draft incident summary",
            "status": "completed",
            "started_at": BASE_TIME,
            "ended_at": BASE_TIME + timedelta(seconds=86),
            "total_cost_usd": 0.038,
            "total_latency_ms": 86_420,
            "retry_count": 1,
            "error_count": 0,
            "score": 0.92,
        },
        {
            "id": "run_repo_docs_017",
            "agent_name": "Documentation Engineer",
            "task": "Inspect repository architecture and produce reviewer notes",
            "status": "completed",
            "started_at": BASE_TIME - timedelta(minutes=24),
            "ended_at": BASE_TIME - timedelta(minutes=22, seconds=5),
            "total_cost_usd": 0.021,
            "total_latency_ms": 115_100,
            "retry_count": 0,
            "error_count": 0,
            "score": 0.88,
        },
        {
            "id": "run_policy_eval_004",
            "agent_name": "Policy Evaluation Agent",
            "task": "Compare generated Kubernetes policy against observed traffic",
            "status": "retried",
            "started_at": BASE_TIME - timedelta(hours=1, minutes=4),
            "ended_at": BASE_TIME - timedelta(hours=1, minutes=1),
            "total_cost_usd": 0.044,
            "total_latency_ms": 173_230,
            "retry_count": 2,
            "error_count": 1,
            "score": 0.79,
        },
        {
            "id": "run_data_analysis_011",
            "agent_name": "Data Analyst Agent",
            "task": "Answer revenue variance question using DuckDB query tools",
            "status": "failed",
            "started_at": BASE_TIME - timedelta(hours=2),
            "ended_at": BASE_TIME - timedelta(hours=1, minutes=58, seconds=42),
            "total_cost_usd": 0.013,
            "total_latency_ms": 78_610,
            "retry_count": 1,
            "error_count": 2,
            "score": 0.41,
        },
    ]


def demo_trace_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for run in demo_runs():
        run_id = run["id"]
        started_at = run["started_at"]
        events.extend(
            [
                {
                    "id": f"{run_id}_trace_001",
                    "run_id": run_id,
                    "timestamp": started_at,
                    "event_type": "thought",
                    "message": "Plan run, identify required tools, and set success criteria.",
                    "metadata": {"phase": "planning"},
                },
                {
                    "id": f"{run_id}_trace_002",
                    "run_id": run_id,
                    "timestamp": started_at + timedelta(seconds=12),
                    "event_type": "tool_call",
                    "message": "Call retrieval tool for evidence and related context.",
                    "metadata": {"tool": "evidence_search"},
                },
                {
                    "id": f"{run_id}_trace_003",
                    "run_id": run_id,
                    "timestamp": started_at + timedelta(seconds=35),
                    "event_type": "tool_result",
                    "message": "Summarize tool output and attach confidence notes.",
                    "metadata": {"tokens": 1120},
                },
            ]
        )
        if run["error_count"]:
            events.append(
                {
                    "id": f"{run_id}_trace_004",
                    "run_id": run_id,
                    "timestamp": started_at + timedelta(seconds=52),
                    "event_type": "retry" if run["status"] == "retried" else "error",
                    "message": "Tool boundary returned incomplete data; retry with narrower input.",
                    "metadata": {"retry_count": run["retry_count"]},
                }
            )
        events.append(
            {
                "id": f"{run_id}_trace_005",
                "run_id": run_id,
                "timestamp": started_at + timedelta(seconds=70),
                "event_type": "evaluation",
                "message": "Score response against correctness, safety, latency, and tool efficiency.",
                "metadata": {"score": run["score"]},
            }
        )
    return events


def demo_tool_calls() -> list[dict[str, Any]]:
    return [
        {
            "id": "tool_001",
            "run_id": "run_soc_triage_001",
            "tool_name": "evidence_search",
            "input_summary": "PowerShell alert hash, host, parent process",
            "output_summary": "Matched prior alert cluster and suspicious encoded command pattern",
            "latency_ms": 940,
            "status": "success",
            "error_message": None,
        },
        {
            "id": "tool_002",
            "run_id": "run_soc_triage_001",
            "tool_name": "timeline_builder",
            "input_summary": "Endpoint events for 30 minute window",
            "output_summary": "Built six-step timeline with initial script execution and network beacon",
            "latency_ms": 1320,
            "status": "success",
            "error_message": None,
        },
        {
            "id": "tool_003",
            "run_id": "run_policy_eval_004",
            "tool_name": "policy_diff",
            "input_summary": "Generated policy YAML and observed flows",
            "output_summary": "First attempt lacked DNS egress allowance; retry generated bounded exception",
            "latency_ms": 2210,
            "status": "failed",
            "error_message": "Missing DNS egress caused validation failure",
        },
        {
            "id": "tool_004",
            "run_id": "run_data_analysis_011",
            "tool_name": "duckdb_query",
            "input_summary": "Revenue variance by segment",
            "output_summary": "Query rejected because source table was not loaded",
            "latency_ms": 410,
            "status": "failed",
            "error_message": "table revenue_events does not exist",
        },
    ]


def demo_evaluations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    criteria = {
        "correctness": "Matches evidence and avoids unsupported claims.",
        "safety": "Flags uncertainty and avoids unsafe automation.",
        "tool_efficiency": "Uses the smallest useful tool set.",
        "latency": "Completes within the target response budget.",
    }
    for run in demo_runs():
        for index, (criterion, explanation) in enumerate(criteria.items(), start=1):
            penalty = 0.04 * (index - 1) + (0.18 if run["status"] == "failed" else 0)
            rows.append(
                {
                    "id": f"{run['id']}_eval_{criterion}",
                    "run_id": run["id"],
                    "criterion": criterion,
                    "score": max(0.0, round(run["score"] - penalty, 2)),
                    "explanation": explanation,
                }
            )
    return rows
