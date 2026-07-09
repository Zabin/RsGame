# GDS-09 — Interface Specification

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment — see "Interface delta" below).** Owned by `03-architecture-design-synthesis`.
> Builds on [GDS-08](08-presentation-architecture.md); the next level,
> [GDS-10 RTM level](10-requirements-traceability-matrix.md), builds on this one.

## Purpose

The module contracts: `build_game_asm(rom) → patches dict`, `build_tile_data()`, `ALL_SCREENS`,
`ZONE_COLLECTS`, `music_data()`, and the `ROM` class emitter surface.

## Content

Six contracts, one per cross-module interface point ([GDS-03](03-architecture.md) names the
modules; this level names their call-boundary shapes):

### `class ROM` (`gbc_lib.py`)

The assembler substrate every other module depends on. **159 public methods** (confirmed by
direct count): one per SM83 instruction variant
([R101](../research/encyclopedia/R101-sm83-instruction-set.md)), plus `label()`/`resolve()`
(the fixup system, [R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md))
and `set_header()` ([R109](../research/encyclopedia/R109-cartridge-header-checksums.md)). Every
other module's only contract with `ROM` is: construct it once, call its methods to emit bytes/
labels, call `resolve()` exactly once at the end. No module reads `ROM`'s internal `fixups`/
`labels` state directly.

### `build_game_asm(rom: ROM) -> dict` (`asm_game.py`)

