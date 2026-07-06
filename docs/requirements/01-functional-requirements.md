# RQ-01 — Functional Requirements

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by `04-requirements-engineering`.
> Derives from [GDS-05](../architecture/05-functional-requirements.md)'s six capability groupings
> (C1–C6) — this document formalizes each into numbered, testable `FR-xxxx` requirements per
> [GDS-10](../architecture/10-requirements-traceability-matrix.md) §3's stated contract: *cite
> back to the specific GDS-05 grouping each requirement formalizes, don't restate the capability
> from scratch.* Priority scale used throughout: **Must** (required for the shipped game to
> function as-built) / **Should** (a real gap or open question, not yet a defect) / **Could**
> (not applicable to any requirement below — no optional-scope FRs exist in the as-built
> baseline).

## FR-1000 — Game states & transitions

*(formalizes [GDS-05](../architecture/05-functional-requirements.md) C1, [GDS-01](../architecture/01-concept-of-play.md) §4)*

### FR-1100 — Six-state game-state machine

- **ID:** FR-1100
- **Title:** The system shall implement a six-state game-state machine.
- **Description:** The system shall represent exactly six mutually exclusive game states: TITLE,
  INTRO, PLAYING, SAVE, MAP, VICTORY.
- **Rationale:** GDS-01 §4's state diagram; GDS-05 C1.
- **Priority:** Must
- **Inputs:** None (structural requirement).
- **Outputs:** A single current-state value, always exactly one of the six.
- **Preconditions:** None.
- **Postconditions:** The system is always in exactly one of the six named states.
- **Acceptance Criteria:** At any observable point in play, the current state is one of {TITLE,
  INTRO, PLAYING, SAVE, MAP, VICTORY} and no other value.
- **Dependencies:** None.
- **Verification Method:** Test (state value inspection at each transition).
- **Source Documents:** GDS-01 §4; GDS-05 C1.
- **Related ADRs:** None.
- **Notes:** None.

### FR-1110 — Clean-boot start state

- **ID:** FR-1110
- **Title:** The system shall start in TITLE on a clean boot (no valid save present).
- **Description:** On power-on/reset with no valid battery save found, the system shall enter
  TITLE as its initial state.
- **Rationale:** GDS-01 §4; GDS-05 C1.
- **Priority:** Must
- **Inputs:** Power-on/reset event; SRAM save-validity check (FR-5100).
- **Outputs:** State = TITLE.
- **Preconditions:** No valid save magic present in SRAM.
- **Postconditions:** State = TITLE.
- **Acceptance Criteria:** Given SRAM contains no valid save magic, after boot the state equals
  TITLE.
- **Dependencies:** FR-5100 (save-validity detection).
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4; GDS-05 C1.
- **Related ADRs:** None.
- **Notes:** `test_rom.py` T4.1 exercises this path but its surrounding suite context (T4) is not
  cited as current-compliance evidence per BL-0006 — this FR is sourced from the direct
  `asm_game.py` read GDS-01/GDS-05 already performed, not from T4's assertions.

### FR-1120 — Auto-load-on-boot bypass

- **ID:** FR-1120
- **Title:** The system shall bypass TITLE/INTRO and enter PLAYING directly when a valid save
  exists at boot.
- **Description:** On power-on/reset, if a valid battery save is found (FR-5100), the system
  shall restore the saved game data and transition directly to PLAYING, skipping TITLE and INTRO
  entirely.
- **Rationale:** GDS-01 §4 ("boot, valid save found ... skips TITLE/INTRO entirely"); GDS-05 C1.
- **Priority:** Must
- **Inputs:** Power-on/reset event; SRAM save-validity check.
- **Outputs:** State = PLAYING; restored player/zone/score/carrot state (FR-5200).
- **Preconditions:** A valid save (magic bytes present) exists in SRAM.
- **Postconditions:** State = PLAYING; game state matches the restored save fields.
- **Acceptance Criteria:** Given a valid save exists, after boot the state equals PLAYING and
  TITLE/INTRO are never observably entered.
- **Dependencies:** FR-5100, FR-5200.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4; GDS-05 C1.
- **Related ADRs:** ADR-0006 (MBC1+RAM+BATTERY cart type).
- **Notes:** None.

### FR-1130 — TITLE → INTRO → PLAYING transition

