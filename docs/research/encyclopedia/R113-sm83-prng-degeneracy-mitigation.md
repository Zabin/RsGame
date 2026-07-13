# R113 — SM83 PRNG Degeneracy Under Repeated Draws & Mitigation Options

- **Document ID:** R113 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R111 (the PRNG this topic re-examines — its own characterization was grounded
  only against the biome-assignment loop's single-draw-per-region usage, never validated against
  repeated back-to-back draws), R101 (SM83 instruction set — the shift/XOR opcodes any fix must
  use), R112 (the maze-generation feature whose braid pass first exposed this defect)
- **Referenced By:** [ADR-0013](../../architecture/adr/ADR-0013-maze-pass-prng-decorrelation.md)
  (the maze-pass-scoped fix, `BL-0070`), [ADR-0014](../../architecture/adr/ADR-0014-gw-prng-step-repair-needs-user-authorization.md)
  (confirms the `7,9,8` shift-triplet fix this topic named as fully correcting the degeneracy —
  0/2000 seeds degenerate vs. the shipped routine's 100/100% — for `BL-0074`, routed `NEEDS-USER`),
  **R114 (2026-07-13 — flags that any new per-region PRNG-reseeding scheme for streaming generation
  must not reintroduce a similar degeneracy defect)**
- **Produces:** grounds the fix `03-architecture-design-synthesis` must choose before `IP-1070`
  (Maze-Shaped Region Adjacency) can re-attempt implementation
- **Feature Mapping:** *(none yet — `FEAT-9100`/`IP-1070` consume this topic's findings once a
  fix is decided)*
- **Related Topics:** R101, R111, R112

## Purpose

Filed to ground **`BL-0070`** (an `08-code-implementation` Blocking Report, 2026-07-11): an
attempt to implement `IP-1070`'s maze-generation braid pass directly measured the shipped PRNG
(`gw_prng_step`, `asm_game.py`, shipped/`VERIFIED` via `IP-1020`) collapsing to a degenerate fixed
point or short cycle within 1–2 calls when drawn repeatedly with no intervening non-PRNG work —
undermining `FR-9150`'s own ~25%-reopen statistical guarantee. This topic answers two concrete
questions: (1) **why**, formally, does the shipped mixing step degenerate this way, and (2) **what
are the cheapest SM83-appropriate fixes**, so `03-architecture-design-synthesis` can decide
without re-deriving the algebra or re-running the hardware-cost survey itself.

## Scope

The shipped `gw_prng_step` routine's actual algorithm as implemented (not as originally cited);
the mathematical reason its final mixing step degenerates; candidate fixes/mitigations and their
hardware cost and compatibility impact. Out of scope: which fix to adopt (`03`'s own call,
per this pipeline's stage boundaries — this topic presents tradeoffs, exactly as
[R112](R112-maze-generation-hardware-feasibility.md) already did for the maze algorithm choice,
without picking one) and the maze-generation algorithm itself (R112's own scope, unaffected by
this finding — the spanning-tree carve phase was directly confirmed correct even under a
degenerate PRNG, since its own "try up to 4 directions in rotation, skip visited" structure
tolerates a low-variety draw stream gracefully; only the braid pass's binary per-edge decision is
sensitive to draw quality).

## Concepts

**The shipped mixing step is not the cited precedent's algorithm — it substitutes a byte-rotate
for a byte-shift, and this substitution is the root defect.** R111 cites a worked "16-bit xorshift
in Z80 assembly" precedent[^1] as the transferable pattern `gw_prng_step` was built from. That
precedent's actual algorithm (John Metcalf's generator, the version R111's own source page
describes) is `hl ^= hl << 7; hl ^= hl >> 9; hl ^= hl << 8` — shift amounts **7, 9, 8**, one of
four shift triplets (alongside 6,7,13; 7,9,13; 9,7,13) that pass lightweight randomness
tests[^1][^2]. The shipped routine instead implements `x ^= x<<1; x ^= x>>1; x ^= byteswap(x)`
(`asm_game.py`, comment at the `gw_prng_step` label) — shift amounts **1, 1**, and a **literal
byte-swap** substituted for the precedent's own `hl << 8` step.

