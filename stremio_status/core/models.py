from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class GatusEndpoint(BaseModel):
    """Health status of a monitored endpoint from Gatus."""

    name: str
    group: str
    key: str
    healthy: bool
    uptime: Optional[float] = None
    response_time: Optional[float] = Field(default=None, alias="responseTime")
    last_updated: Optional[str] = Field(default=None, alias="lastUpdated")


class StremioManifest(BaseModel):
    """Stremio addon manifest describing capabilities."""

    id: str
    version: str
    name: str
    description: str
    logo: Optional[str] = None
    resources: list[str | dict[str, Any]]
    types: list[str]
    catalogs: list[dict[str, str]]
    idPrefixes: Optional[list[str]] = None
    behaviorHints: dict[str, Any] = Field(default_factory=dict)


class CatalogItem(BaseModel):
    """Item displayed in the Stremio catalog grid."""

    id: str
    type: str
    name: str
    poster: Optional[str] = None
    description: Optional[str] = None


class Meta(BaseModel):
    """Detailed metadata for a catalog item."""

    id: str
    type: str
    name: str
    poster: Optional[str] = None
    description: Optional[str] = None


class Stream(BaseModel):
    """Stream entry shown when user clicks a catalog item."""

    name: str
    description: Optional[str] = None
    url: str
    behaviorHints: dict[str, Any] = Field(default_factory=dict)
