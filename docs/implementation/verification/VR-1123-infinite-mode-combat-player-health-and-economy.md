# VR-1123 — Infinite Mode Combat: Player Health, Setback & Healing Economy

> Independent verification of [`IP-1123`](../packages/IP-1123-infinite-mode-combat-player-health-and-economy.md)
> against the shipped tree. Produced by `09-package-verification`.

## Package

- **ID:** `IP-1123` — Infinite Mode Combat: Player Health, Setback & Healing Economy
- **Implementing commit:** `0ed51c4` ("feat(combat): IP-1123 -- Infinite Mode player health,
  setback & healing economy", 2026-07-18)
- **Commit verified at:** tree head at verification time (this session)
- **Independence:** fresh session, no prior work on `IP-1123` performed in this session.

## Result

**RETURNED** — 0 suite checks failed, but one genuine functional defect found by independent live
drive through the real production call chain (see Findings). `T31`'s own 7 checks all pass
because every one of them force-writes `COMBAT_ENTRY_X`/`COMBAT_ENTRY_Y` directly rather than
exercising the real "confirm seed → `INTRO` → `PLAYING`" sequence that reveals the defect — the
suite passing is not sufficient evidence here (the same class of gap `BL-0055` names: fixture
coverage that never exercises the real call ordering).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Mob contact reduces health correctly, HUD reflects it | `inf_mob_contact_check`/`inf_health_hud_draw` read directly (lines 3489-3538, 3587+); `T31.a`/`b` pass | Pass |
| Zero health triggers the setback without a `GAMESTATE` change | `inf_health_setback` (lines 3539-3550) confirmed never writes `GAMESTATE`; `T31.c` passes (with force-set `COMBAT_ENTRY_X`/`Y`) | Pass (as tested) |
| **Setback returns the player to the region-entry point** (§5 Interfaces: `COMBAT_ENTRY_X`/`Y` "recorded on every region-entry event... as the setback's own return point," explicitly including "initial Infinite Mode entry") | **Independent live drive through the real UI path found this false for the very first region of a session** — see Findings. `T31.c` cannot catch this because it force-writes `COMBAT_ENTRY_X`/`Y` rather than deriving it from the real "initial entry" call site | **Fail** |
| Heal-spend decrements the shared count, capped at max; zero-treasure spend is a no-op | `inf_heal_spend` (lines 3552-3585) read directly; `T31.d`/`d2`/`e` pass | Pass |
| `COMBAT_MODE` off leaves base-game HUD/logic inert | `T31.f` passes; every new routine's `COMBAT_MODE`-gate confirmed by direct code read | Pass |
| ROM builds at 32768 bytes; full suite passes | Confirmed (see Test run) | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes, valid header | Confirmed | Pass |
| G5: full `test_rom.py` suite passes | 363/363 passed, 0 failed | Pass |
| `T31.a`–`f` each present and passing | All 7 individual `check()` calls (`a`, `b`, `c`, `d`, `d2`, `e`, `f`) confirmed present and passing | Pass |
| Direct code read: `inf_heal_spend` decrements `RUNNING_TREASURE_COUNT` directly, no second ledger | Confirmed — `inf_heal_spend` reads/writes `RUNNING_TREASURE_COUNT` (`0xC405`) directly, no new counter in this package's own WRAM | Pass |
| Direct code read: `inf_health_setback` never writes `GAMESTATE` | Confirmed by direct read (lines 3546-3550) | Pass |
| FR-11400/FR-11500/RTM/Master-Build-Plan deltas applied; both harvested findings recorded | RTM rows correct (`FR-11400`→`T31.a-c,f`; `FR-11500`→`T31.d,d2,e,f`); `BL-0148` (heal-spend input binding) confirmed already filed; **the region-entry-point ordering defect below was not caught at planning time and is a new finding, not previously recorded** | Partial — see Findings |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11400 | `PLAYER_HEALTH`, `inf_mob_contact_check`, `inf_health_setback`, `inf_health_hud_draw` | `T31.a`-`c`, `f` | `FR-11400 \| ... \| IP-1123 \| T31.a-c, T31.f` | Pass on tested behavior; the setback's own return-point correctness (part of FR-11400's own "non-lethal setback" behavior) is not exercised by any RTM-cited test in a way that reveals the defect |
| FR-11500 | `inf_heal_spend` | `T31.d`, `d2`, `e`, `f` | `FR-11500 \| ... \| IP-1123 \| T31.d, T31.d2, T31.e, T31.f` | Pass |

## Test run

- `python3 build_rom.py` → 32768 bytes written, 32158 used.
- `python3 test_rom.py` → **363/363 passed, 0 failed** (fresh session).

## Scope audit

