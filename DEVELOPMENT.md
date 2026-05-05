# Bunny Garden Adventure — Comprehensive Developer Guide

This guide covers architecture, memory layout, and step-by-step how-to instructions for common development tasks.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Module Responsibilities](#module-responsibilities)
3. [ROM Data Layout](#rom-data-layout)
4. [Memory Maps](#memory-maps)
5. [How to Change Things](#how-to-change-things)
6. [Known Issues](#known-issues)
7. [Roadmap](#roadmap)

---

## Architecture Overview

### Core Principle
**Each file has ONE job. Edit only what you need.**

```
gbc_lib.py     — ROM class (assembler opcodes) + color math + header writing
tiles.py       — All tile pixel data (8x8 arrays) + build_tile_data()
tilemaps.py    — Screen generators + collectible spawn tables + ZONE_COLLECTS
music.py       — Music note data (Twinkle Twinkle, C4 octave)
asm_game.py    — Game logic: ISRs, main loop, all subroutines, WRAM/IO constants
build_rom.py   — Master: imports all modules, lays out ROM sections, patches pointers
```

### Module Interaction
```
build_rom.py (orchestrator)
    ├── imports gbc_lib.ROM
    ├── calls build_game_asm(rom) from asm_game.py
    │   └── emits SM83 assembly code
    ├── calls build_tile_data() from tiles.py
    │   └── returns 4096 bytes of 2bpp tile data
    ├── calls screen functions from tilemaps.py
    │   └── returns tilemap + attribute bytes
    ├── calls music_data() from music.py
    │   └── returns note sequence bytes
    └── patches all addresses and writes final .gbc file
```

### Design Principles
- **Minimal coupling:** Modules don't import each other (except constants)
- **Data-driven:** Game content (tiles, layouts, music) separate from logic
- **Declarative:** Screen layouts are functions, not hardcoded data
- **Testable:** Each module can be validated independently

---

## Module Responsibilities

### gbc_lib.py — ROM Assembler
Low-level Game Boy hardware interface. No game-specific code.

**Exports:**
- `ROM` class: manages byte buffer, labels, fixups, header
- `rgb15()` function: converts R,G,B (0-31) to Game Boy 15-bit color

**Key methods:**
- `emit(*bytes)` — Write bytes at current position
- `label(name)` — Mark current position with label name
- `addr(name)` — Retrieve label address (for jumps/calls)
- `set_header()` — Write GBC header (entry, checksum, cart type)

**Opcodes implemented:**
- Register load/store (`LD_A_n`, `LD_HL_A`, etc.)
- 16-bit operations (`LD_HL_nn`, `DEC_BC`, etc.)
- Control flow (`JP`, `JR`, `CALL`, `RET`)
- Logic (`XOR_A`, `OR_C`, etc.)
- I/O (`LDH_A_n`, `LDH_n_A` for HRAM operations)

**Never edit:** This file is generic. Only touch if adding new SM83 opcodes.

---

### tiles.py — Tile Pixel Art
All 8×8 tile graphics and encoding.

**Data format:** Each tile is 16 bytes (2bpp = 2 bits per pixel, 4 colors)

**Structure:**
```python
def enc(pix):
    """Convert 8x8 pixel array (0-3 values) to 16-byte 2bpp format."""
    # Packs 2 pixels per byte; color split across bitplanes

TL_BUNNY_T_F1 = 0x00    # Tile index constant
TL_GRASS_PLAIN = 0x10
# ... 250+ more constants

def build_tile_data():
    """Emit all tiles in order; return 4096-byte block."""
    data = bytearray()
    # ... call enc() for each tile, return concatenated
```

**Tile indices:**
- 0x00–0x07: OBJ tiles (bunny, gifts, collectibles)
- 0x10–0x2D: BG tiles (grass, dirt, trees, UI)
- 0x40–0x59: Font tiles (A-Z)
- 0x20–0x29: Digit tiles (0-9)

**To add a new tile:**
1. Create pixel function: `def my_tile(): return enc([[...], [...], ...])`
2. Add constant: `TL_MY_TILE = 0x??` (find unused index)
3. Call in `build_tile_data()`: `put(TL_MY_TILE, my_tile())`
4. Reference in `tilemaps.py` or `asm_game.py`

---

### tilemaps.py — Screen Layouts & Collectibles
Screen generators and collectible spawn tables.

**Dimensions:** 32 tiles wide, 18 tiles tall (standard GBC screen)

**Exports:**
- Screen functions: `garden_screen()`, `forest_screen()`, `meadow_screen()`, etc.
  - Each returns: `(tilemap_bytes, attr_bytes)` tuple
- `ALL_SCREENS` list: registered screen functions
- `ZONE_COLLECTS` dict: collectible spawn positions per zone

**Helper functions:**
- `_put(tiles, attrs, x, y, tile_id, palette)` — Write one tile
- `_fill_grass(tiles, attrs, y0, y1)` — Seed-based grass pattern (deterministic)
- `_score_bar(tiles, attrs)` — Top row with hearts and score
- `_horizontal_path()` — Dirt path decoration

**Collectible format:**
```python
ZONE_COLLECTS = {
    0: [  # Garden zone
        (24, 32, 0),    # x, y, type (0=star, 1=flower, 2=gift)
        (80, 32, 1),
        (120, 64, 2),   # Gift!
    ],
    # ... Forest and Meadow zones
}
```

**To edit a screen:**
1. Find screen function in `tilemaps.py` (e.g., `garden_screen()`)
2. Modify `_put()` calls to change tile placement
3. Save and rebuild: `python3 build_rom.py`
4. No other changes needed (addresses auto-computed)

**To move collectibles:**
1. Edit `ZONE_COLLECTS` at bottom of file
2. Keep (x, y) within bounds: 0–159 (x), 16–143 (y)
3. Type: 0=star, 1=flower, 2=gift (one gift per zone)

---

### music.py — Audio Data
Music note sequences.

**Exports:**
```python
def freq(hz):
    """Convert Hz to Game Boy frequency register (0-2047)."""
    # Formula: freq = (4194304 / (32 * hz)) - 1

SONG = [
    (C4, QN),      # frequency, duration (in frames)
    (C4, QN),
    ...
]

def music_data():
    """Encode song notes to ROM format bytes."""
    # Returns list of [lo, hi|0x80, dur, ...] + 0xFF terminator
```

**Note definitions:**
- `C4, D4, E4, F4, G4, A4, B4` — Common notes (octave 4)
- `QN = 18` frames per quarter note (at ~60 FPS)
- `HN = 36` frames per half note
- Rest: use `0` for frequency

**To change music:**
1. Edit `SONG` list in `music.py` (add/remove notes)
2. Save and rebuild
3. Test in emulator (SELECT to see music notes playing)

**To add new song:**
1. Create new list: `MY_SONG = [(C4, QN), ...]`
2. Create wrapper function returning encoded bytes
3. (Phase 2+) Register in music system for dynamic selection

---

### asm_game.py — Game Logic
SM83 assembly code for game mechanics.

**Complexity:** ~30KB of documented assembly (largest file).

**Sections:**
- **Constants:** WRAM addresses, IO offsets, game state IDs
- **Main loop:** VBlank wait, input reading, state dispatch, screen redraw
- **State handlers:** Title, Intro, Playing, Save, Map, Victory
- **Game logic:** Player movement, collision, collectible detection, scoring
- **Utilities:** Screen clearing, palette loading, OAM setup, DMA timing

**WRAM Layout (0xC000–0xC2FF):**
```
C000  GAMESTATE    (0=TITLE, 1=INTRO, 2=PLAYING, 3=SAVE, 4=MAP, 5=VICTORY)
C001  PLAYER_X     (pixel x, 0–159)
C002  PLAYER_Y     (pixel y, 16–143)
C003  PLAYER_DIR   (0=right, 1=left)
C004  PLAYER_FRAME (animation frame: 0 or 1)
C005  ANIM_CTR     (counts 0–10, flips frame at 10)
C006  SCORE        (0–99)
C007  SCORE_DIRTY  (1=redraw needed)
C008  CUR_ZONE     (0=garden, 1=forest, 2=meadow)
C009  GIFTS        (bitmask: bit0=zone0, bit1=zone1, bit2=zone2)
C00A  NEED_REDRAW  (1=full screen redraw next frame)
C00B  TRANSITION_TO (next state when redraw fires)
C00C  JOY_CUR      (joypad bitmask, active HIGH)
C00D  JOY_PREV     (previous frame joypad)
C00E  JOY_NEW      (newly pressed: JOY_CUR & ~JOY_PREV)
C00F  MUSIC_CTR    (frames until next note)
C010–C011 MUSIC_PTR (ROM pointer to current music byte)
C012  VBLANK_FLAG  (set by ISR, cleared by main loop)
C013–C014 TMP1, TMP2 (scratch registers)
C020–C04F COLL_DATA (collectible data: up to 9 entries, 4 bytes each)
C050  COLL_COUNT   (number of active collectibles)
C300  OAM_BUF      (shadow OAM, 160 bytes, DMA'd each VBlank)
```

**Game state machine:**
```
      START
        ↓
    TITLE (GS_0)
        ↓ START pressed
      INTRO (GS_1)
        ↓ A pressed
    PLAYING (GS_2)
     ↙ START  SELECT ↘
   SAVE (GS_3)  MAP (GS_4)
     ↘ A/B    B ↙
       ↓ A (save)
      PLAYING
       (restore or continue)
        ↓ GIFTS=0x07
     VICTORY (GS_5)
```

**Key routines:**
- `main` — Initialization, entry point
- `vblank_isr` — Sets flag; called 60x per second
- `handle_joypad` — Reads button input with settle delay
- `update_player` — Movement, collision, animation
- `detect_collectible` — Proximity check (~10 pixels)
- `do_screen_redraw` — Full VRAM rewrite (slow, run once per state change)

**To change game logic:**
1. Locate routine in `asm_game.py`
2. Edit SM83 assembly code (see gbc_lib.py for opcode methods)
3. Save and rebuild
4. Test in emulator

**SM83 Basics:**
- Registers: A (accumulator), B/C, D/E, H/L (16-bit pairs), SP (stack), PC (program counter)
- Memory: `LD A, (HL)` loads from RAM at HL
- Arithmetic: `ADD A, B`, `SUB A, 5`, `INC HL`
- Jumps: `JP label`, `JR label` (relative, ±127 bytes)
- Calls: `CALL label`, `RET` (return)

See comments in `asm_game.py` for detailed routine documentation.

---

### build_rom.py — Master Orchestrator
Compiles all modules into a 32KB Game Boy Color ROM.

**Process:**
1. Create ROM object (32KB buffer)
2. Emit game code via `build_game_asm(rom)`
3. Append tile data, palettes, music, screens, collectible tables
4. Patch all computed addresses into code
5. Write header (GBC flag, checksum, cart type)
6. Save .gbc file

**Palette definitions:**
```python
BG_PALETTES[0]  — Grass zone colors (sky, light-green, mid-green, dark-green)
BG_PALETTES[1]  — Dirt path colors
BG_PALETTES[2]  — UI text colors
...
OBJ_PALETTES[0] — Bunny colors
OBJ_PALETTES[1] — Star colors
...
```

**Patch points returned by `build_game_asm()`:**
```python
patches = {
    'tile_src': address_in_code_to_tile_data_pointer,
    'bg_pal': address_of_bg_palette_pointer,
    'obj_pal': address_of_obj_palette_pointer,
    'mus_lo': address_of_music_lo_byte,
    'mus_hi': address_of_music_hi_byte,
    # ... screen addresses for each zone
}
```

**ROM sections:**
```
0x0000–0x00FF   ISRs and RST vectors
0x0100–0x0150   Entry point + header
0x0150–0x0800   Game code (~6.5 KB)
0x0800–0x1800   Tile data (4 KB)
0x1800–0x187F   Palettes (128 bytes)
0x1880+         Music + screens + collectible tables
```

**To build ROM:**
```bash
python3 build_rom.py [output_path]
# Default: BunnyGarden.gbc
```

---

## ROM Data Layout

**Total: 32KB (32768 bytes)**

### Fixed Sections (by hardware)
```
0x0000–0x003F   RST vectors (all RETI)
0x0040–0x0047   VBlank ISR
0x0048–0x006F   Timer, Serial, Joypad ISRs (RETI)
0x0100–0x0103   Entry point (NOP; JP main)
```

### Game Sections (by build_rom.py)
```
0x0150–0x0800   Game code (asm_game.py)
0x0800–0x1800   Tile data (build_tile_data(), 256 × 16 bytes)
0x1800–0x187F   BG palettes (8 × 4 colors × 2 bytes = 64 bytes)
0x1880–0x18FF   OBJ palettes (8 × 4 colors × 2 bytes = 64 bytes)
0x1900+         Music data (~1 KB)
0x1A00+         Screen tilemaps + attributes (3 zones × 2 × 288 bytes)
0x????          Collectible spawn tables (3 zones × ~20 bytes)
```

### SRAM (Cartridge Battery, 0xA000–0xBFFF)
```
A000–A003   Magic: 'B', 'U', 'N', 'Y'
A004        CUR_ZONE (0–2)
A005        PLAYER_X (0–159)
A006        PLAYER_Y (16–143)
A007        GIFTS (bitmask)
A008        SCORE (0–99)
A009+       Reserved for future use
```

### VRAM (Video RAM, 0x8000–0x9FFF, 8KB)
Dynamically allocated by hardware during gameplay:
- 0x8000–0x87FF   Tile data (copied from ROM at startup)
- 0x8800–0x97FF   BG tilemaps (32×32 tiles each, mirrored at 0x9800)
- 0x9800–0x9FFF   BG attributes (color palette per tile)

---

## Memory Maps

### WRAM Detailed
See [asm_game.py constants section](asm_game.py#L10) for exact addresses.

### IO Registers (0xFF00–0xFF7F, accessed via `LDH A, (C)`)
```
FF00 (P1)       Joypad input selector
FF04–FF07       Timer
FF10–FF14       Sound channel 1 (square wave)
FF15–FF19       Sound channel 2 (square wave)
FF1A–FF1E       Sound channel 3 (wave)
FF1F–FF23       Sound channel 4 (noise)
FF24–FF26       Sound control
FF40 (LCDC)     LCD control (0x93 = LCD on, obj on, 8×8 sprites)
FF41–FF45       LCD status / Y position
FF46 (DMA)      DMA transfer trigger (for OAM shadow)
FF47–FF49       BG/OBJ/WIN palette
FF4F (VBK)      VRAM bank (0 or 1 for GBC)
FF68–FF69 (BCPS/BCPD) BG color palette pointer/data
FF6A–FF6B (OCPS/OCPD) OBJ color palette pointer/data
```

---

## How to Change Things

### Add a New Tile

**Step 1: Create pixel art**
- Open text editor or pixel art tool
- Design 8×8 pixel image
- Use 4 colors (0=transparent, 1=light, 2=mid, 3=dark)

**Step 2: Write encoding function in tiles.py**
```python
def my_grass_variant():
    return enc([
        [0,0,1,1,0,0,0,0],
        [0,1,2,2,1,0,0,0],
        [1,2,3,3,2,1,0,0],
        [1,2,3,3,2,1,0,0],
        [0,1,2,2,1,0,0,0],
        [0,1,2,2,1,0,0,0],
        [0,0,1,1,0,0,0,0],
        [0,0,1,1,0,0,0,0],
    ])
```

**Step 3: Add tile index constant**
```python
TL_GRASS_VAR2 = 0x11  # Pick unused index 0x00–0xFF
```

**Step 4: Register in build_tile_data()**
```python
def build_tile_data():
    data = bytearray()
    for b in enc(...): data.append(b)  # existing tiles
    put(TL_GRASS_VAR2, my_grass_variant())
    # ...
    return data
```

**Step 5: Use in tilemaps**
```python
def garden_screen():
    tiles, attrs = _blank()
    _put(tiles, attrs, 5, 10, TL_GRASS_VAR2, 0)  # Use new tile
    return tiles, attrs
```

**Step 6: Rebuild and test**
```bash
python3 build_rom.py
# Test in emulator
```

---

### Edit a Screen Layout

**Example: Change garden screen background**

1. Open `tilemaps.py`, find `garden_screen()`
```python
def garden_screen():
    tiles, attrs = _blank()  # 32×18 blank screen
    _fill_grass(tiles, attrs, 1, 15)  # Fill rows 1–15 with grass
    # ... add paths, trees, etc.
```

2. Modify helper calls:
```python
_fill_grass(tiles, attrs, 1, 12)  # Change row range
_horizontal_path(tiles, attrs, 8)  # Move path to row 8
```

3. Save and rebuild:
```bash
python3 build_rom.py
```

4. Test in emulator; screen auto-redraws on zone load

---

### Edit Music

**Change the Twinkle Twinkle melody:**

1. Open `music.py`
2. Edit `SONG` list:
```python
SONG = [
    (C4, QN),     # C4, quarter note
    (C4, QN),
    (G4, QN),
    (G4, QN),
    (A4, QN),
    (A4, QN),
    (G4, HN),     # G4, half note (longer)
    # ... add/remove notes
]
```

3. Save and rebuild:
```bash
python3 build_rom.py
```

**Note frequencies:**
```
C4=261.63Hz, D4=293.66Hz, E4=329.63Hz, F4=349.23Hz
G4=392Hz, A4=440Hz, B4=493.88Hz
(Octaves 2, 3, 4, 5 available)
```

**Durations:**
- `QN = 18` — Quarter note (~300ms at 60 FPS)
- `HN = 36` — Half note (~600ms)
- Customize: any value in frames (60 FPS)

---

### Change Game Logic

**Example: Make player faster**

1. Open `asm_game.py`, find `update_player()` routine
2. Locate movement increment (usually `ADD A, 1` or similar)
3. Change to `ADD A, 2` for double speed
4. Rebuild and test:
```bash
python3 build_rom.py
```

**Example: Adjust collectible proximity**

1. Find `detect_collectible()` in `asm_game.py`
2. Change proximity threshold (currently ~10 pixels)
3. Adjust distance calculation

---

### Add a New Game State

**Goal: Add a SHOP screen (GS_6)**

**Step 1: Add constant in asm_game.py**
```python
GS_SHOP = 6
```

**Step 2: Add to state dispatch in main loop**
```python
rom.CP_n(GS_SHOP); rom.JP_Z('st_shop')
```

**Step 3: Implement handler before data section**
```python
rom.label('st_shop')
# ... shop logic (read input, update state) ...
rom.RET()
```

**Step 4: Add screen generator in tilemaps.py**
```python
def shop_screen():
    tiles, attrs = _blank()
    _str(tiles, attrs, 5, 5, "SHOP", 2)
    # ... add shop items
    return tiles, attrs
```

**Step 5: Register screen in build_rom.py**
```python
ALL_SCREENS.append(('shop', shop_screen))
```

**Step 6: Patch address in build_rom.py**
```python
p16(patches['shop_t'], screen_addrs['shop'][0])
p16(patches['shop_a'], screen_addrs['shop'][1])
```

**Step 7: Add screen name to patches dict in build_game_asm()**
```python
patches['shop_t'] = rom.pos  # tilemap pointer
# ... later, after loading shop tilemap address
```

---

## Known Issues

### Issue 1: Map Screen Hearts Address Calculation
**Location:** `asm_game.py::update_map_hearts()`

**Problem:** Heart tile positions off by one row each.

**Impact:** MAP screen shows heart icons in wrong places (cosmetic, no gameplay effect).

**Current code:** Writes to 0x988C, 0x98CC, 0x990C

**Correct addresses:**
```
Row 6, Col 12:  0x9800 + 6×32 + 12 = 0x98CC
Row 8, Col 12:  0x9800 + 8×32 + 12 = 0x990C
Row 10, Col 12: 0x9800 + 10×32 + 12 = 0x994C
```

**Fix:** (Planned for Phase 2 bug fix release)

---

### Issue 2: Score Display Writes During LCD-On
**Location:** `asm_game.py::update_score()`

**Problem:** Writes to VRAM (0x9800–0x9C00) without checking LCD state.

**Impact:** Works in practice; violates Game Boy hardware rules. Potential glitches on some emulators or hardware.

**Fix:** Add VBlank gate check before VRAM writes. (Planned for Phase 2)

---

### Issue 3: Bunny Sprite Appears Small
**Location:** `tiles.py`, `asm_game.py::render_bunny()`

**Problem:** Uses two 8×8 OAM tiles for head + body; could use 8×16 mode instead.

**Impact:** Bunny is visually smaller than intended.

**Options:**
- Redesign pixel art within 8×8 (minimal change)
- Switch to 8×16 OBJ mode (affects all sprites, moderate effort)

**Decision:** TBD based on visual design goals. (Planned for Phase 2)

---

## Roadmap

### Phase 1: Git Foundation (Current ✓)
- [x] .gitignore, README.md, DEVELOPMENT.md
- [x] Pre-commit hooks (black, pylint, isort)
- [x] Conventional commit standards
- [x] Contributing guide

### Phase 2: Test Infrastructure (Next)
- [ ] Pytest setup with unit + integration tests
- [ ] Refactor test_rom.py into pytest framework
- [ ] Code coverage reporting (target 60%)
- [ ] Automated ROM validation

### Phase 3: CI/CD Pipeline (After Phase 2)
- [ ] GitHub Actions workflows
- [ ] Lint checks (pre-merge gates)
- [ ] Test automation
- [ ] Coverage badges

### Phase 4: Bug Fixes (Concurrent with Phase 3)
- [ ] Fix map hearts addresses
- [ ] VBlank-gate score writes
- [ ] ROM overflow validation
- [ ] Patch point verification

### Phase 5: Feature Architecture (Concurrent with Phase 4+)
- [ ] Music system (multi-track, compositions)
- [ ] Tile registry (dynamic slot allocation)
- [ ] Dialog system (branching narratives)
- [ ] Story framework (lore, characters)

**Estimated timeline:** 12–16 weeks at part-time pace; 6–8 weeks full-time.

---

## Quick Reference

### Build Commands
```bash
python3 build_rom.py                 # Build ROM to BunnyGarden.gbc
python3 test_rom.py                  # Run emulation tests
```

### Edit Common Files
```bash
vim tiles.py     # Add/change tile graphics
vim tilemaps.py  # Edit screen layouts
vim music.py     # Change music
vim asm_game.py  # Modify game logic
```

### File Structure Checklist
- [ ] Each module has ONE responsibility
- [ ] Modules don't import each other (except constants)
- [ ] All data functions return deterministic results
- [ ] No side effects in tile/tilemap generators
- [ ] All patch points documented in build_rom.py

---

## Further Reading

- [memory.md](memory.md) — Detailed memory maps (WRAM, VRAM, ROM)
- [Claude.md](Claude.md) — Original design notes
- [test_rom.py](test_rom.py) — Emulation test examples
- Game Boy documentation: [Pan Docs](https://gbdev.io/pandocs/)

---

**Questions or stuck?** See the module docstrings or trace through build_rom.py execution flow.
