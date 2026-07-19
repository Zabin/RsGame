# R220 — Movement-Based Multi-Directional Weapon Aiming Conventions

- **Document ID:** R220 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R218 (opt-in combat sub-mode design — this topic extends its projectile axis),
  R202 (8-bit game feel — movement/input tolerance conventions this topic's direction-derivation
  choice must stay consistent with)
- **Referenced By:** none yet — grounds a future `03-architecture-design-synthesis` pass on
  `BL-0157`
- **Produces:** grounds a direction-representation choice for widening `PLAYER_DIR`'s own
  established 2-state (left/right) shape into a fuller facing/aim concept
- **Feature Mapping:** `BL-0157` (weapon directionality based on movement)
- **Related Topics:** R218, R202

## Purpose

Ground how comparable titles derive a projectile's firing direction from player movement, without
a dedicated aim input, for the Infinite Mode combat sub-mode (`FS-112`). Today `PROJ_DIR` mirrors
`PLAYER_DIR`'s own real 2-value encoding (0=right, 1=left) — direct code read confirms
`PLAYER_DIR` is written only by `handle_play_input`'s RIGHT/LEFT branches, never UP/DOWN, so the
weapon can only ever fire horizontally (`BL-0151`, already a tracked documentation-accuracy
finding on this exact gap). The user asked specifically that the weapon also fire up/down/diagonal
"based on movement," and asked for research into how other games handle this before it is
architected — this topic is that research.

## Scope

Conventions for deriving a discrete firing direction from player movement input, with no separate
aim button: discrete 4-way vs. 8-way direction schemes; "moving-direction" vs. "last-faced-
direction-when-idle" semantics; how genre precedent (overhead run-and-gun titles, and this
project's own closest genre neighbor, top-down action-adventure) has handled the same problem.
Explicitly **out of scope**: the exact SM83-level representation of a widened `PLAYER_DIR`
(a `03-architecture-design-synthesis` decision, not resolved here); diagonal projectile movement's
own per-frame stepping algorithm (an implementation-level concern once the direction model is
chosen); whether the player's own sprite should visually reflect new directions (a
`08-content-authoring` concern if the architecture pass calls for new art).

## Concepts

**4-way vs. 8-way overhead-shooter direction schemes.** Classic overhead run-and-gun titles —
*Front Line* (1982), *Commando* (1985), *Ikari Warriors* (1986) — tie the player's firing
direction directly to movement input, with no separate aim control.[^1] The genre splits into two
well-documented shapes: **4-directional** schemes (orthogonal only, no diagonals) favor faster,
more chaotic action and make enemies that can fire diagonally comparatively more dangerous (the
player cannot answer in kind); **8-directional** schemes add the four diagonals, which changes the
core tactical texture — the player must continuously trade off "stay back and hold a firing lane"
against "advance and gain more simultaneous firing angles," since movement and firing direction
are the same input.[^1] Both shapes are genuinely genre-authentic conventions, not one being
strictly an upgrade of the other — the choice is a tone/pacing decision, not a technical one.

