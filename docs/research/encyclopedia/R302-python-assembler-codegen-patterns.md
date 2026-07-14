# R302 — Python-Assembler Codegen Patterns

- **Document ID:** R302 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (the opcode emitters this pattern assembles)
- **Referenced By:** R305 (this topic's module-boundary convention grounds R305's
  reference-generator oracle placement), R307 (these conventions are why the build is
  deterministic, making byte-identity a valid refactoring oracle)
- **Produces:** grounds `gbc_lib.py`'s `resolve()`/label mechanism and `build_rom.py`'s
  patch-point dict pattern
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R101

## Purpose

How this project's from-scratch Python assembler resolves labels and wires cross-module data
addresses — the exact mechanism a new `asm_game.py` routine or a new `build_rom.py` data section
must participate in correctly.

## Scope

Two-pass label resolution (forward references, jump-relative range checking), and the
patch-point-dict convention that lets `build_game_asm()` emit code before the data sections whose
addresses it needs even exist yet.

## Concepts

This is not RGBDS or any general-purpose assembler — `gbc_lib.py`'s `ROM` class is a **direct,
single-purpose Python object model of a 32 KB byte buffer**, written to incrementally via opcode
emitter method calls (R101) that `emit()` bytes at the current position. Two custom mechanisms
make this practical without a full multi-pass assembler:

1. **Label/fixup resolution.** `rom.label(name)` records the *current* buffer position under a
   name. Forward-referencing emitter calls (an address not yet known, e.g. a `JP`/`CALL` to a
   label defined later in the file) record a **fixup**: `(position, label_or_int, type)` tuple
   appended to a `fixups` list, with a placeholder written at `position` in the meantime.
   `rom.resolve()` — called once, after all code/labels have been emitted — walks every fixup and
   patches in the real value: `abs16` fixups write a full absolute little-endian address;
   relative-jump fixups compute `offset = target - (position + 1)` and **raise an exception if
   the offset falls outside `-128..127`** (i.e. outside signed-8-bit `JR` range) rather than
   silently truncating — a hard-fail-fast design choice, not a hazard to work around.
2. **Patch-point dicts.** Some data (e.g. a screen's tilemap address, a music track's ROM
   position) genuinely cannot be known until *after* the code that references it has already been
   emitted, because the data sections themselves are laid out by `build_rom.py` **after**
   `build_game_asm(rom)` returns. The convention: `build_game_asm()` returns a plain
   `dict[str, int]` mapping a descriptive key (e.g. `'title_t'`, `'tile_src'`) to the **buffer
   position of a placeholder value it already emitted** — not a label name, a raw byte offset.
   `build_rom.py` then lays out every data section, and once each section's final address is
   known, calls a small helper (`p16(patch_position, address)`) that writes the real 16-bit
   little-endian address directly into `rom.data` at that stored position — bypassing the
   label/fixup system entirely for this class of cross-module reference.

## Operational Context

`gbc_lib.py`'s `resolve()` is confirmed (direct code read) to implement exactly the two-pass
fixup scheme above, including the `abs16` vs. relative-jump distinction and the explicit
out-of-range guard for `JR`. `build_rom.py`'s master `build()` function calls
`build_game_asm(rom)` first (returning both the code's fixups being ready for `resolve()` *and* a
`patches` dict), then lays out tile data / palettes / music / all 14 screen tilemaps (9 zones +
title/intro/save/map/victory, per the Bunny Quest rewrite) / the zone-collectibles table, in that
order, recording each section's start address (`screen_addrs[name] = (t_addr, a_addr)` — tilemap
address, attribute-map address). Only *after* every section has a real address does `build_rom.py`
call `p16(patches[key], real_address)` for every entry in the patches dict returned earlier —
`tile_src`, `bg_pal`, `obj_pal`, `mus_lo`/`mus_hi`/`mus_reset`, and one `_t`/`_a` pair per screen
(`title_t`/`title_a`, `intro_t`/`intro_a`, … `z0`–`z8`'s equivalents via the loop at line ~115).
Only then is `rom.resolve()` called to close out the label/fixup system, and only then is the
header written and the file saved.

**Ordering is load-bearing:** `build_game_asm(rom)` → lay out all data sections → patch every
`patches[key]` position → `rom.resolve()` → `set_header()` → write file. Reordering any of these
steps (e.g. resolving labels before patches are written, or writing the header before checksums
can see the final patched bytes) would produce a corrupt or unbootable ROM.

## Implementation Guidance

- **A new routine referencing a not-yet-laid-out data section must add a new patch-point key**,
  following the existing naming convention (short, descriptive, e.g. `'z9_t'`/`'z9_a'` for a
  tenth zone) — never invent a parallel resolution mechanism; extend the one dict `build_rom.py`
  already threads through.
- **A new intra-code jump/call can rely on the label/fixup system directly** (`rom.label(name)`
  + a `JP`/`CALL`/`JR` emitter call referencing that name) — this does not need a patch-point
  entry; patch points exist specifically for *cross-module* (code → later-laid-out data)
  references, not for ordinary control flow within `asm_game.py` itself.
- **Never call `rom.resolve()` before every patch-point address is known** — resolve is a
  one-shot operation; per the ordering above, it must be the last step before header/checksum
  writing.
- **Respect the `JR` range check as a real signal, not an obstacle to bypass** — an out-of-range
  relative jump means the actual control-flow structure needs restructuring (e.g. an intermediate
  `JP` hop), not a reason to special-case the exception.
- **This pattern's growth path under MSTR-001 C7:** many more zones means many more patch-point
  entries and a much larger `screen_addrs` dict — still the same mechanism, no redesign needed,
  but a future bank-switched ROM (R106) would need `p16`'s helper (or a sibling) to also handle
  bank-relative addressing, since a simple flat 16-bit patch stops being sufficient once code/data
  can live in different banks.

## Where a reference-generator oracle module would live (2026-07-09, grounds MSTR-001 C10/R305)

R305's C10 extension recommends a **Python reference-generator oracle** — a build-side
reimplementation of the SM83 world-generation algorithm (R213/R111), used by `test_rom.py` to
compute expected values for any `(seed, scale)`. This project's existing module boundaries
(`Claude.md`'s "one job per file," `ADR-0003`) suggest the oracle is **its own module**, not
folded into `build_rom.py` or `test_rom.py` directly: `build_rom.py` lays out ROM sections and
has no reason to import test-only code; `test_rom.py` is the natural *consumer* of the oracle,
not its owner. A new module (e.g. a `worldgen.py` sibling to `tiles.py`/`tilemaps.py`/`music.py`)
matching this project's existing one-file-one-job pattern, imported by `test_rom.py` for its
expected-value computation, keeps the boundary clean — this is a naming/placement observation for
whichever `07-implementation-planning` package eventually specs the generator, not a decision
this research topic makes.

### Sources
No new external citation — grounded in this project's own existing module-boundary convention
(`ADR-0003`) and R305's oracle-pattern recommendation.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R101 (the opcode emitters this codegen pattern assembles into a byte buffer) · R305 (the
reference-generator oracle pattern this topic's module-placement note supports) · R213 (the
generation algorithm the oracle mirrors).