**These are not equivalent, and the substitution is the specific point of failure.** For a 16-bit
value `x = (hi, lo)`:
- The precedent's `x << 8` (a genuine left-shift with zero-fill) produces `(lo, 0)` — XORing this
  in gives `new_hi = hi ^ lo`, `new_lo = lo ^ 0 = lo` (**unchanged**).
- A byte-**swap** of `x` produces `(lo, hi)` — XORing this in gives `new_hi = hi ^ lo`,
  `new_lo = lo ^ hi` — **the same value as `new_hi`**, since XOR is commutative (`lo^hi == hi^lo`).

**The shipped routine's final step therefore forces `new_hi == new_lo` on every single call, by
algebraic construction — not merely "often" or "for weak seeds," but always, unconditionally.**
This collapses the *reachable* state space from the full 65536 sixteen-bit values to at most 256
(one per possible shared byte value) on the very first call, regardless of the seed. Directly
confirmed via PyBoy this session (not merely derived): seeding from `SEED=12345` (normalized per
`ADR-0010`) and calling `gw_prng_step` repeatedly, `TMP1`/`TMP2` both read `0` after exactly 2
calls and stay there forever — `0` is a fixed point of any pure-XOR-only construction (XORing
zero-derived shifts and a self-swap of zero all yield zero), so once reached it can never be
escaped. Other tested seeds (999, 42424) instead settle into a short repeating 3-value cycle
(`128, 129, 1, 128, 129, 1, ...`) rather than the `0` fixed point, but are equally degenerate —
the shipped routine's own state space, restricted to the `hi==lo` subspace the first call already
forces it into, is simply too small (256 states) to avoid short cycles for many seeds.

