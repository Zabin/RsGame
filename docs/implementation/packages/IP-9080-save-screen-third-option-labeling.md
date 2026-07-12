# IP-9080 — SAVE Screen Third-Option Labeling

> Owned by `07-implementation-planning` (definition) / `08-content-authoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9080` — bug-remediation series; no FS. Source: **`BL-0049`** (filed via `00-intake`, this
session).

## 2. Objective

Add on-screen text for the SAVE screen's third option (`SELECT`: save-and-exit-to-MAIN-MENU) —
today silent, discoverable only by accident. `st_save`'s own input handling (`asm_game.py:319-339`)
already correctly implements the option's behavior (`IP-1040`); only the missing label is fixed
here.

## 3. Requirements Covered

`FR-1190` (Exit-to-main-menu with auto-save, confirmed in
`docs/requirements/01-functional-requirements.md`). This package fixes a presentation-completeness
gap in the shipped implementation, not the requirement text — the underlying behavior (`SELECT`
saves and exits) was already correct and already tested (`T14.d0`/`T14.d1`); only its on-screen
discoverability was missing.

## 4. Architecture Components

GDS-08 (Presentation Architecture) — the SAVE screen's existing text-and-border layout
(`save_screen`, `tilemaps.py:303-311`) is the direct precedent this addition extends; no new tile
art, no new palette entry (reuses the screen's own existing font tiles and palette 2, identical to
its two existing text lines).

## 5. Interfaces

None new. `tilemaps.py`'s existing `_str()` helper (`tilemaps.py:23-25`) — the same call
`save_screen`'s own two existing lines (`"A: YES"`, `"B: NO"`) already use.

## 6. Files to Create/Modify

- **Modify: `tilemaps.py`**:
  - **`save_screen`** (`tilemaps.py:303-311`): add one new `_str()` call for the third option's
    label, placed within the screen's existing bordered content area (columns 2–17, the same
    horizontal border the two existing lines already respect — `save_screen`'s own
    `for x in range(2, 18): _put(..., TL_BORDER_H, 2)` calls at rows 3/14) and below the existing
    `"B: NO"` line at row 11, above the bottom border at row 14 (rows 12–13 are currently unused).
  - **UI-input-mapping question resolved directly** (per this stage's own precedent, `FS-104` OQ2):
    the existing `A`/`B`/`SELECT` one-button-per-option scheme is **not** redesigned into a
    cursor-based UP/DOWN-select/A-confirm scheme matching MAIN MENU's own convention — see the
    TWBS's own "UI-input-mapping question resolved directly" note for the full rationale (a
    working three-fixed-option scheme doesn't need a control-model redesign to fix a missing
    label). `asm_game.py`'s `st_save` is **not modified** by this package.
  - **Exact wording and column placement is this package's own content-authoring judgment call**
    (per `07-implementation-planning`'s own "behavior, not implementation" discipline — a literal
    pixel/column layout is implementation-level detail for the executing package, not dictated
    here). Constraints that do bind: (a) the label must clearly convey both effects of the
    `SELECT` option — the game **is saved**, and the state **exits to MAIN MENU** (not merely
    "exit," which could read as discarding the game, exactly the ambiguity a bare "EXIT" label
    would introduce); (b) the label must fit within the screen's existing bordered content area
    (columns 2–17) without visually colliding with the border tiles at column 2 or column 17; (c)
    the label's row must fall between the existing `"B: NO"` line (row 11) and the bottom border
    (row 14), i.e. row 12 or row 13. Two non-binding candidate phrasings, for reference only:
    `"SELECT: SAVE+EXIT"` (may need splitting across two short lines to fit the column budget) or
    a two-line form such as `"SELECT: SAVE"` / `"AND EXIT"`.

## 7. Implementation Tasks

Ordered: (1) decide the exact wording/placement within the constraints named in §6; (2) add the
new `_str()` call(s) to `save_screen`; (3) rebuild ROM; (4) confirm visually (or via a direct
tilemap-byte read) that the new text renders within the border and does not overlap the existing
two lines; (5) author the new test check (§8); (6) full suite run; (7) documentation/traceability
updates (§9).

## 8. Tests to Add

Extends the existing **`T5: BG Tilemap`** suite (`test_rom.py`) — no new suite number, since this
is presentation-content coverage of an already-tested screen family:

- **T5.x — SAVE screen's third-option text is present**: enter `GS_SAVE` (mirroring `T14.d0`'s own
  entry path — press START from PLAYING); read the tilemap rows the package's own §6 placement
  names (rows 12–13, columns 2–17); confirm at least one font tile (`TL_FONT_A`..`TL_FONT_COLON`
  range, the same test pattern `T5.2`/`T5.3b` already use for MAIN MENU's own text) is present in
  that region, and that it does not overlap the existing `"A: YES"`/`"B: NO"` rows (9/11) or the
  bottom border row (14).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: add a Notes entry to `FR-1190` recording that
  the third option's on-screen text now exists, citing `BL-0049`.
- `docs/requirements/04-requirements-traceability-matrix.md`: update `FR-1190`'s Test cell to cite
  the new `T5.x` check.
- Master Build Plan status row.

## 10. Definition of Done

- The SAVE screen's third (`SELECT`) option has on-screen text unambiguously describing "save and
  exit," within the screen's existing bordered layout, not overlapping the existing two lines.
- `T5.x` demonstrably passes; no other `T5` check regresses.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct tilemap-byte read: the new text occupies only rows 12–13, columns 2–17 (no border/
      existing-line collision).
- [ ] `asm_game.py` unmodified by this package (content-only, per §6's UI-input-mapping decision).
- [ ] `T5.x` present and passing.
- [ ] Requirements/RTM deltas applied exactly as §9 names.

## 12. Dependencies

None. Independent of every other package in-flight this session (see TWBS Sequencing summary) —
parallel-eligible with `IP-9090`/`IP-9100` (different file, `08-content-authoring` vs.
`08-code-implementation`).

## 13. Risks

- **Low.** A pure content addition to an already-simple, already-tile-budget-comfortable screen
  (no new tile art, no new palette entry, reuses existing font tiles).
- ROM budget: negligible (a handful of existing-font tile placements in an already-allocated
  screen's tilemap, no new tile-index or palette-table entries).

## 14. Rollback Considerations

Revert `tilemaps.py`'s `save_screen` addition and rebuild. Reverts to the shipped (silent
third-option) behavior exactly; no save-format dependency, no data-corruption risk (this is a
presentation-only change, the option's own underlying save/exit behavior is untouched either way).
