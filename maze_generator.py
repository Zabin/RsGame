#!/usr/bin/env python3
"""
maze_generator.py — Generate flowing maze paths across 3×3 biome grid.

The 9 zones are arranged in a 3×3 grid:
  Row 0: Garden (0,0)     Forest (0,1)     Meadow (0,2)
  Row 1: Desert (1,0)     Cave (1,1)       Swamp (1,2)
  Row 2: Snow Peak (2,0)  Crystal Lake (2,1) Sunset Sky (2,2)

Maze generation:
- Creates paths that traverse all 9 zones
- Ensures connectivity between adjacent zones (up/down/left/right)
- Has dead ends at the 8 perimeter edges
- Starts in Garden, can end anywhere on perimeter
"""

import random
from typing import List, Set, Tuple, Dict
from tilemaps import W, H

# Constants
SCORE_BAR_HEIGHT = 1
PLAYABLE_HEIGHT = H - SCORE_BAR_HEIGHT  # 17 rows
PLAYABLE_WIDTH = W  # 20 tiles
GRID_ROWS = 3
GRID_COLS = 3
NUM_ZONES = 9

# Zone grid layout
ZONE_GRID = [
    [(0, 0), (0, 1), (0, 2)],  # Garden, Forest, Meadow
    [(1, 0), (1, 1), (1, 2)],  # Desert, Cave, Swamp
    [(2, 0), (2, 1), (2, 2)],  # Snow Peak, Crystal Lake, Sunset Sky
]

ZONE_NAMES = {
    (0, 0): "SNOW_PEAK",
    (0, 1): "CRYSTAL_LAKE",
    (0, 2): "SUNSET_SKY",
    (1, 0): "GARDEN",
    (1, 1): "FOREST",
    (1, 2): "MEADOW",
    (2, 0): "DESERT",
    (2, 1): "CAVE",
    (2, 2): "SWAMP",
}


