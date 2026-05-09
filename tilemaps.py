"""
tilemaps.py — Bunny Quest screen layouts and per-zone collectibles.
9 zones in a 3x3 world grid. Index = row*3 + col.

Grid layout:
   col 0      col 1       col 2
  +----------+-----------+----------+
0 | BEACH    | FOREST    | MOUNTAIN |
1 | LAKE     | VILLAGE   | CAVE     |
2 | DESERT   | PLAINS    | CASTLE   |
  +----------+-----------+----------+
"""
from tiles import *

W, H = 32, 18

def _blank(t=TL_BG_BLANK, p=2):
    return bytearray([t] * (W * H)), bytearray([p] * (W * H))

def _put(tiles, attrs, x, y, t, p):
    if 0 <= x < W and 0 <= y < H:
        tiles[y * W + x] = t
        attrs[y * W + x] = p & 7

def _str(tiles, attrs, x, y, s, p=2):
    for i, c in enumerate(s.upper()):
        _put(tiles, attrs, x + i, y, char_to_tile(c), p)

def _fill(tiles, attrs, y0, y1, t, p, alt_t=None, alt_p=None, ratio=10):
    """Fill rows y0..y1 with tile t, sprinkling alt_t every ratio cells."""
    for y in range(y0, y1):
        for x in range(W):
            seed = (y * 7 + x * 13 + 5) % 16
            if alt_t and seed < ratio:
                _put(tiles, attrs, x, y, t, p)
            elif alt_t:
                _put(tiles, attrs, x, y, alt_t, alt_p if alt_p is not None else p)
            else:
                _put(tiles, attrs, x, y, t, p)

def _score_bar(tiles, attrs, zone_name=""):
    for x in range(W):
        _put(tiles, attrs, x, 0, TL_BG_BLANK, 2)
    _put(tiles, attrs, 1, 0, TL_CARROT_ICON, 2)
    _put(tiles, attrs, 2, 0, TL_DIGIT_0, 2)   # carrot count digit (rendered)
    _put(tiles, attrs, 3, 0, char_to_tile('-'), 2)
    _put(tiles, attrs, 4, 0, char_to_tile('9'), 2)
    _put(tiles, attrs, 7, 0, TL_STAR_ICON_BG, 2)
    _put(tiles, attrs, 8, 0,  TL_DIGIT_0, 2)
    _put(tiles, attrs, 9, 0,  TL_DIGIT_0, 2)
    _put(tiles, attrs, 10, 0, TL_DIGIT_0, 2)
    if zone_name:
        _str(tiles, attrs, 12, 0, zone_name, 2)

def _zone_arrows(tiles, attrs, zone):
    """Place edge arrows showing which directions you can travel from zone."""
    row, col = zone // 3, zone % 3
    if col < 2: _put(tiles, attrs, W-2, 9, TL_ARROW_R, 2)
    if col > 0: _put(tiles, attrs, 1,   9, TL_ARROW_L, 2)
    if row > 0: _put(tiles, attrs, 15,  1, TL_ARROW_U, 2)
    if row < 2: _put(tiles, attrs, 15, 16, TL_ARROW_D, 2)

# ── Zone screens ──────────────────────────────────────────
def beach_screen():
    """Z0 — sandy beach with palm trees and waves at the bottom."""
    t, a = _blank(TL_SAND, 1)
    _score_bar(t, a, "BEACH")
    # sand body
    for y in range(1, 13):
        for x in range(W):
            seed = (y * 7 + x * 11 + 3) % 16
            tile = TL_SAND if seed < 10 else TL_SAND_RIPPLE
            _put(t, a, x, y, tile, 1)
    # water at bottom rows 13-17
    for x in range(W):
        _put(t, a, x, 13, TL_WATER_TOP, 3)
    for y in range(14, 18):
        for x in range(W):
            _put(t, a, x, y, TL_WATER_MID, 3)
    # palm trees (palette 6 for fronds, 1 for trunk)
    for px in (4, 14, 24):
        _put(t, a, px, 3, TL_PALM_TOP, 6)
        _put(t, a, px, 4, TL_PALM_BOT, 1)
        _put(t, a, px, 5, TL_PALM_BOT, 1)
    # shells (palette 5 — pink)
    for sx, sy in [(7, 9), (18, 7), (22, 11), (10, 5)]:
        _put(t, a, sx, sy, TL_SHELL, 5)
    _zone_arrows(t, a, 0)
    return t, a

