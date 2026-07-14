# ADR-0018 — Finite-mode biome-blob clustering via per-super-cell positional hash, refining ADR-0009 point 2

**Status:** Accepted (2026-07-14)

## Context

[BL-0066](../../pipeline/backlog.md) (project owner, 2026-07-11): cluster biome assignment into
cohesive multi-region blobs — a "Forest area" spans several adjacent regions before drifting —
instead of today's independent per-region grammar-constrained draw. The owner's first-suggested
mechanism, seeding blob centers from the maze's own dead-end regions, was found to conflict
directly with [ADR-0012](ADR-0012-maze-shaped-region-adjacency.md) point 1's fixed pass ordering
(biome assignment runs *before* maze generation, entirely independent of it) — dead-end seeding
needs the opposite order. Not a wording ambiguity: a genuine architecture conflict, correctly
routed rather than patched around, filed as **CR-05** (`docs/requirements/01-functional-
requirements.md`, [RQ-03](../../requirements/03-requirements-review.md) finding #13) and left
un-baselined.

CR-05 was then folded into [BL-0082](../../pipeline/backlog.md) (streaming/infinite-world
generation) at the owner's own direction — correctly, since neither of CR-05's original
candidates (dead-end seeding, flood-fill) survives a streaming model, both assuming a bounded,
fully-known grid. [R114](../../research/encyclopedia/R114-streaming-world-generation-feasibility.md)
resolved that half by naming a **per-super-cell positional hash** technique: partition the grid
into fixed-size super-cells, derive each super-cell's own blob identity from
`hash(SEED, supercell_row, supercell_col)` — the same shift/XOR-only xorshift-reseed technique
already grounding this project's PRNG (R111/R113), no whole-grid pass required.
[ADR-0016](ADR-0016-streaming-infinite-mode-generation-architecture.md) adopted this for a new,
additive Infinite Mode. **The finite mode's own version of CR-05/BL-0066 remained separately
open** — R114's technique was named for Infinite Mode, and nothing had yet applied it back to the
finite mode's own generation pass.

**Direct user instruction, 2026-07-14:** "If there is a blob mechanism that works for infinite
mode, use that concept for the finite mode as well." This ADR records that decision.

## Decision

**Adopt the same per-super-cell `hash(SEED, supercell_row, supercell_col)` positional-hash
technique for the finite mode's own biome assignment, as a deterministic bias layered on top of
the existing grammar-constrained anchor+delta draw ([ADR-0009](ADR-0009-screen-graph-world-generation.md)
point 2) — not a replacement of it, and requiring no reordering of `ADR-0009`/`ADR-0012`'s passes.**

**This is the load-bearing reason the technique resolves CR-05 cleanly where the owner's original
dead-end-seeding idea could not: the hash is purely positional — a pure function of
`(SEED, supercell_row, supercell_col)`, available before any generation pass runs — so it needs
no maze, no whole-grid sweep, and no change to `ADR-0009`'s existing biome-first pass order.**
The conflict CR-05 originally surfaced is sidestepped entirely, not resolved by picking a side.

Concretely (grounded in the shipped `worldgen.py`/`generate_world` mechanics, confirmed by direct
code read):

1. **Partition the `scale`×`scale` grid into fixed-size super-cells.** Exact super-cell sizing is
   an implementation-time tuning question (see Consequences) — not fixed here, mirroring
   `ADR-0017`'s own precedent for leaving its density constant `K` to a later pass.
2. **Each super-cell's target biome-id (0–4, the existing `Water=0`…`Brick=4` axis, R212's
   linear grammar) is derived once via the shift/XOR-only reseed technique** `gw_prng_step`
   already implements, keyed on `SEED` XOR/shift-mixed with `(supercell_row, supercell_col)` —
   the identical construction `ADR-0016`/R114 already ground, reused here for a bounded grid
   rather than a streaming one.
3. **Per-region biome assignment keeps today's exact mechanics unchanged as the hard constraint**:
   region `(row, col)`'s legal range `[lo, hi]` is still computed exactly as `worldgen.py`'s
   `generate()` does today (intersection of the top/left neighbors' own biome-id ±1, clamped to
   `[0, 4]`) — this ADR does not touch that computation.
4. **Deterministic snap-to-blob, with the existing draw as fallback, not augmentation:** if the
   region's own super-cell target lies within `[lo, hi]` (i.e., the blob's biome is
   grammar-compatible at this position), the region's biome-id is **set directly to the target**
   — **no `gw_prng_step` draw is consumed for that region at all.** If the target lies outside
   `[lo, hi]` (grammar-incompatible at this exact position — necessarily true at a boundary
   between two differently-targeted super-cells), the region falls back to **today's unbiased
   `anchor + delta` draw, entirely unchanged**, consuming one `gw_prng_step` draw exactly as now.
5. **This produces the requested "cohesive blob" shape as an emergent property, not an imposed
   one:** super-cell-interior regions (whose clamp range comfortably contains the target) snap
   directly to a shared biome-id, reading as a wide, uniform area; boundary regions between
   differently-targeted super-cells naturally fall back to the existing gradual `±1`-per-step walk
   — exactly the gradient transition R212's grammar already requires (Water→Sand→Grass→Stone→
   Brick), with no separate transition-zone logic needed.
