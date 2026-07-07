# R102 — PPU Modes, VBlank & VRAM/OAM Access Timing

- **Document ID:** R102 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (cycle-cost units)
- **Referenced By:** R103 (LCDC/STAT drive PPU mode), R104 (palette write timing), R105 (OAM DMA
  timing), R110 (VBlank ISR is this topic's central safe window)
- **Produces:** grounds `asm_game.py`'s VBlank ISR (`0x0040`) and every VRAM/tilemap/OAM write
  routine
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R103, R104, R105, R110

## Purpose

When VRAM and OAM are safe to touch from the CPU — the single most important timing fact for a
GBC game, and the exact reason `asm_game.py`'s VBlank ISR pattern exists at all.

## Scope

The four PPU modes, their CPU-access rules, VBlank's duration and use as the standard "do
graphics work now" window, and how this project's shadow-buffer + VBlank-flag pattern satisfies
the constraint.

## Concepts

The PPU cycles through four modes per scanline (and one long mode across all 10 "extra" lines
144–153):

| Mode | Name | VRAM (CPU) | OAM (CPU) | Notes |
|---|---|---|---|---|
| 0 | HBlank | accessible | accessible (direct or DMA) | shortest mode, ends each visible line |
| 1 | VBlank | accessible | accessible (direct or DMA) | lines 144–153, ~4560 T-states total |
| 2 | OAM Scan | accessible | **not accessible** to CPU | PPU reads OAM 1 entry/M-cycle |
| 3 | Pixel Transfer | **not accessible** | **not accessible** | PPU actively rendering |

While the display is off entirely (`LCDC` bit 7 = 0), both VRAM and OAM are freely accessible
regardless of mode.[^1] Modes 2 and 3 block **all** CPU OAM access; mode 3 additionally blocks
VRAM and CGB palette-data access.[^1][^2]

VBlank occurs once per frame (~59.7 Hz on DMG/CGB) starting at scanline 144 and lasts through line
153 before the next frame's mode 2 begins — this is the one guaranteed multi-scanline window
where **both** VRAM and OAM are simultaneously writable, which is why it is the standard "flip
your buffers now" point for any GBC game.[^3]

### Sources
[^1]: [Accessing VRAM and OAM — Pan Docs](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html), accessed 2026-07-06.
[^2]: [Rendering — Pan Docs](https://gbdev.io/pandocs/Rendering.html), accessed 2026-07-06.
[^3]: [Interrupt Sources — Pan Docs](https://gbdev.io/pandocs/Interrupt_Sources.html), accessed 2026-07-06.

## Operational Context

`asm_game.py` implements exactly this pattern. The VBlank ISR (installed at `0x0040`, the
hardware vector Pan Docs documents[^3]) does the minimum possible: it sets a WRAM flag
(`VBLANK_FLAG = 0xC012`) to 1 and returns via `RETI`.[^1 in R110] The main loop spin-waits on that
flag (`rom.LD_A_nn(VBLANK_FLAG); rom.OR_A()` in a loop, then clears it), and only *inside* that
confirmed-VBlank window does it perform the OAM DMA kickoff (`LD A,(OAM_BUF>>8); LDH (DMA),A` —
see R105) and any tilemap/attribute writes the frame needs. This is the textbook safe pattern: do
nothing graphics-related outside the flag-confirmed window.

The known-fixed v1 bug this project already hit (recorded in `Claude.md`'s "Bugs Fixed vs v1" and
still tracked as backlog `BL-0003`/part of `BL-0008`) — "score display writes during LCD-on" —
is exactly a violation of this rule: a VRAM tilemap write issued without confirming VBlank (or
LCD-off) first, which is *usually* invisible on emulator (PyBoy doesn't always model the exact
mode-3 VRAM-block penalty as strictly as hardware) but is a genuine correctness bug against real
silicon.

## Implementation Guidance

- **Any new VRAM write** (a tilemap patch, a BG-attribute change, a new screen's initial draw) must
  happen either (a) with the LCD off (`LCDC` bit 7 = 0, e.g. during `init_video` before the first
  `LD A,0x97; LDH (LCDC),A`), or (b) inside the VBlank-flag-confirmed window in the main loop — never
  from an arbitrary point in game logic that doesn't know the current PPU mode.
- **Any new OAM write** (a new sprite type, more OAM entries) is safe in HBlank or VBlank, or via
  DMA (see R105) — never during OAM Scan/Pixel Transfer. The existing shadow-OAM-buffer + DMA
  pattern (`OAM_BUF = 0xC300`, DMA'd every VBlank) already satisfies this for all sprite writes;
  extend that buffer, don't write OAM (`0xFE00`–`0xFE9F`) directly from game logic.
- **Fixing BL-0003/BL-0008's score-write finding:** locate the score-bar VRAM write call site in
  the current `asm_game.py` and gate it behind the same `VBLANK_FLAG` check the rest of the frame
  loop already uses — do not introduce a second, parallel "is it safe now" mechanism.
- **CGB palette writes (BCPS/BCPD, OCPS/OCPD) are also blocked during mode 3**[^2] — see R104 for
  the palette-specific register sequence; the timing rule here (VBlank-or-LCD-off) is identical.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R103 (LCDC controls the mode-0 bit / display-on bit this topic's rules key off) · R104 (palette
writes share this exact access-window constraint) · R105 (OAM DMA is *the* practical way to update
40 sprites within one VBlank) · R110 (the VBlank interrupt is the mechanism that makes "confirmed
VBlank" observable to the CPU at all).
