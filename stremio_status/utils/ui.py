from __future__ import annotations

from datetime import datetime, timezone

from stremio_status.core.config import get_settings
from stremio_status.core.models import GatusEndpoint

# Bump this version when poster images are updated to bust client caches
POSTER_VERSION = "2"


def status_emoji(healthy: bool) -> str:
    """Return emoji for up/down status."""
    return "✅" if healthy else "⛔"


def status_poster_url(healthy: bool) -> str:
    """Return URL to static poster image for up/down status.

    Uses public_base_url setting to construct the full URL.
    Appends version query param for cache busting.
    """
    settings = get_settings()
    base_url = str(settings.public_base_url).rstrip("/")
    filename = "up.png" if healthy else "down.png"
    return f"{base_url}/static/{filename}?v={POSTER_VERSION}"


def format_relative_time(iso_timestamp: str | None) -> str:
    """Convert ISO timestamp to relative time like '2m ago'.

    Returns "unknown" if timestamp is None.
    Returns original string if parsing fails.
    """
    if not iso_timestamp:
        return "unknown"

    try:
        # Parse ISO timestamp (handle 'Z' suffix)
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt

        seconds = int(diff.total_seconds())
        if seconds < 0:
            return "just now"
        elif seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"
    except (ValueError, TypeError):
        return iso_timestamp


def _get_common_details(ep: GatusEndpoint) -> tuple[str, str, str]:
    """Extract common status details for formatting."""
    status = "Up" if ep.healthy else "Down"
    latency = f"{int(ep.response_time)}ms" if ep.response_time else "n/a"
    last_check = format_relative_time(ep.last_updated)
    return status, latency, last_check


def format_status_desc(ep: GatusEndpoint) -> str:
    """Format description with status details (multi-line)."""
    status, latency, last_check = _get_common_details(ep)
    return (
        f"[Stremio Status]\n"
        f"Status: {status}\n"
        f"Latency: {latency}\n"
        f"Last Check: {last_check}"
    )


# Backward compatibility / specific aliases
format_catalog_desc = format_status_desc
format_stream_desc = format_status_desc


def sort_endpoints(endpoints: list[GatusEndpoint]) -> list[GatusEndpoint]:
    """Sort endpoints: unhealthy first, then healthy, then by name."""
    return sorted(endpoints, key=lambda ep: (ep.healthy, ep.name.lower()))


def get_status_summary(endpoints: list[GatusEndpoint]) -> tuple[str, str, int, str]:
    """Calculate monitoring status summary for endpoints.

    Returns emoji (✅/⚠️/⛔), status text, total count, and last check time.
    Emoji indicates overall health: all up, mixed, or all down.
    """
    total = len(endpoints)
    down = sum(1 for ep in endpoints if not ep.healthy)

    if down == 0:
        emoji = "✅"
        status = "All operational"
    elif down == total:
        emoji = "⛔"
        status = "All down"
    else:
        emoji = "⚠️"
        status = f"{down} down, {total - down} up"

    recent_ts = max(
        (ep.last_updated for ep in endpoints if ep.last_updated),
        default=None,
    )
    last_check = format_relative_time(recent_ts)

    return emoji, status, total, last_check


def format_watchdog_desc(status: str, total: int, last_check: str) -> str:
    """Format watchdog summary description for monitoring status."""
    return (
        f"[Stremio Status]\n"
        f"Monitoring: {total} addon{'s' if total != 1 else ''}\n"
        f"Status: {status}\n"
        f"Last Check: {last_check}"
    )