6. **Region `(0,0)`'s existing hardcoded `Grass` (biome-id 2) anchor is unaffected** — the blob
   bias, like today's existing loop, applies only from region index 1 onward.
7. **Determinism is unaffected, by construction.** Both the super-cell hash and the per-region
   snap/fallback decision are pure functions of already-deterministic inputs (`SEED`,
   `WORLD_SCALE`, coordinates, and the existing PRNG stream where the fallback draw fires) — no
   new non-reproducible input is introduced. `ADR-0009` point 3's existing "regenerate from
   `(seed, scale)`" guarantee is unaffected.
8. **The offline Python oracle (`worldgen.py`) must mirror this pass step-for-step**, exactly as
   it already mirrors the existing anchor-clamp loop — the same lockstep-PRNG discipline
   `ADR-0009`'s Consequences section already names, extended here to the new snap/fallback branch.
   Because the branch changes *whether* a PRNG draw fires per region, the oracle and the SM83
   routine must agree on the branch condition byte-for-byte, not merely on the draw's outcome.

## Consequences

- **`generate_world` (`asm_game.py`) needs a super-cell-hash pre-pass or inline per-region lookup
  added ahead of/alongside its existing anchor-clamp loop** — a future `07-implementation-
  planning`/`08-code-implementation` package's scope, not built by this ADR.
- **Super-cell size is not fixed by this ADR — a real, named tuning question**, flagged
  explicitly rather than silently assumed: `WORLD_SCALE` ranges 2–9 (4–81 regions), and a
  fixed-size super-cell tuned for a large streaming extent (R114's own 4×4/8×8 suggestion) would
  span or exceed the *entire* grid at small finite scales (e.g. `scale=2`'s 2×2 grid), collapsing
  to a single blob covering the whole world — not necessarily wrong (a small world reading as
  "mostly one biome" is a plausible, even desirable, outcome), but a real design choice
  `07-implementation-planning` must make deliberately, e.g. sizing the super-cell relative to
  `WORLD_SCALE` (so at least 2–3 distinct blobs exist at any supported scale) rather than a fixed
  constant. A new backlog recommendation should track this at implementation time.
- **`worldgen.py`'s oracle needs the equivalent Python mirror added** — the super-cell hash, and
  the snap/fallback branch condition exactly as decided above (point 8).
- **PRNG draw count per generation is no longer fixed at exactly one draw per non-root region** —
  it now varies with how many regions snap directly to their super-cell's target vs. fall back to
  the existing draw. This is a real, deliberate behavior change from today's shipped generator
  (which draws once per non-root region unconditionally) — any test or invariant that assumes a
  fixed per-region draw count (none currently baselined that this ADR is aware of; `T12`'s
  existing checks assert determinism/reachability/grammar-validity, not draw count) is unaffected
  in *kind*, but `07`/`08` should confirm no such assumption exists before implementing.
- **Unblocks `BL-0066`/`CR-05`** for the finite mode — the next `04-requirements-engineering`
  pass can derive the real `FR-xxxx` from this decision, mirroring `CR-06`'s own `03→04` routing
  precedent.
- **No `GDS-04`/`GDS-07`/`GDS-09` delta authored by this ADR** — the same deferral
  `ADR-0016`/`ADR-0017` recorded for the Infinite Mode decisions, for the same reason (the new
  "biome blob"/"super-cell" domain concept is named here but not yet formalized into the ladder;
  that is `04-requirements-engineering`'s scope once it derives the FR, or a dedicated `03` delta
  pass beforehand if the resulting FR needs one).
- **Does not itself implement anything** — per this pipeline's standing rule, an ADR records a
  binding design decision; the super-cell-hash pass, its Python oracle mirror, and the exact
  super-cell-size tuning ship through the normal `04`→`08` path, gated by G3 as always.

## Related

- Refines [ADR-0009](ADR-0009-screen-graph-world-generation.md) point 2 (the grammar-constrained
  biome draw this decision biases, not replaces) — does not supersede it; points 1, 3–7 are
  entirely unaffected.
- Does not touch [ADR-0012](ADR-0012-maze-shaped-region-adjacency.md) — the maze-generation pass
  and its own pass ordering relative to biome assignment are unaffected; this decision is exactly
  what makes that reordering unnecessary.
- Reuses, for the finite (bounded) mode, the identical technique
  [ADR-0016](ADR-0016-streaming-infinite-mode-generation-architecture.md) adopted for the
  additive Infinite Mode — a single shared mechanism across both modes, per the project owner's
  own direct instruction.
- Grounded by [R114](../../research/encyclopedia/R114-streaming-world-generation-feasibility.md)
  (the per-super-cell hash technique, already named for exactly this purpose — no new research
  pass needed) and [R212](../../research/encyclopedia/R212-wordless-environmental-storytelling-biome-grammar.md)
  (the linear biome-adjacency grammar this decision's snap/fallback branch preserves by
  construction).
- Resolves [CR-05](../../requirements/01-functional-requirements.md)/[BL-0066](../../pipeline/backlog.md).
