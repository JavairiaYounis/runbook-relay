from collections.abc import Mapping
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient


def auth(api_key: str) -> Mapping[str, str]:
    return {"X-API-Key": api_key}


def create_incident(client: TestClient, api_key: str) -> dict[str, Any]:
    response = client.post(
        "/api/v1/incidents",
        headers=auth(api_key),
        json={
            "client_id": "northstar-connect",
            "description": "Abandoned calls increased during the last 20 minutes.",
            "external_reference": "  OPS-1042  ",
        },
    )
    assert response.status_code == 201
    return cast(dict[str, Any], response.json())


def test_create_incident_returns_persisted_fields(api_client: TestClient, api_key: str) -> None:
    body = create_incident(api_client, api_key)

    UUID(body["id"])
    assert body["client_id"] == "northstar-connect"
    assert body["description"] == "Abandoned calls increased during the last 20 minutes."
    assert body["external_reference"] == "OPS-1042"
    assert body["status"] == "open"
    assert body["category"] is None
    assert body["severity"] is None
    assert body["created_at"].endswith("Z")
    assert body["updated_at"].endswith("Z")


def test_get_incident_returns_created_incident(api_client: TestClient, api_key: str) -> None:
    created = create_incident(api_client, api_key)

    response = api_client.get(f"/api/v1/incidents/{created['id']}", headers=auth(api_key))

    assert response.status_code == 200
    assert response.json() == created


def test_unknown_incident_returns_consistent_404(api_client: TestClient, api_key: str) -> None:
    response = api_client.get(f"/api/v1/incidents/{uuid4()}", headers=auth(api_key))

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "http_404", "message": "Incident not found"}}


def test_incident_endpoints_require_authentication(api_client: TestClient) -> None:
    missing = api_client.post(
        "/api/v1/incidents", json={"client_id": "client", "description": "description"}
    )
    invalid = api_client.get(f"/api/v1/incidents/{uuid4()}", headers={"X-API-Key": "invalid"})

    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_empty_client_id_and_description_are_rejected(api_client: TestClient, api_key: str) -> None:
    response = api_client.post(
        "/api/v1/incidents",
        headers=auth(api_key),
        json={"client_id": "   ", "description": ""},
    )

    assert response.status_code == 422
    fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert fields == {"client_id", "description"}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("client_id", "c" * 101),
        ("description", "d" * 10_001),
        ("external_reference", "r" * 256),
    ],
)
def test_overlong_incident_fields_are_rejected_before_persistence(
    api_client: TestClient, api_key: str, field: str, value: str
) -> None:
    payload = {"client_id": "client", "description": "description", field: value}

    response = api_client.post("/api/v1/incidents", headers=auth(api_key), json=payload)

    assert response.status_code == 422
    assert any(error["loc"][-1] == field for error in response.json()["detail"])
