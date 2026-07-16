# IP-1022 — Finite-Mode Nine-Identity Generation & Screen Dispatch

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1022` — implements the 2026-07-16 revision of [**FS-102**](../../features/FS-102-procedural-world-generation.md)
(`FEAT-9000`, Epic `EP-5000`) and [**FS-103**](../../features/FS-103-generated-region-screen-composition.md)
(`FEAT-4100`, Epic `EP-5000`) together, grounded by `FR-4310`/`FR-4320` (`BL-0128`, `CR-08`
resolved 2026-07-16). Widens finite-mode world generation's biome-id domain from five values to
nine and extends the shared screen-dispatch cascade to render all nine — the two halves the
Technical Work Breakdown's own verb inventory found inseparable (the numeric ID assignment drives
both at once).

## 2. Objective

Widen `generate_world`'s grammar-constrained biome draw from `[0,4]` to `[0,8]`, extend
`dsr_p`/`dsr_p_dispatch`'s screen-selection cascade to the four newly-folded identities
(Village, Cave, Desert, Plains — already-authored screen functions, wiring only), and assemble
`ZONE_COLLECTS`'s final nine-entry array from the five existing lists plus `IP-1033`'s staged
content.

## 3. Requirements Covered

`FR-4310` (grammar-valid adjacency — the nine-value ordering this package's generator clamp and
dispatch cascade both implement), `FR-4320` (nine biome-family identities — the domain/identity
set this package makes concretely reachable in finite-mode play), `FR-4300` (one biome per
screen — unaffected, extended to nine identities by construction, not by new logic).

## 4. Architecture Components

[GDS-08](../../architecture/08-presentation-architecture.md) §4/§8 (terrain-family palette
groups this package's dispatch cascade selects between — no new palette slot, confirmed at `06`)
· [GDS-07](../../architecture/07-data-model.md) §6 (`REGION_GRAPH`'s biome-id byte, already a
full unpacked byte — no data-model change needed for this widening, confirmed at `04`).

## 5. Interfaces

- **`REGION_GRAPH`** (`0xC070`+, existing) — no address/format change; the biome-id byte already
  accommodates 0-255, this package only widens the *range of values the generator actually
  produces and the dispatch actually recognizes*.
- **`ALL_SCREENS`'s existing per-`(name, fn)` contract** (GDS-09 delta, unchanged shape) — four
  new entries appended: `("village", village_screen)`, `("cave", cave_screen)`,
  `("desert", desert_screen)`, `("plains", plains_screen)` — all four functions already exist in
  `tilemaps.py`, confirmed unmodified since the original as-built game.
- **The `patches` dict's existing per-family key pattern** (`water_t`/`water_a`, etc.) — four new
  key pairs: `village_t`/`village_a`, `cave_t`/`cave_a`, `desert_t`/`desert_a`,
  `plains_t`/`plains_a`, resolved by `build_rom.py`'s existing `p16(patches[...], screen_addrs[...])`
  pattern, no new resolution machinery.
- **`ZONE_COLLECTS`** — this package performs the final array assembly `IP-1033`'s own package
  deliberately deferred: splicing its four staged, inert lists into `ZONE_COLLECTS`'s real array
  at indices 5-8 (matching this package's own `CR-08`-resolved identity-to-position assignment),
  and updating `setup_zone_collects`'s consuming index range if it assumes exactly 5 entries
  anywhere (confirm by direct read at implementation time — not assumed here).

## 6. Files to Create/Modify

- **Modify: `worldgen.py`** — `generate()`'s biome-domain constants (confirmed at `worldgen.py:66`
  `lo, hi = 0, 4` and `worldgen.py:85`-ish `if b > 4: b = 4`): both ceiling values `4`→`8`. The
  `_draw_delta`/mod-3 mechanism itself is unchanged — it is a domain-agnostic ±1 random walk;
  widening only the clamp bounds is sufficient, confirmed by direct re-read of the algorithm's own
  shape (no other constant encodes "5 values").
- **Modify: `asm_game.py`**:
  - **`generate_world`** (`asm_game.py:2031`–`2130`-ish): the `gw_delta_neg`/`gw_delta_zero`/
    `gw_b_same` clamp cascade's `CP_n(4)` instances (confirmed at `asm_game.py:2087` and the
    `gw_other_lt`/`gw_other_skip` neighbor-clamp branch's own comparison, confirmed distinct
    from the primary ceiling check — re-verify both at implementation time) → `CP_n(8)`.
  - **`dsr_p`/`dsr_p_dispatch`** (`asm_game.py:1392`–`1411`): extend the `CP_n`/`JR_Z` cascade —
    `CP_n(0)`→water, `CP_n(1)`→sand, `CP_n(2)`→grass, `CP_n(3)`→stone, `CP_n(4)`→brick (all five
    unchanged), then **four new comparisons**: `CP_n(5)`→village, `CP_n(6)`→cave, `CP_n(7)`→desert,
    unconditional fallthrough (was brick, now)→plains (biome-id 8, the new final entry — mirrors
    the existing pattern where the *last* identity is reached by fallthrough, not an explicit
    compare, per `asm_game.py:1397`'s own documented convention). Four new `_dsr_family()` calls
    (`asm_game.py:1400`–`1410`'s own helper, reused verbatim): `_dsr_family('dsr_p_village',
    'village_t', 'village_a')`, `_dsr_family('dsr_p_cave', 'cave_t', 'cave_a')`,
    `_dsr_family('dsr_p_desert', 'desert_t', 'desert_a')`, and a `dsr_p_plains` label reached by
    fallthrough (mirroring `dsr_p_brick`'s own prior fallthrough-target shape, now one step
    further down the cascade).
  - **Update the stale inline comment** at `asm_game.py:1397` ("biome-id 4 (`generate_world`'s own
    invariant: axis-clamped to 0..4)") to reflect the new 0-8 range and the fallthrough target's
    new identity (plains, not brick) — the Technical Work Breakdown's own Supersession sweep
    named this comment as documentation-only drift to fix here.
- **Modify: `tilemaps.py`**:
  - `ALL_SCREENS`: append the four entries named in §5.
  - `ZONE_COLLECTS`: splice `IP-1033`'s four staged lists into the array at indices 5-8 (Village,
    Cave, Desert, Plains, in that `CR-08`-resolved order), removing their "staged, not yet
    spliced" labeling from `IP-1033`'s own package.
- **Modify: `build_rom.py`**: four new `p16(patches['village_t'], screen_addrs['village'][0])`-
  style lines (8 lines total), following the existing `water_t`/`sand_t`/`grass_t`/`stone_t`/
  `brick_t` pattern exactly (`build_rom.py:177`–`185`-ish).
- **Modify: `test_rom.py`**: `T13.a`'s `FAMILY_RANGES` dict (currently 5 entries, biome-ids 0-4)
  extended with the four new identities' own tile-index ranges (`village_screen`'s `0x90`–`0x95`,
  etc. — already documented in `IP-1033`'s own §6); `T12.d`'s adjacency-grammar corpus check
  extended to include region graphs that can legally reach biome-ids 5-8 (confirming no illegal
  pairing exists across the widened axis, not just the original five).
- **No change** to `check_zone_transition`, `setup_zone_collects`'s own biome-id-indexed lookup
  mechanism (the *indexing* logic is domain-size-agnostic — confirmed by direct re-read, only the
  *data* it indexes into grows), or any Infinite Mode file — confirmed clean by this package's own
  Supersession sweep re-run (see Technical Work Breakdown).

## 7. Implementation Tasks

Ordered: (1) confirm every cited line number/constant against the current tree by direct re-read
(planned against commit `1d38b34`; drift is Blocking); (2) confirm `IP-1033`'s own four spawn
lists exist in `tilemaps.py` (this package's own hard dependency — if `IP-1033` hasn't shipped,
this package cannot complete task 6 below and must itself stay `BLOCKED`); (3) widen
`worldgen.py`'s clamp bounds; (4) widen `asm_game.py`'s `generate_world` clamp bounds (both
comparison sites); (5) extend `dsr_p_dispatch`'s cascade, add the four `_dsr_family` calls, fix
the stale inline comment; (6) extend `ALL_SCREENS`, splice `ZONE_COLLECTS`'s four new entries at
indices 5-8; (7) extend `build_rom.py`'s patch wiring; (8) rebuild, full suite run; (9) extend
`T13.a`/`T12.d` per §6; (10) documentation/traceability updates (§9).

## 8. Tests to Add

Landing in the existing **T12: World Generation** / **T13: Screen Composition** suites (no new
suite — a revision of existing generation/rendering features, not a new one):

- **T12.d (extended)** — Grammar-validity property test, re-run across a corpus that reaches
  biome-ids 5-8 (not just 0-4), confirming `|a-b|<=1` holds for every adjacent pair on the full
  nine-value axis, per `FR-4310`'s own now-concrete Acceptance Criteria.
- **T13.a (extended)** — Tile-family audit, `FAMILY_RANGES` extended to all nine identities,
  confirming each of the four new identities' screens render their own family's tiles exclusively
  (mirroring the original five-identity check's own method exactly).
- **New: dispatch cascade completeness check** — direct WRAM force (mirroring `T13.a`'s own
  established pattern: force `REGION_GRAPH`'s biome-id byte directly, force a redraw) for each of
  biome-ids 5-8, confirming the correct screen renders and the correct `ZONE_COLLECTS` entry
  spawns — the same class of evidence this session's own `content-review-ip-1081-ip-1082.md`
  methodology used for a similar direct-force verification.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-4310`/`FR-4320` Notes → cite this
  package once `VERIFIED`.
