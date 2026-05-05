#!/usr/bin/env python3
"""
Bunny Garden - GBC ROM Generator
Generates a complete Game Boy Color ROM from scratch.
No assembler, no GB Studio - pure Python → binary.

Game: Pink bunny collects yellow stars and purple flowers.
Color theme: Pink, Purple, Yellow.
"""

import struct, sys

# ================================================================
#  GBC COLOR UTILITIES
# ================================================================
def rgb15(r, g, b):
    """Pack 0-31 RGB to 15-bit GBC color (little-endian word)."""
    return (r & 0x1F) | ((g & 0x1F) << 5) | ((b & 0x1F) << 10)

def color_lo(c): return c & 0xFF
def color_hi(c): return (c >> 8) & 0xFF

# ================================================================
#  PALETTE COLORS
# ================================================================
PALE_LAV    = rgb15(24, 20, 31)   # pale lavender (light BG)
SOFT_PUR    = rgb15(18, 12, 26)   # soft purple (mid BG)
MED_PUR     = rgb15(11,  6, 22)   # medium purple
DARK_PUR    = rgb15( 6,  2, 16)   # dark purple

LIGHT_PINK  = rgb15(31, 22, 26)   # light pink
SOFT_PINK   = rgb15(28, 14, 20)   # soft pink
HOT_PINK    = rgb15(24,  6, 14)   # hot pink
DARK_PINK   = rgb15(16,  2,  8)   # dark rose

LIGHT_YEL   = rgb15(31, 30, 10)   # light yellow
YELLOW      = rgb15(31, 28,  0)   # bright yellow
GOLD        = rgb15(31, 22,  0)   # golden
DARK_GOLD   = rgb15(24, 14,  0)   # dark gold

WHITE       = rgb15(31, 31, 31)
BLACK       = rgb15( 0,  0,  0)

# 8 BG palettes × 4 colors × 2 bytes = 64 bytes each for BCPD
BG_PALETTES = [
    # Palette 0 — garden ground (purples)
    [PALE_LAV, SOFT_PUR, MED_PUR, DARK_PUR],
    # Palette 1 — flower patches (pinks)
    [PALE_LAV, LIGHT_PINK, SOFT_PINK, HOT_PINK],
    # Palette 2 — score bar (dark purple + yellow/white)
    [DARK_PUR, WHITE, LIGHT_YEL, GOLD],
    # Palettes 3-7 unused (repeat palette 0)
    [PALE_LAV, SOFT_PUR, MED_PUR, DARK_PUR],
    [PALE_LAV, SOFT_PUR, MED_PUR, DARK_PUR],
    [PALE_LAV, SOFT_PUR, MED_PUR, DARK_PUR],
    [PALE_LAV, SOFT_PUR, MED_PUR, DARK_PUR],
    [PALE_LAV, SOFT_PUR, MED_PUR, DARK_PUR],
]

# 8 OBJ palettes × 4 colors
OBJ_PALETTES = [
    # Palette 0 — bunny (white + pink, color 0 = transparent)
    [BLACK,    WHITE,      LIGHT_PINK, HOT_PINK],
    # Palette 1 — star collectible
    [BLACK,    LIGHT_YEL,  YELLOW,     GOLD],
    # Palette 2 — flower collectible
    [BLACK,    LIGHT_PINK, SOFT_PINK,  HOT_PINK],
    # Palettes 3-7 unused
    [BLACK, WHITE, WHITE, WHITE],
    [BLACK, WHITE, WHITE, WHITE],
    [BLACK, WHITE, WHITE, WHITE],
    [BLACK, WHITE, WHITE, WHITE],
    [BLACK, WHITE, WHITE, WHITE],
]

def palettes_to_bytes(palettes):
    """Convert list of [color0..color3] palettes to BCPD byte stream."""
    out = []
    for pal in palettes:
        for c in pal:
            out.append(color_lo(c))
            out.append(color_hi(c))
    return out

# ================================================================
#  TILE GRAPHICS (2bpp format)
# ================================================================
def encode_tile(pixels):
    """8×8 pixel array (0-3) → 16-byte 2bpp tile."""
    result = []
    for row in pixels:
        plane0 = plane1 = 0
        for bit, color in enumerate(row):
            if color & 1: plane0 |= (0x80 >> bit)
            if color & 2: plane1 |= (0x80 >> bit)
        result += [plane0, plane1]
    return result

def empty_tile():
    return encode_tile([[0]*8]*8)

# ---------- Bunny tiles (OBJ palette 0: 0=trans,1=white,2=lpink,3=hpink) ----------
def bunny_top_f1():
    return encode_tile([
        [0,0,3,3,3,0,0,0],
        [0,3,2,2,2,3,0,0],
        [0,3,1,2,2,3,0,0],
        [0,3,2,3,2,2,3,0],
        [0,3,2,2,2,3,0,0],
        [0,0,3,2,3,0,0,0],
        [0,3,1,1,1,3,0,0],
        [3,1,1,1,1,1,3,0],
    ])

def bunny_bot_f1():
    return encode_tile([
        [3,1,1,1,1,1,3,0],
        [3,1,1,0,1,1,3,0],
        [3,1,0,0,0,1,3,0],
        [3,1,0,0,0,1,3,0],
        [0,3,1,0,1,3,0,0],
        [0,3,1,0,1,3,0,0],
        [0,3,3,0,3,3,0,0],
        [0,0,0,0,0,0,0,0],
    ])

def bunny_top_f2():  # same head, same top
    return bunny_top_f1()

def bunny_bot_f2():  # walking step — right leg forward
    return encode_tile([
        [3,1,1,1,1,1,3,0],
        [3,1,1,0,1,1,3,0],
        [3,1,0,0,0,1,3,0],
        [3,1,0,0,1,1,3,0],
        [0,3,1,0,3,1,3,0],
        [0,0,3,0,0,3,0,0],
        [0,0,3,3,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ])

# ---------- Collectible tiles ----------
def star_tile():
    # OBJ palette 1: 0=trans,1=lyellow,2=yellow,3=gold
    return encode_tile([
        [0,0,0,2,2,0,0,0],
        [0,0,2,3,3,2,0,0],
        [0,2,3,2,2,3,2,0],
        [2,3,3,3,3,3,3,2],
        [2,3,3,3,3,3,3,2],
        [0,2,3,2,2,3,2,0],
        [0,0,2,3,3,2,0,0],
        [0,0,0,2,2,0,0,0],
    ])

def flower_tile():
    # OBJ palette 2: 0=trans,1=lpink,2=spink,3=hpink
    return encode_tile([
        [0,0,1,2,2,1,0,0],
        [0,1,2,3,3,2,1,0],
        [1,2,3,1,1,3,2,1],
        [2,3,1,2,2,1,3,2],
        [2,3,1,2,2,1,3,2],
        [1,2,3,1,1,3,2,1],
        [0,1,2,3,3,2,1,0],
        [0,0,1,2,2,1,0,0],
    ])

# ---------- Background tiles ----------
def grass1():
    # BG palette 0: 0=palelavender,1=softpur,2=medpur,3=darkpur
    return encode_tile([
        [1,1,1,1,1,1,1,1],
        [1,0,1,1,1,0,1,1],
        [1,1,2,1,1,1,2,1],
        [1,1,2,2,1,1,2,1],
        [1,1,1,2,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,0,1,1,1,0,1,1],
        [1,1,1,1,1,1,1,1],
    ])

def grass2():
    return encode_tile([
        [1,1,1,0,1,1,1,1],
        [1,1,1,1,2,1,1,1],
        [1,0,1,1,1,1,0,1],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0],
        [1,1,2,1,1,2,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,0,1,1],
    ])

def flower_patch():
    # BG palette 1: 0=palelavender,1=lpink,2=spink,3=hpink
    return encode_tile([
        [1,0,1,1,1,0,1,1],
        [1,1,2,1,1,2,1,1],
        [0,2,3,2,2,3,2,0],
        [1,1,2,1,1,2,1,1],
        [1,0,1,1,1,0,1,1],
        [1,1,1,0,1,1,1,1],
        [1,1,2,3,2,1,1,1],
        [1,1,0,2,0,1,1,1],
    ])

