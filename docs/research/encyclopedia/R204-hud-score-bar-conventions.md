# R204 — HUD & Score-Bar Conventions

- **Document ID:** R204 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R203 (the row-0 slot the HUD occupies within the screen grid)
- **Referenced By:** R218 (extends the "visual weighting by importance" principle to a
  combat-mode health element, `BL-0133`)
- **Produces:** grounds `tilemaps.py`'s `_score_bar()` function
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R203

## Purpose

What makes a persistent single-row HUD legible at a glance, and whether Bunny Quest's current
score bar follows that convention.

## Scope

Static vs. animated HUD elements, visual weighting by gameplay importance, and this project's
current row-0 score-bar layout.

## Concepts

**Static HUD elements** — fixed-position displays that update only their numeric/text content,
without animated transitions — are the standard choice for constantly-relevant, low-drama stats
like score, ammo, or time; they prioritize instant legibility over visual flourish.[^1] **Visual
weighting by importance** — an element that affects moment-to-moment survival (health) is
typically sized/positioned more prominently than one that's informational but non-critical
(currency, a secondary score) — the design principle is that HUD real estate should be spent in
proportion to how much the stat matters to immediate decisions.[^2] Readability is the dominant
constraint: icons must be instantly recognizable and text must be legible at the game's native
resolution, ahead of any stylistic consideration.[^1]

### Sources
[^1]: [Mastering Game HUD Design — Polydin](https://polydin.com/game-hud-design/), accessed 2026-07-06.
[^2]: [How To Design A Good And Unique Game HUD — RocketBrush](https://rocketbrush.com/blog/designing-practical-and-pretty-hud-in-video-games), accessed 2026-07-06.

## Operational Context

`tilemaps.py`'s `_score_bar()` (confirmed by direct code read, shared by all 9 zone screens) is a
static, single-row HUD occupying row 0 of every zone: a carrot icon + digit (carrot count,
formatted `N-9` — confirmed by the literal `-` and `9` tiles placed at fixed columns 3/4,
directly showing the "N of 9" framing this game's scarce-tier goal, R201, calls for) at the left,
a star icon + 3-digit score field to its right, and the zone's name spelled out via `_str()`
starting at column 12. This matches the "static, instantly-legible, importance-ordered" convention
well: the scarce, victory-gating stat (carrots, "N-9") is positioned first/leftmost — arguably the
most important information — with the abundant/secondary stat (star/flower score) placed second.
No animation, no dynamic sizing — purely numeral updates, consistent with R204's "static HUD"
convention for a non-time-critical stat.

## Implementation Guidance

- **Keep the carrot count's "N-9" framing legible as the world grows (C7).** A future carrot total
  beyond single digits (more than 9 zones) breaks the current fixed-width `N-9` display (`_put`
  writes exactly one digit tile at a fixed column) — this is a concrete, near-term HUD redesign
  question for whoever plans the C7 expansion, not a cosmetic afterthought; the map screen's 3×3
  heart grid (R201/R203) has the identical scaling problem and should be redesigned in the same
  pass.
- **Preserve the leftmost-position-for-most-important-stat convention** if the HUD layout is ever
  revised — don't reorder the carrot/star fields without a stated reason, since the current
  ordering already matches the importance-weighting principle.
- **The zone-name field (`_str()` at column 12) doubles as a landmark-identification aid** (R203)
  — as important to the "where am I" read as any in-world visual landmark; keep it present on
  every new zone screen.
- **This HUD is entirely static/non-animated by design** — a future addition (e.g. a pulse/flash
  on carrot pickup) would be a deliberate departure from the current convention and should be
  scoped as its own design decision, not folded in incidentally with an unrelated change.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R203 (the row-0 screen-composition slot this HUD occupies on every zone screen).
