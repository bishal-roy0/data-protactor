from fastapi import APIRouter, File, HTTPException, UploadFile, status

from sentinel_ai.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    RecommendedAction,
    ThreatCategory,
)
from sentinel_ai.core.config import get_settings
from sentinel_ai.services.image_analyzer import ImageAnalyzer
from sentinel_ai.services.reputation import VirusTotalReputationService
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
    """Confirm that the Karna API is running."""

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

    response = threat_analyzer.analyze(payload)
    settings = get_settings()
    reputation_evidence = await VirusTotalReputationService(
        settings.virustotal_api_key
    ).evidence_for([str(url) for url in payload.urls])
    if not reputation_evidence:
        return response
    combined_score = min(response.risk_score + sum(item.weight for item in reputation_evidence), 100)
    return response.model_copy(
        update={
            "risk_score": combined_score,
            "risk_level": threat_analyzer._risk_level(combined_score),
            "threat_category": ThreatCategory.MALWARE_DOWNLOAD,
            "evidence": [*response.evidence, *reputation_evidence],
            "recommended_action": (
                RecommendedAction.QUARANTINE
                if combined_score >= 70
                else RecommendedAction.BLOCK
            ),
            "summary": "URL reputation evidence was added to the local safety assessment.",
        }
    )


@router.post(
    "/analyze/image",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Threat analysis"],
    summary="Analyze an image for visible communication-security signals",
)
async def analyze_image(image: UploadFile = File(...)) -> AnalyzeResponse:
    """Validate an image in memory and optionally send it to configured OpenAI vision analysis."""
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Only JPG, PNG, and WEBP images are supported.")
    image_bytes = await image.read(5 * 1024 * 1024 + 1)
    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image size must not exceed 5 MB.")
    if not _has_valid_image_signature(image_bytes, image.content_type):
        raise HTTPException(status_code=415, detail="The file content does not match its declared image type.")
    settings = get_settings()
    return await ImageAnalyzer(settings.openai_api_key, settings.openai_vision_model).analyze(image_bytes, image.content_type)


def _has_valid_image_signature(image: bytes, content_type: str) -> bool:
    if content_type == "image/jpeg":
        return image.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return image.startswith(b"\x89PNG\r\n\x1a\n")
    return image.startswith(b"RIFF") and image[8:12] == b"WEBP"
