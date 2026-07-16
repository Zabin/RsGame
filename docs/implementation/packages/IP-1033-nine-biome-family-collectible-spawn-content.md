# IP-1033 — Collectible-Spawn Content for the Four Newly-Folded Biome Identities

> Owned by `07-implementation-planning` (definition) / `08-content-authoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1033` — a delta package against [**FS-103**](../../features/FS-103-generated-region-screen-composition.md)
(`FEAT-4100`, Epic `EP-5000`), grounded by `FR-4320` (nine biome-family identities, `BL-0128`,
baselined 2026-07-16). Resolves `FS-102`'s own Open Question 6 (the collectible-spawn-table gap)
and contributes to `FS-103`'s own Open Question 1 (the render-side half of which is already
resolved — this package closes the paired content-side half named there).

## 2. Objective

Author `ZONE_COLLECTS`-format collectible-spawn lists for the four newly-folded biome identities
(Village, Cave, Desert, Plains) — the four that `IP-9070` deleted (not merely orphaned) when it
consolidated `ZONE_COLLECTS` from nine zone-named lists to five biome-family-representative ones.
Each list mirrors the five existing lists' own format and craft conventions exactly: a mix of
star/flower collectibles (types 0/1) plus exactly one `KeyItem`/treasure entry (type 2), placed
to read fairly against that identity's own already-shipped screen layout.

## 3. Requirements Covered

`FR-3220` (item-agnostic collection mechanic — this package supplies spawn *data* the existing
mechanism consumes, adds no new mechanic), `FR-9130`/`FR-9160` (exactly one `KeyItem` per region —
this package's own type-2 entry is what that guarantee spawns once a region is assigned one of
these four identities), `FR-4320` (the identity set this content completes). Does **not** cover
`FR-4320`'s own array-wiring/dispatch-index assignment — that remains with the deferred package
named in the Technical Work Breakdown (`CR-08`).

## 4. Architecture Components

[GDS-08](../../architecture/08-presentation-architecture.md) §1 (the seeded-sprinkle-plus-
landmarks composition pattern every existing zone screen, including these four, already follows)
— this package's own spawn placement must read fairly against that existing pattern, not
introduce a new one. No ADR governs collectible placement specifically (a content-authoring craft
concern, per `IP-9070`'s own precedent for the five existing lists).

## 5. Interfaces

- **`ZONE_COLLECTS`** (`tilemaps.py`, existing 5-entry list) — this package's own output is four
  new entries in the same `[(pixel_x, pixel_y, type), ...]` format, **appended to the module as a
  clearly-labeled block, not yet spliced into the array's own final index positions** — final
  integration (which index 5-8 each list lands at) is the deferred dispatch package's own job,
  entangled with `CR-08`'s identity-to-position assignment (see §12 Dependencies). This package's
  own Definition of Done is therefore "content authored and staged," not "wired and shipped" —
  stated honestly rather than claimed complete.
- **`setup_zone_collects`** (`asm_game.py`, existing, unchanged by this package) — the consuming
  mechanism this content will eventually be read by, once wired.
- **No new `patches` dict key** for this package's own scope — the eventual wiring package needs
  one (extending `zc_table`'s own existing per-entry pointer pattern), not this content-only step.

## 6. Files to Create/Modify

- **Modify: `tilemaps.py`**: add four new collectible lists, in the exact tuple format the
  existing five use (`(pixel_x, pixel_y, type)`, `type`: 0=star, 1=flower, 2=`KeyItem`/treasure;
  pixel space `x∈[8,151], y∈[24,128]`, per the existing `ZONE_COLLECTS` header comment, confirmed
  unchanged at `tilemaps.py:467`–`470`), staged as a clearly-labeled block immediately after the
  existing five (not yet spliced into the array's own index positions — see §5):
  - **Village** (`village_screen`, `tilemaps.py:155`–`178`): avoid the four houses at
    `(3,2)/(11,2)/(19,2)/(26,2)` (top row) and `(5,14)/(14,14)/(23,14)` (bottom row, tile
    coordinates ×8 for pixel space), the four lanterns at `(1,7)/(1,11)/(29,7)/(29,11)`, and the
    fence segments at `(8,6)/(17,6)/(24,6)/(8,12)/(17,12)/(24,12)` — the cobblestone street tiles
    between these landmarks are the open placement area.
  - **Cave** (`cave_screen`, `tilemaps.py:180`–`202`): avoid the seven crystals, three drips, two
    bats, and the cave-wall rows at `y=1`/`y=17` (tile coordinates) — the cave-floor tiles between
    landmarks are the open placement area.
  - **Desert** (`desert_screen`, `tilemaps.py:204`–`224`): avoid the four two-tile cacti, four
    bone piles, and two pyramids — the dune tiles between landmarks are the open placement area.
  - **Plains** (`plains_screen`, `tilemaps.py:226`–`252`): avoid the 19 hand-placed flowers, three
    tall-grass tufts, and three butterflies — the plain-grass tiles between landmarks are the open
    placement area (the most landmark-dense of the four, per this screen's own existing craft —
    fewer open slots than the other three, name this explicitly if it constrains the collectible
    count/spacing).
  - All four: avoid the player spawn point (pixel `(76, 72)`, per `ZONE_COLLECTS`'s own header
    comment) and stay within the documented pixel bounds; each list gets exactly one type-2 entry
    (mirroring the five existing lists' own "5-6 stars/flowers + exactly one type-2" shape,
    confirmed by direct count of the existing five).
- **No change** to `setup_zone_collects`, `ZONE_COLLECTS`'s own existing five entries, `asm_game.py`,
  or `build_rom.py` — this package is pure data addition, staged not wired (§5).

## 7. Implementation Tasks

Ordered: (1) confirm the four target screens' own current tile layouts by direct re-read (drift
in landmark positions since this package was planned, commit `6f0574b`, is a hard Blocking
condition); (2) author each of the four spawn lists, respecting the avoid-zones named in §6 and
the existing five lists' own craft conventions (collectible spacing, no overlap with each other
within a list, exactly one type-2 entry per list); (3) stage the four lists in `tilemaps.py` as a
labeled block (not yet spliced into `ZONE_COLLECTS`'s own array); (4) rebuild the ROM (the staged
block is inert data — unreferenced by any code path, so this must not change ROM behavior or grow
the build beyond the raw data bytes); (5) verify placement fairness the same way `IP-1031`'s own
verification did — force `REGION_GRAPH`/a direct WRAM poke to render each new screen with its
staged collectible list temporarily wired in for inspection purposes only (mirroring this
project's own established direct-force test pattern, e.g. `T13.a`/this session's own
`content-review-ip-1081-ip-1082.md` methodology) — **not** a permanent wiring, reverted after the
verification screenshot is captured; (6) documentation updates (§9).

## 8. Tests to Add

No new suite or permanent check — this package's own data is inert (unreferenced) until the
deferred wiring package splices it into `ZONE_COLLECTS`'s real array positions, at which point
*that* package's own Tests to Add covers the live-mechanism verification (spawn appears, collects
correctly, increments count). This package's own verification is a one-time, temporary-force
visual/placement-fairness check (§7 task 5) — screenshots as evidence, not a permanent
`test_rom.py` assertion, mirroring `content-review-*`'s own established evidentiary convention
rather than inventing a new temporary-test pattern.

