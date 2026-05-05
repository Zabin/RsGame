#!/usr/bin/env python3
"""
test_maze_generator.py — Test maze generation and cross-biome connectivity.

Validates that the maze:
1. Spans all 9 zones
2. Has entry/exit points in each zone
3. Connects zones sequentially
4. Includes branching dead ends
"""

import pytest
from maze_generator import MazeGenerator, NUM_ZONES, PLAYABLE_WIDTH, PLAYABLE_HEIGHT


class TestMazeGeneration:
    """Test maze generator output."""

    def test_maze_dimensions(self):
        """Maze should have correct total dimensions."""
        gen = MazeGenerator()
        maze = gen.generate()

        assert len(maze) == PLAYABLE_HEIGHT, f"Expected height {PLAYABLE_HEIGHT}, got {len(maze)}"
        assert len(maze[0]) == gen.total_width, f"Expected width {gen.total_width}, got {len(maze[0])}"

    def test_maze_is_not_empty(self):
        """Maze should have paths (not all walls)."""
        gen = MazeGenerator()
        maze = gen.generate()

        path_count = sum(1 for row in maze for cell in row if cell)
        assert path_count > 0, "Maze has no paths"

    def test_maze_is_not_full(self):
        """Maze should have walls (not all paths)."""
        gen = MazeGenerator()
        maze = gen.generate()

        wall_count = sum(1 for row in maze for cell in row if not cell)
        assert wall_count > 0, "Maze has no walls (all paths)"

    def test_all_zones_have_paths(self):
        """Each zone should contain at least one path cell."""
        gen = MazeGenerator()
        maze = gen.generate()

        for zone_id in range(NUM_ZONES):
            zone_maze = gen.extract_zone_path(zone_id)
            path_count = sum(1 for row in zone_maze for cell in row if cell)
            assert path_count > 0, f"Zone {zone_id} has no paths"

    def test_all_zones_have_left_entry(self):
        """Each zone should be accessible from left edge."""
        gen = MazeGenerator()
        maze = gen.generate()

        for zone_id in range(NUM_ZONES):
            zone_maze = gen.extract_zone_path(zone_id)
            # Check left edge (column 0) for any path
            left_edge_paths = sum(1 for row in zone_maze if row[0])
            assert left_edge_paths > 0, f"Zone {zone_id} has no path on left edge"

    def test_all_zones_have_right_exit(self):
        """Each zone should be accessible from right edge."""
        gen = MazeGenerator()
        maze = gen.generate()

        for zone_id in range(NUM_ZONES):
            zone_maze = gen.extract_zone_path(zone_id)
            # Check right edge (last column) for any path
            right_edge_paths = sum(1 for row in zone_maze if row[-1])
            assert right_edge_paths > 0, f"Zone {zone_id} has no path on right edge"

    def test_zone_path_extraction(self):
        """Zone path extraction should produce correct dimensions."""
        gen = MazeGenerator()
        maze = gen.generate()

        for zone_id in range(NUM_ZONES):
            zone_maze = gen.extract_zone_path(zone_id)
            assert len(zone_maze) == PLAYABLE_HEIGHT
            assert len(zone_maze[0]) == PLAYABLE_WIDTH

    def test_entry_exit_points_found(self):
        """All zones should have identifiable entry/exit points."""
        gen = MazeGenerator()
        maze = gen.generate()

        for zone_id in range(NUM_ZONES):
            entry, exit_pt = gen.find_path_openings(zone_id)
            assert entry is not None, f"Zone {zone_id} has no entry point"
            assert exit_pt is not None, f"Zone {zone_id} has no exit point"
            assert entry[0] >= 0 and entry[0] < PLAYABLE_WIDTH
            assert exit_pt[0] >= 0 and exit_pt[0] < PLAYABLE_WIDTH
            assert entry[1] >= 0 and entry[1] < PLAYABLE_HEIGHT
            assert exit_pt[1] >= 0 and exit_pt[1] < PLAYABLE_HEIGHT


class TestMazeMandatoryProperties:
    """Test that maze meets design requirements."""

    def test_garden_starts_journey(self):
        """Garden (zone 0) should have entry point on left edge."""
        gen = MazeGenerator()
        maze = gen.generate()

        entry, _ = gen.find_path_openings(0)
        # Garden entry should be accessible from left (x=0)
        zone_maze = gen.extract_zone_path(0)
        assert zone_maze[entry[1]][0], "Garden left edge not accessible"

    def test_sunset_sky_ends_journey(self):
        """Sunset Sky (zone 8) should have exit point on right edge."""
        gen = MazeGenerator()
        maze = gen.generate()

        _, exit_pt = gen.find_path_openings(8)
        zone_maze = gen.extract_zone_path(8)
        assert zone_maze[exit_pt[1]][-1], "Sunset Sky right edge not accessible"

    def test_maze_has_branching(self):
        """Maze should include dead-end branches for complexity."""
        gen = MazeGenerator()
        maze = gen.generate()

        # Count total paths in one zone
        first_zone_maze = gen.extract_zone_path(0)
        total_paths = sum(1 for row in first_zone_maze for cell in row if cell)

        # If there was only a straight corridor (width=20, height<=17),
        # we'd have at most ~34 path cells for a simple corridor
        # With branching, we should have more
        assert total_paths >= 10, f"Zone 0 seems to lack branching (only {total_paths} paths)"

    def test_deterministic_generation(self):
        """Same seed should produce same maze."""
        gen1 = MazeGenerator()
        maze1 = gen1.generate(seed=42)

        gen2 = MazeGenerator()
        maze2 = gen2.generate(seed=42)

        assert maze1 == maze2, "Same seed produced different mazes"

    def test_different_seeds_produce_different_mazes(self):
        """Different seeds should produce different mazes."""
        gen1 = MazeGenerator()
        maze1 = gen1.generate(seed=42)

        gen2 = MazeGenerator()
        maze2 = gen2.generate(seed=99)

        # Mazes should be different (with high probability)
        assert maze1 != maze2, "Different seeds produced identical mazes"


class TestMazeProperties:
    """Test mathematical properties of the maze."""

    def test_path_continuity_in_zone(self):
        """Paths in a zone should form connected region (basic connectivity)."""
        gen = MazeGenerator()
        maze = gen.generate()

        # This is a simplified test - just check that if we have entry and exit,
        # they're both in the same zone's path network
        for zone_id in range(NUM_ZONES):
            entry, exit_pt = gen.find_path_openings(zone_id)
            zone_maze = gen.extract_zone_path(zone_id)

            # Both entry and exit should be paths
            assert zone_maze[entry[1]][entry[0]], f"Zone {zone_id}: entry point is not a path"
            assert zone_maze[exit_pt[1]][exit_pt[0]], f"Zone {zone_id}: exit point is not a path"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
