"""Button platform for Lumalou."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LumalouCoordinator
from .entity import LumalouEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lumalou time-sync button."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [LumalouTimeSyncButton(coordinator, entry.data[CONF_ADDRESS])]
    )


class LumalouTimeSyncButton(LumalouEntity, ButtonEntity):
    """Synchronize the device clock with Home Assistant."""

    _attr_name = "Sync time"

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the time-sync button."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_time_sync"

    async def async_press(self) -> None:
        """Set the device clock to Home Assistant's current local time."""
        await self.coordinator.async_sync_time()
