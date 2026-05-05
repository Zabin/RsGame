"""
sound.py — Music composition and sound effects system for Bunny Garden Adventure.

Enables dynamic song composition, multi-channel mixing, and asset-driven audio
without requiring code changes for new melodies or sound effects.
"""


class Note:
    """A single note with frequency, duration, and properties."""

    def __init__(self, frequency, duration, volume=15, panning=0):
        """
        Args:
            frequency: Game Boy frequency value (2048-131072, Hz equivalent)
            duration: Duration in frames (1 frame = 1/60 second)
            volume: Volume level (0-15)
            panning: Stereo panning (-100 to 100, 0 = center)
        """
        self.frequency = frequency
        self.duration = duration
        self.volume = max(0, min(15, volume))
        self.panning = max(-100, min(100, panning))

    def __repr__(self):
        return f"Note(freq={self.frequency} dur={self.duration}f vol={self.volume})"


class Silence:
    """A silent period (rest) in a song."""

    def __init__(self, duration):
        """
        Args:
            duration: Duration in frames
        """
        self.duration = duration

    def __repr__(self):
        return f"Silence({self.duration}f)"


class Channel:
    """A single audio channel (e.g., Wave, Pulse 1, Pulse 2, Noise)."""

    TYPES = {"pulse1", "pulse2", "wave", "noise"}

    def __init__(self, channel_type, name=""):
        """
        Args:
            channel_type: "pulse1", "pulse2", "wave", or "noise"
            name: Human-readable name
        """
        if channel_type not in self.TYPES:
            raise ValueError(f"Invalid channel type: {channel_type}")
        self.channel_type = channel_type
        self.name = name
        self.notes = []

    def add_note(self, frequency, duration, volume=15, panning=0):
        """Add a note to this channel."""
        note = Note(frequency, duration, volume, panning)
        self.notes.append(note)
        return note

    def add_silence(self, duration):
        """Add a rest to this channel."""
        silence = Silence(duration)
        self.notes.append(silence)
        return silence

    def total_duration(self):
        """Get total duration of all notes in frames."""
        return sum(n.duration for n in self.notes)

    def __repr__(self):
        return f"Channel({self.channel_type} {self.name} {len(self.notes)} notes)"


class Song:
    """A complete song with one or more channels."""

    def __init__(self, name, tempo=120, loop=False):
        """
        Args:
            name: Song name
            tempo: Beats per minute (for reference; durations in frames)
            loop: Whether song should loop
        """
        self.name = name
        self.tempo = tempo
        self.loop = loop
        self.channels = {}

    def create_channel(self, channel_type, name=""):
        """Create and register a new channel."""
        if channel_type not in Channel.TYPES:
            raise ValueError(f"Invalid channel type: {channel_type}")
        key = f"{channel_type}_{len([c for c in self.channels.values() if c.channel_type == channel_type])}"
        channel = Channel(channel_type, name or key)
        self.channels[key] = channel
        return channel

    def get_channel(self, key):
        """Get a channel by key."""
        return self.channels.get(key)

    def list_channels(self):
        """Get all channels."""
        return list(self.channels.values())

    def total_duration(self):
        """Get song duration (max duration of all channels)."""
        if not self.channels:
            return 0
        return max(ch.total_duration() for ch in self.channels.values())

    def encode(self):
        """Generate binary encoding of song for ROM."""
        data = bytearray()
        # Song header: tempo (1 byte), loop (1 byte), channel count (1 byte)
        data.append((self.tempo >> 8) & 0xFF)
        data.append(self.tempo & 0xFF)
        data.append(1 if self.loop else 0)
        data.append(len(self.channels))

        # Channel data
        for channel in self.channels.values():
            # Channel header: type (1 byte), name length (1 byte)
            type_byte = {"pulse1": 0, "pulse2": 1, "wave": 2, "noise": 3}[
                channel.channel_type
            ]
            data.append(type_byte)
            data.append(len(channel.name))
            for c in channel.name:
                data.append(ord(c) & 0xFF)

            # Notes in channel
            data.append(len(channel.notes))
            for note in channel.notes:
                if isinstance(note, Note):
                    # Note: marker (0x00), frequency (2 bytes), duration (1 byte), volume (1 byte)
                    data.append(0x00)
                    data.append(note.frequency & 0xFF)
                    data.append((note.frequency >> 8) & 0xFF)
                    data.append(min(255, note.duration))
                    data.append(note.volume)
                elif isinstance(note, Silence):
                    # Silence: marker (0xFF), duration (1 byte)
                    data.append(0xFF)
                    data.append(min(255, note.duration))

        return bytes(data)

    def __repr__(self):
        return f"Song({self.name} {self.tempo}bpm {len(self.channels)} channels)"