def score_bar():
    # BG palette 2: all color 0 (dark purple) for background
    return encode_tile([[0]*8]*8)

def star_icon():
    # BG palette 2: 0=darkpur,1=white,2=lyellow,3=gold
    return encode_tile([
        [0,0,0,2,2,0,0,0],
        [0,0,2,3,3,2,0,0],
        [0,2,3,3,3,3,2,0],
        [2,3,3,2,2,3,3,2],
        [2,3,3,3,3,3,3,2],
        [0,2,3,3,3,3,2,0],
        [0,0,2,0,0,2,0,0],
        [0,0,0,0,0,0,0,0],
    ])

DIGIT_PIXELS = [
    # 0
    [[0,1,1,1,1,0,0,0],[1,2,0,0,2,1,0,0],[1,2,0,0,2,1,0,0],[1,2,0,0,2,1,0,0],
     [1,2,0,0,2,1,0,0],[1,2,0,0,2,1,0,0],[0,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0]],
    # 1
    [[0,0,1,2,0,0,0,0],[0,1,2,2,0,0,0,0],[0,0,1,2,0,0,0,0],[0,0,1,2,0,0,0,0],
     [0,0,1,2,0,0,0,0],[0,0,1,2,0,0,0,0],[0,1,1,2,1,0,0,0],[0,0,0,0,0,0,0,0]],
    # 2
    [[0,1,1,1,1,0,0,0],[1,2,0,0,2,1,0,0],[0,0,0,1,2,0,0,0],[0,0,1,2,1,0,0,0],
     [0,1,2,1,0,0,0,0],[1,2,1,0,0,0,0,0],[1,1,1,1,1,1,0,0],[0,0,0,0,0,0,0,0]],
    # 3
    [[0,1,1,1,1,0,0,0],[0,0,0,0,2,1,0,0],[0,0,0,1,2,0,0,0],[0,1,1,2,1,0,0,0],
     [0,0,0,1,2,0,0,0],[0,0,0,0,2,1,0,0],[0,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0]],
    # 4
    [[0,0,1,2,1,0,0,0],[0,1,2,2,1,0,0,0],[1,2,1,2,1,0,0,0],[1,1,1,2,1,1,0,0],
     [0,0,1,2,1,0,0,0],[0,0,1,2,1,0,0,0],[0,0,1,2,1,0,0,0],[0,0,0,0,0,0,0,0]],
    # 5
    [[1,1,1,1,1,0,0,0],[1,2,0,0,0,0,0,0],[1,1,1,1,0,0,0,0],[0,0,0,2,1,0,0,0],
     [0,0,0,2,1,0,0,0],[1,2,0,2,1,0,0,0],[0,1,1,1,0,0,0,0],[0,0,0,0,0,0,0,0]],
    # 6
    [[0,1,1,1,1,0,0,0],[1,2,0,0,0,0,0,0],[1,2,1,1,0,0,0,0],[1,2,0,2,1,0,0,0],
     [1,2,0,2,1,0,0,0],[1,2,0,2,1,0,0,0],[0,1,1,1,0,0,0,0],[0,0,0,0,0,0,0,0]],
    # 7
    [[1,1,1,1,1,1,0,0],[0,0,0,0,2,1,0,0],[0,0,0,1,2,0,0,0],[0,0,1,2,0,0,0,0],
     [0,0,1,2,0,0,0,0],[0,0,1,2,0,0,0,0],[0,0,1,2,0,0,0,0],[0,0,0,0,0,0,0,0]],
    # 8
    [[0,1,1,1,1,0,0,0],[1,2,0,0,2,1,0,0],[1,2,0,0,2,1,0,0],[0,1,1,1,1,0,0,0],
     [1,2,0,0,2,1,0,0],[1,2,0,0,2,1,0,0],[0,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0]],
    # 9
    [[0,1,1,1,1,0,0,0],[1,2,0,0,2,1,0,0],[1,2,0,0,2,1,0,0],[0,1,1,1,2,1,0,0],
     [0,0,0,0,2,1,0,0],[0,0,0,1,2,0,0,0],[0,1,1,1,0,0,0,0],[0,0,0,0,0,0,0,0]],
]

def digit_tile(n): return encode_tile(DIGIT_PIXELS[n])

# === Tile index assignments ===
# OBJ tiles (in VRAM 0x8000+idx*16):
TL_BUNNY_R_F1_TOP = 0x00  # bunny right frame1 top
TL_BUNNY_R_F1_BOT = 0x01  # bunny right frame1 bottom
TL_BUNNY_R_F2_TOP = 0x02  # bunny right frame2 top
TL_BUNNY_R_F2_BOT = 0x03  # bunny right frame2 bottom
TL_STAR            = 0x08  # star collectible
TL_FLOWER          = 0x09  # flower collectible
# BG tiles:
TL_SCORE_BAR       = 0x10  # dark purple bar
TL_GRASS1          = 0x11
TL_GRASS2          = 0x12
TL_FLOWER_PATCH    = 0x13
TL_STAR_ICON       = 0x14  # score display star icon
TL_DIGIT_0         = 0x20  # digit tiles 0x20-0x29

def build_tile_data():
    """Build flat tile data for VRAM bank 0 starting at tile 0."""
    data = bytearray(256 * 16)  # 256 tiles × 16 bytes
    def put(idx, tile_bytes):
        start = idx * 16
        for i, b in enumerate(tile_bytes):
            data[start + i] = b
    put(TL_BUNNY_R_F1_TOP, bunny_top_f1())
    put(TL_BUNNY_R_F1_BOT, bunny_bot_f1())
    put(TL_BUNNY_R_F2_TOP, bunny_top_f2())
    put(TL_BUNNY_R_F2_BOT, bunny_bot_f2())
    put(TL_STAR,            star_tile())
    put(TL_FLOWER,          flower_tile())
    put(TL_SCORE_BAR,       score_bar())
    put(TL_GRASS1,          grass1())
    put(TL_GRASS2,          grass2())
    put(TL_FLOWER_PATCH,    flower_patch())
    put(TL_STAR_ICON,       star_icon())
    for n in range(10):
        put(TL_DIGIT_0 + n,  digit_tile(n))
    return data

# ================================================================
#  BACKGROUND MAP (32×32, only 20×18 visible)
# ================================================================
def build_bg_map():
    """Returns (tile_map 576 bytes, attr_map 576 bytes) for 18×32 rows."""
    tiles = bytearray(18 * 32)
    attrs = bytearray(18 * 32)
    for row in range(18):
        for col in range(32):
            idx = row * 32 + col
            if row == 0:
                # Score bar row
                if col == 1:
                    tiles[idx] = TL_STAR_ICON
                elif col == 2:
                    tiles[idx] = TL_DIGIT_0   # hundreds (updated at runtime)
                elif col == 3:
                    tiles[idx] = TL_DIGIT_0   # tens
                elif col == 4:
                    tiles[idx] = TL_DIGIT_0   # ones
                else:
                    tiles[idx] = TL_SCORE_BAR
                attrs[idx] = 0x02  # BG palette 2
            else:
                # Garden — deterministic pattern
                h = (row * 7 + col * 13) % 16
                if h < 9:
                    tiles[idx] = TL_GRASS1
                    attrs[idx] = 0x00  # palette 0
                elif h < 13:
                    tiles[idx] = TL_GRASS2
                    attrs[idx] = 0x00
                else:
                    tiles[idx] = TL_FLOWER_PATCH
                    attrs[idx] = 0x01  # palette 1
    return tiles, attrs

# ================================================================
#  MUSIC DATA (Twinkle Twinkle Little Star)
# ================================================================
# GBC freq formula: f_reg = 2048 - 131072 / Hz
def freq(hz): return round(2048 - 131072 / hz)

