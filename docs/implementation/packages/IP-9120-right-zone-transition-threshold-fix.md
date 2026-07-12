# IP-9120 — RIGHT Zone-Transition Threshold Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9120` — bug-remediation series; no FS. Source: **`BL-0076`** (Critical, project owner report,
filed via `00-intake`, this session).

## 2. Objective

Restore rightward zone transitions, currently broken for every player in every generated world.
`check_zone_transition`'s own RIGHT-edge trigger (`PLAYER_X >= 156`) can no longer be satisfied
through normal gameplay input since this session's `IP-9090` correctly lowered the RIGHT movement
clamp's own maximum reachable `PLAYER_X` to `152` (`BL-0052`'s own fix, itself correct in
isolation). The two thresholds used to overlap by coincidence under the *old*, buggy clamp
(`159 >= 156`); they no longer do. This package brings `check_zone_transition`'s own threshold
back into agreement with the corrected clamp — a one-constant change, no algorithm change.

## 3. Requirements Covered

No FR/NFR text change — this is a defect in the shipped implementation of `FR-2300` (zone-boundary
transition on a valid neighbor, already baselined; `FR-2310` is the *negative* case, "no transition
at a true grid boundary," and is unaffected by this bug). **Correction (2026-07-12, discovered
during `08-code-implementation`):** this field originally cited `FR-2310` — corrected to `FR-2300`,
the actual positive-transition requirement this regression breaks. `FR-2300`'s Notes gain an entry
recording this regression and its fix; no requirement text is wrong, the *code* drifted out of
agreement with itself across two sibling packages (`IP-9050`'s own `check_zone_transition` rewrite
and this session's `IP-9090`).

## 4. Architecture Components

No architecture decision needed — a boundary-constant bug, not a design question. Confirms (does
not revisit) `IP-9050`'s (`BL-0047`) `check_zone_transition` rewrite: every edge branch reads a
`REGION_GRAPH` neighbor byte after a screen-edge position test; only the RIGHT branch's own
position-test operand is wrong post-`IP-9090`.

## 5. Interfaces

None new. `check_zone_transition`'s own interface (no arguments, reads `PLAYER_X`/`PLAYER_Y`/
`CUR_ZONE`/`REGION_GRAPH`, writes `CUR_ZONE`/`PLAYER_X`/`PLAYER_Y`/`TRANSITION_TO`/`NEED_REDRAW`)
is completely unchanged — only the RIGHT branch's own comparison operand.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`check_zone_transition`** (`asm_game.py:660-698` as of this session — confirm exact lines
    during authoring, drift check). Line 662: change
    `rom.LD_A_nn(PLAYER_X); rom.CP_n(156); rom.JR_C('czt_left')` to
    `rom.LD_A_nn(PLAYER_X); rom.CP_n(152); rom.JR_C('czt_left')` — the RIGHT-edge trigger now
    fires at `PLAYER_X >= 152`, exactly matching `handle_play_input`'s own RIGHT clamp ceiling
    (`asm_game.py:518`, `CP_n(153)` → max reachable `X=152`), mirroring DOWN's own already-correct
    "transition threshold == movement clamp's own max reachable value" pattern
    (`check_zone_transition:689`, `CP_n(128)`, matching `handle_play_input`'s DOWN clamp ceiling
    of `128` exactly). No other line in this routine changes — LEFT (`X==0` exact match, floor
    `0`) and UP (`Y<18`, floor `8`, `8<18` so the transition range is still reached while walking)
    remain correct and untouched.
  - Nothing else in `asm_game.py` — confirmed by this pass's own supersession sweep (TWBS, "RIGHT
    zone-transition regression" section): exactly one other call site shares the old `156`/`153`/
    `159`/`160`-class constant (`handle_play_input`'s own already-correct clamp), no third
    location needs updating.
- **Modify: `test_rom.py`**: add a new real-button-press-driven positive-transition regression
  check (§8) — the class of test missing across every direction that let this regression ship
  undetected (named in the TWBS as a broader gap, not fixed wholesale here — only RIGHT, this
  package's own scope).

## 7. Implementation Tasks

Ordered: (1) confirm `check_zone_transition`'s exact current line numbers (drift check); (2)
change line 662's comparison operand `156`→`152`; (3) author the new real-button-press regression
test (§8); (4) rebuild ROM, run the full suite — confirm `T7.9`/`T7.10`/`T7.10b`/`T11.a2`/`T17.*`/
`T19.*` all continue to pass unchanged (they should, per the supersession sweep — a failure here
is itself a signal the sweep missed something); (5) re-confirm (via direct PyBoy check with real,
sustained button-press input, not memory-forced teleportation — the exact discipline that missed
this regression the first time) that a player can now walk into an open right-neighbor zone; (6)
documentation/traceability updates (§9).

## 8. Tests to Add

Extends the existing **`T7: Joypad and Movement`** suite (`test_rom.py`) — no new suite number,
placed immediately after the existing `T7.10b` (RIGHT clamp boundary check) it directly builds on:

- **T7.11 — Real button-press-driven RIGHT transition (the direct `BL-0076` regression test).**
  **Correction (2026-07-12, discovered during `08-code-implementation`):** the default fixture's
  own region 0 (`seed=0`→`1`, `scale=3`) has no open RIGHT neighbor — region 3 does (confirmed via
  `worldgen.py`, right neighbor = region 4), so the test forces `CUR_ZONE=3` directly (the same
  established convention `T7.10`/`T16.a` already use to isolate a specific region for testing)
  rather than replaying a full navigation path. Drives the player rightward via **real, sustained
  `button_press('right')`/tick cycles** (not `pb.memory[PLAYER_X] = <value>` teleportation),
  releasing the button the instant `CUR_ZONE` changes — held past that point, RIGHT keeps moving
  the player inside the *new* zone too (an interaction the original plan didn't account for; a
  fixed-tick-count hold like `T7.10b`'s own dead-end case caused overshoot here since a real
  transition fires partway through). Asserts `CUR_ZONE == 4` (the transition fired) and
  `PLAYER_X <= 20` (settled near the new zone's own left-entry position, tolerant of a couple of
  residual movement ticks) — the exact combination (real movement clamp behavior *and* a live
  transition) no existing check exercises together. This is the check that would have caught
  `BL-0076` before it shipped.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: add a Notes entry to `FR-2300` (corrected
  from this field's own original, wrong `FR-2310` citation — see §3) recording this regression
  (citing `BL-0076`) and its fix — the requirement's own text was never wrong, the implementation
  drifted out of internal agreement across `IP-9050`/`IP-9090`.
- `docs/requirements/04-requirements-traceability-matrix.md`: update `FR-2300`'s Test cell to
  cite the new `T7.11` check and this package.
- Master Build Plan status row.

## 10. Definition of Done

- `check_zone_transition`'s RIGHT-edge comparison reads `CP_n(152)`, exactly matching
  `handle_play_input`'s own RIGHT clamp ceiling.
- `T7.11` demonstrably passes — a real, sustained rightward button-press walk both reaches the
  correct clamp ceiling and crosses into the expected neighbor zone.
- Every existing check that touches `PLAYER_X`/`CUR_ZONE`/`check_zone_transition` still passes
  unchanged (no hardcoded-value updates needed, confirmed by the supersession sweep).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct code read: `check_zone_transition`'s RIGHT-edge comparison reads `CP_n(152)`, not
      the old `CP_n(156)`.
- [ ] `T7.11` present and passing, using real button-press input (not memory-forced position),
      confirmed by direct read of the test's own implementation.
- [ ] Direct PyBoy re-check (ad hoc, mirroring `BL-0076`'s own reproduction method): sustained
      real rightward button-press input at a region with a confirmed-open right neighbor crosses
      into that neighbor zone.
- [ ] `T7.9`/`T7.10`/`T7.10b`/`T11.a2`/every `T17`/`T19` check that touches `PLAYER_X` or
      `CUR_ZONE` still passes, confirming no regression from this fix itself.
- [ ] Requirements/RTM deltas applied exactly as §9 names.

## 12. Dependencies

None functionally — `check_zone_transition` has no upstream dependency beyond `IP-1010`'s own
bootstrap (`VERIFIED`) and `IP-9050`'s own `COMPLETE` rewrite of the routine (not `VERIFIED`, but
this package's own diff is additive/corrective to that work, not a conflict with it). Independent
of `IP-9110` (`gw_prng_step`, a disjoint routine) and the blocked/unauthorized `IP-1080`.

## 13. Risks

- **Very low.** A single comparison-operand change, directly analogous in shape and risk to
  `IP-9090`'s own already-shipped fix; the corrected value (`152`) is independently derived from
  the same sprite-width/screen-width arithmetic `IP-9090` already used and verified, not a new
  guess.
- **Severity of the defect being fixed is Critical** (breaks core navigation universally) — this
  package should be prioritized and, given the class of regression, an expedited G3 ask is
  reasonable rather than leaving it to queue behind lower-severity work.
- ROM budget: a single operand byte changes value, zero bytes added.

## 14. Rollback Considerations

Revert `asm_game.py`'s `check_zone_transition` change (`152`→`156`) and remove `T7.11`, then
rebuild. Reverts to the current regressed state (RIGHT transitions broken for every player) — not
a save-compatibility-relevant rollback (no `SAVE_VERSION_VAL` change, no persisted-format impact).
