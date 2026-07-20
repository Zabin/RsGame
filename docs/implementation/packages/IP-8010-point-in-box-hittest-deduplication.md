# IP-8010 — Point-in-Box Hit-Test Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8010` — refactors `asm_game.py`, filed from **`BL-0170`** (`refactor`, `SCHEDULED`). No
owning `FS-xxx`; this is structural cleanup, not new behavior.

## 2. Objective

`check_collisions` and `inf_mob_contact_check` each inline the identical point-in-box hit test
(`0 <= point_x − origin_x < 8` and `0 <= point_y − origin_y < 16`, origin = `PLAYER_X`/`PLAYER_Y`,
point = the per-slot value the loop just read into `E`/`D`). Extract the shared logic into one
subroutine, `pib_reg_minus_origin`, and call it from both sites. `inf_projectile_hittest`'s own
inlined test computes the arithmetic in the *reverse* order (WRAM-held point minus register-held
origin) — a genuinely different predicate, not a duplicate — and is explicitly **out of scope**;
see §13 for why extracting it would not be a refactor win.

## 3. Requirements Covered

None. This package touches no `FR`/`NFR` — `check_collisions`'s and `inf_mob_contact_check`'s
own observable behavior (which requirements they satisfy) is unchanged bit-for-bit.

## 4. Architecture Components

`ADR-0003` (one-job-per-file decomposition — this package doesn't move code between modules, only
de-duplicates within `asm_game.py`, so `ADR-0003` is unaffected); encyclopedia topic `R307`
(refactoring discipline, grounds the equivalence-proof method this package's own §11 requires).

## 5. Interfaces

- **`check_collisions`** (`FEAT-3000`, existing) — its own point-in-box block (the two
  `LD_A_nn(PLAYER_X)`/`SUB`/`CP_n(8)` and `PLAYER_Y`/`CP_n(16)` pairs) replaced by a `CALL
  pib_reg_minus_origin` + branch on the returned `Z` flag. No other part of `check_collisions`
  changes.
- **`inf_mob_contact_check`** (`IP-1123`/`IP-1127`, existing) — identical replacement of its own
  point-in-box block. The routine's own cooldown/invincibility/knockback logic downstream of the
  test is untouched.
- **New subroutine `pib_reg_minus_origin`** — the only new interface this package introduces.
  **Contract:** Input `HL` = address of a contiguous WRAM `(origin_x, origin_y)` byte pair;
  `E` = point_x, `D` = point_y (already loaded by the caller's own existing per-slot read — no
  change to how either caller loads them). Computes `E − (HL)` and `D − (HL+1)`, each checked
  against its own bound (8, 16). **Returns:** `Z` flag **set** if the point lies inside the box
  (both checks passed), **clear** otherwise — mirrors this codebase's existing `OR_A`/`JR_Z`
  flag-branch idiom used throughout `asm_game.py`, so both call sites' own surrounding control
  flow needs only a mechanical `JR_NZ`/`JP_NZ` substitution for their prior `JR_NC`/`JP_NC`.
  **Clobbers:** `A`, `HL` (advanced by one on both exit paths — callers that still need the
  original `HL` value after the call must not rely on it being preserved). **Preserves:** `B`,
  `C`, `D`, `E` — both call sites already have `BC` safely stashed on the stack at the point of
  the test (via their own pre-existing `PUSH_BC`), and neither needs `D`/`E` again after a
  successful test, so this clobber list is a safe fit for both, verified by direct read of each
  site's own post-test code path.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New subroutine `pib_reg_minus_origin`**, placed near `check_collisions` (its first, and
    conceptually primary, caller) — exact placement and label-ordering are `08-refactoring`'s own
    call, so long as both callers can `CALL` it (SM83 has no forward-reference restriction on
    labels, so placement doesn't affect correctness).
  - **`check_collisions`**: replace lines ~1223-1230 (the inlined test) with `LD_HL_nn(PLAYER_X);
    CALL('pib_reg_minus_origin'); JR_NZ('cc_skip')`. `E`/`D` are already loaded with the item's
    `x`/`y` by the existing loop read immediately above (line ~1207-1208) — no change needed
    there.
  - **`inf_mob_contact_check`**: replace lines ~3758-3763 (the inlined test) with the same
    `LD_HL_nn(PLAYER_X); CALL('pib_reg_minus_origin'); JP_NZ('imcc_skip')` pattern (this site
    uses `JP` not `JR` for its skip branch, per its own existing comment: "body now exceeds JR's
    own +-127 range" — preserve `JP`, do not weaken to `JR`). `E`/`D` already hold the mob's
    `x`/`y` from this routine's own existing loop read (line ~3750-3751).
  - **`inf_projectile_hittest`**: **unchanged.** Confirmed out of scope — see §13.

## 7. Implementation Tasks

Ordered: (1) author `pib_reg_minus_origin`; (2) rewrite `check_collisions`'s own test block to
call it; (3) rewrite `inf_mob_contact_check`'s own test block to call it; (4) rebuild ROM, record
the exact byte delta; (5) run the full `test_rom.py` suite unmodified — **no test file change is
expected or permitted** by this package (a passing suite with zero test-file edits is itself part
of the equivalence proof); (6) direct-diff `check_collisions`/`inf_mob_contact_check`'s own
surrounding code (everything outside the replaced block) against the pre-refactor tree to confirm
byte-for-byte identity outside the two touched blocks; (7) documentation updates (§9).

## 8. Tests to Add

**None.** This is the refactor's own defining constraint: `T8` (collision/score, exercises
`check_collisions`) and `T36` (post-contact protection, exercises `inf_mob_contact_check`) already
cover both call sites' own observable behavior exhaustively. If either suite needs a *new* check
to prove equivalence, that is itself a signal the existing coverage was insufficient *before* this
package — a finding for `07`/`04`, not a task this refactor absorbs. The full existing suite
passing unmodified, byte-for-byte, is the acceptance bar.

## 9. Documentation Updates

- None required. This package changes no requirement, no architecture decision, no WRAM/SRAM
  layout, no interface any other package depends on. `GDS-09`'s own interface catalog doesn't
  currently enumerate `asm_game.py`'s internal subroutines individually (only cross-module
  contracts), so `pib_reg_minus_origin` needs no new GDS-09 entry.
