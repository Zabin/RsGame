# IP-1127 — Infinite Mode Combat: Post-Contact Player Protection

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1127` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Extends Workflow D step 2 (player health/setback,
`IP-1123`) with the combined invincibility/knockback/cooldown mechanism `FS-112`'s own delta
2026-07-19 added.

## 2. Objective

Fix a confirmed player-experience defect (`BL-0158`): sustained mob contact re-triggers
`inf_mob_contact_check`'s own damage decrement every single frame with nothing separating the
player from the mob afterward, resolving a full 3-hit death-and-setback cycle in 3-4 real frames
— too fast to perceive. Implement all three of the user's own decided combination: post-contact
invincibility frames, a knockback separation, and a per-mob cooldown that outlasts both.

## 3. Requirements Covered

FR-11410 (post-contact player protection: invincibility, knockback, cooldown) in full.

## 4. Architecture Components

`FS-112` §6 Workflow D step 2 / §7 (edge cases) · direct user decision, 2026-07-19, on `BL-0158`'s
own live-drive finding (no ADS/GDS document — this leaf's own Rationale is the user decision
itself, per `FR-11410`'s own Source Documents).

## 5. Interfaces

- **`inf_mob_contact_check`** (`IP-1123`, `asm_game.py`) — this package's primary modification
  site: the existing per-mob contact test and health decrement are gated by two new conditions
  (invincibility, per-mob cooldown) and followed by two new effects (invincibility-window start,
  knockback) on an actual hit. `check_collisions`' own asymmetric point-in-box technique itself
  (which `inf_mob_contact_check` already reuses) is not modified.
- **`PLAYER_HEALTH`/`PLAYER_X`/`PLAYER_Y`** (`IP-1123`/existing, unchanged in shape) — health
  decrement logic unchanged in mechanism, only in when it's allowed to fire; position is written
  by the new knockback effect, using the same direct-write pattern `inf_health_setback` already
  uses for its own reposition.
- **`MOB_DATA`** (`IP-1121`, `VERIFIED`, unchanged) — read-only here (mob position/active flag
  consumed for the contact test and the knockback-direction computation); this package's own new
  per-mob cooldown state is a separate, parallel table (see §6), not a `MOB_DATA` field.
- **`st_playing`'s existing per-frame dispatch chain** (unchanged) — this package adds one more
  call (the invincibility-timer tick) alongside the existing `inf_mob_contact_check`/
  `inf_projectile_update`/`inf_mob_move` (`IP-1126`) calls.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constants** (first unclaimed bytes past `IP-1126`'s own `MOB_MOVE_TIMER` end,
    `0xC6DE`): `PLAYER_INVINCIBLE = 0xC6DF` (1 byte — frames of invincibility remaining, 0 =
    vulnerable, boot-cleared); `MOB_CONTACT_FLAGS = 0xC6E0` (1 byte — one bit per `MOB_DATA` slot
    index, set while that specific mob is in unbroken overlap with the player, boot-cleared;
    **deliberately a new, parallel table, not a `MOB_DATA` field** — see the TWBS's own
    supersession-sweep note on why widening `MOB_DATA`'s stride was avoided).
  - **Modify `inf_mob_contact_check`** (`IP-1123`): for each active mob slot, the existing
    overlap test now additionally reads/writes that slot's own `MOB_CONTACT_FLAGS` bit:
    - If **not overlapping**: clear this slot's bit (contact has broken; the next overlap will be
      treated as a fresh approach).
    - If **overlapping and the bit is already set**: no-op — this is continued overlap from an
      already-registered contact, not a new hit (the per-mob cooldown's own core guarantee).
    - If **overlapping and the bit is clear** (a fresh contact): if `PLAYER_INVINCIBLE != 0`,
      still set the bit (so this contact is tracked and won't re-trigger once invincibility
      expires while still overlapping) but do **not** decrement health. If `PLAYER_INVINCIBLE ==
      0`: this is a valid hit — decrement `PLAYER_HEALTH` (existing logic, unchanged), set this
      slot's own bit, set `PLAYER_INVINCIBLE = INVINCIBILITY_FRAMES`, and apply knockback (below)
      — then stop scanning further slots this frame (mirrors `inf_projectile_hittest`'s own
      "at most one resolved per call" discipline).
  - **New subroutine `inf_invincibility_tick`** — called once per frame from `st_playing`'s
    existing per-frame chain, gated on `COMBAT_MODE`: if `PLAYER_INVINCIBLE != 0`, decrement it
    by 1.
  - **Knockback (inline in `inf_mob_contact_check`'s own hit branch)**: compute
    `dx = mob.x - PLAYER_X`, `dy = mob.y - PLAYER_Y` (the vector *from* the player *to* the mob);
    push the player the opposite direction, on whichever axis has the larger absolute value (the
    same dominant-axis technique `IP-1126`'s own `inf_mob_move` uses, inverted), by
    `KNOCKBACK_DISTANCE` pixels. **Clamped** to the same valid-position bounds
    `check_zone_transition`'s own existing player-position clamp logic already enforces
    (`IP-9090`/`BL-0051`/`BL-0052` precedent) — knockback never pushes the player to an invalid
    off-window coordinate.
  - **`INVINCIBILITY_FRAMES`/`KNOCKBACK_DISTANCE`** — two named Python-level constants (compile-
    time adjustable defaults, mirroring `IP-1126`'s own `MOB_MOVE_INTERVAL`/`MOB_MOVE_STEP`
    precedent) with starting values `INVINCIBILITY_FRAMES = 30` (0.5 seconds at 60fps — long
    enough to be a real window, short enough not to trivialize combat) and
    `KNOCKBACK_DISTANCE = 16` (twice `MOB_MOVE_STEP`'s own per-interval mob-closing distance, so
    knockback reliably outpaces a single mob's own next approach step).

## 7. Implementation Tasks

Ordered: (1) `PLAYER_INVINCIBLE`/`MOB_CONTACT_FLAGS` WRAM constants; (2) `inf_mob_contact_check`'s
own per-slot cooldown-bit read/clear/set logic, layered onto its existing overlap test without
disturbing the existing health-decrement mechanism itself; (3) the invincibility gate on the hit
branch; (4) knockback's dominant-axis push + clamp; (5) `inf_invincibility_tick` + its per-frame
hook; (6) rebuild ROM; (7) author new suite; (8) full suite run (including a direct `T31` re-run,
unmodified except where this package's own gating necessarily changes a prior assumption — name
any such site explicitly, mirroring `IP-1120`'s own `T25`-adjustment precedent); (9) documentation
updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T36: Combat Sub-Mode — Post-Contact Player Protection`**:

- T36.a — the exact `BL-0158` repro: force sustained overlap with the same active mob across
  multiple consecutive frames (no intervening break), confirm exactly one health decrement
  occurs, not a cascade to zero.
- T36.b — knockback fires on a hit: confirm the player's position changes by exactly
  `KNOCKBACK_DISTANCE` on the expected dominant axis, in the direction away from the mob,
  immediately on the hit frame.
- T36.c — invincibility blocks a different mob: force a hit from mob A, then immediately force
  overlap with a distinct mob B (fresh contact, bit clear) while `PLAYER_INVINCIBLE != 0`, confirm
  no second health decrement, and confirm mob B's own bit is still set once invincibility expires
  (so mob B doesn't get a "free" hit the instant invincibility ends while still overlapping).
- T36.d — per-mob cooldown outlasts invincibility: force a hit, force `PLAYER_INVINCIBLE` to 0
  directly (simulating the window's own natural expiry) while still overlapping the *same*
  triggering mob, confirm still no second decrement from that mob — the cooldown, not
  invincibility, is what's actually preventing the re-trigger at this point.
- T36.e — cooldown clears on a genuine break-and-resume: force a hit, force the mob's position
  away (breaking overlap) for at least one frame, confirm its own bit clears, then force overlap
  again, confirm a fresh hit registers (health decrements again) — the cooldown is per-approach,
  not permanent.
- T36.f — invincibility countdown: force `PLAYER_INVINCIBLE` to a known value, tick one frame via
  `inf_invincibility_tick`, confirm it decremented by exactly 1; force it to 1, tick, confirm it
  reaches 0 (fully expired, not clamped above 0).
- T36.g — knockback clamped at a window boundary: force a hit with the player already near the
  edge of the valid position range, confirm the resulting position stays within bounds rather
  than reading as an invalid/wrapped coordinate.
- T36.h — `COMBAT_MODE` off: confirm none of invincibility/knockback/cooldown logic executes
  (non-regression against `T31`'s own established `COMBAT_MODE`-off baseline).
- T36.i — `T31` non-regression: re-run `T31`'s own existing checks, confirming a *single* isolated
  contact (no sustained overlap) still behaves exactly as `IP-1123` originally shipped — one
  decrement, HUD reflects it, zero-health setback still fires correctly. Name explicitly whether
  any `T31` assertion needed adjustment because of this package's own new gating (expected: none,
  since a single-frame contact test never re-enters `inf_mob_contact_check` while still
  overlapping in `T31`'s own existing fixtures — confirm this rather than assume it).
- T36.j — independent live PyBoy drive through the real production per-frame chain, mirroring
  `VR-1121`/`VR-1122`'s own established independent-verification discipline: reproduce the exact
  `BL-0158` scenario (real held-input contact, or a stationary player with an `IP-1126`-moved mob)
  and confirm the fix is perceptible in real play — health drops by exactly one heart, the player
  is visibly displaced, not teleported back to full health within an imperceptible handful of
  frames.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11410 status → Implemented; Notes updated
  with the concrete `INVINCIBILITY_FRAMES`/`KNOCKBACK_DISTANCE` values chosen.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11410 row → `IP-1127`/`T36`,
  Module cell → `asm_game.py` (currently `UNASSIGNED`).
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md`: no Open Question closes here (Open
  Question 4 is `IP-1126`'s own act) — Workflow D step 2's own field content already anticipates
  this package's shipped shape, no further amendment expected unless implementation reveals a
  deviation (name it if so, mirroring `IP-1122`'s own `PROJ_DIR` deviation precedent).
- `docs/architecture/07-data-model.md`: new `PLAYER_INVINCIBLE`/`MOB_CONTACT_FLAGS` rows,
  `0xC6DF`–`0xC6E0`.
- `BL-0158`: mark closed once this package's `09-package-verification` pass confirms the fix live.
- Master Build Plan status row; `packages/INDEX.md` status → `BLOCKED` (on `IP-1123` reaching
  `VERIFIED`) until that lands, then `READY`.

## 10. Definition of Done

- The exact `BL-0158` repro (sustained overlap, same mob) produces exactly one health decrement,
  not a cascade (T36.a).
- Knockback, invincibility, and the per-mob cooldown each independently verified, including the
  cooldown outlasting invincibility's own expiry and correctly clearing only on a genuine
  break-and-resume (T36.b–e).
- `COMBAT_MODE` off and a single isolated (non-sustained) contact both remain unaffected by this
  package's own gating (T36.h/i).
- ROM builds at 32768 bytes; full suite passes; `check_collisions`'s own asymmetric point-in-box
  technique and `MOB_DATA`'s own layout are both unmodified.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, including `T31` unmodified (or every necessary change
      named explicitly, mirroring `IP-1120`'s own `T25` precedent).
- [ ] T36.a–j each present and passing.
- [ ] Direct code read: `check_collisions` and `MOB_DATA`'s own per-slot layout are both
      byte-for-byte unchanged from their currently-shipped form.
- [ ] Direct code read: knockback's own position write is clamped against the same bounds
      `check_zone_transition`'s existing clamp logic enforces — no unclamped direct write.
- [ ] Direct code read: `MOB_CONTACT_FLAGS` is a genuinely separate table from `MOB_DATA`, not a
      widened per-slot stride (this package's own supersession-sweep commitment).
- [ ] FR-11410/RTM/Master-Build-Plan/`packages/INDEX.md` deltas applied exactly as §9 names;
      `BL-0158` closed once this package's own `09` pass confirms the live fix.

## 12. Dependencies

- **`IP-1121`** (`VERIFIED`) — `MOB_DATA`, read for the contact test and knockback direction.
- **`IP-1123`** (`COMPLETE`, **not yet `VERIFIED`**) — `inf_mob_contact_check`/`PLAYER_HEALTH`,
  the exact routine this package modifies. **This package cannot be marked `READY` until
  `IP-1123` reaches `VERIFIED`** (`09-package-verification` Pass 2, owed next session) — building
  against `IP-1123`'s own not-yet-independently-confirmed code would risk compounding an
  unverified defect with a second layer of changes on top of it.

## 13. Risks

- **Blocked on `IP-1123`'s own pending verification** (see §12) — not a defect in this package's
  own design, a genuine sequencing dependency correctly named rather than worked around.
- **`NFR-1500`'s own per-frame cycle budget is not confirmed by this package** — the per-mob
  cooldown-bit check adds real, unmeasured cost on top of every other combat-mode per-frame
  routine; the same standing Analysis obligation `IP-1126`/`IP-1121`/`IP-1122`/`IP-1123` all
  already owe.
- **`INVINCIBILITY_FRAMES`/`KNOCKBACK_DISTANCE`'s own starting values (30 frames, 16 pixels) are
  this package's own pacing judgment call**, not derived from any research/design document —
  `FR-11410` explicitly leaves the exact values to `06`/`07`; retunable later without a
  requirements or architecture change.
- **Interaction with `IP-1126`'s own mob movement, once both ship:** a knocked-back player may be
  immediately approached again by a still-active mob (`IP-1126`'s own per-interval closing step)
  before invincibility fully expires — this is expected, intentional layered behavior (knockback
  buys time, invincibility covers the gap, cooldown is the floor guarantee), not a defect, but
  worth a live-drive check with both packages built (T36.j, once `IP-1126` has also shipped) to
  confirm the combination reads correctly in real play, not just each mechanism in isolation.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `inf_mob_contact_check`'s own pre-package
behavior (a plain per-frame overlap-and-decrement test, `IP-1123`'s own shipped form) is restored
exactly by reverting this package's own diff — no existing WRAM value is reassigned, only new
bytes (`PLAYER_INVINCIBLE`/`MOB_CONTACT_FLAGS`) are claimed and can be safely abandoned.
