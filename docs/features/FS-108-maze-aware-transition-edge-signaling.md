# FS-108 — Maze-Aware Transition-Edge Signaling

> Feature Specification for [FEAT-2100](../feature-planning/03-feature-catalog.md#feat-2100--maze-aware-transition-edge-signaling-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-2100, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Scope note (revised 2026-07-12):** this document originally specified FEAT-2100's **logic
> half only** (the render-time classification of each screen edge into one of three states),
> deliberately leaving the **rendering half** (the blocked-edge indicator's actual on-screen
> behavior) as a future spec-writing task once `GDS-08`'s tile-art delta landed. That delta closed
> 2026-07-11 ([08-presentation-architecture.md §10](../architecture/08-presentation-architecture.md)),
> and the logic half itself shipped and was independently `VERIFIED` 2026-07-12
> ([IP-1080](../implementation/packages/IP-1080-maze-aware-edge-classification.md)/
> [VR-1080](../implementation/verification/VR-1080-maze-aware-edge-classification.md)) — but
> `VR-1080`'s own audit confirmed AC-4 (the rendering criterion) still explicitly open, since
> `IP-1080` computed the classification arithmetic (`DRA_ROW`/`DRA_COL`) but did not wire any new
> rendering branch or draw the blocked-edge indicator (both "blocked" and "absent" remain
> identical no-ops in the shipped ROM). **This revision closes that gap**, specifying the
> rendering half's own workflow/behavior/Acceptance Criteria — the real, previously-missing
> spec-writing task this document's own prior forward pointers named. This is `BL-0075`'s tracked
> resolution path (a maze dead-end currently reads identically to a true world edge).

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md) · [ADR-0012](../architecture/adr/ADR-0012-maze-shaped-region-adjacency.md)

> **Forward reference (metadata only):** logic half implemented by
> [IP-1080](../implementation/packages/IP-1080-maze-aware-edge-classification.md) (2026-07-12,
> `VERIFIED`), which resolves this document's Open Question 2 (see §19). Open Question 1 (the
> rendering half's tile art) **resolved 2026-07-11** — see §19; `BL-0068` closed. **The rendering
> half's own workflow/behavior contract is specified by this revision** (§6 Workflow C, §15
> AC-4/5), planned 2026-07-12 as
> [IP-1081](../implementation/packages/IP-1081-maze-blocked-edge-indicator-content.md) (content)
> and
> [IP-1082](../implementation/packages/IP-1082-maze-blocked-edge-indicator-render.md) (render).
> Both authorized 2026-07-12 (user G3, `BL-0092`). `IP-1081` `COMPLETE` (2026-07-12, 231/231),
> awaiting verification; `IP-1082` `BLOCKED` on it. Tracked by `BL-0075`.

## 1. Feature ID

`FS-108` — expands `FEAT-2100` (Maze-Aware Transition-Edge Signaling), Epic `EP-1000` (Core Game
Loop & State Machine).

## 2. Title

Maze-Aware Transition-Edge Signaling

## 3. Purpose

Distinguish, at each screen edge, a maze-blocked-but-grid-adjacent edge from a true grid boundary
— both currently signal identically (no arrow) — so a maze-blocked edge reads as "there is a path
here I haven't opened" rather than as a dead end. Carried forward verbatim from FEAT-2100's own
Purpose/User Value (Medium-High — without this, `FEAT-9100`'s maze loses legibility).

## 4. Scope

**In scope (this document, revised):** (a) the render-time logic that, for each of a region's
four screen edges, determines which of three states applies — open, blocked, or absent (§6
Workflow A, unchanged from the prior revision, already implemented/`VERIFIED`); (b) **new in this
revision:** the rendering-half workflow — when the classification produces **blocked**, drawing a
distinct, non-blank indicator tile at that edge's existing screen position, visually
distinguishable from both the open-edge arrow and the absent case's blank, using the tile
shape/palette [GDS-08 §10](../architecture/08-presentation-architecture.md) already decided (4
new tiles at `0x1A`–`0x1D`, one per direction, palette 2 reused verbatim).

**Out of scope (this document):** the exact pixel bitmap/silhouette for the 4 new tiles — GDS-08
§10 deliberately specifies only the *concept* (a short broken/dashed bar, silhouette-distinct from
the solid arrowhead), leaving the literal bitmap to whichever `08-content-authoring` package draws
it, per this project's standing convention that pixel art is content-authoring's job, not a
feature spec's (mirrored by every other tile-bearing FS in this tree, e.g. `FS-103`). Also
excluded, per FEAT-2100's own catalog entry: the maze generation this Feature signals the output
of (`FEAT-9100`/`FS-107`); the open-edge case's existing rendering (`FEAT-2000`'s `FR-2320`, reused
verbatim, not reimplemented); any mid-screen collision/wall enforcement (out of scope for any
current Feature).

