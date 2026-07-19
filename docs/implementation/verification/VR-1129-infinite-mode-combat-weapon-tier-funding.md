# VR-1129 — Infinite Mode Combat: Weapon-Tier Funding Economy

> Independent verification of [`IP-1129`](../packages/IP-1129-infinite-mode-combat-weapon-tier-funding.md)
> against the shipped tree. Produced by `09-package-verification`.

## Package

- **ID:** `IP-1129` — Infinite Mode Combat: Weapon-Tier Funding Economy
- **Implementing commit:** `95391e5` ("feat(combat): IP-1129 — weapon-tier funding economy
  (FR-11510)", 2026-07-19)
- **Commit verified at:** `efc9968` (tree head at verification time; unrelated verification/
  journal commits landed afterward, none touching this package's own files)
- **Independence:** fresh session; no prior work on `IP-1129` performed in this session.

## Result

**VERIFIED** — 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Tier-spend decrements treasure and increases `WEAPON_TIER`, floored at 3, spending even at the cap (not a no-op) | `inf_tier_spend` (`asm_game.py` lines 3773-3804) read directly: `SCORE_DIRTY`/decrement always execute before the `CP_n(3)` cap check, so a cap-hit spend still consumes treasure — byte-for-byte structural match to `inf_heal_spend`'s own already-`VERIFIED` precedent. `T38.a`/`b` pass | Pass |
| Zero-treasure and `COMBAT_MODE`-off cases are both genuine no-ops | Lines 3774: `COMBAT_MODE` gate, unconditional `RET_Z` first instruction. Lines 3776-3777: 16-bit zero-check (`RUNNING_TREASURE_COUNT`/`+1` both `OR_A`, `RET_Z` on the high byte) before any write. `T38.c`/`d` pass | Pass |
| A tier increase persists across a setback and (where reachable) a save/load round trip | `inf_health_setback` (`IP-1123`) confirmed by direct read to touch only `PLAYER_HEALTH`/`PLAYER_X`/`PLAYER_Y` — no `WEAPON_TIER` write anywhere in its body. `T38.e` passes, correctly scoped to the in-session half only (`FR-11600` save/load remains unimplemented, named explicitly in both the package and the test's own comment, not silently assumed) | Pass |
| ROM builds at 32768 bytes; full suite passes; `WEAPON_TIER`'s own existing shape (1 byte, 1-3) unchanged | Confirmed (see Test run); `WEAPON_TIER`'s own WRAM declaration line untouched by this commit's diff | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes, valid header | Confirmed: `python3 build_rom.py` → "Wrote 32768 bytes → BunnyQuest.gbc" | Pass |
| G5: full `test_rom.py` suite passes | 387/387 passed, 0 failed (fresh session) | Pass |
| `T38.a`–`e` each present and passing | All 5 individual `check()` calls confirmed present and passing | Pass |
| Direct code read: `inf_projectile_hittest`/`WEAPON_TIER`'s own boot-init block both unmodified by this package's own diff | Confirmed — `git show 95391e5 -- asm_game.py` is **purely additive** (`grep -c '^-[^-]'` on the diff returns `0`); neither routine's own label range appears anywhere in the changed hunk (the entire diff is one new subroutine, `inf_tier_spend`, inserted between `inf_heal_spend` and `inf_health_hud_draw`) | Pass |
| FR-11510/RTM/Master-Build-Plan/`packages/INDEX.md` deltas applied exactly as §9 names | `FR-11510` → "Implemented `IP-1129` 2026-07-19, save/load half pending `FR-11600`" (honestly scoped, not overclaimed); RTM row `FR-11510 \| ... \| IP-1129 \| T38.a–e`; Master Build Plan/`packages/INDEX.md` rows present and accurate | Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11510 | `inf_tier_spend` | `T38.a`-`e` | `FR-11510 \| Treasure-spent weapon-tier funding economy (delta 2026-07-19, BL-0147/BL-0155 — Should, Implemented IP-1129 2026-07-19, save/load half pending FR-11600) \| R219 \| ADS-002 §Domain Model \| — \| asm_game.py \| FS-112 \| IP-1129 \| T38.a–e` | Pass |

## Test run

- `python3 build_rom.py` → 32768 bytes written (32414 used).
- `python3 test_rom.py` → **387/387 passed, 0 failed** (fresh session).
- `T38.a`-`e` individually confirmed present and passing (5/5).

## Scope audit

Implementing commit `95391e5` touched `asm_game.py` (one new subroutine, no existing line
removed or modified — confirmed by `grep -c '^-[^-]'` returning `0` on the commit's own diff),
`test_rom.py` (new `T38` suite only), and the doc files named in §9 plus standard build/test
artifacts. No excursion — `inf_projectile_hittest`, `WEAPON_TIER`'s boot-init block,
`inf_heal_spend`, and `inf_health_setback` all confirmed byte-for-byte untouched.

## Independent live drive

`inf_tier_spend` is not itself a per-frame routine and has no player-reachable call site yet
(named explicitly in both the package's own §6/§13 and `BL-0148`'s still-open input-binding gap)
— there is no real production call chain to drive it through today, so `T38`'s own direct-invoke
force-testing (mirroring `inf_heal_spend`'s own already-`VERIFIED` precedent for the identical
class of gap) is the correct and only available verification method, not a shortfall. No
tunable/generated parameter is referenced by this package's DoD, so the `BL-0055` live-drive rule
does not apply. The structural mirror to `inf_heal_spend` was independently re-derived
side-by-side from the assembly (both routines quoted and compared line-for-line during the
Definition-of-Done audit above), not taken from the Implementation Summary's own claim.

## Findings

None.

## Ledger status

Per this skill's own rule, `IP-1129` advances `COMPLETE → VERIFIED` on the Master Build Plan and
`packages/INDEX.md`. No dependent package names `IP-1129` as a dependency, so no other package's
readiness changes as a result of this verification. This closes the fourth and final
`COMPLETE`-but-unverified package from this session's start — the pipeline's `08-code-implementation`
build queue is now clean of verification debt.
