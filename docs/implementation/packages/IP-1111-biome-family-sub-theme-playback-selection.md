# IP-1111 — Biome-Family Sub-Theme Playback Selection

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

**Revision history:** Revised 2026-07-17 (`07-implementation-planning`, the touch `IP-1110`'s own
Outstanding Issue requested): §2/§5/§6/§7/§8 updated to consume the interface `IP-1110` actually
shipped — a flat, biome-id-indexed ROM address table (`music_table`, mirroring `zc_table`'s
precedent) — instead of the originally-planned per-identity `*_mus_lo`/`*_mus_hi` named patch-key
pairs, which were never created (see `IP-1110`'s own recorded deviation). The table indexing also
replaces the original eight per-branch override snippets with **one shared subroutine and one
call site**, a real simplification the shipped interface enables. Line-number citations
re-derived against the current tree (`IP-1022` `VERIFIED` 2026-07-17 shipped all nine
`dsr_p_dispatch` branches, closing §6's original "cannot cite post-widening line numbers yet"
caveat). Same objective, same requirements, same authorization ("Build all six," 2026-07-16) — an
interface-consumption correction, not new scope.

## 1. Package ID

`IP-1111` — implements [**FS-111**](../../features/FS-111-procedural-music-generation.md)
Workflow B (`FEAT-7100`, Epic `EP-7000`) — grounded by `ADR-0019` point 6 and `FR-7110`
(biome-family-identity-keyed sub-theme playback selection). Originally planned against commit
`7cb452f`; revised against the post-`IP-1022`/`IP-1106` tree (head `aa9ba8c`).

## 2. Objective

During `PLAYING` (either mode), switch the currently-playing music track to the sub-theme matching
the player's current region's biome-family identity; outside `PLAYING`, play the main theme.

**Resolves `FS-111`'s Open Question 1** (the selection-mechanism shape): hooks into two
already-shipped trigger points rather than adding a new per-frame poll or new "last-known
identity" WRAM state —

1. **`do_screen_redraw`'s state-entry block** (`asm_game.py:1343`–`1345`, immediately after the
   existing `TRANSITION_TO`→`GAMESTATE`/`NEED_REDRAW`/`SCORE_DIRTY` writes and before the
   `setup_zone_collects` gate) gains an unconditional **default reset to the main theme**: load
   `A = 2` (Grass's biome-id — the zero-transform anchor whose `music_table` entry *is* the main
   theme's own address, per `IP-1110`'s Grass-anchor decision) and call the new shared
   `music_select` subroutine (below). This fires on **every** screen redraw, in every state —
   including `PLAYING`.
2. **`dsr_p_dispatch`'s entry point** (`asm_game.py:1424`, where both the finite path — a
   `REGION_GRAPH` read — and the Infinite Mode path — `INF_WINDOW`'s center-cell low nibble —
   have just converged with **A = the current region's biome-id**) gains a single **override**
   call to the same `music_select` subroutine, before the `CP_n`/`JR_Z` cascade runs. Because
   `music_table` is biome-id-indexed, one call site covers all nine identities — no per-branch
   snippets, and no Grass special case (Grass's own entry is the main theme, so its "override"
   is a harmless rewrite of the same address step 1 already set).

**`music_select` (new shared subroutine):** on entry `A = biome-id (0-8)`; computes
`HL = music_table + 2*A` (the table's base address lands via a new `patches['music_tbl']` key,
resolved by `build_rom.py` exactly as `patches['zc_table']` already is), reads the entry's
lo/hi bytes, writes them to `MUSIC_PTR_LO`/`MUSIC_PTR_HI` **and** `MUSIC_BASE_LO`/`MUSIC_BASE_HI`
(both pairs, same value), resets `MUSIC_CTR` to 1 (mirroring the boot-init pattern,
`asm_game.py:422`–`426`), and **must preserve A** (the caller's cascade dispatches on it —
`PUSH_AF`/`POP_AF` bracket or equivalent).

