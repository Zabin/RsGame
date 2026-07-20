# VR-8010 — Point-in-Box Hit-Test Deduplication

## Package

- **ID:** IP-8010 — [Point-in-Box Hit-Test Deduplication](../packages/IP-8010-point-in-box-hittest-deduplication.md) (refactor)
- **Implementing commit:** `49ec0d5`
- **Verified:** 2026-07-20, same session as the implementing commit.

## Independence note

**Degraded independence, explicitly accepted.** This verification runs in the same conversation
session as `IP-8010`'s own implementation, at the user's own direct instruction to keep iterating
refactoring work without stopping for per-step confirmation. Per this skill's own rule, that
instruction is treated as the user's explicit acceptance of the degraded-independence caveat.
Mitigated by re-deriving every claim directly from the tree (not the implementation session's own
summary) and by this package's own unusually strong equivalence evidence (zero test-file diff, an
exact pre/post ROM byte-count match).

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `pib_reg_minus_origin` exists, called from both `check_collisions` and `inf_mob_contact_check`; neither site's inlined test block remains | `asm_game.py:1221` (`CALL('pib_reg_minus_origin')` in `check_collisions`), `asm_game.py:3778` (same call in `inf_mob_contact_check`), subroutine body at `asm_game.py:1323` | PASS |
| `inf_projectile_hittest` byte-for-byte unchanged | `git show 49ec0d5 -- asm_game.py \| grep -c inf_projectile_hittest` → only a comment reference, zero lines inside its own body touched | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Rebuilt this run: 32768 bytes, 32670 used (identical to the pre-refactor baseline); 404/404 | PASS |
| Byte delta measured and recorded | `git commit 49ec0d5`'s own message and the Master Build Plan record: net-zero at the section-total level; confirmed by this run's own independent rebuild producing the identical SHA-256 (`f5528d...`) as the implementing session's own post-edit build | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Rebuilt this run: 32768 bytes | PASS |
| G5: full suite passes, zero test-file changes | `git diff` of `test_rom.py` against the pre-refactor tree (`fb049d4`): empty | PASS |
| Equivalence contract: diff touches only the three named regions | `git show 49ec0d5 --stat` and direct diff inspection: `asm_game.py` only, hunks at the new subroutine + the two call-site rewrites, nothing else | PASS |
| `pib_reg_minus_origin`'s `Z`-flag convention correctly consumed at both sites | `check_collisions`: `JR_NZ('cc_skip')` (`asm_game.py:1222`); `inf_mob_contact_check`: `JP_NZ('imcc_skip')` (`asm_game.py:3779`) — `JP` correctly preserved at the site whose body exceeds `JR`'s range, per the package's own §13 risk note | PASS |
| `inf_projectile_hittest` zero diff lines | Confirmed above | PASS |
| `T8`/`T36` reconfirmed | `test_results.txt` this run: all `T8.*` and `T36.*` checks `[PASS]` | PASS |

## Requirements audit

Not applicable — this package covers no `FR`/`NFR` (pure structural refactor, per its own §3).

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used)
  → sha256: f5528df7dae35858457a500ccbdb462814bf2b4e2de16028f1ede5fdda17b23d
    (identical to the implementing session's own post-edit build)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed
```

## Scope audit

`git show 49ec0d5 --stat`: `asm_game.py` (+41/-25), `BunnyQuest.gbc` (rebuild), plus the exact
Master Build Plan / `packages/INDEX.md` rows the package's own §9 (implicitly, via the standard
status-flip convention) names. No scope excursion.

## Findings

None.
