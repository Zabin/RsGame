# Feature Planning — Index

Owned by `05-feature-decomposition` (sole write scope). Catalog rows use `FEAT-xxxx` IDs
(planning-grain summaries); the full specification documents they point forward to are stage 06's
`FS-xxx` files under `docs/features/`. Always exactly these five deliverables; see the skill for
templates.

[↑ Docs index](../INDEX.md)

| # | Document | File | Status |
|---|---|---|---|
| 1 | Release Plan (buckets: Baseline (as-built) / MVP / Release 1 / Release 2 / Future) | `01-release-plan.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200, CR-06/BL-0100); delta 2026-07-14 (FEAT-10000 joins Future, ADR-0016/0017/BL-0082); delta 2026-07-16 (FEAT-7100 joins Future, ADR-0019/BL-0127); delta 2026-07-17 (FEAT-11000 joins Future, ADS-002/MSTR-001 C11/BL-0133); delta 2026-07-20 (FEAT-11000 moves Future → Release 2 as a fourth addendum, assessed GO, user-confirmed, BL-0166) |
| 2 | Epic Catalog (EP-xxxx) | `02-epic-catalog.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200 joins EP-1000); delta 2026-07-14 (new EP-6000, FEAT-10000); delta 2026-07-16 (new EP-7000, FEAT-7100); delta 2026-07-17 (FEAT-11000 joins EP-6000) |
| 3 | Feature Catalog (FEAT-xxxx) | `03-feature-catalog.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200, 58 requirements total; forward-ref to FS-109 added); delta 2026-07-14 (FEAT-10000, 71 requirements total incl. BL-0102 tally fold-in); delta 2026-07-14 (cont'd) (FEAT-10000 Dependencies corrected to include FEAT-4100, BL-0111); delta 2026-07-16 (FEAT-10000's own forward-reference status refreshed to Implemented/Verified — all five IP-1100–IP-1104 packages VERIFIED, integration-reviewed clean, BL-0126); delta 2026-07-16 (cont'd) (new FEAT-7100, 74 requirements total, this project's first FR-7xxx audio Feature, ADR-0019/BL-0127); delta 2026-07-17 (new FEAT-11000, 82 requirements total, this project's first FR-11xxx Feature, ADS-002/MSTR-001 C11/BL-0133) |
| 4 | Feature Dependency Graph (Mermaid) | `04-feature-dependency-graph.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (FEAT-1200 added, no cycles); delta 2026-07-14 (FEAT-10000 added, no cycles); delta 2026-07-14 (cont'd) (FEAT-4100→FEAT-10000 edge added, BL-0111); delta 2026-07-16 (FEAT-7100 added, no cycles, ADR-0019/BL-0127); delta 2026-07-17 (FEAT-11000 added, no cycles, ADS-002/MSTR-001 C11/BL-0133) |
| 5 | Feature Review | `05-feature-review.md` | ✅ Authored (2026-07-07); delta 2026-07-10; delta 2026-07-11 (ADR-0012); delta 2026-07-13 (finding #8, FEAT-1200); delta 2026-07-14 (finding #9, FEAT-10000; BL-0102 closed); delta 2026-07-14 (cont'd) (finding #10, FEAT-10000↔FEAT-4100 dependency corrected; BL-0111 closed); delta 2026-07-16 (finding #11, FEAT-7100/EP-7000 added); delta 2026-07-17 (finding #12, FEAT-11000 joins EP-6000) |
