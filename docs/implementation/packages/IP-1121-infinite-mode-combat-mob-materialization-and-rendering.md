# IP-1121 — Infinite Mode Combat: Mob Materialization, Rendering & Defeat

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1121` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow B in full (the `generate` and
`render` verbs for mobs). This tranche's foundational package — defines the `COMBAT_MODE` flag
every other package in this delta reads, mirroring `IP-1101`'s own root-of-tranche role for
`FS-110`.

## 2. Objective

Implement per-region mob presence/type/position materialization as a pure function of
`(SEED, row, col)`, independent of that region's own biome/treasure draws; render up to six
active mobs to shadow OAM each frame; implement non-graphic mob defeat (deactivation, no
persistent corpse). Defines the `COMBAT_MODE` WRAM flag (boot-cleared to 0) that gates this
package's own draw and every downstream combat package's own logic.

## 3. Requirements Covered

FR-11200 (mob presence, materialization, and defeat) in full; the `COMBAT_MODE`-gating half of
FR-11100 (the flag itself — the MODE SELECT UI that sets it is `IP-1120`'s own scope).

## 4. Architecture Components

`ADS-002` §System Architecture (mob entities, mob spawning, sprite budget) and §Domain Model
(`Mob`, `COMBAT_MODE`) · `R115` (OAM headroom, 31-of-40-free measurement this package's own
6-slot default is sized against) · `R218` (poof-defeat convention, mob variety-within-tone
framing).

## 5. Interfaces

- **`IP-1102`'s `inf_ensure_window`** (extended, not replaced — mirrors `IP-1103`'s/`IP-1104`'s
  own established "a later package extends an already-`VERIFIED` upstream routine" pattern on
  this exact routine) — this package adds a `COMBAT_MODE`-gated mob-presence draw immediately
  after the existing treasure-presence write, its own new, independent `gw_prng_step` call in the
  same reseed chain.
- **`gw_prng_step`'s existing shift/XOR-only construction** (unchanged) — reused for the
  mob-presence draw. This package does not modify `gw_prng_step` itself.
- **`update_oam`'s existing shadow-OAM write loop** (extended, not replaced) — a new loop segment
  appended after the existing player+collectible entries, writing up to 6 active mob entries,
  each consuming one `OAM_BUF` slot per `ADR-0007`'s 8×16 OBJ convention (2 tiles/sprite, but one
  OAM entry per sprite — `ADR-0007`'s own established shape).
- **`TL_MOB`/`TL_MOB_BOT`** (`IP-1125`, `0x0A`/`0x0B`) — the sprite tiles this package's OAM
  writes reference.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constants** (first unclaimed bytes past `MUSIC_BASE_HI`'s own end, `0xC6B4`):
    `COMBAT_MODE = 0xC6B5` (1 byte, boot-cleared, valid only alongside `GAME_MODE=1` per
    `ADS-002`), `MOB_COUNT = 0xC6B6` (1 byte, active mob count, mirrors `COLL_COUNT`'s own
    convention), `MOB_DATA = 0xC6B7` (30 bytes, `0xC6B7`–`0xC6D4`: 6 slots × 5 bytes/slot — `x`
    (1 byte), `y` (1 byte), `type` (1 byte, species index, room for future variety per `R218`),
    `health` (1 byte), `active` (1 byte flag), mirroring `ADS-002`'s own committed `Mob` shape).
  - **New subroutine `inf_materialize_mobs`** — called from `inf_ensure_window`, gated on
    `COMBAT_MODE != 0`: for the materializing region's `(row, col)`, draw mob presence via a new
    sequential `gw_prng_step` call (own reseed chain, per `ADS-002`'s no-correlation discipline)
    against a density mask (mirrors `inf_materialize_region`'s own `AND 0x0F` treasure-presence
    technique, tuned constant TBD at implementation time, named in Risks); on presence, populate
    the next free `MOB_DATA` slot (position derived from the region's own materialized-window
    placement, type drawn from a second sequential draw mod the current species count) and
    increment `MOB_COUNT`.
  - **New subroutine `inf_mob_render`** — called from `update_oam`, appended after the existing
    collectible-entry loop: iterates active `MOB_DATA` slots, writes one `OAM_BUF` entry per
    active mob (`TL_MOB` tile, position from the slot, `ADR-0007`'s 8×16 attribute byte).
  - **New subroutine `inf_mob_defeat`** — deactivates a mob slot (clears its `active` flag,
    decrements `MOB_COUNT`) and triggers a brief flash-then-deactivate presentation (mirrors how
    a collected `ScoreItem` already deactivates — no persistent corpse, no graphic content, per
    `R218`). Called by `IP-1122`'s own hit-resolution logic, not directly by this package (this
    package only defines and exposes the subroutine).
  - **`worldgen.py`**: new `materialize_mobs(seed, row, col)` Python function, mirroring
    `inf_materialize_mobs`'s draw steps exactly, for the lockstep oracle discipline `ADR-0016`
    point 8 already established for this family of routines.

## 7. Implementation Tasks

Ordered: (1) `COMBAT_MODE`/`MOB_COUNT`/`MOB_DATA` WRAM constants + boot-clear; (2)
`inf_materialize_mobs`' presence draw + slot population; (3) `worldgen.py` mirror; (4)
`inf_mob_render`'s OAM-write loop; (5) `inf_mob_defeat` (deactivation + presentation stub,
consumed by `IP-1122`); (6) rebuild ROM; (7) author new suite (oracle-vs-SM83 lockstep,
determinism, `COMBAT_MODE`-off no-op confirmation); (8) full suite run; (9) documentation
updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T29: Combat Sub-Mode — Mob Materialization & Rendering`**:

- T29.a — property test: for a `(SEED, row, col)` corpus with `COMBAT_MODE` forced on,
  materializing the same region twice produces byte-identical mob presence/type/position both
  times (FR-11200's own determinism half).
- T29.b — oracle-vs-SM83 lockstep: the same corpus, `worldgen.py`'s `materialize_mobs` vs. the
  live ROM's `inf_materialize_mobs`, 0 mismatches required.
- T29.c — `COMBAT_MODE` off: a region materialized with the flag forced to 0 shows `MOB_COUNT==0`
  and is otherwise byte-for-byte identical to the pre-this-package Infinite Mode behavior
  (confirms this capability is additive, not a fork of the generation algorithm).
- T29.d — mob-count ceiling: force a corpus expected to draw more than 6 mobs across multiple
  regions in the same window; confirm `MOB_COUNT` never exceeds 6 (the adjustable-default ceiling,
  `ADS-002`/`R115`).
- T29.e — defeat: force an active mob slot, call `inf_mob_defeat`, confirm the slot's `active`
  flag clears, `MOB_COUNT` decrements, and no OAM entry is written for it on the next
  `inf_mob_render` call (no persistent corpse).
- T29.f — OAM budget static audit (Inspection): confirm the worst-case concurrent OAM entry count
  (1 player + up to 8 collectibles + 6 mobs) stays at or below 40 (`NFR-4500`).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11200 status → Implemented.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11200 row → `IP-1121`/T29.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: implemented-by pointer for
  Workflow B.
- `docs/architecture/07-data-model.md` (or WRAM quick-reference): new `COMBAT_MODE`/`MOB_COUNT`/
  `MOB_DATA` rows, `0xC6B5`–`0xC6D4`.
- Master Build Plan status row.

## 10. Definition of Done

- `inf_materialize_mobs`/`materialize_mobs` produce byte-identical, deterministic output for any
  `(SEED, row, col)` with `COMBAT_MODE` on (T29.a/b).
- `COMBAT_MODE` off reproduces today's shipped Infinite Mode exactly (T29.c).
- Mob count never exceeds 6; defeat correctly deactivates with no persistent corpse (T29.d/e).
- ROM builds at 32768 bytes; full suite passes; OAM budget confirmed within 40 entries (T29.f).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T29.a–f each present and passing.
- [ ] Direct code read: `inf_materialize_mobs`'s own presence/type draws are a distinct,
      sequential `gw_prng_step` call chain from the biome/connectivity/treasure draws — no shared
      state that would correlate mob presence with either.
- [ ] Direct code read: `COMBAT_MODE`-off path never executes any new code this package adds.
- [ ] FR-11200/RTM/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1101`/`IP-1102`** (`VERIFIED`) — `inf_ensure_window`'s existing materialization hook,
  extended not replaced.
- **`IP-1125`** — `TL_MOB`/`TL_MOB_BOT` tile indices this package's OAM writes reference.

None of this delta's own sibling packages (`IP-1120`/`1122`/`1123`/`1124`) — this is the
delta's dependency root; all four depend on it (directly or transitively), it depends on none of
them.

## 13. Risks

- **Mob-presence density constant is not yet tuned** (Medium) — this package's own draft picks a
  placeholder mask (mirroring `K=16`'s own precedent shape) subject to revision once a real
  playtesting pass judges pacing; not asserted final here, mirroring `FS-110`'s own `K=16` tuning
  precedent (`IP-1101`'s Open Question 2).
- **NFR-1500 (combat sub-mode cycle budget) is not resolved by this package** — this package's own
  new draws add to the same per-materialization cost `IP-1101`'s own five draws already impose;
  the coincident-materialization-and-combat-logic cost `R115` names is `IP-1122`'s/a future
  Analysis pass's own obligation, not measured here.
- ROM budget: a bounded routine (one presence draw, one type draw, a 30-byte table, an OAM-write
  loop) — expected modest against the 1,378-byte headroom, re-affirmed at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`worldgen.py`/`test_rom.py` changes and rebuild. `inf_ensure_window` reverts
to its pre-this-package form (the `COMBAT_MODE`-gated addition is a clean, isolated insertion, not
a rewrite of any existing branch) — the base Infinite Mode capability is completely unaffected.
No existing WRAM address is reassigned.
