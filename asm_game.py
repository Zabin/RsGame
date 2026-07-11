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
                          # CARROT_FLAGS (IP-1020); only indices 0-8 are live until FEAT-1100
                          # wires up world generation, matching CUR_ZONE's current 0-8 range
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
OAM_BUF        = 0xC300

SAVE_VERSION_ADDR = 0xA012   # save-format version guard (FR-5220 / Design Decision 2)
SAVE_VERSION_VAL  = 0x03     # bumped 0x02->0x03 (IP-9070, third bump since ship — the
                              # value sequence is strictly monotonic, never reused)
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
    # clear KEYITEM_FLAGS (9 bytes — IP-1020, generalizes CARROT_FLAGS; only the
    # first 9 slots are live until FEAT-1100 wires up world generation)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.LD_B_n(9); rom.XOR_A()
    rom.label('si_clr'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('si_clr')
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
    # clear KEYITEM_FLAGS (9 bytes — IP-1020, generalizes CARROT_FLAGS; see st_intro)
    rom.LD_HL_nn(KEYITEM_FLAGS); rom.LD_B_n(9); rom.XOR_A()
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
    rom.LD_A_n(GS_SEED_SCALE_ENTRY); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
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
    rom.CALL('generate_world')
    rom.LD_A_n(GS_INTRO); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    rom.label('sse_redraw')
    rom.CALL('draw_sse_digits')
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
    rom.LD_A_n(GS_MAP); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()
    rom.label('hpi_no_sel')

    rom.LD_A_nn(JOY_CUR); rom.LD_B_A()
    rom.XOR_A(); rom.LD_nn_A(TMP1)

    # RIGHT
    rom.BIT_b_B(J_RIGHT); rom.JR_Z('mv_nr')
    rom.LD_A_nn(PLAYER_X); rom.INC_A()
    rom.CP_n(160); rom.JR_NC('mv_skip_r')
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
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(17); rom.JR_C('mv_skip_u')
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

    # |player_x - E| < 10
    rom.LD_A_nn(PLAYER_X); rom.SUB_E()
    rom.JR_NC('cc_dx_p'); rom.CPL(); rom.INC_A()
    rom.label('cc_dx_p'); rom.CP_n(10); rom.JR_NC('cc_skip')

    # |player_y - D| < 10
    rom.LD_A_nn(PLAYER_Y); rom.SUB_D()
    rom.JR_NC('cc_dy_p'); rom.CPL(); rom.INC_A()
    rom.label('cc_dy_p'); rom.CP_n(10); rom.JR_NC('cc_skip')

    # HIT — deactivate
    rom.POP_HL(); rom.XOR_A(); rom.LD_HL_A(); rom.INC_HL()

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

    rom.POP_BC(); rom.DEC_B(); rom.JP_NZ('cc_loop'); rom.RET()

    rom.label('cc_skip')
    rom.POP_HL(); rom.INC_HL()
    rom.POP_BC(); rom.DEC_B(); rom.JP_NZ('cc_loop'); rom.RET()

    # ── check_zone_transition ────────────────────────────
    rom.label('check_zone_transition')
    # right edge: x >= 156
    rom.LD_A_nn(PLAYER_X); rom.CP_n(156); rom.JR_C('czt_left')
    rom.LD_A_nn(CUR_ZONE)
    rom.CP_n(2); rom.JR_Z('czt_left')
    rom.CP_n(5); rom.JR_Z('czt_left')
    rom.CP_n(8); rom.JR_Z('czt_left')
    rom.INC_A(); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(8); rom.LD_nn_A(PLAYER_X)
    rom.JP('czt_redraw')

    rom.label('czt_left')
    rom.LD_A_nn(PLAYER_X); rom.OR_A(); rom.JR_NZ('czt_top')
    rom.LD_A_nn(CUR_ZONE)
    rom.OR_A(); rom.RET_Z()
    rom.CP_n(3); rom.RET_Z()
    rom.CP_n(6); rom.RET_Z()
    rom.DEC_A(); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(150); rom.LD_nn_A(PLAYER_X)
    rom.JP('czt_redraw')

    rom.label('czt_top')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(18); rom.JR_NC('czt_bot')
    rom.LD_A_nn(CUR_ZONE)
    rom.CP_n(3); rom.RET_C()
    rom.SUB_n(3); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(120); rom.LD_nn_A(PLAYER_Y)
    rom.JP('czt_redraw')

    rom.label('czt_bot')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(128); rom.RET_C()
    rom.LD_A_nn(CUR_ZONE)
    rom.CP_n(6); rom.RET_NC()
    rom.ADD_A_n(3); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(24); rom.LD_nn_A(PLAYER_Y)

    rom.label('czt_redraw')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    # ── check_complete ───────────────────────────────────
    rom.label('check_complete')
    rom.LD_A_nn(CARROTS_COUNT); rom.CP_n(9); rom.RET_NZ()
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
                    (GS_MAIN_MENU,'dsr_mm'),(GS_SEED_SCALE_ENTRY,'dsr_sse')]:
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

    # PLAYING: biome-family screen dispatch (IP-1030, generalizes the
    # former fixed 9-entry zs_table). CUR_ZONE is read as the current
    # region index into REGION_GRAPH (5 bytes/region: biome-id, then 4
    # neighbor-index bytes in up/down/left/right order — GDS-07 §6,
    # matching generate_world's own write order exactly).
    rom.label('dsr_p')
    rom.LD_A_nn(CUR_ZONE)
    rom.LD_E_A(); rom.LD_D_n(0)        # DE = region index
    rom.LD_HL_nn(REGION_GRAPH)
    rom.ADD_HL_DE(); rom.ADD_HL_DE(); rom.ADD_HL_DE()
    rom.ADD_HL_DE(); rom.ADD_HL_DE()   # HL = REGION_GRAPH + region*5 (16-bit,
                                        # correct up to scale=9's 81 regions)
    rom.LD_A_HLI()                     # A = biome-id (0..4); HL -> 'up' byte
    rom.PUSH_HL()                      # save neighbor-byte pointer across CALLs

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
    rom.POP_HL()                       # HL -> 'up' neighbor byte, restored
    rom.CALL('draw_region_arrows')
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
    ARROW_ADDR_R = 0x9800 + 9*32 + (32-2)

    def _arrow_write(addr, tile):
        rom.XOR_A(); rom.LDH_n_A(VBK)
        rom.LD_A_n(tile); rom.LD_HL_nn(addr); rom.LD_HL_A()
        rom.LD_A_n(1); rom.LDH_n_A(VBK)
        rom.LD_A_n(2); rom.LD_HL_nn(addr); rom.LD_HL_A()   # palette 2, matching
                                                             # _zone_arrows' original
        rom.XOR_A(); rom.LDH_n_A(VBK)

    rom.label('draw_region_arrows')
    rom.LD_A_HLI(); rom.LD_B_A()       # B = up
    rom.LD_A_HLI(); rom.LD_C_A()       # C = down
    rom.LD_A_HLI(); rom.LD_D_A()       # D = left
    rom.LD_A_HL();  rom.LD_E_A()       # E = right

    rom.LD_A_B(); rom.CP_n(0xFF); rom.JR_Z('dra_no_up')
    _arrow_write(ARROW_ADDR_U, TL_ARROW_U)
    rom.label('dra_no_up')
    rom.LD_A_C(); rom.CP_n(0xFF); rom.JR_Z('dra_no_down')
    _arrow_write(ARROW_ADDR_D, TL_ARROW_D)
    rom.label('dra_no_down')
    rom.LD_A_D(); rom.CP_n(0xFF); rom.JR_Z('dra_no_left')
    _arrow_write(ARROW_ADDR_L, TL_ARROW_L)
    rom.label('dra_no_left')
    rom.LD_A_E(); rom.CP_n(0xFF); rom.JR_Z('dra_no_right')
    _arrow_write(ARROW_ADDR_R, TL_ARROW_R)
    rom.label('dra_no_right')
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

    # ── setup_zone_collects ───────────────────────────────
    # IP-9070: zc_table is now indexed by REGION_GRAPH's biome-id (0-4, the
    # 5 biome-family-representative lists) instead of CUR_ZONE directly (a
    # 9-entry-only ROM table could not survive CUR_ZONE values above 8, which
    # IP-9050 makes reachable) -- mirrors dsr_p's own REGION_GRAPH read
    # exactly (same region*5 addressing, same biome-id byte position).
    rom.label('setup_zone_collects')
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

    rom.label('gw_prng_step')
    # 16-bit xorshift-style state in TMP1:TMP2 (hi:lo). Shift+XOR only, no
    # multiply/divide (NFR-2200): x ^= x<<1; x ^= x>>1; x ^= byteswap(x).
    rom.LD_A_nn(TMP2); rom.SLA_A(); rom.LD_E_A()
    rom.LD_A_nn(TMP1); rom.RLA(); rom.LD_D_A()
    rom.LD_A_nn(TMP2); _xor_e(); rom.LD_nn_A(TMP2)
    rom.LD_A_nn(TMP1); _xor_d(); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(TMP1); rom.SRL_A(); rom.LD_D_A()
    rom.LD_A_nn(TMP2); rom.RRA(); rom.LD_E_A()
    rom.LD_A_nn(TMP1); _xor_d(); rom.LD_nn_A(TMP1)
    rom.LD_A_nn(TMP2); _xor_e(); rom.LD_nn_A(TMP2)
    rom.LD_A_nn(TMP1); rom.LD_D_A()
    rom.LD_A_nn(TMP2); _xor_d()
    rom.LD_nn_A(TMP1); rom.LD_nn_A(TMP2)
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
    rom.LD_A_nn(SAVE_VERSION_ADDR); rom.CP_n(SAVE_VERSION_VAL); rom.JR_NZ('tls_si_skip')
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
