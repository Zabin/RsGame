"""
tilemaps.py — Screen tilemap generators and collectible spawn tables.
Edit screen functions to change zone/menu layouts.
Edit ZONE_COLLECTS to move or add collectibles.
"""
from tiles import *

W, H = 32, 18   # BG map dimensions in tiles

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
    deco = [
        (3,  3,  TL_BG_FLOWER,  5), (6,  5,  TL_BG_FLOWER,  6),
        (10, 4,  TL_BG_FLOWER,  7), (15, 3,  TL_BG_FLOWER,  5),
        (4,  14, TL_ROCK_SMALL, 4), (12, 13, TL_BG_FLOWER,  6),
        (16, 15, TL_BG_FLOWER,  7), (7,  14, TL_BG_FLOWER,  5),
        (2,  5,  TL_ROCK,       4), (17, 13, TL_ROCK_SMALL, 4),
        (13, 15, TL_BG_FLOWER,  6),
    ]
    for x, y, tt, p in deco:
        _put(t, a, x, y, tt, p)
    _put(t, a, 18, 8, TL_ARROW, 2)   # zone-exit hint
    return t, a

def forest_screen():
    t, a = _blank(TL_GRASS_PLAIN, 0)
    _score_bar(t, a, "FOREST")
    _fill_grass(t, a, 1, 18)
    for x in range(W):
        if (x + 1) % 3 == 0:
            _put(t, a, x, 1,  TL_TREE_TOP, 3)
            _put(t, a, x, 2,  TL_TREE_BOT, 3)
            _put(t, a, x, 15, TL_TREE_TOP, 3)
            _put(t, a, x, 16, TL_TREE_BOT, 3)
    _horizontal_path(t, a, row=9)
    deco = [
        (4,  5,  TL_MUSHROOM,  5), (8,  4,  TL_MUSHROOM,  5),
        (12, 6,  TL_MUSHROOM,  5), (15, 5,  TL_MUSHROOM,  5),
        (3,  13, TL_MUSHROOM,  5), (10, 13, TL_BG_FLOWER, 6),
        (14, 14, TL_MUSHROOM,  5), (6,  14, TL_BG_FLOWER, 7),
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
        (2,3,6),(4,4,5),(7,3,7),(10,4,6),(13,3,5),(16,4,7),
        (3,6,5),(8,6,6),(12,7,7),(15,6,5),(5,12,6),(9,13,7),
        (13,12,5),(16,13,6),(3,14,7),(7,15,5),(11,14,6),(14,15,7),
    ]
    for x, y, p in flowers:
        _put(t, a, x, y, TL_BG_FLOWER, p)
    _horizontal_path(t, a, row=9)
    _put(t, a, 6,  5,  TL_ROCK,       4)
    _put(t, a, 14, 13, TL_ROCK_SMALL, 4)
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
