# VR-1123 (Pass 2) — Infinite Mode Combat: Player Health, Setback & Healing Economy

> Independent re-verification of [`IP-1123`](../packages/IP-1123-infinite-mode-combat-player-health-and-economy.md)
> after the `BL-0154` remediation. Produced by `09-package-verification`. Supersedes Pass 1
> ([VR-1123](VR-1123-infinite-mode-combat-player-health-and-economy.md), `RETURNED`) for the
> `COMPLETE → VERIFIED` decision; Pass 1's report is left in place as the historical record of the
> defect it found.

## Package

- **ID:** `IP-1123` — Infinite Mode Combat: Player Health, Setback & Healing Economy
- **Implementing commit (original):** `0ed51c4`
- **Remediating commit (`BL-0154` fix):** `a4a02e9` ("feat(combat): IP-1123 remediation --
  BL-0154 region-entry-point fix", 2026-07-19)
- **Commit verified at:** `e08eb74` (tree head at verification time)
- **Independence:** fresh session; no prior work on `IP-1123`, `BL-0154`, or this package
  performed in this session. This session's only prior action was installing `pyboy` (not
  present in the environment) to run the gates.

## Result

**VERIFIED** — 0 findings. The `BL-0154` defect from Pass 1 (initial-entry `COMBAT_ENTRY_X`/`Y`
recording `(0,0)` instead of the player's real spawn position) is confirmed fixed by direct code
read, by the suite's own new regression check (`T31.g`), and by an independent live drive of my
own that reproduces the exact end-to-end scenario Pass 1 used to find the original defect.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Mob contact reduces health correctly, HUD reflects it | `inf_mob_contact_check`/`inf_health_hud_draw` unchanged since Pass 1 (confirmed by diff — `BL-0154` commit touches only the entry-recording call sites and their comments); `T31.a`/`b` pass | Pass |
| Zero health triggers the setback without a `GAMESTATE` change | `inf_health_setback` unchanged since Pass 1; `T31.c` passes; my own live drive (below) confirms `GAMESTATE` stays `2` (`PLAYING`) through a real setback | Pass |
| **Setback returns the player to the region-entry point**, including "initial Infinite Mode entry" | **Fixed.** Direct code read: the `inf_record_combat_entry` call at the old site (`st_infinite_seed_entry`'s A-confirm, ex-line 929) is removed; a new call now sits in `st_intro`'s A-press handler, immediately after `PLAYER_X`/`PLAYER_Y` are set to `(76, 80)`. `T31.g` (new) and my own independent live drive (below) both confirm `COMBAT_ENTRY_X`/`Y` now match the real spawn position, and a real end-to-end zero-health setback repositions the player correctly | Pass |
| Heal-spend decrements the shared count, capped at max; zero-treasure spend is a no-op | `inf_heal_spend` unchanged since Pass 1; `T31.d`/`d2`/`e` pass | Pass |
| `COMBAT_MODE` off leaves base-game HUD/logic inert | `T31.f` passes | Pass |
| ROM builds at 32768 bytes; full suite passes | Confirmed (see Test run) | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes, valid header | Confirmed: `python3 build_rom.py` reports "Wrote 32768 bytes → BunnyQuest.gbc", 32414/32768 bytes used | Pass |
| G5: full `test_rom.py` suite passes | 387/387 passed, 0 failed (fresh session; the count is higher than the `BL-0154` commit's own recorded 364/364 because `IP-1128`/`IP-1129` added `T37`/`T38` afterward — unrelated to this package) | Pass |
| `T31.a`–`g` each present and passing | All 8 individual `check()` calls (`a`, `b`, `c`, `d`, `d2`, `e`, `f`, `g`) confirmed present and passing | Pass |
| Direct code read: `inf_heal_spend` decrements `RUNNING_TREASURE_COUNT` directly, no second ledger | Re-confirmed, unchanged since Pass 1 | Pass |
| Direct code read: `inf_health_setback` never writes `GAMESTATE` | Re-confirmed, unchanged since Pass 1 | Pass |
| FR-11400/FR-11500/RTM/Master-Build-Plan deltas applied; both harvested findings recorded | `FR-11400` RTM row now reads "Implemented — 2026-07-18, region-entry-point ordering fixed 2026-07-19, `BL-0154`" and tests `T31.a-c, T31.f-g`; Master Build Plan / `packages/INDEX.md` rows record the Pass 1 finding and the remediation; `BL-0154` itself carries the fix in its own backlog row | Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11400 | `PLAYER_HEALTH`, `inf_mob_contact_check`, `inf_health_setback`, `inf_health_hud_draw`, `inf_record_combat_entry` (6 call sites, now all correctly ordered) | `T31.a`-`c`, `f`, `g` | `FR-11400 \| Implemented (region-entry-point ordering fixed) \| ... \| IP-1123 \| T31.a-c, T31.f-g` | Pass — the specific gap Pass 1 found is now exercised and confirmed correct by both the suite and an independent live drive |
| FR-11500 | `inf_heal_spend` | `T31.d`, `d2`, `e`, `f` | `FR-11500 \| ... \| IP-1123 \| T31.d, T31.d2, T31.e, T31.f` | Pass (unchanged since Pass 1) |

## Test run

- `python3 build_rom.py` → 32768 bytes written (32414 used, 354 headroom — reflects `IP-1126`/
  `IP-1128`/`IP-1129`'s own later additions, not this package).
- `python3 test_rom.py` → **387/387 passed, 0 failed** (fresh session; `pyboy` installed into
  this session's environment since it was not preinstalled).
- `T31.a`–`g` individually confirmed present and passing (see grep output below).

```
[PASS] T31.a Mob contact reduces health by exactly 1
[PASS] T31.b HUD reflects health: row-1 heart cells render the matching full/empty pattern for health 0-3
[PASS] T31.c Zero-health setback: health resets to max, position returns to region-entry point, GAMESTATE unchanged
[PASS] T31.d Heal-spend decrements RUNNING_TREASURE_COUNT by 1 and increases PLAYER_HEALTH by 1
[PASS] T31.d2 Spot: heal-spend at max health still spends treasure but does not exceed the health cap
[PASS] T31.e Heal-spend at zero treasure is a no-op (no change to RUNNING_TREASURE_COUNT or PLAYER_HEALTH)
[PASS] T31.f COMBAT_MODE off: no row-1 HUD write, mob-contact/heal-spend logic never executes
[PASS] T31.g BL-0154 regression: initial-entry COMBAT_ENTRY_X/Y match the player's real spawn position
```

## Scope audit

Remediating commit `a4a02e9` touched `asm_game.py` (moves one `CALL` from one existing handler to
another, updates comments), `test_rom.py` (adds `T31.g` only), and the doc files named in the
package's own §9 / the commit message (`docs/architecture/07-data-model.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/requirements/04-requirements-traceability-matrix.md`) plus the standard build artifacts
(`BunnyQuest.gbc`, `test_results.txt`). No excursion — no other routine, WRAM address, or file
outside this package's own declared scope was touched. `check_collisions`, `inf_mob_contact_check`,
`inf_health_setback`, `inf_heal_spend`, `inf_health_hud_draw` all confirmed byte-for-byte
unaffected by this remediation (only `inf_record_combat_entry`'s own call sites moved).

## Independent live drive (confirms the fix, mirrors Pass 1's own repro)

Not a tunable/generated-parameter package in the `BL-0055` sense, but this is exactly the class of
gap Pass 1 caught (a suite that force-writes the field under test rather than deriving it from the
real call chain), so re-deriving it live — not just trusting the new `T31.g` check — is the right
bar here. Ran a standalone PyBoy script (own session, not `test_rom.py`) that:

1. Drove the real UI path `MAIN MENU` → `MODE SELECT` (infinite) → `COMBAT MODE CONFIRM`
   (confirm Y) → `INFINITE SEED ENTRY` → seed confirm → `INTRO` → `PLAYING`.
2. Confirmed, on first arrival at `PLAYING`: `PLAYER_X`/`PLAYER_Y` = `(76, 80)` and
   `COMBAT_ENTRY_X`/`Y` = `(76, 80)` — matching (Pass 1 found `(0, 0)` here).
3. **Went further than `T31.g`**: placed an active mob directly on the player's real position and
   ticked through the real `st_playing` per-frame loop (not a direct-invoke hijack) until three
   real contacts drove `PLAYER_HEALTH` to 0 and the real `inf_health_setback` fired.
4. **Observed:** `GAMESTATE` remained `2` (`PLAYING`, never changed); `PLAYER_HEALTH` reset to `3`;
   the player's position was set to `(76, 80)` — the real spawn point, exactly matching the
   position they actually entered the region at. This is the precise end-to-end scenario Pass 1
   used to demonstrate the defect (teleport to `(0, 0)`); it now resolves correctly.

## Findings

None.

## Ledger status

Per this skill's own rule, `IP-1123` advances `COMPLETE → VERIFIED` on the Master Build Plan and
`packages/INDEX.md`. `IP-1124` (`IP-1121` VERIFIED, `IP-1122` VERIFIED, `IP-1123` now VERIFIED) —
all dependencies now `VERIFIED` — flips to `READY`. `IP-1127` (`BLOCKED` on `IP-1123` reaching
`VERIFIED`) unblocks structurally, but remains `NOT AUTHORIZED` (G3 still owed — a separate gate,
not resolved by this run) and still needs its own stale-WRAM-address re-derivation past
`IP-1128`'s real `0xC6DF`–`0xC6E1` claim before it can be built.
