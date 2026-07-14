# ADS-001 — Streaming, Positionally-Deterministic World Generation for an Additive Infinite Mode

- **Dependencies:** [R114](../research/encyclopedia/R114-streaming-world-generation-feasibility.md)
  (hardware feasibility of streaming/local generation), [R216](../research/encyclopedia/R216-infinite-mode-win-condition-design.md)
  (win-condition/treasure-placement design for unbounded play), [R111](../research/encyclopedia/R111-wram-banking-sm83-prng.md)
  (xorshift PRNG, `SVBK` banking), [R112](../research/encyclopedia/R112-maze-generation-hardware-feasibility.md)
  (maze algorithm hardware-cost framing), [R113](../research/encyclopedia/R113-sm83-prng-degeneracy-mitigation.md)
  (`gw_prng_step` degeneracy — must not be reintroduced by any new per-region seeding scheme),
  [R215](../research/encyclopedia/R215-procgen-win-condition-design.md) (finite-world win-condition
  data, reused as the infinite-mode density-tuning anchor), [ADR-0009](adr/ADR-0009-screen-graph-world-generation.md),
  [ADR-0010](adr/ADR-0010-seed-scale-model.md), [ADR-0012](adr/ADR-0012-maze-shaped-region-adjacency.md),
  [ADR-0013](adr/ADR-0013-maze-pass-prng-decorrelation.md), [ADR-0015](adr/ADR-0015-dead-end-anchored-treasure-and-win-condition.md)
  (all decisions for the **finite** generation model, none amended by this synthesis — see §Decision Log)
- **Produces:** [ADR-0016](adr/ADR-0016-streaming-infinite-mode-generation-architecture.md) (the
  adoption decision), [ADR-0017](adr/ADR-0017-infinite-mode-treasure-placement-and-win-condition.md)
  (treasure/win-condition decision) — the target architecture a future `04-requirements-engineering`
  pass formalizes into `FR`/`NFR`s for a new epic, before any `06`→`07`→`08` implementation work,
  gated by G3 as always

## Executive Design Overview