- `docs/requirements/04-requirements-traceability-matrix.md`: `FR-4310`/`FR-4320` rows' Module/
  Feature Spec/Implementation Package/Test columns filled.
- `docs/features/FS-102-procedural-world-generation.md`/`FS-103-generated-region-screen-composition.md`
  metadata: implemented-by pointer; `FS-102` §19 Open Question 6 (collectible content) marked
  fully resolved (both content authorship, `IP-1033`, and array wiring, this package); `FS-103`
  §19 Open Questions 1-2 marked fully resolved (dispatch wiring complete, not just art/budget
  confirmed pre-existing).
- `docs/architecture/07-data-model.md` §8 (tile-index cross-reference): confirm the shipped
  nine-identity dispatch matches, no format change to document (the byte was always full-range).
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Finite-mode `generate_world` produces grammar-valid worlds drawing from the full nine-value
  biome-id domain, for a `(seed, scale)` corpus including cases that reach biome-ids 5-8.
- All nine identities' screens render correctly when their biome-id is reached (confirmed both by
  live generation and direct-force verification).
- `ZONE_COLLECTS`'s nine-entry array is complete and correctly indexed — each of the four new
  entries spawns its own collectible list on its own screen, with exactly one type-2 entry each.
- `worldgen.py`'s oracle remains in lockstep with the SM83 routine across the widened domain —
  zero mismatches.
