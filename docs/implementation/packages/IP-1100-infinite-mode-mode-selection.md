# IP-1100 — Infinite Mode: Mode Selection & New-Game Entry

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1100` — implements part of [**FS-110**](../../features/FS-110-infinite-mode.md) (`FEAT-10000`,
Epic `EP-6000`, `Future` bucket). Covers Workflow A only. First of five packages in the Infinite
Mode tranche — see the [Technical Work Breakdown](../01-technical-work-breakdown.md)'s "Infinite
Mode" section for the full split rationale and sequencing.

## 2. Objective

Add a `MODE SELECT` cursor menu (finite/infinite) between `MAIN MENU`'s "new game" option and the
existing `SEED/SCALE ENTRY` flow, plus a new seed-only `INFINITE SEED ENTRY` state for the
Infinite Mode path — implementing [GDS-01](../../architecture/01-concept-of-play.md) §4d exactly,
including its deliberate asymmetric-cancel-path tradeoff (`SEED/SCALE ENTRY`'s own shipped
`IP-1040` B-cancel target is not redirected).

## 3. Requirements Covered

FR-10100 (mode choice at new-game creation, seed only, no scale step).

## 4. Architecture Components

[GDS-01](../../architecture/01-concept-of-play.md) §4d (this package's exact source diagram and
named tradeoff) · [ADR-0010](../../architecture/adr/ADR-0010-seed-scale-model.md) (digit-cursor
input convention, reused for the seed-only field) · [ADR-0016](../../architecture/adr/ADR-0016-streaming-infinite-mode-generation-architecture.md)
(Infinite Mode has no `WorldScale` — this package's own reason `INFINITE SEED ENTRY` has no scale
digit).

## 5. Interfaces

- **`IP-1040`'s existing cursor-menu convention** (`MM_CURSOR`-style D-pad up/down toggle, A
  confirms) — reused for `MODE SELECT`'s finite/infinite choice, not reinvented.
- **`IP-1040`'s existing digit-cursor picker** (`SSE_DIGITS`/`SSE_CURSOR`) — reused for
  `INFINITE SEED ENTRY`'s seed-only field (the picker's seed-digit half only; no scale slot is
  ever entered). `SSE_DIGITS`/`SSE_CURSOR` are safe to reuse because `GS_SEED_SCALE_ENTRY` and
  `GS_INFINITE_SEED_ENTRY` are never simultaneously active — mirrors `MM_CURSOR`'s own reuse for
  `GS_SELECT_MENU` (`IP-1090`).
- **`IP-1101`'s per-region materialization routine** (this tranche's own `IP-1101`, not yet
  `VERIFIED` — see Dependencies) — called once, on `INFINITE SEED ENTRY`'s A-confirm, to
  materialize the starting region `(0,0)` before the first `PLAYING` frame, mirroring
  `IP-1040`'s own `generate_world` call-site pattern exactly.
- **New `patches` dict keys** (GDS-09 delta, parallel to `IP-1040`'s own `mm_t`/`sse_t` pattern):
  `ms_t`/`ms_a` (`MODE SELECT` screen) and `ise_t`/`ise_a` (`INFINITE SEED ENTRY` screen).

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constant:** `GAME_MODE = 0xC3F6` (1 byte; 0=finite, default, 1=infinite) — first
    unclaimed byte past `GW_KI_PLACED` (`0xC3F5`, `IP-1021`'s own last WRAM addition).
  - **Game-state constants:** add `GS_MODE_SELECT = 10`, `GS_INFINITE_SEED_ENTRY = 11` (the next
    two free values after `GS_SELECT_MENU=8`/`GS_LEGEND=9`, `asm_game.py:174-175`, per
    `GDS-01` §4d's own explicit note).
  - **Main dispatch loop:** add dispatch entries for both new states, following the existing
    `CP_n(GS_x); JP_Z('st_x')` pattern.
  - **`st_main_menu`'s "new game" branch (existing label):** retarget from
    `GS_SEED_SCALE_ENTRY` directly to `GS_MODE_SELECT`. **`st_seed_scale_entry`'s own B-cancel
    target is left unchanged (`GS_MAIN_MENU`)** — per `GDS-01` §4d's own named tradeoff, not
    redirected through `MODE SELECT`.
  - **`st_mode_select` (new label):** on entry, presents "finite"/"infinite", cursor-selected via
    the reused `MM_CURSOR`-style toggle (exact WRAM byte reused — `MM_CURSOR` itself, since
    `GS_MAIN_MENU` and `GS_MODE_SELECT` are never simultaneously active, mirroring `GDS-01` §4d's
    own explicit "implementation-level" carve-out — or a new dedicated byte, an implementation
    choice left open here exactly as `GDS-01` §4c left the identical choice open for
    `GS_SELECT_MENU`). D-pad up/down toggles; A confirms: "finite" → `GS_SEED_SCALE_ENTRY`
    (unchanged); "infinite" → `GS_INFINITE_SEED_ENTRY`, writing `GAME_MODE = 1` on this transition
    only (not on mere highlight). B cancels directly to `GS_MAIN_MENU`, writing nothing.
  - **`st_infinite_seed_entry` (new label):** digit-cursor picker over the same 5-digit seed field
    `SSE_DIGITS` already provides (0–65535, `SSE_CURSOR` values 0-4 only — no scale slot, value 5
    is never reached from this state). A confirms: composes `SEED` via the existing
    `sse_compose_seed` routine (`IP-1040`, reused verbatim — seed composition doesn't care which
    mode is entering it), normalizes 0→1 (existing `ADR-0010` rule, unchanged), calls `IP-1101`'s
    materialization routine for `(row=0, col=0)`, writes `INF_ROW=0`/`INF_COL=0`, transitions to
    `GS_INTRO`. B cancels to `GS_MODE_SELECT` (not `GS_MAIN_MENU` — this state has no shipped
    precedent to protect, per `GDS-01` §4d's own "one step back" framing for this specific state),
    writing nothing (`GAME_MODE` is left at whatever `st_mode_select`'s own transition set it to
    — re-entering `MODE SELECT` and choosing "finite" instead is the only way to change it before
    a game starts).
  - **`st_victory`'s existing `CARROTS_COUNT==9` victory-check gate:** unchanged, but confirmed
    (Files-to-Modify audit, not a code change) to run only from the finite mode's own `PLAYING`
    loop shape — `GAME_MODE` is not read here in this package; `IP-1103` is the package that must
    confirm this check does not spuriously fire for Infinite Mode saves (named as a dependency
    note, not resolved here).
- **Modify: `tilemaps.py`** — two new screen-generator functions: `mode_select_screen()` (reuses
  `MAIN MENU`'s own cursor-highlight/text primitives, no new tiles) and
  `infinite_seed_entry_screen()` (reuses `seed_scale_entry_screen()`'s own digit-cursor layout
  primitives minus the scale slot, no new tiles); both registered in `ALL_SCREENS` (parallel to
  the existing `mm`/`sse` entries, not the 5 biome-family entries `IP-1030` manages).
- **Modify: `build_rom.py`** — the two new screens' `patches` keys (§5) resolved after
  `build_game_asm()` returns, following the exact existing `mm_t`/`mm_a` pattern.
- **Modify: `test_rom.py`** — add suite **T22** (see §8).

## 7. Implementation Tasks

Ordered: (1) `GAME_MODE` WRAM constant; (2) `GS_MODE_SELECT`/`GS_INFINITE_SEED_ENTRY` constants +
dispatch entries; (3) `st_main_menu`'s "new game" retarget; (4) `st_mode_select` (cursor toggle,
A-confirm branch, B-cancel); (5) `st_infinite_seed_entry` (digit-cursor reuse, A-confirm →
`IP-1101` call → `INTRO`, B-cancel to `MODE SELECT`); (6) two new screen-generator functions +
`ALL_SCREENS`/`patches` registration; (7) rebuild ROM; (8) author T22; (9) full suite run; (10)
documentation/traceability updates (§9).

**Blocked on `IP-1101` existing** for task (5)'s A-confirm call site and task (8)'s materialization
assertions — `IP-1100` cannot reach `COMPLETE` before `IP-1101` does, per the Dependencies field
below, even though most of this package's own files are independently writable.

## 8. Tests to Add

New `test_rom.py` suite **`T22: Infinite Mode — Mode Selection & New-Game Entry`**:

- T22.a1/a2 — from `GS_MAIN_MENU`, select "new game" → assert `GameState == GS_MODE_SELECT`
  (not `GS_SEED_SCALE_ENTRY` directly); D-pad toggle moves the highlight between finite/infinite.
- T22.b1 — `MODE SELECT`, confirm "finite" → assert `GameState == GS_SEED_SCALE_ENTRY`,
  `GAME_MODE == 0` — and that `SEED/SCALE ENTRY`'s own B-cancel still returns to `GS_MAIN_MENU`
  directly (regression check: `GDS-01` §4d's named asymmetric-tradeoff is actually shipped as
  specified, not accidentally routed through `MODE SELECT`).
- T22.b2 — `MODE SELECT`, confirm "infinite" → assert `GameState == GS_INFINITE_SEED_ENTRY`,
  `GAME_MODE == 1`.
- T22.c1 — `MODE SELECT`, press B → assert `GameState == GS_MAIN_MENU`, `GAME_MODE` unchanged
  from its prior value (nothing written on cancel).
- T22.d1/d2 — `INFINITE SEED ENTRY`, drive digit-cursor entry for a known seed, confirm via A →
  assert `GameState == GS_INTRO`, `SEED` equals the entered value, `INF_ROW == 0`,
  `INF_COL == 0`, and the starting region's materialized data (`IP-1101`'s own output shape) is
  present in `INF_WINDOW` (delegates the actual biome/connectivity correctness check to `IP-1101`'s
  own T23 suite).
- T22.e1 — `INFINITE SEED ENTRY`, press B → assert `GameState == GS_MODE_SELECT` (not
  `GS_MAIN_MENU`), `SEED`/`GAME_MODE` unchanged.
- T22.f — seed = 0 entered → assert `SEED` normalized to 1 (existing `ADR-0010` rule, exercised
  through the new entry path).

## 9. Documentation Updates

- `docs/architecture/01-concept-of-play.md` (GDS-01): confirm §4d's target-state diagram as
  shipped (a "confirmed, implemented" note, not a new section).
- `docs/requirements/01-functional-requirements.md`: FR-10100 status → Implemented (mode-choice
  half only — FR-10100 also covers region materialization, `IP-1101`'s own scope).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-10100 row → `IP-1100`/T22.
- `docs/features/FS-110-infinite-mode.md` metadata: implemented-by pointer for Workflow A;
  §19 Open Question 6 marked Resolved (already resolved at `GDS-01` §4d — this package confirms
  it shipped as specified).
- Master Build Plan status row.

## 10. Definition of Done

- Both new states (`GS_MODE_SELECT`, `GS_INFINITE_SEED_ENTRY`) reachable and behave exactly per
  `GDS-01` §4d's diagram, including the named asymmetric-cancel-path tradeoff.
- ROM builds at 32768 bytes; full suite passes.
- `SEED/SCALE ENTRY`'s own shipped (`IP-1040`) behavior is provably unchanged (T22.b1's own
  regression check).
- FR-10100's mode-choice half is demonstrably Implemented via T22.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T22.a1–f each present and passing.
- [ ] Direct code read: `st_seed_scale_entry`'s B-cancel target is still `GS_MAIN_MENU` — no
      accidental redirect through `GS_MODE_SELECT` (the named tradeoff, confirmed shipped as
      specified, not silently "fixed" into symmetry during implementation).
- [ ] Direct code read: `st_mode_select`'s B-cancel writes no `GAME_MODE`/`SEED` value.
- [ ] Direct code read: `INFINITE SEED ENTRY`'s A-confirm calls `IP-1101`'s materialization
      routine for `(0,0)` exactly once, not on every frame `GS_INTRO` is drawn.
- [ ] GDS-01/FR-10100/RTM/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1101`** (this tranche's own per-region materialization package, **NOT YET
  `VERIFIED`/`COMPLETE`/authored-as-code** — `IP-1100`'s task (5)/(8) call it directly). `IP-1100`
  cannot reach `COMPLETE` before `IP-1101` does.
- **`IP-1040`/`FEAT-1100`** (`VERIFIED`) — the cursor-menu and digit-cursor-picker conventions this
  package reuses verbatim, plus `sse_compose_seed`.
- **`IP-1090`/`FEAT-1200`** (`VERIFIED`) — the `MM_CURSOR`/`GAME_MODE`-adjacent-byte-reuse
  precedent this package's own `st_mode_select` cursor-byte choice mirrors.

Independent of `IP-1102`/`IP-1103`/`IP-1104` (no shared file region — parallel-eligible with all
three once `IP-1101` is `COMPLETE`).

## 13. Risks

- **Cursor-byte reuse choice left open** (Low) — mirrors `GDS-01` §4c's own identical, already-
  accepted precedent; a well-isolated single-byte decision, not a structural risk either way.
- **The asymmetric-cancel-path tradeoff is a deliberate, named design choice, not a defect** —
  T22.b1 exists specifically to catch an implementer "fixing" it into symmetry, which would
  silently touch `IP-1040`'s own already-`VERIFIED` code path.
- ROM budget: two new screens (mode select, infinite seed entry), reusing existing text/cursor/
  digit primitives — modest addition, expected well within existing headroom (re-affirmed at
  build time, not asserted here).

## 14. Rollback Considerations

Revert `asm_game.py`/`tilemaps.py`/`build_rom.py`/`test_rom.py` changes and rebuild. `MAIN MENU`'s
"new game" option reverts to its pre-existing direct `GS_SEED_SCALE_ENTRY` target; the finite
mode's own flow is completely unaffected either way (never modified by this package, only its
entry point's predecessor state). No save-format change in this package (`IP-1104`'s scope) —
existing saves remain loadable by the reverted-from build unchanged.
