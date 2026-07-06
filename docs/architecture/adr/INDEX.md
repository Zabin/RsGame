# Architecture Decision Records — Index

Owned by `03-architecture-design-synthesis`. One decision per `ADR-xxxx-<slug>.md` file:
Context · Decision · Status (accepted/superseded) · Consequences. Append-only history —
supersede, never rewrite.

Mined from `Claude.md`/`memory.md`/the code and from the GDS-00…GDS-10 ladder's own findings,
per [`BL-0016`](../../pipeline/backlog.md). Eight as-built decisions recorded on the bootstrap
increment's first ADR-authoring pass (2026-07-06); all Accepted, none superseded yet.

[↑ Architecture index](../INDEX.md)

| ID | Title | Status | Date |
|---|---|---|---|
| [ADR-0001](ADR-0001-single-bank-rom-no-mbc-switching.md) | Single 32KB ROM bank, no MBC bank switching (yet) | Accepted | 2026-07-06 |
| [ADR-0002](ADR-0002-python-assembler-over-rgbds.md) | Python assembler (`gbc_lib.py`) instead of the RGBDS toolchain | Accepted | 2026-07-06 |
| [ADR-0003](ADR-0003-one-job-per-file-module-decomposition.md) | One-job-per-file module decomposition | Accepted | 2026-07-06 |
| [ADR-0004](ADR-0004-patch-point-dict-linkage-contract.md) | Patch-point dict as the code↔data linkage contract | Accepted | 2026-07-06 |
| [ADR-0005](ADR-0005-shadow-oam-dma-every-frame.md) | Shadow-OAM DMA every frame | Accepted | 2026-07-06 |
| [ADR-0006](ADR-0006-mbc1-ram-battery-cart-type.md) | MBC1+RAM+BATTERY cartridge type with `BUNY`-magic save format | Accepted | 2026-07-06 |
| [ADR-0007](ADR-0007-8x16-obj-sprite-mode.md) | 8×16 OBJ sprite mode (corrects this project's own earlier "8×8" framing) | Accepted | 2026-07-06 |
| [ADR-0008](ADR-0008-pyboy-headless-verification-target.md) | PyBoy headless emulator as the verification target, not real hardware | Accepted | 2026-07-06 |