This fires the moment a region's screen is drawn — the same moment the screen's own biome-family
tile content changes — satisfying `FR-7110`'s own "within one frame of the region becoming
current" Acceptance Criteria without any new polling logic, and correctly resets to the main theme
the moment `PLAYING` is left (every other `dsr_*` label runs step 1's default and never reaches
step 2's override).

**A second, load-bearing fix this package also carries** (surfaced by the original planning pass,
not named in `FS-111` — see the Technical Work Breakdown's own "Procedural Music Generation"
section): `music_tick`'s existing loop-restart branch (`asm_game.py:1294`–`1295`) hardcodes its
reset target to the main theme's own address (`patches['mus_reset']`, `asm_game.py:1295`), not
whichever track is currently selected. Without a fix, any sub-theme would silently truncate to a
single pass before falling back to the main theme the moment it loops. This package adds a new
WRAM field (`MUSIC_BASE_LO`/`MUSIC_BASE_HI`) holding the currently-selected track's own base
address, written by `music_select` at every repoint, and changes `music_tick`'s reset branch to
read it instead of the hardcoded `mus_reset` patch constant.

**Scope boundary:** this package does not change `dsr_p_dispatch`'s branch structure, any
branch's tile/attribute/fill repoint logic, or `IP-1022`'s procedural-fill machinery — it inserts
one `CALL` at the dispatch entry and one default-reset snippet upstream, nothing inside the
branches themselves (a further footprint reduction versus the original eight-snippet plan).

## 3. Requirements Covered

`FR-7110` (in full — every one of its Acceptance Criteria across all nine identities;
`dsr_p_dispatch`'s full nine-branch cascade shipped with `IP-1022`, `VERIFIED` 2026-07-17).

## 4. Architecture Components

`ADR-0019` point 6 (identity-keyed selection shape, mirroring `dsr_p_dispatch`'s own cascade —
this package is the concrete implementation of that named candidate shape, now realized as a
single table-indexed subroutine rather than per-branch code). No `GDS-07` delta exists yet for
`MUSIC_BASE_LO`/`MUSIC_BASE_HI` — this package's own Documentation Updates (§9) is where that
address is first committed.

## 5. Interfaces

- **`MUSIC_PTR_LO`/`MUSIC_PTR_HI`/`MUSIC_CTR`** (`0xC010`/`0xC011`/`0xC00F`, existing, unchanged
  addresses) — reused for playback exactly as today; this package writes them more often (at
  every screen redraw and at every `PLAYING` region dispatch) instead of only once at boot.
- **New: `MUSIC_BASE_LO`/`MUSIC_BASE_HI`** (prospective `0xC6B3`–`0xC6B4`, the next free WRAM
  bytes after `IP-1022`'s own `FPS_*` scratch block ends at `FPS_TEMP = 0xC6B2` — **to be
  confirmed against the tree's actual state at implementation time**) — holds the
  currently-selected track's own base address, read by `music_tick`'s loop-restart branch in
  place of the hardcoded `mus_reset` patch constant.
- **`music_table`** (`IP-1110`'s shipped interface — 18 bytes ROM-resident, nine little-endian
  addresses in biome-id order 0=Water…8=Plains, emitted by `build_rom.py` immediately after the
  nine track blocks) — the sub-theme address source this package indexes by biome-id. **New:
  `patches['music_tbl']`** — a 16-bit patch key created at `music_select`'s own `LD_HL_nn(0)`
  placeholder and resolved by `build_rom.py` (`p16(patches['music_tbl'], music_table_addr)`),
  exactly mirroring the existing `patches['zc_table']` pattern (`asm_game.py:2079`,
  `build_rom.py:263`).
- **`dsr_p_dispatch`'s nine-branch cascade** (`asm_game.py:1424`–`1435`, shipped by `IP-1022`) —
  consumed, not redefined: this package adds one `CALL` at the dispatch entry (where A = biome-id
  on both mode paths); the `CP_n`/`JR_Z` logic and every branch body are untouched.
- **`patches['mus_lo']`/`patches['mus_hi']`** (boot-init byte patches, `asm_game.py:422`/`424`) —
  unchanged: boot still initializes `MUSIC_PTR_*` to the main theme; this package additionally
  initializes `MUSIC_BASE_*` there (defensive first-frame correctness, §6).
- **`patches['mus_reset']`** (`asm_game.py:1295`, resolved at `build_rom.py:207`) — **retired**
  by this package (replaced by the `MUSIC_BASE_*` WRAM read).

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **WRAM constants block** (after `FPS_TEMP = 0xC6B2`, `asm_game.py:255`): add
    `MUSIC_BASE_LO = 0xC6B3` / `MUSIC_BASE_HI = 0xC6B4` (addresses to be confirmed against the
    tree's actual free-WRAM state at implementation time, per §5).
  - **New: `music_select` subroutine** — per §2: entry `A = biome-id`; `PUSH_AF`;
    `HL = music_tbl + 2*A` (ADD_A_A + the established `LD_HL_nn(0)`-placeholder-plus-`ADD_HL_DE`
    indexing pattern `setup_zone_collects` already uses at `asm_game.py:2077`–`2080`); read
    lo/hi via `LD_A_HLI`; write `MUSIC_PTR_LO`/`MUSIC_BASE_LO` and `MUSIC_PTR_HI`/
    `MUSIC_BASE_HI`; `MUSIC_CTR = 1`; `POP_AF`; `RET`. Placement: near `music_tick`
    (one-job-per-file conventions, ADR-0003).
  - **`do_screen_redraw`** (`asm_game.py:1343`–`1345`, immediately after the
    `TRANSITION_TO`/`GAMESTATE`/`NEED_REDRAW`/`SCORE_DIRTY` writes, before the
    `setup_zone_collects` gate at `asm_game.py:1348`): add the default reset — `LD_A_n(2)`
    (Grass's biome-id, the main-theme anchor) + `CALL music_select`.
  - **`dsr_p_dispatch` entry** (`asm_game.py:1424`, the label itself — A holds the biome-id from
    both the finite `REGION_GRAPH` read at `asm_game.py:1412` and the infinite
    `INF_WINDOW`-center read at `asm_game.py:1417`–`1418`): insert `CALL music_select` as the
    first instruction after the label, before `CP_n(0)`. `music_select`'s own A-preservation
    contract (§2) keeps the cascade's dispatch value intact.
  - **`music_tick`** (`asm_game.py:1289`–`1302`): change the loop-restart branch
    (`asm_game.py:1294`–`1295`) from `LD_HL_nn(0); patches['mus_reset'] = rom.pos - 2` (a
    hardcoded build-time constant) to reading `MUSIC_BASE_HI`/`MUSIC_BASE_LO` from WRAM into
    `H`/`L` (mirroring the existing `MUSIC_PTR_*` read pattern at `asm_game.py:1292`–`1293`).
    The `patches['mus_reset']` key is retired.
  - **Boot-init block** (`asm_game.py:422`–`426`): add `MUSIC_BASE_LO`/`MUSIC_BASE_HI`
    initialization alongside the existing `MUSIC_PTR_LO`/`MUSIC_PTR_HI` writes (same patched
    values via `mus_lo`/`mus_hi`), for defensive correctness before the first `do_screen_redraw`
    call — functionally redundant once the redraw default fires, kept to avoid any first-frame
    ordering risk (the original plan's own supersession-sweep finding, unchanged).
- **Modify: `build_rom.py`**: add `p16(patches['music_tbl'], music_table_addr)` beside the
  existing `zc_table` resolution (`build_rom.py:263`); remove the `patches['mus_reset']` patch
  line (`build_rom.py:207`, retired per the `music_tick` change) — confirm at implementation time
  by grep that nothing else references `mus_reset` before removing it.
- **Modify: `test_rom.py`**: no existing check reads `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/`MUSIC_CTR` or
  `mus_reset` today (re-confirmed by this revision's own grep — the only mentions are comments) —
  no existing check needs correction, only new checks are added (§8).

## 7. Implementation Tasks

Ordered: (1) confirm `IP-1022`/`IP-1110` are both `VERIFIED` (both are, 2026-07-17/2026-07-17)
and re-confirm the §6 line citations by direct read; (2) confirm `music_table`'s emission and
`zc_table`'s patch-resolution pattern in `build_rom.py` by direct read; (3) confirm
`MUSIC_BASE_LO`/`MUSIC_BASE_HI`'s proposed `0xC6B3`/`0xC6B4` against the tree's actual free-WRAM
state (re-derive, do not assume); (4) add the two new WRAM constants; (5) implement
`music_select` (with the A-preservation bracket); (6) add `do_screen_redraw`'s default-reset
snippet; (7) insert the single `CALL music_select` at `dsr_p_dispatch`'s entry; (8) change
`music_tick`'s reset branch to read `MUSIC_BASE_*`; (9) retire `patches['mus_reset']` from both
`asm_game.py` and `build_rom.py`, confirmed by grep; (10) add `patches['music_tbl']`'s
`build_rom.py` resolution; (11) extend boot-init with the two new fields; (12) write the new
`test_rom.py` checks (§8); (13) full suite run — every existing check must still pass unchanged;
(14) documentation updates (§9).

## 8. Tests to Add

New `test_rom.py` suite (next available `Tnn` — `T28` as of this revision; confirm at
implementation time):

- **Selection correctness:** for each of the nine biome-family identities, force a region of that
  identity current during `PLAYING` (direct WRAM force + redraw — `T13.a`'s `REGION_GRAPH` force
  for finite mode; `T26.i`'s `INF_WINDOW`-center force pattern is the Infinite Mode equivalent,
  at least one identity re-checked via that path to prove the shared entry point serves both
  modes), and assert `MUSIC_PTR_LO`/`MUSIC_PTR_HI` == `music_table[biome-id]`'s own address
  (read the expected value directly from the built ROM's own table bytes, not recomputed).
- **Main-theme fallback:** for each non-`PLAYING` `GAMESTATE` (all eleven others), force entry
  and assert `MUSIC_PTR_LO`/`MUSIC_PTR_HI` == `music_table[2]` (Grass = the main theme).
- **Loop-restart correctness (the `music_tick` fix, §2):** force a non-Grass identity's own
  sub-theme selected, tick until its terminal `0xFF` is reached, and assert `music_tick` resets
  `MUSIC_PTR_LO`/`MUSIC_PTR_HI` back to that **same sub-theme's own start address**
  (`MUSIC_BASE_*`'s value), not the main theme's — the specific regression this package's own §2
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
  chosen (§2, the table-indexed single-subroutine form).
- `docs/features/FS-111-procedural-music-generation.md`: Open Questions 1 and 4 marked resolved
  (the selection mechanism itself, and the citation-precision note — this package's own mechanism
  is `dsr_p_dispatch`-based, confirming `FS-111`'s own Open Question 4 correction was the accurate
  starting point, not `ADR-0019`'s own `_score_bar` citation).
- `docs/requirements/04-requirements-traceability-matrix.md`: `FR-7110` row's Implementation
  Package/Test columns filled.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Entering a region of any of the nine biome-family identities during `PLAYING` results in that
  identity's own sub-theme playing within one frame — all nine identities, both trigger paths
  (finite `REGION_GRAPH`; at least one identity confirmed via the Infinite Mode `INF_WINDOW`
  path too).
- Entering any non-`PLAYING` `GAMESTATE` results in the main theme playing within one frame.
- A sub-theme, once selected, loops correctly from its own start on reaching its own terminal
  `0xFF` — never silently falling back to the main theme mid-play.
- `patches['mus_reset']` is fully retired from both `asm_game.py` and `build_rom.py`, confirmed by
  grep.
- No dispatch-cascade branch *structure*, screen-tile/attribute repoint logic, or
  `IP-1022` fill machinery is touched — this package's `dsr_p_dispatch` footprint is exactly one
  inserted `CALL` at the entry label — confirmed by diff scope.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, zero expected-value changes in any existing check.
- [ ] New selection-correctness checks (§8) pass for all nine identities, including at least one
      via the Infinite Mode window path.
- [ ] New main-theme-fallback checks (§8) pass for all eleven non-`PLAYING` states.
- [ ] New loop-restart-correctness check (§8) passes — the `music_tick` fix confirmed by direct
      WRAM-state assertion, not merely absence of a crash.
- [ ] Direct diff: `dsr_p_dispatch`'s own `CP_n`/`JR_Z` structure and every branch body
      byte-for-byte unchanged beyond the single inserted `CALL` at the entry.
- [ ] Direct diff: no generation code (`generate_world`, `inf_materialize_region`,
      `worldgen.py`) touched.
- [ ] `grep -n "mus_reset"` across the tree returns zero matches post-implementation.
- [ ] `music_select` confirmed to preserve A across the call (direct code read) — the cascade
      dispatches on it.

## 12. Dependencies

- **`IP-1110`** (`VERIFIED` 2026-07-17, `VR-1110`) — `music_table`, the shipped sub-theme address
  source this package indexes.
- **`IP-1022`** (`VERIFIED` 2026-07-17, `VR-1022`) — `dsr_p_dispatch`'s nine-branch cascade and
  its single biome-id-in-A entry point this package hooks.
- **`IP-1106`** (`COMPLETE`, own `09` pass owed) — not a code dependency (the selection mechanism
  reads whatever biome-id the dispatch already carries, either mode), but full nine-identity
  verification *via the Infinite Mode path* exercises `IP-1106`'s widened draw; the §8 Infinite
  Mode spot-check uses the same direct `INF_WINDOW` force `T26.i` established, which works
  regardless. No sequencing block.

## 13. Risks

Low-Medium (down from Medium: the original plan's dominant risk — `IP-1022`'s unshipped cascade
making line-number-level authoring impossible — is resolved; citations in §6 are against the
live tree). **The remaining real risk** is unchanged: the `music_tick` loop-restart fix (§2)
changes a routine every Feature's music playback already depends on (`music_tick` runs
unconditionally every frame, per `ADR-0019`'s own Context) — a regression here would be silently
audible-only (no crash, no test failure unless the new loop-restart check specifically catches
it), which is why §8's own loop-restart-correctness check is a Definition-of-Done item, not an
optional nice-to-have. **New, minor:** `music_select` runs inside `do_screen_redraw`'s LCD-off
bracket (both call sites), so no VBlank-timing exposure (`NFR-1300`) — but its A-preservation
contract is load-bearing for the dispatch cascade; the Verification Checklist names it
explicitly.

## 14. Rollback Considerations

Revert `do_screen_redraw`'s default-reset snippet, the single `dsr_p_dispatch` entry `CALL`, the
`music_select` subroutine, `music_tick`'s reset-branch change (restoring the hardcoded
`mus_reset` patch and its `build_rom.py` line), the `music_tbl` patch resolution, the two new
WRAM constants and their boot-init writes. No SRAM/save-format dependency —
`MUSIC_BASE_LO`/`MUSIC_BASE_HI` are transient, session-only WRAM (never persisted), so no version
bump or migration path is needed.
