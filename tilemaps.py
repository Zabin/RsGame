"""
tilemaps.py — Screen tilemap generators and collectible spawn tables.
Edit screen functions to change zone/menu layouts.
Edit ZONE_COLLECTS to move or add collectibles.
"""
from tiles import *

W, H = 20, 18   # BG map dimensions in tiles (160×144 pixels = visible GBC screen)

# ── Cross-Biome Flow Reference ────────────────────────────────────────────
# Master design blueprint: 9 zones in journey order.
# Rules: path at row 9 in ALL zones, accent colors 5/6/7 (pink/yellow/purple)
# appear in every zone. Walls/objects guide path. Minimal transitions.
CROSS_BIOME_FLOW = {
    "journey": "Garden→Forest→Meadow→Desert→Cave→Swamp→SnowPeak→CrystalLake→SunsetSky",
    "path_row": 9,                  # constant across ALL zones (row 9-10 dirt path)
    "accent_palettes": [5, 6, 7],   # pink/yellow/purple shared accent in every zone
    "elevation_arc": "Garden(start) → Forest → Meadow → Desert → Cave(lowest) → Swamp(rising) → SnowPeak(peak) → CrystalLake → SunsetSky(return)",
    "zones": [
        {"id": 0, "name": "GARDEN",       "palette_family": [0,5,6,7], "theme": "welcoming home - flowers, grass, gentle rocks", "elevation": "start"},
        {"id": 1, "name": "FOREST",       "palette_family": [0,3,5,7], "theme": "wild woodland - tree corridors, mushrooms, shade", "elevation": "gentle descent"},
        {"id": 2, "name": "MEADOW",       "palette_family": [0,5,6,7], "theme": "open field - wide sky, scattered flowers, rocks", "elevation": "descent"},
        {"id": 3, "name": "DESERT",       "palette_family": [1,4,6],   "theme": "arid waste - sand, rock walls, sparse plants", "elevation": "steep descent"},
        {"id": 4, "name": "CAVE",         "palette_family": [4,7],     "theme": "underground - stone corridors, mineral accents", "elevation": "lowest point"},
        {"id": 5, "name": "SWAMP",        "palette_family": [0,3,5],   "theme": "murky wetland - dense flora, mushroom walls", "elevation": "ascending"},
        {"id": 6, "name": "SNOW_PEAK",    "palette_family": [0,4,7],   "theme": "icy summit - white, crystal formations, sparse", "elevation": "peak"},
        {"id": 7, "name": "CRYSTAL_LAKE", "palette_family": [0,6,7],   "theme": "ethereal water - light, reflective, peaceful", "elevation": "high plateau"},
        {"id": 8, "name": "SUNSET_SKY",   "palette_family": [5,6,7],   "theme": "warm return - golden light, home on horizon", "elevation": "return home"},
    ],
    "design_rules": {
        "vertical_flow": "Path (row 9-10) visually connects upper decorations (rows 1-8) to lower decorations (rows 11-17)",
        "walls": "Cluster rocks/trees to create corridors guiding player along path row, especially at path edges",
        "accents": "Pink(5) yellow(6) purple(7) flowers appear in EVERY zone as connecting thread",
        "breathing_room": "25-30% plain grass - avoid cluttering every tile",
        "clustering": "Group same tiles together - NOT scattered randomly",
        "transitions": "Minimal - hard zone boundary, no gradual blending",
        "landmarks": "1-3 distinct visual anchors per zone (tree group, rock cluster, flower bed)",
    },
}

def _blank(t=TL_BG_BLANK, p=2):
    return bytearray([t] * (W * H)), bytearray([p] * (W * H))

def _put(tiles, attrs, x, y, t, p):
    if 0 <= x < W and 0 <= y < H:
        tiles[y * W + x] = t
        attrs[y * W + x] = p & 7

def _str(tiles, attrs, x, y, s, p=2):
    for i, c in enumerate(s.upper()):
        _put(tiles, attrs, x + i, y, char_to_tile(c), p)

