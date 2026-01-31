from __future__ import annotations

import time
from typing import Any, Optional


class TTLCache:
    """Simple in-memory cache with time-to-live expiration."""

    def __init__(self, ttl_seconds: int) -> None:
        self.ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired, None otherwise."""
        entry = self._store.get(key)
        if not entry:
            return None
        expires, value = entry
        if time.time() > expires:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        """Store value with TTL expiration."""
        self._store[key] = (time.time() + self.ttl, value)
