# IP-1081 — Maze-Blocked Edge Indicator (content)

> Owned by `07-implementation-planning` (definition) / `08-content-authoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1081` — implements the content half of
[**FS-108**](../../features/FS-108-maze-aware-transition-edge-signaling.md) (`FEAT-2100`, Epic
`EP-1000`, Release 2 post-ship addendum) — the rendering half's tile art. Render half (the branch
that actually draws these tiles): **IP-1082** (paired package, same FS; that package depends on
this one). This is the second package `FEAT-6100`'s standard
([FS-106](../../features/FS-106-aesthetic-biome-transition-compliance.md)) applies to, via a
future `09-content-review` pass once `IP-1082` ships (new visible art, unlike `IP-1080`'s
logic-only pass).

## 2. Objective

Author and register 4 new small icon tiles — the blocked-edge indicator, one per direction — at
the tile-index slots and palette assignment [GDS-08 §10](../../architecture/08-presentation-architecture.md)
already decided: a short broken/dashed bar, silhouette-distinct from the existing solid-triangle
open-arrow, reusing palette 2 (UI/gold) verbatim. This package supplies the art only; `IP-1082`
wires it into `draw_region_arrows`'s render decision.

## 3. Requirements Covered

FR-2330 — the rendered-*appearance* half of this requirement's Description ("a blocked-edge
indicator... render[s]"), specifically the tile-art component. The render-time *decision* of when
to draw this art is `IP-1082`'s own scope, not this package's.

## 4. Architecture Components

[GDS-08 §10](../../architecture/08-presentation-architecture.md) (the binding decision this
package implements verbatim: 4 new tiles, `0x1A`–`0x1D`, palette 2 reused, 0 new BG palette
entries) · [GDS-07 §4](../../architecture/07-data-model.md) (the existing "clean, 8-tile-aligned
UI-icon block" convention this addition continues, `0x10`–`0x19` already occupied by
`TL_BG_BLANK`…`TL_ARROW_D`).

## 5. Interfaces

- **`build_tile_data()`'s existing `put()` patch-point convention** (`tiles.py`, GDS-09) — the 4
  new tiles register through the exact mechanism `TL_ARROW_R/L/U/D` already use
  (`tiles.py:916-919`), no new patch-point kind.
- **No new WRAM/SRAM interface** — pure ROM-resident tile pattern data.

## 6. Files to Create/Modify

