# IP-1102 — Infinite Mode: Streaming Window, Navigation & Render Integration

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1102` — implements part of [**FS-110**](../../features/FS-110-infinite-mode.md) (`FEAT-10000`,
Epic `EP-6000`, `Future` bucket). Covers Workflow B steps 1, 3, 4 (the fused `navigate`+`render`
verbs — see the [Technical Work Breakdown](../01-technical-work-breakdown.md)'s own
not-independently-completable rationale for why these two verbs share one package).

## 2. Objective

Maintain a 3×3 materialized-region working set centered on the player, trigger `IP-1101`'s
materialization routine as the player approaches a not-yet-resident region, and render the
current region — reusing `dsr_p`'s existing biome-dispatch half verbatim, replacing
`draw_region_arrows` with a new connectivity-nibble-driven equivalent.

## 3. Requirements Covered

FR-10200 (streaming materialization, the navigate/render half); NFR-4300 (materialized-window
WRAM headroom, `NOT YET SIZED` until this package — sized here, see §6).

## 4. Architecture Components

[ADR-0016](../../architecture/adr/ADR-0016-streaming-infinite-mode-generation-architecture.md)
point 7 (no new module — extends `asm_game.py`) · this package's own Technical Work Breakdown
rendering-integration finding (`dsr_p` reusable verbatim, `draw_region_arrows` is not) · the
Technical Work Breakdown's "Per-region encoding, materialized-window… sizing" decisions (3×3
window, 1 byte/region, `INF_ROW`/`INF_COL` center-anchor).

## 5. Interfaces

- **`dsr_p`'s biome-dispatch half** (`asm_game.py:951-966`, unmodified) — this package's own
  render path places a biome-id (`0-4`, read from `INF_WINDOW`'s center cell) into register A and
  jumps directly to the `dsr_p_water`/`sand`/`grass`/`stone`/`brick` branch point, **skipping**
  `dsr_p`'s own `REGION_GRAPH` read entirely (Infinite Mode has no `REGION_GRAPH`) — zero
  `FEAT-4100` code changes.
- **`copy_screen`** (unmodified) — called identically to the finite mode's own `dsr_p_copy` path.
- **A new `draw_region_arrows_inf` routine** (this package's own addition, not a `FEAT-2100`
  modification) — reads the current region's own connectivity nibble directly from `INF_WINDOW`'s
  center cell rather than `REGION_GRAPH` neighbor-index bytes; no grid-boundary distinction is
  needed (Infinite Mode's world is unbounded — a closed direction is always "maze-blocked," never
  "grid-absent," unlike the finite mode's `ADR-0012` point 2 distinction) — draws the plain open
  arrow (`TL_ARROW_U/D/L/R`) wherever the connectivity bit is set, nothing wherever it is clear
  (no blocked-edge indicator tile needed here — Infinite Mode has no concept of a "grid-adjacent
  but maze-pruned" edge distinct from "closed," since every direction always has a real,
  materializable neighbor region).
- **`check_zone_transition`'s existing dispatch shape** (unmodified for the finite mode) — this
  package adds a parallel `GAME_MODE`-gated branch at the *top* of the existing dispatch (checked
  once per transition attempt, not inside any of the four existing direction branches), routing
  to a new `czt_infinite` handler when `GAME_MODE == 1`; the finite mode's own four branches are
  reached only when `GAME_MODE == 0`, unchanged.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New WRAM constants** (first unclaimed bytes past `IP-1100`'s own `GAME_MODE`, `0xC3F6`):
    `INF_ROW = 0xC3F7` (2 bytes, signed 16-bit, player's current region row), `INF_COL = 0xC3F9`
    (2 bytes, signed 16-bit, player's current region col), `INF_WINDOW = 0xC3FB` (9 bytes,
    `0xC3FB`–`0xC403`, 3×3 materialized window, row-major, center cell = current region, 1 byte/
    region per `IP-1101`'s own output format), `INF_TREASURE_HERE = 0xC404` (1 byte, transient
    cache: current region's own treasure-presence-and-uncollected flag for this materialization,
    refreshed whenever the center cell changes — avoids re-drawing the treasure predicate every
    frame; `IP-1103`'s own scope to read/clear).
  - **New subroutine `inf_ensure_window`** — called whenever `INF_ROW`/`INF_COL` changes
    (transition-triggered, below): for each of the 3×3 window's 9 cells not already known to hold
    the correct region's data (the whole window is simply recomputed fresh on every center change
    — no incremental shift logic, since `IP-1101`'s own routine is cheap and pure, per the
    Technical Work Breakdown's own "avoids needing a sliding-window management scheme" framing),
    calls `IP-1101`'s `inf_materialize_region` and writes the result into `INF_WINDOW`'s
    corresponding cell.
  - **New `czt_infinite` handler** (called from `check_zone_transition`'s new `GAME_MODE`-gated
    branch, §5): reads the current region's own connectivity nibble from `INF_WINDOW`'s center
    cell; for the direction the player's `JOY_CUR` press indicates (same `BIT_b_A(J_RIGHT/…)`
    gating `IP-9130`'s own intent-gate fix established, reused verbatim — no regression to that
    fix), if the corresponding connectivity bit is clear, no transition (mirrors the finite mode's
    own "blocked" case); if set, `INF_ROW`/`INF_COL` update by ±1 on the moved axis, then
    `inf_ensure_window` re-centers, then falls through to the existing screen-redraw call site
    (`do_screen_redraw`'s own LCD-off bracket, unmodified — NFR-1300's existing safe-window
    convention, reused not reinvented).
  - **`dsr_p`'s own entry point (existing label):** gains a `GAME_MODE`-gated branch at its very
    start — if `GAME_MODE == 1`, load A from `INF_WINDOW`'s center cell (masked to bits 0-2, the
    biome-id half) and jump directly into the existing `dsr_p_water`/…/`dsr_p_brick` chain,
    **bypassing** the `REGION_GRAPH`/`CUR_ZONE` read entirely; the existing finite-mode path
    (`GAME_MODE == 0`) is otherwise byte-for-byte unchanged. After `dsr_p_copy`'s `copy_screen`
    call, the existing `CALL('draw_region_arrows')` becomes a `GAME_MODE`-gated call to either the
    existing routine (finite) or the new `draw_region_arrows_inf` (infinite).
  - **New subroutine `draw_region_arrows_inf`** (§5) — reads `INF_WINDOW`'s center cell's
    connectivity nibble (bits 3-6), draws the plain open-arrow tile at each of the four fixed
    screen positions (`ARROW_ADDR_U/D/L/R`, the exact same constants `draw_region_arrows` already
    defines, reused verbatim — no new tile positions) wherever its bit is set, nothing wherever
    clear.

## 7. Implementation Tasks

Ordered: (1) `INF_ROW`/`INF_COL`/`INF_WINDOW`/`INF_TREASURE_HERE` WRAM constants; (2)
`inf_ensure_window` (9-cell recompute via `IP-1101`'s routine); (3) `czt_infinite` handler +
`check_zone_transition`'s `GAME_MODE`-gated branch; (4) `dsr_p`'s `GAME_MODE`-gated biome-dispatch
entry; (5) `draw_region_arrows_inf`; (6) `dsr_p_copy`'s arrow-call `GAME_MODE` gate; (7) rebuild
ROM; (8) author T24 (see §8); (9) full suite run; (10) documentation/traceability updates (§9).

**Supersession-sweep note (mandatory per this skill's own rule, applied here since this package
adds a new branch to two existing, heavily-exercised routines — `dsr_p`/`check_zone_transition`):**
swept both routines' full existing call-site set. `dsr_p` has exactly one caller (`PLAYING`'s own
main-loop redraw dispatch) — the new `GAME_MODE` gate at its top is the only new branch, no other
call site needs updating. `check_zone_transition` has exactly one caller (`handle_play_input`'s
own per-frame movement-intent check, per `IP-9130`'s own gating) — same conclusion. **Confirmed
clean — no other call site encodes an assumption this package's own gate violates.**

## 8. Tests to Add

New `test_rom.py` suite **`T24: Infinite Mode — Streaming Window & Rendering`**:

- T24.a — from a materialized starting region, drive movement toward each of the 4 directions in
  turn (using a corpus of seeds with known connectivity, cross-checked against `worldgen.py`'s own
  oracle) — confirm a transition occurs iff the connectivity bit is set, `INF_ROW`/`INF_COL`
  update correctly, and the newly-entered region's own screen renders the correct biome tileset
  (mirrors `T17.a`'s own real-button-press navigation-test shape, extended to the unbounded case).
- T24.b — revisit consistency through the render path: leave a region (window re-centers away from
  it), return to it, confirm the redrawn screen is pixel-identical to the first visit (delegates
  the underlying data check to `IP-1101`'s own T23.c, adds the render-path confirmation T23 alone
  cannot make).
- T24.c — `dsr_p`'s finite-mode path (`GAME_MODE == 0`) is byte-for-byte unchanged — direct `git
  diff`-style confirmation that every existing finite-mode `dsr_p`/`draw_region_arrows` check in
  the current suite (`T13`, `T20`) still passes unmodified, with no new gate altering their
  behavior.
- T24.d — the plain-open-arrow-only claim (no blocked-edge indicator in Infinite Mode): confirm
  `draw_region_arrows_inf` never writes `TL_BLOCKED_U/D/L/R` under any connectivity nibble value
  (static audit + a corpus of connectivity values driven through it).
- T24.e — `NFR-1400` Analysis check: direct cycle-count of `inf_ensure_window`'s worst case (all 9
  cells requiring fresh materialization, e.g. a diagonal move is never possible in this game's
  4-direction input model, so the realistic worst case is 3 new cells per transition — one column
  or row of the 3×3 window) against `check_zone_transition`'s existing safe-timing budget; records
  the measured result honestly (Met or still open) rather than asserting compliance un-measured
  (`FS-110` AC-8's own explicit "not yet a checkable criterion" framing — this is where it becomes
  checkable).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-10200 status → Implemented (navigate/
  render half — `IP-1101` covers the generate half); NFR-4300 status → Met (sized: 3×3 window, 9
  bytes + 4 bytes center-anchor = 13 bytes, against the confirmed ~3.1 KiB bank-0 headroom) or
  `NOT MET`/left `UNCONFIRMED` per whatever T24.e's own measurement actually finds for NFR-1400
  specifically (NFR-4300's own sizing is fixed regardless; NFR-1400's timing compliance is not
  asserted by this document update, only measured and recorded).
- `docs/architecture/07-data-model.md` (GDS-07): new §8 (or equivalent) recording
  `GAME_MODE`/`INF_ROW`/`INF_COL`/`INF_WINDOW`/`INF_TREASURE_HERE`'s WRAM addresses — the first
  real `GDS-07` delta for Infinite Mode (`FS-110` §10 noted none existed yet; this package
  supplies it).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-10200/NFR-4300 rows → `IP-1102`/
  T24; NFR-1400 row updated with T24.e's actual measured result.
- `docs/features/FS-110-infinite-mode.md` metadata: implemented-by pointer for Workflow B steps
  1/3/4; §19 Open Questions 1 and 8 marked Resolved (rendering-integration mechanism, window
  sizing).
- Master Build Plan status row.

## 10. Definition of Done

- Streaming materialization triggers correctly on approach, in all 4 directions, for a real
  navigation corpus (T24.a).
- Revisit-consistency holds through the full render path, not just the data layer (T24.b).
- The finite mode's own `dsr_p`/`draw_region_arrows`/`check_zone_transition` paths are provably
  byte-for-byte unchanged (T24.c, direct diff).
- NFR-4300 is sized and Met; NFR-1400 is measured and its actual result (Met or not) is recorded
  honestly, not asserted.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T24.a–e each present and passing (T24.e passing means "measured and recorded," not
      necessarily "under budget" — see §9's own honest-recording framing).
- [ ] Direct code read: `dsr_p`'s finite-mode branch (`GAME_MODE == 0`) contains zero new
      instructions inserted between its existing entry and its existing `REGION_GRAPH` read.
- [ ] Direct code read: `check_zone_transition`'s existing four direction branches are reached
      only when `GAME_MODE == 0`; the new `GAME_MODE == 1` branch never falls through into them.
- [ ] Direct code read: `inf_ensure_window` calls `IP-1101`'s routine, never re-implements any
      part of it inline.
- [ ] FR-10200/NFR-4300/NFR-1400/GDS-07/RTM/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1101`** (this tranche's own materialization package, **NOT YET `VERIFIED`**) —
  `inf_ensure_window` calls it directly; `IP-1102` cannot reach `COMPLETE` before `IP-1101` does.
- **`IP-1030`/`FEAT-4100`** (`VERIFIED`) — `dsr_p`'s biome-dispatch half and `copy_screen`, reused
  unmodified.
- **`IP-9130`/`FEAT-2000`** (`VERIFIED`) — the `JOY_CUR`-gated intent-check convention
  `czt_infinite` reuses verbatim.

Independent of `IP-1100` (no shared file region touched by both — `IP-1100`'s own state-machine
work and this package's own render/navigate work are parallel-eligible once `IP-1101` is
`COMPLETE`). `IP-1103`/`IP-1104` both depend on this package (materialized window/render path
must exist before treasure collection or the ledger can be exercised end-to-end).

## 13. Risks

- **NFR-1400's actual measured result is unknown until T24.e runs** (Medium-High, carried
  forward from `FEAT-10000`'s own catalog Risk assessment) — this package's own Definition of Done
  explicitly does not require NFR-1400 to pass, only to be honestly measured and recorded; if the
  measurement shows a real stall risk, that becomes a new backlog finding for a follow-up package,
  not silently absorbed here.
- **`dsr_p`/`check_zone_transition` are both heavily-exercised, `VERIFIED` finite-mode routines**
  (Medium) — the supersession sweep (§7) found no other call site, but the new gate itself is a
  real, if small, change to shared code; T24.c's own byte-for-byte regression check is this
  package's own primary mitigation, not merely a spot check.
- ROM budget: two new subroutines (`inf_ensure_window`, `draw_region_arrows_inf`) plus small gate
  branches in two existing routines — modest addition, expected well within existing headroom
  (re-affirmed at build time).

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `dsr_p`/`check_zone_transition`'s new
`GAME_MODE` gates are removed along with everything else this package adds — the finite mode's own
paths, never modified inline (only gated around), are unaffected either way. No `GDS-07` delta
survives a revert (this package's own addition). No save-format change in this package
(`IP-1104`'s scope).
