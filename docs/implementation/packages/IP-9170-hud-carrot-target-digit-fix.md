# IP-9170 — HUD Carrot-Target Digit Fix (`BL-0139`)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9170` — remediation package for [`BL-0139`](../../pipeline/backlog.md) (Medium,
`08-content-authoring` run #206 Outstanding Issue): the HUD's carrot-target digit (row 0, col 4)
is baked to a literal `"9"` by every screen's `_score_bar` and never updated at runtime, but the
finite-mode win condition (`CARROTS_COUNT == WORLD_SCALE`, `IP-1021`) means any world whose scale
isn't 9 shows a target digit that doesn't match its own real win condition. No FS — a
rendered-content correctness gap against an existing, shipped mechanic, not new behavior.

## 2. Objective

During finite-mode `PLAYING`, the HUD's target digit (row 0, col 4, immediately after the
baked `-` at col 3) always shows the current world's actual `WORLD_SCALE` value, matching the
real win condition the player is working toward.

**Explicitly out of scope** (see the Technical Work Breakdown's own scope-decision note): what
Infinite Mode's own col-4 cell should show. Infinite Mode has no fixed carrot ceiling
(`RUNNING_TREASURE_COUNT` only increases), so "the current WORLD_SCALE" has no meaning there —
this is a real, unresolved design question, not a mechanical fix, and is intentionally left to a
future `03`/`06` pass. This package leaves Infinite Mode's col-4 cell completely untouched.

## 3. Requirements Covered

None directly (no FR/NFR describes the target-digit HUD cell specifically). The fix restores
alignment between the HUD and the already-baselined `FR-9130`/`IP-1021` win-condition text
(`CARROTS_COUNT == WORLD_SCALE`), which this package's Documentation Updates (§9) will note.

## 4. Architecture Components

None new. `GDS-08` §5 (row-0 static HUD composition) already documents col 4 as part of the
static/baked target-glyph region; this package converts exactly one of those cells (col 4 only —
col 3's `-` glyph stays baked, unchanged) from build-time-baked to runtime-written, the same class
of change `update_status_disp` already performs for cols 2/8-10.

## 5. Interfaces

- **`WORLD_SCALE`** (`0xC06B`, existing, read-only here — `IP-1020`'s own field, 2-9 range per its
  own established comment) — new read site inside `update_status_disp`.
- **`update_status_disp`** (`asm_game.py:1346`) — gains one new write (col 4) alongside its
  existing `CARROTS_COUNT`→col 2 write; same `TL_DIGIT_0 + value` tile-encoding convention, same
  `GAMESTATE == GS_PLAYING` / `SCORE_DIRTY` gating already governing every other write in this
  routine (no new gating condition — reuses what's already there).
- **`_score_bar`** (`tilemaps.py:39`) — **unchanged**: its baked `"-9"` at cols 3-4 remains the
  correct fallback for the one frame before `update_status_disp` first runs (and for every
  non-`PLAYING` `GAMESTATE`, where `update_status_disp` returns immediately per its own existing
  `RET_NZ`), exactly mirroring how `_score_bar`'s baked `TL_DIGIT_0` placeholders for the carrot
  count and score already work today.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`update_status_disp`** (`asm_game.py:1346`–`1354`): immediately after the existing carrot-
    count write (`asm_game.py:1352`–`1353`, `LD_A_nn(CARROTS_COUNT); rom.ADD_A_n(TL_DIGIT_0);
    rom.LD_HL_nn(0x9802); rom.LD_HL_A()`), insert a **`GAME_MODE`-gated** write: read `GAME_MODE`
    (`0xC3F6`), skip if nonzero (Infinite Mode — leave col 4 untouched, per §2's scope decision),
    otherwise read `WORLD_SCALE`, add `TL_DIGIT_0`, write to `0x9804` (row 0, col 4 — confirm this
    address by direct re-derivation at implementation time: `0x9800 + 0*32 + 4`).
  - No other line in this routine changes.
- **No change** to `tilemaps.py` (`_score_bar`'s bake stays exactly as-is), `build_rom.py`, or
  `worldgen.py` — confirmed by this package's own scope: the fix is a single additional
  conditional write inside an already-existing routine, nothing else.

## 7. Implementation Tasks

Ordered: (1) confirm `update_status_disp`'s cited line numbers and `GAME_MODE`'s address against
the current tree by direct re-read (drift is Blocking); (2) confirm `0x9804` is the correct row-0/
col-4 tilemap address (re-derive, don't assume); (3) insert the `GAME_MODE`-gated `WORLD_SCALE`
write immediately after the existing carrot-count write; (4) rebuild, confirm the ROM's byte
delta is a handful of bytes (a handful of new instructions, no data-section growth); (5) run the
full suite — zero regressions expected, since no existing check reads col 4 explicitly (confirm
by grep before assuming); (6) add the new test (§8); (7) documentation/traceability updates (§9).

## 8. Tests to Add

New check in **T14** (main menu & new-game flow) or a new small check appended to **T7**
(movement/HUD) — whichever suite currently owns `update_status_disp`'s other digit-write
assertions (confirm at implementation time by grep for `0x9802`/`0x9808` in `test_rom.py` and land
beside them, not in a new suite):

- **HUD target-digit correctness (finite mode):** for at least two non-default `WORLD_SCALE`
  values (e.g. 5 and 7, chosen to differ from the suite's own default-fixture scale of 3 per this
  skill's own tunable-parameter rule — a scale=3 world alone would leave this check
  indistinguishable from the pre-existing bug, since the baked default already happens to show a
  plausible-looking digit at low scores), confirm the HUD's col-4 tile reads
  `TL_DIGIT_0 + WORLD_SCALE` after a redraw.
- **Infinite Mode non-regression:** confirm Infinite Mode's own col-4 cell is **unaffected** —
  reads whatever `_score_bar` baked, exactly as before this package (a direct regression guard
  against this package's own `GAME_MODE` gate ever being dropped or inverted by accident).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: a Notes line on `FR-9130`/`IP-1021`'s own
  win-condition text, or a new small note wherever the HUD's target-digit convention is
  documented, recording that the digit now tracks `WORLD_SCALE` at runtime in finite mode.
- `docs/pipeline/backlog.md`: `BL-0139`'s finite-mode half → resolution note (manager flips
  status on harvest); a **new, narrower backlog entry** for the still-open Infinite-Mode-HUD
  design question, filed by this package's own completion (per §2's scope decision) rather than
  silently dropped.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Every finite-mode world, at any `WORLD_SCALE` value 2-9, shows its own actual scale in the HUD's
  target digit (row 0, col 4) once `update_status_disp` has run at least once after entering
  `PLAYING`.
- Infinite Mode's own col-4 cell is confirmed byte-for-byte unaffected by this package (the exact
  pre-existing baked value, whatever `_score_bar` put there).
- ROM builds at exactly 32768 bytes; full suite passes.
- Diff scope: `asm_game.py` only (one routine, one inserted conditional write).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] New HUD target-digit check passes for at least two non-default, non-corpus-default
      `WORLD_SCALE` values.
- [ ] New Infinite Mode non-regression check confirms col 4 is untouched there.
- [ ] Direct diff: no `tilemaps.py`/`build_rom.py`/`worldgen.py` change; `update_status_disp`'s
      only change is the one inserted `GAME_MODE`-gated write.
- [ ] Byte-budget delta recorded (expected: a handful of instruction bytes, no data-section
      growth).

## 12. Dependencies

None — independent of every other in-flight or `VERIFIED` package. `update_status_disp` is not
touched by any other package currently in the tree (confirmed by direct grep of the Master Build
Plan's Files-to-Modify claims).

## 13. Risks

Low. A single additional conditional write inside an already-`VERIFIED`, frequently-exercised
routine, gated on an existing WRAM field (`GAME_MODE`) with no new state. The one real risk named
explicitly: **scope creep toward "also fix Infinite Mode's display"** — this package's own §2/§7
scope decision exists specifically to prevent that; if implementation finds the `GAME_MODE` gate
insufficient for some reason (e.g. a third mode is added before this ships), that is drift →
Blocking Report, not a quiet in-package expansion.

## 14. Rollback Considerations

Remove the inserted `GAME_MODE`-gated write from `update_status_disp`, rebuild. No save-format,
WRAM, or interface dependency — a pure presentation-layer write with no persisted state.
