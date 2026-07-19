# Architecture & Design Synthesis — Index

Owned by `03-architecture-design-synthesis` (GDS-01…10, ADS, ADRs) and `01-vision` (GDS-00 + the
strategic assumptions register). See [`.claude/skills/README.md`](../../.claude/skills/README.md)
for the pipeline.

[↑ Docs index](../INDEX.md)

## §1 — The global ladder (GDS-00…GDS-10)

Strictly sequential and gated: the next level may not start until the previous level's merge gate
is closed with its decision recorded in prose. Status here and in `ROADMAP.md` must never drift.

| Level | Title | File | Status |
|---|---|---|---|
| GDS-00 | Vision (owned by `01-vision`) | [00-vision.md](00-vision.md) | ✅ Authored (gate closed 2026-07-06; revised 2026-07-06, 2026-07-09 for MSTR-001 v3.0, and 2026-07-17 for v4.0's C11 dual-audience carve-out — see MSTR-001 §8/§8a) |
| GDS-01 | Concept of Play | [01-concept-of-play.md](01-concept-of-play.md) | ✅ Authored (gate closed 2026-07-06; delta 2026-07-09 for procgen-world increment, §§2a/3a/4a/4b; delta 2026-07-13 §4c — `SELECT` becomes a small menu (`MAP`/`LEGEND`), target state, `CR-06`/`BL-0100`; delta 2026-07-14 §4d — new-game mode choice (Finite/Infinite) via `MODE SELECT`, target state, `BL-0113`; delta 2026-07-17 §4e — combat sub-mode's own `COMBAT MODE CONFIRM` gating state, target state, `BL-0146`/`ADS-002`/`MSTR-001` C11) |
| GDS-02 | System Context | [02-system-context.md](02-system-context.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-03 | Architecture | [03-architecture.md](03-architecture.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-04 | Domain Model | [04-domain-model.md](04-domain-model.md) | ✅ Authored (gate closed 2026-07-06; delta 2026-07-09 for procgen-world increment — Seed/WorldScale/Region/KeyItem; delta 2026-07-10 — SaveGame bullet corrected, BL-0033; delta 2026-07-12 — `KeyItem` cardinality/win-condition corrected, `ADR-0015`) |
| GDS-05 | Functional Requirements | [05-functional-requirements.md](05-functional-requirements.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-06 | Non-functional Requirements | [06-non-functional-requirements.md](06-non-functional-requirements.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-07 | Data Model | [07-data-model.md](07-data-model.md) | ✅ Authored (gate closed 2026-07-06; delta 2026-07-09 for procgen-world increment — proposed WRAM/SRAM fields for seed/scale/region graph; delta 2026-07-12 — §7c per-region treasure-presence concept, `ADR-0015`; delta 2026-07-14 — §7d Infinite Mode per-region materialization WRAM, `IP-1101`; delta 2026-07-14 (cont'd) — §7e Infinite Mode streaming window/navigation/render WRAM, `IP-1102` (row sync lagged one package — added 2026-07-16); delta 2026-07-16 — §7f Infinite Mode treasure/win-condition WRAM, `IP-1103`, `C405`–`C40C`, joint reserve fully claimed) |
| GDS-08 | Presentation Architecture | [08-presentation-architecture.md](08-presentation-architecture.md) | ✅ Authored (gate closed 2026-07-06; delta 2026-07-09 for procgen-world increment — normative aesthetic standard + biome-transition palette strategy; delta 2026-07-11 §10 — maze-blocked edge indicator tile/palette decision, `BL-0068`/`FS-108` OQ1; delta 2026-07-13 §11 — edge-indicator legend/help screen content, `CR-06`/`BL-0100`) |
| GDS-09 | Interface Specification | [09-interface-specification.md](09-interface-specification.md) | ✅ Authored (gate closed 2026-07-06; delta 2026-07-09 for procgen-world increment — worldgen.py contract, new patch points) |
| GDS-10 | Requirements Traceability Matrix level | [10-requirements-traceability-matrix.md](10-requirements-traceability-matrix.md) | ✅ Authored (gate closed 2026-07-06; ID-scheme table refreshed 2026-07-09 — no new prefix needed for procgen-world increment; delta 2026-07-10 — §3/§4 converted to pointers at RQ-04, BL-0034) |

## §2 — Per-cluster design syntheses (ADS-xxx)

Zero-or-more documents, one per capability cluster with real design tension the ladder doesn't
resolve at the system level. Index-before-content: add the row (⛔ Planned) before writing the
file.

| ID | Cluster | File | Status |
|---|---|---|---|
| [ADS-001](ADS-001-streaming-infinite-world-generation.md) | Streaming, positionally-deterministic world generation for a new, additive Infinite Mode (`BL-0082`) | [ADS-001-streaming-infinite-world-generation.md](ADS-001-streaming-infinite-world-generation.md) | ✅ Authored (2026-07-13; produces `ADR-0016`/`ADR-0017`) |
| [ADS-002](ADS-002-infinite-mode-combat-sub-mode.md) | Infinite Mode combat sub-mode: mobs + treasure-fed ranged weapon (`BL-0133`) | [ADS-002-infinite-mode-combat-sub-mode.md](ADS-002-infinite-mode-combat-sub-mode.md) | ✅ **All eight Open Questions resolved or committed as adjustable defaults, 2026-07-17** (`MSTR-001` C11; `R218`/`R115` research; concrete architecture: 6-slot mob WRAM table, single-slot projectile, MODE SELECT "COMBAT MODE" gating option, A-button fire input, poof-defeat + reused heart-tile HUD; user decisions: treasure spent on healing, no weapon ammo/durability, non-lethal setback fail state, combat state persists across save/load). Still produces no `FS-xxx`/`FR-xxxx` — that's `04`/`06`'s own job next. **Delta 2026-07-19** (`BL-0157`, `ADR-0021`): weapon-directionality shape decided — a new `PLAYER_FACING` concept (not a widened `PLAYER_DIR`), 8-directional, diagonal projectile motion via independent per-axis stepping, no new player sprite art. |

## §3 — Vision-layer artifacts owned by `01-vision`

| Artifact | File | Status |
|---|---|---|
| Strategic assumptions register | [strategic-assumptions-register.md](strategic-assumptions-register.md) | ✅ Authored 2026-07-06 (A1–A8, revised same day — A1/A6 corrected, A8 added, ♻️ living) |

## §4 — Architecture Decision Records

See [adr/INDEX.md](adr/INDEX.md). On the bootstrap increment, `03-architecture-design-synthesis`
mines `Claude.md`/`memory.md`/the code for decisions already made and records them as as-built
ADRs.
