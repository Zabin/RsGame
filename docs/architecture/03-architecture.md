# GDS-03 — Architecture

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-02](02-system-context.md); the next level,
> [GDS-04 Domain Model](04-domain-model.md), builds on this one.

## Purpose

Module decomposition (`gbc_lib`/`tiles`/`tilemaps`/`music`/`asm_game`/`build_rom`), the
one-job-per-file rule, and the patch-point build contract.

## Content

### 1. The one-job-per-file rule

Six modules (2573 lines total), each owning exactly one concern — confirmed by direct code read
against each module's actual top-level exports, not inferred from naming alone:

| Module | Lines | Job | Primary export |
|---|---|---|---|
| `gbc_lib.py` | 225 | SM83 opcode emitters, label/fixup resolution, header/checksum writing | `class ROM` |
| `tiles.py` | 992 | 2bpp tile pixel data | `build_tile_data()` |
| `tilemaps.py` | 420 | Screen composition, collectible tables | `ALL_SCREENS`, `ZONE_COLLECTS` |
| `music.py` | 57 | Channel-1 melody data | `SONG`, `music_data()` |
| `asm_game.py` | 706 | Game logic: ISRs, state machine, WRAM/IO constants | `build_game_asm(rom: ROM) -> dict` |
| `build_rom.py` | 173 | Master orchestrator | `build(out_path='BunnyQuest.gbc')` |

No module reaches into another's internal representation — `asm_game.py` calls `ROM`'s emitter
methods but never touches `gbc_lib.py`'s internal `fixups`/`labels` state directly; `build_rom.py`
imports every other module's top-level export but contains no opcode-emission logic of its own.
This is the concrete instance of the "one job per file" rule
[GDS-02](02-system-context.md) named without detailing.

### 2. `gbc_lib.py` — the assembler substrate

`class ROM` (confirmed by direct read) is a single-purpose byte-buffer object: one method per
SM83 instruction variant ([R101](../research/encyclopedia/R101-sm83-instruction-set.md)),
`label()`/`resolve()` implementing the two-pass fixup scheme
([R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)), and
`set_header()` writing the cartridge header and both checksums
([R109](../research/encyclopedia/R109-cartridge-header-checksums.md)). Every other module
depends on this one; it depends on nothing else in the project.

### 3. Content modules — `tiles.py`, `tilemaps.py`, `music.py`

Three modules that produce **data, not code**: `tiles.py`'s `build_tile_data()` returns encoded
tile bytes ([R303](../research/encyclopedia/R303-2bpp-tile-encoding.md)); `tilemaps.py`'s
`ALL_SCREENS` (14 entries: 9 zones + title/intro/save/map/victory) and `ZONE_COLLECTS` (per-zone
collectible coordinate/type tables) are the screen-composition output
([R203](../research/encyclopedia/R203-screen-composition-tile-grid.md)); `music.py`'s `SONG`
(a list of `(freq, duration)`-shaped note tuples via its `note()`/`freq()` helpers) and
`music_data()` produce the channel-1 melody bytes
([R108](../research/encyclopedia/R108-apu-channels-registers.md)/
[R207](../research/encyclopedia/R207-gb-chiptune-composition.md)). None of these three modules
import `asm_game.py` or `build_rom.py` — data flows one direction only, from content modules
toward the orchestrator, never back.

### 4. `asm_game.py` — game logic

The one module that emits actual game behavior: ISRs (the VBlank handler at `0x0040`,
[R110](../research/encyclopedia/R110-interrupt-model-isr.md)), the six-state game-state machine
([GDS-01](01-concept-of-play.md)), WRAM/IO address constants (`GAMESTATE`, `CUR_ZONE`,
`CARROTS_COUNT`, `CARROT_FLAGS`, etc. — [GDS-07](07-data-model.md) owns the full map once
authored), joypad handling ([R107](../research/encyclopedia/R107-joypad-register.md)), sound init
([R108](../research/encyclopedia/R108-apu-channels-registers.md)), OAM/DMA
([R105](../research/encyclopedia/R105-oam-sprites-dma.md)), and save/load
([R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md)). Its single public entry point,
`build_game_asm(rom: ROM) -> dict`, both emits all of this code into the passed `ROM` instance
*and* returns the patch-point dict (§5) — the two outputs of one call, not two separate steps.

### 5. `build_rom.py` — the patch-point contract

The master orchestrator, `build(out_path='BunnyQuest.gbc')`, is the only module that calls every
other module and the only one that knows the final build order. Per
[R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md), that order is fixed
and load-bearing:

```
build_game_asm(rom)              # emits code + labels; returns `patches` dict of
                                  # position -> not-yet-known-address placeholders
   ↓
lay out tile data / palettes /   # each section's real address becomes known
music / all 14 screens /            only once it's actually placed in the buffer
zone-collectible table
   ↓
p16(patches[key], real_address)  # for every key returned above, patch the
                                  # real address into its placeholder position
   ↓
rom.resolve()                    # close out the label/fixup system (intra-code
                                  # jumps/calls only — never used for the
                                  # patch-point class of reference)
   ↓
rom.set_header(...)              # header + both checksums, last (sees final bytes)
   ↓
write file
```

Reordering any step in this chain (e.g. resolving labels before patches are written, or writing
the header before the ROM's final bytes are settled) produces a corrupt or unbootable ROM — this
is not a stylistic preference, it's the actual dependency order the six modules' outputs require.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-02`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `Claude.md`'s "Architecture Overview" section (the module table
+ ROM data-layout diagram) is close to accurate for the *module list* itself — the six-module
decomposition hasn't changed since the Bunny Quest rewrite — but its accompanying prose and
`test_rom.py`-suite references elsewhere in the same file are stale (per `GDS-01`/`GDS-02`'s
established finding). **Decision: this level supersedes `Claude.md`'s Architecture Overview
section as the authoritative module-decomposition reference**, since this level's line counts,
export names, and build-order description were verified directly against the current source
(not assumed from the existing table). `Claude.md`'s section should become a short pointer here
once the `BL-0007`/`BL-0008` documentation-refresh pass lands.

## Recommendation (not actioned this pass)

This level's own scope note (docs/architecture/adr/) suggests authoring the as-built ADRs this
project has accumulated (single-bank ROM, Python-assembler-over-RGBDS, shadow-OAM DMA every
frame, 8×16 OBJ mode, MBC1+RAM+BATTERY, PyBoy-as-gate). Deferred to a dedicated future pass rather
than folded into this run, per the one-level-per-advance discipline — `docs/architecture/adr/`
remains empty pending that pass.
