#!/usr/bin/env python3
"""
build_rom.py — Master build script for Bunny Garden Adventure GBC ROM.

Edit OTHER files to change content:
  tiles.py    → tile graphics
  tilemaps.py → screen layouts + collectible positions
  music.py    → music data
  asm_game.py → game logic (SM83 assembly)
  gbc_lib.py  → ROM assembler class (rarely needs editing)

This file only:
  1. Creates the ROM object
  2. Calls build_game_asm() to emit code
  3. Appends all data sections
  4. Patches in the addresses
  5. Writes the .gbc file
"""

import sys
from gbc_lib import ROM, rgb15
from tiles   import build_tile_data
from tilemaps import ALL_SCREENS, ZONE_COLLECTS
from music   import music_data
from asm_game import build_game_asm

# ── Palette definitions (edit colors here) ──────────────────────────────
def _c(r,g,b): return rgb15(r,g,b)

# Natural greens / browns / grays / snow
SKY        = _c(28,30,26); GRASS_L = _c(18,26,12); GRASS_M = _c(12,21, 8); GRASS_D = _c( 6,14, 4)
DIRT_L     = _c(26,19,11); DIRT_M  = _c(20,13, 6); DIRT_D  = _c(13, 8, 3)
ROCK_L     = _c(22,22,24); ROCK_M  = _c(15,15,17); ROCK_D  = _c( 9, 9,11)
TREE_L     = _c( 9,17, 7); TREE_M  = _c( 5,12, 4); TREE_D  = _c( 2, 7, 2)
# Snow palette (white/light-blue/mid-blue/dark-blue)
SNOW_W     = _c(31,31,30); SNOW_L   = _c(26,28,31); SNOW_M  = _c(18,22,28); SNOW_D  = _c(10,14,20)
# Crystal Lake palette (white/light-cyan/mid-blue/dark-blue water)
CRYS_W     = _c(31,31,31); CRYS_L   = _c(20,30,31); CRYS_M  = _c(10,20,28); CRYS_D  = _c(4,12,20)
# Sunset Sky palette (white/orange/pink/red warm colors)
SUNS_W     = _c(31,31,31); SUNS_O   = _c(31,24,12); SUNS_P  = _c(31,16,16); SUNS_R  = _c(24,8,4)
# Meadow palette (white/light-green/mid-green/dark-green - open grassland)
MEAD_W     = _c(31,31,31); MEAD_L   = _c(24,28,18); MEAD_M  = _c(16,22,10); MEAD_D  = _c(8,14,4)
# Forest palette (white/dark-green/mid-green/dark-brown - dense woodland)
FORE_W     = _c(31,31,31); FORE_L   = _c(12,18,8); FORE_M  = _c(8,12,4); FORE_D  = _c(12,8,4)
# Desert palette (white/light-tan/mid-tan/dark-tan - sandy dunes)
DESE_W     = _c(31,31,31); DESE_L   = _c(28,24,16); DESE_M  = _c(24,18,10); DESE_D  = _c(18,12,4)
# Accent: pink, yellow, purple
PNK_L      = _c(31,22,26); PNK_M   = _c(28,12,20); PNK_D   = _c(20, 4,12)
YEL_L      = _c(31,30,14); YEL_M   = _c(31,26, 0); YEL_D   = _c(24,16, 0)
PUR_L      = _c(22,14,30); PUR_M   = _c(15, 6,24); PUR_D   = _c( 8, 2,16)
WHITE      = _c(31,31,31); BG_W    = _c(30,30,28); BLACK   = _c( 0, 0, 0)

BG_PALETTES = [
    [SKY,   GRASS_L, GRASS_M, GRASS_D],   # 0 grass
    [SKY,   DIRT_L,  DIRT_M,  DIRT_D ],   # 1 dirt
    [PUR_D, BG_W,    YEL_L,   YEL_M  ],   # 2 UI / text
    [SKY,   TREE_L,  TREE_M,  TREE_D ],   # 3 trees
    [SKY,   ROCK_L,  ROCK_M,  ROCK_D ],   # 4 rocks
    [SNOW_W, SNOW_L, SNOW_M,  SNOW_D ],   # 5 snow peak
    [CRYS_W, CRYS_L, CRYS_M,  CRYS_D ],   # 6 crystal lake
    [SUNS_W, SUNS_O, SUNS_P,  SUNS_R ],   # 7 sunset sky
    [MEAD_W, MEAD_L, MEAD_M,  MEAD_D ],   # 8 meadow
    [FORE_W, FORE_L, FORE_M,  FORE_D ],   # 9 forest
    [DESE_W, DESE_L, DESE_M,  DESE_D ],   # 10 desert
]
OBJ_PALETTES = [
    [BLACK, BG_W,  PNK_L, PNK_D],   # 0 bunny
    [BLACK, YEL_L, YEL_M, YEL_D],   # 1 star
    [BLACK, PNK_L, PNK_M, PNK_D],   # 2 flower
    [BLACK, YEL_L, PUR_M, PUR_D],   # 3 gift
    [BLACK, WHITE, PNK_M, PNK_D],   # 4 cursor (unused)
    [BLACK, WHITE, WHITE, WHITE ],   # 5-7 unused
    [BLACK, WHITE, WHITE, WHITE ],
    [BLACK, WHITE, WHITE, WHITE ],
]

