# FP-01 — Release Plan

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07); delta 2026-07-10 (procgen-world
> increment + `BL-0036` correction); Baseline + Release 1 assessed **GO** 2026-07-10
> ([release-assessment-bootstrap-tranche.md](../reviews/release-assessment-bootstrap-tranche.md));
> delta 2026-07-11 (`ADR-0012` maze-adjacency remediation, `FEAT-9100`/`FEAT-2100` join Release 2
> as an addendum); **Release 2 assessed GO 2026-07-12, user-confirmed**
> ([release-assessment-release-2-bundled.md](../reviews/release-assessment-release-2-bundled.md))
> — **with `FEAT-2100` explicitly carried forward as partially delivered** (logic half shipped
> and `VERIFIED`; rendering half not yet built, tracked as `BL-0075`).** Owned by
> `05-feature-decomposition`. Assigns every Feature
> in [FP-03](03-feature-catalog.md) (now fifteen) to exactly one bucket, using
> [FP-04](04-feature-dependency-graph.md)'s dependency analysis. **Bootstrap framing: seven of
> eight bootstrap-baseline Features are already shipped** (FEAT-5100 shipped and verified
> 2026-07-07, correcting this document's prior "no shipped implementation" framing — `BL-0036`).
> **Release 2** holds the procgen-world increment's five original Features (all shipped and
> `VERIFIED`) plus two 2026-07-11 post-ship remediation Features (`FEAT-9100` shipped/`VERIFIED`;
> `FEAT-2100` partially shipped — see above).

## Bucket: Baseline (as-built)

> **Release-readiness: GO (2026-07-10)** — see
> [release-assessment-bootstrap-tranche.md](../reviews/release-assessment-bootstrap-tranche.md).
> Assessed together with Release 1 below (one tranche, one integration review).

Everything the shipped `BunnyQuest.gbc` ROM already does, as of this pipeline's bootstrap
increment (2026-07-06/07). No scheduling decision was made for these — they are a record of what
exists, not a plan for what to build.

| Feature | Why here |
|---|---|
| FEAT-1000 (Game State Machine & Menu Flow) | Foundational; fully shipped; zero dependencies. |
| FEAT-4000 (Zone & Screen Composition) | Foundational content layer; fully shipped; zero dependencies. |
| FEAT-2000 (Player Movement & Zone Traversal) | Fully shipped; depends only on FEAT-1000/FEAT-4000, both baseline. |
| FEAT-3000 (Collectibles, Scoring & Victory) | Fully shipped; depends only on baseline Features. |
| FEAT-5000 (Save/Load System, as-built) | Fully shipped; depends only on baseline Features. |
| FEAT-6000 (Presentation & HUD) | Fully shipped; depends only on baseline Features. Its one tracked non-compliance (`NFR-1200`, `BL-0003`/`BL-0008`) is **resolved** (`IP-9020` VERIFIED, 2026-07-07). |
| FEAT-7000 (Engine Quality & Build Infrastructure) | Fully shipped (6 of 6 included NFRs now Met). Its prior highest-severity non-compliance (`NFR-7100`, `BL-0006`/`BL-0008`) is **resolved** (`IP-9010` VERIFIED, 2026-07-07) — confirmed again by `10-integration-review`'s bootstrap-tranche pass (2026-07-10). |

## Bucket: Release 1 — Save-System Completion (✅ shipped, VERIFIED 2026-07-07; **GO 2026-07-10**)

