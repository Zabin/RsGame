# IP-1020 — Procedural World Generation & Item-Agnostic Collection

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1020` — implements
[**FS-102**](../../features/FS-102-procedural-world-generation.md) (`FEAT-9000`, Epic EP-5000,
Release 2). Resolves FS-102 Open Questions 1–3 and (jointly with IP-1030) FS-103 Open Questions
1–2 — see the [Technical Work Breakdown](../01-technical-work-breakdown.md)'s "Deferred design
decisions resolved in this pass" for the full reasoning; this package states only the resulting
concrete design.

## 2. Objective

Deterministically generate a `WorldScale × WorldScale` region grid from `(Seed, WorldScale)` via
a flood-fill biome assignment that is grammar-legal and fully-reachable **by construction**
(never post-hoc-validated), place exactly one `KeyItem` per region, generalize the collection
mechanic from `Carrot`-specific to item-agnostic, and author the `worldgen.py` build-side
reference-generator oracle in lockstep with the SM83 routine.

## 3. Requirements Covered

FR-9100, FR-9110, FR-9120, FR-9130, FR-4310, FR-3220 (FS-102's full Included-Requirements set);
NFR-2200, NFR-4200.

## 4. Architecture Components

GDS-04 delta (`Seed`/`WorldScale`/`Region`/`KeyItem` entities, generator-guaranteed domain rules)
· GDS-07 delta §6/§7 (proposed WRAM layout — this package confirms/finalizes it) · GDS-08 delta
§8 (biome-family palette-stepping strategy — informs the family axis order below) · GDS-09 delta
(`worldgen.py` contract, `ALL_SCREENS`/patch-point extensions — the `ALL_SCREENS` half is
IP-1030's scope, not this package's) · ADR-0009 (screen/room-graph generation, on-console,
grammar-by-construction) · ADR-0010 (seed/scale model) · R111 (xorshift PRNG) · R305 (reference-
generator-oracle testing pattern).

## 5. Interfaces

- **New module `worldgen.py`** (GDS-09 delta): `generate(seed: int, scale: int) -> RegionGraph`,
  where `RegionGraph` exposes `regions: list[{biome_id, neighbors}]` (a Python list mirroring
  `REGION_GRAPH`'s byte layout field-for-field) and a `key_item_region_index`-equivalent (trivial
  here, since every region gets exactly one `KeyItem` — this field is really just "all regions,"
  kept for contract-shape parity with GDS-09's own naming). **Imported only by `test_rom.py`** —
  `build_rom.py`/`asm_game.py` never import it (GDS-09 delta, explicit).
- **No new `patches` dict key.** OQ3 resolved (see TWBS): the grammar check is inline arithmetic
  (`|axis_a − axis_b| ≤ 1`), not ROM-resident table data — no patch point needed for it. (IP-1030
  may still add its own patch-point keys for the region-screen-entry mechanism; that is IP-1030's
  concern, not this package's.)
- **`check_collisions`/`setup_zone_collects`** (existing `asm_game.py` labels) — extended in
  place, not replaced; same calling contract.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - WRAM constants block (after the existing `SCOREITEM_FLAGS = 0xC060` line): add `SEED =
    0xC069` (2 bytes, `C069`–`C06A`), `WORLD_SCALE = 0xC06B` (1 byte), `REGION_GRAPH = 0xC070`
    (5 bytes/region: 1 biome-id byte + 4 neighbor-region-index bytes, `0xFF` = no neighbor in
    that direction, up to 81 regions = 405 bytes worst case), `KEYITEM_FLAGS` at the next
    8-aligned address after `REGION_GRAPH`'s worst-case extent (`0xC070 + 405` rounded up to the
    next multiple of 8 = `0xC220`; up to 81 bytes). All four addresses fall inside the existing
    boot-time WRAM clear (`0xC000`–`0xC2FF`, `asm_game.py:93`) — the all-zero fresh-boot state is
    free, exactly as `SCOREITEM_FLAGS` already gets it.
  - **New routine `generate_world`** (new label, called from the SEED/SCALE ENTRY confirm action
    — the call site itself is IP-1040's scope; this package only authors the routine): seeds a
    16-bit xorshift PRNG from `SEED` (0 normalized to 1 first); assigns region 0's biome-id = 2
    (Grass); visits every other region index 1…`scale²−1` in row-major order, each region's
    biome-id = an already-visited grid-adjacent neighbor's biome-id (prefer the row-major
    predecessor: left neighbor if col > 0, else top neighbor) plus a PRNG-drawn delta in
    `{-1, 0, +1}` clamped to `[0, 4]`; fills all 4 neighbor-index bytes per region with the
    grid-adjacent region's index or `0xFF` at grid boundaries (`row = idx // scale, col = idx %
    scale`, generalizing `CUR_ZONE`'s existing `row = zone // 3, col = zone % 3` arithmetic);
    sets exactly one `KeyItem` flag-slot per region (trivial — every region gets one, per
    FR-9130).
  - **`check_collisions`'s carrot branch** (existing label, `cc_not_c`'s sibling branch handling
    `type==2`): generalize the WRAM constant referenced from `CARROT_FLAGS`/`CARROTS_COUNT` to
    `KEYITEM_FLAGS`/`KEYITEM_COUNT` — **same bit-set logic, same push/pop-HL discipline**, only
    the target array/counter names change (a rename-in-place, not new logic). `CARROTS_COUNT`'s
    WRAM slot is reused as `KeyItemCount`'s slot (GDS-04 delta: "renamed running total... same
    WRAM slot, behaviorally identical increment logic").
  - **`setup_zone_collects`'s carrot check** (existing label): same generalization — test
    `KEYITEM_FLAGS[current region]` instead of `CARROT_FLAGS[CUR_ZONE]`; identical logic
    otherwise.
