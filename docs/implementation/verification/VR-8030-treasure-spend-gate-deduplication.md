# VR-8030 — Treasure-Spend Gate-and-Decrement Deduplication

## Package

- **ID:** IP-8030 — [Treasure-Spend Gate-and-Decrement Deduplication](../packages/IP-8030-treasure-spend-gate-deduplication.md) (refactor)
- **Verified:** 2026-07-20, same session as the implementing edit.

## Independence note

**Degraded independence, explicitly accepted** — same basis as `VR-8010`/`VR-8020`.

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `treasure_spend_gate_and_decrement` exists, called from both `inf_heal_spend`/`inf_tier_spend`; neither site's own inlined gate/decrement block remains | `grep -n "label('ihs_have'\|label('its_have'" asm_game.py` → no matches; `grep -n "CALL('treasure_spend_gate_and_decrement')"` → two call sites | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Rebuilt: 32768 bytes, 32670 used (unchanged from baseline); 404/404 | PASS |
| Byte delta measured and recorded | Net-zero at the section-total level, recorded in the Master Build Plan | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes | Confirmed | PASS |
| G5: full suite, zero `test_rom.py` diff | `git diff --stat test_rom.py` → empty | PASS |
| Equivalence contract: diff touches only the new subroutine + two replaced blocks | Full diff reviewed: exactly `treasure_spend_gate_and_decrement`'s new body plus `inf_heal_spend`/`inf_tier_spend`'s own replaced prefixes | PASS |
| Explicit `OR_A()` precedes the success-path `RET()` | `asm_game.py`, `treasure_spend_gate_and_decrement`'s own final two lines: `LD_A_n(1); LD_nn_A(SCORE_DIRTY)` then `OR_A()` then `RET()` — confirmed present, not dropped | PASS |
| `T31.d`/`T31.d2`/`T31.e`/`T31.f` and `T38.a`-`d` all still pass, "spends even at cap" reconfirmed | `test_results.txt`: `T38.b` (`[PASS] Spot: tier-spend at the cap still spends treasure...`) and `T31.d2` both `[PASS]` | PASS |

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used, unchanged from baseline)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed (identical check-name set to baseline)
```

## Scope audit

`asm_game.py` only. No scope excursion.

## Findings

None.
