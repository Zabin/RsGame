# ADR-0013 — Maze-pass PRNG decorrelation via a per-draw loop-index perturbation (`gw_prng_step` itself unchanged)

**Status:** Accepted (2026-07-11)

## Context

[BL-0070](../../pipeline/backlog.md) (an `08-code-implementation` Blocking Report, 2026-07-11)
found that an `IP-1070` implementation attempt's braid pass — drawing `gw_prng_step` many times
back-to-back with no intervening non-PRNG state change — exposed a structural defect in the
shipped PRNG: its final mixing step (`x ^= byteswap(x)`) forces the new state's high and low
bytes equal on **every** call, by algebraic construction (XOR commutativity: `hi^lo == lo^hi`), a
rank-reducing linear transformation over `GF(2)^16`, not a valid xorshift variant.
[R113](../../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md) formally grounds this
and directly confirms it via PyBoy: seed 12345 collapses `TMP1:TMP2` to `0` after 2 calls and
stays there forever; other seeds settle into a short 3-value cycle. Measured impact on the braid
pass's own ~25%-reopen target (`FR-9150`): some seeds keep 0/16 non-tree candidate edges, others
~11/16 — neither approximates the target.

**This defect is real but its blast radius today is confined to `IP-1070`, not-yet-shipped.** The
only *existing* caller (`generate_world`'s biome-assignment loop, `IP-1020`, `VERIFIED`) draws
once per region with substantial other computation between draws, and consumes each draw via a
heavily-quantizing `mod-3`-clamped-delta reduction that produces deterministic, grammar-valid
output even from a degenerate stream — `T12`'s existing checks (determinism, reachability,
grammar-validity) are not sensitive to draw *quality*, only determinism, which a degenerate
stream still satisfies perfectly. No shipped, `VERIFIED` behavior is incorrect today.

R113 presents two candidate fixes without adopting one, per that stage's own job:

- **(a) Repair `gw_prng_step`'s own mixing step** to a period-sound shift triplet (e.g. the
  R111-cited precedent's own 7,9,8[^ref-r113]). Comparable hardware cost. **Compatibility
  impact, more severe than first framed when this ADR requested R113's grounding:** `REGION_GRAPH`
  is never persisted — it **regenerates from `(SEED, WORLD_SCALE)` alone on every save load**
  (`ADR-0009` point 3, tested directly by `IP-1050`'s own `T15.a5`, "Regenerated region graph
  matches pre-save graph"). Changing `gw_prng_step`'s own algorithm would mean **every existing
  save file, on its next load, regenerates a *different* world than the one the player has
  actually been exploring and collecting `KeyItem`s in** — not merely a stale documentation
  example, a real save-compatibility break for any player with an in-progress save at the moment
  this ships. This is a materially different (and materially larger) consequence than "an
  externally-recorded seed/output pairing changes."
- **(b) Decorrelate `IP-1070`'s own repeated draws with a cheap per-draw perturbation** (XOR a
  loop-local counter into the drawn byte before using it for a decision, without feeding the
  perturbation back into `gw_prng_step`'s own carried `TMP1`/`TMP2` state). Negligible cost, zero
  compatibility impact — `gw_prng_step`'s own algorithm and every existing biome-generation output
  stay completely untouched. Caveat: does not repair the underlying PRNG for some future caller
  with the same usage shape.

## Decision

**Adopt (b): within `IP-1070`'s own maze-generation pass — both the spanning-tree carve phase's
direction draws and the braid/prune pass's keep/prune draws — XOR the pass's own per-draw loop
counter into each drawn `gw_prng_step` byte before using it for a decision. The perturbed value is
used for the decision only; it is never written back into `TMP1`/`TMP2`, so `gw_prng_step`'s own
carried state, its algorithm, and every other call site (the biome-assignment loop) are completely
unaffected.** `gw_prng_step` itself is **not** repaired by this ADR.

**This decision is made directly from R113's comparison, without adopting fix (a), reasoning
recorded here so the call is a decision, not a shortcut:**

1. **Fix (a)'s compatibility cost is a real, player-facing save-compatibility break, not a
   cosmetic one.** `ADR-0009` point 3's own determinism guarantee — the one `IP-1050`'s save
   system is built on and `T15.a5` directly tests — is precisely "regenerate `REGION_GRAPH` from
   `(seed, scale)` alone." Changing the generator function that guarantee depends on, for any
   already-created save, silently redefines what that save's world *is*. This is squarely the
   kind of consequence that needs the user's explicit, informed authorization before shipping —
   not a call `03-architecture-design-synthesis` should make silently on the user's behalf, even
   though this stage generally has the delegated authority to make research-driven technical
   calls (`ADR-0012`'s own precedent). The two situations differ: `ADR-0012` chose an *algorithm*
   for a *new* feature with no prior behavior to break; fix (a) would *retroactively redefine*
   already-shipped, already-`VERIFIED`, already-played behavior. **This ADR declines fix (a) for
   that reason — not because it is technically unsound, but because adopting it is not this
   stage's decision to make unilaterally.** If a future pass wants to pursue it, that decision
   should be posed to the user explicitly, ideally bundled with a save-format version bump (the
   established precedent for a save-affecting behavior change, `IP-1010`→`IP-1050`→`IP-9070`'s
   own strictly-monotonic `SAVE_VERSION_VAL` sequence) so an old save can be handled deliberately
   rather than silently reinterpreted.
2. **Fix (b) fully resolves `IP-1070`'s own actual problem** — the braid pass needs per-edge
   variation *within one generation event*, not a globally higher-quality PRNG. A loop-local
   counter, incrementing once per draw and never persisted, guarantees the perturbed byte varies
   draw-to-draw within that event even when `gw_prng_step`'s own raw output is stuck at a
   constant or a short cycle — sufficient for `FR-9150`'s own "statistically reasonable band"
   Acceptance Criterion, without touching anything save-relevant.
3. **Scope extended to the carve phase's own direction draws, not just the braid pass**, on a
   real player-facing quality concern this ADR surfaces (not previously named in `BL-0070`/R113,
   which focused on the braid pass specifically): under the unrepaired PRNG, the carve phase's own
   mod-4 starting-direction draw is *also* stuck at a constant for any seed that has collapsed —
   meaning every such seed would carve an **identical** maze shape (only biome layout would still
   vary, itself questionably, via the same degenerate stream), directly undermining
   `BL-0064`'s own stated goal (distinct, seed-varied Zelda/Pokémon-style regions, not the same
   shape every time). Perturbing the carve phase's draws the same way closes this gap at zero
   additional cost, using the same technique already adopted for the braid pass.
4. **Determinism is unaffected.** The loop counter is a pure function of the pass's own draw
   position — deterministic, not itself randomized — so perturbing with it preserves full
   reproducibility: identical `(seed, scale)` always produces the identical counter sequence,
   hence the identical perturbed-byte sequence, hence byte-identical `REGION_GRAPH` output.
   `FR-9140`'s own determinism Acceptance Criterion (c) is unaffected by this decision.

Concretely, for `07-implementation-planning`/`08-code-implementation` to pick back up:

1. **`gw_prng_step`'s own routine, opcode sequence, and every existing call site (the
   biome-assignment loop) are unmodified.** No `R111`/`ADR-0009` amendment. No `GDS-07` delta —
   `REGION_GRAPH`'s data format and every existing WRAM address are untouched.
