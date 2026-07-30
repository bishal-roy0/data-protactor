"""Read-only GoPhish simulation metadata for authorized internal test fixtures.

This adapter is intentionally not imported by API routes and must never run as
part of a user-facing analysis request.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx


@dataclass(frozen=True)
class GoPhishSimulationSettings:
    api_url: str | None
    api_key: str | None
    enabled: bool = False


class GoPhishSimulationAdapter:
    """Extracts URLs from owner-authorized simulation metadata without logging it."""

    def __init__(self, settings: GoPhishSimulationSettings) -> None:
        self._settings = settings

    async def authorized_fixture_urls(self) -> list[str]:
        """Return de-duplicated HTTPS simulation URLs only when explicitly enabled."""

        if not (self._settings.enabled and self._settings.api_url and self._settings.api_key):
            return []
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self._settings.api_url.rstrip('/')}/api/campaigns/",
                    headers={"Authorization": f"Bearer {self._settings.api_key}"},
                )
                if response.status_code != 200:
                    return []
                return self._safe_urls(response.json())
        except (httpx.HTTPError, ValueError, TypeError):
            return []

    @staticmethod
    def _safe_urls(metadata: object) -> list[str]:
        if not isinstance(metadata, list):
            return []
        urls: list[str] = []
        for item in metadata:
            if not isinstance(item, dict):
                continue
            value = item.get("url")
            if not isinstance(value, str):
                continue
            parsed = urlsplit(value)
            if parsed.scheme == "https" and parsed.hostname:
                urls.append(value)
        return list(dict.fromkeys(urls))