**"Moving-direction, or last-faced-direction when idle" semantics (Zelda's own convention).**
A directly relevant, GB-era precedent for deriving an *action* direction from *movement* state
without a separate aim input: in *The Legend of Zelda: Link's Awakening*, Link's spin-attack
direction (and, more generally, his sword's facing) is determined by his current movement
direction if he is moving, or by the last direction he faced if he is standing still.[^2] This is
exactly the "last-pressed-direction vs. held-direction" semantics question the user's own request
named — the Zelda convention resolves it as: **held movement wins while moving; the most recent
facing persists when idle**, rather than requiring the player to hold a direction at the moment of
the attack/fire input.

### Sources
[^1]: [A Review of Overhead 8-Directional Shooters — cxong.github.io](https://cxong.github.io/2016/04/a-review-of-overhead-8-directional-shooters), accessed via search 2026-07-19: names Front Line, Commando, and Ikari Warriors as overhead titles where movement direction determines firing direction with no separate aim control; contrasts 4-directional (faster, more chaotic, diagonal-firing enemies disproportionately dangerous) against 8-directional (continuous movement/firing tradeoff) schemes. **Single-source claim, flagged** — a personal design-analysis blog, not independently corroborated by a second source in this pass; recommend a fetch-verification pass once direct URL access is available in this environment (blocked this session, see Operational Context).
[^2]: Community-documented technical note on Link's sword/spin-attack animation direction, accessed via search 2026-07-19 (search-derived summary; the underlying source page could not be directly fetched in this session — see Operational Context). Describes the spin-attack's rotation direction as determined by Link's current movement direction if moving, or his last-faced direction if standing still. **Needs fetch-verification**: this claim should be re-confirmed against a primary source (a disassembly note or a directly quotable wiki page) before it grounds an architecture-level decision.

## Operational Context

**A genuine research-access gap in this session, named honestly rather than silently worked
around:** this pass's outbound web access was restricted to the `WebSearch` tool only — every
`WebFetch` attempt against five different, unrelated hosts (Wikipedia, Contra Wiki, StrategyWiki,
Steemit, a personal GitHub Pages blog) returned a `403` from this session's own egress-policy
proxy, confirming a blanket restriction rather than a per-site block. `WebSearch` itself worked and
returned real, attributable synthesized content, which is what grounds every claim above — but
neither citation in this topic was verified against a directly fetched, quotable primary page, per
this skill's own methodology fallback ("if WebSearch/WebFetch are unavailable, mark citations
'needs fetch-verification' and report the gap"). Both citations are marked accordingly. A future
pass with unrestricted `WebFetch` access should re-verify both before this topic grounds a binding
architecture decision at `03`.

Direct code read confirms the exact current shape this topic must widen: `PLAYER_DIR` (`asm_game.py`)
is written only by `handle_play_input`'s RIGHT/LEFT branches (0=right, 1=left) — UP/DOWN movement
never touches it, so "facing" is architecturally a 2-state fact today, not merely an
implementation shortcut (`GDS-07` documents it the same way). `PROJ_DIR` (`0xC6D8`, `IP-1122`)
copies `PLAYER_DIR` verbatim at fire time; `inf_projectile_update` only ever `INC`/`DEC`s `PROJ_X`
— there is no vertical or diagonal projectile-movement code path today at all.

## Implementation Guidance

- **Both 4-way and 8-way are legitimate, genre-authentic choices** — this research does not
  recommend one over the other; that is a tone/pacing call for `03-architecture-design-synthesis`
  to make against this project's own already-decided combat pacing (`ADS-002`), not something
  this topic should decide unilaterally.
- **Recommend the "moving-direction, else last-faced-direction" semantics** (the Zelda
  convention) over a "must be actively holding a direction at the moment of firing" rule — it
  matches this project's own existing input feel (the player can already stand still after
  moving, per `T7`'s own regression coverage) and avoids a frustrating edge case where releasing
  the D-pad a frame before pressing fire would otherwise produce an undefined or default
  direction.
- **A widened `PLAYER_DIR` is an architecture-level change, not merely a weapon-code change** —
  `GDS-07`'s own data-model documentation of `PLAYER_DIR` as "facing (left/right)" would need a
  delta regardless of which direction scheme is chosen, since the fact being widened is a
  domain-model concept other code could plausibly read in the future (sprite rendering, future
  mechanics), not private state internal to the weapon.
- **Re-verify both citations above before they ground a binding decision** — this pass's
  `WebSearch`-only grounding is enough to inform `03`'s own framing of the two viable schemes,
  but not yet strong enough (single-sourced, unfetched) to cite as settled precedent in an ADR.

## Feature Mapping

`BL-0157` (weapon directionality based on movement) — grounded above, with an explicit, honest
research-access limitation named rather than papered over. Recommends `03-architecture-design-
synthesis` receive this topic alongside the still-open question of 4-way vs. 8-way (a tone
decision this research deliberately does not make) and the "moving, else last-faced" direction
semantics (which this research does recommend, subject to the fetch-verification caveat above).

## Related Topics

R218 (opt-in combat sub-mode design — this topic extends its projectile axis specifically), R202
(8-bit game feel — this project's existing movement/input tolerance conventions the chosen
direction-derivation rule must stay consistent with).
