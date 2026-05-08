"""FastAPI routes for agent observability data."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from agentops_control_plane.models import (
    AgentRun,
    MetricsSummary,
    RunDetail,
    TraceImportRequest,
    TraceImportResult,
)
from agentops_control_plane.repository import AgentOpsRepository

router = APIRouter(prefix="/api", tags=["agentops"])


def get_repository(request: Request) -> AgentOpsRepository:
    return request.app.state.repository


RepositoryDep = Annotated[AgentOpsRepository, Depends(get_repository)]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/runs", response_model=list[AgentRun])
def list_runs(repository: RepositoryDep) -> list[AgentRun]:
    return repository.list_runs()


@router.get("/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str, repository: RepositoryDep) -> RunDetail:
    detail = repository.get_run_detail(run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return detail


@router.get("/metrics/summary", response_model=MetricsSummary)
def metrics_summary(repository: RepositoryDep) -> MetricsSummary:
    return repository.metrics_summary()


@router.post("/runs/import", response_model=TraceImportResult)
def import_run(payload: TraceImportRequest, repository: RepositoryDep) -> TraceImportResult:
    detail = payload.to_run_detail()
    repository.import_run_detail(detail)
    return TraceImportResult(
        run_id=detail.run.id,
        trace_events=len(detail.trace),
        tool_calls=len(detail.tool_calls),
        evaluations=len(detail.evaluations),
        summary=repository.metrics_summary(),
    )


@router.post("/demo/reset", response_model=MetricsSummary)
def reset_demo_data(repository: RepositoryDep) -> MetricsSummary:
    repository.reset_demo_data()
    return repository.metrics_summary()
