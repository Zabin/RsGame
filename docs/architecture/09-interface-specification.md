# GDS-09 — Interface Specification

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-08](08-presentation-architecture.md); the
> next level, [GDS-10 RTM level](10-requirements-traceability-matrix.md), builds on this one.

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
