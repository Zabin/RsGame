#!/usr/bin/env python3
"""
test_road_generator.py — Test + shaped road generation.

Validates that roads:
1. Form proper + shapes in each zone
2. Connect to adjacent zones correctly
3. Have consistent dimensions
4. Provide clear pathways for navigation
"""

import pytest
from road_generator import RoadGenerator, PLAYABLE_WIDTH, PLAYABLE_HEIGHT, CENTER_X, CENTER_Y, GRID_ROWS, GRID_COLS

SCORE_BAR_HEIGHT = 1
CENTER_Y_IN_ZONE = CENTER_Y - SCORE_BAR_HEIGHT


class TestRoadGeneration:
    """Test road generator."""

    def test_road_generator_initializes(self):
        """Road generator should initialize without errors."""
        gen = RoadGenerator()
        assert gen is not None
        assert gen.width == PLAYABLE_WIDTH
        assert gen.height == PLAYABLE_HEIGHT

    def test_roads_generate_successfully(self):
        """Roads should generate for all zones."""
        gen = RoadGenerator()
        roads = gen.generate()
        assert roads is not None
        assert len(roads) == 9

    def test_all_zones_have_roads(self):
        """All 9 zones should have road data."""
        gen = RoadGenerator()
        gen.generate()

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_pos = (row, col)
                assert zone_pos in gen.zone_roads
                assert gen.zone_roads[zone_pos] is not None

    def test_zone_road_dimensions(self):
        """Each zone road map should have correct dimensions."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            assert len(roads) == PLAYABLE_HEIGHT
            assert all(len(row) == PLAYABLE_WIDTH for row in roads)

    def test_each_zone_has_plus_shape(self):
        """Each zone should have a + shaped road (vertical + horizontal, trimmed at edges)."""
        gen = RoadGenerator()
        gen.generate()

        zone_row_col = {(0, 0): (0, 0), (0, 1): (0, 1), (0, 2): (0, 2),
                        (1, 0): (1, 0), (1, 1): (1, 1), (1, 2): (1, 2),
                        (2, 0): (2, 0), (2, 1): (2, 1), (2, 2): (2, 2)}

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            zone_row, zone_col = zone_pos

            # Check vertical road (column CENTER_X), trimmed at grid edges
            vertical_start = 0 if zone_row > 0 else 1
            vertical_end = PLAYABLE_HEIGHT if zone_row < GRID_ROWS - 1 else PLAYABLE_HEIGHT - 1
            vertical_count = sum(1 for y in range(vertical_start, vertical_end) if roads[y][CENTER_X])
            expected_vertical = vertical_end - vertical_start
            assert vertical_count == expected_vertical, f"Zone {zone_pos} vertical road count {vertical_count}, expected {expected_vertical}"

            # Check horizontal road (row CENTER_Y_IN_ZONE), trimmed at grid edges
            horizontal_start = 0 if zone_col > 0 else 1
            horizontal_end = PLAYABLE_WIDTH if zone_col < GRID_COLS - 1 else PLAYABLE_WIDTH - 1
            horizontal_count = sum(1 for x in range(horizontal_start, horizontal_end) if roads[CENTER_Y_IN_ZONE][x])
            expected_horizontal = horizontal_end - horizontal_start
            assert horizontal_count == expected_horizontal, f"Zone {zone_pos} horizontal road count {horizontal_count}, expected {expected_horizontal}"

    def test_road_intersects_at_center(self):
        """Roads should intersect at center of zone."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            # Center point should be a road
            assert roads[CENTER_Y_IN_ZONE][CENTER_X], f"Zone {zone_pos} center not a road"

    def test_zone_road_cell_counts(self):
        """Each zone should have correct road cell count based on position."""
        gen = RoadGenerator()
        gen.generate()

        # Expected counts based on trimming:
        # Center zone (1,1): 36 cells (full +)
        # Edge zones (not corner): 35 cells (trimmed on 1 side)
        # Corner zones: 34 cells (trimmed on 2 sides)

        corner_zones = [(0, 0), (0, 2), (2, 0), (2, 2)]
        edge_zones = [(0, 1), (1, 0), (1, 2), (2, 1)]
        center_zone = (1, 1)

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            road_count = sum(1 for row in roads for cell in row if cell)

            if zone_pos == center_zone:
                assert road_count == 36, f"Center zone {zone_pos} has {road_count} cells, expected 36"
            elif zone_pos in corner_zones:
                assert road_count == 34, f"Corner zone {zone_pos} has {road_count} cells, expected 34"
            elif zone_pos in edge_zones:
                assert road_count == 35, f"Edge zone {zone_pos} has {road_count} cells, expected 35"

    def test_all_zones_have_non_road_cells(self):
        """Each zone should have non-road cells (for obstacles, scenery)."""
        gen = RoadGenerator()
        gen.generate()

        corner_zones = [(0, 0), (0, 2), (2, 0), (2, 2)]
        edge_zones = [(0, 1), (1, 0), (1, 2), (2, 1)]
        center_zone = (1, 1)

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            non_road_count = sum(1 for row in roads for cell in row if not cell)
            assert non_road_count > 0, f"Zone {zone_pos} has no non-road cells"

            # Expected non-road counts (340 total - road count)
            if zone_pos == center_zone:
                assert non_road_count == 304, f"Center zone {zone_pos} has {non_road_count} non-road cells, expected 304"
            elif zone_pos in corner_zones:
                assert non_road_count == 306, f"Corner zone {zone_pos} has {non_road_count} non-road cells, expected 306"
            elif zone_pos in edge_zones:
                assert non_road_count == 305, f"Edge zone {zone_pos} has {non_road_count} non-road cells, expected 305"