- **ID:** FR-1130
- **Title:** The system shall transition TITLE → INTRO on START, then INTRO → PLAYING on A.
- **Description:** From TITLE, pressing START shall transition to INTRO. From INTRO, pressing A
  shall transition to PLAYING.
- **Rationale:** GDS-01 §4's state diagram; GDS-05 C1.
- **Priority:** Must
- **Inputs:** START button press (in TITLE); A button press (in INTRO).
- **Outputs:** State transitions TITLE→INTRO, then INTRO→PLAYING.
- **Preconditions:** Current state is TITLE (for the first transition) or INTRO (for the second).
- **Postconditions:** State advances exactly one step per the diagram.
- **Acceptance Criteria:** From TITLE, START press results in state = INTRO. From INTRO, A press
  results in state = PLAYING.
- **Dependencies:** FR-1100.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4.
- **Related ADRs:** None.
- **Notes:** None.

### FR-1140 — PLAYING ↔ SAVE transition

- **ID:** FR-1140
- **Title:** The system shall transition PLAYING → SAVE on START, and SAVE → PLAYING on A or B.
- **Description:** From PLAYING, pressing START shall transition to SAVE. From SAVE, pressing
  either A or B shall return to PLAYING.
- **Rationale:** GDS-01 §4's state diagram; GDS-05 C1, C5.
- **Priority:** Must
- **Inputs:** START press (in PLAYING); A or B press (in SAVE).
- **Outputs:** State transitions PLAYING→SAVE, SAVE→PLAYING.
- **Preconditions:** Current state is PLAYING or SAVE respectively.
- **Postconditions:** State transitions as specified; an A press in SAVE additionally commits the
  save (FR-5100).
- **Acceptance Criteria:** From PLAYING, START press results in state = SAVE. From SAVE, A or B
  press results in state = PLAYING.
- **Dependencies:** FR-1100, FR-5100.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4.
- **Related ADRs:** None.
- **Notes:** None.

### FR-1150 — PLAYING ↔ MAP transition

- **ID:** FR-1150
- **Title:** The system shall transition PLAYING → MAP on SELECT, and MAP → PLAYING on B.
- **Description:** From PLAYING, pressing SELECT shall transition to MAP. From MAP, pressing B
  shall return to PLAYING.
- **Rationale:** GDS-01 §4's state diagram; GDS-05 C1, C6.
- **Priority:** Must
- **Inputs:** SELECT press (in PLAYING); B press (in MAP).
- **Outputs:** State transitions PLAYING→MAP, MAP→PLAYING.
- **Preconditions:** Current state is PLAYING or MAP respectively.
- **Postconditions:** State transitions as specified.
- **Acceptance Criteria:** From PLAYING, SELECT press results in state = MAP. From MAP, B press
  results in state = PLAYING.
- **Dependencies:** FR-1100.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4.
- **Related ADRs:** None.
- **Notes:** None.

### FR-1160 — PLAYING → VICTORY transition

- **ID:** FR-1160
- **Title:** The system shall transition PLAYING → VICTORY the instant the victory condition is
  met, then VICTORY → TITLE on A.
- **Description:** From PLAYING, the moment CarrotCount reaches 9 the system shall transition to
  VICTORY, regardless of any other concurrent input. From VICTORY, pressing A shall transition
  back to TITLE.
- **Rationale:** GDS-01 §4's state diagram; GDS-05 C1, C4.
- **Priority:** Must
- **Inputs:** CarrotCount reaching 9 (in PLAYING); A press (in VICTORY).
- **Outputs:** State transitions PLAYING→VICTORY, VICTORY→TITLE.
- **Preconditions:** Current state is PLAYING (for the first transition) with CarrotCount == 9;
  current state is VICTORY (for the second).
- **Postconditions:** State transitions as specified.
- **Acceptance Criteria:** The instant CarrotCount reaches 9 while in PLAYING, state becomes
  VICTORY (see FR-3300 for the underlying victory condition). From VICTORY, A press results in
  state = TITLE.
- **Dependencies:** FR-1100, FR-3300.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4; GDS-05 C4.
- **Related ADRs:** None.
- **Notes:** None.

## FR-2000 — Player movement & zone traversal

*(formalizes [GDS-05](../architecture/05-functional-requirements.md) C2)*

### FR-2100 — Continuous fixed-speed movement while held

- **ID:** FR-2100
- **Title:** The system shall move the player continuously at a fixed speed while a directional
  input is held.
