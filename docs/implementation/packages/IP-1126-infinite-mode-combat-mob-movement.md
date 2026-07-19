# IP-1126 — Infinite Mode Combat: Mob Movement

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1126` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers the movement half of Workflow B (mob
materialization already shipped, `IP-1121`; this package adds the per-frame movement step
Workflow B's own step 4 names).

## 2. Objective

Give each active mob a per-frame behavior it currently lacks entirely: periodically recompute a
single grid-aligned step toward the player's current position, at an adjustable speed (distance
per recomputation) and update rate (frames between recomputations), holding still once the mob's
position exactly coincides with the player's.

## 3. Requirements Covered

FR-11210 (mob movement toward the player) in full.

## 4. Architecture Components

`FS-112` §6 Workflow B step 4 / §7 (edge cases) / §19 Open Question 4 (this package's own
resolution of it — see §7 below) · `ADS-002` §System Architecture (no new module; mob AI/defeat
logic already scoped to `asm_game.py`).

## 5. Interfaces

- **`MOB_DATA`/`MOB_COUNT`** (`IP-1121`, `VERIFIED`, unchanged in shape) — this package's sole
  consumer/mutator of the x/y fields; species/health/active fields are read-only here (movement
  never changes them). Reused exactly as `IP-1122`/`IP-1123` already read `MOB_DATA`'s own layout
  — no stride change (see the TWBS's own supersession-sweep note: widening `MOB_DATA` was
  deliberately avoided).
- **`PLAYER_X`/`PLAYER_Y`** (existing, unchanged) — read-only target for the movement step; this
  package never writes them.
- **The player's own existing grid-aligned single-axis-step movement model**
  (`handle_play_input`, unchanged) — reused as the movement *shape* (one axis at a time, ±1 pixel
  per step), not the routine itself; this package implements its own, separate step logic for
  mobs, per `FS-112` §9's own framing.
- **`st_playing`'s existing per-frame dispatch chain** (`inf_mob_contact_check`/
  `inf_projectile_update` call sites, `IP-1122`/`IP-1123`, unchanged) — this package adds one
  more call alongside them, gated the same way (`COMBAT_MODE`).

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constant** (first unclaimed byte past `IP-1120`'s own `CMC_CURSOR` end, `0xC6DD`):
    `MOB_MOVE_TIMER = 0xC6DE` (1 byte — frames remaining until the next recomputation; boot-
    cleared to 0, which is fine since a 0 timer simply recomputes on the very first eligible
    frame rather than waiting a full interval — a harmless, deterministic startup case, not an
    uninitialized-read risk).
  - **New subroutine `inf_mob_move`** — called once per frame from `st_playing`'s existing
    per-frame chain (alongside `inf_mob_contact_check`/`inf_projectile_update`), gated on
    `COMBAT_MODE` (a no-op call otherwise, matching the established pattern): decrements
    `MOB_MOVE_TIMER`; if it has not reached 0, returns immediately (no movement this frame). At
    0: resets `MOB_MOVE_TIMER` to `MOB_MOVE_INTERVAL` (a fixed constant, adjustable default — see
    Risks for the concrete starting value) and iterates all 6 `MOB_DATA` slots, for each active
    slot:
    1. Compute `dx = PLAYER_X - mob.x`, `dy = PLAYER_Y - mob.y`.
    2. If `dx == 0` and `dy == 0` (mob already coincident with the player): no movement this
       interval — the resolution of `FS-112` Open Question 4 (§7 below).
    3. Else, move on whichever axis has the larger absolute distance (`|dx| >= |dy|` moves X,
       otherwise Y), by exactly `MOB_MOVE_STEP` pixels (a fixed constant, adjustable default)
       toward the player, mirroring the player's own single-axis-per-step model — never both
       axes in the same recomputation, and never diagonal motion.
  - **`MOB_MOVE_INTERVAL`/`MOB_MOVE_STEP`** — two named Python-level constants (not WRAM;
    compile-time adjustable defaults, mirroring `FR-11200`'s own six-mob-slot constant and
    `FR-11300`'s own single-projectile-cap constant) with starting values `MOB_MOVE_INTERVAL = 8`
    (recompute roughly 7.5 times/second at 60fps) and `MOB_MOVE_STEP = 1` (one pixel per
    recomputation, the same per-step magnitude the player's own D-pad movement uses) — chosen as
    a conservative, clearly-perceptible-but-not-overwhelming starting pace; re-tunable without a
    requirements change, per `FR-11210`'s own "not fixed here" framing.

## 7. Implementation Tasks

Ordered: (1) `MOB_MOVE_TIMER` constant; (2) `inf_mob_move`'s timer-decrement/reset logic; (3) the
per-slot dominant-axis step computation, including the coincident-with-player hold-still case
(closes `FS-112` Open Question 4 — mark it resolved in `FS-112`'s own metadata, and in
`FEAT-11000`'s forward-reference note, as part of this package's own Documentation Updates); (4)
hook `inf_mob_move` into `st_playing`'s per-frame chain; (5) rebuild ROM; (6) author new suite;
(7) full suite run; (8) documentation updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T35: Combat Sub-Mode — Mob Movement`**:

