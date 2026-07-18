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
2. Is treasure *spent* on healing (reducing the win/high-score count) or does it trigger healing
   without being consumed? Changes the entire economy model.
3. Does the weapon have ammo/durability, or is "upgraded... healed... by the treasure" its only
   resource interaction? (Owner's own 2026-07-17 clarification narrowed this but didn't close it.)
4. What is the fail state? No player-damage/health concept exists today — does combat introduce a
   real "game over," or is damage non-lethal/cosmetic (consistent with C9's tone either way this
   resolves)?
5. Finite mode or Infinite Mode only? `BL-0133`'s own filing says "on the infinite map" — should
   this be confirmed as Infinite-Mode-exclusive, or could/should it extend to finite mode later?
6. Concurrent mob count and spawn density — a first-order OAM/ROM-budget-shaping decision.
7. Does mob/weapon-tier state persist across save/load (a new SRAM version bump, mirroring
   `IP-1010`/`IP-1050`/`IP-1104`'s own precedent), or is it session-only?
8. **(Research-level, blocking a fuller architecture pass) — NEW 2026-07-17.** No R1xx/R2xx/R3xx
   research topic covers combat/enemy design conventions, hardware-feasible projectile/hit-
   detection techniques on SM83, or health/damage HUD conventions. Committing to concrete mob/
   projectile/health entity shapes (the System Architecture sketch above stays a sketch, not a
   decision) needs this grounding first — routed to `02-research-game-design` (design
   conventions: enemy AI patterns, difficulty pacing for an opt-in "parent mode," health/damage
   HUD conventions on GBC-era titles) and `02-research-gbc-hardware` (hardware feasibility:
   projectile movement/collision cost on SM83, OAM budget for concurrent mob+projectile sprites,
   whether a second APU channel is needed for combat SFX — this project currently uses only
   channel 1).

## Decision Log

| Date | Decision | Basis |
|---|---|---|
| 2026-07-17 | This ADS stops short of producing an `FS-xxx` or any `FR-xxxx` — the Vision-level tension (Open Question 1) is judged blocking, not merely informative, because every downstream requirement's shape depends on its answer. | This skill's own charter: it names tensions and routes genuine domain gaps upstream rather than inventing a resolution; a vision-level tonal question is exactly the class `01-vision` exists to own, not `03`. |
| 2026-07-17 | Treasure's dual-purpose-economy question (Open Question 2) and the weapon's ammo/durability question (Open Question 3) are recorded as open rather than assumed, per the owner's own 2026-07-17 clarification narrowing but not closing them. | Direct owner statement, quoted in `BL-0133`'s own backlog entry. |
| 2026-07-17 | **A second stop, found on this same day's follow-up pass** (after Open Question 1 resolved): before committing to concrete mob/projectile/health entity designs or a gating mechanism, this skill searched the research encyclopedia for any grounding on combat/enemy/damage design and found **none** — a genuine domain-knowledge gap, not a small detail. `R204` mentions HUD health-bar *weighting* in passing (not combat design); `R214` explicitly warns *against* treating existing combat-focused GBC homebrew (Azure Dreams/Dragon Crystal) as design templates for *this* project, without offering an alternative. No R1xx/R2xx/R3xx topic covers enemy AI patterns, projectile/hitscan feasibility on SM83, sprite-based hit-detection conventions, or health/damage HUD conventions for a GBC title. This pass stops here rather than inventing combat-design conventions itself — that would be exactly the kind of research-origination this skill's own charter forbids. | Direct search of `docs/research/encyclopedia/` (grep for combat/enemy/mob/projectile/weapon/health/damage across every R1xx/R2xx/R3xx topic) — confirmed empty beyond the two tangential mentions above. |

## What this ADS does NOT do

It does not baseline any `FR-xxxx`, does not produce an `FS-xxx`, and does not commit to any of
the candidate shapes sketched under System Architecture/Domain Model above — those are
groundwork for whichever pass follows once Open Question 1 is answered, not decisions. This
mirrors `ADS-001`'s own precedent of naming candidate shapes without prematurely fixing them,
one level further upstream than that document sat (that one already had an unambiguous Vision
basis in `C7`; this one does not yet).