C5=freq(523.25); D5=freq(587.33); E5=freq(659.26)
F5=freq(698.46); G5=freq(783.99); A5=freq(880.00)

def note(f, dur):
    return [f & 0xFF, ((f >> 8) & 0x07) | 0x80, dur]

Q = 15  # quarter note frames at ~60fps
H = 30  # half note

MUSIC_DATA = []
for pattern in [
    (C5,Q),(C5,Q),(G5,Q),(G5,Q),(A5,Q),(A5,Q),(G5,H),
    (F5,Q),(F5,Q),(E5,Q),(E5,Q),(D5,Q),(D5,Q),(C5,H),
    (G5,Q),(G5,Q),(F5,Q),(F5,Q),(E5,Q),(E5,Q),(D5,H),
    (G5,Q),(G5,Q),(F5,Q),(F5,Q),(E5,Q),(E5,Q),(D5,H),
    (C5,Q),(C5,Q),(G5,Q),(G5,Q),(A5,Q),(A5,Q),(G5,H),
    (F5,Q),(F5,Q),(E5,Q),(E5,Q),(D5,Q),(D5,Q),(C5,H),
]:
    MUSIC_DATA += note(pattern[0], pattern[1])
MUSIC_DATA += [0xFF]  # loop marker

# ================================================================
#  COLLECTIBLE INITIAL POSITIONS
# ================================================================
# (x_pixel, y_pixel, type: 0=star/1=flower, active=1)
INIT_COLLECTS = [
    (24, 32, 0, 1),
    (80, 24, 1, 1),
    (136, 48, 0, 1),
    (48, 88, 1, 1),
    (112, 72, 0, 1),
    (32, 116, 1, 1),
    (100, 108, 0, 1),
    (144, 96, 1, 1),
]

