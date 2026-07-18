# R206 — Difficulty, Pacing & Session Length for Handheld Play

- **Document ID:** R206 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R201 (goal density directly drives pacing)
- **Referenced By:** R215 (pacing bounds on how large a win-condition threshold can grow, `BL-0081`),
  R216 (2026-07-13 — extends this topic's short-loop preference to a mode with no generation-
  defined end, `BL-0082`/`BL-0094`), R218 (2026-07-17 — grounds the difficulty-gated-optional-
  content precedent for an opt-in combat sub-mode, `BL-0133`)
- **Produces:** grounds zone sizing/collectible density decisions in `tilemaps.py`
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R201, R215, R216

## Purpose

Why short, low-failure sessions are the right pacing target for this game, and what "zone size"
and "collectible density" decisions should optimize for as the world grows (C7).

## Concepts

Handheld games are conventionally built around **short, repeatable gameplay loops** that fit
fragmented, interruptible playtime — waiting for a bus, a few quiet minutes — rather than long
uninterrupted sessions.[^1] Good pacing keeps the player moving fast enough to stay invested
without outrunning the content or the player's ability to track what's left to do.[^2] Poor
pacing in this era's handheld titles often came from *slow, unforgiving* movement compounding
with sparse checkpointing — Castlevania: The Adventure's sluggish movement made it hard to build
momentum, a frequently-cited example of handheld pacing done wrong.[^1] Difficulty options
(explicit modes, or implicit tuning like collision forgiveness) let a wider range of players
reach a satisfying pace without changing the core design for anyone.[^3]

### Sources
[^1]: [From Game Boy to Galaxy: The Evolution of Handheld Gaming — Retromash](https://retromash.com/2026/02/17/from-game-boy-to-galaxy-the-evolution-of-handheld-gaming/), accessed 2026-07-06.
[^2]: [Dimensions of Games – Pacing](https://www.gamesprecipice.com/pacing/), accessed 2026-07-06.
[^3]: [Pacing Problems in Game Design — Game Developer](https://www.gamedeveloper.com/design/pacing-problems-in-game-design), accessed 2026-07-06.

## Operational Context

Bunny Quest is already well-aligned with the "short, low-friction, no-fail-state" target
(MSTR-001 assumption A5): a fixed single movement speed (no sluggish ramp-up, R202), a generous
10px collision tolerance (R202), no enemies, no fail states, no timer, and — per R201's goal
structure — a small, fully-enumerable 9-carrot completion goal rather than a sprawling one. Nine
zones at one screen each (no scrolling within a zone) means the entire game world is visible in
nine discrete "screenfuls," a genuinely short total traversal even before considering how quickly
a session can start and stop (title→intro→playing in a handful of button presses, auto-load
skipping even that on subsequent sessions, R205).

**This is exactly the pacing model MSTR-001 C7 puts pressure on.** A Zelda/Pokémon-scale world is,
by genre convention, a *long-session* target — those games' own pacing model assumes many hours
of play, save-and-resume across many sessions, and a much larger "fully enumerable" completion
goal (or an explicit partial-completion threshold, R201). Growing Bunny Quest's world without
addressing pacing explicitly risks inheriting Zelda/Pokémon's scale without their session-shape
assumptions — a mismatch this project's own casual/short-session identity (A5) doesn't currently
have to solve, but will once C7 is actually pursued.

## Implementation Guidance

- **Zone/collectible density decisions today should optimize for "short and complete-able in one
  sitting."** Adding more zones for C7's sake is fine; adding zones that individually take much
  longer to fully explore, or raising collectible density per zone substantially, would erode the
  current pacing identity and should be a deliberate, stated tradeoff at GDS-01, not an incidental
  side effect of "more content."
- **A world-scale expansion (C7) needs an explicit pacing decision, not an assumed one:** does the
  game stay a single short-sitting experience with a much bigger *map* but similar total
  playtime (more, smaller zones), or does it deliberately become a longer, multi-session game
  (fewer, larger zones, more collectibles per zone)? Both are legitimate directions; neither
  should be the silent default. This belongs in GDS-01 (Concept of Play) as an explicit statement,
  citing this topic.
- **Preserve the no-fail-state, no-timer design** regardless of world-scale growth — nothing about
  making the world bigger requires adding failure states, and MSTR-001 A5 explicitly commits to
  keeping them absent.
- **If session length does grow significantly under C7,** revisit R205's save-system gap (no
  auto-checkpoint) with more urgency — a longer game raises the cost of losing unsaved progress
  proportionally.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R201 (the collectible-goal structure this topic's pacing analysis is built on).
