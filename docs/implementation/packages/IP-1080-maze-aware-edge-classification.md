# IP-1080 — Maze-Aware Transition-Edge Classification (logic half)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1080` — implements
[**FS-108**](../../features/FS-108-maze-aware-transition-edge-signaling.md) (`FEAT-2100`, Epic
`EP-1000`, Release 2 post-ship addendum) — **logic half only**. FS-108's rendering half (the
blocked-edge indicator's tile art/palette) is not planned by this package — it remains blocked on
`BL-0068`'s still-unrouted `GDS-08` delta (FS-108 Open Question 1). Resolves FS-108 Open Question
2 (classification result needs no dedicated transient storage — computed and consumed inline, see
§6).

## 2. Objective

Extend `draw_region_arrows` (`asm_game.py`, `IP-1030`) with the render-time logic that classifies
each of a region's four screen edges into **open** / **blocked** / **absent**, by re-deriving grid
adjacency from `(row, col, WORLD_SCALE)` arithmetic and comparing it against `REGION_GRAPH`'s own
neighbor byte — the classification `FR-2330` requires, independent of what the blocked state
eventually renders as.

## 3. Requirements Covered

FR-2330 — **partially**: the classification behavior only (this requirement's render-time
"independently re-derive... and compare" clause). The requirement's rendered-*appearance*
obligation for the blocked state is not covered by this package — it is `BL-0068`'s own scope,
riding a future package once the `GDS-08` delta lands. This partial-coverage note is carried
forward from FS-108 §5 verbatim, not narrowed further here.

## 4. Architecture Components

`ADR-0012` point 2 (confirms `REGION_GRAPH`'s data format carries no open/blocked distinction —
exactly why this render-time re-derivation is necessary) · `ADR-0009` (the boundary-arithmetic
convention this logic reuses) · GDS-09 (`draw_region_arrows`'s existing loop shape, extended in
place).

## 5. Interfaces

- **`REGION_GRAPH`'s existing confirmed layout** — read-only, same neighbor-byte access
  `draw_region_arrows` already performs (confirmed by direct re-read, `asm_game.py:885`+).
- **`draw_region_arrows`'s existing per-direction loop** — extended with a new conditional branch
  inside the existing loop body, not a new routine or call site.