def _fill_grass(tiles, attrs, y0, y1):
    """Deterministic grass pattern using tile coords as seed."""
    for y in range(y0, y1):
        for x in range(W):
            h = (y * 7 + x * 13 + 5) % 16
            t = TL_GRASS_PLAIN if h < 9 else (TL_GRASS_TUFT if h < 13 else TL_GRASS_CLOVER)
            _put(tiles, attrs, x, y, t, 0)

def _score_bar(tiles, attrs, zone_name=""):
    """Top row: dark bar with gift hearts, score digits, zone label."""
    for x in range(W):
        _put(tiles, attrs, x, 0, TL_BG_BLANK, 2)
    _put(tiles, attrs, 1, 0, TL_GIFT_ICON, 2)
    _put(tiles, attrs, 2, 0, TL_HEART_EMPTY, 2)
    _put(tiles, attrs, 3, 0, TL_HEART_EMPTY, 2)
    _put(tiles, attrs, 4, 0, TL_HEART_EMPTY, 2)
    _put(tiles, attrs, 7, 0, TL_STAR_ICON_BG, 2)
    _put(tiles, attrs, 8, 0, TL_DIGIT_0, 2)
    _put(tiles, attrs, 9, 0, TL_DIGIT_0, 2)
    _put(tiles, attrs, 10, 0, TL_DIGIT_0, 2)
    if zone_name:
        _str(tiles, attrs, 13, 0, zone_name, 2)

def _horizontal_path(tiles, attrs, row=9):
    """Draw a 2-tile-tall dirt path at 'row'."""
    for x in range(W):
        _put(tiles, attrs, x, row,   TL_PATH_TOP, 1)
        _put(tiles, attrs, x, row+1, TL_PATH_BOT, 1)

def _apply_zone_roads(tiles, attrs, zone_id):
    """Apply + shaped roads from road generator to zone tilemap."""
    from road_generator import RoadGenerator
    gen = RoadGenerator()
    gen.generate()
    road_map = gen.get_zone_road(zone_id)

    # Place road tiles where road map indicates True, but only on grass (don't overwrite decorations)
    grass_tiles = {TL_GRASS_PLAIN, TL_GRASS_TUFT, TL_GRASS_CLOVER}
    for y in range(len(road_map)):
        for x in range(len(road_map[0])):
            if road_map[y][x]:
                tile_idx = (y + 1) * W + x  # y+1 to account for score bar
                # Only replace grass tiles with road tiles
                if tile_idx < len(tiles) and tiles[tile_idx] in grass_tiles:
                    _put(tiles, attrs, x, y + 1, TL_PATH, 1)

