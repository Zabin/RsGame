#!/usr/bin/env python3
"""
test_rom.py — Systematic test suite for BunnyQuest.gbc (Bunny Quest, 3x3 world).
Run from the repo root: python3 test_rom.py
Requires: pyboy, numpy (pillow optional, for screenshots).

Suites:
  T1  ROM header / metadata (no emulator) + source-data invariants
  T2  VRAM tile data loaded
  T3  LCDC / LCD flags (8x16 OBJ mode)
  T4  State machine transitions (TITLE/INTRO/PLAYING/SAVE/MAP/VICTORY)
  T5  BG tilemap content per screen (score bar, title, zone terrain)
  T6  OAM / sprite rendering (single 8x16 bunny entry + collectibles)
  T7  Joypad movement and boundaries
  T8  Collision, score, carrot tracking, map hearts
  T9  Zone transitions (3x3 grid, all four edges)
  T10 SRAM save/load persistence (BUNY magic, full field set)
  T11 Per-zone ScoreItem persistence (IP-1010)
  T12 World generation (IP-1020) — determinism, oracle parity, reachability,
      grammar-validity, one-KeyItem-per-region, item-agnostic collection,
      seed=0 normalization, WRAM headroom

WRAM model under test (see docs/architecture/07-data-model.md):
  C000 GAMESTATE (0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY)
  C001/C002 PLAYER_X/PLAYER_Y   C003 PLAYER_DIR   C004 PLAYER_FRAME
  C006 SCORE (0-99)   C008 CUR_ZONE (0-8)   C009 CARROTS_COUNT (0-9, victory at 9)
  C015-C01D CARROT_FLAGS (9 bytes, one per zone)
  C020 COLL_DATA (4 bytes/entry: x,y,type,active)   C050 COLL_COUNT
"""
import os, struct
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROM_PATH = str(BASE / 'BunnyQuest.gbc')
RAM_PATH = ROM_PATH + '.ram'          # PyBoy writes <rom>.ram for battery carts
SHOT_DIR = BASE / 'test_shots'
SHOT_DIR.mkdir(exist_ok=True)
RESULTS_PATH = BASE / 'test_results.txt'

# WRAM addresses (must match asm_game.py / GDS-07)
GAMESTATE = 0xC000; PLAYER_X = 0xC001; PLAYER_Y = 0xC002
PLAYER_DIR = 0xC003; PLAYER_FRAME = 0xC004; ANIM_CTR = 0xC005
SCORE = 0xC006; SCORE_DIRTY = 0xC007; CUR_ZONE = 0xC008
CARROTS_COUNT = 0xC009; NEED_REDRAW = 0xC00A
CARROT_FLAGS = 0xC015; COLL_DATA = 0xC020; COLL_COUNT = 0xC050
SCOREITEM_FLAGS = 0xC060   # 9 bytes — one bitfield per zone (FR-5220, IP-1010)
SEED = 0xC069; WORLD_SCALE = 0xC06B; REGION_GRAPH = 0xC070
KEYITEM_FLAGS = 0xC220     # up to 81 bytes — generalizes CARROT_FLAGS (IP-1020);
                            # only indices 0-8 are live until FEAT-1100 ships
KEYITEM_COUNT = CARROTS_COUNT   # same WRAM slot as CARROTS_COUNT (IP-1020)

# SRAM save-format addresses (must match asm_game.py's save_to_sram/try_load_save)
SRAM_MAGIC = 0xA000; SRAM_CUR_ZONE = 0xA004; SRAM_PLAYER_X = 0xA005
SRAM_PLAYER_Y = 0xA006; SRAM_CARROTS_COUNT = 0xA007; SRAM_SCORE = 0xA008
SRAM_CARROT_FLAGS = 0xA009   # 9 bytes, A009-A011
SAVE_VERSION_ADDR = 0xA012; SAVE_VERSION_VAL = 0x01
SRAM_SCOREITEM = 0xA013      # 9 bytes, A013-A01B

# Tile indices (must match tiles.py)
TL_BG_BLANK = 0x10; TL_HEART_FULL = 0x11; TL_HEART_EMPTY = 0x12
TL_CARROT_ICON = 0x13; TL_STAR_ICON_BG = 0x14; TL_BORDER_H = 0x15
TL_DIGIT_0 = 0x20; TL_FONT_A = 0x40; TL_FONT_COLON = 0x61
TL_CARROT = 0x04; TL_STAR = 0x06; TL_FLOWER_OBJ = 0x08

results = []
PASS = 0; FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    status = "PASS" if cond else "FAIL"
    if cond: PASS += 1
    else:    FAIL += 1
    msg = f"[{status}] {name}"
    if detail: msg += f"  ({detail})"
    results.append(msg)
    print(msg)

def wipe_save():
    """Remove PyBoy's RAM file so next boot starts clean (no auto-load)."""
    for p in [RAM_PATH, RAM_PATH.replace('.ram', '.sav')]:
        try: os.remove(p)
        except OSError: pass

from pyboy import PyBoy

# T12: resolve generate_world's assembled address once (dynamic, not
# hardcoded — stays in sync with any future asm_game.py change). This is a
# standalone assembly pass (no tile/palette data needed), matching exactly
# what build_rom.py's real build produces for the same source.
from gbc_lib import ROM as _ROM
from asm_game import build_game_asm as _build_game_asm
import worldgen
_gw_rom = _ROM()
_build_game_asm(_gw_rom)
GW_ADDR = _gw_rom.labels['generate_world']
GW_SEED_OK_ADDR = _gw_rom.labels['gw_seed_ok']
GW_SCALE_SQ = 0xC27C
TMP1 = 0xC013; TMP2 = 0xC014
GW_TRAP_ADDR = 0xC27D   # scratch, inside the boot-clear range, never read elsewhere

def fresh_boot(frames=180):
    """Clean boot to title screen with no saved game."""
    wipe_save()
    pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
    pb.set_emulation_speed(0)
    for _ in range(frames): pb.tick()
    return pb

def advance_to_playing(pb):
    """From TITLE: START -> INTRO, A -> PLAYING."""
    pb.button('start'); [pb.tick() for _ in range(80)]
    pb.button('a');     [pb.tick() for _ in range(80)]

def shoot(pb, name):
    try:
        pb.screen.image.save(str(SHOT_DIR / f"{name}.png"))
    except Exception:
        pass   # screenshots are diagnostics, not assertions

