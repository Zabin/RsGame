# IP-1122 — Infinite Mode Combat: Weapon Fire & Hit Resolution

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1122` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow C in full (the `act` verb for
the ranged weapon).

## 2. Objective

Implement the A-button fire input during `PLAYING` with `COMBAT_MODE` active: spawn a single-slot
transient projectile from the player's position/facing direction, move it each frame, resolve a
hit against the mob table (reusing `check_collisions`' own hitbox technique), and deactivate it
on a hit or at a terminal boundary.

## 3. Requirements Covered

FR-11300 (ranged weapon fire and hit resolution) in full.

## 4. Architecture Components

`ADS-002` §System Architecture (ranged weapon, hit-test, "A-button... no new control-scheme
invention needed") · `R115` (no hardware collision detection — software point-in-box, reusing
`check_collisions`).

## 5. Interfaces

- **`handle_play_input`/`st_playing`'s existing input-dispatch surface** — the A button is
  confirmed unbound during `PLAYING` today (direct code read, `ADS-002`); this package adds a new
  branch, not a rebinding of any button already claimed elsewhere (confirmed again by direct
  re-read of `handle_play_input` at planning time, no drift since `ADS-002`'s own check).
- **`check_collisions`' existing asymmetric point-in-box technique** (`IP-9100`/`BL-0053`,
  unchanged) — reused verbatim for the projectile-vs-mob hit-test; this package does not modify
  `check_collisions` itself, it authors a new, separate hit-test call using the same technique
  against `MOB_DATA` instead of `COLL_DATA`.
- **`IP-1121`'s `MOB_DATA`/`MOB_COUNT`/`inf_mob_defeat`** — consumed, not modified: a hit reduces
  a mob slot's own `health` field and calls `inf_mob_defeat` at zero.
- **`TL_PROJECTILE`/`TL_PROJECTILE_BOT`** (`IP-1125`, `0x0C`/`0x0D`) — the sprite tile this
  package's OAM write references.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constants** (first unclaimed bytes past `IP-1121`'s own `MOB_DATA` end, `0xC6D4`):
    `PROJ_ACTIVE = 0xC6D5` (1 byte flag), `PROJ_X = 0xC6D6` (1 byte), `PROJ_Y = 0xC6D7` (1 byte),
    `PROJ_DIR = 0xC6D8` (1 byte, 0-3 mirroring the player's own facing-direction encoding),
    `WEAPON_TIER = 0xC6D9` (1 byte, default 1, range 1-3 — see Risks for the funding-mechanism
    gap this package explicitly does not resolve).
  - **`handle_play_input`**: new branch, gated on `COMBAT_MODE != 0` and `GAMESTATE == PLAYING`:
    on A-button-just-pressed and `PROJ_ACTIVE == 0`, set `PROJ_ACTIVE=1`, `PROJ_X`/`PROJ_Y` from
    the player's current position, `PROJ_DIR` from the player's current facing direction.
  - **New subroutine `inf_projectile_update`** — called once per frame (from the existing main
    per-frame update chain, gated on `COMBAT_MODE`/`PROJ_ACTIVE`): advances `PROJ_X`/`PROJ_Y` by
    one step in `PROJ_DIR`; if the new position exits the visible window (a terminal boundary),
    clears `PROJ_ACTIVE`; otherwise calls a new `inf_projectile_hittest` subroutine.
  - **New subroutine `inf_projectile_hittest`** — iterates active `MOB_DATA` slots, applying
    `check_collisions`' own asymmetric point-in-box test between the projectile's position and
    each active mob's position; on a hit, subtracts `WEAPON_TIER` from the mob's `health` field
    (calling `inf_mob_defeat` at or below zero), clears `PROJ_ACTIVE` (the projectile stops on
    hit, does not pass through, per FR-11300's own Postcondition).
  - **`update_oam`**: extended (after `IP-1121`'s own mob-render segment) with one more OAM
    entry, gated on `PROJ_ACTIVE`, using `TL_PROJECTILE`.

## 7. Implementation Tasks

Ordered: (1) `PROJ_*`/`WEAPON_TIER` WRAM constants; (2) `handle_play_input`'s new fire branch;
(3) `inf_projectile_update`'s per-frame movement + terminal-boundary check; (4)
`inf_projectile_hittest`'s hit-test loop + `WEAPON_TIER`-scaled damage + `inf_mob_defeat` call;
(5) OAM-write extension; (6) rebuild ROM; (7) author new suite; (8) full suite run; (9)
documentation updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T30: Combat Sub-Mode — Weapon Fire & Hit Resolution`**:

- T30.a — fire spawns a projectile: force `COMBAT_MODE`/`PLAYING`, press A, confirm
  `PROJ_ACTIVE=1` at the player's own position/facing.
- T30.b — no double-fire: with `PROJ_ACTIVE` already 1, press A again, confirm no second
  projectile state change (FR-11300's own Acceptance Criterion).
- T30.c — hit resolution: force an active projectile adjacent to an active mob slot, step one
  frame, confirm the mob's `health` decreases by `WEAPON_TIER`, `PROJ_ACTIVE` clears, and (at
  zero health) `inf_mob_defeat`'s own effects are observed (T29.e's own assertions, reused).
- T30.d — miss/terminal boundary: force an active projectile with no mob in its path, step frames
  until it exits the window, confirm `PROJ_ACTIVE` clears with no mob's `health` affected.
- T30.e — `COMBAT_MODE` off: confirm the A button remains a no-op during `PLAYING` when
  `COMBAT_MODE` is 0 (non-regression against the base game's own existing free-A-button state).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11300 status → Implemented.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11300 row → `IP-1122`/T30.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: implemented-by pointer for
  Workflow C.
- `docs/architecture/07-data-model.md`: new `PROJ_*`/`WEAPON_TIER` rows, `0xC6D5`–`0xC6D9`.
- Master Build Plan status row.
- **New backlog finding** (routed via this run's harvest, not fixed here): `WEAPON_TIER`'s own
  funding mechanism — how a player actually raises it via spent treasure — has no baselined FR.
  `FR-11500` (the only baselined "economy" requirement) covers healing only; `ADS-002`'s Domain
  Model and `FR-11300`'s own Notes both reference a treasure-funded power axis that never
  received its own FR leaf. This package implements `WEAPON_TIER` as a persisted stat (fixed
  default, no player-facing way to raise it) to honor `FR-11600`'s explicit mention of "weapon
  tier" as state that persists, without inventing an ungrounded upgrade mechanic. Routed to
  `04-requirements-engineering` for a delta closing this gap.

## 10. Definition of Done

- Fire input spawns exactly one projectile at a time, moves it correctly, resolves hits against
  active mobs at `WEAPON_TIER`-scaled damage, and deactivates cleanly on hit or terminal boundary
  (T30.a–d all passing).
- `COMBAT_MODE` off leaves the A button a no-op, unchanged from today (T30.e).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T30.a–e each present and passing.
- [ ] Direct code read: the hit-test reuses `check_collisions`' own asymmetric-tolerance
      technique verbatim (same constants/approach), not a new hitbox model.
- [ ] Direct code read: `check_collisions` itself is unmodified by this package.
- [ ] FR-11300/RTM/Master-Build-Plan deltas applied exactly as §9 names; the `WEAPON_TIER`
      funding-gap finding harvested to the backlog.

## 12. Dependencies

- **`IP-1121`** — `MOB_DATA`/`MOB_COUNT`/`inf_mob_defeat`, consumed for hit resolution.
- **`IP-1125`** — `TL_PROJECTILE`/`TL_PROJECTILE_BOT` tile indices.

## 13. Risks

- **`WEAPON_TIER`'s funding mechanism is out of scope, named as a genuine requirements gap**
  (Medium) — see §9's harvested finding. This package ships a fixed-tier weapon; treating this as
  the full FR-11300/FR-11500 economy would overstate what's actually implemented.
- **NFR-1500 (cycle budget) is not confirmed by this package** — per-frame projectile
  update/hit-test adds a real, unmeasured cost on top of `IP-1121`'s own mob-materialization
  draws; a future Analysis pass (mirroring `NFR-1400`'s own direct cycle-counting methodology)
  is owed once both packages are built.
- ROM budget: a bounded routine — expected modest, re-affirmed at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `handle_play_input`'s new branch is a
clean, isolated addition (the A button's prior no-op behavior during `PLAYING` is otherwise
unmodified) — no existing input path is altered when `COMBAT_MODE` is 0.
