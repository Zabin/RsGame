# GDS-04 — Domain Model

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-03](03-architecture.md); the next level,
> [GDS-05 Functional Requirements](05-functional-requirements.md), builds on this one.

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
- **SaveGame is a strict subset of live game state** — `Player.Direction`/`AnimationFrame`, and
  all `ScoreItem` positions/consumed-state per zone, are **not** persisted. A reloaded zone's
  score items are implicitly reset to "all present" (not tracked as collected/not, unlike
  Carrots) — confirmed by the save routine's field list omitting any per-zone score-item state.
  This is a real, as-built design choice (only the scarce tier's collection state persists) worth
  stating plainly rather than leaving implicit.

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
