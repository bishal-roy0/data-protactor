from dataclasses import dataclass

from sentinel_ai.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    RecommendedAction,
    RiskLevel,
    ThreatCategory,
    ThreatEvidence,
)


@dataclass(frozen=True)
class DetectionRule:
    terms: tuple[str, ...]
    signal: str
    explanation: str
    weight: int
    category: ThreatCategory


TEXT_RULES = (
    DetectionRule(
        terms=("verify your account", "confirm your account", "account suspended"),
        signal="Account-verification pressure",
        explanation="The message pressures the recipient to verify an account, a common phishing pretext.",
        weight=30,
        category=ThreatCategory.PHISHING,
    ),
    DetectionRule(
        terms=("i am your boss", "i'm your boss", "ceo needs", "government fine"),
        signal="Possible impersonation pressure",
        explanation="The message uses an authority claim that can be used to pressure a recipient into acting.",
        weight=25,
        category=ThreatCategory.IMPERSONATION,
    ),
    DetectionRule(
        terms=("urgent", "immediately", "act now", "limited time"),
        signal="Urgency pressure",
        explanation="Urgency can be used to discourage careful verification before acting.",
        weight=15,
        category=ThreatCategory.SOCIAL_ENGINEERING,
    ),
    DetectionRule(
        terms=("password", "otp", "one-time code", "security code"),
        signal="Credential request",
        explanation="Requests for passwords or verification codes can indicate an attempt to take over an account.",
        weight=35,
        category=ThreatCategory.PHISHING,
    ),
    DetectionRule(
        terms=("gift card", "wire transfer", "crypto payment", "cryptocurrency"),
        signal="High-risk payment request",
        explanation="Unusual payment requests are frequently used in impersonation and fraud attempts.",
        weight=30,
        category=ThreatCategory.SOCIAL_ENGINEERING,
    ),
)


class ThreatAnalyzer:
    """Rule-based baseline analyzer that never fetches supplied URLs."""

    def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        evidence = self._analyze_text(request.text or "")
        evidence.extend(self._analyze_urls([str(url) for url in request.urls]))
        risk_score = min(sum(item.weight for item in evidence), 100)
        risk_level = self._risk_level(risk_score)

        return AnalyzeResponse(
            risk_level=risk_level,
            risk_score=risk_score,
            threat_category=self._primary_category(evidence),
            evidence=evidence,
            confidence=self._confidence(evidence),
            recommended_action=self._recommended_action(risk_level),
            summary=self._summary(risk_level, evidence),
        )

    def _analyze_text(self, text: str) -> list[ThreatEvidence]:
        normalized_text = text.casefold()
        evidence: list[ThreatEvidence] = []
        for rule in TEXT_RULES:
            if any(term in normalized_text for term in rule.terms):
                evidence.append(
                    ThreatEvidence(
                        signal=rule.signal,
                        explanation=rule.explanation,
                        weight=rule.weight,
                    )
                )
        return evidence

    def _analyze_urls(self, urls: list[str]) -> list[ThreatEvidence]:
        evidence: list[ThreatEvidence] = []
        for url in urls:
            host = url.split("//", maxsplit=1)[-1].split("/", maxsplit=1)[0].casefold()
            if "@" in url.split("//", maxsplit=1)[-1].split("/", maxsplit=1)[0]:
                evidence.append(
                    ThreatEvidence(
                        signal="Misleading URL authority",
                        explanation="The URL contains an @ character before the path, which can hide the actual destination host.",
                        weight=35,
                    )
                )
            if host.startswith("xn--") or ".xn--" in host:
                evidence.append(
                    ThreatEvidence(
                        signal="Internationalized domain name",
                        explanation="This URL uses an encoded domain name. It may be legitimate, but it can also be used to imitate trusted brands.",
                        weight=20,
                    )
                )
            if self._is_ipv4_host(host):
                evidence.append(
                    ThreatEvidence(
                        signal="IP-address URL",
                        explanation="The URL uses a numeric IP address instead of a domain name, which can make the destination harder to recognize.",
                        weight=20,
                    )
                )
            lowered_url = url.casefold()
            if any(parameter in lowered_url for parameter in ("?url=", "?redirect=", "?next=", "?continue=")):
                evidence.append(
                    ThreatEvidence(
                        signal="Redirect-style URL",
                        explanation="The link contains a redirect parameter that can conceal its final destination.",
                        weight=20,
                    )
                )
            if any(lowered_url.split("?", maxsplit=1)[0].endswith(extension) for extension in (".exe", ".msi", ".apk", ".dmg", ".iso", ".scr", ".bat", ".cmd", ".zip", ".rar")):
                evidence.append(
                    ThreatEvidence(
                        signal="Executable or archive download link",
                        explanation="The URL points to a downloadable executable or archive. Verify the publisher before downloading.",
                        weight=45,
                    )
                )
            if any(marker in lowered_url for marker in ("private-video", "watch-now", "video-download")):
                evidence.append(
                    ThreatEvidence(
                        signal="Potentially deceptive media link",
                        explanation="The media-link wording is commonly used to lure recipients to unverified destinations.",
                        weight=20,
                    )
                )
        return evidence

    @staticmethod
    def _is_ipv4_host(host: str) -> bool:
        parts = host.split(":", maxsplit=1)[0].split(".")
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

    @staticmethod
    def _risk_level(score: int) -> RiskLevel:
        if score >= 70:
            return RiskLevel.CRITICAL
        if score >= 45:
            return RiskLevel.HIGH
        if score >= 20:
            return RiskLevel.MEDIUM
        if score > 0:
            return RiskLevel.LOW
        return RiskLevel.SAFE

    @staticmethod
    def _primary_category(evidence: list[ThreatEvidence]) -> ThreatCategory:
        if not evidence:
            return ThreatCategory.SAFE
        if any("download" in item.signal.lower() for item in evidence):
            return ThreatCategory.MALWARE_DOWNLOAD
        if any(item.signal == "Credential request" for item in evidence):
            return ThreatCategory.PHISHING
        if any("impersonation" in item.signal.lower() for item in evidence):
            return ThreatCategory.IMPERSONATION
        if any("URL" in item.signal or "domain" in item.signal.lower() for item in evidence):
            return ThreatCategory.SUSPICIOUS_URL
        return ThreatCategory.SOCIAL_ENGINEERING

    @staticmethod
    def _confidence(evidence: list[ThreatEvidence]) -> float:
        if not evidence:
            return 0.65
        return min(0.55 + (0.1 * len(evidence)), 0.95)

    @staticmethod
    def _recommended_action(risk_level: RiskLevel) -> RecommendedAction:
        if risk_level is RiskLevel.CRITICAL:
            return RecommendedAction.QUARANTINE
        if risk_level is RiskLevel.HIGH:
            return RecommendedAction.BLOCK
        if risk_level in {RiskLevel.LOW, RiskLevel.MEDIUM}:
            return RecommendedAction.CAUTION
        return RecommendedAction.ALLOW

    @staticmethod
    def _summary(risk_level: RiskLevel, evidence: list[ThreatEvidence]) -> str:
        if not evidence:
            return "No common phishing, social-engineering, or suspicious-URL signals were detected."
        return f"{risk_level.value.title()} risk: {len(evidence)} signal(s) require attention."
