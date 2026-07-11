# FS-108 — Maze-Aware Transition-Edge Signaling (logic half)

> Feature Specification for [FEAT-2100](../feature-planning/03-feature-catalog.md#feat-2100--maze-aware-transition-edge-signaling-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-2100, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Scope note (deliberate, not an oversight):** this document specifies FEAT-2100's **logic
> half only** — the render-time classification of each screen edge into one of three states. The
> **rendering half** (the blocked-edge indicator's actual tile art/palette assignment) cannot be
> specified yet: it needs a `GDS-08` presentation-architecture delta that has not been authored,
> named as `03-architecture-design-synthesis`'s own open item by Feature Review finding #7
> ([05-feature-review.md](../feature-planning/05-feature-review.md)) and carried forward here as
> Open Question 1. This is a partial specification of one Feature by design, not a defect — the
> classification logic is independently specifiable and independently testable before the tile
> art exists.

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md) · [ADR-0012](../architecture/adr/ADR-0012-maze-shaped-region-adjacency.md)

> **Forward reference (metadata only):** logic half planned by
> [IP-1080](../implementation/packages/IP-1080-maze-aware-edge-classification.md) (2026-07-11),
> which resolves this document's Open Question 2. Open Question 1 (the rendering half's tile art)
> remains open, tracked as `BL-0068`.

## 1. Feature ID

`FS-108` — expands `FEAT-2100` (Maze-Aware Transition-Edge Signaling), Epic `EP-1000` (Core Game
Loop & State Machine).

## 2. Title

Maze-Aware Transition-Edge Signaling (logic half)

## 3. Purpose

Distinguish, at each screen edge, a maze-blocked-but-grid-adjacent edge from a true grid boundary
— both currently signal identically (no arrow) — so a maze-blocked edge reads as "there is a path
here I haven't opened" rather than as a dead end. Carried forward verbatim from FEAT-2100's own
Purpose/User Value (Medium-High — without this, `FEAT-9100`'s maze loses legibility).

## 4. Scope

**In scope (this document):** the render-time logic that, for each of a region's four screen
edges, determines which of three states applies — open (a live, maze-connected neighbor), blocked
(a grid-adjacent region exists but the maze doesn't connect to it), or absent (no grid-adjacent
region exists at all) — by re-deriving grid adjacency from `(row, col, WORLD_SCALE)` arithmetic
and comparing it against `REGION_GRAPH`'s own neighbor byte, since the data format itself does not
distinguish the latter two cases (both are `0xFF`, `ADR-0012` point 2).

**Out of scope (this document, and not specified here):** the blocked-edge indicator's actual
tile art, palette assignment, or any new tile-budget accounting — blocked on the `GDS-08` delta
named above (§19 Open Question 1); this is a genuine gap in what can be specified today, not an
omission. Also excluded, per FEAT-2100's own catalog entry: the maze generation this Feature
signals the output of (`FEAT-9100`/`FS-107`); the open-edge case's existing rendering (`FEAT-2000`'s
`FR-2320`, reused verbatim, not reimplemented); any mid-screen collision/wall enforcement (out of
scope for any current Feature).

## 5. Requirements Implemented

FR-2330 — the exact requirement FEAT-2100 owns. **Only the classification behavior this
requirement describes is fully specified here** (its Description's "render-time logic must
independently re-derive... and compare" clause); the requirement's own rendered-*appearance*
obligation for the blocked state cannot be closed until the `GDS-08` delta lands (§19 OQ1) — this
is recorded as a partial-coverage note against FR-2330, not a silent narrowing of the requirement
Requirements Implemented cross-check.

## 6. User Workflows

**Workflow A — screen-edge classification during PLAYING** (extends `FEAT-2000`'s existing
render dispatch that draws `FR-2320`'s open-edge arrows, per `IP-1030`'s shipped
`draw_region_arrows` loop shape):

1. Player is in a generated region during `PLAYING`, a maze-shaped world has been generated
   (`FEAT-9100` precondition, `FR-2330`).
2. For each of the region's four directions (up/down/left/right), the render routine reads
   `REGION_GRAPH`'s corresponding neighbor byte for the current region.
3. If the neighbor byte is a live region index (not `0xFF`), the edge is classified **open** —
   `FR-2320`'s existing arrow-rendering logic fires unchanged (this Feature adds no new behavior
   for this case).
4. If the neighbor byte is `0xFF`, the routine independently computes whether a grid-adjacent
   region exists in that direction from the current region's `(row, col)` and the world's
   `WORLD_SCALE` (the same arithmetic a grid boundary is defined by — e.g. "up" is grid-adjacent
   iff `row > 0`, mirroring the inverse of the boundary-halt check `check_zone_transition`
   already performs at each edge, `IP-9050`).
5. If that arithmetic confirms a grid-adjacent region exists, the edge is classified **blocked** —
   this Feature's own new case. *(Rendering the blocked indicator itself is not specified in this
   document — see §19 OQ1.)*
