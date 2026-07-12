# FS-107 — Maze-Shaped Region Adjacency

> Feature Specification for [FEAT-9100](../feature-planning/03-feature-catalog.md#feat-9100--maze-shaped-region-adjacency-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-9100, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md) · [ADR-0012](../architecture/adr/ADR-0012-maze-shaped-region-adjacency.md)

> **Forward reference (metadata only):** implemented by
> [IP-1070](../implementation/packages/IP-1070-maze-shaped-region-adjacency.md) (2026-07-11,
> `COMPLETE`), which resolves this document's Open Questions 1–3 (see §19).

## 1. Feature ID

`FS-107` — expands `FEAT-9100` (Maze-Shaped Region Adjacency), Epic `EP-5000` (World Generation &
Visual Narrative).

## 2. Title

Maze-Shaped Region Adjacency

## 3. Purpose

Replace `FEAT-9000`'s full-lattice region adjacency (every grid-adjacent region pair always
connected) with a generated maze — a spanning tree guaranteeing reachability, plus a braid pass
reopening a configurable fraction of pruned edges — so the traversable world reads as distinct
regions connected by paths, not a uniformly open grid. Carried forward verbatim from FEAT-9100's
own Purpose/User Value (High — directly answers the project owner's stated goal, the reason
`BL-0064` was filed).

## 4. Scope

**In scope:** the maze-generation algorithm itself — a randomized DFS/recursive-backtracker
spanning tree over the full candidate edge set (every grid-adjacent region pair), followed by a
braid pass reopening a fraction of the pruned edges — as a second, independent pass over the same
`scale`×`scale` region grid `FEAT-9000`'s biome assignment already produces; the braid-fraction
parameter's mechanism and fixed initial default; the resulting `REGION_GRAPH` neighbor-byte
output this pass populates.

