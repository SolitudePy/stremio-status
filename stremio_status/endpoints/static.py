from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from stremio_status.core.constants import STATIC_DIR

logger = logging.getLogger(__name__)

static_router = APIRouter()

# Specific posters to cache aggressively
POSTER_FILES = {"up.png", "down.png"}

# 1 year in seconds
CACHE_MAX_AGE = 31536000


async def _serve_poster(filename: str) -> FileResponse:
    """Serve specific poster file with aggressive caching."""
    file_path = STATIC_DIR / filename
    if not file_path.exists():
        logger.error(f"Poster file missing: {file_path}")
        raise HTTPException(status_code=404, detail="Not found")

    return FileResponse(
        path=file_path,
        media_type="image/png",
        headers={
            "Cache-Control": f"public, max-age={CACHE_MAX_AGE}, immutable",
        },
    )


@static_router.get("/static/up.png")
async def up_poster() -> FileResponse:
    return await _serve_poster("up.png")


@static_router.get("/static/down.png")
async def down_poster() -> FileResponse:
    return await _serve_poster("down.png")


@static_router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    file_path = STATIC_DIR / "favicon.ico"
    return FileResponse(path=file_path, media_type="image/x-icon")
