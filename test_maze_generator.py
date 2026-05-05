#!/usr/bin/env python3
"""
test_maze_generator.py — Test 3×3 grid maze generation.

Validates that the maze:
1. Connects all 9 zones in a spanning tree
2. Each zone has internal path structure
3. Zone-to-zone connections exist
"""

import pytest
from maze_generator import GridMazeGenerator, GRID_ROWS, GRID_COLS, NUM_ZONES, PLAYABLE_HEIGHT, PLAYABLE_WIDTH


class TestGridMazeGeneration:
    """Test grid-based maze generator."""

    def test_maze_generates_successfully(self):
        """Maze should generate without errors."""
        gen = GridMazeGenerator()
        maze = gen.generate()
        assert maze is not None
        assert len(maze) == NUM_ZONES

    def test_all_zones_have_maze(self):
        """All 9 zones should have maze data."""
        gen = GridMazeGenerator()
        gen.generate()

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                assert (row, col) in gen.zone_mazes
                assert gen.zone_mazes[(row, col)] is not None

    def test_zone_maze_dimensions(self):
        """Each zone maze should have correct dimensions."""
        gen = GridMazeGenerator()
        gen.generate()

        for zone_pos in gen.zone_mazes:
            maze = gen.zone_mazes[zone_pos]
            assert len(maze) == PLAYABLE_HEIGHT
            assert len(maze[0]) == PLAYABLE_WIDTH

    def test_all_zones_have_paths(self):
        """Each zone should have at least one path cell."""
        gen = GridMazeGenerator()
        gen.generate()

        for zone_pos in gen.zone_mazes:
            maze = gen.zone_mazes[zone_pos]
            path_count = sum(1 for row in maze for cell in row if cell)
            assert path_count > 0, f"Zone {zone_pos} has no paths"

    def test_all_zones_have_walls(self):
        """Each zone should have some walls (not all paths)."""
        gen = GridMazeGenerator()
        gen.generate()

        for zone_pos in gen.zone_mazes:
            maze = gen.zone_mazes[zone_pos]
            wall_count = sum(1 for row in maze for cell in row if not cell)
            assert wall_count > 0, f"Zone {zone_pos} is all paths"

    def test_zone_to_zone_connections_exist(self):
        """Spanning tree should create zone-to-zone connections."""
        gen = GridMazeGenerator()
        gen.generate()

        # Should have 8 connections (for spanning tree of 9 nodes)
        assert len(gen.connections) == 8, f"Expected 8 connections, got {len(gen.connections)}"

    def test_garden_is_connected(self):
        """Garden (0,0) should be connected to at least one neighbor."""
        gen = GridMazeGenerator()
        gen.generate()

        garden_connections = [
            direction for (zone, direction) in gen.connections if zone == (0, 0)
        ]
        assert len(garden_connections) > 0, "Garden has no outgoing connections"

    def test_all_zones_reachable(self):
        """All zones should be reachable via spanning tree."""
        gen = GridMazeGenerator()
        gen.generate()

        # Build adjacency from connections
        reachable = set()
        to_visit = [(0, 0)]  # Start from Garden

        while to_visit:
            zone = to_visit.pop(0)
            if zone in reachable:
                continue
            reachable.add(zone)

            # Find connections from this zone
            for (from_zone, direction), to_zone in gen.connections.items():
                if from_zone == zone and to_zone not in reachable:
                    to_visit.append(to_zone)

        assert len(reachable) == NUM_ZONES, f"Only {len(reachable)}/{NUM_ZONES} zones reachable"

    def test_get_zone_maze_by_id(self):
        """get_zone_maze should return correct zone by ID."""
        gen = GridMazeGenerator()
        gen.generate()

        # Zone 0 = (0,0) = Garden
        maze_0 = gen.get_zone_maze(0)
        maze_0_0 = gen.zone_mazes[(0, 0)]
        assert maze_0 == maze_0_0

        # Zone 4 = (1,1) = Cave
        maze_4 = gen.get_zone_maze(4)
        maze_1_1 = gen.zone_mazes[(1, 1)]
        assert maze_4 == maze_1_1

        # Zone 8 = (2,2) = Sunset Sky
        maze_8 = gen.get_zone_maze(8)
        maze_2_2 = gen.zone_mazes[(2, 2)]
        assert maze_8 == maze_2_2


class TestMazeDeterminism:
    """Test deterministic maze generation."""

    def test_same_seed_same_maze(self):
        """Same seed should produce identical maze."""
        gen1 = GridMazeGenerator()
        gen1.generate(seed=42)

        gen2 = GridMazeGenerator()
        gen2.generate(seed=42)

        # Compare all zones
        for zone_pos in gen1.zone_mazes:
            assert gen1.zone_mazes[zone_pos] == gen2.zone_mazes[zone_pos]

    def test_different_seeds_different_mazes(self):
        """Different seeds should produce different mazes."""
        gen1 = GridMazeGenerator()
        gen1.generate(seed=42)

        gen2 = GridMazeGenerator()
        gen2.generate(seed=99)

        # At least some zones should differ
        different = False
        for zone_pos in gen1.zone_mazes:
            if gen1.zone_mazes[zone_pos] != gen2.zone_mazes[zone_pos]:
                different = True
                break

        assert different, "Different seeds produced identical mazes"


class TestMazeProperties:
    """Test mathematical properties of maze."""

    def test_spanning_tree_is_minimal(self):
        """Spanning tree should have exactly 8 edges for 9 nodes."""
        gen = GridMazeGenerator()
        gen.generate()

        # A spanning tree of N nodes has exactly N-1 edges
        assert len(gen.connections) == 9 - 1

    def test_no_cycles_in_spanning_tree(self):
        """Spanning tree should not have cycles."""
        gen = GridMazeGenerator()
        gen.generate()

        # Build graph and check for cycles
        graph = {}
        for (from_zone, direction), to_zone in gen.connections.items():
            if from_zone not in graph:
                graph[from_zone] = []
            graph[from_zone].append(to_zone)

        # Simple DFS to detect cycle
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True

            rec_stack.remove(node)
            return False

        visited = set()
        rec_stack = set()
        for node in graph:
            if node not in visited:
                assert not has_cycle(node, visited, rec_stack), "Cycle detected in spanning tree"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
