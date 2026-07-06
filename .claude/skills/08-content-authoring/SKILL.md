---
name: 08-content-authoring
description: Implement exactly one approved, eligible content-scoped Implementation Package — tile pixel art, screen/tilemap layouts, collectible spawn tables, palettes, and music note data (the data halves of tiles.py, tilemaps.py, music.py) plus the test_rom.py checks that verify them — rebuild the ROM, run the full suite, and advance the package on the Master Build Plan. Use when asked to implement a content package ("draw the new tile set," "lay out the new zone screen," "add the new song," "implement IP-xxxx" where the package names this skill). Peer of 08-code-implementation, which owns game logic and build machinery; this skill never edits asm_game.py/gbc_lib.py/build_rom.py beyond the data-registration hook its package explicitly names (e.g. a put() call in build_tile_data() or a screen registration in ALL_SCREENS). Verification to VERIFIED belongs to 09-package-verification; qualitative review belongs to 09-content-review.
---

# Content Authoring

The stage-08 peer that owns the game's **content**: tile art, screen layouts, spawn tables,
palettes, and music. Same discipline as `08-code-implementation` — one approved, eligible package
per invocation, faithful to the package, full suite green after — with a content-shaped write
surface and content-shaped verification.

## Write scope (G1)

- `tiles.py` — pixel arrays, `TL_*` constants, `put()` registrations in `build_tile_data()`.
- `tilemaps.py` — screen generator functions, `ALL_SCREENS`, `ZONE_COLLECTS` spawn tables.
- `music.py` — `SONG` note data, tempo constants, `freq()` uses.
- `test_rom.py` — checks verifying the new content (tile non-zero/bitplane checks, tilemap
  content checks, spawn-position checks, music-data checks), extending the existing suite
  pattern.
- Palette definitions in `build_rom.py` **only if** the package explicitly names them (colors
  live there today; a palette-only package is legitimate content work).

Everything else — logic, ISRs, opcodes, ROM layout, WRAM — is `08-code-implementation`'s surface.
A package needing both surfaces should have been split at stage 07; if it wasn't, implement only
this skill's half and file the seam problem as an Outstanding Issue.

## Workflow (mirrors the code peer; differences below)

1. **Select & gate** exactly as `08-code-implementation` Steps 0–1 (status `READY`, dependencies
   `VERIFIED`, G3 authorization or the bootstrap carve-out). The package must name this skill as
   its owner.
2. **Read the package + spec + the content quick-refs** — `memory.md`'s tile index map and
   palette tables, and GDS-07/GDS-08 once authored — before drawing anything. Verify claimed tile
   slots are actually free and claimed screens/constants exist.
3. **Mark `IN PROGRESS`**, then author the content per the package:
   - **Tiles:** 8×8 arrays in the established 2-bit color-index style; register via `put()` in an
     unused slot; keep the tile index map's conventions (0x00–0x0F sprites, 0x10+ BG, 0x40+ font
     — see `memory.md`).
   - **Screens:** generator functions returning the established (tiles, attrs) shape; respect the
     20×18 visible grid, row-0 UI bar, and edge-exit conventions; spawn tables keep the
     (x, y, type) format and must not overlap player spawns (a v1 bug class — see `Claude.md`).
   - **Music:** (freq, duration) tuples via `freq()`; keep QN/HN frame conventions.
   - **Budget:** every tile is 16 bytes, every screen 576 bytes, music is pointer-walked — state
     the byte cost against the GDS-07 section budget; overflow is a Blocking Report, not a
     squeeze.
4. **Verify (G5 + eyes):** rebuild the ROM, run the full `test_rom.py`, **and** drive the
   affected screens in the emulator via `run-bunnygarden` and capture screenshot(s) — content
   work is not done on green checks alone; the screenshot goes in the Implementation Summary for
   `09-content-review` to judge.
5. **Docs & traceability:** update `memory.md`'s tile/palette/collectible quick-refs and any
   Documentation Updates the package names; fill the RTM cells for Requirements Covered.
6. **Ledger, summary, stop:** package → `COMPLETE`; Implementation Summary (same fields as the
   code peer, plus screenshot paths); no second package.

## Blocking conditions & quality checklist

Identical in kind to `08-code-implementation` (drift, eligibility, authorization, budget
overflow → Blocking Report; full-suite green, scope discipline, traceability, honest summary) —
plus:

- [ ] New tiles registered in `build_tile_data()` and recorded in `memory.md`'s tile index map.
- [ ] Screens/spawns respect grid, UI-bar, edge-exit, and no-spawn-overlap conventions.
- [ ] Byte cost stated against the section budget.
- [ ] Screenshot(s) of the affected content captured and referenced in the summary.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 08 — Package Execution (content peer)** of the pipeline (see
[`.claude/skills/README.md`](../README.md)). Upstream: `07-implementation-planning`. Downstream:
`09-package-verification` (ledger verification) and `09-content-review` (qualitative review of
the rendered result).

End every run with the Implementation Summary plus:

1. **Recommendations** — Outstanding Issues with suggested owners.
2. **Next step** — after `COMPLETE`: `09-package-verification` on this package, then
   `09-content-review` for the rendered result (both before any dependent package builds on it);
   after a Blocking Report: whatever it names.

Never end a run without naming the next step.
