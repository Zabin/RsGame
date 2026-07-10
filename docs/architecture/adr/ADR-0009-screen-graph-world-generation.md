# ADR-0009 — Screen/room-graph procedural world generation, executed on-console at new-game creation

**Status:** Accepted (2026-07-09)

## Context

[MSTR-001](../../master/MSTR-001-program-vision.md) **C10** (v3.0) commits the world to
deterministic procedural generation from a user-set seed and world-scale parameter, both fixed
at new-game creation (**D3/D6/D7**) — the first concrete shape of **C7**'s long-term scale
direction. **C9** requires that the generated world read as a coherent journey: a **logical
biome-adjacency grammar** between whole screens (one biome per screen; e.g. water → beach →
grassland → hills → mountains → sky; never a disjointed pairing), per
[R212](../../research/encyclopedia/R212-wordless-environmental-storytelling-biome-grammar.md).

The shipped game's adjacency is today entirely hand-authored and arbitrary: `tilemaps.py`'s
`_zone_arrows(tiles, attrs, zone)` derives `row, col = zone // 3, zone % 3` and places directional
arrows purely from fixed 3×3-rectangle boundary math — no adjacency *rule* exists, only a fixed
grid shape. This is exactly what C10/C5 (per MSTR-001 §8's blast-radius enumeration) supersedes.

[R213](../../research/encyclopedia/R213-procedural-map-generation-algorithms.md) surveyed
generation algorithm families against this project's actual two-sided architecture (unconstrained
Python build side; heavily constrained SM83 runtime side) and recommended **screen/room-graph
generation**, not per-tile approaches (cellular automata, Wave Function Collapse) — WFC in
particular carries known complexity/contradiction risk[^R213] poorly suited to a hard-real-time,
backtracking-unfriendly SM83 runtime.
[R214](../../research/encyclopedia/R214-gbc-homebrew-procgen-case-studies.md) grounds this
recommendation's real-hardware feasibility: **Roguecraft GB**, a shipped, award-winning GBC
homebrew title, generates ten dungeons as **5×5 room-graph maps** within real GBC memory
constraints — direct, corroborated evidence that this project's own architecture (already
screen-composed, per `ALL_SCREENS`/GDS-04) is the right unit for procedural generation on this
hardware class, not a novel risk.

## Decision

**Adopt screen/room-graph generation, executed on-console (SM83 runtime) at new-game creation,
from `(seed, scale)`, seeded once and run to completion before the first `PLAYING` frame.**

Concretely:

1. **Generation unit is the screen, not the tile.** A generated world is a graph of `scale`-
   determined region nodes (one biome assignment per node), connected by adjacency edges — the
   same granularity `ALL_SCREENS`/`_zone_arrows` already use, generalized past a fixed 3×3.
2. **The adjacency grammar (R212) is enforced by construction, not by post-hoc validation.** The
   generator only ever proposes edges the grammar table permits (e.g. water may connect to beach
   but never directly to sky); a constrained-random graph walk over *legal* edges cannot produce
   an illegal adjacency, avoiding WFC-style contradiction/backtracking entirely — R213's stated
   reason to prefer this shape over per-tile constraint solving.
3. **Runs on SM83 at new-game creation, not precomputed on the Python build side.** Per D7, the
   seed/scale pair is entered once, at new-game creation, and the resulting world must be
   reproducible from that pair alone (assumption **A9**) — generating on-console keeps the
   save format minimal (persist `(seed, scale)`, not the generated world itself; see
   [ADR-0010](ADR-0010-seed-scale-model.md)) and gives the Python reference-generator oracle
   ([R305](../../research/encyclopedia/R305-emulator-based-test-design.md)) a single well-defined
   routine to mirror.
4. **Uses the xorshift-family PRNG and WRAM budget
   [R111](../../research/encyclopedia/R111-wram-banking-sm83-prng.md) grounds** — 2–4 bytes of
   state, seeded once from the player's seed value, no `DIV`/uninitialized-RAM dependence.
5. **Generation runs under the same LCD-off bracket `do_screen_redraw` already uses** for
   full-screen work ([R102](../../research/encyclopedia/R102-ppu-vram-oam-timing.md)'s
   extension) — no new "safe window" convention.
6. **`_zone_arrows`'s hardcoded rectangle math is superseded**, not patched — a generated world's
   directional-arrow logic reads neighbor validity from the generated adjacency graph, not from
   `row//3`/`col%3` arithmetic. This is a deliberate C5 protected-baseline amendment (already
   named in MSTR-001 §8), implemented once the corresponding package ships (not by this ADR).
7. **Per-region content (terrain texture within an assigned biome) continues to use the existing
   `_fill()` seeded-sprinkle pattern** ([GDS-08](../08-presentation-architecture.md) §1) — this
   ADR decides *which biome goes where and how regions connect*, not *how a biome's terrain
   looks*, preserving the existing, working separation of concerns.

## Consequences

- **New `asm_game.py` routine(s)**: a graph-generation routine (PRNG step + grammar-constrained
  edge selection + biome assignment), invoked once per new game. Code-only cost — no large
  precomputed map data — which is a net ROM *saving* relative to the nine hand-authored screen
  tilemaps it replaces, directly supporting C10's framing that procedural generation helps the
  ROM budget rather than merely adding a feature.
- **A new build-side Python module** (per
  [R302](../../research/encyclopedia/R302-python-assembler-codegen-patterns.md)'s extension,
  proposed as a `worldgen.py` sibling to `tiles.py`/`tilemaps.py`/`music.py`) reimplementing this
  exact algorithm as `test_rom.py`'s reference-generator oracle — the SM83 routine and the Python
  oracle must be kept in lockstep by direct correspondence (same PRNG step order, same grammar
  check), the discipline R305's extension already names.
- **The determinism/reachability/one-item-per-region/grammar-validity invariants
  ([R305](../../research/encyclopedia/R305-emulator-based-test-design.md)'s extension) become
  this generator's Definition-of-Done** once packaged — generator-*guaranteed* properties, not
  authored conventions (the `BL-0017` precedent, generalized).
- **Per-screen biome content still needs actual tile data for each biome family** — this ADR
  does not size how many distinct biome tile sets are needed at a given world scale; that is
  [GDS-08](../08-presentation-architecture.md)'s delta (Phase 3, per the adopted plan) and
  contends for the ROM headroom [ADR-0011](ADR-0011-bank-switching-mbc1-default-wiring.md)
  addresses.
- **Does not itself implement anything** — per this pipeline's rules, an ADR records a binding
  design decision; the actual generator routine, its Python oracle, and the `_zone_arrows`
  supersession ship through the normal `04`→`05`→`06`→`07`→`08` path, gated by G3 as always.

[^R213]: [R213](../../research/encyclopedia/R213-procedural-map-generation-algorithms.md)
§"Concepts" (WFC complexity/contradiction citations) and §"Implementation Guidance"
("Recommend screen/room-graph generation as the primary structural algorithm").
