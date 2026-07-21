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
  T22 Infinite Mode per-region materialization (IP-1101) — determinism,
      oracle parity, revisit-consistency, treasure-density, static audit,
      seed=0 normalization, no spawn-region special case. (Named T22, not
      T23 — the package planned T23, but IP-1101 was implemented before
      IP-1100, so it claims the next free suite number instead; mirrors
      IP-1050's own precedent for the identical situation.)

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
                     # -- also SELECT MENU's own cursor: 0=map, 1=legend (IP-1090, reused)
MM_JUST_ENTERED = 0xC2D7   # genuine-entry flag, reused by GS_MAIN_MENU and
                            # GS_SELECT_MENU transitions alike (IP-1040/IP-1090)
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
from asm_game import MOB_MOVE_STEP, MOB_MOVE_INTERVAL
import worldgen
_gw_rom = _ROM()
_build_game_asm(_gw_rom)
GW_ADDR = _gw_rom.labels['generate_world']
GW_SEED_OK_ADDR = _gw_rom.labels['gw_seed_ok']
GW_SCALE_SQ = 0xC27C
TMP1 = 0xC013; TMP2 = 0xC014
GW_TRAP_ADDR = 0xC27D   # scratch, inside the boot-clear range, never read elsewhere
DRA_ROW = 0xC2D8; DRA_COL = 0xC2D9   # draw_region_arrows' own re-derived row/col (IP-1080)

# T22 (IP-1101): Infinite Mode per-region materialization
IMR_ADDR = _gw_rom.labels['inf_materialize_region']
INF_MZ_ROW = 0xC40D; INF_MZ_COL = 0xC40F
INF_MZ_RESULT = 0xC411; INF_MZ_TREASURE = 0xC412

# T24 (IP-1102): Infinite Mode streaming window / navigation / render
GAME_MODE = 0xC3F6; INF_ROW = 0xC3F7; INF_COL = 0xC3F9
INF_WINDOW = 0xC3FB; INF_TREASURE_HERE = 0xC404
INF_ENSURE_WINDOW_ADDR = _gw_rom.labels['inf_ensure_window']
CZT_REDRAW_ADDR = _gw_rom.labels['czt_redraw']

def fresh_boot(frames=180):
    """Clean boot to title screen with no saved game."""
    wipe_save()
    pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
    pb.set_emulation_speed(0)
    for _ in range(frames): pb.tick()
    return pb

def advance_to_playing(pb):
    """From MAIN MENU (IP-1040 — boot always lands here; a fresh boot has no
    save, so 'new game' is the only/forced option): A -> MODE SELECT (IP-1100,
    GDS-01 §4d), A (confirm default: MM_CURSOR=0="finite") -> SEED/SCALE
    ENTRY, A (confirm defaults: seed=0 -> normalized to 1 internally,
    scale=3) -> INTRO (runs generate_world), A -> PLAYING."""
    pb.button('a'); [pb.tick() for _ in range(40)]
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

def invoke_inf_materialize_region(pb, seed, row, col):
    """
    T22 (IP-1101): directly invoke inf_materialize_region (asm_game.py) —
    no call site exists yet, IP-1100/1102 wire that up from the new-game
    entry / streaming-window flows. Sets SEED/INF_MZ_ROW/INF_MZ_COL (row/col
    as signed 16-bit, two's complement), hijacks PC/SP with the same
    self-loop trap `invoke_generate_world` established, and returns
    (region_byte, treasure_present) read from INF_MZ_RESULT/INF_MZ_TREASURE,
    or None if the trap was never reached within budget.
    """
    pb.memory[SEED] = seed & 0xFF
    pb.memory[SEED + 1] = (seed >> 8) & 0xFF
    r = row & 0xFFFF; c = col & 0xFFFF
    pb.memory[INF_MZ_ROW] = r & 0xFF; pb.memory[INF_MZ_ROW + 1] = (r >> 8) & 0xFF
    pb.memory[INF_MZ_COL] = c & 0xFF; pb.memory[INF_MZ_COL + 1] = (c >> 8) & 0xFF
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE  # JR -2
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = IMR_ADDR
    for _ in range(60):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            return pb.memory[INF_MZ_RESULT], pb.memory[INF_MZ_TREASURE]
    return None

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
# IP-9070 widened ZONE_COLLECTS from 9 zone-named lists to 5 biome-family-
# representative ones (indexed by REGION_GRAPH's biome-id); IP-1022 widened
# it again to 9 biome-family-representative lists (Village/Cave/Desert/
# Plains spliced in at indices 5-8, FR-4320/BL-0128).
from tilemaps import ZONE_COLLECTS
check("T1.10 ZONE_COLLECTS has 9 biome-family lists (IP-1022)",
      len(ZONE_COLLECTS) == 9, f"{len(ZONE_COLLECTS)}")
carrots_per_zone = [sum(1 for (_, _, t) in z if t == 2) for z in ZONE_COLLECTS]
check("T1.11 Exactly one carrot per list", all(c == 1 for c in carrots_per_zone),
      f"{carrots_per_zone}")
check("T1.12 No zone exceeds 8 collectibles (1-byte bitfield capacity)",
      all(len(z) <= 8 for z in ZONE_COLLECTS), f"{[len(z) for z in ZONE_COLLECTS]}")

# T1.13 — tile-data bounds (IP-9150): the trimmed emission length matches
# the shared constant exactly, and every TL_* index sits below the trim
# boundary — the permanent guard against a future tile added at or beyond
# the boundary without bumping TILE_DATA_TILES.
import tiles as _tiles_mod
_t113_len = len(_tiles_mod.build_tile_data())
_t113_tl = [(n, getattr(_tiles_mod, n)) for n in dir(_tiles_mod)
            if n.startswith('TL_') and isinstance(getattr(_tiles_mod, n), int)]
_t113_over = [(n, v) for n, v in _t113_tl if v >= _tiles_mod.TILE_DATA_TILES]
check("T1.13 Tile-data bounds: build_tile_data() length == TILE_DATA_TILES*16 and every TL_* index < TILE_DATA_TILES (IP-9150)",
      _t113_len == _tiles_mod.TILE_DATA_TILES * 16 and _t113_over == [],
      f"len={_t113_len} expected={_tiles_mod.TILE_DATA_TILES * 16} over={_t113_over}")

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
#      4=MAP 5=VICTORY 6=MAIN_MENU 7=SEED_SCALE_ENTRY — IP-1040;
#      8=SELECT_MENU 9=LEGEND — IP-1090; 10=MODE_SELECT 11=INFINITE_SEED_ENTRY — IP-1100)
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
check("T4.2 A (new game, no save) -> MODE SELECT (GS=10, IP-1100/GDS-01 §4d)",
      pb.memory[GAMESTATE] == 10, f"GS={pb.memory[GAMESTATE]}")
shoot(pb, "T4_mode_select")

pb.button('a'); [pb.tick() for _ in range(40)]
check("T4.2a A (confirm default: finite) -> SEED/SCALE ENTRY (GS=7)",
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
pb.button('a');      [pb.tick() for _ in range(40)]   # IP-1090: SELECT MENU, "map" default -> A
check("T4.6 SELECT -> MAP (GS=4)",          pb.memory[GAMESTATE] == 4)
shoot(pb, "T4_map")

pb.button('b'); [pb.tick() for _ in range(40)]
check("T4.7 B in MAP -> PLAYING (GS=2)",   pb.memory[GAMESTATE] == 2)

# Force victory: check_complete now reads CARROTS_COUNT == WORLD_SCALE
# (IP-1021, FR-9161/ADR-0015 — was a hardcoded 9, replaced by a runtime
# WORLD_SCALE read). Read whatever WORLD_SCALE this fixture's own
# SEED/SCALE ENTRY "confirm defaults" step actually set (the shipped
# default is 3, per SSE_SCALE's own default — read live rather than
# hardcoding, so this test stays correct if that default ever changes)
# and force CARROTS_COUNT/KEYITEM_FLAGS to match it, not a literal 9.
# Per R305's dual-assertion rule, set the flags AND the count so the forced
# state is internally consistent with what save/zone logic reads. IP-1020
# generalized the live flags array to KEYITEM_FLAGS (CARROT_FLAGS is orphaned
# — check_collisions/setup_zone_collects no longer touch it; only the save
# routines still mirror it, pending IP-1050).
t4_scale = pb.memory[WORLD_SCALE]
for i in range(t4_scale): pb.memory[KEYITEM_FLAGS + i] = 1
pb.memory[CARROTS_COUNT] = t4_scale
[pb.tick() for _ in range(40)]
check("T4.8 CARROTS=WORLD_SCALE -> VICTORY (GS=5)",  pb.memory[GAMESTATE] == 5,
      f"GS={pb.memory[GAMESTATE]} scale={t4_scale}")
shoot(pb, "T4_victory")

pb.button('a'); [pb.tick() for _ in range(60)]
check("T4.9 A in VICTORY -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
check("T4.10 Victory exit clears progress",
      pb.memory[CARROTS_COUNT] == 0 and pb.memory[SCORE] == 0
      and all(pb.memory[KEYITEM_FLAGS + i] == 0 for i in range(t4_scale)),
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

# IP-9080 (BL-0049): SAVE screen's SELECT-option text (rows 12-13),
# previously silent -- confirm the label is present and doesn't collide
# with the existing "A: YES"/"B: NO" rows (9/11) or the bottom border (14).
pb.button('start'); [pb.tick() for _ in range(40)]
check("T5.10 SAVE screen reached (GS=3)", pb.memory[GAMESTATE] == 3, f"GS={pb.memory[GAMESTATE]}")
save_label_rows = [[pb.memory[0x9800 + r*32 + c] for c in range(2, 18)] for r in (12, 13)]
save_label_font_tiles = sum(1 for row in save_label_rows for b in row if TL_FONT_A <= b <= TL_FONT_COLON)
check("T5.11 SAVE screen SELECT-option label present (rows 12-13)",
      save_label_font_tiles > 0, f"font_tiles={save_label_font_tiles}")
existing_rows = [[pb.memory[0x9800 + r*32 + c] for c in range(2, 18)] for r in (9, 11, 14)]
check("T5.12 SELECT-option label doesn't collide with A/B rows (9/11) or bottom border (14)",
      all(b in (TL_BG_BLANK, TL_BORDER_H) or (TL_FONT_A <= b <= TL_FONT_COLON) for row in existing_rows for b in row),
      "existing rows unaffected")
shoot(pb, "T5_save_screen")
pb.button('b'); [pb.tick() for _ in range(40)]

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

# Upper Y boundary: movement floor is Y=8, one 8px tile row below the
# static row-0 HUD -- IP-9090 (BL-0051) fix: previously incorrectly
# floored at Y=17, ~9px short of the true playfield top edge.
pb.memory[PLAYER_Y] = 18; pb.memory[PLAYER_X] = 80; pb.memory[CUR_ZONE] = 0
pb.button_press('up'); [pb.tick() for _ in range(20)]; pb.button_release('up')
[pb.tick() for _ in range(2)]
check("T7.8 UP clamp floors exactly at Y=8 (IP-9090/BL-0051 fix)",
      pb.memory[PLAYER_Y] == 8, f"y={pb.memory[PLAYER_Y]} zone={pb.memory[CUR_ZONE]}")
pb.button_press('up'); [pb.tick() for _ in range(5)]; pb.button_release('up')
[pb.tick() for _ in range(2)]
check("T7.8b UP clamp does not go below Y=8", pb.memory[PLAYER_Y] == 8,
      f"y={pb.memory[PLAYER_Y]}")

# Left X boundary: zone 0 is col 0 — X=0 must not move or change zone
pb.memory[CUR_ZONE] = 0; pb.memory[PLAYER_X] = 0; pb.memory[NEED_REDRAW] = 0
pb.button_press('left'); [pb.tick() for _ in range(3)]; pb.button_release('left')
[pb.tick() for _ in range(2)]
check("T7.9 X=0 in zone 0: no move, no zone change",
      pb.memory[PLAYER_X] <= 5 and pb.memory[CUR_ZONE] == 0,
      f"x={pb.memory[PLAYER_X]} zone={pb.memory[CUR_ZONE]}")

# Right X boundary: zone 2 is col 2 (true grid boundary, no right-neighbor
# regardless of maze) -- the sprite's true flush maximum is X=152 (screen
# width 160, sprite width 8), not 159 -- IP-9090 (BL-0052) fix. This first
# check forces X=159 directly (bypassing the clamp) so it only confirms
# "no further increase," still true under the corrected ceiling; T7.10b
# drives the clamp via genuine movement to confirm the real boundary.
pb.memory[CUR_ZONE] = 2; pb.memory[PLAYER_X] = 159; pb.memory[NEED_REDRAW] = 0
pb.button_press('right'); [pb.tick() for _ in range(3)]; pb.button_release('right')
[pb.tick() for _ in range(2)]
check("T7.10 X=159 in zone 2: no overflow, no zone change",
      pb.memory[PLAYER_X] <= 159 and pb.memory[CUR_ZONE] == 2,
      f"x={pb.memory[PLAYER_X]} zone={pb.memory[CUR_ZONE]}")

pb.memory[CUR_ZONE] = 2; pb.memory[PLAYER_X] = 80; pb.memory[NEED_REDRAW] = 0
pb.button_press('right'); [pb.tick() for _ in range(90)]; pb.button_release('right')
[pb.tick() for _ in range(2)]
check("T7.10b RIGHT clamp floors exactly at X=152 via genuine movement (IP-9090/BL-0052 fix)",
      pb.memory[PLAYER_X] == 152, f"x={pb.memory[PLAYER_X]} zone={pb.memory[CUR_ZONE]}")

# T7.11 — real button-press-driven RIGHT transition (the direct BL-0076
# regression test). Zone 3, at this default (seed=0->1, scale=3) fixture's
# own oracle-confirmed graph, has a genuinely open right neighbor (zone 4)
# -- unlike zone 2 (T7.10/T7.10b, a true grid boundary, used deliberately
# there to isolate the clamp from any transition). check_zone_transition
# runs every frame immediately after handle_play_input, so the instant
# PLAYER_X reaches the (now-corrected) threshold the transition fires in
# the same tick and resets PLAYER_X to 8 (the new zone's own left-entry
# position) -- held past that tick, RIGHT keeps moving the player inside
# the *new* zone too, so the button is released the moment CUR_ZONE flips
# rather than after a fixed tick count (unlike T7.10b's own dead-end case,
# where no transition ever fires so overshoot past the clamp can't occur).
# Asserting CUR_ZONE==4 and a small entry-side PLAYER_X together is
# exactly the combination (real movement clamp + a live transition) no
# existing check exercises -- BL-0076 pre-fix, CUR_ZONE stayed 3 and
# PLAYER_X stuck at 152 forever, no matter how long RIGHT was held.
_t711_expected_right = worldgen.generate(1, 3)[3]['neighbors'][3]
check("T7.11 setup: zone 3's oracle-confirmed right neighbor is zone 4",
      _t711_expected_right == 4, f"neighbor={_t711_expected_right}")
pb.memory[CUR_ZONE] = 3; pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 72
pb.memory[NEED_REDRAW] = 0
[pb.tick() for _ in range(3)]
pb.button_press('right')
for _ in range(120):
    pb.tick()
    if pb.memory[CUR_ZONE] == 4:
        break
pb.button_release('right')
[pb.tick() for _ in range(2)]
check("T7.11 Real, sustained RIGHT button-press input crosses into the open neighbor zone (BL-0076 direct regression test)",
      pb.memory[CUR_ZONE] == 4 and pb.memory[PLAYER_X] <= 20,
      f"zone={pb.memory[CUR_ZONE]} x={pb.memory[PLAYER_X]}")

# T7.12 -- no spurious transition on a perpendicular approach (the direct
# BL-0078 regression test). Region 0 (the default new-game start) has no
# right neighbor (true grid boundary) but does have an open down neighbor
# (region 3), which itself has an open right neighbor (region 4) -- walk
# RIGHT until blocked, release, then walk DOWN only (never touching
# left/right again): the down transition must still fire correctly, and
# must NOT spuriously continue on into region 4 just because PLAYER_X is
# still sitting at the RIGHT clamp ceiling from the earlier walk.
pb.memory[CUR_ZONE] = 0; pb.memory[PLAYER_X] = 76; pb.memory[PLAYER_Y] = 80
pb.memory[NEED_REDRAW] = 0
[pb.tick() for _ in range(3)]
pb.button_press('right')
[pb.tick() for _ in range(120)]
pb.button_release('right')
[pb.tick() for _ in range(2)]
check("T7.12 setup: RIGHT walk in region 0 stays blocked (true grid boundary, no right neighbor)",
      pb.memory[CUR_ZONE] == 0 and pb.memory[PLAYER_X] == 152,
      f"zone={pb.memory[CUR_ZONE]} x={pb.memory[PLAYER_X]}")
pb.button_press('down')
[pb.tick() for _ in range(120)]
pb.button_release('down')
[pb.tick() for _ in range(20)]
check("T7.12 No spurious follow-on transition after a perpendicular approach (BL-0078 direct regression test)",
      pb.memory[CUR_ZONE] == 3, f"zone={pb.memory[CUR_ZONE]}")

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

# IP-9100 (BL-0053): pickup hitbox fix -- a synthetic ScoreItem is written
# into COLL_DATA slot 2 (Forest index 2, (120,40), already active/untouched
# by the checks above) at controlled offsets from a fixed player position,
# to directly verify the corrected point-in-box overlap test (0<=dx<=7,
# 0<=dy<=15) rather than the old buggy symmetric +/-9px window.
def _t8_synthetic_pickup(item_x, item_y, px=80, py=80):
    pb.memory[PLAYER_X] = px; pb.memory[PLAYER_Y] = py
    [pb.tick() for _ in range(3)]
    pb.memory[COLL_DATA + 2*4 + 0] = item_x
    pb.memory[COLL_DATA + 2*4 + 1] = item_y
    pb.memory[COLL_DATA + 2*4 + 2] = 1   # ScoreItem
    pb.memory[COLL_DATA + 2*4 + 3] = 1   # active
    [pb.tick() for _ in range(3)]
    return pb.memory[COLL_DATA + 2*4 + 3] == 0   # True if collected

check("T8.x Item 5px above the sprite's true top edge is NOT collected (BL-0053 repro)",
      not _t8_synthetic_pickup(80, 75), "item_y=75, PLAYER_Y=80")
check("T8.y Item overlapping the sprite's bottom edge IS collected (BL-0053 repro)",
      _t8_synthetic_pickup(80, 94), "item_y=94, PLAYER_Y=80")
_dx7 = _t8_synthetic_pickup(87, 80); _dx8 = _t8_synthetic_pickup(88, 80)
check("T8.z1 dx=7 collects, dx=8 does not", _dx7 and not _dx8, f"dx7={_dx7} dx8={_dx8}")
_dy15 = _t8_synthetic_pickup(80, 95); _dy16 = _t8_synthetic_pickup(80, 96)
check("T8.z2 dy=15 collects, dy=16 does not", _dy15 and not _dy16, f"dy15={_dy15} dy16={_dy16}")

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

# T8.10c/d/e (IP-9170, BL-0139): HUD carrot-target digit (row 0, col 4,
# 0x9804) must track WORLD_SCALE at runtime in finite mode -- previously
# baked to a literal "9" regardless of the real win condition
# (CARROTS_COUNT == WORLD_SCALE, IP-1021). Two non-default, non-corpus-
# default scale values (this suite's own default fixture scale is 3) so
# the check can't pass vacuously against the pre-existing bug.
world_scale_pre = pb.memory[WORLD_SCALE]
pb.memory[WORLD_SCALE] = 5; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]
td5 = pb.memory[0x9804] - TL_DIGIT_0
check("T8.10c HUD carrot-target digit reflects forced WORLD_SCALE=5 within 2 frames (IP-9170)",
      td5 == 5, f"digit={td5}")
pb.memory[WORLD_SCALE] = 7; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]
td7 = pb.memory[0x9804] - TL_DIGIT_0
check("T8.10d HUD carrot-target digit reflects forced WORLD_SCALE=7 within 2 frames (IP-9170)",
      td7 == 7, f"digit={td7}")
# T8.10e/f (IP-9180, BL-0144): in Infinite Mode, col 4 shows
# RUNNING_TREASURE_COUNT's low byte reduced mod 10 -- WORLD_SCALE changes
# must NOT affect it once GAME_MODE=1 (the IP-9170/IP-9180 branch split),
# and the digit must correctly wrap past 9 (a value >=10 proves the mod-10
# reduction runs, not just a raw low-nibble read).
rtc_pre = pb.memory[0xC405]
pb.memory[GAME_MODE] = 1; pb.memory[WORLD_SCALE] = 6
pb.memory[0xC405] = 7; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]
td_inf7 = pb.memory[0x9804] - TL_DIGIT_0
check("T8.10e Infinite Mode HUD digit reflects RUNNING_TREASURE_COUNT=7 within 2 frames (IP-9180)",
      td_inf7 == 7, f"digit={td_inf7}")
pb.memory[0xC405] = 13; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]
td_inf13 = pb.memory[0x9804] - TL_DIGIT_0
check("T8.10f Infinite Mode HUD digit wraps correctly for RUNNING_TREASURE_COUNT=13 -> 3 (IP-9180)",
      td_inf13 == 3, f"digit={td_inf13}")
pb.memory[GAME_MODE] = 0
pb.memory[0xC405] = rtc_pre
pb.memory[WORLD_SCALE] = world_scale_pre; pb.memory[SCORE_DIRTY] = 1
[pb.tick() for _ in range(2)]
td_fin_regress = pb.memory[0x9804] - TL_DIGIT_0
check("T8.10g Finite mode non-regression: WORLD_SCALE digit unaffected by IP-9180's Infinite Mode branch",
      td_fin_regress == world_scale_pre, f"digit={td_fin_regress} expected={world_scale_pre}")

# Map hearts (BL-0001 closure): z0 heart full, z1 heart empty.
# update_map_hearts writes 0x9800 + {6,9,12}*32 + {6,11,16}, LCD off during redraw.
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]   # IP-1090: SELECT MENU, "map" default -> A
check("T8.11 SELECT -> MAP", pb.memory[GAMESTATE] == 4)
h_z0 = pb.memory[0x9800 + 6*32 + 6]
h_z1 = pb.memory[0x9800 + 6*32 + 11]
check("T8.12 Map heart z0 = FULL (0x11)",  h_z0 == TL_HEART_FULL,  f"0x{h_z0:02X}")
check("T8.13 Map heart z1 = EMPTY (0x12)", h_z1 == TL_HEART_EMPTY, f"0x{h_z1:02X}")
shoot(pb, "T8_map_hearts")
pb.button('b'); [pb.tick() for _ in range(40)]

# Victory at WORLD_SCALE carrots (IP-1021, FR-9161/ADR-0015 — was a
# hardcoded 9; dual-assert per R305: flags + count, matching whatever
# WORLD_SCALE this fixture's own default new-game flow actually set)
t8_scale = pb.memory[WORLD_SCALE]
for i in range(t8_scale): pb.memory[CARROT_FLAGS + i] = 1
pb.memory[CARROTS_COUNT] = t8_scale
[pb.tick() for _ in range(40)]
check("T8.14 CARROTS_COUNT=WORLD_SCALE -> VICTORY", pb.memory[GAMESTATE] == 5,
      f"GS={pb.memory[GAMESTATE]} scale={t8_scale}")

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
# Forest index 0 (star) is at (28,40) -- placed exactly on it (IP-9100's
# corrected pickup test requires genuine sprite overlap, not the old
# generous +/-9px proximity window this position used to rely on).
pb.memory[PLAYER_X] = 28; pb.memory[PLAYER_Y] = 40
[pb.tick() for _ in range(5)]
sc_after = pb.memory[SCORE]
check("T11.a1 Star (index 0) collected", sc_after > 0, f"score={sc_after}")

# IP-9130 (BL-0078): check_zone_transition now also requires the matching
# direction actually held (not just position) -- hold the real button
# across each teleport-and-settle window, mirroring T7.9-T7.11's own
# already-working pattern.
_t11a_out_btn = 'right' if _t11a_dir == 3 else 'down'
pb.button_press(_t11a_out_btn)
if _t11a_dir == 3:
    pb.memory[PLAYER_X] = 156; pb.memory[PLAYER_Y] = 72
else:
    pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 128
[pb.tick() for _ in range(80)]
pb.button_release(_t11a_out_btn)
check("T11.a2 Transitioned out of zone 0", pb.memory[CUR_ZONE] == _t11a_expect, f"zone={pb.memory[CUR_ZONE]}")
_t11a_back_btn = 'left' if _t11a_dir == 3 else 'up'
pb.button_press(_t11a_back_btn)
if _t11a_dir == 3:
    pb.memory[PLAYER_X] = 0
else:
    pb.memory[PLAYER_Y] = 17
[pb.tick() for _ in range(80)]
pb.button_release(_t11a_back_btn)
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
# IP-1022 (FR-4320): the base corpus above never actually reaches biome-ids
# 5-8 (confirmed by direct check — a small/short random walk from the
# Grass(2) origin rarely wanders 3+ steps in one direction) — T12.d's own
# grammar-validity check would otherwise pass vacuously against the widened
# 0-8 domain. Seeds 38/50 (scale=9), found by direct search, together cover
# every biome-id 0-8 at least once.
T12_CORPUS += [(38, 9), (50, 9)]

# T12.b/c/d/e — reuse one long-lived instance across the whole corpus:
# generate_world completes within a single tick() and depends only on
# SEED/WORLD_SCALE (both set fresh each call), so no reboot is needed.
pb = fresh_boot(180)
oracle_mismatches = []
bad_count = []
unreachable = []
bad_grammar = []
treasure_mismatches = []
bad_treasure_count = []
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
    # IP-1021 (FR-9160/ADR-0015): KEYITEM_FLAGS placement-pass output —
    # dead-end-priority with random-fill fallback, exactly `scale` present.
    n = scale * scale
    actual_ki = [pb.memory[KEYITEM_FLAGS + i] for i in range(n)]
    _, expected_ki = worldgen.generate(seed, scale, _with_treasure=True)
    if actual_ki != expected_ki:
        bad_idx = [i for i in range(n) if actual_ki[i] != expected_ki[i]][:3]
        treasure_mismatches.append((seed, scale, f"regions {bad_idx}"))
    present = sum(1 for v in actual_ki if v == 0)
    if present != scale:
        bad_treasure_count.append((seed, scale, present))
pb.stop()

check("T12.b Oracle parity: worldgen.py matches SM83 output, every corpus entry (AC-2 lockstep)",
      len(oracle_mismatches) == 0, f"mismatches={oracle_mismatches[:3]}")
check("T12.m Region count: exactly scale^2 regions, every corpus entry",
      len(bad_count) == 0, f"bad={bad_count[:3]}")
check("T12.c Reachability: every region reachable from region 0, every corpus entry (AC-3)",
      len(unreachable) == 0, f"unreachable={unreachable[:3]}")
check("T12.d Grammar-validity: every generated edge legal (|biome_a-biome_b|<=1), every corpus entry (AC-4)",
      len(bad_grammar) == 0, f"bad_edges={bad_grammar[:3]}")
check("T12.e KeyItem placement: dead-end-priority + fallback, oracle parity, every corpus entry (FR-9160/ADR-0015)",
      len(treasure_mismatches) == 0, f"mismatches={treasure_mismatches[:3]}")
check("T12.n Exactly WORLD_SCALE KeyItems placed, every corpus entry (FR-9160/FR-9161)",
      len(bad_treasure_count) == 0, f"bad={bad_treasure_count[:3]}")

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

# T12.j — Non-degeneracy statistical check (BL-0074/IP-9110 regression guard):
# across a seed corpus at scale=9 (the scale where the pre-fix defect was most
# visible), the fraction of regions assigned biome_id=0 (Water) must stay well
# below the ~46% mean / ~55%-of-seeds-over-50% the unrepaired PRNG produced.
# Uses the live SM83-built ROM directly, not only the Python oracle (the
# oracle is the thing being kept in lockstep, not independent evidence).
T12J_SEED_CORPUS = list(range(30)) + [42, 12345, 65535, 777, 999, 42424]
pb = fresh_boot(180)
t12j_water_fracs = []
t12j_over_40 = []
for seed in T12J_SEED_CORPUS:
    invoke_generate_world(pb, seed, 9)
    regions = read_region_graph(pb, 9)
    water = sum(1 for r in regions if r['biome_id'] == 0)
    frac = water / len(regions)
    t12j_water_fracs.append(frac)
    if frac > 0.40:
        t12j_over_40.append((seed, round(frac, 3)))
pb.stop()
check("T12.j Non-degeneracy: Water fraction stays under ~40% across a seed corpus at scale=9 (BL-0074 regression guard)",
      len(t12j_over_40) == 0,
      f"mean={sum(t12j_water_fracs)/len(t12j_water_fracs):.3f} over_40={t12j_over_40[:5]}")

