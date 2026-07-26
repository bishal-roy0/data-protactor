from fastapi import APIRouter, status

from sentinel_ai.api.schemas import HealthResponse
from sentinel_ai.core.config import get_settings

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check service health",
)
async def health_check() -> HealthResponse:
    """Confirm that the Sentinel AI API is running."""

    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        environment=settings.environment,
    )