| Feature | Why here |
|---|---|
| FEAT-5100 (Per-Zone ScoreItem Persistence) | **Shipped and independently verified 2026-07-07** ([IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md)/[VR-1010](../implementation/verification/VR-1010-per-zone-scoreitem-persistence.md)). Its full dependency chain (FEAT-1000 → FEAT-2000 → FEAT-3000 → FEAT-5000, per FP-04's critical path) was already Baseline, so nothing blocked it. Approved by explicit user decision (2026-07-07, resolving `BL-0018`); the release's own critical path is complete end-to-end. **Correction (`BL-0036`, 2026-07-10):** this row previously read "the only Feature with no shipped implementation" — stale since the same day's implementation; corrected. |

Release 1 is closed — its sole Feature shipped and was independently verified the same day it was
scheduled.

## Bucket: Release 2 — Procedural World & Visual Narrative (✅ shipped; **GO 2026-07-12**)

> **Release-readiness: GO (2026-07-12, user-confirmed)** — see
> [release-assessment-release-2-bundled.md](../reviews/release-assessment-release-2-bundled.md),
> assessed together with the addendum below plus 15 non-Feature remediation packages (post-ship
> navigation/menu fixes, movement/pickup/UI fixes, `IP-9110`/`9120`/`9130`/`9140`) per the user's
> own bundled-scope selection. **One named exception, not silently absorbed into this GO:**
> `FEAT-2100` (addendum, below) shipped only its logic half.

The aesthetics/visual-story-narrative/procgen-world-map increment's five new Features, per its
2026-07-09 RQ-01…04 requirements delta. **All five have shipped and are `VERIFIED`**
(`IP-1020`/`1030`/`1031`/`1040`/`1050`, all five `VERIFIED`, `FEAT-6100`'s content-review
`Clean`) — this bucket's original "None yet implemented" framing is stale and corrected here.

| Feature | Why here |
|---|---|
| FEAT-9000 (Procedural World Generation & Item-Agnostic Collection) | This release's foundational new-work node (per FP-04's critical path) — every other Feature in this bucket depends on it. Depends only on already-shipped Baseline Features (FEAT-1000, FEAT-3000, FEAT-4000), so nothing blocks starting it now. |
| FEAT-4100 (Generated-Region Screen Composition) | Depends on FEAT-9000 (needs a region's biome assignment before it can be rendered) plus already-shipped Baseline Features (FEAT-4000, FEAT-6000). |
| FEAT-1100 (Main Menu & New-Game Flow) | Depends on FEAT-9000 (triggers its generation routine) plus already-shipped Baseline Features (FEAT-1000, FEAT-5000). Independent of FEAT-4100/FEAT-6100 — can proceed in parallel per FP-04. |
| FEAT-5300 (Generated-World Save Persistence) | Depends on FEAT-9000 (persists its output) plus already-shipped Baseline/Release-1 Features (FEAT-5000, FEAT-5100). Independent of FEAT-4100/FEAT-1100/FEAT-6100 — can proceed in parallel per FP-04. |
| FEAT-6100 (Aesthetic & Biome-Transition Compliance) | Depends on FEAT-4100 (needs biome-family screen assignments to judge) plus the already-shipped FEAT-6000. The last node on this release's critical path. |

No Feature in this bucket is scheduled before a Feature it depends on (FEAT-9000 first; the
remaining four in any order or in parallel, per FP-04's parallel-opportunities analysis).

### Release 2 addendum — post-ship remediation (`ADR-0012`, added 2026-07-11)

Two new Features, from a project-owner design request following up on this release's own shipped
navigation fix (`BL-0047`/`IP-9050`) — not part of the original 2026-07-09 requirements delta,
but structurally an extension of this same release's `FEAT-9000` generation routine, so they join
this bucket rather than opening a new one (the fixed bucket vocabulary this stage uses has no
"Release 3" — see this stage's own Step 4). **`FEAT-9100` fully shipped and `VERIFIED`.
`FEAT-2100` partially shipped** — see its own row.

| Feature | Why here |
|---|---|
| FEAT-9100 (Maze-Shaped Region Adjacency) | **Shipped and `VERIFIED`** ([IP-1070](../implementation/packages/IP-1070-maze-shaped-region-adjacency.md)/[VR-1070](../implementation/verification/VR-1070-maze-shaped-region-adjacency.md)). Depended only on the already-shipped `FEAT-9000` (extends its generation routine with a second pass). `ADR-0012`'s algorithm choice (randomized DFS/recursive backtracker) and hardware-cost grounding (`R112`) both held. |
| FEAT-2100 (Maze-Aware Transition-Edge Signaling) | **Partially shipped — logic half only.** [IP-1080](../implementation/packages/IP-1080-maze-aware-edge-classification.md)/[VR-1080](../implementation/verification/VR-1080-maze-aware-edge-classification.md) deliver correct maze-blocked-edge *classification*, `VERIFIED` 2026-07-12. The `GDS-08` tile-art delta this Feature originally named as its blocker (`BL-0068`) has since landed, but **the visual rendering itself — the actual arrow/indicator a player sees — was never implemented**; `VR-1080`'s own audit leaves AC-4 explicitly open. Player-facing symptom (a maze-pruned dead end still looks identical to a true world edge) tracked as `BL-0075`, deliberately kept open, routed `07-implementation-planning` for a follow-on package. Recorded here as a genuine, uncorrected scope gap — not an authorized descope — per the 2026-07-12 Release Assessment's Deviation #1. |

`FEAT-9100` before `FEAT-2100` — the only ordering constraint in this addendum. Both are
independent of the original five Features' own current state (already shipped) and independent
of `BL-0066`'s still-open `NEEDS-USER` conflict (`CR-05`) — that item has no `FEAT-xxxx` row at
all yet, per this stage's own rule against inventing a Feature for an unresolved requirements
conflict.

## Bucket: Future (not yet decomposed into Features)

These are named here for completeness because they're real, tracked program-level concerns — but
neither has a baselined `FR-xxxx` yet, so neither gets a `FEAT-xxxx` row per this stage's own
rule against inventing requirements:

- **MSTR-001 commitment C7** (Zelda/Pokémon-scale world growth) — tied to `CR-03`
  (bank-switching-ready extensibility, RQ-02) and `ADR-0001`'s named future-supersession trigger
  for `NFR-4000` (superseded by `ADR-0011`, which records the future bank-split principle without
  yet implementing it). **Release 2's `FEAT-9000` group is C10, C7's first concrete shape** — a
  user-scalable world (2–9 per axis) generated at new-game time — but true bank-switched
  Zelda/Pokémon-scale growth beyond `WORLD_SCALE`'s 9×9 ceiling remains undecomposed: no FRs yet
  describe what an expanded world must do beyond "be bigger," and doing so needs a
  `03-architecture-design-synthesis` pass to scope the bank-switching architecture before a
  `04-requirements-engineering` delta could derive concrete FRs.
- **`BL-0006`/`BL-0008` (test-suite rewrite)** — **resolved**, no longer a Future-bucket item.
  Both were remediation of `FEAT-7000`'s own `NFR-7100` non-compliance, closed by `IP-9010`
  (VERIFIED 2026-07-07); kept here only as a historical note, since a completed remediation was
  never itself new Feature scope.

## Callouts

- **Highest Value:** FEAT-3000 (Collectibles, Scoring & Victory) — the core loop the entire game
  is built to deliver; every other Feature exists to support reaching this one's win condition.
  **Release 2's highest value:** FEAT-9000 (Procedural World Generation & Item-Agnostic
  Collection) — the increment's foundational new capability; every other Release-2 Feature
  depends on or renders what it generates.
- **Highest Risk:** **Release 2's `FEAT-9000`** (Procedural World Generation & Item-Agnostic
  Collection) — Medium-High risk, a wholly new generation algorithm with no shipped precedent,
  depending on a new verification technique (the reference-generator-oracle pattern, R305)
  working correctly. The bootstrap baseline's prior Highest-Risk item (`FEAT-7000`'s `NFR-7100`
  non-compliance, `BL-0006`/`BL-0008`) is **resolved** (`IP-9010` VERIFIED, 2026-07-07;
  reconfirmed by `10-integration-review`, 2026-07-10) and no longer holds this title.
