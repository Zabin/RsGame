# ADS-002 — Infinite Mode Combat Sub-Mode (Mobs + Treasure-Fed Ranged Weapon)

**Dependencies:** `BL-0133` (project-owner intake filing); `FEAT-9000`/`FS-110` (the shipped
Infinite Mode this sub-mode builds on); `ADR-0007` (8×16 OBJ sprite mode); `MSTR-001`'s **C11**
(the dual-audience carve-out that unblocked this pass, 2026-07-17); **R218** (combat/enemy design
conventions — poof-defeat, heart-container HUD, difficulty-gating precedent); **R115** (hardware
feasibility — OAM/APU headroom, no-hardware-collision-detection).
**Produces:** still nothing yet — this document does not produce an `FS-xxx`. This revision
commits to concrete candidate architecture (System Architecture/Domain Model below are no longer
sketches-only) but the remaining economy/persistence Open Questions (2, 3, 4, 7) are genuine
requirements-level decisions this skill does not have standing to make; `04-requirements-
engineering` still cannot proceed until those are resolved. See §"What this ADS does NOT do."

**Delta record (2026-07-19):** §"Weapon Directionality Delta" added below, per `BL-0157`
(user-requested weapon directionality) and `R220` (movement-based multi-directional aiming
conventions, newly authored). Resolves the direction-representation shape a future
`04-requirements-engineering`/`06-feature-specification` pass needs for widening the weapon's
firing direction beyond today's shipped left/right-only encoding. Recorded as `ADR-0021`. No
re-authoring of §1–§8/Open Questions 1–8 above — those remain accurate as the already-shipped
`IP-1120`–`1126` baseline describes it; this delta is additive, extending the weapon axis only.

## Executive Design Overview

The project owner filed a request (via `00-intake`, `BL-0133`) for a new sub-mode on Infinite
Mode's procedurally-generated map: mobs (enemies) are present, the player carries a ranged
weapon, and the weapon is "upgraded and healed by the treasure" — the owner later clarified
(2026-07-17) that treasure heals the **player**, not the weapon; whether the weapon itself has a
separate durability/ammo concept is a still-open question, not resolved by that clarification.

This is not a small rider on the shipped game. Every mechanic it implies — mob entities, mob
AI/spawning, a fireable projectile, a weapon-stat model, player health/damage, and treasure's role
widening from a pure win-condition collectible to a dual-purpose (win-condition *and*
player-health-economy) resource — has **zero precedent** anywhere in the current GDS ladder,
requirements baseline, or shipped code (confirmed: `docs/architecture/`, `docs/requirements/`,
and the full backlog were searched for "mob"/"enemy"/"combat"/"weapon"/"health"/"damage" —
zero hits before `BL-0133` itself). The nearest touchpoint is `ADR-0007`'s own note that any
future enemy sprite must fit the 8×16 OBJ tile-pair convention already established for the player.

**This ADS's actual job, at this stage, is narrower than "design the combat system."** It:
(1) confirms combat has real architecture-level design tension, not just requirements-level
detail, so a jump straight to `04-requirements-engineering` would skip a real gate; (2) surfaces
the one load-bearing tension with the existing Vision that **must** be settled before any FR/FS
can commit to a shape — `MSTR-001`'s **C9** ("item-agnostic and **child-friendly** collect-goal")
was written for a pure collect-a-thon with no adversarial mechanic at all; introducing mobs the
player fires a weapon at is a genuine tonal/design question this ADS cannot answer on its own
authority, because answering it would mean inventing a Vision-level position (violence/combat
framing, difficulty, fail-state) that no one has actually decided; and (3) inventories the
architecture-level questions a future full design pass will need to resolve, so that pass starts
from a real list instead of a blank page.

## System Architecture

Committed candidate architecture (this revision), grounded in `R218`/`R115`. Still not an
`FS-xxx` — `04`/`06` may adjust any numeric default named here, but the *shape* is now a real
recommendation, not a placeholder:

- **Mob entities**: a fixed-size WRAM table mirroring `COLL_DATA`/`COLL_COUNT`'s own established
  shape (position + type + a per-slot active flag), sized to **6 concurrent slots** — a concrete
  default derived from `R115`'s own measured headroom (31 of 40 OAM entries free today; 6 mobs +
  1 projectile = 7 new entries, leaving 24 free for future growth, comfortably inside budget
  without assuming it). Each mob slot also carries a health field (see Domain Model). No
  eviction/FIFO scheme needed (unlike `IP-1104`'s `LEDGER`) — mobs are session-local per
  materialized region, not an ever-growing history.
- **Mob spawning**: hooks into `inf_ensure_window`'s existing per-region materialization
  (`IP-1101`/`IP-1102`), mirroring treasure-presence's own independent-reseed draw
  (`hash(seed,row,col) mod 16 == 0`) — a mob-presence draw takes its own sequential
  `gw_prng_step` call in the same reseed chain, per `worldgen.py`'s own no-correlation
  discipline. **Only fires when `COMBAT_MODE` is active** (new WRAM flag, see Gating Mechanism
  below) — a materialized region looks and plays identically to today's Infinite Mode when
  `COMBAT_MODE` is off, so this is additive, not a fork of the generation algorithm.
- **The ranged weapon**: fire input reuses the **A button during `PLAYING`** — today `A` has no
  binding during gameplay (confirmed by direct code read of `handle_play_input`; A is only bound
  during menu/dialog states) — no new control-scheme invention needed, an existing free input.
  Projectile: a single-slot transient WRAM record (position, direction, active flag) — mirrors
  `INF_MZ_RESULT`'s own "transient, generation-time-only, never persisted" precedent (§14
  Rollback Considerations' own established pattern for this codebase's transient state). Hit-test
  against mob positions reuses `check_collisions`' own asymmetric point-in-box technique
  (`IP-9100`/`BL-0053`), per `R115`'s own explicit recommendation — no new hitbox model.
- **Enemy defeat presentation**: per `R218`'s own grounded convention, a mob's defeat is a brief
  flash-then-deactivate sequence (mirroring how a collected `ScoreItem` already deactivates today)
  — no persistent corpse sprite, no graphic content, consistent with the base game's own existing
  content discipline and `C11`'s own "can be grimmer, not necessarily graphic" framing.
- **Health HUD**: reuses `tiles.py`'s already-shipped `TL_HEART_FULL`/`TL_HEART_EMPTY` tiles
  (zero new tile-art budget spent), per `R218`'s own heart-container convention. Exact screen
  placement (a second HUD row visible only during `COMBAT_MODE`, vs. a repurposed region of the
  existing row-0 bar) is a `06-feature-specification`-level layout decision, not fixed here.
- **Gating mechanism (Open Question 1's own follow-on, now committed)**: a new **third option on
  the MODE SELECT screen** (`GS_MODE_SELECT`, alongside today's finite/Infinite toggle) —
  labeled distinctly (e.g. "COMBAT MODE") so it reads as an explicit, clearly-signposted choice,
  per `R218`'s own difficulty-gated-optional-content precedent (Double Dragon II/TimeSplitters 2
  — never a hidden toggle a child could stumble into). Selecting it sets the new `COMBAT_MODE`
  WRAM flag (alongside the existing `GAME_MODE=1` Infinite Mode flag — `BL-0133`'s own filing
  scopes this to Infinite Mode only, confirmed by its own text: "on the infinite map"). A
  first-time-entry confirmation screen (mirroring `IP-1090`'s own SELECT-menu-confirmation
  precedent) can additionally state the mode's own nature before the player commits, if `06`
  judges that necessary — not fixed here, a presentation-layer detail.
- **Sprite budget**: confirmed by `R115` at 31 of 40 OAM entries free today (1 player + up to 8
  collectibles = 9 used). The 6-mob-slot default above (7 new entries incl. the projectile)
  leaves 24 entries of margin.
- **Cycle budget**: per `R115`'s own explicit constraint, any new per-frame combat logic (mob
  AI tick, projectile update, hit-test) must be measured separately against `inf_ensure_window`'s
  own already-`NOT MET` `NFR-1400` overage — not assumed safe because "headroom exists" on paper.
  A concrete measurement is `07-implementation-planning`'s/`08`'s own obligation once a real FR
  exists, not resolved here.
