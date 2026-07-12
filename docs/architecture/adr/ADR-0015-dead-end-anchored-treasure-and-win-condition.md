# ADR-0015 — Dead-end-anchored treasure placement and scale-count win condition

**Status:** Accepted (2026-07-12)

## Context

[BL-0093](../../pipeline/backlog.md) (project owner, direct decision, resolving
[BL-0081](../../pipeline/backlog.md)/[R215](../../research/encyclopedia/R215-procgen-win-condition-design.md)):
the shipped win condition (`CARROTS_COUNT == 9`) is an unexamined holdover from the pre-procgen
fixed 3×3/9-zone map. `FEAT-9000`'s procedural world generation replaced the fixed map with a
`WORLD_SCALE`×`WORLD_SCALE` grid (2–81 regions) and, per `GDS-04`'s existing domain rule, placed
exactly one `KeyItem` in **every** region — but the victory threshold was never revisited. A
player can win by collecting any 9 of up to 81 generated KeyItems, from regions adjacent to spawn,
without meaningfully navigating the generated world or its maze (`ADR-0012`).

[R215](../../research/encyclopedia/R215-procgen-win-condition-design.md) surveyed four
win-condition conventions (scale-relative count, percentage threshold, fixed goal region, hybrid)
and measured the generated world's own pre-braid spanning-tree dead-end distribution
(`worldgen.py` oracle, 200 seeds/scale). The owner's own resolution, reviewing that data directly,
combines a fixed scale-proportional target count with dead-end-prioritized placement — a fifth
shape not among the original four, closer in spirit to candidate C (tie the goal to maze
topology) but keeping candidate A's simplicity (a fixed count, not a new "reach a place" mechanic).

**This is a binding decision on two previously-independent systems that must now interact**:
`generate_world`'s KeyItem-placement behavior (today: universal, one per region, entirely
determined by each region's biome-family screen template — no generation-time placement decision
exists at all) and the maze-carve pass (`ADR-0012`, `IP-1070`) — the KeyItem-placement decision
must now read the maze-carve pass's own intermediate state (spanning-tree leaf status) at an
exact point in its pipeline, before that state is consumed by the braid pass.

## Decision

**1. KeyItem placement becomes selective, not universal, decided at generation time from the
pre-braid spanning tree's own leaf structure, with a random-fill fallback.**

- Target count: exactly `WORLD_SCALE` KeyItems per generated world (not `WORLD_SCALE²`/region
  count) — 2 at the minimum scale, 9 at the maximum, a small number by construction at every
  scale, matching `R206`'s session-length guidance and, at the shipped default scale, numerically
  identical to the value already in play today.
