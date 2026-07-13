# VR-1021 — Win-Condition Redesign (Dead-End-Anchored Treasure Placement)

> Independent verification of [IP-1021](../packages/IP-1021-win-condition-redesign.md), performed
> by `09-package-verification` in a fresh session (the same-session-independence rule blocked
> verification in the implementing session, 2026-07-13).

## Package

- **ID:** IP-1021
- **Title:** Win-Condition Redesign (Dead-End-Anchored Treasure Placement)
- **Commit implemented:** `1dd4968` ("feat(IP-1021): scale-relative win condition — dead-end-anchored
  treasure placement")
- **Commit verified against:** `282d68c` (`main`, post-PR #18 merge; no further changes to the
  package's files since `1dd4968`)

## Result

**VERIFIED** — 0 failed checks, 0 findings requiring remediation. One Low informational note
(§Findings).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| For every `(seed, scale)` in the test corpus, exactly `WORLD_SCALE` regions hold a `KeyItem`, prioritizing pre-braid leaves, fallback fill reaching the target when leaf count falls short | `T12.n` (233/233 suite run, this session) asserts `present == scale` for all 15 `T12_CORPUS` entries (scale ∈ {2,3,9}); `T12.e` asserts full oracle parity (dead-end-priority + fallback logic) for the same corpus, 0 mismatches. Independently re-driven this session at **non-corpus** scales 6 and 8 via the real MAIN MENU → SEED/SCALE ENTRY → INTRO UI path (not the T12 direct-invoke fixture): `present=6/6` (seed 65535) and `present=8/8` (seed 55432), both oracle-matched. | PASS |
| Placement decision unaffected by which edges the braid pass reopens | Confirmed by code read: the placement pass (`asm_game.py:1591-1726`) runs entirely between `maze_carve_done` (spanning tree complete) and `maze_prune_region` (braid pass start), reading only `GW_MAZE_STATE`'s parent-direction bits as written by the carve pass — no braid-pass output is read. `worldgen.py`'s oracle (`_carve_maze:181-206`) computes `is_leaf`/`treasure` from the pre-braid `parent_dir` array, before its own braid loop at line 212. | PASS |
| `check_complete` triggers victory at `KeyItemCount == WORLD_SCALE` for every tested scale, not before | `T4.8` (corrected) confirms at the suite's default scale=3. Independently re-driven this session at scale=6 and scale=8 (real UI path): `CARROTS_COUNT = scale-1` → GS stays 2 (PLAYING); `CARROTS_COUNT = scale` → GS becomes 5 (VICTORY), in both cases. | PASS |
| `setup_zone_collects`/`check_collisions`/`save_to_sram`/`try_load_save` byte-for-byte unchanged | `git diff 1dd4968~1 1dd4968 -- asm_game.py` hunks confined to lines ~132 (constant comment), ~306-320 (`st_intro` clear removal), ~459-475 (`sse_compose_seed` clear relocation), ~727-740 (`check_complete`), ~1571-1720 (new placement pass). None of the four named routines appear in any hunk. | PASS |
| `worldgen.py` mirrors the placement decision in lockstep with the SM83 routine — zero mismatches across the full corpus | `T12.e`/`T12.b` (oracle parity) both pass, 0 mismatches, corpus of 15 `(seed,scale)` pairs; independent live drive above adds 2 more non-corpus pairs, also 0 mismatches. | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | `python3 build_rom.py BunnyQuest.gbc` this session: "Wrote 32768 bytes → BunnyQuest.gbc"; header validity confirmed by `test_rom.py`'s own T1 header suite (part of the 233/233 full-suite pass below). | PASS |
| G5: full `test_rom.py` suite passes | **233/233 passed, 0 failed** (fresh run this session, `test_results.txt`), matching the package's own reported count exactly. | PASS |
| Direct diff: the four named routines byte-for-byte unchanged | See DoD row above — same evidence. | PASS |
| Direct diff: `check_complete`'s only change is the comparison operand | `asm_game.py:742-749` — the diff replaces `rom.LD_A_n(9)` (implied by the prior hardcoded operand) with `rom.LD_A_nn(WORLD_SCALE); rom.LD_B_A()` before the existing `CP_B()`/`RET_NZ()`/victory-transition sequence; control flow (compare → conditional return → `GS_VICTORY` write → `NEED_REDRAW` set → `RET`) unchanged. | PASS |
| `T12.e` (revised) and new `T12.n` confirmed passing; `T4.8` confirmed corrected and passing | All three appear in the 233/233 run: `T12.e`, `T12.n`, `T4.8` (`GS=5 scale=3`) all `[PASS]`. | PASS |
| `worldgen.py`/SM83 lockstep confirmed via `T12.b`, extended to the new pass | `T12.b` passes (0 oracle mismatches for `REGION_GRAPH`); `T12.e` is the placement-pass-specific extension of the same lockstep property, also 0 mismatches. | PASS |
| Confirmed no new PRNG draws were added without a `worldgen.py` mirror update / braid PRNG sequence unaffected | Code read: the placement pass (`asm_game.py:1591-1726`) contains no `CALL('gw_prng_step')` or PRNG-consuming instruction anywhere in its span — confirmed by direct read, not inference. `worldgen.py`'s `_carve_maze` placement block (lines 181-206) similarly makes no `_step`/`perturb` calls; `draw_ctr`'s state entering the braid loop (line 208 onward) is therefore identical to what it would have been without this pass. `T19.e`'s braid-fraction statistical check (24.35%, within the ~25% target band) is unchanged evidence the braid pass's own PRNG sequence is undisturbed. | PASS |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-9160 | `asm_game.py:1591-1726` (placement pass), `worldgen.py:181-206` (oracle mirror) | `T12.e` (revised), `T12.n` | Filled: `asm_game.py, worldgen.py` / `FS-102` / `IP-1021` / `T12.e (revised), T12.n` — confirmed matches the actual files/tests | PASS |
| FR-9161 | `asm_game.py:742-749` (`check_complete`) | `T4.8` (corrected), `T12.n` | Filled: `asm_game.py` / `FS-102` / `IP-1021` / `T4.8 (corrected), T12.n` — confirmed | PASS |

`FR-9130`/`FR-3300`'s own Notes fields confirmed to state "superseded... implemented 2026-07-13,"
matching the established `FR-1120`→`FR-1170`/`1190` precedent's second step (`01-functional-
requirements.md:1123,651` and RTM rows at lines 41/64).

## Test run

- `python3 build_rom.py BunnyQuest.gbc` → `Wrote 32768 bytes → BunnyQuest.gbc` (exact budget, no
  overflow).
- `python3 test_rom.py` → **233/233 passed, 0 failed** (fresh PyBoy 2.7.0 install this session;
  not present in the container at session start, installed to run the gate — same precedent as
  `VR-9010`).
- Independent live drive (this session, not part of `test_rom.py`): real UI-driven new-game flow
  at `(seed=65535, scale=6)` and `(seed=55432, scale=8)` — both outside `T12_CORPUS`'s scale set
  `{2,3,9}` — confirmed exact `WORLD_SCALE`-count placement, oracle parity, and correct
  victory-threshold triggering (not one below). Script and full output retained in this session's
  scratch directory; behavior summarized above is what's load-bearing, not the script itself.

## Scope audit

Diff (`1dd4968~1..1dd4968`) touches exactly `asm_game.py`, `worldgen.py`, `test_rom.py`,
`test_results.txt`, `BunnyQuest.gbc` (rebuilt binary) — matches the package's declared "Files to
Create/Modify" (§6) exactly, plus the routine build/test artifacts every package regenerates. No
excursion into `setup_zone_collects`/`check_collisions`/`save_to_sram`/`try_load_save`, no
`tiles.py`/`build_rom.py` content-package touch (this package has no `08-content-authoring` peer).
The doc/traceability updates (§9) landed in a separate follow-up commit (`16a6e52`,
"docs(IP-1021): traceability + journal"), also confirmed scoped to exactly the named documents
(FR-9160/9161 Notes, RTM rows, `FS-102` metadata, GDS-07 §7c note, Master Build Plan,
`packages/INDEX.md`).

## Findings

| Finding | Severity | Owner |
|---|---|---|
| None requiring remediation. | — | — |

No new backlog entries filed by this verification — every claim in the package's Implementation
Summary and Definition of Done was independently re-derived from the tree and a fresh test/live
run, not taken on faith, and all held.