Implementing commit `0ed51c4` touched `asm_game.py` (declared in §6) plus the doc files named in
§9 and standard build/test artifacts. No excursion. `check_collisions` confirmed unmodified by
direct diff (`inf_mob_contact_check` is a new, separate routine reusing the same technique).

## Independent live drive (found the defect)

Not a tunable/generated-parameter package in the `BL-0055` sense, but `T31`'s own tests all force
`COMBAT_ENTRY_X`/`Y` directly via WRAM rather than deriving them from the real six recording call
sites the package's own §5 Interfaces names — so the suite's green result does not actually cover
whether those six hooks record the right value. Independently live-driven via a standalone PyBoy
script (own session): navigated the real UI path `MAIN MENU` → `MODE SELECT` (infinite) →
`COMBAT MODE CONFIRM` (confirm Y) → `INFINITE SEED ENTRY` → seed confirm → `INTRO` → `PLAYING`.

**Observed:** immediately upon reaching `PLAYING`, `PLAYER_X`/`PLAYER_Y` read `(76, 80)` (the
real spawn position `st_intro` sets) but `COMBAT_ENTRY_X`/`COMBAT_ENTRY_Y` read `(0, 0)` — not
the player's actual entry position. Root cause, confirmed by direct code read: the package's own
"initial Infinite Mode entry" hook (`asm_game.py` lines 928-929, `CALL('inf_ensure_window')` then
`CALL('inf_record_combat_entry')`) sits inside `st_infinite_seed_entry`'s own A-confirm handler,
which transitions to `GS_INTRO` — but `PLAYER_X`/`PLAYER_Y` are not set to their real spawn value
`(76, 80)` until `st_intro`'s own later, separate A-press handler (line 614-615), which runs
strictly *after* the "initial entry" hook already fired and read whatever `PLAYER_X`/`PLAYER_Y`
held at that point (0 on a fresh session — `PLAYER_X`/`Y` have no explicit boot-clear, so they
read as PyBoy's zero-initialized WRAM default).

This is a **narrow, single-site defect** — by contrast, all four `czt_infinite` direction
branches (lines 1376-1421) correctly set `PLAYER_X`/`PLAYER_Y` to the wrapped edge coordinate
*before* calling `inf_record_combat_entry`, and the post-load-restore site's own comment ("PLAYER_
X/Y already restored above," line 3928) is correct by the same logic. Only the "initial entry"
site orders its record-position call before the position it's supposed to record actually exists.

**Reproduced end-to-end:** forced an active mob onto the player's real position after reaching
`PLAYING` and let three real per-frame contacts drop `PLAYER_HEALTH` to 0 through the actual
`st_playing`→`inf_mob_contact_check` chain (not a direct-invoke hijack) — the resulting setback
correctly restored `PLAYER_HEALTH` to 3 and left `GAMESTATE` at `PLAYING` (both per spec), but
repositioned the player to `(0, 0)` — not `(76, 80)`, the position they actually entered the
region at.

**Player-facing impact:** any Infinite Mode Combat session where the player takes lethal contact
damage before ever crossing a region boundary (a common, easily-reached scenario, not an edge
case) sends the setback to the wrong position instead of the promised "position they entered the
current region at." Not data-corrupting, not crash-causing, `GAMESTATE`/health both still correct
— hence Medium, not Critical/High.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | **The "initial Infinite Mode entry" `inf_record_combat_entry` call site (`asm_game.py` lines 928-929, inside `st_infinite_seed_entry`'s A-confirm) fires before `PLAYER_X`/`PLAYER_Y` are set to their real spawn position `(76, 80)` in `st_intro` (lines 614-615) — so `COMBAT_ENTRY_X`/`COMBAT_ENTRY_Y` record `(0, 0)` instead of the player's real entry point for the first region of every session.** A zero-health setback before the player ever crosses a region boundary teleports them to `(0, 0)` instead of their actual starting position. The other five recording call sites (four `czt_infinite` direction branches + the post-load-restore path) are correctly ordered — this is isolated to the one "initial entry" site. Not caught by `T31.c` because it force-writes `COMBAT_ENTRY_X`/`Y` directly rather than deriving it from the real call chain. | Medium (real, common repro window; no crash/corruption; `GAMESTATE`/health both correct, only position wrong) | `08-code-implementation` — move the "initial entry" `inf_record_combat_entry` call from `st_infinite_seed_entry`'s own A-confirm handler (line 929) to `st_intro`'s own A-press handler, immediately after `PLAYER_X`/`PLAYER_Y` are set to `(76, 80)` (after line 615) |

## Ledger status

Per this skill's own rule ("On fail, back to `IN PROGRESS`... with a pointer to the report"),
`IP-1123` returns to `IN PROGRESS` on the Master Build Plan and `packages/INDEX.md`, pointing to
this report. `IP-1124` remains blocked (its dependency `IP-1123` is not `VERIFIED`).
