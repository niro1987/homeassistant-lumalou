"""Bluetooth connection and state updates for Lumalou."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

import lumalou
import lumalou.client as lumalou_client
from lumalou import LumalouClient

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)


class _HomeAssistantBleakClient:
    """Use Home Assistant's retry-aware connector for the Lumalou library."""

    def __init__(self, device: BLEDevice) -> None:
        """Store the device for connection through Home Assistant."""
        self._device = device
        self._client: BleakClient | None = None

    async def connect(self) -> None:
        """Connect with Home Assistant's Bluetooth retry handling."""
        self._client = await establish_connection(
            BleakClientWithServiceCache,
            self._device,
            self._device.name or "Lumalou",
        )

    def __getattr__(self, name: str) -> Any:
        """Delegate GATT operations to the connected Bleak client."""
        if self._client is None:
            raise AttributeError(name)
        return getattr(self._client, name)


# lumalou 0.2.0 hard-codes BleakClient and has no client-factory option.
lumalou_client.BleakClient = _HomeAssistantBleakClient

_LIBRARY_ERRORS = (
    (lumalou.LumalouError,) if hasattr(lumalou, "LumalouError") else ()
)


class LumalouCoordinator(DataUpdateCoordinator[dict]):
    """Manage a Lumalou BLE connection and its state."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.address = address
        self.client: LumalouClient | None = None

    async def _async_connect(self) -> LumalouClient:
        """Connect through Home Assistant's Bluetooth adapter management."""
        device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if device is None:
            raise HomeAssistantError(
                "Bluetooth device is not currently reachable. Check its address "
                "and ensure a connectable Bluetooth adapter is nearby."
            )

        self.client = LumalouClient(device)
        await self.client.connect()
        await self.client.sync_time(dt_util.now())
        return self.client

    async def _async_update_data(self) -> dict:
        """Fetch a fresh device state."""
        try:
            client = self.client
            if client is None or not client.connected:
                client = await self._async_connect()
            state = await client.request_state(timeout=10)
        except (
            BleakError,
            HomeAssistantError,
            OSError,
            TimeoutError,
        ) + _LIBRARY_ERRORS as err:
            raise UpdateFailed(f"Unable to communicate with Lumalou: {err}") from err
        if state is None:
            raise UpdateFailed("Lumalou did not return its state")
        return state

    async def async_send(self, command: bytes) -> None:
        """Send a library command and refresh the reported state."""
        await self.async_send_sequence(command)

    async def async_send_sequence(self, *commands: bytes) -> None:
        """Send related commands before refreshing the reported state."""
        client = self.client
        if client is None or not client.connected:
            client = await self._async_connect()
        for command in commands:
            await client.send(command)
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Close the active BLE session."""
        if self.client is not None:
            await self.client.disconnect()
            self.client = None
