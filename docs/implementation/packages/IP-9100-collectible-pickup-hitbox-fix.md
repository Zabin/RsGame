# IP-9100 — Collectible Pickup Hitbox Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9100` — bug-remediation series; no FS. Source: **`BL-0053`** (Medium, project owner report,
filed via `00-intake`, this session).

## 2. Objective

Replace `check_collisions`' symmetric ±9px/±9px proximity window with a true axis-aligned
bounding-box overlap test against the player sprite's and item's real 8×16 extents, so the game
collects an item exactly when — and only when — the player's sprite visually overlaps it, per the
user's own explicit report ("The bunny collects items above the topmost edge of the sprite but
does not collect items which overlap with the bottommost edge of the sprite. The bunny should
collect and only collect items with which the sprite overlaps.").

## 3. Requirements Covered

`FR-3100` (collection-proximity detection). **This package's fix directly contradicts `FR-3100`'s
own currently-baselined Acceptance Criteria and Rationale text** ("within 10px on both axes...
two independent axis checks," `Notes` explicitly citing the `10px` threshold as a confirmed,
source-grounded fact, not merely descriptive prose) — `FR-3100` describes the *shipped* (buggy)
symmetric-window behavior as if it were the intended design, which `BL-0053`'s own direct
reproduction shows is not what a sprite-overlap-based pickup actually requires for an 8-wide/
16-tall (8×16 OBJ mode) sprite. **This package does not modify `FR-3100`'s text** (out of this
stage's own scope, per `07-implementation-planning`'s SHALL-NOT list) — it implements the corrected
behavior and flags the resulting FR/implementation divergence as a Notes-only forward pointer
(§9), mirroring `IP-9050`'s own precedent for `FR-2300`/`FR-2310` (implement the correction, cite
the FR as the closest existing statement of intent, route the actual text correction to a future
`04-requirements-engineering` delta rather than silently absorbing it here).

## 4. Architecture Components

GDS-01 §3 (Concept of Play, collection mechanic) — unaffected in shape (proximity-based pickup is
still the model); only the implementation's own threshold formula is wrong. GDS-08 confirms both
the player and every Collectible sprite use 8×16 OBJ mode (`LCDC=0x97`) — the geometric fact this
fix's corrected formula is grounded in.

## 5. Interfaces

