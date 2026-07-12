# VR-9050 — Generated-World Navigation Fix

> Verification Report for
> [IP-9050](../packages/IP-9050-generated-world-navigation-fix.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9050-generated-world-navigation-fix.md)

## Package

- **ID / Title:** IP-9050 — Generated-World Navigation Fix (`BL-0047` remediation, no FS)
- **Commit verified:** tree head `d899d50` (2026-07-12). As with `IP-9070` (see `VR-9070`), no
  isolated implementing commit survives for this package in `git log` — `git blame` traces
  `check_zone_transition`'s `REGION_GRAPH`-driven rewrite to the same large squashed snapshot
  commit (`988bf6f`). A repository-history artifact, not a scope concern.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session (`git blame`/commit history shows no
  trace of this session's own work in the implementing change).

## Result

**VERIFIED** — 0 failed checks attributable to IP-9050. All 4 Definition of Done items and all 5
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
213/213 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.
`check_zone_transition` has since been legitimately extended twice more by later, separately
authorized packages (`IP-9120`'s RIGHT-threshold correction `156`→`152`; `IP-9130`'s `JOY_CUR`
direction-intent gate on all four branches) — both already reflected in the RTM's `FR-2300` row
and this package's own core claim (`REGION_GRAPH`-driven, zero hardcoded `CUR_ZONE` arithmetic)
still holds exactly as shipped.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | All four `check_zone_transition` edge-branches read `REGION_GRAPH`'s neighbor bytes; zero hardcoded `CUR_ZONE` comparisons/arithmetic remain | `asm_game.py:675-724`: all four branches (`right`/`czt_left`/`czt_top`/`czt_bot`) call the shared `czt_region_hl` subroutine (`:659-665`, `HL = REGION_GRAPH + CUR_ZONE*5`), read the direction's own offset byte (`+4`/`+3`/`+1`/`+2` per `GDS-07` §6), branch on `0xFF`, and on a valid neighbor write it **directly** to `CUR_ZONE` (`LD_nn_A(CUR_ZONE)`) — no `INC_A`/`DEC_A`/`ADD_A_n`/`SUB_n` anywhere in the routine, confirmed by direct read of the full body | ✅ |
| 2 | `T17.a` demonstrably passes at `scale=5`, a player can reach every region via real button-driven navigation | `T17.a0`/`a0b`/`a`/`a1` all `[PASS]` — scale=5 new game reaches PLAYING, oracle region count = 25, every real-navigation transition matches `REGION_GRAPH` (oracle-cross-checked), all 25/25 regions visited via genuine button presses | ✅ |
| 3 | `T17.b` confirms scale=3 behavior is bit-for-bit unchanged | `T17.b1`–`b5` all `[PASS]` — scale=3 traversal matches the oracle at every step, entry positions correct, all 9/9 regions visited, every direction at every region (open or blocked/boundary) matches the oracle | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | `python3 build_rom.py` → "Wrote 32768 bytes"; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes (213/213 at package time) | **231/231 pass, 0 failed** this run (current suite size — later packages, `IP-9060` through `IP-9140`, added the intervening checks) | ✅ |
| 3 | T17.a–d each present and passing | All 13 `T17.*` checks located in `test_results.txt` (lines 198–210), all `[PASS]` | ✅ |
| 4 | Direct code read: `check_zone_transition` contains no `CUR_ZONE` literal-integer comparison or `±1`/`±3` arithmetic; addressing matches `dsr_p`/`draw_region_arrows` exactly via shared `czt_region_hl` | Confirmed — `czt_region_hl` (`:659-665`) is byte-for-byte the same `LD_A_nn(CUR_ZONE); LD_E_A(); LD_D_n(0); LD_HL_nn(REGION_GRAPH); ADD_HL_DE()×5` sequence `dsr_p` (`:876-882`) independently performs; both direction offsets and the `0xFF` sentinel check match `GDS-07` §6's documented byte order. Note: `CP_n(152)`/`18`/`128` (RIGHT/UP/DOWN screen-edge thresholds) and four `CP_n(0xFF)` (neighbor sentinels) are the only `CP_n` literals in the routine — the RIGHT threshold reads `152`, not the package's own originally-cited `156`, because `IP-9120` (a later, separately authorized package) corrected it after `IP-9090`'s clamp fix made `156` unreachable; this is expected, already-documented drift from a downstream package, not a defect in `IP-9050`'s own delivery | ✅ |
| 5 | This session's own independence rule: `IP-9070` confirmed `COMPLETE`/`VERIFIED` before this package's suite run | `IP-9070` is `VERIFIED` (`VR-9070`, this session's own prior run) — the hard prerequisite is satisfied, and `SCOREITEM_FLAGS`/`ZONE_COLLECTS` are safe for the full `CUR_ZONE` range this package's fix makes reachable | ✅ |
| 6 | GDS-04/FR-2300/FR-2310 RTM/Master-Build-Plan deltas applied exactly as §9 names | GDS-04 §"New domain rules" confirms `check_zone_transition` as `REGION_GRAPH`-driven (2026-07-11 delta, cites `IP-9050`/`BL-0047`); RTM's `FR-2300` row cites `IP-9050, IP-9120, IP-9130` and `T17.a–b`/`T7.11`/`T7.12` (already correctly extended by those later packages' own verification-adjacent doc passes); `FR-2310` row cites `T7.9/T7.10, T17.c` | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-2300 (zone-boundary transition on valid neighbor) | `check_zone_transition`'s four `REGION_GRAPH`-driven branches (`asm_game.py`) | `T17.a`/`T17.b` (this package) + `T7.11`/`T7.12` (later packages, already correctly cited) | Cites `IP-9050, IP-9120, IP-9130` — current and accurate | ✅ |
| FR-2310 (no transition at grid boundary) | Same routine's `0xFF`-sentinel clamp branches | `T7.9`/`T7.10`, `T17.c` | Cites the correct tests; `UNASSIGNED` package column is a pre-existing gap (this fix wasn't itself packaged under an ID this row names) — not introduced by this run | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
grep -c "T17\." test_results.txt     → 13 (a0, a0b, a, d, a1, c0, c1, c2, b1, b2, b3, b4, b5)
```

Non-default-parameter drive: `T17.a`/`a0`/`a0b`/`a1` themselves boot a genuine `scale=5` world (25
regions, not the default `scale=3`) and drive real button-press navigation across all 25 regions,
oracle-cross-checked at every step — this package's core claim (navigation works for any
generated world, not just the fixed pre-procgen 3×3 grid) is exercised at a non-default value by
the suite itself.

## Scope audit

Every changed symbol traces to exactly the §6-declared file: `asm_game.py`
(`check_zone_transition` full rewrite + new shared `czt_region_hl` subroutine), `test_rom.py`
(suite `T17`, `T9` fully retired — confirmed by grep, zero live `T9.*` references remain, only
historical comments). No excursion beyond the declared set found.

## Findings

No new findings. The RIGHT-threshold value drift noted under Verification Checklist item 4 is
already fully explained, documented, and attributed to `IP-9120`'s own later, separately
authorized change — not a gap this run needed to correct.

No Critical/High findings. `IP-9050`'s core correctness claim (navigation fully generalized to
`REGION_GRAPH`, addressing identical to the already-`VERIFIED` rendering path, scale=3 behavior
preserved bit-for-bit, a real generated world fully reachable via genuine button-driven play) is
independently confirmed against a fresh 231/231 suite run and direct source reads — not taken on
the Implementation Summary's word.
