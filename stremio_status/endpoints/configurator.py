from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

from stremio_status.core.constants import STATIC_DIR
from stremio_status.services import status_service

logger = logging.getLogger(__name__)

configurator_router = APIRouter()


@configurator_router.get("/stremio/configure")
async def configure() -> FileResponse:
    """Serve the configurator HTML page."""
    logger.debug("Serving configurator HTML")
    return FileResponse(
        path=STATIC_DIR / "configure.html",
        media_type="text/html",
    )


@configurator_router.get("/{config_token}/configure")
async def configure_with_config(config_token: str) -> RedirectResponse:
    """Redirect to configurator with config token as query parameter.

    Frontend will decode the base64 token client-side.
    """
    logger.debug(
        f"Redirecting to configurator with config token: {config_token[:20]}..."
    )
    return RedirectResponse(
        url=f"/stremio/configure?config={config_token}", status_code=302
    )


@configurator_router.get("/configure")
async def configure_redirect() -> RedirectResponse:
    """Redirect to main configurator route."""
    return RedirectResponse(url="/stremio/configure", status_code=301)


@configurator_router.get("/")
async def root_redirect() -> RedirectResponse:
    """Redirect root to configurator."""
    return RedirectResponse(url="/stremio/configure", status_code=301)


@configurator_router.get("/api/endpoints")
async def get_endpoints() -> dict[str, list[dict[str, Any]]]:
    """Return available endpoints for the configurator UI.

    Uses the cached status snapshot (same cache as catalog).
    """
    logger.debug("Fetching endpoints for configurator API")
    endpoints = await status_service.get_status_snapshot()

    return {
        "endpoints": [
            {
                "key": ep.key,
                "name": ep.name,
                "group": ep.group,
                "healthy": ep.healthy,
            }
            for ep in endpoints
        ]
    }
