# Bunny Garden Adventure 🐰🌻

A playable **Game Boy Color game** built entirely in Python, compiling to a 32KB ROM. Explore three zones (Garden, Forest, Meadow), collect gifts, and discover the magic of the garden.

**Status:** v3 — Phase 5 complete. Feature-complete gameplay with battery-backed saves, graphics iteration tools, 180+ tests, and enhanced biome artwork.

---

## Quick Start

### Prerequisites
- Python 3.10+
- `pip` (Python package manager)
- `make` (for convenient build commands; optional but recommended)

### Setup
```bash
pip install -r requirements.txt
make install-hooks    # Install git pre-commit hook (optional)
```

### Build the ROM
```bash
make build
# Output: BunnyGarden.gbc (32KB Game Boy Color ROM)
```

### Play in an Emulator
1. Download [PyBoy](https://github.com/Baekalfen/PyBoy) or [BGB](https://bgb.bircd.org/) emulator
2. Open `BunnyGarden.gbc` in your emulator
3. **Controls:**
   - **D-Pad:** Move bunny left/right
   - **START:** Open SAVE menu (A=save, B=cancel)
   - **SELECT:** Open MAP screen (B=close)
   - **A:** Confirm dialogs

### Run Tests & Generate Previews
```bash
# Full build pipeline (tests, ROM, previews)
make all

# Run tests only
make test              # All tests (requires PyBoy)
make test-unit        # Unit tests only (fast, ~0.2s)

# Generate graphics previews (no ROM rebuild)
make previews
```

---

## Project Structure

```
RsGame/
├── gbc_lib.py           — ROM assembler: opcodes, color math, header writing
├── tiles.py             — Tile pixel art (8×8) + encoding
├── tilemaps.py          — Screen generators + collectible spawn tables
├── music.py             — Music data (Twinkle Twinkle melody)
├── asm_game.py          — Game logic: state machine, movement, scoring (SM83 assembly)
├── build_rom.py         — Master builder: compiles all modules → 32KB ROM
├── test_rom.py          — PyBoy emulation tests (state transitions, gameplay)
├── tile_pixels.py       — Raw tile pixel database (8×8 arrays, 0-3 values)
├── tile_preview.py      — Render tiles to PNG (fast iteration tool)
├── screen_preview.py    — Render screens to PNG (tilemap + attributes)
├── graphics_utils.py    — Shared graphics utilities (color conversion, palette loading)
├── GRAPHICS_PREVIEW.md  — Graphics iteration workflow & tool usage
├── Claude.md            — Original developer guide
├── DEVELOPMENT.md       — Comprehensive architecture & how-to guide
├── CONTRIBUTING.md      — Contributing guidelines, commit conventions
├── memory.md            — Detailed memory maps & build status
└── .gitignore           — Git ignore patterns
```

---

## Architecture Overview

**One file, one job:**
- **gbc_lib.py** — Low-level ROM class (no game-specific logic)
- **tiles.py** — Tile pixel data only (no screen layout logic)
- **tilemaps.py** — Screen layouts only (no gameplay logic)
- **asm_game.py** — Game logic only (imports constants but not render code)
- **build_rom.py** — Orchestrator (imports all, patches addresses, writes file)

**Design principle:** Minimal coupling. Each module is independently testable.

---

## Game Overview

### Game States
1. **TITLE** — Press START
2. **INTRO** — Story/tutorial (press A)
3. **PLAYING** — Explore 3 zones, collect gifts
4. **SAVE** — Save progress to cartridge battery
5. **MAP** — See which zones have gifts (heart icons)
6. **VICTORY** — Collected all 3 gifts!

### The Three Zones
- **Garden** 🌷 — Starting area, natural grass and flowers
- **Forest** 🌲 — Trees, mushrooms, slightly harder collectible positions
- **Meadow** 🌼 — Wide open space with varied landscape

### Gameplay
- Collect **3 gifts** (one per zone) to win
- Move bunny with D-Pad; animation is automatic
- Gifts appear near collectible pickup zones (star 🌟, flower 🌺)
- SRAM battery save persists game state across power cycles

---

## Graphics Preview Tools (Phase 5)

**Iterate graphics without full ROM builds** — preview PNG output in < 1 second.

### Quick Start

```bash
# Generate tile previews (grids + individual tiles)
python tile_preview.py --all
python tile_preview.py --tile 0x10        # Single tile
python tile_preview.py --type bg          # All background tiles
python tile_preview.py --palettes         # Palette swatches

# Generate screen previews (complete tilemaps)
python screen_preview.py --all
python screen_preview.py --screen garden  # Single screen
python screen_preview.py --all --grid     # With tile grid overlay

# View outputs
open previews/                    # macOS/Linux
start previews/                   # Windows
```

### Features

- **Tile Preview:** 8×8 tiles at 8× upscale, hex-labeled grids, palette visualization
- **Screen Preview:** 32×18 tilemaps with attributes applied, 2× upscale (512×576 px)
- **Instant Feedback:** Generate all previews in ~1 second vs. 30-90 second full build
- **Side-by-side Comparison:** View before/after graphics changes immediately

### Workflow

1. Edit tile pixels in `tile_pixels.py`
2. Run `python tile_preview.py --all` to see changes instantly
3. Edit screen layouts in `tilemaps.py`
4. Run `python screen_preview.py --all` to verify full screens
5. Build final ROM when satisfied: `python build_rom.py`

**See [GRAPHICS_PREVIEW.md](GRAPHICS_PREVIEW.md) for comprehensive tool documentation.**

---

## Development

### Setting Up
```bash
# Install all dependencies
pip install -r requirements.txt

# Or manually:
pip install pyboy pytest black pylint flake8 pillow

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

**Pillow is required** for graphics preview tools (`tile_preview.py`, `screen_preview.py`).

### Making Changes

**See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed how-to guides:**
- [Add a new tile](DEVELOPMENT.md#add-a-new-tile)
- [Edit a screen layout](DEVELOPMENT.md#edit-a-screen-layout)
- [Change game logic](DEVELOPMENT.md#change-game-logic)
- [Add a new game state](DEVELOPMENT.md#add-a-new-game-state)
- [Understand the ROM layout](DEVELOPMENT.md#rom-layout)

### Commit Conventions
Use conventional commit format:
```
[SCOPE] Short description (< 70 chars)

Detailed explanation if needed.
- Bullet point 1
- Bullet point 2

Fixes: (optional issue ref)
```

**Scopes:**
- `[BUILD]` — ROM generation, build_rom.py
- `[GAME]` — Game logic, asm_game.py
- `[TILES]` — Tile/palette work
- `[LAYOUT]` — Screen/zone layouts
- `[MUSIC]` — Audio
- `[TEST]` — Tests
- `[DOCS]` — Documentation

Example:
```
[TILES] Add stone path tile variant

Added TL_PATH_STONE with gray palette for forest paths.
Useful for rocky areas and transitions between biomes.

Fixes: visual variety in forest zone
```

### Testing
```bash
python3 test_rom.py            # Full emulation test
pytest tests/ --cov             # (Phase 2+) Coverage report
```

---

## Known Issues & Limitations

### Minor Issues (Low Priority)

- **Map hearts:** Address calculation off by one row (visual glitch, [fix documented](memory.md))
  - Hearts display at rows 6/8/10 instead of intended rows
  - Functionality unaffected; planned for Phase 6 polish release
  
- **Bunny render:** Uses two 8×8 OAM tiles (appears small relative to background)
  - Matches GBC architectural constraints
  - Animation frames (4 total) working correctly
  
- **Score writes:** Not VBlank-gated
  - Works in practice on all tested emulators
  - Edge case on real hardware; planned for Phase 6

### Tested Compatibility

- **Emulators:** PyBoy 2.7.0+ (full pass), BGB (expected to work)
- **Platforms:** Linux, macOS, Windows
- **ROM Type:** MBC1, 32KB + 8KB SRAM + Battery (cart type 0x03)

See [DEVELOPMENT.md Known Issues](DEVELOPMENT.md#known-issues) for detailed technical notes.

---

## ROM Size Budget

**32KB total:**
```
0x0000-0x00FF   RST vectors + ISRs          256 bytes
0x0100-0x0150   Entry point                 80 bytes
0x0150-0x0800   Game code (asm_game.py)     ~6.5 KB
0x0800-0x1800   Tile data (256 tiles)       4 KB
0x1800-0x187F   BG + OBJ palettes           128 bytes
0x1880+         Music data + screens + tables  ~20 KB
```

**Headroom:** ~4-5 KB available for future expansions.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Branch naming convention
- Pull request process
- Code style expectations
- Testing requirements

---

## Technical Details

### Memory Maps
- **WRAM (0xC000–0xC2FF):** Game state variables (position, score, flags)
- **VRAM (0x8000–0x9FFF):** Tile data, tilemaps, palettes
- **SRAM (0xA000–0xBFFF):** Persistent save game (battery-backed)
- **ROM (0x0000–0x7FFF):** Code, graphics, music

See [memory.md](memory.md) for detailed breakdown.

### Build Pipeline
```
tiles.py  ──┐
tilemaps.py┼→ build_rom.py ──→ ROM assembler ──→ BunnyGarden.gbc
music.py  ──┤ (orchestrator)   (gbc_lib.py)
asm_game.py─┘
```

1. Each module exports data functions
2. `build_rom.py` calls all data generators
3. `gbc_lib.ROM` class patches addresses into code
4. Final ROM written with GBC header and checksum

---

## Performance & Emulator Compatibility

- **Tested:** PyBoy 2.7.0+ (headless emulation)
- **Expected:** Works on real GBC hardware (uses standard GBC features)
- **Performance:** Emulation at full speed (~60 FPS)
- **ROM type:** MBC1 with 32KB ROM + 8KB RAM + Battery (cart type 0x03)

---

## Completed Phases

✅ **Phase 1:** Core gameplay (movement, collision, gift collection)
✅ **Phase 2:** Zones & state transitions (3 zones, save system, persistent scoring)
✅ **Phase 3:** Tile encoding & rendering (all 54 tiles, 8 BG + 4 OBJ palettes)
✅ **Phase 4:** Audio (Twinkle Twinkle melody, mute toggle)
✅ **Phase 5:** Feature architecture (graphics iteration tools, comprehensive test suite, 180+ tests)

## Future Roadmap (Phase 6+)

Planned enhancements:

**Phase 6 — Enhanced Graphics:**
- Animation preview (GIF export for sprite sequences)
- Palette designer (interactive RGB15 color picker)
- Tile editor (8×8 pixel grid UI)
- Additional biomes (Desert, Cave, Swamp from concept art)

**Phase 7 — Gameplay Expansion:**
- Dialog system (NPC interactions, branching storyline)
- Inventory mechanics (use/combine items)
- Boss encounters or puzzle challenges

**Phase 8 — Polish & Optimization:**
- Performance profiling
- Battery save encryption
- ROM size optimization
- Real hardware testing (actual GBC cartridge)

See [DEVELOPMENT.md Roadmap](DEVELOPMENT.md#roadmap) for detailed architecture guidance.

---

## License

Generated via Claude AI code generation. See repository for LICENSE if applicable.

---

## Questions?

See [DEVELOPMENT.md](DEVELOPMENT.md) for architecture deep-dives and how-to guides.

For bugs, file an issue with:
- Description of what happened
- Steps to reproduce
- Expected vs. actual behavior
- Emulator version
