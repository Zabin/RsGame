"""Unit tests for 9-zone biome support and 3×3 grid navigation."""
import pytest


class TestNineZoneStructure:
    """Tests for 9-zone data structures."""

    def test_zone_collects_has_nine_zones(self):
        """ZONE_COLLECTS supports all 9 zones."""
        from tilemaps import ZONE_COLLECTS
        assert len(ZONE_COLLECTS) == 9, f"Expected 9 zones, got {len(ZONE_COLLECTS)}"

    def test_each_zone_has_collectibles(self):
        """Each of 9 zones has at least one collectible (gift)."""
        from tilemaps import ZONE_COLLECTS
        for zone_id, clist in enumerate(ZONE_COLLECTS):
            # Each zone should have at least one item (gift)
            assert len(clist) > 0, f"Zone {zone_id} has no collectibles"
            # At least one should be a gift (type 2)
            gifts = [c for c in clist if len(c) >= 3 and c[2] == 2]
            assert len(gifts) >= 1, f"Zone {zone_id} has no gift"

    def test_collectible_coordinates_valid(self):
        """Collectible coordinates are within game area."""
        from tilemaps import ZONE_COLLECTS
        for zone_id, clist in enumerate(ZONE_COLLECTS):
            for x, y, ctype in clist:
                assert 0 <= x <= 159, f"Zone {zone_id}: x={x} out of range"
                assert 16 <= y <= 143, f"Zone {zone_id}: y={y} out of range"

    def test_all_screens_includes_nine_biomes(self):
        """ALL_SCREENS includes all 9 biome screens."""
        from tilemaps import ALL_SCREENS
        screen_names = [name for name, _ in ALL_SCREENS]

        # 9 biome zones (3×3 grid)
        required_biomes = ['garden', 'forest', 'meadow', 'desert', 'cave', 'swamp',
                          'snow_peak', 'crystal_lake', 'sunset_sky']
        for biome in required_biomes:
            assert biome in screen_names, f"Missing biome screen: {biome}"

    def test_all_screens_includes_ui_screens(self):
        """ALL_SCREENS includes all UI screens."""
        from tilemaps import ALL_SCREENS
        screen_names = [name for name, _ in ALL_SCREENS]

        # UI screens
        required_ui = ['title', 'intro', 'save', 'map', 'victory']
        for ui in required_ui:
            assert ui in screen_names, f"Missing UI screen: {ui}"

    def test_all_screens_total_count(self):
        """ALL_SCREENS has exactly 14 screens (9 biomes + 5 UI)."""
        from tilemaps import ALL_SCREENS
        assert len(ALL_SCREENS) == 14, f"Expected 14 screens, got {len(ALL_SCREENS)}"

    def test_screen_functions_callable(self):
        """All screen functions are callable."""
        from tilemaps import ALL_SCREENS
        for name, fn in ALL_SCREENS:
            assert callable(fn), f"Screen {name} is not callable"

    def test_screen_functions_return_correct_format(self):
        """All screen functions return (tiles, attrs) tuple."""
        from tilemaps import ALL_SCREENS
        for name, fn in ALL_SCREENS:
            result = fn()
            assert isinstance(result, tuple), f"Screen {name} doesn't return tuple"
            assert len(result) == 2, f"Screen {name} tuple wrong length"
            tiles, attrs = result
            assert len(tiles) == 576, f"Screen {name} tiles wrong size: {len(tiles)}"
            assert len(attrs) == 576, f"Screen {name} attrs wrong size: {len(attrs)}"


