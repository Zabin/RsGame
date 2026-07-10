# RQ-01 — Functional Requirements

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment, FR-1170–9200 — see Changelog).** Owned by `04-requirements-engineering`.
> Derives from [GDS-05](../architecture/05-functional-requirements.md)'s six capability groupings
> (C1–C6) — this document formalizes each into numbered, testable `FR-xxxx` requirements per
> [GDS-10](../architecture/10-requirements-traceability-matrix.md) §3's stated contract: *cite
> back to the specific GDS-05 grouping each requirement formalizes, don't restate the capability
> from scratch.* Priority scale used throughout: **Must** (required for the shipped game to
> function as-built) / **Should** (a real gap or open question, not yet a defect) / **Could**
> (not applicable to any requirement below — no optional-scope FRs exist in the as-built
> baseline).

## Changelog

- **2026-07-07 — BL-0018 resolved by explicit user decision.** The user determined: (1) player
  facing direction and animation frame are **not important** — no persistence requirement added;
  (2) per-zone `ScoreItem` collected-state **should persist** across save/load. Accordingly:
  CR-01 (below) is split — its facing/frame half is **REJECTED**, its ScoreItem half is
  **APPROVED** and promoted to **FR-5220** (new). FR-5210 is reworded to reflect that only
  facing/frame remain outside the persisted save set. See `BL-0018` in
  `docs/pipeline/backlog.md` (now `DONE`).