# ── Zone screens ──────────────────────────────────────────────────────────
def garden_screen():
    """Starting garden: Vibrant, welcoming Pokémon-style garden with fountains and flower beds."""
    t, a = _blank(TL_GRASS_PLAIN, 0)
    _score_bar(t, a, "GARDEN")
    _fill_grass(t, a, 1, 18)
    _apply_zone_roads(t, a, 0)  # Zone 0 = Garden (base layer)

    # ── EDGE BORDERS: Rock frame around perimeter ────────────────────────────────────
    # Top border (row 1-2)
    for x in range(W):
        _put(t, a, x, 1, TL_ROCK, 4)

    # Bottom border (row 16-17)
    for x in range(W):
        _put(t, a, x, 16, TL_ROCK, 4)

    # Left border (col 0)
    for y in range(3, 16):
        _put(t, a, 0, y, TL_ROCK, 4)

    # Right border (col 19)
    for y in range(3, 16):
        _put(t, a, 19, y, TL_ROCK, 4)

    # ── GRASS TEXTURE: Structured patterns for visual flow ─────────────────────────
    # Upper garden zone (rows 3-5): Clover/tuft pattern flowing from left
    for x in range(1, 8):
        if x % 2 == 0:
            _put(t, a, x, 3, TL_GRASS_CLOVER, 0)
        if (x + 1) % 3 == 0:
            _put(t, a, x, 4, TL_GRASS_TUFT, 0)

    # Upper garden zone: Pattern from right side
    for x in range(12, 19):
        if x % 2 == 1:
            _put(t, a, x, 3, TL_GRASS_CLOVER, 0)
        if (x + 1) % 3 == 1:
            _put(t, a, x, 4, TL_GRASS_TUFT, 0)

    # Lower garden zone (rows 12-14): Clover arcs
    for x in range(1, 8):
        if (x + 2) % 3 == 0:
            _put(t, a, x, 12, TL_GRASS_CLOVER, 0)
            _put(t, a, x, 13, TL_GRASS_TUFT, 0)

    for x in range(12, 19):
        if (x + 2) % 3 == 0:
            _put(t, a, x, 12, TL_GRASS_CLOVER, 0)
            _put(t, a, x, 13, TL_GRASS_TUFT, 0)

    # ── VISUAL ANCHORS: Tree landmarks ────────────────────────────────────────────
    # Upper-left tree (framing upper garden)
    _put(t, a, 2, 3, TL_TREE_TOP, 3)
    _put(t, a, 2, 4, TL_TREE_BOT, 3)

    # Upper-right tree (framing upper garden)
    _put(t, a, 17, 3, TL_TREE_TOP, 3)
    _put(t, a, 17, 4, TL_TREE_BOT, 3)

    # ── CENTRAL FLOWER GARDENS: Color-accented clusters ─────────────────────────────
    # Upper-left garden cluster
    upper_left_flowers = [
        (4, 2, 5), (5, 2, 5), (6, 2, 6),      # Pink and yellow top row
        (4, 3, 6), (5, 3, 7), (6, 3, 5),      # Mixed palette middle
    ]

    # Upper-right garden cluster
    upper_right_flowers = [
        (13, 2, 7), (14, 2, 6), (15, 2, 5),   # Purple, yellow, pink
        (13, 3, 5), (14, 3, 7), (15, 3, 6),   # Pink, purple, yellow
    ]

    # Upper-center garden cluster
    upper_center_flowers = [
        (8, 2, 6), (9, 2, 5), (10, 2, 7),     # Yellow, pink, purple
        (8, 3, 5), (9, 3, 6), (10, 3, 5),     # Pink, yellow, pink
    ]

    # Lower-left garden cluster (below path)
    lower_left_flowers = [
        (3, 14, 5), (4, 14, 6), (5, 14, 7),   # Pink, yellow, purple
        (3, 15, 7), (4, 15, 5), (5, 15, 6),   # Purple, pink, yellow
    ]

    # Lower-right garden cluster (below path)
    lower_right_flowers = [
        (14, 14, 7), (15, 14, 5), (16, 14, 6), # Purple, pink, yellow
        (14, 15, 6), (15, 15, 7), (16, 15, 5), # Yellow, purple, pink
    ]

    # Lower-center garden cluster (below path)
    lower_center_flowers = [
        (8, 15, 6), (9, 15, 5), (10, 15, 7),  # Yellow, pink, purple
        (8, 16, 5), (9, 16, 7), (10, 16, 6),  # Pink, purple, yellow
    ]

    # Apply all flower clusters (skip if road tile)
    all_flowers = (upper_left_flowers + upper_right_flowers + upper_center_flowers +
                   lower_left_flowers + lower_right_flowers + lower_center_flowers)

    for x, y, p in all_flowers:
        tile_idx = (y + 1) * W + x  # Account for score bar
        if tile_idx < len(t) and t[tile_idx] != TL_PATH:  # Don't overlap roads
            _put(t, a, x, y, TL_BG_FLOWER, p)

    # ── FOUNTAIN FEATURE: Bottom left quadrant ────────────────────────────────────
    # Fountain center (using rock as base - decorative accent)
    fountain_tiles = [(2, 14), (2, 13), (1, 14), (3, 13)]
    for x, y in fountain_tiles:
        tile_idx = (y + 1) * W + x
        if tile_idx < len(t) and t[tile_idx] != TL_PATH:
            _put(t, a, x, y, TL_ROCK_SMALL, 4)

    # Flowers around fountain for welcoming feel
    fountain_flowers = [(1, 12, 5), (3, 12, 6)]
    for x, y, p in fountain_flowers:
        tile_idx = (y + 1) * W + x
        if tile_idx < len(t) and t[tile_idx] != TL_PATH:
            _put(t, a, x, y, TL_BG_FLOWER, p)

    # ── PATH FRAMING: Accent flowers directly adjacent to main path ────────────────
    # Just above path (row 8)
    path_frame_upper = [
        (5, 8, 5), (7, 8, 6), (9, 8, 5),
        (11, 8, 7), (13, 8, 5), (15, 8, 6),
    ]

    # Just below path (row 11)
    path_frame_lower = [
        (5, 11, 6), (7, 11, 7), (9, 11, 5),
        (11, 11, 6), (13, 11, 7), (15, 11, 5),
    ]

    for x, y, p in path_frame_upper + path_frame_lower:
        tile_idx = (y + 1) * W + x
        if tile_idx < len(t) and t[tile_idx] != TL_PATH:
            _put(t, a, x, y, TL_BG_FLOWER, p)

    _put(t, a, 18, 8, TL_ARROW, 2)   # zone-exit hint
    return t, a

