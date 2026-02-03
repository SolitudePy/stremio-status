from __future__ import annotations

from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
