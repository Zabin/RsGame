# VR-1126 — Infinite Mode Combat: Mob Movement

> Independent verification of [`IP-1126`](../packages/IP-1126-infinite-mode-combat-mob-movement.md)
> against the shipped tree. Produced by `09-package-verification`.

## Package

- **ID:** `IP-1126` — Infinite Mode Combat: Mob Movement
- **Implementing commit:** `3412be8` ("IP-1126: implement Infinite Mode Combat mob movement
  (FR-11210)", 2026-07-19)
- **Commit verified at:** `e3757d5` (tree head at verification time; several unrelated commits —
  `IP-1128`/`IP-1129` implementation, `IP-1123` Pass 2 verification, journal updates — landed
  afterward, none touching this package's own files)
- **Independence:** fresh session; no prior work on `IP-1126` or `BL-0156`/`FR-11210` performed
  in this session.

## Result

**VERIFIED** — 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| An active mob's position converges toward the player over successive recomputation intervals, exactly `MOB_MOVE_STEP` pixels on exactly one (dominant) axis per interval, at exactly the `MOB_MOVE_INTERVAL`-frame cadence | `inf_mob_move` read directly (`asm_game.py` lines 3445-3563): timer-gated cadence (`imv_move_reset` resets to `MOB_MOVE_INTERVAL=8`), dominant-axis selection via `CP L`/`JR_C` (X wins ties, matching §6's "`\|dx\| >= \|dy\|` moves X"), single-axis step of exactly `MOB_MOVE_STEP=1`. `T35.a`-`d`, `f` pass | Pass |
| A mob already coincident with the player holds still rather than jittering | Lines 3517-3519: `ax==0` checked first, falls through to check `ay==0`; both zero → `imv_skip` (no movement). `T35.e` passes | Pass |
| `COMBAT_MODE` off and inactive mob slots both correctly excluded | Line 3466: `LD_A_nn(COMBAT_MODE); OR_A(); RET_Z()` — first instruction, unconditional no-op gate. Line 3483-3485: per-slot `active` byte checked, `imv_skip` on inactive. `T35.g`/`h` pass | Pass |
| ROM builds at 32768 bytes; full suite passes; `MOB_DATA`'s 5-byte-per-slot stride unchanged | Confirmed (see Test run); implementing commit's own diff of `asm_game.py` is **purely additive** (`git show 3412be8 -- asm_game.py \| grep -E '^-[^-]'` returns no lines) — no existing line, including any `MOB_DATA` layout code, was altered | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes, valid header | Confirmed: `python3 build_rom.py` → "Wrote 32768 bytes → BunnyQuest.gbc" (32414/32768 used — later packages `IP-1128`/`IP-1129` added to this since `IP-1126`'s own 373/373-passing build) | Pass |
| G5: full `test_rom.py` suite passes | 387/387 passed, 0 failed (fresh session; `pyboy` installed this session, not preinstalled) | Pass |
| `T35.a`–`i` each present and passing | All 9 individual `check()` calls confirmed present and passing | Pass |
| Direct code read: `MOB_DATA`'s per-slot layout/stride byte-for-byte unchanged from `IP-1121`'s shipped form | Confirmed — purely-additive diff (above); `inf_mob_move` only ever writes the existing x/y fields via `INC_HL`/`DEC_HL` walks relative to the record's existing layout, no stride constant touched | Pass |
| Direct code read: `inf_mob_render`/`inf_projectile_hittest`/`inf_mob_contact_check` all unmodified by this package's own diff | Confirmed — same purely-additive diff; none of those three routines' own label ranges appear in the commit's changed-line set | Pass |
| FR-11210/RTM/`FS-112`-Open-Question-4/Master-Build-Plan/`packages/INDEX.md` deltas applied exactly as §9 names | `FR-11210` → "Implemented 2026-07-19" (`04-functional-requirements` row confirms `MOB_MOVE_INTERVAL`/`MOB_MOVE_STEP` values recorded); RTM row `FR-11210 \| ... \| IP-1126 \| T35.a-i`; `FS-112` Open Question 4 marked Resolved; Master Build Plan / `packages/INDEX.md` rows present (pre-existing this run, confirmed accurate) | Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11210 | `MOB_MOVE_TIMER`, `inf_mob_move` | `T35.a`-`i` | `FR-11210 \| Mob movement toward the player (delta 2026-07-19, BL-0156 — Implemented 2026-07-19) \| ... \| IP-1126 \| T35.a-i` | Pass |

## Test run

- `python3 build_rom.py` → 32768 bytes written (32414 used, 354 headroom — reflects the later
  `IP-1128`/`IP-1129` additions, not this package's own footprint).
- `python3 test_rom.py` → **387/387 passed, 0 failed** (fresh session).
- `T35.a`-`i` individually confirmed present and passing (9/9).

## Scope audit

Implementing commit `3412be8` touched only `asm_game.py` (purely additive — new WRAM constant,
one boot-clear line, one per-frame call-site line, one new subroutine) plus the doc files named
in §9 and standard build/test artifacts. No excursion — `inf_mob_render`, `inf_projectile_hittest`,
`inf_mob_contact_check` all confirmed byte-for-byte unaffected by direct diff inspection (no
removed/modified lines anywhere in the commit's `asm_game.py` hunk).

## Independent live drive

`MOB_MOVE_INTERVAL`/`MOB_MOVE_STEP` are compile-time Python constants baked into the ROM, not a
player- or generator-set runtime parameter in the `BL-0055` sense — no non-default-value live
drive is required by that rule. The package's own `T35.i` already independently live-drives the
real per-frame production chain (not a direct-invoke force) at a real, non-fixture player/mob
position and confirms the observed total movement matches the expected distance — re-confirmed
passing this run, and the dominant-axis/tie-break logic (`X` wins on `\|dx\|==\|dy\|`) was
independently re-derived from the assembly (not merely trusted from the Implementation Summary)
during the Definition-of-Done audit above.

## Findings

None.

## Ledger status

Per this skill's own rule, `IP-1126` advances `COMPLETE → VERIFIED` on the Master Build Plan and
`packages/INDEX.md`. No dependent package names `IP-1126` as a dependency (mob movement was a
delta off `IP-1121`, not on the original critical path), so no other package's readiness changes
as a result of this verification.
