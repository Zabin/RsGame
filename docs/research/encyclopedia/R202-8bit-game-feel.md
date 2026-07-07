# R202 — 8-bit Game Feel: Movement, Animation Cadence, Collision Tolerance

- **Document ID:** R202 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** none
- **Referenced By:** R211 (case studies exemplify these feel principles)
- **Produces:** grounds `asm_game.py`'s movement/animation/collision constants
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R211

## Purpose

What makes 2D movement and animation "feel right" at this era's frame rate and resolution, so a
future movement or animation change is a deliberate feel decision, not an arbitrary number.

## Scope

Animation-physics synchronization ("skating"), state-matched animation, acceleration/deceleration
feel, and collision-tolerance norms for small-sprite games — each checked against Bunny Quest's
current constants.

## Concepts

**Stride matching:** the horizontal distance a character's run-animation implies per frame must
match the distance the physics/movement code actually moves it, or the character appears to
"skate" — feet sliding rather than planting.[^1] **State-matched animation:** every distinct
movement state (idle, walk, run, jump ascent/peak/descent) should have its own animation; a
character whose idle pose plays while actually moving reads as broken regardless of how good the
idle pose looks on its own.[^1] **Acceleration/deceleration:** instant top-speed and instant stop
reads as stiff; even a couple of frames of ramp-up/ramp-down reads as more deliberate and
weighted.[^2] **Exaggeration for small-scale readability:** at small sprite sizes and low frame
rates, exaggerated counter-motion (arms swinging opposite legs, anticipation frames before an
action) reads as *more* energetic, not less, because subtlety is the first thing lost at small
scale.[^2]

### Sources
[^1]: [Deft and intuitive player character movement in a 2D platformer](https://maryrosecook.com/blog/post/deft-and-intuitive-player-character-movement-in-a-2d-platformer), accessed 2026-07-06.
[^2]: [Platformer Animation: Creating Responsive Character Movement — MoCap Online](https://mocaponline.com/blogs/mocap-news/platformer-animation-guide), accessed 2026-07-06.

## Operational Context

Bunny Quest's current movement model (confirmed by direct `asm_game.py` read) is deliberately
simple relative to the above: constant-speed movement while a direction is held (no acceleration
ramp), 1px/frame per the existing joypad-driven movement routine, with a two-frame walk-cycle
(`PLAYER_FRAME` 0/1, `ANIM_CTR` counting up to a threshold before flipping frame) — i.e. a fixed
cadence, not stride-matched to a variable speed, because there is only one speed. This is a
defensible simplification for the current scope: with only one movement speed, "stride matching"
degenerates to "does the walk-cycle's flip rate look right at 1px/frame," which the project's
"Known Good Behavior" acceptance already covers empirically (playtested, not derived from a
formula) rather than through R202's more general multi-speed guidance.

**Collision tolerance:** `asm_game.py`'s collectible-proximity check compares both the X and Y
distance between player and collectible against a threshold of **10px** (`CP_n(10)`, confirmed at
two call sites in the collision routine) — i.e. a collectible is collected once the player is
within a 10px "radius" (actually a 10×10 box, not a circle, per the two independent axis checks)
of it.

## Implementation Guidance

- **A future acceleration/deceleration feature** (if the game ever adds a run/dash state) must
  re-derive the walk-cycle's frame-flip cadence per speed, following the stride-matching principle
  — the current fixed-cadence approach only works because there is exactly one speed today.
- **The current 10px collision box is generous** relative to the sprite's own footprint (an 8×16
  OBJ pair, R105) — this reads as forgiving/player-friendly, appropriate for the game's
  casual/all-ages tone (MSTR-001 assumption A5). Shrinking it would make collection feel stingier;
  don't shrink it without also reconsidering zone-transition edge tolerances (R203) in the same
  pass, since both are "how forgiving is proximity" decisions that should move together for a
  consistent feel.
- **State-matched animation is already correctly followed** for the two states the game has (idle
  implicitly = no frame-flip; walking = two-frame cycle) — a future new state (e.g. a "collecting"
  animation, a future dash) should get its own distinct frames, not reuse the walk cycle.
- **Exaggeration guidance applies most directly to any new sprite art** (R209/R210) — a small
  8×16 sprite benefits from clear silhouette-level differentiation between frames, not subtle
  shading-only differences that won't read at this scale.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R211 (acclaimed GBC games' animation/movement feel as comparative examples).