def forest_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)
    _score_bar(t, a, "FOREST")
    _fill_grass(t, a, 1, 18)
    _apply_zone_roads(t, a, 1)  # Zone 1 = FOREST (base layer)
    # Tree walls at top and bottom edges (every 3 columns)
    for x in range(W):
        if (x + 1) % 3 == 0:
            _put(t, a, x, 1,  TL_TREE_TOP, 3)
            _put(t, a, x, 2,  TL_TREE_BOT, 3)
            _put(t, a, x, 15, TL_TREE_TOP, 3)
            _put(t, a, x, 16, TL_TREE_BOT, 3)
    deco = [
        (2,  5,  TL_MUSHROOM, 3), (5,  4,  TL_MUSHROOM, 3),
        (8,  6,  TL_MUSHROOM, 3), (11, 5,  TL_MUSHROOM, 3),
        (3,  13, TL_MUSHROOM, 3), (7,  13, TL_BG_FLOWER, 5),
        (10, 14, TL_MUSHROOM, 3), (4,  14, TL_BG_FLOWER, 7),
        (14, 4,  TL_BG_FLOWER, 5), (16, 12, TL_MUSHROOM, 3),
    ]
    for x, y, tt, p in deco:
        _put(t, a, x, y, tt, p)
    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a

def meadow_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)
    _score_bar(t, a, "MEADOW")
    _fill_grass(t, a, 1, 18)
    _apply_zone_roads(t, a, 2)  # Zone 2 = MEADOW (base layer)
    flowers = [
        (1,3,6),(3,4,5),(5,3,7),(7,4,6),(9,3,5),(11,4,7),
        (2,6,5),(6,6,6),(9,7,7),(12,6,5),(4,12,6),(8,13,7),
        (10,12,5),(13,13,6),(2,14,7),(5,15,5),(8,14,6),(11,15,7),
        (14,4,5),(15,6,7),(17,3,6),(3,16,7),(13,16,5),
    ]
    for x, y, p in flowers:
        _put(t, a, x, y, TL_BG_FLOWER, p)
    _apply_zone_roads(t, a, 2)  # Zone 2 = Meadow
    _put(t, a, 6,  5,  TL_ROCK,       4)
    _put(t, a, 13, 13, TL_ROCK_SMALL, 4)
    _put(t, a, 17, 15, TL_ROCK_SMALL, 4)
    return t, a

