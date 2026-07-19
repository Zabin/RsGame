# IP-1129 — Infinite Mode Combat: Weapon-Tier Funding Economy

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1129` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow D step 3a (treasure-spent
weapon-tier funding), a sibling economy action to `IP-1123`'s own shipped healing spend.

## 2. Objective

Close the traceability gap `BL-0147` named: `WEAPON_TIER` (`IP-1122`) ships as a persisted stat
with no way to ever change it. Add a treasure-spent, persistent-purchase funding action —
`RUNNING_TREASURE_COUNT` decrements, `WEAPON_TIER` increases by one, up to its own existing
maximum (3), permanently.

## 3. Requirements Covered

FR-11510 (treasure-spent weapon-tier funding economy) in full.

## 4. Architecture Components

`FS-112` §6 Workflow D step 3a / §10 Data Model Changes (`Weapon`'s own funding mechanism) ·
`R219` (ranged-weapon upgrade/progression conventions — the currency-spent/persistent-purchase
shape this package implements).

## 5. Interfaces

- **`RUNNING_TREASURE_COUNT`** (existing, 16-bit, `IP-1103`/`IP-1123`, unchanged in shape) — a
  second consumer alongside `inf_heal_spend`, decremented via the identical 16-bit-borrow
  technique `inf_heal_spend` already established (check low byte for a needed high-byte borrow
  *before* decrementing). No second ledger.
- **`WEAPON_TIER`** (existing, `0xC6D9`, `IP-1122`, unchanged in shape) — this package's sole
  mutator; read by `inf_projectile_hittest` (`IP-1122`, unchanged, not touched by this package).
- **`COMBAT_MODE`** (existing, unchanged) — gates this action exactly like every other
  combat-sub-mode routine.
- **`SCORE_DIRTY`** (existing, `IP-1123`'s own established convention) — set whenever
  `RUNNING_TREASURE_COUNT`/`WEAPON_TIER`-adjacent state changes, mirroring `inf_heal_spend`'s own
  precedent so the HUD redraws promptly (no visible `WEAPON_TIER` HUD element exists yet — this
  is the same forward-looking discipline `inf_heal_spend` already applied for `PLAYER_HEALTH`).

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New subroutine `inf_tier_spend`** — gated on `COMBAT_MODE` and `RUNNING_TREASURE_COUNT > 0`
    (16-bit check, mirroring `inf_heal_spend`'s own exact structure verbatim). Decrements
    `RUNNING_TREASURE_COUNT` by 1 using the identical 16-bit-borrow technique. **Unconditionally**
    (mirroring `FR-11500`'s own real shipped precedent, `T31.d2` — spending is not gated on
    `WEAPON_TIER`'s own current value, so it still spends even at the cap): sets `SCORE_DIRTY`,
    then checks `WEAPON_TIER < 3`; if so, increments it; if already at 3, the treasure was still
    spent but `WEAPON_TIER` is left unchanged (floored, not a no-op on the spend itself).
  - **No new WRAM.** Both fields this package touches (`RUNNING_TREASURE_COUNT`, `WEAPON_TIER`)
    already exist.
  - **Not called from anywhere in this package's own control flow** — mirrors `inf_heal_spend`'s
    own "defined and exposed, no real input binding yet" precedent (`BL-0148`'s own still-
    unresolved gap; this package's own action shares the identical unresolved-binding class, named
    in §13, not invented a binding for).

## 7. Implementation Tasks

Ordered: (1) `inf_tier_spend` subroutine, mirroring `inf_heal_spend`'s own structure field-for-field
(currency-check → borrow-safe decrement → `SCORE_DIRTY` → capped increment); (2) rebuild ROM; (3)
author new suite; (4) full suite run; (5) documentation updates (§9).

**Supersession sweep:** this package introduces no new model and widens no existing one —
`WEAPON_TIER`'s own shape (1 byte, range 1-3, per its existing WRAM comment) is unchanged, only a
second writer is added. Confirmed by direct grep: `WEAPON_TIER`'s only other writer is the boot-init
block (`IP-1122`); its only reader is `inf_projectile_hittest` (unchanged, reads the current value
each hit, no caching). No supersession risk.

## 8. Tests to Add

New `test_rom.py` suite **`T38: Combat Sub-Mode — Weapon-Tier Funding Economy`**:

- T38.a — tier-spend decrements `RUNNING_TREASURE_COUNT` by exactly 1 and increases `WEAPON_TIER`
  by exactly 1 (mirrors `T31.d`'s own established shape for the sibling healing-spend action).
- T38.b — spot check: tier-spend at `WEAPON_TIER == 3` still decrements `RUNNING_TREASURE_COUNT`
  by 1 but does not push `WEAPON_TIER` past 3 (mirrors `T31.d2`'s own exact precedent — confirms
  this is the spend-even-at-cap convention, not a no-op).
- T38.c — tier-spend at `RUNNING_TREASURE_COUNT == 0` is a genuine no-op: neither
  `RUNNING_TREASURE_COUNT` nor `WEAPON_TIER` changes (mirrors `T31.e`'s own precondition-failure
  shape).
- T38.d — `COMBAT_MODE` off: `inf_tier_spend` is a complete no-op (mirrors `T31.f`'s own
  established `COMBAT_MODE`-off pattern).
- T38.e — persistence: a tier increase survives a mob-contact setback (`inf_health_setback`,
  `IP-1123`, confirmed to touch only `PLAYER_HEALTH`/`PLAYER_X`/`PLAYER_Y`, never `WEAPON_TIER`)
  and a save/load round trip (`WEAPON_TIER` already persisted since `IP-1122`/whichever package
  implements `FR-11600`'s own save-write; if `IP-1124` has not shipped yet when this package
  builds, this check is scoped to the in-session, non-save-boundary persistence half only, named
  explicitly rather than silently assumed).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11510 status → Implemented; Notes updated
  with the concrete spend-rate (1 treasure per tier, mirroring `FR-11500`'s own 1-for-1 rate).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11510 row → `IP-1129`/`T38`.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md`: metadata-only status update (no field
  content changes — already fully amended at `06-feature-specification`, 2026-07-19).