- Placement priority: at the exact moment the spanning-tree carve completes and **before** the
  braid pass runs (`maze_carve_done`, prior to `maze_prune` in `asm_game.py`'s pass ordering;
  `_carve_maze`, prior to its own braid loop, in `worldgen.py`'s oracle mirror) — enumerate every
  region whose spanning-tree degree is exactly 1 (a leaf: no other region's `parent_dir` points to
  it, and it is not the root). This snapshot must happen at this exact pipeline point because the
  braid pass can reopen pruned edges, changing a region's `REGION_GRAPH`-visible degree after the
  fact — "dead end" for placement purposes means "spanning-tree leaf," a property of the tree, not
  of the final braided graph.
- If the pre-braid leaf count is `>= WORLD_SCALE`: place all `WORLD_SCALE` KeyItems among the leaf
  regions (a further random or deterministic selection among leaves when the leaf count exceeds
  the target — the exact selection rule among multiple eligible leaves is an implementation-level
  choice, not decided here, so long as it is deterministic from `(SEED, WORLD_SCALE)`).
- If the pre-braid leaf count is `< WORLD_SCALE` (**confirmed the common case, not a rare edge
  case** — R215's own measured data shows some seeds have zero pre-braid leaves at every
  `WORLD_SCALE` from 2 through 7): place a KeyItem at every leaf region, then fill the remainder
  with additional regions chosen randomly (excluding regions already selected) until the total
  reaches `WORLD_SCALE`.
- This decision is made once, at generation time, and does not change for the life of the
  generated world (consistent with `REGION_GRAPH`'s own "generated once, not regenerated mid-game"
  lifecycle, `ADR-0009`).

**2. Win condition: collect all `WORLD_SCALE` KeyItems** (a fixed target read from live
`WORLD_SCALE` state, not a hardcoded constant) — replaces `CARROTS_COUNT == 9`'s literal-9 check.
Scale-and-world-size-agnostic by construction: the check never references region count, so it
requires no revision if a future increment changes how regions/world size are computed (including
the deferred infinite/streaming-world variant, `BL-0094`, which replaces this fixed-target shape
entirely rather than needing it generalized further).

**3. `GDS-04`'s existing domain rule "exactly one `KeyItem` per `Region`" (added by the
2026-07-09 procgen-world delta) is superseded, not amended in place** — a `Region` now has **zero
or one** `KeyItem`, decided at generation time per this ADR, not universally one. The
"structurally guaranteed by the generator itself" framing that rule used remains true in spirit
(the *count* — `WORLD_SCALE` — is still generator-guaranteed, exactly as before), but the
per-region *presence* guarantee it stated no longer holds and must be corrected in `GDS-04`'s own
text (this ADR's Consequences name the exact edit), not left silently stale.

**4. Data-model concept, not byte layout:** the game needs a new way to represent "this region has
no KeyItem at all," distinct from `KeyItemFlags`' existing "collected / not yet collected"
semantics (today a 0/1 bitmap; a region with no KeyItem cannot be represented in that domain
today). This ADR names the **concept** the data model needs — a per-region tri-state (no item /
item present, uncollected / item present, collected), or an equivalent representable however
`07-implementation-planning` finds cheapest against the real `KEYITEM_FLAGS`/`ZONE_COLLECTS` code
— and deliberately does not choose the byte-level encoding (a new bitmap vs. widening
`KEYITEM_FLAGS`'s value domain vs. another shape) — that choice belongs to `07`/`08` against the
real source tree, per this pipeline's own architecture/implementation boundary.

**Deferred, not decided here — filed separately per the owner's own scoping ([BL-0094](../../pipeline/backlog.md)):**
the infinite/streaming-world variant (treasure only at dead ends, no random-fill fallback, win
condition replaced by a persisted top-3 high score of KeyItems collected) is a distinct future
decision, blocked on `BL-0082`'s own unresolved streaming-generation feasibility research. This
ADR's Decision applies only to the finite, currently-shipped generation model.

## Consequences

- **`generate_world` (`asm_game.py`) needs a new placement pass inserted between the spanning-tree
  carve and the braid pass** — reads `GW_MAZE_STATE`'s parent-direction bits (already computed by
  `IP-1070`'s carve phase, confirmed still resident in WRAM at that pipeline point — its own
  comment already notes it is "transient, meaningless outside a `generate_world` call" but is not
  physically cleared until the *next* `generate_world` call, so it remains readable immediately
  after `maze_carve_done`) to compute per-region leaf status, then decides and records the
  `WORLD_SCALE`-sized KeyItem placement set before `maze_prune` runs. A future `07`/`08` package's
  scope — not built by this ADR.
- **`setup_zone_collects` (the routine that currently unconditionally spawns each region's
  biome-template KeyItem entry) must consult the new per-region presence decision** before
  spawning a KeyItem — today it spawns one unconditionally for every region, gated only by
  `KEYITEM_FLAGS`' collected/not-collected bit.
- **The victory check (`check_complete` or equivalent) must read `WORLD_SCALE` instead of a
  hardcoded `9`.**
- **`worldgen.py`'s oracle needs the equivalent Python mirror added** — placement decision,
  leaf-detection, and random-fill fallback, in the same lockstep-PRNG discipline every other
  generation pass in this codebase already follows (`ADR-0009`'s Consequences, extended here).
- **`GDS-04`'s "exactly one `KeyItem` per `Region`" domain rule needs a corrective delta** (this
  synthesis pass's own scope, applied below) — the entity model's `Region`↔`KeyItem` cardinality
  changes from exactly-one to zero-or-one, generator-decided.
- **`GDS-07`'s data model needs a delta** naming the new per-region-presence concept (this
  synthesis pass's own scope, applied below) — the exact WRAM encoding is left to `07`.
- **Unblocks `BL-0050`** (the MAP/status-screen redesign) indirectly, by giving it a concrete,
  small, always-fully-enumerable target set (`WORLD_SCALE` KeyItems, each individually
  nameable/locatable) to display progress against — a real design input for that future work,
  not itself resolved here.
- **Standing instruction ([BL-0095](../../pipeline/backlog.md)):** this decision is not
  permanently fixed — the owner asked for it to be re-checked at future `11-release-readiness`
  passes as other components (the MAP redesign, any infinite-mode work) come together.
- **Does not itself implement anything** — the actual generation-pass code, the Python oracle
  mirror, the `setup_zone_collects`/victory-check edits, and the exact `GDS-07` byte-level
  encoding ship through the normal `04`→`06`→`07`→`08` path, gated by G3 as always.

## Related

- Builds on [ADR-0012](ADR-0012-maze-shaped-region-adjacency.md) (the spanning-tree-plus-braid
  generator whose intermediate state this decision consumes) — does not amend or supersede it;
  the maze algorithm itself is unchanged.
- Builds on [ADR-0009](ADR-0009-screen-graph-world-generation.md)/[ADR-0010](ADR-0010-seed-scale-model.md)
  (the generation determinism and seed/scale model this decision's own determinism guarantee
  depends on).
- Grounded by [R215](../../research/encyclopedia/R215-procgen-win-condition-design.md) (the
  win-condition convention survey and the measured pre-braid dead-end distribution this decision's
  fallback rule is evidenced against).
- Resolves [BL-0081](../../pipeline/backlog.md)/[BL-0093](../../pipeline/backlog.md). Files
  [BL-0094](../../pipeline/backlog.md) (deferred infinite-world variant) and
  [BL-0095](../../pipeline/backlog.md) (standing revisit instruction) as separate, not decided
  here.