**This is consistent with, and explained by, the formal theory governing why xorshift shift
triplets must be chosen carefully.** A Marsaglia-family xorshift generator's period is maximal
(`2^n - 1`) **if and only if** the linear transformation's characteristic polynomial over `GF(2)`
is *primitive* — an algebraic property that most shift triplets do **not** satisfy; only specific,
verified triplets (like the cited precedent's 6,7,13 / 7,9,8 / 7,9,13 / 9,7,13) are known to work,
and even some of those still fail statistical tests despite achieving full period[^3][^4]. A
byte-**swap** step is not a member of the xorshift family's shift/XOR vocabulary at all — it is a
**rank-reducing** linear transformation over `GF(2)^16` (mapping every 16-bit input to an 8-bit
image, since `new_hi` and `new_lo` are forced equal), which is about as far from a primitive,
full-rank transformation as a construction can get. The shipped routine's degeneracy is not an
unlucky parameter choice within a sound family — it is a structurally different, provably
non-full-rank construction that was never a valid xorshift variant to begin with.

**Why this was never previously caught.** The only existing caller
(`generate_world`'s biome-assignment loop, `IP-1020`) draws `gw_prng_step` once per region, with
substantial other computation (biome-clamp arithmetic, WRAM writes) between draws, and consumes
each draw via a `mod-3` reduction clamped into a delta of `{-1, 0, +1}` further clamped into a
valid biome range `[0,4]` — a heavily-quantizing consumption pattern that produces deterministic,
grammar-valid output even from a degenerate, low-variety, or all-equal draw stream (a
constant-delta walk still yields a monotonically-clamped, grammar-legal biome sequence). None of
`T12`'s existing checks (determinism, reachability, grammar-validity, one-KeyItem-per-region) are
sensitive to draw *quality* — only to determinism, which a degenerate-but-deterministic stream
still satisfies perfectly. `IP-1070`'s braid pass is the first caller to draw many `gw_prng_step`
values back-to-back (up to ~16 per generated world at `scale=5`, more at larger scales) with
**zero** intervening non-PRNG state change and a **binary**, unclamped keep/prune decision per
draw — exactly the usage pattern that turns "restricted to 256 states, prone to short cycles"
into "observably broken" (0/16 or ~11/16 kept, versus a ~4/16 target).

## Operational Context

`gw_prng_step` runs once per PRNG draw, called from `generate_world`'s existing biome-assignment
loop (up to 81 times, once per region at `scale=9`) and, in `IP-1070`'s attempted design, from
both the spanning-tree carve phase (one draw per region visited, for the starting-direction mod-4
pick) and the braid/prune pass (one draw per non-tree canonical edge, up to ~72 at `scale=9`).
All of this runs within `generate_world`'s existing one-time, LCD-off-bracketed cost class
(R102's convention, already established) — a fix's cycle cost is not competing with a per-frame
budget, only with the same generous one-time-generation allowance R112 already sized the maze
pass's own cost against.

## Implementation Guidance

Three candidate fixes/mitigations, presented for `03-architecture-design-synthesis` to choose
between — none adopted here:

**(a) Replace the mixing step with a period-sound shift triplet** (e.g. the cited precedent's own
7,9,8[^1], or another triplet verified against the primitive-polynomial criterion[^3]),
implemented as genuine shifts (zero-fill), not a rotate/swap. **Hardware cost:** comparable order
of magnitude to today's routine — the SM83 has no "shift-by-N" opcode (only single-bit
`SLA`/`SRA`/`SRL`/`RLC`/`RRC`-family instructions, per R101), so a shift-by-7 or shift-by-9 needs
several chained single-bit shifts, while a shift-by-8 is actually *cheaper* than today's swap (a
straight byte move + one register zeroed, versus today's cross-XOR of both bytes) — a real
implementation-time measurement, not asserted here, but not expected to blow any existing ROM/cycle
budget. **Compatibility impact:** **changes every existing `(seed, scale)` combination's generated
biome output** — `T12`'s oracle-parity/determinism fixtures don't hardcode specific byte values
(they compare the SM83 routine against `worldgen.py`'s own mirror, which would be updated in
lockstep), so this doesn't *break* `T12`'s own checks, but it does mean any *externally* recorded
seed/output pairing (documentation examples, a player's saved expectation of "what seed X looks
like") would change — a compatibility-relevant decision this topic flags but does not adjudicate.
Fixing `gw_prng_step` itself is squarely `03-architecture-design-synthesis`'s territory (an
`R111`/`ADR-0009` amendment), not `07`/`08`'s to invent.

**(b) Leave `gw_prng_step` itself untouched; decorrelate `IP-1070`'s own repeated draws with a
cheap per-draw perturbation** — e.g. XOR the current loop counter (already held in a register/WRAM
byte for the carve/braid loop's own bookkeeping, per `IP-1070`'s own design) into the drawn byte
before using it for a decision, without feeding that perturbation back into `TMP1`/`TMP2`'s own
carried state. **Hardware cost:** one `XOR` against an already-live register value — negligible,
no new WRAM, no new opcode primitive. **Compatibility impact:** **zero** — `gw_prng_step`'s own
algorithm and every existing biome-generation output are completely untouched; only `IP-1070`'s
own new call sites change. **Caveat, not resolved here:** this does not fix the underlying
PRNG — a future caller with the same "many back-to-back draws, no counter handy" shape could
still hit the same wall; it is a narrowly-scoped mitigation, not a general repair, and
`03-architecture-design-synthesis` should record explicitly whether that scope limitation is
acceptable or whether it warrants revisiting when the next such caller appears.

**(c) A combination or a different well-established cheap technique for this hardware class** —
e.g. reseeding `TMP1`/`TMP2` from a cheap non-PRNG counter every few draws (a coarser version of
(b)), or adopting one of the other three verified full-period triplets[^3] if 7,9,8 turns out
costlier than an alternative once actually measured. Not further specified here — this topic's
job is to establish that (a) and (b) are both real, cheap, SM83-appropriate options with clearly
different compatibility footprints, not to pick between them.

**Do not treat this as urgent-fix-anything territory** — the *existing*, shipped biome-generation
output is not corrupted or incorrect by any test this project runs (§Concepts above explains
exactly why `T12` never caught it and never needed to); the defect is real but its *blast radius*
today is confined to the not-yet-shipped `IP-1070` braid pass, which is already `BLOCKED` pending
this decision.

### Sources
[^1]: [Retro Programming: 16-Bit Xorshift Pseudorandom Numbers in Z80 Assembly](http://www.retroprogramming.com/2017/07/xorshift-pseudorandom-numbers-in-z80.html) (the same source R111 already cites); direct fetch returned HTTP 403 this session (same failure mode R111's own Sources section already recorded for this exact URL) — content confirmed via WebSearch summary, which quotes the algorithm's actual shift amounts (7, 9, 8) and John Metcalf's generator by name, corroborated by [^2].
[^2]: [Fast quality Xor-Shift random number generator for Z80 — raxoft (GitHub Gist)](https://gist.github.com/raxoft/c074743ea3f926db0037); accessed 2026-07-11 via WebSearch summary — corroborates the shift-triplet convention (naming the same class of 7/9/8-style triplets) and gives an independent, differently-tuned Z80 xorshift implementation as a second data point that real Z80/SM83 xorshift generators use genuine shifts, never a byte-swap step.
[^3]: [An experimental exploration of Marsaglia's xorshift generators, scrambled — Vigna](https://vigna.di.unimi.it/ftp/papers/xorshift.pdf); accessed 2026-07-11 via WebSearch summary — establishes the primitive-characteristic-polynomial-over-GF(2) requirement for maximal period, and that most shift triplets do not satisfy it (grounding why "any similar-looking shift/XOR sequence" is not automatically sound).
[^4]: [On the xorshift random number generators — ResearchGate summary](https://www.researchgate.net/publication/220136542_On_the_xorshift_random_number_generators); accessed 2026-07-11 via WebSearch summary — corroborates [^3]'s primitivity requirement and separately notes that even full-period shift triplets can still fail statistical tests, reinforcing that shift-triplet choice is a real, non-trivial design constraint, not an arbitrary implementation detail.

**Single-source flag:** the core formal claim (primitive-polynomial requirement for maximal
period) is corroborated across two independent sources ([^3], [^4]); the specific shift-triplet
values (7,9,8 and siblings) rest on WebSearch summaries of [^1]/[^2] rather than a direct fetch
(the same access limitation R111 already recorded for this identical URL) — flagged, not
presented as beyond doubt, though the shipped code's own comment ("byteswap(x)") independently
corroborates that a byte-swap, not a shift, is what was actually implemented, which is the load-
bearing fact this topic's own analysis depends on, verified directly against this project's own
source (`asm_game.py`) and PyBoy-measured runtime behavior — Tier-A evidence per this skill's own
sourcing hierarchy, not resting on the external citations alone.

## Feature Mapping

*(None yet — `IP-1070` is `BLOCKED` pending a fix decision this topic grounds; once
`03-architecture-design-synthesis` decides, this topic's Feature Mapping should be updated to
point at whichever package/FS actually implements the chosen fix.)*

## Related Topics

R101 (SM83 opcode-level shift/XOR instructions any fix must use — confirms no new opcode
primitives are needed for either candidate fix) · R111 (the PRNG topic this one directly extends
— R111's own characterization was accurate for the biome-loop's single-draw usage but incomplete
against repeated back-to-back draws, a gap this topic closes) · R112 (the maze-generation feature
whose braid pass first exposed this defect; R112's own algorithm-choice findings are unaffected —
the spanning-tree carve phase tolerates a degenerate PRNG gracefully, per this topic's own
Concepts section).