6. If the arithmetic confirms no grid-adjacent region exists, the edge is classified **absent** —
   no indicator renders, identical to today's shipped behavior.

**Workflow B — before `FEAT-9100` ships or for a non-maze edge:** unaffected — this Feature's
classification logic only produces a different outcome than today's 2-state behavior for edges
where `REGION_GRAPH` shows `0xFF` but a grid neighbor genuinely exists, which cannot occur before
`FEAT-9100`'s maze pass ships (today's full-lattice model never leaves a grid-adjacent edge
`0xFF`). No regression to the open/absent cases either way.

## 7. System Behaviour

**Normal path:** for any generated region and any of its four directions, the classification
routine produces exactly one of the three states, matching `FR-2330`'s own Acceptance Criteria
(a)/(b)/(c) verbatim.

**Edge case — a region at a true grid corner (e.g. `row=0, col=0`):** two of its four directions
(up, left) are classified absent unconditionally, regardless of `REGION_GRAPH` content — the grid
arithmetic alone determines this, matching today's shipped boundary-halt behavior exactly
(`check_zone_transition`'s existing logic already computes the same non-adjacency for these
directions, `FR-2310`).

**Edge case — `WORLD_SCALE` at its minimum (2) vs. maximum (9):** the classification arithmetic
is scale-parameterized identically to `check_zone_transition`'s own existing boundary check
(`IP-9050`) — no new scale-dependent behavior beyond what that already-shipped logic establishes;
this Feature reuses the same arithmetic, applied at render time instead of navigation time.

**Edge case — every edge of a region is blocked (a maze dead end with a zero-fraction braid
draw):** all four directions could, in principle, classify as some mix of blocked/absent with no
open edges at all — a valid state under `FR-9140`'s own guarantees (the region remains reachable
via the edge it was *entered* through, which is by definition open from the adjacent region's own
perspective) — not a failure state this Feature needs to handle specially.

## 8. Module Responsibilities

Per GDS-03's module decomposition:

- **`asm_game.py`** — `draw_region_arrows`'s own extension: a new branch, taken only when
  `REGION_GRAPH`'s neighbor byte reads `0xFF`, that performs the grid-adjacency arithmetic (§6
  step 4) and produces the blocked/absent classification. The existing open-edge branch (`FR-2320`)
  is unchanged.
- **`tiles.py`/`tilemaps.py`** — **not specified by this document.** The blocked-edge indicator's
  tile art is FEAT-2100's rendering half, blocked on the `GDS-08` delta (§19 OQ1); this
  specification names the module that will eventually own it without committing to its content.

## 9. Interfaces Used

- **`REGION_GRAPH`'s existing confirmed layout** (GDS-07 §2/§6, unchanged by `ADR-0012` point 2)
  — read-only, same neighbor-byte access `draw_region_arrows` already performs.
- **`draw_region_arrows`'s existing loop shape** (`IP-1030`, GDS-09's confirmed delta) — extended
  in place with a new conditional branch inside the existing per-direction loop, not a new
  routine or a new call site.
