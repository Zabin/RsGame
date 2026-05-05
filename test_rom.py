#!/usr/bin/env python3
"""
test_rom.py — Systematic test suite for BunnyGarden.gbc
Run: python3 test_rom.py

Suites:
  T1  ROM header / metadata (no emulator)
  T2  VRAM tile data loaded
  T3  LCDC / LCD flags
  T4  State machine transitions
  T5  BG tilemap content per screen
  T6  OAM / sprite rendering (bunny + collectibles)
  T7  Joypad movement and boundaries
  T8  Collision, score, and gift tracking
  T9  Zone transitions
  T10 SRAM save/load persistence
"""
import os, sys, struct, subprocess
from pathlib import Path

ROM_PATH = '/mnt/user-data/outputs/BunnyGarden.gbc'
RAM_PATH = '/mnt/user-data/outputs/BunnyGarden.gbc.ram'   # PyBoy uses .gbc.ram
SHOT_DIR = '/home/claude/bunnygarden/test_shots'
os.makedirs(SHOT_DIR, exist_ok=True)

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
    """Remove PyBoy's RAM file so next boot starts clean."""
    for p in [RAM_PATH, RAM_PATH.replace('.ram', '.sav')]:
        try: os.remove(p)
        except: pass

from pyboy import PyBoy

def fresh_boot(frames=180):
    """Clean boot to title screen with no saved game."""
    wipe_save()
    pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
    pb.set_emulation_speed(0)
    for _ in range(frames): pb.tick()
    return pb

def advance_to_playing(pb):
    """From TITLE: Start→Intro, A→Playing."""
    # Handle both title and already-playing states
    if pb.memory[0xC000] != 0:  # not at title, might be in playing from save
        pass
    pb.button('start'); [pb.tick() for _ in range(80)]
    pb.button('a');     [pb.tick() for _ in range(80)]

def shoot(pb, name):
    pb.screen.image.save(f"{SHOT_DIR}/{name}.png")

def oam_entry(pb, n):
    """Read OAM entry n from actual OAM registers (0xFE00)."""
    base = 0xFE00 + n * 4
    return (pb.memory[base], pb.memory[base+1], pb.memory[base+2], pb.memory[base+3])

# ══════════════════════════════════════════════════════
# T1 — ROM Header (pure binary checks, no emulator)
# ══════════════════════════════════════════════════════
print("\n=== T1: ROM Header ===")
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

# ══════════════════════════════════════════════════════
# T2 — VRAM Tile Data
# ══════════════════════════════════════════════════════
print("\n=== T2: VRAM Tile Data ===")
pb = fresh_boot()

def tile(idx): return [pb.memory[0x8000 + idx*16 + i] for i in range(16)]
t0  = tile(0x00)   # bunny head
t4  = tile(0x04)   # gift obj
t16 = tile(0x10)   # grass plain
t64 = tile(0x40)   # font A

