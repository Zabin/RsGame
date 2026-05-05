# memory.md — Runtime Notes & Debug Log

## Current Build Status: v3.0 (Phase 5 complete — Graphics iteration framework)

### Last verified working (PyBoy 2.7.0 headless test):
- Title screen renders (purple BG, yellow text, pink/yellow/purple flowers)
- Intro dialog renders
- Garden zone: enhanced vibrant grass with detailed flower tiles, dirt path with texture
- Forest zone: trees, mushrooms, path
- Meadow zone: varied landscape with natural flora
- Bunny sprite visible on path (2 OAM entries, 8x8 tiles) with animation frames
- Collectibles (star, flower, gift) visible as OBJ sprites
- D-pad movement works (1px per frame held)
- Gift collection works (proximity check, gifts bitfield, score++)
- Zone transition (right edge → next zone, left edge → prev)
- START → SAVE menu works (A=save, B=cancel)
- SELECT → MAP screen works (B=exit)
- Victory screen fires when GIFTS = 0x07
- SRAM battery save works (MBC1+RAM+BATTERY, magic BUNY)
- Save auto-loads on reboot (skips title, restores position/gifts/score)
- ROM builds successfully: 32KB with all features
- **180+ tests passing** in full test suite

---

## Phase 5: Graphics Iteration System

### New Tools (Graphics Preview Framework)

**tile_preview.py** — Render individual tiles and tile grids to PNG
```bash
python tile_preview.py --all              # All tiles and palettes
python tile_preview.py --tile 0x10        # Single tile
python tile_preview.py --type bg          # All BG tiles
python tile_preview.py --palettes         # Palette swatches
```

**screen_preview.py** — Render complete game screens with tilemaps
```bash
python screen_preview.py --all            # All screens
python screen_preview.py --screen garden  # Single screen
python screen_preview.py --all --grid     # With tile grid overlay
```

**graphics_utils.py** — Shared utilities
- `rgb15_to_rgb8()` — GBC color format conversion
- `apply_palette()` — Map pixel indices to RGB
- `get_tile_pixels()` — Load raw 8x8 pixel arrays
- `get_palette()` — Load palette colors by ID

**tile_pixels.py** — Raw tile pixel database
- 54 tiles with 8x8 pixel arrays (values 0-3)
- Direct lookup for fast preview generation
- Parallel to tiles.py encoding system

### Workflow: Iterative Graphics Design

1. Edit tile pixels in `tile_pixels.py` or tile functions in `tiles.py`
2. Generate previews instantly: `python tile_preview.py --all` (~1 sec)
3. View previews in `previews/` folder
4. Iterate and compare before/after
5. Build final ROM when satisfied: `python build_rom.py`

### Garden Biome Enhancement (Recent)

Updated 5 key garden tiles with vibrant, detailed designs:
- **GRASS_PLAIN (0x10)** — Varied texture pattern with colors 0-2
- **GRASS_TUFT (0x11)** — Colorful flower with pink/purple accents (colors 2-3)
- **GRASS_CLOVER (0x12)** — Vibrant flower bed using full palette range
- **BG_FLOWER (0x1B)** — Detailed accent flower with bright color 3
- **PATH_TILE (0x13)** — Textured path with subtle darker spots

Result: Garden zone now visually matches concept art with natural, detailed appearance.

### Performance

| Operation | Time |
|-----------|------|
| Single tile render | < 5ms |
| Tile grid (all BG) | < 50ms |
| Screen render | < 30ms |
| All previews (full) | < 1 second |

**Total iteration: Change code → Preview → View = ~2 seconds** (vs 30-90 sec full build cycle)

---

## Active Bug: Map Screen Hearts at Wrong Addresses

### Problem
In `asm_game.py` `update_map_hearts`, addresses are wrong.

Correct BG map addresses for row N, col C:
```
0x9800 + row * 32 + col
```

Map screen hearts are at col 12, rows 6, 8, 10:
```python
row 6,  col 12 → 0x9800 + 6*32 + 12  = 0x98CC
row 8,  col 12 → 0x9800 + 8*32 + 12  = 0x990C
row 10, col 12 → 0x9800 + 10*32 + 12 = 0x994C
```

Old (wrong) values: 0x988C, 0x98CC, 0x990C (off by one row each).