def forest_screen():
    """Z1 — dense forest with trees lining the edges."""
    t, a = _blank(TL_GRASS, 0)
    _score_bar(t, a, "FOREST")
    _fill(t, a, 1, 18, TL_GRASS, 0, TL_GRASS_TUFT, 0, 11)
    # tree wall at rows 1-2 and 15-16
    for x in range(W):
        if x % 3 == 0:
            _put(t, a, x, 1,  TL_TREE_TOP, 6)
            _put(t, a, x, 2,  TL_TREE_BOT, 6)
            _put(t, a, x, 15, TL_TREE_TOP, 6)
            _put(t, a, x, 16, TL_TREE_BOT, 6)
    # mushrooms + log
    for sx, sy in [(5, 5), (10, 7), (16, 6), (22, 8), (8, 12)]:
        _put(t, a, sx, sy, TL_MUSHROOM, 7)
    _put(t, a, 17, 12, TL_LOG, 1)
    _put(t, a, 18, 12, TL_LOG, 1)
    _zone_arrows(t, a, 1)
    return t, a

def mountain_screen():
    """Z2 — snowy mountain with rocky peaks."""
    t, a = _blank(TL_SNOW, 4)
    _score_bar(t, a, "MOUNTAIN")
    # snow ground
    for y in range(1, 18):
        for x in range(W):
            seed = (y * 5 + x * 17 + 1) % 13
            tile = TL_SNOW if seed < 9 else TL_SNOW_BUMP
            _put(t, a, x, y, tile, 4)
    # peaks across the top half (rows 2-5)
    for px in (3, 11, 20, 27):
        _put(t, a, px,   2, TL_PEAK_TOP, 4)
        _put(t, a, px,   3, TL_PEAK_BOT, 4)
        _put(t, a, px,   4, TL_PEAK_BOT, 4)
    # rocks scattered
    for rx, ry in [(7, 6), (14, 7), (24, 11), (5, 12), (19, 13)]:
        _put(t, a, rx, ry, TL_ROCK_BIG, 4)
    # icicles on bottom edge
    for ix in (4, 9, 17, 23, 28):
        _put(t, a, ix, 14, TL_ICICLE, 3)
    _zone_arrows(t, a, 2)
    return t, a

def lake_screen():
    """Z3 — calm lake with reeds, lilies and a pier."""
    t, a = _blank(TL_WATER_DEEP, 3)
    _score_bar(t, a, "LAKE")
    # water everywhere
    for y in range(1, 18):
        for x in range(W):
            seed = (y * 11 + x * 7 + 4) % 17
            tile = TL_WATER_DEEP if seed < 12 else TL_WATER_RIPPLE
            _put(t, a, x, y, tile, 3)
    # grassy banks (palette 0 grass) at top + bottom strip
    for x in range(W):
        _put(t, a, x, 1, TL_GRASS, 0)
        _put(t, a, x, 17, TL_GRASS, 0)
    for x in range(0, W, 4):
        _put(t, a, x, 1, TL_REED, 6)
        _put(t, a, x+2, 17, TL_REED, 6)
    # lilypads scattered
    for lx, ly in [(5, 5), (12, 6), (20, 4), (8, 10), (18, 11), (25, 8), (14, 13)]:
        _put(t, a, lx, ly, TL_LILYPAD, 6)
    # fish
    for fx, fy in [(6, 8), (22, 12), (16, 7)]:
        _put(t, a, fx, fy, TL_FISH, 7)
    # pier sticking down from top
    for py in range(2, 5):
        _put(t, a, 10, py, TL_PIER, 1)
    _zone_arrows(t, a, 3)
    return t, a

