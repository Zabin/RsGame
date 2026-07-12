# R112 — Maze-Generation Algorithm Hardware Feasibility (Spanning Tree + Braid)

- **Document ID:** R112 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (SM83 instruction set — opcode-level cost of each candidate algorithm's
  own operations), R111 (the existing xorshift PRNG and current WRAM headroom this topic updates
  against the shipped generated-world tree, not the pre-generation estimate), R213 (the
  screen/graph-generation family this topic's candidates all operate within — R213 already
  recommended graph generation "on a 2D grid of cells where each cell can be connected from any of
  the four main directions," a framing that already permits selective, not-necessarily-full,
  adjacency; this topic grounds the hardware cost of actually exercising that selectivity)
- **Referenced By:** *(none yet — grounds `BL-0064`'s pending `03-architecture-design-synthesis`
  ADR-0009-amending decision)*
- **Produces:** a costed, evidence-grounded comparison of three spanning-tree-maze algorithm
  candidates (randomized Kruskal, randomized Prim, randomized depth-first search / recursive
  backtracker) plus a braid pass, for `03-architecture-design-synthesis` to decide between when it
  revisits `ADR-0009`'s current full-lattice-adjacency commitment
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R101, R111, R213, R305 (whichever algorithm is chosen needs an offline
  Python oracle mirror, following R305's existing determinism-testing pattern for `generate_world`)

## Purpose

Filed to ground `BL-0064` (backlog: "maze-shaped region adjacency for the procgen world," a
project-owner design request following up on `BL-0047`'s own disposition, which explicitly
anticipated this exact follow-up once grid navigation worked end-to-end — `IP-9050`, 2026-07-11).
The request: replace `REGION_GRAPH`'s current fully-connected adjacency (every grid-adjacent
region pair is always linked; `worldgen.py`/`generate_world` only randomizes each region's
biome-id) with a **generated maze** — a randomized spanning tree over the `scale`×`scale` region
grid (guaranteeing full reachability, an already-tested domain invariant) plus a **braid pass**
that reopens a fraction of the pruned edges (avoiding a single-path maze; adds loops/shortcuts).
This is an explicit amendment to `ADR-0009`'s Decision (today's full lattice is a deliberate
choice, not an oversight) — that amendment decision belongs to `03-architecture-design-synthesis`,
not this topic. This topic's job is narrower: **which spanning-tree algorithm is cheapest and
most natural to implement on real SM83 hardware, at new-game creation, within this project's
already-established PRNG and WRAM constraints** — so the architecture decision has real cost
numbers to weigh, not guesses.

## Scope

Three spanning-tree-maze algorithm families (randomized Kruskal, randomized Prim, randomized
depth-first search / recursive backtracker) and the braid post-process, evaluated for: PRNG
compatibility (does the algorithm's own randomness fit the existing shift/XOR-only, no-`DIV`
xorshift generator R111 established), WRAM state cost at `scale=9`'s worst case (81 regions), pass
structure/complexity relative to the existing single-pass `generate_world` baseline, and ROM
budget. **Out of scope:** whether to adopt a maze at all (`03-architecture-design-synthesis`'s
call), the braid-fraction/difficulty parameter's own UI placement (`BL-0065`), biome-blob
clustering (`BL-0066`), and edge-indicator tile art (`BL-0067`) — all three ride this topic's own
output once it lands.

## Concepts

**The current adjacency model is a full lattice, not a maze, and this is architecturally
deliberate.** `worldgen.py`'s `generate()` computes every region's `up`/`down`/`left`/`right`
neighbor purely from `(row, col, scale)` — every grid-adjacent pair is connected, unconditionally,
independent of the seed. `ADR-0009`'s own Decision point 1 commits to "a graph of `scale`-
determined region nodes... connected by adjacency edges," and R213 already established the
graph-on-a-grid family (citing `metazelda`/`GraphDungeonGenerator`, tools that lay a graph "on a
2D grid of cells where each cell can be connected from any of the four main directions") as the
right generation family — but the shipped implementation took that family's simplest member (full
connectivity) rather than its selective-adjacency variant. A maze is exactly that selective
variant: a spanning subgraph of the same grid, not a different graph family.