- **ROM budget**: 1,378 bytes of headroom remain post-`IP-9170`/`IP-9180` (31390/32768). Mob AI,
  the weapon-fire state machine, and new tile/palette art (mob sprites, projectile, any new HUD
  cells beyond the reused heart tiles) will compete for this — likely needs either further
  ROM-efficiency work (mirroring `ADR-0020`) or `ADR-0011`'s committed-but-unimplemented
  bank-switching cutover. Named explicitly for whatever `07-implementation-planning` pass
  eventually plans this, not discovered mid-implementation (`BL-0134`'s own lesson).

## Domain Model

Committed candidate entities (not yet formalized as `FR-xxxx`/GDS-04 additions — that is `04`'s
own job once the remaining economy Open Questions below are answered):

- **Mob**: position (x, y), type/species (1 byte, room for multiple mob "species" per `R218`'s
  own variety-within-tone framing), health (1 byte), active flag. Six concurrent slots (System
  Architecture above).
- **Projectile**: origin, direction, active flag — a single transient slot (System Architecture
  above); a design needing more than one in-flight projectile is a future extension, not this
  pass's own default.
- **PlayerHealth**: a new player-state field (today the player has no health/damage concept at
  all — `check_collisions` only ever *adds* to score/treasure counts, never subtracts or ends a
  run on damage). Presented via the reused heart-tile HUD (System Architecture above).
- **Weapon**: a stat model — "upgraded... by the treasure" implies at least one upgrade tier axis;
  whether it also has ammo/durability is explicitly named as unresolved by the owner's own
  2026-07-17 clarification (Open Question 3, still open).
- **Treasure's widened role**: today `RUNNING_TREASURE_COUNT` is a pure win/high-score input
  (`IP-1103`, `FR-10300`/`FR-10400`). This request adds a second consumption path (player-health
  restoration) — whether treasure is *spent* (reducing the win-condition count) or merely
  *triggers* healing without being consumed is a first-order, unresolved economy question (Open
  Question 2, still open) — this ADS commits to entity shapes, not to this economy decision,
  which is a real requirements-level choice `04`/the user must make.
- **`COMBAT_MODE`** (new): a 1-byte WRAM flag, valid only alongside `GAME_MODE=1` (Infinite Mode)
  — the gating mechanism's own state, set via the new MODE SELECT option above.

## User Stories

Deferred. Per this skill's own conventions, concrete stories belong to the eventual `FS-xxx` this
capability produces — premature here because the tonal/vision question below hasn't been
answered, and stories written against an unresolved tone (cartoonish "poof" mobs vs. anything
grimmer) would need to be rewritten once it is.

## Functional Requirements (capability-level, formalized later as `FR-xxxx` by `04`)

Not written. `04-requirements-engineering` cannot derive real FRs from this ADS until the Vision
question below is answered — an FR baselined against an unresolved tone would need revision the
moment that tone is decided, the exact "wasted rework" pattern this pipeline's own `DEFERRED`
disposition convention exists to avoid (mirrors `BL-0127`'s own precedent, where R2xx research
was deliberately deferred until `BL-0128`'s count question settled first).

## Non-functional Requirements

Named, not yet formalized: ROM-budget impact (headroom above); OAM/sprite-count budget; save-format
impact (does mob/weapon state need to persist across save/load, mirroring `IP-1104`'s own
ledger — likely yes, if mobs/weapon-tier are meant to be permanent-progression, not per-session);
`NFR-1400`-class cycle-budget risk if mob AI runs inside `inf_ensure_window`'s already-`NOT MET`
per-transition cost.

## Constraints

Single 32KB bank today (`ADR-0001`), 1,378 bytes free; 40-entry shadow-OAM budget; every existing
D-pad/button binding already claimed; `NFR-1400`'s existing cycle overage in the one routine a
mob-spawn draw would most naturally hook into.

## Risks

- **Vision-tension risk (the dominant one):** proceeding to write FRs/an FS for combat before
  the Vision question is answered risks baselining requirements that get invalidated by whatever
  answer the owner gives — a vision change is this pipeline's most expensive kind of change
  (per `01-vision`'s own framing), and combat/violence framing is exactly Vision-altitude, not
  something a downstream FS should quietly decide.
- **Scope risk:** this is the largest single capability ever proposed for this codebase — larger
  than the entire Infinite Mode epic (5 packages) or the nine-biome-family delta (8 packages)
  combined, by entity count alone (mobs + projectiles + weapon + health + a new HUD + a new
  economy). A future `05-feature-decomposition` pass should expect to cut this into multiple
  Features across more than one release bucket, not one `FEAT-xxxx`.
- **ROM-budget risk:** named above; real, not yet quantified until a concrete FR exists.

## Open Questions

1. **(Vision-level, blocking) — RESOLVED 2026-07-17.** Does `MSTR-001`'s **C9** ("child-friendly
   collect-goal") tolerate an adversarial combat mechanic at all, and if so, in what tone?
   Answered by `MSTR-001` v4.0's new **C11**: yes, via a narrow, opt-in carve-out — a gated
   combat sub-mode intended for a parent/adult player may be tonally grimmer; the base game's own
   child-friendly commitment is unchanged. See `01-vision`'s run for the full record.
2. **RESOLVED 2026-07-17 (user decision).** Is treasure *spent* on healing (reducing the
   win/high-score count) or does it trigger healing without being consumed? **Spent** — treasure
   is consumed to heal, creating a real risk/reward tension (heal now vs. bank treasure for
   score). `RUNNING_TREASURE_COUNT` itself is decremented on heal, not merely read.
3. **RESOLVED 2026-07-17 (user decision).** Does the weapon have ammo/durability? **No** — it
   fires freely once acquired; treasure funds only its power/upgrade tier, not ammo or
   durability. No ammo-count HUD element needed.
4. **RESOLVED 2026-07-17 (user decision).** What is the fail state? **Non-lethal setback** — no
   real "game over" in combat mode; reaching zero health triggers a setback (e.g. respawn at the
   last safe point, some treasure lost) while the run continues. Consistent with `A5`'s own
   fail-state-free base-game design holding even inside `C11`'s grimmer carve-out — "grimmer"
   describes tone/presentation, not a departure from this project's no-fail-state principle.
5. **RESOLVED** (was always this by the owner's own filing, not newly decided). Finite mode or
   Infinite Mode only? `BL-0133`'s own filing text says "on the infinite map" — **Infinite Mode
   exclusive**, confirmed; `COMBAT_MODE` is only ever valid alongside `GAME_MODE=1` (System
   Architecture above).
6. **Committed as an architecture default, not a fixed requirement.** Concurrent mob count: **6
   slots**, derived from `R115`'s own measured OAM headroom (System Architecture above) — `04`/`06`
   may adjust this number, but it is no longer an open question in the sense of "undecided," only
   "adjustable."
7. **RESOLVED 2026-07-17 (user decision).** Does combat state persist across save/load? **Yes** —
   mob state, weapon tier, and player health all persist, mirroring `IP-1010`/`IP-1050`/`IP-1104`'s
   own established save-format-bump precedent. A new `SAVE_VERSION_VAL` bump is therefore a real,
   expected part of this capability's own implementation, not optional.
8. **RESOLVED 2026-07-17.** Research grounding gap, closed by **`R218`** (design conventions:
   poof-defeat, heart-container HUD, difficulty-gating precedent) and **`R115`** (hardware
   feasibility: no hardware collision detection, OAM/APU headroom) — both authored and cited
   throughout System Architecture above.

**All eight Open Questions now resolved or committed as adjustable defaults.** This ADS is
complete for what `03-architecture-design-synthesis` can decide; `04-requirements-engineering`
can now baseline real `FR-xxxx`s against it.

## Weapon Directionality Delta (2026-07-19, `BL-0157`, grounded by `R220`)

The shipped weapon (`IP-1122`) fires only left/right because `PROJ_DIR` copies `PLAYER_DIR`
verbatim, and `PLAYER_DIR` itself is a 2-value fact — direct code read confirms it is written
only by `handle_play_input`'s RIGHT/LEFT branches (0=right, 1=left), never UP/DOWN, and is read
exactly once elsewhere, at OAM-render time, to isolate its bit 0 into the sprite's X-flip
attribute bit (`update_oam`: three `RRCA`s then `AND 0x20`). The user asked for the weapon to
also fire up/down/diagonal, based on movement. Four decisions, each with its own basis:

**(a) A new, separate WRAM concept — not a widening of `PLAYER_DIR` in place.** `PLAYER_DIR`
stays exactly as shipped: 2-value, left/right, driving the existing X-flip render unchanged. A
new byte (name TBD by `07`, working name `PLAYER_FACING` below) carries the fuller direction. This
mirrors this project's own already-established convention for exactly this kind of extension —
`IP-1127`'s own planning (`docs/implementation/packages/IP-1127-...md`) deliberately chose a new
parallel `MOB_CONTACT_FLAGS` table over widening `MOB_DATA`'s stride, for the identical reason: a
widened shared field risks every existing consumer of the old shape, where a new field risks
nothing already shipped. Here the calculus is even more one-sided — `PLAYER_DIR` has exactly one
non-copy consumer (the X-flip render), and decision (d) below means that consumer's own behavior
is not changing at all, so there is no shared behavior to even keep in sync.

**(b) Eight-directional, not four.** `R220` deliberately leaves this choice open as a tone/pacing
call; this project's own concrete fact tips it: `handle_play_input`'s RIGHT/LEFT/UP/DOWN branches
are independent `BIT`-tested branches, not a mutually-exclusive chain — holding e.g. RIGHT+UP
already moves the player diagonally today (each axis steps independently in the same frame). A
weapon restricted to 4-way would fire a strictly narrower set of directions than the player can
already move in, reading as an arbitrary mismatch rather than a deliberate constraint. 8-way keeps
the weapon's own expressive range matching the movement model that already exists, at no
additional input-scheme cost (no new button, still derived from the same D-pad state already read
every frame).

**(c) Diagonal projectile motion via simultaneous independent per-axis stepping — not vector
math.** This project's existing movement idiom, used everywhere it needs 2D motion (the player's
own D-pad movement above; `IP-1126`'s `inf_mob_move`, dominant-axis stepping toward the player),
is single-axis-at-a-time integer stepping — no trigonometry, no multiplication (SM83 has neither
natively). The player's own "diagonal movement" today is not a diagonal primitive at all: it is
two independent per-frame `INC`/`DEC` operations on `PLAYER_X` and `PLAYER_Y`, each gated on its
own D-pad bit, that happen to run in the same frame. A diagonal-firing projectile can copy this
exact idiom rather than inventing vector motion: `PLAYER_FACING` decodes to an independent
per-axis step (`-1`/`0`/`+1` on X, `-1`/`0`/`+1` on Y — 8 of the 9 combinations are the compass
directions, the 9th, `(0,0)`, is unreachable since firing requires the player to be facing some
direction); `inf_projectile_update` applies both axis steps every frame instead of only the X
step it applies today. No new hardware-level technique, no new research gap — an extension of an
idiom `R213`/this codebase's own shipped code already establish.

**(d) No new player sprite art.** The player's own walk-cycle sprite keeps rendering exactly as
today (frame-based animation + X-flip only) regardless of `PLAYER_FACING`'s value — `PLAYER_DIR`
is untouched (decision a), so the existing render path has nothing new to reflect. This is
consistent with `R218`'s own "abstract stakes over graphic depiction" convention (mob defeat is a
poof, not gore) and this ADS's own repeated pattern of reusing existing art at zero new cost
(the heart-tile HUD, the mob/projectile tiles' own already-shipped-then-reused palette slots).
`ADR-0007`'s 8×16 OBJ mode has no established Y-flip-based up/down variant or diagonal frame set
to reuse, and inventing one is new art-authoring scope this delta does not ask for. A future
`09-content-review` pass may recommend directional sprite art later as a purely additive
follow-on — not required by this decision, and not blocking it.

**Named risk, not resolved here:** `NFR-1500` (combat sub-mode per-frame cycle budget) is already
`UNCONFIRMED` and now also covers this delta's own added cost (`handle_play_input`'s
direction-decode, `inf_projectile_update`'s second per-frame axis step) — the same standing,
unmeasured risk `IP-1121`–`1126` all already carry, not a new category of risk this delta
introduces, but real cost added on top of an already-unmeasured budget.

**Not decided here (`04`/`06`'s own job):** the exact bit-encoding of `PLAYER_FACING` (a compact
3-bit compass value vs. two signed 1-bit-per-axis fields vs. some other shape); the exact
WRAM address (`07-implementation-planning`'s own job, following `GDS-07`'s address-allocation
convention); whether `PLAYER_FACING` is written on every frame a D-pad direction is held or only
on transition (idle-preserves-last-facing per the Link's Awakening convention `R220` grounds,
requiring "held" vs. "just-changed" to be distinguished somewhere) — a real implementation detail
this delta names but does not resolve.

## Decision Log

| Date | Decision | Basis |
|---|---|---|
| 2026-07-17 | This ADS stops short of producing an `FS-xxx` or any `FR-xxxx` — the Vision-level tension (Open Question 1) is judged blocking, not merely informative, because every downstream requirement's shape depends on its answer. | This skill's own charter: it names tensions and routes genuine domain gaps upstream rather than inventing a resolution; a vision-level tonal question is exactly the class `01-vision` exists to own, not `03`. |
| 2026-07-17 | Treasure's dual-purpose-economy question (Open Question 2) and the weapon's ammo/durability question (Open Question 3) are recorded as open rather than assumed, per the owner's own 2026-07-17 clarification narrowing but not closing them. | Direct owner statement, quoted in `BL-0133`'s own backlog entry. |
| 2026-07-17 | **A second stop, found on this same day's follow-up pass** (after Open Question 1 resolved): before committing to concrete mob/projectile/health entity designs or a gating mechanism, this skill searched the research encyclopedia for any grounding on combat/enemy/damage design and found **none** — a genuine domain-knowledge gap, not a small detail. `R204` mentions HUD health-bar *weighting* in passing (not combat design); `R214` explicitly warns *against* treating existing combat-focused GBC homebrew (Azure Dreams/Dragon Crystal) as design templates for *this* project, without offering an alternative. No R1xx/R2xx/R3xx topic covers enemy AI patterns, projectile/hitscan feasibility on SM83, sprite-based hit-detection conventions, or health/damage HUD conventions for a GBC title. This pass stops here rather than inventing combat-design conventions itself — that would be exactly the kind of research-origination this skill's own charter forbids. | Direct search of `docs/research/encyclopedia/` (grep for combat/enemy/mob/projectile/weapon/health/damage across every R1xx/R2xx/R3xx topic) — confirmed empty beyond the two tangential mentions above. |
| 2026-07-17 | Committed to concrete candidate architecture (6-slot mob table, transient projectile, MODE SELECT gating option, A-button fire input, poof-defeat + reused heart-tile HUD) now that `R218`/`R115` ground it. Every concrete claim (A-button unbound during `PLAYING`, `TL_HEART_FULL`/`TL_HEART_EMPTY` already shipped) re-verified against the live tree before being stated, not assumed from the research topics alone. | `R218`, `R115`, direct code read of `handle_play_input`/`st_playing`/`tiles.py`. |
| 2026-07-17 | **User resolved all four remaining Open Questions in one batched round**: treasure is *spent* on healing (Open Question 2); the weapon fires freely with no ammo/durability, treasure funds power only (Open Question 3); the fail state is a non-lethal setback, no real game-over (Open Question 4); combat state (mobs, weapon tier, health) persists across save/load via a new `SAVE_VERSION_VAL` bump (Open Question 7). All eight Open Questions are now closed or committed as adjustable defaults — `04-requirements-engineering` can proceed. | Direct user decision, 2026-07-17 (batched `AskUserQuestion`, all four recommended options accepted). |
| 2026-07-19 | **Weapon Directionality Delta committed** (`BL-0157`): a new, separate `PLAYER_FACING`-shaped WRAM concept (not a widened `PLAYER_DIR`) carries an 8-directional facing value; `PLAYER_DIR` and its own sole non-copy consumer (the X-flip OAM render) stay untouched; diagonal projectile motion is simultaneous independent per-axis stepping (this codebase's own existing 2D-movement idiom, not new vector math); no new player sprite art. Recorded as `ADR-0021`. | `R220` (movement-based directional aiming conventions); direct code read of `handle_play_input`/`update_oam` confirming `PLAYER_DIR`'s exact single non-copy consumer and its independent-branch (not mutually-exclusive) D-pad handling; `IP-1127`'s own "new parallel structure over widened shared field" precedent. |

## What this ADS does NOT do

All eight Open Questions are now resolved or committed as adjustable defaults, and the System
Architecture/Domain Model sections above are real candidate architecture, not sketches. Even so,
this document itself **does not baseline any `FR-xxxx` and does not produce an `FS-xxx`** — that
formalization is `04-requirements-engineering`'s (then `06-feature-specification`'s) own job,
never this skill's. The numeric defaults named here (6 mob slots, A-button binding, etc.) are
recommendations `04`/`06` may adjust, not fixed requirements.
