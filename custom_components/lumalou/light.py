"""Light platform for Lumalou."""

from __future__ import annotations

from typing import ClassVar

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
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
    """Set up the Lumalou light."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LumalouLight(coordinator, entry.data[CONF_ADDRESS])])


class LumalouLight(LumalouEntity, LightEntity):
    """Controllable night light on the Lumalou."""

    _attr_color_mode: ClassVar[ColorMode] = ColorMode.BRIGHTNESS
    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.BRIGHTNESS}

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the light."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_light"

    @property
    def is_on(self) -> bool:
        """Return whether the light is on."""
        return bool(self.coordinator.data["lightStatus"])

    @property
    def brightness(self) -> int:
        """Return brightness on Home Assistant's 0-255 scale."""
        return round(self.coordinator.data["lightBrightness"] * 255 / 9)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the light, optionally setting its brightness."""
        brightness = kwargs.get("brightness")
        level = round(brightness * 9 / 255) if brightness is not None else None
        await self.coordinator.async_send(
            commands.set_global_state(lights_on=1, brightness=level)
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        await self.coordinator.async_send(commands.set_global_state(lights_on=0))
