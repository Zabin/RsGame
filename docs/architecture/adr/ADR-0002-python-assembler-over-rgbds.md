# ADR-0002 — Python assembler (`gbc_lib.py`) instead of the RGBDS toolchain

**Status:** Accepted (as-built, mined 2026-07-06)

## Context

The project does not use RGBDS (the standard Game Boy assembler/linker toolchain) or any `.asm`
source files. Instead, `gbc_lib.py`'s `class ROM` (159 public methods, one per SM83 instruction
variant, confirmed by direct count — [GDS-09](../09-interface-specification.md)) is called
directly from Python (`asm_game.py`, `build_rom.py`) to emit ROM bytes programmatically, with its
own `label()`/`resolve()` fixup system standing in for a linker
([R302](../../research/encyclopedia/R302-python-assembler-codegen-patterns.md)). This is confirmed
as the entire toolchain — no RGBDS dependency exists anywhere in the build (`build_rom.py`).

## Decision

Keep the Python-assembler-as-library approach as the project's toolchain rather than migrating to
RGBDS. This was an already-made decision by the time this ADR was mined (the entire codebase is
built on it); recording it here makes the decision and its tradeoffs explicit for future
contributors rather than leaving it as an implicit fact only visible by reading all six modules.

## Consequences

- The whole game-logic/data-emission pipeline is ordinary Python: testable with standard Python
  tooling, no separate assembler invocation/toolchain-installation step
  ([R306](../../research/encyclopedia/R306-toolchain-portability.md)), and data-driven screen/
  tile/music generation (`tilemaps.py`, `tiles.py`, `music.py`) is naturally expressed as Python
  functions rather than hand-written assembly with a codegen preprocessor bolted on.
- Trades away RGBDS's macro system, standard-library conventions, and the wider GBC-dev
  community's tooling/debugging familiarity — a contributor fluent in RGBDS-based projects must
  learn this project's bespoke `ROM` class API instead of reusing existing RGBDS knowledge.
- The patch-point dict pattern ([ADR-0004](ADR-0004-patch-point-dict-linkage-contract.md)) exists
  *because* there is no linker doing this resolution automatically — a direct consequence of this
  decision, not an independent one.
