# FS-106 — Aesthetic & Biome-Transition Compliance

> Feature Specification for [FEAT-6100](../feature-planning/03-feature-catalog.md#feat-6100--aesthetic--biome-transition-compliance-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-6100, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-106` — expands `FEAT-6100` (Aesthetic & Biome-Transition Compliance), Epic `EP-5000` (World
Generation & Visual Narrative).

## 2. Title

Aesthetic & Biome-Transition Compliance

## 3. Purpose

Give `09-content-review`'s existing "does this screen read well" judgment a written standard to
check against — craft rules for tile/sprite art and a palette-stepping strategy for
grammar-adjacent biome families. Carried forward verbatim from FEAT-6100's own Purpose (High
User Value, indirectly — MSTR-001 C8/D4's "every screen clean" quality bar).

## 4. Scope

**In scope:** the compliance standard itself (already authored, GDS-08 delta §7/§8) and its
review process — this is a verification/quality-gate capability, not new player-visible behavior
of its own (carried forward from FEAT-6100's own framing, "an internally complete system
capability," the same allowance FEAT-7000 uses).

**Out of scope** (per FEAT-6100's own Excluded Requirements, carried forward verbatim): *which*
biomes are adjacent (FR-4310 — [FEAT-9000](FS-102-procedural-world-generation.md)'s grammar-legal
generation); *how* a screen is structurally composed (FR-4300 —
[FEAT-4100](FS-103-generated-region-screen-composition.md)'s one-biome-per-screen rule). This
Feature judges the aesthetic quality of what those two Features produce; it does not produce
game behavior itself.

## 5. Requirements Implemented

NFR-6500, NFR-6510 — the exact set FEAT-6100 owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-6100--aesthetic--biome-transition-compliance-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

This Feature has no player-facing workflow — it is a content-review process capability, not a
runtime behavior. Its "workflow" is a review-pipeline sequence:

**Workflow A — Content review against the standard (extends `09-content-review`'s existing
process, not a new mechanism):**

1. A future `08-content-authoring` package produces new tile/sprite art and/or biome-family
   screen content (consuming [FEAT-4100](FS-103-generated-region-screen-composition.md)'s
   rendering contract).
2. `09-content-review` drives the built ROM in the emulator, screenshots the affected
   screens/states (its existing process, unchanged).
3. `09-content-review` judges the screenshots against **GDS-08 delta §7**'s craft checklist
   (silhouette-first, color budget, outline placement, no anti-aliasing, terrain-variant
   consistency) and **clean-screen rules** (no undefined tiles, no illegal adjacency pairs,
   correct transition-edge neighbors).
4. `09-content-review` separately judges grammar-adjacent biome-family pairs against **GDS-08
   delta §8**'s palette-stepping strategy (do adjacent families' palettes read as
   color-family-related, e.g. blues stepping toward sands, per the worked example ordering).
5. `09-content-review` reports findings exactly as it already does for hand-authored content —
   this Feature adds no new report format, routing mechanism, or ownership change.

## 7. System Behaviour

**Normal path:** every tile/sprite and every rendered screen a content package produces satisfies
every checklist item in GDS-08 delta §7; every grammar-legal adjacent biome-family pair's
palettes read as color-family-related per GDS-08 delta §8 (both Acceptance Criteria, verbatim
from NFR-6500/NFR-6510).

**Edge case — the mechanically-checkable subset (undefined tile indices, illegal seam pairs):**
these can be automated as a `test_rom.py` check (a tilemap scan for undefined indices, an
adjacency-pair table lookup), distinct from the craft/palette-stepping judgment, which remains
`09-content-review`'s human/inspection process (NFR-6500's own Verification Method, verbatim:
"Inspection... / Test (the mechanically-checkable subset)").

**Edge case — NFR-6510 is a "Should," not a "Must":** unlike every other requirement this
increment's Features implement, NFR-6510 is explicitly a design-quality guideline within the
existing 8-palette budget, not a hard functional gate (NFR-6510's own Priority field, verbatim) —
a failed palette-stepping judgment is a review finding routed for improvement, not a build-
blocking defect the way a failed NFR-6500 clean-screen check would be.

**Edge case — a biome-family pair that is grammar-legal (per FR-4310) but whose palettes were
assigned before this standard existed:** not a scenario this increment introduces (no biome-family
palette assignments exist yet, per NFR-6510's own Status field — "No biome-family palette
assignments exist yet to check") — this Feature's review process applies from the first content
package that creates such an assignment onward, not retroactively to anything shipped today.

## 8. Module Responsibilities

Per GDS-03's module decomposition: **none directly** — this Feature is a review-process
capability (`09-content-review`'s existing process, applied against GDS-08 delta §7/§8's
checklist), not a code change. Any future content package (`tiles.py`/`tilemaps.py`) is judged
against this Feature's standard, not modified by it — carried forward verbatim from FEAT-6100's
own Affected Modules field.

## 9. Interfaces Used

None new. This Feature does not introduce a GDS-09 interface — it is a checklist applied within
`09-content-review`'s existing review workflow (`.claude/skills/09-content-review`'s own process,
outside this pipeline stage's normal module-interface scope). The mechanically-checkable subset
(§7) would use `test_rom.py`'s existing tilemap-inspection pattern (the same pattern FS-103's
AC-1 tile-family audit uses), not a new interface.

## 10. Data Model Changes

None. This Feature reads rendered tile/screen data for judgment purposes; it defines no new
WRAM/SRAM/ROM entity and modifies no existing one.

## 11. State Changes

None. This Feature has no runtime state of its own — it operates entirely at build/review time,
outside the game's state machine.

## 12. Error Handling

Not applicable in the runtime-failure-mode sense — a "failure" of this Feature is a review
finding (a screen or palette assignment that doesn't meet the standard), routed back to the
originating content package for revision, exactly as `09-content-review`'s existing process
already handles any other content-quality finding. No new error-handling contract is introduced.

## 13. Performance Considerations

None — this Feature has no runtime performance characteristics of its own; it is a build/review-
time process.

## 14. Integrity Considerations

None beyond what the standard itself (GDS-08 delta §7/§8, already authored) establishes — this
Feature does not introduce a save-data, checksum, or determinism concern.

## 15. Acceptance Criteria

1. Every checklist item in GDS-08 delta §7 passes for every screen a content package produces,
   confirmed by `09-content-review` per its existing review process, extended to apply this
   checklist (NFR-6500).
2. For every grammar-legal adjacent biome-family pair, a reviewer (`09-content-review`) confirms
   their assigned palettes read as color-family-related rather than arbitrary, per GDS-08 delta
   §8's worked example ordering (NFR-6510).

## 16. Verification Plan

Per NFR-6500/NFR-6510's own Verification Methods (Inspection — `09-content-review`'s existing
process, extended to this checklist — / Test for NFR-6500's mechanically-checkable subset):

- **AC-1 (craft/clean-screen, mechanically-checkable subset):** a `test_rom.py` check (landing
  alongside FS-103's tile-family audit, the same T-suite family) scanning every rendered screen's
  tilemap for undefined tile indices and any hardcoded illegal-adjacency-pair table lookup, once
  such a table exists (downstream of FS-103's own Open Question 1 — the biome-family set must be
  fixed before an adjacency-pair table can be written).
- **AC-1 (craft, judgment subset):** `09-content-review`'s existing screenshot-driven inspection
  process, applied against GDS-08 delta §7's checklist — no new automated test, per NFR-6500's
  own Verification Method framing (silhouette-first/color-budget/outline-placement judgment is
  not mechanically checkable).
- **AC-2 (palette-stepping):** `09-content-review`'s inspection process, applied against GDS-08
  delta §8's worked example — a design-quality judgment call, explicitly not mechanically
  checkable (NFR-6510's own Verification Method, verbatim).

## 17. Dependencies

Per FEAT-6100's own Dependencies (carried forward verbatim): **FEAT-4100** (needs biome-family
screen assignments to exist before their palette-stepping can be judged —
[FS-103](FS-103-generated-region-screen-composition.md), already specified); FEAT-6000 (extends
its existing presentation Feature with a written craft standard, already shipped Baseline). This
Feature is the last node on the procgen-world increment's critical path (FEAT-9000 → FEAT-4100 →
**FEAT-6100**, per FP-04) — it cannot be meaningfully exercised until FEAT-4100's actual biome-
family content exists to judge, even though its own standard (GDS-08 delta §7/§8) is already
fully authored today.

## 18. Risks

Carried forward from FEAT-6100's own Risk assessment (Low): no new mechanism, a written standard
applied to an existing review process; NFR-6510 is explicitly a "Should," not a hard gate. This
spec surfaces no additional risk beyond the catalog entry's own assessment.

## 19. Open Questions

None. Unlike FEAT-9000/FEAT-4100, this Feature's standard is already fully authored (GDS-08
delta §7/§8) and its review process already exists (`09-content-review`) — there is no design-
level ambiguity for `06-feature-specification` to surface. The exact adjacency-pair table
needed for AC-1's mechanically-checkable subset depends on FS-103's own Open Question 1 (the
biome-family set), but that dependency is already named there, not a new ambiguity this spec
introduces.

## 20. Related ADRs

ADR-0009 (biome-family adjacency is what NFR-6510 judges the palette-stepping of — carried
forward verbatim from FEAT-6100's own Related ADRs).
