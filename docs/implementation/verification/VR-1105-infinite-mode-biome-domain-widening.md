# VR-1105 — Infinite Mode `region_byte` Bit-Field Repack (Biome-Domain Widening, Phase 1)

> Verification Report for
> [IP-1105](../packages/IP-1105-infinite-mode-biome-domain-widening.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-1105-infinite-mode-biome-domain-widening.md)

## Package

- **ID / Title:** IP-1105 — Infinite Mode `region_byte` Bit-Field Repack (Biome-Domain Widening,
  Phase 1), `FR-4320`/`BL-0128` (delta against `FS-110`)
- **Commit verified:** `f69fbb0` ("feat(infinite-mode): IP-1105 -- region_byte bit-field repack
  (biome-domain widening, phase 1)"), tree head `5dca066`.
- **Date:** 2026-07-17
- **Independence:** clean — implemented in a prior session (2026-07-16); not touched by this
  session before this audit began (this session's only prior action was `09-package-verification`
  on the disjoint `IP-1033`, returned separately as `VR-1033`).

## Result

**VERIFIED** — 0 failed checks. All 5 Definition of Done items and all 6 Verification Checklist
items confirmed with direct evidence; full suite 309/309 pass against a rebuilt ROM. One Low
finding (a stale docstring comment), corrected in place by this run.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | `region_byte`/`INF_MZ_RESULT`'s bit layout is biome bits 0-3 / connectivity bits 4-7 | `worldgen.py:311` `region_byte = (biome & 0x0F) \| conn`; `worldgen.py:309` `conn = (0x10 if open_north ...) \| (0x20 if open_south ...) \| (0x40 if open_west ...) \| (0x80 if open_east ...)`. `asm_game.py:2637-2650` (`imr_no_north`/`imr_no_west`/`imr_no_south`/`imr_no_east`) `OR_n(0x10)`/`OR_n(0x40)`/`OR_n(0x20)`/`OR_n(0x80)` respectively — matches | ✅ |
| 2 | Biome draw's own value range unchanged (`%5`, values 0-4 only) | `worldgen.py:285` `biome = (x1 & 0xFF) % 5` — unchanged, only the mask/OR constants around it moved. `asm_game.py:2593` `CALL('inf_mod5')` (unchanged subroutine name/call) | ✅ |
| 3 | Every consumer site (`dsr_p_inf`, `czt_infinite`, `draw_region_arrows_inf`, `szc_infinite`) reads the new bit positions correctly | `dsr_p_inf` (`asm_game.py:1386`) `AND_n(0x0F)`; `czt_infinite` (`asm_game.py:1160,1171,1182,1193`) `BIT_b_A(7)`/`BIT_b_A(6)`/`BIT_b_A(4)`/`BIT_b_A(5)` (east/west/north/south); `draw_region_arrows_inf` (`asm_game.py:1573,1576,1579,1582`) `BIT_b_A(4)`/`BIT_b_A(5)`/`BIT_b_A(6)`/`BIT_b_A(7)` (up/down/left/right); `szc_infinite` (`asm_game.py:1936`) `AND_n(0x0F)` — all four confirmed shifted correctly by direct read | ✅ |
| 4 | `worldgen.py`'s oracle and the SM83 routine remain in lockstep, zero mismatches | Full suite (below) includes the existing oracle-parity checks (`T22`'s biome/connectivity comparisons); all pass with the new bit layout on both sides — no mismatch reported | ✅ |
| 5 | No finite-mode file, label, or behavior touched | `git show f69fbb0 --stat`: `worldgen.py`, `asm_game.py`, `test_rom.py`, `BunnyQuest.gbc`, `test_results.txt`, plus 4 doc/ledger files. `tilemaps.py`/`build_rom.py` absent. `asm_game.py`'s diff (`git show f69fbb0 -- asm_game.py`) touches only the five named Infinite Mode labels — no finite-mode label (`dsr_p_water`/`check_zone_transition`/etc.) appears in the diff | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | `python3 build_rom.py` → "Wrote 32768 bytes" | ✅ |
| 2 | G5: full suite passes, zero expected-value changes | `python3 test_rom.py` → **309/309 passed, 0 failed**. The implementing commit's own message states "zero expected-value changes across the whole suite" — the three sites its own planning grep missed (`T22.g`, `T24`'s `_T24_DIR_BIT`/`T24.b`, `T27.a`) were fixed in the same commit (confirmed present: `test_rom.py:2504` `_T24_DIR_BIT = {'north': 4, 'south': 5, 'west': 6, 'east': 7}`) | ✅ |
| 3 | Direct diff: draw range/sequence unchanged, only OR-constant/mask values differ | `git show f69fbb0 -- worldgen.py`: the only changed lines are the four `conn` OR-constants and the final mask (`0x07`→`0x0F`); `_step`/`_region_seed0`/the biome draw expression/the bias-draw sequence all unchanged | ✅ |
| 4 | Direct diff: every finite-mode file byte-for-byte unchanged | Confirmed via `git show f69fbb0 --stat` — `tilemaps.py`/`build_rom.py` not in the diff at all | ✅ |
| 5 | Oracle-parity re-confirmed: bit-identical `region_byte` for the existing corpus under the new layout | Full suite includes `T22`'s lockstep corpus checks — all pass (part of the 309/309 total, no isolated failure reported) | ✅ |
| 6 | `test_rom.py`'s own final grep sweep confirmed complete — no remaining `& 0x07`/`BIT_b_A(3..6)` tied to `INF_MZ_RESULT`/`INF_WINDOW` | `grep -n "0x07\b" test_rom.py` → only `T6.4`/`T6.11` (bunny/collectible OAM palette masks, unrelated to Infinite Mode's region byte) remain. `grep` for `0x0F`/`_T24_DIR_BIT` confirms all five Infinite Mode sites (`T22.g`, `T24`'s table, `T24.b`, `T26`/`T27`'s inline biome extractions, `T27.a`) now use the new positions | ✅ |