### Fix: In `asm_game.py`, `emit_update_map_hearts()`:
```python
rom.LD_HL_nn(0x98CC); rom.LD_HL_A()  # row 6
rom.LD_HL_nn(0x990C); rom.LD_HL_A()  # row 8
rom.LD_HL_nn(0x994C); rom.LD_HL_A()  # row 10
```

---

## Tile Index Map (quick ref)

| Index | Tile |
|-------|------|
| 0x00  | Bunny head frame 1 |
| 0x01  | Bunny body frame 1 |
| 0x02  | Bunny head frame 2 |
| 0x03  | Bunny body frame 2 |
| 0x04  | Gift (OBJ) |
| 0x05  | Star (OBJ) |
| 0x06  | Flower (OBJ) |
| 0x07  | Cursor |
| 0x10  | Grass plain |
| 0x11  | Grass tuft |
| 0x12  | Grass clover |
| 0x13  | Dirt path center |
| 0x14  | Dirt path top edge |
| 0x15  | Dirt path bot edge |
| 0x16  | Rock big |
| 0x17  | Rock small |
| 0x18  | Tree top |
| 0x19  | Tree bottom (trunk) |
| 0x1A  | Mushroom |
| 0x1B  | BG flower |
| 0x1C  | UI dark (blank bar) |
| 0x1D  | Heart full |
| 0x1E  | Heart empty |
| 0x1F  | Gift icon (score bar) |
| 0x20-0x29 | Digits 0-9 |
| 0x2A  | Border horizontal |
| 0x2B  | Arrow right |
| 0x2D  | Star icon (score bar) |
| 0x40-0x59 | Font A-Z |
| 0x5A  | Space |
| 0x5B-0x61 | Punctuation . ! ? , ' - : |

## BG Palette Quick Ref
| Pal | Use | Colors (0→3) |
|-----|-----|-------------|
| 0   | Grass | sky, lite-green, mid-green, dark-green |
| 1   | Dirt  | sky, lite-brown, mid-brown, dark-brown |
| 2   | UI    | purple-dark, bg-white, yellow-lite, yellow-mid |
| 3   | Trees | sky, lite-tree, mid-tree, dark-tree |
| 4   | Rocks | sky, lite-gray, mid-gray, dark-gray |
| 5   | Pink  | sky, lite-pink, mid-pink, dark-pink |
| 6   | Yellow| sky, lite-yel, mid-yel, dark-yel |
| 7   | Purple| bg-white, lite-pur, mid-pur, dark-pur |

## OBJ Palette Quick Ref
| Pal | Use | Colors (0=trans) |
|-----|-----|------------------|
| 0   | Bunny | trans, white, lite-pink, dark-pink |
| 1   | Star  | trans, lite-yel, mid-yel, dark-yel |
| 2   | Flower| trans, lite-pink, mid-pink, dark-pink |
| 3   | Gift  | trans, lite-yel, mid-pur, dark-pur |

## Joypad Bit Map (JOY_CUR — active HIGH)
```
bit 0 = A        bit 4 = RIGHT
bit 1 = B        bit 5 = LEFT
bit 2 = SELECT   bit 6 = UP
bit 3 = START    bit 7 = DOWN
```

## Collectible Positions
Format: (x, y, type)  type: 0=star, 1=flower, 2=GIFT

**Garden (zone 0):** player spawns at (76, 72)
- (24, 32, star), (80, 32, flower), (136, 32, star)
- (40, 96, flower), (120, 96, star)
- **(120, 64, gift)** ← walk right+up from spawn

**Forest (zone 1):** spawns at (8, 72) from left, (150, 72) from right
- (32, 40, flower), (64, 40, star), (96, 40, flower), (128, 40, star)
- (48, 104, star), (104, 104, flower)
- **(40, 64, gift)**

**Meadow (zone 2):**
- (24, 40, flower), (56, 32, star), (88, 40, flower), (120, 32, star), (152, 40, flower)
- (40, 104, star), (88, 104, flower), (136, 104, star)
- **(136, 64, gift)**

## Emulator Test Command
```python
from pyboy import PyBoy
pb = PyBoy('/mnt/user-data/outputs/BunnyGarden.gbc', window='null', sound_emulated=False)
pb.set_emulation_speed(0)
```
Remove any .sav file before testing fresh boots:
```bash
rm -f /mnt/user-data/outputs/*.sav
```
