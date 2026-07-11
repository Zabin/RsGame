# ADR-0014 — `gw_prng_step` repair is the right fix, but shipping it needs explicit user authorization (not decided here)

**Status:** Accepted (2026-07-11) — decision on *which fix is correct* is made; *authorization to
ship it* is explicitly routed to the user, not granted by this ADR.

## Context

[BL-0074](../../pipeline/backlog.md) (project owner report, 2026-07-11): two new games at the
literal default seed (`SEED=0`, scale 3 and scale 9) both produced heavily degenerate worlds.
Directly confirmed against the real built ROM (PyBoy): `seed=0` normalizes to `1`
([ADR-0010](ADR-0010-seed-scale-model.md)), and `gw_prng_step(1)`'s state collapses to its
absorbing fixed point (`0x0000`) after exactly 2 calls. Every biome-assignment draw after that
returns a constant `delta=-1`. `REGION_GRAPH`'s real biome-id grid at `scale=9` is confirmed over
90% Water (row 0 = `[2,3,2,1,0,0,0,0,0]`, rows 1–8 all zero); `scale=3` only looks acceptable by
coincidence of how the adjacency-grammar clamp's own gradient-decay math happens to render a
small grid.

This is the same structural defect [R113](../../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md)
formally characterized and [ADR-0013](ADR-0013-maze-pass-prng-decorrelation.md) already fixed —
but *only* for `IP-1070`'s own maze-generation pass. `ADR-0013`'s Context section explicitly
reasoned the biome-assignment loop (`generate_world`, shipped and `VERIFIED` via `IP-1020`) was
safe because it "draws once per region with substantial other computation between draws, and
consumes each draw via a heavily-quantizing `mod-3`-clamped-delta reduction that produces
deterministic, grammar-valid output even from a degenerate stream." **`BL-0074` directly falsifies
that assumption for `SEED=0` specifically** — but this ADR's own investigation, run before
deciding, found the truth is much worse than "one bad default seed":

