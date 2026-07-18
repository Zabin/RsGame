# IP-1125 — Combat Sub-Mode: Mob & Projectile Sprite Content

> Owned by `07-implementation-planning` (definition) / `08-content-authoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1125` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers the *render* verb's content half — new
tile pixel art only, no runtime logic. Has no dependency on any other combat package; every other
package in this delta depends on it for the tile indices it reserves.

## 2. Objective

Author pixel art and register tile-index constants for one representative mob sprite and the
ranged projectile, both in 8×16 OBJ mode per `ADR-0007`, claiming the next unclaimed OBJ-range
tile-pair slots.

## 3. Requirements Covered

FR-11200 (mob presence — this package supplies the sprite it materializes as), FR-11300
(projectile — this package supplies the sprite it renders as). Neither FR names tile art directly
(implementation-independent, per `04`'s own discipline) — this package supplies the concrete
asset both require to be visible at all.

## 4. Architecture Components

[ADR-0007](../../architecture/adr/ADR-0007-8x16-obj-sprite-mode.md) (8×16 OBJ tile-pair
convention, governs both new sprites) · `ADS-002` §System Architecture ("Sprite budget," "Enemy
defeat presentation").

## 5. Interfaces

- **`build_tile_data()`'s existing `put(index, pixel_art)` registration contract** (`tiles.py`,
  `GDS-09`) — extended with two new calls, no change to the function's own signature or the
  `ROM` class surface.
- **`tiles.py`'s existing tile-index constant convention** (`TL_xxx = 0xNN`) — two new pairs
  added following the file's own comment-documented "OBJ tiles 0x00-0x09" range, which this
  package extends to 0x00-0x0D (still fully within the 8-bit OBJ tile-index space, no VRAM-bank
  concern).

## 6. Files to Create/Modify

- **Modify: `tiles.py`**:
  - New constants (next free OBJ-range slots after `TL_FLOWER_OBJ`'s own bottom half at `0x09`):
    `TL_MOB       = 0x0A` (mob top half), `TL_MOB_BOT   = 0x0B` (mob bottom half — reuses
    `TL_BLANK_OBJ`'s own blank pixel content, mirroring `TL_CARROT`/`TL_STAR`/`TL_FLOWER_OBJ`'s
    established "top has art, bottom is blank" precedent for a single-cell-tall sprite in 8×16
    mode), `TL_PROJECTILE = 0x0C` (projectile top half), `TL_PROJECTILE_BOT = 0x0D` (blank).
  - New pixel-art functions `mob_obj()`/`mob_obj_bot()`/`projectile_obj()`/`projectile_obj_bot()`
    (mirroring `flower_obj()`'s own function shape) — a simple, readable silhouette per `R218`'s
    own "poof"-convention framing (no gore, no graphic detail): a small creature silhouette for
    the mob (single palette, distinct from the player's own `OBJ pal 0`), a simple projectile
    shape (e.g. a small orb/dart) for the projectile.
  - `build_tile_data()`: four new `put()` calls registering the constants above at their claimed
    indices.
  - `boot`/tile-copy DMA count (`asm_game.py`, mirrors `IP-9150`'s own shared
    `TILE_DATA_TILES` constant/assertion) — confirm the highest used tile index (`0x0D` from this
    package, still well below the existing ceiling `TL_TORCH = 0xB5`) does not change the
    build-time assertion's own bound.

## 7. Implementation Tasks

Ordered: (1) draft mob silhouette pixel art; (2) draft projectile pixel art; (3) register both
top halves + their blank bottoms via `put()`; (4) rebuild ROM; (5) direct visual confirmation
(force-render both new tiles to a test screen via PyBoy, screenshot); (6) full suite run
(no behavior change expected — pure data addition); (7) documentation updates (§9).

## 8. Tests to Add

New checks in an existing or new content-audit suite (mirrors `IP-1031`'s own zero-new-palette
audit pattern):

- A new tile-count/index check confirming `TL_MOB`/`TL_MOB_BOT`/`TL_PROJECTILE`/
  `TL_PROJECTILE_BOT` exist at `0x0A`–`0x0D` and are registered in `build_tile_data()`'s output.
- A palette-budget check confirming no new palette *slot* is claimed beyond what the mob/
  projectile's own OBJ palette assignment needs (exact palette re-use vs. a new one is this
  package's own §7 drafting choice, confirmed against the built ROM here, not assumed).
- Direct visual confirmation (PyBoy screenshot, force-rendered) that both sprites are visually
  distinct from every existing OBJ tile (player, carrot, star, flower) and from each other.

## 9. Documentation Updates

- `docs/architecture/07-data-model.md` (or the tile-index quick-reference, if the project keeps
  one separate from `tiles.py` itself): new tile-index rows for `0x0A`–`0x0D`.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: implemented-by pointer for the
  content half of the *render* verb.
- Master Build Plan status row.

## 10. Definition of Done

- Four new tiles registered, visually confirmed distinct, ROM builds at exactly 32768 bytes with
  the full suite passing, no palette budget regression.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] `TL_MOB`/`TL_MOB_BOT`/`TL_PROJECTILE`/`TL_PROJECTILE_BOT` all present in `build_tile_data()`'s
      output at `0x0A`–`0x0D`.
- [ ] Screenshot confirms both new sprites render and are visually distinct from every existing
      OBJ tile and from each other.
- [ ] No new palette slot claimed beyond what this package's own drafting needs — confirmed
      against the built ROM.

## 12. Dependencies

None — this package claims new, previously-unused tile indices only; it does not read or modify
any existing tile, screen, or code path.

## 13. Risks

- **ROM budget** (Low): four 16-byte tiles = 64 bytes, negligible against the 1,378-byte headroom
  (`R115`/`NFR-4500`).
- **Content-review risk** (Low-Medium): a `09-content-review` pass is owed once this ships,
  mirroring the standing pattern this project already applies to every new tile-art package
  (e.g. `BL-0097`'s own finding for `IP-1081`) — silhouette distinctiveness is judged there, not
  asserted final here.

## 14. Rollback Considerations

Revert `tiles.py`/`asm_game.py` (tile-copy-count assertion only) and rebuild. No existing tile
index is touched or reassigned — purely additive, zero blast radius on any shipped screen/sprite.