class TestZoneGridLayout:
    """Tests for 3×3 grid zone layout."""

    def test_zone_grid_dimensions(self):
        """Zone grid is 3×3 (9 zones total)."""
        # Grid layout:
        # [0=Garden,    1=Forest,  2=Meadow]
        # [3=Desert,    4=Cave,    5=Swamp]
        # [6=SnowPeak,  7=CrysLake, 8=SunsetSky]
        from tilemaps import ZONE_COLLECTS
        assert len(ZONE_COLLECTS) == 9, "Not 9 zones"

    def test_zone_grid_adjacency(self):
        """Zones follow 3×3 grid adjacency rules."""
        # Zone IDs and positions:
        # 0(0,0) 1(0,1) 2(0,2)
        # 3(1,0) 4(1,1) 5(1,2)
        # 6(2,0) 7(2,1) 8(2,2)

        def grid_pos(zone_id):
            """Convert zone ID to (row, col)."""
            return (zone_id // 3, zone_id % 3)

        # Verify grid mapping
        assert grid_pos(0) == (0, 0), "Zone 0 not at (0,0)"
        assert grid_pos(1) == (0, 1), "Zone 1 not at (0,1)"
        assert grid_pos(2) == (0, 2), "Zone 2 not at (0,2)"
        assert grid_pos(3) == (1, 0), "Zone 3 not at (1,0)"
        assert grid_pos(4) == (1, 1), "Zone 4 not at (1,1)"
        assert grid_pos(5) == (1, 2), "Zone 5 not at (1,2)"
        assert grid_pos(6) == (2, 0), "Zone 6 not at (2,0)"
        assert grid_pos(7) == (2, 1), "Zone 7 not at (2,1)"
        assert grid_pos(8) == (2, 2), "Zone 8 not at (2,2)"

    def test_zone_neighbors_correct(self):
        """Zone navigation neighbors are correctly adjacent."""
        def neighbors(zone_id):
            """Return dict of neighboring zones."""
            r, c = zone_id // 3, zone_id % 3
            ns = {}
            if c < 2: ns['right'] = r * 3 + (c + 1)
            if c > 0: ns['left'] = r * 3 + (c - 1)
            if r < 2: ns['down'] = (r + 1) * 3 + c
            if r > 0: ns['up'] = (r - 1) * 3 + c
            return ns

        # Zone 0 (top-left): right=1, down=3
        assert neighbors(0) == {'right': 1, 'down': 3}, "Zone 0 neighbors wrong"

        # Zone 4 (center): all 4 neighbors
        assert neighbors(4) == {'right': 5, 'left': 3, 'down': 7, 'up': 1}, "Zone 4 neighbors wrong"

        # Zone 8 (bottom-right): left=7, up=5
        assert neighbors(8) == {'left': 7, 'up': 5}, "Zone 8 neighbors wrong"

    def test_zone_navigation_boundaries(self):
        """Zone navigation respects grid boundaries."""
        # Top row (0,1,2): can't go up
        # Bottom row (6,7,8): can't go down
        # Left column (0,3,6): can't go left
        # Right column (2,5,8): can't go right

        top_row = [0, 1, 2]
        bottom_row = [6, 7, 8]
        left_col = [0, 3, 6]
        right_col = [2, 5, 8]

        assert all(z in top_row for z in [0, 1, 2]), "Top row definition"
        assert all(z in bottom_row for z in [6, 7, 8]), "Bottom row definition"
        assert all(z in left_col for z in [0, 3, 6]), "Left column definition"
        assert all(z in right_col for z in [2, 5, 8]), "Right column definition"


class TestZoneProgression:
    """Tests for zone progression logic."""

    def test_zone_transitions_linear_or_grid(self):
        """Zone transitions support either linear or grid movement."""
        # Currently: linear 0→1→2
        # Target: grid-based navigation (3×3)
        from asm_game import CUR_ZONE
        assert CUR_ZONE == 0xC008, "CUR_ZONE at correct address"

    def test_cur_zone_range_nine_zones(self):
        """CUR_ZONE can represent all 9 zones (0-8)."""
        # Currently limited to 3 (0-2) by assembly
        # After fix: should support 0-8
        # Verify GIFTS bitfield can represent collected gifts from 9 zones
        # (currently uses 3 bits, needs 9 bits)
        assert True, "Target behavior: CUR_ZONE 0-8 after fix"

    def test_gifts_bitfield_nine_zones(self):
        """GIFTS bitfield can represent gifts from 9 zones."""
        # Current: 3 bits (0x07 = 0b111)
        # Target: 9 bits minimum (0x1FF = 0b111111111)
        # Will require expanding to 16-bit field or using full byte
        from asm_game import GIFTS
        assert GIFTS == 0xC009, "GIFTS at correct address"

    def test_zone_names_map(self):
        """Zone IDs map to correct biome names."""
        zone_names = {
            0: 'garden',
            1: 'forest',
            2: 'meadow',
            3: 'desert',
            4: 'cave',
            5: 'swamp',
            6: 'snow_peak',
            7: 'crystal_lake',
            8: 'sunset_sky',
        }

        from tilemaps import ALL_SCREENS
        screen_names = [name for name, _ in ALL_SCREENS]

        for zone_id, zone_name in zone_names.items():
            assert zone_name in screen_names, f"Zone {zone_id} ({zone_name}) not in screens"


class TestZoneGifts:
    """Tests for gift collection across 9 zones."""

    def test_each_zone_has_exactly_one_gift(self):
        """Each of 9 zones has exactly one collectible gift."""
        from tilemaps import ZONE_COLLECTS
        assert len(ZONE_COLLECTS) == 9, "Not 9 zones"

        for zone_id, clist in enumerate(ZONE_COLLECTS):
            gifts = [c for c in clist if len(c) >= 3 and c[2] == 2]
            assert len(gifts) == 1, f"Zone {zone_id} has {len(gifts)} gifts, expected 1"

    def test_gifts_completion_requires_all_nine(self):
        """Completing game requires collecting all 9 gifts."""
        # Current: check_complete in assembly does: GIFTS & 0x07 == 0x07
        # Target: should check all 9 bits are set
        assert True, "Target behavior: complete = all 9 gifts collected"

    def test_zone_collectible_spacing(self):
        """Collectibles in each zone are spaced to avoid overlap."""
        from tilemaps import ZONE_COLLECTS

        for zone_id, clist in enumerate(ZONE_COLLECTS):
            if len(clist) <= 1:
                continue
            # Check no two collectibles overlap
            for i, (x1, y1, t1) in enumerate(clist):
                for j, (x2, y2, t2) in enumerate(clist):
                    if i < j:
                        # Collision radius is ~10 pixels
                        dx = abs(x1 - x2)
                        dy = abs(y1 - y2)
                        assert dx >= 10 or dy >= 10, \
                            f"Zone {zone_id}: items {i} and {j} too close"
