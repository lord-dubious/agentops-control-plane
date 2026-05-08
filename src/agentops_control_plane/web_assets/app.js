const state = {
  runs: [],
  activeRunId: null,
};

const formatMoney = (value) => `$${Number(value).toFixed(3)}`;
const formatMs = (value) => `${Math.round(Number(value) / 1000)}s`;
const scoreLabel = (value) => `${Math.round(Number(value) * 100)}%`;

async function getJson(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function metricCard(label, value, note) {
  return `<article class="metric-card"><span>${label}</span><strong>${value}</strong><span>${note}</span></article>`;
}

function renderMetrics(summary) {
  document.querySelector('#hero-run-count').textContent = `${summary.run_count} runs observed`;
  document.querySelector('#metrics-grid').innerHTML = [
    metricCard('Runs', summary.run_count, `${summary.completed_count} completed / ${summary.failed_count} failed`),
    metricCard('Average Score', scoreLabel(summary.average_score), 'quality evaluation rollup'),
    metricCard('Total Cost', formatMoney(summary.total_cost_usd), 'deterministic demo estimate'),
    metricCard('Tool Failure Rate', scoreLabel(summary.tool_failure_rate), `${formatMs(summary.average_latency_ms)} avg latency`),
  ].join('');
}

function renderRuns() {
  const list = document.querySelector('#run-list');
  list.innerHTML = state.runs.map((run) => `
    <button class="run-card ${run.id === state.activeRunId ? 'active' : ''}" data-run-id="${run.id}" type="button">
      <strong>${run.agent_name}</strong>
      <small>${run.task}</small>
      <span class="status ${run.status}">${run.status}</span>
    </button>
  `).join('');
  list.querySelectorAll('[data-run-id]').forEach((button) => {
    button.addEventListener('click', () => selectRun(button.dataset.runId));
  });
}

function eventClass(eventType) {
  if (eventType === 'error') return 'error';
  if (eventType === 'retry') return 'retry';
  return '';
}

function renderDetail(detail) {
  const { run, trace, tool_calls: toolCalls, evaluations } = detail;
  document.querySelector('#detail-status').textContent = `${run.status} / ${formatMoney(run.total_cost_usd)} / ${formatMs(run.total_latency_ms)}`;
  document.querySelector('#detail-title').textContent = run.agent_name;
  document.querySelector('#detail-task').textContent = run.task;
  document.querySelector('#score-ring').textContent = scoreLabel(run.score);

  document.querySelector('#timeline').innerHTML = trace.map((event) => `
    <article class="timeline-item ${eventClass(event.event_type)}">
      <div class="meta-row"><span>${event.event_type}</span><span>${new Date(event.timestamp).toLocaleTimeString()}</span></div>
      <p>${event.message}</p>
    </article>
  `).join('');

  document.querySelector('#tool-stack').innerHTML = toolCalls.length ? toolCalls.map((tool) => `
    <article class="tool-card ${tool.status}">
      <div class="meta-row"><span>${tool.tool_name}</span><span>${tool.latency_ms}ms</span></div>
      <p>${tool.output_summary}</p>
      ${tool.error_message ? `<small class="muted">${tool.error_message}</small>` : ''}
    </article>
  `).join('') : '<p class="muted">No tool calls captured for this run.</p>';

  document.querySelector('#eval-stack').innerHTML = evaluations.map((evaluation) => `
    <article class="eval-card">
      <div class="meta-row"><span>${evaluation.criterion}</span><span>${scoreLabel(evaluation.score)}</span></div>
      <div class="eval-bar"><div class="eval-fill" style="width: ${Math.round(evaluation.score * 100)}%"></div></div>
      <p>${evaluation.explanation}</p>
    </article>
  `).join('');
}

async function selectRun(runId) {
  state.activeRunId = runId;
  renderRuns();
  renderDetail(await getJson(`/api/runs/${runId}`));
}

async function loadDashboard(preferredRunId = null) {
  try {
    const [summary, runs] = await Promise.all([
      getJson('/api/metrics/summary'),
      getJson('/api/runs'),
    ]);
    state.runs = runs;
    renderMetrics(summary);
    renderRuns();

    // Default to first run if available and none active
    const preferredExists = runs.some((run) => run.id === preferredRunId);
    const activeExists = runs.some((run) => run.id === state.activeRunId);
    if (preferredExists) {
      await selectRun(preferredRunId);
    } else if (activeExists) {
      await selectRun(state.activeRunId);
    } else if (runs.length > 0) {
      await selectRun(runs[0].id);
    }
  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

const SAMPLE_IMPORT = {
  run: {
    id: 'run_local_import_001',
    agent_name: 'Local Trace Agent',
    task: 'Replay a LangGraph-style trace export through the local importer',
    status: 'completed',
    started_at: '2026-05-08T10:00:00Z',
    ended_at: '2026-05-08T10:01:12Z',
    total_cost_usd: 0.012,
    total_latency_ms: 72000,
    retry_count: 0,
    error_count: 0,
    score: 0.91
  },
  trace: [
    {
      id: 'trace_local_001',
      timestamp: '2026-05-08T10:00:04Z',
      event_type: 'thought',
      message: 'Plan trace replay and identify required evidence.',
      metadata: { framework: 'langgraph', node: 'planner' }
    },
    {
      id: 'trace_local_002',
      timestamp: '2026-05-08T10:00:18Z',
      event_type: 'tool_call',
      message: 'Called repository search node.',
      metadata: { framework: 'langgraph', node: 'research', tool: 'repo_search' }
    }
  ],
  tool_calls: [
    {
      id: 'tool_local_001',
      tool_name: 'repo_search',
      input_summary: 'Search risk-related code paths',
      output_summary: 'Found config and API boundaries',
      latency_ms: 820,
      status: 'success',
      error_message: null
    }
  ],
  evaluations: [
    {
      id: 'eval_local_correctness',
      criterion: 'correctness',
      score: 0.91,
      explanation: 'Grounded in imported trace evidence.'
    }
  ]
};

function initImportUI() {
  const textarea = document.querySelector('#import-json');
  const btn = document.querySelector('#import-btn');
  const status = document.querySelector('#import-status');

  if (textarea) {
    textarea.value = JSON.stringify(SAMPLE_IMPORT, null, 2);
  }

  btn?.addEventListener('click', async () => {
    status.textContent = 'Importing...';
    status.className = 'status-msg';

    try {
      const payload = JSON.parse(textarea.value);
      const result = await getJson('/api/runs/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      status.textContent = 'Success';
      status.className = 'status-msg success';

      await loadDashboard(payload.run.id);
    } catch (err) {
      status.textContent = 'Failed';
      status.className = 'status-msg error';
      console.error('Import error:', err);
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
  initImportUI();

  document.querySelector('#reset-demo').addEventListener('click', async () => {
    await getJson('/api/demo/reset', { method: 'POST' });
    await loadDashboard();
  });
});