def village_screen():
    """Z4 — town square with cobblestone, houses, lanterns."""
    t, a = _blank(TL_COBBLE, 4)
    _score_bar(t, a, "VILLAGE")
    # cobble streets
    for y in range(1, 18):
        for x in range(W):
            tile = TL_COBBLE if (x + y) % 2 == 0 else TL_COBBLE_VAR
            _put(t, a, x, y, tile, 4)
    # houses at top (rows 2-3) and bottom (rows 14-15)
    for hx in (3, 11, 19, 26):
        _put(t, a, hx, 2,  TL_HOUSE_TOP, 5)
        _put(t, a, hx, 3,  TL_HOUSE_BOT, 5)
    for hx in (5, 14, 23):
        _put(t, a, hx, 14, TL_HOUSE_TOP, 5)
        _put(t, a, hx, 15, TL_HOUSE_BOT, 5)
    # lanterns at corners
    for lx, ly in [(1, 7), (1, 11), (29, 7), (29, 11)]:
        _put(t, a, lx, ly, TL_LANTERN, 2)
    # fence segments
    for fx in (8, 17, 24):
        _put(t, a, fx, 6,  TL_FENCE, 1)
        _put(t, a, fx, 12, TL_FENCE, 1)
    _zone_arrows(t, a, 4)
    return t, a

def cave_screen():
    """Z5 — dark cave with crystals and bats."""
    t, a = _blank(TL_CAVE_FLOOR, 4)
    _score_bar(t, a, "CAVE")
    # cave floor with bumps
    for y in range(1, 18):
        for x in range(W):
            seed = (y * 13 + x * 5 + 7) % 18
            tile = TL_CAVE_FLOOR if seed < 14 else TL_CAVE_BUMP
            _put(t, a, x, y, tile, 4)
    # cave walls top + bottom
    for x in range(W):
        _put(t, a, x, 1,  TL_CAVE_WALL, 4)
        _put(t, a, x, 17, TL_CAVE_WALL, 4)
    # crystals
    for cx, cy in [(5, 4), (13, 6), (22, 5), (28, 9), (8, 11), (17, 13), (25, 14)]:
        _put(t, a, cx, cy, TL_CRYSTAL, 7)
    # drips + bats
    for dx in (7, 16, 24):
        _put(t, a, dx, 2, TL_DRIP, 3)
    _put(t, a, 11, 3, TL_BAT, 4)
    _put(t, a, 20, 4, TL_BAT, 4)
    _zone_arrows(t, a, 5)
    return t, a

def desert_screen():
    """Z6 — orange desert with dunes, cactus and a pyramid."""
    t, a = _blank(TL_DUNE, 1)
    _score_bar(t, a, "DESERT")
    for y in range(1, 18):
        for x in range(W):
            seed = (y * 19 + x * 11 + 9) % 17
            tile = TL_DUNE if seed < 12 else TL_DUNE_BUMP
            _put(t, a, x, y, tile, 1)
    # cacti
    for cx in (4, 12, 19, 27):
        _put(t, a, cx, 5, TL_CACTUS_TOP, 6)
        _put(t, a, cx, 6, TL_CACTUS_BOT, 6)
        _put(t, a, cx, 12, TL_CACTUS_TOP, 6)
        _put(t, a, cx, 13, TL_CACTUS_BOT, 6)
    # bones + pyramid centerpiece
    for bx, by in [(7, 9), (16, 11), (23, 8), (10, 14)]:
        _put(t, a, bx, by, TL_BONES, 4)
    _put(t, a, 14, 8, TL_PYRAMID, 1)
    _put(t, a, 22, 4, TL_PYRAMID, 1)
    _zone_arrows(t, a, 6)
    return t, a

