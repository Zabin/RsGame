# VR-8080 — Ledger-Entry Write-Block Deduplication

## Package

- **ID:** IP-8080 — [Ledger-Entry Write-Block Deduplication](../packages/IP-8080-ledger-entry-write-deduplication.md) (refactor)
- **Verified:** 2026-07-20, same session as the implementing edit.

## Independence note

**Degraded independence, explicitly accepted** — same basis as the prior refactors this session.

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `write_ledger_entry_at_hl` exists, called from both sites; neither retains its own inlined block | `grep -n "CALL('write_ledger_entry_at_hl')"` → two call sites; the removed 5-instruction-pair block no longer appears at either original site | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Rebuilt: 32768 bytes, 32670 used (unchanged from baseline); 404/404 | PASS |
| Byte delta measured and recorded | Net-zero at the section-total level (alignment-slack absorption) | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes | Confirmed | PASS |
| G5: full suite, zero `test_rom.py` diff | `git diff --stat test_rom.py` → empty | PASS |
| Equivalence contract: diff touches only the new subroutine + two replaced blocks | Full diff reviewed: exactly two hunks, the two call-site rewrites and the new subroutine | PASS |
| Ledger append and FIFO-eviction tests still pass | `test_results.txt`: corresponding checks `[PASS]` | PASS |

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used, unchanged from baseline)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed (identical check-name set to baseline)
```

## Scope audit

`asm_game.py` only — two regions (`ilmc_notfound`/`ilmc_evict` call-site rewrites) plus the new
subroutine. No scope excursion.

## Findings

None.