- **New file: `worldgen.py`** — the Python reference-generator oracle, `generate(seed, scale) ->
  RegionGraph`, reimplementing the exact algorithm above (same PRNG step order, same neighbor-
  delta rule, same row-major visitation order) — kept in lockstep with the SM83 routine by direct
  correspondence, not shared code (GDS-09 delta).
- **Modify: `test_rom.py`** — add suite **T12** (see §8).

## 7. Implementation Tasks

Ordered: (1) WRAM constants; (2) `generate_world` routine (PRNG step, flood-fill biome
assignment, neighbor-index fill, `KeyItem` placement); (3) `check_collisions`/
`setup_zone_collects` generalization (`CARROT_FLAGS`→`KEYITEM_FLAGS`, `CARROTS_COUNT`→
`KeyItemCount`, same slot); (4) `worldgen.py` oracle, written against task 2's exact step order;
(5) rebuild ROM; (6) author T12; (7) full suite run; (8) documentation/traceability updates (§9).
Tasks 2 and 4 must be authored together, cross-checked line-by-line against each other before
task 6 — the oracle-vs-SM83 lockstep is this package's single most load-bearing correctness
property (FS-102 §14).

## 8. Tests to Add

New `test_rom.py` suite **`T12: World Generation`**, implementing FS-102's Verification Plan
against a fixed multi-seed/multi-scale corpus (R305's extension — at minimum `scale ∈ {2, 3, 9}`,
seeds including `0`):

