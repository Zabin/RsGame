# VR-1122 — Infinite Mode Combat: Weapon Fire & Hit Resolution

> Independent verification of [`IP-1122`](../packages/IP-1122-infinite-mode-combat-weapon-fire-and-hit-resolution.md)
> against the shipped tree. Produced by `09-package-verification`.

## Package

- **ID:** `IP-1122` — Infinite Mode Combat: Weapon Fire & Hit Resolution
- **Implementing commit:** `072af1b` ("feat(combat): IP-1122 -- Infinite Mode weapon fire & hit
  resolution", 2026-07-18)
- **Commit verified at:** tree head at verification time (this session)
- **Independence:** fresh session, no prior work on `IP-1122` performed in this session.

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Fire input spawns exactly one projectile at a time, moves it correctly, resolves hits at `WEAPON_TIER`-scaled damage, deactivates cleanly on hit or terminal boundary | `handle_play_input`'s new branch (lines ~1049-1053), `inf_projectile_update`/`inf_projectile_hittest` (lines ~3403-3472) read directly; `T30.a`/`b`/`c`/`c2`/`d` all pass; independently reproduced live via PyBoy through the **real production per-frame call chain** (button press → `handle_play_input` fire branch → `inf_projectile_update` per-frame movement → `inf_projectile_hittest` → `inf_mob_defeat`), not the suite's own PC-hijack direct-invoke technique — mob health 1→0, `MOB_COUNT` 1→0, `PROJ_ACTIVE` cleared on hit, all observed across real ticks | Pass |
| `COMBAT_MODE` off leaves the A button a no-op, unchanged from today | `T30.e` passes; `handle_play_input`'s new branch confirmed gated on `COMBAT_MODE != 0` by direct code read (line ~1049 region, gate precedes the branch) | Pass |
| ROM builds at 32768 bytes; full suite passes | `python3 build_rom.py` → 32768 bytes, 32158 used; full suite 363/363 | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes, valid header | Confirmed (see Test run) | Pass |
| G5: full `test_rom.py` suite passes | 363/363 passed, 0 failed | Pass |
| `T30.a`–`e` each present and passing | All 6 individual `check()` calls (`a`, `b`, `c`, `c2`, `d`, `e`) confirmed present and passing | Pass |
| Direct code read: hit-test reuses `check_collisions`' own asymmetric-tolerance technique verbatim | `inf_projectile_hittest` (lines 3437-3472) uses the identical `CP_n(8)`/`CP_n(16)` unsigned-subtract-then-compare pattern `check_collisions` itself uses (same 8×16 box constants) | Pass |
| Direct code read: `check_collisions` itself unmodified | `git show 072af1b -- asm_game.py`: `check_collisions`'s own label/body has zero diff lines; only its existing (pre-existing) call site is unchanged; `inf_projectile_hittest` is a wholly new, separate routine | Pass |
| FR-11300/RTM/Master-Build-Plan deltas applied; `WEAPON_TIER` funding-gap finding harvested | FR-11300 status "Implemented — 2026-07-18"; RTM row `IP-1122 \| T30.a-e, T30.c2`; Master Build Plan row updated; funding-gap finding traced to `BL-0147` (filed at planning time, run #230, `SCHEDULED` for a future `04` delta) — already in the backlog, not lost | Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11300 | `asm_game.py`: `PROJ_ACTIVE`/`PROJ_X`/`PROJ_Y`/`PROJ_DIR`/`WEAPON_TIER` (`0xC6D5`-`0xC6D9`), `handle_play_input`'s fire branch, `inf_projectile_update`, `inf_projectile_hittest`, `update_oam`'s projectile OAM entry | `T30.a`-`e`, `T30.c2` | `FR-11300 \| Ranged weapon fire and hit resolution (Implemented — 2026-07-18) \| ... \| IP-1122 \| T30.a-e, T30.c2` — matches shipped state | Pass |

`docs/architecture/07-data-model.md` §7j confirmed present (`PROJ_*`/`WEAPON_TIER` rows,
`0xC6D5`-`0xC6D9`, funding-mechanism-not-yet-built note preserved). `FS-112` metadata confirms
Workflow C implemented-by pointer to `IP-1122`.

## Test run

- `python3 build_rom.py` → 32768 bytes written, 32158 used, 610 headroom — same figures as
  `IP-1120`'s own build (all six combat packages are on the current tree head together).
- `python3 test_rom.py` → **363/363 passed, 0 failed** (fresh session).

## Scope audit

Implementing commit `072af1b` touched `asm_game.py` (declared in §6) plus the doc files named in
§9 (`docs/architecture/07-data-model.md`, `FS-112`, Master Build Plan, `packages/INDEX.md`,
functional requirements, RTM) and standard build/test artifacts (`BunnyQuest.gbc`, `test_rom.py`,
`test_results.txt`). No excursion.

## Named deviation (not a defect)

`PROJ_DIR` ships as a 2-value encoding (0=right, 1=left, mirroring `PLAYER_DIR`'s own real
encoding) rather than the package's own planning-time "0-3" assumption — `PLAYER_DIR` is written
only by the RIGHT/LEFT input branches, never UP/DOWN, confirmed by direct code read of
`handle_play_input`. `FR-11300`'s own Notes explicitly delegate the exact facing-direction
mechanism to `06`/`08` discretion, so this is a documented, in-scope implementation choice, not an
unresolved gap. Already tracked as `BL-0151` (Low, `DEFERRED`) — not re-filed.

## Independent live drive

Not a tunable/generated-parameter package in the `BL-0055` sense (no seed/scale/count the DoD
varies), but the suite's own `T30` tests all use a PC-hijack direct-invoke technique on
`handle_play_input`/`inf_projectile_update` in isolation — never the real per-frame call chain a
player's button press actually drives. Independently live-driven via a standalone PyBoy script
(own session): navigated `MAIN MENU` → `MODE SELECT` (infinite) → `COMBAT MODE CONFIRM` (confirm
Y) → `INFINITE SEED ENTRY` → `PLAYING`, confirmed `COMBAT_MODE=1`/`GAME_MODE=1` via the real UI
path; forced an active mob 5px from the player's real position via WRAM; pressed A once (real
joypad input, not a register hijack) — observed, across real ticks:

1. `PROJ_ACTIVE` set to 1, `PROJ_X`/`PROJ_Y` spawned at the player's real position, in the same
   frame `inf_projectile_update`'s own per-frame hook already advanced it one pixel (77, matching
   the frame's real dispatch order: fire branch runs, then the per-frame movement call later in
   the same frame's chain — both wired correctly into the real loop, not just callable in
   isolation).
2. The projectile continued advancing across subsequent real ticks (78, ...).
3. After 3 more real frames, `PROJ_ACTIVE` cleared; mob health read 0, mob `active` cleared,
   `MOB_COUNT` decremented to 0 — the full fire→move→hit→defeat chain reproduced end-to-end
   through the actual production call path.

(The 5px offset chosen for this drive placed the mob almost directly adjacent to/overlapping the
player sprite, so the before/after screenshots don't visually distinguish the mob clearly — a
self-inflicted test-setup artifact, not a rendering defect; the WRAM-level evidence above is
definitive and unambiguous.)

## Findings

None.
