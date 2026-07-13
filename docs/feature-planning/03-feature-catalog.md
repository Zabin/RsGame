# FP-03 — Feature Catalog

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07); delta 2026-07-10 (procgen-world
> increment, 5 new Features + FEAT-5100 shipped-status correction; FEAT-6000/FEAT-7000 Risk
> fields corrected, `BL-0037`); delta 2026-07-11 (2 new Features — `FEAT-9100` maze-shaped region
> adjacency, `FEAT-2100` maze-aware transition-edge signaling — for `ADR-0012`'s post-ship
> remediation, `BL-0064`/`0065`/`0067`).** Owned by
> `05-feature-decomposition`. Derives from the closed
> [RQ-01](../requirements/01-functional-requirements.md)/
> [RQ-02](../requirements/02-non-functional-requirements.md) baseline, now 36 bootstrap `FR-xxxx`/
> `NFR-xxxx` leaves + 17 target leaves from the 2026-07-09 RQ-01…04 delta + 3 target leaves from
> the 2026-07-11 `ADR-0012` delta (`FR-9140`/`FR-9150`/`FR-2330`; 56 total, all owned by exactly
> one Feature below). **Bootstrap framing: six of the original seven Features describe
> capability the shipped `BunnyQuest.gbc` already implements** — their catalog entries are
> as-built summaries, not proposals. **FEAT-5100 shipped and was independently verified
> 2026-07-07** ([IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md)/
> [VR-1010](../implementation/verification/VR-1010-per-zone-scoreitem-persistence.md)) — this
> entry's earlier "not yet implemented" framing is corrected below (`BL-0036`). **Five new
> Features (FEAT-1100, FEAT-4100, FEAT-5300, FEAT-6100, FEAT-9000) formalize the
> aesthetics/visual-story-narrative/procgen-world-map increment's 17 target requirements** — none
> yet implemented, per that increment's RQ-01…04 delta (2026-07-09). **Two more new Features
> (FEAT-9100, FEAT-2100) formalize `ADR-0012`'s maze-shaped-region-adjacency post-ship
> remediation** — neither yet implemented, per the 2026-07-11 delta.

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
  active); FEAT-1100, FEAT-1200 (each extends this Feature's own state set with new nodes).
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

## FEAT-2100 — Maze-Aware Transition-Edge Signaling (new — not yet implemented)

> **Forward reference (metadata only):** specified by
> [FS-108](../features/FS-108-maze-aware-transition-edge-signaling.md) (2026-07-11, revised
> 2026-07-12) — **fully specified.** Logic half implemented and `VERIFIED`
> ([IP-1080](../implementation/packages/IP-1080-maze-aware-edge-classification.md)/
> [VR-1080](../implementation/verification/VR-1080-maze-aware-edge-classification.md)); rendering
> half specified (FS-108 §6 Workflow C, §15 AC-4/5) and planned 2026-07-12 as
> [IP-1081](../implementation/packages/IP-1081-maze-blocked-edge-indicator-content.md)/
> [IP-1082](../implementation/packages/IP-1082-maze-blocked-edge-indicator-render.md) — both
> authorized 2026-07-12 (`BL-0092`); `IP-1081` **`COMPLETE`**, `IP-1082` `BLOCKED` on it, tracked
> as `BL-0075`.

- **Feature ID:** FEAT-2100
- **Title:** Maze-Aware Transition-Edge Signaling
- **Purpose:** Distinguish, at each screen edge, a maze-blocked-but-grid-adjacent edge from a true
  grid boundary — both currently signal identically (no arrow) once `FEAT-9100`'s maze ships.
- **Description:** Extends `FEAT-2000`'s existing on-screen arrow signal (`FR-2320`) from its
  2-state form (arrow / no-arrow) to 3 states: open (a live, maze-connected neighbor — reuses the
  existing arrow verbatim), blocked (a grid-adjacent region exists but the maze doesn't connect to
  it — a new indicator), or absent (a true grid boundary — no indicator, as today). The
  open-vs-something-else distinction is already correct today; this Feature adds the
  blocked-vs-boundary distinction the maze makes meaningful for the first time.
- **Scope:** The render-time logic distinguishing "grid-adjacent but maze-blocked" from "not
  grid-adjacent at all" (re-deriving grid adjacency from `(row, col, WORLD_SCALE)` arithmetic,
  since the region graph's own data doesn't carry this distinction — both cases are `0xFF`), and
  whatever new tile art the blocked-edge indicator needs. Explicitly **excludes** the maze
  generation this Feature signals the output of (`FEAT-9100`), and any mid-screen collision/wall
  enforcement (out of scope for any current Feature — explicitly not part of this request).
- **Included Requirements:** FR-2330.
- **Excluded Requirements:** FR-2300, FR-2310, FR-2320 (`FEAT-2000`'s own shipped requirements —
  this Feature's open-edge case reuses `FR-2320`'s existing rendering verbatim, not a
  reimplementation); FR-9140/FR-9150 (the maze this Feature signals — `FEAT-9100`).
- **Dependencies:** FEAT-2000 (extends its arrow-signaling logic; the open-edge case is this
  Feature's own dependency on that logic continuing to work unchanged); FEAT-9100 (there is no
  "blocked but grid-adjacent" case to signal before the maze exists — this Feature cannot ship
  before FEAT-9100 does).
- **Dependent Features:** FEAT-1200 (LEGEND's own content displays this Feature's tiles/meaning —
  a content dependency, not a build-order one; both this Feature's tiles already ship).
- **Affected Modules:** `asm_game.py` (`draw_region_arrows`'s own extension — the new 3-way
  branch); `tiles.py`/`tilemaps.py` (new tile art for the blocked-edge indicator — **not yet
  designed**; a `GDS-08` presentation-architecture delta is needed before this Feature's tile
  budget/palette assignment can be specified, flagged here as an open blocker, not assumed
  resolved).
- **Related ADRs:** ADR-0009, ADR-0012 (point 2 — confirms the region graph's own data format
  needs no change; this Feature's distinction is computed at render time, not stored).
- **User Value:** Medium-High — without this, a maze-blocked edge is indistinguishable from a
  dead end, undermining the legibility of `FEAT-9100`'s own core value (a maze the player can
  read as "there's a path here I haven't opened" vs. "this is the edge of the world").
- **Technical Value:** Low — a presentation-layer extension of already-shipped rendering logic, no
  new subsystem.
- **Complexity:** Low — the render-time logic itself is simple arithmetic (re-derive grid
  adjacency, compare against the region graph); the only real unknown is the new tile art, which
  is a content/architecture question, not a logic one.
- **Risk:** Low, contingent on one real blocker: **cannot be specified past the logic layer until
  the `GDS-08` tile-art delta this Feature needs is authored** (see Open Questions) — a
  dependency this catalog entry names explicitly rather than silently assuming away.
- **Suggested Verification Strategy:** Test — per-edge 3-way state audit across a `(seed, scale)`
  corpus, extending `FR-2320`'s existing tilemap-inspection pattern (per `FR-2330`'s own
  Acceptance Criteria).
- **Open Questions:** The blocked-edge indicator's actual tile art/palette assignment is
  undecided — routed to `03-architecture-design-synthesis` for a `GDS-08` delta before
  `06-feature-specification` can fully specify this Feature's rendering half. The logic half
  (grid-arithmetic re-derivation) has no open question and could be specified independently if
  `06` prefers to unblock that part first.

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

## FEAT-5100 — Per-Zone ScoreItem Persistence (shipped, VERIFIED 2026-07-07)

> **Forward reference (metadata only):** specified by
> [FS-101](../features/FS-101-per-zone-scoreitem-persistence.md) (2026-07-07); implemented by
> [IP-1010](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md); independently
> verified by [VR-1010](../implementation/verification/VR-1010-per-zone-scoreitem-persistence.md)
> (2026-07-07). **Correction (`BL-0036`, 2026-07-10):** this entry previously read "no shipped
> implementation" — stale since the same day's `IP-1010`/`VR-1010`; corrected below.

- **Feature ID:** FEAT-5100
- **Title:** Per-Zone ScoreItem Persistence
- **Purpose:** Extend the save system so a restored game does not re-present already-collected
  `ScoreItem`s (stars/flowers) as available.
- **Description:** Formalizes `FR-5220`, approved by the user on 2026-07-07 resolving `BL-0018`.
  **Shipped and independently verified 2026-07-07** — Release 1's sole Feature, closing that
  release's critical path end-to-end.
- **Scope:** Saving and restoring per-zone `ScoreItem` collected-state alongside the existing
  save-field set. Explicitly **excludes** facing direction/animation-frame persistence — the user
  confirmed these are "not important" (2026-07-07); no Feature anywhere claims that scope.
- **Included Requirements:** FR-5220.
- **Excluded Requirements:** None applicable (single-requirement Feature).
- **Dependencies:** FEAT-5000 (extends its save/load mechanism rather than introducing a new
  one); FEAT-3000 (`ScoreItem` collection state is the data being persisted).
- **Dependent Features:** FEAT-5300 (extends this Feature's version-byte precedent for the
  generated-world save fields).
