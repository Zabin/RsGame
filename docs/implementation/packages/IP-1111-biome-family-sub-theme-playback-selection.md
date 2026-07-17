# IP-1111 — Biome-Family Sub-Theme Playback Selection

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1111` — implements [**FS-111**](../../features/FS-111-procedural-music-generation.md)
Workflow B (`FEAT-7100`, Epic `EP-7000`) — grounded by `ADR-0019` point 6 and `FR-7110`
(biome-family-identity-keyed sub-theme playback selection). Planned against commit `7cb452f`.

## 2. Objective

During `PLAYING` (either mode), switch the currently-playing music track to the sub-theme matching
the player's current region's biome-family identity; outside `PLAYING`, play the main theme.

**Resolves `FS-111`'s Open Question 1** (the selection-mechanism shape): hooks into two
already-shipped trigger points rather than adding a new per-frame poll or new "last-known
identity" WRAM state —

1. **`do_screen_redraw`**'s existing per-`GAMESTATE` dispatch (`asm_game.py:1305`–`1327`) gains an
   unconditional **default reset to the main theme's own address** (`grass_mus_lo`/`grass_mus_hi`,
   per `IP-1110`'s own Grass-anchor decision), written immediately after `TRANSITION_TO`/
   `GAMESTATE`/`NEED_REDRAW` are set (`asm_game.py:1311`–`1313`) and before the twelve-way state
   dispatch. This fires on **every** screen redraw, in every state — including `PLAYING`.
2. **`dsr_p_dispatch`**'s existing per-identity biome cascade (`asm_game.py:1392`–`1410`,
   currently 5 branches, `_dsr_family`) gains, inside each non-Grass branch, an **override**
   repointing `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/`MUSIC_CTR` to that identity's own sub-theme address
   (`IP-1110`'s own `*_mus_lo`/`*_mus_hi` patch keys). The Grass branch needs no override — step 1's
   own default already points at the correct (identical) address.

This fires the moment a region's screen is drawn — the same moment the screen's own biome-family
tile content changes — satisfying `FR-7110`'s own "within one frame of the region becoming
current" Acceptance Criteria without any new polling logic, and correctly resets to the main theme
the moment `PLAYING` is left (any of the other eleven `dsr_*` labels run step 1's own default and
never reach step 2's override).

**A second, load-bearing fix this package also carries** (surfaced by this planning pass, not
named in `FS-111` — see the Technical Work Breakdown's own "Procedural Music Generation" section):
`music_tick`'s existing loop-restart branch (`asm_game.py:1256`–`1270`) hardcodes its reset target
to the main theme's own address (`patches['mus_reset']`, `asm_game.py:1263`), not whichever track
is currently selected. Without a fix, any sub-theme would silently truncate to a single pass
before falling back to the main theme the moment it loops. This package adds a new WRAM field
(`MUSIC_BASE_LO`/`MUSIC_BASE_HI`) holding the currently-selected track's own base address, written
alongside `MUSIC_PTR_LO`/`MUSIC_PTR_HI` at every repoint (both step 1's default and step 2's
override), and changes `music_tick`'s reset branch to read it instead of the hardcoded
`mus_reset` patch constant.

**Scope boundary:** this package does not itself widen `dsr_p_dispatch`'s cascade to nine
branches — it adds a music-repoint override to whichever branches already exist. It is `BLOCKED`
until `IP-1022` ships all nine branches (§12) — adding this package's own override code to only 5
of 9 branches today, then needing a second pass once the remaining 4 exist, was considered and
rejected as a genuine file/region-overlap risk against `IP-1022`'s own planned diff (see the
Technical Work Breakdown's own Split rationale).

## 3. Requirements Covered

`FR-7110` (in full, once unblocked — every one of its Acceptance Criteria across all nine
identities requires `dsr_p_dispatch`'s full cascade to exist first, which this package depends on
rather than duplicates).

## 4. Architecture Components

`ADR-0019` point 6 (identity-keyed selection shape, mirroring `dsr_p_dispatch`'s own cascade —
this package is the concrete implementation of that named candidate shape). No `GDS-07` delta
exists yet for `MUSIC_BASE_LO`/`MUSIC_BASE_HI` — this package's own Documentation Updates (§9) is
where that address is first committed.

## 5. Interfaces

- **`MUSIC_PTR_LO`/`MUSIC_PTR_HI`/`MUSIC_CTR`** (`0xC010`–`0xC00F`, existing, unchanged addresses)
  — reused for playback exactly as today; this package writes them more often (at every screen
  redraw and biome-branch override) instead of only once at boot.
- **New: `MUSIC_BASE_LO`/`MUSIC_BASE_HI`** (prospective `0xC69B`–`0xC69C`, the next free WRAM
  bytes after `LEDGER`'s own `0xC69A` end per `GDS-07` — **to be confirmed against the tree's
  actual state at implementation time**, since `IP-1022`/`IP-1033`/`IP-1105`/`IP-1106` may claim
  WRAM first) — holds the currently-selected track's own base address, read by `music_tick`'s
  loop-restart branch in place of the hardcoded `mus_reset` patch constant.
- **`IP-1110`'s own nine `*_mus_lo`/`*_mus_hi` patch-key pairs** (ROM-resident addresses) — read
  by this package's own repoint code, one pair per identity branch.
- **`dsr_p_dispatch`'s own post-`IP-1022` nine-branch cascade** — consumed, not redefined: this
  package adds instructions inside each existing branch, it does not change the branch structure,
  the `CP_n`/`JR_Z` dispatch logic, or the screen-tile/attribute repoint each branch already
  performs.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **WRAM constants block** (near `MUSIC_CTR`/`MUSIC_PTR_LO`/`MUSIC_PTR_HI`, `asm_game.py:36`–
    `38`): add `MUSIC_BASE_LO = 0xC69B` / `MUSIC_BASE_HI = 0xC69C` (addresses to be confirmed
    against the tree's actual free-WRAM state at implementation time, per §5).
  - **`do_screen_redraw`** (`asm_game.py:1311`–`1313`, immediately after the existing
    `TRANSITION_TO`/`GAMESTATE`/`NEED_REDRAW`/`SCORE_DIRTY` writes and before the twelve-way state
    dispatch loop at `asm_game.py:1320`–`1327`): add the default reset — load
    `grass_mus_lo`/`grass_mus_hi`'s own patched address into `MUSIC_PTR_LO`/`MUSIC_PTR_HI` and
    `MUSIC_BASE_LO`/`MUSIC_BASE_HI` (both pairs, same value), reset `MUSIC_CTR` to 1 (mirroring the
    existing boot-init pattern at `asm_game.py:390`–`394`).
  - **`dsr_p_dispatch`'s eight non-Grass `_dsr_family` branches** (`asm_game.py:1400`–`1410`,
    post-`IP-1022` nine-branch form — **this package's own Files to Modify cites the branches by
    identity name, not by line number, since `IP-1022` has not shipped and the post-widening line
    numbers do not exist yet; re-derive exact line numbers at implementation time, once `IP-1022`
    is `VERIFIED`**): inside each of Water/Sand/Stone/Brick/Village/Cave/Desert/Plains's own
    branch (every identity except Grass), after the existing `LD_DE_nn(0)`/`LD_BC_nn(0)`
    tile/attribute patch-loads, add the identity's own `*_mus_lo`/`*_mus_hi` repoint into
    `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/`MUSIC_BASE_LO`/`MUSIC_BASE_HI` plus a `MUSIC_CTR` reset to 1.
    The Grass branch is unmodified — step 1's own default already points there.
  - **`music_tick`** (`asm_game.py:1256`–`1270`): change the loop-restart branch
    (`asm_game.py:1262`–`1263`) from `LD_HL_nn(0); patches['mus_reset'] = rom.pos - 2` (a hardcoded
    build-time constant) to reading `MUSIC_BASE_LO`/`MUSIC_BASE_HI` from WRAM into `H`/`L`
    (mirroring the existing `MUSIC_PTR_LO`/`MUSIC_PTR_HI` read pattern at `asm_game.py:1260`–
    `1261`). The `patches['mus_reset']` key and its `build_rom.py` patch line
    (`build_rom.py:144`) are retired — no longer needed once the reset target is a WRAM read
    instead of a build-time-patched constant.
  - **Boot-init block** (`asm_game.py:390`–`394`): add `MUSIC_BASE_LO`/`MUSIC_BASE_HI`
    initialization alongside the existing `MUSIC_PTR_LO`/`MUSIC_PTR_HI` writes, for defensive
    correctness before the first `do_screen_redraw` call (the Technical Work Breakdown's own
    supersession sweep found this block becomes functionally redundant once `do_screen_redraw`'s
    own default fires, but leaving it — now extended to the two new fields — is harmless and
    avoids any first-frame ordering risk).
- **Modify: `build_rom.py`**: remove the `patches['mus_reset']` patch line (`build_rom.py:144`,
  retired per the `music_tick` change above) — confirm at implementation time that no other code
  references this key before removing it (grep `mus_reset` across the tree).
- **Modify: `test_rom.py`**: no existing check reads `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/`MUSIC_CTR` or
  `mus_reset` today (confirmed by this planning pass's own grep, `test_rom.py:2269`'s only mention
  is a comment, not an assertion) — no existing check needs correction, only new checks are added
  (§8).

## 7. Implementation Tasks

Ordered: (1) confirm `IP-1022` is `VERIFIED` and re-derive `dsr_p_dispatch`'s exact post-widening
branch line numbers by direct re-read (this package cannot start before this — see §12); (2)
confirm `IP-1110` is `VERIFIED` and its nine `*_mus_lo`/`*_mus_hi` patch keys exist; (3) confirm
`MUSIC_BASE_LO`/`MUSIC_BASE_HI`'s proposed address against the tree's actual free-WRAM state at
that time (re-derive, do not assume `0xC69B`); (4) add the two new WRAM constants; (5) add
`do_screen_redraw`'s own default-reset snippet; (6) add each of the eight non-Grass branches' own
override snippet; (7) change `music_tick`'s reset branch to read `MUSIC_BASE_LO`/`MUSIC_BASE_HI`;
(8) retire `patches['mus_reset']` from both `asm_game.py` and `build_rom.py`, confirmed by grep
that nothing else references it; (9) extend boot-init with the two new fields; (10) write the new
`test_rom.py` checks (§8); (11) full suite run — every existing check must still pass unchanged
(this package adds new WRAM/behavior, touches no existing assertion's own expected value); (12)
documentation updates (§9).

## 8. Tests to Add

New `test_rom.py` suite (next available `Tnn`, confirm exact number at implementation time — this
session's own precedent of suite-number collisions during concurrent planning, `T25`'s own
renaming history, means the number is not fixed here):

- **Selection correctness:** for each of the nine biome-family identities, force the player into a
  region of that identity during `PLAYING` (direct WRAM force, mirroring this session's own
  established direct-force verification pattern used for the maze-blocked edge-indicator content
  review), drive one frame, and assert `MUSIC_PTR_LO`/`MUSIC_PTR_HI` point at that identity's own
  `*_mus_lo`/`*_mus_hi`-patched address. **Only the identities `dsr_p_dispatch`'s own cascade
  actually reaches at implementation time are checkable** — if `IP-1022` shipped exactly nine
  branches (its own Definition of Done requires this), all nine are checkable here.
- **Main-theme fallback:** for each non-`PLAYING` `GAMESTATE` (all eleven others), force entry and
  assert `MUSIC_PTR_LO`/`MUSIC_PTR_HI` point at `grass_mus_lo`/`grass_mus_hi`'s own address (the
  main theme).
- **Loop-restart correctness (the `music_tick` fix, §2):** force a non-Grass identity's own
  sub-theme selected, advance `MUSIC_CTR`/simulate ticks past that sub-theme's own note count
  until its terminal `0xFF` is reached, and assert `music_tick` resets `MUSIC_PTR_LO`/
  `MUSIC_PTR_HI` back to that **same sub-theme's own start address** (`MUSIC_BASE_LO`/
  `MUSIC_BASE_HI`'s value), not the main theme's — the specific regression this package's own §2
  fix prevents.
- **Transition timing:** confirm the track switches within one frame of `TRANSITION_TO` taking
  effect (`FR-7110`'s own "within one frame" Acceptance Criteria) — a single-frame-advance check
  after a forced state transition.

## 9. Documentation Updates

- `docs/architecture/07-data-model.md`: new entry for `MUSIC_BASE_LO`/`MUSIC_BASE_HI` (confirmed
  address, once implementation settles it against the tree's actual state), dated and citing this
  package and `FR-7110`/`ADR-0019` point 6.
- `docs/requirements/01-functional-requirements.md`: `FR-7110`'s own Notes gains a line marking it
  Implemented once this package ships, citing `IP-1111` and the concrete selection-mechanism shape
  chosen (§2).
- `docs/features/FS-111-procedural-music-generation.md`: Open Questions 1 and 4 marked resolved
  (the selection mechanism itself, and the citation-precision note — this package's own mechanism
  is `dsr_p_dispatch`-based, confirming `FS-111`'s own Open Question 4 correction was the accurate
  starting point, not `ADR-0019`'s own `_score_bar` citation).
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Entering a region of any of the nine biome-family identities during `PLAYING` results in that
  identity's own sub-theme playing within one frame — confirmed for however many identities
  `dsr_p_dispatch` dispatches at implementation time (nine, if `IP-1022` shipped its own full
  Definition of Done).
- Entering any non-`PLAYING` `GAMESTATE` results in the main theme playing within one frame.
- A sub-theme, once selected, loops correctly from its own start on reaching its own terminal
  `0xFF` — never silently falling back to the main theme mid-play.
- `patches['mus_reset']` is fully retired from both `asm_game.py` and `build_rom.py`, confirmed by
  grep.
- No finite-mode/Infinite-Mode generation, dispatch-cascade branch *structure*, or screen-tile/
  attribute repoint logic is touched beyond the added music-repoint instructions — confirmed by
  diff scope against `IP-1022`'s own shipped state.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, zero expected-value changes in any existing check.
- [ ] New selection-correctness checks (§8) pass for every identity `dsr_p_dispatch` dispatches.
- [ ] New main-theme-fallback checks (§8) pass for all eleven non-`PLAYING` states.
- [ ] New loop-restart-correctness check (§8) passes — the `music_tick` fix confirmed by direct
      WRAM-state assertion, not merely absence of a crash.
- [ ] Direct diff: `dsr_p_dispatch`'s own `CP_n`/`JR_Z` dispatch structure and each branch's
      existing tile/attribute repoint logic byte-for-byte unchanged beyond the added music-repoint
      instructions.
- [ ] Direct diff: no finite-mode generation code (`generate_world`, `worldgen.py`) touched.
- [ ] `grep -n "mus_reset"` across the tree returns zero matches post-implementation.

## 12. Dependencies

- **`IP-1110`** (`NOT STARTED`, gated only on G3) — the nine `*_mus_lo`/`*_mus_hi` patch-key pairs
  this package repoints to. A real unshipped prerequisite, not merely a co-authorization.
- **`IP-1022`** (`BLOCKED` — itself depends on `IP-1033`) — `dsr_p_dispatch`'s own nine-branch
  cascade this package adds override instructions inside. This package cannot even be fully
  authored at the line-number level (§6's own explicit caveat) until `IP-1022` ships — a genuine,
  two-level-removed unshipped prerequisite, the deepest dependency in this Feature's own chain,
  mirroring `IP-1106`'s own precedent for exactly this kind of cascade-sharing block.
- **Not a code dependency, but a verification-completeness one:** `FEAT-10000` (Infinite Mode)
  being release-scheduled — this package's own selection mechanism works identically for both
  modes (they share `dsr_p_dispatch`), so no code change depends on Infinite Mode's own scheduling
  status, but full verification across Infinite Mode's own nine-identity range additionally needs
  `IP-1106` (also `BLOCKED` on `IP-1022`) to have shipped, per `FS-111`/[FP-04](../../feature-planning/04-feature-dependency-graph.md)'s
  own named two-source sequencing risk.

## 13. Risks

Medium — the real, named two-level dependency on `IP-1022` (itself `BLOCKED` on `IP-1033`) means
this package's own `Files to Modify` (§6) cannot cite exact post-widening line numbers today, only
identity names and the current (pre-widening) branch structure's own shape — a deliberate,
disclosed gap in this package's own specificity, not an oversight (re-derivation is listed as
Implementation Task 1). **A second risk, independent of the above:** the `music_tick` loop-restart
fix (§2) changes a routine every other Feature's own music playback already depends on
(`music_tick` runs unconditionally every frame, per `ADR-0019`'s own Context) — a regression here
would be silently audible-only (no crash, no test failure unless the new loop-restart check
specifically catches it), which is why §8's own loop-restart-correctness check is named as a
Definition-of-Done item, not an optional nice-to-have.

## 14. Rollback Considerations

Revert `do_screen_redraw`'s default-reset snippet, the eight branch-level override snippets,
`music_tick`'s reset-branch change (restoring the hardcoded `mus_reset` patch), the two new WRAM
constants and their boot-init writes, and `build_rom.py`'s `mus_reset` patch line. No SRAM/save-
format dependency — `MUSIC_BASE_LO`/`MUSIC_BASE_HI` are transient, session-only WRAM (never
persisted), so no version bump or migration path is needed.