- **Modify: `tiles.py`**:
  - Add 4 new tile-index constants immediately after the existing UI-icon block
    (`tiles.py:29-39`, currently ending at `TL_ARROW_D = 0x19`): `TL_BLOCKED_U = 0x1A`,
    `TL_BLOCKED_D = 0x1B`, `TL_BLOCKED_L = 0x1C`, `TL_BLOCKED_R = 0x1D` — matching
    `TL_ARROW_*`'s own per-direction-tile naming/ordering convention (up/down/left/right), not a
    single rotated tile (GDS-08 §10 explicitly rejected that shape).
  - Add 4 new pixel-art functions (mirroring `arrow_up()`/`arrow_down()`/`arrow_left()`/
    `arrow_right()`'s own existing shape/signature at `tiles.py` near line 916 — an 8×8 2bpp
    bitmap function returning the tile's pixel data), each drawing a short broken/dashed
    horizontal or vertical bar (two short filled segments with a visible gap between them) —
    oriented per direction the same way the arrow tiles are (a directional glyph, not a
    direction-agnostic icon). The exact pixel layout is this package's own craft decision, judged
    against [GDS-08 §7](../../architecture/08-presentation-architecture.md)'s tile-craft
    checklist ("silhouette-first: recognizable as a solid shape before color is assigned," R209)
    by the follow-on `09-content-review` pass — not dictated by this package document, consistent
    with how every other tile-bearing package in this tree (e.g. `IP-1031`) leaves exact pixel
    choices to the implementing pass.
  - Register all 4 new tiles in `build_tile_data()` via `put(TL_BLOCKED_U, blocked_up())` etc.,
    immediately after the existing `put(TL_ARROW_D, arrow_down())` call (`tiles.py:919`) —
    continuing the same block, not a new one.

- **No modification to `build_rom.py`'s `BG_PALETTES`/`OBJ_PALETTES` tables** — GDS-08 §10's own
  decision is 0 new palette entries (palette 2 reused verbatim by `IP-1082`'s own render branch,
  not by this content package, which authors pixel patterns only).

## 7. Implementation Tasks

Ordered: (1) confirm `0x1A`–`0x1D` remain free in the current tree (direct `tiles.py` re-read,
since this package plans against the tree as of 2026-07-12 — a stale assumption here is a hard
Blocking condition per this skill's own rule); (2) design the 4 pixel bitmaps against GDS-08
§10's silhouette concept; (3) add the 4 tile-index constants and pixel-art functions; (4) register
via `put()`; (5) rebuild ROM, confirm byte growth matches the ~64-byte estimate (§13); (6) full
suite run — no behavior change expected yet (nothing calls the new tiles until `IP-1082` ships),
so this package's own DoD is "tiles exist and are ROM-resident," not "tiles render in-game."

## 8. Tests to Add

None new in `test_rom.py` — this package adds inert tile data with no runtime code path
referencing it yet (`IP-1082`'s own scope). A direct build-time confirmation (§11) that the 4
tiles are registered at the correct indices is this package's own verification method — no
emulator-driven behavioral test is possible before `IP-1082` wires the render branch.

## 9. Documentation Updates

- [GDS-07 §4](../../architecture/07-data-model.md): tile-index table — `0x1A`–`0x1D` flip from
  "free" to occupied (`TL_BLOCKED_U/D/L/R`), confirming GDS-08 §10's own prospective allocation.
- `docs/features/FS-108-…md` metadata: implemented-by pointer (content half, `IP-1081`).
- Master Build Plan status row.

## 10. Definition of Done

- 4 new tile-index constants exist (`TL_BLOCKED_U/D/L/R`, `0x1A`–`0x1D`) and are registered in
  `build_tile_data()`.
- Each tile's pixel silhouette is distinct from the corresponding `TL_ARROW_*` tile (not a
  recolor) — confirmed by direct visual inspection of the built tile data, judged fully against
  GDS-08 §7's craft checklist by the follow-on `09-content-review` pass.
- Zero new BG/OBJ palette entries added to `build_rom.py` (confirmed by diff).
- ROM builds successfully with the 4 new tiles present; no existing test regresses (nothing yet
  calls the new tiles, so no new assertion is expected to pass or fail on their account).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes (unchanged count — this package adds no new checks).
- [ ] Direct diff: `tiles.py` gains exactly 4 new tile-index constants + 4 new pixel-art functions
      + 4 new `put()` calls, nothing else.
- [ ] Direct diff: `build_rom.py`'s `BG_PALETTES`/`OBJ_PALETTES` tables unchanged.
- [ ] `0x1A`–`0x1D` confirmed unused by any other tile before this package claims them.
- [ ] GDS-07 §4 / Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1080`** (`VERIFIED`) — not a build dependency (this package doesn't touch
  `draw_region_arrows`), but the classification logic this content exists to visualize must
  already exist for the pairing to make sense; cited for completeness.
- No other package's files overlap this one's own `Files to Create/Modify`.

## 13. Risks

Low — pure content addition, no control-flow change, no new palette entries, ROM growth
(~64 bytes: 4 tiles × 16 bytes/tile in 2bpp encoding) trivial against the confirmed ~10KB
headroom. The only real risk is a pixel-craft judgment call (does the silhouette actually read as
"interrupted path" at 8×8 scale) — explicitly deferred to `09-content-review`, not resolved by
this package's own Definition of Done, per `FS-106`'s own established review-process split.

## 14. Rollback Considerations

Revert `tiles.py`'s 4 new constants/functions/`put()` calls and rebuild. No save-format
dependency (pure ROM-resident tile data, never touches WRAM/SRAM); no other package's Files to
Modify overlap, so rollback is fully self-contained.