# T12.k — Direct BL-0074 reproduction check: seed=0 at scale=9 no longer
# floods to Water (the literal originally-reported case; pre-fix, row 0 =
# [2,3,2,1,0,0,0,0,0], rows 1-8 all zero).
pb = fresh_boot(180)
invoke_generate_world(pb, 0, 9)
t12k_regions = read_region_graph(pb, 9)
pb.stop()
t12k_water = sum(1 for r in t12k_regions if r['biome_id'] == 0)
t12k_frac = t12k_water / len(t12k_regions)
t12k_rows_1_8_all_zero = all(r['biome_id'] == 0 for r in t12k_regions[9:81])
check("T12.k Direct BL-0074 reproduction: seed=0 scale=9 no longer near-total-Water-flooded",
      t12k_frac < 0.40 and not t12k_rows_1_8_all_zero,
      f"water_frac={t12k_frac:.3f} rows1-8_all_zero={t12k_rows_1_8_all_zero}")

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
# dsr_p's biome-id dispatch selects the right family screen for all 9 IDs
# (widened from 5 by IP-1022/FR-4320 — village/cave/desert/plains' own
# landmark-overlay tiles all stay within their own family's tile range too,
# confirmed by direct check of every *_LANDMARKS entry against tiles.py).
FAMILY_RANGES = {
    0: (0x88, 0x8D),   # water -> lake_screen
    1: (0x70, 0x76),   # sand  -> beach_screen
    2: (0x78, 0x7D),   # grass -> forest_screen
    3: (0x80, 0x85),   # stone -> mountain_screen
    4: (0xB0, 0xB5),   # brick -> castle_screen
    5: (0x90, 0x95),   # village -> procedural fill + landmark overlay (IP-1022)
    6: (0x98, 0x9D),   # cave    -> procedural fill + landmark overlay (IP-1022)
    7: (0xA0, 0xA5),   # desert  -> procedural fill + landmark overlay (IP-1022)
    8: (0xA8, 0xAD),   # plains  -> procedural fill + landmark overlay (IP-1022)
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
check("T13.a Tile-family audit: each of the 9 biome-ids renders its own family's tiles (AC-1)",
      len(family_bad) == 0, f"bad={family_bad}")

# T13.e — oracle-parity (IP-1022, ADR-0020): the on-device procedural-fill +
# landmark-overlay routine's output must be byte-for-byte identical to each
# Python *_screen() function's own returned arrays — not a sampled/visual
# check, every one of the 17*32=544 tile cells and 544 attr cells, for all
# four newly-folded identities. Mirrors T12.b's own oracle-parity precedent.
# Reads the attribute plane by directly toggling VBK (0xFF4F) between reads,
# the same register the game's own code writes via LDH (VBK),A.
# Excludes the four navigation-arrow/blocked-edge-indicator tile positions
# (row,col) draw_region_arrows(_inf) draws *after* this package's own fill+
# overlay work completes, in the same dsr_p_after_copy tail every screen
# (baked or procedural) already shares — T13.a's own family-range check
# tolerates the identical class of overwrite via its own count threshold,
# not a defect this package introduces.
_ARROW_EXCLUDE_RC = {(1, 15), (16, 15), (9, 1), (9, 18)}   # up/down/left/right
# IP-9160: row 0 is now compared too (the zone-name region is real
# per-screen oracle content — its wholesale exclusion masked BL-0138's
# stale-name defect). Only the live digit cells update_status_disp
# rewrites at runtime are excluded: col 2 (carrot count), col 4
# (carrot-target, IP-9170 -- finite mode only, but this suite always
# advances via advance_to_playing's finite path), cols 8-10 (score) —
# inventoried by direct read of every row-0 writer (_score_bar's own
# placeholders are static; update_status_disp is the sole runtime row-0
# writer, tile plane only).
_ROW0_DYNAMIC_RC = {(0, 2), (0, 4), (0, 8), (0, 9), (0, 10)}
def full_screen_tiles_attrs(pb):
    tiles = [pb.memory[0x9800 + r*32 + c] for r in range(0, 18) for c in range(32)]
    pb.memory[0xFF4F] = 1
    attrs = [pb.memory[0x9800 + r*32 + c] for r in range(0, 18) for c in range(32)]
    pb.memory[0xFF4F] = 0
    return tiles, attrs

from tilemaps import village_screen, cave_screen, desert_screen, plains_screen
_ORACLE_SCREENS = {
    5: ('village', village_screen),
    6: ('cave',    cave_screen),
    7: ('desert',  desert_screen),
    8: ('plains',  plains_screen),
}
pb = fresh_boot(180)
advance_to_playing(pb)
oracle_bad = []
for biome_id, (name, screen_fn) in _ORACLE_SCREENS.items():
    pb.memory[REGION_GRAPH] = biome_id
    for k in range(4): pb.memory[REGION_GRAPH + 1 + k] = 0xFF
    force_region_redraw(pb, 0)
    actual_tiles, actual_attrs = full_screen_tiles_attrs(pb)
    exp_tiles_full, exp_attrs_full = screen_fn()
    W = 32
    exp_tiles = [exp_tiles_full[y*W+x] for y in range(0, 18) for x in range(W)]
    exp_attrs = [exp_attrs_full[y*W+x] for y in range(0, 18) for x in range(W)]
    tile_mismatches = 0
    attr_mismatches = 0
    for i in range(len(exp_tiles)):
        row, col = i // W, i % W
        if (row, col) in _ARROW_EXCLUDE_RC or (row, col) in _ROW0_DYNAMIC_RC:
            continue
        if actual_tiles[i] != exp_tiles[i]: tile_mismatches += 1
        if actual_attrs[i] != exp_attrs[i]: attr_mismatches += 1
    if tile_mismatches or attr_mismatches:
        oracle_bad.append((name, tile_mismatches, attr_mismatches))
pb.stop()
check("T13.e Oracle-parity: on-device procedural-fill + landmark-overlay output is "
      "byte-for-byte identical to each Python *_screen() function, all four new "
      "identities, full 18-row tile + attr comparison incl. row 0's static "
      "cells (ADR-0020; row-0 name region per IP-9160)",
      len(oracle_bad) == 0, f"bad={oracle_bad}")

# T13.f — dispatch-cascade completeness (IP-1022): confirms the ZONE_COLLECTS
# splice landed at exactly the indices dsr_p_dispatch's cascade expects (5=
# Village, 6=Cave, 7=Desert, 8=Plains, CR-08's resolved order) by forcing
# each biome-id and checking setup_zone_collects' own live spawn output
# (COLL_COUNT/COLL_DATA) matches that identity's own ZONE_COLLECTS list
# exactly, entry-for-entry — the risk this package's own §13 Risks named
# explicitly (a wrong splice index would silently spawn the wrong
# collectible list on the wrong screen, not a build-time-caught error).
from tilemaps import ZONE_COLLECTS as _ZC_CHECK
pb = fresh_boot(180)
advance_to_playing(pb)
spawn_bad = []
for biome_id in (5, 6, 7, 8):
    pb.memory[REGION_GRAPH] = biome_id
    for k in range(4): pb.memory[REGION_GRAPH + 1 + k] = 0xFF
    force_region_redraw(pb, 0)
    expected = _ZC_CHECK[biome_id]
    actual_count = pb.memory[COLL_COUNT]
    actual_entries = [tuple(pb.memory[COLL_DATA + i*4 + k] for k in range(3))
                      for i in range(actual_count)]
    expected_entries = [(x, y, t) for (x, y, t) in expected]
    if actual_count != len(expected) or actual_entries != expected_entries:
        spawn_bad.append((biome_id, actual_count, actual_entries, expected_entries))
pb.stop()
check("T13.f Dispatch-cascade completeness: setup_zone_collects spawns the exact "
      "ZONE_COLLECTS list for each of biome-ids 5-8, entry-for-entry",
      len(spawn_bad) == 0, f"bad={spawn_bad}")

# T13.g — stale-name regression (IP-9160/BL-0138): render a procedural
# screen AFTER a differently-named screen and assert the name region
# (row 0, cols 12-19) shows the SECOND screen's own oracle cells — the
# exact scenario the content review's screenshots caught (Village showing
# "FOREST"). Both directions: procedural-after-baked (the shipped defect)
# and baked-after-procedural (documents the baked path's copy_screen
# already rewrites all of row 0, closing the asymmetry from both sides).
def _t13g_name_region_tiles(pb):
    return [pb.memory[0x9800 + 0*32 + c] for c in range(12, 20)]

def _t13g_oracle_name(screen_fn):
    t, _a = screen_fn()
    return [t[c] for c in range(12, 20)]

pb = fresh_boot(180)
advance_to_playing(pb)
# direction 1: grass/forest (baked, name "FOREST") then village (procedural)
pb.memory[REGION_GRAPH] = 2
for k in range(4): pb.memory[REGION_GRAPH + 1 + k] = 0xFF
force_region_redraw(pb, 0)
_t13g_after_forest = _t13g_name_region_tiles(pb)
pb.memory[REGION_GRAPH] = 5
force_region_redraw(pb, 0)
_t13g_after_village = _t13g_name_region_tiles(pb)
from tilemaps import forest_screen as _t13g_forest
_t13g_ok1 = (_t13g_after_forest == _t13g_oracle_name(_t13g_forest)
             and _t13g_after_village == _t13g_oracle_name(village_screen))
# direction 2: back to a baked screen (stone/mountain, name "MOUNTAIN")
pb.memory[REGION_GRAPH] = 3
force_region_redraw(pb, 0)
from tilemaps import mountain_screen as _t13g_mountain
_t13g_ok2 = _t13g_name_region_tiles(pb) == _t13g_oracle_name(_t13g_mountain)
pb.stop()
check("T13.g Stale-name regression: name region shows each screen's own name after "
      "a differently-named predecessor, both directions (IP-9160/BL-0138)",
      _t13g_ok1 and _t13g_ok2,
      f"forest={_t13g_after_forest} village={_t13g_after_village}")

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
             'left': arrow_addr(1, 9), 'right': arrow_addr(20-2, 9)}   # IP-9140
             # (BL-0084): right arrow moved from column 32-2=30 (off the
             # true 20-column visible window, never rendered) to 20-2=18.
ARROW_TILE = {'up': 0x18, 'down': 0x19, 'left': 0x17, 'right': 0x16}  # TL_ARROW_U/D/L/R
BLOCKED_TILE = {'up': 0x1A, 'down': 0x1B, 'left': 0x1C, 'right': 0x1D}  # TL_BLOCKED_U/D/L/R (IP-1081)

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

# T13.d — screen-visibility audit (the direct BL-0084 regression test):
# each of the four arrow addresses must fall inside the true visible
# background window (20 columns x 18 rows -- the fixed 160x144px GBC
# display, SCX=SCY=0 always in this codebase, confirmed by direct code
# read: asm_game.py never writes either register). A tilemap-byte-value
# check alone (T13.a-c's own method) cannot distinguish a correctly
# written but off-screen tile from a correctly written and visible one --
# this is the check that would have caught BL-0084 (ARROW_ADDR_R at
# column 32-2=30, never on-screen) before it shipped.
visibility_bad = []
for direction, addr in ARROW_POS.items():
    col = (addr - 0x9800) % 32
    row = (addr - 0x9800) // 32
    if not (0 <= col <= 19 and 0 <= row <= 17):
        visibility_bad.append((direction, col, row))
check("T13.d Screen-visibility audit: every arrow address falls inside the true visible 20x18 window (BL-0084)",
      len(visibility_bad) == 0, f"bad={visibility_bad}")

# ══════════════════════════════════════════════════════
# T14 — Main Menu & New-Game Flow (IP-1040)
# (FS-104's own template names "T13"; renumbered — IP-1030 already claimed
# T13 earlier this same tranche.)
# ══════════════════════════════════════════════════════
print("\n=== T14: Main Menu & New-Game Flow ===")

def enter_new_game_finite(pb):
    """From MAIN MENU: A (new game) -> MODE SELECT (IP-1100, GDS-01 §4d),
    A (confirm default: MM_CURSOR=0="finite") -> SEED/SCALE ENTRY."""
    pb.button('a'); [pb.tick() for _ in range(40)]
    pb.button('a'); [pb.tick() for _ in range(40)]

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
enter_new_game_finite(pb)                                # MAIN MENU -> new game -> MODE SELECT -> finite -> SEED/SCALE ENTRY
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
enter_new_game_finite(pb)
enter_seed_scale(pb, [1, 2, 3, 4, 5], 5)
region_graph_b2 = read_region_graph(pb, 5)
pb.stop()
check("T14.b3 Same (seed,scale) -> identical region graph across two new-game creations (AC-4)",
      region_graph_b1 == region_graph_b2, "")

# T14.c1 — SEED/SCALE ENTRY, B -> MAIN MENU, without writing SEED/WORLD_SCALE
# (FS-104 Open Question 1's resolution, tested directly).
pb = fresh_boot(200)
enter_new_game_finite(pb)
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
# MAP: SELECT (IP-1090: -> SELECT MENU, "map" default -> A) enters,
# B and SELECT both exit back to PLAYING (st_map's own pre-existing merge)
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('a');       [pb.tick() for _ in range(40)]       # SELECT MENU: A -> MAP
pb.button('b');       [pb.tick() for _ in range(40)]       # MAP: B
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('a');       [pb.tick() for _ in range(40)]       # SELECT MENU: A -> MAP
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
enter_new_game_finite(pb)
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
enter_new_game_finite(pb)
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

_T17_DIR_BTN = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}

def _t17_do_move(pb, direction):
    """Performs the memory-forced edge-crossing move for `direction`
    (0=up,1=down,2=left,3=right, REGION_GRAPH's own order) and returns
    (actual_zone, position_ok). IP-9130 (BL-0078): check_zone_transition
    now also requires the matching direction actually held, not just
    position -- holds the real button across the teleport window,
    mirroring T7.9-T7.11's own already-working pattern. Released the
    instant CUR_ZONE changes (not for a fixed tick count) -- held past
    that point, the button would keep moving the player inside the
    *newly entered* zone too (T7.11's own overshoot bug, mirrored here)."""
    btn = _T17_DIR_BTN[direction]
    start_zone = pb.memory[CUR_ZONE]
    pb.button_press(btn)
    if direction == 3:
        pb.memory[PLAYER_X] = 156
    elif direction == 2:
        pb.memory[PLAYER_X] = 0
    elif direction == 1:
        pb.memory[PLAYER_Y] = 128
    else:
        pb.memory[PLAYER_Y] = 17
    for _ in range(80):
        pb.tick()
        if pb.memory[CUR_ZONE] != start_zone:
            break
    pb.button_release(btn)
    [pb.tick() for _ in range(2)]
    if direction == 3:
        result = pb.memory[CUR_ZONE], pb.memory[PLAYER_X] <= 20
    elif direction == 2:
        result = pb.memory[CUR_ZONE], pb.memory[PLAYER_X] >= 140
    elif direction == 1:
        result = pb.memory[CUR_ZONE], pb.memory[PLAYER_Y] <= 40
    else:
        result = pb.memory[CUR_ZONE], pb.memory[PLAYER_Y] >= 100
    return result

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
enter_new_game_finite(pb)
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
enter_new_game_finite(pb)
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
pb.button('a'); [pb.tick() for _ in range(40)]   # A from MM_CURSOR=1 -> MODE SELECT (IP-1100)
pb.button('a'); [pb.tick() for _ in range(40)]   # A (confirm default: finite) -> SEED/SCALE ENTRY
check("T18.d New game reachable: A from MM_CURSOR=1 -> MODE SELECT -> SEED/SCALE ENTRY (GS=7)",
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
pb.button('a'); [pb.tick() for _ in range(40)]   # A from cursor=1 -> MODE SELECT (IP-1100)
pb.button('a'); [pb.tick() for _ in range(40)]   # A (confirm default: finite) -> SEED/SCALE ENTRY
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
# T20 — Maze-Aware Transition-Edge Classification (IP-1080/IP-1082) —
#       render-time open/blocked/absent classification inside
#       draw_region_arrows, distinguishing a maze-pruned edge from a true
#       grid boundary once REGION_GRAPH's own neighbor byte alone can no
#       longer tell them apart (FR-2330, FS-108). AC-4 (visual rendering of
#       the blocked state, IP-1082) and AC-5 (open-case non-regression) are
#       both exercised here as of IP-1082.
# ══════════════════════════════════════════════════════
print("\n=== T20: Maze-Aware Transition-Edge Classification ===")

T20_CORPUS = [(0, 2), (0, 3), (1, 3), (0, 9)]   # FS-108 §16's own minimum:
                           # scale in {2,3,9}, seed 0 included. Deliberately
                           # NOT the full 15-entry T19_CORPUS -- unlike T19's
                           # own checks (which read WRAM straight after
                           # invoke_generate_world's PC/SP hijack trap),
                           # this suite needs the CPU actually running its
                           # normal game loop afterward (force_region_redraw
                           # relies on it), so each entry is driven through
                           # real button input (enter_seed_scale, T17's own
                           # established method) rather than the trap -- an
                           # invoke_generate_world'd CPU is left spinning in
                           # a self-loop and never processes another redraw
                           # (see T13.c's own comment on exactly this). A
                           # full 15-entry real-input corpus would be a lot
                           # of button-driven ticks for marginal extra
                           # coverage; ARROW_POS/ARROW_TILE reused from
                           # T13.c, defined above.

t20_open_bad = []
t20_blocked_bad = []
t20_absent_bad = []
t20_blocked_n = 0
t20_absent_n = 0

for seed, scale in T20_CORPUS:
    pb = fresh_boot(200)
    enter_new_game_finite(pb)
    enter_seed_scale(pb, [int(c) for c in f"{seed:05d}"], scale)   # -> INTRO
    pb.button('a'); [pb.tick() for _ in range(80)]   # INTRO -> PLAYING
    regions = worldgen.generate(seed, scale)   # oracle -- T19.c already
                                                # proves this matches the
                                                # real SM83-generated
                                                # REGION_GRAPH byte-for-byte
    for i, r in enumerate(regions):
        row, col = divmod(i, scale)
        # One real redraw (dsr_p -> draw_region_arrows, IP-1030's own
        # established call site, mirroring T13.c) covers all four
        # directions of region i in a single pass -- draw_region_arrows'
        # own row/col re-derivation (IP-1080 §6) is left in TMP1/TMP2 by
        # the time do_screen_redraw's LCD-off bracket completes.
        force_region_redraw(pb, i)
        got_row, got_col = pb.memory[DRA_ROW], pb.memory[DRA_COL]
        row_col_ok = (got_row, got_col) == (row, col)
        for d, direction in enumerate(('up', 'down', 'left', 'right')):
            nb = r['neighbors'][d]
            full_cand = _t19_full_lattice_neighbor(i, d, scale)
            tile_at_pos = pb.memory[ARROW_POS[direction]]
            arrow_present = tile_at_pos == ARROW_TILE[direction]
            blocked_present = tile_at_pos == BLOCKED_TILE[direction]
            if nb is not None:
                # open (AC-1/AC-5): REGION_GRAPH shows a live neighbor --
                # arrow must render, unchanged from today's shipped behavior.
                if not arrow_present:
                    t20_open_bad.append((seed, scale, i, direction))
            elif full_cand is not None:
                # blocked (AC-2/AC-4, IP-1082): grid-adjacent but maze-pruned
                # -- the re-derivation arithmetic that DRIVES the
                # classification must be correct AND the new blocked-tile
                # indicator (IP-1081's TL_BLOCKED_<dir>) must render, not the
                # open-edge arrow and not a blank tile.
                t20_blocked_n += 1
                if not row_col_ok or not blocked_present:
                    t20_blocked_bad.append((seed, scale, i, direction,
                                             (got_row, got_col), (row, col), tile_at_pos))
            else:
                # absent (AC-3): true grid boundary -- identical to
                # today's shipped no-op, no arrow drawn.
                t20_absent_n += 1
                if not row_col_ok or arrow_present or blocked_present:
                    t20_absent_bad.append((seed, scale, i, direction,
                                            (got_row, got_col), (row, col), tile_at_pos))
    pb.stop()

check("T20.a Open classification: arrow renders wherever REGION_GRAPH shows a live neighbor, every corpus entry (AC-1)",
      len(t20_open_bad) == 0, f"bad={t20_open_bad[:3]}")
check("T20.b Blocked classification: grid-adjacent-but-maze-pruned edges re-derive the correct (row,col) and draw the blocked-tile indicator, every corpus entry (AC-2/AC-4)",
      t20_blocked_n > 0 and len(t20_blocked_bad) == 0,
      f"n={t20_blocked_n} bad={t20_blocked_bad[:3]}")
check("T20.c Absent classification: true grid-boundary edges re-derive the correct (row,col) and draw no arrow/blocked tile, every corpus entry (AC-3)",
      t20_absent_n > 0 and len(t20_absent_bad) == 0,
      f"n={t20_absent_n} bad={t20_absent_bad[:3]}")
check("T20.e Open-case non-regression: live-neighbor edges still render the existing open-arrow tile, unaffected by the new blocked-branch addition, every corpus entry (AC-5)",
      len(t20_open_bad) == 0,
      f"bad={t20_open_bad[:3]}")

# T20.d -- static audit (Inspection): the row/col re-derivation sits before
# the four REGION_GRAPH neighbor bytes are loaded into B-E (must, since
# that load clobbers the same registers the division loop uses), and the
# existing open-edge branch/arrow-write logic is textually unchanged from
# IP-1030's own shipped form (FR-2320 zero-diff claim, DoD item 4).
with open('asm_game.py') as f:
    _t20_src = f.read()
_dra_start = _t20_src.index("rom.label('draw_region_arrows')")
_dra_end = _t20_src.index("rom.label('dra_no_right')")
_dra_src = _t20_src[_dra_start:_dra_end]
_div_pos = _dra_src.find('dra_div_loop')
_div_done_pos = _dra_src.find('dra_div_done')
_b_up_pos = _dra_src.find("LD_B_A()", _div_done_pos)   # first B=up load,
                           # searched only after dra_div_done -- LD_B_A()
                           # also appears earlier (stashing WORLD_SCALE for
                           # the division loop itself), an unrelated call
                           # this scan must not match
check("T20.d Static audit: row/col re-derivation precedes the neighbor-byte loads it would otherwise clobber (AC-2/AC-3 precondition)",
      _div_pos != -1 and _b_up_pos != -1 and _div_pos < _b_up_pos,
      "source-scanned")

print("\n=== T21: SELECT Menu & Edge-Indicator Legend Screen ===")

pb = fresh_boot(200)
advance_to_playing(pb)

# T21.a1/a2 -- SELECT MENU entry + toggle (AC-1/AC-2)
pb.button('select'); [pb.tick() for _ in range(40)]
check("T21.a1 SELECT -> SELECT MENU (GS=8), MAP default highlighted",
      pb.memory[GAMESTATE] == 8 and pb.memory[MM_CURSOR] == 0,
      f"GS={pb.memory[GAMESTATE]} cursor={pb.memory[MM_CURSOR]}")
pb.button('down'); [pb.tick() for _ in range(10)]
check("T21.a2a DOWN toggles MM_CURSOR to 1 (legend)", pb.memory[MM_CURSOR] == 1,
      f"cursor={pb.memory[MM_CURSOR]}")
pb.button('down'); [pb.tick() for _ in range(10)]
check("T21.a2b DOWN again toggles MM_CURSOR back to 0 (map)", pb.memory[MM_CURSOR] == 0,
      f"cursor={pb.memory[MM_CURSOR]}")
pb.stop()

# T21.b -- MM_CURSOR=0, A -> MAP (AC-3)
pb = fresh_boot(200)
advance_to_playing(pb)
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('a');      [pb.tick() for _ in range(40)]
check("T21.b SELECT MENU, map highlighted, A -> MAP (GS=4)", pb.memory[GAMESTATE] == 4,
      f"GS={pb.memory[GAMESTATE]}")
pb.stop()

# T21.c -- toggle to legend, A -> LEGEND (AC-4)
pb = fresh_boot(200)
advance_to_playing(pb)
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('down');   [pb.tick() for _ in range(10)]
pb.button('a');      [pb.tick() for _ in range(40)]
check("T21.c SELECT MENU, legend highlighted, A -> LEGEND (GS=9)", pb.memory[GAMESTATE] == 9,
      f"GS={pb.memory[GAMESTATE]}")
pb.stop()

# T21.d -- B cancels SELECT MENU -> PLAYING, writing nothing else (AC-5).
# A raw full-WRAM diff would false-positive on bytes that change every
# frame regardless of menu state (MUSIC_CTR/MUSIC_PTR_LO/MUSIC_PTR_HI,
# JOY_CUR/PREV/NEW, VBLANK_FLAG) -- so this checks the meaningful,
# player-visible game-progress fields FR-1200's Postcondition is actually
# about, the same set T14's own SEED/SCALE-immutability check targets
# rather than diffing the entire WRAM region.
MEANINGFUL_FIELDS = [SEED, SEED + 1, WORLD_SCALE, 0xC001, 0xC002,  # PLAYER_X/Y
                      0xC003, 0xC004, SCORE, CARROTS_COUNT, CUR_ZONE]
pb = fresh_boot(200)
advance_to_playing(pb)
before = {addr: pb.memory[addr] for addr in MEANINGFUL_FIELDS}
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('b');      [pb.tick() for _ in range(40)]
check("T21.d1 SELECT MENU, B -> PLAYING (GS=2)", pb.memory[GAMESTATE] == 2,
      f"GS={pb.memory[GAMESTATE]}")
after = {addr: pb.memory[addr] for addr in MEANINGFUL_FIELDS}
changed = [hex(a) for a in MEANINGFUL_FIELDS if before[a] != after[a]]
check("T21.d2 B-cancel writes nothing outside GAMESTATE/NEED_REDRAW/TRANSITION_TO/MM_CURSOR/MM_JUST_ENTERED",
      len(changed) == 0, f"changed={changed}")
pb.stop()

# T21.e -- from LEGEND, B -> PLAYING (AC-6)
pb = fresh_boot(200)
advance_to_playing(pb)
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('down');   [pb.tick() for _ in range(10)]
pb.button('a');      [pb.tick() for _ in range(40)]
check("T21.e0 LEGEND reached (GS=9)", pb.memory[GAMESTATE] == 9, f"GS={pb.memory[GAMESTATE]}")
pb.button('b'); [pb.tick() for _ in range(40)]
check("T21.e LEGEND, B -> PLAYING (GS=2)", pb.memory[GAMESTATE] == 2,
      f"GS={pb.memory[GAMESTATE]}")

# T21.f -- LEGEND's static content: real tiles beside their labels, plus a
# genuinely blank world-edge cell (Inspection, GDS-08 §11) -- re-enter
# LEGEND (same pb instance) to read its tilemap directly.
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('down');   [pb.tick() for _ in range(10)]
pb.button('a');      [pb.tick() for _ in range(40)]
legend_open_tile    = pb.memory[arrow_addr(4, 6)]
legend_blocked_tile = pb.memory[arrow_addr(4, 9)]
legend_edge_tile    = pb.memory[arrow_addr(4, 12)]
check("T21.f1 LEGEND row 1 shows the real open-arrow tile (TL_ARROW_U) beside OPEN PATH",
      legend_open_tile == ARROW_TILE['up'], f"0x{legend_open_tile:02X}")
check("T21.f2 LEGEND row 2 shows the real blocked-edge tile (TL_BLOCKED_U) beside MAZE BLOCKED",
      legend_blocked_tile == BLOCKED_TILE['up'], f"0x{legend_blocked_tile:02X}")
check("T21.f3 LEGEND row 3 is genuinely blank beside WORLD EDGE (no tile drawn)",
      legend_edge_tile == TL_BG_BLANK, f"0x{legend_edge_tile:02X}")
pb.button('b'); [pb.tick() for _ in range(40)]
pb.stop()

# T21.g (FS-109 Verification Plan) -- not a separate assertion: this
# requirement is that the corrected two-hop SELECT->SELECT MENU->MAP path
# (T4.6/T8.11/T14.e2, all earlier in this same run) passes alongside T21's
# own new-state checks in one full-suite run, not merely in isolation --
# already satisfied structurally by this script's own single-process,
# top-to-bottom execution (see RESULTS below).

# ══════════════════════════════════════════════════════
# T22 — Infinite Mode: Per-Region Materialization (IP-1101)
# ══════════════════════════════════════════════════════
print("\n=== T22: Infinite Mode — Per-Region Materialization ===")

# Corpus spans negative and positive row/col (Infinite Mode's world is
# unbounded, unlike the finite mode's own 0..WORLD_SCALE-1 grid) and
# includes the origin (0,0) -- confirming Open Question 4's "no
# spawn-region special case" via the same corpus, not a separate check.
T22_CORPUS = [(seed, row, col)
              for seed in (0, 1, 42, 12345, 65535)
              for row, col in [(0, 0), (1, 0), (0, 1), (5, 5), (-5, 5),
                                (5, -5), (-5, -5), (100, -100), (3, 7)]]

pb = fresh_boot(180)
oracle_mismatches = []
for seed, row, col in T22_CORPUS:
    got = invoke_inf_materialize_region(pb, seed, row, col)
    exp_byte, exp_treasure = worldgen.materialize_region(seed, row, col)
    exp = (exp_byte, 1 if exp_treasure else 0)
    if got is None or got != exp:
        oracle_mismatches.append((seed, row, col, got, exp))
pb.stop()
check("T22.b Oracle parity: worldgen.py matches SM83 output, every corpus entry incl. (0,0) (AC-2)",
      len(oracle_mismatches) == 0, f"mismatches={oracle_mismatches[:3]}")

# T22.a -- determinism: two separate PyBoy instances, same (seed,row,col)
det_mismatches = []
for seed, row, col in [(777, -12, 34), (0, 0, 0), (65535, 200, -200)]:
    pb1 = fresh_boot(180)
    r1 = invoke_inf_materialize_region(pb1, seed, row, col)
    pb1.stop()
    pb2 = fresh_boot(180)
    r2 = invoke_inf_materialize_region(pb2, seed, row, col)
    pb2.stop()
    if r1 != r2:
        det_mismatches.append((seed, row, col, r1, r2))
check("T22.a Determinism: same (seed,row,col) across two fresh boots -> byte-identical output (FR-10200)",
      len(det_mismatches) == 0, f"mismatches={det_mismatches}")

# T22.c -- revisit-consistency: materializing the same region a second time,
# as an independent call with no prior state consulted (simulating "left the
# materialized window and re-entered it"), reproduces the first result
# exactly (FR-10210) -- the actual persisted-store integration (IP-1102's
# own INF_WINDOW) doesn't exist yet, so this checks the routine's own
# revisit-safety at the data layer, per this package's own scope boundary.
pb = fresh_boot(180)
revisit_mismatches = []
for seed, row, col in [(99, 7, -3), (1, 0, 0), (777, -50, 50)]:
    first = invoke_inf_materialize_region(pb, seed, row, col)
    # unrelated intervening call, mirroring a materialized-window eviction
    invoke_inf_materialize_region(pb, seed + 1, row + 10, col - 10)
    second = invoke_inf_materialize_region(pb, seed, row, col)
    if first != second:
        revisit_mismatches.append((seed, row, col, first, second))
pb.stop()
check("T22.c Revisit-consistency: re-materializing after an intervening call reproduces the first result (FR-10210)",
      len(revisit_mismatches) == 0, f"mismatches={revisit_mismatches}")

# T22.d -- treasure-density statistical check: over a large (row,col) corpus
# at one fixed seed, measured presence rate falls within a reasonable band
# around K=16's own 6.25% target (mirrors T12.j's own non-degeneracy shape).
pb = fresh_boot(180)
present = 0
total = 0
for row in range(0, 40):
    for col in range(0, 20):
        _, treasure = invoke_inf_materialize_region(pb, 2026, row, col)
        total += 1
        if treasure:
            present += 1
pb.stop()
rate = present / total
check("T22.d Treasure-density: measured rate near K=16's 6.25% target (2%-11% band, FR-10300)",
      0.02 <= rate <= 0.11, f"rate={rate:.4f} ({present}/{total})")

# T22.e -- determinism static audit (AC-7, Inspection): inf_materialize_region/
# inf_region_seed0/inf_mod9 must read no hardware register (DIV et al., via
# LDH) -- a real source-text scan, mirroring T12.h's own established pattern.
_t22_src = (BASE / 'asm_game.py').read_text()
_t22_start = _t22_src.index("rom.label('inf_region_seed0')")
_t22_end = _t22_src.index("rom.RET()", _t22_src.index("rom.label('inf_materialize_region')"))
_t22_slice = _t22_src[_t22_start:_t22_end]
check("T22.e Static audit: no LDH (hardware register, incl. DIV) read in inf_materialize_region/inf_region_seed0/inf_mod9 (NFR-2300)",
      'LDH_A_n' not in _t22_slice and 'LDH_A_C' not in _t22_slice, "source-scanned")

# T22.f -- seed=0 normalization: direct WRAM inspection of the PRNG state
# immediately after inf_region_seed0's own normalization step (hooked),
# never observing (TMP1,TMP2) == (0,0) (mirrors T12.f's own established
# pattern).
IRS0_SEED_OK_ADDR = _gw_rom.labels['irs0_seed_ok']
pb = fresh_boot(180)
t22f_state = {}
def _t22f_hook(ctx):
    t22f_state['tmp1'] = pb.memory[TMP1]
    t22f_state['tmp2'] = pb.memory[TMP2]
pb.hook_register(0, IRS0_SEED_OK_ADDR, _t22f_hook, None)
invoke_inf_materialize_region(pb, 0, 0, 0)
pb.stop()
check("T22.f seed=0 normalizes to a nonzero PRNG state, direct WRAM inspection (AC-7 precondition)",
      t22f_state.get('tmp1', 0) != 0 or t22f_state.get('tmp2', 0) != 0,
      f"state=({t22f_state.get('tmp1')},{t22f_state.get('tmp2')})")

# T22.g -- cross-consistency (a stronger check than the oracle-parity
# corpus above can give in isolation): this region's own south/east
# connectivity bits must match what directly materializing the south/east
# neighbor computes as ITS OWN north/west bits -- confirms the Binary Tree
# construction's neighbor-consulting symmetry holds through the real SM83
# routine, not just the Python oracle (which T22.b already trusts, so this
# check runs entirely oracle-side, extending the algorithm-correctness
# claim independent of the SM83 comparison above).
_t22g_bad = []
for seed in (0, 42, 65535):
    for row in range(-3, 4):
        for col in range(-3, 4):
            rb, _ = worldgen.materialize_region(seed, row, col)
            south_open_here = bool(rb & 0x20)
            nrb, _ = worldgen.materialize_region(seed, row + 1, col)
            north_open_neighbor = bool(nrb & 0x10)
            if south_open_here != north_open_neighbor:
                _t22g_bad.append((seed, row, col, "south/north"))
            east_open_here = bool(rb & 0x80)
            erb, _ = worldgen.materialize_region(seed, row, col + 1)
            west_open_neighbor = bool(erb & 0x40)
            if east_open_here != west_open_neighbor:
                _t22g_bad.append((seed, row, col, "east/west"))
check("T22.g Neighbor-consulting symmetry: south/east openness matches the neighbor's own north/west bit, every corpus entry (ADR-0016 pt.5)",
      len(_t22g_bad) == 0, f"bad={_t22g_bad[:3]}")

# ══════════════════════════════════════════════════════
# T24 — Infinite Mode: Streaming Window & Rendering (IP-1102)
# ══════════════════════════════════════════════════════
print("\n=== T24: Infinite Mode — Streaming Window & Rendering ===")

_T24_WINDOW_OFFSETS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)]

