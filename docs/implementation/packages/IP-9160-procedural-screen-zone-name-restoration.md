# IP-9160 — Procedural-Screen Zone-Name Restoration (`BL-0138`)

> Owned by `07-implementation-planning` (definition) / `08-content-authoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9160` — remediation package for [`BL-0138`](../../pipeline/backlog.md) (Medium,
`09-content-review` finding 1, [content-review-nine-biome-family-delta.md](../../reviews/content-review-nine-biome-family-delta.md)):
the four procedurally-filled screens (Village/Cave/Desert/Plains, `ADR-0020`/`IP-1022`) display
the *previous* screen's zone name in the row-0 HUD, because the on-device fill starts at row 1
and never writes the name the Python `*_screen()` oracles put at row 0. No FS — a rendered-content
defect against `FS-103`'s existing acceptance intent, not new behavior.

## 2. Objective

Every visit to a Village/Cave/Desert/Plains screen shows that screen's own zone name in the HUD
("VILLAGE"/"CAVE"/"DESERT"/"PLAINS"), exactly as the corresponding Python `*_screen()` function's
own row 0 renders it — using the already-shipped landmark-overlay mechanism, no new code.

## 3. Requirements Covered

`FR-4320` (nine biome-family identities — completes the *presentation* fidelity of the four
newly-folded identities' screens; the RTM row already lists this package's siblings) and
`FS-103`'s screen-composition acceptance intent (each screen renders as its own `*_screen()`
oracle describes — the row-0 name is part of that oracle's output).

## 4. Architecture Components

`ADR-0020` (the procedural-fill + landmark-overlay decision this package operates inside — the
landmark-overlay list format is the delivery vehicle; no new mechanism, no ADR change).
`GDS-08` §5 (row-0 static HUD composition — the name region is static per-screen content; the
score/carrot digits are the only live cells, redrawn by `update_status_disp`).

## 5. Interfaces

- **The landmark-overlay list format** (`(tile_x, tile_y, tile_id, attr)`, 1-byte count prefix,
  `IP-1022`/`ADR-0020`) — **unchanged**: `apply_landmark_overlay` already writes any `(x, y)`
  including row 0 (`asm_game.py`: `HL = 0x9800 + tile_y*32 + tile_x`, no row filter — confirmed
  by direct read). This package only *appends entries* to the four existing `*_LANDMARKS` lists.
- **`build_rom.py`'s landmark emission loop** — unchanged: it emits `len(lm)` and the tuple
  stream generically; longer lists need zero build-side change (count stays well under the
  1-byte prefix's 255 ceiling: current counts 24/12/22/25, +8 each).
- **`update_status_disp`** (`asm_game.py`) — untouched; it redraws only the live digit cells,
  which this package's name cells must not overlap (see §6's dynamic-cell inventory task).

## 6. Files to Create/Modify

- **Modify: `tilemaps.py`** (data half — the owning peer's surface):
  - Append each screen's **name-region row-0 cells** to `VILLAGE_LANDMARKS`/`CAVE_LANDMARKS`/
    `DESERT_LANDMARKS`/`PLAINS_LANDMARKS`: entries `(x, 0, tile_id, attr)` for the columns the
    name region spans, **derived mechanically from that screen's own `*_screen()` oracle row 0**
    (the `_score_bar(t, a, "VILLAGE")` call renders the name at col 12, attr 2, via `_str` —
    confirmed by direct read of `tilemaps.py:39-51`), not hand-picked. Cover the full fixed-width
    name region (col 12 through the longest name's extent, 8 cells — "MOUNTAIN" is the shipped
    maximum) so a shorter name (e.g. "CAVE") also *overwrites the leftover tail* of any longer
    previous name with the oracle's own base-tile cells — the exact stale-tail scenario the
    review screenshots show. State the derivation in the data comment (the existing `*_LANDMARKS`
    comment block's "derived by direct per-cell diff" description must be extended to note the
    row-0 name cells and their different derivation basis, since row 0 has no base-fill formula).
  - No change to any `*_FILL` tuple, any `*_screen()` function, `ZONE_COLLECTS`, or
    `ALL_SCREENS`.
- **Modify: `test_rom.py`** (the checks that verify this content, the content peer's own test
  surface):
  - **`T13.e`**: narrow the exclusion from "all of row 0" (the current `range(1, 18)` read) to
    **row 0 included, minus exactly the live dynamic cells** — inventory those cells at
    implementation time by direct read of *every* row-0 writer (`_score_bar`'s own digit
    placeholders, `update_status_disp`'s carrot-count/score cells, and any other row-0 writer a
    grep for `0x980` reveals) rather than assuming; the arrow-position exclusion set stays as-is.
    After this package, the parity check proves the name region byte-identical to each oracle.
  - **New check (`T13.g`)**: stale-name regression test — render one of the four screens *after*
    a different named screen (e.g. force Grass/Forest, then force Village), and assert the name
    region's tiles equal the second screen's own oracle row-0 cells (the direct regression
    `BL-0138`'s screenshots demonstrate; a fresh-boot-only parity pass would miss the stale-tail
    case if the first-drawn screen happened to be one of the four).
- **No change to `asm_game.py`/`build_rom.py`/`worldgen.py`** — confirmed by direct read that
  the existing applier and emission loop handle the extended lists unchanged. If implementation
  finds otherwise (e.g. an applier row filter this planning read missed), that is drift →
  Blocking Report, not an in-package code edit (the code halves belong to
  `08-code-implementation`).

## 7. Implementation Tasks

Ordered: (1) confirm the §5/§6 direct-read claims still hold (applier writes row 0 unfiltered;
emission generic; name at col 12/attr 2); (2) derive each screen's name-region cells from its own
oracle row 0 (mechanical, per §6); (3) append the entries to the four lists + extend the data
comment; (4) inventory row-0 dynamic cells by direct read of every row-0 writer; (5) narrow
`T13.e`'s exclusion accordingly and extend its comparison to row 0; (6) add the `T13.g`
stale-name regression check; (7) rebuild, confirm byte budget (≈128 bytes: 8 cells × 4 bytes ×
4 screens; data-section growth only — no code-section alignment shift expected, but re-measure);
(8) full suite; (9) documentation/traceability updates (§9).

## 8. Tests to Add

- **`T13.e` (extended)** — oracle parity now covering row 0's static cells (name region
  included), minus the inventoried dynamic digit cells; all four screens.
