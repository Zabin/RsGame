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
| R101 | [SM83 instruction set & cycle costs](encyclopedia/R101-sm83-instruction-set.md) | opcode semantics/timings `gbc_lib.py` emitters must honor | ✅ |
| R102 | [PPU modes, VBlank & VRAM/OAM access timing](encyclopedia/R102-ppu-vram-oam-timing.md) | when VRAM/OAM writes are safe; why the VBlank ISR pattern exists | ✅ |
| R103 | [LCDC/STAT registers](encyclopedia/R103-lcdc-stat-registers.md) | bit meanings, the current LCDC=0x97 configuration (8x16 OBJ), mode interrupts | ✅ |
| R104 | [CGB palette system](encyclopedia/R104-cgb-palette-system.md) | BCPS/BCPD, OCPS/OCPD, RGB15 encoding, palette upload discipline | ✅ |
| R105 | [OAM, sprites & OAM DMA](encyclopedia/R105-oam-sprites-dma.md) | OAM entry format, shadow-OAM DMA, 8x8 vs 8x16 modes, priority | ✅ |
| R106 | [MBC1, SRAM enable & battery saves](encyclopedia/R106-mbc1-sram-battery-saves.md) | cart type 0x03, RAM enable sequence, save persistence, banking (C7 growth path) | ✅ |
| R107 | [Joypad register & dual-read settling](encyclopedia/R107-joypad-register.md) | P1 matrix, settle delays, the v1 bug class | ✅ |
| R108 | [APU channels & register map](encyclopedia/R108-apu-channels-registers.md) | pulse channels, frequency encoding, the music engine's surface | ✅ |
| R109 | [Cartridge header, checksums & boot](encyclopedia/R109-cartridge-header-checksums.md) | header fields, checksum algorithms, GBC flag | ✅ |
| R110 | [Interrupt model & ISR conventions](encyclopedia/R110-interrupt-model-isr.md) | IE/IF, vector table, RETI discipline, VBLANK_FLAG pattern | ✅ |

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
