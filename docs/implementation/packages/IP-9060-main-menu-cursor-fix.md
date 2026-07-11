# IP-9060 — Main Menu Cursor Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9060` — bug-remediation series; no FS. Source: **`BL-0048`** (High, project owner
playtesting, filed via `00-intake`).

## 2. Objective

Stop `check_save_valid`'s `MM_CURSOR`-reset side effect from firing on every MAIN MENU redraw —
including the redraw the player's own UP/DOWN toggle causes — so "new game" becomes selectable
again whenever a valid save exists.

## 3. Requirements Covered

`FR-1170` (MAIN MENU state) — this package fixes a regression in its own shipped implementation;
no new requirement, no requirement text change (the requirement itself, "highlighted option
toggles between continue/new-game," was always correct — the implementation silently violated it
in one specific cell, exactly the untested `(save present) × (select new-game)` cell `R305`'s
2026-07-11 delta (`BL-0057`) names).

## 4. Architecture Components

GDS-01 §2a/3a/4a (MAIN MENU target-state diagram — unchanged by this fix, since the *intended*
behavior already matches it; only the implementation's own internal side effect is wrong).

## 5. Interfaces

None new. Internal fix within the existing `mm_on_entry`/`check_save_valid`/`draw_menu_cursor`
call chain (`asm_game.py:855-883`) — no change to any WRAM address, GDS-09 contract, or the
`st_main_menu` input-handling entry points `IP-1040` already established.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`check_save_valid`** (`asm_game.py:1290`): remove its own `MM_CURSOR`-reset tail
    (`csv_cur_cont`/`csv_cur_set` — the unconditional "if a valid save exists, force `MM_CURSOR`
    to `0`" logic at the end of the routine). `check_save_valid` becomes exactly what its name
    says: it computes `MM_SAVE_VALID` and nothing else.
  - **`mm_on_entry`** (`asm_game.py:865`): the `MM_CURSOR`-to-default reset moves here, but is
    gated on **genuine state entry**, not every redraw. Concretely: add a new 1-byte WRAM flag
    (or reuse the existing state-transition machinery — `check_zone_transition`'s own
    `TRANSITION_TO`/`GAMESTATE` distinction already tells the dispatcher "did we just arrive at
    this state, or are we redrawing within it" one frame earlier, at `do_screen_redraw`'s own
    call site) so `mm_on_entry` can tell the two cases apart: on genuine entry (boot into MAIN
    MENU, arrival from VICTORY, arrival from SAVE's exit-to-main-menu option), reset `MM_CURSOR`
    to its default (`0` if a valid save exists, `1` otherwise — the existing, correct default
    logic); on a same-state redraw triggered by the player's own toggle (`st_main_menu`'s
    `mm_toggle` path), skip the reset entirely and just re-draw the cursor at `MM_CURSOR`'s
    current (just-toggled) value.
  - **`st_main_menu`**'s toggle path (`asm_game.py:317-324`, `mm_toggle`): unchanged — it already
    correctly writes `MM_CURSOR` before setting `NEED_REDRAW`; the bug is entirely in what runs
    *after* that write, not in the toggle logic itself.

## 7. Implementation Tasks

Ordered: (1) add the entry-vs-redraw distinction (a new 1-byte flag, e.g. `MM_JUST_ENTERED`, set
by whatever transitions `GAMESTATE` to `GS_MAIN_MENU` — boot, VICTORY's A-press, SAVE's SELECT
option — and cleared by `mm_on_entry` itself after consuming it); (2) remove
`check_save_valid`'s own `MM_CURSOR`-reset tail; (3) gate `mm_on_entry`'s `MM_CURSOR` reset on the
new flag; (4) confirm the toggle path (`mm_toggle`) still calls `mm_on_entry` (for the redraw/
cursor-draw side) but no longer has its own toggle silently undone; (5) rebuild ROM; (6) author
T18 (see §8), including the exact previously-untested cell (`R305`'s `BL-0057` delta, gap 3); (7)
full suite run; (8) documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T18: Main Menu Cursor Fix`** — the direct regression test for the
exact untested `(entry-condition × action)` cell `R305`'s 2026-07-11 delta (`BL-0057`, gap 3)
named:

- **T18.a — toggle with a valid save present (the direct `BL-0048` regression test)**: boot with
  a valid save, confirm `MM_CURSOR == 0`; press DOWN, confirm `MM_CURSOR == 1`; press DOWN again,
  confirm `MM_CURSOR == 0` (wraps); press UP, confirm `MM_CURSOR == 1`. Every step asserts the
  *exact* value, not just "changed" — per `R305`'s boundary-assertion convention (gap 2).
- **T18.b — toggle with no save present**: boot with no save, confirm `MM_CURSOR == 1` (forced,
  "continue" not offered); UP/DOWN presses are no-ops (`mm_toggle`'s own existing
  `MM_SAVE_VALID`-gate, unchanged by this package) — confirm `MM_CURSOR` stays `1`.
- **T18.c — genuine re-entry still resets correctly**: from MAIN MENU with `MM_CURSOR` toggled to
  `1` (new game highlighted), navigate away and back to MAIN MENU via a genuine state-entry path
  (e.g. SEED/SCALE ENTRY's B-cancel, `T14.c1`'s existing path) — confirm `MM_CURSOR` resets to
  its correct entry default, proving the fix didn't simply delete the reset, only mis-scoped it.
- **T18.d — "new game" is actually reachable end-to-end**: from T18.a's toggled state
  (`MM_CURSOR == 1`), press A, confirm `GameState` transitions to `GS_SEED_SCALE_ENTRY` — the
  full regression test proving the reported symptom ("not possible to select new game") is
  resolved, not just that the byte value changes.

## 9. Documentation Updates

- `docs/architecture/01-concept-of-play.md` (GDS-01): no change expected (the target-state
  diagram already describes the correct, now-actually-achieved behavior) — confirm during
  authoring, note only if a gap is found.
- Master Build Plan status row.

## 10. Definition of Done

- `check_save_valid` no longer writes `MM_CURSOR` under any circumstance.
- `MM_CURSOR` resets to its default only on genuine MAIN MENU state entry, never on a same-state
  redraw the player's own toggle causes.
- T18.a-d demonstrably pass; "new game" is reachable from MAIN MENU whenever a save exists.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T18.a–d each present and passing.
- [ ] Direct code read: `check_save_valid`'s body contains no `MM_CURSOR` write.
- [ ] Direct code read: `mm_on_entry`'s `MM_CURSOR`-reset is gated on the entry-vs-redraw
      distinction, not unconditional.
- [ ] Direct code read: every `GAMESTATE → GS_MAIN_MENU` transition site sets the new entry flag
      (boot, `st_victory`'s A-press, `st_save`'s SELECT option) — none silently bypasses it.
- [ ] GDS-01/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1040** (`VERIFIED`, `MM_CURSOR`/`check_save_valid`/`mm_on_entry`'s own shipped
  implementation this package fixes).

Independent of `IP-9050`/`IP-9070` (parallel-eligible — unrelated file region, no shared root
cause).

## 13. Risks

- **Low.** A contained, well-understood fix to a single side effect; the toggle logic itself is
  already correct and untouched.
- ROM budget: one new 1-byte WRAM flag, negligible.

## 14. Rollback Considerations

Revert `asm_game.py`'s `check_save_valid`/`mm_on_entry` changes and rebuild. Reverts to the
shipped (buggy — cursor stuck at "continue") behavior exactly; no save-format dependency, no
data-corruption risk in either direction (this fix touches only in-session WRAM cursor state, not
persisted save data).
