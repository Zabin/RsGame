# GDS-08 — Presentation Architecture

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment — see "Presentation Architecture delta" below).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-07](07-data-model.md); the next level,
> [GDS-09 Interface Specification](09-interface-specification.md), builds on this one.
>
> **Reading this document:** §§1–6 below describe presentation **as currently shipped** and
> remain accurate. The delta section is the **normative standard** [MSTR-001](../master/MSTR-001-program-vision.md)
> **C8** requires and the **C9** biome-transition strategy — the target `09-content-review` will
> judge future content against, not a description of what exists today.

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

## Presentation Architecture delta (2026-07-09 — normative standard, grounds C8/C9)

### 7. The normative aesthetic standard (MSTR-001 C8)

C8 requires presentation be "a first-class, reviewed quality commitment... checked against a
normative standard, not left as an unstated craft preference." This section **is** that standard
— the checklist `09-content-review` judges future content against, and the criteria
`07-implementation-planning` packages should cite in their Verification Checklists. Grounded
directly in [R209](../research/encyclopedia/R209-pixel-art-technique.md)'s craft rules (already
partially honored by the shipped art, per R209's own Operational Context) and D4's "smooth,
every screen/room/view clean" language:

**Tile/sprite craft (per R209):**
- [ ] Every new tile/sprite is **silhouette-first**: recognizable as a solid shape before color
  is assigned (R209 §"Implementation Guidance").
- [ ] Color budget follows **background + base + shadow (+ highlight)** — no unplanned
  even-spread across all 4 palette slots.
- [ ] **Outlines on characters/objects, never on tiling terrain** (an outlined terrain tile
  creates a visible seam when repeated — R209's explicit rule, already honored by the shipped
  terrain set).
- [ ] **No anti-aliased/gradient edges** at 8×8 scale — hard color-index boundaries only.
- [ ] New terrain variants extend the existing two-variant seeded-sprinkle pattern (`_fill()`,
  R203) rather than introducing an inconsistent third variant.

