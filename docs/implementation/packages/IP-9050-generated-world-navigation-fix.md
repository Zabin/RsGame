# IP-9050 — Generated-World Navigation Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9050` — bug-remediation series; no FS. Source: **`BL-0047`** (Critical, project owner
playtesting, filed via `00-intake`).

## 2. Objective

Regeneralize `check_zone_transition` to read `REGION_GRAPH`'s per-region neighbor bytes —
exactly the structure `dsr_p`/`draw_region_arrows` (`IP-1030`) already correctly consume for
rendering — instead of the pre-procgen hardcoded fixed-9-zone `CUR_ZONE` arithmetic it still
runs today. This is the missing *navigate* verb `IP-1020`/`IP-1030` never packaged (see the
[TWBS](../01-technical-work-breakdown.md#post-ship-remediation-tranche-playtesting-bugs-bl-0047bl-0048-planned-2026-07-11)'s
own verb-inventory finding).

## 3. Requirements Covered

`FR-2300`/`FR-2310` (zone-boundary transition on valid/no neighbor) — cited as the closest
existing statement of intent, **explicitly noted as a gap**: both are worded entirely in terms
of "the 3×3 grid" and have no target-state counterpart generalizing them to `REGION_GRAPH`
(filed as `BL-0061`, routed to `04-requirements-engineering`, not blocking this package). Also:
`ADR-0009` (binding architecture decision — navigation must read the generated adjacency graph,
"a graph of `scale`-determined region nodes... connected by adjacency edges," Decision point 1)
and `FR-9100` (world-scale determinism — this fix is what makes `WORLD_SCALE` actually observable
in gameplay, not just in generation).

## 4. Architecture Components

ADR-0009 (Decision points 1, 6 — the generalized-navigation and `_zone_arrows`-supersession
decisions this package finally completes the second half of) · GDS-04 delta (region-graph domain
model) · GDS-07 §6 (`REGION_GRAPH`'s 5-bytes-per-region layout: biome-id, then up/down/left/right
neighbor-index bytes, `0xFF` = no neighbor — already shipped and already correctly consumed by
`dsr_p`/`draw_region_arrows`).

## 5. Interfaces

No new interface. Consumes the **existing** `REGION_GRAPH` read contract `dsr_p`/
`draw_region_arrows` already established (`asm_game.py:751-761`, `:820-823`) — same 5-bytes-per-
region layout, same `0xFF`-means-no-neighbor convention, same `region*5` addressing arithmetic
(`ADD_HL_DE` ×5, "correct up to scale=9's 81 regions" per the existing inline comment this
package's fix finally makes true for navigation, not just rendering).

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`check_zone_transition`** (`asm_game.py:566`, full rewrite): replace every hardcoded
    `CUR_ZONE` comparison (`CP_n(2)`/`CP_n(5)`/`CP_n(8)` for the right edge, `CP_n(3)`/`CP_n(6)`
    for the left edge, `CP_n(3)`/`CP_n(6)` for top/bottom) and every `±1`/`±3` `CUR_ZONE`
    arithmetic step with a `REGION_GRAPH` neighbor-byte lookup: compute `HL = REGION_GRAPH +
    CUR_ZONE*5` (the identical addressing `dsr_p` already performs), read the neighbor byte for
    the crossed edge's direction (`HL+1`=up, `HL+2`=down, `HL+3`=left, `HL+4`=right — `GDS-07`
    §6's established byte order), and branch on `0xFF` (no transition — clamp position at the
    boundary, `FR-2310`'s intent) vs. a valid region index (transition — `CUR_ZONE` ← the
    neighbor byte's own value directly, **not** computed via arithmetic; reposition
    `PLAYER_X`/`PLAYER_Y` to the entry edge exactly as today's shipped code already does — the
    `8`/`150`/`24`/`120` entry-position constants are geometry, not zone-count-dependent, and are
    unchanged by this fix).
  - Edge-detection thresholds (`PLAYER_X CP_n(156)`, `PLAYER_Y CP_n(18)`/`CP_n(128)`) are
    unchanged — they detect "the player reached a screen edge," a per-screen-geometry fact
    independent of how many regions exist or which one is current.

## 7. Implementation Tasks

Ordered: (1) confirm `IP-9070` has landed and `VERIFIED`/`COMPLETE` first (hard dependency — see
§12); (2) rewrite `check_zone_transition`'s four edge-branches (right/left/top/bottom) to read
`REGION_GRAPH`'s neighbor bytes instead of hardcoded `CUR_ZONE` comparisons; (3) confirm
`setup_zone_collects`'s own `REGION_GRAPH` biome-id read (added by `IP-9070`) still executes
correctly on every zone entry now that `CUR_ZONE` can exceed 8 (an integration check between the
two packages, not new code in this one); (4) rebuild ROM; (5) author T17 (see §8), including the
`scale≠3` in-context world-walk regression this fix exists to close; (6) full suite run; (7)
documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T17: Generated-World Navigation`**:

- **T17.a — scale=5 full-world traversal (the direct `BL-0047` regression test)**: new game with
  a fixed `(seed, scale)` pair chosen (via `worldgen.py`'s oracle, offline, before writing the
  test) to place regions reachably across the full 5×5 grid; walk the actual button-driven
  gameplay path (not `force_region_redraw`) across every legal transition the oracle's own graph
  says exists, asserting `CUR_ZONE` matches the oracle-predicted neighbor at each step. This is
  the runtime-driven reachability check `R305`'s 2026-07-11 delta (`BL-0057`) names as
  necessary-but-previously-missing, paired with `T12.c`'s existing oracle-only check — not a
  replacement for it.
- **T17.b — scale=3 regression**: confirm the existing shipped scale=3 behavior (the case every
  prior suite already covered) is bit-for-bit unchanged — `REGION_GRAPH`-driven navigation at
  scale=3 must produce identical transitions to the old hardcoded math, since `ADR-0009`'s
  generation algorithm's own row/col grid shape is unchanged, only the *mechanism* reading it is.
- **T17.c — boundary halt**: for a region genuinely at a generated-world edge (an oracle-computed
  boundary at whatever scale T17.a uses, not assumed to be `CUR_ZONE==2` the way the retired
  `T9.5` did), confirm no transition occurs and `CUR_ZONE` is unchanged — the `FR-2310` regression
  test, generalized past the fixed-grid vocabulary `BL-0057`'s R305 delta flagged in `T9.5`'s own
  stale comment.
- **T17.d — entry-position correctness**: confirm `PLAYER_X`/`PLAYER_Y` land at the correct entry
  edge (`8`/`150`/`24`/`120`) after each of T17.a's transitions, exactly as the pre-existing
  `T9.3`/`T9.7`/`T9.9` checks already verify for the scale=3 case.

**`T9`'s existing checks are retired, not merely left alongside these** — `T9.5`'s own comment
("No right transition from col 2 (z2)") is stale fixed-grid vocabulary this package's fix makes
literally false as a general statement (region 2 has no special meaning once `REGION_GRAPH`
drives navigation); replace `T9` with `T17` rather than keeping both, per `R305`'s "rewrite, don't
patch" precedent (`BL-0006`'s own resolution).

## 9. Documentation Updates

- `docs/architecture/04-domain-model.md` (GDS-04 delta): confirm `check_zone_transition` as
  `REGION_GRAPH`-driven, as-shipped (a "confirmed, implemented" note completing `ADR-0009`
  Decision point 1's own deferred implementation pointer).
- `docs/requirements/01-functional-requirements.md`: `FR-2300`/`FR-2310` get a forward-pointer
  note that generated-world navigation now honors their intent via `REGION_GRAPH` (metadata
  note only — the postcondition-generalizing FR text itself is `BL-0061`'s future `04` delta, not
  rewritten here, per this skill's own SHALL-NOT-modify-requirements rule).
- `docs/requirements/04-requirements-traceability-matrix.md`: `FR-2300`/`FR-2310` Test cells
  updated to cite `T17` (superseding the retired `T9` citation).
- Master Build Plan status row.

## 10. Definition of Done

- All four `check_zone_transition` edge-branches read `REGION_GRAPH`'s neighbor bytes; zero
  hardcoded `CUR_ZONE` comparisons/arithmetic remain in the routine.
- `T17.a` demonstrably passes at `scale=5` (or another non-default scale) — a player can reach
  every region a generated world contains, via real button-driven navigation.
- `T17.b` confirms scale=3 behavior is bit-for-bit unchanged from the pre-fix shipped behavior.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [x] G5: ROM builds at exactly 32768 bytes with valid header.
- [x] G5: full `test_rom.py` suite passes (213/213).
- [x] T17.a–d each present and passing.
- [x] Direct code read: `check_zone_transition` contains no `CUR_ZONE` literal-integer comparison
      or `±1`/`±3` arithmetic step anywhere in its body — every branch reads a `REGION_GRAPH`
      byte. Confirmed by a direct regex sweep of the routine's own body: the only `CP_n(...)`
      literals remaining are `156`/`18`/`128` (the unchanged screen-edge-detection thresholds,
      per §6) and four `0xFF` (the `REGION_GRAPH` neighbor-byte sentinel checks); zero
      `INC_A`/`DEC_A`/`SUB_n`/`ADD_A_n` occurrences.
- [x] Direct code read: the neighbor-byte addressing (`REGION_GRAPH + CUR_ZONE*5`, `+1..+4` for
      up/down/left/right) matches `dsr_p`/`draw_region_arrows`'s own addressing exactly — no
      independent/divergent reimplementation of the same lookup (`check_zone_transition` calls a
      new shared `czt_region_hl` subroutine using the identical `LD_E_A`/`LD_D_n(0)`/`ADD_HL_DE`×5
      sequence `dsr_p` already uses).
- [x] **This session's own independence rule**: confirmed `IP-9070` is `COMPLETE` (its own DoD
      met, 193/193 at the time) before this package's own suite run.
- [x] GDS-04/FR-2300/FR-2310 RTM/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-9070`** (`SCOREITEM_FLAGS`/`ZONE_COLLECTS` generalization) — **hard prerequisite, not a
  convenience ordering.** This package is what makes `CUR_ZONE > 8` reachable; `IP-9070` is what
  makes every other `CUR_ZONE`-indexed structure safe for that range. Shipping this package
  without `IP-9070` already `VERIFIED`/`COMPLETE` converts `BL-0058`/`BL-0059` from dormant to
  active.
- **IP-1020** (`VERIFIED`, `REGION_GRAPH`'s own generation) · **IP-1030** (`VERIFIED`, the
  `dsr_p`/`draw_region_arrows` addressing pattern this package's fix mirrors exactly).

## 13. Risks

- **The single highest-risk package in this remediation tranche if sequenced wrong** — see §11's
  explicit dependency-gate checklist item. Mitigated entirely by making `IP-9070` a named hard
  dependency rather than a scheduling suggestion.
- **Requirements-traceability gap** (`BL-0061`, `FR-2300`/`FR-2310` have no target-state
  counterpart) — not blocking, routed upstream per §3.
- ROM budget: negligible — `check_zone_transition`'s rewrite is a like-for-like control-flow
  change (hardcoded comparisons replaced by a table read), not new data.

## 14. Rollback Considerations

Revert `asm_game.py`'s `check_zone_transition` and rebuild. Reverts to the shipped (buggy,
fixed-3×3-only) navigation behavior exactly — no save-format dependency, since `CUR_ZONE` itself
is already persisted as a raw byte with no range assumption baked into the save routines
(confirmed: `save_to_sram`/`try_load_save` copy `CUR_ZONE` as a single unconditioned byte).