- T12.a — **determinism**: boot twice with the same `(seed, scale)` (fresh `PyBoy` instance each
  time, R305's two-instance pattern), assert byte-identical `REGION_GRAPH`/`KEYITEM_FLAGS` WRAM
  both times (AC-2).
- T12.b — **oracle parity**: for every corpus `(seed, scale)`, compare `worldgen.py`'s computed
  `RegionGraph` against the SM83 routine's actual WRAM output — byte-for-byte match (proves the
  lockstep the whole suite's future determinism assertions depend on).
- T12.c — **reachability**: graph-traversal from region 0 over the generated `REGION_GRAPH`
  visits every region (AC-3) — for every corpus entry.
- T12.d — **grammar-validity**: for every generated adjacency edge, assert `|biome_a − biome_b|
  ≤ 1` (AC-4) — for every corpus entry; this also documents the concrete grammar table this
  package defines (§ below).
- T12.e — **one-KeyItem-per-region**: count check across every region in the corpus (AC-5).
- T12.f — **seed=0 normalization**: assert the PRNG's internal state is never 0 when the
  player-entered seed is 0 (a direct WRAM/register-state inspection, not an output-based test).
- T12.g — **item-agnostic collection**: extends T8's existing carrot-collection checks,
  retargeted to `KEYITEM_FLAGS`/`KeyItemCount` — confirms the generalization preserves the exact
  shipped behavior (AC-6).
- T12.h — **static determinism audit** (AC-7, Inspection not Test): a direct code read confirming
  `generate_world` reads no `DIV` register and no WRAM address outside `SEED`/`WORLD_SCALE`/its
  own prior output.
- T12.i — **headroom audit** (AC-8, Inspection not Test): confirm `REGION_GRAPH`+`KEYITEM_FLAGS`'
  worst-case extent (`0xC070`–`0xC26F`, 512 bytes) stays inside bank-0 (`0xC000`–`0xCFFF`).

## 9. Documentation Updates

- `docs/architecture/07-data-model.md` (GDS-07): finalize the delta's proposed WRAM addresses as
  confirmed (`SEED`/`WORLD_SCALE`/`REGION_GRAPH`/`KEYITEM_FLAGS` at the addresses §6 states).
- `docs/architecture/09-interface-specification.md` (GDS-09): confirm `worldgen.py`'s contract as
  shipped (the proposed signature matches exactly, no change needed beyond a "confirmed" note).
- `docs/requirements/02-non-functional-requirements.md`: NFR-2200/NFR-4200 status → Met.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-9100/9110/9120/9130/4310/3220,
  NFR-2200/4200 rows → IP-1020/T12.
- `docs/features/FS-102-…md` metadata: implemented-by pointer.
- Master Build Plan status row.

## 10. Definition of Done

- All eight FS-102 Acceptance Criteria demonstrably pass via T12.
- ROM builds at 32768 bytes; full suite passes headless.
- `worldgen.py` and the SM83 routine produce byte-identical output for the full test corpus
  (T12.b) — the lockstep property is proven, not assumed.
- No new `patches` dict key; `ALL_SCREENS`/`ZONE_COLLECTS` untouched (IP-1030's scope).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes (T1–T12).
- [ ] T12.a–i each present and passing (map 1:1 to FS-102 AC-1…8, plus the oracle-parity check).
- [ ] Direct code read: `generate_world` reads no `DIV`/uninitialized WRAM.
- [ ] Direct code read: `KEYITEM_FLAGS`/`KeyItemCount` generalization reuses the exact bit-set/
      push-pop discipline the carrot branch already established — no new pattern invented.
- [ ] `worldgen.py`'s PRNG step order and neighbor-delta rule match `generate_world`'s, confirmed
      by direct side-by-side read, not only by T12.b's output match.
- [ ] BL-0019/NFR-4200 rider: WRAM headroom re-affirmed at `scale=9` (worst case 512 bytes new
      WRAM against ~3.1 KiB confirmed bank-0 headroom).
- [ ] GDS-07/GDS-09/NFR-2200/NFR-4200/RQ-04/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-9010, IP-9020, IP-9030, IP-9040, IP-1010** (all `VERIFIED`) — this package builds on the
  trustworthy suite and the shipped `CARROT_FLAGS`/`check_collisions`/`setup_zone_collects`
  pattern it generalizes.
- No other package in this tranche is a prerequisite — IP-1020 is this tranche's own foundational
  node (per FP-04/TWBS).

## 13. Risks

- **Genuinely new algorithmic work with no shipped precedent** (Medium-High, carried from
  FEAT-9000's own catalog assessment) — mitigated by choosing the simplest algorithm satisfying
  all four invariants by construction (no backtracking, no contradiction risk) rather than a more
  general but riskier constraint-solving approach.
- **Oracle/SM83 lockstep drift** — if `worldgen.py` and the SM83 routine diverge, T12's
  determinism/reachability/grammar-validity assertions could pass against a wrong oracle while
  the shipped generator is actually broken. Mitigated by T12.b's explicit byte-for-byte parity
  check (not just internal consistency of each side alone) and by authoring both together (§7).
- ROM budget: a new code-only routine (`generate_world`), no precomputed map data — per ADR-0009's
  own framing, expected to be a net ROM *saving* relative to nine hand-authored screens it
  eventually lets `_zone_arrows`' hardcoded rectangle math retire (that retirement is IP-1030's
  scope, not this package's). WRAM growth: up to 512 bytes worst case at `scale=9` (re-affirmed
  at §11).

## 14. Rollback Considerations

Revert `asm_game.py`/`worldgen.py` (new file, safe to delete)/`test_rom.py` and rebuild. No save-
format change in this package (that's IP-1050's scope) — no save-compatibility concern from a
rollback of this package alone.
