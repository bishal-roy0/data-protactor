"""Image safety analysis with an optional OpenAI vision enrichment path."""

import base64
import json

from openai import AsyncOpenAI

from sentinel_ai.api.schemas import (
    AnalyzeResponse,
    RecommendedAction,
    RiskLevel,
    ThreatCategory,
    ThreatEvidence,
)


class ImageAnalyzer:
    """Analyzes validated images without persisting them locally."""

    def __init__(self, api_key: str | None, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key) if api_key else None
        self._model = model

    async def analyze(self, image: bytes, media_type: str) -> AnalyzeResponse:
        if not self._client:
            return AnalyzeResponse(
                risk_level=RiskLevel.SAFE,
                risk_score=0,
                threat_category=ThreatCategory.SAFE,
                evidence=[],
                confidence=0.35,
                recommended_action=RecommendedAction.ALLOW,
                summary="Image format was validated. Visual threat analysis is unavailable because OPENAI_API_KEY is not configured.",
            )

        try:
            image_url = f"data:{media_type};base64,{base64.b64encode(image).decode()}"
            response = await self._client.responses.create(
                model=self._model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Assess this image only for communication-security signals: phishing, fake login "
                                    "screens, scam payments, QR-code risks, impersonation, or social engineering. "
                                    "Return strict JSON with risk_score (0-100), threat_category, confidence (0-1), "
                                    "summary, and evidence (an array of objects with signal, explanation, weight). "
                                    "Do not claim malware detection or certainty."
                                ),
                            },
                            {"type": "input_image", "image_url": image_url, "detail": "low"},
                        ],
                    }
                ],
            )
            return self._from_model_output(response.output_text)
        except Exception:
            return AnalyzeResponse(
                risk_level=RiskLevel.LOW,
                risk_score=10,
                threat_category=ThreatCategory.UNSAFE_ATTACHMENT,
                evidence=[],
                confidence=0.2,
                recommended_action=RecommendedAction.CAUTION,
                summary="Image analysis could not be completed. Treat unexpected images cautiously and verify their sender.",
            )

    @staticmethod
    def _from_model_output(output: str) -> AnalyzeResponse:
        data = json.loads(output)
        score = max(0, min(int(data.get("risk_score", 0)), 100))
        level = (
            RiskLevel.CRITICAL
            if score >= 70
            else RiskLevel.HIGH
            if score >= 45
            else RiskLevel.MEDIUM
            if score >= 20
            else RiskLevel.LOW
            if score
            else RiskLevel.SAFE
        )
        category = ThreatCategory(data.get("threat_category", "safe"))
        evidence = [ThreatEvidence(**item) for item in data.get("evidence", [])]
        action = (
            RecommendedAction.QUARANTINE
            if level is RiskLevel.CRITICAL
            else RecommendedAction.BLOCK
            if level is RiskLevel.HIGH
            else RecommendedAction.CAUTION
            if level in {RiskLevel.LOW, RiskLevel.MEDIUM}
            else RecommendedAction.ALLOW
        )
        return AnalyzeResponse(
            risk_level=level,
            risk_score=score,
            threat_category=category,
            evidence=evidence,
            confidence=max(0.0, min(float(data.get("confidence", 0.5)), 1.0)),
            recommended_action=action,
            summary=str(data.get("summary", "Image analysis completed.")),
        )
