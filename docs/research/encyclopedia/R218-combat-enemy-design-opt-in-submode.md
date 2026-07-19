# R218 — Combat & Enemy Design for an Opt-In, Tonally-Distinct Sub-Mode

- **Document ID:** R218 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R201 (collect-a-thon goal design, the base loop this sub-mode layers onto),
  R204 (HUD conventions, extended here for a health element), R206 (difficulty/pacing, extended
  here for an opt-in harder mode), R214 (already warns against treating Azure Dreams/Dragon
  Crystal as combat-design templates for this project, without offering an alternative — this
  topic is that alternative)
- **Referenced By:** `docs/architecture/ADS-002-infinite-mode-combat-sub-mode.md`
- **Produces:** grounds `ADS-002`'s fuller architecture pass (mob/projectile/health entity shapes,
  the gating mechanism) once this topic exists
- **Feature Mapping:** `BL-0133` (Infinite Mode combat sub-mode)
- **Related Topics:** R201, R204, R206, R211, R214

## Purpose

Ground the design of a combat mechanic (mobs, a ranged weapon, player health/damage) for
`BL-0133`'s Infinite Mode sub-mode — specifically the class of *non-lethal-by-convention* combat
this project's own Vision now permits (`MSTR-001` v4.0 **C11**: an opt-in, gated sub-mode for a
parent/adult player, tonally grimmer than the base game but not required to be graphic), and how
that combat mode can sit beside an otherwise all-ages, non-violent base game without either
undermining the base game's own tone or feeling like a bolted-on, unrelated genre.

## Scope

Enemy-defeat presentation conventions (the "poof"/non-graphic-death norm and why it exists);
health/damage HUD display conventions; how retro/GBC-era titles have historically gated harder or
tonally-distinct content behind an optional mode without splitting the game in two; explicitly
**out of scope**: hardware feasibility of projectile movement/hit-detection on SM83 (routed to
`02-research-gbc-hardware`, a separate open item under the same `BL-0145` filing) and the
project's own economy/fail-state decisions (architecture/requirements questions, not research
conclusions).

## Concepts

**The "poof" / non-graphic-defeat convention.** The Legend of Zelda series (including its
Game Boy/GBC entries, `Link's Awakening`, `Oracle of Seasons`/`Ages`) has enemies disappear in a
puff/flash effect on defeat rather than leaving a body — Nintendo's own long-standing internal
policy against depicting graphic death or blood, which the "poof" convention satisfies while still
giving the player unambiguous, immediate defeat feedback.[^1] This is the load-bearing precedent
for `MSTR-001` C11's own framing: "grimmer" does not have to mean *graphic* — a combat mode can
carry real stakes (health loss, a fail state, tactical pressure) while keeping defeat presentation
itself abstract/symbolic, which is both genre-authentic for 8-bit-era action and consistent with
this project's existing content discipline (no blood/gore anywhere in the shipped game today).

**Heart-container health HUD.** The same series established a persistent, top-of-screen health
gauge rendered as a row of heart icons, full/empty/partial per point of damage, with a low-health
audio warning below a threshold.[^2] This is a well-understood, instantly-legible convention for
exactly the kind of "moment-to-moment survival stat deserves prominent placement" principle R204
already establishes for this project's own HUD design — health is precisely the kind of
gameplay-critical value R204's own Concepts section names as warranting the most prominent HUD
treatment, more so than the existing carrot-count/score digits.

**Difficulty-gated optional content, not a second game.** Retro and retro-adjacent titles have
long precedent for locking harder, more demanding content behind an explicit difficulty choice
without altering the base experience for players who don't opt in — *Double Dragon II*'s hidden
final boss reachable only on its hardest named difficulty, and *TimeSplitters 2*'s harder
difficulties shortening levels and reducing available objectives, are both documented instances
of the same underlying pattern: the base game stays intact and completable on its own terms,
while a clearly-labeled harder/different mode sits beside it as strictly additive, optional
content.[^3] This is the precedent for `C11`'s own "opt-in, explicitly gated" framing — the
combat sub-mode should read to the player as a clearly-labeled *choice*, not a hidden toggle that
quietly changes the base game's own tone.

