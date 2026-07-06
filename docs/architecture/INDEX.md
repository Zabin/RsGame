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
| GDS-00 | Vision (owned by `01-vision`) | [00-vision.md](00-vision.md) | ✅ Authored (gate closed 2026-07-06; content revised same day, see MSTR-001 §8) |
| GDS-01 | Concept of Play | [01-concept-of-play.md](01-concept-of-play.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-02 | System Context | [02-system-context.md](02-system-context.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-03 | Architecture | [03-architecture.md](03-architecture.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-04 | Domain Model | [04-domain-model.md](04-domain-model.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-05 | Functional Requirements | [05-functional-requirements.md](05-functional-requirements.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-06 | Non-functional Requirements | [06-non-functional-requirements.md](06-non-functional-requirements.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-07 | Data Model | [07-data-model.md](07-data-model.md) | ✅ Authored (gate closed 2026-07-06) |
| GDS-08 | Presentation Architecture | [08-presentation-architecture.md](08-presentation-architecture.md) | ⛔ Planned (scaffold only) |
| GDS-09 | Interface Specification | [09-interface-specification.md](09-interface-specification.md) | ⛔ Planned (scaffold only) |
| GDS-10 | Requirements Traceability Matrix level | [10-requirements-traceability-matrix.md](10-requirements-traceability-matrix.md) | ⛔ Planned (scaffold only) |

## §2 — Per-cluster design syntheses (ADS-xxx)

Zero-or-more documents, one per capability cluster with real design tension the ladder doesn't
resolve at the system level. Index-before-content: add the row (⛔ Planned) before writing the
file.

| ID | Cluster | File | Status |
|---|---|---|---|
| *(none yet)* | | | |

## §3 — Vision-layer artifacts owned by `01-vision`

| Artifact | File | Status |
|---|---|---|
| Strategic assumptions register | [strategic-assumptions-register.md](strategic-assumptions-register.md) | ✅ Authored 2026-07-06 (A1–A8, revised same day — A1/A6 corrected, A8 added, ♻️ living) |

## §4 — Architecture Decision Records

See [adr/INDEX.md](adr/INDEX.md). On the bootstrap increment, `03-architecture-design-synthesis`
mines `Claude.md`/`memory.md`/the code for decisions already made and records them as as-built
ADRs.
