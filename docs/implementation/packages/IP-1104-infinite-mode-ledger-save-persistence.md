# IP-1104 — Infinite Mode: Visited-Region-Ledger Save Persistence

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1104` — implements part of [**FS-110**](../../features/FS-110-infinite-mode.md) (`FEAT-10000`,
Epic `EP-6000`, `Future` bucket). Covers Workflow D in full (the `persist` verb). Last package in
the tranche's critical path.

## 2. Objective

Extend `save_to_sram`/`try_load_save` with a new, ledger-based save shape for Infinite Mode:
player position (region row/col), the visited-region ledger (which regions have been visited and
whether their treasure is collected, FIFO-bounded at 128 entries), the running treasure count, and
the persistent top-3 table — bumping `SAVE_VERSION_VAL` to extend the existing monotonic sequence.

## 3. Requirements Covered

FR-10500 (save/load); FR-10600 (indefinitely-resumable run — "continue" always resumes exactly
where the player left off); NFR-5400 (ledger round-trip integrity, sized this pass).

## 4. Architecture Components

[ADR-0006](../../architecture/adr/ADR-0006-mbc1-battery-sram.md) (MBC1+RAM+BATTERY mechanism,
single save slot, unchanged) · this package's own Technical Work Breakdown sizing decisions (128
entries × 5 bytes, FIFO eviction, `SAVE_VERSION_VAL` `0x04`→`0x05`).

## 5. Interfaces

- **The existing `save_to_sram`/`try_load_save` routines and their existing single MBC1-enable
  bracket** (`FEAT-5000`, extended not replaced — mirrors `IP-1050`'s own extension pattern
  exactly: new fields added inside the existing bracket, no second bracket opened).
- **`SAVE_VERSION_ADDR`/`SAVE_VERSION_VAL`** (`0xA012`, existing) — bumped `0x04`→`0x05`, extending
  the strictly-monotonic sequence `IP-9110` last advanced (Technical Work Breakdown's own
  resolution of `OQ7` — a single version guard covers both save shapes, selected by the persisted
  `GAME_MODE` byte, not a second parallel version scheme).
- **The existing `memcpy` subroutine** (`IP-1050`'s own precedent) — reused for the 640-byte
  ledger transfer, not an unrolled loop.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New SRAM constants** (first unclaimed bytes past `SRAM_SCOREITEM`'s own end, `0xA0C0`):
    `SRAM_GAME_MODE = 0xA0C1` (1 byte, mirrors `GAME_MODE`), `SRAM_INF_ROW = 0xA0C2` (2 bytes),
    `SRAM_INF_COL = 0xA0C4` (2 bytes), `SRAM_RUNNING_TREASURE_COUNT = 0xA0C6` (2 bytes),
    `SRAM_TOP_SCORE_TABLE = 0xA0C8` (6 bytes — persists across new games, not per-run: a "new
    game" starting a fresh `RUNNING_TREASURE_COUNT` at Infinite Mode entry does not clear this
    table, the same "persistent high score, distinct from per-run state" split `ADR-0017` point 4
    already frames), `SRAM_LEDGER_COUNT = 0xA0CE` (1 byte, number of valid entries, 0-128),
    `SRAM_LEDGER_CURSOR = 0xA0CF` (1 byte, FIFO write cursor, 0-127), `SRAM_LEDGER = 0xA0D0` (640
    bytes, `0xA0D0`–`0xA34F`, 128 entries × 5 bytes: row signed 16-bit, col signed 16-bit,
    collected-flag 1 byte).
  - **`save_to_sram` (existing label):** inside the existing single MBC1-enable bracket, gains a
    `GAME_MODE`-gated block — when `GAME_MODE == 1`: write `SRAM_GAME_MODE`, `SRAM_INF_ROW`/`COL`
    (from `INF_ROW`/`INF_COL`), `SRAM_RUNNING_TREASURE_COUNT`, `SRAM_TOP_SCORE_TABLE` (always
    written regardless of mode — the persistent table, §above), and the ledger via the existing
    `memcpy` subroutine. When `GAME_MODE == 0` (finite mode saving): `SRAM_GAME_MODE` still
    written (`=0`), the Infinite-Mode-only fields (`SRAM_INF_ROW`/`COL`/ledger) left as whatever
    they last held — never read back unless `GAME_MODE` on load says `1` (§ below), so stale
    bytes are harmless, mirroring `ADR-0010`'s own "unread fields are inert" framing for the
    finite mode's own version-guard discipline.
  - **`try_load_save` (existing label):** version check widened to accept `0x05`; on a matching
    version, restores `GAME_MODE` first, then branches: `GAME_MODE == 0` restores exactly as
    today (unchanged); `GAME_MODE == 1` restores `INF_ROW`/`INF_COL`, `RUNNING_TREASURE_COUNT`,
    `TOP_SCORE_TABLE`, and the ledger (`memcpy`), **then calls `IP-1102`'s `inf_ensure_window`**
    to re-materialize the 3×3 working set around the restored position (no region's biome/
    connectivity is ever itself persisted — re-derived on demand, `FR-10500`'s own explicit
    requirement) — and, for each of the up-to-128 restored ledger entries whose position falls
    within the freshly-materialized window, restores `INF_TREASURE_HERE`'s own cleared/set state
    by cross-referencing the ledger's collected-flag (a small, bounded lookup — at most 9 window
    cells checked against at most 128 ledger entries, not a full linear scan of anything larger).
  - **New subroutine `inf_ledger_mark_collected`** (the forward call `IP-1103`'s own collection
    branch names) — inputs: current `INF_ROW`/`INF_COL`. Searches `SRAM_LEDGER`'s first
    `SRAM_LEDGER_COUNT` entries for a matching `(row, col)`; if found, sets its collected-flag; if
    not found (first visit to this region) and `SRAM_LEDGER_COUNT < 128`, appends a new entry
    (row, col, collected=1) and increments `SRAM_LEDGER_COUNT`; if not found and the ledger is
    full (`SRAM_LEDGER_COUNT == 128`), overwrites the entry at `SRAM_LEDGER_CURSOR` (FIFO
    eviction, Technical Work Breakdown's own resolution of `OQ5`) and advances
    `SRAM_LEDGER_CURSOR` modulo 128 (a `AND 0x7F` mask, no `DIV`).
  - **`try_load_save`'s existing pre-upgrade rejection path (existing behavior, unchanged):** a
    version-mismatched save (anything other than `0x05`) is still treated as pre-upgrade — no
    `continue` option offered, mirroring `IP-9070`'s own precedent exactly. This includes every
    prior version value (`0x01`-`0x04`), none of which ever wrote `GAME_MODE` — confirming a
    pre-Infinite-Mode save cannot be misread as an Infinite Mode save (`FS-110` §12's named edge
    case, resolved: rejected outright by the version guard, not partially loaded).

## 7. Implementation Tasks

Ordered: (1) new SRAM constants; (2) `save_to_sram`'s `GAME_MODE`-gated write block (position,
running count, top-3 table, ledger via `memcpy`); (3) `SAVE_VERSION_VAL` bump `0x04`→`0x05`,
`try_load_save`'s version-check widening; (4) `try_load_save`'s `GAME_MODE`-gated restore block,
including the `inf_ensure_window` re-materialization call and the ledger-cross-reference
`INF_TREASURE_HERE` restore; (5) `inf_ledger_mark_collected` (search, append, or FIFO-evict); (6)
wire `IP-1103`'s own collection branch to call `inf_ledger_mark_collected`; (7) rebuild ROM; (8)
author T26 (see §8); (9) full suite run; (10) documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T26: Infinite Mode — Ledger Save Persistence`**:

- T26.a — two-instance save/reload harness (mirroring `IP-1050`'s own `T15` pattern): materialize
  a region, collect its treasure, move to a second region, save, load in a fresh instance →
  assert `INF_ROW`/`INF_COL`, `RUNNING_TREASURE_COUNT`, and the first region's own collected-state
  (via `INF_TREASURE_HERE` after re-materialization) all restore exactly (AC-5).
- T26.b — no region's biome/connectivity is itself persisted: direct SRAM-byte audit confirms
  `SRAM_LEDGER`'s 5-byte-per-entry format contains no biome/connectivity field, only
  position+collected-flag (AC-5's own explicit "no SRAM field represents biome or connectivity"
  clause).
- T26.c — FIFO eviction: fill the ledger to exactly 128 entries, visit a 129th distinct region →
  assert the entry at the pre-eviction `SRAM_LEDGER_CURSOR` position is overwritten, all others
  unchanged, `SRAM_LEDGER_COUNT` stays at 128.
- T26.d — pre-upgrade rejection: a synthetic `version=0x04` fixture (the pre-Infinite-Mode value)
  → assert "continue" absent, mirroring `T11.d`/`T16.d`'s own established pattern.
- T26.e — finite-mode save round-trip regression: a `GAME_MODE=0` save/load cycle restores
  exactly as before this package (`T15`'s own existing checks, re-run unmodified against the new
  `SAVE_VERSION_VAL`).
- T26.f — indefinite resumability (AC-6): from a loaded Infinite Mode save, attempt every
  reachable input sequence from the equivalent of `PLAYING` — assert none forcibly ends the run or
  transitions anywhere but `PLAYING`/`SAVE`/`MAP`-equivalent states (mirrors `T13.e`'s/`T14.e`'s
  own systematic negative-test-sweep shape, FR-10600).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-10500/FR-10600 status → Implemented;
  NFR-5400 status → Met (sized: 128 entries × 5 bytes = 640 bytes, against ~8 KiB SRAM budget).
- `docs/architecture/07-data-model.md` (GDS-07): new SRAM section recording
  `SRAM_GAME_MODE`/`SRAM_INF_ROW`/`SRAM_INF_COL`/`SRAM_RUNNING_TREASURE_COUNT`/
  `SRAM_TOP_SCORE_TABLE`/`SRAM_LEDGER_COUNT`/`SRAM_LEDGER_CURSOR`/`SRAM_LEDGER`'s addresses;
  `SAVE_VERSION_VAL`'s row updated to `0x05` (fifth bump since ship).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-10500/FR-10600/NFR-5400 rows →
  `IP-1104`/T26.
- `docs/features/FS-110-infinite-mode.md` metadata: implemented-by pointer for Workflow D in
  full; §19 Open Questions 5 and 7 marked Resolved (ledger capacity/FIFO eviction, save-format
  version value). **This closes the Infinite Mode tranche's own Files-to-Modify set** — Open
  Question 3 (`BL-0112`) remains the tranche's sole standing gap, per `IP-1103`'s own explicit
  scope boundary.
- Master Build Plan status row.

## 10. Definition of Done

- A full save/load round trip restores position, running count, top-3 table, and every ledger
  entry's collected-state exactly (T26.a).
- No SRAM byte represents a region's biome or connectivity (T26.b, direct audit).
- FIFO eviction behaves correctly at capacity (T26.c).
- A pre-Infinite-Mode save is cleanly rejected, never partially loaded (T26.d).
- The finite mode's own save/load is provably unaffected (T26.e).
- No reachable input sequence forcibly ends a loaded Infinite Mode run (T26.f, FR-10600).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T26.a–f each present and passing.
- [ ] Direct code read: `save_to_sram`/`try_load_save` still use exactly one MBC1-enable bracket
      (no second bracket opened for the new fields).
- [ ] Direct code read: `SRAM_LEDGER`'s 5-byte entry format matches §6 exactly — no biome/
      connectivity field present anywhere in the ledger's own byte layout.
- [ ] Direct code read: `try_load_save`'s `GAME_MODE == 1` restore branch calls
      `IP-1102`'s `inf_ensure_window` before any gameplay frame renders — no window/render call
      is skipped on the load path the way it would be if only WRAM were restored.
- [ ] FR-10500/FR-10600/NFR-5400/GDS-07/RTM/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1100`** (**NOT YET `VERIFIED`**) — `GAME_MODE`'s own WRAM definition.
- **`IP-1101`** (**NOT YET `VERIFIED`**) — the position/region format this package's ledger
  entries encode.
- **`IP-1102`** (**NOT YET `VERIFIED`**) — `inf_ensure_window`, called on load to re-materialize
  the working set around the restored position.
- **`IP-1103`** (**NOT YET `VERIFIED`**) — `RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE`'s own WRAM
  definitions, and the collection branch this package's `inf_ledger_mark_collected` is called
  from.
- **`IP-1050`/`FEAT-5300`** (`VERIFIED`) — the existing `save_to_sram`/`try_load_save`/`memcpy`
  extension pattern this package follows exactly.
- **`IP-9070`/`FEAT-5220`** (`VERIFIED`) — the most recent prior `SAVE_VERSION_VAL` precedent this
  package's own bump extends.

Last package in the tranche's critical path — depends on all four other Infinite Mode packages.

## 13. Risks

- **640-byte SRAM ledger is a substantial single addition** (Low, against an ~8 KiB budget with
  only ~193 bytes currently used) — re-affirmed at build time via a direct SRAM-map audit, not
  merely computed here.
- **`try_load_save`'s `GAME_MODE`-gated restore branch is the single most save-format-invasive
  change in this tranche** (Medium) — extends, rather than replaces, the existing routine
  (mirrors `IP-1050`'s own precedent), but a version-guard defect here would affect every future
  save, both modes; T26.d/e's own explicit regression coverage is this package's primary
  mitigation.
- **The ledger's FIFO eviction policy (Technical Work Breakdown's own choice) may prove
  player-hostile in extended play** (Low, named not hidden) — evicting the oldest visited region
  means a very long run could "forget" a treasure the player collected early, re-offering it as
  uncollected on re-approach; a future revision could switch to a different eviction rule, an
  observation for `09`/`10`, not resolved here.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `SAVE_VERSION_VAL` reverts to `0x04` —
existing (finite-mode, version-4) saves remain loadable by the reverted-from build unchanged; any
Infinite Mode (version-5) save created before the revert becomes pre-upgrade and is cleanly
excluded from "continue," exactly as every prior version bump has behaved on revert.
