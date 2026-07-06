# Documentation Roadmap

Single authoritative tracker for **every document this project produces or has planned** — what
exists, what depends on what, and what's still open. Humans and future sessions read this file
first to answer "what's done, what's in flight, what's left" without re-deriving it from `git
log` or scanning the tree.

**Update this file whenever a document's status changes.** Finish a doc → flip it to ✅. Start
one → 🚧. Identify a new doc → add a row with `⛔ Planned`. Don't let this file drift from
reality. The owning skill flips its rows together with the theme `INDEX.md` in the same commit.

## Status legend

| Symbol | Meaning |
|---|---|
| ✅ | Done — written, current, matches the implementation/research it describes. |
| 🚧 | In progress — drafted but incomplete, or gate not fully closed. |
| ⛔ | Planned — identified as needed, not yet started. |
| ♻️ | Living — intentionally never "done"; updated continuously. |

`Depends on` lists the IDs whose content a document assumes or must stay consistent with — not a
build order.

---

## Root guides

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RT-README | Project overview & quick start | `README.md` | — | ♻️ |
| RT-CLAUDE | Durable developer/agent quick-reference | `Claude.md` | GDS ladder merge decisions | ♻️ |
| RT-MEMORY | Runtime notes & quick-ref tables | `memory.md` | — | ♻️ |
| RT-ROADMAP | This file | `ROADMAP.md` | all IDs below | ♻️ |
| RT-INDEX | Master docs router | `docs/INDEX.md` | all theme indexes | ♻️ |
| RT-BOOTSTRAP | Bootstrap run-book | `docs/pipeline/BOOTSTRAP.md` | pipeline README | ✅ |

## Theme: Pipeline (`docs/pipeline/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| PL-JOURNAL | Pipeline journal | `docs/pipeline/pipeline-journal.md` | — | ♻️ |
| PL-BACKLOG | Pipeline backlog | `docs/pipeline/backlog.md` | — | ♻️ |

## Theme: Master (`docs/master/`) — owner `01-vision` (+ `03`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| MSTR-001 | Program vision | `docs/master/MSTR-001-program-vision.md` | — | ✅ |
| MSTR-002…007 | Optional principle docs (see `docs/master/INDEX.md`) | `docs/master/` | MSTR-001 | ⛔ (on demand) |

## Theme: Research (`docs/research/`) — owners: the three `02-research-*` skills

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RS-INDEX | Research index (tier tables) | `docs/research/INDEX.md` | — | ♻️ |
| R101–R110 | Tier R100 — GBC hardware & SM83 | `docs/research/encyclopedia/` | MSTR-001 | ✅ (2026-07-06) |
| R201–R211 | Tier R200 — Game design (incl. R209–R211, pixel art / AI-generation workflow / GBC case studies, filed via `BL-0013`) | `docs/research/encyclopedia/` | MSTR-001 | ✅ (2026-07-06) |
| R301–R306 | Tier R300 — Tooling & verification | `docs/research/encyclopedia/` | MSTR-001 | ✅ (2026-07-06) |