def plains_screen():
    """Z7 — bright plains full of wildflowers."""
    t, a = _blank(TL_PLAIN_GRASS, 0)
    _score_bar(t, a, "PLAINS")
    for y in range(1, 18):
        for x in range(W):
            seed = (y * 23 + x * 7 + 2) % 16
            tile = TL_PLAIN_GRASS if seed < 11 else TL_GRASS_TUFT
            _put(t, a, x, y, tile, 0)
    # mass of flowers in patterned bands
    flowers = [
        (3, 4, TL_FLOWER_RED, 5), (8, 3, TL_FLOWER_YEL, 2), (13, 4, TL_FLOWER_BLUE, 3),
        (18, 3, TL_FLOWER_RED, 5), (23, 4, TL_FLOWER_YEL, 2), (28, 3, TL_FLOWER_BLUE, 3),
        (5, 7, TL_FLOWER_BLUE, 3), (11, 8, TL_FLOWER_RED, 5), (17, 7, TL_FLOWER_YEL, 2),
        (24, 8, TL_FLOWER_RED, 5), (29, 7, TL_FLOWER_BLUE, 3),
        (3, 12, TL_FLOWER_YEL, 2), (9, 13, TL_FLOWER_BLUE, 3), (15, 12, TL_FLOWER_RED, 5),
        (21, 13, TL_FLOWER_YEL, 2), (27, 12, TL_FLOWER_BLUE, 3),
        (6, 15, TL_FLOWER_RED, 5), (14, 16, TL_FLOWER_YEL, 2), (22, 15, TL_FLOWER_BLUE, 3),
    ]
    for x, y, tt, p in flowers:
        _put(t, a, x, y, tt, p)
    # tall grass + butterflies
    for tx in (4, 16, 25):
        _put(t, a, tx, 10, TL_TALL_GRASS, 0)
    for bx, by in [(10, 5), (20, 9), (7, 14)]:
        _put(t, a, bx, by, TL_BUTTERFLY, 7)
    _zone_arrows(t, a, 7)
    return t, a

def castle_screen():
    """Z8 — royal castle with banners and torches."""
    t, a = _blank(TL_CASTLE_BRICK, 5)
    _score_bar(t, a, "CASTLE")
    for y in range(1, 18):
        for x in range(W):
            tile = TL_CASTLE_BRICK if (x + y) % 4 != 0 else TL_CASTLE_GOLD
            _put(t, a, x, y, tile, 5 if tile == TL_CASTLE_BRICK else 2)
    # banners on the walls
    for bx in (4, 13, 22, 28):
        _put(t, a, bx, 2, TL_BANNER_TOP, 7)
        _put(t, a, bx, 3, TL_BANNER_BOT, 7)
    # torches
    for tx in (2, 10, 19, 27):
        _put(t, a, tx, 8,  TL_TORCH, 2)
        _put(t, a, tx, 13, TL_TORCH, 2)
    # central gate
    for gx in (14, 15, 16):
        _put(t, a, gx, 14, TL_GATE, 1)
        _put(t, a, gx, 15, TL_GATE, 1)
    _zone_arrows(t, a, 8)
    return t, a

