# IP-9180 — Infinite Mode HUD Target-Digit Convention (`BL-0144`)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9180` — remediation package for [`BL-0144`](../../pipeline/backlog.md) (the Infinite-Mode-HUD
design question `IP-9170` split off `BL-0139` to answer separately): Infinite Mode's HUD col-4
cell has no fixed carrot ceiling to display, and previously showed whatever the last-drawn
screen's `_score_bar` happened to bake there. **User decision, 2026-07-17: show the running
treasure count.**

## 2. Objective

During Infinite Mode `PLAYING`, the HUD's row-0/col-4 cell shows the current run's
`RUNNING_TREASURE_COUNT` (low decimal digit — see §13's own named single-cell constraint),
replacing whatever stale value `_score_bar` baked there.

## 3. Requirements Covered

None directly (no FR/NFR describes this HUD cell). Companion to `IP-9170`'s own `FR-9161` Notes
entry — this package's own Documentation Updates (§9) adds the matching Infinite Mode half.

## 4. Architecture Components

None new. Continues `IP-9170`'s own precedent of converting a baked HUD cell to a runtime write
inside the already-`VERIFIED` `update_status_disp` routine; no `GDS-08`/`GDS-07` delta beyond a
Notes-level update (no new WRAM address — `RUNNING_TREASURE_COUNT`, `0xC405`, already exists).

## 5. Interfaces

- **`RUNNING_TREASURE_COUNT`** (`0xC405`, 2 bytes, existing — `IP-1103`) — read-only here; this
  package reads its low byte and reduces it mod 10 for single-digit display.
- **`update_status_disp`** (`asm_game.py:1346`, extended by `IP-9170`'s own `GAME_MODE`-gated
  finite-mode branch) — gains the paired `GAME_MODE != 0` (Infinite Mode) branch, writing to the
  same `0x9804` cell `IP-9170`'s branch writes in finite mode. The two branches are mutually
  exclusive (gated on the same `GAME_MODE` read `IP-9170` already added) — confirm at
  implementation time that `IP-9170` has shipped and re-derive its exact branch structure before
  adding the Infinite Mode half, rather than duplicating the `GAME_MODE` read.
- **`_score_bar`** (`tilemaps.py:39`) — unchanged; its baked digit remains the correct fallback
  for the one frame before `update_status_disp` first runs.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`update_status_disp`**: extend the `IP-9170` `GAME_MODE` check (currently `JR_NZ` to skip
    the finite-mode write entirely) into a real two-way branch: `GAME_MODE == 0` → `IP-9170`'s
    existing `WORLD_SCALE` write (unchanged); `GAME_MODE != 0` → new: read
    `RUNNING_TREASURE_COUNT`'s low byte, reduce mod 10 (repeated-subtraction, no `DIV`, mirroring
    `inf_mod9`'s established technique per the TWBS note), add `TL_DIGIT_0`, write to `0x9804`.
    Confirm the exact current branch shape by direct re-read at implementation time (drift check
    — `IP-9170` may have shipped with a slightly different structure than planned).
- **No change** to `tilemaps.py`, `build_rom.py`, or `worldgen.py`.

## 7. Implementation Tasks

Ordered: (1) confirm `IP-9170` shipped and re-derive `update_status_disp`'s exact current
structure by direct read (drift check, Blocking if materially different); (2) confirm
`RUNNING_TREASURE_COUNT`'s address/width unchanged; (3) implement the mod-10 reduction (mirror
`inf_mod9`'s repeated-subtraction pattern, bound 10 instead of 9); (4) wire the `GAME_MODE != 0`
branch to write the resulting digit to `0x9804`; (5) rebuild, confirm byte delta is a handful of
instruction bytes; (6) full suite run; (7) add the new test (§8); (8) documentation updates (§9).

## 8. Tests to Add

Extends the same suite `IP-9170`'s own `T8.10c`–`T8.10e` checks landed in:

- **Infinite Mode HUD digit correctness:** force `GAME_MODE=1` and `RUNNING_TREASURE_COUNT` to at
  least two values that exercise the mod-10 wrap (e.g. 7 and 13 — the second confirms the digit
  reads `3`, not garbage or an unreduced value), confirm col 4 reads the correct low digit within
  2 frames.
- **Finite Mode non-regression:** confirm `IP-9170`'s own finite-mode `WORLD_SCALE` write is
  unaffected by this package's addition (a direct regression guard the same way `T8.10e` guards
  the reverse direction).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-9161`'s Notes (already extended by
  `IP-9170`) gains a follow-up line recording the Infinite Mode convention this package resolves.
- `docs/pipeline/backlog.md`: `BL-0144` → resolution note (manager flips status on harvest).
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Infinite Mode's HUD col-4 cell shows `RUNNING_TREASURE_COUNT mod 10` once `update_status_disp`
  has run at least once after entering `PLAYING` in Infinite Mode.
- Finite mode's own `WORLD_SCALE` display (`IP-9170`) is confirmed unaffected.
- ROM builds at exactly 32768 bytes; full suite passes.
- Diff scope: `asm_game.py` only.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] New Infinite Mode HUD digit check passes at two `RUNNING_TREASURE_COUNT` values, including
      one that exercises the mod-10 wrap (e.g. 13 → digit 3).
- [ ] Finite mode's own `WORLD_SCALE` display confirmed unaffected (regression guard).
- [ ] Direct diff: no `tilemaps.py`/`build_rom.py`/`worldgen.py` change.
- [ ] Mod-10 reduction confirmed `DIV`/`MUL`-free by direct code read.

## 12. Dependencies

- **`IP-9170`** (`COMPLETE`, own `09` pass owed as of this planning pass) — this package extends
  the exact `GAME_MODE` branch structure `IP-9170` adds to `update_status_disp`; **hard
  sequencing precondition** — implementing this package before `IP-9170` ships would mean
  guessing at a branch structure that doesn't exist yet.

## 13. Risks

Low. **Named, not resolved:** the single-cell format means any `RUNNING_TREASURE_COUNT` value
≥10 displays only its low digit (13 and 23 both show "3") — the user's own decision text
explicitly named this option ("or its low digit"), so this is an accepted, deliberate scoping
choice, not a defect this package should try to work around by claiming more HUD cells (that
would be a real layout change, a separate, larger package if ever wanted).

## 14. Rollback Considerations

Remove the `GAME_MODE != 0` branch and its mod-10 reduction from `update_status_disp`, rebuild.
No save-format, WRAM, or interface dependency.
