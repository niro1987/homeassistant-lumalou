"""Config flow for the Lumalou integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN


class LumalouConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lumalou."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Set up a device by Bluetooth address."""
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

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ):
        """Handle a device discovered by Home Assistant Bluetooth."""
        await self.async_set_unique_id(discovery_info.address.casefold())
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {
            "name": discovery_info.name or "Lumalou"
        }
        self._discovery_info = discovery_info
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input=None):
        """Confirm setup of a discovered Lumalou."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.context["title_placeholders"]["name"],
                data={CONF_ADDRESS: self._discovery_info.address},
            )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self.context["title_placeholders"],
        )