# ================================================================
#  ROM ASSEMBLER
# ================================================================
class ROM:
    def __init__(self, size=32768):
        self.data  = bytearray(size)
        self.pos   = 0
        self.labels = {}
        self.fixups = []   # (pos_of_target_field, label, 'abs16'|'rel8')

    # ---------- seek ----------
    def seek(self, addr): self.pos = addr

    # ---------- raw emit ----------
    def emit(self, *bs):
        for b in bs:
            self.data[self.pos] = b & 0xFF
            self.pos += 1

    # ---------- label ----------
    def label(self, name):
        if name in self.labels:
            raise Exception(f"Duplicate label: {name}")
        self.labels[name] = self.pos

    # ---------- basic opcodes ----------
    def NOP(self):  self.emit(0x00)
    def RETI(self): self.emit(0xD9)
    def RET(self):  self.emit(0xC9)
    def RET_Z(self):  self.emit(0xC8)
    def RET_NZ(self): self.emit(0xC0)
    def EI(self):   self.emit(0xFB)
    def DI(self):   self.emit(0xF3)
    def HALT(self): self.emit(0x76)
    def XOR_A(self):self.emit(0xAF)
    def OR_A(self): self.emit(0xB7)
    def CPL(self):  self.emit(0x2F)
    def SCF(self):  self.emit(0x37)
    def CCF(self):  self.emit(0x3F)
    def DAA(self):  self.emit(0x27)
    def RLCA(self): self.emit(0x07)

    # LD r, n
    def LD_A_n(self,n): self.emit(0x3E,n)
    def LD_B_n(self,n): self.emit(0x06,n)
    def LD_C_n(self,n): self.emit(0x0E,n)
    def LD_D_n(self,n): self.emit(0x16,n)
    def LD_E_n(self,n): self.emit(0x1E,n)
    def LD_H_n(self,n): self.emit(0x26,n)
    def LD_L_n(self,n): self.emit(0x2E,n)

    # LD r16, nn
    def LD_SP_nn(self,nn): self.emit(0x31, nn&0xFF, nn>>8)
    def LD_BC_nn(self,nn): self.emit(0x01, nn&0xFF, nn>>8)
    def LD_DE_nn(self,nn): self.emit(0x11, nn&0xFF, nn>>8)
    def LD_HL_nn(self,nn): self.emit(0x21, nn&0xFF, nn>>8)

    # LD r, r  (reg encoding: B=0,C=1,D=2,E=3,H=4,L=5,(HL)=6,A=7)
    def LD_A_B(self):  self.emit(0x78)
    def LD_A_C(self):  self.emit(0x79)
    def LD_A_D(self):  self.emit(0x7A)
    def LD_A_E(self):  self.emit(0x7B)
    def LD_A_H(self):  self.emit(0x7C)
    def LD_A_L(self):  self.emit(0x7D)
    def LD_A_HL(self): self.emit(0x7E)  # LD A, (HL)
    def LD_B_A(self):  self.emit(0x47)
    def LD_C_A(self):  self.emit(0x4F)
    def LD_D_A(self):  self.emit(0x57)
    def LD_E_A(self):  self.emit(0x5B)  # wait: 0x40+3*8+7=0x5F, E dest=3
    def LD_E_A_(self): self.emit(0x5F)  # LD E, A = 0x5F
    def LD_H_A(self):  self.emit(0x67)
    def LD_L_A(self):  self.emit(0x6F)
    def LD_HL_A(self): self.emit(0x77)  # LD (HL), A
    def LD_B_B(self):  self.emit(0x40)
    def LD_B_HL(self): self.emit(0x46)  # LD B, (HL)
    def LD_C_HL(self): self.emit(0x4E)  # LD C, (HL)
    def LD_D_HL(self): self.emit(0x56)  # LD D, (HL)
    def LD_E_HL(self): self.emit(0x5E)  # LD E, (HL)
    def LD_H_HL(self): self.emit(0x66)  # LD H, (HL)
    def LD_L_HL(self): self.emit(0x6E)  # LD L, (HL)
    def LD_B_H(self):  self.emit(0x44)
    def LD_B_L(self):  self.emit(0x45)
    def LD_C_H(self):  self.emit(0x4C)
    def LD_C_L(self):  self.emit(0x4D)
    def LD_H_B(self):  self.emit(0x60)
    def LD_H_C(self):  self.emit(0x61)
    def LD_H_D(self):  self.emit(0x62)
    def LD_H_E(self):  self.emit(0x63)
    def LD_L_B(self):  self.emit(0x68)
    def LD_L_C(self):  self.emit(0x69)
    def LD_L_D(self):  self.emit(0x6A)
    def LD_L_E(self):  self.emit(0x6B)
    def LD_L_H(self):  self.emit(0x6C)
    def LD_B_D(self):  self.emit(0x42)
    def LD_B_E(self):  self.emit(0x43)
    def LD_C_B(self):  self.emit(0x48)
    def LD_C_D(self):  self.emit(0x4A)
    def LD_C_E(self):  self.emit(0x4B)
    def LD_D_B(self):  self.emit(0x50)
    def LD_D_C(self):  self.emit(0x51)
    def LD_D_E(self):  self.emit(0x53)
    def LD_E_B(self):  self.emit(0x58)
    def LD_E_C(self):  self.emit(0x59)
    def LD_E_D(self):  self.emit(0x5A)
    def LD_E_H(self):  self.emit(0x5C)
    def LD_E_L(self):  self.emit(0x5D)
    def LD_A_E2(self): self.emit(0x7B)  # LD A, E (alias)
    def LD_A_B2(self): self.emit(0x78)  # alias

    # LD A, (reg16) and LD (reg16), A
    def LD_A_BC(self):  self.emit(0x0A)
    def LD_A_DE(self):  self.emit(0x1A)
    def LD_A_HLI(self): self.emit(0x2A)  # LD A, (HL+)
    def LD_A_HLD(self): self.emit(0x3A)  # LD A, (HL-)
    def LD_BC_A(self):  self.emit(0x02)
    def LD_DE_A(self):  self.emit(0x12)
    def LD_HLI_A(self): self.emit(0x22)  # LD (HL+), A
    def LD_HLD_A(self): self.emit(0x32)  # LD (HL-), A
    def LD_HL_n(self,n):self.emit(0x36,n)# LD (HL), n

    # LD A, (nn) and LD (nn), A
    def LD_A_nn(self,nn): self.emit(0xFA, nn&0xFF, nn>>8)
    def LD_nn_A(self,nn): self.emit(0xEA, nn&0xFF, nn>>8)

    # LDH — IO range 0xFF00
    def LDH_n_A(self,n):  self.emit(0xE0, n&0xFF)  # LD (FF00+n), A
    def LDH_A_n(self,n):  self.emit(0xF0, n&0xFF)  # LD A, (FF00+n)
    def LDH_C_A(self):    self.emit(0xE2)           # LD (FF00+C), A
    def LDH_A_C(self):    self.emit(0xF2)           # LD A, (FF00+C)

    # LD SP/HL transfers
    def LD_SP_HL(self): self.emit(0xF9)

    # INC / DEC 8-bit
    def INC_A(self): self.emit(0x3C)
    def INC_B(self): self.emit(0x04)
    def INC_C(self): self.emit(0x0C)
    def INC_D(self): self.emit(0x14)
    def INC_E(self): self.emit(0x1C)
    def INC_H(self): self.emit(0x24)
    def INC_L(self): self.emit(0x2C)
    def INC_HL_mem(self):self.emit(0x34) # INC (HL)
    def DEC_A(self): self.emit(0x3D)
    def DEC_B(self): self.emit(0x05)
    def DEC_C(self): self.emit(0x0D)
    def DEC_D(self): self.emit(0x15)
    def DEC_E(self): self.emit(0x1D)
    def DEC_H(self): self.emit(0x25)
    def DEC_L(self): self.emit(0x2D)
    def DEC_HL_mem(self):self.emit(0x35)

    # INC / DEC 16-bit
    def INC_BC(self): self.emit(0x03)
    def INC_DE(self): self.emit(0x13)
    def INC_HL(self): self.emit(0x23)
    def INC_SP(self): self.emit(0x33)
    def DEC_BC(self): self.emit(0x0B)
    def DEC_DE(self): self.emit(0x1B)
    def DEC_HL(self): self.emit(0x2B)
    def DEC_SP(self): self.emit(0x3B)

    # ADD / SUB / AND / OR / XOR / CP  (A operand)
    def ADD_A_n(self,n): self.emit(0xC6,n)
    def ADD_A_A(self):   self.emit(0x87)
    def ADD_A_B(self):   self.emit(0x80)
    def ADD_A_C(self):   self.emit(0x81)
    def ADD_A_D(self):   self.emit(0x82)
    def ADD_A_E(self):   self.emit(0x83)
    def ADD_A_H(self):   self.emit(0x84)
    def ADD_A_L(self):   self.emit(0x85)
    def ADD_A_HL(self):  self.emit(0x86)  # ADD A, (HL)
    def SUB_A_n(self,n): self.emit(0xD6,n)
    def SUB_B(self):     self.emit(0x90)
    def SUB_C(self):     self.emit(0x91)
    def SUB_D(self):     self.emit(0x92)
    def SUB_E(self):     self.emit(0x93)
    def AND_n(self,n):   self.emit(0xE6,n)
    def AND_B(self):     self.emit(0xA0)
    def AND_A(self):     self.emit(0xA7)
    def OR_n(self,n):    self.emit(0xF6,n)
    def OR_B(self):      self.emit(0xB0)
    def OR_C(self):      self.emit(0xB1)
    def CP_n(self,n):    self.emit(0xFE,n)
    def CP_B(self):      self.emit(0xB8)
    def CP_C(self):      self.emit(0xB9)
    def CP_D(self):      self.emit(0xBA)
    def CP_E(self):      self.emit(0xBB)
    def CP_HL(self):     self.emit(0xBE)

    # PUSH / POP
    def PUSH_AF(self): self.emit(0xF5)
    def PUSH_BC(self): self.emit(0xC5)
    def PUSH_DE(self): self.emit(0xD5)
    def PUSH_HL(self): self.emit(0xE5)
    def POP_AF(self):  self.emit(0xF1)
    def POP_BC(self):  self.emit(0xC1)
    def POP_DE(self):  self.emit(0xD1)
    def POP_HL(self):  self.emit(0xE1)

    # Jumps (label-aware)
    def _fixup_abs(self, lbl):
        if isinstance(lbl, int):
            self.emit(lbl & 0xFF, (lbl >> 8) & 0xFF)
        else:
            self.fixups.append((self.pos, lbl, 'abs16'))
            self.emit(0x00, 0x00)
    def _fixup_rel(self, lbl):
        self.fixups.append((self.pos, lbl, 'rel8'))
        self.emit(0x00)

    def JP(self, lbl):   self.emit(0xC3); self._fixup_abs(lbl)
    def JP_Z(self, lbl): self.emit(0xCA); self._fixup_abs(lbl)
    def JP_NZ(self,lbl): self.emit(0xC2); self._fixup_abs(lbl)
    def JP_C(self, lbl): self.emit(0xDA); self._fixup_abs(lbl)
    def JP_NC(self,lbl): self.emit(0xD2); self._fixup_abs(lbl)
    def JP_HL(self):     self.emit(0xE9)

    def JR(self, lbl):   self.emit(0x18); self._fixup_rel(lbl)
    def JR_Z(self, lbl): self.emit(0x28); self._fixup_rel(lbl)
    def JR_NZ(self,lbl): self.emit(0x20); self._fixup_rel(lbl)
    def JR_C(self, lbl): self.emit(0x38); self._fixup_rel(lbl)
    def JR_NC(self,lbl): self.emit(0x30); self._fixup_rel(lbl)

    def CALL(self, lbl):    self.emit(0xCD); self._fixup_abs(lbl)
    def CALL_Z(self, lbl):  self.emit(0xCC); self._fixup_abs(lbl)
    def CALL_NZ(self, lbl): self.emit(0xC4); self._fixup_abs(lbl)

    # CB-prefix
    def BIT_b_A(self,b):  self.emit(0xCB, 0x40 + b*8 + 7)
    def BIT_b_B(self,b):  self.emit(0xCB, 0x40 + b*8 + 0)
    def SET_b_A(self,b):  self.emit(0xCB, 0xC0 + b*8 + 7)
    def RES_b_A(self,b):  self.emit(0xCB, 0x80 + b*8 + 7)
    def SWAP_A(self):     self.emit(0xCB, 0x37)
    def SRL_A(self):      self.emit(0xCB, 0x3F)
    def SRL_B(self):      self.emit(0xCB, 0x38)
    def SLA_A(self):      self.emit(0xCB, 0x27)
    def SLA_B(self):      self.emit(0xCB, 0x20)
    def SRA_A(self):      self.emit(0xCB, 0x2F)
    def RL_A_cb(self):    self.emit(0xCB, 0x17)  # RL A (through carry)
    def RR_A_cb(self):    self.emit(0xCB, 0x1F)

    # ADD HL, rr
    def ADD_HL_BC(self): self.emit(0x09)
    def ADD_HL_DE(self): self.emit(0x19)
    def ADD_HL_HL(self): self.emit(0x29)

    # Resolve all fixups
    def resolve(self):
        for (pos, lbl, typ) in self.fixups:
            if lbl not in self.labels:
                raise Exception(f"Undefined label '{lbl}'")
            target = self.labels[lbl]
            if typ == 'abs16':
                self.data[pos]   = target & 0xFF
                self.data[pos+1] = (target >> 8) & 0xFF
            else:  # rel8
                offset = target - (pos + 1)
                if not (-128 <= offset <= 127):
                    raise Exception(f"JR offset OOR for '{lbl}': {offset}")
                self.data[pos] = offset & 0xFF

    # Write Nintendo logo + header
    def set_header(self, title="BUNNYGARDEN"):
        LOGO = bytes([
            0xCE,0xED,0x66,0x66,0xCC,0x0D,0x00,0x0B,
            0x03,0x73,0x00,0x83,0x00,0x0C,0x00,0x0D,
            0x00,0x08,0x11,0x1F,0x88,0x89,0x00,0x0E,
            0xDC,0xCC,0x6E,0xE6,0xDD,0xDD,0xD9,0x99,
            0xBB,0xBB,0x67,0x63,0x6E,0x0E,0xEC,0xCC,
            0xDD,0xDC,0x99,0x9F,0xBB,0xB9,0x33,0x3E,
        ])
        for i,b in enumerate(LOGO): self.data[0x104+i] = b
        tb = title[:15].encode('ascii')
        for i,b in enumerate(tb): self.data[0x134+i] = b
        self.data[0x143] = 0x80   # GBC compatible
        self.data[0x144] = 0x30   # new licensee '00'
        self.data[0x145] = 0x30
        self.data[0x146] = 0x00   # no SGB
        self.data[0x147] = 0x00   # ROM only
        self.data[0x148] = 0x00   # 32KB
        self.data[0x149] = 0x00   # no SRAM
        self.data[0x14A] = 0x01   # non-JP
        self.data[0x14B] = 0x33   # use new licensee
        self.data[0x14C] = 0x00   # version 0
        # Header checksum
        chk = 0
        for a in range(0x134, 0x14D):
            chk = (chk - self.data[a] - 1) & 0xFF
        self.data[0x14D] = chk
        # Global checksum (optional but nice)
        gchk = sum(b for i,b in enumerate(self.data) if i not in (0x14E,0x14F)) & 0xFFFF
        self.data[0x14E] = (gchk >> 8) & 0xFF
        self.data[0x14F] = gchk & 0xFF

