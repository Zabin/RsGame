# GDS-08 — Presentation Architecture

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-07](07-data-model.md); the next level,
> [GDS-09 Interface Specification](09-interface-specification.md), builds on this one.

## Purpose

Screens and their composition, sprite strategy (8×16 OBJ pairs — corrected from this level's own
scaffold, which said 8×8; the shipped game uses 8×16 mode, R103/R105), palette assignment
strategy, HUD/score bar, audio engine shape.

## Content

### 1. Screen composition strategy

Every one of the 14 screens ([GDS-04](04-domain-model.md)) follows one authoring pattern
([R203](../research/encyclopedia/R203-screen-composition-tile-grid.md)): a base terrain fill via
a seeded pseudo-random two-variant sprinkle (`_fill()`), then 3–7 hand-placed landmark elements
giving the screen its identity, with row 0 reserved for the HUD (§3) on every zone screen. This
is a deliberate, consistent authoring convention — not an accident of nine independently-designed
screens converging by coincidence — confirmed by all nine zone functions sharing the identical
structural shape in `tilemaps.py`.

### 2. Sprite strategy

The player sprite uses **8×16 OBJ mode** (LCDC bit 2 set, `LCDC=0x97` —
[R103](../research/encyclopedia/R103-lcdc-stat-registers.md)), each frame an adjacent
even/odd tile-index pair ([R105](../research/encyclopedia/R105-oam-sprites-dma.md)): two walk
frames (`0x00`/`0x01` and `0x02`/`0x03`, [GDS-07](07-data-model.md)). This mode was adopted via
commit `9a587ac` specifically to fix an earlier invisible-sprite bug — a real, already-made
architectural decision, not an incidental default (worth a future ADR per
[`BL-0016`](../pipeline/backlog.md)). Every collectible (star, flower, carrot) is also an OBJ
sprite, sharing the same 40-entry OAM budget with the player — currently well within budget (a
handful of collectibles per zone plus the player), but a real ceiling
([R105](../research/encyclopedia/R105-oam-sprites-dma.md)) a future content-dense zone must
respect explicitly, not assume infinite.

### 3. HUD

A static, non-animated row-0 bar on every zone screen
([R204](../research/encyclopedia/R204-hud-score-bar-conventions.md)): carrot progress (`N-9`,
leftmost — the scarce, victory-gating stat) and score (star icon + 3 digits, secondary). No
per-UI-screen HUD (title/intro/save/map/victory each have their own bespoke, non-HUD layout).

### 4. Palette assignment strategy — corrected picture

Per [GDS-07](07-data-model.md)'s byte-level confirmation (correcting
[`BL-0009`](../pipeline/backlog.md)'s original framing): BG palettes are assigned **by terrain
family, not one-per-zone**, and are already substantially reused —

| Terrain family (BG palette) | Zones |
|---|---|
| grass (0) | Forest, Plains |
| sand/dirt (1) | Beach, Desert |
| water (3) | Lake |
| stone (4) | Mountain, Village, Cave |
| brick/red (5) | Castle |

Only 5 of 8 BG palettes serve zone terrain today; palette 4 alone covers three zones. This is a
deliberate strategy (assign by *what the terrain looks like*, let visually-similar zones share)
that already accommodates real growth headroom before the 8-palette ceiling binds — the correct
framing for [GDS-01](01-concept-of-play.md) §5's open C7 world-scale question to build from.
OBJ palettes: 4 of 8 in active use (bunny, star, flower, carrot); 4 reserved/unused.

### 5. Audio engine shape

Single-channel (Channel 1 only, [R108](../research/encyclopedia/R108-apu-channels-registers.md))
melody: one 16-bar original theme
([R207](../research/encyclopedia/R207-gb-chiptune-composition.md)), initialized once at boot
(`NR52`/`NR50`/`NR51`/`NR11`/`NR12` set, then per-note `NR13`/`NR14` writes drive playback).
Channels 2–4 are entirely unused — real headroom for a future harmony/percussion layer without
disturbing the existing melody (R108's guidance).

### 6. Process note — authoring new presentation content

Per [R210](../research/encyclopedia/R210-ai-assisted-tile-art-workflow.md): any future tile, screen,
or sprite added to this presentation layer should be authored design-grid-first (an explicit,
reviewable pixel grid before touching `tiles.py`), budget-checked against the tile-index and
palette ceilings this level documents (§2/§4), then rendered and visually reviewed via
`run-bunnygarden`'s screenshot capability before being treated as done — not designed and
committed to code in one step. This is a process convention for `08-content-authoring` to follow,
not new content itself.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for (byte-level
      specifics — tile indices, palette indices — are cited from [GDS-07](07-data-model.md)
      rather than re-derived here).
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-07`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `memory.md`'s palette/tile quick-reference tables are already
superseded by [GDS-07](07-data-model.md) (the byte-level authority); this level draws its
palette/tile facts from GDS-07, not from `memory.md` directly. `tiles.py`/`tilemaps.py`/`music.py`'s
own code structure is the direct source for the composition/sprite/audio strategy described
above, confirmed by direct read. **Decision: this level supersedes `memory.md`'s presentation-
strategy framing entirely** (its palette table already superseded at GDS-07; this closes the loop
for the remaining strategy-level prose). The level's own scaffolded Purpose text ("8×8 OBJ
pairs") is corrected to 8×16 in this authoring pass, matching the shipped `LCDC=0x97` fact.
