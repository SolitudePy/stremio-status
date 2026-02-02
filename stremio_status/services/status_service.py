from __future__ import annotations

from typing import cast

import logging

from stremio_status.clients.gatus_client import get_client
from stremio_status.core.cache import TTLCache
from stremio_status.core.config import get_settings
from stremio_status.core.constants import ID_PREFIX
from stremio_status.core.models import CatalogItem, GatusEndpoint, Meta, Stream
from stremio_status.core.user_config import UserConfig
from stremio_status.utils import ui

logger = logging.getLogger(__name__)

settings = get_settings()
cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)


async def get_status_snapshot() -> list[GatusEndpoint]:
    """Fetch current endpoint statuses (cached).

    Returns cached data if fresh, otherwise fetches from Gatus.
    On fetch failure, returns empty list.
    """
    cached = cache.get("endpoints")
    if cached is not None:
        logger.debug("Returning cached endpoints")
        return cast(list[GatusEndpoint], cached)

    # Cache expired or empty - fetch fresh data
    client = get_client()
    try:
        logger.debug("Fetching fresh endpoints from Gatus")
        endpoints = await client.fetch_statuses()
        cache.set("endpoints", endpoints)
        logger.debug(f"Cached {len(endpoints)} endpoints")
        return endpoints
    except Exception as e:
        logger.error(f"Failed to fetch from Gatus: {e}")
        return []


def filter_by_addon_selection(
    endpoints: list[GatusEndpoint], config: UserConfig
) -> list[GatusEndpoint]:
    """Filter endpoints by addon selection only.

    - If config.addons is None: return all endpoints
    - If config.addons is []: return no endpoints
    - If config.addons has values: return only matching endpoints
    """
    if config.wants_no_addons():
        return []
    if config.addons is None:
        return endpoints

    wanted = {key.lower() for key in config.addons}
    return [
        ep for ep in endpoints if ep.key.lower() in wanted or ep.name.lower() in wanted
    ]


def filter_by_health(
    endpoints: list[GatusEndpoint], only_down: bool
) -> list[GatusEndpoint]:
    """Filter endpoints by health status.

    - If only_down is True: return only unhealthy endpoints
    - If only_down is False: return all endpoints
    """
    if not only_down:
        return endpoints
    return [ep for ep in endpoints if not ep.healthy]


def apply_config_filter(
    endpoints: list[GatusEndpoint], config: UserConfig
) -> list[GatusEndpoint]:
    """Apply all user config filters to endpoints.

    Combines addon selection and health filtering.
    """
    result = filter_by_addon_selection(endpoints, config)
    return filter_by_health(result, config.only_down)


async def build_catalog(config: UserConfig) -> list[CatalogItem]:
    """Build catalog items - always shows all health statuses.

    Only filters by addon selection, never by only_down.
    """
    endpoints = await get_status_snapshot()
    filtered = filter_by_addon_selection(endpoints, config)
    sorted_eps = ui.sort_endpoints(filtered)

    items: list[CatalogItem] = []
    for ep in sorted_eps:
        emoji = ui.status_emoji(ep.healthy)
        poster = ui.status_poster_url(ep.healthy)
        items.append(
            CatalogItem(
                id=f"{ID_PREFIX}{ep.key}",
                type="tv",
                name=f"{emoji} {ep.name}",
                poster=poster,
                description=ui.format_catalog_desc(ep),
            )
        )
    return items


async def build_meta(addon_id: str, config: UserConfig) -> Meta | None:
    """Build meta for a specific addon.

    Only filters by addon selection, not by health status.
    This ensures clicking a healthy addon in catalog doesn't 404.
    """
    endpoints = await get_status_snapshot()
    filtered = filter_by_addon_selection(endpoints, config)

    clean_id = addon_id.removeprefix(ID_PREFIX)
    for ep in filtered:
        if ep.key == clean_id or ep.name == clean_id:
            emoji = ui.status_emoji(ep.healthy)
            poster = ui.status_poster_url(ep.healthy)
            return Meta(
                id=f"{ID_PREFIX}{ep.key}",
                type="tv",
                name=f"{emoji} {ep.name}",
                poster=poster,
                description=ui.format_catalog_desc(ep),
            )
    return None


async def build_streams(config: UserConfig) -> list[Stream]:
    """Build stream list based on user config.

    Respects config.only_down to filter healthy/unhealthy endpoints.
    Sorts: DOWN first, then UP, alphabetically by name.
    """
    endpoints = await get_status_snapshot()
    filtered = apply_config_filter(endpoints, config)
    sorted_eps = ui.sort_endpoints(filtered)

    streams: list[Stream] = []
    for ep in sorted_eps:
        emoji = ui.status_emoji(ep.healthy)

        streams.append(
            Stream(
                name=f"{emoji} {ep.name}",
                description=ui.format_stream_desc(ep),
                url=f"{settings.public_base_url}",
                behaviorHints={"notWebReady": True},
            )
        )
    return streams
