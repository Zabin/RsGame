#!/usr/bin/env python3
"""
build_rom.py — Master build script for Bunny Quest GBC ROM.

Wires together:
  tiles.py    → tile graphics
  tilemaps.py → 9-zone screen layouts + collectible positions
  music.py    → music data
  asm_game.py → game logic (SM83 assembly) for 3x3 grid

Output: BunnyQuest.gbc
"""
import os, sys
from gbc_lib import ROM, rgb15
from tiles    import build_tile_data
from tilemaps import ALL_SCREENS, ZONE_COLLECTS
from music    import music_data
from asm_game import build_game_asm

def _c(r,g,b): return rgb15(r,g,b)

# ── BG palette colors ──────────────────────────────────────
# Pal 0: lush grass (sky / lite-green / mid-green / dark-green)
SKY      = _c(28,30,26); G_LITE = _c(18,28,12); G_MID = _c(10,22, 6); G_DARK = _c( 4,14, 4)
# Pal 1: sand/dirt (sky / pale-sand / sand / brown)
S_LITE   = _c(31,28,18); S_MID  = _c(28,21, 8); S_DARK = _c(20,12, 2)
# Pal 2: UI dark-purple / white / lite-yellow / gold
UI_BG    = _c( 4, 2,12); UI_W   = _c(31,31,31); UI_YL = _c(31,30,12); UI_GD = _c(28,20, 0)
# Pal 3: water (sky / lite-blue / blue / navy)
W_LITE   = _c(20,28,31); W_MID  = _c( 8,16,28); W_DARK = _c( 2, 6,16)
# Pal 4: stone/cave (light-gray / gray / dark-gray / near-black)
R_LITE   = _c(24,24,26); R_MID  = _c(14,14,18); R_DARK = _c( 6, 6,10)
# Pal 5: brick/red (lite-pink / red / dark-red / near-black)
B_LITE   = _c(31,18,16); B_MID  = _c(24, 6, 8); B_DARK = _c(14, 2, 4)
# Pal 6: tree/leaf (lite-green / green / dark-green / brown)
T_LITE   = _c(14,24, 8); T_MID  = _c( 6,18, 4); T_DARK = _c( 8, 6, 2)
# Pal 7: accent purple/magenta (lite / magenta / purple / dark)
P_LITE   = _c(26,18,30); P_MID  = _c(18, 6,24); P_DARK = _c(10, 2,16)

WHITE = _c(31,31,31); BLACK = _c(0,0,0)

# OBJ palette colors
OB_LITE_PNK = _c(31,22,26); OB_HOT_PNK = _c(28, 4,16)
OB_LITE_YEL = _c(31,30,12); OB_GOLD    = _c(28,18, 0)
OB_LITE_PUR = _c(28,18,30); OB_PURPLE  = _c(16, 4,24)
OB_LITE_ORG = _c(31,22,12); OB_ORANGE  = _c(28,12, 4); OB_LEAF = _c( 8,18, 2)

BG_PALETTES = [
    [SKY,    G_LITE, G_MID,  G_DARK],   # 0 grass
    [SKY,    S_LITE, S_MID,  S_DARK],   # 1 sand/dirt
    [UI_BG,  UI_W,   UI_YL,  UI_GD ],   # 2 UI / gold
    [SKY,    W_LITE, W_MID,  W_DARK],   # 3 water
    [SKY,    R_LITE, R_MID,  R_DARK],   # 4 stone
    [SKY,    B_LITE, B_MID,  B_DARK],   # 5 brick / red
    [SKY,    T_LITE, T_MID,  T_DARK],   # 6 tree / leaf
    [SKY,    P_LITE, P_MID,  P_DARK],   # 7 accent purple
]
OBJ_PALETTES = [
    [BLACK, WHITE,       OB_LITE_PNK, OB_HOT_PNK ],   # 0 bunny
    [BLACK, OB_LITE_YEL, OB_GOLD,     OB_PURPLE  ],   # 1 star
    [BLACK, OB_LITE_PNK, OB_HOT_PNK,  OB_PURPLE  ],   # 2 flower
    [BLACK, OB_LITE_ORG, OB_ORANGE,   OB_LEAF    ],   # 3 carrot
    [BLACK, WHITE,       OB_LITE_PNK, OB_HOT_PNK ],   # 4 unused / cursor
    [BLACK, WHITE,       WHITE,       WHITE      ],
    [BLACK, WHITE,       WHITE,       WHITE      ],
    [BLACK, WHITE,       WHITE,       WHITE      ],
]

def _pal_bytes(pals):
    out = []
    for p in pals:
        for c in p:
            out.append(c & 0xFF); out.append((c >> 8) & 0xFF)
    return bytes(out)