- **No new `patches` dict key** for the classification logic itself (pure WRAM-read/arithmetic).
  A tile/attribute patch-point pair for the blocked-edge indicator's own art is the rendering
  half's concern, not planned here.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`draw_region_arrows`** (existing label, `asm_game.py:885`): within the routine's existing
    per-direction loop (four iterations, up/down/left/right — the same slot order `REGION_GRAPH`
    itself uses), the existing logic already branches on whether the current direction's
    `REGION_GRAPH` neighbor byte is `0xFF`: today, `0xFF` means "draw nothing," any other value
    means "draw the open-edge arrow." This package inserts a classification step **inside the
    `0xFF` branch only** (the non-`0xFF`/open case is untouched, per `FR-2330`'s own Dependencies
    on `FR-2320`'s unmodified rendering, FS-108 §4): compute whether a grid-adjacent region exists
    in the current direction from the current region's `(row, col)` (already derived elsewhere in
    `dsr_p`'s own region-index arithmetic — `row = CUR_ZONE / WORLD_SCALE`, `col = CUR_ZONE MOD
    WORLD_SCALE`, no `DIV`/`MOD` opcode needed since `WORLD_SCALE` is a small runtime value: reuse
    `check_zone_transition`'s own established boundary-check pattern (`IP-9050`) — `up` exists iff
    `row > 0`, `down` iff `row < WORLD_SCALE - 1`, `left` iff `col > 0`, `right` iff `col <
    WORLD_SCALE - 1`, the exact same per-direction test `check_zone_transition`'s own boundary
    halt already performs, reused here rather than reinvented). If that arithmetic confirms a
    grid-adjacent region exists: the edge is **blocked** — for this package's own scope, this
    resolves to a no-op render-wise (no new tile drawn — the actual blocked-edge tile write is the
    rendering half's scope, `BL-0068`), but the classification decision itself is made and is
    directly testable (see §8) independent of what, if anything, gets drawn for it. If the
    arithmetic confirms no grid-adjacent region exists: the edge is **absent** — identical to
    today's shipped no-op, no change.
  - **No new WRAM address.** Resolves FS-108 Open Question 2: the classification result (open /
    blocked / absent) is computed and consumed entirely within one loop iteration — no value
    needs to survive past the iteration that computes it, so no transient scratch byte is
    introduced (unlike `IP-1070`'s `GW_MAZE_STATE` family, which must persist across the whole
    generation routine).
- **No change to `worldgen.py`** — this package is presentation-layer logic, not generation; the
  oracle has no rendering counterpart.
- **Modify: `test_rom.py`** — add new suite **T20** (see §8), gated to run only when a maze-shaped
  world is present (i.e., depends on `IP-1070` having shipped) — see §12.

## 7. Implementation Tasks

**Verb inventory:** this capability is pure **render** (the classification decision feeds a render
branch) — `generate` (`IP-1070`'s own scope, a hard dependency, §12), `navigate`
(`check_zone_transition` is read-only reused here for its boundary-arithmetic pattern, not
modified), `persist` (not applicable — no new state), and `review` (`09-content-review` — not
applicable to *this* package, since it draws no new visible tile; the eventual rendering-half
package, once `BL-0068` resolves, is the actual content-review target) are named and explicitly
deferred-not-applicable, not silently skipped.

**Supersession sweep:** this package extends `draw_region_arrows`'s existing 2-state branch into a
3-state one; the sweep confirms no *other* call site independently re-implements the same
open/no-open distinction `draw_region_arrows` already owns. Swept: `dsr_p` (the only caller of
`draw_region_arrows`, passes through unmodified) and `check_zone_transition` (a sibling consumer
of the same grid-boundary arithmetic this package reuses, not a duplicate of it — confirmed by
direct re-read that its own boundary check is functionally identical in shape, which is exactly
why this package cites it as the pattern to reuse rather than re-deriving independently). **No
other call site found; sweep confirmed clean.**

Ordered: (1) the classification branch inside `draw_region_arrows`'s existing `0xFF` case; (2)
author T20; (3) full suite run; (4) documentation/traceability updates (§9). No WRAM-constants
task (§6) and no oracle task (no Python mirror needed — this is render-time-only logic with no
build-side reference to keep in lockstep, unlike `IP-1070`).

## 8. Tests to Add

New `test_rom.py` suite **`T20: Maze-Aware Transition-Edge Classification`**, implementing FS-108's
Verification Plan. **Shares `IP-1070`'s T19 corpus** (both suites need maze-shaped worlds to
exercise the blocked case at all) — at minimum `scale ∈ {2, 3, 9}`, seeds including `0`, plus a
zero-braid-fraction run (pure spanning tree — the corpus case most likely to exercise the blocked
classification densely, per FS-108 §16).

- T20.a — **open classification** (FS-108 AC-1): for every corpus entry, every region/direction
  where `REGION_GRAPH` shows a live neighbor, confirm the routine takes the unmodified open-edge
  branch (a direct extension of `T13`'s existing arrow-presence check, IP-1030's own suite).
- T20.b — **blocked classification** (FS-108 AC-2): for every corpus entry, every
  region/direction where `REGION_GRAPH` shows `0xFF` but independently-computed grid arithmetic
  confirms a grid-adjacent region exists, confirm the routine's classification reaches the new
  blocked branch — asserted via a direct WRAM/register-state inspection at the classification
  point (since no new tile is drawn yet to inspect visually, per this package's own logic-only
  scope), cross-checked against the oracle's own graph (`worldgen.py`, reusing `IP-1070`'s T19
  corpus fixtures).
- T20.c — **absent classification** (FS-108 AC-3): for every corpus entry, every region/direction
  where grid arithmetic confirms no grid-adjacent region exists, confirm no branch fires and no
  tile changes from today's shipped no-op — a direct regression check against `T13`'s existing
  boundary-case assertions.
- **AC-4 (visual/rendering criterion) is explicitly not exercised by T20** — per FS-108 §16, no
  suite section is authored for it; the Verification Checklist (§11) names this gap explicitly so
  `09-package-verification` confirms it is still open, not silently treated as covered.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-2330 Notes → logic half implemented,
  rendering half still open (cites `BL-0068`).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-2330 row → `IP-1080`/T20 (logic),
  `UNASSIGNED` still honest for the rendering half's own eventual test coverage.
- `docs/features/FS-108-…md` metadata: implemented-by pointer for the logic half; Open Question 2
  marked resolved; Open Question 1 remains open, unchanged.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- FS-108's three closeable Acceptance Criteria (AC-1/2/3) demonstrably pass via T20.a–c.
- AC-4 remains explicitly open, named as such in this package's own Definition of Done and
  Verification Checklist — not silently dropped.
- ROM builds at 32768 bytes; full suite passes headless.
- The existing open-edge case (`FR-2320`) shows zero behavioral change — confirmed by T20.a's
  direct regression check against `T13`'s own existing assertions.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes (T1–T20).
- [ ] T20.a–c each present and passing (map 1:1 to FS-108 AC-1…3).
- [ ] **AC-4 (visual rendering) confirmed still open** — no suite claims to cover it; this is a
      genuine, tracked gap (`BL-0068`), not an oversight.
- [ ] Direct code read: the new classification branch fires only inside `draw_region_arrows`'s
      existing `0xFF` case — the open-edge branch (`FR-2320`) shows zero diff.
- [ ] Direct code read: the grid-adjacency arithmetic matches `check_zone_transition`'s own
      boundary-check pattern exactly (reused, not reinvented) — confirmed by side-by-side read.
- [ ] GDS-09/RQ-01/RQ-04/FS-108/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1070** (this package's own hard prerequisite) — **must reach at least `COMPLETE` before
  this package can enter `IN PROGRESS`**, since there is no maze-blocked case to classify before
  a maze exists; per this skill's own `READY`-means-`VERIFIED` convention, this package is
  `BLOCKED` (not merely `NOT STARTED`) until `IP-1070` is `VERIFIED`.
- **IP-1030** (`VERIFIED`) — this package extends `draw_region_arrows`, the routine `IP-1030`
  shipped.
- **IP-9050** (`COMPLETE`, not yet `VERIFIED`) — not a functional dependency (this package doesn't
  modify `check_zone_transition`, only reuses its boundary-arithmetic *pattern* by reference), but
  its own boundary-check code is what this package's classification logic mirrors — named for
  traceability of the reused pattern, not a build order requirement.

## 13. Risks

- **Depends on `IP-1070` shipping first** (Low — a scheduling risk, not a design risk; `FS-108`'s
  own Dependencies already name this explicitly, not discovered late).
- **Partial-FR coverage** (Low-Medium, carried from FS-108 §18): this package closes only part of
  `FR-2330` — a future package (rendering half) is required before the requirement is fully
  satisfied. Mitigated by naming the gap explicitly in every field that could otherwise imply
  completeness (§3, §10, §11) rather than letting `IP-1080` reaching `COMPLETE` read as "FR-2330
  done."
- **T20.b's classification-point inspection (no visible tile to check)** — a slightly weaker test
  than a screenshot-based assertion would be; acceptable because the actual visual claim (AC-4) is
  explicitly not this package's scope, and the classification decision itself is fully observable
  via direct WRAM/register inspection at the point it's made.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` and rebuild. No WRAM/SRAM layout change, no save-format
concern. Independent of `IP-1070`'s own rollback — reverting `IP-1080` alone leaves `IP-1070`'s
maze generation intact, simply with blocked edges rendering as if absent again (today's shipped
2-state behavior).
