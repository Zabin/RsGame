# FP-01 — Release Plan

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07).** Owned by `05-feature-decomposition`.
> Assigns every Feature in [FP-03](03-feature-catalog.md) to exactly one bucket, using
> [FP-04](04-feature-dependency-graph.md)'s dependency analysis. **Bootstrap framing: six of seven
> Features are already shipped** — this plan's first bucket exists to give later buckets a
> truthful floor, not to re-plan work already done.

## Bucket: Baseline (as-built)

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
| FEAT-6000 (Presentation & HUD) | Fully shipped; depends only on baseline Features. Carries one tracked non-compliance (`NFR-1200`, `BL-0003`/`BL-0008`) that does not block baseline status — it's a real, tracked gap in an otherwise-shipped Feature, not unshipped scope. |
| FEAT-7000 (Engine Quality & Build Infrastructure) | Substantially shipped (4 of 6 included NFRs Met). Carries the catalog's highest-severity tracked non-compliance (`NFR-7100`, Critical, `BL-0006`/`BL-0008`) — see Highest Risk below. |

## Bucket: Release 1 — Save-System Completion

| Feature | Why here |
|---|---|
| FEAT-5100 (Per-Zone ScoreItem Persistence) | **The only Feature in this catalog with no shipped implementation.** Its full dependency chain (FEAT-1000 → FEAT-2000 → FEAT-3000 → FEAT-5000, per FP-04's critical path) is entirely in the Baseline bucket already, so nothing blocks starting this now. Approved by explicit user decision (2026-07-07, resolving `BL-0018`). Scheduled as its own single-Feature release rather than folded into Baseline, since it is genuinely new work requiring a full `06`→`07`→`08`→`09` pass. |

No other Feature is ready to schedule into Release 1 — every other Feature is already Baseline.

## Bucket: Release 2

*(none — no second wave of new Feature work exists in the current requirements baseline beyond
FEAT-5100. A future requirements delta would populate this bucket.)*

## Bucket: Future (not yet decomposed into Features)

These are named here for completeness because they're real, tracked program-level concerns — but
neither has a baselined `FR-xxxx` yet, so neither gets a `FEAT-xxxx` row per this stage's own
rule against inventing requirements:

- **MSTR-001 commitment C7** (Zelda/Pokémon-scale world growth) — tied to `CR-03`
  (bank-switching-ready extensibility, RQ-02) and `ADR-0001`'s named future-supersession trigger
  for `NFR-4000`. No FRs exist yet describing *what* the expanded world must do beyond "be bigger"
  — decomposing this into Features requires a `03-architecture-design-synthesis` pass to scope the
  bank-switching architecture first, then a `04-requirements-engineering` delta to derive concrete
  FRs, before this stage could responsibly produce Feature rows for it.
- **`BL-0006`/`BL-0008` (test-suite rewrite)** — this is **remediation of FEAT-7000's own
  `NFR-7100` non-compliance**, not new Feature scope; it doesn't get a `FEAT-xxxx` row because it
  adds no new observable game behavior — it repairs verification of behavior already baselined.
  Tracked here only as a pointer; its actual disposition lives in `docs/pipeline/backlog.md` and
  is not re-decided by this stage.

## Callouts

- **Highest Value:** FEAT-3000 (Collectibles, Scoring & Victory) — the core loop the entire game
  is built to deliver; every other Feature exists to support reaching this one's win condition.
- **Highest Risk:** FEAT-7000 (Engine Quality & Build Infrastructure), specifically its
  `NFR-7100` non-compliance (`BL-0006`/`BL-0008`, Critical) — every other Feature's claim to
  "Test"-method verification is currently unsatisfiable until this is remediated. **This is a
  sequencing question for the user/`07-implementation-planning`**: whether to schedule
  `BL-0006`/`BL-0008`'s remediation before, alongside, or after FEAT-5100's new work. Both are
  independent of each other per FP-04's parallel-opportunities analysis — there is no technical
  reason either must go first, only a prioritization choice.
- **Foundational:** FEAT-1000 and FEAT-4000 — the two zero-dependency Features everything else in
  the Baseline bucket is built on.
- **Optional:** None in the current baseline — every Feature is either already shipped or
  (FEAT-5100) explicitly approved. `CR-02`/`CR-03`/`CR-04` (RQ-01/RQ-02's remaining Candidate
  Requirements) remain un-baselined and therefore have no Feature row to mark optional.
- **Deferred:** The Future bucket's two items (C7 world-scale expansion; the test-suite
  remediation isn't "deferred" so much as "not yet scheduled by this stage" — see Highest Risk).

## Sequencing note

No Feature is scheduled before a Feature it depends on (verified against
[FP-04](04-feature-dependency-graph.md)): FEAT-5100 (Release 1) depends only on FEAT-5000 and
FEAT-3000, both Baseline — the ordering constraint is already satisfied trivially.