- **Foundational:** FEAT-1000 and FEAT-4000 (Baseline); **FEAT-9000 (Release 2)** — the
  zero-upstream-Release-2-dependency Feature everything else in Release 2 is built on, mirroring
  FEAT-1000/FEAT-4000's role in Baseline. **Within the 2026-07-11 addendum: `FEAT-9100`** plays
  the same foundational role for `FEAT-2100` that `FEAT-9000` plays for the rest of Release 2.
- **Optional:** None in the current baseline. `NFR-6510` (Release 2, biome-transition
  palette-stepping, part of `FEAT-6100`) is the one **"Should"**-priority requirement in this
  entire plan rather than "Must" — a design-quality guideline, not a hard functional gate; still
  scheduled since it rides the same Feature as `NFR-6500`, not split out. `CR-02`/`CR-03`/`CR-04`
  (RQ-01/RQ-02's remaining Candidate Requirements) remain un-baselined and therefore have no
  Feature row to mark optional. `CR-05` (`BL-0066`, biome-blob clustering — an `ADR-0012`
  pass-ordering conflict, `NEEDS-USER`) joins them, added 2026-07-11.
- **Deferred:** The Future bucket's one remaining item (C7's beyond-`WORLD_SCALE`-9 bank-switched
  growth — the test-suite remediation item is resolved, kept only as a historical note).

## Sequencing note

No Feature is scheduled before a Feature it depends on (verified against
[FP-04](04-feature-dependency-graph.md)): FEAT-5100 (Release 1, shipped) depended only on
FEAT-5000 and FEAT-3000, both Baseline. Release 2's FEAT-9000 depends only on Baseline Features
(FEAT-1000, FEAT-3000, FEAT-4000); FEAT-4100/FEAT-1100/FEAT-5300/FEAT-6100 each depend on FEAT-9000
plus Baseline/Release-1 Features already scheduled or shipped earlier — no ordering violation
anywhere in the plan. **2026-07-11 addendum:** FEAT-9100 depends only on the now-shipped FEAT-9000;
FEAT-2100 depends on FEAT-9100 plus the already-shipped FEAT-2000 — both schedule cleanly after
their dependencies, no violation.
