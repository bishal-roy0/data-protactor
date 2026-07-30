from dataclasses import dataclass
from urllib.parse import parse_qsl, unquote, urlsplit

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
    DetectionRule(
        terms=("you have won", "you've won", "claim your prize", "lottery winner", "processing fee"),
        signal="Prize or lottery scam",
        explanation="Unexpected prize, lottery, or fee requests are common scam patterns and should be independently verified.",
        weight=30,
        category=ThreatCategory.SCAM,
    ),
    DetectionRule(
        terms=("share your access", "share your login", "send me the code", "send the code"),
        signal="Sensitive-access request",
        explanation="The message asks for access or a code that should not be shared outside a verified process.",
        weight=20,
        category=ThreatCategory.PHISHING,
    ),
)
EMOTIONAL_PRETEXT_TERMS = (
    "worried about your job", "boss is really angry", "heard your company is downsizing",
    "sorry to hear about your loss", "feeling really stressed", "don't miss out",
)
RISKY_REQUEST_TERMS = (
    "verify your details", "verify your identity", "share your access", "share your login",
    "send me the code", "send the code", "send your password", "send your otp",
)

KNOWN_BRANDS = {
    "amazon": ("amazon.com",),
    "apple": ("apple.com",),
    "google": ("google.com",),
    "microsoft": ("microsoft.com",),
    "netflix": ("netflix.com",),
    "paypal": ("paypal.com",),
}
URL_SHORTENERS = {"bit.ly", "cutt.ly", "is.gd", "rb.gy", "t.co", "tinyurl.com"}
PROMOTION_LURE_TERMS = {"bonus", "cashback", "giveaway", "reward", "refund"}
HIGH_RISK_PROMOTION_TLDS = {".click", ".link", ".shop", ".top", ".xyz"}
FREE_SUBDOMAIN_SUFFIXES = {".us.cc"}
REDIRECT_PARAMETERS = {"continue", "destination", "next", "redirect", "target", "url"}
CREDENTIAL_PATH_TERMS = {"account", "login", "otp", "password", "reset", "signin", "verify"}
PAYMENT_PATH_TERMS = {"bank", "crypto", "delivery", "gift", "lottery", "payment", "prize", "support"}
DOWNLOAD_EXTENSIONS = (".apk", ".bat", ".cmd", ".dmg", ".exe", ".iso", ".msi", ".rar", ".scr", ".zip")


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
            analysis_sources=["local_rules"],
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
        if (
            any(term in normalized_text for term in EMOTIONAL_PRETEXT_TERMS)
            and any(term in normalized_text for term in RISKY_REQUEST_TERMS)
        ):
            evidence.append(
                ThreatEvidence(
                    signal="Emotional-pressure pretext",
                    explanation="The message combines fear, loss, workplace pressure, or scarcity with a sensitive request. Verify the sender through a trusted channel before acting.",
                    weight=20,
                )
            )
        return evidence

    def _analyze_urls(self, urls: list[str]) -> list[ThreatEvidence]:
        evidence: list[ThreatEvidence] = []
        for url in urls:
            parsed = urlsplit(url)
            host = (parsed.hostname or "").casefold()
            authority = url.split("//", maxsplit=1)[-1].split("/", maxsplit=1)[0]
            if "@" in authority:
                evidence.append(self._evidence("Misleading URL authority", "The URL contains an @ character before the path, which can hide the actual destination host.", 35))
            if host.startswith("xn--") or ".xn--" in host:
                evidence.append(self._evidence("Encoded domain", "The domain uses an encoded format that can hide look-alike characters.", 20))
            if self._is_ipv4_host(host):
                evidence.append(self._evidence("IP-address URL", "The URL uses a numeric IP address instead of a domain name, which can make the destination harder to recognize.", 20))
            lowered_url = url.casefold()
            evidence.extend(self._domain_evidence(host))
            evidence.extend(self._query_evidence(parsed.query, lowered_url))
            if host in URL_SHORTENERS:
                evidence.append(self._evidence("URL shortener", "Shortened links conceal the destination until they are expanded by a trusted service.", 20))
            if any(lowered_url.split("?", maxsplit=1)[0].endswith(extension) for extension in DOWNLOAD_EXTENSIONS):
                evidence.append(self._evidence("Executable or archive download link", "The URL points to a downloadable executable or archive. Verify the publisher before downloading.", 45))
            path_and_query = f"{parsed.path}?{parsed.query}".casefold()
            if any(term in path_and_query for term in CREDENTIAL_PATH_TERMS):
                evidence.append(self._evidence("Credential-harvesting URL", "The URL contains login, account, password, verification, or OTP wording that can be used to imitate a sign-in page.", 30))
            if any(term in path_and_query for term in PAYMENT_PATH_TERMS):
                evidence.append(self._evidence("Payment or prize lure URL", "The URL contains payment, prize, delivery, bank, crypto, or support wording commonly used in scam lures.", 20))
            if any(marker in lowered_url for marker in ("adult-lure", "private-video", "video-download", "watch-now")):
                evidence.append(self._evidence("Potentially deceptive media link", "The media-link wording is commonly used to lure recipients to unverified destinations.", 20))
        return evidence

    @staticmethod
    def _evidence(signal: str, explanation: str, weight: int) -> ThreatEvidence:
        return ThreatEvidence(signal=signal, explanation=explanation, weight=weight)

    def _domain_evidence(self, host: str) -> list[ThreatEvidence]:
        evidence: list[ThreatEvidence] = []
        labels = host.split(".")
        if len(labels) > 4:
            evidence.append(self._evidence("Excessive subdomains", "The domain has an unusually deep subdomain structure that can obscure the registered destination.", 15))
        if self._has_ip_style_subdomain(labels):
            evidence.append(self._evidence("IP-address-style subdomain", "The hostname begins with four numeric labels that resemble an IP address but route through a different domain. This construction can obscure the real destination.", 35))
        if any(label.count("-") >= 2 for label in labels):
            evidence.append(self._evidence("Suspicious hyphenated domain", "Multiple hyphens in a domain label can be used to imitate a brand or login destination.", 15))
        if any(len(label) >= 14 and sum(character.isdigit() for character in label) >= 3 for label in labels):
            evidence.append(self._evidence("Random-looking domain label", "A long domain label with several digits can make a destination harder to recognize.", 15))
        if (
            any(term in host for term in PROMOTION_LURE_TERMS)
            and any(host.endswith(tld) for tld in HIGH_RISK_PROMOTION_TLDS)
        ):
            evidence.append(self._evidence("Suspicious reward-lure domain", "The domain combines a financial reward or cashback lure with a generic top-level domain often used for short-lived promotions. Verify the offer through the official provider.", 45))
        if any(host.endswith(suffix) for suffix in FREE_SUBDOMAIN_SUFFIXES) and self._looks_opaque_label(labels[0]):
            evidence.append(self._evidence("Opaque free-subdomain host", "The URL uses a random-looking hostname beneath a free subdomain service. This can make a short-lived destination difficult to verify.", 45))
        for brand, official_domains in KNOWN_BRANDS.items():
            if any(host == domain or host.endswith(f".{domain}") for domain in official_domains):
                continue
            label_parts = [part for label in labels for part in label.split("-")]
            if brand in host or any(
                self._edit_distance(label, brand) == 1
                for label in label_parts
                if len(label) >= 4
            ):
                evidence.append(self._evidence("Possible brand impersonation", "The domain closely resembles a well-known brand but is not an official domain.", 35))
                break
        return evidence

    def _query_evidence(self, query: str, lowered_url: str) -> list[ThreatEvidence]:
        evidence: list[ThreatEvidence] = []
        decoded_query = unquote(query).casefold()
        parameters = {key.casefold(): value.casefold() for key, value in parse_qsl(query, keep_blank_values=True)}
        if any(parameter in REDIRECT_PARAMETERS for parameter in parameters):
            evidence.append(self._evidence("Redirect-style URL", "The link contains a redirect parameter that can conceal its final destination.", 20))
        if "http://" in decoded_query or "https://" in decoded_query:
            evidence.append(self._evidence("Nested destination URL", "The link contains another URL in its query, which can hide the final destination.", 20))
        if "%" in query or "%" in lowered_url:
            evidence.append(self._evidence("Encoded URL content", "The URL contains encoded content that can obscure a destination or request.", 15))
        return evidence

    @staticmethod
    def _edit_distance(first: str, second: str) -> int:
        if abs(len(first) - len(second)) > 1:
            return 2
        previous = list(range(len(second) + 1))
        for first_index, first_character in enumerate(first, start=1):
            current = [first_index]
            for second_index, second_character in enumerate(second, start=1):
                current.append(min(current[-1] + 1, previous[second_index] + 1, previous[second_index - 1] + (first_character != second_character)))
            previous = current
        return previous[-1]

    @staticmethod
    def _is_ipv4_host(host: str) -> bool:
        parts = host.split(":", maxsplit=1)[0].split(".")
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

    @staticmethod
    def _has_ip_style_subdomain(labels: list[str]) -> bool:
        return len(labels) > 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in labels[:4])

    @staticmethod
    def _looks_opaque_label(label: str) -> bool:
        return len(label) >= 6 and sum(character in "aeiou" for character in label) <= 1

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
        if any("credential" in item.signal.lower() for item in evidence):
            return ThreatCategory.PHISHING
        if any("impersonation" in item.signal.lower() for item in evidence):
            return ThreatCategory.IMPERSONATION
        if any("scam" in item.signal.lower() for item in evidence):
            return ThreatCategory.SCAM
        if any(
            "url" in item.signal.lower()
            or "domain" in item.signal.lower()
            or "media link" in item.signal.lower()
            for item in evidence
        ):
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
