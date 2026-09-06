import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from runbook_relay.database import get_session
from runbook_relay.incidents.repository import IncidentRepository
from runbook_relay.incidents.schemas import IncidentCreate, IncidentResponse
from runbook_relay.incidents.service import IncidentService

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_incident_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IncidentService:
    return IncidentService(IncidentRepository(session))


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    service: Annotated[IncidentService, Depends(get_incident_service)],
) -> IncidentResponse:
    incident = await service.create(data)
    return IncidentResponse.model_validate(incident)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    service: Annotated[IncidentService, Depends(get_incident_service)],
) -> IncidentResponse:
    incident = await service.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return IncidentResponse.model_validate(incident)