- No Infinite Mode file touched — confirmed by diff scope.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct diff: no Infinite Mode file (`inf_*`/`czt_infinite`/`draw_region_arrows_inf`) touched.
- [ ] `T12.d`/`T13.a` (both extended) confirmed passing across the full nine-value domain.
- [ ] Dispatch-cascade completeness check (§8, direct-force) confirmed for all four new
      identities.
- [ ] `worldgen.py`/SM83 lockstep re-confirmed across the widened domain, zero mismatches.
- [ ] `ZONE_COLLECTS`'s nine entries each contain exactly one type-2 entry, confirmed by direct
      count.

## 12. Dependencies

- **`FR-4310`/`FR-4320`** (baselined, `04-requirements-engineering`) — the concrete nine-value
  ordering and identity set this package implements.
- **`IP-1033`** (`NOT STARTED`, not authorized) — this package's own task 6 (`ZONE_COLLECTS`
  splicing) cannot complete until `IP-1033`'s four spawn lists exist in the tree. This package is
  therefore **`BLOCKED`**, not merely unauthorized — a real, unshipped prerequisite, distinct from
  `IP-1033`'s/`IP-1105`'s own current "`NOT STARTED`, gated only on G3" state.
- **`IP-9070`** (`VERIFIED`) — the package whose own five-entry `ZONE_COLLECTS`/dispatch
  consolidation this package extends, not replaces.
- No other in-flight package's Files to Modify overlap this one's own (`IP-1106` depends on this
  package but touches disjoint Infinite-Mode-only files).

## 13. Risks

Medium — larger surface than `IP-1105`/`IP-1033` individually (touches the live generation
algorithm, the shared render dispatch, and the collectible-spawn array assembly in one package),
but each individual change is mechanical (clamp-bound widening, cascade extension following an
established four-call pattern, array splicing) with strong existing precedent (`IP-1030`'s own
original five-entry version of this exact dispatch shape). The one real risk: the `ZONE_COLLECTS`
splice must land the four new entries at exactly the indices `dsr_p_dispatch`'s own cascade
expects (5=Village, 6=Cave, 7=Desert, 8=Plains) — a mismatch here would silently spawn the wrong
collectible list on the wrong screen, not a build-time-caught error. Mitigated by the dispatch-
cascade completeness check (§8), which exercises both the screen *and* the collectible list
together per identity, not separately.

## 14. Rollback Considerations

Revert the clamp-bound widenings, the four dispatch-cascade branches/`_dsr_family` calls, the
`ALL_SCREENS`/`ZONE_COLLECTS` extensions, and the `build_rom.py`/`test_rom.py` corrections, then
rebuild. No save-format dependency — `REGION_GRAPH`'s biome-id byte format is unchanged (still a
full byte, just a wider range of values), so no `SAVE_VERSION_VAL` bump or migration path is
needed, mirroring `IP-1105`'s own equivalent finding for the Infinite Mode side.