**Current live WRAM headroom in bank 0, measured directly against the shipped tree (not R111's
pre-generation estimate).** Confirmed by parsing `asm_game.py`'s own WRAM constant declarations:
the highest-addressed named allocation is `OAM_BUF` (`0xC300`, 160 bytes, ending `0xC3A0`) — this
position is unchanged since before world generation existed. Total live usage from `0xC000` to
`OAM_BUF`'s end is **928 bytes**; remaining headroom to bank 0's `0xD000` boundary is **3168 bytes
(≈3.09 KiB)**. This is nearly identical to R111's original ~3.1 KiB pre-generation estimate,
because every generated-world structure since (`REGION_GRAPH`, `KEYITEM_FLAGS`, `SCOREITEM_FLAGS`,
`GW_*`/`MM_*`/`SSE_*` scratch, `IP-9070`'s widened arrays) was fit into the gap *below* `OAM_BUF`,
not appended after it — the headroom figure below is therefore real, current, and independently
re-derivable from the shipped `asm_game.py`, not an estimate that predates the actual build.

**Randomized Kruskal's algorithm.** Considers all grid edges in random order; adds an edge to the
spanning tree only if its two endpoints are not already connected (a **union-find/disjoint-set**
query), guaranteeing no cycles and full connectivity once every edge has been considered.[^1]
State: a **parent array, 1 byte/region (81 bytes worst case at `scale=9`)** — region indices fit a
byte, and a naive union-find (no rank/path-compression) is acceptable since this runs once, at
new-game creation, not per-frame; worst-case `find()` chain length is bounded by region count
(81), trivial against a one-time cost the existing `generate_world` already pays a comparable
order of magnitude for. **The hard part on SM83 is the "random order" itself**: with up to
`2×scale×(scale-1)` grid edges (144 at `scale=9`), producing a uniformly shuffled edge sequence
without a hardware `DIV`/`MUL` (a true Fisher-Yates shuffle needs a uniform random index into a
*shrinking* range, i.e. modulo by a runtime value that changes every draw) is exactly the class of
operation R111/R213 already flagged xorshift as unsuited for on its own — this is a real,
non-trivial cost this algorithm imposes that the other two candidates handle more cheaply (Prim
partially, DFS/backtracker fully, see below).

**Randomized Prim's algorithm.** Grows a single connected region from a start node; maintains a
**frontier** of candidate edges connecting the tree to not-yet-visited regions; repeatedly picks a
random frontier edge, adds it (and its new endpoint) to the tree, and updates the frontier.[^1]
Produces mazes "less biased" than Kruskal's, with shorter average dead-ends and more local
variation, at the cost of "extra memory and bookkeeping to manage the frontier list."[^1] State: a
visited flag per region (81 bytes, or bit-packed to 11 bytes) plus a **frontier list of bounded
but variable size** (each newly-tree'd region contributes up to 4 candidate edges; empirically
bounded well under the full edge count for a grid, but not a fixed constant). **This is the
weakest SM83 fit of the three**: picking a uniformly random *valid* entry from a frontier list
that both grows and shrinks every iteration means a fresh modulo-by-current-count draw at every
one of ~81 steps — worse than Kruskal's single up-front shuffle, since Kruskal's randomization
cost is paid once (before the main loop) while Prim's is paid every iteration.

**Randomized depth-first search / recursive backtracker.** Starts at a region, repeatedly moves to
a random *unvisited* neighbor (carving that edge into the tree), pushing the path onto a stack;
when no unvisited neighbor exists, backtracks (pops the stack) until a region with an unvisited
neighbor is found again, continuing until every region has been visited.[^2] Produces mazes
"biased towards... low branching factors and many long corridors" — easy to find the way back to
the start, harder to find any other specific point.[^3] State, naively: a visited flag per region
(81 bytes, or 11 bytes bit-packed) plus an explicit backtracking stack, worst case 81 entries (one
per region, for a maximally snaking traversal) — but **the backtracking information does not need
a separate stack array at all**: a cited implementation note observes recursive-backtracker mazes
can be "rearranged into a loop by storing backtracking information in the maze itself,"[^2]
i.e. as parent pointers. This project already builds exactly that structure as a side effect —
`REGION_GRAPH`'s own neighbor bytes, written as each edge is carved, **are** the parent-pointer
graph; backtracking is "follow the edge back the way it was carved," needing no WRAM beyond the
81-byte (or 11-byte packed) visited flags. **Per-step randomness is also the cheapest of the
three**: at most 4 candidate directions exist at any region, so picking a random starting
direction is a single `AND 3` bitmask (mod-4, a power of two — no compare/subtract loop at all),
strictly *cheaper* than this exact codebase's own existing PRNG idiom (`worldgen.py`'s
`_draw_delta`, a mod-3 draw implemented as a compare-subtract loop since 3 is not a power of two).
Trying up to 4 directions in a fixed rotation from that random start (skipping already-visited or
off-grid neighbors) needs no modulo-by-variable-count operation anywhere in the algorithm.

