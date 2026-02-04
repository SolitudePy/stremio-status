from __future__ import annotations

import base64
import binascii
import json

from pydantic import BaseModel, Field


class UserConfig(BaseModel):
    """User configuration for addon filtering.

    Attributes:
        addons: list of addon keys to monitor. Empty list = no addons.
                If None (omitted from JSON), means "all addons".
        only_down: If True, only show unhealthy addons in streams.
        hide_addon_status_catalog: If True, hide the "Addon Status" catalog in Stremio.
    """

    addons: list[str] | None = None  # None = all addons, [] = no addons
    only_down: bool = Field(default=True, alias="onlyDown")
    hide_addon_status_catalog: bool = Field(
        default=False, alias="hideAddonStatusCatalog"
    )

    def wants_all_addons(self) -> bool:
        """Check if config means 'show all addons'."""
        return self.addons is None

    def wants_no_addons(self) -> bool:
        """Check if config explicitly means 'no addons'."""
        return self.addons is not None and len(self.addons) == 0


def decode_config(token: str) -> UserConfig:
    """Decode base64 token to UserConfig.

    Returns default config (all addons, only DOWN) on any error.
    """
    try:
        padded = token + "=" * (-len(token) % 4)
        json_bytes = base64.urlsafe_b64decode(padded)
        data = json.loads(json_bytes)
        return UserConfig.model_validate(data)
    except (ValueError, json.JSONDecodeError, binascii.Error):
        return UserConfig()
    except Exception:
        # Pydantic validation errors or unexpected issues
        return UserConfig()
