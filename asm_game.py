"""
asm_game.py — SM83 game logic for Bunny Quest (3x3 zone grid).

Call build_game_asm(rom) to emit code starting at 0x0150.
Returns dict of patch-point addresses for build_rom.py to fill in.

Zone layout (CUR_ZONE = row*3 + col):
   col0   col1     col2
0  Beach  Forest   Mountain
1  Lake   Village  Cave
2  Desert Plains   Castle
"""
from gbc_lib import ROM
from tiles import (TL_CARROT, TL_STAR, TL_FLOWER_OBJ,
                   TL_HEART_FULL, TL_HEART_EMPTY, TL_DIGIT_0,
                   TL_ARROW_U, TL_ARROW_D, TL_ARROW_L, TL_ARROW_R,
                   TL_BLOCKED_U, TL_BLOCKED_D, TL_BLOCKED_L, TL_BLOCKED_R,
                   TL_BG_BLANK)

# ── WRAM addresses ─────────────────────────────────────────
GAMESTATE      = 0xC000
PLAYER_X       = 0xC001
PLAYER_Y       = 0xC002
PLAYER_DIR     = 0xC003
PLAYER_FRAME   = 0xC004
ANIM_CTR       = 0xC005
SCORE          = 0xC006   # 0-99 stars/flowers
SCORE_DIRTY    = 0xC007
CUR_ZONE       = 0xC008   # 0-8
CARROTS_COUNT  = 0xC009   # 0-9
NEED_REDRAW    = 0xC00A
TRANSITION_TO  = 0xC00B
JOY_CUR        = 0xC00C
JOY_PREV       = 0xC00D
JOY_NEW        = 0xC00E
MUSIC_CTR      = 0xC00F
MUSIC_PTR_LO   = 0xC010
MUSIC_PTR_HI   = 0xC011
VBLANK_FLAG    = 0xC012
TMP1           = 0xC013
TMP2           = 0xC014
CARROT_FLAGS   = 0xC015   # 9 bytes — one per zone, 0/1
COLL_DATA      = 0xC020
COLL_COUNT     = 0xC050
SEED           = 0xC069  # 2 bytes, C069-C06A — player-entered generation seed (IP-1020)
WORLD_SCALE    = 0xC06B  # 1 byte — regions per grid axis, 2-9 (IP-1020)
REGION_GRAPH   = 0xC070  # 5 bytes/region (1 biome-id + 4 neighbor-region-index), up to 81
                          # regions = 405 bytes worst case (IP-1020)
KEYITEM_FLAGS  = 0xC220  # up to 81 bytes, one collected-flag per region — generalizes
                          # CARROT_FLAGS (IP-1020). All 81 indices are live as of IP-9050
                          # (CUR_ZONE reaches the full generated-world range); both reset
                          # sites (st_intro/st_victory) widened to match (BL-0063)
KEYITEM_COUNT  = CARROTS_COUNT  # same WRAM slot as CARROTS_COUNT — item-agnostic alias
                                  # for the running collected-count (IP-1020, FR-3220)
GW_TOP_ROW     = 0xC271  # 9 bytes — generate_world's own transient scratch: the biome
                          # of the region above each column, written before it's read
                          # (NFR-2200: "the routine's own prior output", never external
                          # or uninitialized state). Not part of the persisted data model.
GW_REGION_IDX  = 0xC27A  # 1 byte — generate_world's own loop counter (0..scale²-1)
GW_B_SCRATCH   = 0xC27B  # 1 byte — generate_world's own scratch (anchor, then result)
GW_SCALE_SQ    = 0xC27C  # 1 byte — generate_world's own precomputed WORLD_SCALE²
MM_SAVE_VALID  = 0xC27D  # 1 byte — MAIN MENU's cached save-validity probe (magic+version),
                          # computed once on state entry, not re-probed every frame (IP-1040)
MM_CURSOR      = 0xC27E  # 1 byte — MAIN MENU highlighted option: 0=continue, 1=new game (IP-1040)
SSE_DIGITS     = 0xC27F  # 5 bytes, C27F-C283 — SEED/SCALE ENTRY's 5 independent decimal
                          # digits (ten-thousands..ones, each 0-9), edited directly; composed
                          # into the real 16-bit SEED (saturating at 65535) only on A-confirm,
                          # per ADR-0010's digit-cursor picker (IP-1040)
SSE_SCALE      = 0xC284  # 1 byte — SEED/SCALE ENTRY's scale value, 2-9, default 3 (IP-1040)
SSE_CURSOR     = 0xC285  # 1 byte — SEED/SCALE ENTRY's cursor position, 0-4 = digit index
                          # (MSB first), 5 = scale slot (IP-1040)
SCOREITEM_FLAGS = 0xC286  # up to 81 bytes, C286-C2D6 — one bitfield per region, bit =
                          # list-position (FR-5220), generalized from the old fixed
                          # 9-byte/9-zone array (IP-9070) the same way KEYITEM_FLAGS
                          # generalized CARROT_FLAGS. Relocated (not grown in place at
                          # its old 0xC060 address) to the confirmed-unused WRAM gap
                          # between SSE_CURSOR and OAM_BUF — growing to 81 bytes in place
                          # would have collided with REGION_GRAPH at 0xC070.
MM_JUST_ENTERED = 0xC2D7  # 1 byte — set by every GAMESTATE -> GS_MAIN_MENU transition site
                          # (boot, st_victory's A-press, st_save's SELECT option,
                          # st_seed_scale_entry's B-cancel), cleared by mm_on_entry once
                          # consumed. Lets mm_on_entry tell a genuine state entry (reset
                          # MM_CURSOR to its default) apart from a same-state redraw the
                          # player's own toggle causes (leave MM_CURSOR alone) — IP-9060,
                          # BL-0048's fix. Sits in the confirmed-unused byte immediately
                          # after SCOREITEM_FLAGS's own 81-byte extent.
DRA_ROW        = 0xC2D8  # 1 byte -- draw_region_arrows' own re-derived row (CUR_ZONE /
DRA_COL        = 0xC2D9  # 1 byte -- WORLD_SCALE) / col (CUR_ZONE MOD WORLD_SCALE), IP-1080
                          # (FR-2330). Transient, meaningless outside a draw_region_arrows
                          # call, same convention as the GW_* family below. Added mid-
                          # implementation, not named in IP-1080's own package text (which
                          # suggested reusing TMP1/TMP2): TMP1 turned out to double as
                          # handle_play_input's own per-frame "did the player move" flag,
                          # clobbered on the very next frame after draw_region_arrows sets
                          # it -- confirmed by a real T20.b/c test failure (row/col reading
                          # back as the FIRST region's stale values), not assumed. TMP2 is
                          # not similarly touched (only generate_world uses it, which never
                          # runs during PLAYING), but both moved here together for a self-
                          # contained, unambiguously-safe pair rather than mixing TMP2 with
                          # a new dedicated byte. Sits in the same confirmed-unused gap
                          # MM_JUST_ENTERED's own comment already names (SSE_CURSOR..OAM_BUF).
OAM_BUF        = 0xC300  # 160 bytes, C300-C39F, shadow OAM

GW_MAZE_STATE  = 0xC3A0  # up to 81 bytes, one per region: bit 7 = visited, bits 1:0 =
                          # parent-direction (0=up,1=down,2=left,3=right, matching
                          # REGION_GRAPH's own neighbor-byte order), recorded at carve time.
                          # The maze-generation pass's own backtracking state -- reuses
                          # REGION_GRAPH's own already-written full-lattice candidate bytes
                          # as the "does a grid-adjacent region exist here" test rather than
                          # re-deriving grid adjacency (IP-1070, ADR-0012 point 3). First
                          # unclaimed byte past OAM_BUF's own 160-byte extent (C300-C39F).
                          # Transient, meaningless outside a generate_world call, like
                          # GW_TOP_ROW.
GW_CUR_REGION  = 0xC3F1  # 1 byte -- the maze pass's own current-region pointer during the
                          # spanning-tree carve (IP-1070)
GW_MAZE_DIR    = 0xC3F2  # 1 byte -- during carving: the starting-direction draw / direction
                          # currently being tried (0-3). Repurposed, once carving completes,
                          # as the canonical prune pass's own "current direction" (1=down,
                          # 3=right) -- the two uses never overlap in time, the same
                          # non-overlapping one-shot-scratch reuse pattern TMP1/TMP2 already
                          # establish elsewhere in this routine (IP-1070).
GW_BRAID_IDX   = 0xC3F3  # 1 byte -- during carving: the current region's own try-count
                          # (0-3, how many of its 4 directions have been tried).
                          # Repurposed, once carving completes, as the canonical prune
                          # pass's own region-loop counter (0..scale²-1) -- same
                          # non-overlapping reuse pattern as GW_MAZE_DIR above (IP-1070).
GW_MAZE_DRAW_CTR = 0xC3F4  # 1 byte -- a monotonic, never-persisted per-draw counter, XORed
                          # into every gw_prng_step draw the maze pass performs (both the
                          # carve phase's direction draw and the braid phase's keep/prune
                          # draw) before the drawn byte is used for a decision, per
                          # ADR-0013 -- decorrelates this pass's own repeated draws without
                          # touching gw_prng_step's own algorithm or any other call site
                          # (R113: the shipped PRNG collapses to a degenerate fixed point/
                          # short cycle under many back-to-back draws with no such
                          # perturbation). Never fed back into TMP1/TMP2.
GW_KI_PLACED   = 0xC3F5  # 1 byte -- IP-1021 (FR-9160/ADR-0015): the KeyItem-placement pass's
                          # own running count of regions marked "present" so far (capped at
                          # WORLD_SCALE), transient like the rest of the GW_* family. First
                          # unclaimed byte past GW_MAZE_DRAW_CTR (0xC3F4). This pass consumes
                          # no PRNG draws, so GW_MAZE_DRAW_CTR's own running state is untouched
                          # by it.

# Infinite Mode (IP-1102). GAME_MODE was originally planned as IP-1100's own
# addition, but IP-1102 was implemented first and needs it (dsr_p/check_
# zone_transition both gate on it) -- claimed here instead; IP-1100's own
# future implementation reuses this constant rather than redefining it.
GAME_MODE      = 0xC3F6  # 1 byte -- 0=finite (default, boot-cleared explicitly, see below --
                          # outside the 0xC000-C2FF boot-clear range), 1=infinite. No code path
                          # currently writes 1 (IP-1100, not yet implemented, is what will) --
                          # only test_rom.py's own T24 suite pokes this directly today.
INF_ROW        = 0xC3F7  # 2 bytes, C3F7-C3F8 -- player's current region row (signed 16-bit,
                          # low byte first, mirrors SEED's own byte order), Infinite Mode only
INF_COL        = 0xC3F9  # 2 bytes, C3F9-C3FA -- player's current region col, same convention
INF_WINDOW     = 0xC3FB  # 9 bytes, C3FB-C403 -- 3x3 materialized window, row-major (index =
                          # (dr+1)*3+(dc+1), dr/dc in {-1,0,1}), center cell (index 4, C3FF) =
                          # current region. 1 byte/region, IP-1101's own output format (bits
                          # 0-2 biome-id, bits 3-6 connectivity: up/down/left/right, 1=open)
INF_TREASURE_HERE = 0xC404  # 1 byte -- transient cache: current region's own treasure-
                          # presence-and-uncollected flag for this materialization.
                          # Reserved by IP-1102 (same contiguous address run); populated
                          # by IP-1103: written from INF_MZ_TREASURE at inf_ensure_window's
                          # center-cell materialization, cleared on collection
                          # (check_collisions' GAME_MODE==1 branch), read by
                          # setup_zone_collects' infinite-mode spawn branch.

# Win-condition state (IP-1103, FR-10400). Outside the 0xC000-C2FF boot-clear
# range -- explicitly boot-cleared (see the GAME_MODE clear below), the same
# uninitialized-WRAM lesson IP-1102 recorded there: TOP_SCORE_TABLE is read
# (compared against) before any code path guarantees a write, and a fresh
# cartridge must not present garbage bytes as standing high scores. When a
# NEW run's count resets (vs. an abandoned run's count persisting) is NOT
# decided here -- that is BL-0112/OQ3's own open question (IP-1103 §13), and
# this boot clear is initialization hygiene, not run-lifecycle semantics.
RUNNING_TREASURE_COUNT = 0xC405  # 2 bytes, C405-C406 -- current run's treasure total,
                          # unsigned 16-bit, low byte first (SEED's own byte-order
                          # convention). No overflow guard (IP-1103 §6: 65536 treasures
                          # is not a realistic play scenario).
TOP_SCORE_TABLE = 0xC407  # 6 bytes, C407-C40C -- 3 entries x 2 bytes (unsigned 16-bit,
                          # low byte first), stored descending: index 0 (C407-C408) is
                          # the current high score, index 2 (C40B-C40C) the lowest.
                          # Written only by inf_check_top_score (no automatic call site
                          # yet -- BL-0112) and, later, IP-1104's save/load restore.

# 0xC3F6-0xC40C is the full range IP-1100/1102/1103's own already-documented
# WRAM plan reserves (docs/implementation/packages/IP-1100.../IP-1102.../
# IP-1103...md) -- GAME_MODE/INF_ROW/INF_COL/INF_WINDOW/INF_TREASURE_HERE
# (IP-1102) claim 0xC3F6-0xC404; RUNNING_TREASURE_COUNT/TOP_SCORE_TABLE
# (IP-1103, above) claim the remaining 0xC405-0xC40C -- the range is now
# fully claimed.
INF_MZ_ROW      = 0xC40D  # 2 bytes, C40D-C40E -- inf_materialize_region's own row input
                          # (signed 16-bit, low byte first, mirrors SEED's own byte order)
INF_MZ_COL      = 0xC40F  # 2 bytes, C40F-C410 -- column input, same convention
INF_MZ_RESULT   = 0xC411  # 1 byte -- output: packed biome (bits 0-2) + connectivity nibble
                          # (bits 3-6: up/down/left/right, 1=open), the TWBS's own per-region
                          # encoding decision
INF_MZ_TREASURE = 0xC412  # 1 byte -- output: 0 or 1, hash(SEED,row,col) mod 16 == 0 (K=16)
INF_MZ_BIOME    = 0xC413  # 1 byte -- transient scratch: own biome value, held while the
                          # south/east neighbor consultations run
INF_MZ_BIAS     = 0xC414  # 1 byte -- transient scratch: own carve-bias (0=carve north,
                          # 1=carve west) -- Binary Tree construction (ADR-0016 point 5)
INF_MZ_TROW     = 0xC415  # 2 bytes, C415-C416 -- transient scratch: the row currently being
                          # hashed by inf_region_seed0 (own region or a neighbor)
INF_MZ_TCOL     = 0xC417  # 2 bytes, C417-C418 -- transient scratch: the column currently
                          # being hashed by inf_region_seed0

# IP-1104: visited-region ledger, live WRAM working copy. First unclaimed
# bytes past INF_MZ_TCOL's own end (0xC418). Amended 2026-07-16 per BL-0119
# (originally planned as SRAM-only, touched on every collection -- that
# would have needed an MBC1-enable bracket around every single pickup, and
# would still have left inf_ensure_window, which runs on every navigation
# step, nothing cheap to consult, exactly why the mid-session respawn gap
# went unnoticed at planning time). This WRAM copy is what makes a
# per-navigation-step ledger check affordable: no SRAM access outside the
# two explicit save/load memcpy calls below, the same "WRAM working copy +
# SRAM backing store" split KEYITEM_FLAGS/SCOREITEM_FLAGS/CARROT_FLAGS
# already use project-wide.
LEDGER_COUNT   = 0xC419  # 1 byte -- number of valid ledger entries, 0-128
LEDGER_CURSOR  = 0xC41A  # 1 byte -- FIFO write cursor, 0-127
LEDGER         = 0xC41B  # 640 bytes, C41B-C69A -- 128 entries x 5 bytes: row (signed
                          # 16-bit, low byte first), col (same), collected-flag (1 byte).
                          # LEDGER_COUNT/LEDGER_CURSOR/LEDGER form one contiguous 642-byte
                          # block (C419-C69A), deliberately laid out to mirror
                          # SRAM_LEDGER_COUNT/SRAM_LEDGER_CURSOR/SRAM_LEDGER byte-for-byte
                          # (same field order, same sizes) so save/load is a single memcpy.

SAVE_VERSION_ADDR = 0xA012   # save-format version guard (FR-5220 / Design Decision 2)
SAVE_VERSION_VAL  = 0x05     # bumped 0x04->0x05 (IP-1104, fifth bump since ship — the
                              # value sequence is strictly monotonic, never reused). A single
                              # version guard covers both save shapes; GAME_MODE (restored
                              # first on load) selects which fields are meaningful.
SRAM_SEED          = 0xA01C  # 2 bytes, A01C-A01D — SEED mirror (IP-1050)
SRAM_WORLD_SCALE   = 0xA01E  # 1 byte — WORLD_SCALE mirror (IP-1050)
SRAM_KEYITEM_FLAGS = 0xA01F  # up to 81 bytes, A01F-A06F — KEYITEM_FLAGS mirror,
                              # generalizes the old CARROT_FLAGS mirror at A009-A011
                              # (IP-1050). REGION_GRAPH itself is never persisted —
                              # it regenerates deterministically from (SEED, WORLD_SCALE)
                              # via generate_world on load (ADR-0009).
SRAM_SCOREITEM    = 0xA070   # up to 81 bytes, A070-A0C0 — SCOREITEM_FLAGS mirror,
                              # generalized from the old fixed 9-byte/9-zone mirror at
                              # A013-A01B (IP-9070). Relocated to immediately after
                              # SRAM_KEYITEM_FLAGS's own end, leaving SRAM_SEED/
                              # SRAM_WORLD_SCALE/SRAM_KEYITEM_FLAGS's addresses untouched.

# IP-1104: Infinite Mode save shape, GAME_MODE-gated (Workflow D). First
# unclaimed bytes past SRAM_SCOREITEM's own end (0xA0C0).
SRAM_GAME_MODE = 0xA0C1  # 1 byte -- mirrors GAME_MODE
SRAM_INF_ROW   = 0xA0C2  # 2 bytes, A0C2-A0C3 -- mirrors INF_ROW
SRAM_INF_COL   = 0xA0C4  # 2 bytes, A0C4-A0C5 -- mirrors INF_COL
SRAM_RUNNING_TREASURE_COUNT = 0xA0C6  # 2 bytes, A0C6-A0C7 -- mirrors RUNNING_TREASURE_COUNT
SRAM_TOP_SCORE_TABLE = 0xA0C8  # 6 bytes, A0C8-A0CD -- mirrors TOP_SCORE_TABLE. Persists
                          # across new games (not per-run state) -- ADR-0017 point 4's own
                          # "persistent high score, distinct from per-run state" split.
SRAM_LEDGER_COUNT  = 0xA0CE  # 1 byte -- mirrors LEDGER_COUNT
SRAM_LEDGER_CURSOR = 0xA0CF  # 1 byte -- mirrors LEDGER_CURSOR
SRAM_LEDGER        = 0xA0D0  # 640 bytes, A0D0-A34F -- mirrors LEDGER, identical 5-byte-
                          # per-entry format. SRAM_LEDGER_COUNT/SRAM_LEDGER_CURSOR/
                          # SRAM_LEDGER form one contiguous 642-byte block (A0CE-A34F),
                          # the exact SRAM mirror of LEDGER_COUNT/LEDGER_CURSOR/LEDGER above.

J_A=0; J_B=1; J_SELECT=2; J_START=3; J_RIGHT=4; J_LEFT=5; J_UP=6; J_DOWN=7

P1=0x00; NR11=0x11; NR12=0x12; NR13=0x13; NR14=0x14
NR50=0x24; NR51=0x25; NR52=0x26
LCDC=0x40; LY=0x44; DMA=0x46; VBK=0x4F; BCPS=0x68; BCPD=0x69; OCPS=0x6A; OCPD=0x6B

HRAM_DMA = 0xFF80

GS_TITLE, GS_INTRO, GS_PLAYING, GS_SAVE, GS_MAP, GS_VICTORY = 0, 1, 2, 3, 4, 5
# GS_TITLE is superseded (IP-1040): boot now always reaches GS_MAIN_MENU, so
# st_title's dispatch entry/code is unreachable dead code, left in place —
# same orphaning precedent as CARROT_FLAGS/village_screen etc.
GS_MAIN_MENU, GS_SEED_SCALE_ENTRY = 6, 7
GS_SELECT_MENU, GS_LEGEND = 8, 9  # IP-1090: SELECT now opens a small
                                  # map/legend cursor menu instead of
                                  # jumping directly to GS_MAP (GDS-01 §4c)
GS_MODE_SELECT, GS_INFINITE_SEED_ENTRY = 10, 11  # IP-1100: MAIN MENU's
                                  # "new game" now opens a finite/infinite
                                  # cursor menu instead of jumping directly
                                  # to GS_SEED_SCALE_ENTRY (GDS-01 §4d)