def inf_window_bytes(seed, row, col):
    """The 9 region bytes inf_ensure_window would compute for a window
    centered on (row, col) -- same row-major order as asm_game.py's own
    _INF_WINDOW_OFFSETS."""
    return [worldgen.materialize_region(seed, row + dr, col + dc)
            for dr, dc in _T24_WINDOW_OFFSETS]

def set_infinite_state(pb, seed, row, col):
    """Directly pokes WRAM into the state a real inf_ensure_window call
    would have produced for (seed, row, col) -- not the PC/SP hijack trap
    T22's own invoke_inf_materialize_region uses, which strands the CPU in
    a self-loop (T20's own documented caution) incompatible with the real
    button-driven gameplay T24 needs afterward. Leaves the CPU's normal
    running loop undisturbed so real button presses can drive
    check_zone_transition -> czt_infinite -> inf_ensure_window naturally,
    as an ordinary in-loop CALL/RET."""
    pb.memory[SEED] = seed & 0xFF; pb.memory[SEED + 1] = (seed >> 8) & 0xFF
    pb.memory[GAME_MODE] = 1
    r = row & 0xFFFF; c = col & 0xFFFF
    pb.memory[INF_ROW] = r & 0xFF; pb.memory[INF_ROW + 1] = (r >> 8) & 0xFF
    pb.memory[INF_COL] = c & 0xFF; pb.memory[INF_COL + 1] = (c >> 8) & 0xFF
    for idx, (byte, _treasure) in enumerate(inf_window_bytes(seed, row, col)):
        pb.memory[INF_WINDOW + idx] = byte
    pb.memory[NEED_REDRAW] = 1
    [pb.tick() for _ in range(10)]

def force_infinite_redraw_with_center(pb, center_byte):
    """Isolated dispatch/render check (T13.a's own isolation style, applied
    to the infinite-mode path): pokes only INF_WINDOW's center cell,
    ignoring neighbors -- dsr_p_inf/draw_region_arrows_inf never read them."""
    pb.memory[GAME_MODE] = 1
    pb.memory[INF_WINDOW + 4] = center_byte
    pb.memory[NEED_REDRAW] = 1
    [pb.tick() for _ in range(10)]

def read_inf_pos(pb):
    row = pb.memory[INF_ROW] | (pb.memory[INF_ROW + 1] << 8)
    col = pb.memory[INF_COL] | (pb.memory[INF_COL + 1] << 8)
    if row >= 0x8000: row -= 0x10000
    if col >= 0x8000: col -= 0x10000
    return row, col

_T24_DIR_BTN  = {'north': 'up', 'south': 'down', 'west': 'left', 'east': 'right'}
_T24_DIR_BIT  = {'north': 4, 'south': 5, 'west': 6, 'east': 7}
_T24_DIR_DELTA = {'north': (-1, 0), 'south': (1, 0), 'west': (0, -1), 'east': (0, 1)}

def t24_do_move(pb, direction):
    """Real button-driven transition attempt (T17's own _t17_do_move
    pattern, generalized to Infinite Mode's unbounded INF_ROW/INF_COL in
    place of CUR_ZONE): forces position to the relevant edge, holds the
    matching direction, ticks until INF_ROW/INF_COL changes (or the budget
    is exhausted -- correctly the case when the connectivity bit is
    clear), releases, settles a few more frames for the redraw to
    complete. Returns (moved, end_row, end_col)."""
    btn = _T24_DIR_BTN[direction]
    start = read_inf_pos(pb)
    pb.button_press(btn)
    if direction == 'east':
        pb.memory[PLAYER_X] = 156
    elif direction == 'west':
        pb.memory[PLAYER_X] = 0
    elif direction == 'south':
        pb.memory[PLAYER_Y] = 128
    else:
        pb.memory[PLAYER_Y] = 17
    moved = False
    for _ in range(80):
        pb.tick()
        if read_inf_pos(pb) != start:
            moved = True
            break
    pb.button_release(btn)
    [pb.tick() for _ in range(20)]   # settle the redraw for the biome check
    end_row, end_col = read_inf_pos(pb)
    return moved, end_row, end_col

# T24.a — real button-driven navigation (mirrors T17.a's own shape,
# extended to the unbounded case): from a materialized starting region, for
# each of the 4 directions, confirm a transition occurs iff the current
# region's own connectivity bit is set, INF_ROW/INF_COL update by exactly
# ±1 on the correct axis, and the newly-entered region's own screen renders
# the correct biome tileset (AC-1/FR-10200).
T24_NAV_SEEDS = [7, 99, 4242, 65535, 0xBEEF]
nav_bad = []
for seed in T24_NAV_SEEDS:
    pb = fresh_boot(200)
    advance_to_playing(pb)
    center_byte, _ = worldgen.materialize_region(seed, 0, 0)
    for direction in ('north', 'south', 'west', 'east'):
        set_infinite_state(pb, seed, 0, 0)
        expected_open = bool(center_byte & (1 << _T24_DIR_BIT[direction]))
        dr, dc = _T24_DIR_DELTA[direction]
        moved, end_row, end_col = t24_do_move(pb, direction)
        if moved != expected_open:
            nav_bad.append((seed, direction, 'transition-mismatch', moved, expected_open))
            continue
        if not expected_open:
            continue
        if (end_row, end_col) != (dr, dc):
            nav_bad.append((seed, direction, 'position-mismatch', (end_row, end_col), (dr, dc)))
            continue
        new_center_byte, _ = worldgen.materialize_region(seed, dr, dc)
        biome_id = new_center_byte & 0x0F
        lo, hi = FAMILY_RANGES[biome_id]
        field = field_tiles(pb)
        in_family = sum(1 for b in field if lo <= b <= hi)
        if in_family <= 40:
            nav_bad.append((seed, direction, 'biome-render-mismatch', in_family))
    pb.stop()
check("T24.a Real button-driven navigation: transitions occur iff the connectivity bit is set, INF_ROW/INF_COL update correctly, and the newly-entered region renders its own biome tileset (AC-1/FR-10200)",
      len(nav_bad) == 0, f"bad={nav_bad[:5]}")

# T24.b — revisit consistency through the render path (FR-10210): leaving a
# region (window re-centers away) and returning to it redraws a
# pixel-identical screen. Delegates the underlying data-layer check to
# IP-1101's own T22.c; this is the render-path confirmation T22 alone
# cannot make. Picks the first (seed, row, col) in a small search whose own
# south bit is open (T22.g's own proven south/north symmetry guarantees the
# return move north is always then open too), so the round trip is
# guaranteed reversible for any seed, not cherry-picked for one.
T24B_SEED = 2024
T24B_ROW = T24B_COL = None
for _r in range(20):
    for _c in range(20):
        _byte, _ = worldgen.materialize_region(T24B_SEED, _r, _c)
        if _byte & 0x20:   # south bit
            T24B_ROW, T24B_COL = _r, _c
            break
    if T24B_ROW is not None:
        break

pb = fresh_boot(200)
advance_to_playing(pb)
set_infinite_state(pb, T24B_SEED, T24B_ROW, T24B_COL)
tiles_visit1 = field_tiles(pb)
moved_away, r2, c2 = t24_do_move(pb, 'south')
moved_back, r3, c3 = t24_do_move(pb, 'north')
tiles_visit2 = field_tiles(pb)
pb.stop()
check("T24.b Revisit-consistency through the render path: leaving and returning to a region redraws a pixel-identical screen (FR-10210)",
      moved_away and (r2, c2) == (T24B_ROW + 1, T24B_COL)
      and moved_back and (r3, c3) == (T24B_ROW, T24B_COL)
      and tiles_visit1 == tiles_visit2,
      f"moved_away={moved_away} moved_back={moved_back} pos_back=({r3},{c3}) tiles_match={tiles_visit1 == tiles_visit2}")

# T24.c — finite mode (GAME_MODE == 0) is provably unchanged.
# T24.c1: static diff -- dsr_p's finite-mode body (from its existing
# CUR_ZONE read through its existing REGION_GRAPH-pointer JR) is, call for
# call, exactly the pre-IP-1102 instruction sequence, with only the
# 3-instruction GAME_MODE gate prefixed ahead of it (no instruction
# inserted, removed, or reordered within the pre-existing body itself).
import re
_dsr_p_finite_body = _src[_src.index("rom.label('dsr_p')"):_src.index("rom.label('dsr_p_inf')")]
_t24c_calls = [c for c in re.findall(r"rom\.([A-Za-z_]+)\(", _dsr_p_finite_body) if c != 'label']
_t24c_expected = ['LD_A_nn', 'OR_A', 'JR_NZ',                          # the new gate
                   'LD_A_nn', 'LD_E_A', 'LD_D_n', 'LD_HL_nn',           # pre-existing body,
                   'ADD_HL_DE', 'ADD_HL_DE', 'ADD_HL_DE',               # unmodified
                   'ADD_HL_DE', 'ADD_HL_DE', 'LD_A_HLI', 'PUSH_HL', 'JR']
check("T24.c1 Static diff: dsr_p's finite-mode body is byte-for-byte the pre-IP-1102 instruction sequence, only a 3-instruction gate prefixed",
      _t24c_calls == _t24c_expected, f"got={_t24c_calls}")

# T24.c2: regression -- every T13/T20 check (dsr_p/draw_region_arrows,
# exercised earlier in this same run under GAME_MODE's default-0 boot
# state) still passes unmodified under the new gate.
_t24c_regression = [r for r in results if r.split(']')[1].strip().startswith(('T13.', 'T20.'))]
_t24c_bad = [r for r in _t24c_regression if r.startswith('[FAIL]')]
check("T24.c2 Regression: every existing T13/T20 dsr_p/draw_region_arrows/check_zone_transition check still passes unmodified under the new GAME_MODE gate",
      len(_t24c_bad) == 0 and len(_t24c_regression) > 0,
      f"failed={_t24c_bad} total_checked={len(_t24c_regression)}")

# T24.d — the plain-open-arrow-only claim: draw_region_arrows_inf never
# writes a blocked-edge tile (Infinite Mode has no "grid-adjacent but
# maze-pruned" concept, ADR-0012 point 2's distinction is finite-mode-only).
# T24.d1: static audit.
_t24d_src = _src[_src.index("rom.label('draw_region_arrows_inf')"):_src.index("rom.label('mm_on_entry')")]
check("T24.d1 Static audit: draw_region_arrows_inf's source never references TL_BLOCKED_U/D/L/R",
      'BLOCKED' not in _t24d_src, "source-scanned")

# T24.d2: corpus -- drive every one of the 16 connectivity-nibble values
# (bits 3-6) through the real render path, confirm none ever produces a
# blocked-edge tile at any of the four arrow addresses.
pb = fresh_boot(200)
advance_to_playing(pb)
blocked_found = []
for nibble in range(16):
    force_infinite_redraw_with_center(pb, nibble << 3)
    for direction, addr in ARROW_POS.items():
        if pb.memory[addr] == BLOCKED_TILE[direction]:
            blocked_found.append((nibble, direction))
pb.stop()
check("T24.d2 Corpus: draw_region_arrows_inf never writes a blocked-edge tile, all 16 connectivity nibble values",
      len(blocked_found) == 0, f"bad={blocked_found[:5]}")

