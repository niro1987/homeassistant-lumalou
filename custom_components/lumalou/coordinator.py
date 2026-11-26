"""Bluetooth connection and state updates for Lumalou."""

from __future__ import annotations

import asyncio
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
        self._io_lock = asyncio.Lock()

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

        self.client = LumalouClient(device, on_state=self._handle_state_update)
        await self.client.connect()
        await self.client.sync_time(dt_util.now())
        return self.client

    def _handle_state_update(self, state: dict) -> None:
        """Publish device-initiated state updates without waiting for polling."""
        self.async_set_updated_data(state)

    async def _async_update_data(self) -> dict:
        """Fetch a fresh device state."""
        async with self._io_lock:
            try:
                client = self.client
                if client is None or not client.connected:
                    client = await self._async_connect()
                state = await self._async_request_state(client)
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
        """Send a command and immediately publish the resulting device state."""
        async with self._io_lock:
            client = self.client
            if client is None or not client.connected:
                client = await self._async_connect()
            await client.send(command)
            state = await self._async_request_state(client)
            if state is None:
                raise HomeAssistantError("Lumalou did not return its state")
            self.async_set_updated_data(state)

    async def _async_request_state(self, client: LumalouClient) -> dict | None:
        """Read the current device state."""
        return await client.request_state(timeout=10)

    async def async_sync_time(self) -> None:
        """Synchronize the device clock with Home Assistant's local time."""
        async with self._io_lock:
            client = self.client
            if client is None or not client.connected:
                await self._async_connect()
            else:
                await client.sync_time(dt_util.now())

    async def async_shutdown(self) -> None:
        """Close the active BLE session."""
        if self.client is not None:
            await self.client.disconnect()
            self.client = None
