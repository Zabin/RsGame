# IP-1082 — Maze-Blocked Edge Indicator (render)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1082` — implements the render half of
[**FS-108**](../../features/FS-108-maze-aware-transition-edge-signaling.md) (`FEAT-2100`, Epic
`EP-1000`, Release 2 post-ship addendum) — the last unimplemented piece of this Feature and the
resolution path for `BL-0075`. Content half (the 4 new tile bitmaps this package draws): **IP-1081**
(paired package, same FS; this package depends on it). Classification logic this package's render
decision reads: **IP-1080** (`VERIFIED`, unmodified by this package).

## 2. Objective

Extend `draw_region_arrows` (`asm_game.py`) so that, for each direction `IP-1080`'s own
classification arithmetic already identifies as **blocked**, the routine draws the corresponding
new indicator tile (`IP-1081`'s `TL_BLOCKED_U/D/L/R`) at that direction's existing screen
position — closing FS-108's own Acceptance Criteria 4/5 (Workflow C) and resolving `BL-0075`'s
player-facing symptom (a maze dead-end currently reading identically to a true world edge).

## 3. Requirements Covered

FR-2330 — the render-time-decision half of the rendered-appearance obligation (drawing
`IP-1081`'s art in the correct case). Together with `IP-1080` (classification) and `IP-1081`
(art), this package closes FR-2330's full Description; no other package touches this requirement.

## 4. Architecture Components

[GDS-08 §10](../../architecture/08-presentation-architecture.md) (confirms `ARROW_ADDR_*` is the
correct screen position for the blocked indicator too — "only one of the two states is ever drawn
per edge") · `ADR-0012` point 2 (why the classification this package renders exists at all) ·
GDS-09 (`draw_region_arrows`'s existing loop shape, extended in place, same convention `IP-1080`
already used).

## 5. Interfaces

- **`REGION_GRAPH`'s existing confirmed layout** — unchanged, read-only, same access `IP-1080`
  already established.
- **`DRA_ROW`/`DRA_COL`** (`0xC2D8`–`0xC2D9`, `IP-1080`) — read-only, this package's own new
  branch reads these (already populated once per `draw_region_arrows` call) rather than
  recomputing them.
- **`ARROW_ADDR_U`/`D`/`L`/`R`** (`asm_game.py:944-947`) — reused verbatim as the blocked
  indicator's own screen position; no new constant.
- **`_arrow_write`** (`asm_game.py:957-963`) — the existing write helper (bank-toggled tile-index
  write + palette-2 attribute write) is reused as-is, called with the new tile constant instead
  of a new helper being written — it already takes `(addr, tile)` as parameters, no signature
  change needed.
- **`TL_BLOCKED_U`/`D`/`L`/`R`** (`IP-1081`, `tiles.py`) — the only new symbol this package's own
  branch references; not defined by this package.
- **No new `patches` dict key** — this is a pure control-flow extension inside an already-patched
  routine.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`draw_region_arrows`** (`asm_game.py:965`, extended by `IP-1080` at the `dra_div_*`/`B`–`E`
    load region, `asm_game.py:987-1013`): within each of the four existing per-direction branches
    (`dra_no_up`/`dra_no_down`/`dra_no_left`/`dra_no_right`, the `0xFF`-neighbor case), insert the
    blocked-vs-absent test `IP-1080`'s own Files-to-Modify commentary already named but did not
    implement as a render branch (`asm_game.py` comment at line 982-983: "Both remain no-op
    render-wise for this package's own scope"): using `DRA_ROW`/`DRA_COL` (already populated) and
    `WORLD_SCALE`, test `row > 0` (up) / `row < WORLD_SCALE - 1` (down) / `col > 0` (left) /
    `col < WORLD_SCALE - 1` (right, the corrected minimum WORLD_SCALE-1 bound already established
    by the SM83 `CP`/`JR` idiom `check_zone_transition` used pre-`IP-9050`, per `FS-108` §6 step
    4's own citation) — the exact per-direction grid-adjacency test `FS-108` §6/§7 specifies. If
    true (grid-adjacent, hence **blocked**): call `_arrow_write(ARROW_ADDR_<dir>,
    TL_BLOCKED_<dir>)` — the same call shape the open-edge branch already uses one label up,
    just the new tile constant. If false (**absent**): no write, exactly as today.
  - **No change** to the existing open-edge branches (`dra_no_up`'s sibling live-neighbor path
    etc.) — `FR-2320`'s rendering stays byte-for-byte unchanged, per `FS-108` §4's own boundary.
  - **No new WRAM address** — `DRA_ROW`/`DRA_COL`/`WORLD_SCALE` all already exist; this package
    only reads them.
- **Modify: `test_rom.py`** — extend the existing **T20** suite (no new suite number, per the
  TWBS's own supersession-sweep finding): add the blocked-tile-index assertion to `T20.b`'s
  existing per-region/per-direction sweep (§8), and add new **T20.e** for the open-case
  non-regression check (FS-108 AC-5).
- **No change to `tiles.py`** beyond what `IP-1081` already adds (this package references
  `IP-1081`'s constants, does not define them) and **no change to `worldgen.py`** (presentation
  layer, no generation counterpart, same as `IP-1080`'s own precedent).

## 7. Implementation Tasks

**Verb inventory:** pure **render** — `generate`/`navigate` are closed upstream scope
(`IP-1070`/`IP-9050`, unmodified); `persist` doesn't apply; `review` **does** apply once this
package ships (new visible art actually renders in-game for the first time) — a
`09-content-review` pass is owed after this package, named explicitly as this package's own
completion-summary Next Step, not silently assumed covered by `IP-1081`'s own DoD.

**Supersession sweep:** this package extends, not retires, `draw_region_arrows`'s existing
`0xFF`-branch shape (`IP-1080` already extended it once, from a bare no-op to a classification
computation; this package adds the render decision that computation was missing). Swept
`test_rom.py`'s `T20.b`/`T20.c` for any assertion that assumes "blocked" stays a permanent no-op:
found `T20.b`'s own `arrow_present` check (line 2086: `if not row_col_ok or arrow_present`) already
treats *any* non-blank tile at a blocked position as a failure — that assertion must be corrected,
not merely extended, since a blocked position drawing the new blocked tile is now the *correct*
outcome, not a regression (`T20.c`'s absent-case assertion is unaffected — absent still means "no
write," genuinely unchanged). Recorded as this package's own required `test_rom.py` edit (§6), not
a hidden side effect.

Ordered: (1) confirm `IP-1081` has shipped and reached `VERIFIED` (hard dependency, §12); (2) add
the blocked/absent render branch inside `draw_region_arrows`'s existing `0xFF` cases; (3) correct
`T20.b`'s own assertion (blocked now expects the new tile, not "no arrow") and add `T20.e`
(open-case non-regression); (4) rebuild ROM; (5) full suite run; (6) documentation/traceability
updates (§9); (7) flag the follow-on `09-content-review` need in the completion summary.

## 8. Tests to Add

Extends the existing **T20** suite (no new suite number):

- **`T20.b` corrected** (FS-108 AC-4): for every corpus entry, every region/direction classified
  `blocked`, assert the tile at `ARROW_POS[direction]` equals the direction's new
  `TL_BLOCKED_<dir>` constant — replacing the current "no arrow present" assertion (which becomes
  the *wrong* expectation once this package ships) with the correct positive assertion.
- **T20.e — open-case non-regression** (FS-108 AC-5): for every corpus entry, every
  region/direction classified `open`, assert the tile at `ARROW_POS[direction]` still equals the
  existing `TL_ARROW_<dir>` constant — confirming the new blocked-branch addition does not leak
  into or regress the unrelated open-edge branch.
- **`T20.c` unchanged** — absent case still asserts no write; this package's own branch produces
  identical output for that case (§6), so no update needed, confirmed by direct trace not assumed.
- **Exact pixel-bitmap correctness remains out of `test_rom.py`'s scope** (FS-108 §16) — the
  follow-on `09-content-review` pass judges craft, this suite only confirms *which* tile index is
  written.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-2330 Notes → rendering half implemented,
  citing `IP-1081`/`IP-1082`, superseding the "both cases remain visually identical no-ops" note.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-2330 row → adds `IP-1081`,
  `IP-1082`, `T20.b` (corrected)/`T20.e`.
- `docs/features/FS-108-…md` metadata: implemented-by pointer for the render half; AC-4/AC-5
  flipped from "specified, not yet implemented" to implemented (pending this package's own
  `VERIFIED` status, not asserted prematurely).
- Master Build Plan status row.

## 10. Definition of Done

- Every region/direction classified `blocked` (by `IP-1080`'s own unmodified arithmetic) renders
  the correct directional `TL_BLOCKED_*` tile at its existing screen position, palette 2.
- Every region/direction classified `open` still renders the existing `TL_ARROW_*` tile, unchanged.
- Every region/direction classified `absent` still renders nothing, unchanged.
- `T20.b` (corrected) and `T20.e` (new) both pass; `T20.a`/`T20.c`/`T20.d` unchanged and still pass.
- `IP-1080`'s own classification arithmetic (`DRA_ROW`/`DRA_COL`, the four grid-adjacency
  comparisons) is read, not modified.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct diff: `asm_game.py`'s open-edge branches (the non-`0xFF` case) byte-for-byte
      unchanged.
- [ ] Direct diff: `IP-1080`'s own `DRA_ROW`/`DRA_COL` computation (`dra_div_loop`/`dra_div_done`)
      unchanged — this package reads, never writes, those bytes.
- [ ] `T20.b` confirmed corrected (positive tile-index assertion, not "no arrow"); `T20.e`
      confirmed new and passing.
- [ ] `FR-2330`'s full Description (classification + rendered appearance) confirmed satisfied —
      no remaining "not yet closeable" clause on this requirement.
- [ ] Flag in the completion summary: a `09-content-review` pass is owed next (new visible art,
      first exercise for these 4 tiles) — not silently treated as this package's own scope.

## 12. Dependencies

- **`IP-1081`** (must reach `VERIFIED`, not merely `COMPLETE`, per this skill's own `READY`
  convention — the tile constants this package's branch references must exist) — hard
  prerequisite, this pairing's own critical path.
- **`IP-1080`** (`VERIFIED`) — the classification arithmetic (`DRA_ROW`/`DRA_COL`, the neighbor-
  byte loads) this package's own branch is inserted next to; read-only dependency, no conflict.
- **`IP-1070`** (`VERIFIED`, transitively) — the maze pass that makes the `blocked` case reachable
  at all in any real generated world; already a dependency of `IP-1080`, carried forward.

## 13. Risks

Low — a small, well-isolated control-flow addition inside an already-`VERIFIED` routine's existing
branch structure, reusing every constant/helper it needs rather than inventing new ones. The one
real risk is the `T20.b` assertion-correction itself (§7) — a package that only *adds* a check
without correcting the now-incorrect existing one would leave a permanently-failing test, caught
by this package's own Verification Checklist item naming the correction explicitly, not left
implicit.

## 14. Rollback Considerations

Revert `asm_game.py`'s new branch and `test_rom.py`'s `T20.b` correction/`T20.e` addition, rebuild.
No save-format dependency (pure presentation-layer render logic, touches no WRAM/SRAM). `IP-1081`'s
own tile data can remain in the tree independent of this rollback (inert without this package's
render branch calling it) or be rolled back together, at the rollback's own discretion.
