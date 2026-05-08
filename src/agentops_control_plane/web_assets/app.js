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

async function loadDashboard() {
  const [summary, runs] = await Promise.all([
    getJson('/api/metrics/summary'),
    getJson('/api/runs'),
  ]);
  state.runs = runs;
  state.activeRunId = runs[0]?.id;
  renderMetrics(summary);
  renderRuns();
  if (state.activeRunId) {
    await selectRun(state.activeRunId);
  }
}

document.querySelector('#reset-demo').addEventListener('click', async () => {
  await getJson('/api/demo/reset', { method: 'POST' });
  await loadDashboard();
});

loadDashboard().catch((error) => {
  document.querySelector('#detail-title').textContent = 'Dashboard failed to load';
  document.querySelector('#detail-task').textContent = error.message;
});
