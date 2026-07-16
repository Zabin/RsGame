# GDS-07 — Data Model

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment — see "Data Model delta" below; delta 2026-07-12 — §7c, per-region treasure-presence
> concept, `ADR-0015`; delta 2026-07-14 — §7d, Infinite Mode per-region materialization WRAM
> confirmed by `IP-1101`, `C40D`–`C418`; delta 2026-07-14 (cont'd) — §7e, Infinite Mode streaming
> window/navigation/render WRAM confirmed by `IP-1102`, `C3F6`–`C404`; delta 2026-07-16 — §7f,
> Infinite Mode treasure/win-condition WRAM confirmed by `IP-1103`, `C405`–`C40C`, the joint
> reserve now fully claimed).** Owned by
> `03-architecture-design-synthesis`.
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
| `C27D` | `MM_SAVE_VALID` | 1 byte — MAIN MENU's own cached save-validity probe (magic+version), computed once per entry by `mm_on_entry`/`check_save_valid`, gates whether "continue" is offered/toggle-reachable ([IP-1040](../implementation/packages/IP-1040-main-menu-new-game-flow.md)). Backfilled into this table by [IP-1090](../implementation/packages/IP-1090-select-menu-edge-indicator-legend-screen.md) — referenced by `IP-1040`/`IP-9060` since 2026-07-11 but never previously entered here. |
| `C27E` | `MM_CURSOR` | 1 byte — MAIN MENU's highlighted option: 0=continue, 1=new game ([IP-1040](../implementation/packages/IP-1040-main-menu-new-game-flow.md)/[IP-9060](../implementation/packages/IP-9060-main-menu-cursor-fix.md)). **Reused, not newly allocated, by [IP-1090](../implementation/packages/IP-1090-select-menu-edge-indicator-legend-screen.md)** as SELECT MENU's own highlighted option (0=map, 1=legend) — valid since `GS_MAIN_MENU` and `GS_SELECT_MENU` are never simultaneously active and no transition connects them directly. Backfilled into this table by `IP-1090`. |
| `C286`–`C2D6` | `SCOREITEM_FLAGS` | **up to 81 bytes**, one bitfield per region, bit *N* = the *N*th `ZONE_COLLECTS`-family-list entry ([FR-5220](../requirements/01-functional-requirements.md); originally 9 bytes at `C060`–`C068` per [IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md), 2026-07-07; relocated and widened to 81 bytes by [IP-9070](../implementation/packages/IP-9070-cur-zone-indexed-structures-generalization.md), 2026-07-11, to the confirmed-unused gap between `SSE_CURSOR` (ends `C285`) and `OAM_BUF` — growing in place at `C060` would have collided with `REGION_GRAPH` at `C070`). `setup_zone_collects` now indexes `zc_table` by `REGION_GRAPH`'s biome-id rather than `CUR_ZONE` directly ([BL-0059](../../pipeline/backlog.md) fix). |
| `C2D7` | `MM_JUST_ENTERED` | 1 byte — set by every `GAMESTATE` → `GS_MAIN_MENU` transition site, cleared by `mm_on_entry` once consumed ([IP-9060](../implementation/packages/IP-9060-main-menu-cursor-fix.md), `BL-0048`). **Reused by every `GAMESTATE` → `GS_SELECT_MENU` transition site as well** ([IP-1090](../implementation/packages/IP-1090-select-menu-edge-indicator-legend-screen.md)) — valid for the same reason `MM_CURSOR`'s reuse is (the two states never overlap), cleared by `sm_on_entry` on that side. |
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

### 4. Tile index map (`0x00`–`0xFF`, 87 of 256 slots used)

Confirmed directly against `tiles.py`'s 87 `TL_*` constants (updated by
[IP-1081](../implementation/packages/IP-1081-maze-blocked-edge-indicator-content.md), 2026-07-12
— 4 new tiles, `0x1A`–`0x1D`):

| Range | Content |
|---|---|
| `0x00`–`0x09` | OBJ sprites: bunny frames (8×16 pairs `00/01`, `02/03`), carrot (`04`+blank `05`), star (`06`+blank `07`), flower (`08`+blank `09`) |
| `0x10`–`0x19` | UI icons: BG blank, heart full/empty, carrot icon, star icon, border, 4 direction arrows |
| `0x1A`–`0x1D` | **Maze-blocked edge indicator** (`IP-1081`/`FS-108`) — 4 directional broken/dashed-bar tiles, palette 2 reused, drawn by `IP-1082`'s render branch wherever `draw_region_arrows` classifies an edge `blocked` |
| `0x1E`–`0x1F` | Free — 2 slots unused (next free slot in this block) |
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

### 7c. Per-region treasure-presence concept — `ADR-0015` (implemented 2026-07-13, `IP-1021`)

