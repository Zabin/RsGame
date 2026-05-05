# Graphics Preview System

Fast tile and screen preview generation without building the full ROM. Dramatically speeds up iterative graphics design.

## Quick Start

```bash
# Generate all tile grids and screen previews
python tile_preview.py --all
python screen_preview.py --all

# View results
open previews/
```

## Tools

### tile_preview.py — Tile Rendering

Generate PNG previews of individual tiles and tile grids.

**Usage:**

```bash
# All tiles and palettes
python tile_preview.py --all

# Single tile (hex index)
python tile_preview.py --tile 0x10    # Grass plain tile
python tile_preview.py --tile 0x00    # Bunny top frame 1

# All tiles of type
python tile_preview.py --type bg      # All background tiles
python tile_preview.py --type obj     # All sprite tiles
python tile_preview.py --type font    # All font tiles

# Palette swatches
python tile_preview.py --palettes

# Custom output directory
python tile_preview.py --all --output my_previews/
```

**Output Structure:**

```
previews/
├── tiles_obj_0x00_0x07.png       # OBJ sprites: 8x upscale
├── tiles_bg_0x10_0x2B.png        # BG tiles: 8x upscale
├── tiles_font_0x40_0x61.png      # Font tiles: 6x upscale
├── palettes_bg_all.png           # All 8 BG palettes
├── palettes_obj_all.png          # All 4 OBJ palettes
├── tile_0x10.png                 # Single tile example
└── [more individual tiles...]
```

**Features:**

- **Grid Layout**: 8 tiles per row with hex labels
- **Palette Visualization**: Color swatches with RGB15/RGB8 values
- **Upscaling**: Nearest-neighbor for pixel-perfect preview
- **Performance**: Entire grid in < 100ms

### screen_preview.py — Full Screen Rendering

Generate PNG previews of complete game screens with tilemaps and attributes.

**Usage:**

```bash
# All screens
python screen_preview.py --all

# Single screen
python screen_preview.py --screen garden
python screen_preview.py --screen forest
python screen_preview.py --screen meadow
python screen_preview.py --screen title

# With grid overlay (helps see tile boundaries)
python screen_preview.py --all --grid

# List available screens
python screen_preview.py --all 2>&1 | grep "Found"
```

**Available Screens:**

- `title` — Title screen
- `intro` — Introduction/story screen
- `garden` — Main game world: garden zone
- `forest` — Gameplay zone: forest
- `meadow` — Gameplay zone: meadow
- `map` — Zone map screen
- `save` — Save game menu
- `victory` — Victory/completion screen

**Output:**

```
previews/screens/
├── title.png       # 512×576 pixels (2x upscale)
├── garden.png
├── forest.png
├── meadow.png
├── map.png
├── save.png
├── intro.png
└── victory.png
```

**Features:**

- **Full Tilemap**: 32×18 tiles rendered with proper attributes
- **Palette Application**: Each tile uses correct palette from attribute map
- **Grid Overlay**: Optional tile grid for analysis (use `--grid`)
- **2x Upscale**: 512×576 final size for visibility

## Workflow: Iterative Graphics Design

### 1. Make a Graphics Change

Edit tile pixel data in `tile_pixels.py`:

```python
# Change grass plain tile
GRASS_PLAIN = [
    [0,1,2,1,0,1,2,1],  # Modified pattern
    [2,1,0,1,2,1,0,1],
    # ... rest of 8x8 array
]
```

Or modify a tile function in `tiles.py`:

```python
def rock_big():
    return enc([
        [0,0,2,2,2,2,0,0],  # Updated design
        # ... etc
    ])
```

### 2. Preview Instantly

```bash
# 1 second to generate all previews
python tile_preview.py --all
python screen_preview.py --all

# Open previews folder
open previews/
```

### 3. Iterate & Compare

- View tile grids to check design
- See screen mockups with attributes applied
- Compare before/after side-by-side
- Verify palette cohesion across biomes

### 4. Final Build

Once satisfied:

```bash
python build_rom.py
# Emulate and test final ROM
```

## Design Principles (from Research)

Inspired by acclaimed GBC games with outstanding graphics:

| Game | Known For |
|------|-----------|
| **Pokémon Gold/Silver** | Refined 2D sprites with smooth animations |
| **Zelda Oracle of Ages/Seasons** | Exceptional detailed backgrounds (2001 benchmark) |
| **Shantae** | Outstanding sprite animation, lavishly colored backgrounds |
| **Donkey Kong Country** | Detail and character in colorful sprites |

### Principles Applied:

