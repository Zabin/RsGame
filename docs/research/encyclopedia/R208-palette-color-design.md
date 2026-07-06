# R208 — Palette & Color Design Under CGB Constraints

- **Document ID:** R208 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R104 (the hardware palette mechanism this design works within)
- **Referenced By:** R209 (pixel-art technique applies these palette choices at the tile level),
  R211 (case studies exemplify strong CGB-era palette design)
- **Produces:** grounds `build_rom.py`'s per-zone palette color choices
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R104, R209, R211

## Purpose

How to spend a 4-color-per-palette, 8-palette budget on *design* grounds (mood, readability,
zone identity) — distinct from R104, which covers the hardware mechanism itself.

## Scope

4-color palette allocation strategy (base/shadow/highlight-style budgeting), per-zone identity
through color, and the real ceiling this project is already pressing against (per `BL-0009`).

## Concepts

A widely-used allocation pattern for a small, fixed color budget: **2–3 colors per "part," roughly
a base tone, a shadow, and a highlight**, keeping any individual object legible while still
reading as shaded/three-dimensional rather than flat.[^1] With only 4 colors *total* per palette
(one of which, for BG palettes, is typically reserved as a "background/sky" tone shared across
many tiles), the effective per-object budget is even tighter than a general "pick 4–8 colors"
guideline suggests — every color placed must earn its slot. The Game Boy Color's real ceiling is
**8 BG palettes + 8 OBJ palettes**, 4 colors each, chosen from a 32,768-color RGB555 space, giving
up to 56 simultaneous on-screen colors when every palette is used fully and distinctly (R104).[^2]

### Sources
[^1]: [Pixel Art Design for Game Development — Alain Galvan](https://alain.xyz/blog/pixel-art-design-for-game-dev), accessed 2026-07-06.
[^2]: cross-referenced from GBC hardware capability summaries corroborating R104's BCPS/BCPD facts (the "56 colors from 32,768" figure is a standard, frequently-repeated GBC spec restatement — treat as well-established but not independently re-derived from a primary spec sheet this session).

## Operational Context

Bunny Quest's per-zone palette strategy (confirmed by direct `build_rom.py` read) already follows
the base/shadow/highlight-style 3-tone budgeting closely: each zone's terrain palette uses a
light/mid/dark triple of one hue family (e.g. Beach's sand tones, Forest's greens, Mountain's
grays/whites) plus a shared sky/background tone — giving each zone a distinct, legible identity
purely through color, exactly the "color as zone identity" technique the best-regarded CGB titles
use (R211). This is **already at real risk under R104/`BL-0009`'s finding**: 9 zones sharing 8 BG
palettes means at least one pair must reuse a palette, and MSTR-001 C7's much larger world target
makes this tension structural, not incidental.

## Implementation Guidance

- **A future zone must either reuse an existing palette deliberately** (pairing zones whose
  intended mood/tone genuinely overlaps, e.g. two "warm arid" zones sharing dune tones) **or the
  project must accept and design around visually-repeated zone tinting** as C7 scales up — this
  is the same finding `BL-0009` already raised; treat any new zone's palette assignment as an
  explicit choice between those two options, never an unexamined default.
- **Reserve one tone per palette for a shared sky/background role** (as the current zones already
  do) — this keeps the remaining 2–3 tones focused on the zone's actual identifying color, rather
  than spreading 4 colors across too many jobs.
- **OBJ palettes are a separate, smaller budget** (also 8, R104) shared across all sprite types
  (player, star, flower, carrot, and any future NPC/enemy) — a new sprite type competes with the
  existing four for this space; audit current OBJ palette usage before assuming one is free.
- **Color choices should reinforce zone-specific mood**, not just avoid clashing — R211's case
  studies (Oracle of Seasons/Ages' vibrant palette-per-dungeon-type, Shantae's saturated
  fantasy-adventure palette) are useful comparative references for "does this zone's palette
  actually feel like its theme," not just "is it technically distinct from its neighbors."

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R104 (the hardware mechanism/budget this design works within) · R209 (applying these palette
choices at the individual-tile pixel-art level) · R211 (comparative case studies of strong CGB
palette design).