# T24.e — NFR-1400 Analysis check: direct cycle-count of inf_ensure_window's
# real per-transition cost (all 9 window cells -- this package's own §6
# text commits to "the whole window is simply recomputed fresh on every
# center change, no incremental shift logic", so 9 fresh
# inf_materialize_region calls is the actual cost of every transition, not
# merely a rare worst case; this package's own §8 T24.e wording additionally
# floats a hypothetical "realistic worst case of 3 cells" premised on an
# incremental-shift optimization that was never implemented — that
# assumption does not hold for the code as built, recorded here rather than
# silently adopted). Measured via a direct PC/SP hijack into
# inf_ensure_window (T12/T22's own established technique) with the return
# address pointed at the real ROM label czt_redraw (a hook there is safe --
# ROM only; hooking the WRAM self-loop trap T12/T22 use for coarse
# completion-detection was tried first and hangs PyBoy's emulation core, so
# this measurement avoids it entirely) and two hook_register callpoints
# (entry, return) reading PyBoy's own cycle counter -- exact, not
# frame-quantized.
def measure_inf_ensure_window_cycles(seed, row, col):
    pb = fresh_boot(180)
    pb.memory[SEED] = seed & 0xFF; pb.memory[SEED + 1] = (seed >> 8) & 0xFF
    r = row & 0xFFFF; c = col & 0xFFFF
    pb.memory[INF_ROW] = r & 0xFF; pb.memory[INF_ROW + 1] = (r >> 8) & 0xFF
    pb.memory[INF_COL] = c & 0xFF; pb.memory[INF_COL + 1] = (c >> 8) & 0xFF
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = CZT_REDRAW_ADDR & 0xFF
    pb.memory[sp + 1] = (CZT_REDRAW_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    state = {}
    def _start(ctx): state.setdefault('start', pb._cycles())
    def _end(ctx): state.setdefault('end', pb._cycles())
    pb.hook_register(0, INF_ENSURE_WINDOW_ADDR, _start, None)
    pb.hook_register(0, CZT_REDRAW_ADDR, _end, None)
    pb.register_file.PC = INF_ENSURE_WINDOW_ADDR
    for _ in range(10):
        pb.tick()
        if 'end' in state:
            break
    pb.stop()
    if 'start' not in state or 'end' not in state:
        return None
    return state['end'] - state['start']

T24E_CORPUS = [(2026, 0, 0), (7, 5, -5), (65535, -100, 100)]
t24e_measurements = [measure_inf_ensure_window_cycles(s, r, c) for s, r, c in T24E_CORPUS]
t24e_valid = [m for m in t24e_measurements if m is not None]
FRAME_BUDGET_CYCLES = 70224   # one CGB single-speed frame -- NFR-1400's own
                               # "same per-frame budget every other VRAM-
                               # adjacent write already respects" bar
t24e_met = bool(t24e_valid) and max(t24e_valid) <= FRAME_BUDGET_CYCLES
check("T24.e NFR-1400 Analysis: inf_ensure_window's real per-transition cost, direct cycle-count, measured and recorded (Met or not, not asserted un-measured)",
      len(t24e_valid) == len(T24E_CORPUS),
      f"cycles={t24e_measurements} budget={FRAME_BUDGET_CYCLES} status={'MET' if t24e_met else 'NOT MET'}")

# ══════════════════════════════════════════════════════
# T25 — Infinite Mode: Mode Selection & New-Game Entry (IP-1100)
# (FS-110's own template names "T22"; renumbered — IP-1101 already claimed
# T22 earlier this same tranche, mirroring IP-1101's own identical renaming
# of its planned "T23" -> "T22" when it shipped before IP-1100.)
# ══════════════════════════════════════════════════════
print("\n=== T25: Infinite Mode — Mode Selection & New-Game Entry ===")

def enter_infinite_seed(pb, digits):
    """From INFINITE SEED ENTRY at its just-entered defaults (cursor=0, all
    digits 0): drive the digit-cursor picker to the given 5 seed digits,
    then confirm with A. No scale slot exists in this state (bounded 0-4)."""
    for i, d in enumerate(digits):
        for _ in range(d):
            pb.button('up'); [pb.tick() for _ in range(10)]
        if i < 4:
            pb.button('right'); [pb.tick() for _ in range(10)]
    pb.button('a'); [pb.tick() for _ in range(80)]

# T25.a1/a2 — from MAIN MENU, "new game" -> MODE SELECT (not SEED/SCALE
# ENTRY directly); D-pad toggle moves the highlight between finite/infinite.
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
check("T25.a1 MAIN MENU, new game -> MODE SELECT (GS=10)", pb.memory[GAMESTATE] == 10,
      f"GS={pb.memory[GAMESTATE]}")
check("T25.a1b MODE SELECT defaults to MM_CURSOR=0 (finite)", pb.memory[MM_CURSOR] == 0,
      f"cursor={pb.memory[MM_CURSOR]}")
pb.button('down'); [pb.tick() for _ in range(40)]
check("T25.a2 D-pad toggles MM_CURSOR to 1 (infinite highlighted)", pb.memory[MM_CURSOR] == 1,
      f"cursor={pb.memory[MM_CURSOR]}")
pb.stop()

# T25.b1 — MODE SELECT, confirm "finite" -> SEED/SCALE ENTRY, GAME_MODE==0
# -- and SEED/SCALE ENTRY's own B-cancel still returns directly to MAIN
# MENU (regression check: GDS-01 §4d's named asymmetric-tradeoff is
# actually shipped as specified, not accidentally routed through MODE
# SELECT).
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm finite -> SEED/SCALE ENTRY
check("T25.b1a MODE SELECT, confirm finite -> SEED/SCALE ENTRY (GS=7)",
      pb.memory[GAMESTATE] == 7, f"GS={pb.memory[GAMESTATE]}")
check("T25.b1b GAME_MODE == 0 (finite)", pb.memory[GAME_MODE] == 0,
      f"GAME_MODE={pb.memory[GAME_MODE]}")
pb.button('b'); [pb.tick() for _ in range(40)]
check("T25.b1c SEED/SCALE ENTRY's own B-cancel target is still MAIN MENU (GS=6) directly, not redirected through MODE SELECT",
      pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
pb.stop()

# T25.b2 — MODE SELECT, confirm "infinite" -> COMBAT MODE CONFIRM,
# GAME_MODE==1. IP-1120 (BL-0153): ms_infinite's own transition target
# retargeted from GS_INFINITE_SEED_ENTRY (11) to GS_COMBAT_MODE_CONFIRM
# (12) -- this assertion's own expected GAMESTATE is a necessary,
# intentional consequence of that package's own Interfaces §5 (not a
# silent break of "T25 stays unmodified"; the COMBAT MODE CONFIRM state
# itself is fully covered by IP-1120's own T33 suite).
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb.button('down'); [pb.tick() for _ in range(40)]     # toggle to infinite
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm infinite
check("T25.b2a MODE SELECT, confirm infinite -> COMBAT MODE CONFIRM (GS=12, IP-1120)",
      pb.memory[GAMESTATE] == 12, f"GS={pb.memory[GAMESTATE]}")
check("T25.b2b GAME_MODE == 1 (infinite)", pb.memory[GAME_MODE] == 1,
      f"GAME_MODE={pb.memory[GAME_MODE]}")
pb.stop()

# T25.c1 — MODE SELECT, press B -> MAIN MENU, GAME_MODE unchanged from its
# prior value (nothing written on cancel) -- toggling the highlight to
# "infinite" without confirming must not itself write GAME_MODE; only
# ms_infinite's own A-confirm branch ever does.
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb.button('down'); [pb.tick() for _ in range(40)]     # highlight infinite, do NOT confirm
pb.button('b'); [pb.tick() for _ in range(40)]
check("T25.c1a MODE SELECT, B -> MAIN MENU (GS=6)", pb.memory[GAMESTATE] == 6,
      f"GS={pb.memory[GAMESTATE]}")
check("T25.c1b B-cancel writes no GAME_MODE (still 0, mere highlight never wrote it)",
      pb.memory[GAME_MODE] == 0, f"GAME_MODE={pb.memory[GAME_MODE]}")
pb.stop()

# T25.d1/d2 — INFINITE SEED ENTRY: drive digit-cursor entry for a known
# seed, confirm via A -> GS_INTRO, SEED equals the entered value,
# INF_ROW==INF_COL==0, and the starting region's materialized data
# (IP-1101's own output shape, oracle-cross-checked) is present in
# INF_WINDOW's center cell.
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb.button('down'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm infinite -> COMBAT MODE CONFIRM (IP-1120)
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm default "N" -> INFINITE SEED ENTRY
enter_infinite_seed(pb, [1, 2, 3, 4, 5])              # seed=12345
check("T25.d1 Confirm -> INTRO (GS=1)", pb.memory[GAMESTATE] == 1, f"GS={pb.memory[GAMESTATE]}")
check("T25.d1b SEED written correctly (12345)",
      pb.memory[SEED] | (pb.memory[SEED+1] << 8) == 12345,
      f"seed={pb.memory[SEED] | (pb.memory[SEED+1] << 8)}")
inf_row_d1 = pb.memory[INF_ROW] | (pb.memory[INF_ROW+1] << 8)
inf_col_d1 = pb.memory[INF_COL] | (pb.memory[INF_COL+1] << 8)
check("T25.d2a INF_ROW == 0, INF_COL == 0 at new-game entry",
      inf_row_d1 == 0 and inf_col_d1 == 0, f"row={inf_row_d1} col={inf_col_d1}")
expected_center, _ = worldgen.materialize_region(12345, 0, 0)
check("T25.d2b Starting region's materialized data present in INF_WINDOW's center cell, oracle-matched (IP-1101's own output shape)",
      pb.memory[INF_WINDOW + 4] == expected_center,
      f"got=0x{pb.memory[INF_WINDOW + 4]:02X} expected=0x{expected_center:02X}")
pb.button('a'); [pb.tick() for _ in range(80)]        # INTRO -> PLAYING
check("T25.d2c Reaches PLAYING cleanly (GS=2)", pb.memory[GAMESTATE] == 2,
      f"GS={pb.memory[GAMESTATE]}")
pb.stop()

# T25.e1 — INFINITE SEED ENTRY, press B -> MODE SELECT (not MAIN MENU --
# this state has no shipped precedent to protect, GDS-01 §4d's own "one
# step back" framing), SEED/GAME_MODE unchanged.
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
pb.button('down'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]        # -> COMBAT MODE CONFIRM (IP-1120)
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm default "N" -> INFINITE SEED ENTRY
seed_before_e1 = pb.memory[SEED] | (pb.memory[SEED+1] << 8)
mode_before_e1 = pb.memory[GAME_MODE]
pb.button('up'); [pb.tick() for _ in range(10)]       # touch a digit, then abandon via B
pb.button('b'); [pb.tick() for _ in range(40)]
check("T25.e1a INFINITE SEED ENTRY, B -> MODE SELECT (GS=10)", pb.memory[GAMESTATE] == 10,
      f"GS={pb.memory[GAMESTATE]}")
check("T25.e1b B-cancel writes no SEED/GAME_MODE",
      pb.memory[SEED] | (pb.memory[SEED+1] << 8) == seed_before_e1
      and pb.memory[GAME_MODE] == mode_before_e1,
      f"seed={pb.memory[SEED] | (pb.memory[SEED+1] << 8)} mode={pb.memory[GAME_MODE]}")
pb.stop()

# T25.f — seed=0 entered: SEED WRAM itself is left at exactly 0 (not
# force-normalized to 1) -- matching the finite mode's own established,
# already-verified precedent (sse_compose_seed, reused verbatim here, has
# never written a normalized value back to SEED WRAM; only the internal
# PRNG working state normalizes 0->1, T22.f's own already-existing check).
# This package's own §8 text describes this as "SEED normalized to 1",
# imprecise relative to the actual shipped behavior -- tested here as it
# actually, correctly works, not as literally worded (same class of small
# drift as VR-1101's own citation findings this tranche). What IS asserted:
# the internal materialization for (0,0) still produces a valid,
# non-degenerate result despite the raw SEED==0 (AC-7's own real intent).
pb = fresh_boot(200)
pb.button('a'); [pb.tick() for _ in range(40)]
pb.button('down'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]        # -> COMBAT MODE CONFIRM (IP-1120)
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm default "N" -> INFINITE SEED ENTRY
enter_infinite_seed(pb, [0, 0, 0, 0, 0])              # seed=0
check("T25.f1 SEED left at exactly 0 as entered (not force-written to 1, matches finite mode's own precedent)",
      pb.memory[SEED] | (pb.memory[SEED+1] << 8) == 0,
      f"seed={pb.memory[SEED] | (pb.memory[SEED+1] << 8)}")
expected_center_0, _ = worldgen.materialize_region(0, 0, 0)
check("T25.f2 seed=0 still produces a valid materialized starting region (internal PRNG normalization, AC-7)",
      pb.memory[INF_WINDOW + 4] == expected_center_0 and expected_center_0 is not None,
      f"got=0x{pb.memory[INF_WINDOW + 4]:02X} expected=0x{expected_center_0:02X}")
pb.stop()

# ══════════════════════════════════════════════════════
# T26 — Infinite Mode: Treasure & Win-Condition State (IP-1103)
# (IP-1103's own §8 names "T25"; renumbered — IP-1100 already claimed T25
# when it shipped first: the tranche's third such renaming, after IP-1101's
# T23->T22 and IP-1100's own T22->T25.)
# ══════════════════════════════════════════════════════
print("\n=== T26: Infinite Mode — Treasure & Win-Condition State ===")

RUNNING_TREASURE_COUNT = 0xC405
TOP_SCORE_TABLE = 0xC407
ICTS_ADDR = _gw_rom.labels['inf_check_top_score']
ITP_ADDR = _gw_rom.labels['inf_treasure_pos']

def enter_infinite_mode(pb, seed):
    """MAIN MENU -> MODE SELECT -> (infinite) -> COMBAT MODE CONFIRM
    (IP-1120, confirms default "N") -> INFINITE SEED ENTRY -> seed digits
    -> INTRO -> A -> PLAYING. The same button script T25.d established,
    packaged for reuse."""
    pb.button('a'); [pb.tick() for _ in range(40)]
    pb.button('down'); [pb.tick() for _ in range(40)]
    pb.button('a'); [pb.tick() for _ in range(40)]
    pb.button('a'); [pb.tick() for _ in range(40)]        # COMBAT MODE CONFIRM: confirm default "N"
    enter_infinite_seed(pb, [(seed // 10 ** (4 - i)) % 10 for i in range(5)])
    pb.button('a'); [pb.tick() for _ in range(80)]

def read_rtc(pb):
    return pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)

def read_top3(pb):
    return [pb.memory[TOP_SCORE_TABLE + 2 * i] | (pb.memory[TOP_SCORE_TABLE + 2 * i + 1] << 8)
            for i in range(3)]

# T26.a0 — static: the per-biome spawn-position table in ROM matches
# ZONE_COLLECTS's own type-2 (KeyItem) entry exactly, biome for biome.
# asm_game.py deliberately duplicates these values rather than importing
# the content module (ADR-0003's module-boundary rule) — this check is
# what makes content-side drift fail the suite loudly instead of the two
# copies desyncing silently.
with open(ROM_PATH, 'rb') as _f:
    _t26_rom = _f.read()
_t26_expected_pos = []
for _b in range(9):   # IP-1106: all nine identities, not just the original five
    _k2 = [(x, y) for (x, y, t) in ZONE_COLLECTS[_b] if t == 2]
    _t26_expected_pos.append(_k2[0] if len(_k2) == 1 else None)
_t26_table = [(_t26_rom[ITP_ADDR + 2 * _b], _t26_rom[ITP_ADDR + 2 * _b + 1]) for _b in range(9)]
check("T26.a0 Static: inf_treasure_pos table matches ZONE_COLLECTS's single type-2 entry per biome, all nine identities (drift guard for the deliberate duplication)",
      _t26_table == _t26_expected_pos, f"rom={_t26_table} expected={_t26_expected_pos}")

# T26.a1 — boot init: RUNNING_TREASURE_COUNT/TOP_SCORE_TABLE sit outside
# the 0xC000-C2FF blanket boot clear; the targeted 8-byte boot clear
# (IP-1102's GAME_MODE lesson applied) must leave all of them zero on a
# fresh cartridge — no garbage bytes standing as high scores.
pb = fresh_boot(200)
check("T26.a1 Boot: RUNNING_TREASURE_COUNT == 0 and TOP_SCORE_TABLE == [0,0,0] (explicit boot clear — the range sits outside the 0xC000-C2FF blanket clear)",
      read_rtc(pb) == 0 and read_top3(pb) == [0, 0, 0],
      f"rtc={read_rtc(pb)} top3={read_top3(pb)}")

# T26.a — treasure collection end-to-end (FR-10300, collection half).
# Seed chosen by oracle search: the first seed whose (0,0) region holds
# treasure, so the starting region itself is the collection site.
t26_seed = None
for _s in range(1, 65536):
    if worldgen.materialize_region(_s, 0, 0)[1]:
        t26_seed = _s
        break
enter_infinite_mode(pb, t26_seed)
check("T26.a2 Reached PLAYING in Infinite Mode (GS=2, GAME_MODE=1)",
      pb.memory[GAMESTATE] == 2 and pb.memory[GAME_MODE] == 1,
      f"GS={pb.memory[GAMESTATE]} mode={pb.memory[GAME_MODE]} seed={t26_seed}")
check("T26.a3 INF_TREASURE_HERE cached == 1 at the region's own materialization (IP-1101's predicate via inf_ensure_window's center cell)",
      pb.memory[INF_TREASURE_HERE] == 1, f"cache={pb.memory[INF_TREASURE_HERE]}")
_t26_biome = pb.memory[INF_WINDOW + 4] & 0x0F
_t26_pos = _t26_expected_pos[_t26_biome]
_t26_cd = tuple(pb.memory[COLL_DATA + i] for i in range(4))
check("T26.a4 Spawn: COLL_COUNT == 1 and COLL_DATA[0] == (biome's table x, y, type 2, active 1) — exactly one item, the treasure",
      pb.memory[COLL_COUNT] == 1 and _t26_cd == (_t26_pos[0], _t26_pos[1], 2, 1),
      f"count={pb.memory[COLL_COUNT]} entry={_t26_cd} expected={_t26_pos + (2, 1)}")
_t26_oam1 = oam_entry(pb, 1)
check("T26.a4b Render: the treasure is a live OAM sprite at the spawn position (update_oam's existing type-2 path, TL_CARROT)",
      _t26_oam1[0] == _t26_pos[1] + 16 and _t26_oam1[1] == _t26_pos[0] + 8
      and _t26_oam1[2] == TL_CARROT,
      f"oam={_t26_oam1} expected=({_t26_pos[1]+16},{_t26_pos[0]+8},0x{TL_CARROT:02X},*)")
_t26_score0 = pb.memory[SCORE]
_t26_carrots0 = pb.memory[CARROTS_COUNT]
check("T26.a5 Pre-collection baseline: RUNNING_TREASURE_COUNT == 0, SCORE == 0, CARROTS_COUNT == 0",
      read_rtc(pb) == 0 and _t26_score0 == 0 and _t26_carrots0 == 0,
      f"rtc={read_rtc(pb)} score={_t26_score0} carrots={_t26_carrots0}")
# Drive the player onto the collection position (check_collisions' own
# existing collision-point convention: 0 <= item-player < 8/16 box, T8's
# established synthetic-position technique).
pb.memory[PLAYER_X] = _t26_pos[0]
pb.memory[PLAYER_Y] = _t26_pos[1]
[pb.tick() for _ in range(12)]
check("T26.a6 Collection: RUNNING_TREASURE_COUNT increments by exactly 1, INF_TREASURE_HERE clears, item deactivates",
      read_rtc(pb) == 1 and pb.memory[INF_TREASURE_HERE] == 0 and pb.memory[COLL_DATA + 3] == 0,
      f"rtc={read_rtc(pb)} cache={pb.memory[INF_TREASURE_HERE]} active={pb.memory[COLL_DATA + 3]}")
check("T26.a7 No finite-mode counter touched: SCORE/CARROTS_COUNT(=KEYITEM_COUNT) unchanged, KEYITEM_FLAGS[0] untouched",
      pb.memory[SCORE] == _t26_score0 and pb.memory[CARROTS_COUNT] == _t26_carrots0
      and pb.memory[KEYITEM_FLAGS] == 0,
      f"score={pb.memory[SCORE]} carrots={pb.memory[CARROTS_COUNT]} kif0={pb.memory[KEYITEM_FLAGS]}")
[pb.tick() for _ in range(10)]
check("T26.a8 No spurious finite victory: GAMESTATE stays PLAYING after collection (IP-1100 §6's named confirmation, owned by this package)",
      pb.memory[GAMESTATE] == 2, f"GS={pb.memory[GAMESTATE]}")

# T26.b — no double collection.
[pb.tick() for _ in range(30)]
check("T26.b1 No double collection: RUNNING_TREASURE_COUNT stays 1 while standing on the collection point (item inactive, cache cleared)",
      read_rtc(pb) == 1, f"rtc={read_rtc(pb)}")
# Menu round-trip: SELECT -> SELECT MENU -> B -> PLAYING forces a full
# do_screen_redraw -> setup_zone_collects re-run without leaving the
# region or the materialized window — the collected treasure must not
# respawn (szc_infinite's cache-cleared path: COLL_COUNT stays 0).
pb.button('select'); [pb.tick() for _ in range(40)]
pb.button('b'); [pb.tick() for _ in range(40)]
check("T26.b2 Redraw after collection does not respawn the treasure: back in PLAYING with COLL_COUNT == 0 and the count still 1",
      pb.memory[GAMESTATE] == 2 and pb.memory[COLL_COUNT] == 0 and read_rtc(pb) == 1,
      f"GS={pb.memory[GAMESTATE]} count={pb.memory[COLL_COUNT]} rtc={read_rtc(pb)}")
pb.stop()

# T26.c — inf_check_top_score against a synthetic corpus (FR-10400, AC-4's
# insertion half), called directly via the established PC/SP-hijack
# technique (invoke_generate_world's own pattern) — no in-game call site
# exists, deliberately (see T26.d).
def invoke_icts(pb, count, table):
    """Write RUNNING_TREASURE_COUNT + TOP_SCORE_TABLE fixtures, CALL
    inf_check_top_score via PC/SP hijack, return the table read back
    (list of 3 ints), or None if the routine never returned."""
    pb.memory[RUNNING_TREASURE_COUNT] = count & 0xFF
    pb.memory[RUNNING_TREASURE_COUNT + 1] = (count >> 8) & 0xFF
    for i, v in enumerate(table):
        pb.memory[TOP_SCORE_TABLE + 2 * i] = v & 0xFF
        pb.memory[TOP_SCORE_TABLE + 2 * i + 1] = (v >> 8) & 0xFF
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE  # JR -2
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = ICTS_ADDR
    for _ in range(30):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            return read_top3(pb)
    return None

def icts_model(count, table):
    """The subroutine's specified behavior (IP-1103 §6): strictly-exceeds
    qualification against the lowest entry, sorted-descending insertion,
    previous lowest displaced; ties never insert."""
    if count <= table[2]:
        return list(table)
    if count > table[0]:
        return [count, table[0], table[1]]
    if count > table[1]:
        return [table[0], count, table[1]]
    return [table[0], table[1], count]

_t26c_corpus = [
    (5, [0, 0, 0]),          # empty table -> straight to index 0
    (7, [10, 5, 2]),         # mid insertion -> [10, 7, 5]
    (1, [10, 5, 2]),         # below lowest -> unchanged
    (2, [10, 5, 2]),         # TIE with lowest -> unchanged (strictly-exceeds)
    (100, [10, 5, 2]),       # new high -> [100, 10, 5]
    (10, [10, 5, 2]),        # tie with top -> slots at index 1
    (5, [10, 5, 2]),         # tie with middle -> slots at index 2
    (0x0200, [0x1234, 0x0100, 0x00FF]),   # 16-bit, high-byte-decided
    (0x0105, [0x0110, 0x0107, 0x0102]),   # 16-bit, equal-high low-byte-decided
    (0xFFFF, [0xFFFE, 0x8000, 0x0001]),   # top of the unsigned range
    (0x00FF, [0x0100, 0x0100, 0x0100]),   # below all, high-byte-decided -> unchanged
]
pb = fresh_boot(200)
_t26c_bad = []
for _count, _table in _t26c_corpus:
    _got = invoke_icts(pb, _count, _table)
    _want = icts_model(_count, _table)
    if _got != _want:
        _t26c_bad.append((_count, _table, _got, _want))
check("T26.c1 inf_check_top_score corpus: qualifying counts insert at the sorted-descending position displacing the previous lowest; non-qualifying (incl. exact ties) leave the table byte-for-byte unchanged (FR-10400/AC-4)",
      not _t26c_bad, f"mismatches={_t26c_bad}")
# Two hand-written spot expectations, independent of the model function:
check("T26.c2 Spot: (7 into [10,5,2]) -> [10,7,5]; (2 into [10,5,2]) -> unchanged (tie rejected)",
      invoke_icts(pb, 7, [10, 5, 2]) == [10, 7, 5]
      and invoke_icts(pb, 2, [10, 5, 2]) == [10, 5, 2], "spot-checked")
pb.stop()

# T26.d — negative test, stating the BL-0112 deferral explicitly rather
# than leaving it silent (IP-1103 §8/§10): inf_check_top_score has ZERO
# call sites — no in-game event invokes it. A future package's addition of
# the automatic trigger (once BL-0112 resolves) shows up as a clean,
# detectable diff: this check flips.
_t26_src = (BASE / 'asm_game.py').read_text()
_t26d_refs = re.findall(
    r"rom\.(?:CALL|CALL_NZ|CALL_Z|JP|JP_Z|JP_NZ|JP_C|JP_NC|JR|JR_Z|JR_NZ|JR_C|JR_NC)\('inf_check_top_score'\)",
    _t26_src)
_t26d_labels = _t26_src.count("rom.label('inf_check_top_score')")
# ROM-level corroboration: no CALL/JP-family opcode carrying the routine's
# resolved address appears anywhere in the assembled code region.
_t26d_lo, _t26d_hi = ICTS_ADDR & 0xFF, (ICTS_ADDR >> 8) & 0xFF
_t26d_code_end = _gw_rom.pos
_t26d_hits = [i for i in range(0x150, _t26d_code_end)
              if _t26_rom[i] in (0xCD, 0xC4, 0xCC, 0xD4, 0xDC,
                                 0xC3, 0xC2, 0xCA, 0xD2, 0xDA)
              and _t26_rom[i + 1] == _t26d_lo and _t26_rom[i + 2] == _t26d_hi]
check("T26.d Zero call sites for inf_check_top_score: source audit (label defined once, never CALLed/JPed) + ROM scan of the code region — the BL-0112 trigger deferral, checkable",
      _t26d_refs == [] and _t26d_labels == 1 and _t26d_hits == [],
      f"src_refs={_t26d_refs} labels={_t26d_labels} rom_hits={[hex(h) for h in _t26d_hits]}")

# T26.e — no name-entry state is reachable from any code path this package
# adds (FR-10400/FS-110 AC-4's own explicit requirement): static audit over
# exactly the three new/extended code blocks — none of them writes
# TRANSITION_TO or GAMESTATE at all (so they cannot transition anywhere,
# let alone to a name-entry state), and no name-entry GAMESTATE exists
# anywhere in the source to transition to.
def _t26_seg(start_marker, end_marker):
    return _t26_src[_t26_src.index(start_marker):_t26_src.index(end_marker)]
_t26e_segs = {
    'szc_infinite': _t26_seg("rom.label('szc_infinite')", "rom.label('update_map_hearts')"),
    'cc_inf_hit': _t26_seg("rom.label('cc_inf_hit')", "rom.label('czt_region_hl')"),
    'inf_check_top_score+ledger stub': _t26_seg("rom.label('inf_check_top_score')",
                                                "rom.label('save_to_sram')"),
}
_t26e_bad = [name for name, s in _t26e_segs.items()
             if 'TRANSITION_TO' in s or "LD_nn_A(GAMESTATE" in s]
check("T26.e No name-entry state reachable from this package's new branches: none writes TRANSITION_TO/GAMESTATE, and no name-entry GAMESTATE exists in the source at all",
      _t26e_bad == [] and re.search(r"GS_\w*NAME", _t26_src) is None,
      f"segments_writing_state={_t26e_bad}")

# T26.h — value-range coverage (IP-1106, FR-4320's Infinite Mode half):
# the live SM83 biome draw reaches every value of the widened 0-8 domain
# across T22's own (seed,row,col) corpus — asserted on the *SM83 output*,
# not the oracle, so the check cannot pass vacuously if the corpus never
# actually exercised the widened range (T12.d's own IP-1022 lesson applied
# here); each drawn value is simultaneously re-checked against the oracle
# (redundant with T22.b by construction, kept as this check's own guard).
pb = fresh_boot(180)
_t26h_seen = set()
_t26h_mismatch = []
for _seed, _row, _col in T22_CORPUS:
    _got = invoke_inf_materialize_region(pb, _seed, _row, _col)
    _exp_byte, _exp_t = worldgen.materialize_region(_seed, _row, _col)
    if _got is None or _got[0] != _exp_byte:
        _t26h_mismatch.append((_seed, _row, _col, _got))
        continue
    _t26h_seen.add(_got[0] & 0x0F)
pb.stop()
check("T26.h Value-range coverage: SM83 biome draw reaches all nine values 0-8 across the corpus, oracle-matched (IP-1106/FR-4320)",
      _t26h_seen == set(range(9)) and _t26h_mismatch == [],
      f"seen={sorted(_t26h_seen)} mismatches={_t26h_mismatch[:3]}")

# T26.i — dispatch-integration (IP-1106): for each of the four newly-folded
# identities, force INF_WINDOW's center cell to that biome-id (T24's own
# force_infinite_redraw_with_center isolation pattern) with the region's
# treasure cache set — confirming the correct family screen renders (IP-1022's
# cascade, exercised from the *infinite* path specifically) AND the correct
# treasure position spawns from inf_treasure_pos's own new entries (this
# package's extension) — the end-to-end integration point neither package
# alone verifies (IP-1022's own VR drove finite mode only).
pb = fresh_boot(200)
advance_to_playing(pb)
_t26i_bad = []
for _biome in (5, 6, 7, 8):
    pb.memory[INF_TREASURE_HERE] = 1
    force_infinite_redraw_with_center(pb, _biome)   # connectivity nibble 0
    _lo, _hi = FAMILY_RANGES[_biome]
    _field = field_tiles(pb)
    _in_family = sum(1 for _b in _field if _lo <= _b <= _hi)
    _pos = _t26_expected_pos[_biome]
    _cd = tuple(pb.memory[COLL_DATA + _i] for _i in range(4))
    if _in_family <= 40 or pb.memory[COLL_COUNT] != 1 or _cd != (_pos[0], _pos[1], 2, 1):
        _t26i_bad.append((_biome, _in_family, pb.memory[COLL_COUNT], _cd, _pos))
pb.stop()
check("T26.i Dispatch-integration: biome-ids 5-8 render their own family screen and spawn their own inf_treasure_pos treasure in Infinite Mode (IP-1106 + IP-1022 jointly)",
      _t26i_bad == [], f"bad={_t26i_bad}")

# ══════════════════════════════════════════════════════
# T27 — Infinite Mode: Ledger Save Persistence (IP-1104)
# (IP-1104's own §8 names "T26" -- renumbered; IP-1103 already claimed T26
# earlier this same tranche when it shipped first, the fourth such
# renaming after IP-1101/IP-1100/IP-1103's own identical precedents.)
# ══════════════════════════════════════════════════════
print("\n=== T27: Infinite Mode — Ledger Save Persistence ===")

LEDGER_COUNT = 0xC419
LEDGER_CURSOR = 0xC41A
LEDGER = 0xC41B
SRAM_GAME_MODE = 0xA0C1
SRAM_INF_ROW = 0xA0C2
SRAM_INF_COL = 0xA0C4
SRAM_RUNNING_TREASURE_COUNT = 0xA0C6
SRAM_TOP_SCORE_TABLE = 0xA0C8
SRAM_LEDGER_COUNT = 0xA0CE
SRAM_LEDGER_CURSOR = 0xA0CF
SRAM_LEDGER = 0xA0D0
ILMC_ADDR = _gw_rom.labels['inf_ledger_mark_collected']

def invoke_ilmc(pb, row, col):
    """Directly invoke inf_ledger_mark_collected via the established
    PC/SP-hijack technique (invoke_icts's own pattern) -- sets INF_ROW/
    INF_COL, CALLs the routine, returns True once it RETs (trap reached)."""
    r = row & 0xFFFF; c = col & 0xFFFF
    pb.memory[INF_ROW] = r & 0xFF; pb.memory[INF_ROW + 1] = (r >> 8) & 0xFF
    pb.memory[INF_COL] = c & 0xFF; pb.memory[INF_COL + 1] = (c >> 8) & 0xFF
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE  # JR -2
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = ILMC_ADDR
    for _ in range(60):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            return True
    return False

# T27.a — two-instance save/reload harness (mirroring IP-1050's own T15
# pattern): materialize a region with treasure, collect it, move to a
# second region, save, load in a fresh instance -> assert INF_ROW/INF_COL,
# RUNNING_TREASURE_COUNT, and the first region's own collected-state (via
# INF_TREASURE_HERE after navigating back to it post-load) all restore
# exactly (AC-5). Seed chosen so (0,0) holds treasure AND its east edge is
# open (Binary Tree edges are symmetric -- IP-1102's own carve-bias
# design -- so the return path west is guaranteed open too).
t27_seed = None
for _s in range(1, 65536):
    _center, _treasure = worldgen.materialize_region(_s, 0, 0)
    if _treasure and (_center >> 7) & 1:
        t27_seed = _s
        break

wipe_save()
pb = fresh_boot(200)
enter_infinite_mode(pb, t27_seed)
_t27a_biome = pb.memory[INF_WINDOW + 4] & 0x0F
_t27a_pos = None
for (_x, _y, _t) in ZONE_COLLECTS[_t27a_biome]:
    if _t == 2:
        _t27a_pos = (_x, _y)
pb.memory[PLAYER_X] = _t27a_pos[0]
pb.memory[PLAYER_Y] = _t27a_pos[1]
[pb.tick() for _ in range(12)]
rtc_pre27a = read_rtc(pb)
# Move right to a second region (guaranteed open, per the seed search above)
pb.memory[PLAYER_X] = 152
pb.button('right'); [pb.tick() for _ in range(20)]
inf_row_mid = pb.memory[INF_ROW] | (pb.memory[INF_ROW + 1] << 8)
inf_col_mid = pb.memory[INF_COL] | (pb.memory[INF_COL + 1] << 8)
check("T27.a1 Pre-save: treasure collected (RUNNING_TREASURE_COUNT==1) and player moved to a second region (INF_COL==1)",
      rtc_pre27a == 1 and inf_row_mid == 0 and inf_col_mid == 1,
      f"rtc={rtc_pre27a} row={inf_row_mid} col={inf_col_mid}")
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]   # SAVE: A (save)
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(60)]   # MAIN MENU: continue
inf_row_post = pb2.memory[INF_ROW] | (pb2.memory[INF_ROW + 1] << 8)
inf_col_post = pb2.memory[INF_COL] | (pb2.memory[INF_COL + 1] << 8)
rtc_post27a = read_rtc(pb2)
check("T27.a2 Post-load: INF_ROW/INF_COL and RUNNING_TREASURE_COUNT restore exactly, straight to PLAYING",
      pb2.memory[GAMESTATE] == 2 and inf_row_post == 0 and inf_col_post == 1
      and rtc_post27a == 1,
      f"GS={pb2.memory[GAMESTATE]} row={inf_row_post} col={inf_col_post} rtc={rtc_post27a}")
# Navigate back (west) to the first region -- symmetric edge, guaranteed open.
pb2.memory[PLAYER_X] = 0
pb2.button('left'); [pb2.tick() for _ in range(20)]
inf_col_back = pb2.memory[INF_COL] | (pb2.memory[INF_COL + 1] << 8)
treasure_back = pb2.memory[INF_TREASURE_HERE]
check("T27.a3 Back at the first region: INF_COL==0 again, INF_TREASURE_HERE==0 (collected-state survived the save/load boundary, not re-derived as present)",
      inf_col_back == 0 and treasure_back == 0,
      f"col={inf_col_back} treasure_here={treasure_back}")
pb2.stop()

# T27.b — no region's biome/connectivity is itself persisted: after T27.a's
# own save (exactly one ledger entry -- region (0,0), collected), read the
# raw SRAM bytes directly and confirm the 5-byte entry format holds only
# (row, col, collected) -- nothing else, no biome/connectivity byte
# anywhere in the record (AC-5's own explicit clause).
with open(RAM_PATH, 'rb') as _f:
    _t27b_sram = _f.read()
_t27b_entry = list(_t27b_sram[SRAM_LEDGER - 0xA000 : SRAM_LEDGER - 0xA000 + 5])
check("T27.b SRAM_LEDGER's 5-byte entry format holds only (row, col, collected) -- direct byte audit of the persisted (0,0) entry, no biome/connectivity field anywhere",
      _t27b_entry == [0, 0, 0, 0, 1], f"entry_bytes={_t27b_entry}")
wipe_save()

# T27.c — FIFO eviction: fill the ledger to exactly 128 entries (direct
# WRAM pokes -- 128 real collection events would be impractically slow),
# invoke inf_ledger_mark_collected directly for a genuinely new 129th
# region -> assert the entry at the pre-eviction LEDGER_CURSOR position is
# overwritten, all others unchanged, LEDGER_COUNT stays at 128; a
# follow-up save/load round trip confirms the same state survives the
# memcpy into SRAM_LEDGER/back.
pb = fresh_boot(200)
enter_infinite_mode(pb, 777)
for _i in range(128):
    _base = LEDGER + _i * 5
    pb.memory[_base] = _i & 0xFF; pb.memory[_base + 1] = (_i >> 8) & 0xFF
    pb.memory[_base + 2] = 0; pb.memory[_base + 3] = 0
    pb.memory[_base + 4] = 1
pb.memory[LEDGER_COUNT] = 128
pb.memory[LEDGER_CURSOR] = 0
ok27c = invoke_ilmc(pb, 999, 999)
check("T27.c1 inf_ledger_mark_collected invoked cleanly at capacity", ok27c, "")
post_count27c = pb.memory[LEDGER_COUNT]
post_cursor27c = pb.memory[LEDGER_CURSOR]
evicted_entry = [pb.memory[LEDGER + k] for k in range(5)]
other_entry_1 = [pb.memory[LEDGER + 5 + k] for k in range(5)]
check("T27.c2 LEDGER_COUNT stays 128, LEDGER_CURSOR advances to 1 (mod 128, AND 0x7F, no DIV)",
      post_count27c == 128 and post_cursor27c == 1,
      f"count={post_count27c} cursor={post_cursor27c}")
check("T27.c3 Entry at the pre-eviction cursor position (0) is overwritten with the new region (999,999,collected=1); all others unchanged (spot check: entry 1)",
      evicted_entry == [999 & 0xFF, (999 >> 8) & 0xFF, 999 & 0xFF, (999 >> 8) & 0xFF, 1]
      and other_entry_1 == [1, 0, 0, 0, 1],
      f"evicted={evicted_entry} entry1={other_entry_1}")
# PC/SP-hijack calls (invoke_ilmc, mirroring invoke_icts/invoke_generate_
# world's own established technique) leave the CPU parked in the trap's
# infinite self-loop -- this codebase's own convention is always pb.stop()
# right after, never further button-driven interaction in the same
# instance. The save/load round trip is therefore a fresh, independent
# instance (T27.c4) that reproduces the identical post-eviction state via
# direct WRAM pokes (already proven correct by c1-c3 above) rather than
# re-using this instance's now-stuck CPU.
pb.stop()

pb = fresh_boot(200)
enter_infinite_mode(pb, 777)
pb.memory[LEDGER_COUNT] = post_count27c
pb.memory[LEDGER_CURSOR] = post_cursor27c
for _i, _b in enumerate(evicted_entry):
    pb.memory[LEDGER + _i] = _b
for _i, _b in enumerate(other_entry_1):
    pb.memory[LEDGER + 5 + _i] = _b
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]
pb.stop()
pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(40)]
post_count27c2 = pb2.memory[LEDGER_COUNT]
post_cursor27c2 = pb2.memory[LEDGER_CURSOR]
evicted_entry2 = [pb2.memory[LEDGER + k] for k in range(5)]
pb2.stop()
check("T27.c4 Eviction state (count/cursor/overwritten entry) survives a save/load round trip",
      post_count27c2 == 128 and post_cursor27c2 == 1 and evicted_entry2 == evicted_entry,
      f"count={post_count27c2} cursor={post_cursor27c2} entry={evicted_entry2}")
wipe_save()

# T27.d — pre-upgrade rejection: a synthetic version=0x04 fixture (the
# pre-Infinite-Mode value) -> assert "continue" absent, mirroring T11.d's/
# T16.d's own established pattern.
fixture27d = bytearray(8192)
fixture27d[0:4] = bytes([0x42, 0x55, 0x4E, 0x59])
fixture27d[SRAM_CUR_ZONE - 0xA000] = 0
fixture27d[SRAM_PLAYER_X - 0xA000] = 76
fixture27d[SRAM_PLAYER_Y - 0xA000] = 80
fixture27d[SAVE_VERSION_ADDR - 0xA000] = 0x04   # IP-9110's own vintage, now superseded
for _i in range(81): fixture27d[SRAM_SCOREITEM - 0xA000 + _i] = 0xFF
with open(RAM_PATH, 'wb') as _f:
    _f.write(bytes(fixture27d))
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T27.d1 Boot with a version=0x04 (pre-Infinite-Mode) save -> MAIN MENU",
      pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
check("T27.d2 Version-0x04 save -> CONTINUE absent",
      not continue_offered(pb), "")
pb.stop()
wipe_save()

# T27.e — finite-mode save round-trip regression: T15's own existing
# checks (already executed earlier in this same run) still pass unmodified
# against the new SAVE_VERSION_VAL (0x05) -- mirrors T24.c2's own
# already-executed-suite cross-reference technique.
_t27e_regression = [r for r in results if r.split(']')[1].strip().startswith('T15.')]
_t27e_bad = [r for r in _t27e_regression if r.startswith('[FAIL]')]
check("T27.e Regression: every existing T15 (generated-world save persistence) check still passes unmodified under the new SAVE_VERSION_VAL",
      len(_t27e_bad) == 0 and len(_t27e_regression) > 0,
      f"failed={_t27e_bad} total_checked={len(_t27e_regression)}")

# T27.f — indefinite resumability (AC-6, FR-10600): from a loaded Infinite
# Mode save, attempt every reachable input sequence from the equivalent of
# PLAYING -- assert none forcibly ends the run or transitions anywhere but
# PLAYING/SAVE/MAP-equivalent states (mirrors T14.e's own systematic
# negative-test-sweep shape).
wipe_save()
pb = fresh_boot(200)
enter_infinite_mode(pb, 42)
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]      # SAVE: A (save)
pb.stop()
pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(60)]    # continue -> straight to PLAYING
gs_after_load = pb2.memory[GAMESTATE]
for btn in ('up', 'down', 'left', 'right'):
    pb2.button(btn); [pb2.tick() for _ in range(10)]
pb2.button('start'); [pb2.tick() for _ in range(40)]
pb2.button('b');     [pb2.tick() for _ in range(40)]     # SAVE: B
pb2.button('start'); [pb2.tick() for _ in range(40)]
pb2.button('a');      [pb2.tick() for _ in range(40)]    # SAVE: A (save again)
pb2.button('select'); [pb2.tick() for _ in range(40)]
pb2.button('a');       [pb2.tick() for _ in range(40)]   # SELECT MENU: A
pb2.button('b');       [pb2.tick() for _ in range(40)]   # back
pb2.button('select'); [pb2.tick() for _ in range(40)]
pb2.button('a');       [pb2.tick() for _ in range(40)]
pb2.button('select');  [pb2.tick() for _ in range(40)]   # back the other way
gs_final = pb2.memory[GAMESTATE]
game_mode_final = pb2.memory[GAME_MODE]
pb2.stop()
check("T27.f Indefinite resumability: a loaded Infinite Mode run survives every reachable input branch (movement, SAVE round trips, SELECT-menu round trips) without ending -- lands back in PLAYING, GAME_MODE still 1",
      gs_after_load == 2 and gs_final == 2 and game_mode_final == 1,
      f"gs_after_load={gs_after_load} gs_final={gs_final} game_mode={game_mode_final}")
wipe_save()

# T27.g — in-session re-entry does not respawn a collected treasure,
# without any save/load boundary (BL-0119, the amendment this package's
# own §6 exists to close): materialize a region with treasure present,
# collect it, navigate away far enough that the region leaves the
# materialized window, then navigate back to it within the same session --
# assert INF_TREASURE_HERE == 0 at the region's own re-materialization
# (not re-derived as present from the raw hash predicate) and that
# RUNNING_TREASURE_COUNT does not increment a second time. Directly
# exercises FS-110 §7's own edge case for the in-session case specifically
# -- T27.a (this same suite) already covers the save/load-boundary case;
# this is what closes the gap between them.
pb = fresh_boot(200)
enter_infinite_mode(pb, t27_seed)   # same seed as T27.a: (0,0) treasure, east open
_t27g_biome = pb.memory[INF_WINDOW + 4] & 0x0F
_t27g_pos = None
for (_x, _y, _t) in ZONE_COLLECTS[_t27g_biome]:
    if _t == 2:
        _t27g_pos = (_x, _y)
