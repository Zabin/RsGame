# Docs — Master router

All prose documentation for Bunny Garden Adventure, organized by pipeline stage (see
[`.claude/skills/README.md`](../.claude/skills/README.md) for the pipeline itself and
[`ROADMAP.md`](../ROADMAP.md) for per-document status). Every directory has its own `INDEX.md`;
statuses live there and in the ROADMAP, kept in sync by the owning skill.

| Directory | Contents | Owning skill(s) |
|---|---|---|
| [`pipeline/`](pipeline/BOOTSTRAP.md) | The run-book ([BOOTSTRAP.md](pipeline/BOOTSTRAP.md)), the manager's journal ([pipeline-journal.md](pipeline/pipeline-journal.md), older runs in [pipeline-journal-archive.md](pipeline/pipeline-journal-archive.md)), backlog ([backlog.md](pipeline/backlog.md), closed entries in [backlog-archive.md](pipeline/backlog-archive.md)), and increment plans ([PLAN-requirements-aesthetics-story-map.md](pipeline/PLAN-requirements-aesthetics-story-map.md)) | `00-pipeline-manager`, `00-intake` |
| [`master/`](master/INDEX.md) | Program-level MSTR documents (vision, governance, …) | `01-vision` (+ `03`) |
| [`research/`](research/INDEX.md) | Encyclopedia tiers R100 (GBC hardware) / R200 (game design) / R300 (tooling & verification) | the three `02-research-*` skills |
| [`architecture/`](architecture/INDEX.md) | The GDS-00…10 ladder, ADS clusters, [ADRs](architecture/adr/INDEX.md), assumptions register | `03-architecture-design-synthesis` (+ `01-vision` for GDS-00) |
| [`requirements/`](requirements/INDEX.md) | FR/NFR baselines, Requirements Review, RTM | `04-requirements-engineering` |
| [`feature-planning/`](feature-planning/INDEX.md) | Release plan, epic/feature catalogs (FEAT-xxxx), dependency graph, feature review | `05-feature-decomposition` |
| [`features/`](features/INDEX.md) | Full Feature Specifications (FS-xxx) | `06-feature-specification` |
| [`implementation/`](implementation/00-master-build-plan.md) | Master Build Plan, TWBS, [packages (IP-xxxx)](implementation/packages/INDEX.md), [verification reports (VR-xxxx)](implementation/verification/INDEX.md) | `07-implementation-planning`, stage-08 peers, `09-package-verification` |
| [`reviews/`](reviews/INDEX.md) | Content reviews, integration reviews, release assessments | `09-content-review`, `10-integration-review`, `11-release-readiness` |

Repo-root working docs that predate the pipeline and stay live: [`Claude.md`](../Claude.md)
(developer quick-reference — merged into the GDS ladder level by level, per each level's recorded
merge decision) and [`memory.md`](../memory.md) (runtime notes & quick-reference tables,
maintained by the stage-08 skills).
