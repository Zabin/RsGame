# R114 — Streaming/On-the-Fly World Generation Hardware Feasibility

- **Document ID:** R114 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (SM83 instruction set — no hardware `MUL`/`DIV`, the constraint that rules
  out several standard hashing techniques), R111 (the existing xorshift PRNG and `SVBK` banked-WRAM
  path, both load-bearing here), R112 (the shipped maze algorithm's own hardware-cost framing, which
  this topic extends from "generate once, globally" to "generate lazily, locally"), R113 (the
  shipped PRNG's own degeneracy history — any new per-region seeding scheme must not reintroduce
  it), R213 (the graph-on-a-grid generation family this topic's local variant still operates
  within), ADR-0009/ADR-0012/ADR-0013 (the binding decisions this topic's findings would amend if
  streaming generation is adopted), `IP-1021`/`ADR-0015` (the just-shipped dead-end-anchored win
  condition, whose own global full-graph sweep this topic finds is not streaming-compatible as
  written)
- **Referenced By:** *(none yet — grounds `BL-0082`'s pending `02-research-game-design` follow-on
  and, if adopted, a future `03-architecture-design-synthesis` ADR)*
- **Produces:** a direct answer to whether `generate_world`'s two load-bearing global algorithms
  (sequential biome-anchor-clamp, backtracking spanning-tree carve) are representable in a
  streaming/local form at all; concrete SM83-compatible alternatives where they are; WRAM/ROM/
  compute cost figures for whichever alternative gets chosen; a hardware-feasibility answer to
  `BL-0066`'s widened scope (does per-region deterministic blob-clustering survive a streaming
  model)
- **Feature Mapping:** *(none yet — this is exploratory/foundational research, not yet tied to any
  `FS-xxx`)*
- **Related Topics:** R101, R111, R112, R113, R213, R215 (the win-condition research this topic's
  own finding about `IP-1021`'s global sweep directly bears on, connecting to `BL-0094`'s already-
  deferred infinite-mode design)

## Purpose

Filed to ground `BL-0082` (project owner: "how the procgen architecture might be able to build the
map on the fly as the player moves... with the goal that a theoretical infinite map could be
played"). The request names its own hardest question directly: **whether `GW_MAZE_STATE`'s
backtracking spanning-tree carve — which currently assumes global visited-state across the whole
graph — is representable in a streaming/local fashion at all**, and what the WRAM/ROM/compute cost
of doing so would be on real SM83 hardware. This topic answers that question first, since (per the
owner's own framing and this session's task instructions) it gates whether the design half
(`02-research-game-design`: what "infinite" means for win conditions) is worth pursuing at all.
**Scope explicitly widened (2026-07-13, project owner direct instruction):** must also evaluate
whether `BL-0066`'s two candidate biome-blob-clustering strategies (dead-end seeding, N-random-point
flood-fill) — both of which assume a bounded, fully-known grid — survive a streaming model, or
whether a different clustering concept (e.g. a per-region deterministic blob-id derived purely from
`(seed, region coordinate)`) is needed instead.

## Scope

The hardware-feasibility half only: whether the *shape* of the current generation algorithms can be
made local (representable per-region from `(seed, row, col)` plus already-materialized neighbor
state, without replaying global history), what SM83-compatible technique would make each piece
local, and the resulting WRAM/ROM/compute cost against this project's already-measured budgets.
**Out of scope:** what "infinite" means for win conditions, biome-blob aesthetics/shape quality,
and any UI/save-format decision beyond the raw feasibility question — all three are
`02-research-game-design`'s and `03-architecture-design-synthesis`'s territory, per this session's
own task framing. This topic also does not decide *whether* to adopt streaming generation — that
remains `03-architecture-design-synthesis`'s call, informed by the cost/risk picture below.

## Concepts

**The current algorithm has exactly two load-bearing dependencies on global, sequential state —
identifying them precisely is the actual research question, not a general "is procgen hard"
question.** Direct code read of `generate_world` (`asm_game.py:1366`–, mirrored in `worldgen.py`):

