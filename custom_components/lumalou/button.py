"""Diagnostic buttons for Lumalou."""

from __future__ import annotations

from typing import ClassVar

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from lumalou import commands

from .const import DOMAIN
from .coordinator import LumalouCoordinator
from .entity import LumalouEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up temporary master-power test buttons."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    address = entry.data[CONF_ADDRESS]
    async_add_entities(
        [
            LumalouMasterPowerTestButton(coordinator, address, True),
            LumalouMasterPowerTestButton(coordinator, address, False),
        ]
    )


class LumalouMasterPowerTestButton(LumalouEntity, ButtonEntity):
    """Send one master on/off command for hardware testing."""

    _attr_entity_category: ClassVar[EntityCategory] = EntityCategory.CONFIG

    def __init__(
        self, coordinator: LumalouCoordinator, address: str, turn_on: bool
    ) -> None:
        """Initialize a master-power test button."""
        super().__init__(coordinator, address)
        self._turn_on = turn_on
        action = "on" if turn_on else "off"
        self._attr_unique_id = f"{address.casefold()}_master_power_{action}_test"
        self._attr_name = f"Master power {action} (test)"

    async def async_press(self) -> None:
        """Send only the device-wide master on/off command."""
        await self.coordinator.async_send(commands.set_global_on(self._turn_on))
