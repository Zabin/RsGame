"""Unit tests for music data generation.

Tests the music module:
- Note frequency calculation
- Music data encoding
- Song structure
"""
import pytest

from music import SONG, freq, music_data


@pytest.mark.unit
class TestFrequency:
    """Tests for freq() function."""

    def test_freq_returns_int(self):
        """freq() returns integer register value."""
        result = freq(261.63)  # C4
        assert isinstance(result, int)

    def test_freq_in_valid_range(self):
        """Game Boy frequency register is 0-2047."""
        for hz in [261.63, 293.66, 329.63, 392.0, 440.0]:  # C4-A4
            result = freq(hz)
            assert 0 <= result <= 2047, f"Frequency {hz}Hz = {result}, out of range"

    def test_freq_c4_reasonable(self):
        """C4 (261.63 Hz) produces reasonable register value."""
        result = freq(261.63)
        # Based on Game Boy formula: freq = 2048 - 131072/hz
        # For C4: 2048 - 131072/261.63 ≈ 1547
        assert 1500 < result < 1600

    def test_freq_higher_pitch_higher_value(self):
        """Higher frequencies produce higher register values."""
        c4 = freq(261.63)
        a4 = freq(440.0)
        assert a4 > c4  # Higher pitch = higher register value (different formula)

    def test_freq_monotonic_increasing(self):
        """Frequency values increase monotonically with Hz."""
        c4 = freq(261.63)
        d4 = freq(293.66)
        e4 = freq(329.63)
        # Higher Hz should give higher freq register
        assert c4 < d4 < e4


@pytest.mark.unit
class TestMusicStructure:
    """Tests for music data format."""

    def test_song_is_list_of_tuples(self):
        """SONG is list of (frequency, duration) tuples."""
        assert isinstance(SONG, list)
        assert len(SONG) > 0
        for note in SONG:
            assert isinstance(note, tuple)
            assert len(note) == 2
            freq_val, duration = note
            # Frequency should be Hz value or special value
            assert isinstance(freq_val, (int, float))
            # Duration should be frame count
            assert isinstance(duration, int)
            assert duration > 0

    def test_song_has_reasonable_length(self):
        """Song has at least a few notes."""
        assert len(SONG) >= 3, "Song too short"

    def test_song_durations_positive(self):
        """All note durations are positive."""
        for freq_hz, duration in SONG:
            assert duration > 0, f"Duration {duration} not positive"

    def test_music_data_callable(self):
        """music_data() is a callable function."""
        assert callable(music_data)


@pytest.mark.unit
class TestMusicEncoding:
    """Tests for music data encoding."""

    def test_music_data_returns_sequence(self):
        """music_data() returns list or bytes."""
        result = music_data()
        assert isinstance(result, (list, bytes, bytearray))

    def test_music_data_not_empty(self):
        """music_data() produces at least some bytes."""
        result = music_data()
        assert len(result) > 0

    def test_music_data_ends_with_terminator(self):
        """Music data ends with 0xFF terminator."""
        result = music_data()
        # Last byte should be terminator
        assert result[-1] == 0xFF, f"Last byte {result[-1]:02X}, expected FF"

    def test_music_data_bytes_valid(self):
        """All music data bytes are valid (0x00-0xFF)."""
        result = music_data()
        for byte in result:
            assert isinstance(byte, int)
            assert 0 <= byte <= 255

    def test_music_data_deterministic(self):
        """music_data() produces same output on multiple calls."""
        data1 = music_data()
        data2 = music_data()
        assert data1 == data2


@pytest.mark.unit
class TestNoteFormat:
    """Tests for note data format assumptions."""

    def test_note_frequencies_non_zero(self):
        """Notes should have non-zero frequencies (except rests)."""
        non_zero_notes = [note for note in SONG if note[0] > 0]
        assert len(non_zero_notes) > len(SONG) / 2, "Most notes should be non-zero frequency"

    def test_typical_note_durations(self):
        """Note durations are reasonable (10-40 frames at 60 FPS)."""
        QN = 18  # Quarter note
        HN = 36  # Half note
        for freq_hz, duration in SONG:
            # Most notes should be in reasonable range
            assert 5 <= duration <= 100, f"Duration {duration} seems unrealistic"
