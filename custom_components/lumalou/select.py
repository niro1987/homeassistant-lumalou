"""Select platform for Lumalou light colors."""

from __future__ import annotations

from typing import ClassVar

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from lumalou import Color, commands

from .const import DOMAIN
from .coordinator import LumalouCoordinator
from .entity import LumalouEntity

_COLOR_OPTIONS = {color.name.replace("_", " ").title(): color for color in Color}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lumalou color selector."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LumalouColorSelect(coordinator, entry.data[CONF_ADDRESS])])


class LumalouColorSelect(LumalouEntity, SelectEntity):
    """Select the Lumalou light color."""

    _attr_options: ClassVar[list[str]] = list(_COLOR_OPTIONS)

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the selector."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_light_color"
        self._attr_name = "Light color"

    @property
    def current_option(self) -> str | None:
        """Return the currently selected color."""
        try:
            color = Color(self.coordinator.data["lightColor"])
        except ValueError:
            return None
        return color.name.replace("_", " ").title()

    async def async_select_option(self, option: str) -> None:
        """Set the light color."""
        await self.coordinator.async_send(
            commands.set_light_color(_COLOR_OPTIONS[option])
        )
