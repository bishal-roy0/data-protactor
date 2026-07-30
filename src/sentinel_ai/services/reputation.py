"""Optional URL reputation enrichment without visiting supplied URLs."""

import base64
from typing import Protocol

import httpx

from sentinel_ai.api.schemas import ThreatEvidence


class UrlReputationProvider(Protocol):
    """Contract for optional providers that return existing URL reputation only."""

    async def evidence_for(self, urls: list[str]) -> list[ThreatEvidence]: ...


class VirusTotalReputationService:
    """Looks up VirusTotal's existing URL reputation only when configured."""

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    async def evidence_for(self, urls: list[str]) -> list[ThreatEvidence]:
        if not self._api_key:
            return []

        evidence: list[ThreatEvidence] = []
        headers = {"x-apikey": self._api_key}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                for url in urls:
                    url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
                    response = await client.get(
                        f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers
                    )
                    if response.status_code != 200:
                        continue
                    stats = response.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                    malicious = int(stats.get("malicious", 0))
                    suspicious = int(stats.get("suspicious", 0))
                    if malicious or suspicious:
                        evidence.append(
                            ThreatEvidence(
                                signal="URL reputation warning",
                                explanation=(
                                    "A configured reputation provider reports malicious or suspicious detections "
                                    f"for this URL ({malicious} malicious, {suspicious} suspicious)."
                                ),
                                weight=min(60, 25 + (malicious * 10) + (suspicious * 5)),
                            )
                        )
        except httpx.HTTPError:
            return evidence
        return evidence


def configured_reputation_providers(api_key: str | None) -> tuple[UrlReputationProvider, ...]:
    """Return only configured providers; an empty tuple preserves local analysis."""

    return (VirusTotalReputationService(api_key),) if api_key else ()
