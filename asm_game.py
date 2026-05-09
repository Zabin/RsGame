"""
asm_game.py — SM83 game logic for Bunny Garden Adventure.
Call build_game_asm(rom) to emit all code starting at 0x0150.
Returns a dict of patch-point addresses that build_rom.py must fill in.
"""
from gbc_lib import ROM
from tiles import TL_BUNNY_T_F1, TL_GIFT, TL_STAR, TL_FLOWER_OBJ
from tiles import TL_HEART_FULL, TL_HEART_EMPTY, TL_DIGIT_0

# ── WRAM addresses ──────────────────────────────────────────────────────────
GAMESTATE    = 0xC000   # 0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY
PLAYER_X     = 0xC001   # pixel x (0-159)
PLAYER_Y     = 0xC002   # pixel y (16-143)
PLAYER_DIR   = 0xC003   # 0=right 1=left
PLAYER_FRAME = 0xC004   # 0 or 1
ANIM_CTR     = 0xC005   # animation frame counter
SCORE        = 0xC006   # 0-99
SCORE_DIRTY  = 0xC007   # 1=needs redisplay
CUR_ZONE     = 0xC008   # 0=garden 1=forest 2=meadow
GIFTS        = 0xC009   # bitfield: bit0=zone0 bit1=zone1 bit2=zone2
NEED_REDRAW  = 0xC00A   # 1=full screen reload next frame
TRANSITION_TO= 0xC00B   # next GAMESTATE when NEED_REDRAW fires
JOY_CUR      = 0xC00C   # current joypad (active HIGH, see bit map below)
JOY_PREV     = 0xC00D   # previous frame joypad
JOY_NEW      = 0xC00E   # newly-pressed = JOY_CUR & ~JOY_PREV
MUSIC_CTR    = 0xC00F   # frames until next note
MUSIC_PTR_LO = 0xC010   # ROM ptr to current music byte (lo)
MUSIC_PTR_HI = 0xC011   # ROM ptr to current music byte (hi)
VBLANK_FLAG  = 0xC012   # set by ISR, cleared by main loop
TMP1         = 0xC013   # scratch
TMP2         = 0xC014   # scratch
COLL_DATA    = 0xC020   # array of (x,y,type,active) — 4 bytes each, up to 9
COLL_COUNT   = 0xC050   # number of entries in COLL_DATA
GIFTS_HI     = 0xC015   # high byte for 9th zone gift (zones 0-7 in GIFTS, zone 8 in GIFTS_HI bit0)
OAM_BUF      = 0xC300   # shadow OAM (160 bytes), DMA'd each VBlank

# Joypad bit positions in JOY_CUR (active HIGH after read_joypad)
J_A=0; J_B=1; J_SELECT=2; J_START=3; J_RIGHT=4; J_LEFT=5; J_UP=6; J_DOWN=7

# ── IO register offsets (from 0xFF00) ──────────────────────────────────────
P1=0x00; NR11=0x11; NR12=0x12; NR13=0x13; NR14=0x14
NR50=0x24; NR51=0x25; NR52=0x26
LCDC=0x40; LY=0x44; DMA=0x46; VBK=0x4F; BCPS=0x68; BCPD=0x69; OCPS=0x6A; OCPD=0x6B

HRAM_DMA = 0xFF80   # tiny DMA-wait routine lives here

# ── Game state IDs ──────────────────────────────────────────────────────────
GS_TITLE, GS_INTRO, GS_PLAYING, GS_SAVE, GS_MAP, GS_VICTORY = 0, 1, 2, 3, 4, 5


