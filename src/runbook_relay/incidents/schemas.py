import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from runbook_relay.models import IncidentStatus

ClientId = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Description = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000)
]
ExternalReference = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
]


class IncidentCreate(BaseModel):
    client_id: ClientId
    description: Description
    external_reference: ExternalReference | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: str
    description: str
    external_reference: str | None
    status: IncidentStatus
    category: str | None
    severity: str | None
    created_at: datetime
    updated_at: datetime
