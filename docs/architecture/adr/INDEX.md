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