class TestZoneConnectivity:
    """Test zone-to-zone connections."""

    def test_adjacency_map_built(self):
        """Adjacency map should be built correctly."""
        gen = RoadGenerator()
        assert len(gen.connections) == 9

    def test_corner_zones_have_2_neighbors(self):
        """Corner zones should have 2 neighbors each."""
        gen = RoadGenerator()
        corner_zones = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for zone_pos in corner_zones:
            neighbors = gen.connections[zone_pos]
            assert len(neighbors) == 2, f"Corner zone {zone_pos} has {len(neighbors)} neighbors, expected 2"

    def test_edge_zones_have_3_neighbors(self):
        """Edge zones (non-corner) should have 3 neighbors each."""
        gen = RoadGenerator()
        edge_zones = [(0, 1), (1, 0), (1, 2), (2, 1)]
        for zone_pos in edge_zones:
            neighbors = gen.connections[zone_pos]
            assert len(neighbors) == 3, f"Edge zone {zone_pos} has {len(neighbors)} neighbors, expected 3"

    def test_center_zone_has_4_neighbors(self):
        """Center zone should have 4 neighbors."""
        gen = RoadGenerator()
        neighbors = gen.connections[(1, 1)]
        assert len(neighbors) == 4, f"Center zone has {len(neighbors)} neighbors, expected 4"

    def test_connection_points_valid(self):
        """Connection points should be at zone edges."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            for direction in ["up", "down", "left", "right"]:
                if direction in gen.connections[zone_pos]:
                    point = gen.get_connection_point(zone_pos, direction)
                    x, y = point

                    # Check bounds
                    assert 0 <= x < PLAYABLE_WIDTH
                    assert 0 <= y < PLAYABLE_HEIGHT

                    # Check that connection point is a road
                    roads = gen.zone_roads[zone_pos]
                    assert roads[y][x], f"Connection point {point} in {zone_pos} {direction} is not a road"

    def test_bidirectional_connections(self):
        """Connections should be consistent in both directions."""
        gen = RoadGenerator()

        # If Zone A connects to Zone B in direction D,
        # then Zone B should connect back to Zone A in opposite direction
        direction_opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}

        for zone_pos in gen.connections:
            for direction, neighbor_pos in gen.connections[zone_pos].items():
                opposite_direction = direction_opposites[direction]
                assert opposite_direction in gen.connections[neighbor_pos]
                assert gen.connections[neighbor_pos][opposite_direction] == zone_pos


class TestRoadProperties:
    """Test properties of the road network."""

    def test_roads_have_correct_structure(self):
        """Roads should have correct + structure with proper trimming."""
        gen = RoadGenerator()
        gen.generate()

        # Verify road counts match zone positions
        corner_zones = [(0, 0), (0, 2), (2, 0), (2, 2)]
        edge_zones = [(0, 1), (1, 0), (1, 2), (2, 1)]

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            road_count = sum(1 for row in roads for cell in row if cell)

            if zone_pos == (1, 1):  # Center
                assert road_count == 36
            elif zone_pos in corner_zones:  # Corners
                assert road_count == 34
            elif zone_pos in edge_zones:  # Edges
                assert road_count == 35

    def test_roads_touch_connected_edges(self):
        """Roads should touch edges that have adjacent zones, not perimeter edges."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            zone_row, zone_col = zone_pos
            roads = gen.zone_roads[zone_pos]

            # Check edges only if adjacent zone exists (not perimeter)
            if zone_col > 0:  # Has left neighbor
                left_edge = any(roads[y][0] for y in range(PLAYABLE_HEIGHT))
                assert left_edge, f"Zone {zone_pos} left edge not touched but has neighbor"

            if zone_col < GRID_COLS - 1:  # Has right neighbor
                right_edge = any(roads[y][PLAYABLE_WIDTH - 1] for y in range(PLAYABLE_HEIGHT))
                assert right_edge, f"Zone {zone_pos} right edge not touched but has neighbor"

            if zone_row > 0:  # Has top neighbor
                top_edge = any(roads[0][x] for x in range(PLAYABLE_WIDTH))
                assert top_edge, f"Zone {zone_pos} top edge not touched but has neighbor"

            if zone_row < GRID_ROWS - 1:  # Has bottom neighbor
                bottom_edge = any(roads[PLAYABLE_HEIGHT - 1][x] for x in range(PLAYABLE_WIDTH))
                assert bottom_edge, f"Zone {zone_pos} bottom edge not touched but has neighbor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
