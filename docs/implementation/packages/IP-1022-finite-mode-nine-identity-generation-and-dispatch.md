# IP-1022 — Finite-Mode Nine-Identity Generation & Screen Dispatch

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

**Revision history:** Re-planned 2026-07-17 against [`ADR-0020`](../../architecture/adr/ADR-0020-procedural-screen-fill-for-rom-budget.md)
after a first `08-code-implementation` attempt hit a genuine ~3,358-byte ROM-budget overflow
baking all four new screens' full tile+attr arrays (`BL-0134`). This revision replaces §5–§8/§10–
§11/§13 (Interfaces, Files to Modify, Implementation Tasks, Tests to Add, Definition of Done,
Verification Checklist, Risks); §1–§4/§9/§12/§14 (Package ID, Objective's requirement grounding,
Requirements Covered, Architecture Components, Documentation Updates, Dependencies, Rollback)
carry forward with light edits where the new approach changes a cited detail. Same authorized
scope, same objective (supply the four screens' content and dispatch) — a strategy change, not
new work requiring a fresh G3 ask.

## 1. Package ID

`IP-1022` — implements the 2026-07-16 revision of [**FS-102**](../../features/FS-102-procedural-world-generation.md)
(`FEAT-9000`, Epic `EP-5000`) and [**FS-103**](../../features/FS-103-generated-region-screen-composition.md)
(`FEAT-4100`, Epic `EP-5000`) together, grounded by `FR-4310`/`FR-4320` (`BL-0128`, `CR-08`
resolved 2026-07-16), and by [**`ADR-0020`**](../../architecture/adr/ADR-0020-procedural-screen-fill-for-rom-budget.md)
(runtime procedural screen fill, 2026-07-17) for *how* the four new screens' content is stored and
rendered.

## 2. Objective

Widen `generate_world`'s grammar-constrained biome draw from `[0,4]` to `[0,8]`, extend
`dsr_p`/`dsr_p_dispatch`'s screen-selection cascade to the four newly-folded identities
(Village, Cave, Desert, Plains), and supply their content — **not** by baking each screen's full
576-tile + 576-attr array into ROM (the originally-planned approach, which overflows the ROM
budget by ~3,358 bytes, `BL-0134`), but via a **runtime procedural background-fill routine**
(evaluating the same small modulo formula each screen's Python `*_screen()` function already
uses) plus a **compact landmark-overlay list** per screen, per `ADR-0020`. `IP-1033`'s own staged
`tilemaps.py` collectible-spawn lists (`VILLAGE_COLLECTS`/`CAVE_COLLECTS`/`DESERT_COLLECTS`/
`PLAINS_COLLECTS`, distinct from screen *tile* content) are still spliced into `ZONE_COLLECTS` as
originally planned — `ADR-0020` only changes how the four screens' own background/landmark tiles
are produced, not the collectible-spawn mechanism.

## 3. Requirements Covered

`FR-4310` (grammar-valid adjacency — the nine-value ordering this package's generator clamp and
dispatch cascade both implement), `FR-4320` (nine biome-family identities — the domain/identity
set this package makes concretely reachable in finite-mode play), `FR-4300` (one biome per
screen — unaffected, extended to nine identities by construction, not by new logic). Unchanged
from the original plan — `ADR-0020` changes implementation strategy, not the requirements this
package satisfies.

## 4. Architecture Components

[GDS-08](../../architecture/08-presentation-architecture.md) §4/§8 (terrain-family palette
groups this package's dispatch cascade selects between — no new palette slot, confirmed at `06`)
· [GDS-07](../../architecture/07-data-model.md) §6 (`REGION_GRAPH`'s biome-id byte, already a
full unpacked byte — no data-model change needed for this widening, confirmed at `04`) ·
[**`ADR-0020`**](../../architecture/adr/ADR-0020-procedural-screen-fill-for-rom-budget.md) (this
package is the first implementation of that decision — the procedural-fill-plus-landmark-overlay
technique is introduced here, for these four screens only; the five original screens are
unaffected and keep their existing baked-array format) · `NFR-1400`'s own measured, `NOT MET`
per-frame concern **does not apply** to this package — confirmed by direct code read that
`do_screen_redraw`'s entire dispatch (where this package's new fill routine runs) executes with
the LCD fully disabled (`asm_game.py:1306-1426`), a structurally different context from Infinite
Mode's own `inf_ensure_window` path `NFR-1400` measures.

## 5. Interfaces

- **`REGION_GRAPH`** (`0xC070`+, existing) — no address/format change; the biome-id byte already
  accommodates 0-255, this package only widens the *range of values the generator actually
  produces and the dispatch actually recognizes*.
- **`ALL_SCREENS`'s existing per-`(name, fn)` contract** — **unchanged shape, but the four new
  entries are NOT added here.** Per `ADR-0020`, Village/Cave/Desert/Plains are rendered by the new
  procedural-fill dispatch branches (see §6), not by `build_rom.py`'s existing bake-from-
  `ALL_SCREENS` loop. `ALL_SCREENS` itself keeps exactly its current five biome-family + five UI
  entries — a real, deliberate reduction in this package's own footprint versus the original plan.
- **New: the landmark-overlay data format** (`ADR-0020`'s own new GDS-09 delta) — one list per new
  screen, entries `(tile_x, tile_y, tile_id, attr)`, mirroring `ZONE_COLLECTS`'s own established
  `(x, y, type)` compactness convention (4 bytes/entry: x, y, tile_id, attr — all byte-range
  values, confirmed by direct check: max tile-grid coordinate is `(31,17)`, every `TL_*` constant
  and `attr` value used by these four screens is `<256` and `<8` respectively).
- **New: per-screen fill-formula parameters** — each screen's background pattern is fully
  described by five small constants (row-multiplier, column-multiplier, offset, modulus,
  threshold) plus two tile IDs and one attr value (confirmed by direct read of each Python
  `*_screen()` function, values below) — small enough to inline as immediate operands in each
  screen's own fill routine rather than needing a separate ROM-resident parameter table.
- **The `patches` dict's existing per-family key pattern** (`water_t`/`water_a`, etc.) — **no new
  key pairs for Village/Cave/Desert/Plains** (unlike the original plan) — these four screens have
  no baked tile/attr array address to patch; their dispatch branches call the new fill routine
  directly instead of `_dsr_family`'s existing `memcpy`-from-ROM pattern.
- **`ZONE_COLLECTS`** — unchanged from the original plan: this package performs the final array
  assembly `IP-1033`'s own package deliberately deferred, splicing its four staged, inert lists
  into `ZONE_COLLECTS`'s real array at indices 5-8, and updating `setup_zone_collects`'s consuming
  index range if it assumes exactly 5 entries anywhere (confirm by direct read at implementation
  time — not assumed here).

## 6. Files to Create/Modify

- **Modify: `worldgen.py`** — unchanged from the original plan: `generate()`'s biome-domain
  constants (`worldgen.py:68` `lo, hi = 0, 4` and `worldgen.py:84-85` `if b > 4: b = 4`), both
  ceiling values `4`→`8`.
- **Modify: `asm_game.py`**:
  - **`generate_world`** (`asm_game.py:2087`, confirmed at implementation time — drift check):
    the ceiling-clamp `CP_n(4)` → `CP_n(8)`, unchanged from the original plan.
  - **`dsr_p`/`dsr_p_dispatch`** (`asm_game.py:1392-1411`): extend the `CP_n`/`JR_Z` cascade —
    `CP_n(0..3)`→water/sand/grass/stone (unchanged), **`CP_n(4)`→brick (now explicit — previously
    the unconditional fallthrough target, now one step earlier in the cascade)**, then four new
    comparisons: `CP_n(5)`→village, `CP_n(6)`→cave, `CP_n(7)`→desert, unconditional
    fallthrough→plains (the new final entry, mirroring the cascade's own established "last
    identity reached by fallthrough" convention). Update the stale inline comment at
    `asm_game.py:1397` (currently "biome-id 4... axis-clamped to 0..4") to state the new 0-8
    range and plains as the new fallthrough target.
  - **Four new dispatch-target branches** (`dsr_p_village`/`dsr_p_cave`/`dsr_p_desert`/
    `dsr_p_plains`), each: (a) reads `REGION_GRAPH`'s per-region data as normal, (b) calls the new
    shared **procedural-fill subroutine** (below) parameterized by that screen's own five fill
    constants + two tile IDs + one attr value, (c) calls a shared **landmark-overlay applier**
    subroutine pointed at that screen's own landmark-list address (a new, small `patches` key per
    screen: `village_lm`/`cave_lm`/`desert_lm`/`plains_lm`, resolved the same way `zc_table`'s own
    per-entry pointers are), (d) falls through to `dsr_p_copy`'s existing `POP_HL()`/
    `draw_region_arrows` tail exactly as the five baked-array branches do — **no change to
    anything downstream of the fill+overlay step**.
  - **New: the procedural-fill subroutine.** Computes each tile's value from its own screen's
    formula using **no multiplication** (this codebase's own established constraint, `NFR-2200` —
    `generate_world`'s own `WORLD_SCALE^2` repeated-addition and `gw_mod3`'s own repeated-
    subtraction modulo are the direct, already-proven precedent to mirror). Iterate row-major
    (`y` 0..17, `x` 0..31, skipping row 0's score-bar area exactly as every existing `*_screen()`
    function does); maintain the formula's row/column terms as **running accumulators**
    incremented by each screen's own row-multiplier/column-multiplier constant per step (not
    recomputed from scratch per tile), reduced modulo each screen's own modulus via repeated
    subtraction (mirroring `gw_mod3`'s exact technique), then compared against that screen's own
    threshold to select one of two tile IDs. Cave's own wall rows (`y==1`/`y==17`, currently a
    separate override pass in `cave_screen`) are folded into the *same* fill routine as a
    conditional — a deterministic special case, not a separate landmark, avoiding 64 landmark
    entries this would otherwise cost.
  - **New: the landmark-overlay applier subroutine.** For each of `N` entries at a screen's own
    landmark-list address (`N` read from a 1-byte count prefix, mirroring `ZONE_COLLECTS`'s own
    per-list length-prefix convention seen in `build_rom.py`'s zone-data loop), write
    `(tile_id, attr)` at tilemap position `(tile_x, tile_y)` directly to VRAM — the same
    `0x9800`-relative addressing `copy_screen`/`_put` already use.
- **Modify: `tilemaps.py`**:
  - **No change to `ALL_SCREENS`** (unlike the original plan — see §5).
  - **`ZONE_COLLECTS`**: splice `IP-1033`'s four staged lists into the array at indices 5-8
    (Village, Cave, Desert, Plains, in that `CR-08`-resolved order), removing their "staged, not
    yet spliced" labeling from `IP-1033`'s own package. Unchanged from the original plan.
  - **New: four landmark-overlay lists** (`VILLAGE_LANDMARKS`/`CAVE_LANDMARKS`/
    `DESERT_LANDMARKS`/`PLAINS_LANDMARKS`), each a Python list of `(tile_x, tile_y, tile_id, attr)`
    tuples transcribed directly from the corresponding `*_screen()` function's own landmark-
    placement code (houses/lanterns/fences for Village — 24 entries; crystals/drips/bats for Cave
    — 12 entries, wall rows excluded per above; cacti/bones/pyramids for Desert — 22 entries;
    flowers/tall-grass/butterflies for Plains — 25 entries; 83 entries total, confirmed by direct
    count against each function's own literal loops). **The existing `village_screen`/
    `cave_screen`/`desert_screen`/`plains_screen` Python functions are NOT removed or modified** —
    they remain the oracle-parity source of truth (§8) and continue to exist for `IP-1033`'s own
    already-shipped placement-fairness reasoning to reference; only the fact that they are never
    invoked by `build_rom.py` for these four identities changes.
  - **New: each screen's five fill-formula constants** recorded as a short comment/constant block
    beside its landmark list, transcribed directly from the corresponding `*_screen()` function:
    Village `(mult_y=0, mult_x=0, offset=0, modulus=2, threshold=1, tile_a=TL_COBBLE,
    tile_b=TL_COBBLE_VAR, attr=4)` — a checkerboard, expressible as the same modulo-threshold
    shape with `mult_y=mult_x=1` (since `(x+y)%2` is the formula; the general routine handles the
    `mult=1` case without special-casing it); Cave `(mult_y=13, mult_x=5, offset=7, modulus=18,
    threshold=14, tile_a=TL_CAVE_FLOOR, tile_b=TL_CAVE_BUMP, attr=4, wall_tile=TL_CAVE_WALL)`;
    Desert `(mult_y=19, mult_x=11, offset=9, modulus=17, threshold=12, tile_a=TL_DUNE,
    tile_b=TL_DUNE_BUMP, attr=1)`; Plains `(mult_y=23, mult_x=7, offset=2, modulus=16,
    threshold=11, tile_a=TL_PLAIN_GRASS, tile_b=TL_GRASS_TUFT, attr=0)` — all confirmed by direct
    read of each `*_screen()` function's own `seed = (...)` expression.
- **Modify: `build_rom.py`**: **no new `village_t`/`cave_t`/`desert_t`/`plains_t` patch lines**
  (unlike the original plan) — instead, four new small landmark-list emissions (mirroring the
  existing zone-collectibles loop's own length-prefix + tuple-stream pattern) plus their four
  `patches[...village_lm'...]`-style pointer resolutions.
- **Modify: `test_rom.py`**: `T13.a`'s `FAMILY_RANGES` dict (currently 5 entries, biome-ids 0-4)
  extended with the four new identities' own tile-index ranges (unchanged from the original plan
  — `village_screen`'s `0x90-0x95`, etc., since the *tile IDs themselves* are identical whether
  baked or procedurally computed); `T12.d`'s adjacency-grammar corpus check extended to include
  region graphs that can legally reach biome-ids 5-8; **new: an oracle-parity check** (§8) proving
  the on-device fill+overlay routine's output matches each Python `*_screen()` function's own
  array, tile-for-tile and attr-for-attr, for all four screens.
- **No change** to `check_zone_transition`, `setup_zone_collects`'s own biome-id-indexed lookup
  mechanism, or any Infinite Mode file — confirmed clean by this package's own Supersession sweep
  re-run (see Technical Work Breakdown), unchanged from the original plan.

## 7. Implementation Tasks

Ordered: (1) confirm every cited line number/constant against the current tree by direct re-read;
(2) confirm `IP-1033`'s own four spawn lists exist in `tilemaps.py` (already `VERIFIED`); (3)
widen `worldgen.py`'s clamp bounds; (4) widen `asm_game.py`'s `generate_world` clamp bounds; (5)
extend `dsr_p_dispatch`'s cascade (make brick explicit, add village/cave/desert comparisons,
plains as the new fallthrough), fix the stale inline comment; (6) author the four
`VILLAGE_LANDMARKS`/`CAVE_LANDMARKS`/`DESERT_LANDMARKS`/`PLAINS_LANDMARKS` lists in `tilemaps.py`
by direct transcription from each `*_screen()` function's own landmark-placement code (not
guessed — a transcription error here is exactly what the oracle-parity check in §8 exists to
catch); (7) implement the shared procedural-fill subroutine (no-multiplication, incremental
accumulator + repeated-subtraction modulo, per §6) and the shared landmark-overlay applier; (8)
wire the four new dispatch branches (`dsr_p_village`/`cave`/`desert`/`plains`) to call these two
subroutines with each screen's own parameters/landmark-list pointer; (9) extend `build_rom.py`'s
emission for the four landmark lists + patch resolution; (10) splice `IP-1033`'s content into
`ZONE_COLLECTS` at indices 5-8 (unchanged from the original plan); (11) rebuild the ROM, confirm
the byte-budget recovery (~4,272 bytes estimated before code cost — re-measure exactly); (12) run
the full suite including the new oracle-parity check; (13) documentation/traceability updates
(§9).

## 8. Tests to Add

Landing in the existing **T12: World Generation** / **T13: Screen Composition** suites (no new
suite number — a revision of existing generation/rendering features):

- **T12.d (extended)** — Grammar-validity property test, re-run across a corpus that reaches
  biome-ids 5-8, confirming `|a-b|<=1` holds for every adjacent pair on the full nine-value axis.
- **T13.a (extended)** — Tile-family audit, `FAMILY_RANGES` extended to all nine identities.
- **New: dispatch cascade completeness check** — direct WRAM force (mirroring `T13.a`'s own
  pattern) for each of biome-ids 5-8, confirming the correct screen renders and the correct
  `ZONE_COLLECTS` entry spawns.
- **New: oracle-parity check (the load-bearing new obligation `ADR-0020` requires).** For each of
  the four new screens, render it via the live SM83 fill+overlay routine (direct WRAM force to
  select that biome-id, then a forced redraw, mirroring `T13.a`'s own established methodology),
  read back the full `0x9800`-relative tilemap+attr region PyBoy exposes, and assert it is
  **byte-for-byte identical** to that screen's own Python `*_screen()` function's own returned
  arrays (`tilemaps.village_screen()` etc., called directly from `test_rom.py` exactly as
  `worldgen.generate()` is already called for `T12.b`'s own oracle-parity check) — not a visual
  or sampled comparison, a full per-cell equality check across all `32*18=576` tile cells and 576
  attr cells, for all four screens. This is the check that proves the on-device formula
  transcription and the landmark-list transcription are both exactly correct, not merely
  "close enough."

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-4310`/`FR-4320` Notes → cite this
  package once `VERIFIED`, noting the procedural-fill implementation strategy (`ADR-0020`).
- `docs/requirements/02-non-functional-requirements.md`: `NFR-4000`'s Notes → record the actual
  post-package ROM usage and headroom, and that the four new screens did not require reaching for
  `ADR-0011`'s bank-switching cutover.
- `docs/requirements/04-requirements-traceability-matrix.md`: `FR-4310`/`FR-4320` rows' Module/
  Feature Spec/Implementation Package/Test columns filled.
- `docs/features/FS-102-procedural-world-generation.md`/`FS-103-generated-region-screen-composition.md`
  metadata: implemented-by pointer; `FS-102` §19 Open Question 6 (collectible content) marked
  fully resolved; `FS-103` §19 Open Questions 1-2 marked fully resolved, noting the procedural-fill
  strategy for these four screens specifically.
- `docs/architecture/08-presentation-architecture.md`: note `ADR-0020`'s exception (four screens
  procedurally filled, not baked) the next time GDS-08 is touched — not a blocking obligation of
  this package, since `ADR-0020` itself already records the decision.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Finite-mode `generate_world` produces grammar-valid worlds drawing from the full nine-value
  biome-id domain, for a `(seed, scale)` corpus including cases that reach biome-ids 5-8.
- All nine identities' screens render correctly when their biome-id is reached (confirmed both by
  live generation and direct-force verification).
- **The four new screens' on-device rendering is byte-for-byte identical to their Python
  `*_screen()` functions' own output** — the oracle-parity obligation, not merely "looks right."
- `ZONE_COLLECTS`'s nine-entry array is complete and correctly indexed.
- `worldgen.py`'s oracle remains in lockstep with the SM83 routine across the widened domain.
- No Infinite Mode file touched.
- **ROM builds successfully at exactly 32768 bytes** — the obligation this package's first attempt
  failed; re-confirmed here as a first-class Definition of Done item, not assumed.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct diff: no Infinite Mode file touched.
- [ ] `T12.d`/`T13.a` (both extended) confirmed passing across the full nine-value domain.
- [ ] Dispatch-cascade completeness check confirmed for all four new identities.
- [ ] `worldgen.py`/SM83 lockstep re-confirmed across the widened domain, zero mismatches.
- [ ] `ZONE_COLLECTS`'s nine entries each contain exactly one type-2 entry, confirmed by direct
      count.
- [ ] **Oracle-parity check present and passing for all four new screens** — full 576-tile +
      576-attr byte-for-byte match against each Python `*_screen()` function, not sampled.
- [ ] **No multiplication opcode used in the fill routine** (`NFR-2200`) — confirmed by direct
      code read, incremental-accumulator/repeated-subtraction technique used throughout.
- [ ] **`ALL_SCREENS` confirmed unchanged** (still exactly 5 biome-family + 5 UI entries) — a
      direct, positive confirmation that this package did not silently revert to the
      original bake-everything plan.
- [ ] ROM byte-budget recovery confirmed and recorded exactly (estimated ~4,272 bytes before code
      cost; measure the actual net figure after code is written).

## 12. Dependencies

- **`FR-4310`/`FR-4320`** (baselined, `04-requirements-engineering`) — unchanged.
- **`ADR-0020`** (accepted, `03-architecture-design-synthesis`, 2026-07-17) — the strategy this
  revision implements.
- **`IP-9070`** (`VERIFIED`) — unchanged: the package whose own five-entry `ZONE_COLLECTS`/
  dispatch consolidation this package extends.
- **`IP-1033`** (`VERIFIED`) — its four staged `ZONE_COLLECTS` lists are still spliced in as
  originally planned; `ADR-0020` does not touch `IP-1033`'s own scope or content.
- No other in-flight package's Files to Modify overlap this one's own.

## 13. Risks

**Medium** (was: Medium, for a different reason). The original risk — array-splice-index
correctness — still applies unchanged. **New risk this revision introduces**: on-device
arithmetic must exactly reproduce each Python formula's output, including the no-multiplication
constraint's own repeated-addition/repeated-subtraction technique — a transcription error here
(wrong constant, off-by-one in the modulo reduction, wrong threshold) would silently produce a
*visually plausible but wrong* screen, not a build-time-caught error. **Mitigated by the
oracle-parity check (§8)**, which is a full byte-for-byte comparison against the known-correct
Python source, not a spot check — this is the same class of mitigation `worldgen.py`/
`generate_world`'s own lockstep testing already relies on for exactly this kind of "two
independent implementations of the same algorithm" risk. **This revision is lower-risk than the
original plan's own successor risk (bank-switching) would have been**: no new hardware capability,
no build-pipeline-wide layout change, and the failure mode (a visibly wrong screen) is exactly
what the oracle-parity check is designed to catch before shipping, not a subtler defect.

## 14. Rollback Considerations

Remove the four dispatch branches, the procedural-fill/landmark-overlay subroutines, the four
landmark lists + fill-formula constants from `tilemaps.py`, and `build_rom.py`'s corresponding
emission, then rebuild. No save-format dependency, no `SAVE_VERSION_VAL` bump — `REGION_GRAPH`'s
biome-id byte format is unchanged (still a full byte, wider range of values only). The five
original screens and their existing baked-array format are completely unaffected by this
package's own rollback.
