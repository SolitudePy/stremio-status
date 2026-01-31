from __future__ import annotations

import logging

from typing import Any

import httpx

from stremio_status.core.config import get_settings
from stremio_status.core.models import GatusEndpoint

logger = logging.getLogger(__name__)


class GatusClient:
    """Async HTTP client for fetching health data from Gatus API."""

    def __init__(self, base_url: str, timeout: float = 3.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def fetch_statuses(self) -> list[GatusEndpoint]:
        """Fetch health status for all monitored endpoints.

        Returns list of GatusEndpoint models with health data.
        Raises httpx.HTTPError on network/API errors.
        """
        url = f"{self.base_url}/api/v1/endpoints/statuses"
        logger.debug(f"Fetching statuses from {url}")

        resp = await self._client.get(url)
        resp.raise_for_status()
        data = resp.json()

        endpoints: list[GatusEndpoint] = []
        for ep in data:
            endpoint = self._parse_endpoint(ep)
            endpoints.append(endpoint)

        logger.debug(f"Fetched {len(endpoints)} endpoints")
        return endpoints

    def _parse_endpoint(self, ep: dict[str, Any]) -> GatusEndpoint:
        """Parse raw Gatus API response into GatusEndpoint model."""
        healthy, response_ms, last_updated = self._extract_health_data(ep)
        key = self._generate_key(ep)

        return GatusEndpoint.model_validate(
            {
                **ep,
                "key": key,
                "healthy": healthy,
                "responseTime": response_ms,
                "lastUpdated": last_updated,
            }
        )

    def _extract_health_data(
        self, ep: dict[str, Any]
    ) -> tuple[bool, int | None, str | None]:
        """Extract health status, response time, and last check time.

        Returns (healthy, response_ms, last_updated).
        """
        results = ep.get("results") or []
        if not results:
            return False, None, None

        last = results[-1]
        healthy = bool(last.get("success"))

        # Convert nanoseconds to milliseconds
        duration_ns = last.get("duration")
        response_ms = (
            int(duration_ns / 1_000_000)
            if isinstance(duration_ns, (int, float))
            else None
        )

        # Get timestamp from multiple possible fields
        last_updated = last.get("timestamp") or ep.get("lastUpdated") or ep.get("time")

        return healthy, response_ms, last_updated

    def _generate_key(self, ep: dict[str, Any]) -> str:
        """Generate unique key for endpoint.

        Uses existing key or creates one from group + name.
        Replaces '/' and spaces with '-' for URL safety.
        """
        if ep.get("key"):
            return str(ep["key"])

        group = (ep.get("group") or "").replace("/", "-")
        name = (ep.get("name") or "").replace("/", "-")
        return f"{group}_{name}".replace(" ", "-")

    async def close(self) -> None:
        """Close the HTTP client and release connections."""
        await self._client.aclose()


_client: GatusClient | None = None


def get_client() -> GatusClient:
    """Get or create the singleton Gatus client instance."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = GatusClient(str(settings.health_base_url))
    return _client
