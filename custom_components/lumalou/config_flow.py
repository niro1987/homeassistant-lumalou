"""Config flow for the Lumalou integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


class LumalouConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lumalou."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Ask for the device's Bluetooth address."""
        errors: dict[str, str] = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip()
            if not address:
                errors[CONF_ADDRESS] = "invalid_address"
            else:
                await self.async_set_unique_id(address.casefold())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Lumalou ({address})",
                    data={CONF_ADDRESS: address},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): str}),
            errors=errors,
        )


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Keep the config flow module importable across HA versions."""
    return True


@callback
def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    """Return the options flow handler (reserved for future settings)."""
    return LumalouOptionsFlow(config_entry)


class LumalouOptionsFlow(config_entries.OptionsFlow):
    """Options flow placeholder."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry
