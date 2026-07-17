# VR-1022 — Finite-Mode Nine-Identity Generation & Screen Dispatch

> Verification Report for
> [IP-1022](../packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md)

## Package

- **ID / Title:** IP-1022 — Finite-Mode Nine-Identity Generation & Screen Dispatch
  (`FS-102`/`FS-103` delta, `FR-4310`/`FR-4320`/`BL-0128`, re-planned 2026-07-17 against
  [`ADR-0020`](../../architecture/adr/ADR-0020-procedural-screen-fill-for-rom-budget.md))
- **Commit verified:** `cfa4168` ("feat(worldgen): IP-1022 — nine-identity generation &
  procedural screen dispatch"), tree head `4af0087`.
- **Date:** 2026-07-17
- **Independence:** clean — this run executed in a fresh session with no memory of the
  implementing session (runs #192–#197, per the pipeline journal). PyBoy installed fresh in this
  container; every claim below re-derived from the tree, not the Implementation Summary.

## Result

**VERIFIED** — 0 failed checks. Every Definition of Done item and Verification Checklist item
passes with recorded evidence, the permanent gates are green (ROM exactly 32768 bytes, rebuild
byte-identical to the checked-in `BunnyQuest.gbc`; **311/311** suite), and this run's own
independent live drive at a non-default `(seed, scale)` — real menu entry, real generation, real
button-driven navigation into all four newly-folded identities' regions — confirmed the claimed
behavior directly (see Test run). Two Low documentation-wording findings recorded; neither
affects correctness.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | Finite-mode `generate_world` produces grammar-valid worlds from the full nine-value domain, corpus reaching biome-ids 5-8 | `worldgen.py:69` (`lo, hi = 0, 8`), `worldgen.py:85-86` (clamp to 8); `asm_game.py` `generate_world` clamp `CP_n(8)` (line 2290); `test_rom.py:995-1005` — `T12_CORPUS` 17 entries incl. seeds 38/50 at scale=9, added *because* the base corpus never reached ids 5-8 (vacuity honestly closed); `T12.d` passes 0 illegal edges. Independently confirmed: `worldgen.generate(38,9)` reaches ids 5-7, `generate(50,9)` reaches 5-8 (distribution counted directly this run) | ✅ |
| 2 | All nine identities' screens render correctly when reached — live generation and direct-force both | Direct-force: `T13.a` (9-entry `FAMILY_RANGES`, `test_rom.py:1172-1195`) + `T13.e` pass. Live: this run's own drive at seed=50/scale=9 navigated (real held-button edge crossings) into regions of biome-ids 5, 6, 7, and 8 — correct screen rendered at each, 0 parity mismatches (below) | ✅ |
| 3 | Four new screens' on-device rendering byte-for-byte identical to their Python `*_screen()` functions | `T13.e` (`test_rom.py:1198-1252`): full 544-tile + 544-attr per-cell comparison, all four screens, passes. Re-confirmed live by this run at seed=50/scale=9 in real navigated gameplay: 0 tile + 0 attr mismatches on all four screens (same arrow-position exclusion set) | ✅ |
| 4 | `ZONE_COLLECTS` nine-entry array complete and correctly indexed | `tilemaps.py:556` splices `IP-1033`'s four staged lists at indices 5-8; direct count this run: 9 entries, each with exactly one type-2 (carrot/KeyItem) entry; `T13.f` (dispatch-cascade completeness) proves live spawn output matches each list entry-for-entry for ids 5-8; live drive observed `COLL_COUNT=6` in all four reached regions (matches list lengths) | ✅ |
| 5 | `worldgen.py` oracle in lockstep with SM83 across the widened domain | `T12.b` (17-entry corpus) passes; independently re-confirmed this run at seed=50/scale=9: all 81 live WRAM `REGION_GRAPH` records (biome-id + 4 neighbors) match `worldgen.generate(50, 9)` exactly, 0 mismatches | ✅ |
| 6 | No Infinite Mode file touched | `git diff cfa4168^ cfa4168`: no `inf_*`/`materialize_region` code hunks — Infinite Mode appears only in ledger-doc status rows. `asm_game.py` hunks are the WRAM scratch block, dispatch, the two new subroutines, and the `generate_world` clamp only | ✅ |
| 7 | ROM builds at exactly 32768 bytes | `python3 build_rom.py` → "Wrote 32768 bytes", 32158 used (0x7D9E), byte-identical to checked-in `BunnyQuest.gbc` (`cmp` clean) | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM 32768 bytes, valid header | Build output + byte-identical rebuild (header validity implied by the build's own `set_header()` checks and the suite's boot tests all passing) | ✅ |
| 2 | G5: full suite passes | **311/311, 0 failed** — run by name this session, `test_results.txt` regenerated identically | ✅ |
| 3 | No Infinite Mode file touched | DoD #6 above | ✅ |
| 4 | `T12.d`/`T13.a` extended, passing across nine-value domain | `T12.d` corpus-wide 0 illegal edges; `T13.a` 9-entry `FAMILY_RANGES` audit passes | ✅ |
| 5 | Dispatch-cascade completeness for all four new identities | `T13.f` passes (forces each of ids 5-8, asserts live `COLL_DATA` matches that identity's own list exactly) | ✅ |
| 6 | Oracle/SM83 lockstep, zero mismatches | DoD #5 above — suite + this run's independent 81-region live comparison | ✅ |
| 7 | Nine `ZONE_COLLECTS` entries, exactly one type-2 each | Direct count this run: `[1,1,1,1,1,1,1,1,1]` | ✅ |
| 8 | Oracle-parity present and passing, all four screens, full comparison | `T13.e` + live re-confirmation (DoD #3) | ✅ |
| 9 | No multiplication in the fill routine (`NFR-2200`) | Direct code read `asm_game.py:1523-1598`: only `ADD_A_B`/`SUB_C`/`ADD_HL_*` — incremental column accumulator (`E += mult_x`, repeated-subtraction modulo reduce) + build-time-precomputed per-row seed table (`tilemaps.py` `*_FILL` `row_table`). The landmark applier's `tile_y*32` uses shift-equivalent `ADD_HL_HL`×5 | ✅ |
| 10 | `ALL_SCREENS` confirmed unchanged | `git diff cfa4168^ cfa4168 -- tilemaps.py` contains no `ALL_SCREENS` hunk; live read: still the same 16 entries (5 biome-family + 11 UI). **Note:** the checklist's own "(still exactly 5 biome-family + 5 UI entries)" wording undercounts the UI screens — see Finding 1; the load-bearing claim ("unchanged, no baked entries added") is true | ✅ |
| 11 | ROM byte-budget recovery recorded exactly | Recorded: 32158/32768 used, 610 headroom; ~4,272-byte data-only recovery vs. baking (4×1152=4608 baked minus 96 fill-param + 336 landmark bytes = 4176 data, plus per-screen patch-table deltas ≈ the stated figure), stated in the Master Build Plan row + commit message before code cost | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM state | Verdict |
|---|---|---|---|---|
| `FR-4310` (grammar-valid nine-value adjacency) | `worldgen.py:69,85-86`; `asm_game.py` `generate_world` clamp | `T12.d` (17-entry corpus incl. ids 5-8) | Row filled (Module/FS/IP/Test all present); IP status cell updated `COMPLETE`→`VERIFIED` this run | ✅ |
| `FR-4320` (nine biome-family identities, finite-mode side) | `dsr_p_dispatch` cascade (`asm_game.py:1424-1468`), `fill_procedural_screen`/`apply_landmark_overlay`, `ZONE_COLLECTS` splice | `T13.a`/`T13.e`/`T13.f` | Row filled; Infinite Mode side correctly still `UNASSIGNED` (rides `IP-1106`); IP status cell updated this run | ✅ |
| `FR-4300` (one biome per screen — extended by construction) | Unchanged mechanism, widened domain | Covered by `T13.a`'s per-region single-family audit | Row unchanged (correctly — no new logic) | ✅ |

## Test run

- **Build:** `python3 build_rom.py <scratchpad>/BunnyQuest_verify.gbc` → `Total used: 0x7D9E
  (32158 bytes of 32768)`, `Wrote 32768 bytes`; `cmp` against checked-in `BunnyQuest.gbc`:
  **byte-identical**.
- **Suite:** `python3 test_rom.py` → **`RESULTS: 311/311 passed  0 failed`** (PyBoy 2.7.0,
  fresh install this container).
- **Independent live drive at non-default parameters** (the `BL-0055` rule — the DoD is about
  `(seed, scale)`-generated worlds, and every suite fixture defaults scale=3): scripted PyBoy run,
  real menu flow (`MAIN MENU → MODE SELECT → finite → SEED/SCALE ENTRY`), entered **seed=50,
  scale=9** by button, `INTRO → PLAYING`. Verified live: `SEED=50`, `WORLD_SCALE=9`, all 81
  SM83-generated `REGION_GRAPH` records match `worldgen.generate(50,9)` (0 mismatches). Then
  navigated by real held-button edge crossings (the suite's own T17 method) from start region 0
  into a region of each new identity — Village r3 (5 crossings), Cave r4, Desert r7, Plains r8
  (16 crossings total path) — and at each: correct biome-id live, **0/544 tile + 0/544 attr
  parity mismatches** against that screen's Python oracle, collectibles spawned
  (`COLL_COUNT=6`). Screenshots captured for all four screens. **PASS.**

## Scope audit

Implementing commit `cfa4168` touched: `worldgen.py`, `asm_game.py`, `tilemaps.py`,
`build_rom.py`, `test_rom.py` (all in §6's declared set), the §9-named docs (FS-102/FS-103,
FR/NFR/RTM, Master Build Plan, packages INDEX), and the build outputs (`BunnyQuest.gbc`,
`test_results.txt`). **No excursion beyond the declared set.** The `tilemaps.py` data-half touch
under `08-code-implementation` (the code/content peer seam) was already found, filed, and
dispositioned at implementation time (`BL-0135`, Low, `DEFERRED`) — confirmed accurate, no new
action.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | The package's Verification Checklist wording "(still exactly 5 biome-family + 5 UI entries)" for `ALL_SCREENS` undercounts reality — 16 entries: 5 biome-family + 11 UI (`title`/`intro`/`save`/`map`/`victory`/`main_menu`/`seed_scale_entry`/`select_menu`/`legend`/`mode_select`/`infinite_seed_entry`). Inherited from `tilemaps.py`'s own stale module docstring (line 3, "5 biome-family … + 5 UI", pre-`IP-1040`). The load-bearing claim (unchanged by this package) is true and verified. | Low | The standing `IP-110x` documentation-accuracy sweep (`BL-0115` family) — add `tilemaps.py`'s docstring + this package wording to its list |
| 2 | As-built fill parameterization deviates from the package's §5/§6 letter: §5 says the five constants are "small enough to inline as immediate operands in each screen's own fill routine"; §6 describes a per-row *running accumulator* for the row term. Shipped: a shared routine reading a 24-byte ROM parameter block per screen (`*_FILL` tuples), with the row term precomputed at build time into a 17-byte `row_table` (build-time Python does the multiplies; on-device only column stepping remains). Functionally equivalent, `NFR-2200`-compliant, oracle-proven byte-for-byte, and disclosed in the Master Build Plan row + commit message — but the package doc itself still describes the unshipped variant. | Low | `07-implementation-planning` (a §5/§6 as-built accuracy touch, only if the package doc is ever revised; the deviation is already on record in the Build Plan) |

## Status transitions applied

- `IP-1022`: `COMPLETE` → **`VERIFIED`** (Master Build Plan + `packages/INDEX.md`).
- `IP-1106`: `BLOCKED` → **`READY`** — all three dependencies (`IP-1105`, `IP-1022`, `IP-1033`)
  now `VERIFIED`; authorization already on record (G3, "Build all six").
- `IP-1111`: remains **`BLOCKED`** — its dependencies (`IP-1110`, `IP-1022`) are now both
  `VERIFIED`, but its own §5/§6 still require the `07-implementation-planning` touch `IP-1110`'s
  Outstanding Issue named (consume the shipped `music_table` biome-id-indexed interface, not the
  originally-planned named patch keys) before it is executable. Blocker is now planning-side
  only.
- RTM `FR-4310`/`FR-4320` rows: IP status cells corrected `COMPLETE` → `VERIFIED`.
