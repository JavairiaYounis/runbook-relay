import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from runbook_relay.config import Settings
from runbook_relay.main import create_app

TEST_KEY = "test-secret-key"


def make_client() -> TestClient:
    settings = Settings(
        api_key=SecretStr(TEST_KEY),
        database_url=SecretStr("sqlite+aiosqlite:///:memory:"),
        environment="test",
    )
    return TestClient(create_app(settings))


def test_health_is_public() -> None:
    response = make_client().get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "Runbook Relay",
        "status": "ok",
        "environment": "test",
        "version": "0.1.0",
    }


def test_missing_api_key_is_rejected() -> None:
    response = make_client().get("/api/v1/ping")

    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "http_401", "message": "Invalid or missing API key"}
    }


def test_invalid_api_key_is_rejected() -> None:
    response = make_client().get("/api/v1/ping", headers={"X-API-Key": "wrong"})

    assert response.status_code == 401


def test_valid_api_key_is_accepted() -> None:
    response = make_client().get("/api/v1/ping", headers={"X-API-Key": TEST_KEY})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_secret_is_not_exposed_in_settings_representation() -> None:
    settings = Settings(
        api_key=SecretStr(TEST_KEY),
        database_url=SecretStr("postgresql+asyncpg://user:secret@example.invalid/database"),
    )

    assert TEST_KEY not in repr(settings)
    assert TEST_KEY not in str(settings)


def test_secret_is_not_logged_or_returned(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("runbook_relay.test")
    client = make_client()

    with client:
        response = client.get("/api/v1/ping", headers={"X-API-Key": TEST_KEY})
        logger.info("authentication completed")

    assert TEST_KEY not in response.text
    assert TEST_KEY not in caplog.text
