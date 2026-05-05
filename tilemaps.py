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

# ── Zone screens ──────────────────────────────────────────────────────────
def garden_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)
    _score_bar(t, a, "GARDEN")
    _fill_grass(t, a, 1, 18)
    _horizontal_path(t, a, row=9)

    # Tree landmarks anchoring upper and lower zones
    # Upper trees — frame the upper area
    _put(t, a, 2,  2,  TL_TREE_TOP, 3)
    _put(t, a, 2,  3,  TL_TREE_BOT, 3)
    _put(t, a, 17, 2,  TL_TREE_TOP, 3)
    _put(t, a, 17, 3,  TL_TREE_BOT, 3)
    # Lower tree — anchor lower area
    _put(t, a, 10, 15, TL_TREE_TOP, 3)
    _put(t, a, 10, 16, TL_TREE_BOT, 3)

    # Rock wall anchors — frame the path from above and below, create visual "gateway"
    # Left side: upper and lower anchors
    _put(t, a, 0, 7,  TL_ROCK, 4)
    _put(t, a, 0, 8,  TL_ROCK, 4)
    _put(t, a, 0, 11, TL_ROCK, 4)
    _put(t, a, 0, 12, TL_ROCK, 4)
    # Right side: upper and lower anchors
    _put(t, a, 19, 7,  TL_ROCK, 4)
    _put(t, a, 19, 8,  TL_ROCK, 4)
    _put(t, a, 19, 11, TL_ROCK, 4)
    _put(t, a, 19, 12, TL_ROCK, 4)

    # Small rock clusters connecting upper area to path
    # Left side flow down to path
    _put(t, a, 3, 5,  TL_ROCK_SMALL, 4)
    _put(t, a, 3, 6,  TL_ROCK_SMALL, 4)
    _put(t, a, 3, 7,  TL_ROCK, 4)
    # Right side flow down to path
    _put(t, a, 16, 5,  TL_ROCK_SMALL, 4)
    _put(t, a, 16, 6,  TL_ROCK_SMALL, 4)
    _put(t, a, 16, 7,  TL_ROCK, 4)

    # Small rock clusters connecting path to lower area
    # Left side flow from path
    _put(t, a, 3, 12, TL_ROCK, 4)
    _put(t, a, 3, 13, TL_ROCK_SMALL, 4)
    # Right side flow from path
    _put(t, a, 16, 12, TL_ROCK, 4)
    _put(t, a, 16, 13, TL_ROCK_SMALL, 4)

    # Flower beds — create vertical pathways of pink/yellow/purple through the zone
    flowers = [
        # Upper-left corner cluster (above path)
        (4,2,5),(5,2,5),(4,3,6),(5,3,6),
        # Upper-right corner cluster (above path)
        (14,2,7),(15,2,7),(14,3,6),(15,3,5),
        # Upper-center accent (rows 4-5, above path)
        (8,4,5),(9,4,6),(10,4,7),(9,5,5),

        # Path frame flowers — directly adjacent to path (rows 6-7 above, rows 11-12 below)
        # Left side above path
        (5,6,5),(6,7,6),(7,7,5),
        # Right side above path
        (12,6,7),(13,6,5),(13,7,6),
        # Center above path
        (10,6,6),(10,7,7),

        # Left side below path
        (5,12,6),(6,11,5),(7,11,6),
        # Right side below path
        (12,12,5),(13,12,6),(13,11,7),
        # Center below path
        (10,11,7),(10,12,5),

        # Lower-left corner cluster (below path)
        (2,14,5),(3,14,6),(4,14,5),(2,15,7),
        # Lower-right corner cluster (below path)
        (15,14,7),(16,14,6),(17,14,5),(16,15,7),
        # Lower-center cluster (below path)
        (8,16,6),(9,16,5),(10,15,7),(11,16,6),
    ]
    for x, y, p in flowers:
        _put(t, a, x, y, TL_BG_FLOWER, p)

    _put(t, a, 18, 8, TL_ARROW, 2)   # zone-exit hint
    return t, a

def forest_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)
    _score_bar(t, a, "FOREST")
    _fill_grass(t, a, 1, 18)
    # Tree walls at top and bottom edges (every 3 columns)
    for x in range(W):
        if (x + 1) % 3 == 0:
            _put(t, a, x, 1,  TL_TREE_TOP, 3)
            _put(t, a, x, 2,  TL_TREE_BOT, 3)
            _put(t, a, x, 15, TL_TREE_TOP, 3)
            _put(t, a, x, 16, TL_TREE_BOT, 3)
    _horizontal_path(t, a, row=9)
    deco = [
        (2,  5,  TL_MUSHROOM,  5), (5,  4,  TL_MUSHROOM,  5),
        (8,  6,  TL_MUSHROOM,  5), (11, 5,  TL_MUSHROOM,  5),
        (3,  13, TL_MUSHROOM,  5), (7,  13, TL_BG_FLOWER, 6),
        (10, 14, TL_MUSHROOM,  5), (4,  14, TL_BG_FLOWER, 7),
        (14, 4,  TL_BG_FLOWER, 5), (16, 12, TL_MUSHROOM,  5),
    ]
    for x, y, tt, p in deco:
        _put(t, a, x, y, tt, p)
    _put(t, a, 18, 8, TL_ARROW, 2)
    return t, a

def meadow_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)
    _score_bar(t, a, "MEADOW")
    _fill_grass(t, a, 1, 18)
    flowers = [
        (1,3,6),(3,4,5),(5,3,7),(7,4,6),(9,3,5),(11,4,7),
        (2,6,5),(6,6,6),(9,7,7),(12,6,5),(4,12,6),(8,13,7),
        (10,12,5),(13,13,6),(2,14,7),(5,15,5),(8,14,6),(11,15,7),
        (14,4,5),(15,6,7),(17,3,6),(3,16,7),(13,16,5),
    ]
    for x, y, p in flowers:
        _put(t, a, x, y, TL_BG_FLOWER, p)
    _horizontal_path(t, a, row=9)
    _put(t, a, 6,  5,  TL_ROCK,       4)
    _put(t, a, 13, 13, TL_ROCK_SMALL, 4)
    _put(t, a, 17, 15, TL_ROCK_SMALL, 4)
    return t, a

# ── Menu/story screens ────────────────────────────────────────────────────
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

# All 8 screens as (name, function) for build_rom to iterate
ALL_SCREENS = [
    ("garden",  garden_screen),
    ("forest",  forest_screen),
    ("meadow",  meadow_screen),
    ("title",   title_screen),
    ("intro",   intro_screen),
    ("save",    save_screen),
    ("map",     map_screen),
    ("victory", victory_screen),
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
]
