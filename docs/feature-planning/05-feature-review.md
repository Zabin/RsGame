# FP-05 — Feature Review

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07); re-run 2026-07-10 (procgen-world
> increment delta + `BL-0036` correction; finding #5 resolved, `BL-0037`); re-run 2026-07-11
> (`ADR-0012` maze-adjacency remediation delta — see finding #7); re-run 2026-07-13
> (edge-indicator legend screen delta, `FEAT-1200` — see finding #8).** Owned by
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

**`ADR-0012` maze-adjacency delta** (2026-07-11 RQ-01 delta) — 3 new `FR-xxxx` = 3 requirement IDs:

- FEAT-9100: FR-9140, FR-9150 (2)
- FEAT-2100: FR-2330 (1)

**Total: 53 + 3 = 56.** Both new Features' requirements checked against every existing list above
— no overlap, no ID reused. **Clean — no unassigned or double-assigned requirements.** (`CR-05`
is explicitly not in this tally — it is a Candidate, not baselined, per RQ-01/RQ-03's own
disposition; this stage correctly does not force it into a Feature row.)

**Edge-indicator legend screen delta** (2026-07-13 RQ-01 delta) — 2 new `FR-xxxx` = 2 requirement
IDs:

- FEAT-1200: FR-1200, FR-1210 (2)

**Total: 56 + 2 = 58.** Checked against every existing list above — no overlap, no ID reused.
**Clean — no unassigned or double-assigned requirements.** (`FR-9160`/`FR-9161`, baselined
2026-07-12 for `ADR-0015`'s win-condition redesign, remain outside this tally — they supersede
`FR-9130`/`FR-3300` in place within the already-catalogued `FEAT-9000`, not a new Feature this
stage needed to add a row for; a pre-existing gap in this tally's own bookkeeping, not introduced
by this delta, noted here rather than silently carried forward unremarked.)

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Missing requirement (surfaced here, not fixed here) | (no FR exists) — GDS-08 §2, ADR-0005, ADR-0007, `test_rom.py` T6 | **No numbered functional requirement covers player/collectible sprite (OAM) rendering as an observable behavior**, even though it is shipped, architecturally documented (8×16 OBJ pairs, shadow-OAM DMA), and exercised by `test_rom.py`'s T6 suite. Unchanged since the 2026-07-07 review — still open. | Low–Medium (informational; the behavior is shipped and working, only its formal requirement is missing) | Still routed to `04-requirements-engineering` (`BL-0020`, `SCHEDULED`) for a future delta. Not blocking any current Feature. |
| 2 | Architectural straddle (reviewed and accepted, not a defect) | FEAT-2000 | FEAT-2000 touches both `asm_game.py` and `tilemaps.py` (arrow-tile rendering, FR-2320). | Informational | No action — unchanged from the 2026-07-07 review; confirmed correct on re-review. |
| 3 | **Resolved since the last review** | FEAT-5100 | FEAT-5100's two prior Open Questions (SRAM byte layout; save-compatibility default) are both answered — `FS-101` resolved them, `IP-1010` implemented them, `VR-1010` independently confirmed both (`T11.d`'s synthetic pre-upgrade fixture proves the save-compatibility answer specifically). | — (closed) | No further action. This finding is retained here, marked resolved, rather than deleted — the Feature Catalog's own Open Questions field for FEAT-5100 was updated to "None remaining" in the same pass that corrected `BL-0036`. |
| 4 | **Resolved since the last review** | FEAT-5100 vs. FEAT-7000's `NFR-7100` remediation | Both scheduling options this finding named are now moot — both work items completed the same day (2026-07-07): `IP-1010` (FEAT-5100) and `IP-9010` (`NFR-7100` remediation) both shipped and were independently verified. | — (closed) | No further action. |
| 5 | Stale Risk field — **RESOLVED 2026-07-10** | FEAT-6000, FEAT-7000 (Feature Catalog entries) | **Both Features' own Risk fields in [FP-03](03-feature-catalog.md) still described non-compliances as current** — FEAT-6000's Risk said `NFR-1200` is "confirmed not met"; FEAT-7000's said `NFR-7100` is "confirmed not met at Critical severity." Both are now Met, VERIFIED 2026-07-07 (`IP-9020`/`VR-9020`, `IP-9010`/`VR-9010`) and reconfirmed by `10-integration-review` (2026-07-10). **Resolved:** both Risk fields corrected to Low, citing the VERIFIED status; FEAT-7000's Open Questions field also corrected (its former sequencing question is moot — both items it named landed the same day). | Low (cosmetic at filing) → resolved | No further action — `BL-0037` closed. |
| 6 | Oversized-Feature judgment call (reviewed and accepted, not a defect) | FEAT-9000 | FEAT-9000 (8 requirements: FR-9100/9110/9120/9130/4310/3220, NFR-2200/4200) is the largest Feature in the catalog, tied with FEAT-1000. It deliberately merges two threads — the generation algorithm itself and the item-agnostic collection generalization — because `FR-9130` ("one KeyItem per region") and `FR-3220` ("item-agnostic collection") name each other as dependencies at the requirement level (see [FP-04](04-feature-dependency-graph.md)'s circular-dependency check). Splitting them into two Features would either force an artificial FEAT-level cycle or an arbitrary one-directional cut through a genuinely mutual coupling. | Informational | No action — reviewed and confirmed the right call: cohesion (avoiding a cycle) was correctly prioritized over uniform Feature size. If `06-feature-specification` finds the two threads separable once implementation detail is known, splitting at that stage remains available; not pre-judged here. |
| 7 | Missing dependency artifact — **RESOLVED 2026-07-11** | FEAT-2100, GDS-08 | **`FEAT-2100` (maze-aware transition-edge signaling) cannot be fully specified past its logic half** — its own blocked-edge indicator's tile art/palette assignment has no `GDS-08` (presentation architecture) delta authored yet, and this stage correctly does not originate one (out of `05-feature-decomposition`'s own scope, per its SHALL-NOT-redesign-architecture rule — the same rule `04-requirements-engineering` invoked for `CR-05`/`BL-0066` one stage upstream). `FEAT-2100`'s own catalog entry already names this as an Open Question, not silently assumed resolved. **Resolved:** `GDS-08` §10 landed 2026-07-11 (`BL-0068`), `FEAT-2100`'s rendering half fully specified and its content half shipped/`VERIFIED` (`IP-1081`); only the render branch (`IP-1082`) remains unimplemented, a `07`/`08` question, not a `05`-stage gap anymore. | Low-Medium (a real, named blocker on full specification — not a defect in what's cataloged, since the logic half is fully specifiable independent of the art question) | Routed to `03-architecture-design-synthesis` for a `GDS-08` delta (blocked-edge indicator tile art). `06-feature-specification` can still specify `FEAT-2100`'s logic half (the grid-arithmetic re-derivation `FR-2330` describes) independently, per that Feature's own Suggested Verification Strategy, without waiting on the art decision — not a hard block on all downstream work, only on the rendering half's full spec. |
| 8 | 05-delta review (`FEAT-1200` added) | FEAT-1200, FEAT-1000, FEAT-1100, FEAT-2100 | Reviewed the new Feature against the catalog's own consistency rules. **Cohesion/coupling:** `FEAT-1200` cleanly separates from `FEAT-1000` (extends its state set, doesn't modify its existing states' behavior) and from `FEAT-2100` (displays its tiles, doesn't redefine their meaning or render-time classification) — no straddle, no artificial split needed. **Dependency correctness:** cross-checked against [FP-04](04-feature-dependency-graph.md) — `FEAT-1200`'s three dependencies (`FEAT-1000`, `FEAT-1100`, `FEAT-2100`) are correctly a *content* dependency on `FEAT-2100` (its already-shipped tiles), not a *build-order* dependency on `FEAT-2100`'s own still-in-flight render branch — confirmed by direct re-read of `IP-1081`'s `VERIFIED` status (tiles shipped) versus `IP-1082`'s `COMPLETE`-pending-verification status (render branch, unrelated to what `FEAT-1200` needs). **Requirement assignment:** `FR-1200`/`FR-1210` assigned to `FEAT-1200` only, confirmed not double-assigned anywhere else in the catalog. **Bucket placement:** joins Release 2 as a second, independent addendum (this stage's own established "no Release 3" convention, per the `ADR-0012` addendum's own precedent) — reviewed and confirmed not a forced fit, since `FEAT-1200` genuinely has no dependency on the `ADR-0012` remediation thread it shares a bucket with. | — (clean check, no new defect; one new Feature added, correctly scoped and placed) | None — this finding records that the delta was reviewed and found internally consistent, per this stage's own Step-5 discipline (a zero-finding pass is a signal to re-check, not proof of quality — this re-check found the addition clean). |

## Oversized / undersized Feature check

**Bootstrap baseline:** unchanged — no Feature approaches a size where splitting or merging would
improve cohesion. **Procgen-world delta:** FEAT-9000 (8 requirements) is addressed by finding #6
above (reviewed and accepted). The other four new Features (FEAT-4100: 2, FEAT-1100: 3,
FEAT-5300: 2, FEAT-6100: 2) are all appropriately small, single-capability Features, consistent
with FEAT-5100's own precedent (1 requirement) for a new, narrowly-scoped addition.
**`ADR-0012` delta (2026-07-11):** FEAT-9100 (2 requirements) and FEAT-2100 (1 requirement) are
both appropriately small — FEAT-9100's 2-requirement size mirrors FEAT-4100/FEAT-5300/FEAT-6100's
own established precedent for a focused, single-capability extension; FEAT-2100's 1-requirement
size mirrors FEAT-5100's own precedent exactly.

## Duplicate Feature check

None found, including after this delta. Each of the five new Features' Purpose is distinct from
every other Feature (new and bootstrap); no overlap in player-visible or system-level capability.
**`ADR-0012` delta:** FEAT-9100/FEAT-2100 checked against all fifteen other Features — neither
overlaps `FEAT-9000` (generation vs. adjacency-shaping) nor `FEAT-2000` (base traversal/signaling
vs. maze-aware signaling extension); both are genuinely new capability, not restatements.

## Architectural consistency check

Every Feature's Affected Modules list — including the five new Features' — is consistent with
[GDS-03](../architecture/03-architecture.md)'s module decomposition and
[GDS-09](../architecture/09-interface-specification.md)'s interface contracts, including that
delta's new `worldgen.py` module contract (FEAT-9000) and the generalization of
`ALL_SCREENS`/per-zone screen functions to per-biome-family functions (FEAT-4100). No Feature
implies a module boundary violation. **`ADR-0012` delta:** FEAT-9100's Affected Modules
(`worldgen.py`, `asm_game.py`) match `ADR-0012` point 1 exactly (a second pass within the same two
modules `FEAT-9000` already touches, not a new module); FEAT-2100's (`asm_game.py`, `tiles.py`/
`tilemaps.py`) match `FEAT-2000`'s own precedent for the identical straddle (finding #2 above) —
consistent, not a new pattern.

## Circular dependency check

Re-confirmed clean per [FP-04](04-feature-dependency-graph.md)'s own check, including the five
new Features — no cycle exists. **`ADR-0012` delta:** re-confirmed clean again with
`FEAT-9100`/`FEAT-2100` added — both sit at the end of existing chains (`FEAT-9000` → `FEAT-9100`
→ `FEAT-2100`, with `FEAT-2100` also depending on the already-terminal `FEAT-2000`), introducing
no new back-edge. The one near-miss at the requirement level (`FR-9130`/`FR-3220`,
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

**2026-07-11 `ADR-0012` delta review:** the Feature Catalog remains complete and internally
consistent after adding `FEAT-9100`/`FEAT-2100` — all 56 requirement IDs (53 prior + 3 new) are
owned exactly once, neither new Feature is mis-sized or duplicated, and no circular dependency
exists. **One new Low-Medium finding** (#7: `FEAT-2100`'s tile art needs a `GDS-08` delta not yet
authored) is a real, correctly-surfaced blocker on that Feature's *rendering* half only — its
logic half and `FEAT-9100` entirely are unblocked. `CR-05`/`BL-0066` correctly received no Feature
row (no baselined FR exists for it yet) — this stage did not invent one to fill the gap. No
finding in this delta requires revising FP-01–FP-04 before advancing to `06-feature-specification`
on `FEAT-9100`/`FEAT-2100`'s unblocked portions.
