# ADR-0016 — Streaming, positionally-deterministic generation architecture for a new, additive Infinite Mode

**Status:** Accepted (2026-07-13)

## Context

[BL-0082](../../pipeline/backlog.md) (project owner): whether the procgen architecture could build
the world lazily, region by region, as the player moves, deriving biome/adjacency/maze state from
`(seed, region coordinates)` instead of today's single upfront pass — with the goal of a
theoretically infinite playable world.

[R114](../../research/encyclopedia/R114-streaming-world-generation-feasibility.md) answers the
hardware-feasibility half directly: `generate_world`'s two load-bearing algorithms
(raster-scan biome anchor-clamp; backtracking-DFS maze carve, `ADR-0012`) both depend on global
generation history, not on a region's own coordinates alone — genuinely different problems from
"is this too expensive for an 8-bit CPU," which R112/R114 both confirm it is not. Streaming
generation is representable, but requires a real algorithm-family swap: a per-region xorshift
instance reseeded from `SEED` XOR/shift-mixed with `(row, col)` (no multiplication — SM83 has
none, the same shift/XOR-only construction `gw_prng_step` already uses), replacing both the
sequential biome-anchor chain and the global backtracking maze carve with pure functions of
`(seed, row, col)`. R114 further identifies the Binary Tree maze algorithm as the only proven
zero-memory streaming-compatible option, but flags its own directional dead-end bias as
conflicting with `IP-1021`'s just-shipped dead-end-priority win condition —
[ADR-0017](ADR-0017-infinite-mode-treasure-placement-and-win-condition.md) resolves that conflict.

[ADS-001](../ADS-001-streaming-infinite-world-generation.md) is the full design synthesis this ADR
and ADR-0017 are drawn from; see it for the complete system architecture, domain model, and Open
Questions this decision does not itself resolve.

**User authorization:** the project owner explicitly authorized this stage to make the
adoption call this session (`00-pipeline-manager` gate stop, 2026-07-13), after both
`02-research-gbc-hardware` (`R114`) and `02-research-game-design` (`R216`) halves completed.

## Decision

**Adopt streaming, positionally-deterministic world generation as the architecture for a new,
additive "Infinite Mode" — selectable at new-game creation alongside the existing finite
`(seed, scale)` model, not replacing it.** `ADR-0009`, `ADR-0010`, `ADR-0012`, and `ADR-0013`
continue to govern the finite mode's generation algorithm, seed/scale entry, and PRNG usage
**exactly as written, entirely unchanged** — this decision adds a second, independent generation
path, mirroring how `ADR-0012` refined `ADR-0009` without reversing it, except here neither ADR is
even refined, only cross-referenced.

Concretely:

1. **Infinite Mode takes a seed only, no world-scale.** There is no fixed grid extent to bound;
   `WorldScale`'s finite-mode meaning (`ADR-0010`) does not apply.
2. **Every region's biome and maze connectivity are computed on demand, at the moment the player
   approaches it**, as pure functions of `(seed, row, col)` — never as a whole-grid upfront pass.
   Regions outside a small materialized window around the player are not resident in WRAM at all;
   returning to a previously-visited region re-derives the identical result deterministically.
3. **Positional determinism is achieved by reseeding a fresh `gw_prng_step`-family xorshift
   instance from `SEED` XOR/shift-mixed with `(row, col)`**, per region — reusing the existing
   shift/XOR-only construction (`R111`/`R113`) without introducing a multiplication-based hash
   (standard techniques like FNV-1a are not portable to SM83, which has no hardware `MUL`/`DIV`).
   The seeded instance is discarded immediately after deriving that region's needed values; no
   per-region PRNG state persists.
4. **The maze algorithm is the Binary Tree algorithm** (carve north or west from each region,
   decided by one local PRNG draw) — the only maze family requiring zero memory and no
   sequential/backtracking history, per R114. Adopted specifically because
   [ADR-0017](ADR-0017-infinite-mode-treasure-placement-and-win-condition.md) removes the only
   reason its directional dead-end bias would matter to the win condition; its aesthetic quality
   (maze "feel") is not decided here (see ADS-001 Open Question 2).
