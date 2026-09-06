# Runbook Relay

Runbook Relay is a configurable AI operations copilot for support teams. Given an
operational incident, it will retrieve relevant procedures, collect permitted diagnostic
evidence, produce a grounded assessment, and escalate when it cannot safely reach a
conclusion.

This repository currently contains the tested API foundation and PostgreSQL-backed incident
creation and retrieval. It does not yet implement retrieval, diagnostic tools, or AI
workflows, and it does not claim to be production-ready.

## Current capabilities

- Public health and generated OpenAPI documentation endpoints
- API-key protection for `/api/v1/*`
- Typed environment settings and structured JSON logging
- Consistent JSON authentication errors
- Persistent incident creation and retrieval
- Async SQLAlchemy sessions and Alembic migrations
- Automated tests, linting, formatting, type checking, and CI

## Local setup

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
# Replace both password placeholders with the same local-only value.
uv sync
docker compose up --build
```

Open `http://127.0.0.1:8000/docs` for the API documentation or check health:

```bash
curl http://127.0.0.1:8000/health
```

To run the API outside Compose while PostgreSQL is available:

```bash
uv run alembic upgrade head
uv run uvicorn runbook_relay.main:app --reload
```

## Incident API

Create an incident:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-local-api-key" \
  -d '{"client_id":"northstar-connect","description":"Abandoned calls increased."}'
```

Retrieve it using the returned UUID:

```bash
curl http://127.0.0.1:8000/api/v1/incidents/INCIDENT_ID \
  -H "X-API-Key: your-local-api-key"
```

Run all quality checks with `make check`, or run the equivalent commands from the
`Makefile` individually. On Windows, the `uv run ...` commands work directly in
PowerShell even when `make` is unavailable.

The normal test suite uses isolated SQLite databases. The PostgreSQL repository test is
explicitly enabled after applying migrations:

```bash
RUN_POSTGRES_TESTS=1 uv run pytest tests/test_postgres_integration.py -v
```

It reads `RUNBOOK_RELAY_DATABASE_URL` and never falls back to SQLite.

## Configuration

Settings use the `RUNBOOK_RELAY_` prefix. Copy `.env.example` to `.env` and replace its
placeholder API and database credentials before starting the service. The application
intentionally has no default credentials. Never commit `.env` or real credentials.

## Roadmap

Later milestones add client-specific policy configuration, fictional runbook retrieval,
read-only diagnostics, a bounded investigation workflow, and a reproducible evaluation
harness.

## License

MIT
