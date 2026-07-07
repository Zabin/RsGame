# R209 — Pixel Art Technique at 8×8/2bpp Scale

- **Document ID:** R209 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R303 (the 2bpp encoding this technique's output is packed into), R208
  (palette-level color budgeting this topic applies at the tile level)
- **Referenced By:** R210 (the craft technique an AI-assisted workflow must still apply)
- **Produces:** grounds how any new `tiles.py` art (a `pix` array passed to `enc()`) should be
  authored
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R303, R208, R210, R211

## Purpose

**Filed per backlog `BL-0013`** (project owner's direct request for a pixel-art research
thread). This topic is the craft-technique half of that request: how to draw a good 8×8 (or
8×16-paired, R105) tile within a 4-color budget, independent of *how* the pixels get produced
(hand-drawn or AI-assisted, R210 covers that).

## Scope

Silhouette-first design, the 2–3-colors-per-part budgeting convention, outline use, and the
anti-aliasing-vs-readability tradeoff — each applied to this project's actual 8×8/4-color/256-tile
constraints.

## Concepts

**Silhouette is the primary readability test:** if a sprite or tile isn't recognizable as a solid
single-color shape, no amount of internal color detail will fix it — design the shape first, add
color after, and check the silhouette in isolation before finishing a tile.[^1] **Color budgeting
per part:** 2–3 colors per distinct "part" of a subject (a base tone, a shadow tone, a highlight
tone) is a common allocation that keeps small subjects legible while still reading as shaded;
scaled down to this project's hard 4-colors-*total*-per-palette ceiling (R104), a single tile
effectively gets a background/base/shadow/highlight quartet with almost no slack.[^2]
**Anti-aliasing actively hurts readability at very small scale** — smoothing edges reduces the
crisp, high-contrast boundaries that make a tiny image legible; outlines (a single dark-tone
pixel border) are frequently the *opposite* choice that works better for small character/object
art, though less appropriate for tiling background terrain (where a hard outline on every tile
edge would visibly seam the tiled repeat).[^2] The commonly-cited "sweet spot" sizes (16×16,
32×32) are both larger than this project's native 8×8 single-tile unit — meaning an 8×16 OBJ pair
(R105) is closer to that "forces simplicity" 16×16 constraint than a lone 8×8 BG tile is, which
matters when judging how much detail a given tile can actually carry.

### Sources
[^1]: [Pixel Art for Games: A Practical Guide — Ziva](https://ziva.sh/blogs/pixel-art-tutorial), accessed 2026-07-06.
[^2]: [Pixel art fundamentals: everything you need to know — Sprite-AI](https://www.sprite-ai.art/guides/pixel-art-fundamentals), accessed 2026-07-06.

## Operational Context

Bunny Quest's existing art (per direct `tiles.py` read) already applies several of these
techniques correctly: the player sprite uses the full 8×16 OBJ budget (R105) rather than a single
cramped 8×8, giving it enough area for a recognizable silhouette across two animation frames; UI
icons (hearts, arrows, digits) are simple, high-contrast, outline-free glyphs appropriate for
their tiny, non-shaded role; the seeded terrain-fill technique (R203) uses exactly two tile
variants per terrain type (a "plain" and a "bump/tuft/ripple" variant) sprinkled pseudo-randomly —
a pragmatic way to add visual texture across many tiles without hand-authoring unique art for
each, while staying within the tile budget (R303).

## Implementation Guidance

- **Design new character/object sprites silhouette-first** — sketch (even mentally, via the `pix`
  array's 0/non-0 shape before assigning specific color indices) the solid shape, confirm it reads
  clearly, and only then decide which 2–4 color indices go where.
- **Budget colors per-tile as background + base + shadow (+ highlight if the 4th slot allows)** —
  do not spread all 4 palette colors evenly without a plan; an unplanned 4-color tile usually
  reads as flatter than a deliberately 3-tier one with one color reserved for background/negative
  space.
- **Use outlines for characters/objects, not for tiling terrain** — an outlined BG tile creates a
  visible grid seam when repeated across many cells; this project's existing terrain tiles are
  correctly outline-free, and new terrain art should follow suit, while new OBJ sprites may
  benefit from a one-pixel dark-tone outline for silhouette clarity.
- **Never introduce gradient/anti-aliased edges into an 8×8 tile** — at this resolution, softened
  edges cost more readability than they add smoothness; hard, deliberate color-index boundaries
  are the correct choice, consistent with the existing tile set's style.
- **New terrain variants should follow the existing two-variant seeded-sprinkle pattern** (R203)
  rather than introducing a third variant per terrain type without also updating `_fill()`'s
  sprinkle-ratio logic — keeps the visual texture technique consistent project-wide.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R303 (the 2bpp format this technique's pixel arrays are encoded into) · R208 (palette-level color
budgeting, one level up from this topic's per-tile application) · R210 (the AI-assisted
generation workflow that must still produce output honoring this topic's craft rules) · R211
(comparative case studies demonstrating these techniques applied well).
