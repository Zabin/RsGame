# FS-102 — Procedural World Generation & Item-Agnostic Collection

> Feature Specification for [FEAT-9000](../feature-planning/03-feature-catalog.md#feat-9000--procedural-world-generation--item-agnostic-collection-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-9000, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Forward reference (metadata only):** planned by
> [IP-1020](../implementation/packages/IP-1020-procedural-world-generation.md) (2026-07-10),
> which resolves this document's Open Questions 1–3. **VERIFIED 2026-07-10**
> ([VR-1020](../implementation/verification/VR-1020-procedural-world-generation.md)) — all eight
> Acceptance Criteria (§15) confirmed via `test_rom.py`'s T12 suite, 133/133 pass independently
> re-run, ROM byte-identical.
>
> **Revision (2026-07-12, `ADR-0015`/`BL-0093`):** `FR-9130` (the "exactly one `KeyItem` per
> region" rule this document's own §5/§6/§15 AC-5 originally specified and `IP-1020` shipped) is
> **superseded by `FR-9160`**. §6 Workflow A step 5 and §15 AC-5 below are updated to describe the
> new target behavior. §6 Workflow B step 4's victory-condition forward reference is also
> corrected (it previously stated a formula — `KeyItemCount == WorldScale²`, i.e. full 100%
> collection — that was never actually decided by any binding artifact and is now superseded by
> `FR-9161`'s `KeyItemCount == WorldScale`; see the correction below and Open Question 4).
>
> **Implemented 2026-07-13 as
> [IP-1021](../implementation/packages/IP-1021-win-condition-redesign.md)**, **`VERIFIED`
> 2026-07-13 ([VR-1021](../implementation/verification/VR-1021-win-condition-redesign.md))** —
> resolves this document's own **Open
> Question 5** (the per-region encoding: `KEYITEM_FLAGS`'s existing value domain widened in place
> to a tri-state, 0=present/uncollected, 1=present/collected, 2=absent, rather than a new bitmap).
> `test_rom.py` T12.e (revised)/T12.n; `worldgen.py` oracle-mirrored, zero mismatches across the
> full corpus.
>
> **Revision (2026-07-16, `FR-4320`/`BL-0128`):** the biome-family axis this Feature's generation
> routine draws from widens from 5 identities to 9 (Village/Cave/Desert/Plains folded in alongside
> the existing Water/Sand/Grass/Stone/Brick), per a direct project-owner decision baselined as
> `FR-4320`. **Partially resolves Open Question 1** (below): the biome-family *count* is now fixed
> at 9 — the exact grammar-table *ordering* for the four new identities remains open, filed as
> `CR-08` rather than decided here. §10 and §19 updated; no other section changes (this Feature's
> generation *mechanism* — PRNG step order, edge-proposal logic, `FR-9170`'s snap/fallback bias —
> is unaffected, only the domain size it operates over).
>
> **`CR-08` resolved 2026-07-16** (baselined into `FR-4310`, `R212` v1.1). **Planned same day:**
> [IP-1022](../implementation/packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md)
> (`BLOCKED` on `IP-1033`, not yet authorized) implements the widened generation clamp and the
> shared screen-dispatch cascade together — Open Question 1 (grammar-table contents) and Open
> Question 6 (collectible-spawn content) both close once it and `IP-1033` both ship.

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

FR-9100, FR-9110, FR-9120, FR-9130 (**superseded by FR-9160, 2026-07-12 revision — see §6/§15**),
FR-4310, FR-3220; NFR-2200, NFR-4200 — the exact set FEAT-9000 owns, no more, no fewer
(cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-9000--procedural-world-generation--item-agnostic-collection-new--not-yet-implemented)'s
Included Requirements). **FR-9160 is FR-9130's own direct successor, within the same Feature's
scope** — FEAT-9000's own catalog entry names `FR-9130`, not `FR-9160` (the catalog entry itself
is metadata this skill does not edit, per this skill's own SHALL-NOT rule); this is flagged as
Open Question 4 for `05-feature-decomposition` to reconcile, not resolved unilaterally here.

## 6. User Workflows

**Workflow A — New-game world generation** (triggered by FEAT-1100's FR-1180, consumed here):

1. Player has confirmed a `(seed, scale)` pair via FEAT-1100's entry screen.
2. The generation routine (this Feature) receives `(seed, scale)` and executes to completion
   before the first `PLAYING` frame (ADR-0009 §"Decision" point 3).
3. The routine initializes a xorshift-family PRNG from `seed` (0 normalized to 1, per ADR-0010).
4. The routine constructs `scale × scale` regions: for each region, assigns a biome identity and
   proposes adjacency edges, accepting only grammar-legal edges (FR-4310) — a constrained-random
   graph walk, never a post-hoc-validated one (ADR-0009 §"Decision" point 2).
5. **(Revised 2026-07-12, `FR-9160`, supersedes the original step 5's "exactly one `KeyItem` per
   region"):** at the exact point the maze pass's spanning-tree carve completes and before its
   braid pass runs (`FR-9140`), the routine identifies every region whose spanning-tree degree is
   exactly 1 (a leaf). If the leaf count is `>= WORLD_SCALE`, the routine places a `KeyItem` in
   `WORLD_SCALE` of those leaf regions. If the leaf count is `< WORLD_SCALE`, the routine places a
   `KeyItem` in every leaf region, then fills the remainder with additional regions chosen
   randomly (excluding regions already selected) until exactly `WORLD_SCALE` regions hold a
   `KeyItem`. Every other region holds none.
6. The routine confirms (by construction, not a separate check pass) every region is reachable
   from the starting region (FR-9120) — unaffected by step 5's revision, since `KeyItem` placement
   is a subset of already-reachable regions, not a new region type.
7. Control returns to FEAT-1100's flow, which transitions to `INTRO`.

**Sequencing note (step 5's own precondition):** this workflow's step 4 (biome/adjacency) and the
maze pass step 5 now depends on (`FR-9140`, owned by `FS-107`) are two independent passes over the
same grid, per `ADR-0012` point 1 — step 5 does not change their own relative ordering, it only
adds a new consumer (`KeyItem` placement) that must run at one specific point *inside* the maze
pass's own two-phase (carve, then braid) structure, between those two phases.

**Workflow B — KeyItem collection during play** (extends the existing collection-proximity
detection, FR-3100, unchanged):

1. Player moves onto/adjacent to an active `KeyItem` in the current region.
2. FR-3100's existing detection fires (unchanged — this Feature does not modify detection logic).
3. On a `KeyItem` hit: the current region's `KeyItemFlags` bit is set, `KeyItemCount` increments
   by exactly one, and the `KeyItem` is removed from further play (no longer rendered or
   collectible) — mirroring `CARROT_FLAGS`'/`CARROTS_COUNT`'s existing push/pop-HL discipline
   exactly (per `IP-1010`'s established pattern for this class of per-region flag update).
4. **(Corrected 2026-07-12, `FR-9161`):** victory triggers per `FR-3300`'s existing trigger
   *mechanism* (unchanged — `FEAT-1000`'s own PLAYING→VICTORY transition logic is not touched by
   this Feature), but the threshold `FR-9161` supersedes is `KeyItemCount == WORLD_SCALE` — **not**
   the generated world's full region count (`WorldScale²`) this document previously stated here.
   That prior formula was never actually decided by any binding artifact (no ADR/FR ever committed
   to full-collection-as-victory) and is corrected in place, per `ADR-0015`/`BL-0093`'s resolved
   decision. This Feature supplies the count `FR-9160`'s own placement guarantees make always
   achievable; `FR-3300`/`FR-9161`'s own victory-trigger ownership is unaffected by this Feature.

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
  **(2026-07-16 delta, `FR-4320`):** `Region`'s own biome-identity value domain widens from 5
  values to 9 — this Feature's routine (§6 Workflow A step 4) draws from the wider domain, and
  `FR-9170`'s snap/fallback clamp (a `FEAT-9000`-adjacent mechanism, not itself in this Feature's
  own Requirements Implemented list — see Open Question 4) widens in lockstep, `[0,4]`→`[0,8]`.
  The domain's nine concrete identities and their palette-group mapping are `FR-4320`'s own scope,
  not restated here; this Feature's own generation *mechanism* is unaffected, only the range one
  of its outputs may take.
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
- **Revised (2026-07-12, `FR-9160`/`GDS-07` §7c):** `KEYITEM_FLAGS`' own value domain needs a new
  per-region concept — "no `KeyItem` at this region," distinct from the existing "has one,
  collected/not collected." `GDS-07` §7c names the concept and two plausible encodings (widening
  `KEYITEM_FLAGS`' value domain to a tri-state, or a new separate presence bitmap) without
  deciding between them — this Feature's own Data Model Changes inherits that same open choice,
  not resolved here (this skill's own SHALL-NOT-invent-byte-layout rule). Whichever encoding is
  chosen, it is **generation-derived, not itself save-worthy** — recomputed identically every time
  `REGION_GRAPH` regenerates from `(SEED, WORLD_SCALE)` on load, the same "regenerate, don't
  persist" precedent `REGION_GRAPH` itself already sets (`ADR-0012` point 6); only the *collected*
  half of whichever encoding is chosen needs its own SRAM field, unchanged from what FEAT-5300
  already reads today.

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
5. **(Revised 2026-07-12, `FR-9160`, supersedes the original AC-5's "exactly 1 for every
   region"):** for any `(seed, scale)` in a test corpus: (a) exactly `WORLD_SCALE` regions hold a
   `KeyItem`; (b) every pre-braid spanning-tree leaf region holds one, up to `WORLD_SCALE`; (c)
   when leaf count is below `WORLD_SCALE`, the shortfall is filled by additional regions until the
   total reaches exactly `WORLD_SCALE`; (d) the placement result is unchanged by which edges the
   subsequent braid pass reopens.
6. Collecting a region's `KeyItem` sets that region's `KeyItemFlags` bit and increases
   `KeyItemCount` by exactly one, once (FR-3220).
7. Static inspection of the generation routine finds no read of `DIV` or any WRAM address not
   explicitly initialized from `(seed, scale)` or the routine's own prior output (NFR-2200).
8. At world scale 9, the built ROM's WRAM working set for `REGION_GRAPH` + `KEYITEM_FLAGS` fits
   within bank-0 (`0xC000`–`0xCFFF`) without requiring `SVBK` banking (NFR-4200).
9. **(New, 2026-07-12, `FR-9161`):** for any `WORLD_SCALE` in `{2..9}`, the moment `KeyItemCount`
   reaches that world's own `WORLD_SCALE` value, victory triggers — not before, and not requiring
   a threshold independent of `WORLD_SCALE`.

## 16. Verification Plan

Per FR-9100/9110/9120/9160/4310's own Verification Methods (Test, property-test-across-a-corpus),
FR-9161 (Test), and NFR-2200/4200 (Inspection + Test), landing in a new **T12: World Generation**
suite in `test_rom.py` (the next unused suite number, after T11):

- **Determinism (AC-2):** boot twice with the same `(seed, scale)` — a fresh `PyBoy` instance
  each time, following the existing save/reload two-instance harness pattern (R305's extension)
  — assert byte-identical resulting WRAM state both times; separately, compare the `worldgen.py`
  oracle's computed output against the SM83 routine's actual WRAM output for the same corpus.
- **Reachability (AC-3):** graph-traversal check over the oracle's own computed graph,
  cross-checked against the SM83 routine's actual generated adjacency data.
- **Grammar-validity (AC-4):** for every edge in the generated graph, confirm the biome-family
  pair appears in the adjacency grammar table — a property test across the corpus, not a single
  case.
- **Scale-relative, dead-end-prioritized placement (AC-5, revised):** count check across every
  region in the corpus confirming the total equals `WORLD_SCALE`, plus a leaf-priority check
  cross-referencing the `worldgen.py` oracle's own pre-braid spanning-tree parent data (the same
  data `FS-107`'s `T19` suite already computes for its own leaf-adjacent purposes) — replaces the
  retired one-per-region count this AC previously checked (`T1.11`'s own retired pattern).
- **Collection mechanic (AC-6):** direct extension of the existing carrot-collection test
  pattern (T8's carrot checks), retargeted to `KeyItemFlags`/`KeyItemCount`.
- **Determinism static audit (AC-7):** Inspection — a direct code read of the generation routine
  confirming no `DIV`/uninitialized-RAM read, per NFR-2200's own Verification Method.
- **Headroom (AC-8):** Inspection — a direct WRAM-layout audit against the built ROM at
  `scale=9`, following the standing `BL-0019` convention this NFR extends.
- **Scale-relative victory (AC-9, new):** for a corpus spanning `WORLD_SCALE` 2 through 9, drive a
  real playthrough (or a direct `KeyItemCount` WRAM write, mirroring `T4.8`'s own existing
  victory-trigger test pattern) to `KeyItemCount == WORLD_SCALE` and confirm the PLAYING→VICTORY
  transition fires at exactly that value, not before.

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

**New dependency (2026-07-12, `FR-9160`):** this Feature's revised placement step now depends on
`FR-9140` (`FS-107`'s maze-generation pass) having reached its own carve-complete point before
this Feature's placement decision can run — a real, new sequencing dependency `FR-9130`'s original
"one per region, computed independently of maze state" rule never had. `FS-107` is already
`VERIFIED`, so this dependency is satisfied today; it is named here because it did not exist in
this document's original (2026-07-10) form.

## 18. Risks

Carried forward from FEAT-9000's own Risk assessment (Medium-High): genuinely new algorithmic
work with no shipped precedent; the `worldgen.py` reference-generator-oracle pattern is itself a
new verification technique this Feature's entire Test-method verification strategy depends on
working correctly — if the oracle and the SM83 routine drift out of lockstep, the test suite
could pass while the shipped generator is actually wrong (a risk this spec names explicitly, per
§14's Integrity Considerations, rather than assuming the discipline holds automatically).

**New risk (2026-07-12, `FR-9160`):** Low — the placement revision's own implementation risk is
mostly `GW_MAZE_STATE`-reuse correctness (reading parent-direction bits at exactly the right
pipeline moment, before the braid pass overwrites the graph they describe) rather than new
algorithmic uncertainty; `ADR-0015` already resolved the design-level ambiguity, leaving only
ordinary implementation risk for `07`/`08`.

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
   be resolving an architectural deferral this stage has no authority to make). **(2026-07-16
   delta, `FR-4320`/`BL-0128`) — partially resolved, narrowed, not closed:** the biome-family
   *count* is now fixed by `FR-4320` at 9 (the five already-generated identities plus Village,
   Cave, Desert, Plains), so this Open Question's own "count" half is answered. The *ordering*
   half — where the four new identities sit on the grammar table's adjacency axis — remains
   genuinely open, filed as **`CR-08`** (`01-functional-requirements.md`, Candidate
   Requirements) rather than decided here, since `R212` itself anticipates "a refinement of"
   the five-family axis without saying where a refinement's new entries sit. Still resolves at
   `07-implementation-planning`, once `02-research-game-design`/`03-architecture-design-synthesis`
   closes `CR-08` upstream of it.
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
4. **(New, 2026-07-12) `FEAT-9000`'s own catalog entry names `FR-9130`, not `FR-9160`, in its
   Included Requirements.** `FR-9160` is `FR-9130`'s direct successor within this same Feature's
   conceptual scope (placement algorithm, still owned by `FEAT-9000`), but this specification has
   no authority to edit the catalog entry's own content (this skill's own SHALL-NOT rule) — the
   entry's Included Requirements list needs a corresponding update once `FR-9160` is confirmed the
   permanent replacement (i.e. once implemented and `FR-9130` is formally superseded, not merely
   target-noted). Resolves at: `05-feature-decomposition`, the catalog's own owner. Similarly,
   `FR-9161` (victory condition) has **no owning `FEAT-xxxx` catalog entry at all** — `FR-3300`,
   the requirement it supersedes, was never claimed by any Feature's Included Requirements either
   (a pre-existing gap, not new to this revision) — this specification's own §6 Workflow B
   mentions the victory trigger only as a forward cross-reference, never as owned scope, and that
   remains true for `FR-9161` too. Resolves at: `05-feature-decomposition`, if a formal ownership
   assignment for the victory-condition requirement family is ever wanted; not blocking this
   Feature's own implementation-readiness, since `FS-102` never claimed to own it either.
   **(2026-07-16 addition) Two further instances of this exact same gap class:** `FR-9170`
   (finite-mode biome-blob clustering, `FEAT-9000`-adjacent generation-mechanism work) and
   `FR-4320` (nine biome-family identities) are both, like `FR-9160`/`FR-9161` before them, not
   yet named in `FEAT-9000`'s own catalog Included Requirements — confirmed by direct read of
   `03-feature-catalog.md`'s `FEAT-9000` entry, still listing only `FR-9100, FR-9110, FR-9120,
   FR-9130, FR-4310, FR-3220`. Not blocking either requirement's own implementation-readiness
   (`FR-9170` is already `SCHEDULED` per its own backlog entry `BL-0110`; `FR-4320` is fully
   specified by this document's own §10/§19 delta) — recorded here as the same class of
   catalog-bookkeeping gap, for `05-feature-decomposition` to reconcile whenever it next touches
   `FEAT-9000`'s own entry, not urgent enough to warrant its own dedicated pass.
5. **(New, 2026-07-12; RESOLVED 2026-07-13) The exact per-region tri-state encoding** (`GDS-07`
   §7c's two named candidates: widen `KEYITEM_FLAGS`' value domain, or a new separate presence
   bitmap) was left undecided by `ADR-0015`/`GDS-07` deliberately, to be resolved at
   `07-implementation-planning` against the real `KEYITEM_FLAGS`/`setup_zone_collects` code. **
   Resolved by `IP-1021` §6**: `KEYITEM_FLAGS`'s existing value domain is widened in place (0 =
   present/uncollected, 1 = present/collected, 2 = absent) — both real consumers
   (`setup_zone_collects`, `check_collisions`) already treat any nonzero value as "no active item
   here," exactly correct for "absent" too, so no separate bitmap or downstream changes were
   needed.
6. **(New, 2026-07-16, `FR-4320`/`BL-0128`) Collectible-spawn-table content for the four newly
   folded biome identities does not exist yet.** This Feature's own Workflow B / §4 Scope covers
   the collection *mechanic* (item-agnostic, generalized from `FR-3210`) but the per-region spawn
   *content* itself (`ZONE_COLLECTS`, a `tilemaps.py` data table `FEAT-4100`/`FS-103` more
   directly owns, consumed by this Feature's `setup_zone_collects` mechanism) currently has only
   5 of the 9 identities' spawn lists — `IP-9070` deleted the other four (Village, Cave, Desert,
   Plains) rather than merely orphaning them when it consolidated `ZONE_COLLECTS` to five
   biome-family-representative lists, confirmed by direct citation of that package's own §6 text.
   Until fresh spawn tables are authored, a region assigned one of those four identities would
   have no collectible to place — a real content-completeness gap this Feature's own generation
   routine does not itself detect or guard against (mirrors this document's own §12 Error
   Handling framing: generator-guaranteed properties are enforced by construction, not checked
   defensively at runtime). Resolves at: `08-content-authoring` (author the four missing
   `ZONE_COLLECTS` lists, mirroring the five existing ones' own format), scheduled via a future
   `07-implementation-planning` package — see `FS-103`'s own Open Questions for the paired
   screen-dispatch half of the same underlying content-completeness question.

## 20. Related ADRs

ADR-0009 (screen/room-graph generation, on-console, grammar-enforced-by-construction), ADR-0010
(seed & scale model — 16-bit seed, byte scale 2–9), ADR-0011 (MBC1 default wiring — tangential,
no bank-switching dependency for this Feature at any supported scale). **Added 2026-07-12:**
ADR-0015 (dead-end-anchored treasure placement + scale-count win condition — the binding decision
behind this revision's §6/§10/§15/§16 changes), ADR-0012 (the maze pass this revision's placement
step now reads intermediate state from).