**Confirming note (2026-07-13):** the shipped encoding is the first candidate below — `KEYITEM_FLAGS`'s
value domain widened in place to `{0, 1, 2}`. The re-audit this section flagged as needed
(`setup_zone_collects`'s nonzero-means-inactive check) was performed directly against the code:
both real consumers (`setup_zone_collects`, `check_collisions`) already treat any nonzero value as
"no active item here," which is exactly correct for the new `2` ("absent") value too — no
downstream changes were needed. No new WRAM address was added; `SRAM_KEYITEM_FLAGS`'s existing
81-byte mirror is unaffected (value-agnostic memcpy). The remainder of this section is left as the
original decision record.

`ADR-0015` (`BL-0093`) makes `KeyItem` placement selective — `WorldScale` total, zero-or-one per
`Region`, decided at generation time from the pre-braid spanning-tree's leaf structure (§7b's
`GW_MAZE_STATE`, read before `maze_prune` runs) with a random-fill fallback. **This needs a new
data-model concept `KEYITEM_FLAGS` cannot currently represent**: today `KEYITEM_FLAGS` (§2, up to
81 bytes) is a 2-valued bitmap per region — `0` = has a `KeyItem`, not yet collected; `1` =
collected. There is no value meaning "this region was never assigned a `KeyItem`," because under
the shipped (and 2026-07-09 target) model every region always has one.

**This level names the concept, not the byte encoding** (this pass's own scope boundary; the
choice below is a real, open implementation decision for `07-implementation-planning`/
`08-code-implementation` to make against the real code, not dictated here):

- A per-region **tri-state** is needed: *no `KeyItem`* / *`KeyItem` present, uncollected* /
  *`KeyItem` present, collected*. Two representationally distinct shapes are both plausible
  against the existing byte-per-region convention this codebase already uses throughout
  (`KEYITEM_FLAGS`, `SCOREITEM_FLAGS`, `GW_MAZE_STATE`):
  - **Widen `KEYITEM_FLAGS`'s own value domain** from `{0, 1}` to `{0, 1, 2}` (e.g. `0`=present/
    uncollected, `1`=present/collected, `2`=absent) — no new WRAM/SRAM address, but every reader
    of `KEYITEM_FLAGS` that currently treats "nonzero" as "collected" (`setup_zone_collects`'s
    inactive-marking check, per its own comment at `asm_game.py:1194-1196`) needs re-auditing,
    since a value of `2` would also read as "nonzero" — whether that's the *correct* behavior
    (suppressing render for an absent item, same visible effect as an already-collected one) or a
    latent bug needs direct confirmation against the real pickup/render code paths at
    implementation time, not assumed here.
  - **A new, separate per-region presence bitmap** (up to 81 bytes, mirroring `KEYITEM_FLAGS`'s
    own sizing convention) — costs new WRAM (comfortably inside the confirmed headroom, per §7b's
    own precedent of adding 85 bytes for the maze pass alone) but keeps "has an item" and "has
    been collected" as cleanly separable concerns, avoiding the widened-value-domain's re-audit
    risk above.
