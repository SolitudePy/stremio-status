from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from stremio_status.core.config import get_settings
from stremio_status.core.constants import ID_PREFIX
from stremio_status.core.models import Meta, StremioManifest
from stremio_status.core.user_config import UserConfig, decode_config
from stremio_status.services import status_service

logger = logging.getLogger(__name__)

stremio_router = APIRouter()

# Valid types/IDs for validation
VALID_CATALOG_TYPES = {"other"}
VALID_CATALOG_IDS = {"addon-status"}
VALID_CONTENT_TYPES = {"tv", "movie", "series"}


def _manifest_response() -> StremioManifest:
    """Generate the static addon manifest."""
    settings = get_settings()
    base_url = str(settings.public_base_url).rstrip("/")
    return StremioManifest(
        id="com.stremio.status",
        version="1.1.1",
        name="Stremio Status",
        description="Shows health status of stremio addons & services",
        logo=f"{base_url}/static/logo.png",
        resources=[
            "catalog",
            {
                "name": "meta",
                "types": ["tv", "movie", "series"],
                "idPrefixes": [ID_PREFIX],
            },
            "stream",
        ],
        types=["tv", "movie", "series"],
        catalogs=[{"type": "other", "id": "addon-status", "name": "Addon Status"}],
        behaviorHints={"configurable": True, "configurationRequired": False},
    )


async def _get_catalog(
    config: UserConfig, catalog_type: str, catalog_id: str
) -> list[dict[str, Any]]:
    """Build catalog items with validation."""
    logger.debug(f"Catalog request: type={catalog_type}, id={catalog_id}")

    if catalog_type not in VALID_CATALOG_TYPES:
        raise HTTPException(status_code=404, detail="Catalog type not found")
    if catalog_id not in VALID_CATALOG_IDS:
        raise HTTPException(status_code=404, detail="Catalog not found")

    items = await status_service.build_catalog(config)
    return [item.model_dump() for item in items]


async def _get_meta(config: UserConfig, meta_type: str, meta_id: str) -> dict[str, Any]:
    """Build meta for a specific addon."""
    logger.debug(f"Meta request: type={meta_type}, id={meta_id}")

    if meta_type not in VALID_CONTENT_TYPES:
        raise HTTPException(status_code=404, detail="Meta type not found")

    m = await status_service.build_meta(meta_id, config)
    if not m:
        raise HTTPException(status_code=404, detail="Not found")
    return Meta.model_validate(m).model_dump()


async def _get_streams(
    config: UserConfig, stream_type: str, stream_id: str
) -> list[dict[str, Any]]:
    """Build streams list.

    Note: `stream_id` is intentionally ignored because this addon provides
    global health status streams regardless of the specific content ID requested.
    It returns status streams for all monitored addons matching the config.
    """
    logger.debug(f"Stream request: type={stream_type}, id={stream_id}")

    if stream_type not in VALID_CONTENT_TYPES:
        raise HTTPException(status_code=404, detail="Stream type not found")

    streams = await status_service.build_streams(config)
    return [s.model_dump() for s in streams]


# Default routes (no config - shows all addons)


@stremio_router.get("/manifest.json", response_model=StremioManifest)
async def manifest() -> StremioManifest:
    """Default manifest endpoint (no configuration)."""
    return _manifest_response()


@stremio_router.get("/catalog/{catalog_type}/{catalog_id}.json")
async def catalog(
    catalog_type: str,
    catalog_id: str,
) -> dict[str, list[dict[str, Any]]]:
    """Default catalog endpoint (all addons)."""
    metas = await _get_catalog(UserConfig(), catalog_type, catalog_id)
    return {"metas": metas}


@stremio_router.get("/meta/{meta_type}/{meta_id}.json")
async def meta(meta_type: str, meta_id: str) -> dict[str, dict[str, Any]]:
    """Default meta endpoint (all addons)."""
    meta_data = await _get_meta(UserConfig(), meta_type, meta_id)
    return {"meta": meta_data}


@stremio_router.get("/stream/{stream_type}/{stream_id}.json")
async def stream(
    stream_type: str,
    stream_id: str,
) -> dict[str, list[dict[str, Any]]]:
    """Default stream endpoint (all addons)."""
    streams = await _get_streams(UserConfig(), stream_type, stream_id)
    return {"streams": streams}


# Configured routes (with base64 config token)


@stremio_router.get("/{config_token}/manifest.json", response_model=StremioManifest)
async def manifest_configured(config_token: str) -> StremioManifest:
    """Configured manifest endpoint.

    Decodes config to validate it, but returns standard manifest.
    Fail-safe: Invalid config tokens are ignored.
    """
    # Just validate decoding, result ignored for manifest
    _ = decode_config(config_token)
    return _manifest_response()


@stremio_router.get("/{config_token}/catalog/{catalog_type}/{catalog_id}.json")
async def catalog_configured(
    config_token: str,
    catalog_type: str,
    catalog_id: str,
) -> dict[str, list[dict[str, Any]]]:
    """Configured catalog endpoint."""
    config = decode_config(config_token)
    metas = await _get_catalog(config, catalog_type, catalog_id)
    return {"metas": metas}


@stremio_router.get("/{config_token}/meta/{meta_type}/{meta_id}.json")
async def meta_configured(
    config_token: str,
    meta_type: str,
    meta_id: str,
) -> dict[str, dict[str, Any]]:
    """Configured meta endpoint."""
    config = decode_config(config_token)
    meta_data = await _get_meta(config, meta_type, meta_id)
    return {"meta": meta_data}


@stremio_router.get("/{config_token}/stream/{stream_type}/{stream_id}.json")
async def stream_configured(
    config_token: str,
    stream_type: str,
    stream_id: str,
) -> dict[str, list[dict[str, Any]]]:
    """Configured stream endpoint."""
    config = decode_config(config_token)
    streams = await _get_streams(config, stream_type, stream_id)
    return {"streams": streams}
