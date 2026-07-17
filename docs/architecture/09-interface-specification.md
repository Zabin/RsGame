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

### `generate_theme_variations(main_theme=SONG, transforms=THEME_TRANSFORMS) -> dict[str, list[int]]` (`music.py`, `IP-1110`)

Build-time-only (called from `build_rom.py`, never on-console — `ADR-0019` point 2/3). Produces
one `music_data()`-format byte list per non-Grass biome-family identity (`water`/`sand`/`stone`/
`brick`/`village`/`cave`/`desert`/`plains`) by applying a per-identity `(semitone_shift,
duration_scale)` pair to every note in `SONG`, reusing `music_data()`'s own terminal-`0xFF`-marker
convention via the shared `_encode_notes()` helper (`music_data()` itself now delegates to it).
Grass is the zero-transform anchor (`IP-1110`'s own resolution of `FS-111` Open Question 3) — its
own track is `music_data()`'s existing output, unmodified, not a `generate_theme_variations()`
entry. Raises `ValueError` at build time if any transposed frequency falls outside `freq()`'s own
representable 11-bit range (`note()`'s encoding would otherwise silently truncate it).

**Contract: the nine tracks (Grass + eight generated) are exposed via a flat, ROM-resident
16-bit address table (`build_rom.py`'s `music_table_addr`), indexed by `FR-4320`'s own biome-id
order (0=Water…8=Plains), mirroring `zc_table`'s own established pointer-array pattern** — **not**
the per-identity named-patch-key scheme `IP-1110`'s own planning text originally proposed
(mirroring `mus_lo`/`mus_hi`'s two-key shape). That scheme would require creating each new patch
key at the SM83 instruction that loads it, which only `asm_game.py` code can do — contradicting
`IP-1110`'s own explicit no-`asm_game.py`-changes scope boundary, a genuine inconsistency in the
original plan discovered during implementation. This table-indexed contract is what a future
runtime-selection package (`IP-1111`) must consume — it needs to build the table's own base
address and index by biome-id (`table_addr + biome_id*2`), not read a per-identity named constant.

## Interface delta (2026-07-09 — target state, not yet shipped)

Per **ADR-0009**/**ADR-0010** and [GDS-07](07-data-model.md)'s/
[R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)'s deltas: one new
module contract and two extensions to existing contracts.

### `worldgen.py` (shipped 2026-07-10, `IP-1020` — build-side reference-generator oracle)

Per [R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)'s extension: a
new sibling module to `tiles.py`/`tilemaps.py`/`music.py`, reimplementing the SM83 world-
generation algorithm ([ADR-0009](adr/ADR-0009-screen-graph-world-generation.md)) in Python.
**Confirmed contract**: `generate(seed: int, scale: int) -> list[dict]`, matching the proposed
shape exactly — each element is `{'biome_id': int, 'neighbors': [up, down, left, right]}`
(`None` where the proposed contract's `0xFF` sentinel appears), row-major order matching
[GDS-07](07-data-model.md) §6's confirmed `REGION_GRAPH` layout field-for-field (no separate
`key_item_region_index` field was needed — every region unconditionally holds exactly one
`KeyItem`, per FR-9130, so nothing distinguishes one region's item slot from another's).
**Contract confirmed as shipped: `worldgen.py`'s algorithm and `asm_game.py`'s
`generate_world`/`gw_prng_step` routines produce byte-identical results for the same `(seed,
scale)`** — proven, not just asserted, by `test_rom.py`'s **T12.b** (a 15-entry seed/scale
corpus, zero mismatches) — this is the load-bearing correctness property
[R305](../research/encyclopedia/R305-emulator-based-test-design.md)'s reference-generator-oracle
testing strategy depends on; the two implementations are kept in lockstep by direct
correspondence (same PRNG step order — 16-bit xorshift, `x^=x<<1; x^=x>>1; x^=byteswap(x)` — same
row-major visitation, same top/left-constraint-intersection clamp), not shared code, the same
discipline this level's existing contracts already assume between `build_rom.py` and
`asm_game.py`. **Consumer**: `test_rom.py` imports `worldgen.py` to compute expected values for
any `(seed, scale)` in its T12 property-test corpus, and to drive `generate_world` directly via a
PC/SP hijack (`invoke_generate_world`, since no call site exists yet — `FEAT-1100`'s scope);
`build_rom.py`/`asm_game.py` do **not** import it — the SM83 routine is the actual runtime
generator, `worldgen.py` is a test-only oracle, not a shared implementation.

### `build_game_asm(rom: ROM) -> dict` — new patch-point keys (extends the existing contract)

**Confirmed (2026-07-10, `IP-1020`): `generate_world` itself needs no new `patches` dict key.**
FS-102 Open Question 3 resolved during `07-implementation-planning`: the grammar check is inline
arithmetic (adjacency legal iff axis indices differ by ≤1, a single comparison), not ROM-resident
table data, so no generator-data pointer exists to patch. The seed/scale-entry *screen's*
tile/attribute addresses (parallel to today's `title_t`/`title_a` pattern) remain
`FEAT-1100`/`IP-1040`'s scope — still expected to use this same, unmodified `patches` dict
mechanism, following the established naming convention. **No new resolution mechanism** — this is
the existing contract, exercised with new keys where `IP-1040` needs them, exactly as
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

**Confirmed (2026-07-10, `IP-1030`): the shipped mechanism is 5 named `patches` dict key pairs
(`water_t`/`water_a` … `brick_t`/`brick_a`), parallel to `title_t`/`title_a`, not a build-time
variable-length table.** `ALL_SCREENS` itself stays a fixed 10-entry list (5 biome-family
representatives + 5 UI screens) — the "variable-length, `WorldScale`-driven set" language above
described the *player-visible region count*, not `ALL_SCREENS`'s own shape, which this package
confirms is fixed at build time (family count is a build-time constant; only the *runtime dispatch*
— which of the 5 pre-built family screens a given region's generated biome-id selects — varies).
At runtime, `asm_game.py`'s `dsr_p` reads the current region's biome-id out of `REGION_GRAPH`
(`IP-1020`) and branches to the matching named patch pair before the unmodified `copy_screen` call
— `_zone_arrows`' build-time rectangle math (`tilemaps.py`) is retired in favor of a new runtime
`draw_region_arrows` routine reading `REGION_GRAPH`'s per-region neighbor bytes directly.

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