# ── Menu/story screens ────────────────────────────────────────────────────
def desert_screen():
    t, a = _blank(TL_GRASS_PLAIN, 1)  # Palette 1: dirt base
    _score_bar(t, a, "DESERT")
    _fill_grass(t, a, 1, 18)
    _apply_zone_roads(t, a, 3)  # Zone 3 = DESERT (base layer)

    # Rock formations — desert shelter/shelter
    # Left side columns
    for y in range(4, 8):
        _put(t, a, 2, y, TL_ROCK, 4)
    for y in range(12, 16):
        _put(t, a, 2, y, TL_ROCK, 4)

    # Right side columns
    for y in range(3, 7):
        _put(t, a, 17, y, TL_ROCK, 4)
    for y in range(13, 17):
        _put(t, a, 17, y, TL_ROCK, 4)

    # Central rock cluster (ascending toward peak)
    for rx, ry in [(10, 2), (9, 3), (11, 3), (10, 4)]:
        _put(t, a, rx, ry, TL_ROCK_SMALL, 4)

    # Sparse yellow flowers (oasis feel) — palette 6
    flowers = [
        (5, 3, 6), (6, 4, 6),
        (14, 4, 6), (15, 3, 6),
        (8, 14, 6), (9, 15, 6),
        (11, 14, 6), (12, 15, 6),
    ]
    for x, y, p in flowers:
        _put(t, a, x, y, TL_BG_FLOWER, p)

    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a


def cave_screen():
    t, a = _blank(TL_GRASS_PLAIN, 4)  # Palette 4: gray/rock base
    _score_bar(t, a, "CAVE")
    _fill_grass(t, a, 1, 18)
    _apply_zone_roads(t, a, 4)  # Zone 4 = CAVE (base layer)

    # Rock walls forming cave passage
    for y in range(2, 6):
        _put(t, a, 0, y, TL_ROCK, 4)
    for y in range(12, 16):
        _put(t, a, 0, y, TL_ROCK, 4)

    for y in range(2, 6):
        _put(t, a, 19, y, TL_ROCK, 4)
    for y in range(12, 16):
        _put(t, a, 19, y, TL_ROCK, 4)

    # Rock clusters in center (mineral formations)
    for rx, ry in [(5, 3), (6, 4), (14, 3), (15, 4), (10, 5), (10, 13)]:
        _put(t, a, rx, ry, TL_ROCK_SMALL, 4)

    # Purple crystal accents (glowing minerals) — palette 7
    crystals = [
        (3, 2, 7), (17, 2, 7),
        (4, 13, 7), (16, 13, 7),
        (10, 6, 7), (10, 12, 7),
        (8, 8, 7), (12, 8, 7),
    ]
    for x, y, p in crystals:
        _put(t, a, x, y, TL_BG_FLOWER, p)

    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a


def swamp_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)  # Palette 0: grass base
    _score_bar(t, a, "SWAMP")
    _fill_grass(t, a, 1, 18)
    _apply_zone_roads(t, a, 5)  # Zone 5 = SWAMP (base layer)

    # Dense tree walls (swamp forest)
    for x in range(1, W, 2):
        _put(t, a, x, 2, TL_TREE_TOP, 3)
        _put(t, a, x, 3, TL_TREE_BOT, 3)
        _put(t, a, x, 15, TL_TREE_TOP, 3)
        _put(t, a, x, 16, TL_TREE_BOT, 3)

    # Pink flowers (wetland blooms) — palette 5
    flowers = [
        (2, 5, 5), (4, 6, 5), (6, 5, 5),
        (14, 5, 5), (16, 6, 5), (18, 5, 5),
        (3, 12, 5), (5, 11, 5), (8, 12, 5),
        (12, 11, 5), (15, 12, 5), (17, 11, 5),
    ]
    for x, y, p in flowers:
        _put(t, a, x, y, TL_BG_FLOWER, p)

    # Mushroom clusters (swamp fungi) — palette 5
    for mx, my in [(10, 4), (10, 14)]:
        _put(t, a, mx, my, TL_MUSHROOM, 5)

    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a


