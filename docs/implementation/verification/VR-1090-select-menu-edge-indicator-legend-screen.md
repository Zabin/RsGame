# VR-1090 — SELECT Menu & Edge-Indicator Legend Screen

> Independent verification of
> [IP-1090](../packages/IP-1090-select-menu-edge-indicator-legend-screen.md), performed by
> `09-package-verification` in a fresh session (the same-session-independence rule blocked
> verification in the implementing session, 2026-07-13).

## Package

- **ID:** IP-1090
- **Title:** SELECT Menu & Edge-Indicator Legend Screen
- **Commit implemented:** `4698faa` ("feat(IP-1090): SELECT Menu & Edge-Indicator Legend Screen")
- **Commit verified against:** `14c3468` (`main`, post-PR #20 merge; no further changes to the
  package's files since `4698faa`)

## Result

**VERIFIED** — 0 failed checks, 0 findings requiring remediation.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| All seven FS-109 Acceptance Criteria demonstrably pass via T21 | `T21.a1`/`a2a`/`a2b` (AC-1/AC-2), `T21.b` (AC-3), `T21.c` (AC-4), `T21.d1`/`d2` (AC-5), `T21.e0`/`e` (AC-6), `T21.f1`/`f2`/`f3` (AC-7) — all 12 checks `[PASS]` in a fresh 246/246 suite run this session. | PASS |
| ROM builds at 32768 bytes; full suite passes | `python3 build_rom.py BunnyQuest.gbc` this session: "Wrote 32768 bytes → BunnyQuest.gbc" (25544/32768 used, matching the package's own reported figure); `python3 test_rom.py`: **246/246 passed, 0 failed**. | PASS |
| T4.6/T8.11/T14.e2 corrected for the new two-hop SELECT path and passing | Read each site directly (`test_rom.py:300-302`, `698-700`, `1367-1374`): each now presses `select` then `a` (SELECT MENU → MAP) before its `GAMESTATE`/seed-immutability assertion; all three `[PASS]` in this session's suite run. | PASS |
| `st_map`'s own pre-existing SELECT==B merge confirmed byte-for-byte unchanged | Direct code read, `asm_game.py:373-378` (`st_map` label through its `end_frame` jump): identical shape to the package's own quoted pre-`IP-1090` text (`AND_n((1<<J_B)\|(1<<J_SELECT))` gate, unconditional transition to `GS_PLAYING`) — no `IP-1090` diff hunk touches this range (`git diff 4698faa~1 4698faa -- asm_game.py` confirms the nearest hunk is `handle_play_input`'s SELECT branch, ~200 lines away). | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | See DoD row above; T1 header suite (part of the 246/246 run) confirms header validity. | PASS |
| G5: full `test_rom.py` suite passes | **246/246 passed, 0 failed** (fresh PyBoy 2.7.0 + Pillow install this session — neither present in the container at session start), matching the package's own reported count exactly. | PASS |
| T21.a1–g each present and passing | All 12 checks enumerated above, each mapped 1:1 to FS-109 AC-1…7 plus the T4.6/T8.11/T14.e2 corrected-path confirmation (T21.g, structural — same-run co-execution). | PASS |
| Direct code read: `handle_play_input`'s SELECT branch now targets `GS_SELECT_MENU`, not `GS_MAP`; `st_map` itself byte-for-byte unchanged | `asm_game.py:582-589`: `BIT_b_B(J_SELECT)` branch writes `GS_SELECT_MENU` to `TRANSITION_TO`, sets `NEED_REDRAW` and `MM_JUST_ENTERED`. `st_map` unchanged, see DoD row above. | PASS |
| Direct code read: `st_select_menu`'s B-cancel writes only `TRANSITION_TO`/`NEED_REDRAW` — no `MM_CURSOR`/`MM_JUST_ENTERED` write on cancel | `asm_game.py:505-508` (`sm_check_b` through its `end_frame` jump): exactly two writes, `TRANSITION_TO = GS_PLAYING` and `NEED_REDRAW = 1` — no `MM_CURSOR`/`MM_JUST_ENTERED` write anywhere in that branch. Confirmed empirically by `T21.d2`'s live WRAM diff (0 changed fields). | PASS |
| Direct code read: `MM_CURSOR`/`MM_JUST_ENTERED` reuse does not corrupt MAIN MENU's own behavior | Every `GAMESTATE → GS_MAIN_MENU` transition site (`sv_sel`, `asm_game.py:367`, plus `st_main_menu`'s own internal paths) and every `GAMESTATE → GS_SELECT_MENU` site (`handle_play_input`'s SELECT branch, the only one) confirmed by grep to set `MM_JUST_ENTERED = 1` on entry — no path re-enters either state with a stale cursor value from a visit to the other. Structural, not spot-checked. | PASS |
| GDS-07/FR-1200/FR-1210/RQ-04/`FEAT-1200`/Master-Build-Plan deltas applied exactly as §9 names | `docs/architecture/07-data-model.md:73,74,76` — `MM_SAVE_VALID`/`MM_CURSOR` rows backfilled, `MM_JUST_ENTERED` row extended, both crediting `IP-1090`. `docs/requirements/01-functional-requirements.md:353,394` — FR-1200/FR-1210 both "Implemented — 2026-07-13, `IP-1090`". `docs/requirements/04-requirements-traceability-matrix.md:62,63` — FR-1200/FR-1210 rows filled (`FS-109`/`IP-1090`/T21+corrected-sites, "246/246 pass"). `docs/features/FS-109-…md` — Open Questions 1–3 (§19) all marked Resolved with `IP-1090`'s decisions; forward-reference metadata at top of file states "COMPLETE 2026-07-13". `docs/feature-planning/03-feature-catalog.md` and Master Build Plan / `packages/INDEX.md` rows all point at `IP-1090`, `COMPLETE` (pre-this-verification status, correctly reflecting the package's own state prior to this VR). | PASS |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-1200 | `asm_game.py:582-589` (SELECT branch retarget), `:496-518` (`st_select_menu`), `:1176-1182` (`sm_on_entry`), `:1184-1192` (`draw_select_menu_cursor`), `tilemaps.py:387-395` (`select_menu_screen`) | `T21.a1, a2a, a2b, b, c, d1, d2` plus corrected `T4.6/T8.11/T14.e2` | Filled: `asm_game.py, tilemaps.py` / `FS-109` / `IP-1090` / matching test list — confirmed matches the actual files/tests | PASS |
| FR-1210 | `asm_game.py:524-530` (`st_legend`), `tilemaps.py:397-410` (`legend_screen`) | `T21.e0, e, f1, f2, f3` | Filled: `asm_game.py, tilemaps.py` / `FS-109` / `IP-1090` / matching test list — confirmed | PASS |

## Test run

- `python3 build_rom.py BunnyQuest.gbc` → `Wrote 32768 bytes → BunnyQuest.gbc` (25544/32768 bytes
  used, exact match to the package's own reported figure, no overflow).
- `python3 test_rom.py` → **246/246 passed, 0 failed** (fresh PyBoy 2.7.0 + Pillow install this
  session — neither present in the container at session start, installed to run the gates, same
  precedent as `VR-9010`/`VR-1021`).
- Independent live drive (this session, not part of `test_rom.py`): real MAIN MENU → SEED/SCALE
  ENTRY → INTRO → PLAYING boot path, then PLAYING → SELECT (GS 2→8, `MM_CURSOR`=0/"map" default,
  screenshot confirms cursor glyph beside MAP) → DOWN (`MM_CURSOR`→1, screenshot confirms cursor
  glyph moved to LEGEND) → A (GS 8→9/LEGEND, screenshot confirms the real open-arrow tile beside
  "OPEN PATH", the real blocked-bar tile beside "MAZE BLOCKED," a genuinely blank cell beside
  "WORLD EDGE," and the "B: EXIT" footer — visually matching GDS-08 §11's content decision exactly,
  not merely the WRAM tile-index assertions `T21.f1–f3` already cover). No tunable/generated
  parameter (seed/scale) is referenced by this package's DoD — both new screens are static and
  state-machine-only, so this skill's tunable-parameter rule does not apply; the live drive above
  instead exercises the actual rendered content, which the suite's own WRAM-only assertions cannot.

## Scope audit

Diff (`4698faa~1..4698faa`) touches exactly `asm_game.py`, `build_rom.py`, `tilemaps.py`,
`test_rom.py`, `test_results.txt`, `BunnyQuest.gbc` (rebuilt binary), plus the named documentation
set (`docs/architecture/07-data-model.md`, `docs/feature-planning/03-feature-catalog.md`,
`docs/features/FS-109-…md`, `docs/features/INDEX.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/requirements/01-functional-requirements.md`,
`docs/requirements/04-requirements-traceability-matrix.md`, `ROADMAP.md`) — matches the package's
declared "Files to Create/Modify" (§6) and "Documentation Updates" (§9) exactly. No excursion into
`gbc_lib.py`, `worldgen.py`, `music.py`, or `map_screen()`'s own content (`tilemaps.py:358-376`,
confirmed unchanged by the same diff — only `select_menu_screen()`/`legend_screen()` and
`ALL_SCREENS`'s two new rows were added).

## Findings

| Finding | Severity | Owner |
|---|---|---|
| None requiring remediation. | — | — |

No new backlog entries filed by this verification — every claim in the package's Implementation
Summary and Definition of Done was independently re-derived from the tree, a fresh test run, and a
live screenshot-driven UI walkthrough, not taken on faith, and all held.