def _pal_bytes(pals):
    out = []
    for p in pals:
        for c in p:
            out.append(c & 0xFF); out.append((c >> 8) & 0xFF)
    return bytes(out)

# ── Build ────────────────────────────────────────────────────────────────
def build(out_path='/mnt/user-data/outputs/BunnyGarden.gbc'):
    rom = ROM(32768)

    # 1. Emit all game code, get patch-point addresses back
    patches = build_game_asm(rom)

    # Pad code section to 0x0800 boundary
    while rom.pos % 0x100:
        rom.emit(0)
    print(f"Code end:     0x{rom.pos:04X}")

    # ── 2. Data sections (order matters for the addresses we patch in) ────

    # Tile data (256 × 16 bytes = 4096)
    tile_addr = rom.pos
    for b in build_tile_data(): rom.emit(b)

    # BG + OBJ palettes
    bg_pal_addr  = rom.pos
    for b in _pal_bytes(BG_PALETTES):  rom.emit(b)
    obj_pal_addr = rom.pos
    for b in _pal_bytes(OBJ_PALETTES): rom.emit(b)

    # Music
    music_addr = rom.pos
    for b in music_data(): rom.emit(b)

    # All screens (tile tilemap + attr tilemap, 576 bytes each)
    screen_addrs = {}
    for name, fn in ALL_SCREENS:
        tiles, attrs = fn()
        t_addr = rom.pos
        for b in tiles: rom.emit(b)
        a_addr = rom.pos
        for b in attrs: rom.emit(b)
        screen_addrs[name] = (t_addr, a_addr)
        print(f"  {name:8s}: T=0x{t_addr:04X} A=0x{a_addr:04X}")

    # Zone collectible tables
    # Each zone: [count, x0,y0,t0,0, x1,y1,t1,0, ...]
    zone_data_addrs = []
    for clist in ZONE_COLLECTS:
        addr = rom.pos
        rom.emit(len(clist))
        for (x, y, t) in clist:
            rom.emit(x, y, t, 0)   # trailing 0 = source "active" placeholder
        zone_data_addrs.append(addr)

    # Zone lookup table: 3 × 2-byte pointers
    zc_table_addr = rom.pos
    for a in zone_data_addrs:
        rom.emit(a & 0xFF, (a >> 8) & 0xFF)

    total = rom.pos
    print(f"Total used:   0x{total:04X} ({total} bytes of 32768)")

    # ROM overflow check
    if total > 32768:
        raise Exception(f"❌ ROM OVERFLOW: {total} bytes exceeds 32KB limit (32768 bytes)")
    headroom = 32768 - total
    print(f"Headroom:     {headroom} bytes available for expansion")

    # ── 3. Patch all addresses into code ─────────────────────────────────
    def p16(pos, v):
        rom.data[pos]   = v & 0xFF
        rom.data[pos+1] = (v >> 8) & 0xFF

    # Validate all patch points exist before patching
    required_patches = [
        'tile_src', 'bg_pal', 'obj_pal', 'mus_lo', 'mus_hi', 'mus_reset',
        'title_t', 'title_a', 'intro_t', 'intro_a', 'save_t', 'save_a',
        'map_t', 'map_a', 'vic_t', 'vic_a', 'gar_t', 'gar_a',
        'for_t', 'for_a', 'mea_t', 'mea_a', 'zc_table'
    ]
    for patch_name in required_patches:
        if patch_name not in patches:
            raise Exception(f"❌ PATCH POINT MISSING: '{patch_name}' not found in game code")

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
    p16(patches['gar_t'],   screen_addrs['garden'][0])
    p16(patches['gar_a'],   screen_addrs['garden'][1])
    p16(patches['for_t'],   screen_addrs['forest'][0])
    p16(patches['for_a'],   screen_addrs['forest'][1])
    p16(patches['mea_t'],   screen_addrs['meadow'][0])
    p16(patches['mea_a'],   screen_addrs['meadow'][1])
    p16(patches['zc_table'], zc_table_addr)

    print("✅ All patch points verified and applied")

    # ── 4. Resolve labels + write header ────────────────────────────────
    rom.resolve()
    rom.set_header("BUNNYGARDEN", cart=0x03, rsize=0x00, ramsize=0x02)

    # ── 5. Write file ────────────────────────────────────────────────────
    with open(out_path, 'wb') as f:
        f.write(rom.data)
    print(f"Wrote {len(rom.data)} bytes → {out_path}")
    return rom


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/outputs/BunnyGarden.gbc'
    build(out)
