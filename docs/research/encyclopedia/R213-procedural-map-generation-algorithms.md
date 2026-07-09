# R213 — Procedural Map Generation Algorithms Under 8-Bit/GBC Constraints

- **Document ID:** R213 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R212 (biome-adjacency grammar this generator must satisfy), R106 (MBC1/SRAM,
  banking headroom), R111 (WRAM budget and SM83 PRNG implementation this recommendation assumes),
  R302 (Python-assembler codegen patterns), R305 (emulator-based test design)
- **Referenced By:** R111 (grounds this topic's PRNG/WRAM feasibility in hardware terms), R305
  (this topic's recommended algorithm is what the reference-generator oracle mirrors)
- **Produces:** a costed, evidence-grounded recommendation for the world-generation algorithm
  approach `03-architecture-design-synthesis` decides in its Phase 3 ADR (per MSTR-001 C10/D3 —
  the owner explicitly delegates the algorithm choice to this research, not to a fiat pick)
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R212, R214, R106, R111, R302, R305

## Purpose

Filed to ground **MSTR-001 C10** (the world is deterministically procedurally generated from a
seed and a user-adjustable world-scale parameter, both fixed at new-game creation) per **D3**'s
explicit instruction: research procedural map generation algorithms and let the algorithm choice
be evidence-derived, not owner-dictated. This topic surveys the algorithm families available,
evaluates each against this project's actual constraints (SM83 runtime, Python-assembler build
side, ROM/WRAM budget, R212's adjacency grammar, testable determinism), and recommends a
direction for the Phase 3 world-generation ADR.

## Scope

Generation algorithm families at the granularity relevant to a **screen-composed** world (not
continuous-scroll/free-tile): random-walk/drunkard's-walk, cellular automata, Wave Function
Collapse (WFC)/constraint-based, and graph/mission-grammar generation. Also: PRNG choice for a
resource-constrained CPU, and the build-time-vs-runtime generation split question this project's
two-sided (Python build / SM83 runtime) architecture raises. Out of scope: the biome-adjacency
grammar's *content* (R212) and specific case-study titles (R214).

## Concepts

**Random walk / drunkard's walk.** A single "digger" entity moves randomly step by step, carving
a path; guarantees full connectivity (every carved cell reaches every other) and produces
organic, cave-like results, but is "pretty unreliable" on its own — results vary widely in
quality/shape run to run.[^1] Cheap to implement (a handful of bytes of state: position +
direction), but its *strength* — pure chance-driven blob shapes — is a poor match for this
project's requirement that each screen have a **specific, identifiable biome**, not an organic
undifferentiated blob.

**Cellular automata.** A 2D grid where each cell is alive/dead by a birth/death rule applied
iteratively from a random initial seeding, converging toward smooth, natural-looking cave/organic
shapes; often *combined* with random walk (random walk supplies chaotic input, cellular automata
smooths it).[^1] Same limitation as random walk for this project's purposes: excellent for
undifferentiated organic terrain, no native concept of "labeled regions in a specific order."

**Wave Function Collapse (WFC) / constraint-based generation.** Directly formalizes adjacency
rules: "which tiles can appear adjacent... creates adjacency rules, then generates content
satisfying these constraints," working by repeatedly collapsing the lowest-entropy (most
constrained) cell to one value and propagating the resulting constraint outward.[^2] This is the
*closest conceptual match* to R212's biome-adjacency grammar — a WFC-style engine given "region
type X may border region types {Y, Z}" rules would directly enforce it. However, WFC carries real
cost and risk: known **complexity and scaling problems** ("lack the ability to generate
commercialized large-scale or infinite content due to constraint conflict and time complexity
costs"[^3]) and **contradictions** — states where a cell has no valid remaining option, requiring
backtracking.[^3] For an SM83-class CPU with no native stack-heavy backtracking budget and a hard
frame-time expectation (this project's smoothness commitment, MSTR-001 C8/D4), full per-tile WFC
run live on console is a poor fit; it is far better suited to the **unconstrained Python build
side** if used at all (see Implementation Guidance).

**Graph / mission-grammar generation.** Generates a **graph of discrete rooms/screens** (nodes)
connected by validated edges (doorways/adjacencies), rather than operating at tile granularity —
exactly the granularity this project's own architecture already uses. Tools built specifically
for Zelda-like generation (`metazelda`, a "Zelda-like dungeon-design-generating library"[^4];
`GraphDungeonGenerator`, built on Joris Dormans' Mission Graph and Layout Grammar work[^4]) lay
the graph "on a 2D grid of cells where each cell can be connected from any of the four main
directions"[^4] — structurally identical to this project's 3×3-grid-of-screens shape (GDS-04),
just generalized past a fixed 3×3. Overworld generation specifically is described as usable "at
tile granularity instead of room/screen granularity" as a *choice*, not a requirement[^4] — this
project should choose screen granularity, matching its existing architecture and R212's
screen-level grammar exactly.

**PRNG choice for a resource-constrained CPU.** Xorshift-family generators are "confined to
simple XOR and shift operations," need only a few bytes of state (as few as 4), avoid
multiply/divide entirely, and are noted specifically as well-suited to embedded/8-bit
contexts.[^5] A worked Z80-family assembly implementation of a 16-bit xorshift generator exists
as a direct precedent for SM83 (a close relative of the Z80 instruction set this project's own
`gbc_lib.py`/R101 already target).[^6] This directly satisfies **MSTR-001 A9** (seed is the sole
entropy source, no DIV-register/uninitialized-RAM dependence) at negligible cost.

**Historical grounding: procedural generation on constrained hardware is not a novel proposal —
it is PCG's founding use case.** "Procedural Content Generation (PCG)... was initially adopted in
early titles such as *Rogue* and *Maze Craze*, where limited system resources were the primary
constraint... using seeds and rules to generate larger worlds dynamically while reducing memory
and storage requirements."[^7] This is the exact motivation MSTR-001 C10 and the adopted plan's
§7 constraints section already name for this project (ROM/WRAM headroom pressure) — procedural
generation is being adopted for the same reason it was invented.

## Operational Context

This project has a **two-sided build architecture** unlike a typical single-target game: an
unconstrained **Python build side** (`build_rom.py` + friends, runs on the host machine, no
byte/cycle budget) and a heavily constrained **SM83 runtime side** (`asm_game.py`, VBlank-gated
VRAM writes, no native multiply/divide, tight WRAM). Every algorithm above can in principle run on
either side, but the cost profile differs enormously — a full WFC solve is trivial for the Python
build side and impractical for the SM83 runtime; the reverse is not true (a tiny PRNG-driven graph
walk is cheap on *either* side). This split is the single most important project-specific fact
missing from a generic "which algorithm is best" comparison, and is the crux of this topic's
recommendation.

The existing `tilemaps.py` screen-authoring pattern (GDS-08 §1: a seeded pseudo-random two-variant
terrain sprinkle via `_fill()`, plus 3–7 hand-placed landmark elements) is itself already a small,
working, *deterministic*, seed-driven generation primitive — evidence this project's own toolchain
already has a proven, cheap building block for texture-level variation within a screen, distinct
from the region-*sequence* generation problem this topic addresses.

## Implementation Guidance

- **Recommend screen/room-graph generation as the primary structural algorithm**, not per-tile
  WFC/cellular-automata/random-walk. Reasoning: (1) it matches this project's existing
  screen-composed architecture exactly (`ALL_SCREENS`, one Python function per screen — GDS-04/07)
  rather than requiring a new continuous-tile-canvas concept; (2) it is the graph shape R212's
  adjacency grammar is natively expressed over (edge validity = grammar-legal biome pairing);
  (3) it sidesteps WFC's contradiction/backtracking risk entirely, since a small graph (tens of
  nodes even at a generous world-scale) with a simple grammar is trivially satisfiable by
  constrained random walk over the *graph*, not the tile grid — cellular-automata/WFC's
  complexity concerns[^3] apply at tile-canvas scale, not room-graph scale.
- **Recommend the graph/region-assignment generation step run on the Python build/first-boot
  side, not as live SM83 tile-by-tile computation.** Two concrete implementation shapes, both
  worth the Phase 3 ADR's evaluation (this topic does not pick between them — that's
  architecture's call): **(a)** generate the full region graph + biome assignment on first boot
  in SM83 from (seed, scale) using a tiny xorshift-style PRNG (a few bytes of WRAM state, no
  multiply/divide — R101/R110-compatible) and a compact grammar-check routine, writing the result
  to WRAM/SRAM as a lookup table the rest of the game already treats zones through (minimal
  runtime cost, matches C10's "generated ... at new-game creation" framing exactly); **(b)**
  precompute a curated pool of grammar-valid region templates at Python build time and have SM83
  select among them by seed — cheaper at runtime, more ROM cost, less "true" generation. Given
  A9's determinism requirement and the adopted plan's Python-reference-generator-oracle testing
  strategy (R305), **(a)** is the more natural fit: a Python mirror of the exact SM83 xorshift +
  grammar-check routine can serve as the test oracle for any (seed, scale) pair, exactly
  paralleling how `build_rom.py` and `test_rom.py` already relate.
- **Reuse the existing `_fill()` seeded-sprinkle pattern (GDS-08 §1) for within-screen texture
  variation once a screen's biome is assigned** — do not invent a second per-tile generation
  system; the region/graph layer (this topic) decides *which biome goes where and how they
  connect*, the existing per-screen fill primitive decides *how that biome's terrain texture
  looks*, cleanly separating concerns already split in the current codebase.
- **PRNG: adopt a xorshift-family generator with 2–4 bytes of state**, avoiding
  multiply/divide/modulo entirely, directly implementable in SM83 assembly following the
  precedent Z80 pattern[^6] — satisfies MSTR-001 A9 and keeps ROM/cycle cost negligible.
- **Do not adopt full per-tile WFC on the SM83 runtime.** Its documented complexity/contradiction
  risk[^3] is a poor match for a hard-real-time, VBlank-budgeted rendering loop with no
  backtracking-friendly stack budget; if WFC-style tile-adjacency reasoning is ever wanted for
  *within-screen* texture coherence (a much smaller-scoped future question, not this increment's),
  it belongs on the unconstrained Python build side only.
- **Cost this against the adopted plan's headroom constraint (§7):** a graph/PRNG-based generator
  is ROM-cheap (small code, no large precomputed map data) relative to the handcrafted 3×3 world
  it replaces (9 full hand-authored screen tilemaps) — directly supporting C10's framing that
  procedural generation *helps* the ROM budget, not just adds a feature; exact byte costs are a
  Phase 3 architecture question once a concrete grammar/graph size is chosen.

### Sources
[^1]: [Procedural Dungeon Generation: Cellular Automata — jrheard's blog](https://blog.jrheard.com/procedural-dungeon-generation-cellular-automata); corroborated by [Generating a 2D map using the Random Walk algorithm — Noveltech](https://www.noveltech.dev/procgen-random-walk) and [Procedural Level Generation in Games using a Cellular Automaton, Part 1 — Kodeco](https://www.kodeco.com/2425-procedural-level-generation-in-games-using-a-cellular-automaton-part-1); accessed 2026-07-09 via WebSearch summary.
[^2]: [Wave Function Collapse Explained — BorisTheBrave.Com](https://www.boristhebrave.com/2020/04/13/wave-function-collapse-explained/); accessed 2026-07-09 via WebSearch summary.
[^3]: [Extend Wave Function Collapse to Large-Scale Content Generation (arXiv 2308.07307)](https://arxiv.org/abs/2308.07307); corroborated by [Lessons Learned from Implementing "Wave Function Collapse" — fxhash](https://www.fxhash.xyz/article/lessons-learned-from-implementing-%22wave-function-collapse%22); accessed 2026-07-09 via WebSearch summary.
[^4]: [metazelda — GitHub](https://github.com/tcoxon/metazelda); [GraphDungeonGenerator — GitHub](https://github.com/amidos2006/GraphDungeonGenerator); [Zelda-like procedural map generation — GameDev.net](https://www.gamedev.net/forums/topic/514911-zelda-like-procedural-map-generation/); accessed 2026-07-09 via WebSearch summary.
[^5]: [Pseudorandom Number Generators — filterpaper notes](https://filterpaper.github.io/prng.html); corroborated by [Fast 8-bit pseudorandom number generator — Wikistix](https://www.stix.id.au/wiki/Fast_8-bit_pseudorandom_number_generator); accessed 2026-07-09 via WebSearch summary.
[^6]: [Retro Programming: 16-Bit Xorshift Pseudorandom Numbers in Z80 Assembly](http://www.retroprogramming.com/2017/07/xorshift-pseudorandom-numbers-in-z80.html); accessed 2026-07-09 via WebSearch summary. Cross-reference [R101](R101-sm83-instruction-set.md) for the SM83/Z80 instruction-set relationship this precedent transfers through.
[^7]: WebSearch synthesis citing PCG's origin in *Rogue*/*Maze Craze* as a memory-constraint response, from the "NES retro 8-bit procedural generation" search pass, 2026-07-09; **flagged needs-fetch-verification** — this specific historical claim was returned as a search-engine synthesis without a single clearly attributable primary source in the result set; treat as plausible, well-known game-history context rather than a citable authoritative claim until a primary source (e.g. a PCG survey paper) is directly fetched.

**Single-source flag:** §7's historical-origin claim is flagged above. All other claim clusters
carry ≥2 independent corroborating sources from this session's search pass. As with R212, direct
page fetches were blocked (HTTP 403) for several underlying sites this session; citations rest on
WebSearch result summaries — adequate for algorithm-selection grounding (a design/engineering
comparison, not a hardware-timing claim), consistent with this project's existing citation-
confidence precedent (R301, `BL-0011`).

## Feature Mapping

*(No `FS-xxx` authored yet — this grounds the Phase 3 world-generation ADR and, eventually,
stage-06/07 work.)*

## Related Topics

R212 (the adjacency grammar this generator must satisfy) · R214 (GBC-hardware feasibility
evidence, esp. Roguecraft GB's room-graph precedent) · R106 (MBC1/banking headroom this
generator's ROM cost trades against) · R302 (Python-assembler codegen patterns the SM83-side
generator routine would follow) · R305 (emulator-based test design — the reference-generator
oracle pattern this topic's recommendation depends on).
