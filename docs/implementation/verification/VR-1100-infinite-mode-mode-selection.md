# VR-1100 — Infinite Mode: Mode Selection & New-Game Entry

> Owned by `09-package-verification`. Independently verifies
> [IP-1100](../packages/IP-1100-infinite-mode-mode-selection.md) against the shipped tree.

## Package

- **ID:** IP-1100 — Infinite Mode: Mode Selection & New-Game Entry
- **Title:** Add a `MODE SELECT` cursor menu (finite/infinite) between `MAIN MENU`'s "new game"
  option and the existing `SEED/SCALE ENTRY` flow, plus a new seed-only `INFINITE SEED ENTRY`
  state for the Infinite Mode path — implementing `GDS-01` §4d exactly, including its deliberate
  asymmetric-cancel-path tradeoff.
- **Implements:** [FS-110](../../features/FS-110-infinite-mode.md) (`FEAT-10000`, `EP-6000`) —
  Workflow A only.
- **Commit verified:** `b3114da` (`feat(infinite-mode): IP-1100 -- mode selection & new-game
  entry`, 2026-07-14), plus its immediate follow-up journal/backlog commit `a872951` (no further
  code changes) — the branch head at this run's start (`43fb0e0`) is three commits ahead of
  `a872951` (`55f8827`/`c63f9bf`/`43fb0e0`, all `IP-1103` work by this same session — untouched by
  this verification, confirmed by `git status` clean before the first read).
- **Independence:** this session implemented `IP-1103` (a different package, same tranche) earlier
  in this conversation, but did **not** implement `IP-1100` — that shipped in commit `b3114da`
  under session `01WqLw97LZnsUJgaaPTZJLjn`, a prior, distinct session per the journal's run #160
  entry. No memory of writing `IP-1100`'s own code exists in this run. Independence requirement
  satisfied without caveat.

## Result

