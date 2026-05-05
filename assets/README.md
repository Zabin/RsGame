# Game Assets

This directory contains all game content defined in JSON format:

- **aesthetics.json** — Tile graphics and color palettes
- **sounds.json** — Music tracks and sound effects
- **narrative.json** — Story dialog and branching narrative

## Asset Types

### Aesthetics
Defines color palettes for backgrounds and objects. Each palette has:
- ID (0-7 within type)
- Type (BG or OBJ)
- 4 colors in hex format (#RRGGBB)

### Sounds
Defines music and sound effects. Effects have:
- Channel (pulse1, pulse2, wave, noise)
- Frequency (Game Boy value)
- Duration (frames)
- Volume (0-15)

Songs have multiple channels that play simultaneously, each with a sequence of notes and silences.

### Narrative
Defines dialog and story scenes. Each narrative tree contains:
- Multiple scenes (e.g., "intro", "forest_zone")
- Each scene has nodes with dialog text
- Nodes can have player choices leading to other nodes

## Loading Assets

Assets are loaded during ROM build:

```python
from aesthetics import load_assets_from_json as load_aesthetics
from sound import load_sounds_from_json
from narrative import load_narrative_from_json

# Load from JSON files
aesthetics = load_aesthetics('assets/aesthetics.json')
sounds = load_sounds_from_json('assets/sounds.json')
story = load_narrative_from_json('assets/narrative.json')
```

## Adding New Content

See `HOW_TO_ADD_CONTENT.md` for detailed guides on:
- Adding tiles and palettes
- Creating music and sound effects
- Writing dialog and branching story

## Content Guidelines

- Use clear, descriptive IDs (e.g., "garden_grass" not "tile_1")
- Keep files organized and well-commented
- Test content in the Game Boy emulator
- Track changes with git commits

## File Format

All files use standard JSON format. Validate syntax with:
```bash
python -m json.tool assets/aesthetics.json
```
