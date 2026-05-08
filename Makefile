.PHONY: dev test lint format

dev:
	uv run uvicorn agentops_control_plane.main:app --reload

test:
	uv run pytest tests/ --cov=agentops_control_plane --cov-report=term-missing

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
