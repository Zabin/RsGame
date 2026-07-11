# ADR-0012 — Maze-shaped region adjacency (spanning tree + braid), refining ADR-0009 Decision point 1

**Status:** Accepted (2026-07-11)

> **Forward-pointer note (append-only, 2026-07-11):** an `IP-1070` implementation attempt found
> the shipped PRNG (`gw_prng_step`) degenerates under the many back-to-back draws this ADR's own
> carve/braid pass performs — see
> [ADR-0013](ADR-0013-maze-pass-prng-decorrelation.md), which decides a per-draw decorrelation
> technique scoped to this pass, without amending anything decided here (point 3's mod-4 draw and
> point 4's braid mechanism both stand exactly as written; ADR-0013 only adds how the drawn byte
> is perturbed before use).

## Context

[BL-0064](../../pipeline/backlog.md) (project owner, design discussion this session) asks to
replace `REGION_GRAPH`'s current adjacency model — every grid-adjacent region pair is always
connected, unconditionally, independent of the seed — with a **generated maze**: a randomized
spanning tree over the `scale`×`scale` region grid (guaranteeing full reachability) plus a
**braid pass** that reopens a fraction of the pruned edges (avoiding a single-path maze; adds
loops/shortcuts). This directly follows up on [`BL-0047`](../../pipeline/backlog.md)'s own
disposition, which explicitly anticipated exactly this request once grid navigation actually
worked end-to-end (`IP-9050`, 2026-07-11, closed that precondition). The owner's stated goal: an
overworld that reads as **distinct regions connected by paths**, in the spirit of Zelda/Pokémon
map design, not a uniformly open grid — and explicitly delegated the algorithm choice to
"research driven implementation," the same delegation pattern **D3** used for `ADR-0009`'s
original generation-algorithm choice.

**This refines `ADR-0009` Decision point 1; it does not reverse it.** Point 1's own text commits
only to "a graph of `scale`-determined region nodes... connected by adjacency edges" — it never
states every grid-adjacent pair must be connected. The shipped `worldgen.py`/`generate_world`
implementation chose the simplest member of that family (full connectivity) for the initial
procgen-world increment; this ADR makes the previously-unspecified edge-*selectivity* question
concrete, without contradicting anything Decision point 1 actually committed to. Points 2–7 of
`ADR-0009`'s Decision (grammar-by-construction, on-console generation, the existing PRNG, the
LCD-off generation window, `_zone_arrows`'s supersession, terrain-texture separation) are
**entirely unaffected** and remain as-is.