class GridMazeGenerator:
    """Generate maze paths across 3×3 biome grid."""

    def __init__(self, width: int = PLAYABLE_WIDTH, height: int = PLAYABLE_HEIGHT):
        self.zone_width = width
        self.zone_height = height
        # Grid of zones, each with their own maze
        # self.zone_mazes[(row, col)] = 2D list of bools (path vs wall)
        self.zone_mazes: Dict[Tuple[int, int], List[List[bool]]] = {}
        # Connections between zones: (from_zone, direction) -> to_zone
        self.connections: Dict[Tuple[int, int], Tuple[int, int]] = {}

    def generate(self, seed: int = 42) -> Dict[Tuple[int, int], List[List[bool]]]:
        """
        Generate maze paths for all zones in the 3×3 grid.

        Returns:
            Dict mapping (row, col) to zone maze grid
        """
        random.seed(seed)

        # Initialize all zones with empty mazes
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self.zone_mazes[(row, col)] = [
                    [False for _ in range(self.zone_width)] for _ in range(self.zone_height)
                ]

        # Generate paths using spanning tree to ensure all zones connected
        self._generate_spanning_tree()

        # Add internal branching to each zone
        self._add_zone_internal_paths()

        return self.zone_mazes

    def _generate_spanning_tree(self):
        """Generate minimal spanning tree connecting all 9 zones."""
        # Start from Garden (0, 0)
        visited = set()
        edges = []

        def dfs(zone_pos: Tuple[int, int]):
            visited.add(zone_pos)
            row, col = zone_pos

            # Get unvisited neighbors
            neighbors = []
            if row > 0 and (row - 1, col) not in visited:
                neighbors.append(("up", (row - 1, col)))
            if row < GRID_ROWS - 1 and (row + 1, col) not in visited:
                neighbors.append(("down", (row + 1, col)))
            if col > 0 and (row, col - 1) not in visited:
                neighbors.append(("left", (row, col - 1)))
            if col < GRID_COLS - 1 and (row, col + 1) not in visited:
                neighbors.append(("right", (row, col + 1)))

            # Randomize neighbor order
            random.shuffle(neighbors)

            for direction, neighbor_pos in neighbors:
                if neighbor_pos not in visited:
                    # Add edge
                    edges.append((zone_pos, direction, neighbor_pos))
                    # Create path in both zones
                    self._connect_zones(zone_pos, direction, neighbor_pos)
                    # Continue DFS
                    dfs(neighbor_pos)

        dfs((0, 0))  # Start from Garden

    def _connect_zones(
        self, from_zone: Tuple[int, int], direction: str, to_zone: Tuple[int, int]
    ):
        """Create a connection path between two adjacent zones."""
        from_row, from_col = from_zone
        to_row, to_col = to_zone

        # Determine connection points
        if direction == "right":
            # Connect from_zone right edge to to_zone left edge
            from_y = random.randint(2, self.zone_height - 3)
            to_y = from_y
            from_x = self.zone_width - 1
            to_x = 0

        elif direction == "left":
            from_y = random.randint(2, self.zone_height - 3)
            to_y = from_y
            from_x = 0
            to_x = self.zone_width - 1

        elif direction == "down":
            # Connect from_zone bottom edge to to_zone top edge
            from_x = random.randint(2, self.zone_width - 3)
            to_x = from_x
            from_y = self.zone_height - 1
            to_y = 0

        elif direction == "up":
            from_x = random.randint(2, self.zone_width - 3)
            to_x = from_x
            from_y = 0
            to_y = self.zone_height - 1

        # Mark path in both zones
        self.zone_mazes[from_zone][from_y][from_x] = True
        self.zone_mazes[to_zone][to_y][to_x] = True

        # Store connection
        self.connections[(from_zone, direction)] = to_zone

    def _add_zone_internal_paths(self):
        """Add internal winding paths within each zone."""
        for zone_pos in self.zone_mazes:
            self._create_zone_corridor(zone_pos)

    def _create_zone_corridor(self, zone_pos: Tuple[int, int]):
        """Create winding corridor within a single zone."""
        # Start from a random point in the zone (preferably near an existing connection)
        start_y = random.randint(3, self.zone_height - 4)
        start_x = random.randint(3, self.zone_width - 4)

        # Carve paths using random walk
        visited = set()
        self._carve_zone_path(zone_pos, start_x, start_y, visited)

    def _carve_zone_path(
        self, zone_pos: Tuple[int, int], x: int, y: int, visited: Set[Tuple[int, int]]
    ):
        """Recursively carve paths within zone using depth-first search."""
        if (x, y) in visited:
            return

        visited.add((x, y))
        self.zone_mazes[zone_pos][y][x] = True

        # Only recurse about 50% of the time to create walls
        if random.random() > 0.5:
            return

        # Random directions
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]  # Step by 2 to create proper maze
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Bounds check
            if 0 <= nx < self.zone_width and 0 <= ny < self.zone_height:
                if (nx, ny) not in visited:
                    # Carve intermediate cell
                    mid_x, mid_y = x + dx // 2, y + dy // 2
                    if 0 <= mid_x < self.zone_width and 0 <= mid_y < self.zone_height:
                        self.zone_mazes[zone_pos][mid_y][mid_x] = True
                    self._carve_zone_path(zone_pos, nx, ny, visited)

    def get_zone_maze(self, zone_id: int) -> List[List[bool]]:
        """Get maze for a zone by ID (0-8)."""
        row = zone_id // 3
        col = zone_id % 3
        return self.zone_mazes[(row, col)]

    def print_grid_summary(self):
        """Print connectivity summary."""
        print("🌀 Zone Connectivity Summary:\n")
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_pos = (row, col)
                zone_name = ZONE_NAMES[zone_pos]
                print(f"Zone ({row},{col}) {zone_name:12}", end=" → ")

                # Check which zones it connects to
                connections_list = []
                for direction in ["up", "down", "left", "right"]:
                    if (zone_pos, direction) in self.connections:
                        to_zone = self.connections[(zone_pos, direction)]
                        to_name = ZONE_NAMES[to_zone]
                        connections_list.append(f"{direction}({to_name})")

                print(" | ".join(connections_list) if connections_list else "PERIMETER")

    def print_ascii_grid(self):
        """Print ASCII representation of zone grid."""
        print("\n🗺️  Zone Grid Layout:\n")
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_name = ZONE_NAMES[(row, col)]
                print(f"[{zone_name:12}]", end=" ")
            print()


def generate_grid_maze(seed: int = 42) -> GridMazeGenerator:
    """Generate the full 3×3 grid maze."""
    gen = GridMazeGenerator()
    gen.generate(seed=seed)
    return gen


if __name__ == "__main__":
    gen = generate_grid_maze()
    gen.print_ascii_grid()
    gen.print_grid_summary()
    print("\n✅ Maze generated!")
