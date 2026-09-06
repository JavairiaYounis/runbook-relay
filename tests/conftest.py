import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

# The module-level FastAPI app requires configuration during test collection.
os.environ.setdefault("RUNBOOK_RELAY_API_KEY", "pytest-collection-key")
os.environ.setdefault("RUNBOOK_RELAY_DATABASE_URL", "sqlite+aiosqlite:///pytest-collection.db")

from runbook_relay.config import Settings  # noqa: E402
from runbook_relay.database import Base  # noqa: E402
from runbook_relay.main import create_app  # noqa: E402


@pytest.fixture
def api_key() -> str:
    return "test-secret-key"


@pytest.fixture
def api_client(tmp_path: Path, api_key: str) -> Iterator[TestClient]:
    import asyncio

    database_path = tmp_path / "api.db"
    settings = Settings(
        api_key=SecretStr(api_key),
        database_url=SecretStr(f"sqlite+aiosqlite:///{database_path.as_posix()}"),
        environment="test",
    )
    app = create_app(settings)

    async def create_schema() -> None:
        async with app.state.database_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(create_schema())
    with TestClient(app) as client:
        yield client