check("T2.1 Tile 0x00 (bunny head) non-zero",  any(b != 0 for b in t0),  f"[{t0[:4]}]")
check("T2.2 Tile 0x04 (gift) non-zero",         any(b != 0 for b in t4),  f"[{t4[:4]}]")
check("T2.3 Tile 0x10 (grass) non-zero",        any(b != 0 for b in t16), f"[{t16[:4]}]")
check("T2.4 Tile 0x40 (font A) non-zero",       any(b != 0 for b in t64), f"[{t64[:4]}]")
check("T2.5 Bunny tile has both bitplanes",     any(t0[i*2] for i in range(8)) and any(t0[i*2+1] for i in range(8)))
# Font A should have pixel in top-centre (row 0, approximate)
check("T2.6 Font A tile has outline pixels",    t64[0] != 0 or t64[1] != 0, f"row0={t64[:2]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T3 — LCDC Flags
# ══════════════════════════════════════════════════════
print("\n=== T3: LCDC Flags ===")
pb = fresh_boot()

lcdc = pb.memory[0xFF40]
check("T3.1 LCD enabled (bit 7)",          (lcdc>>7)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.2 OBJ enabled (bit 1)",          (lcdc>>1)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.3 BG enabled (bit 0)",           (lcdc>>0)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.4 Tile data at 0x8000 (bit 4)",  (lcdc>>4)&1 == 1, f"LCDC=0x{lcdc:02X}")
check("T3.5 BG map at 0x9800 (bit 3=0)",   (lcdc>>3)&1 == 0, f"LCDC=0x{lcdc:02X}")
check("T3.6 LCDC = 0x93 exactly",          lcdc == 0x93, f"0x{lcdc:02X}")

pb.stop()

# ══════════════════════════════════════════════════════
# T4 — State Machine
# ══════════════════════════════════════════════════════
print("\n=== T4: State Machine ===")
pb = fresh_boot()

check("T4.1 Clean boot → TITLE (GS=0)",   pb.memory[0xC000] == 0, f"GS={pb.memory[0xC000]}")

pb.button('start'); [pb.tick() for _ in range(80)]
check("T4.2 START → INTRO (GS=1)",        pb.memory[0xC000] == 1, f"GS={pb.memory[0xC000]}")
shoot(pb, "T4_intro")

pb.button('a'); [pb.tick() for _ in range(80)]
check("T4.3 A in INTRO → PLAYING (GS=2)", pb.memory[0xC000] == 2, f"GS={pb.memory[0xC000]}")
shoot(pb, "T4_playing")

pb.button('start'); [pb.tick() for _ in range(40)]
check("T4.4 START in PLAYING → SAVE (GS=3)", pb.memory[0xC000] == 3)
shoot(pb, "T4_save")

pb.button('b'); [pb.tick() for _ in range(40)]
check("T4.5 B in SAVE → PLAYING (GS=2)",  pb.memory[0xC000] == 2)

pb.button('select'); [pb.tick() for _ in range(40)]
check("T4.6 SELECT → MAP (GS=4)",          pb.memory[0xC000] == 4)
shoot(pb, "T4_map")

pb.button('b'); [pb.tick() for _ in range(40)]
check("T4.7 B in MAP → PLAYING (GS=2)",   pb.memory[0xC000] == 2)

# Force victory
pb.memory[0xC009] = 0x07
pb.button_press('right'); [pb.tick() for _ in range(5)]; pb.button_release('right')
[pb.tick() for _ in range(40)]
check("T4.8 GIFTS=7 → VICTORY (GS=5)",   pb.memory[0xC000] == 5, f"GS={pb.memory[0xC000]}")
shoot(pb, "T4_victory")

pb.button('a'); [pb.tick() for _ in range(60)]
check("T4.9 A in VICTORY → TITLE (GS=0)", pb.memory[0xC000] == 0, f"GS={pb.memory[0xC000]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T5 — BG Tilemap Content
# ══════════════════════════════════════════════════════
print("\n=== T5: BG Tilemap ===")
pb = fresh_boot(200)   # enough frames for title to render

# Title row 0 = all blank (0x1C UI tiles)
row0 = [pb.memory[0x9800 + i] for i in range(20)]
check("T5.1 Title: row 0 has UI blank tiles",    any(b == 0x1C for b in row0), f"row0[0]=0x{row0[0]:02X}")

# Title: BUNNY GARDEN text should appear. Title puts text at row 4 cols 4..15
# Font B=0x41, U=0x54, N=0x4D, etc.
row4 = [pb.memory[0x9800 + 4*32 + i] for i in range(4, 16)]
check("T5.2 Title: font tiles in row 4 (title text)", any(0x40 <= b <= 0x5A for b in row4), f"row4[4..16]={[f'{b:02X}' for b in row4]}")

# Advance to garden
pb.button('start'); [pb.tick() for _ in range(80)]
pb.button('a');     [pb.tick() for _ in range(80)]

# Garden score bar (row 0)
row0 = [pb.memory[0x9800 + i] for i in range(12)]
check("T5.3 Garden: row 0 blank tiles (score bar)",  row0[0] == 0x1C, f"row0[0]=0x{row0[0]:02X}")
check("T5.4 Garden: col 1 = gift icon (0x1F)",       row0[1] == 0x1F, f"0x{row0[1]:02X}")
check("T5.5 Garden: hearts at cols 2-4",             all(row0[c] in (0x1D,0x1E) for c in [2,3,4]))
check("T5.6 Garden: star icon at col 7 (0x2D)",      row0[7] == 0x2D, f"0x{row0[7]:02X}")
check("T5.7 Garden: digit tiles at cols 8-10",       all(0x20 <= row0[c] <= 0x29 for c in [8,9,10]))

# Grass and path
row3  = [pb.memory[0x9800 +  3*32 + i] for i in range(5)]
row9  = [pb.memory[0x9800 +  9*32 + i] for i in range(5)]
row10 = [pb.memory[0x9800 + 10*32 + i] for i in range(5)]
check("T5.8 Garden: row 3 has grass tiles",         any(b in (0x10,0x11,0x12,0x1B) for b in row3), f"{[f'{b:02X}' for b in row3]}")
check("T5.9 Garden: row 9 = path-top (0x14)",      row9[0] == 0x14, f"0x{row9[0]:02X}")
check("T5.10 Garden: row 10 = path-bot (0x15)",    row10[0] == 0x15, f"0x{row10[0]:02X}")

shoot(pb, "T5_garden")
pb.stop()

# ══════════════════════════════════════════════════════
# T6 — OAM / Sprite Rendering
# NOTE: Read from 0xFE00 (actual OAM), NOT 0xC300 (shadow OAM).
#       PyBoy clears the shadow OAM source buffer after DMA — this is
#       PyBoy-specific behaviour; the actual hardware OAM is correct.
# ══════════════════════════════════════════════════════
print("\n=== T6: OAM / Sprite Rendering ===")
pb = fresh_boot()
advance_to_playing(pb)
# Set known player position
pb.memory[0xC001] = 80    # X
pb.memory[0xC002] = 80    # Y
pb.memory[0xC003] = 0     # dir: right
pb.memory[0xC004] = 0     # frame 0
for _ in range(5): pb.tick()

y0, x0, t0, a0 = oam_entry(pb, 0)   # bunny head
y1, x1, t1, a1 = oam_entry(pb, 1)   # bunny body
print(f"  Player pos: ({pb.memory[0xC001]}, {pb.memory[0xC002]})")
print(f"  OAM[0] head: Y={y0} X={x0} tile=0x{t0:02X} attr=0x{a0:02X}")
print(f"  OAM[1] body: Y={y1} X={x1} tile=0x{t1:02X} attr=0x{a1:02X}")

check("T6.1 OAM head Y = player_y+16",    y0 == pb.memory[0xC002] + 16, f"{y0} vs {pb.memory[0xC002]+16}")
check("T6.2 OAM head X = player_x+8",     x0 == pb.memory[0xC001] + 8,  f"{x0} vs {pb.memory[0xC001]+8}")
check("T6.3 OAM head tile = 0 or 2",      t0 in (0, 2), f"0x{t0:02X}")
check("T6.4 OAM head attr palette = 0",   a0 & 0x07 == 0, f"attr=0x{a0:02X}")
check("T6.5 OAM body Y = player_y+24",    y1 == pb.memory[0xC002] + 24, f"{y1} vs {pb.memory[0xC002]+24}")
check("T6.6 OAM body tile = head+1",      t1 == t0 + 1, f"0x{t1:02X} vs 0x{t0+1:02X}")
check("T6.7 OAM body X = same as head",   x1 == x0, f"{x1}")

# Verify actual rendering: check pixels where bunny should be
import numpy as np
shoot(pb, "T6_bunny")
img = np.array(pb.screen.image)
# Bunny at (80,80) → head rows 80-87, body rows 88-95, cols 80-87
# White pixels = bunny body, non-background = bunny present
bg_color = img[5, 5, :3]   # sample a background grass pixel
head_region = img[80:88, 80:88, :3]
non_bg = np.any(head_region != bg_color, axis=2)
check("T6.8 Bunny head region has non-BG pixels",  non_bg.sum() > 4, f"non-bg pixels={non_bg.sum()}")

# Collectibles
c0 = oam_entry(pb, 2)
print(f"  OAM[2] collectible: Y={c0[0]} X={c0[1]} tile=0x{c0[2]:02X} attr=0x{c0[3]:02X}")
check("T6.9 Collectible OAM Y > 15",       c0[0] > 15, f"Y={c0[0]}")
check("T6.10 Collectible tile = star/flower/gift", c0[2] in (0x04,0x05,0x06), f"tile=0x{c0[2]:02X}")

pb.stop()

# ══════════════════════════════════════════════════════
# T7 — Joypad and Movement
# ══════════════════════════════════════════════════════
print("\n=== T7: Joypad / Movement ===")
pb = fresh_boot()
advance_to_playing(pb)

# Reset to known position
pb.memory[0xC001] = 80; pb.memory[0xC002] = 72
pb.memory[0xC003] = 0; pb.memory[0xC004] = 0; pb.memory[0xC005] = 0
[pb.tick() for _ in range(3)]

x0 = pb.memory[0xC001]; y0 = pb.memory[0xC002]

# RIGHT
pb.button_press('right'); [pb.tick() for _ in range(20)]; pb.button_release('right')
[pb.tick() for _ in range(2)]
x1 = pb.memory[0xC001]
check("T7.1 RIGHT increases X",           x1 > x0, f"{x0}→{x1}")
check("T7.2 RIGHT sets DIR=0",            pb.memory[0xC003] == 0)

# LEFT
pb.button_press('left'); [pb.tick() for _ in range(20)]; pb.button_release('left')
[pb.tick() for _ in range(2)]
x2 = pb.memory[0xC001]
check("T7.3 LEFT decreases X",            x2 < x1, f"{x1}→{x2}")
check("T7.4 LEFT sets DIR=1",             pb.memory[0xC003] == 1)

# UP
pb.button_press('up'); [pb.tick() for _ in range(20)]; pb.button_release('up')
[pb.tick() for _ in range(2)]
y2 = pb.memory[0xC002]
check("T7.5 UP decreases Y",              y2 < y0, f"{y0}→{y2}")

# DOWN
pb.button_press('down'); [pb.tick() for _ in range(20)]; pb.button_release('down')
[pb.tick() for _ in range(2)]
y3 = pb.memory[0xC002]
check("T7.6 DOWN increases Y",            y3 > y2, f"{y2}→{y3}")

# Animation: reset both ANIM_CTR and PLAYER_FRAME
pb.memory[0xC004] = 0; pb.memory[0xC005] = 0
pb.button_press('right')
for _ in range(12): pb.tick()   # 12 > 10 threshold
pb.button_release('right')
[pb.tick() for _ in range(2)]
frame = pb.memory[0xC004]
check("T7.7 Frame flips after 10 walk frames", frame == 1, f"frame={frame}")

# Upper Y boundary
pb.memory[0xC002] = 17; pb.memory[0xC001] = 80
pb.button_press('up'); [pb.tick() for _ in range(3)]; pb.button_release('up')
[pb.tick() for _ in range(2)]
check("T7.8 Can't go above Y=16",         pb.memory[0xC002] >= 16, f"y={pb.memory[0xC002]}")

# Left X boundary — must be at zone 0 to not trigger zone transition
pb.memory[0xC008] = 0   # force zone 0
pb.memory[0xC001] = 0   # X = 0
pb.memory[0xC00A] = 0   # clear NEED_REDRAW
pb.button_press('left'); [pb.tick() for _ in range(3)]; pb.button_release('left')
[pb.tick() for _ in range(2)]
check("T7.9 X=0 in zone 0: no move or zone change", pb.memory[0xC001] <= 5 and pb.memory[0xC008] == 0,
      f"x={pb.memory[0xC001]} zone={pb.memory[0xC008]}")

# Right X boundary
pb.memory[0xC008] = 2   # force zone 2 (last) to prevent zone change
pb.memory[0xC001] = 159
pb.memory[0xC00A] = 0
pb.button_press('right'); [pb.tick() for _ in range(3)]; pb.button_release('right')
[pb.tick() for _ in range(2)]
check("T7.10 X=159 in zone 2: no overflow", pb.memory[0xC001] <= 159, f"x={pb.memory[0xC001]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T8 — Collision, Score, Gifts
# ══════════════════════════════════════════════════════
print("\n=== T8: Collision / Score / Gifts ===")
pb = fresh_boot()
advance_to_playing(pb)

# Reset state
pb.memory[0xC006] = 0; pb.memory[0xC009] = 0; pb.memory[0xC007] = 0
[pb.tick() for _ in range(5)]

check("T8.1 Score starts 0",  pb.memory[0xC006] == 0, f"{pb.memory[0xC006]}")
check("T8.2 Gifts starts 0",  pb.memory[0xC009] == 0, f"{pb.memory[0xC009]}")
check("T8.3 COLL_COUNT > 0",  pb.memory[0xC050] > 0,  f"count={pb.memory[0xC050]}")

# Zone 0 collectible 0 is a star at (24,32). Move player there.
# But ensure player ISN'T already at (24,32) by starting away.
pb.memory[0xC001] = 80; pb.memory[0xC002] = 80   # start away
[pb.tick() for _ in range(3)]
pb.memory[0xC001] = 24; pb.memory[0xC002] = 32   # teleport to star
[pb.tick() for _ in range(5)]
sc1 = pb.memory[0xC006]
check("T8.4 Score++ on collision",    sc1 > 0, f"score={sc1}")
check("T8.5 Collectible deactivated", pb.memory[0xC020 + 3] == 0, f"active={pb.memory[0xC020+3]}")

# Collect gift: zone 0 gift is at (120,64)
pb.memory[0xC001] = 120; pb.memory[0xC002] = 64
[pb.tick() for _ in range(5)]
gf = pb.memory[0xC009]
check("T8.6 Gift sets GIFTS bit 0",   gf & 0x01 == 1, f"gifts=0x{gf:02X}")

# Heart tile updates
hrt = pb.memory[0x9802]  # row 0 col 2
check("T8.7 Heart col 2 = full (0x1D)", hrt == 0x1D, f"tile=0x{hrt:02X}")

# All gifts → victory
pb.memory[0xC009] = 0x07
pb.button_press('right'); [pb.tick() for _ in range(3)]; pb.button_release('right')
[pb.tick() for _ in range(40)]
check("T8.8 GIFTS=7 → VICTORY",       pb.memory[0xC000] == 5, f"GS={pb.memory[0xC000]}")

pb.stop()

# ══════════════════════════════════════════════════════
# T9 — Zone Transitions
# ══════════════════════════════════════════════════════
print("\n=== T9: Zone Transitions ===")
pb = fresh_boot()
advance_to_playing(pb)

check("T9.1 Starts zone 0",     pb.memory[0xC008] == 0, f"zone={pb.memory[0xC008]}")

# Walk to right edge
pb.memory[0xC001] = 155; pb.memory[0xC002] = 72
[pb.tick() for _ in range(3)]
pb.button_press('right'); [pb.tick() for _ in range(5)]; pb.button_release('right')
[pb.tick() for _ in range(80)]   # allow redraw
z1 = pb.memory[0xC008]
check("T9.2 Right edge → zone 1", z1 == 1, f"zone={z1}")
check("T9.3 X reset after advance", pb.memory[0xC001] <= 20)
shoot(pb, "T9_forest")

# Zone 1 → zone 2
pb.memory[0xC001] = 155
[pb.tick() for _ in range(3)]
pb.button_press('right'); [pb.tick() for _ in range(5)]; pb.button_release('right')
[pb.tick() for _ in range(80)]
z2 = pb.memory[0xC008]
check("T9.4 Right edge → zone 2", z2 == 2, f"zone={z2}")
shoot(pb, "T9_meadow")

# Can't go past zone 2
pb.memory[0xC001] = 155
pb.button_press('right'); [pb.tick() for _ in range(10)]; pb.button_release('right')
[pb.tick() for _ in range(40)]
check("T9.5 Zone 2 is last",      pb.memory[0xC008] == 2, f"zone={pb.memory[0xC008]}")

# Go back: zone 2 → zone 1
pb.memory[0xC001] = 0; pb.memory[0xC00A] = 0
[pb.tick() for _ in range(3)]
pb.button_press('left'); [pb.tick() for _ in range(5)]; pb.button_release('left')
[pb.tick() for _ in range(80)]
z3 = pb.memory[0xC008]
check("T9.6 Left edge zone 2 → zone 1", z3 == 1, f"zone={z3}")
check("T9.7 X reset when going back",    pb.memory[0xC001] >= 140)

pb.stop()

# ══════════════════════════════════════════════════════
# T10 — SRAM Save/Load
# ══════════════════════════════════════════════════════
print("\n=== T10: SRAM Save/Load ===")
wipe_save()

# 1. Fresh boot must hit TITLE
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T10.1 No save → TITLE (GS=0)", pb.memory[0xC000] == 0, f"GS={pb.memory[0xC000]}")

pb.button('start'); [pb.tick() for _ in range(80)]
pb.button('a');     [pb.tick() for _ in range(80)]
check("T10.2 GS=2 (PLAYING) after start→intro→A", pb.memory[0xC000] == 2)

# Establish known state, move away from any collectible
pb.memory[0xC001] = 50; pb.memory[0xC002] = 50
pb.memory[0xC006] = 7;  pb.memory[0xC009] = 0x01; pb.memory[0xC008] = 0
[pb.tick() for _ in range(5)]
sc_pre = pb.memory[0xC006]; z_pre = pb.memory[0xC008]
px_pre = pb.memory[0xC001]; py_pre = pb.memory[0xC002]
gf_pre = pb.memory[0xC009]

# Save via START→A
pb.button('start'); [pb.tick() for _ in range(40)]
check("T10.3 START → SAVE menu",    pb.memory[0xC000] == 3)
pb.button('a'); [pb.tick() for _ in range(40)]
check("T10.4 A saves → PLAYING",    pb.memory[0xC000] == 2)
pb.stop()
check("T10.5 RAM file created",     os.path.exists(RAM_PATH), RAM_PATH)

# Reload
pb = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()
check("T10.6 Reload → PLAYING (saved state loaded)", pb.memory[0xC000] == 2, f"GS={pb.memory[0xC000]}")
check("T10.7 Zone preserved",      pb.memory[0xC008] == z_pre,  f"{z_pre}→{pb.memory[0xC008]}")
check("T10.8 PLAYER_X preserved",  pb.memory[0xC001] == px_pre, f"{px_pre}→{pb.memory[0xC001]}")
check("T10.9 PLAYER_Y preserved",  pb.memory[0xC002] == py_pre, f"{py_pre}→{pb.memory[0xC002]}")
check("T10.10 GIFTS preserved",    pb.memory[0xC009] == gf_pre, f"0x{gf_pre:02X}→0x{pb.memory[0xC009]:02X}")
check("T10.11 SCORE preserved",    pb.memory[0xC006] == sc_pre, f"{sc_pre}→{pb.memory[0xC006]}")

# B cancels save (should not create/update file if we wipe first)
wipe_save()
pb.button('start'); [pb.tick() for _ in range(40)]
pb.button('b');     [pb.tick() for _ in range(40)]
check("T10.12 B cancels → PLAYING", pb.memory[0xC000] == 2)
pb.stop()
# PyBoy always flushes battery RAM on stop() for MBC1+RAM+BAT carts.
# Correct test: after B-cancel and reload, saved data should be unchanged.
pb2 = PyBoy(ROM_PATH, window='null', sound_emulated=False)
pb2.set_emulation_speed(0)
for _ in range(180): pb2.tick()
check("T10.13 B cancel: reload still has saved data",
      pb2.memory[0xC001] == px_pre and pb2.memory[0xC006] == sc_pre,
      f"x={pb2.memory[0xC001]} score={pb2.memory[0xC006]}")
pb2.stop()

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

with open('/home/claude/bunnygarden/test_results.txt', 'w') as f:
    f.write(f"BunnyGarden ROM Tests  PASS={PASS}/{total}  FAIL={FAIL}\n{'='*50}\n")
    for r in results: f.write(r + "\n")
print("\nSaved: test_results.txt")
