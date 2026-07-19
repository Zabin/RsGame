# IP-1128 — Infinite Mode Combat: Weapon Directionality

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1128` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow C step 4 (weapon directionality),
widening the fire mechanism `IP-1122` already shipped.

## 2. Objective

Widen the fired projectile's own direction from today's shipped left/right-only encoding to all
eight compass directions, derived from the player's own movement (current direction while moving,
last direction while idle) — with diagonal projectiles moving along both axes simultaneously,
mirroring this codebase's own established single-axis-integer-stepping idiom applied to two axes
at once rather than inventing vector motion.

## 3. Requirements Covered

FR-11310 (movement-based multi-directional weapon fire) in full.

## 4. Architecture Components

`FS-112` §6 Workflow C step 4 / §9 Interfaces Used (`PLAYER_DIR` cross-reference) / §10 Data Model
Changes (`PlayerFacing`) · `ADS-002` "Weapon Directionality Delta" (2026-07-19) · `ADR-0021`
(weapon-direction representation — all four of this package's own design decisions below trace
directly to that ADR's own four numbered decisions).

## 5. Interfaces

- **`handle_play_input`'s existing RIGHT/LEFT/UP/DOWN branches** (`asm_game.py`, unchanged in
  their own `PLAYER_X`/`PLAYER_Y`/`PLAYER_DIR`/`TMP1` writes) — this package adds one additional
  write inside each of the four branches (the new facing fields, §6 below), touching no existing
  line in any of the four.
- **`PLAYER_DIR`** (existing, `0xC003`, unchanged) — read-only reference confirming its own
  established 2-value shape stays untouched, per `ADR-0021`'s own Decision 1. This package does
  not write or widen it.
- **`inf_projectile_hittest`** (`IP-1122`, unchanged) — reads `PROJ_X`/`PROJ_Y` only, never
  `PROJ_DIR`'s own encoding; confirmed by direct code read (§7 Supersession sweep) to need no
  change regardless of how many axes the projectile steps on.
- **`inf_mob_move`'s own dominant-axis stepping idiom** (`IP-1126`, unchanged, referenced not
  reused) — the *shape* (raw signed integer stepping, no multiplication) this package's own
  per-axis projectile stepping mirrors; not the routine itself.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **Two new WRAM constants** (first unclaimed bytes past `IP-1126`'s own `MOB_MOVE_TIMER` end,
    `0xC6DE`): `PLAYER_FACING_X = 0xC6DF`, `PLAYER_FACING_Y = 0xC6E0` (1 byte each — the player's
    own persistent facing, stored as a raw signed step already ready for direct addition:
    `0x01` = +1, `0x00` = 0, `0xFF` = −1). **Boot-initialized** (outside the `0xC000`–`0xC2FF`
    blanket-clear range, needs an explicit boot block, mirroring `WEAPON_TIER`'s own
    boot-*initialize*-not-clear precedent): `PLAYER_FACING_X = 1` (facing right, matching
    `PLAYER_DIR`'s own default-right shape), `PLAYER_FACING_Y = 0` (no vertical bias) — a sane
    default so firing before the player has ever moved still produces a rightward shot rather
    than a directionless (0,0) projectile.
  - **One new WRAM constant**: `PROJ_STEP_Y = 0xC6E1` (1 byte — the projectile's own transient
    Y-axis step, mirroring `PROJ_X`/`PROJ_Y`'s own established "transient copy taken at fire
    time" pattern; no boot-init needed, `PROJ_ACTIVE == 0` gates its validity like every other
    projectile field).
  - **`PROJ_DIR` (`0xC6D8`, existing address) repurposed in place, not widened elsewhere** —
    renamed `PROJ_STEP_X` and redefined from "0=right/1=left" to the same raw-signed-step
    encoding as `PLAYER_FACING_X`/`Y` above. Safe per the mandatory supersession sweep (§7): its
    only two consumers (the fire-time copy, `inf_projectile_update`'s own read) are both rewritten
    by this same package; no third site reads or writes it (confirmed by direct grep). Reusing the
    existing byte rather than allocating a fourth new one is the economical choice, mirroring this
    project's own "claim only what's genuinely new" discipline.
  - **`handle_play_input`'s fire branch** — the existing `LD_A_nn(PLAYER_DIR); LD_nn_A(PROJ_DIR)`
    line (the copy-at-fire-time step) becomes two copies: `PLAYER_FACING_X → PROJ_STEP_X`
    (`PROJ_DIR`'s own repurposed address) and `PLAYER_FACING_Y → PROJ_STEP_Y`.
  - **`handle_play_input`'s RIGHT/LEFT/UP/DOWN branches** — each gains one additional write,
    inserted alongside each branch's own existing `PLAYER_X`/`PLAYER_Y`/`TMP1` writes (no existing
    line removed or reordered): RIGHT writes `PLAYER_FACING_X = 1`; LEFT writes
    `PLAYER_FACING_X = -1` (i.e. `0xFF`); UP writes `PLAYER_FACING_Y = -1`; DOWN writes
    `PLAYER_FACING_Y = 1`. A direction *not* held this frame leaves its own axis's facing field
    untouched — mirroring `PLAYER_DIR`'s own exact "only written inside RIGHT/LEFT, never reset
    elsewhere" convention, extended to two independent axes. **Named behavioral property, not
    smoothed over:** because each axis latches independently, a player who moves right, stops,
    then moves up fires diagonally (up-right) on the first up-only frame, not straight up — the
    X axis's own last-held value persists until X is next pressed with a different value. This is
    the natural per-axis reading of "last-faced direction while idle" (`R220`), not a defect;
    named explicitly as a Test to Add (§8) and an Open Question for a future playtest-driven
    revisit, not resolved here.
  - **`inf_projectile_update`** — restructured from the single left/right branch to independent
    per-axis stepping: add `PROJ_STEP_X` to `PROJ_X`, add `PROJ_STEP_Y` to `PROJ_Y` (both plain
    signed-byte additions, no branch needed when a step is 0 — adding 0 is a no-op); a diagonal
    projectile (`PROJ_STEP_X` and `PROJ_STEP_Y` both nonzero) therefore moves on both axes the
    same frame, at the same per-axis magnitude the existing horizontal-only code already used (1
    pixel/frame/axis) — the same accepted "diagonal is faster than cardinal" property the
    player's own existing D-pad movement already has today (simultaneous RIGHT+UP already moves
    both axes 1px/frame each), not a new inconsistency this package introduces. **Boundary check
    extended to Y**: reuses `PLAYER_Y`'s own established clamp constants (the same 8/129 pair
    `handle_play_input`'s own UP/DOWN branches already clamp against) as the projectile's own
    vertical terminal edge, mirroring how the existing code already reuses `PLAYER_X`'s own 0/152
    pair horizontally. Deactivates (no hit-test) if *either* axis's new position falls outside its
    own bound — first axis to fail wins, matching the existing single-axis code's own "stops on
    reaching a boundary" behavior extended to two axes.
  - **`inf_projectile_hittest`** — **not modified**, confirmed by the supersession sweep (§7): it
    reads only `PROJ_X`/`PROJ_Y`, never any direction/step field.

## 7. Implementation Tasks

Ordered: (1) `PLAYER_FACING_X`/`PLAYER_FACING_Y`/`PROJ_STEP_Y` WRAM constants + boot-init block;
(2) rename `PROJ_DIR` → `PROJ_STEP_X` throughout `asm_game.py` (its own existing address/comment,
redefined semantics); (3) extend `handle_play_input`'s four movement branches with the new
per-axis facing writes; (4) update the fire branch's own copy-at-fire-time step to two copies; (5)
restructure `inf_projectile_update`'s own stepping/boundary logic for two independent axes; (6)
rebuild ROM; (7) author new suite; (8) full suite run; (9) documentation updates (§9).

**Mandatory supersession sweep** (this package repurposes `PROJ_DIR`, an existing model):
`grep`ed every reference to `PROJ_DIR` in `asm_game.py` and `test_rom.py` — confirmed exactly two
production-code sites (the fire-time copy in `handle_play_input`, the read in
`inf_projectile_update`, both rewritten by this package) and confirmed `inf_projectile_hittest`
reads only `PROJ_X`/`PROJ_Y`, never `PROJ_DIR`. `test_rom.py`'s own `T30.a`/`T30.b` reference
`PROJ_DIR_ADDR` directly (asserting `dir=1`/`dir=0` for a rightward/leftward fire) — these
assertions must be re-verified still pass under the new raw-signed-step encoding (`1` for right
still reads as `1`; the existing tests only ever exercised right/left, whose new encoding —
`0x01`/`0xFF` — differs from the old `0`/`1` encoding for the *left* case specifically). **Named
explicitly, not discovered mid-implementation:** `T30.b`'s own assertion `dir=0` for a leftward
fire will need updating to the new encoding's leftward value (`0xFF`, not `0`) — a required,
pre-named `test_rom.py` correction, not an unexpected regression to be rediscovered by `08`.

## 8. Tests to Add

New `test_rom.py` suite **`T37: Combat Sub-Mode — Weapon Directionality`**:

- T37.a — firing while moving right (only) spawns a projectile whose per-frame step is
  `(+1, 0)` — moves along X only, Y unchanged across several frames.
- T37.b — firing while moving up (only) spawns a projectile whose per-frame step is `(0, -1)`.
- T37.c — firing while moving diagonally (e.g. RIGHT+UP both held) spawns a projectile whose
  per-frame step is `(+1, -1)` — moves along both axes simultaneously.
- T37.d — all eight compass directions reachable: parameterized corpus over
  RIGHT/LEFT/UP/DOWN/RIGHT+UP/RIGHT+DOWN/LEFT+UP/LEFT+DOWN, confirming each produces its own
  distinct, correct `(step_x, step_y)` pair.
- T37.e — firing while stationary (no direction held this frame) uses the most recently held
  movement direction, not a fixed default — force a prior direction, release all D-pad input,
  fire, confirm the projectile still moves in the last-held direction.
- T37.f — a fresh session that has never moved (boot default) fires rightward — confirms the
  boot-init default (`PLAYER_FACING_X = 1`, `PLAYER_FACING_Y = 0`) produces a sane shot rather
  than a directionless (0,0) projectile.
- T37.g — Y-axis boundary: force a vertically-moving projectile toward the window's own top/bottom
  edge, confirm clean deactivation (mirroring `T30.d`'s own existing X-boundary test).
- T37.h — hit resolution still works correctly for a non-cardinal (diagonal) projectile: force a
  mob into a diagonal projectile's own path, confirm the hit registers exactly as `T30.c` already
  established for the horizontal case — confirms `inf_projectile_hittest`'s own unmodified code
  is genuinely axis-agnostic, not merely assumed to be.
- T37.i — independent live PyBoy drive through the real production per-frame chain (not a
  direct-invoke force), mirroring `T35.i`'s own established discipline: drive the player
  diagonally via real button input during real `PLAYING`, fire, confirm the real projectile's own
  recorded position moves diagonally over several real ticks.
- **Corrected, not merely added:** `T30.b`'s own `dir=0` assertion updated to the new encoding's
  leftward value (`0xFF`) — named in §7's own supersession sweep, applied here.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11310 status → Implemented; Notes updated
  with the concrete WRAM field names/addresses and the boot-default choice.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11310 row → `IP-1128`/`T37`.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md`: metadata-only status update (no field
  content changes — already fully amended at `06-feature-specification`, 2026-07-19).
