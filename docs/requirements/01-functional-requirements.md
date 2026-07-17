# RQ-01 — Functional Requirements

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment, FR-1170–9200; delta 2026-07-11 for `ADR-0012`'s maze-shaped region adjacency,
> FR-9140/9150/2330; delta 2026-07-12 for `ADR-0015`'s win-condition redesign, FR-9160/9161;
> delta 2026-07-13 for the edge-indicator legend screen, FR-1200/1210, `CR-06`/`BL-0100`; delta
> 2026-07-13 (cont'd) for the Infinite Mode epic, FR-10000–10500, `CR-07`, `ADS-001`/`ADR-0016`/
> `ADR-0017`/`BL-0094`/`BL-0106`; delta 2026-07-13 (cont'd) — `CR-07` resolved by direct user
> decision, baselined as FR-10600; delta 2026-07-14 — `CR-05` mechanism resolved by direct user
> decision, `ADR-0018` adopted, not yet baselined pending a future `04` pass; delta 2026-07-14
> (cont'd) — `IP-1101` partially implements FR-10200/10210/10300 (per-region materialization/
> treasure-presence half; streaming window, render, and collection remain `IP-1102`/`1103`'s own
> scope); delta 2026-07-14 (cont'd) — `CR-05` baselined as `FR-9170` (finite-mode biome-blob
> clustering); `FR-10100`'s Notes/Acceptance Criteria refreshed against `GDS-01` §4d, now landed;
> delta 2026-07-16 — `IP-1103` fully implements FR-10300 (collection half lands) and partially
> implements FR-10400 (state + comparison subroutine, no automatic trigger — `BL-0112`); delta
> 2026-07-16 (cont'd) — `IP-1104` fully implements FR-10500/FR-10600, closing the Infinite Mode
> tranche's own FR set; delta 2026-07-16 (cont'd) — new **FR-4320** (nine biome-family
> identities, `BL-0128`), a requirements delta to `FR-9100`/`FR-10200`'s shared biome-family
> axis, widening it from five to nine identities so every already-shipped zone screen becomes a
> reachable generation target; `FR-9170`/`FR-4310` updated in place for the new domain; delta
> 2026-07-16 (cont'd) — **`CR-08` resolved and baselined into `FR-4310`**, a concrete nine-value
> adjacency-grammar ordering grounded in `R212` v1.1; delta 2026-07-16 (cont'd) — **new FR-7000
> group (FR-7100/FR-7110), procedural music generation, `ADR-0019`/`BL-0127`** — this project's
> first use of the FR-7xxx audio range — see Changelog).**
> Owned by `04-requirements-engineering`.
> Derives from [GDS-05](../architecture/05-functional-requirements.md)'s six capability groupings
> (C1–C6) — this document formalizes each into numbered, testable `FR-xxxx` requirements per
> [GDS-10](../architecture/10-requirements-traceability-matrix.md) §3's stated contract: *cite
> back to the specific GDS-05 grouping each requirement formalizes, don't restate the capability
> from scratch.* Priority scale used throughout: **Must** (required for the shipped game to
> function as-built) / **Should** (a real gap or open question, not yet a defect) / **Could**
> (not applicable to any requirement below — no optional-scope FRs exist in the as-built
> baseline).

## Changelog

- **2026-07-16 — New FR-7000 group (FR-7100/FR-7110), procedural music generation** (`BL-0127`,
  `ADR-0019`). This project's first use of the FR-7xxx audio range (confirmed unused before this
  delta). `FR-7100`: build-time generation of nine biome-family sub-themes from the existing main
  theme via transposition/tempo-scaling, no independent composition, no new sibling module
  (`ADR-0019`'s own reasoning: no runtime/oracle-lockstep need, unlike `worldgen.py`). `FR-7110`:
  identity-keyed playback selection, mirroring the existing HUD zone-label mechanism's own trigger
  shape — decides the selection's *shape* only, leaves the exact `GAMESTATE`/WRAM mechanism to
  `06`/`07` per this stage's own discipline. Both FRs name a real, non-blocking sequencing
  dependency: their eventual implementation needs `FR-4320`'s own packages
  (`IP-1105`/`IP-1033`/`IP-1022`/`IP-1106`, all unauthorized) shipped first, since `FR-7110` reads
  the same widened biome-id domain those packages establish.
- **2026-07-16 — `CR-08` resolved and baselined into `FR-4310`** (`BL-0128`/`BL-0129`,
  `02-research-game-design`'s `R212` v1.1 delta). `FR-4310`'s own Description/Postconditions/
  Acceptance Criteria now state a concrete nine-value adjacency-grammar ordering — `Water(0) –
  Sand(1) – Grass(2) – Stone(3) – Brick(4) – Village(5) – Cave(6) – Desert(7) – Plains(8)` —
  replacing the previous abstract "appears in R212's adjacency grammar table" phrasing with the
  table's own actual contents, now that R212 states them. Grounded in three independent real-
  world precedents, not invented: Cappadocia's Uçhisar (a real castle-fortress-plus-troglodyte-
  village-plus-cave-city, grounding Castle↔Village↔Cave as one real place rather than three
  separately-invented pairings), Petra (desert cave dwellings, a documented thermal-adaptation
  motive grounding Cave↔Desert), and Minecraft's own real biome-generation rule (already `R212`'s
  own cited precedent source, now reused to ground Desert↔Plains). Confirmed no architecture
  conflict — `FR-4320`'s own palette-mapping decision (§10 there) is independent of this axis, per
  direct cross-check. One honest, deliberately-kept trade-off restated in `FR-4310`'s own Notes
  rather than hidden: the append-only ordering (preserving the shipped `0`-`4` range to avoid a
  renumbering risk) decouples the four new identities' grammar-legality from their palette-group
  siblings — not a defect, since this FR never required the two to coincide. `CR-08` is closed —
  see its own entry for the full resolution trail (`02-research-game-design` → this delta).
- **2026-07-16 — New FR-4320 (nine biome-family identities); FR-9170/FR-4310 updated for the new
  domain** (`BL-0128`, direct project-owner decision: "merge the two sets keeping the art from
  both... there should be no art content and area definitions unused"). Widens the biome-family
  axis both `FR-9100` (finite mode) and `FR-10200` (Infinite Mode) generate over from five
  identities to nine, folding in the four original zone identities (Village, Cave, Desert,
  Plains) that `IP-1030`/`IP-1031`/`IP-9070` left orphaned when they consolidated to five. Grounds
  the decision in `R212`'s own already-written allowance for "a refinement of" the five-way
  palette-family vocabulary, and `08-presentation-architecture.md` §8's explicit deferral of
  "exact biome-family count" to a future implementation package — **no new architecture/ADR pass
  was needed**, this delta exercises a choice the architecture ladder already reserved.
  `FR-9170`'s biome-id clamp widened `[0,4]`→`[0,8]`; `FR-4310`'s Notes flag that R212's own
  adjacency-grammar table still needs to place the four new identities on its ordering axis (not
  resolved here — routed to `02`/`03`, see `03-requirements-review.md`). Two gaps named but not
  resolved by this delta, both flagged in the Review: (1) four of the nine identities
  (Village/Cave/Desert/Plains) have no collectible-spawn table today — `IP-9070` deleted the
  originals rather than orphaning them, so this needs fresh content-authoring, not a rewire; (2)
  Infinite Mode's separate per-region streaming representation currently allocates only 3 bits to
  biome-id (max 8 values) alongside a 4-bit connectivity field — reaching 9 values needs that
  byte's field widths re-apportioned (fits without growing the byte; a real but self-contained
  future `08-code-implementation` change).
- **2026-07-16 — FR-10500/FR-10600 fully Implemented** (`IP-1104`, visited-region-ledger save
  persistence; status updates only, no requirement text amended). FR-10500: position +
  bounded-ledger save/load shipped, `SAVE_VERSION_VAL` bumped `0x04`→`0x05`, two-instance
  round-trip verified (`T27.a`); FIFO eviction at the 128-entry capacity verified (`T27.c`), also
  closing `NFR-5400`'s own sizing question. FR-10600: a systematic negative-test sweep across
  every reachable input branch (movement, both SAVE round-trip paths, SELECT-menu round trip)
  confirms no mechanic forcibly ends a loaded Infinite Mode run (`T27.f`). This closes the
  Infinite Mode tranche's own FR set in full — `BL-0112` (the run-end trigger for `FR-10400`'s
  top-3 comparison) remains the tranche's sole standing gap, per `IP-1103`'s own explicit
  boundary.
- **2026-07-16 — FR-10300 fully Implemented; FR-10400 Partially Implemented** (`IP-1103`,
  treasure collection & win-condition state; status updates only, no requirement text amended).
  FR-10300's collection half shipped: the current region's treasure spawns as the sole
  `COLL_DATA` entry (per-biome position mirroring `ZONE_COLLECTS`' type-2 entry) and
  `check_collisions`' new `GAME_MODE == 1` branch counts the pickup without touching any
  finite-mode counter (`T26.a/b`). FR-10400's state (`RUNNING_TREASURE_COUNT`,
  `TOP_SCORE_TABLE`) and comparison subroutine (`inf_check_top_score`) shipped and
  corpus-verified (`T26.c`), **deliberately without any automatic call site** (`T26.d` asserts
  the zero-call-site state) — the run-end trigger is `BL-0112`'s own open question, routed to
  `04` or a direct user decision by `FS-110` itself, so FR-10400 is recorded **Partially
  Implemented**, not rounded up.
- **2026-07-14 — CR-05 baselined as FR-9170** (finite-mode biome-blob clustering, `BL-0066`).
  Derives the real requirement from `ADR-0018`'s per-super-cell `hash(SEED, supercell_row,
  supercell_col)` snap-to-blob mechanism, layered on `ADR-0009` point 2's existing draw as
  fallback. `CR-05` closed — see its own entry for the full resolution trail.
- **2026-07-14 — FR-10100 refreshed against `GDS-01` §4d** (mode-selection UI, `BL-0113`, now
  landed). Acceptance Criteria extended to state the mode-choice-before-either-entry-step
  sequencing and both new cancel-path targets at the observable-behavior level; Notes updated to
  point at the concrete UI shape instead of flagging it as missing. No new FR-ID — the existing
  FR-10100 already covered the substantive "what" (mode choice offered, seed-only); `GDS-01`
  §4d supplies the "how," which is a Notes/Acceptance-Criteria-level refinement here, not a
  missing capability the way `CR-06`'s edge-indicator legend screen was (no FR existed for that
  at all). No FR/NFR contradicts another as a result of this refresh.
- **2026-07-14 — FR-10200/10210/10300 partially implemented** (`IP-1101`, per-region
  materialization/treasure-presence). `T22` (7 checks) confirms determinism, oracle parity,
  revisit-consistency at the data layer, treasure-density near `K=16`'s target, and a static
  no-`DIV`/`MUL` audit. Streaming window management, transition-triggered materialization,
  render integration (`FR-10200`'s own navigate/render half), and treasure collection
  (`FR-10300`'s own collection half) are `IP-1102`/`1103`'s own scope, not yet implemented.
- **2026-07-14 — CR-05 mechanism resolved by explicit user decision** (`ADR-0018`,
  `BL-0066`/`CR-05`). The project owner directed reusing Infinite Mode's own per-super-cell
  `hash(SEED, supercell_row, supercell_col)` blob technique for the finite mode too, superseding
  CR-05's original dead-end-seeding proposal — [ADR-0018](../architecture/adr/ADR-0018-finite-mode-biome-blob-clustering.md)
  adopts it, refining `ADR-0009` point 2, needing no `ADR-0012` pass-ordering change. CR-05 is now
  ready for a future `04-requirements-engineering` pass to derive the real FR from — not yet
  baselined, mirroring `CR-06`'s own `03→04` precedent.
- **2026-07-13 — CR-07 resolved by explicit user decision.** The project owner decided directly:
  "for now assume indefinitely resumable." **CR-07** (run/session shape) is RESOLVED and
  BASELINED — promoted to new **FR-10600** (Indefinitely resumable Infinite Mode run, no
  death/retreat/checkpoint mechanic). No `GDS-01` delta was needed (the no-new-mechanic branch of
  CR-07's own analysis applies), so this resolves entirely within `04`, without a
  `03-architecture-design-synthesis` round-trip. Explicitly a "for now" decision — revisitable,
  not permanently closed, per the owner's own wording (carried into `FR-10600`'s Notes verbatim).
- **2026-07-13 — Delta for the Infinite Mode epic** (`ADS-001`/`ADR-0016`/`ADR-0017`, `BL-0082`'s
  architecture-adoption decision; carries `BL-0094`'s score-chasing win condition and `BL-0106`'s
  run/session-shape question forward; re-run Step 0 on the delta only, per this skill's own
  Gotchas — not a wholesale regeneration). **Seven new FRs added**, all target — none shipped
  yet: **FR-10100** (new-game entry, seed-only), **FR-10200** (streaming positionally-
  deterministic generation), **FR-10210** (revisit-consistent materialization), **FR-10300**
  (hash-density treasure placement, decoupled from maze structure — a named departure from
  `BL-0094`'s literal "at dead ends" wording, per `ADR-0017`), **FR-10400** (score-chasing win
  condition — running count + top-3, no name entry), **FR-10500** (visited-region-ledger
  save/load). **None of FR-9000's finite-mode leaves are amended or superseded** — Infinite Mode
  is additive, per `ADR-0016`/`ADR-0017`'s own text. **One Candidate filed, not baselined:**
  **CR-07** (run/session shape — indefinitely resumable vs. a new bounded-run end-condition
  mechanic) — `R216`/`ADR-0017` both explicitly surface this as an unresolved design question,
  not a gap this stage can close by inventing an answer; routed as a future `NEEDS-USER` decision
  (see RQ-03 finding #17). Two new Recommendation-type backlog items (`BL-0107` Binary Tree
  aesthetic, `BL-0108` visited-region ledger SRAM sizing) are referenced in Notes but not
  restated as requirements — both are implementation-time concerns, not requirements-level gaps.
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
- **2026-07-11 — Delta for `ADR-0012`'s maze-shaped region adjacency** (`BL-0064`–`BL-0067`,
  project-owner design request; re-run Step 0 on the delta only, per this skill's own Gotchas —
  not a wholesale regeneration). **Three new FRs added:** **FR-9140** (maze-generation pass —
  spanning tree + braid, `BL-0064`), **FR-9150** (braid-fraction parameter mechanism + a fixed
  initial default, `BL-0065` — its own UI-exposure question is *not* resolved here, see RQ-03
  finding), **FR-2330** (3-state transition-edge signaling, generalizing `FR-2320` past its
  still-2-state/3×3-worded text — `FR-2320` itself is left unmodified, describing the currently
  shipped behavior, per this project's established `FR-1120`→`FR-1170`-`1190` coexistence
  precedent, `RQ-03` finding #7). **`BL-0066` (biome-blob clustering) did not receive a
  baseline FR** — dead-end-seeded clustering (the owner's own first suggestion) conflicts with
  `ADR-0012`'s fixed biome-first generation ordering; flood-fill-seeded clustering does not.
  Routed as **CR-05** (Candidate, not baselined) pending a `03-architecture-design-synthesis`
  revisit if dead-end-seeding is specifically wanted — see RQ-03's finding for the full
  conflict analysis. Light Notes-field touches only (no Description/Postcondition changes) on
  **FR-9100** (cross-references `FR-9140`), **FR-9120** (reachability now a structural spanning-
  tree guarantee, `ADR-0012`), and **FR-4310** (confirmed: still holds unchanged, since biome
  generation is grid-wide and maze-connectivity-independent per `ADR-0012` point 1).
- **2026-07-12 — Delta for `ADR-0015`'s win-condition redesign** (`BL-0093`, project-owner direct
  decision resolving `BL-0081`/`R215`; re-run Step 0 on the delta only, per this skill's own
  Gotchas — not a wholesale regeneration). **Two new FRs added:** **FR-9160** (scale-relative,
  dead-end-prioritized KeyItem placement — supersedes `FR-9130`'s "exactly one per region" rule)
  and **FR-9161** (scale-relative victory condition — supersedes `FR-3300`'s fixed "reaches 9"
  threshold), both target — not yet implemented, per this project's established
  `FR-1120`→`FR-1170`-`1190` coexistence precedent: the superseded FRs are left with their
  substantive text unmodified (they remain accurate for the currently shipped game) and gain only
  a Notes forward-pointer. **`FR-9130` Notes also corrected** for an unrelated, pre-existing
  documentation-staleness finding: its own text claimed "Not yet implemented," but `IP-1020`
  actually shipped and independently verified the original one-per-region rule (`VR-1020`,
  `T12.e`) before `ADR-0015` superseded it — a factual correction, not a behavior-text edit, made
  in passing while this FR was already open for its own supersession note.
- **2026-07-13 — Delta for the edge-indicator legend screen** (`BL-0100`, project-owner request;
  re-run Step 0 on the delta only). First pass (same day) found no traceable architecture source
  and correctly declined to invent one — filed as **CR-06** (Candidate Requirements) and routed to
  `03-architecture-design-synthesis` (RQ-03 finding #15). Second pass, same day, once
  [GDS-01](../architecture/01-concept-of-play.md) §4c and
  [GDS-08](../architecture/08-presentation-architecture.md) §11 landed: **two new FRs added,
  both target — not yet implemented:** **FR-1200** (SELECT MENU state — `SELECT` now opens a
  two-option cursor menu, `MAP`/`LEGEND`, superseding FR-1150's own "SELECT→MAP" clause) and
  **FR-1210** (LEGEND state — the static edge-indicator explanation screen itself). `FR-1150` is
  left with its substantive text unmodified (accurate for the currently shipped game) and gains
  only a Notes forward-pointer, per the established `FR-1120`→`FR-1170` coexistence precedent.
  `CR-06` is closed, pointing forward to `FR-1200`/`FR-1210` rather than deleted.

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
  supersession trigger). **Forward-pointer note (2026-07-10, `IP-1040`):** the superseding
  implementation has now shipped — `try_load_save`'s unconditional-at-boot call site no longer
  exists (confirmed by direct code read and `T14.a1`/`a3a`'s regression checks); this FR's own
  postcondition text is left unmodified here (a future `04-requirements-engineering` delta's
  call, per this stage's SHALL-NOT rule against editing requirements from an implementation run).

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
- **Notes:** **Target-state pointer (2026-07-13):** [GDS-01](../architecture/01-concept-of-play.md)
  §4c commits SELECT's own target to a new SELECT MENU state (FR-1200) rather than jumping
  directly to MAP — MAP's own content and its own "B → PLAYING" clause are unaffected and remain
  this FR's. Unmodified here; accurate for the current shipped game. Will gain a forward-pointer
  note once FR-1200 ships, per the established FR-1120→FR-1170 coexistence precedent (RQ-03
  finding #7).

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
  **Forward-pointer note (2026-07-10, `IP-1040`):** the superseding implementation has shipped —
  `st_victory`'s A-press target is now `GS_MAIN_MENU` (confirmed by direct code read and
  `T4.9`'s regression check); this FR's own postcondition text is left unmodified here.

### FR-1170 — MAIN MENU state (Implemented — 2026-07-10, `IP-1040`)

- **ID:** FR-1170
- **Title:** The system shall present a MAIN MENU state on every boot, offering continue and new
  game.
- **Description:** On power-on/reset, the system shall always enter a MAIN MENU state — never
  bypassing it — offering a "continue" option (only if a version-matching save exists) and a
  "new game" option.
- **Rationale:** MSTR-001 C2 (amended v3.0); GDS-01 §2a/§4a; ADR-0010.
- **Priority:** Must (Met)
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
- **Notes:** Supersedes FR-1120's auto-load bypass (see FR-1120's own forward-pointer note).
  **Implemented (2026-07-10, `IP-1040`):** `st_main_menu`/`check_save_valid` (`asm_game.py`);
  `test_rom.py` T14.a1–a4 cover both option-set directions plus the version-mismatch case,
  163/163 full suite pass.

### FR-1180 — New-game seed/scale entry and world generation trigger (Implemented — 2026-07-10, `IP-1040`)

- **ID:** FR-1180
- **Title:** The system shall, on "new game," collect a seed and world-scale value via a
  digit-cursor entry screen, then generate the world before entering INTRO.
- **Description:** From MAIN MENU's "new game" option, the system shall present a digit-cursor
  entry UI for a 16-bit seed and a world-scale value (2–9, default 3), then — on confirmation —
  initialize the world generator from that (seed, scale) pair and transition to INTRO.
- **Rationale:** MSTR-001 C10; GDS-01 §4a; ADR-0009; ADR-0010.
- **Priority:** Must (Met)
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
  requirement, per R111/ADR-0010) — the player may still enter 0.
  **Implemented (2026-07-10, `IP-1040`):** `st_seed_scale_entry`/`sse_compose_seed`
  (`asm_game.py`) — 5 independent decimal digits, composed into the real 16-bit SEED via
  saturating repeated-addition (no general multiply needed); `test_rom.py` T14.b1–b3 confirm a
  known (seed,scale) pair reaches INTRO with the correct region count and reproduces identically
  across two separate new-game creations; T14.c1 confirms B-cancel back to MAIN MENU writes
  neither field.

### FR-1190 — Exit-to-main-menu with auto-save (Implemented — 2026-07-10, `IP-1040`)

- **ID:** FR-1190
- **Title:** The system shall offer an exit-to-main-menu option from the SAVE state that
  auto-saves before returning to MAIN MENU.
- **Description:** In addition to FR-1140's existing A(save)/B(cancel) options, the SAVE state
  shall offer a third option that first performs the same save-field write FR-5100 performs, then
  transitions to MAIN MENU (not back to PLAYING).
- **Rationale:** MSTR-001 C2 (amended v3.0), owner decisions D8/D10; GDS-01 §4a.
- **Priority:** Must (Met)
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
- **Notes:** **Implemented (2026-07-10, `IP-1040`):** `st_save`'s SELECT branch (`asm_game.py`)
  calls the exact same `save_to_sram` A(save) already calls, then targets `GS_MAIN_MENU` instead
  of `GS_PLAYING`; `test_rom.py` T14.d1/d2 confirm the auto-save and exact state restoration on
  a subsequent "continue". **2026-07-11 delta (`IP-9080`, `BL-0049`):** the option's own behavior
  was already correct, but had no on-screen label — `save_screen` (`tilemaps.py`) now renders
  "SELECT: SAVE" / "AND EXIT" (rows 12–13), fixing a real discoverability gap (the option was
  functionally present but invisible to the player). Content-only; no behavior change.

### FR-1200 — SELECT MENU state (Implemented — 2026-07-13, `IP-1090`)

- **ID:** FR-1200
- **Title:** The system shall present a SELECT MENU offering MAP and LEGEND when SELECT is
  pressed from PLAYING.
- **Description:** From PLAYING, pressing SELECT shall transition to a SELECT MENU state
  presenting two cursor-selectable options, "map" and "legend." D-pad up/down moves the
  highlighted option; A confirms the highlighted option, transitioning to MAP or LEGEND
  respectively; B cancels, returning directly to PLAYING with neither option visited.
- **Rationale:** [GDS-01](../architecture/01-concept-of-play.md) §4c (project owner request,
  `BL-0100`); reuses the cursor-menu convention FR-1170/GDS-01 §4a already established for MAIN
  MENU rather than introducing a second UI convention for the same shape of choice.
- **Priority:** Must (Met)
- **Inputs:** SELECT press (in PLAYING); D-pad up/down (in SELECT MENU); A (confirm); B (cancel).
- **Outputs:** State transitions PLAYING→SELECT MENU (on SELECT); SELECT MENU→MAP or SELECT
  MENU→LEGEND (on A, per the highlighted option); SELECT MENU→PLAYING (on B).
- **Preconditions:** Current state is PLAYING (for entry); current state is SELECT MENU (for the
  confirm/cancel transitions).
- **Postconditions:** State transitions as specified; a B-cancel writes nothing and leaves
  PLAYING's own state exactly as it was before SELECT was pressed.
- **Acceptance Criteria:** From PLAYING, SELECT press results in state = SELECT MENU with "map"
  highlighted by default. D-pad up/down toggles the highlighted option between "map" and
  "legend." With "map" highlighted, A results in state = MAP. With "legend" highlighted, A
  results in state = LEGEND. From SELECT MENU, B results in state = PLAYING regardless of which
  option was highlighted.
- **Dependencies:** FR-1100 (extends the state set by one), FR-1150 (this FR supersedes FR-1150's
  own "PLAYING → MAP on SELECT" clause — MAP's own "B → PLAYING" clause and content are
  unaffected and remain FR-1150's), FR-1170 (the cursor-menu convention reused).
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4c.
- **Related ADRs:** None.
- **Notes:** **Named tradeoff (GDS-01 §4c):** reaching MAP now costs one extra confirm step for
  every player, not just those who want LEGEND — accepted per GDS-01 §4c's own reasoning (the
  same one-extra-step shape FR-1170/MAIN MENU's continue/new-game choice already asks with no
  recorded player-facing complaint), not silently absorbed. FR-1150's own "PLAYING → MAP on
  SELECT" acceptance criterion becomes inaccurate once this FR ships — left unmodified in
  FR-1150's own text per the established FR-1120→FR-1170 coexistence precedent (RQ-03 finding
  #7), to be marked superseded there once implemented. **Implemented 2026-07-13 (`IP-1090`):**
  `GS_SELECT_MENU`/`GS_LEGEND` = 8/9; `MM_CURSOR`/`MM_JUST_ENTERED` reused for the new state
  rather than new WRAM bytes; confirmed by `T21.a1`–`T21.d2`.

### FR-1210 — LEGEND state (Implemented — 2026-07-13, `IP-1090`)

- **ID:** FR-1210
- **Title:** The system shall present a read-only LEGEND screen explaining the transition-edge
  indicator tiles.
- **Description:** From SELECT MENU's "legend" option, the system shall present a static,
  read-only screen showing each of the three transition-edge indicator states (FR-2320/FR-2330:
  open arrow, blocked-edge bar, no indicator/world edge) alongside a plain-language label for
  each. B returns to PLAYING.
- **Rationale:** [GDS-08](../architecture/08-presentation-architecture.md) §11 (project owner
  request, `BL-0100`) — today's three-state edge signal (FR-2320/FR-2330) has no in-game
  explanation anywhere.
- **Priority:** Must (Met)
- **Inputs:** B press (in LEGEND).
- **Outputs:** State transitions LEGEND→PLAYING (on B).
- **Preconditions:** Current state is LEGEND.
- **Postconditions:** State = PLAYING.
- **Acceptance Criteria:** From LEGEND, B press results in state = PLAYING. The screen displays
  the actual open-arrow tile and the actual blocked-edge-bar tile (not redrawn approximations)
  each beside its own plain-language label, plus a labeled blank cell for the world-edge case.
- **Dependencies:** FR-1200, FR-2320, FR-2330.
- **Verification Method:** Test (state transition) / Inspection (visual — the exact tile/label
  layout, per GDS-08 §11's own "not decided here" deferral of precise screen coordinates to
  `07`/`08`).
- **Source Documents:** GDS-08 §11.
- **Related ADRs:** None.
- **Notes:** No new tile art or palette entry — reuses `TL_ARROW_U`/`TL_BLOCKED_U` and palette 2
  verbatim (GDS-08 §11). A single static page, no `SELECT`-triggered sub-paging within LEGEND
  itself (GDS-08 §11's own R206-grounded reasoning: three short facts don't need a multi-page
  manual). **Implemented 2026-07-13 (`IP-1090`):** confirmed by `T21.e`/`T21.f1`–`f3` — the real
  `TL_ARROW_U`/`TL_BLOCKED_U` tiles render beside their labels, plus a genuinely blank cell for
  the world-edge case.

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
  per the architecture-independence writing rule. **2026-07-11 delta (`IP-9090`, `BL-0051`/
  `BL-0052`):** the playfield's own pixel-edge clamp values (the point at which "blocked" per
  this FR's own Preconditions actually applies within a screen, distinct from `FR-2300`'s
  zone-boundary blocking) were corrected — UP floor `Y=8`, RIGHT ceiling `X=152` (both now flush
  with the true playfield edge: one 8px tile row below the static HUD, and the screen's own
  160px width minus the 8px sprite width, respectively) — previously `Y=17`/`X=159`, stopping the
  sprite short of/past the true edge. **This FR still does not baseline the exact pixel bounds**
  (a genuine requirements gap this delta does not close — see `IP-9090`'s own §3) — noted here as
  a candidate for a future `04-requirements-engineering` pass to formalize, not resolved by this
  Notes entry.

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
- **Notes:** Forward-pointer only (metadata, not a rewrite — `BL-0061` routes the actual
  target-state generalization of this FR's text to a future `04-requirements-engineering`
  delta): as of `IP-9050` (2026-07-11), generated-world navigation (`check_zone_transition`
  reading `REGION_GRAPH`'s neighbor bytes, `ADR-0009`) honors this FR's intent for the full
  `scale`×`scale` region graph, not just the 3×3 case its Description/Acceptance Criteria still
  name verbatim. **2026-07-12 delta (`IP-9120`, `BL-0076`):** this FR's own RIGHT-direction
  case regressed to fully broken (no rightward transition could ever fire through normal
  gameplay input) when `IP-9090`'s own correct RIGHT movement-clamp fix lowered the reachable
  `PLAYER_X` ceiling below `check_zone_transition`'s own RIGHT-edge trigger threshold — a code
  defect, not a requirement-text problem; fixed by aligning the threshold to the corrected
  clamp (`152`). `T7.11` added as a real-button-press-driven positive-transition regression
  test, the class of check missing across all four directions that let this ship undetected.
  **2026-07-12 delta (`IP-9130`, `BL-0078`):** a second, distinct defect in this FR's own
  implementation — `check_zone_transition`'s four branches tested only position, never whether
  the player was actually holding the corresponding direction, so entering a new region via one
  axis while still positioned at a boundary on the *other* axis (e.g. sitting at the RIGHT clamp
  ceiling after an earlier rightward walk, then entering a new region by walking DOWN) could fire
  a spurious transition the player never intended. Invisible under the old full-lattice model
  (blocked-right was uniform per grid column); reachable once the maze pass (`IP-1070`) made
  open/blocked vary per-region. Fixed by gating all four branches on the corresponding `JOY_CUR`
  direction bit, mirroring `handle_play_input`'s own gating. New check `T7.12` (direct `BL-0078`
  regression test).

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
- **Notes:** Forward-pointer only (metadata, not a rewrite — see `FR-2300`'s identical note,
  `BL-0061`). As of `IP-9050` (2026-07-11), the boundary-halt behavior this FR describes is
  honored for the full generated world (a `REGION_GRAPH` neighbor byte of `0xFF`), not just the
  3×3 grid's row/column edges its text still names verbatim.

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
- **Notes:** **Defect found and fixed ([IP-9140](../implementation/packages/IP-9140-right-arrow-offscreen-position-fix.md), 2026-07-12, `BL-0084`):** the right-edge arrow's tilemap position (`ARROW_ADDR_R`) placed it at tilemap column 30 — outside the true 20-column visible background window (`SCX=0` always) — so it was written to VRAM correctly but never actually rendered on screen, on any build, since before this pipeline's own work began (inherited from the retired pre-procgen `_zone_arrows`). Fixed to column 18; new check `T13.d` (screen-visibility audit) closes the test-coverage gap that let a correctly-written-but-invisible tile pass every prior tilemap-byte-value check. **Superseded by `FR-2330`, implemented 2026-07-13** ([IP-1081](../implementation/packages/IP-1081-maze-blocked-edge-indicator-content.md)/[IP-1082](../implementation/packages/IP-1082-maze-blocked-edge-indicator-render.md)) — the open-edge case this requirement describes remains byte-for-byte unchanged (confirmed by `IP-1082`'s own zero-diff claim on the open branches), but `FR-2330` now generalizes it to the full 3-state signal.

### FR-2330 — Three-state transition-edge signaling for a maze-shaped generated world (implemented — 2026-07-13)

- **ID:** FR-2330
- **Title:** The system shall distinguish, at each screen edge, between a grid boundary, a
  maze-blocked-but-grid-adjacent edge, and an open (maze-connected) edge.
- **Description:** Generalizes `FR-2320`'s on-screen arrow signal past its 2-state (arrow /
  no-arrow) form: for every screen edge, the system shall render one of three distinct visual
  states — an open-edge indicator (a valid, maze-connected neighbor exists, matching `FR-2320`'s
  existing arrow), a blocked-edge indicator (a grid-adjacent region exists but the generated maze
  does not connect to it), or no indicator at all (a true grid boundary — no grid-adjacent region
  exists in that direction). The distinction between the latter two is **not derivable from
  `REGION_GRAPH` alone** (both read as "no neighbor," `0xFF`, per `ADR-0012` point 2) — the
  render-time logic must independently re-derive "does a grid-adjacent region exist in this
  direction" from `(row, col, WORLD_SCALE)` arithmetic and compare that against whether
  `REGION_GRAPH` shows a live neighbor there.
- **Rationale:** `BL-0067` (owner design request, 2026-07-11): a maze-blocked edge must not look
  identical to a true dead end, or the player cannot tell "there is a path here I haven't opened"
  from "this is the edge of the world." Explicitly presentation-layer only — not mid-screen
  walls/collision, which remains out of scope for any current requirement.
- **Priority:** Must (implemented)
- **Inputs:** The current region's `REGION_GRAPH` neighbor bytes (`ADR-0012`); the current
  region's `(row, col)` position and the world's `WORLD_SCALE`.
- **Outputs:** One of three visual states rendered at each of the four screen edges.
- **Preconditions:** State is PLAYING; a maze-shaped world has been generated (`FR-9140`).
- **Postconditions:** Each screen edge's rendered indicator state matches exactly one of the
  three cases above, with no edge left ambiguous between "blocked" and "boundary."
- **Acceptance Criteria:** For any generated world in a test corpus, at every region and every
  direction: (a) if `REGION_GRAPH` shows a live neighbor, the open-edge indicator renders; (b) if
  no `REGION_GRAPH` neighbor exists but grid arithmetic confirms a grid-adjacent region exists in
  that direction, the blocked-edge indicator renders; (c) if grid arithmetic confirms no
  grid-adjacent region exists in that direction, no indicator renders.
- **Dependencies:** FR-9140, FR-2320 (the open-edge case reuses its existing arrow rendering
  verbatim).
- **Verification Method:** Test (per-edge state audit across a `(seed, scale)` corpus, extending
  `FR-2320`'s existing tilemap-inspection pattern to the new 3-way case) / Inspection (visual —
  `09-content-review` owed, see Notes).
- **Source Documents:** `BL-0067`; `ADR-0012` point 2.
- **Related ADRs:** ADR-0009, ADR-0012.
- **Notes:** **Logic half implemented ([IP-1080](../implementation/packages/IP-1080-maze-aware-edge-classification.md), 2026-07-12):** `draw_region_arrows` (`asm_game.py`) now re-derives `(row, col)` from `CUR_ZONE`/`WORLD_SCALE` at render time and independently confirms whether a grid-adjacent region exists in each direction — the classification arithmetic this requirement's AC-(b)/(c) clause describes, verified by `T20.a`–`d`. **Rendering half implemented ([IP-1081](../implementation/packages/IP-1081-maze-blocked-edge-indicator-content.md) content + [IP-1082](../implementation/packages/IP-1082-maze-blocked-edge-indicator-render.md) render, 2026-07-13):** `IP-1081` authored the 4 blocked-edge tiles (`0x1A`–`0x1D`, palette 2, per `GDS-08` §10); `IP-1082` extended `draw_region_arrows`'s existing per-direction branches so the blocked case now draws the corresponding `TL_BLOCKED_<dir>` tile at the same screen position the open-edge arrow uses — closing AC-(b) in full. `T20.b` (corrected) confirms the positive tile-index assertion; `T20.e` confirms the open-edge case is unaffected (AC-(a) non-regression). `FR-2320` is now formally superseded (its own Notes updated) — this requirement's full 3-state Description is satisfied. A `09-content-review` pass is still owed (this is the first exercise of these 4 tiles as live, rendered art — `IP-1081`'s own `BL-0097` finding, direction-pair tiles pixel-identical, is routed there).

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
  **2026-07-11 delta (`IP-9100`, `BL-0053`):** the shipped `10px`/`10px` symmetric-proximity model
  above is corrected — collection now fires iff the Collectible's own anchor point falls inside
  the player sprite's real `8×16` pixel extent (`0 <= item_x-PLAYER_X <= 7`,
  `0 <= item_y-PLAYER_Y <= 15`), an exact-overlap test with no forgiveness margin, per the project
  owner's own explicit request ("collect and only collect items with which the sprite overlaps").
  This corrects a real defect the old symmetric `10px` window had: it collected items up to 9px
  *above* the sprite's own top edge (outside any real overlap) while missing items genuinely
  overlapping the sprite's bottom edge (only reaching 9px down against the sprite's real 15px
  extent below its own anchor). **This FR's own Title/Description/Rationale/Acceptance Criteria
  text above still describes the old, now-superseded `10px`-symmetric model** — left unmodified
  here, out of `07-implementation-planning`'s/`08-code-implementation`'s own scope; a future
  `04-requirements-engineering` pass should correct it to describe the point-in-box model
  directly, not merely note the divergence.

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
- **Notes:** **Superseded (2026-07-13, `IP-1021`):** this fixed threshold's implementation has
  now shipped over — `check_complete` no longer compares against a hardcoded `9`; **FR-9161** is
  the authoritative requirement for the victory condition going forward. This FR's text above is
  left unmodified as an accurate historical record of the rule as it stood through `IP-1020`'s
  lifetime, per the `FR-1120`→`FR-1170`/`1180`/`1190` precedent's own second step.

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
  shall appear in R212's adjacency grammar table — two identities are grammar-legal adjacent iff
  they are the same or immediately adjacent on the ordered axis **(2026-07-16 delta, `BL-0128`,
  resolves `CR-08`):** `Water(0) – Sand(1) – Grass(2) – Stone(3) – Brick(4) – Village(5) –
  Cave(6) – Desert(7) – Plains(8)`, per R212 v1.1's own Delta section — e.g. water may border
  beach but never sky; Brick(Castle) may border Village but never Desert directly.
- **Rationale:** MSTR-001 C9; R212 (v1.1 delta, `CR-08`'s resolution); ADR-0009 (enforced by
  construction, not post-hoc validation).
- **Priority:** Must (target — not yet implemented)
- **Inputs:** The candidate adjacency the generator is about to create.
- **Outputs:** The adjacency is created only if grammar-legal; otherwise the generator selects a
  different candidate.
- **Preconditions:** Generation is in progress (FR-9100).
- **Postconditions:** Every edge in the generated region graph is grammar-legal — for any two
  adjacent regions' biome-id values `a`/`b` on the nine-value axis above, `|a - b| <= 1`.
- **Acceptance Criteria:** For any generated world (finite or Infinite Mode, once `FR-4320`'s own
  domain widening ships in each), every adjacent region pair's biome-family combination appears in
  the nine-value grammar table above; no illegal pairing exists anywhere in the graph. Specifically:
  `Stone(3)` may border `Brick(4)` but not `Village(5)`; `Village(5)` may border `Brick(4)` and
  `Cave(6)` but not `Stone(3)` or `Desert(7)`; `Cave(6)` may border `Village(5)` and `Desert(7)`
  but not `Brick(4)` or `Plains(8)`; `Desert(7)` may border `Cave(6)` and `Plains(8)` but not
  `Village(5)`; `Plains(8)` may border only `Desert(7)` (the axis's far endpoint, symmetric with
  `Water(0)`'s own single-neighbor status at the near endpoint).
- **Dependencies:** FR-9100, FR-4320 (the nine-identity domain and palette mapping this
  Acceptance Criteria's own axis operates over).
- **Verification Method:** Test (property test across a (seed, scale) corpus, per R305's
  extension).
- **Source Documents:** R212; ADR-0009; GDS-04 delta.
- **Related ADRs:** ADR-0009.
- **Notes:** Not yet implemented. This is a generator-*guaranteed* property (enforced during
  generation), not a post-generation check that could fail. **2026-07-11 delta:** confirmed
  still accurate, unchanged, once `FR-9140` (`ADR-0012`) ships — biome assignment remains a
  grid-wide pass, entirely independent of the maze's own connectivity (`ADR-0012` point 1), so
  every grid-adjacent pair's grammar-legality holds regardless of whether the maze ends up
  connecting or blocking that specific edge. **2026-07-16 delta (`BL-0128`):** once `FR-4320`'s
  nine-identity axis lands, this grammar table's own ordering (today defined only over the
  5-value palette-family axis, per R212's worked example) needs to place the four newly-folded-in
  identities (Village, Cave, Desert, Plains) somewhere on it — **R212 itself anticipates exactly
  this** ("the adjacency grammar should be defined over these families **or a refinement of
  them**," R212 Implementation Guidance) but does not say where the refinement sits. Not resolved
  here — a requirements pass cannot invent an ordering a design document hasn't stated. Filed as
  **CR-08** (Candidate Requirements, below), routed to `02-research-game-design` (extend R212's
  grammar table) or `03-architecture-design-synthesis` (a GDS-08 §8 delta) — the same routing
  `NFR-6510`'s own Stone↔Brick finding already used for a smaller version of this question.
  **Resolved (`02-research-game-design`, 2026-07-16): `R212` v1.1 grounds a concrete ordering**
  (Water–Sand–Grass–Stone–Brick–Village–Cave–Desert–Plains), real-precedented (Cappadocia's
  Uçhisar castle-village-cave cluster, Petra's desert cave dwellings, Minecraft's own
  desert-plains adjacency rule). **Baselined into this FR's own Description/Postconditions/
  Acceptance Criteria above, same day.** One honest, deliberately-kept trade-off, stated by R212
  itself and restated here rather than hidden: the append-only ordering (positions 5-8, preserving
  the shipped `0`-`4` order intact) decouples the four new identities' grammar-legality from their
  palette-group siblings — Village/Cave share Stone's palette (GDS-08 §4) but are not
  grammar-adjacent to Stone(3) on this axis. Not a defect — this FR never required palette
  grouping and adjacency-axis position to coincide, and R212 itself confirms `FR-4320`'s own
  palette-mapping decision (§10 there) is independent of this FR's own axis. `CR-08` is closed —
  see its own entry below for the resolution trail.

### FR-4320 — Nine biome-family identities, mapped onto five terrain-palette groups (target — 2026-07-16)

- **ID:** FR-4320
- **Title:** The system's biome-family axis (consumed by both finite-mode `FR-9100` and Infinite
  Mode `FR-10200` generation) shall comprise nine distinct content identities, each with its own
  dedicated screen composition, reusing the game's existing five-way terrain-palette grouping
  rather than requiring new palette budget.
- **Description:** The generator's biome-family domain shall be nine identities — the five
  already generated today (Water/Lake, Sand/Beach, Grass/Forest, Stone/Mountain, Brick/Castle)
  plus four folded in from the original, pre-procedural-generation zone set (Village, Cave,
  Desert, Plains) — so that every biome-identity screen this project has ever shipped art for is
  a reachable generation target, and none stays permanently orphaned. Each identity shall map
  onto one of the five existing terrain-palette groups (grass, sand/dirt, water, stone, brick/red
  — `GDS-08` §4), reusing the exact grouping the original nine-zone game already established
  (Forest+Plains→grass; Beach+Desert→sand/dirt; Lake→water; Mountain+Village+Cave→stone;
  Castle→brick/red) — no new BG palette slot is required.
- **Rationale:** Direct project-owner decision (`BL-0128`): "I'd like to merge the two sets
  keeping the art from both for use in the current game, there should be no art content and area
  definitions unused... the zone art should be added to the biome list, the biome list will
  include more art and biome options." Grounded in `R212`'s own Implementation Guidance ("reuse
  the existing terrain-family palette groups... as the biome-identity vocabulary... the adjacency
  grammar should be defined over these families **or a refinement of them**") and
  `08-presentation-architecture.md` §8's explicit deferral ("exact biome-family count and palette
  assignment for a specific `WorldScale` is deferred to the implementation package that sizes
  it") — this FR is the requirements-level exercise of a choice the architecture ladder already
  reserved, not a new architecture decision.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** None (a structural property of the generator's own domain, not a runtime input).
- **Outputs:** A biome-id domain of nine values (today: five) available to both `FR-9100`
  (finite-mode `REGION_GRAPH`) and `FR-10200` (Infinite Mode per-region materialization).
- **Preconditions:** None (structural).
- **Postconditions:** Every one of the nine biome identities (a) has a dedicated,
  fully-distinguishable screen composition (confirmed today for all nine — Notes), and (b) is a
  reachable generation target in both finite-mode and Infinite Mode worlds, replacing today's
  five-value domain.
- **Acceptance Criteria:** For any generated world (finite or Infinite Mode), a region's biome-id
  may take any of nine values, each rendering its own dedicated screen; a tile-family audit
  (mirroring `FR-4300`'s own T13.a-style method) confirms all nine identities are distinct and
  none renders another's tiles. Every one of the nine identities' assigned BG palette is one of
  the five existing terrain-palette groups — no BG palette index outside that existing five-slot
  set is introduced.
- **Dependencies:** FR-4300 (one biome per screen — extended, not superseded, to nine
  identities); FR-9100 (finite-mode generation, whose biome draw's numeric range this FR widens);
  FR-10200 (Infinite Mode generation, whose per-region biome-id representation this FR widens).
- **Verification Method:** Test (tile-family audit across all nine identities, mirroring
  `FR-4300`'s T13.a) / Inspection (palette-assignment audit against the five-group mapping named
  above).
- **Source Documents:** R212 Implementation Guidance; `08-presentation-architecture.md` §8;
  `07-data-model.md` §5 (confirms the palette-reuse headroom this FR relies on); `BL-0128`.
  Not yet implemented.
- **Related ADRs:** ADR-0009 (the biome-family concept this FR extends the domain of). No new ADR
  is needed for this specific count/mapping decision — see Rationale.
- **Notes:** **Screen art for all nine identities already exists and is unmodified** — confirmed
  by direct read of `tilemaps.py`: `beach_screen`/`forest_screen`/`mountain_screen`/
  `lake_screen`/`castle_screen` are already wired (the current five); `village_screen`/
  `cave_screen`/`desert_screen`/`plains_screen` are fully drawn but currently orphaned (defined,
  unreferenced by `ALL_SCREENS`/`REGION_GRAPH`'s dispatch). **Collectible-spawn content is not
  equally ready**: `IP-9070` deleted (not merely orphaned) the four unused `ZONE_COLLECTS` spawn
  lists when it consolidated to five biome-family-representative lists — reaching this FR's own
  Postcondition (b) for Village/Cave/Desert/Plains needs four freshly-authored spawn tables, a
  content-authoring task this FR does not itself resolve (flagged in
  `03-requirements-review.md`, routed to a future `07`/`08-content-authoring` package). **Two
  representation-level facts, not restated as requirement text per this skill's own
  implementation-independence rule, but worth a pointer for whichever package implements this
  FR:** finite-mode's `REGION_GRAPH` biome-id is stored as a full, unpacked byte (trivially
  widens from its current five-value range to nine); Infinite Mode's separate per-region
  streaming/materialization representation currently allocates only 3 bits to biome-id (max eight
  values) alongside a 4-bit connectivity field in the same byte — reaching nine values needs that
  byte's field widths re-apportioned, a real but self-contained implementation change (the byte
  does not need to grow) belonging to whichever `07`/`08-code-implementation` package implements
  `FR-10200`'s side of this FR.

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

## FR-7000 — Audio (target — 2026-07-16, new capability, not yet shipped, `BL-0127`)

*(formalizes `ADR-0019`; the first requirement group to use this capability's own FR-7xxx range —
confirmed unused before this delta by direct grep of the existing document.)*

### FR-7100 — Procedural biome-family sub-theme generation from the main theme

- **ID:** FR-7100
- **Title:** The system shall generate, at ROM-build time, one music sub-theme per biome-family
  identity by transposing and/or tempo-scaling the game's existing main theme.
- **Description:** For each of the nine biome-family identities `FR-4320` establishes, the build
  pipeline shall derive a sub-theme from the existing shipped main theme (`music.py`'s `SONG`,
  unchanged) by applying transposition (a shifted starting pitch) and/or uniform tempo/duration
  scaling — not by independently composing new melodic material. The main theme's own identity
  is one of the nine — either directly reused as its own biome-family's sub-theme, or the anchor
  every other sub-theme derives from — this FR does not require nine independently-transformed
  variations distinct from the main theme itself; it requires nine music selections total,
  covering all nine identities, related by the theme-and-variation technique `ADR-0019` decides.
- **Rationale:** `ADR-0019` points 1–4; `R217` (leitmotif/theme-and-variation precedent, the
  concrete transform menu); `FR-4320` (the nine-identity axis this FR's own sub-theme count
  targets).
- **Priority:** Must (target — not yet implemented)
- **Inputs:** The existing main theme's note sequence (`music.py`'s `SONG`); `FR-4320`'s
  nine-identity set.
- **Outputs:** Nine music data sequences (one per biome-family identity), compiled into ROM
  exactly as the existing single track already is.
- **Preconditions:** None (a build-time, not runtime, generation step — `ADR-0019` point 2).
- **Postconditions:** Every one of the nine biome-family identities has an associated,
  playable music sequence.
- **Acceptance Criteria:** For each of the nine biome-family identities, the built ROM contains a
  distinct, playable music data sequence; every non-main-theme sequence's note sequence is
  derivable from the main theme's own via transposition and/or duration scaling alone (no
  independently-composed melodic material) — checkable by direct comparison of the generated
  sequence's own frequency/duration values against the main theme's, confirming a pure transform
  relationship.
- **Dependencies:** FR-4320 (the nine-identity set this FR's own generation target is sized
  against).
- **Verification Method:** Test (direct comparison of each generated sequence's data against the
  main theme's own, confirming the transform relationship; a build-time unit-test-style check,
  mirroring `worldgen.py`'s own oracle-comparison precedent in spirit, though this FR's own
  generation has no separate runtime routine to compare against — see `ADR-0019` point 3).
- **Source Documents:** `ADR-0019` points 1–4; `R217`.
- **Related ADRs:** ADR-0019.
- **Notes:** Not yet implemented. **Explicitly does not require a new build-side sibling module**
  (`ADR-0019` point 3's own reasoning: no runtime/oracle lockstep discipline applies here, unlike
  `worldgen.py`'s) — the generation function belongs inside `music.py` itself, called from
  `build_rom.py`. **Explicitly excludes the shared-ostinato/second-APU-channel transform option**
  (`ADR-0019` point 5) — a future revision could extend this FR to cover it, not assumed here.

### FR-7110 — Biome-family-identity-keyed sub-theme playback selection

- **ID:** FR-7110
- **Title:** During `PLAYING`, the system shall play the music sub-theme matching the current
  region's biome-family identity; the main theme shall play outside gameplay.
- **Description:** Mirroring the existing HUD zone-name-label mechanism's own trigger shape (which
  already reads and displays the current region's identity every frame), the system shall select
  which of `FR-7100`'s nine generated sub-themes plays based on the player's current region's
  biome-family identity while in `PLAYING` (either mode — finite or Infinite, both of which share
  the same biome-family identity axis per `FR-4320`); outside `PLAYING` (title, menus, and other
  non-gameplay states), the main theme plays.
- **Rationale:** `ADR-0019` point 6.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** The current region's biome-family identity (finite mode: `REGION_GRAPH`'s biome-id
  byte via `CUR_ZONE`; Infinite Mode: `INF_WINDOW`'s center-cell biome-id — both already read by
  the existing screen-dispatch mechanism, `FR-4310`/`FR-4320`, this FR's own input is the
  identical value, not a new read).
- **Outputs:** The currently-playing music track switches to match the selected sub-theme (or the
  main theme, outside `PLAYING`).
- **Preconditions:** `FR-7100`'s nine sub-themes exist in the built ROM.
- **Postconditions:** The music track playing at any given moment always matches the player's
  current context (region identity during `PLAYING`, main theme otherwise) — never a stale or
  mismatched track.
- **Acceptance Criteria:** For each of the nine biome-family identities, entering a region of that
  identity during `PLAYING` (either mode) results in that identity's own sub-theme playing, within
  one frame of the region becoming current; entering any non-`PLAYING` state results in the main
  theme playing.
- **Dependencies:** FR-7100 (the sub-themes this FR selects between); FR-4310/FR-4320 (the
  biome-family identity value this FR's own selection reads, unchanged, not redefined here).
- **Verification Method:** Test (drive each of the nine identities via direct force or live
  generation, mirroring this session's own established direct-force verification pattern for
  biome-family dispatch, and confirm the correct track is selected).
- **Source Documents:** `ADR-0019` point 6.
- **Related ADRs:** ADR-0019.
- **Notes:** Not yet implemented. **This FR decides the selection's *shape* (identity-keyed) only
  — the exact `GAMESTATE`/WRAM mechanism (a new `CURRENT_THEME` pointer, a dispatch cascade
  mirroring `dsr_p_dispatch`'s own shape, or another approach) is `06-feature-specification`'s/
  `07-implementation-planning`'s own scope**, per this stage's own SHALL-NOT-invent-implementation
  rule (mirroring `FR-1200`'s own precedent for leaving a comparable dispatch mechanism
  undecided at this level). **Real sequencing dependency, not a blocker to this FR's own
  baselining**: this FR's eventual implementation needs `FR-4320`'s own packages
  (`IP-1105`/`IP-1033`/`IP-1022`/`IP-1106`, all unauthorized as of this delta) to have shipped
  first, since it reads the same widened biome-id domain those packages establish — named here,
  not resolved, per `ADR-0019`'s own identical note.

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
  implemented. **2026-07-11 delta:** this FR's own "adjacency edges" output was never specified
  as necessarily complete — `FR-9140` (`ADR-0012`) narrows how that output is constructed (a
  maze, not a full lattice); no change to this FR's own text was needed. **2026-07-11 delta
  (`IP-9110`, `BL-0074`/`ADR-0014`):** the shipped `gw_prng_step` mixing step degenerated to a
  fixed point/short cycle for effectively every seed, producing majority-Water worlds for a
  large fraction of `scale=9` generations — a defect in the *implementation* of this FR's own
  determinism guarantee, not in the guarantee's text. Repaired to a period-sound shift triplet
  (`worldgen.py`'s oracle updated in lockstep); this FR's own acceptance criterion (byte-identical
  output for identical `(seed, scale)`) continued to hold throughout, since the defect was a
  quality-of-output problem, not a determinism problem. No FR/NFR currently states a testable
  "the PRNG shall not degenerate" criterion — flagged as a candidate for a future
  `04-requirements-engineering` pass, not resolved here.

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
  post-generation check that could fail and be silently accepted. **2026-07-11 delta:** once
  `FR-9140` (`ADR-0012`) ships, this guarantee's *mechanism* changes from "incidental to full
  lattice connectivity" to "structural — a spanning tree connects every node by definition" —
  strictly stronger, not weaker; this FR's own text needed no change.

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
  construction** (ADR-0009) — a stronger guarantee than the shipped model's. **Correction
  (2026-07-12): this rule was in fact implemented and independently verified** — `IP-1020`
  shipped it, confirmed by `VR-1020`'s own audit (`T12.e`) — this document's prior "Not yet
  implemented" framing was stale, a documentation-only correction unrelated to the point below.
  **Superseded (2026-07-13, `IP-1021`):** this rule's implementation has now shipped over —
  `generate_world` no longer places exactly one `KeyItem` per region; **FR-9160** is the
  authoritative requirement for `KeyItem` placement going forward. This FR's text above is left
  unmodified as an accurate historical record of the rule as it stood through `IP-1020`'s
  lifetime, per the `FR-1120`→`FR-1170`/`1180`/`1190` precedent's own second step.

### FR-9140 — Maze-shaped region adjacency (implemented — 2026-07-11)

- **ID:** FR-9140
- **Title:** The system shall generate region adjacency edges as a maze — a spanning tree plus a
  braided subset of the remaining candidate edges — rather than connecting every grid-adjacent
  region pair.
- **Description:** After biome assignment (`FR-9100`) completes for a generated world, the
  system shall generate the world's adjacency structure in a second, independent pass: build a
  spanning tree over the full candidate edge set (every grid-adjacent region pair), guaranteeing
  every region is reachable (`FR-9120`); then, for every candidate edge not selected by the
  spanning tree, reopen it according to `FR-9150`'s braid-fraction parameter. The resulting
  adjacency graph — not the full grid graph — is what the region graph's neighbor data exposes to
  navigation (`check_zone_transition`) and rendering (`dsr_p`/`draw_region_arrows`).
- **Rationale:** `BL-0064` (owner design request, 2026-07-11): a Zelda/Pokémon-style overworld —
  distinct regions connected by paths, not a uniformly open grid. `ADR-0012` (refines `ADR-0009`
  Decision point 1, which never itself mandated full connectivity).
- **Priority:** Must (implemented — `IP-1070`, T19)
- **Inputs:** The full candidate edge set (every grid-adjacent region pair, a pure function of
  `WORLD_SCALE`); `SEED`-derived PRNG state; `FR-9150`'s braid-fraction value.
- **Outputs:** The generated region graph's adjacency edges — a subgraph of the full grid graph.
- **Preconditions:** Biome assignment (`FR-9100`) has completed for this world.
- **Postconditions:** The resulting adjacency graph is a (not-necessarily-strict) subgraph of the
  full grid graph; every region remains reachable from the starting region (`FR-9120`); every
  edge that does exist remains grammar-legal (`FR-4310`, unaffected — see that FR's Notes).
- **Acceptance Criteria:** For any `(seed, scale, braid-fraction)` combination in a test corpus:
  (a) every edge in the generated graph also exists in the full grid graph (no adjacency is
  invented that isn't grid-adjacent); (b) every region is reachable from the starting region; (c)
  regenerating from identical inputs produces byte-identical adjacency output, matching
  `FR-9100`'s existing determinism guarantee extended to this pass.
- **Dependencies:** FR-9100, FR-9120, FR-9150.
- **Verification Method:** Test (property test across a `(seed, scale, braid-fraction)` corpus,
  extending `R305`'s existing pattern; a specific subgraph-of-full-lattice check, since this is a
  genuinely new property the prior full-lattice model never needed).
- **Source Documents:** `BL-0064`; `ADR-0012`.
- **Related ADRs:** ADR-0009, ADR-0012, ADR-0013.
- **Notes:** Implemented `IP-1070` (2026-07-11): `asm_game.py`'s `generate_world` runs an iterative
  randomized DFS/recursive-backtracker spanning-tree carve, then a canonical-edge (down/right only)
  braid/prune pass, immediately after biome assignment. `worldgen.py`'s `_carve_maze` mirrors it
  step-for-step (validated byte-identical across a 36-`(seed,scale)` corpus). Does not change
  `FR-9100`'s own text — that FR's "adjacency edges" output was never specified as necessarily
  complete; this FR narrows how that output is actually constructed. `REGION_GRAPH`'s WRAM/ROM
  data format (`GDS-07`) is unaffected — only the generation algorithm populating it changes
  (`ADR-0012` point 2); `dsr_p`/`draw_region_arrows` (`IP-1030`, `FR-2320`) and
  `check_zone_transition` (`IP-9050`, `FR-2300`) required no code changes, since both already
  consume the graph's neighbor bytes generically (confirmed by T19/T17's non-regression). Every
  `gw_prng_step` draw this pass makes is decorrelated via `ADR-0013`'s loop-local counter-XOR
  perturbation, since the shipped PRNG degenerates under this pass's repeated back-to-back draws
  ([R113](../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md)) — `gw_prng_step`
  itself and `FR-9100`'s own biome-assignment draw are untouched.

### FR-9150 — Braid-fraction parameter (implemented — 2026-07-11)

- **ID:** FR-9150
- **Title:** The system shall control what fraction of `FR-9140`'s pruned edges the braid pass
  reopens via a single configurable parameter.
- **Description:** The braid pass (`FR-9140`) shall, for each candidate edge not selected by the
  spanning tree, draw one PRNG value and reopen that edge if the drawn value is at or below a
  fixed braid-fraction threshold. This requirement establishes the parameter's existence, valid
  range, and a fixed initial default; **whether the value becomes player-adjustable (a new
  SEED/SCALE ENTRY field, a value derived from another player input, or remains a fixed
  non-exposed constant) is explicitly not decided by this requirement** — see this document's
  companion Requirements Review finding.
- **Rationale:** `BL-0065` (owner design request, 2026-07-11): a maze-difficulty scaling
  variable. `ADR-0012` fixed the mechanism (a single-byte PRNG-vs-threshold draw per pruned
  edge) but explicitly left the default value and UI exposure to this stage.
- **Priority:** Must (target — not yet implemented)
- **Inputs:** None from the player, at this requirement's own scope (a fixed default — see
  Notes); PRNG state, per pruned edge.
- **Outputs:** A single byte-valued threshold consumed by `FR-9140`'s braid pass.
- **Preconditions:** `FR-9140`'s spanning-tree pass has completed (pruned edges are known).
- **Postconditions:** The fraction of pruned edges actually reopened approximates the configured
  threshold (a probabilistic, not exact, guarantee — each edge's reopening is an independent draw).
- **Acceptance Criteria:** For a large `(seed, scale)` corpus at a fixed threshold value, the
  observed fraction of reopened edges falls within a statistically reasonable band of the
  threshold's implied probability (not exact-equality, since this is a per-edge independent
  random process).
- **Dependencies:** FR-9140.
- **Verification Method:** Test (statistical corpus check, extending `R305`'s existing
  property-test pattern to a probabilistic property — a new kind of check this baseline hasn't
  needed before).
- **Source Documents:** `BL-0065`; `ADR-0012`.
- **Related ADRs:** ADR-0012.
- **Notes:** Implemented `IP-1070` (2026-07-11) as `GW_BRAID_THRESHOLD = 63` (a fixed code-level
  constant, `~63/255`), reopening ~25% of pruned edges — measured 25.80% across a 345-edge, 15-
  `(seed,scale)`-combination corpus (T19.e). The UI-exposure question (a new SEED/SCALE ENTRY
  field, a derived value, or the fixed non-exposed default this FR shipped with) remains
  undecided, as this FR's own text always allowed.

### FR-9160 — Scale-relative, dead-end-prioritized KeyItem placement (implemented — 2026-07-13)

- **ID:** FR-9160
- **Title:** The system shall generate exactly `WORLD_SCALE` KeyItems per generated world,
  prioritizing pre-braid maze dead-end regions, with any shortfall filled by randomly-selected
  additional regions.
- **Description:** Supersedes `FR-9130`'s "exactly one per region" rule. At the exact point the
  spanning-tree carve completes and before the braid pass runs (`FR-9140`), the system shall
  identify every region whose spanning-tree degree is exactly 1 (a leaf — no other region's
  parent points to it, and it is not the root). If the leaf count is `>= WORLD_SCALE`, the system
  shall place a `KeyItem` in `WORLD_SCALE` of those leaf regions. If the leaf count is
  `< WORLD_SCALE`, the system shall place a `KeyItem` in every leaf region, then place the
  remainder in additional regions chosen randomly (excluding regions already selected) until
  exactly `WORLD_SCALE` regions hold a `KeyItem`. Every other region holds none.
- **Rationale:** `ADR-0015` (`BL-0093`, project-owner direct decision resolving `BL-0081`/`R215`).
- **Priority:** Must (implemented by `IP-1021`, `COMPLETE`; `VERIFIED` pending)
- **Inputs:** `WORLD_SCALE`; the pre-braid spanning tree's own per-region degree (`GDS-07` §7c).
- **Outputs:** Exactly `WORLD_SCALE` regions marked as holding a `KeyItem`; every other region
  marked as holding none.
- **Preconditions:** The spanning-tree carve (`FR-9140`) has completed; the braid pass has not yet
  run.
- **Postconditions:** Exactly `WORLD_SCALE` regions hold a `KeyItem`, snapshotted from pre-braid
  leaf status and therefore unaffected by which edges the braid pass subsequently reopens.
- **Acceptance Criteria:** For any `(seed, scale)` in a test corpus: (a) exactly `WORLD_SCALE`
  regions are marked as holding a `KeyItem`; (b) every pre-braid leaf region is marked as holding
  one, up to `WORLD_SCALE`; (c) when pre-braid leaf count is below `WORLD_SCALE` (a confirmed
  common case at `WORLD_SCALE` ≤ 7, per `R215`'s measured data), the shortfall is filled by
  additional regions until the total reaches exactly `WORLD_SCALE`; (d) the placement decision is
  unchanged by which edges the braid pass reopens (verifiable by comparing the pre-braid and
  post-braid `REGION_GRAPH` state against the same placement result).
- **Dependencies:** FR-9100, FR-9140, FR-3220 (the item-agnostic collection mechanic this
  placement feeds — unaffected by this FR).
- **Verification Method:** Test (property test across a `(seed, scale)` corpus, extending
  `FR-9130`'s retired T1.11/T12.e pattern) / Inspection (static check that the placement decision
  is made before the braid pass's own call site, mirroring `T20.d`'s established static-audit
  precedent for a similar pipeline-ordering requirement).
- **Source Documents:** `ADR-0015`; `GDS-04` delta (2026-07-12 correction); `GDS-07` §7c.
- **Related ADRs:** ADR-0015, ADR-0012 (the maze pass this decision's leaf data comes from),
  ADR-0009.
- **Notes:** Supersedes `FR-9130` (see that FR's own Notes for the reverse pointer). The exact
  per-region data representation `GDS-07` §7c names as needed was resolved by `IP-1021` §6: the
  existing `KEYITEM_FLAGS` value domain was widened in place to a tri-state (0=present/
  uncollected, 1=present/collected, 2=absent) rather than adding a new bitmap — implemented
  2026-07-13, `test_rom.py` T12.e (revised)/T12.n, oracle-mirrored in `worldgen.py`.

### FR-9161 — Scale-relative victory condition (implemented — 2026-07-13)

- **ID:** FR-9161
- **Title:** The system shall trigger victory the instant `KeyItemCount` reaches `WORLD_SCALE`.
- **Description:** Supersedes `FR-3300`'s fixed "reaches 9" threshold. During PLAYING, the instant
  `KeyItemCount` equals `WORLD_SCALE` (read directly), the system shall trigger the PLAYING →
  VICTORY transition (`FR-1160`).
- **Rationale:** `ADR-0015` (`BL-0093`).
- **Priority:** Must (implemented by `IP-1021`, `COMPLETE`; `VERIFIED` pending)
- **Inputs:** `KeyItemCount` value; `WORLD_SCALE` value.
- **Outputs:** Victory transition trigger (`FR-1160`).
- **Preconditions:** State is PLAYING; `KeyItemCount == WORLD_SCALE`.
- **Postconditions:** The victory transition fires.
- **Acceptance Criteria:** For any `WORLD_SCALE` in `{2..9}`, victory fires the instant
  `KeyItemCount` reaches that world's own `WORLD_SCALE` value — not before, and not requiring a
  fixed count independent of `WORLD_SCALE`.
- **Dependencies:** FR-9160 (the placement rule that makes `WORLD_SCALE` always achievable),
  FR-1160, FR-3220.
- **Verification Method:** Test.
- **Source Documents:** `ADR-0015`.
- **Related ADRs:** ADR-0015.
- **Notes:** Supersedes `FR-3300` (see that FR's own Notes for the reverse pointer). Always
  achievable by construction: `FR-9160` guarantees exactly `WORLD_SCALE` `KeyItem`s exist, and
  `FR-9120`'s full-reachability guarantee (unaffected by this decision) ensures every one of them
  is reachable. Implemented 2026-07-13 (`IP-1021`): `check_complete` reads `WORLD_SCALE` at
  runtime in place of the old hardcoded `9`; `test_rom.py` T4.8 (corrected)/T12.n.

### FR-9170 — Finite-mode biome-blob clustering via per-super-cell positional hash

- **ID:** FR-9170
- **Title:** The system shall bias finite-mode biome assignment toward cohesive multi-region
  "blobs," using a deterministic per-super-cell positional hash layered on the existing
  grammar-constrained draw — never replacing it.
- **Description:** The `scale`×`scale` grid shall be partitioned into fixed-size super-cells, each
  with a target biome-id (`0`–`8` per `FR-4320`'s nine-identity axis — `0`–`4` prior to that FR)
  derived once via `hash(SEED, supercell_row, supercell_col)` — the same shift/XOR-only reseed
  construction `FR-9100`'s own generation routine already uses. For each non-root region, the
  system shall first compute its legal biome range `[lo, hi]` exactly as today (the intersection
  of its already-placed top/left neighbors' biome-ids ±1, clamped to `[0, 8]` per `FR-4320`'s
  domain — unchanged in mechanism by this FR, only in the clamp's own upper bound).
  If the region's own super-cell target lies within `[lo, hi]`, the system shall set that region's
  biome-id directly to the target, consuming no PRNG draw for that region. If the target lies
  outside `[lo, hi]`, the system shall fall back to today's unbiased `anchor + delta` draw,
  entirely unchanged, consuming one PRNG draw exactly as now.
- **Rationale:** `ADR-0018` (`BL-0066`/`CR-05`, resolving a project-owner request via direct user
  instruction, 2026-07-14: "If there is a blob mechanism that works for infinite mode, use that
  concept for the finite mode as well.").
- **Priority:** Must (target — not yet implemented)
- **Inputs:** `SEED`; `WORLD_SCALE`; the super-cell size (an implementation-time tuning constant,
  not fixed by this FR — see Notes); each region's own already-computed `[lo, hi]` range.
- **Outputs:** Each non-root region's biome-id, either snapped to its super-cell's target or drawn
  via the existing unbiased mechanism.
- **Preconditions:** `SEED`/`WORLD_SCALE` are set (`FR-1180`); region `(0,0)`'s hardcoded `Grass`
  anchor has already been placed (unaffected by this FR — the bias applies only from region index
  1 onward, per `ADR-0018` point 6).
- **Postconditions:** Every region's biome-id is grammar-valid (`FR-4310` — adjacent regions'
  biome-ids differ by at most 1, unaffected by this FR); regions within a super-cell whose target
  is locally grammar-compatible read as a cohesive, uniform-biome area; regions at a boundary
  between differently-targeted super-cells still fall back to a gradual `±1`-per-step transition,
  with no separate transition-zone logic.
- **Acceptance Criteria:** For a corpus of `(seed, scale)` pairs: (a) every region whose super-cell
  target lies within its own `[lo, hi]` range has a biome-id exactly equal to that target; (b)
  every region whose target lies outside `[lo, hi]` has a biome-id produced by the existing
  `anchor + delta` draw, unchanged from `FR-9100`'s own pre-existing behavior; (c) the full
  grammar-validity invariant (`FR-4310`) holds for every generated edge; (d) generating the same
  `(seed, scale)` pair twice — including via the Python reference-generator oracle vs. the SM83
  routine — produces byte-identical output both times (extends `FR-9100`'s own determinism
  guarantee to the new snap/fallback branch, per `ADR-0018` point 8's explicit requirement that
  the oracle and the SM83 routine agree on the branch condition byte-for-byte, not merely the
  draw's outcome).
- **Dependencies:** FR-9100 (the generation routine this bias layers onto), FR-4310 (the
  grammar-validity invariant this FR must preserve, not merely avoid violating), FR-4320
  (**2026-07-16 delta, `BL-0128`:** the biome-id domain and clamp bound this FR's own snap/
  fallback mechanism operates over is now defined by `FR-4320`, not restated independently here).
- **Verification Method:** Test (property test across a `(seed, scale)` corpus, mirroring
  `FR-9100`'s own determinism-test shape, extended with the snap/fallback branch-condition
  comparison `ADR-0018` point 8 requires) / Inspection (static audit confirming the per-region
  draw is skipped exactly when the snap branch fires, mirroring `T20.d`'s established
  pipeline-ordering static-audit precedent).
- **Source Documents:** `ADR-0018`; `ADR-0009` point 2 (the existing draw this FR biases, cited
  verbatim, not restated).
- **Related ADRs:** ADR-0018, ADR-0009 (refined, not superseded — points 1, 3–7 unaffected),
  ADR-0012 (explicitly not touched — this FR needs no maze-pass reordering, which is the whole
  reason it resolves `CR-05`'s original conflict rather than reopening it).
- **Notes:** Resolves `CR-05`/`BL-0066` — see `CR-05`'s own entry below for the closed-out
  resolution trail. **Super-cell size is not fixed by this FR** — `ADR-0018`'s own Consequences
  section names this an explicit implementation-time tuning question (`BL-0110`, `SCHEDULED`,
  rides a future `07-implementation-planning` pass), mirroring `ADR-0017`'s own precedent for
  leaving its density constant `K` open at the requirements level. Not yet implemented. This FR
  is deliberately silent on PRNG draw *count* per generation — `ADR-0018`'s own Consequences
  section notes the count is no longer fixed at exactly one draw per non-root region, and that no
  currently-baselined requirement assumes a fixed count (`T12`'s existing checks assert
  determinism/reachability/grammar-validity, not draw count) — flagged there, not restated as a
  new constraint here. **2026-07-16 delta (`BL-0128`):** Description/Dependencies updated for
  `FR-4320`'s nine-value biome-id domain (widened from the prior `[0, 4]` clamp to `[0, 8]`) —
  this FR's own snap/fallback *mechanism* is unaffected; only the numeric range it operates over
  changed.

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

## FR-10000 — Infinite Mode (target — 2026-07-13, new capability, not yet shipped)

*(formalizes [ADS-001](../architecture/ADS-001-streaming-infinite-world-generation.md),
[ADR-0016](../architecture/adr/ADR-0016-streaming-infinite-mode-generation-architecture.md),
[ADR-0017](../architecture/adr/ADR-0017-infinite-mode-treasure-placement-and-win-condition.md) —
a second, additive world-generation mode selectable alongside FR-9000's finite mode; none of
FR-9000's own leaves are amended or superseded by this group)*

### FR-10100 — Infinite Mode new-game entry (seed-only, no world-scale)

- **ID:** FR-10100
- **Title:** The system shall offer Infinite Mode as a distinct new-game choice, accepting a seed
  value only — no world-scale parameter.
- **Description:** At new-game creation, the system shall let the player choose between Finite
  Mode (FR-1180's existing seed+scale flow) and Infinite Mode. Choosing Infinite Mode shall
  accept a seed value (the same 16-bit domain FR-1180/ADR-0010 already establish) and no
  world-scale value — Infinite Mode has no fixed grid extent for a scale to bound.
- **Rationale:** ADR-0016 point 1; ADS-001 §System Architecture ("Infinite mode (new, this
  synthesis): (seed) alone — no scale").
- **Priority:** Must (**Implemented, 2026-07-14, `IP-1100`** — mode-choice half; region
  materialization for the starting region is `IP-1101`'s own scope, already Implemented)
- **Inputs:** A mode selection (Finite/Infinite); a seed value if Infinite Mode is chosen.
- **Outputs:** A new save whose generation model is Infinite Mode, seeded from the given value.
- **Preconditions:** The player is at the new-game creation flow (FR-1180's existing entry point).
- **Postconditions:** The new save's generation mode (Finite or Infinite) and seed are fixed for
  the life of that save, mirroring FR-9110's existing immutability guarantee for the finite mode.
- **Acceptance Criteria:** Choosing "new game" presents a mode choice (Finite/Infinite) before
  either mode's own entry step; selecting Infinite Mode presents a seed-entry step only (no scale
  step); the resulting save's mode is recorded and does not change without starting a new game;
  cancelling out of the mode choice returns to the point "new game" was chosen from, without
  recording any mode or seed; cancelling out of Infinite Mode's own seed-entry step returns to the
  mode choice (not past it), also without recording any mode or seed. The Finite Mode path's own
  existing seed/scale entry screen and its own existing cancel behavior are unaffected by this FR
  — selecting Finite Mode reaches that unchanged flow, not a new one.
- **Dependencies:** FR-1180 (the existing new-game entry flow this extends), FR-9110 (the
  immutability pattern this mirrors for Infinite Mode's own seed).
- **Verification Method:** Test (drive the new-game flow, confirm no scale-entry step appears
  for Infinite Mode and the recorded mode/seed match the player's input).
- **Source Documents:** ADR-0016 point 1; ADS-001 §System Architecture; `GDS-01` §4d (the
  mode-selection UI shape, landed 2026-07-14).
- **Related ADRs:** ADR-0016.
- **Notes:** **Implemented, `IP-1100`, 2026-07-14** — `T25` (10 checks): `GS_MODE_SELECT`/
  `GS_INFINITE_SEED_ENTRY` reachable exactly per `GDS-01` §4d's own diagram, including the named
  asymmetric-cancel-path tradeoff (`T25.b1c`); `GAME_MODE` written only on `MODE SELECT`'s own
  "infinite" A-confirm, never on mere highlight or cancel (`T25.c1b`); `INFINITE SEED ENTRY`'s own
  A-confirm calls `IP-1102`'s `inf_ensure_window` (not a single direct `inf_materialize_region`
  call as this package's own §6 text — written before `IP-1102` existed — originally described;
  reusing the already-built full-window routine avoids duplicating its 9-cell logic and avoids
  leaving `INF_WINDOW`'s 8 non-center cells uninitialized). **`GDS-01` §4d landed 2026-07-14**
  (`BL-0113`, resolving what this Notes field previously flagged as missing) and names the concrete UI shape this FR's own Acceptance Criteria above now reflects:
  a `MODE SELECT` cursor menu (reusing `MAIN MENU`'s own convention) forking into the Finite
  mode's completely unchanged `SEED/SCALE ENTRY` flow or a new seed-only `INFINITE SEED ENTRY`
  state. `GDS-01` §4d also names a deliberate, out-of-scope-for-this-FR asymmetry: `SEED/SCALE
  ENTRY`'s own already-shipped (`IP-1040`) cancel target (straight to `MAIN MENU`) is preserved
  unchanged rather than redirected through `MODE SELECT`, while `INFINITE SEED ENTRY`'s own
  cancel target is `MODE SELECT` — a UI/state-machine implementation choice this FR's Acceptance
  Criteria states at the observable-behavior level ("returns to the point `new game` was chosen
  from" vs. "returns to the mode choice") without naming the underlying asymmetry's own
  rationale, which `GDS-01` §4d owns. This FR still does not name exact `GameState` values or
  WRAM addresses — that remains `07`/`08`'s scope (`IP-1100`'s own package already resolves
  those choices).

### FR-10200 — Streaming, positionally-deterministic region generation

- **ID:** FR-10200
- **Title:** In Infinite Mode, the system shall compute each region's biome and maze
  connectivity as a pure function of (seed, row, col), materialized only when the player
  approaches that region — never as an upfront whole-grid pass.
- **Description:** Unlike FR-9100's finite-mode generation (one global pass over the entire
  `scale`×`scale` grid at new-game creation), Infinite Mode shall derive each region's biome and
  connectivity on demand, at the moment the player approaches it, using a per-region reseeded
  PRNG instance derived from `SEED` XOR/shift-mixed with `(row, col)` — never from replayed
  generation history. Regions outside a small materialized window around the player are not held
  in memory.
- **Rationale:** ADR-0016 points 2–3; R114 (the positional-determinism finding this decision is
  grounded in — the shipped finite-mode algorithm's two global-sequential dependencies are not
  directly streamable, requiring this different, positionally-deterministic construction).
- **Priority:** Must (**Implemented, 2026-07-14, `IP-1101`+`IP-1102`** — the per-region
  generation half: `inf_materialize_region`/`worldgen.materialize_region` produce a region's
  biome/connectivity as a pure function of `(SEED, row, col)`, `T22` (7 checks); the streaming
  materialized-window management (`inf_ensure_window`), transition-triggered materialization
  (`czt_infinite`), and render integration (`dsr_p`'s `GAME_MODE`-gated dispatch,
  `draw_region_arrows_inf`) are `IP-1102`'s own scope, `T24` (7 checks).)
- **Inputs:** SEED (Infinite Mode's own, per FR-10100); the region coordinate `(row, col)` the
  player is approaching.
- **Outputs:** That region's biome assignment and maze connectivity (which of its up to four
  grid-adjacent neighbors are open).
- **Preconditions:** An Infinite Mode save is active (FR-10100); the player's movement has
  triggered materialization of a not-yet-resident region.
- **Postconditions:** The materialized region's biome/connectivity depend only on
  `(SEED, row, col)` — never on the order regions were visited, nor on any other region's own
  materialization history.
- **Acceptance Criteria:** Materializing the same `(row, col)` twice — in the same session, or
  after the region has left and re-entered the materialized window — produces byte-identical
  biome/connectivity output both times, for a corpus of `(seed, row, col)` triples.
- **Dependencies:** FR-10100.
- **Verification Method:** Test (positional-determinism property test — re-materialize a corpus
  of previously-materialized regions and confirm identical output — mirroring FR-9100's own
  determinism test shape, extended to per-region rather than whole-graph scope).
- **Source Documents:** ADR-0016 points 2–3; R114 §Concepts/§Implementation Guidance.
- **Related ADRs:** ADR-0016.
- **Notes:** **Implemented (`IP-1101`+`IP-1102`, 2026-07-14)** — see Priority above. The maze
  algorithm is the Binary Tree family (ADR-0016 point 4), operationalized as a "carve north or
  west" bias per region with south/east openness read from the corresponding neighbor's own
  bias (no grid-boundary special case — Infinite Mode's world is unbounded, confirmed by direct
  implementation, not merely asserted); its own aesthetic acceptability (directional corridor
  bias) is not decided by this FR, tracked separately (`BL-0107`, routed to
  `02-research-game-design`/`09-content-review` once a package exists to review). `IP-1102`'s own
  `inf_ensure_window` recomputes the full 3×3 window fresh on every center change (no incremental
  shift logic) — see NFR-1400's own updated status for this design choice's measured cost.
  Materialization-window sizing against bank-0's WRAM headroom is an NFR concern (NFR-4300
  below), owned by `IP-1102`, not restated here.

### FR-10210 — Revisit-consistent region materialization

- **ID:** FR-10210
- **Title:** Walking away from an Infinite Mode region and back shall reproduce the identical
  region — biome, connectivity, and (if not yet collected) its treasure state.
- **Description:** When a previously-materialized region leaves the materialized window (per
  FR-10200) and the player later re-approaches it, the system shall re-derive that region and
  produce output identical to its first materialization, except for any treasure the player has
  since collected (which stays collected, per FR-10500's persisted ledger).
- **Rationale:** ADS-001 §User Stories ("walking away from a region and back reproduces the
  identical region... because both are pure functions of (seed, row, col), not of my own path
  history"); a direct consequence of FR-10200's positional-determinism guarantee, stated
  separately because it is the player-observable property that guarantee exists to deliver.
- **Priority:** Must (**partially implemented, 2026-07-14, `IP-1101`** — `T22.c` confirms the
  data-layer revisit-consistency property (re-materializing after an intervening call
  reproduces the first result byte-for-byte). The player-observable, materialized-window-based
  revisit path — and the treasure-state-preserved-through-collection half, which depends on
  `IP-1104`'s own ledger — are not yet implemented, `IP-1102`/`IP-1104`'s own scope.)
- **Inputs:** A region coordinate the player is re-approaching after it left the materialized
  window.
- **Outputs:** The re-materialized region's biome, connectivity, and treasure-presence/collected
  state.
- **Preconditions:** The region was previously materialized at least once (FR-10200) during the
  current save's play history.
- **Postconditions:** The re-materialized region's biome and connectivity exactly match the
  first materialization; its treasure state reflects the persisted ledger (FR-10500), not a
  fresh re-roll.
- **Acceptance Criteria:** For a corpus of `(seed, row, col)` triples, materializing, evicting
  (simulated by re-deriving from scratch rather than from cached in-memory state), and
  re-materializing produces identical biome/connectivity, and — for a region whose treasure was
  collected between the two materializations — the treasure reads as collected on the second.
- **Dependencies:** FR-10200, FR-10500.
- **Verification Method:** Test (re-derive-from-scratch comparison, since a streaming
  implementation's correctness specifically depends on not relying on cached state that a real
  materialized-window eviction would discard).
- **Source Documents:** ADR-0016 points 2, 5; ADS-001 §User Stories.
- **Related ADRs:** ADR-0016.
- **Notes:** **Partially implemented (`IP-1101`, 2026-07-14)** — see Priority above.

### FR-10300 — Treasure placement decoupled from maze structure

- **ID:** FR-10300
- **Title:** In Infinite Mode, a region shall hold treasure if and only if
  `hash(SEED, row, col) mod K == 0`, for a tuned density constant K — independent of that
  region's maze connectivity or dead-end status.
- **Description:** Unlike FR-9160's finite-mode placement (dead-end-prioritized, read from the
  spanning-tree's own leaf structure), Infinite Mode shall place treasure using the same
  per-region positional-hash technique FR-10200 uses for biome/connectivity, evaluated against a
  tuned density constant `K` — computable the instant a region is materialized, with no
  dependency on maze-carve completion or connectivity degree.
- **Rationale:** ADR-0017 point 1; R216 (resolves R114's finding that the cheapest
  streaming-compatible maze algorithm, Binary Tree, has zero dead-ends in two of four
  directions — a direct conflict with a literal dead-end-only rule). This is a deliberate,
  named departure from `BL-0094`'s original "at dead ends" wording, not a silent substitution —
  see Notes.
- **Priority:** Must (**Implemented** — the presence-predicate half 2026-07-14, `IP-1101`
  (`hash(SEED, row, col) mod K == 0`, `K=16`, `T22.d` measures 6.25%, matching target); the
  collection half 2026-07-16, `IP-1103` (reusing `check_collisions`' existing collision-point
  convention on a spawned type-2 item, `T26.a`/`T26.b`).)
- **Inputs:** SEED; the region coordinate `(row, col)`; the tuned density constant `K`.
- **Outputs:** A boolean treasure-presence value for that region.
- **Preconditions:** The region has been materialized (FR-10200).
- **Postconditions:** Treasure-presence for a given region is a pure function of
  `(SEED, row, col, K)` — never of maze connectivity, dead-end status, or generation order.
- **Acceptance Criteria:** For a corpus of `(seed, row, col)` triples, treasure-presence matches
  the `hash(SEED, row, col) mod K == 0` predicate exactly, regardless of that region's maze
  connectivity.
- **Dependencies:** FR-10200.
- **Verification Method:** Test (property test against the hash predicate, mirroring FR-9160's
  own placement-verification shape).
- **Source Documents:** ADR-0017 point 1; R216 §Concepts/§Implementation Guidance.
- **Related ADRs:** ADR-0017.
- **Notes:** **Partially implemented (`IP-1101`, 2026-07-14)** — see Priority above. **`K`'s
  exact value is an implementation-time tuning question, not fixed by this FR** — ADR-0017
  recommends anchoring near R215's measured `scale=9` finite-world dead-end density (~6.4%) as a
  starting point; `07-implementation-planning` settled `K=16` (a power-of-two divisor, `AND
  0x0F`, no `DIV`/`MUL`, ≈6.25%), confirmed by `IP-1101`'s own `T22.d`. This FR deliberately
  diverges from
  `BL-0094`'s literal "treasure only at dead ends" request — flagged explicitly per this
  document's own traceability discipline (a genuine design substitution, not an oversight);
  `FR-9160` (the finite mode's own dead-end-anchored placement) is entirely unaffected and
  remains as shipped. **Collection implemented (`IP-1103`, 2026-07-16):** in Infinite Mode the
  current region's treasure (when the presence predicate holds and it is uncollected this
  materialization) spawns as the sole `COLL_DATA` entry at a per-biome position mirroring
  `ZONE_COLLECTS`' own type-2 entry; `check_collisions`' new `GAME_MODE == 1` branch increments
  `RUNNING_TREASURE_COUNT` and clears the `INF_TREASURE_HERE` cache on pickup, touching no
  finite-mode counter (`T26.a6`/`a7`). Collected-state across window re-entry awaits `IP-1104`'s
  ledger (FS-110 Workflow D).

### FR-10400 — Score-chasing win condition (running count + top-3 persisted, no name entry)

- **ID:** FR-10400
- **Title:** In Infinite Mode, the system shall track a running count of treasures collected
  during the current run and, on run end, compare it against a persisted top-3 high-score table,
  inserting it if it qualifies — with no character-name-entry step.
- **Description:** Replacing FR-9161's finite-mode fixed-threshold victory condition (collect
  `WORLD_SCALE` KeyItems), Infinite Mode has no completion threshold — the goal is a persisted
  high score. The system shall maintain a running count of treasures collected (FR-10300) during
  the current run, and on run end, compare that count against the three highest previously
  recorded scores, inserting it into the table (displacing the lowest, if any) if it qualifies.
  No UI step for entering a player name or initials is required.
- **Rationale:** ADR-0017 points 2–3; R216 (the arcade high-score convention as the historically
  correct genre answer for non-terminating play; the name-entry UI's original social/cabinet
  purpose does not transfer to a single-player handheld cartridge with one save slot).
- **Priority:** Must (**Partially Implemented, 2026-07-16, `IP-1103`** — the win-condition
  *state* (running count + top-3 table) and the comparison *subroutine* exist and are
  corpus-verified (`T26.c`); **no automatic trigger calls the comparison** — the run-end trigger
  is `BL-0112`'s own open question, deliberately not decided by implementation (see Notes).)
- **Inputs:** Treasure-collection events (FR-10300) during the current run; the persisted top-3
  table.
- **Outputs:** An updated running count; on run end, an updated top-3 table if the run's count
  qualifies.
- **Preconditions:** An Infinite Mode run is active (FR-10100); the run has ended (see Notes —
  the exact end-of-run trigger is not decided by this FR).
- **Postconditions:** The top-3 table contains the three highest scores ever achieved, most
  recent qualifying run included if applicable; no player-entered name is recorded with any
  entry.
- **Acceptance Criteria:** A run's final treasure count that exceeds the lowest of the current
  top-3 is inserted, displacing the previous lowest; a run's count that does not exceed any
  current top-3 entry leaves the table unchanged; no name-entry prompt appears at any point.
- **Dependencies:** FR-10300, FR-10500.
- **Verification Method:** Test (drive a corpus of run outcomes against a seeded top-3 table,
  confirm correct insertion/non-insertion; confirm no name-entry state is reachable).
- **Source Documents:** ADR-0017 points 2–3; R216 §Concepts.
- **Related ADRs:** ADR-0017.
- **Notes:** **Partially Implemented (`IP-1103`, 2026-07-16), stated precisely (mirroring
  `IP-1080`'s own precedent for a requirement split across packages):** `RUNNING_TREASURE_COUNT`
  (`0xC405`, 16-bit) and `TOP_SCORE_TABLE` (`0xC407`–`0xC40C`, 3 × 16-bit descending) exist,
  boot-cleared, and the comparison subroutine `inf_check_top_score` implements the
  strictly-exceeds/sorted-insertion/no-name-entry behavior exactly (corpus-verified, `T26.c`;
  no name-entry state reachable, `T26.e`) — **but no in-game event calls it** (`T26.d` asserts
  the zero-call-site state). The Acceptance Criteria's insertion half is therefore verified at
  the subroutine level only; end-to-end ("a run's final count…") remains genuinely untestable
  until `BL-0112` resolves the run-end trigger and a follow-up package wires the call site.
  Persistence of both fields is `IP-1104`'s scope. **This FR's Preconditions name "the run has
  ended" without
  defining what ends a run** — whether an Infinite Mode playthrough is indefinitely resumable
  (matching FR-5100/FR-1190's existing save/continue convention) or is its own bounded "run"
  needing a new end-condition mechanic (death/retreat/checkpoint) this game does not currently
  have is a genuine, unresolved design question (R216 surfaces it, deliberately does not answer
  it; ADR-0017 point 4 explicitly declines to decide it here). **Not baselined as part of this
  FR** — see CR-07 below and RQ-03 finding #17. This FR's own win-condition *state* (running
  count, top-3 table) is compatible with either eventual answer and needs no rework once decided
  (ADR-0017 point 4), which is why it is safe to baseline now despite that open question.

### FR-10500 — Visited-region-ledger save/load (position + collected-state only)

- **ID:** FR-10500
- **Title:** In Infinite Mode, the system shall persist the player's current position and a
  bounded ledger of which visited regions have had their treasure collected — never the region
  graph itself.
- **Description:** Unlike FR-9200's finite-mode save format (persist `SEED`/`WORLD_SCALE`,
  regenerate the graph, restore per-region flags onto it), Infinite Mode has no fixed `scale` to
  regenerate against. On save, the system shall write the player's position (an unbounded
  coordinate pair, not a bounded zone index) and a bounded-by-SRAM-capacity ledger of
  visited-region treasure-collected state. On load, the system shall restore position directly
  and restore the ledger; biome/connectivity for any region are re-derived on demand (FR-10200),
  never read from SRAM.
- **Rationale:** ADR-0016 point 5; R114 (save/load needs "a bounded-by-SRAM-capacity
  visited-region ledger, not a flat whole-grid array, since an unbounded world cannot reserve
  SRAM for every region that could ever exist").
- **Priority:** Must (**Implemented, 2026-07-16, `IP-1104`** — position + bounded ledger save/load
  shipped exactly as described; `SAVE_VERSION_VAL` bumped `0x04`→`0x05`; verified end-to-end via
  a two-instance save/reload harness, `T27.a`.)
- **Inputs:** Player position; visited-region treasure-collected state at save time; SRAM
  contents at load time.
- **Outputs:** SRAM updated with position and ledger entries (save); in-memory position and
  ledger restored, with any region's biome/connectivity re-derived on demand rather than read
  from SRAM (load).
- **Preconditions:** An Infinite Mode save-confirm or exit-to-main-menu action (save); a
  version-matching Infinite Mode save exists (load).
- **Postconditions:** SRAM's position and ledger match in-memory values at save time (save); the
  restored position and ledger, combined with FR-10210's revisit-consistency guarantee, exactly
  reproduce the pre-save world state as the player re-encounters it (load).
- **Acceptance Criteria:** Saving then loading an Infinite Mode game restores the exact player
  position and treasure-collected state for every previously-visited region in the ledger; no
  SRAM field represents biome or connectivity for any region.
- **Dependencies:** FR-10100, FR-10200, FR-10210.
- **Verification Method:** Test (save/reload two-instance harness, mirroring FR-9200's existing
  pattern, extended to the ledger's own bounded-capacity shape).
- **Source Documents:** ADR-0016 point 5; R114 §Implementation Guidance.
- **Related ADRs:** ADR-0016.
- **Notes:** **Implemented (`IP-1104`, 2026-07-16).** The ledger's real SRAM capacity, `BL-0108`'s
  own open sizing question, is resolved as-shipped: 128 entries × 5 bytes = 640 bytes SRAM (plus
  a byte-identical 642-byte WRAM working copy, `BL-0119`'s own amendment — see `GDS-07`
  §7f/§7g), against the confirmed ~8 KiB SRAM budget and ~3.1 KiB bank-0 WRAM headroom (`R111`)
  respectively; FIFO eviction once full (`T27.c`). The save-format version bump `IP-1104` names is
  `SAVE_VERSION_VAL` `0x04`→`0x05`, the fifth bump since ship, extending `IP-9110`'s own strictly-
  monotonic sequence.

### FR-10600 — Indefinitely resumable Infinite Mode run (no bounded end-condition mechanic)

- **ID:** FR-10600
- **Title:** An Infinite Mode run shall be indefinitely resumable — the same save/continue
  convention the finite mode already uses — with no death/retreat/checkpoint mechanic ending it.
- **Description:** Resolves `CR-07`'s open question (project owner, 2026-07-13: "for now assume
  indefinitely resumable"). An Infinite Mode save persists exactly as FR-1190/FR-5100 already
  describe for the finite mode: the player exits to the main menu (or the console powers off) at
  any point, and "continue" resumes from the exact persisted state (FR-10500's position +
  visited-region ledger) — there is no in-game action, timer, or hazard that forcibly ends a run.
  "Run end" for the purposes of FR-10400's top-3 comparison (see Notes) is therefore a player
  choice, not a game-imposed event.
- **Rationale:** Project owner, direct decision, 2026-07-13 ("for now assume indefinitely
  resumable") — resolves `CR-07`, itself grounded in R216's own framing of this exact choice
  ("indefinitely resumable... matching this project's existing save/continue convention").
- **Priority:** Must (**Implemented, 2026-07-16, `IP-1104`** — no run-ending mechanic exists
  anywhere in the shipped code; verified by a systematic negative-test sweep across every
  reachable input branch from a loaded Infinite Mode save, `T27.f`.)
- **Inputs:** A save-confirm or exit-to-main-menu action (mirroring FR-1190); a "continue" action
  from the MAIN MENU (mirroring FR-1170).
- **Outputs:** None beyond FR-10500's own save/restore behavior — this FR adds no new state of
  its own; it states that no mechanic exists to *forcibly* end a run.
- **Preconditions:** An Infinite Mode save exists.
- **Postconditions:** No reachable input sequence ends an Infinite Mode run other than the
  player's own choice to exit; "continue" always resumes exactly where the player left off.
- **Acceptance Criteria:** No in-game state, timer, or hazard exists that transitions an Infinite
  Mode save out of active play without the player's own exit action; repeated
  save/exit/continue cycles never lose or forcibly reset run state.
- **Dependencies:** FR-10500, FR-1170, FR-1190.
- **Verification Method:** Test (negative test — attempt every reachable input sequence, confirm
  none forcibly ends a run; mirroring FR-9110's own negative-test shape).
- **Source Documents:** Project owner decision, 2026-07-13; R216 §Concepts.
- **Related ADRs:** ADR-0017 (point 4 — this FR is the decision that ADR point deferred).
- **Notes:** **Implemented (`IP-1104`, 2026-07-16).** `T27.f` drives movement, both SAVE
  round-trip branches (B-cancel and A-save), and a full SELECT-menu round trip from a loaded
  Infinite Mode save — none forcibly ends the run; `GAMESTATE`/`GAME_MODE` are unchanged
  afterward. **This is explicitly a "for now" decision, not a permanently
  closed one** — the project owner's own wording leaves room to revisit if a bounded-run mechanic
  later proves desirable; any such change would be a new, dated RQ-01 delta at that time, not an
  amendment to this FR's own text. `FR-10400`'s own win-condition Preconditions field ("the run
  has ended") should be read, per this FR, as "the player has chosen to stop, at any point they
  like" — not a game-imposed event — since no bounded-run mechanic exists. No `GDS-01` delta is
  needed: an indefinitely-resumable run introduces no new `GAMESTATE`, matching `CR-07`'s own
  analysis that this answer carries no architecture gap.

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

### CR-05 — Biome-blob clustering seeded from the maze's own dead-ends (`BL-0066`) — RESOLVED, BASELINED 2026-07-14

- **Description:** Cluster biome assignment into cohesive multi-region blobs (so a "Forest area"
  spans several regions before drifting, per `BL-0066`'s own ask), with blob centers seeded from
  `FR-9140`'s spanning-tree maze's own dead-end regions (leaf nodes) — the owner's own first
  suggestion.
- **Why excluded:** **Direct architecture conflict, not a gap.** `ADR-0012` point 1 fixes the
  generation pass order as biome-assignment-first, then maze-generation second, entirely
  independent of each other — biome assignment reads only each region's grid-fixed top/left
  neighbor, never the maze's connectivity. Dead-end-seeded clustering requires the *opposite*
  order (maze must exist first, to identify its own dead-ends, before biome-seeded-from-dead-ends
  assignment can run) — this is not a requirements-level ambiguity to resolve by rewording, it is
  a genuine conflict with a binding architecture decision. Per this skill's own rule ("a
  wrong/ambiguous/self-contradictory architecture statement is a Review finding, never patched by
  writing around it"), this is routed to the Review (`RQ-03` finding), not silently reworded into
  something compatible.
- **A compatible alternative exists and is baselined instead:** flood-fill-seeded clustering (N
  independently-drawn seed points, no maze dependency) does not conflict with `ADR-0012`'s pass
  ordering — but this requirements pass does not baseline that either, since `BL-0066`'s own
  filed disposition explicitly named evaluating dead-end-seeding "against simpler alternatives...
  as part of the same [design] pass, not assumed as the only option," and picking definitively
  between them here would be originating a design decision this stage's own rules forbid
  ("redesign the architecture... never patched by writing around it" — the *choice* between two
  compatible-vs-incompatible clustering strategies is itself an architecture-level call once the
  conflict is known, not a requirements-authoring one).
- **Disposition:** `BL-0066` remains open, unresolved by this delta. Routed back to
  `03-architecture-design-synthesis` (or directly to the user, if the owner has a preference
  between "revisit `ADR-0012`'s pass ordering to allow dead-end-seeding" vs. "keep the ordering,
  use flood-fill instead") — see `RQ-03`'s finding for the full conflict write-up.
  **Resolved (2026-07-14): the project owner picked neither original option** — direct
  instruction: "If there is a blob mechanism that works for infinite mode, use that concept for
  the finite mode as well," pointing at the per-super-cell `hash(SEED, supercell_row,
  supercell_col)` technique `R114`/`ADR-0016` already established for Infinite Mode.
  [ADR-0018](../architecture/adr/ADR-0018-finite-mode-biome-blob-clustering.md) adopts it for the
  finite mode too — a deterministic snap-to-blob layered on top of `ADR-0009` point 2's existing
  grammar-constrained draw (unchanged as the fallback), requiring no `ADR-0012` pass-ordering
  change at all, since the hash needs no maze to exist first. This Candidate's own original
  dead-end-seeding proposal is superseded, not adopted — see `ADR-0018` for the full mechanism.
  **Baselined 2026-07-14 as [FR-9170](#fr-9170--finite-mode-biome-blob-clustering-via-per-super-cell-positional-hash)**
  — the per-super-cell snap-to-blob mechanism, layered on `ADR-0009` point 2's existing draw as
  fallback, exactly as `ADR-0018` decides. This Candidate is now closed — `CR-05` is no longer an
  open item; `BL-0066` closes in step (mirroring `CR-06`'s own `03→04` precedent above).

### CR-06 — Edge-indicator legend/help screen, reachable via SELECT (`BL-0100`) — RESOLVED, BASELINED 2026-07-13

- **Description:** A read-only screen explaining the on-screen transition-edge indicator tiles to
  the player — the open-arrow (a valid, maze-connected neighbor exists, `FR-2320`) versus the
  blocked-edge indicator (a grid-adjacent region exists but the generated maze doesn't connect to
  it, `FR-2330`) versus no indicator at all (a true grid boundary) — reachable via the SELECT
  button, per the owner's own request.
- **Why excluded:** **No traceable architecture source, not a gap this pass can close by
  rewording.** [GDS-01](../architecture/01-concept-of-play.md) §4's game-state machine names
  exactly six states (`TITLE`/`INTRO`/`PLAYING`/`SAVE`/`MAP`/`VICTORY`), with §4a's own delta
  list (the only mechanism this document uses to add new states — it already added `MAIN MENU`/
  `SEED SCALE ENTRY` this way, per `BL-0031`'s own `01→02→03→04` routing precedent) naming
  nothing resembling a legend/help screen or a SELECT sub-menu. `MAP` is documented as SELECT's
  *sole* destination ("reachable only from PLAYING (SELECT)") — there is currently no state-
  machine node this new screen could occupy, and no GDS-08 presentation-layer description of its
  layout/content. Per this skill's own rule ("a wrong/ambiguous/self-contradictory architecture
  statement is a Review finding, never patched by writing around it" — the same standard `CR-05`
  above applies to a direct `ADR-0012` conflict, applied here to a missing-concept gap instead of
  a conflicting one), inventing a new `GAMESTATE` value or a SELECT-menu restructuring here would
  be originating an architecture decision, not deriving a requirement from one.
- **Disposition:** Routed to `03-architecture-design-synthesis` first — a GDS-01 §4/§4a delta
  (new state, or a redefinition of what SELECT reaches) and a GDS-08 delta (the new screen's own
  layout/content) are both needed before a clean, implementation-independent FR can be written.
  `04-requirements-engineering` returns to derive the actual FR once that lands, mirroring
  `BL-0031`'s own `01→02→03→04` precedent for `MAIN MENU`/`SEED SCALE ENTRY`. See `RQ-03`'s
  finding for the full write-up. **Architecture landed (2026-07-13):** [GDS-01](../architecture/01-concept-of-play.md)
  §4c (`SELECT` now opens a small `MAP`/`LEGEND` cursor menu, `MAP` itself unchanged) and
  [GDS-08](../architecture/08-presentation-architecture.md) §11 (the `LEGEND` screen's static
  three-row content, reusing existing tiles/palette) both authored — this Candidate is now ready
  for `04-requirements-engineering` to derive its real FR from, still un-baselined until that
  pass runs. **Resolved (`04-requirements-engineering`, 2026-07-13): baselined as FR-1200**
  (SELECT MENU state, supersedes FR-1150's own SELECT→MAP clause) **and FR-1210** (LEGEND state
  itself, citing GDS-08 §11 directly) — both target, not yet implemented. This Candidate is now
  closed; further tracking lives on FR-1200/FR-1210 themselves.

### CR-07 — Infinite Mode run/session shape: indefinitely resumable vs. a bounded run with a new end-condition mechanic (`BL-0106`) — RESOLVED, BASELINED 2026-07-13

- **Description:** Whether an Infinite Mode playthrough is expected to be resumed indefinitely
  (matching FR-5100/FR-1190's existing finite-mode save/continue convention — a run simply
  continues across power-off, with no "end" until the player chooses to start a new game) or is
  its own bounded "run" that ends deliberately, needing a new end-condition mechanic
  (death/retreat/checkpoint) this game does not currently have.
- **Why excluded:** **Genuine missing concept, not an ambiguity fixable by rewording, and not a
  direct architecture conflict either — R216 and ADR-0017 both explicitly surface this question
  without answering it.** R216 states plainly: "a future spec pass should decide whether an
  infinite run is expected to be resumed indefinitely... or is itself a bounded 'run' that ends
  deliberately... this topic surfaces the question, deliberately does not answer it, since it is
  a genuine new mechanic decision outside a pure win-condition-scaling scope." ADR-0017 point 4
  repeats this explicitly: "Run/session shape is explicitly NOT decided by this ADR." If the
  answer turns out to be "a bounded run with a death/retreat/checkpoint mechanic," that is a new
  `GAMESTATE`-level concept `GDS-01`'s six-state (soon eight-state, per `FR-1200`/`FR-1210`) game
  loop has no node for today — the same class of gap `CR-06` (above) named for the LEGEND
  screen, resolved the same way: routed upstream rather than invented here. If the answer is
  simply "indefinitely resumable, no new mechanic," no architecture gap exists at all — but this
  stage has no basis in the current inputs to know which answer is correct, and inventing either
  one would be "originating an architecture decision, not deriving a requirement from one" (the
  same standard `CR-06` applied).
- **Disposition:** Not routed to `03-architecture-design-synthesis` outright, unlike `CR-05`/`CR-06`
  — this is a genuine **player-experience preference**, not a technical architecture question a
  research-driven synthesis pass is well-positioned to decide unilaterally (contrast `ADR-0012`'s
  maze-algorithm choice, correctly delegated to `03` per that ADR's own reasoning). Recommend the
  pipeline manager surface this directly to the user (`NEEDS-USER`) the next time Infinite Mode's
  own implementation is imminent (i.e., once `05-feature-decomposition`/`06-feature-specification`
  reach this epic) — not urgent now, since `FR-10400`'s own win-condition state is compatible with
  either answer and needs no rework once decided (`ADR-0017` point 4). If the answer requires a
  new mechanic, that decision then routes to `03-architecture-design-synthesis` for the resulting
  `GDS-01` delta before this Candidate can be baselined into a real FR. See `RQ-03` finding #17
  for the full write-up. **Resolved (2026-07-13): project owner decided directly — "for now
  assume indefinitely resumable."** The no-new-mechanic branch of this Candidate's own analysis
  applies: no `GDS-01` delta is needed, so no `03-architecture-design-synthesis` routing was
  required after all. Baselined as **FR-10600** (Indefinitely resumable Infinite Mode run). This
  Candidate is now closed; further tracking lives on `FR-10600` itself. The owner's own wording
  ("for now") is carried into `FR-10600`'s Notes verbatim — this is a revisitable decision, not a
  permanently closed one.

### CR-08 — Adjacency-grammar ordering position for the four newly-folded biome identities (`BL-0128`) — RESOLVED, BASELINED 2026-07-16

- **Description:** Once `FR-4320` ships, `FR-4310`'s adjacency grammar (today defined only over
  the five-value palette-family axis — water/sand/grass/stone/brick, per R212's own worked
  example) must say where the four newly-folded-in identities (Village, Cave, Desert, Plains)
  sit on that ordering, so the generator can decide which of the nine identities are legal to
  place next to which others.
- **Why excluded:** **Genuine missing concept, not an ambiguity fixable by rewording, and not a
  direct architecture conflict either — R212 explicitly anticipates this exact expansion without
  deciding it.** R212's own Implementation Guidance states: "the adjacency grammar should be
  defined over these families **or a refinement of them**" (emphasis in the original research
  document) — naming the possibility of a finer-grained axis than the five palette groups, but
  not saying where a refinement's new entries would sit. Two genuinely different answers exist,
  neither decidable from the current inputs: (a) the four new identities could each inherit their
  parent palette-group's position exactly (Village/Cave slot at Stone's position, Desert slots at
  Sand's, Plains at Grass's — meaning multiple identities share one adjacency-legality slot, only
  their *rendered* content differs) — the minimal-change reading; or (b) each could get its own
  distinct position on a finer nine-point axis (e.g. water → beach → desert → grassland → plains
  → hills → village → mountains → cave, an ordering `R212`/`GDS-08` §8 have never stated) — a
  richer reading that would let e.g. Desert legally border Sand/Beach but not Grass/Forest
  directly, distinguishing identities the palette axis alone cannot. This is the same class of
  gap `CR-05`/`CR-06` (above) named for a conflicting mechanism and a missing screen concept
  respectively, applied here to a missing *ordering*: inventing either answer here would be
  originating a design decision, not deriving a requirement from one.
- **Disposition:** Routed to `02-research-game-design` first (extend R212's own grammar-table
  worked example to state where the four new identities sit — the same kind of grounding R212
  already provides for the original five) or `03-architecture-design-synthesis` (a GDS-08 §8
  delta, if the answer is judged more a presentation-layer palette-stepping question than a
  narrative/environmental-storytelling one — R212's own scope). Not urgent: `FR-4320` itself
  (the count/identity/palette-mapping requirement) is fully baselined and unblocked by this gap
  — only `FR-4310`'s own extension to the nine-identity axis, and any future generator code that
  consumes it, waits on this answer. `04-requirements-engineering` returns to derive the real
  `FR-4310` delta once that lands, mirroring `CR-06`'s own `03→04` precedent exactly.
  **Resolved (`02-research-game-design`, 2026-07-16): `R212` v1.1 grounds reading (b)** — a
  distinct nine-point axis, not the minimal-change palette-inheritance reading (a) — with real,
  independently-documented precedent for each new adjacency (Cappadocia's Uçhisar grounding
  Castle-Village-Cave as one real place, not three invented pairings; Petra grounding Cave-Desert;
  Minecraft's own real generation rule, already R212's own cited source, grounding Desert-Plains).
  **Baselined (`04-requirements-engineering`, same day): `FR-4310`'s own Description/
  Postconditions/Acceptance Criteria now state the concrete nine-value ordering** (`Water(0) –
  Sand(1) – Grass(2) – Stone(3) – Brick(4) – Village(5) – Cave(6) – Desert(7) – Plains(8)`). This
  Candidate is now closed; further tracking lives on `FR-4310` itself.
