"""Select platform for Lumalou light colors."""

from __future__ import annotations

from typing import ClassVar

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from lumalou import ClockFormat, Color, commands

from .const import DOMAIN
from .coordinator import LumalouCoordinator
from .entity import LumalouEntity

_COLOR_OPTIONS = {color.name.replace("_", " ").title(): color for color in Color}
_CLOCK_FORMAT_OPTIONS = {
    "12-hour (AM/PM)": ClockFormat.H12,
    "24-hour": ClockFormat.H24,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lumalou selectors."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    address = entry.data[CONF_ADDRESS]
    async_add_entities(
        [
            LumalouColorSelect(coordinator, address),
            LumalouClockFormatSelect(coordinator, address),
        ]
    )


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


class LumalouClockFormatSelect(LumalouEntity, SelectEntity):
    """Select the clock's 12-hour or 24-hour display format."""

    _attr_entity_category: ClassVar[EntityCategory] = EntityCategory.CONFIG
    _attr_options: ClassVar[list[str]] = list(_CLOCK_FORMAT_OPTIONS)

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the clock format selector."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_clock_format"
        self._attr_name = "Clock format"

    @property
    def current_option(self) -> str | None:
        """Return the currently configured clock format."""
        try:
            clock_format = ClockFormat(self.coordinator.data["clockFormat"])
        except ValueError:
            return None
        return next(
            (
                option
                for option, value in _CLOCK_FORMAT_OPTIONS.items()
                if value == clock_format
            ),
            None,
        )

    async def async_select_option(self, option: str) -> None:
        """Set the clock format without changing its display or brightness."""
        state = self.coordinator.data
        clock_format = _CLOCK_FORMAT_OPTIONS[option]
        await self.coordinator.async_send_sequence(
            commands.set_clock_settings(
                bool(state["clockDisplay"]),
                state["clockBrightness"],
                clock_format,
            ),
            refresh=False,
            optimistic_state={"clockFormat": int(clock_format)},
        )
