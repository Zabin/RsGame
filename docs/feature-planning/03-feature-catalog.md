# FP-03 — Feature Catalog

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07).** Owned by `05-feature-decomposition`.
> Derives from the closed [RQ-01](../requirements/01-functional-requirements.md)/
> [RQ-02](../requirements/02-non-functional-requirements.md) baseline (25 `FR-xxxx` + 11
> `NFR-xxxx` leaves, all owned by exactly one Feature below). **Bootstrap framing: six of these
> seven Features describe capability the shipped `BunnyQuest.gbc` already implements** — their
> catalog entries are as-built summaries, not proposals. **FEAT-5100 is the one genuinely new,
> not-yet-implemented Feature in this baseline**, formalizing `FR-5220` (per-zone `ScoreItem`
> persistence), which the user approved on 2026-07-07 (`BL-0018`, resolved).

## FEAT-1000 — Game State Machine & Menu Flow

- **Feature ID:** FEAT-1000
- **Title:** Game State Machine & Menu Flow
- **Purpose:** Provide the top-level dispatch that gates which subsystem (title, intro, gameplay,
  save menu, map, victory) is active at any time.
- **Description:** Implements the six-state machine (TITLE/INTRO/PLAYING/SAVE/MAP/VICTORY) and
  every transition between them, including the auto-load-on-boot bypass that skips TITLE/INTRO
  entirely when a valid battery save exists.
- **Scope:** State representation, all inter-state transitions, boot-time save detection and
  bypass routing. Does **not** include what happens *inside* PLAYING (movement, collection) or
  the save mechanism's own read/write behavior — only the state-level gating around them.
- **Included Requirements:** FR-1100, FR-1110, FR-1120, FR-1130, FR-1140, FR-1150, FR-1160;
  NFR-2100 (deterministic state-machine behavior — assigned here rather than to the catch-all
  engineering Feature, since it's specifically about this Feature's own correctness).
- **Excluded Requirements:** FR-5100/FR-5200 (the save mechanism's read/write behavior — FEAT-5000
  owns *what* gets saved; this Feature owns only *when* SAVE/load happens relative to state).
- **Dependencies:** None — this is the foundational dispatch layer.
- **Dependent Features:** FEAT-2000, FEAT-3000, FEAT-5000, FEAT-6000 (all gated by which state is
  active).
