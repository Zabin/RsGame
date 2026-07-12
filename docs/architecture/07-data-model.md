# GDS-07 — Data Model

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment — see "Data Model delta" below).** Owned by `03-architecture-design-synthesis`.
> Builds on [GDS-06](06-non-functional-requirements.md); the next level,
> [GDS-08 Presentation Architecture](08-presentation-architecture.md), builds on this one.
> **This is the first level authorized to state exact byte addresses** — GDS-04's Domain
> Model deliberately stayed at entity altitude and deferred all of this here.
>
> **Reading this document:** §§1–5 below describe the ROM/WRAM/SRAM/tile/palette layout **as
> currently shipped** and remain accurate. The delta section describes the **target** layout
> [ADR-0009](adr/ADR-0009-screen-graph-world-generation.md)/
> [ADR-0010](adr/ADR-0010-seed-scale-model.md) commit to — proposed addresses, not yet built;
> final confirmation happens at implementation, the same precedent `FS-101`/`IP-1010` set for
> `SCOREITEM_FLAGS`' address.

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
| `C220`–`C270` | `KEYITEM_FLAGS` | **up to 81 bytes**, one per region — generalizes the original `CARROT_FLAGS` ([IP-1020](../implementation/packages/IP-1020-world-generation-engine.md)); only indices 0–8 are live until `FEAT-1100` ships. |
| `C070`–`C204` | `REGION_GRAPH` | **up to 405 bytes**, 5 bytes/region (biome-id + 4 neighbor-region-index bytes: up/down/left/right, `0xFF`=none), up to 81 regions ([IP-1020](../implementation/packages/IP-1020-world-generation-engine.md)/[IP-1030](../implementation/packages/IP-1030-generated-region-screen-composition.md)). Never persisted to SRAM — regenerated from `SEED`/`WORLD_SCALE` on load. |
| `C286`–`C2D6` | `SCOREITEM_FLAGS` | **up to 81 bytes**, one bitfield per region, bit *N* = the *N*th `ZONE_COLLECTS`-family-list entry ([FR-5220](../requirements/01-functional-requirements.md); originally 9 bytes at `C060`–`C068` per [IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md), 2026-07-07; relocated and widened to 81 bytes by [IP-9070](../implementation/packages/IP-9070-cur-zone-indexed-structures-generalization.md), 2026-07-11, to the confirmed-unused gap between `SSE_CURSOR` (ends `C285`) and `OAM_BUF` — growing in place at `C060` would have collided with `REGION_GRAPH` at `C070`). `setup_zone_collects` now indexes `zc_table` by `REGION_GRAPH`'s biome-id rather than `CUR_ZONE` directly ([BL-0059](../../pipeline/backlog.md) fix). |
| `C2D7` | `MM_JUST_ENTERED` | 1 byte — set by every `GAMESTATE` → `GS_MAIN_MENU` transition site, cleared by `mm_on_entry` once consumed ([IP-9060](../implementation/packages/IP-9060-main-menu-cursor-fix.md), `BL-0048`). |
| `C2D8`–`C2D9` | `DRA_ROW`/`DRA_COL` | 2 bytes — `draw_region_arrows`' own re-derived `(row, col)` position (`CUR_ZONE` / `WORLD_SCALE`, `CUR_ZONE` MOD `WORLD_SCALE`), computed once per call and shared by all four direction tests ([IP-1080](../implementation/packages/IP-1080-maze-aware-edge-classification.md), [FR-2330](../requirements/01-functional-requirements.md)). Transient, meaningless outside a `draw_region_arrows` call, same convention as the `GW_*` family below. Added mid-implementation in place of the originally-suggested `TMP1`/`TMP2` reuse — `TMP1` collides with `handle_play_input`'s own per-frame "did the player move" flag. |
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
| `A012` | Save-format version guard ([FR-5220](../requirements/01-functional-requirements.md); `SAVE_VERSION_VAL = 0x03`) — added 2026-07-07 by [IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md) at `0x01`; bumped to `0x02` by [IP-1050](../implementation/packages/IP-1050-generated-world-save-persistence.md) (seed/scale/`REGION_GRAPH`-regen/`KEYITEM_FLAGS` fields); bumped to `0x03` by [IP-9070](../implementation/packages/IP-9070-cur-zone-indexed-structures-generalization.md), 2026-07-11 (`SRAM_SCOREITEM` relocation/widening below). A save whose version byte doesn't match the current value is treated as pre-upgrade: every version-guarded field loads as its fresh-new-game default rather than trusting stale/relocated SRAM bytes. |
| `A070`–`A0C0` | `SRAM_SCOREITEM` — `SCOREITEM_FLAGS` mirror, **up to 81 bytes**. Originally 9 bytes at `A013`–`A01B` ([IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md)); relocated by [IP-9070](../implementation/packages/IP-9070-cur-zone-indexed-structures-generalization.md) to immediately after `SRAM_KEYITEM_FLAGS`'s own end, leaving `SRAM_SEED`/`SRAM_WORLD_SCALE`/`SRAM_KEYITEM_FLAGS`'s addresses untouched. |

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