def snow_peak_screen():
    t, a = _blank(TL_SNOW_GROUND, 5)  # Snow Peak base: custom snow ground
    _score_bar(t, a, "SNOW PEAK")

    # Fill snowy terrain
    for y in range(1, 18):
        for x in range(20):
            tile_idx = y * 20 + x
            if t[tile_idx] == TL_SNOW_GROUND:
                t[tile_idx] = TL_SNOW_GROUND
                a[tile_idx] = 5

    # Apply snow path (distinct packed snow path through the terrain)
    from road_generator import RoadGenerator
    gen = RoadGenerator()
    gen.generate()
    road_map = gen.get_zone_road(6)  # Zone 6 = SNOW PEAK

    for y in range(len(road_map)):
        for x in range(len(road_map[0])):
            if road_map[y][x]:
                _put(t, a, x, y + 1, TL_SNOW_PATH, 5)  # Snow path with white/light-blue border

    # Rock borders (mountain ridges) - palette 4 for gray rocks
    for x in range(20):
        idx = 1 * 20 + x
        if t[idx] != TL_PATH:
            _put(t, a, x, 1, TL_ROCK, 4)
        idx = 16 * 20 + x
        if t[idx] != TL_PATH:
            _put(t, a, x, 16, TL_ROCK, 4)

    for y in range(2, 16):
        idx = y * 20 + 0
        if t[idx] != TL_PATH:
            _put(t, a, 0, y, TL_ROCK, 4)
        idx = y * 20 + 19
        if t[idx] != TL_PATH:
            _put(t, a, 19, y, TL_ROCK, 4)

    # Pine tree clusters - palette 5 for snow context
    pines = [
        (3, 3), (4, 3),
        (16, 3), (17, 3),
        (2, 14), (3, 14),
        (17, 14), (18, 14),
    ]
    for px, py in pines:
        if py < 18 and px < 20:
            idx = py * 20 + px
            if t[idx] != TL_PATH:
                _put(t, a, px, py, TL_PINE_TREE, 5)

    # Ice cliff formations - palette 5 for snowy ice
    iceCliffs = [
        (10, 2),
        (5, 6), (15, 6),
        (8, 11), (12, 11),
    ]
    for ix, iy in iceCliffs:
        idx = iy * 20 + ix
        if t[idx] != TL_PATH:
            _put(t, a, ix, iy, TL_ICE_CLIFF, 5)

    # Frozen water patches - palette 5 for snowy water
    frozenWater = [
        (2, 5), (3, 5),
        (17, 5), (18, 5),
        (5, 12), (6, 12),
        (14, 12), (15, 12),
    ]
    for fw_x, fw_y in frozenWater:
        idx = fw_y * 20 + fw_x
        if t[idx] != TL_PATH:
            _put(t, a, fw_x, fw_y, TL_FROZEN_WATER, 5)

    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a


def crystal_lake_screen():
    t, a = _blank(TL_CRYSTAL_WATER, 6)  # Crystal Lake: water base with palette 6
    _score_bar(t, a, "CRYSTAL LAKE")

    # Fill water terrain
    for y in range(1, 18):
        for x in range(20):
            tile_idx = y * 20 + x
            if t[tile_idx] == TL_CRYSTAL_WATER:
                t[tile_idx] = TL_CRYSTAL_WATER
                a[tile_idx] = 6

    # Apply crystalline path through water
    from road_generator import RoadGenerator
    gen = RoadGenerator()
    gen.generate()
    road_map = gen.get_zone_road(7)  # Zone 7 = CRYSTAL LAKE

    for y in range(len(road_map)):
        for x in range(len(road_map[0])):
            if road_map[y][x]:
                _put(t, a, x, y + 1, TL_CRYSTAL_PATH, 6)

    # Lily pads scattered throughout - peaceful and minimal
    lily_pads = [
        (2, 3), (5, 4),
        (15, 4), (18, 3),
        (3, 8), (17, 8),
        (2, 13), (7, 12),
        (13, 12), (18, 13),
        (5, 16), (10, 15),
        (15, 16),
    ]
    for lx, ly in lily_pads:
        if ly < 18 and lx < 20:
            idx = ly * 20 + lx
            if t[idx] != TL_CRYSTAL_PATH:
                _put(t, a, lx, ly, TL_LILY_PAD, 6)

    # Crystal formations (faceted crystals) - visual landmarks
    crystals = [
        (10, 2),
        (4, 6), (16, 6),
        (8, 11), (12, 11),
        (10, 16),
    ]
    for cx, cy in crystals:
        if cy < 18 and cx < 20:
            idx = cy * 20 + cx
            if t[idx] != TL_CRYSTAL_PATH:
                _put(t, a, cx, cy, TL_CRYSTAL, 6)

    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a