- T35.a — a mob directly right of the player moves left by exactly `MOB_MOVE_STEP` after one
  recomputation interval elapses (force `MOB_MOVE_TIMER` to 1, tick one frame, confirm `mob.x`
  decreased by exactly `MOB_MOVE_STEP` and `mob.y` unchanged).
- T35.b — a mob directly below the player moves up by exactly `MOB_MOVE_STEP` (the Y-axis
  counterpart of T35.a, confirming the dominant-axis choice is not X-only).
- T35.c — a mob diagonally offset (both `dx`/`dy` nonzero, `|dx| > |dy|`) moves only on the X
  axis this interval, Y unchanged — confirms single-axis-per-step, never diagonal.
- T35.d — the symmetric case (`|dy| > |dx|`) moves only on the Y axis.
- T35.e — a mob already coincident with the player (`dx == 0`, `dy == 0`) does not move on a
  recomputation interval (`FS-112` Open Question 4's own resolution, direct regression test).
- T35.f — no movement occurs before `MOB_MOVE_TIMER` reaches 0: force the timer to a value > 1,
  tick one frame, confirm `mob.x`/`mob.y` unchanged and the timer decremented by exactly 1.
- T35.g — `COMBAT_MODE` off: confirm `inf_mob_move` is a complete no-op (mob position and
  `MOB_MOVE_TIMER` both unchanged across multiple ticks).
- T35.h — an inactive `MOB_DATA` slot is never moved (iterate all 6 slots with one inactive,
  confirm only active slots' positions change).
- T35.i — independent live PyBoy drive through the real production per-frame chain (not a
  direct-invoke force), mirroring `VR-1121`/`VR-1122`'s own established independent-verification
  discipline: force a real mob a known distance from the real player during real `PLAYING`, let
  several real recomputation intervals elapse via real ticks, confirm the mob's own recorded
  position has moved the expected total distance and direction.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11210 status → Implemented; Notes
  updated with the concrete `MOB_MOVE_INTERVAL`/`MOB_MOVE_STEP` values chosen.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11210 row → `IP-1126`/`T35`,
  Module cell → `asm_game.py` (currently `UNASSIGNED`).
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md`: Open Question 4 marked Resolved (holds
  still once coincident, per this package's own §6/§10); `FEAT-11000`'s forward-reference note
  (Feature Catalog) updated to match, metadata only.
- `docs/architecture/07-data-model.md`: new `MOB_MOVE_TIMER` row, `0xC6DE`.
- Master Build Plan status row; `packages/INDEX.md` status → `NOT STARTED` (unblocked).

## 10. Definition of Done

- An active mob's position converges toward the player's own position over successive
  recomputation intervals, moving exactly `MOB_MOVE_STEP` pixels on exactly one (dominant) axis
  per interval, at exactly the `MOB_MOVE_INTERVAL`-frame cadence (T35.a–d, f all passing).
- A mob already coincident with the player holds still rather than jittering (T35.e).
- `COMBAT_MODE` off and inactive mob slots are both correctly excluded (T35.g/h).
- ROM builds at 32768 bytes; full suite passes; `MOB_DATA`'s own 5-byte-per-slot stride is
  unchanged (confirmed by direct code read — this package's own supersession-sweep commitment).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T35.a–i each present and passing.
- [ ] Direct code read: `MOB_DATA`'s own per-slot layout/stride is byte-for-byte unchanged from
      `IP-1121`'s own shipped form — this package only writes the existing x/y fields, never
      widens the record.
- [ ] Direct code read: `inf_mob_render`/`inf_projectile_hittest`/`inf_mob_contact_check`
      (`IP-1121`/`IP-1122`/`IP-1123`) are all unmodified by this package's own diff.
- [ ] FR-11210/RTM/`FS-112`-Open-Question-4/Master-Build-Plan/`packages/INDEX.md` deltas applied
      exactly as §9 names.

## 12. Dependencies

- **`IP-1121`** (`VERIFIED`) — `MOB_DATA`/`MOB_COUNT`, consumed and mutated (x/y fields only).

## 13. Risks

- **`NFR-1500`'s own per-frame cycle budget is not confirmed by this package** — a per-mob
  movement recomputation adds real, unmeasured cost on top of `IP-1121`/`IP-1122`/`IP-1123`'s own
  already-unmeasured combat-mode frame cost; a future Analysis pass (mirroring `NFR-1400`'s own
  direct cycle-counting methodology) remains owed once the full combat tranche is built.
- **`MOB_MOVE_INTERVAL`/`MOB_MOVE_STEP`'s own starting values (8 frames, 1 pixel) are this
  package's own pacing judgment call, not derived from any research/design document** — `FR-11210`
  explicitly leaves the exact values to `06`/`07`; if playtesting later finds the pace wrong, a
  future package can retune the two constants without any requirements or architecture change.
- ROM budget: a bounded routine (one new subroutine, one new WRAM byte) — expected modest,
  re-affirmed at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `inf_mob_move`'s own call site in
`st_playing`'s per-frame chain is a clean, isolated addition (mirrors `inf_mob_contact_check`'s
own precedent) — no existing per-frame routine is altered. `MOB_DATA`'s own x/y fields revert to
their pre-package (materialization-time-only) semantics automatically once `inf_mob_move`'s call
site is removed; no data migration needed since no new persistent field was claimed beyond the
transient `MOB_MOVE_TIMER`.