## 5. Requirements Implemented

FR-2330 — the exact requirement FEAT-2100 owns. **Both the classification behavior and the
rendered-appearance obligation are now specified by this document** (the requirement's full
Description/AC set, closing the partial-coverage note the prior revision carried).

## 6. User Workflows

**Workflow A — screen-edge classification during PLAYING** (extends `FEAT-2000`'s existing
render dispatch that draws `FR-2320`'s open-edge arrows, per `IP-1030`'s shipped
`draw_region_arrows` loop shape) — **unchanged from the prior revision, already implemented and
`VERIFIED`** (`IP-1080`/`VR-1080`):

1. Player is in a generated region during `PLAYING`, a maze-shaped world has been generated
   (`FEAT-9100` precondition, `FR-2330`).
2. For each of the region's four directions (up/down/left/right), the render routine reads
   `REGION_GRAPH`'s corresponding neighbor byte for the current region.
3. If the neighbor byte is a live region index (not `0xFF`), the edge is classified **open** —
   `FR-2320`'s existing arrow-rendering logic fires unchanged.
4. If the neighbor byte is `0xFF`, the routine independently computes whether a grid-adjacent
   region exists in that direction from the current region's `(row, col)` (`DRA_ROW`/`DRA_COL`,
   already re-derived once per call, shared by all four direction tests) and the world's
   `WORLD_SCALE` — the same arithmetic a grid boundary is defined by: up is grid-adjacent iff
   `row > 0`; down iff `row < WORLD_SCALE-1`; left iff `col > 0`; right iff `col < WORLD_SCALE-1`
   (a square `WORLD_SCALE`×`WORLD_SCALE` grid, `ADR-0010`).
5. If that arithmetic confirms a grid-adjacent region exists, the edge is classified **blocked**.
6. If the arithmetic confirms no grid-adjacent region exists, the edge is classified **absent**.

**Workflow B — before `FEAT-9100` ships or for a non-maze edge:** unaffected — this Feature's
classification logic only produces a different outcome than the pre-`FEAT-9100` 2-state behavior
for edges where `REGION_GRAPH` shows `0xFF` but a grid neighbor genuinely exists, which cannot
occur before `FEAT-9100`'s maze pass ships. No regression to the open/absent cases either way.

**Workflow C — blocked-edge rendering during PLAYING (new in this revision):**

1. Continuing from Workflow A step 5 (edge classified **blocked**): the render routine draws the
   direction's own new indicator tile (`TL_BLOCKED_U`/`D`/`L`/`R`, `0x1A`–`0x1D` per
   `GDS-08` §10) at that direction's existing screen position — the same `ARROW_ADDR_U`/`D`/`L`/`R`
   constant the open-edge case already writes to (`IP-1030`'s established convention: only one of
   the three states is ever drawn per edge, so no new screen position is needed), with the same
   palette-2 (UI/gold) attribute byte the open arrow already uses (`GDS-08` §10: zero new BG
   palette entries spent).
2. Continuing from Workflow A step 6 (edge classified **absent**): no indicator renders — unchanged
   from today's shipped behavior, and unchanged from the open case's own existing "no write when
   there's nothing to show" convention.
