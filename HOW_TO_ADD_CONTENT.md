# How to Add Content to Bunny Garden Adventure

This guide explains how to add new tiles, music, and story content without writing code.

---

## Quick Start

All content is defined in JSON asset files in the `assets/` directory. Three systems manage content:

1. **Aesthetics** — Tile graphics and color palettes
2. **Sound** — Music, songs, and sound effects
3. **Narrative** — Dialog, scenes, and branching story

---

## 1. Adding Tiles and Palettes

### Location
File: `assets/aesthetics.json`

### Palette Structure

```json
{
  "palettes": {
    "grass": {
      "id": 0,
      "type": "BG",
      "colors": ["#1E1E1A", "#121A0C", "#0C1508", "#060E04"]
    },
    "bunny": {
      "id": 0,
      "type": "OBJ",
      "colors": ["#000000", "#FF69B4", "#FF1493", "#FFFFFF"]
    }
  }
}
```

**Parameters:**
- `id` (0-7): Palette index within type
- `type` ("BG" or "OBJ"): Palette type (background or sprite)
- `colors`: List of 4 hex color values (#RRGGBB)

### Tips for Palette Design

- **Color 0** is always transparent/background
- **Colors 1-3** are foreground colors
- Use complementary colors for contrast
- Test on Game Boy emulator to verify appearance
- BG palettes (0-7) used for map tiles
- OBJ palettes (0-7) used for sprites (bunny, items)

### Tile Graphics

Currently tiles are defined in `tiles.py` as Python functions. To add a new tile:

1. Edit `tiles.py`
2. Create a pixel function:
   ```python
   def my_new_tile():
       return [
           [0, 0, 1, 1, 2, 2, 3, 3],
           [0, 0, 1, 1, 2, 2, 3, 3],
           ...
       ]
   ```
3. Register it with the registry in `aesthetics.py`:
   ```python
   from aesthetics import registry
   registry.allocate_bg_tile("my_tile", my_new_tile, palette=0)
   ```

---

## 2. Adding Music and Sound Effects

### Location
File: `assets/sounds.json`

### Sound Effects

```json
{
  "effects": {
    "pop": {
      "channel": "pulse1",
      "frequency": 131072,
      "duration": 10,
      "volume": 15
    },
    "chime": {
      "channel": "wave",
      "frequency": 65536,
      "duration": 20,
      "volume": 12
    }
  }
}
```

**Parameters:**
- `channel`: "pulse1", "pulse2", "wave", or "noise"
- `frequency`: Game Boy frequency value (higher = higher pitch)
- `duration`: Length in frames (1/60 second per frame)
- `volume`: 0-15 (0=silent, 15=loudest)

### Songs

```json
{
  "songs": {
    "title_theme": {
      "tempo": 120,
      "loop": false,
      "channels": {
        "melody": {
          "type": "pulse1",
          "notes": [
            {"frequency": 131072, "duration": 30},
            {"frequency": 122070, "duration": 30},
            {"type": "silence", "duration": 15}
          ]
        },
        "harmony": {
          "type": "pulse2",
          "notes": [
            {"frequency": 65536, "duration": 30},
            {"frequency": 61035, "duration": 30},
            {"type": "silence", "duration": 15}
          ]
        }
      }
    }
  }
}
```

**Song Parameters:**
- `tempo`: Beats per minute (reference only; durations in frames)
- `loop`: true/false (song repeats when finished)
- `channels`: Named channels (melody, harmony, bass, etc.)

**Channel Parameters:**
- `type`: "pulse1", "pulse2", "wave", or "noise"
- `notes`: Array of note/silence objects

**Note Parameters:**
- `frequency`: Game Boy frequency (0-131072)
- `duration`: Length in frames
- `volume`: 0-15 (optional, default 15)

**Silence Parameters:**
- `type`: "silence"
- `duration`: Rest length in frames

### Frequency Reference

Game Boy formula: `register_value = 2048 - 131072/frequency`

Common frequencies:
- C4: 131072 Hz → register ~2048
- D4: 147146 Hz → register ~2147
- E4: 165063 Hz → register ~2215
- A4: 220000 Hz → register ~2400

Use online Game Boy frequency calculators for exact values.

---

## 3. Adding Story and Dialog

### Location
File: `assets/narrative.json`

### Narrative Structure

```json
{
  "narratives": {
    "Main Campaign": {
      "version": "1.0",
      "scenes": {
        "intro": {
          "name": "Introduction",
          "start": "greet",
          "nodes": {
            "greet": {
              "text": "Welcome to the garden!",
              "speaker": "Sage",
              "audio": "chime",
              "choices": [
                {"label": "Listen", "next": "listen"},
                {"label": "Leave", "next": "leave"}
              ]
            },
            "listen": {
              "text": "The garden holds many secrets...",
              "speaker": "Sage",
              "choices": []
            },
            "leave": {
              "text": "You leave the garden.",
              "speaker": "",
              "choices": []
            }
          }
        }
      }
    }
  }
}
```

**Scene Parameters:**
- `name`: Human-readable scene name
- `start`: ID of first dialog node
- `nodes`: Dictionary of all dialog nodes

**Node Parameters:**
- `text`: What the character says (max 255 chars)
- `speaker`: Character name (optional)
- `audio`: Sound effect or music cue to play (optional)
- `choices`: Array of player choices (if empty, auto-advances)

**Choice Parameters:**
- `label`: What the player sees (e.g., "Yes", "No", "Help!")
- `next`: ID of next node to display

### Dialog Flow Tips

- **Linear scenes**: Chain nodes with single "next" choice
- **Branching**: Use multiple choices to create paths
- **Loops**: Can reference earlier nodes (e.g., "Talk again")
- **Dead ends**: Choices with no next show final message
- **Conditional content**: Difficult to implement via JSON; use code for complex logic

### Example: Simple Linear Dialog

```json
{
  "narratives": {
    "Garden Tour": {
      "version": "1.0",
      "scenes": {
        "tour": {
          "name": "Garden Tour",
          "start": "step1",
          "nodes": {
            "step1": {
              "text": "This is the North Garden.",
              "speaker": "Guide",
              "choices": [{"label": "Continue", "next": "step2"}]
            },
            "step2": {
              "text": "Over there is the West Garden.",
              "speaker": "Guide",
              "choices": [{"label": "Continue", "next": "step3"}]
            },
            "step3": {
              "text": "That concludes the tour!",
              "speaker": "Guide",
              "choices": []
            }
          }
        }
      }
    }
  }
}
```

### Example: Branching Dialog

```json
{
  "narratives": {
    "Help Quest": {
      "version": "1.0",
      "scenes": {
        "decision": {
          "name": "Make a Choice",
          "start": "ask",
          "nodes": {
            "ask": {
              "text": "Will you help me?",
              "speaker": "Villager",
              "choices": [
                {"label": "Yes, I'll help!", "next": "accept"},
                {"label": "No, sorry", "next": "refuse"}
              ]
            },
            "accept": {
              "text": "Thank you! Head to the forest.",
              "speaker": "Villager",
              "choices": []
            },
            "refuse": {
              "text": "Suit yourself.",
              "speaker": "Villager",
              "choices": []
            }
          }
        }
      }
    }
  }
}
```

---

## 4. Asset File Organization

```
assets/
├── aesthetics.json      # Tiles and palettes
├── sounds.json          # Music and sound effects
├── narrative.json       # Story and dialog
└── README.md            # Asset documentation
```

### Best Practices

1. **Keep files organized** — One asset file per system
2. **Use clear IDs** — "garden_grass" not "tile_0"
3. **Comment in files** — Add notes about design decisions
4. **Version control** — Track changes in git commits
5. **Test in emulator** — Verify assets appear correctly
6. **Use semantic naming** — Follow existing conventions

---

## 5. Workflow Example: Add a Flower Tile

### Step 1: Design the Palette

Edit `assets/aesthetics.json`:

```json
{
  "palettes": {
    "flowers": {
      "id": 5,
      "type": "BG",
      "colors": ["#1E1E1A", "#FF69B4", "#FF1493", "#FFD700"]
    }
  }
}
```

### Step 2: Create the Tile Graphic

Edit `tiles.py`:

```python
def flower_tile():
    return [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 2, 2, 1, 1, 0],
        [0, 1, 1, 2, 2, 1, 1, 0],
        [0, 0, 1, 3, 3, 1, 0, 0],
        [0, 0, 0, 3, 3, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
```

### Step 3: Register the Tile

Edit `tiles.py` or a new module. Call during game initialization:

```python
from aesthetics import registry
registry.allocate_bg_tile("flower", flower_tile, palette=5, description="Pretty flower")
```

### Step 4: Use in Game

Reference in screen/tilemap code:

```python
# In tilemaps.py or game code
TILE_FLOWER = registry.get_tile(0x15).index  # Get allocated index
```

---

## 6. Common Issues

### Tile doesn't appear
- Verify palette ID matches tile's palette
- Check tile index is in valid range (BG: 0x10-0x3F, OBJ: 0x08-0x0F)
- Ensure tilemap references correct tile index

### Music sounds wrong
- Verify frequency values are correct
- Test in emulator with different channels
- Check duration doesn't exceed frame budget

### Dialog doesn't advance
- Verify choice "next" values point to existing nodes
- Ensure scene contains all referenced nodes
- Check no circular loops (unless intentional)

### Build fails
- Validate JSON syntax (use online validator)
- Verify all referenced IDs exist
- Check file encoding is UTF-8

---

## 7. Advanced: Custom Pixel Functions

For complex tiles, create reusable patterns:

```python
def create_checkerboard_tile(pattern_colors):
    """Generate checkerboard pattern from color indices."""
    tile = []
    for row in range(8):
        row_data = []
        for col in range(8):
            color = pattern_colors[(row + col) % len(pattern_colors)]
            row_data.append(color)
        tile.append(row_data)
    return tile

# Use it
checker = create_checkerboard_tile([0, 1])
registry.allocate_bg_tile("checker", lambda: checker, palette=0)
```

---

## 8. Integration with Build System

Assets are loaded during ROM build:

1. `build_rom.py` calls `load_assets_from_json()`
2. All JSON files in `assets/` are processed
3. Data is encoded and embedded in ROM
4. Build generates ROM with all content

To rebuild with new assets:

```bash
python build_rom.py
```

---

## See Also

- `DEVELOPMENT.md` — Architecture and technical details
- `tests/unit/test_aesthetics.py` — Asset loading tests
- `tests/unit/test_sound.py` — Sound system tests
- `tests/unit/test_narrative.py` — Narrative system tests