**Out of scope** (per FEAT-9100's own Excluded Requirements, carried forward verbatim): biome
assignment itself (`FEAT-9000`'s own unchanged pass — this Feature reads its output, does not
modify it); navigation (`check_zone_transition`, `FEAT-2000`/`IP-9050`) and rendering
(`dsr_p`/`draw_region_arrows`, `FEAT-4100`/`IP-1030`) consumption of the resulting graph — both
already consume `REGION_GRAPH`'s neighbor bytes generically and need zero changes (`ADR-0012`
point 2); the braid-fraction value's player-facing UI exposure (an open design question,
explicitly not this Feature's scope per `FR-9150`'s own Notes); the maze-blocked-vs-boundary
visual distinction (`FEAT-2100`/`FS-108`, this Feature's own dependent).

## 5. Requirements Implemented

FR-9140, FR-9150 — the exact set FEAT-9100 owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-9100--maze-shaped-region-adjacency-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — New-game world generation, maze-adjacency pass** (extends
[FS-102](FS-102-procedural-world-generation.md) Workflow A at the exact point that workflow's
step 4 populates adjacency edges — `ADR-0012` point 1 supersedes only that clause, not the rest of
FS-102):

1. FS-102 Workflow A steps 1–3 run unchanged (player confirms `(seed, scale)`; the routine
   receives it and initializes the xorshift PRNG).
2. Biome assignment (FS-102 Workflow A step 4's biome-*identity* half only) completes for every
   region, entirely unchanged in mechanism — each region's biome is still drawn from its grid-fixed
   top/left neighbor's constraint window, independent of maze connectivity (`ADR-0012` point 1).
   FS-102 step 4's own "proposes adjacency edges" clause is what this Feature's pass replaces —
   the full-lattice edge set that clause built is no longer written to `REGION_GRAPH` directly.
3. This Feature's maze pass begins, over the same grid's full candidate edge set (every
   grid-adjacent region pair — a pure function of `WORLD_SCALE`, `FR-9140`'s own Inputs field):
   starting from the world's starting region, the routine builds a spanning tree via randomized
   DFS/recursive backtracker, moving to a random unvisited grid-adjacent neighbor (a single mod-4
   `AND 3` direction draw, trying up to 4 directions in a fixed rotation from that draw until an
   unvisited neighbor is carved or none remains), and backtracking by re-reading the just-carved
   edge's own reverse direction out of `REGION_GRAPH`'s own neighbor bytes — no separate stack
   array (`ADR-0012` point 3, R112's cited "store backtracking information in the maze itself"
   technique).
4. The braid pass runs once, over every grid edge *not* selected by the spanning tree (≤144 at
   `scale=9`): for each such edge, one PRNG byte is drawn and compared against `FR-9150`'s
   braid-fraction threshold; the edge is reopened (written into `REGION_GRAPH`) if the drawn byte
   is at or below the threshold (`ADR-0012` point 4).
5. `REGION_GRAPH`'s neighbor bytes now hold the maze's own edge set — a subgraph of the full grid
   graph, not the full grid graph itself. Every region remains reachable from the starting region
   by construction (`FR-9120`, a structural guarantee of step 3's spanning tree, not a separate
   check).
6. Control returns to FS-102 Workflow A step 7 unchanged (transition to `INTRO`).

**Workflow B — collection during play:** unaffected. FS-102 Workflow B (`KeyItem` collection) does
not read adjacency edges at all — this Feature has no interaction with it.

## 7. System Behaviour

**Normal path:** for any valid `(seed, scale, braid-fraction)`, the routine terminates having
populated `REGION_GRAPH`'s neighbor bytes with a maze — a spanning tree plus the braid pass's
reopened edges — that is a subgraph of the full grid graph, with every region reachable from the
starting region.

**Edge case — a region with zero grid-adjacent neighbors ever selected by the tree (corner/edge
regions at small `scale`):** at `scale=2` (the minimum, 4 regions), every region has exactly 2
grid-adjacent neighbors; the spanning tree still connects all 4 by construction — this is the
floor case any test corpus must cover (mirroring FS-102 §7's own `scale=2` edge case).

**Edge case — the starting region's own first step:** the backtracker's very first move has no
"reverse direction" to read yet (no edge has been carved into it) — the routine's own
current-region pointer starts *at* the starting region with no prior edge, per `ADR-0012` point 3's
"explicit loop with a 'current region' pointer" framing; this is a genuine implementation-detail
edge case, not resolved further here (see §19 Open Questions).

**Edge case — braid-fraction threshold at its extremes:** a threshold of 0 reopens no pruned
edges (a pure spanning tree, maximally maze-like); a threshold at its maximum reopens every
pruned edge (recovering the old full-lattice behavior exactly) — both are valid inputs to the
mechanism `FR-9150` establishes, though only the fixed initial default (~25%, per `FR-9150`'s
Notes) is exercised by this Feature's own scope (UI-driven threshold selection is out of scope,
§4).

**Edge case — re-generating with the same `(seed, scale, braid-fraction)`:** must produce
byte-identical adjacency output, per `FR-9140`'s Acceptance Criteria (c) — exercised the same way
as FS-102's own determinism check (§16), extended to this pass.

## 8. Module Responsibilities

Per GDS-03's module decomposition and GDS-09's delta (both already established by FS-102 §8,
extended here, not redefined):

- **`asm_game.py`** — `generate_world` gains a new maze-generation pass (spanning tree + braid),
  inserted between FS-102's existing biome-assignment logic and the routine's return to its
  caller. The existing biome-assignment code itself is untouched.
- **`worldgen.py`** (build-side Python oracle, already exists per FS-102 §8) — gains the
  equivalent maze-generation pass, kept in lockstep with the SM83 routine by direct correspondence
  (same PRNG step order, same edge-visitation order), per `ADR-0012` point 7 and the same
  discipline FS-102 §14 already names for the existing generation pass.

No other module is touched — `tilemaps.py`'s biome-family screen functions, `gbc_lib.py`,
`build_tile_data()`'s buffer contract, and `music.py` are all unaffected, exactly as `ADR-0012`'s
Consequences section states.

## 9. Interfaces Used

- **`worldgen.py`'s existing confirmed contract** (`generate(seed: int, scale: int) -> list[dict]`,
  GDS-09's Interface delta, shipped `IP-1020`) — extended in place, not replaced: each returned
  region `dict`'s `'neighbors'` field now reflects the maze's subgraph rather than the full grid,
  same shape (`[up, down, left, right]`, `None` where `0xFF` appears on-console).
- **No new `patches` dict key** — this Feature's entire output is WRAM working-set data
  (`REGION_GRAPH`'s existing neighbor bytes), not ROM-resident content; mirrors FS-102's own
  Open Question 3 resolution (no generator-data ROM pointer was needed for biome assignment
  either, per GDS-09's confirmed delta).
- **`ALL_SCREENS`/`dsr_p`/`draw_region_arrows`/`check_zone_transition`** — consumed by this
  Feature's *dependents*, not by this Feature itself; named here only to confirm (per `ADR-0012`
  point 2, directly verified by reading both shipped call sites) that none of their existing
  contracts need to change to consume this Feature's sparser output.

## 10. Data Model Changes

Per GDS-07's existing confirmed layout (§2/§6) and `ADR-0012` point 2:

- **`REGION_GRAPH`'s own format is unchanged** — still 5 bytes/region (1 biome-id byte + 4
  neighbor-region-index bytes, `0xFF` = no neighbor), `0xC070`–`0xC204` worst case at `scale=9`.
  This Feature changes *which* edges get written as valid neighbors, not the structure holding
  them.
- **New transient generation-time scratch (proposed, address TBD at implementation):** the
  spanning-tree pass needs a per-region "visited" flag during construction (R112's grounding: 81
  bytes flat, or 11 bytes if bit-packed — a genuine open sizing/packing choice, not decided by
  `ADR-0012`; see §19 Open Questions) plus a one-byte "current region" pointer and a one-byte
  braid-pass loop counter, both comparable in role to `generate_world`'s existing
  `GW_REGION_IDX`/`GW_B_SCRATCH` transient scratch (GDS-07 §6) — transient, meaningless outside a
  `generate_world` call, not part of the persisted data model, following that precedent exactly
  rather than inventing a new scratch convention.
- **No SRAM change** — this Feature's output is entirely encoded in `REGION_GRAPH`'s existing
  neighbor bytes, which are (per `ADR-0009` point 3, unaffected by this Feature) never persisted
  to SRAM; save/load continues to regenerate `REGION_GRAPH` from `SEED`/`WORLD_SCALE` alone
  (`FEAT-5300`'s scope, unaffected).
- **No new domain entity** beyond GDS-04's existing delta note for this Feature (`Region`'s
  "generated adjacency edges" becoming selective — already recorded there, 2026-07-11, this
  Feature is what implements it).

## 11. State Changes

None beyond FS-102's existing framing: this Feature's pass runs as an additional step inside the
same synchronous generation routine FS-102 §11 already describes (once, between the new-game
confirmation and the `INTRO` transition). No new `GameState` value; no new persistent runtime
state beyond the transient scratch named in §10, which does not outlive the `generate_world` call.

## 12. Error Handling

- **A region left completely unvisited by the spanning tree:** cannot occur — the algorithm's own
  termination condition (backtrack until no unvisited neighbor exists anywhere reachable, per
  `ADR-0012` point 3) is what guarantees full reachability; this is a generator-*guaranteed*
  property (`FR-9120`), not a condition checked and recovered from after construction, mirroring
  FS-102 §12's identical framing for the biome/grammar guarantees.
- **Invalid braid-fraction threshold values:** out of this Feature's scope at this stage — a fixed
  code-level constant (`FR-9150`'s Notes) is the only value exercised until a future stage
  exposes it as player input; that future stage owns validating whatever input mechanism it adds.

## 13. Performance Considerations

- **Stays within `generate_world`'s existing one-time, LCD-off-bracketed cost class** — per
  `ADR-0012`'s Context (citing R112's Operational Context): the spanning-tree pass is bounded by
  region count (≤81), the braid pass by edge count (≤144), both small constants comparable to or
  smaller than the region count `generate_world` already iterates today. No new "safe window"
  convention or frame-budget renegotiation, consistent with `NFR-1300`'s existing framing
  (generation is a one-time cost, not a per-transition smoothness concern).
- **NFR-4200** (generated-world WRAM headroom): this Feature's new transient scratch (§10) — up to
  81 bytes worst case, or 11 bytes if bit-packed — is directly grounded against the confirmed
  3168-byte/3.09-KiB bank-0 headroom `R112`/`NFR-4200`'s 2026-07-11 delta already measured; WRAM
  budget does not gate this Feature regardless of which packing choice `07-implementation-planning`
  makes (§19).
- **ROM budget:** not separately estimated here — the new pass is comparable in code size to the
  existing biome-assignment pass it sits alongside; an implementation-time measurement per
  `BL-0019`'s standing convention, not asserted by this specification.

## 14. Integrity Considerations

- **Determinism (`NFR-2200`, unaffected in kind, extended in scope):** this Feature's entire
  output must remain a pure function of `(SEED, WORLD_SCALE)` — no new PRNG source, no read of
  `DIV` or uninitialized WRAM anywhere in the new pass, per `ADR-0012` point 6. This is what keeps
  the `worldgen.py` oracle valid for this pass exactly as it already is for biome assignment
  (FS-102 §14's identical framing).
- **Oracle/SM83 lockstep (`ADR-0012` point 7, extending `ADR-0009`'s Consequences and FS-102
  §14's identical discipline):** the Python oracle's maze pass and the SM83 routine's maze pass
  must produce byte-identical `REGION_GRAPH` output for the same `(seed, scale, braid-fraction)` —
  a standing implementation discipline this spec names but does not itself enforce mechanically;
  `07-implementation-planning`/`08-code-implementation` maintain the correspondence,
  `09-package-verification` confirms it holds.

## 15. Acceptance Criteria

1. For any `(seed, scale, braid-fraction)` in a test corpus, every edge in the generated adjacency
   graph also exists in the full grid graph — no adjacency is invented that isn't grid-adjacent
   (FR-9140 AC-a).
2. For any `(seed, scale, braid-fraction)` in a test corpus, every region is reachable from the
   starting region (FR-9140 AC-b, `FR-9120`).
3. Regenerating from identical `(seed, scale, braid-fraction)` — in two separate new-game
   creations, or via the `worldgen.py` oracle vs. the SM83 routine — produces byte-identical
   adjacency output both times (FR-9140 AC-c).
4. For every edge that does exist in the generated graph, the two regions' biome families remain
   grammar-legal per `FR-4310` — confirming this Feature's pass does not disturb that already-held
   guarantee (`ADR-0012` point 1).
5. For a large `(seed, scale)` corpus at the fixed default threshold, the observed fraction of
   reopened (non-tree) edges falls within a statistically reasonable band of the threshold's
   implied probability (FR-9150's own Acceptance Criteria — a probabilistic, not exact-equality,
   check).
6. Static inspection of the new pass finds no read of `DIV` or any WRAM address not explicitly
   initialized from `(seed, scale)`, the braid-fraction constant, or the pass's own prior output
   (NFR-2200, extended).
7. At world scale 9, the built ROM's total WRAM working set (existing `REGION_GRAPH`/
   `KEYITEM_FLAGS` plus this Feature's new transient scratch) fits within bank-0 without requiring
   `SVBK` banking (NFR-4200).

## 16. Verification Plan

Per `FR-9140`/`FR-9150`'s own Verification Methods (Test — property test across a corpus, plus a
new statistical check), landing in a new **T19: Maze-Shaped Region Adjacency** suite in
`test_rom.py` (the next unused suite number, after T18):

- **Subgraph-of-full-lattice (AC-1):** for every edge in the generated graph, confirm it appears
  in the full grid-adjacency set computed independently from `(row, col, scale)` arithmetic — a
  new check, since the prior full-lattice model made this property trivially true and untested.
- **Reachability (AC-2):** direct extension of T12's existing graph-traversal check, re-run
  against this Feature's sparser graph — the check itself is unchanged, only the graph it walks is
  new (per `ADR-0012` point 5: the guarantee's mechanism changes, not its truth).
- **Determinism (AC-3):** direct extension of T12's existing two-boot / oracle-vs-SM83 comparison
  pattern, extended to include the maze pass's own output.
- **Grammar-validity non-regression (AC-4):** direct extension of T12's existing grammar-table
  check, confirming it still holds for whichever edges the maze pass actually keeps.
- **Braid-fraction statistical check (AC-5):** a new corpus-level check — count reopened
  (non-tree) edges across a large `(seed, scale)` sample at the fixed default threshold, assert
  the observed fraction falls within a defined statistical tolerance band (the exact band width is
  an implementation-time test-design choice, not fixed by this spec).
- **Determinism static audit (AC-6):** Inspection, direct code read of the new pass, extending
  T12's existing NFR-2200 audit pattern.
- **Headroom (AC-7):** Inspection, a direct WRAM-layout audit against the built ROM at `scale=9`,
  extending NFR-4200's existing audit convention.

**Multi-seed/multi-scale/multi-braid-fraction corpus:** extends FS-102 §16's existing corpus
(minimum `scale=2`, `scale=9`, `scale=3`, `seed=0`) with at least one braid-fraction value at each
extreme (0 and maximum, per §7's edge case) plus the fixed default, per `R305`'s adequate-not-
unbounded corpus convention.

## 17. Dependencies

Per FEAT-9100's own Dependencies (carried forward verbatim): `FEAT-9000`/`FS-102` (this Feature's
maze pass runs after and reads the region grid FS-102's biome-assignment pass produces; also
depends on FS-102's own determinism/reachability guarantees holding as preconditions). No other
`FS-xxx` is a prerequisite.

## 18. Risks

Carried forward from FEAT-9100's own Risk assessment (Low-Medium): the highest-risk design
question (which algorithm fits this hardware) is already resolved and evidenced (`R112`/
`ADR-0012`); remaining risk is ordinary implementation risk — getting the iterative backtracker's
edge cases right (the starting region's own no-reverse-edge first step, §7), not an open
architectural unknown. A secondary, smaller risk this spec surfaces: the oracle/SM83 lockstep
discipline (§14) is the same load-bearing verification dependency FS-102 §18 already names for
the existing generation pass, now extended to a second algorithm family within the same routine —
if the two implementations drift, the property-test corpus could pass while the shipped maze
generator is actually wrong, exactly as FS-102 §18 already warns for biome assignment.

## 19. Open Questions

1. **RESOLVED (`IP-1070`, 2026-07-11).** Visited-flag storage: flat (81 bytes) or bit-packed (11
   bytes)? Resolved flat — `GW_MAZE_STATE` (81 bytes, `0xC3A0`–`0xC3F0`, [GDS-07 §7b](../architecture/07-data-model.md)),
   combined with the 2-bit parent-direction field in the same byte (bit 7 = visited, bits 1:0 =
   parent-direction), which the bit-packed alternative could not have absorbed as cheaply. WRAM
   headroom remained comfortable at this size (T19.g).
2. **RESOLVED (`IP-1070`, 2026-07-11).** The exact transient-scratch WRAM addresses: `GW_MAZE_STATE`
   (`0xC3A0`), `GW_CUR_REGION` (`0xC3F1`), `GW_MAZE_DIR` (`0xC3F2`, doubles as the braid pass's
   direction after carving completes), `GW_BRAID_IDX` (`0xC3F3`, doubles as the braid pass's region
   counter), plus one address `ADR-0012` did not anticipate — `GW_MAZE_DRAW_CTR` (`0xC3F4`,
   `ADR-0013`'s PRNG-decorrelation counter, added mid-implementation after a Blocking Report). See
   [GDS-07 §7b](../architecture/07-data-model.md).
3. **RESOLVED (`IP-1070`, 2026-07-11).** The starting region's own first backtracking step: region
   0 is marked visited at `maze_init` with no parent-direction write; its `GW_MAZE_STATE` byte's
   bits 1:0 are simply never read until the carve loop backtracks into it (which requires it to
   still be "current" with all 4 directions exhausted) — at that point the carve loop's own
   termination check (`cur == 0` with nothing left to carve) fires before any parent-direction read
   would occur, so no explicit sentinel value was needed in practice.

**New finding during implementation (not a pre-existing Open Question):** `08-code-implementation`
found the shipped `gw_prng_step` degenerates under this pass's repeated back-to-back draws — see
[R113](../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md) and
[ADR-0013](../architecture/adr/ADR-0013-maze-pass-prng-decorrelation.md) for the root cause and
fix (a loop-local counter-XOR perturbation, applied only within this pass's own draws).

## 20. Related ADRs

ADR-0009 (screen/room-graph generation — the family this Feature's spanning tree stays within,
refined not reversed), ADR-0012 (the specific decision this Feature implements — algorithm choice,
braid mechanism, pass ordering, data-format non-change).
