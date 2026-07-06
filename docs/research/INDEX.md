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
| R201 | [Top-down collect-a-thon structure & goal design](encyclopedia/R201-collectathon-goal-design.md) | goal hierarchies, gating, the 9-carrot victory shape | ✅ |
| R202 | [8-bit game feel](encyclopedia/R202-8bit-game-feel.md) | movement speed, animation cadence, collision tolerance norms | ✅ |
| R203 | [Screen composition on a 20×18 tile grid](encyclopedia/R203-screen-composition-tile-grid.md) | readability, landmarking, edges-as-exits | ✅ |
| R204 | [HUD & score-bar conventions](encyclopedia/R204-hud-score-bar-conventions.md) | row-0 UI bar patterns, icon+digit layouts | ✅ |
| R205 | [Save-system design & player expectations](encyclopedia/R205-save-system-design.md) | battery saves, auto-load, save menus | ✅ |
| R206 | [Difficulty, pacing & session length for handheld play](encyclopedia/R206-difficulty-pacing-session-length.md) | zone sizing, collectible density | ✅ |
| R207 | [GB-era chiptune composition & audio feedback cues](encyclopedia/R207-gb-chiptune-composition.md) | melody conventions, jingles, note-length feel | ✅ |
| R208 | [Palette & color design under CGB constraints](encyclopedia/R208-palette-color-design.md) | 4-color-per-palette design, 8-palette budgets | ✅ |
| R209 | [Pixel art technique at 8×8/2bpp scale](encyclopedia/R209-pixel-art-technique.md) | silhouette-first design, color-per-part budgeting, outline use (filed via `BL-0013`) | ✅ |
| R210 | [AI/agent-assisted tile-art generation & iteration workflow](encyclopedia/R210-ai-assisted-tile-art-workflow.md) | design→encode→render→review→revise loop for this project's own tooling (filed via `BL-0013`) | ✅ |
| R211 | [Comparative case studies: acclaimed GBC/GBC-era visual design](encyclopedia/R211-acclaimed-gbc-visual-design-case-studies.md) | Oracle of Seasons/Ages, Shantae, Pokémon Gold/Silver, DKC (GBC) (filed via `BL-0013`) | ✅ |

## Tier R300 — Tooling, Emulation & Verification (`02-research-tooling-and-testing`)

| ID | Topic | Scope (one line) | Status |
|---|---|---|---|
| R301 | [PyBoy headless API](encyclopedia/R301-pyboy-headless-api.md) | memory access, button input, ticks, screenshots, `.ram` saves | ✅ |
| R302 | [Python-assembler codegen patterns](encyclopedia/R302-python-assembler-codegen-patterns.md) | label resolution, patch-point dicts, section layout | ✅ |
| R303 | [2bpp tile encoding & palette data formats](encyclopedia/R303-2bpp-tile-encoding.md) | bitplanes, attribute maps, byte costs, the 256-tile budget | ✅ |
| R304 | [ROM validation](encyclopedia/R304-rom-validation.md) | header checksum, size, cart-type fields; why T1 survives the BL-0006 rewrite | ✅ |
| R305 | [Emulator-based test design](encyclopedia/R305-emulator-based-test-design.md) | memory vs. pixel assertions, frame determinism, save harnesses; **the concrete BL-0006 rewrite target** | ✅ |
| R306 | [Toolchain portability](encyclopedia/R306-toolchain-portability.md) | path conventions; **the concrete BL-0005 rewrite target** | ✅ |

The planned-topic lists are suggestions recorded at scaffold time — the owning skill adjusts them
to real gaps (adding/retitling rows) as grounding needs emerge; keep this index the single source
of tier truth.
