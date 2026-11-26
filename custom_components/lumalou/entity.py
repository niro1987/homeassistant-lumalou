"""Shared entity helpers for Lumalou."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LumalouCoordinator


class LumalouEntity(CoordinatorEntity[LumalouCoordinator]):
    """Base entity for a Lumalou device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_BLUETOOTH, address)},
            identifiers={(DOMAIN, address.casefold())},
            manufacturer="Mattel",
            model="Lumalou gld09",
            name="Lumalou",
        )
