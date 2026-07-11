# FP-05 — Feature Review

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07); re-run 2026-07-10 (procgen-world
> increment delta + `BL-0036` correction; finding #5 resolved, `BL-0037`).** Owned by
> `05-feature-decomposition`. Reviews
> [FP-02](02-epic-catalog.md)–[FP-04](04-feature-dependency-graph.md) for oversized/undersized
> Features, duplicates, missing Features, mis-assigned requirements, and architectural
> inconsistencies. **Recommend only — this document applies no fixes to the other four
> documents** (the correction to FEAT-5100/Release 1's status, `BL-0036`, was applied directly to
> those two documents by this same pass per the user's explicit instruction, not by this review).

## Requirement-assignment check (every FR/NFR owned by exactly one Feature)

**Bootstrap baseline** (unchanged from the 2026-07-07 tally) against
[RQ-01](../requirements/01-functional-requirements.md)/
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

**Procgen-world increment delta** (2026-07-09 RQ-01…04 delta) — 11 new `FR-xxxx` + 6 new
`NFR-xxxx` = 17 requirement IDs:

- FEAT-9000: FR-9100, FR-9110, FR-9120, FR-9130, FR-4310, FR-3220, NFR-2200, NFR-4200 (8)
- FEAT-4100: FR-4300, NFR-1300 (2)
- FEAT-1100: FR-1170, FR-1180, FR-1190 (3)
- FEAT-5300: FR-9200, NFR-5300 (2)
- FEAT-6100: NFR-6500, NFR-6510 (2)

**Total: 36 + 17 = 53.** Every requirement ID appears exactly once across all thirteen lists
(checked by direct cross-reference, no ID repeated, no ID from either the bootstrap baseline or
the 2026-07-09 delta omitted). **Clean — no unassigned or double-assigned requirements.**

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Missing requirement (surfaced here, not fixed here) | (no FR exists) — GDS-08 §2, ADR-0005, ADR-0007, `test_rom.py` T6 | **No numbered functional requirement covers player/collectible sprite (OAM) rendering as an observable behavior**, even though it is shipped, architecturally documented (8×16 OBJ pairs, shadow-OAM DMA), and exercised by `test_rom.py`'s T6 suite. Unchanged since the 2026-07-07 review — still open. | Low–Medium (informational; the behavior is shipped and working, only its formal requirement is missing) | Still routed to `04-requirements-engineering` (`BL-0020`, `SCHEDULED`) for a future delta. Not blocking any current Feature. |
| 2 | Architectural straddle (reviewed and accepted, not a defect) | FEAT-2000 | FEAT-2000 touches both `asm_game.py` and `tilemaps.py` (arrow-tile rendering, FR-2320). | Informational | No action — unchanged from the 2026-07-07 review; confirmed correct on re-review. |
| 3 | **Resolved since the last review** | FEAT-5100 | FEAT-5100's two prior Open Questions (SRAM byte layout; save-compatibility default) are both answered — `FS-101` resolved them, `IP-1010` implemented them, `VR-1010` independently confirmed both (`T11.d`'s synthetic pre-upgrade fixture proves the save-compatibility answer specifically). | — (closed) | No further action. This finding is retained here, marked resolved, rather than deleted — the Feature Catalog's own Open Questions field for FEAT-5100 was updated to "None remaining" in the same pass that corrected `BL-0036`. |
| 4 | **Resolved since the last review** | FEAT-5100 vs. FEAT-7000's `NFR-7100` remediation | Both scheduling options this finding named are now moot — both work items completed the same day (2026-07-07): `IP-1010` (FEAT-5100) and `IP-9010` (`NFR-7100` remediation) both shipped and were independently verified. | — (closed) | No further action. |
| 5 | Stale Risk field — **RESOLVED 2026-07-10** | FEAT-6000, FEAT-7000 (Feature Catalog entries) | **Both Features' own Risk fields in [FP-03](03-feature-catalog.md) still described non-compliances as current** — FEAT-6000's Risk said `NFR-1200` is "confirmed not met"; FEAT-7000's said `NFR-7100` is "confirmed not met at Critical severity." Both are now Met, VERIFIED 2026-07-07 (`IP-9020`/`VR-9020`, `IP-9010`/`VR-9010`) and reconfirmed by `10-integration-review` (2026-07-10). **Resolved:** both Risk fields corrected to Low, citing the VERIFIED status; FEAT-7000's Open Questions field also corrected (its former sequencing question is moot — both items it named landed the same day). | Low (cosmetic at filing) → resolved | No further action — `BL-0037` closed. |
| 6 | Oversized-Feature judgment call (reviewed and accepted, not a defect) | FEAT-9000 | FEAT-9000 (8 requirements: FR-9100/9110/9120/9130/4310/3220, NFR-2200/4200) is the largest Feature in the catalog, tied with FEAT-1000. It deliberately merges two threads — the generation algorithm itself and the item-agnostic collection generalization — because `FR-9130` ("one KeyItem per region") and `FR-3220` ("item-agnostic collection") name each other as dependencies at the requirement level (see [FP-04](04-feature-dependency-graph.md)'s circular-dependency check). Splitting them into two Features would either force an artificial FEAT-level cycle or an arbitrary one-directional cut through a genuinely mutual coupling. | Informational | No action — reviewed and confirmed the right call: cohesion (avoiding a cycle) was correctly prioritized over uniform Feature size. If `06-feature-specification` finds the two threads separable once implementation detail is known, splitting at that stage remains available; not pre-judged here. |

## Oversized / undersized Feature check

**Bootstrap baseline:** unchanged — no Feature approaches a size where splitting or merging would
improve cohesion. **Procgen-world delta:** FEAT-9000 (8 requirements) is addressed by finding #6
above (reviewed and accepted). The other four new Features (FEAT-4100: 2, FEAT-1100: 3,
FEAT-5300: 2, FEAT-6100: 2) are all appropriately small, single-capability Features, consistent
with FEAT-5100's own precedent (1 requirement) for a new, narrowly-scoped addition.

## Duplicate Feature check

None found, including after this delta. Each of the five new Features' Purpose is distinct from
every other Feature (new and bootstrap); no overlap in player-visible or system-level capability.

## Architectural consistency check

Every Feature's Affected Modules list — including the five new Features' — is consistent with
[GDS-03](../architecture/03-architecture.md)'s module decomposition and
[GDS-09](../architecture/09-interface-specification.md)'s interface contracts, including that
delta's new `worldgen.py` module contract (FEAT-9000) and the generalization of
`ALL_SCREENS`/per-zone screen functions to per-biome-family functions (FEAT-4100). No Feature
implies a module boundary violation.

## Circular dependency check

Re-confirmed clean per [FP-04](04-feature-dependency-graph.md)'s own check, including the five
new Features — no cycle exists. The one near-miss at the requirement level (`FR-9130`/`FR-3220`,
finding #6 above) was resolved by Feature-level grouping, not left as an unresolved graph cycle.

## Summary

The Feature Catalog remains complete and internally consistent after this delta: all 53
requirement IDs (36 bootstrap + 17 new) are owned exactly once, no Feature is mis-sized or
duplicated (FEAT-9000's size is a reviewed, accepted cohesion trade-off, not a defect), and no
circular dependency exists at the Feature level. **Two findings closed since the last review**
(FEAT-5100's Open Questions and the FEAT-5100/FEAT-7000 sequencing choice — both resolved by
2026-07-07's implementation work). **One new Low finding** (#5: FEAT-6000/FEAT-7000's own Risk
fields are stale, cosmetic only) is routed to a future light `05-feature-decomposition` touch.
**One prior finding remains open** (#1, the missing sprite-rendering FR, `BL-0020`). No finding
in this review requires revising FP-01–FP-04 before advancing to `06-feature-specification`.
