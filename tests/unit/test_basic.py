"""Basic tests for RsGame."""
import pytest


class TestBasic:
    """Basic smoke tests."""

    def test_all_nine_zones_defined(self):
        """Verify all 9 zone screens are defined."""
        from tilemaps import ALL_SCREENS

        zone_screens = [s for s, _ in ALL_SCREENS if s not in ["title", "intro", "save", "map", "victory"]]
        expected_zones = ["garden", "forest", "meadow", "desert", "cave", "swamp", "snow_peak", "crystal_lake", "sunset_sky"]

        for zone in expected_zones:
            assert zone in zone_screens, f"Zone '{zone}' not found in ALL_SCREENS"

    def test_nine_zone_melodies_defined(self):
        """Verify all 9 zone melodies are defined."""
        from music import ZONE_MELODIES

        assert len(ZONE_MELODIES) == 9, f"Expected 9 melodies, got {len(ZONE_MELODIES)}"

        for i, melody in enumerate(ZONE_MELODIES):
            assert len(melody) > 0, f"Zone {i} melody is empty"
            assert all(isinstance(note, tuple) and len(note) == 2 for note in melody), \
                f"Zone {i} melody has invalid format"

    def test_rom_builds(self, rom_path):
        """Verify ROM builds without errors."""
        import subprocess
        result = subprocess.run(["python", "build_rom.py"], capture_output=True, text=True)
        assert result.returncode == 0, f"ROM build failed: {result.stderr}"