- **No new `patches` dict key** for the classification logic itself — it is pure WRAM-read/
  arithmetic, not ROM-resident content. (A new tile/attribute patch-point pair would be needed for
  the rendering half once the `GDS-08` delta specifies it — out of this document's scope.)

## 10. Data Model Changes

- **No change to `REGION_GRAPH`** — confirmed by `ADR-0012` point 2: the classification is
  computed at render time from existing data, not stored.
- **No new persistent WRAM or SRAM entity.** The classification result for a given edge is
  transient — computed and consumed within the same `draw_region_arrows` call, exactly as the
  existing open/absent decision already is today; no new domain entity is introduced (GDS-04 has
  no delta note for this Feature's logic half beyond the one already recorded for `ADR-0012` point
  2's "indistinguishable at the data-model level" observation).

## 11. State Changes

None. This Feature adds no new `GameState` value and no new persistent state; it changes only
what `draw_region_arrows` computes and (once the rendering half is specified) draws during the
existing `PLAYING`-state render path.

## 12. Error Handling

- **A direction's grid-adjacency arithmetic disagreeing with `REGION_GRAPH`'s own neighbor byte in
  a way that implies an open edge with no grid-adjacent region:** cannot occur under `FR-9140`'s
  own postcondition (every edge in the generated graph also exists in the full grid graph,
  `FS-107` §15 AC-1) — the open case is only ever reached when `REGION_GRAPH` already shows a live
  neighbor, which by that guarantee is always grid-adjacent. No defensive check needed beyond what
  `FEAT-9100`'s own generator-guaranteed invariant already provides.

## 13. Performance Considerations

- **NFR-1300/NFR-1100** (screen-transition smoothness, VBlank-gated PPU access): this Feature's
  classification logic adds one small, fixed-cost arithmetic check per direction (≤4 per region
  render) inside `draw_region_arrows`'s existing per-direction loop — the same cost class as the
  loop's existing per-direction work, no new VRAM/OAM write timing concern beyond what `IP-1030`
  already establishes for that routine.
- **ROM budget:** the classification logic itself is small (a handful of comparisons); the
  rendering half's ROM cost (new tile data) is not estimated here, pending the `GDS-08` delta.

## 14. Integrity Considerations

None beyond what `FEAT-9100`/`FS-107` already guarantees as this Feature's own precondition
(`REGION_GRAPH`'s determinism and subgraph-of-full-lattice property, consumed read-only here).
This Feature introduces no new determinism or save-integrity concern of its own.

## 15. Acceptance Criteria

1. For any generated world in a test corpus, at every region and every direction: if
   `REGION_GRAPH` shows a live neighbor, the classification routine reports **open** (FR-2330
   AC-a).
2. For any generated world in a test corpus, at every region and every direction: if no
   `REGION_GRAPH` neighbor exists but grid arithmetic confirms a grid-adjacent region exists in
   that direction, the classification routine reports **blocked** (FR-2330 AC-b).
3. For any generated world in a test corpus, at every region and every direction: if grid
   arithmetic confirms no grid-adjacent region exists in that direction, the classification
   routine reports **absent** (FR-2330 AC-c).
4. **Not yet closeable by this document:** "the blocked-edge indicator renders visually distinct
   from the open/absent states" — depends on the `GDS-08` delta (§19 OQ1); recorded here as an
   explicitly open criterion, not silently dropped from FR-2330's own Acceptance Criteria.

## 16. Verification Plan

Per `FR-2330`'s own Verification Method (Test — per-edge state audit across a `(seed, scale)`
corpus, extending `FR-2320`'s existing tilemap-inspection pattern), landing in a new **T20:
Maze-Aware Transition-Edge Classification** suite in `test_rom.py` (the next unused suite number
after `FS-107`'s proposed T19):

- **Classification correctness (AC-1/2/3):** for a `(seed, scale, braid-fraction)` corpus (reusing
  `FS-107`'s own T19 corpus, since both suites need maze-shaped worlds to exercise the blocked
  case at all), assert every region/direction's classification matches the oracle's independently
  computed expectation (grid arithmetic cross-checked against `worldgen.py`'s own graph, mirroring
  `T12`/`T17`'s existing oracle-comparison pattern).
- **Visual/rendering criterion (AC-4):** explicitly **not verifiable yet** — no suite section is
  authored for it; `09-package-verification`'s own checklist should confirm this gap is still open
  when this Feature's implementation package is verified, not silently treated as covered by the
  classification tests above.

**Corpus:** shares `FS-107`'s T19 corpus (`scale=2`, `scale=9`, `scale=3`, `seed=0`, plus at least
one braid-fraction extreme) — a maze with zero braided edges (pure spanning tree) is the corpus
case most likely to exercise the blocked classification densely, since it has the most pruned
edges.

## 17. Dependencies

Per FEAT-2100's own Dependencies (carried forward verbatim): `FEAT-2000` (extends its
arrow-signaling logic; the open-edge case is this Feature's own dependency on that logic
continuing to work unchanged); `FEAT-9100`/`FS-107` (there is no "blocked but grid-adjacent" case
to signal before the maze exists — this Feature's logic half can be implemented once `FS-107`'s
maze pass ships, but not before).

## 18. Risks

Carried forward from FEAT-2100's own Risk assessment (Low, contingent on one real blocker): the
classification logic itself is low-risk (simple arithmetic, no new algorithm family) — the actual
named risk is entirely the rendering half's missing `GDS-08` delta (§19 OQ1), which this document
does not resolve and explicitly does not attempt to work around (e.g. by reusing an existing tile
as a stand-in) — that would be inventing a presentation decision outside this stage's authority.

## 19. Open Questions

1. **The blocked-edge indicator's actual tile art and palette assignment are undecided.** No
   `GDS-08` delta exists yet for this new visual state — Feature Review finding #7
   ([05-feature-review.md](../feature-planning/05-feature-review.md)) already flagged this as
   real and open, not yet routed to an actual `03-architecture-design-synthesis` invocation as of
   this document's authoring. This blocks FEAT-2100's rendering half entirely — AC-4 (§15) and its
   corresponding verification gap (§16) cannot close until it resolves. Resolves at:
   `03-architecture-design-synthesis` (a `GDS-08` delta), then a follow-up pass of this skill to
   extend this document (or author a sibling `FS-xxx`) covering the rendering half once the tile
   art exists.
2. **Whether the classification result needs any transient storage of its own** (e.g. a per-
   direction scratch byte holding the 3-way state before the render decision consumes it) or can
   be computed and consumed inline within the existing loop iteration, is an implementation-detail
   choice not decided here — mirrors `FS-107` Open Question 2's identical deferral pattern.
   Resolves at: `07-implementation-planning`/`08-code-implementation`.

## 20. Related ADRs

ADR-0009 (screen-graph world generation — the boundary-arithmetic convention this Feature's
classification logic reuses), ADR-0012 (point 2 — confirms `REGION_GRAPH`'s data format carries no
open/blocked distinction, which is exactly why this Feature's render-time re-derivation is
necessary).