2. **Every PRNG draw inside `IP-1070`'s own new maze-generation pass** (the carve phase's
   starting-direction draw, and the braid pass's per-edge keep/prune draw) **is XORed against a
   loop-local counter before use** — the counter increments once per draw within that pass
   (region-visit order for the carve phase, canonical-edge iteration order for the braid pass;
   the exact WRAM/register representation is `07`/`08`'s own implementation-detail latitude, per
   this pipeline's usual division — `IP-1070`'s own package document already tracks comparable
   loop-position state (`GW_CUR_REGION`, `GW_BRAID_IDX`) that a counter can piggyback on or
   extend, at this ADR's discretion left unspecified beyond "some monotonic per-draw counter,
   scoped to this pass, never persisted").
3. **The perturbation is applied only to the value consumed for a decision** (the direction mask,
   the keep/prune comparison) — it is never written back into `TMP1`/`TMP2`. `gw_prng_step`'s own
   next call, whether from this pass or the biome loop, continues its own unperturbed sequence
   exactly as today.
4. **The Python oracle (`worldgen.py`) must mirror this perturbation step-for-step**, exactly as
   it already must mirror the carve/braid algorithm itself (`ADR-0012` point 7's lockstep
   discipline, extended here to the perturbation step specifically) — this is not a new
   obligation in kind, only in scope.

## Consequences

- **`gw_prng_step`'s own known weakness is not repaired by this ADR** — it remains exactly as
  degenerate as R113 describes, for any future caller. **This is a deliberate, recorded
  deferral, not an oversight**: fix (a) is explicitly named as the eventual real repair, gated on
  future explicit user authorization (per Decision point 1) and likely bundled with a save-format
  version bump if and when it ships. A future backlog entry should track this if a subsequent
  feature needs higher-quality randomness than a loop-local counter perturbation can provide.
- **Unblocks `IP-1070`** (`BL-0064`/`BL-0065`) — `07-implementation-planning`/
  `08-code-implementation` can resume with the carve phase's own already-validated design
  unchanged, adding only the counter-XOR perturbation at each of the two draw sites.
- **No GDS-04/GDS-07/GDS-09 delta needed** — `REGION_GRAPH`'s data format, `gw_prng_step`'s own
  interface/behavior for existing callers, and every existing WRAM address are all unaffected;
  the perturbation is entirely internal to `IP-1070`'s own new pass.
- **Does not itself implement anything** — per this pipeline's rules, an ADR records the
  decision; the actual counter-perturbation code, its `worldgen.py` mirror, and any
  `07`/`08`-level detail (which register/WRAM byte holds the counter, exact XOR placement) ship
  through the normal `07`→`08` path, gated by G3 as always. `IP-1070`'s own existing package
  document does not need re-planning from scratch — this ADR is a narrow addendum to its already-
  validated carve/braid algorithm, not a redesign of it.

## Related

- Refines the PRNG-consumption strategy `ADR-0009`/`ADR-0012` already assume, without amending
  either — `ADR-0009` point 3's determinism guarantee and `ADR-0012`'s own maze-algorithm
  decision are both unaffected and remain as-is.
- Grounded by [R113](../../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md) (root
  cause and candidate-fix comparison) and
  [R111](../../research/encyclopedia/R111-wram-banking-sm83-prng.md) (the original PRNG
  characterization this defect was never visible against).
- Unblocks `IP-1070`/`IP-1080` (`BL-0064`/`BL-0065`/`BL-0067`, all `SCHEDULED` pending this
  decision, per `00-pipeline-manager`'s own triage).

[^ref-r113]: See R113 §Implementation Guidance for the full cost/compatibility comparison this
ADR's Context section summarizes.