**New finding (this ADR's own investigation, not previously known):** the shipped `gw_prng_step`
degenerates to a fixed point or a short cycle (period ≤4) within 20 draws for **every one of the
first 2000 seed values tested (2000/2000, 100%)** — not a rare edge case, the *normal* case.
Measuring the actual downstream consequence (fraction of a generated world's regions assigned
Water, `biome_id=0`, the floor value every degenerate stream decays toward) across 200 seeds:

| Scale | Mean Water fraction | Seeds >50% Water | Seeds >80% Water | Seeds <20% Water (looks fine) |
|---|---|---|---|---|
| 9 (81 regions) | 46.4% | 110/200 (55%) | 64/200 (32%) | 72/200 (36%) |
| 3 (9 regions) | 21.3% | 21/200 (10.5%) | — | — |

At `scale=9` — the exact scale the reporter tried — **a majority of all seeds, not just the
default, produce a majority-Water world**, and roughly a third produce an almost-entirely-Water
world. The small-grid case (`scale=3`) degrades much more gracefully only because the
adjacency-grammar clamp's own gradient-decay math happens to still look varied over just 9 cells;
the defect is identical underneath. **This means `ADR-0009`'s/`ADR-0012`'s own foundational
premise — biome-assignment already produces meaningfully varied worlds, and the maze pass adds
distinct shape on top of that — was never actually true for `scale=9`, the project's own stated
long-term target (`MSTR-001` commitment C7).**

R113 already presents two repair candidates for `gw_prng_step` itself (never adopted, by design —
that stage's own job is comparison, not decision):

- **(a) Repair the mixing step to a period-sound shift triplet** (`x ^= x<<7; x ^= x>>9; x ^= x<<8`,
  the R111-cited precedent). **This ADR verified it directly** (not merely citing R113's own
  claim): the corrected triplet produces **0/2000 degenerate seeds** in the same test that found
  the shipped version 100% degenerate, and a full 65535-state period starting from seed 1 (maximal
  for a 16-bit xorshift excluding the 0 fixed point). Hardware cost: comparable order, shift-by-8
  is actually *cheaper* than today's byte-swap (a straight byte move vs. a cross-XOR of both
  bytes); shift-by-7/9 need several chained single-bit shifts (no shift-by-N opcode on SM83).
- **(b) A scoped per-draw perturbation, mirroring `ADR-0013`'s own maze-pass fix.** This is where
  this ADR's own reasoning **diverges from `ADR-0013`'s precedent, not merely reapplies it**: for
  the maze pass, perturbation was compatibility-*free* because the maze pass is brand-new work
  with zero prior shipped output to preserve. Biome-assignment has no such luxury — it has been
  shipped and `VERIFIED` since `IP-1020`, and `REGION_GRAPH` regenerates from `(seed, scale)` alone
  on every save load (`ADR-0009` point 3). XORing a counter into *every* biome-assignment draw
  would change the generated biome-id sequence for *every* seed, not just the degenerate ones —
  this is **not** the free, zero-compatibility-impact move it was for the maze pass. It carries
  nearly the same blast radius as option (a), for a strictly worse result (a perturbed-but-still-
  fundamentally-broken PRNG, vs. a genuinely repaired one).
- **(c) Detect-and-perturb only the specific degenerate condition**, leaving every currently-
  well-behaved seed untouched. Given the 100%-degeneracy finding above, this collapses to
  "perturb every seed" in practice — there is no meaningful "well-behaved" subset left to
  preserve. **Not viable as a narrower alternative**, contrary to how it looked before this ADR's
  own investigation ran the numbers.
- **(d) Normalize `seed=0` to some other, empirically-verified-non-degenerate value instead of
  `1`.** **Directly falsified by this ADR's own investigation**: seeds 0 through 1999 are *all*
  degenerate within 20 draws. There is no small-integer replacement value that would actually
  fix this — the defect is in `gw_prng_step` itself, not in which specific seed a player happens
  to type.

## Decision

**Technical decision (made here, not deferred): fix (a) — repairing `gw_prng_step`'s own mixing
step to the period-sound `7,9,8` shift triplet — is the correct fix.** Every alternative this ADR
or R113 considered is either technically insufficient (b, c, d, per the investigation above) or
strictly worse for comparable or higher cost. This is not a close call on the technical merits.

**Authorization decision: this ADR does NOT authorize shipping fix (a).** Unlike `ADR-0012`
(a genuinely new algorithm for genuinely new work, no prior behavior to break) — and unlike this
same session's own `ADR-0013` (a fix scoped to guarantee zero compatibility impact) — fix (a)
**retroactively redefines the world every existing save regenerates on its next load.** `ADR-0013`
already established the principle that this class of consequence is not this stage's call to make
unilaterally (`ADR-0013` Decision point 1); this ADR's own investigation shows the actual blast
radius is **larger than `ADR-0013` anticipated when declining fix (a) for the maze pass** — that
decision was made assuming biome-assignment was *not* independently broken. It is. Repairing
`gw_prng_step` now touches the one generation step every single `(seed, scale)` combination has
depended on since `IP-1020` shipped, not a narrow, not-yet-released feature.

**This is explicitly routed to the user as a `NEEDS-USER` decision, not decided here**, for two
reasons stated honestly rather than assumed:

1. **The compatibility cost is real and asymmetric in a way worth the user's own judgment.** Every
   currently-in-progress save regenerates a *different* world on its next load after this fix
   ships — for most players (the 55-64%+ whose current world is majority/near-total Water at
   `scale=9`) this is a strict improvement they'd almost certainly want; for the minority whose
   current seed happens to already look fine, it's an unrequested change to a world they may have
   already explored and partially completed. Whether "most players are better off" is sufficient
   grounds to accept a save-breaking change for the minority is exactly the kind of tradeoff this
   project's own owner should make explicitly, not have made silently on their behalf.
2. **Precedent already established in this same session.** `ADR-0013` set the standard that a
   save-format-relevant PRNG change needs explicit user authorization, "ideally bundled with a
   save-format version bump ... so an old save can be handled deliberately rather than silently
   reinterpreted" (`ADR-0013` Decision point 1). This ADR follows that standard rather than
   quietly relaxing it now that the stakes are actually higher, not lower.

**If the user authorizes fix (a):** the recommended shape is: replace `gw_prng_step`'s final
mixing step (currently `x ^= byteswap(x)`) with the verified `7,9,8` shift triplet; bump
`SAVE_VERSION_VAL` (the established `IP-1010`→`IP-1050`→`IP-9070` strictly-monotonic sequence) so
a pre-fix save is handled deliberately (per this project's own existing convention — see
`ADR-0010`/`IP-1040`'s "a version-mismatched save is absent for 'continue' purposes" pattern,
which already exists precisely for this class of change) rather than silently regenerating a
different world under the player without any signal that happened; update `worldgen.py`'s oracle
mirror in lockstep (the same discipline `ADR-0012`/`ADR-0013` already established); confirm
`ADR-0013`'s own maze-pass counter-XOR perturbation is either removed (if `gw_prng_step` alone now
suffices for the maze pass's own draw-quality needs, worth re-measuring) or kept as a defense-in-
depth layer (cheap either way, no correctness cost to leaving it in). **This work — the actual
code change — belongs to `07-implementation-planning`/`08-code-implementation`, once authorized;
this ADR does not implement it.**

**If the user declines fix (a):** the fallback is **option (c)'s own logic inverted** — since
there is no narrow "degenerate subset" to detect, declining fix (a) effectively means accepting
that biome-assignment stays broken for roughly half of all `scale=9` worlds indefinitely,
including the literal default seed. That should be stated to the user plainly as the real
consequence of declining, not softened.

## Consequences

- **`gw_prng_step` remains unrepaired until the user explicitly authorizes fix (a).** This is a
  deliberate, recorded gate — not an oversight, and not a technical judgment that the current
  state is acceptable (it is not, per the measured data above).
- **`BL-0074` stays open, `NEEDS-USER`**, not `SCHEDULED` to `07` — there is nothing for
  `07-implementation-planning` to package until the user answers.
- **`ADR-0013`'s own Consequences section already flagged this exact scenario** ("a future backlog
  entry should track this if a subsequent feature needs higher-quality randomness than a
  loop-local counter perturbation can provide") — `BL-0074` is that entry, arriving sooner and
  with a larger blast radius than `ADR-0013` itself anticipated.
- **No code, requirements, or package changes from this ADR.** `REGION_GRAPH`'s data format,
  `GDS-04`/`GDS-07`/`GDS-09`, and every existing package's own status are unaffected by this ADR
  alone — only by whatever the user's answer authorizes next.
- **This finding is broader than `BL-0074`'s own original framing** ("the default seed is bad") —
  the real finding is "the shipped PRNG is degenerate for effectively all seeds, and this was
  always true since `IP-1020` shipped, just never visually obvious until a large-scale (`scale=9`)
  world's biome map was actually inspected." Recorded here so this context survives even if the
  user's eventual answer is deferred rather than immediate.

## Related

- Directly extends [ADR-0013](ADR-0013-maze-pass-prng-decorrelation.md)'s own declined-fix-(a)
  reasoning — same principle, now applied with a materially larger measured blast radius.
- Grounded by [R113](../../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md) (root
  cause, the `7,9,8` shift-triplet candidate, and the original two-fix comparison) and
  [R111](../../research/encyclopedia/R111-wram-banking-sm83-prng.md) (the original PRNG
  characterization, now confirmed incomplete against realistic multi-draw-per-region usage at
  `scale=9`).
- Does not amend [ADR-0009](ADR-0009-screen-graph-world-generation.md) point 3's own determinism
  guarantee (`REGION_GRAPH` regenerates from `(seed, scale)` alone) — that guarantee is exactly
  *why* this fix's consequence is a save-compatibility question at all, and remains correct and
  unchanged either way the user answers.
- [ADR-0010](ADR-0010-seed-scale-model.md)'s own `seed=0 → 1` normalization is confirmed **not**
  the source of the defect (every tested seed is equally degenerate) — no change to that ADR is
  implied or needed.
- Filed from [BL-0074](../../pipeline/backlog.md) (`00-intake`, 2026-07-11, project owner report).
