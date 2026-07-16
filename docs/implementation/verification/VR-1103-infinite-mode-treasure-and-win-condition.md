# VR-1103 — Infinite Mode: Treasure Placement & Win-Condition State

> Owned by `09-package-verification`. Independently verifies
> [IP-1103](../packages/IP-1103-infinite-mode-treasure-and-win-condition.md) against the shipped
> tree.

## Package

- **ID:** IP-1103 — Infinite Mode: Treasure Placement & Win-Condition State
- **Title:** Treasure-presence detection (reusing `IP-1101`'s predicate via `IP-1102`'s
  `INF_TREASURE_HERE` cache), collection (reusing `check_collisions`'s existing interface), and
  the running-count/top-3-table data plus its comparison subroutine — Workflow C steps 1–2 of
  `FS-110` in full; step 3 (the automatic run-end trigger's own call site) deliberately not
  implemented (`FS-110` Open Question 3 / `BL-0112`).
- **Implements:** [FS-110](../../features/FS-110-infinite-mode.md) (`FEAT-10000`, `EP-6000`) —
  Workflow C steps 1–2.
- **Commit verified:** `c63f9bf` (`feat(infinite-mode): IP-1103 -- treasure collection &
  win-condition state`, 2026-07-16), plus its immediate follow-up journal/backlog commit `43fb0e0`
  (no further code changes).
- **Independence:** this is a fresh session with no memory of writing `IP-1103`'s code — the
  package was implemented in a prior session (commit `c63f9bf`, per `git log`), now merged into
  this branch's history. `git status` was confirmed clean before the first read (`nothing to
  commit, working tree clean`), and no local uncommitted state related to `IP-1103` existed at
  the start of this run. Independence requirement satisfied without caveat.

## Result

**VERIFIED** — 0 failed checks, 0 open Definition-of-Done items, 1 informational note (does not
block `VERIFIED`).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Treasure collection increments the running count exactly once per region's treasure (T25.a/b, shipped as T26.a/b) | Direct code read: `check_collisions`'s new `cc_inf_hit` branch (`asm_game.py:944-966`) increments `RUNNING_TREASURE_COUNT` 16-bit (`INC` low byte, `INC` high byte only on carry) and clears `INF_TREASURE_HERE` on collection, gated on the cache being non-zero (`JR_Z 'cc_iter'` otherwise). `T26.a5/a6` confirm the count goes 0→1 on collection at a live materialized region (seed=10, the suite's own oracle-searched fixture); `T26.b1/b2` confirm no re-increment while lingering on the (now-inactive) point, nor after a SELECT-menu redraw round-trip. Independently re-driven at a non-fixture seed (53, see Test run) with the identical result | PASS |
| 2 | `inf_check_top_score` correctly inserts/rejects against a synthetic corpus, no name-entry state reachable (T25.c/e, shipped as T26.c/e) | Direct code read of `inf_check_top_score` (`asm_game.py:2620-2661`): 16-bit unsigned compare (high byte first, low byte on tie), strictly-exceeds qualification against the lowest entry (index 2), sorted-descending insertion shifting lower entries down. `T26.c1` runs an 11-case corpus (including exact ties, top-of-range 0xFFFF, and high-byte-decided/low-byte-decided cases) against an independent model function — 0 mismatches; `T26.c2` hand-checks two spot cases outside the model. `T26.e` confirms none of the three new/extended code segments (`szc_infinite`, `cc_inf_hit`, `inf_check_top_score`+`inf_ledger_mark_collected`) write `TRANSITION_TO` or `GAMESTATE`, and no `GS_*NAME*` state exists anywhere in the source | PASS |
| 3 | No automatic call site exists for the comparison subroutine (T25.d, shipped as T26.d) — stated as a pass condition, not a gap | Confirmed independently, not just via the suite: `grep -n "inf_check_top_score" asm_game.py` shows exactly one `rom.label('inf_check_top_score')` and zero `CALL`/`JP`/`JR`-family references anywhere in `asm_game.py` outside comments; `T26.d` corroborates with a ROM-level scan (no `CALL`/`JP`/`JR` opcode anywhere in the assembled code region carries the routine's resolved address). This is the package's own stated Definition of Done — genuinely absent, by design, not an oversight (`BL-0112` still open) | PASS |
| 4 | ROM builds at 32768 bytes; full suite passes | Independently rebuilt to a throwaway path; `sha256sum` matched the committed `BunnyQuest.gbc` byte-for-byte. Full suite: **296/296 passed, 0 failed** (see Test run) | PASS |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Rebuilt independently to `/tmp/.../vr1103_check.gbc`; 32768 bytes; `sha256sum` byte-identical to the committed ROM (which itself passes `T1`'s header/metadata checks every full-suite run, including this run's) | PASS |
| 2 | G5: full `test_rom.py` suite passes | 296/296, 0 failed (see Test run) | PASS |
| 3 | T25.a–e each present and passing (shipped as T26.a0/a1/a2/a3/a4/a4b/a5/a6/a7/a8/b1/b2/c1/c2/d/e) | `grep -c 'check("T26\.' test_rom.py` → **16** — matches every ledger's own claimed count exactly (`00-master-build-plan.md`, `packages/INDEX.md`, `01-functional-requirements.md`, `04-requirements-traceability-matrix.md`, `FS-110-infinite-mode.md` all say "16 checks"). Unlike `T25`'s own stale "10 checks" claim this same tranche's `VR-1100` caught (actual 19), `IP-1103`'s own ledger text for `T26` is accurate — an explicit count-accuracy audit, not assumed. All 16 individual `check()` calls confirmed present and passing in the full run; every scenario the package's §8 names (a: spawn+collect; b: no double-collect; c: corpus+spot; d: zero-call-site; e: no name-entry) is covered, several correctly split into multiple sub-assertions (e.g. `a` → `a0`/`a1`/`a2`/`a3`/`a4`/`a4b`/`a5`/`a6`/`a7`/`a8`, 10 checks) | PASS |
| 4 | Direct code read: `inf_check_top_score` is reachable only via direct test-harness calls, not from `PLAYING`'s own dispatch, `st_save`, `st_victory`, or any other existing state handler | Confirmed (see DoD item 3) — zero `CALL`/`JP`/`JR` references anywhere in `asm_game.py` outside the label definition itself; `test_rom.py`'s own `invoke_icts` reaches it only via an explicit PC/SP hijack (`pb.register_file.PC = ICTS_ADDR`), the same direct-invocation technique `T12`'s `generate_world` corpus tests use, not a real dispatch path | PASS |
| 5 | Direct code read: `check_collisions`'s new `GAME_MODE == 1` branch does not alter the existing `KeyItem`/`ScoreItem` branches' own code path | Confirmed: the shared HIT code (`asm_game.py:882-892`) deactivates the item, then branches on `GAME_MODE` (`JP_NZ 'cc_inf_hit'`) — when `GAME_MODE == 0`, execution falls through unmodified into the existing `KeyItem`(`cc_not_c`)/`ScoreItem` branches (`:894-930`), byte-for-byte as shipped before this package; the new `cc_inf_hit` body lives entirely past `cc_iter`/`cc_skip` (`:944-966`), never touched when `GAME_MODE == 0`. `T26.a7` confirms live: `SCORE`/`CARROTS_COUNT`/`KEYITEM_FLAGS[0]` all unchanged after an Infinite Mode collection, and `T26.a8` confirms no spurious finite `GAMESTATE` transition | PASS |
| 6 | `FR-10300`/`FR-10400`/`RTM`/`Master-Build-Plan` deltas applied exactly as §9 names, with `FR-10400`'s own partial-implementation status stated precisely, not rounded up to Implemented | `docs/requirements/01-functional-requirements.md`: FR-10300 → "Implemented" (collection half, `IP-1103`, 2026-07-16); FR-10400 → "Partially Implemented" with a Notes entry precisely describing the state+subroutine-exist/no-trigger split, mirroring `IP-1080`'s cited precedent. `docs/requirements/04-requirements-traceability-matrix.md`: FR-10300 row → `IP-1101 (presence half) + IP-1103 (collection half)` / `T22.d, T26.a/T26.b`; FR-10400 row → `IP-1103 (partial ...)` / `T26.c (subroutine corpus), T26.d (zero-call-site state, explicit), T26.e (no name entry)` — both confirmed accurate against the shipped code and suite. Master Build Plan's `IP-1103` row was `COMPLETE` with an accurate narrative pending this run | PASS |

## Requirements audit

| Requirement | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-10300 (treasure collection, collection-event half) | `asm_game.py`: `check_collisions`'s new `cc_inf_hit` branch (`:944-966`), `setup_zone_collects`'s new `szc_infinite` spawn branch (`:1866-1888`), `inf_ensure_window`'s `INF_TREASURE_HERE` cache write (`:1078-1088`) | `T26.a0/a2-a8, T26.b1/b2` (12 checks) | `FR-10300 \| ... \| IP-1101 (presence half) + IP-1103 (collection half) \| T22.d, T26.a/T26.b` — accurate | PASS |
| FR-10400 (win-condition state + comparison subroutine, automatic trigger explicitly out of scope) | `asm_game.py`: `RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE` WRAM (`:174-182`), boot clear (`:301-306`), `inf_check_top_score` (`:2620-2661`) | `T26.a1` (boot clear), `T26.c1/c2` (subroutine corpus), `T26.d` (zero-call-site state, explicit), `T26.e` (no name entry) — 5 checks | `FR-10400 \| ... \| IP-1103 (partial — state + subroutine only; no automatic trigger, BL-0112) \| T26.c, T26.d, T26.e` — accurate, correctly does not claim end-to-end AC-4 coverage | PASS |

## Test run

```
$ python3 build_rom.py /tmp/.../vr1103_check.gbc
...
Total used:   0x72C8 (29384 bytes of 32768)
Wrote 32768 bytes → /tmp/.../vr1103_check.gbc
$ sha256sum BunnyQuest.gbc /tmp/.../vr1103_check.gbc
696f6e37850c955f02d955cfc52f09b4d42b599c598a820fd9dc72ac0e16c7ec  BunnyQuest.gbc
696f6e37850c955f02d955cfc52f09b4d42b599c598a820fd9dc72ac0e16c7ec  /tmp/.../vr1103_check.gbc

$ python3 test_rom.py
...
====================================================
  RESULTS: 296/296 passed   0 failed
====================================================
```

**Independent live drive at a non-fixture seed** (`53` — distinct from `T25`'s `12345`/`0`,
`T26`'s own oracle-searched `10`, and every other suite's own fixtures; per this skill's own rule
that a green suite alone is not sufficient evidence for a package whose DoD references
tunable/generated values — here specifically the *player-chosen seed that determines whether the
starting region holds treasure*, which every existing `T26` check shares from one oracle-chosen
fixture):

A standalone script (not `test_rom.py`) independently confirmed, via `worldgen.materialize_region`
run fresh (not reusing suite state), that seed 53's own `(0,0)` region holds treasure, then drove
the real UI path — `MAIN MENU → MODE SELECT → INFINITE SEED ENTRY → INTRO → PLAYING` — at that
seed:

```
seed=53 worldgen.materialize_region -> center=0x4a treasure=True
after new-game A: GS=10
after confirm infinite: GS=11 GAME_MODE=1
digits=[0, 0, 0, 5, 3]
after seed confirm: GS=1
SEED written = 53 (expected 53)
after A -> PLAYING: GS=2 GAME_MODE=1
INF_WINDOW center=0x4a expected=0x4a
INF_TREASURE_HERE=1 (expected 1)
COLL_COUNT=1 COLL_DATA[0]=(84, 56, 2, 1)
pre-collection: RUNNING_TREASURE_COUNT=0 SCORE=0 CARROTS_COUNT=0
post-collection: RUNNING_TREASURE_COUNT=1 INF_TREASURE_HERE=0 active=0
finite-mode counters untouched? SCORE=0 CARROTS_COUNT=0 KEYITEM_FLAGS[0]=0
final GAMESTATE (no spurious victory)=2
RUNNING_TREASURE_COUNT after lingering on the collection point=1

VR-1103 INDEPENDENT LIVE DRIVE at seed=53: ALL ASSERTIONS PASSED
```

Materialized center byte oracle-matched, treasure cache set, exactly one active type-2 `COLL_DATA`
entry at the biome's own `inf_treasure_pos` position, collection increments
`RUNNING_TREASURE_COUNT` to exactly 1, clears the cache, deactivates the item, touches no
finite-mode counter, and produces no spurious victory or double-collection — the identical
behavior `T26.a/b` claim at their own single fixture (seed 10), independently reproduced at a
seed no suite in the tree uses.

## Scope audit

Commit `c63f9bf` touches: `asm_game.py` (the only file `IP-1103` §6 names), `test_rom.py` (§8),
`BunnyQuest.gbc` (rebuild artifact), `test_results.txt` (suite-run artifact), plus documentation:
`docs/requirements/01-functional-requirements.md`, `docs/requirements/04-requirements-
traceability-matrix.md`, `docs/features/FS-110-infinite-mode.md`, `docs/implementation/00-master-
build-plan.md`, `docs/implementation/packages/INDEX.md`, `ROADMAP.md` — all exactly the locations
§9 names (or the same standing convention `VR-1100`/`VR-1101`/`VR-1102` already accepted for this
tranche: `docs/architecture/07-data-model.md` §7f + `docs/architecture/INDEX.md`, confirming the
`GDS-07` WRAM-reservation delta `IP-1101`/`IP-1102` both already established this same pattern
for). No excursion into `gbc_lib.py`, `tilemaps.py`, `tiles.py`, `music.py`, `worldgen.py`,
`build_rom.py`, or any file belonging to `IP-1100`/`1101`/`1102`/`1104`'s own declared scope — the
`inf_ledger_mark_collected` forward-call target is a `RET` stub `IP-1103` itself defines (its own
§6 names this exactly), not an excursion into `IP-1104`'s scope. Code-only package
(`08-code-implementation`); no tile/palette/screen-layout changes, consistent with `IP-1103` §6
naming no content-adjacent exception (unlike `IP-1100`'s narrow `tilemaps.py` carve-out).

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | `docs/features/FS-110-infinite-mode.md`'s own header block still lists `IP-1100` as `COMPLETE 2026-07-14` (not `VERIFIED`) — stale since `VR-1100` (2026-07-16) flipped it, and `VR-1100`'s own commit did not touch `FS-110` (confirmed via `git show --stat` on `d6fb743`). Same class of low-stakes package-text/ledger drift this tranche has repeatedly found (`VR-1100` Finding 1/2, `VR-1101`/`VR-1102` citation findings) — informational only, not introduced by this run, and this run's own scope (per this skill's own rules) does not include editing `FS-110`. | Low (documentation currency only; the authoritative status lives on the Master Build Plan and `packages/INDEX.md`, both accurate) | `07-implementation-planning`/manager (a one-line `FS-110` header refresh whenever next touched, or bundled with the citation-sweep `VR-1100`/`VR-1102` already recommended) |

## Status transition

`IP-1103`: `COMPLETE` → **`VERIFIED`**. Downstream: `IP-1104` names `IP-1100`/`IP-1101`/`IP-1102`/
`IP-1103` as dependencies — all four are now `VERIFIED` (`IP-1100` by `VR-1100`, `IP-1101`/`IP-1102`
previously, `IP-1103` by this report), so `IP-1104` is **eligible in principle** on dependency
grounds alone. It does **not** flip to `READY` by this run: backlog `BL-0119` (filed at `IP-1103`'s
own implementation time, run #161) stands as a named blocker — `IP-1104`'s package text as
currently written omits the mid-session re-entry case (`inf_ensure_window`'s cache re-derivation
would let a collected treasure respawn on walking back into a region within the same session,
before any save/load boundary), and `BL-0119` requires a `07-implementation-planning` amendment to
`IP-1104` §6 before `08-code-implementation` should pick it up. This report does not resolve or
dismiss `BL-0119` — it stays open, exactly as filed.
