# VR-1070 — Maze-Shaped Region Adjacency

> Owned by `09-package-verification`. Independently verifies
> [IP-1070](../packages/IP-1070-maze-shaped-region-adjacency.md) against the shipped tree.

## Package

- **ID:** IP-1070 — Maze-Shaped Region Adjacency
- **Title:** Extend `generate_world` and `worldgen.py` with a second, independent generation
  pass — a randomized DFS/recursive-backtracker spanning tree over `REGION_GRAPH`, then a
  canonical-edge braid/prune pass, per `ADR-0012`/`ADR-0013`.
- **Implements:** [FS-107](../../features/FS-107-maze-shaped-region-adjacency.md) (`FEAT-9100`)
- **Commit verified:** `f9ecbc7` (`feat(worldgen): IP-1070 -- maze-shaped region adjacency`,
  2026-07-11), on top of the tree at the current session head (`ec53ae0`). No later commit
  touches `asm_game.py`'s maze-pass code or `worldgen.py`'s `_carve_maze`.
- **Independence:** this session did not implement IP-1070 (implemented 2026-07-11 in an earlier
  session; this verification runs 2026-07-12 in a fresh session with no prior involvement in that
  implementation). Independence requirement satisfied without caveat.

## Result

**VERIFIED** — 0 failed checks, 0 open Definition-of-Done items, 1 Low documentation-accuracy
finding (does not block `VERIFIED`).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | All seven FS-107 ACs demonstrably pass via T19 | `test_rom.py` T19.a–g, all `[PASS]` (see Test run below); each maps 1:1 to AC-1…7 per the package's own §8/§11 mapping | PASS |
| 2 | ROM builds at 32768 bytes, valid header | `python3 build_rom.py BunnyQuest.gbc` → "Wrote 32768 bytes → BunnyQuest.gbc"; `test_rom.py`'s own header-validity check (T1) passed as part of the full run | PASS |
| 3 | `worldgen.py`'s `_carve_maze` and the SM83 pass produce byte-identical `REGION_GRAPH` output for the full T19 corpus | T19.c "Determinism/oracle parity… mismatches=[]" | PASS |
| 4 | `T12`'s existing suite continues to pass unmodified against the new sparser graph | Full suite run includes T12; all T12 checks `[PASS]` in the 226/226 total (verified no T12 check appears in any failure) | PASS |
| 5 | No new `patches` dict key; `dsr_p`/`draw_region_arrows`/`check_zone_transition` show zero diff | `git diff f9ecbc7~1 f9ecbc7 -- asm_game.py`: only two hunks, one at the WRAM-constants block (~line 83) and one at the `generate_world` insertion point (~line 1358+); no hunk touches `dsr_p`, `draw_region_arrows`, or `check_zone_transition` | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | `build_rom.py` output: "Wrote 32768 bytes"; T1 header checks pass | PASS |
| G5: full `test_rom.py` suite passes (T1–T19) | **226/226 passed, 0 failed** (fresh run, PyBoy 2.7.0 installed this session) | PASS |
| T19.a–g each present and passing, mapped to FS-107 AC-1…7 | All seven present in `test_rom.py` output, all `[PASS]`: a (AC-1 subgraph), b (AC-2 reachability), c (AC-3 determinism), d (AC-4 grammar), e (AC-5 braid-fraction, measured 24.35%/84 of 345 — within the ~25% statistical band), f (AC-6 static audit), g (AC-7 headroom) | PASS |
| Direct code read: new pass reads no `DIV`/uninitialized WRAM | Read `asm_game.py:1416–1611` in full — no `LDH`/hardware-register read anywhere in the maze pass; `GW_MAZE_STATE` is unconditionally zeroed before first read (`gwm_zero` loop, line 1462–1463); T19.f's own static source scan corroborates | PASS |
| Direct code read: prune-pass logic evaluates each undirected edge exactly once (`down`/`right` only) | `maze_prune_region`/`maze_prune_dir` (line 1520–1577): `GW_MAZE_DIR` iterates only `{1 (down), 3 (right)}` per region, confirmed by the `CP_n(1)` branch at line 1569 that switches `down→right` then advances to the next region — `up`/`left` never independently visited | PASS |
| `worldgen.py`'s `_carve_maze` step order matches `generate_world`'s pass, by direct side-by-side read | Read both in full (`asm_game.py:1456–1578`, `worldgen.py:107–182`): identical starting-direction draw → 4-direction rotation → carve/backtrack structure, identical canonical `down`(1)/`right`(3) prune order, identical perturbation formula (`raw XOR counter`, counter += 97, same seed-zero/root-mark-visited init). One deliberate divergence confirmed **not** a bug: `worldgen.py`'s tree-edge test (line 171) evaluates `(parent_dir[v] == OPPOSITE[d]) or (parent_dir[r] == d)` — two conditions — while the SM83 side implements the identical two-check logic across lines 1532–1544 ("Check 1" / "Check 2"). Both sides agree; T19.c's 0-mismatch parity check is direct empirical confirmation | PASS |
| `asm_game.py`'s `dsr_p`/`draw_region_arrows`/`check_zone_transition` show zero diff from this package | Confirmed via the commit-scoped `git diff` above (DoD item 5) | PASS |
| `BL-0019`/`NFR-4200` rider: WRAM headroom re-affirmed against this package's actual new-WRAM byte count | [NFR-4200](../../requirements/02-non-functional-requirements.md) §"2026-07-11 delta" states "actual measured cost is 85 bytes (`GW_MAZE_STATE`–`GW_MAZE_DRAW_CTR`, `0xC3A0`–`0xC3F4`)"; T19.g independently confirms the same extent against the built ROM | PASS |
| `GDS-07`/`RQ-01`/`RQ-02`/`RQ-04`/`FS-107`/Master-Build-Plan deltas applied exactly as §9 names | [GDS-07 §6](../../architecture/07-data-model.md) lines 247–253 document all five new WRAM entries at the exact addresses; [FR-9140/FR-9150](../../requirements/01-functional-requirements.md) marked implemented; [NFR-4200](../../requirements/02-non-functional-requirements.md) delta present; [RTM rows](../../requirements/04-requirements-traceability-matrix.md) FR-9140/FR-9150 cite `IP-1070`/T19; [FS-107 §19](../../features/FS-107-maze-shaped-region-adjacency.md) Open Questions 1–3 all marked RESOLVED with concrete detail; Master Build Plan row present and accurate | PASS |

