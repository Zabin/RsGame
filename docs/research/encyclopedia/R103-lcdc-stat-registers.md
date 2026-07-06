# R103 — LCDC/STAT Registers

- **Document ID:** R103 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R102 (PPU modes these registers control/report)
- **Referenced By:** R105 (LCDC bit 2 sets OBJ size, load-bearing for the bunny-sprite fix)
- **Produces:** grounds `asm_game.py`'s `LCDC=0x97`/`0x93` writes
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R102, R105

## Purpose

Exact bit meanings for `LCDC` (`0xFF40`) and `STAT` (`0xFF41`) so a future LCDC value change (e.g.
enabling the window layer, or a different OBJ size) is deliberate, not a guess at "which bit was
that again."

## Scope

`LCDC` bit-by-bit; `STAT`'s mode bits and interrupt-select bits; the specific values this project
already uses and why.

## Concepts

**LCDC (`0xFF40`, LCD Control)** — each bit toggles a display element:[^1]

| Bit | Name | Meaning when set |
|---|---|---|
| 7 | LCD/PPU enable | Display on; clearing it grants immediate full VRAM/OAM access (R102) |
| 6 | Window tile map area | Window uses `0x9C00` instead of `0x9800` |
| 5 | Window enable | Window layer displayed |
| 4 | BG/Window tile data area | Tiles addressed from `0x8000` (unsigned) instead of `0x8800` (signed, "method 2") |
| 3 | BG tile map area | BG uses `0x9C00` instead of `0x9800` |
| 2 | OBJ size | Sprites are 8×16 (stacked pair) instead of 8×8 |
| 1 | OBJ enable | Sprites displayed |
| 0 | BG/Window enable (DMG); priority-related on CGB | Clearing it blanks BG/Window on DMG; on CGB this bit instead controls BG-vs-OBJ priority ordering, and BG/Window are never actually blanked |

**STAT (`0xFF41`, LCD Status)** — bits 0–1 report the current PPU mode (read-only, reads 0 while
the PPU is disabled); bit 2 is the read-only LYC==LY coincidence flag; bits 3–6 are read/write
interrupt-select enables for mode-0, mode-1, mode-2, and the LYC-coincidence STAT interrupt
sources respectively.[^2]

### Sources
[^1]: [LCD Control — Pan Docs](https://gbdev.io/pandocs/LCDC.html), accessed 2026-07-06.
[^2]: [LCD Status Registers — Pan Docs](https://gbdev.io/pandocs/STAT.html), accessed 2026-07-06.

## Operational Context

`asm_game.py` writes `LCDC` twice with the value `0x97` (both at initial boot and when
re-enabling the LCD after the SAVE-menu's LCD-off period), and writes `0x00` (via `XOR_A;
LDH (LCDC),A`) to turn the display off.[^1] Decoding `0x97` = `1001 0111`: bit 7 (LCD on) = 1,
bit 4 (BG/Window tile data `0x8000` addressing) = 1, bit 2 (**OBJ size = 8×16**) = 1, bit 1 (OBJ
enable) = 1, bit 0 (BG/Window enable) = 1; bits 6/5/3 (window map/enable, BG map area) = 0 (no
window layer used; BG uses `0x9800`).

This is a **direct, load-bearing fact about a real bug this project already had and fixed**:
`Claude.md`'s "Bugs Fixed vs v1" originally recorded `LCDC = 0x91` (bit 1 OBJ-enable **missing**,
sprites invisible) as the v1 defect, and a later commit (`9a587ac`, "Fix invisible bunny: 8x16 OBJ
mode + WRAM clear bug") moved the project to `0x97` — enabling bit 2 (8×16 OBJ mode) on top of the
fix, not just correcting the missing OBJ-enable bit. `STAT` is not written anywhere in the current
code — this project does not use STAT interrupts (no mode-0/1/2/LYC-driven raster effects); all
timing is driven purely by the VBlank interrupt (R110).

## Implementation Guidance

- **Never disable bit 1 (OBJ enable) when writing LCDC** — this is the exact class of bug
  `Claude.md`'s bug history already recorded once (v1's `0x91`); any future LCDC value change
  should be decoded bit-by-bit against the table above before committing to it, not copy-pasted
  from a similar-looking hex literal.
- **8×16 OBJ mode (bit 2 = 1) changes OAM semantics**, not just LCDC: an OBJ's tile index in OAM
  is treated as an *even* index, with the next tile immediately following as the bottom half — see
  R105 for the OAM-entry-layout consequence. Do not flip bit 2 without also checking every OAM
  write assumes the matching (8×8 or 8×16) tile-pairing convention.
- **A future window-layer feature** (bits 5/6) would need its own tilemap allocation distinct from
  the BG's `0x9800`/`0x9C00` choice (bit 3) — currently unused, so introducing it is a real new
  VRAM-budget line item for GDS-07 (Data Model) to account for, not a free toggle.
- **This project does not use STAT interrupts.** A future feature needing raster-timed effects
  (e.g. a split-screen HUD via an LYC interrupt) would be the first user of STAT's interrupt-select
  bits and needs its own IE/IF wiring (see R110) — nothing in the current codebase can be copied
  as a starting point.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R102 (the modes STAT reports and LCDC bit 7 gates) · R105 (OBJ size bit's OAM-layout consequence).
