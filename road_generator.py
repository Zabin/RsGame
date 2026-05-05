#!/usr/bin/env python3
"""
road_generator.py — Generate simple + shaped roads in each zone.

Each zone has a + (plus) shaped road:
- Vertical road through center (connects top/bottom edges)
- Horizontal road through center (connects left/right edges)
- Center intersection in middle of zone

Roads connect to center of each edge for inter-zone transitions.
"""

from typing import List, Tuple, Dict
from tilemaps import W, H

# Constants
SCORE_BAR_HEIGHT = 1
PLAYABLE_HEIGHT = H - SCORE_BAR_HEIGHT  # 17 rows
PLAYABLE_WIDTH = W  # 20 tiles
GRID_ROWS = 3
GRID_COLS = 3
NUM_ZONES = 9

# Calculate center positions (0-indexed within playable area)
CENTER_X = PLAYABLE_WIDTH // 2  # 10
CENTER_Y = (PLAYABLE_HEIGHT // 2) + SCORE_BAR_HEIGHT  # 9 (accounting for score bar)

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

# Map from zone_id (journey order 0-8) to grid position (row, col)
ZONE_ID_TO_GRID = {
    0: (1, 0),  # GARDEN
    1: (1, 1),  # FOREST
    2: (1, 2),  # MEADOW
    3: (2, 0),  # DESERT
    4: (2, 1),  # CAVE
    5: (2, 2),  # SWAMP
    6: (0, 0),  # SNOW_PEAK
    7: (0, 1),  # CRYSTAL_LAKE
    8: (0, 2),  # SUNSET_SKY
}


class RoadGenerator:
    """Generate + shaped roads for 3×3 zone grid."""

    def __init__(self, width: int = PLAYABLE_WIDTH, height: int = PLAYABLE_HEIGHT):
        self.width = width
        self.height = height
        # Road map: True = road cell, False = non-road
        self.zone_roads: Dict[Tuple[int, int], List[List[bool]]] = {}
        # Zone adjacency for connections
        self.connections: Dict[Tuple[int, int], Dict[str, Tuple[int, int]]] = self._build_adjacency()

    def _build_adjacency(self) -> Dict[Tuple[int, int], Dict[str, Tuple[int, int]]]:
        """Build zone adjacency map (which zones connect in which directions)."""
        connections = {}
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_pos = (row, col)
                connections[zone_pos] = {}

                # Check all 4 directions
                if row > 0:
                    connections[zone_pos]["up"] = (row - 1, col)
                if row < GRID_ROWS - 1:
                    connections[zone_pos]["down"] = (row + 1, col)
                if col > 0:
                    connections[zone_pos]["left"] = (row, col - 1)
                if col < GRID_COLS - 1:
                    connections[zone_pos]["right"] = (row, col + 1)

        return connections

    def generate(self) -> Dict[Tuple[int, int], List[List[bool]]]:
        """
        Generate + shaped roads for all zones.

        Returns:
            Dict mapping (row, col) to zone road grid
        """
        # Initialize all zones with empty roads (all False = non-road)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self.zone_roads[(row, col)] = [
                    [False for _ in range(self.width)] for _ in range(self.height)
                ]

        # Generate + shaped roads for each zone
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self._create_plus_road((row, col))

        return self.zone_roads

    def _create_plus_road(self, zone_pos: Tuple[int, int]):
        """Create + shaped road in a single zone, with dead ends trimmed."""
        zone_row, zone_col = zone_pos
        zone_roads = self.zone_roads[zone_pos]
        center_y_in_zone = CENTER_Y - SCORE_BAR_HEIGHT

        # Vertical road: draw only if there's an adjacent zone in that direction
        # If no "up" neighbor (on perimeter or corner), start road from row 1 instead of row 0
        # If no "down" neighbor (on perimeter or corner), end road at row height-2 instead of height-1
        has_up = "up" in self.connections[zone_pos]
        has_down = "down" in self.connections[zone_pos]

        vertical_start = 0 if has_up else 1
        vertical_end = self.height if has_down else self.height - 1

        for y in range(vertical_start, vertical_end):
            zone_roads[y][CENTER_X] = True

        # Horizontal road: draw only if there's an adjacent zone in that direction
        # If no "left" neighbor (on perimeter or corner), start road from col 1 instead of col 0
        # If no "right" neighbor (on perimeter or corner), end road at col width-2 instead of width-1
        has_left = "left" in self.connections[zone_pos]
        has_right = "right" in self.connections[zone_pos]

        horizontal_start = 0 if has_left else 1
        horizontal_end = self.width if has_right else self.width - 1

        for x in range(horizontal_start, horizontal_end):
            zone_roads[center_y_in_zone][x] = True

    def get_zone_road(self, zone_id: int) -> List[List[bool]]:
        """Get road map for zone by ID (0-8 in journey order)."""
        row, col = ZONE_ID_TO_GRID[zone_id]
        return self.zone_roads[(row, col)]

    def get_connection_point(
        self, zone_pos: Tuple[int, int], direction: str
    ) -> Tuple[int, int]:
        """
        Get (x, y) connection point at edge of zone.

        Args:
            zone_pos: (row, col) of zone
            direction: "up", "down", "left", or "right"

        Returns:
            (x, y) pixel coordinate within zone where road meets edge
        """
        center_y_in_zone = CENTER_Y - SCORE_BAR_HEIGHT

        if direction == "left":
            return (0, center_y_in_zone)
        elif direction == "right":
            return (self.width - 1, center_y_in_zone)
        elif direction == "up":
            return (CENTER_X, 0)
        elif direction == "down":
            return (CENTER_X, self.height - 1)

    def print_zone_info(self):
        """Print road connection information for all zones."""
        print("🛣️  Road Network Summary:\n")
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_pos = (row, col)
                zone_name = ZONE_NAMES[zone_pos]
                print(f"Zone ({row},{col}) {zone_name:12}")

                # Print connections
                for direction in ["up", "down", "left", "right"]:
                    if direction in self.connections[zone_pos]:
                        neighbor = self.connections[zone_pos][direction]
                        neighbor_name = ZONE_NAMES[neighbor]
                        connection_point = self.get_connection_point(zone_pos, direction)
                        print(f"  {direction:5} → {neighbor_name:12} at {connection_point}")
                    else:
                        print(f"  {direction:5} → PERIMETER EDGE")
                print()

    def print_road_stats(self):
        """Print road statistics."""
        print("\n📊 Road Statistics:\n")
        for zone_pos in self.zone_roads:
            zone_name = ZONE_NAMES[zone_pos]
            road_map = self.zone_roads[zone_pos]
            road_cells = sum(1 for row in road_map for cell in row if cell)
            non_road_cells = len(road_map) * len(road_map[0]) - road_cells

            print(f"{zone_name:12} → {road_cells:3} road cells, {non_road_cells:3} non-road cells")


def generate_roads(width: int = PLAYABLE_WIDTH, height: int = PLAYABLE_HEIGHT) -> RoadGenerator:
    """Generate + shaped roads for the 3×3 grid."""
    gen = RoadGenerator(width, height)
    gen.generate()
    return gen


if __name__ == "__main__":
    print("🛣️  Generating + shaped roads...\n")

    gen = generate_roads()
    gen.print_zone_info()
    gen.print_road_stats()

    print("✅ Road network generated!")
