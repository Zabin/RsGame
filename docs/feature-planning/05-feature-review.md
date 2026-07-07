# FP-05 — Feature Review

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07).** Owned by `05-feature-decomposition`.
> Reviews [FP-02](02-epic-catalog.md)–[FP-04](04-feature-dependency-graph.md) for oversized/
> undersized Features, duplicates, missing Features, mis-assigned requirements, and architectural
> inconsistencies. **Recommend only — this document applies no fixes to the other four
> documents.**

## Requirement-assignment check (every FR/NFR owned by exactly one Feature)

Direct tally against [RQ-01](../requirements/01-functional-requirements.md)/
[RQ-02](../requirements/02-non-functional-requirements.md)'s 25 `FR-xxxx` + 11 `NFR-xxxx` = 36
requirement IDs:

- FEAT-1000: FR-1100, FR-1110, FR-1120, FR-1130, FR-1140, FR-1150, FR-1160, NFR-2100 (8)
- FEAT-2000: FR-2100, FR-2200, FR-2300, FR-2310, FR-2320 (5)
- FEAT-3000: FR-3100, FR-3200, FR-3210, FR-3300 (4)
- FEAT-4000: FR-4100, FR-4200, NFR-4100 (3)
- FEAT-5000: FR-5100, FR-5200, FR-5210, NFR-5100, NFR-5200 (5)
- FEAT-5100: FR-5220 (1)
- FEAT-6000: FR-6100, FR-6200, FR-6300, NFR-1200 (4)
- FEAT-7000: NFR-1100, NFR-3100, NFR-4000, NFR-6100, NFR-7100, NFR-8100 (6)

**Total: 8+5+4+3+5+1+4+6 = 36.** Every requirement ID appears exactly once across the eight lists
above (checked by direct cross-reference, no ID repeated). **Clean — no unassigned or
double-assigned requirements.**

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Missing requirement (surfaced here, not fixed here) | (no FR exists) — GDS-08 §2, ADR-0005, ADR-0007, `test_rom.py` T6 | **No numbered functional requirement covers player/collectible sprite (OAM) rendering as an observable behavior**, even though it is shipped, architecturally documented (8×16 OBJ pairs, shadow-OAM DMA), and exercised by `test_rom.py`'s T6 suite. FR-2100/FR-2200 cover player *position/facing* updates; FR-3100 covers *collision detection*; none states that the player or Collectibles are rendered as on-screen sprites at all. This is a genuine gap in the RQ-01 baseline, not something this stage may patch by inventing an FR (per this skill's own SHALL-NOT rule: "a gap found here is a Review finding, never a new FR"). | Low–Medium (informational; the behavior is shipped and working, only its formal requirement is missing) | Route to `04-requirements-engineering` for a future delta: a plausible `FR-6400` ("Player and Collectible sprite rendering") under the Presentation grouping, citing GDS-08 §2/ADR-0005/ADR-0007. Not blocking any current Feature — FEAT-2000/FEAT-3000/FEAT-6000 already describe the behaviors that produce sprite output; only the formal requirement statement is absent. |
| 2 | Architectural straddle (reviewed and accepted, not a defect) | FEAT-2000 | FEAT-2000 (Player Movement & Zone Traversal) touches both `asm_game.py` (movement/traversal logic) and `tilemaps.py` (arrow-tile rendering for FR-2320). | Informational | No action — the Feature Catalog entry explicitly justifies this straddle (arrow signaling is a traversal-communication concern, not a screen-composition concern) rather than silently spanning modules. Confirmed as the correct call on review, not a mis-scoped Feature. |
| 3 | Forward-looking design question (not resolved here) | FEAT-5100 | FEAT-5100's two Open Questions (exact SRAM byte layout for the new persisted field; save-compatibility default for pre-upgrade saves) are real, unresolved product/design decisions. | Low (correctly flagged as open, not a defect in this catalog) | Route both explicitly to `06-feature-specification` as required decisions before FEAT-5100's spec can be considered complete — do not let implementation begin with either question implicitly assumed. |
| 4 | Sequencing choice, not a defect | FEAT-5100 vs. FEAT-7000's `NFR-7100` remediation | Both are ready to schedule independently (per FP-04's parallel-opportunities analysis) with no technical ordering constraint between them, but no decision has been made about which goes first. | Informational | This is a legitimate prioritization call for the user/`07-implementation-planning`, not a gap in this catalog — already surfaced in [FP-01](01-release-plan.md)'s Highest-Risk callout. No further catalog action needed. |

## Oversized / undersized Feature check

None found. The seven Features range from 1 requirement (FEAT-5100, appropriately small since
it's a single new capability) to 8 (FEAT-1000, appropriately larger since a six-state machine's
transitions are one cohesive unit that would fragment awkwardly if split further). No Feature
approaches a size where splitting or merging would improve cohesion.

## Duplicate Feature check

None found. Each Feature's Purpose is distinct; no two Features describe overlapping player-visible
or system-level capability.

## Architectural consistency check

Every Feature's Affected Modules list is consistent with [GDS-03](../architecture/03-architecture.md)'s
module decomposition and [GDS-09](../architecture/09-interface-specification.md)'s interface
contracts — no Feature implies a module boundary violation (e.g. no Feature has data-authoring
modules making assembly decisions, or vice versa, per `ADR-0003`).

## Circular dependency check

Re-confirmed clean per [FP-04](04-feature-dependency-graph.md)'s own check — no cycle exists.

## Summary

The Feature Catalog is complete and internally consistent: every requirement is owned exactly
once, no Feature is mis-sized or duplicated, and the one architectural straddle (FEAT-2000) is
justified rather than accidental. **One real gap surfaced** (finding #1, the missing sprite-
rendering FR) — low-to-medium severity, informational, routed to `04-requirements-engineering`
for a future delta rather than blocking this stage's own completion. **Two real open design
questions** (finding #3, FEAT-5100's SRAM layout and save-compatibility default) are correctly
left open for `06-feature-specification` to resolve, not assumed here. No finding in this review
requires revising FP-01–FP-04 before advancing.
