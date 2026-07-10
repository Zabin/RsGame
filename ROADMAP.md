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
| RT-README | Project overview & quick start | `README.md` | — | ♻️ (refreshed 2026-07-09, IP-9030) |
| RT-CLAUDE | Durable developer/agent quick-reference | `Claude.md` | GDS ladder merge decisions | ♻️ (refreshed 2026-07-09, IP-9030 — byte-level tables now supersede to GDS-07/08) |
| RT-MEMORY | Runtime notes & quick-ref tables | `memory.md` | — | ♻️ (refreshed 2026-07-09, IP-9030) |
| RT-ROADMAP | This file | `ROADMAP.md` | all IDs below | ♻️ |
| RT-INDEX | Master docs router | `docs/INDEX.md` | all theme indexes | ♻️ |
| RT-BOOTSTRAP | Bootstrap run-book | `docs/pipeline/BOOTSTRAP.md` | pipeline README | ✅ |

## Theme: Pipeline (`docs/pipeline/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| PL-JOURNAL | Pipeline journal | `docs/pipeline/pipeline-journal.md` | — | ♻️ |
| PL-BACKLOG | Pipeline backlog | `docs/pipeline/backlog.md` | — | ♻️ |
| PL-PLAN-ASM | Increment plan: requirements for aesthetics / visual story / procgen map | `docs/pipeline/PLAN-requirements-aesthetics-story-map.md` | MSTR-001, PL-BACKLOG, RQ baseline | ✅ **PHASE 4 COMPLETE** (adopted 2026-07-09; all 4 phases executed same day, runs #31–#42 — RQ-01…04 delta is the terminal deliverable) |

## Theme: Master (`docs/master/`) — owner `01-vision` (+ `03`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| MSTR-001 | Program vision | `docs/master/MSTR-001-program-vision.md` | — | ✅ v3.0 (2026-07-09 — adds C8/C9/C10, amends C2; see §8) |
| MSTR-002…007 | Optional principle docs (see `docs/master/INDEX.md`) | `docs/master/` | MSTR-001 | ⛔ (on demand) |

## Theme: Research (`docs/research/`) — owners: the three `02-research-*` skills

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RS-INDEX | Research index (tier tables) | `docs/research/INDEX.md` | — | ♻️ |
| R101–R111 | Tier R100 — GBC hardware & SM83 (R111, CGB banked WRAM + SM83 PRNG determinism, added 2026-07-09 via `BL-0031`; R102/R106 extended same day) | `docs/research/encyclopedia/` | MSTR-001 | ✅ (2026-07-06; R111 + extensions 2026-07-09) |
| R201–R214 | Tier R200 — Game design (incl. R209–R211, pixel art / AI-generation workflow / GBC case studies, filed via `BL-0013`; R212–R214, wordless narrative / procgen algorithms / GBC procgen case studies, filed via `BL-0030`/`BL-0031`) | `docs/research/encyclopedia/` | MSTR-001 | ✅ (2026-07-06; R212–R214 added 2026-07-09) |
| R301–R306 | Tier R300 — Tooling & verification (R302/R305 extended 2026-07-09 for MSTR-001 C10's reference-generator-oracle testing strategy, via `BL-0031`) | `docs/research/encyclopedia/` | MSTR-001 | ✅ (2026-07-06; extensions 2026-07-09) |

## Theme: Architecture (`docs/architecture/`) — owner `03-architecture-design-synthesis` (+ `01-vision` for GDS-00)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| GDS-00 | Vision level | `docs/architecture/00-vision.md` | MSTR-001 | ✅ (revised 2026-07-09 for MSTR-001 v3.0) |
| GDS-01 | Concept of Play | `docs/architecture/01-concept-of-play.md` | GDS-00 | ✅ (2026-07-06; delta 2026-07-09 for procgen-world increment) |
| GDS-02 | System Context | `docs/architecture/02-system-context.md` | GDS-01 | ✅ (2026-07-06) |
| GDS-03 | Architecture | `docs/architecture/03-architecture.md` | GDS-02 | ✅ (2026-07-06) |
| GDS-04 | Domain Model | `docs/architecture/04-domain-model.md` | GDS-03 | ✅ (2026-07-06; delta 2026-07-09 for procgen-world increment) |
| GDS-05 | Functional Requirements | `docs/architecture/05-functional-requirements.md` | GDS-04 | ✅ (2026-07-06) |
| GDS-06 | Non-functional Requirements | `docs/architecture/06-non-functional-requirements.md` | GDS-05 | ✅ (2026-07-06) |
| GDS-07 | Data Model | `docs/architecture/07-data-model.md` | GDS-06 | ✅ (2026-07-06; delta 2026-07-09 for procgen-world increment) |
| GDS-08 | Presentation Architecture | `docs/architecture/08-presentation-architecture.md` | GDS-07 | ✅ (2026-07-06; delta 2026-07-09 — normative aesthetic standard + biome-transition strategy for C8/C9) |
| GDS-09 | Interface Specification | `docs/architecture/09-interface-specification.md` | GDS-08 | ✅ (2026-07-06; delta 2026-07-09 — worldgen.py contract, new patch points) |
| GDS-10 | RTM level | `docs/architecture/10-requirements-traceability-matrix.md` | GDS-09 | ✅ (2026-07-06; ID-scheme refreshed 2026-07-09 — confirms no new prefix needed for procgen-world increment) |
| AR-ASSUME | Strategic assumptions register | `docs/architecture/strategic-assumptions-register.md` | MSTR-001 | ♻️ (A1–A10, revised 2026-07-09) |
| ADR-xxxx | Architecture Decision Records | `docs/architecture/adr/` | GDS-03 | ✅ (as-built set ADR-0001…0008, 2026-07-06; ADR-0009…0011 added 2026-07-09 for the procgen-world increment, ADR-0009 supersedes ADR-0001) |
| ADS-xxx | Per-cluster design syntheses | `docs/architecture/` | research tiers | ⛔ (zero-or-more, on demand) |

## Theme: Requirements (`docs/requirements/`) — owner `04-requirements-engineering`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RQ-01 | Functional Requirements | `docs/requirements/01-functional-requirements.md` | GDS-01…05, ADRs | ✅ (2026-07-06; delta 2026-07-09, FR-1170–FR-9200, procgen-world increment) |
| RQ-02 | Non-Functional Requirements | `docs/requirements/02-non-functional-requirements.md` | GDS-06 | ✅ (2026-07-06; delta 2026-07-09, NFR-1300–NFR-6510, procgen-world increment) |
| RQ-03 | Requirements Review | `docs/requirements/03-requirements-review.md` | RQ-01, RQ-02 | ✅ (2026-07-06; delta 2026-07-09, findings #7–10) |
| RQ-04 | Requirements Traceability Matrix | `docs/requirements/04-requirements-traceability-matrix.md` | RQ-01…03 | ✅ (2026-07-06; delta 2026-07-09, 16 new rows) |

## Theme: Feature planning (`docs/feature-planning/`) — owner `05-feature-decomposition`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| FP-01 | Release Plan | `docs/feature-planning/01-release-plan.md` | RQ baseline | ✅ (2026-07-07; delta 2026-07-10 — Release 2 populated, FEAT-5100/`BL-0036` corrected) |
| FP-02 | Epic Catalog | `docs/feature-planning/02-epic-catalog.md` | FP-03 | ✅ (2026-07-07; delta 2026-07-10 — EP-5000 added) |
| FP-03 | Feature Catalog (FEAT-xxxx) | `docs/feature-planning/03-feature-catalog.md` | RQ baseline | ✅ (2026-07-07; delta 2026-07-10 — 5 new Features, 53 requirements total) |
| FP-04 | Feature Dependency Graph | `docs/feature-planning/04-feature-dependency-graph.md` | FP-03 | ✅ (2026-07-07; delta 2026-07-10 — no cycles, critical path FEAT-9000→FEAT-4100→FEAT-6100) |
| FP-05 | Feature Review | `docs/feature-planning/05-feature-review.md` | FP-01…04 | ✅ (2026-07-07; re-run 2026-07-10 — 1 new Low finding, 2 prior findings closed) |

## Theme: Feature specifications (`docs/features/`) — owner `06-feature-specification`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| FS-101+ | One spec per approved Feature | `docs/features/FS-xxx-*.md` | FP catalog, RQ baseline | ✅ (FS-101 ✅ shipped/VERIFIED 2026-07-07; FS-102–106 ✅ 2026-07-10, all five Release-2 Features specified, none yet implemented — 7 Open Questions total routed to `07`) |

## Theme: Implementation (`docs/implementation/`) — owners `07`/`08`/`09`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| IM-00 | Master Build Plan | `docs/implementation/00-master-build-plan.md` | FS specs | ♻️ (live — 5 packages tracked, 2026-07-07) |
| IM-01 | Technical Work Breakdown | `docs/implementation/01-technical-work-breakdown.md` | FS specs | ✅ (first pass, 2026-07-07) |
| IP-xxxx | Implementation Packages | `docs/implementation/packages/` | IM-01 | 🚧 (IP-9010/9020/9030/9040 + IP-1010 authored 2026-07-07; none implemented) |
| VR-xxxx | Verification Reports | `docs/implementation/verification/` | IP-xxxx at COMPLETE | ⛔ |

## Theme: Reviews (`docs/reviews/`) — owners `09-content-review`/`10`/`11`

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RV-CONTENT | Content reviews | `docs/reviews/content-review-*.md` | content packages | ⛔ (per scope) |
| RV-INTEG | Integration reviews | `docs/reviews/integration-review-*.md` | tranche VERIFIED | ✅ (bootstrap tranche, 2026-07-10 — clean, 2 Medium doc-drift findings, no Critical/High) |
| RV-RELEASE | Release assessments | `docs/reviews/release-assessment-*.md` | RV-INTEG | ⛔ (per release) |
