# Architecture

AgentOps Control Plane is a local-first observability surface for agentic systems. The current implementation is intentionally small: a FastAPI app, a SQLite repository, deterministic demo data, and a browser dashboard that renders API responses directly.

## System Diagram

```mermaid
flowchart TB
    classDef client fill:#e0f2fe,stroke:#0369a1,color:#0c4a6e,stroke-width:2px
    classDef api fill:#ecfeff,stroke:#0891b2,color:#164e63,stroke-width:2px
    classDef core fill:#f8fafc,stroke:#475569,color:#0f172a,stroke-width:2px
    classDef store fill:#fef3c7,stroke:#d97706,color:#78350f,stroke-width:2px
    classDef insight fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:2px
    classDef boundary fill:#fee2e2,stroke:#dc2626,color:#7f1d1d,stroke-dasharray: 6 4,stroke-width:2px

    subgraph Browser[Operator Dashboard]
        UI[Dashboard shell<br/>HTML, CSS, JavaScript]:::client
        RunList[Run list and status cards]:::client
        Detail[Trace, tool, and evaluation panels]:::client
    end

    subgraph FastAPI[FastAPI Application]
        Web[Web router<br/>serves dashboard assets]:::api
        API[API router<br/>/api/runs, /api/runs/import, /api/metrics]:::api
        AppState[Application state<br/>repository dependency]:::core
    end

    subgraph Repository[Local Repository Boundary]
        Repo[AgentOpsRepository<br/>sqlite3 adapter]:::core
        Schema[Tables<br/>runs, trace_events, tool_calls, evaluations]:::store
        Seed[Deterministic demo seed<br/>offline portfolio run examples]:::store
        Import[Local JSON trace import<br/>validated with Pydantic]:::store
    end

    subgraph OperationalViews[Reviewable AgentOps Views]
        Runs[AgentRun records<br/>status, cost, latency, retries]:::insight
        Trace[TraceEvent timeline<br/>thought, tool, retry, error, evaluation]:::insight
        Tools[ToolCall audit trail<br/>inputs, outputs, failures, latency]:::insight
        Eval[EvaluationScore rollups<br/>correctness, safety, efficiency]:::insight
        Metrics[MetricsSummary<br/>failure rate, total cost, average latency]:::insight
    end

    subgraph Boundaries[Current Boundaries]
        LocalOnly[Local-first demo data<br/>no provider keys required]:::boundary
        LiveProviders[Live provider ingestion<br/>future extension, not required]:::boundary
    end

    UI -- "fetch JSON" --> API
    UI -- "static assets" --> Web
    RunList -- "select run" --> Detail
    API -- "request-scoped dependency" --> AppState
    AppState -- "query commands" --> Repo
    Repo -- "creates and reads" --> Schema
    Seed -- "idempotent reset" --> Schema
    Import -- "replace one run" --> Schema
    Schema -- "hydrates" --> Runs
    Schema -- "hydrates" --> Trace
    Schema -- "hydrates" --> Tools
    Schema -- "hydrates" --> Eval
    Runs -- "aggregated into" --> Metrics
    Trace -- "shown in" --> Detail
    Tools -- "shown in" --> Detail
    Eval -- "shown in" --> Detail
    LocalOnly -. "documents demo scope" .-> Seed
    LiveProviders -. "explicit non-goal for v0.1" .-> API
```

## Main Components

- `src/agentops_control_plane/main.py` builds the FastAPI app, seeds the local repository, mounts static assets, and includes the API and web routers.
- `src/agentops_control_plane/api.py` defines the typed HTTP surface for health, runs, run detail, metrics, local trace import, and demo reset.
- `src/agentops_control_plane/repository.py` owns SQLite schema creation, deterministic seeding, JSON metadata storage, and model hydration.
- `src/agentops_control_plane/models.py` defines the run, trace, tool-call, evaluation, metrics, and detail response contracts.
- `src/agentops_control_plane/web_assets/` contains the browser dashboard that fetches JSON from the API and renders the operator view.

## Data Flow

1. `create_app()` builds an `AgentOpsRepository` from `Settings` and stores it on `app.state`.
2. `ensure_seeded()` loads deterministic agent runs when the local SQLite database is empty.
3. The dashboard loads `/api/metrics/summary` and `/api/runs` on page start.
4. Selecting a run loads `/api/runs/{run_id}` and renders the trace timeline, tool calls, and evaluation bars.
5. `POST /api/runs/import` validates one local JSON trace, attaches the run id to child rows, and replaces that run transactionally in SQLite.
6. `POST /api/demo/reset` clears and reseeds the local database so the demo can be restored during interviews.

## Local Import Boundary

The import endpoint is designed for local trace exports from agent frameworks. It accepts one run plus optional trace events, tool calls, and evaluation scores. This gives reviewers a realistic extension point without introducing provider SDKs, queues, background workers, or paid APIs.

Imported runs are stored with the same `AgentRun`, `TraceEvent`, `ToolCall`, and `EvaluationScore` models used by seeded demo data, so they immediately appear in the dashboard and metrics rollups.

## Review Boundaries

- The current repo is a local observability demo. It can import local JSON trace exports, but it does not subscribe to live OpenAI, Anthropic, LangGraph, or CrewAI provider webhooks yet.
- No model provider key is required for the seeded demo path.
- SQLite keeps setup simple for portfolio review. A production service would add auth, migrations, background ingestion, tenant isolation, and retention policies.
- The dashboard is intentionally dependency-light: static HTML, CSS, and JavaScript served by FastAPI.
