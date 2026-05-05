"""Unit tests for sound system (songs, effects, channels).

Tests music composition, multi-channel mixing, and asset loading from JSON.
"""
import pytest
import json
import tempfile
from pathlib import Path


class TestNote:
    """Tests for Note class."""

    def test_note_creation(self):
        """Note can be created with frequency and duration."""
        from sound import Note

        note = Note(131072, 30)
        assert note.frequency == 131072
        assert note.duration == 30
        assert note.volume == 15

    def test_note_volume_clamping(self):
        """Note volume is clamped to 0-15 range."""
        from sound import Note

        note1 = Note(131072, 30, volume=20)
        assert note1.volume == 15

        note2 = Note(131072, 30, volume=-5)
        assert note2.volume == 0

    def test_note_panning_clamping(self):
        """Note panning is clamped to -100 to 100."""
        from sound import Note

        note1 = Note(131072, 30, panning=150)
        assert note1.panning == 100

        note2 = Note(131072, 30, panning=-150)
        assert note2.panning == -100

    def test_note_repr(self):
        """Note repr shows frequency, duration, volume."""
        from sound import Note

        note = Note(131072, 30, volume=10)
        repr_str = repr(note)
        assert "131072" in repr_str
        assert "30f" in repr_str


class TestSilence:
    """Tests for Silence class."""

    def test_silence_creation(self):
        """Silence can be created with duration."""
        from sound import Silence

        silence = Silence(30)
        assert silence.duration == 30

    def test_silence_repr(self):
        """Silence repr shows duration."""
        from sound import Silence

        silence = Silence(30)
        repr_str = repr(silence)
        assert "30f" in repr_str


class TestChannel:
    """Tests for Channel class."""

    def test_channel_creation(self):
        """Channel can be created with type and name."""
        from sound import Channel

        ch = Channel("pulse1", "melody")
        assert ch.channel_type == "pulse1"
        assert ch.name == "melody"
        assert len(ch.notes) == 0

    def test_channel_invalid_type(self):
        """Channel with invalid type raises error."""
        from sound import Channel

        with pytest.raises(ValueError):
            Channel("invalid_type")

    def test_channel_add_note(self):
        """Notes can be added to channel."""
        from sound import Channel

        ch = Channel("pulse1")
        ch.add_note(131072, 30)
        assert len(ch.notes) == 1

    def test_channel_add_silence(self):
        """Silence can be added to channel."""
        from sound import Channel

        ch = Channel("pulse1")
        ch.add_silence(15)
        assert len(ch.notes) == 1

    def test_channel_total_duration(self):
        """Channel total_duration sums all notes."""
        from sound import Channel

        ch = Channel("pulse1")
        ch.add_note(131072, 30)
        ch.add_silence(15)
        ch.add_note(65536, 30)
        assert ch.total_duration() == 75

    def test_channel_repr(self):
        """Channel repr shows type, name, note count."""
        from sound import Channel

        ch = Channel("wave", "harmony")
        ch.add_note(65536, 30)
        repr_str = repr(ch)
        assert "wave" in repr_str
        assert "1 notes" in repr_str


class TestSong:
    """Tests for Song class."""

    def test_song_creation(self):
        """Song can be created with name and tempo."""
        from sound import Song

        song = Song("Title Theme", tempo=120, loop=False)
        assert song.name == "Title Theme"
        assert song.tempo == 120
        assert song.loop is False

    def test_song_create_channel(self):
        """Channels can be created in song."""
        from sound import Song

        song = Song("Test Song")
        ch = song.create_channel("pulse1", "melody")
        assert ch is not None
        assert ch.name == "melody"

    def test_song_create_invalid_channel(self):
        """Creating invalid channel type raises error."""
        from sound import Song

        song = Song("Test Song")
        with pytest.raises(ValueError):
            song.create_channel("invalid")

    def test_song_get_channel(self):
        """Channels can be retrieved."""
        from sound import Song

        song = Song("Test Song")
        ch = song.create_channel("pulse1", "melody")
        retrieved = song.get_channel("pulse1_0")
        assert retrieved is not None
        assert retrieved.name == "melody"

    def test_song_list_channels(self):
        """All channels can be listed."""
        from sound import Song

        song = Song("Test Song")
        song.create_channel("pulse1", "melody")
        song.create_channel("pulse2", "bass")
        channels = song.list_channels()
        assert len(channels) == 2

    def test_song_total_duration(self):
        """Song duration is max of all channels."""
        from sound import Song

        song = Song("Test Song")
        ch1 = song.create_channel("pulse1")
        ch1.add_note(131072, 60)  # 60 frames
        ch2 = song.create_channel("pulse2")
        ch2.add_note(65536, 120)  # 120 frames
        assert song.total_duration() == 120

    def test_song_encode(self):
        """Song can be encoded to bytes."""
        from sound import Song

        song = Song("Test", tempo=120, loop=True)
        ch = song.create_channel("pulse1")
        ch.add_note(131072, 30)
        data = song.encode()
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_song_repr(self):
        """Song repr shows name, tempo, channel count."""
        from sound import Song

        song = Song("Battle Theme", tempo=140)
        song.create_channel("pulse1")
        repr_str = repr(song)
        assert "Battle Theme" in repr_str
        assert "140bpm" in repr_str


