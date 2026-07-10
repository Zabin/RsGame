# Feature Specifications — Index

Owned by `06-feature-specification` (sole write scope). One `FS-xxx-<slug>.md` per approved
Feature, numbered `FS-101` upward, each expanding a `FEAT-xxxx` catalog row from
`docs/feature-planning/03-feature-catalog.md` via the fixed 20-field template. Record the
FEAT↔FS mapping in both directions.

[↑ Docs index](../INDEX.md)

| FS ID | Title | FEAT source | Epic | Status | One-line summary |
|---|---|---|---|---|---|
| [FS-101](FS-101-per-zone-scoreitem-persistence.md) | Per-Zone ScoreItem Persistence | FEAT-5100 | EP-3000 | ✅ Specified (2026-07-07); shipped/VERIFIED 2026-07-07 | Extends the save system to persist which stars/flowers have been collected per zone, plus fixes a confirmed same-session respawn behavior as a side effect. |
| [FS-102](FS-102-procedural-world-generation.md) | Procedural World Generation & Item-Agnostic Collection | FEAT-9000 | EP-5000 | ✅ Specified (2026-07-10) — not yet implemented | Deterministic region-graph generation from `(seed, scale)` with grammar-valid adjacency, full reachability, and exactly one item-agnostic KeyItem per region; 3 Open Questions (grammar table contents, algorithm detail, ROM-pointer need) all routed to `07-implementation-planning`. |
| [FS-103](FS-103-generated-region-screen-composition.md) | Generated-Region Screen Composition | FEAT-4100 | EP-5000 | ✅ Specified (2026-07-10) — not yet implemented | Renders each generated region from exactly one biome family's tiles within the existing LCD-off transition budget; 2 Open Questions (biome-family content completeness, tile-index/palette sizing) routed to `07-implementation-planning`, in lockstep with FS-102's grammar-table question. |
| [FS-104](FS-104-main-menu-new-game-flow.md) | Main Menu & New-Game Flow | FEAT-1100 | EP-1000 | ✅ Specified (2026-07-10) — not yet implemented | Mandatory MAIN MENU on every boot, SEED/SCALE ENTRY triggering world generation, and SAVE's new exit-to-main-menu auto-save option; retires the shipped auto-load bypass. 2 Open Questions (SEED/SCALE ENTRY cancel path, menu input mapping) routed to `07-implementation-planning`. |
| [FS-105](FS-105-generated-world-save-persistence.md) | Generated-World Save Persistence | FEAT-5300 | EP-3000 | ✅ Specified (2026-07-10) — not yet implemented | Extends the save system to persist seed/scale/per-region KeyItemFlags and regenerate (not persist) the region graph on load; a pre-upgrade save is never offered on "continue." No Open Questions — fully determined by ADR-0010/GDS-07's delta. |
