# IP-9150 — Tile-Data Padding Trim

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9150` — bug-remediation/hygiene series; no FS. Source: **`BL-0134`** (High, found by
`09-package-verification`'s own `08-code-implementation` attempt at `IP-1022`, this session,
2026-07-17) — this package is the one safe, mechanical recovery `BL-0134`'s own ROM-budget
analysis found; it does not itself resolve `BL-0134`'s larger residual shortfall.

## 2. Objective

Recover ROM headroom that is currently pure waste: `tiles.py`'s `build_tile_data()` allocates a
fixed 256-tile (4,096-byte) array regardless of how many tile slots are actually populated. Direct
scan of every `TL_*` constant finds the highest in use is `TL_TORCH = 0xB5` (181) — only 182 of
256 slots are ever written; the remaining 74 slots (182–255) are zero-padding shipped in every
build today, unrelated to and pre-dating `IP-1022`'s own attempted work. Trimming the emitted
range (and the boot-time copy count that must match it) recovers this space with zero behavior
change.

## 3. Requirements Covered

None directly — no FR/NFR describes tile-data size; this is a pure ROM-budget hygiene fix.
`NFR-4000`'s existing "32768-byte single-bank budget, headroom re-affirmed per `BL-0019`'s
standing convention" gains a Notes entry citing the recovered headroom.

## 4. Architecture Components

No architecture decision needed — a data-size reduction with no format/interface change.
[GDS-07](../../architecture/07-data-model.md) §3 (tile-index map) is unaffected: every existing
`TL_*` index (0–181) keeps its exact same value and meaning; only indices 182–255, which no code
anywhere addresses, stop being copied.

## 5. Interfaces

- **`build_tile_data()`** (`tiles.py`) — return-value length shrinks from `256*16=4096` bytes to
  a rounded boundary above the highest used index (see §6); every existing caller (`build_rom.py`'s
  single `for b in build_tile_data(): rom.emit(b)` site) is unaffected — it just emits fewer bytes.
- **The boot-time tile-copy DMA** (`asm_game.py:358-360`) — the hardcoded `LD_BC_nn(256 * 16)`
  byte count shrinks to match `build_tile_data()`'s new length exactly. No new patch key, no new
  WRAM/SRAM address — a pure literal-constant change on both ends of one existing copy.

## 6. Files to Create/Modify

- **Modify: `tiles.py`**:
  - `build_tile_data()` (`tiles.py:924-925`): change `data = bytearray(256 * 16)` to
    `data = bytearray(TILE_DATA_TILES * 16)`, where `TILE_DATA_TILES` is a new module-level
    constant set to **184** (the highest used index, 181, rounded up to a clean multiple-of-8
    boundary for a small safety margin against the next tile added without needing this trim
    revisited immediately) — recovers `(256-184)*16 = 1,152` bytes.
  - Add an assertion immediately after the last `put()` call: confirm the highest index any
    `put()` call actually writes is `< TILE_DATA_TILES` (a build-time guard — if a future package
    adds a tile at index ≥184 without bumping this constant, the build fails loudly here instead
    of silently corrupting VRAM at runtime).
- **Modify: `asm_game.py`**:
  - `asm_game.py:359`: change `rom.LD_BC_nn(256 * 16)` to `rom.LD_BC_nn(TILE_DATA_TILES * 16)`,
    importing/mirroring the same constant from `tiles.py` (this file already does
    `from tiles import *` per its own existing convention — confirm at implementation time,
    drift check) so the two sites can never silently desync.
- **No change** to any `TL_*` constant's own value, any `_put()` call site, `build_rom.py`, or any
  screen-composition file — confirmed by this package's own scope: only the *emitted array length*
  and the *matching copy count* change, nothing that reads or writes a specific tile index.

## 7. Implementation Tasks

Ordered: (1) confirm the highest-used `TL_*` constant by direct re-scan at implementation time
(drift check — a future package may have added tiles since this planning pass; re-verify 181 is
still the ceiling before hardcoding 184); (2) add `TILE_DATA_TILES` to `tiles.py`, update
`build_tile_data()`'s allocation and add the bounds assertion; (3) update `asm_game.py`'s copy-count
constant to match; (4) rebuild the ROM — confirm exactly `1,152` fewer bytes used than the current
baseline, valid header; (5) run the full suite — confirm zero regressions (every existing tile
render/lookup test should be completely unaffected, since no tile's own index or content changed);
(6) documentation/traceability updates (§9).

## 8. Tests to Add

No new suite. Extends **T1** (ROM structure/header) with one new static check:

- **New check (T1.x) — Tile-data bounds:** confirms `build_tile_data()`'s returned length equals
  `TILE_DATA_TILES * 16` exactly, and that every `TL_*` constant in `tiles.py` is `< TILE_DATA_TILES`
  — a permanent guard against this exact class of future drift (a new tile added at an index at or
  beyond the trimmed boundary without updating the constant).

## 9. Documentation Updates

- `docs/requirements/02-non-functional-requirements.md`: `NFR-4000` Notes — record the recovered
  headroom (1,152 bytes) and the new, lower "wasted padding" baseline (256-184=72 slots still
  reserved above the current ceiling, available for future tiles up to index 183 with zero further
  ROM-layout change).
- `docs/architecture/07-data-model.md` §3: no change needed — the tile-index *map* (which index
  means what) is unchanged; only the *unused tail* shrinks.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- `build_tile_data()` emits exactly `184 * 16 = 2,944` bytes (down from 4,096).
- The boot-time tile-copy DMA count matches exactly — confirmed by direct code read, both sites
  reference the same `TILE_DATA_TILES` constant.
- Every existing tile render/lookup behavior is bit-for-bit unchanged — confirmed by full suite
  pass with zero new/changed assertions beyond the one new bounds check.
- ROM total usage drops by exactly 1,152 bytes from the pre-package baseline.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, unchanged in every existing assertion.
- [ ] Direct diff: no `TL_*` constant's value changed; no `_put()` call site changed.
- [ ] `tiles.py`'s `build_tile_data()` and `asm_game.py`'s copy-count both reference the same
      `TILE_DATA_TILES` constant (confirmed by direct code read, not just matching literals).
- [ ] New T1.x bounds check present and passing.
- [ ] ROM total usage confirmed exactly 1,152 bytes lower than the pre-package build.

## 12. Dependencies

None — independent of `IP-1022`/`BL-0134`'s own larger residual shortfall, safe to ship on its own
regardless of how that larger question is resolved. No other in-flight package touches
`tiles.py`'s `build_tile_data()` or `asm_game.py`'s boot-init tile-copy block.

## 13. Risks

- **Very low.** A fixed-size-array trim with a build-time bounds assertion guarding against silent
  future drift; zero WRAM/SRAM impact, zero save-format impact, zero change to any tile's own
  content or index.
- **Does not, by itself, unblock `IP-1022`** — recovers 1,152 of the ~3,358 bytes that package
  needs; the residual ~2,200-byte gap requires a separate decision (see `BL-0134`'s own TWBS
  entry). Named explicitly so this package is not mistaken for a full fix.

## 14. Rollback Considerations

Revert `tiles.py`'s `TILE_DATA_TILES` constant/assertion and `asm_game.py`'s copy-count change,
then rebuild — reverts to the current 4,096-byte fixed allocation. No save-format dependency, no
WRAM/SRAM layout change, no `SAVE_VERSION_VAL` bump.