## Theme: Architecture (`docs/architecture/`) — owner `03-architecture-design-synthesis` (+ `01-vision` for GDS-00)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| GDS-00 | Vision level | `docs/architecture/00-vision.md` | MSTR-001 | ✅ |
| GDS-01 | Concept of Play | `docs/architecture/01-concept-of-play.md` | GDS-00 | ✅ (2026-07-06) |
| GDS-02 | System Context | `docs/architecture/02-system-context.md` | GDS-01 | ⛔ (scaffold) |
| GDS-03 | Architecture | `docs/architecture/03-architecture.md` | GDS-02 | ⛔ (scaffold) |
| GDS-04 | Domain Model | `docs/architecture/04-domain-model.md` | GDS-03 | ⛔ (scaffold) |
| GDS-05 | Functional Requirements | `docs/architecture/05-functional-requirements.md` | GDS-04 | ⛔ (scaffold) |
| GDS-06 | Non-functional Requirements | `docs/architecture/06-non-functional-requirements.md` | GDS-05 | ⛔ (scaffold) |
| GDS-07 | Data Model | `docs/architecture/07-data-model.md` | GDS-06 | ⛔ (scaffold) |
| GDS-08 | Presentation Architecture | `docs/architecture/08-presentation-architecture.md` | GDS-07 | ⛔ (scaffold) |
| GDS-09 | Interface Specification | `docs/architecture/09-interface-specification.md` | GDS-08 | ⛔ (scaffold) |
| GDS-10 | RTM level | `docs/architecture/10-requirements-traceability-matrix.md` | GDS-09 | ⛔ (scaffold) |
| AR-ASSUME | Strategic assumptions register | `docs/architecture/strategic-assumptions-register.md` | MSTR-001 | ♻️ (A1–A8, revised 2026-07-06) |
| ADR-xxxx | Architecture Decision Records | `docs/architecture/adr/` | GDS-03 | ⛔ (as-built set) |
| ADS-xxx | Per-cluster design syntheses | `docs/architecture/` | research tiers | ⛔ (zero-or-more, on demand) |

## Theme: Requirements (`docs/requirements/`) — owner `04-requirements-engineering`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RQ-01 | Functional Requirements | `docs/requirements/01-functional-requirements.md` | GDS-01…05, ADRs | ⛔ |
| RQ-02 | Non-Functional Requirements | `docs/requirements/02-non-functional-requirements.md` | GDS-06 | ⛔ |
| RQ-03 | Requirements Review | `docs/requirements/03-requirements-review.md` | RQ-01, RQ-02 | ⛔ |
| RQ-04 | Requirements Traceability Matrix | `docs/requirements/04-requirements-traceability-matrix.md` | RQ-01…03 | ⛔ |

## Theme: Feature planning (`docs/feature-planning/`) — owner `05-feature-decomposition`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| FP-01 | Release Plan | `docs/feature-planning/01-release-plan.md` | RQ baseline | ⛔ |
| FP-02 | Epic Catalog | `docs/feature-planning/02-epic-catalog.md` | FP-03 | ⛔ |
| FP-03 | Feature Catalog (FEAT-xxxx) | `docs/feature-planning/03-feature-catalog.md` | RQ baseline | ⛔ |
| FP-04 | Feature Dependency Graph | `docs/feature-planning/04-feature-dependency-graph.md` | FP-03 | ⛔ |
| FP-05 | Feature Review | `docs/feature-planning/05-feature-review.md` | FP-01…04 | ⛔ |

## Theme: Feature specifications (`docs/features/`) — owner `06-feature-specification`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| FS-101+ | One spec per approved Feature | `docs/features/FS-xxx-*.md` | FP catalog, RQ baseline | ⛔ |

## Theme: Implementation (`docs/implementation/`) — owners `07`/`08`/`09`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| IM-00 | Master Build Plan | `docs/implementation/00-master-build-plan.md` | FS specs | ♻️ (scaffold) |
| IM-01 | Technical Work Breakdown | `docs/implementation/01-technical-work-breakdown.md` | FS specs | ⛔ |
| IP-xxxx | Implementation Packages | `docs/implementation/packages/` | IM-01 | ⛔ |
| VR-xxxx | Verification Reports | `docs/implementation/verification/` | IP-xxxx at COMPLETE | ⛔ |

## Theme: Reviews (`docs/reviews/`) — owners `09-content-review`/`10`/`11`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RV-CONTENT | Content reviews | `docs/reviews/content-review-*.md` | content packages | ⛔ (per scope) |
| RV-INTEG | Integration reviews | `docs/reviews/integration-review-*.md` | tranche VERIFIED | ⛔ (per scope) |
| RV-RELEASE | Release assessments | `docs/reviews/release-assessment-*.md` | RV-INTEG | ⛔ (per release) |
