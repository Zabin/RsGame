# IP-1030 — Generated-Region Screen Composition (code)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1030` — implements the code half of
[**FS-103**](../../features/FS-103-generated-region-screen-composition.md) (`FEAT-4100`, Epic
EP-5000, Release 2). Content half (biome-family screen-generator registration): **IP-1031**
(paired package, same FS). Jointly resolves FS-103 Open Questions 1–2 (see the
[Technical Work Breakdown](../01-technical-work-breakdown.md)).

## 2. Objective

Generalize the build pipeline's screen-rendering iteration from a fixed 9-entry, per-zone list to
a `WorldScale²`-driven, per-region set — each region rendered via its assigned biome family's
screen-generator function — reusing the existing `copy_screen`/`do_screen_redraw` transition
mechanism unmodified, and retiring `_zone_arrows`'s hardcoded rectangle-boundary math in favor of
reading neighbor validity from `IP-1020`'s generated `REGION_GRAPH`.

## 3. Requirements Covered

FR-4300 (FS-103's Included Requirements, code half); NFR-1300 (transition-timing bar — satisfied
by reuse, not new code).

## 4. Architecture Components

GDS-08 §1 (existing per-screen authoring pattern — unchanged) · GDS-09 delta (`ALL_SCREENS`
extension to per-biome-family iteration) · ADR-0009 point 6 (`_zone_arrows` supersession,
explicitly named there as shipping "once the corresponding package ships" — this package).

## 5. Interfaces

- **`ALL_SCREENS`, extended** (GDS-09 delta, cited verbatim): "one `fn()` per biome family... each
  `fn() -> (tiles, attrs)` still returns the same two-buffer shape; only the caller's iteration
  source changes." This package is the caller-side change: `build_rom.py`'s iteration over
  `ALL_SCREENS` generalizes from "one call per fixed zone name" to "one call per generated
  region, dispatched by that region's biome-id to the matching family function" (IP-1020's
  `REGION_GRAPH` supplies the biome-id per region at generation time on-console; at build time,
  `build_rom.py` lays out one copy of each family's rendered tile/attribute data, since the
  region *count* is a runtime/generation-time fact, not a build-time one — see §6 for the
  resulting build/runtime split).