**VERIFIED** — 0 failed checks, 0 open Definition-of-Done items, 2 Low-severity documentation
findings (neither blocks `VERIFIED`).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Both new states (`GS_MODE_SELECT`, `GS_INFINITE_SEED_ENTRY`) reachable and behave exactly per `GDS-01` §4d's diagram, including the named asymmetric-cancel-path tradeoff | Direct code read confirms `GS_MODE_SELECT, GS_INFINITE_SEED_ENTRY = 10, 11` (`asm_game.py:241`), dispatch entries present (`:390-391`), `st_mode_select`/`st_infinite_seed_entry` implement the toggle/confirm/cancel behavior exactly as `GDS-01` §4d specifies (`:603-699`). Independently live-driven twice — once at `T25`'s own fixture seeds (full suite run below) and once at a seed no fixture uses (`39482`, see Test run) — both reach `PLAYING` via the full `MAIN MENU → MODE SELECT → INFINITE SEED ENTRY → INTRO → PLAYING` path with the oracle-matched starting region | PASS |
| 2 | ROM builds at 32768 bytes; full suite passes | `python3 build_rom.py` → independently rebuilt to a throwaway path, `sha256sum` matched the committed `BunnyQuest.gbc` byte-for-byte. Full suite: **296/296 passed, 0 failed** (up from 280/280 at `IP-1100`'s own implementation time — the +16 are `IP-1103`'s own later, unrelated `T26` suite) | PASS |
| 3 | `SEED/SCALE ENTRY`'s own shipped (`IP-1040`) behavior is provably unchanged (T22.b1's own regression check) | `T25.b1a/b1b/b1c` (the suite's actual name for the package's planned `T22.b1`) confirm: confirming "finite" at `MODE SELECT` reaches `GS_SEED_SCALE_ENTRY` with `GAME_MODE == 0`, and that state's own `B`-cancel still targets `GS_MAIN_MENU` directly — not redirected through `MODE SELECT`. Direct code read of `st_seed_scale_entry`'s `sse_no_b` branch (`asm_game.py:541-548`) confirms the literal instruction: `LD_A_n(GS_MAIN_MENU); LD_nn_A(TRANSITION_TO)`, unconditional, no `MODE SELECT` reference anywhere in the branch | PASS |
| 4 | `FR-10100`'s mode-choice half is demonstrably Implemented via `T22` (shipped as `T25`) | `docs/requirements/01-functional-requirements.md` FR-10100 status reads "Implemented"; `docs/requirements/04-requirements-traceability-matrix.md` row `FR-10100 \| ... \| IP-1100 \| T25` — both confirmed present and accurate against the shipped code and suite | PASS |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Rebuilt independently; 32768 bytes; header logo/title/CGB-flag/checksum bytes match the standard/expected values (same mechanism prior VRs in this tranche used) | PASS |
| 2 | G5: full `test_rom.py` suite passes | 296/296, 0 failed (see Test run) | PASS |
| 3 | T22.a1–f each present and passing (shipped as T25.a1/a1b/a2/b1a/b1b/b1c/b2a/b2b/c1a/c1b/d1/d1b/d2a/d2b/d2c/e1a/e1b/f1/f2) | All 19 individual `check()` assertions grouped under the package's own `a`–`f` scenario letters (`grep -c 'check("T25\.' test_rom.py` → 19) present and passing in the full run; each scenario the package's §8 names (a: MODE SELECT reachable+toggle; b1: finite path+regression; b2: infinite path; c1: B-cancel no-write; d: INFINITE SEED ENTRY confirm→materialization; e1: B-cancel no-write; f: seed=0) is covered | PASS |
| 4 | Direct code read: `st_seed_scale_entry`'s B-cancel target is still `GS_MAIN_MENU` — no accidental redirect through `GS_MODE_SELECT` | Confirmed directly (see DoD item 3 above) — the named tradeoff shipped as specified, not silently "fixed" into symmetry | PASS |
| 5 | Direct code read: `st_mode_select`'s B-cancel writes no `GAME_MODE`/`SEED` value | `ms_check_b`/the B branch (`asm_game.py:611-615`) writes only `TRANSITION_TO`, `NEED_REDRAW`, `MM_JUST_ENTERED` — no `GAME_MODE` or `SEED` instruction anywhere in the branch. `T25.c1b` confirms `GAME_MODE` unchanged at runtime | PASS |
| 6 | Direct code read: `INFINITE SEED ENTRY`'s A-confirm calls `IP-1101`'s materialization routine for `(0,0)` exactly once, not on every frame `GS_INTRO` is drawn | The A-confirm branch (`asm_game.py:686-695`, gated on a fresh `J_A` press via `AND_n(1<<J_A); JP_Z('end_frame')`) calls `inf_ensure_window` — **not** a direct single call to `inf_materialize_region` as the checklist item's own literal wording says, a documented deviation (code comment `asm_game.py:641-647`, and the package's own journal-run narrative): `IP-1102` didn't exist when `IP-1100` was authored, so the package text predates the actual shipped call site. `inf_ensure_window` (`IP-1102`'s routine) itself calls `inf_materialize_region` (`IP-1101`'s routine) once per each of its 9 window cells, including the `(0,0)` center — so the underlying intent (the starting region is correctly materialized, exactly once per new-game entry, not per-frame) is satisfied, and more thoroughly than the checklist item anticipated (the full 3×3 window is populated, not just the center, avoiding an uninitialized-`INF_WINDOW` read). Confirmed called exactly once per A-confirm (guarded by the fresh-press check, and independently confirmed live at seed `39482` below — the routine's output matched the oracle on the first and only materialization, no repeated/drifting values across frames). See Finding 1 below for the package-text gap this leaves | PASS (with Finding 1) |
| 7 | `GDS-01`/`FR-10100`/`RTM`/`Master-Build-Plan` deltas applied exactly as §9 names | `GDS-01` §4d carries a "Confirmed as shipped" note (`01-concept-of-play.md:347-352`); `FR-10100` → Implemented; RTM row filled; Master Build Plan's `IP-1100` row → `COMPLETE` with an accurate narrative — all confirmed present | PASS |

## Requirements audit

| Requirement | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-10100 (mode choice at new-game creation, seed only, no scale step) | `asm_game.py`: `GS_MODE_SELECT`/`GS_INFINITE_SEED_ENTRY` constants, dispatch, `st_mode_select`/`st_infinite_seed_entry`, `mm_newgame`'s retarget; `tilemaps.py`: `mode_select_screen()`/`infinite_seed_entry_screen()`; `build_rom.py`: `ms_t`/`ms_a`/`ise_t`/`ise_a` patch resolution | `T25` (19 checks across a–f) | `FR-10100 \| ... \| IP-1100 \| T25` — accurate | PASS |

## Test run

```
$ python3 build_rom.py /tmp/vr1100_check.gbc
...
Total used:   0x72C8 (29384 bytes of 32768)
Wrote 32768 bytes → /tmp/vr1100_check.gbc
$ sha256sum BunnyQuest.gbc /tmp/vr1100_check.gbc
696f6e37850c955f02d955cfc52f09b4d42b599c598a820fd9dc72ac0e16c7ec  BunnyQuest.gbc
696f6e37850c955f02d955cfc52f09b4d42b599c598a820fd9dc72ac0e16c7ec  /tmp/vr1100_check.gbc

$ python3 test_rom.py
...
====================================================
  RESULTS: 296/296 passed   0 failed
====================================================
```

