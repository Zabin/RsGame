# Master documents — Index

The `docs/master/` corpus holds the program-level statements every other document cites. Until
each is authored, the interim governance text is `.claude/skills/README.md` §"Hard rules the
stages share" (rules G1–G5).

[↑ Docs index](../INDEX.md)

| ID | Document | Owned by | Status |
|---|---|---|---|
| MSTR-001 | Program vision (`MSTR-001-program-vision.md`) | `01-vision` | ⛔ Planned |
| MSTR-002 | Architecture principles (`MSTR-002-architecture-principles.md`) | `03-architecture-design-synthesis` (optional; author when GDS-03's merge gate wants a home for cross-cutting principles) | ⛔ Planned |
| MSTR-003 | Design philosophy (`MSTR-003-design-philosophy.md`) | `01-vision`/`03` (optional) | ⛔ Planned |
| MSTR-004 | Glossary (`MSTR-004-glossary.md`) | any stage skill may add terms; `03` curates (optional) | ⛔ Planned |
| MSTR-005 | Documentation map (`MSTR-005-documentation-map.md`) | `03-architecture-design-synthesis` (optional; formalizes what `docs/INDEX.md` sketches) | ⛔ Planned |
| MSTR-006 | Governance principles (`MSTR-006-governance-principles.md`) — formalizes G1–G5 | `01-vision` (or `03`), when the interim README rules need elaboration | ⛔ Planned |
| MSTR-007 | Research philosophy (`MSTR-007-research-philosophy.md`) — formalizes the methodology embedded in the `02-research-*` skills | the `02-research-*` skills' owner, when the embedded methodology needs elaboration | ⛔ Planned |

Only MSTR-001 is required by the bootstrap increment; the rest are authored on demand when a
skill's inline rules prove insufficient. When an MSTR document is authored, update the skills
that cite the interim rules to cite it instead (a doc-defect backlog entry per skill is the clean
way to track that).