- **Description:** While the player holds a directional input (up/down/left/right) during
  PLAYING, the system shall move the player's on-screen position continuously in that direction
  at a fixed per-frame speed, for as long as the input is held.
- **Rationale:** GDS-05 C2; R202 (8-bit game feel — fixed-speed movement convention).
- **Priority:** Must
- **Inputs:** Directional joypad input (held).
- **Outputs:** Continuously updated player position in the held direction.
- **Preconditions:** State is PLAYING; movement in the held direction is not blocked by a zone
  boundary with no neighbor (FR-2300).
- **Postconditions:** Player position advances one fixed increment per frame in the held
  direction until released or blocked.
- **Acceptance Criteria:** Holding a directional input for N frames (where movement is
  unobstructed) results in the player's position advancing by exactly N times the fixed per-frame
  speed in that direction.
- **Dependencies:** FR-2300.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C2; R202.
- **Related ADRs:** None.
- **Notes:** The exact per-frame speed value is a Data Model (GDS-07) concern, not restated here
  per the architecture-independence writing rule.

### FR-2200 — Facing-direction tracking

- **ID:** FR-2200
- **Title:** The system shall track and update the player's current facing direction.
- **Description:** The system shall record which of the four directions the player last moved in,
  updating it whenever a new directional input changes the facing.
- **Rationale:** GDS-04 (Player entity has a Direction attribute); GDS-05 C2 (implied by
  directional movement).
- **Priority:** Must
- **Inputs:** Directional joypad input.
- **Outputs:** Current facing direction (one of four).
- **Preconditions:** State is PLAYING.
- **Postconditions:** Facing direction matches the most recently pressed movement direction.
- **Acceptance Criteria:** After moving in a given direction, the recorded facing direction equals
  that direction.
- **Dependencies:** FR-2100.
- **Verification Method:** Test.
- **Source Documents:** GDS-04; GDS-05 C2.
- **Related ADRs:** None.
- **Notes:** Facing direction is **not** part of the persisted save set — see FR-5210 and its
  cross-reference to BL-0018.

### FR-2300 — Zone-boundary transition on valid neighbor

- **ID:** FR-2300
- **Title:** The system shall transition to the adjacent zone when the player crosses a screen
  edge with a valid neighboring zone.
- **Description:** When the player's position crosses the edge of the current zone's screen in a
  direction that has a valid neighboring zone in the 3×3 grid, the system shall transition play to
  that neighboring zone, placing the player at the corresponding entry position on the new zone's
  screen.
- **Rationale:** GDS-05 C2; GDS-04 (Zone's 3×3 grid position); GDS-01 §4 (zone traversal within
  PLAYING).
- **Priority:** Must
- **Inputs:** Player position crossing a screen edge; the 3×3 grid adjacency of the current zone.
- **Outputs:** Current zone changes to the neighbor; player repositioned to the entry point of the
  new zone's screen.
- **Preconditions:** State is PLAYING; the crossed edge has a valid neighbor (not a grid boundary).
- **Postconditions:** CurrentZone equals the neighboring zone; the new zone's screen is displayed.
- **Acceptance Criteria:** Crossing the edge of a zone screen toward a direction with a defined
  neighbor in the 3×3 grid results in CurrentZone updating to that neighbor.
- **Dependencies:** FR-2100.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C2; GDS-04.
- **Related ADRs:** None.
- **Notes:** None.

### FR-2310 — No transition at grid boundary

- **ID:** FR-2310
- **Title:** The system shall not transition zones toward a 3×3 grid edge with no neighbor.
- **Description:** When the player's position reaches the edge of a zone screen in a direction
  with no neighboring zone (a row/column boundary of the 3×3 grid), the system shall not perform a
  zone transition; the player's movement in that direction shall be halted at the boundary.
- **Rationale:** GDS-05 C2 ("No transition shall occur toward a grid edge with no neighbor").
- **Priority:** Must
- **Inputs:** Player position reaching a screen edge with no grid neighbor.
- **Outputs:** No zone transition; player position clamped at the boundary.
- **Preconditions:** State is PLAYING; the approached edge has no valid neighbor.
- **Postconditions:** CurrentZone is unchanged; player position does not exceed the screen
  boundary.
- **Acceptance Criteria:** Given the player is in a zone at a grid edge (e.g. row 0 or column 2),
  moving toward the direction with no neighbor results in no CurrentZone change and the player's
  position remaining within the screen bounds.
