# ADR-0011 — MBC1 default-wiring ROM bank switching (supersedes ADR-0001's single-bank scope)

**Status:** Accepted (2026-07-09) — **supersedes [ADR-0001](ADR-0001-single-bank-rom-no-mbc-switching.md)**

## Context

[ADR-0001](ADR-0001-single-bank-rom-no-mbc-switching.md) explicitly anticipated its own
supersession: "this decision does not survive C7 unmodified... this ADR is explicitly superseded
when that work is planned." [MSTR-001](../../master/MSTR-001-program-vision.md) v3.0's **C8**
(presentation quality, more biome tile sets) and **C10** (procedural world generation, new
generator code) are the first *named, concrete* consumers of the ~9.1 KiB headroom ADR-0001 left
unplanned-for — strategic assumption **A1** was sharpened at v3.0 specifically to record this:
"the bar is lowered again — C9's expanded biome tile sets and C10's generator code are named,
concrete consumers of the remaining headroom, not a hypothetical future one." This is that
planned work.

[R106](../../research/encyclopedia/R106-mbc1-sram-battery-saves.md) already grounds MBC1's two
wiring modes: the **default wiring** (32 banks × 16 KiB = 512 KiB ROM, RAM banking intact, a
5-bit bank-select register at `$2000`–`$3FFF`) versus the **large-ROM alternate wiring** (extends
ROM addressing to 2 MiB at the cost of RAM banking, toggled via `$6000`–`$7FFF`). R106's own
Implementation Guidance already named the default wiring as "the natural first step... requires
the *least* change to the existing single-RAM-bank save format," reserving the alternate wiring
for a ROM need exceeding 512 KiB. Cart type `0x03` (MBC1+RAM+BATTERY) is already declared in the
header ([ADR-0006](ADR-0006-mbc1-ram-battery-cart-type.md)) — the hardware capability has been
present, unused, since the project's first build.

## Decision

**Adopt MBC1's default wiring**: up to 512 KiB ROM across 32 banks of 16 KiB (bank 0 fixed at
`$0000`–`$3FFF`, a selected bank at `$4000`–`$7FFF` via the `$2000`–`$3FFF` register), **RAM
banking left unused** (the existing single 8 KiB SRAM bank, `ramsize=0x02`, is untouched — this
project's save data does not need RAM banking, only ROM banking).

**Bank layout strategy**: bank 0 carries the fixed-address requirements — the interrupt vector
table, the VBlank ISR, the entry point, and the core game-logic code path that must be reachable
regardless of which `ROMX` bank is currently selected (the main loop, state dispatch, the
world-generator routine from [ADR-0009](ADR-0009-screen-graph-world-generation.md), and the PRNG
from [R111](../../research/encyclopedia/R111-wram-banking-sm83-prng.md)). Content that is
selected *by* the generator rather than *driving* it — biome-specific tile sets, per-biome
terrain templates, expanded music data — is the natural candidate for `ROMX` banks, since it is
addressed through data lookups (already patch-point-mediated, per
[R302](../../research/encyclopedia/R302-python-assembler-codegen-patterns.md)) rather than
inline-jumped-to code. **Exact bank assignment (which biome families/content go in which bank)
is deferred to the implementation package that actually grows content past the single-bank
ceiling** — this ADR commits to the wiring and the code/data split principle, not a byte-level
bank map, consistent with this level's own altitude (ADR-0001 set the same precedent: record the
strategy, not the implementation).

**Trigger for actually cutting over**: per R106's own framing (reaffirmed here), the cutover
happens **when a specific package's content genuinely cannot fit remaining bank-0 headroom** —
this ADR commits to the *strategy* now (so the eventual cutover is planned, not improvised,
exactly as R106 originally recommended) but does not mandate immediate implementation. The
increment's own content (generator code, R213's recommendation) is expected to be ROM-*cheap*
(code, not large map data — ADR-0009's consequence) — the more likely trigger is C9's expanded
biome tile sets once GDS-08's presentation delta sizes them.

**MBC1's bank-0-unselectable quirk** (a write of `0` to the `$2000`–`$3FFF` register is treated
as `1`, per R106) applies to whatever bank-numbering scheme the eventual implementation package
adopts — noted here so that package does not rediscover it as a bug.

## Consequences

- **`gbc_lib.py`'s `ROM` class needs new opcode-emission methods** for the MBC1 bank-select write
  (`LD (0x2000),A`-style bank writes) — R106 already flagged this gap; this ADR confirms it is
  now committed, not merely hypothetical.
- **`build_rom.py`'s layout needs a bank-aware section scheme** — today's `build()` lays out one
  flat 32 KiB buffer; a banked build needs to track which bank each section belongs to and emit
  bank-boundary padding, a real but bounded extension to the existing section-layout code.
- **`R302`'s patch-point mechanism needs bank-relative addressing** — a simple flat 16-bit patch
  (today's `p16` helper) is insufficient once code/data can live in different banks; R302's own
  Implementation Guidance already anticipated this exact extension ("a future bank-switched ROM
  would need `p16`'s helper (or a sibling) to also handle bank-relative addressing").
- **`test_rom.py`'s T1 header-validation suite is unaffected** — per
  [R304](../../research/encyclopedia/R304-rom-validation.md), header/checksum validation does not
  change shape when `rsize` moves off `0x00`; only the specific expected `rsize` value changes
  once a package actually grows past 32 KiB.
- **ADR-0001 is superseded, not deleted** — its "no bank-switching, single fixed bank" scope
  applied to the bootstrap-through-v2.0 increment and remains historically accurate for that
  period; this ADR records the planned transition ADR-0001 itself named as its own trigger.
- **Does not implement anything** — the `gbc_lib.py`/`build_rom.py`/`R302` extensions ship
  through the normal `04`→`08` path once a concrete package needs the headroom, gated by G3.
