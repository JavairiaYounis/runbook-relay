import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from runbook_relay.models import Incident


class IncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, incident: Incident) -> Incident:
        self._session.add(incident)
        await self._session.commit()
        await self._session.refresh(incident)
        return incident

    async def get(self, incident_id: uuid.UUID) -> Incident | None:
        return await self._session.get(Incident, incident_id)
