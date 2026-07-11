# GDS-04 — Domain Model

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment — see "Domain Model delta" below; delta 2026-07-10 — SaveGame relationship bullet
> corrected to reflect shipped `ScoreItem` persistence, `BL-0033`).** Owned by
> `03-architecture-design-synthesis`.
> Builds on [GDS-03](03-architecture.md); the next level,
> [GDS-05 Functional Requirements](05-functional-requirements.md), builds on this one.
>
> **Reading this document:** the Entity-relationship overview and Entities below describe the
> game **as currently shipped** and remain accurate. The delta section describes the **target**
> entity model [ADR-0009](adr/ADR-0009-screen-graph-world-generation.md)/
> [ADR-0010](adr/ADR-0010-seed-scale-model.md) commit to — not yet built.

## Purpose

Game entities and relationships: zones, screens, collectibles, carrots, score, save-game, game
states, player. *(This level's own scaffold description said "gifts" — the pre-correction term;
the real entity, per [GDS-01](01-concept-of-play.md) and
[R201](../research/encyclopedia/R201-collectathon-goal-design.md), is the **carrot**. Corrected
here, consistent with the same fix already applied throughout the ladder.)*

## Content

### Entity-relationship overview

```
Zone (×9) ──composes──▶ Screen (zone screen)
  │                          
  ├──hosts, per zone──▶ Collectible (×N, two subtypes)
  │                          ├─ ScoreItem  (star | flower)  — abundant, feeds Score
  │                          └─ Carrot     (exactly 1/zone) — scarce, feeds victory
  │
  └──has──▶ BG Palette (1 of 8, may be shared across zones — see Open Question)

Player ──occupies──▶ exactly one Zone at a time
       ──has──▶ Position, Direction, AnimationFrame

Score       ──accumulates from──▶ ScoreItem collection
CarrotCount ──accumulates from──▶ Carrot collection, one per Zone (CarrotFlags[zone])

SaveGame ──snapshots──▶ { Player.Position, current Zone, CarrotCount, Score, CarrotFlags[9] }

GameState (6 states — owned by GDS-01, cross-referenced not re-described here)
  ──gates──▶ which entities are active/visible (e.g. Collectibles only interactable in PLAYING)

Screen (×14 total = 9 Zone screens + 5 UI screens: Title, Intro, Save, Map, Victory)
  ──rendered for──▶ exactly one GameState (or one Zone, for the 9 zone screens)
```

### Entities

**Zone** — one of 9 fixed instances (Beach, Forest, Mountain, Lake, Village, Cave, Desert,
Plains, Castle), each with a position in a 3×3 grid (`row = index // 3, col = index % 3` —
[GDS-01](01-concept-of-play.md)), one BG palette
([R104](../research/encyclopedia/R104-cgb-palette-system.md)/
[R208](../research/encyclopedia/R208-palette-color-design.md)), and a terrain/landmark
composition ([R203](../research/encyclopedia/R203-screen-composition-tile-grid.md)). A Zone is
also the unit the player occupies at any moment and the unit a Carrot belongs to.

**Screen** — one of the 14 `ALL_SCREENS` entries (confirmed by direct `tilemaps.py` read): 9 Zone
screens (one per Zone, `beach_screen()` … `castle_screen()`) plus 5 UI screens (`title`, `intro`,
`save`, `map`, `victory`) that render independent of any specific Zone. A Screen is a rendering
artifact — the tile/attribute data a `GameState` (or, for Zone screens, the current Zone) causes
to display; it is not itself game state.

**Collectible** — two structurally distinct subtypes sharing one coordinate/type table
(`ZONE_COLLECTS`, [R201](../research/encyclopedia/R201-collectathon-goal-design.md)):
- **ScoreItem** (type 0 = star, type 1 = flower) — abundant, several per Zone, no individual
  identity beyond position; collecting one increments `Score` and the item is consumed.
- **Carrot** (type 2) — scarce, **exactly one per Zone** (9 total across the game), individually
  tracked (`CarrotFlags[zone]` — collected or not), consumed on pickup, feeds `CarrotCount`.

**Player** — a single instance: `Position` (x, y in pixel space), `Direction` (left/right),
`AnimationFrame` (walk-cycle state) — [GDS-01](01-concept-of-play.md) §3/
[R202](../research/encyclopedia/R202-8bit-game-feel.md). The Player entity's `Zone` (which zone
it currently occupies) is itself game state, not a fixed property.

**Score** — a single running total (0–99) accumulated from `ScoreItem` collection across the
whole game (not per-zone) — an abundant-tier stat with no completion requirement
([R201](../research/encyclopedia/R201-collectathon-goal-design.md)).

**CarrotCount** — a single running total (0–9), the sum of `CarrotFlags` — the scarce-tier,
victory-gating stat. `CarrotCount == 9` is the win condition
([GDS-01](01-concept-of-play.md) §4).

