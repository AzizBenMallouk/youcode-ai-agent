from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from youcode_ai.core.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    application: str
    environment: str


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        environment=settings.app_env,
    )