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
            LumalouCloudBacklight(coordinator, address),
            LumalouStarLight(coordinator, address),
        ]
    )


class LumalouCloudBacklight(LumalouEntity, LightEntity):
    """Controllable cloud backlight on the Lumalou."""

    _attr_color_mode: ClassVar[ColorMode] = ColorMode.ONOFF
    _attr_name = "Cloud backlight"
    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.ONOFF}

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the light."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_light"

    @property
    def is_on(self) -> bool:
        """Return whether the light is on."""
        return bool(self.coordinator.data["lightStatus"])

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the cloud backlight."""
        await self.coordinator.async_send(commands.set_global_state(lights_on=1))

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off only the cloud backlight."""
        await self.coordinator.async_send(commands.turn_off_backlight())


class LumalouStarLight(LumalouEntity, LightEntity):
    """Controllable star light on the Lumalou."""

    _attr_assumed_state: ClassVar[bool] = True
    _attr_color_mode: ClassVar[ColorMode] = ColorMode.BRIGHTNESS
    _attr_name = "Star light"
    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.BRIGHTNESS}

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the light."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_star_light"
        self._is_on = False
        self._brightness: int | None = None

    @property
    def is_on(self) -> bool:
        """Return the last commanded state; the device does not report the star separately."""
        return self._is_on

    @property
    def brightness(self) -> int | None:
        """Return the last commanded brightness on Home Assistant's 0-255 scale."""
        return self._brightness

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the star, optionally setting its brightness."""
        brightness = kwargs.get("brightness")
        if brightness is not None:
            level = max(1, round(brightness * 9 / 255))
        elif self._brightness is not None:
            level = max(1, round(self._brightness * 9 / 255))
        else:
            level = 9
        await self.coordinator.async_send(commands.set_led_brightness(level))
        self._is_on = True
        self._brightness = round(level * 255 / 9)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the star without changing the cloud backlight."""
        await self.coordinator.async_send(commands.set_led_brightness(0))
        self._is_on = False
        self.async_write_ha_state()