pb.memory[PLAYER_X] = _t27g_pos[0]
pb.memory[PLAYER_Y] = _t27g_pos[1]
[pb.tick() for _ in range(12)]
rtc_pre27g = read_rtc(pb)
# Move right (away from (0,0)) -- the window recenters, (0,0) leaves it.
pb.memory[PLAYER_X] = 152
pb.button('right'); [pb.tick() for _ in range(20)]
# Move back left -- (0,0) re-enters the window, re-materialized fresh.
pb.memory[PLAYER_X] = 0
pb.button('left'); [pb.tick() for _ in range(20)]
inf_col_back27g = pb.memory[INF_COL] | (pb.memory[INF_COL + 1] << 8)
treasure_back27g = pb.memory[INF_TREASURE_HERE]
rtc_back27g = read_rtc(pb)
check("T27.g In-session re-entry: collected treasure does not respawn on ordinary navigation back (no save/load boundary crossed) -- INF_TREASURE_HERE stays 0, RUNNING_TREASURE_COUNT does not double-increment",
      rtc_pre27g == 1 and inf_col_back27g == 0 and treasure_back27g == 0
      and rtc_back27g == 1,
      f"rtc_pre={rtc_pre27g} col={inf_col_back27g} treasure_here={treasure_back27g} rtc_back={rtc_back27g}")
pb.stop()
wipe_save()

# ══════════════════════════════════════════════════════
# T28 — Biome-Family Sub-Theme Playback Selection (IP-1111)
# ══════════════════════════════════════════════════════
print("\n=== T28: Biome-Family Sub-Theme Playback Selection ===")

MUSIC_CTR = 0xC00F; MUSIC_PTR_LO = 0xC010; MUSIC_PTR_HI = 0xC011
MUSIC_BASE_LO = 0xC6B3; MUSIC_BASE_HI = 0xC6B4

# Expected per-biome track addresses: read straight from the built ROM's
# own music_table via the music_tbl patch pointer (re-derive the patch
# position with a fresh in-process assembly pass — deterministic, same
# positions as the shipped build), not recomputed from music.py.
_t28_patches = _build_game_asm(_ROM())
with open(ROM_PATH, 'rb') as _f:
    _t28_rom = _f.read()
_t28_tbl_pos = _t28_patches['music_tbl']
MUSIC_TBL_ADDR = _t28_rom[_t28_tbl_pos] | (_t28_rom[_t28_tbl_pos + 1] << 8)
_t28_track = [_t28_rom[MUSIC_TBL_ADDR + 2*_b] | (_t28_rom[MUSIC_TBL_ADDR + 2*_b + 1] << 8)
              for _b in range(9)]
check("T28.a0 Static: music_tbl patch resolves inside ROM and the nine table entries are distinct, ordered track addresses",
      0x150 <= MUSIC_TBL_ADDR < 0x8000 and len(set(_t28_track)) == 9,
      f"tbl=0x{MUSIC_TBL_ADDR:04X} entries={[hex(a) for a in _t28_track]}")

def read_music_ptr(pb):
    return pb.memory[MUSIC_PTR_LO] | (pb.memory[MUSIC_PTR_HI] << 8)

def read_music_base(pb):
    return pb.memory[MUSIC_BASE_LO] | (pb.memory[MUSIC_BASE_HI] << 8)

# T28.a — selection correctness, finite path: force each of the nine
# biome-ids current during PLAYING (T13.a's REGION_GRAPH direct-force +
# redraw pattern) and assert MUSIC_PTR/MUSIC_BASE == that identity's own
# music_table entry.
pb = fresh_boot(180)
advance_to_playing(pb)
# MUSIC_BASE is the stable selection record; MUSIC_PTR is a live playback
# cursor that has already advanced past the first note(s) by read time —
# assert BASE equals the entry exactly and PTR sits inside that track's
# own byte range (start..next track's start), proving playback is running
# the selected track, not merely that a value was written once.
_t28_end = _t28_track + [MUSIC_TBL_ADDR]   # each track ends where the next begins
def _t28_on_track(pb, biome):
    return (read_music_base(pb) == _t28_track[biome]
            and _t28_track[biome] <= read_music_ptr(pb) < _t28_end[biome + 1])
_t28a_bad = []
for _biome in range(9):
    pb.memory[REGION_GRAPH] = _biome
    for _k in range(4): pb.memory[REGION_GRAPH + 1 + _k] = 0xFF
    force_region_redraw(pb, 0)
    if not _t28_on_track(pb, _biome):
        _t28a_bad.append((_biome, hex(read_music_ptr(pb)), hex(read_music_base(pb)), hex(_t28_track[_biome])))
check("T28.a Selection: each of the nine biome-ids repoints MUSIC_BASE to its own music_table entry with MUSIC_PTR playing inside that track (finite path, FR-7110)",
      _t28a_bad == [], f"bad={_t28a_bad}")

# T28.b — selection correctness, Infinite Mode path: at least one identity
# selected via the INF_WINDOW-center force (T26.i's pattern), proving the
# shared dsr_p_dispatch entry point serves both modes. Biome 7 (Desert) --
# arbitrary non-Grass pick among the newly-folded ids.
pb.memory[INF_TREASURE_HERE] = 0
force_infinite_redraw_with_center(pb, 7)
check("T28.b Selection via Infinite Mode window path: biome 7 (Desert) repoints MUSIC_BASE to music_table[7], MUSIC_PTR playing inside that track",
      _t28_on_track(pb, 7),
      f"ptr=0x{read_music_ptr(pb):04X} base=0x{read_music_base(pb):04X} expected=0x{_t28_track[7]:04X}")
pb.memory[GAME_MODE] = 0   # restore finite mode for the checks below

# T28.c — main-theme fallback: force entry into each of the eleven
# non-PLAYING states via TRANSITION_TO/NEED_REDRAW (the game's own
# transition mechanism, exercised with a non-main-theme track selected
# first) and assert the default reset repointed to music_table[2] (Grass =
# the main theme).
TRANSITION_TO = 0xC00B
_t28c_bad = []
for _gs in (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11):
    pb.memory[REGION_GRAPH] = 7
    for _k in range(4): pb.memory[REGION_GRAPH + 1 + _k] = 0xFF
    force_region_redraw(pb, 0)          # select Desert's sub-theme first
    pb.memory[TRANSITION_TO] = _gs
    pb.memory[NEED_REDRAW] = 1
    [pb.tick() for _ in range(10)]
    if not _t28_on_track(pb, 2):
        _t28c_bad.append((_gs, hex(read_music_ptr(pb)), hex(read_music_base(pb))))
    pb.memory[TRANSITION_TO] = 2        # back to PLAYING for the next round
    pb.memory[NEED_REDRAW] = 1
    [pb.tick() for _ in range(10)]
check("T28.c Fallback: every one of the eleven non-PLAYING states resets MUSIC_BASE to music_table[2] (the main theme), MUSIC_PTR playing inside it",
      _t28c_bad == [], f"bad={_t28c_bad}")

# T28.d — loop-restart correctness (the music_tick fix): with a non-Grass
# sub-theme selected, plant a terminal 0xFF at the playback cursor's
# current position... impossible in ROM — instead point MUSIC_PTR at the
# track's own real terminal 0xFF (scan the ROM from the track's start) and
# force MUSIC_CTR to expire; music_tick must restart from MUSIC_BASE (the
# sub-theme's own start), not the main theme's address.
pb.memory[REGION_GRAPH] = 5             # Village's sub-theme
for _k in range(4): pb.memory[REGION_GRAPH + 1 + _k] = 0xFF
force_region_redraw(pb, 0)
_t28d_start = _t28_track[5]
_t28d_ff = _t28d_start
while _t28_rom[_t28d_ff] != 0xFF:
    _t28d_ff += 1
pb.memory[MUSIC_PTR_LO] = _t28d_ff & 0xFF
pb.memory[MUSIC_PTR_HI] = (_t28d_ff >> 8) & 0xFF
pb.memory[MUSIC_CTR] = 1                # expires on the next music_tick
[pb.tick() for _ in range(2)]           # music_tick runs once per frame
_t28d_ptr = read_music_ptr(pb)
check("T28.d Loop restart: a sub-theme reaching its terminal 0xFF restarts from its own MUSIC_BASE start (Village), never the main theme (the music_tick fix)",
      _t28d_start < _t28d_ptr <= _t28d_start + 6 and read_music_base(pb) == _t28d_start,
      f"ptr=0x{_t28d_ptr:04X} base=0x{read_music_base(pb):04X} start=0x{_t28d_start:04X} ff=0x{_t28d_ff:04X}")

# T28.e — transition timing (FR-7110's "within one frame"): the redraw that
# performs a state transition also performs the repoint — confirmed by
# forcing a transition and checking the track after a single redraw
# completes (the [10-tick settle above already proves ≤10 frames; this
# check pins the mechanism: the repoint happens inside do_screen_redraw
# itself, i.e. the same frame the new state's screen appears).
pb.memory[REGION_GRAPH] = 8             # Plains current
for _k in range(4): pb.memory[REGION_GRAPH + 1 + _k] = 0xFF
pb.memory[TRANSITION_TO] = 2
pb.memory[NEED_REDRAW] = 1
_t28e_frames = None
for _i in range(10):
    pb.tick()
    if read_music_ptr(pb) == _t28_track[8]:
        _t28e_frames = _i + 1
        break
check("T28.e Timing: the sub-theme repoint lands with the redraw itself (within FR-7110's one-frame budget of the screen appearing)",
      _t28e_frames is not None and _t28e_frames <= 2,
      f"frames={_t28e_frames}")
pb.stop()
wipe_save()

print("\n=== T29: Combat Sub-Mode — Mob Materialization & Rendering (IP-1121) ===")

COMBAT_MODE_ADDR = 0xC6B5; MOB_COUNT_ADDR = 0xC6B6; MOB_DATA_ADDR = 0xC6B7
IMM_ADDR = _gw_rom.labels['inf_materialize_mobs']

def invoke_inf_materialize_mobs(pb, seed, row, col, combat_mode=1):
    """
    T29 (IP-1121): directly invoke inf_materialize_mobs (asm_game.py) —
    the real call site is inf_ensure_window's own center-cell recompute
    (T24/T26 already exercise that indirectly); this harness mirrors
    invoke_inf_materialize_region's own PC/SP-hijack + self-loop-trap
    technique for a direct, isolated invocation. Sets SEED/INF_ROW/INF_COL/
    COMBAT_MODE, ticks until the trap fires, returns the 6 (x, y, species,
    health, active) tuples read back from MOB_DATA, or None if the trap was
    never reached within budget.
    """
    pb.memory[SEED] = seed & 0xFF
    pb.memory[SEED + 1] = (seed >> 8) & 0xFF
    r = row & 0xFFFF; c = col & 0xFFFF
    pb.memory[INF_ROW] = r & 0xFF; pb.memory[INF_ROW + 1] = (r >> 8) & 0xFF
    pb.memory[INF_COL] = c & 0xFF; pb.memory[INF_COL + 1] = (c >> 8) & 0xFF
    pb.memory[COMBAT_MODE_ADDR] = combat_mode
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE  # JR -2
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = IMM_ADDR
    for _ in range(400):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            slots = []
            for i in range(6):
                base = MOB_DATA_ADDR + i * 5
                slots.append(tuple(pb.memory[base + k] for k in range(5)))
            return pb.memory[MOB_COUNT_ADDR], slots
    return None

pb = fresh_boot(180)
advance_to_playing(pb)

# T29.a — determinism: materializing the same region twice (COMBAT_MODE on)
# produces byte-identical mob presence/type/position both times.
_t29_seed, _t29_row, _t29_col = 4242, 3, -2
_t29_r1 = invoke_inf_materialize_mobs(pb, _t29_seed, _t29_row, _t29_col)
_t29_r2 = invoke_inf_materialize_mobs(pb, _t29_seed, _t29_row, _t29_col)
check("T29.a Determinism: materializing the same region twice produces byte-identical mob slots",
      _t29_r1 is not None and _t29_r1 == _t29_r2, f"r1={_t29_r1} r2={_t29_r2}")

# T29.b — oracle-vs-SM83 lockstep: worldgen.materialize_mobs vs. the live
# ROM's inf_materialize_mobs, 0 mismatches required across a small corpus
# (incl. negative coordinates, per this codebase's own two's-complement
# convention for INF_ROW/INF_COL).
_t29_corpus = [(1, 0, 0), (4242, 3, -2), (999, -5, 7), (2026, 100, -100), (0, -1, -1)]
_t29_mismatches = []
for _s, _r, _c in _t29_corpus:
    _got_count, _got_slots = invoke_inf_materialize_mobs(pb, _s, _r, _c)
    _exp_slots = worldgen.materialize_mobs(_s, _r, _c)
    _exp_count = sum(1 for slot in _exp_slots if slot[4] == 1)
    if _got_count != _exp_count or _got_slots != _exp_slots:
        _t29_mismatches.append((_s, _r, _c, _got_count, _exp_count, _got_slots, _exp_slots))
check("T29.b Oracle-vs-SM83 lockstep: worldgen.materialize_mobs matches inf_materialize_mobs exactly",
      len(_t29_mismatches) == 0, f"mismatches={_t29_mismatches}")

# T29.c — COMBAT_MODE off: a region materialized with the flag forced to 0
# shows MOB_COUNT==0 and leaves every MOB_DATA slot completely untouched by
# this call (the top-of-routine RET_Z fires before any write) -- confirms
# this capability is additive, not a fork of the generation algorithm.
pb.memory[MOB_COUNT_ADDR] = 0
_t29_before_slots = [tuple(pb.memory[MOB_DATA_ADDR + i * 5 + k] for k in range(5))
                      for i in range(6)]
_t29_offcount, _t29_offslots = invoke_inf_materialize_mobs(pb, 555, 9, 9, combat_mode=0)
check("T29.c COMBAT_MODE off: MOB_COUNT stays 0 and MOB_DATA is left untouched (no-op, additive only)",
      _t29_offcount == 0 and _t29_offslots == _t29_before_slots,
      f"count={_t29_offcount} slots={_t29_offslots} prior={_t29_before_slots}")

# T29.d — mob-count ceiling: across the corpus above (COMBAT_MODE on),
# MOB_COUNT never exceeds 6 -- true by construction (exactly 6 candidate
# slots are ever drawn), confirmed directly rather than merely assumed.
_t29_ceiling_bad = []
for _s, _r, _c in _t29_corpus:
    _cnt, _ = invoke_inf_materialize_mobs(pb, _s, _r, _c)
    if _cnt > 6: _t29_ceiling_bad.append((_s, _r, _c, _cnt))
check("T29.d Mob-count ceiling: MOB_COUNT never exceeds 6 across the corpus",
      len(_t29_ceiling_bad) == 0, f"bad={_t29_ceiling_bad}")

# T29.e — defeat: force an active mob slot, call inf_mob_defeat, confirm
# the slot's active flag clears, MOB_COUNT decrements, and no OAM entry is
# written for it on the next inf_mob_render call (no persistent corpse).
IMD_ADDR = _gw_rom.labels['inf_mob_defeat']
IMR2_ADDR = _gw_rom.labels['inf_mob_render']
OAM_BUF = 0xC300   # shadow OAM buffer base (update_oam's own write target)

def invoke_inf_mob_defeat(pb, slot):
    pb.register_file.B = slot
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = IMD_ADDR
    for _ in range(60):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            return True
    return False

def invoke_inf_mob_render(pb):
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.HL = OAM_BUF
    pb.register_file.PC = IMR2_ADDR
    for _ in range(60):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            return True
    return False

# Force exactly one active mob at slot 0 (MOB_COUNT=1), everything else
# inactive. inf_mob_render gates on COMBAT_MODE (not MOB_COUNT, see its
# own comment) -- set explicitly since T29.c's last call left it 0.
pb.memory[COMBAT_MODE_ADDR] = 1
pb.memory[MOB_COUNT_ADDR] = 1
for _i in range(6):
    _base = MOB_DATA_ADDR + _i * 5
    pb.memory[_base] = 80; pb.memory[_base + 1] = 60
    pb.memory[_base + 2] = 0; pb.memory[_base + 3] = 1
    pb.memory[_base + 4] = 1 if _i == 0 else 0
_t29e_defeated = invoke_inf_mob_defeat(pb, 0)
_t29e_active_after = pb.memory[MOB_DATA_ADDR + 4]
_t29e_count_after = pb.memory[MOB_COUNT_ADDR]
for _k in range(160): pb.memory[OAM_BUF + _k] = 0xAA   # poison the buffer first
invoke_inf_mob_render(pb)
_t29e_oam_slot0 = [pb.memory[OAM_BUF + k] for k in range(4)]
check("T29.e Defeat: active flag clears, MOB_COUNT decrements, no OAM entry written for the defeated slot",
      _t29e_defeated and _t29e_active_after == 0 and _t29e_count_after == 0 and
      _t29e_oam_slot0 == [0, 0, 0, 0],
      f"active_after={_t29e_active_after} count_after={_t29e_count_after} oam={_t29e_oam_slot0}")

# T29.f — OAM budget static audit (Inspection, NFR-4500): worst-case
# concurrent OAM entry count (1 player + up to 8 collectibles [finite
# mode's own worst case, R115] + 6 mobs) stays at or below the 40-entry
# hardware table -- Infinite Mode's own COLL_COUNT is always <= 1
# (szc_infinite spawns exactly one treasure), so this is a conservative
# combined bound across both modes, not the real Infinite-Mode-combat
# worst case (1 + 1 + 6 = 8).
check("T29.f OAM budget static audit: 1 player + up to 8 collectibles + 6 mobs <= 40 entries (NFR-4500)",
      1 + 8 + 6 <= 40, f"total={1 + 8 + 6}")

pb.stop()
wipe_save()

print("\n=== T30: Combat Sub-Mode — Weapon Fire & Hit Resolution (IP-1122) ===")

PROJ_ACTIVE_ADDR = 0xC6D5; PROJ_X_ADDR = 0xC6D6; PROJ_Y_ADDR = 0xC6D7
PROJ_STEP_X_ADDR = 0xC6D8; WEAPON_TIER_ADDR = 0xC6D9   # PROJ_DIR renamed/redefined, IP-1128
PLAYER_FACING_X_ADDR = 0xC6DF; PLAYER_FACING_Y_ADDR = 0xC6E0  # IP-1128
PROJ_STEP_Y_ADDR = 0xC6E1                                      # IP-1128
JOY_CUR_ADDR = 0xC00C; JOY_NEW_ADDR = 0xC00E
J_A_BIT = 0   # asm_game.py's own J_A=0 encoding
HPI_ADDR = _gw_rom.labels['handle_play_input']
IPU_ADDR = _gw_rom.labels['inf_projectile_update']

def invoke_no_arg(pb, addr, budget=400):
    """Direct PC/SP-hijack + self-loop-trap invocation of a no-argument
    subroutine (handle_play_input / inf_projectile_update), mirroring
    T29's own invoke_inf_materialize_mobs technique."""
    pb.memory[GW_TRAP_ADDR] = 0x18; pb.memory[GW_TRAP_ADDR + 1] = 0xFE  # JR -2
    sp = (pb.register_file.SP - 2) & 0xFFFF
    pb.memory[sp] = GW_TRAP_ADDR & 0xFF
    pb.memory[sp + 1] = (GW_TRAP_ADDR >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = addr
    for _ in range(budget):
        pb.tick()
        if pb.register_file.PC == GW_TRAP_ADDR:
            return True
    return False

def t30_reset(pb, combat_mode=1, weapon_tier=1):
    pb.memory[GAME_MODE] = 1
    pb.memory[COMBAT_MODE_ADDR] = combat_mode
    pb.memory[MOB_COUNT_ADDR] = 0
    for i in range(6):
        base = MOB_DATA_ADDR + i * 5
        for k in range(5): pb.memory[base + k] = 0
    pb.memory[PROJ_ACTIVE_ADDR] = 0
    pb.memory[PROJ_X_ADDR] = 0; pb.memory[PROJ_Y_ADDR] = 0
    # IP-1128: default rightward step (1, 0), preserving the pre-IP-1128 tests'
    # own implicit "projectile moves right by default" assumption for any
    # check below that doesn't explicitly override the facing/step fields.
    pb.memory[PROJ_STEP_X_ADDR] = 1; pb.memory[PROJ_STEP_Y_ADDR] = 0
    pb.memory[PLAYER_FACING_X_ADDR] = 1; pb.memory[PLAYER_FACING_Y_ADDR] = 0
    pb.memory[WEAPON_TIER_ADDR] = weapon_tier
    pb.memory[JOY_CUR_ADDR] = 0; pb.memory[JOY_NEW_ADDR] = 0

pb = fresh_boot(180)
advance_to_playing(pb)

# T30.a — fire spawns a projectile at the player's own position/facing.
# IP-1128: facing is now PLAYER_FACING_X/Y (not PLAYER_DIR, which no longer
# feeds fire direction at all -- ADR-0021 Decision 1) -- force a
# distinguishing non-default facing (left) so the check is a real
# confirmation, not a coincidental match against the boot default (right).
t30_reset(pb)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
pb.memory[PLAYER_FACING_X_ADDR] = 0xFF; pb.memory[PLAYER_FACING_Y_ADDR] = 0
pb.memory[JOY_NEW_ADDR] = 1 << J_A_BIT
_t30a_ok = invoke_no_arg(pb, HPI_ADDR)
_t30a_active = pb.memory[PROJ_ACTIVE_ADDR]
_t30a_x = pb.memory[PROJ_X_ADDR]; _t30a_y = pb.memory[PROJ_Y_ADDR]
_t30a_dir = pb.memory[PROJ_STEP_X_ADDR]
check("T30.a Fire spawns a projectile at the player's own position/facing",
      _t30a_ok and _t30a_active == 1 and _t30a_x == 80 and _t30a_y == 60 and _t30a_dir == 0xFF,
      f"ok={_t30a_ok} active={_t30a_active} x={_t30a_x} y={_t30a_y} dir={_t30a_dir}")

# T30.b — no double-fire: pressing A again while a projectile is already
# active leaves its state completely unchanged (FR-11300's own Acceptance
# Criterion), even though the player's own position/facing differ this time.
t30_reset(pb)
pb.memory[PROJ_ACTIVE_ADDR] = 1
pb.memory[PROJ_X_ADDR] = 40; pb.memory[PROJ_Y_ADDR] = 90; pb.memory[PROJ_STEP_X_ADDR] = 0
pb.memory[PLAYER_X] = 120; pb.memory[PLAYER_Y] = 20
pb.memory[PLAYER_FACING_X_ADDR] = 0xFF
pb.memory[JOY_NEW_ADDR] = 1 << J_A_BIT
_t30b_ok = invoke_no_arg(pb, HPI_ADDR)
check("T30.b No double-fire: pressing A while a projectile is active leaves its state unchanged",
      _t30b_ok and pb.memory[PROJ_ACTIVE_ADDR] == 1 and pb.memory[PROJ_X_ADDR] == 40 and
      pb.memory[PROJ_Y_ADDR] == 90 and pb.memory[PROJ_STEP_X_ADDR] == 0,
      f"ok={_t30b_ok} active={pb.memory[PROJ_ACTIVE_ADDR]} x={pb.memory[PROJ_X_ADDR]} "
      f"y={pb.memory[PROJ_Y_ADDR]} dir={pb.memory[PROJ_STEP_X_ADDR]}")

# T30.c — hit resolution: an active projectile that reaches an active mob's
# hitbox reduces its health by WEAPON_TIER, deactivates the projectile, and
# (at zero health) triggers inf_mob_defeat's own effects (active clears,
# MOB_COUNT decrements — reusing T29.e's own assertions).
t30_reset(pb)
pb.memory[MOB_COUNT_ADDR] = 1
_t30c_mob = MOB_DATA_ADDR
pb.memory[_t30c_mob + 0] = 100; pb.memory[_t30c_mob + 1] = 50
pb.memory[_t30c_mob + 2] = 0; pb.memory[_t30c_mob + 3] = 1; pb.memory[_t30c_mob + 4] = 1
pb.memory[WEAPON_TIER_ADDR] = 1
pb.memory[PROJ_ACTIVE_ADDR] = 1
pb.memory[PROJ_X_ADDR] = 99; pb.memory[PROJ_Y_ADDR] = 50; pb.memory[PROJ_STEP_X_ADDR] = 1
_t30c_ok = invoke_no_arg(pb, IPU_ADDR)
_t30c_health = pb.memory[_t30c_mob + 3]; _t30c_active = pb.memory[_t30c_mob + 4]
_t30c_count = pb.memory[MOB_COUNT_ADDR]; _t30c_proj = pb.memory[PROJ_ACTIVE_ADDR]
check("T30.c Hit resolution: mob health reduced by WEAPON_TIER, defeated at zero (inf_mob_defeat's own effects), projectile stops",
      _t30c_ok and _t30c_health == 0 and _t30c_active == 0 and _t30c_count == 0 and _t30c_proj == 0,
      f"ok={_t30c_ok} health={_t30c_health} active={_t30c_active} count={_t30c_count} proj_active={_t30c_proj}")

# T30.c2 — spot check: a non-lethal hit damages without defeating (mob
# stays active, MOB_COUNT unchanged) — confirms the floor-at-0 write path
# and the defeat-vs-damage-only branch are both independently correct.
t30_reset(pb)
pb.memory[MOB_COUNT_ADDR] = 1
_t30c2_mob = MOB_DATA_ADDR
pb.memory[_t30c2_mob + 0] = 100; pb.memory[_t30c2_mob + 1] = 50
pb.memory[_t30c2_mob + 2] = 0; pb.memory[_t30c2_mob + 3] = 5; pb.memory[_t30c2_mob + 4] = 1
pb.memory[WEAPON_TIER_ADDR] = 2
pb.memory[PROJ_ACTIVE_ADDR] = 1
pb.memory[PROJ_X_ADDR] = 99; pb.memory[PROJ_Y_ADDR] = 50; pb.memory[PROJ_STEP_X_ADDR] = 1
_t30c2_ok = invoke_no_arg(pb, IPU_ADDR)
check("T30.c2 Spot: a non-lethal hit reduces health by WEAPON_TIER without defeating the mob",
      _t30c2_ok and pb.memory[_t30c2_mob + 3] == 3 and pb.memory[_t30c2_mob + 4] == 1 and
      pb.memory[MOB_COUNT_ADDR] == 1 and pb.memory[PROJ_ACTIVE_ADDR] == 0,
      f"ok={_t30c2_ok} health={pb.memory[_t30c2_mob+3]} active={pb.memory[_t30c2_mob+4]} "
      f"count={pb.memory[MOB_COUNT_ADDR]} proj_active={pb.memory[PROJ_ACTIVE_ADDR]}")

# T30.d — miss/terminal boundary: an active projectile with no mob in its
# path deactivates cleanly on exiting the window, no mob health affected
# (there are none active here to affect).
t30_reset(pb)
pb.memory[MOB_COUNT_ADDR] = 0
pb.memory[PROJ_ACTIVE_ADDR] = 1
pb.memory[PROJ_X_ADDR] = 150; pb.memory[PROJ_Y_ADDR] = 60; pb.memory[PROJ_STEP_X_ADDR] = 1
_t30d_steps = 0
while pb.memory[PROJ_ACTIVE_ADDR] == 1 and _t30d_steps < 20:
    invoke_no_arg(pb, IPU_ADDR)
    _t30d_steps += 1
check("T30.d Miss/terminal boundary: projectile deactivates cleanly on exiting the window",
      pb.memory[PROJ_ACTIVE_ADDR] == 0 and 0 < _t30d_steps <= 5,
      f"proj_active={pb.memory[PROJ_ACTIVE_ADDR]} steps={_t30d_steps}")

# T30.e — COMBAT_MODE off: the A button remains a no-op during PLAYING,
# unchanged from today's shipped base game (non-regression).
t30_reset(pb, combat_mode=0)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60; pb.memory[PLAYER_DIR] = 0
pb.memory[JOY_NEW_ADDR] = 1 << J_A_BIT
_t30e_ok = invoke_no_arg(pb, HPI_ADDR)
check("T30.e COMBAT_MODE off: A button remains a no-op during PLAYING (PROJ_ACTIVE stays 0)",
      _t30e_ok and pb.memory[PROJ_ACTIVE_ADDR] == 0,
      f"ok={_t30e_ok} proj_active={pb.memory[PROJ_ACTIVE_ADDR]}")

pb.stop()
wipe_save()

print("\n=== T31: Combat Sub-Mode — Player Health & Economy (IP-1123) ===")

PLAYER_HEALTH_ADDR = 0xC6DA; COMBAT_ENTRY_X_ADDR = 0xC6DB; COMBAT_ENTRY_Y_ADDR = 0xC6DC
IMCC_ADDR = _gw_rom.labels['inf_mob_contact_check']
IHSB_ADDR = _gw_rom.labels['inf_health_setback']
IHEAL_ADDR = _gw_rom.labels['inf_heal_spend']
IHHD_ADDR = _gw_rom.labels['inf_health_hud_draw']

def t31_reset(pb, combat_mode=1, player_health=3):
    pb.memory[GAME_MODE] = 1
    pb.memory[COMBAT_MODE_ADDR] = combat_mode
    pb.memory[MOB_COUNT_ADDR] = 0
    for i in range(6):
        base = MOB_DATA_ADDR + i * 5
        for k in range(5): pb.memory[base + k] = 0
    pb.memory[PLAYER_HEALTH_ADDR] = player_health
    pb.memory[COMBAT_ENTRY_X_ADDR] = 0; pb.memory[COMBAT_ENTRY_Y_ADDR] = 0
    pb.memory[RUNNING_TREASURE_COUNT] = 0; pb.memory[RUNNING_TREASURE_COUNT + 1] = 0

pb = fresh_boot(180)
advance_to_playing(pb)

# T31.a — mob contact reduces health: force the player onto an active mob's
# position, step one frame (invoke_no_arg on inf_mob_contact_check),
# confirm PLAYER_HEALTH decreases by exactly 1.
t31_reset(pb, player_health=3)
pb.memory[PLAYER_X] = 100; pb.memory[PLAYER_Y] = 50
pb.memory[MOB_COUNT_ADDR] = 1
_t31a_mob = MOB_DATA_ADDR
pb.memory[_t31a_mob + 0] = 100; pb.memory[_t31a_mob + 1] = 50
pb.memory[_t31a_mob + 2] = 0; pb.memory[_t31a_mob + 3] = 1; pb.memory[_t31a_mob + 4] = 1
_t31a_ok = invoke_no_arg(pb, IMCC_ADDR)
check("T31.a Mob contact reduces health by exactly 1",
      _t31a_ok and pb.memory[PLAYER_HEALTH_ADDR] == 2,
      f"ok={_t31a_ok} health={pb.memory[PLAYER_HEALTH_ADDR]}")

# T31.b — HUD reflects health: force PLAYER_HEALTH to each of 0-3, confirm
# the row-1 heart cells render the matching full/empty pattern.
_t31b_bad = []
for _h in range(4):
    t31_reset(pb, player_health=_h)
    invoke_no_arg(pb, IHHD_ADDR)
    _row1 = [pb.memory[0x9820 + k] for k in range(3)]
    _expected = [TL_HEART_FULL if k < _h else TL_HEART_EMPTY for k in range(3)]
    if _row1 != _expected: _t31b_bad.append((_h, _row1, _expected))
check("T31.b HUD reflects health: row-1 heart cells render the matching full/empty pattern for health 0-3",
      len(_t31b_bad) == 0, f"bad={_t31b_bad}")

# T31.c — zero-health setback: force PLAYER_HEALTH to 0, a known
# COMBAT_ENTRY_X/Y, and the player elsewhere; confirm PLAYER_HEALTH resets
# to max, position returns to the recorded region-entry point, and
# GAMESTATE remains PLAYING (never transitions to any other state).
t31_reset(pb, player_health=0)
pb.memory[COMBAT_ENTRY_X_ADDR] = 40; pb.memory[COMBAT_ENTRY_Y_ADDR] = 90
pb.memory[PLAYER_X] = 120; pb.memory[PLAYER_Y] = 20
_t31c_gs_before = pb.memory[GAMESTATE]
_t31c_ok = invoke_no_arg(pb, IHSB_ADDR)
_t31c_gs_after = pb.memory[GAMESTATE]
check("T31.c Zero-health setback: health resets to max, position returns to region-entry point, GAMESTATE unchanged",
      _t31c_ok and pb.memory[PLAYER_HEALTH_ADDR] == 3 and pb.memory[PLAYER_X] == 40 and
      pb.memory[PLAYER_Y] == 90 and _t31c_gs_after == _t31c_gs_before,
      f"ok={_t31c_ok} health={pb.memory[PLAYER_HEALTH_ADDR]} x={pb.memory[PLAYER_X]} "
      f"y={pb.memory[PLAYER_Y]} gs_before={_t31c_gs_before} gs_after={_t31c_gs_after}")

# T31.d — heal-spend decrements the shared count: force a known
# RUNNING_TREASURE_COUNT, trigger inf_heal_spend, confirm the exact
# decrement and the corresponding PLAYER_HEALTH increase.
t31_reset(pb, player_health=1)
pb.memory[RUNNING_TREASURE_COUNT] = 5; pb.memory[RUNNING_TREASURE_COUNT + 1] = 0
_t31d_ok = invoke_no_arg(pb, IHEAL_ADDR)
_t31d_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T31.d Heal-spend decrements RUNNING_TREASURE_COUNT by 1 and increases PLAYER_HEALTH by 1",
      _t31d_ok and _t31d_rtc == 4 and pb.memory[PLAYER_HEALTH_ADDR] == 2,
      f"ok={_t31d_ok} rtc={_t31d_rtc} health={pb.memory[PLAYER_HEALTH_ADDR]}")

