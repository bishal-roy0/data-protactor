"""QR safety analysis that decodes in memory and never follows a QR destination."""

from __future__ import annotations

import io

from sentinel_ai.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    RecommendedAction,
    RiskLevel,
    ThreatCategory,
    ThreatEvidence,
)
from sentinel_ai.services.threat_analyzer import ThreatAnalyzer


class QrAnalyzer:
    """Decode a QR image locally, then inspect the decoded text without network access."""

    def __init__(self, threat_analyzer: ThreatAnalyzer) -> None:
        self._threat_analyzer = threat_analyzer

    def analyze(self, image: bytes) -> AnalyzeResponse:
        payload = self._decode(image)
        if not payload:
            return AnalyzeResponse(
                risk_level=RiskLevel.LOW,
                risk_score=10,
                threat_category=ThreatCategory.UNSAFE_ATTACHMENT,
                evidence=[ThreatEvidence(
                    signal="Unreadable QR code",
                    explanation="No readable QR content was detected. Karna did not open or execute the image.",
                    weight=10,
                )],
                confidence=0.5,
                recommended_action=RecommendedAction.CAUTION,
                summary="No QR destination could be assessed. Use caution with unexpected QR codes.",
                analysis_sources=["local_qr_decoder"],
            )
        if payload.lower().startswith(("https://", "http://")):
            result = self._threat_analyzer.analyze(AnalyzeRequest(urls=[payload]))
            return result.model_copy(update={"analysis_sources": ["local_qr_decoder", *result.analysis_sources]})
        return AnalyzeResponse(
            risk_level=RiskLevel.LOW,
            risk_score=15,
            threat_category=ThreatCategory.UNSAFE_ATTACHMENT,
            evidence=[ThreatEvidence(
                signal="Non-web QR payload",
                explanation="The QR code contains non-web data. Karna did not execute, import, or act on that data.",
                weight=15,
            )],
            confidence=0.7,
            recommended_action=RecommendedAction.CAUTION,
            summary="The QR code is not a web link. Review it carefully before using it in another app.",
            analysis_sources=["local_qr_decoder"],
        )

    @staticmethod
    def _decode(image: bytes) -> str | None:
        """Use OpenCV locally. Importing here preserves a safe fallback if a deploy misses the extra wheel."""
        try:
            import cv2
            import numpy

            pixels = numpy.asarray(bytearray(io.BytesIO(image).read()), dtype=numpy.uint8)
            decoded_image = cv2.imdecode(pixels, cv2.IMREAD_COLOR)
            if decoded_image is None:
                return None
            value, _, _ = cv2.QRCodeDetector().detectAndDecode(decoded_image)
            return value.strip() or None
        except Exception:
            return None
