# R303 — 2bpp Tile Encoding & Palette Data Formats

- **Document ID:** R303 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R104 (palette data this topic's tile indices select into)
- **Referenced By:** none yet
- **Produces:** grounds `tiles.py`'s `enc()` helper and `build_tile_data()`'s tile-index budget
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R104

## Purpose

The exact byte layout of a GBC tile and this project's current 256-tile budget, so a new tile is
authored in the correct format and slotted into a free index, not guessed.

## Scope

2bpp planar tile encoding, the tile-index space (OBJ vs. BG conventions this project uses), and
the current budget/allocation.

## Concepts

Each tile is an 8×8 grid of 2-bit color indices (0–3, selecting into one of the 4 colors of
whichever palette the tile/OBJ is assigned — R104), encoded as **16 bytes**: one row = 2 bytes,
stored as two separate "bitplanes" — the first byte holds bit 0 of every pixel in the row
(MSB = leftmost pixel), the second byte holds bit 1 of every pixel in the same row.[^1] A pixel's
final 2-bit color index is `bit1_from_byte2 << 1 | bit0_from_byte1`. This "row-major planar"
layout (not "one byte per pixel," not "both bitplanes interleaved per-pixel") is fixed by the
PPU's tile-fetch hardware and is the same for BG/Window tiles and OBJ tiles alike.

Tile indices are addressed two ways depending on LCDC bit 4 (R103): the **unsigned** `$8000`
method (index 0–255 → `$8000`+index×16, used by OBJs always and by BG/Window when LCDC.4=1) or
the **signed** `$8800` method (index treated as signed −128..127 relative to `$9000`, used by
BG/Window only when LCDC.4=0).[^2] This project's `LCDC=0x97` has bit 4 set, so BG/Window tiles
use the simple unsigned `$8000` addressing — the same scheme OBJs always use — meaning **one
flat 256-tile index space is shared by everything** (BG, Window, OBJ) with no signed/unsigned
split to reason about.

### Sources
[^1]: [Tile Data — Pan Docs](https://gbdev.io/pandocs/Tile_Data.html), accessed 2026-07-06.
[^2]: [LCD Control — Pan Docs](https://gbdev.io/pandocs/LCDC.html), accessed 2026-07-06.

## Operational Context

`tiles.py`'s `enc(pix)` helper is confirmed (direct code read) to implement exactly the
documented 2bpp planar format: for each of the 8 rows, it builds `p0` (bit-0 plane) and `p1`
(bit-1 plane) by testing `c & 1`/`c & 2` per pixel and setting bit `0x80 >> b` (MSB-first,
correctly matching "leftmost pixel = highest bit"), then appends `[p0, p1]` — 2 bytes per row, 16
bytes total per tile, in the same byte order Pan Docs describes.

The project's tile-index allocation (per `tiles.py`'s own header comment and constants) is: OBJ
tiles at `0x00`–`0x09` (bunny frames as 8×16 pairs at `0x00`–`0x03` per R105's tile-pairing
convention, carrot at `0x04`+blank `0x05`, star at `0x06`+blank `0x07`, flower at `0x08`+blank
`0x09`), UI tiles from `0x10` (hearts, icons, borders, arrows), and the remainder allocated to the
9 zones' BG art (sand/grass/snow/water/cobble/cave/dune/plains/castle-themed tiles) plus a font
range. The header comment states "9 visually distinct zones share one 256-tile bank" —
confirming the entire game's visual variety is packed into a single 256-entry index space with no
per-zone bank-switching of tile data (consistent with the current single-ROM-bank state, R106).

## Implementation Guidance

- **A new tile must be encoded via `enc()`, never hand-packed** — the helper is already correct
  and is the one place this format's bit-ordering logic lives; a hand-written 16-byte literal
  risks a subtle bit-order mistake that would only show up as visually-scrambled art.
- **A new tile needs a free index in the shared 256-slot space** — check `tiles.py`'s existing
  constant list for gaps before assigning a new `TL_*` value; the project does not currently
  partition the index space by zone, so a new zone's tiles compete for the same budget as every
  existing zone's tiles (this becomes a real constraint as MSTR-001 C7 grows the world — 256
  tiles total, already substantially allocated across 9 zones + OBJs + UI + font).
- **8×16 OBJ sprites still need even/odd adjacent-index pairs** (R105/R103) — this project's OBJ
  allocation already follows that convention (`0x00`/`0x01`, `0x02`/`0x03`, etc.); preserve it for
  any new sprite.
- **A tile budget audit belongs to GDS-07 (Data Model)** once authored — this topic supplies the
  *format* fact; the *how many tiles are actually free right now* fact needs a fresh count against
  the current `tiles.py` contents at that time, since it will have changed by then.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R104 (the palette each tile's 2-bit color indices select into) · R103 (LCDC bit 4's
addressing-mode choice, currently moot since this project always uses unsigned addressing) · R105
(OBJ tile-pairing convention in 8×16 mode).