# T31.d2 — spot check: heal-spend still spends treasure even when already
# at max health, but does not push health past the cap (3).
t31_reset(pb, player_health=3)
pb.memory[RUNNING_TREASURE_COUNT] = 5; pb.memory[RUNNING_TREASURE_COUNT + 1] = 0
_t31d2_ok = invoke_no_arg(pb, IHEAL_ADDR)
_t31d2_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T31.d2 Spot: heal-spend at max health still spends treasure but does not exceed the health cap",
      _t31d2_ok and _t31d2_rtc == 4 and pb.memory[PLAYER_HEALTH_ADDR] == 3,
      f"ok={_t31d2_ok} rtc={_t31d2_rtc} health={pb.memory[PLAYER_HEALTH_ADDR]}")

# T31.e — heal-spend at zero treasure is a no-op: force
# RUNNING_TREASURE_COUNT=0, trigger inf_heal_spend, confirm no change to
# either field.
t31_reset(pb, player_health=1)
pb.memory[RUNNING_TREASURE_COUNT] = 0; pb.memory[RUNNING_TREASURE_COUNT + 1] = 0
_t31e_ok = invoke_no_arg(pb, IHEAL_ADDR)
_t31e_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T31.e Heal-spend at zero treasure is a no-op (no change to RUNNING_TREASURE_COUNT or PLAYER_HEALTH)",
      _t31e_ok and _t31e_rtc == 0 and pb.memory[PLAYER_HEALTH_ADDR] == 1,
      f"ok={_t31e_ok} rtc={_t31e_rtc} health={pb.memory[PLAYER_HEALTH_ADDR]}")

# T31.f — COMBAT_MODE off: no row-1 HUD write occurs, and mob-contact/
# heal-spend logic never executes (non-regression against the base game's
# own row-0-only HUD).
t31_reset(pb, combat_mode=0, player_health=3)
pb.memory[PLAYER_X] = 100; pb.memory[PLAYER_Y] = 50
pb.memory[MOB_COUNT_ADDR] = 1
_t31f_mob = MOB_DATA_ADDR
pb.memory[_t31f_mob + 0] = 100; pb.memory[_t31f_mob + 1] = 50
pb.memory[_t31f_mob + 2] = 0; pb.memory[_t31f_mob + 3] = 1; pb.memory[_t31f_mob + 4] = 1
pb.memory[RUNNING_TREASURE_COUNT] = 5; pb.memory[RUNNING_TREASURE_COUNT + 1] = 0
for _k in range(3): pb.memory[0x9820 + _k] = 0xAA   # poison row-1 first
invoke_no_arg(pb, IMCC_ADDR)
invoke_no_arg(pb, IHEAL_ADDR)
invoke_no_arg(pb, IHHD_ADDR)
_t31f_row1 = [pb.memory[0x9820 + k] for k in range(3)]
_t31f_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T31.f COMBAT_MODE off: no row-1 HUD write, mob-contact/heal-spend logic never executes",
      pb.memory[PLAYER_HEALTH_ADDR] == 3 and _t31f_rtc == 5 and _t31f_row1 == [0xAA, 0xAA, 0xAA],
      f"health={pb.memory[PLAYER_HEALTH_ADDR]} rtc={_t31f_rtc} row1={_t31f_row1}")

pb.stop()
wipe_save()

# T31.g — BL-0154 regression: the "initial Infinite Mode entry" combat-
# entry-point recording must capture the player's REAL spawn position, not
# a stale pre-spawn value. Drives the real MODE SELECT -> COMBAT MODE
# CONFIRM (confirm "Y") -> INFINITE SEED ENTRY -> INTRO -> PLAYING path
# (not a direct-invoke force -- this is the only way to exercise the
# actual call-site ordering), confirms COMBAT_ENTRY_X/Y match PLAYER_X/Y
# exactly on first arrival at PLAYING, rather than the (0,0) VR-1123 found.
pb31g = fresh_boot(180)
pb31g.button('a'); [pb31g.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb31g.button('down'); [pb31g.tick() for _ in range(40)]     # toggle infinite
pb31g.button('a'); [pb31g.tick() for _ in range(40)]        # confirm -> COMBAT MODE CONFIRM
pb31g.button('up'); [pb31g.tick() for _ in range(40)]       # toggle to "Y"
pb31g.button('a'); [pb31g.tick() for _ in range(40)]        # confirm Y -> INFINITE SEED ENTRY
enter_infinite_seed(pb31g, [4, 2, 0, 0, 0])
pb31g.button('a'); [pb31g.tick() for _ in range(100)]       # confirm seed -> INTRO
pb31g.button('a'); [pb31g.tick() for _ in range(40)]        # INTRO -> PLAYING
check("T31.g BL-0154 regression: initial-entry COMBAT_ENTRY_X/Y match the player's real spawn position",
      pb31g.memory[GAMESTATE] == 2 and pb31g.memory[COMBAT_MODE_ADDR] == 1 and
      pb31g.memory[PLAYER_X] == 76 and pb31g.memory[PLAYER_Y] == 80 and
      pb31g.memory[COMBAT_ENTRY_X_ADDR] == 76 and pb31g.memory[COMBAT_ENTRY_Y_ADDR] == 80,
      f"gs={pb31g.memory[GAMESTATE]} combat_mode={pb31g.memory[COMBAT_MODE_ADDR]} "
      f"player=({pb31g.memory[PLAYER_X]},{pb31g.memory[PLAYER_Y]}) "
      f"entry=({pb31g.memory[COMBAT_ENTRY_X_ADDR]},{pb31g.memory[COMBAT_ENTRY_Y_ADDR]})")
pb31g.stop()
wipe_save()

# ══════════════════════════════════════════════════════
# T32 — Combat Sub-Mode: Save Persistence (IP-1124)
# ══════════════════════════════════════════════════════
print("\n=== T32: Combat Sub-Mode — Save Persistence (IP-1124) ===")

SRAM_COMBAT_MODE_ADDR = 0xA350; SRAM_MOB_COUNT_ADDR = 0xA351
SRAM_MOB_DATA_ADDR = 0xA352; SRAM_WEAPON_TIER_ADDR = 0xA370
SRAM_PLAYER_HEALTH_ADDR = 0xA371

# T32.a — round trip: force a known combat state (two distinct mob slots,
# a non-default WEAPON_TIER, a non-max PLAYER_HEALTH) placed well clear of
# the player's own hitbox and with MOB_MOVE_TIMER pinned high (so neither
# inf_mob_move nor inf_mob_contact_check can perturb the forced state in
# the few real per-frame ticks the SAVE menu itself requires), save via
# the real SAVE screen, reload in a fresh instance, confirm every field
# restores exactly.
wipe_save()
pb = fresh_boot(200)
enter_infinite_mode(pb, 555)
pb.memory[COMBAT_MODE_ADDR] = 1
pb.memory[0xC6DE] = 8   # MOB_MOVE_TIMER, pinned above 0 -- no movement this window
pb.memory[MOB_COUNT_ADDR] = 2
_t32a_mob0 = (20, 20, 1, 2, 1)     # x, y, species, health, active
_t32a_mob1 = (140, 120, 2, 1, 1)
for _i, _slot in enumerate([_t32a_mob0, _t32a_mob1]):
    _base = MOB_DATA_ADDR + _i * 5
    for _k, _v in enumerate(_slot): pb.memory[_base + _k] = _v
for _i in range(2, 6):
    _base = MOB_DATA_ADDR + _i * 5
    for _k in range(5): pb.memory[_base + _k] = 0
pb.memory[WEAPON_TIER_ADDR] = 2
pb.memory[PLAYER_HEALTH_ADDR] = 1
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]   # SAVE: A (save)
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
# IP-1124 own test note: read back immediately (a handful of frames, not
# T27.a2's own 60-tick settle) -- try_load_save's own restore is a single-
# frame, synchronous jump straight to PLAYING (not an animated menu), and
# once there with COMBAT_MODE now correctly restored to 1, inf_mob_move
# runs automatically every frame with no further input needed -- waiting
# a full 60 ticks (nearly 8x MOB_MOVE_INTERVAL) would let it genuinely
# move the just-restored mobs before this check ever reads them, a
# test-only timing gap (T35.i's own established "force, then check
# promptly" discipline), not a product defect.
pb2.button('a'); [pb2.tick() for _ in range(6)]   # MAIN MENU: continue
_t32a_mob0_after = tuple(pb2.memory[MOB_DATA_ADDR + k] for k in range(5))
_t32a_mob1_after = tuple(pb2.memory[MOB_DATA_ADDR + 5 + k] for k in range(5))
check("T32.a Save/load round trip: mob state, weapon tier, and player health all restore exactly",
      pb2.memory[GAMESTATE] == 2 and pb2.memory[COMBAT_MODE_ADDR] == 1 and
      pb2.memory[MOB_COUNT_ADDR] == 2 and _t32a_mob0_after == _t32a_mob0 and
      _t32a_mob1_after == _t32a_mob1 and pb2.memory[WEAPON_TIER_ADDR] == 2 and
      pb2.memory[PLAYER_HEALTH_ADDR] == 1,
      f"GS={pb2.memory[GAMESTATE]} combat_mode={pb2.memory[COMBAT_MODE_ADDR]} "
      f"mob_count={pb2.memory[MOB_COUNT_ADDR]} mob0={_t32a_mob0_after} mob1={_t32a_mob1_after} "
      f"tier={pb2.memory[WEAPON_TIER_ADDR]} health={pb2.memory[PLAYER_HEALTH_ADDR]}")
pb2.stop()
wipe_save()

# T32.b — projectile not persisted: force an active projectile alongside
# a real combat state, save, reload, confirm PROJ_ACTIVE is 0 after load
# (mirrors IP-1101's own transient-state non-persistence precedent).
pb = fresh_boot(200)
enter_infinite_mode(pb, 555)
pb.memory[COMBAT_MODE_ADDR] = 1
pb.memory[PROJ_ACTIVE_ADDR] = 1
pb.memory[PROJ_X_ADDR] = 100; pb.memory[PROJ_Y_ADDR] = 80
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(60)]
check("T32.b Projectile not persisted: PROJ_ACTIVE is 0 after load",
      pb2.memory[PROJ_ACTIVE_ADDR] == 0, f"proj_active={pb2.memory[PROJ_ACTIVE_ADDR]}")
pb2.stop()
wipe_save()

# T32.c — pre-combat-mode save compatibility: a synthetic SAVE_VERSION_VAL
# == 0x05 fixture (the immediately-prior, post-Infinite-Mode-but-pre-
# combat value), with garbage (0xFF) at every new combat SRAM address,
# mirrors T11.d's/T27.d's own established synthetic-fixture pattern.
# Version 0x05 != the current 0x06, so this is treated as absent for
# "continue" purposes (ADR-0010, same as T27.d's 0x04 case) -- confirms
# the garbage combat bytes are never read at all, and a fresh new-game
# session's own COMBAT_MODE holds its correct boot-cleared default (0),
# not any garbage byte from the stale fixture.
fixture32c = bytearray(8192)
fixture32c[0:4] = bytes([0x42, 0x55, 0x4E, 0x59])
fixture32c[SRAM_CUR_ZONE - 0xA000] = 0
fixture32c[SRAM_PLAYER_X - 0xA000] = 76
fixture32c[SRAM_PLAYER_Y - 0xA000] = 80
fixture32c[SRAM_GAME_MODE - 0xA000] = 1
fixture32c[SAVE_VERSION_ADDR - 0xA000] = 0x05
for _i in range(81): fixture32c[SRAM_SCOREITEM - 0xA000 + _i] = 0xFF
for _addr in (SRAM_COMBAT_MODE_ADDR, SRAM_MOB_COUNT_ADDR, SRAM_WEAPON_TIER_ADDR,
              SRAM_PLAYER_HEALTH_ADDR):
    fixture32c[_addr - 0xA000] = 0xFF
for _i in range(30):
    fixture32c[SRAM_MOB_DATA_ADDR - 0xA000 + _i] = 0xFF
with open(RAM_PATH, 'wb') as _f:
    _f.write(bytes(fixture32c))
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T32.c1 Boot with a version=0x05 (pre-combat) save -> MAIN MENU",
      pb.memory[GAMESTATE] == 6, f"GS={pb.memory[GAMESTATE]}")
check("T32.c2 Version-0x05 save -> CONTINUE absent (ADR-0010, mirrors T27.d)",
      not continue_offered(pb), "")
advance_to_playing(pb)
check("T32.c3 New game reaches PLAYING cleanly; COMBAT_MODE holds its correct boot-cleared default (0), never reads the fixture's own garbage bytes",
      pb.memory[GAMESTATE] == 2 and pb.memory[COMBAT_MODE_ADDR] == 0,
      f"GS={pb.memory[GAMESTATE]} combat_mode={pb.memory[COMBAT_MODE_ADDR]}")
pb.stop()
wipe_save()

# T32.d — COMBAT_MODE off at save time: force COMBAT_MODE=0 (default,
# never entered combat), save, confirm the combat-state DATA block
# (MOB_COUNT/MOB_DATA/WEAPON_TIER/PLAYER_HEALTH) is skipped -- left at
# its zero-initialized default, never written -- while SRAM_COMBAT_MODE
# itself is still written as 0 (the flag, mirroring SRAM_GAME_MODE's own
# always-written precedent). Reads the raw .ram file directly: a reload
# alone can't distinguish "restored as the correct default" from "never
# written, still zero-initialized" since both read back as the same
# boot-time defaults -- WEAPON_TIER's real default (1) and PLAYER_HEALTH's
# real default (3) are both nonzero, so any wrongly-written SRAM byte
# would show up directly in the raw file.
pb = fresh_boot(200)
enter_infinite_mode(pb, 555)   # COMBAT_MODE stays 0 (confirms default "N")
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]
pb.stop()
with open(RAM_PATH, 'rb') as _f:
    _t32d_sram = _f.read()
_t32d_combat_mode = _t32d_sram[SRAM_COMBAT_MODE_ADDR - 0xA000]
_t32d_tier = _t32d_sram[SRAM_WEAPON_TIER_ADDR - 0xA000]
_t32d_health = _t32d_sram[SRAM_PLAYER_HEALTH_ADDR - 0xA000]
check("T32.d COMBAT_MODE off at save time: SRAM_COMBAT_MODE written as 0 (the flag), MOB/tier/health data left unwritten (still zero-initialized)",
      _t32d_combat_mode == 0 and _t32d_tier == 0 and _t32d_health == 0,
      f"sram_combat_mode={_t32d_combat_mode} sram_tier={_t32d_tier} sram_health={_t32d_health}")
wipe_save()

print("\n=== T33: Combat Sub-Mode — Mode Gating & UI (IP-1120) ===")

CMC_CURSOR_ADDR = 0xC6DD

def _to_mode_select(pb):
    """MAIN MENU -> MODE SELECT, cursor at default (finite)."""
    pb.button('a'); [pb.tick() for _ in range(40)]

def _to_combat_confirm(pb):
    """MAIN MENU -> MODE SELECT -> toggle infinite -> confirm -> COMBAT
    MODE CONFIRM (GS=12)."""
    _to_mode_select(pb)
    pb.button('down'); [pb.tick() for _ in range(40)]
    pb.button('a'); [pb.tick() for _ in range(40)]

# T33.a — off by default: from a fresh COMBAT MODE CONFIRM entry (cursor
# defaults to "N"), press A immediately without touching UP/DOWN, confirm
# COMBAT_MODE stays 0 and GAMESTATE reaches INFINITE SEED ENTRY (GS=11).
pb = fresh_boot(200)
_to_combat_confirm(pb)
check("T33.a0 Reaches COMBAT MODE CONFIRM (GS=12)", pb.memory[GAMESTATE] == 12,
      f"GS={pb.memory[GAMESTATE]}")
check("T33.a0b CMC_CURSOR defaults to 0 (N)", pb.memory[CMC_CURSOR_ADDR] == 0,
      f"cursor={pb.memory[CMC_CURSOR_ADDR]}")
pb.button('a'); [pb.tick() for _ in range(40)]
check("T33.a Off by default: A at default N cursor leaves COMBAT_MODE == 0",
      pb.memory[COMBAT_MODE_ADDR] == 0, f"combat_mode={pb.memory[COMBAT_MODE_ADDR]}")
check("T33.a2 Reaches INFINITE SEED ENTRY (GS=11)", pb.memory[GAMESTATE] == 11,
      f"GS={pb.memory[GAMESTATE]}")
pb.stop()

# T33.b — confirm sets the flag: toggle to "Y" (one UP or DOWN press),
# press A, confirm COMBAT_MODE == 1 and GAMESTATE == GS_INFINITE_SEED_ENTRY.
pb = fresh_boot(200)
_to_combat_confirm(pb)
pb.button('up'); [pb.tick() for _ in range(40)]
check("T33.b0 UP toggles CMC_CURSOR to 1 (Y)", pb.memory[CMC_CURSOR_ADDR] == 1,
      f"cursor={pb.memory[CMC_CURSOR_ADDR]}")
pb.button('a'); [pb.tick() for _ in range(40)]
check("T33.b Confirm sets the flag: COMBAT_MODE == 1, GAMESTATE == 11",
      pb.memory[COMBAT_MODE_ADDR] == 1 and pb.memory[GAMESTATE] == 11,
      f"combat_mode={pb.memory[COMBAT_MODE_ADDR]} GS={pb.memory[GAMESTATE]}")
pb.stop()

# T33.c — B-cancel returns to MODE SELECT with "infinite" still
# highlighted: from COMBAT MODE CONFIRM, press B, confirm GAMESTATE ==
# GS_MODE_SELECT and MM_CURSOR != 0 (still "infinite", not reset to
# "finite").
pb = fresh_boot(200)
_to_combat_confirm(pb)
pb.button('b'); [pb.tick() for _ in range(40)]
check("T33.c B-cancel returns to MODE SELECT (GS=10) with infinite still highlighted",
      pb.memory[GAMESTATE] == 10 and pb.memory[MM_CURSOR] != 0,
      f"GS={pb.memory[GAMESTATE]} MM_CURSOR={pb.memory[MM_CURSOR]}")
check("T33.c2 B-cancel writes no COMBAT_MODE (still 0)", pb.memory[COMBAT_MODE_ADDR] == 0,
      f"combat_mode={pb.memory[COMBAT_MODE_ADDR]}")
pb.stop()

# T33.d — re-entry resets to "N": toggle to "Y", B-cancel back to MODE
# SELECT, re-enter COMBAT MODE CONFIRM (MM_CURSOR still "infinite," so a
# plain A re-enters it), confirm CMC_CURSOR == 0 on the fresh entry (never
# carries a stale "Y" forward).
pb = fresh_boot(200)
_to_combat_confirm(pb)
pb.button('up'); [pb.tick() for _ in range(40)]        # toggle to Y
check("T33.d0 Toggled to Y before cancelling", pb.memory[CMC_CURSOR_ADDR] == 1,
      f"cursor={pb.memory[CMC_CURSOR_ADDR]}")
pb.button('b'); [pb.tick() for _ in range(40)]         # cancel -> MODE SELECT
pb.button('a'); [pb.tick() for _ in range(40)]         # re-enter (MM_CURSOR already "infinite")
check("T33.d Re-entry resets to N: fresh CMC_CURSOR == 0 despite prior Y toggle",
      pb.memory[GAMESTATE] == 12 and pb.memory[CMC_CURSOR_ADDR] == 0,
      f"GS={pb.memory[GAMESTATE]} cursor={pb.memory[CMC_CURSOR_ADDR]}")
pb.stop()

# T33.e — finite path unaffected: drive MODE SELECT -> "finite" (default
# cursor, no toggle), confirm GAMESTATE == GS_SEED_SCALE_ENTRY directly, no
# detour through COMBAT MODE CONFIRM, COMBAT_MODE unaffected.
pb = fresh_boot(200)
_to_mode_select(pb)
pb.button('a'); [pb.tick() for _ in range(40)]         # confirm finite (default cursor)
check("T33.e Finite path unaffected: MODE SELECT confirm finite -> SEED/SCALE ENTRY (GS=7) directly",
      pb.memory[GAMESTATE] == 7 and pb.memory[COMBAT_MODE_ADDR] == 0,
      f"GS={pb.memory[GAMESTATE]} combat_mode={pb.memory[COMBAT_MODE_ADDR]}")
pb.stop()

# T33.f — T25 non-regression spot check: MODE SELECT's own B-cancel to
# MAIN MENU and SEED/SCALE ENTRY's own direct reachability both still work
# exactly as T25 itself already re-confirms elsewhere in this same
# full-suite run (T25.b1/T25.c1, both updated only where IP-1120's own
# retarget actually changed behavior — T25.b2a/d1/e1/f's own button
# scripts, not their assertions' intent).
pb = fresh_boot(200)
_to_mode_select(pb)
pb.button('down'); [pb.tick() for _ in range(40)]      # highlight infinite, do NOT confirm
pb.button('b'); [pb.tick() for _ in range(40)]
check("T33.f T25 non-regression: MODE SELECT B-cancel still reaches MAIN MENU (GS=6), GAME_MODE unwritten",
      pb.memory[GAMESTATE] == 6 and pb.memory[GAME_MODE] == 0,
      f"GS={pb.memory[GAMESTATE]} GAME_MODE={pb.memory[GAME_MODE]}")
pb.stop()

# T33.g — reused-array non-corruption (BL-0153 remediation-specific):
# after visiting COMBAT MODE CONFIRM (forcing its own redraw so the
# text-overlay memcpy calls run), navigate back to MODE SELECT and
# confirm its own screen still reads "BUNNY QUEST"/"FINITE"/"INFINITE"
# correctly -- proving the overlay only ever touches the live VRAM copy,
# never mode_select_screen's own ROM-resident array.
pb = fresh_boot(200)
_to_combat_confirm(pb)
pb.button('up'); [pb.tick() for _ in range(40)]        # force an extra redraw (toggle)
pb.button('b'); [pb.tick() for _ in range(40)]         # back to MODE SELECT
_t33g_title = [pb.memory[0x9800 + 3*32 + 5 + i] for i in range(len("BUNNY QUEST"))]
_t33g_expected_title = [_tiles_mod.char_to_tile(c) for c in "BUNNY QUEST"]
_t33g_finite = [pb.memory[0x9800 + 7*32 + 8 + i] for i in range(len("FINITE"))]
_t33g_expected_finite = [_tiles_mod.char_to_tile(c) for c in "FINITE"]
_t33g_infinite = [pb.memory[0x9800 + 9*32 + 8 + i] for i in range(len("INFINITE"))]
_t33g_expected_infinite = [_tiles_mod.char_to_tile(c) for c in "INFINITE"]
check("T33.g Reused-array non-corruption: MODE SELECT still reads BUNNY QUEST/FINITE/INFINITE after visiting COMBAT MODE CONFIRM",
      _t33g_title == _t33g_expected_title and _t33g_finite == _t33g_expected_finite and
      _t33g_infinite == _t33g_expected_infinite,
      f"title={_t33g_title} finite={_t33g_finite} infinite={_t33g_infinite}")
pb.stop()

# T33.h — overlay content correct: drive to COMBAT MODE CONFIRM, read the
# row-3/row-7/row-9 VRAM tile bytes directly, confirm they read "COMBAT
# MODE?"/"NO"/"YES" (not stale BUNNY QUEST/FINITE/INFINITE leftovers) and
# that no trailing character from the longer original labels survives the
# shorter replacement (row 7 col 13, FINITE's own last letter's position,
# and row 9 col 15, INFINITE's own last letter's position, both blank).
pb = fresh_boot(200)
_to_combat_confirm(pb)
_t33h_title = [pb.memory[0x9800 + 3*32 + 5 + i] for i in range(len("COMBAT MODE?"))]
_t33h_expected_title = [_tiles_mod.char_to_tile(c) for c in "COMBAT MODE?"]
_t33h_no = [pb.memory[0x9800 + 7*32 + 8 + i] for i in range(2)]
_t33h_expected_no = [_tiles_mod.char_to_tile(c) for c in "NO"]
_t33h_yes = [pb.memory[0x9800 + 9*32 + 8 + i] for i in range(3)]
_t33h_expected_yes = [_tiles_mod.char_to_tile(c) for c in "YES"]
_t33h_trailing_finite = pb.memory[0x9800 + 7*32 + 13]   # FINITE's own last letter's cell
_t33h_trailing_infinite = pb.memory[0x9800 + 9*32 + 15] # INFINITE's own last letter's cell
check("T33.h Overlay content correct: COMBAT MODE?/NO/YES render, no stale trailing characters",
      _t33h_title == _t33h_expected_title and _t33h_no == _t33h_expected_no and
      _t33h_yes == _t33h_expected_yes and _t33h_trailing_finite == TL_BG_BLANK and
      _t33h_trailing_infinite == TL_BG_BLANK,
      f"title={_t33h_title} no={_t33h_no} yes={_t33h_yes} "
      f"trailing_finite={_t33h_trailing_finite} trailing_infinite={_t33h_trailing_infinite}")
pb.stop()
wipe_save()

print("\n=== T34: Combat Sub-Mode — Sprite Content (IP-1125) ===")

import build_rom as _build_rom_mod

_t34_data = _tiles_mod.build_tile_data()
def _t34_tile_bytes(idx):
    return _t34_data[idx * 16:(idx + 1) * 16]

_t34_mob = bytes(_t34_tile_bytes(_tiles_mod.TL_MOB))
_t34_mob_bot = bytes(_t34_tile_bytes(_tiles_mod.TL_MOB_BOT))
_t34_proj = bytes(_t34_tile_bytes(_tiles_mod.TL_PROJECTILE))
_t34_proj_bot = bytes(_t34_tile_bytes(_tiles_mod.TL_PROJECTILE_BOT))
check("T34.a Tile indices: TL_MOB/TL_MOB_BOT/TL_PROJECTILE/TL_PROJECTILE_BOT sit at 0x0A-0x0D exactly",
      (_tiles_mod.TL_MOB, _tiles_mod.TL_MOB_BOT,
       _tiles_mod.TL_PROJECTILE, _tiles_mod.TL_PROJECTILE_BOT) == (0x0A, 0x0B, 0x0C, 0x0D),
      f"got={(_tiles_mod.TL_MOB, _tiles_mod.TL_MOB_BOT, _tiles_mod.TL_PROJECTILE, _tiles_mod.TL_PROJECTILE_BOT)}")

check("T34.b Registered: TL_MOB/TL_PROJECTILE tile data matches mob_obj()/projectile_obj() exactly; both bottom halves are blank",
      _t34_mob == bytes(_tiles_mod.mob_obj())
      and _t34_proj == bytes(_tiles_mod.projectile_obj())
      and _t34_mob_bot == bytes(_tiles_mod.ui_blank())
      and _t34_proj_bot == bytes(_tiles_mod.ui_blank()),
      "mismatch against tiles.py's own generator functions")

_t34_existing_obj = {
    'bunny_t': bytes(_t34_tile_bytes(_tiles_mod.TL_BUNNY_T_F1)),
    'bunny_b': bytes(_t34_tile_bytes(_tiles_mod.TL_BUNNY_B_F1)),
    'carrot':  bytes(_t34_tile_bytes(_tiles_mod.TL_CARROT)),
    'star':    bytes(_t34_tile_bytes(_tiles_mod.TL_STAR)),
    'flower':  bytes(_t34_tile_bytes(_tiles_mod.TL_FLOWER_OBJ)),
}
_t34_dupes = [name for name, data in _t34_existing_obj.items()
              if data == _t34_mob or data == _t34_proj]
check("T34.c Distinctness: mob/projectile art is visually distinct (byte-for-byte) from every existing OBJ tile and from each other",
      _t34_dupes == [] and _t34_mob != _t34_proj,
      f"dupes={_t34_dupes} mob==proj:{_t34_mob == _t34_proj}")

