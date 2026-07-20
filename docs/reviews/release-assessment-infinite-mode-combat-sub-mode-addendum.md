# Release Assessment — Infinite Mode Combat Sub-Mode (Release 2, fourth addendum)

## Release

- **Bucket:** Release 2 — fourth addendum (`FEAT-11000`, Infinite Mode Combat Sub-Mode), per
  `01-release-plan.md` (moved from `Future` 2026-07-20, `BL-0166`).
- **Date:** 2026-07-20.
- **Commit reviewed:** `cb8b2ad` (tree head at assessment time — no source changes since
  `IP-1127`'s own `a8117d7`; the two `05-feature-decomposition`/`10-integration-review` commits
  since then touched planning docs only).

## Scope audit

`FEAT-11000`'s Included Requirements (`03-feature-catalog.md`): 10 FRs + 2 NFRs = 12
requirements, all owned exclusively by this Feature.

| Requirement | Package(s) | VR | Delivered |
|---|---|---|---|
| FR-11100 (mode gating & UI) | IP-1120 | [VR-1120](../implementation/verification/VR-1120-infinite-mode-combat-mode-gating.md) | ✅ VERIFIED |
| FR-11200 (mob materialization, rendering, defeat) | IP-1121 | [VR-1121](../implementation/verification/VR-1121-infinite-mode-combat-mob-materialization-and-rendering.md) | ✅ VERIFIED |
| FR-11210 (mob movement toward the player) | IP-1126 | [VR-1126](../implementation/verification/VR-1126-infinite-mode-combat-mob-movement.md) | ✅ VERIFIED |
| FR-11300 (weapon fire & hit resolution) | IP-1122 | [VR-1122](../implementation/verification/VR-1122-infinite-mode-combat-weapon-fire-and-hit-resolution.md) | ✅ VERIFIED |
| FR-11310 (8-directional weapon fire) | IP-1128 | [VR-1128](../implementation/verification/VR-1128-infinite-mode-combat-weapon-directionality.md) | ✅ VERIFIED |
| FR-11400 (player health, setback) | IP-1123 | [VR-1123 Pass 2](../implementation/verification/VR-1123-infinite-mode-combat-player-health-and-economy-pass2.md) | ✅ VERIFIED |
| FR-11410 (post-contact protection: invincibility/knockback/cooldown) | IP-1127 | [VR-1127](../implementation/verification/VR-1127-infinite-mode-combat-post-contact-protection.md) | ✅ VERIFIED |
| FR-11500 (treasure-spent healing economy) | IP-1123 | VR-1123 Pass 2 | ⚠️ VERIFIED (logic), **no player-reachable input binding** — see Deviations |
| FR-11510 (treasure-spent weapon-tier funding) | IP-1129 | [VR-1129](../implementation/verification/VR-1129-infinite-mode-combat-weapon-tier-funding.md) | ⚠️ VERIFIED (logic), **no player-reachable input binding** — see Deviations |
| FR-11600 (combat state save persistence) | IP-1124 | [VR-1124](../implementation/verification/VR-1124-infinite-mode-combat-save-persistence.md) | ✅ VERIFIED |
| NFR-1500 (combat per-frame cycle budget) | — (cross-cutting) | — | ❌ **UNCONFIRMED — never measured** — see Deviations |
| NFR-4500 (combat ROM/OAM budget) | IP-1120–IP-1129 (cumulative) | all above | ✅ Met by direct, repeated measurement (32768 bytes every build; `T29.f` static OAM audit) |

**Sprite content** (mob/projectile art, not FR-owned but part of the delivered scope): IP-1125 →
[VR-1125](../implementation/verification/VR-1125-combat-sprite-content.md) `VERIFIED`, and
independently [content-reviewed](../reviews/content-review-ip-1125-combat-sprites.md) clean (one
Low finding, `BL-0150`, already tracked, non-blocking).

**Package inventory:** all ten packages in the delta (`IP-1120`–`IP-1129`) are `VERIFIED` on the
Master Build Plan. No Feature in this bucket was silently dropped, split, or descoped since
planning — the ten-package shape matches `07-implementation-planning`'s own original decomposition
(six packages authorized 2026-07-17, four more added by the same day's later planning passes, all
eventually authorized).

**Integration:** [10-integration-review](../reviews/integration-review-infinite-mode-combat-sub-mode-tranche.md)
(2026-07-20) — clean, 0 Critical/High, all five review dimensions exercised including an own live
drive chaining all ten packages together in one continuous real per-frame session.

## Evidence