None new. Internal fix within `check_collisions` (`asm_game.py:556-...`, X/Y overlap test at
`asm_game.py:570-578` as of this session — confirm the exact current line numbers during
authoring, since intervening packages this session may have shifted them) — no change to any WRAM
address, `COLL_DATA` layout, or GDS-09 contract.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **X-axis overlap test** (`asm_game.py:570-573`): the sprite is 8px wide (`X∈[PLAYER_X,
    PLAYER_X+7]`), and every Collectible sprite is the same width. Two same-width-8 boxes overlap
    on the X-axis iff `|PLAYER_X - item_x| < 8` (the general two-box-overlap rule, `pos1 <
    pos2+w2 AND pos2 < pos1+w1`, collapses to this symmetric form exactly because both widths are
    equal) — this is a **true zero-margin exact-overlap test**, matching the user's own explicit
    request ("collect and only collect items with which the sprite overlaps," not a forgiving
    margin). Change the X-axis comparison's threshold from `CP_n(10)` to `CP_n(8)`.
  - **Y-axis overlap test** (`asm_game.py:576-578`): the sprite is 16px tall (8×16 OBJ mode,
    `Y∈[PLAYER_Y, PLAYER_Y+15]`), and every Collectible sprite is the same height. By the identical
    reasoning, two same-height-16 boxes overlap on the Y-axis iff `|PLAYER_Y - item_y| < 16`.
    Change the Y-axis comparison's threshold from `CP_n(10)` to `CP_n(16)`.
  - **No change to the overlap-test's own structure** (the existing `SUB`/absolute-value/`CP_n`
    shape already computes `|a-b|` correctly — only the two threshold constants are wrong).
    Confirmed by this pass's own supersession sweep (TWBS): no other routine reuses these two
    constants, and no existing `T8` check depends on the old symmetric window's specific asymmetry
    (every existing pickup test places the player at the item's own exact coordinates, `dx=dy=0`).

## 7. Implementation Tasks

Ordered: (1) confirm the current exact line numbers of the X/Y overlap comparisons (drift check,
per this skill's own Step 2 discipline); (2) change the X-axis threshold `10`→`8`; (3) change the
Y-axis threshold `10`→`16`; (4) author the new boundary-exactness checks (§8); (5) rebuild ROM; (6)
full suite run, confirming existing `T8` checks are unaffected and new checks pass; (7)
documentation/traceability updates (§9).

## 8. Tests to Add

Extends the existing **`T8: Collision / Score / Carrots`** suite (`test_rom.py`) — no new suite
number, since this is a correction within an already-exercised routine, not a new capability:

- **T8.x — item just outside the sprite's true top edge is NOT collected** (the direct
  reproduction case from `BL-0053`'s own filing): synthetic item placed 5px above the sprite's
  actual top edge (`item_y = PLAYER_Y - 5`, i.e. within the old buggy ±9 window but outside the
  true `Y∈[PLAYER_Y, PLAYER_Y+15]` box) — confirm no collection event fires.
- **T8.y — item genuinely overlapping the sprite's bottom edge IS collected** (the other direct
  reproduction case): synthetic item placed at `item_y = PLAYER_Y + 14` (inside the true box, just
  short of its bottom edge, outside the old buggy ±9 window) — confirm a collection event fires.
- **T8.z — exact-boundary X/Y checks**: items placed at `dx = 7`/`dx = 8` (must collect / must not
  collect) and `dy = 15`/`dy = 16` (must collect / must not collect) — the precise off-by-one
  boundary the corrected formula's own `<` (strict) comparison implies, verifying the fix is exact,
  not merely "closer."

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: add a Notes entry to `FR-3100` recording that
  its own baselined `10px`/`10px` threshold values and Acceptance Criteria text now diverge from
  the corrected shipped behavior (`8px` X / `16px` Y, an exact-overlap AABB test against the
  sprite's real 8×16 extent) — flagged as a forward pointer to a future `04-requirements-
  engineering` delta that should correct `FR-3100`'s own text, not resolved by this package (out of
  this stage's scope).
- `docs/requirements/04-requirements-traceability-matrix.md`: update `FR-3100`'s Test cell to cite
  the new `T8.x`/`T8.y`/`T8.z` checks alongside its existing evidence.
- Master Build Plan status row.

## 10. Definition of Done

- `check_collisions`' X-axis threshold is exactly `8`; Y-axis threshold is exactly `16`.
- `T8.x`/`T8.y`/`T8.z` demonstrably pass; every existing `T8` check still passes unchanged.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct code read: X-axis comparison reads `CP_n(8)`; Y-axis comparison reads `CP_n(16)`.
- [ ] `T8.x`/`T8.y`/`T8.z` present and passing, each using a synthetic item placed via WRAM at the
      exact boundary coordinates named in §8, not an approximate position.
- [ ] `FR-3100` Notes/RTM deltas applied exactly as §9 names; `FR-3100`'s own baselined text left
      unmodified (out of this stage's scope).

## 12. Dependencies

None. Independent of every other package in-flight this session (see TWBS Sequencing summary).

## 13. Risks

- **Low.** A two-constant fix to an already-correct-in-structure overlap test; the geometric
  derivation (8×16 OBJ mode, confirmed by GDS-08) is not in dispute.
- **Requirements-baseline divergence (not a code risk):** `FR-3100`'s own text will read as
  describing behavior the shipped code no longer exhibits until a future `04` delta corrects it —
  named explicitly in §3/§9, not silently left inconsistent without a trace.
- ROM budget: none (constant-value changes only, no new bytes).

## 14. Rollback Considerations

Revert `asm_game.py`'s two threshold changes and `test_rom.py`'s new `T8.x`/`T8.y`/`T8.z` checks,
then rebuild. Reverts to the shipped (buggy — asymmetric miss/false-collect at the sprite's top/
bottom edges) behavior exactly, restoring consistency with `FR-3100`'s own currently-baselined
text; no save-format dependency, no data-corruption risk (this fix touches only in-session
collision detection, not persisted save data).
