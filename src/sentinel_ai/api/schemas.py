from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl, model_validator


class HealthResponse(BaseModel):
    """Service availability response."""

    status: str = Field(description="Current service availability.")
    service: str = Field(description="Name of the running service.")
    environment: str = Field(description="Active deployment environment.")


class RiskLevel(StrEnum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(StrEnum):
    SAFE = "safe"
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    SUSPICIOUS_URL = "suspicious_url"


class RecommendedAction(StrEnum):
    ALLOW = "allow"
    CAUTION = "show_caution"
    BLOCK = "block"


class AnalyzeRequest(BaseModel):
    """Content submitted by an authorized platform for safety analysis."""

    text: str | None = Field(
        default=None,
        max_length=10_000,
        description="Message content to inspect. Do not submit credentials or sensitive personal data.",
    )
    urls: list[HttpUrl] = Field(
        default_factory=list,
        max_length=20,
        description="URLs to inspect without fetching or visiting them.",
    )

    @model_validator(mode="after")
    def require_content(self) -> "AnalyzeRequest":
        if not (self.text and self.text.strip()) and not self.urls:
            raise ValueError("Provide non-empty text, at least one URL, or both.")
        return self


class ThreatEvidence(BaseModel):
    """A human-readable signal that contributed to the assessment."""

    signal: str = Field(description="Short name for the detected signal.")
    explanation: str = Field(description="Why this signal can indicate a threat.")
    weight: int = Field(ge=1, le=100, description="Risk points contributed by this signal.")


class AnalyzeResponse(BaseModel):
    """Structured result returned after a local safety assessment."""

    risk_level: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    threat_category: ThreatCategory
    evidence: list[ThreatEvidence]
    confidence: float = Field(ge=0, le=1)
    recommended_action: RecommendedAction
    summary: str
