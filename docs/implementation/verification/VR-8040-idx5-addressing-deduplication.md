# VR-8040 — Index*5 Addressing Arithmetic Deduplication

## Package

- **ID:** IP-8040 — [Index*5 Addressing Arithmetic Deduplication](../packages/IP-8040-idx5-addressing-deduplication.md) (refactor)
- **Verified:** 2026-07-20, same session as the implementing edit.

## Independence note

**Degraded independence, explicitly accepted** — same basis as `VR-8010`/`VR-8020`/`VR-8030`.

## Result

**VERIFIED** — 0 failed checks, 0 findings beyond the already-filed `BL-0174` (a real, deliberate
test-constraint discovery, not a defect).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `idx5_to_hl` exists, called from `czt_region_hl`/`setup_zone_collects`/`gw_neighbor_hl`/`ilmc_evict`; none of the four retains its own inlined block | `grep -n "CALL('idx5_to_hl')"` → four call sites, plus the subroutine's own label | PASS |
| `dsr_p` confirmed unmodified | `git diff` shows zero lines touching `dsr_p`'s own body (the attempted edit was reverted before commit) | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Rebuilt: 32768 bytes, 32670 used; 404/404 | PASS |
| Byte delta measured and recorded | Net-zero at the section-total level, recorded in the Master Build Plan | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes | Confirmed | PASS |
| G5: full suite, zero `test_rom.py` diff | `git diff --stat test_rom.py` → empty | PASS |
| Equivalence contract: diff touches only the new subroutine + four replaced blocks; `dsr_p` zero diff | Full diff reviewed: exactly `idx5_to_hl`'s new body plus the four call-site rewrites; no `dsr_p` hunk present | PASS |
| `gw_neighbor_hl`'s own `C` (direction) still correct on return | `CALL` instructions don't touch registers other than the return address/`SP`; `idx5_to_hl`'s own body never references `C` — confirmed by direct read | PASS |
| `T9`/`T17`/`T1.11`/`T11`/maze-generation suites/`T27.g`/`T24.c1` all still pass | `test_results.txt`: all corresponding checks `[PASS]`, including `T24.c1` itself (now passing since `dsr_p` was reverted) | PASS |

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used, unchanged from baseline)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed (identical check-name set to baseline)
```

## Scope audit

`asm_game.py` only — five regions (the new subroutine + four call-site rewrites). `dsr_p`
confirmed zero diff lines. No scope excursion.

## Findings

`BL-0174` (Low, `DEFERRED`) — `T24.c1`'s own characterization-test nature discovered during this
package's own execution; already filed, not a defect in this package.
