# ADR-0004 — Patch-point dict as the code↔data linkage contract

**Status:** Accepted (as-built, mined 2026-07-06)

## Context

Because there is no linker ([ADR-0002](ADR-0002-python-assembler-over-rgbds.md)), code emitted by
`build_game_asm(rom)` before data sections exist cannot reference those sections' final addresses
directly. `asm_game.py` instead returns a `patches: dict` — `{key: buffer_position}` — for every
placeholder the caller must later fill once tile/palette/music/screen data is laid out
([GDS-09](../09-interface-specification.md), [R302](../../research/encyclopedia/R302-python-assembler-codegen-patterns.md)).
Confirmed keys: `tile_src`, `bg_pal`, `obj_pal`, `mus_lo`/`mus_hi`/`mus_reset`, and a `_t`/`_a`
pair per screen. `build_rom.py` is the only caller and honors a fixed build order: emit game logic
→ lay out data sections → fill every `patches[key]` → `rom.resolve()` → `rom.set_header()` →
write file.

## Decision

Keep the patch-point dict as the sole code↔data linkage mechanism. Any new placeholder a future
module needs (e.g. a new zone's screen addresses, a new song's pointer) is added to this same
`patches` dict, not via a parallel mechanism (no second linkage pattern is introduced alongside
it).

## Consequences

- The pattern is simple and fully visible — one dict, one caller, one fixed fill-then-resolve
  order — but it is also entirely convention-enforced, not compiler-enforced: an unfilled key is
  a silent, wrong ROM unless the caller is disciplined about filling every key before
  `rom.resolve()` ([GDS-09](../09-interface-specification.md)'s explicit contract statement).
- The build order (emit → lay out → patch → resolve → header → write) is load-bearing and must
  never be reordered — doing so corrupts the ROM, per [GDS-03](../03-architecture.md)/
  [R302](../../research/encyclopedia/R302-python-assembler-codegen-patterns.md).
- Any future module (e.g. a bank-switching layer per [ADR-0001](ADR-0001-single-bank-rom-no-mbc-switching.md))
  that needs cross-section addresses must plug into this same dict-based contract rather than
  inventing a second linkage mechanism, to keep `build_rom.py` the single place resolution order
  is reasoned about.
