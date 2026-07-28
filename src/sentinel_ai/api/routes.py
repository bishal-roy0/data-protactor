from fastapi import APIRouter, status

from sentinel_ai.api.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse
from sentinel_ai.core.config import get_settings
from sentinel_ai.services.threat_analyzer import ThreatAnalyzer

router = APIRouter(tags=["System"])
threat_analyzer = ThreatAnalyzer()


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


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Threat analysis"],
    summary="Analyze text and URLs for common threat signals",
)
async def analyze_content(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Return a transparent baseline risk assessment without opening supplied URLs."""

    return threat_analyzer.analyze(payload)
