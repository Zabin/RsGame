# IP-9140 — Right-Arrow Off-Screen Position Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9140` — bug-remediation series; no FS. Source: **`BL-0084`** (High, project owner report,
filed via `00-intake`, this session).

## 2. Objective

Make the right-edge navigation arrow actually visible. `draw_region_arrows`'s `ARROW_ADDR_R`
constant places it at tilemap column 30 — outside the 20-column-wide visible background window
(`SCX=0` always, confirmed empirically), so it has never rendered on any screen, on any build,
since before this pipeline's own work began (traced to the pre-procgen `_zone_arrows`, which used
the full 32-tile tilemap width instead of the 20-tile visible width). `IP-1030`'s runtime port
preserved this defect faithfully (its own stated goal was matching the shipped placement exactly),
and no existing test ever checked screen-window visibility, only the tilemap byte value at the
address — the gap this package's own new test closes. A one-constant change, no algorithm change.

## 3. Requirements Covered

No FR/NFR text change — `FR-2320`'s existing "open-edge indicator renders" language is correct;
the shipped *implementation* placed one of the four indicators off-screen. `FR-2320`'s Notes gain
an entry recording this defect and its fix.

## 4. Architecture Components

No architecture decision needed — a screen-position constant bug, not a design question. Does not
revisit `IP-1030`'s own `draw_region_arrows` design (GDS-09) or `IP-1080`'s classification logic
(`FR-2330`), both of which are unaffected — confirmed by this package's own investigation (a full
DFS-driven traversal via real button input across five `(seed,scale)` combinations found zero
discrepancies in `IP-1080`'s classification decisions).

## 5. Interfaces

None new. `draw_region_arrows`'s own interface (reads `REGION_GRAPH`'s four neighbor bytes via
`HL`, writes to four fixed VRAM tilemap addresses) is unchanged — only the RIGHT arrow's own
target address.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`draw_region_arrows`** (`ARROW_ADDR_R` constant, `asm_game.py` — confirm exact line during
    authoring, drift check). Change
    `ARROW_ADDR_R = 0x9800 + 9*32 + (32-2)` to `ARROW_ADDR_R = 0x9800 + 9*32 + (20-2)` — the right
    arrow now targets tilemap column 18, one tile in from the visible window's own right edge
    (column 19), mirroring `ARROW_ADDR_L`'s already-correct column-1 margin from the left edge
    (column 0) symmetrically. `ARROW_ADDR_U`/`ARROW_ADDR_D`/`ARROW_ADDR_L` are already within the
    visible 0–19/0–17 range — confirmed by direct calculation, no change needed.
  - Nothing else in `asm_game.py` — confirmed by direct grep: `ARROW_ADDR_R` has exactly one
    definition site and one consumer (`_arrow_write(ARROW_ADDR_R, TL_ARROW_R)` inside
    `draw_region_arrows` itself); no other routine references it.
- **Modify: `test_rom.py`**: add a genuine screen-visibility regression check (§8) — the class of
  test missing that let this ship undetected across every prior verification pass.

## 7. Implementation Tasks

Ordered: (1) confirm `ARROW_ADDR_R`'s exact current definition (drift check); (2) change the
column offset `(32-2)`→`(20-2)`; (3) author the new visibility regression check (§8); (4) rebuild
ROM, run the full suite — confirm `T13.*`/`T19.*`/`T20.*` all continue to pass unchanged (a
byte-value check at the corrected address should still find the right value; the *new* check adds
the visibility assertion none of them performed); (5) re-confirm via direct PyBoy screenshot that
the right arrow is now visually present at a region with a live right-neighbor; (6)
documentation/traceability updates (§9).

## 8. Tests to Add

Extends the existing **`T13: Generated-Region Screen Composition`** suite (`test_rom.py`) — no
new suite number, placed immediately after `T13.c` (the arrow-placement regression check) it
directly corrects:

- **T13.d — Screen-visibility audit (the direct `BL-0084` regression test).** For each of the
  four arrow addresses (`ARROW_ADDR_U/D/L/R`), asserts the tilemap column/row is within the true
  visible background window — column `0`–`19`, row `0`–`17` (the fixed 160×144px/20×18-tile GBC
  display, `SCX=SCY=0` always in this codebase, confirmed by direct code read: `asm_game.py` never
  writes either register). This is the check that would have caught `BL-0084` before it shipped —
  a tilemap-byte-value check alone (`T13.c`'s own existing method) cannot distinguish a correctly
  written but off-screen tile from a correctly written and visible one.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: add a Notes entry to `FR-2320` recording this
  defect (citing `BL-0084`) and its fix — the requirement's own text was never wrong, the shipped
  tile-position constant was.
- `docs/requirements/04-requirements-traceability-matrix.md`: update `FR-2320`'s Test cell to cite
  the new `T13.d` check and this package.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- `ARROW_ADDR_R` targets tilemap column 18 (visible), not column 30 (off-screen).
- `T13.d` demonstrably passes — all four arrow addresses confirmed within the true visible window.
- Every existing check that touches arrow tiles/positions still passes unchanged.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct code read: `ARROW_ADDR_R` reads `0x9800 + 9*32 + (20-2)` (column 18), not the old
      column 30.
- [ ] `T13.d` present and passing, confirmed by direct read of the test's own implementation.
- [ ] Direct PyBoy screenshot re-check (ad hoc, mirroring `BL-0084`'s own reproduction method): a
      region with a confirmed-open right neighbor visibly shows the right arrow.
- [ ] `T13.a`/`T13.b`/`T13.c`/every `T19`/`T20` check that touches arrow tiles still passes,
      confirming no regression from this fix itself.
- [ ] Requirements/RTM deltas applied exactly as §9 names.

## 12. Dependencies

None functionally — `draw_region_arrows` has no upstream dependency beyond `IP-1030`'s own
`VERIFIED` baseline and `IP-1080`'s own `COMPLETE` classification extension (this package's diff
is disjoint from `IP-1080`'s own row/col re-derivation code — different lines, no merge risk).

## 13. Risks

- **Very low.** A single constant-offset change (one component of one address), zero ROM-size
  impact, zero WRAM impact.
- **Severity of the defect being fixed is High** (a core, always-broken navigation affordance
  affecting literally every screen with a right-neighbor) — worth shipping promptly rather than
  queuing behind lower-severity work, but not Critical (movement itself is unaffected; only the
  visual cue is missing).

## 14. Rollback Considerations

Revert `asm_game.py`'s `ARROW_ADDR_R` change and remove `T13.d`, then rebuild. Reverts to the
current (long-standing) regressed state — not a save-compatibility-relevant rollback (no WRAM/SRAM
layout change, no `SAVE_VERSION_VAL` bump).