1. **Vibrant 4-color palettes** — Maximize visual impact within GBC constraint
2. **Detailed tile variations** — Multiple grass/dirt/rock tiles for natural look
3. **Coherent color schemes** — Each biome has consistent palette family
4. **Animation emphasis** — Sprite frames for smooth movement
5. **High contrast** — Ensure readability and visual clarity

## Technical Details

### Tile Index Ranges

| Type | Range | Count | Examples |
|------|-------|-------|----------|
| **OBJ Sprites** | 0x00-0x07 | 8 | Bunny (4 frames), Gift, Star, Flower |
| **BG Tiles** | 0x10-0x2B | 23 | Grass variants, paths, rocks, trees, UI |
| **Font** | 0x40-0x61 | 34 | A-Z, digits, punctuation |

### Color System

**RGB15 Format**: 5 bits per channel (0-31), converted to RGB8 (0-255) for preview

```python
# Game Boy color value (5-bit per channel)
rgb15 = 0x7C1F  # Red=31, Green=0, Blue=31 (bright magenta)

# Convert to standard RGB
r = (rgb15 & 0x1F) << 3         # 0x1F << 3 = 0xF8 (248)
g = ((rgb15 >> 5) & 0x1F) << 3  # 0x00 << 3 = 0x00 (0)
b = ((rgb15 >> 10) & 0x1F) << 3 # 0x1F << 3 = 0xF8 (248)
```

### Palette Application

Each tile in a tilemap has an attribute byte specifying its palette:

```
Tile at (x=5, y=3): index=0x10 (grass)
Attribute at same position: 0x02 (use palette 2 = "dirt")
Result: Grass tile rendered with dirt palette colors
```

## Performance

| Operation | Time |
|-----------|------|
| Single tile render | < 5ms |
| Tile grid (BG/OBJ) | < 50ms |
| Screen render | < 30ms per screen |
| All previews (tiles + screens) | < 1 second |
| ROM build (unaffected) | 30-60 sec |

**Total iteration cycle**: Change code → Preview generated → View result = **~2 seconds**

vs.

**Old workflow**: Change code → Full build → Load in emulator → View = **30-90 seconds**

## Troubleshooting

### "Pillow not installed"

```bash
pip install Pillow
```

### Tile preview shows garbled colors

- Check tile pixel values are 0-3 (not 0-255)
- Verify palette ID matches tile's palette
- Confirm RGB15 values in palette are valid (0-0x7FFF)

### Screen preview is blank or wrong colors

- Verify tilemap indices point to valid tiles (0x00-0xFF)
- Check attribute bytes match tile palette assignments
- Ensure palette is registered for both "BG" and "OBJ" types

### Want to modify tile pixels directly?

1. Edit `tile_pixels.py` for raw pixel arrays
2. Or edit `tiles.py` and rerun `python tile_pixels.py` to regenerate
3. Preview instantly with `python tile_preview.py --tile 0xNN`

## Architecture

```
graphics_utils.py
├── rgb15_to_rgb8()         # Color format conversion
├── apply_palette()         # Map pixel indices to RGB
├── get_tile_pixels()       # Load tile pixel data
└── get_screen_function()   # Load screen tilemap

tile_pixels.py
├── [All 8x8 pixel arrays for 54 tiles]
└── TILE_PIXELS mapping    # Index → pixel data

tile_preview.py
├── render_tile()           # Single tile to Image
├── create_tile_grid()      # Multiple tiles to grid
├── create_palette_preview() # Palette swatches
└── main()                  # CLI interface

screen_preview.py
├── render_screen()         # Full tilemap to Image
├── render_screen_with_grid() # + overlay
└── main()                  # CLI interface
```

## Future Enhancements

Planned but not yet implemented:

1. **Animation Preview** — GIF output for sprite sequences
2. **Palette Designer** — Interactive RGB15 color picker
3. **Tile Editor** — 8×8 pixel grid UI for quick edits
4. **Comparison View** — Side-by-side before/after
5. **Web UI** — Local Flask server for browsing tiles/screens
6. **CI/CD Integration** — Auto-generate previews on commits

## References

- Game Boy Color Graphics: [DMG-01 Documentation](https://rylev.github.io/DMG-01/public/book/graphics/)
- Palette System: [Pan Docs - Graphics](https://gbdev.io/pandocs/Graphics.html)
- Tile Format: [2bpp Encoding Guide](https://www.codeslinger.co.uk/pages/projects/gameboy/graphics.html)

## See Also

- `tile_pixels.py` — Pixel database
- `tiles.py` — Tile generation functions  
- `build_rom.py` — ROM assembly (color definitions)
- `HOW_TO_ADD_CONTENT.md` — Content creation guide
