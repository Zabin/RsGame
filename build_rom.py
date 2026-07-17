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
from tilemaps import (ALL_SCREENS, ZONE_COLLECTS,
                      VILLAGE_FILL, CAVE_FILL, DESERT_FILL, PLAINS_FILL,
                      VILLAGE_LANDMARKS, CAVE_LANDMARKS, DESERT_LANDMARKS, PLAINS_LANDMARKS)
from music    import music_data, generate_theme_variations
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

    # Music -- IP-1110: nine biome-family sub-themes, one per FR-4320's
    # own biome-family identity, emitted in that FR's own biome-id order
    # (0=Water..8=Plains) so the address table below is directly
    # indexable by biome-id, mirroring ZONE_COLLECTS/zc_table's own
    # established convention. Grass is the zero-transform anchor (IP-1110
    # Objective) -- its own track *is* the main theme's existing
    # music_data() output, unchanged; the other eight are generated via
    # generate_theme_variations(). mus_lo/mus_hi/mus_reset below continue
    # to point at Grass's own address exactly as they pointed at the
    # single main theme before this package -- existing single-track
    # playback is completely unaffected until a future package (IP-1111)
    # adds runtime selection logic.
    #
    # Deviation from this package's own planning text: IP-1110's own
    # scope explicitly excludes asm_game.py changes, but a named
    # per-identity patch-key pair (the originally-planned interface,
    # mirroring mus_lo/mus_hi) can only be created where the
    # corresponding LD_A_n(0) placeholder is emitted -- i.e. in
    # asm_game.py, contradicting that scope boundary. Uses this package's
    # own already-named fallback instead (a flat ROM-resident address
    # table, mirroring zc_table's own precedent) -- zero asm_game.py
    # involvement, fully within this package's declared scope. See this
    # package's own Master Build Plan entry for the full reasoning; a
    # future 07-implementation-planning pass should update IP-1111's own
    # §5/§6 text to consume this table by biome-id index rather than the
    # originally-planned named-key scheme.
    _MUSIC_IDENTITY_ORDER = ['water', 'sand', 'grass', 'stone', 'brick',
                             'village', 'cave', 'desert', 'plains']
    _music_sub_themes = generate_theme_variations()
    music_addrs = {}
    for _identity in _MUSIC_IDENTITY_ORDER:
        _addr = rom.pos
        _data = music_data() if _identity == 'grass' else _music_sub_themes[_identity]
        for b in _data: rom.emit(b)
        music_addrs[_identity] = _addr
        print(f"  music/{_identity:8s}: 0x{_addr:04X} ({len(_data)} bytes)")
    music_addr = music_addrs['grass']

    music_table_addr = rom.pos
    for _identity in _MUSIC_IDENTITY_ORDER:
        _a = music_addrs[_identity]
        rom.emit(_a & 0xFF, (_a >> 8) & 0xFF)
    print(f"  music_table  : 0x{music_table_addr:04X} (18 bytes, biome-id order 0-8)")

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

    # IP-1022 (ADR-0020): procedural-fill parameter blocks + landmark-
    # overlay lists for the four newly-folded biome identities — see
    # tilemaps.py's own *_FILL/*_LANDMARKS comment block for the format.
    fill_addrs = {}
    for name, fill in [('village', VILLAGE_FILL), ('cave', CAVE_FILL),
                        ('desert', DESERT_FILL), ('plains', PLAINS_FILL)]:
        mult_x, modulus, threshold, tile_a, tile_b, attr, wall_tile, row_table = fill
        addr = rom.pos
        rom.emit(mult_x, modulus, threshold, tile_a, tile_b, attr, wall_tile)
        for b in row_table: rom.emit(b)
        fill_addrs[name] = addr

    landmark_addrs = {}
    for name, lm in [('village', VILLAGE_LANDMARKS), ('cave', CAVE_LANDMARKS),
                      ('desert', DESERT_LANDMARKS), ('plains', PLAINS_LANDMARKS)]:
        addr = rom.pos
        rom.emit(len(lm))
        for (x, y, t, a) in lm:
            rom.emit(x, y, t, a)
        landmark_addrs[name] = addr

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

    # IP-1040: main menu + seed/scale entry screens, same title_t/title_a pattern.
    p16(patches['mm_t'],  screen_addrs['main_menu'][0])
    p16(patches['mm_a'],  screen_addrs['main_menu'][1])
    p16(patches['sse_t'], screen_addrs['seed_scale_entry'][0])
    p16(patches['sse_a'], screen_addrs['seed_scale_entry'][1])

    # IP-1090: select menu + legend screens, same title_t/title_a pattern.
    p16(patches['sm_t'], screen_addrs['select_menu'][0])
    p16(patches['sm_a'], screen_addrs['select_menu'][1])
    p16(patches['lg_t'], screen_addrs['legend'][0])
    p16(patches['lg_a'], screen_addrs['legend'][1])

    # IP-1100: mode select + infinite seed entry screens, same title_t/title_a pattern.
    p16(patches['ms_t'],  screen_addrs['mode_select'][0])
    p16(patches['ms_a'],  screen_addrs['mode_select'][1])
    p16(patches['ise_t'], screen_addrs['infinite_seed_entry'][0])
    p16(patches['ise_a'], screen_addrs['infinite_seed_entry'][1])

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

    # IP-1022 (ADR-0020): fill-parameter-block + landmark-list addresses
    # for the four newly-folded identities — no baked screen_addrs entry
    # (they are not in ALL_SCREENS), a fill/landmark pointer pair instead.
    p16(patches['village_fill'], fill_addrs['village'])
    p16(patches['village_lm'],   landmark_addrs['village'])
    p16(patches['cave_fill'],    fill_addrs['cave'])
    p16(patches['cave_lm'],      landmark_addrs['cave'])
    p16(patches['desert_fill'],  fill_addrs['desert'])
    p16(patches['desert_lm'],    landmark_addrs['desert'])
    p16(patches['plains_fill'],  fill_addrs['plains'])
    p16(patches['plains_lm'],    landmark_addrs['plains'])

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