- `docs/architecture/07-data-model.md`: new `PLAYER_FACING_X`/`PLAYER_FACING_Y`/`PROJ_STEP_Y` rows;
  `PROJ_DIR`'s own existing row updated in place to `PROJ_STEP_X`, its new encoding documented,
  noted as a rename+redefinition (not a new address).
- Master Build Plan status row; `packages/INDEX.md` status → `NOT STARTED` (unblocked).

## 10. Definition of Done

- Firing produces a projectile moving in the correct direction for all eight compass directions,
  including simultaneous both-axis motion for diagonals (T37.a–d).
- Firing while stationary uses the last-held direction, not a fixed default; a fresh, never-moved
  session still fires rightward (T37.e–f).
- Y-axis boundary termination works correctly, mirroring the existing X-axis behavior (T37.g).
- Hit resolution is confirmed axis-agnostic for a diagonal projectile, not merely assumed (T37.h).
- ROM builds at 32768 bytes; full suite passes, including the corrected `T30.b`; `inf_projectile_
  hittest` confirmed byte-for-byte unchanged by direct diff.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T37.a–i each present and passing; `T30.b` corrected and passing under the new encoding.
- [ ] Direct code read: `inf_projectile_hittest` unmodified by this package's own diff.
- [ ] Direct code read: `PLAYER_DIR` unmodified — no widening, no new consumer added.
- [ ] FR-11310/RTM/Master-Build-Plan/`packages/INDEX.md`/`GDS-07` deltas applied exactly as §9
      names.

