# VR-1124 — Infinite Mode Combat: Save Persistence

## Package

- **ID:** IP-1124 — [Infinite Mode Combat: Save Persistence](../packages/IP-1124-infinite-mode-combat-save-persistence.md)
- **Implementing commit:** `113a7af` (feat(combat): IP-1124 — Infinite Mode Combat save persistence, FR-11600)
- **Verified:** 2026-07-20, fresh session (independent of `IP-1124`'s own 2026-07-19 implementing session)

## Result

**VERIFIED** — 0 failed checks, 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Save/load round trip reproduces identical mob state, weapon tier, player health | `T32.a` (asm_game.py:4242-4249 save block, 4380-4386 load block; test_rom.py:4212-4255) — real SAVE-screen path, real fresh-instance reload | PASS |
| Projectile never restored | `T32.b` (test_rom.py:4258-4276) — `PROJ_ACTIVE` untouched by `save_to_sram`/`try_load_save`, confirmed by direct read (only appears in a comment at asm_game.py:4236) | PASS |
| Pre-combat-mode save loads cleanly without combat fields | `T32.c1`-`c3` (test_rom.py:4279-4314) — synthetic `SAVE_VERSION_VAL=0x05` fixture with `0xFF` garbage at every new SRAM address; `COMBAT_MODE` confirmed boot-default 0 | PASS |
| `COMBAT_MODE` off at save time writes no combat-state block | `T32.d` (test_rom.py:4317-4340) — raw `.ram` file read confirms `SRAM_WEAPON_TIER`/`SRAM_PLAYER_HEALTH` left at 0 (their real nonzero defaults are 1/3, so any wrongly-written byte would show) | PASS |
| ROM builds at 32768 bytes; full suite passes | `python3 build_rom.py` → 32768 bytes (32670 used); `python3 test_rom.py` → 404/404 | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Rebuilt this run: `Wrote 32768 bytes → BunnyQuest.gbc` | PASS |
| G5: full `test_rom.py` suite passes | 404/404 passed, 0 failed (`test_results.txt`, this run) | PASS |
| T32.a-d each present and passing | All four present in `test_rom.py:4199-4341`, all `[PASS]` in this run's output | PASS |
| `save_to_sram`/`try_load_save` still open exactly one MBC1-enable bracket each | Direct read: `save_to_sram` opens at asm_game.py:4174 (`LD_A_n(0x0A)`), closes at 4255 (`XOR_A`); the combat block (4219-4249) sits inside. `try_load_save` opens at 4284, closes at 4396 (success path) / 4403 (failure path) — a single bracket with two correctly-matched exits; the combat restore (4380-4387) sits inside | PASS |
| `PROJ_ACTIVE`/`PROJ_X`/`PROJ_Y`/`PROJ_DIR` never referenced by `save_to_sram`/`try_load_save` | `grep` of lines 4170-4410 finds only one match, a comment (line 4236) explaining the exclusion — no read/write of any `PROJ_*` symbol | PASS |
| FR-11600/RTM/`SAVE_VERSION_VAL`-history/Master-Build-Plan deltas applied exactly as §9 names | See Requirements audit below and Documentation Updates check | PASS |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11600 | `asm_game.py` `save_to_sram`/`try_load_save` combat-state blocks (4219-4249, 4380-4387) | `T32.a`-`d` | `04-requirements-traceability-matrix.md:134` → `IP-1124` / `T32.a–d` | PASS |

`01-functional-requirements.md:2785-2809` FR-11600 leaf: Priority correctly reads "Must (delta
2026-07-19 — Implemented `IP-1124`)". `07-data-model.md:655-668` §7o: SRAM table (`A350`-`A371`)
matches the shipped constants exactly, address-for-address. `FS-112-infinite-mode-combat-sub-mode.md:113-116`:
Workflow E cross-reference present and accurate (`SAVE_VERSION_VAL` `0x05`→`0x06`, both routines
extended inside their existing brackets). Master Build Plan row (`00-master-build-plan.md:903`)
correctly reads `COMPLETE` pending this VR — flipped to `VERIFIED` by this run.

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed
```

## Scope audit

`git show 113a7af --stat`: `asm_game.py` (+84), `test_rom.py` (+147, new suite T32), plus exactly
the doc files §9 named (`07-data-model.md`, `FS-112...md`, `00-master-build-plan.md`,
`packages/INDEX.md`, `01-functional-requirements.md`, `04-requirements-traceability-matrix.md`)
and the two build artifacts (`BunnyQuest.gbc`, `test_results.txt`). `git show 113a7af -- asm_game.py
| grep -E '^-[^-]'` shows exactly one pre-existing line touched — the `SAVE_VERSION_VAL = 0x05`
constant and its comment, bumped to `0x06` — everything else is additive. No scope excursion.

## Findings

None.

## Independence note

This verification ran in a session distinct from `IP-1124`'s own 2026-07-19 implementing
session (run #266), satisfying the same-session independence rule the manager deferred this
pass for at the end of that session.