1. **Biome assignment is a raster-scan chain, not a positional function.** Each region's biome is
   drawn as `anchor + PRNG_delta`, clamped to `[0,4]`, where `anchor` is the **immediately-preceding
   region in generation order** — the left neighbor if `col>0` (`asm_game.py:1399-1404`), else the
   region directly above via `GW_TOP_ROW[col]` (`:1405-1408`), and if both a row and column
   predecessor exist, the result is further clamped against *both* (`:1437-1441`). The PRNG itself
   also advances **once per region, in a single global stream** seeded once at generation start
   (`gw_prng_step`, stepped from `TMP1`/`TMP2`, `:1412`). This means region `(row, col)`'s biome
   value is a function of *the entire generation history from `(0,0)` up to that point* — not of
   `(seed, row, col)` alone. Two consequences: (a) a region cannot be materialized independently of
   its neighbors' own materialization order, and (b) the PRNG draw a given region "consumes" depends
   on how many regions were generated before it, which for an unbounded world has no fixed count.
2. **Maze connectivity is a global backtracking DFS spanning tree, not a local rule.** The carve
   pass (`asm_game.py:1487`–, `ADR-0012`) starts at region 0, walks to a random *unvisited* neighbor
   via `REGION_GRAPH`'s own neighbor bytes, and **backtracks along already-carved edges** when no
   unvisited neighbor remains, continuing until every region is visited (`GW_MAZE_STATE`'s `bit 7`
   visited flag, `R112`). "Every region is visited" has no meaning for an unbounded grid — there is
   no terminating condition, and the backtrack step can walk arbitrarily far back through history
   that a streaming implementation would have already discarded.

**These are genuinely different problems from "is a maze/biome-grid too expensive to compute on an
8-bit CPU" — they are algorithm-shape problems.** Both algorithms are already cheap in the
hardware-cost sense R112 already established (bounded per-region work, no `DIV`/`MUL`, small
constant state). The obstacle to streaming is that **neither algorithm's per-region output is
currently a pure function of that region's own coordinates** — both require sequential replay from
a fixed origin. This is exactly the property that must change for streaming/on-demand generation
and revisit-consistency (walking away from a region and back must reproduce the identical result)
to both hold simultaneously.

**A proven SM83-compatible technique exists for making a value positionally deterministic: hash
the coordinates into a fresh, independent PRNG seed, without multiplication.** Chunk-based
open-world games solve exactly this problem by hashing chunk coordinates into a per-chunk seed —
"seeding a random number generator with concatenated coordinates... to generate deterministic
content placement within sectors," so "any world coordinate can be hashed... into chunk space" and
"the same seed will always produce the same results."[^1] The standard implementations (FNV-1a,
Minecraft's own per-chunk seeding) use integer **multiplication** by a prime constant as their
mixing step[^1] — **not available on SM83** (R101: no hardware `MUL`/`DIV`; every existing PRNG/
biome/maze routine in this codebase already works around this, `ADR-0013`/R113). The workaround is
already this project's own established pattern: `gw_prng_step`'s xorshift construction uses only
shift/XOR (R111), and `ADR-0013`'s own fix for PRNG degeneracy under repeated draws already
demonstrates XOR-mixing a loop-local counter into a shared stream to decorrelate it. The same
technique — XOR/shift-mixing `(SEED, row, col)` together into a fresh xorshift seed, entirely
without multiplication — is a direct, already-proven-on-this-hardware way to make any per-region
value (biome candidate, blob-id, maze bias) a pure function of `(seed, row, col)`, discarding all
history dependence. Xorshift-family combination via shift/XOR (not addition or multiplication) is
independently corroborated as sound practice for combining PRNG state.[^2]

**A proven, purely local, "no memory at all" maze algorithm already exists — the Binary Tree
algorithm — but its own shape conflicts with this session's just-shipped win condition.** The
Binary Tree maze algorithm "is the only one with the ability to generate a perfect maze without
keeping any state at all... it can build the entire maze by looking at only a single cell at a
time" — for every cell, carve a passage either north or west (a fixed, coordinate-independent
choice of direction pair), determined by one PRNG draw local to that cell.[^3] Because each cell's
connectivity depends only on its own coordinates (never on a neighbor's already-decided state or
a global visited set), "if you can guarantee that for any given cell you will always carve a
particular direction, you never need to keep any of the maze in memory... you could create
infinitely large mazes in very little memory."[^3] This is a direct, hardware-proven existence
proof that a purely local, streaming-compatible, revisit-consistent maze algorithm is possible in
principle — but it comes with a **named structural bias directly relevant to this project's own
just-shipped mechanic**: the algorithm "has a strong north-west bias... two of the four sides of
the maze will be spanned by a single corridor... there are no dead-ends (and never will be any
dead-ends) facing either north or west."[^3] `IP-1021` (this session, `FR-9160`/`ADR-0015`) just
shipped a win condition built entirely on **prioritizing dead-end regions** for treasure placement,
and `BL-0094` (the already-filed, deferred infinite-mode design) explicitly carries that same
dead-end-only placement rule forward unmodified. A maze algorithm with zero dead-ends in two of
four directions would systematically bias treasure placement toward the remaining two directions —
a real, concrete conflict between "cheapest streaming-compatible maze algorithm" and "the win
condition this project already committed to," not a hypothetical one.