### Sources
[^1]: Community-documented convention discussion, [Defeated Enemies — Zelda Dungeon Forums](https://www.zeldadungeon.net/forum/threads/defeated-enemies.4906/), accessed 2026-07-17: "Developers don't want bloody bodies all over the place... [the] 'poof' is often interpreted as representational of defeat rather than death" — cites Nintendo's own general no-graphic-death/no-blood content policy as the reason.
[^2]: [Life Gauge — Zelda Wiki (Fandom)](https://zelda.fandom.com/wiki/Life_Gauge) and [Heart Container — Zelda Wiki (Fandom)](https://zelda.fandom.com/wiki/Heart_Container), accessed 2026-07-17 — the Game Boy-specific Heart Meter layout (two rows, upper-right) and the low-health audio warning are both documented there directly.
[^3]: [Simple Article: How to Design Difficulty Modes in Games — Red Hare Studios](https://redharegames.wordpress.com/2022/02/14/simple-article-how-to-design-difficulty-modes-in-games/), accessed 2026-07-17 — names the Double Dragon II and TimeSplitters 2 examples specifically as instances of content gated behind a difficulty choice.

## Operational Context

This project already ships the exact tile art a heart-container-style health display would need,
for an unrelated purpose: `tiles.py`'s `TL_HEART_FULL`/`TL_HEART_EMPTY` constants (`0x11`/`0x12`,
confirmed by direct code read) render the MAP screen's per-zone completion indicator
(`update_map_hearts`, `asm_game.py`). **Zero new tile-art budget would be spent** reusing this
existing pair for a combat-mode health HUD — a direct, concrete instance of R204's own "HUD
elements should be spent in proportion to importance" principle, now with a real, zero-cost asset
already in the ROM. `_score_bar()`'s own row-0 HUD (R204) has no free columns today (every cell
from col 1 through col 19 is already claimed by the carrot/score/name display) — a combat-mode
health row would need either a second HUD row (only reachable during the combat sub-mode's own
distinct screen state, not overlapping the base game's row-0) or a repurposed region only visible
when the sub-mode is active, a real layout decision for the eventual `06-feature-specification`
pass, not resolved here.

This project's existing collision/hitbox technique (`check_collisions`' asymmetric point-in-box
test, `IP-9100`/`BL-0053`'s own fix) is a directly reusable pattern for mob-vs-player and
projectile-vs-mob hit detection — the same asymmetric-tolerance design principle (generous on the
approach side, tight on the exit side) that already reads as "fair" to players in this game's
existing collectible pickup, per that package's own established precedent.

## Implementation Guidance

- **Defeat presentation:** design mob defeat as a brief tile/palette-flash-then-disappear
  sequence (mirroring the "poof" convention above), not a persistent corpse/gib sprite — this
  keeps the combat mode's own visual language consistent with every other defeat-adjacent event
  already in this game (a collected item simply deactivates, no persistent "used" art either),
  and avoids any graphic content C11's own "can be grimmer" carve-out never asked for.
- **Health HUD:** reuse `TL_HEART_FULL`/`TL_HEART_EMPTY` (already in the tile budget, zero new
  art cost) for the combat mode's own health display, mirroring the exact heart-row convention
  R218's own Concepts section grounds — a concrete, already-shipped asset this project can point
  to instead of inventing new health-display art.
- **Difficulty/tone gating:** the combat sub-mode's own entry point (its exact UI shape is an
  `ADS-002`/`06-feature-specification` decision, not resolved here) should read as an explicit,
  clearly-labeled choice — mirroring the Double Dragon II/TimeSplitters 2 precedent — not a
  setting a child could stumble into from the base game's own default flow. This directly informs
  `ADS-002`'s own still-open gating-mechanism question.
- **Hit detection:** reuse `check_collisions`' existing asymmetric point-in-box technique for
  mob/projectile collision, rather than inventing a new hitbox model — proven, tested, and already
  reads as fair in this exact codebase.

## Feature Mapping

`BL-0133` (Infinite Mode combat sub-mode) — this topic grounds `ADS-002`'s still-pending fuller
architecture pass (mob/projectile/health entity shapes). Does not itself resolve `ADS-002`'s own
Open Questions 2–7 (economy, ammo/durability, fail-state severity, mode scope, spawn density,
save persistence) — those remain architecture/requirements-level decisions this research topic
only informs, never answers on its own authority.

## Related Topics

R201 (collect-a-thon goal design — the base loop this sub-mode is strictly additive to), R204
(HUD conventions, extended here), R206 (difficulty/pacing, extended here for an opt-in harder
mode), R211 (comparative GBC-era visual design case studies — a future content-authoring pass for
mob sprites should consult this alongside R218), R214 (the existing warning against Azure
Dreams/Dragon Crystal as templates — this topic is the alternative that warning called for).

**Extended by (2026-07-19):** R219 (ranged-weapon upgrade/progression conventions, grounding
`WEAPON_TIER`'s own funding mechanism) and R220 (movement-based multi-directional weapon aiming
conventions, grounding a future `PLAYER_DIR` widening) — both declare this topic as a dependency
and extend its weapon/projectile axis specifically, filed via `BL-0155`/`BL-0157`.
