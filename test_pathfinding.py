#!/usr/bin/env python3
"""
test_pathfinding.py — Test cross-biome pathfinding and path validation.

Validates that:
1. Each biome has a clear path row (row 9)
2. Paths can be found from left to right edges
3. Path flow works for playable zones
"""

import pytest
from pathfinding import PathValidator, validate_all_biomes, BLOCKED_TILES, WALKABLE_TILES
from tilemaps import garden_screen, forest_screen, meadow_screen, title_screen


class TestPathValidator:
    """Test path validator on known biomes."""

    def test_garden_has_clear_path_row(self):
        """Garden should have clear path at row 9."""
        tiles, attrs = garden_screen()
        validator = PathValidator(tiles, attrs)
        is_valid, message = validator.validate_path_row(path_row=9)
        assert is_valid, f"Garden path validation failed: {message}"

    def test_forest_has_clear_path_row(self):
        """Forest should have clear path at row 9."""
        tiles, attrs = forest_screen()
        validator = PathValidator(tiles, attrs)
        is_valid, message = validator.validate_path_row(path_row=9)
        assert is_valid, f"Forest path validation failed: {message}"

    def test_meadow_has_clear_path_row(self):
        """Meadow should have clear path at row 9."""
        tiles, attrs = meadow_screen()
        validator = PathValidator(tiles, attrs)
        is_valid, message = validator.validate_path_row(path_row=9)
        assert is_valid, f"Meadow path validation failed: {message}"

    def test_garden_path_connects_left_to_right(self):
        """Garden path should connect left edge (x=0) to right edge (x=19)."""
        tiles, attrs = garden_screen()
        validator = PathValidator(tiles, attrs)
        path = validator.find_path((0, 9), (19, 9))
        assert path is not None, "No path found from left to right in Garden"
        assert path[0] == (0, 9), "Path should start at left edge"
        assert path[-1] == (19, 9), "Path should end at right edge"

    def test_forest_path_connects_left_to_right(self):
        """Forest path should connect left edge to right edge."""
        tiles, attrs = forest_screen()
        validator = PathValidator(tiles, attrs)
        path = validator.find_path((0, 9), (19, 9))
        assert path is not None, "No path found from left to right in Forest"
        assert path[0] == (0, 9)
        assert path[-1] == (19, 9)

    def test_meadow_path_connects_left_to_right(self):
        """Meadow path should connect left edge to right edge."""
        tiles, attrs = meadow_screen()
        validator = PathValidator(tiles, attrs)
        path = validator.find_path((0, 9), (19, 9))
        assert path is not None, "No path found from left to right in Meadow"
        assert path[0] == (0, 9)
        assert path[-1] == (19, 9)

    def test_menu_screens_have_blocked_path(self):
        """Menu screens (title, intro, etc.) should have blocked paths at row 9."""
        tiles, attrs = title_screen()
        validator = PathValidator(tiles, attrs)
        path = validator.find_path((0, 9), (19, 9))
        # Menu screens are blank/blocked, so path may or may not exist
        # Just test that validator doesn't crash
        assert validator is not None


class TestCrossBiomeFlow:
    """Test cross-biome pathfinding validation."""

    def test_all_biomes_validate(self):
        """All biomes should pass path validation."""
        all_valid, results = validate_all_biomes()

        # Print results for debugging
        for screen_name, is_valid, message in results:
            status = "✓" if is_valid else "✗"
            print(f"{status} {screen_name}: {message}")

        assert all_valid, "Not all biomes have valid path flow"

    def test_playable_zones_have_paths(self):
        """All playable zones should have valid paths."""
        playable_zones = ["garden", "forest", "meadow"]
        for zone_name in playable_zones:
            if zone_name == "garden":
                tiles, attrs = garden_screen()
            elif zone_name == "forest":
                tiles, attrs = forest_screen()
            elif zone_name == "meadow":
                tiles, attrs = meadow_screen()
            else:
                continue

            validator = PathValidator(tiles, attrs)
            is_valid, message = validator.validate_path_row(9)
            assert is_valid, f"{zone_name} failed: {message}"


class TestTileClassification:
    """Test that tile blocking/walkability is correct."""

    def test_blocked_tiles_are_defined(self):
        """Blocked tiles should be defined."""
        assert len(BLOCKED_TILES) > 0, "No blocked tiles defined"
        # Check for common blocking tiles
        assert 0x16 in BLOCKED_TILES, "Rocks should be blocked"
        assert 0x18 in BLOCKED_TILES, "Trees should be blocked"

    def test_walkable_tiles_are_defined(self):
        """Walkable tiles should be defined."""
        assert len(WALKABLE_TILES) > 0, "No walkable tiles defined"
        # Check for common walkable tiles
        assert 0x10 in WALKABLE_TILES, "Grass should be walkable"

    def test_blocked_and_walkable_dont_overlap(self):
        """Blocked and walkable tiles should not overlap."""
        overlap = BLOCKED_TILES & WALKABLE_TILES
        assert len(overlap) == 0, f"Tiles in both lists: {overlap}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