**Braid pass — algorithm-agnostic, adds cheaply to any of the three above.** A "braid" maze is one
with reduced or zero dead ends, produced by re-opening a chosen fraction of the edges a spanning
tree pruned, rather than removing dead ends after the fact;[^4] partial braiding (some dead ends
kept, some removed) is the normal case, controlled by a single probability/threshold
parameter.[^4] Mechanically: iterate every grid edge once (≤144 at `scale=9`); for each edge *not*
already in the spanning tree, draw one PRNG byte and compare it against a fixed threshold (the
braid-fraction parameter `BL-0065` names) to decide keep-or-discard. This is a single additional
`O(edges)` pass, structurally identical in shape to the existing `draw_region_arrows`'s own
"for each of up to 4 neighbor directions, do X" loop (`IP-1030`) and `IP-9050`'s new
`czt_region_hl` neighbor-offset pattern — a close, already-shipped precedent for this exact loop
shape. It needs no persistent WRAM beyond a transient loop counter (comparable to `GW_REGION_IDX`'s
existing transient-scratch role during `generate_world`), and its cost is identical regardless of
which of the three tree-building algorithms produced the tree it's braiding.

## Operational Context

`generate_world` (`asm_game.py`) today runs as a single `O(scale²)` row-major pass, stepping the
existing xorshift PRNG once per region, entirely under the same LCD-off bracket
`do_screen_redraw` already uses for full-screen work (R102's convention, R111's recommendation,
already followed) — this is a **one-time cost at new-game creation**, not a per-frame budget, the
same class of cost `check_zone_transition`/`setup_zone_collects` pay once per zone-entry, not
every frame. Any of the three candidate algorithms above stays in this same cost class: worst-case
work is bounded by region count (81) or edge count (144), both small constants comparable to or
smaller than the region count `generate_world` already iterates today — no new "safe window"
convention or frame-budget renegotiation is implied by adopting any of them. This is a materially
different backtracking profile than R213's own WFC caution ("no native stack-heavy backtracking
budget... full per-tile WFC... poor fit") — WFC's backtracking is contradiction-driven and
potentially unbounded (retry until a global constraint set is satisfiable); a maze's backtracking
(Kruskal has none; Prim has none; DFS/backtracker's is monotonically bounded by region count, each
region visited exactly once) is bounded by construction and cannot blow up.

## Implementation Guidance

- **Randomized DFS/recursive backtracker is the strongest SM83 fit of the three**, on hardware-cost
  grounds alone (not a final pick — that is `03-architecture-design-synthesis`'s call, informed by
  this comparison): its per-step randomness (≤4 directions) needs only a mod-4 `AND 3` mask, no
  modulo-by-variable-count operation anywhere, and its backtracking state can be the
  already-planned `REGION_GRAPH` neighbor bytes themselves rather than a separate stack array —
  the cheapest total WRAM footprint of the three (visited flags only: 81 bytes flat, or 11 bytes
  if bit-packed against the existing `LD`/`AND`/shift primitives R101 already grounds).
- **Do not implement true CPU-stack recursion (`CALL`) for the backtracker** — follow the cited
  "rearrange into a loop, store backtracking info in the maze itself" pattern[^2] instead: an
  explicit loop with a "current region" pointer, moving forward by carving an edge and moving
  backward by re-reading the just-carved edge's own reverse direction. This avoids any recursion-
  depth concern entirely, not just mitigates it.
- **If Kruskal is chosen instead** (its more locally-scattered, "high randomness" corridor pattern[^1]
  may be judged a better visual/gameplay fit despite the higher hardware cost — a
  `03-architecture-design-synthesis`/`02-research-game-design` call, not this topic's), budget for
  a **union-find parent array, 1 byte/region (81 bytes worst case)**, and resolve the edge-
  shuffling cost explicitly rather than assuming a textbook Fisher-Yates is free — a
  rejection-sampling scheme (draw a random edge repeatedly, skip if already processed, accept
  otherwise) avoids the shrinking-range modulo problem at the cost of a bounded-but-unpredictable
  number of retries; size that against the existing frame/timing budget before committing.
- **Prim is not recommended** against either alternative for this specific hardware target: its
  per-iteration variable-length-frontier modulo cost is paid at every one of ~81 steps (vs.
  Kruskal's one-time shuffle cost, or DFS/backtracker's constant ≤4-direction cost), for maze
  characteristics ("less biased," shorter dead-ends[^1]) that do not obviously outrank the other
  two for this project's stated goal (Zelda/Pokémon-style distinct areas with paths between them,
  not minimizing dead-end frequency specifically).