class SoundEffect:
    """A short sound effect (burst, pop, chime, etc.)."""

    def __init__(self, name, channel_type, frequency, duration, volume=15):
        """
        Args:
            name: Effect name
            channel_type: "pulse1", "pulse2", "wave", or "noise"
            frequency: Frequency value
            duration: Duration in frames
            volume: Volume (0-15)
        """
        self.name = name
        self.channel_type = channel_type
        self.frequency = frequency
        self.duration = duration
        self.volume = max(0, min(15, volume))

    def encode(self):
        """Generate binary encoding for ROM."""
        data = bytearray()
        type_byte = {"pulse1": 0, "pulse2": 1, "wave": 2, "noise": 3}.get(
            self.channel_type, 0
        )
        data.append(type_byte)
        data.append(self.frequency & 0xFF)
        data.append((self.frequency >> 8) & 0xFF)
        data.append(self.duration)
        data.append(self.volume)
        return bytes(data)

    def __repr__(self):
        return f"SoundEffect({self.name} {self.channel_type})"


class SoundLibrary:
    """Central registry for all songs and sound effects."""

    def __init__(self):
        self.songs = {}  # name -> Song
        self.effects = {}  # name -> SoundEffect

    def register_song(self, song):
        """Register a song."""
        if song.name in self.songs:
            raise ValueError(f"Song '{song.name}' already registered")
        self.songs[song.name] = song
        return song

    def register_effect(self, effect):
        """Register a sound effect."""
        if effect.name in self.effects:
            raise ValueError(f"Effect '{effect.name}' already registered")
        self.effects[effect.name] = effect
        return effect

    def get_song(self, name):
        """Retrieve a song by name."""
        return self.songs.get(name)

    def get_effect(self, name):
        """Retrieve a sound effect by name."""
        return self.effects.get(name)

    def list_songs(self):
        """List all registered songs."""
        return list(self.songs.values())

    def list_effects(self):
        """List all registered sound effects."""
        return list(self.effects.values())

    def build_song_data(self):
        """Generate complete binary song data for ROM."""
        data = bytearray()
        song_addrs = {}
        for song in self.songs.values():
            song_addrs[song.name] = len(data)
            for b in song.encode():
                data.append(b)
        return bytes(data), song_addrs

    def build_effect_data(self):
        """Generate complete binary effect data for ROM."""
        data = bytearray()
        effect_addrs = {}
        for effect in self.effects.values():
            effect_addrs[effect.name] = len(data)
            for b in effect.encode():
                data.append(b)
        return bytes(data), effect_addrs

    def __repr__(self):
        return f"SoundLibrary({len(self.songs)} songs, {len(self.effects)} effects)"


# Global sound library instance
library = SoundLibrary()


def load_sounds_from_json(json_path):
    """Load song and effect definitions from JSON asset file."""
    import json
    from pathlib import Path

    json_file = Path(json_path)
    if not json_file.exists():
        raise FileNotFoundError(f"Asset file not found: {json_path}")

    with open(json_file) as f:
        assets = json.load(f)

    # Load sound effects
    if "effects" in assets:
        for effect_name, effect_def in assets["effects"].items():
            channel_type = effect_def.get("channel", "pulse1")
            frequency = effect_def.get("frequency", 0)
            duration = effect_def.get("duration", 1)
            volume = effect_def.get("volume", 15)
            effect = SoundEffect(effect_name, channel_type, frequency, duration, volume)
            library.register_effect(effect)

    # Load songs
    if "songs" in assets:
        for song_name, song_def in assets["songs"].items():
            tempo = song_def.get("tempo", 120)
            loop = song_def.get("loop", False)
            song = Song(song_name, tempo=tempo, loop=loop)

            # Load channels in song
            if "channels" in song_def:
                for channel_name, channel_def in song_def["channels"].items():
                    channel_type = channel_def.get("type", "pulse1")
                    channel = song.create_channel(channel_type, channel_name)

                    # Load notes in channel
                    if "notes" in channel_def:
                        for note_def in channel_def["notes"]:
                            if note_def.get("type") == "silence":
                                duration = note_def.get("duration", 1)
                                channel.add_silence(duration)
                            else:
                                frequency = note_def.get("frequency", 0)
                                duration = note_def.get("duration", 1)
                                volume = note_def.get("volume", 15)
                                channel.add_note(frequency, duration, volume)

            library.register_song(song)

    return library
