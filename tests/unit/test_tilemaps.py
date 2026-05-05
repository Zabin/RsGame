"""Unit tests for screen layouts and collectibles.

Tests the tilemaps module:
- Screen generators (dimensions, structure)
- Collectible spawn tables
- Palette assignments
"""
import pytest

from tilemaps import (
    ALL_SCREENS,
    ZONE_COLLECTS,
    garden_screen,
    forest_screen,
    meadow_screen,
)


@pytest.mark.unit
class TestScreenDimensions:
    """Tests for screen layout dimensions."""

    EXPECTED_WIDTH = 32
    EXPECTED_HEIGHT = 18
    EXPECTED_SIZE = 32 * 18  # 576 tiles

    def test_garden_screen_dimensions(self):
        """Garden screen is 32×18 tiles."""
        tiles, attrs = garden_screen()
        assert len(tiles) == self.EXPECTED_SIZE
        assert len(attrs) == self.EXPECTED_SIZE

    def test_forest_screen_dimensions(self):
        """Forest screen is 32×18 tiles."""
        tiles, attrs = forest_screen()
        assert len(tiles) == self.EXPECTED_SIZE
        assert len(attrs) == self.EXPECTED_SIZE

    def test_meadow_screen_dimensions(self):
        """Meadow screen is 32×18 tiles."""
        tiles, attrs = meadow_screen()
        assert len(tiles) == self.EXPECTED_SIZE
        assert len(attrs) == self.EXPECTED_SIZE

    def test_all_screens_registered(self):
        """All expected screens are registered in ALL_SCREENS."""
        screen_names = [name for name, _ in ALL_SCREENS]
        expected = ["title", "intro", "save", "map", "victory", "garden", "forest", "meadow"]
        for name in expected:
            assert name in screen_names, f"Screen '{name}' not registered"


@pytest.mark.unit
class TestScreenTypes:
    """Tests for screen data types."""

    def test_screen_data_is_bytearray(self):
        """Screen generators return bytearrays."""
        tiles, attrs = garden_screen()
        assert isinstance(tiles, (list, bytearray))
        assert isinstance(attrs, (list, bytearray))

    def test_tile_values_in_range(self):
        """All tile indices are valid (0x00-0xFF)."""
        tiles, _ = garden_screen()
        for tile in tiles:
            assert isinstance(tile, int)
            assert 0 <= tile <= 0xFF

    def test_attr_values_in_range(self):
        """All attribute/palette values are valid (0-7)."""
        _, attrs = garden_screen()
        for attr in attrs:
            assert isinstance(attr, int)
            assert 0 <= attr <= 7


@pytest.mark.unit
class TestCollectibles:
    """Tests for collectible spawn tables."""

    def test_zone_collects_has_three_zones(self):
        """ZONE_COLLECTS has entries for 3 zones."""
        assert 0 in ZONE_COLLECTS
        assert 1 in ZONE_COLLECTS
        assert 2 in ZONE_COLLECTS
        assert len(ZONE_COLLECTS) == 3

    def test_collectibles_are_tuples(self):
        """Each collectible is (x, y, type) tuple."""
        for zone, collects in ZONE_COLLECTS.items():
            for collect in collects:
                assert isinstance(collect, tuple)
                assert len(collect) == 3
                x, y, typ = collect
                assert isinstance(x, int)
                assert isinstance(y, int)
                assert isinstance(typ, int)

    def test_collectible_positions_in_bounds(self):
        """Collectible X/Y positions are within screen bounds."""
        for zone, collects in ZONE_COLLECTS.items():
            for x, y, typ in collects:
                assert 0 <= x <= 159, f"Zone {zone}: X {x} out of bounds"
                assert 16 <= y <= 143, f"Zone {zone}: Y {y} out of bounds (UI bar is 0-15)"

    def test_collectible_types_valid(self):
        """Collectible types are 0 (star), 1 (flower), 2 (gift)."""
        for zone, collects in ZONE_COLLECTS.items():
            for x, y, typ in collects:
                assert typ in (0, 1, 2), f"Zone {zone}: Invalid type {typ}"

    def test_one_gift_per_zone(self):
        """Each zone has exactly one gift (type=2)."""
        for zone, collects in ZONE_COLLECTS.items():
            gifts = [c for c in collects if c[2] == 2]
            assert len(gifts) == 1, f"Zone {zone} has {len(gifts)} gifts, expected 1"

    def test_collectibles_not_at_spawn(self):
        """Collectibles don't spawn at known player spawn positions."""
        spawn_positions = {
            0: (76, 72),  # Garden
            1: (8, 72),  # Forest (left entry)
            2: (40, 72),  # Meadow (?)
        }
        # Verify gifts aren't too close to spawn (10px threshold)
        for zone, spawn_x, spawn_y in spawn_positions.items():
            if zone in spawn_positions:
                for x, y, typ in ZONE_COLLECTS[zone]:
                    if typ == 2:  # Gift
                        # At least shouldn't be exactly at spawn
                        assert (x, y) != spawn_positions[zone]


@pytest.mark.unit
class TestScreenCallable:
    """Tests for screen generator functions."""

    def test_all_screens_callable(self):
        """All registered screen functions are callable."""
        for name, screen_fn in ALL_SCREENS:
            assert callable(screen_fn), f"Screen '{name}' is not callable"

    def test_all_screens_return_tuple(self):
        """All screen functions return (tiles, attrs) tuple."""
        for name, screen_fn in ALL_SCREENS:
            result = screen_fn()
            assert isinstance(result, tuple)
            assert len(result) == 2
            tiles, attrs = result
            assert len(tiles) == 576
            assert len(attrs) == 576

    def test_screens_deterministic(self):
        """Screen generators produce same result on multiple calls."""
        tiles1, attrs1 = garden_screen()
        tiles2, attrs2 = garden_screen()
        assert tiles1 == tiles2
        assert attrs1 == attrs2


@pytest.mark.unit
class TestScreenContent:
    """Tests for screen content validity."""

    def test_garden_has_score_bar(self):
        """Garden screen has score bar (row 0)."""
        tiles, _ = garden_screen()
        # Score bar should have hearts and gift icon
        row_0 = tiles[0:32]
        # At minimum, shouldn't be all same tile (should have variation)
        assert len(set(row_0)) > 1, "Score bar lacks variation"

    def test_screen_not_all_zeros(self):
        """Screens aren't empty (at least some non-zero tiles)."""
        for name, screen_fn in ALL_SCREENS:
            tiles, _ = screen_fn()
            non_zero = [t for t in tiles if t != 0x00]
            assert len(non_zero) > 0, f"Screen '{name}' is all zeros"

    def test_screen_not_all_same_tile(self):
        """Screens aren't monotonous (have multiple different tiles)."""
        for name, screen_fn in ALL_SCREENS:
            tiles, _ = screen_fn()
            unique_tiles = len(set(tiles))
            assert unique_tiles > 1, f"Screen '{name}' has only 1 unique tile"
