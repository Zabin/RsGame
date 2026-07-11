# memory.md — Runtime Notes & Debug Log

## Current Build Status

Shipped game: **Bunny Quest**, 9 zones (3×3 grid), 9-carrot victory condition. ROM builds at
exactly 32768 bytes; **125/125 `test_rom.py` checks pass** (headless PyBoy, repo-relative
paths — `python3 build_rom.py <out.gbc>` then `python3 test_rom.py` from the repo root; no
absolute paths required since `IP-9010`). This file is a live quick-reference maintained by the
stage-08 skills — its byte-level tables below are quick lookups only; the authoritative source
for all of them is [`docs/architecture/07-data-model.md`](docs/architecture/07-data-model.md)
(GDS-07) and [`08-presentation-architecture.md`](docs/architecture/08-presentation-architecture.md)
(GDS-08). Update GDS-07/08 first when a byte layout changes; this file's tables are copies for
convenience and must be re-derived from there, not hand-edited independently — duplication
without that discipline is exactly what went stale before (`BL-0007`/`BL-0008`).

### Last verified working (PyBoy 2.7.0 headless test, 2026-07-09)

- Title → Intro → gameplay flow renders correctly across all 9 zones
- Bunny sprite: single 8×16 OBJ pair per walk frame (not two separate 8×8 entries)
- D-pad movement, star/flower/carrot collection, `SCORE`/`CARROTS_COUNT` HUD all confirmed
- Zone transition via screen-edge walk-off across the full 3×3 grid
- START → SAVE menu (A=save, B=cancel); SELECT → MAP screen (B=exit), shows 9-carrot progress
- Victory screen fires at `CARROTS_COUNT == 9`
- SRAM battery save works (MBC1+RAM+BATTERY, magic `BUNY`, `SAVE_VERSION_VAL` guard); a valid
  save auto-loads on boot
- Per-zone `ScoreItem` (star/flower) collected-state persists across save/reload within a
  session and does not re-award `SCORE` on zone re-entry (`FR-5220`, `IP-1010`)

---

## Tile Index Map (quick ref — authoritative table: GDS-07 §4)

| Range | Content |
|---|---|
| `0x00`–`0x03` | Bunny walk frames, 8×16 OBJ pairs (`00`/`01`, `02`/`03`) |
| `0x04`–`0x09` | Carrot / star / flower OBJ sprites (each + blank pad tile) |
| `0x10`–`0x19` | UI icons: BG blank, heart full/empty, carrot icon, star icon, border, 4 arrows |
| `0x20`+ | Digits |
| `0x40`–`0x61` | Font: A–Z + punctuation |
| `0x70`–`0x76` | Beach terrain | `0x78`–`0x7D` | Forest terrain |
| `0x80`–`0x85` | Mountain terrain | `0x88`–`0x8D` | Lake terrain |
| `0x90`–`0x95` | Village terrain | `0x98`–`0x9D` | Cave terrain |
| `0xA0`–`0xA5` | Desert terrain | `0xA8`–`0xAD` | Plains terrain |
| `0xB0`–`0xB5` | Castle terrain | `0xB6`–`0xFF` | Free (74 slots unused; next 8-aligned block: `0xB8`) |

## BG Palette Quick Ref (authoritative table: GDS-07 §5 / GDS-08 §4)

Palettes are assigned **by terrain family, not one-per-zone** — 5 of 8 in active zone use today.

| Pal | Terrain family | Zones using it |
|-----|-----|-------------|
| 0 | Grass | Forest, Plains |
| 1 | Sand/dirt | Beach, Desert |
| 2 | UI/gold | *(UI screens only)* |
| 3 | Water | Lake |
| 4 | Stone | Mountain, Village, Cave |
| 5 | Brick/red | Castle |
| 6 | Tree/leaf | *(accent role)* |
| 7 | Accent purple | *(accent role)* |

## OBJ Palette Quick Ref

4 of 8 in active use — bunny, star, flower, carrot; 4 reserved/unused. Exact color values live
in `build_rom.py`'s `OBJ_PALETTES` table (GDS-07 §5).

## Joypad Bit Map (JOY_CUR — active HIGH)
```
bit 0 = A        bit 4 = RIGHT
bit 1 = B        bit 5 = LEFT
bit 2 = SELECT   bit 6 = UP
bit 3 = START    bit 7 = DOWN
```

## Collectible Positions

Collectible layouts (stars/flowers/one carrot each) are authored in `tilemaps.py`'s
`ZONE_COLLECTS` table — that table is the single source of truth for positions; this file no
longer duplicates the coordinates (a hand-copy is exactly the kind of table that drifts). As of
`IP-9070` (2026-07-11), `ZONE_COLLECTS` has **5 biome-family-representative lists**, indexed by
biome-id (`0`=Water `1`=Sand `2`=Grass `3`=Stone `4`=Brick), not 9 zone-indexed lists —
`setup_zone_collects` reads `REGION_GRAPH`'s biome-id and indexes by that, mirroring the screen
dispatch's own biome-id lookup (`IP-1030`). To find a biome family's layout: open `tilemaps.py`,
search `ZONE_COLLECTS`.

## Emulator Test Command

```python
from pyboy import PyBoy
pb = PyBoy('BunnyQuest.gbc', window='null', sound_emulated=False)   # repo-relative
pb.set_emulation_speed(0)
```

`test_rom.py` derives `ROM_PATH`/`RAM_PATH` repo-relative from its own location — no absolute
paths, no manual cleanup needed before a fresh run (the suite handles its own `.ram` state).
The `run-bunnygarden` utility skill wraps this for driving the game with button input and
screenshots.
