# IP-1040 — Main Menu & New-Game Flow

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1040` — implements
[**FS-104**](../../features/FS-104-main-menu-new-game-flow.md) (`FEAT-1100`, Epic EP-1000,
Release 2). Resolves FS-104 Open Questions 1–2 — see the
[Technical Work Breakdown](../01-technical-work-breakdown.md)'s "Deferred design decisions
resolved in this pass."

## 2. Objective

Add MAIN MENU and SEED/SCALE ENTRY states to the game-state machine, retiring the shipped
auto-load-on-boot bypass in favor of a menu-driven continue/new-game choice; add a third
exit-to-main-menu option (with auto-save) to the existing SAVE state.

## 3. Requirements Covered

FR-1170, FR-1180, FR-1190 (FS-104's full Included-Requirements set).

## 4. Architecture Components

GDS-01 §2a/3a/4a (target-state game-flow delta — this package's exact source diagram) · ADR-0009
(this package's SEED/SCALE ENTRY confirm action invokes IP-1020's generation routine) · ADR-0010
(seed & scale entry surface, digit-cursor picker, immutability rule, pre-upgrade-save "continue"
exclusion).

## 5. Interfaces

- **New `patches` dict keys** (GDS-09 delta, cited verbatim: "a patch point for the seed/scale-
  entry screen's tile/attribute addresses, parallel to today's `title_t`/`title_a` pattern"):
  `mm_t`/`mm_a` (main menu screen) and `sse_t`/`sse_a` (seed/scale entry screen), following the
  existing pattern exactly.
- **`IP-1020`'s `generate_world` routine** — called once, from the SEED/SCALE ENTRY confirm
  action (this package supplies the call site; `IP-1020` supplies the routine itself).
- **The existing save-write routine** (`FR-5100`, unchanged) — called from the new
  exit-to-main-menu option, exactly as the existing SAVE-state A(save) option already calls it.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **Game-state constants**: add `GS_MAIN_MENU` and `GS_SEED_SCALE_ENTRY` (following the
    existing `GS_TITLE`/`GS_INTRO`/… numbering convention, extending the state count).
  - **Main dispatch loop**: add dispatch entries for the two new states, following the existing
    `CP_n(GS_x); JP_Z('st_x')` pattern per state.
  - **Boot sequence**: replace the existing unconditional `try_load_save` call at boot with an
    unconditional transition to `GS_MAIN_MENU` — `try_load_save`'s call moves to become
    MAIN MENU's "continue" action only (retiring the auto-load bypass, ADR-0009/GDS-01 §2a).
  - **`st_main_menu` (new label)**: on entry, check save-validity (calls the existing magic/
    version check, without yet restoring fields — a read-only validity probe, or restores fully
    but discards if the player picks "new game," an implementation choice left to
    `08-code-implementation` since FS-104 doesn't fix which). D-pad up/down toggles the
    highlighted option between "continue" (rendered only if a valid save exists) and "new game";
    A confirms the highlighted option. "Continue" → full `try_load_save` restore → `GS_PLAYING`.
    "New game" → `GS_SEED_SCALE_ENTRY`.
  - **`st_seed_scale_entry` (new label)**: digit-cursor picker over a 5-digit seed field (0–65535)
    and a 1-digit scale field (2–9, default 3) — D-pad up/down changes the highlighted
    digit/value, left/right moves the cursor between fields, A confirms, **B cancels back to
    `GS_MAIN_MENU`** (resolves FS-104 Open Question 1). On A-confirm: write `SEED`/`WORLD_SCALE`
    WRAM (0 seed normalized to 1 per ADR-0010 — this normalization happens here or inside
    `IP-1020`'s `generate_world`, an implementation choice left to `08-code-implementation`
    since both packages land together); call `generate_world` (`IP-1020`); transition to
    `GS_INTRO`.
  - **`st_save`'s existing A/B branch** (existing label): add a third input check for the
    exit-to-main-menu option (a new button/menu-position, e.g. SELECT or a third cursor
    position — implementation detail left to `08-code-implementation`); on select: call the
    existing save-write routine (unconditionally, exactly as A already does), then transition to
    `GS_MAIN_MENU` instead of `GS_PLAYING`.
  - **`st_victory`'s A-press target** (existing label): change from `GS_TITLE` to `GS_MAIN_MENU`.
- **Modify: `tilemaps.py`** — two new screen-generator functions: `main_menu_screen()` (reuses
  existing digit/cursor/font tile primitives, per D1 — no new tiles) and
  `seed_scale_entry_screen()` (digit-cursor picker layout, same tile primitives); both registered
  in `ALL_SCREENS` (parallel to the existing title/intro/save/map/victory entries, not the 5
  biome-family entries `IP-1030` manages).
- **Modify: `build_rom.py`** — the two new screens' `patches` keys (§5) resolved after
  `build_game_asm()` returns, following the exact existing `title_t`/`title_a` pattern.
- **Modify: `test_rom.py`** — add suite **T13** (see §8).

## 7. Implementation Tasks

Ordered: (1) game-state constants + dispatch entries; (2) boot-sequence change (auto-load bypass
→ unconditional MAIN MENU); (3) `st_main_menu` (option-set logic, input handling, transitions);
(4) `st_seed_scale_entry` (digit-cursor input, B-cancel, A-confirm → `generate_world` call →
INTRO); (5) `st_save`'s third exit-to-main-menu option; (6) `st_victory`'s target-state change;
(7) two new screen-generator functions + `ALL_SCREENS`/`patches` registration; (8) rebuild ROM;
(9) author T13, including the FR-9110 negative-test sweep (§8); (10) full suite run; (11)
documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T13: Main Menu & New-Game Flow`**, implementing FS-104's Verification
Plan:

- T13.a1/a2 — boot with no save present → assert `GameState == GS_MAIN_MENU`, "continue" option
  absent (AC-1/AC-2 forward half).
- T13.a3 — boot with a valid version-matching save present → assert `GameState == GS_MAIN_MENU`
  (not `GS_PLAYING`, confirming the auto-load bypass is actually retired), "continue" present
  (AC-1/AC-2 reverse half).
- T13.a4 — boot with a synthetic pre-upgrade (version-mismatched) save (`IP-1010`'s T11.d
  pattern) → assert "continue" absent.
- T13.b1/b2 — drive digit-cursor entry for a known `(seed, scale)`, confirm via A → assert
  `GameState == GS_INTRO`, region count equals `scale²` (AC-3).
- T13.b3 — repeat the same `(seed, scale)` pair in a fresh new-game creation → assert identical
  region-graph output (AC-4, delegating the actual comparison to IP-1020's T12.b).
- T13.c1 — SEED/SCALE ENTRY, press B → assert `GameState == GS_MAIN_MENU` (Open Question 1's
  resolution, tested directly).
- T13.d1/d2 — from `GS_PLAYING` with known state, START → SAVE → exit-to-main-menu → assert
  `GameState == GS_MAIN_MENU`; reload via "continue" → assert restored state matches exactly
  (AC-5/AC-6, extending T10's save/reload harness).
- T13.e — **FR-9110 negative-test sweep**: from `GS_PLAYING`, `GS_SAVE`, and `GS_MAP`, attempt
  every reachable input sequence; assert none writes `SEED`/`WORLD_SCALE` (a systematic sweep
  over the existing input-handling branches in each state, not a single spot check).

## 9. Documentation Updates

- `docs/architecture/01-concept-of-play.md` (GDS-01): confirm §2a/3a/4a's target-state diagram
  as shipped (a "confirmed, implemented" note on the existing delta, not a new section).
- `docs/requirements/01-functional-requirements.md`: FR-1170/1180/1190 status → Implemented;
  FR-1120's own text gets a forward-pointer note that its auto-load-bypass behavior is now
  superseded by this package (a metadata note, not a rewrite of FR-1120's postcondition — that
  correction, if any is needed, is a future `04` delta's call, per this skill's own SHALL-NOT
  rule against modifying requirements).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-1170/1180/1190 rows → IP-1040/
  T13.
- `docs/features/FS-104-…md` metadata: implemented-by pointer; §19 Open Questions marked
  Resolved with this package's decisions.
- Master Build Plan status row.

## 10. Definition of Done

- All six FS-104 Acceptance Criteria demonstrably pass via T13.
- ROM builds at 32768 bytes; full suite passes.
- The auto-load bypass (FR-1120's shipped behavior) no longer exists in the tree — boot always
  reaches MAIN MENU, confirmed by T13.a3's direct regression check.
- FR-9110's immutability rule holds against every reachable input sequence (T13.e).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T13.a1–e each present and passing (map 1:1 to FS-104 AC-1…6 plus the FR-9110 negative test).
- [ ] Direct code read: `try_load_save`'s call site is now MAIN MENU's "continue" action only —
      no unconditional call remains anywhere in the boot sequence.
- [ ] Direct code read: SEED/SCALE ENTRY's B-cancel returns to MAIN MENU without writing
      `SEED`/`WORLD_SCALE` (confirms Open Question 1's resolution didn't introduce a partial
      write on cancel).
- [ ] Direct code read: SAVE's exit-to-main-menu option calls the exact same save-write routine
      A(save) already calls — no duplicated/divergent save-write logic.
- [ ] GDS-01/FR-1170/1180/1190/RQ-04/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1020** (triggers its `generate_world` routine on new-game confirm) — this tranche's
  foundational predecessor.
- **IP-9010, IP-9020, IP-9030, IP-9040, IP-1010** (all `VERIFIED`) — the trustworthy suite and
  the existing save-write mechanism this package's exit-to-main-menu option reuses.

Independent of IP-1030/IP-1031/IP-1050 (parallel-eligible, per FP-04/TWBS).

## 13. Risks

- **Retiring FR-1120's auto-load bypass is a deliberate protected-baseline change** (Medium,
  carried from FEAT-1100's own catalog assessment) — mitigated by T13.a3's direct regression
  check and T13.e's systematic negative-test sweep for FR-9110.
- **Open Question 1's B-cancel convention** is this package's own confident resolution, not
  upstream-mandated — if a future design pass wants different behavior, it is a well-isolated
  single input branch to change, not a structural risk.
- ROM budget: two new screens (main menu, seed/scale entry) — modest addition, expected well
  within existing headroom (re-affirmed against `NFR-4000` at build time, not asserted here).

## 14. Rollback Considerations

Revert `asm_game.py`/`tilemaps.py`/`build_rom.py`/`test_rom.py` changes and rebuild. Reverts to
the shipped auto-load-bypass behavior exactly. No save-format change in this package (IP-1050's
scope) — existing saves remain loadable by the reverted-from build unchanged.
