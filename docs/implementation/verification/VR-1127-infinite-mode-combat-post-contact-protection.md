# VR-1127 — Infinite Mode Combat: Post-Contact Player Protection

## Package

- **ID:** IP-1127 — [Infinite Mode Combat: Post-Contact Player Protection](../packages/IP-1127-infinite-mode-combat-post-contact-protection.md)
- **Implementing commit:** `a8117d7` (feat(combat): IP-1127 — post-contact player protection, FR-11410)
- **Verified:** 2026-07-20, fresh session (independent of `IP-1127`'s own 2026-07-19 implementing session)

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Exact `BL-0158` repro: sustained overlap, same mob, produces exactly one health decrement | `T36.a` (asm_game.py:3744-3894 `inf_mob_contact_check`; test_rom.py T36.a) | PASS |
| Knockback, invincibility, per-mob cooldown each independently verified, incl. cooldown outlasting invincibility and clearing only on genuine break-and-resume | `T36.b`-`e` all pass; direct code read of `imcc_hit_no_dec`/`imcc_skip`/`imcc_advance` (asm_game.py:3791-3894) confirms the bit-set-on-hit, bit-clear-on-non-overlap, bit-independent-of-invincibility-expiry logic exactly as designed | PASS |
| `COMBAT_MODE` off and a single isolated contact both unaffected by this package's new gating | `T36.h` (COMBAT_MODE-off no-op, both routines' first instruction is `RET_Z` on `COMBAT_MODE`), `T36.i` (T31 non-regression) | PASS |
| ROM builds at 32768 bytes; full suite passes; `check_collisions`/`MOB_DATA` layout unmodified | ROM rebuild 32768 bytes (32670 used, matches the package's own claim); 404/404 suite; `git show a8117d7 -- asm_game.py \| grep -E '^-[^-]'` shows only `inf_mob_contact_check`'s own prior body removed — `check_collisions` never appears in the diff | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Rebuilt this run (shared with `IP-1124`'s pass, same session, unchanged tree): 32768 bytes | PASS |
| G5: full suite passes, incl. `T31` unmodified or every change named | `T36.i` explicitly re-runs `T31`'s own single-contact scenario and confirms unchanged behavior; no `T31` assertion was altered by this package's diff (confirmed by `git show a8117d7 -- test_rom.py`, no `T31.*` lines touched) | PASS |
| T36.a–j each present and passing | 11 checks present (`a`, `b`, `c`, `c2`, `d`, `e`, `f`, `g`, `h`, `i`, `j` — one extra sub-check `c2` beyond the package's own named `a`-`j` list), all `[PASS]` | PASS |
| Direct code read: `check_collisions`/`MOB_DATA` layout byte-for-byte unchanged | `check_collisions` absent from the implementing commit's diff entirely; `MOB_DATA`'s 5-byte-per-slot stride (`asm_game.py` — x/y/species/health/active) unchanged, confirmed by the unmodified slot-read sequence at 3750-3754 | PASS |
| Direct code read: knockback's position write clamped against the same bounds player movement already enforces | `ikb_x_left_ok`/`ikb_x_right_ok`/`ikb_y_up_ok`/`ikb_y_down_ok` (asm_game.py:3836-3874) clamp to 0/152 (X) and 8/128 (Y) — the identical bound values `handle_play_input`'s own movement clamp uses at lines 1155/1184 (`CP_n(153)`/`CP_n(129)`) | PASS |
| Direct code read: `MOB_CONTACT_FLAGS` a genuinely separate table, not a widened `MOB_DATA` stride | `MOB_CONTACT_FLAGS = 0xC6E3` is a standalone 1-byte bitmask (asm_game.py:383); `MOB_DATA`'s own per-slot layout is untouched by the diff | PASS |
| FR-11410/RTM/Master-Build-Plan/`packages/INDEX.md` deltas applied exactly as §9 names; `BL-0158` closed once this pass confirms the fix live | Confirmed below | PASS |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11410 | `asm_game.py` `inf_mob_contact_check` (extended, 3717-3894) + new `inf_invincibility_tick` (3896-3904) | `T36.a`-`j` | `04-requirements-traceability-matrix.md:131` → `IP-1127` / `T36.a–j` | PASS |

`01-functional-requirements.md:2593-` FR-11410 leaf correctly reads "Implemented `IP-1127`
2026-07-19" with `INVINCIBILITY_FRAMES=30`/`KNOCKBACK_DISTANCE=16` recorded. `07-data-model.md`
§7p (lines 650, 712-715): `PLAYER_INVINCIBLE`/`MOB_CONTACT_FLAGS` rows at `0xC6E2`-`0xC6E3` match
the shipped constants exactly, including the note explaining the re-derivation from the
package's own originally-planned `0xC6DF`-`0xC6E0` (superseded by `IP-1128`'s real claim,
`BL-0163`). Master Build Plan row (`00-master-build-plan.md`) and `packages/INDEX.md` both
correctly recorded `COMPLETE` pending this VR — flipped to `VERIFIED` by this run.

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed
```

(Shared with this session's `IP-1124` verification pass — the tree was unchanged between the two
passes, so the same build/suite run stands as independent evidence for both.)

## Scope audit

`git show a8117d7 --stat`: `asm_game.py` (+200/-17, all removed lines confirmed inside
`inf_mob_contact_check`'s own prior body), `test_rom.py` (+256, new suite T36), plus exactly the
doc files §9 named (`07-data-model.md`, `FS-112...md`, `00-master-build-plan.md`,
`packages/INDEX.md`, `01-functional-requirements.md`, `04-requirements-traceability-matrix.md`)
and the two build artifacts. No scope excursion.

## Findings

None.

## Independence note

This verification ran in a session distinct from `IP-1127`'s own 2026-07-19 implementing session
(run #268), satisfying the same-session independence rule the manager deferred this pass for.

## Backlog

`BL-0158` (the live-drive finding that originated this package) closes `DONE` as a direct result
of this VR: `T36.a`/`T36.j` both independently reconfirm the fix live — sustained contact now
produces exactly one health decrement plus a perceptible knockback, not an imperceptible cascade.
