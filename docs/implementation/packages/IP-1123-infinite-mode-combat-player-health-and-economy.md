# IP-1123 — Infinite Mode Combat: Player Health, Setback & Healing Economy

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1123` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow D in full (the `act`/`render`
verbs for player health, and the `persist`-adjacent healing economy).

## 2. Objective

Track player health, display it via the existing heart-tile HUD, reduce it on mob contact,
trigger a non-lethal setback at zero, and implement the treasure-spend healing economy that
decrements `RUNNING_TREASURE_COUNT`.

## 3. Requirements Covered

FR-11400 (player health and non-lethal setback), FR-11500 (treasure-spent healing economy) — both
in full.

## 4. Architecture Components

`ADS-002` §Domain Model (`PlayerHealth`), §System Architecture ("Health HUD") · `R218`
(heart-container HUD convention) · user decisions 2026-07-17 (non-lethal setback; treasure is
*spent*, not merely triggering).

## 5. Interfaces

- **`TL_HEART_FULL`/`TL_HEART_EMPTY`** (`tiles.py`, `0x11`/`0x12`, already shipped) — reused
  verbatim, zero new tile-art cost.
- **`RUNNING_TREASURE_COUNT`** (`0xC405`, `FS-110`'s own existing field, unchanged) — this
  package's healing spend decrements it directly; no second ledger. This package does not modify
  `RUNNING_TREASURE_COUNT`'s own win/high-score read path (`inf_check_top_score`, `IP-1103`) —
  that subroutine still reads whatever value remains after any spend.
- **`IP-1121`'s `MOB_DATA`/`MOB_COUNT`** — consumed for mob-contact detection (a position-overlap
  test between the player and any active mob, reusing `check_collisions`' own technique, a
  distinct call site from `IP-1122`'s own projectile-vs-mob hit-test).
- **A new HUD write region** — row 1 of the tilemap (VRAM `0x9820`–`0x9822`, the three cells
  immediately below the existing row-0 score bar), a `07`-level placement choice (`FS-112`'s own
  §9 left this undecided, mirroring `ADR-0015`'s precedent of leaving equally-valid
  byte/placement choices to this stage) — visible only when `COMBAT_MODE` is active, so the base
  game's own screen composition is completely unaffected when it is not.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constant** (first unclaimed byte past `IP-1122`'s own `WEAPON_TIER` end,
    `0xC6D9`): `PLAYER_HEALTH = 0xC6DA` (1 byte, default/max 3 — three heart cells, mirroring the
    heart-container convention `R218` grounds; a fixed max, not itself an upgrade axis this
    package invents).
  - **New subroutine `inf_mob_contact_check`** — called once per frame (gated on `COMBAT_MODE`),
    tests the player's position against each active `MOB_DATA` slot (reusing `check_collisions`'
    own asymmetric point-in-box technique, a separate call site from `IP-1122`'s projectile
    hit-test); on contact, decrements `PLAYER_HEALTH` by 1 (a fixed per-contact cost, not
    per-mob-type-scaled — `FS-112` does not specify per-type damage variation, so none is
    invented here).
  - **New subroutine `inf_health_setback`** — called when `PLAYER_HEALTH` reaches 0: restores
    `PLAYER_HEALTH` to its own max, returns the player to the position they entered the current
    region at (a WRAM-held "region entry position," a new 2-byte field this package also claims
    — see below), and does **not** change `GAMESTATE` (stays `PLAYING`, per FR-11400's own
    Postcondition — no game-over state exists to transition to).
  - **New WRAM constant**: `COMBAT_ENTRY_X`/`COMBAT_ENTRY_Y` (2×1 bytes, `0xC6DB`/`0xC6DC`) —
    recorded on every region-entry event (gated on `COMBAT_MODE`) as the setback's own return
    point.
  - **New subroutine `inf_heal_spend`** — called on a new heal-spend input (mirrors `ADS-002`'s
    own framing: a player *choice*, not automatic) gated on `COMBAT_MODE` and
    `RUNNING_TREASURE_COUNT > 0`: decrements `RUNNING_TREASURE_COUNT` by a fixed spend unit (e.g.
    1), increments `PLAYER_HEALTH` by a fixed heal amount (e.g. 1, capped at max) — the exact
    input binding for this action is an Open Question this package inherits from `FS-112` §19
    Open Question 3's own sibling gap (no fire-input-equivalent free button is named for it in
    `ADS-002`); **named here as a real, unresolved gap**, not invented — see Risks.
  - **New subroutine `inf_health_hud_draw`** — called from the existing HUD-update chain
    (mirrors `update_status_disp`'s own trigger, gated on `COMBAT_MODE`): writes `TL_HEART_FULL`/
    `TL_HEART_EMPTY` across the three row-1 cells according to `PLAYER_HEALTH`'s current value.

## 7. Implementation Tasks

Ordered: (1) `PLAYER_HEALTH`/`COMBAT_ENTRY_X`/`COMBAT_ENTRY_Y` WRAM constants; (2)
`inf_mob_contact_check`'s per-frame contact test + health decrement; (3) `inf_health_setback`'s
restore-and-reposition logic; (4) region-entry-position recording hook; (5) `inf_heal_spend`
(input binding deferred pending Risk resolution — implemented against a placeholder input,
flagged); (6) `inf_health_hud_draw`'s row-1 write; (7) rebuild ROM; (8) author new suite; (9) full
suite run; (10) documentation updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T31: Combat Sub-Mode — Player Health & Economy`**:

- T31.a — mob contact reduces health: force the player onto an active mob's position, step one
  frame, confirm `PLAYER_HEALTH` decreases by exactly 1.
- T31.b — HUD reflects health: force `PLAYER_HEALTH` to each of 0-3, confirm the row-1 heart
  cells render the matching full/empty pattern.
- T31.c — zero-health setback: force `PLAYER_HEALTH` to 0, step one frame, confirm
  `PLAYER_HEALTH` resets to max, the player's position returns to the recorded region-entry point,
  and `GAMESTATE` remains `PLAYING` (never transitions to any other state).
- T31.d — heal-spend decrements the shared count: force a known `RUNNING_TREASURE_COUNT`, trigger
  `inf_heal_spend`, confirm the exact decrement and the corresponding `PLAYER_HEALTH` increase
  (capped at max).
- T31.e — heal-spend at zero treasure is a no-op: force `RUNNING_TREASURE_COUNT=0`, trigger
  `inf_heal_spend`, confirm no change to either field.
- T31.f — `COMBAT_MODE` off: confirm no row-1 HUD write occurs and mob-contact/heal-spend logic
  never executes when `COMBAT_MODE` is 0 (non-regression against the base game's own row-0-only
  HUD).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11400/FR-11500 status → Implemented.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11400/FR-11500 rows →
  `IP-1123`/T31.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: implemented-by pointer for
  Workflow D; §19 Open Question 3 (no-op heal-spend feedback) — a silent no-op is what this
  package ships (T31.e); a richer cue remains open, not resolved here.
- `docs/architecture/07-data-model.md`: new `PLAYER_HEALTH`/`COMBAT_ENTRY_X`/`COMBAT_ENTRY_Y`
  rows, `0xC6DA`–`0xC6DC`.
- Master Build Plan status row.
- **New backlog finding** (harvested, not fixed here): the heal-spend action's own input binding
  has no free button named by `ADS-002`/`FS-112` — every existing button is already claimed
  (D-pad movement, A now claimed by `IP-1122`'s fire input, B is the universal cancel, START/
  SELECT both claimed by existing menus). This package implements the subroutine against a
  placeholder call site (not wired to any real input) pending a decision — a genuine gap for
  `06-feature-specification`/`03-architecture-design-synthesis` to resolve (a new button
  combination, a menu-based spend, or reusing an existing button contextually), not invented
  here.

## 10. Definition of Done

- Mob contact reduces health correctly and the HUD reflects it; zero health triggers the
  setback without a `GAMESTATE` change; heal-spend correctly decrements the shared treasure count
  and increases health, capped at max; a zero-treasure spend is a clean no-op (T31.a–e all
  passing).
- `COMBAT_MODE` off leaves the base game's HUD/mob-contact/heal-spend logic entirely inert
  (T31.f).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T31.a–f each present and passing.
- [ ] Direct code read: `inf_heal_spend` decrements `RUNNING_TREASURE_COUNT` directly — no second,
      independent counter exists anywhere in this package's own new WRAM (FR-11500's own
      Acceptance Criterion, "no separate ledger exists").
- [ ] Direct code read: `inf_health_setback` never writes `GAMESTATE`.
- [ ] FR-11400/FR-11500/RTM/Master-Build-Plan deltas applied exactly as §9 names; both harvested
      findings (heal-spend input binding, heal-spend feedback) recorded in the backlog.

## 12. Dependencies

- **`IP-1121`** — `MOB_DATA`/`MOB_COUNT`, consumed for contact detection.

## 13. Risks

- **The heal-spend action's input binding is a genuine, unresolved gap** (Medium-High) — every
  existing free button is already claimed by the time this package is authored (see §9's
  harvested finding). This package's own Definition of Done is satisfiable via direct WRAM/
  subroutine forcing (T31.d/e), but the *player-reachable* path to trigger a heal-spend does not
  exist until this gap resolves — named explicitly, not silently assumed away.
- **Per-contact damage is a fixed constant (1), not scaled by mob type** — `FS-112` does not
  specify per-type damage, so this package does not invent it; a future delta could add this
  without breaking this package's own Definition of Done.
- ROM budget: a bounded set of routines and one new HUD-write call — expected modest, re-affirmed
  at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. The row-1 HUD write and all new
subroutines are gated on `COMBAT_MODE` — reverting leaves the base game's own row-0-only HUD and
`RUNNING_TREASURE_COUNT`'s existing win-condition read path completely unaffected.