- **New `patches` dict keys** (GDS-09 delta, cited verbatim: "a patch point for the seed/scale-
  entry screen's tile/attribute addresses... and any generator-data pointers `build_rom.py` lays
  out"): one tile/attribute-address pair per biome family (5 families → 5 pairs), parallel to the
  existing `title_t`/`title_a` pattern — **not** one pair per region (region count varies by
  `WorldScale` at runtime; family count is fixed at 5, a build-time constant).
- **`_zone_arrows`, superseded** (ADR-0009 point 6) — the new region-transition-arrow logic reads
  which of the 4 neighbor-index bytes in `IP-1020`'s per-region `REGION_GRAPH` entry are `0xFF`
  (no neighbor) vs. a valid region index, rather than computing `row = zone // 3, col = zone % 3`
  rectangle-boundary arithmetic.

## 6. Files to Create/Modify

- **Modify: `tilemaps.py`** — the `ALL_SCREENS` list itself: change from 14 fixed `(name, fn)`
  entries to 5 biome-family entries (Water/Sand/Grass/Stone/Brick, per the TWBS's axis
  assignment) + the existing 5 non-zone UI screens (title/intro/save/map/victory — unchanged,
  IP-1040 adds MAIN MENU/SEED-SCALE-ENTRY as two more). Each family entry's `fn()` is IP-1031's
  scope (which existing function is reused per family) — this package only changes the *list
  shape and iteration*, not which function each family maps to.
- **Modify: `build_rom.py`** — the `for name, fn in ALL_SCREENS` loop (existing site, cited in
  GDS-09): lay out one copy of each of the 5 family screens' tile/attribute data (build-time,
  fixed cost — 5 screens' worth of ROM space, same as any 5 of today's 9 zone screens, likely a
  net ROM *reduction* from today's 9-screen layout since 4 fewer distinct screens are laid out).
  Add the 5 new `patches` dict key-pairs (§5) resolved after `build_game_asm()` returns, following
  the exact existing pattern for `title_t`/`title_a` etc.
- **Modify: `asm_game.py`** — the region-entry screen-selection dispatch (a new small routine or
  an extension of `do_screen_redraw`'s existing dispatch): given the current region's biome-id
  (read from `REGION_GRAPH`), select which of the 5 patched tile/attribute address pairs to
  `copy_screen` from — **the `copy_screen`/`do_screen_redraw` call itself is unmodified** (NFR-1300's
  own requirement). Also: retire `_zone_arrows`'s rectangle math, replaced by a read of the
  current region's 4 neighbor-index bytes in `REGION_GRAPH` (0xFF ⇒ no arrow in that direction;
  otherwise ⇒ draw the arrow, matching the existing arrow-tile placement logic unchanged).
- **Modify: `test_rom.py`** — extends **T12** (IP-1020's suite) or adds a small sibling check set
  — a sizing decision left to `08-code-implementation` (this package's own right-sizing call, not
  fixed here), per FS-103 §16's own framing.

## 7. Implementation Tasks

Ordered: (1) `ALL_SCREENS` shape change (5 family entries + existing 5 UI entries); (2)
`build_rom.py`'s layout loop generalization + 5 new `patches` keys; (3) the region-entry
screen-selection dispatch in `asm_game.py` (reading `REGION_GRAPH`'s biome-id, unchanged
`copy_screen` call); (4) `_zone_arrows` retirement, replaced by the `REGION_GRAPH`
neighbor-index read; (5) rebuild ROM; (6) tile-family audit test (AC-1); (7) transition
call-site audit (AC-2, Inspection); (8) full suite run; (9) documentation/traceability updates
(§9).

## 8. Tests to Add

Per FS-103's Verification Plan:

- **Tile-family audit (AC-1):** for every region in the T12 corpus (IP-1020's multi-seed/
  multi-scale corpus, reused here rather than establishing a second one), read the rendered
  screen's tilemap and confirm every tile index falls within its assigned biome family's known
  tile-index range (the existing 8-tile-aligned blocks, `0x70`–`0xB5`, per GDS-07 §8/GDS-08 §9 —
  no new range, since IP-1031 introduces zero new tiles).
- **Transition call-site audit (AC-2, Inspection not Test):** direct code read confirming exactly
  one `copy_screen` call site handles region-entry rendering, with no new/alternate write path —
  mirroring `VR-9020`'s own sweep methodology.

## 9. Documentation Updates

- `docs/architecture/09-interface-specification.md` (GDS-09): confirm the `ALL_SCREENS`
  extension and the 5 new `patches` keys as shipped (the delta's proposal matches).
- `docs/requirements/02-non-functional-requirements.md`: NFR-1300 status → Met.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-4300/NFR-1300 rows → IP-1030.
- `docs/features/FS-103-…md` metadata: implemented-by pointer (code half).
- Master Build Plan status row.

## 10. Definition of Done

- FS-103's two Acceptance Criteria demonstrably pass.
- ROM builds at 32768 bytes (or smaller, per §6's expected net reduction); full suite passes.
- `_zone_arrows`'s rectangle math no longer exists in the tree; the new `REGION_GRAPH`-based
  arrow logic produces identical player-visible arrow behavior for the shipped 3×3-equivalent
  case (`scale=3`, the default) as a regression check.
- No pixel art or palette assignment introduced by this package (IP-1031's scope).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Tile-family audit (AC-1) passes across the full T12 corpus.
- [ ] Transition call-site audit (AC-2) confirms no new/alternate VRAM write path.
- [ ] Direct code read: `_zone_arrows`'s `row = zone // 3, col = zone % 3` arithmetic no longer
      exists; the replacement reads `REGION_GRAPH` neighbor-index bytes.
- [ ] Regression: at `scale=3` with a region layout equivalent to the shipped 3×3 grid, arrow
      placement matches the shipped behavior exactly (a direct comparison, not an assumption).
- [ ] GDS-09/NFR-1300/RQ-04/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1020** (needs a region's biome assignment and `REGION_GRAPH`'s neighbor data to exist
  before either can be consumed) — this tranche's critical-path predecessor.
- **IP-9010, IP-9020, IP-9030, IP-9040, IP-1010** (all `VERIFIED`) — the trustworthy suite and
  the shipped screen-composition pattern this package generalizes.

## 13. Risks

- **Retiring `_zone_arrows` is a deliberate protected-baseline change** (ADR-0009 point 6,
  MSTR-001 C5-style) — mitigated by the exact regression check at §11 (scale=3 behavioral
  parity with the shipped 3×3 grid).
- ROM budget: likely net reduction (5 family screens laid out vs. today's 9 zone screens) — no
  headroom concern; confirmed at build time, not assumed.

## 14. Rollback Considerations

Revert `tilemaps.py`/`build_rom.py`/`asm_game.py`/`test_rom.py` changes and rebuild. `_zone_arrows`
reverts to its shipped rectangle-math form; no save-format dependency on this package (region
rendering is derived at load time from `REGION_GRAPH`, not persisted directly — IP-1050's scope).
