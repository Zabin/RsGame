# R203 — Screen Composition on a 20×18 Tile Grid

- **Document ID:** R203 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R102 (the hardware tile-map/screen size these compositions fill)
- **Referenced By:** R204 (HUD occupies row 0 of this same grid), R209 (tile-level composition)
- **Produces:** grounds `tilemaps.py`'s per-zone screen-composition functions
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R102, R204, R209

## Purpose

What makes a single-screen tile-based level read clearly at a glance, and how Bunny Quest's nine
zone-composition functions already do (or don't) follow that convention.

## Scope

The Game Boy's visible 20×18 tile viewport, landmark/focal-point placement, edges-as-exits
signaling, and readability under a fixed camera (no scrolling within a zone).

## Concepts

The GBC's visible screen is 160×144 pixels = a **20×18 tile grid** (the full BG tile map is
32×32, but only 20×18 of it is on-screen at once).[^1] General level-composition guidance:
meaningful landmarks and focal points that contrast with their surroundings anchor a screen's
readability, giving the player an immediate sense of "where am I, what matters here" without
relying on text.[^2] For a single fixed-camera screen (no scrolling), every one of the 360
visible tiles is doing composition work simultaneously — there is no "off-screen" to defer detail
to, unlike a scrolling level.

### Sources
[^1]: [Gameboy Graphics Overview — Larold's Retro Gameyard](https://laroldsretrogameyard.com/tutorials/gb/gameboy-graphics-overview/), accessed 2026-07-06.
[^2]: [Composition — The Level Design Book](https://book.leveldesignbook.com/process/blockout/massing/composition), accessed 2026-07-06.

## Operational Context

Every one of Bunny Quest's nine zone functions (`beach_screen()` through `castle_screen()`,
confirmed by direct `tilemaps.py` read) follows the same compositional pattern: row 0 reserved
for the HUD (R204), a base terrain fill across the remaining 17 rows using a seeded
pseudo-random variant-tile sprinkle (`_fill()`'s `seed = (y*k1 + x*k2 + k3) % k4` pattern, giving
organic-looking but fully deterministic ground texture), then 3–7 hand-placed **landmark
elements** per zone at fixed coordinates (palm trees for Beach, a pyramid + cacti for Desert,
houses + lanterns for Village, crystals + bats for Cave, etc.) — each zone's landmark set is
thematically distinct and visually non-overlapping with its neighbors, giving each of the nine
screens an immediately-recognizable identity. `_zone_arrows()` places directional arrow tiles at
the screen edges corresponding to valid zone-transition directions (right/left at row 9, up/down
at column 15) — a direct, minimal-text implementation of "edges as exits" signaling.

## Implementation Guidance

- **Preserve the row-0-reserved / landmark-set-per-screen pattern for any new zone** — it is
  already the established, working convention; a new zone should place 3–7 distinct landmark
  elements using the same seeded-fill-plus-hand-placed-features structure, not a fundamentally
  different composition approach.
- **The directional-arrow edge signaling must stay accurate as the world grows (C7).** Today's
  `_zone_arrows()` derives valid directions purely from the zone's row/col position in a *fixed*
  3×3 grid (`if col<2: right-arrow`, etc.) — a larger, non-rectangular, or larger-than-3×3 world
  topology would need this function generalized to look up actual neighbor existence per zone
  rather than assuming a full 3×3 rectangle; flag this as a concrete GDS-01/GDS-03 design question
  once world-scale growth is actually planned, not something to patch ad hoc.
- **Landmark placement should stay clear of the 10px collision-check zones (R202)** and the
  player's spawn point — this project's own past bug history (`Claude.md`'s "Gift collectible
  positions don't overlap player spawn" fix, pre-rewrite but the same class of defect) shows this
  is a real, recurring failure mode worth an explicit check whenever new collectible/landmark
  coordinates are added.
- **A new zone's terrain fill should reuse the existing seeded-pseudo-random pattern**, choosing
  new prime-ish multipliers for visual distinctness from existing zones, rather than inventing a
  different randomization approach per zone.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R102 (the hardware screen/tile-map size this composition fills) · R204 (the HUD's row-0
reservation, load-bearing for every zone's layout) · R209 (tile-level pixel-art composition
within each landmark element).
