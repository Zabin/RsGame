# FS-112 — Infinite Mode Combat Sub-Mode

> Feature Specification for [FEAT-11000](../feature-planning/03-feature-catalog.md#feat-11000--infinite-mode-combat-sub-mode-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-11000, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Specified 2026-07-17.** This Feature sits in the `Future` release bucket (no release
> commitment made); planning does not require or imply scheduling, per
> `05-feature-decomposition`'s own established precedent (`FEAT-10000`/`FEAT-7100`).
>
> **Planned 2026-07-17** (`07-implementation-planning`) — six packages,
> [IP-1120](../implementation/packages/IP-1120-infinite-mode-combat-mode-gating.md)–[IP-1125](../implementation/packages/IP-1125-combat-sprite-content.md),
> **none authorized.** [IP-1120](../implementation/packages/IP-1120-infinite-mode-combat-mode-gating.md)
> (mode gating & UI, resolving Open Question 1) is additionally **`BLOCKED`** on a `GDS-01` §4d
> amendment (a genuine architecture gap this planning pass found — `MODE SELECT`'s own
> architecture text states a closed two-option fact a third option would falsify, mirroring
> `BL-0113`'s own precedent for `MODE SELECT`'s original existence) — routed to
> `03-architecture-design-synthesis`, not resolved here. The other five packages
> ([IP-1121](../implementation/packages/IP-1121-infinite-mode-combat-mob-materialization-and-rendering.md)
> mob materialization/rendering/defeat,
> [IP-1122](../implementation/packages/IP-1122-infinite-mode-combat-weapon-fire-and-hit-resolution.md)
> weapon fire/hit resolution,
> [IP-1123](../implementation/packages/IP-1123-infinite-mode-combat-player-health-and-economy.md)
> player health/setback/healing economy,
> [IP-1124](../implementation/packages/IP-1124-infinite-mode-combat-save-persistence.md) save
> persistence,
> [IP-1125](../implementation/packages/IP-1125-combat-sprite-content.md) sprite content) do not
> depend on the gating mechanism's exact shape and are independently plannable/buildable. Planning
> also surfaced two genuine requirements gaps, harvested to the backlog rather than resolved
> unilaterally: `WEAPON_TIER`'s own treasure-funded upgrade mechanism has no baselined FR
> (`IP-1122` §9); the heal-spend action's own input binding has no free button named upstream
> (`IP-1123` §9) — both routed to `04-requirements-engineering`/`06-feature-specification`.

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-112` — expands `FEAT-11000` (Infinite Mode Combat Sub-Mode), Epic `EP-6000` (Infinite Mode).

## 2. Title

Infinite Mode Combat Sub-Mode

## 3. Purpose

Offer a distinct, explicitly opt-in combat layer inside Infinite Mode — mobs, ranged weapon fire,
player health, a treasure-spent healing economy — for the dual-audience carve-out `MSTR-001` C11
names, without touching the base child-friendly Infinite Mode or finite mode at all. Carried
forward verbatim from FEAT-11000's own Purpose/User Value (Medium-High — directly answers a real
Vision-level commitment, `MSTR-001` C11, rather than exploratory scope).

## 4. Scope

**In scope:** a third, explicitly-labeled MODE SELECT option gating the sub-mode on for a save's
entire life; per-region mob materialization/defeat, drawn as a pure function of `(seed, row, col)`
independent of the region's own biome/treasure draws; a single-slot ranged projectile fired on
player input, resolved against mob hitboxes; player health tracked and displayed via the existing
heart-tile art, with a non-lethal setback on reaching zero; a treasure-spent healing economy that
decrements the same `RUNNING_TREASURE_COUNT` `FEAT-10000`'s own win/high-score logic reads; combat
state (mob state, weapon tier, player health) persisted across save/load via a new
`SAVE_VERSION_VAL` bump.

**Out of scope** (per FEAT-11000's own Excluded Requirements, carried forward verbatim):
`FEAT-10000`'s own base Infinite Mode capability (mode entry, streaming generation, treasure
placement, the base win condition, save/load) — none of its leaves are amended by this Feature,
per `ADS-002`'s own Open Question 5 confirming this capability is additive and
Infinite-Mode-exclusive; the entire finite mode (`FEAT-9000`/`FEAT-4100`/`FEAT-5300`), confirmed
unaffected by the same Open Question.

**Scope note carried from FEAT-11000's own catalog entry:** this Feature is deliberately kept as
one cohesive unit (gating, mob materialization/defeat, weapon fire/hit resolution, player
health/setback, the healing economy, save persistence) rather than pre-split by concern, since
nothing has been implemented yet to reveal a clean seam — mirroring how `FEAT-10000` itself
started unsplit. A future `05-feature-decomposition` pass may split it once implementation detail
is known (e.g. mob AI vs. weapon/hit-resolution vs. HUD).

## 5. Requirements Implemented

FR-11100, FR-11200, FR-11300, FR-11400, FR-11500, FR-11600; NFR-1500, NFR-4500 — the exact set
FEAT-11000 owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-11000--infinite-mode-combat-sub-mode-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — Combat sub-mode entry** (FR-11100):

1. Player reaches new-game creation and chooses Infinite Mode (the existing `GS_MODE_SELECT`
   entry point, `FS-110` Workflow A).
2. Before or immediately after committing to Infinite Mode, the player is offered a third,
   distinctly-labeled choice (e.g. "COMBAT MODE") — never defaulted on, never reachable by any
   path a player could enter unintentionally (`ADS-002` §System Architecture, Gating Mechanism).
3. The chosen `COMBAT_MODE` state is recorded for the new save and fixed for that save's entire
   life, mirroring `FR-9110`/`FR-10100`'s own established immutability precedent.
4. Control passes to Workflow B for the player's starting region, now with combat active.

**Workflow B — Mob materialization and defeat** (FR-11200):

1. When a region materializes (`FS-110`'s existing `inf_ensure_window` hook, Workflow B step 2)
   and `COMBAT_MODE` is active, the system draws mob presence/type as a pure function of
   `(SEED, row, col)`, via its own sequential `gw_prng_step` reseed call in the same per-region
   reseed chain treasure-presence already uses — independent of and uncorrelated with that
   region's own biome/treasure draws (`ADS-002` §System Architecture, Mob spawning).
2. Up to six mobs may be concurrently active (an adjustable default, not a hard ceiling this
   Feature fixes).
3. When the player defeats a mob (Workflow C), it disappears via a brief, non-graphic
   presentation sequence (mirroring how a collected `ScoreItem` already deactivates today) — no
   persistent corpse sprite.
4. Re-materializing the same region with the same seed reproduces identical mob
   presence/type/position; a region materialized with `COMBAT_MODE` inactive shows zero mobs and
   is otherwise byte-for-byte identical to today's shipped Infinite Mode.

**Workflow C — Ranged weapon fire and hit resolution** (FR-11300):

1. During `PLAYING` with `COMBAT_MODE` active, the player presses the fire input — the A button,
   confirmed unbound during gameplay today by direct code read of `handle_play_input`/
   `st_playing` (`ADS-002` §System Architecture).
2. If no projectile is currently active, one spawns from the player's own position in the
   player's current facing direction; if one is already active, the new press has no additional
   effect until the active one terminates (at most one projectile in flight at a time, an
   adjustable default).
3. Each frame, the active projectile moves; if it reaches an active mob's hitbox (a point-in-box
   test reusing `check_collisions`' own established asymmetric-tolerance technique, per `R115`),
   that mob's health is reduced (defeated at zero, Workflow B step 3) and the projectile
   deactivates; if it instead reaches a terminal boundary (window/screen edge) without a hit, it
   deactivates without effect.

**Workflow D — Player health, setback, and the healing economy** (FR-11400, FR-11500):

1. Mob contact/attack reduces the player's health value, displayed via a persistent HUD element
   reusing the already-shipped `TL_HEART_FULL`/`TL_HEART_EMPTY` tiles (`tiles.py`) — zero new art
   cost.
2. The player may choose to spend collected treasure (`RUNNING_TREASURE_COUNT`, the same count
   `FS-110` Workflow C reads for the win/high-score comparison) to restore health — spending
   decrements that same count; no second, independent ledger is created.
3. If player health reaches zero, a non-lethal setback triggers (e.g. returning the player to the
   last region entered, with treasure/health partially restored) — never a `GAMESTATE` transition
   to a game-over state, consistent with `MSTR-001` A5's fail-state-free base design holding
   inside `C11`'s own carve-out. The run continues in `PLAYING` afterward.

**Workflow E — Combat state save persistence** (FR-11600):

1. On a save-confirm or exit-to-main-menu action (the same trigger `FS-110` Workflow D uses), if
   `COMBAT_MODE` is active, the system additionally writes mob state, weapon tier, and player
   health to SRAM under a new `SAVE_VERSION_VAL` bump (mirroring `IP-1010`/`IP-1050`/`IP-1104`'s
   own established version-byte pattern).
2. On load, this state is restored exactly as it was at save time; a pre-combat-mode save (an
   older `SAVE_VERSION_VAL`) loads cleanly without it, mirroring `FS-110`'s own version-guard
   precedent for pre-Infinite-Mode saves.

## 7. System Behaviour

**Normal path (mob materialization):** given any `(SEED, row, col)` and `COMBAT_MODE` active, the
mob-presence draw terminates having produced mob presence/type/position that are a pure function
of those inputs alone — no dependency on generation order, treasure/biome draw order, or any
other region's own history (mirrors `FS-110`'s own `NFR-2300` positional-determinism framing,
extended to mobs).

**Edge case — `COMBAT_MODE` inactive:** a materialized region shows zero mobs and is byte-for-byte
identical to today's shipped Infinite Mode — this capability is additive by construction, not a
fork of the generation algorithm (`ADS-002` §System Architecture).

**Edge case — firing while a projectile is already active:** the fire input has no additional
effect (§6 Workflow C step 2) — not queued, not an error, simply a no-op until the active
projectile terminates.

**Edge case — a mob and the healing economy interacting in the same frame (taking damage while
spending treasure to heal):** not yet defined — whether damage and a heal-spend can resolve in
the same frame, and in what order, is genuinely undecided (Open Question 3).

**Edge case — player health reaching zero while treasure remains unspent:** the setback (§6
Workflow D step 3) fires regardless of remaining treasure — treasure is a player *choice* to
spend proactively, not an automatic save-from-death mechanic, per the user's own "spent," not
"triggers," economy decision (`ADS-002` Open Question 2).

**Edge case — a single frame where both region materialization and mob AI/projectile logic must
run:** whether this coincidence is reachable, and if so its combined cycle cost against
`NFR-1400`'s own already-`NOT MET` overage, is explicitly `UNCONFIRMED` (NFR-1500) — no
implementation exists yet to measure it.

## 8. Module Responsibilities

Per GDS-03's module decomposition, extended by `ADS-002`'s own module framing (no new module):

- **`asm_game.py`** — the mob-presence/type draw (hooked into `inf_ensure_window`'s existing
  per-region materialization), mob AI/defeat logic, the fire-input handler and projectile-update
  routine, player-health tracking and the non-lethal setback, the treasure-spend healing
  subroutine, the MODE SELECT gating extension (`GS_MODE_SELECT`), the health HUD write, and the
  save-write/load-restore extension. None of this code exists yet.
- **`worldgen.py`** (prospective) — the Python reference-generator-oracle mirror for the
  mob-presence draw, per `ADS-002`'s own reseed-chain discipline, mirroring `FS-110`'s own
  identical obligation for its per-region routine.
- **`tiles.py`** — the already-shipped `TL_HEART_FULL`/`TL_HEART_EMPTY` tiles this Feature's
  health HUD reuses verbatim. **This Feature does not add any new tile art for the health HUD**
  — a genuinely new mob/projectile sprite is the only new tile-art need, and its exact pixel
  content is `08-content-authoring`'s own scope, not decided here.

No module outside this set is touched.

## 9. Interfaces Used

- **`inf_ensure_window`'s existing per-region materialization hook** (`FS-110`, unchanged) — this
  Feature's mob-presence draw extends the same reseed chain treasure-presence already uses,
  consumed not redefined.
- **`gw_prng_step`'s existing shift/XOR-only construction** (R111/R113, unchanged) — reused for
  the mob-presence draw's own sequential reseed call, per `ADS-002`'s own no-correlation
  discipline. This Feature does not modify `gw_prng_step` itself.
- **`check_collisions`' existing asymmetric point-in-box technique** (`IP-9100`/`BL-0053`,
  unchanged) — reused verbatim for projectile-vs-mob hit-testing, per `R115`'s own explicit
  recommendation. No new hitbox model.
- **`handle_play_input`/`st_playing`'s existing input-dispatch surface** — the A button is
  confirmed unbound during `PLAYING` today (direct code read, `ADS-002`); this Feature adds a new
  branch for it, not a rebinding of any button already claimed elsewhere.
- **`RUNNING_TREASURE_COUNT`'s existing read/write surface** (`FS-110` Workflow C, unchanged) —
  this Feature's healing economy decrements the same count the win/high-score comparison reads;
  no second ledger, no new interface.
- **The existing `GS_MODE_SELECT` state / MODE SELECT UI** (`FS-110` Workflow A, `IP-1100`) —
  this Feature's gating choice (Workflow A) extends this same screen with a third option. **The
  exact UI mechanic (a three-state `MM_CURSOR` cycle vs. a follow-up confirmation screen shown
  only after choosing Infinite Mode) is not decided by this specification** — flagged as Open
  Question 1.
- **A new save-format version value** (mirroring `FS-110`'s own `SAVE_VERSION_VAL` precedent,
  currently `0x05`) — this Feature's combat state needs its own version discriminator; the next
  value in the established strictly-monotonic sequence would be `0x06`, but the exact bump is
  `07-implementation-planning`'s/`08`'s own act, not asserted here (mirrors `FS-110`'s own
  identical framing for its own version bump, Open Question 7 there).

## 10. Data Model Changes

**No `GDS-04`/`GDS-07`/`GDS-09` delta has been authored for the combat sub-mode** — like `FS-110`
before it, this specification has no proposed WRAM/SRAM address table to cite, only the
conceptual entities `ADS-002`'s own Domain Model already names:

- **`Mob`** — position (x, y), type/species (1 byte, room for multiple species per `R218`'s own
  variety-within-tone framing), health (1 byte), active flag. A fixed-size table, six concurrent
  slots (an adjustable default, `ADS-002`/`R115`), mirroring `COLL_DATA`/`COLL_COUNT`'s own
  established shape. No eviction/FIFO scheme needed — mobs are session-local per materialized
  region, not an ever-growing history.
- **`Projectile`** — origin, direction, active flag — a single transient WRAM record, mirroring
  `INF_MZ_RESULT`'s own "transient, generation-time-only, never persisted" precedent. A design
  needing more than one in-flight projectile is a future extension, not this Feature's own
  default.
- **`PlayerHealth`** — a new player-state field; today the player has no health/damage concept at
  all (`check_collisions` only ever adds to score/treasure counts). Presented via the reused
  heart-tile HUD.
- **`Weapon`** — a stat model with at least one upgrade-tier axis, funded by treasure; explicitly
  no ammo/durability field, per the user's own decision (`ADS-002` Open Question 3).
- **`COMBAT_MODE`** — a new 1-byte WRAM flag, valid only alongside `GAME_MODE=1` (Infinite Mode).

**SRAM additions** are this Feature's own scope (mirroring `FS-110`'s own identical framing) —
Workflow E's mob-state/weapon-tier/player-health fields are written directly by this Feature's
own save/load routine, since no separate save-persistence Feature exists for this capability in
the current catalog.

## 11. State Changes

- **Whether the combat sub-mode's own gating choice introduces a new `GameState` value is not
  decided by this Feature** — depends entirely on Open Question 1's own resolution (a new
  confirmation-screen state vs. an in-place `MM_CURSOR` extension). If the chosen shape reuses
  `GS_MODE_SELECT` itself (a three-state cursor), no new state is needed; if it needs a dedicated
  confirmation screen, a new state is implied, mirroring `FEAT-1200`'s/`FS-110`'s own precedent
  for a genuinely new screen.
- **No new state is introduced for gameplay itself** — combat's own weapon-fire/mob-AI behavior
  reuses the existing `PLAYING` state; this Feature changes what happens *within* that state, not
  the state machine's own node set for play itself.
- **Runtime state created:** the mob table, the projectile record, and player health, persisting
  for the life of the play session and, via Workflow E, across save/reload.

## 12. Error Handling

- **Invalid mode-selection input:** out of this Feature's own scope — the same input-validation
  discipline `FS-110`/`FEAT-1100` already establish for the MODE SELECT screen applies identically
  here (Workflow A).
- **A mob-presence/type draw producing an invalid value:** not a runtime failure mode this
  Feature handles defensively — the positional-determinism guarantee is enforced by construction
  (the reseed-and-clamp computation), not checked and recovered from after the fact, mirroring
  `FS-110`'s own identical framing for its own generator-guaranteed properties.
- **Firing with no mob in range:** not an error — the projectile simply reaches its terminal
  boundary and deactivates without effect (§7 edge case).
- **Spending treasure to heal with `RUNNING_TREASURE_COUNT` at zero:** the heal-spend action has
  no effect (FR-11500's own Precondition, `RUNNING_TREASURE_COUNT > 0`) — not a crash or an
  underflow; the exact player-visible feedback (a no-op vs. a disabled-menu-option cue) is Open
  Question 4.
- **A pre-combat-mode save loaded after this Feature ships:** mirrors `FS-110`'s own
  version-guard precedent (a version-mismatched-for-this-field save simply lacks the combat
  fields, not offered garbage data) — the exact version value is not fixed here (§9).

## 13. Performance Considerations

- **NFR-1500** (combat sub-mode per-frame cycle budget, `UNCONFIRMED`): whether mob AI tick,
  projectile update, and hit-test logic fit inside the existing per-frame budget — and, critically,
  whether a frame where combat logic and region materialization coincide would compound
  `NFR-1400`'s own already-`NOT MET` overage — is not confirmed by any evidence this specification
  can cite. `R115` names the risk directly but does not treat it as settled. This Feature's own
  Acceptance Criteria (§15) states the bar; it does not claim compliance.
- **NFR-4500** (ROM/OAM budget): `R115`'s own direct measurement (post-`IP-9170`/`IP-9180`) found
  1,378 bytes of ROM headroom and 31 of 40 shadow-OAM entries free (9 used: 1 player + up to 8
  collectibles). The 6-mob-slot default (7 new entries including the projectile) leaves 24 free —
  favorable, but not yet confirmed against a real implementation's actual footprint.

## 14. Integrity Considerations

- **Positional determinism** (mirrors `FS-110`'s own `NFR-2300` framing, extended to mobs): the
  mob-presence draw's output must be a pure function of `(SEED, row, col)` alone — no read of
  `DIV`, uninitialized WRAM, generation order, or any other history-dependent input.
- **Save round-trip integrity** (FR-11600): mob state, weapon tier, and player health must
  restore exactly on load; the version-guard must reject a pre-combat-mode save's own combat
  fields as absent rather than reading garbage bytes as valid state.
- **The SM83 mob-presence routine and its `worldgen.py` oracle mirror must be kept in lockstep by
  direct correspondence** (same reseed construction), mirroring `ADR-0018`'s/`FS-110`'s own
  identical discipline — named here as a standing implementation obligation, not itself enforced
  by this specification.

## 15. Acceptance Criteria

1. The combat sub-mode is never enabled by default and is never reachable via any path a player
   could enter unintentionally; once chosen, it is fixed for that save's life (FR-11100).
2. For a corpus of `(SEED, row, col)` triples with `COMBAT_MODE` active, materializing the same
   region twice produces byte-identical mob presence/type/position both times; the same region
   materialized with `COMBAT_MODE` inactive shows zero mobs and is otherwise unaffected (FR-11200).
3. Firing while no projectile is active spawns one; firing while one is already active has no
   additional effect; a projectile that reaches an active mob's hitbox reduces its health and
   deactivates; a projectile that reaches a terminal boundary without a hit deactivates without
   effect (FR-11300).
4. Player health decreases on mob contact/attack, reflected in the HUD within a frame budget
   mirroring the existing HUD-update timing; reaching zero health triggers the defined setback
   and the run continues in `PLAYING`, never a game-over state (FR-11400).
5. Spending treasure to heal reduces `RUNNING_TREASURE_COUNT` by exactly the spent amount; the
   same count is what the win/high-score comparison reads at run's end — no separate ledger
   exists (FR-11500).
6. A save/load round trip reproduces identical mob state, weapon tier, and player health; a
   pre-combat-mode save loads cleanly without this state (FR-11600).
7. Static inspection of the mob-presence draw finds no read of `DIV` or any WRAM address not
   explicitly derived from `SEED`/`(row, col)` (mirrors NFR-2300's own audit shape).
8. **Not yet a checkable criterion** — NFR-1500's cycle-budget bar has no fixed numeric target to
   check against until an implementation exists to measure it; this specification names the bar
   (§13) without asserting compliance.

## 16. Verification Plan

Per FR-11100–11600's own Verification Methods (Test) and NFR-1500 (Analysis) / NFR-4500
(Inspection, once implemented) — no `test_rom.py` suite exists yet for this Feature (no code
exists to test):

- **Combat sub-mode entry (AC-1):** drive the MODE SELECT flow once Open Question 1 resolves a
  concrete UI shape; confirm the sub-mode is off by default and fixed once chosen.
- **Mob materialization determinism (AC-2):** property test across a `(SEED, row, col)` corpus,
  mirroring `FS-110`'s own T22/T24 determinism-test shape (fresh-instance comparison plus
  oracle-vs-SM83 comparison), extended to mob presence/type/position.
- **Weapon fire/hit resolution (AC-3):** direct-force integration checks mirroring `IP-9100`'s
  own established hitbox-test methodology — force a mob into range, fire, confirm health
  reduction and projectile deactivation; force a miss, confirm clean deactivation without effect.
- **Player health/setback (AC-4):** direct-force integration checks — force mob contact, confirm
  HUD reflects the reduction; force health to zero, confirm the setback fires and `GAMESTATE`
  remains `PLAYING`.
- **Healing economy (AC-5):** direct-force integration check — force a known `RUNNING_TREASURE_COUNT`,
  trigger a heal-spend, confirm the exact decrement and the resulting health increase.
- **Save/load (AC-6):** two-instance save/reload harness, mirroring `IP-1104`'s own T27 pattern,
  extended to mob state/weapon tier/player health.
- **Determinism static audit (AC-7):** Inspection — direct code read of the mob-presence draw,
  mirroring `FS-110`'s own T22.h-equivalent precedent.
- **Cycle budget (AC-8):** Analysis — direct cycle-counting against a real per-frame call context
  including the coincident-materialization case (NFR-1500), not possible until an implementation
  exists to measure.

**Corpus:** not yet defined — depends on the mob-slot count (an adjustable default, `ADS-002`)
and the mob-presence density constant, neither fixed by this specification.

## 17. Dependencies

Per FEAT-11000's own Dependencies (carried forward verbatim): FEAT-10000 (Infinite Mode — this
Feature is strictly a gated sub-mode of it; mob/projectile materialization piggybacks on its own
per-region materialization hook; combat state persistence extends its own save/load mechanism and
version-byte precedent); FEAT-3000 (Collectibles, Scoring & Victory — `RUNNING_TREASURE_COUNT` is
the same count this Feature's own healing economy spends from); FEAT-6000 (Presentation & HUD —
the player-health display reuses its own existing heart-tile art and HUD-write pattern).

## 18. Risks

Carried forward from FEAT-11000's own Risk assessment (Medium-High): `NFR-1500`'s own per-frame
cycle budget is honestly `UNCONFIRMED` (measurement owed once real code exists, and must be
checked against `NFR-1400`'s own already-`NOT MET` region-materialization cost, not the nominal
frame ceiling alone — a compounding-cost risk `R115` names directly); `NFR-4500`'s ROM/OAM budget
is real but favorable, not yet confirmed against a real implementation's actual footprint.

**Additional risk surfaced by this specification, not named at the Feature-catalog level:** three
genuinely open questions (below) touch UI shape, edge-case sequencing, and setback feedback —
fewer than `FS-110`'s own eight, but still enough that whoever picks this Feature up next should
weigh routing some upstream (Open Question 1, an architecture-level UI-shape choice) before
`07-implementation-planning` attempts a package, versus letting `07` resolve the others as
implementation-level choices, mirroring `FS-110`'s own precedent for exactly this judgment call.

## 19. Open Questions

1. **UI mechanic for the combat sub-mode's own gating choice is not decided.** `ADS-002` commits
   to *a* third MODE SELECT option existing, but not its concrete shape: a three-state `MM_CURSOR`
   cycle on the existing `GS_MODE_SELECT` screen (Finite / Infinite / Infinite+Combat) versus a
   separate confirmation screen shown only after choosing Infinite Mode (mirroring `IP-1090`'s own
   SELECT-menu-confirmation precedent, which `ADS-002` itself names as a possibility). This is an
   architecture/interface-level choice (does it need a new `GameState`, per §11), not a
   requirements-level one. Resolves at: `07-implementation-planning`, mirroring `FS-110`'s own
   Open Question 6 precedent for exactly this class of UI-shape decision — or a return to
   `03-architecture-design-synthesis` first if the chosen shape needs a `GDS-01` delta.
2. **Damage-vs-heal-spend ordering within the same frame is not decided.** Whether a mob's attack
   and a player's heal-spend action can both resolve in the same frame, and if so which applies
   first, is genuinely undecided (§7 edge case). Not expected to matter often (both are
   player/enemy-initiated discrete events, not continuous per-frame effects), but not asserted
   safe either. Resolves at: `07-implementation-planning`, as an implementation-level sequencing
   choice — does not require a requirements or architecture change either way.
3. **The exact player-visible feedback for a no-op heal-spend attempt (zero treasure available)
   is not decided.** A silent no-op versus a disabled-option/audio cue is a presentation-layer
   choice `FR-11500` does not fix. Resolves at: `07-implementation-planning`/`08-code-
   implementation`, mirroring how `FS-110` left comparable presentation-only choices (e.g. the
   first-time-entry confirmation screen's exact wording) to implementation.

## 20. Related ADRs

ADR-0007 (8×16 OBJ sprite mode — governs any new mob/projectile sprite).
