#!/usr/bin/env python3
"""
maze_generator.py — Generate flowing maze paths across 9 biomes.

Uses recursive backtracking to create naturalistic paths that:
- Start at left edge of Garden (zone 0)
- Flow through all 9 zones sequentially
- End at right edge of Sunset Sky (zone 8)
- Include dead ends and branching for maze-like complexity
"""

import random
from typing import List, Set, Tuple, Dict
from tilemaps import W, H

# Constants
SCORE_BAR_HEIGHT = 1  # Row 0 is score bar, playable area is rows 1-17
PLAYABLE_HEIGHT = H - SCORE_BAR_HEIGHT  # 17 rows
PLAYABLE_WIDTH = W  # 20 tiles
NUM_ZONES = 9


class MazeGenerator:
    """Generate maze paths across 9-zone strip."""

    def __init__(self, width: int = PLAYABLE_WIDTH, height: int = PLAYABLE_HEIGHT, num_zones: int = NUM_ZONES):
        self.zone_width = width
        self.height = height
        self.num_zones = num_zones
        self.total_width = width * num_zones
        # Maze grid: True = path (walkable), False = wall (blocked)
        self.maze = [[False for _ in range(self.total_width)] for _ in range(height)]

    def generate(self, seed: int = 42) -> List[List[bool]]:
        """
        Generate a winding path across all 9 zones.

        Creates a naturalistic corridor that:
        - Starts at left edge of Garden
        - Winds through all zones
        - Ends at right edge of Sunset Sky
        - Includes branching dead ends for maze complexity

        Returns:
            2D list of booleans: True = path, False = wall
        """
        random.seed(seed)

        # Generate main corridor that winds through all 9 zones
        self._create_main_corridor()

        # Add branching dead ends to create maze complexity
        self._add_dead_ends()

        return self.maze

    def _create_main_corridor(self):
        """Create winding main path from left to right across all zones."""
        # Start position: left edge of first zone, middle row
        current_x = 0
        current_y = self.height // 2

        # For each zone, create a winding path to the right
        for zone_id in range(self.num_zones):
            zone_start_x = zone_id * self.zone_width
            zone_end_x = (zone_id + 1) * self.zone_width

            # Create winding corridor through zone
            while current_x < zone_end_x:
                # Mark current position as path
                self.maze[current_y][current_x] = True

                # Move right (required to progress through zone)
                current_x += 1

                # Occasionally wander up/down for natural feel
                if current_x < zone_end_x and random.random() < 0.4:
                    # Try to move vertically
                    dy = random.choice([-1, 1])
                    next_y = current_y + dy
                    if 0 <= next_y < self.height:
                        current_y = next_y

            # Mark path at zone boundary
            if current_x < self.total_width:
                self.maze[current_y][current_x - 1] = True

    def _add_dead_ends(self):
        """Add branching dead ends to create maze complexity."""
        # For each zone, add a few dead-end branches off the main path
        for zone_id in range(self.num_zones):
            num_branches = random.randint(2, 4)

            for _ in range(num_branches):
                # Pick random point on main path in this zone
                zone_start_x = zone_id * self.zone_width
                zone_end_x = (zone_id + 1) * self.zone_width

                # Find a path point in this zone to branch from
                path_x = random.randint(zone_start_x, min(zone_end_x - 1, self.total_width - 1))
                path_y = None

                for y in range(self.height):
                    if self.maze[y][path_x]:
                        path_y = y
                        break

                if path_y is None:
                    continue

                # Create dead end branch
                branch_length = random.randint(2, 5)
                branch_y = path_y

                for _ in range(branch_length):
                    dy = random.choice([-1, 0, 1])
                    next_y = branch_y + dy

                    if 0 <= next_y < self.height:
                        branch_y = next_y
                        if 0 <= path_x < self.total_width:
                            self.maze[branch_y][path_x] = True

    def extract_zone_path(self, zone_id: int) -> List[List[bool]]:
        """
        Extract maze path for a specific zone.

        Args:
            zone_id: Zone number (0-8)

        Returns:
            2D list for this zone (height × width)
        """
        start_x = zone_id * self.zone_width
        end_x = (zone_id + 1) * self.zone_width

        zone_maze = []
        for y in range(self.height):
            row = []
            for x in range(start_x, end_x):
                row.append(self.maze[y][x])
            zone_maze.append(row)

        return zone_maze

    def get_all_zone_paths(self) -> Dict[int, List[List[bool]]]:
        """Get maze paths for all 9 zones."""
        return {zone_id: self.extract_zone_path(zone_id) for zone_id in range(self.num_zones)}

    def find_path_openings(self, zone_id: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Find entry and exit points for a zone.

        Returns:
            ((entry_x, entry_y), (exit_x, exit_y))
        """
        zone_maze = self.extract_zone_path(zone_id)

        # Find leftmost path point in zone (entry point)
        entry = None
        for y in range(self.height):
            if zone_maze[y][0]:  # Leftmost column
                if entry is None:
                    entry = (0, y)
                break

        # Find rightmost path point in zone (exit point)
        exit_point = None
        for y in range(self.height):
            if zone_maze[y][self.zone_width - 1]:  # Rightmost column
                if exit_point is None:
                    exit_point = (self.zone_width - 1, y)
                break

        return entry or (0, self.height // 2), exit_point or (self.zone_width - 1, self.height // 2)


def generate_cross_biome_maze(seed: int = 42) -> Tuple[MazeGenerator, Dict[int, List[List[bool]]]]:
    """
    Generate the full 9-zone maze and return generator + zone paths.

    Returns:
        (maze_generator, zone_paths_dict)
    """
    gen = MazeGenerator()
    gen.generate(seed=seed)
    return gen, gen.get_all_zone_paths()


if __name__ == "__main__":
    print("🌀 Generating 9-zone maze path...\n")

    gen, zone_paths = generate_cross_biome_maze()

    print(f"Maze dimensions: {gen.total_width}w × {gen.height}h ({NUM_ZONES} zones of {PLAYABLE_WIDTH}w)")
    print(f"Generated path across all zones\n")

    # Show zone connectivity info
    for zone_id in range(NUM_ZONES):
        entry, exit_pt = gen.find_path_openings(zone_id)
        zone_names = ["GARDEN", "FOREST", "MEADOW", "DESERT", "CAVE", "SWAMP", "SNOW_PEAK", "CRYSTAL_LAKE", "SUNSET_SKY"]
        print(f"Zone {zone_id:d} ({zone_names[zone_id]:12}) — Entry: {entry}, Exit: {exit_pt}")

    # Simple ASCII visualization of maze (compressed)
    print("\nMaze overview (compressed):")
    for y in range(0, gen.height, 2):  # Show every other row for readability
        line = ""
        for x in range(0, gen.total_width, 2):  # Show every other column
            if gen.maze[y][x]:
                line += "█"  # Path
            else:
                line += " "  # Wall
            if (x // 2 + 1) % 10 == 0:
                line += "|"  # Zone separator every 10 tiles (5 displayed)
        print(line)

    print("\n✅ Maze generated!")
