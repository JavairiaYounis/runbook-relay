import os
from datetime import timedelta
from uuid import UUID

import pytest

from runbook_relay.database import create_engine, create_session_factory
from runbook_relay.incidents.repository import IncidentRepository
from runbook_relay.models import Incident, IncidentStatus

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_TESTS") != "1",
    reason="set RUN_POSTGRES_TESTS=1 to run PostgreSQL integration tests",
)


@pytest.mark.asyncio
async def test_postgres_repository_persists_and_retrieves_incident() -> None:
    database_url = os.environ["RUNBOOK_RELAY_DATABASE_URL"]
    assert database_url.startswith("postgresql+asyncpg://"), (
        "PostgreSQL integration tests require a postgresql+asyncpg URL"
    )

    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)
    try:
        async with session_factory() as session:
            repository = IncidentRepository(session)
            created = await repository.add(
                Incident(client_id="postgres-test", description="Repository integration test")
            )
            incident_id = created.id

        async with session_factory() as session:
            retrieved = await IncidentRepository(session).get(incident_id)

        assert isinstance(incident_id, UUID)
        assert retrieved is not None
        assert retrieved.id == incident_id
        assert retrieved.status is IncidentStatus.OPEN
        assert retrieved.created_at.utcoffset() == timedelta(0)
        assert retrieved.updated_at.utcoffset() == timedelta(0)
    finally:
        await engine.dispose()
