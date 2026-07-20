# IP-8030 — Treasure-Spend Gate-and-Decrement Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8030` — refactors `asm_game.py`, filed from **`BL-0172`** (`refactor`, `SCHEDULED`).

## 2. Objective

`inf_heal_spend` and `inf_tier_spend` each inline the identical gate-and-decrement prefix: check
`COMBAT_MODE`, check `RUNNING_TREASURE_COUNT` (16-bit) is nonzero, decrement it with borrow, set
`SCORE_DIRTY`. Extract into `treasure_spend_gate_and_decrement`.

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

`ADR-0003` (unaffected, stays within `asm_game.py`); `R307`.

## 5. Interfaces

- **`inf_heal_spend`** (`IP-1123`, existing) — its own gate/decrement block (`COMBAT_MODE` check
  through the `SCORE_DIRTY` write) replaced by `CALL('treasure_spend_gate_and_decrement');
  RET_Z()`. The subsequent `PLAYER_HEALTH` capped-increment tail is unchanged.
- **`inf_tier_spend`** (`IP-1129`, existing) — identical replacement; the subsequent
  `WEAPON_TIER` capped-increment tail is unchanged.
- **New subroutine `treasure_spend_gate_and_decrement`** — **Contract:** no input registers.
  Checks `COMBAT_MODE`; if zero, returns immediately with `Z` **set** (signal: caller should
  `RET` without spending). Checks `RUNNING_TREASURE_COUNT` (16-bit); if zero, returns with `Z`
  **set** (same signal). Otherwise decrements `RUNNING_TREASURE_COUNT` (16-bit, with borrow),
  sets `SCORE_DIRTY`, and returns with `Z` **clear** (signal: caller should apply its own effect).
  **Correctness note (found during planning, guarded explicitly):** the final `Z`-clear state
  must be produced by an explicit `OR_A()` immediately before `RET()`, not left to whatever flag
  state the preceding `DEC_A` happened to leave — `DEC_A` on `RUNNING_TREASURE_COUNT`'s low byte
  can itself set `Z` (if the count was exactly 1), which would corrupt the success signal if not
  re-asserted. **Clobbers:** `A`. **Preserves:** nothing needed by either caller (both callers'
  own tails re-read their own target stat fresh via `LD_A_nn`).

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New subroutine `treasure_spend_gate_and_decrement`**, placed near `inf_heal_spend` (its
    first caller).
  - **`inf_heal_spend`**: replace lines ~3938-3948 (from the `COMBAT_MODE` check through the
    `SCORE_DIRTY` write) with `CALL('treasure_spend_gate_and_decrement'); RET_Z()`. The
    `PLAYER_HEALTH` cap/increment tail (currently lines ~3949-3952) is unchanged.
  - **`inf_tier_spend`**: identical replacement of lines ~3968-3978; the `WEAPON_TIER` tail
    (~3979-3982) unchanged.

## 7. Implementation Tasks

Ordered: (1) author `treasure_spend_gate_and_decrement`, with the explicit `OR_A()` before its
final `RET()`; (2) rewrite `inf_heal_spend`; (3) rewrite `inf_tier_spend`; (4) rebuild, record
byte delta; (5) run full suite unmodified; (6) direct-diff both routines' own remaining tails
against the pre-refactor tree; (7) documentation updates (§9, none expected).

## 8. Tests to Add

**None.** `T31.d`/`T31.d2`/`T31.e`/`T31.f` (heal-spend) and `T38.a`-`d` (tier-spend) already
exercise every branch of both routines — including the specific "spends even at the cap" case
(`T31.d2`/`T38.b`) that depends on the gate-and-decrement always running independent of the
target stat's own cap state. Full suite passing unmodified is the acceptance bar.

## 9. Documentation Updates

None expected.

## 10. Definition of Done

- `treasure_spend_gate_and_decrement` exists, called from both `inf_heal_spend` and
  `inf_tier_spend`; neither site's own inlined gate/decrement block remains.
- ROM builds at exactly 32768 bytes; full suite passes unmodified.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes.
- [ ] G5: full suite passes, zero `test_rom.py` diff.
- [ ] Equivalence contract: diff touches only the new subroutine + the two replaced blocks.
- [ ] Direct code read: the subroutine's final `RET()` is preceded by an explicit `OR_A()`, not
      relying on `DEC_A`'s own incidental flag state.
- [ ] `T31.d`/`T31.d2`/`T31.e`/`T31.f` and `T38.a`-`d` all still pass, specifically re-confirming
      the "spends even at the cap" behavior (`T31.d2`/`T38.b`) survives the refactor.

## 12. Dependencies

None.

## 13. Risks

- **Flag-correctness risk** (Low, already mitigated in design): the explicit `OR_A()` before the
  success-path `RET()` is required, not optional — named explicitly in §5/§11 so it isn't
  dropped during implementation as "redundant."
- **ROM budget** (Low, favorable): expected net decrease.

## 14. Rollback Considerations

Revert `asm_game.py`'s three touched regions and rebuild.
