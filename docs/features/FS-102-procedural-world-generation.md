# FS-102 — Procedural World Generation & Item-Agnostic Collection

> Feature Specification for [FEAT-9000](../feature-planning/03-feature-catalog.md#feat-9000--procedural-world-generation--item-agnostic-collection-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-9000, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Forward reference (metadata only):** planned by
> [IP-1020](../implementation/packages/IP-1020-procedural-world-generation.md) (2026-07-10),
> which resolves this document's Open Questions 1–3. **Implemented 2026-07-10** — all eight
> Acceptance Criteria (§15) demonstrably pass via `test_rom.py`'s T12 suite (133/133 total,
> full suite green); independent verification pending `09-package-verification`.

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-102` — expands `FEAT-9000` (Procedural World Generation & Item-Agnostic Collection),
Epic `EP-5000` (World Generation & Visual Narrative).

## 2. Title

Procedural World Generation & Item-Agnostic Collection

## 3. Purpose

Deterministically generate a grammar-valid, fully-reachable region graph from `(seed, scale)`,
with exactly one collectible `KeyItem` per region, collected via an item-agnostic mechanism
generalizing the shipped Carrot rule. Carried forward verbatim from FEAT-9000's own Purpose/User
Value (High — this is the increment's central new capability).

## 4. Scope

**In scope:** the on-console (SM83) generation algorithm producing a region graph (biome
assignment + adjacency edges) for `WorldScale²` regions from `(Seed, WorldScale)`; the three
generator-guaranteed structural invariants (determinism, full reachability, grammar-valid
adjacency); the item-agnostic collection-mechanic generalization (`KeyItem`/`KeyItemFlags`/
`KeyItemCount` replacing `Carrot`/`CarrotFlags`/`CarrotCount`); the WRAM working-set and headroom
this generation requires; the build-side Python reference-generator oracle (`worldgen.py`) that
mirrors the SM83 algorithm for test purposes only.

**Out of scope** (per FEAT-9000's own Excluded Requirements, carried forward verbatim): the
seed/scale entry UI and the generation *trigger* — [FEAT-1100](../feature-planning/03-feature-catalog.md#feat-1100--main-menu--new-game-flow-new--not-yet-implemented)
owns *how* a player starts generation, this Feature owns what the generator does once invoked;
the generated-region *screen's rendering* — [FEAT-4100](../feature-planning/03-feature-catalog.md#feat-4100--generated-region-screen-composition-new--not-yet-implemented)
owns *how* a biome's tiles are drawn, this Feature owns only *which* biome a region gets;
persisting the generated world's parameters to SRAM —
[FEAT-5300](../feature-planning/03-feature-catalog.md#feat-5300--generated-world-save-persistence-new--not-yet-implemented)
owns save/load, this Feature owns only the in-memory generation routine and the collection
mechanic's runtime behavior.

## 5. Requirements Implemented

FR-9100, FR-9110, FR-9120, FR-9130, FR-4310, FR-3220; NFR-2200, NFR-4200 — the exact set FEAT-9000
owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-9000--procedural-world-generation--item-agnostic-collection-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — New-game world generation** (triggered by FEAT-1100's FR-1180, consumed here):

1. Player has confirmed a `(seed, scale)` pair via FEAT-1100's entry screen.
2. The generation routine (this Feature) receives `(seed, scale)` and executes to completion
   before the first `PLAYING` frame (ADR-0009 §"Decision" point 3).
3. The routine initializes a xorshift-family PRNG from `seed` (0 normalized to 1, per ADR-0010).
4. The routine constructs `scale × scale` regions: for each region, assigns a biome identity and
   proposes adjacency edges, accepting only grammar-legal edges (FR-4310) — a constrained-random
   graph walk, never a post-hoc-validated one (ADR-0009 §"Decision" point 2).
5. The routine places exactly one `KeyItem` in each region (FR-9130).
6. The routine confirms (by construction, not a separate check pass) every region is reachable
   from the starting region (FR-9120).
7. Control returns to FEAT-1100's flow, which transitions to `INTRO`.

**Workflow B — KeyItem collection during play** (extends the existing collection-proximity
detection, FR-3100, unchanged):

1. Player moves onto/adjacent to an active `KeyItem` in the current region.
2. FR-3100's existing detection fires (unchanged — this Feature does not modify detection logic).
3. On a `KeyItem` hit: the current region's `KeyItemFlags` bit is set, `KeyItemCount` increments
   by exactly one, and the `KeyItem` is removed from further play (no longer rendered or
   collectible) — mirroring `CARROT_FLAGS`'/`CARROTS_COUNT`'s existing push/pop-HL discipline
   exactly (per `IP-1010`'s established pattern for this class of per-region flag update).
4. Victory triggers per FR-3300's existing condition, generalized from "9 carrots" to
   "`KeyItemCount` equals the generated world's region count" (`WorldScale²`) — this Feature
   supplies the generalized count; FR-3300/FEAT-1000's own victory-trigger logic is unchanged.

## 7. System Behaviour

**Normal path (generation):** given any valid `(seed, scale)` where `seed` is 0–65535 and `scale`
is 2–9, the routine terminates having produced a complete region graph satisfying all three
invariants (determinism, reachability, grammar-validity) and exactly one `KeyItem` per region.

**Edge case — seed = 0:** normalized to 1 internally before PRNG initialization (ADR-0010,
xorshift's nonzero-state requirement) — the player-visible seed value entered is 0, but the
generator's actual internal state never is.

**Edge case — scale = 2 (minimum):** 4 regions total; the grammar-adjacency + reachability
invariants must both still hold at this floor — a 4-region graph is the smallest case any
generator-property test corpus must include (per R305's extension), since a degenerate
single-node graph (scale 1) is excluded by ADR-0010's own range decision, not this Feature's
concern.

**Edge case — scale = 9 (maximum):** 81 regions; this is NFR-4200's stress case for WRAM/SRAM
headroom (see §13).

**Edge case — KeyItem collection at region boundary:** identical to the existing Carrot-collection
edge cases (FR-3210's shipped behavior) since FR-3220 is behaviorally identical to FR-3210,
generalized only in identity — no new edge case beyond what FR-3210 already handles.

**Edge case — re-generating with the same (seed, scale) in a separate new-game creation:** must
produce byte-identical region-graph output to the first generation (FR-9100's own Acceptance
Criteria) — this is exercised by the Python reference-generator oracle comparison and by the
two-boot determinism test (§16).

## 8. Module Responsibilities

Per GDS-03's module decomposition and GDS-09's delta:

- **`asm_game.py`** — the actual SM83 generation routine (PRNG step, grammar-constrained edge
  selection, biome assignment); the `KeyItem` collection-mechanic generalization (extending
  `check_collisions` and the zone/region-entry check, mirroring `IP-1010`'s exact pattern for
  `SCOREITEM_FLAGS` but generalizing `CARROT_FLAGS`'s own existing bit-set logic instead).
- **New `worldgen.py`** (build-side, proposed per GDS-09's delta) — the Python reference-generator
  oracle, `generate(seed: int, scale: int) -> RegionGraph`. **Consumed only by `test_rom.py`**,
  never imported by `build_rom.py`/`asm_game.py` (GDS-09's delta, explicit).
- **`tilemaps.py`** — supplies the biome-family screen-rendering functions this Feature's
  generated biome assignments select from (owned by FEAT-4100, consumed here as a fixed
  interface — this Feature does not define what a biome-family screen looks like).

No module outside this set is touched; `gbc_lib.py`, `build_tile_data()`'s buffer contract, and
`music.py` are unaffected (GDS-09's delta, explicit).

## 9. Interfaces Used

- **`worldgen.py`'s proposed contract** (GDS-09 delta): `generate(seed: int, scale: int) ->
  RegionGraph`, where `RegionGraph` exposes `regions: list[{biome_id, neighbors}]` and a
  `key_item_region_index`-style field matching GDS-07's proposed `REGION_GRAPH` layout
  field-for-field. **This interface does not exist yet** — it is this Feature's own deliverable,
  named here as a needed contract per GDS-09's own delta, not an Open Question.
- **`build_game_asm(rom: ROM) -> dict`'s existing patch-point mechanism** (GDS-09 §"new
  patch-point keys" delta) — this Feature's generator-data pointers (if any are needed beyond
  pure WRAM working-set, e.g. a grammar-table ROM pointer) ride the existing `patches` dict
  mechanism, no new resolution machinery.
- **`ALL_SCREENS`'s existing per-`(name, fn)` contract** (GDS-09 delta) — consumed, not
  redefined, by this Feature: the generation routine's biome assignment selects *which*
  biome-family `fn()` a region uses; the contract shape itself belongs to FEAT-4100.
- **The existing `check_collisions`/collection-detection interface** (FR-3100, unchanged) — this
  Feature extends its `KeyItem`-branch behavior, does not alter its calling contract.

## 10. Data Model Changes

Per GDS-04's delta (entities) and GDS-07's delta (proposed addresses — subject to confirmation
at implementation, per the FS-101/IP-1010 confidence precedent this document follows exactly):

- **New entities** (GDS-04 delta): `Seed`, `WorldScale`, `Region` (replaces `Zone`), `KeyItem`
  (replaces `Carrot`). This Feature owns `Region`'s generated biome-identity/adjacency-edge data
  and `KeyItem`'s collection state; `Seed`/`WorldScale` themselves are read here (supplied by
  FEAT-1100) and persisted by FEAT-5300 — this Feature only consumes them as generation inputs.
- **New WRAM (proposed):** `SEED` (`0xC069`–`C06A`, 16-bit), `WORLD_SCALE` (`0xC06B`, 1 byte),
  `REGION_GRAPH` (`0xC070`+, 5 bytes/region × up to 81 regions = ≤405 bytes worst case: 1
  biome-id byte + 4 neighbor-region-index bytes per region, `0xFF` = no neighbor in that
  direction), `KEYITEM_FLAGS` (next 8-aligned address after `REGION_GRAPH`, up to 81 bytes,
  generalizing `CARROT_FLAGS`). Worst-case total: ~489 bytes, inside the confirmed ~3.1 KiB
  bank-0 headroom (R111) — no `SVBK` banking triggered.
- **Renamed running total:** `KeyItemCount` generalizes `CarrotCount` (same WRAM slot,
  behaviorally identical increment logic, per FR-3220/GDS-04's delta).
- **SRAM additions** are FEAT-5300's scope, not this Feature's — this Feature's outputs
  (`SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS`) are *read by* FEAT-5300's save/load routine, not written
  to SRAM by this Feature directly.

## 11. State Changes

- The generation routine executes once, synchronously, between FEAT-1100's new-game confirmation
  and the `INTRO` state transition (GDS-01 §4a's target-state game-flow, consumed here — this
  Feature does not itself define the state machine, only runs during one of its transitions).
- No new `GameState` value is introduced by this Feature (MAIN MENU/SEED-SCALE-ENTRY are
  FEAT-1100's states).
- Runtime state created: the in-memory `REGION_GRAPH`/`KEYITEM_FLAGS` working set (§10), which
  persists for the remainder of the play session (and across save/reload via FEAT-5300's
  regenerate-from-seed approach, not direct persistence of this Feature's own working set).

## 12. Error Handling

- **Invalid `(seed, scale)` inputs:** out of this Feature's scope — FEAT-1100's entry UI is
  responsible for constraining player input to the valid ranges (seed 0–65535, scale 2–9) before
  this Feature's routine ever receives them; this Feature's Acceptance Criteria assume valid
  input, per FR-9100/FR-1180's own division of responsibility.
- **Generation producing an incomplete/invalid graph:** not a runtime failure mode this Feature
  handles defensively — FR-9120/FR-4310/FR-9130 are generator-*guaranteed* properties (enforced
  by construction, ADR-0009), not conditions checked and recovered from after the fact. If the
  construction logic itself has a defect, that is a correctness bug in the routine, caught by the
  property-test corpus (§16), not a runtime error path this Feature's behavior contract needs to
  define.
- **`KeyItem` collection on an already-collected item:** cannot occur under FR-3100's existing
  proximity-detection precondition (the item is removed from play on first collection, mirroring
  `CARROT_FLAGS`'s existing guarantee) — no new error path beyond what FR-3210 already handles.

## 13. Performance Considerations

- **NFR-4200** (generated-world WRAM/SRAM headroom): at `scale=9` (81 regions), this Feature's
  WRAM working set (~489 bytes worst case, §10) fits within bank-0's confirmed ~3.1 KiB headroom
  (R111) without `SVBK` banking — the figure this NFR's Acceptance Criteria requires confirming
  at implementation against the actual built ROM, not merely the architecture-level estimate.
- **Generation timing:** ADR-0009 places generation under the same LCD-off bracket
  `do_screen_redraw` already uses for full-screen work (R102's extension) — this Feature's
  routine must not run during an active VBlank-gated write window; it runs once, at new-game
  creation, with the LCD already off (consistent with NFR-1300's framing that generation itself
  is explicitly out of scope for the in-session transition-smoothness bar, since it happens once,
  not per-transition).
- **ROM budget:** per ADR-0009's Consequences, this Feature's code-only generation routine is
  expected to be a net ROM *saving* relative to the nine hand-authored screen tilemaps it
  replaces — not a new pressure on NFR-4000's 32768-byte budget, though the exact delta is an
  implementation-time measurement, not asserted here.

## 14. Integrity Considerations

- **NFR-2200** (deterministic generation): the routine's output must be a pure function of
  `(seed, scale)` alone — no read of `DIV`, uninitialized WRAM, or any other non-reproducible
  value anywhere in the generation algorithm (static-inspection Acceptance Criteria, per NFR-2200
  verbatim). This is the property that makes the `worldgen.py` reference-generator oracle valid
  at all (R305's extension, explicit) — an oracle can only predict SM83 output for a
  deterministic routine by design, not by accident.
- **The SM83 routine and the `worldgen.py` oracle must be kept in lockstep by direct
  correspondence** (same PRNG step order, same grammar-check order) — not shared code (GDS-09's
  delta, explicit). This is a standing implementation discipline this Feature's spec names but
  does not itself enforce mechanically; `07-implementation-planning`/`08-code-implementation`
  must maintain the correspondence, and `09-package-verification` must confirm it holds (via the
  oracle-vs-SM83 comparison test, §16).

## 15. Acceptance Criteria

1. For any `(seed, scale)` with `seed` in 0–65535 and `scale` in 2–9, generation produces exactly
   `scale²` regions (FR-9100).
2. Generating twice from the same `(seed, scale)` — in two separate new-game creations, or via
   the `worldgen.py` oracle vs. the SM83 routine — produces byte-identical region-graph output
   both times (FR-9100).
3. For any `(seed, scale)` in a test corpus, a graph-traversal from the starting region visits
   every generated region (FR-9120).
4. For any generated world, every adjacent region pair's biome-family combination appears in the
   grammar table; no illegal pairing exists anywhere in the graph (FR-4310).
5. For any `(seed, scale)` in a test corpus, counting `KeyItem`s per region yields exactly 1 for
   every region, with no region holding 0 or ≥2 (FR-9130).
6. Collecting a region's `KeyItem` sets that region's `KeyItemFlags` bit and increases
   `KeyItemCount` by exactly one, once (FR-3220).
7. Static inspection of the generation routine finds no read of `DIV` or any WRAM address not
   explicitly initialized from `(seed, scale)` or the routine's own prior output (NFR-2200).
8. At world scale 9, the built ROM's WRAM working set for `REGION_GRAPH` + `KEYITEM_FLAGS` fits
   within bank-0 (`0xC000`–`0xCFFF`) without requiring `SVBK` banking (NFR-4200).

## 16. Verification Plan

Per FR-9100/9110/9120/9130/4310's own Verification Methods (Test, property-test-across-a-corpus)
and NFR-2200/4200 (Inspection + Test), landing in a new **T12: World Generation** suite in
`test_rom.py` (the next unused suite number, after T11):

- **Determinism (AC-2):** boot twice with the same `(seed, scale)` — a fresh `PyBoy` instance
  each time, following the existing save/reload two-instance harness pattern (R305's extension)
  — assert byte-identical resulting WRAM state both times; separately, compare the `worldgen.py`
  oracle's computed output against the SM83 routine's actual WRAM output for the same corpus.
- **Reachability (AC-3):** graph-traversal check over the oracle's own computed graph,
  cross-checked against the SM83 routine's actual generated adjacency data.
- **Grammar-validity (AC-4):** for every edge in the generated graph, confirm the biome-family
  pair appears in the adjacency grammar table — a property test across the corpus, not a single
  case.
- **One-KeyItem-per-region (AC-5):** count check across every region in the corpus, generalizing
  T1.11's existing one-carrot-per-zone pattern.
- **Collection mechanic (AC-6):** direct extension of the existing carrot-collection test
  pattern (T8's carrot checks), retargeted to `KeyItemFlags`/`KeyItemCount`.
- **Determinism static audit (AC-7):** Inspection — a direct code read of the generation routine
  confirming no `DIV`/uninitialized-RAM read, per NFR-2200's own Verification Method.
- **Headroom (AC-8):** Inspection — a direct WRAM-layout audit against the built ROM at
  `scale=9`, following the standing `BL-0019` convention this NFR extends.

**Multi-seed/multi-scale corpus:** per R305's extension, a fixed, adequate corpus (not an
unbounded search) covering at minimum: `scale=2` (the floor), `scale=9` (the ceiling, NFR-4200's
stress case), `scale=3` (the shipped-baseline-equivalent default), and several representative
seed values including `seed=0` (the normalization edge case, §7).

## 17. Dependencies

Per FEAT-9000's own Dependencies (carried forward verbatim): FEAT-1000 (generation is invoked
during a state transition, FR-1180); FEAT-3000 (generalizes FR-3210's Carrot-specific collection
rule); FEAT-4000 (generalizes the fixed 9-zone/3×3 structural model). No other `FS-xxx` is a
prerequisite — this is the first Feature Specification for the procgen-world increment, and the
foundational node of its own critical path (FEAT-9000 → FEAT-4100 → FEAT-6100, per FP-04).

## 18. Risks

Carried forward from FEAT-9000's own Risk assessment (Medium-High): genuinely new algorithmic
work with no shipped precedent; the `worldgen.py` reference-generator-oracle pattern is itself a
new verification technique this Feature's entire Test-method verification strategy depends on
working correctly — if the oracle and the SM83 routine drift out of lockstep, the test suite
could pass while the shipped generator is actually wrong (a risk this spec names explicitly, per
§14's Integrity Considerations, rather than assuming the discipline holds automatically).

## 19. Open Questions

1. **The concrete adjacency grammar table's exact contents are not yet decided by any upstream
   artifact.** R212 gives a conceptual example ordering (water → beach → grassland → hills →
   mountains → sky, six categories) and recommends reusing "the existing terrain-family palette
   groups" as the biome-identity vocabulary — but the shipped palette groups are five families
   (grass, sand/dirt, water, stone, brick/red) under different names and a different count than
   R212's six-category example, and GDS-08's delta explicitly states "exact biome-family count
   and palette assignment for a specific `WorldScale` is deferred to the implementation package
   that sizes it" (GDS-08 §8). **This Feature's Acceptance Criteria (#4, grammar-validity)
   cannot be made concrete without this table.** Resolves at: `07-implementation-planning`,
   per GDS-08 §8's own explicit deferral — the package that sizes biome-family count/assignment
   is the correct place to fix the exact table, not this specification (inventing one here would
   be resolving an architectural deferral this stage has no authority to make).
2. **The exact PRNG step sequence and graph-construction algorithm's line-by-line design** is
   named by ADR-0009/R213 at the *approach* level (xorshift-family PRNG, constrained-random graph
   walk over legal edges) but not at the implementation-detail level (e.g. exact edge-proposal
   order, exact biome-assignment order relative to edge construction). Resolves at:
   `07-implementation-planning`/`08-code-implementation` — FEAT-9000's own catalog entry already
   named this as an open question in identical terms; this spec does not narrow it further, since
   doing so would be inventing algorithm detail beyond what GDS-07/09/the ADRs commit to (this
   skill's own SHALL-NOT rule).
3. **Whether any generator-data ROM pointer is needed in the `patches` dict** (beyond the pure
   WRAM working-set this spec describes) depends on whether the grammar table itself is
   ROM-resident data or inline-encoded logic — a decision downstream of Open Question 1.
   Resolves at: `07-implementation-planning`, once Open Question 1 is resolved.

## 20. Related ADRs

ADR-0009 (screen/room-graph generation, on-console, grammar-enforced-by-construction), ADR-0010
(seed & scale model — 16-bit seed, byte scale 2–9), ADR-0011 (MBC1 default wiring — tangential,
no bank-switching dependency for this Feature at any supported scale).
