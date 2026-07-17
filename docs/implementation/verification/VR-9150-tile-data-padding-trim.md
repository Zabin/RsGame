# VR-9150 — Tile-Data Padding Trim

## Package

`IP-9150` (commit `db0f663`, "perf(rom): IP-9150 -- tile-data padding trim (1,152 bytes
recovered)"), verified against the current tree head.

## Result

**VERIFIED** — 0 failed checks.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `build_tile_data()` emits exactly `184*16=2,944` bytes | `T1.13`: `len=2944 expected=2944` | PASS |
| Boot-time copy DMA count matches, both sites reference the same `TILE_DATA_TILES` | `tiles.py:930` `TILE_DATA_TILES = 184`; `asm_game.py:400` `rom.LD_BC_nn(TILE_DATA_TILES * 16)` — same imported constant (`asm_game.py:18`'s `from tiles import ... TILE_DATA_TILES`), not a duplicated literal | PASS |
| Every existing tile render/lookup behavior bit-for-bit unchanged | No `TL_*` constant value changed (`git show db0f663` diff to `tiles.py` is additive: new constant + assertion only); full suite 321/321 with no existing assertion altered | PASS |
| ROM usage drops by exactly 1,152 bytes from the pre-package baseline | Pre-package (post-`IP-9160`) baseline: 32542/32768 (per `VR-9160`'s commit note). Current: 31390/32768. `32542 - 31390 = 1,152` — exact match | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | `python3 build_rom.py` → 32768 bytes written, 31390/32768 used | PASS |
| G5: full suite passes, unchanged in every existing assertion | 321/321 pass | PASS |
| No `TL_*` value changed; no `_put()` call site changed | Direct read of `tiles.py` diff: only the new `TILE_DATA_TILES` constant + `build_tile_data()`'s allocation line + one bounds assertion added; independently re-derived the highest-used `TL_*` (`max(...) == 181`) matching the package's own claim | PASS |
| Both sites reference the same constant, confirmed by code read (not matching literals) | Confirmed above — `asm_game.py` imports `TILE_DATA_TILES` from `tiles.py` via its existing `from tiles import *`-style explicit list, not a re-typed literal | PASS |
| New `T1.13` bounds check present and passing | Confirmed (`T1.13` in the 321/321 run) | PASS |
| ROM total usage confirmed exactly 1,152 bytes lower than the pre-package build | Confirmed above | PASS |

## Requirements audit

No FR/NFR directly implemented (package's own §3: none). `NFR-4000`'s Notes entry (recorded
headroom) confirmed present in `docs/requirements/02-non-functional-requirements.md`'s diff in
commit `db0f663`.

## Test run

- `python3 build_rom.py` → 32768 bytes, valid header, 31390/32768 used.
- `python3 test_rom.py` → **321/321 passed, 0 failed** (same tree state as the three preceding
  verification passes this session).

## Scope audit

Commit `db0f663` touches exactly: `asm_game.py` (2 lines), `tiles.py` (13 lines, additive),
`test_rom.py`, `docs/requirements/02-non-functional-requirements.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`BunnyQuest.gbc`, `test_results.txt`. No `build_rom.py` or screen-composition file touched, per
the package's own §6. No excursion.

## Findings

None.

## Independence note

Implemented in a prior session (run #207, 2026-07-17), not this one — independence satisfied.
