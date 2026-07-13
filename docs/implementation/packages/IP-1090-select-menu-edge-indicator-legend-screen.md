# IP-1090 — SELECT Menu & Edge-Indicator Legend Screen

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1090` — implements
[**FS-109**](../../features/FS-109-select-menu-edge-indicator-legend-screen.md) (`FEAT-1200`,
Epic EP-1000, Release 2, `BL-0100`). Resolves FS-109 Open Questions 1–3 — see the
[Technical Work Breakdown](../01-technical-work-breakdown.md)'s "SELECT Menu & Edge-Indicator
Legend Screen" tranche.

## 2. Objective

Extend `PLAYING`'s `SELECT` press into a two-option cursor menu (`GS_SELECT_MENU`: "map"/
"legend") instead of jumping directly to `MAP`; add a new `GS_LEGEND` state, a single static
screen explaining the three transition-edge indicator states via the already-shipped
`TL_ARROW_U`/`TL_BLOCKED_U` tiles. `MAP` itself is untouched.

## 3. Requirements Covered

FR-1200, FR-1210 (FS-109's full Included-Requirements set).

## 4. Architecture Components

GDS-01 §4c (target-state game-flow delta — this package's exact source diagram: `SELECT` →
`SELECT MENU` → `MAP`/`LEGEND`, `B` cancels/exits directly to `PLAYING` from any of the three) ·
GDS-08 §11 (LEGEND's static three-row content: open-arrow tile / blocked-bar tile / blank, each
beside a plain-language label, footer "B: EXIT").

## 5. Interfaces

- **New `patches` dict keys** (GDS-09's `build_game_asm(rom) → patches dict` contract, cited
  verbatim: "a patch point for the seed/scale-entry screen's tile/attribute addresses, parallel
  to today's `title_t`/`title_a` pattern" — the same mechanism `IP-1040`'s `mm_t`/`mm_a`/`sse_t`/
  `sse_a` already extended): `sm_t`/`sm_a` (SELECT MENU screen) and `lg_t`/`lg_a` (LEGEND
  screen), following the existing pattern exactly.
- **`TL_ARROW_U`/`TL_BLOCKED_U`** (already ROM-resident since `IP-1030`/`IP-1081`) — LEGEND's
  screen-generator function places these existing tile indices directly via `_put()`; no new
  tile art, no new palette entry (GDS-08 §11).
- **`MM_CURSOR` (`0xC27E`) and `MM_JUST_ENTERED` (`0xC2D7`)** — reused, not newly allocated
  (this package's own resolution of FS-109 Open Question 1, see §13 Risks for the rationale).
  `MM_CURSOR` doubles as SELECT MENU's own two-option cursor (0="map", 1="legend"); a
  `GAMESTATE → GS_SELECT_MENU` transition sets `MM_JUST_ENTERED`, exactly mirroring how every
  existing `GAMESTATE → GS_MAIN_MENU` transition site already does, so `MM_CURSOR` resets to its
  default (0) on a genuine state entry but survives a same-state toggle-triggered redraw.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **Game-state constants** (`asm_game.py:174`, immediately after
    `GS_MAIN_MENU, GS_SEED_SCALE_ENTRY = 6, 7`): add `GS_SELECT_MENU, GS_LEGEND = 8, 9` — the
    next two free values per this project's own append-only `GAMESTATE` numbering convention
    (resolves FS-109 Open Question 2).
  - **Main dispatch loop** (`asm_game.py:291-298`): add two `CP_n(GS_x); JP_Z('st_x')` entries
    following the existing pattern, for `GS_SELECT_MENU`→`st_select_menu` and `GS_LEGEND`→
    `st_legend`.
  - **`handle_play_input`'s SELECT branch** (`asm_game.py:536-538`, currently
    `rom.BIT_b_B(J_SELECT); rom.JR_Z('hpi_no_sel') / rom.LD_A_n(GS_MAP); rom.LD_nn_A(TRANSITION_TO)`):
    retarget the transition from `GS_MAP` to `GS_SELECT_MENU`; add
    `rom.LD_A_n(1); rom.LD_nn_A(MM_JUST_ENTERED)` alongside the existing `NEED_REDRAW` write, so
    `MM_CURSOR` resets to "map" (0) on this genuine entry (mirroring `st_save`'s own
    exit-to-main-menu site, `asm_game.py:364`, which already sets `MM_JUST_ENTERED` the same way
    for `GS_MAIN_MENU`). `st_map` itself (`asm_game.py:368-373`) is **not** modified — its own
    pre-existing `SELECT`==`B` exit-to-`PLAYING` merge is untouched, a different (downstream, not
    entry-path) behavior per the Technical Work Breakdown's supersession sweep.
  - **`st_select_menu` (new label)**: D-pad up/down toggles `MM_CURSOR` unconditionally between 0
    and 1 (no save-validity-style gate needed — both options are always offered, unlike MAIN
    MENU's conditional "continue"), following `mm_toggle`'s own `XOR_n(1)` toggle shape
    (`asm_game.py:406`) exactly. `A` confirms: `MM_CURSOR == 0` → `TRANSITION_TO = GS_MAP`;
    `MM_CURSOR == 1` → `TRANSITION_TO = GS_LEGEND`. `B` cancels: `TRANSITION_TO = GS_PLAYING`,
    writing nothing else (FR-1200's own Postconditions). `J_SELECT` is not tested by this
    handler — a plain no-op if pressed again while already in SELECT MENU (resolves FS-109 Open
    Question 3).
  - **`st_legend` (new label)**: checks only `J_B` → `TRANSITION_TO = GS_PLAYING`. No other input
    is tested (SELECT is a no-op here too, same resolution as SELECT MENU).
  - **`do_screen_redraw`'s dispatch list** (`asm_game.py:862-864`): add
    `(GS_SELECT_MENU,'dsr_sm'), (GS_LEGEND,'dsr_lg')` to the `for gs, lbl in [...]` list.
  - **Two new `_dsr_screen()` calls** (`asm_game.py:886-887` area, following `dsr_mm`/`dsr_sse`'s
    own shape): `_dsr_screen('dsr_sm', 'sm_t', 'sm_a', extra='sm_on_entry')` and
    `_dsr_screen('dsr_lg', 'lg_t', 'lg_a')` (LEGEND is fully static — no `extra`, unlike SELECT
    MENU which needs its cursor drawn/reset on every entry).
  - **`sm_on_entry` / `draw_select_menu_cursor` (new functions)**, mirroring `mm_on_entry`/
    `draw_menu_cursor` (`asm_game.py:1081-1108`) but without the save-validity gate (no label ever
    needs blanking — both "map" and "legend" are always offered): on entry, if `MM_JUST_ENTERED`
    is set, clear it and reset `MM_CURSOR` to 0; then call `draw_select_menu_cursor`, which blanks
    both cursor-glyph cells and writes `TL_ARROW_R` (the same highlight glyph `draw_menu_cursor`
    already uses) next to whichever row `MM_CURSOR` selects. New VRAM address constants for the
    SELECT MENU screen's own "map"/"legend" row-cursor cells, computed the same
    `0x9800 + row*32 + col` way as `MM_CURSOR_CONT_ADDR`/`MM_CURSOR_NEW_ADDR`.
- **Modify: `tilemaps.py`**:
  - **`select_menu_screen()` (new function)**: reuses `main_menu_screen()`'s own static-screen
    shape (`_blank`, title `_str`, two horizontal `TL_BORDER_H` rules, two label rows — "MAP" /
    "LEGEND" in place of "CONTINUE"/"NEW GAME") — same row positions `main_menu_screen()` already
    uses (rows 7/9), so `sm_on_entry`'s cursor-cell addresses can reuse
    `MM_CURSOR_CONT_ADDR`/`MM_CURSOR_NEW_ADDR`'s own row math directly (col offset differs only
    if the label text length differs).
  - **`legend_screen()` (new function)**: `_blank`, title "LEGEND", one horizontal `TL_BORDER_H`
    rule, three body rows each placing the real tile (`TL_ARROW_U` / `TL_BLOCKED_U` / nothing) via
    `_put()` beside its own `_str()` label ("OPEN PATH" / "MAZE BLOCKED" / "WORLD EDGE" — GDS-08
    §11's content, verbatim), footer `_str(... "B: EXIT" ...)`. No new tile constants needed —
    both `TL_ARROW_U`/`TL_BLOCKED_U` are already imported via `tilemaps.py`'s existing
    `from tiles import *`.
  - **`ALL_SCREENS`** (`tilemaps.py:388-401`): add `("select_menu", select_menu_screen)` and
    `("legend", legend_screen)` entries, parallel to the existing `main_menu`/`seed_scale_entry`
    rows.
- **Modify: `build_rom.py`** (`build_rom.py:157-161` area, following the `IP-1040` `mm_t`/`sse_t`
  comment's own pattern): add
  `p16(patches['sm_t'], screen_addrs['select_menu'][0])` / `p16(patches['sm_a'],
  screen_addrs['select_menu'][1])` / `p16(patches['lg_t'], screen_addrs['legend'][0])` /
  `p16(patches['lg_a'], screen_addrs['legend'][1])`.
- **Modify: `test_rom.py`**:
  - Add suite **T21** (see §8).
  - **Correct three existing sites** the Technical Work Breakdown's supersession sweep found,
    which simulate a bare `SELECT` press from `PLAYING` and assert an immediate
    `GAMESTATE == GS_MAP` (4) — each needs an inserted `A` press between the `SELECT` press and
    the `MAP`-state check, since `SELECT` now lands in `GS_SELECT_MENU` (8) first:
    - **T4.6** (`test_rom.py:297-298`): insert `pb.button('a'); [pb.tick() for _ in range(40)]`
      between the existing `select` press and the `GS==4` assertion.
    - **T8.11** (`test_rom.py:694-695`): same insertion.
    - **T14.e2** (`test_rom.py:1362-1366`): the "MAP: SELECT enters" step needs the same inserted
      `A` press; the subsequent "MAP: B" / re-enter / "MAP: SELECT" (exercising `st_map`'s own
      `SELECT`==`B` merge, unaffected by this package) steps are unchanged once the two-hop entry
      is corrected.

## 7. Implementation Tasks

Ordered: (1) `GS_SELECT_MENU`/`GS_LEGEND` constants + main-dispatch entries; (2)
`handle_play_input`'s SELECT-branch retarget + `MM_JUST_ENTERED` write; (3) `st_select_menu`
(toggle, A-confirm branches, B-cancel); (4) `st_legend` (B-only); (5) `do_screen_redraw` dispatch
entries + two new `_dsr_screen()` calls; (6) `sm_on_entry`/`draw_select_menu_cursor`; (7)
`select_menu_screen()`/`legend_screen()` + `ALL_SCREENS` registration; (8) `build_rom.py` patch
resolution; (9) rebuild ROM; (10) correct T4.6/T8.11/T14.e2 (§6); (11) author T21 (§8); (12) full
suite run; (13) documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T21: SELECT Menu & Edge-Indicator Legend Screen`**, implementing
FS-109's Verification Plan:

- **T21.a1** — from `GS_PLAYING`, press SELECT → assert `GameState == GS_SELECT_MENU` (8) and
  `MM_CURSOR == 0` ("map" default) (AC-1).
- **T21.a2** — press D-pad up (or down) → assert `MM_CURSOR == 1`; press again → assert
  `MM_CURSOR == 0` (AC-2), following T14's own `MM_CURSOR`-toggle assertion pattern.
- **T21.b** — with `MM_CURSOR == 0`, press A → assert `GameState == GS_MAP` (4) (AC-3).
- **T21.c** — from a fresh SELECT MENU entry, toggle to `MM_CURSOR == 1`, press A → assert
  `GameState == GS_LEGEND` (9) (AC-4).
- **T21.d** — from SELECT MENU (either `MM_CURSOR` value), press B → assert
  `GameState == GS_PLAYING`; snapshot WRAM before SELECT and after the B-cancel, assert no byte
  outside `MM_CURSOR`/`MM_JUST_ENTERED`/`NEED_REDRAW`/`TRANSITION_TO`/`GAMESTATE` changed (AC-5),
  mirroring T14's own SEED/SCALE-immutability diff-sweep pattern.
- **T21.e** — from LEGEND, press B → assert `GameState == GS_PLAYING` (AC-6).
- **T21.f** — with `GameState == GS_LEGEND`, read the rendered tilemap: assert the row-1 tile
  cell equals `TL_ARROW_U` adjacent to "OPEN PATH"'s label tiles, row-2 equals `TL_BLOCKED_U`
  adjacent to "MAZE BLOCKED", row-3's tile cell is blank (`TL_BG_BLANK`) adjacent to "WORLD EDGE"
  (AC-7) — a direct tilemap-content assertion, following T20's own tilemap-inspection pattern for
  the live MAP indicator tiles (Inspection, per FS-109's own Verification Method).
- **T21.g** — re-run T4.6/T8.11/T14.e2's corrected two-hop paths (§6) as part of the full suite,
  confirming the correction itself, not just the new states in isolation.

## 9. Documentation Updates

- `docs/architecture/07-data-model.md` (GDS-07): backfill missing WRAM-table rows for
  `MM_SAVE_VALID` (`0xC27D`) and `MM_CURSOR` (`0xC27E`) — referenced by `IP-1040`/`IP-9060` but
  never entered in the table — and extend `MM_JUST_ENTERED`'s existing row (`0xC2D7`) to note its
  reuse by every `GAMESTATE → GS_SELECT_MENU` transition site as well, not `GS_MAIN_MENU` alone.
- `docs/requirements/01-functional-requirements.md`: FR-1200/FR-1210 status → Implemented (a
  metadata note, not a rewrite of either requirement's text).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-1200/FR-1210 rows → `IP-1090`/
  T21.
- `docs/features/FS-109-…md` metadata: implemented-by pointer; §19 Open Questions 1–3 marked
  Resolved with this package's decisions (byte reuse, `GAMESTATE` values 8/9, SELECT-as-no-op).
- `docs/feature-planning/03-feature-catalog.md`: `FEAT-1200`'s forward-reference metadata →
  points at `IP-1090`.
- Master Build Plan status row; `packages/INDEX.md` row; `ROADMAP.md` FS-101+/IP-xxxx rows.

## 10. Definition of Done

- All seven FS-109 Acceptance Criteria demonstrably pass via T21.
- ROM builds at 32768 bytes; full suite passes.
- T4.6/T8.11/T14.e2 corrected for the new two-hop SELECT path and passing (§6).
- `st_map`'s own pre-existing SELECT==B merge confirmed byte-for-byte unchanged (direct code
  read — this package must not touch `asm_game.py:368-373`).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T21.a1–g each present and passing (map 1:1 to FS-109 AC-1…7 plus the corrected-path
      confirmation).
- [ ] Direct code read: `handle_play_input`'s SELECT branch now targets `GS_SELECT_MENU`, not
      `GS_MAP`; `st_map` itself is byte-for-byte unchanged.
- [ ] Direct code read: `st_select_menu`'s B-cancel writes only `TRANSITION_TO`/`NEED_REDRAW` —
      no `MM_CURSOR`/`MM_JUST_ENTERED` write on cancel (confirms FR-1200's "writing nothing"
      Postcondition).
- [ ] Direct code read: `MM_CURSOR`/`MM_JUST_ENTERED` reuse does not corrupt MAIN MENU's own
      behavior — no reachable path re-enters `GS_MAIN_MENU` with a stale `MM_CURSOR` value left
      over from a SELECT MENU visit (both states always set `MM_JUST_ENTERED` on their own
      entry, so this is a structural guarantee, not a spot check — confirm by direct read that
      every `GAMESTATE → GS_MAIN_MENU` and every `GAMESTATE → GS_SELECT_MENU` transition site
      sets `MM_JUST_ENTERED`).
- [ ] GDS-07/FR-1200/FR-1210/RQ-04/`FEAT-1200`/Master-Build-Plan deltas applied exactly as §9
      names.

## 12. Dependencies

`FEAT-1000`'s existing state machine (as-built, shipped Baseline, no dedicated `IP-xxxx`);
**IP-1040** (`VERIFIED`) — the cursor-menu convention (`MM_CURSOR`-toggle shape, `mm_on_entry`/
`draw_menu_cursor` pattern) this package reuses directly, plus the WRAM bytes (`MM_CURSOR`,
`MM_JUST_ENTERED`) it reuses; **IP-1030** and **IP-1081** (both `VERIFIED`) — the already-shipped
`TL_ARROW_U`/`TL_BLOCKED_U` tiles LEGEND displays (a content dependency, not a build-order one).

Independent of `IP-1082` (its own still-pending independent verification does not block this
package — disjoint files, `draw_region_arrows` vs. this package's `handle_play_input`/new state
handlers) and independent of the still-undecided `BL-0082` streaming-generation thread.

## 13. Risks

- **`MM_CURSOR`/`MM_JUST_ENTERED` reuse (this package's own resolution of FS-109 Open Question
  1)** is a confident implementation choice, not upstream-mandated — valid because `GS_MAIN_MENU`
  and `GS_SELECT_MENU` are never simultaneously active and no transition connects them directly
  (each always sets `MM_JUST_ENTERED` on its own entry, resetting `MM_CURSOR` before either
  state's own logic reads it). If a future design pass wants either state to remember its cursor
  position across an intervening visit to the other, this reuse would need revisiting — a
  narrow, well-isolated risk, not a structural one.
- **Three existing tests need correction, not just addition** (T4.6/T8.11/T14.e2) — mitigated by
  naming the exact insertion (§6/§8) rather than leaving it for `08-code-implementation` to
  rediscover via test failures, the same discipline `IP-1082`'s own package should have applied
  up front (that package's T20.b/e correction was found *during* implementation instead).
- ROM budget: two new static screens (SELECT MENU, LEGEND), no new tile art — modest addition
  (comparable to `IP-1040`'s own two-screen addition, ~2.3 KB combined tile+attribute data),
  expected well within the current ~9.7 KB of free ROM space (re-affirmed against `NFR-4000` at
  build time, not asserted here).

## 14. Rollback Considerations

Revert `asm_game.py`/`tilemaps.py`/`build_rom.py`/`test_rom.py` changes and rebuild. Reverts to
the shipped single-hop SELECT→MAP behavior exactly (T4.6/T8.11/T14.e2 revert to their
pre-`IP-1090` form alongside the rest). No save-format change in this package (FS-109 §14: no
SRAM/checksum obligation) — existing saves remain loadable by the reverted-from build unchanged.