class TestSoundEffect:
    """Tests for SoundEffect class."""

    def test_effect_creation(self):
        """SoundEffect can be created with basic parameters."""
        from sound import SoundEffect

        effect = SoundEffect("pop", "pulse1", 131072, 10)
        assert effect.name == "pop"
        assert effect.channel_type == "pulse1"
        assert effect.duration == 10

    def test_effect_volume_clamping(self):
        """SoundEffect volume is clamped to 0-15."""
        from sound import SoundEffect

        effect = SoundEffect("pop", "pulse1", 131072, 10, volume=20)
        assert effect.volume == 15

    def test_effect_encode(self):
        """SoundEffect can be encoded to bytes."""
        from sound import SoundEffect

        effect = SoundEffect("pop", "pulse1", 131072, 10)
        data = effect.encode()
        assert isinstance(data, bytes)
        assert len(data) == 5

    def test_effect_repr(self):
        """SoundEffect repr shows name and channel type."""
        from sound import SoundEffect

        effect = SoundEffect("chime", "wave", 65536, 15)
        repr_str = repr(effect)
        assert "chime" in repr_str
        assert "wave" in repr_str


class TestSoundLibrary:
    """Tests for SoundLibrary class."""

    def test_library_creation(self):
        """SoundLibrary initializes empty."""
        from sound import SoundLibrary

        lib = SoundLibrary()
        assert len(lib.songs) == 0
        assert len(lib.effects) == 0

    def test_register_song(self):
        """Songs can be registered."""
        from sound import SoundLibrary, Song

        lib = SoundLibrary()
        song = Song("Test")
        lib.register_song(song)
        assert "Test" in lib.songs

    def test_register_duplicate_song_fails(self):
        """Registering duplicate song fails."""
        from sound import SoundLibrary, Song

        lib = SoundLibrary()
        song1 = Song("Test")
        song2 = Song("Test")
        lib.register_song(song1)
        with pytest.raises(ValueError):
            lib.register_song(song2)

    def test_register_effect(self):
        """Effects can be registered."""
        from sound import SoundLibrary, SoundEffect

        lib = SoundLibrary()
        effect = SoundEffect("pop", "pulse1", 131072, 10)
        lib.register_effect(effect)
        assert "pop" in lib.effects

    def test_get_song(self):
        """Songs can be retrieved."""
        from sound import SoundLibrary, Song

        lib = SoundLibrary()
        song = Song("Title Theme")
        lib.register_song(song)
        retrieved = lib.get_song("Title Theme")
        assert retrieved is not None
        assert retrieved.name == "Title Theme"

    def test_get_effect(self):
        """Effects can be retrieved."""
        from sound import SoundLibrary, SoundEffect

        lib = SoundLibrary()
        effect = SoundEffect("chime", "wave", 65536, 10)
        lib.register_effect(effect)
        retrieved = lib.get_effect("chime")
        assert retrieved is not None

    def test_list_songs(self):
        """All songs can be listed."""
        from sound import SoundLibrary, Song

        lib = SoundLibrary()
        lib.register_song(Song("Song1"))
        lib.register_song(Song("Song2"))
        songs = lib.list_songs()
        assert len(songs) == 2

    def test_list_effects(self):
        """All effects can be listed."""
        from sound import SoundLibrary, SoundEffect

        lib = SoundLibrary()
        lib.register_effect(SoundEffect("pop", "pulse1", 131072, 10))
        lib.register_effect(SoundEffect("chime", "wave", 65536, 10))
        effects = lib.list_effects()
        assert len(effects) == 2

    def test_library_repr(self):
        """Library repr shows song and effect counts."""
        from sound import SoundLibrary, Song, SoundEffect

        lib = SoundLibrary()
        lib.register_song(Song("Test"))
        lib.register_effect(SoundEffect("pop", "pulse1", 131072, 10))
        repr_str = repr(lib)
        assert "1 songs" in repr_str
        assert "1 effects" in repr_str


class TestGlobalLibrary:
    """Tests for global library instance."""

    def test_global_library_exists(self):
        """Global library instance is available."""
        from sound import library

        assert library is not None


class TestLoadSoundsFromJSON:
    """Tests for JSON sound asset loading."""

    def test_load_effects_from_json(self):
        """Sound effects can be loaded from JSON."""
        from sound import load_sounds_from_json

        assets = {
            "effects": {
                "pop": {
                    "channel": "pulse1",
                    "frequency": 131072,
                    "duration": 10,
                    "volume": 15,
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "sounds.json"
            with open(json_path, "w") as f:
                json.dump(assets, f)

            lib = load_sounds_from_json(str(json_path))
            effect = lib.get_effect("pop")
            assert effect is not None
            assert effect.name == "pop"

    def test_load_songs_from_json(self):
        """Songs can be loaded from JSON."""
        from sound import load_sounds_from_json

        assets = {
            "songs": {
                "title": {
                    "tempo": 120,
                    "loop": False,
                    "channels": {
                        "melody": {
                            "type": "pulse1",
                            "notes": [
                                {"frequency": 131072, "duration": 30},
                                {"type": "silence", "duration": 15},
                            ],
                        }
                    },
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "sounds.json"
            with open(json_path, "w") as f:
                json.dump(assets, f)

            lib = load_sounds_from_json(str(json_path))
            song = lib.get_song("title")
            assert song is not None
            assert song.name == "title"

    def test_load_missing_file_fails(self):
        """Loading missing file raises FileNotFoundError."""
        from sound import load_sounds_from_json

        with pytest.raises(FileNotFoundError):
            load_sounds_from_json("/nonexistent/sounds.json")