def sunset_sky_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)  # Palette 0: grass base
    _score_bar(t, a, "SUNSET SKY")
    _fill_grass(t, a, 1, 18)
    _apply_zone_roads(t, a, 8)  # Zone 8 = SUNSET (base layer)

    # Vibrant celebration flowers (pink, yellow, purple) — palettes 5, 6, 7
    flowers = [
        # Upper area — warm welcome
        (2, 2, 5), (4, 2, 6), (6, 2, 7), (8, 2, 5), (10, 2, 6), (12, 2, 7), (14, 2, 5), (16, 2, 6), (18, 2, 7),
        (3, 3, 7), (7, 3, 5), (11, 3, 6), (15, 3, 7),
        # Mid-upper
        (2, 5, 6), (8, 5, 7), (14, 5, 5),
        # Near path above
        (5, 7, 5), (10, 7, 6), (15, 7, 7),
        # Near path below
        (5, 11, 7), (10, 11, 5), (15, 11, 6),
        # Mid-lower
        (2, 14, 7), (8, 14, 6), (14, 14, 5),
        # Lower area — home bound
        (3, 16, 5), (7, 16, 6), (11, 16, 7), (15, 16, 5), (18, 16, 6),
    ]
    for x, y, p in flowers:
        _put(t, a, x, y, TL_BG_FLOWER, p)

    # Minimal trees for framing
    _put(t, a, 1, 4, TL_TREE_TOP, 3)
    _put(t, a, 1, 5, TL_TREE_BOT, 3)
    _put(t, a, 18, 13, TL_TREE_TOP, 3)
    _put(t, a, 18, 14, TL_TREE_BOT, 3)

    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a


def title_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    for s, y in [("BUNNY GARDEN", 4), ("ADVENTURE", 6),
                 ("PRESS START", 11), ("BY CLAUDE", 16)]:
        _str(t, a, (20 - len(s)) // 2, y, s, 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 14, TL_BORDER_H, 2)
    _put(t, a, 3,  8, TL_BG_FLOWER, 5)
    _put(t, a, 16, 8, TL_BG_FLOWER, 6)
    _put(t, a, 4,  9, TL_BG_FLOWER, 7)
    _put(t, a, 15, 9, TL_BG_FLOWER, 5)
    return t, a

def intro_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    lines = ["TODAY IS HONEYS", "BIRTHDAY!", "",
             "I MUST FIND", "THREE GIFTS", "FOR THE PARTY!", "",
             "PRESS A TO START"]
    for i, ln in enumerate(lines):
        _str(t, a, (20 - len(ln)) // 2, 4 + i, ln, 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 15, TL_BORDER_H, 2)
    return t, a

def save_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 5, 5, "SAVE GAME?", 2)
    _str(t, a, 5, 9, "A: YES", 2)
    _str(t, a, 5, 11, "B: NO", 2)
    for x in range(2, 18):
        _put(t, a, x, 3,  TL_BORDER_H, 2)
        _put(t, a, x, 14, TL_BORDER_H, 2)
    return t, a

def map_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 4,  2,  "WORLD MAP",  2)
    for x in range(2, 18):
        _put(t, a, x, 4, TL_BORDER_H, 2)
    _str(t, a, 1, 6,  "GARDEN", 2)
    _str(t, a, 1, 8,  "FOREST", 2)
    _str(t, a, 1, 10, "MEADOW", 2)
    # Hearts at col 12: rows 6, 8, 10
    _put(t, a, 12, 6,  TL_HEART_EMPTY, 2)
    _put(t, a, 12, 8,  TL_HEART_EMPTY, 2)
    _put(t, a, 12, 10, TL_HEART_EMPTY, 2)
    for x in range(2, 18):
        _put(t, a, x, 12, TL_BORDER_H, 2)
    _str(t, a, 1, 13, "DPAD: MOVE",  2)
    _str(t, a, 1, 14, "START: SAVE", 2)
    _str(t, a, 1, 15, "SELECT: MAP", 2)
    _str(t, a, 1, 16, "B: EXIT MAP", 2)
    return t, a

