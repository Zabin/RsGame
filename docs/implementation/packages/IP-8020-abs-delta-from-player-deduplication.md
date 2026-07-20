# IP-8020 — Absolute-Delta-From-Player Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8020` — refactors `asm_game.py`, filed from **`BL-0171`** (`refactor`, `SCHEDULED`). No
owning `FS-xxx`.

## 2. Objective

`inf_mob_move` and the knockback block inside `inf_mob_contact_check` each inline the identical
"absolute delta from `PLAYER_X`/`PLAYER_Y`" computation (`ax = |point_x − PLAYER_X|`,
`ay = |point_y − PLAYER_Y|`), used to pick the dominant axis for the mob's own approach step and
the knockback's own push direction respectively. The second site's own existing comment already
names the duplication ("Mirrors `inf_mob_move`'s own dominant-axis magnitude computation").
Extract the shared computation into one subroutine, `abs_delta_from_player`.

## 3. Requirements Covered

None — structural only, no observable behavior change.

## 4. Architecture Components

`ADR-0003` (one-job-per-file — unaffected, this stays within `asm_game.py`); `R307` (refactoring
discipline, equivalence-proof method).

## 5. Interfaces

- **`inf_mob_move`** (`IP-1126`, existing) — its own `imv_ax_zero`/`imv_ax_neg`/`imv_ax_done`/
  `imv_ay_zero`/`imv_ay_neg`/`imv_ay_done` block replaced by `CALL('abs_delta_from_player')`.
  `E`/`D` (mob x/y) are already loaded by this routine's own existing per-slot read immediately
  above — unchanged.
- **`inf_mob_contact_check`**'s own knockback block (`IP-1127`, existing) — identical
  replacement of its own `ikb_ax_*`/`ikb_ay_*` block. `E`/`D` (mob x/y) already hold the current
  slot's position from this routine's own existing loop read — unchanged.
- **New subroutine `abs_delta_from_player`** — the only new interface. **Contract:** Input
  `E` = point_x, `D` = point_y (already loaded by each caller's own existing per-slot read).
  Computes `C = |E − PLAYER_X|`, `L = |D − PLAYER_Y|` — the exact same three-way
  zero/negative/positive branch each site's own inlined code already used (unsigned point vs.
  `PLAYER_X`/`Y`, `CP`+`JR_Z`/`JR_C` to pick the sign, `SUB` in the matching direction).
  **Returns:** result in `C` (x-axis) and `L` (y-axis) — mirrors both callers' own existing
  post-computation register expectations exactly (both immediately compare `C` vs `L` to pick the
  dominant axis). **Clobbers:** `A`, `H`. **Preserves:** `B`, `D`, `E` — both callers re-read
  `E`/`D` again in their own axis-specific branch immediately after (`imv_axis_x`/`imv_axis_y`,
  `ikb_axis_x`/`ikb_axis_y`), and both callers' own existing comments confirm `C` is free scratch
  and `B` is safely stacked (via each routine's own pre-existing `PUSH_BC`) at the point this
  subroutine is called.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New subroutine `abs_delta_from_player`**, placed near `inf_mob_move` (its first caller).
  - **`inf_mob_move`**: replace the `imv_ax_zero`/`imv_ax_neg`/`imv_ax_done`/`imv_ay_zero`/
    `imv_ay_neg`/`imv_ay_done` label block (~line 3544-3572) with a single
    `CALL('abs_delta_from_player')`. The subsequent coincident-check
    (`imv_pick_axis`'s own `LD_A_C(); OR_A(); JR_NZ(...)`) and dominant-axis compare
    (`LD_A_C(); CP L; JR_C(...)`) are unchanged — they already consume `C`/`L` exactly as this
    subroutine produces them.
  - **`inf_mob_contact_check`**'s knockback block: replace the equivalent `ikb_ax_*`/`ikb_ay_*`
    block (~line 3820-3846) with the same `CALL('abs_delta_from_player')`. The subsequent
    `LD_A_C(); CP L; JR_C('ikb_axis_y')` dominant-axis compare is unchanged.
  - **All other routines**: unchanged. In particular `inf_mob_move`'s own timer/loop scaffolding
    and `inf_mob_contact_check`'s own point-in-box test (already refactored under `IP-8010`, via
    `pib_reg_minus_origin`), hit/health logic, and invincibility/cooldown bit handling are
    untouched.

## 7. Implementation Tasks

Ordered: (1) author `abs_delta_from_player`; (2) rewrite `inf_mob_move`'s own block to call it;
(3) rewrite the knockback block's own equivalent to call it; (4) rebuild ROM, record the byte
delta; (5) run the full `test_rom.py` suite unmodified; (6) direct-diff both routines' own
surrounding code (everything outside the replaced blocks) against the pre-refactor tree to
confirm byte-for-byte identity outside the two touched blocks plus the new subroutine; (7)
documentation updates (§9, none expected).

## 8. Tests to Add

**None.** `T35` (mob movement) and `T36` (post-contact protection, including `T36.b`'s own
knockback-direction assertion) already exercise both call sites' observable behavior on every
axis case (dominant-X, dominant-Y, coincident). The full suite passing unmodified is the
acceptance bar.

## 9. Documentation Updates

None expected — no requirement, WRAM/SRAM layout, or cross-module interface changes. `GDS-07`/
`ADS-002` describe the dominant-axis *behavior* (which this package doesn't change), not the
opcode-level implementation.

## 10. Definition of Done

- `abs_delta_from_player` exists, called from both `inf_mob_move` and the knockback block; neither
  site's own inlined `a[xy]_*` block remains.
- ROM builds at exactly 32768 bytes; full `test_rom.py` suite passes, unmodified, at its current
  count.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full suite passes, zero `test_rom.py` diff.
- [ ] Equivalence contract: implementing diff touches only the new subroutine + the two replaced
      blocks — confirmed by direct diff.
- [ ] Direct code read: `C`/`L` output convention correctly consumed by both callers' own
      unchanged dominant-axis compare (`LD_A_C(); CP L`).
- [ ] Direct code read: `E`/`D` still hold the correct mob position when each caller's own
      axis-specific branch re-reads them after the call.
- [ ] `T35`'s own movement checks and `T36.b`'s own knockback-direction check both still pass,
      reconfirming real behavior on both axes, not just suite count.

## 12. Dependencies

None.

## 13. Risks

- **ROM budget** (Low, favorable): expected net decrease, larger in magnitude than `IP-8010`'s
  own (the duplicated block here is roughly 2.5x the size) — measured, not assumed, at build
  time.
- **Register-liveness risk** (Low, already checked during planning): both call sites' own
  existing comments confirm `C` is free scratch and `B` is safely stacked at the point of the
  call — re-confirmed by direct read before authoring this package, not assumed from the
  comments alone.

## 14. Rollback Considerations

Revert `asm_game.py`'s three touched regions and rebuild — both routines return to their exact
pre-refactor inlined form; no WRAM/SRAM address or requirement is affected.
