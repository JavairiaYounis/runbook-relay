import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from runbook_relay import __version__
from runbook_relay.config import Settings, get_settings
from runbook_relay.logging import configure_logging

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class HealthResponse(BaseModel):
    service: str
    status: str
    environment: str
    version: str


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody


async def require_api_key(
    provided_key: Annotated[str | None, Depends(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    expected_key = settings.api_key.get_secret_value()
    if provided_key is None or not secrets.compare_digest(provided_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)

    application = FastAPI(
        title=app_settings.service_name,
        version=__version__,
        description="Evidence-based operational incident investigation.",
    )
    if settings is not None:
        application.dependency_overrides[get_settings] = lambda: app_settings

    @application.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        content = ErrorResponse(
            error=ErrorBody(code=f"http_{exc.status_code}", message=str(exc.detail))
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=content.model_dump(),
            headers=exc.headers,
        )

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        return HealthResponse(
            service=app_settings.service_name,
            status="ok",
            environment=app_settings.environment,
            version=__version__,
        )

    protected = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])

    @protected.get("/ping", include_in_schema=False)
    async def protected_ping() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(protected)
    return application


app = create_app()
