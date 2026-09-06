.PHONY: install run test lint format format-check typecheck check

install:
	uv sync

run:
	uv run uvicorn runbook_relay.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy

check: lint format-check typecheck test
