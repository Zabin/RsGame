# IP-9130 — Zone-Transition Intent Gate

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9130` — bug-remediation series; no FS. Source: **`BL-0078`** (High, project owner report,
filed via `00-intake`, this session).

## 2. Objective

Stop spurious zone transitions: `check_zone_transition` currently fires whenever the player's
position satisfies a direction's threshold and a neighbor exists — regardless of whether the
player is actually pressing that direction. Confirmed reproducible at the literal default game
start: walk RIGHT until blocked (correct, no transition), then walk DOWN only — the very next
region entered fires a spurious RIGHT transition if it happens to have an open right neighbor,
since `PLAYER_X` is still sitting at the RIGHT clamp ceiling from the earlier walk. This package
adds an intent gate (the corresponding `JOY_CUR` direction bit must be held) to all four branches.

## 3. Requirements Covered

No FR/NFR text change — this is a defect in the shipped implementation of `FR-2300` (zone-boundary
transition on a valid neighbor). `FR-2300`'s Notes gain an entry recording this regression and its
fix; the requirement's own text never specified position-only triggering as correct — it describes
"the player crosses the edge," which a purely positional check does not faithfully implement once
crossing can be approached from a perpendicular direction (post-`IP-1070`).

## 4. Architecture Components

No architecture decision needed — a trigger-condition bug, not a design question. Confirms (does
not revisit) `IP-9050`'s (`BL-0047`) `check_zone_transition` rewrite and `IP-9120`'s (`BL-0076`)
threshold fix: every edge branch still reads a `REGION_GRAPH` neighbor byte after a screen-edge
position test; this package adds one more precondition (held input) ahead of that existing logic,
changing no other part of the routine's shape.

## 5. Interfaces

None new. `check_zone_transition`'s own interface (no arguments, reads `PLAYER_X`/`PLAYER_Y`/
`CUR_ZONE`/`REGION_GRAPH`/`JOY_CUR`, writes `CUR_ZONE`/`PLAYER_X`/`PLAYER_Y`/`TRANSITION_TO`/
`NEED_REDRAW`) gains one new read (`JOY_CUR`, already-existing WRAM, already read elsewhere by
`handle_play_input`) — not a new address, not a data-model change.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`check_zone_transition`** (`asm_game.py:660-701` as of this session — confirm exact lines
    during authoring, drift check). Add a `JOY_CUR` bit-test gate at the top of each of the four
    branches, before the existing position test, using the same `BIT_b_A`/`LD_A_nn(JOY_CUR)`
    pattern `handle_play_input` already uses (with `BIT_b_B` against `B`, per that routine's own
    register convention — this routine uses `A` directly since nothing else needs `B` held at
    this point):
    - **RIGHT** (label `check_zone_transition`, current line 665): before
      `LD_A_nn(PLAYER_X); CP_n(152); JR_C('czt_left')`, insert
      `LD_A_nn(JOY_CUR); BIT_b_A(J_RIGHT); JR_Z('czt_left')` — if RIGHT isn't held, fall straight
      through to the LEFT branch exactly as if the position test had failed.
    - **LEFT** (label `czt_left`, current line 674): before the existing `PLAYER_X`/`OR_A` test,
      insert `LD_A_nn(JOY_CUR); BIT_b_A(J_LEFT); JR_Z('czt_top')`.
    - **UP** (label `czt_top`, current line 683): before the existing `PLAYER_Y`/`CP_n(18)` test,
      insert `LD_A_nn(JOY_CUR); BIT_b_A(J_UP); JR_Z('czt_bot')`.
    - **DOWN** (label `czt_bot`, current line 692): before the existing `PLAYER_Y`/`CP_n(128)`
      test, insert `LD_A_nn(JOY_CUR); BIT_b_A(J_DOWN); RET_Z()` — `czt_bot` is the routine's last
      branch (no further fallthrough label), so a failed gate here returns directly, exactly
      mirroring the existing `RET_C()` "not at the edge" outcome it sits beside.
    - `J_RIGHT`/`J_LEFT`/`J_UP`/`J_DOWN` are the existing bit constants (`asm_game.py:140`,
      `4`/`5`/`6`/`7`) `handle_play_input` already uses; `JOY_CUR` is the existing WRAM address
      (`asm_game.py:32`, `0xC00C`). `BIT_b_A` is `handle_play_input`'s own sibling helper
      (`gbc_lib.py`) already used in this file's maze pass — no new opcode wrapper needed.
    - No other line in the routine changes — the existing position/neighbor logic is unchanged,
      only gated behind one new precondition per branch.
- **Modify: `test_rom.py`**:
  - **`T11.a2`** (`test_rom.py:784-798`): the memory-forced position write that triggers the
    zone-0 transition must be bracketed by a real `button_press`/`button_release` for the matching
    direction (`right` when `_t11a_dir == 3`, `down` otherwise) — the teleport still gives instant
    positioning; the held button satisfies the new gate.
  - **`_t17_do_move`** (`test_rom.py:1601-1615`): each of the four direction branches must hold
    the matching real button (`button_press`) across its own teleport-and-`settle` window, then
    release — this single helper covers `T17.a`, `T17.b2`, and `T17.b5`, so one fix here is
    sufficient; no other call site needs its own separate change.
  - Add the new regression check (§8).

## 7. Implementation Tasks

Ordered: (1) confirm `check_zone_transition`'s exact current line numbers (drift check); (2) add
the four `JOY_CUR` gates per §6's own instruction-level guidance; (3) update `T11.a2` and
`_t17_do_move` to hold the matching real button around their own position writes; (4) author the
new direct regression check (§8); (5) rebuild ROM, run the full suite — confirm `T7.9`–`T7.11`,
`T16`, `T17.c1`/`T17.c2` all continue to pass unchanged (per the supersession sweep, a failure
here signals the sweep missed something); (6) re-confirm via direct PyBoy check with real,
sustained button-press input (mirroring `BL-0078`'s own reproduction: hold RIGHT until blocked,
release, hold DOWN only) that the spurious transition no longer occurs; (7) documentation/
traceability updates (§9).

## 8. Tests to Add

Extends the existing **`T7: Joypad and Movement`** suite (`test_rom.py`) — no new suite number,
placed immediately after `T7.11`:

- **T7.12 — No spurious transition on a perpendicular approach (the direct `BL-0078` regression
  test).** Using the same default fixture and region shape `T7.11` already establishes (region 0
  right-blocked, `down`→region 3, region 3's own right neighbor open to region 4): drive the
  player rightward via real, sustained `button_press('right')` input until it settles at the
  clamp ceiling (mirroring `T7.10b`), release, then drive **only** `button_press('down')` (never
  touching left/right again) into region 3. Assert `CUR_ZONE == 3` (the down transition still
  fires correctly) **and** `CUR_ZONE` stays `3` for a further settle window (no spurious rightward
  follow-on transition) — the exact sequence `BL-0078`'s own reproduction used.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: add a Notes entry to `FR-2300` recording
  this regression (citing `BL-0078`) and its fix.
- `docs/requirements/04-requirements-traceability-matrix.md`: update `FR-2300`'s Test cell to add
  `T7.12` and this package.
- Master Build Plan status row.

## 10. Definition of Done

- All four of `check_zone_transition`'s branches require the corresponding `JOY_CUR` direction
  bit held, in addition to the existing position/neighbor test.
- `T7.12` demonstrably passes — a real, sustained right-then-down walk no longer produces a
  spurious follow-on transition.
- Every existing check that touches `PLAYER_X`/`PLAYER_Y`/`CUR_ZONE`/`check_zone_transition`
  still passes (only `T11.a2`/`_t17_do_move` needed updating, confirmed by the supersession
  sweep — every other site was already button-driven or non-boundary).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct code read: all four `check_zone_transition` branches gate on the matching `JOY_CUR`
      bit before their existing position test.
- [ ] `T7.12` present and passing, using real button-press input, confirmed by direct read.
- [ ] Direct PyBoy re-check (ad hoc, mirroring `BL-0078`'s own reproduction method): the
      right-then-down sequence no longer produces a spurious transition, at the literal reported
      scenario (default fixture, region 0→3).
- [ ] `T7.9`–`T7.11`, `T16`, `T17.a`, `T17.b2`/`b5`, `T17.c1`/`c2`, `T19.*` all still pass,
      confirming no regression from this fix itself.
- [ ] Requirements/RTM deltas applied exactly as §9 names.

## 12. Dependencies

None functionally — `check_zone_transition` has no upstream dependency beyond `IP-1010`'s own
bootstrap (`VERIFIED`) and the already-`COMPLETE` `IP-9050`/`IP-9120` (both touch the same
routine; this package's own diff is additive/corrective, not a conflict). Independent of `IP-9110`
(`gw_prng_step`, disjoint) and the blocked/unauthorized `IP-1080`.

## 13. Risks

- **Low.** The production change is small and mechanically simple (one `BIT` test per branch,
  identical in shape to `handle_play_input`'s own existing gating); the test-suite ripple was
  swept exhaustively (§ TWBS) and found to touch exactly two sites, both already using an
  established, working real-button-hold pattern elsewhere in the same file.
- **Not fully play-blocking** (unlike `IP-9120`'s own Critical regression) — the player can still
  navigate, just occasionally into an unintended zone — but reproducible from the literal default
  game start, so real and worth prioritizing rather than deferring indefinitely.
- ROM budget: four new `BIT`-test sequences (~7 bytes each, ~28 bytes total) — negligible against
  ~10KB current headroom.

## 14. Rollback Considerations

Revert `asm_game.py`'s four `check_zone_transition` gate insertions and `test_rom.py`'s `T11.a2`/
`_t17_do_move`/`T7.12` changes, then rebuild. Reverts to the current regressed state (spurious
perpendicular-approach transitions) — not a save-compatibility-relevant rollback (no
`SAVE_VERSION_VAL` change, no persisted-format impact).