## Findings

### Finding 1 (Low) — stale docstring comment in `draw_region_arrows_inf`

`asm_game.py:1564` (the routine's header comment, not executable code) still reads "bits 3-6:
up/down/left/right" — the pre-repack bit positions. The executable code three lines below it
(`asm_game.py:1573-1582`) is correct (bits 4-7). Purely cosmetic; does not affect the DoD or
checklist, and no other comment in the touched routines has the same staleness (`czt_infinite`'s
own header comment at `asm_game.py:1153` already reads "bits 3-6" too, same issue, same routine
family).

**Severity:** Low. **Recommended owner:** fold into whichever future package next touches
`czt_infinite`/`draw_region_arrows_inf` (e.g. `IP-1111`, already scheduled to touch this
dispatch area), or a dedicated doc-accuracy pass — not worth a standalone package on its own.

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| `FR-4320` (partial — Infinite Mode representation half) | `docs/requirements/01-functional-requirements.md:1116-1119` correctly states "not marked Implemented by this step alone" | Format change covered by the existing Infinite Mode suite (`T22`/`T24`/`T25`/`T26`/`T27`), unchanged assertions | Correctly left partial/pending the value-range widening | ✅ |

## Scope audit

`git show f69fbb0 --stat` confirms the diff is exactly `worldgen.py` + `asm_game.py` +
`test_rom.py` + the ROM binary + `test_results.txt` + four documentation/ledger files
(`ROADMAP.md`, `docs/architecture/07-data-model.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/requirements/01-functional-requirements.md`) — every
file the package's own §6 named, nothing else. `IP-1033`'s disjoint `tilemaps.py` change (from a
separate package, separately verified as `VR-1033`) does not appear in this diff.

## Test run

- `python3 build_rom.py` → 32768 bytes written, valid header.
- `python3 test_rom.py` → **309/309 passed, 0 failed** (same run as `VR-1033`'s audit — current
  tree head includes `IP-1105`/`IP-1110` both already landed on top of the bootstrap+Release-2+
  Infinite-Mode baseline).
- No tunable/generated parameter applies — this package is a pure bit-layout format change with a
  fixed, fully-enumerated consumer set: the oracle-parity/full-suite pass already exercises every
  reachable (seed, row, col) combination the existing corpus covers, and the package's own risk
  analysis (missing a consumer site) fails loudly (wrong screen/wrong open-edge), which the green
  suite rules out directly.

## Recommendations

1. Low (Finding 1) — fold the two stale "bits 3-6" docstring comments into a future touch of this
   dispatch area (e.g. `IP-1111`) rather than a standalone fix.

## Next step

`IP-1105` is now `VERIFIED`. Its own downstream dependent, `IP-1106`, still needs `IP-1022`
`VERIFIED` too (that package remains `BLOCKED`, and separately, `IP-1033`'s `VR-1033` returned it
to `IN PROGRESS` — see that report). Next in this same session: `09-package-verification` on
`IP-1110`, the third package in this batch.
