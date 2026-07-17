# VR-1104 — Infinite Mode: Visited-Region-Ledger Save Persistence

> Owned by `09-package-verification`. Independently verifies
> [IP-1104](../packages/IP-1104-infinite-mode-ledger-save-persistence.md) against the shipped
> tree.

## Package

- **ID:** IP-1104 — Infinite Mode: Visited-Region-Ledger Save Persistence
- **Title:** Extends `save_to_sram`/`try_load_save` with a ledger-based Infinite Mode save shape
  (position, 128-entry FIFO-bounded visited-region ledger, running treasure count, persistent
  top-3 table; `SAVE_VERSION_VAL` `0x04`→`0x05`) — Workflow D of `FS-110` in full. **Amended in
  place 2026-07-16 per `BL-0119`** (before implementation, same prior session) to add a 642-byte
  WRAM working copy of the ledger, so `IP-1102`'s `inf_ensure_window` can cheaply cross-reference
  collected-state on *every* materialization (new-game entry, ordinary in-session navigation, and
  post-load restore), not only at the save/load boundary the original plan covered. This report
  verifies the current, already-amended package text against the shipped code — it does not
  re-litigate the amendment decision itself (`BL-0119` is already `DONE`).
- **Implements:** [FS-110](../../features/FS-110-infinite-mode.md) (`FEAT-10000`, `EP-6000`) —
  Workflow D in full. Last package in the Infinite Mode tranche's critical path.
- **Commit verified:** `3c85a02` (`feat(infinite-mode): IP-1104 -- visited-region-ledger save
  persistence`, 2026-07-16), plus the package-amendment commit `c6b9462` (`docs(implementation):
  IP-1104 -- amended per BL-0119`, 2026-07-16, the same prior session, planning-only) and the
  immediate follow-up journal commit `807f942` (no further code changes).
- **Independence:** this is a fresh session with no memory of writing `IP-1104`'s code or of
  authoring its `BL-0119` amendment — both were done in a prior session (commits `c6b9462`/
  `3c85a02`, per `git log`), now merged into this branch's history. `git status` was confirmed
  clean (`nothing to commit, working tree clean`) before the first read of any package/code file
  in this run, and no local uncommitted state related to `IP-1104` existed at the start.
  Independence requirement satisfied without caveat.

## Result

