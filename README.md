# Lumalou for Home Assistant

Control a Fisher-Price Lumalou (`gld09`) locally over Bluetooth Low Energy. The integration uses the [Lumalou Python library](https://github.com/stramanu/lumalou); it does not use a cloud service.

The integration adds:

- A cloud backlight light entity with on/off and brightness control, plus a
  separate color selector.
- A media player for audio playback, source selection, and volume.
- Automatic clock synchronization with Home Assistant's local time on every BLE connection.

This project is independent and is not affiliated with or endorsed by Mattel or Fisher-Price.

<!-- ha-marketplace:exclude-start -->
## Install from the Home Assistant [Marketplace](https://contributors.home-assistant.io/marketplace/)

[![Open Lumalou in the Home Assistant Marketplace](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=niro1987&repository=homeassistant-lumalou&category=integration)

For Home Assistant 2026.11 and newer:

1. Open the Marketplace link above and connect your GitHub account if prompted.
2. Add this repository as a custom repository, then install **Lumalou**.
3. Go to **Settings → Devices & services → Add integration** and search for **Lumalou**. Confirm the discovered device, or enter its Bluetooth address if it is not discovered.

This repository is not yet in the shared Marketplace catalog, so use the link above to add it as a custom repository. On a first install, Home Assistant loads the config flow without a restart. See the [Marketplace guide for custom repositories](https://contributors.home-assistant.io/marketplace/guides/catalog/#the-link-to-your-repository) for details.

### Older Home Assistant versions

Before Home Assistant 2026.11, install through HACS:

1. In HACS, open **Integrations → Custom repositories**.
2. Add `https://github.com/niro1987/homeassistant-lumalou` with category **Integration**.
3. Install **Lumalou**, restart Home Assistant, then add it under **Settings → Devices & services**.
<!-- ha-marketplace:exclude-end -->

## Requirements

- Home Assistant with a connectable Bluetooth adapter in range, or a supported Bluetooth proxy that allows connections.
- A Fisher-Price Lumalou (`gld09`).

Home Assistant's Bluetooth integration manages adapters and discovery. Keep the device powered on and within range while setting it up.

## Development

The integration is in `custom_components/lumalou`. The `lumalou` package implements the local BLE protocol and is installed by Home Assistant from PyPI. Marketplace uses the repository's `hacs.json` metadata; the HACS validation action and Hassfest run on pushes and pull requests. To list the repository in the shared Marketplace catalog, it must meet the [catalog requirements](https://contributors.home-assistant.io/marketplace/guides/catalog/#before-you-open-the-pull-request), including valid GitHub topics, passing validation, a published release, and an accepted listing PR in [hacs/default](https://github.com/hacs/default).

## License and attribution

This repository is MIT-licensed. The protocol implementation is the separate MIT-licensed [stramanu/lumalou](https://github.com/stramanu/lumalou) project. "Fisher-Price" and "Lumalou" are trademarks of their respective owners.