# ================================================================
#  WRAM & IO CONSTANTS
# ================================================================
# WRAM layout
PLAYER_X     = 0xC000
PLAYER_Y     = 0xC001
PLAYER_DIR   = 0xC002   # 0=right 1=left
PLAYER_FRAME = 0xC003   # 0 or 1
ANIM_CTR     = 0xC004   # counts 0-15, toggles frame
SCORE        = 0xC005
SCORE_DIRTY  = 0xC006
HUND_DIG     = 0xC007   # hundreds digit
TENS_DIG     = 0xC008
ONES_DIG     = 0xC009
COLL_DATA    = 0xC010   # 8 × 4 bytes
VBLANK_FLAG  = 0xC100
JOY_CUR      = 0xC101
JOY_PREV     = 0xC102
MUSIC_CTR    = 0xC103
MUSIC_PTR_LO = 0xC104
MUSIC_PTR_HI = 0xC105
ALL_COLL     = 0xC106
OAM_BUF      = 0xC300   # 160 bytes shadow OAM
HRAM_DMA     = 0xFF80   # DMA wait routine lives here

# GBC IO offsets from 0xFF00
P1    = 0x00  # Joypad
NR10  = 0x10; NR11 = 0x11; NR12 = 0x12; NR13 = 0x13; NR14 = 0x14
NR50  = 0x24; NR51 = 0x25; NR52 = 0x26
LCDC  = 0x40; STAT = 0x41; SCY  = 0x42; SCX  = 0x43
LY    = 0x44; LYC  = 0x45; DMA  = 0x46
VBK   = 0x4F
BCPS  = 0x68; BCPD = 0x69
OCPS  = 0x6A; OCPD = 0x6B
IE    = 0xFF  # Interrupt Enable (absolute address 0xFFFF)