def build_game_asm(rom: ROM) -> dict:
    """
    Emit all game code into rom starting at 0x0150.
    Returns dict of patch-point addresses (to be written by build_rom.py).
    """
    patches = {}

    # ── RST vectors 0x0000-0x003F — all RETI ──────────────────────────────
    for a in range(0x0000, 0x0040):
        rom.data[a] = 0xD9

    # ── VBlank ISR at 0x0040 ───────────────────────────────────────────────
    rom.seek(0x0040)
    rom.PUSH_AF()
    rom.LD_A_n(1); rom.LD_nn_A(VBLANK_FLAG)
    rom.POP_AF(); rom.RETI()

    # Other ISRs — RETI
    for a in (0x0048, 0x0050, 0x0058, 0x0060):
        rom.seek(a); rom.RETI()

    # ── Entry point at 0x0100 ─────────────────────────────────────────────
    rom.seek(0x0100)
    rom.NOP(); rom.JP('main')

    # ── MAIN ─────────────────────────────────────────────────────────────
    rom.seek(0x0150)
    rom.label('main')
    rom.LD_SP_nn(0xFFFE)
    rom.DI()

    # Wait for VBlank, disable LCD so we can safely write VRAM
    rom.label('wv1')
    rom.LDH_A_n(LY); rom.CP_n(144); rom.JR_C('wv1')
    rom.XOR_A(); rom.LDH_n_A(LCDC)

    # Clear WRAM C000-C2FF (768 bytes)
    rom.LD_HL_nn(0xC000); rom.LD_BC_nn(0x0300); rom.XOR_A()
    rom.label('cw'); rom.LD_HLI_A(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cw')

    # Clear shadow OAM
    rom.LD_HL_nn(OAM_BUF); rom.LD_B_n(160); rom.XOR_A()
    rom.label('coam'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('coam')

    # Clear VRAM bank 1 (BG attribute map; prevents stale BG-OAM priority bits hiding sprites)
    rom.LD_A_n(1); rom.LDH_n_A(VBK)
    rom.LD_HL_nn(0x8000); rom.LD_BC_nn(0x2000); rom.XOR_A()
    rom.label('cv1'); rom.LD_HLI_A(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cv1')

    # Clear VRAM bank 0 (tile data + tilemap)
    rom.XOR_A(); rom.LDH_n_A(VBK)
    rom.LD_HL_nn(0x8000); rom.LD_BC_nn(0x2000); rom.XOR_A()
    rom.label('cv'); rom.LD_HLI_A(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cv')

    # Copy tile data → 0x8000
    rom.LD_DE_nn(0); patches['tile_src'] = rom.pos - 2
    rom.LD_HL_nn(0x8000); rom.LD_BC_nn(256 * 16)
    rom.CALL('memcpy')

    # Load BG palettes
    rom.LD_A_n(0x80); rom.LDH_n_A(BCPS)
    rom.LD_DE_nn(0); patches['bg_pal'] = rom.pos - 2
    rom.LD_B_n(64)
    rom.label('bgp')
    rom.LD_A_DE(); rom.LDH_n_A(BCPD); rom.INC_DE(); rom.DEC_B()
    rom.JR_NZ('bgp')

    # Load OBJ palettes
    rom.LD_A_n(0x80); rom.LDH_n_A(OCPS)
    rom.LD_DE_nn(0); patches['obj_pal'] = rom.pos - 2
    rom.LD_B_n(64)
    rom.label('obp')
    rom.LD_A_DE(); rom.LDH_n_A(OCPD); rom.INC_DE(); rom.DEC_B()
    rom.JR_NZ('obp')

    # Install DMA-wait routine in HRAM (6 bytes: LD A,40; DEC A; JR NZ,-1; RET)
    rom.LD_HL_nn(HRAM_DMA)
    for b in [0x3E, 40, 0x3D, 0x20, 0xFD, 0xC9]:
        rom.LD_A_n(b); rom.LD_HLI_A()

    # Init sound
    rom.LD_A_n(0x80); rom.LDH_n_A(NR52)
    rom.LD_A_n(0x77); rom.LDH_n_A(NR50)
    rom.LD_A_n(0xFF); rom.LDH_n_A(NR51)
    rom.LD_A_n(0x80); rom.LDH_n_A(NR11)   # 50% duty square
    rom.LD_A_n(0xF0); rom.LDH_n_A(NR12)   # initial volume 0xF, envelope period 0 (no decay)

    # Init music pointer (patched by build_rom.py)
    rom.LD_A_n(0); patches['mus_lo'] = rom.pos - 1
    rom.LD_nn_A(MUSIC_PTR_LO)
    rom.LD_A_n(0); patches['mus_hi'] = rom.pos - 1
    rom.LD_nn_A(MUSIC_PTR_HI)
    rom.LD_A_n(1); rom.LD_nn_A(MUSIC_CTR)

    # Try to load a battery save (sets state to PLAYING if valid)
    rom.CALL('try_load_save')

    # Enable LCD: 0x93 = LCD on, BG map 0x9800, tile data 0x8000, OBJ on, BG on
    rom.LD_A_n(0x93); rom.LDH_n_A(LCDC)
    rom.LD_A_n(0x01); rom.LD_nn_A(0xFFFF)   # enable VBlank interrupt only
    rom.EI()

    # ── MAIN GAME LOOP ───────────────────────────────────────────────────
    rom.label('game_loop')
    rom.HALT()
    rom.LD_A_nn(VBLANK_FLAG); rom.OR_A()
    rom.JR_Z('game_loop')
    rom.XOR_A(); rom.LD_nn_A(VBLANK_FLAG)

    # OAM DMA must happen early in VBlank, before any heavy operations
    rom.CALL('do_dma')

    # Full screen redraw if flagged
    rom.LD_A_nn(NEED_REDRAW); rom.OR_A()
    rom.CALL_NZ('do_screen_redraw')

    rom.CALL('read_joypad')

    # State dispatch
    rom.LD_A_nn(GAMESTATE)
    rom.CP_n(GS_TITLE);   rom.JP_Z('st_title')
    rom.CP_n(GS_INTRO);   rom.JP_Z('st_intro')
    rom.CP_n(GS_PLAYING); rom.JP_Z('st_playing')
    rom.CP_n(GS_SAVE);    rom.JP_Z('st_save')
    rom.CP_n(GS_MAP);     rom.JP_Z('st_map')
    rom.CP_n(GS_VICTORY); rom.JP_Z('st_victory')
    rom.JP('end_frame')

    # ── State: TITLE ─────────────────────────────────────────────────────
    rom.label('st_title')
    rom.LD_A_nn(JOY_NEW); rom.AND_n((1<<J_A)|(1<<J_START))
    rom.JP_Z('end_frame')
    rom.LD_A_n(GS_INTRO); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: INTRO ─────────────────────────────────────────────────────
    rom.label('st_intro')
    rom.LD_A_nn(JOY_NEW); rom.AND_n(1 << J_A)
    rom.JP_Z('end_frame')
    rom.XOR_A()
    rom.LD_nn_A(GIFTS); rom.LD_nn_A(SCORE); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(76); rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(72); rom.LD_nn_A(PLAYER_Y)
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: PLAYING ───────────────────────────────────────────────────
    rom.label('st_playing')
    rom.CALL('handle_play_input')
    rom.LD_A_nn(NEED_REDRAW); rom.OR_A()   # START/SELECT set this; skip physics
    rom.JP_NZ('end_frame')
    rom.CALL('check_collisions')
    rom.CALL('check_zone_transition')
    rom.CALL('check_complete')
    rom.CALL('update_score_disp')
    rom.JP('end_frame')

    # ── State: SAVE ──────────────────────────────────────────────────────
    rom.label('st_save')
    rom.LD_A_nn(JOY_NEW); rom.LD_B_A()
    rom.BIT_b_B(J_A); rom.JR_Z('sv_b')
    rom.CALL('save_to_sram')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')
    rom.label('sv_b')
    rom.BIT_b_B(J_B); rom.JP_Z('end_frame')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: MAP ───────────────────────────────────────────────────────
    rom.label('st_map')
    rom.LD_A_nn(JOY_NEW); rom.AND_n((1<<J_B)|(1<<J_SELECT))
    rom.JP_Z('end_frame')
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.JP('end_frame')

    # ── State: VICTORY ───────────────────────────────────────────────────
    rom.label('st_victory')
    rom.LD_A_nn(JOY_NEW); rom.AND_n((1<<J_A)|(1<<J_START))
    rom.JP_Z('end_frame')
    rom.LD_A_n(GS_TITLE); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.XOR_A(); rom.LD_nn_A(GIFTS); rom.LD_nn_A(SCORE)
    rom.JP('end_frame')

    # ── End of frame: update OAM, hearts, music ──────────────────────────
    rom.label('end_frame')
    rom.CALL('update_oam')
    rom.CALL('update_hearts')
    rom.CALL('music_tick')
    rom.JP('game_loop')

    # ====================================================================
    # SUBROUTINES
    # ====================================================================

    # ── memcpy: copy BC bytes from DE → HL ───────────────────────────────
    rom.label('memcpy')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('memcpy')
    rom.RET()

    # ── do_dma: OAM DMA transfer + HRAM wait ─────────────────────────────
    rom.label('do_dma')
    rom.LD_A_n(OAM_BUF >> 8); rom.LDH_n_A(DMA)
    rom.CALL(HRAM_DMA); rom.RET()

    # ── read_joypad ───────────────────────────────────────────────────────
    # Result in JOY_CUR: bit 0=A 1=B 2=SEL 3=START 4=RIGHT 5=LEFT 6=UP 7=DOWN
    rom.label('read_joypad')
    rom.LD_A_nn(JOY_CUR); rom.LD_nn_A(JOY_PREV)

    # Select buttons (P1 bit4=0): low nibble = A,B,SEL,START (active low)
    rom.LD_A_n(0x10); rom.LDH_n_A(P1)
    rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1)
    rom.AND_n(0x0F); rom.LD_B_A()                # B = button nibble

    # Select d-pad (P1 bit5=0): low nibble = RIGHT,LEFT,UP,DOWN (active low)
    rom.LD_A_n(0x20); rom.LDH_n_A(P1)
    rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1)
    rom.AND_n(0x0F); rom.SWAP_A()                # d-pad → high nibble
    rom.OR_B()                                    # combine
    rom.CPL()                                     # invert: 1 = pressed
    rom.LD_nn_A(JOY_CUR)

    rom.LD_A_n(0x30); rom.LDH_n_A(P1)           # deselect both

    # JOY_NEW = JOY_CUR & ~JOY_PREV
    rom.LD_A_nn(JOY_PREV); rom.CPL(); rom.LD_B_A()
    rom.LD_A_nn(JOY_CUR);  rom.AND_B()
    rom.LD_nn_A(JOY_NEW)
    rom.RET()

    # ── handle_play_input ────────────────────────────────────────────────
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

    # D-pad (held — use JOY_CUR)
    rom.LD_A_nn(JOY_CUR); rom.LD_B_A()
    rom.XOR_A(); rom.LD_nn_A(TMP1)        # moving flag

    rom.BIT_b_B(J_RIGHT); rom.JR_Z('mv_nr')
    rom.LD_A_nn(PLAYER_X); rom.INC_A()
    rom.CP_n(160); rom.JR_NC('mv_skip_r')
    rom.LD_nn_A(PLAYER_X)
    rom.label('mv_skip_r')
    rom.XOR_A(); rom.LD_nn_A(PLAYER_DIR)
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nr')

    rom.BIT_b_B(J_LEFT); rom.JR_Z('mv_nl')
    rom.LD_A_nn(PLAYER_X); rom.OR_A(); rom.JR_Z('mv_nl')
    rom.DEC_A(); rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(1); rom.LD_nn_A(PLAYER_DIR)
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nl')

    rom.BIT_b_B(J_UP); rom.JR_Z('mv_nu')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(17); rom.JR_C('mv_skip_u')
    rom.JR_Z('mv_skip_u'); rom.DEC_A(); rom.LD_nn_A(PLAYER_Y)
    rom.label('mv_skip_u')
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nu')

    rom.BIT_b_B(J_DOWN); rom.JR_Z('mv_nd')
    rom.LD_A_nn(PLAYER_Y); rom.INC_A()
    rom.CP_n(129); rom.JR_NC('mv_skip_d')
    rom.LD_nn_A(PLAYER_Y)
    rom.label('mv_skip_d')
    rom.LD_A_n(1); rom.LD_nn_A(TMP1)
    rom.label('mv_nd')

    # Walking animation
    rom.LD_A_nn(TMP1); rom.OR_A(); rom.JR_Z('mv_done')
    rom.LD_A_nn(ANIM_CTR); rom.INC_A()
    rom.CP_n(10); rom.JR_C('mv_save')
    rom.XOR_A(); rom.LD_nn_A(ANIM_CTR)
    rom.LD_A_nn(PLAYER_FRAME); rom.XOR_n(1); rom.LD_nn_A(PLAYER_FRAME)
    rom.RET()
    rom.label('mv_save'); rom.LD_nn_A(ANIM_CTR)
    rom.label('mv_done'); rom.RET()

    # ── check_collisions ─────────────────────────────────────────────────
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

    # Hit! Deactivate.
    rom.POP_HL(); rom.XOR_A(); rom.LD_HL_A(); rom.INC_HL()

    # If gift (type 2): set bit for CUR_ZONE in GIFTS (or GIFTS_HI for zone 8)
    rom.LD_A_C(); rom.CP_n(2); rom.JR_NZ('cc_not_g')
    rom.LD_A_nn(CUR_ZONE); rom.CP_n(8); rom.JR_NZ('cc_gift_lo')
    # Zone 8: set bit in GIFTS_HI
    rom.LD_A_nn(GIFTS_HI); rom.OR_n(1); rom.LD_nn_A(GIFTS_HI); rom.JR('cc_not_g')
    # Zones 0-7: set bit in GIFTS
    rom.label('cc_gift_lo')
    rom.LD_A_n(1); rom.LD_C_A()           # mask starts at 1
    rom.LD_A_nn(CUR_ZONE); rom.OR_A(); rom.JR_Z('cc_mask_done')
    rom.LD_D_A()
    rom.label('cc_msl')
    rom.LD_A_C(); rom.ADD_A_A(); rom.LD_C_A(); rom.DEC_D()
    rom.JR_NZ('cc_msl')
    rom.label('cc_mask_done')
    rom.LD_A_nn(GIFTS); rom.OR_C(); rom.LD_nn_A(GIFTS)
    rom.label('cc_not_g')

    # Score++
    rom.LD_A_nn(SCORE); rom.INC_A()
    rom.CP_n(100); rom.JR_C('cc_so'); rom.LD_A_n(99)
    rom.label('cc_so'); rom.LD_nn_A(SCORE)
    rom.LD_A_n(1); rom.LD_nn_A(SCORE_DIRTY)

    rom.POP_BC(); rom.DEC_B(); rom.JR_NZ('cc_loop'); rom.RET()

    rom.label('cc_skip')
    rom.POP_HL(); rom.INC_HL()
    rom.POP_BC(); rom.DEC_B(); rom.JR_NZ('cc_loop'); rom.RET()

    # ── check_zone_transition (3×3 grid navigation) ───────────────────────
    rom.label('check_zone_transition')
    # Check RIGHT (X >= 156): move to (row, col+1) if col < 2
    rom.LD_A_nn(PLAYER_X); rom.CP_n(156)
    rom.JR_C('czt_check_left')
    rom.LD_A_nn(CUR_ZONE); rom.LD_B_A()
    rom.LD_A_B(); rom.AND_n(3); rom.CP_n(2); rom.JR_NC('czt_check_left')
    rom.LD_A_B(); rom.INC_A(); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(8); rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    # Check LEFT (X = 0): move to (row, col-1) if col > 0
    rom.label('czt_check_left')
    rom.LD_A_nn(PLAYER_X); rom.OR_A(); rom.JR_NZ('czt_check_down')
    rom.LD_A_nn(CUR_ZONE); rom.LD_B_A()
    rom.LD_A_B(); rom.AND_n(3); rom.JR_Z('czt_check_down')
    rom.LD_A_B(); rom.DEC_A(); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(150); rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    # Check DOWN (Y >= 110): move to (row+1, col) if row < 2
    rom.label('czt_check_down')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(110)
    rom.JR_C('czt_check_up')
    rom.LD_A_nn(CUR_ZONE); rom.LD_B_A()
    rom.LD_A_B(); rom.SRL_A(); rom.SRL_A(); rom.CP_n(2); rom.JR_NC('czt_check_up')
    rom.LD_A_B(); rom.ADD_A_n(3); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(32); rom.LD_nn_A(PLAYER_Y)
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    # Check UP (Y < 50): move to (row-1, col) if row > 0
    rom.label('czt_check_up')
    rom.LD_A_nn(PLAYER_Y); rom.CP_n(50)
    rom.JR_NC('czt_done')
    rom.LD_A_nn(CUR_ZONE); rom.LD_B_A()
    rom.LD_A_B(); rom.SRL_A(); rom.SRL_A(); rom.RET_Z()
    rom.LD_A_B(); rom.SUB_n(3); rom.LD_nn_A(CUR_ZONE)
    rom.LD_A_n(110); rom.LD_nn_A(PLAYER_Y)
    rom.LD_A_n(GS_PLAYING); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    rom.label('czt_done')

    # ── check_complete (all 9 zones) ──────────────────────────────────────
    rom.label('check_complete')
    rom.LD_A_nn(GIFTS); rom.CP_n(0xFF); rom.RET_NZ()
    rom.LD_A_nn(GIFTS_HI); rom.AND_n(1); rom.RET_Z()
    rom.LD_A_n(GS_VICTORY); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW); rom.RET()

    # ── update_oam ───────────────────────────────────────────────────────
    rom.label('update_oam')
    rom.LD_HL_nn(OAM_BUF); rom.LD_B_n(160); rom.XOR_A()
    rom.label('uo_clr'); rom.LD_HLI_A(); rom.DEC_B(); rom.JR_NZ('uo_clr')

    rom.LD_A_nn(GAMESTATE); rom.CP_n(GS_PLAYING); rom.RET_NZ()

    # Bunny: head OAM entry
    rom.LD_HL_nn(OAM_BUF)
    rom.LD_A_nn(PLAYER_Y); rom.ADD_A_n(16); rom.LD_HLI_A()   # Y
    rom.LD_A_nn(PLAYER_X); rom.ADD_A_n(8);  rom.LD_HLI_A()   # X
    rom.LD_A_nn(PLAYER_FRAME); rom.ADD_A_A(); rom.LD_HLI_A() # tile (0 or 2)
    rom.LD_A_nn(PLAYER_DIR)
    rom.RRCA(); rom.RRCA(); rom.RRCA(); rom.AND_n(0x20)       # dir→x-flip
    rom.LD_HLI_A()                                            # attr

    # Bunny: body OAM entry
    rom.LD_A_nn(PLAYER_Y); rom.ADD_A_n(24); rom.LD_HLI_A()
    rom.LD_A_nn(PLAYER_X); rom.ADD_A_n(8);  rom.LD_HLI_A()
    rom.LD_A_nn(PLAYER_FRAME); rom.ADD_A_A(); rom.ADD_A_n(1); rom.LD_HLI_A()
    rom.LD_A_nn(PLAYER_DIR)
    rom.RRCA(); rom.RRCA(); rom.RRCA(); rom.AND_n(0x20)
    rom.LD_HLI_A()

    # Collectibles
    rom.LD_A_nn(COLL_COUNT); rom.OR_A(); rom.RET_Z()
    rom.LD_B_A(); rom.LD_DE_nn(COLL_DATA)

    rom.label('uo_cl')
    rom.LD_A_DE(); rom.PUSH_AF(); rom.INC_DE()   # save x
    rom.LD_A_DE(); rom.PUSH_AF(); rom.INC_DE()   # save y
    rom.LD_A_DE(); rom.LD_C_A(); rom.INC_DE()    # C = type
    rom.LD_A_DE(); rom.INC_DE()                   # active
    rom.OR_A(); rom.JR_Z('uo_hide')
    rom.POP_AF(); rom.ADD_A_n(16); rom.LD_HLI_A()  # y
    rom.POP_AF(); rom.ADD_A_n(8);  rom.LD_HLI_A()  # x
    # tile by type: 0→star, 1→flower, 2→gift
    rom.LD_A_C()
    rom.OR_A();   rom.JR_NZ('uo_t1')
    rom.LD_A_n(TL_STAR);       rom.JR('uo_tw')
    rom.label('uo_t1'); rom.CP_n(1); rom.JR_NZ('uo_t2')
    rom.LD_A_n(TL_FLOWER_OBJ); rom.JR('uo_tw')
    rom.label('uo_t2'); rom.LD_A_n(TL_GIFT)
    rom.label('uo_tw'); rom.LD_HLI_A()
    rom.LD_A_C(); rom.ADD_A_n(1); rom.LD_HLI_A()   # OBJ palette = type+1
    rom.JR('uo_next')
    rom.label('uo_hide')
    rom.POP_AF(); rom.POP_AF()
    rom.XOR_A()
    rom.LD_HLI_A(); rom.LD_HLI_A(); rom.LD_HLI_A(); rom.LD_HLI_A()
    rom.label('uo_next')
    rom.DEC_B(); rom.JR_NZ('uo_cl'); rom.RET()

    # ── music_tick ───────────────────────────────────────────────────────
    rom.label('music_tick')
    rom.LD_A_nn(MUSIC_CTR); rom.DEC_A(); rom.LD_nn_A(MUSIC_CTR)
    rom.RET_NZ()
    rom.LD_A_nn(MUSIC_PTR_LO); rom.LD_L_A()
    rom.LD_A_nn(MUSIC_PTR_HI); rom.LD_H_A()
    rom.LD_A_HL(); rom.CP_n(0xFF); rom.JR_NZ('mt_play')
    rom.LD_HL_nn(0); patches['mus_reset'] = rom.pos - 2   # reset to start
    rom.label('mt_play')
    rom.LD_A_HLI(); rom.LDH_n_A(NR13)
    rom.LD_A_HLI(); rom.LDH_n_A(NR14)
    rom.LD_A_HLI(); rom.LD_nn_A(MUSIC_CTR)
    rom.LD_A_H(); rom.LD_nn_A(MUSIC_PTR_HI)
    rom.LD_A_L(); rom.LD_nn_A(MUSIC_PTR_LO)
    rom.RET()

    # ── update_score_disp ────────────────────────────────────────────────
    # Writes 3 digit tiles to BG map row 0 cols 8,9,10 (VBlank-gated)
    rom.label('update_score_disp')
    rom.LD_A_nn(SCORE_DIRTY); rom.OR_A(); rom.RET_Z()
    rom.LD_A_nn(GAMESTATE); rom.CP_n(GS_PLAYING); rom.RET_NZ()

    # Check VBlank: only write during VBlank (LY >= 144)
    rom.LDH_A_n(LY); rom.CP_n(144); rom.RET_C()

    rom.XOR_A(); rom.LD_nn_A(SCORE_DIRTY)
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

    # ── update_hearts: write heart tiles to score bar (row 0 cols 2,3,4) ──
    # Also called each frame in PLAYING state — cheap BG map write
    rom.label('update_hearts')
    rom.LD_A_nn(GAMESTATE); rom.CP_n(GS_PLAYING); rom.RET_NZ()
    rom.LD_A_nn(GIFTS); rom.LD_B_A()
    rom.LD_HL_nn(0x9802)
    for bit in range(3):
        rom.LD_A_n(TL_HEART_EMPTY)
        rom.BIT_b_B(bit); rom.JR_Z(f'uh_w{bit}')
        rom.LD_A_n(TL_HEART_FULL)
        rom.label(f'uh_w{bit}'); rom.LD_HLI_A()
    rom.RET()

    # ── do_screen_redraw ──────────────────────────────────────────────────
    # Turn off LCD, copy new tilemap+attrs to VRAM, re-enable LCD.
    rom.label('do_screen_redraw')
    rom.label('dsr_wv')
    rom.LDH_A_n(LY); rom.CP_n(144); rom.JR_C('dsr_wv')
    rom.XOR_A(); rom.LDH_n_A(LCDC)

    rom.LD_A_nn(TRANSITION_TO); rom.LD_nn_A(GAMESTATE)
    rom.XOR_A(); rom.LD_nn_A(NEED_REDRAW)
    rom.LD_A_n(1); rom.LD_nn_A(SCORE_DIRTY)

    # Setup collectibles when entering PLAYING
    rom.LD_A_nn(GAMESTATE); rom.CP_n(GS_PLAYING); rom.JR_NZ('dsr_no_coll')
    rom.CALL('setup_zone_collects')
    rom.label('dsr_no_coll')

    # Pick screen
    for gs, lbl in [(GS_TITLE,'dsr_t'),(GS_INTRO,'dsr_i'),(GS_PLAYING,'dsr_p'),
                    (GS_SAVE,'dsr_sv'),(GS_MAP,'dsr_m'),(GS_VICTORY,'dsr_v')]:
        rom.LD_A_nn(GAMESTATE); rom.CP_n(gs); rom.JP_Z(lbl)
    rom.JP('dsr_done')

    def _dsr_screen(lbl, pt_key, ptas_key):
        rom.label(lbl)
        rom.LD_DE_nn(0); patches[pt_key]  = rom.pos - 2
        rom.LD_BC_nn(0); patches[ptas_key] = rom.pos - 2
        rom.CALL('copy_screen'); rom.JP('dsr_done')

    _dsr_screen('dsr_t',  'title_t',  'title_a')
    _dsr_screen('dsr_i',  'intro_t',  'intro_a')
    _dsr_screen('dsr_sv', 'save_t',   'save_a')
    _dsr_screen('dsr_v',  'vic_t',    'vic_a')

    rom.label('dsr_m')
    rom.LD_DE_nn(0); patches['map_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['map_a'] = rom.pos - 2
    rom.CALL('copy_screen')
    rom.CALL('update_map_hearts')
    rom.JP('dsr_done')

    # Zone selection (9 zones)
    rom.label('dsr_p')
    rom.LD_A_nn(CUR_ZONE)
    rom.CP_n(0); rom.JR_NZ('dsr_p1')
    rom.LD_DE_nn(0); patches['gar_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['gar_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p1'); rom.CP_n(1); rom.JR_NZ('dsr_p2')
    rom.LD_DE_nn(0); patches['for_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['for_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p2'); rom.CP_n(2); rom.JR_NZ('dsr_p3')
    rom.LD_DE_nn(0); patches['mea_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['mea_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p3'); rom.CP_n(3); rom.JR_NZ('dsr_p4')
    rom.LD_DE_nn(0); patches['des_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['des_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p4'); rom.CP_n(4); rom.JR_NZ('dsr_p5')
    rom.LD_DE_nn(0); patches['cav_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['cav_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p5'); rom.CP_n(5); rom.JR_NZ('dsr_p6')
    rom.LD_DE_nn(0); patches['swa_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['swa_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p6'); rom.CP_n(6); rom.JR_NZ('dsr_p7')
    rom.LD_DE_nn(0); patches['sno_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['sno_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p7'); rom.CP_n(7); rom.JR_NZ('dsr_p8')
    rom.LD_DE_nn(0); patches['cry_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['cry_a'] = rom.pos - 2
    rom.JR('dsr_p_copy')
    rom.label('dsr_p8')
    rom.LD_DE_nn(0); patches['sun_t'] = rom.pos - 2
    rom.LD_BC_nn(0); patches['sun_a'] = rom.pos - 2
    rom.label('dsr_p_copy')
    rom.CALL('copy_screen')

    rom.label('dsr_done')
    rom.LD_A_n(0x93); rom.LDH_n_A(LCDC)   # re-enable LCD + OBJ
    rom.RET()

    # ── copy_screen: DE=tile_src, BC=attr_src → write 576 bytes each ─────
    rom.label('copy_screen')
    rom.PUSH_BC()
    rom.XOR_A(); rom.LDH_n_A(VBK)          # bank 0: tiles
    rom.LD_HL_nn(0x9800); rom.LD_BC_nn(576)
    rom.label('cs_t')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cs_t')
    rom.LD_A_n(1); rom.LDH_n_A(VBK)        # bank 1: attrs
    rom.POP_BC()
    rom.LD_A_C(); rom.LD_E_A()              # move BC → DE
    rom.LD_A_B(); rom.LD_D_A()
    rom.LD_HL_nn(0x9800); rom.LD_BC_nn(576)
    rom.label('cs_a')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE(); rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C(); rom.JR_NZ('cs_a')
    rom.XOR_A(); rom.LDH_n_A(VBK)          # back to bank 0
    rom.RET()

    # ── setup_zone_collects ───────────────────────────────────────────────
    # Load collectible list for CUR_ZONE from ROM table into COLL_DATA/COLL_COUNT.
    # Already-collected gifts are marked inactive.
    rom.label('setup_zone_collects')
    # zone_collect_table[zone] → address of (count, x,y,t,1 ...) data
    rom.LD_A_nn(CUR_ZONE); rom.ADD_A_A()   # *2 (16-bit pointers)
    rom.LD_E_A(); rom.LD_D_n(0)
    rom.LD_HL_nn(0); patches['zc_table'] = rom.pos - 2
    rom.ADD_HL_DE()
    rom.LD_A_HLI(); rom.LD_E_A()           # load ptr from table
    rom.LD_A_HLI(); rom.LD_D_A()
    # DE → zone data block
    rom.LD_A_DE(); rom.LD_nn_A(COLL_COUNT); rom.LD_B_A(); rom.INC_DE()
    rom.LD_HL_nn(COLL_DATA)
    rom.label('szc_lp')
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE()    # x
    rom.LD_A_DE(); rom.LD_HLI_A(); rom.INC_DE()    # y
    rom.LD_A_DE(); rom.LD_C_A()                     # C = type
    rom.LD_HLI_A(); rom.INC_DE()
    rom.LD_A_n(1); rom.LD_HLI_A()                   # active = 1
    rom.INC_DE()                                    # skip stored 0 in source
    # If gift and already collected this zone → mark inactive
    rom.LD_A_C(); rom.CP_n(2); rom.JR_NZ('szc_sk')
    rom.PUSH_BC()
    rom.LD_A_n(1); rom.LD_C_A()
    rom.LD_A_nn(CUR_ZONE); rom.OR_A(); rom.JR_Z('szc_md')
    rom.LD_D_A()
    rom.label('szc_sl'); rom.LD_A_C(); rom.ADD_A_A(); rom.LD_C_A(); rom.DEC_D()
    rom.JR_NZ('szc_sl')
    rom.label('szc_md')
    rom.LD_A_nn(GIFTS); rom.AND_C()
    rom.POP_BC(); rom.JR_Z('szc_sk')
    rom.DEC_HL(); rom.XOR_A(); rom.LD_HL_A(); rom.INC_HL()
    rom.label('szc_sk')
    rom.DEC_B(); rom.JR_NZ('szc_lp'); rom.RET()

    # ── update_map_hearts ─────────────────────────────────────────────────
    # Write hearts to BG map for zones 0,1,2 (rows 6,8,10 col 12)
    # BG addr = 0x9800 + row*32 + col
    rom.label('update_map_hearts')
    rom.LD_A_nn(GIFTS); rom.LD_B_A()
    map_heart_addrs = [
        (0, 0x9800 + 6*32 + 12),   # zone 0 → row 6 col 12 = 0x98CC
        (1, 0x9800 + 8*32 + 12),   # zone 1 → row 8 col 12 = 0x990C
        (2, 0x9800 + 10*32 + 12),  # zone 2 → row 10 col 12 = 0x994C
    ]
    for bit, addr in map_heart_addrs:
        rom.LD_A_n(TL_HEART_EMPTY)
        rom.BIT_b_B(bit); rom.JR_Z(f'umh_w{bit}')
        rom.LD_A_n(TL_HEART_FULL)
        rom.label(f'umh_w{bit}')
        rom.LD_HL_nn(addr); rom.LD_HL_A()
    rom.RET()

    # ── save_to_sram ─────────────────────────────────────────────────────
    rom.label('save_to_sram')
    rom.LD_A_n(0x0A); rom.LD_nn_A(0x0000)   # enable SRAM
    for addr, val in [(0xA000, 0x42), (0xA001, 0x55),  # 'B','U'
                      (0xA002, 0x4E), (0xA003, 0x59)]:  # 'N','Y'
        rom.LD_A_n(val); rom.LD_nn_A(addr)
    for src, dst in [(CUR_ZONE, 0xA004), (PLAYER_X, 0xA005),
                     (PLAYER_Y, 0xA006), (GIFTS, 0xA007), (SCORE, 0xA008)]:
        rom.LD_A_nn(src); rom.LD_nn_A(dst)
    rom.XOR_A(); rom.LD_nn_A(0x0000)        # disable SRAM
    rom.RET()

    # ── try_load_save ─────────────────────────────────────────────────────
    # If SRAM magic == 'BUNY', load and jump to PLAYING; else set TITLE.
    rom.label('try_load_save')
    rom.LD_A_n(0x0A); rom.LD_nn_A(0x0000)
    for addr, val in [(0xA000,0x42),(0xA001,0x55),(0xA002,0x4E),(0xA003,0x59)]:
        rom.LD_A_nn(addr); rom.CP_n(val); rom.JR_NZ('tls_no')
    # Valid save — restore
    for dst, src in [(CUR_ZONE,0xA004),(PLAYER_X,0xA005),(PLAYER_Y,0xA006),
                     (GIFTS,0xA007),(SCORE,0xA008)]:
        rom.LD_A_nn(src); rom.LD_nn_A(dst)
    rom.XOR_A(); rom.LD_nn_A(0x0000)
    rom.LD_A_n(GS_PLAYING)
    rom.LD_nn_A(GAMESTATE); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.RET()

    rom.label('tls_no')
    rom.XOR_A(); rom.LD_nn_A(0x0000)
    rom.LD_A_n(GS_TITLE)
    rom.LD_nn_A(GAMESTATE); rom.LD_nn_A(TRANSITION_TO)
    rom.LD_A_n(1); rom.LD_nn_A(NEED_REDRAW)
    rom.RET()

    return patches