**The Growing Tree algorithm family is the middle ground, but revisit-consistency is not free for
it.** Growing Tree generalizes recursive-backtracker/Prim/others by maintaining an active-cell list
and a selection strategy for which cell to extend from next;[^4] R112 already grounds this family's
per-step hardware cost. Because its active-list can, in principle, be bounded to a small window
(the region radius around wherever generation is currently focused) rather than the whole graph,
it does not require unbounded backtracking history the way the shipped recursive-backtracker does
— but **the maze shape it produces depends on the order cells are added to the active list**, and
if that order is driven by "whichever region the player approaches next," walking away and
returning by a different path could visit/carve the frontier in a different order, in principle
producing a different maze on revisit. Achieving revisit-consistency for this family would require
defining the growth/carve order as a **canonical function of region coordinates** (e.g. a fixed
enumeration — a spiral or row-major sweep outward from the origin — that generation always follows
regardless of which direction the player actually approaches from), not the player's actual path.
This is real, unsolved design work, not a hardware question — flagged here as a risk for
`03-architecture-design-synthesis` to weigh, not resolved by this topic.

**`BL-0066`'s two existing blob-clustering candidates do not survive a streaming model as written —
confirmed, not merely asserted, by re-reading them against the positional-determinism requirement
above.** Dead-end seeding needs a *completed* maze pass over a *known extent* to identify dead
ends from; N-random-point flood-fill needs a *bounded grid* to place `N` points across and flood-
fill between. Neither input exists in a streaming model before the region graph itself is
materialized. **The same coordinate-hashing technique above directly supplies a streaming-
compatible substitute**, mirroring exactly how real open-world games derive biome/structure
placement per chunk: partition the infinite grid into fixed-size **super-cells** (e.g. 4×4 or 8×8
regions each), and derive each super-cell's "blob identity" from `hash(SEED, supercell_row,
supercell_col)` alone — the same XOR/shift-mixed xorshift-reseed technique named above, with no
whole-grid pass and no dependency on maze/dead-end structure. Individual regions within a
super-cell then inherit or lightly perturb that identity (still locally, from `(seed, row, col)`).
This is the same "hash chunk coordinates into chunk-local content" pattern cited above,[^1] applied
to this project's own biome-family/blob concept rather than terrain height — **a genuinely
different clustering *mechanism* than either of `BL-0066`'s original candidates, not a third
variant of the same shape** — its aesthetic/gameplay quality (does a super-cell-hashed blob still
read as a coherent visual region, per `R209`/`R210`/`R211`'s established craft standard) is a
`02-research-game-design`/`03` judgment call this topic does not make.

**WRAM budget, measured directly against the shipped tree (updates R111/R112's own prior
figures, both now stale post-`IP-1070`/`IP-1021`).** The highest-addressed named WRAM allocation as
of this session is `GW_KI_PLACED` (`asm_game.py:136`, `0xC3F5`) — R112's own claim ("the
highest-addressed named allocation is `OAM_BUF`... this position is unchanged since before world
generation existed") is itself now stale, since `GW_MAZE_STATE`/`GW_MAZE_DRAW_CTR`/`GW_KI_PLACED`
(all higher-addressed than `OAM_BUF`) were added after that topic was written; not fixed here
(out of this topic's own write scope — `03`'s job, `BL-0099` already routes the general pattern).
Directly re-measured this session: **3082 bytes of bank-0 headroom remain** (`0xC3F6`–`0xCFFF`),
down from R112's 3168-byte figure by exactly the 86 net-new bytes `IP-1021` added (`GW_KI_PLACED` +
the encoding-domain widening needed no new bytes). **`SVBK` banked WRAM (R111) remains entirely
untouched** — 7 more 4 KiB banks (28 KiB) are available if a bounded "materialized window" approach
needs more than bank-0's ~3 KiB, a real and already-documented path (R111's own conclusion: "a
generated world's working set would need to grow by more than 3× the entire game's current total
WRAM footprint before `SVBK` banking becomes relevant" — a streaming window sized to, say, a 5×5 or
7×7 region neighborhood around the player, each region needing only a handful of bytes (biome-id,
maze-connectivity nibble, `KEYITEM_FLAGS`-equivalent state), stays comfortably inside bank-0 without
banking at all; banking only becomes relevant for a substantially larger materialized radius).

**ROM budget is not a binding constraint at this codebase's current size.** 22984/32768 bytes used
(directly re-measured this session, `build_rom.py`), 9784 bytes (~9.55 KiB) free. A per-region
hash-seeded generation routine (biome candidate + local maze-connectivity decision) is structurally
smaller than the existing whole-grid `generate_world` pass it would replace or extend (one
region's worth of logic, not a `scale²`-iteration loop) — comparable in scale to any single
existing subroutine this codebase already ships, not a meaningful fraction of remaining headroom.

**Compute/timing cost per materialization event is a new question this project has not had to
answer before, and is not resolved here.** Today's `generate_world` runs once, at new-game
creation, under the same LCD-off bracket `do_screen_redraw` already uses (R102, R111's own
recommendation, already followed) — a one-time cost, never a per-frame or per-transition budget.
Streaming generation would need to materialize a region's data **at the moment the player
approaches it** (plausibly inside `check_zone_transition`'s own existing call site, `asm_game.py`),
a genuinely new "safe window" question: is a single region's hash-seed-and-clamp computation cheap
enough to run inside whatever timing budget zone-transition handling already has, without a new
LCD-off bracket or a player-visible stall? A single-region computation (one xorshift reseed, one
clamp against ≤4 already-materialized neighbors) is a small constant amount of work — almost
certainly well under `generate_world`'s existing per-region cost (already proven affordable at up
to 81 regions in one LCD-off pass, R112) — but this needs direct cycle-counting against
`check_zone_transition`'s actual call context (R102's VBlank/mode-timing figures) before being
treated as settled, not merely assumed here.

## Operational Context

None of this topic's findings are exercised by the shipped ROM today — `generate_world` remains
the single, global, upfront pass IP-1020/IP-1070/IP-1021 have each extended without changing its
fundamental shape. This topic is purely forward-looking, grounding a not-yet-authorized
architecture change, the same relationship R112 had to `BL-0064` before `ADR-0012` was written.

## Implementation Guidance

- **The load-bearing finding, restated plainly for `03-architecture-design-synthesis`: streaming
  generation is representable, but requires replacing both the biome-assignment algorithm's
  sequential anchor-clamp and the maze-carve algorithm's global backtracking DFS with genuinely
  different, positionally-deterministic algorithms — this is a real algorithm-family change, not
  an incremental patch to `generate_world`'s existing shape.** Do not attempt to make the *current*
  algorithms lazy by simply "running `generate_world` further" on demand — their per-region output
  is defined in terms of generation history, which a streaming model does not have available.
- **For biome/blob positional determinism, seed a fresh `gw_prng_step`-family xorshift instance per
  region (or per super-cell, for `BL-0066`'s clustering case) from `SEED` XOR/shift-mixed with
  `(row, col)`** — reuse the exact shift/XOR-only construction `gw_prng_step` already implements
  (`asm_game.py`, `R111`/`R113`), never introduce a multiply-based hash (FNV-1a and similar
  standard techniques[^1] are not portable to this hardware without a costly software-multiply
  routine this codebase has never needed before). Discard the seeded instance after deriving the
  region's few needed values — no persistent per-region PRNG state is implied.
- **For maze connectivity, weigh the Binary Tree algorithm's "genuinely free, zero-memory" property
  against its own named conflict with `IP-1021`'s dead-end-priority win condition before adopting
  it** — a `03-architecture-design-synthesis` tradeoff, not resolved here. If adopted, `BL-0094`'s
  own already-deferred infinite-mode win-condition design (dead-end-only placement) would need to
  either accept the biased dead-end distribution or choose a maze family with more even dead-end
  coverage (Growing Tree, at the cost of the harder revisit-consistency design work above).
- **If Growing Tree (or any frontier-based family) is chosen instead, revisit-consistency must be
  designed in from the start as a canonical, coordinate-driven enumeration order** (e.g. a fixed
  spiral or row-major sweep outward from `(0,0)`, applied identically regardless of player
  approach direction) — do not derive carve order from player movement history, which cannot
  guarantee the same maze on revisit.
- **Bound any "materialized window" to bank-0's ~3 KiB headroom first; only reach for `SVBK`
  banking (R111) if a specific chosen window radius concretely exceeds it** — `gbc_lib.py` has no
  `SVBK` emitter today (R111's own note), so adopting banking is itself new toolchain work, not a
  free capability.
- **Save/load needs a genuinely different persisted shape, not an extension of the current one.**
  `ADR-0009` point 6's "regenerate `REGION_GRAPH` from `(seed, scale)` on load" has no meaning once
  there is no fixed `scale` — but if biome/maze become purely positional (per the findings above),
  **nothing about the graph itself needs to be saved at all**, only the player's current position
  (a signed or unbounded coordinate pair, not `CUR_ZONE`'s current 0–80 byte) and which regions'
  `KeyItem`/collectible state has been mutated by play (collected/absent) — a bounded-by-SRAM-
  capacity "visited-region ledger," not a flat whole-grid array, since an unbounded world cannot
  reserve SRAM for every region that could ever exist. Sizing that ledger's real capacity (how many
  distinct visited regions a save can remember) is new SRAM-budget work this topic flags but does
  not size — `R106`'s existing SRAM/battery-save grounding is the starting point for that follow-on.
- **Materialization timing needs direct cycle-counting against `check_zone_transition`'s actual call
  context before being treated as settled** — likely affordable (a single region's hash-reseed-
  and-clamp is a small constant cost, well under `generate_world`'s already-proven-affordable
  per-region cost), but not confirmed here; a future `02-research-tooling-and-testing` or direct
  implementation-time measurement should close this gap before `03` treats it as free.

### Sources
[^1]: [How can I create a persistent seed for each chunk of an infinite procedural world? — Game Development Stack Exchange](https://gamedev.stackexchange.com/questions/183142/how-can-i-create-a-persistent-seed-for-each-chunk-of-an-infinite-procedural-worl); [The World Generation of Minecraft — Alan Zucconi](https://www.alanzucconi.com/2022/06/05/minecraft-world-generation/); [Procedural Generation 101: Build Infinite Game Worlds](https://respawn.outlookindia.com/gaming/gaming-guides/essential-procedural-generation-techniques-for-game-developers); accessed 2026-07-13 via `WebSearch` summary. Corroborated across three independent sources describing the same coordinate-hashing pattern.
[^2]: [Xorshift — Wikipedia](https://en.wikipedia.org/wiki/Xorshift); [Looking for a good hash for 2 integers — GameDev.net Forums](https://gamedev.net/forums/topic/609003-looking-for-a-good-hash-for-2-integers/); accessed 2026-07-13 via `WebSearch` summary (consistent with R111's own identical-class citations, which also rested on `WebSearch` summaries after direct-fetch blocks).
[^3]: [Buckblog: Maze Generation — Binary Tree algorithm (Jamis Buck)](https://weblog.jamisbuck.org/2011/2/1/maze-generation-binary-tree-algorithm.html); [Binary Tree Maze — Procedural Generation Algorithms, Kansas State CS wiki](https://people.cs.ksu.edu/~ashley78/wiki.ashleycoleman.me/index.php/Binary_Tree_Maze.html); accessed 2026-07-13 via `WebSearch` summary — same source family (Jamis Buck, "Mazes for Programmers") R112 already cites for the braid-pass and recursive-backtracker characterizations, extending it here to the binary-tree variant.
[^4]: [Buckblog: Maze Generation — Growing Tree algorithm (Jamis Buck)](https://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm.html); accessed 2026-07-13 via `WebSearch` summary.

**Single-source flag:** none of this topic's load-bearing claims rest on a single source — the
coordinate-hashing technique ([^1]) is corroborated across three independent descriptions of the
same pattern; the Binary Tree algorithm's no-memory property and its directional-bias drawback
([^3]) are corroborated across two independent sources describing the same well-known technique
(the same source family R112 already relied on for the sibling maze-algorithm topic). The direct
WRAM/ROM measurements (3082 bytes bank-0 headroom, 9784 bytes ROM headroom, `GW_KI_PLACED` as the
current highest-addressed allocation) are Tier-A: re-derived directly from the shipped tree this
session (`asm_game.py`, a fresh `build_rom.py` run), not externally sourced, matching R111/R112's
own established precedent for treating this project's own verified code as primary evidence.
**Environmental note:** all `WebSearch` results this session were consumed as summaries; no direct
`WebFetch` of the underlying URLs was attempted (consistent with R111/R112/R113's own documented
experience of frequent HTTP 403s from `en.wikipedia.org`, `gbdev.io`, and similar hosts in this
environment) — flagged per this skill's own single-source-and-fetch-availability discipline, not a
gap specific to this topic.

## Feature Mapping

*(No `FS-xxx`/`FEAT-xxxx` authored yet — this grounds `BL-0082`'s own pending `02-research-game-
design` follow-on and, if the project owner and `03-architecture-design-synthesis` choose to adopt
streaming generation, a future ADR amending `ADR-0009`/`ADR-0012`/`ADR-0013`.)*

## Related Topics

R101 (no hardware `MUL`/`DIV` — the constraint every candidate hashing/mixing scheme above must
respect) · R111 (the existing xorshift PRNG this topic's per-region reseeding technique directly
reuses, and the `SVBK` banked-WRAM path a bounded materialized window could fall back to) · R112
(the shipped maze algorithm's own hardware-cost framing, extended here from "once, globally" to
"lazily, locally") · R113 (the shipped PRNG's own degeneracy history — any new per-region seeding
scheme must not reintroduce a similar defect) · R213 (the graph-on-a-grid generation family this
topic's local variant still operates within) · R215 (the win-condition research whose own
`IP-1021`-shipped candidate this topic finds is not streaming-compatible as written, directly
bearing on `BL-0094`'s already-deferred infinite-mode design).