Takes a `ROM` instance, emits all game logic into it (ISRs, state machine, WRAM constants), and
**returns a `patches` dict**: `{key: buffer_position}` for every placeholder the caller
(`build_rom.py`) must later fill with a real address once data sections are laid out
([R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)). Confirmed keys
(per [GDS-07](07-data-model.md)'s section list): `tile_src`, `bg_pal`, `obj_pal`, `mus_lo`/
`mus_hi`/`mus_reset`, and one `_t`/`_a` pair per screen (`title_t`/`title_a` … `z0`…`z8`'s
equivalents via `zs_table`, `zc_table`). **Contract: every key this function returns must be
filled by the caller before `rom.resolve()`** — an unfilled patch key is an incomplete build, not
a silent default.

### `build_tile_data() -> bytes` (`tiles.py`)

Returns a **fixed 4096-byte buffer** (`256 tiles × 16 bytes`, confirmed by direct read:
`bytearray(256 * 16)`), populated via an internal `put(idx, tile)` helper at each `TL_*` index
([GDS-07](07-data-model.md)). **Contract: the caller emits this buffer verbatim as one
contiguous ROM section** — it is not an incremental/streaming interface; every one of the 256
slots (used or not) is always present in the returned buffer, so unused slots contribute known,
zeroed bytes to the ROM rather than being omitted.

### `ALL_SCREENS` / `ZONE_COLLECTS` (`tilemaps.py`)

`ALL_SCREENS`: a list of 14 `(name, fn)` pairs, `fn() -> (tiles, attrs)` — two same-length byte
buffers per screen ([GDS-04](04-domain-model.md)/[GDS-07](07-data-model.md)). **Contract: the
caller calls every `fn()` in list order** and records each screen's resulting tile/attribute
addresses (the `zs_table`, for the 9 zone entries specifically). `ZONE_COLLECTS`: a list of 9
lists of `(x, y, type)` tuples, one outer entry per zone in index order — **contract: the caller
prefixes each zone's list with its length byte and emits `(x, y, type, 0)` per entry**
([GDS-07](07-data-model.md)'s per-zone collectible-table format), building the `zc_table` pointer
array from the resulting addresses.

### `music_data() -> list[int]` (`music.py`)

Returns a flat byte list built from `SONG`'s `(freq, duration)` note tuples via `note()`/`freq()`
([R108](../research/encyclopedia/R108-apu-channels-registers.md)) — with one notable interface
detail confirmed by direct read: a **terminal `0xFF` byte appended after every note**, a loop-back
marker for the playback routine to detect end-of-song and restart. **Contract: any future
multi-track or per-zone music extension must preserve this terminal marker convention** — the
playback code in `asm_game.py` reads until it sees `0xFF`, not a fixed length.

## Interface delta (2026-07-09 — target state, not yet shipped)

Per **ADR-0009**/**ADR-0010** and [GDS-07](07-data-model.md)'s/
[R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)'s deltas: one new
module contract and two extensions to existing contracts.

### `worldgen.py` (new, proposed — build-side reference-generator oracle)

Per [R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)'s extension: a
new sibling module to `tiles.py`/`tilemaps.py`/`music.py`, reimplementing the SM83 world-
generation algorithm ([ADR-0009](adr/ADR-0009-screen-graph-world-generation.md)) in Python.
**Proposed contract**: `generate(seed: int, scale: int) -> RegionGraph`, where `RegionGraph`
exposes at minimum `regions: list[{biome_id, neighbors}]` and `key_item_region_index: int`-style
data matching [GDS-07](07-data-model.md)'s proposed `REGION_GRAPH` layout field-for-field.
**Contract: `worldgen.py`'s algorithm and `asm_game.py`'s SM83 generation routine must produce
byte-identical results for the same `(seed, scale)`** — this is the load-bearing correctness
property [R305](../research/encyclopedia/R305-emulator-based-test-design.md)'s reference-
generator-oracle testing strategy depends on; the two implementations are kept in lockstep by
direct correspondence (same PRNG step order, same grammar-check order), not shared code, the
same discipline this level's existing contracts already assume between `build_rom.py` and
`asm_game.py`. **Consumer**: `test_rom.py` imports `worldgen.py` to compute expected values for
any `(seed, scale)` in its determinism/property-test corpus; `build_rom.py`/`asm_game.py` do
**not** import it — the SM83 routine is the actual runtime generator, `worldgen.py` is a test-only
oracle, not a shared implementation.

### `build_game_asm(rom: ROM) -> dict` — new patch-point keys (extends the existing contract)

The world-generation and seed/scale-entry code
([ADR-0009](adr/ADR-0009-screen-graph-world-generation.md)/
[ADR-0010](adr/ADR-0010-seed-scale-model.md)) needs new entries in the existing `patches` dict,
following the established naming convention — e.g. a patch point for the seed/scale-entry
screen's tile/attribute addresses (parallel to today's `title_t`/`title_a` pattern) and any
generator-data pointers `build_rom.py` lays out after `build_game_asm()` returns. **No new
resolution mechanism** — this is the existing contract, exercised with new keys, exactly as
[R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)'s own guidance already
anticipated for future growth ("many more zones means many more patch-point entries... still the
same mechanism, no redesign needed").

### `ALL_SCREENS` — biome-family screen generators (extends the existing contract)

Where `ALL_SCREENS` today lists one `(name, fn)` pair per fixed zone (`beach_screen()` …
`castle_screen()`), a generated world's per-region rendering needs **one `fn()` per biome
*family*** (not per region — regions of the same biome family share a rendering function,
parameterized by the region's specific generated content), consistent with
[GDS-08](08-presentation-architecture.md)'s delta (biome families, not per-region unique art).
**Contract unchanged**: each `fn() -> (tiles, attrs)` still returns the same two-buffer shape;
only the caller's iteration source changes (from a fixed 9-entry list to a variable-length,
`WorldScale`-driven set of generated region-render calls) — a `build_rom.py`-side change, not an
`ALL_SCREENS`-shape change.

**This delta does not touch `class ROM`, `build_tile_data()`'s buffer contract, `ZONE_COLLECTS`'s
per-zone-list shape (generalizes to per-region, same shape), or `music_data()`** — none of those
contracts are affected by C9/C10.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for (interface
      *shapes* — parameter/return types, contract obligations — not the emitted bytes'
      addresses, which are [GDS-07](07-data-model.md)'s job).
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-08`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** This level's only stated source is "the code itself" — no
`Claude.md`/`memory.md` section is superseded here, since neither document previously attempted
to state these interface contracts explicitly (they describe *what the code does*, not *what
contract callers must honor*). No merge conflict to resolve; this level is wholly new content
relative to the pre-existing docs.

**Delta record (2026-07-09):** "Interface delta" section added above, per the adopted increment
plan's Phase 3. Delta, not re-authoring — the six as-built contracts above remain accurate; the
new/extended contracts describe the target `worldgen.py`/patch-point/`ALL_SCREENS` shape, not
yet built. No merge-gate box above is reopened.
