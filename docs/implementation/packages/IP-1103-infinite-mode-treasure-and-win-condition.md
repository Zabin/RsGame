# IP-1103 — Infinite Mode: Treasure Placement & Win-Condition State

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1103` — implements part of [**FS-110**](../../features/FS-110-infinite-mode.md) (`FEAT-10000`,
Epic `EP-6000`, `Future` bucket). Covers Workflow C steps 1-2 in full; **step 3 (the top-3
comparison's own call site) is explicitly NOT implemented by this package** — see §2/§7/§13,
`FS-110` Open Question 3 / `BL-0112`.

## 2. Objective

Implement treasure-presence detection (reusing `IP-1101`'s predicate), collection (reusing the
existing `check_collisions` interface), and the running-count/top-3-table data and comparison
**subroutine**. **Deliberately incomplete by design, not by oversight:** the automatic call site
that decides *when* the top-3 comparison fires during play is not implemented — `FS-110` itself
routes that decision to `04-requirements-engineering` or a direct user decision (`BL-0112`), not
to `07-implementation-planning`, and this package honors that routing rather than inventing an
answer.

## 3. Requirements Covered

FR-10300 (treasure collection, the collection-event half — `IP-1101` covers the presence-
predicate half); FR-10400 (win-condition state and the comparison subroutine — **the automatic
trigger is out of this package's own scope**, see §2).

## 4. Architecture Components

[ADR-0017](../../architecture/adr/ADR-0017-infinite-mode-treasure-placement-and-win-condition.md)
(treasure decoupled from maze structure; score-chasing win condition, no name-entry UI; point 4
confirms the top-3 mechanism is compatible with either run/session-shape answer, so this
package's own deferral of the trigger does not block building the comparison subroutine itself).

## 5. Interfaces

- **`check_collisions`** (`FR-3100`, unchanged) — this package's own collection-detection reuses
  this interface's existing calling contract exactly as `FEAT-9000`'s own `KeyItem` collection
  already does, gated on `GAME_MODE == 1` and `INF_TREASURE_HERE` (`IP-1102`'s own cached flag)
  being set.
- **`IP-1101`'s treasure-presence predicate** (called once per region materialization by
  `IP-1102`'s own `inf_ensure_window`, cached into `INF_TREASURE_HERE`) — this package reads that
  cache, it does not re-derive the predicate itself.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constants** (first unclaimed bytes past `IP-1102`'s own `INF_TREASURE_HERE`,
    `0xC404`): `RUNNING_TREASURE_COUNT = 0xC405` (2 bytes, signed range not needed — unsigned
    16-bit, wide enough for an indefinitely-resumable run's own running total), `TOP_SCORE_TABLE
    = 0xC407` (6 bytes, `0xC407`–`0xC40C`, 3 entries × 2 bytes, stored in descending order —
    index 0 is the current high score).
  - **`check_collisions`'s existing per-item-type branch (existing label):** gains a new
    `GAME_MODE == 1` branch, parallel to the existing `KeyItem`/`ScoreItem` branches — on a
    collision at the player's current position when `INF_TREASURE_HERE != 0`: increment
    `RUNNING_TREASURE_COUNT` (16-bit, `INC` low byte then `INC` high byte on carry — no overflow
    guard needed at this scope, an indefinitely-resumable run reaching 65536 treasures is not a
    realistic play scenario), clear `INF_TREASURE_HERE` (collected, not re-collectible this
    materialization), and mark the current region collected in `IP-1104`'s own ledger-write
    interface (a forward call this package names but `IP-1104` implements — see Dependencies).
  - **New subroutine `inf_check_top_score`** (the comparison subroutine, §2) — inputs: none
    (reads `RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE` directly). Compares
    `RUNNING_TREASURE_COUNT` against `TOP_SCORE_TABLE`'s own lowest entry (index 2); if
    `RUNNING_TREASURE_COUNT` exceeds it, inserts in sorted-descending position (displacing the
    previous lowest, shifting the table), otherwise leaves the table unchanged. **No name-entry
    UI anywhere in this subroutine or its callers** (`FR-10400`'s own explicit requirement) — pure
    numeric insertion. **This subroutine is written, but is not called from anywhere in the
    shipped dispatch this package touches** — no in-game event invokes it. A future package
    (once `BL-0112` resolves) supplies the call site.

## 7. Implementation Tasks

Ordered: (1) `RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE` WRAM constants; (2) `check_collisions`'s
`GAME_MODE == 1` branch (collection detection, count increment, `INF_TREASURE_HERE` clear,
ledger-mark forward call); (3) `inf_check_top_score` (comparison + sorted insertion, unit-callable
but not wired to any trigger); (4) rebuild ROM; (5) author T25 (see §8, including the explicit
"no automatic call site exists" negative check); (6) full suite run; (7) documentation/
traceability updates (§9).

**`OQ3`/`BL-0112` boundary, stated precisely:** tasks (1)-(3) above are fully buildable and
testable without `OQ3` resolving — `inf_check_top_score` is directly callable from a test harness
with a synthetic `RUNNING_TREASURE_COUNT`, exactly as `T23`'s own oracle-style tests call
`IP-1101`'s routine directly. What remains unbuilt is *only* the automatic in-game invocation —
the piece `FS-110` itself says is not this stage's call to make.

## 8. Tests to Add

New `test_rom.py` suite **`T25: Infinite Mode — Treasure & Win-Condition State`**:

- T25.a — treasure collection: at a region with `INF_TREASURE_HERE` set, drive the player onto
  the collection position (reusing `check_collisions`'s own existing collision-point convention) →
  assert `RUNNING_TREASURE_COUNT` increments by exactly 1, `INF_TREASURE_HERE` clears.
- T25.b — no double-collection: repeat the same approach at the same region without leaving/
  re-entering the materialized window → assert `RUNNING_TREASURE_COUNT` does not increment again.
- T25.c — `inf_check_top_score`, called directly with a corpus of synthetic
  `(RUNNING_TREASURE_COUNT, TOP_SCORE_TABLE)` fixtures: a count exceeding the current lowest entry
  is inserted, displacing it, table stays sorted descending; a count not exceeding any entry
  leaves the table byte-for-byte unchanged (AC-4, FR-10400).
- T25.d — **negative test, stating the deferral explicitly rather than leaving it silent:** static
  audit confirms `inf_check_top_score` has zero call sites anywhere in the built ROM's dispatch
  tables — documents, in a checkable form, that this package genuinely does not wire an automatic
  trigger, so a future package's own addition of one is a clean, detectable diff.
- T25.e — no name-entry state is reachable from any Infinite Mode code path this package adds
  (static audit over the new branches only, mirroring `FS-110` AC-4's own explicit requirement).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-10300 status → Implemented (collection
  half); FR-10400 status → **Partially Implemented** (comparison subroutine exists, no automatic
  trigger — a Notes entry stating this precisely, mirroring `IP-1080`'s own precedent for a
  requirement split across packages).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-10300/FR-10400 rows → `IP-1103`/
  T25, with FR-10400's own row noting the trigger-call-site gap explicitly.
- `docs/features/FS-110-infinite-mode.md` metadata: implemented-by pointer for Workflow C steps
  1-2 only (step 3 explicitly not yet implemented); §19 Open Question 3 left open, cross-
  referenced to this package's own stated boundary rather than silently dropped.
- Master Build Plan status row, noting the deliberate scope boundary.

## 10. Definition of Done

- Treasure collection increments the running count exactly once per region's treasure (T25.a/b).
- `inf_check_top_score` correctly inserts/rejects against a synthetic corpus, no name-entry state
  reachable (T25.c/e).
- **No automatic call site exists for the comparison subroutine** (T25.d) — this is a pass
  condition, not a gap to silently fix; `AC-4`'s own "no name-entry prompt is reachable at any
  point" half is trivially true (nothing calls the routine that would lead there), while its own
  "final treasure count… is inserted" half remains genuinely untestable end-to-end until `BL-0112`
  resolves and a follow-up package wires the trigger — stated exactly this way in `FS-110`'s own
  Acceptance Criteria tracking, not asserted complete.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T25.a–e each present and passing.
- [ ] Direct code read: `inf_check_top_score` is reachable only via direct test-harness calls, not
      from `PLAYING`'s own dispatch, `st_save`, `st_victory`, or any other existing state handler.
- [ ] Direct code read: `check_collisions`'s new `GAME_MODE == 1` branch does not alter the
      existing `KeyItem`/`ScoreItem` branches' own code path (finite-mode collection unaffected).
- [ ] FR-10300/FR-10400/RTM/Master-Build-Plan deltas applied exactly as §9 names, with FR-10400's
      own partial-implementation status stated precisely, not rounded up to Implemented.

## 12. Dependencies

- **`IP-1101`** (**NOT YET `VERIFIED`**) — the treasure-presence predicate this package's own
  collection branch consumes (via `IP-1102`'s cache).
- **`IP-1102`** (**NOT YET `VERIFIED`**) — `INF_TREASURE_HERE`'s own cache and the materialized-
  window's per-frame loop this package's collection check rides inside.
- **`IP-1010`/`FEAT-3000`** (`VERIFIED`) — `check_collisions`'s existing calling contract, reused
  unmodified for the finite mode's own branches.

`IP-1104` depends on this package (the ledger's own collected-state field is written by this
package's collection branch, via a forward call `IP-1104` implements the receiving end of).

## 13. Risks

- **`OQ3`/`BL-0112` remaining unresolved leaves `FR-10400` genuinely incomplete** (Medium, named
  explicitly rather than absorbed) — the win condition cannot be fully exercised end-to-end (a
  real run, played to whatever "end" eventually means, actually landing in the top-3 table)
  until a future pass wires the call site; this package's own Definition of Done draws the line
  precisely so no one mistakes "the subroutine exists" for "the feature is complete."
- **The `RUNNING_TREASURE_COUNT` reset-on-new-game question is untouched by this package** — since
  no automatic trigger exists yet, when exactly a *new* run's count starts at zero (vs. an
  abandoned run's own final count silently persisting) is part of the same `OQ3`/`BL-0112`
  question a future package resolves, not decided here; `IP-1100`'s own `INFINITE SEED ENTRY`
  A-confirm does not currently reset it (an honest gap, not silently patched around).
- ROM budget: small — two WRAM constants, one dispatch branch, one small subroutine.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `check_collisions`'s existing `KeyItem`/
`ScoreItem` branches, never modified inline (only a new branch added alongside them), are
unaffected. No save-format change in this package (`IP-1104`'s scope, though `IP-1104` persists
this package's own `RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE` fields).
