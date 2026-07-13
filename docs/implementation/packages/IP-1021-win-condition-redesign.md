# IP-1021 — Win-Condition Redesign (Dead-End-Anchored Treasure Placement)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1021` — implements the 2026-07-12 revision of
[**FS-102**](../../features/FS-102-procedural-world-generation.md) (`FEAT-9000`, Epic `EP-5000`)
grounded by [**ADR-0015**](../../architecture/adr/ADR-0015-dead-end-anchored-treasure-and-win-condition.md)
(`BL-0093`, project-owner direct decision). Resolves `FS-102`'s own Open Question 5 (the
per-region tri-state encoding, see §6 below); Open Question 4 (the `FEAT-9000` catalog entry's
own stale `FR-9130` citation) is **not** resolved by this package — it is a `05-feature-
decomposition` bookkeeping item, out of this skill's own write scope.

## 2. Objective

Replace `generate_world`'s universal "one `KeyItem` per region" placement with a selective
`WORLD_SCALE`-total placement prioritizing the pre-braid spanning tree's own dead-end (leaf)
regions, and replace `check_complete`'s hardcoded `CARROTS_COUNT == 9` victory check with a
runtime `KeyItemCount == WORLD_SCALE` comparison — the exact pair `FR-9160`/`FR-9161` require.

## 3. Requirements Covered

FR-9160 (scale-relative, dead-end-prioritized `KeyItem` placement — supersedes `FR-9130`),
FR-9161 (scale-relative victory condition — supersedes `FR-3300`).

## 4. Architecture Components

