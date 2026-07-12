# VR-9070 — CUR_ZONE-Indexed Structure Generalization

> Verification Report for
> [IP-9070](../packages/IP-9070-cur-zone-indexed-structures-generalization.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9070-cur-zone-indexed-structures-generalization.md)

## Package

- **ID / Title:** IP-9070 — `CUR_ZONE`-Indexed Structure Generalization (`BL-0058` + `BL-0059`
  remediation, no FS)
- **Commit verified:** tree head `87b42c1` (2026-07-12). The individual implementing commit for
  this package could not be isolated in `git log` — `git blame` traces every changed line
  (`SCOREITEM_FLAGS = 0xC286`, `ZONE_COLLECTS`'s 5-entry reduction, `setup_zone_collects`'s
  biome-id lookup, suite `T16`) to `988bf6f`, a large pipeline-scaffold commit that bundled many
  unrelated files in one snapshot; no per-package commit boundary survives in this branch's
  history for `IP-9070`/`IP-9050`/`IP-9060`. This is a repository-history artifact, not a scope
  concern — verification proceeded against the current tree state directly, per the as-built
  gotcha in this skill's own instructions.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session. This session's only prior action was
  invoking `09-package-verification` itself; no code was touched before this audit began.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9070. All 5 Definition of Done items and all 6
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
193/193 at the package's own claimed implementation time — later packages, `IP-9050` through
`IP-9140`, added the intervening checks) against a byte-identical rebuilt ROM. One Low finding
(stale RTM cell), corrected in place by this run.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` are 81 bytes each at new, non-colliding addresses; `REGION_GRAPH` unaffected by any `CUR_ZONE` 0–80 | `asm_game.py:71` `SCOREITEM_FLAGS = 0xC286`; `:149` `SRAM_SCOREITEM = 0xA070`; both sized 81 bytes at every read/write/copy site (`:318`, `:383`, `:640`, `:1222`, `:1685`, `:1745` all use `LD_B_n(81)`/`LD_BC_nn(81)`). `T16.a4` directly asserts `REGION_GRAPH` bytes unchanged before/after a forced region-40 collection — `[PASS]` | ✅ |
| 2 | `ZONE_COLLECTS` has exactly 5 entries; `setup_zone_collects` indexes `zc_table` by biome-id, not `CUR_ZONE` | `python3 -c "import tilemaps; print(len(tilemaps.ZONE_COLLECTS))"` → `5`. `setup_zone_collects` (`asm_game.py:1171-1184`) reads `REGION_GRAPH[CUR_ZONE*5]` (biome-id byte), doubles it, and indexes `zc_table` by that — not by `CUR_ZONE` directly. `T16.b` confirms all 5 biome-ids populate `COLL_DATA` from their own list — `[PASS]` | ✅ |
| 3 | `SAVE_VERSION_VAL` is `0x03` [as of this package]; a version-2 (or earlier) save is never offered on "continue" | `asm_game.py:137` now reads `0x04` — a *later* package (`IP-9110`, confirmed by its own inline comment "bumped 0x03->0x04") bumped it again after `IP-9070` landed; this is expected forward drift, not a defect in this package. `IP-9070`'s own contribution (`0x02`→`0x03`) is confirmed via `T16.d1–d3`: a synthetic version-2 fixture boots to MAIN MENU with CONTINUE absent, new game still reaches PLAYING — `[PASS]` all three | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | `python3 build_rom.py BunnyQuest.gbc` → "Wrote 32768 bytes"; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`, both). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |
| 5 | SRAM headroom re-affirmed (net +72 bytes, trivial against ~10 KiB margin) | `SRAM_SCOREITEM` 9→81 bytes at `0xA070`–`0xA0C0`, immediately after `SRAM_KEYITEM_FLAGS`'s end (`0xA01F`+81=`0xA070`, exact) — no other SRAM region touched. GDS-07/NFR-4200 both restate this headroom figure, consistent with the code | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Rebuild wrote 32768 bytes; byte-identical to checked-in ROM (sha256 match) | ✅ |
| 2 | G5: full `test_rom.py` suite passes (193/193 at package time) | **231/231 pass, 0 failed** this run (current suite size — see DoD #4) | ✅ |
| 3 | T16.a–e each present and passing | All 13 `T16.*` checks located in `test_results.txt` (lines 185–197), all `[PASS]` — `a1–a4` (bounds/`BL-0058`), `b` (biome-keyed lookup/`BL-0059`), `c` (save-format v3 round-trip incl. region 80), `d1–d3` (pre-upgrade rejection), `e1–e4` (legacy-field regression) | ✅ |
| 4 | Direct code read: `SCOREITEM_FLAGS`'s new range (`0xC286`–`0xC2D6`) doesn't overlap `REGION_GRAPH`/`KEYITEM_FLAGS`/`GW_*`/`MM_*`/`SSE_*` | Confirmed by direct constant dump: `REGION_GRAPH=0xC070` (5 bytes × up to 81 regions = 405 bytes, ends `0xC203`), `KEYITEM_FLAGS=0xC220` (81 bytes, ends `0xC271`), `SSE_CURSOR=0xC285` (1 byte, immediately before `SCOREITEM_FLAGS`), `SCOREITEM_FLAGS=0xC286` (81 bytes, ends `0xC2D7`), `OAM_BUF=0xC300` (next allocation). No overlap in the sorted sequence | ✅ |
| 5 | Direct code read: `SRAM_SCOREITEM`'s new range (`0xA070`–`0xA0C0`) doesn't overlap `SRAM_SEED`/`SRAM_WORLD_SCALE`/`SRAM_KEYITEM_FLAGS` | `SRAM_SEED=0xA01C` (2B), `SRAM_WORLD_SCALE=0xA01E` (1B), `SRAM_KEYITEM_FLAGS=0xA01F` (81B, ends exactly `0xA070`), `SRAM_SCOREITEM=0xA070` (81B, ends `0xA0C1`) — begins exactly where `SRAM_KEYITEM_FLAGS` ends, no overlap | ✅ |
| 6 | Direct code read: `ZONE_COLLECTS` has exactly 5 entries; `build_rom.py`'s `zc_table` emission needed no code change | `len(ZONE_COLLECTS) == 5` confirmed by direct import. `build_rom.py:120` (`for clist in ZONE_COLLECTS:`) is list-length-agnostic — confirmed by direct read, no hardcoded `9` anywhere in the emission loop | ✅ |
| 7 | GDS-07/GDS-08/NFR-4200/NFR-5300/Master-Build-Plan deltas applied exactly as §9 names | GDS-07 §7a documents the relocation with confirmed addresses; GDS-08 documents the `ZONE_COLLECTS` biome-family reduction cross-referencing `IP-1031`; NFR-4200/NFR-5300 both cite `IP-9070` with the correct figures (+72 bytes, third version bump); `memory.md`'s collectible quick-ref updated (lines 77–83); Master Build Plan row present and accurate (`COMPLETE — 193/193 checks pass`, matches package-time count) | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-5220 (per-zone ScoreItem persistence, generalized storage) | `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` relocation+widening (`asm_game.py`), `setup_zone_collects`'s continued `CUR_ZONE`-indexed bookkeeping | `T16.a1–a4` (bounds), `T16.c` (round-trip), `T16.e1–e4` (legacy-field regression) | **Corrected by this run** — now cites `IP-1010, IP-9070` and `T11.a–e, T16.a–e` (231/231) | ✅ |
| NFR-4200 (generated-world WRAM/SRAM headroom) | SRAM growth re-affirmed (+72 bytes) | Verification Checklist item 7 (headroom re-check) | Correctly cites `IP-9070` | ✅ |
| NFR-5300 (save-format version guard) | `SAVE_VERSION_VAL` `0x02`→`0x03` (this package's own bump; later superseded `0x03`→`0x04` by `IP-9110`, unrelated) | `T16.d1–d3` | Correctly cites `IP-9070` (third bump) alongside `IP-9110` (fourth) | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
grep -c "T16\." test_results.txt     → 13 (matches §8's 5 sub-suites a-e, all present)
```

Non-default-parameter drive: `T16.a1–a4`/`T16.c`/`T16.e3` themselves force `CUR_ZONE`/region
indices up to 40 and 80 (well beyond the old 9-zone ceiling this package's DoD is about) and
`T16.e3` regenerates at `scale=7` (49 regions) — this package's core claim (structures survive
`CUR_ZONE > 8`) is exercised at non-default values by the suite itself, not merely re-run at the
default `scale=3` fixture.

## Scope audit

Every changed symbol traces to exactly the §6-declared files: `asm_game.py` (`SCOREITEM_FLAGS`/
`SRAM_SCOREITEM` relocation, `SAVE_VERSION_VAL` bump, `setup_zone_collects`/`save_to_sram`/
`try_load_save`/`check_save_valid` updates), `tilemaps.py` (`ZONE_COLLECTS` 9→5 reduction),
`test_rom.py` (suite `T16`). `build_rom.py` confirmed untouched and correctly so (list-length-
agnostic already). No excursion beyond the declared set found.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | `docs/requirements/04-requirements-traceability-matrix.md`'s `FR-5220` row cited only `IP-1010`/`T11.a–e` (125/125) — never updated to also name `IP-9070`/`T16` even though this package relocated and widened FR-5220's own storage (`SCOREITEM_FLAGS`/`SRAM_SCOREITEM`). Not a defect in `IP-9070` itself — its own §9 Documentation Updates list never named the RTM as a file this package would touch. **Corrected by this run** (RTM cell now cites both packages/suites, 231/231) — a stale-cell correction within this skill's own "only to correct cells the audit proved wrong" allowance, not a code/package/spec edit. | Low | Closed — corrected in this VR |

No Critical/High findings. IP-9070's core correctness claims (non-overlapping WRAM/SRAM
relocation, biome-keyed `zc_table` lookup replacing the old 9-zone-only indexing, monotonic
version-guard extension, `REGION_GRAPH`/`KEYITEM_FLAGS`/`SEED`/`WORLD_SCALE` all unaffected) are
each independently confirmed against a fresh 231/231 suite run and direct source reads — not
taken on the Implementation Summary's word.
