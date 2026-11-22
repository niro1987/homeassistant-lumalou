# Lumalou for Home Assistant

A Home Assistant custom integration scaffold for local Bluetooth control of the Fisher-Price Lumalou (`gld09`). It is intended for installation through the [Home Assistant Community Store (HACS)](https://hacs.xyz/).

> **Scaffold status:** This repository currently provides the HACS package structure and a basic config flow only. Bluetooth communication, entities, controls, and device discovery are not implemented yet. Adding the integration does not control the device at this stage.

The device protocol implementation is provided by [`stramanu/lumalou`](https://github.com/stramanu/lumalou), an independent local BLE project. This integration is not affiliated with or endorsed by Mattel or Fisher-Price.

## Install with HACS

1. Install and configure HACS in Home Assistant.
2. In HACS, open **Integrations** and select the three-dot menu, then **Custom repositories**.
3. Add `https://github.com/niro1987/lumalou-home-assistant` and choose **Integration** as the category.
4. Find **Lumalou** in HACS and install it.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration**, search for **Lumalou**, and enter the device Bluetooth address when prompted.

## Requirements

- Home Assistant with Bluetooth support and a Bluetooth adapter within range of the device.
- Fisher-Price Lumalou (`gld09`).

## Development

The integration lives in `custom_components/lumalou`. The `manifest.json` pins the upstream `lumalou` Python package. Once device support is implemented, add platform entities and tests here.

## License and attribution

This repository is MIT-licensed. Lumalou protocol and Python library: [stramanu/lumalou](https://github.com/stramanu/lumalou). "Fisher-Price" and "Lumalou" are trademarks of their respective owners.