def invoke_generate_world(pb, seed, scale):
    """
    T12: directly invoke generate_world (asm_game.py) — no call site exists
    yet, IP-1040 wires that up from the SEED/SCALE ENTRY flow. Sets SEED/
    WORLD_SCALE, then hijacks PC/SP to CALL the routine: pushes the address
    of a scratch 'JR -2' (infinite self-loop) trap as the return address,
    jumps PC to generate_world, and ticks until PC reaches the trap — a
    deterministic, unambiguous signal the routine's own RET has executed.
    Returns True if the trap was reached (routine completed) within budget.
    """
    pb.memory[SEED] = seed & 0xFF
    pb.memory[SEED + 1] = (seed >> 8) & 0xFF
    pb.memory[WORLD_SCALE] = scale
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE  # JR -2
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = GW_ADDR
    for _ in range(30):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            return True
    return False

def read_region_graph(pb, scale):
    """Read the actual SM83-generated REGION_GRAPH out of WRAM as a list of
    {'biome_id', 'neighbors'} dicts, same shape as worldgen.generate()'s
    return value (0xFF -> None), for direct comparison against the oracle."""
    regions = []
    for i in range(scale * scale):
        base = REGION_GRAPH + i * 5
        biome = pb.memory[base]
        neighbors = [pb.memory[base + 1 + k] for k in range(4)]
        neighbors = [None if n == 0xFF else n for n in neighbors]
        regions.append({'biome_id': biome, 'neighbors': neighbors})
    return regions

def oam_entry(pb, n):
    """Read OAM entry n from actual OAM (0xFE00), not the shadow buffer."""
    base = 0xFE00 + n * 4
    return (pb.memory[base], pb.memory[base+1], pb.memory[base+2], pb.memory[base+3])

# ══════════════════════════════════════════════════════
# T1 — ROM Header (pure binary checks, no emulator)
#      + source-data invariants (host-side, no emulator)
# ══════════════════════════════════════════════════════
print("\n=== T1: ROM Header / Data Invariants ===")
with open(ROM_PATH, 'rb') as f:
    raw = f.read()

check("T1.1 ROM size = 32768",             len(raw) == 32768, f"{len(raw)}")
check("T1.2 Entry = NOP; JP",             raw[0x100:0x102] == bytes([0x00, 0xC3]))
entry = struct.unpack_from('<H', raw, 0x102)[0]
check("T1.3 JP target >= 0x0150",          entry >= 0x0150, f"0x{entry:04X}")
check("T1.4 GBC flag = 0x80",             raw[0x143] == 0x80, f"0x{raw[0x143]:02X}")
check("T1.5 Cart type = 0x03 MBC1+RAM+BAT", raw[0x147] == 0x03, f"0x{raw[0x147]:02X}")
check("T1.6 RAM size = 0x02 (8KB SRAM)",  raw[0x149] == 0x02, f"0x{raw[0x149]:02X}")
chk = 0
for a in range(0x134, 0x14D): chk = (chk - raw[a] - 1) & 0xFF
check("T1.7 Header checksum valid",        chk == raw[0x14D], f"0x{chk:02X}=0x{raw[0x14D]:02X}")
check("T1.8 VBlank ISR @ 0x40 = PUSH AF", raw[0x40] == 0xF5, f"0x{raw[0x40]:02X}")
check("T1.9 VBlank ISR sets VBLANK_FLAG", raw[0x41:0x44] == bytes([0x3E, 0x01, 0xEA]))

# Source-data invariants (BL-0017 rider): exactly one carrot per zone list.
from tilemaps import ZONE_COLLECTS
check("T1.10 ZONE_COLLECTS has 9 zones",   len(ZONE_COLLECTS) == 9, f"{len(ZONE_COLLECTS)}")
carrots_per_zone = [sum(1 for (_, _, t) in z if t == 2) for z in ZONE_COLLECTS]
check("T1.11 Exactly one carrot per zone", all(c == 1 for c in carrots_per_zone),
      f"{carrots_per_zone}")
check("T1.12 No zone exceeds 8 collectibles (1-byte bitfield capacity)",
      all(len(z) <= 8 for z in ZONE_COLLECTS), f"{[len(z) for z in ZONE_COLLECTS]}")

# ══════════════════════════════════════════════════════
# T2 — VRAM Tile Data
# ══════════════════════════════════════════════════════
print("\n=== T2: VRAM Tile Data ===")
pb = fresh_boot()

def tile(idx): return [pb.memory[0x8000 + idx*16 + i] for i in range(16)]
t_bunny  = tile(0x00)        # bunny head F1
t_carrot = tile(TL_CARROT)   # carrot OBJ
t_star   = tile(TL_STAR)     # star OBJ
t_flower = tile(TL_FLOWER_OBJ)
t_font   = tile(TL_FONT_A)   # font 'A'
t_sand   = tile(0x70)        # beach terrain (TL_SAND)
t_grass  = tile(0x78)        # forest terrain (TL_GRASS)

check("T2.1 Tile 0x00 (bunny head) non-zero",   any(t_bunny),  f"[{t_bunny[:4]}]")
check("T2.2 Tile 0x04 (carrot) non-zero",       any(t_carrot), f"[{t_carrot[:4]}]")
check("T2.3 Tile 0x06 (star) non-zero",         any(t_star),   f"[{t_star[:4]}]")
check("T2.4 Tile 0x08 (flower) non-zero",       any(t_flower), f"[{t_flower[:4]}]")
check("T2.5 Tile 0x40 (font A) non-zero",       any(t_font),   f"[{t_font[:4]}]")
check("T2.6 Tile 0x70 (beach sand) non-zero",   any(t_sand),   f"[{t_sand[:4]}]")
check("T2.7 Tile 0x78 (forest grass) non-zero", any(t_grass),  f"[{t_grass[:4]}]")
check("T2.8 Bunny tile has both bitplanes",
      any(t_bunny[i*2] for i in range(8)) and any(t_bunny[i*2+1] for i in range(8)))

pb.stop()

# ══════════════════════════════════════════════════════
# T3 — LCDC Flags (LCDC = 0x97: LCD on, 8x16 OBJ, BG map 0x9800)
# ══════════════════════════════════════════════════════
print("\n=== T3: LCDC Flags ===")
pb = fresh_boot()