- **2026-07-09 — Delta for the adopted aesthetics/visual-story-narrative/procgen-world-map
  increment** ([PLAN-requirements-aesthetics-story-map.md](../pipeline/PLAN-requirements-aesthetics-story-map.md),
  Phase 4; grounds `MSTR-001` v3.0's C9/C10, `ADR-0009`/`0010`, and the GDS-01/04 deltas — see
  `BL-0030`/`BL-0031`). **Ten new FRs added, all describing target behavior the increment's
  future implementation packages build toward — none shipped yet** (the same forward-looking
  framing `MSTR-001` §8 already applies to C7/C8/C9/C10 themselves): **FR-1170/1180/1190** (main
  menu, seed/scale entry, exit-to-main-menu-with-autosave — supersede `FR-1120`'s auto-load
  behavior and `FR-1160`'s VICTORY→TITLE transition once implemented, both left unmodified below
  since they remain accurate for the *currently shipped* game); **FR-3220** (item-agnostic
  KeyItem collection, generalizing `FR-3210`'s Carrot-specific wording); **FR-4300/4310**
  (one-biome-per-screen structural rule, grammar-valid adjacency); **FR-9100–9200** (a new
  World Generation group: deterministic generation, new-game-only immutable seed/scale entry,
  full reachability, one-KeyItem-per-region as a generator-guaranteed property, save-format
  extension). **No FR was added for text dialogue** — `MSTR-001` D1/§4 records it as a
  deliberately non-required (not ruled out) non-goal at this vision's date; see FR-9100's Notes.
- **2026-07-10 — 04-delta batch (`BL-0020`/`BL-0022`).** **FR-6400** added (new): player/
  collectible sprite (OAM) rendering, shipped and tested (`test_rom.py` T6) but never formally
  stated as a requirement — surfaced by `05-feature-decomposition`'s FP-05 review (finding #1,
  run #19). **FR-3200**'s postcondition corrected: it previously claimed a collected `ScoreItem`
  is "permanently inactive for the remainder of that play session" — direct code reading of
  `setup_zone_collects` (surfaced by `06-feature-specification`'s FS-101 authoring, run #20)
  shows `ScoreItem`s actually respawn on every zone re-entry within a session; only `Carrot`s are
  session-permanent. The corrected text matches the shipped code exactly (and matches what
  `FR-5220`/`IP-1010` already build on top of).

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
- **Notes:** **Target-state pointer (2026-07-09):** `MSTR-001` C2 (amended v3.0) and
  [GDS-01](../architecture/01-concept-of-play.md) §2a/§4a commit to superseding this auto-load
  behavior with player-initiated loading via a new MAIN MENU state (see FR-1170/1180). This FR
  remains accurate for the *currently shipped* game and is not modified here; it will be
  superseded by a dated revision only once the corresponding implementation package ships (per
  the ladder's delta-update discipline, same pattern `NFR-4000` already uses for its own C7
  supersession trigger).

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
- **Notes:** **Target-state pointer (2026-07-09):** [GDS-01](../architecture/01-concept-of-play.md)
  §4a commits VICTORY's A-press target to MAIN MENU instead of TITLE, following TITLE's own
  supersession (see FR-1170's note). Unmodified here; accurate for the current shipped game.

### FR-1170 — MAIN MENU state (target — 2026-07-09, not yet shipped)

- **ID:** FR-1170
- **Title:** The system shall present a MAIN MENU state on every boot, offering continue and new
  game.
- **Description:** On power-on/reset, the system shall always enter a MAIN MENU state — never
  bypassing it — offering a "continue" option (only if a version-matching save exists) and a
  "new game" option.
- **Rationale:** MSTR-001 C2 (amended v3.0); GDS-01 §2a/§4a; ADR-0010.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** Power-on/reset event; SRAM save-validity and version check.
- **Outputs:** State = MAIN MENU; "continue" option present iff a version-matching save exists.
- **Preconditions:** None (unconditional on boot).
- **Postconditions:** State is MAIN MENU; the menu's option set matches save presence/validity.
- **Acceptance Criteria:** After boot, state always equals MAIN MENU regardless of save presence.
  Given a version-matching save exists, "continue" is offered; given none exists (or its version
  does not match), "continue" is not offered.
- **Dependencies:** FR-1100 (extends the state set to seven states).
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §2a/§4a; ADR-0010.
- **Related ADRs:** ADR-0010.
- **Notes:** Supersedes FR-1120's auto-load bypass once implemented (see FR-1120's own
  target-state pointer). Not yet implemented — no `test_rom.py` coverage exists yet.

### FR-1180 — New-game seed/scale entry and world generation trigger (target — 2026-07-09)

- **ID:** FR-1180
- **Title:** The system shall, on "new game," collect a seed and world-scale value via a
  digit-cursor entry screen, then generate the world before entering INTRO.
- **Description:** From MAIN MENU's "new game" option, the system shall present a digit-cursor
  entry UI for a 16-bit seed and a world-scale value (2–9, default 3), then — on confirmation —
  initialize the world generator from that (seed, scale) pair and transition to INTRO.
- **Rationale:** MSTR-001 C10; GDS-01 §4a; ADR-0009; ADR-0010.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** D-pad (digit/value selection, cursor movement); A (confirm).
- **Outputs:** SEED and WORLD_SCALE set to the entered values; the generated world's region graph
  populated; state = INTRO.
- **Preconditions:** State is MAIN MENU with "new game" selected.
- **Postconditions:** SEED/WORLD_SCALE hold the entered values; a complete, grammar-valid,
  fully-reachable region graph exists (FR-9100/9120/9130); state = INTRO.
- **Acceptance Criteria:** Entering seed S and scale N and confirming results in a generated
  world of exactly N² regions, and state becomes INTRO. Re-entering the same (S, N) pair on a
  separate new-game creation produces an identical region graph (see FR-9100).
- **Dependencies:** FR-1170, FR-9100, FR-9110.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4a; ADR-0009; ADR-0010.
- **Related ADRs:** ADR-0009, ADR-0010.
- **Notes:** A seed value of 0 is normalized to 1 internally (xorshift's nonzero-state
  requirement, per R111/ADR-0010) — the player may still enter 0. Not yet implemented.

### FR-1190 — Exit-to-main-menu with auto-save (target — 2026-07-09)

- **ID:** FR-1190
- **Title:** The system shall offer an exit-to-main-menu option from the SAVE state that
  auto-saves before returning to MAIN MENU.
- **Description:** In addition to FR-1140's existing A(save)/B(cancel) options, the SAVE state
  shall offer a third option that first performs the same save-field write FR-5100 performs, then
  transitions to MAIN MENU (not back to PLAYING).
- **Rationale:** MSTR-001 C2 (amended v3.0), owner decisions D8/D10; GDS-01 §4a.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** The exit-to-main-menu input (in SAVE).
- **Outputs:** SRAM updated with the current save-field set (as FR-5100); state = MAIN MENU.
- **Preconditions:** State is SAVE.
- **Postconditions:** SRAM reflects the pre-exit game state exactly; state = MAIN MENU.
- **Acceptance Criteria:** Selecting exit-to-main-menu from SAVE results in SRAM containing the
  current save-field set (verifiable by a subsequent "continue") and state = MAIN MENU. No
  progress present at the time of exit is ever lost.
- **Dependencies:** FR-1140, FR-1170, FR-5100.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4a.
- **Related ADRs:** None.
- **Notes:** Not yet implemented.

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
- **Postconditions:** Score reflects the increment; the ScoreItem is inactive for the remainder
  of the current zone visit, and its collected-state persists across save/load per FR-5220 (see
  BL-0018, resolved) — but **respawns as active on every zone re-entry within the same session**,
  per the shipped `setup_zone_collects` behavior (corrected 2026-07-10, `BL-0022`; the prior text
  read "permanently inactive for the remainder of that play session," which direct code reading
  during `FS-101`'s authoring (2026-07-07) found does not match the shipped code — only `Carrot`s
  are session-permanent, per FR-3210).
- **Acceptance Criteria:** Collecting a ScoreItem increases Score by its defined value and the
  item is not collectible again until the player re-enters the zone.
- **Dependencies:** FR-3100.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C3; `asm_game.py`'s `setup_zone_collects` (direct code read,
  `BL-0022`).
- **Related ADRs:** None.
- **Notes:** This is the shipped, intentional behavior `IP-1010`/`FS-101` built on top of (not a
  bug in this requirement's own scope) — the farming-abuse risk this respawn created was
  `BL-0023`, fixed by `FR-5220`'s persistence, not by this requirement changing.

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
  Requirements section). **Target-state pointer (2026-07-09):** see FR-3220 for the
  item-agnostic generalization (`MSTR-001` C9/D2) — this FR remains accurate for the currently
  shipped Carrot-specific behavior and is not modified here.

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

### FR-3220 — Item-agnostic KeyItem collection (target — 2026-07-09, generalizes FR-3210)

- **ID:** FR-3220
- **Title:** The system shall set the collecting region's key-item flag, increment KeyItemCount,
  and remove the item from play when a KeyItem is collected.
- **Description:** On a collection event (FR-3100) for a KeyItem, the system shall set that
  region's flag in KeyItemFlags, increment KeyItemCount by one, and remove the KeyItem from
  further play. Behaviorally identical to FR-3210's Carrot-specific rule, generalized to an
  item-agnostic identity — the specific item theme (carrot or otherwise) is a content/theming
  concern (GDS-08 §8), not a functional one.
- **Rationale:** MSTR-001 C9/D2; GDS-04 delta (KeyItem entity); GDS-09 delta.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** A collection event for a KeyItem.
- **Outputs:** That region's KeyItemFlags bit set; KeyItemCount incremented by one; the KeyItem no
  longer rendered or collectible.
- **Preconditions:** The KeyItem is active; that region's KeyItemFlags bit is not already set.
- **Postconditions:** KeyItemFlags[region] = true; KeyItemCount reflects the increment.
- **Acceptance Criteria:** Collecting a region's KeyItem sets that region's flag and increases
  KeyItemCount by exactly one, once.
- **Dependencies:** FR-3100, FR-9130 (one-KeyItem-per-region invariant).
- **Verification Method:** Test.
- **Source Documents:** GDS-04 delta; MSTR-001 C9.
- **Related ADRs:** ADR-0009.
- **Notes:** Generalizes FR-3210 (see that FR's own target-state pointer). Carrots are today's
  shipped instance of KeyItem theming, not a fixed requirement (D2). Not yet implemented.

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

### FR-4300 — One biome per screen (target — 2026-07-09)

- **ID:** FR-4300
- **Title:** The system shall render exactly one biome per region screen — never a blend of two
  biomes within a single screen.
- **Description:** Every generated region's screen shall be composed entirely from one biome
  family's tile set; no screen shall mix tiles from two different biome families.
- **Rationale:** MSTR-001 C9, owner decision D2 (explicit clarification: "flow into each other"
  does not mean two biomes rendered in a single frame); R212; GDS-08 §8.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** A region's generated biome assignment (FR-9100).
- **Outputs:** The region's rendered screen, composed from exactly one biome family's tiles.
- **Preconditions:** None (structural).
- **Postconditions:** Every rendered region screen's tile content is drawn from exactly one biome
  family.
- **Acceptance Criteria:** For every generated region, its screen's tile-family composition
  contains no tile from any biome family other than its assigned one.
- **Dependencies:** FR-9100.
- **Verification Method:** Test (tile-family audit per screen) / Inspection.
- **Source Documents:** GDS-08 §8; R212.
- **Related ADRs:** ADR-0009.
- **Notes:** Not yet implemented.

### FR-4310 — Grammar-valid adjacency only (target — 2026-07-09)

- **ID:** FR-4310
- **Title:** The system shall only generate region adjacencies that appear in the biome-adjacency
  grammar.
- **Description:** For every pair of adjacent generated regions, their biome families' pairing
  shall appear in R212's adjacency grammar table (e.g. water may border beach; water shall never
  border sky directly).
- **Rationale:** MSTR-001 C9; R212; ADR-0009 (enforced by construction, not post-hoc validation).
- **Priority:** Must (target — not yet implemented)
- **Inputs:** The candidate adjacency the generator is about to create.
- **Outputs:** The adjacency is created only if grammar-legal; otherwise the generator selects a
  different candidate.
- **Preconditions:** Generation is in progress (FR-9100).
- **Postconditions:** Every edge in the generated region graph is grammar-legal.
- **Acceptance Criteria:** For any generated world, every adjacent region pair's biome-family
  combination appears in the grammar table; no illegal pairing exists anywhere in the graph.
- **Dependencies:** FR-9100.
- **Verification Method:** Test (property test across a (seed, scale) corpus, per R305's
  extension).
- **Source Documents:** R212; ADR-0009; GDS-04 delta.
- **Related ADRs:** ADR-0009.
- **Notes:** Not yet implemented. This is a generator-*guaranteed* property (enforced during
  generation), not a post-generation check that could fail.

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
- **Title:** The system shall leave player facing direction and animation frame to their default
  values on every restore.
- **Description:** Because these fields are not part of the save-field set (FR-5100/FR-5200), a
  restore shall always yield a default facing direction and animation frame.
- **Rationale:** GDS-05 C5 (originally flagged all three fields as not persisted; per the
  2026-07-07 user decision recorded in this document's Changelog, facing/frame are confirmed
  **not important** and intentionally excluded, while per-zone ScoreItem state is promoted to
  FR-5220 below).
- **Priority:** Must — no longer ambiguous; the user has confirmed this is intended scope, not an
  oversight (BL-0018, closed).
- **Inputs:** A completed restore (FR-5200).
- **Outputs:** Default facing direction and animation frame.
- **Preconditions:** A restore has just completed.
- **Postconditions:** Facing/frame equal their boot-time defaults.
- **Acceptance Criteria:** After a restore, the player's facing direction and animation frame
  equal their documented defaults.
- **Dependencies:** FR-5200.
- **Verification Method:** Test.
- **Source Documents:** GDS-05 C5; BL-0018 (resolved).
- **Related ADRs:** None.
- **Notes:** Prior to 2026-07-07 this requirement also excluded per-zone ScoreItem state; that
  scope moved to FR-5220 (now a Must-persist requirement) per the user's explicit decision. See
  this document's Changelog.

### FR-5220 — Persist per-zone ScoreItem collected-state

- **ID:** FR-5220
- **Title:** The system shall persist each zone's ScoreItem collected-state across save/load.
- **Description:** In addition to the FR-5100/FR-5200 save-field set, the system shall save and
  restore, per zone, which ScoreItems (stars/flowers) have already been collected, so that a
  restored game does not re-present previously-collected ScoreItems as available.
- **Rationale:** Explicit user decision, 2026-07-07 (see this document's Changelog): "Zone score
  item state should save and persist," resolving BL-0018's previously-open question in favor of
  widening the persisted save-field set.
- **Priority:** Must
- **Inputs:** Player save-confirm action (in SAVE, FR-5100); per-zone ScoreItem active/collected
  state at save time.
- **Outputs:** SRAM updated with per-zone ScoreItem collected-state; on restore, each zone's
  ScoreItems reflect that saved state rather than defaulting to "all present."
- **Preconditions:** State is SAVE and the save-confirm input is received (for persisting); a
  valid save is being restored (for loading).
- **Postconditions:** After a save, SRAM's per-zone ScoreItem collected-state matches the
  in-memory state at save time. After a restore, in-memory per-zone ScoreItem collected-state
  exactly matches what was last saved.
- **Acceptance Criteria:** Given a ScoreItem was collected before a save, after a subsequent
  restore that same ScoreItem is **not** re-collectible (remains marked collected). Given a
  ScoreItem was never collected before a save, after a restore it remains collectible.
- **Dependencies:** FR-5100, FR-5200, FR-3200 (ScoreItem collection).
- **Verification Method:** Test.
- **Source Documents:** User decision, 2026-07-07; BL-0018.
- **Related ADRs:** ADR-0006 (MBC1+RAM+BATTERY save format — this requirement widens the
  persisted field set within that same save mechanism, not a new one).
- **Notes:** This requirement was a Candidate (part of former CR-01) until the user's decision
  promoted it to the numbered baseline. Implementation scope (e.g. the exact SRAM bytes/bitfield
  used to represent per-zone ScoreItem state) is a Data Model (GDS-07)/future implementation
  concern, not stated here — this FR states only the observable persistence behavior required.

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

### FR-6400 — Player and collectible sprite rendering (added 2026-07-10, `BL-0020`)

- **ID:** FR-6400
- **Title:** The system shall render the player and each active Collectible as on-screen sprites.
- **Description:** During PLAYING, the system shall render the player as a single 8×16 OBJ pair
  at its current position and facing, and each active Collectible in the current zone as its own
  OBJ sprite, using the shadow-OAM-DMA mechanism every frame.
- **Rationale:** GDS-08 §2 (sprite strategy); ADR-0005 (shadow-OAM DMA every frame); ADR-0007
  (8×16 OBJ mode). Shipped and exercised by `test_rom.py`'s T6 suite since before this
  requirement existed — this FR formalizes already-shipped, already-tested behavior that had no
  numbered requirement statement (surfaced by `05-feature-decomposition`'s FP-05 review, finding
  #1, run #19, `BL-0020`).
- **Priority:** Must
- **Inputs:** Player position/facing (FR-2100/FR-2200); each active Collectible's position/type
  (FR-3100's zone data).
- **Outputs:** One 8×16 OBJ pair for the player (X-flipped per facing, per T6.5/T6.6); one OBJ
  entry per active Collectible.
- **Preconditions:** State is PLAYING.
- **Postconditions:** The player's OBJ position/tile/attribute match its current
  position/frame/facing; each active Collectible has a corresponding on-screen OBJ; a collected/
  inactive Collectible has no OBJ.
- **Acceptance Criteria:** The player's OBJ Y/X equal `PLAYER_Y+16`/`PLAYER_X+8`; its tile index
  is one of the two walk-frame values; its palette is 0; X-flip matches facing direction (T6.1–
  T6.6). Every active Collectible has an on-screen OBJ (Y>15) with a tile matching its type
  (T6.9/T6.10).
- **Dependencies:** FR-2100, FR-2200, FR-3100.
- **Verification Method:** Test — `test_rom.py` T6.1–T6.10 (already passing, pre-existing
  evidence; this requirement adds no new test).
- **Source Documents:** GDS-08 §2; ADR-0005; ADR-0007; `test_rom.py` T6.
- **Related ADRs:** ADR-0005, ADR-0007.
- **Notes:** A formal-requirement-only addition — no behavior change, no new test. Closes
  `BL-0020`.

## FR-9000 — World generation (target — 2026-07-09, new capability, not yet shipped)

*(formalizes [MSTR-001](../master/MSTR-001-program-vision.md) C10, [ADR-0009](../architecture/adr/ADR-0009-screen-graph-world-generation.md)/[ADR-0010](../architecture/adr/ADR-0010-seed-scale-model.md), the [GDS-04](../architecture/04-domain-model.md) delta's new domain rules)*

### FR-9100 — Deterministic world generation from (seed, scale)

- **ID:** FR-9100
- **Title:** The system shall generate an identical world for an identical (seed, scale) pair,
  every time.
- **Description:** Given the same seed and world-scale values, the system's world-generation
  routine shall produce byte-identical region-graph output (biome assignments and adjacency
  edges) every time it runs — across boots, across sessions, with no dependence on any input
  other than (seed, scale).
- **Rationale:** MSTR-001 C10; ADR-0009; strategic assumption A9 (seed is the sole determinism
  input — no DIV-register or uninitialized-RAM dependence).
- **Priority:** Must (target — not yet implemented)
- **Inputs:** SEED (16-bit), WORLD_SCALE (2–9).
- **Outputs:** A region graph: WORLD_SCALE² regions, each with a biome assignment and adjacency
  edges to its neighbors.
- **Preconditions:** SEED and WORLD_SCALE have been set (FR-1180).
- **Postconditions:** The region graph is fully determined by (SEED, WORLD_SCALE) alone.
- **Acceptance Criteria:** Generating a world twice from the same (seed, scale) pair — in
  separate new-game creations, or via the Python reference-generator oracle vs. the SM83
  routine — produces byte-identical region-graph output both times.
- **Dependencies:** FR-1180.
- **Verification Method:** Test (determinism property test, R305's extension; the
  reference-generator-oracle comparison).
- **Source Documents:** ADR-0009; strategic-assumptions-register A9.
- **Related ADRs:** ADR-0009.
- **Notes:** No text-dialogue system is required to satisfy C9's narrative delivery — the
  generated world's own structure (this FR, FR-4300/4310) carries the narrative, per MSTR-001
  D1/§4's explicit non-goal (not ruled out, not required at this vision's date). Not yet
  implemented.

### FR-9110 — Seed/scale immutable per save, entered only at new-game creation

- **ID:** FR-9110
- **Title:** The system shall accept seed and world-scale values only during new-game creation,
  and never permit changing them for an existing save.
- **Description:** SEED and WORLD_SCALE shall be set exactly once, during the FR-1180 new-game
  flow, and shall remain fixed for the entire life of that save — no in-game menu, state, or
  input sequence shall allow modifying either value once a game has begun.
- **Rationale:** Owner decisions D6/D7, 2026-07-09; ADR-0010.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** None beyond FR-1180's entry event (the only path that sets these values).
- **Outputs:** None (a negative/structural requirement — the absence of any other write path).
- **Preconditions:** A save exists (has been created via FR-1180).
- **Postconditions:** SEED/WORLD_SCALE for that save are identical to their values at creation,
  for the save's entire lifetime.
- **Acceptance Criteria:** No reachable input sequence from PLAYING, SAVE, or MAP changes
  SEED/WORLD_SCALE for an in-progress save. The only way to obtain a different (seed, scale) is
  starting a new game (FR-1180).
- **Dependencies:** FR-1180.
- **Verification Method:** Test (negative test — attempt every in-game menu path, confirm none
  writes SEED/WORLD_SCALE) / Inspection.
- **Source Documents:** ADR-0010.
- **Related ADRs:** ADR-0010.
- **Notes:** Not yet implemented.

### FR-9120 — Full reachability of every generated region

- **ID:** FR-9120
- **Title:** The system shall generate only worlds in which every region is reachable from the
  starting region.
- **Description:** For any generated world, every region shall be reachable from the player's
  starting region via a sequence of legal (grammar-valid, FR-4310) region transitions.
- **Rationale:** MSTR-001 C10; ADR-0009; GDS-04 delta (new domain rule — no shipped-baseline
  precedent needed, since a fixed 3×3 grid is trivially fully connected).
- **Priority:** Must (target — not yet implemented)
- **Inputs:** The generated region graph (FR-9100).
- **Outputs:** None (a structural guarantee of the graph itself).
- **Preconditions:** Generation has completed (FR-9100).
- **Postconditions:** Every region in the graph is reachable from the starting region.
- **Acceptance Criteria:** For any (seed, scale) in a test corpus, a graph-traversal from the
  starting region visits every generated region.
- **Dependencies:** FR-9100.
- **Verification Method:** Test (property test across a (seed, scale) corpus, R305's extension).
- **Source Documents:** ADR-0009; GDS-04 delta.
- **Related ADRs:** ADR-0009.
- **Notes:** Not yet implemented. This is a generator-*guaranteed* property, not a
  post-generation check that could fail and be silently accepted.

### FR-9130 — Exactly one KeyItem per generated region

- **ID:** FR-9130
- **Title:** The system shall generate exactly one KeyItem per region, for every region in a
  generated world.
- **Description:** Generalizes the "exactly one Carrot per Zone" convention (BL-0017, T1.11) to
  the generated-world case: every region, regardless of world scale, shall contain exactly one
  KeyItem.
- **Rationale:** MSTR-001 C9/C10; GDS-04 delta; BL-0017 (the convention this generalizes).
- **Priority:** Must (target — not yet implemented)
- **Inputs:** The generated region graph (FR-9100).
- **Outputs:** Exactly one KeyItem instance placed per region.
- **Preconditions:** Generation has completed.
- **Postconditions:** Every region has exactly one KeyItem.
- **Acceptance Criteria:** For any (seed, scale) in a test corpus, counting KeyItems per region
  yields exactly 1 for every region, with no region holding 0 or ≥2.
- **Dependencies:** FR-9100, FR-3220.
- **Verification Method:** Test (property test across a (seed, scale) corpus, generalizing
  T1.11's existing pattern).
- **Source Documents:** GDS-04 delta; BL-0017.
- **Related ADRs:** ADR-0009.
- **Notes:** Unlike BL-0017's shipped-baseline finding (the one-carrot-per-zone rule holds only
  by convention, not code-level enforcement), this requirement is **generator-guaranteed by
  construction** (ADR-0009) — a stronger guarantee than the shipped model's. Not yet implemented.

### FR-9200 — Save-format extension: seed, scale, and per-region flags

- **ID:** FR-9200
- **Title:** The system shall persist SEED, WORLD_SCALE, and per-region KeyItemFlags to SRAM,
  and regenerate the region graph from SEED/WORLD_SCALE on load rather than persisting the graph
  itself.
- **Description:** Extends FR-5100/FR-5200's save-field set: on save, the system shall write
  SEED, WORLD_SCALE, and KeyItemFlags[region] to SRAM under a new save-format version value. On
  load, the system shall restore SEED/WORLD_SCALE, regenerate the region graph via FR-9100 (not
  read a persisted graph), then restore KeyItemFlags onto the regenerated graph.
- **Rationale:** ADR-0010; GDS-07 delta §7; R106's extension (extends the FS-101/IP-1010
  version-byte precedent).
- **Priority:** Must (target — not yet implemented)
- **Inputs:** SEED, WORLD_SCALE, KeyItemFlags at save time; SRAM contents at load time.
- **Outputs:** SRAM updated with the new fields under the new version value (save); in-memory
  SEED/WORLD_SCALE/regenerated-graph/KeyItemFlags matching the saved values (load).
- **Preconditions:** A save-confirm or exit-to-main-menu action (save); a version-matching save
  exists (load, per FR-1170).
- **Postconditions:** SRAM's SEED/WORLD_SCALE/KeyItemFlags match in-memory values at save time
  (save); the regenerated graph plus restored KeyItemFlags exactly reproduce the pre-save world
  state (load).
- **Acceptance Criteria:** Saving then loading a game yields an identical region graph
  (regenerated from the same SEED/WORLD_SCALE, per FR-9100's determinism) and identical
  KeyItemFlags to those present at save time.
- **Dependencies:** FR-9100, FR-9110, FR-5100, FR-5200.
- **Verification Method:** Test (save/reload two-instance harness, R305's existing pattern,
  extended to SEED/WORLD_SCALE/KeyItemFlags).
- **Source Documents:** GDS-07 delta §7; ADR-0010.
- **Related ADRs:** ADR-0010, ADR-0006.
- **Notes:** A save whose version byte does not match this new value is not offered on the
  MAIN MENU's "continue" path (FR-1170) — the world *model* differs, not just a field, per
  ADR-0010's explicit reasoning (following the FS-101 precedent for resolving this class of
  question directly rather than escalating). Not yet implemented.

## Candidate Requirements

*(untraceable to a current source, or contingent on an unresolved design decision — explicitly
excluded from the numbered baseline above; marked `CANDIDATE — NOT BASELINED` in RQ-04)*

### CR-01 — Full save-field persistence (facing/frame/per-zone ScoreItem state) — RESOLVED, SPLIT 2026-07-07

- **Description:** Extend the persisted save-field set (FR-5100/FR-5200) to also include player
  facing direction, animation frame, and per-zone ScoreItem collected-state.
- **Resolution (2026-07-07, explicit user decision):** Split into two independent halves —
  - **Facing direction / animation frame persistence — REJECTED.** User's stated reason: "not
    important." No FR added; FR-5210 continues to document these as intentionally excluded.
  - **Per-zone ScoreItem collected-state persistence — APPROVED.** User's stated decision: "Zone
    score item state should save and persist." Promoted to the numbered baseline as **FR-5220**.
- **Disposition:** CLOSED — no longer a live Candidate. Kept here (not deleted) as the historical
  record of the original untraceable request and its resolution, per this document's append-only
  changelog discipline.

### CR-02 — Build-time or runtime enforcement of "exactly one Carrot per zone"

- **Description:** Add an explicit check (build-time validation of `ZONE_COLLECTS`, or a runtime
  assertion) that each zone's collectible list contains exactly one Carrot.
- **Why excluded:** No source document requires this invariant be *enforced* — GDS-04/GDS-05
  describe it as a fact that currently holds, not a requirement that it be checked. BL-0017 is the
  tracking finding.
- **Disposition:** SCHEDULED per BL-0017 — recommended as a Verification Checklist item on any
  future package touching `ZONE_COLLECTS`, not a standalone requirement today.
