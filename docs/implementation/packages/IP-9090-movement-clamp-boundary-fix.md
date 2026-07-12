# IP-9090 — Movement Clamp Boundary Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9090` — bug-remediation series; no FS. Source: **`BL-0051`**/**`BL-0052`** (both filed via
`00-intake`, this session).

## 2. Objective

Correct `handle_play_input`'s UP and RIGHT movement-clamp magic bounds so both match the pattern
their own already-correct DOWN/LEFT siblings already establish — the player currently stops
several pixels short of the true playfield edge in both directions, a real, constantly-visible
movement-feel defect.

## 3. Requirements Covered

`FR-2100` (continuous fixed-speed movement while held) — this package fixes a regression in the
shipped implementation's own boundary behavior, not the requirement text. **No baselined FR
explicitly states the exact playfield-edge pixel bounds** (`FR-2100`'s own Postconditions say only
"advances... until released or blocked," `FR-2310` governs zone-boundary/transition blocking, not
intra-screen pixel clamping) — this is a genuine requirements-baseline gap, not invented or
silently assumed here; noted for `04-requirements-engineering` as a candidate Notes addition (a
Data Model-level pixel-value detail, consistent with `FR-2100`'s own Notes field already deferring
per-frame speed the same way), not blocking this remediation.

## 4. Architecture Components

GDS-01 (Concept of Play, player-altitude movement) — unaffected in shape, only the implementation's
own boundary constants are wrong. No ADR governs the exact pixel values (they derive from screen
geometry — HUD row height and sprite dimensions — not a binding design decision).

## 5. Interfaces

None new. Internal fix within `handle_play_input` (`asm_game.py:495-554`) — no change to any WRAM
address, GDS-09 contract, or the movement input-handling entry point `IP-1010`'s original shipped
code established.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **UP clamp** (`asm_game.py:531-536`): the current comparison (`CP_n(17)`, skip-if-carry-or-zero)
    clamps the floor at `Y=17`. The correct floor is `Y=8` — one 8px tile row below the static
    row-0 HUD (GDS-08's own confirmed HUD height), the same geometric-derivation logic the DOWN
    clamp's own `129` bound already uses (screen height 144, sprite height 16, ceiling
    `144-16=128`, compared via `INC_A(); CP_n(129); JR_NC skip`). Change the UP clamp's magic bound
    from `17` to `8`, preserving the existing comparison structure (`CP_n(8)`, same `JR_C`/`JR_Z`
    skip-logic shape) so the floor becomes `8` instead of `17`.
  - **RIGHT clamp** (`asm_game.py:513-517`): the current comparison (`CP_n(160)`) allows the
    written maximum to reach `159` (screen width 160, sprite width 8, true ceiling `160-8=152` —
    matching the LEFT clamp's own already-correct `X>=0` floor, which is derived from the same
    8px-sprite-width geometry). Change the RIGHT clamp's comparison from `CP_n(160)` to
    `CP_n(153)` (skip-if-`A>=153`, i.e. skip once the incremented value would reach `153`), capping
    the written maximum at `152`.
  - No other clamp in `handle_play_input` changes — DOWN (`129`) and LEFT (`X>0` check) are
    already correct by this package's own analysis and this pass's supersession sweep (TWBS,
    "Movement/pickup/UI bug-remediation tranche").

- **Modify: `test_rom.py`** (supersession-sweep finding, in scope per this package — see TWBS):
  - **`T7.8`** (`test_rom.py:477-482`): currently asserts the player **cannot** move above `Y=17`
    — this is the pre-fix buggy floor asserted as if correct. Update the assertion to confirm the
    player **can** reach the corrected floor (`Y=8`) and **cannot** go below it, and correct the
    check's own name/comment (it no longer has anything to do with "zone 0, no up-transition" —
    the floor is a pure geometric constant independent of zone/region).
  - **`T7.10`**: the check's own numeric assertion (`x<=159`) does not break (it forces `X=159`
    directly, bypassing the clamp, then only checks "no further increase" — still true against the
    new `152` ceiling), but its comment ("X capped at 159") is now factually wrong. Correct the
    comment to state the real cap (`152`), and add a new check that reaches the ceiling via genuine
    clamp-driven movement (not a forced WRAM value) to directly verify the corrected boundary.

## 7. Implementation Tasks

Ordered: (1) change the UP clamp's magic bound `17`→`8`; (2) change the RIGHT clamp's comparison
`CP_n(160)`→`CP_n(153)`; (3) update `T7.8`'s assertion and comment to the corrected floor; (4)
correct `T7.10`'s stale comment and add a genuine-movement boundary check; (5) rebuild ROM; (6)
full suite run, confirming both new/corrected checks pass and nothing else regresses; (7)
documentation/traceability updates (§9).

## 8. Tests to Add

Extends the existing **`T7: Joypad / Movement`** suite (`test_rom.py`) — no new suite number:

- **T7.8 (corrected):** from a safe mid-playfield position, hold UP long enough to reach the
  clamp; confirm `PLAYER_Y` settles at exactly `8`, not `17`, and does not go below `8` with
  continued UP input.
- **T7.10 (corrected comment) + new T7.10b:** drive `PLAYER_X` to the RIGHT clamp via genuine
  movement input (not a forced WRAM value) from a safe starting position; confirm it settles at
  exactly `152`, not `159` or `160`, and does not exceed `152` with continued RIGHT input.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: add a Notes entry to `FR-2100` recording the
  corrected boundary values (`Y` floor `8`, `X` ceiling `152`) and flagging the requirements-baseline
  gap named in §3 (no FR states the exact pixel bounds) as a candidate future `04` addition, citing
  `BL-0051`/`BL-0052`.
- `docs/requirements/04-requirements-traceability-matrix.md`: update `FR-2100`'s Test cell to cite
  `T7.8`/`T7.10`/`T7.10b`.
- Master Build Plan status row.

## 10. Definition of Done

- UP clamp floor is exactly `Y=8`; RIGHT clamp ceiling is exactly `X=152`.
- DOWN (`Y=128`) and LEFT (`X=0`) clamps unchanged.
- `T7.8`/`T7.10`/`T7.10b` demonstrably pass; no other suite regresses.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct code read: UP clamp's magic bound reads `8`, not `17`; RIGHT clamp's comparison reads
      `CP_n(153)`, not `CP_n(160)`.
- [ ] Direct code read: DOWN/LEFT clamps byte-for-byte unchanged.
- [ ] `T7.8`/`T7.10`/new `T7.10b` present and passing, and each exercises the boundary via genuine
      movement input, not only a forced WRAM value.
- [ ] Requirements/RTM deltas applied exactly as §9 names.

## 12. Dependencies

None. Independent of every other package in-flight this session (the maze-shaped-adjacency
thread, the five packages awaiting fresh-session verification, and `IP-9100`/`IP-9080` — see TWBS
Sequencing summary).

## 13. Risks

- **Low.** A two-constant fix in an already-simple, already-correct-in-structure routine; the
  geometric derivation (HUD height, sprite dimensions) is not in dispute, only the two stale
  literals.
- ROM budget: none (constant-value changes only, no new bytes).
- Test-conflict risk: **already identified and folded into this package's own scope** (`T7.8`'s
  stale assertion) — not a residual risk, a named task (§6/§8).

## 14. Rollback Considerations

Revert `asm_game.py`'s two clamp-constant changes and `test_rom.py`'s `T7.8`/`T7.10` edits, then
rebuild. Reverts to the shipped (buggy — player stops short of the true playfield edge in two
directions) behavior exactly; no save-format dependency, no data-corruption risk (this fix touches
only in-session movement clamping, not persisted save data).