## Data Model delta (2026-07-09 — target state; §6 WRAM confirmed 2026-07-10 by `IP-1020`;
§7 SRAM confirmed 2026-07-10 by `IP-1050`)

Per **ADR-0009**/**ADR-0010**, additions to the WRAM/SRAM layout above. §6 (WRAM) and §7 (SRAM)
are now both **confirmed as-shipped**, following the same confidence level `FS-101` used before
`IP-1010` confirmed `SCOREITEM_FLAGS`' final placement.

### 6. WRAM additions (confirmed 2026-07-10, `IP-1020`, within existing bank-0 headroom)

The prior WRAM map ended its named allocations at `0xC068` (`SCOREITEM_FLAGS`) before jumping to
`0xC300` (`OAM_BUF`) — a ~660-byte unused gap between them
([R111](../research/encyclopedia/R111-wram-banking-sm83-prng.md) confirms ~3.1 KiB of headroom in
bank 0 alone). Shipped placement:

| Address | Name | Content |
|---|---|---|
| `C069`–`C06A` | `SEED` | 16-bit seed value (low/high byte), source for the PRNG's initial state ([R111](../research/encyclopedia/R111-wram-banking-sm83-prng.md)). Written by `FEAT-1100` (not yet shipped); read-only to `generate_world`. |
| `C06B` | `WORLD_SCALE` | 1 byte, 2–9 ([ADR-0010](adr/ADR-0010-seed-scale-model.md)). Same write/read split as `SEED`. |
| `C070`–`C070+5×(scale²)−1` | `REGION_GRAPH` | 5 bytes/region (1 biome-id byte + 4 neighbor-region-index bytes in up/down/left/right order, `0xFF`=no neighbor in that direction) × up to 81 regions at `scale=9` = **≤405 bytes worst case**, ending at `0xC204`. Written by `generate_world`. |
| `C220`–`C220+80` | `KEYITEM_FLAGS` | up to 81 bytes, one collected-flag per region (generalizes `CARROT_FLAGS`'s 9-byte array — [GDS-04](04-domain-model.md)'s delta). **`CARROT_FLAGS` (`0xC015`–`0xC01D`) is now orphaned** — `check_collisions`/`setup_zone_collects`/`update_map_hearts`/the `st_intro`/`st_victory` reset paths all target `KEYITEM_FLAGS` instead; only `save_to_sram`/`try_load_save` still mirror the old array, pending `IP-1050`'s save-format migration. A `0xC205`–`0xC21F` gap separates the two (address chosen as the implementation's own confirmed placement, not tightly packed at `0xC205`, still safely inside the boot-clear range). Written by `check_collisions`/`setup_zone_collects` (collection); read by `update_map_hearts`; cleared by the boot-time WRAM clear and the `st_intro`/`st_victory` reset paths (9 bytes each, matching `CUR_ZONE`'s current 0–8 range — full `scale²`-extent clearing on new-game/replay is `FEAT-1100`'s scope once it wires up variable-scale play). |
| `C271`–`C279` | `GW_TOP_ROW` | 9 bytes — `generate_world`'s own transient scratch (the biome of the region directly above each column, written before it's read; satisfies NFR-2200's "routine's own prior output" rule). Not part of the persisted data model; meaningless outside a `generate_world` call. |
| `C27A` | `GW_REGION_IDX` | 1 byte — `generate_world`'s own loop counter (0..scale²-1). Transient, as above. |
| `C27B` | `GW_B_SCRATCH` | 1 byte — `generate_world`'s own scratch (holds the candidate anchor value, then the final clamped biome result, across the PRNG-step `CALL` boundary). Transient, as above. |
| `C27C` | `GW_SCALE_SQ` | 1 byte — `generate_world`'s own precomputed `WORLD_SCALE²` (no `MUL` opcode on SM83; computed once via repeated addition). Transient, as above. |
| `C069`–`C06A` renamed alias | `KEYITEM_COUNT` | Same WRAM slot as `CARROTS_COUNT` (`0xC009`, unmoved) — a source-level rename only, not a new address; `check_complete`'s victory check and the HUD digit-writer still reference it under its original name (out of `IP-1020`'s scope; both work correctly either way since the address is identical). |

Worst-case total new/repurposed WRAM: ~570 bytes (`2+1+405+81+9+1+1+1`, plus the `0xC205`–`0xC21F`
padding gap) — comfortably inside the confirmed ~3.1 KiB bank-0 headroom (R111); `SVBK`/banked
WRAM is **not** triggered, consistent with R111's conclusion. All of it falls inside the existing
boot-time WRAM clear (`0xC000`–`0xC2FF`, unchanged).

### 7. SRAM save-format additions (confirmed 2026-07-10, `IP-1050`, extends the `FS-101`/
`IP-1010` version-byte pattern)

Per [R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md)'s extension and
**ADR-0010**: a new save-format version value (`SAVE_VERSION_VAL`, bumped `0x01`→`0x02` —
superseding `IP-1010`'s own value at `0xA012`) signals this layout; fields appended after the
existing `0xA013`–`0xA01B` `SCOREITEM_FLAGS` mirror, exactly at the addresses this section
proposed:

| Address | Content |
|---|---|
| `A012` | Save-format version guard — `0x02`, superseding `IP-1010`'s `0x01` |
| `A01C`–`A01D` | `SEED` mirror (16-bit) |
| `A01E` | `WORLD_SCALE` mirror |
| `A01F`–`A06F` | `KEYITEM_FLAGS` mirror, 81 bytes worst-case (generalizes the `CARROT_FLAGS` mirror at `A009`–`A011`) |

Written by `save_to_sram` (the `KEYITEM_FLAGS` copy reuses the existing `memcpy` subroutine, not
an unrolled 81-iteration loop). Restored by `try_load_save`, version-guarded: `SEED`/`WORLD_SCALE`
restore first, then `IP-1020`'s `generate_world` regenerates `REGION_GRAPH` from them (never
itself persisted — ADR-0009's determinism guarantee), then `KEYITEM_FLAGS` restores onto the
freshly-regenerated graph via the same `memcpy` subroutine, reversed. A version-1 (`IP-1010`-era)
or absent save is excluded from `IP-1040`'s MAIN MENU "continue" option entirely — `try_load_save`
never runs against one — a stricter response than `IP-1010`'s own "default to safe empty state"
choice, since here the world *model* differs, not just one field (ADR-0010).

Total addition: ~84 bytes — against 8 KiB SRAM, negligible (R106's extension). **The generated
world's region graph/biome content is *not* persisted** — only `SEED`+`WORLD_SCALE`+
`KEYITEM_FLAGS` are saved; `REGION_GRAPH` regenerates deterministically from `SEED`+`WORLD_SCALE`
on load, per ADR-0009's determinism requirement. Per **ADR-0010**'s decision, a save whose version
byte does not match this new value is not offered on the main menu's "continue" path (the world
*model* differs, not just a field — the same reasoning ADR-0010 already recorded).

### 7a. `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` relocation — `IP-9070` (confirmed 2026-07-11)

Playtesting (`BL-0058`) found `SCOREITEM_FLAGS` had never been widened past its original
`IP-1010` 9-byte/9-zone array, despite `IP-1020` generalizing `CUR_ZONE` to the full generated
world (up to 81 regions): `setup_zone_collects` was writing collection state through
`CUR_ZONE`-as-byte-offset into only 9 bytes, silently corrupting adjacent WRAM once a real,
scale≥4 world made `CUR_ZONE > 8` reachable. `IP-9070` fixes this a level below `IP-9050`
(`BL-0047`'s own navigation fix, which is what actually makes `CUR_ZONE > 8` reachable at
runtime) — the two are sequenced so the storage is safe before the value range that exercises it
expands.

- `SCOREITEM_FLAGS` (WRAM): widened 9→81 bytes, **relocated** `0xC060`→`0xC286` (growing in place
  at `0xC060` would have collided with `REGION_GRAPH` at `0xC070`; `0xC286` is the
  confirmed-unused gap between `SSE_CURSOR` (ends `0xC285`, `IP-1040`) and `OAM_BUF` (`0xC300`)).
- `SRAM_SCOREITEM` (SRAM): widened 9→81 bytes, **relocated** `0xA013`→`0xA070` (immediately after
  `SRAM_KEYITEM_FLAGS`'s own end, leaving `SRAM_SEED`/`SRAM_WORLD_SCALE`/`SRAM_KEYITEM_FLAGS`'s
  existing addresses untouched).
- `SAVE_VERSION_VAL` bumped `0x02`→`0x03` (third bump in the same version-guard chain `IP-1010`
  started); a version-2 or earlier save is excluded from "continue," the same pattern `IP-1040`/
  `IP-1050` already established twice.
- `setup_zone_collects` now reads `REGION_GRAPH[CUR_ZONE]`'s biome-id first and indexes
  `zc_table` by biome-id, not `CUR_ZONE` directly (`BL-0059` fix) — `ZONE_COLLECTS` (GDS-08) was
  reduced from 9 zone-named lists to 5 biome-family-representative lists to match.
- Net SRAM growth: +72 bytes (9→81 at `SRAM_SCOREITEM`), trivial against the ~10 KiB headroom
  margin already confirmed by `IP-1050`.

### 7b. Maze-generation pass WRAM additions — `IP-1070` (confirmed 2026-07-11)

`ADR-0012`'s maze-shaped region adjacency (`FS-107`, `FR-9140`/`FR-9150`) adds a second,
orthogonal generation pass after `generate_world`'s existing biome-assignment loop, carving a
randomized spanning tree over `REGION_GRAPH`'s already-written neighbor bytes (pruning full-lattice
edges to `0xFF`) and then braiding a fraction of the pruned edges back open. `REGION_GRAPH`'s own
5-bytes/region format (§6) is **unchanged** — this pass only rewrites some of its existing neighbor
bytes, never its shape. All-new transient scratch, same framing as `GW_TOP_ROW`/`GW_B_SCRATCH`
above — meaningless outside a `generate_world` call, falls inside the existing boot-time WRAM
clear:

| Address | Name | Content |
|---|---|---|
| `C3A0`–`C3F0` | `GW_MAZE_STATE` | up to 81 bytes, one per region — bit 7: visited (carve phase); bits 1:0: parent-direction (0=up/1=down/2=left/3=right), the edge this region was first carved from, used both to backtrack during carving and as one half of the braid pass's tree-edge test. |
| `C3F1` | `GW_CUR_REGION` | 1 byte — the carve phase's current-region pointer (the iterative recursive-backtracker's only "stack," per `ADR-0012`'s decision not to allocate a separate stack array). |
| `C3F2` | `GW_MAZE_DIR` | 1 byte — carve phase: the current region's rotated try-direction. Repurposed after carving completes as the braid phase's canonical-edge direction (down/right only, so each undirected edge is decided exactly once). |
| `C3F3` | `GW_BRAID_IDX` | 1 byte — carve phase: try-count within the current region's 4-direction rotation. Repurposed after carving completes as the braid phase's region-loop counter. |
| `C3F4` | `GW_MAZE_DRAW_CTR` | 1 byte — `ADR-0013`'s loop-local, never-persisted PRNG-decorrelation counter (XORed into each `gw_prng_step` draw this pass makes, stepped by +97 per draw, zeroed at maze-pass start). Exists solely to decorrelate this pass's own repeated back-to-back draws from `gw_prng_step`'s shipped mixing-step defect ([R113](../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md)); never written back into `gw_prng_step`'s own carried `TMP1`/`TMP2` state, so every other caller (the biome-assignment loop) is completely unaffected. |

Net new WRAM: 85 bytes (`81+1+1+1+1`), entirely inside the `0xC3A0`–`0xC3F4` range — comfortably
inside the confirmed bank-0 headroom (R111) and the existing `0xC000`–`0xC2FF`... boot-clear
range's neighbor (this pass's own scratch is re-derived fresh every `generate_world` call, so it
does not need to be zeroed by the boot-time clear the way persisted fields do — `maze_init`
explicitly zeroes `GW_MAZE_STATE`/`GW_MAZE_DRAW_CTR` and marks region 0 visited itself, at the
start of every call). Two new subroutines, `gw_neighbor_hl` (region+direction → `REGION_GRAPH`
neighbor-byte address) and `gw_maze_state_hl` (region → `GW_MAZE_STATE` byte address), reached
only via `CALL`, placed immediately before `save_to_sram`'s label.

### 8. Tile index map implication (cross-reference only — GDS-08 decides the actual strategy)

**ADR-0009**'s biome-family `Region` identity (GDS-04's delta) needs tile budget per family,
generalizing today's per-zone terrain blocks (§4 above: `0x70`–`0xB5`, 6–8 tiles/zone,
8-tile-aligned). **This document does not decide how many biome families exist or how their tile
budgets are assigned** — that is [GDS-08](08-presentation-architecture.md)'s delta (the
normative aesthetic standard for C8, biome-transition presentation for C9), which this level's
own existing Purpose statement already reserves ("presentation architecture... builds on this
one"). Noted here only as a forward pointer, not resolved.

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
code. **As of `IP-9030` (2026-07-09), both `Claude.md` and `memory.md` now carry short pointers
here instead of duplicated tables** — the merge this decision anticipated has landed.

**Delta record (2026-07-09):** §§6–8 ("Data Model delta") added above, per the adopted increment
plan's Phase 3 and ADR-0009/0010. Delta, not re-authoring — §§1–5's tables remain the accurate
as-shipped layout; no merge-gate box above is reopened.