- **Dependencies:** FR-2300.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C2.
- **Related ADRs:** None.
- **Notes:** None.

### FR-2320 — On-screen transition-edge signaling

- **ID:** FR-2320
- **Title:** The system shall signal a valid zone-transition edge with an on-screen arrow.
- **Description:** For every screen edge that has a valid neighboring zone, the system shall
  display an on-screen arrow indicator at that edge during PLAYING.
- **Rationale:** GDS-05 C2 ("signaled by an on-screen arrow"); R203 (screen composition
  conventions).
- **Priority:** Must
- **Inputs:** The current zone's grid adjacency.
- **Outputs:** An arrow tile rendered at each edge with a valid neighbor; no arrow at edges with
  none.
- **Preconditions:** State is PLAYING.
- **Postconditions:** Arrow presence at each screen edge matches that edge's neighbor validity.
- **Acceptance Criteria:** For a given zone, an arrow tile is rendered at exactly the edges that
  have a defined neighbor in the 3×3 grid, and at no others.
- **Dependencies:** None.
- **Verification Method:** Test (tilemap inspection) / Inspection (visual).
- **Source Documents:** GDS-05 C2; R203.
- **Related ADRs:** None.
- **Notes:** None.

## FR-3000 — Collectibles, score & victory

*(formalizes [GDS-05](../architecture/05-functional-requirements.md) C3, C4)*

### FR-3100 — Collection-proximity detection

- **ID:** FR-3100
- **Title:** The system shall detect collection when the player is within the proximity threshold
  of a Collectible on both axes.
- **Description:** During PLAYING, the system shall detect that the player has collected a
  Collectible when the player's position is within the defined proximity threshold of the
  Collectible's position on both the horizontal and vertical axes independently.
- **Rationale:** GDS-05 C3 ("within 10px on both axes ... two independent axis checks"); R202.
- **Priority:** Must
- **Inputs:** Player position; active Collectible positions in the current zone.
- **Outputs:** A collection event for each Collectible meeting the proximity threshold.
- **Preconditions:** State is PLAYING; the Collectible is active (not yet collected).
- **Postconditions:** A collection event fires exactly once per Collectible when the threshold is
  first met.
- **Acceptance Criteria:** When the player's position is within the proximity threshold of an
  active Collectible on both axes simultaneously, a collection event fires for that Collectible.
- **Dependencies:** None.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C3; R202.
- **Related ADRs:** None.
- **Notes:** The exact threshold value (10px) is a Data Model (GDS-07)/behavior fact cited by
  GDS-05, not restated as a hardcoded number requirement here beyond what's needed for testability
  — Acceptance Criteria may cite it directly since GDS-05 already confirms it against source.

### FR-3200 — ScoreItem collection increments Score

- **ID:** FR-3200
- **Title:** The system shall increment Score and remove the item from play when a ScoreItem is
  collected.
- **Description:** On a collection event (FR-3100) for a ScoreItem (star or flower), the system
  shall increment the player's Score by the item's value and remove that item from further play
  in its zone.
- **Rationale:** GDS-05 C3; GDS-04 (ScoreItem entity).
- **Priority:** Must
- **Inputs:** A collection event for a ScoreItem.
- **Outputs:** Score incremented; the collected ScoreItem no longer rendered or collectible.
- **Preconditions:** The ScoreItem is active.
- **Postconditions:** Score reflects the increment; the ScoreItem is permanently inactive for the
  remainder of that play session (see FR-5210/BL-0018 regarding persistence across save/load).
- **Acceptance Criteria:** Collecting a ScoreItem increases Score by its defined value and the
  item is not collectible again in the same session.
- **Dependencies:** FR-3100.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C3.
- **Related ADRs:** None.
- **Notes:** None.

### FR-3210 — Carrot collection sets zone flag and increments CarrotCount

- **ID:** FR-3210
- **Title:** The system shall set the collecting zone's carrot flag, increment CarrotCount, and
  remove the item from play when a Carrot is collected.
- **Description:** On a collection event (FR-3100) for a Carrot, the system shall set that zone's
  flag in CarrotFlags, increment CarrotCount by one, and remove the Carrot from further play.
- **Rationale:** GDS-05 C3; GDS-04 (Carrot entity, exactly one per zone).
- **Priority:** Must
- **Inputs:** A collection event for a Carrot.
- **Outputs:** That zone's CarrotFlags bit set; CarrotCount incremented by one; the Carrot no
  longer rendered or collectible.