**VERIFIED** — 0 failed checks, 0 open Definition-of-Done items, 2 informational (Low-severity)
findings, neither blocking.

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | A full save/load round trip restores position, running count, top-3 table, and every ledger entry's collected-state exactly (T27.a) | Direct code read: `save_to_sram` (`asm_game.py:2846-2869`) writes `SRAM_GAME_MODE`/`SRAM_INF_ROW`/`SRAM_INF_COL`/`SRAM_RUNNING_TREASURE_COUNT` and a single 642-byte `memcpy` of the ledger block, gated on `GAME_MODE==1`; `TOP_SCORE_TABLE` always written. `try_load_save` (`:2954-2976`) restores the mirror image, then calls `inf_ensure_window` to re-materialize. `T27.a1-a3` confirm end-to-end. Independently re-driven at a non-fixture seed (9092, see Test run) with the identical result | PASS |
| 2 | No SRAM byte represents a region's biome or connectivity (T27.b) | Direct code read: `SRAM_LEDGER`'s 5-byte entry (`asm_game.py:255-258`) is row(2)/col(2)/collected(1) only — no biome/connectivity field anywhere in the layout, confirmed against `inf_ledger_mark_collected`'s own write pattern (`:2789-2794`, `:2808-2812`, four position bytes + one collected byte, nothing else). `T27.b`'s direct SRAM-byte audit confirms `[0,0,0,0,1]` for the sole persisted entry | PASS |
| 3 | A collected treasure does not respawn on ordinary in-session re-entry (T27.g, BL-0119) | Direct code read: `inf_ensure_window`'s ledger cross-reference (`asm_game.py:1130-1145`) sits inside the existing `if _idx == 4:` block, immediately after `IP-1103`'s `INF_TREASURE_HERE` write, overriding it to 0 on a ledger hit — this is the *only* call site that ever writes `INF_TREASURE_HERE`, reached uniformly from new-game entry, `czt_infinite` navigation, and post-load restore. `T27.g` confirms in-session (one-step move). Independently re-driven with a **genuine two-region window eviction** (region truly leaves the resident window, not just recentered adjacent to it — see Test run) at seed 9092: treasure stays collected, no double-increment | PASS |
| 4 | FIFO eviction behaves correctly at capacity (T27.c) | Direct code read: `ilmc_evict` (`asm_game.py:2797-2816`) computes `LEDGER + LEDGER_CURSOR*5` via five fixed `ADD_HL_DE` steps, overwrites that entry, advances cursor `AND 0x7F`. `T27.c1-c4` confirm invocation at capacity, correct cursor/count, correct overwritten entry, all others unchanged, and survival across a save/load round trip | PASS |
| 5 | A pre-Infinite-Mode save is cleanly rejected, never partially loaded (T27.d) | Direct code read: `check_save_valid`/`try_load_save` both compare against the single `SAVE_VERSION_VAL` (`asm_game.py:2888`, `:2920`), now `0x05` — a `0x04` (or earlier) save fails the compare and takes the pre-upgrade path (`tls_no`/`csv_no`), offering no "continue". `T27.d1/d2` confirm via a synthetic `version=0x04` fixture | PASS |
| 6 | The finite mode's own save/load is provably unaffected (T27.e) | Direct code read: the existing finite-mode restore/save fields (`CUR_ZONE`/`PLAYER_X`/`PLAYER_Y`/`CARROTS_COUNT`/`SCORE`/`CARROT_FLAGS`/`SCOREITEM_FLAGS`/`SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS`) are written/read unconditionally, exactly as before this package — the new Infinite-Mode fields are additive, gated separately. `T27.e` re-checks all 17 `T15.*` assertions unmodified under the new `SAVE_VERSION_VAL` — 0 failures | PASS |
| 7 | No reachable input sequence forcibly ends a loaded Infinite Mode run (T27.f, FR-10600) | No code anywhere writes `GAMESTATE`/`TRANSITION_TO` to a terminal/victory value from any Infinite Mode-reachable branch (confirmed alongside `IP-1103`'s own `T26.e`/`d` audit, unchanged by this package). `T27.f` drives movement, both SAVE round-trip branches, and a SELECT-menu round trip from a loaded save — lands back in `PLAYING`, `GAME_MODE` still 1 | PASS |
| 8 | ROM builds at 32768 bytes; full suite passes | Independently rebuilt to a throwaway path; `sha256sum` matched the committed `BunnyQuest.gbc` byte-for-byte. Full suite: **309/309 passed, 0 failed** (see Test run) | PASS |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Rebuilt independently to `/tmp/.../vr1104_check.gbc`; 32768 bytes; `sha256sum` byte-identical to the committed ROM | PASS |
| 2 | G5: full `test_rom.py` suite passes | 309/309, 0 failed (see Test run) | PASS |
| 3 | T27.a–g each present and passing | All present and passing (`T27.a1/a2/a3`, `T27.b`, `T27.c1/c2/c3/c4`, `T27.d1/d2`, `T27.e`, `T27.f`, `T27.g`). Direct count (`grep -c 'check("T27\.' test_rom.py`) → **13**, not the "7 checks" every ledger claims (`00-master-build-plan.md`, `packages/INDEX.md`, `FS-110-infinite-mode.md`, `01-functional-requirements.md`, the pipeline journal) — see Findings #1. Every named scenario letter a–g is present and correctly covered, several split into sub-checks (`a`→`a1/a2/a3`, `c`→`c1/c2/c3/c4`, `d`→`d1/d2`), the identical "stale summary count, not a coverage gap" pattern `VR-1100` found for `T25` in this same tranche | PASS (finding filed, non-blocking) |
| 4 | Direct code read: `save_to_sram`/`try_load_save` still use exactly one MBC1-enable bracket | `save_to_sram`: single `LD_A_n(0x0A); LD_nn_A(0x0000)` at entry (`:2820`), single `XOR_A(); LD_nn_A(0x0000)` at exit (`:2870`) — the new IP-1104 fields (`:2846-2869`) sit entirely between them, no second bracket. `try_load_save`: single enable at entry (`:2899`), single disable at `tls_si_skip` (`:2978`) — the new restore block (`:2937-2971`, including the `inf_ensure_window` call) sits entirely between them, no second bracket opened | PASS |
| 5 | Direct code read: `SRAM_LEDGER`'s 5-byte entry format matches §6 exactly — no biome/connectivity field | Confirmed (see DoD item 2) — `asm_game.py:255-258` and the write sites in `inf_ledger_mark_collected` agree exactly: row(2)/col(2)/collected(1), nothing else | PASS |
| 6 | Direct code read: `try_load_save`'s `GAME_MODE==1` restore branch calls `inf_ensure_window` before any gameplay frame renders | Confirmed: the `CALL('inf_ensure_window')` (`asm_game.py:2970`) executes before `GAMESTATE`/`TRANSITION_TO` are set to `GS_PLAYING` (`:2979-2980`) and before `NEED_REDRAW` is set (`:2981`) — no render call is skipped on the load path | PASS |
| 7 | Direct code read: `inf_ledger_mark_collected` and `inf_ensure_window`'s ledger cross-reference both operate on WRAM `LEDGER`/`LEDGER_COUNT`/`LEDGER_CURSOR`, never directly on `SRAM_LEDGER*` outside the MBC1-bracketed `memcpy` calls | `grep -n "SRAM_LEDGER" asm_game.py` shows exactly two live-code references, both `SRAM_LEDGER_COUNT` as the `memcpy` source/dest in `save_to_sram`/`try_load_save` (`:2863`, `:2962`) — both inside their routine's single MBC1 bracket. `inf_ledger_find`/`inf_ledger_mark_collected`/`inf_ensure_window`'s cross-reference (`:2740-2816`, `:1130-1145`) reference only `LEDGER`/`LEDGER_COUNT`/`LEDGER_CURSOR` (WRAM) throughout | PASS |
| 8 | Direct code read: `inf_ensure_window`'s ledger cross-reference runs on every call — not gated on any load-specific flag | Confirmed: the cross-reference (`:1141-1145`) is unconditional code inside the `if _idx == 4:` block of the single, non-branching `inf_ensure_window` routine — the same routine every call site (`new-game` entry, `czt_infinite` × 4 directions, post-load restore) invokes uniformly, with no flag/state gate distinguishing them | PASS |
| 9 | FR-10500/FR-10600/NFR-5400/GDS-07/RTM/Master-Build-Plan deltas applied exactly as §9 names | `docs/requirements/01-functional-requirements.md`: FR-10500/FR-10600 → "Implemented, 2026-07-16, IP-1104" with accurate Notes (sizing, `SAVE_VERSION_VAL` bump). `docs/requirements/02-non-functional-requirements.md`: NFR-5400 → "Met, 2026-07-16, IP-1104", "SIZED AND MET" status line, accurate Notes (FIFO policy, WRAM copy). **Note:** the package's own §9 text names `docs/requirements/01-functional-requirements.md` for the NFR-5400 status update — an NFR belongs in `02-non-functional-requirements.md`, where the implementation in fact correctly placed it; a citation slip in the package's own prose, not an implementation scope error (see Findings #2). `docs/architecture/07-data-model.md`: new §7g (WRAM `LEDGER_COUNT`/`LEDGER_CURSOR`/`LEDGER`, `C419`–`C69A`) and §7h (SRAM block, `A0C1`–`A34F`) both present, addresses confirmed byte-for-byte against `asm_game.py`. `docs/requirements/04-requirements-traceability-matrix.md`: FR-10500/FR-10600/NFR-5400 rows all cite `IP-1104`/`T27.a`,`T27.c`,`T27.f` correctly. `docs/features/FS-110-infinite-mode.md`: `IP-1104` header entry present, §19 OQ5/OQ7 marked Resolved accurately. Master Build Plan status row present (`COMPLETE`, pending this run) | PASS |

## Requirements audit

| Requirement | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-10500 (visited-region-ledger save/load) | `asm_game.py`: new WRAM (`LEDGER_COUNT`/`LEDGER_CURSOR`/`LEDGER`, `:217-224`) + SRAM (`SRAM_GAME_MODE`…`SRAM_LEDGER`, `:246-258`) constants, `save_to_sram`/`try_load_save`'s `GAME_MODE`-gated blocks (`:2846-2869`, `:2937-2976`) | `T27.a1-a3` (3 checks) | `FR-10500 \| ... \| IP-1104 \| T27.a, T27.c` — accurate | PASS |
| FR-10600 (indefinitely resumable run) | `asm_game.py`: no run-ending mechanic added or altered by this package; save/continue extended per FR-10500 | `T27.f` (1 check, systematic negative-test sweep) | `FR-10600 \| ... \| IP-1104 \| T27.f` — accurate | PASS |
| NFR-5400 (ledger round-trip integrity, bounded capacity) | `asm_game.py`: `inf_ledger_mark_collected`/`ilmc_evict` (`:2775-2816`), 128-entry FIFO bound (`LEDGER_COUNT`/`LEDGER_CURSOR` `AND 0x7F`) | `T27.a` (round trip), `T27.c1-c4` (FIFO eviction + round trip) | `NFR-5400 \| ... \| IP-1104 \| T27.a, T27.c` — accurate | PASS |

## Test run

```
$ python3 build_rom.py /tmp/.../vr1104_check.gbc
...
Total used:   0x74C8 (29896 bytes of 32768)
Wrote 32768 bytes → /tmp/.../vr1104_check.gbc
$ sha256sum BunnyQuest.gbc /tmp/.../vr1104_check.gbc
a6d1f5697dcbb58ab3b3772e51f49ee51958a7f5028c3df24b022ad8f53b16ee  BunnyQuest.gbc
a6d1f5697dcbb58ab3b3772e51f49ee51958a7f5028c3df24b022ad8f53b16ee  /tmp/.../vr1104_check.gbc

$ python3 test_rom.py
...
====================================================
  RESULTS: 309/309 passed   0 failed
====================================================
```

**Independent live drive at a non-fixture seed** (`9092` — distinct from `T27`'s own fixture
seeds `27` (`T27.a`/`T27.g`), `777` (`T27.c`), `42` (`T27.f`), `T26`'s `10`, `T25`'s `12345`/`0`,
and this tranche's own prior VR probe seeds `39482`/`53` — per this skill's own rule that a green
suite alone is not sufficient evidence for a package whose DoD references a tunable/generated
value, here the player-chosen Infinite Mode seed that determines *both* whether the starting
region holds treasure *and* the maze connectivity a multi-region round trip depends on):

A standalone script (not `test_rom.py`) confirmed via `worldgen.materialize_region` (run fresh,
not reusing suite state) that seed 9092's own `(0,0)` region holds treasure with a two-region-deep
open corridor east, then drove the real UI path — `MAIN MENU → MODE SELECT → INFINITE SEED
ENTRY → INTRO → PLAYING` — at that seed, in two independent scenarios:

```
seed=9092 oracle (0,0): center=0x49 treasure=True east_open=True
(0,1): center=0x72 west_open=True east_open=True
(0,2): center=0x31 west_open=True
[PASS] B1 Reached PLAYING in Infinite Mode at the independently-chosen seed  (GS=2 mode=1)
[PASS] B2 Materialized center matches the oracle byte-for-byte  (live=0x49 oracle=0x49)
[PASS] B3 INF_TREASURE_HERE cache == 1 at first materialization  (cache=1)
[PASS] B4 Collection: RUNNING_TREASURE_COUNT increments to 1, cache clears  (rtc=1 cache=0)
[PASS] B5 Player genuinely moved two regions east (INF_COL: 0 -> 1 -> 2)  (col_after_1=1 col_after_2=2)
[PASS] B6 Back at region (0,0) after genuinely leaving and re-entering the window (no save/load)  (col_back_1=1 col_back_0=0)
[PASS] B7 BL-0119 core claim: collected treasure does NOT respawn -- INF_TREASURE_HERE stays 0  (treasure_here=0)
[PASS] B8 RUNNING_TREASURE_COUNT does not double-increment on standing at the collection point again  (rtc_back=1)
[PASS] B9 Standing directly on the (now-inactive) collection point again does not re-increment  (rtc_stand=1)
[PASS] A1 Pre-save: treasure collected (rtc==1), moved to a second region (col==1)  (rtc=1 col=1)
[PASS] A2 Post-load: INF_COL and RUNNING_TREASURE_COUNT restore exactly, straight to PLAYING  (GS=2 col=1 rtc=1)
[PASS] A3 Back at region (0,0) post-load: col==0, INF_TREASURE_HERE==0 (collected-state survived the save/load boundary)  (col=0 treasure_here=0)

VR-1104 INDEPENDENT LIVE DRIVE at seed=9092: ALL ASSERTIONS PASSED
```

Scenario B is a deliberately *stronger* variant of `T27.g`'s own one-step move: `T27.g` moves the
player exactly one region east, which recenters the window at col=1, spanning col `{0,1,2}` — the
originating region (col 0) technically never leaves the resident window under that move. This
independent drive moves two full regions east (window recenters at col=2, spanning `{1,2,3}`,
genuinely evicting col 0) and back, directly exercising the "leaves the materialized window and
walks back" language `BL-0119`/the package's own §6 and §8 (`T27.g`) use, with no save/load
boundary crossed anywhere in Scenario B. Scenario A independently reproduces the `T27.a` save/load
round-trip shape at the same non-fixture seed. Both scenarios pass with the same behavior the
suite's own fixtures claim, at values none of them cover.

## Scope audit

Commit `3c85a02` touches: `asm_game.py` (the only code file `IP-1104` §6 names), `test_rom.py`
(§8), `BunnyQuest.gbc` (rebuild artifact), `test_results.txt` (suite-run artifact), plus
documentation exactly at the locations §9 names: `docs/requirements/01-functional-requirements.md`,
`docs/requirements/02-non-functional-requirements.md`, `docs/requirements/04-requirements-
traceability-matrix.md`, `docs/architecture/07-data-model.md`, `docs/features/FS-110-infinite-
mode.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
plus `ROADMAP.md` — the same standing convention `VR-1100`/`VR-1102`/`VR-1103` already accepted
for this tranche for locations not literally named by every package's own §9 but consistently
updated by every prior package in this set. No excursion into `gbc_lib.py`, `tilemaps.py`,
`tiles.py`, `music.py`, `worldgen.py`, or `build_rom.py`. The separate amendment commit `c6b9462`
(package text only: `IP-1104`'s own file, `ROADMAP.md`, Master Build Plan, `packages/INDEX.md`) is
`07-implementation-planning`'s own prior-session planning work, not `08`'s code-implementation
scope — correctly outside this package's own implementing diff. Code-only package
(`08-code-implementation`); no tile/palette/screen-layout changes.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | Every ledger describing `T27` (`00-master-build-plan.md`, `packages/INDEX.md`, `01-functional-requirements.md`, `FS-110-infinite-mode.md`, the pipeline journal) states "7 checks" — the package's own §8 names 7 lettered scenarios (a–g), but the shipped suite correctly splits several into multiple `check()` assertions (`a`→`a1/a2/a3`, `c`→`c1/c2/c3/c4`, `d`→`d1/d2`). Direct count (`grep -c 'check("T27\.' test_rom.py`) → **13**, not 7. Every named scenario is present and covered — this is a stale summary count, not a coverage gap, the identical pattern `VR-1100` found and filed for `T25` ("10 checks" vs. actual 19) earlier in this same tranche. | Low (cosmetic — a stale summary number in five documents, no missing test coverage) | `07-implementation-planning`/manager (a one-line correction whenever next touched, consistent with how `VR-1100`'s identical finding was routed) |
| 2 | `IP-1104` §9's own text names `docs/requirements/01-functional-requirements.md` as the location for the "NFR-5400 status → Met" update. `NFR-5400` is a non-functional requirement and correctly lives in, and was correctly updated in, `docs/requirements/02-non-functional-requirements.md` — the implementation did the right thing despite the package's own §9 prose naming the wrong file. Not a scope excursion (the diff touched the correct file) — a citation slip in the package text itself. | Low (documentation-text accuracy only; no incorrect ledger update resulted) | `07-implementation-planning`/manager (a one-line correction to `IP-1104` §9's own wording whenever next touched) |

## Status transition

`IP-1104`: `COMPLETE` → **`VERIFIED`**. This was the last `COMPLETE` package in the tree — all
**31 of 31** implementation packages are now `VERIFIED` (confirmed by direct count against the
Master Build Plan's own package table: 30 rows already read `VERIFIED` before this run, `IP-1104`
was the sole `COMPLETE` row). This closes the Infinite Mode tranche's own five-package
implementation set end-to-end (`BL-0112`, the `FR-10400` run-end trigger, remains the tranche's
sole standing gap — explicitly out of this package's own scope, not resolved here). With every
package in the tree now `VERIFIED`, the Infinite Mode tranche's own `10-integration-review` pass
(across `IP-1100`–`IP-1104` as a set) becomes the natural next pipeline step.
