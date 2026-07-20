# VR-8050 — KEYITEM_FLAGS Addressing Deduplication

## Package

- **ID:** IP-8050 — [KEYITEM_FLAGS Addressing Deduplication](../packages/IP-8050-keyitem-flags-addressing-deduplication.md) (refactor)
- **Verified:** 2026-07-20, same session as the implementing edit.

## Independence note

**Degraded independence, explicitly accepted** — same basis as the prior refactors this session.

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `keyitem_flags_hl` exists, called from all six sites; none retains its own inlined block | `grep -n "CALL('keyitem_flags_hl')"` → six call sites; `grep -n "LD_HL_nn(KEYITEM_FLAGS); rom.ADD_HL_DE()"` → only the subroutine's own body remains | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Rebuilt: 32768 bytes, 32670 used (unchanged from baseline); 404/404 | PASS |
| Byte delta measured and recorded | Net-zero at the section-total level, recorded in the Master Build Plan | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes | Confirmed | PASS |
| G5: full suite, zero `test_rom.py` diff | `git diff --stat test_rom.py` → empty | PASS |
| Equivalence contract: diff touches only the new subroutine + six replaced blocks | Full diff reviewed: exactly the new subroutine body plus six `CALL` substitutions, nothing else | PASS |
| Maze-generation suites and `T1.11`/`T11` all still pass | `test_results.txt`: all corresponding checks `[PASS]` | PASS |

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used, unchanged from baseline)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed (identical check-name set to baseline)
```

## Scope audit

`asm_game.py` only — seven regions (the new subroutine + six call-site rewrites). No scope
excursion.

## Findings

None.
