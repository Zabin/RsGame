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
        """Each zone should have a + shaped road (vertical + horizontal)."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]

            # Check vertical road (column CENTER_X)
            vertical_count = sum(1 for y in range(PLAYABLE_HEIGHT) if roads[y][CENTER_X])
            assert vertical_count == PLAYABLE_HEIGHT, f"Zone {zone_pos} missing vertical road"

            # Check horizontal road (row CENTER_Y_IN_ZONE)
            horizontal_count = sum(1 for x in range(PLAYABLE_WIDTH) if roads[CENTER_Y_IN_ZONE][x])
            assert horizontal_count == PLAYABLE_WIDTH, f"Zone {zone_pos} missing horizontal road"

    def test_road_intersects_at_center(self):
        """Roads should intersect at center of zone."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            # Center point should be a road
            assert roads[CENTER_Y_IN_ZONE][CENTER_X], f"Zone {zone_pos} center not a road"

    def test_all_zones_have_36_road_cells(self):
        """Each zone should have exactly 36 road cells (20 + 17 - 1 center)."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            road_count = sum(1 for row in roads for cell in row if cell)
            assert road_count == 36, f"Zone {zone_pos} has {road_count} road cells, expected 36"

    def test_all_zones_have_non_road_cells(self):
        """Each zone should have non-road cells (for obstacles, scenery)."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            non_road_count = sum(1 for row in roads for cell in row if not cell)
            assert non_road_count > 0, f"Zone {zone_pos} has no non-road cells"
            assert non_road_count == 304, f"Zone {zone_pos} has {non_road_count} non-road cells, expected 304"


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

    def test_roads_are_symmetric(self):
        """Same zone layouts should have identical road patterns."""
        gen = RoadGenerator()
        gen.generate()

        # All zones should have same road structure (just rotated/translated)
        # Get road for first zone as reference
        ref_roads = gen.zone_roads[(0, 0)]
        center_y = CENTER_X - 1

        # Count roads in different sectors
        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]
            assert sum(1 for row in roads for cell in row if cell) == 36

    def test_roads_cover_all_edges(self):
        """Roads should touch all 4 edges of each zone (or be perimeter)."""
        gen = RoadGenerator()
        gen.generate()

        for zone_pos in gen.zone_roads:
            roads = gen.zone_roads[zone_pos]

            # Check left edge
            left_edge = any(roads[y][0] for y in range(PLAYABLE_HEIGHT))
            # Check right edge
            right_edge = any(roads[y][PLAYABLE_WIDTH - 1] for y in range(PLAYABLE_HEIGHT))
            # Check top edge
            top_edge = any(roads[0][x] for x in range(PLAYABLE_WIDTH))
            # Check bottom edge
            bottom_edge = any(roads[PLAYABLE_HEIGHT - 1][x] for x in range(PLAYABLE_WIDTH))

            # All edges should be touched by roads
            assert left_edge, f"Zone {zone_pos} left edge not touched"
            assert right_edge, f"Zone {zone_pos} right edge not touched"
            assert top_edge, f"Zone {zone_pos} top edge not touched"
            assert bottom_edge, f"Zone {zone_pos} bottom edge not touched"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
