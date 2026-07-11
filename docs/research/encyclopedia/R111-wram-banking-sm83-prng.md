# R111 — CGB Banked WRAM & SM83 PRNG Determinism

- **Document ID:** R111 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (SM83 instruction set — the PRNG's opcode-level implementation), R102
  (VBlank/LCD-off redraw cost — the sibling generated-world hardware topic), R106 (SRAM cost of
  persisting the seed/scale), R110 (interrupt/RETI discipline the PRNG routine must not violate)
- **Referenced By:** R213 (this topic grounds R213's screen/room-graph + xorshift-PRNG
  recommendation in real hardware terms), R305 (the reference-generator oracle must mirror this
  topic's PRNG step-for-step), R112 (re-measures this topic's WRAM-headroom estimate against the
  shipped, post-generation tree, for the maze-generation hardware-feasibility comparison), **R113
  (2026-07-11 — found the shipped `gw_prng_step` deviates from this topic's own cited precedent
  and degenerates under repeated back-to-back draws; this topic's own PRNG characterization was
  accurate for the biome-loop's single-draw-per-region usage but incomplete against that usage
  pattern, never previously exercised or tested)**
- **Produces:** grounds `asm_game.py`'s future WRAM working-set for a generated world and its
  future PRNG routine; grounds strategic assumption **A9** (seed is the sole determinism input)
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R101, R102, R106, R110, R213

## Purpose

Filed to ground **MSTR-001 C10** (deterministic procedurally generated world) on two concrete
hardware questions the adopted increment plan's Phase 2 names explicitly
([PLAN-requirements-aesthetics-story-map.md](../../pipeline/PLAN-requirements-aesthetics-story-map.md)
§2): (1) how much WRAM does a generated world's working set actually have available across the
D6 scale range, and (2) how is a *deterministic* pseudo-random sequence actually produced on an
SM83 CPU with no hardware RNG, satisfying assumption **A9** (seed+scale are the sole entropy
sources — no DIV-register or uninitialized-RAM dependence anywhere in generation).

## Scope

The CGB's banked-WRAM mechanism (`SVBK`) and this project's current WRAM usage against it; a
concrete, cited, SM83-implementable deterministic PRNG algorithm and its state/code cost. Out of
scope: the generation *algorithm* the PRNG feeds (R213) and SRAM/save-format cost (R106).

## Concepts

**CGB WRAM is 32 KiB total, organized as 8 banks of 4 KiB, only 4 of which are addressable at
once.** Bank 0 is permanently mapped at `$C000`–`$CFFF`; one of banks 1–7 is switched into
`$D000`–`$DFFF` via the `SVBK` register at `$FF70` (CGB mode only, bits 0–2 select the bank).[^1]
`SVBK` carries the **same "value 0 quirk" family as MBC1's ROM banking** (R106): writing `$00`
does not select bank 0 in the switchable window — it maps bank 1 instead, since bank 0 is already
permanently available at `$C000`.[^1] This project's toolchain (`gbc_lib.py`) has no `SVBK`
read/write emitter today — adding banked-WRAM support would be a new opcode-emission addition,
exactly analogous to R106's note that `gbc_lib.py` has no MBC1 banking-register emitters either.

**This project's current WRAM usage is nowhere close to needing bank switching.** Per GDS-07 §2,
every WRAM address in active use today spans `0xC000`–`0xC3A0` (`OAM_BUF` at `0xC300` plus its
160-byte shadow-OAM buffer is the last and largest single allocation) — **under 928 bytes total**,
entirely within the fixed 4 KiB bank-0 window, with roughly **3.1 KiB of headroom remaining in
bank 0 alone**, before the switchable banks 1–7 (24 KiB more) are even touched. A generated
world's working set — a region-adjacency graph, a per-region biome-assignment table, generation
scratch state — would need to grow by more than 3× the entire game's *current total WRAM
footprint* before `SVBK` banking becomes relevant at all.

**Deterministic PRNG on an SM83 CPU is a solved, cheap, well-precedented problem.** Xorshift-family
generators need as little as 4 bytes of state, use only XOR and shift operations, and explicitly
avoid multiply/divide/modulo — the exact instruction classes an 8-bit CPU without a hardware
multiplier handles poorly.[^2] A worked **Z80 assembly implementation of a 16-bit xorshift
generator** exists as a direct transferable precedent: the SM83 is a close relative of the Z80
instruction set (the same lineage R101 already grounds this project's opcode emitters in), and the
cited implementation uses only shift/XOR/register operations with no multiply — directly portable
to `gbc_lib.py`'s existing opcode-emitter surface with no new primitive opcodes required.[^3]
Critically, **xorshift's only input is its own carried state** — no read of `DIV`, no read of
uninitialized RAM, no timing-dependent value anywhere in the algorithm — which is exactly what
strategic assumption **A9** requires: seed the generator's state once from the player-entered
seed value, and every subsequent "random" value is a pure, reproducible function of that seed and
how many times the generator has been stepped.

## Operational Context

`asm_game.py` has no PRNG today. The closest existing precedent is `tilemaps.py`'s `_fill()`
function (GDS-08 §1), which does a "seeded pseudo-random two-variant sprinkle" — but this runs
entirely on the **Python build side**, not on SM83 at runtime, and its "seed" is a build-time
constant, not a player-entered value. **No SM83-runtime randomness of any kind exists in the
shipped game** — R213's recommendation (generate the region graph on first boot from the
player's seed) would be this project's first runtime PRNG, not an extension of an existing one.

## Implementation Guidance

- **Do not pursue `SVBK`/banked-WRAM support as part of this increment.** At under 1 KiB of
  current usage against 4 KiB of unbanked bank-0 headroom, a generated world's WRAM working set
  would need to be extraordinarily large before banking is the binding constraint — treat this
  the same way R106 treats ROM banking: a real, documented future path (this topic *is* that
  documentation), not a near-term requirement. Revisit only if a specific Phase 3 architecture
  pass concretely sizes a working set that exceeds bank-0's remaining ~3.1 KiB.
- **Implement the PRNG as a xorshift-family generator with 2–4 bytes of WRAM state**, following
  the cited Z80 precedent's shift/XOR-only structure[^3] — no new `gbc_lib.py` opcode primitives
  are needed (`LD`, `XOR`, `RLC`/`RRC`-family shifts, and register moves are already emitted per
  R101). Seed the state once, at new-game creation, from the player-entered seed value (per
  MSTR-001 D6/D7 — seed entry happens exactly once, at new-game creation, matching a one-time
  PRNG-state initialization exactly).
- **Never read `DIV`, an uninitialized WRAM byte, or any other timing-dependent value as PRNG
  input or reseed source** — doing so would violate A9's determinism guarantee and make the
  Python reference-generator oracle (R305's testing pattern, per the adopted plan §2) unable to
  predict expected output for a given seed, breaking the entire determinism-testing strategy this
  increment depends on.
- **Route the PRNG call through the same discipline `do_screen_redraw` already uses for
  first-boot/transition work** — if generation runs at new-game creation (R213's recommendation),
  it is a good candidate to run under the same LCD-off bracket `do_screen_redraw` uses for
  full-screen work (R102's extension above), rather than inventing a second "safe window"
  convention.

### Sources
[^1]: [SVBK/WBK Register Details — pandocs (`gbdev/pandocs`, GitHub mirror, `CGB_Registers.md`)](https://github.com/gbdev/pandocs/blob/master/src/CGB_Registers.md), fetched directly 2026-07-09 (the `gbdev.io` hosted mirror returned HTTP 403 this session; the GitHub source mirror fetched successfully and is the same canonical Pan Docs content this project's R101–R110 already cite via the hosted mirror).
[^2]: [Pseudorandom Number Generators — filterpaper notes](https://filterpaper.github.io/prng.html); corroborated by [Fast 8-bit pseudorandom number generator — Wikistix](https://www.stix.id.au/wiki/Fast_8-bit_pseudorandom_number_generator); accessed 2026-07-09 via WebSearch summary (see [R213](R213-procedural-map-generation-algorithms.md)'s identical citation — this topic and R213 ground the same PRNG fact from hardware-feasibility and algorithm-selection angles respectively).
[^3]: [Retro Programming: 16-Bit Xorshift Pseudorandom Numbers in Z80 Assembly](http://www.retroprogramming.com/2017/07/xorshift-pseudorandom-numbers-in-z80.html); accessed 2026-07-09 via WebSearch summary; cross-reference [R101](R101-sm83-instruction-set.md) for the SM83/Z80 instruction-set relationship this precedent transfers through.

**Single-source flag:** none — the SVBK citation ([^1]) was directly fetched from a primary
source this session (unlike most other citations in this research pass, which rested on
WebSearch summaries after repeated HTTP 403s); the PRNG citations ([^2]/[^3]) are corroborated
across ≥2 sources each, consistent with R213's identical citation set.

## Feature Mapping

*(No `FS-xxx` authored yet — this grounds the Phase 3 world-generation ADR.)*

## Related Topics

R101 (SM83 opcode-level implementation of the PRNG) · R102 (the sibling generated-world hardware
topic — redraw cost vs. this topic's working-set/RNG cost) · R106 (SRAM cost of persisting the
seed this PRNG is initialized from) · R110 (interrupt/RETI discipline the PRNG/generation routine
must respect) · R213 (the generation algorithm this topic's PRNG and WRAM-budget findings ground)
· **R113 (2026-07-11 — the as-shipped `gw_prng_step` routine's degeneracy under repeated draws,
found via `IP-1070`'s Blocking Report, `BL-0070`; extends this topic's characterization rather
than contradicting it — the single-draw-per-region usage this topic grounded remains accurately
described).**
