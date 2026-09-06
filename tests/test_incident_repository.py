from datetime import UTC

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from runbook_relay.database import Base, create_session_factory
from runbook_relay.incidents.repository import IncidentRepository
from runbook_relay.models import Incident, IncidentStatus


@pytest.mark.asyncio
async def test_repository_persists_and_retrieves_incident() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        repository = IncidentRepository(session)
        created = await repository.add(Incident(client_id="client-a", description="API errors"))
        incident_id = created.id

    async with session_factory() as session:
        repository = IncidentRepository(session)
        retrieved = await repository.get(incident_id)

    assert retrieved is not None
    assert retrieved.status is IncidentStatus.OPEN
    assert retrieved.created_at.tzinfo is UTC
    assert retrieved.updated_at.tzinfo is UTC
    await engine.dispose()