## 12. Dependencies

- **`IP-1122`** (`VERIFIED`) — `PROJ_ACTIVE`/`PROJ_X`/`PROJ_Y`/`PROJ_DIR` (repurposed in place),
  `inf_projectile_update`/`inf_projectile_hittest`, consumed and modified.
- **`ADR-0021`** — the binding design decisions this package's own §6 directly implements.

## 13. Risks

- **WRAM address contention with `IP-1127` (still `BLOCKED`, not yet built):** `IP-1127`'s own
  package doc prospectively claims `0xC6DF`–`0xC6E0` for `PLAYER_INVINCIBLE`/`MOB_CONTACT_FLAGS`
  — the identical range this package also cites for `PLAYER_FACING_X`/`PLAYER_FACING_Y`. This is
  a genuine planning-time collision between two concurrently-planned, unbuilt packages, named
  explicitly rather than silently assumed away: whichever package `08-code-implementation` builds
  first legitimately claims that range in the real `GDS-07` map; the other must re-derive its own
  next-free-byte at build time (a routine, expected consequence of parallel planning against a
  shared WRAM budget, not a blocking defect in either package).
- **The per-axis-independent-facing-latch behavior** (§6, RIGHT/LEFT/UP/DOWN branch note) is a
  real, named UX nuance — a stale opposite-axis value can produce an unintended diagonal shot
  after a direction change. Not fixed here; a future playtest-driven package could reset the
  opposite axis to 0 after a configurable idle window, if this proves to matter in practice.
- **`NFR-1500`'s own per-frame cycle budget is not confirmed by this package** — a
  direction-decode in `handle_play_input` and a second per-frame axis step in
  `inf_projectile_update` both add real, unmeasured cost on top of the already-unmeasured combat-
  mode frame cost every prior package in this tranche also carries.
- ROM budget: a bounded routine restructuring (no new subroutine, three new WRAM bytes, one
  existing byte repurposed) — expected modest, re-affirmed at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `PROJ_DIR`'s own rename/redefinition is
the only non-additive change this package makes — reverting restores its original two-value
semantics and the two call sites that read/write it, with no data migration needed (the field is
transient, gated by `PROJ_ACTIVE`, never persisted). `PLAYER_FACING_X`/`Y`/`PROJ_STEP_Y` are pure
additions; removing their own call sites is a clean, isolated revert.