[R112](../../research/encyclopedia/R112-maze-generation-hardware-feasibility.md) (this session)
grounds three spanning-tree algorithm candidates against this project's existing constraints:
the shift/XOR-only, no-`DIV`/`MUL` xorshift PRNG (`R111`), and current live WRAM headroom
re-measured directly against the shipped tree (928 bytes used, 3168 bytes / 3.09 KiB free in
bank 0 — not R111's older pre-generation estimate). Its finding: randomized Kruskal and
randomized Prim both need a modulo-by-variable-count random draw this codebase's PRNG has no
native primitive for (a shrinking-edge-list shuffle and a variable-length-frontier selection,
respectively); randomized depth-first search / recursive backtracker needs only a mod-4 (`AND 3`
bitmask) draw at every step — cheaper than this codebase's own existing mod-3 biome-delta draw
(`worldgen.py`'s `_draw_delta`) — and its backtracking state can reuse `REGION_GRAPH`'s own
neighbor bytes as parent pointers, needing no separate stack array. WRAM/ROM budget does not
differentiate the three candidates (all comfortably affordable against the measured headroom).

## Decision

**Adopt randomized depth-first search / recursive backtracker, implemented iteratively (no
native `CALL`-based recursion — an explicit "current region" pointer, moving forward by carving
an edge and backward by re-reading the just-carved edge's own reverse direction, per R112's own
cited "store backtracking information in the maze itself" technique), as the spanning-tree
algorithm, followed by a braid pass over the pruned edges.**

**This decision is made directly from R112's hardware-cost comparison, without a supplementary
`02-research-game-design` pass on maze-quality/bias characteristics (DFS/backtracker's
long-corridor/low-branching bias vs. Kruskal's more locally-scattered pattern).** Reasoning,
recorded here so the call is a decision, not a shortcut: (1) WRAM/ROM headroom does not
differentiate the three candidates — the choice is decided on implementation cost and
correctness-risk grounds, both of which R112 already grounds decisively; (2) the mandatory braid
pass (BL-0064's own request, not optional) specifically exists to counteract a raw spanning
tree's dead-end/corridor bias by reopening loops — its presence substantially narrows the
*behavioral* gap between the three algorithms' raw output, the exact axis a maze-quality research
pass would otherwise need to weigh; (3) DFS/backtracker's implementation-cost advantage (no
modulo-by-variable-count operation anywhere in the algorithm, vs. a real, nontrivial gap for the
other two on this specific no-`DIV` CPU) is large enough, and R112's grounding of it specific
enough, to be dispositive on its own. If the shipped result's maze *feel* (post-braid) turns out
not to match the Zelda/Pokémon-style goal once played, that is exactly the kind of concrete,
evidenced finding a future `09-content-review`/playtesting pass should surface — not a reason to
front-load a second research pass against a still-hypothetical concern.

Concretely:

1. **Two independent passes over the same `scale`×`scale` grid, in the existing order.** Biome
   assignment runs first, **entirely unchanged** — it still reads each region's grid-fixed
   top/left neighbor (independent of maze connectivity) for its adjacency-grammar constraint
   window, exactly as `worldgen.py`'s `generate()`/`generate_world` already do. Maze-adjacency
   generation runs as a **second, orthogonal pass** over the same grid's edge set, populating
   `REGION_GRAPH`'s neighbor bytes. The two concerns do not interact — a region's biome-grammar
   compatibility with its grid neighbor holds regardless of whether that edge ends up
   maze-open or maze-blocked. This preserves the existing, working separation of concerns
   `ADR-0009` point 7 already established for biome-vs-terrain, extended here to
   biome-vs-connectivity.
2. **`REGION_GRAPH`'s own 5-bytes-per-region WRAM/ROM format is unchanged.** Byte 0 remains the
   biome-id; bytes 1–4 remain the up/down/left/right neighbor indices, `0xFF` = no neighbor. A
   maze-blocked-but-grid-adjacent edge is represented identically to a true grid-boundary edge —
   `0xFF` — at this data-format level; distinguishing the two cases for player-facing display is
   `BL-0067`'s own scope (a rendering-layer question, not a data-format one). **This means
   `dsr_p`/`draw_region_arrows` (`IP-1030`) and `check_zone_transition` (`IP-9050`) need zero
   code changes of their own** — both already consume `REGION_GRAPH`'s neighbor bytes generically
   (any value 0–80 as a valid neighbor, `0xFF` as none), with no assumption that a grid-adjacent
   pair is always connected. The entire downstream consumption chain already correctly
   generalizes to a sparser graph, for free.
3. **Per-step randomness: a single mod-4 (`AND 3`) draw** to pick a starting direction among the
   ≤4 grid-adjacent candidates at the current region, trying up to 4 directions in a fixed
   rotation from that start (skipping already-visited or off-grid neighbors) until an unvisited
   neighbor is carved or none remains (backtrack). No modulo-by-variable-count operation anywhere
   in the tree-building pass.
4. **Braid pass: a single `O(edges)` sweep after the tree is built.** For every grid edge *not*
   already in the spanning tree (≤`2×scale×(scale-1)`, 144 at `scale=9`), draw one PRNG byte and
   compare it against a **braid-fraction threshold** — a single-byte parameter, semantics "reopen
   this edge if the drawn byte is at or below the threshold." **This ADR establishes the
   mechanism and its byte-valued range; the threshold's actual default value and whether/how it
   becomes a player-facing parameter are `BL-0065`'s own scope**, not decided here. A
   provisional, non-binding suggestion for `BL-0065` to formalize: a moderate default (roughly a
   quarter of pruned edges reopened) as a reasonable starting point for "not a single-path maze,
   not the old fully-open lattice either," subject to revision once played.
5. **Reachability is preserved by construction, more strongly than before.** A spanning tree
   connects every region by definition — the existing "full reachability" domain invariant
   (`GDS-04`'s New domain rules, tested as a corpus property per `R305`'s extension) continues to
   hold, now as a structural guarantee of the algorithm itself rather than an incidental property
   of full-lattice connectivity. No test or invariant needs to be *relaxed* by this change; the
   guarantee's *mechanism* changes, not its truth.
6. **Determinism is unaffected.** Maze generation derives purely from `(SEED, WORLD_SCALE)`, the
   same inputs biome generation already uses — no new persisted state, `REGION_GRAPH` continues
   to regenerate from `(seed, scale)` alone on load, per `ADR-0009` point 3's existing
   determinism guarantee.
7. **The offline Python oracle (`worldgen.py`) must mirror the new maze-generation pass
   step-for-step**, exactly as it already mirrors biome generation — the same lockstep-PRNG
   discipline `ADR-0009`'s Consequences section already names, extended to the new pass, not a
   new obligation in kind.

## Consequences

- **`generate_world` (`asm_game.py`) needs a new maze-generation pass added** (spanning tree +
  braid), while its existing biome-assignment logic is untouched — a future `07-implementation-
  planning`/`08-code-implementation` package's scope, not built by this ADR (per this pipeline's
  standing rule: an ADR records the decision, not the code).
- **`worldgen.py`'s oracle needs the equivalent Python mirror added**, keeping `T12`'s existing
  determinism/reachability/grammar-validity corpus tests meaningful against the new algorithm —
  those tests' *properties* don't change (reachability/determinism/grammar-validity all still
  hold, per points 1/5/6 above), only the graph they're checked against gets sparser.
- **Zero changes required to `dsr_p`/`draw_region_arrows`/`check_zone_transition`** (point 2) —
  a direct, load-bearing benefit of `IP-1030`/`IP-9050` having already generalized both
  rendering and navigation to read `REGION_GRAPH` generically, before this decision was made.
- **Unblocks `BL-0065`** (braid-fraction/difficulty scaling variable — this ADR fixes the
  mechanism, leaves the default/UI to that item), **`BL-0066`** (biome-blob clustering — may
  consume this ADR's spanning tree's dead-ends as blob-center candidates, per the owner's own
  suggestion, or an independent flood-fill seeding, per that item's own design-time evaluation),
  and **`BL-0067`** (cosmetic 3-state edge indicator — needs a rendering-layer distinction between
  "maze-blocked but grid-adjacent" and "true grid boundary," both currently `0xFF` at the data
  level per point 2; that distinction must be computed at render time by re-deriving "is this a
  grid boundary" from `(row, col, scale)` arithmetic, comparing against whether `REGION_GRAPH`
  shows a live neighbor — a `BL-0067`-scoped rendering question, not a data-format change).
- **Does not itself implement anything** — per this pipeline's rules, an ADR records a binding
  design decision; the actual maze-generation routine, its Python oracle, and any GDS-04/GDS-07/
  GDS-09 deltas needed at implementation time ship through the normal `04`→`06`→`07`→`08` path,
  gated by G3 as always.

## Related

- Refines [ADR-0009](ADR-0009-screen-graph-world-generation.md) Decision point 1 (does not
  supersede it — see Context).
- Grounded by [R112](../../research/encyclopedia/R112-maze-generation-hardware-feasibility.md)
  (algorithm hardware-cost comparison) and [R111](../../research/encyclopedia/R111-wram-banking-sm83-prng.md)
  (existing PRNG/WRAM baseline).
- Unblocks `BL-0065`/`BL-0066`/`BL-0067` (all `DEFERRED` pending this ADR, per
  `00-pipeline-manager` run #69's triage).
