# Research — Index

The research encyclopedia grounds specs and packages in cited fact. Three tiers, one owning skill
each; topics live under `docs/research/encyclopedia/`. **Index-before-content:** a topic gets its
row here (⛔ Planned) before its file is written; the row flips ✅ only when the owning skill's
quality gate passes. The methodology (seven-section shape, inline citations, `### Sources` per
section, 3–8 page band) is embedded in each `02-research-*` skill.

[↑ Docs index](../INDEX.md)

## Tier R100 — GBC Hardware & SM83 (`02-research-gbc-hardware`)

| ID | Topic | Scope (one line) | Status |
|---|---|---|---|
| R101 | SM83 instruction set & cycle costs | opcode semantics/timings `gbc_lib.py` emitters must honor | ⛔ Planned |
| R102 | PPU modes, VBlank & VRAM/OAM access timing | when VRAM/OAM writes are safe; why the VBlank ISR pattern exists | ⛔ Planned |
| R103 | LCDC/STAT registers | bit meanings, the LCDC=0x93 configuration, mode interrupts | ⛔ Planned |
| R104 | CGB palette system | BCPS/BCPD, OCPS/OCPD, RGB15 encoding, palette upload discipline | ⛔ Planned |
| R105 | OAM, sprites & OAM DMA | OAM entry format, shadow-OAM DMA, 8x8 vs 8x16 modes, priority | ⛔ Planned |
| R106 | MBC1, SRAM enable & battery saves | cart type 0x03, RAM enable sequence, save persistence | ⛔ Planned |
| R107 | Joypad register & dual-read settling | P1 matrix, settle delays, the v1 bug class | ⛔ Planned |
| R108 | APU channels & register map | pulse channels, frequency encoding, the music engine's surface | ⛔ Planned |
| R109 | Cartridge header, checksums & boot | header fields, checksum algorithms, GBC flag | ⛔ Planned |
| R110 | Interrupt model & ISR conventions | IE/IF, vector table, RETI discipline, VBLANK_FLAG pattern | ⛔ Planned |

## Tier R200 — Game Design (`02-research-game-design`)

| ID | Topic | Scope (one line) | Status |
|---|---|---|---|
| R201 | Top-down collect-a-thon structure & goal design | goal hierarchies, gating, the gifts→victory shape | ⛔ Planned |
| R202 | 8-bit game feel | movement speed, animation cadence, collision tolerance norms | ⛔ Planned |
| R203 | Screen composition on a 20×18 tile grid | readability, landmarking, edges-as-exits | ⛔ Planned |
| R204 | HUD & score-bar conventions | row-0 UI bar patterns, icon+digit layouts | ⛔ Planned |
| R205 | Save-system design & player expectations | battery saves, auto-load, save menus | ⛔ Planned |
| R206 | Difficulty, pacing & session length for handheld play | zone sizing, collectible density | ⛔ Planned |
| R207 | GB-era chiptune composition & audio feedback cues | melody conventions, jingles, note-length feel | ⛔ Planned |
| R208 | Palette & color design under CGB constraints | 4-color-per-palette design, 8-palette budgets | ⛔ Planned |

## Tier R300 — Tooling, Emulation & Verification (`02-research-tooling-and-testing`)

| ID | Topic | Scope (one line) | Status |
|---|---|---|---|
| R301 | PyBoy headless API | memory access, button input, ticks, screenshots, `.ram` saves | ⛔ Planned |
| R302 | Python-assembler codegen patterns | label resolution, patch-point dicts, section layout | ⛔ Planned |
| R303 | 2bpp tile encoding & palette data formats | bitplanes, attribute maps, byte costs | ⛔ Planned |
| R304 | ROM validation | header checksum, size, cart-type fields | ⛔ Planned |
| R305 | Emulator-based test design | memory vs. pixel assertions, frame determinism, save harnesses | ⛔ Planned |
| R306 | Toolchain portability | path conventions, CI-friendly builds, cross-checking emulators | ⛔ Planned |

The planned-topic lists are suggestions recorded at scaffold time — the owning skill adjusts them
to real gaps (adding/retitling rows) as grounding needs emerge; keep this index the single source
of tier truth.