- **Affected Modules:** `asm_game.py`. **Shipped design:** a 9-byte `SCOREITEM_FLAGS` array
  (`0xC060`–`0xC068`) mirroring `CARROT_FLAGS`, plus a save-format version guard (`0xA012`) —
  both confirmed against GDS-07 (see FS-101's resolved Open Questions).
- **Related ADRs:** ADR-0006 (this Feature widens that ADR's declared save-field set within the
  same MBC1+RAM+BATTERY mechanism, not a new one).
- **User Value:** Medium — a completionist/quality-of-life improvement, not core-loop-critical
  (the game is fully playable and winnable without it).
- **Technical Value:** Medium — widened the save-format contract for the first time since ship,
  establishing the version-byte pattern `FEAT-5300` now extends.
- **Complexity:** Medium (as designed and shipped) — a compact per-zone bitfield, a save-write and
  a load-restore path, both mirroring the existing `CARROT_FLAGS` handling.
- **Risk:** Low — shipped and independently verified; the save-format-compatibility question
  (below) was resolved before implementation, not discovered after.
- **Suggested Verification Strategy:** Test — **T11.a–e** (14 checks), independently re-run by
  `VR-1010` (125/125 pass). Not blocked by `BL-0006`/`BL-0008` (which was itself remediated and
  closed the same day, `IP-9010`/`VR-9010`).
- **Open Questions:** None remaining — both resolved by `FS-101`: (1) SRAM byte layout assigned
  `0xC060`–`C068`/`0xA013`–`A01B` (GDS-07). (2) Save compatibility: pre-upgrade saves default to
  "all ScoreItems uncollected," guarded by the new version byte — confirmed by `T11.d`'s synthetic
  pre-upgrade fixture.

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
- **Risk:** Low — `NFR-1200` (score-bar VRAM write timing) is confirmed **Met** (`IP-9020`,
  independently verified `VR-9020`, 2026-07-07); the prior hardware-timing gap (`BL-0003`/
  `BL-0008`) is resolved (correction 2026-07-10, `BL-0037` — this field previously said "not
  met," stale since before this catalog was even first authored).
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
- **Risk:** Low — `NFR-7100` (test-suite currency) is confirmed **Met** (`IP-9010`, independently
  verified `VR-9010`, 2026-07-07): the suite is trustworthy again, and every Feature above can
  claim genuine automated Test-method verification, not just direct source-code confirmation.
  This was the single biggest risk in this catalog at authoring time (`BL-0006`/`BL-0008`,
  Critical) — resolved the same day the catalog was first authored, but this field was never
  updated to say so until now (correction 2026-07-10, `BL-0037`).
- **Suggested Verification Strategy:** Test — the rewritten suite (`IP-9010`) now covers this
  Feature's own NFRs directly (T1–T10's currency is exactly what `NFR-7100` requires).
- **Open Questions:** None remaining — `BL-0006`/`BL-0008`'s remediation shipped and was
  independently verified 2026-07-07; the prior sequencing question (relative to FEAT-5100's new
  work) is moot since both landed the same day, resolving this catalog's own former Highest-Risk
  callout (see the Release Plan, already updated to reflect this at run #48).

## FEAT-9000 — Procedural World Generation & Item-Agnostic Collection (new — not yet implemented)

> **Forward reference (metadata only):** specified by
> [FS-102](../features/FS-102-procedural-world-generation.md) (2026-07-10; revised 2026-07-12,
> `FR-9160`/`ADR-0015`). 3 original Open Questions (grammar-table contents, algorithm
> implementation detail, ROM-pointer need), all routed to `07-implementation-planning`, resolved
> at `IP-1020`. **2 new Open Questions from the 2026-07-12 revision:** OQ4 (this entry's own
> Included Requirements cites `FR-9130`, not `FR-9160`, its direct successor — routed to
> `05-feature-decomposition`, this stage's own owner) and **OQ5 resolved same day** — planned as
> [IP-1021](../implementation/packages/IP-1021-win-condition-redesign.md) (`NOT STARTED`, not
> authorized), which decides the per-region tri-state encoding against the real code.

- **Feature ID:** FEAT-9000
- **Title:** Procedural World Generation & Item-Agnostic Collection
- **Purpose:** Deterministically generate a grammar-valid, fully-reachable region graph from
  (seed, scale), with exactly one collectible KeyItem per region, collected via an item-agnostic
  mechanism generalizing the shipped Carrot rule.
- **Description:** Formalizes MSTR-001 C10's world-generation commitment and C9's item-agnostic
  collect-goal together, since ADR-0009 ties them at the generator level: the generator produces
  `WORLD_SCALE²` regions, each with a biome assignment and adjacency edges restricted to R212's
  grammar-legal pairings (enforced by construction, not post-hoc validation), guarantees every
  region is reachable from the start and holds exactly one KeyItem, and the collection mechanic
  itself is generalized from FR-3210's Carrot-specific rule to an item-agnostic identity.
- **Scope:** The generation algorithm (region graph: biome assignment + grammar-constrained
  adjacency), its determinism/reachability/one-KeyItem-per-region guarantees, the WRAM/SRAM
  working-set headroom it must fit within, and the collection-mechanic generalization. Explicitly
  **excludes** the seed/scale entry UI and the generation *trigger* (FEAT-1100 — this Feature owns
  what the generator does once invoked, not how a player starts it), the generated-region screen's
  *rendering* (FEAT-4100 — this Feature owns *which* biome a region gets, not how that biome's
  tiles are drawn), and persisting the generated world's parameters to SRAM (FEAT-5300).
- **Included Requirements:** FR-9100, FR-9110, FR-9120, FR-9130, FR-4310, FR-3220; NFR-2200,
  NFR-4200.
- **Excluded Requirements:** FR-1180 (the entry UI/trigger — FEAT-1100, though it calls into this
  Feature's routine); FR-4300 (screen rendering — FEAT-4100); FR-9200 (save persistence —
  FEAT-5300).
- **Dependencies:** FEAT-1000 (generation is invoked during a state transition, FR-1180); FEAT-3000
  (generalizes FR-3210's Carrot-specific collection rule — FR-3220 is this Feature's own
  requirement, but the mechanism it generalizes is FEAT-3000's); FEAT-4000 (generalizes the fixed
  9-zone/3×3 structural model this Feature's `WORLD_SCALE²` regions supersede).
- **Dependent Features:** FEAT-1100 (triggers this Feature's routine from the new-game flow);
  FEAT-4100 (renders the biome each region's generation assigns); FEAT-5300 (persists this
  Feature's seed/scale/KeyItemFlags output).
- **Affected Modules:** New module `worldgen.py` (per GDS-09's delta — the on-console SM83
  generator; a build-side Python mirror also lives here per R305's reference-generator-oracle
  pattern, imported only by `test_rom.py`, never by `build_rom.py`/`asm_game.py`); `asm_game.py`
  (collection-mechanic generalization, FR-3220).
- **Related ADRs:** ADR-0009 (screen/room-graph generation, on-console at new-game creation,
  grammar-constrained by construction), ADR-0010 (seed & scale model, 16-bit seed/byte scale
  2–9), ADR-0011 (MBC1 default wiring — tangential, no immediate bank-switching dependency).
- **User Value:** High — this is the increment's central new capability; every other new Feature
  in this catalog depends on or renders what this Feature generates.
- **Technical Value:** High — the foundational new-work Feature for this entire increment.
- **Complexity:** High — a new generation algorithm (screen/room-graph, per R213's recommendation)
  with three simultaneous structural guarantees (determinism, reachability, grammar-legality) that
  must all be generator-*guaranteed*, not post-hoc-checked, per ADR-0009.
- **Risk:** Medium-High — genuinely new algorithmic work with no shipped precedent; R305's
  reference-generator-oracle pattern (a build-side Python mirror whose output must byte-match the
  SM83 routine) is itself a new verification technique this Feature depends on working correctly.
- **Suggested Verification Strategy:** Test — property tests across a (seed, scale) corpus
  (determinism, reachability, one-KeyItem-per-region, grammar-legality), per R305's extension;
  entirely new assertions, unblocked by any prior remediation.
- **Open Questions:** The exact generation algorithm's implementation detail (R213 recommends
  screen/room-graph generation and a xorshift-family PRNG but leaves the concrete step-by-step
  construction to `06-feature-specification`/`07-implementation-planning`) is not decided here —
  ADR-0009 fixes the *approach*, not the routine's line-by-line design.

## FEAT-9100 — Maze-Shaped Region Adjacency (new — not yet implemented)

> **Forward reference (metadata only):** specified by
> [FS-107](../features/FS-107-maze-shaped-region-adjacency.md) (2026-07-11). 3 Open Questions
> recorded there (visited-flag packing, transient-scratch addresses, starting-region backtrack
> initialization), all routed to `07-implementation-planning`.

- **Feature ID:** FEAT-9100
- **Title:** Maze-Shaped Region Adjacency
- **Purpose:** Replace `FEAT-9000`'s current full-lattice region adjacency (every grid-adjacent
  region pair always connected) with a generated maze — a spanning tree guaranteeing reachability
  plus a braid pass reopening a configurable fraction of pruned edges — so the traversable world
  reads as distinct regions connected by paths, not a uniformly open grid.
- **Description:** Extends `FEAT-9000`'s generation routine with a second, independent pass over
  the same region grid: after biome assignment completes (unchanged), build a spanning tree via
  randomized DFS/recursive backtracker (iterative form, reusing the region graph's own neighbor
  data as backtracking state — no separate stack), then reopen a fraction of the pruned edges
  (the braid pass) according to a configurable threshold. The resulting adjacency graph — not the
  full grid — is what navigation and rendering consume.
- **Scope:** The maze-generation algorithm itself (spanning tree + braid) and the braid-fraction
  parameter's mechanism/default. Explicitly **excludes** biome assignment (`FEAT-9000`'s own
  unchanged pass), navigation/rendering consumption of the resulting graph (both already
  generalize to any subgraph with no further changes — see Dependent Features), the braid-fraction
  value's player-facing UI exposure (open question, not this Feature's scope), and the
  maze-blocked-vs-boundary visual distinction (`FEAT-2100`).
- **Included Requirements:** FR-9140, FR-9150.
- **Excluded Requirements:** FR-9100 (biome assignment/base determinism — `FEAT-9000`, unchanged);
  FR-9120 (reachability — `FEAT-9000`'s own requirement, now structurally guaranteed by this
  Feature's spanning tree rather than incidentally by full connectivity, but the requirement
  itself stays owned by `FEAT-9000`); FR-4310 (grammar-valid adjacency — `FEAT-9000`, confirmed
  unaffected since biome assignment doesn't consume maze connectivity); FR-2330 (the maze-blocked
  visual indicator — `FEAT-2100`).
- **Dependencies:** FEAT-9000 (this Feature's maze pass runs after and reads the region grid
  FEAT-9000's biome-assignment pass produces; also depends on FEAT-9000's own determinism/
  reachability guarantees holding as preconditions).
- **Dependent Features:** FEAT-2100 (needs this Feature's maze output to have a "blocked but
  grid-adjacent" case to signal at all). **No changes needed to any already-shipped Feature**:
  `FEAT-2000`'s navigation (`check_zone_transition`, `IP-9050`) and `FEAT-4100`'s rendering
  (`dsr_p`/`draw_region_arrows`, `IP-1030`) already consume the region graph's neighbor data
  generically (any 0–80 value or `0xFF`) — neither assumed full connectivity, so both already
  work correctly against this Feature's sparser output with zero code changes (`ADR-0012` point 2,
  directly confirmed by reading both shipped call sites).
- **Affected Modules:** `worldgen.py` (Python oracle mirror, new maze-generation pass);
  `asm_game.py` (`generate_world`, same new pass on the SM83 side).
- **Related ADRs:** ADR-0009 (screen/room-graph generation — the family this Feature stays
  within), ADR-0012 (the specific decision this Feature implements — algorithm choice, braid
  mechanism, pass ordering).
- **User Value:** High — directly answers the project owner's own stated goal (Zelda/Pokémon-
  style distinct regions and paths, not a uniformly open grid), the reason `BL-0064` was filed.
- **Technical Value:** Medium — extends an already-proven generation pipeline (same PRNG,
  same LCD-off generation window, same Python-oracle-parity testing pattern) rather than
  introducing new infrastructure.
- **Complexity:** Medium — a new algorithm family (spanning-tree construction) the codebase
  hasn't implemented before, but `R112` already grounds the specific SM83-cheap approach
  (mod-4 direction draw, `REGION_GRAPH`-as-backtracking-state) in detail, leaving comparatively
  little open design space for `06-feature-specification` to resolve.
- **Risk:** Low-Medium — the highest-risk design question (which algorithm fits this hardware) is
  already resolved and evidenced (`R112`/`ADR-0012`); remaining risk is ordinary
  implementation risk (getting the iterative backtracker's edge cases right — e.g. the starting
  region's own dead-end/backtrack-to-nothing case), not an open architectural unknown.
- **Suggested Verification Strategy:** Test — property tests across a `(seed, scale,
  braid-fraction)` corpus (subgraph-of-full-lattice, reachability, determinism), extending
  `R305`'s existing pattern; a new statistical check for the braid-fraction's probabilistic
  guarantee (per `FR-9150`'s own Acceptance Criteria — not an exact-equality check).
- **Open Questions:** None left for this stage — `FR-9150`'s own Notes field already resolves the
  "does the UI-exposure question block this Feature" question (no, a fixed default unblocks
  implementation) and the CR-05/`BL-0066` conflict this Feature's own output would otherwise
  enable is explicitly out of this Feature's scope, not silently assumed resolved.

## FEAT-4100 — Generated-Region Screen Composition (new — not yet implemented)

> **Forward reference (metadata only):** specified by
> [FS-103](../features/FS-103-generated-region-screen-composition.md) (2026-07-10). 2 Open
> Questions recorded there (biome-family content completeness, tile-index/palette sizing), both
> routed to `07-implementation-planning` in lockstep with FS-102's grammar-table question.

- **Feature ID:** FEAT-4100
- **Title:** Generated-Region Screen Composition
- **Purpose:** Render each generated region's screen from exactly one biome family's tile set,
  within the existing transition-smoothness budget.
- **Description:** Extends `FEAT-4000`'s zone/screen existence layer to the generated-world case:
  every region's screen is composed entirely from its assigned biome family (`FEAT-9000`'s output)
  — never a blend of two — and its screen transition uses the same `copy_screen`/LCD-off mechanism
  every existing zone transition already uses, with no new, slower path introduced.
- **Scope:** The rendering constraint (one biome per screen) and its transition-timing bar.
  Explicitly **excludes** *which* biome a region is assigned (`FEAT-9000`'s generation output) and
  the biome-family palette-stepping *quality* judgment (`FEAT-6100` — this Feature owns the hard
  structural constraint; `FEAT-6100` owns the aesthetic-quality bar on top of it).
- **Included Requirements:** FR-4300; NFR-1300.
- **Excluded Requirements:** FR-4310 (grammar-valid adjacency — a generation-time construction
  guarantee, `FEAT-9000`, per ADR-0009's own framing, not a rendering concern); NFR-6510
  (palette-stepping aesthetic judgment — `FEAT-6100`).
- **Dependencies:** FEAT-9000 (needs a region's biome assignment to exist before it can be
  rendered); FEAT-4000 (extends its zone/screen composition existence layer); FEAT-6000 (reuses
  the existing terrain-fill-plus-landmarks rendering pattern, per GDS-08 §8's extension).
- **Dependent Features:** FEAT-6100 (judges this Feature's biome-family screen output for
  palette-stepping quality).
- **Affected Modules:** `tilemaps.py` (screen generator, generalized from one-function-per-zone to
  one-function-per-biome-family per GDS-09's delta), `tiles.py` (biome-family terrain tile sets,
  content-authoring scope for whichever content package implements this).
- **Related ADRs:** ADR-0009 (per-biome terrain texture continues the existing `_fill()` pattern —
  this ADR decides adjacency/placement, not texture, per its own framing).
- **User Value:** High — the player's entire visual experience of the generated world.
- **Technical Value:** Medium.
- **Complexity:** Medium — structurally similar to the shipped per-zone rendering pattern,
  generalized from a fixed 9-zone set to a variable-count biome-family set.
- **Risk:** Low — reuses the existing, already-verified LCD-off transition mechanism unchanged;
  the new constraint (one biome per screen) is enforced by which tiles a screen generator uses,
  not new hardware-timing-sensitive code.
- **Suggested Verification Strategy:** Test (tile-family audit per generated screen) / Inspection
  — new assertions, unblocked by prior remediation.
- **Open Questions:** None surfaced yet — the exact biome-family tile-set assignments are content-
  authoring detail for whichever `08-content-authoring` package implements this Feature.

## FEAT-5300 — Generated-World Save Persistence (new — not yet implemented)

> **Forward reference (metadata only):** specified by
> [FS-105](../features/FS-105-generated-world-save-persistence.md) (2026-07-10). No Open
> Questions — fully determined by ADR-0010/GDS-07's delta.

- **Feature ID:** FEAT-5300
- **Title:** Generated-World Save Persistence
- **Purpose:** Persist a generated world's (seed, scale, per-region KeyItemFlags) to SRAM, and
  regenerate the region graph from (seed, scale) on load rather than persisting the graph itself.
- **Description:** Formalizes FR-9200/NFR-5300, extending `FEAT-5000`/`FEAT-5100`'s save mechanism
  and version-byte precedent: on save, writes `SEED`/`WORLD_SCALE`/`KeyItemFlags[region]` under a
  new save-format version value; on load, restores `SEED`/`WORLD_SCALE`, regenerates the region
  graph via `FEAT-9000`'s routine (never reads a persisted graph), then restores `KeyItemFlags`
  onto the regenerated graph. A pre-upgrade save (predating this extension) is never offered on
  "continue," never partially loaded with garbage seed/scale/region-flags bytes.
- **Scope:** The save-write and load-restore code paths for the three new fields, and the
  version-guard bump that protects pre-upgrade saves. Explicitly **excludes** the generation
  routine itself (`FEAT-9000` — this Feature only persists/restores its inputs and per-region
  flags, never the graph structure) and the "continue" option's gating logic (`FEAT-1100` — this
  Feature supplies the version-match fact `FEAT-1100`'s MAIN MENU consumes).
- **Included Requirements:** FR-9200; NFR-5300.
- **Excluded Requirements:** FR-9100/FR-9110 (the generation routine and its immutability rule —
  `FEAT-9000`); FR-1170 (the MAIN MENU's own continue/new-game branching — `FEAT-1100`).
- **Dependencies:** FEAT-9000 (persists its output — seed, scale, KeyItemFlags); FEAT-5000
  (extends its save/load mechanism); FEAT-5100 (extends its version-byte precedent — the second
  save-format change since ship, following the same pattern as the first).
- **Dependent Features:** None yet.
- **Affected Modules:** `asm_game.py` (save-write/load-restore extension, following `IP-1010`'s
  established pattern exactly).
- **Related ADRs:** ADR-0010 (save-format extension), ADR-0006 (the MBC1+RAM+BATTERY mechanism
  this Feature's fields ride, unchanged).
- **User Value:** High — losing world seed/scale or per-region collection state on reload would
  make the generated world worthless to return to.
- **Technical Value:** Medium — a second, structurally-identical instance of the version-byte
  pattern `FEAT-5100` established; low technical novelty, high correctness stakes.
- **Complexity:** Low-Medium — directly follows `IP-1010`'s shipped precedent (a version-guarded
  field-set extension), with the added regenerate-don't-persist twist for the region graph itself.
- **Risk:** Medium — a wrong version-guard bump could either falsely reject valid new saves or
  falsely accept a pre-upgrade save's garbage bytes as seed/scale/region data; needs the same
  synthetic pre-upgrade fixture discipline `IP-1010`'s T11.d established.
- **Suggested Verification Strategy:** Test — save/reload two-instance harness (R305's existing
  pattern) extended to SEED/WORLD_SCALE/KeyItemFlags, plus a synthetic pre-upgrade fixture
  following T11.d's precedent exactly.
- **Open Questions:** None surfaced yet — ADR-0010 already resolved the pre-upgrade-save-on-
  continue question (not offered, following the FS-101 precedent for resolving this class of
  question directly).

## FEAT-1100 — Main Menu & New-Game Flow (new — not yet implemented)

> **Forward reference (metadata only):** specified by
> [FS-104](../features/FS-104-main-menu-new-game-flow.md) (2026-07-10). 2 Open Questions recorded
> there (SEED/SCALE ENTRY cancel path, menu input mapping), both routed to
> `07-implementation-planning`.

- **Feature ID:** FEAT-1100
- **Title:** Main Menu & New-Game Flow
- **Purpose:** Gate every boot through a mandatory MAIN MENU offering continue/new-game, drive the
  new-game seed/scale entry that triggers world generation, and offer exit-to-main-menu with
  auto-save from the SAVE state.
- **Description:** Extends `FEAT-1000`'s state machine with three new states/transitions: MAIN
  MENU (always entered on boot, never bypassed — retiring the current auto-load bypass), a
  SEED/SCALE ENTRY digit-cursor UI that triggers `FEAT-9000`'s generation routine on confirmation,
  and a new SAVE-state option that auto-saves (reusing `FEAT-5000`'s save-write) before returning
  to MAIN MENU rather than PLAYING.
- **Scope:** The state-level gating and UI flow around world creation/continuation. Explicitly
  **excludes** what the generator does once triggered (`FEAT-9000`), the save-field set itself
  (`FEAT-5000`/`FEAT-5300`), and the "continue" option's version-match evaluation logic beyond
  reading the flag `FEAT-5300` supplies.
- **Included Requirements:** FR-1170, FR-1180, FR-1190.
- **Excluded Requirements:** FR-1120 (the current auto-load bypass — `FEAT-1000`'s existing entry;
  this Feature supersedes its *behavior* on implementation, per FR-1120's own target-state pointer,
  but does not modify `FEAT-1000`'s catalog entry, which remains the as-built record until then);
  FR-9100/FR-9110 (the generation routine and its immutability rule — `FEAT-9000`); FR-5100 (the
  underlying save-write mechanism — `FEAT-5000`, reused not reimplemented).
- **Dependencies:** FEAT-1000 (extends its state machine); FEAT-9000 (triggers its generation
  routine on new-game confirm); FEAT-5000 (reuses its save-write for the auto-save option).
- **Dependent Features:** FEAT-1200 (reuses this Feature's own cursor-menu convention for its
  SELECT MENU rather than inventing a second one).
- **Affected Modules:** `asm_game.py` (new states/dispatch), `tilemaps.py` (two new screens: main
  menu, seed/scale entry).
- **Related ADRs:** ADR-0009, ADR-0010.
- **User Value:** High — the first screen every player sees after this increment ships, and the
  sole path into a generated world.
- **Technical Value:** High — the wiring point that connects the new state machine to world
  generation.
- **Complexity:** Medium — a new digit-cursor entry UI (no text engine, D-pad + A only, per D1),
  a save-validity/version check, and one new SAVE-state option.
- **Risk:** Medium — retires FR-1120's auto-load bypass, a deliberate protected-baseline change
  (MSTR-001 C2 amendment, the same C5-style deliberateness the 3×3 world's archival already
  named); needs careful negative testing that FR-9110's "seed/scale immutable mid-game" rule
  actually holds against every reachable input sequence.
- **Suggested Verification Strategy:** Test — entirely new assertions; unblocked by any prior
  remediation.
- **Open Questions:** None surfaced yet — first specified at `06-feature-specification`.

## FEAT-1200 — SELECT Menu & Edge-Indicator Legend Screen (new — not yet implemented)

> **Forward reference (metadata only):** requirements baselined as FR-1200/FR-1210
> (`04-requirements-engineering`, 2026-07-13, `CR-06`/`BL-0100`); no `FS-xxx` authored yet.

- **Feature ID:** FEAT-1200
- **Title:** SELECT Menu & Edge-Indicator Legend Screen
- **Purpose:** Give the player an in-game explanation of the on-screen transition-edge indicator
  tiles (`FEAT-2100`'s open-arrow/blocked-edge/absent three-state signal), which today has no
  in-game explanation anywhere (`BL-0100`, project owner request).
- **Description:** Extends `FEAT-1000`'s state machine with two new states: a SELECT MENU
  (cursor-selectable "map"/"legend," reusing `FEAT-1100`'s own cursor-menu convention) that
  replaces `SELECT`'s current direct jump to `MAP`, and a LEGEND screen (a single static page
  showing each indicator tile beside a plain-language label). `MAP` itself is entirely unchanged
  — this Feature adds a menu step in front of it, not a change to its own content.
- **Scope:** The new state-machine nodes/transitions (SELECT MENU, LEGEND) and the LEGEND
  screen's own static content. Explicitly **excludes** `MAP`'s own content/layout (`FEAT-1000`'s
  existing entry, untouched — its own future redesign is `BL-0050`, tracked separately) and the
  indicator tiles' own meaning/rendering logic (`FEAT-2100`, reused/displayed, not redefined).
- **Included Requirements:** FR-1200, FR-1210.
- **Excluded Requirements:** FR-1150 (the existing PLAYING↔MAP transition — `FEAT-1000`'s own
  entry; this Feature's FR-1200 supersedes only its SELECT-entry clause on implementation, per
  FR-1150's own target-state pointer, without modifying `FEAT-1000`'s catalog entry); FR-2320/
  FR-2330 (the indicator tiles' own meaning and render-time classification — `FEAT-2000`/
  `FEAT-2100`, this Feature only displays them).
- **Dependencies:** FEAT-1000 (extends its state machine); FEAT-1100 (reuses its cursor-menu
  convention rather than inventing a second one); FEAT-2100 (LEGEND's own content depends on the
  open-arrow/blocked-edge tiles that Feature defines already existing — both tiles are already
  shipped, `IP-1030`/`IP-1081`, so this is a content dependency, not a build-order one).
- **Dependent Features:** None yet.
- **Affected Modules:** `asm_game.py` (new states/dispatch — the SELECT MENU cursor and the two
  confirm branches), `tilemaps.py` (one new screen: LEGEND; `map_screen()` itself untouched).
- **Related ADRs:** None.
- **User Value:** Medium — closes a real discoverability gap (`FEAT-2100`'s own 3-state signal is
  currently unexplained in-game), but affects a reference screen a player visits rarely, not the
  moment-to-moment loop.
- **Technical Value:** Low — a small state-machine extension reusing two already-established
  conventions (cursor-menu UI, static-screen layout); no new subsystem.
- **Complexity:** Low — no new tile art or palette entry (GDS-08 §11), no new generation/collision
  logic; the only new mechanism is the two-state cursor menu itself, which directly mirrors
  `FEAT-1100`'s own MAIN MENU implementation.
- **Risk:** Low — the one real, explicitly-named tradeoff (an extra button press to reach `MAP`
  for every player) was already weighed and accepted at the architecture level (GDS-01 §4c), not
  an open risk this Feature carries forward undecided.
- **Suggested Verification Strategy:** Test — state-transition assertions for the new SELECT
  MENU/LEGEND states (mirroring `FEAT-1100`'s own MAIN MENU test pattern) plus an Inspection pass
  on LEGEND's exact tile/label layout (GDS-08 §11 leaves precise coordinates to `07`/`08`).
- **Open Questions:** None surfaced yet — first specified at `06-feature-specification`.

## FEAT-6100 — Aesthetic & Biome-Transition Compliance (new — not yet implemented)

> **Forward reference (metadata only):** specified by
> [FS-106](../features/FS-106-aesthetic-biome-transition-compliance.md) (2026-07-10). No Open
> Questions — the standard (GDS-08 delta §7/§8) and review process (`09-content-review`) both
> already exist.

- **Feature ID:** FEAT-6100
- **Title:** Aesthetic & Biome-Transition Compliance
- **Purpose:** Give `09-content-review`'s existing "does this screen read well" judgment a
  written standard to check against — craft rules for tile/sprite art and a palette-stepping
  strategy for grammar-adjacent biome families.
- **Description:** Formalizes NFR-6500/NFR-6510: every tile/sprite (new or existing) must satisfy
  GDS-08 delta §7's craft checklist (silhouette-first, per-part color budgeting, no
  anti-aliasing); every rendered screen must satisfy the clean-screen rules (no undefined tiles,
  no illegal adjacency pairs); and grammar-legal adjacent biome families' assigned palettes must
  read as color-family-related (e.g. water-blues stepping toward beach-sands), not arbitrary.
- **Scope:** The compliance *standard* and its review process — this Feature is a verification/
  quality-gate capability, not new player-visible behavior of its own (an "internally complete
  system capability" per this stage's allowance, the same framing `FEAT-7000` uses). Explicitly
  **excludes** *which* biomes are adjacent (`FEAT-9000`'s grammar-legal generation) and *how* a
  screen is composed structurally (`FEAT-4100`'s one-biome-per-screen rule) — this Feature judges
  the aesthetic quality of what those two produce.
- **Included Requirements:** NFR-6500, NFR-6510.
- **Excluded Requirements:** FR-4300/FR-4310 (the structural constraints being judged, not this
  Feature's own scope — `FEAT-4100`/`FEAT-9000`).
- **Dependencies:** FEAT-4100 (needs biome-family screen assignments to exist before their palette-
  stepping can be judged); FEAT-6000 (extends its existing presentation Feature with a written
  craft standard, rather than introducing a new rendering mechanism).
- **Dependent Features:** None.
- **Affected Modules:** None directly — this Feature is a review-process capability
  (`09-content-review`'s existing process, applied against GDS-08 delta §7/§8's checklist), not a
  code change. Any future content package (`tiles.py`/`tilemaps.py`) is judged against it, not
  modified by it.
- **Related ADRs:** ADR-0009 (biome-family adjacency is what NFR-6510 judges the palette-stepping
  of).
- **User Value:** High — indirectly, via MSTR-001 C8/D4's "every screen clean" quality bar, which
  this Feature is the first formal check against.
- **Technical Value:** Low — no new mechanism; a written standard applied to an existing review
  process.
- **Complexity:** Low — the standard (GDS-08 delta §7/§8) is already authored; this Feature's own
  work is applying it, not inventing it.
- **Risk:** Low — NFR-6510 is explicitly a "Should," not a hard functional gate (a design-quality
  guideline within the existing 8-palette budget); NFR-6500's mechanically-checkable subset
  (undefined tiles, illegal seam pairs) can be automated, but the craft judgment itself remains
  `09-content-review`'s existing human/inspection process, not a new automated check.
- **Suggested Verification Strategy:** Inspection (`09-content-review`'s existing process,
  extended to this checklist) for the craft/palette-stepping judgment; Test for the
  mechanically-checkable subset (undefined tile indices, illegal adjacency pairs).
- **Open Questions:** None surfaced yet.

## Requirement-to-Feature tally (completeness check)

**Bootstrap baseline:** 25 `FR-xxxx` + 11 `NFR-xxxx` = 36 requirement IDs, all owned by exactly
one of the original eight Features (unchanged by this delta). **Procgen-world increment delta**
(2026-07-09 RQ-01…04): 11 new `FR-xxxx` + 6 new `NFR-xxxx` = 17 requirement IDs, all owned by
exactly one of the five new Features above. **Total: 53 requirement IDs**, every one assigned to
exactly one Feature project-wide (verified by direct tally, restated in
[FP-05](05-feature-review.md)'s review rather than only asserted here).
