"""
tilemaps.py — Bunny Quest screen layouts and per-zone collectibles.
ALL_SCREENS (IP-1030) is 5 biome-family screen representatives + 5 UI
screens, dispatched at runtime by REGION_GRAPH's generated biome-id.
ZONE_COLLECTS (IP-9070) is now 5 biome-family-representative collectible
lists, indexed by the same biome-id (0=Water 1=Sand 2=Grass 3=Stone
4=Brick) instead of CUR_ZONE directly — the identical representative-zone
choice ALL_SCREENS already made per family (setup_zone_collects reads
REGION_GRAPH's biome-id first, then indexes zc_table by it).
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

# _zone_arrows (build-time, fixed 3x3 rectangle math) retired — IP-1030.
# Region-transition arrows are now drawn at runtime from REGION_GRAPH's
# per-region neighbor data (asm_game.py: draw_region_arrows), since a
# generated world's neighbor structure isn't known until generation runs.

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
    # IP-9080 (BL-0049): the SELECT option (saves and exits to MAIN MENU,
    # st_save's own already-correct behavior, IP-1040) had no on-screen
    # label -- two short lines instead of one, since "SELECT: SAVE+EXIT"
    # doesn't fit the column budget and '+' isn't in the font's char set.
    _str(t, a, 5, 12, "SELECT: SAVE", 2)
    _str(t, a, 5, 13, "AND EXIT", 2)
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

# ── Main menu / new-game flow screens (IP-1040) ────────────
# Both bake only their static labels/borders — the "CONTINUE" row is
# conditionally blanked at runtime if no valid save exists (MM_SAVE_VALID),
# and the digit values + cursor indicator on SEED/SCALE ENTRY are written
# at runtime (asm_game.py: draw_sse_digits) since they change during editing.
def main_menu_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 5, 3, "BUNNY QUEST", 2)
    _str(t, a, 8, 7, "CONTINUE", 2)
    _str(t, a, 8, 9, "NEW GAME", 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 14, TL_BORDER_H, 2)
    return t, a

def seed_scale_entry_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 5, 3, "NEW GAME", 2)
    _str(t, a, 4, 6, "SEED", 2)
    _str(t, a, 4, 10, "SCALE", 2)
    _str(t, a, 4, 14, "A:GO B:BACK", 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 15, TL_BORDER_H, 2)
    return t, a

# ── SELECT menu / edge-indicator legend screens (IP-1090) ──
# select_menu_screen() reuses main_menu_screen()'s own static-screen shape
# (same row/column layout — cursor cell math in asm_game.py's
# sm_on_entry/draw_select_menu_cursor reuses main_menu_screen()'s rows
# 7/9, label start col 8 — directly). legend_screen() bakes GDS-08 §11's
# static content verbatim: the real TL_ARROW_U/TL_BLOCKED_U tiles beside
# their plain-language labels, plus a genuinely blank cell for the
# world-edge case (no new tile art, no new palette entry).
def select_menu_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 5, 3, "BUNNY QUEST", 2)
    _str(t, a, 8, 7, "MAP", 2)
    _str(t, a, 8, 9, "LEGEND", 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 14, TL_BORDER_H, 2)
    return t, a

def legend_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 7, 1, "LEGEND", 2)
    for x in range(2, 18):
        _put(t, a, x, 3, TL_BORDER_H, 2)
    _put(t, a, 4, 6, TL_ARROW_U, 2)
    _str(t, a, 7, 6, "OPEN PATH", 2)
    _put(t, a, 4, 9, TL_BLOCKED_U, 2)
    _str(t, a, 7, 9, "MAZE BLOCKED", 2)
    # Row 12: deliberately no _put() — the real absence of a tile is the
    # point (GDS-08 §11); the pre-blanked background already reads blank.
    _str(t, a, 7, 12, "WORLD EDGE", 2)
    _str(t, a, 6, 15, "B: EXIT", 2)
    return t, a

# ── Mode select / infinite seed entry screens (IP-1100, GDS-01 §4d) ───
# mode_select_screen() reuses select_menu_screen()'s own row/column layout
# (rows 7/9, cursor col 6, label start col 8) — same cursor-menu shape,
# different labels (ms_on_entry/draw_mode_select_cursor in asm_game.py).
# infinite_seed_entry_screen() reuses seed_scale_entry_screen()'s own
# digit-cursor layout primitives (SEED label/row, digit cursor row) minus
# the SCALE row entirely — Infinite Mode has no scale concept (ADR-0016).
def mode_select_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 5, 3, "BUNNY QUEST", 2)
    _str(t, a, 8, 7, "FINITE", 2)
    _str(t, a, 8, 9, "INFINITE", 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 14, TL_BORDER_H, 2)
    return t, a

def infinite_seed_entry_screen():
    t, a = _blank(TL_BG_BLANK, 2)
    _str(t, a, 3, 3, "INFINITE MODE", 2)
    _str(t, a, 4, 6, "SEED", 2)
    _str(t, a, 4, 10, "A:GO B:BACK", 2)
    for x in range(2, 18):
        _put(t, a, x, 2,  TL_BORDER_H, 2)
        _put(t, a, x, 12, TL_BORDER_H, 2)
    return t, a

# All screens (5 biome-family representatives first, then UI screens).
# IP-1030: generalizes from one entry per fixed zone (9) to one entry per
# biome family (5), matching generate_world's Water=0..Brick=4 axis and
# GDS-07's existing terrain-family palette grouping. Representative pick
# per family (IP-1031's to revise; a one-line change, no structural impact):
# water->lake (only zone on that palette), sand->beach, grass->forest,
# stone->mountain, brick->castle (only zone on that palette). village_screen/
# cave_screen/desert_screen/plains_screen are now orphaned (still defined,
# no longer referenced) — same treatment as CARROT_FLAGS's own orphaning.
ALL_SCREENS = [
    ("water", lake_screen),
    ("sand",  beach_screen),
    ("grass", forest_screen),
    ("stone", mountain_screen),
    ("brick", castle_screen),
    ("title",   title_screen),
    ("intro",   intro_screen),
    ("save",    save_screen),
    ("map",     map_screen),
    ("victory", victory_screen),
    ("main_menu",       main_menu_screen),
    ("seed_scale_entry", seed_scale_entry_screen),
    ("select_menu", select_menu_screen),
    ("legend",      legend_screen),
    ("mode_select", mode_select_screen),
    ("infinite_seed_entry", infinite_seed_entry_screen),
]

# ── Collectibles per zone ─────────────────────────────────
# Format: (pixel_x, pixel_y, type)  type: 0=star 1=flower 2=CARROT (the goal)
# Player spawns at (76, 72). Carrot positions chosen for zone variety.
# Pixel space: x∈[8,151], y∈[24,128].
ZONE_COLLECTS = [
    # 0 Water (Lake) — reuses the old Z3 list verbatim
    [(28, 48, 1), (60, 88, 0), (96, 56, 1), (132, 88, 0),
     (40, 112, 1), (120, 112, 0),
     (140, 56, 2)],
    # 1 Sand (Beach) — reuses the old Z0 list verbatim
    [(20, 32, 0), (52, 40, 1), (108, 32, 0), (140, 48, 1),
     (32, 80, 0), (96, 88, 1),
     (132, 88, 2)],
    # 2 Grass (Forest) — reuses the old Z1 list verbatim
    [(28, 40, 1), (64, 32, 0), (120, 40, 1),
     (40, 96, 0), (104, 96, 1), (140, 88, 0),
     (84, 56, 2)],
    # 3 Stone (Mountain) — reuses the old Z2 list verbatim
    [(24, 56, 0), (88, 48, 1), (140, 64, 0),
     (32, 104, 1), (108, 96, 0),
     (60, 88, 2)],
    # 4 Brick (Castle) — reuses the old Z8 list verbatim
    [(20, 56, 0), (52, 88, 1), (140, 56, 0),
     (28, 32, 1), (108, 96, 0),
     (84, 64, 2)],
]
