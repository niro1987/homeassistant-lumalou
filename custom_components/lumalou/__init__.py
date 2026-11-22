"""Lumalou Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration from YAML (not currently supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a Lumalou config entry.

    This starter scaffold establishes the HACS/config-entry install path. Device
    communication and entities will be added in a follow-up implementation.
    """
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Lumalou config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