[ADR-0015](../../architecture/adr/ADR-0015-dead-end-anchored-treasure-and-win-condition.md) (the
binding decision this package implements) · [ADR-0012](../../architecture/adr/ADR-0012-maze-shaped-region-adjacency.md)
point 3 (the spanning-tree carve whose `GW_MAZE_STATE` this package's new pass reads) ·
[GDS-07](../../architecture/07-data-model.md) §7b (`GW_MAZE_STATE`'s exact bit layout) / §7c (the
per-region tri-state concept this package's §6 resolves against real code).

## 5. Interfaces

- **`GW_MAZE_STATE`** (`0xC3A0`–`0xC3F0`, `IP-1070`) — read-only, this package's own new pass
  reads each region's `bit 7` (visited) and `bits 1:0` (parent-direction) to compute leaf status.
  Not written by this package.
- **`REGION_GRAPH`'s existing neighbor-byte layout** (unchanged) — read-only, via the existing
  `gw_neighbor_hl` subroutine (`IP-1070`), reused as-is (no new addressing helper needed — this
  package's own leaf test is structurally the same "is this grid-adjacent neighbor my tree child"
  test `maze_prune_dir`'s own "Check 1" already performs, `asm_game.py:1586-1591`, reused for a
  classification purpose instead of an edge-pruning one).
- **`WORLD_SCALE`** (`0xC06B`, existing) — read by both the new placement pass (target count) and
  the revised `check_complete` (victory threshold).
- **`KEYITEM_FLAGS`** (`0xC220`–`0xC270`, existing, up to 81 bytes) — **value domain widened**
  in place (§6); no new address, no new patch-point key.
- **No new `patches` dict key** — this package is pure WRAM-read/-write logic inside an
  already-patched routine (`generate_world`) plus a one-operand change in an existing routine
  (`check_complete`); no new ROM-resident data table.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`generate_world`** (existing label, spans the biome-assignment pass through the maze pass):
    insert a new placement pass **between `maze_carve_done`'s own tree-completion point
    (`asm_game.py:1571-1572`, immediately after the `GW_BRAID_IDX` repurpose-zero and before
    `maze_prune_region`'s own label) and the start of the braid pass**. This ordering is load-
    bearing: leaf status must be snapshotted from the finished spanning tree *before* the braid
    pass reopens any edges (braiding can turn a former leaf into a non-leaf by giving it a second
    open neighbor). The new pass:
    1. **Leaf classification, one full region sweep:** for every region `R` (0 to `WORLD_SCALE²
       - 1`), test each of its up to 4 grid-adjacent neighbors `V` (via `REGION_GRAPH`, same
       access `gw_neighbor_hl` already provides): if `V` exists and `V`'s own `GW_MAZE_STATE`
       parent-direction equals the direction from `V` back to `R` (i.e. `V` is `R`'s spanning-tree
       child — the identical test `maze_prune_dir`'s own "Check 1," `asm_game.py:1586-1591`,
       already performs for an unrelated purpose), then `R` has a child in that direction and is
       **not** a leaf. A region with zero such children across all 4 directions is a **leaf**
       (region 0, the tree root, is never a leaf for `WORLD_SCALE >= 2` — the spanning tree always
       carves at least one edge from it).
    2. **Selection, up to `WORLD_SCALE` leaves:** for the first `WORLD_SCALE` leaf regions found
       by this sweep (region-index order — deterministic from `(SEED, WORLD_SCALE)` by
       construction, since which regions are leaves already varies by seed; `ADR-0015`'s own
       Decision explicitly leaves the exact selection-among-multiple-eligible-leaves rule open,
       so long as it is deterministic — this is that choice, made here): these regions are the
       placed set — leave their `KEYITEM_FLAGS` byte at the default `0` ("present, uncollected,"
       written by the pre-existing boot/reset clear — see §6's own encoding decision) and record
       how many were placed this way (the leaf count, capped at `WORLD_SCALE`).
    3. **Random-fill fallback, if leaf count < `WORLD_SCALE`:** for every region *not* selected as
       a leaf-placement, in region-index order, mark `KEYITEM_FLAGS[region] = 2` (absent) —
       **except** for the first `(WORLD_SCALE - leaf_count)` such regions encountered, which stay
       at the default `0` (present) instead. **Recommended, not mandated:** this fixed-order
       fill needs no new PRNG draw at all (the "randomness" comes entirely from which regions are
       leaves, which already varies by seed/braid outcome) — avoiding the same class of
       modulo-by-variable-count selection problem `ADR-0012` already ruled out Kruskal/Prim for
       on this codebase's PRNG (selecting `K` items without replacement from a variable-size
       candidate set has no cheap exact solution on this hardware). If a future revision wants
       genuine per-seed randomization of *which* non-leaf regions fill the shortfall (not just
       *which* leaves get first priority), that is new algorithmic work outside this package's own
       scope — flagged, not solved, here.
    4. **Every other region** (not a leaf-placement, not a fallback-fill) gets `KEYITEM_FLAGS
       [region] = 2` explicitly written — the existing boot-time/`st_intro`/`st_victory` reset
       loops zero the array (meaning "present" under the encoding below), so this pass must
       overwrite every non-selected region's byte, not rely on any implicit default.
    5. This pass consumes **no PRNG draws** (per the recommended fixed-order approach above) —
       confirm this leaves the subsequent braid pass's own PRNG sequence, and `worldgen.py`'s own
       lockstep mirror, entirely unaffected. If a future implementer deviates from the recommended
       approach and does add draws here, `worldgen.py`'s oracle mirror must add the identical
       draws at the identical point, per the established lockstep discipline (`ADR-0009`'s
       Consequences).
  - **`check_complete`** (`asm_game.py:728-732`): change the comparison operand from the literal
    `9` to a runtime read of `WORLD_SCALE` — the routine's own control flow (compare, `RET_NZ`,
    transition to `GS_VICTORY`) is otherwise unchanged.
  - **No change** to `setup_zone_collects`, `check_collisions`, `save_to_sram`, `try_load_save`,
    or `maze_prune_dir`/the braid pass itself — confirmed clean by the TWBS's own Supersession
    sweep, not assumed.
- **Modify: `worldgen.py`**: add the equivalent Python mirror of the new placement pass inside (or
  immediately after) `_carve_maze` — leaf classification from the already-computed `parent_dir`
  array (this oracle already builds `parent_dir` for its own braid-pass tree-edge test,
  `worldgen.py:126,171` — the leaf test reuses that same array, no new state needed on the Python
  side), then the identical selection/fallback-fill logic, returning enough information for
  `test_rom.py` to assert against (e.g. a `has_keyitem: bool` field per region in the returned
  dict, alongside the existing `biome_id`/`neighbors`).
- **Modify: `test_rom.py`**:
  - Retire/replace the count-only assertion `T12.e` currently makes (`asm_game.py`'s
    `KEYITEM_FLAGS` count check, `test_rom.py:961-962`) with the new AC-5 property test (§8).
  - Correct `T4.8` (`test_rom.py:304-313`): it currently forces `KEYITEM_FLAGS[0..8]=1` and
    `CARROTS_COUNT=9` against the default boot fixture's implicit `WORLD_SCALE`, then asserts
    victory. Once `check_complete` reads `WORLD_SCALE` at runtime, this fixture must also force
    `WORLD_SCALE` to a known value matching the forced count (or read whatever `WORLD_SCALE`
    already holds in that fixture and match `CARROTS_COUNT` to it) — a direct fixture-consistency
    fix, not a new test.

## 7. Implementation Tasks

Ordered: (1) confirm `IP-1070` (`GW_MAZE_STATE`) and `IP-1020` (`generate_world`'s current
structure) match this package's own citations by direct re-read (drift here is a hard Blocking
condition, per this skill's own rule); (2) implement the leaf-classification sweep inside
`generate_world`, between `maze_carve_done` and the braid pass; (3) implement the selection +
fallback-fill logic, writing `KEYITEM_FLAGS`'s tri-state values; (4) change `check_complete`'s
comparison operand; (5) mirror steps 2-3 in `worldgen.py`; (6) correct `T4.8`, replace `T12.e`,
add the new property tests (§8); (7) full suite run; (8) documentation/traceability updates (§9).

## 8. Tests to Add

Landing in the existing **T12: World Generation** suite (`test_rom.py`, no new suite number —
this is a revision of an existing generation feature, not a new one):

- **T12.e (revised)** — Scale-relative, dead-end-prioritized placement (FR-9160, FS-102 AC-5): for
  a `(seed, scale)` corpus (reusing the existing T12 corpus), assert: (a) exactly `WORLD_SCALE`
  regions have `KEYITEM_FLAGS != 2`; (b) every pre-braid leaf region (per the `worldgen.py` oracle's
  own leaf computation, cross-checked against the actual SM83 `GW_MAZE_STATE`-derived result) is
  among the placed set, up to `WORLD_SCALE`; (c) for corpus entries where leaf count is below
  `WORLD_SCALE` (confirmed a real, common case at `scale` ≤ 7 by `R215`'s own measured data — the
  corpus should include at least one such case deliberately, not rely on chance), the total still
  reaches exactly `WORLD_SCALE` via the fallback fill.
- **New T12.n — Scale-relative victory (FR-9161, FS-102 AC-9):** for a corpus spanning
  `WORLD_SCALE` 2 through 9, drive (or directly force, mirroring `T4.8`'s own established
  WRAM-write pattern) `KeyItemCount` to exactly `WORLD_SCALE` and confirm the PLAYING→VICTORY
  transition fires; confirm it does **not** fire one below that value.
- **T4.8 (corrected):** forces `WORLD_SCALE` to match the forced `CARROTS_COUNT`/`KEYITEM_FLAGS`
  values in that fixture, so the assertion remains meaningful once `check_complete` reads
  `WORLD_SCALE` at runtime rather than a compile-time `9`.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-9160`/`FR-9161` Notes → implemented,
  citing this package and its VR once verified; `FR-9130`/`FR-3300` Notes → formally superseded
  (not merely target-noted), per the established `FR-1120`→`FR-1170`-`1190` precedent's own
  second step (the FR-1120 Notes field itself, once `IP-1040` shipped, records "the superseding
  implementation has now shipped").
- `docs/requirements/04-requirements-traceability-matrix.md`: `FR-9160`/`FR-9161` rows' Module/
  Feature Spec/Implementation Package/Test columns filled (currently `UNASSIGNED`).
- `docs/features/FS-102-procedural-world-generation.md` metadata: implemented-by pointer for the
  2026-07-12 revision; Open Question 5 (encoding) marked resolved, citing this package's §6
  decision.
- `docs/architecture/07-data-model.md` §7c: confirm the shipped encoding matches (widened
  `KEYITEM_FLAGS` domain, not a new bitmap) — a short confirming note, not a new delta section.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- For every `(seed, scale)` in the test corpus, exactly `WORLD_SCALE` regions hold a `KeyItem`
  (`KEYITEM_FLAGS != 2`), prioritizing pre-braid leaves, with the fallback fill reaching the exact
  target when leaf count falls short.
- The placement decision is unaffected by which edges the subsequent braid pass reopens (verified
  by comparing pre-braid leaf computation against the final placement result).
- `check_complete` triggers victory at `KeyItemCount == WORLD_SCALE` for every tested
  `WORLD_SCALE`, not before.
- `setup_zone_collects`/`check_collisions`/`save_to_sram`/`try_load_save` confirmed byte-for-byte
  unchanged (the Supersession sweep's own "no change needed" finding re-confirmed against the
  actual diff, not just the plan).
- `worldgen.py`'s oracle mirrors the placement decision in lockstep with the SM83 routine —
  zero mismatches across the full corpus.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct diff: `setup_zone_collects`, `check_collisions`, `save_to_sram`, `try_load_save`
      byte-for-byte unchanged.
- [ ] Direct diff: `check_complete`'s only change is the comparison operand (constant → `WORLD_SCALE`
      read); control flow otherwise identical.
- [ ] `T12.e` (revised) and the new `T12.n` both confirmed passing; `T4.8` confirmed corrected and
      passing.
- [ ] `worldgen.py`/SM83 lockstep confirmed via the existing oracle-parity check (`T12.b`),
      extended to cover the new placement pass's own output.
- [ ] Confirmed no new PRNG draws were added without a corresponding `worldgen.py` mirror update
      (per §6 task 5's own note) — or, if the recommended no-new-draws approach was followed,
      confirmed the braid pass's own PRNG sequence is bit-for-bit unaffected by this package.

## 12. Dependencies

- **`IP-1020`** (`VERIFIED`) — the `generate_world`/`check_complete` routines this package
  extends.
- **`IP-1070`** (`VERIFIED`) — `GW_MAZE_STATE`'s own parent-direction data, this package's own
  leaf-classification input.
- No other in-flight package's Files to Modify overlap this one's own (`IP-1081`/`IP-1082` touch
  `tiles.py`/`draw_region_arrows`, disjoint).

## 13. Risks

Low-Medium — the leaf-classification logic reuses an already-shipped, already-tested pattern
(`maze_prune_dir`'s own "Check 1"), and the recommended fallback-fill approach deliberately avoids
new PRNG-sequencing risk. The one real risk this package names explicitly: if a future
implementation deviates from the recommended no-new-draws fallback approach, the `worldgen.py`
lockstep discipline becomes load-bearing again in a new place, the same class of risk `FS-102`
§18 already names for the base generation routine — not a new risk category, an extension of an
already-acknowledged one.

## 14. Rollback Considerations

Revert `asm_game.py`'s new placement pass and `check_complete`'s operand change, `worldgen.py`'s
mirror addition, and the `test_rom.py` corrections, then rebuild. No save-format dependency — the
chosen encoding reuses `KEYITEM_FLAGS`'s existing SRAM mirror unchanged (§6), so no version bump
and no migration path are needed, a genuine simplicity benefit of the widened-domain encoding
decision over the alternative (a new bitmap would have raised the same save-format-version
question `IP-9070`/`IP-1050`/`IP-9110` each had to answer for their own new persisted fields —
this package avoids that entirely since nothing new is persisted).