5. **Save/load persists player position and a bounded visited-region ledger (which regions have
   had their treasure collected), not the region graph itself.** Biome/maze state is never
   persisted — it regenerates identically from `(seed, row, col)` on demand. This supersedes, for
   Infinite Mode only, `ADR-0009` point 3's "regenerate `REGION_GRAPH` from `(seed, scale)`"
   framing, which has no meaning without a fixed scale; the finite mode's own use of that framing
   is entirely unaffected.
6. **A materialized window is bounded to bank-0's ~3 KiB headroom (3082 bytes free, re-measured
   this session) first; `SVBK` banking (R111) is a fallback only if a chosen window radius
   concretely exceeds it** — `gbc_lib.py` has no `SVBK` emitter today, so banking is itself new
   toolchain work, not assumed free.
7. **This ADR authorizes the architecture target only.** No code ships from this decision — the
   actual generation routine, its Python oracle mirror, WRAM layout, and materialization-timing
   validation ship through the normal `04`→`05`→`06`→`07`→`08` pipeline, gated by G3, as a new
   epic distinct from the finite mode's existing implementation.

## Consequences

- **`ADR-0009`/`ADR-0010`/`ADR-0012`/`ADR-0013` are unamended** — forward-pointer notes are added
  to each, cross-referencing this ADR, per this project's append-only convention (the same pattern
  `ADR-0009`'s own top-of-file note set for `ADR-0012`). None of their Decision text changes.
- **Unblocks `BL-0094`** (the deferred infinite-mode win-condition design) to proceed to
  `04-requirements-engineering` once `ADR-0017` (below) is also in place.
- **Partially resolves `BL-0066`** for the Infinite Mode context only (see `ADR-0017`'s sibling
  treatment and ADS-001's Decision Log) — the finite-mode blob-clustering question `ADR-0012`
  originally left open is not resolved by this ADR and remains a separate pipeline-manager
  re-triage item.
- **Unblocks `BL-0050`** (finite-mode MAP/status-screen redesign) to proceed independently, since
  the two modes coexist rather than one superseding the other.
- **No `GDS-04`/`GDS-07`/`GDS-09` delta yet** — Infinite Mode's new entities (visited-region
  ledger, running/top-3 score) are named in ADS-001 but not formalized into the ladder; that is
  `04-requirements-engineering`'s scope for this new epic, exactly as the original procgen-world
  increment's own `GDS-04` delta followed `ADR-0009` in a later, separate pass.
- **Real open engineering risk, not resolved here:** whether a single region's materialization cost
  fits inside `check_zone_transition`'s existing safe window without a new LCD-off-style bracket —
  flagged for `07`/`08`-time direct cycle-counting (ADS-001 Open Question 4).
- **Does not itself implement anything** — per this pipeline's standing rule, an ADR records a
  binding design decision; the generation routine, Python oracle, and WRAM/SRAM layout ship through
  the normal pipeline, gated by G3 as always.

## Related

- Synthesized in [ADS-001](../ADS-001-streaming-infinite-world-generation.md) alongside
  [ADR-0017](ADR-0017-infinite-mode-treasure-placement-and-win-condition.md) (treasure placement
  and win condition for this same mode).
- Grounded by [R114](../../research/encyclopedia/R114-streaming-world-generation-feasibility.md)
  (feasibility, algorithm choice, WRAM/ROM budget) and
  [R111](../../research/encyclopedia/R111-wram-banking-sm83-prng.md)/[R113](../../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md)
  (PRNG construction this decision reuses).
- Cross-references, without amending: [ADR-0009](ADR-0009-screen-graph-world-generation.md),
  [ADR-0010](ADR-0010-seed-scale-model.md), [ADR-0012](ADR-0012-maze-shaped-region-adjacency.md),
  [ADR-0013](ADR-0013-maze-pass-prng-decorrelation.md) — all continue to govern the finite mode
  exactly as written.
- Resolves the architecture-adoption half of [BL-0082](../../pipeline/backlog.md). Unblocks
  [BL-0094](../../pipeline/backlog.md) and, indirectly, [BL-0050](../../pipeline/backlog.md).
  Partially addresses [BL-0066](../../pipeline/backlog.md) (Infinite Mode context only).
