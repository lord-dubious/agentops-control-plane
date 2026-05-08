"""Typed API models for agent observability data."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    """Lifecycle state for an agent run."""

    COMPLETED = "completed"
    RUNNING = "running"
    FAILED = "failed"
    RETRIED = "retried"


class TraceEventType(StrEnum):
    """Kinds of trace events shown in the run timeline."""

    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    RETRY = "retry"
    ERROR = "error"
    EVALUATION = "evaluation"


class ToolStatus(StrEnum):
    """Result state for a tool invocation."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentRun(BaseModel):
    """Summary row for one observed agent execution."""

    id: str
    agent_name: str
    task: str
    status: RunStatus
    started_at: datetime
    ended_at: datetime | None = None
    total_cost_usd: float = Field(ge=0)
    total_latency_ms: int = Field(ge=0)
    retry_count: int = Field(ge=0)
    error_count: int = Field(ge=0)
    score: float = Field(ge=0, le=1)


class TraceEvent(BaseModel):
    """Timeline event for a run."""

    id: str
    run_id: str
    timestamp: datetime
    event_type: TraceEventType
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """Tool call metadata captured during a run."""

    id: str
    run_id: str
    tool_name: str
    input_summary: str
    output_summary: str
    latency_ms: int = Field(ge=0)
    status: ToolStatus
    error_message: str | None = None


class EvaluationScore(BaseModel):
    """Evaluation score attached to a run."""

    id: str
    run_id: str
    criterion: str
    score: float = Field(ge=0, le=1)
    explanation: str


class MetricsSummary(BaseModel):
    """Rollup metrics for dashboard cards."""

    run_count: int
    completed_count: int
    failed_count: int
    average_score: float
    total_cost_usd: float
    average_latency_ms: int
    tool_failure_rate: float


class RunDetail(BaseModel):
    """Full run view consumed by the run detail page and API."""

    run: AgentRun
    trace: list[TraceEvent]
    tool_calls: list[ToolCall]
    evaluations: list[EvaluationScore]


def utcnow() -> datetime:
    """Return a timezone-aware timestamp for deterministic seed offsets."""

    return datetime.now(tz=UTC)