- ROM build (this assessment, reusing the integration review's own unchanged-tree rebuild):
  `python3 build_rom.py BunnyQuest.gbc` → 32768 bytes, valid header.
- Full suite: `python3 test_rom.py` → **404/404 passed, 0 failed**.
- Ten VRs (table above), one content review, one integration review — all independently produced,
  none same-session as their own subject package's implementation.

## Deviations

1. **`FR-11500`/`FR-11510` have no player-reachable input binding (`BL-0148`, Medium-High).**
   Both spend actions (`inf_heal_spend`, `inf_tier_spend`) are fully implemented, unit-verified,
   and correctly persist — but no button binding was ever assigned (every existing button is
   already claimed: D-pad/movement, A/fire, B/cancel, START/SELECT/menus). This is a **named,
   adjudicated deviation with an authorization trail**, not silent drift: `07-implementation-
   planning` named the gap explicitly at `IP-1123`'s own authoring time (run #230), the requirements
   doc itself states it plainly (`FR-11500`'s own Priority field: "Implemented — 2026-07-18,
   IP-1123; player-reachable path still blocked"), and it was deliberately not treated as blocking
   either package's own authorization or verification, on the reasoning that each package's own
   Definition of Done is satisfiable via direct force-testing in the interim. **Practical effect:
   a player in this release can heal by picking up treasure only as far as any existing automatic
   trigger reaches — they cannot currently choose to spend treasure to heal or to upgrade their
   weapon tier at all**, since no input path exists. `BL-0148` is `SCHEDULED`, riding a future
   `06`/`03` UI-binding pass (a shared spend menu, most likely).
2. **`NFR-1500` (combat per-frame cycle budget) was never measured (Priority: Must).** Its own
   Acceptance Criteria requires "direct cycle-counting of combat-mode per-frame logic... performed
   and recorded before the owning implementation package is considered `COMPLETE`" — no stage-08
   package across all ten ever performed this measurement; the NFR's own status line still reads
   `UNCONFIRMED` from its original 2026-07-17 baselining, unchanged through every subsequent
   implementation. This is an **honest, named gap, not a claim of compliance** — mirroring this
   project's own established practice for `NFR-1400` (region-materialization cost), which shipped
   in Release 2's first addendum as a knowingly `NOT MET` NFR, accepted as a residual risk rather
   than blocking. Unlike `NFR-1400`, `NFR-1500` has never been measured at all (not even a
   `NOT MET` result) — so there is no data point one way or the other on whether combat-mode
   per-frame logic fits the budget. **Mitigating evidence, not a substitute for the measurement**:
   every VR and this assessment's own integration-review live drive exercised combat-mode's full
   per-frame chain (materialization + movement + fire + hit resolution + contact + knockback) via
   real PyBoy ticks with zero observed hangs, stalls, or dropped input across dozens of real
   sessions — informal evidence the frame budget is not obviously blown, but not the direct
   cycle-count measurement `NFR-1500` requires.

No other deviation found — every other Included Requirement traces to a `VERIFIED` package with a
clean integration pass.

## Residual risks

- The two deviations above, both already named with an authorization/tracking trail (`BL-0148`,
  and `NFR-1500`'s own standing gap — not yet filed as a discrete backlog entry since it's a
  Feature-wide obligation rather than a single package's finding; recommend filing it explicitly
  if GO is given, so it doesn't silently fall out of the backlog's own tracking).
- `BL-0150` (Low) — mob placement's ~3% same-cell collision rate, cosmetic, already `SCHEDULED`.
- `BL-0164`/`BL-0165`/`BL-0167` (doc-staleness, Medium/Low/Low) — all already found and either
  fixed (`BL-0164`) or `SCHEDULED` (`BL-0165`/`BL-0167`) this session; none touch shipped
  behavior.
- Standing, pre-existing, unrelated-to-this-scope items already tracked: `BL-0112` (Infinite
  Mode run-end trigger), `BL-0123` (`try_load_save` unneeded finite-mode work), `BL-0118`
  (`NFR-1400` cycle-budget gap, the precedent this assessment's own NFR-1500 reasoning leans on).

## Assessment

**GO**, conditional on the user accepting the two named deviations above (the input-binding gap
and the unmeasured cycle budget) as shipped-with-known-gaps, matching this project's own
established practice of shipping honestly-tracked partial/unmeasured items rather than blocking
on them indefinitely (`FEAT-2100`'s partial delivery in Release 2's original GO; `NFR-1400`'s
`NOT MET` status in the first addendum).

Every requirement this Feature owns traces to a `VERIFIED` package or an honestly-stated,
already-adjudicated gap; the shipped code passed a clean five-dimension integration review
including its own independent full-tranche live drive; the ROM builds correctly and the full
test suite is green. Nothing found here is a correctness defect in shipped code — both
deviations are scope/verification-completeness gaps, not bugs.

**This recommendation is advisory.** No baseline record has been flipped by this assessment —
per this skill's own charter, that happens only after the user's explicit GO.
