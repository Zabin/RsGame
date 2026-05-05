#!/usr/bin/env python3
"""
pathfinding.py — Maze pathfinding and cross-biome path validation.

Validates that each biome's tilemap allows unobstructed path flow from
left edge → right edge at the designated path row.
"""

import heapq
from typing import List, Tuple, Optional
from tilemaps import ALL_SCREENS, W, H


# Tile IDs that block movement
BLOCKED_TILES = {
    0x16,  # TL_ROCK (big rock)
    0x17,  # TL_ROCK_SMALL (small rock)
    0x18,  # TL_TREE_TOP (tree top)
    0x19,  # TL_TREE_BOT (tree bottom/trunk)
    0x1A,  # TL_MUSHROOM
}

# Tile IDs that are walkable (path or grass)
WALKABLE_TILES = {
    0x10,  # TL_GRASS_PLAIN
    0x11,  # TL_GRASS_TUFT
    0x12,  # TL_GRASS_CLOVER
    0x13,  # TL_PATH_CENTER (main path tile)
    0x14,  # TL_PATH_TOP (path top edge)
    0x15,  # TL_PATH_BOT (path bottom edge)
    0x1B,  # TL_BG_FLOWER (walkable accent)
}

# Score bar row
SCORE_BAR_ROW = 0


class PathValidator:
    """Validates path flow through biome tilemaps."""

    def __init__(self, tiles: bytearray, attrs: bytearray):
        """
        Initialize validator with tilemap data.

        Args:
            tiles: 360-byte tilemap (20×18 tiles)
            attrs: 360-byte attribute/palette map
        """
        self.tiles = tiles
        self.attrs = attrs
        self.width = W
        self.height = H
        self.path_map = self._compute_walkability()

    def _compute_walkability(self) -> List[List[bool]]:
        """Compute which tiles are walkable."""
        path_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                idx = y * self.width + x
                tile_id = self.tiles[idx]
                # Score bar is impassable
                is_walkable = y > SCORE_BAR_ROW and (
                    tile_id in WALKABLE_TILES or tile_id not in BLOCKED_TILES
                )
                row.append(is_walkable)
            path_map.append(row)
        return path_map

    def find_path(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find shortest path using A* algorithm.

        Args:
            start: (x, y) starting position
            goal: (x, y) goal position

        Returns:
            List of (x, y) positions, or None if no path exists
        """
        sx, sy = start
        gx, gy = goal

        # Priority queue: (f_score, counter, (x, y))
        counter = 0
        open_set = [(0, counter, (sx, sy))]
        counter += 1

        came_from = {}
        g_score = {(sx, sy): 0}
        f_score = {(sx, sy): self._heuristic((sx, sy), (gx, gy))}

        closed_set = set()

        while open_set:
            _, _, current = heapq.heappop(open_set)
            cx, cy = current

            if current == (gx, gy):
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]

            if current in closed_set:
                continue

            closed_set.add(current)

            for nx, ny in self._neighbors(cx, cy):
                if (nx, ny) in closed_set:
                    continue

                if not self.path_map[ny][nx]:
                    continue

                tentative_g = g_score[current] + 1

                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    came_from[(nx, ny)] = current
                    g_score[(nx, ny)] = tentative_g
                    f = tentative_g + self._heuristic((nx, ny), (gx, gy))
                    f_score[(nx, ny)] = f
                    heapq.heappush(open_set, (f, counter, (nx, ny)))
                    counter += 1

        return None

    def _heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Manhattan distance heuristic."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def _neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighbors (4-directional)."""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors

    def validate_path_row(self, path_row: int = 9) -> Tuple[bool, str]:
        """
        Validate that path_row connects left edge to right edge.

        Args:
            path_row: Row number to validate (typically row 9)

        Returns:
            (is_valid, message)
        """
        start = (0, path_row)
        goal = (self.width - 1, path_row)

        # Check if start/goal positions are walkable
        if not self.path_map[path_row][0]:
            return False, f"Left edge (x=0, row {path_row}) is blocked"
        if not self.path_map[path_row][self.width - 1]:
            return False, f"Right edge (x={self.width-1}, row {path_row}) is blocked"

        # Try direct path first (most zones should have clear path at row 9)
        direct_path_clear = all(self.path_map[path_row][x] for x in range(self.width))
        if direct_path_clear:
            return True, f"Direct path at row {path_row} is clear"

        # If not, try A* pathfinding
        path = self.find_path(start, goal)
        if path:
            return True, f"Path found (length {len(path)}, uses rows {min(p[1] for p in path)}-{max(p[1] for p in path)})"
        else:
            return False, f"No path from left edge to right edge at row {path_row}"


def validate_all_biomes() -> Tuple[bool, List[Tuple[str, bool, str]]]:
    """
    Validate path flow through all biomes.

    Returns:
        (all_valid, results_list)
        where results_list = [(biome_name, is_valid, message), ...]
    """
    results = []
    all_valid = True

    for screen_name, screen_fn in ALL_SCREENS:
        try:
            tiles, attrs = screen_fn()
        except Exception as e:
            results.append((screen_name, False, f"Error rendering: {e}"))
            all_valid = False
            continue

        if not tiles or not attrs or len(tiles) != 360 or len(attrs) != 360:
            results.append((screen_name, False, "Invalid tilemap size"))
            all_valid = False
            continue

        validator = PathValidator(tiles, attrs)
        is_valid, message = validator.validate_path_row(path_row=9)
        results.append((screen_name, is_valid, message))

        if not is_valid:
            all_valid = False

    return all_valid, results


if __name__ == "__main__":
    print("🔍 Validating cross-biome path flow...\n")
    all_valid, results = validate_all_biomes()

    for screen_name, is_valid, message in results:
        status = "✓" if is_valid else "✗"
        print(f"{status} {screen_name:12} — {message}")

    print("\n" + ("=" * 60))
    if all_valid:
        print("✅ All biomes have valid path flow!")
    else:
        print("❌ Some biomes have path flow issues. See above.")