**SaveGame** — the persisted subset of all the above: current `Zone`, `Player.Position`,
`CarrotCount`, `Score`, and all 9 `CarrotFlags` — confirmed by direct code read of
`try_load_save`/the save routine as exactly this field set, no more, no less
([R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md)/
[R205](../research/encyclopedia/R205-save-system-design.md)). Notably, `Player.Direction` and
`Player.AnimationFrame` are **not** persisted — a reloaded game always restores the player facing
a fixed default, not whatever direction they were facing when saved; a cosmetic-only gap, not a
functional one.

**GameState** — the 6-state machine ([GDS-01](01-concept-of-play.md) §4, owned there, not
re-described here): TITLE, INTRO, PLAYING, SAVE, MAP, VICTORY. Gates which entities are active —
Collectibles are only interactable in PLAYING; the Map screen reads `CarrotFlags` read-only; SAVE
reads/writes the full SaveGame snapshot.

### Relationships worth naming explicitly

- **Zone ↔ Collectible is one-to-many, but Carrot is constrained to exactly one per Zone** — this
  constraint is not enforced by any code-level invariant (it's a property of how `ZONE_COLLECTS`
  happens to be authored, one `type 2` entry per zone list), so a future content package adding a
  new zone or editing an existing one's collectible list could silently violate it. Worth an
  explicit Verification Checklist item in any future implementation package touching
  `ZONE_COLLECTS` (a note for `07-implementation-planning`, not resolved here).
- **Zone ↔ BG Palette is many-to-one at the CGB's hardware ceiling** ([GDS-03](03-architecture.md)
  §4 palette facts) — already true for at least one pair of the current 9 zones
  ([`BL-0009`](../pipeline/backlog.md)). This domain model does not resolve which zones share,
  only names that the relationship is (or will become) many-to-one, not one-to-one as a reader
  might otherwise assume.
- **SaveGame is a strict subset of live game state, but narrower than it once was** —
  `Player.Direction`/`AnimationFrame` remain **not** persisted (confirmed "not important" by the
  user, 2026-07-07, `BL-0018`). Per-zone `ScoreItem` collected-state, by contrast, **does**
  persist — `SCOREITEM_FLAGS` (`0xC060`–`0xC068`, mirrored to SRAM `0xA013`–`0xA01B`) was added by
  [`IP-1010`](../implementation/packages/IP-1010-per-zone-scoreitem-persistence.md)/
  [`FS-101`](../features/FS-101-per-zone-scoreitem-persistence.md) (implemented and independently
  verified 2026-07-07, [`VR-1010`](../implementation/verification/VR-1010-per-zone-scoreitem-persistence.md)),
  formalizing [`FR-5220`](../requirements/01-functional-requirements.md); confirmed directly
  against [GDS-07](07-data-model.md) §2/§3's WRAM/SRAM tables (2026-07-10 correction, `BL-0033`
  — this bullet previously said the opposite, stale since before `IP-1010` shipped). A reloaded
  zone's score items now correctly reflect their collected/uncollected state from the prior
  session, not an "all present" reset.

## Domain Model delta (2026-07-09 — target state, not yet shipped)

Per **MSTR-001 C9/C10**, **ADR-0009**, and **ADR-0010**: four entity changes and two new domain
rules, superseding the fixed-`Zone`/fixed-`Carrot` shape above **once the corresponding packages
ship** — the entities and rules above remain the accurate as-shipped model until then.

### Changed/new entities