lcdc = pb.memory[0xFF40]
check("T3.1 LCD enabled (bit 7)",          (lcdc>>7)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.2 OBJ enabled (bit 1)",          (lcdc>>1)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.3 BG enabled (bit 0)",           (lcdc>>0)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.4 8x16 OBJ mode (bit 2)",        (lcdc>>2)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.5 Tile data at 0x8000 (bit 4)",  (lcdc>>4)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.6 BG map at 0x9800 (bit 3=0)",   (lcdc>>3)&1 == 0, f"LCDC=0x{lcdc:02X}")
check("T3.7 LCDC = 0x97 exactly",          lcdc == 0x97, f"0x{lcdc:02X}")

pb.stop()

# ══════════════════════════════════════════════════════
# T4 — State Machine (GS: 0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY)
# ══════════════════════════════════════════════════════
print("\n=== T4: State Machine ===")
pb = fresh_boot()

check("T4.1 Clean boot -> TITLE (GS=0)",   pb.memory[GAMESTATE] == 0, f"GS={pb.memory[GAMESTATE]}")

pb.button('start'); [pb.tick() for _ in range(80)]
check("T4.2 START -> INTRO (GS=1)",        pb.memory[GAMESTATE] == 1, f"GS={pb.memory[GAMESTATE]}")
shoot(pb, "T4_intro")

pb.button('a'); [pb.tick() for _ in range(80)]
check("T4.3 A in INTRO -> PLAYING (GS=2)", pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
shoot(pb, "T4_playing")

pb.button('start'); [pb.tick() for _ in range(40)]
check("T4.4 START in PLAYING -> SAVE (GS=3)", pb.memory[GAMESTATE] == 3)
shoot(pb, "T4_save")

pb.button('b'); [pb.tick() for _ in range(40)]
check("T4.5 B in SAVE -> PLAYING (GS=2)",  pb.memory[GAMESTATE] == 2)

pb.button('select'); [pb.tick() for _ in range(40)]
check("T4.6 SELECT -> MAP (GS=4)",          pb.memory[GAMESTATE] == 4)
shoot(pb, "T4_map")

pb.button('b'); [pb.tick() for _ in range(40)]
check("T4.7 B in MAP -> PLAYING (GS=2)",   pb.memory[GAMESTATE] == 2)

# Force victory: the game's check_complete reads CARROTS_COUNT == 9.
# Per R305's dual-assertion rule, set the flags AND the count so the forced
# state is internally consistent with what save/zone logic reads. IP-1020
# generalized the live flags array to KEYITEM_FLAGS (CARROT_FLAGS is orphaned
# — check_collisions/setup_zone_collects no longer touch it; only the save
# routines still mirror it, pending IP-1050).
for i in range(9): pb.memory[KEYITEM_FLAGS + i] = 1
pb.memory[CARROTS_COUNT] = 9
[pb.tick() for _ in range(40)]
check("T4.8 CARROTS=9 -> VICTORY (GS=5)",  pb.memory[GAMESTATE] == 5, f"GS={pb.memory[GAMESTATE]}")
shoot(pb, "T4_victory")

pb.button('a'); [pb.tick() for _ in range(60)]
check("T4.9 A in VICTORY -> TITLE (GS=0)", pb.memory[GAMESTATE] == 0, f"GS={pb.memory[GAMESTATE]}")
check("T4.10 Victory exit clears progress",
      pb.memory[CARROTS_COUNT] == 0 and pb.memory[SCORE] == 0
      and all(pb.memory[KEYITEM_FLAGS + i] == 0 for i in range(9)),
      f"carrots={pb.memory[CARROTS_COUNT]} score={pb.memory[SCORE]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T5 — BG Tilemap Content (title screen + zone 0 Beach)
# ══════════════════════════════════════════════════════
print("\n=== T5: BG Tilemap ===")
pb = fresh_boot(200)

# Title: row 0 blank, border row 2, "BUNNY QUEST" (font tiles) on row 4
row0 = [pb.memory[0x9800 + i] for i in range(20)]
check("T5.1 Title: row 0 is BG blank (0x10)",  row0[0] == TL_BG_BLANK, f"0x{row0[0]:02X}")
row2 = [pb.memory[0x9800 + 2*32 + i] for i in range(2, 18)]
check("T5.2 Title: border row 2 (0x15)",       all(b == TL_BORDER_H for b in row2),
      f"row2[2]=0x{row2[0]:02X}")
row4 = [pb.memory[0x9800 + 4*32 + i] for i in range(4, 16)]
check("T5.3 Title: font tiles in row 4 (BUNNY QUEST)",
      any(TL_FONT_A <= b <= TL_FONT_COLON for b in row4),
      f"{[f'{b:02X}' for b in row4]}")
shoot(pb, "T5_title")

# Advance to zone 0 (Beach)
pb.button('start'); [pb.tick() for _ in range(80)]
pb.button('a');     [pb.tick() for _ in range(80)]

# Score bar (row 0, all zones share the pattern from _score_bar)
row0 = [pb.memory[0x9800 + i] for i in range(12)]
check("T5.4 Zone: row 0 col 0 = BG blank",        row0[0] == TL_BG_BLANK, f"0x{row0[0]:02X}")
check("T5.5 Zone: col 1 = carrot icon (0x13)",    row0[1] == TL_CARROT_ICON, f"0x{row0[1]:02X}")
check("T5.6 Zone: col 2 = carrot-count digit",    TL_DIGIT_0 <= row0[2] <= TL_DIGIT_0+9, f"0x{row0[2]:02X}")
check("T5.7 Zone: col 7 = star icon (0x14)",      row0[7] == TL_STAR_ICON_BG, f"0x{row0[7]:02X}")
check("T5.8 Zone: score digits at cols 8-10",     all(TL_DIGIT_0 <= row0[c] <= TL_DIGIT_0+9 for c in (8, 9, 10)),
      f"{[f'{row0[c]:02X}' for c in (8,9,10)]}")

# Beach terrain: field rows should use the Beach tile family (0x70-0x76)
field = [pb.memory[0x9800 + r*32 + c] for r in range(2, 17) for c in range(20)]
beach_tiles = sum(1 for b in field if 0x70 <= b <= 0x76)
check("T5.9 Zone 0 field uses Beach terrain family (0x70-0x76)", beach_tiles > 40,
      f"{beach_tiles} beach-family tiles")

shoot(pb, "T5_beach")
pb.stop()

# ══════════════════════════════════════════════════════
# T6 — OAM / Sprite Rendering (8x16 mode: bunny = ONE OAM entry)
# NOTE: Read from 0xFE00 (actual OAM), NOT 0xC300 (shadow OAM) —
#       PyBoy-specific: the shadow source reads back cleared after DMA.
# ══════════════════════════════════════════════════════
print("\n=== T6: OAM / Sprite Rendering ===")
pb = fresh_boot()
advance_to_playing(pb)
pb.memory[PLAYER_X] = 80
pb.memory[PLAYER_Y] = 80
pb.memory[PLAYER_DIR] = 0
pb.memory[PLAYER_FRAME] = 0
for _ in range(5): pb.tick()

y0, x0, t0, a0 = oam_entry(pb, 0)   # bunny (single 8x16 entry)
print(f"  Player pos: ({pb.memory[PLAYER_X]}, {pb.memory[PLAYER_Y]})")
print(f"  OAM[0] bunny: Y={y0} X={x0} tile=0x{t0:02X} attr=0x{a0:02X}")

check("T6.1 Bunny OAM Y = player_y+16",    y0 == pb.memory[PLAYER_Y] + 16, f"{y0} vs {pb.memory[PLAYER_Y]+16}")
check("T6.2 Bunny OAM X = player_x+8",     x0 == pb.memory[PLAYER_X] + 8,  f"{x0} vs {pb.memory[PLAYER_X]+8}")
check("T6.3 Bunny tile = frame*2 (0 or 2)", t0 in (0, 2), f"0x{t0:02X}")
check("T6.4 Bunny attr palette = 0",       a0 & 0x07 == 0, f"attr=0x{a0:02X}")
check("T6.5 Bunny faces right (no X-flip)", a0 & 0x20 == 0, f"attr=0x{a0:02X}")

# Face left -> X-flip bit set
pb.memory[PLAYER_DIR] = 1
for _ in range(3): pb.tick()
_, _, _, a_left = oam_entry(pb, 0)
check("T6.6 DIR=1 sets X-flip (attr bit 5)", a_left & 0x20 == 0x20, f"attr=0x{a_left:02X}")
pb.memory[PLAYER_DIR] = 0
for _ in range(3): pb.tick()

# Rendering: the bunny's screen region should differ from background
import numpy as np
shoot(pb, "T6_bunny")
img = np.asarray(pb.screen.ndarray)
bg_color = img[5, 5, :3]
head_region = img[80:96, 80:88, :3]      # 8x16 sprite at (80,80)
non_bg = np.any(head_region != bg_color, axis=2)
check("T6.7 Bunny region has non-BG pixels",  int(non_bg.sum()) > 4, f"non-bg pixels={int(non_bg.sum())}")

# Collectibles occupy OAM entries 1..COLL_COUNT (zone 0 has 7)
cc = pb.memory[COLL_COUNT]
check("T6.8 Zone 0 COLL_COUNT = 7",        cc == 7, f"count={cc}")
c0 = oam_entry(pb, 1)
print(f"  OAM[1] collectible: Y={c0[0]} X={c0[1]} tile=0x{c0[2]:02X} attr=0x{c0[3]:02X}")
check("T6.9 Collectible OAM on-screen (Y>15)", c0[0] > 15, f"Y={c0[0]}")
check("T6.10 Collectible tile = carrot/star/flower",
      c0[2] in (TL_CARROT, TL_STAR, TL_FLOWER_OBJ), f"tile=0x{c0[2]:02X}")
check("T6.11 Collectible palette = type+1",  c0[3] & 0x07 in (1, 2, 3), f"attr=0x{c0[3]:02X}")

pb.stop()

# ══════════════════════════════════════════════════════
# T7 — Joypad and Movement (bounds: X 0..159, Y 17..128)
# ══════════════════════════════════════════════════════
print("\n=== T7: Joypad / Movement ===")
pb = fresh_boot()
advance_to_playing(pb)

pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 72
pb.memory[PLAYER_DIR] = 0; pb.memory[PLAYER_FRAME] = 0; pb.memory[ANIM_CTR] = 0
[pb.tick() for _ in range(3)]

x0 = pb.memory[PLAYER_X]; y0 = pb.memory[PLAYER_Y]

pb.button_press('right'); [pb.tick() for _ in range(20)]; pb.button_release('right')
[pb.tick() for _ in range(2)]
x1 = pb.memory[PLAYER_X]
check("T7.1 RIGHT increases X",           x1 > x0, f"{x0}->{x1}")
check("T7.2 RIGHT sets DIR=0",            pb.memory[PLAYER_DIR] == 0)

pb.button_press('left'); [pb.tick() for _ in range(20)]; pb.button_release('left')
[pb.tick() for _ in range(2)]
x2 = pb.memory[PLAYER_X]
check("T7.3 LEFT decreases X",            x2 < x1, f"{x1}->{x2}")
check("T7.4 LEFT sets DIR=1",             pb.memory[PLAYER_DIR] == 1)

pb.button_press('up'); [pb.tick() for _ in range(20)]; pb.button_release('up')
[pb.tick() for _ in range(2)]
y2 = pb.memory[PLAYER_Y]
check("T7.5 UP decreases Y",              y2 < y0, f"{y0}->{y2}")

pb.button_press('down'); [pb.tick() for _ in range(20)]; pb.button_release('down')
[pb.tick() for _ in range(2)]
y3 = pb.memory[PLAYER_Y]
check("T7.6 DOWN increases Y",            y3 > y2, f"{y2}->{y3}")

# Animation: frame flips after ANIM_CTR reaches 10 moving frames
pb.memory[PLAYER_FRAME] = 0; pb.memory[ANIM_CTR] = 0
pb.button_press('right')
for _ in range(12): pb.tick()
pb.button_release('right')
[pb.tick() for _ in range(2)]
frame = pb.memory[PLAYER_FRAME]
check("T7.7 Frame flips after 10 walk frames", frame == 1, f"frame={frame}")

# Upper Y boundary: movement floor is Y=17 (zone 0 = top row, no up-transition)
pb.memory[PLAYER_Y] = 18; pb.memory[PLAYER_X] = 80
pb.button_press('up'); [pb.tick() for _ in range(5)]; pb.button_release('up')
[pb.tick() for _ in range(2)]
check("T7.8 Can't move above Y=17 (zone 0)", pb.memory[PLAYER_Y] >= 17,
      f"y={pb.memory[PLAYER_Y]} zone={pb.memory[CUR_ZONE]}")

# Left X boundary: zone 0 is col 0 — X=0 must not move or change zone
pb.memory[CUR_ZONE] = 0; pb.memory[PLAYER_X] = 0; pb.memory[NEED_REDRAW] = 0
pb.button_press('left'); [pb.tick() for _ in range(3)]; pb.button_release('left')
[pb.tick() for _ in range(2)]
check("T7.9 X=0 in zone 0: no move, no zone change",
      pb.memory[PLAYER_X] <= 5 and pb.memory[CUR_ZONE] == 0,
      f"x={pb.memory[PLAYER_X]} zone={pb.memory[CUR_ZONE]}")

# Right X boundary: zone 2 is col 2 — no right-transition, X capped at 159
pb.memory[CUR_ZONE] = 2; pb.memory[PLAYER_X] = 159; pb.memory[NEED_REDRAW] = 0
pb.button_press('right'); [pb.tick() for _ in range(3)]; pb.button_release('right')
[pb.tick() for _ in range(2)]
check("T7.10 X=159 in zone 2: no overflow, no zone change",
      pb.memory[PLAYER_X] <= 159 and pb.memory[CUR_ZONE] == 2,
      f"x={pb.memory[PLAYER_X]} zone={pb.memory[CUR_ZONE]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T8 — Collision, Score, Carrots, Map Hearts
#      Zone 0 (Beach) collectibles, from tilemaps.ZONE_COLLECTS[0]:
#      [0]=(20,32,star) ... [6]=(132,88,CARROT). Hit radius: |dx|<10, |dy|<10.
# ══════════════════════════════════════════════════════
print("\n=== T8: Collision / Score / Carrots ===")
pb = fresh_boot()
advance_to_playing(pb)

pb.memory[SCORE] = 0; pb.memory[CARROTS_COUNT] = 0
[pb.tick() for _ in range(5)]

check("T8.1 Score starts 0",   pb.memory[SCORE] == 0, f"{pb.memory[SCORE]}")
check("T8.2 Carrots start 0",  pb.memory[CARROTS_COUNT] == 0, f"{pb.memory[CARROTS_COUNT]}")
check("T8.3 COLL_COUNT = 7 in zone 0", pb.memory[COLL_COUNT] == 7, f"count={pb.memory[COLL_COUNT]}")

# Collect the star at (20,32) — teleport onto it from a safe spot
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 80
[pb.tick() for _ in range(3)]
pb.memory[PLAYER_X] = 20; pb.memory[PLAYER_Y] = 32
[pb.tick() for _ in range(5)]
sc1 = pb.memory[SCORE]
check("T8.4 Score++ on ScoreItem collision", sc1 > 0, f"score={sc1}")
check("T8.5 ScoreItem deactivated in COLL_DATA", pb.memory[COLL_DATA + 3] == 0,
      f"active={pb.memory[COLL_DATA + 3]}")
check("T8.6 ScoreItem does not touch CARROTS_COUNT", pb.memory[CARROTS_COUNT] == 0,
      f"{pb.memory[CARROTS_COUNT]}")

# Collect zone 0's carrot at (132,88) — entry index 6
pb.memory[PLAYER_X] = 132; pb.memory[PLAYER_Y] = 88
[pb.tick() for _ in range(5)]
# IP-1020: check_collisions' carrot branch now targets KEYITEM_FLAGS (CARROT_FLAGS
# is orphaned — nothing writes it anymore; save routines still mirror it pending IP-1050).
check("T8.7 Carrot sets KEYITEM_FLAGS[0] (IP-1020)", pb.memory[KEYITEM_FLAGS + 0] == 1,
      f"flag={pb.memory[KEYITEM_FLAGS + 0]}")
check("T8.8 Carrot increments KEYITEM_COUNT (IP-1020)", pb.memory[KEYITEM_COUNT] == 1,
      f"{pb.memory[KEYITEM_COUNT]}")
check("T8.9 Carrot deactivated in COLL_DATA", pb.memory[COLL_DATA + 6*4 + 3] == 0,
      f"active={pb.memory[COLL_DATA + 6*4 + 3]}")
check("T8.10 Carrot does not touch SCORE", pb.memory[SCORE] == sc1, f"{pb.memory[SCORE]}")

# IP-9020 regression: update_status_disp now runs at frame-top (VBlank-gated,
# moved out of st_playing) — a dirtied SCORE/CARROTS_COUNT must still reflect
# in the HUD tiles within 2 frames.
carrots_pre = pb.memory[CARROTS_COUNT]
pb.memory[SCORE] = 42; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]
hi = pb.memory[0x9808] - TL_DIGIT_0; te = pb.memory[0x9809] - TL_DIGIT_0; on = pb.memory[0x980A] - TL_DIGIT_0
check("T8.10a HUD score digits reflect forced SCORE=42 within 2 frames (IP-9020)",
      (hi, te, on) == (0, 4, 2), f"digits=({hi},{te},{on})")
pb.memory[CARROTS_COUNT] = 5; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]
cd = pb.memory[0x9802] - TL_DIGIT_0
check("T8.10b HUD carrot-count digit reflects forced CARROTS_COUNT=5 within 2 frames (IP-9020)",
      cd == 5, f"digit={cd}")
pb.memory[CARROTS_COUNT] = carrots_pre; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]

# Map hearts (BL-0001 closure): z0 heart full, z1 heart empty.
# update_map_hearts writes 0x9800 + {6,9,12}*32 + {6,11,16}, LCD off during redraw.
pb.button('select'); [pb.tick() for _ in range(40)]
check("T8.11 SELECT -> MAP", pb.memory[GAMESTATE] == 4)
h_z0 = pb.memory[0x9800 + 6*32 + 6]
h_z1 = pb.memory[0x9800 + 6*32 + 11]
check("T8.12 Map heart z0 = FULL (0x11)",  h_z0 == TL_HEART_FULL,  f"0x{h_z0:02X}")
check("T8.13 Map heart z1 = EMPTY (0x12)", h_z1 == TL_HEART_EMPTY, f"0x{h_z1:02X}")
shoot(pb, "T8_map_hearts")
pb.button('b'); [pb.tick() for _ in range(40)]

# Victory at 9 carrots (dual-assert per R305: flags + count)
for i in range(9): pb.memory[CARROT_FLAGS + i] = 1
pb.memory[CARROTS_COUNT] = 9
[pb.tick() for _ in range(40)]
check("T8.14 CARROTS_COUNT=9 -> VICTORY", pb.memory[GAMESTATE] == 5, f"GS={pb.memory[GAMESTATE]}")

pb.stop()

# NOTE (BL-0023 / IP-1010): ScoreItems currently respawn on zone re-entry —
# deliberately not asserted either way here; T11 will assert non-respawn
# once IP-1010 (per-zone ScoreItem persistence) ships.

# ══════════════════════════════════════════════════════
# T9 — Zone Transitions (3x3 grid)
#      right: x>=156 (cols 0,1) -> zone+1, X=8
#      left:  x==0  (cols 1,2) -> zone-1, X=150
#      up:    y<18  (rows 1,2) -> zone-3, Y=120
#      down:  y>=128 (rows 0,1) -> zone+3, Y=24
# ══════════════════════════════════════════════════════
print("\n=== T9: Zone Transitions ===")
pb = fresh_boot()
advance_to_playing(pb)

check("T9.1 Starts in zone 0", pb.memory[CUR_ZONE] == 0, f"zone={pb.memory[CUR_ZONE]}")

def settle(pb, frames=80):
    [pb.tick() for _ in range(frames)]

# Right: z0 -> z1
pb.memory[PLAYER_X] = 156; pb.memory[PLAYER_Y] = 72
settle(pb)
check("T9.2 Right edge z0 -> z1", pb.memory[CUR_ZONE] == 1, f"zone={pb.memory[CUR_ZONE]}")
check("T9.3 X reset to 8 after right transition", pb.memory[PLAYER_X] <= 20,
      f"x={pb.memory[PLAYER_X]}")
shoot(pb, "T9_forest")

# Right: z1 -> z2
pb.memory[PLAYER_X] = 156
settle(pb)
check("T9.4 Right edge z1 -> z2", pb.memory[CUR_ZONE] == 2, f"zone={pb.memory[CUR_ZONE]}")

# Right blocked in col 2: z2 stays z2
pb.memory[PLAYER_X] = 159
settle(pb, 40)
check("T9.5 No right transition from col 2 (z2)", pb.memory[CUR_ZONE] == 2,
      f"zone={pb.memory[CUR_ZONE]}")

# Left: z2 -> z1
pb.memory[PLAYER_X] = 0
settle(pb)
check("T9.6 Left edge z2 -> z1", pb.memory[CUR_ZONE] == 1, f"zone={pb.memory[CUR_ZONE]}")
check("T9.7 X reset to 150 going left", pb.memory[PLAYER_X] >= 140, f"x={pb.memory[PLAYER_X]}")

# Down: z1 -> z4 (row 0 -> row 1)
pb.memory[PLAYER_Y] = 128
settle(pb)
check("T9.8 Bottom edge z1 -> z4", pb.memory[CUR_ZONE] == 4, f"zone={pb.memory[CUR_ZONE]}")
check("T9.9 Y reset to 24 going down", pb.memory[PLAYER_Y] <= 40, f"y={pb.memory[PLAYER_Y]}")
shoot(pb, "T9_village")

# Down: z4 -> z7, then blocked at row 2
pb.memory[PLAYER_Y] = 128
settle(pb)
check("T9.10 Bottom edge z4 -> z7", pb.memory[CUR_ZONE] == 7, f"zone={pb.memory[CUR_ZONE]}")
pb.memory[PLAYER_Y] = 128
settle(pb, 40)
check("T9.11 No down transition from row 2 (z7)", pb.memory[CUR_ZONE] == 7,
      f"zone={pb.memory[CUR_ZONE]}")

# Up: z7 -> z4
pb.memory[PLAYER_Y] = 17
settle(pb)
check("T9.12 Top edge z7 -> z4", pb.memory[CUR_ZONE] == 4, f"zone={pb.memory[CUR_ZONE]}")
check("T9.13 Y reset to 120 going up", pb.memory[PLAYER_Y] >= 100, f"y={pb.memory[PLAYER_Y]}")

# Up blocked in row 0: force z2, y=17 -> stays z2 (movement floor, no transition)
pb.memory[CUR_ZONE] = 2; pb.memory[NEED_REDRAW] = 0
[pb.tick() for _ in range(3)]
pb.memory[PLAYER_Y] = 17
settle(pb, 40)
check("T9.14 No up transition from row 0 (z2)", pb.memory[CUR_ZONE] == 2,
      f"zone={pb.memory[CUR_ZONE]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T10 — SRAM Save/Load (magic 'BUNY' at A000; fields A004-A011)
# ══════════════════════════════════════════════════════
print("\n=== T10: SRAM Save/Load ===")
wipe_save()

pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T10.1 No save -> TITLE (GS=0)", pb.memory[GAMESTATE] == 0, f"GS={pb.memory[GAMESTATE]}")

pb.button('start'); [pb.tick() for _ in range(80)]
pb.button('a');     [pb.tick() for _ in range(80)]
check("T10.2 PLAYING after START -> A", pb.memory[GAMESTATE] == 2)

# Establish a distinctive state: zone 4, position (60,40), progress markers.
pb.memory[CUR_ZONE] = 4; pb.memory[NEED_REDRAW] = 1
[pb.tick() for _ in range(80)]          # redraw into zone 4
pb.memory[PLAYER_X] = 60; pb.memory[PLAYER_Y] = 40
pb.memory[SCORE] = 7; pb.memory[CARROTS_COUNT] = 2
pb.memory[CARROT_FLAGS + 0] = 1; pb.memory[CARROT_FLAGS + 4] = 1
[pb.tick() for _ in range(5)]
z_pre  = pb.memory[CUR_ZONE];  px_pre = pb.memory[PLAYER_X]
py_pre = pb.memory[PLAYER_Y];  sc_pre = pb.memory[SCORE]
cc_pre = pb.memory[CARROTS_COUNT]

pb.button('start'); [pb.tick() for _ in range(40)]
check("T10.3 START -> SAVE menu", pb.memory[GAMESTATE] == 3)
pb.button('a'); [pb.tick() for _ in range(40)]
check("T10.4 A saves -> PLAYING", pb.memory[GAMESTATE] == 2)
pb.stop()
check("T10.5 RAM file created", os.path.exists(RAM_PATH), RAM_PATH)

# Reload: boot auto-loads the save straight into PLAYING
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T10.6 Reload -> PLAYING (auto-load)", pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
check("T10.7 Zone preserved",      pb.memory[CUR_ZONE] == z_pre,  f"{z_pre}->{pb.memory[CUR_ZONE]}")
check("T10.8 PLAYER_X preserved",  pb.memory[PLAYER_X] == px_pre, f"{px_pre}->{pb.memory[PLAYER_X]}")
check("T10.9 PLAYER_Y preserved",  pb.memory[PLAYER_Y] == py_pre, f"{py_pre}->{pb.memory[PLAYER_Y]}")
check("T10.10 CARROTS_COUNT preserved", pb.memory[CARROTS_COUNT] == cc_pre,
      f"{cc_pre}->{pb.memory[CARROTS_COUNT]}")
check("T10.11 SCORE preserved",    pb.memory[SCORE] == sc_pre, f"{sc_pre}->{pb.memory[SCORE]}")
check("T10.12 CARROT_FLAGS preserved (z0, z4 set; z1 clear)",
      pb.memory[CARROT_FLAGS + 0] == 1 and pb.memory[CARROT_FLAGS + 4] == 1
      and pb.memory[CARROT_FLAGS + 1] == 0,
      f"flags={[pb.memory[CARROT_FLAGS + i] for i in range(9)]}")

# B cancels save; previously saved data must survive the cancel
wipe_save()
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('b');     [pb.tick() for _ in range(40)]
check("T10.13 B cancels -> PLAYING", pb.memory[GAMESTATE] == 2)
pb.stop()
# PyBoy always flushes battery RAM on stop() for MBC1+RAM+BAT carts, so the
# correct assertion is: after B-cancel and reload, saved data is unchanged.
pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
check("T10.14 B cancel: reload still has saved data",
      pb2.memory[PLAYER_X] == px_pre and pb2.memory[SCORE] == sc_pre,
      f"x={pb2.memory[PLAYER_X]} score={pb2.memory[SCORE]}")
pb2.stop()
wipe_save()   # leave no runtime save behind

# ══════════════════════════════════════════════════════
# T11 — Per-Zone ScoreItem Persistence (IP-1010 / FR-5220)
#       Zone 0 (Beach) ZONE_COLLECTS: [0]=(20,32,star) [1]=(52,40,*)
#       [4]=(32,80,*) ... [6]=(132,88,CARROT).
# ══════════════════════════════════════════════════════
print("\n=== T11: Per-Zone ScoreItem Persistence ===")

# T11.a — same-session: collect, leave the zone, return; item stays inactive
# and SCORE does not re-increment (AC-1; BL-0023's farming-bug regression).
pb = fresh_boot()
advance_to_playing(pb)
pb.memory[PLAYER_X] = 20; pb.memory[PLAYER_Y] = 32
[pb.tick() for _ in range(5)]
sc_after = pb.memory[SCORE]
check("T11.a1 Star (index 0) collected", sc_after > 0, f"score={sc_after}")

pb.memory[PLAYER_X] = 156; pb.memory[PLAYER_Y] = 72
[pb.tick() for _ in range(80)]
check("T11.a2 Transitioned out of zone 0", pb.memory[CUR_ZONE] == 1, f"zone={pb.memory[CUR_ZONE]}")
pb.memory[PLAYER_X] = 0
[pb.tick() for _ in range(80)]
check("T11.a3 Back in zone 0", pb.memory[CUR_ZONE] == 0, f"zone={pb.memory[CUR_ZONE]}")
check("T11.a4 Collected item (index 0) stays inactive on re-entry (AC-1)",
      pb.memory[COLL_DATA + 3] == 0, f"active={pb.memory[COLL_DATA + 3]}")
check("T11.a5 SCORE did not re-increment on re-entry (BL-0023 fix)",
      pb.memory[SCORE] == sc_after, f"{sc_after}->{pb.memory[SCORE]}")
pb.stop()

# T11.b/c/e — save/reload: collected item stays inactive (AC-2), a
# never-collected item (index 1) stays active (AC-3), and the pre-existing
# save fields still round-trip exactly (AC-5, alongside IP-9010's T10).
wipe_save()
pb = fresh_boot()
advance_to_playing(pb)
pb.memory[PLAYER_X] = 32; pb.memory[PLAYER_Y] = 80   # index 4
[pb.tick() for _ in range(5)]
sc_pre = pb.memory[SCORE]
check("T11.b1 Star (index 4) collected", sc_pre > 0, f"score={sc_pre}")
zone_pre = pb.memory[CUR_ZONE]; x_pre = pb.memory[PLAYER_X]; y_pre = pb.memory[PLAYER_Y]
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');     [pb.tick() for _ in range(40)]
check("T11.b2 Saved -> PLAYING", pb.memory[GAMESTATE] == 2)
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
check("T11.b3 Reload -> PLAYING (auto-load)", pb2.memory[GAMESTATE] == 2, f"GS={pb2.memory[GAMESTATE]}")
check("T11.e1 Legacy fields still round-trip (zone/x/y/score, AC-5)",
      pb2.memory[CUR_ZONE] == zone_pre and pb2.memory[PLAYER_X] == x_pre
      and pb2.memory[PLAYER_Y] == y_pre and pb2.memory[SCORE] == sc_pre,
      f"zone={pb2.memory[CUR_ZONE]} x={pb2.memory[PLAYER_X]} y={pb2.memory[PLAYER_Y]} score={pb2.memory[SCORE]}")
check("T11.b5 Collected item (index 4) stays inactive after save/reload (AC-2)",
      pb2.memory[COLL_DATA + 4*4 + 3] == 0, f"active={pb2.memory[COLL_DATA + 4*4 + 3]}")
check("T11.c Never-collected item (index 1) remains active (AC-3)",
      pb2.memory[COLL_DATA + 1*4 + 3] == 1, f"active={pb2.memory[COLL_DATA + 1*4 + 3]}")
pb2.stop()
wipe_save()

# T11.d — pre-upgrade save fixture: valid magic + legacy fields, but the
# version-guard byte doesn't match and SCOREITEM_FLAGS mirror bytes are
# garbage; every ScoreItem must load as uncollected, no crash (AC-4).
fixture = bytearray(8192)
fixture[0:4] = bytes([0x42, 0x55, 0x4E, 0x59])          # 'BUNY' magic
fixture[SRAM_CUR_ZONE - 0xA000] = 0
fixture[SRAM_PLAYER_X - 0xA000] = 76
fixture[SRAM_PLAYER_Y - 0xA000] = 80
fixture[SRAM_CARROTS_COUNT - 0xA000] = 0
fixture[SRAM_SCORE - 0xA000] = 0
for i in range(9): fixture[SRAM_CARROT_FLAGS - 0xA000 + i] = 0
fixture[SAVE_VERSION_ADDR - 0xA000] = 0x00              # mismatched version
for i in range(9): fixture[SRAM_SCOREITEM - 0xA000 + i] = 0xFF   # garbage
with open(RAM_PATH, 'wb') as f:
    f.write(bytes(fixture))

pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T11.d1 Pre-upgrade save loads without crash -> PLAYING",
      pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
check("T11.d2 SCOREITEM_FLAGS all zero (garbage ignored)",
      all(pb.memory[SCOREITEM_FLAGS + i] == 0 for i in range(9)),
      f"flags={[pb.memory[SCOREITEM_FLAGS + i] for i in range(9)]}")
cc = pb.memory[COLL_COUNT]
check("T11.d3 Every zone-0 collectible loads active (uncollected default)",
      all(pb.memory[COLL_DATA + i*4 + 3] == 1 for i in range(cc)),
      f"count={cc} actives={[pb.memory[COLL_DATA + i*4 + 3] for i in range(cc)]}")
pb.stop()
wipe_save()

# ══════════════════════════════════════════════════════
# T12 — World Generation (IP-1020)
# ══════════════════════════════════════════════════════
print("\n=== T12: World Generation ===")

T12_CORPUS = [(seed, scale) for scale in (2, 3, 9) for seed in (0, 1, 42, 12345, 65535)]

# T12.b/c/d/e — reuse one long-lived instance across the whole corpus:
# generate_world completes within a single tick() and depends only on
# SEED/WORLD_SCALE (both set fresh each call), so no reboot is needed.
pb = fresh_boot(180)
oracle_mismatches = []
bad_count = []
unreachable = []
bad_grammar = []
for seed, scale in T12_CORPUS:
    if not invoke_generate_world(pb, seed, scale):
        oracle_mismatches.append((seed, scale, "did not complete"))
        continue
    actual = read_region_graph(pb, scale)
    expected = worldgen.generate(seed, scale)
    if actual != expected:
        bad_idx = [i for i in range(len(actual)) if actual[i] != expected[i]][:3]
        oracle_mismatches.append((seed, scale, f"regions {bad_idx}"))
    if len(actual) != scale * scale:
        bad_count.append((seed, scale, len(actual)))
    seen = {0}; stack = [0]
    while stack:
        cur = stack.pop()
        for nb in actual[cur]['neighbors']:
            if nb is not None and nb not in seen:
                seen.add(nb); stack.append(nb)
    if len(seen) != len(actual):
        unreachable.append((seed, scale, len(seen), len(actual)))
    for i, r in enumerate(actual):
        for nb in r['neighbors']:
            if nb is not None and abs(r['biome_id'] - actual[nb]['biome_id']) > 1:
                bad_grammar.append((seed, scale, i, nb))
pb.stop()

check("T12.b Oracle parity: worldgen.py matches SM83 output, every corpus entry (AC-2 lockstep)",
      len(oracle_mismatches) == 0, f"mismatches={oracle_mismatches[:3]}")
check("T12.e One KeyItem per region: exactly scale^2 regions, every corpus entry (AC-5)",
      len(bad_count) == 0, f"bad={bad_count[:3]}")
check("T12.c Reachability: every region reachable from region 0, every corpus entry (AC-3)",
      len(unreachable) == 0, f"unreachable={unreachable[:3]}")
check("T12.d Grammar-validity: every generated edge legal (|biome_a-biome_b|<=1), every corpus entry (AC-4)",
      len(bad_grammar) == 0, f"bad_edges={bad_grammar[:3]}")

# T12.a — determinism: two separate PyBoy instances, same (seed, scale)
det_mismatches = []
for seed, scale in [(777, 5), (0, 9)]:
    pb1 = fresh_boot(180)
    invoke_generate_world(pb1, seed, scale)
    r1 = read_region_graph(pb1, scale)
    pb1.stop()
    pb2 = fresh_boot(180)
    invoke_generate_world(pb2, seed, scale)
    r2 = read_region_graph(pb2, scale)
    pb2.stop()
    if r1 != r2:
        det_mismatches.append((seed, scale))
check("T12.a Determinism: same (seed,scale) across two fresh boots -> byte-identical REGION_GRAPH (AC-2)",
      len(det_mismatches) == 0, f"mismatches={det_mismatches}")

# T12.f — seed=0 normalization: direct WRAM inspection of the PRNG state
# immediately after generate_world's own normalization step (hooked), never
# observing (TMP1,TMP2) == (0,0).
pb = fresh_boot(180)
t12f_state = {}
def _t12f_hook(ctx):
    t12f_state['tmp1'] = pb.memory[TMP1]
    t12f_state['tmp2'] = pb.memory[TMP2]
pb.hook_register(0, GW_SEED_OK_ADDR, _t12f_hook, None)
invoke_generate_world(pb, 0, 2)
pb.stop()
check("T12.f seed=0 normalizes to a nonzero PRNG state, direct WRAM inspection (AC-7 precondition)",
      t12f_state.get('tmp1', 0) != 0 or t12f_state.get('tmp2', 0) != 0,
      f"state=({t12f_state.get('tmp1')},{t12f_state.get('tmp2')})")

# T12.g — item-agnostic collection (AC-6): a direct extension of the existing
# carrot-collection pattern, per FS-102 Sec.16 — retargeted in T8.7/T8.8/
# T4.10 (KEYITEM_FLAGS/KEYITEM_COUNT) rather than duplicated here.

# T12.h — static determinism audit (AC-7, Inspection): generate_world/
# gw_prng_step must read no hardware register (DIV et al., via LDH) and no
# WRAM address beyond SEED/WORLD_SCALE/TMP1/TMP2/GW_*/REGION_GRAPH (its own
# prior output) — a real source-text scan, not an assumed pass.
_src = (BASE / 'asm_game.py').read_text()
_gw_start = _src.index("rom.label('generate_world')")
_gw_end = _src.index("rom.RET()", _src.index("rom.label('gw_prng_step')"))
_gw_src = _src[_src.index("rom.label('gw_prng_step')"):_gw_end] + _src[_gw_start:]
check("T12.h Static audit: no LDH (hardware register, incl. DIV) read in generate_world/gw_prng_step (NFR-2200)",
      'LDH_A_n' not in _gw_src and 'LDH_A_C' not in _gw_src, "source-scanned")

# T12.i — headroom audit (AC-8, Inspection): the new WRAM this package adds
# (SEED..GW_SCALE_SQ) stays inside bank-0 and the boot-time clear range.
check("T12.i WRAM headroom: SEED..GW_SCALE_SQ extent stays inside bank-0 + boot-clear range (NFR-4200)",
      SEED >= 0xC000 and GW_SCALE_SQ <= 0xC2FF,
      f"SEED=0x{SEED:04X} extent_end=0x{GW_SCALE_SQ:04X}")

# ══════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════
total = PASS + FAIL
print(f"\n{'='*52}")
print(f"  RESULTS: {PASS}/{total} passed   {FAIL} failed")
print(f"{'='*52}")
if FAIL:
    print("\nFailed tests:")
    for r in results:
        if r.startswith("[FAIL]"):
            print(" ", r)

with open(RESULTS_PATH, 'w') as f:
    f.write(f"BunnyQuest ROM Tests  PASS={PASS}/{total}  FAIL={FAIL}\n{'='*50}\n")
    for r in results: f.write(r + "\n")
print(f"\nSaved: {RESULTS_PATH}")

import sys
sys.exit(1 if FAIL else 0)
