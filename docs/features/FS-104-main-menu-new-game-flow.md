# FS-104 — Main Menu & New-Game Flow

> Feature Specification for [FEAT-1100](../feature-planning/03-feature-catalog.md#feat-1100--main-menu--new-game-flow-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-1100, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Forward reference (metadata only):** [IP-1040](../implementation/packages/IP-1040-main-menu-new-game-flow.md)
> **VERIFIED 2026-07-11** ([VR-1040](../implementation/verification/VR-1040-main-menu-new-game-flow.md))
> — all six Acceptance Criteria (§15) demonstrably pass via `test_rom.py`'s T14 suite (20/20,
> full suite 180/180 green). Resolves this document's Open Questions 1–2 (§19).

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-104` — expands `FEAT-1100` (Main Menu & New-Game Flow), Epic `EP-1000` (Core Gameplay Loop).

## 2. Title

Main Menu & New-Game Flow

## 3. Purpose

Gate every boot through a mandatory MAIN MENU offering continue/new-game, drive the new-game
seed/scale entry that triggers world generation, and offer exit-to-main-menu with auto-save from
the SAVE state. Carried forward verbatim from FEAT-1100's own Purpose (High User Value — the
first screen every player sees after this increment ships, and the sole path into a generated
world).

## 4. Scope

**In scope:** the MAIN MENU state (always entered on boot, offering continue/new-game); the
SEED/SCALE ENTRY state (digit-cursor entry, triggers world generation on confirm); the SAVE
state's new exit-to-main-menu option (auto-save then return to MAIN MENU).

**Out of scope** (per FEAT-1100's own Excluded Requirements, carried forward verbatim): FR-1120
(the current auto-load bypass — FEAT-1000's existing as-built catalog entry, whose *behavior* is
superseded on implementation per FR-1120's own target-state pointer, but whose catalog entry is
not modified by this spec); the generation routine itself and the seed/scale immutability rule
(FR-9100/FR-9110 — [FEAT-9000](FS-102-procedural-world-generation.md)); the underlying save-write
mechanism (FR-5100 — FEAT-5000, reused here, not reimplemented).

## 5. Requirements Implemented

FR-1170, FR-1180, FR-1190 — the exact set FEAT-1100 owns, no more, no fewer (cross-checked
against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-1100--main-menu--new-game-flow-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — Boot with no valid save (or a version-mismatched save):**

1. Console powers on / resets.
2. State enters MAIN MENU unconditionally (FR-1170) — no auto-load bypass, no TITLE screen (that
   state is superseded, per GDS-01 §4a).
3. MAIN MENU presents only "new game" (no "continue," since no version-matching save exists,
   FR-1170's Acceptance Criteria).
4. Player selects "new game" → transitions to SEED/SCALE ENTRY.
5. Player enters a seed (up to 5 decimal digits, 0–65535) and a world scale (2–9, default 3) via
   the digit-cursor picker (D-pad selects/moves the cursor, A confirms), per ADR-0010.
6. On confirm: SEED/WORLD_SCALE are set to the entered values (0 is normalized to 1 internally
   per ADR-0010's own PRNG-nonzero-state rule); FEAT-9000's generation routine runs to completion
   (FR-1180's own Dependencies: FR-9100, FR-9110); state transitions to INTRO.

**Workflow B — Boot with a valid, version-matching save:**

1. Console powers on / resets.
2. State enters MAIN MENU unconditionally (unlike the superseded TITLE, which the old auto-load
   bypass skipped entirely when a valid save existed — GDS-01 §4a's explicit distinction).
3. MAIN MENU presents both "continue" and "new game" (FR-1170).
4. Player selects "continue" → the existing save-restore mechanism (FEAT-5300's scope, consumed
   here) loads SEED/WORLD_SCALE/KeyItemFlags/etc.; state transitions to PLAYING directly (no
   INTRO, no re-generation — FEAT-5300 regenerates the region graph from the restored
   SEED/WORLD_SCALE, per ADR-0009's determinism guarantee, not this Feature's own concern).

**Workflow C — Exit to main menu from SAVE:**

1. Player is in PLAYING, presses START → transitions to SAVE (existing FR-1140 behavior,
   unchanged).
2. SAVE now offers three options instead of two: A (save, existing FR-5100 behavior, unchanged),
   B (cancel, existing behavior, unchanged), and the new exit-to-main-menu option.
3. Player selects exit-to-main-menu: the system performs the same save-field write FR-5100
   performs (FR-1190's own Description, verbatim), then transitions to MAIN MENU — not back to
   PLAYING (the distinguishing behavior versus A/B).

## 7. System Behaviour

**Normal path:** covered by Workflows A/B/C above, each ending in a well-defined state
(INTRO, PLAYING, or MAIN MENU respectively) with no ambiguous intermediate state.

**Edge case — "continue" selected with no valid save present:** cannot occur — FR-1170's own
Acceptance Criteria guarantees "continue" is only ever offered when a version-matching save
exists; this Feature's MAIN MENU rendering logic must not present an option that has no valid
target state.

**Edge case — seed entered as 0:** normalized to 1 internally before PRNG initialization
(ADR-0010) — the player-visible entered value remains 0 (e.g. if the player later views/re-enters
via a future "view seed" surface, which does not currently exist and is not assumed here); only
the generator's actual internal state is never 0.

**Edge case — seed/scale entry abandoned mid-entry:** not named by any upstream artifact (ADR-0010
specifies confirm-to-proceed via A, but not an explicit cancel/back-to-MAIN-MENU path from
SEED/SCALE ENTRY) — see Open Questions.

**Edge case — exit-to-main-menu selected with no unsaved changes pending:** behaves identically
to the case with pending changes (the save-write is unconditional, mirroring FR-5100's own
unconditional-on-selection behavior) — no special-cased "nothing to save" branch.

**Edge case — a save written under a pre-upgrade version byte, present at boot:** per ADR-0010 (as
FEAT-5300 implements it), such a save is treated as absent for "continue" purposes — MAIN MENU
presents only "new game," exactly as Workflow A describes; this Feature's own behavior contract
does not distinguish "no save" from "incompatible save" beyond the option-set difference
FR-1170's Acceptance Criteria already states.

## 8. Module Responsibilities

Per GDS-03's module decomposition and GDS-09's delta:

- **`asm_game.py`** — the two new states' dispatch logic (MAIN MENU, SEED/SCALE ENTRY), the
  option-set-by-save-validity check (FR-1170), the digit-cursor input handling (D-pad/A) for
  seed/scale entry, the new SAVE-state exit-to-main-menu branch, and the call into FEAT-9000's
  generation routine on confirm.
- **`tilemaps.py`** — two new screen layouts: the main menu screen and the seed/scale entry
  screen (both reusing existing tile primitives — digits, cursor/arrow tiles — per D1's
  no-text-engine constraint), consumed via the existing `ALL_SCREENS`-style registration
  mechanism.

No module outside this set is touched; this Feature does not modify `gbc_lib.py`,
`build_tile_data()`'s buffer contract, `music.py`, or `worldgen.py` (FEAT-9000's own module).

## 9. Interfaces Used

- **`build_game_asm(rom: ROM) -> dict`'s existing patch-point mechanism** (GDS-09 delta, cited
  verbatim): "a patch point for the seed/scale-entry screen's tile/attribute addresses (parallel
  to today's `title_t`/`title_a` pattern)" — this Feature's two new screens ride this existing
  mechanism, no new resolution machinery.
- **FEAT-9000's generation routine** — invoked as a call, not a new interface this Feature
  defines; this Feature is a consumer of FEAT-9000's contract (`generate`-equivalent SM83
  routine), per FS-102 §9.
- **The existing save-write mechanism (FR-5100, FEAT-5000)** — reused for the exit-to-main-menu
  auto-save, called exactly as the existing SAVE-state A(save) option already calls it (no new
  save-write code path, only a new caller).
- **FEAT-5300's save-validity/version-match fact** — this Feature's MAIN MENU option-set logic
  consumes a version-match determination FEAT-5300's save/load mechanism supplies; this Feature
  does not itself evaluate the SRAM version byte's raw bytes.

## 10. Data Model Changes

None beyond what FEAT-9000/FEAT-5300 already introduce — this Feature reads
`SEED`/`WORLD_SCALE`/save-validity state and writes via the existing save mechanism; it defines
no new WRAM/SRAM/ROM entity of its own. The two new screens' tilemap/attribute ROM data is a
content-authoring cost (existing digit/cursor tiles, no new tile-index allocation per D1),
against the existing ROM-section-layout convention (GDS-07 §1), not a new data-model concern.

## 11. State Changes

Per GDS-01 §4a's target-state diagram (cited verbatim above in Workflows):

- **New states:** MAIN MENU, SEED/SCALE ENTRY — both introduced by this Feature.
- **Retired behavior:** the auto-load-bypass (FR-1120's current shipped behavior) is superseded
  — `try_load_save`'s unconditional-at-boot call is replaced by MAIN MENU's "continue" action.
  This Feature's implementation is the trigger that retires this behavior; FR-1120's own
  requirement text and FEAT-1000's catalog entry are unmodified by this spec (per this skill's
  own SHALL-NOT rule) — the retirement is this Feature's *implementation* consequence, not a
  requirements-layer edit this stage performs.
- **Changed transition targets:** VICTORY's A-press target changes from TITLE to MAIN MENU
  (TITLE itself being superseded); SAVE gains a third exit branch to MAIN MENU alongside its
  existing A/B branches to PLAYING.

## 12. Error Handling

- **Invalid seed/scale input (out of range):** the digit-cursor picker's own input constraints
  (bounded digit positions, bounded scale value 2–9) prevent an out-of-range value from ever
  being confirmable — this is an input-UI constraint, not a post-entry validation/rejection path;
  no "invalid input" error state exists because the entry mechanism cannot produce one.
- **Generation failure:** out of this Feature's scope — per FS-102 §12, generation is not a
  runtime failure mode with a recovery path; this Feature assumes FEAT-9000's routine always
  completes successfully once invoked.
- **Save-write failure during exit-to-main-menu:** identical to the existing SAVE-state A(save)
  option's own (unstated, unchanged) failure characteristics — this Feature introduces no new
  failure mode beyond what FR-5100's existing save-write already has.

## 13. Performance Considerations

No NFR directly names this Feature's own timing (the two new screens use the existing
screen-rendering mechanism, unmodified). The generation call this Feature triggers is FEAT-9000's
NFR-4200 concern, not this Feature's own performance contract.

## 14. Integrity Considerations

- The exit-to-main-menu auto-save must leave SRAM reflecting the pre-exit game state exactly
  (FR-1190's own Acceptance Criteria, verbatim) — "no progress present at the time of exit is
  ever lost." This Feature's own integrity obligation is calling the existing save-write
  correctly, not re-implementing its correctness guarantees (those are FR-5100/FEAT-5000's).
- **Immutability enforcement (FR-9110) is explicitly not this Feature's own obligation to
  implement structurally** — FR-9110 is a negative/structural requirement ("no reachable input
  sequence from PLAYING, SAVE, or MAP changes SEED/WORLD_SCALE") that this Feature satisfies
  simply by not providing any such input path, not by an active guard this Feature's design adds.
  Confirmed by omission: no workflow in §6 above reaches SEED/SCALE ENTRY from anywhere except
  MAIN MENU's "new game."

## 15. Acceptance Criteria

1. After boot, state always equals MAIN MENU regardless of save presence (FR-1170).
2. Given a version-matching save exists, "continue" is offered; given none exists (or its version
   does not match), "continue" is not offered (FR-1170).
3. Entering seed S and scale N and confirming results in a generated world of exactly N² regions,
   and state becomes INTRO (FR-1180).
4. Re-entering the same (S, N) pair on a separate new-game creation produces an identical region
   graph (FR-1180, delegating the actual determinism guarantee to FR-9100/FS-102).
5. Selecting exit-to-main-menu from SAVE results in SRAM containing the current save-field set
   (verifiable by a subsequent "continue") and state = MAIN MENU (FR-1190).
6. No progress present at the time of exit is ever lost (FR-1190).

## 16. Verification Plan

Per FR-1170/1180/1190's own Verification Method (Test), landing in a new **T13: Main Menu &
New-Game Flow** suite in `test_rom.py` (the next unused suite number after FS-102's proposed T12):

- **AC-1/AC-2 (MAIN MENU option-set):** boot with no save present → assert state == MAIN MENU,
  "continue" option absent; boot with a valid version-matching save present → assert state ==
  MAIN MENU (not PLAYING, confirming the auto-load bypass is actually retired), "continue"
  present; boot with a version-mismatched (synthetic pre-upgrade) save → assert "continue" absent
  — following `IP-1010`'s T11.d synthetic-fixture pattern exactly.
- **AC-3/AC-4 (new-game trigger + determinism):** drive the digit-cursor entry for a known
  `(seed, scale)`, confirm, assert state == INTRO and the resulting region count equals
  `scale²`; repeat with the same pair in a fresh new-game creation, assert identical region-graph
  output (delegating the actual comparison to FS-102's T12 oracle-comparison check, invoked here
  only to confirm this Feature's own trigger path reaches it correctly).
- **AC-5/AC-6 (exit-to-main-menu):** from PLAYING, force known state (`SCORE`, `CUR_ZONE`, etc.),
  START → SAVE → exit-to-main-menu, assert state == MAIN MENU; reload via "continue," assert the
  restored state matches exactly what was present at exit — extending T10's existing save/reload
  two-instance harness pattern.
- **Negative test for FR-9110 (§14):** attempt every reachable input sequence from PLAYING, SAVE,
  and MAP, confirm none writes SEED/WORLD_SCALE — a systematic sweep, not a single spot check,
  per FR-9110's own Verification Method ("negative test — attempt every in-game menu path").

## 17. Dependencies

Per FEAT-1100's own Dependencies (carried forward verbatim): FEAT-1000 (extends its state
machine, already shipped Baseline); **FEAT-9000** (triggers its generation routine on new-game
confirm — [FS-102](FS-102-procedural-world-generation.md), already specified); FEAT-5000 (reuses
its save-write for the auto-save option, already shipped Baseline). This Feature does not sit on
the procgen-world increment's own critical path (FEAT-9000 → FEAT-4100 → FEAT-6100, per FP-04) —
it depends only on FEAT-9000 (already specified) plus already-shipped Baseline Features, so it is
parallel-eligible with FEAT-4100/FEAT-5300 once FEAT-9000's implementation exists.

## 18. Risks

Carried forward from FEAT-1100's own Risk assessment (Medium): retires FR-1120's auto-load
bypass, a deliberate protected-baseline change (MSTR-001 C2 amendment) needing careful negative
testing that FR-9110's "seed/scale immutable mid-game" rule actually holds against every
reachable input sequence (§16's negative-test plan addresses this directly). This spec surfaces
one additional, narrower risk: the undefined cancel/back path from SEED/SCALE ENTRY (Open
Question 1) could leave a player with no way out of that screen short of completing entry — a
design gap this spec did not silently assume away.

## 19. Open Questions

1. **Whether SEED/SCALE ENTRY offers a cancel/back-to-MAIN-MENU path is not named by ADR-0010 or
   GDS-01 §4a.** ADR-0010 specifies confirm-via-A but is silent on an abandon path; GDS-01 §4a's
   state diagram shows only a one-directional `MAIN MENU → SEED/SCALE ENTRY → INTRO` edge, no
   return edge. Without one, a player who selects "new game" by mistake has no way back to MAIN
   MENU short of completing a full seed/scale entry and generation. This matters because it's a
   genuine player-experience gap this Feature's own workflow (Workflow A) does not currently
   allow for. **Resolved (`IP-1040`, 2026-07-10):** B cancels SEED/SCALE ENTRY back to MAIN MENU
   without writing `SEED`/`WORLD_SCALE` (`st_seed_scale_entry`'s B-branch), matching the existing
   SAVE state's own A/B pattern exactly, confirmed by `T14.c1`/`c1b`.
2. **Whether "continue"/"new game" selection uses A-confirm-only or also supports a D-pad
   up/down selector between the two options** is an input-mapping detail GDS-01 §4a does not
   specify at the state-machine altitude. **Resolved (`IP-1040`, 2026-07-10):** D-pad up/down
   toggles the highlighted option (`st_main_menu`'s toggle branch, gated on a valid save
   existing), A confirms — the same digit-cursor idiom ADR-0010 already establishes for
   SEED/SCALE ENTRY, reused rather than inventing a second input convention.

## 20. Related ADRs

ADR-0009 (this Feature's SEED/SCALE ENTRY confirm-action invokes ADR-0009's generation routine),
ADR-0010 (seed & scale entry surface, digit-cursor picker, immutability rule, pre-upgrade-save
"continue" exclusion — this Feature's core design source).