- Master Build Plan status row; `packages/INDEX.md` status → `NOT STARTED` (unblocked).

## 10. Definition of Done

- Tier-spend decrements treasure and increases `WEAPON_TIER`, floored at 3, spending even at the
  cap (not a no-op) — matching `FR-11500`'s own shipped precedent exactly (T38.a–b).
- Zero-treasure and `COMBAT_MODE`-off cases are both genuine no-ops (T38.c–d).
- A tier increase persists across a setback and (where reachable) a save/load round trip (T38.e).
- ROM builds at 32768 bytes; full suite passes; `WEAPON_TIER`'s own existing shape (1 byte, 1-3)
  is unchanged — confirmed by direct code read.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T38.a–e each present and passing.
- [ ] Direct code read: `inf_projectile_hittest`/`WEAPON_TIER`'s own boot-init block both
      unmodified by this package's own diff.
- [ ] FR-11510/RTM/Master-Build-Plan/`packages/INDEX.md` deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1122`** (`VERIFIED`) — `WEAPON_TIER`, this package's sole mutator.
- **`IP-1103`** (`VERIFIED`) — `RUNNING_TREASURE_COUNT`, this package's second consumer alongside
  `inf_heal_spend`.

## 13. Risks

- **Input-binding gap, not resolved here**: mirrors `FR-11500`'s own still-open `BL-0148` — this
  package's own tier-spend action has no obviously free input button either. `FS-112`'s own Risks
  (§18, amended 2026-07-19) already recommends a future `06`/`07` pass consolidate both spend
  actions behind a single shared UI rather than each package independently re-discovering the
  same gap; not this package's own scope to resolve.
- **`NFR-1500`'s own per-frame cycle budget is not confirmed by this package** — `inf_tier_spend`
  is not itself a per-frame routine (called only on an eventual explicit player action, not every
  frame), so its own marginal cost is small relative to the tranche's other per-frame additions —
  named for completeness, not a significant new contributor.
- ROM budget: one small new subroutine, no new WRAM — expected minimal, re-affirmed at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `inf_tier_spend` has no call site anywhere
in this package's own control flow (mirrors `inf_heal_spend`'s own precedent) — removing it is a
clean, fully isolated revert with no data migration, since `WEAPON_TIER`'s own existing shape and
every other consumer are entirely untouched.
