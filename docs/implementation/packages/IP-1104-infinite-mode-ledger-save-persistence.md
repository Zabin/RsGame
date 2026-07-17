# IP-1104 — Infinite Mode: Visited-Region-Ledger Save Persistence

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1104` — implements part of [**FS-110**](../../features/FS-110-infinite-mode.md) (`FEAT-10000`,
Epic `EP-6000`, `Future` bucket). Covers Workflow D in full (the `persist` verb). Last package in
the tranche's critical path.

## 2. Objective

Extend `save_to_sram`/`try_load_save` with a new, ledger-based save shape for Infinite Mode:
player position (region row/col), the visited-region ledger (which regions have been visited and
whether their treasure is collected, FIFO-bounded at 128 entries), the running treasure count, and
the persistent top-3 table — bumping `SAVE_VERSION_VAL` to extend the existing monotonic sequence.

**Amended 2026-07-16 per `BL-0119`** (filed during `IP-1103`'s own implementation, run #161): the
ledger now additionally maintains a **WRAM working copy**, consulted by `IP-1102`'s
`inf_ensure_window` on *every* center-cell materialization (new-game entry, ordinary in-session
navigation, and post-load re-materialization alike) — not only on the save/load boundary the
original §6 text named. This closes a real gap the original plan left open: a collected
treasure would otherwise respawn whenever the player left the materialized window and walked
back within the same session, since nothing before this amendment ever consulted the ledger
outside `try_load_save`'s own restore branch. See §6/§8/§10/§13 below for the amendment's full
shape — it also *simplifies* the original design (§13), not just patches it: the ledger no
longer needs an SRAM read on every single treasure collection, only at explicit save points.

## 3. Requirements Covered

FR-10500 (save/load); FR-10600 (indefinitely-resumable run — "continue" always resumes exactly
where the player left off); NFR-5400 (ledger round-trip integrity, sized this pass).

## 4. Architecture Components

[ADR-0006](../../architecture/adr/ADR-0006-mbc1-battery-sram.md) (MBC1+RAM+BATTERY mechanism,
single save slot, unchanged) · this package's own Technical Work Breakdown sizing decisions (128
entries × 5 bytes, FIFO eviction, `SAVE_VERSION_VAL` `0x04`→`0x05`).

## 5. Interfaces

- **The existing `save_to_sram`/`try_load_save` routines and their existing single MBC1-enable
  bracket** (`FEAT-5000`, extended not replaced — mirrors `IP-1050`'s own extension pattern
  exactly: new fields added inside the existing bracket, no second bracket opened).
- **`SAVE_VERSION_ADDR`/`SAVE_VERSION_VAL`** (`0xA012`, existing) — bumped `0x04`→`0x05`, extending
  the strictly-monotonic sequence `IP-9110` last advanced (Technical Work Breakdown's own
  resolution of `OQ7` — a single version guard covers both save shapes, selected by the persisted
  `GAME_MODE` byte, not a second parallel version scheme).
- **The existing `memcpy` subroutine** (`IP-1050`'s own precedent) — reused for the 642-byte
  ledger transfer (count + cursor + 640-byte entry table, one contiguous block both sides, see
  §6), not an unrolled loop.
- **`IP-1102`'s `inf_ensure_window`** (**amended by this package, 2026-07-16, per `BL-0119`** —
  the same "a later package extends an already-`VERIFIED` upstream routine because it owns the
  data the routine now needs to consult" pattern `IP-1103` itself already established on this
  identical routine for `INF_TREASURE_HERE`'s own presence-predicate write). This package adds a
  ledger cross-reference immediately after that existing write — see §6.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New SRAM constants** (first unclaimed bytes past `SRAM_SCOREITEM`'s own end, `0xA0C0`):
    `SRAM_GAME_MODE = 0xA0C1` (1 byte, mirrors `GAME_MODE`), `SRAM_INF_ROW = 0xA0C2` (2 bytes),
    `SRAM_INF_COL = 0xA0C4` (2 bytes), `SRAM_RUNNING_TREASURE_COUNT = 0xA0C6` (2 bytes),
    `SRAM_TOP_SCORE_TABLE = 0xA0C8` (6 bytes — persists across new games, not per-run: a "new
    game" starting a fresh `RUNNING_TREASURE_COUNT` at Infinite Mode entry does not clear this
    table, the same "persistent high score, distinct from per-run state" split `ADR-0017` point 4
    already frames), `SRAM_LEDGER_COUNT = 0xA0CE` (1 byte, number of valid entries, 0-128),
    `SRAM_LEDGER_CURSOR = 0xA0CF` (1 byte, FIFO write cursor, 0-127), `SRAM_LEDGER = 0xA0D0` (640
    bytes, `0xA0D0`–`0xA34F`, 128 entries × 5 bytes: row signed 16-bit, col signed 16-bit,
    collected-flag 1 byte). `SRAM_LEDGER_COUNT`/`SRAM_LEDGER_CURSOR`/`SRAM_LEDGER` form one
    contiguous 642-byte block (`0xA0CE`–`0xA34F`), deliberately laid out to mirror the new WRAM
    block below byte-for-byte, so a single `memcpy` moves the whole thing either direction.
  - **New WRAM constants (added by this amendment, `BL-0119`), first unclaimed bytes past
    `IP-1101`'s own `INF_MZ_TCOL` end (`0xC418`):** `LEDGER_COUNT = 0xC419` (1 byte),
    `LEDGER_CURSOR = 0xC41A` (1 byte), `LEDGER = 0xC41B` (640 bytes, `0xC41B`–`0xC69A`) — the
    **live, in-session working copy** of the ledger, identical 5-byte-per-entry format to
    `SRAM_LEDGER`. `LEDGER_COUNT`/`LEDGER_CURSOR`/`LEDGER` form one contiguous 642-byte block
    (`0xC419`–`0xC69A`), the exact WRAM mirror of the SRAM block above (same field order, same
    sizes) — this is what makes the save/load `memcpy` a single 642-byte transfer rather than
    three separate ones. 642 bytes is a substantial single WRAM addition (§13); comfortably
    within the confirmed ~3.1 KiB bank-0 headroom (`R111`/`GDS-07` §6) even after the tranche's
    prior ~23-byte additions — re-affirmed at build time via a direct SRAM/WRAM-map audit, not
    merely computed here. `LEDGER_COUNT`/`LEDGER_CURSOR` sit outside the `0xC000`–`0xC2FF`
    boot-clear range and are explicitly boot-cleared to 0 (the same targeted-clear pattern
    `GAME_MODE`/`RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE` already established) — a fresh
    cartridge must start with an empty ledger, not garbage. `LEDGER`'s own 640 bytes need **no**
    boot clear: `LEDGER_COUNT == 0` gates validity, the identical "count gates array validity"
    convention `COLL_COUNT`/`COLL_DATA` already use project-wide. **Whether `LEDGER_COUNT` also
    resets to 0 at a fresh Infinite Mode *new-game* entry (as opposed to only at boot) is left
    exactly as open as `IP-1103`'s own identical `RUNNING_TREASURE_COUNT` question (§13 there) —
    both are the same run/session-shape question `BL-0112` hasn't resolved yet, and this package
    does not silently pick an answer for one while leaving the other honestly open.**
  - **`inf_ensure_window` (`IP-1102`'s existing routine, amended — see §5):** immediately after
    the existing center-cell (`_idx == 4`) write of `INF_TREASURE_HERE` from `INF_MZ_TREASURE`
    (`IP-1103`'s own addition), this package adds a bounded lookup against the **WRAM** `LEDGER`:
    search its first `LEDGER_COUNT` entries for a matching `(row, col)` — the same
    `(INF_MZ_ROW, INF_MZ_COL)` pair already live in registers/WRAM at that point in the loop —
    with a set collected-flag; if found, overwrite `INF_TREASURE_HERE` to 0 (collected,
    regardless of what the fresh presence predicate says), otherwise leave `IP-1103`'s own write
    untouched. This one change is what closes `BL-0119`: `inf_ensure_window` is the *only* call
    site that ever writes `INF_TREASURE_HERE` (new-game entry, every ordinary in-session
    navigation transition via `czt_infinite`, and — after this package's own `try_load_save`
    change below populates the WRAM ledger — the post-load re-materialization too), so fixing it
    once here fixes every call site uniformly, rather than requiring a second, load-path-only
    special case (the original §6 text's own now-superseded approach, below).
  - **`save_to_sram` (existing label):** inside the existing single MBC1-enable bracket, gains a
    `GAME_MODE`-gated block — when `GAME_MODE == 1`: write `SRAM_GAME_MODE`, `SRAM_INF_ROW`/`COL`
    (from `INF_ROW`/`INF_COL`), `SRAM_RUNNING_TREASURE_COUNT`, `SRAM_TOP_SCORE_TABLE` (always
    written regardless of mode — the persistent table, §above), and the ledger block — a single
    642-byte `memcpy` from WRAM `LEDGER_COUNT` (source) to SRAM `SRAM_LEDGER_COUNT` (dest),
    **not** three separate reads of a live SRAM-resident structure (the amendment above makes the
    WRAM copy authoritative during play; SRAM is now purely the save-time backing store). When
    `GAME_MODE == 0` (finite mode saving): `SRAM_GAME_MODE` still written (`=0`), the
    Infinite-Mode-only fields (`SRAM_INF_ROW`/`COL`/ledger) left as whatever they last held —
    never read back unless `GAME_MODE` on load says `1` (§ below), so stale bytes are harmless,
    mirroring `ADR-0010`'s own "unread fields are inert" framing for the finite mode's own
    version-guard discipline.
  - **`try_load_save` (existing label):** version check widened to accept `0x05`; on a matching
    version, restores `GAME_MODE` first, then branches: `GAME_MODE == 0` restores exactly as
    today (unchanged); `GAME_MODE == 1` restores `INF_ROW`/`INF_COL`, `RUNNING_TREASURE_COUNT`,
    `TOP_SCORE_TABLE`, and the ledger block — a single 642-byte `memcpy` from SRAM `SRAM_LEDGER_
    COUNT` (source) into WRAM `LEDGER_COUNT` (dest), populating the WRAM working copy —
    **then calls `IP-1102`'s `inf_ensure_window`** to re-materialize the 3×3 working set around
    the restored position (no region's biome/connectivity is ever itself persisted — re-derived
    on demand, `FR-10500`'s own explicit requirement). Because `inf_ensure_window` itself now
    always consults the (freshly-populated) WRAM ledger, this restore path needs **no separate
    ledger cross-reference of its own** — the original §6 text's load-path-only lookup is
    superseded by the uniform fix in `inf_ensure_window` above, not duplicated alongside it.
  - **New subroutine `inf_ledger_mark_collected`** (the forward call `IP-1103`'s own collection
    branch names, currently a `RET` stub) — inputs: current `INF_ROW`/`INF_COL`. Operates on the
    **WRAM** `LEDGER` (amended — the original §6 text specified `SRAM_LEDGER` directly, which
    would have required an MBC1-enable/disable bracket around every single treasure collection, a
    correctness/performance cost this amendment avoids entirely). Searches `LEDGER`'s first
    `LEDGER_COUNT` entries for a matching `(row, col)`; if found, sets its collected-flag; if not
    found (first visit to this region) and `LEDGER_COUNT < 128`, appends a new entry (row, col,
    collected=1) and increments `LEDGER_COUNT`; if not found and the ledger is full
    (`LEDGER_COUNT == 128`), overwrites the entry at `LEDGER_CURSOR` (FIFO eviction, Technical
    Work Breakdown's own resolution of `OQ5`) and advances `LEDGER_CURSOR` modulo 128 (a
    `AND 0x7F` mask, no `DIV`). No SRAM access, no MBC1 bracket — safe to call every frame a
    collection occurs, mirroring `check_collisions`' own existing branches (none of which touch
    SRAM either).
  - **`try_load_save`'s existing pre-upgrade rejection path (existing behavior, unchanged):** a
    version-mismatched save (anything other than `0x05`) is still treated as pre-upgrade — no
    `continue` option offered, mirroring `IP-9070`'s own precedent exactly. This includes every
    prior version value (`0x01`-`0x04`), none of which ever wrote `GAME_MODE` — confirming a
    pre-Infinite-Mode save cannot be misread as an Infinite Mode save (`FS-110` §12's named edge
    case, resolved: rejected outright by the version guard, not partially loaded).

## 7. Implementation Tasks

Ordered: (1) new SRAM constants **and new WRAM ledger constants** (`LEDGER_COUNT`/
`LEDGER_CURSOR`/`LEDGER`, amended); (2) boot-clear extension for `LEDGER_COUNT`/`LEDGER_CURSOR`;
(3) **`inf_ensure_window`'s ledger cross-reference amendment** (the `BL-0119` fix — extend the
existing center-cell `INF_TREASURE_HERE` write with the WRAM `LEDGER` lookup); (4)
`inf_ledger_mark_collected` (search/append/FIFO-evict, against **WRAM** `LEDGER`, amended); (5)
wire `IP-1103`'s own collection branch (already names this forward call) to the now-implemented
`inf_ledger_mark_collected`; (6) `save_to_sram`'s `GAME_MODE`-gated write block (position,
running count, top-3 table, the 642-byte ledger block via one `memcpy`); (7) `SAVE_VERSION_VAL`
bump `0x04`→`0x05`, `try_load_save`'s version-check widening; (8) `try_load_save`'s
`GAME_MODE`-gated restore block (position, running count, top-3 table, the 642-byte ledger block
via one `memcpy` — **no separate ledger cross-reference needed here, superseded by task (3)**),
including the `inf_ensure_window` re-materialization call; (9) rebuild ROM; (10) author T27 (see
§8, including the new in-session re-entry check); (11) full suite run; (12) documentation/
traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T27: Infinite Mode — Ledger Save Persistence`**:

- T27.a — two-instance save/reload harness (mirroring `IP-1050`'s own `T15` pattern): materialize
  a region, collect its treasure, move to a second region, save, load in a fresh instance →
  assert `INF_ROW`/`INF_COL`, `RUNNING_TREASURE_COUNT`, and the first region's own collected-state
  (via `INF_TREASURE_HERE` after re-materialization) all restore exactly (AC-5).
- T27.b — no region's biome/connectivity is itself persisted: direct SRAM-byte audit confirms
  `SRAM_LEDGER`'s 5-byte-per-entry format contains no biome/connectivity field, only
  position+collected-flag (AC-5's own explicit "no SRAM field represents biome or connectivity"
  clause).
- T27.c — FIFO eviction: fill the ledger to exactly 128 entries, visit a 129th distinct region →
  assert the entry at the pre-eviction `LEDGER_CURSOR` position (WRAM — where eviction actually
  happens, per the amendment above) is overwritten, all others unchanged, `LEDGER_COUNT` stays at
  128; a follow-up save/load round trip confirms the same state survives the `memcpy` into
  `SRAM_LEDGER`/back.
- T27.d — pre-upgrade rejection: a synthetic `version=0x04` fixture (the pre-Infinite-Mode value)
  → assert "continue" absent, mirroring `T11.d`/`T16.d`'s own established pattern.
- T27.e — finite-mode save round-trip regression: a `GAME_MODE=0` save/load cycle restores
  exactly as before this package (`T15`'s own existing checks, re-run unmodified against the new
  `SAVE_VERSION_VAL`).
- T27.f — indefinite resumability (AC-6): from a loaded Infinite Mode save, attempt every
  reachable input sequence from the equivalent of `PLAYING` — assert none forcibly ends the run or
  transitions anywhere but `PLAYING`/`SAVE`/`MAP`-equivalent states (mirrors `T13.e`'s/`T14.e`'s
  own systematic negative-test-sweep shape, FR-10600).
- **T27.g (new, `BL-0119`) — in-session re-entry does not respawn a collected treasure, without
  any save/load boundary:** materialize a region with treasure present, collect it (assert
  `RUNNING_TREASURE_COUNT` increments, mirroring `T26.a`/`b` from `IP-1103`'s own suite), navigate
  away far enough that the region leaves the materialized window, then navigate back to it —
  assert `INF_TREASURE_HERE == 0` at the region's own re-materialization (not re-derived as
  present from the raw hash predicate) and that `RUNNING_TREASURE_COUNT` does not increment a
  second time on standing at the collection point again. Directly exercises `FS-110` §7's own
  edge case ("re-approaching a previously-visited, treasure-collected region… with the treasure
  reading as collected") for the in-session case specifically — `T27.a` (this same suite) already
  covers the save/load-boundary case; this check is what closes the gap between them.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-10500/FR-10600 status → Implemented;
  NFR-5400 status → Met (sized: 128 entries × 5 bytes = 640 bytes, against ~8 KiB SRAM budget;
  plus the 642-byte WRAM working copy against the ~3.1 KiB bank-0 headroom, `NFR-4300`).
- `docs/architecture/07-data-model.md` (GDS-07): new SRAM section recording
  `SRAM_GAME_MODE`/`SRAM_INF_ROW`/`SRAM_INF_COL`/`SRAM_RUNNING_TREASURE_COUNT`/
  `SRAM_TOP_SCORE_TABLE`/`SRAM_LEDGER_COUNT`/`SRAM_LEDGER_CURSOR`/`SRAM_LEDGER`'s addresses; **new
  §7g WRAM section** recording `LEDGER_COUNT`/`LEDGER_CURSOR`/`LEDGER`'s addresses
  (`0xC419`–`0xC69A`), the amendment's own mirror-layout rationale, and the boot-clear scope;
  `SAVE_VERSION_VAL`'s row updated to `0x05` (fifth bump since ship).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-10500/FR-10600/NFR-5400 rows →
  `IP-1104`/T27.
- `docs/features/FS-110-infinite-mode.md` metadata: implemented-by pointer for Workflow D in
  full; §19 Open Questions 5 and 7 marked Resolved (ledger capacity/FIFO eviction, save-format
  version value). **This closes the Infinite Mode tranche's own Files-to-Modify set** — Open
  Question 3 (`BL-0112`) remains the tranche's sole standing gap, per `IP-1103`'s own explicit
  scope boundary.
- Master Build Plan status row.

## 10. Definition of Done

- A full save/load round trip restores position, running count, top-3 table, and every ledger
  entry's collected-state exactly (T27.a).
- No SRAM byte represents a region's biome or connectivity (T27.b, direct audit).
- **A collected treasure does not respawn on ordinary in-session re-entry — leaving the
  materialized window and walking back within the same session, no save/load boundary crossed
  (T27.g, `BL-0119`).**
- FIFO eviction behaves correctly at capacity (T27.c).
- A pre-Infinite-Mode save is cleanly rejected, never partially loaded (T27.d).
- The finite mode's own save/load is provably unaffected (T27.e).
- No reachable input sequence forcibly ends a loaded Infinite Mode run (T27.f, FR-10600).
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T27.a–g each present and passing (note: g is this amendment's own addition).
- [ ] Direct code read: `save_to_sram`/`try_load_save` still use exactly one MBC1-enable bracket
      (no second bracket opened for the new fields).
- [ ] Direct code read: `SRAM_LEDGER`'s 5-byte entry format matches §6 exactly — no biome/
      connectivity field present anywhere in the ledger's own byte layout.
- [ ] Direct code read: `try_load_save`'s `GAME_MODE == 1` restore branch calls
      `IP-1102`'s `inf_ensure_window` before any gameplay frame renders — no window/render call
      is skipped on the load path the way it would be if only WRAM were restored.
- [ ] **Direct code read: `inf_ledger_mark_collected` and `inf_ensure_window`'s new ledger
      cross-reference both operate on the WRAM `LEDGER`/`LEDGER_COUNT`/`LEDGER_CURSOR` — never
      directly on `SRAM_LEDGER`/`SRAM_LEDGER_COUNT`/`SRAM_LEDGER_CURSOR` outside `save_to_sram`/
      `try_load_save`'s own MBC1-bracketed `memcpy` calls (`BL-0119`'s amendment: no per-collection
      SRAM access).**
- [ ] **Direct code read: `inf_ensure_window`'s ledger cross-reference runs on every call —
      new-game entry, ordinary `czt_infinite` navigation, and post-load re-materialization alike
      — not gated on any load-specific flag or state.**
- [ ] FR-10500/FR-10600/NFR-5400/GDS-07/RTM/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1100`** (**NOT YET `VERIFIED`**) — `GAME_MODE`'s own WRAM definition.
- **`IP-1101`** (**NOT YET `VERIFIED`**) — the position/region format this package's ledger
  entries encode.
- **`IP-1102`** (**NOT YET `VERIFIED`**) — `inf_ensure_window`, called on load to re-materialize
  the working set around the restored position.
- **`IP-1103`** (**NOT YET `VERIFIED`**) — `RUNNING_TREASURE_COUNT`/`TOP_SCORE_TABLE`'s own WRAM
  definitions, and the collection branch this package's `inf_ledger_mark_collected` is called
  from.
- **`IP-1050`/`FEAT-5300`** (`VERIFIED`) — the existing `save_to_sram`/`try_load_save`/`memcpy`
  extension pattern this package follows exactly.
- **`IP-9070`/`FEAT-5220`** (`VERIFIED`) — the most recent prior `SAVE_VERSION_VAL` precedent this
  package's own bump extends.

Last package in the tranche's critical path — depends on all four other Infinite Mode packages.

## 13. Risks

- **640-byte SRAM ledger is a substantial single addition** (Low, against an ~8 KiB budget with
  only ~193 bytes currently used) — re-affirmed at build time via a direct SRAM-map audit, not
  merely computed here.
- **This amendment adds a matching 642-byte WRAM working copy** (Low-Medium — the largest single
  WRAM addition in the tranche so far, against the confirmed ~3.1 KiB bank-0 headroom with only
  ~23 bytes consumed by `IP-1101`/`1102`/`1103` combined; comfortably fits, but re-affirmed at
  build time, not merely computed here) — this is a deliberate design correction, not scope
  creep: the original plan's SRAM-only ledger, read/written on every single collection event,
  would have needed an MBC1-enable/disable bracket around every pickup and would still have left
  `inf_ensure_window` — the routine that runs on *every* navigation step — with nothing cheap to
  consult, which is exactly how `BL-0119`'s gap went unnoticed at planning time. The WRAM copy
  is what makes a per-navigation-step ledger check actually affordable (no SRAM access outside
  the two explicit save/load `memcpy` calls), consistent with every other piece of collectible
  state this project tracks (`KEYITEM_FLAGS`/`SCOREITEM_FLAGS`/`CARROT_FLAGS` are all WRAM
  working copies with an SRAM backing store, never queried from SRAM live during play) — the
  original ledger plan was the one outlier, now corrected.
- **`try_load_save`'s `GAME_MODE`-gated restore branch is the single most save-format-invasive
  change in this tranche** (Medium) — extends, rather than replaces, the existing routine
  (mirrors `IP-1050`'s own precedent), but a version-guard defect here would affect every future
  save, both modes; T27.d/e's own explicit regression coverage is this package's primary
  mitigation.
- **`inf_ensure_window`'s new ledger cross-reference is an ADDED per-transition cost** (Low) —
  `IP-1102`'s own `NFR-1400` was already honestly measured `NOT MET` for the unrelated PRNG cost
  (`BL-0118`, a filed follow-up optimization); a bounded ≤128-entry linear scan added once per
  center-cell materialization is a small additive cost on top of that pre-existing, already-known
  budget miss — worth re-measuring alongside `BL-0118`'s own eventual optimization pass rather
  than treated as a fresh, separate finding here.
- **The ledger's FIFO eviction policy (Technical Work Breakdown's own choice) may prove
  player-hostile in extended play** (Low, named not hidden) — evicting the oldest visited region
  means a very long run could "forget" a treasure the player collected early, re-offering it as
  uncollected on re-approach; a future revision could switch to a different eviction rule, an
  observation for `09`/`10`, not resolved here.
- **`LEDGER_COUNT`'s own reset-on-new-game question is deliberately left open by this amendment**
  (Low, honest gap not silently patched around) — mirrors `IP-1103`'s own identical, already-
  accepted treatment of `RUNNING_TREASURE_COUNT` (§13 there); both are facets of the same
  `BL-0112` run/session-shape question, resolved together whenever that backlog item resolves,
  not piecemeal here.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. `SAVE_VERSION_VAL` reverts to `0x04` —
existing (finite-mode, version-4) saves remain loadable by the reverted-from build unchanged; any
Infinite Mode (version-5) save created before the revert becomes pre-upgrade and is cleanly
excluded from "continue," exactly as every prior version bump has behaved on revert.