**Independent live drive at a non-fixture seed** (`39482` — distinct from `T25.d`'s `12345` and
`T25.f`'s `0`, per this skill's own rule that a green suite alone is not sufficient evidence for a
package whose DoD references a player-entered value if every consuming test shares one fixture;
here two fixtures already exist within `T25` itself, but a third, independently-chosen value adds
evidence beyond trusting the package's own test author):

```
after new-game A: GS= 10
after confirm infinite: GS= 11 GAME_MODE= 1
digits [3, 9, 4, 8, 2]
GS=1 seed=39482 (expected 39482) inf_row=0 inf_col=0
center=0x32 expected=0x32 match=True
after A -> PLAYING: GS= 2
```

Full `MAIN MENU → MODE SELECT → INFINITE SEED ENTRY → INTRO → PLAYING` path, seed composed
correctly, `INF_ROW`/`INF_COL` zeroed, starting region's materialized byte matches
`worldgen.materialize_region(39482, 0, 0)` exactly.

## Scope audit

Commit `b3114da` touches exactly: `asm_game.py`, `tilemaps.py` (two new screen-generator
functions, `mode_select_screen()`/`infinite_seed_entry_screen()` — explicitly authorized by the
package's own §6, no new tile art, reuses existing font/cursor/digit primitives), `build_rom.py`
(patch-key resolution for the two new screens), `test_rom.py` (new suite), plus the exact
documentation locations §9 names (`GDS-01`, `FR-10100`, RTM, Master Build Plan, packages/INDEX,
`FS-110` metadata + §19 OQ6, `ROADMAP.md`). No excursion into `gbc_lib.py`, `music.py`,
`worldgen.py`, or any file belonging to `IP-1101`/`1102`/`1103`/`1104`'s own declared scope — no
treasure/win-condition code, no save-format code, no per-region materialization logic (only a
call site into `IP-1102`'s already-built routine). Code-only package (`08-code-implementation`);
the two `tilemaps.py` functions are the narrow, explicitly-named content-adjacent exception the
package's own §6 carves out, not an unscoped crossing of the `08-content-authoring` seam.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | `IP-1100` §5/§6 (Interfaces / Files to Modify) still describe `INFINITE SEED ENTRY`'s A-confirm as calling "`IP-1101`'s per-region materialization routine... for the starting region `(0,0)`" — the package document itself was never amended to state the shipped deviation (a call to `IP-1102`'s `inf_ensure_window`, which populates the full 3×3 window via nine internal calls to `IP-1101`'s routine, instead of one direct call). The deviation is real, correct, and better than the original plan (avoids leaving `INF_WINDOW`'s 8 non-center cells uninitialized) — and it *is* documented, just not in the package file itself: a code comment (`asm_game.py:641-647`) and the pipeline journal's run #160 narrative both state it precisely. Same class of package-text-vs-shipped-code drift as `VR-1101`/`VR-1102`'s own citation findings this tranche (a recurring, low-stakes pattern across the `IP-110x` series worth a single future sweep rather than five separate fixes). | Low (documentation accuracy only; the actual behavior is correct, verified independently above, and already captured in code comments + the journal — no functional risk, no RTM/FR inaccuracy) | `07-implementation-planning` (amend `IP-1100` §5/§6 in place the next time this package is touched; consider bundling with the same citation sweep `VR-1102`'s Finding 1 already recommended for `ADR-0016` point references across the `IP-110x` series) |
| 2 | The package's own DoD/Master-Build-Plan/`packages/INDEX.md`/journal/`FS-110` text all describe the new suite as "`T25`, 10 checks." Direct count (`grep -c 'check("T25\.' test_rom.py`) shows **19** individual `check()` assertions, not 10 — the package's own §8 names 7 lettered scenario groups (a/b1/b2/c1/d/e1/f), several of which the implementation correctly split into multiple sub-assertions (e.g. `d` → `d1`/`d1b`/`d2a`/`d2b`/`d2c`, 5 checks). Every named scenario is present and covered — this is a stale summary count, not a coverage gap (cross-checked against `T22`/`T24`, whose "N checks" claims *do* match their literal `check()` counts exactly, confirming this is an isolated miscount for `T25` specifically, not a project-wide counting convention). | Low (cosmetic — a stale summary number in four documents, no missing test coverage) | `07-implementation-planning`/manager (a one-line correction to `IP-1100`'s own text and the derived MBP/INDEX/journal/FS-110 mentions, whenever next touched — not urgent enough to warrant a dedicated pass on its own) |

## Status transition

`IP-1100`: `COMPLETE` → **`VERIFIED`**. Downstream: `IP-1104` names `IP-1100`/`IP-1101`/`IP-1102`/
`IP-1103` as dependencies — `IP-1101`/`IP-1102` are already `VERIFIED`, `IP-1100` is now
`VERIFIED` by this report, and `IP-1103` is `COMPLETE` (implemented this same session, **not yet**
independently verified — a separate `09-package-verification` run is still owed on `IP-1103`
before `IP-1104` can flip to `READY`; per this skill's own scope, that run stays entirely out of
this report). `IP-1104` remains `NOT STARTED`/blocked-in-substance on `IP-1103`'s own verification
— and, per backlog `BL-0119`, on a pre-execution `07` amendment to its own §6 (mid-session ledger
cross-reference gap).