# ================================================================
#  ROM BUILD
# ================================================================
def build():
    rom = ROM(32768)

    # ---- RST vectors (0x0000-0x003F): all RETI ----
    for a in range(0x0000, 0x0040):
        rom.data[a] = 0xD9

    # ---- VBlank ISR at 0x0040 (8 bytes) ----
    rom.seek(0x0040)
    rom.PUSH_AF()
    rom.LD_A_n(1)
    rom.LD_nn_A(VBLANK_FLAG)
    rom.POP_AF()
    rom.RETI()
    assert rom.pos <= 0x0048, f"VBlank ISR overflowed: {rom.pos:#x}"

    # ---- Other ISR stubs ----
    for a in (0x0048, 0x0050, 0x0058, 0x0060):
        rom.seek(a); rom.RETI()

    # ---- Entry point at 0x0100 ----
    rom.seek(0x0100)
    rom.NOP()
    rom.JP('main')

    # ---- MAIN at 0x0150 ----
    rom.seek(0x0150)
    rom.label('main')

    # Initialize stack
    rom.LD_SP_nn(0xFFFE)
    rom.DI()

    # Wait for VBlank before disabling LCD (LY >= 144 = in VBlank)
    rom.label('wvb1')
    rom.LDH_A_n(LY)
    rom.CP_n(144)
    rom.JR_C('wvb1')   # loop while LY < 144

    # Disable LCD (clear bit 7 of LCDC)
    rom.XOR_A()
    rom.LDH_n_A(LCDC)

    # ----- Clear WRAM C000-C1FF -----
    rom.LD_HL_nn(0xC000)
    rom.LD_BC_nn(0x0200)
    rom.XOR_A()
    rom.label('clrwram')
    rom.LD_HLI_A()
    rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C()
    rom.JR_NZ('clrwram')

    # ----- Clear OAM buffer -----
    rom.LD_HL_nn(OAM_BUF)
    rom.LD_B_n(160)
    rom.XOR_A()
    rom.label('clroam')
    rom.LD_HLI_A()
    rom.DEC_B()
    rom.JR_NZ('clroam')

    # ----- Switch VBK=0: load tile data to VRAM 0x8000 -----
    rom.XOR_A()
    rom.LDH_n_A(VBK)

    # Clear VRAM bank 0 first (8KB)
    rom.LD_HL_nn(0x8000)
    rom.LD_BC_nn(0x2000)
    rom.XOR_A()
    rom.label('clrvram0')
    rom.LD_HLI_A()
    rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C()
    rom.JR_NZ('clrvram0')

    # Copy tile data from ROM to 0x8000
    rom.LD_DE_nn(0)        # source = tile_data_addr, will patch below
    TILE_SRC_PATCH = rom.pos - 2   # remember address to patch
    rom.LD_HL_nn(0x8000)   # dest
    rom.LD_BC_nn(256*16)   # count (all 256 tiles = 4096 bytes)
    rom.CALL('memcpy')

    # Copy BG tile map to VRAM 0x9800 (VBK=0 still)
    rom.LD_DE_nn(0)
    BG_MAP_SRC_PATCH = rom.pos - 2
    rom.LD_HL_nn(0x9800)
    rom.LD_BC_nn(18*32)
    rom.CALL('memcpy')

    # ----- Switch VBK=1: load BG attributes -----
    rom.LD_A_n(1)
    rom.LDH_n_A(VBK)

    # Clear VRAM bank 1 (just the map area 0x9800-0x9C00)
    rom.LD_HL_nn(0x9800)
    rom.LD_BC_nn(0x0400)
    rom.XOR_A()
    rom.label('clrvram1')
    rom.LD_HLI_A()
    rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C()
    rom.JR_NZ('clrvram1')

    # Copy BG attributes to VRAM bank 1 at 0x9800
    rom.LD_DE_nn(0)
    BG_ATTR_SRC_PATCH = rom.pos - 2
    rom.LD_HL_nn(0x9800)
    rom.LD_BC_nn(18*32)
    rom.CALL('memcpy')

    # Switch back to VBK=0
    rom.XOR_A()
    rom.LDH_n_A(VBK)

    # ----- Set BG color palettes (BCPS/BCPD) -----
    rom.LD_A_n(0x80)        # auto-increment, start at byte 0
    rom.LDH_n_A(BCPS)
    rom.LD_DE_nn(0)
    BG_PAL_PATCH = rom.pos - 2
    rom.LD_B_n(64)          # 8 palettes × 4 colors × 2 bytes
    rom.label('bg_pal_loop')
    rom.LD_A_DE()
    rom.LDH_n_A(BCPD)
    rom.INC_DE()
    rom.DEC_B()
    rom.JR_NZ('bg_pal_loop')

    # ----- Set OBJ color palettes (OCPS/OCPD) -----
    rom.LD_A_n(0x80)
    rom.LDH_n_A(OCPS)
    rom.LD_DE_nn(0)
    OBJ_PAL_PATCH = rom.pos - 2
    rom.LD_B_n(64)
    rom.label('obj_pal_loop')
    rom.LD_A_DE()
    rom.LDH_n_A(OCPD)
    rom.INC_DE()
    rom.DEC_B()
    rom.JR_NZ('obj_pal_loop')

    # ----- Copy DMA wait routine to HRAM (0xFF80) -----
    # DMA wait routine bytes: LD A,40; DEC A; JR NZ,-2; RET
    rom.LD_HL_nn(HRAM_DMA)
    rom.LD_A_n(0x3E); rom.LD_HLI_A()   # LD A, n opcode
    rom.LD_A_n(40);   rom.LD_HLI_A()   # 40 iterations
    rom.LD_A_n(0x3D); rom.LD_HLI_A()   # DEC A
    rom.LD_A_n(0x20); rom.LD_HLI_A()   # JR NZ
    rom.LD_A_n(0xFD); rom.LD_HLI_A()   # -3 (back to DEC A)
    rom.LD_A_n(0xC9); rom.LD_HLI_A()   # RET

    # ----- Init sound -----
    rom.LD_A_n(0x80)
    rom.LDH_n_A(NR52)   # Master sound enable
    rom.LD_A_n(0x77)
    rom.LDH_n_A(NR50)   # Max volume both sides
    rom.LD_A_n(0xFF)
    rom.LDH_n_A(NR51)   # All channels both sides
    rom.LD_A_n(0x80)    # 50% duty, continuous
    rom.LDH_n_A(NR11)
    rom.LD_A_n(0xF0)    # Max volume, no decay
    rom.LDH_n_A(NR12)

    # ----- Init game variables -----
    rom.LD_A_n(76)          # player_x = 76 (near center)
    rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(64)          # player_y = 64
    rom.LD_nn_A(PLAYER_Y)
    rom.XOR_A()
    rom.LD_nn_A(PLAYER_DIR)
    rom.LD_nn_A(PLAYER_FRAME)
    rom.LD_nn_A(ANIM_CTR)
    rom.LD_nn_A(SCORE)
    rom.LD_A_n(1)
    rom.LD_nn_A(SCORE_DIRTY)  # force initial score display

    # Init music pointer
    rom.LD_DE_nn(0)
    MUS_PTR_PATCH = rom.pos - 2
    rom.LD_A_n(1)
    rom.LD_nn_A(MUSIC_CTR)    # trigger first note on frame 1

    # Patch music pointer into init code
    # (will be done after we know music_data address)

    # Init collectibles
    rom.LD_DE_nn(0)
    COLL_INIT_SRC_PATCH = rom.pos - 2
    rom.LD_HL_nn(COLL_DATA)
    rom.LD_BC_nn(8*4)
    rom.CALL('memcpy')

    # ----- Enable LCD -----
    # LCDC = 0x97: LCD on | tile data 0x8000 | 8x16 OBJ | OBJ on | BG on | BG priority
    rom.LD_A_n(0x97)
    rom.LDH_n_A(LCDC)

    # ----- Enable interrupts -----
    rom.LD_A_n(0x01)      # VBlank only
    rom.LD_nn_A(0xFFFF)   # IE register (absolute address)
    rom.EI()

    # Init music ptr via WRAM (music_data address patched later)
    # We wrote to MUSIC_PTR_LO/HI via LD_DE + store approach below:
    # Actually we need to store the address of music_data to MUSIC_PTR_LO/HI
    # We'll patch this by directly writing music_data address into ROM after we know it
    # For now emit placeholder code that reads MUSIC_CTR and sets music ptr
    # --> Handled via MUS_PTR_PATCH above: we patch DE before storing to WRAM

    # Store music ptr (patched later from LD DE,nn)
    rom.LD_A_n(0)    # placeholder lo
    MUS_LO_PATCH2 = rom.pos - 1
    rom.LD_nn_A(MUSIC_PTR_LO)
    rom.LD_A_n(0)    # placeholder hi
    MUS_HI_PATCH2 = rom.pos - 1
    rom.LD_nn_A(MUSIC_PTR_HI)

    # =================== MAIN GAME LOOP ===================
    rom.label('game_loop')
    rom.HALT()

    # Check vblank flag
    rom.LD_A_nn(VBLANK_FLAG)
    rom.CP_n(0)
    rom.JR_Z('game_loop')   # not VBlank, keep waiting

    # Clear flag
    rom.XOR_A()
    rom.LD_nn_A(VBLANK_FLAG)

    # --- Frame processing ---
    rom.CALL('read_joypad')
    rom.CALL('handle_input')
    rom.CALL('check_collisions')
    rom.CALL('update_oam')
    rom.CALL('do_dma')
    rom.CALL('music_tick')
    rom.CALL('check_all_collected')
    rom.CALL('update_score_display')

    rom.JP('game_loop')

    # ===================== SUBROUTINES =====================

    # ---- memcpy: copy BC bytes from DE to HL ----
    rom.label('memcpy')
    rom.LD_A_DE()
    rom.LD_HLI_A()
    rom.INC_DE()
    rom.DEC_BC()
    rom.LD_A_B(); rom.OR_C()
    rom.JR_NZ('memcpy')
    rom.RET()

    # ---- do_dma: trigger OAM DMA from OAM_BUF (0xC300) ----
    rom.label('do_dma')
    rom.LD_A_n(OAM_BUF >> 8)   # high byte = 0xC3
    rom.LDH_n_A(DMA)            # start OAM DMA
    rom.CALL(HRAM_DMA)          # wait ~160 cycles in HRAM
    rom.RET()

    # ---- read_joypad ----
    rom.label('read_joypad')
    # Save previous
    rom.LD_A_nn(JOY_CUR)
    rom.LD_nn_A(JOY_PREV)
    # Select buttons first (good practice)
    rom.LD_A_n(0x20)
    rom.LDH_n_A(P1)
    rom.LDH_n_A(P1)   # wait
    rom.LDH_A_n(P1)   # discard
    # Select D-pad
    rom.LD_A_n(0x10)
    rom.LDH_n_A(P1)
    rom.LDH_n_A(P1)
    rom.LDH_n_A(P1)
    rom.LDH_A_n(P1)
    rom.AND_n(0x0F)
    rom.XOR_A(); rom.ADD_A_n(0x0F)  # A = 0x0F
    # invert: pressed bits are 0, we want 1
    rom.LD_A_n(0x0F)
    # read P1 again
    rom.LDH_A_n(P1)
    rom.AND_n(0x0F)
    rom.XOR_A()
    # Simpler approach: read dpad, invert bottom nibble
    rom.LDH_A_n(P1)       # re-read
    rom.AND_n(0x0F)
    # XOR with 0x0F to invert (0=pressed → 1)
    rom.emit(0xEE, 0x0F)  # XOR n
    rom.LD_nn_A(JOY_CUR)
    # Reset P1 to no-select
    rom.LD_A_n(0x30)
    rom.LDH_n_A(P1)
    rom.RET()

    # ---- handle_input: update player position & direction ----
    rom.label('handle_input')
    rom.LD_A_nn(JOY_CUR)
    rom.LD_B_A()              # B = joypad state

    rom.LD_A_n(0)             # moving flag
    rom.LD_nn_A(0xC120)       # MOVING temp

    # Right (bit 0)
    rom.BIT_b_B(0)
    rom.JR_Z('no_right')
    rom.LD_A_nn(PLAYER_X)
    rom.INC_A()
    rom.CP_n(153)             # max x = 152
    rom.JR_NC('no_right_mv')
    rom.LD_nn_A(PLAYER_X)
    rom.label('no_right_mv')
    rom.LD_A_n(0)             # dir = right
    rom.LD_nn_A(PLAYER_DIR)
    rom.LD_A_n(1)
    rom.LD_nn_A(0xC120)       # moving = 1
    rom.label('no_right')

    # Left (bit 1)
    rom.BIT_b_B(1)
    rom.JR_Z('no_left')
    rom.LD_A_nn(PLAYER_X)
    rom.CP_n(1)               # don't go below 1
    rom.JR_Z('no_left')
    rom.JR_C('no_left')
    rom.DEC_A()
    rom.LD_nn_A(PLAYER_X)
    rom.LD_A_n(1)             # dir = left
    rom.LD_nn_A(PLAYER_DIR)
    rom.LD_nn_A(0xC120)
    rom.label('no_left')

    # Up (bit 2)
    rom.BIT_b_B(2)
    rom.JR_Z('no_up')
    rom.LD_A_nn(PLAYER_Y)
    rom.CP_n(9)               # min y = 8 (below score bar)
    rom.JR_Z('no_up')
    rom.JR_C('no_up')
    rom.DEC_A()
    rom.LD_nn_A(PLAYER_Y)
    rom.LD_A_n(1)
    rom.LD_nn_A(0xC120)
    rom.label('no_up')

    # Down (bit 3)
    rom.BIT_b_B(3)
    rom.JR_Z('no_down')
    rom.LD_A_nn(PLAYER_Y)
    rom.INC_A()
    rom.CP_n(129)             # max y = 128
    rom.JR_NC('no_down_mv')
    rom.LD_nn_A(PLAYER_Y)
    rom.label('no_down_mv')
    rom.LD_A_n(1)
    rom.LD_nn_A(0xC120)
    rom.label('no_down')

    # Animation (only when moving)
    rom.LD_A_nn(0xC120)
    rom.CP_n(0)
    rom.JR_Z('no_anim')
    rom.LD_A_nn(ANIM_CTR)
    rom.INC_A()
    rom.CP_n(12)              # toggle every 12 frames
    rom.JR_C('anim_ok')
    rom.XOR_A()
    # Toggle frame
    rom.LD_nn_A(ANIM_CTR)
    rom.LD_A_nn(PLAYER_FRAME)
    rom.emit(0xEE, 0x01)      # XOR 1 (toggle)
    rom.LD_nn_A(PLAYER_FRAME)
    rom.JR('anim_done')
    rom.label('anim_ok')
    rom.LD_nn_A(ANIM_CTR)
    rom.label('anim_done')
    rom.label('no_anim')
    rom.RET()

    # ---- check_collisions ----
    rom.label('check_collisions')
    rom.LD_HL_nn(COLL_DATA)
    rom.LD_B_n(8)

    rom.label('coll_loop')
    # Read coll.x into E, coll.y into D
    rom.LD_E_HL()             # E = coll.x
    rom.INC_HL()
    rom.LD_D_HL()             # D = coll.y
    rom.INC_HL()
    rom.INC_HL()              # skip type
    rom.LD_A_HL()             # A = active
    rom.INC_HL()              # HL now → next entry

    # Push B and HL to preserve them
    rom.PUSH_BC()
    rom.PUSH_HL()

    rom.CP_n(0)
    rom.JR_Z('coll_skip')     # not active, skip

    # Check |player_x - E| < 10
    rom.LD_A_nn(PLAYER_X)
    rom.SUB_E()               # A = player_x - coll_x
    rom.JR_NC('px_pos')
    rom.CPL(); rom.INC_A()    # negate
    rom.label('px_pos')
    rom.CP_n(10)
    rom.JR_NC('coll_skip')    # |dx| >= 10, no hit

    # Check |player_y - D| < 10
    rom.LD_A_nn(PLAYER_Y)
    rom.SUB_D()               # A = player_y - coll_y
    rom.JR_NC('py_pos')
    rom.CPL(); rom.INC_A()
    rom.label('py_pos')
    rom.CP_n(10)
    rom.JR_NC('coll_skip')    # |dy| >= 10, no hit

    # Collision! HL is at next entry's x; go back 1 to active byte
    rom.POP_HL()
    rom.DEC_HL()              # back to active byte
    rom.XOR_A()
    rom.LD_HL_A()             # deactivate
    rom.INC_HL()              # advance past active

    # Increment score
    rom.LD_A_nn(SCORE)
    rom.INC_A()
    rom.CP_n(100)             # cap at 99
    rom.JR_C('score_ok')
    rom.LD_A_n(99)
    rom.label('score_ok')
    rom.LD_nn_A(SCORE)
    rom.LD_A_n(1)
    rom.LD_nn_A(SCORE_DIRTY)

    rom.POP_BC()
    rom.DEC_B()
    rom.JR_NZ('coll_loop')
    rom.RET()

    rom.label('coll_skip')
    rom.POP_HL()
    rom.POP_BC()
    rom.DEC_B()
    rom.JR_NZ('coll_loop')
    rom.RET()

    # ---- update_oam: fill OAM_BUF shadow ----
    rom.label('update_oam')
    rom.LD_HL_nn(OAM_BUF)

    # Entry 0: Bunny
    rom.LD_A_nn(PLAYER_Y)
    rom.ADD_A_n(16)           # OAM Y offset
    rom.LD_HLI_A()
    rom.LD_A_nn(PLAYER_X)
    rom.ADD_A_n(8)            # OAM X offset
    rom.LD_HLI_A()
    # Tile: frame 0 → tile 0x00, frame 1 → tile 0x02
    rom.LD_A_nn(PLAYER_FRAME)
    rom.ADD_A_A()             # *2
    rom.LD_HLI_A()
    # Attr: palette 0, x-flip if facing left
    # dir=1 → 0x20; dir=0 → 0x00
    rom.LD_A_nn(PLAYER_DIR)
    rom.RLCA(); rom.RLCA(); rom.RLCA(); rom.RLCA(); rom.RLCA()  # dir<<5
    rom.AND_n(0x20)           # keep only bit 5
    rom.LD_HLI_A()            # attr (palette 0 | x-flip)

    # Entries 1-8: collectibles
    rom.LD_DE_nn(COLL_DATA)
    rom.LD_B_n(8)

    rom.label('oam_coll_loop')
    # Read x, y from DE using LD A,(DE) repeatedly
    rom.LD_A_DE()             # x
    rom.INC_DE()
    rom.PUSH_AF()             # save x
    rom.LD_A_DE()             # y
    rom.INC_DE()
    rom.PUSH_AF()             # save y
    rom.LD_A_DE()             # type
    rom.INC_DE()
    rom.LD_C_A()              # C = type
    rom.LD_A_DE()             # active
    rom.INC_DE()
    rom.CP_n(0)
    rom.JR_Z('hide_coll_oam')

    # Active: write OAM entry
    rom.POP_AF()              # y
    rom.ADD_A_n(16)
    rom.LD_HLI_A()
    rom.POP_AF()              # x
    rom.ADD_A_n(8)
    rom.LD_HLI_A()
    # tile: star=0x08 (type 0), flower=0x09 (type 1)
    rom.LD_A_C()
    rom.ADD_A_n(TL_STAR)
    rom.LD_HLI_A()
    # palette: star=1, flower=2
    rom.LD_A_C()
    rom.INC_A()               # type 0 → pal 1, type 1 → pal 2
    rom.LD_HLI_A()
    rom.JR('oam_coll_next')

    rom.label('hide_coll_oam')
    rom.POP_AF()              # discard y
    rom.POP_AF()              # discard x
    rom.XOR_A()
    rom.LD_HLI_A(); rom.LD_HLI_A()
    rom.LD_HLI_A(); rom.LD_HLI_A()

    rom.label('oam_coll_next')
    rom.DEC_B()
    rom.JR_NZ('oam_coll_loop')

    # Fill remaining OAM entries (entries 9-39 = 31 entries × 4 bytes)
    rom.LD_B_n(31)
    rom.XOR_A()
    rom.label('fill_oam_rest')
    rom.LD_HLI_A(); rom.LD_HLI_A()
    rom.LD_HLI_A(); rom.LD_HLI_A()
    rom.DEC_B()
    rom.JR_NZ('fill_oam_rest')
    rom.RET()

    # ---- music_tick ----
    rom.label('music_tick')
    rom.LD_A_nn(MUSIC_CTR)
    rom.DEC_A()
    rom.LD_nn_A(MUSIC_CTR)
    rom.RET_NZ()

    # Load music pointer into HL
    rom.LD_A_nn(MUSIC_PTR_LO)
    rom.LD_L_A()
    rom.LD_A_nn(MUSIC_PTR_HI)
    rom.LD_H_A()

    # Check end marker
    rom.LD_A_HL()
    rom.CP_n(0xFF)
    rom.JR_NZ('play_note')
    # Reset to start
    rom.LD_DE_nn(0)
    MUS_RESET_PATCH = rom.pos - 2
    rom.LD_H_D()
    rom.LD_L_E()

    rom.label('play_note')
    rom.LD_A_HLI()
    rom.LDH_n_A(NR13)         # freq lo
    rom.LD_A_HLI()
    rom.LDH_n_A(NR14)         # freq hi + trigger
    rom.LD_A_HLI()
    rom.LD_nn_A(MUSIC_CTR)    # duration

    # Save new HL
    rom.LD_A_H()
    rom.LD_nn_A(MUSIC_PTR_HI)
    rom.LD_A_L()
    rom.LD_nn_A(MUSIC_PTR_LO)
    rom.RET()

    # ---- check_all_collected ----
    rom.label('check_all_collected')
    rom.LD_HL_nn(COLL_DATA + 3)   # point to first active byte
    rom.LD_B_n(8)
    rom.label('chk_coll_loop')
    rom.LD_A_HL()
    rom.CP_n(1)
    rom.RET_Z()               # found an active one, return (not all done)
    # Advance to next entry's active byte (+4)
    rom.INC_HL(); rom.INC_HL(); rom.INC_HL(); rom.INC_HL()
    rom.DEC_B()
    rom.JR_NZ('chk_coll_loop')

    # All collected! Reset all collectibles
    rom.LD_DE_nn(0)
    COLL_RESET_PATCH = rom.pos - 2
    rom.LD_HL_nn(COLL_DATA)
    rom.LD_BC_nn(8*4)
    rom.CALL('memcpy')
    # Play a jingle (briefly raise NR12 for a chord)
    rom.LD_A_n(0xF0)
    rom.LDH_n_A(NR12)
    rom.RET()

    # ---- update_score_display ----
    rom.label('update_score_display')
    rom.LD_A_nn(SCORE_DIRTY)
    rom.CP_n(0)
    rom.RET_Z()
    rom.XOR_A()
    rom.LD_nn_A(SCORE_DIRTY)

    # Convert score to digits
    rom.LD_A_nn(SCORE)
    rom.LD_B_A()              # B = score

    # Hundreds
    rom.LD_C_n(0)
    rom.label('hund_loop')
    rom.LD_A_B(); rom.CP_n(100)
    rom.JR_C('hund_done')
    rom.SUB_A_n(100)
    rom.LD_B_A()
    rom.INC_C()
    rom.JR('hund_loop')
    rom.label('hund_done')
    rom.LD_A_C(); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x9802)    # row 0, col 2 of BG map
    rom.LD_HL_A()

    # Tens
    rom.LD_C_n(0)
    rom.label('tens_loop')
    rom.LD_A_B(); rom.CP_n(10)
    rom.JR_C('tens_done')
    rom.SUB_A_n(10)
    rom.LD_B_A()
    rom.INC_C()
    rom.JR('tens_loop')
    rom.label('tens_done')
    rom.LD_A_C(); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x9803)
    rom.LD_HL_A()

    # Ones = B
    rom.LD_A_B(); rom.ADD_A_n(TL_DIGIT_0)
    rom.LD_HL_nn(0x9804)
    rom.LD_HL_A()
    rom.RET()

    # ====================================================
    # DATA SECTION — align to 0x0500 boundary for tidiness
    # ====================================================
    # Pad up to 0x0500
    while rom.pos < 0x0500:
        rom.emit(0x00)

    # ---- Tile data ----
    TILE_DATA_ADDR = rom.pos
    tile_bytes = build_tile_data()
    for b in tile_bytes:
        rom.emit(b)

    # ---- BG tile map ----
    BG_MAP_ADDR = rom.pos
    bg_tiles, bg_attrs = build_bg_map()
    for b in bg_tiles:
        rom.emit(b)

    # ---- BG attributes ----
    BG_ATTR_ADDR = rom.pos
    for b in bg_attrs:
        rom.emit(b)

    # ---- BG color palettes ----
    BG_PAL_ADDR = rom.pos
    for b in palettes_to_bytes(BG_PALETTES):
        rom.emit(b)

    # ---- OBJ color palettes ----
    OBJ_PAL_ADDR = rom.pos
    for b in palettes_to_bytes(OBJ_PALETTES):
        rom.emit(b)

    # ---- Music data ----
    MUSIC_DATA_ADDR = rom.pos
    for b in MUSIC_DATA:
        rom.emit(b)

    # ---- Collectible init data ----
    COLL_INIT_ADDR = rom.pos
    for (x, y, t, a) in INIT_COLLECTS:
        rom.emit(x, y, t, a)

    # ====================================================
    # PATCH source addresses into init code
    # ====================================================
    def patch16(pos, addr):
        rom.data[pos]   = addr & 0xFF
        rom.data[pos+1] = (addr >> 8) & 0xFF

    patch16(TILE_SRC_PATCH,     TILE_DATA_ADDR)
    patch16(BG_MAP_SRC_PATCH,   BG_MAP_ADDR)
    patch16(BG_ATTR_SRC_PATCH,  BG_ATTR_ADDR)
    patch16(BG_PAL_PATCH,       BG_PAL_ADDR)
    patch16(OBJ_PAL_PATCH,      OBJ_PAL_ADDR)
    patch16(MUS_PTR_PATCH,      MUSIC_DATA_ADDR)  # initial LD DE,nn for music ptr
    patch16(MUS_RESET_PATCH,    MUSIC_DATA_ADDR)  # music reset also
    patch16(COLL_INIT_SRC_PATCH,COLL_INIT_ADDR)
    patch16(COLL_RESET_PATCH,   COLL_INIT_ADDR)

    # Patch the two LD A,n / LD (MUSIC_PTR_LO/HI),A stores
    rom.data[MUS_LO_PATCH2] = MUSIC_DATA_ADDR & 0xFF
    rom.data[MUS_HI_PATCH2] = (MUSIC_DATA_ADDR >> 8) & 0xFF

    # ====================================================
    # RESOLVE LABELS
    # ====================================================
    rom.resolve()

    # ====================================================
    # HEADER
    # ====================================================
    rom.set_header("BUNNYGARDEN")

    print(f"ROM built successfully.")
    print(f"  Tile data:       0x{TILE_DATA_ADDR:04X}")
    print(f"  BG map:          0x{BG_MAP_ADDR:04X}")
    print(f"  BG attributes:   0x{BG_ATTR_ADDR:04X}")
    print(f"  BG palettes:     0x{BG_PAL_ADDR:04X}")
    print(f"  OBJ palettes:    0x{OBJ_PAL_ADDR:04X}")
    print(f"  Music data:      0x{MUSIC_DATA_ADDR:04X}")
    print(f"  Coll init:       0x{COLL_INIT_ADDR:04X}")
    print(f"  Code end:        0x{0x0500:04X}")
    print(f"  Data end:        0x{rom.pos:04X}")
    return rom

if __name__ == '__main__':
    rom = build()
    out_path = '/mnt/user-data/outputs/BunnyGarden.gbc'
    with open(out_path, 'wb') as f:
        f.write(rom.data)
    print(f"\nWrote {len(rom.data)} bytes → {out_path}")
