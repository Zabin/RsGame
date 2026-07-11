# R101 — SM83 Instruction Set & Cycle Costs

- **Document ID:** R101 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** none (foundation topic)
- **Referenced By:** R102, R105, R110 (ISR/DMA timing budgets), every future GDS/FS/IP touching `gbc_lib.py`
- **Produces:** grounds `gbc_lib.py` (opcode emitter methods), every `asm_game.py` routine
- **Feature Mapping:** *(none yet — no FS-xxx authored)*
- **Related Topics:** R102 (PPU timing budgets consume these cycle costs), R110 (ISR entry/exit costs)

## Purpose

What the SM83 CPU's opcode set actually costs in cycles, and which opcodes `gbc_lib.py` currently
emits — so an agent adding a new `ROM` method or budgeting a VBlank-window routine picks the right
instruction, not a plausible-looking one.

## Scope

Opcode encoding shape, cycle-cost units (M-cycles vs. T-states), the four illegal/lock-up
opcodes, and the concrete subset `gbc_lib.py` implements today.

## Concepts

The SM83 (the CPU core in DMG/CGB, a customized Z80-derivative — not a stock Z80 or 8080) uses a
variable-length instruction encoding: the first byte is the opcode; some opcodes take one or two
immediate operand bytes. Instructions are grouped into four "blocks" by the top two bits of the
opcode byte.[^1] Timing is conventionally given in **M-cycles** (machine cycles); one M-cycle = 4
**T-states** (clock ticks) at the Game Boy's ~4.194304 MHz system clock, so 1 M-cycle ≈ 0.954 µs.
A `NOP` costs 1 M-cycle; most 8-bit loads cost 1–2 M-cycles; 16-bit loads and calls cost more
(`CALL` is 6 M-cycles taken, 3 not taken).[^1]

Ten opcodes are **illegal and hard-lock the CPU** until power-cycle: `$D3, $DB, $DD, $E3, $E4,
$EB, $EC, $ED, $F4, $FC, $FD`.[^1] None of these are reachable through any `gbc_lib.py` emitter
method today (every method hardcodes a specific valid opcode byte), but a future contributor
adding raw-byte emission (e.g. a generic `emit_opcode(n)` escape hatch) must guard against this
set explicitly — the CPU gives no warning, just silent lock-up.

### Sources
[^1]: [CPU Instruction Set — Pan Docs](https://gbdev.io/pandocs/CPU_Instruction_Set.html), accessed 2026-07-06.

## Operational Context

`gbc_lib.py`'s `ROM` class is a hand-written subset emitter, not a full assembler — it defines one
Python method per SM83 instruction *variant* it needs (e.g. `LD_A_n`, `LD_BC_nn`, `LD_A_HL`), each
hardcoding the correct opcode byte(s) via `self.emit(...)`. As of this topic's authoring, the
class covers: control flow (`NOP`, `DI`/`EI`, `HALT`, `RET`/`RET_Z`/`RET_NZ`/`RET_C`/`RET_NC`,
`RETI`), accumulator ops (`XOR_A`, `OR_A`, `CPL`, rotates `RLA`/`RRA`/`RLCA`/`RRCA`, `DAA`),
8-bit/16-bit immediate loads (`LD_A_n`…`LD_L_n`, `LD_BC_nn`…`LD_SP_nn`), and the full
register-to-register `LD r,r'` grid via a shared `_rr(d,s)` helper that packs the destination/
source register codes into the `0x40`-based opcode block.[^1] This is the same encoding Pan Docs
describes: `LD r,r'` occupies the `01xxxyyy` opcode block, register codes 0–7 mapping to
B,C,D,E,H,L,(HL),A.

Every `asm_game.py` routine is built exclusively from these emitter methods — there is no path to
emit an opcode `gbc_lib.py` doesn't already expose. This is a real constraint: extending the game's
logic (e.g. a future bank-switch `LD A,(nn)` from a banked region, or 16-bit arithmetic
`gbc_lib.py` doesn't yet emit) requires **adding a new method to `gbc_lib.py` first** — implicitly
routing that work through the code-implementation stage, not something a game-logic package can
work around inline.

## Implementation Guidance

- **Adding a new opcode emitter:** follow the existing pattern exactly — one method per addressing
  mode (not one method with runtime-branching operand types), hardcode the opcode byte(s), and
  never touch the illegal-opcode set (`$D3,$DB,$DD,$E3,$E4,$EB,$EC,$ED,$F4,$FC,$FD`) even
  transitively through a computed/parameterized emission path.
- **Cycle budgeting a new VBlank-window routine** (relevant to R102's access-timing budget):
  sum each opcode's M-cycle cost from Pan Docs' instruction table before assuming a routine fits
  in the VBlank period — **1140 M-cycles (4560 T-states)**, per R102's directly-confirmed figure
  (10 scanlines × 456 T-states/line, [Pan Docs](https://github.com/gbdev/pandocs/blob/master/src/Rendering.md),
  accessed 2026-07-10) — `gbc_lib.py` does not track or assert cycle counts itself, so this is a
  manual check the implementer must do. **Correction (2026-07-10, `BL-0032`):** this line
  previously read "~1140 T-state," a units error — 1140 is the *M-cycle* count; the equivalent
  T-state count is 4560, matching R102's own figure exactly (this document's own §Concepts states
  the 1 M-cycle = 4 T-states conversion above). Both topics now cite the identical, directly-
  confirmed figure.
- **Do not add a generic raw-byte-emission escape hatch** (`emit_opcode(int)`) without an explicit
  guard rejecting the eleven illegal opcodes — the existing per-instruction methods are safe by
  construction (they never encode an illegal byte); a generic path would remove that safety.

## Feature Mapping

*(No `FS-xxx` authored yet — updated when a Feature Specification cites this topic.)*

## Related Topics

R102 (PPU/VRAM timing — consumes cycle costs from this topic to derive safe VBlank-window budgets)
· R110 (interrupt/ISR entry-exit overhead, itself an instruction-cost calculation).
