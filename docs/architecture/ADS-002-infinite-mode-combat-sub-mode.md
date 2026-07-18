# ADS-002 — Infinite Mode Combat Sub-Mode (Mobs + Treasure-Fed Ranged Weapon)

**Dependencies:** `BL-0133` (project-owner intake filing); `FEAT-9000`/`FS-110` (the shipped
Infinite Mode this sub-mode builds on); `ADR-0007` (8×16 OBJ sprite mode — any mob/projectile
sprite must fit its tile-pair convention); `GDS-01` (Concept of Play) and `MSTR-001`'s own
Commitment **C9** (item-agnostic, **child-friendly** collect-goal) — the one real tension this
document exists to surface, not resolve.
**Produces:** nothing yet — this document does not produce an `FS-xxx`. See §"What this ADS does
NOT do" below.

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

Sketched, not committed — every element here is a candidate shape to ground the Open Questions
below, not a decision:

- **Mob entities** would need a new WRAM table (parallel structure to how `REGION_GRAPH`/
  `INF_WINDOW` already represent per-region state) — candidate: a fixed-size mob-slot array
  (position, type, health, alive-flag), sized to whatever concurrent-mob-count the design settles
  on. Existing precedent for fixed-size WRAM tables with a cursor/eviction scheme:
  `IP-1104`'s own `LEDGER`/`LEDGER_COUNT`/`LEDGER_CURSOR` (128-entry FIFO). A mob table would be
  smaller (concurrent on-screen mobs, not an ever-growing visited history) but could mirror the
  same shape.
- **Mob spawning** would need to hook into `inf_ensure_window`'s existing per-region
  materialization (`IP-1101`/`IP-1102`) — the natural point where a region's content is already
  decided deterministically from `(seed, row, col)`, mirroring how treasure-presence is drawn
  today (`hash(seed,row,col) mod 16 == 0`). A mob-presence draw would need its own independent
  `gw_prng_step` call in the same sequential-reseed chain, following the established
  no-correlation discipline `worldgen.py`'s own docstring already documents.
- **The ranged weapon** would need: a fire-input binding (no spare button exists today — every
  D-pad direction plus A/B/START/SELECT are already assigned; a weapon-fire input needs either a
  context-sensitive reuse of an existing button during `PLAYING`, or a genuinely new control
  scheme decision), a projectile entity (transient, not persisted — mirrors `INF_MZ_RESULT`'s own
  "transient, generation-time-only" precedent), and a hit-test against mob positions (the existing
  `check_collisions` routine's asymmetric point-in-box technique, `BL-0053`'s own fix, is a
  plausible reusable pattern).
- **Sprite budget**: shadow OAM (`OAM_BUF`, 160 bytes = 40 entries) currently covers the player
  (in 8×16 mode, 1 entry) plus up to 8 on-screen collectibles per screen (`ZONE_COLLECTS`'s own
  per-family cap). Mobs + a projectile sprite would compete for the same 40-entry budget — real
  headroom exists, but "how many concurrent mobs" is a first-order design question, not a detail.
- **ROM budget**: 1,378 bytes of headroom remain post-`IP-9170` (31390/32768). Mob AI, a
  weapon-fire state machine, and new tile/palette art for mobs/projectiles/health-HUD will
  compete for this — a combat sub-mode of any real depth will likely need either further
  ROM-efficiency work (mirroring `ADR-0020`'s procedural-fill precedent) or `ADR-0011`'s
  already-committed-but-unimplemented bank-switching cutover. This should be named explicitly in
  whatever `07-implementation-planning` pass eventually plans this, not discovered mid-implementation
  (`BL-0134`'s own lesson).

## Domain Model

Candidate new entities (none yet formalized as `FR-xxxx`/GDS-04 additions):

- **Mob**: position, type/species, health, alive/dead state, (optionally) an AI behavior tag.
- **Projectile**: origin, direction/velocity, transient lifetime, damage value.
- **PlayerHealth**: a new player-state field (today the player has no health/damage concept at
  all — `check_collisions` only ever *adds* to score/treasure counts, never subtracts or ends a
  run on damage).
- **Weapon**: a stat model — "upgraded... by the treasure" implies at least one upgrade tier axis;
  whether it also has ammo/durability is explicitly named as unresolved by the owner's own
  2026-07-17 clarification.
- **Treasure's widened role**: today `RUNNING_TREASURE_COUNT` is a pure win/high-score input
  (`IP-1103`, `FR-10300`/`FR-10400`). This request adds a second consumption path (player-health
  restoration) — whether treasure is *spent* (reducing the win-condition count) or merely
  *triggers* healing without being consumed is a first-order, unresolved economy question.

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
