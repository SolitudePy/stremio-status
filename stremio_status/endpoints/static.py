from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from stremio_status.core.constants import STATIC_DIR
from stremio_status.utils.ui import POSTER_VERSION

logger = logging.getLogger(__name__)

static_router = APIRouter()

# Allowed image files (HTML served by configurator.py)
ALLOWED_FILES = {"up.png", "down.png"}

# 1 year in seconds
CACHE_MAX_AGE = 31536000


@static_router.get("/static/{filename}")
async def get_static_file(filename: str) -> FileResponse:
    """Serve static image files with aggressive caching."""
    if filename not in ALLOWED_FILES:
        logger.warning(f"Attempt to access unauthorized file: {filename}")
        raise HTTPException(status_code=404, detail="Not found")

    file_path = STATIC_DIR / filename
    if not file_path.exists():
        logger.error(f"Static file missing on disk: {file_path}")
        raise HTTPException(status_code=404, detail="Not found")

    return FileResponse(
        path=file_path,
        media_type="image/png",
        headers={
            "Cache-Control": f"public, max-age={CACHE_MAX_AGE}, immutable",
            "ETag": f'"{filename.split(".")[0]}-v{POSTER_VERSION}"',
        },
    )