# ── Menu/story screens ────────────────────────────────────
def title_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    for s, y in [("BUNNY QUEST", 4), ("3X3 ADVENTURE", 6),
                 ("PRESS START", 11), ("BY CLAUDE", 16)]:
        _str(t, a, (20 - len(s)) // 2, y, s, 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 14, TL_BORDER_H, 2)
    _put(t, a, 3,  8, TL_FLOWER_OBJ, 5)
    _put(t, a, 16, 8, TL_FLOWER_OBJ, 7)
    _put(t, a, 4,  9, TL_CARROT_ICON, 2)
    _put(t, a, 15, 9, TL_CARROT_ICON, 2)
    return t, a

def intro_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    lines = ["NINE CARROTS", "ARE HIDDEN", "ACROSS NINE", "LANDS!", "",
             "FIND THEM ALL", "AND SAVE", "THE GARDEN!", "",
             "PRESS A"]
    for i, ln in enumerate(lines):
        _str(t, a, (20 - len(ln)) // 2, 3 + i, ln, 2)
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
    """3x3 map: hearts at 9 grid positions show which carrots are collected."""
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 5, 1, "WORLD MAP", 2)
    for x in range(2, 18):
        _put(t, a, x, 3, TL_BORDER_H, 2)
    # Map cells are 5 wide × 3 tall. Anchor at col 3, row 4.
    cell_x0, cell_y0, cw, ch = 3, 5, 5, 3
    labels = ["BCH", "FOR", "MTN",
              "LAK", "VIL", "CAV",
              "DES", "PLN", "CTL"]
    # The HEARTS are placed in a known grid so the assembly loop can update them.
    for r in range(3):
        for c in range(3):
            cx = cell_x0 + c * cw
            cy = cell_y0 + r * ch
            _str(t, a, cx, cy, labels[r * 3 + c], 2)
            _put(t, a, cx + 3, cy + 1, TL_HEART_EMPTY, 2)
    for x in range(2, 18):
        _put(t, a, x, 14, TL_BORDER_H, 2)
    _str(t, a, 1, 15, "DPAD: WALK",  2)
    _str(t, a, 1, 16, "B: EXIT MAP", 2)
    return t, a

def victory_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    lines = ["ALL NINE!", "", "THE GARDEN", "IS SAVED!", "",
             "BUNNY HERO!", "", "PRESS A"]
    for i, ln in enumerate(lines):
        _str(t, a, (20 - len(ln)) // 2, 3 + i, ln, 2)
    for x, y, p in [(3,14,5),(6,15,2),(9,14,7),(12,15,3),(15,14,5)]:
        _put(t, a, x, y, TL_FLOWER_OBJ, p)
    return t, a

# All screens (zones first 0..8, then UI screens)
ALL_SCREENS = [
    ("z0", beach_screen),
    ("z1", forest_screen),
    ("z2", mountain_screen),
    ("z3", lake_screen),
    ("z4", village_screen),
    ("z5", cave_screen),
    ("z6", desert_screen),
    ("z7", plains_screen),
    ("z8", castle_screen),
    ("title",   title_screen),
    ("intro",   intro_screen),
    ("save",    save_screen),
    ("map",     map_screen),
    ("victory", victory_screen),
]

# ── Collectibles per zone ─────────────────────────────────
# Format: (pixel_x, pixel_y, type)  type: 0=star 1=flower 2=CARROT (the goal)
# Player spawns at (76, 72). Carrot positions chosen for zone variety.
# Pixel space: x∈[8,151], y∈[24,128].
ZONE_COLLECTS = [
    # Z0 Beach
    [(20, 32, 0), (52, 40, 1), (108, 32, 0), (140, 48, 1),
     (32, 80, 0), (96, 88, 1),
     (132, 88, 2)],
    # Z1 Forest
    [(28, 40, 1), (64, 32, 0), (120, 40, 1),
     (40, 96, 0), (104, 96, 1), (140, 88, 0),
     (84, 56, 2)],
    # Z2 Mountain
    [(24, 56, 0), (88, 48, 1), (140, 64, 0),
     (32, 104, 1), (108, 96, 0),
     (60, 88, 2)],
    # Z3 Lake
    [(28, 48, 1), (60, 88, 0), (96, 56, 1), (132, 88, 0),
     (40, 112, 1), (120, 112, 0),
     (140, 56, 2)],
    # Z4 Village
    [(32, 64, 0), (52, 96, 1), (108, 56, 0), (132, 96, 1),
     (24, 32, 0), (140, 120, 1),
     (88, 88, 2)],
    # Z5 Cave
    [(28, 56, 1), (88, 48, 0), (140, 72, 1),
     (40, 104, 0), (108, 112, 1), (60, 88, 0),
     (132, 32, 2)],
    # Z6 Desert
    [(28, 80, 0), (60, 32, 1), (96, 80, 0), (132, 32, 1),
     (40, 112, 0), (108, 112, 1),
     (140, 88, 2)],
    # Z7 Plains
    [(28, 40, 0), (60, 56, 1), (88, 32, 2),  # carrot here
     (132, 56, 1), (28, 96, 0), (60, 112, 1),
     (108, 88, 0), (140, 112, 1)],
    # Z8 Castle
    [(20, 56, 0), (52, 88, 1), (140, 56, 0),
     (28, 32, 1), (108, 96, 0),
     (84, 64, 2)],
]
