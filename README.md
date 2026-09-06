# Runbook Relay

Runbook Relay is a configurable AI operations copilot for support teams. Given an
operational incident, it will retrieve relevant procedures, collect permitted diagnostic
evidence, produce a grounded assessment, and escalate when it cannot safely reach a
conclusion.

This repository currently contains **Milestone 1**: the small, tested FastAPI foundation.
It does not yet implement incident persistence, retrieval, tools, or AI workflows, and it
does not claim to be production-ready.

## Current capabilities

- Public health and generated OpenAPI documentation endpoints
- API-key protection for `/api/v1/*`
- Typed environment settings and structured JSON logging
- Consistent JSON authentication errors
- Automated tests, linting, formatting, type checking, and CI

## Local setup

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
uv sync
uv run uvicorn runbook_relay.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API documentation or check health:

```bash
curl http://127.0.0.1:8000/health
```

Run all quality checks with `make check`, or run the equivalent commands from the
`Makefile` individually. On Windows, the `uv run ...` commands work directly in
PowerShell even when `make` is unavailable.

## Configuration

Settings use the `RUNBOOK_RELAY_` prefix. Copy `.env.example` to `.env` and replace its
placeholder API key before starting the service. The application intentionally has no
default API key. Never commit `.env` or real credentials.

## Roadmap

Later milestones add persistent incidents, client-specific policy configuration,
fictional runbook retrieval, read-only diagnostics, a bounded investigation workflow,
and a reproducible evaluation harness.

## License

MIT