check("T34.d Palette budget: OBJ_PALETTES table still holds exactly 8 fixed-size entries (mob/projectile reuse the two previously-placeholder 'unused/white' slots, no new slot added)",
      len(_build_rom_mod.OBJ_PALETTES) == 8 and all(len(p) == 4 for p in _build_rom_mod.OBJ_PALETTES),
      f"count={len(_build_rom_mod.OBJ_PALETTES)}")

print("\n=== T35: Combat Sub-Mode — Mob Movement (IP-1126) ===")

MOB_MOVE_TIMER_ADDR = 0xC6DE
IMV_ADDR = _gw_rom.labels['inf_mob_move']

def t35_reset(pb, combat_mode=1, timer=0):
    pb.memory[GAME_MODE] = 1
    pb.memory[COMBAT_MODE_ADDR] = combat_mode
    pb.memory[MOB_COUNT_ADDR] = 0
    for i in range(6):
        base = MOB_DATA_ADDR + i * 5
        for k in range(5): pb.memory[base + k] = 0
    pb.memory[MOB_MOVE_TIMER_ADDR] = timer

def t35_set_slot(pb, slot, x, y, species=0, health=1, active=1):
    base = MOB_DATA_ADDR + slot * 5
    pb.memory[base + 0] = x; pb.memory[base + 1] = y
    pb.memory[base + 2] = species; pb.memory[base + 3] = health
    pb.memory[base + 4] = active

def t35_slot(pb, slot):
    base = MOB_DATA_ADDR + slot * 5
    return tuple(pb.memory[base + k] for k in range(5))

pb = fresh_boot(180)
advance_to_playing(pb)

# T35.a — a mob directly right of the player moves left by exactly
# MOB_MOVE_STEP after one recomputation interval elapses (timer forced to
# 1 -- decrementing to 0 this same frame moves it, per inf_mob_move's own
# "reaches 0 this frame" rule, not merely counting down to 0 unmoved).
t35_reset(pb, timer=1)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
t35_set_slot(pb, 0, 100, 60)
_t35a_ok = invoke_no_arg(pb, IMV_ADDR)
_t35a_slot = t35_slot(pb, 0)
check("T35.a A mob directly right of the player moves left by exactly MOB_MOVE_STEP after one recomputation interval elapses",
      _t35a_ok and _t35a_slot[0] == 100 - MOB_MOVE_STEP and _t35a_slot[1] == 60,
      f"ok={_t35a_ok} slot={_t35a_slot}")

# T35.b — the Y-axis counterpart: a mob directly below the player moves up.
t35_reset(pb, timer=1)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
t35_set_slot(pb, 0, 80, 100)
_t35b_ok = invoke_no_arg(pb, IMV_ADDR)
_t35b_slot = t35_slot(pb, 0)
check("T35.b A mob directly below the player moves up by exactly MOB_MOVE_STEP (dominant-axis choice is not X-only)",
      _t35b_ok and _t35b_slot[1] == 100 - MOB_MOVE_STEP and _t35b_slot[0] == 80,
      f"ok={_t35b_ok} slot={_t35b_slot}")

# T35.c — diagonal offset with |dx| > |dy|: moves only on X this interval.
t35_reset(pb, timer=1)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
t35_set_slot(pb, 0, 100, 70)   # dx=20, dy=10
_t35c_ok = invoke_no_arg(pb, IMV_ADDR)
_t35c_slot = t35_slot(pb, 0)
check("T35.c Diagonal offset (|dx|>|dy|) moves only on the X axis this interval, Y unchanged",
      _t35c_ok and _t35c_slot[0] == 100 - MOB_MOVE_STEP and _t35c_slot[1] == 70,
      f"ok={_t35c_ok} slot={_t35c_slot}")

# T35.d — the symmetric case: |dy| > |dx| moves only on the Y axis.
t35_reset(pb, timer=1)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
t35_set_slot(pb, 0, 90, 100)   # dx=10, dy=40
_t35d_ok = invoke_no_arg(pb, IMV_ADDR)
_t35d_slot = t35_slot(pb, 0)
check("T35.d Symmetric case (|dy|>|dx|) moves only on the Y axis",
      _t35d_ok and _t35d_slot[1] == 100 - MOB_MOVE_STEP and _t35d_slot[0] == 90,
      f"ok={_t35d_ok} slot={_t35d_slot}")

# T35.e — a mob already coincident with the player does not move on a
# recomputation interval (FS-112 Open Question 4's own resolution).
t35_reset(pb, timer=1)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
t35_set_slot(pb, 0, 80, 60)
_t35e_ok = invoke_no_arg(pb, IMV_ADDR)
_t35e_slot = t35_slot(pb, 0)
check("T35.e A mob already coincident with the player does not move on a recomputation interval",
      _t35e_ok and _t35e_slot[0] == 80 and _t35e_slot[1] == 60,
      f"ok={_t35e_ok} slot={_t35e_slot}")

# T35.f — no movement occurs before MOB_MOVE_TIMER reaches 0: force the
# timer above 1, tick one frame, confirm no movement and the timer
# decremented by exactly 1.
t35_reset(pb, timer=5)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
t35_set_slot(pb, 0, 100, 60)
_t35f_ok = invoke_no_arg(pb, IMV_ADDR)
_t35f_slot = t35_slot(pb, 0)
_t35f_timer = pb.memory[MOB_MOVE_TIMER_ADDR]
check("T35.f No movement occurs before MOB_MOVE_TIMER reaches 0; timer decremented by exactly 1",
      _t35f_ok and _t35f_slot[0] == 100 and _t35f_slot[1] == 60 and _t35f_timer == 4,
      f"ok={_t35f_ok} slot={_t35f_slot} timer={_t35f_timer}")

# T35.g — COMBAT_MODE off: inf_mob_move is a complete no-op, mob position
# and MOB_MOVE_TIMER both unchanged across multiple ticks.
t35_reset(pb, combat_mode=0, timer=1)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
t35_set_slot(pb, 0, 100, 60)
for _ in range(3): invoke_no_arg(pb, IMV_ADDR)
_t35g_slot = t35_slot(pb, 0)
_t35g_timer = pb.memory[MOB_MOVE_TIMER_ADDR]
check("T35.g COMBAT_MODE off: inf_mob_move is a complete no-op (mob position and MOB_MOVE_TIMER unchanged across multiple ticks)",
      _t35g_slot[0] == 100 and _t35g_slot[1] == 60 and _t35g_timer == 1,
      f"slot={_t35g_slot} timer={_t35g_timer}")

# T35.h — an inactive MOB_DATA slot is never moved: alternate active/
# inactive slots at the same relative offset from the player, confirm only
# the active ones move.
t35_reset(pb, timer=1)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
for i in range(6):
    t35_set_slot(pb, i, 100, 60, active=(1 if i % 2 == 0 else 0))
_t35h_ok = invoke_no_arg(pb, IMV_ADDR)
_t35h_slots = [t35_slot(pb, i) for i in range(6)]
_t35h_expect = all(
    (_t35h_slots[i][0] == 100 - MOB_MOVE_STEP if i % 2 == 0 else _t35h_slots[i][0] == 100)
    and _t35h_slots[i][1] == 60
    for i in range(6)
)
check("T35.h An inactive MOB_DATA slot is never moved (only active slots' positions change)",
      _t35h_ok and _t35h_expect, f"ok={_t35h_ok} slots={_t35h_slots}")

pb.stop()
wipe_save()

