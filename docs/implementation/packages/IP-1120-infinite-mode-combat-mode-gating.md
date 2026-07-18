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
- **`mode_select_screen`'s own already-registered tile/attr array** (`tilemaps.py`, `IP-1100`,
  unchanged) — **reused directly as this state's own base screen**, per the `BL-0153` ROM-budget
  remediation (2026-07-18; see the Master Build Plan `IP-1120` row and
  [TWBS](../01-technical-work-breakdown.md#ip-1120-re-plan--rom-budget-remediation-bl-0153-2026-07-18)
  for the full byte math). `COMBAT MODE CONFIRM` and `MODE SELECT` share almost their entire
  static layout (blank background, border rows 2/14, label rows 7/9) — registering a second
  1,152-byte `ALL_SCREENS` array to change three lines of text overflowed the ROM by 542 bytes
  against the 866-byte headroom remaining after `IP-1122`/`IP-1123`. This package does **not**
  touch `tilemaps.py` or `ALL_SCREENS` at all.
- **`memcpy`** (`asm_game.py`, existing, unmodified) — reused verbatim to write this state's own
  three small literal-text overlays (title, "NO", "YES") on top of the reused base array's own
  baked-in "BUNNY QUEST"/"FINITE"/"INFINITE" text, the same technique `draw_sse_digits`/
  `draw_ise_digits` already use for their own dynamic content (a static base blit via
  `copy_screen`, then a small runtime overlay) — just applied to fixed literal strings instead of
  computed digits.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`** (sole file this package touches — `tilemaps.py` is not modified,
  per the `BL-0153` remediation above):
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
    'dsr_ise')` row; new `_dsr_screen('dsr_cmc', 'cmc_t', 'cmc_a', extra='cmc_on_entry')` call —
    **`'cmc_t'`/`'cmc_a'` are their own distinct `patches` dict keys** (each `_dsr_screen` call
    needs a unique key, one per `LD_DE_nn(0)`/`LD_BC_nn(0)` placeholder instruction pair it
    emits), but `build_rom.py`'s own patch-resolution line points them at **the same address
    pair `'ms_t'`/`'ms_a'` already resolve to** (`screen_addrs['mode_select']`) instead of
    registering a new `screen_addrs` entry — two labeled call sites, one shared underlying array.
  - **New inline literal-text data** (three small byte blobs, emitted directly in the code
    stream behind a `JR` that skips over them — never executed, only referenced by address):
    `cmc_str_title` = `char_to_tile()` of `"COMBAT MODE?"` (12 bytes, replaces `mode_select_
    screen`'s own 11-char "BUNNY QUEST" at row 3 col 5 — 12 bytes fully covers the original
    11-char span, no separate blanking needed); `cmc_str_no` = `char_to_tile()` of `"NO"` padded
    with 4 `TL_BG_BLANK` bytes (6 bytes total, replacing "FINITE"'s own 6-char span at row 7 col
    8 — the blank padding erases "FINITE"'s trailing 4 characters in the same write); `cmc_str_
    yes` = `char_to_tile()` of `"YES"` padded with 5 `TL_BG_BLANK` bytes (8 bytes total, replacing
    "INFINITE"'s own 8-char span at row 9 col 8, same padding-erases-trailing-chars technique).
  - **New subroutine `cmc_on_entry`/`draw_combat_confirm_cursor`** — mirrors `ms_on_entry`/
    `draw_mode_select_cursor`, with one addition at the top: **unconditionally** (every dispatch
    into `dsr_cmc`, not gated on `MM_JUST_ENTERED` — `copy_screen` re-blits the full reused
    `mode_select_screen` array, including its own baked-in text, on *every* redraw of this state,
    including a same-state toggle redraw, so the overlay must be redrawn every time too, exactly
    like the cursor glyph below already is) three `memcpy` calls: `cmc_str_title` → `0x9800 +
    3*32 + 5` (12 bytes), `cmc_str_no` → `0x9800 + 7*32 + 8` (6 bytes), `cmc_str_yes` → `0x9800 +
    9*32 + 8` (8 bytes) — `VBK` is already 0 (the tile-plane bank) on entry, since `copy_screen`'s
    own body always leaves it at 0 before returning, so no extra bank switch is needed. Then,
    exactly as `ms_on_entry` does: on a genuine state entry (`MM_JUST_ENTERED` set), reset
    `CMC_CURSOR = 0`; always redraw the cursor glyph at whichever row `CMC_CURSOR` currently
    selects, blanking the other row first (two fixed VRAM addresses, mirroring `MS_CURSOR_
    FINITE_ADDR`/`MS_CURSOR_INFINITE_ADDR`'s own construction: `CMC_CURSOR_NO_ADDR = 0x9800 +
    7*32 + 6`, `CMC_CURSOR_YES_ADDR = 0x9800 + 9*32 + 6` — the same cursor column `mode_select_
    screen`'s own reused array already uses, since the label column is unchanged).
- **Modify: `build_rom.py`** (already in `08-code-implementation`'s own standing write scope,
  not a content-peer-seam crossing): one new two-line patch block, `p16(patches['cmc_t'],
  screen_addrs['mode_select'][0])` / `p16(patches['cmc_a'], screen_addrs['mode_select'][1])`,
  alongside the existing `'ms_t'`/`'ms_a'`/`'ise_t'`/`'ise_a'` block.

## 7. Implementation Tasks

Ordered: (1) `GS_COMBAT_MODE_CONFIRM`/`CMC_CURSOR` constants; (2) `ms_infinite`'s retarget +
`CMC_CURSOR` reset; (3) `st_combat_mode_confirm`'s UP/DOWN/A/B handling; (4) the three inline
literal-text data blobs (`cmc_str_title`/`cmc_str_no`/`cmc_str_yes`); (5) `do_screen_redraw`
dispatch entry (`'cmc_t'`/`'cmc_a'` patch keys) + `build_rom.py`'s own patch-resolution line
pointing them at `mode_select`'s address pair; (6) `cmc_on_entry`'s text-overlay `memcpy` calls +
`draw_combat_confirm_cursor`; (7) rebuild ROM; (8) author new suite; (9) full suite run (including
a direct `T25` re-run, unmodified, plus a fresh check that `MODE SELECT`'s own screen still
renders "BUNNY QUEST"/"FINITE"/"INFINITE" correctly — confirming the reused array itself is
untouched by the overlay, only the VRAM copy is); (10) documentation updates (§9).

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
- T33.g — reused-array non-corruption (`BL-0153` remediation-specific): after visiting `COMBAT
  MODE CONFIRM` (forcing the redraw so its own text-overlay `memcpy` calls run), navigate back to
  `MODE SELECT` and confirm its own screen still reads "BUNNY QUEST"/"FINITE"/"INFINITE"
  correctly — proving the overlay technique only ever touches the live VRAM *copy*
  `copy_screen` just wrote, never `mode_select_screen`'s own ROM-resident array, so the two
  states sharing one array cannot cross-contaminate each other's display.
- T33.h — overlay content correct: drive to `COMBAT MODE CONFIRM`, read the row-3/row-7/row-9
  VRAM tile bytes directly, confirm they read "COMBAT MODE?"/"NO"/"YES" (not stale "BUNNY
  QUEST"/"FINITE"/"INFINITE" leftovers) and that no trailing character from the longer original
  labels survives the shorter replacement (e.g. row 7 col 13, "FINITE"'s own last letter's
  position, reads blank, not "E").

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-11100 status → Implemented.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-11100 row → `IP-1120`/T33.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md` metadata: Open Question 1 marked
  Resolved (`GDS-01` §4e, `IP-1120`).
- `docs/architecture/07-data-model.md` (or WRAM quick-reference): new `CMC_CURSOR` row,
  `0xC6DD`; new `GAMESTATE` row, `GS_COMBAT_MODE_CONFIRM = 12`; a note that `dsr_cmc` reuses
  `mode_select_screen`'s own tile/attr array rather than registering a new `ALL_SCREENS` entry.
- Master Build Plan status row; `packages/INDEX.md` status → `NOT STARTED` (unblocked).

## 10. Definition of Done

- `COMBAT MODE CONFIRM` defaults to "N," correctly sets `COMBAT_MODE` on "Y" confirm, B-cancels
  cleanly back to `MODE SELECT` with "infinite" still highlighted, and resets to "N" on every
  fresh entry (T33.a–d all passing).
- The finite path and `T25`'s own prior behavior are completely unaffected (T33.e/f).
- The reused `mode_select_screen` array is never corrupted by the overlay technique, and
  `COMBAT MODE CONFIRM`'s own overlay content (title + NO/YES, no stale trailing characters)
  renders correctly (T33.g/h).
- ROM builds at 32768 bytes; full suite passes; **no new `ALL_SCREENS` entry exists** — this is
  the load-bearing constraint the `BL-0153` remediation exists to satisfy, checkable directly
  against `tilemaps.py`'s own diff (empty) and `ALL_SCREENS`'s own length (unchanged from before
  this package).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, including `T25` unmodified.
- [ ] T33.a–h each present and passing.
- [ ] Direct code read: `ms_check_a`'s "finite" branch (`GS_SEED_SCALE_ENTRY` target) is
      byte-for-byte unchanged from `IP-1100`'s own shipped form.
- [ ] Direct code read: `st_infinite_seed_entry` itself is unmodified — this package's new state
      only redirects into it, never edits its own body.
- [ ] Direct code read: `tilemaps.py` is untouched by this package's own diff — `ALL_SCREENS`'s
      own length and every existing entry are unchanged (the `BL-0153` remediation's own
      load-bearing constraint).
- [ ] Direct code read: `patches['cmc_t']`/`patches['cmc_a']` resolve to the identical address
      pair `patches['ms_t']`/`patches['ms_a']` resolve to (`screen_addrs['mode_select']`), not a
      new `screen_addrs` entry.
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
- **ROM budget (re-derived 2026-07-18, `BL-0153`):** the original design (a new `ALL_SCREENS`
  entry) overflowed the ROM by 542 bytes against the 866-byte headroom remaining after
  `IP-1122`/`IP-1123` — a real, measured blocker, not a hypothetical one (see the Blocking
  Report on the Master Build Plan's own `IP-1120` row and the
  [TWBS](../01-technical-work-breakdown.md#ip-1120-re-plan--rom-budget-remediation-bl-0153-2026-07-18)).
  The re-plan above (reuse `mode_select_screen`'s own array + a runtime text overlay) reduces
  this package's own total growth to roughly 260-320 bytes — re-affirm the exact figure at build
  time regardless, the same discipline every other package in this tranche already follows.
- **First use of the "reuse an existing screen's array + runtime text overlay" technique in this
  codebase** (Low-Medium) — `draw_sse_digits`/`draw_ise_digits` establish the general "static
  base + runtime overlay" shape but for *computed digits*, not *fixed literal strings*; this
  package's own inline-data-behind-a-`JR` technique for the literal strings is new, though it
  reuses `memcpy` (already-shipped, unmodified) as its own copy mechanism. T33.g/h are the direct
  checks that the technique works correctly and doesn't corrupt the shared array.

## 14. Rollback Considerations

Revert `asm_game.py`/`build_rom.py`/`test_rom.py` changes and rebuild (`tilemaps.py` is not
touched by this package at all, per the `BL-0153` remediation — nothing to revert there).
`ms_infinite`'s retarget is the only touch to already-shipped code — reverting it restores
`IP-1100`'s own original direct `GS_MODE_SELECT` → `GS_INFINITE_SEED_ENTRY` transition exactly.
No existing WRAM/`GAMESTATE`
value is reassigned; this package only claims new ones.