`BL-0082` asked whether the shipped procedural-generation architecture could build the world
lazily — region by region, as the player approaches — with the goal of a theoretically unbounded
playable world, and connected two already-filed items to the answer: `BL-0066` (biome-blob
clustering) and `BL-0050`/`BL-0094` (win-condition/status-display redesign). Both research halves
are now complete: `R114` confirms streaming generation is representable on this hardware, but only
by replacing both of `generate_world`'s load-bearing global-sequential algorithms (the
raster-scan biome anchor-clamp chain, the backtracking-DFS maze carve) with genuinely
positionally-deterministic ones — not an incremental patch. `R216` resolves the one concrete design
conflict that finding surfaced (the cheapest streaming-compatible maze algorithm has a directional
dead-end bias that conflicts with `IP-1021`'s dead-end-priority win condition) by decoupling
treasure placement from maze structure entirely.

**Decision: adopt streaming generation, scoped as a new, additive "Infinite Mode" selectable at
new-game creation alongside the existing finite `(seed, scale)` model — not a replacement for it.**
The finite mode's shipped generation algorithm, win condition, and save format
(`ADR-0009`/`ADR-0010`/`ADR-0012`/`ADR-0013`/`ADR-0015`) are **entirely unaffected**: this is new
scope layered beside them, exactly as `ADR-0012` refined `ADR-0009` without reversing it. This
synthesis authorizes the *architecture target* only — no code ships from this pass; the normal
`04`→`05`→`06`→`07`→`08` pipeline still applies, gated by G3, before any Infinite Mode package is
implemented.

## System Architecture

**Two independent generation architectures coexist, selected once at new-game creation and fixed
for the life of that save** (mirroring `ADR-0010`'s existing seed/scale immutability convention):

- **Finite mode** (existing, unchanged): `(seed, scale)` → `generate_world`'s global
  raster-scan-biome + backtracking-DFS-maze pass, run once, in full, under an LCD-off bracket.
  `REGION_GRAPH` regenerates from `(seed, scale)` on every load (`ADR-0009` point 3).
- **Infinite mode** (new, this synthesis): `(seed)` alone — no `scale`, since there is no fixed
  extent. Each region's biome and maze-connectivity are **pure functions of `(seed, row, col)`**,
  computed the instant the player approaches that region (plausibly inside
  `check_zone_transition`'s existing call site), never requiring a global pass or a fixed grid
  size. A materialized "window" around the player (sized to stay inside bank-0's ~3 KiB headroom,
  `R114`) holds the only regions currently resident in WRAM; regions outside the window are
  discarded and re-derived identically on return, exactly as `R114`'s Minecraft-chunk analogy
  describes.

**Positional-determinism technique (both biome and maze, Infinite Mode only):** seed a fresh
`gw_prng_step`-family xorshift instance per region from `SEED` XOR/shift-mixed with `(row, col)` —
reusing the existing shift/XOR-only construction (`R111`/`R113`), never introducing a
multiplication-based hash (SM83 has no hardware `MUL`; `R114`'s own finding). The seeded instance
is discarded immediately after deriving that region's few needed values; no persistent per-region
PRNG state exists.

**Maze algorithm (Infinite Mode only): the Binary Tree algorithm**, the one maze family `R114`
confirms needs "no memory at all" — for every region, carve a passage either north or west,
decided by a single PRNG draw local to that region's own coordinates. Chosen over the Growing Tree
alternative because `ADR-0017` (below) removes the only reason Growing Tree's extra
revisit-consistency design cost (a canonical, coordinate-driven enumeration order, not yet
designed) would have been worth paying: decoupling treasure from maze structure makes Binary
Tree's directional dead-end bias irrelevant to the win condition. Binary Tree's **aesthetic**
quality (does its NW-corridor bias read as an acceptable "maze feel" once played) is **not**
decided here — flagged as an Open Question below, routed to `02-research-game-design`/
`09-content-review` once implemented.

**Save/load model (Infinite Mode only): a bounded visited-region ledger, not regenerate-from-scale.**
`ADR-0009` point 3's "regenerate from `(seed, scale)`" has no meaning without a fixed `scale`. Per
`R114`'s recommendation: persist the player's current position (an unbounded coordinate pair, not
`CUR_ZONE`'s 0–80 byte) and a bounded-by-SRAM-capacity ledger of which visited regions have had
their KeyItem collected — biome/maze state itself needs no persistence at all, since it
regenerates identically from `(seed, row, col)` on demand. Sizing the ledger's real capacity is new
SRAM-budget work, not sized here (Open Question below).

## Domain Model

New entities this synthesis names but does not yet formalize into `GDS-04` (deferred to
`04-requirements-engineering`, exactly as the original procgen-world increment's own `GDS-04` delta
followed its `ADR-0009` by a separate pass, not the same one):

- **InfiniteWorldSeed** — the sole new-game parameter for this mode (no `WorldScale` counterpart).
- **VisitedRegionLedger** — a bounded, SRAM-capacity-limited record of which positionally-addressed
  regions have been visited and whether their treasure (if any) has been collected. Replaces
  `REGION_GRAPH`'s whole-graph materialization for this mode.
- **RunningTreasureCount** / **TopScoreTable(3)** — the Infinite Mode win-condition state
  (`ADR-0017`), replacing `CARROTS_COUNT`/`WORLD_SCALE`-target semantics for this mode only.

## User Stories

- As a player who has explored the entire finite world, I can start a new Infinite Mode game and
  keep exploring without a fixed endpoint, chasing a high score instead of a completion count.
- As a returning player, walking away from a region and back reproduces the identical region
  (biome, connectivity, and — if not yet collected — its treasure), because both are pure functions
  of `(seed, row, col)`, not of my own path history.
- As a player checking my progress, I see a running treasure count and my top-3 all-time high
  scores, not a region-grid status screen (which has no meaning without a fixed world size).

## Functional Requirements (capability-level, formalized later as `FR-xxxx` by `04`)

1. New-game creation offers a Finite/Infinite mode choice; Infinite Mode takes only a seed.
2. Each region's biome and maze connectivity are computed on demand from `(seed, row, col)` and are
   revisit-consistent (identical result on every re-approach).
3. A region holds treasure iff `hash(SEED, row, col) mod K == 0` for a tuned density constant `K`
   (`ADR-0017`), independent of maze connectivity.
4. Collecting a region's treasure increments a running count; on run end (see Open Questions —
   run/session shape not yet decided), the running count is compared against a persisted top-3
   table and inserted if it qualifies. No name-entry UI.
5. Save/load persists player position and the visited-region ledger only; biome/maze regenerate
   deterministically and are never themselves persisted.

## Non-functional Requirements

- **WRAM:** the materialized window must fit bank-0's confirmed ~3.1 KiB headroom
  (3082 bytes as of this session, `R114`) without `SVBK` banking; banking (`R111`) is a fallback
  only if a chosen window radius concretely exceeds it, and is itself new toolchain work
  (`gbc_lib.py` has no `SVBK` emitter today).
- **ROM:** a per-region hash-seeded generation routine is structurally smaller than the whole-grid
  `generate_world` pass it runs alongside (not replaces) — not a binding constraint against the
  9784-byte headroom measured this session (`R114`).
- **Determinism:** identical `(seed, row, col)` must always produce identical biome/connectivity/
  treasure-presence output — the same discipline `ADR-0009` point 3 and `ADR-0012` point 6 already
  establish for the finite mode, extended here to per-region rather than whole-graph scope.
- **Timing:** a single region's materialization cost must fit inside whatever safe window
  `check_zone_transition` already has, without a new LCD-off bracket or player-visible stall — **not
  confirmed here**, flagged as an Open Question requiring direct cycle-counting at implementation
  time (`R114`).

## Constraints

- No hardware `MUL`/`DIV` (SM83) — every mixing step must remain shift/XOR-only, reusing
  `gw_prng_step`'s existing construction.
- `gbc_lib.py` has no `SVBK` emitter today — banked WRAM remains available in principle (R111) but
  is not a free capability.
- The finite mode's shipped algorithms, save format, and win condition
  (`ADR-0009`/`ADR-0010`/`ADR-0012`/`ADR-0013`/`ADR-0015`) are **not to be changed** by this or any
  Infinite Mode implementation work — this is additive scope, not a migration.

## Risks

- **Binary Tree's NW-corridor bias may read poorly once played**, even though it no longer biases
  treasure placement (decoupled, `ADR-0017`). A future `02-research-game-design`/`09-content-review`
  pass may recommend the harder Growing Tree family instead, which would require designing a
  canonical coordinate-driven enumeration order for revisit-consistency (not designed here).
- **Materialization timing is unconfirmed.** If a region's hash-reseed-and-clamp computation turns
  out not to fit `check_zone_transition`'s existing safe window, a new LCD-off-style bracket or a
  multi-frame materialization budget would be needed — a real, if likely small, implementation-time
  risk `R114` explicitly does not resolve.
- **Run/session shape is undecided** (see Open Questions) — building the win-condition state
  without first deciding this could require rework.

## Open Questions

1. **Run/session shape** (`R216`, surfaced not resolved): is an Infinite Mode playthrough
   indefinitely resumable (matching the finite game's save/continue convention), or its own bounded
   "run" needing a new end-condition mechanic (death/retreat/checkpoint) this game does not
   currently have? Routed to a future `04-requirements-engineering` pass — genuine new mechanic
   scope, not a generation-architecture question.
2. **Binary Tree maze aesthetic quality** — does the NW-corridor bias read as acceptable "maze
   feel" once actually played? Routed to `02-research-game-design` and/or `09-content-review` once
   an Infinite Mode package is implemented; Growing Tree (with its added revisit-consistency design
   cost) remains a named fallback if not.
3. **Visited-region ledger capacity** — how many distinct visited regions a save can remember before
   exhausting available SRAM. Routed to a future `02-research-gbc-hardware`/`07-implementation-
   planning` pass against `R106`'s existing SRAM/battery-save grounding; not sized here.
4. **Materialization cycle cost** — direct cycle-counting against `check_zone_transition`'s actual
   call context, per `R114`'s own flag. Routed to `07-implementation-planning`/`08-code-
   implementation` measurement at build time.
5. **Treasure density constant `K`** — an implementation-time tuning question (`R216` suggests
   anchoring near `R215`'s measured `scale=9` dead-end density, ~6.4%, as a starting point, not a
   binding number).

## Decision Log

- **2026-07-13 — Adopt streaming/positionally-deterministic generation as a new, additive Infinite
  Mode; finite mode entirely unaffected.** Recorded in [ADR-0016](adr/ADR-0016-streaming-infinite-mode-generation-architecture.md).
  User-authorized (`00-pipeline-manager` gate stop, this session) after both `02-research-*` halves
  (`R114`/`R216`) completed.
- **2026-07-13 — Binary Tree over Growing Tree for the maze algorithm**, made possible by decoupling
  treasure placement from maze structure (below) — trades a small, real aesthetic risk (Open
  Question 2) for zero-memory simplicity and no new revisit-consistency design burden.
- **2026-07-13 — Decouple treasure placement from maze structure via `hash(SEED,row,col) mod K`**,
  adopting `R216`'s proposed resolution to the dead-end-bias conflict as a genuine design
  substitution for `BL-0094`'s literal "at dead ends" wording — recorded, with the tradeoff named
  explicitly, in [ADR-0017](adr/ADR-0017-infinite-mode-treasure-placement-and-win-condition.md).
- **2026-07-13 — Adopt `BL-0094`'s score-chasing win condition (running count + top-3, no
  name-entry UI) unchanged** — `R216` confirms it is genre-correct, not merely convenient; no
  amendment needed.
- **2026-07-13 — `BL-0066` (biome-blob clustering) resolved for the Infinite Mode context**: adopt
  the per-super-cell `hash(SEED, supercell_row, supercell_col)` blob-identity mechanism `R114`
  names as the streaming-compatible substitute for both of `BL-0066`'s original candidates (neither
  of which survives a streaming model). **`BL-0066`'s original finite-mode question — the
  `ADR-0012` pass-ordering conflict between dead-end seeding and the shipped biome-first ordering —
  is not resolved by this decision** and remains open for the pipeline manager to re-triage: either
  revisit `ADR-0012`'s ordering for the finite mode independently, adopt the finite-mode's own
  flood-fill alternative, or (if the owner's intent has shifted, per their own framing connecting
  `BL-0066` to `BL-0082`) treat blob-clustering as an Infinite-Mode-only feature and close the
  finite-mode question as no-longer-pursued. This synthesis does not assume which.
- **2026-07-13 — `BL-0050` (MAP/status-screen redesign) unblocked for the finite mode
  independently of Infinite Mode's own status display.** The two modes coexist rather than one
  superseding the other, so `BL-0050`'s finite-mode screen redesign can proceed against `IP-1021`'s
  already-shipped finite win condition without waiting on Infinite Mode's own separate high-score
  display (which has no fixed region-grid to show progress against and would need its own screen
  content, out of `BL-0050`'s own scope).
- **2026-07-13 — `ADR-0009`/`ADR-0012`/`ADR-0013` are not amended, only cross-referenced.** None of
  their decisions govern anything but the finite mode; per this project's append-only ADR
  convention, forward-pointer notes are added to each rather than editing their Decision text (the
  same precedent `ADR-0009`'s own top-of-file note set for `ADR-0012`).
