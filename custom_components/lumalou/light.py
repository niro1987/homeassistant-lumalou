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
    """Set up the Lumalou lights."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    address = entry.data[CONF_ADDRESS]
    async_add_entities([LumalouCloudBacklight(coordinator, address)])


class LumalouCloudBacklight(LumalouEntity, LightEntity):
    """Controllable cloud backlight on the Lumalou."""

    _attr_color_mode: ClassVar[ColorMode] = ColorMode.BRIGHTNESS
    _attr_name = "Cloud backlight"
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
        """Turn on the cloud backlight, optionally setting its brightness."""
        brightness = kwargs.get("brightness")
        level = max(1, round(brightness * 9 / 255)) if brightness is not None else None
        if self.is_on:
            if level is not None:
                await self.coordinator.async_send(commands.set_led_brightness(level))
            return

        await self.coordinator.async_send_sequence(
            commands.set_global_on(True),
            commands.set_global_state(lights_on=1, brightness=level),
            refresh=False,
            optimistic_state={
                "lightStatus": 1,
                **({"lightBrightness": level} if level is not None else {}),
            },
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off only the cloud backlight."""
        await self.coordinator.async_send_sequence(
            commands.turn_off_backlight(),
            refresh=False,
            optimistic_state={"lightStatus": 0},
        )