- **Preconditions:** The Carrot is active; that zone's CarrotFlags bit is not already set.
- **Postconditions:** CarrotFlags[zone] = true; CarrotCount reflects the increment.
- **Acceptance Criteria:** Collecting a zone's Carrot sets that zone's flag and increases
  CarrotCount by exactly one, once.
- **Dependencies:** FR-3100.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C3.
- **Related ADRs:** None.
- **Notes:** Per BL-0017 (open, see RQ-03): the "exactly one Carrot per zone" invariant is not
  code-enforced today — this requirement describes the collection behavior assuming that
  invariant holds, and does not itself assert the invariant's enforcement (see the Candidate
  Requirements section).

### FR-3300 — Victory condition

- **ID:** FR-3300
- **Title:** The system shall trigger victory the instant CarrotCount reaches 9.
- **Description:** During PLAYING, the instant CarrotCount reaches 9 (read directly, not derived
  by summing CarrotFlags at check-time), the system shall trigger the PLAYING → VICTORY
  transition (FR-1160).
- **Rationale:** GDS-05 C4 ("reads CarrotCount directly ... not derived from summing CarrotFlags
  at check-time").
- **Priority:** Must
- **Inputs:** CarrotCount value.
- **Outputs:** Victory transition trigger (FR-1160).
- **Preconditions:** State is PLAYING; CarrotCount == 9.
- **Postconditions:** The victory transition fires.
- **Acceptance Criteria:** Whenever CarrotCount reaches 9 while in PLAYING, the system transitions
  to VICTORY within the same frame it is checked.
- **Dependencies:** FR-3210, FR-1160.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C4.
- **Related ADRs:** None.
- **Notes:** None.

## FR-4000 — Zones & screens

*(formalizes [GDS-05](../architecture/05-functional-requirements.md) C6's structural half; see
FR-6000 for the presentation half)*

### FR-4100 — Fixed 3×3 zone grid

- **ID:** FR-4100
- **Title:** The system shall define exactly nine zones arranged in a fixed 3×3 grid.
- **Description:** The system shall define nine distinct zones (Beach, Forest, Mountain, Lake,
  Village, Cave, Desert, Plains, Castle), each occupying a fixed position in a 3×3 grid.
- **Rationale:** GDS-04 (Zone entity); GDS-05 C2 (referenced grid).
- **Priority:** Must
- **Inputs:** None (structural).
- **Outputs:** Nine addressable zones, each with a fixed grid position.
- **Preconditions:** None.
- **Postconditions:** Exactly nine zones exist, each reachable via zone traversal (FR-2300).
- **Acceptance Criteria:** The set of zones the player can traverse to has exactly nine distinct
  members, matching the named list, each at its documented grid position.
- **Dependencies:** None.
- **Verification Method:** Test / Inspection.
- **Source Documents:** GDS-04; GDS-01 §3.
- **Related ADRs:** None.
- **Notes:** None.

### FR-4200 — Fourteen total screens

- **ID:** FR-4200
- **Title:** The system shall define fourteen total screens: nine zone screens plus five UI
  screens.
- **Description:** In addition to the nine zone screens (FR-4100), the system shall define five
  non-zone UI screens: Title, Intro, Save, Map, Victory — one rendered per corresponding game
  state.
- **Rationale:** GDS-04 (Screen entity, ×14 total); GDS-05 C6.
- **Priority:** Must
- **Inputs:** Current game state (FR-1100).
- **Outputs:** The screen corresponding to the current state (or current zone, for PLAYING) is
  rendered.
- **Preconditions:** None.
- **Postconditions:** Exactly one of the fourteen screens is rendered at any time, matching the
  current state/zone.
- **Acceptance Criteria:** For each of the six states, the rendered screen matches: TITLE→Title
  screen, INTRO→Intro screen, PLAYING→the current zone's screen, SAVE→Save screen, MAP→Map screen,
  VICTORY→Victory screen.
- **Dependencies:** FR-1100, FR-4100.
- **Verification Method:** Test.
- **Source Documents:** GDS-04; GDS-05 C6.
- **Related ADRs:** None.
- **Notes:** None.

## FR-5000 — Save / load (SRAM)

*(formalizes [GDS-05](../architecture/05-functional-requirements.md) C5)*

### FR-5100 — Explicit player-initiated save

- **ID:** FR-5100
- **Title:** The system shall persist the defined save-field set to battery-backed SRAM on an
  explicit player-initiated SAVE-menu action.
- **Description:** When the player confirms a save from the SAVE state (FR-1140), the system
  shall write the current values of {CurrentZone, PlayerPosition, CarrotCount, Score,
  CarrotFlags[9]} to battery-backed SRAM, preceded by a valid-save marker.
- **Rationale:** GDS-05 C5; R106; R205.
- **Priority:** Must
- **Inputs:** Player save-confirm action (in SAVE); current values of the save-field set.
- **Outputs:** SRAM updated with the save-field set and a valid-save marker.
- **Preconditions:** State is SAVE; the save-confirm input is received.
- **Postconditions:** SRAM contains the save-field set's current values and is detectable as valid
  on a subsequent boot (FR-1120).
- **Acceptance Criteria:** After a save-confirm action, reading SRAM yields exactly the current
  in-memory values of {CurrentZone, PlayerPosition, CarrotCount, Score, CarrotFlags[9]}, and a
  subsequent boot detects the save as valid.
- **Dependencies:** FR-1140.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C5; GDS-06 N3.
- **Related ADRs:** ADR-0006 (MBC1+RAM+BATTERY, `BUNY` magic).
- **Notes:** None.

### FR-5200 — Restore save-field set on valid-save boot

- **ID:** FR-5200
- **Title:** The system shall restore the exact save-field set from SRAM when a valid save is
  detected at boot.
- **Description:** On boot, if SRAM contains a valid-save marker, the system shall restore
  {CurrentZone, PlayerPosition, CarrotCount, Score, CarrotFlags[9]} from SRAM before entering
  PLAYING (FR-1120).
- **Rationale:** GDS-05 C5; R106.
- **Priority:** Must
- **Inputs:** SRAM contents at boot.
- **Outputs:** In-memory game state fields set to the restored values.
- **Preconditions:** SRAM contains a valid-save marker.
- **Postconditions:** In-memory {CurrentZone, PlayerPosition, CarrotCount, Score, CarrotFlags[9]}
  exactly match the values last written by FR-5100.
- **Acceptance Criteria:** Given SRAM holds a save written by FR-5100, after boot the in-memory
  save-field set exactly equals the values at the time of that save.
- **Dependencies:** FR-1120, FR-5100.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C5; GDS-06 N3.
- **Related ADRs:** ADR-0006.
- **Notes:** None.

### FR-5210 — Fields explicitly outside the persisted save set

- **ID:** FR-5210
- **Title:** The system shall leave player facing direction, animation frame, and per-zone
  ScoreItem collected-state to their default values on every restore.
- **Description:** Because these fields are not part of the save-field set (FR-5100/FR-5200), a
  restore shall always yield a default facing direction and animation frame, and every zone's
  ScoreItems shall be restored to "all present" regardless of pre-save collection state.
- **Rationale:** GDS-05 C5 (explicitly flags this as not persisted); direct read of the save
  routine's field list.
- **Priority:** Must (as-built behavior) — **flagged Should-revisit**: whether this is the
  *intended* scope is unresolved; see RQ-03 and BL-0018.
- **Inputs:** A completed restore (FR-5200).
- **Outputs:** Default facing/animation frame; all zones' ScoreItems marked present.
- **Preconditions:** A restore has just completed.
- **Postconditions:** Facing/frame equal their boot-time defaults; every ScoreItem in every zone
  is active regardless of prior collection.
- **Acceptance Criteria:** After a restore, the player's facing direction and animation frame
  equal their documented defaults, and every ScoreItem in every zone is collectible again even if
  it was collected before the save.
- **Dependencies:** FR-5200.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C5; BL-0018.
- **Related ADRs:** None.
- **Notes:** **This requirement documents current as-built behavior, not an endorsed design.**
  RQ-03 flags the open question of whether this is intended scope. Do not treat this FR as license
  to close BL-0018 without a user/design decision.

## FR-6000 — Presentation

*(formalizes [GDS-05](../architecture/05-functional-requirements.md) C6's rendering half)*

### FR-6100 — Zone screen composition

- **ID:** FR-6100
- **Title:** The system shall render each zone as a static single-screen composition of terrain
  and landmark elements.
- **Description:** For every zone, the system shall render a single, non-scrolling screen
  combining a terrain fill with 3–7 hand-placed landmark elements giving the zone its visual
  identity.
- **Rationale:** GDS-05 C6; R203; GDS-08 §1.
- **Priority:** Must
- **Inputs:** Current zone (FR-2300).
- **Outputs:** The zone's rendered screen.
- **Preconditions:** State is PLAYING.
- **Postconditions:** The displayed screen matches the current zone's authored composition.
- **Acceptance Criteria:** For each of the nine zones, the rendered screen's tile content matches
  that zone's authored terrain/landmark data.
- **Dependencies:** FR-4100.
- **Verification Method:** Test / Inspection.
- **Source Documents:** GDS-05 C6; GDS-08 §1.
- **Related ADRs:** None.
- **Notes:** None.

### FR-6200 — Persistent row-0 HUD

- **ID:** FR-6200
- **Title:** The system shall render a persistent row-0 HUD showing carrot progress and score on
  every zone screen.
- **Description:** On every zone screen during PLAYING, the system shall render a static HUD in
  row 0 showing carrot progress (as "N-9") and the current Score.
- **Rationale:** GDS-05 C6; R204; GDS-08 §3.
- **Priority:** Must
- **Inputs:** CarrotCount; Score.
- **Outputs:** Row-0 HUD tiles reflecting current CarrotCount and Score.
- **Preconditions:** State is PLAYING.
- **Postconditions:** The HUD's displayed carrot progress and score match the current in-memory
  values.
- **Acceptance Criteria:** On any zone screen, the row-0 HUD's carrot-progress digit(s) equal
  CarrotCount and its score digits equal Score.
- **Dependencies:** FR-3200, FR-3210.
- **Verification Method:** Test / Inspection.
- **Source Documents:** GDS-05 C6; GDS-08 §3.
- **Related ADRs:** None.
- **Notes:** The HUD's underlying VRAM-write timing is a non-functional concern — see NFR-1200
  (GDS-06 N2, BL-0003/BL-0008), not restated here.

### FR-6300 — Five non-zone UI screens

- **ID:** FR-6300
- **Title:** The system shall render five distinct, non-zone UI screens: Title, Intro, Save, Map,
  Victory.
- **Description:** For each of the five non-PLAYING states, the system shall render that state's
  own bespoke screen layout (not a zone screen).
- **Rationale:** GDS-05 C6; GDS-04 (five UI screens).
- **Priority:** Must
- **Inputs:** Current game state (FR-1100).
- **Outputs:** The UI screen matching the current state.
- **Preconditions:** State is one of {TITLE, INTRO, SAVE, MAP, VICTORY}.
- **Postconditions:** The rendered screen is that state's own distinct layout, not a zone screen.
- **Acceptance Criteria:** For each of the five non-PLAYING states, the rendered screen's tile
  content matches that state's own authored UI layout and differs from every zone screen's
  layout.
- **Dependencies:** FR-1100.
- **Verification Method:** Test / Inspection.
- **Source Documents:** GDS-05 C6; GDS-04.
- **Related ADRs:** None.
- **Notes:** None.

## Candidate Requirements

*(untraceable to a current source, or contingent on an unresolved design decision — explicitly
excluded from the numbered baseline above; marked `CANDIDATE — NOT BASELINED` in RQ-04)*

### CR-01 — Full save-field persistence (facing/frame/per-zone ScoreItem state)

- **Description:** Extend the persisted save-field set (FR-5100/FR-5200) to also include player
  facing direction, animation frame, and per-zone ScoreItem collected-state.
- **Why excluded:** No source document states this as required; FR-5210 documents the opposite
  as current as-built behavior. This is a plausible *future* requirement contingent on BL-0018
  being resolved toward "yes, persist it" rather than "no, this is intentional."
- **Disposition:** Held pending a design decision (RQ-03 flags this; owner: the user, or
  `03-architecture-design-synthesis` if reopened at the architecture level).

### CR-02 — Build-time or runtime enforcement of "exactly one Carrot per zone"

- **Description:** Add an explicit check (build-time validation of `ZONE_COLLECTS`, or a runtime
  assertion) that each zone's collectible list contains exactly one Carrot.
- **Why excluded:** No source document requires this invariant be *enforced* — GDS-04/GDS-05
  describe it as a fact that currently holds, not a requirement that it be checked. BL-0017 is the
  tracking finding.
- **Disposition:** SCHEDULED per BL-0017 — recommended as a Verification Checklist item on any
  future package touching `ZONE_COLLECTS`, not a standalone requirement today.
