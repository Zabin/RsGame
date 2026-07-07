# GDS-07 — Data Model

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-06](06-non-functional-requirements.md); the
> next level, [GDS-08 Presentation Architecture](08-presentation-architecture.md), builds on this
> one. **This is the first level authorized to state exact byte addresses** — GDS-04's Domain
> Model deliberately stayed at entity altitude and deferred all of this here.

## Purpose

ROM section layout, WRAM map (C000–C2FF), SRAM save format (magic `BUNY`), tile index map,
palette tables.

## Content

### 1. ROM section layout

Confirmed directly against `build_rom.py`'s `build()`. Code (emitted by `build_game_asm`) is
padded to the next `0x100` boundary; sections follow in this fixed order:

```
code (build_game_asm output, padded to 0x100)
tile data          — build_tile_data()
BG palette bytes   — 8 palettes × 4 colors × 2 bytes = 64 bytes
OBJ palette bytes  — 8 palettes × 4 colors × 2 bytes = 64 bytes
music data         — music_data()
screens (×14, ALL_SCREENS order: z0…z8, title, intro, save, map, victory)
                     each screen = tile bytes, then attribute bytes
zone-screens lookup table — 9 × 4 bytes (tile_addr_lo/hi, attr_addr_lo/hi), indexed by zone
zone-collectible tables   — one per zone: 1 length byte + 4 bytes/entry (x, y, type, 0-pad)
zc_table                  — 9 × 2 bytes, pointer to each zone's collectible table
```

**Total used: 23148 of 32768 bytes** (~9.6KB headroom — [GDS-02](02-system-context.md)/
[GDS-06](06-non-functional-requirements.md) N1), confirmed by a direct build.

### 2. WRAM map (`0xC000`–`0xC3A0`)

Confirmed directly against `asm_game.py`'s constant declarations:

| Address | Name | Content |
|---|---|---|
| `C000` | `GAMESTATE` | 0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY ([GDS-01](01-concept-of-play.md)) |
| `C001` | `PLAYER_X` | pixel X |
| `C002` | `PLAYER_Y` | pixel Y |
| `C003` | `PLAYER_DIR` | facing (left/right) |
| `C004` | `PLAYER_FRAME` | walk-cycle frame |
| `C005` | `ANIM_CTR` | frame-flip counter |
| `C006` | `SCORE` | 0–99, from ScoreItem collection |
| `C007` | `SCORE_DIRTY` | redraw-needed flag |
| `C008` | `CUR_ZONE` | **0–8** (row = ÷3, col = %3) |
| `C009` | `CARROTS_COUNT` | **0–9**, victory at 9 |
| `C00A` | `NEED_REDRAW` | screen-redraw flag |
| `C00B` | `TRANSITION_TO` | pending `GAMESTATE` transition |
| `C00C`–`C00E` | `JOY_CUR`/`JOY_PREV`/`JOY_NEW` | joypad state ([R107](../research/encyclopedia/R107-joypad-register.md)) |
| `C00F`–`C011` | `MUSIC_CTR`/`MUSIC_PTR_LO`/`MUSIC_PTR_HI` | music playback state |
| `C012` | `VBLANK_FLAG` | set by ISR, cleared by main loop ([R110](../research/encyclopedia/R110-interrupt-model-isr.md)) |
| `C013`–`C014` | `TMP1`/`TMP2` | scratch |
| `C015`–`C01D` | `CARROT_FLAGS` | **9 bytes**, one per zone, 0/1 |
| `C020` | `COLL_DATA` | working collectible struct |
| `C050` | `COLL_COUNT` | collectible count for current zone |
| `C060`–`C068` | `SCOREITEM_FLAGS` | **9 bytes** — one bitfield per zone, bit *N* = the *N*th `ZONE_COLLECTS` list entry ([FR-5220](../requirements/01-functional-requirements.md), [IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md), 2026-07-07). Assigned here (deferred by [FS-101](../features/FS-101-per-zone-scoreitem-persistence.md) Open Question 3): sits inside the boot clear of `C000`–`C2FF`, 8-aligned, with headroom to `COLL_COUNT` on one side and `OAM_BUF` on the other. |
| `C300` | `OAM_BUF` | 160 bytes, shadow OAM ([R105](../research/encyclopedia/R105-oam-sprites-dma.md)) |

### 3. SRAM save format (`0xA000`+)

Confirmed directly against `try_load_save`/the save routine:

| Address | Content |
|---|---|
| `A000`–`A003` | Magic `B`,`U`,`N`,`Y` (`0x42,0x55,0x4E,0x59`) |
| `A004` | `CUR_ZONE` |
| `A005`–`A006` | `PLAYER_X`/`PLAYER_Y` |
| `A007` | `CARROTS_COUNT` |
| `A008` | `SCORE` |
| `A009`–`A011` | `CARROT_FLAGS` (9 bytes) |
| `A012` | Save-format version guard ([FR-5220](../requirements/01-functional-requirements.md); `SAVE_VERSION_VAL = 0x01`) — added 2026-07-07 by [IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md), the first save-format change since ship (`ADR-0006`). A save lacking this byte or not matching it is treated as pre-upgrade: `SCOREITEM_FLAGS` loads as all-zero (all uncollected) rather than trusting whatever garbage occupies `A013`–`A01B`. |
| `A013`–`A01B` | `SCOREITEM_FLAGS` mirror (9 bytes) — same addition. |

