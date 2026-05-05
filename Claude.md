# Bunny Garden Adventure — Developer Guide

## Architecture Overview

Each file has ONE job. Edit only what you need.

```
gbc_lib.py     — ROM class (assembler opcodes) + color math + header writing
tiles.py       — All tile pixel data (8x8 arrays) + build_tile_data()
tilemaps.py    — Screen generators + collectible spawn tables + ZONE_COLLECTS
music.py       — Music note data (Twinkle Twinkle, C4 octave)
asm_game.py    — Game logic: ISRs, main loop, all subroutines, WRAM/IO constants
build_rom.py   — Master: imports all modules, lays out ROM sections, patches pointers
```

### Data layout in ROM (32KB)
```
0x0000-0x003F  RST vectors (RETI)
0x0040-0x0047  VBlank ISR
0x0048-0x006F  Other ISRs (RETI)
0x0100-0x0103  Entry point (NOP; JP main)
0x0150-0x0800  Game code (from asm_game.py)
0x0800-0x17FF  Tile data (256 tiles × 16 bytes = 4096 bytes)
0x1800-0x183F  BG palettes  (8 palettes × 4 colors × 2 bytes)
0x1840-0x187F  OBJ palettes (8 palettes × 4 colors × 2 bytes)
0x1880-...     Music data
...            Screen tilemaps (tiles + attrs, 576 bytes each × 8 screens)
...            Zone collectible tables
```

### WRAM map (C000-C2FF)
```
C000  GAMESTATE      0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY
C001  PLAYER_X       pixel x (0-159)
C002  PLAYER_Y       pixel y (16-143, row 0 is UI bar)
C003  PLAYER_DIR     0=right 1=left
C004  PLAYER_FRAME   0 or 1
C005  ANIM_CTR       counts up to 10 then flips frame
C006  SCORE          0-99
C007  SCORE_DIRTY    1=needs redraw
C008  CUR_ZONE       0=garden 1=forest 2=meadow
C009  GIFTS          bit 0=zone0 bit 1=zone1 bit 2=zone2
C00A  NEED_REDRAW    1=call do_screen_redraw next frame
C00B  TRANSITION_TO  state to transition to
C00C  JOY_CUR        bitmask: bit0=A 1=B 2=SELECT 3=START 4=RIGHT 5=LEFT 6=UP 7=DOWN
C00D  JOY_PREV       previous frame joypad
C00E  JOY_NEW        newly pressed this frame
C00F  MUSIC_CTR      countdown timer per note
C010  MUSIC_PTR_LO   ROM pointer to current music byte (low)
C011  MUSIC_PTR_HI   ROM pointer to current music byte (high)
C012  VBLANK_FLAG    set by ISR, cleared by main loop
C013  TMP1           scratch
C014  TMP2           scratch
C020  COLL_DATA      collectible structs: 4 bytes each (x, y, type, active)
C050  COLL_COUNT     number of collectibles loaded for current zone
C300  OAM_BUF        shadow OAM (160 bytes), DMA'd each frame
```

### SRAM save format (0xA000)
```
A000  Magic 'B' (0x42)
A001  Magic 'U' (0x55)
A002  Magic 'N' (0x4E)
A003  Magic 'Y' (0x59)
A004  CUR_ZONE
A005  PLAYER_X
A006  PLAYER_Y
A007  GIFTS
A008  SCORE
```

---

## How to Change Things

### Add a new tile
1. Edit `tiles.py`: add a new pixel array function and a new `TL_*` constant (use unused 0x00-0xFF slot)
2. Add a `put(TL_NEW, new_fn())` call in `build_tile_data()`
3. Reference `TL_NEW` from `tilemaps.py` or `asm_game.py`

### Edit a screen layout
1. Edit the function in `tilemaps.py` (e.g. `garden_screen()`)
2. No changes needed elsewhere — it auto-rebuilds
3. Collectible positions are in `ZONE_COLLECTS` at bottom of `tilemaps.py`

### Edit music
1. Edit `music.py` — change `SONG` list of (freq, duration) tuples
2. QN=18 frames per quarter note, HN=36 half note
3. Frequencies: use `freq(hz)` helper. `freq(261.63)` = C4

### Change game logic
1. Edit `asm_game.py` — functions return label dictionaries for patch points
2. Each subroutine is a labeled block. The `build_game_asm(rom)` function emits all code.
3. Patch points are returned as a dict so `build_rom.py` can write data addresses.

### Add a new game state
1. Add `GS_NEW = 6` constant in `asm_game.py`
2. Add dispatch entry in main loop: `rom.CP_n(GS_NEW); rom.JP_Z('st_new')`
3. Add handler label + RET somewhere before data section
4. Add redraw handler in `do_screen_redraw`
5. Add screen generator in `tilemaps.py` + emit it in `build_rom.py`

---

## Known Good Behavior (v2)
- Title → START → Intro → A → Garden gameplay
- D-pad moves bunny (held), animation works
- Collectibles detected by proximity (10px)
- Gift collected → GIFTS bit set, heart fills in score bar
- All 3 gifts → VICTORY screen
- START in game → SAVE menu → A saves to SRAM, B cancels
- SELECT in game → MAP screen → B exits
- SRAM save persists across sessions (battery save, MBC1+RAM+BATTERY cart type 0x03)
- Zone transition: walk off right edge → next zone, left edge → previous zone
- Saved game auto-loads on boot (skips title if valid save found)

## Bugs Fixed vs v1
- Joypad dual-read with settle delay (was wrong button bits before)
- LCDC = 0x93 (was 0x91, bit 1=OBJ enable was missing)
- Gift collectible positions don't overlap player spawn

## Remaining Known Issues
- Map screen hearts: address calculation was off (fixed in memory.md)
- Bunny render: OBJ 8x8 mode, head+body = 2 separate OAM entries; looks small
- Score display writes during LCD-on (works in practice, but should be VBlank-gated)
