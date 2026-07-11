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
  T10 SRAM save/load persistence (BUNY magic, full field set)
  T11 Per-zone ScoreItem persistence (IP-1010)
  T12 World generation (IP-1020) — determinism, oracle parity, reachability,
      grammar-validity, one-KeyItem-per-region, item-agnostic collection,
      seed=0 normalization, WRAM headroom
  T13 Generated-region screen composition (IP-1030) — tile-family audit,
      transition call-site audit, scale=3 arrow-placement regression
  T14 Main menu & new-game flow (IP-1040) — continue/new-game option-set,
      digit-cursor seed/scale entry, exit-to-main-menu, FR-9110 negative sweep
  T15 Generated-world save persistence (IP-1050) — seed/scale/KeyItemFlags
      round-trip, pre-upgrade rejection, legacy-field regression
  T16 CUR_ZONE-indexed structure generalization (IP-9070) — SCOREITEM_FLAGS
      bounds, zc_table biome-keyed lookup, save-format v3 round-trip,
      pre-upgrade rejection, legacy-field regression
  T17 Generated-world navigation (IP-9050) — scale=5 full-world traversal,
      scale=3 regression, boundary halt, entry-position correctness
      (supersedes/retires T9's fixed-3x3-grid checks)
  T18 Main menu cursor fix (IP-9060) — toggle with/without a save present,
      genuine re-entry still resets correctly, new-game end-to-end reachable

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
SCOREITEM_FLAGS = 0xC286   # up to 81 bytes, C286-C2D6 — one bitfield per region
                            # (FR-5220, generalized from the old 9-byte/9-zone array by IP-9070;
                            # relocated off 0xC060 to avoid colliding with REGION_GRAPH)
SEED = 0xC069; WORLD_SCALE = 0xC06B; REGION_GRAPH = 0xC070
MM_CURSOR = 0xC27E   # MAIN MENU highlighted option: 0=continue, 1=new game (IP-1040/IP-9060)
KEYITEM_FLAGS = 0xC220     # up to 81 bytes — generalizes CARROT_FLAGS (IP-1020);
                            # only indices 0-8 are live until FEAT-1100 ships
KEYITEM_COUNT = CARROTS_COUNT   # same WRAM slot as CARROTS_COUNT (IP-1020)

# SRAM save-format addresses (must match asm_game.py's save_to_sram/try_load_save)
SRAM_MAGIC = 0xA000; SRAM_CUR_ZONE = 0xA004; SRAM_PLAYER_X = 0xA005
SRAM_PLAYER_Y = 0xA006; SRAM_CARROTS_COUNT = 0xA007; SRAM_SCORE = 0xA008
SRAM_CARROT_FLAGS = 0xA009   # 9 bytes, A009-A011
SAVE_VERSION_ADDR = 0xA012; SAVE_VERSION_VAL = 0x03
SRAM_SCOREITEM = 0xA070      # up to 81 bytes, A070-A0C0 — relocated off A013-A01B by
                              # IP-9070, immediately after SRAM_KEYITEM_FLAGS's own end

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
    """From MAIN MENU (IP-1040 — boot always lands here; a fresh boot has no
    save, so 'new game' is the only/forced option): A -> SEED/SCALE ENTRY,
    A (confirm defaults: seed=0 -> normalized to 1 internally, scale=3) ->
    INTRO (runs generate_world), A -> PLAYING."""
    pb.button('a'); [pb.tick() for _ in range(40)]
    pb.button('a'); [pb.tick() for _ in range(80)]
    pb.button('a'); [pb.tick() for _ in range(80)]

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

# Source-data invariants (BL-0017 rider): exactly one carrot per list.
# IP-9070: ZONE_COLLECTS is now 5 biome-family-representative lists (indexed
# by REGION_GRAPH's biome-id), not 9 zone-named lists.
from tilemaps import ZONE_COLLECTS
check("T1.10 ZONE_COLLECTS has 5 biome-family lists (IP-9070)",
      len(ZONE_COLLECTS) == 5, f"{len(ZONE_COLLECTS)}")
carrots_per_zone = [sum(1 for (_, _, t) in z if t == 2) for z in ZONE_COLLECTS]
check("T1.11 Exactly one carrot per list", all(c == 1 for c in carrots_per_zone),
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
# T4 — State Machine (GS: 0=TITLE[superseded] 1=INTRO 2=PLAYING 3=SAVE
#      4=MAP 5=VICTORY 6=MAIN_MENU 7=SEED_SCALE_ENTRY — IP-1040)
# ══════════════════════════════════════════════════════
print("\n=== T4: State Machine ===")
pb = fresh_boot()

# IP-1040: the auto-load-on-boot bypass is retired — boot always reaches
# MAIN MENU now, never the superseded TITLE state (T14 covers MAIN MENU/
# SEED/SCALE ENTRY's own behavior in full; this suite just needs the
# overall state-machine loop to still hold end to end).
check("T4.1 Clean boot -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
shoot(pb, "T4_main_menu")

pb.button('a'); [pb.tick() for _ in range(40)]
check("T4.2 A (new game, no save) -> SEED/SCALE ENTRY (GS=7)",
      pb.memory[GAMESTATE] == 7, f"GS={pb.memory[GAMESTATE]}")
shoot(pb, "T4_seed_scale_entry")

pb.button('a'); [pb.tick() for _ in range(80)]
check("T4.2b A (confirm defaults) -> INTRO (GS=1)", pb.memory[GAMESTATE] == 1,
      f"GS={pb.memory[GAMESTATE]}")
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
check("T4.9 A in VICTORY -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
check("T4.10 Victory exit clears progress",
      pb.memory[CARROTS_COUNT] == 0 and pb.memory[SCORE] == 0
      and all(pb.memory[KEYITEM_FLAGS + i] == 0 for i in range(9)),
      f"carrots={pb.memory[CARROTS_COUNT]} score={pb.memory[SCORE]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T5 — BG Tilemap Content (main menu + region 0)
# ══════════════════════════════════════════════════════
print("\n=== T5: BG Tilemap ===")
pb = fresh_boot(200)

# IP-1040: MAIN MENU replaces TITLE as the boot screen. No save exists yet
# (fresh_boot wipes it), so "CONTINUE" must be blanked (mm_on_entry) and
# "NEW GAME" must remain visible.
row2 = [pb.memory[0x9800 + 2*32 + i] for i in range(2, 18)]
check("T5.1 Main menu: border row 2 (0x15)",   all(b == TL_BORDER_H for b in row2),
      f"row2[2]=0x{row2[0]:02X}")
row3 = [pb.memory[0x9800 + 3*32 + i] for i in range(5, 16)]
check("T5.2 Main menu: font tiles on row 3 (BUNNY QUEST)",
      any(TL_FONT_A <= b <= TL_FONT_COLON for b in row3),
      f"{[f'{b:02X}' for b in row3]}")
cont_row = [pb.memory[0x9800 + 7*32 + c] for c in range(8, 16)]
check("T5.3 Main menu: CONTINUE blanked (no save present)",
      all(b == TL_BG_BLANK for b in cont_row), f"{[f'{b:02X}' for b in cont_row]}")
newgame_row = [pb.memory[0x9800 + 9*32 + c] for c in range(8, 16)]
check("T5.3b Main menu: NEW GAME visible (font tiles)",
      any(TL_FONT_A <= b <= TL_FONT_COLON for b in newgame_row),
      f"{[f'{b:02X}' for b in newgame_row]}")
shoot(pb, "T5_main_menu")

# Advance to region 0 (new-game defaults: seed=0 -> normalized to 1, scale=3)
advance_to_playing(pb)

# Score bar (row 0, all regions share the pattern from _score_bar)
row0 = [pb.memory[0x9800 + i] for i in range(12)]
check("T5.4 Zone: row 0 col 0 = BG blank",        row0[0] == TL_BG_BLANK, f"0x{row0[0]:02X}")
check("T5.5 Zone: col 1 = carrot icon (0x13)",    row0[1] == TL_CARROT_ICON, f"0x{row0[1]:02X}")
check("T5.6 Zone: col 2 = carrot-count digit",    TL_DIGIT_0 <= row0[2] <= TL_DIGIT_0+9, f"0x{row0[2]:02X}")
check("T5.7 Zone: col 7 = star icon (0x14)",      row0[7] == TL_STAR_ICON_BG, f"0x{row0[7]:02X}")
check("T5.8 Zone: score digits at cols 8-10",     all(TL_DIGIT_0 <= row0[c] <= TL_DIGIT_0+9 for c in (8, 9, 10)),
      f"{[f'{row0[c]:02X}' for c in (8,9,10)]}")

# IP-1040 wires up the actual new-game generation call site: region 0's
# screen is now whatever biome worldgen.generate(seed=1, scale=3) — the
# real defaults advance_to_playing exercises — assigns it (verified
# directly: region 0 -> biome-id 2, Grass/forest_screen), not the
# pre-generation all-zero (Water) case IP-1030's T5.9 tested.
import worldgen as _wg5
_region0_biome = _wg5.generate(1, 3)[0]['biome_id']
_FAMILY_RANGES_T5 = {0: (0x88, 0x8D), 1: (0x70, 0x76), 2: (0x78, 0x7D),
                     3: (0x80, 0x85), 4: (0xB0, 0xB5)}
_lo, _hi = _FAMILY_RANGES_T5[_region0_biome]
field = [pb.memory[0x9800 + r*32 + c] for r in range(2, 17) for c in range(20)]
family_tiles = sum(1 for b in field if _lo <= b <= _hi)
check(f"T5.9 Region 0 (seed=1,scale=3 -> biome-id {_region0_biome}) uses its own tile family",
      family_tiles > 40, f"{family_tiles} tiles in 0x{_lo:02X}-0x{_hi:02X}")

shoot(pb, "T5_region0")
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
#      IP-9070: region 0's biome-id is always Grass (worldgen.py's own
#      "region (0,0) is always Grass" invariant), so setup_zone_collects
#      now pulls from ZONE_COLLECTS[2] (Forest, the Grass-family
#      representative) rather than ZONE_COLLECTS[0] (which is Water/Lake
#      under the new biome-id-ordered indexing) — the exact content this
#      package's fix is supposed to deliver (spawn content tracking the
#      region's real biome, not a fixed CUR_ZONE-indexed slot).
#      Forest's list: [0]=(28,40,flower) [1]=(64,32,star) [2]=(120,40,flower)
#      [3]=(40,96,star) [4]=(104,96,flower) [5]=(140,88,star) [6]=(84,56,CARROT).
#      Hit radius: |dx|<10, |dy|<10.
# ══════════════════════════════════════════════════════
print("\n=== T8: Collision / Score / Carrots ===")
pb = fresh_boot()
advance_to_playing(pb)

pb.memory[SCORE] = 0; pb.memory[CARROTS_COUNT] = 0
[pb.tick() for _ in range(5)]

check("T8.1 Score starts 0",   pb.memory[SCORE] == 0, f"{pb.memory[SCORE]}")
check("T8.2 Carrots start 0",  pb.memory[CARROTS_COUNT] == 0, f"{pb.memory[CARROTS_COUNT]}")
check("T8.3 COLL_COUNT = 7 in zone 0", pb.memory[COLL_COUNT] == 7, f"count={pb.memory[COLL_COUNT]}")

# Collect the star at (64,32) — entry index 1 — teleport onto it from a safe spot
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 80
[pb.tick() for _ in range(3)]
pb.memory[PLAYER_X] = 64; pb.memory[PLAYER_Y] = 32
[pb.tick() for _ in range(5)]
sc1 = pb.memory[SCORE]
check("T8.4 Score++ on ScoreItem collision", sc1 > 0, f"score={sc1}")
check("T8.5 ScoreItem deactivated in COLL_DATA", pb.memory[COLL_DATA + 1*4 + 3] == 0,
      f"active={pb.memory[COLL_DATA + 1*4 + 3]}")
check("T8.6 ScoreItem does not touch CARROTS_COUNT", pb.memory[CARROTS_COUNT] == 0,
      f"{pb.memory[CARROTS_COUNT]}")

# Collect the carrot at (84,56) — entry index 6
pb.memory[PLAYER_X] = 84; pb.memory[PLAYER_Y] = 56
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
# T10 — SRAM Save/Load (magic 'BUNY' at A000; fields A004-A011)
# ══════════════════════════════════════════════════════
print("\n=== T10: SRAM Save/Load ===")
wipe_save()

pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T10.1 No save -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")

advance_to_playing(pb)
check("T10.2 PLAYING after new-game flow", pb.memory[GAMESTATE] == 2)

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

# Reload: IP-1040 retires the auto-load bypass — boot always reaches MAIN
# MENU, now offering "continue" since a valid save exists (T14 covers this
# option-set logic in full); the player must explicitly select it.
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T10.6 Reload -> MAIN MENU (not auto-loaded)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
cont_row = [pb.memory[0x9800 + 7*32 + c] for c in range(8, 16)]
check("T10.6b CONTINUE offered (valid save present)",
      any(TL_FONT_A <= b <= TL_FONT_COLON for b in cont_row),
      f"{[f'{b:02X}' for b in cont_row]}")
pb.button('a'); [pb.tick() for _ in range(40)]
check("T10.6c A (continue) -> PLAYING", pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
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
# IP-1040: reload lands at MAIN MENU, not auto-loaded — select "continue".
pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(40)]
check("T10.14 B cancel: reload still has saved data",
      pb2.memory[PLAYER_X] == px_pre and pb2.memory[SCORE] == sc_pre,
      f"x={pb2.memory[PLAYER_X]} score={pb2.memory[SCORE]}")
pb2.stop()
wipe_save()   # leave no runtime save behind

# ══════════════════════════════════════════════════════
# T11 — Per-Zone ScoreItem Persistence (IP-1010 / FR-5220)
#       IP-9070: region 0 is always Grass, so ZONE_COLLECTS[2] (Forest)
#       applies here too — see T8's header for the full list. Hit radius:
#       |dx|<10, |dy|<10 (same as T8).
# ══════════════════════════════════════════════════════
print("\n=== T11: Per-Zone ScoreItem Persistence ===")

# T11.a — same-session: collect, leave the zone, return; item stays inactive
# and SCORE does not re-increment (AC-1; BL-0023's farming-bug regression).
# Region 0 is the grid's top-left corner, so only its down/right edges are
# ever grid-adjacent (up/left are always None) -- IP-1070's maze pass can
# block either one, so pick whichever the oracle actually left open instead
# of hardcoding "right" (which the default seed=0->1/scale=3 world no
# longer guarantees, the same supersession-sweep gap T17.b's rewrite found).
_t11a_regions = worldgen.generate(1, 3)   # advance_to_playing's own default
if _t11a_regions[0]['neighbors'][3] is not None:
    _t11a_dir, _t11a_expect = 3, _t11a_regions[0]['neighbors'][3]   # right
else:
    _t11a_dir, _t11a_expect = 1, _t11a_regions[0]['neighbors'][1]   # down

pb = fresh_boot()
advance_to_playing(pb)
pb.memory[PLAYER_X] = 20; pb.memory[PLAYER_Y] = 32
[pb.tick() for _ in range(5)]
sc_after = pb.memory[SCORE]
check("T11.a1 Star (index 0) collected", sc_after > 0, f"score={sc_after}")

if _t11a_dir == 3:
    pb.memory[PLAYER_X] = 156; pb.memory[PLAYER_Y] = 72
else:
    pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 128
[pb.tick() for _ in range(80)]
check("T11.a2 Transitioned out of zone 0", pb.memory[CUR_ZONE] == _t11a_expect, f"zone={pb.memory[CUR_ZONE]}")
if _t11a_dir == 3:
    pb.memory[PLAYER_X] = 0
else:
    pb.memory[PLAYER_Y] = 17
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
pb.memory[PLAYER_X] = 104; pb.memory[PLAYER_Y] = 96   # index 4 (Forest flower)
[pb.tick() for _ in range(5)]
sc_pre = pb.memory[SCORE]
check("T11.b1 ScoreItem (index 4) collected", sc_pre > 0, f"score={sc_pre}")
zone_pre = pb.memory[CUR_ZONE]; x_pre = pb.memory[PLAYER_X]; y_pre = pb.memory[PLAYER_Y]
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');     [pb.tick() for _ in range(40)]
check("T11.b2 Saved -> PLAYING", pb.memory[GAMESTATE] == 2)
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
check("T11.b3a Reload -> MAIN MENU (not auto-loaded, IP-1040)",
      pb2.memory[GAMESTATE] == 6, f"GS={pb2.memory[GAMESTATE]}")
pb2.button('a'); [pb2.tick() for _ in range(40)]
check("T11.b3 A (continue) -> PLAYING", pb2.memory[GAMESTATE] == 2, f"GS={pb2.memory[GAMESTATE]}")
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

# IP-1040/ADR-0010 supersedes the old auto-load-based graceful-degrade:
# a version-mismatched save is now treated as absent for "continue"
# purposes at MAIN MENU (never auto-loaded at all, not even partially) —
# its bytes are left untouched (not overwritten) until the player proceeds
# through a fresh new-game creation, which must still work cleanly.
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T11.d1 Pre-upgrade save loads without crash -> MAIN MENU",
      pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
cont_row = [pb.memory[0x9800 + 7*32 + c] for c in range(8, 16)]
check("T11.d1b CONTINUE absent (version-mismatched save treated as none, ADR-0010)",
      all(b == TL_BG_BLANK for b in cont_row), f"{[f'{b:02X}' for b in cont_row]}")
advance_to_playing(pb)
check("T11.d1c New game still reaches PLAYING cleanly despite old SRAM bytes",
      pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
check("T11.d2 SCOREITEM_FLAGS all zero (fresh new-game default)",
      all(pb.memory[SCOREITEM_FLAGS + i] == 0 for i in range(9)),
      f"flags={[pb.memory[SCOREITEM_FLAGS + i] for i in range(9)]}")
cc = pb.memory[COLL_COUNT]
check("T11.d3 Every region-0 collectible loads active (fresh new-game default)",
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
# T13 — Generated-Region Screen Composition (IP-1030)
# ══════════════════════════════════════════════════════
print("\n=== T13: Generated-Region Screen Composition ===")

def force_region_redraw(pb, region):
    pb.memory[CUR_ZONE] = region
    pb.memory[NEED_REDRAW] = 1
    for _ in range(10): pb.tick()

def field_tiles(pb):
    return [pb.memory[0x9800 + r*32 + c] for r in range(2, 17) for c in range(20)]

# T13.a — tile-family audit (AC-1): one representative region per biome-id,
# directly forced via REGION_GRAPH (isolates the rendering dispatch from
# generation correctness, which T12 already covers exhaustively) — confirms
# dsr_p's biome-id dispatch selects the right family screen for all 5 IDs.
FAMILY_RANGES = {
    0: (0x88, 0x8D),   # water -> lake_screen
    1: (0x70, 0x76),   # sand  -> beach_screen
    2: (0x78, 0x7D),   # grass -> forest_screen
    3: (0x80, 0x85),   # stone -> mountain_screen
    4: (0xB0, 0xB5),   # brick -> castle_screen
}
pb = fresh_boot(180)
advance_to_playing(pb)
family_bad = []
for biome_id, (lo, hi) in FAMILY_RANGES.items():
    pb.memory[REGION_GRAPH] = biome_id
    for k in range(4): pb.memory[REGION_GRAPH + 1 + k] = 0xFF   # no neighbors
    force_region_redraw(pb, 0)
    field = field_tiles(pb)
    in_family = sum(1 for b in field if lo <= b <= hi)
    if in_family <= 40:
        family_bad.append((biome_id, in_family))
pb.stop()
check("T13.a Tile-family audit: each of the 5 biome-ids renders its own family's tiles (AC-1)",
      len(family_bad) == 0, f"bad={family_bad}")

# T13.b — transition call-site audit (AC-2, Inspection): exactly one
# copy_screen call site handles region-entry (PLAYING) rendering, mirroring
# VR-9020's own sweep methodology (confirms no new/alternate VRAM write
# path was introduced for generated content) — scoped to dsr_p's own body,
# since the 5 UI screens (title/intro/save/map/victory) have always had
# their own separate, pre-existing copy_screen call site (_dsr_screen).
_src = (BASE / 'asm_game.py').read_text()
_dsr_p_src = _src[_src.index("rom.label('dsr_p')"):_src.index("rom.label('dsr_done')")]
_copy_screen_calls = _dsr_p_src.count("CALL('copy_screen')")
check("T13.b Transition call-site audit: exactly one copy_screen call site in dsr_p (AC-2)",
      _copy_screen_calls == 1, f"{_copy_screen_calls} call site(s)")

# T13.c — regression: at scale=3, arrow placement matches the shipped 3x3
# grid exactly, for every region. generate_world's neighbor computation is a
# pure function of (row, col, scale) — independent of the PRNG/seed — so
# this holds for any seed at scale=3, not just one fixed case. Neighbor
# bytes are forced directly (not via invoke_generate_world, whose PC/SP
# hijack traps the CPU in a self-loop that can't resume normal button-
# driven gameplay afterward — T12 already exhaustively covers generation
# correctness; this test isolates the rendering side, same as T13.a).
def arrow_addr(x, y): return 0x9800 + y*32 + x
ARROW_POS = {'up': arrow_addr(15, 1), 'down': arrow_addr(15, 16),
             'left': arrow_addr(1, 9), 'right': arrow_addr(32-2, 9)}
ARROW_TILE = {'up': 0x18, 'down': 0x19, 'left': 0x17, 'right': 0x16}  # TL_ARROW_U/D/L/R

pb = fresh_boot(180)
advance_to_playing(pb)
arrow_bad = []
for region in range(9):
    row, col = region // 3, region % 3
    expected = {'up': row > 0, 'down': row < 2, 'left': col > 0, 'right': col < 2}
    pb.memory[REGION_GRAPH + region*5 + 1] = (region - 3) & 0xFF if row > 0 else 0xFF
    pb.memory[REGION_GRAPH + region*5 + 2] = (region + 3) & 0xFF if row < 2 else 0xFF
    pb.memory[REGION_GRAPH + region*5 + 3] = (region - 1) & 0xFF if col > 0 else 0xFF
    pb.memory[REGION_GRAPH + region*5 + 4] = (region + 1) & 0xFF if col < 2 else 0xFF
    force_region_redraw(pb, region)
    for direction, addr in ARROW_POS.items():
        present = pb.memory[addr] == ARROW_TILE[direction]
        if present != expected[direction]:
            arrow_bad.append((region, direction, present, expected[direction]))
pb.stop()
check("T13.c Regression: scale=3 arrow placement matches shipped 3x3 grid, every region/direction",
      len(arrow_bad) == 0, f"bad={arrow_bad[:5]}")

# ══════════════════════════════════════════════════════
# T14 — Main Menu & New-Game Flow (IP-1040)
# (FS-104's own template names "T13"; renumbered — IP-1030 already claimed
# T13 earlier this same tranche.)
# ══════════════════════════════════════════════════════
print("\n=== T14: Main Menu & New-Game Flow ===")

def enter_seed_scale(pb, digits, scale):
    """From SEED/SCALE ENTRY at its just-entered defaults (cursor=0, all
    digits 0, scale=3): drive the digit-cursor picker to the given 5 seed
    digits + scale, then confirm with A."""
    for i, d in enumerate(digits):
        for _ in range(d):
            pb.button('up'); [pb.tick() for _ in range(10)]
        if i < 4:
            pb.button('right'); [pb.tick() for _ in range(10)]
    pb.button('right'); [pb.tick() for _ in range(10)]   # move to scale slot
    delta = scale - 3
    btn = 'up' if delta > 0 else 'down'
    for _ in range(abs(delta)):
        pb.button(btn); [pb.tick() for _ in range(10)]
    pb.button('a'); [pb.tick() for _ in range(80)]

def continue_offered(pb):
    row = [pb.memory[0x9800 + 7*32 + c] for c in range(8, 16)]
    return any(TL_FONT_A <= b <= TL_FONT_COLON for b in row)

# T14.a1/a2 — no save present: MAIN MENU, "continue" absent (AC-1/AC-2 fwd).
pb = fresh_boot(200)
check("T14.a1 Boot, no save -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
check("T14.a2 No save -> CONTINUE absent", not continue_offered(pb), "")
pb.stop()
wipe_save()

# T14.a3 — valid version-matching save present: MAIN MENU (not PLAYING,
# confirming the auto-load bypass is retired), "continue" present (AC-1/2 rev).
pb = fresh_boot(200)
advance_to_playing(pb)
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]     # SAVE -> A -> PLAYING
pb.stop()
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T14.a3a Valid save present -> MAIN MENU, not auto-loaded PLAYING",
      pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
check("T14.a3b Valid save -> CONTINUE present", continue_offered(pb), "")
pb.stop()
wipe_save()

# T14.a4 — version-mismatched (pre-upgrade) save: "continue" absent,
# following IP-1010's T11.d synthetic-fixture pattern exactly.
fixture = bytearray(8192)
fixture[0:4] = bytes([0x42, 0x55, 0x4E, 0x59])
fixture[SAVE_VERSION_ADDR - 0xA000] = 0x00
with open(RAM_PATH, 'wb') as f:
    f.write(bytes(fixture))
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T14.a4 Version-mismatched save -> CONTINUE absent (ADR-0010)",
      not continue_offered(pb), "")
pb.stop()
wipe_save()

# T14.b1/b2 — digit-cursor entry for a known (seed, scale): confirm -> INTRO,
# region count == scale^2 (AC-3).
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]           # MAIN MENU -> new game -> SEED/SCALE ENTRY
enter_seed_scale(pb, [1, 2, 3, 4, 5], 5)                 # seed=12345, scale=5
check("T14.b1 Confirm -> INTRO (GS=1)", pb.memory[GAMESTATE] == 1, f"GS={pb.memory[GAMESTATE]}")
check("T14.b1b SEED written correctly (12345)",
      pb.memory[SEED] | (pb.memory[SEED+1] << 8) == 12345,
      f"seed={pb.memory[SEED] | (pb.memory[SEED+1] << 8)}")
check("T14.b1c WORLD_SCALE written correctly (5)", pb.memory[WORLD_SCALE] == 5,
      f"scale={pb.memory[WORLD_SCALE]}")
regions_b = read_region_graph(pb, 5)
check("T14.b2 Region count == scale^2 (25) (AC-3)", len(regions_b) == 25, f"{len(regions_b)}")
region_graph_b1 = regions_b
pb.stop()

# T14.b3 — same (seed, scale) in a fresh new-game creation -> identical
# region graph (AC-4; the actual byte-for-byte comparison rides IP-1020's
# own oracle/SM83 lockstep, T12.b — this confirms this Feature's own
# trigger path reaches generate_world with the same inputs both times).
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
enter_seed_scale(pb, [1, 2, 3, 4, 5], 5)
region_graph_b2 = read_region_graph(pb, 5)
pb.stop()
check("T14.b3 Same (seed,scale) -> identical region graph across two new-game creations (AC-4)",
      region_graph_b1 == region_graph_b2, "")

# T14.c1 — SEED/SCALE ENTRY, B -> MAIN MENU, without writing SEED/WORLD_SCALE
# (FS-104 Open Question 1's resolution, tested directly).
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
seed_before = pb.memory[SEED] | (pb.memory[SEED+1] << 8)
scale_before = pb.memory[WORLD_SCALE]
pb.button('up'); [pb.tick() for _ in range(10)]   # touch a digit, then abandon via B
pb.button('b');  [pb.tick() for _ in range(40)]
check("T14.c1 B in SEED/SCALE ENTRY -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
check("T14.c1b B-cancel does not write SEED/WORLD_SCALE",
      pb.memory[SEED] | (pb.memory[SEED+1] << 8) == seed_before
      and pb.memory[WORLD_SCALE] == scale_before,
      f"seed={pb.memory[SEED] | (pb.memory[SEED+1] << 8)} scale={pb.memory[WORLD_SCALE]}")
pb.stop()
wipe_save()

# T14.d1/d2 — exit-to-main-menu from SAVE (AC-5/AC-6): auto-saves, ->
# MAIN MENU; reload via "continue" restores the exact pre-exit state.
pb = fresh_boot(200)
advance_to_playing(pb)
pb.memory[PLAYER_X] = 90; pb.memory[PLAYER_Y] = 100
pb.memory[SCORE] = 4; pb.memory[CARROTS_COUNT] = 1
[pb.tick() for _ in range(5)]
x_pre14 = pb.memory[PLAYER_X]; y_pre14 = pb.memory[PLAYER_Y]
sc_pre14 = pb.memory[SCORE]; cc_pre14 = pb.memory[CARROTS_COUNT]
pb.button('start');  [pb.tick() for _ in range(40)]
check("T14.d0 START -> SAVE", pb.memory[GAMESTATE] == 3)
pb.button('select'); [pb.tick() for _ in range(40)]
check("T14.d1 SELECT (exit-to-main-menu) -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
pb.stop()
check("T14.d1b RAM file created (auto-save on exit)", os.path.exists(RAM_PATH), RAM_PATH)

pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T14.d2a Reload -> MAIN MENU, CONTINUE present", continue_offered(pb), "")
pb.button('a'); [pb.tick() for _ in range(40)]
check("T14.d2b Continue -> PLAYING", pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
check("T14.d2c Restored state matches exactly what was present at exit (AC-6)",
      pb.memory[PLAYER_X] == x_pre14 and pb.memory[PLAYER_Y] == y_pre14
      and pb.memory[SCORE] == sc_pre14 and pb.memory[CARROTS_COUNT] == cc_pre14,
      f"x={pb.memory[PLAYER_X]} y={pb.memory[PLAYER_Y]} score={pb.memory[SCORE]} carrots={pb.memory[CARROTS_COUNT]}")
pb.stop()
wipe_save()

# T14.e — FR-9110 negative-test sweep: no reachable input sequence from
# PLAYING, SAVE, or MAP writes SEED/WORLD_SCALE. Static audit (the only
# write sites are inside sse_compose_seed, reachable only via
# st_seed_scale_entry's A-confirm, and try_load_save's SRAM-restore block,
# reachable only via MAIN MENU's "continue" — IP-1050 — neither reachable
# from PLAYING/SAVE/MAP) + a runtime spot-check driving every input branch
# in each of the 3 states.
_src14 = (BASE / 'asm_game.py').read_text()
_scs_start = _src14.index("rom.label('sse_compose_seed')")
_scs_end = _src14.index("rom.label('setup_zone_collects')")
_tls_start = _src14.index("rom.label('try_load_save')")
_tls_end = _src14.index("rom.label('tls_no')")
_outside_scs = (_src14[:_scs_start] + _src14[_scs_end:_tls_start]
                + _src14[_tls_end:])
_seed_writes_outside = _outside_scs.count("LD_nn_A(SEED)") + _outside_scs.count("LD_nn_A(SEED + 1)")
_scale_writes_outside = _outside_scs.count("LD_nn_A(WORLD_SCALE)")
check("T14.e1 Static audit: SEED/WORLD_SCALE written only inside sse_compose_seed/try_load_save (FR-9110)",
      _seed_writes_outside == 0 and _scale_writes_outside == 0,
      f"seed_writes={_seed_writes_outside} scale_writes={_scale_writes_outside}")

pb = fresh_boot(200)
advance_to_playing(pb)
seed_before_e = pb.memory[SEED] | (pb.memory[SEED+1] << 8)
scale_before_e = pb.memory[WORLD_SCALE]
# PLAYING: movement, START (->SAVE->B->PLAYING), START (->SAVE->A(save)->PLAYING)
for btn in ('up', 'down', 'left', 'right'):
    pb.button(btn); [pb.tick() for _ in range(10)]
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('b');     [pb.tick() for _ in range(40)]        # SAVE: B
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]       # SAVE: A (save)
# MAP: SELECT enters, B and SELECT both exit back to PLAYING
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('b');       [pb.tick() for _ in range(40)]       # MAP: B
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('select');  [pb.tick() for _ in range(40)]       # MAP: SELECT
seed_after_e = pb.memory[SEED] | (pb.memory[SEED+1] << 8)
scale_after_e = pb.memory[WORLD_SCALE]
pb.stop()
wipe_save()
check("T14.e2 Runtime sweep (PLAYING/SAVE/MAP, every input branch) leaves SEED/WORLD_SCALE unchanged",
      seed_after_e == seed_before_e and scale_after_e == scale_before_e,
      f"seed {seed_before_e}->{seed_after_e} scale {scale_before_e}->{scale_after_e}")

# ══════════════════════════════════════════════════════
# T15 — Generated-World Save Persistence (IP-1050)
# (FS-105's own template names "T14"; renumbered — IP-1040 already
# claimed T14 earlier this same tranche.)
# ══════════════════════════════════════════════════════
print("\n=== T15: Generated-World Save Persistence ===")

# T15.a — round-trip: save with a known (SEED, WORLD_SCALE, KeyItemFlags),
# reload in a fresh PyBoy instance, assert exact match on all three, and
# assert the regenerated region graph matches the pre-save graph (AC-1).
wipe_save()
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
enter_seed_scale(pb, [5, 4, 3, 2, 1], 3)   # seed=54321, scale=3
seed_pre15 = pb.memory[SEED] | (pb.memory[SEED + 1] << 8)
scale_pre15 = pb.memory[WORLD_SCALE]
pb.button('a'); [pb.tick() for _ in range(80)]   # INTRO -> PLAYING
region_graph_pre15 = read_region_graph(pb, scale_pre15)
pb.memory[PLAYER_X] = 84; pb.memory[PLAYER_Y] = 56   # region 0's KeyItem (Forest CARROT, IP-9070)
[pb.tick() for _ in range(5)]
keyitem_pre15 = [pb.memory[KEYITEM_FLAGS + i] for i in range(9)]
check("T15.a0 KeyItem collected (KEYITEM_FLAGS[0] set)", keyitem_pre15[0] == 1,
      f"flags={keyitem_pre15}")
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');     [pb.tick() for _ in range(40)]   # SAVE -> A -> PLAYING
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
check("T15.a1 Reload -> MAIN MENU, CONTINUE present (version-2 save)",
      continue_offered(pb2), "")
pb2.button('a'); [pb2.tick() for _ in range(40)]
check("T15.a2 Continue -> PLAYING", pb2.memory[GAMESTATE] == 2, f"GS={pb2.memory[GAMESTATE]}")
seed_post15 = pb2.memory[SEED] | (pb2.memory[SEED + 1] << 8)
scale_post15 = pb2.memory[WORLD_SCALE]
check("T15.a3 SEED round-trips exactly", seed_post15 == seed_pre15,
      f"{seed_pre15}->{seed_post15}")
check("T15.a4 WORLD_SCALE round-trips exactly", scale_post15 == scale_pre15,
      f"{scale_pre15}->{scale_post15}")
region_graph_post15 = read_region_graph(pb2, scale_post15)
check("T15.a5 Regenerated region graph matches pre-save graph (AC-1, ADR-0009 determinism)",
      region_graph_post15 == region_graph_pre15, "")
keyitem_post15 = [pb2.memory[KEYITEM_FLAGS + i] for i in range(9)]
check("T15.a6 KEYITEM_FLAGS round-trips exactly", keyitem_post15 == keyitem_pre15,
      f"{keyitem_pre15}->{keyitem_post15}")
pb2.stop()
wipe_save()

# T15.b — pre-upgrade rejection: a synthetic IP-1010-vintage fixture
# (version byte 0x01, valid magic + legacy fields, no valid seed/scale/
# region data) — confirm "continue" is not offered (AC-2).
fixture = bytearray(8192)
fixture[0:4] = bytes([0x42, 0x55, 0x4E, 0x59])
fixture[SRAM_CUR_ZONE - 0xA000] = 0
fixture[SRAM_PLAYER_X - 0xA000] = 76
fixture[SRAM_PLAYER_Y - 0xA000] = 80
fixture[SAVE_VERSION_ADDR - 0xA000] = 0x01   # IP-1010's own vintage, now superseded
for i in range(9): fixture[SRAM_SCOREITEM - 0xA000 + i] = 0xFF
with open(RAM_PATH, 'wb') as f:
    f.write(bytes(fixture))
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T15.b1 Boot with IP-1010-vintage (version=1) save -> MAIN MENU",
      pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
check("T15.b2 Version-1 save -> CONTINUE absent (AC-2, ADR-0010)",
      not continue_offered(pb), "")
advance_to_playing(pb)
check("T15.b3 New game still reaches PLAYING cleanly despite the old version-1 save",
      pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
pb.stop()
wipe_save()

# T15.c — legacy-field regression: CUR_ZONE/position/KeyItemCount/SCORE/
# KEYITEM_FLAGS/SCOREITEM_FLAGS still round-trip exactly under the new
# version-2 format, extending T10/T11's existing patterns.
pb = fresh_boot(200)
advance_to_playing(pb)
pb.memory[PLAYER_X] = 132; pb.memory[PLAYER_Y] = 88
[pb.tick() for _ in range(5)]   # collect zone 0's KeyItem -> KEYITEM_COUNT/SCORE
pb.memory[PLAYER_X] = 20; pb.memory[PLAYER_Y] = 32
[pb.tick() for _ in range(5)]   # collect a ScoreItem -> SCOREITEM_FLAGS/SCORE
zone_pre15c = pb.memory[CUR_ZONE]; x_pre15c = pb.memory[PLAYER_X]; y_pre15c = pb.memory[PLAYER_Y]
kc_pre15c = pb.memory[KEYITEM_COUNT]; sc_pre15c = pb.memory[SCORE]
kf_pre15c = [pb.memory[KEYITEM_FLAGS + i] for i in range(9)]
sf_pre15c = [pb.memory[SCOREITEM_FLAGS + i] for i in range(9)]
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(40)]
check("T15.c1 CUR_ZONE preserved (version-2 format)", pb2.memory[CUR_ZONE] == zone_pre15c,
      f"{zone_pre15c}->{pb2.memory[CUR_ZONE]}")
check("T15.c2 PLAYER_X/Y preserved",
      pb2.memory[PLAYER_X] == x_pre15c and pb2.memory[PLAYER_Y] == y_pre15c,
      f"({x_pre15c},{y_pre15c})->({pb2.memory[PLAYER_X]},{pb2.memory[PLAYER_Y]})")
check("T15.c3 KEYITEM_COUNT preserved", pb2.memory[KEYITEM_COUNT] == kc_pre15c,
      f"{kc_pre15c}->{pb2.memory[KEYITEM_COUNT]}")
check("T15.c4 SCORE preserved", pb2.memory[SCORE] == sc_pre15c,
      f"{sc_pre15c}->{pb2.memory[SCORE]}")
check("T15.c5 KEYITEM_FLAGS preserved",
      [pb2.memory[KEYITEM_FLAGS + i] for i in range(9)] == kf_pre15c, "")
check("T15.c6 SCOREITEM_FLAGS preserved",
      [pb2.memory[SCOREITEM_FLAGS + i] for i in range(9)] == sf_pre15c, "")
pb2.stop()
wipe_save()

# T15.d — static audit: REGION_GRAPH is never written to SRAM by
# save_to_sram — only SEED/WORLD_SCALE/KEYITEM_FLAGS (DoD's own explicit
# requirement, confirmed by direct diff, not merely asserted).
_src15 = (BASE / 'asm_game.py').read_text()
_sts_start = _src15.index("rom.label('save_to_sram')")
_sts_end = _src15.index("rom.label('check_save_valid')")
_save_lines = _src15[_sts_start:_sts_end].splitlines()
_save_code_only = "\n".join(ln.split('#', 1)[0] for ln in _save_lines)
check("T15.d REGION_GRAPH never written to SRAM by save_to_sram",
      "REGION_GRAPH" not in _save_code_only, "")

# ══════════════════════════════════════════════════════
# T16 — CUR_ZONE-Indexed Structure Generalization (IP-9070)
# ══════════════════════════════════════════════════════
print("\n=== T16: CUR_ZONE-Indexed Structure Generalization ===")

# T16.a — SCOREITEM_FLAGS bounds (direct regression for BL-0058): force
# CUR_ZONE to a region above the old 9-zone ceiling and a real ScoreItem
# collection event; confirm the write lands inside SCOREITEM_FLAGS's new
# 81-byte extent and REGION_GRAPH's own bytes are byte-for-byte unchanged.
pb = fresh_boot(180)
advance_to_playing(pb)
pb.memory[REGION_GRAPH + 40*5] = 2   # force region 40 = Grass (Forest list)
for k in range(4): pb.memory[REGION_GRAPH + 40*5 + 1 + k] = 0xFF
force_region_redraw(pb, 40)
check("T16.a1 COLL_COUNT = 7 in forced region 40 (Forest list, biome-id lookup)",
      pb.memory[COLL_COUNT] == 7, f"count={pb.memory[COLL_COUNT]}")
region_graph_snapshot = [pb.memory[REGION_GRAPH + i] for i in range(405)]
pb.memory[PLAYER_X] = 64; pb.memory[PLAYER_Y] = 32   # Forest index 1 (star)
[pb.tick() for _ in range(5)]
check("T16.a2 ScoreItem collected in region 40", pb.memory[SCORE] > 0,
      f"score={pb.memory[SCORE]}")
check("T16.a3 SCOREITEM_FLAGS[40] bit 1 set, inside the new 81-byte extent",
      pb.memory[SCOREITEM_FLAGS + 40] == 0b10, f"{pb.memory[SCOREITEM_FLAGS + 40]:#04b}")
region_graph_after = [pb.memory[REGION_GRAPH + i] for i in range(405)]
check("T16.a4 REGION_GRAPH bytes unaffected by the region-40 collection (BL-0058)",
      region_graph_after == region_graph_snapshot, "")
pb.stop()

# T16.b — zc_table/ZONE_COLLECTS biome-keyed lookup (direct regression for
# BL-0059): for each of the 5 biome-ids, force REGION_GRAPH's biome byte and
# confirm setup_zone_collects populates COLL_DATA from the correct
# biome-family list, cross-checked against the 5 retained lists' own
# contents (imported directly from tilemaps.ZONE_COLLECTS, not re-typed).
pb = fresh_boot(180)
advance_to_playing(pb)
lookup_bad = []
for biome_id in range(5):
    pb.memory[REGION_GRAPH] = biome_id
    for k in range(4): pb.memory[REGION_GRAPH + 1 + k] = 0xFF
    force_region_redraw(pb, 0)
    expected = ZONE_COLLECTS[biome_id]
    count = pb.memory[COLL_COUNT]
    actual = [(pb.memory[COLL_DATA + i*4], pb.memory[COLL_DATA + i*4 + 1],
               pb.memory[COLL_DATA + i*4 + 2]) for i in range(count)]
    if count != len(expected) or actual != list(expected):
        lookup_bad.append((biome_id, count, actual, expected))
pb.stop()
check("T16.b zc_table biome-keyed lookup: each of the 5 biome-ids populates COLL_DATA from its own ZONE_COLLECTS list (BL-0059)",
      len(lookup_bad) == 0, f"bad={lookup_bad}")

# T16.c — save-format version-3 round-trip: a known SCOREITEM_FLAGS state
# spanning multiple regions, including one above the old 9-zone ceiling,
# round-trips exactly through a fresh PyBoy reload (extends T11/T15's
# two-instance pattern).
wipe_save()
pb = fresh_boot(180)
advance_to_playing(pb)
for zone, bits in {0: 0b101, 8: 0b1, 40: 0b10, 80: 0b1000001}.items():
    pb.memory[SCOREITEM_FLAGS + zone] = bits
sf_pre16c = [pb.memory[SCOREITEM_FLAGS + i] for i in range(81)]
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(40)]
sf_post16c = [pb2.memory[SCOREITEM_FLAGS + i] for i in range(81)]
check("T16.c SCOREITEM_FLAGS round-trips exactly across all 81 bytes, including region 80 (save-format v3)",
      sf_post16c == sf_pre16c,
      f"mismatch at {[i for i in range(81) if sf_post16c[i] != sf_pre16c[i]]}")
pb2.stop()
wipe_save()

# T16.d — pre-upgrade rejection: a synthetic IP-1050-vintage (version=2)
# save fixture -> confirm "continue" is not offered under the new
# version-3 guard (AC-2 extended a third time, following T15.b1-3's exact
# precedent).
fixture = bytearray(8192)
fixture[0:4] = bytes([0x42, 0x55, 0x4E, 0x59])
fixture[SRAM_CUR_ZONE - 0xA000] = 0
fixture[SRAM_PLAYER_X - 0xA000] = 76
fixture[SRAM_PLAYER_Y - 0xA000] = 80
fixture[SAVE_VERSION_ADDR - 0xA000] = 0x02   # IP-1050's own vintage, now superseded
for i in range(81): fixture[SRAM_SCOREITEM - 0xA000 + i] = 0xFF
with open(RAM_PATH, 'wb') as f:
    f.write(bytes(fixture))
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T16.d1 Boot with IP-1050-vintage (version=2) save -> MAIN MENU",
      pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
check("T16.d2 Version-2 save -> CONTINUE absent (AC-2, third guard extension)",
      not continue_offered(pb), "")
advance_to_playing(pb)
check("T16.d3 New game still reaches PLAYING cleanly despite the old version-2 save",
      pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")
pb.stop()
wipe_save()

# T16.e — legacy-field regression (scope audit, not just a DoD claim):
# SEED/WORLD_SCALE/KEYITEM_FLAGS/REGION_GRAPH regeneration are all
# unaffected by this package's SCOREITEM_FLAGS relocation. Uses scale=7
# (49 regions) so the region range genuinely exceeds the old 9-zone model.
wipe_save()
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
enter_seed_scale(pb, [0, 0, 7, 7, 7], 7)   # seed=777, scale=7
seed_pre16e = pb.memory[SEED] | (pb.memory[SEED + 1] << 8)
scale_pre16e = pb.memory[WORLD_SCALE]
pb.button('a'); [pb.tick() for _ in range(80)]   # INTRO -> PLAYING
region_graph_pre16e = read_region_graph(pb, scale_pre16e)
kf_pre16e = [pb.memory[KEYITEM_FLAGS + i] for i in range(81)]
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(40)]
seed_post16e = pb2.memory[SEED] | (pb2.memory[SEED + 1] << 8)
scale_post16e = pb2.memory[WORLD_SCALE]
region_graph_post16e = read_region_graph(pb2, scale_post16e)
kf_post16e = [pb2.memory[KEYITEM_FLAGS + i] for i in range(81)]
check("T16.e1 SEED unaffected by SCOREITEM_FLAGS relocation",
      seed_post16e == seed_pre16e, f"{seed_pre16e}->{seed_post16e}")
check("T16.e2 WORLD_SCALE unaffected", scale_post16e == scale_pre16e,
      f"{scale_pre16e}->{scale_post16e}")
check("T16.e3 REGION_GRAPH regeneration unaffected (49 regions, scale=7)",
      region_graph_post16e == region_graph_pre16e, "")
check("T16.e4 KEYITEM_FLAGS unaffected", kf_post16e == kf_pre16e, "")
pb2.stop()
wipe_save()

# ══════════════════════════════════════════════════════
# T17 — Generated-World Navigation (IP-9050; graph-driven since IP-1070)
#      check_zone_transition regeneralized to read REGION_GRAPH's neighbor
#      bytes (BL-0047's fix) — supersedes T9's fixed-3x3-grid checks
#      entirely (retired, not kept alongside these, per R305's "rewrite,
#      don't patch" precedent).
#      right: x>=156 -> zone=REGION_GRAPH[zone].right, X=8
#      left:  x==0  -> zone=REGION_GRAPH[zone].left, X=150
#      up:    y<18  -> zone=REGION_GRAPH[zone].up, Y=120
#      down:  y>=128 -> zone=REGION_GRAPH[zone].down, Y=24
#
#      IP-1070 (2026-07-11) supersedes a hidden assumption this suite's own
#      original hardcoded walks made: that every grid-adjacent region pair
#      is always connected. That's no longer true for ANY scale, including
#      the scale=3 default fixture T17.b uses (IP-1070's maze pass runs for
#      every generated world) -- a genuine supersession-sweep miss in
#      IP-1070's own planning pass (its own §7 only checked dsr_p/
#      draw_region_arrows/check_zone_transition/tilemaps.py/T12, not this
#      suite's own hardcoded-path assumption). Both T17.a (scale=5) and
#      T17.b (scale=3) below are rewritten graph-driven: a real,
#      button-driven DFS tour over whatever edges the actual generated
#      graph provides (including its own backtrack steps, each a genuine
#      valid move since REGION_GRAPH is symmetric by construction), visiting
#      every reachable region -- works for any maze topology, not just a
#      full lattice, and (T17.b) also probes every direction at every
#      visited region to confirm open/blocked matches the oracle exactly,
#      subsuming the original suite's specific blocked-case spot-checks.
# ══════════════════════════════════════════════════════
print("\n=== T17: Generated-World Navigation ===")

def settle(pb, frames=80):
    [pb.tick() for _ in range(frames)]

_T17_OPP = {0: 1, 1: 0, 2: 3, 3: 2}   # up<->down, left<->right

def _t17_dfs_tour(regions, start=0):
    """A continuous walk (real, valid single-step edge crossings only,
    including backtrack steps) visiting every region reachable from
    `start`. Returns (moves, visited) where moves is a list of
    (from_region, direction, to_region)."""
    visited = {start}
    moves = []
    def dfs(cur):
        for d in range(4):
            nxt = regions[cur]['neighbors'][d]
            if nxt is None or nxt in visited:
                continue
            visited.add(nxt)
            moves.append((cur, d, nxt))
            dfs(nxt)
            moves.append((nxt, _T17_OPP[d], cur))
    dfs(start)
    return moves, visited

def _t17_do_move(pb, direction):
    """Performs the memory-forced edge-crossing move for `direction`
    (0=up,1=down,2=left,3=right, REGION_GRAPH's own order) and returns
    (actual_zone, position_ok)."""
    if direction == 3:
        pb.memory[PLAYER_X] = 156; settle(pb)
        return pb.memory[CUR_ZONE], pb.memory[PLAYER_X] <= 20
    if direction == 2:
        pb.memory[PLAYER_X] = 0; settle(pb)
        return pb.memory[CUR_ZONE], pb.memory[PLAYER_X] >= 140
    if direction == 1:
        pb.memory[PLAYER_Y] = 128; settle(pb)
        return pb.memory[CUR_ZONE], pb.memory[PLAYER_Y] <= 40
    pb.memory[PLAYER_Y] = 17; settle(pb)
    return pb.memory[CUR_ZONE], pb.memory[PLAYER_Y] >= 100

# T17.a/T17.d — scale=5 full-world traversal (the direct BL-0047 regression
# test): a graph-driven DFS tour via real button-driven navigation
# (memory-forced edge crossings, matching T9's own established method — not
# force_region_redraw, which only isolates rendering). At every step,
# CUR_ZONE is asserted against worldgen.py's own oracle (T17.a) and the
# entry position against the exact edge constant (T17.d, mirroring
# T9.3/T9.7/T9.9's own tolerance style) — the runtime-driven reachability
# check R305's 2026-07-11 delta (BL-0057) names as necessary, paired with
# (not replacing) T12.c's/T19.b's existing oracle-only checks.
T17_SEED, T17_SCALE = 4242, 5
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]        # MAIN MENU -> new game -> SEED/SCALE ENTRY
enter_seed_scale(pb, [int(c) for c in f"{T17_SEED:05d}"], T17_SCALE)   # -> INTRO
pb.button('a'); [pb.tick() for _ in range(80)]        # INTRO -> PLAYING
check("T17.a0 New game at scale=5 reaches PLAYING", pb.memory[GAMESTATE] == 2,
      f"GS={pb.memory[GAMESTATE]}")

regions = worldgen.generate(T17_SEED, T17_SCALE)
check("T17.a0b Oracle region count == scale^2 (25)", len(regions) == T17_SCALE ** 2,
      f"{len(regions)}")

pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 72
[pb.tick() for _ in range(5)]

t17_moves, t17_visited = _t17_dfs_tour(regions, 0)
zone_bad, pos_bad = [], []
for cur, d, expected in t17_moves:
    actual, pos_ok = _t17_do_move(pb, d)
    if actual != expected:
        zone_bad.append((cur, d, expected, actual))
    if not pos_ok:
        pos_bad.append((cur, d, actual))

check("T17.a Scale=5 graph-driven full-world traversal: every transition matches REGION_GRAPH, oracle-cross-checked (BL-0047 direct regression)",
      len(zone_bad) == 0, f"bad={zone_bad[:3]}")
check("T17.d Entry position correct at every transition (mirrors T9.3/T9.7/T9.9's own tolerance)",
      len(pos_bad) == 0, f"bad={pos_bad[:3]}")
check("T17.a1 Traversal visited every one of the 25 regions via real navigation (FR-9120, runtime-driven)",
      len(t17_visited) == T17_SCALE * T17_SCALE, f"visited={len(t17_visited)}/25")
pb.stop()
wipe_save()

# T17.c — boundary halt: region 24 (bottom-right corner) has no right/down
# neighbor by construction regardless of the maze (a true grid boundary is a
# property of (row,col,scale) alone, unaffected by ADR-0012's maze pass) —
# confirm no transition occurs and CUR_ZONE is unchanged (FR-2310). Reuses a
# real scale=5 new-game (same seed/scale as T17.a) so REGION_GRAPH actually
# holds generated data for region 24 -- forcing CUR_ZONE/WORLD_SCALE alone
# on a scale=3 boot (T16.a's "force region N" pattern) leaves REGION_GRAPH's
# region-24 bytes unpopulated, which previously produced a spurious
# transition off stale WRAM rather than a genuine boundary-halt result.
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
enter_seed_scale(pb, [int(c) for c in f"{T17_SEED:05d}"], T17_SCALE)
pb.button('a'); [pb.tick() for _ in range(80)]
check("T17.c0 Region 24 (scale=5 oracle) genuinely has no right/down neighbor",
      worldgen.generate(T17_SEED, T17_SCALE)[24]['neighbors'][3] is None and
      worldgen.generate(T17_SEED, T17_SCALE)[24]['neighbors'][1] is None, "")
pb.memory[CUR_ZONE] = 24; pb.memory[NEED_REDRAW] = 0
[pb.tick() for _ in range(3)]
pb.memory[PLAYER_X] = 159
settle(pb, 40)
check("T17.c1 No right transition at the true grid edge (region 24)",
      pb.memory[CUR_ZONE] == 24, f"zone={pb.memory[CUR_ZONE]}")
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 128
settle(pb, 40)
check("T17.c2 No down transition at the true grid edge (region 24)",
      pb.memory[CUR_ZONE] == 24, f"zone={pb.memory[CUR_ZONE]}")
pb.stop()
wipe_save()

# T17.b — scale=3 regression: REGION_GRAPH-driven navigation at the default
# fixture (seed=0 normalized to 1, scale=3) must correctly follow whatever
# maze the generator actually produces (IP-1070) — no longer "identical to
# the old full-lattice math" (that assumption is exactly what IP-1070
# retires), but the *mechanism* (check_zone_transition reading REGION_GRAPH)
# must still be bit-for-bit correct against the real generated graph.
pb = fresh_boot()
advance_to_playing(pb)
regions_default = worldgen.generate(1, 3)   # advance_to_playing's own default (seed=0->1, scale=3)

check("T17.b1 Starts in zone 0", pb.memory[CUR_ZONE] == 0, f"zone={pb.memory[CUR_ZONE]}")

t17b_moves, t17b_visited = _t17_dfs_tour(regions_default, 0)
t17b_zone_bad, t17b_pos_bad = [], []
for cur, d, expected in t17b_moves:
    actual, pos_ok = _t17_do_move(pb, d)
    if actual != expected:
        t17b_zone_bad.append((cur, d, expected, actual))
    if not pos_ok:
        t17b_pos_bad.append((cur, d, actual))
check("T17.b2 Scale=3 graph-driven traversal: every transition matches REGION_GRAPH, oracle-cross-checked",
      len(t17b_zone_bad) == 0, f"bad={t17b_zone_bad[:3]}")
check("T17.b3 Entry position correct at every scale=3 transition",
      len(t17b_pos_bad) == 0, f"bad={t17b_pos_bad[:3]}")
check("T17.b4 Scale=3 traversal visited every one of the 9 regions via real navigation",
      len(t17b_visited) == 9, f"visited={len(t17b_visited)}/9")

# T17.b5 — every direction at every visited region matches the oracle
# exactly (open transitions AND blocked/boundary non-transitions alike) —
# subsumes the original suite's specific blocked-case spot-checks (the
# retired T17.b5/b11/b14) with full per-edge coverage instead of 3 samples.
t17b_probe_bad = []
for region in sorted(t17b_visited):
    pb.memory[CUR_ZONE] = region; pb.memory[NEED_REDRAW] = 0
    pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 72
    [pb.tick() for _ in range(3)]
    for d in range(4):
        expected = regions_default[region]['neighbors'][d]
        pb.memory[CUR_ZONE] = region; pb.memory[NEED_REDRAW] = 0
        pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 72
        [pb.tick() for _ in range(3)]
        actual, _ = _t17_do_move(pb, d)
        expected_zone = expected if expected is not None else region
        if actual != expected_zone:
            t17b_probe_bad.append((region, d, expected, actual))
check("T17.b5 Every direction at every scale=3 region matches the oracle (open or blocked/boundary)",
      len(t17b_probe_bad) == 0, f"bad={t17b_probe_bad[:5]}")

pb.stop()
# ══════════════════════════════════════════════════════
# T18 — Main Menu Cursor Fix (IP-9060)
# ══════════════════════════════════════════════════════
print("\n=== T18: Main Menu Cursor Fix ===")

# T18.a — toggle with a valid save present (the direct BL-0048 regression
# test): every step asserts the exact MM_CURSOR value, not just "changed".
pb = fresh_boot(200)
advance_to_playing(pb)
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]   # SAVE -> A -> PLAYING
pb.stop()
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T18.a1 MAIN MENU with a valid save: MM_CURSOR defaults to 0 (continue)",
      pb.memory[MM_CURSOR] == 0, f"cursor={pb.memory[MM_CURSOR]}")
pb.button('down'); [pb.tick() for _ in range(40)]
check("T18.a2 DOWN toggles MM_CURSOR to 1 (BL-0048 direct regression)",
      pb.memory[MM_CURSOR] == 1, f"cursor={pb.memory[MM_CURSOR]}")
pb.button('down'); [pb.tick() for _ in range(40)]
check("T18.a3 DOWN again wraps MM_CURSOR back to 0",
      pb.memory[MM_CURSOR] == 0, f"cursor={pb.memory[MM_CURSOR]}")
pb.button('up'); [pb.tick() for _ in range(40)]
check("T18.a4 UP toggles MM_CURSOR to 1",
      pb.memory[MM_CURSOR] == 1, f"cursor={pb.memory[MM_CURSOR]}")

# T18.d — "new game" is actually reachable end-to-end from this toggled
# state (the full regression test proving the reported symptom is
# resolved, not just that the byte value changes).
pb.button('a'); [pb.tick() for _ in range(40)]
check("T18.d New game reachable: A from MM_CURSOR=1 -> SEED/SCALE ENTRY (GS=7)",
      pb.memory[GAMESTATE] == 7, f"GS={pb.memory[GAMESTATE]}")
pb.stop()
wipe_save()

# T18.b — toggle with no save present: MM_CURSOR forced to 1 ("continue"
# not offered); UP/DOWN are no-ops (mm_toggle's own existing
# MM_SAVE_VALID-gate, unchanged by this package).
pb = fresh_boot(200)
check("T18.b1 MAIN MENU with no save: MM_CURSOR forced to 1",
      pb.memory[MM_CURSOR] == 1, f"cursor={pb.memory[MM_CURSOR]}")
pb.button('up'); [pb.tick() for _ in range(40)]
check("T18.b2 UP is a no-op with no save (MM_SAVE_VALID gate)",
      pb.memory[MM_CURSOR] == 1, f"cursor={pb.memory[MM_CURSOR]}")
pb.button('down'); [pb.tick() for _ in range(40)]
check("T18.b3 DOWN is a no-op with no save",
      pb.memory[MM_CURSOR] == 1, f"cursor={pb.memory[MM_CURSOR]}")
pb.stop()
wipe_save()

# T18.c — genuine re-entry still resets correctly: from MAIN MENU with
# MM_CURSOR toggled to 1 (new game highlighted), navigate away and back
# via a genuine state-entry path (SEED/SCALE ENTRY's B-cancel, T14.c1's
# own path) — confirm MM_CURSOR resets to its correct entry default (0,
# a valid save exists), proving the fix didn't simply delete the reset,
# only mis-scoped it.
pb = fresh_boot(200)
advance_to_playing(pb)
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]   # SAVE -> A -> PLAYING
pb.stop()
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
pb.button('down'); [pb.tick() for _ in range(40)]
check("T18.c1 MM_CURSOR toggled to 1 before navigating away",
      pb.memory[MM_CURSOR] == 1, f"cursor={pb.memory[MM_CURSOR]}")
pb.button('a'); [pb.tick() for _ in range(40)]   # A from cursor=1 -> SEED/SCALE ENTRY
check("T18.c2 Reached SEED/SCALE ENTRY (GS=7)", pb.memory[GAMESTATE] == 7,
      f"GS={pb.memory[GAMESTATE]}")
pb.button('b'); [pb.tick() for _ in range(40)]   # B-cancel -> MAIN MENU (genuine re-entry)
check("T18.c3 B-cancel -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
check("T18.c4 Genuine re-entry resets MM_CURSOR to its correct default (0, save exists)",
      pb.memory[MM_CURSOR] == 0, f"cursor={pb.memory[MM_CURSOR]}")
pb.stop()
wipe_save()

# ══════════════════════════════════════════════════════
# T19 — Maze-Shaped Region Adjacency (IP-1070) — spanning-tree
#       carve + canonical-edge braid/prune pass replacing full-lattice
#       adjacency; ADR-0012/ADR-0013
# ══════════════════════════════════════════════════════
print("\n=== T19: Maze-Shaped Region Adjacency ===")

def _t19_full_lattice_neighbor(i, d, scale):
    """Independently re-derives the true grid-adjacent candidate at region
    index i, direction d (0=up,1=down,2=left,3=right), from (row,col,scale)
    arithmetic alone -- the oracle this Feature's own subgraph guarantee is
    checked against, deliberately not reusing REGION_GRAPH/worldgen.py's own
    candidate computation."""
    row, col = divmod(i, scale)
    if d == 0: return i - scale if row > 0 else None
    if d == 1: return i + scale if row < scale - 1 else None
    if d == 2: return i - 1 if col > 0 else None
    return i + 1 if col < scale - 1 else None

T19_CORPUS = [(seed, scale) for scale in (2, 3, 9) for seed in (0, 1, 42, 12345, 65535)]
# Braid-fraction is a fixed code-level constant this package (FR-9150 Notes:
# UI-exposure deliberately not gating this FR) -- no runtime threshold
# parameter exists to sweep extremes against; the statistical check (T19.e)
# instead aggregates across this same multi-seed/multi-scale corpus.

pb = fresh_boot(180)
t19_oracle_mismatches = []
t19_subgraph_bad = []
t19_unreachable = []
t19_bad_grammar = []
t19_tree_reopened = 0
t19_tree_total = 0
for seed, scale in T19_CORPUS:
    if not invoke_generate_world(pb, seed, scale):
        t19_oracle_mismatches.append((seed, scale, "did not complete"))
        continue
    actual = read_region_graph(pb, scale)
    expected = worldgen.generate(seed, scale)
    if actual != expected:
        bad_idx = [i for i in range(len(actual)) if actual[i] != expected[i]][:3]
        t19_oracle_mismatches.append((seed, scale, f"regions {bad_idx}"))
    n = scale * scale
    for i, r in enumerate(actual):
        for d, nb in enumerate(r['neighbors']):
            if nb is None:
                continue
            full_cand = _t19_full_lattice_neighbor(i, d, scale)
            if nb != full_cand:
                t19_subgraph_bad.append((seed, scale, i, d, nb, full_cand))
    seen = {0}; stack = [0]
    while stack:
        cur = stack.pop()
        for nb in actual[cur]['neighbors']:
            if nb is not None and nb not in seen:
                seen.add(nb); stack.append(nb)
    if len(seen) != n:
        t19_unreachable.append((seed, scale, len(seen), n))
    for i, r in enumerate(actual):
        for nb in r['neighbors']:
            if nb is not None and abs(r['biome_id'] - actual[nb]['biome_id']) > 1:
                t19_bad_grammar.append((seed, scale, i, nb))
    # braid-fraction statistical aggregate: count non-tree candidate edges
    # (grid-adjacent per full-lattice arithmetic, but not present in the
    # spanning tree) that were reopened, vs. the total non-tree candidates,
    # canonical direction (down/right) only so each undirected edge counts once
    tree_edges = set()
    seen2 = {0}; stack2 = [0]
    while stack2:
        cur = stack2.pop()
        for nb in actual[cur]['neighbors']:
            if nb is not None and nb not in seen2:
                tree_edges.add(frozenset((cur, nb)))
                seen2.add(nb); stack2.append(nb)
    for i in range(n):
        for d in (1, 3):
            full_cand = _t19_full_lattice_neighbor(i, d, scale)
            if full_cand is None:
                continue
            edge = frozenset((i, full_cand))
            if edge in tree_edges:
                continue
            t19_tree_total += 1
            if actual[i]['neighbors'][d] is not None:
                t19_tree_reopened += 1
pb.stop()

check("T19.a Subgraph-of-full-lattice: every generated edge also exists in the full grid, every corpus entry (AC-1)",
      len(t19_subgraph_bad) == 0, f"bad={t19_subgraph_bad[:3]}")
check("T19.b Reachability: every region reachable from region 0, every corpus entry (AC-2)",
      len(t19_unreachable) == 0, f"unreachable={t19_unreachable[:3]}")
check("T19.c Determinism/oracle parity: worldgen.py matches SM83 output, every corpus entry (AC-3)",
      len(t19_oracle_mismatches) == 0, f"mismatches={t19_oracle_mismatches[:3]}")
check("T19.d Grammar-validity non-regression: every generated edge legal (|biome_a-biome_b|<=1), every corpus entry (AC-4)",
      len(t19_bad_grammar) == 0, f"bad_edges={t19_bad_grammar[:3]}")
_t19_frac = (t19_tree_reopened / t19_tree_total) if t19_tree_total else 0
check(f"T19.e Braid-fraction statistical check: aggregate reopen fraction within a reasonable band of ~25% target",
      t19_tree_total > 0 and 0.05 <= _t19_frac <= 0.45,
      f"reopened={t19_tree_reopened}/{t19_tree_total} ({_t19_frac:.2%})")

# T19.f -- static determinism audit (AC-6, Inspection): the new maze pass
# (between 'gw_loop's own JP_NZ and the routine's final RET, plus the two new
# helper subroutines) reads no LDH (hardware register, incl. DIV).
with open('asm_game.py') as f:
    _t19_src = f.read()
_t19_maze_start = _t19_src.index("maze-generation pass (IP-1070")
_t19_maze_end = _t19_src.index("── save_to_sram")
_t19_maze_src = _t19_src[_t19_maze_start:_t19_maze_end]
check("T19.f Static audit: no LDH (hardware register, incl. DIV) read in the maze-generation pass (NFR-2200)",
      "LDH_A_n" not in _t19_maze_src and "LDH_A_C" not in _t19_maze_src,
      "source-scanned")

# T19.g -- WRAM headroom audit (AC-7, Inspection): GW_MAZE_STATE..
# GW_MAZE_DRAW_CTR's extent (0xC3A0-0xC3F4, 85 bytes worst case) stays
# inside bank-0 (0xC000-0xCFFF) without SVBK banking.
GW_MAZE_STATE_ADDR = 0xC3A0
GW_MAZE_DRAW_CTR_ADDR = 0xC3F4
check("T19.g WRAM headroom: GW_MAZE_STATE..GW_MAZE_DRAW_CTR extent stays inside bank-0 (NFR-4200)",
      0xC000 <= GW_MAZE_STATE_ADDR and GW_MAZE_DRAW_CTR_ADDR <= 0xCFFF,
      f"GW_MAZE_STATE={hex(GW_MAZE_STATE_ADDR)} extent_end={hex(GW_MAZE_DRAW_CTR_ADDR)}")

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
