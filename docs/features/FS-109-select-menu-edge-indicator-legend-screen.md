# FS-109 — SELECT Menu & Edge-Indicator Legend Screen

> Feature Specification for [FEAT-1200](../feature-planning/03-feature-catalog.md#feat-1200--select-menu--edge-indicator-legend-screen-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-1200, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Forward reference (metadata only):** [IP-1090](../implementation/packages/IP-1090-select-menu-edge-indicator-legend-screen.md)
> **COMPLETE 2026-07-13** — all seven Acceptance Criteria (§15) demonstrably pass via
> `test_rom.py`'s T21 suite (12/12, full suite 246/246 green), awaiting independent
> (`09-package-verification`) review. Resolves this document's Open Questions 1–3 (§19).

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-109` — expands `FEAT-1200` (SELECT Menu & Edge-Indicator Legend Screen), Epic `EP-1000`
(Core Gameplay Loop).

## 2. Title

SELECT Menu & Edge-Indicator Legend Screen

## 3. Purpose

Give the player an in-game explanation of the on-screen transition-edge indicator tiles
(`FEAT-2100`'s open-arrow/blocked-edge/absent three-state signal), which today has no in-game
explanation anywhere. Carried forward verbatim from FEAT-1200's own Purpose (`BL-0100`, project
owner request; Medium User Value — closes a real discoverability gap, but affects a reference
screen a player visits rarely, not the moment-to-moment loop).

## 4. Scope

**In scope:** the new SELECT MENU state (cursor-selectable "map"/"legend," reached from PLAYING
via SELECT, replacing SELECT's current direct jump to MAP); the new LEGEND state (a single
static screen showing each transition-edge indicator tile beside a plain-language label).

**Out of scope** (per FEAT-1200's own Excluded Requirements, carried forward verbatim): FR-1150
(the existing PLAYING↔MAP transition — `FEAT-1000`'s own catalog entry; this Feature's FR-1200
supersedes only its SELECT-entry clause on implementation, per FR-1150's own target-state
pointer, without modifying FEAT-1000's catalog entry or MAP's own content/layout — MAP's future
redesign is `BL-0050`, tracked separately); FR-2320/FR-2330 (the indicator tiles' own meaning and
render-time classification — `FEAT-2000`/`FEAT-2100`'s scope; this Feature only displays the
already-shipped tiles, it does not redefine what they mean or how they're computed).

## 5. Requirements Implemented

FR-1200, FR-1210 — the exact set FEAT-1200 owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-1200--select-menu--edge-indicator-legend-screen-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — Open the map from PLAYING:**

1. Player is in PLAYING, presses SELECT.
2. State transitions to SELECT MENU with "map" highlighted by default (FR-1200's own Acceptance
   Criteria).
3. Player presses A (no D-pad input) → state transitions to MAP.
4. MAP behaves exactly as it does today (FEAT-1000's own unchanged entry) — B returns to
   PLAYING.

**Workflow B — Open the legend from PLAYING:**

1. Player is in PLAYING, presses SELECT.
2. State transitions to SELECT MENU with "map" highlighted by default.
3. Player presses D-pad up or down → highlight toggles to "legend."
4. Player presses A → state transitions to LEGEND (FR-1210).
5. LEGEND displays the three-row static content: the open-arrow tile beside "OPEN PATH," the
   blocked-edge-bar tile beside "MAZE BLOCKED," and a blank cell beside "WORLD EDGE" (GDS-08
   §11's content decision, verbatim).
6. Player presses B → state transitions to PLAYING.

**Workflow C — Cancel out of SELECT MENU without visiting either destination:**

1. Player is in PLAYING, presses SELECT → state = SELECT MENU.
2. Player presses B (regardless of which option is highlighted) → state transitions directly to
   PLAYING, matching PLAYING's own state exactly as it was before SELECT was pressed (FR-1200's
   own Postconditions — no destination visited, nothing written).

## 7. System Behaviour

**Normal path:** covered by Workflows A/B/C above, each ending in a well-defined state (MAP,
LEGEND, or PLAYING respectively) with no ambiguous intermediate state.

**Edge case — D-pad pressed repeatedly (up/up/up or down/down/down) while in SELECT MENU:** with
only two options, the highlight toggles between "map" and "legend" on every D-pad up/down press
(FR-1200's Acceptance Criteria specifies toggling, not a bounded/saturating cursor across more
than two positions) — mirrors `MAIN MENU`'s own `MM_CURSOR` toggle behavior (`asm_game.py`'s
`mm_toggle` branch) exactly, not a new cursor-movement idiom.

**Edge case — A pressed with no D-pad input since entering SELECT MENU:** "map" is confirmed,
since "map" is the default highlight (FR-1200's Acceptance Criteria, Workflow A above) — this is
the normal path for the common case, not a special-cased default.

**Edge case — B pressed while in LEGEND:** returns directly to PLAYING (FR-1210's own
Postconditions), not back through SELECT MENU — matching MAP's own existing one-step-back
convention exactly (GDS-01 §4c, cited verbatim), never re-presenting the menu the player already
passed through.

**Edge case — SELECT pressed while already in SELECT MENU, MAP, or LEGEND:** not named by any
upstream artifact (GDS-01 §4c's diagram shows SELECT as PLAYING's own outbound trigger only, with
no self-transition or SELECT-triggered behavior defined for the three new/existing destination
states themselves) — see Open Questions.

## 8. Module Responsibilities

Per GDS-03's module decomposition and GDS-01 §4c/GDS-08 §11's deltas:

- **`asm_game.py`** — the two new states' dispatch logic (SELECT MENU, LEGEND); the SELECT MENU
  cursor toggle and two confirm branches (A→MAP, A→LEGEND) plus its B-cancel branch (→PLAYING);
  LEGEND's own single B-branch (→PLAYING); the existing PLAYING SELECT-press handler retargeted
  from a direct GS_MAP transition to GS_SELECT_MENU.
- **`tilemaps.py`** — two new screen layouts: the SELECT MENU screen (two cursor-selectable
  labels, reusing `main_menu_screen()`'s own static-screen shape per D1's no-text-engine
  constraint) and the LEGEND screen (title line, horizontal rule, three-row body placing the real
  `TL_ARROW_U`/`TL_BLOCKED_U` tiles beside their labels plus the blank WORLD EDGE row, footer
  "B: EXIT" — GDS-08 §11's content decision, verbatim), both consumed via the existing
  `ALL_SCREENS`-style registration mechanism.

No module outside this set is touched; this Feature does not modify `gbc_lib.py`, `worldgen.py`,
`music.py`, or `map_screen()`'s own existing content (`tilemaps.py`, untouched per FEAT-1200's own
Scope).

## 9. Interfaces Used

- **`build_game_asm(rom: ROM) -> dict`'s existing patch-point mechanism** (GDS-09, reused): the
  two new screens ride the same patch-point pattern `main_menu_screen()`'s own tile/attribute
  addresses already use — no new resolution machinery.
- **The existing cursor-menu convention (`MM_CURSOR`-style toggle, D-pad up/down + A confirm)**
  established by `FEAT-1100`'s MAIN MENU (FR-1170) — this Feature's SELECT MENU reuses the
  identical input-handling shape rather than a new one, per GDS-01 §4c's own stated design
  intent.
- **`TL_ARROW_U` and `TL_BLOCKED_U`** (already ROM-resident since `IP-1030`/`IP-1081`) — LEGEND
  displays these existing tiles directly; this Feature defines no new tile art or palette entry
  (GDS-08 §11).
- **The existing static-screen layout convention** (`main_menu_screen()`/`map_screen()`'s title
  line + horizontal rule + body + footer-control-hint shape, `tilemaps.py`) — reused for both new
  screens, not reinvented.

## 10. Data Model Changes

One new WRAM byte for SELECT MENU's own cursor state, per GDS-01 §4c's own explicit deferral:
either a reuse of `MM_CURSOR` (valid since MAIN MENU and SELECT MENU are never simultaneously
active) or a new dedicated byte — left as a GDS-07 data-model choice for `07`/`08`, not decided
here (an Open Question, per GDS-01 §4c's own framing of this as an implementation-level decision,
not a design-level one this spec must resolve). No new SRAM entity; no new ROM tile/palette data
(GDS-08 §11 — LEGEND reuses `TL_ARROW_U`/`TL_BLOCKED_U`/palette 2 verbatim).

## 11. State Changes

Per GDS-01 §4c's target-state diagram (cited verbatim above in Workflows):

- **New states:** SELECT MENU, LEGEND — both introduced by this Feature. Numeric `GAMESTATE`
  values are left to `07`/`08` (the next two free values following the existing
  `GS_SEED_SCALE_ENTRY = 7`, per this project's own append-only `GAMESTATE` numbering
  convention, `asm_game.py:170,174` — an Open Question, not decided here).
- **Changed transition targets:** PLAYING's existing SELECT-press handler, which today
  transitions directly to MAP, is retargeted to SELECT MENU. MAP's inbound edge changes from a
  direct PLAYING→MAP transition to an indirect PLAYING→SELECT MENU→MAP path only — MAP's own
  content, and its existing "B → PLAYING" clause, are unaffected (FR-1150's own text, unmodified
  per this spec's own SHALL-NOT rule).
- **Retired behavior:** none — this is a purely additive state-machine change; no existing state
  or transition is removed, only PLAYING's SELECT-press target is redirected.

## 12. Error Handling

- **No invalid-input state exists for SELECT MENU's own two-option cursor:** the toggle-between-
  two-values mechanism cannot produce an out-of-range highlight; there is no rejection/error path
  to define.
- **LEGEND has no player input beyond B:** no error condition is reachable from a screen with a
  single control.
- **A pressed while B is also physically held (or vice versa) in SELECT MENU:** not named by any
  upstream artifact — this codebase's existing input-handling convention (per `MAIN MENU`'s own
  precedent, R107) has no documented simultaneous-press priority rule anywhere; this Feature
  inherits whatever the existing joypad-read routine's natural precedence is, introducing no new
  behavior of its own.

## 13. Performance Considerations

No NFR directly names this Feature's own timing — both new screens use the existing
screen-rendering mechanism, unmodified, and their content is fully static (GDS-08 §11's own
"no animation" decision). No VBlank-budget concern beyond what the existing static-screen
convention already satisfies.

## 14. Integrity Considerations

None — this Feature reads no SRAM, writes no SRAM, and its own WRAM cursor byte (§10) is
transient UI state with no save-persistence or checksum obligation, per FR-1200/FR-1210's own
Postconditions (state transitions only, no data write named by either requirement).

## 15. Acceptance Criteria

1. From PLAYING, SELECT press results in state = SELECT MENU with "map" highlighted by default
   (FR-1200).
2. D-pad up/down toggles the highlighted option between "map" and "legend" (FR-1200).
3. With "map" highlighted, A results in state = MAP (FR-1200).
4. With "legend" highlighted, A results in state = LEGEND (FR-1200).
5. From SELECT MENU, B results in state = PLAYING regardless of which option was highlighted,
   writing nothing (FR-1200).
6. From LEGEND, B results in state = PLAYING (FR-1210).
7. LEGEND's screen displays the actual open-arrow tile and the actual blocked-edge-bar tile (not
   redrawn approximations), each beside its own plain-language label, plus a labeled blank cell
   for the world-edge case (FR-1210).

## 16. Verification Plan

Per FR-1200/FR-1210's own Verification Method (Test, plus Inspection for LEGEND's exact
tile/label layout per GDS-08 §11's own coordinate deferral), landing in a new **T21: SELECT Menu
& Edge-Indicator Legend Screen** suite in `test_rom.py` (the next unused suite number after the
existing T1–T20 suites):

- **AC-1/AC-2 (SELECT MENU entry + toggle):** from PLAYING, press SELECT → assert state ==
  SELECT MENU and the cursor byte reflects "map" highlighted; press D-pad up (or down) → assert
  the cursor byte now reflects "legend"; press again → assert it toggles back to "map" —
  following `T14`'s existing `MM_CURSOR`-toggle assertion pattern exactly.
- **AC-3/AC-4 (confirm branches):** with "map" highlighted, press A → assert state == MAP; from a
  fresh SELECT MENU entry, toggle to "legend," press A → assert state == LEGEND.
- **AC-5 (cancel):** from SELECT MENU (either highlight), press B → assert state == PLAYING, and
  assert no WRAM byte outside the transient cursor byte itself changed versus the pre-SELECT
  snapshot (a diff-based negative check, mirroring `T14`'s own SEED/SCALE-immutability sweep
  pattern).
- **AC-6 (LEGEND exit):** from LEGEND, press B → assert state == PLAYING.
- **AC-7 (LEGEND content, Inspection):** with state == LEGEND, read the rendered tilemap and
  assert row 1 contains `TL_ARROW_U` adjacent to the "OPEN PATH" label tiles, row 2 contains
  `TL_BLOCKED_U` adjacent to "MAZE BLOCKED," and row 3's tile cell is blank adjacent to "WORLD
  EDGE" — a direct tilemap-content assertion, not a rendered-pixel comparison, following
  `T20`'s own tilemap-inspection pattern for the live MAP indicator tiles.

## 17. Dependencies

Per FEAT-1200's own Dependencies (carried forward verbatim): FEAT-1000 (extends its state
machine, already shipped Baseline); FEAT-1100 (reuses its cursor-menu convention, already
specified/shipped — [FS-104](FS-104-main-menu-new-game-flow.md)); FEAT-2100 (LEGEND's own content
depends on the open-arrow/blocked-edge tiles that Feature defines already existing — both tiles
are already shipped, `IP-1030`/`IP-1081`, a content dependency, not a build-order one — FEAT-2100's
own still-unverified render branch, `IP-1082`, does not block this Feature). This Feature does not
sit on any other Feature's own critical path; it is immediately buildable once packaged.

## 18. Risks

Carried forward from FEAT-1200's own Risk assessment (Low): the one real, explicitly-named
tradeoff (an extra button press to reach MAP for every player) was already weighed and accepted
at the architecture level (GDS-01 §4c), not an open risk this Feature carries forward undecided.
This spec surfaces no additional risk beyond the two Open Questions below, both narrow
implementation-level choices rather than design-level ambiguity.

## 19. Open Questions

1. **The exact WRAM byte for SELECT MENU's own cursor state is not decided here** — reuse
   `MM_CURSOR` (valid since MAIN MENU and SELECT MENU are never simultaneously active) or a new
   dedicated byte. GDS-01 §4c explicitly defers this to `07`/`08` (a GDS-07 data-model choice,
   following `ADR-0015`'s own precedent of leaving byte-encoding choices to `07`/`08` when either
   representation is equally valid). Matters because `07-implementation-planning` needs a
   concrete WRAM address before packaging. Resolved by: `07-implementation-planning` (or a
   GDS-07 delta if the chosen encoding warrants documenting as a data-model entity). **Resolved
   (`IP-1090`, 2026-07-13):** reuses `MM_CURSOR` (`0xC27E`) and `MM_JUST_ENTERED` (`0xC2D7`)
   rather than allocating two new WRAM bytes.
2. **The new `GAMESTATE` numeric values for SELECT MENU/LEGEND are not decided here** — GDS-01
   §4c names them as "the next two free values following the existing `GS_SEED_SCALE_ENTRY = 7`"
   but defers the actual assignment to implementation, per this project's own append-only
   `GAMESTATE` numbering convention (`asm_game.py:170,174`). Matters for the same packaging
   reason as Open Question 1. Resolved by: `07-implementation-planning`. **Resolved (`IP-1090`,
   2026-07-13):** `GS_SELECT_MENU = 8`, `GS_LEGEND = 9`.
3. **Whether SELECT pressed while already in SELECT MENU, MAP, or LEGEND has any defined
   behavior is not named by GDS-01 §4c's diagram**, which shows SELECT only as PLAYING's own
   outbound trigger. Matters because an implementer needs to know whether SELECT is simply
   ignored (no handler registered) in the three new/existing destination states, or whether it
   should do something else. This spec assumes the former (no handler, matching how MAP and
   SAVE already ignore inputs they don't explicitly handle) but flags it as unconfirmed by any
   upstream artifact. Resolved by: `07-implementation-planning`, or a GDS-01 delta if the
   architecture owner wants it stated explicitly. **Resolved (`IP-1090`, 2026-07-13):** SELECT is
   a plain no-op inside both SELECT MENU and LEGEND (neither handler tests `J_SELECT`); `MAP`'s
   own pre-existing SELECT==B exit merge (`st_map`, unrelated, unchanged) continues to apply once
   inside `MAP` itself, per the Technical Work Breakdown's own supersession sweep.

## 20. Related ADRs

None (FEAT-1200's own catalog entry states None; this Feature's design is grounded in GDS-01 §4c
and GDS-08 §11 directly, neither of which required a dedicated ADR — the same precedent GDS-01
§4c itself cites for SAVE's own third option never needing one).
