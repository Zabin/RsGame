# VR-1033 — Collectible-Spawn Content for the Four Newly-Folded Biome Identities

> Verification Report for
> [IP-1033](../packages/IP-1033-nine-biome-family-collectible-spawn-content.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-1033-nine-biome-family-collectible-spawn-content.md)

## Package

- **ID / Title:** IP-1033 — Collectible-Spawn Content for the Four Newly-Folded Biome Identities
  (Village/Cave/Desert/Plains, `FR-4320`/`BL-0128`, delta against `FS-103`)
- **Commit verified:** `e5cbab1` ("content(IP-1033): nine-biome-family collectible-spawn content"),
  tree head `5dca066`.
- **Date:** 2026-07-17
- **Independence:** clean — implemented in a prior session (2026-07-16); this session's only
  prior action was invoking `09-package-verification` itself.

## Result

**RETURNED** — 1 failed Definition-of-Done / Verification-Checklist item. Direct arithmetic
re-derivation of every staged collectible's pixel position against its screen's own landmark
placements (both computed straight from source, not from a screenshot) shows **3 of the 4 staged
lists place a collectible on the exact same tile as an existing landmark** — the placement-
fairness claim ("no overlap") the package's own Definition of Done and Verification Checklist
require is false as shipped. Every other checked item passes: ROM builds correctly, the full
suite is unchanged, the diff stayed in scope, type-2 counts are correct, and the player-spawn zone
is respected.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | Four new `ZONE_COLLECTS`-format lists exist, one per newly-folded identity, each respecting its own screen's existing landmark layout and the player-spawn exclusion zone | `tilemaps.py:506-541` — `VILLAGE_COLLECTS`/`CAVE_COLLECTS`/`DESERT_COLLECTS`/`PLAINS_COLLECTS`, four lists present, correct `(pixel_x, pixel_y, type)` format. Landmark respect: see Finding 1 below — **3 of 4 lists fail this** | ❌ |
| 2 | Each list contains exactly one type-2 (`KeyItem`) entry and a fair mix of type-0/1 entries | Direct count: Village 5+1, Cave 5+1, Desert 5+1, Plains 5+1 — all four correct | ✅ |
| 3 | A temporary-force visual check confirms each list's collectibles render correctly-positioned against their screen's real, already-shipped art, with no overlap | Package/commit claims "no overlap" for all four (`00-master-build-plan.md:826`: "placement verified visually via a temporary-force render (all four screenshots, no overlap)"). **This claim is false** — see Finding 1 | ❌ |
| 4 | The ROM's behavior is unchanged (staged data inert, confirmed by full suite pass with zero new/changed assertions and byte-identical gameplay-affecting code) | Rebuilt ROM: 31362/32768 bytes (matches package's claimed post-`IP-1110` baseline exactly — see Test run below). `test_rom.py`: 309/309, 0 failed, no new suites added by this package. `git show e5cbab1 --stat`: only `tilemaps.py` + docs touched, no `asm_game.py`/`build_rom.py` change | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | `python3 build_rom.py` → "Wrote 32768 bytes"; header emitted by the same `set_header()` path used by every prior VERIFIED package | ✅ |
| 2 | G5: full `test_rom.py` suite passes, unchanged in every existing assertion | `python3 test_rom.py` → **309/309 passed, 0 failed** (matches the count recorded for `IP-1105`/`IP-1110`, both already-shipped siblings — this package added no suite) | ✅ |
| 3 | Direct diff: `setup_zone_collects`, `asm_game.py`, `build_rom.py` byte-for-byte unchanged | `git show e5cbab1 --stat` → only `tilemaps.py`, `ROADMAP.md`, `docs/features/FS-102-*.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, `memory.md` changed. No `asm_game.py`/`build_rom.py` lines touched | ✅ |
| 4 | Each of the four staged lists inspected against its screen's own landmark layout — confirmed no overlap, confirmed exactly one type-2 entry each, confirmed player-spawn zone respected | Type-2 count and spawn-zone clearance both hold (see DoD #2 and Finding 2 below). **Overlap does not hold** — 4 of the 24 staged entries (across 3 of 4 lists) sit on the exact same tile as an already-placed landmark, computed directly from `tilemaps.py`'s own tile-grid arithmetic. See Finding 1 | ❌ |
| 5 | Temporary-force screenshots captured for each of the four confirming visual placement fairness | Per §8, screenshots are evidence-only, not committed to the repo — none exist to independently re-inspect. The commit message and Master Build Plan both assert "no overlap" for all four; direct arithmetic re-derivation contradicts that assertion for three of the four (Finding 1). Whatever was screenshotted, the placement itself is objectively wrong at the coordinates named below | ❌ |

## Findings

### Finding 1 (High) — 3 of 4 staged collectible lists place an entry on the exact same tile as an existing landmark

`tilemaps.py` renders all screens on a `W=32 × H=18` tile grid (`tilemaps.py:13`), and `_put(tiles,
attrs, x, y, ...)` (`tilemaps.py:18-21`) writes to tile-grid coordinates `(x, y)`. `ZONE_COLLECTS`'s
own header comment (`tilemaps.py:467-470`) and this package's own §6 both establish that a staged
collectible's `(pixel_x, pixel_y)` corresponds to tile-grid position `(pixel_x/8, pixel_y/8)` — the
same convention the package's own §6 avoid-lists use ("tile coordinates ×8 for pixel space"). Cross-
referencing every staged entry's tile position against every landmark `_put` call in the same
screen function finds three exact collisions:

- **Village** — `VILLAGE_COLLECTS`'s type-2 (`KeyItem`) entry, `(136, 96, 2)` (`tilemaps.py:511`,
  tile `(17, 12)`), lands on the exact fence tile placed by `village_screen`'s
  `for fx in (8, 17, 24): ... _put(t, a, fx, 12, TL_FENCE, 1)` (`tilemaps.py:175-177`, `fx=17` →
  tile `(17, 12)`). This is precisely one of the six fence positions the package's own §6 explicitly
  names as an avoid-zone ("fence segments at ... `(17,12)`").
- **Desert** — `DESERT_COLLECTS`'s second entry, `(32, 96, 1)` (`tilemaps.py:526`, tile `(4, 12)`),
  lands on the exact cactus tile placed by `desert_screen`'s
  `for cx in (4, 12, 19, 27): ... _put(t, a, cx, 12, TL_CACTUS_TOP, 6)` (`tilemaps.py:214-218`,
  `cx=4` → tile `(4, 12)`) — one of the four two-tile cacti the package's own §6 names as an
  avoid-zone.
- **Plains** — `PLAINS_COLLECTS`'s first two entries both land on hand-placed flowers:
  `(24, 32, 1)` (`tilemaps.py:538`, tile `(3, 4)`) exactly matches
  `(3, 4, TL_FLOWER_RED, 5)` (`tilemaps.py:237`); `(24, 96, 0)` (`tilemaps.py:539`, tile `(3, 12)`)
  exactly matches `(3, 12, TL_FLOWER_YEL, 2)` (`tilemaps.py:241`). Both are inside the "19
  hand-placed flowers" the package's own §6 names as Plains' avoid-zone.

Only `CAVE_COLLECTS` is clean — every one of its six entries lands on a tile at least 3 tile-widths
(24px) from the nearest crystal/drip/bat, matching the spacing precedent set by the five
already-shipped `ZONE_COLLECTS` entries (spot-checked against `lake_screen`'s own shipped list,
which has zero exact-tile collisions with its own landmarks, confirming the arithmetic method
against a known-good baseline).

This contradicts the package's own Definition of Done item 3, Verification Checklist item 4, and
the Master Build Plan's recorded claim ("placement verified visually via a temporary-force render
(all four screenshots, no overlap)"). Whatever the temporary-force render actually showed, the
underlying coordinates are objectively wrong at the four points named above — this is not a
judgment call, it is the same tile-grid arithmetic the package's own avoid-lists in §6 already use.

**Severity:** High — this is exactly the placement-fairness property this content-only package
exists to deliver; a KeyItem sprite rendered on top of a fence tile, or a star/flower sprite on top
of a cactus/flower tile, is a visible craft defect once `IP-1022` wires this data live, and shipping
it silently would surface as a player-facing bug in the next release rather than being caught here.

**Recommended owner:** `08-content-authoring`, re-run against `IP-1033` — reposition the four named
entries (Village's type-2 entry, Desert's second entry, Plains' first two entries) off the
landmark tiles named above, respecting the same avoid-list §6 already documents, then re-verify.

### Finding 2 (Informational) — player-spawn exclusion and type-2 counts are correct, no re-work needed

Confirmed directly: no staged entry across all four lists falls within a landmark-comparable
distance of the player-spawn point `(76, 72)` named in `ZONE_COLLECTS`'s header comment, and each
of the four lists carries exactly one type-2 entry as required. These two DoD/checklist items pass
cleanly and don't need to be revisited when `08-content-authoring` fixes Finding 1.

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| `FR-3220` (item-agnostic collection mechanic) | Not touched by this package (pre-existing mechanism, correctly unmodified per §5/§6) | N/A — no new mechanic | Unaffected | ✅ (out of this package's scope, correctly so) |
| `FR-9130`/`FR-9160` (exactly one `KeyItem` per region) | Each staged list carries exactly one type-2 entry — confirmed by direct count | Not yet live (data inert until `IP-1022` splices it in, per package's own §5) | Correctly `UNASSIGNED`/pending wiring — no premature claim in the RTM | ✅ |
| `FR-4320` (nine biome-family identity set) | This package supplies 4 of the identity set's own content; correct per its own scope | Same as above — pending `IP-1022` | Correctly pending | ✅ |

No RTM correction needed — the package correctly left forward columns unassigned rather than
claiming premature completion.

## Scope audit

`git show e5cbab1 --stat`: `tilemaps.py` (+49 lines, the four staged lists) plus five documentation/
ledger files (`ROADMAP.md`, `FS-102`, Master Build Plan, `packages/INDEX.md`, `memory.md`). No
excursion outside the package's declared file set (§6: "Modify: `tilemaps.py`" only, "No change" to
`setup_zone_collects`/`asm_game.py`/`build_rom.py` — confirmed).

## Test run

- `python3 build_rom.py` → 32768 bytes written, valid header (same build path every prior
  `VERIFIED` package uses).
- `python3 test_rom.py` → **309/309 passed, 0 failed** (fresh install of `pyboy`/`Pillow` in this
  session's container; matches the count both sibling packages `IP-1105`/`IP-1110` already
  recorded — this package adds no new suite, consistent with §8's "no new suite" statement).
- ROM size: 31362/32768 bytes, matching the tree's current state after `IP-1105`/`IP-1110` already
  landed (this package's own staged data is inert bytes with negligible/zero footprint change, as
  claimed).

No tunable/generated parameter applies to this package's own DoD (it stages static data, not a
runtime-configurable parameter), so the tunable-parameter re-drive rule does not add an additional
obligation here — the overlap check above is itself the parameter this package's own DoD cares
about, and it was driven directly against the real, current screen-layout source, not a fixture.

## Recommendations

1. **High** (Finding 1) — route back to `08-content-authoring`: reposition `VILLAGE_COLLECTS`'s
   type-2 entry (currently `(136, 96, 2)`), `DESERT_COLLECTS`'s second entry (currently
   `(32, 96, 1)`), and `PLAINS_COLLECTS`'s first two entries (currently `(24, 32, 1)` and
   `(24, 96, 0)`) off the landmark tiles named above, then re-run this verification.
2. Informational (Finding 2) — no action needed; carries forward cleanly once Finding 1 is fixed.

## Next step

**`08-content-authoring` re-run on `IP-1033`** against Finding 1 — the package stays `COMPLETE`
until the four named coordinates are repositioned and this verification is re-run. `IP-1105` and
`IP-1110` are unaffected (disjoint files) and remain independently eligible for their own
`09-package-verification` passes in this same session (each is a different package, so the
same-session-independence rule applies per-package, not per-run — see the pipeline manager's own
disposition of this batch).
