# Bunny Garden Adventure 🐰🌻

A playable **Game Boy Color game** built entirely in Python, compiling to a 32KB ROM. Explore three zones (Garden, Forest, Meadow), collect gifts, and discover the magic of the garden.

**Status:** v2 — Feature complete with battery-backed saves, 3-zone exploration, gift collection, and persistent high scores.

---

## Quick Start

### Prerequisites
- Python 3.10+
- `pip` (Python package manager)

### Build the ROM
```bash
python3 build_rom.py
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

### Run Tests
```bash
# Full test suite (requires PyBoy)
python3 test_rom.py

# Quick build validation
python3 -c "from build_rom import build; rom = build('test.gbc'); print(f'ROM: {len(rom.data)} bytes')"
```

---

## Project Structure

```
RsGame/
├── gbc_lib.py        — ROM assembler: opcodes, color math, header writing
├── tiles.py          — Tile pixel art (8×8) + encoding
├── tilemaps.py       — Screen generators + collectible spawn tables
├── music.py          — Music data (Twinkle Twinkle melody)
├── asm_game.py       — Game logic: state machine, movement, scoring (SM83 assembly)
├── build_rom.py      — Master builder: compiles all modules → 32KB ROM
├── test_rom.py       — PyBoy emulation tests (state transitions, gameplay)
├── Claude.md         — Original developer guide
├── DEVELOPMENT.md    — Comprehensive architecture & how-to guide
├── CONTRIBUTING.md   — Contributing guidelines, commit conventions
├── memory.md         — Detailed memory maps (WRAM, ROM, SRAM, VRAM)
└── .gitignore        — Git ignore patterns
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

## Development

### Setting Up
```bash
# Install dependencies for testing
pip install pyboy pytest black pylint

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

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

See [DEVELOPMENT.md Known Issues](DEVELOPMENT.md#known-issues) for details:

- **Map hearts:** Address calculation off by one row (rendering issue, [fix documented](memory.md))
- **Bunny render:** Uses two 8×8 OAM tiles (appears small)
- **Score writes:** Not VBlank-gated (works in practice, hardware edge case)

These are planned for Phase 2-3 bug fix release.

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

## Future Roadmap (Phase 2+)

See [DEVELOPMENT.md Roadmap](DEVELOPMENT.md#roadmap) for:
- Bug fix release (map hearts, score VBlank gating, ROM validation)
- Music system expansion (multi-track compositions)
- Tile/palette registry (easy content creation)
- Dialog system (NPC interactions, branching storyline)
- Story framework (lore, characters, narrative progression)

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