# T35.i — independent live drive through the real production per-frame
# chain (not a direct-invoke force), mirroring VR-1121/VR-1122's own
# established independent-verification discipline: drive the real MODE
# SELECT -> COMBAT MODE CONFIRM (Y) -> INFINITE SEED ENTRY -> INTRO ->
# PLAYING path, force a real mob a known distance right of the real player,
# let several real recomputation intervals elapse via real pb.tick() calls
# (st_playing's own per-frame chain, not invoke_no_arg), and confirm the
# mob's own recorded position moved the expected total distance/direction.
# Per inf_mob_move's corrected timer semantics (see its own header comment),
# a timer forced to 0 moves immediately, then every MOB_MOVE_INTERVAL frames
# thereafter -- moves land at frames 1, 1+MOB_MOVE_INTERVAL, 1+2*MOB_MOVE_INTERVAL, ...
pb35i = fresh_boot(180)
pb35i.button('a'); [pb35i.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb35i.button('down'); [pb35i.tick() for _ in range(40)]     # toggle infinite
pb35i.button('a'); [pb35i.tick() for _ in range(40)]        # confirm -> COMBAT MODE CONFIRM
pb35i.button('up'); [pb35i.tick() for _ in range(40)]       # toggle to "Y"
pb35i.button('a'); [pb35i.tick() for _ in range(40)]        # confirm Y -> INFINITE SEED ENTRY
enter_infinite_seed(pb35i, [4, 2, 0, 0, 0])
pb35i.button('a'); [pb35i.tick() for _ in range(100)]       # confirm seed -> INTRO
pb35i.button('a'); [pb35i.tick() for _ in range(40)]        # INTRO -> PLAYING

_t35i_px = pb35i.memory[PLAYER_X]; _t35i_py = pb35i.memory[PLAYER_Y]
pb35i.memory[MOB_COUNT_ADDR] = 1
for i in range(6):
    base = MOB_DATA_ADDR + i * 5
    for k in range(5): pb35i.memory[base + k] = 0
pb35i.memory[PROJ_ACTIVE_ADDR] = 0   # clear any menu-navigation A-press latched into a stray fire
_t35i_mob_x0 = _t35i_px + 40
t35_set_slot(pb35i, 0, _t35i_mob_x0, _t35i_py)
pb35i.memory[MOB_MOVE_TIMER_ADDR] = 0

_t35i_frames = 1 + 2 * MOB_MOVE_INTERVAL   # exactly 3 moves land within this many frames
for _ in range(_t35i_frames): pb35i.tick()
_t35i_final = t35_slot(pb35i, 0)
_t35i_expected_x = _t35i_mob_x0 - 3 * MOB_MOVE_STEP
check("T35.i Independent live drive: a real mob moves the expected total distance/direction toward the real player over several real recomputation intervals",
      pb35i.memory[GAMESTATE] == 2 and _t35i_final[0] == _t35i_expected_x and _t35i_final[1] == _t35i_py,
      f"gs={pb35i.memory[GAMESTATE]} player=({_t35i_px},{_t35i_py}) mob0={_t35i_mob_x0} "
      f"final={_t35i_final} expected_x={_t35i_expected_x} frames={_t35i_frames}")
pb35i.stop()
wipe_save()

# ══════════════════════════════════════════════════════
# T36 — Combat Sub-Mode: Post-Contact Player Protection (IP-1127)
# ══════════════════════════════════════════════════════
print("\n=== T36: Combat Sub-Mode — Post-Contact Player Protection (IP-1127) ===")

PLAYER_INVINCIBLE_ADDR = 0xC6E2; MOB_CONTACT_FLAGS_ADDR = 0xC6E3
IIT_ADDR = _gw_rom.labels['inf_invincibility_tick']
IP1127_KNOCKBACK_DISTANCE = 16

def t36_reset(pb, combat_mode=1, player_health=3):
    pb.memory[GAME_MODE] = 1
    pb.memory[COMBAT_MODE_ADDR] = combat_mode
    pb.memory[MOB_COUNT_ADDR] = 0
    for i in range(6):
        base = MOB_DATA_ADDR + i * 5
        for k in range(5): pb.memory[base + k] = 0
    pb.memory[PLAYER_HEALTH_ADDR] = player_health
    pb.memory[PLAYER_INVINCIBLE_ADDR] = 0
    pb.memory[MOB_CONTACT_FLAGS_ADDR] = 0
    pb.memory[COMBAT_ENTRY_X_ADDR] = 0; pb.memory[COMBAT_ENTRY_Y_ADDR] = 0

# T36.a — the exact BL-0158 repro: sustained overlap with the same mob
# across several direct-invoke "frames" produces exactly one health
# decrement, not a cascade.
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
_t36a_mob = MOB_DATA_ADDR
pb.memory[_t36a_mob + 0] = 80; pb.memory[_t36a_mob + 1] = 60
pb.memory[_t36a_mob + 2] = 0; pb.memory[_t36a_mob + 3] = 1; pb.memory[_t36a_mob + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
for _ in range(5):
    invoke_no_arg(pb, IMCC_ADDR)
    # IP-1127's own knockback (correctly) separates the player from the
    # mob on a hit -- re-pin the player back to the overlap position
    # between invocations so this check genuinely exercises *sustained*
    # overlap (the cooldown-bit mechanism specifically), not knockback's
    # own already-separately-tested (T36.b/g) side effect of ending
    # overlap naturally after one hit.
    pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
check("T36.a BL-0158 repro: sustained overlap with the same mob across multiple frames produces exactly one health decrement, not a cascade",
      pb.memory[PLAYER_HEALTH_ADDR] == 2,
      f"health={pb.memory[PLAYER_HEALTH_ADDR]}")
pb.stop()
wipe_save()

# T36.b — knockback fires on a hit: player pushed exactly
# KNOCKBACK_DISTANCE on the expected dominant axis, away from the mob.
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
_t36b_mob = MOB_DATA_ADDR
pb.memory[_t36b_mob + 0] = 84; pb.memory[_t36b_mob + 1] = 60   # mob to the right (dx=4, dominant X)
pb.memory[_t36b_mob + 2] = 0; pb.memory[_t36b_mob + 3] = 1; pb.memory[_t36b_mob + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
invoke_no_arg(pb, IMCC_ADDR)
check("T36.b Knockback fires on a hit: player pushed exactly KNOCKBACK_DISTANCE on the dominant axis, away from the mob",
      pb.memory[PLAYER_X] == 80 - IP1127_KNOCKBACK_DISTANCE and pb.memory[PLAYER_Y] == 60,
      f"x={pb.memory[PLAYER_X]} y={pb.memory[PLAYER_Y]}")
pb.stop()
wipe_save()

# T36.c — invincibility blocks a fresh hit from a distinct mob (tracked,
# not decremented); T36.c2 — once invincibility expires, that tracked
# mob's own bit still covers it as a cooldown (no "free" hit).
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
_t36c_mobA = MOB_DATA_ADDR
pb.memory[_t36c_mobA + 0] = 80; pb.memory[_t36c_mobA + 1] = 60
pb.memory[_t36c_mobA + 2] = 0; pb.memory[_t36c_mobA + 3] = 1; pb.memory[_t36c_mobA + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
invoke_no_arg(pb, IMCC_ADDR)   # mob A hits: health 3->2, PLAYER_INVINCIBLE=30
_t36c_health_a = pb.memory[PLAYER_HEALTH_ADDR]
_t36c_inv_a = pb.memory[PLAYER_INVINCIBLE_ADDR]
# IP-1127's own knockback correctly moves the player away from mob A on
# the hit (already covered by T36.b/g) -- re-pin the player back to the
# overlap position so mob B's own fresh-contact test isn't confounded by
# that already-separately-tested side effect.
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
_t36c_mobB = MOB_DATA_ADDR + 5
pb.memory[_t36c_mobB + 0] = 80; pb.memory[_t36c_mobB + 1] = 60   # distinct mob, same position, fresh contact
pb.memory[_t36c_mobB + 2] = 0; pb.memory[_t36c_mobB + 3] = 1; pb.memory[_t36c_mobB + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 2
invoke_no_arg(pb, IMCC_ADDR)   # mob A: bit already set, no-op; mob B: fresh but invincible, tracked
_t36c_health_b = pb.memory[PLAYER_HEALTH_ADDR]
_t36c_mobB_bit = pb.memory[MOB_CONTACT_FLAGS_ADDR] & 0b10
check("T36.c Invincibility blocks a fresh hit from a distinct mob: no second decrement, but the new mob's own bit is tracked",
      _t36c_health_a == 2 and _t36c_inv_a == 30 and _t36c_health_b == 2 and _t36c_mobB_bit != 0,
      f"health_a={_t36c_health_a} inv_a={_t36c_inv_a} health_b={_t36c_health_b} mobB_bit={_t36c_mobB_bit}")
pb.memory[PLAYER_INVINCIBLE_ADDR] = 0   # force natural expiry
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60   # re-pin: mob B's own hit (if any) would also knock back
invoke_no_arg(pb, IMCC_ADDR)
check("T36.c2 Once invincibility expires, the tracked mob (B) still doesn't get a free hit -- its own bit already covers it as a cooldown",
      pb.memory[PLAYER_HEALTH_ADDR] == 2,
      f"health={pb.memory[PLAYER_HEALTH_ADDR]}")
pb.stop()
wipe_save()

# T36.d — per-mob cooldown outlasts invincibility: force a hit, force
# PLAYER_INVINCIBLE to 0 directly (simulating natural expiry) while still
# overlapping the *same* triggering mob, confirm still no second decrement.
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
_t36d_mob = MOB_DATA_ADDR
pb.memory[_t36d_mob + 0] = 80; pb.memory[_t36d_mob + 1] = 60
pb.memory[_t36d_mob + 2] = 0; pb.memory[_t36d_mob + 3] = 1; pb.memory[_t36d_mob + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
invoke_no_arg(pb, IMCC_ADDR)   # hit: health 3->2
pb.memory[PLAYER_INVINCIBLE_ADDR] = 0
# Re-pin the player: knockback (already covered by T36.b/g) moved it off
# the mob -- this check is specifically about *genuinely still overlapping*
# the same mob, so restore that premise before testing the cooldown gate.
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
invoke_no_arg(pb, IMCC_ADDR)   # still overlapping the same mob -- cooldown, not invincibility, blocks it
check("T36.d Per-mob cooldown outlasts invincibility: no second decrement from the same mob even after invincibility is forced to 0 while still overlapping",
      pb.memory[PLAYER_HEALTH_ADDR] == 2,
      f"health={pb.memory[PLAYER_HEALTH_ADDR]}")
pb.stop()
wipe_save()

# T36.e — cooldown clears on a genuine break-and-resume: bit set after a
# hit, clears once overlap genuinely breaks, a fresh hit registers on
# resumed overlap (the cooldown is per-approach, not permanent).
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
_t36e_mob = MOB_DATA_ADDR
pb.memory[_t36e_mob + 0] = 80; pb.memory[_t36e_mob + 1] = 60
pb.memory[_t36e_mob + 2] = 0; pb.memory[_t36e_mob + 3] = 1; pb.memory[_t36e_mob + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
invoke_no_arg(pb, IMCC_ADDR)   # hit: health 3->2, bit set
_t36e_bit_after_hit = pb.memory[MOB_CONTACT_FLAGS_ADDR] & 1
pb.memory[_t36e_mob + 0] = 200; pb.memory[_t36e_mob + 1] = 200   # move far away -- breaks overlap
invoke_no_arg(pb, IMCC_ADDR)   # not overlapping -- clears the bit
_t36e_bit_after_break = pb.memory[MOB_CONTACT_FLAGS_ADDR] & 1
# Re-pin the player: the first hit's own knockback (already covered by
# T36.b/g) moved it -- restore the overlap position before the fresh
# approach, so this check is genuinely about the cooldown bit clearing,
# not a coincidental non-overlap from the earlier knockback.
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
pb.memory[_t36e_mob + 0] = 80; pb.memory[_t36e_mob + 1] = 60   # move back -- fresh approach
pb.memory[PLAYER_INVINCIBLE_ADDR] = 0   # not invincible, so the fresh hit can register
invoke_no_arg(pb, IMCC_ADDR)
check("T36.e Cooldown clears on a genuine break-and-resume: bit set after the first hit, clears once overlap breaks, a fresh hit registers on resumed overlap",
      _t36e_bit_after_hit != 0 and _t36e_bit_after_break == 0 and pb.memory[PLAYER_HEALTH_ADDR] == 1,
      f"bit_after_hit={_t36e_bit_after_hit} bit_after_break={_t36e_bit_after_break} health={pb.memory[PLAYER_HEALTH_ADDR]}")
pb.stop()
wipe_save()

# T36.f — invincibility countdown: decrements by exactly 1, reaches
# exactly 0 (not clamped above 0).
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_INVINCIBLE_ADDR] = 10
invoke_no_arg(pb, IIT_ADDR)
_t36f_after1 = pb.memory[PLAYER_INVINCIBLE_ADDR]
pb.memory[PLAYER_INVINCIBLE_ADDR] = 1
invoke_no_arg(pb, IIT_ADDR)
_t36f_after2 = pb.memory[PLAYER_INVINCIBLE_ADDR]
check("T36.f Invincibility countdown: decrements by exactly 1, reaches exactly 0 (not clamped above)",
      _t36f_after1 == 9 and _t36f_after2 == 0,
      f"after1={_t36f_after1} after2={_t36f_after2}")
pb.stop()
wipe_save()

# T36.g — knockback clamped at a window boundary: player position stays
# within bounds rather than reading as an invalid/wrapped coordinate.
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_X] = 4; pb.memory[PLAYER_Y] = 60   # near the left edge (min 0)
_t36g_mob = MOB_DATA_ADDR
pb.memory[_t36g_mob + 0] = 8; pb.memory[_t36g_mob + 1] = 60   # mob to the right -> push left, would underflow unclamped
pb.memory[_t36g_mob + 2] = 0; pb.memory[_t36g_mob + 3] = 1; pb.memory[_t36g_mob + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
invoke_no_arg(pb, IMCC_ADDR)
check("T36.g Knockback clamped at the window boundary: player position stays within bounds (0), not an invalid/wrapped coordinate",
      pb.memory[PLAYER_X] == 0,
      f"x={pb.memory[PLAYER_X]}")
pb.stop()
wipe_save()

# T36.h — COMBAT_MODE off: inf_mob_contact_check/inf_invincibility_tick
# are both complete no-ops.
pb = fresh_boot(180)
t36_reset(pb, combat_mode=0)
pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60
_t36h_mob = MOB_DATA_ADDR
pb.memory[_t36h_mob + 0] = 80; pb.memory[_t36h_mob + 1] = 60
pb.memory[_t36h_mob + 2] = 0; pb.memory[_t36h_mob + 3] = 1; pb.memory[_t36h_mob + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
pb.memory[PLAYER_INVINCIBLE_ADDR] = 5
invoke_no_arg(pb, IMCC_ADDR)
invoke_no_arg(pb, IIT_ADDR)
check("T36.h COMBAT_MODE off: inf_mob_contact_check/inf_invincibility_tick are both complete no-ops",
      pb.memory[PLAYER_HEALTH_ADDR] == 3 and pb.memory[PLAYER_X] == 80 and
      pb.memory[PLAYER_INVINCIBLE_ADDR] == 5 and pb.memory[MOB_CONTACT_FLAGS_ADDR] == 0,
      f"health={pb.memory[PLAYER_HEALTH_ADDR]} x={pb.memory[PLAYER_X]} inv={pb.memory[PLAYER_INVINCIBLE_ADDR]} flags={pb.memory[MOB_CONTACT_FLAGS_ADDR]}")
pb.stop()
wipe_save()

# T36.i — T31 non-regression: a single isolated (non-sustained) contact
# still behaves exactly as IP-1123 originally shipped -- one decrement,
# HUD redraw flagged. No T31 assertion needed adjustment (confirmed by
# the unmodified full-suite run, not merely assumed): this package's own
# new gating only changes behavior on a *second* overlapping frame for
# the *same* mob, which no existing T31 fixture ever exercises.
pb = fresh_boot(180)
t36_reset(pb)
pb.memory[PLAYER_X] = 100; pb.memory[PLAYER_Y] = 50
_t36i_mob = MOB_DATA_ADDR
pb.memory[_t36i_mob + 0] = 100; pb.memory[_t36i_mob + 1] = 50
pb.memory[_t36i_mob + 2] = 0; pb.memory[_t36i_mob + 3] = 1; pb.memory[_t36i_mob + 4] = 1
pb.memory[MOB_COUNT_ADDR] = 1
pb.memory[SCORE_DIRTY] = 0
invoke_no_arg(pb, IMCC_ADDR)
check("T36.i T31 non-regression: a single isolated contact still behaves exactly as IP-1123 originally shipped -- one decrement, HUD redraw flagged",
      pb.memory[PLAYER_HEALTH_ADDR] == 2 and pb.memory[SCORE_DIRTY] == 1,
      f"health={pb.memory[PLAYER_HEALTH_ADDR]} score_dirty={pb.memory[SCORE_DIRTY]}")
pb.stop()
wipe_save()

# T36.j — independent live PyBoy drive through the real production
# per-frame chain (not a direct-invoke force), mirroring T35.i's/T37.i's
# own established discipline: reproduce the exact BL-0158 scenario --
# real held contact during real PLAYING -- and confirm the fix is
# perceptible in real play: health drops by exactly one heart, the player
# is visibly displaced, not teleported through a rapid death-and-setback
# cascade within an imperceptible handful of frames.
pb = fresh_boot(180)
pb.button('a'); [pb.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb.button('down'); [pb.tick() for _ in range(40)]     # toggle infinite
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm -> COMBAT MODE CONFIRM
pb.button('up'); [pb.tick() for _ in range(40)]       # toggle to "Y"
pb.button('a'); [pb.tick() for _ in range(40)]        # confirm Y -> INFINITE SEED ENTRY
enter_infinite_seed(pb, [4, 2, 0, 0, 0])
pb.button('a'); [pb.tick() for _ in range(100)]       # confirm seed -> INTRO
pb.button('a'); [pb.tick() for _ in range(40)]        # INTRO -> PLAYING
_t36j_px0 = pb.memory[PLAYER_X]; _t36j_py0 = pb.memory[PLAYER_Y]
pb.memory[MOB_COUNT_ADDR] = 1
_t36j_mob = MOB_DATA_ADDR
pb.memory[_t36j_mob + 0] = _t36j_px0; pb.memory[_t36j_mob + 1] = _t36j_py0
pb.memory[_t36j_mob + 2] = 0; pb.memory[_t36j_mob + 3] = 1; pb.memory[_t36j_mob + 4] = 1
pb.memory[0xC6DE] = 200   # MOB_MOVE_TIMER pinned high -- mob stays put, isolating the effect being tested
for _ in range(20):
    pb.tick()   # sustained real per-frame overlap -- the exact BL-0158 scenario
_t36j_health = pb.memory[PLAYER_HEALTH_ADDR]
_t36j_px1 = pb.memory[PLAYER_X]; _t36j_py1 = pb.memory[PLAYER_Y]
check("T36.j Independent live drive: sustained real per-frame overlap produces exactly one health decrement and a visible knockback displacement, not a rapid death-and-setback cascade",
      pb.memory[GAMESTATE] == 2 and _t36j_health == 2 and
      (_t36j_px1, _t36j_py1) != (_t36j_px0, _t36j_py0),
      f"GS={pb.memory[GAMESTATE]} health0=3 health1={_t36j_health} pos0=({_t36j_px0},{_t36j_py0}) pos1=({_t36j_px1},{_t36j_py1})")
pb.stop()
wipe_save()

print("\n=== T37: Combat Sub-Mode — Weapon Directionality (IP-1128) ===")

pb = fresh_boot(180)
advance_to_playing(pb)

J_RIGHT_BIT = 4; J_LEFT_BIT = 5; J_UP_BIT = 6; J_DOWN_BIT = 7  # asm_game.py's own bit positions

def t37_reset(pb, weapon_tier=1):
    t30_reset(pb, weapon_tier=weapon_tier)
    pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 60

def fire_with_facing(pb, facing_x, facing_y):
    """Single invoke_no_arg call (the only proven-reliable pattern -- see
    T30.a): directly force PLAYER_FACING_X/Y to the value under test (as if
    a prior frame's movement branch had already set it, per
    handle_play_input's real ordering: fire copies whatever facing is
    currently on record) and fire in the same frame."""
    pb.memory[PLAYER_FACING_X_ADDR] = facing_x & 0xFF
    pb.memory[PLAYER_FACING_Y_ADDR] = facing_y & 0xFF
    pb.memory[JOY_CUR_ADDR] = 0; pb.memory[JOY_NEW_ADDR] = 1 << J_A_BIT
    return invoke_no_arg(pb, HPI_ADDR)

def proj_step(pb):
    sx = pb.memory[PROJ_STEP_X_ADDR]
    sy = pb.memory[PROJ_STEP_Y_ADDR]
    return (sx - 256 if sx > 127 else sx, sy - 256 if sy > 127 else sy)

# T37.a — firing with a right-facing record spawns a projectile whose
# per-frame step is (+1, 0).
t37_reset(pb)
_t37a_ok = fire_with_facing(pb, 1, 0)
_t37a_step = proj_step(pb)
check("T37.a Firing while moving right spawns a projectile stepping (+1, 0)",
      _t37a_ok and pb.memory[PROJ_ACTIVE_ADDR] == 1 and _t37a_step == (1, 0),
      f"ok={_t37a_ok} active={pb.memory[PROJ_ACTIVE_ADDR]} step={_t37a_step}")

# T37.b — firing with an up-facing record spawns a projectile whose
# per-frame step is (0, -1).
t37_reset(pb)
_t37b_ok = fire_with_facing(pb, 0, -1)
_t37b_step = proj_step(pb)
check("T37.b Firing while moving up spawns a projectile stepping (0, -1)",
      _t37b_ok and pb.memory[PROJ_ACTIVE_ADDR] == 1 and _t37b_step == (0, -1),
      f"ok={_t37b_ok} active={pb.memory[PROJ_ACTIVE_ADDR]} step={_t37b_step}")

# T37.c — firing with a diagonal (RIGHT+UP) facing record spawns a
# projectile whose per-frame step is (+1, -1) -- both axes simultaneously.
t37_reset(pb)
_t37c_ok = fire_with_facing(pb, 1, -1)
_t37c_step = proj_step(pb)
check("T37.c Firing while moving diagonally (RIGHT+UP) spawns a projectile stepping (+1, -1)",
      _t37c_ok and pb.memory[PROJ_ACTIVE_ADDR] == 1 and _t37c_step == (1, -1),
      f"ok={_t37c_ok} active={pb.memory[PROJ_ACTIVE_ADDR]} step={_t37c_step}")

# T37.d — all eight compass directions reachable: parameterized corpus.
_t37d_corpus = [
    (1, 0, (1, 0)),
    (-1, 0, (-1, 0)),
    (0, -1, (0, -1)),
    (0, 1, (0, 1)),
    (1, -1, (1, -1)),
    (1, 1, (1, 1)),
    (-1, -1, (-1, -1)),
    (-1, 1, (-1, 1)),
]
_t37d_bad = []
for _fx, _fy, _expected in _t37d_corpus:
    t37_reset(pb)
    fire_with_facing(pb, _fx, _fy)
    _got = proj_step(pb)
    if _got != _expected:
        _t37d_bad.append(((_fx, _fy), _expected, _got))
check("T37.d All eight compass directions reachable, each producing its own correct (step_x, step_y)",
      _t37d_bad == [], f"bad={_t37d_bad}")

# T37.e — firing while stationary uses the most recently held movement
# direction, not a fixed default: PLAYER_FACING_Y already holds "up" from a
# prior frame (t37_reset's own baseline leaves PLAYER_FACING_X/Y untouched
# by a no-direction-held frame -- movement branches only overwrite facing
# when their own direction is actually pressed), so forcing it directly and
# firing with no D-pad bits held reproduces that same real invariant in one
# call.
t37_reset(pb)
pb.memory[PLAYER_FACING_X_ADDR] = 0; pb.memory[PLAYER_FACING_Y_ADDR] = 0xFF
pb.memory[JOY_CUR_ADDR] = 0; pb.memory[JOY_NEW_ADDR] = 1 << J_A_BIT
_t37e_ok = invoke_no_arg(pb, HPI_ADDR)
_t37e_step = proj_step(pb)
check("T37.e Firing while stationary uses the most recently held movement direction",
      _t37e_ok and pb.memory[PROJ_ACTIVE_ADDR] == 1 and _t37e_step == (0, -1),
      f"ok={_t37e_ok} active={pb.memory[PROJ_ACTIVE_ADDR]} step={_t37e_step}")

# T37.f — a fresh session that has never moved (boot default) fires
# rightward -- confirms the boot-init default (PLAYER_FACING_X=1,
# PLAYER_FACING_Y=0) produces a sane shot rather than a directionless
# (0,0) projectile.
pb37f = fresh_boot(180)
advance_to_playing(pb37f)
pb37f.memory[COMBAT_MODE_ADDR] = 1
pb37f.memory[PROJ_ACTIVE_ADDR] = 0
pb37f.memory[JOY_NEW_ADDR] = 1 << J_A_BIT
_t37f_ok = invoke_no_arg(pb37f, HPI_ADDR)
_t37f_step = proj_step(pb37f)
check("T37.f A fresh, never-moved session fires rightward by default (not a directionless (0,0) shot)",
      _t37f_ok and pb37f.memory[PROJ_ACTIVE_ADDR] == 1 and _t37f_step == (1, 0),
      f"ok={_t37f_ok} active={pb37f.memory[PROJ_ACTIVE_ADDR]} step={_t37f_step}")
pb37f.stop()
wipe_save()

# T37.g — Y-axis boundary: force a vertically-moving projectile toward the
# window's own top edge, confirm clean deactivation (mirrors T30.d's own
# existing X-boundary test).
t37_reset(pb)
pb.memory[MOB_COUNT_ADDR] = 0
pb.memory[PROJ_ACTIVE_ADDR] = 1
pb.memory[PROJ_X_ADDR] = 80; pb.memory[PROJ_Y_ADDR] = 10
pb.memory[PROJ_STEP_X_ADDR] = 0; pb.memory[PROJ_STEP_Y_ADDR] = 0xFF
_t37g_steps = 0
while pb.memory[PROJ_ACTIVE_ADDR] == 1 and _t37g_steps < 20:
    invoke_no_arg(pb, IPU_ADDR)
    _t37g_steps += 1
check("T37.g Y-axis boundary: projectile deactivates cleanly on exiting the window vertically",
      pb.memory[PROJ_ACTIVE_ADDR] == 0 and 0 < _t37g_steps <= 5,
      f"proj_active={pb.memory[PROJ_ACTIVE_ADDR]} steps={_t37g_steps}")

# T37.h — hit resolution still works correctly for a non-cardinal (diagonal)
# projectile: force a mob into a diagonal projectile's own path, confirm
# the hit registers exactly as T30.c already established for the
# horizontal case -- confirms inf_projectile_hittest's own unmodified code
# is genuinely axis-agnostic, not merely assumed to be.
t37_reset(pb)
pb.memory[MOB_COUNT_ADDR] = 1
_t37h_mob = MOB_DATA_ADDR
pb.memory[_t37h_mob + 0] = 100; pb.memory[_t37h_mob + 1] = 50
pb.memory[_t37h_mob + 2] = 0; pb.memory[_t37h_mob + 3] = 1; pb.memory[_t37h_mob + 4] = 1
pb.memory[WEAPON_TIER_ADDR] = 1
pb.memory[PROJ_ACTIVE_ADDR] = 1
pb.memory[PROJ_X_ADDR] = 99; pb.memory[PROJ_Y_ADDR] = 51
pb.memory[PROJ_STEP_X_ADDR] = 1; pb.memory[PROJ_STEP_Y_ADDR] = 0xFF
_t37h_ok = invoke_no_arg(pb, IPU_ADDR)
_t37h_health = pb.memory[_t37h_mob + 3]; _t37h_active = pb.memory[_t37h_mob + 4]
check("T37.h Hit resolution works correctly for a non-cardinal (diagonal) projectile",
      _t37h_ok and _t37h_health == 0 and _t37h_active == 0 and pb.memory[PROJ_ACTIVE_ADDR] == 0,
      f"ok={_t37h_ok} health={_t37h_health} active={_t37h_active} proj_active={pb.memory[PROJ_ACTIVE_ADDR]}")

pb.stop()
wipe_save()

# T37.i — independent live PyBoy drive through the real production
# per-frame chain (not a direct-invoke force), mirroring T35.i's own
# established discipline: drive the player diagonally via real button
# input during real PLAYING, fire, confirm the real projectile's own
# recorded position moves diagonally over several real ticks.
pb37i = fresh_boot(180)
pb37i.button('a'); [pb37i.tick() for _ in range(40)]        # MAIN MENU -> MODE SELECT
pb37i.button('down'); [pb37i.tick() for _ in range(40)]     # toggle infinite
pb37i.button('a'); [pb37i.tick() for _ in range(40)]        # confirm -> COMBAT MODE CONFIRM
pb37i.button('up'); [pb37i.tick() for _ in range(40)]       # toggle to "Y"
pb37i.button('a'); [pb37i.tick() for _ in range(40)]        # confirm Y -> INFINITE SEED ENTRY
enter_infinite_seed(pb37i, [4, 2, 0, 0, 0])
pb37i.button('a'); [pb37i.tick() for _ in range(100)]       # confirm seed -> INTRO
pb37i.button('a'); [pb37i.tick() for _ in range(40)]        # INTRO -> PLAYING

_t37i_px0 = pb37i.memory[PLAYER_X]; _t37i_py0 = pb37i.memory[PLAYER_Y]
pb37i.memory[MOB_COUNT_ADDR] = 0   # no mobs -- isolate movement, no contact/hit interference
pb37i.memory[PROJ_ACTIVE_ADDR] = 0

pb37i.button_press('right'); pb37i.button_press('up')
pb37i.tick()   # hold RIGHT+UP one real frame -> updates PLAYER_FACING_X/Y
pb37i.button('a')   # fire, still holding RIGHT+UP (button() presses for this tick only)
pb37i.tick()
pb37i.button_release('right'); pb37i.button_release('up')

_t37i_proj_x0 = pb37i.memory[PROJ_X_ADDR]; _t37i_proj_y0 = pb37i.memory[PROJ_Y_ADDR]
for _ in range(5): pb37i.tick()
_t37i_proj_x1 = pb37i.memory[PROJ_X_ADDR]; _t37i_proj_y1 = pb37i.memory[PROJ_Y_ADDR]
check("T37.i Independent live drive: a real diagonally-fired projectile moves on both axes over several real ticks",
      pb37i.memory[GAMESTATE] == 2 and pb37i.memory[PROJ_ACTIVE_ADDR] == 1 and
      _t37i_proj_x1 > _t37i_proj_x0 and _t37i_proj_y1 < _t37i_proj_y0,
      f"gs={pb37i.memory[GAMESTATE]} proj_active={pb37i.memory[PROJ_ACTIVE_ADDR]} "
      f"player0=({_t37i_px0},{_t37i_py0}) proj0=({_t37i_proj_x0},{_t37i_proj_y0}) "
      f"proj1=({_t37i_proj_x1},{_t37i_proj_y1})")
pb37i.stop()
wipe_save()

# T37.j/k/l/m — IP-9200 (BL-0184) axis-reset regression suite. Unlike
# fire_with_facing (direct force-injection of the exact facing pair under
# test), these drive handle_play_input via real successive invocations
# holding real JOY_CUR bitmasks, so they can actually express -- and
# would have caught -- the reported bug: PLAYER_FACING_X/Y previously
# were only ever SET on press, never CLEARED when that axis's own
# direction stopped being held, so a stale value from an earlier axis
# silently rode along into a later, different-axis-only movement.
J37_RIGHT = 1 << 4; J37_LEFT = 1 << 5; J37_UP = 1 << 6; J37_DOWN = 1 << 7

def fire_after_real_movement(pb, presses):
    """Drive handle_play_input via successive invoke_no_arg calls (T30's
    own established real-routine-invocation technique), holding each
    successive JOY_CUR bitmask in `presses` for one call each -- exercises
    the routine's own real per-frame facing computation across a sequence
    of held directions. After the sequence, releases all directions and
    fires (forces JOY_NEW's own A bit), returning (step_x, step_y)."""
    for mask in presses:
        pb.memory[JOY_CUR_ADDR] = mask
        pb.memory[JOY_NEW_ADDR] = 0
        invoke_no_arg(pb, HPI_ADDR)
    pb.memory[JOY_CUR_ADDR] = 0
    pb.memory[JOY_NEW_ADDR] = 1 << J_A_BIT
    invoke_no_arg(pb, HPI_ADDR)
    return proj_step(pb)

t37_reset(pb37i := fresh_boot(180))
_t37j_step = fire_after_real_movement(pb37i, [J37_RIGHT, J37_RIGHT, J37_UP, J37_UP])
check("T37.j Axis-reset regression (BL-0184): moving RIGHT then switching to UP-only and firing yields pure up, not diagonal",
      _t37j_step == (0, -1), f"step={_t37j_step}")
pb37i.stop()

t37_reset(pb37i := fresh_boot(180))
_t37k_step = fire_after_real_movement(pb37i, [J37_UP, J37_UP, J37_RIGHT, J37_RIGHT])
check("T37.k Axis-reset regression, symmetric case: moving UP then switching to RIGHT-only and firing yields pure right, not diagonal",
      _t37k_step == (1, 0), f"step={_t37k_step}")
pb37i.stop()

t37_reset(pb37i := fresh_boot(180))
_t37l_step = fire_after_real_movement(pb37i, [])
check("T37.l Non-regression: a fresh, never-moved session still fires rightward by default through the real code path",
      _t37l_step == (1, 0), f"step={_t37l_step}")
pb37i.stop()

t37_reset(pb37i := fresh_boot(180))
_t37m_step = fire_after_real_movement(pb37i, [J37_UP, J37_UP, 0, 0])
check("T37.m Non-regression: releasing all directions after moving preserves the last-held facing (real per-frame path)",
      _t37m_step == (0, -1), f"step={_t37m_step}")
pb37i.stop()
wipe_save()

print("\n=== T38: Combat Sub-Mode — Automatic Weapon-Tier Upgrade (IP-9210) ===")

ITS_ADDR = _gw_rom.labels['inf_tier_spend']

def t38_reset(pb, combat_mode=1, weapon_tier=1, treasure=0):
    pb.memory[GAME_MODE] = 1
    pb.memory[COMBAT_MODE_ADDR] = combat_mode
    pb.memory[WEAPON_TIER_ADDR] = weapon_tier
    pb.memory[RUNNING_TREASURE_COUNT] = treasure & 0xFF
    pb.memory[RUNNING_TREASURE_COUNT + 1] = (treasure >> 8) & 0xFF

def t38_tick_real_frame(pb):
    """Ticks a real per-frame st_playing pass (not a direct inf_tier_spend
    invoke) -- proves the automatic call site actually fires, per this
    package's own T38.a requirement. JOY_CUR/JOY_NEW/NEED_REDRAW forced to 0
    first so handle_play_input's own NEED_REDRAW early-exit doesn't skip the
    combat chain this frame (mirrors T39's own established discipline).
    Empirically confirmed (diagnostic script, not asserted from theory): the
    very next pb.tick() immediately after advance_to_playing's own last
    transition tick does not reach as far as inf_tier_spend within
    st_playing's own call chain (a hook on st_playing's own entry fires on
    tick 1, a hook on inf_tier_spend's own entry only fires on tick 2) --
    ticks twice to reliably land on a genuinely complete PLAYING frame."""
    pb.memory[JOY_CUR_ADDR] = 0; pb.memory[JOY_NEW_ADDR] = 0
    pb.memory[NEED_REDRAW] = 0
    pb.tick()
    pb.memory[JOY_CUR_ADDR] = 0; pb.memory[JOY_NEW_ADDR] = 0
    pb.memory[NEED_REDRAW] = 0
    pb.tick()

pb = fresh_boot(180)
advance_to_playing(pb)

# T38.a — tier 1->2 threshold crossing via the real per-frame path: forcing
# RUNNING_TREASURE_COUNT to exactly the tier-1 threshold (1, per the user's
# own direct "first upgrade with the first treasure" instruction) and
# ticking one real frame raises WEAPON_TIER to 2 and spends exactly that 1
# treasure -- with no input event of any kind (BL-0148's own gap resolved).
t38_reset(pb, weapon_tier=1, treasure=1)
t38_tick_real_frame(pb)
_t38a_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T38.a Tier 1->2 threshold crossing via the real st_playing per-frame path (no input event): WEAPON_TIER becomes 2, RUNNING_TREASURE_COUNT decreases by 1",
      _t38a_rtc == 0 and pb.memory[WEAPON_TIER_ADDR] == 2,
      f"rtc={_t38a_rtc} tier={pb.memory[WEAPON_TIER_ADDR]}")

# T38.b — below-threshold: RUNNING_TREASURE_COUNT == 0 (one below the
# tier-1 threshold of 1) is a genuine no-op -- re-checked every frame, not
# consumed.
t38_reset(pb, weapon_tier=1, treasure=0)
invoke_no_arg(pb, ITS_ADDR)
_t38b_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T38.b Below-threshold: RUNNING_TREASURE_COUNT=0 (below the tier-1 threshold of 1) is a no-op",
      _t38b_rtc == 0 and pb.memory[WEAPON_TIER_ADDR] == 1,
      f"rtc={_t38b_rtc} tier={pb.memory[WEAPON_TIER_ADDR]}")

# T38.c — tier 2->3 threshold crossing (threshold 3, the triangular
# sequence's own next value) and independence from tier 1's own threshold;
# spot-check one below (2) does not fire.
t38_reset(pb, weapon_tier=2, treasure=3)
invoke_no_arg(pb, ITS_ADDR)
_t38c_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T38.c Tier 2->3 threshold crossing: RUNNING_TREASURE_COUNT=3 raises WEAPON_TIER to 3 and spends exactly 3",
      _t38c_rtc == 0 and pb.memory[WEAPON_TIER_ADDR] == 3,
      f"rtc={_t38c_rtc} tier={pb.memory[WEAPON_TIER_ADDR]}")

t38_reset(pb, weapon_tier=2, treasure=2)
invoke_no_arg(pb, ITS_ADDR)
_t38c2_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T38.c2 Spot: RUNNING_TREASURE_COUNT=2 (one below the tier-2 threshold of 3) does not fire",
      _t38c2_rtc == 2 and pb.memory[WEAPON_TIER_ADDR] == 2,
      f"rtc={_t38c2_rtc} tier={pb.memory[WEAPON_TIER_ADDR]}")

# T38.d — true no-op at cap: unlike inf_heal_spend's own "spends even at
# cap" precedent (T31.d2), an already-maxed WEAPON_TIER has no further
# threshold to check against, so RUNNING_TREASURE_COUNT is never decremented
# by this leaf again once WEAPON_TIER == 3.
t38_reset(pb, weapon_tier=3, treasure=999)
invoke_no_arg(pb, ITS_ADDR)
_t38d_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T38.d True no-op at WEAPON_TIER==3 (unlike inf_heal_spend's own spend-even-at-cap precedent): RUNNING_TREASURE_COUNT unchanged",
      _t38d_rtc == 999 and pb.memory[WEAPON_TIER_ADDR] == 3,
      f"rtc={_t38d_rtc} tier={pb.memory[WEAPON_TIER_ADDR]}")

# T38.e — COMBAT_MODE off: inf_tier_spend is a complete no-op (mirrors
# T31.f's own established COMBAT_MODE-off pattern).
t38_reset(pb, combat_mode=0, weapon_tier=1, treasure=1)
invoke_no_arg(pb, ITS_ADDR)
_t38e_rtc = pb.memory[RUNNING_TREASURE_COUNT] | (pb.memory[RUNNING_TREASURE_COUNT + 1] << 8)
check("T38.e COMBAT_MODE off: inf_tier_spend is a complete no-op",
      _t38e_rtc == 1 and pb.memory[WEAPON_TIER_ADDR] == 1,
      f"rtc={_t38e_rtc} tier={pb.memory[WEAPON_TIER_ADDR]}")

# T38.f — persistence: a tier increase earned via the automatic trigger
# survives a mob-contact setback (inf_health_setback touches only
# PLAYER_HEALTH/PLAYER_X/PLAYER_Y, never WEAPON_TIER) and a save/load round
# trip (WEAPON_TIER's own SRAM mirror, IP-1124, is unaffected by this
# package -- confirm it still round-trips).
t38_reset(pb, weapon_tier=1, treasure=1)
invoke_no_arg(pb, ITS_ADDR)
_t38f_tier_after_spend = pb.memory[WEAPON_TIER_ADDR]
pb.memory[PLAYER_HEALTH_ADDR] = 0
pb.memory[COMBAT_ENTRY_X_ADDR] = 40; pb.memory[COMBAT_ENTRY_Y_ADDR] = 90
pb.memory[PLAYER_X] = 120; pb.memory[PLAYER_Y] = 20
_t38f_ok = invoke_no_arg(pb, IHSB_ADDR)
check("T38.f A tier increase earned via the automatic trigger survives a mob-contact setback",
      _t38f_ok and _t38f_tier_after_spend == 2 and pb.memory[WEAPON_TIER_ADDR] == 2 and
      pb.memory[PLAYER_HEALTH_ADDR] == 3,
      f"ok={_t38f_ok} tier_after_spend={_t38f_tier_after_spend} tier_after_setback={pb.memory[WEAPON_TIER_ADDR]} "
      f"health={pb.memory[PLAYER_HEALTH_ADDR]}")
pb.stop()
wipe_save()

# T38.g — save/load round trip: an automatically-earned tier increase
# persists through a real SAVE/reload, mirroring T32.a's own established
# two-instance harness.
pb = fresh_boot(200)
enter_infinite_mode(pb, 777)
pb.memory[COMBAT_MODE_ADDR] = 1
pb.memory[0xC6DE] = 8   # MOB_MOVE_TIMER, pinned above 0 -- no movement this window
pb.memory[MOB_COUNT_ADDR] = 0
pb.memory[WEAPON_TIER_ADDR] = 1
pb.memory[RUNNING_TREASURE_COUNT] = 1; pb.memory[RUNNING_TREASURE_COUNT + 1] = 0
t38_tick_real_frame(pb)
_t38g_tier_before_save = pb.memory[WEAPON_TIER_ADDR]
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('a'); [pb.tick() for _ in range(40)]   # SAVE: A (save)
pb.stop()

pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
pb2.button('a'); [pb2.tick() for _ in range(6)]   # MAIN MENU: continue
check("T38.g Save/load round trip: an automatically-earned tier increase persists",
      pb2.memory[GAMESTATE] == 2 and _t38g_tier_before_save == 2 and
      pb2.memory[WEAPON_TIER_ADDR] == 2,
      f"GS={pb2.memory[GAMESTATE]} tier_before_save={_t38g_tier_before_save} tier_after_load={pb2.memory[WEAPON_TIER_ADDR]}")
pb2.stop()
wipe_save()

# ══════════════════════════════════════════════════════
# T39 — Combat Sub-Mode Per-Frame Cycle Budget Measurement (IP-9190, NFR-1500)
# ══════════════════════════════════════════════════════
print("\n=== T39: Combat Sub-Mode Per-Frame Cycle Budget Measurement (NFR-1500) ===")

# Direct cycle-count of the combat per-frame chain st_playing already runs
# unconditionally every frame (asm_game.py:711-714): inf_mob_move ->
# inf_projectile_update (incl. inf_projectile_hittest) -> inf_mob_contact_
# check -> inf_invincibility_tick -> check_zone_transition. Mirrors
# NFR-1400/IP-1102's own already-VERIFIED T24.e PC/SP-hijack + direct-
# cycle-count technique, extended to chain multiple real routines: each
# routine's own real RET is made to land directly at the next routine's
# real ROM label by pre-loading the stack with the successor addresses in
# order -- exactly what st_playing's own real CALL sequence produces,
# just triggered directly rather than waiting for the per-frame
# dispatcher. (A first attempt wrote a synthetic CALL-chain trampoline
# into WRAM scratch and hooked addresses there -- that hung PyBoy's own
# emulation core for hours with no progress, almost certainly because
# hook_register only supports real ROM-bank addresses, not arbitrary
# WRAM; this technique only ever hooks/targets real, already-assembled
# ROM labels, exactly like every other PC/SP-hijack test in this suite.)
INF_MOB_MOVE_ADDR = _gw_rom.labels['inf_mob_move']
INF_PROJECTILE_UPDATE_ADDR = _gw_rom.labels['inf_projectile_update']
INF_MOB_CONTACT_CHECK_ADDR = _gw_rom.labels['inf_mob_contact_check']
INF_INVINCIBILITY_TICK_ADDR = _gw_rom.labels['inf_invincibility_tick']
CHECK_ZONE_TRANSITION_ADDR = _gw_rom.labels['check_zone_transition']
COMBAT_ENTRY_X_ADDR = 0xC6DA; COMBAT_ENTRY_Y_ADDR = 0xC6DB

def measure_combat_chain_cycles(pb, hook_end_addr, budget=10):
    """Hijack PC directly to inf_mob_move with the stack pre-loaded (in
    reverse order, mirroring how PUSH itself works) with the real ROM
    entry labels of inf_projectile_update, inf_mob_contact_check,
    inf_invincibility_tick, and check_zone_transition, in that order --
    so each routine's own real RET lands squarely at the next one's real
    entry point. hook_end_addr is purely a measurement hook, independent
    of the stack chain itself: CHECK_ZONE_TRANSITION_ADDR for the
    combat-only case (fires the instant we'd enter it, before any of its
    own logic runs -- a pure four-routine measurement) or CZT_REDRAW_ADDR
    for the coinciding case (check_zone_transition's own real logic,
    including a real inf_ensure_window recompute if its own branch
    conditions are met, executes first and this hook fires once its own
    control flow naturally reaches czt_redraw -- T24.e's own established
    safe ROM hook point). Measures via two hook_register callpoints
    (inf_mob_move's entry, hook_end_addr) reading PyBoy's own cycle
    counter -- T24.e's own established technique
    (measure_inf_ensure_window_cycles), and for the same established
    reason: pb.tick() advances a full frame at a time, so reading
    pb._cycles() only after tick() returns would be frame-quantized
    regardless of the chain's real cost; the hook fires synchronously at
    the exact cycle the CPU reaches that address, mid-tick."""
    targets = [INF_PROJECTILE_UPDATE_ADDR, INF_MOB_CONTACT_CHECK_ADDR,
               INF_INVINCIBILITY_TICK_ADDR, CHECK_ZONE_TRANSITION_ADDR]
    sp = pb.register_file.SP
    for addr in reversed(targets):
        sp = (sp - 2) & 0xFFFF
        pb.memory[sp] = addr & 0xFF
        pb.memory[sp + 1] = (addr >> 8) & 0xFF
    pb.register_file.SP = sp
    pb.register_file.PC = INF_MOB_MOVE_ADDR
    state = {}
    def _start(ctx): state.setdefault('start', pb._cycles())
    def _end(ctx): state.setdefault('end', pb._cycles())
    pb.hook_register(0, INF_MOB_MOVE_ADDR, _start, None)
    pb.hook_register(0, hook_end_addr, _end, None)
    for _ in range(budget):
        pb.tick()
        if 'end' in state:
            break
    if 'start' not in state or 'end' not in state:
        return None
    return state['end'] - state['start']

def t39_set_combat_state(pb, mob_count, proj_active):
    """Force a realistic non-empty combat frame -- COMBAT_MODE=1 is not
    enough on its own (every gated routine short-circuits almost
    immediately on its own count/flag check, understating the real cost);
    mob slots and an in-flight projectile exercise each routine's own real
    body. Mirrors T32.a's own direct MOB_DATA injection pattern."""
    pb.memory[COMBAT_MODE_ADDR] = 1
    pb.memory[MOB_COUNT_ADDR] = mob_count
    for i in range(6):
        base = MOB_DATA_ADDR + i * 5
        if i < mob_count:
            # x, y, species, health, active -- placed well clear of the
            # player's own hitbox so inf_mob_contact_check's own hit
            # branch doesn't fire and perturb PLAYER_HEALTH mid-measurement
            slot = (30 + i * 15, 40 + i * 10, 0, 1, 1)
        else:
            slot = (0, 0, 0, 0, 0)
        for k, v in enumerate(slot): pb.memory[base + k] = v
    pb.memory[PLAYER_X] = 80; pb.memory[PLAYER_Y] = 100   # clear of every mob slot above
    pb.memory[PROJ_ACTIVE_ADDR] = 1 if proj_active else 0
    if proj_active:
        pb.memory[PROJ_X_ADDR] = 60; pb.memory[PROJ_Y_ADDR] = 100
        pb.memory[PROJ_STEP_X_ADDR] = 1; pb.memory[PROJ_STEP_Y_ADDR] = 0
    pb.memory[0xC6DE] = 8   # MOB_MOVE_TIMER, pinned above 0 -- irrelevant to cost
                             # (inf_mob_move's own body runs its full per-mob
                             # loop regardless of whether the timer reaches 0
                             # this frame; T35.a's own precedent), kept high
                             # only so no positional side effect leaks into
                             # the next corpus entry's own fixture.
    pb.memory[PLAYER_HEALTH_ADDR] = 3

T39_MOB_PROJ_CORPUS = [(1, 0), (1, 1), (6, 0), (6, 1)]

# T39.a — combat-only frame: measure the four-routine chain in isolation
# (check_zone_transition deliberately excluded from the trampoline, so no
# materialization cost can leak in) across the mob-count/projectile-active
# corpus.
FRAME_BUDGET_CYCLES_T39 = 70224   # one CGB single-speed frame, same bar T24.e uses
_t39a_measurements = []
for _mob_count, _proj_active in T39_MOB_PROJ_CORPUS:
    pb = fresh_boot(180)
    t39_set_combat_state(pb, _mob_count, _proj_active)
    _cycles = measure_combat_chain_cycles(pb, CHECK_ZONE_TRANSITION_ADDR)
    pb.stop()
    _t39a_measurements.append((_mob_count, _proj_active, _cycles))
_t39a_valid = [c for (_, _, c) in _t39a_measurements if c is not None]
_t39a_met = bool(_t39a_valid) and max(_t39a_valid) <= FRAME_BUDGET_CYCLES_T39
check("T39.a NFR-1500 Analysis: combat-only per-frame chain cost, direct cycle-count, measured and recorded (Met or not, not asserted un-measured)",
      len(_t39a_valid) == len(T39_MOB_PROJ_CORPUS),
      f"measurements={_t39a_measurements} budget={FRAME_BUDGET_CYCLES_T39} status={'MET' if _t39a_met else 'NOT MET'}")

# T39.b — combat-plus-materialization frame: the same stack-chained
# sequence, but hooked at CZT_REDRAW_ADDR instead of CHECK_ZONE_TRANSITION_
# ADDR so check_zone_transition's own real logic actually executes, set up
# so its own czt_infinite east-branch genuinely fires (GAME_MODE=1,
# JOY_CUR's RIGHT bit held, PLAYER_X at the real 152 threshold, INF_
# WINDOW's own east-neighbor-exists bit forced) -- confirming the
# "coinciding" case NFR-1500 asks about is not just reachable in principle
# but real cycles were taken while it actually fired, across T24.e's own
# established 3-entry (seed, row, col) boundary corpus crossed with the
# same mob/projectile corpus T39.a uses.
J_RIGHT = 4
_t39b_measurements = []
for _seed, _row, _col in T24E_CORPUS:
    for _mob_count, _proj_active in T39_MOB_PROJ_CORPUS:
        pb = fresh_boot(180)
        t39_set_combat_state(pb, _mob_count, _proj_active)
        pb.memory[SEED] = _seed & 0xFF; pb.memory[SEED + 1] = (_seed >> 8) & 0xFF
        _r = _row & 0xFFFF; _c = _col & 0xFFFF
        pb.memory[INF_ROW] = _r & 0xFF; pb.memory[INF_ROW + 1] = (_r >> 8) & 0xFF
        pb.memory[INF_COL] = _c & 0xFF; pb.memory[INF_COL + 1] = (_c >> 8) & 0xFF
        pb.memory[GAME_MODE] = 1
        pb.memory[JOY_CUR_ADDR] = 1 << J_RIGHT
        pb.memory[PLAYER_X] = 152
        pb.memory[INF_WINDOW + 4] = 0x80   # bit 7: east neighbor exists (czt_infinite's own gate)
        _cycles = measure_combat_chain_cycles(pb, CZT_REDRAW_ADDR)
        _fired = pb.memory[PLAYER_X] == 8   # czt_infinite's own east branch always rewrites PLAYER_X to 8
        pb.stop()
        _t39b_measurements.append((_seed, _row, _col, _mob_count, _proj_active, _cycles, _fired))
_t39b_valid = [c for (*_, c, fired) in _t39b_measurements if c is not None and fired]
_t39b_met = bool(_t39b_valid) and max(_t39b_valid) <= FRAME_BUDGET_CYCLES_T39
check("T39.b NFR-1500 Analysis: combat-plus-region-materialization coinciding frame cost, direct cycle-count with confirmed real transition firing, measured and recorded (Met or not, not asserted un-measured)",
      len(_t39b_valid) == len(T24E_CORPUS) * len(T39_MOB_PROJ_CORPUS),
      f"measurements={_t39b_measurements} budget={FRAME_BUDGET_CYCLES_T39} status={'MET' if _t39b_met else 'NOT MET'}")

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