## Requirements audit

| Requirement | Implemented where | Tested where | RTM cell | Result |
|---|---|---|---|---|
| FR-9140 (maze-shaped region adjacency) | `asm_game.py` maze pass (line 1416–1611); `worldgen.py:_carve_maze` | T19.a, T19.b, T19.c, T19.d, T19.f, T19.g; T17.a/b (navigation non-regression) | Cites T19.a/b/c/d/f/g + T17.a/b — matches | PASS |
| FR-9150 (braid-fraction parameter) | `GW_BRAID_THRESHOLD = 63` (`asm_game.py:1432`), `_GW_BRAID_THRESHOLD = 63` (`worldgen.py:103`) | T19.e (statistical check, 24.35% measured against ~25% target) | Cites T19.e — matches | PASS |

Both requirements trace to real code and a real, passing check. No stale RTM cells found.

## Test run

- `python3 build_rom.py BunnyQuest.gbc` → **32768 bytes written**, valid header, 22472/32768 code
  bytes used.
- `python3 test_rom.py` → **226/226 passed, 0 failed** (fresh PyBoy 2.7.0 install this session;
  T1–T19 all present, including the 8-package remediation/procgen/maze tranches already shipped
  ahead of this package in file order).
- T19 sub-results: a (subgraph, `bad=[]`), b (reachability, `unreachable=[]`), c (oracle parity,
  `mismatches=[]`), d (grammar, `bad_edges=[]`), e (braid-fraction, `84/345 = 24.35%`), f (static
  audit, clean), g (headroom, `0xC3A0`–`0xC3F4` confirmed inside bank-0).

## Scope audit

`git diff f9ecbc7~1 f9ecbc7 --stat` shows changes confined to: `asm_game.py` (WRAM constants +
`generate_world` pass, +231/-1 lines), `worldgen.py` (`_carve_maze` + `_GW_BRAID_THRESHOLD`,
+83 lines), `test_rom.py` (T19 suite + corpus wiring, +385/-... lines), plus the package's own
named documentation targets (FS-107, Master Build Plan, `packages/INDEX.md`, RQ-01/02/04) and
`test_results.txt`. No excursion outside the declared file set or the code/content peer seam —
this is a code-only package (`08-code-implementation`), and no content files (`tiles.py`,
`tilemaps.py`, `music.py`) were touched.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | The package's own §6 task 4 states the tree-edge test is a **single check** ("`GW_MAZE_STATE[V]` bit 7 is set and its parent-direction equals `opposite(Di)` … this single check correctly identifies every tree edge"). The shipped code (and the `worldgen.py` oracle, which explicitly comments on it: "mirroring the SM83 side's own unconditional Check 1/Check 2") actually implements **two** checks — the stated one plus a second, symmetric check for the case where `R`'s own parent is `V` (`R.parent_dir == Di`). This second check is genuinely necessary: a randomized DFS can carve an edge in either direction (parent-to-child order is not fixed by grid position), so a single-direction check would misclassify roughly half of all real tree edges as prunable, corrupting spanning-tree connectivity. The shipped algorithm is correct; the package's own written description of *why* is incomplete/inaccurate. Not a functional defect — T19.b (reachability) and T19.c (oracle/SM83 parity) empirically confirm the two-check version is what shipped on both sides and that it produces a fully connected, mutually consistent graph. | Low (documentation accuracy only — the as-built GDS-07/FS-107 docs are correct; only the package's own §6 narrative undersells the real algorithm) | `07-implementation-planning` (correct IP-1070 §6's own prose the next time that package is touched, or fold into a future doc-hygiene pass — not urgent, no re-implementation needed) |

## Status transition

`IP-1070`: `COMPLETE` → **`VERIFIED`**. Downstream: `IP-1080` depends on `IP-1070` reaching
`VERIFIED` as a hard prerequisite (per its own package's §12) — that prerequisite is now
satisfied. `IP-1080` remains **not authorized** (no G3 on record) and stays its own separate gate;
this verification does not authorize it.
