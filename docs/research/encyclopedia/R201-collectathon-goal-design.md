# R201 — Top-Down Collect-a-thon Structure & Goal Design

- **Document ID:** R201 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** none
- **Referenced By:** R206 (pacing depends on goal density), R211 (case studies share this structure)
- **Produces:** grounds `tilemaps.py`'s `ZONE_COLLECTS` structure and `asm_game.py`'s victory logic
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R206, R211

## Purpose

Why Bunny Quest's collectible hierarchy (stars/flowers for score, one carrot per zone for
victory) is a sound structural choice, and what a future world-scale expansion (MSTR-001 C7) must
preserve to keep that structure legible.

## Scope

The tiered-pickup convention collect-a-thon games use, how Bunny Quest maps onto it, and what
scaling a 9-zone goal set to a much larger world implies structurally.

## Concepts

Collect-a-thon design conventionally separates pickups into tiers: a low-value, high-frequency
tier that rewards exploration moment-to-moment (score items), and a scarce, high-value **"plot
coupon"** tier that gates progress and is the game's actual stated goal — Donkey Kong 64's Golden
Bananas and Super Mario 64's Power Stars are canonical examples of the latter.[^1] Not every
pickup needs to be collected to win — Mario 64 requires only 70 of 120 stars — but the design
intent is usually that the scarce tier is fully enumerable and individually meaningful (the
player can name what's left), unlike the abundant tier.[^1] Both Zelda and Pokémon lean on
"collect everything" as a core thesis, using nested collection loops (small collectibles inside
larger ones) to keep exploration rewarding at every scale.[^2]

### Sources
[^1]: [The Nintendo Collectathon: A Genre of the Past — The Artifice](https://the-artifice.com/nintendo-collectathon/), accessed 2026-07-06.
[^2]: [The Nintendo Collectathon: A Genre of the Past — The Artifice](https://the-artifice.com/nintendo-collectathon/), accessed 2026-07-06.

## Operational Context

Bunny Quest already implements exactly the two-tier structure: `ZONE_COLLECTS` (confirmed by
direct code read) holds, per zone, several `type 0` (star) and `type 1` (flower) entries — the
abundant, score-only tier — plus exactly **one `type 2` (carrot)** entry per zone — the scarce,
fully-enumerable, victory-gating tier. `CARROTS_COUNT == 9` (all nine collected) is required for
victory; there is no "collect enough of them" partial-completion path like Mario 64's, which
matches the smaller total (9, not 120) and the game's shorter, more deliberate session shape (R206).
Every zone has exactly one carrot — a clean, evenly-distributed "collect everything" goal, not a
weighted/gated one (no zone requires another zone's carrot first, per `asm_game.py`'s victory
check reading only the flat `CARROTS_COUNT` total, not a per-zone unlock sequence).

## Implementation Guidance

- **Keep the scarce tier fully enumerable as the world grows (C7).** The moment a future
  world-scale expansion makes "one carrot per zone" produce, say, 40+ carrots, the map screen
  (already a 3×3 heart grid) must scale its own display accordingly (see R203/R204) — a "collect
  everything" goal only stays motivating if the player can always see how many remain and where.
- **Consider a partial-victory threshold once the scarce tier grows large enough** (Mario 64's
  70-of-120 pattern) — appropriate once the world genuinely can't expect 100% completion in one
  sitting; not appropriate at today's 9-carrot scale, where 100% is the right bar.
- **Do not introduce inter-zone gating** (carrot N required before zone M unlocks) without an
  explicit design decision recorded in a future GDS/ADS document — the current flat, ungated
  structure is a real design choice (every zone reachable and completable independently) worth
  preserving deliberately, not eroding by accident as content is added.
- **The abundant tier (stars/flowers) has no completion requirement** — keep it that way; forcing
  100% star/flower collection would collapse the two-tier distinction this genre's convention
  depends on.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R206 (goal density directly shapes pacing) · R211 (Zelda/Pokémon case studies share this same
tiered-collectible structure).
