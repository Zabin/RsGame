# IP-1120 — Infinite Mode Combat: Mode Gating & UI

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
>
> **`BLOCKED`** — pending a light `GDS-01` §4d amendment (`03-architecture-design-synthesis`),
> not a G3/user-authorization gate. See §12/§13.

## 1. Package ID

`IP-1120` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow A (the `gate` verb) — resolves
`FS-112`'s own Open Question 1.

## 2. Objective

Add a third, explicitly-labeled MODE SELECT option ("COMBAT MODE") that sets the `COMBAT_MODE`
WRAM flag `IP-1121` defines, gated so it is never enabled by default and never reachable
unintentionally.

## 3. Requirements Covered

FR-11100 (combat sub-mode entry) — the UI-gating half; the flag itself is `IP-1121`'s own scope
(see that package's §2).

## 4. Architecture Components

**Currently insufficient** — see §12/§13. Once amended: `GDS-01` §4d (target state).

## 5. Interfaces

- **The existing `GS_MODE_SELECT` state / `MM_CURSOR` cursor byte** (`FS-110`, `IP-1100`,
  unchanged today) — this package's own mechanism is **not yet decided** (mirrors `FS-112`'s own
  Open Question 1 verbatim): either (a) extend `MM_CURSOR`'s own two-state toggle to a three-state
  cycle on the existing `GS_MODE_SELECT` screen, or (b) present a new confirmation screen (a new
  `GameState`) reachable only after choosing Infinite Mode, mirroring `IP-1090`'s own
  SELECT-menu-confirmation precedent. **This planning pass does not choose between them** — see
  §12/§13, this is exactly the gap routed upstream.
- **`IP-1121`'s `COMBAT_MODE` flag** — this package's sole job, once its own mechanism is decided,
  is to set it to 1 when the player confirms the combat option, alongside `GAME_MODE=1`.

## 6. Files to Create/Modify

**Not fully specified** — pending the `GDS-01` §4d amendment. What is certain regardless of which
mechanism (a) or (b) above is chosen: `asm_game.py`'s `st_mode_select` (or a new state handler, if
(b)) writes `1` to `COMBAT_MODE` on confirmation, and nowhere else in the tree writes to
`COMBAT_MODE` except `IP-1121`'s own boot-clear. The exact `Files to Create/Modify` list (a
three-state `ms_check_a` rewrite vs. a wholly new state handler) is authored in full once the
architecture amendment lands.

## 7. Implementation Tasks

**Not fully specified** — see §6. The task list depends on which UI mechanism the `GDS-01`
amendment settles on.

## 8. Tests to Add

**Not fully specified** — see §6. Regardless of mechanism, the eventual suite must cover: (a) the
combat option is off by default for a new save; (b) confirming it sets `COMBAT_MODE=1` and it
persists (via `IP-1124`) for that save's life; (c) the base Finite/Infinite toggle's own existing
behavior (`T25`) is completely unaffected — a direct non-regression re-run of `T25` alongside
whatever new checks this package adds.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11100's UI-gating half status → Implemented
  (once built).
- `docs/architecture/01-concept-of-play.md` §4d: **not this package's own scope to edit** — the
  amendment is `03-architecture-design-synthesis`'s own act; this package's Interfaces section
  (§5) is updated to cite the landed decision once it exists.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: Open Question 1 marked
  Resolved once the amendment lands and this package is re-planned in full.
- Master Build Plan status row.

## 10. Definition of Done

**Not yet determinable** — depends on the landed `GDS-01` amendment's own shape.

## 11. Verification Checklist

- [ ] **Prerequisite, not yet met:** `GDS-01` §4d amended to name the third MODE SELECT option
      and its own mechanism (three-state cursor vs. new state).
- [ ] G5: ROM builds at exactly 32768 bytes with valid header (once built).
- [ ] G5: full `test_rom.py` suite passes (once built).
- [ ] The base Finite/Infinite toggle's own existing behavior (`T25`) is confirmed byte-for-byte
      unchanged (once built).

## 12. Dependencies

- **`IP-1121`** — the `COMBAT_MODE` flag this package sets.
- **A `GDS-01` §4d amendment** (`03-architecture-design-synthesis`) — **not another package**, an
  upstream architecture-document delta. This package cannot be planned in full (§6/§7/§8/§10) or
  marked `READY` until it lands.

## 13. Risks

- **This is the one package in the delta genuinely blocked on upstream work, not on G3
  authorization** — direct re-read of
  [GDS-01 §4d](../../architecture/01-concept-of-play.md#4d-new-game-mode-choice-finite--infinite--delta-for-bl-0113-decided-2026-07-14)
  finds it states, as a load-bearing fact, that `MODE SELECT` "presents **finite** and
  **infinite**" — a closed, two-option description that a silently-added third option would
  falsify. This mirrors `BL-0113`'s own precedent (the *original* `MODE SELECT` screen itself
  needed a `GDS-01` delta before `IP-1100` could be planned) — the same class of gap, not a new
  kind of caution. **Recommendation:** `03-architecture-design-synthesis` runs next for this
  narrow amendment (naming the third option and, if chosen, the extended cursor range or new
  state) — a small, low-risk delta given the precedent already established for `MODE SELECT`'s
  own existence, not a Vision-level or otherwise contentious decision.
- Once amended, this package's own risk profile is expected to be Low — a small, isolated UI
  extension with no new game-logic surface beyond setting one existing flag.

## 14. Rollback Considerations

**Not yet determinable** — no code exists yet.
