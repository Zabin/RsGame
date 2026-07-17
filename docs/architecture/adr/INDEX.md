# Architecture Decision Records — Index

Owned by `03-architecture-design-synthesis`. One decision per `ADR-xxxx-<slug>.md` file:
Context · Decision · Status (accepted/superseded) · Consequences. Append-only history —
supersede, never rewrite.

Mined from `Claude.md`/`memory.md`/the code and from the GDS-00…GDS-10 ladder's own findings,
per [`BL-0016`](../../pipeline/backlog.md). Eight as-built decisions recorded on the bootstrap
increment's first ADR-authoring pass (2026-07-06). Three new decisions (ADR-0009…0011) added
2026-07-09 for the adopted aesthetics/visual-story-narrative/procgen-world-map increment
(per `BL-0031`, [PLAN-requirements-aesthetics-story-map.md](../../pipeline/PLAN-requirements-aesthetics-story-map.md)
Phase 3); ADR-0009's decision supersedes ADR-0001's single-bank scope.

[↑ Architecture index](../INDEX.md)

| ID | Title | Status | Date |
|---|---|---|---|
| [ADR-0001](ADR-0001-single-bank-rom-no-mbc-switching.md) | Single 32KB ROM bank, no MBC bank switching (yet) | **Superseded by ADR-0011** | 2026-07-06 |
| [ADR-0002](ADR-0002-python-assembler-over-rgbds.md) | Python assembler (`gbc_lib.py`) instead of the RGBDS toolchain | Accepted | 2026-07-06 |
| [ADR-0003](ADR-0003-one-job-per-file-module-decomposition.md) | One-job-per-file module decomposition | Accepted | 2026-07-06 |
| [ADR-0004](ADR-0004-patch-point-dict-linkage-contract.md) | Patch-point dict as the code↔data linkage contract | Accepted | 2026-07-06 |
| [ADR-0005](ADR-0005-shadow-oam-dma-every-frame.md) | Shadow-OAM DMA every frame | Accepted | 2026-07-06 |
| [ADR-0006](ADR-0006-mbc1-ram-battery-cart-type.md) | MBC1+RAM+BATTERY cartridge type with `BUNY`-magic save format | Accepted | 2026-07-06 |
| [ADR-0007](ADR-0007-8x16-obj-sprite-mode.md) | 8×16 OBJ sprite mode (corrects this project's own earlier "8×8" framing) | Accepted | 2026-07-06 |
| [ADR-0008](ADR-0008-pyboy-headless-verification-target.md) | PyBoy headless emulator as the verification target, not real hardware | Accepted | 2026-07-06 |
| [ADR-0009](ADR-0009-screen-graph-world-generation.md) | Screen/room-graph procedural world generation, on-console at new-game creation | Accepted | 2026-07-09 |
| [ADR-0010](ADR-0010-seed-scale-model.md) | Seed & world-scale parameter model (16-bit seed, scale 2–9, new-game-only entry) | Accepted | 2026-07-09 |
| [ADR-0011](ADR-0011-bank-switching-mbc1-default-wiring.md) | MBC1 default-wiring ROM bank switching (supersedes ADR-0001) | Accepted | 2026-07-09 |
| [ADR-0012](ADR-0012-maze-shaped-region-adjacency.md) | Maze-shaped region adjacency — spanning tree (recursive backtracker) + braid pass, refines ADR-0009 point 1 | Accepted | 2026-07-11 |
| [ADR-0013](ADR-0013-maze-pass-prng-decorrelation.md) | Maze-pass PRNG decorrelation via a per-draw loop-index perturbation (`gw_prng_step` itself unchanged) | Accepted | 2026-07-11 |
| [ADR-0014](ADR-0014-gw-prng-step-repair-needs-user-authorization.md) | `gw_prng_step` repair (shift-triplet `7,9,8`) confirmed the correct fix — 100% of tested seeds degenerate, not just the default; shipping it is routed `NEEDS-USER`, not authorized here | Accepted | 2026-07-11 |
| [ADR-0015](ADR-0015-dead-end-anchored-treasure-and-win-condition.md) | Dead-end-anchored treasure placement (`WORLD_SCALE` count, pre-braid leaf priority, random-fill fallback) and scale-count win condition, supersedes `GDS-04`'s "exactly one `KeyItem` per `Region`" rule | Accepted | 2026-07-12 |
| [ADR-0016](ADR-0016-streaming-infinite-mode-generation-architecture.md) | Streaming, positionally-deterministic generation architecture for a new, additive Infinite Mode (Binary Tree maze, `hash(SEED,row,col)` biome/connectivity, visited-region-ledger save model) — finite mode (`ADR-0009`/`ADR-0012`/`ADR-0013`) unaffected | Accepted | 2026-07-13 |
| [ADR-0017](ADR-0017-infinite-mode-treasure-placement-and-win-condition.md) | Infinite Mode treasure placement decoupled from maze structure (`hash(SEED,row,col) mod K`) and score-chasing win condition (running count + top-3, no name-entry UI) | Accepted | 2026-07-13 |
| [ADR-0018](ADR-0018-finite-mode-biome-blob-clustering.md) | Finite-mode biome-blob clustering via per-super-cell positional hash (deterministic snap-to-blob, existing grammar-constrained draw as fallback), refines ADR-0009 point 2, resolves `CR-05`/`BL-0066` | Accepted | 2026-07-14 |
| [ADR-0019](ADR-0019-procedural-music-generation-architecture.md) | Procedural music generation: build-time theme-and-variation (transposition + tempo/duration scaling) from the existing main theme, nine sub-themes per `FR-4320`'s biome-family axis, no new APU channel, no `worldgen.py`-style sibling module (no runtime/oracle lockstep needed) | Accepted | 2026-07-16 |
