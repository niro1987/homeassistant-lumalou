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
    async_add_entities(
        [
            LumalouLight(coordinator, address),
            LumalouCloudBacklight(coordinator, address),
        ]
    )


class LumalouLight(LumalouEntity, LightEntity):
    """Controllable star light on the Lumalou."""

    _attr_color_mode: ClassVar[ColorMode] = ColorMode.BRIGHTNESS
    _attr_name = "Star light"
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
        await self.coordinator.async_send(commands.set_global_on(True))
        await self.coordinator.async_send(
            commands.set_global_state(lights_on=1, brightness=level)
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        await self.coordinator.async_send(commands.set_global_state(lights_on=0))


class LumalouCloudBacklight(LumalouEntity, LightEntity):
    """Controllable light around the Lumalou cloud."""

    _attr_color_mode: ClassVar[ColorMode] = ColorMode.BRIGHTNESS
    _attr_name = "Cloud backlight"
    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.BRIGHTNESS}

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the cloud backlight."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_cloud_backlight"
        self._is_on: bool | None = None
        self._level: int | None = None

    @property
    def is_on(self) -> bool | None:
        """Return the last commanded state; the protocol has no global-state field."""
        return self._is_on

    @property
    def brightness(self) -> int | None:
        """Return brightness on Home Assistant's 0-255 scale."""
        if self._level is None:
            return None
        return round(self._level * 255 / 9)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the cloud backlight, optionally setting its brightness."""
        brightness = kwargs.get("brightness")
        if brightness is None:
            brightness = round(self._level * 255 / 9) if self._level else 255
        level = max(1, round(brightness * 9 / 255))
        await self.coordinator.async_send(commands.set_led_brightness(level))
        self._is_on = True
        self._level = level
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the cloud backlight."""
        await self.coordinator.async_send(commands.turn_off_backlight())
        self._is_on = False
        self.async_write_ha_state()
