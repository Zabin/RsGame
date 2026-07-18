# IP-1120 — Infinite Mode Combat: Mode Gating & UI

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1120` — implements part of [**FS-112**](../../features/FS-112-infinite-mode-combat-sub-mode.md)
(`FEAT-11000`, Epic `EP-6000`, `Future` bucket). Covers Workflow A (the `gate` verb) — resolves
`FS-112`'s own Open Question 1, per [GDS-01 §4e](../../architecture/01-concept-of-play.md#4e-infinite-mode-combat-sub-modes-own-gating-confirmation--delta-for-bl-0146-decided-2026-07-17)
(`BL-0146`).

## 2. Objective

Add a new `COMBAT MODE CONFIRM` state — a binary Y/N cursor choice, defaulting to N — reached
only after choosing Infinite Mode on `MODE SELECT`, that sets the `COMBAT_MODE` WRAM flag
`IP-1121` defines before proceeding to `INFINITE SEED ENTRY`. `MODE SELECT`'s own two options and
the finite path are both completely unaffected.

## 3. Requirements Covered

FR-11100 (combat sub-mode entry) in full — the UI-gating half; the flag's own existence/boot-clear
is `IP-1121`'s scope (see that package's §2), this package is the sole writer of a nonzero value
into it.

## 4. Architecture Components

[GDS-01 §4e](../../architecture/01-concept-of-play.md#4e-infinite-mode-combat-sub-modes-own-gating-confirmation--delta-for-bl-0146-decided-2026-07-17)
(target state, decided 2026-07-17) · `R218` (difficulty-gated-optional-content precedent — an
explicit, clearly-signposted choice, never a hidden toggle).

## 5. Interfaces

- **The existing `GS_MODE_SELECT` state's `ms_infinite` branch** (`asm_game.py`, `IP-1100`,
  currently transitions directly to `GS_INFINITE_SEED_ENTRY` after setting `GAME_MODE=1`) —
  retargeted to the new `GS_COMBAT_MODE_CONFIRM` state instead. `MODE SELECT`'s own `MM_CURSOR`
  toggle and its "finite" branch (`ms_check_a`'s `GS_SEED_SCALE_ENTRY` target) are both completely
  unchanged.
- **The existing cursor-menu pattern** (`MAIN MENU`/`SELECT MENU`/`MODE SELECT` — UP/DOWN toggles
  a cursor byte, A confirms, B cancels one step back) — reused verbatim for the new state, per
  `GDS-01` §4e's own explicit framing ("not a new UI convention").
- **`st_infinite_seed_entry`** (`IP-1100`, unchanged) — this package's new state's own A-confirm
  transitions into it exactly as `ms_infinite` used to, once `COMBAT_MODE` is set/left as chosen.
- **`IP-1121`'s `COMBAT_MODE`** (`0xC6B5`, boot-cleared to 0 by that package) — this package is
  the sole call site that ever writes `1` into it.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New `GAMESTATE` constant** (next free value following `GS_INFINITE_SEED_ENTRY = 11`, per
    this project's own append-only numbering convention): `GS_COMBAT_MODE_CONFIRM = 12`, added
    alongside the existing `GS_MODE_SELECT, GS_INFINITE_SEED_ENTRY = 10, 11` line.
  - **New WRAM constant** (first unclaimed byte past `IP-1123`'s own `COMBAT_ENTRY_Y` end,
    `0xC6DC`): `CMC_CURSOR = 0xC6DD` (1 byte — this state's own Y/N cursor; **not** a reuse of
    `MM_CURSOR`, since `MODE SELECT`'s own cursor value ("infinite") must survive a B-cancel
    round trip through this new state and back, unlike `MM_CURSOR`'s existing reuse across
    `MAIN MENU`/`SELECT MENU`/`MODE SELECT`, which are never simultaneously reachable from one
    another the way this state's own B-cancel target is).
  - **Main state dispatch** (`handle_input`'s per-`GAMESTATE` `CP_n`/`JP_Z` chain, alongside the
    existing `GS_INFINITE_SEED_ENTRY` line): new
    `rom.CP_n(GS_COMBAT_MODE_CONFIRM); rom.JP_Z('st_combat_mode_confirm')`.
  - **`ms_infinite`** (the `GS_MODE_SELECT` branch reached when `MM_CURSOR != 0`): its existing
    `GS_INFINITE_SEED_ENTRY` transition target changes to `GS_COMBAT_MODE_CONFIRM`; also resets
    `CMC_CURSOR = 0` on this transition (defaults to "N" every time this state is freshly entered,
    per `GDS-01` §4e's own "never defaults to enabled" requirement — not a boot-only clear, since
    the player can retry this state multiple times in one boot via repeated B-cancel/re-entry).
    `GAME_MODE = 1` is still set here, unchanged — the combat confirm is reached only after
    already committing to Infinite Mode.
  - **New state handler `st_combat_mode_confirm`** — mirrors `st_mode_select`'s own UP/DOWN-
    toggle/A-confirm/B-cancel shape exactly:
    - UP or DOWN: `CMC_CURSOR ^= 1`, set `NEED_REDRAW`, `JP('end_frame')` (mirrors `ms_toggle`).
    - B: transition to `GS_MODE_SELECT` — **does not** write `MM_JUST_ENTERED` (mirrors
      `st_infinite_seed_entry`'s own identical B-cancel precedent exactly, so `MODE SELECT`'s own
      `MM_CURSOR` stays on "infinite" rather than resetting to "finite"). Does **not** reset
      `GAME_MODE` back to 0 — the player is still returning to a state reached only via the
      Infinite Mode path.
    - A: if `CMC_CURSOR == 0` ("N"), leave `COMBAT_MODE` at its existing boot-cleared 0; if
      `CMC_CURSOR != 0` ("Y"), `LD_A_n(1); LD_nn_A(COMBAT_MODE)`. Either way, transition to
      `GS_INFINITE_SEED_ENTRY` (`st_infinite_seed_entry`, `IP-1100`'s own unmodified state).
  - **`do_screen_redraw`'s per-state dispatch table**: new entry
    `(GS_COMBAT_MODE_CONFIRM, 'dsr_cmc')` alongside the existing `(GS_INFINITE_SEED_ENTRY,
    'dsr_ise')` row; new `_dsr_screen('dsr_cmc', 'cmc_t', 'cmc_a', extra='cmc_on_entry')` call
    (mirroring `dsr_ms`'s own shape exactly).
  - **New subroutine `cmc_on_entry`/`draw_combat_confirm_cursor`** — mirrors `ms_on_entry`/
    `draw_mode_select_cursor` exactly: on a genuine state entry (`MM_JUST_ENTERED` set — this
    package's own transition into the state, via `ms_infinite`'s retarget, still uses the existing
    `MM_JUST_ENTERED` convention for the "reset on genuine entry, preserve on same-state redraw"
    rule, even though the cursor byte itself is `CMC_CURSOR` not `MM_CURSOR`), reset
    `CMC_CURSOR = 0`; always redraw the cursor glyph at whichever row `CMC_CURSOR` currently
    selects, blanking the other row first (two fixed VRAM addresses, mirroring
    `MS_CURSOR_FINITE_ADDR`/`MS_CURSOR_INFINITE_ADDR`'s own construction:
    `CMC_CURSOR_NO_ADDR = 0x9800 + 7*32 + 6`, `CMC_CURSOR_YES_ADDR = 0x9800 + 9*32 + 6`, matching
    `combat_mode_confirm_screen()`'s own row/column layout below).
- **Modify: `tilemaps.py`**:
  - **New screen function `combat_mode_confirm_screen()`** — mirrors `mode_select_screen()`'s own
    layout exactly (reuses existing font tiles/palette 2, zero new tile art or palette entries):
    title "ENABLE COMBAT MODE?" (row 3), "NO" (row 7, col 8), "YES" (row 9, col 8), the same
    top/bottom border rows (2/14) `mode_select_screen()` already draws.
  - `ALL_SCREENS`: one new entry for `combat_mode_confirm_screen`, alongside the existing
    `mode_select_screen`/`infinite_seed_entry_screen` UI entries (this project's established
    "code owns the state machine, this same package also owns a small, font-only new screen"
    precedent — `IP-1090` shipped its own new `LEGEND` screen inside a single, code-owned package
    the same way, since the content here is plain text reusing existing tiles, not new pixel art
    warranting a `08-content-authoring` split).

## 7. Implementation Tasks

Ordered: (1) `GS_COMBAT_MODE_CONFIRM`/`CMC_CURSOR` constants; (2) `ms_infinite`'s retarget +
`CMC_CURSOR` reset; (3) `st_combat_mode_confirm`'s UP/DOWN/A/B handling; (4)
`combat_mode_confirm_screen()` (`tilemaps.py`) + `ALL_SCREENS` entry; (5) `do_screen_redraw`
dispatch entry + `cmc_on_entry`/`draw_combat_confirm_cursor`; (6) rebuild ROM; (7) author new
suite; (8) full suite run (including a direct `T25` re-run, unmodified); (9) documentation updates
(§9).

## 8. Tests to Add

New `test_rom.py` suite **`T33: Combat Sub-Mode — Mode Gating & UI`**:

- T33.a — off by default: drive a fresh new-game Infinite Mode entry through `COMBAT MODE
  CONFIRM` without pressing UP/DOWN, confirm A immediately at the default "N" cursor position
  leaves `COMBAT_MODE == 0`.
- T33.b — confirm sets the flag: toggle to "Y" (one UP or DOWN press), press A, confirm
  `COMBAT_MODE == 1` and `GAMESTATE == GS_INFINITE_SEED_ENTRY`.
- T33.c — B-cancel returns to `MODE SELECT` with "infinite" still highlighted: from `COMBAT MODE
  CONFIRM`, press B, confirm `GAMESTATE == GS_MODE_SELECT` and `MM_CURSOR != 0` (still
  "infinite", not reset to "finite").
- T33.d — re-entry resets to "N": re-enter `COMBAT MODE CONFIRM` a second time (via `MODE
  SELECT` → "infinite" again) after having left it toggled to "Y," confirm `CMC_CURSOR == 0` on
  the fresh entry (never carries a stale "Y" forward).
- T33.e — finite path unaffected: drive `MODE SELECT` → "finite," confirm `GAMESTATE ==
  GS_SEED_SCALE_ENTRY` directly, no detour through `COMBAT MODE CONFIRM`, `COMBAT_MODE`
  unaffected.
- T33.f — `T25` non-regression: re-run `T25`'s own existing checks unmodified, confirming `MODE
  SELECT`/`INFINITE SEED ENTRY`'s own prior behavior is byte-for-byte unchanged by this delta.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11100 status → Implemented.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11100 row → `IP-1120`/T33.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: Open Question 1 marked
  Resolved (`GDS-01` §4e, `IP-1120`).
- `docs/architecture/07-data-model.md` (or WRAM quick-reference): new `CMC_CURSOR` row,
  `0xC6DD`; new `GAMESTATE` row, `GS_COMBAT_MODE_CONFIRM = 12`.
- Master Build Plan status row; `packages/INDEX.md` status → `NOT STARTED` (unblocked).

## 10. Definition of Done

- `COMBAT MODE CONFIRM` defaults to "N," correctly sets `COMBAT_MODE` on "Y" confirm, B-cancels
  cleanly back to `MODE SELECT` with "infinite" still highlighted, and resets to "N" on every
  fresh entry (T33.a–d all passing).
- The finite path and `T25`'s own prior behavior are completely unaffected (T33.e/f).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, including `T25` unmodified.
- [ ] T33.a–f each present and passing.
- [ ] Direct code read: `ms_check_a`'s "finite" branch (`GS_SEED_SCALE_ENTRY` target) is
      byte-for-byte unchanged from `IP-1100`'s own shipped form.
- [ ] Direct code read: `st_infinite_seed_entry` itself is unmodified — this package's new state
      only redirects into it, never edits its own body.
- [ ] FR-11100/RTM/`FS-112`-metadata/Master-Build-Plan/`packages/INDEX.md` deltas applied exactly
      as §9 names.

## 12. Dependencies

- **`IP-1121`** — the `COMBAT_MODE` flag this package sets.
- **`IP-1100`** (`VERIFIED`) — `GS_MODE_SELECT`/`ms_infinite`/`st_infinite_seed_entry`, extended
  (one retargeted transition) not replaced.

## 13. Risks

- **`ms_infinite`'s retarget is a one-line change to an already-`VERIFIED` package's own shipped
  code** (Low-Medium, mirrors the standing "a later package extends an already-`VERIFIED`
  upstream routine" pattern this project has used repeatedly, e.g. `IP-1103`/`IP-1104` on
  `inf_ensure_window`) — the change is a single transition-target constant, not a rewrite; T33.f's
  own `T25` non-regression re-run is the direct check that nothing else in `IP-1100`'s own shipped
  behavior moved.
- ROM budget: one new `GAMESTATE` branch, one new small screen (reusing existing font/palette,
  no new tile art), one new cursor-draw subroutine mirroring an existing one almost verbatim —
  expected modest against the 1,378-byte headroom (`R115`/`NFR-4500`), re-affirmed at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`tilemaps.py`/`test_rom.py` changes and rebuild. `ms_infinite`'s retarget is
the only touch to already-shipped code — reverting it restores `IP-1100`'s own original direct
`GS_MODE_SELECT` → `GS_INFINITE_SEED_ENTRY` transition exactly. No existing WRAM/`GAMESTATE`
value is reassigned; this package only claims new ones.
