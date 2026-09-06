import uuid

from runbook_relay.incidents.repository import IncidentRepository
from runbook_relay.incidents.schemas import IncidentCreate
from runbook_relay.models import Incident


class IncidentService:
    def __init__(self, repository: IncidentRepository) -> None:
        self._repository = repository

    async def create(self, data: IncidentCreate) -> Incident:
        incident = Incident(
            client_id=data.client_id,
            description=data.description,
            external_reference=data.external_reference,
        )
        return await self._repository.add(incident)

    async def get(self, incident_id: uuid.UUID) -> Incident | None:
        return await self._repository.get(incident_id)
