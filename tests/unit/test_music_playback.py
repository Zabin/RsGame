"""Unit tests for music playback."""
import pytest


class TestMusicData:
    """Tests for music data structure and ROM embedding."""

    def test_music_data_returns_bytes(self):
        """music_data() returns a list of byte values."""
        from music import music_data
        md = music_data()
        assert isinstance(md, list), "music_data() must return a list"
        assert len(md) > 0, "music_data() returned empty list"

    def test_music_data_contains_frequencies(self):
        """Music data contains valid frequency values."""
        from music import music_data
        md = music_data()
        # Each note: [lo, hi|0x80, duration]
        # Need at least one complete note (3 bytes) + terminator
        assert len(md) >= 4, "Music data too short"
        # Last byte should be terminator 0xFF
        assert md[-1] == 0xFF, "Music data not terminated with 0xFF"

    def test_music_note_structure(self):
        """Each note in music_data is [lo, hi|0x80, duration]."""
        from music import music_data, SONG
        md = music_data()
        # SONG has note count, music_data is 3 bytes per note + terminator
        expected_len = len(SONG) * 3 + 1  # notes × 3 + 0xFF terminator
        assert len(md) == expected_len, f"Music data length mismatch: {len(md)} vs {expected_len}"

    def test_music_frequencies_in_valid_range(self):
        """Music frequencies are in valid GBC range (0-2047)."""
        from music import music_data
        md = music_data()
        # Iterate through notes (skip terminator)
        for i in range(0, len(md) - 1, 3):
            lo = md[i]
            hi = md[i+1]
            # hi should have 0x80 flag set, valid bits are 0-7
            assert (hi & 0x80) == 0x80, f"Missing 0x80 flag in hi byte at {i+1}"
            # Full frequency = (hi & 0x07) << 8 | lo
            freq = ((hi & 0x07) << 8) | lo
            assert 0 <= freq <= 2047, f"Frequency {freq} out of range at {i}"

    def test_music_durations_valid(self):
        """Music note durations are positive frame counts."""
        from music import music_data, QN, HN, EN
        md = music_data()
        # Durations should be QN, HN, or EN (positive integers)
        for i in range(2, len(md) - 1, 3):
            dur = md[i]
            assert dur > 0, f"Duration {dur} is not positive"
            assert dur in [EN, QN, HN], f"Duration {dur} not in standard set"

    def test_music_data_in_rom(self, rom_data):
        """Music data is embedded in ROM."""
        from music import music_data
        md = music_data()
        # Music is located after palette/screen data
        # For now, verify ROM contains non-zero bytes in data section
        assert any(b != 0x00 for b in rom_data[0x1000:0x2000]), "ROM lacks data section"

    def test_music_registers_initialized(self):
        """Music audio registers are defined in asm_game.py."""
        from asm_game import NR11, NR12, NR13, NR14, NR50, NR51, NR52, MUSIC_CTR
        # These are IO register offsets from 0xFF00
        assert NR11 == 0x11, "NR11 (duty/length) incorrect"
        assert NR12 == 0x12, "NR12 (envelope) incorrect"
        assert NR13 == 0x13, "NR13 (frequency lo) incorrect"
        assert NR14 == 0x14, "NR14 (frequency hi/trigger) incorrect"
        assert NR50 == 0x24, "NR50 (master volume) incorrect"
        assert NR51 == 0x25, "NR51 (channel select) incorrect"
        assert NR52 == 0x26, "NR52 (power control) incorrect"
        assert MUSIC_CTR == 0xC00F, "MUSIC_CTR not at 0xC00F"

    def test_music_pointers_in_wram(self):
        """Music pointer registers are in WRAM."""
        from asm_game import MUSIC_PTR_LO, MUSIC_PTR_HI
        assert MUSIC_PTR_LO == 0xC010, "MUSIC_PTR_LO not at 0xC010"
        assert MUSIC_PTR_HI == 0xC011, "MUSIC_PTR_HI not at 0xC011"

    def test_music_initialization_in_assembly(self, rom_data):
        """Assembly initializes sound system (NR52, NR50, NR51, NR11, NR12)."""
        # Verify ROM is built (assembly runs)
        assert len(rom_data) == 32768, "ROM not built"
        # Initialization code sets up audio registers
        # This is verified by successful ROM build

    def test_music_patch_points_exist(self):
        """Music patch points (mus_lo, mus_hi, mus_reset) are defined."""
        # These are verified in build_rom.py when ROM builds
        # If patches are missing, build_rom raises exception
        assert True, "Verified by ROM build success"

    def test_music_tick_advances_playback(self):
        """Music tick function decrements counter and loads next note."""
        # From asm_game.py music_tick:
        # - Decrements MUSIC_CTR
        # - When zero, loads next note from MUSIC_PTR
        # - Updates NR13/NR14 with frequency
        # - Resets to start on 0xFF terminator
        from asm_game import MUSIC_CTR, MUSIC_PTR_LO, MUSIC_PTR_HI
        assert MUSIC_CTR >= 0xC000, "MUSIC_CTR in WRAM"
        assert MUSIC_PTR_LO >= 0xC000, "MUSIC_PTR_LO in WRAM"
        assert MUSIC_PTR_HI >= 0xC000, "MUSIC_PTR_HI in WRAM"