**Clean-screen rules (per D4, newly operationalized — no shipped precedent needed before now,
since every existing screen is hand-authored and reviewed once):**
- [ ] No undefined/blank-placeholder tile indices anywhere in a rendered screen.
- [ ] No illegal tile-adjacency pairs within a screen (a terrain tile from one biome family never
  directly abuts a structurally incompatible tile from an unrelated family within the same
  screen's fill).
- [ ] Every screen edge that signals a transition (directional arrow, per GDS-01) has a
  consistent, correctly-rendered neighbor on the far side once generated (a generated-world
  instance of the same "does the seam look right" check `09-content-review` already performs on
  hand-authored screens).

**Smoothness (per D4, generated-world-specific — extends R102's redraw-cost analysis, GDS-07's
delta):** a screen transition (generated or hand-authored) completes within the existing
LCD-off `do_screen_redraw`/`copy_screen` budget (GDS-07/R102) — no new, slower transition
mechanism is introduced by generated content; generation itself (ADR-0009, at new-game creation
only, not per-transition) does not block the smoothness bar for in-session travel.

### 8. Biome-transition presentation strategy (MSTR-001 C9, grounds ADR-0009's grammar)

Per [R212](../research/encyclopedia/R212-wordless-environmental-storytelling-biome-grammar.md)'s
grounding and **D2's clarification** (one biome per screen — no intra-screen blending): the
existing **terrain-family palette strategy (§4 above)** already has the right shape to extend,
not replace. Today, 5 of 8 BG palettes serve zone terrain (grass, sand/dirt, water, stone,
brick/red), each a single, consistent per-family color identity. Biome-transition presentation
adds one requirement to that existing strategy: **palettes for grammar-adjacent biome families
should step coherently**, not be assigned arbitrarily. Concretely — following R212's own cited
precedent (Minecraft's temperature-based adjacency smoothing) applied at the *palette* rather
than *terrain* level — a biome sequence like water → beach → grassland → hills → mountains → sky
should read, in palette terms, as **blues stepping toward sands stepping toward greens stepping
toward grays stepping toward whites/light-blues**, each adjacent pair sharing a plausible
color-family relationship, rather than two arbitrary, unrelated palettes placed next to each
other. This is a **content-authoring guideline for whichever future biome-family palette
assignments are made**, not a change to the 8-palette budget itself.

**The palette ceiling binds biome-family *count*, not blending — confirmed, not merely
asserted.** Because D2 rules out any two biomes sharing a single screen, there is no
per-screen palette-mixing problem for this increment to solve (unlike, say, a smooth-scrolling
game that blends adjacent screens' colors mid-frame). The existing terrain-family reuse pattern
(§4/§5) — palette 4 alone already serving three zones (Mountain, Village, Cave) — demonstrates
the ceiling has real headroom for a *generated* world's likely biome-family count too, provided
biome families continue to be defined at the same granularity today's zones are (a handful of
distinct visual families, not one family per generated region). **Exact biome-family count and
palette assignment for a specific `WorldScale` is deferred to the implementation package that
sizes it** — this level confirms the *strategy* (family-based reuse, adjacency-aware stepping),
not a final palette table.

**Shipped as of `IP-1031`:** the biome-family vocabulary this section named in the abstract is
now the concrete, running mapping — Water→`lake_screen()`, Sand→`beach_screen()`,
Grass→`forest_screen()`, Stone→`mountain_screen()`, Brick→`castle_screen()` — five of the nine
pre-existing zone screens reused verbatim as each family's canonical representative (zero new
tile art, zero new palette entries), dispatched at runtime by `REGION_GRAPH`'s generated biome-id
(`IP-1030`). This is the concrete instantiation of §8's family-based-reuse strategy, not a
revision of it; the four remaining shipped zone screens (`village_screen`, `cave_screen`,
`desert_screen`, `plains_screen`) remain unwired, available as future per-family variety.

**Extended to spawn content by `IP-9070` (2026-07-11):** the identical five-way representative
choice above now also governs `ZONE_COLLECTS` (`docs/architecture/07-data-model.md`
`setup_zone_collects`) — reduced from 9 zone-named collectible lists to the same 5
biome-family-representative lists (Water→old `Z3`/Lake, Sand→old `Z0`/Beach, Grass→old
`Z1`/Forest, Stone→old `Z2`/Mountain, Brick→old `Z8`/Castle), reusing each list's original item
positions verbatim. `setup_zone_collects` now reads `REGION_GRAPH`'s biome-id and indexes
`zc_table` by it, mirroring `dsr_p`'s own screen dispatch exactly — spawn content and screen
art now track the same biome-id, closing the gap `BL-0059` found (spawn content had been left on
the old fixed `CUR_ZONE`-indexed model while screen art was already generalized by `IP-1030`).

### 9. Cross-reference: tile index budget (informational, per GDS-07's delta)

[GDS-07](07-data-model.md)'s delta forward-referenced this section for the actual biome-family
tile/palette strategy. §§7–8 above are that answer: biome families reuse the existing
terrain-family tile-block convention (§4 above: 8-tile-aligned blocks, `0x70`–`0xB5` today, next
free block `0xB8`) — a generated world's biome families draw from this same convention, sized to
however many distinct families the eventual content package defines, not a new tile-allocation
scheme.

### 10. Maze-blocked edge indicator — `GDS-08` delta for `BL-0068`/`FS-108` (decided 2026-07-11)

`ADR-0012`'s maze pass (`IP-1070`, shipped) means a screen edge with no arrow is now ambiguous
between two cases the player cannot otherwise distinguish: a true grid boundary (no candidate
region exists in that direction) and a maze-blocked-but-grid-adjacent edge (a region exists there,
but the maze doesn't connect to it). `FS-108`'s logic half (`FR-2330`) already specifies the
render-time classification that tells them apart; this section decides the third visual state that
classification needs to actually display, closing `FS-108`'s own Open Question 1.

**Decision: a distinct tile shape, not a recolored arrow, on the existing arrow's palette.**
`draw_region_arrows` (`asm_game.py:918`, `IP-1030`) already writes a directional arrow tile at one
of four fixed screen-edge positions (`ARROW_ADDR_U`/`D`/`L`/`R`) with a hardcoded palette-2 (UI/gold)
attribute whenever `REGION_GRAPH` has a neighbor in that direction. Two ways to add a third state:
recolor the same arrowhead shape (cheapest — zero new tile-index cost, one new palette entry), or
draw a genuinely different silhouette on the *same* palette-2 attribute the open arrow already
uses. **This level decides the latter.** Per §7's tile-craft checklist above ("silhouette-first:
recognizable as a solid shape before color is assigned," R209), a same-palette recolor asks the
player to distinguish state by hue alone at 8×8 scale from three screen-edge tiles away — a weak
signal, and one that degrades for any player with reduced color discrimination. A distinct shape
(a short broken/dashed bar — two short segments with a visible gap, silhouette-distinct from the
open arrow's solid filled triangle) reads as "interrupted path" against "open path" without relying
on color at all, and costs nothing in palette budget: it reuses palette 2 verbatim, the same
attribute byte `_arrow_write` already writes for the open state. **No new BG palette entry is
spent** — palettes 6/7 (`tree/leaf`, `accent purple`, both currently unused as zone-terrain
palettes per [GDS-07 §5](07-data-model.md)) remain free for a future need, not consumed here.

**Tile-index placement:** 4 new tiles, one per direction (mirroring `TL_ARROW_R/L/U/D`'s own
per-direction-tile pattern, not a single rotated tile), at `0x1A`–`0x1D` — the next 4 of the 6 free
slots directly following the existing UI-icon block (`0x10`–`0x19`, [GDS-07 §4](07-data-model.md)),
before the tile map's `Digits` block begins at `0x20`. This continues §4's existing "clean,
8-tile-aligned block per icon family" convention rather than reaching into the `0xB6`+ terrain-block
free space, since this is a UI icon, not a terrain tile. `0x1E`–`0x1F` (2 slots) remain free in the
same block for one more future UI icon. Net cost: 4 tile-index slots (of 74 free), 0 new palette
entries.

**Not decided here (implementation-package-level, `06`/`07`/`08-content-authoring`):** the exact
pixel silhouette (this level specifies the *concept* — a short broken/dashed bar, silhouette-
distinct from the arrow — not a literal bitmap, per this skill's own no-production-code rule); the
exact screen-position offset for each of the 4 directional tiles (the existing `ARROW_ADDR_*`
constants are the natural default — same position as the open-arrow case, since only one of the
two states is ever drawn per edge — but confirming that is a code-level detail for whoever
implements `FS-108`'s rendering half).

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

**Delta record (2026-07-09):** §§7–9 ("Presentation Architecture delta") added, per the adopted
increment plan's Phase 3 and MSTR-001 C8/C9. Delta, not re-authoring — §§1–6 remain the accurate
as-shipped description; §§7–9 are the normative standard/strategy content downstream stage-06/08
work and `09-content-review` will apply once built. No merge-gate box above is reopened.

### 11. Edge-indicator legend/help screen — `GDS-08` delta for `CR-06`/`BL-0100` (decided 2026-07-13)

The project owner asked for a screen explaining the on-screen transition-edge indicator tiles to
the player (`BL-0100`) — today's `FR-2320`/`FR-2330` three-state signal (open arrow / blocked-edge
bar / no indicator, §10 above) has no in-game explanation anywhere; a player must infer the
distinction from play alone. This section decides the new **LEGEND** screen's content and layout;
[GDS-01](01-concept-of-play.md) §4c decides where it sits in the state machine (a new `SELECT`
menu, not a change to `MAP`'s own existing content).

**Decision: a single static, read-only screen showing each of the three indicator tiles next to a
one-line plain-language explanation — no animation, no interactivity beyond exit.** Reuses this
project's own established static-screen layout convention (a title line, a horizontal border rule,
body content, a footer control hint — the exact shape `main_menu_screen()`/`map_screen()` already
use, `tilemaps.py`). Content, three rows:

```
 <open-arrow tile>   OPEN PATH
 <blocked-bar tile>  MAZE BLOCKED
 (blank)             WORLD EDGE
```

Each row places the real tile (`TL_ARROW_U` reused as the representative open-arrow glyph;
`TL_BLOCKED_U` reused as the representative blocked-edge glyph, both already ROM-resident since
`IP-1030`/`IP-1081` — no new tile art, no new palette entry) directly beside its own plain-language
label, so the player compares the *actual* on-screen glyph to its meaning rather than a redrawn
approximation. The third row is the "no indicator" case — deliberately shown as a blank cell (the
real absence of a tile is the point), labeled "WORLD EDGE" rather than left unexplained. Footer:
`"B: EXIT"` (this screen has one control, matching `MAP`'s own single-control footer convention).
No `SELECT`-triggered page-cycling within `LEGEND` itself — it is a single static page, unlike
`MAP`, which already has its own (pre-existing, unrelated) internal content; nothing about this
delta touches `map_screen()`.

**Why one static page, not more:** `R206` (session length/pacing) favors short, low-friction
reference material for a handheld game — a single glance-and-return screen matches that better
than a multi-page manual would, and the entire explanation is three short facts, not a tutorial
needing sequencing.

**Not decided here (implementation-level, `06`/`07`/`08-code-implementation`):** the exact screen
coordinates for each row/label (a direct, low-risk layout choice for whoever implements this,
following `map_screen()`'s/`main_menu_screen()`'s own existing coordinate conventions); whether the
representative tiles are drawn via the existing `_arrow_write`-style helper or a plain `_put()`
call (no palette/VBlank-timing question is raised by a static screen, unlike the live `MAP`/
`draw_region_arrows` case — either is fine, a pure code-shape choice).

- [x] Stub body replaced with real content addressing the stated Purpose (delta, not re-authoring
      — §§1–10 unaffected, no merge-gate box above reopened).
- [x] Every "merges from" source consulted (`FR-2320`/`FR-2330`, `tilemaps.py`'s existing static-
      screen shape, `R206`).
- [x] No production code or byte-level detail beyond what this level calls for — no new tile art,
      no new palette entry, no WRAM address (the new `GAMESTATE` value and menu-cursor byte are
      [GDS-01](01-concept-of-play.md) §4c's/`GDS-07`'s own concern, not this level's).
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together (this delta, alongside
      GDS-01 §4c).

**Delta record (2026-07-13):** §11 added, per `CR-06`/`BL-0100` (project owner request, routed
here by `04-requirements-engineering`'s own finding #15 after it correctly declined to invent this
content at the requirements level). Delta, not re-authoring — §§1–10 remain accurate; §11 is new,
independent content with no dependency on `MAP`'s own future redesign (`BL-0050`, still deferred).