- **The braid pass is a fixed cost regardless of which tree algorithm is chosen** — implement it
  as its own pass after the tree is built, structurally mirroring `draw_region_arrows`'s existing
  4-direction sweep; a single PRNG-byte-vs-threshold comparison per non-tree edge, no new WRAM
  beyond a transient loop counter.
- **Current bank-0 headroom (3168 bytes / 3.09 KiB, measured directly against the shipped tree,
  not estimated) comfortably affords any of the three candidates' worst-case state** (81–288 bytes
  depending on algorithm and packing choice) — WRAM budget does not differentiate between the
  three; algorithm-choice should be decided on PRNG/complexity fit (above) and maze-quality/
  gameplay-feel grounds (`02-research-game-design`'s territory), not WRAM pressure.
- **ROM headroom** (10552 bytes / ~10.3 KiB free against the 32768-byte budget, per the current
  build) is similarly non-binding — none of the three candidates' code size is likely to approach
  a meaningful fraction of that margin, comparable in scale to `generate_world`'s own existing
  routine size. Confirm at implementation time with a direct build, per `BL-0019`'s standing
  ROM-headroom-watching convention — not re-estimated here.
- **Whichever algorithm is chosen needs an offline Python oracle mirror** before implementation,
  following `R305`'s existing determinism-testing pattern for `generate_world` (`worldgen.py`) —
  the oracle and the SM83 routine must step the same PRNG the same number of times in the same
  order to stay in lockstep, exactly as today's biome-generation oracle does.

### Sources
[^1]: [Maze Generation Algorithms: A Comparative Research](https://www.scitepress.org/Papers/2025/143608/143608.pdf); [Maze Generation Algorithms Explained: Backtracking, Prim's, and Kruskal's](https://www.htmlmaze.online/blog/maze-generation-algorithms-explained); [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm) (via `WebSearch` summary — direct fetch of `en.wikipedia.org` returned HTTP 403 this session, the same class of block R111 encountered on `gbdev.io`; corroborated across the ≥2 independent sources listed here, consistent with this project's existing single-source-flagging discipline); accessed 2026-07-11.
[^2]: [Recursive Backtracker Maze Generator — Miklix](https://www.miklix.com/mazes/maze-generators/recursive-backtracker); [Maze Generation With Depth-First Search and Recursive Backtracking — Jake Mills, Medium](https://medium.com/swlh/maze-generation-with-depth-first-search-and-recursive-backtracking-869f5c4496ad); accessed 2026-07-11 via `WebSearch` summary (direct fetches 403'd).
[^3]: [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm), via `WebSearch` summary; accessed 2026-07-11.
[^4]: [Braiding Mazes — Mazes for Programmers (Jamis Buck), O'Reilly](https://www.oreilly.com/library/view/mazes-for-programmers/9781680501315/f_0066.html); [Maze Generation: Hunt-and-Kill algorithm — Buckblog](https://weblog.jamisbuck.org/2011/1/24/maze-generation-hunt-and-kill-algorithm); accessed 2026-07-11 via `WebSearch` summary (direct fetch 403'd).

**Single-source flag:** the WRAM headroom figures (928 bytes used / 3168 bytes free) are **not**
externally sourced — they are directly re-derived from the shipped `asm_game.py`'s own WRAM
constant declarations this session (a Tier-A source per this skill's own methodology, matching
R111's precedent of treating this project's verified code as primary evidence), not a citation
that could be single- or multi-sourced externally. All maze-algorithm characterization claims
([^1]–[^4]) rest on `WebSearch`-summarized secondary sources after repeated direct-fetch HTTP 403s
(`en.wikipedia.org`, `courses.cs.washington.edu`, `astrolog.org` all blocked this session) — the
same environmental constraint R111/R213 already documented, not specific to this topic. Each claim
above is corroborated across at least two independent search results where stated; the "rearrange
into a loop" backtracking-storage technique ([^2]) rests on a single corroborating pair of
sources describing the same well-known technique, not a single outlier claim.

## Feature Mapping

*(No `FS-xxx`/`FEAT-xxxx` authored yet — this grounds `BL-0064`'s pending `03-architecture-
design-synthesis` ADR-amendment decision, one step upstream of any feature specification.)*

## Related Topics

R101 (opcode-level cost of each candidate's own operations — `AND`, compares, byte-array
indexing) · R111 (the existing PRNG and current WRAM headroom this topic re-measures against the
shipped, not pre-generation, tree) · R213 (the graph-generation family this topic's candidates all
operate within — R213 already flagged selective grid-cell connectivity as a legitimate variant,
not a new family) · R305 (the reference-generator oracle pattern whichever algorithm is chosen
must mirror, exactly as `generate_world`'s biome assignment already does).
