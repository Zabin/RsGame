# VR-8070 — `gw_neighbor_hl` Read-Wrapper Deduplication

## Package

- **ID:** IP-8070 — [`gw_neighbor_hl` Read-Wrapper Deduplication](../packages/IP-8070-gw-neighbor-read-deduplication.md) (refactor)
- **Verified:** 2026-07-20, same session as the implementing edit.

## Independence note

**Degraded independence, explicitly accepted** — same basis as the prior refactors this session.

## Result

**VERIFIED** — 0 failed checks (after scope correction), 0 findings beyond the scope correction
itself.

## Scope correction (found during execution)

`ki_passA_dir` was originally planned as a third call site. Rewriting it broke `T12.e` (KeyItem
placement oracle-parity test) — `gw_read_neighbor` uses `B` as a scratch register to hold the
region index across the `LD_A_nn(GW_MAZE_DIR); LD_C_A()` step, but `ki_passA_dir`'s own enclosing
loop (`ki_passA_region`) uses `B` as a live `has_child` accumulator across the entire
direction-loop, set before the loop and read after it ends — a conflict invisible from the
block's own immediate context, only from the enclosing loop. Reverted that one site back to its
original inlined form (confirmed zero diff lines against the pre-refactor tree); kept
`maze_try_loop`/`maze_prune_dir`, both confirmed by direct read to have no such conflict.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `gw_read_neighbor` exists, called from `maze_try_loop`/`maze_prune_dir`; `ki_passA_dir` correctly excluded | `grep -n "CALL('gw_read_neighbor')"` → two call sites; `git diff` confirms `ki_passA_dir` zero diff lines | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Rebuilt: 32768 bytes, 32670 used (unchanged from baseline); 404/404 | PASS |
| Byte delta measured and recorded | Net-zero at the section-total level (alignment-slack absorption) | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes | Confirmed | PASS |
| G5: full suite, zero `test_rom.py` diff | `git diff --stat test_rom.py` → empty | PASS |
| Equivalence contract: diff touches only the new subroutine + two replaced blocks | Full diff reviewed: exactly the new subroutine plus two `CALL` substitutions; `ki_passA_dir` zero diff lines | PASS |
| Maze-generation suites still pass | `test_results.txt`: `T12.e` and all maze-generation checks `[PASS]` | PASS |

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used, unchanged from baseline)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed (identical check-name set to baseline, incl. T12.e)
```

## Scope audit

`asm_game.py` only — three regions (the new subroutine + two call-site rewrites). `ki_passA_dir`
confirmed zero diff lines (reverted cleanly). No scope excursion beyond the corrected plan.

## Findings

None beyond the scope correction itself (not a defect — `gw_read_neighbor`'s design is sound for
its two actual call sites; `ki_passA_dir` was correctly excluded, not silently dropped).
