"""Media player platform for Lumalou audio."""

from __future__ import annotations

from typing import ClassVar

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from lumalou import Audio, Song, commands

from .const import DOMAIN
from .coordinator import LumalouCoordinator
from .entity import LumalouEntity

_AUDIO_SOURCES = {
    source.name.replace("_", " ").title(): source for source in Audio
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lumalou media player."""
    coordinator: LumalouCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LumalouMediaPlayer(coordinator, entry.data[CONF_ADDRESS])])


class LumalouMediaPlayer(LumalouEntity, MediaPlayerEntity):
    """Control Lumalou audio playback and volume."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )
    _attr_source_list: ClassVar[list[str]] = list(_AUDIO_SOURCES)

    def __init__(self, coordinator: LumalouCoordinator, address: str) -> None:
        """Initialize the media player."""
        super().__init__(coordinator, address)
        self._attr_unique_id = f"{address.casefold()}_audio"
        self._attr_name = "Audio"

    @property
    def state(self) -> MediaPlayerState:
        """Return the playback state."""
        return (
            MediaPlayerState.PLAYING
            if self.coordinator.data["musicStatus"]
            else MediaPlayerState.IDLE
        )

    @property
    def volume_level(self) -> float:
        """Return volume on Home Assistant's 0-1 scale."""
        return self.coordinator.data["currentVolume"] / 9

    @property
    def media_title(self) -> str | None:
        """Return the current track when the device reports one."""
        try:
            song = Song(self.coordinator.data["currentSong"])
        except ValueError:
            return None
        if song is Song.NO_SONG:
            return None
        return song.name.replace("_", " ").title()

    async def async_media_play(self) -> None:
        """Start the default sleep playlist."""
        await self.coordinator.async_send_sequence(
            commands.play_audio(Audio.SLEEP_PLAYLIST),
            refresh=False,
            optimistic_state={"musicStatus": 1},
        )

    async def async_media_stop(self) -> None:
        """Stop audio playback."""
        await self.coordinator.async_send_sequence(
            commands.turn_off_audio(),
            refresh=False,
            optimistic_state={"musicStatus": 0},
        )

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the device volume."""
        level = round(volume * 9)
        await self.coordinator.async_send_sequence(
            commands.set_volume(level),
            refresh=False,
            optimistic_state={"currentVolume": level},
        )

    async def async_select_source(self, source: str) -> None:
        """Start the selected audio source."""
        await self.coordinator.async_send_sequence(
            commands.play_audio(_AUDIO_SOURCES[source]),
            refresh=False,
            optimistic_state={"musicStatus": 1},
        )
