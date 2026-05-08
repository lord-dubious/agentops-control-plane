"""Deterministic demo data for offline AgentOps portfolio walkthroughs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

BASE_TIME = datetime(2026, 5, 8, 9, 0, tzinfo=UTC)


def _portfolio_runs() -> list[dict[str, Any]]:
    projects = [
        (
            "run_portfolio_malware_001",
            "Malware Analysis Pipeline Agent",
            "Review Cuckoo, Magika, Gemini, and YARA degraded-mode boundaries",
            "completed",
            3,
            0.031,
            94_500,
            0.91,
        ),
        (
            "run_portfolio_k8s_001",
            "Kubernetes Policy Agent",
            "Inspect NetworkPolicy generation metadata and GitOps dry-run state",
            "completed",
            6,
            0.026,
            88_200,
            0.9,
        ),
        (
            "run_portfolio_contract_001",
            "Smart Contract Auditor Agent",
            "Audit Slither, Gemini enrichment, and Foundry verification fallbacks",
            "completed",
            9,
            0.034,
            111_700,
            0.89,
        ),
        (
            "run_portfolio_siem_001",
            "SIEM Enrichment Agent",
            "Inspect Redis degradation metadata and firewall suggestion review gates",
            "completed",
            12,
            0.022,
            79_900,
            0.88,
        ),
        (
            "run_portfolio_swarm_001",
            "Coding Swarm Review Agent",
            "Review generated-code provenance and Docker sandbox execution metadata",
            "retried",
            15,
            0.041,
            142_400,
            0.84,
        ),
        (
            "run_portfolio_video_001",
            "Semantic Video Search Agent",
            "Inspect LanceDB dependency boundaries and explicit in-memory test store usage",
            "completed",
            18,
            0.019,
            73_250,
            0.87,
        ),
        (
            "run_portfolio_voice_001",
            "Realtime Voice Agent",
            "Review explicit Gemini mock mode, VAD fallback, and TTS error metadata",
            "completed",
            21,
            0.024,
            97_300,
            0.86,
        ),
        (
            "run_portfolio_research_001",
            "Research Team Agent",
            "Inspect SearXNG, FlashRank, and Gemini fallback provenance in reports",
            "completed",
            24,
            0.029,
            105_600,
            0.89,
        ),
        (
            "run_portfolio_pentest_001",
            "Cognitive Pentesting Agent",
            "Review authorization guardrails and OWASP ZAP phase failure handling",
            "completed",
            27,
            0.028,
            99_800,
            0.9,
        ),
        (
            "run_portfolio_data_001",
            "Autonomous Data Analyst Agent",
            "Inspect DuckDB load metadata and Pydantic AI degraded analysis boundaries",
            "completed",
            30,
            0.018,
            69_400,
            0.88,
        ),
    ]
    rows: list[dict[str, Any]] = []
    for run_id, agent_name, task, status, offset, cost, latency, score in projects:
        rows.append(
            {
                "id": run_id,
                "agent_name": agent_name,
                "task": task,
                "status": status,
                "started_at": BASE_TIME - timedelta(minutes=offset),
                "ended_at": BASE_TIME - timedelta(minutes=offset) + timedelta(milliseconds=latency),
                "total_cost_usd": cost,
                "total_latency_ms": latency,
                "retry_count": 1 if status == "retried" else 0,
                "error_count": 1 if status == "retried" else 0,
                "score": score,
            }
        )
    return rows


def demo_runs() -> list[dict[str, Any]]:
    base_runs = [
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
    return base_runs + _portfolio_runs()


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
    rows = [
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
    for run in _portfolio_runs():
        rows.extend(
            [
                {
                    "id": f"{run['id']}_tool_repo_review",
                    "run_id": run["id"],
                    "tool_name": "portfolio_repo_review",
                    "input_summary": "Inspect merged PRs, README, docs, and CI status",
                    "output_summary": "Found portfolio hardening evidence and reviewable boundaries",
                    "latency_ms": 820,
                    "status": "success",
                    "error_message": None,
                },
                {
                    "id": f"{run['id']}_tool_ci_check",
                    "run_id": run["id"],
                    "tool_name": "github_checks",
                    "input_summary": "Read latest CI and merge state for the project",
                    "output_summary": "Confirmed checks, PR history, and remaining limitations",
                    "latency_ms": 640,
                    "status": "failed" if run["status"] == "retried" else "success",
                    "error_message": "Initial review needed a retry for sandbox metadata"
                    if run["status"] == "retried"
                    else None,
                },
            ]
        )
    return rows


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