- **`Seed`** *(new)* — a single 16-bit value, player-entered once at new-game creation
  ([ADR-0010](adr/ADR-0010-seed-scale-model.md)), immutable for the life of a save. Initializes
  the world generator's PRNG state
  ([R111](../research/encyclopedia/R111-wram-banking-sm83-prng.md)). A value of 0 is normalized
  to 1 internally (xorshift's nonzero-state requirement) — this normalization is a `Seed`
  property, not a UI validation rule (the player may still enter 0; the domain model handles it).
- **`WorldScale`** *(new)* — a single byte, valid range 2–9, player-entered once alongside `Seed`
  at new-game creation, equally immutable per save. Determines the **count** of `Region` entities
  a generated world contains (`WorldScale × WorldScale`), replacing `Zone`'s fixed count of 9.
- **`Region`** *(replaces `Zone`)* — the generated-world generalization of `Zone`: a `Region` has
  a **biome identity** (one of the terrain families [GDS-08](08-presentation-architecture.md)
  defines — grass, sand/dirt, water, stone, brick/red, etc., generalizing today's Beach/Forest/…
  naming to a *family*, not nine fixed proper names) and a set of **generated adjacency edges** to
  other Regions, rather than a fixed `row = index // 3, col = index % 3` grid position. Unlike
  `Zone`, a `Region`'s neighbors are not derivable from its index alone — they are an explicit
  part of the generated world's graph (`ADR-0009`), read from generated data rather than computed
  from arithmetic. `Region` still composes exactly one `Screen`, the same relationship `Zone` had.
- **`KeyItem`** *(replaces `Carrot`)* — the item-agnostic generalization **D2** requires: exactly
  one per `Region` (the direct generalization of "exactly one Carrot per Zone"), scarce, feeds a
  renamed running total (`KeyItemCount`, generalizing `CarrotCount`), individually tracked
  (`KeyItemFlags[region]`, generalizing `CarrotFlags[zone]`). `Carrot` becomes **one shipped
  instance** of `KeyItem`'s theming, not the entity's permanent identity — which specific item
  theme a given biome uses is a [GDS-08](08-presentation-architecture.md)/content-authoring
  question, not a domain-model one. `ScoreItem` is unaffected — the abundant tier's structure
  (star/flower, feeding `Score`) does not change under C9/C10.

### New domain rules (generator-guaranteed, per ADR-0009)

- **Exactly one `KeyItem` per `Region`** — generalizes the existing "exactly one Carrot per Zone"
  invariant. Where the shipped rule holds only because `ZONE_COLLECTS` happens to be authored
  that way (no code-level enforcement, per this document's existing "Relationships worth naming
  explicitly" note above), the generated-world version is **structurally guaranteed by the
  generator itself** (ADR-0009) and independently confirmed by a generator-property test across a
  `(seed, scale)` corpus ([R305](../research/encyclopedia/R305-emulator-based-test-design.md)'s
  extension) — a stronger guarantee than the shipped model's, not a weaker one.
- **Grammar-valid adjacency everywhere** *(new — no shipped precedent)* — every generated
  `Region`-to-`Region` edge must appear in
  [R212](../research/encyclopedia/R212-wordless-environmental-storytelling-biome-grammar.md)'s
  adjacency table (e.g. water may border beach, never sky directly). Enforced by construction at
  generation time (ADR-0009), tested as a corpus property (R305's extension).
- **Full reachability** *(new — no shipped precedent needed, since the fixed 3×3 grid is
  trivially fully connected)* — every generated `Region` must be reachable from the start
  `Region` via legal transitions. A real invariant a generator could violate that the fixed
  layout never had to guard against; also a generator-property test target.

**Confirmed, implemented (`IP-9050`, 2026-07-11):** the "generated adjacency edges, read from
generated data rather than computed from arithmetic" property this section describes for
`Region` now also holds for *navigation*, not just generation/rendering — `check_zone_transition`
was found still running the pre-`ADR-0009` fixed-3×3 `Zone` arithmetic (`BL-0047`), silently
capping real gameplay at 9 reachable regions regardless of `WorldScale`. Regeneralized to read
`REGION_GRAPH`'s own neighbor bytes, the same data `dsr_p`/`draw_region_arrows` (`IP-1030`)
already correctly consumed for rendering — completing `ADR-0009`'s Decision point 1 for the last
consumer that hadn't yet moved off the retired fixed-grid model.

### Updated relationship overview (target state)

```
Seed, WorldScale ──parameterize──▶ Region (×WorldScale²) ──composes──▶ Screen (region screen)
                                      │
                                      ├──hosts, per region──▶ Collectible (×N, two subtypes)
                                      │      ├─ ScoreItem  (star | flower)  — abundant, unchanged
                                      │      └─ KeyItem    (exactly 1/region) — scarce, feeds victory
                                      │
                                      ├──has──▶ biome identity (terrain family, GDS-08)
                                      └──has (generated)──▶ adjacency edges to other Regions,
                                                             grammar-valid (R212), fully reachable

KeyItemCount ──accumulates from──▶ KeyItem collection, one per Region (KeyItemFlags[region])

SaveGame ──snapshots──▶ { Player.Position, current Region, KeyItemCount, Score, KeyItemFlags[≤81],
                           Seed, WorldScale }  (ADR-0010; region *content* regenerates from
                                                 Seed+WorldScale, it is not itself persisted)
```

**This delta does not touch `Player`, `Score`, `ScoreItem`, or `GameState`'s core shape** — those
entities and their relationships are unaffected by C9/C10 beyond `GameState` gaining the two new
states [GDS-01](01-concept-of-play.md) §4a already records (MAIN MENU, SEED/SCALE ENTRY).

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-03`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `Claude.md` and `memory.md`'s quick-reference tables (tile index
map, zone/collectible lists) describe the pre-rewrite entity set (3 zones, gifts/stars/flowers,
no Carrot/CarrotFlags concept) and are **not** the source of the entity model above — this level
is sourced directly from `tilemaps.py`/`asm_game.py`, per the same correction discipline applied
throughout this ladder. **Decision: this level supersedes `Claude.md`/`memory.md`'s entity-level
description entirely** (not just superseding, as earlier levels did, an overview paragraph — the
prior quick-reference tables describe entities that no longer exist under those names).
`memory.md`'s *byte-address-level* quick-reference tables (tile index numbers, WRAM addresses)
remain a separate concern for [GDS-07](07-data-model.md) to merge/supersede when it authors the
Data Model level; this level does not touch byte addresses.

**Delta record (2026-07-09):** the "Domain Model delta" section above added, per the adopted
increment plan's Phase 3 and ADR-0009/0010. Delta, not re-authoring — the original
Entity-relationship overview/Entities remain the accurate as-shipped model; no merge-gate box
above is reopened.