- Master Build Plan / `packages/INDEX.md` status row (mechanical, not a "documentation update" in
  the content sense).

## 10. Definition of Done

- `pib_reg_minus_origin` exists, is called from both `check_collisions` and
  `inf_mob_contact_check`, and neither site's own inlined test block remains.
- `inf_projectile_hittest` is byte-for-byte unchanged.
- ROM builds at exactly 32768 bytes; full `test_rom.py` suite passes, unmodified, at its current
  count.
- The byte delta from the pre-refactor tree is measured and recorded (predicted: a net decrease;
  see §13).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, **zero test-file changes** (a diff of `test_rom.py`
      against the pre-refactor tree must be empty).
- [ ] **Equivalence contract:** the implementing diff against the pre-refactor tree touches only
      (a) the new `pib_reg_minus_origin` label body, (b) `check_collisions`'s own test block, (c)
      `inf_mob_contact_check`'s own test block — confirmed by direct diff, no other line changed.
      Not byte-identical (a `CALL`/`RET` restructuring necessarily changes byte layout) — the
      **predicted byte delta** (§13) is recorded and the actual measured delta compared against
      it, with any material difference (not just alignment-padding noise) explained.
- [ ] Direct code read: `pib_reg_minus_origin`'s own `Z`-flag return convention is correctly
      consumed at both call sites (`JR_NZ`/`JP_NZ`, matching each site's own pre-existing branch
      *direction* — fail branches to the same `..._skip` labels as before).
- [ ] Direct code read: `inf_projectile_hittest` — zero diff lines.
- [ ] `T8`'s own collision checks and `T36`'s own contact/knockback/cooldown checks all still
      pass, reconfirming both refactored call sites' real behavior end-to-end, not just that the
      suite count is unchanged.

## 12. Dependencies

None. Both call sites live entirely within `asm_game.py`; no other package's own `VERIFIED`
status is a precondition.

## 13. Risks

- **Scope-narrowing risk (already resolved in this planning pass, named for the record):** the
  originating backlog entry (`BL-0170`) hypothesized all three call sites were duplicates.
  Reconstructing the actual arithmetic during this planning pass found `inf_projectile_hittest`
  computes the operands in the opposite order (a real, different predicate, not interchangeable)
  — extracting it into a *second* subroutine would add one `CALL` (~3 bytes) plus a new ~14-16
  byte shared body for a single caller, a **net ROM cost**, not a saving, since there is nothing
  else to de-duplicate it against. Left unmodified; not a deferred TODO, a deliberate scope
  boundary.
- **`inf_mob_contact_check`'s own `JP` requirement** (Low): its skip branch already exceeds `JR`'s
  ±127-byte range per its own existing comment — the replacement `CALL`+`JP_NZ` sequence must
  preserve `JP`, not regress to `JR`, or the build will fail range validation at assembly time
  (a hard, self-detecting failure, not a silent risk).
- **ROM budget** (Low, favorable): expected net decrease, a positive contribution against the
  tranche's current 98-byte headroom (`VR-1127`) — not a risk to the budget, but the *predicted
  magnitude* (roughly 2×(9-10 byte inline − 3 byte `CALL`) − 1×(14-16 byte shared body) ≈ 2-4
  bytes net decrease, a rough estimate to be replaced by the actual measured figure, not treated
  as a target to hit) should be sanity-checked against the real build rather than assumed exact.

## 14. Rollback Considerations

Revert `asm_game.py`'s three touched regions (the new subroutine plus the two call-site rewrites)
and rebuild — `check_collisions`/`inf_mob_contact_check` return to their exact pre-refactor
inlined form; no WRAM/SRAM address, save format, or requirement is affected by either direction.
