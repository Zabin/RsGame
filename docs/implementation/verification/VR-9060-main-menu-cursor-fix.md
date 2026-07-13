# VR-9060 — Main Menu Cursor Fix

> Verification Report for
> [IP-9060](../packages/IP-9060-main-menu-cursor-fix.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9060-main-menu-cursor-fix.md)

## Package

- **ID / Title:** IP-9060 — Main Menu Cursor Fix (`BL-0048` remediation, no FS)
- **Commit verified:** tree head `b3ca697` (2026-07-12). As with `IP-9070`/`IP-9050`, no isolated
  implementing commit survives for this package in `git log` — `git blame` traces every changed
  line to the same large squashed snapshot commit (`988bf6f`). A repository-history artifact, not
  a scope concern.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9060. All 4 Definition of Done items and all 5
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
205/205 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.
One Low finding (stale RTM cell), corrected in place by this run.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | `check_save_valid` no longer writes `MM_CURSOR` under any circumstance | `asm_game.py:1709-1720`: the routine's full body writes only `MM_SAVE_VALID` (`:1714`/`:1717`) and brackets the MBC1 RAM-enable pair — no `MM_CURSOR` reference anywhere in the routine, confirmed by direct read of every line | ✅ |
| 2 | `MM_CURSOR` resets to its default only on genuine MAIN MENU state entry, never on a same-state redraw the player's toggle causes | `mm_on_entry` (`:1030-1046`) gates the reset block (`:1034-1039`) on `MM_JUST_ENTERED` being nonzero (`:1032`, `JR_Z('mm_oe_no_reset')` skips the whole reset if the flag is clear) and clears the flag immediately after consuming it (`:1033`) — a same-state redraw (the flag left clear by `mm_toggle`) falls straight to `mm_oe_no_reset` and never touches `MM_CURSOR` | ✅ |
| 3 | T18.a–d demonstrably pass; "new game" reachable from MAIN MENU whenever a save exists | All 12 `T18.*` checks located in `test_results.txt` (lines 211–222), all `[PASS]` — `a1–a4` (toggle with a valid save, exact values at every step), `d` (A-press from `MM_CURSOR=1` reaches `GS_SEED_SCALE_ENTRY`), `b1–b3` (no-save no-op), `c1–c4` (genuine re-entry via SEED/SCALE ENTRY's B-cancel still resets correctly) | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes (205/205 at package time) | **231/231 pass, 0 failed** this run (current suite size) | ✅ |
| 3 | T18.a–d each present and passing | Confirmed above, all 12 `[PASS]` | ✅ |
| 4 | Direct code read: `check_save_valid`'s body contains no `MM_CURSOR` write | Confirmed under DoD #1 | ✅ |
| 5 | Direct code read: `mm_on_entry`'s `MM_CURSOR`-reset gated on `MM_JUST_ENTERED`, not unconditional | Confirmed under DoD #2 | ✅ |
| 6 | Direct code read: every `GAMESTATE → GS_MAIN_MENU` transition site sets `MM_JUST_ENTERED` — 4 sites, not the 3 the package's own §6 originally named | `grep -n "LD_nn_A(MM_JUST_ENTERED)"` finds exactly 5 occurrences: 4 write sites at boot (`:263`), `st_victory`'s A-press (`:357`), `st_save`'s SELECT option (`:374`), and `st_seed_scale_entry`'s B-cancel (`:433`, the package's own found-during-implementation 4th site), plus `mm_on_entry`'s own consuming clear (`:1033`) — no site silently bypasses it | ✅ |
| 7 | GDS-01/Master-Build-Plan deltas applied exactly as §9 names | Master Build Plan row present and accurate (`COMPLETE — 205/205 checks pass`, confirming GDS-01's target-state diagram needed no change, as the package itself predicted) | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-1170 (MAIN MENU state, regression fix) | `check_save_valid`/`mm_on_entry` fix (`asm_game.py`) | `T18.a1–a4`, `T18.d`, `T18.b1–b3`, `T18.c1–c4` | **Corrected by this run** — now cites `IP-1040, IP-9060` and `T14.a1–a4, T18.a–d` (231/231) | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
grep -c "T18\." test_results.txt     → 12 (a1–a4, d, b1–b3, c1–c4)
```

No tunable/generated parameter is named in this package's DoD (a pure WRAM-flag control-flow
fix, independent of `seed`/`scale`) — the non-default-parameter drive rule does not apply.

## Scope audit

Every changed symbol traces to exactly the §6-declared file: `asm_game.py` (`MM_JUST_ENTERED` new
WRAM flag, `check_save_valid`'s reset tail removed, `mm_on_entry`'s gated reset, the 4th
transition-site fix at `st_seed_scale_entry`'s B-cancel), `test_rom.py` (suite `T18`). No
excursion beyond the declared set found.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | `docs/requirements/04-requirements-traceability-matrix.md`'s `FR-1170` row cited `IP-1040`/`T14.a1–a4` (180/180) only — never extended to also cite `IP-9060`/`T18`, the package that actually fixed the regression this row's own requirement covers. Not a defect in `IP-9060` itself — its own §9 Documentation Updates list only named GDS-01 (confirmed no change needed) and the Master Build Plan row, never the RTM. **Corrected by this run** (RTM cell now cites both packages/suites, 231/231). | Low | Closed — corrected in this VR |

No Critical/High findings. `IP-9060`'s core correctness claims (`MM_CURSOR` reset fully relocated
out of `check_save_valid`, correctly gated on genuine state entry via `MM_JUST_ENTERED`, all four
real transition sites covered including the package's own found-during-implementation 4th site)
are each independently confirmed against a fresh 231/231 suite run and direct source reads — not
taken on the Implementation Summary's word.
