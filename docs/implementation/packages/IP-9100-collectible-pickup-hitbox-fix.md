# IP-9100 — Collectible Pickup Hitbox Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9100` — bug-remediation series; no FS. Source: **`BL-0053`** (Medium, project owner report,
filed via `00-intake`, this session).

## 2. Objective

Replace `check_collisions`' symmetric ±9px/±9px proximity window with a true point-in-box test —
does the item's own anchor point fall inside the player sprite's real 8×16 extent — so the game
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

> **Correction (2026-07-11, discovered during `08-code-implementation`):** this section's original
> text (below, struck through in spirit) proposed a *symmetric* `|diff|<threshold` fix — keeping
> the existing abs-value `SUB`/`CPL`/`INC_A`/`CP_n` structure, just changing the two threshold
> constants to `8`/`16`. **That formula does not actually reproduce the bug's own reported
> symptoms.** Direct PyBoy verification against `BL-0053`'s own two concrete reproduction points
> (item at `item_y=75`, 5px above the sprite's top edge, must NOT collect; item at `item_y=94`,
> overlapping the sprite's bottom edge, must collect) shows the symmetric-16 formula *still*
> incorrectly collects `item_y=75` (`|80-75|=5 < 16`) — because it treats the *item* as if it also
> had a full 16px-tall box, when `BL-0053`'s own diagnosis (and the empirical fact that
> `item_y=75 < PLAYER_Y=80` alone was enough to call it "outside the true bounding box," with no
> item-height consideration) makes clear the intended model is: **the item is a collision point,
> not a second box** — pickup fires iff that point falls inside the player's own real
> `X∈[PLAYER_X,PLAYER_X+7]`, `Y∈[PLAYER_Y,PLAYER_Y+15]` box. That is an **asymmetric, one-directional
> range test** (`0 <= item_x-PLAYER_X <= 7`, `0 <= item_y-PLAYER_Y <= 15`), not a symmetric
> `|diff|<threshold` test — it needed a genuinely different (if similarly small) code shape, not
> just two different constants. The corrected version actually implemented and verified is below.

- **Modify: `asm_game.py`**:
  - **X-axis overlap test** (`asm_game.py:570-581` as implemented): replaced the symmetric
    abs-value/`CP_n(10)` test with a single unsigned-range check: `A = item_x - PLAYER_X` (computed
    fresh, via `H` as scratch for `PLAYER_X`, not the old `CPL`/`INC_A` absolute-value dance), then
    `CP_n(8)` + `JR_NC` skip. Because the subtraction is unsigned 8-bit, `item_x < PLAYER_X` wraps
    to a large value (≥`249`), which the same `CP_n(8)`/`JR_NC` check correctly rejects as "out of
    range" alongside the `item_x > PLAYER_X+7` case — one comparison covers both exclusion
    directions.
  - **Y-axis overlap test**: identical shape, `A = item_y - PLAYER_Y` (via `H` for `PLAYER_Y`),
    `CP_n(16)` + `JR_NC` skip.
  - **Register choice:** `H` (not `B`/`C`) is used as scratch — `B` is the live loop counter
    (re-read directly, not via a pop, at this same function's `COLL_COUNT-B` arithmetic further
    down) and `C` is the item's own `type` byte (read directly, not via a pop, at the `HIT` branch
    immediately below) — both must survive this block untouched. `H` is free: the loop's real `HL`
    (the `COLL_DATA` entry's own address) is already saved by this iteration's own `PUSH_HL` before
    this block runs, and not needed again until the `HIT` branch's `POP_HL`.
  - Verified directly via PyBoy against `BL-0053`'s own two reproduction points (both now correct)
    plus all four exact boundary values (`dx∈{-1,0,7,8}`, `dy∈{-1,0,15,16}`) before this package was
    called done.

## 7. Implementation Tasks

Ordered (as actually executed): (1) confirmed the current exact line numbers of the X/Y overlap
comparisons (drift check — clean, no shift); (2) implemented the originally-planned symmetric
`8`/`16` threshold change; (3) **direct PyBoy verification against `BL-0053`'s own two
reproduction points found the symmetric formula still wrong** — reverted the symmetric approach;
(4) re-derived and implemented the correct asymmetric point-in-box test (§6); (5) re-verified via
PyBoy against both reproduction points and all four exact boundary values, confirmed correct; (6)
authored the boundary-exactness checks (§8); (7) rebuilt ROM; (8) full suite run, confirming
existing `T8` checks unaffected and new checks pass; (9) documentation/traceability updates (§9).

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
- **T8.z1/T8.z2 — exact-boundary X/Y checks**: items placed at `dx = 7`/`dx = 8` (must collect /
  must not collect) and `dy = 15`/`dy = 16` (must collect / must not collect) — the precise
  off-by-one boundary the corrected formula's own inclusive-range test implies, verifying the fix
  is exact, not merely "closer."

**Supersession fix, in scope per Step 7 (a failure this package's own changes caused):**
`T11.a1` forced the player to `(20, 32)` to collect region 0's index-0 star at `(28, 40)` — an
`(dx, dy) = (8, 8)` offset that the old buggy `±9` window tolerated but the corrected exact-overlap
test (`dx` must be `<=7`) does not. Every other existing pickup test in the suite already places
the player at the item's exact coordinates (`dx=dy=0`); `T11.a1` was the sole exception, an
artifact of the old tolerance, not a deliberate proximity test. Corrected to `(28, 40)` (exact),
matching the suite's own established convention — not a weakening of this package's own fix.

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

- `check_collisions` collects an item iff `0 <= item_x-PLAYER_X <= 7` AND `0 <= item_y-PLAYER_Y <=
  15` (the item's collision point falls inside the player's real 8×16 box) — not the symmetric
  `|diff|<8`/`|diff|<16` formula originally proposed in §6 (corrected, see this section's own
  correction note above).
- `T8.x`/`T8.y`/`T8.z` demonstrably pass; every existing `T8` check still passes unchanged.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [x] G5: ROM builds at exactly 32768 bytes with valid header.
- [x] G5: full `test_rom.py` suite passes.
- [x] Direct code read: X-axis comparison reads `CP_n(8)` after an `item_x - PLAYER_X` subtraction
      (not the old abs-value shape); Y-axis comparison reads `CP_n(16)` after an
      `item_y - PLAYER_Y` subtraction.
- [x] Direct PyBoy verification (not just static read): both of `BL-0053`'s own reproduction
      points (`item_y=75` not collected, `item_y=94` collected) and all four exact boundary values
      (`dx∈{-1,0,7,8}`, `dy∈{-1,0,15,16}`) confirmed correct before this package was called done.
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
