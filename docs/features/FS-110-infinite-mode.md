# FS-110 — Infinite Mode

> Feature Specification for [FEAT-10000](../feature-planning/03-feature-catalog.md#feat-10000--infinite-mode-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-10000, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Planned 2026-07-14** (`07-implementation-planning`) — five packages,
> [IP-1100](../implementation/packages/IP-1100-infinite-mode-mode-selection.md)–[IP-1104](../implementation/packages/IP-1104-infinite-mode-ledger-save-persistence.md),
> **AUTHORIZED (G3, "Yes, build all five," 2026-07-14)**.
> [IP-1101](../implementation/packages/IP-1101-infinite-mode-region-materialization.md)
> **`VERIFIED` 2026-07-14** — Workflow B step 2/Workflow C step 1 (per-region materialization,
> treasure-presence) implemented and independently verified, `T22` (7 checks).
> [IP-1102](../implementation/packages/IP-1102-infinite-mode-streaming-window-and-render.md)
> **`VERIFIED` 2026-07-14** — Workflow B steps 1/3/4 (streaming materialized-window management,
> transition-triggered materialization, biome-dispatch/arrow-draw render integration)
> implemented and independently verified, `T24` (7 checks).
> [IP-1100](../implementation/packages/IP-1100-infinite-mode-mode-selection.md)
> **`VERIFIED` 2026-07-16** — Workflow A (`MODE SELECT`/`INFINITE SEED ENTRY`, `GDS-01` §4d)
> implemented and independently verified, `T25` (19 checks, 296/296 full suite at verification
> time).
> [IP-1103](../implementation/packages/IP-1103-infinite-mode-treasure-and-win-condition.md)
> **`VERIFIED` 2026-07-16** — **Workflow C steps 1–2 only** (treasure spawn/collection, running
> count, top-3 comparison subroutine), `T26` (16 checks); **step 3's
> automatic run-end trigger is explicitly NOT implemented** — `inf_check_top_score` exists with
> zero call sites (`T26.d` asserts exactly that), per this document's own §19 Open Question 3 /
> `BL-0112` routing.
> [IP-1104](../implementation/packages/IP-1104-infinite-mode-ledger-save-persistence.md)
> **`COMPLETE` 2026-07-16** — Workflow D in full (position + bounded-ledger save/load,
> `SAVE_VERSION_VAL` `0x04`→`0x05`), `T27` (7 checks, 309/309 full suite). Amended per `BL-0119`
> before implementation: a WRAM ledger working copy so `inf_ensure_window` consults
> collected-state on every materialization, closing a mid-session respawn gap uniformly. **This
> closes the Infinite Mode tranche's own five-package set — `BL-0112` (the run-end trigger for
> `FR-10400`'s top-3 comparison) is the tranche's sole standing gap.** See the
> [Technical Work Breakdown](../implementation/01-technical-work-breakdown.md#infinite-mode-fs-110feat-10000ep-6000-planned-2026-07-14)
> for the split rationale. This Feature sits in the `Future` release bucket (no release commitment
> made) — planning does not require or imply scheduling, per `05-feature-decomposition`'s own
> established precedent. Open Question 3 (`BL-0112`, run-end trigger timing) is deliberately left
> unresolved by this planning pass, exactly as this document's own §19 routes it.

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-110` — expands `FEAT-10000` (Infinite Mode), Epic `EP-6000` (Infinite Mode).

## 2. Title

Infinite Mode

## 3. Purpose

Offer a second, additive world-generation mode — seeded, streaming, positionally-deterministic,
with no fixed extent — alongside the existing finite `(seed, scale)` mode, replacing a completion
threshold with a persisted high score for non-terminating play. Carried forward verbatim from
FEAT-10000's own Purpose/User Value (Medium — a genuinely new mode with real replay value, per
R216's arcade-convention grounding, but exploratory and owner-initiated rather than tied to any
MSTR-001 commitment).

## 4. Scope

**In scope:** mode selection at new-game creation (seed only, no scale); streaming,
positionally-deterministic per-region biome/connectivity materialization; revisit-consistency;
treasure placement decoupled from maze structure via a tuned hash-density predicate; a running
treasure count compared against a persisted top-3 high-score table, with no name-entry UI; a
bounded visited-region ledger (player position + per-region collected state) as the save format;
an indefinitely-resumable run with no forced end-condition mechanic.

**Out of scope** (per FEAT-10000's own Excluded Requirements, carried forward verbatim): the
finite mode's own biome-blob clustering work (`CR-05`/`ADR-0018`/`BL-0066`) — a related but
independent thread that reuses this Feature's own super-cell-hash *technique* without depending
on this Feature's own code or save format; the finite mode's own generation, win condition, and
save format entirely (`FEAT-9000`/`FEAT-3000`/`FEAT-5300`), which `ADR-0016`/`ADR-0017` leave
completely unamended.

**Scope note carried from FEAT-10000's own catalog entry:** this Feature is deliberately kept as
one cohesive unit (mode selection, generation, treasure, win condition, save/load, session shape)
rather than pre-split by concern, since nothing has been implemented yet to reveal a clean seam —
mirroring how `FEAT-9000` itself started unsplit before `FEAT-4100`/`FEAT-5300`/`FEAT-9100` were
later carved out. This specification follows that same boundary; a future `05-feature-
decomposition` pass may split it once implementation detail is known (see Open Question 6).

## 5. Requirements Implemented

FR-10100, FR-10200, FR-10210, FR-10300, FR-10400, FR-10500, FR-10600; NFR-1400, NFR-2300,
NFR-4300, NFR-5400 — the exact set FEAT-10000 owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-10000--infinite-mode-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — New-game Infinite Mode entry** (FR-10100):

1. Player reaches new-game creation (the same entry point FEAT-1100's own finite-mode flow uses).
2. Player chooses Infinite Mode instead of Finite Mode.
3. Player enters a seed value only (the same 16-bit domain FR-1180/ADR-0010 already establish for
   the finite mode's own seed field) — no world-scale step is presented.
4. The chosen mode and seed are recorded for the new save; both are fixed for the life of that
   save (mirroring FR-9110's existing immutability guarantee for the finite mode).
5. Control passes to Workflow B for the player's starting region.

**Workflow B — Region materialization during play** (FR-10200, FR-10210):

1. The player's movement approaches a region not currently resident in the materialized window
   (the bounded set of regions held in WRAM around the player, §10).
2. The system computes that region's biome-id and connectivity as a pure function of
   `(SEED, row, col)` — a fresh per-region xorshift reseed (`SEED` XOR/shift-mixed with
   `(row, col)`, reusing `gw_prng_step`'s existing shift/XOR-only construction), discarded after
   deriving the region's values (ADR-0016 point 3).
3. The newly-materialized region is rendered using the existing biome-family screen-composition
   pipeline (see §9/Open Question 1 — the exact integration point is not yet decided).
4. As the player moves away, a region may leave the materialized window; if the player later
   re-approaches it, step 2 repeats and must reproduce byte-identical biome/connectivity output
   (FR-10210) — collected-treasure state persists via the ledger (Workflow D), never re-rolled.

**Workflow C — Treasure placement & collection** (FR-10300, FR-10400):

1. At the moment a region is materialized (Workflow B step 2), the system evaluates
   `hash(SEED, row, col) mod K` (a tuned density constant, not fixed by this Feature — Open
   Question 2) to decide whether that region holds treasure, independent of that region's own
   connectivity or dead-end status.
2. If the player collects that region's treasure (mirroring FR-3100's existing collection-
   proximity mechanic), the running treasure count for the current run increments by one and the
   ledger's own collected-state for that region is set (Workflow D).
3. **On run end** (see Open Question 3 — the exact trigger is not decided by this Feature), the
   running count is compared against the persisted top-3 high-score table; if it qualifies, it is
   inserted (displacing the previous lowest entry, if any). No name-entry prompt is ever shown
   (FR-10400).

**Workflow D — Save/load** (FR-10500, FR-10600):

1. On a save-confirm or exit-to-main-menu action (mirroring FR-1190's existing trigger), the
   system writes the player's current position (an unbounded coordinate pair, not a bounded zone
   index) and the visited-region ledger's collected-treasure entries to SRAM.
2. On load, position and ledger are restored directly; no region's biome or connectivity is ever
   read from or written to SRAM — every region is re-derived on demand (Workflow B) as the player
   re-encounters it.
3. Per FR-10600 (resolving `CR-07` by direct project-owner decision, 2026-07-13 — "for now assume
   indefinitely resumable"), no in-game action, timer, or hazard forcibly ends a run; "continue"
   from the MAIN MENU always resumes exactly where the player left off, mirroring the finite
   mode's own existing save/continue convention (FR-1170/FR-1190) exactly.

## 7. System Behaviour

**Normal path (materialization):** given any `(SEED, row, col)`, the region-materialization
routine terminates having produced a biome-id and connectivity value that are a pure function of
those three inputs alone — no dependency on generation order or any other region's own history
(NFR-2300).

**Edge case — seed = 0:** normalized to 1 internally before any per-region reseed, mirroring
ADR-0010's existing xorshift nonzero-state requirement for the finite mode's own seed.

**Edge case — the starting region:** unlike the finite mode's hardcoded `(0,0)` = Grass anchor
(a raster-scan-chain artifact this Feature's positional-hash construction has no equivalent
need for), Infinite Mode's spawn region is materialized identically to any other region — no
special-cased biome value. Stated as the expected behavior, not yet confirmed against any binding
artifact (Open Question 4).

**Edge case — re-approaching a previously-visited, treasure-collected region:** must reproduce
identical biome/connectivity to the first materialization (FR-10210), with the treasure reading
as collected, sourced from the ledger, not re-evaluated against the density predicate a second
time.

**Edge case — the visited-region ledger reaching its own capacity:** not yet defined — the
ledger's real SRAM-bounded capacity is unsized (NFR-5400, `BL-0108`), so what happens when a
player visits more distinct regions than it can hold (oldest-entry eviction, a hard cap on further
materialization, or another policy) is genuinely undecided. Flagged, not resolved (Open
Question 5).

**Edge case — a single region's materialization cost against the safe timing window:** whether
this introduces a player-visible stall is explicitly `UNCONFIRMED` (NFR-1400, `BL-0109`) — no
implementation exists yet to measure it. Named here as a real behavioral risk, not asserted safe.

## 8. Module Responsibilities

Per GDS-03's module decomposition, extended by ADR-0016 point 7's own module framing (no new
module):

- **`asm_game.py`** — the per-region materialization routine (per-region PRNG reseed, biome/
  connectivity derivation, treasure-density evaluation), mode dispatch (Infinite vs. Finite),
  the materialized-window management, and the visited-region-ledger save/load logic. None of this
  code exists yet.
- **`worldgen.py`** (prospective) — the Python reference-generator-oracle mirror for this
  Feature's own per-region routine, per ADR-0016 point 8's lockstep-PRNG discipline, the same
  obligation `FEAT-9000`'s own oracle already carries for the finite mode's whole-graph pass.
- **`tilemaps.py`/`tiles.py`** — the existing biome-family screen-composition functions
  (`FEAT-4100`'s own deliverable) this Feature's materialized regions must render through. **This
  Feature does not itself own or extend that rendering pipeline** — it supplies a biome-id per
  materialized region and expects the existing dispatch to consume it, exactly as the finite
  mode's own `REGION_GRAPH`-sourced biome-id already does. Whether this integration is actually
  possible without a `FEAT-4100`-owned change is not yet confirmed (Open Question 1).

No module outside this set is touched.

## 9. Interfaces Used

- **The existing biome-family screen-composition dispatch** (`FEAT-4100`'s own `ALL_SCREENS`/
  `dsr_p`-style pattern, GDS-09) — consumed, not redefined: this Feature's materialized-region
  biome-id must select the same representative screen the finite mode's own biome-id already
  selects. **Not yet confirmed to accept a biome-id from a source other than `REGION_GRAPH`
  lookup-by-index** — flagged as Open Question 1, not assumed.
- **`gw_prng_step`'s existing shift/XOR-only construction** (R111/R113, unchanged by this
  Feature) — reused for per-region reseeding, per ADR-0016 point 3. This Feature does not modify
  `gw_prng_step` itself, nor any of its existing finite-mode call sites.
- **The existing `check_collisions`/collection-detection interface** (FR-3100, unchanged) — this
  Feature's treasure-collection event reuses this interface's existing calling contract, exactly
  as `FEAT-9000`'s own `KeyItem` collection already does.
- **The existing MAIN MENU / new-game entry flow** (`FEAT-1100`'s own state machine, FR-1170/
  FR-1180) — this Feature's mode-selection step (Workflow A) extends this flow with a new choice
  point. **The exact UI shape this extension takes (a new menu step, or a repurposed SEED/SCALE
  ENTRY screen) has no `GDS-01` delta authored yet** — flagged as Open Question 6, mirroring
  `CR-06`'s own precedent for a missing architecture-level concept.
- **A new save-format version value** (mirroring `FEAT-5300`'s own `SAVE_VERSION_VAL` precedent)
  — this Feature's ledger-based save shape is structurally different from the finite mode's
  regenerate-from-scale format, so it needs its own version discriminator. Not yet named (Open
  Question 7).

## 10. Data Model Changes

**No `GDS-04`/`GDS-07`/`GDS-09` delta has been authored for Infinite Mode** (ADR-0016's own
explicit deferral) — unlike `FS-102`'s own precedent, this specification has no proposed WRAM/
SRAM address table to cite, only the conceptual entities `ADS-001`'s own Domain Model already
names:

- **`InfiniteWorldSeed`** — the sole new-game parameter for this mode (no `WorldScale`
  counterpart). Read at Workflow A, consumed by Workflow B.
- **Materialized-window working set** — biome-id, connectivity, and treasure-presence/collected
  state for each currently-resident region, bounded to fit bank-0's confirmed ~3 KiB headroom
  first (NFR-4300) before any `SVBK` banking is considered. Exact per-region byte cost and window
  radius are not decided here (Open Question 8).
- **`VisitedRegionLedger`** — a bounded, SRAM-capacity-limited record of which positionally-
  addressed regions have been visited and whether their treasure has been collected. Replaces
  `REGION_GRAPH`'s whole-graph materialization for this mode entirely — no region's biome or
  connectivity is ever persisted (NFR-5400).
- **`RunningTreasureCount`** / **`TopScoreTable(3)`** — the win-condition state (FR-10400),
  compatible with either run/session-shape answer per `ADR-0017` point 4, confirmed unaffected by
  `FR-10600`'s own resolution.
- **Player position** — an unbounded coordinate pair (not `CUR_ZONE`'s bounded 0–80 byte), exact
  representation (signed 16-bit per axis, or another shape) not decided here (Open Question 8).

**SRAM additions** are this Feature's own scope (unlike `FEAT-9000`, whose SRAM writes are
`FEAT-5300`'s scope) — Workflow D's ledger and position fields are written directly by this
Feature's own save/load routine, since no separate save-persistence Feature exists for Infinite
Mode in the current catalog.

## 11. State Changes

- **Whether Infinite Mode introduces any new `GameState` value is not decided by this Feature** —
  depends entirely on Open Question 6's own resolution (the mode-selection UI shape). If the
  chosen shape reuses existing states (e.g. a toggle within the existing SEED/SCALE ENTRY flow),
  no new state is needed; if it needs a dedicated screen, a new state is implied, mirroring
  `FEAT-1200`'s own `GS_SELECT_MENU`/`GS_LEGEND` precedent.
- **No new state is introduced for gameplay itself** — Infinite Mode's own PLAYING-equivalent
  behavior reuses the existing `PLAYING` state; this Feature changes what happens *within* that
  state (streaming materialization instead of a pre-generated `REGION_GRAPH` lookup), not the
  state machine's own node set for play itself.
- **Runtime state created:** the materialized window and ledger working sets (§10), persisting
  for the life of the play session and, via Workflow D, across save/reload.

## 12. Error Handling

- **Invalid seed input:** out of this Feature's own scope — the same entry-UI validation
  discipline FR-1180/FEAT-1100 already establish for the finite mode's own seed field applies
  identically here (Workflow A step 3), per FR-10100's own Dependencies.
- **A materialized region's treasure-density/biome computation producing an invalid value:** not
  a runtime failure mode this Feature handles defensively — NFR-2300's positional-determinism
  guarantee is enforced by construction (the reseed-and-clamp computation), not checked and
  recovered from after the fact, mirroring `FEAT-9000`'s own identical framing for its generator-
  guaranteed properties.
- **Visited-region-ledger capacity exceeded:** genuinely undefined (§7 edge case, Open
  Question 5) — this Feature's Error Handling cannot state a contract here until that question
  resolves.
- **A pre-Infinite-Mode-format save loaded after this Feature ships:** mirrors `FEAT-5300`'s own
  version-guard precedent (a version-mismatched save is not offered on "continue") — the exact
  version value is Open Question 7, not fixed here.

## 13. Performance Considerations

- **NFR-1400** (region-materialization timing, `UNCONFIRMED`): whether a single region's
  materialization fits inside `check_zone_transition`'s existing safe timing window, without a
  new LCD-off-style bracket or a player-visible stall, is not confirmed by any evidence this
  specification can cite — R114 judges it likely affordable but explicitly declines to treat it
  as settled without direct cycle-counting against the real call context. This Feature's own
  Acceptance Criteria (§15) states the bar; it does not claim compliance.
- **NFR-4300** (materialized-window WRAM headroom, `NOT YET SIZED`): the window must fit bank-0's
  confirmed ~3082-byte headroom without `SVBK` banking, for a window radius sized deliberately
  (not a fixed constant blindly reused from a large-extent assumption) — see Open Question 8.
- **ROM budget:** per ADR-0016's own Consequences, a per-region hash-seeded routine is
  structurally smaller than `generate_world`'s existing whole-grid pass — not expected to be a
  meaningful pressure on NFR-4000's 32768-byte budget, though not measured here.

## 14. Integrity Considerations

- **NFR-2300** (positional determinism): the per-region materialization routine's output must be
  a pure function of `(SEED, row, col)` alone — no read of `DIV`, uninitialized WRAM, generation
  order, or any other history-dependent input, mirroring NFR-2200's identical framing for the
  finite mode's own whole-graph determinism.
- **NFR-5400** (ledger round-trip integrity): the visited-region ledger must restore exactly on
  load; its maximum entry count must be a documented, fixed constant against real SRAM headroom
  (R106), never an assumption of unbounded capacity — not yet sized (Open Question 5/8).
- **The SM83 routine and its `worldgen.py` oracle mirror must be kept in lockstep by direct
  correspondence** (same reseed construction, same snap/fallback-equivalent branch conditions,
  mirroring `ADR-0018`'s own identical discipline for the finite mode's blob-bias branch) — named
  here as a standing implementation obligation, not itself enforced by this specification.

## 15. Acceptance Criteria

1. Selecting Infinite Mode at new-game creation presents a seed-entry step only (no scale step);
   the resulting save's mode is recorded and does not change without starting a new game
   (FR-10100).
2. For a corpus of `(SEED, row, col)` triples, materializing the same region twice — in the same
   session, or after it has left and re-entered the materialized window — produces byte-identical
   biome/connectivity output both times (FR-10200, FR-10210).
3. For a corpus of `(SEED, row, col)` triples, treasure-presence matches the
   `hash(SEED, row, col) mod K == 0` predicate exactly, regardless of that region's own maze
   connectivity (FR-10300).
4. A run's final treasure count that exceeds the lowest of the current top-3 is inserted,
   displacing the previous lowest; a count that does not exceed any current entry leaves the
   table unchanged; no name-entry prompt is reachable at any point (FR-10400).
5. Saving then loading an Infinite Mode game restores the exact player position and treasure-
   collected state for every previously-visited region in the ledger; no SRAM field represents
   biome or connectivity for any region (FR-10500).
6. No reachable input sequence forcibly ends an Infinite Mode run; "continue" always resumes
   exactly where the player left off (FR-10600).
7. Static inspection of the per-region reseed routine finds no read of `DIV` or any WRAM address
   not explicitly derived from `SEED`/`(row, col)` (NFR-2300).
8. **Not yet a checkable criterion** — NFR-1400's materialization-timing bar and NFR-4300/
   NFR-5400's sizing questions have no fixed numeric target to check against until Open
   Questions 5/8 resolve; this specification names the bar (§13/§14) without asserting compliance.

## 16. Verification Plan

Per FR-10100/10200/10210/10300/10400/10500/10600's own Verification Methods (Test) and
NFR-2300 (Inspection + Test) / NFR-1400 (Analysis) / NFR-4300/5400 (Inspection, once sized) — no
`test_rom.py` suite exists yet for this Feature (no code exists to test):

- **Mode entry (AC-1):** drive the new-game flow once Open Question 6 resolves a concrete UI
  shape; confirm no scale-entry step appears for Infinite Mode.
- **Positional determinism / revisit-consistency (AC-2):** property test across a
  `(SEED, row, col)` corpus, mirroring FR-9100's own determinism-test shape (fresh-instance
  comparison plus oracle-vs-SM83 comparison), extended to per-region rather than whole-graph
  scope — the same technique `FS-102`'s own T12 suite already establishes.
- **Treasure placement (AC-3):** property test against the hash predicate, mirroring FR-9160's
  own placement-verification shape (`FS-102`'s T12.e-equivalent).
- **Win condition (AC-4):** drive a corpus of run outcomes against a seeded top-3 table; confirm
  correct insertion/non-insertion; confirm no name-entry state is reachable — blocked on Open
  Question 3 (the run-end trigger) resolving first, since the test needs a concrete trigger to
  drive.
- **Save/load (AC-5):** two-instance save/reload harness, mirroring FEAT-5300's own T15 pattern,
  extended to the ledger's own bounded-capacity shape once Open Question 5/8 size it.
- **Indefinite resumability (AC-6):** negative test — attempt every reachable input sequence from
  the equivalent of PLAYING, confirm none forcibly ends a run, mirroring FR-9110's own
  negative-test shape.
- **Determinism static audit (AC-7):** Inspection — direct code read of the per-region reseed
  routine, mirroring NFR-2200's own T12.h precedent.
- **Timing/sizing (AC-8):** Analysis — direct cycle-counting against `check_zone_transition`'s
  real call context (NFR-1400); WRAM/SRAM layout audit against the built ROM (NFR-4300/5400) —
  neither possible until an implementation exists to measure.

**Corpus:** not yet defined — depends on the materialized-window radius (Open Question 8) and the
density constant `K` (Open Question 2), neither fixed by this specification.

## 17. Dependencies

Per FEAT-10000's own Dependencies (carried forward verbatim): FEAT-1000 (game-state machine);
FEAT-1100 (Main Menu & New-Game Flow — FR-10100's mode choice extends this Feature's own
new-game entry point); FEAT-3000 (Collectibles, Scoring & Victory — the running-count/high-score
mechanic generalizes this Feature's own collection/score concepts); FEAT-5000 (Save/Load System
— FR-10600's indefinitely-resumable run restates this Feature's own save/continue convention);
FEAT-9000 (Procedural World Generation — shares the underlying `gw_prng_step` construction, a
code-reuse dependency, not a structural one).

**Possible missing dependency, not decided here (Open Question 1):** this specification's own
§8/§9 found that rendering a materialized region requires `FEAT-4100`'s existing biome-family
screen-composition pipeline, but `FEAT-4100` does not appear in `FEAT-10000`'s own catalog
Dependencies list. This is a genuine finding for `05-feature-decomposition` to reconcile (the
same class of gap `FS-102`'s own Open Question 4 surfaced for a stale requirement citation), not
resolved unilaterally here.

## 18. Risks

Carried forward from FEAT-10000's own Risk assessment (Medium-High): shares `FEAT-9000`'s
original risk profile (a wholly new generation algorithm with no shipped precedent) plus two
explicitly-named open technical questions this Feature's own NFRs surface honestly rather than
assume away — whether a single region's materialization fits inside the existing safe timing
window (NFR-1400, unmeasured), and how large the materialized-window/visited-region-ledger can be
sized against real WRAM/SRAM budget (NFR-4300/NFR-5400, unsized).

**Additional risk surfaced by this specification, not named at the Feature-catalog level:** the
number of genuinely open architecture/requirements-level questions this spec had to raise (8, see
§19) is unusually high for a single Feature Specification — a signal that this Feature may be
under-decided for its current position in the pipeline, not a defect in this specification's own
rigor. Whether to route several of these upstream before `07-implementation-planning` attempts a
package, versus letting `07` resolve them as implementation-level choices (the precedent `FS-102`
itself followed for its own Open Questions 1–3), is a judgment call for whoever picks this
Feature up next — named here, not decided.

## 19. Open Questions

1. **Resolved (`IP-1102`, 2026-07-14).** Rendering integration was possible without any
   `FEAT-4100`-owned change: `dsr_p`'s biome-dispatch half (the `dsr_p_water`/`sand`/`grass`/
   `stone`/`brick` chain) is reused verbatim, reached via a new `GAME_MODE`-gated prefix that
   sources the biome-id from `INF_WINDOW`'s center cell instead of a `REGION_GRAPH` lookup —
   `dsr_p`'s existing `REGION_GRAPH` half is unmodified (`T24.c1`, direct static diff). A new
   `draw_region_arrows_inf` routine (not a `FEAT-2100` modification) replaces
   `draw_region_arrows` for the infinite-mode path, reading connectivity from `INF_WINDOW`
   directly. No missing dependency after all — `FEAT-4100`'s catalog entry needed no change.
2. **Resolved (`IP-1101`, 2026-07-14 — marking landed here per `BL-0116`, one `08-code-
   implementation` cycle late).** `K=16` (~6.25% density), implemented in
   `inf_materialize_region`'s own treasure-presence draw and confirmed by `T22.d`'s statistical
   check (measured 6.25% over an 800-region corpus, within the 2%-11% band).
3. **The run-end trigger for the top-3 comparison (Workflow C step 3) is not decided.** `FR-10600`
   resolved *whether* a forced end-condition mechanic exists (no) but not *when* the running
   count is compared against the top-3 table, given that a run is now indefinitely resumable
   across sessions. A reasoned candidate this specification surfaces but does not assert as
   decided: starting a new Infinite Mode game necessarily abandons whatever run preceded it
   (single save-slot precedent, `ADR-0006`) — that moment could be the natural "run end" trigger,
   comparing the abandoned run's final count before it is overwritten. This is a genuine design
   choice, not obviously implied by any binding artifact. Resolves at: `04-requirements-
   engineering` (a delta to `FR-10400`'s own Preconditions) or a direct user decision, mirroring
   `CR-07`'s own resolution path. **Still open after `IP-1103` (2026-07-16, deliberately):**
   that package built Workflow C steps 1–2 in full plus the comparison *subroutine*
   (`inf_check_top_score`, corpus-verified, `T26.c`) but wired **no automatic call site** —
   `T26.d` asserts the zero-call-site state explicitly, so the future package resolving this
   question lands the trigger as a clean, detectable diff (see `IP-1103` §2/§7's own stated
   boundary and `BL-0112`).
4. **Resolved (`IP-1101`, 2026-07-14 — marking landed here per `BL-0116`, one `08-code-
   implementation` cycle late).** No special case: `inf_materialize_region` treats every region,
   including `(0,0)`, identically — a Grass-at-spawn special case would have required an explicit
   branch that was never added, and `T22.b`'s own oracle-parity corpus includes `(0,0)`
   specifically to confirm this by direct implementation, not merely by absence of a branch.
5. **Resolved (`IP-1104`, 2026-07-16).** 128 entries × 5 bytes = 640 bytes SRAM (`NFR-5400`,
   `BL-0108`), sized against the confirmed ~8 KiB SRAM budget (`R106`). When exceeded: FIFO
   eviction (the Technical Work Breakdown's own resolution, a deliberate, revisitable choice, not
   asserted as the only correct one) — the oldest-visited entry is overwritten (`T27.c`).
6. **Resolved (`GDS-01` §4d, `IP-1100`, 2026-07-14).** A new `MODE SELECT` cursor menu (reusing
   `MAIN MENU`'s own convention) forks "new game" into the Finite mode's unchanged `SEED/SCALE
   ENTRY` flow or a new seed-only `INFINITE SEED ENTRY` state — two new `GameState` values
   (`GS_MODE_SELECT=10`, `GS_INFINITE_SEED_ENTRY=11`), shipped exactly per the diagram, `T25`.
7. **Resolved (`IP-1104`, 2026-07-16).** `SAVE_VERSION_VAL` bumped `0x04`→`0x05`, extending
   `IP-9110`'s own strictly-monotonic sequence (the fifth bump since ship) — mirrors `FEAT-5300`'s
   own precedent exactly, never a reused value.
8. **Resolved (`IP-1102`, 2026-07-14).** The materialized window is a 3×3 radius, 1 byte/region
   (`INF_WINDOW`, 9 bytes) plus a 4-byte center-anchor (`INF_ROW`/`INF_COL`) — 13 bytes, 15
   counting `GAME_MODE`/`INF_TREASURE_HERE` — comfortably inside bank-0's confirmed ~3.1 KiB
   headroom, no `SVBK` banking needed (`NFR-4300`, Met; `GDS-07` §7e). `IP-1101`'s single-region
   materialization routine is called once per resident cell, all 9 recomputed fresh on every
   center change (no incremental shift logic) — the actual per-transition cost this design
   choice produces is now measured, `NFR-1400`/`T24.e`.

## 20. Related ADRs

ADR-0016 (streaming, positionally-deterministic generation architecture for Infinite Mode),
ADR-0017 (treasure placement decoupled from maze structure; score-chasing win condition).