- **New `T13.g`** — stale-name regression: screen B rendered after differently-named screen A
  shows B's own name region, for at least one of the four new screens (and the reverse
  direction: a baked screen rendered after a procedural one also shows its own name — the baked
  path's `copy_screen` already rewrites all of row 0, so this direction documents the asymmetry
  is closed from both sides).

## 9. Documentation Updates

- `docs/pipeline/backlog.md`: `BL-0138` → resolution note (manager flips status on harvest).
- `docs/reviews/content-review-nine-biome-family-delta.md` is **not** edited (review reports are
  immutable records; the finding's closure lives in the backlog and this package's own trail).
- RTM `FR-4320` row: add this package alongside `IP-1022`/`IP-1033` once shipped.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Each of the four procedurally-filled screens displays its own zone name after every redraw,
  including immediately after a differently-named screen was displayed (the stale-tail case).
- `T13.e`'s parity comparison includes row 0's static cells and passes byte-for-byte for all
  four screens.
- `T13.g` passes in both directions (procedural-after-baked and baked-after-procedural).
- ROM builds at exactly 32768 bytes; full suite passes.
- Diff scope: `tilemaps.py` data + `test_rom.py` only.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] `T13.e` (extended to row 0) passes for all four screens — the name region is
      byte-identical to each oracle.
- [ ] `T13.g` stale-name regression passes both directions.
- [ ] Live rendered evidence: re-drive at least one of the four screens after a differently-named
      screen and screenshot the corrected name (the exact scenario the review screenshots show
      failing).
- [ ] Diff scope confirmed: no `asm_game.py`/`build_rom.py`/`worldgen.py` change; no `*_FILL`/
      `*_screen()`/`ZONE_COLLECTS`/`ALL_SCREENS` change.
- [ ] Byte-budget delta recorded (≈128 bytes expected, data section).

## 12. Dependencies

- **`IP-1022`** (`VERIFIED`) — the landmark-overlay mechanism and the four lists this package
  extends.
- **`IP-1033`** (`VERIFIED`) — co-resident `tilemaps.py` content, not modified here.
- No open package's Files-to-Modify overlaps (`IP-1106`/`IP-1111` are `COMPLETE`, touching
  `worldgen.py`/`asm_game.py`/`build_rom.py` — disjoint from this package's `tilemaps.py` data +
  `test_rom.py` surface).

## 13. Risks

Low. The mechanism is shipped and `VERIFIED` (`apply_landmark_overlay`); the data is a mechanical
derivation from already-shipped oracle content (the same derivation class `IP-1022`'s landmark
lists used, with the same oracle-parity safety net — now extended to actually cover the cells in
question). ROM budget: ≈128 data bytes against 354 headroom; data-section growth should not move
the code-section alignment boundary (re-measure at implementation — a surprise 256-byte alignment
shift would still fit but must be recorded). One planning-level note: this package deliberately
routes to `08-content-authoring` (pure data + its verifying tests) — the seam question `BL-0135`
raised for `IP-1022` does not arise here because no `asm_game.py` change is needed.

## 14. Rollback Considerations

Remove the appended name-region entries from the four lists, restore `T13.e`'s original row-0
exclusion, remove `T13.g`, rebuild. No save-format, WRAM, or interface dependency — pure
ROM-resident data + tests.