3. The blocked-edge indicator is visually distinguishable from the open-edge arrow (a different
   tile index, hence a different silhouette per `GDS-08` §10's decision — not a recolor) and from
   the absent case (a non-blank tile drawn vs. nothing drawn) — satisfying `FR-2330`'s own
   Rationale ("a maze-blocked edge must not look identical to a true dead end").

## 7. System Behaviour

**Normal path:** for any generated region and any of its four directions, the classification
routine produces exactly one of the three states (Workflow A), and the render routine draws
exactly the visual state matching it (Workflow C) — an open arrow, a blocked-edge indicator, or
nothing.

**Edge case — a region at a true grid corner (e.g. `row=0, col=0`):** two of its four directions
(up, left) are classified absent unconditionally, regardless of `REGION_GRAPH` content — no
indicator renders for either, matching today's shipped boundary behavior exactly.

**Edge case — `WORLD_SCALE` at its minimum (2) vs. maximum (9):** the classification and rendering
arithmetic is scale-parameterized identically to the existing `WORLD_SCALE`-driven division
(`IP-1080`'s own `dra_div_loop`) — no new scale-dependent behavior beyond what that already-shipped
logic establishes.

**Edge case — every edge of a region is blocked (a maze dead end with a zero-fraction braid
draw):** all four directions render the blocked-edge indicator, no open arrow anywhere on screen —
a valid, fully-specified state under this Workflow (the region remains reachable via the edge it
was *entered* through, which is by definition open from the adjacent region's own perspective;
this Feature does not need to guarantee at least one open edge is ever visible).

**Edge case — re-entering the same region after a save/reload:** the classification and rendering
are both computed fresh at render time from `REGION_GRAPH` (itself regenerated from
`SEED`/`WORLD_SCALE` on load, `FS-105`) — no persisted state to go stale; identical output to a
fresh visit at the same region.

## 8. Module Responsibilities

Per GDS-03's module decomposition:

- **`asm_game.py`** — `draw_region_arrows`'s own extension: the existing `0xFF`-branch (Workflow A,
  already implemented) additionally distinguishes blocked from absent via the `row`/`col`
  comparisons in Workflow A step 4, and — **new in this revision** — a blocked-case call to the
  existing `_arrow_write`-shaped write helper, targeting the same `ARROW_ADDR_*` constant with the
  new tile index instead of the open-arrow tile. The existing open-edge branch (`FR-2320`) is
  unchanged.
- **`tiles.py`** — **new in this revision:** four new tile-index constants (`TL_BLOCKED_U`/`D`/`L`/
  `R`) at `0x1A`–`0x1D`, registered via `build_tile_data()`'s existing `put()` convention
  (`tiles.py:916-919`'s own pattern for `TL_ARROW_R/L/U/D`), each backed by a new pixel-art
  function. The pixel bitmap itself is out of this document's scope (§4) — `08-content-authoring`
  designs it against `GDS-08 §10`'s silhouette concept (a short broken/dashed bar).
- **`tilemaps.py`** — **not affected.** The blocked-edge indicator is drawn at render time by
  `draw_region_arrows` (an `asm_game.py` routine, same as the open-arrow case), not baked into any
  screen's static tilemap layout.

## 9. Interfaces Used

- **`REGION_GRAPH`'s existing confirmed layout** (GDS-07 §2/§6, unchanged by `ADR-0012` point 2)
  — read-only, same neighbor-byte access `draw_region_arrows` already performs.
- **`DRA_ROW`/`DRA_COL`** (GDS-07 §2, `IP-1080`) — the transient re-derived `(row, col)` position,
  read (not written) by this revision's blocked/absent comparisons.
- **`draw_region_arrows`'s existing loop shape** (`IP-1030`/`IP-1080`, GDS-09's confirmed delta) —
  extended in place with a new write path inside the existing per-direction branches, not a new
  routine or a new call site.
- **`ARROW_ADDR_U`/`D`/`L`/`R`** (`asm_game.py`, `IP-1030`/`IP-9140`) — reused verbatim as the
  blocked indicator's own screen position, per `GDS-08` §10's own decision that no new screen
  position is needed (only one of the three states is ever drawn per edge).
- **`build_tile_data()`'s `put()` patch-point convention** (`tiles.py`, GDS-09) — the mechanism the
  4 new tiles register through; no new patch-point *kind* is introduced, only 4 new entries under
  the existing convention.
- **No new `patches` dict key.** The classification/rendering logic itself is pure WRAM-read/
  arithmetic plus a VRAM tile-index write, using the exact same write mechanism (`VBK`-bank
  toggling around a tilemap + attribute-map write) `_arrow_write` already performs for the open
  case.

## 10. Data Model Changes

- **No change to `REGION_GRAPH` or `DRA_ROW`/`DRA_COL`** — both already exist, read-only in this
  revision's own new logic.
- **New ROM-resident tile data:** 4 new tile bitmaps (`0x1A`–`0x1D`), per `GDS-08` §10's already-
  decided tile-index placement and palette assignment (palette 2, 0 new BG palette entries). This
  is new *content* (pixel data), not a new WRAM/SRAM entity — no GDS-07 WRAM/SRAM table delta is
  needed, only GDS-07's tile-index table gaining 4 populated rows where `0x1A`–`0x1D` are
  currently listed free (already recorded prospectively by `GDS-08` §10's own edit).
- **No new persistent WRAM or SRAM entity.**

## 11. State Changes

None. This Feature adds no new `GameState` value and no new persistent state; it changes only
what `draw_region_arrows` computes and draws during the existing `PLAYING`-state render path.

## 12. Error Handling

- **A direction's grid-adjacency arithmetic disagreeing with `REGION_GRAPH`'s own neighbor byte in
  a way that implies an open edge with no grid-adjacent region:** cannot occur under `FR-9140`'s
  own postcondition (every edge in the generated graph also exists in the full grid graph,
  `FS-107` §15 AC-1) — the open case is only ever reached when `REGION_GRAPH` already shows a live
  neighbor, which by that guarantee is always grid-adjacent. No defensive check needed.
- **Drawing the blocked-edge indicator when VRAM/OAM budget is otherwise exhausted:** cannot occur
  — the indicator reuses the exact same 1-tile background-map write the open arrow already
  performs at the same fixed position; no new VRAM tile-map cost per draw, only new ROM-resident
  tile *pattern* data (§10), unrelated to the per-frame write budget.

## 13. Performance Considerations

- **NFR-1300/NFR-1100** (screen-transition smoothness, VBlank-gated PPU access): the blocked-case
  write reuses the exact same write helper shape the open-arrow case already uses inside
  `do_screen_redraw`'s existing LCD-off bracket — no new timing concern, no new safe-window
  convention needed.
- **ROM budget:** 4 new tile bitmaps at `0x1A`–`0x1D` (16 bytes each in 2bpp encoding, 64 bytes
  total) — well within GDS-08 §10's own confirmed free-slot budget (74 free tile-index slots
  before this addition); no measurable impact on the ~10KB headroom this project has tracked
  throughout.

## 14. Integrity Considerations

None beyond what `FEAT-9100`/`FS-107` already guarantees as this Feature's own precondition
(`REGION_GRAPH`'s determinism and subgraph-of-full-lattice property, consumed read-only here).
This Feature introduces no new determinism or save-integrity concern of its own.

## 15. Acceptance Criteria

1. For any generated world in a test corpus, at every region and every direction: if
   `REGION_GRAPH` shows a live neighbor, the open-edge arrow renders (FR-2330 AC-a). **Already
   verified** (`T20.a`).
2. For any generated world in a test corpus, at every region and every direction: if no
   `REGION_GRAPH` neighbor exists but grid arithmetic confirms a grid-adjacent region exists in
   that direction, the classification arithmetic correctly identifies **blocked** (FR-2330 AC-b,
   classification half). **Already verified** (`T20.b`).
3. For any generated world in a test corpus, at every region and every direction: if grid
   arithmetic confirms no grid-adjacent region exists in that direction, no indicator renders
   (FR-2330 AC-c). **Already verified** (`T20.c`).
4. **New in this revision — the rendering half, closing the formerly-open criterion:** for any
   generated world in a test corpus, at every region and every direction classified **blocked**
   (per AC-2's own classification), the tile at that direction's screen position (`ARROW_ADDR_U`/
   `D`/`L`/`R`) reads as one of the 4 new blocked-edge tile indices (`0x1A`–`0x1D`, matching the
   direction), **not** the open-arrow tile index and **not** blank — satisfying FR-2330's full
   Description ("a blocked-edge indicator... render[s]").
5. **New in this revision:** for the same corpus, at every direction classified **open**, the tile
   at that position still reads as the existing open-arrow tile index (`TL_ARROW_U`/`D`/`L`/`R`),
   confirming the blocked-indicator addition does not regress the open case — a direct extension
   of `T20.a`'s own existing assertion, not a new behavior.

## 16. Verification Plan

Extends the existing **T20: Maze-Aware Transition-Edge Classification** suite in `test_rom.py`
(rather than opening a new suite number — same corpus, same routine, a natural rider):

- **AC-1/2/3 (classification correctness):** already covered by `T20.a`/`b`/`c` — no change.
- **AC-4 (blocked-edge rendering, new):** Test — for the same `T20_CORPUS` entries and the same
  per-region/per-direction sweep `T20.b` already performs, additionally assert the tile at
  `ARROW_POS[direction]` equals the direction's new blocked-tile constant whenever that
  direction's classification is `blocked` (reusing `T20.b`'s own `t20_blocked_n`/`t20_blocked_bad`
  bookkeeping shape, extended with a tile-index check rather than only the row/col + "no arrow"
  check it performs today).
- **AC-5 (open-case non-regression, new):** Test — extend `T20.a`'s own existing assertion set to
  also confirm the open-case tile index specifically (not just "some non-blank tile"), landing in
  the same check.
- **Exact pixel-bitmap correctness** is explicitly **out of this Verification Plan's scope** — a
  content-review concern (`09-content-review`'s own craft-checklist judgment, `FS-106`), not a
  `test_rom.py` assertion; this Feature's own tests verify *which* tile index is drawn, not
  whether that tile's pixels read well.

**Corpus:** reuses `T20_CORPUS` (`test_rom.py`'s existing scale/seed set for this suite) — no new
corpus needed, since AC-4/5 ride the same per-region/per-direction sweep AC-2/AC-1 already
perform.

## 17. Dependencies

Per FEAT-2100's own Dependencies (carried forward verbatim): `FEAT-2000` (extends its
arrow-signaling logic; the open-edge case is this Feature's own dependency on that logic
continuing to work unchanged); `FEAT-9100`/`FS-107` (there is no "blocked but grid-adjacent" case
to signal before the maze exists). **This revision's own new dependency:** the logic half
(`IP-1080`, `VERIFIED`) — the rendering half's implementation reads `DRA_ROW`/`DRA_COL` and the
classification arithmetic `IP-1080` already built; it does not re-derive them.

## 18. Risks

Carried forward from FEAT-2100's own Risk assessment (Low): the classification logic itself is
low-risk (simple arithmetic, already shipped and `VERIFIED`). **This revision's own new risk
surface (Low):** the 4 new tile bitmaps are pure content (pixel art), no new algorithm or data
flow — the only implementation risk is a routine content-authoring task (design 4 small icon
tiles against an already-decided silhouette concept), not an architectural or logic risk.

## 19. Open Questions

1. **RESOLVED (2026-07-11).** The blocked-edge indicator's tile art and palette assignment were
   undecided (Feature Review finding #7,
   [05-feature-review.md](../feature-planning/05-feature-review.md); tracked as `BL-0068`).
   `03-architecture-design-synthesis` closed the gap:
   [GDS-08 §10](../architecture/08-presentation-architecture.md) decides a distinct
   broken/dashed-bar tile shape (silhouette-different from the open-path arrow, not a recolor), 4
   new directional tiles at `0x1A`–`0x1D` (continuing the existing UI-icon block before `Digits` at
   `0x20`), reusing the open arrow's own palette 2 (UI/gold) attribute verbatim — 0 new palette
   entries spent.
2. **RESOLVED (`IP-1080`, 2026-07-12).** The classification needs one piece of transient storage:
   `DRA_ROW`/`DRA_COL` (`0xC2D8`–`0xC2D9`), the re-derived `(row, col)` position, computed once
   per `draw_region_arrows` call.
3. **RESOLVED (this revision, 2026-07-12).** The rendering half's own workflow/behavior contract
   was the last open item this document tracked — §6 Workflow C and §15 AC-4/AC-5 close it. **Not
   an Open Question for this document, by design:** the exact pixel bitmap for the 4 new tiles —
   `GDS-08` §10 deliberately specifies only the silhouette concept, leaving the literal artwork to
   whichever `08-content-authoring` package implements this spec, the same division of labor every
   other tile-bearing FS in this tree uses (not a gap in this specification).

## 20. Related ADRs

ADR-0009 (screen-graph world generation — the boundary-arithmetic convention this Feature's
classification logic reuses), ADR-0012 (point 2 — confirms `REGION_GRAPH`'s data format carries no
open/blocked distinction, which is exactly why this Feature's render-time re-derivation is
necessary).