- **SRAM/save-format impact:** whichever encoding is chosen, the presence decision (unlike
  collected-state) is **generation-derived, not save-worthy on its own** — it must be
  recomputed identically every time `REGION_GRAPH` regenerates from `(SEED, WORLD_SCALE)` on load
  (`ADR-0009`'s existing determinism guarantee, extended here), the same "regenerate, don't
  persist" precedent `REGION_GRAPH` itself already sets (`ADR-0012` point 6). Only the *collected*
  half of whichever encoding is chosen needs its own save-format field, following `KEYITEM_FLAGS`'
  existing `SRAM_KEYITEM_FLAGS` precedent (§7 above) exactly.
- **Victory-check impact:** `check_complete`'s comparison target changes from the literal `9` to
  a read of `WORLD_SCALE` (§2's existing WRAM address, no new field needed) — a one-operand change
  at the implementation level, named here only because it is this delta's own direct consequence.

### 7d. Infinite Mode: per-region materialization WRAM — `IP-1101` (confirmed 2026-07-14)

`FS-110` §10 noted "no `GDS-04`/`07`/`09` delta has been authored for Infinite Mode" — `IP-1101`
is the first package to actually claim WRAM, so this is that delta's first real content, not a
target statement. Eight new bytes, `0xC40D`–`0xC418`, immediately past `GW_KI_PLACED` (`0xC3F5`)
and the range `0xC3F6`–`0xC40C` `IP-1100`/`1102`/`1103`'s own already-published planning documents
reserve (`GAME_MODE`/`INF_ROW`/`INF_COL`/`INF_WINDOW`/`INF_TREASURE_HERE`/
`RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE`) — that reserved range is claimed in code by `IP-1102`,
§7e below.

| Address | Name | Size | Purpose |
|---|---|---|---|
| `C40D`–`C40E` | `INF_MZ_ROW` | 2 bytes | `inf_materialize_region`'s own row input (signed 16-bit, low byte first, mirrors `SEED`'s own byte order) |
| `C40F`–`C410` | `INF_MZ_COL` | 2 bytes | column input, same convention |
| `C411` | `INF_MZ_RESULT` | 1 byte | output: packed biome (bits 0-2) + connectivity nibble (bits 3-6: up/down/left/right, 1=open) |
| `C412` | `INF_MZ_TREASURE` | 1 byte | output: 0 or 1, `hash(SEED,row,col) mod 16 == 0` (`K=16`) |
| `C413` | `INF_MZ_BIOME` | 1 byte | transient scratch: own biome value, held while the south/east neighbor consultations run |
| `C414` | `INF_MZ_BIAS` | 1 byte | transient scratch: own carve-bias (0=carve north, 1=carve west) |
| `C415`–`C416` | `INF_MZ_TROW` | 2 bytes | transient scratch: the row currently being hashed by `inf_region_seed0` |
| `C417`–`C418` | `INF_MZ_TCOL` | 2 bytes | transient scratch: the column currently being hashed by `inf_region_seed0` |

Trivial against the confirmed ~3.1 KiB bank-0 headroom (§6, `R111`). All eight bytes are
transient/call-scoped, meaningless outside an `inf_materialize_region` call, the same convention
the `GW_*` family already establishes for `generate_world`'s own scratch (§6). No SRAM impact —
this package persists nothing (per-region output is always re-derived, `NFR-2300`).

### 7e. Infinite Mode: streaming window / navigation / render WRAM — `IP-1102` (confirmed 2026-07-14)

Six bytes, `0xC3F6`–`0xC404`, immediately below `IP-1101`'s own `0xC40D` block (§7d) and inside
the same range `IP-1100`/`1102`/`1103`'s planning documents jointly reserved. `GAME_MODE` was
originally planned as `IP-1100`'s own addition, but `IP-1102` was implemented first and needs it
(`dsr_p`/`check_zone_transition` both gate on it) — claimed here instead; `IP-1100`'s own
implementation reuses this constant rather than redefining it (a same-address, implementation-
order-only deviation from the original plan, not a real conflict — both packages' own planning
documents already agreed on `0xC3F6`).

| Address | Name | Size | Purpose |
|---|---|---|---|
| `C3F6` | `GAME_MODE` | 1 byte | `0`=finite (default — boot-cleared explicitly, since it sits outside the `0xC000`–`0xC2FF` boot-clear range, §2), `1`=infinite |
| `C3F7`–`C3F8` | `INF_ROW` | 2 bytes | player's current region row (signed 16-bit, low byte first, mirrors `SEED`'s own byte order), Infinite Mode only |
| `C3F9`–`C3FA` | `INF_COL` | 2 bytes | player's current region col, same convention |
| `C3FB`–`C403` | `INF_WINDOW` | 9 bytes | 3×3 materialized window, row-major (index = `(dr+1)*3+(dc+1)`, `dr,dc` in `{-1,0,1}`); center cell (index 4, `C3FF`) = current region. 1 byte/region, `IP-1101`'s own output format (bits 0-2 biome-id, bits 3-6 connectivity: up/down/left/right, 1=open) |
| `C404` | `INF_TREASURE_HERE` | 1 byte | transient cache: current region's own treasure-presence-and-uncollected flag for this materialization — reserved here, populated by `IP-1103` |

Fifteen bytes total against `IP-1101`'s block (`0xC3F6`–`0xC418`), trivial against the confirmed
~3.1 KiB bank-0 headroom (§6, `R111`; `NFR-4300`, Met). `inf_ensure_window` (new subroutine)
recomputes all 9 `INF_WINDOW` cells fresh on every center change via `IP-1101`'s
`inf_materialize_region` — no incremental shift logic, no additional WRAM beyond the table above.
No SRAM impact in this package (`IP-1104`'s own scope).

### 7f. Infinite Mode: treasure & win-condition state WRAM — `IP-1103` (confirmed 2026-07-16)

Eight bytes, `0xC405`–`0xC40C` — exactly the remainder the joint `IP-1100`/`1102`/`1103` reserve
(§7e above) left for `IP-1103`; the `0xC3F6`–`0xC418` run is now fully claimed. Both fields sit
outside the `0xC000`–`0xC2FF` blanket boot clear and are explicitly boot-cleared (the same
targeted-clear pattern `GAME_MODE` established, §7e), so a fresh cartridge never presents
uninitialized bytes as standing high scores. `INF_TREASURE_HERE` (§7e) is now populated as its
row anticipated: written from `INF_MZ_TREASURE` at `inf_ensure_window`'s center-cell
materialization, cleared on collection, read by `setup_zone_collects`' infinite-mode spawn
branch.

| Address | Name | Size | Purpose |
|---|---|---|---|
| `C405`–`C406` | `RUNNING_TREASURE_COUNT` | 2 bytes | current run's treasure total, unsigned 16-bit, low byte first (`SEED`'s own byte-order convention); incremented by `check_collisions`' `GAME_MODE == 1` branch. When a *new* run resets it is `BL-0112`'s open question — deliberately undecided (`IP-1103` §13) |
| `C407`–`C40C` | `TOP_SCORE_TABLE` | 6 bytes | 3 entries × 2 bytes (unsigned 16-bit, low byte first), stored descending — index 0 (`C407`) is the current high score. Written only by `inf_check_top_score` (which has **zero call sites**, deliberately — `BL-0112`) and, in the future, `IP-1104`'s save/load restore |

Persistence of both fields is `IP-1104`'s scope (no SRAM impact in `IP-1103`).

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
