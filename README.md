# Lumalou for Home Assistant

Control a Fisher-Price Lumalou (`gld09`) locally over Bluetooth Low Energy. The integration uses the [Lumalou Python library](https://github.com/stramanu/lumalou); it does not use a cloud service.

The integration adds:

- A light entity for power and brightness.
- A color selector for the light's built-in colors.
- A media player for audio playback, source selection, and volume.

This project is independent and is not affiliated with or endorsed by Mattel or Fisher-Price.

## Install with HACS

1. Install and configure [HACS](https://www.hacs.xyz/docs/use/).
2. In HACS, open **Integrations** and select **Custom repositories** from the menu.
3. Add `https://github.com/niro1987/lumalou-home-assistant` with category **Integration**.
4. Install **Lumalou**, then restart Home Assistant.
5. In **Settings → Devices & services**, choose **Add integration** and search for **Lumalou**. If Bluetooth discovery finds the device, confirm it; otherwise enter its Bluetooth address.

The repository is HACS-compatible. To appear in HACS's default store, it still needs a successful HACS validation, a published GitHub release, and acceptance of a listing PR in [hacs/default](https://github.com/hacs/default).

## Requirements

- Home Assistant with a connectable Bluetooth adapter in range, or a supported Bluetooth proxy that allows connections.
- A Fisher-Price Lumalou (`gld09`).

Home Assistant's Bluetooth integration manages adapters and discovery. Keep the device powered on and within range while setting it up.

## Development

The integration is in `custom_components/lumalou`. The `lumalou` package implements the local BLE protocol and is installed by Home Assistant from PyPI. HACS and Hassfest validation run on pushes and pull requests.

## License and attribution

This repository is MIT-licensed. The protocol implementation is the separate MIT-licensed [stramanu/lumalou](https://github.com/stramanu/lumalou) project. "Fisher-Price" and "Lumalou" are trademarks of their respective owners.
