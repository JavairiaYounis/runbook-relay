import pytest

from runbook_relay.config import Settings


def test_settings_read_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNBOOK_RELAY_ENVIRONMENT", "testing")
    monkeypatch.setenv("RUNBOOK_RELAY_API_KEY", "environment-secret")
    monkeypatch.setenv("RUNBOOK_RELAY_DATABASE_URL", "postgresql+asyncpg://example.invalid/db")

    settings = Settings()  # type: ignore[call-arg]

    assert settings.environment == "testing"
    assert settings.api_key.get_secret_value() == "environment-secret"
    assert settings.database_url.get_secret_value() == "postgresql+asyncpg://example.invalid/db"