def victory_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    lines = ["ALL GIFTS!", "", "HONEY WILL BE", "SO HAPPY!", "",
             "HAPPY BIRTHDAY", "HONEY BEAR!", "", "PRESS A"]
    for i, ln in enumerate(lines):
        _str(t, a, (20 - len(ln)) // 2, 3 + i, ln, 2)
    for x, y, p in [(3,14,5),(6,15,6),(9,14,7),(12,15,5),(15,14,6)]:
        _put(t, a, x, y, TL_BG_FLOWER, p)
    return t, a

# All 14 screens: 9 playable zones + 5 menu screens
ALL_SCREENS = [
    ("garden",      garden_screen),
    ("forest",      forest_screen),
    ("meadow",      meadow_screen),
    ("desert",      desert_screen),
    ("cave",        cave_screen),
    ("swamp",       swamp_screen),
    ("snow_peak",   snow_peak_screen),
    ("crystal_lake",crystal_lake_screen),
    ("sunset_sky",  sunset_sky_screen),
    ("title",       title_screen),
    ("intro",       intro_screen),
    ("save",        save_screen),
    ("map",         map_screen),
    ("victory",     victory_screen),
]

# ── Collectibles per zone ─────────────────────────────────────────────────
# Format: (pixel_x, pixel_y, type)
# type: 0=star(yellow) 1=flower(pink) 2=GIFT(purple+yellow) — one gift per zone
# Player spawns at (76, 72). Gifts placed well away from spawn.
ZONE_COLLECTS = [
    # Zone 0 — Garden
    [(24, 32, 0), (80, 32, 1), (136, 32, 0),
     (40, 96, 1), (120, 96, 0),
     (120, 64, 2)],            # gift: top-right area

    # Zone 1 — Forest
    [(32, 40, 1), (64, 40, 0), (96, 40, 1), (128, 40, 0),
     (48, 104, 0), (104, 104, 1),
     (40, 64, 2)],             # gift: top-left area

    # Zone 2 — Meadow
    [(24, 40, 1), (56, 32, 0), (88, 40, 1), (120, 32, 0), (152, 40, 1),
     (40, 104, 0), (88, 104, 1), (136, 104, 0),
     (136, 64, 2)],            # gift: top-right area

    # Zone 3 — Desert
    [(32, 48, 0), (80, 40, 1), (128, 48, 0),
     (56, 104, 1), (112, 104, 0),
     (88, 72, 2)],             # gift: center area

    # Zone 4 — Cave
    [(40, 56, 1), (88, 40, 0), (136, 56, 1),
     (56, 112, 0), (120, 112, 1),
     (88, 80, 2)],             # gift: center area

    # Zone 5 — Swamp
    [(32, 40, 0), (72, 48, 1), (112, 40, 0), (152, 48, 1),
     (48, 104, 1), (128, 104, 0),
     (88, 64, 2)],             # gift: center area

    # Zone 6 — Snow Peak
    [(40, 56, 1), (88, 32, 0), (136, 56, 1),
     (56, 112, 0), (120, 112, 1),
     (88, 72, 2)],             # gift: center area

    # Zone 7 — Crystal Lake
    [(32, 40, 1), (72, 32, 0), (112, 40, 1), (152, 32, 0),
     (48, 104, 0), (128, 104, 1),
     (88, 64, 2)],             # gift: center area

    # Zone 8 — Sunset Sky
    [(24, 32, 0), (56, 40, 1), (88, 32, 0), (120, 40, 1), (152, 32, 0),
     (40, 104, 1), (88, 104, 0), (136, 104, 1),
     (88, 72, 2)],             # gift: center area
]