# ── Build ──────────────────────────────────────────────────
def build(out_path='BunnyQuest.gbc'):
    rom = ROM(32768)

    patches = build_game_asm(rom)

    # Pad code to next 0x100 boundary
    while rom.pos % 0x100:
        rom.emit(0)
    print(f"Code end:     0x{rom.pos:04X}")

    # Tile data
    tile_addr = rom.pos
    for b in build_tile_data(): rom.emit(b)

    # Palettes
    bg_pal_addr  = rom.pos
    for b in _pal_bytes(BG_PALETTES):  rom.emit(b)
    obj_pal_addr = rom.pos
    for b in _pal_bytes(OBJ_PALETTES): rom.emit(b)

    # Music
    music_addr = rom.pos
    for b in music_data(): rom.emit(b)

    # Screens (5 biome-family representatives first, then UI) — IP-1030
    # generalizes this from a fixed 9-zone list to ALL_SCREENS's new shape.
    screen_addrs = {}
    for name, fn in ALL_SCREENS:
        tiles, attrs = fn()
        t_addr = rom.pos
        for b in tiles: rom.emit(b)
        a_addr = rom.pos
        for b in attrs: rom.emit(b)
        screen_addrs[name] = (t_addr, a_addr)
        print(f"  {name:8s}: T=0x{t_addr:04X} A=0x{a_addr:04X}")

    # (zs_table retired — IP-1030. The 9-entry per-zone lookup table is
    # replaced by 5 named per-biome-family patch pairs below, parallel to
    # the existing title_t/title_a pattern; dispatched at runtime by
    # REGION_GRAPH's generated biome-id, not a fixed CUR_ZONE*4 index.)

    # Zone collectibles tables
    zone_data_addrs = []
    for clist in ZONE_COLLECTS:
        addr = rom.pos
        rom.emit(len(clist))
        for (x, y, t) in clist:
            rom.emit(x, y, t, 0)
        zone_data_addrs.append(addr)

    zc_table_addr = rom.pos
    for a in zone_data_addrs:
        rom.emit(a & 0xFF, (a >> 8) & 0xFF)

    total = rom.pos
    print(f"Total used:   0x{total:04X} ({total} bytes of 32768)")

    # Patch addresses
    def p16(pos, v):
        rom.data[pos]   = v & 0xFF
        rom.data[pos+1] = (v >> 8) & 0xFF

    p16(patches['tile_src'], tile_addr)
    p16(patches['bg_pal'],   bg_pal_addr)
    p16(patches['obj_pal'],  obj_pal_addr)
    rom.data[patches['mus_lo']] = music_addr & 0xFF
    rom.data[patches['mus_hi']] = (music_addr >> 8) & 0xFF
    p16(patches['mus_reset'],   music_addr)

    p16(patches['title_t'], screen_addrs['title'][0])
    p16(patches['title_a'], screen_addrs['title'][1])
    p16(patches['intro_t'], screen_addrs['intro'][0])
    p16(patches['intro_a'], screen_addrs['intro'][1])
    p16(patches['save_t'],  screen_addrs['save'][0])
    p16(patches['save_a'],  screen_addrs['save'][1])
    p16(patches['map_t'],   screen_addrs['map'][0])
    p16(patches['map_a'],   screen_addrs['map'][1])
    p16(patches['vic_t'],   screen_addrs['victory'][0])
    p16(patches['vic_a'],   screen_addrs['victory'][1])

    # IP-1030: one tile/attr address pair per biome family (5), parallel
    # to the title_t/title_a pattern above — not one pair per region.
    p16(patches['water_t'], screen_addrs['water'][0])
    p16(patches['water_a'], screen_addrs['water'][1])
    p16(patches['sand_t'],  screen_addrs['sand'][0])
    p16(patches['sand_a'],  screen_addrs['sand'][1])
    p16(patches['grass_t'], screen_addrs['grass'][0])
    p16(patches['grass_a'], screen_addrs['grass'][1])
    p16(patches['stone_t'], screen_addrs['stone'][0])
    p16(patches['stone_a'], screen_addrs['stone'][1])
    p16(patches['brick_t'], screen_addrs['brick'][0])
    p16(patches['brick_a'], screen_addrs['brick'][1])

    p16(patches['zc_table'], zc_table_addr)

    rom.resolve()
    rom.set_header("BUNNYQUEST", cart=0x03, rsize=0x00, ramsize=0x02)

    with open(out_path, 'wb') as f:
        f.write(rom.data)
    print(f"Wrote {len(rom.data)} bytes → {out_path}")
    return rom


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'BunnyQuest.gbc'
    build(out)
