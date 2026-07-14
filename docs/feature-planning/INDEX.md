# Feature Planning — Index

Owned by `05-feature-decomposition` (sole write scope). Catalog rows use `FEAT-xxxx` IDs
(planning-grain summaries); the full specification documents they point forward to are stage 06's
`FS-xxx` files under `docs/features/`. Always exactly these five deliverables; see the skill for
templates.

[↑ Docs index](../INDEX.md)

| # | Document | File | Status |
|---|---|---|---|
| 1 | Release Plan (buckets: Baseline (as-built) / MVP / Release 1 / Release 2 / Future) | `01-release-plan.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200, CR-06/BL-0100); delta 2026-07-14 (FEAT-10000 joins Future, ADR-0016/0017/BL-0082) |
| 2 | Epic Catalog (EP-xxxx) | `02-epic-catalog.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200 joins EP-1000); delta 2026-07-14 (new EP-6000, FEAT-10000) |
| 3 | Feature Catalog (FEAT-xxxx) | `03-feature-catalog.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200, 58 requirements total; forward-ref to FS-109 added); delta 2026-07-14 (FEAT-10000, 71 requirements total incl. BL-0102 tally fold-in); delta 2026-07-14 (cont'd) (FEAT-10000 Dependencies corrected to include FEAT-4100, BL-0111) |
| 4 | Feature Dependency Graph (Mermaid) | `04-feature-dependency-graph.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200 added, no cycles); delta 2026-07-14 (FEAT-10000 added, no cycles); delta 2026-07-14 (cont'd) (FEAT-4100→FEAT-10000 edge added, BL-0111) |
| 5 | Feature Review | `05-feature-review.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (finding #8, FEAT-1200); delta 2026-07-14 (finding #9, FEAT-10000; BL-0102 closed); delta 2026-07-14 (cont'd) (finding #10, FEAT-10000↔FEAT-4100 dependency corrected; BL-0111 closed) |
