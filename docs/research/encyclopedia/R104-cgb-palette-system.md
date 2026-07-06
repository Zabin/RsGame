# R104 — CGB Palette System (BCPS/BCPD, OCPS/OCPD, RGB15)

- **Document ID:** R104 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R102 (palette-write access-timing constraint)
- **Referenced By:** R108's sibling content topics (each Bunny Quest zone has its own BG palette)
- **Produces:** grounds `gbc_lib.py`'s `rgb15()` helper and `build_rom.py`'s palette tables
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R102, R103

## Purpose

The exact register sequence and color encoding for CGB palettes, so a new zone's palette (or a
future palette-budget expansion past the current 8 BG + 8 OBJ) is written correctly the first
time.

## Scope

RGB15 color encoding, the BCPS/BCPD (background) and OCPS/OCPD (object) index+data register pair,
auto-increment behavior, and this project's current palette budget/usage.

## Concepts

CGB colors are stored as **RGB555**: three 5-bit components (0–31 each) packed into a 15-bit
value, conventionally written as a 16-bit little-endian pair (bit 15 unused).[^1] The CGB provides
**8 background palettes and 8 object (sprite) palettes**, each holding 4 colors (color 0 of an
OBJ palette is always transparent), selected per-tile via the BG tile's attribute byte or per-OBJ
via its OAM attribute byte.[^1]

Palette RAM is written indirectly through an index+data register pair, not addressed directly:
`BCPS`/`BGPI` (`0xFF68`) selects a byte offset into background palette memory (0–63, two bytes
per color × 4 colors × 8 palettes) and `BCPD`/`BGPD` (`0xFF69`) reads/writes the byte at that
offset; `OCPS`/`OBPI` (`0xFF6A`) and `OCPD`/`OBPD` (`0xFF6B`) are the equivalent pair for object
palettes.[^1] Setting the auto-increment bit (bit 7) of the index register causes the index to
advance automatically after each data write — the standard way to stream a whole palette table
without re-issuing the index write per byte.[^1] Palette data writes are blocked during PPU mode 3
(R102), same as VRAM.

### Sources
[^1]: [Palettes — Pan Docs](https://gbdev.io/pandocs/Palettes.html), accessed 2026-07-06.

## Operational Context

`gbc_lib.py`'s `rgb15(r, g, b)` helper packs three 0–31 components into the RGB15 encoding Pan
Docs describes — every color constant in `build_rom.py` (e.g. `_c(28,30,26)` for sky, per zone
palette) is built through this one helper, so the encoding itself is centralized and correct by
construction; what varies per-zone is only the *palette table contents*.

Per the Bunny Quest rewrite (`679b5cf`), the game now uses **8 BG palettes**, one per zone theme
(sand/water for Beach, grass for Forest, snow for Mountain, deep water for Lake, cobble for
Village, cave-dark for Cave, dune for Desert, plains-grass for Plains, brick/gold for Castle —
nine zones sharing eight BG palette slots, since Beach/Desert or similar pairs likely share a
palette index; confirm the exact zone→palette assignment against `build_rom.py`'s palette table
before citing a specific mapping in a future FS). This is already at the CGB's per-layer palette
ceiling (8 BG / 8 OBJ) — **there is no palette headroom left for a ninth or later distinctly-
palette'd zone** without either reusing an existing palette across two zones (already true for at
least one pair) or accepting less distinct per-zone tinting.

## Implementation Guidance

- **The 8 BG / 8 OBJ palette ceiling is hardware-fixed, not a `gbc_lib.py` limitation.** Growing
  the world past nine zones (per MSTR-001 C7's long-term target) means new zones will need to
  **share** an existing BG palette with a similar-toned zone, or the project accepts visually
  repeated zone tinting — this is a real, near-term design constraint for GDS-01/GDS-08 to state
  explicitly, not a detail to defer.
- **Any new palette write must happen inside a VBlank-safe window** (R102) — write the index
  register, then stream color bytes through the data register with auto-increment set, entirely
  before the next mode-3 begins if done outside LCD-off initialization.
- **OBJ palette color 0 is always transparent** — a sprite tile's color-index-0 pixels show
  through to the BG regardless of what's stored in that palette slot; don't waste a meaningful
  color there.
- **Use `rgb15()` for every new color constant** — never hand-compute the packed value; this is
  the one existing safety net against an encoding mistake.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R102 (write-timing constraint shared with all VRAM/OAM access) · R103 (LCDC/attribute bits select
which of the 8 palettes a given BG tile or OBJ uses).
