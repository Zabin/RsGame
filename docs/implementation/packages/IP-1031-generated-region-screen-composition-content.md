# IP-1031 — Generated-Region Screen Composition (content)

> Owned by `07-implementation-planning` (definition) / `08-content-authoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1031` — implements the content half of
[**FS-103**](../../features/FS-103-generated-region-screen-composition.md) (`FEAT-4100`, Epic
EP-5000, Release 2). Code half (build-pipeline generalization): **IP-1030** (paired package,
same FS; this package depends on it). This is also the first package `FEAT-6100`'s standard
([FS-106](../../features/FS-106-aesthetic-biome-transition-compliance.md)) applies to, via a
future `09-content-review` pass (not this package's own scope).

## 2. Objective

Register one canonical screen-generator function per biome family (Water/Sand/Grass/Stone/Brick)
against `IP-1030`'s generalized `ALL_SCREENS` shape, reusing five of the nine existing,
already-shipped zone screen functions exactly as authored — **zero new tile art, zero new
palette assignment**.

## 3. Requirements Covered

FR-4300 (FS-103's Included Requirements, content half — the actual "one biome, one screen"
content this package supplies).

## 4. Architecture Components

GDS-08 §1 (existing per-screen authoring pattern, reused unchanged) · GDS-08 §4/GDS-07 §5
(existing terrain-family palette table — the biome-family vocabulary this package's mapping
reuses exactly) · GDS-08 delta §8 (biome-transition palette-stepping strategy — informs *why*
this mapping's axis order, water→sand→grass→stone→brick, was chosen, though judging it is
FS-106's scope, not this package's).

## 5. Interfaces

No new interface — this package populates `IP-1030`'s generalized `ALL_SCREENS` list with
specific `(family_name, fn)` entries, using `fn`s that already exist and already satisfy the
`fn() -> (tiles, attrs)` contract (GDS-09, unchanged).

## 6. Files to Create/Modify

- **Modify: `tilemaps.py`** — the 5 `ALL_SCREENS` family entries `IP-1030` introduces get their
  `fn` values assigned here:
  - **Water** → `lake_screen()` (existing function, unchanged, `tilemaps.py:135`)
  - **Sand** → `beach_screen()` (existing function, unchanged, `tilemaps.py:64`)
  - **Grass** → `forest_screen()` (existing function, unchanged, `tilemaps.py:91`)
  - **Stone** → `mountain_screen()` (existing function, unchanged, `tilemaps.py:111`)
  - **Brick** → `castle_screen()` (existing function, unchanged, `tilemaps.py:267`)

  No modification to any of these five functions' bodies — they are reused verbatim as each
  family's canonical representative. The four remaining shipped zone functions
  (`village_screen()`, `cave_screen()`, `desert_screen()`, `plains_screen()`) are **not** wired
  into this mapping — they become optional future per-family variety (a future
  `08-content-authoring` addition, explicitly out of this package's Definition of Done, per the
  TWBS's own framing).

## 7. Implementation Tasks

Ordered: (1) confirm each of the five chosen functions' current tile-index usage falls
cleanly within its family's existing 8-tile-aligned block (`0x70`–`0xB5`, no cross-family
tile reuse that would break the tile-family audit IP-1030 tests); (2) wire the five
`(family_name, fn)` pairs into `ALL_SCREENS`; (3) rebuild ROM; (4) confirm IP-1030's tile-family
audit (T12/AC-1) passes against this mapping; (5) full suite run; (6) documentation updates (§9).

## 8. Tests to Add

None new — this package is exercised entirely by `IP-1030`'s own tile-family audit (AC-1) and
transition call-site audit (AC-2), since it supplies exactly the data those checks already test
against. Adding a duplicate test here would test the same fact twice.

## 9. Documentation Updates

- `docs/architecture/08-presentation-architecture.md` (GDS-08): confirm the biome-family →
  screen-function mapping as shipped (a short confirming note, not a new delta section — GDS-08
  delta §8 already named the strategy; this is the concrete instantiation).
- `docs/features/FS-103-…md` metadata: implemented-by pointer (content half).
- Master Build Plan status row.

## 10. Definition of Done

- All 5 biome families have exactly one registered screen-generator function.
- IP-1030's tile-family audit (AC-1) passes for every family using this package's mapping.
- Zero new tiles added to `tiles.py`; zero new palette entries added to `build_rom.py`'s
  `BG_PALETTES`/`OBJ_PALETTES` tables (confirmed by diff, not merely asserted).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header (or smaller, per IP-1030's expected
      net reduction).
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct diff: `tiles.py` unchanged by this package (zero new tile art).
- [ ] Direct diff: `build_rom.py`'s `BG_PALETTES`/`OBJ_PALETTES` unchanged by this package (zero
      new palette entries).
- [ ] Each of the five reused functions' tile-index usage confirmed within its own family's
      existing 8-tile-aligned block — no cross-family leakage.
- [ ] GDS-08/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1030** (`ALL_SCREENS`'s 5-family shape must exist before this package can populate it) —
  the direct predecessor in this pairing.
- **IP-1020** (region biome-id assignment must exist for the mapping to be reachable at all).

## 13. Risks

Low — no new pixel art, no new palette work, reuses five already-shipped, already-verified
screen functions verbatim. The only risk this package carries is a tile-index collision if a
reused function's block unexpectedly overlaps another family's (mitigated by §11's direct
per-function audit, not merely assumed clean because the functions are already shipped).

## 14. Rollback Considerations

Revert `tilemaps.py`'s `ALL_SCREENS` entries and rebuild. No save-format dependency; no content
(tile/palette) deletion needed since nothing new was authored.
