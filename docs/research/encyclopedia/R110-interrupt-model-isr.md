# R110 — Interrupt Model & ISR Conventions

- **Document ID:** R110 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (instruction/ISR-overhead costs), R102 (VBlank is the interrupt this
  project actually uses)
- **Referenced By:** R102, R105 (both describe the VBlank-gated safe window this interrupt creates)
- **Produces:** grounds `asm_game.py`'s RST-vector table and VBlank ISR at `0x0040`
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R101, R102, R105, R107 (joypad interrupt, unused)

## Purpose

The SM83 interrupt model — enable/flag registers, vector addresses, priority — so the project's
single-interrupt (VBlank-only) design is understood as a deliberate minimal choice, and any future
addition (STAT, timer, joypad, serial) is wired correctly against real vector addresses.

## Scope

IE/IF register semantics, the five interrupt sources and their fixed vectors, priority ordering,
and this project's current VBlank-only ISR implementation.

## Concepts

Two registers gate interrupts: **IE** (Interrupt Enable, `0xFFFF`) — one bit per source,
must be set for that source's handler to ever be invoked — and **IF** (Interrupt Flag, `0xFF0F`)
— set by hardware when a source's condition occurs (a pending request), independent of whether
IE permits it to fire yet.[^1] The five sources, in **priority order** (bit 0 highest), each with
a fixed vector address the CPU jumps to when the interrupt actually fires (`IME`=1 via `EI`, the
corresponding IE bit set, and the corresponding IF bit set):[^1]

| Bit | Source | Vector |
|---|---|---|
| 0 | VBlank | `$0040` |
| 1 | LCD (STAT) | `$0048` |
| 2 | Timer | `$0050` |
| 3 | Serial | `$0058` |
| 4 | Joypad | `$0060` |

VBlank fires once per frame at the start of Mode 1 (~59.7 Hz), at the highest priority of the
five.[^1] A CPU `RETI` both returns from the handler and re-enables `IME` in one instruction —
the standard way to end any ISR that doesn't need to stay in a nested-disabled state.

### Sources
[^1]: [Interrupts — Pan Docs](https://gbdev.io/pandocs/Interrupts.html), accessed 2026-07-06.

## Operational Context

`asm_game.py` fills the entire RST vector table (`$0000`–`$003F`) with `RETI` (a defensive no-op:
if a spurious RST instruction is ever executed, the ISR-return convention still holds harmlessly),
then places the real VBlank handler at `$0040` — matching the fixed vector address above exactly.
The handler is minimal by design: set `VBLANK_FLAG = 0xC012` to 1, `RETI`. Every other vector slot
(`$0048` LCD/STAT, `$0050` Timer, `$0058` Serial, `$0060` Joypad) is also filled with bare `RETI`
stubs — present so a stray/unexpected interrupt doesn't jump into arbitrary code, but none of
these sources are actually enabled or used.

Interrupts are globally enabled once, at boot, via `LD A,0x01; LD (0xFFFF),A` (writing IE with
only bit 0 — VBlank — set) followed by `EI` — confirming directly that **VBlank is the only
interrupt source this project has ever enabled**; STAT, Timer, Serial, and Joypad interrupts are
all present as inert vector stubs only. Game logic instead polls `VBLANK_FLAG` from the main loop
(spin-wait, then clear) rather than doing meaningful work inside the ISR itself — the ISR's only
job is to make "VBlank just started" observable to polling code, which is the safest possible
design (minimizes time spent with interrupts effectively "in use," minimizes ISR-reentrancy
concerns).

## Implementation Guidance

- **This project's one-interrupt-source design is deliberate and should stay minimal** — a future
  feature needing raster-timed effects (STAT/LYC) or precise sub-frame timing (Timer) is the
  first user of that vector; wire it by writing the correct IE bit (per the table above) and
  replacing that vector's `RETI` stub with real handler code, following the existing VBlank ISR's
  minimal-flag-set pattern rather than doing heavy work inside the handler.
- **Never do lengthy work directly inside an ISR.** The existing VBlank handler is a template:
  set a flag, return; let the main loop's polling do the actual graphics/logic work inside the
  VBlank-confirmed window (R102) that the flag identifies.
- **RST-vector `RETI` stubs are a safety net, not a specification of intended behavior** — if a
  future feature enables, say, the Timer interrupt, its stub at `$0050` must be replaced with real
  handler code (following the VBlank pattern: minimal work, set a flag, `RETI`), not left as a
  silent no-op that would swallow the interrupt.
- **Interrupt priority (VBlank highest) matters only once multiple sources are simultaneously
  pending** — irrelevant today (only one source is ever enabled) but becomes a real ordering fact
  the moment a second source is added.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R101 (ISR entry/exit is itself a cycle cost against the VBlank window's budget) · R102 (VBlank is
the PPU-mode event this interrupt observes) · R105 (OAM DMA timing is planned around the
VBlank-flag-confirmed window this interrupt creates) · R107 (the joypad interrupt source, present
as an unused vector stub).