def build_game_asm(rom: ROM) -> dict:
    patches = {}

    # RST vectors
    for a in range(0x0000, 0x0040):
        rom.data[a] = 0xD9

    # VBlank ISR
    rom.seek(0x0040)
    rom.PUSH_AF()
    rom.LD_A_n(1); rom.LD_nn_A(VBLANK_FLAG)
    rom.POP_AF(); rom.RETI()

    for a in (0x0048, 0x0050, 0x0058, 0x0060):
        rom.seek(a); rom.RETI()

    # Entry point
    rom.seek(0x0100)
    rom.NOP(); rom.JP('main')

    # ── MAIN ─────────────────────────────────────────────
    rom.seek(0x0150)
    rom.label('main')
    rom.LD_SP_nn(0xFFFE)
    rom.DI()

    # Wait VBlank, disable LCD
    rom.label('wv1')
    rom.LDH_A_n(LY); rom.CP_n(144); rom.JR_C('wv1')
    rom.XOR_A(); rom.LDH_n_A(LCDC)

    # Clear WRAM C000-C2FF
    # NB: re-zero A each iteration; the BC==0 check clobbers A via LD A,B.
    rom.LD_HL_nn(0xC000); rom.LD_BC_nn(0x0300)
    rom.label('cw')
    rom.XOR_A(); rom.LD_HLI_A(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cw')

    # Clear shadow OAM
    rom.LD_HL_nn(OAM_BUF); rom.LD_B_n(160); rom.XOR_A()
    rom.label('coam'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('coam')

    # Clear GAME_MODE (IP-1102) -- outside the 0xC000-C2FF range above, but
    # dsr_p/check_zone_transition read it every PLAYING frame with no
    # guaranteed prior write until IP-1100's own new-game flow exists;
    # without an explicit boot value this would read uninitialized WRAM and
    # could spuriously route ordinary finite-mode gameplay into the new,
    # untested Infinite Mode code paths. Mirrors the shadow-OAM clear
    # immediately above — a targeted single-purpose clear, not a blind
    # widening of the existing 0xC000-C2FF loop (which would also needlessly
    # re-zero OAM_BUF/GW_* in between, both already handled by their own
    # write-before-read discipline).
    rom.XOR_A(); rom.LD_nn_A(GAME_MODE)

    # Clear RUNNING_TREASURE_COUNT + TOP_SCORE_TABLE (IP-1103) -- same
    # outside-the-0xC000-C2FF-range situation, same targeted-clear rationale
    # as GAME_MODE immediately above: TOP_SCORE_TABLE must never present
    # boot-time garbage as standing high scores. 8 bytes, 0xC405-0xC40C.
    rom.LD_HL_nn(RUNNING_TREASURE_COUNT); rom.LD_B_n(8); rom.XOR_A()
    rom.label('cts'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('cts')

    # Clear LEDGER_COUNT/LEDGER_CURSOR (IP-1104) -- same targeted-clear
    # rationale: a fresh cartridge must start with an empty ledger, not
    # garbage read as valid entries. LEDGER's own 640 bytes need no boot
    # clear -- LEDGER_COUNT == 0 gates validity, the same "count gates
    # array validity" convention COLL_COUNT/COLL_DATA already use.
    rom.XOR_A(); rom.LD_nn_A(LEDGER_COUNT); rom.LD_nn_A(LEDGER_CURSOR)

    # Clear VRAM bank 0 (same A-clobber caveat — re-zero each iter)
    rom.XOR_A(); rom.LDH_n_A(VBK)
    rom.LD_HL_nn(0x8000); rom.LD_BC_nn(0x2000)
    rom.label('cv')
    rom.XOR_A(); rom.LD_HLI_A(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cv')

    # Copy tile data → 0x8000
    rom.LD_DE_nn(0); patches['tile_src'] = rom.pos - 2
    rom.LD_HL_nn(0x8000); rom.LD_BC_nn(256 * 16)
    rom.CALL('memcpy')

    # BG palettes
    rom.LD_A_n(0x80); rom.LDH_n_A(BCPS)
    rom.LD_DE_nn(0); patches['bg_pal'] = rom.pos - 2
    rom.LD_B_n(64)
    rom.label('bgp')
    rom.LD_A_DE(); rom.LDH_n_A(BCPD); rom.INC_DE(); rom.DEC_B()
    rom.JR_NZ('bgp')

    # OBJ palettes
    rom.LD_A_n(0x80); rom.LDH_n_A(OCPS)
    rom.LD_DE_nn(0); patches['obj_pal'] = rom.pos - 2
    rom.LD_B_n(64)
    rom.label('obp')
    rom.LD_A_DE(); rom.LDH_n_A(OCPD); rom.INC_DE(); rom.DEC_B()
    rom.JR_NZ('obp')

    # Install DMA-wait routine in HRAM
    rom.LD_HL_nn(HRAM_DMA)
    for b in [0x3E, 40, 0x3D, 0x20, 0xFD, 0xC9]:
        rom.LD_A_n(b); rom.LD_HLI_A()

    # Init sound
    rom.LD_A_n(0x80); rom.LDH_n_A(NR52)
    rom.LD_A_n(0x77); rom.LDH_n_A(NR50)
    rom.LD_A_n(0xFF); rom.LDH_n_A(NR51)
    rom.LD_A_n(0x80); rom.LDH_n_A(NR11)
    rom.LD_A_n(0xD2); rom.LDH_n_A(NR12)

    rom.LD_A_n(0); patches['mus_lo'] = rom.pos - 1
    rom.LD_nn_A(MUSIC_PTR_LO)
    rom.LD_A_n(0); patches['mus_hi'] = rom.pos - 1
    rom.LD_nn_A(MUSIC_PTR_HI)
    rom.LD_A_n(1); rom.LD_nn_A(MUSIC_CTR)

    # IP-1040: the auto-load-on-boot bypass (unconditional try_load_save call)
    # is retired — boot now always reaches MAIN MENU. try_load_save's call
    # moves to become MAIN MENU's "continue" action only (ADR-0009/GDS-01 §2a).
    rom.LD_A_n(GS_MAIN_MENU)
    rom.LD_nn_A(GAMESTATE); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.LD_nn_A(MM_JUST_ENTERED)

    rom.LD_A_n(0x97); rom.LDH_n_A(LCDC)   # 0x97 = LCD on + 8x16 OBJ
    rom.LD_A_n(0x01); rom.LD_nn_A(0xFFFF)
    rom.EI()

    # ── MAIN LOOP ────────────────────────────────────────
    rom.label('game_loop')
    rom.HALT()
    rom.LD_A_nn(VBLANK_FLAG); rom.OR_A()
    rom.JR_Z('game_loop')
    rom.XOR_A(); rom.LD_nn_A(VBLANK_FLAG)

    rom.CALL('update_status_disp')

    rom.LD_A_nn(NEED_REDRAW); rom.OR_A()
    rom.CALL_NZ('do_screen_redraw')

    rom.CALL('read_joypad')

    rom.LD_A_nn(GAMESTATE)
    rom.CP_n(GS_TITLE);   rom.JP_Z('st_title')
    rom.CP_n(GS_INTRO);   rom.JP_Z('st_intro')
    rom.CP_n(GS_PLAYING); rom.JP_Z('st_playing')
    rom.CP_n(GS_SAVE);    rom.JP_Z('st_save')
    rom.CP_n(GS_MAP);     rom.JP_Z('st_map')
    rom.CP_n(GS_VICTORY); rom.JP_Z('st_victory')
    rom.CP_n(GS_MAIN_MENU); rom.JP_Z('st_main_menu')
    rom.CP_n(GS_SEED_SCALE_ENTRY); rom.JP_Z('st_seed_scale_entry')
    rom.CP_n(GS_SELECT_MENU); rom.JP_Z('st_select_menu')
    rom.CP_n(GS_LEGEND); rom.JP_Z('st_legend')
    rom.CP_n(GS_MODE_SELECT); rom.JP_Z('st_mode_select')
    rom.CP_n(GS_INFINITE_SEED_ENTRY); rom.JP_Z('st_infinite_seed_entry')
    rom.JP('end_frame')

    # ── State: TITLE ─────────────────────────────────────
    rom.label('st_title')
    rom.LD_A_nn(JOY_NEW); rom.AND_n((1<<J_A)|(1<<J_START))
    rom.JP_Z('end_frame')
    rom.LD_A_n(GS_INTRO); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: INTRO ─────────────────────────────────────
    rom.label('st_intro')
    rom.LD_A_nn(JOY_NEW); rom.AND_n(1 << J_A)
    rom.JP_Z('end_frame')
    # reset run
    rom.XOR_A()
    rom.LD_nn_A(SCORE); rom.LD_nn_A(CARROTS_COUNT); rom.LD_nn_A(CUR_ZONE)
    # KEYITEM_FLAGS is no longer cleared here (IP-1021) — generate_world's own
    # placement pass now writes a real present/collected/absent pattern per
    # region, and this state is entered only after generate_world has already
    # run (from the SEED/SCALE ENTRY confirm handler), so clearing here would
    # destroy that placement. The stale-prior-playthrough-bytes clear moved to
    # immediately before CALL('generate_world') instead.
    # clear SCOREITEM_FLAGS (81 bytes — IP-9070, generalized from the old fixed
    # 9-byte/9-zone clear the same way KEYITEM_FLAGS's own boot-clear was sized
    # for CARROT_FLAGS's 9-byte predecessor) — FR-5220 new-game reset
    rom.LD_HL_nn(SCOREITEM_FLAGS); rom.LD_B_n(81); rom.XOR_A()
    rom.label('si_clr2'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('si_clr2')
    rom.LD_A_n(76); rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(80); rom.LD_nn_A(PLAYER_Y)
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: PLAYING ───────────────────────────────────
    rom.label('st_playing')
    rom.CALL('handle_play_input')
    rom.LD_A_nn(NEED_REDRAW); rom.OR_A()
    rom.JP_NZ('end_frame')
    rom.CALL('check_collisions')
    rom.CALL('check_zone_transition')
    rom.CALL('check_complete')
    rom.JP('end_frame')

    # ── State: SAVE ──────────────────────────────────────
    rom.label('st_save')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()
    rom.BIT_b_B(J_A); rom.JR_Z('sv_b')
    rom.CALL('save_to_sram')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('sv_b')
    rom.BIT_b_B(J_B); rom.JR_Z('sv_sel')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    # IP-1040: third option, exit-to-main-menu with auto-save (FR-1190) —
    # calls the exact same save-write routine A(save) already calls, no
    # duplicated/divergent save-write logic, then targets MAIN MENU instead
    # of PLAYING (the distinguishing behavior versus A/B).
    rom.label('sv_sel')
    rom.BIT_b_B(J_SELECT); rom.JP_Z('end_frame')
    rom.CALL('save_to_sram')
    rom.LD_A_n(GS_MAIN_MENU); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.JP('end_frame')

    # ── State: MAP ───────────────────────────────────────
    rom.label('st_map')
    rom.LD_A_nn(JOY_NEW); rom.AND_n((1<<J_B)|(1<<J_SELECT))
    rom.JP_Z('end_frame')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: VICTORY ───────────────────────────────────
    rom.label('st_victory')
    rom.LD_A_nn(JOY_NEW); rom.AND_n((1<<J_A)|(1<<J_START))
    rom.JP_Z('end_frame')
    # IP-1040: target is now MAIN MENU, not the superseded TITLE state.
    rom.LD_A_n(GS_MAIN_MENU); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.LD_nn_A(MM_JUST_ENTERED)
    # clear progress
    rom.XOR_A(); rom.LD_nn_A(CARROTS_COUNT); rom.LD_nn_A(SCORE)
    # clear KEYITEM_FLAGS (81 bytes — IP-1020, generalizes CARROT_FLAGS; widened
    # by IP-9050/BL-0063, see st_intro's identical widening)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.LD_B_n(81); rom.XOR_A()
    rom.label('sv_clrf'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('sv_clrf')
    # clear SCOREITEM_FLAGS (81 bytes — IP-9070, see st_intro's identical widening)
    # — FR-5220 victory progress-clear
    rom.LD_HL_nn(SCOREITEM_FLAGS); rom.LD_B_n(81); rom.XOR_A()
    rom.label('sv_clrf2'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('sv_clrf2')
    rom.JP('end_frame')

    # ── State: MAIN MENU (IP-1040) ────────────────────────
    # D-pad up/down toggles the highlighted option (only when a valid save
    # exists — MM_SAVE_VALID, computed once per entry by mm_on_entry); A
    # confirms. "Continue" (cursor=0) calls the existing try_load_save,
    # which sets GAMESTATE/TRANSITION_TO/NEED_REDRAW itself. "New game"
    # (cursor=1) resets SEED/SCALE ENTRY's fields to defaults and enters it.
    rom.label('st_main_menu')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()
    rom.BIT_b_B(J_UP); rom.JR_NZ('mm_toggle')
    rom.BIT_b_B(J_DOWN); rom.JP_Z('mm_check_a')
    rom.label('mm_toggle')
    rom.LD_A_nn(MM_SAVE_VALID); rom.OR_A(); rom.JP_Z('mm_check_a')
    rom.LD_A_nn(MM_CURSOR); rom.XOR_n(1); rom.LD_nn_A(MM_CURSOR)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('mm_check_a')
    rom.LD_A_nn(JOY_NEW); rom.AND_n(1 << J_A)
    rom.JP_Z('end_frame')
    rom.LD_A_nn(MM_CURSOR); rom.OR_A(); rom.JP_NZ('mm_newgame')
    rom.CALL('try_load_save')
    rom.JP('end_frame')
    rom.label('mm_newgame')
    rom.LD_HL_nn(SSE_DIGITS); rom.LD_B_n(5); rom.XOR_A()
    rom.label('mm_ng_clr'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('mm_ng_clr')
    rom.LD_A_n(3); rom.LD_nn_A(SSE_SCALE)   # default scale (ADR-0010)
    rom.XOR_A(); rom.LD_nn_A(SSE_CURSOR)
    # IP-1100 (GDS-01 §4d): "new game" now opens MODE SELECT, not SEED/SCALE
    # ENTRY directly. GAME_MODE is explicitly reset to 0 (finite) here, on
    # every "new game" entry -- a defensive fix caught during implementation:
    # without it, a player who picks "infinite" at MODE SELECT (setting
    # GAME_MODE=1), then B-cancels all the way back to MAIN MENU, then
    # starts a fresh "new game" and picks "finite" this time, would have
    # GAME_MODE still stuck at 1 (st_mode_select's own "finite" branch,
    # mirroring GDS-01 §4d's diagram, does not itself write GAME_MODE) --
    # silently routing an intended finite-mode game through IP-1102's
    # infinite-mode dsr_p/check_zone_transition paths. Resetting here, once,
    # at the single genuine "new game" entry point, is the simplest correct
    # fix -- st_mode_select's own "infinite" branch is still the only place
    # that ever sets GAME_MODE=1.
    rom.XOR_A(); rom.LD_nn_A(GAME_MODE)
    rom.LD_A_n(GS_MODE_SELECT); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.JP('end_frame')

    # ── State: SEED/SCALE ENTRY (IP-1040) ─────────────────
    # Digit-cursor picker (ADR-0010): left/right moves SSE_CURSOR (0-4 = the
    # 5 seed digits MSB-first, 5 = scale); up/down adjusts the value at the
    # cursor (wrapping); B cancels back to MAIN MENU without writing SEED/
    # WORLD_SCALE (FS-104 Open Question 1); A composes the digits into the
    # real 16-bit SEED (saturating), writes WORLD_SCALE, calls IP-1020's
    # generate_world, and transitions to INTRO.
    rom.label('st_seed_scale_entry')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()

    rom.BIT_b_B(J_B); rom.JP_Z('sse_no_b')
    rom.LD_A_n(GS_MAIN_MENU); rom.LD_nn_A(TRANSITION_TO)
    # IP-9060: also a genuine GAMESTATE -> GS_MAIN_MENU entry site (T18.c's
    # own regression path) — not named in IP-9060's own §6 task list, but
    # required for MM_CURSOR to reset correctly here too; caught during
    # implementation, not silently left as a 4th unguarded entry point.
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.JP('end_frame')
    rom.label('sse_no_b')

    rom.BIT_b_B(J_LEFT); rom.JP_Z('sse_no_left')
    rom.LD_A_nn(SSE_CURSOR); rom.OR_A(); rom.JP_Z('sse_redraw')
    rom.DEC_A(); rom.LD_nn_A(SSE_CURSOR)
    rom.JP('sse_redraw')
    rom.label('sse_no_left')

    rom.BIT_b_B(J_RIGHT); rom.JP_Z('sse_no_right')
    rom.LD_A_nn(SSE_CURSOR); rom.CP_n(5); rom.JP_NC('sse_redraw')
    rom.INC_A(); rom.LD_nn_A(SSE_CURSOR)
    rom.JP('sse_redraw')
    rom.label('sse_no_right')

    rom.BIT_b_B(J_UP); rom.JP_Z('sse_no_up')
    rom.CALL('sse_adjust_up')
    rom.JP('sse_redraw')
    rom.label('sse_no_up')

    rom.BIT_b_B(J_DOWN); rom.JP_Z('sse_no_down')
    rom.CALL('sse_adjust_down')
    rom.JP('sse_redraw')
    rom.label('sse_no_down')

    rom.LD_A_nn(JOY_NEW); rom.AND_n(1 << J_A)
    rom.JP_Z('end_frame')
    rom.CALL('sse_compose_seed')
    # clear KEYITEM_FLAGS (81 bytes) before generation writes its own
    # present/collected/absent pattern — clears any prior playthrough's bytes
    # beyond this world's region count (IP-1020/BL-0063's original intent),
    # without clobbering generate_world's own output the way clearing it in
    # st_intro (which runs after this call) used to (IP-1021 fix)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.LD_B_n(81); rom.XOR_A()
    rom.label('sse_ki_clr'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('sse_ki_clr')
    rom.CALL('generate_world')
    rom.LD_A_n(GS_INTRO); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    rom.label('sse_redraw')
    rom.CALL('draw_sse_digits')
    rom.JP('end_frame')

    # ── State: MODE SELECT (IP-1100, GDS-01 §4d) ──────────
    # D-pad up/down toggles MM_CURSOR unconditionally between 0 ("finite")
    # and 1 ("infinite") -- both options always offered, mirrors
    # st_select_menu's own unconditional toggle exactly (no MM_SAVE_VALID-
    # style gate needed here). A confirms: "finite" -> GS_SEED_SCALE_ENTRY,
    # completely unchanged (GAME_MODE already reset to 0 at mm_newgame,
    # not touched again here); "infinite" -> GS_INFINITE_SEED_ENTRY, writing
    # GAME_MODE=1 on this transition only, not on mere highlight. B cancels
    # directly to MAIN MENU, writing nothing (the named asymmetric-tradeoff
    # counterpart is SEED/SCALE ENTRY's own unchanged B-cancel target,
    # GDS-01 §4d's own explicit framing -- not this state).
    rom.label('st_mode_select')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()
    rom.BIT_b_B(J_UP); rom.JR_NZ('ms_toggle')
    rom.BIT_b_B(J_DOWN); rom.JP_Z('ms_check_b')
    rom.label('ms_toggle')
    rom.LD_A_nn(MM_CURSOR); rom.XOR_n(1); rom.LD_nn_A(MM_CURSOR)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('ms_check_b')
    rom.BIT_b_B(J_B); rom.JR_Z('ms_check_a')
    rom.LD_A_n(GS_MAIN_MENU); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.JP('end_frame')
    rom.label('ms_check_a')
    rom.BIT_b_B(J_A); rom.JP_Z('end_frame')
    rom.LD_A_nn(MM_CURSOR); rom.OR_A(); rom.JR_NZ('ms_infinite')
    rom.LD_A_n(GS_SEED_SCALE_ENTRY); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('ms_infinite')
    rom.LD_A_n(1); rom.LD_nn_A(GAME_MODE)
    rom.LD_A_n(GS_INFINITE_SEED_ENTRY); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: INFINITE SEED ENTRY (IP-1100, GDS-01 §4d) ──
    # Reuses SEED/SCALE ENTRY's own digit-cursor picker convention
    # (ADR-0010) over the same SSE_DIGITS/SSE_CURSOR bytes -- safe since
    # GS_SEED_SCALE_ENTRY and GS_INFINITE_SEED_ENTRY are never
    # simultaneously active (mirrors MM_CURSOR's own established reuse
    # precedent, IP-1090). LEFT/RIGHT are bounded to cursor 0-4 only (never
    # 5, the finite mode's own scale slot -- there is no scale digit here);
    # UP/DOWN reuse sse_adjust_up/sse_adjust_down verbatim (their own
    # CP_n(5) scale branch never triggers, since cursor never reaches 5
    # from this state). A composes the seed via sse_compose_seed (IP-1040,
    # reused verbatim -- it also writes WORLD_SCALE from SSE_SCALE's
    # leftover value, harmless here since no Infinite Mode code path ever
    # reads WORLD_SCALE), sets INF_ROW=INF_COL=0, then calls IP-1102's own
    # inf_ensure_window (not a single direct inf_materialize_region call --
    # a deliberate deviation from this package's own original §6 text,
    # which predates IP-1102's existence: inf_ensure_window populates the
    # full 3x3 INF_WINDOW correctly in one call, reusing IP-1102's already-
    # built routine instead of duplicating its 9-cell logic here, and avoids
    # leaving INF_WINDOW's 8 non-center cells as uninitialized WRAM --
    # GAME_MODE's own identical boot-clear-gap lesson from IP-1102, applied
    # proactively here rather than rediscovered the same way). B cancels to
    # GS_MODE_SELECT (not GS_MAIN_MENU -- this state has no shipped
    # precedent to protect, GDS-01 §4d's own "one step back" framing),
    # writing nothing -- MM_JUST_ENTERED is deliberately NOT set on this
    # transition, so MODE SELECT's own cursor stays on "infinite" (whatever
    # is normal, given B-cancel only happens after choosing it), letting the
    # player retry immediately rather than resetting back to "finite".
    rom.label('st_infinite_seed_entry')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()

    rom.BIT_b_B(J_B); rom.JP_Z('ise_no_b')
    rom.LD_A_n(GS_MODE_SELECT); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('ise_no_b')

    rom.BIT_b_B(J_LEFT); rom.JP_Z('ise_no_left')
    rom.LD_A_nn(SSE_CURSOR); rom.OR_A(); rom.JP_Z('ise_redraw')
    rom.DEC_A(); rom.LD_nn_A(SSE_CURSOR)
    rom.JP('ise_redraw')
    rom.label('ise_no_left')

    rom.BIT_b_B(J_RIGHT); rom.JP_Z('ise_no_right')
    rom.LD_A_nn(SSE_CURSOR); rom.CP_n(4); rom.JP_NC('ise_redraw')
    rom.INC_A(); rom.LD_nn_A(SSE_CURSOR)
    rom.JP('ise_redraw')
    rom.label('ise_no_right')

    rom.BIT_b_B(J_UP); rom.JP_Z('ise_no_up')
    rom.CALL('sse_adjust_up')
    rom.JP('ise_redraw')
    rom.label('ise_no_up')

    rom.BIT_b_B(J_DOWN); rom.JP_Z('ise_no_down')
    rom.CALL('sse_adjust_down')
    rom.JP('ise_redraw')
    rom.label('ise_no_down')

    rom.LD_A_nn(JOY_NEW); rom.AND_n(1 << J_A)
    rom.JP_Z('end_frame')
    rom.CALL('sse_compose_seed')
    rom.XOR_A()
    rom.LD_nn_A(INF_ROW); rom.LD_nn_A(INF_ROW + 1)
    rom.LD_nn_A(INF_COL); rom.LD_nn_A(INF_COL + 1)
    rom.CALL('inf_ensure_window')
    rom.LD_A_n(GS_INTRO); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    rom.label('ise_redraw')
    rom.CALL('draw_ise_digits')
    rom.JP('end_frame')

    # ── State: SELECT MENU (IP-1090) ──────────────────────
    # D-pad up/down toggles MM_CURSOR unconditionally between 0 ("map")
    # and 1 ("legend") -- both options are always offered, unlike MAIN
    # MENU's conditional "continue". A confirms the highlighted option;
    # B cancels straight back to PLAYING, writing nothing else (FR-1200).
    # SELECT itself is not tested here -- a plain no-op if pressed again.
    rom.label('st_select_menu')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()
    rom.BIT_b_B(J_UP); rom.JR_NZ('sm_toggle')
    rom.BIT_b_B(J_DOWN); rom.JP_Z('sm_check_b')
    rom.label('sm_toggle')
    rom.LD_A_nn(MM_CURSOR); rom.XOR_n(1); rom.LD_nn_A(MM_CURSOR)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('sm_check_b')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()
    rom.BIT_b_B(J_B); rom.JR_Z('sm_check_a')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('sm_check_a')
    rom.BIT_b_B(J_A); rom.JP_Z('end_frame')
    rom.LD_A_nn(MM_CURSOR); rom.OR_A(); rom.JP_NZ('sm_legend')
    rom.LD_A_n(GS_MAP); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('sm_legend')
    rom.LD_A_n(GS_LEGEND); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: LEGEND (IP-1090) ────────────────────────────
    # Single static screen (GDS-08 §11) -- only B is tested; SELECT is a
    # plain no-op here too, same resolution as SELECT MENU.
    rom.label('st_legend')
    rom.LD_A_nn(JOY_NEW); rom.AND_n(1 << J_B)
    rom.JP_Z('end_frame')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── End of frame ─────────────────────────────────────
    rom.label('end_frame')
    rom.CALL('update_oam')
    rom.CALL('do_dma')
    rom.CALL('music_tick')
    rom.JP('game_loop')

    # ====================================================
    # SUBROUTINES
    # ====================================================

    rom.label('memcpy')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('memcpy')
    rom.RET()

    rom.label('do_dma')
    rom.LD_A_n(OAM_BUF >> 8); rom.LDH_n_A(DMA)
    rom.CALL(HRAM_DMA); rom.RET()

    # ── read_joypad ───────────────────────────────────────
    rom.label('read_joypad')
    rom.LD_A_nn(JOY_CUR); rom.LD_nn_A(JOY_PREV)

    rom.LD_A_n(0x10); rom.LDH_n_A(P1)
    rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1)
    rom.AND_n(0x0F); rom.LD_B_A()

    rom.LD_A_n(0x20); rom.LDH_n_A(P1)
    rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1)
    rom.AND_n(0x0F); rom.SWAP_A()
    rom.OR_B()
    rom.CPL()
    rom.LD_nn_A(JOY_CUR)

    rom.LD_A_n(0x30); rom.LDH_n_A(P1)

    rom.LD_A_nn(JOY_PREV); rom.CPL(); rom.LD_B_A()
    rom.LD_A_nn(JOY_CUR);  rom.AND_B()
    rom.LD_nn_A(JOY_NEW)
    rom.RET()

    # ── handle_play_input ────────────────────────────────
    rom.label('handle_play_input')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()

    rom.BIT_b_B(J_START); rom.JR_Z('hpi_no_st')
    rom.LD_A_n(GS_SAVE); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()
    rom.label('hpi_no_st')

    rom.BIT_b_B(J_SELECT); rom.JR_Z('hpi_no_sel')
    # IP-1090: SELECT now opens SELECT MENU (map/legend cursor choice)
    # instead of jumping directly to MAP (GDS-01 §4c). MM_JUST_ENTERED
    # set here so MM_CURSOR resets to "map" (0) on this genuine entry,
    # mirroring st_save's own exit-to-main-menu site.
    rom.LD_A_n(GS_SELECT_MENU); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.RET()
    rom.label('hpi_no_sel')

    rom.LD_A_nn(JOY_CUR); rom.LD_B_A()
    rom.XOR_A(); rom.LD_nn_A(TMP1)

    # RIGHT
    rom.BIT_b_B(J_RIGHT); rom.JR_Z('mv_nr')
    rom.LD_A_nn(PLAYER_X); rom.INC_A()
    rom.CP_n(153); rom.JR_NC('mv_skip_r')
    rom.LD_nn_A(PLAYER_X)
    rom.label('mv_skip_r')
    rom.XOR_A(); rom.LD_nn_A(PLAYER_DIR)
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nr')

    # LEFT
    rom.BIT_b_B(J_LEFT); rom.JR_Z('mv_nl')
    rom.LD_A_nn(PLAYER_X); rom.OR_A(); rom.JR_Z('mv_nl')
    rom.DEC_A(); rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(1); rom.LD_nn_A(PLAYER_DIR)
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nl')

    # UP
    rom.BIT_b_B(J_UP); rom.JR_Z('mv_nu')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(8); rom.JR_C('mv_skip_u')
    rom.JR_Z('mv_skip_u'); rom.DEC_A(); rom.LD_nn_A(PLAYER_Y)
    rom.label('mv_skip_u')
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nu')

    # DOWN
    rom.BIT_b_B(J_DOWN); rom.JR_Z('mv_nd')
    rom.LD_A_nn(PLAYER_Y); rom.INC_A()
    rom.CP_n(129); rom.JR_NC('mv_skip_d')
    rom.LD_nn_A(PLAYER_Y)
    rom.label('mv_skip_d')
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nd')

    rom.LD_A_nn(TMP1); rom.OR_A(); rom.JR_Z('mv_done')
    rom.LD_A_nn(ANIM_CTR); rom.INC_A()
    rom.CP_n(10); rom.JR_C('mv_save')
    rom.XOR_A(); rom.LD_nn_A(ANIM_CTR)
    rom.LD_A_nn(PLAYER_FRAME); rom.XOR_n(1); rom.LD_nn_A(PLAYER_FRAME)
    rom.RET()
    rom.label('mv_save'); rom.LD_nn_A(ANIM_CTR)
    rom.label('mv_done'); rom.RET()

    # ── check_collisions ─────────────────────────────────
    rom.label('check_collisions')
    rom.LD_A_nn(COLL_COUNT); rom.OR_A(); rom.RET_Z()
    rom.LD_B_A()
    rom.LD_HL_nn(COLL_DATA)

    rom.label('cc_loop')
    rom.LD_E_HL(); rom.INC_HL()        # E = x
    rom.LD_D_HL(); rom.INC_HL()        # D = y
    rom.LD_C_HL(); rom.INC_HL()        # C = type
    rom.LD_A_HL()                       # A = active
    rom.PUSH_BC(); rom.PUSH_HL()
    rom.OR_A(); rom.JR_Z('cc_skip')

    # Item point (E=item_x) falls within the player's real 8x16 box:
    # 0 <= (item_x - PLAYER_X) <= 7, computed as one unsigned subtract +
    # compare (item_x < PLAYER_X wraps to a large unsigned value, correctly
    # failing the CP_n(8)/JR_NC check the same as "too far right"). Uses H
    # as scratch (not B/C — B is the live loop counter re-read at cc_loop's
    # own COLL_COUNT-B arithmetic below, C is the item's own type, read
    # again at the HIT branch below — both must survive this block; H is
    # free here, HL's real value already stashed by this iteration's own
    # PUSH_HL, not touched again until cc_skip/the HIT branch's POP_HL).
    rom.LD_A_nn(PLAYER_X); rom.LD_H_A()
    rom.LD_A_E(); rom.emit(0x94)          # SUB H
    rom.CP_n(8); rom.JR_NC('cc_skip')

    # Same test on Y: 0 <= (item_y - PLAYER_Y) <= 15 (D=item_y)
    rom.LD_A_nn(PLAYER_Y); rom.LD_H_A()
    rom.LD_A_D(); rom.emit(0x94)          # SUB H
    rom.CP_n(16); rom.JR_NC('cc_skip')

    # HIT — deactivate
    rom.POP_HL(); rom.XOR_A(); rom.LD_HL_A(); rom.INC_HL()

    # IP-1103: Infinite Mode treasure branch, parallel to the KeyItem/
    # ScoreItem branches below (FR-10300) -- those branches' own code is
    # unchanged and now runs only when GAME_MODE == 0, so no finite-mode
    # counter (KEYITEM_COUNT/SCORE/flags) is ever touched by an Infinite
    # Mode pickup and check_complete's finite victory check cannot
    # spuriously fire there (IP-1100 §6's named hazard). Handler body lives
    # past cc_skip (cc_inf_hit) to keep this shared HIT path short.
    rom.LD_A_nn(GAME_MODE); rom.OR_A(); rom.JP_NZ('cc_inf_hit')

    # If KeyItem (type 2): set KEYITEM_FLAGS[CUR_ZONE] = 1 + INC KEYITEM_COUNT
    # (IP-1020: generalizes the carrot branch — same bit-set logic, same
    # push/pop-HL discipline, only the target array/counter names change)
    rom.LD_A_C(); rom.CP_n(2); rom.JR_NZ('cc_not_c')
    rom.LD_A_nn(CUR_ZONE)
    rom.PUSH_HL()
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.ADD_HL_DE()
    rom.LD_A_n(1); rom.LD_HL_A()
    rom.POP_HL()
    rom.LD_A_nn(KEYITEM_COUNT); rom.INC_A(); rom.LD_nn_A(KEYITEM_COUNT)
    rom.JR('cc_dirty')
    rom.label('cc_not_c')

    # Star/flower → SCORE++
    rom.LD_A_nn(SCORE); rom.INC_A()
    rom.CP_n(100); rom.JR_C('cc_so'); rom.LD_A_n(99)
    rom.label('cc_so'); rom.LD_nn_A(SCORE)

    # FR-5220: set bit k = COLL_COUNT-B (B still live from this iteration's
    # PUSH_BC, pre-decrement) in SCOREITEM_FLAGS[CUR_ZONE], mirroring the
    # carrot branch's push/pop-HL scratch-register discipline.
    rom.LD_A_nn(COLL_COUNT); rom.SUB_B()
    rom.LD_C_A()
    rom.LD_B_n(1)
    rom.label('cc_si_mkloop')
    rom.LD_A_C(); rom.OR_A(); rom.JR_Z('cc_si_mkdone')
    rom.SLA_B(); rom.DEC_C(); rom.JR('cc_si_mkloop')
    rom.label('cc_si_mkdone')
    rom.PUSH_HL()
    rom.LD_A_nn(CUR_ZONE); rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(SCOREITEM_FLAGS); rom.ADD_HL_DE()
    rom.LD_A_HL(); rom.OR_B(); rom.LD_HL_A()
    rom.POP_HL()

    rom.label('cc_dirty')
    rom.LD_A_n(1); rom.LD_nn_A(SCORE_DIRTY)

    rom.label('cc_iter')
    rom.POP_BC(); rom.DEC_B(); rom.JP_NZ('cc_loop'); rom.RET()

    rom.label('cc_skip')
    rom.POP_HL(); rom.INC_HL()
    rom.POP_BC(); rom.DEC_B(); rom.JP_NZ('cc_loop'); rom.RET()

    # IP-1103: Infinite Mode treasure collection (FR-10300, collection-event
    # half -- the presence-predicate half is IP-1101's, consumed via the
    # INF_TREASURE_HERE cache). Item already deactivated by the shared HIT
    # code above (update_oam hides it next frame). SCORE_DIRTY deliberately
    # not set: no HUD field this routine owns changes.
    rom.label('cc_inf_hit')
    # Gated on INF_TREASURE_HERE != 0 (IP-1103 §5/§6). Defensive: the spawn
    # branch (szc_infinite) only creates an item while the cache is set, so
    # a hit with a cleared cache should be unreachable -- treated as
    # no-collect rather than counting a phantom treasure.
    rom.LD_A_nn(INF_TREASURE_HERE); rom.OR_A(); rom.JR_Z('cc_iter')
    # RUNNING_TREASURE_COUNT += 1: 16-bit, INC low byte, INC high byte only
    # on wrap (Z). No overflow guard at 0xFFFF (IP-1103 §6: an indefinitely-
    # resumable run reaching 65536 treasures is not a realistic scenario).
    rom.LD_A_nn(RUNNING_TREASURE_COUNT); rom.INC_A()
    rom.LD_nn_A(RUNNING_TREASURE_COUNT)
    rom.JR_NZ('cc_inf_nc')
    rom.LD_A_nn(RUNNING_TREASURE_COUNT + 1); rom.INC_A()
    rom.LD_nn_A(RUNNING_TREASURE_COUNT + 1)
    rom.label('cc_inf_nc')
    # Collected: not re-collectible this materialization (re-entry re-derives
    # the cache; collected-state across re-entry is IP-1104's ledger's scope).
    rom.XOR_A(); rom.LD_nn_A(INF_TREASURE_HERE)
    # Mark the current region collected -- IP-1104's own ledger-write
    # interface: the forward call IP-1103 names, IP-1104 implements the
    # receiving end of (a RET stub until then, see inf_ledger_mark_collected).
    rom.CALL('inf_ledger_mark_collected')
    rom.JR('cc_iter')

    # ── check_zone_transition ────────────────────────────
    # czt_region_hl: HL = REGION_GRAPH + CUR_ZONE*5 (region base, biome-id
    # byte) — the identical addressing dsr_p/draw_region_arrows (IP-1030)
    # already perform, correct up to scale=9's 81 regions. check_zone_
    # transition's 4 branches each add the fixed GDS-07 §6 offset for their
    # own direction (+1 up, +2 down, +3 left, +4 right) after calling this.
    rom.label('czt_region_hl')
    rom.LD_A_nn(CUR_ZONE)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(REGION_GRAPH)
    rom.ADD_HL_DE(); rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.RET()

    # IP-9050 (BL-0047): regeneralized from the pre-procgen hardcoded
    # fixed-3x3 CUR_ZONE arithmetic to REGION_GRAPH neighbor-byte reads —
    # 0xFF = no neighbor in that direction (blocked, clamp at the edge),
    # otherwise the neighbor byte's own value is the new CUR_ZONE directly
    # (no arithmetic). The branch-cascade control flow (right-blocked falls
    # through to check the vertical edges; left/top/bottom-blocked RET
    # immediately) is unchanged from the pre-fix shipped code (T17.b's own
    # scale=3 regression requires bit-for-bit identical behavior there).
    rom.label('check_zone_transition')
    # IP-1102: GAME_MODE-gated entry -- the four finite-mode branches below
    # (right/left/top/bottom) are reached only when GAME_MODE == 0, entirely
    # unchanged; Infinite Mode has its own parallel czt_infinite handler
    # (below czt_redraw), since CUR_ZONE/REGION_GRAPH don't apply to it.
    rom.LD_A_nn(GAME_MODE); rom.OR_A(); rom.JR_Z('czt_finite_start')
    rom.JP('czt_infinite')
    rom.label('czt_finite_start')
    # right edge: x >= 152 (matches handle_play_input's own RIGHT clamp
    # ceiling exactly -- IP-9090's corrected clamp (max X=152) fell below
    # this threshold's old value of 156, making the RIGHT transition
    # unreachable through normal play; fixed here, IP-9120/BL-0076)
    # -- gated on RIGHT actually being held (IP-9130/BL-0078): the
    # position test alone is not enough, since PLAYER_X persists across a
    # transition on the OTHER axis -- entering a new region via DOWN/UP
    # while still sitting at the RIGHT clamp ceiling from an earlier walk
    # must not spuriously fire RIGHT here just because that new region
    # happens to have an open right neighbor.
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_RIGHT); rom.JR_Z('czt_left')
    rom.LD_A_nn(PLAYER_X); rom.CP_n(152); rom.JR_C('czt_left')
    rom.CALL('czt_region_hl')
    rom.INC_HL(); rom.INC_HL(); rom.INC_HL(); rom.INC_HL()   # HL -> +4 (right)
    rom.LD_A_HL(); rom.CP_n(0xFF); rom.JR_Z('czt_left')
    rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(8); rom.LD_nn_A(PLAYER_X)
    rom.JP('czt_redraw')

    rom.label('czt_left')
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_LEFT); rom.JR_Z('czt_top')
    rom.LD_A_nn(PLAYER_X); rom.OR_A(); rom.JR_NZ('czt_top')
    rom.CALL('czt_region_hl')
    rom.INC_HL(); rom.INC_HL(); rom.INC_HL()   # HL -> +3 (left)
    rom.LD_A_HL(); rom.CP_n(0xFF); rom.RET_Z()
    rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(150); rom.LD_nn_A(PLAYER_X)
    rom.JP('czt_redraw')

    rom.label('czt_top')
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_UP); rom.JR_Z('czt_bot')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(18); rom.JR_NC('czt_bot')
    rom.CALL('czt_region_hl')
    rom.INC_HL()   # HL -> +1 (up)
    rom.LD_A_HL(); rom.CP_n(0xFF); rom.RET_Z()
    rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(120); rom.LD_nn_A(PLAYER_Y)
    rom.JP('czt_redraw')

    rom.label('czt_bot')
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_DOWN); rom.RET_Z()
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(128); rom.RET_C()
    rom.CALL('czt_region_hl')
    rom.INC_HL(); rom.INC_HL()   # HL -> +2 (down)
    rom.LD_A_HL(); rom.CP_n(0xFF); rom.RET_Z()
    rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(24); rom.LD_nn_A(PLAYER_Y)

    rom.label('czt_redraw')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    # ── inf_ensure_window (IP-1102) ────────────────────────
    # Recomputes the entire 3x3 materialized window around INF_ROW/INF_COL
    # by calling IP-1101's inf_materialize_region for each of the 9 cells --
    # no incremental shift logic (the routine is cheap and pure, so a full
    # recompute on every center change is simpler and avoids a sliding-
    # window management scheme entirely, per the TWBS's own framing).
    # Window layout: row-major, index = (dr+1)*3+(dc+1) for dr,dc in
    # {-1,0,1}; index 4 (dr=0,dc=0) is always the current region. Assembled
    # unrolled at Python-assembly-time (9 fixed cells, no runtime loop) --
    # matches this codebase's own established style for small fixed counts.
    _INF_WINDOW_OFFSETS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)]
    rom.label('inf_ensure_window')
    for _idx, (_dr, _dc) in enumerate(_INF_WINDOW_OFFSETS):
        rom.LD_A_nn(INF_ROW); rom.LD_E_A()
        rom.LD_A_nn(INF_ROW + 1); rom.LD_D_A()
        if _dr == 1: rom.INC_DE()
        elif _dr == -1: rom.DEC_DE()
        rom.LD_A_E(); rom.LD_nn_A(INF_MZ_ROW)
        rom.LD_A_D(); rom.LD_nn_A(INF_MZ_ROW + 1)
        rom.LD_A_nn(INF_COL); rom.LD_E_A()
        rom.LD_A_nn(INF_COL + 1); rom.LD_D_A()
        if _dc == 1: rom.INC_DE()
        elif _dc == -1: rom.DEC_DE()
        rom.LD_A_E(); rom.LD_nn_A(INF_MZ_COL)
        rom.LD_A_D(); rom.LD_nn_A(INF_MZ_COL + 1)
        rom.CALL('inf_materialize_region')
        rom.LD_A_nn(INF_MZ_RESULT)
        rom.LD_nn_A(INF_WINDOW + _idx)
        if _idx == 4:
            # IP-1103: cache the center (= current) region's treasure-presence
            # flag -- inf_materialize_region leaves it in INF_MZ_TREASURE, and
            # every window recompute recenters on the current region, so the
            # center cell's own materialization is exactly the "at the moment a
            # region is materialized" evaluation FS-110 Workflow C step 1 names.
            # Cleared on collection (check_collisions); re-derived on every
            # re-entry.
            rom.LD_A_nn(INF_MZ_TREASURE)
            rom.LD_nn_A(INF_TREASURE_HERE)
            # IP-1104 (BL-0119): cross-reference the visited-region ledger --
            # if this region is already marked collected there, override the
            # fresh presence-predicate write above to 0, regardless of what it
            # says. INF_ROW/INF_COL already hold this center region's own
            # coordinates at this point (every call site updates them before
            # calling inf_ensure_window), matching inf_ledger_find's own
            # contract exactly. This one cross-reference is what closes the
            # mid-session respawn gap uniformly -- inf_ensure_window is the
            # only call site that ever writes INF_TREASURE_HERE, reached from
            # new-game entry, ordinary navigation, and post-load restore
            # alike, so fixing it once here fixes every call site.
            rom.CALL('inf_ledger_find')
            rom.JR_NZ('iew_no_ledger_hit')
            rom.LD_A_HL(); rom.OR_A(); rom.JR_Z('iew_no_ledger_hit')
            rom.XOR_A(); rom.LD_nn_A(INF_TREASURE_HERE)
            rom.label('iew_no_ledger_hit')
    rom.RET()

    # ── czt_infinite (IP-1102) ─────────────────────────────
    # Infinite Mode's own transition handler -- mirrors check_zone_
    # transition's finite-mode branch cascade (same JOY_CUR-gated intent
    # check per direction, IP-9130/BL-0078's own convention, reused
    # verbatim; same player-position reset constants) but tests the current
    # region's own connectivity nibble (INF_WINDOW's center cell, bits 3-6)
    # instead of a REGION_GRAPH neighbor byte, and updates INF_ROW/INF_COL
    # instead of CUR_ZONE -- there is no bounded grid, so no "0xFF = grid
    # edge" concept applies here (Infinite Mode's world is unbounded).
    rom.label('czt_infinite')
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_RIGHT); rom.JR_Z('czti_left')
    rom.LD_A_nn(PLAYER_X); rom.CP_n(152); rom.JR_C('czti_left')
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(6); rom.JR_Z('czti_left')   # east
    rom.LD_A_nn(INF_COL); rom.LD_E_A(); rom.LD_A_nn(INF_COL + 1); rom.LD_D_A()
    rom.INC_DE()
    rom.LD_A_E(); rom.LD_nn_A(INF_COL); rom.LD_A_D(); rom.LD_nn_A(INF_COL + 1)
    rom.CALL('inf_ensure_window')
    rom.LD_A_n(8); rom.LD_nn_A(PLAYER_X)
    rom.JP('czt_redraw')

    rom.label('czti_left')
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_LEFT); rom.JR_Z('czti_top')
    rom.LD_A_nn(PLAYER_X); rom.OR_A(); rom.JR_NZ('czti_top')
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(5); rom.JR_Z('czti_top')    # west
    rom.LD_A_nn(INF_COL); rom.LD_E_A(); rom.LD_A_nn(INF_COL + 1); rom.LD_D_A()
    rom.DEC_DE()
    rom.LD_A_E(); rom.LD_nn_A(INF_COL); rom.LD_A_D(); rom.LD_nn_A(INF_COL + 1)
    rom.CALL('inf_ensure_window')
    rom.LD_A_n(150); rom.LD_nn_A(PLAYER_X)
    rom.JP('czt_redraw')

    rom.label('czti_top')
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_UP); rom.JR_Z('czti_bot')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(18); rom.JR_NC('czti_bot')
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(3); rom.JR_Z('czti_bot')    # north
    rom.LD_A_nn(INF_ROW); rom.LD_E_A(); rom.LD_A_nn(INF_ROW + 1); rom.LD_D_A()
    rom.DEC_DE()
    rom.LD_A_E(); rom.LD_nn_A(INF_ROW); rom.LD_A_D(); rom.LD_nn_A(INF_ROW + 1)
    rom.CALL('inf_ensure_window')
    rom.LD_A_n(120); rom.LD_nn_A(PLAYER_Y)
    rom.JP('czt_redraw')

    rom.label('czti_bot')
    rom.LD_A_nn(JOY_CUR); rom.BIT_b_A(J_DOWN); rom.RET_Z()
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(128); rom.RET_C()
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(4); rom.RET_Z()             # south
    rom.LD_A_nn(INF_ROW); rom.LD_E_A(); rom.LD_A_nn(INF_ROW + 1); rom.LD_D_A()
    rom.INC_DE()
    rom.LD_A_E(); rom.LD_nn_A(INF_ROW); rom.LD_A_D(); rom.LD_nn_A(INF_ROW + 1)
    rom.CALL('inf_ensure_window')
    rom.LD_A_n(24); rom.LD_nn_A(PLAYER_Y)
    rom.JP('czt_redraw')

    # ── check_complete ───────────────────────────────────
    rom.label('check_complete')
    # IP-1021 (FR-9161/ADR-0015): victory threshold is now WORLD_SCALE, read at
    # runtime -- not a hardcoded 9 -- since KeyItem placement is now scale-
    # relative (FR-9160), not one-per-region.
    rom.LD_A_nn(WORLD_SCALE); rom.LD_B_A()
    rom.LD_A_nn(CARROTS_COUNT); rom.CP_B(); rom.RET_NZ()
    rom.LD_A_n(GS_VICTORY); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    # ── update_oam ───────────────────────────────────────
    rom.label('update_oam')
    rom.LD_HL_nn(OAM_BUF); rom.LD_B_n(160); rom.XOR_A()
    rom.label('uo_clr'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('uo_clr')

    rom.LD_A_nn(GAMESTATE); rom.CP_n(GS_PLAYING); rom.RET_NZ()

    # Bunny — single 8x16 OBJ (tile pair = head + body, frame * 2)
    rom.LD_HL_nn(OAM_BUF)
    rom.LD_A_nn(PLAYER_Y); rom.ADD_A_n(16); rom.LD_HLI_A()    # OAM Y
    rom.LD_A_nn(PLAYER_X); rom.ADD_A_n(8);  rom.LD_HLI_A()    # OAM X
    rom.LD_A_nn(PLAYER_FRAME); rom.ADD_A_A(); rom.LD_HLI_A()  # tile (0 or 2)
    rom.LD_A_nn(PLAYER_DIR)
    rom.RRCA(); rom.RRCA(); rom.RRCA(); rom.AND_n(0x20)        # dir → x-flip
    rom.LD_HLI_A()                                              # attr (palette 0)

    # Collectibles
    rom.LD_A_nn(COLL_COUNT); rom.OR_A(); rom.RET_Z()
    rom.LD_B_A(); rom.LD_DE_nn(COLL_DATA)

    rom.label('uo_cl')
    rom.LD_A_DE(); rom.PUSH_AF(); rom.INC_DE()
    rom.LD_A_DE(); rom.PUSH_AF(); rom.INC_DE()
    rom.LD_A_DE(); rom.LD_C_A(); rom.INC_DE()
    rom.LD_A_DE(); rom.INC_DE()
    rom.OR_A(); rom.JR_Z('uo_hide')
    rom.POP_AF(); rom.ADD_A_n(16); rom.LD_HLI_A()
    rom.POP_AF(); rom.ADD_A_n(8);  rom.LD_HLI_A()
    # tile by type: 0→star, 1→flower, 2→carrot
    rom.LD_A_C()
    rom.OR_A();   rom.JR_NZ('uo_t1')
    rom.LD_A_n(TL_STAR);       rom.JR('uo_tw')
    rom.label('uo_t1'); rom.CP_n(1); rom.JR_NZ('uo_t2')
    rom.LD_A_n(TL_FLOWER_OBJ); rom.JR('uo_tw')
    rom.label('uo_t2'); rom.LD_A_n(TL_CARROT)
    rom.label('uo_tw'); rom.LD_HLI_A()
    rom.LD_A_C(); rom.ADD_A_n(1); rom.LD_HLI_A()   # palette = type+1
    rom.JR('uo_next')
    rom.label('uo_hide')
    rom.POP_AF(); rom.POP_AF()
    rom.XOR_A()
    rom.LD_HLI_A(); rom.LD_HLI_A(); rom.LD_HLI_A(); rom.LD_HLI_A()
    rom.label('uo_next')
    rom.DEC_B(); rom.JR_NZ('uo_cl'); rom.RET()

    # ── music_tick ───────────────────────────────────────
    rom.label('music_tick')
    rom.LD_A_nn(MUSIC_CTR); rom.DEC_A(); rom.LD_nn_A(MUSIC_CTR)
    rom.RET_NZ()
    rom.LD_A_nn(MUSIC_PTR_LO); rom.LD_L_A()
    rom.LD_A_nn(MUSIC_PTR_HI); rom.LD_H_A()
    rom.LD_A_HL(); rom.CP_n(0xFF); rom.JR_NZ('mt_play')
    rom.LD_HL_nn(0); patches['mus_reset'] = rom.pos - 2
    rom.label('mt_play')
    rom.LD_A_HLI(); rom.LDH_n_A(NR13)
    rom.LD_A_HLI(); rom.LDH_n_A(NR14)
    rom.LD_A_HLI(); rom.LD_nn_A(MUSIC_CTR)
    rom.LD_A_H(); rom.LD_nn_A(MUSIC_PTR_HI)
    rom.LD_A_L(); rom.LD_nn_A(MUSIC_PTR_LO)
    rom.RET()

    # ── update_status_disp ───────────────────────────────
    # During PLAYING: update carrots count digit + 3-digit score
    rom.label('update_status_disp')
    rom.LD_A_nn(GAMESTATE); rom.CP_n(GS_PLAYING); rom.RET_NZ()
    rom.LD_A_nn(SCORE_DIRTY); rom.OR_A(); rom.RET_Z()
    rom.XOR_A(); rom.LD_nn_A(SCORE_DIRTY)

    # carrot count digit at (col 2, row 0) → 0x9802
    rom.LD_A_nn(CARROTS_COUNT); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x9802); rom.LD_HL_A()

    # score digits at 0x9808-0x980A
    rom.LD_A_nn(SCORE); rom.LD_B_A()
    rom.LD_C_n(0)
    rom.label('usd_h')
    rom.LD_A_B(); rom.CP_n(100); rom.JR_C('usd_hd')
    rom.SUB_n(100); rom.LD_B_A(); rom.INC_C(); rom.JR('usd_h')
    rom.label('usd_hd')
    rom.LD_A_C(); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x9808); rom.LD_HL_A()

    rom.LD_C_n(0)
    rom.label('usd_t')
    rom.LD_A_B(); rom.CP_n(10); rom.JR_C('usd_td')
    rom.SUB_n(10); rom.LD_B_A(); rom.INC_C(); rom.JR('usd_t')
    rom.label('usd_td')
    rom.LD_A_C(); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x9809); rom.LD_HL_A()

    rom.LD_A_B(); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x980A); rom.LD_HL_A()
    rom.RET()

    # ── do_screen_redraw ──────────────────────────────────
    rom.label('do_screen_redraw')
    rom.label('dsr_wv')
    rom.LDH_A_n(LY); rom.CP_n(144); rom.JR_C('dsr_wv')
    rom.XOR_A(); rom.LDH_n_A(LCDC)

    rom.LD_A_nn(TRANSITION_TO); rom.LD_nn_A(GAMESTATE)
    rom.XOR_A(); rom.LD_nn_A(NEED_REDRAW)
    rom.LD_A_n(1); rom.LD_nn_A(SCORE_DIRTY)

    # When entering PLAYING, set up zone collectibles
    rom.LD_A_nn(GAMESTATE); rom.CP_n(GS_PLAYING); rom.JR_NZ('dsr_no_coll')
    rom.CALL('setup_zone_collects')
    rom.label('dsr_no_coll')

    # Dispatch to state-specific draw
    for gs, lbl in [(GS_TITLE,'dsr_t'),(GS_INTRO,'dsr_i'),(GS_PLAYING,'dsr_p'),
                    (GS_SAVE,'dsr_sv'),(GS_MAP,'dsr_m'),(GS_VICTORY,'dsr_v'),
                    (GS_MAIN_MENU,'dsr_mm'),(GS_SEED_SCALE_ENTRY,'dsr_sse'),
                    (GS_SELECT_MENU,'dsr_sm'),(GS_LEGEND,'dsr_lg'),
                    (GS_MODE_SELECT,'dsr_ms'),(GS_INFINITE_SEED_ENTRY,'dsr_ise')]:
        rom.LD_A_nn(GAMESTATE); rom.CP_n(gs); rom.JP_Z(lbl)
    rom.JP('dsr_done')

    def _dsr_screen(lbl, pt_key, ptas_key, extra=None):
        rom.label(lbl)
        rom.LD_DE_nn(0); patches[pt_key]  = rom.pos - 2
        rom.LD_BC_nn(0); patches[ptas_key] = rom.pos - 2
        rom.CALL('copy_screen')
        if extra:
            rom.CALL(extra)
        rom.JP('dsr_done')

    _dsr_screen('dsr_t',  'title_t',  'title_a')
    _dsr_screen('dsr_i',  'intro_t',  'intro_a')
    _dsr_screen('dsr_sv', 'save_t',   'save_a')
    _dsr_screen('dsr_v',  'vic_t',    'vic_a')
    _dsr_screen('dsr_m',  'map_t',    'map_a',  extra='update_map_hearts')
    # IP-1040: main menu recomputes save-validity + blanks "CONTINUE" if
    # absent + draws the cursor on every entry (mm_on_entry); seed/scale
    # entry redraws its digits + cursor on every entry (draw_sse_digits,
    # also called directly on every digit-cursor edit — see st_seed_scale_entry).
    _dsr_screen('dsr_mm',  'mm_t',  'mm_a',  extra='mm_on_entry')
    _dsr_screen('dsr_sse', 'sse_t', 'sse_a', extra='draw_sse_digits')
    # IP-1090: select menu draws/resets its own cursor on every entry
    # (sm_on_entry, mirroring mm_on_entry); legend is fully static -- no
    # per-entry logic needed, plain copy_screen suffices.
    _dsr_screen('dsr_sm', 'sm_t', 'sm_a', extra='sm_on_entry')
    _dsr_screen('dsr_lg', 'lg_t', 'lg_a')
    # IP-1100: mode select draws/resets its own cursor on every entry
    # (ms_on_entry, mirroring sm_on_entry); infinite seed entry redraws its
    # digits + cursor on every entry (draw_ise_digits, also called directly
    # on every digit-cursor edit — see st_infinite_seed_entry).
    _dsr_screen('dsr_ms',  'ms_t',  'ms_a',  extra='ms_on_entry')
    _dsr_screen('dsr_ise', 'ise_t', 'ise_a', extra='draw_ise_digits')

    # PLAYING: biome-family screen dispatch (IP-1030, generalizes the
    # former fixed 9-entry zs_table). CUR_ZONE is read as the current
    # region index into REGION_GRAPH (5 bytes/region: biome-id, then 4
    # neighbor-index bytes in up/down/left/right order — GDS-07 §6,
    # matching generate_world's own write order exactly).
    rom.label('dsr_p')
    # IP-1102: GAME_MODE-gated entry -- Infinite Mode has no REGION_GRAPH,
    # so it skips this read entirely and sources its biome-id from
    # INF_WINDOW's own center cell instead. The finite path below (from
    # LD_A_nn(CUR_ZONE) through the REGION_GRAPH read) is otherwise
    # byte-for-byte identical to the shipped code -- only this 3-instruction
    # gate precedes it.
    rom.LD_A_nn(GAME_MODE); rom.OR_A(); rom.JR_NZ('dsr_p_inf')
    rom.LD_A_nn(CUR_ZONE)
    rom.LD_E_A(); rom.LD_D_n(0)        # DE = region index
    rom.LD_HL_nn(REGION_GRAPH)
    rom.ADD_HL_DE(); rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.ADD_HL_DE(); rom.ADD_HL_DE()   # HL = REGION_GRAPH + region*5 (16-bit,
                                        # correct up to scale=9's 81 regions)
    rom.LD_A_HLI()                     # A = biome-id (0..4); HL -> 'up' byte
    rom.PUSH_HL()                      # save neighbor-byte pointer across CALLs
    rom.JR('dsr_p_dispatch')

    rom.label('dsr_p_inf')
    rom.LD_A_nn(INF_WINDOW + 4)        # center cell of the 3x3 window
    rom.AND_n(0x07)                    # A = biome-id (bits 0-2)
    rom.PUSH_HL()                      # stack-balance only -- dsr_p_copy's own
                                        # POP_HL() must see something pushed on
                                        # both paths; draw_region_arrows_inf
                                        # ignores HL entirely (reads WRAM directly)

    rom.label('dsr_p_dispatch')
    rom.CP_n(0); rom.JR_Z('dsr_p_water')
    rom.CP_n(1); rom.JR_Z('dsr_p_sand')
    rom.CP_n(2); rom.JR_Z('dsr_p_grass')
    rom.CP_n(3); rom.JR_Z('dsr_p_stone')
    rom.JR('dsr_p_brick')              # biome-id 4 (generate_world's own
                                        # invariant: axis-clamped to 0..4)

    def _dsr_family(lbl, pt_key, pa_key):
        rom.label(lbl)
        rom.LD_DE_nn(0); patches[pt_key] = rom.pos - 2
        rom.LD_BC_nn(0); patches[pa_key] = rom.pos - 2
        rom.JR('dsr_p_copy')

    _dsr_family('dsr_p_water', 'water_t', 'water_a')
    _dsr_family('dsr_p_sand',  'sand_t',  'sand_a')
    _dsr_family('dsr_p_grass', 'grass_t', 'grass_a')
    _dsr_family('dsr_p_stone', 'stone_t', 'stone_a')
    _dsr_family('dsr_p_brick', 'brick_t', 'brick_a')

    rom.label('dsr_p_copy')
    rom.CALL('copy_screen')
    rom.POP_HL()                       # HL -> 'up' neighbor byte, restored (finite mode) or
                                        # a discarded stack-balance value (infinite mode)
    rom.LD_A_nn(GAME_MODE); rom.OR_A(); rom.JR_NZ('dsr_p_copy_inf')
    rom.CALL('draw_region_arrows')
    rom.JP('dsr_done')

    rom.label('dsr_p_copy_inf')
    rom.CALL('draw_region_arrows_inf')
    rom.JP('dsr_done')

    rom.label('dsr_done')
    rom.LD_A_n(0x97); rom.LDH_n_A(LCDC)   # re-enable LCD + 8x16 OBJ
    rom.RET()

    # ── copy_screen: DE=tile_src, BC=attr_src ─────────────
    rom.label('copy_screen')
    rom.PUSH_BC()
    rom.XOR_A(); rom.LDH_n_A(VBK)
    rom.LD_HL_nn(0x9800); rom.LD_BC_nn(576)
    rom.label('cs_t')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cs_t')
    rom.LD_A_n(1); rom.LDH_n_A(VBK)
    rom.POP_BC()
    rom.LD_A_C(); rom.LD_E_A()
    rom.LD_A_B(); rom.LD_D_A()
    rom.LD_HL_nn(0x9800); rom.LD_BC_nn(576)
    rom.label('cs_a')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cs_a')
    rom.XOR_A(); rom.LDH_n_A(VBK)
    rom.RET()

    # ── draw_region_arrows (IP-1030) ──────────────────────
    # Retires tilemaps.py's build-time _zone_arrows (fixed 3x3 rectangle
    # math, ADR-0009 point 6). Reads the 4 neighbor-index bytes for the
    # current region (HL, passed in by the caller, positioned at
    # REGION_GRAPH's 'up' byte per dsr_p) and draws an arrow wherever the
    # neighbor is valid (!= 0xFF) — same tile positions/palette as the
    # retired build-time version, just resolved at runtime since a
    # generated world's neighbor structure isn't known until generation
    # runs. Called from inside do_screen_redraw's existing LCD-off
    # bracket (NFR-1300: no new safe-window convention).
    ARROW_ADDR_U = 0x9800 + 1*32 + 15
    ARROW_ADDR_D = 0x9800 + 16*32 + 15
    ARROW_ADDR_L = 0x9800 + 9*32 + 1
    ARROW_ADDR_R = 0x9800 + 9*32 + (20-2)   # IP-9140 (BL-0084): the true
                          # visible background window is 20 tiles wide
                          # (SCX=0 always in this codebase) x 18 tall, not
                          # the full 32x32 tilemap -- (32-2)=column 30 has
                          # never been on-screen, a defect inherited
                          # unchanged from the retired pre-procgen
                          # _zone_arrows. Column 18 mirrors ARROW_ADDR_L's
                          # own column-1 margin symmetrically within the
                          # true visible 0-19 column range.

    def _arrow_write(addr, tile):
        rom.XOR_A(); rom.LDH_n_A(VBK)
        rom.LD_A_n(tile); rom.LD_HL_nn(addr); rom.LD_HL_A()
        rom.LD_A_n(1); rom.LDH_n_A(VBK)
        rom.LD_A_n(2); rom.LD_HL_nn(addr); rom.LD_HL_A()   # palette 2, matching
                                                             # _zone_arrows' original
        rom.XOR_A(); rom.LDH_n_A(VBK)

    rom.label('draw_region_arrows')
    # IP-1080 (FR-2330): re-derive grid adjacency from (row, col, WORLD_SCALE)
    # arithmetic before the four REGION_GRAPH neighbor bytes below claim
    # B-E -- row/col must survive all four direction tests, and B-E are
    # about to be repurposed. row = CUR_ZONE / WORLD_SCALE, col = CUR_ZONE
    # MOD WORLD_SCALE via repeated subtraction (WORLD_SCALE is 2-9, CUR_ZONE
    # is 0-80, at most 9 iterations -- same repeated-subtraction style as
    # generate_world's own gw_mod3, parameterized by a runtime WORLD_SCALE
    # via CP_B rather than a compile-time CP_n). Stashed in DRA_ROW/DRA_COL
    # -- dedicated transient scratch, not TMP1/TMP2 as originally suggested
    # (this package's own §6 text) -- TMP1 collides with handle_play_input's
    # own per-frame "did the player move" flag, see DRA_ROW's own WRAM
    # comment above for the discovery. This is what lets a maze-pruned edge
    # (a grid-neighbor genuinely exists here, REGION_GRAPH just says 0xFF
    # because IP-1070's braid pass pruned it -- "blocked") be distinguished
    # from a true grid boundary (no grid-neighbor at all -- "absent") --
    # REGION_GRAPH's own neighbor byte alone cannot tell the two apart once
    # the maze pass has run (ADR-0012 point 2). IP-1082 (FR-2330) draws the
    # blocked-edge indicator using this same row/col; row/col are directly
    # testable via DRA_ROW/DRA_COL (T20.b/c), the classification arithmetic
    # FR-2330 requires.
    rom.LD_A_nn(WORLD_SCALE); rom.LD_B_A()
    rom.LD_A_nn(CUR_ZONE); rom.LD_C_n(0)
    rom.label('dra_div_loop')
    rom.CP_B(); rom.JR_C('dra_div_done')
    rom.SUB_B(); rom.INC_C()
    rom.JR('dra_div_loop')
    rom.label('dra_div_done')
    rom.LD_nn_A(DRA_COL)                 # A = col (remainder)
    rom.LD_A_C(); rom.LD_nn_A(DRA_ROW)   # C = row (quotient)

    rom.LD_A_HLI(); rom.LD_B_A()       # B = up
    rom.LD_A_HLI(); rom.LD_C_A()       # C = down
    rom.LD_A_HLI(); rom.LD_D_A()       # D = left
    rom.LD_A_HL();  rom.LD_E_A()       # E = right

    rom.LD_A_B(); rom.CP_n(0xFF); rom.JR_Z('dra_no_up')
    _arrow_write(ARROW_ADDR_U, TL_ARROW_U)
    rom.JR('dra_up_done')
    rom.label('dra_no_up')
    # IP-1082 (FR-2330): B is dead past the check above (nothing later reads
    # it) -- REGION_GRAPH said 0xFF, but that alone can't distinguish a maze-
    # pruned edge ("blocked") from a true grid boundary ("absent", ADR-0012
    # point 2). row>0 means a grid neighbor genuinely exists above -- blocked.
    rom.LD_A_nn(DRA_ROW); rom.OR_A(); rom.JR_Z('dra_up_done')
    _arrow_write(ARROW_ADDR_U, TL_BLOCKED_U)
    rom.label('dra_up_done')

    rom.LD_A_C(); rom.CP_n(0xFF); rom.JR_Z('dra_no_down')
    _arrow_write(ARROW_ADDR_D, TL_ARROW_D)
    rom.JR('dra_down_done')
    rom.label('dra_no_down')
    # C is dead past the check above. row < WORLD_SCALE-1 means a grid
    # neighbor genuinely exists below -- blocked. B is dead (consumed by the
    # up-branch's own entry check) -- reused as scratch for WORLD_SCALE.
    rom.LD_A_nn(WORLD_SCALE); rom.LD_B_A()
    rom.LD_A_nn(DRA_ROW); rom.INC_A(); rom.CP_B(); rom.JR_NC('dra_down_done')
    _arrow_write(ARROW_ADDR_D, TL_BLOCKED_D)
    rom.label('dra_down_done')

    rom.LD_A_D(); rom.CP_n(0xFF); rom.JR_Z('dra_no_left')
    _arrow_write(ARROW_ADDR_L, TL_ARROW_L)
    rom.JR('dra_left_done')
    rom.label('dra_no_left')
    # D is dead past the check above. col>0 means a grid neighbor genuinely
    # exists to the left -- blocked.
    rom.LD_A_nn(DRA_COL); rom.OR_A(); rom.JR_Z('dra_left_done')
    _arrow_write(ARROW_ADDR_L, TL_BLOCKED_L)
    rom.label('dra_left_done')

    rom.LD_A_E(); rom.CP_n(0xFF); rom.JR_Z('dra_no_right')
    _arrow_write(ARROW_ADDR_R, TL_ARROW_R)
    rom.JR('dra_right_done')
    rom.label('dra_no_right')
    # E is dead past the check above (this is the last direction). col <
    # WORLD_SCALE-1 means a grid neighbor genuinely exists to the right --
    # blocked. C is dead (consumed by the down-branch's own entry check) --
    # reused as scratch for WORLD_SCALE.
    rom.LD_A_nn(WORLD_SCALE); rom.LD_C_A()
    rom.LD_A_nn(DRA_COL); rom.INC_A(); rom.CP_C(); rom.JR_NC('dra_right_done')
    _arrow_write(ARROW_ADDR_R, TL_BLOCKED_R)
    rom.label('dra_right_done')
    rom.RET()

    # ── draw_region_arrows_inf (IP-1102) ──────────────────
    # Infinite Mode's own arrow-draw routine -- reads the current region's
    # connectivity nibble directly from INF_WINDOW's center cell (bits 3-6:
    # up/down/left/right, 1=open) rather than REGION_GRAPH neighbor-index
    # bytes. No grid-boundary distinction is needed here (ADR-0012 point 2's
    # own "blocked vs. absent" question is a finite-mode-only concept --
    # Infinite Mode's world is unbounded, every direction always has a real,
    # materializable neighbor) -- draws the plain open-arrow tile wherever
    # the bit is set, nothing wherever it is clear. Never writes
    # TL_BLOCKED_U/D/L/R (T24.d's own static-audit claim).
    rom.label('draw_region_arrows_inf')
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(3); rom.JR_Z('drai_no_up')
    _arrow_write(ARROW_ADDR_U, TL_ARROW_U)
    rom.label('drai_no_up')
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(4); rom.JR_Z('drai_no_down')
    _arrow_write(ARROW_ADDR_D, TL_ARROW_D)
    rom.label('drai_no_down')
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(5); rom.JR_Z('drai_no_left')
    _arrow_write(ARROW_ADDR_L, TL_ARROW_L)
    rom.label('drai_no_left')
    rom.LD_A_nn(INF_WINDOW + 4); rom.BIT_b_A(6); rom.JR_Z('drai_no_right')
    _arrow_write(ARROW_ADDR_R, TL_ARROW_R)
    rom.label('drai_no_right')
    rom.RET()

    # ── mm_on_entry / draw_menu_cursor (IP-1040 / IP-9060) ────
    # Runs once each time MAIN MENU is (re)entered/redrawn (state entry, or
    # after a cursor toggle — a full LCD-off redraw either way, matching
    # this codebase's existing menu-screen convention): recomputes
    # save-validity, blanks the baked "CONTINUE" label if no valid save
    # exists, and draws the highlight cursor next to MM_CURSOR's selection.
    # IP-9060 (BL-0048): MM_CURSOR's own reset-to-default only fires here on
    # a genuine state entry (MM_JUST_ENTERED, set by every GAMESTATE ->
    # GS_MAIN_MENU transition site) — a same-state redraw the player's own
    # toggle (mm_toggle) causes leaves MM_CURSOR at its just-toggled value.
    MM_CONT_ADDR = 0x9800 + 7*32 + 8   # "CONTINUE" label start (8 chars)
    MM_CURSOR_CONT_ADDR = 0x9800 + 7*32 + 6
    MM_CURSOR_NEW_ADDR  = 0x9800 + 9*32 + 6

    rom.label('mm_on_entry')
    rom.CALL('check_save_valid')
    rom.LD_A_nn(MM_JUST_ENTERED); rom.OR_A(); rom.JR_Z('mm_oe_no_reset')
    rom.XOR_A(); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.LD_A_nn(MM_SAVE_VALID); rom.OR_A(); rom.JR_NZ('mm_oe_cur_cont')
    rom.LD_A_n(1); rom.JR('mm_oe_cur_set')
    rom.label('mm_oe_cur_cont')
    rom.XOR_A()
    rom.label('mm_oe_cur_set')
    rom.LD_nn_A(MM_CURSOR)
    rom.label('mm_oe_no_reset')
    rom.LD_A_nn(MM_SAVE_VALID); rom.OR_A(); rom.JR_NZ('mm_oe_have_save')
    rom.LD_HL_nn(MM_CONT_ADDR); rom.LD_B_n(8); rom.LD_A_n(TL_BG_BLANK)
    rom.label('mm_oe_blank'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('mm_oe_blank')
    rom.label('mm_oe_have_save')
    rom.CALL('draw_menu_cursor')
    rom.RET()

    rom.label('draw_menu_cursor')
    rom.LD_HL_nn(MM_CURSOR_CONT_ADDR); rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()
    rom.LD_HL_nn(MM_CURSOR_NEW_ADDR);  rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()
    rom.LD_A_nn(MM_CURSOR); rom.OR_A(); rom.JR_NZ('dmc_newgame')
    rom.LD_HL_nn(MM_CURSOR_CONT_ADDR); rom.JR('dmc_write')
    rom.label('dmc_newgame')
    rom.LD_HL_nn(MM_CURSOR_NEW_ADDR)
    rom.label('dmc_write')
    rom.LD_A_n(TL_ARROW_R); rom.LD_HL_A()
    rom.RET()

    # ── sm_on_entry / draw_select_menu_cursor (IP-1090) ───────
    # Mirrors mm_on_entry/draw_menu_cursor, but with no save-validity gate
    # -- "map" and "legend" are always both offered, nothing is ever
    # blanked. select_menu_screen() uses the same row/column layout as
    # main_menu_screen() (rows 7/9, label start col 8), so the cursor-cell
    # addresses reuse the identical row math.
    SM_CURSOR_MAP_ADDR    = 0x9800 + 7*32 + 6
    SM_CURSOR_LEGEND_ADDR = 0x9800 + 9*32 + 6

    rom.label('sm_on_entry')
    rom.LD_A_nn(MM_JUST_ENTERED); rom.OR_A(); rom.JR_Z('sm_oe_no_reset')
    rom.XOR_A(); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.LD_nn_A(MM_CURSOR)
    rom.label('sm_oe_no_reset')
    rom.CALL('draw_select_menu_cursor')
    rom.RET()

    rom.label('draw_select_menu_cursor')
    rom.LD_HL_nn(SM_CURSOR_MAP_ADDR);    rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()
    rom.LD_HL_nn(SM_CURSOR_LEGEND_ADDR); rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()
    rom.LD_A_nn(MM_CURSOR); rom.OR_A(); rom.JR_NZ('dsmc_legend')
    rom.LD_HL_nn(SM_CURSOR_MAP_ADDR); rom.JR('dsmc_write')
    rom.label('dsmc_legend')
    rom.LD_HL_nn(SM_CURSOR_LEGEND_ADDR)
    rom.label('dsmc_write')
    rom.LD_A_n(TL_ARROW_R); rom.LD_HL_A()
    rom.RET()

    # ── ms_on_entry / draw_mode_select_cursor (IP-1100) ───────
    # Mirrors sm_on_entry/draw_select_menu_cursor exactly (no save-validity
    # gate -- "finite" and "infinite" are always both offered). MM_CURSOR
    # is reused (GS_MODE_SELECT is never simultaneously active with
    # GS_MAIN_MENU/GS_SELECT_MENU), reset to 0 ("finite") only on a genuine
    # state entry (MM_JUST_ENTERED, set by mm_newgame's own transition into
    # this state) -- a same-state redraw from the player's own toggle
    # (ms_toggle) leaves MM_CURSOR at its just-toggled value, and the B-
    # cancel-from-INFINITE-SEED-ENTRY return path deliberately does not set
    # MM_JUST_ENTERED, so the cursor stays wherever it was. mode_select_
    # screen() reuses select_menu_screen()'s own row/column layout (rows
    # 7/9, cursor col 6, label start col 8).
    MS_CURSOR_FINITE_ADDR   = 0x9800 + 7*32 + 6
    MS_CURSOR_INFINITE_ADDR = 0x9800 + 9*32 + 6

    rom.label('ms_on_entry')
    rom.LD_A_nn(MM_JUST_ENTERED); rom.OR_A(); rom.JR_Z('ms_oe_no_reset')
    rom.XOR_A(); rom.LD_nn_A(MM_JUST_ENTERED)
    rom.LD_nn_A(MM_CURSOR)
    rom.label('ms_oe_no_reset')
    rom.CALL('draw_mode_select_cursor')
    rom.RET()

    rom.label('draw_mode_select_cursor')
    rom.LD_HL_nn(MS_CURSOR_FINITE_ADDR);   rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()
    rom.LD_HL_nn(MS_CURSOR_INFINITE_ADDR); rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()
    rom.LD_A_nn(MM_CURSOR); rom.OR_A(); rom.JR_NZ('dmsc_infinite')
    rom.LD_HL_nn(MS_CURSOR_FINITE_ADDR); rom.JR('dmsc_write')
    rom.label('dmsc_infinite')
    rom.LD_HL_nn(MS_CURSOR_INFINITE_ADDR)
    rom.label('dmsc_write')
    rom.LD_A_n(TL_ARROW_R); rom.LD_HL_A()
    rom.RET()

    # ── draw_sse_digits (IP-1040) ──────────────────────────
    # Writes the 5 seed digit tiles + 1 scale digit tile, then the cursor
    # (a down-arrow above the currently-selected digit/scale slot). Called
    # once on SEED/SCALE ENTRY's state entry and again after every
    # digit-cursor edit (st_seed_scale_entry's 'sse_redraw' path) — cheap
    # enough (a handful of single-tile writes) to just redraw in full each
    # time rather than tracking a dirty subset.
    SSE_SEED_ROW = 6; SSE_SEED_COL0 = 10; SSE_SCALE_ROW = 10; SSE_SCALE_COL = 10
    SSE_CURSOR_SEED_ROW = 5; SSE_CURSOR_SCALE_ROW = 9

    rom.label('draw_sse_digits')
    for i in range(5):
        addr = 0x9800 + SSE_SEED_ROW*32 + (SSE_SEED_COL0 + i)
        rom.LD_A_nn(SSE_DIGITS + i); rom.ADD_A_n(TL_DIGIT_0)
        rom.LD_HL_nn(addr); rom.LD_HL_A()
    rom.LD_A_nn(SSE_SCALE); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x9800 + SSE_SCALE_ROW*32 + SSE_SCALE_COL); rom.LD_HL_A()

    for i in range(5):
        addr = 0x9800 + SSE_CURSOR_SEED_ROW*32 + (SSE_SEED_COL0 + i)
        rom.LD_HL_nn(addr); rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()
    rom.LD_HL_nn(0x9800 + SSE_CURSOR_SCALE_ROW*32 + SSE_SCALE_COL)
    rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()

    rom.LD_A_nn(SSE_CURSOR); rom.CP_n(5); rom.JP_Z('dsd_scale_cursor')
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(0x9800 + SSE_CURSOR_SEED_ROW*32 + SSE_SEED_COL0)
    rom.ADD_HL_DE()
    rom.LD_A_n(TL_ARROW_D); rom.LD_HL_A()
    rom.RET()
    rom.label('dsd_scale_cursor')
    rom.LD_HL_nn(0x9800 + SSE_CURSOR_SCALE_ROW*32 + SSE_SCALE_COL)
    rom.LD_A_n(TL_ARROW_D); rom.LD_HL_A()
    rom.RET()

    # ── draw_ise_digits (IP-1100) ───────────────────────────
    # Mirrors draw_sse_digits, minus the scale-digit/scale-cursor writes
    # entirely -- INFINITE SEED ENTRY has no scale slot, and SSE_CURSOR
    # never reaches 5 from this state (st_infinite_seed_entry's own
    # LEFT/RIGHT bound it to 0-4), so the cursor-arrow placement is always
    # over a seed digit, never needing dsd_scale_cursor's own branch.
    # Reuses infinite_seed_entry_screen()'s own SEED row/col (same as
    # seed_scale_entry_screen()'s, SSE_SEED_ROW/SSE_SEED_COL0/
    # SSE_CURSOR_SEED_ROW -- both screens share the identical seed-row
    # layout by design).
    rom.label('draw_ise_digits')
    for i in range(5):
        addr = 0x9800 + SSE_SEED_ROW*32 + (SSE_SEED_COL0 + i)
        rom.LD_A_nn(SSE_DIGITS + i); rom.ADD_A_n(TL_DIGIT_0)
        rom.LD_HL_nn(addr); rom.LD_HL_A()

    for i in range(5):
        addr = 0x9800 + SSE_CURSOR_SEED_ROW*32 + (SSE_SEED_COL0 + i)
        rom.LD_HL_nn(addr); rom.LD_A_n(TL_BG_BLANK); rom.LD_HL_A()

    rom.LD_A_nn(SSE_CURSOR)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(0x9800 + SSE_CURSOR_SEED_ROW*32 + SSE_SEED_COL0)
    rom.ADD_HL_DE()
    rom.LD_A_n(TL_ARROW_D); rom.LD_HL_A()
    rom.RET()

    # ── sse_adjust_up / sse_adjust_down (IP-1040) ──────────
    # SSE_CURSOR 0-4 selects a seed digit (wraps 0-9); 5 selects the scale
    # (wraps 2-9). Only the value at the cursor changes; digits don't carry
    # into each other (an odometer, not decimal arithmetic — composition
    # into the real 16-bit SEED happens once, at A-confirm, in
    # sse_compose_seed).
    rom.label('sse_adjust_up')
    rom.LD_A_nn(SSE_CURSOR); rom.CP_n(5); rom.JR_Z('sau_scale')
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(SSE_DIGITS); rom.ADD_HL_DE()
    rom.LD_A_HL(); rom.INC_A(); rom.CP_n(10); rom.JR_NZ('sau_dwrite')
    rom.XOR_A()
    rom.label('sau_dwrite')
    rom.LD_HL_A()
    rom.RET()
    rom.label('sau_scale')
    rom.LD_A_nn(SSE_SCALE); rom.INC_A(); rom.CP_n(10); rom.JR_NZ('sau_swrite')
    rom.LD_A_n(2)
    rom.label('sau_swrite')
    rom.LD_nn_A(SSE_SCALE)
    rom.RET()

    rom.label('sse_adjust_down')
    rom.LD_A_nn(SSE_CURSOR); rom.CP_n(5); rom.JR_Z('sad_scale')
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(SSE_DIGITS); rom.ADD_HL_DE()
    rom.LD_A_HL(); rom.OR_A(); rom.JR_NZ('sad_dec')
    rom.LD_A_n(10)
    rom.label('sad_dec')
    rom.DEC_A(); rom.LD_HL_A()
    rom.RET()
    rom.label('sad_scale')
    rom.LD_A_nn(SSE_SCALE); rom.CP_n(2); rom.JR_NZ('sad_sdec')
    rom.LD_A_n(10)
    rom.label('sad_sdec')
    rom.DEC_A(); rom.LD_nn_A(SSE_SCALE)
    rom.RET()

    # ── sse_compose_seed (IP-1040) ──────────────────────────
    # Composes the 5 independently-edited decimal digits into the real
    # 16-bit SEED via repeated addition (digit * place-value, digit is
    # always 0-9 so at most 9 iterations per place — no general multiply
    # needed), saturating at 0xFFFF (65535, itself a valid SEED value) if
    # the combination would otherwise overflow 16 bits. Writes WORLD_SCALE
    # directly from SSE_SCALE (already range-safe by construction).
    rom.label('sse_compose_seed')
    rom.LD_HL_nn(0)

    def _scs_place(idx, place_value, next_label):
        rom.LD_A_nn(SSE_DIGITS + idx); rom.LD_B_A()
        loop_lbl = f'scs_d{idx}lp'
        rom.label(loop_lbl)
        rom.LD_A_B(); rom.OR_A(); rom.JP_Z(next_label)
        rom.LD_DE_nn(place_value); rom.ADD_HL_DE()
        rom.JP_C('scs_sat')
        rom.DEC_B(); rom.JP(loop_lbl)

    _scs_place(0, 10000, 'scs_d1')
    rom.label('scs_d1'); _scs_place(1, 1000, 'scs_d2')
    rom.label('scs_d2'); _scs_place(2, 100,  'scs_d3')
    rom.label('scs_d3'); _scs_place(3, 10,   'scs_d4')
    rom.label('scs_d4'); _scs_place(4, 1,    'scs_store')
    rom.label('scs_store')
    rom.LD_A_H(); rom.LD_nn_A(SEED + 1)
    rom.LD_A_L(); rom.LD_nn_A(SEED)
    rom.LD_A_nn(SSE_SCALE); rom.LD_nn_A(WORLD_SCALE)
    rom.RET()
    rom.label('scs_sat')
    rom.LD_HL_nn(0xFFFF)
    rom.JP('scs_store')

    # ── inf_treasure_pos (IP-1103) ────────────────────────
    # Per-biome treasure spawn position, 5 x (x, y) pairs indexed by
    # biome-id*2 -- the exact (x, y) of each biome family's type-2 (KeyItem)
    # entry in tilemaps.py's ZONE_COLLECTS, so the Infinite Mode treasure
    # appears at the same sensible, landmark-clear spot the finite mode
    # places this item on the identical screen art (and renders with the
    # same TL_CARROT tile/palette via update_oam's existing type-2 path --
    # no new tile art, this tranche's own convention). Values duplicated
    # here rather than imported (asm_game.py deliberately imports nothing
    # from the content modules, ADR-0003); T26.a's static check asserts
    # this table matches ZONE_COLLECTS's type-2 entries, so content-side
    # drift fails the suite instead of silently desyncing. Data, not code:
    # the block above ends with JP, execution never falls through here.
    rom.label('inf_treasure_pos')
    rom.emit(140, 56,   # 0 Water
             132, 88,   # 1 Sand
             84,  56,   # 2 Grass
             60,  88,   # 3 Stone
             84,  64)   # 4 Brick

    # ── setup_zone_collects ───────────────────────────────
    # IP-9070: zc_table is now indexed by REGION_GRAPH's biome-id (0-4, the
    # 5 biome-family-representative lists) instead of CUR_ZONE directly (a
    # 9-entry-only ROM table could not survive CUR_ZONE values above 8, which
    # IP-9050 makes reachable) -- mirrors dsr_p's own REGION_GRAPH read
    # exactly (same region*5 addressing, same biome-id byte position).
    # IP-1103: GAME_MODE-gated entry, mirroring IP-1102's own gates on
    # check_zone_transition/dsr_p -- Infinite Mode has no REGION_GRAPH or
    # zc_table spawn concept (CUR_ZONE is stale there), so it branches to
    # its own spawn logic (szc_infinite, below the finite body): COLL_DATA
    # holds exactly one item -- the region's treasure -- when the current
    # region's INF_TREASURE_HERE cache is set, and no items otherwise.
    # Before this gate, the finite body ran against stale CUR_ZONE/
    # REGION_GRAPH data in Infinite Mode, spawning finite-mode collectibles
    # whose type-2 entries incremented KEYITEM_COUNT on pickup -- reachable
    # spurious finite victory (check_complete), exactly the hazard IP-1100
    # §6 named for this package to close.
    rom.label('setup_zone_collects')
    rom.LD_A_nn(GAME_MODE); rom.OR_A(); rom.JP_NZ('szc_infinite')
    rom.LD_A_nn(CUR_ZONE)
    rom.LD_E_A(); rom.LD_D_n(0)        # DE = region index
    rom.LD_HL_nn(REGION_GRAPH)
    rom.ADD_HL_DE(); rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.ADD_HL_DE(); rom.ADD_HL_DE()   # HL = REGION_GRAPH + region*5
    rom.LD_A_HL()                      # A = biome-id (0..4)
    rom.ADD_A_A()                      # A = biome-id * 2 (zc_table index)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(0); patches['zc_table'] = rom.pos - 2
    rom.ADD_HL_DE()
    rom.LD_A_HLI(); rom.LD_E_A()
    rom.LD_A_HLI(); rom.LD_D_A()
    # DE → zone block
    rom.LD_A_DE(); rom.LD_nn_A(COLL_COUNT); rom.LD_B_A(); rom.INC_DE()
    rom.LD_HL_nn(COLL_DATA)
    rom.label('szc_lp')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE()    # x
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE()    # y
    rom.LD_A_DE(); rom.LD_C_A()                     # C = type
    rom.LD_HLI_A(); rom.INC_DE()
    rom.LD_A_n(1); rom.LD_HLI_A()                   # active = 1
    rom.INC_DE()
    # If KeyItem (type==2) and KEYITEM_FLAGS[CUR_ZONE] != 0 → mark inactive
    # (IP-1020: generalizes the carrot check — same logic, KEYITEM_FLAGS target)
    rom.LD_A_C(); rom.CP_n(2); rom.JR_NZ('szc_score_chk')
    rom.PUSH_BC(); rom.PUSH_DE(); rom.PUSH_HL()
    rom.LD_A_nn(CUR_ZONE)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.ADD_HL_DE()
    rom.LD_A_HL()
    rom.POP_HL(); rom.POP_DE(); rom.POP_BC()
    rom.OR_A(); rom.JR_Z('szc_sk')
    # mark inactive: HL points one past 'active' field, so HL-1
    rom.DEC_HL(); rom.XOR_A(); rom.LD_HL_A(); rom.INC_HL()
    rom.JR('szc_sk')

    # FR-5220: non-carrot entry — if bit k = COLL_COUNT-B of
    # SCOREITEM_FLAGS[CUR_ZONE] is set, this ScoreItem was already collected
    # (this session or a prior save) — mark inactive, mirroring the carrot
    # branch's push/pop-scratch discipline exactly.
    rom.label('szc_score_chk')
    rom.PUSH_BC(); rom.PUSH_DE(); rom.PUSH_HL()
    rom.LD_A_nn(COLL_COUNT); rom.SUB_B()
    rom.LD_C_A()
    rom.LD_B_n(1)
    rom.label('szc_si_mkloop')
    rom.LD_A_C(); rom.OR_A(); rom.JR_Z('szc_si_mkdone')
    rom.SLA_B(); rom.DEC_C(); rom.JR('szc_si_mkloop')
    rom.label('szc_si_mkdone')
    rom.LD_A_nn(CUR_ZONE); rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(SCOREITEM_FLAGS); rom.ADD_HL_DE()
    rom.LD_A_HL(); rom.AND_B()
    rom.POP_HL(); rom.POP_DE(); rom.POP_BC()
    rom.OR_A(); rom.JR_Z('szc_sk')
    rom.DEC_HL(); rom.XOR_A(); rom.LD_HL_A(); rom.INC_HL()

    rom.label('szc_sk')
    rom.DEC_B(); rom.JR_NZ('szc_lp'); rom.RET()

    # IP-1103: Infinite Mode spawn branch (see the gate at this routine's
    # entry). COLL_COUNT is written 0 first so a treasure-less region leaves
    # no stale finite-mode COLL_DATA active (check_collisions/update_oam
    # both early-out on COLL_COUNT==0). With the cache set, spawns exactly
    # one active type-2 item at the biome's own inf_treasure_pos entry --
    # biome-id read from INF_WINDOW's center cell, the identical source
    # dsr_p_inf renders from, so the spawn position always matches the art
    # on screen. Runs on every PLAYING (re)entry (menu round-trips
    # included): cache still set -> same treasure re-spawns (uncollected);
    # cache cleared by collection -> COLL_COUNT stays 0, no respawn.
    rom.label('szc_infinite')
    rom.XOR_A(); rom.LD_nn_A(COLL_COUNT)
    rom.LD_A_nn(INF_TREASURE_HERE); rom.OR_A(); rom.RET_Z()
    rom.LD_A_nn(INF_WINDOW + 4); rom.AND_n(0x07)   # biome-id (0..4)
    rom.ADD_A_A()                                   # * 2 ((x,y) pairs)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(rom.addr('inf_treasure_pos')); rom.ADD_HL_DE()
    rom.LD_A_HLI(); rom.LD_nn_A(COLL_DATA)          # x
    rom.LD_A_HL();  rom.LD_nn_A(COLL_DATA + 1)      # y
    rom.LD_A_n(2);  rom.LD_nn_A(COLL_DATA + 2)      # type 2 (KeyItem art/palette)
    rom.LD_A_n(1);  rom.LD_nn_A(COLL_DATA + 3)      # active
    rom.LD_A_n(1);  rom.LD_nn_A(COLL_COUNT)
    rom.RET()

    # ── update_map_hearts ─────────────────────────────────
    # 9 hearts at 3x3 grid. Read KEYITEM_FLAGS[i] and write FULL or EMPTY.
    # (IP-1020: generalizes from CARROT_FLAGS, which check_collisions/
    # setup_zone_collects no longer write — this read must track the rename.)
    rom.label('update_map_hearts')
    map_addrs = [
        # (BG addr for heart at zone index i)
        0x9800 + 6*32 + 6,    # z0 = (col=0, row=0)
        0x9800 + 6*32 + 11,   # z1 = (col=1, row=0)
        0x9800 + 6*32 + 16,   # z2 = (col=2, row=0)
        0x9800 + 9*32 + 6,    # z3
        0x9800 + 9*32 + 11,   # z4
        0x9800 + 9*32 + 16,   # z5
        0x9800 + 12*32 + 6,   # z6
        0x9800 + 12*32 + 11,  # z7
        0x9800 + 12*32 + 16,  # z8
    ]
    for i, addr in enumerate(map_addrs):
        rom.LD_A_nn(KEYITEM_FLAGS + i)
        rom.OR_A()
        rom.LD_A_n(TL_HEART_FULL)
        rom.JR_NZ(f'umh_w{i}')
        rom.LD_A_n(TL_HEART_EMPTY)
        rom.label(f'umh_w{i}')
        rom.LD_HL_nn(addr); rom.LD_HL_A()
    rom.RET()

    # ── generate_world (IP-1020) ──────────────────────────
    # Deterministically generates a WORLD_SCALE x WORLD_SCALE region grid from
    # (SEED, WORLD_SCALE) into REGION_GRAPH, flood-filling biome axis-indices
    # (0=Water..4=Brick) in row-major order so every already-placed grid-
    # adjacent pair (not just the generation-predecessor edge) stays within 1
    # axis step — grammar-validity (FR-4310) by construction — and every
    # region is reachable via the fully-connected grid itself (FR-9120).
    # No call site yet: IP-1040 wires this up from the SEED/SCALE ENTRY flow.
    def _xor_d(): rom.emit(0xAA)          # XOR D  (not wrapped in gbc_lib.py)
    def _xor_e(): rom.emit(0xAB)          # XOR E
    def _cp_e():  rom.emit(0xBB)          # CP E
    def _sla_e(): rom.emit(0xCB, 0x23)    # SLA E  (not wrapped in gbc_lib.py)
    def _rl_d():  rom.emit(0xCB, 0x12)    # RL D
    def _srl_d(): rom.emit(0xCB, 0x22)    # SRL D
    def _rr_e():  rom.emit(0xCB, 0x1B)    # RR E

    rom.label('gw_prng_step')
    # 16-bit xorshift-style state in TMP1:TMP2 (hi:lo). Shift+XOR only, no
    # multiply/divide (NFR-2200): x ^= x<<7; x ^= x>>9; x ^= x<<8 -- the
    # period-sound R111-cited shift triplet (ADR-0014/IP-9110/BL-0074). The
    # previously-shipped x^=x<<1;x^=x>>1;x^=byteswap(x) sequence forced the
    # state's high and low bytes equal on every call (R113) -- fixed here.
    # Clobbers A, D, E only; HL/BC untouched, matching every existing call
    # site's own contract (the biome-assignment loop needs HL to survive
    # across CALL('gw_prng_step'); the maze pass explicitly brackets its own
    # D-must-survive call in PUSH_DE/POP_DE, confirming D/E are fair game).

    # x ^= x<<7. No cheap byte-move decomposition exists for a truncated
    # 16-bit left-shift-by-7 ((x<<8)>>1 != x<<7 for ~half of all 16-bit
    # values, verified exhaustively) -- 7 chained single-bit left shifts on
    # a D:E scratch pair (SLA on the low byte, RL on the high byte to rotate
    # the carry in, mirroring the routine's own original step-1 primitive).
    rom.LD_A_nn(TMP1); rom.LD_D_A()
    rom.LD_A_nn(TMP2); rom.LD_E_A()
    for _ in range(7):
        _sla_e(); _rl_d()
    rom.LD_A_nn(TMP1); _xor_d(); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(TMP2); _xor_e(); rom.LD_nn_A(TMP2)

    # x ^= x>>9 == (x>>8)>>1 (verified exact for all 65536 values) -- a free
    # byte-move (E := old TMP1, D := 0, i.e. x>>8) followed by one
    # single-bit right shift on the D:E pair.
    rom.LD_A_nn(TMP1); rom.LD_E_A()
    rom.LD_D_n(0)
    _srl_d(); _rr_e()
    rom.LD_A_nn(TMP1); _xor_d(); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(TMP2); _xor_e(); rom.LD_nn_A(TMP2)

    # x ^= x<<8 -- a straight byte-move (D := old TMP2; the shifted low byte
    # is always 0, so it never changes TMP2) -- cheaper than the byte-swap
    # step it replaces.
    rom.LD_A_nn(TMP2); rom.LD_D_A()
    rom.LD_A_nn(TMP1); _xor_d(); rom.LD_nn_A(TMP1)

    rom.LD_A_nn(TMP2)             # A = new PRNG state's low byte
    rom.RET()

    rom.label('generate_world')
    # Seed PRNG state from SEED, normalizing 0 -> 1 (ADR-0010).
    rom.LD_A_nn(SEED); rom.LD_nn_A(TMP2)
    rom.LD_A_nn(SEED + 1); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(TMP1); rom.OR_A(); rom.JR_NZ('gw_seed_ok')
    rom.LD_A_nn(TMP2); rom.OR_A(); rom.JR_NZ('gw_seed_ok')
    rom.LD_A_n(1); rom.LD_nn_A(TMP2)
    rom.label('gw_seed_ok')

    # Precompute WORLD_SCALE^2 (no MUL opcode — repeated addition).
    rom.XOR_A(); rom.LD_nn_A(GW_SCALE_SQ)
    rom.LD_A_nn(WORLD_SCALE); rom.LD_D_A()
    rom.label('gw_sq_loop')
    rom.LD_A_D(); rom.OR_A(); rom.JR_Z('gw_sq_done')
    rom.LD_A_nn(GW_SCALE_SQ); rom.LD_E_A()
    rom.LD_A_nn(WORLD_SCALE); rom.ADD_A_E()
    rom.LD_nn_A(GW_SCALE_SQ)
    rom.LD_A_D(); rom.DEC_A(); rom.LD_D_A()
    rom.JR('gw_sq_loop')
    rom.label('gw_sq_done')

    rom.LD_HL_nn(REGION_GRAPH)
    rom.XOR_A(); rom.LD_nn_A(GW_REGION_IDX)
    rom.LD_B_n(0)   # row
    rom.LD_C_n(0)   # col

    rom.label('gw_loop')
    rom.LD_A_nn(GW_REGION_IDX); rom.OR_A(); rom.JR_NZ('gw_not_first')
    rom.LD_A_n(2); rom.LD_nn_A(GW_B_SCRATCH)
    rom.JR('gw_have_b')

    rom.label('gw_not_first')
    # anchor = left = *(HL-5) if col>0, else top = GW_TOP_ROW[col]
    rom.LD_A_C(); rom.OR_A(); rom.JR_Z('gw_anchor_top')
    rom.PUSH_HL()
    for _ in range(5): rom.DEC_HL()
    rom.LD_A_HL()
    rom.POP_HL()
    rom.JR('gw_anchor_got')
    rom.label('gw_anchor_top')
    rom.LD_D_n(GW_TOP_ROW >> 8)
    rom.LD_A_n(GW_TOP_ROW & 0xFF); rom.ADD_A_C(); rom.LD_E_A()
    rom.LD_A_DE()
    rom.label('gw_anchor_got')
    rom.LD_nn_A(GW_B_SCRATCH)   # GW_B_SCRATCH := anchor (temporary use)

    rom.CALL('gw_prng_step')    # A = new PRNG state's low byte
    rom.label('gw_mod3')
    rom.CP_n(3); rom.JR_C('gw_mod3_done')
    rom.SUB_n(3); rom.JR('gw_mod3')
    rom.label('gw_mod3_done')
    rom.LD_E_A()                 # E = mod3 result (0,1,2) -> delta (-1,0,+1)

    # b = anchor + delta, guarded to [0,4]
    rom.LD_A_E(); rom.CP_n(1); rom.JR_Z('gw_delta_zero')
    rom.JR_C('gw_delta_neg')
    rom.LD_A_nn(GW_B_SCRATCH); rom.CP_n(4); rom.JR_Z('gw_b_same')
    rom.INC_A(); rom.JR('gw_b_done')
    rom.label('gw_delta_neg')
    rom.LD_A_nn(GW_B_SCRATCH); rom.OR_A(); rom.JR_Z('gw_b_same')
    rom.DEC_A(); rom.JR('gw_b_done')
    rom.label('gw_delta_zero')
    rom.LD_A_nn(GW_B_SCRATCH); rom.JR('gw_b_done')
    rom.label('gw_b_same')
    rom.LD_A_nn(GW_B_SCRATCH)
    rom.label('gw_b_done')
    rom.LD_nn_A(GW_B_SCRATCH)

    # If both row>0 and col>0, also clamp against the top neighbor (proven by
    # induction: top/left always differ by <=2, so this two-step sequential
    # clamp equals clamping to the true [lo,hi] intersection — see worldgen.py).
    rom.LD_A_B(); rom.OR_A(); rom.JR_Z('gw_other_skip')
    rom.LD_A_C(); rom.OR_A(); rom.JR_Z('gw_other_skip')
    rom.LD_D_n(GW_TOP_ROW >> 8)
    rom.LD_A_n(GW_TOP_ROW & 0xFF); rom.ADD_A_C(); rom.LD_E_A()
    rom.LD_A_DE()
    rom.LD_D_A()                 # D = top
    rom.LD_A_nn(GW_B_SCRATCH)
    rom.CP_D()
    rom.JR_C('gw_other_lt')
    rom.SUB_D()
    rom.CP_n(2); rom.JR_C('gw_other_skip')
    rom.LD_A_D(); rom.INC_A(); rom.LD_nn_A(GW_B_SCRATCH)
    rom.JR('gw_other_skip')
    rom.label('gw_other_lt')
    rom.LD_E_A()
    rom.LD_A_D(); rom.SUB_E()
    rom.CP_n(2); rom.JR_C('gw_other_skip')
    rom.LD_A_D(); rom.DEC_A(); rom.LD_nn_A(GW_B_SCRATCH)
    rom.label('gw_other_skip')

    rom.label('gw_have_b')
    rom.LD_A_nn(GW_B_SCRATCH)
    rom.LD_HL_A()                # REGION_GRAPH[region].biome = b
    # GW_TOP_ROW[col] = b (this row's value, for next row's lookup)
    rom.PUSH_HL()
    rom.LD_D_n(GW_TOP_ROW >> 8)
    rom.LD_A_n(GW_TOP_ROW & 0xFF); rom.ADD_A_C(); rom.LD_E_A()
    rom.LD_A_nn(GW_B_SCRATCH)
    rom.LD_DE_A()
    rom.POP_HL()
    rom.INC_HL()                 # HL -> up-slot

    # up = idx-scale if row>0 else 0xFF
    rom.LD_A_B(); rom.OR_A(); rom.JR_NZ('gw_up_calc')
    rom.LD_A_n(0xFF); rom.JR('gw_up_write')
    rom.label('gw_up_calc')
    rom.LD_A_nn(WORLD_SCALE); rom.LD_E_A()
    rom.LD_A_nn(GW_REGION_IDX); rom.SUB_E()
    rom.label('gw_up_write')
    rom.LD_HL_A(); rom.INC_HL()  # HL -> down-slot

    # down = idx+scale if row < scale-1 else 0xFF
    rom.LD_A_nn(WORLD_SCALE); rom.LD_E_A()
    rom.LD_A_B(); rom.INC_A(); _cp_e()
    rom.JR_C('gw_down_calc')
    rom.LD_A_n(0xFF); rom.JR('gw_down_write')
    rom.label('gw_down_calc')
    rom.LD_A_nn(GW_REGION_IDX); rom.ADD_A_E()
    rom.label('gw_down_write')
    rom.LD_HL_A(); rom.INC_HL()  # HL -> left-slot

    # left = idx-1 if col>0 else 0xFF
    rom.LD_A_C(); rom.OR_A(); rom.JR_NZ('gw_left_calc')
    rom.LD_A_n(0xFF); rom.JR('gw_left_write')
    rom.label('gw_left_calc')
    rom.LD_A_nn(GW_REGION_IDX); rom.DEC_A()
    rom.label('gw_left_write')
    rom.LD_HL_A(); rom.INC_HL()  # HL -> right-slot

    # right = idx+1 if col < scale-1 else 0xFF
    rom.LD_A_nn(WORLD_SCALE); rom.LD_E_A()
    rom.LD_A_C(); rom.INC_A(); _cp_e()
    rom.JR_C('gw_right_calc')
    rom.LD_A_n(0xFF); rom.JR('gw_right_write')
    rom.label('gw_right_calc')
    rom.LD_A_nn(GW_REGION_IDX); rom.INC_A()
    rom.label('gw_right_write')
    rom.LD_HL_A(); rom.INC_HL()  # HL -> next region's start (advanced by 5 total)

    # advance region_idx
    rom.LD_A_nn(GW_REGION_IDX); rom.INC_A(); rom.LD_nn_A(GW_REGION_IDX)
    # advance col/row
    rom.LD_A_C(); rom.INC_A(); rom.LD_C_A()
    rom.LD_A_nn(WORLD_SCALE)
    rom.CP_C(); rom.JR_NZ('gw_no_row_wrap')
    rom.LD_C_n(0)
    rom.LD_A_B(); rom.INC_A(); rom.LD_B_A()
    rom.label('gw_no_row_wrap')
    # done?
    rom.LD_A_nn(GW_REGION_IDX); rom.LD_E_A()
    rom.LD_A_nn(GW_SCALE_SQ); _cp_e()
    rom.JP_NZ('gw_loop')   # JR range (-128..127) is too short for this loop body
    # (biome-assignment pass ends here, entirely unchanged -- ADR-0012 point 1)

    # ── maze-generation pass (IP-1070, ADR-0012, ADR-0013) ────
    # A second, independent pass over the same grid: a randomized DFS/recursive-
    # backtracker spanning tree (reusing REGION_GRAPH's own already-written
    # full-lattice candidate bytes above as the "does a grid-adjacent region
    # exist here" test, per ADR-0012 point 3), then a canonical-edge (down/right
    # only, so each undirected edge is decided exactly once) braid/prune pass.
    # Every gw_prng_step draw in this pass is XORed against GW_MAZE_DRAW_CTR
    # (incremented per draw, never fed back into TMP1/TMP2) before use, per
    # ADR-0013 -- gw_prng_step's own algorithm and every other call site
    # (the biome loop above) are completely unaffected.
    # NOTE: gw_neighbor_hl/gw_maze_state_hl (called throughout below) are
    # defined AFTER this pass's own final RET (before save_to_sram) -- placing
    # a subroutine's body where normal fall-through execution would enter it
    # before any CALL is a real bug (its own RET would then pop whatever the
    # stack's top actually holds, not a legitimate return address); every
    # subroutine in this file is reached only via CALL, defined past a RET.
    GW_BRAID_THRESHOLD = 63   # ~63/255 -> reopen ~25% of pruned edges (FR-9150 default)

    def _xor_c(): rom.emit(0xA9)          # XOR C  (not wrapped in gbc_lib.py)

    def _perturb_draw():
        # On entry: A = raw gw_prng_step output. On exit: A = perturbed byte
        # (A XOR GW_MAZE_DRAW_CTR, pre-step), GW_MAZE_DRAW_CTR advanced.
        # Clobbers C, E. Never touches D (the braid pass's own call site relies
        # on D surviving across this, per its own PUSH_DE/POP_DE bracket below).
        # The counter steps by 97 (odd, so it cycles through all 256 byte
        # values before repeating) rather than 1: a handful of draws already
        # scatters across the full 0-255 range, so XORing it against even a
        # PRNG output stuck at a constant (R113's degenerate-cycle finding)
        # still produces a well-spread perturbed byte relative to the
        # braid-fraction threshold comparison below -- a plain +1 counter
        # stays under any reasonable threshold for the first ~60 draws of a
        # single generation event, which is not enough spread by itself.
        rom.LD_E_A()
        rom.LD_A_nn(GW_MAZE_DRAW_CTR)
        rom.LD_C_A()
        rom.ADD_A_n(97); rom.LD_nn_A(GW_MAZE_DRAW_CTR)
        rom.LD_A_E()
        _xor_c()

    # ── maze_init: zero GW_MAZE_STATE (fixed 81-byte clear, mirroring the
    # established KEYITEM_FLAGS/SCOREITEM_FLAGS convention exactly -- clearing
    # past scale² is harmless, those indices are never read); zero the draw
    # counter; mark region 0 (the tree's root) visited with no parent (root-
    # ness is disambiguated by region index 0 at the backtrack-termination
    # check, not a distinct bit).
    rom.LD_HL_nn(GW_MAZE_STATE); rom.LD_B_n(81); rom.XOR_A()
    rom.label('gwm_zero'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('gwm_zero')
    rom.XOR_A(); rom.LD_nn_A(GW_MAZE_DRAW_CTR)
    rom.LD_A_n(0x80); rom.LD_nn_A(GW_MAZE_STATE)   # region 0 == GW_MAZE_STATE base
    rom.XOR_A(); rom.LD_nn_A(GW_CUR_REGION)

    # ── maze_carve_top: fresh mod-4 starting-direction draw at GW_CUR_REGION
    # (ADR-0012 point 3 -- a single AND 3 mask, no modulo-by-variable-count
    # operation anywhere in this pass), perturbed per ADR-0013.
    rom.label('maze_carve_top')
    rom.CALL('gw_prng_step')
    _perturb_draw()
    rom.AND_n(3); rom.LD_nn_A(GW_MAZE_DIR)
    rom.XOR_A(); rom.LD_nn_A(GW_BRAID_IDX)   # try-count, reset

    rom.label('maze_try_loop')
    rom.LD_A_nn(GW_MAZE_DIR); rom.LD_C_A()
    rom.LD_A_nn(GW_CUR_REGION)
    rom.CALL('gw_neighbor_hl')               # HL -> REGION_GRAPH[R].neighbor[dir]
    rom.LD_A_HL()
    rom.CP_n(0xFF); rom.JR_Z('maze_try_next')   # off-grid in this direction

    rom.LD_D_A()                              # D = V (candidate region)
    rom.LD_A_D()
    rom.CALL('gw_maze_state_hl')              # HL -> GW_MAZE_STATE[V]
    rom.LD_A_HL()
    rom.BIT_b_A(7); rom.JR_NZ('maze_try_next')   # already visited

    # carve: V.visited=1, V.parent_dir = opposite(dir); HL still -> GW_MAZE_STATE[V]
    rom.LD_A_nn(GW_MAZE_DIR)
    rom.XOR_n(1); rom.OR_n(0x80)
    rom.LD_HL_A()
    rom.LD_A_D(); rom.LD_nn_A(GW_CUR_REGION)  # advance: current region := V
    rom.JP('maze_carve_top')

    rom.label('maze_try_next')
    rom.LD_A_nn(GW_MAZE_DIR); rom.INC_A(); rom.AND_n(3); rom.LD_nn_A(GW_MAZE_DIR)
    rom.LD_A_nn(GW_BRAID_IDX); rom.INC_A(); rom.LD_nn_A(GW_BRAID_IDX)
    rom.CP_n(4); rom.JP_NZ('maze_try_loop')

    # all 4 directions exhausted at GW_CUR_REGION: backtrack, or done if root
    rom.LD_A_nn(GW_CUR_REGION); rom.OR_A(); rom.JR_NZ('maze_backtrack')
    rom.JP('maze_carve_done')

    rom.label('maze_backtrack')
    rom.LD_A_nn(GW_CUR_REGION)
    rom.CALL('gw_maze_state_hl')              # HL -> GW_MAZE_STATE[GW_CUR_REGION]
    rom.LD_A_HL(); rom.AND_n(3); rom.LD_C_A()  # C = this region's own parent-dir
    rom.LD_A_nn(GW_CUR_REGION)
    rom.CALL('gw_neighbor_hl')                # HL -> the parent's region index
    rom.LD_A_HL(); rom.LD_nn_A(GW_CUR_REGION) # move to parent
    rom.JP('maze_carve_top')

    # ── maze_carve_done: spanning tree complete. Canonical-edge (down/right
    # only, so each undirected edge is decided exactly once) braid/prune pass.
    rom.label('maze_carve_done')
    rom.XOR_A(); rom.LD_nn_A(GW_BRAID_IDX)    # repurposed: region-loop counter

    # ── IP-1021 (FR-9160/ADR-0015): KeyItem placement pass. Runs here --
    # spanning tree complete, braid pass not yet started -- because leaf
    # status must be snapshotted from the pure tree; braiding can turn a
    # former leaf into a non-leaf by reopening a pruned edge. Reuses
    # GW_MAZE_DIR/GW_BRAID_IDX as this pass's own nested direction/region
    # loop counters (safe: maze_prune_region's own first instructions
    # re-set GW_MAZE_DIR unconditionally, and this pass finishes by
    # re-zeroing GW_BRAID_IDX to satisfy maze_prune_region's own
    # precondition, restoring exactly what maze_carve_done's own line
    # above already set up). GW_MAZE_STATE bit 6 (never read by the
    # carve/braid passes, which only ever test bit 7/bits 1:0) is
    # repurposed as a transient "is this region a leaf" scratch flag,
    # meaningful only within this same pass. No PRNG draws -- placement
    # "randomness" comes entirely from which regions the tree/braid
    # shape makes leaves, which already varies by seed; this avoids the
    # same modulo-by-variable-count selection problem ADR-0012 already
    # ruled out Kruskal/Prim for on this codebase's PRNG.
    rom.XOR_A(); rom.LD_nn_A(GW_KI_PLACED)    # placed := 0

    # Pass A: one full region sweep. Classify each region's leaf status
    # (all 4 directions -- unlike the braid pass's own canonical
    # down/right-only sweep, leaf-ness needs every direction) and mark
    # KEYITEM_FLAGS: leaves get placed (byte stays 0, "present",
    # up to WORLD_SCALE), everything else gets 2 ("absent") tentatively
    # -- Pass B below may un-mark a non-leaf region back to 0 if a
    # shortfall needs filling.
    rom.XOR_A(); rom.LD_nn_A(GW_BRAID_IDX)    # region R := 0

    rom.label('ki_passA_region')
    rom.XOR_A(); rom.LD_B_A()                 # B := has_child (0 = no)
    rom.XOR_A(); rom.LD_nn_A(GW_MAZE_DIR)     # dir := 0 (plain 0..3 count, no
                                                # rotation needed -- order doesn't
                                                # matter for classification)

    rom.label('ki_passA_dir')
    rom.LD_A_nn(GW_MAZE_DIR); rom.LD_C_A()
    rom.LD_A_nn(GW_BRAID_IDX)                 # A = R
    rom.CALL('gw_neighbor_hl')                # HL -> REGION_GRAPH[R].neighbor[dir]
    rom.LD_A_HL()
    rom.CP_n(0xFF); rom.JR_Z('ki_passA_dir_next')   # no neighbor this direction

    # A = V (neighbor region index) -- gw_maze_state_hl clobbers A only,
    # and A already holds V, so no stash is needed before the call.
    rom.CALL('gw_maze_state_hl')              # HL -> GW_MAZE_STATE[V]
    rom.LD_A_HL(); rom.AND_n(3); rom.LD_E_A() # E = V's own parent-direction
    rom.LD_A_nn(GW_MAZE_DIR); rom.XOR_n(1)    # A = opposite(dir) -- same trick
                                                # maze_try_loop's own carve step uses
    _cp_e()                                    # V.parent_dir == opposite(dir)?
    rom.JR_NZ('ki_passA_dir_next')            # no -- V is not R's child via this edge
    rom.LD_A_n(1); rom.LD_B_A()               # yes -- R has a child, not a leaf

    rom.label('ki_passA_dir_next')
    rom.LD_A_nn(GW_MAZE_DIR); rom.INC_A(); rom.LD_nn_A(GW_MAZE_DIR)
    rom.CP_n(4); rom.JR_NZ('ki_passA_dir')

    # B = has_child for region R. Leaf iff B == 0.
    rom.LD_A_B(); rom.OR_A(); rom.JR_NZ('ki_passA_not_leaf')

    # --- leaf branch: mark GW_MAZE_STATE[R] bit 6, place if under cap ---
    rom.LD_A_nn(GW_BRAID_IDX)
    rom.CALL('gw_maze_state_hl')              # HL -> GW_MAZE_STATE[R]
    rom.LD_A_HL(); rom.SET_b_A(6); rom.LD_HL_A()   # mark leaf

    rom.LD_A_nn(WORLD_SCALE); rom.LD_D_A()    # D = WORLD_SCALE
    rom.LD_A_nn(GW_KI_PLACED)
    rom.CP_D(); rom.JR_NC('ki_passA_mark_absent2')   # placed >= WORLD_SCALE: cap
                                                       # already reached, this excess
                                                       # leaf becomes absent instead
    rom.LD_A_nn(GW_KI_PLACED); rom.INC_A(); rom.LD_nn_A(GW_KI_PLACED)
    rom.LD_A_nn(GW_BRAID_IDX)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.ADD_HL_DE()
    rom.XOR_A(); rom.LD_HL_A()                # KEYITEM_FLAGS[R] = 0 (present)
    rom.JR('ki_passA_next_region')

    rom.label('ki_passA_mark_absent2')
    rom.LD_A_nn(GW_BRAID_IDX)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.ADD_HL_DE()
    rom.LD_A_n(2); rom.LD_HL_A()              # KEYITEM_FLAGS[R] = 2 (absent)
    rom.JR('ki_passA_next_region')

    rom.label('ki_passA_not_leaf')
    rom.LD_A_nn(GW_BRAID_IDX)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.ADD_HL_DE()
    rom.LD_A_n(2); rom.LD_HL_A()              # KEYITEM_FLAGS[R] = 2 (absent, tentative)

    rom.label('ki_passA_next_region')
    rom.LD_A_nn(GW_BRAID_IDX); rom.INC_A(); rom.LD_nn_A(GW_BRAID_IDX)
    rom.LD_E_A()
    rom.LD_A_nn(GW_SCALE_SQ); _cp_e()
    rom.JP_NZ('ki_passA_region')   # JP not JR: the per-region body this closes is
                                     # too long for JR's +-127 byte range

    # Pass B: only if Pass A placed fewer than WORLD_SCALE (leaf count was
    # short) -- fill the remainder from the first non-leaf regions found,
    # in region-index order (deterministic from (SEED, WORLD_SCALE), since
    # which regions are leaves already varies by seed).
    rom.LD_A_nn(WORLD_SCALE); rom.LD_D_A()
    rom.LD_A_nn(GW_KI_PLACED)
    rom.CP_D(); rom.JR_NC('ki_passB_done')    # already reached WORLD_SCALE -- no
                                                # shortfall, skip Pass B entirely

    rom.XOR_A(); rom.LD_nn_A(GW_BRAID_IDX)    # region R := 0 again

    rom.label('ki_passB_region')
    rom.LD_A_nn(GW_BRAID_IDX)
    rom.CALL('gw_maze_state_hl')              # HL -> GW_MAZE_STATE[R]
    rom.LD_A_HL(); rom.BIT_b_A(6)
    rom.JR_NZ('ki_passB_next_region')         # was a leaf -- already placed, skip

    rom.LD_A_nn(WORLD_SCALE); rom.LD_D_A()
    rom.LD_A_nn(GW_KI_PLACED)
    rom.CP_D(); rom.JR_NC('ki_passB_done')    # shortfall now fully filled -- stop
                                                # the whole pass, not just this region

    rom.LD_A_nn(GW_KI_PLACED); rom.INC_A(); rom.LD_nn_A(GW_KI_PLACED)
    rom.LD_A_nn(GW_BRAID_IDX)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.ADD_HL_DE()
    rom.XOR_A(); rom.LD_HL_A()                # KEYITEM_FLAGS[R] = 0 (present, fallback fill)

    rom.label('ki_passB_next_region')
    rom.LD_A_nn(GW_BRAID_IDX); rom.INC_A(); rom.LD_nn_A(GW_BRAID_IDX)
    rom.LD_E_A()
    rom.LD_A_nn(GW_SCALE_SQ); _cp_e()
    rom.JP_NZ('ki_passB_region')   # JP not JR: same range concern as Pass A's own
                                     # back-edge above

    rom.label('ki_passB_done')
    rom.XOR_A(); rom.LD_nn_A(GW_BRAID_IDX)    # restore maze_prune_region's own
                                                # precondition (region-loop counter
                                                # starts at 0), since this pass
                                                # advanced it through GW_SCALE_SQ.

    rom.label('maze_prune_region')
    rom.LD_A_n(1); rom.LD_nn_A(GW_MAZE_DIR)   # repurposed: current direction (down first)

    rom.label('maze_prune_dir')
    rom.LD_A_nn(GW_MAZE_DIR); rom.LD_C_A()
    rom.LD_A_nn(GW_BRAID_IDX)                 # A = R
    rom.CALL('gw_neighbor_hl')                # HL -> REGION_GRAPH[R].neighbor[dir]
    rom.LD_A_HL()
    rom.CP_n(0xFF); rom.JR_Z('maze_prune_next_dir')   # true boundary

    rom.LD_D_A()                              # D = V

    # Check 1: V is R's child? (V.parent_dir == opposite(dir))
    rom.LD_A_D()
    rom.CALL('gw_maze_state_hl')              # HL -> GW_MAZE_STATE[V]
    rom.LD_A_HL(); rom.AND_n(3); rom.LD_E_A() # E = V.parent_dir
    rom.LD_A_nn(GW_MAZE_DIR); rom.XOR_n(1)    # A = opposite(dir)
    _cp_e(); rom.JR_Z('maze_prune_next_dir')  # tree edge -- leave both slots as-is

    # Check 2: R is V's child? (R.parent_dir == dir)
    rom.LD_A_nn(GW_BRAID_IDX)                 # A = R
    rom.CALL('gw_maze_state_hl')              # HL -> GW_MAZE_STATE[R]
    rom.LD_A_HL(); rom.AND_n(3); rom.LD_E_A() # E = R.parent_dir
    rom.LD_A_nn(GW_MAZE_DIR)                  # A = dir
    _cp_e(); rom.JR_Z('maze_prune_next_dir')  # tree edge -- leave both slots as-is

    # Not a tree edge: braid decision. D (=V) must survive the PRNG call.
    rom.PUSH_DE()
    rom.CALL('gw_prng_step')
    rom.POP_DE()                              # restore V into D; A (raw byte) untouched
    _perturb_draw()
    rom.CP_n(GW_BRAID_THRESHOLD + 1)
    rom.JR_C('maze_prune_next_dir')           # perturbed byte <= threshold: reopen, leave as-is

    # prune both directed slots of this undirected edge. Stash V into B BEFORE
    # any gw_neighbor_hl call here -- that routine clobbers D (it computes its
    # own 16-bit offset via LD_D_n(0)), so D can no longer be trusted to hold
    # V once the first of these two calls has happened; B survives both.
    rom.LD_A_D(); rom.LD_B_A()                # B = V (durable stash)
    rom.LD_A_nn(GW_MAZE_DIR); rom.LD_C_A()
    rom.LD_A_nn(GW_BRAID_IDX)
    rom.CALL('gw_neighbor_hl')                # HL -> REGION_GRAPH[R].neighbor[dir]
    rom.LD_A_n(0xFF); rom.LD_HL_A()
    rom.LD_A_nn(GW_MAZE_DIR); rom.XOR_n(1); rom.LD_C_A()   # C = opposite(dir)
    rom.LD_A_B()                              # A = V (from the durable stash)
    rom.CALL('gw_neighbor_hl')                # HL -> REGION_GRAPH[V].neighbor[opposite(dir)]
    rom.LD_A_n(0xFF); rom.LD_HL_A()

    rom.label('maze_prune_next_dir')
    rom.LD_A_nn(GW_MAZE_DIR); rom.CP_n(1); rom.JR_NZ('maze_prune_next_region')
    rom.LD_A_n(3); rom.LD_nn_A(GW_MAZE_DIR)
    rom.JP('maze_prune_dir')

    rom.label('maze_prune_next_region')
    rom.LD_A_nn(GW_BRAID_IDX); rom.INC_A(); rom.LD_nn_A(GW_BRAID_IDX)
    rom.LD_E_A()
    rom.LD_A_nn(GW_SCALE_SQ); _cp_e()
    rom.JP_NZ('maze_prune_region')
    rom.RET()

    # gw_neighbor_hl: on entry A=region index (0-80), C=direction (0=up,1=down,
    # 2=left,3=right). Returns HL -> REGION_GRAPH[region]'s neighbor byte for
    # that direction. Clobbers A, D, E; preserves C. Generalizes czt_region_hl's
    # addressing to an arbitrary region+direction rather than CUR_ZONE alone.
    # Reached only via CALL (from the maze pass above) -- never fallen into.
    rom.label('gw_neighbor_hl')
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(REGION_GRAPH)
    rom.ADD_HL_DE(); rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.ADD_HL_DE(); rom.ADD_HL_DE()   # HL = REGION_GRAPH + region*5 (biome byte)
    rom.INC_HL()                        # HL -> +1 (up slot, direction 0 base)
    rom.LD_A_C()
    rom.OR_A(); rom.JR_Z('gnh_done')            # dir 0 (up): already there
    rom.CP_n(1); rom.JR_NZ('gnh_try2')
    rom.INC_HL(); rom.JR('gnh_done')            # dir 1 (down)
    rom.label('gnh_try2')
    rom.CP_n(2); rom.JR_NZ('gnh_try3')
    rom.INC_HL(); rom.INC_HL(); rom.JR('gnh_done')   # dir 2 (left)
    rom.label('gnh_try3')
    rom.INC_HL(); rom.INC_HL(); rom.INC_HL()    # dir 3 (right, only case left)
    rom.label('gnh_done')
    rom.RET()

    # gw_maze_state_hl: on entry A=region index (0-80). Returns HL ->
    # GW_MAZE_STATE[region]. Clobbers A only. No page-cross: base low byte
    # 0xA0 + max index 80 (0x50) = 0xF0, stays within one page. Reached only
    # via CALL -- never fallen into.
    rom.label('gw_maze_state_hl')
    rom.ADD_A_n(GW_MAZE_STATE & 0xFF)
    rom.LD_L_A()
    rom.LD_H_n(GW_MAZE_STATE >> 8)
    rom.RET()

    # ── Infinite Mode: per-region materialization (IP-1101) ───────────────
    # inf_region_seed0: reseeds gw_prng_step's own state (TMP1:TMP2) to
    # hash(SEED, INF_MZ_TROW, INF_MZ_TCOL) -- SEED normalized 0->1 (mirrors
    # generate_world's own rule), XORed with the row then stepped once,
    # XORed with the col then stepped once (ADR-0016 point 3's "shift/XOR-
    # only per-region reseed" commitment, operationalized here). Leaves the
    # mixed state in TMP1:TMP2 for the caller's own subsequent draws.
    # Clobbers A, B (own scratch), D, E (gw_prng_step's own contract);
    # preserves C and HL.
    rom.label('inf_region_seed0')
    rom.LD_A_nn(SEED); rom.LD_nn_A(TMP2)
    rom.LD_A_nn(SEED + 1); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(TMP1); rom.OR_A(); rom.JR_NZ('irs0_seed_ok')
    rom.LD_A_nn(TMP2); rom.OR_A(); rom.JR_NZ('irs0_seed_ok')
    rom.LD_A_n(1); rom.LD_nn_A(TMP2)
    rom.label('irs0_seed_ok')
    rom.LD_A_nn(INF_MZ_TROW + 1); rom.LD_B_A()
    rom.LD_A_nn(TMP1); rom.XOR_B(); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(INF_MZ_TROW); rom.LD_B_A()
    rom.LD_A_nn(TMP2); rom.XOR_B(); rom.LD_nn_A(TMP2)
    rom.CALL('gw_prng_step')
    rom.LD_A_nn(INF_MZ_TCOL + 1); rom.LD_B_A()
    rom.LD_A_nn(TMP1); rom.XOR_B(); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(INF_MZ_TCOL); rom.LD_B_A()
    rom.LD_A_nn(TMP2); rom.XOR_B(); rom.LD_nn_A(TMP2)
    rom.CALL('gw_prng_step')
    rom.RET()

    # inf_mod5: A := A mod 5 (repeated-subtraction, no DIV/MUL -- NFR-2300,
    # generalizes gw_mod3's own established pattern, 3->5).
    rom.label('inf_mod5')
    rom.label('im5_loop')
    rom.CP_n(5); rom.JR_C('im5_done')
    rom.SUB_n(5); rom.JR('im5_loop')
    rom.label('im5_done')
    rom.RET()

    # inf_materialize_region: on entry, INF_MZ_ROW/INF_MZ_COL hold the
    # region to materialize (signed 16-bit each, caller-set). Produces a
    # biome-id + 4-direction connectivity nibble (Binary Tree maze, zero-
    # memory, ADR-0016 point 5) and a treasure-presence predicate, purely as
    # a function of (SEED, row, col) -- no read of DIV or any other
    # history-dependent input (NFR-2300).
    #
    # Own region: reseed once via inf_region_seed0, then draw three
    # sequential values from the resulting state -- biome, own carve-bias,
    # treasure-presence. Sequential, not three independent reseeds: an
    # earlier draft of this routine (matching this package's own planning
    # text) reseeded a *second* time for the treasure draw, but a second
    # reseed of the identical (SEED,row,col) reproduces the exact same
    # first-drawn byte, making treasure fully correlated with (not
    # independent of) the biome draw -- caught during implementation
    # (T22.d's own statistical-independence claim would have been false),
    # fixed here by drawing sequentially from one reseed instead, per this
    # skill's own material-drift discipline (a drift from the plan, not
    # from the shipped code, corrected in place rather than shipped wrong).
    #
    # Connectivity: this region's own carve-bias decides whether it opens
    # north or west; south/east openness is read from the south/east
    # neighbor's own carve-bias (one discarded "would-be biome" draw, one
    # kept carve-bias draw each) -- the neighbor on that side is the one
    # that "decides" the shared edge. No grid-boundary special case is ever
    # needed (Infinite Mode's world is unbounded -- every direction always
    # has a real, materializable neighbor), unlike the finite mode's own
    # bounded carve pass (IP-1070) -- confirms Open Question 4's resolution
    # (no spawn-region special case) is correct by construction, not just
    # asserted.
    rom.label('inf_materialize_region')
    rom.LD_A_nn(INF_MZ_ROW); rom.LD_nn_A(INF_MZ_TROW)
    rom.LD_A_nn(INF_MZ_ROW + 1); rom.LD_nn_A(INF_MZ_TROW + 1)
    rom.LD_A_nn(INF_MZ_COL); rom.LD_nn_A(INF_MZ_TCOL)
    rom.LD_A_nn(INF_MZ_COL + 1); rom.LD_nn_A(INF_MZ_TCOL + 1)
    rom.CALL('inf_region_seed0')
    rom.CALL('gw_prng_step')          # draw 1: biome
    rom.CALL('inf_mod5')
    rom.LD_nn_A(INF_MZ_BIOME)
    rom.CALL('gw_prng_step')          # draw 2: own carve-bias
    rom.AND_n(1)
    rom.LD_nn_A(INF_MZ_BIAS)
    rom.CALL('gw_prng_step')          # draw 3: treasure-presence
    rom.AND_n(0x0F)
    rom.LD_B_n(0)
    rom.CP_n(0); rom.JR_NZ('imr_no_treasure')
    rom.LD_B_n(1)
    rom.label('imr_no_treasure')
    rom.LD_A_B(); rom.LD_nn_A(INF_MZ_TREASURE)

    # South neighbor (row+1, col): reseed, draw 1 discarded, draw 2 (own
    # carve-bias) kept in C -- gw_prng_step/inf_region_seed0 both preserve
    # C, so it survives the east-neighbor section below.
    rom.LD_A_nn(INF_MZ_ROW); rom.LD_E_A()
    rom.LD_A_nn(INF_MZ_ROW + 1); rom.LD_D_A()
    rom.INC_DE()
    rom.LD_A_E(); rom.LD_nn_A(INF_MZ_TROW)
    rom.LD_A_D(); rom.LD_nn_A(INF_MZ_TROW + 1)
    rom.LD_A_nn(INF_MZ_COL); rom.LD_nn_A(INF_MZ_TCOL)
    rom.LD_A_nn(INF_MZ_COL + 1); rom.LD_nn_A(INF_MZ_TCOL + 1)
    rom.CALL('inf_region_seed0')
    rom.CALL('gw_prng_step')          # discard (that region's own biome)
    rom.CALL('gw_prng_step')          # keep: that region's own carve-bias
    rom.AND_n(1)
    rom.LD_C_A()                      # C = south_bias (open_south iff ==0)

    # East neighbor (row, col+1): reseed, draw 1 discarded, draw 2 kept in D.
    rom.LD_A_nn(INF_MZ_ROW); rom.LD_nn_A(INF_MZ_TROW)
    rom.LD_A_nn(INF_MZ_ROW + 1); rom.LD_nn_A(INF_MZ_TROW + 1)
    rom.LD_A_nn(INF_MZ_COL); rom.LD_E_A()
    rom.LD_A_nn(INF_MZ_COL + 1); rom.LD_D_A()
    rom.INC_DE()
    rom.LD_A_E(); rom.LD_nn_A(INF_MZ_TCOL)
    rom.LD_A_D(); rom.LD_nn_A(INF_MZ_TCOL + 1)
    rom.CALL('inf_region_seed0')
    rom.CALL('gw_prng_step')          # discard
    rom.CALL('gw_prng_step')          # keep: east neighbor's own carve-bias
    rom.AND_n(1)
    rom.LD_D_A()                      # D = east_bias (open_east iff ==1)

    # Compose the connectivity nibble (bit3=up/north, bit4=down/south,
    # bit5=left/west, bit6=right/east, 1=open) and pack with the biome-id.
    rom.LD_E_n(0)
    rom.LD_A_nn(INF_MZ_BIAS); rom.CP_n(0); rom.JR_NZ('imr_no_north')
    rom.LD_A_E(); rom.OR_n(0x08); rom.LD_E_A()
    rom.label('imr_no_north')
    rom.LD_A_nn(INF_MZ_BIAS); rom.CP_n(1); rom.JR_NZ('imr_no_west')
    rom.LD_A_E(); rom.OR_n(0x20); rom.LD_E_A()
    rom.label('imr_no_west')
    rom.LD_A_C(); rom.CP_n(0); rom.JR_NZ('imr_no_south')
    rom.LD_A_E(); rom.OR_n(0x10); rom.LD_E_A()
    rom.label('imr_no_south')
    rom.LD_A_D(); rom.CP_n(1); rom.JR_NZ('imr_no_east')
    rom.LD_A_E(); rom.OR_n(0x40); rom.LD_E_A()
    rom.label('imr_no_east')
    rom.LD_A_nn(INF_MZ_BIOME); rom.OR_E()
    rom.LD_nn_A(INF_MZ_RESULT)
    rom.RET()

    # ── inf_check_top_score (IP-1103, FR-10400) ───────────
    # The win-condition comparison subroutine. Inputs: none (reads
    # RUNNING_TREASURE_COUNT and TOP_SCORE_TABLE directly); clobbers A/B/D/E.
    # If RUNNING_TREASURE_COUNT strictly exceeds TOP_SCORE_TABLE's lowest
    # entry (index 2), inserts it at its sorted-descending position,
    # shifting lower entries down and displacing the previous lowest;
    # otherwise leaves the table byte-for-byte unchanged. Pure numeric
    # insertion -- no name-entry UI in this subroutine or any caller
    # (FR-10400's own explicit requirement).
    #
    # DELIBERATELY UNCALLED (IP-1103 §2/§6, FS-110 Open Question 3 /
    # BL-0112): no in-game event invokes this routine -- when the top-3
    # comparison fires during play is a decision FS-110 routes to
    # 04-requirements-engineering or a direct user decision, not to
    # implementation planning. A future package supplies the call site once
    # BL-0112 resolves; until then it is reachable only via the test
    # harness's direct-call mechanism (T26.c), exactly like generate_world
    # before IP-1040 wired its call site. T26.d asserts the zero-call-site
    # state so the future wiring shows up as a clean, detectable diff.
    #
    # 16-bit unsigned compare convention (little-endian, SEED's byte order):
    # compare high bytes first; only on equality compare low bytes.
    rom.label('inf_check_top_score')
    rom.LD_A_nn(RUNNING_TREASURE_COUNT); rom.LD_E_A()
    rom.LD_A_nn(RUNNING_TREASURE_COUNT + 1); rom.LD_D_A()
    # Qualify: DE > entry2 (lowest, TABLE+4/+5)? If not, return unchanged.
    rom.LD_A_nn(TOP_SCORE_TABLE + 5); rom.LD_B_A()
    rom.LD_A_D(); rom.CP_B(); rom.JR_C('icts_ret'); rom.JR_NZ('icts_q')
    rom.LD_A_nn(TOP_SCORE_TABLE + 4); rom.LD_B_A()
    rom.LD_A_E(); rom.CP_B(); rom.JR_C('icts_ret'); rom.JR_Z('icts_ret')
    rom.label('icts_q')
    # Qualified. DE > entry0 (TABLE+0/+1)? -> insert at index 0.
    rom.LD_A_nn(TOP_SCORE_TABLE + 1); rom.LD_B_A()
    rom.LD_A_D(); rom.CP_B(); rom.JR_C('icts_chk1'); rom.JR_NZ('icts_ins0')
    rom.LD_A_nn(TOP_SCORE_TABLE + 0); rom.LD_B_A()
    rom.LD_A_E(); rom.CP_B(); rom.JR_C('icts_chk1'); rom.JR_Z('icts_chk1')
    rom.label('icts_ins0')
    # entry2 = entry1; entry1 = entry0; entry0 = DE
    rom.LD_A_nn(TOP_SCORE_TABLE + 2); rom.LD_nn_A(TOP_SCORE_TABLE + 4)
    rom.LD_A_nn(TOP_SCORE_TABLE + 3); rom.LD_nn_A(TOP_SCORE_TABLE + 5)
    rom.LD_A_nn(TOP_SCORE_TABLE + 0); rom.LD_nn_A(TOP_SCORE_TABLE + 2)
    rom.LD_A_nn(TOP_SCORE_TABLE + 1); rom.LD_nn_A(TOP_SCORE_TABLE + 3)
    rom.LD_A_E(); rom.LD_nn_A(TOP_SCORE_TABLE + 0)
    rom.LD_A_D(); rom.LD_nn_A(TOP_SCORE_TABLE + 1)
    rom.RET()
    rom.label('icts_chk1')
    # DE > entry1 (TABLE+2/+3)? -> insert at index 1, else index 2.
    rom.LD_A_nn(TOP_SCORE_TABLE + 3); rom.LD_B_A()
    rom.LD_A_D(); rom.CP_B(); rom.JR_C('icts_ins2'); rom.JR_NZ('icts_ins1')
    rom.LD_A_nn(TOP_SCORE_TABLE + 2); rom.LD_B_A()
    rom.LD_A_E(); rom.CP_B(); rom.JR_C('icts_ins2'); rom.JR_Z('icts_ins2')
    rom.label('icts_ins1')
    # entry2 = entry1; entry1 = DE
    rom.LD_A_nn(TOP_SCORE_TABLE + 2); rom.LD_nn_A(TOP_SCORE_TABLE + 4)
    rom.LD_A_nn(TOP_SCORE_TABLE + 3); rom.LD_nn_A(TOP_SCORE_TABLE + 5)
    rom.LD_A_E(); rom.LD_nn_A(TOP_SCORE_TABLE + 2)
    rom.LD_A_D(); rom.LD_nn_A(TOP_SCORE_TABLE + 3)
    rom.RET()
    rom.label('icts_ins2')
    # entry2 = DE (displaces the previous lowest directly)
    rom.LD_A_E(); rom.LD_nn_A(TOP_SCORE_TABLE + 4)
    rom.LD_A_D(); rom.LD_nn_A(TOP_SCORE_TABLE + 5)
    rom.label('icts_ret')
    rom.RET()

    # ── inf_ledger_find (IP-1104) ──────────────────────────
    # Shared bounded search over the visited-region ledger's WRAM working
    # copy -- both inf_ensure_window's own cross-reference (above) and
    # inf_ledger_mark_collected (below) need "find the entry for the
    # current region, if any," so this is written once, not duplicated,
    # mirroring this codebase's own established "reuse, don't duplicate"
    # convention.
    #
    # Inputs: none (reads INF_ROW/INF_COL directly -- the current region's
    # own canonical WRAM location, always correctly set by every caller
    # before this routine runs).
    #
    # Outputs: Z set + HL = address of the matching entry's collected-flag
    # byte, if a matching (row, col) entry exists among LEDGER's first
    # LEDGER_COUNT entries. NZ + HL = LEDGER + LEDGER_COUNT*5 (the next
    # free append slot), if no match exists -- true whether LEDGER_COUNT
    # is 0 or the full search came up empty, since HL is advanced by
    # exactly 5 bytes per entry checked either way.
    #
    # Clobbers: A, B, D, E, H, L.
    rom.label('inf_ledger_find')
    rom.LD_DE_nn(5)
    rom.LD_HL_nn(LEDGER)
    rom.LD_A_nn(LEDGER_COUNT); rom.OR_A(); rom.JR_Z('ilf_notfound')
    rom.LD_B_A()
    rom.label('ilf_loop')
    rom.PUSH_HL()
    rom.LD_A_nn(INF_ROW); rom.emit(0xBE); rom.JR_NZ('ilf_miss')       # CP (HL): row lo
    rom.INC_HL()
    rom.LD_A_nn(INF_ROW + 1); rom.emit(0xBE); rom.JR_NZ('ilf_miss')   # row hi
    rom.INC_HL()
    rom.LD_A_nn(INF_COL); rom.emit(0xBE); rom.JR_NZ('ilf_miss')       # col lo
    rom.INC_HL()
    rom.LD_A_nn(INF_COL + 1); rom.emit(0xBE); rom.JR_NZ('ilf_miss')   # col hi
    # Match: Z still set from the last CP (INC_HL/POP_DE below don't
    # touch flags on SM83's 16-bit INC/POP).
    rom.INC_HL()                    # HL -> collected-flag byte
    rom.POP_DE()                    # discard the pushed entry-base (unused from here)
    rom.RET()
    rom.label('ilf_miss')
    rom.POP_HL()                    # restore HL = this entry's own base
    rom.ADD_HL_DE()                 # HL += 5 -> next entry base
    rom.DEC_B(); rom.JR_NZ('ilf_loop')
    rom.label('ilf_notfound')
    rom.OR_n(1)                     # force NZ regardless of A's prior value
    rom.RET()

    # ── inf_ledger_mark_collected (IP-1103 -> IP-1104 seam) ──
    # The ledger-write interface IP-1103's collection branch calls forward
    # into (IP-1103 §6/§12): marks the current region's treasure collected
    # in the visited-region ledger's WRAM working copy (IP-1104, amended
    # 2026-07-16 per BL-0119 -- operates on WRAM `LEDGER`, never touches
    # SRAM directly; no MBC1 bracket needed here, safe to call on every
    # collection). Uses inf_ledger_find (above) rather than re-deriving the
    # same search.
    rom.label('inf_ledger_mark_collected')
    rom.CALL('inf_ledger_find')
    rom.JR_NZ('ilmc_notfound')
    # Found: HL -> collected-flag byte. Set to 1 (idempotent if already 1
    # -- a second collision at an already-collected region is unreachable
    # in practice, since check_collisions clears INF_TREASURE_HERE/
    # deactivates the item on first collection, but setting unconditionally
    # is simpler and equally correct either way).
    rom.LD_A_n(1); rom.LD_HL_A()
    rom.RET()
    rom.label('ilmc_notfound')
    # HL = LEDGER + LEDGER_COUNT*5 (the next free append slot, per
    # inf_ledger_find's own contract).
    rom.LD_A_nn(LEDGER_COUNT); rom.CP_n(128); rom.JR_NC('ilmc_evict')
    # Append: write (row, col, collected=1) at HL; LEDGER_COUNT += 1.
    rom.LD_A_nn(INF_ROW); rom.LD_HLI_A()
    rom.LD_A_nn(INF_ROW + 1); rom.LD_HLI_A()
    rom.LD_A_nn(INF_COL); rom.LD_HLI_A()
    rom.LD_A_nn(INF_COL + 1); rom.LD_HLI_A()
    rom.LD_A_n(1); rom.LD_HL_A()
    rom.LD_A_nn(LEDGER_COUNT); rom.INC_A(); rom.LD_nn_A(LEDGER_COUNT)
    rom.RET()
    rom.label('ilmc_evict')
    # Full (LEDGER_COUNT == 128): FIFO-evict the entry at LEDGER_CURSOR --
    # HL = LEDGER + LEDGER_CURSOR*5, computed via five fixed ADD_HL_DE
    # steps (DE = cursor, 0-127, fits one byte) rather than a multiply
    # instruction (none exists on SM83) or a runtime loop -- a small fixed
    # unrolled sequence, this codebase's own established style (see
    # inf_ensure_window's own identical framing for its 9-cell unroll).
    rom.LD_A_nn(LEDGER_CURSOR); rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(LEDGER)
    rom.ADD_HL_DE(); rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.LD_A_nn(INF_ROW); rom.LD_HLI_A()
    rom.LD_A_nn(INF_ROW + 1); rom.LD_HLI_A()
    rom.LD_A_nn(INF_COL); rom.LD_HLI_A()
    rom.LD_A_nn(INF_COL + 1); rom.LD_HLI_A()
    rom.LD_A_n(1); rom.LD_HL_A()
    # Advance cursor modulo 128 (AND 0x7F, no DIV).
    rom.LD_A_nn(LEDGER_CURSOR); rom.INC_A(); rom.AND_n(0x7F)
    rom.LD_nn_A(LEDGER_CURSOR)
    rom.RET()

    # ── save_to_sram ─────────────────────────────────────
    rom.label('save_to_sram')
    rom.LD_A_n(0x0A); rom.LD_nn_A(0x0000)
    for addr, val in [(0xA000, 0x42), (0xA001, 0x55),
                      (0xA002, 0x4E), (0xA003, 0x59)]:
        rom.LD_A_n(val); rom.LD_nn_A(addr)
    for src, dst in [(CUR_ZONE, 0xA004), (PLAYER_X, 0xA005),
                     (PLAYER_Y, 0xA006), (CARROTS_COUNT, 0xA007),
                     (SCORE, 0xA008)]:
        rom.LD_A_nn(src); rom.LD_nn_A(dst)
    # Save 9 carrot flags A009..A011
    for i in range(9):
        rom.LD_A_nn(CARROT_FLAGS + i); rom.LD_nn_A(0xA009 + i)
    # FR-5220: save-format version guard
    rom.LD_A_n(SAVE_VERSION_VAL); rom.LD_nn_A(SAVE_VERSION_ADDR)
    # IP-9070: ScoreItem flags, generalized from a 9-byte per-byte loop to an
    # 81-byte memcpy (SCOREITEM_FLAGS widened the same way KEYITEM_FLAGS was
    # by IP-1050 — see immediately below).
    rom.LD_DE_nn(SCOREITEM_FLAGS); rom.LD_HL_nn(SRAM_SCOREITEM); rom.LD_BC_nn(81)
    rom.CALL('memcpy')
    # FR-9200 (IP-1050): SEED/WORLD_SCALE mirrors + KEYITEM_FLAGS mirror
    # (up to 81 bytes). REGION_GRAPH itself is never written here — it
    # regenerates from (SEED, WORLD_SCALE) on load (ADR-0009).
    rom.LD_A_nn(SEED);         rom.LD_nn_A(SRAM_SEED)
    rom.LD_A_nn(SEED + 1);     rom.LD_nn_A(SRAM_SEED + 1)
    rom.LD_A_nn(WORLD_SCALE);  rom.LD_nn_A(SRAM_WORLD_SCALE)
    rom.LD_DE_nn(KEYITEM_FLAGS); rom.LD_HL_nn(SRAM_KEYITEM_FLAGS); rom.LD_BC_nn(81)
    rom.CALL('memcpy')
    # IP-1104: Infinite Mode save shape (Workflow D). SRAM_GAME_MODE always
    # written (mirrors GAME_MODE unconditionally); the Infinite-Mode-only
    # fields below are gated on GAME_MODE == 1 -- when finite-mode saving,
    # left as whatever they last held, never read back unless GAME_MODE on
    # load says 1 (mirroring ADR-0010's own "unread fields are inert"
    # framing for the finite mode's own version-guard discipline).
    rom.LD_A_nn(GAME_MODE); rom.LD_nn_A(SRAM_GAME_MODE)
    rom.OR_A(); rom.JR_Z('sts_inf_skip')
    rom.LD_A_nn(INF_ROW); rom.LD_nn_A(SRAM_INF_ROW)
    rom.LD_A_nn(INF_ROW + 1); rom.LD_nn_A(SRAM_INF_ROW + 1)
    rom.LD_A_nn(INF_COL); rom.LD_nn_A(SRAM_INF_COL)
    rom.LD_A_nn(INF_COL + 1); rom.LD_nn_A(SRAM_INF_COL + 1)
    rom.LD_A_nn(RUNNING_TREASURE_COUNT); rom.LD_nn_A(SRAM_RUNNING_TREASURE_COUNT)
    rom.LD_A_nn(RUNNING_TREASURE_COUNT + 1); rom.LD_nn_A(SRAM_RUNNING_TREASURE_COUNT + 1)
    # Ledger block: single 642-byte memcpy (LEDGER_COUNT/LEDGER_CURSOR/
    # LEDGER -> their exact SRAM mirror, one contiguous transfer both sides
    # per the amendment's own mirror-layout design).
    rom.LD_DE_nn(LEDGER_COUNT); rom.LD_HL_nn(SRAM_LEDGER_COUNT); rom.LD_BC_nn(642)
    rom.CALL('memcpy')
    rom.label('sts_inf_skip')
    # TOP_SCORE_TABLE: always written, both modes -- the persistent high
    # score, distinct from per-run state (ADR-0017 point 4).
    for i in range(6):
        rom.LD_A_nn(TOP_SCORE_TABLE + i); rom.LD_nn_A(SRAM_TOP_SCORE_TABLE + i)
    rom.XOR_A(); rom.LD_nn_A(0x0000)
    rom.RET()

    # ── check_save_valid (IP-1040) ─────────────────────────
    # Read-only validity probe for MAIN MENU's option-set (FR-1170): checks
    # the magic bytes AND the version byte (ADR-0010: a version-mismatched
    # save is treated as absent for "continue" purposes — stricter than
    # try_load_save's own magic-only gate, which still loads a mismatched
    # save with ScoreItem restore skipped, IP-1010's shipped behavior,
    # unchanged). Writes no game-state field, only the cached MM_SAVE_VALID
    # flag — IP-9060 (BL-0048) removed this routine's own MM_CURSOR-reset
    # tail, which used to fire on every call (i.e. every MAIN MENU redraw,
    # including the player's own toggle), silently undoing it. The reset
    # itself moved to mm_on_entry, gated on a genuine state-entry flag.
    rom.label('check_save_valid')
    rom.LD_A_n(0x0A); rom.LD_nn_A(0x0000)
    for addr, val in [(0xA000,0x42),(0xA001,0x55),(0xA002,0x4E),(0xA003,0x59)]:
        rom.LD_A_nn(addr); rom.CP_n(val); rom.JR_NZ('csv_no')
    rom.LD_A_nn(SAVE_VERSION_ADDR); rom.CP_n(SAVE_VERSION_VAL); rom.JR_NZ('csv_no')
    rom.LD_A_n(1); rom.LD_nn_A(MM_SAVE_VALID)
    rom.JR('csv_done')
    rom.label('csv_no')
    rom.XOR_A(); rom.LD_nn_A(MM_SAVE_VALID)
    rom.label('csv_done')
    rom.XOR_A(); rom.LD_nn_A(0x0000)
    rom.RET()

    # ── try_load_save ─────────────────────────────────────
    rom.label('try_load_save')
    rom.LD_A_n(0x0A); rom.LD_nn_A(0x0000)
    for addr, val in [(0xA000,0x42),(0xA001,0x55),(0xA002,0x4E),(0xA003,0x59)]:
        rom.LD_A_nn(addr); rom.CP_n(val); rom.JP_NZ('tls_no')
    for dst, src in [(CUR_ZONE,0xA004),(PLAYER_X,0xA005),(PLAYER_Y,0xA006),
                     (CARROTS_COUNT,0xA007),(SCORE,0xA008)]:
        rom.LD_A_nn(src); rom.LD_nn_A(dst)
    for i in range(9):
        rom.LD_A_nn(0xA009 + i); rom.LD_nn_A(CARROT_FLAGS + i)
    # FR-5220: version-guarded ScoreItem restore. SCOREITEM_FLAGS is already
    # all-zero from the boot-time WRAM clear (this routine runs once right
    # after it) — a pre-upgrade save (version byte != SAVE_VERSION_VAL) is
    # handled by simply skipping the restore, leaving it at that all-zero
    # "uncollected" default rather than trusting garbage SRAM bytes.
    # IP-1050: this routine is now only reachable from MAIN MENU's
    # "continue" action once check_save_valid has already confirmed the
    # version matches — so this branch is never actually taken in normal
    # play (MM_SAVE_VALID gates it upstream) — kept as a defensive-correct
    # fallback matching tls_no's own precedent, not a live path.
    # JR->JP: this package's own additions push the version-mismatch skip
    # target out of JR's +-127 byte range (the same class of range issue
    # IP-1010's own JR->JP conversions hit first).
    rom.LD_A_nn(SAVE_VERSION_ADDR); rom.CP_n(SAVE_VERSION_VAL); rom.JP_NZ('tls_si_skip')
    # IP-9070: 81-byte memcpy, generalized from the old 9-byte per-byte loop
    # (SCOREITEM_FLAGS widened the same way KEYITEM_FLAGS was by IP-1050).
    rom.LD_DE_nn(SRAM_SCOREITEM); rom.LD_HL_nn(SCOREITEM_FLAGS); rom.LD_BC_nn(81)
    rom.CALL('memcpy')
    # FR-9200 (IP-1050): restore SEED/WORLD_SCALE, regenerate REGION_GRAPH
    # via IP-1020's generate_world (never persisted itself — ADR-0009's
    # determinism guarantee), then restore KEYITEM_FLAGS onto the
    # freshly-regenerated graph. generate_world touches only WRAM (SEED,
    # WORLD_SCALE, REGION_GRAPH, its own GW_* scratch) — harmless to call
    # while SRAM's MBC1 bank window is still enabled.
    rom.LD_A_nn(SRAM_SEED);        rom.LD_nn_A(SEED)
    rom.LD_A_nn(SRAM_SEED + 1);    rom.LD_nn_A(SEED + 1)
    rom.LD_A_nn(SRAM_WORLD_SCALE); rom.LD_nn_A(WORLD_SCALE)
    rom.CALL('generate_world')
    rom.LD_DE_nn(SRAM_KEYITEM_FLAGS); rom.LD_HL_nn(KEYITEM_FLAGS); rom.LD_BC_nn(81)
    rom.CALL('memcpy')
    # IP-1104: GAME_MODE-gated Infinite Mode restore (Workflow D). Only
    # reachable inside this version-matched branch -- SRAM_GAME_MODE and
    # every field below it are meaningless bytes in any earlier-version
    # save and are never read otherwise. The existing finite-mode restore
    # above (CUR_ZONE/PLAYER_X/PLAYER_Y/CARROTS_COUNT/SCORE/CARROT_FLAGS/
    # SCOREITEM_FLAGS/SEED/WORLD_SCALE/generate_world/KEYITEM_FLAGS) runs
    # exactly as before this package, unconditionally, for both modes --
    # deliberately not gated on GAME_MODE (this package's own scope is
    # additive, not a restructuring of already-`VERIFIED` finite-mode
    # code): for an Infinite Mode save these fields are simply never read
    # by any Infinite Mode code path (mirrors save_to_sram's own identical
    # "unread fields are inert" framing, applied symmetrically). Known,
    # named inefficiency: generate_world still runs once even when loading
    # an Infinite Mode save, though its REGION_GRAPH output is unused
    # there -- a few hundred wasted T-states, not a correctness issue, not
    # fixed here (out of this package's own named scope; see Implementation
    # Summary).
    rom.LD_A_nn(SRAM_GAME_MODE); rom.LD_nn_A(GAME_MODE)
    rom.OR_A(); rom.JR_Z('tls_inf_skip')
    rom.LD_A_nn(SRAM_INF_ROW); rom.LD_nn_A(INF_ROW)
    rom.LD_A_nn(SRAM_INF_ROW + 1); rom.LD_nn_A(INF_ROW + 1)
    rom.LD_A_nn(SRAM_INF_COL); rom.LD_nn_A(INF_COL)
    rom.LD_A_nn(SRAM_INF_COL + 1); rom.LD_nn_A(INF_COL + 1)
    rom.LD_A_nn(SRAM_RUNNING_TREASURE_COUNT); rom.LD_nn_A(RUNNING_TREASURE_COUNT)
    rom.LD_A_nn(SRAM_RUNNING_TREASURE_COUNT + 1); rom.LD_nn_A(RUNNING_TREASURE_COUNT + 1)
    rom.LD_DE_nn(SRAM_LEDGER_COUNT); rom.LD_HL_nn(LEDGER_COUNT); rom.LD_BC_nn(642)
    rom.CALL('memcpy')
    # Re-materialize the 3x3 working set around the restored position --
    # no region's biome/connectivity is ever itself persisted (FR-10500's
    # own explicit requirement); this call re-derives it, and (per the
    # BL-0119 amendment) also re-populates INF_TREASURE_HERE correctly
    # from the just-restored WRAM ledger via inf_ensure_window's own
    # cross-reference -- no separate restore-path lookup needed here.
    rom.CALL('inf_ensure_window')
    rom.label('tls_inf_skip')
    # TOP_SCORE_TABLE: always restored, both modes (persistent high score,
    # independent of GAME_MODE -- ADR-0017 point 4; save_to_sram writes it
    # unconditionally too).
    for i in range(6):
        rom.LD_A_nn(SRAM_TOP_SCORE_TABLE + i); rom.LD_nn_A(TOP_SCORE_TABLE + i)
    rom.label('tls_si_skip')
    rom.XOR_A(); rom.LD_nn_A(0x0000)
    rom.LD_A_n(GS_PLAYING)
    rom.LD_nn_A(GAMESTATE); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.RET()

    rom.label('tls_no')
    rom.XOR_A(); rom.LD_nn_A(0x0000)
    # IP-1040: try_load_save is now only called from MAIN MENU's "continue"
    # action (already gated on MM_SAVE_VALID) — this defensive fallback
    # returns to MAIN MENU rather than the retired TITLE state.
    rom.LD_A_n(GS_MAIN_MENU)
    rom.LD_nn_A(GAMESTATE); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.RET()

    return patches
