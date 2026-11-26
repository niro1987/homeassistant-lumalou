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
    """Set up temporary diagnostic command buttons."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    address = entry.data[CONF_ADDRESS]
    buttons = (
        (
            "Master power on (test)",
            "master_power_on_test",
            commands.set_global_on(True),
        ),
        (
            "Master power off (test)",
            "master_power_off_test",
            commands.set_global_on(False),
        ),
        (
            "Global state lights on (test)",
            "global_state_lights_on_test",
            commands.set_global_state(lights_on=1),
        ),
        (
            "Global state lights off (test)",
            "global_state_lights_off_test",
            commands.set_global_state(lights_on=0),
        ),
        (
            "Cloud backlight off (test)",
            "cloud_backlight_off_test",
            commands.turn_off_backlight(),
        ),
        (
            "LED brightness 0 (test)",
            "led_brightness_0_test",
            commands.set_led_brightness(0),
        ),
        (
            "LED brightness 9 (test)",
            "led_brightness_9_test",
            commands.set_led_brightness(9),
        ),
    )
    async_add_entities(
        LumalouCommandTestButton(coordinator, address, name, unique_id, command)
        for name, unique_id, command in buttons
    )


class LumalouCommandTestButton(LumalouEntity, ButtonEntity):
    """Send one Lumalou command for hardware testing."""

    _attr_entity_category: ClassVar[EntityCategory] = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: LumalouCoordinator,
        address: str,
        name: str,
        unique_id: str,
        command: bytes,
    ) -> None:
        """Initialize a diagnostic command button."""
        super().__init__(coordinator, address)
        self._command = command
        self._attr_unique_id = f"{address.casefold()}_{unique_id}"
        self._attr_name = name

    async def async_press(self) -> None:
        """Send only the selected diagnostic command."""
        await self.coordinator.async_send(self._command)
