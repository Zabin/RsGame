# R105 — OAM, Sprites & OAM DMA

- **Document ID:** R105 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (DMA timing budget), R102 (access-window rules), R103 (LCDC OBJ-size bit)
- **Referenced By:** R110 (the VBlank ISR is what makes DMA timing safe), R115 (2026-07-17 —
  the OAM entry format/40-entry budget this topic establishes grounds the combat sub-mode's own
  concurrent-sprite headroom arithmetic, `BL-0133`)
- **Produces:** grounds `asm_game.py`'s `OAM_BUF`/`HRAM_DMA`/sprite-write routines
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R101, R102, R103, R110

## Purpose

OAM entry format, why this project DMA's a shadow buffer every frame instead of writing OAM
directly, and the exact fixed cost of that DMA — the thing an agent must not accidentally break
while adding a new sprite type.

## Scope

OAM entry layout (Y/X/tile/attributes), 8×8 vs. 8×16 OBJ-size semantics, the OAM DMA transfer
mechanism and its fixed timing cost, and this project's shadow-buffer convention.

## Concepts

Each of the 40 OAM entries is 4 bytes: **Y position** (actual Y + 16, so Y=16 places the sprite's
top at screen row 0), **X position** (actual X + 8), **tile index**, and an **attributes** byte
(priority, Y/X flip, palette selection — DMG palette bit and CGB palette-number bits 0–2, plus a
CGB VRAM-bank-select bit).[^1] In **8×16 mode** (LCDC bit 2 set, R103), the tile index's least
significant bit is ignored/forced to 0: the indexed tile is the top half, and `index+1` is always
the bottom half, drawn immediately below — sprites in this mode are conventionally allocated as
adjacent even/odd tile-index pairs.[^2]

**OAM DMA** (triggered by writing the high byte of a source address to `DMA`, `0xFF46`) copies
160 bytes (all 40 entries) from `XX00`–`XX9F` (where `XX` is the written byte) into OAM
automatically, taking a fixed **160 M-cycles** (~154 µs) during which the CPU may only access
**HRAM** (`0xFF80`–`0xFFFE`) — this is why the standard idiom is a small HRAM routine that kicks
off the DMA and then spin-waits in HRAM until it completes, rather than the CPU touching any
other memory mid-transfer.[^3] OAM itself is inaccessible to direct CPU writes during modes 2/3
regardless of DMA (R102); DMA is not exempt from that timing rule for *reads of OAM*, but it *is*
the standard way to update all 40 entries within a single VBlank instead of writing OAM directly
during the HBlank/VBlank windows one entry at a time.

### Sources
[^1]: [OAM DMA Transfer — Pan Docs](https://gbdev.io/pandocs/OAM_DMA_Transfer.html), accessed 2026-07-06 (entry layout cross-referenced from the same page's linked OAM description).
[^2]: [LCD Control — Pan Docs](https://gbdev.io/pandocs/LCDC.html), accessed 2026-07-06.
[^3]: [OAM DMA Transfer — Pan Docs](https://gbdev.io/pandocs/OAM_DMA_Transfer.html), accessed 2026-07-06.

## Operational Context

`asm_game.py` implements exactly the HRAM-routine idiom: at boot, a small DMA-wait routine is
copied into HRAM at `HRAM_DMA = 0xFF80`; every frame, once `VBLANK_FLAG` confirms the safe window,
the code writes the shadow buffer's high byte (`OAM_BUF >> 8`, where `OAM_BUF = 0xC300`) to `DMA`
and calls the HRAM routine to spin-wait out the transfer.[^3] The shadow buffer is cleared to zero
at boot (`LD HL,OAM_BUF; LD B,160; XOR A` loop) and again at each screen-redraw boundary before
being repopulated — the player sprite's two OAM entries are written as `Y = PLAYER_Y + 16, X =
PLAYER_X + 8` (confirming the R105 Y+16/X+8 encoding directly against this project's own code).

Since `9a587ac` ("Fix invisible bunny: 8x16 OBJ mode + WRAM clear bug"), the player sprite uses
**8×16 OBJ mode** (LCDC bit 2 set, per R103) — meaning the player's tile-index allocation must
follow the even/odd adjacent-pair convention described above; a future sprite-art change (backlog
`BL-0002`, currently flagged for re-verification) that assumes 8×8 semantics would silently
mis-render if 8×16 mode is still active.

## Implementation Guidance

- **Every new sprite (collectible OBJ, a future NPC, etc.) is written into the shadow buffer
  (`OAM_BUF`), never directly to OAM** — the existing per-frame DMA already flushes the whole
  buffer; a direct OAM write from outside the DMA'd VBlank window risks hitting mode 2/3's OAM
  lockout (R102).
- **Respect the current OBJ-size mode when allocating new sprite tile indices.** With LCDC bit 2
  set (8×16, current state), any new sprite's tile index must be even, with its bottom-half tile
  immediately following at `index+1` — allocate tile-index pairs, not singles.
- **40 OAM entries is the hard ceiling.** Collectibles + player + any future sprite type all share
  this budget; a scene with many simultaneous collectibles (relevant as MSTR-001 C7's world grows)
  needs an explicit budget check against 40, not an assumption that "OAM has room."
- **Never issue the DMA kickoff outside the VBlank-confirmed window** (R102) — the 160 M-cycle
  transfer itself is safe to run across the mode-2/3 boundary once started (Pan Docs' documented
  behavior), but *starting* it should still happen from the same VBlank-flag-gated point the rest
  of the frame's graphics work uses, to keep the whole frame's timing predictable.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R101 (the DMA's 160 M-cycle cost is a cycle-budget fact) · R102 (the access-window rule DMA is
built to respect) · R103 (LCDC bit 2's OBJ-size semantics, load-bearing for tile-pair allocation)
· R110 (the VBlank interrupt flag is what gates when DMA may safely start).