## 9. Documentation Updates

- `docs/features/FS-102-procedural-world-generation.md` §19 Open Question 6: marked partially
  resolved — content authored and staged, final wiring still pending the deferred dispatch
  package (`CR-08`).
- `docs/architecture/07-data-model.md` §8 (tile-index-map cross-reference) or wherever
  `ZONE_COLLECTS`'s own format is documented: no change needed — this package introduces no new
  format, only new data in the existing one.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Four new `ZONE_COLLECTS`-format lists exist in `tilemaps.py`, one per newly-folded identity,
  each respecting its own screen's existing landmark layout and the player-spawn exclusion zone.
- Each list contains exactly one type-2 (`KeyItem`) entry and a fair mix of type-0/1 entries,
  matching the existing five lists' own craft shape.
- A temporary-force visual check (§7 task 5) confirms each list's collectibles render
  correctly-positioned against their screen's real, already-shipped art, with no overlap.
- The ROM's behavior is unchanged (the staged data is inert — confirmed by full suite pass with
  zero new/changed assertions and byte-identical gameplay-affecting code).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes (or documents the new data's own small byte-budget
      addition, per this skill's own ROM-budget-impact rule) with valid header.
- [ ] G5: full `test_rom.py` suite passes, unchanged in every existing assertion (this package's
      own data is inert, so nothing existing should be affected).
- [ ] Direct diff: `setup_zone_collects`, `asm_game.py`, `build_rom.py` byte-for-byte unchanged.
- [ ] Each of the four staged lists inspected against its screen's own landmark layout (§6) —
      confirmed no overlap, confirmed exactly one type-2 entry each, confirmed player-spawn zone
      respected.
- [ ] Temporary-force screenshots captured for each of the four (evidence, not committed as a
      permanent test) confirming visual placement fairness.

## 12. Dependencies

- **`FR-4320`** (baselined, `04-requirements-engineering`) — the identity list and palette
  mapping this content targets.
- **`IP-9070`** (`VERIFIED`) — the package whose own §6 deletion of the original four lists this
  package replaces with freshly-authored content, not a recovery.
- **The deferred dispatch package** (Technical Work Breakdown, "Nine biome-family identities"
  section, blocked on `CR-08`) — required for this package's own staged data to actually splice
  into `ZONE_COLLECTS`'s real array and become live/collectible in shipped gameplay. This
  package's own scope ends at "authored and staged," honestly, not "shipped and collectible."
- No other in-flight package's Files to Modify overlap this one's own (`IP-1105` touches only
  `worldgen.py`/`asm_game.py`'s Infinite Mode labels, disjoint).

## 13. Risks

Low — pure content authoring against already-shipped, unchanging screen art, following an
established five-instance precedent (the existing `ZONE_COLLECTS` entries) for format and craft.
The one risk worth naming: authoring content now that sits unwired until a future package (staged
data can drift from the screen's own art if that screen is ever revised before wiring happens) —
mitigated by this package's own re-verification task (§7 task 1) at implementation time, and by
the fact that none of the four target screens (`village_screen`/`cave_screen`/`desert_screen`/
`plains_screen`) has been touched by any package since the original as-built game shipped,
per this planning pass's own direct-read confirmation.

## 14. Rollback Considerations

Remove the four staged lists from `tilemaps.py`, then rebuild. No save-format dependency, no
wiring to unwind — this package's own data is never referenced by any code path until a future
package splices it in, so rollback is a pure data deletion with zero behavioral consequence.
