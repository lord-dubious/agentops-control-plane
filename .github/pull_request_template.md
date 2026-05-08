## Summary

-

## Verification

- [ ] `uv run --extra dev ruff check src tests`
- [ ] `uv run --extra dev ruff format --check src tests`
- [ ] `uv run python -m compileall -q src tests`
- [ ] `uv run --extra dev pytest tests/ --cov=agentops_control_plane --cov-report=term-missing`
- [ ] Dashboard/manual review completed when UI changes are included

## Review Notes

- Does this keep the demo local-first and deterministic?
- Are screenshots and docs generated from real project behavior?
- Are any new operational boundaries or limits documented honestly?
