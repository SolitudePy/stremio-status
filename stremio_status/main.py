from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from stremio_status.clients.gatus_client import get_client
from stremio_status.core.config import get_settings
from stremio_status.core.constants import STATIC_DIR
from stremio_status.endpoints.configurator import configurator_router
from stremio_status.endpoints.health import health_router
from stremio_status.endpoints.static import static_router
from stremio_status.endpoints.stremio import stremio_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Lazy init client; nothing else to start
    yield
    client = get_client()
    try:
        await client.close()
    except Exception:
        pass


def create_app() -> FastAPI:
    app = FastAPI(title="Stremio Status", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(stremio_router)
    app.include_router(configurator_router)
    app.include_router(static_router)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()


def run() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    uvicorn.run(
        "stremio_status.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    run()