**This updates `BL-0018`'s prior field-set finding** ([GDS-04](04-domain-model.md)): per-zone
ScoreItem state is no longer absent — `A012`–`A01B` now cover it (per the user's 2026-07-07
decision recorded at [RQ-01](../requirements/01-functional-requirements.md) FR-5220). `PLAYER_DIR`/
`PLAYER_FRAME` remain absent, per the same decision (explicitly rejected as "not important").

### 4. Tile index map (`0x00`–`0xFF`, 83 of 256 slots used)

Confirmed directly against `tiles.py`'s 83 `TL_*` constants:

| Range | Content |
|---|---|
| `0x00`–`0x09` | OBJ sprites: bunny frames (8×16 pairs `00/01`, `02/03`), carrot (`04`+blank `05`), star (`06`+blank `07`), flower (`08`+blank `09`) |
| `0x10`–`0x19` | UI icons: BG blank, heart full/empty, carrot icon, star icon, border, 4 direction arrows |
| `0x20`+ | Digits |
| `0x40`–`0x61` | Font: A–Z + punctuation |
| `0x70`–`0x76` | **Beach** terrain (sand, water edge, palm, shell) |
| `0x78`–`0x7D` | **Forest** terrain (grass, tree, mushroom, log) |
| `0x80`–`0x85` | **Mountain** terrain (snow, peak, rock, icicle) |
| `0x88`–`0x8D` | **Lake** terrain (deep water, lilypad, reed, fish, pier) |
| `0x90`–`0x95` | **Village** terrain (cobble, house, lantern, fence) |
| `0x98`–`0x9D` | **Cave** terrain (floor, wall, crystal, drip, bat) |
| `0xA0`–`0xA5` | **Desert** terrain (dune, cactus, bones, pyramid) |
| `0xA8`–`0xAD` | **Plains** terrain (grass, flowers, butterfly, tall grass) |
| `0xB0`–`0xB5` | **Castle** terrain (brick, gold, banner, gate, torch) |
| `0xB6`–`0xFF` | **Free** — 74 slots unused |

Each zone owns a clean, 8-tile-aligned block (using 6–8 of the 8 slots per zone) — a deliberate,
consistent allocation pattern a future 10th zone should follow (next free 8-aligned block:
`0xB8`).

### 5. Palette tables — corrected picture (supersedes `BL-0009`'s framing)

Confirmed directly against `build_rom.py`'s `BG_PALETTES`/`OBJ_PALETTES` tables and each zone
screen's actual palette argument. **The 8 BG palettes are organized by terrain type, not
one-per-zone, and are already substantially reused:**

| BG palette | Terrain family | Zones using it |
|---|---|---|
| 0 | grass | Forest, Plains |
| 1 | sand/dirt | Beach, Desert |
| 2 | UI/gold | *(UI screens, not a zone terrain)* |
| 3 | water | Lake |
| 4 | stone | Mountain, Village, Cave *(three zones)* |
| 5 | brick/red | Castle |
| 6 | tree/leaf | *(accent role, not a zone base terrain)* |
| 7 | accent purple | *(accent role, not a zone base terrain)* |

**Only 5 of 8 BG palettes are used as zone terrain today** (0, 1, 3, 4, 5); three zones already
share palette 4. **This corrects [`BL-0009`](../pipeline/backlog.md)'s prior framing** ("already
at or near its ceiling… at least one pair shares") — the real picture is more headroom and more
reuse than that framing suggested: a design decision to organize palettes by terrain family, not
by individual zone, was already made and already accommodates significant zone growth before the
8-palette ceiling becomes binding. (OBJ palettes: 4 of 8 in active use — bunny, star, flower,
carrot; 4 unused/placeholder slots remain.)

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail *beyond* what this level calls for (byte addresses
      are exactly this level's job).
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-06`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `Claude.md`'s "Data layout in ROM"/"WRAM map"/"SRAM save format"
sections and `memory.md`'s tile-index/palette quick-reference tables are the sources this level
was scaffolded to merge from — both describe the *pre-rewrite* game (3 zones, gifts, different
WRAM layout) and are **not** the source of the facts above, which are verified directly against
the current `build_rom.py`/`asm_game.py`/`tiles.py`. **Decision: this level supersedes both
documents' byte-level tables entirely** — the single most consequential merge decision in this
ladder so far, since these are exactly the tables developers reach for first when touching game
code. Both should become short pointers here once the `BL-0007`/`BL-0008` documentation-refresh
pass lands; until then they remain flagged stale (per `MSTR-001` §6).
