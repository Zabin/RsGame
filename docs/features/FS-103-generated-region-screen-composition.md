# FS-103 — Generated-Region Screen Composition

> Feature Specification for [FEAT-4100](../feature-planning/03-feature-catalog.md#feat-4100--generated-region-screen-composition-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-4100, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Forward reference (metadata only):** [IP-1030](../implementation/packages/IP-1030-generated-region-screen-composition-code.md)
> (code) **VERIFIED 2026-07-10** ([VR-1030](../implementation/verification/VR-1030-generated-region-screen-composition-code.md))
> — AC-1/AC-2 confirmed via T13.a/T13.b, 180/180 full suite green, ROM byte-identical.
> [IP-1031](../implementation/packages/IP-1031-generated-region-screen-composition-content.md)
> (content) **implemented 2026-07-11** — registers the 5 biome-family screen mapping
> (Water→`lake_screen`, Sand→`beach_screen`, Grass→`forest_screen`, Stone→`mountain_screen`,
> Brick→`castle_screen`) IP-1030's own `ALL_SCREENS` shape already carried; independent
> verification pending `09-package-verification`. Jointly with IP-1030, this document's Open
> Questions 1–2 are now both resolved (IP-1030 resolved the code-side implementation-detail
> portion; IP-1031 resolves the content-sizing/registration portion).
>
> **Revision (2026-07-16, `FR-4320`/`BL-0128`):** the biome-family set this Feature dispatches
> screens for widens from 5 to 9 identities (Village/Cave/Desert/Plains folded in). **Reopens
> Open Question 1 for the 4 new identities only, but finds it nearly free to close**: their
> screen-generator functions (`village_screen`/`cave_screen`/`desert_screen`/`plains_screen`) and
> their tile-index budgets (`0x90`–`0x95`/`0x98`–`0x9D`/`0xA0`–`0xA5`/`0xA8`–`0xAC`, confirmed by
> direct read of `tiles.py`) were never removed when `IP-1030`/`IP-1031` narrowed `ALL_SCREENS`'
> own dispatch to 5 — both are already fully authored and already emitted into the ROM by
> `build_tile_data()`. What remains is a dispatch-table rewire (§9), not new content authoring —
> see §5/§19 below. §5, §6, §7, §10, §19 updated.

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-103` — expands `FEAT-4100` (Generated-Region Screen Composition), Epic `EP-5000` (World
Generation & Visual Narrative).

## 2. Title

Generated-Region Screen Composition

## 3. Purpose

Render each generated region's screen from exactly one biome family's tile set, within the
existing transition-smoothness budget. Carried forward verbatim from FEAT-4100's own Purpose
(High User Value — the player's entire visual experience of the generated world).

## 4. Scope

**In scope:** the rendering constraint that a region's screen is composed entirely from its
assigned biome family's tiles (never a blend of two); the transition-timing bar that a
generated-region transition must meet, using the existing mechanism unchanged.

**Out of scope** (per FEAT-4100's own Excluded Requirements, carried forward verbatim): *which*
biome a region is assigned — [FEAT-9000](FS-102-procedural-world-generation.md) owns generation
output, this Feature only consumes it; grammar-valid adjacency itself (FR-4310) —
FEAT-9000's own scope, per ADR-0009's framing that adjacency legality is a generation-time
construction guarantee, not a rendering concern; the biome-family palette-stepping *aesthetic
quality* judgment — FEAT-6100 (Aesthetic & Biome-Transition Compliance, not yet specified) owns
judging this Feature's output, this Feature owns only the hard structural constraint.

## 5. Requirements Implemented

FR-4300, NFR-1300 — the exact set FEAT-4100 owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-4100--generated-region-screen-composition-new--not-yet-implemented)'s
Included Requirements). **(2026-07-16 delta) FR-4320** (nine biome-family identities) is this
Feature's natural owner — its own count/identity/palette-mapping requirement is fundamentally
about *which and how many* screens this Feature dispatches, the same territory `FR-4300` already
covers — but, mirroring `FS-102` §19 Open Question 4's own already-established precedent for
`FR-9160`/`FR-9161`/`FR-9170`, `FEAT-4100`'s own catalog Included Requirements list (`FR-4300;
NFR-1300`, confirmed by direct read) does not yet name `FR-4320`. Not blocking this Feature's own
implementation-readiness — flagged as Open Question 3 below for `05-feature-decomposition` to
reconcile.

## 6. User Workflows

**Workflow A — Entering a generated region (screen rendering):**

1. Player crosses a region boundary via a legal transition (the existing zone-boundary-crossing
   mechanic, FR-2300, unchanged — this Feature does not alter *when* a transition fires, only
   *what* gets rendered once it does).
2. The system looks up the destination region's assigned biome family (FEAT-9000's generation
   output).
3. The system renders that region's screen using the biome family's screen-generator function —
   structurally the same authoring pattern every existing zone screen already uses (GDS-08 §1: a
   base terrain fill via `_fill()`, then hand-placed/generated landmark elements), parameterized
   by biome family rather than by a fixed per-zone identity. **(2026-07-16 delta, `FR-4320`):**
   the biome-family set this step dispatches over is nine identities, not five —
   `lake_screen`/`beach_screen`/`forest_screen`/`mountain_screen`/`castle_screen` (the current
   dispatch set) plus `village_screen`/`cave_screen`/`desert_screen`/`plains_screen` (already
   authored, currently orphaned — `tilemaps.py`'s own header comment).
4. The render uses the existing `copy_screen`/`do_screen_redraw` LCD-off mechanism, unchanged —
   no new "safe window" convention is introduced (this Feature's own NFR-1300).

## 7. System Behaviour

**Normal path:** for every generated region, its rendered screen's tile content is drawn from
exactly one biome family — confirmed by a tile-family audit of the screen's composed tilemap
(FR-4300's own Acceptance Criteria, verbatim).

**Edge case — a region whose biome family has no dedicated screen-generator function yet
authored:** out of this Feature's own scope to resolve — this Feature's behavior contract assumes
every biome family FEAT-9000 can assign has a corresponding rendering function; whether every
possible biome family is actually content-authored is a content-package concern (see Open
Questions). **(2026-07-16 delta, `FR-4320`):** for the screen-*rendering* half specifically, this
edge case is now moot for all nine identities `FR-4320` names — every one already has an authored
screen-generator function (confirmed by direct read of `tilemaps.py`, see header revision note
above). It is **not** moot for the paired collectible-*content* half (`ZONE_COLLECTS`) — four of
the nine identities have no spawn table today, a distinct gap this Feature's own Scope (§4)
explicitly excludes (collectible placement is `FEAT-9000`/`FS-102`'s scope) — see `FS-102` §19
Open Question 6 for that half.

**Edge case — the row-0 HUD reservation:** unchanged — every existing zone screen reserves row 0
for the HUD (GDS-08 §1/§3); a generated region's screen follows the identical convention, since
this Feature reuses the existing per-screen authoring pattern rather than introducing a new one.

**Edge case — transition timing under the maximum region count (scale 9, 81 regions):** the
transition mechanism itself is unchanged from the shipped 9-zone case — NFR-1300's Acceptance
Criteria requires the *same* `copy_screen` routine and LCD-off bracket with no additional
per-frame cost, regardless of how many total regions exist in the generated world (region *count*
affects how many distinct screen-generator functions might exist, not the cost of rendering any
one of them).

## 8. Module Responsibilities

Per GDS-03's module decomposition and GDS-09's delta:

- **`tilemaps.py`** — the biome-family screen-generator functions themselves (one `fn()` per
  biome family, generalizing today's one-`fn()`-per-fixed-zone shape, per GDS-09's delta); the
  `ALL_SCREENS`-equivalent iteration source `build_rom.py` consumes to lay out each region's
  actual tilemap/attribute data at build/generation time.
- **`tiles.py`** — the biome-family terrain tile sets a screen-generator function draws from
  (content-authoring scope for whichever `08-content-authoring` package implements this Feature,
  not this Feature's own design-time concern beyond naming the module).
- **`asm_game.py`** — unchanged: `copy_screen`/`do_screen_redraw` (the existing LCD-off transition
  mechanism this Feature reuses without modification).

No module outside this set is touched.

## 9. Interfaces Used

- **`ALL_SCREENS`'s existing per-`(name, fn)` contract, extended** (GDS-09 delta, cited
  verbatim): "one `fn()` per biome *family*... consistent with GDS-08's delta (biome families,
  not per-region unique art). Contract unchanged: each `fn() -> (tiles, attrs)` still returns the
  same two-buffer shape; only the caller's iteration source changes." This Feature is the
  consumer of that extended contract — it does not redefine the contract shape itself.
- **The existing `copy_screen`/`do_screen_redraw` mechanism** (unchanged, per ADR-0009 point 5:
  "Generation runs under the same LCD-off bracket `do_screen_redraw` already uses... no new safe
  window convention") — this Feature's transitions use this mechanism exactly as every existing
  zone transition does.
- **FEAT-9000's generation output** (a region's biome-family assignment) — consumed as an input,
  not a contract this Feature defines.

## 10. Data Model Changes

None beyond what FEAT-9000 already introduces (`Region`'s biome-identity field, GDS-04's delta) —
this Feature reads that field to select a rendering function; it adds no new WRAM/SRAM/ROM
entity of its own. The tile-index-map budget consumed by biome-family tile sets is a content-
authoring concern (GDS-07 §8's cross-reference / GDS-08 §9), not a new data-model entity this
Feature's design introduces. **(2026-07-16 delta, `FR-4320`):** the four newly-dispatched
identities' tile-index budgets already exist and require no new allocation — `village_screen`
(`0x90`–`0x95`), `cave_screen` (`0x98`–`0x9D`), `desert_screen` (`0xA0`–`0xA5`), `plains_screen`
(`0xA8`–`0xAC`), all confirmed 8-tile-aligned per the existing convention, all already emitted by
`build_tile_data()`. Palette assignment likewise introduces no new BG palette slot — `FR-4320`
reuses the original nine-zone game's own established grouping (`village_screen`/`cave_screen`
share palette 4 with `mountain_screen`; `desert_screen` shares palette 1 with `beach_screen`;
`plains_screen` shares palette 0 with `forest_screen`), confirmed against `07-data-model.md` §5's
own palette-reuse table.

## 11. State Changes

None beyond the existing zone-transition state changes (`CUR_ZONE`/`Region`-equivalent update,
already FEAT-2000's/FEAT-9000's scope) — this Feature is purely a rendering response to a
transition already occurring, not a state-machine participant of its own.

## 12. Error Handling

- **A region assigned a biome family with no authored screen-generator function:** not a runtime
  failure mode this Feature's own design handles — per Open Questions below, this is a
  content-completeness precondition this Feature's behavior contract assumes holds, not a defect
  path it recovers from.
- **Tile-index collision between two biome families' tile sets:** out of this Feature's scope to
  prevent at runtime — GDS-07 §8/GDS-08 §9's existing tile-index-budget convention (8-tile-aligned
  blocks) is the structural mechanism that prevents this, unchanged by this Feature; this
  Feature's own Acceptance Criteria (the tile-family audit) is the check that would catch a
  violation, not a runtime guard.

## 13. Performance Considerations

- **NFR-1300** (transition smoothness, cited verbatim): "A generated-region screen transition
  shall complete within the same LCD-off redraw budget existing transitions already use... with
  no new, slower transition path introduced for generated content." This Feature's entire
  performance contract is this single constraint — reuse, not re-optimize.
- **World generation itself (FEAT-9000) is explicitly out of scope for this NFR's in-session
  smoothness bar** (NFR-1300's own Notes field, cited verbatim: generation "happens once, at
  new-game creation — not per-transition") — this Feature's timing bar applies only to the
  repeated, in-session act of entering a region, not the one-time generation event.

## 14. Integrity Considerations

None beyond what the existing `copy_screen`/`do_screen_redraw` mechanism already guarantees
(unchanged) — this Feature introduces no new save-data, checksum, or determinism concern of its
own; determinism of *which* biome a region gets is FEAT-9000's concern (NFR-2200), not this
Feature's.

## 15. Acceptance Criteria

1. For every generated region, its screen's tile-family composition contains no tile from any
   biome family other than its assigned one (FR-4300).
2. A generated-region transition's tilemap/attribute write uses the same `copy_screen` routine
   and LCD-off bracket as every existing zone transition, with no additional per-frame cost
   beyond that routine's existing, already-budgeted 1152-byte copy (NFR-1300).

## 16. Verification Plan

Per FR-4300's own Verification Method (Test — tile-family audit per screen — / Inspection) and
NFR-1300's (Inspection — call-site audit — / Test), landing alongside FS-102's proposed **T12:
World Generation** suite (or a dedicated sibling suite, an implementation-time sizing decision
per the right-sizing convention, not fixed here):

- **Tile-family audit (AC-1):** for every region in a multi-seed/multi-scale test corpus
  (following R305's extension, the same corpus FS-102's T12 suite establishes), read the rendered
  screen's tilemap and confirm every tile index falls within its assigned biome family's known
  tile-index range (GDS-07 §8/GDS-08 §9's 8-tile-aligned block convention) — a property test,
  not a single-screen spot check.
- **Transition call-site audit (AC-2):** Inspection — direct code read confirming the
  generated-region transition path calls the same `copy_screen`/`do_screen_redraw` routine every
  existing zone transition uses, with no new call site introduced; this mirrors `VR-9020`'s own
  sweep methodology exactly (confirm no additional/alternate write path exists), applied here at
  design-verification time rather than post-implementation audit time.

## 17. Dependencies

Per FEAT-4100's own Dependencies (carried forward verbatim): **FEAT-9000** (needs a region's
biome assignment to exist before it can be rendered — [FS-102](FS-102-procedural-world-generation.md),
already specified); FEAT-4000 (extends its zone/screen composition existence layer, already
shipped Baseline); FEAT-6000 (reuses the existing terrain-fill-plus-landmarks rendering pattern,
already shipped Baseline). This Feature is the second node on the procgen-world increment's
critical path (FEAT-9000 → **FEAT-4100** → FEAT-6100, per FP-04).

## 18. Risks

Carried forward from FEAT-4100's own Risk assessment (Low): reuses the existing, already-verified
LCD-off transition mechanism unchanged; the new constraint (one biome per screen) is enforced by
which tiles a screen generator uses, not new hardware-timing-sensitive code. The only risk this
spec surfaces beyond the catalog entry's own assessment is content-completeness (Open Question 1
below) — not a design or architecture risk. **(2026-07-16 delta, `FR-4320`):** the nine-identity
expansion's own risk is lower still than the original five-identity case — no new tile art, no
new palette slot, no new tile-index allocation is needed for the screen-rendering half (§10), so
implementation risk is confined to a dispatch-table rewire plus the separately-tracked
collectible-content gap (`FS-102` §19 Open Question 6), not new rendering-mechanism work.

## 19. Open Questions

1. **Whether every biome family FEAT-9000's generator can assign has a corresponding authored
   screen-generator function is a content-completeness question, not resolved by this design
   spec.** GDS-08 §8 explicitly defers "exact biome-family count and palette assignment for a
   specific `WorldScale`... to the implementation package that sizes it" — meaning the actual set
   of biome families this Feature must have rendering functions for is not yet fixed by any
   upstream artifact (the same open question FS-102 §19 Open Question 1 names for the adjacency
   grammar table — these are two views of the same underlying deferral). Resolves at:
   `07-implementation-planning`, in lockstep with FS-102's Open Question 1 (the grammar table and
   the biome-family set should be sized together, since the grammar table is defined *over*
   whatever biome-family set is chosen). **(2026-07-16 delta, `FR-4320`/`BL-0128`) — RESOLVED for
   the screen-rendering half.** `FR-4320` fixes the biome-family set at nine identities by name,
   and all nine already have authored screen-generator functions (confirmed by direct read of
   `tilemaps.py` — see header revision note). What remains for `07-implementation-planning` is a
   mechanical dispatch-table rewire (`ALL_SCREENS`/`REGION_GRAPH` biome-id range), not new content
   authoring. **Not resolved for the paired collectible-content half** — see `FS-102` §19 Open
   Question 6.
2. **The exact tile-index ranges/palette assignments for whatever biome-family set is eventually
   chosen** are, per GDS-07 §8/GDS-08 §9's own cross-references, deferred to the same future
   content-sizing package — this spec does not invent tile-index ranges beyond citing the
   existing 8-tile-aligned-block *convention* GDS-07/GDS-08 already establish. Resolves at:
   `07-implementation-planning`/`08-content-authoring`, once Open Question 1 is resolved.
   **(2026-07-16 delta, `FR-4320`/`BL-0128`) — RESOLVED.** Both the tile-index ranges and the
   palette-group assignments for all four newly-dispatched identities already exist (§10 above) —
   no new allocation of either kind is needed; `07-implementation-planning` only needs to point
   the dispatch table at what already exists.
3. **(New, 2026-07-16, `FR-4320`/`BL-0128`) `FEAT-4100`'s own catalog Included Requirements list
   does not yet name `FR-4320`**, mirroring the exact gap class `FS-102` §19 Open Question 4
   already established for `FR-9160`/`FR-9161`/`FR-9170`. Not blocking this Feature's own
   implementation-readiness. Resolves at: `05-feature-decomposition`, whenever it next touches
   `FEAT-4100`'s own catalog entry.

## 20. Related ADRs

ADR-0009 (per-biome terrain texture continues the existing `_fill()` pattern — this ADR decides
adjacency/placement, not texture, per its own framing — the framing this Feature's Scope section
relies on to exclude FR-4310).
