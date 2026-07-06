# ADR-0003 — One-job-per-file module decomposition

**Status:** Accepted (as-built, mined 2026-07-06)

## Context

The codebase is split into six modules, each with a single clear responsibility, confirmed by
direct read and line count ([GDS-03](../03-architecture.md)): `gbc_lib.py` (225 lines, the
assembler substrate), `tiles.py` (992 lines, tile-graphics data only), `tilemaps.py` (420 lines,
screen/collectible layout data only), `music.py` (57 lines, song data only), `asm_game.py` (706
lines, game logic/state machine only), `build_rom.py` (173 lines, orchestration only). No module
mixes data authoring with the assembler substrate or the orchestration logic.

## Decision

Maintain strict one-job-per-file boundaries: data-authoring modules (`tiles.py`, `tilemaps.py`,
`music.py`) never call `ROM` methods directly or make assembly decisions; `asm_game.py` never
authors tile/screen/song data inline; `build_rom.py` never contains game logic, only sequencing.
New content (a new zone, a new song, a new game-state) is added by extending the module that owns
that kind of content, not by reaching across the boundary.

## Consequences

- Each module can be understood, tested, and modified independently — a tile-art change never
  risks touching the state machine, and vice versa.
- The [GDS-09](../09-interface-specification.md) interface contracts (`build_game_asm(rom) ->
  patches`, `build_tile_data() -> bytes`, `ALL_SCREENS`/`ZONE_COLLECTS`, `music_data()`) exist
  as clean call-boundary shapes specifically because this decomposition is honored — a module
  that mixed responsibilities would not have a describable single contract.
- The tradeoff is indirection: adding a new screen touches `tilemaps.py` (data) and `build_rom.py`
  (wiring the resulting patch keys), never a single file — a deliberate cost in exchange for the
  isolation above.
