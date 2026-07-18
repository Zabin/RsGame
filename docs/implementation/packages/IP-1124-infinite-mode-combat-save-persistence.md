# IP-1124 — Infinite Mode Combat: Save Persistence

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1124` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow E in full (the `persist` verb).
Last package in this delta's own critical path — depends on `IP-1121`/`IP-1122`/`IP-1123` for the
state fields it persists.

## 2. Objective

Extend `save_to_sram`/`try_load_save` with combat state (mob table, weapon tier, player health)
under a new `SAVE_VERSION_VAL` bump, mirroring `IP-1010`/`IP-1050`/`IP-1104`'s own established
version-byte pattern.

## 3. Requirements Covered

FR-11600 (combat state save persistence) in full.

## 4. Architecture Components

`ADS-002` Open Question 7 (resolved — combat state persists) · this project's own
strictly-monotonic `SAVE_VERSION_VAL` sequence (`IP-1010`→`IP-1050`→`IP-9110`→`IP-1104`, currently
`0x05`).

## 5. Interfaces

- **The existing `save_to_sram`/`try_load_save` routines and their existing single MBC1-enable
  bracket** (`FEAT-5000`, extended not replaced — mirrors `IP-1104`'s own extension pattern
  exactly: new fields added inside the existing bracket, no second bracket opened).
- **`SAVE_VERSION_ADDR`/`SAVE_VERSION_VAL`** (`0xA012`, existing) — bumped `0x05`→`0x06`,
  extending the sequence `IP-1104` last advanced.
- **The existing `memcpy` subroutine** (`IP-1050`'s own precedent) — reused for the `MOB_DATA`
  block transfer (30 bytes, one contiguous block both sides).
- **`IP-1121`'s `MOB_COUNT`/`MOB_DATA`, `IP-1122`'s `WEAPON_TIER`, `IP-1123`'s `PLAYER_HEALTH`** —
  consumed, not modified: this package reads and restores these fields, it does not change their
  own runtime semantics.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New SRAM constants** (first unclaimed bytes past `SRAM_LEDGER`'s own end, `0xA34F`):
    `SRAM_COMBAT_MODE = 0xA350` (1 byte, mirrors `COMBAT_MODE`), `SRAM_MOB_COUNT = 0xA351` (1
    byte), `SRAM_MOB_DATA = 0xA352` (30 bytes, `0xA352`–`0xA36F`, identical 5-byte-per-slot format
    to `MOB_DATA`), `SRAM_WEAPON_TIER = 0xA370` (1 byte), `SRAM_PLAYER_HEALTH = 0xA371` (1 byte).
    **`PROJ_*` fields are deliberately NOT persisted** — mirrors `INF_MZ_RESULT`'s own
    "transient, generation-time-only, never persisted" precedent (`ADS-002` §System
    Architecture); a loaded save always resumes with no projectile in flight.
  - **`save_to_sram`**: extended (inside the existing bracket) with a `COMBAT_MODE`-gated block
    writing `COMBAT_MODE`/`MOB_COUNT`/`MOB_DATA`/`WEAPON_TIER`/`PLAYER_HEALTH` to their SRAM
    mirrors via `memcpy` (one 34-byte contiguous transfer for the `SRAM_COMBAT_MODE`–
    `SRAM_PLAYER_HEALTH` block, since all five WRAM sources are themselves contiguous,
    `0xC6B5`–`0xC6DA`).
  - **`try_load_save`**: extended (inside the existing version-guard branch, `SAVE_VERSION_VAL ==
    0x06`) with the matching restore; a pre-combat-mode save (`SAVE_VERSION_VAL < 0x06`) loads
    cleanly with `COMBAT_MODE` defaulting to its boot-cleared 0, mirroring `IP-1104`'s own
    version-guard precedent for pre-Infinite-Mode saves exactly.
  - **`SAVE_VERSION_VAL`**: `0x05` → `0x06`.

## 7. Implementation Tasks

Ordered: (1) new SRAM constants; (2) `save_to_sram`'s new `COMBAT_MODE`-gated write block; (3)
`try_load_save`'s matching restore + version-guard extension; (4) `SAVE_VERSION_VAL` bump; (5)
rebuild ROM; (6) author new suite; (7) full suite run; (8) documentation updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T32: Combat Sub-Mode — Save Persistence`**:

- T32.a — round trip: force a known combat state (specific mob slots active with distinct
  positions/types/health, a non-default `WEAPON_TIER`, a non-max `PLAYER_HEALTH`), save, reload
  in a fresh instance, confirm every field restores exactly.
- T32.b — projectile not persisted: force an active projectile, save, reload, confirm
  `PROJ_ACTIVE` is 0 after load (never restored) — mirrors `IP-1101`'s own transient-state
  non-persistence precedent.
- T32.c — pre-combat-mode save compatibility: construct a synthetic `SAVE_VERSION_VAL == 0x05`
  fixture (mirrors `T11.d`'s own established synthetic-fixture pattern), load it, confirm
  `COMBAT_MODE` defaults to 0 and no combat field reads garbage bytes.
- T32.d — `COMBAT_MODE` off at save time: force `COMBAT_MODE=0`, save, confirm the combat-state
  block is skipped (not written) — non-regression against a pure base-Infinite-Mode save.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11600 status → Implemented.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11600 row → `IP-1124`/T32.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: implemented-by pointer for
  Workflow E; note `SAVE_VERSION_VAL`'s actual bump value (`0x06`), resolving §9's own
  "next value would be 0x06" framing as confirmed, not merely predicted.
- `docs/architecture/07-data-model.md`: new SRAM rows, `0xA350`–`0xA371`; `SAVE_VERSION_VAL`
  history table updated (sixth bump since ship).
- Master Build Plan status row.

## 10. Definition of Done

- A save/load round trip reproduces identical mob state, weapon tier, and player health; the
  projectile is never restored; a pre-combat-mode save loads cleanly without combat fields
  (T32.a–c all passing).
- `COMBAT_MODE` off at save time writes no combat-state block (T32.d).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T32.a–d each present and passing.
- [ ] Direct code read: `save_to_sram`/`try_load_save` still open exactly one MBC1-enable
      bracket — this package's own writes/reads live inside the existing bracket, not a second
      one.
- [ ] Direct code read: `PROJ_ACTIVE`/`PROJ_X`/`PROJ_Y`/`PROJ_DIR` are never referenced by
      `save_to_sram`/`try_load_save`.
- [ ] FR-11600/RTM/`SAVE_VERSION_VAL`-history/Master-Build-Plan deltas applied exactly as §9
      names.

## 12. Dependencies

- **`IP-1121`** (`MOB_COUNT`/`MOB_DATA`), **`IP-1122`** (`WEAPON_TIER`), **`IP-1123`**
  (`PLAYER_HEALTH`) — all three must be `VERIFIED` before this package can persist their real
  fields (persisting fields that don't exist yet is not meaningful work).

## 13. Risks

- **SRAM budget** (Low): 34 new bytes against `R106`'s own confirmed ~8 KiB SRAM budget,
  negligible alongside the existing `SRAM_LEDGER`'s own 640-byte claim.
- **Version-guard correctness** (Medium, mirrors `IP-1104`'s own named risk class): a wrong
  guard could either falsely reject a valid pre-combat-mode save or falsely accept its absent
  combat fields as valid data — needs the same synthetic pre-upgrade fixture discipline `T11.d`/
  `T32.c` establish.
- ROM budget: a bounded extension to two existing routines — expected modest, re-affirmed at
  build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `save_to_sram`/`try_load_save`'s new
blocks are additive within the existing bracket — reverting restores the exact pre-this-package
save format (`SAVE_VERSION_VAL` back to `0x05`), with no other save field affected.