- **Affected Modules:** `asm_game.py`.
- **Related ADRs:** ADR-0006 (tangential, via FR-1120's auto-load bypass reading SRAM).
- **User Value:** High — defines the entire menu/play session shape the player experiences.
- **Technical Value:** High — every other Feature's activation depends on this dispatch.
- **Complexity:** Low (six states, a simple dispatch table, already shipped).
- **Risk:** Low — stable, directly confirmed against source; automated Test-method verification is
  currently compromised project-wide by `BL-0006` (see FEAT-7000), not by anything specific to
  this Feature.
- **Suggested Verification Strategy:** Test (state-value inspection at each transition) — blocked
  today by `BL-0006`'s stale suite; direct source-code confirmation is the interim method
  (as GDS-01/GDS-05 already performed).
- **Open Questions:** None.

## FEAT-2000 — Player Movement & Zone Traversal

- **Feature ID:** FEAT-2000
- **Title:** Player Movement & Zone Traversal
- **Purpose:** Move the player within a zone screen and across the 3×3 zone grid.
- **Description:** Continuous fixed-speed movement while a direction is held, facing-direction
  tracking, zone-boundary crossing into a valid neighbor, boundary-halt at grid edges, and
  on-screen arrow signaling of valid transition edges.
- **Scope:** All player-position and facing-state updates during PLAYING, and the logic
  determining whether a screen-edge crossing changes the current zone.
- **Included Requirements:** FR-2100, FR-2200, FR-2300, FR-2310, FR-2320.
- **Excluded Requirements:** FR-3100 (collision/proximity detection against Collectibles —
  FEAT-3000 owns detection logic even though it consumes this Feature's player-position output);
  FR-4100 (the zone grid's existence — FEAT-4000 owns the content this Feature traverses).
- **Dependencies:** FEAT-1000 (movement/traversal only active in PLAYING); FEAT-4000 (a zone grid
  and its screens must exist to traverse into).
- **Dependent Features:** FEAT-3000 (proximity detection needs current player position);
  FEAT-5000 (player position is part of the persisted save-field set).
- **Affected Modules:** `asm_game.py` (movement/traversal logic); `tilemaps.py` (arrow-tile
  rendering, FR-2320). **Straddle justified:** arrow signaling is a traversal-communication
  concern (telling the player which edges are crossable), not a screen-composition concern, so it
  stays with this Feature despite touching `tilemaps.py` rather than being folded into FEAT-4000
  or FEAT-6000.
- **Related ADRs:** None directly.
- **User Value:** High — core to-and-fro exploration mechanic.
- **Technical Value:** Medium.
- **Complexity:** Medium (per-axis edge detection plus 3×3 grid adjacency logic).
- **Risk:** Low.
- **Suggested Verification Strategy:** Test — currently compromised project-wide by `BL-0006`
  (the T7 suite's specific assertions are stale, per RQ-04's matrix).
- **Open Questions:** None.

## FEAT-3000 — Collectibles, Scoring & Victory

- **Feature ID:** FEAT-3000
- **Title:** Collectibles, Scoring & Victory
- **Purpose:** The proximity-based collection mechanic, score/carrot accumulation, and the win
  condition.
- **Description:** Detects player-to-Collectible proximity on both axes; increments Score and
  deactivates a collected `ScoreItem`; sets a zone's carrot flag, increments `CarrotCount`, and
  deactivates a collected Carrot; triggers VICTORY the instant `CarrotCount` reaches 9.
- **Scope:** Collection detection and its immediate score/carrot-count/flag effects, and the
  victory-trigger condition itself (the state transition it causes is FEAT-1000's FR-1160).
- **Included Requirements:** FR-3100, FR-3200, FR-3210, FR-3300.
- **Excluded Requirements:** FR-1160 (the VICTORY state transition itself — FEAT-1000); FR-5220
  (persisting collected-state across save/load — FEAT-5100, the new Feature); FR-6200 (displaying
  Score/`CarrotCount` in the HUD — FEAT-6000).
- **Dependencies:** FEAT-1000 (only active in PLAYING); FEAT-2000 (needs current player position);
  FEAT-4000 (Collectibles are per-zone authored content).
- **Dependent Features:** FEAT-5000/FEAT-5100 (`CarrotCount`/Score/ScoreItem state get
  persisted); FEAT-6000 (HUD reads `Score`/`CarrotCount`).
- **Affected Modules:** `asm_game.py`.
- **Related ADRs:** None.
- **User Value:** High — this is the core collect-a-thon loop the whole game is built around.
- **Technical Value:** High.
- **Complexity:** Low.
- **Risk:** Low, with one known soft spot carried forward from the requirements layer, not
  re-decided here: `BL-0017`/`CR-02` (the "exactly one Carrot per zone" invariant isn't
  code-enforced) — noted, not resolved, since its disposition already lives in the backlog.
- **Suggested Verification Strategy:** Test — compromised project-wide by `BL-0006`.
- **Open Questions:** Should a future package add build-time enforcement of the one-Carrot-per-zone
  invariant (`CR-02`/`BL-0017`)? Not decided here — routed to whichever future package touches
  `ZONE_COLLECTS`, per the backlog's existing disposition.

## FEAT-4000 — Zone & Screen Composition

- **Feature ID:** FEAT-4000
- **Title:** Zone & Screen Composition
- **Purpose:** The structural existence of the 9-zone 3×3 grid and the full 14-screen set.
- **Description:** Defines the nine fixed zones at their 3×3 grid positions, and the fourteen
  total screens (9 zone + 5 UI), each mapped to exactly one game state or zone.
- **Scope:** The *existence and addressing* of zones/screens as content — not their visual
  rendering technique (FEAT-6000) or the traversal logic that moves between them (FEAT-2000).
- **Included Requirements:** FR-4100, FR-4200; NFR-4100 (CGB palette budget — assigned here since
  it's specifically about zone-terrain palette assignment, not a generic build concern).
- **Excluded Requirements:** FR-6100 (the terrain/landmark *rendering* pattern applied to each
  zone screen — FEAT-6000 owns the presentation half; this Feature owns only that the 9 zones and
  14 screens exist and are addressable).
- **Dependencies:** None — a foundational content layer.
- **Dependent Features:** FEAT-2000 (traverses this grid), FEAT-3000 (Collectibles are per-zone
  content), FEAT-6000 (renders on top of this content).
- **Affected Modules:** `tilemaps.py`, `tiles.py`.
- **Related ADRs:** None directly.
- **User Value:** High — the game's entire explorable world.
- **Technical Value:** High — foundational.
- **Complexity:** Medium (14 screens authored, one per `ALL_SCREENS` entry).
- **Risk:** Low, with a known forward-looking watch item carried from the requirements layer, not
  re-decided here: `BL-0009`/`BL-0019` (CGB palette/ROM headroom consumption as future zones are
  added).
- **Suggested Verification Strategy:** Test/Inspection — Test compromised project-wide by
  `BL-0006`.
- **Open Questions:** None new — `BL-0009`/`BL-0019`'s existing disposition applies to any future
  zone addition.

## FEAT-5000 — Save/Load System (as-built)

- **Feature ID:** FEAT-5000
- **Title:** Save/Load System (as-built)
- **Purpose:** Persist and restore core progress via battery-backed SRAM.
- **Description:** On explicit player save-confirm, writes `{CurrentZone, PlayerPosition,
  CarrotCount, Score, CarrotFlags[9]}` plus a valid-save marker to SRAM; on boot, restores that
  exact field set if a valid marker is found. Facing direction and animation frame are
  intentionally left unpersisted (confirmed "not important" by the user, 2026-07-07).
- **Scope:** The save-field set as it stood before the 2026-07-07 widening — this Feature is the
  as-built, already-shipped mechanism; its extension is FEAT-5100, tracked separately since it has
  no shipped implementation yet.
- **Included Requirements:** FR-5100, FR-5200, FR-5210; NFR-5100, NFR-5200.
- **Excluded Requirements:** FR-5220 (the new per-zone `ScoreItem` persistence — FEAT-5100).
- **Dependencies:** FEAT-1000 (SAVE state gates the save action); FEAT-2000 (player position is
  persisted); FEAT-3000 (`CarrotCount`/Score/`CarrotFlags` are persisted).
- **Dependent Features:** FEAT-5100 (extends this Feature's mechanism rather than replacing it).
- **Affected Modules:** `asm_game.py`.
- **Related ADRs:** ADR-0006 (MBC1+RAM+BATTERY, `BUNY` magic).
- **User Value:** High — progress persistence is core to a collect-a-thon's play pattern.
- **Technical Value:** High.
- **Complexity:** Low–Medium.
- **Risk:** Low — `NFR-5100`/`NFR-5200` both confirmed **Met** for this field set at the
  requirements layer.
- **Suggested Verification Strategy:** Test — this specific mechanism was directly source-verified
  independent of the stale suite (GDS-06/RQ-02), unlike most other Features here.
- **Open Questions:** None — `BL-0018`'s scope question is resolved (2026-07-07); see FEAT-5100
  for the approved extension.

## FEAT-5100 — Per-Zone ScoreItem Persistence (new — not yet implemented)

- **Feature ID:** FEAT-5100
- **Title:** Per-Zone ScoreItem Persistence
- **Purpose:** Extend the save system so a restored game does not re-present already-collected
  `ScoreItem`s (stars/flowers) as available.
- **Description:** Formalizes `FR-5220`, approved by the user on 2026-07-07 resolving `BL-0018`.
  **This Feature has no shipped implementation** — it is the one genuinely new piece of scope in
  the current requirements baseline, requiring a real `06-feature-specification` →
  `07-implementation-planning` → `08-code-implementation` → `09-package-verification` pass.
- **Scope:** Saving and restoring per-zone `ScoreItem` collected-state alongside the existing
  save-field set. Explicitly **excludes** facing direction/animation-frame persistence — the user
  confirmed these are "not important" (2026-07-07); no Feature anywhere claims that scope.
- **Included Requirements:** FR-5220.
- **Excluded Requirements:** None applicable (single-requirement Feature).
- **Dependencies:** FEAT-5000 (extends its save/load mechanism rather than introducing a new
  one); FEAT-3000 (`ScoreItem` collection state is the data being persisted).
- **Dependent Features:** None yet.
- **Affected Modules:** `asm_game.py`; likely also the SRAM save-format layout GDS-07 documents —
  see Open Questions below, a real design question for `06-feature-specification` to resolve, not
  assumed here.
- **Related ADRs:** ADR-0006 (this Feature widens that ADR's declared save-field set within the
  same MBC1+RAM+BATTERY mechanism, not a new one).
- **User Value:** Medium — a completionist/quality-of-life improvement, not core-loop-critical
  (the game is fully playable and winnable without it).
- **Technical Value:** Medium — widens the save-format contract for the first time since it
  shipped.
- **Complexity:** Medium — needs a compact per-zone representation (e.g. a bitfield) fitting
  within the existing SRAM budget, plus both a save-write and a load-restore code path, and
  confirming whatever in-memory `ScoreItem`-active tracking already exists is in a saveable form.
- **Risk:** Medium — touches the save-format contract (ADR-0006) and the SRAM byte layout; must
  not silently break saves written before this Feature ships (see Open Questions).
- **Suggested Verification Strategy:** Test — new save/load round-trip assertions specific to
  per-zone `ScoreItem` state. These would be **entirely new** assertions, not repairs of stale
  ones, so this Feature's verification is not blocked by `BL-0006`/`BL-0008`'s remediation and can
  proceed independently of it.
- **Open Questions:** (1) **Exact SRAM byte layout** for per-zone `ScoreItem` state — an additive
  Data Model extension; decide at `06-feature-specification` time if purely additive, or route
  back to `03-architecture-design-synthesis` as a GDS-07 delta if it isn't. (2) **Save
  compatibility:** should a save written *before* this Feature ships be treated on first load as
  "all ScoreItems already collected" (a safe default matching nothing-changes-visually) or "all
  ScoreItems uncollected" (matching current no-persistence behavior, but re-presenting items the
  player may already recall collecting)? This is a real product decision for
  `06-feature-specification` to make explicit — not assumed either way here.

## FEAT-6000 — Presentation & HUD

- **Feature ID:** FEAT-6000
- **Title:** Presentation & HUD
- **Purpose:** Render each zone's terrain/landmark composition, the persistent HUD, and the five
  non-zone UI screens.
- **Description:** Applies the shared terrain-fill-plus-landmarks composition pattern to every
  zone screen; renders a static row-0 HUD showing carrot progress and score on every zone screen;
  renders Title/Intro/Save/Map/Victory as their own bespoke, non-zone layouts.
- **Scope:** The rendering/overlay behavior applied on top of FEAT-4000's authored content — this
  Feature owns *how* it's drawn and the HUD overlay; FEAT-4000 owns *what* content exists.
- **Included Requirements:** FR-6100, FR-6200, FR-6300; NFR-1200 (score-bar write timing — **not
  met**, assigned here since it's specific to this Feature's HUD-write behavior rather than the
  catch-all engineering Feature).
- **Excluded Requirements:** FR-4100/FR-4200 (zone/screen existence — FEAT-4000).
- **Dependencies:** FEAT-1000 (state-driven screen selection); FEAT-3000 (Score/`CarrotCount`
  values displayed); FEAT-4000 (the zone content being rendered).
- **Dependent Features:** None.
- **Affected Modules:** `tilemaps.py`, `tiles.py`, `asm_game.py` (HUD digit-writing).
- **Related ADRs:** ADR-0005 (shadow-OAM DMA — tangential; the HUD's VRAM writes are subject to
  the same VBlank-discipline pattern, per NFR-1100 in FEAT-7000).
- **User Value:** High — the player's entire visual experience.
- **Technical Value:** Medium.
- **Complexity:** Medium.
- **Risk:** Medium — `NFR-1200` (score-bar VRAM write timing) is confirmed **not met**; a real,
  tracked hardware-timing gap (`BL-0003`/`BL-0008`), not resolved by this catalog entry.
- **Suggested Verification Strategy:** Test/Inspection; `NFR-1200`'s remediation rides
  `BL-0003`/`BL-0008`'s existing disposition, not decided here.
- **Open Questions:** None new.

## FEAT-7000 — Engine Quality & Build Infrastructure

- **Feature ID:** FEAT-7000
- **Title:** Engine Quality & Build Infrastructure
- **Purpose:** The cross-cutting, non-player-visible guarantees every other Feature depends on
  holding true: ROM budget, module-boundary discipline, build determinism, and the verification
  approach itself.
- **Description:** An "internally complete system capability" per this stage's own allowance for
  Features with no player-visible behavior of their own — this entry is the aggregate of the
  build/tooling/quality NFRs that don't belong more specifically to any single player-visible
  Feature above.
- **Scope:** ROM-budget compliance, VBlank-write discipline (the general/structural half — HUD's
  specific instance is FEAT-6000's), one-job-per-file module boundaries, the PyBoy verification
  target, test-suite currency, and build reproducibility.
- **Included Requirements:** NFR-1100, NFR-3100, NFR-4000, NFR-6100, NFR-7100, NFR-8100.
- **Excluded Requirements:** NFR-1200 (FEAT-6000), NFR-2100 (FEAT-1000), NFR-4100 (FEAT-4000),
  NFR-5100/NFR-5200 (FEAT-5000) — each assigned to the Feature it's most specifically about
  instead of this catch-all, per the cohesion-maximizing rule.
- **Dependencies:** None — this is the infrastructure floor every other Feature is built on.
- **Dependent Features:** All six other Features implicitly depend on this Feature's NFRs holding
  true (a broken ROM budget, a broken build, or a meaningless test suite would undermine every
  Feature above equally).
- **Affected Modules:** All six (`gbc_lib.py`, `tiles.py`, `tilemaps.py`, `music.py`,
  `asm_game.py`, `build_rom.py`), plus `test_rom.py` and the `run-bunnygarden` harness.
- **Related ADRs:** ADR-0001 (single-bank ROM budget), ADR-0002 (Python-assembler build
  determinism), ADR-0003 (one-job-per-file), ADR-0008 (PyBoy verification target).
- **User Value:** Low — invisible to players directly.
- **Technical Value:** Critical — every other Feature's honest verification depends on this one.
- **Complexity:** N/A for the already-shipped portions; the two known gaps are remediation, not
  new construction.
- **Risk:** **High** — `NFR-7100` (test-suite currency) is confirmed **not met** at Critical
  severity (`BL-0006`/`BL-0008`): the single biggest risk in this entire catalog, since it means
  no Feature above can currently claim genuine automated Test-method verification, only direct
  source-code confirmation.
- **Suggested Verification Strategy:** Inspection today, per RQ-03 finding #3; Test once
  `BL-0006`/`BL-0008`'s remediation package lands.
- **Open Questions:** When should the `BL-0006`/`BL-0008` test-suite-rewrite remediation be
  prioritized relative to FEAT-5100's new work? Not decided in this pass — see the Release Plan's
  Highest-Risk callout; this is a sequencing question for `07-implementation-planning`/the user,
  not resolved here.

## Requirement-to-Feature tally (completeness check)

25 `FR-xxxx` + 11 `NFR-xxxx` = 36 requirement IDs; every one assigned to exactly one Feature above
(verified by direct tally, restated in [FP-05](05-feature-review.md)'s review rather than only
asserted here).
