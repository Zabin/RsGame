# VR-8020 — Absolute-Delta-From-Player Deduplication

## Package

- **ID:** IP-8020 — [Absolute-Delta-From-Player Deduplication](../packages/IP-8020-abs-delta-from-player-deduplication.md) (refactor)
- **Verified:** 2026-07-20, same session as the implementing edit.

## Independence note

**Degraded independence, explicitly accepted** — same basis as `VR-8010`: the user's own direct
instruction to keep iterating refactoring work without stopping for per-step confirmation.
Mitigated by re-deriving every claim from the tree and by strong equivalence evidence (zero
test-file diff, exact pre/post ROM byte-count match).

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `abs_delta_from_player` exists, called from both `inf_mob_move` and the knockback block; neither site's own inlined `a[xy]_*` block remains | `grep -n "label('imv_a[xy]\|label('ikb_a[xy]" asm_game.py` → no matches; `grep -n "CALL('abs_delta_from_player')"` → two call sites | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Rebuilt this run: 32768 bytes, 32670 used (identical to baseline); 404/404 | PASS |
| Byte delta measured and recorded | Net-zero at the section-total level, recorded in the Master Build Plan | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes | Confirmed this run | PASS |
| G5: full suite passes, zero `test_rom.py` diff | `git diff --stat test_rom.py` → empty | PASS |
| Equivalence contract: diff touches only the new subroutine + two replaced blocks | `git diff asm_game.py` reviewed in full: removed lines are exactly the twelve `imv_a[xy]_*`/`ikb_a[xy]_*` labels and their bodies; added lines are the new subroutine plus two `CALL` sites | PASS |
| `C`/`L` output convention correctly consumed by both callers' own unchanged dominant-axis compare | `inf_mob_move`'s own `LD_A_C(); OR_A(); JR_NZ('imv_pick_axis')`/`CP L` and the knockback block's own `LD_A_C(); CP L; JR_C('ikb_axis_y')` both unchanged, immediately follow the new `CALL` | PASS |
| `E`/`D` still hold the correct point position when each caller's own axis-specific branch re-reads them | `imv_axis_x`/`ikb_axis_x` both still read `E` directly after the call, unmodified — confirms `abs_delta_from_player` doesn't clobber them | PASS |
| `T35`/`T36.b` reconfirmed | `test_results.txt`: all `T35.*` and `T36.*` checks `[PASS]`, including `T36.b` (knockback direction) | PASS |

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used, unchanged from baseline)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed (identical check-name set to baseline)
```

## Scope audit

`asm_game.py` only; no other file touched by the implementing edit. No scope excursion.

## Findings

None.
