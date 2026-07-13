# R305 — Emulator-Based Test Design

- **Document ID:** R305 · **Version:** 1.1 · **Status:** ✅
- **Dependencies:** R301 (the PyBoy API these tests are built on), R304 (the header-check class
  that stays stable across game-logic rewrites), R212/R213/R111 (the grammar/algorithm/PRNG this
  topic's C10 determinism-testing extension grounds test design against)
- **Referenced By:** R213 (assumes this topic's reference-generator oracle pattern), R111
  (same), R307 (this suite is the characterization baseline every refactor is proven against) —
  **this topic directly grounds the BL-0006/BL-0008 remediation, MSTR-001 C10's
  determinism-testing strategy (2026-07-09), and, as of 2026-07-11, the `BL-0047`/`BL-0048`/
  `BL-0051`/`BL-0052`/`BL-0053` remediation packages' regression-test design**
- **Produces:** grounds the rewrite `test_rom.py` needs against the current WRAM map; grounds the
  generated-world test suite's design; grounds four concrete testing-convention fixes for the
  gaps a live bug batch exposed (2026-07-11)
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R301, R304, R212, R213, R111, R302

## Purpose

How to design memory-assertion tests against *this specific game's* current state model — written
specifically to close backlog `BL-0006` (Critical: `test_rom.py` asserts pre-rewrite WRAM
semantics and cannot currently pass) with concrete, address-correct guidance rather than generic
"use PyBoy to test things" advice.

## Scope

Memory-assertion vs. pixel-assertion test design, frame-count determinism, save/reload test
harnesses, and — the concrete deliverable — the **current, correct WRAM addresses and values**
`test_rom.py`'s stale suites must be rewritten against.

## Concepts

**Memory assertions vs. pixel assertions.** A memory assertion reads a specific WRAM/HRAM address
and checks its value against an expected constant (e.g. "game state equals 2"); a pixel assertion
inspects `screen.image` (R301) for rendered content. Memory assertions are strongly preferred for
*logic* correctness — they're exact, fast, and immune to color/palette changes; pixel assertions
(or full screenshots for human review) are appropriate for *content* correctness (does a screen
look right, R106... see R109-adjacent content-review use cases) but a poor tool for "did the state
machine transition correctly," since a passing pixel-diff doesn't prove the *reason* the pixels
are what they are.

**Frame-count determinism.** A GBC game (and this emulator) is deterministic given the same ROM +
input sequence + starting state — the same button-press-at-frame-N produces the same resulting
state every run. Tests exploit this by using **generous, fixed frame-count waits** after each
input (this project's existing tests use 40–80-frame settle windows) rather than polling for a
state change — a fixed wait that's long enough is simpler and just as deterministic as a polling
loop, and matches the existing test style.

**Save/reload harnesses.** Testing persistence requires: play to a known state → `stop()` (which
writes the `.ram` file per R301) → construct a **second** `PyBoy` instance against the same ROM
path (which auto-loads that `.ram` file) → assert the reloaded state matches. This project's
existing T10 suite already follows this two-instance pattern; it is unaffected by the WRAM-model
change since save/load mechanics (not the specific fields saved) are what it tests, though its
specific field list (see below) does need updating for `CARROT_FLAGS`/`CARROTS_COUNT`.

## Operational Context — the concrete rewrite target for BL-0006

The current, shipped WRAM map (confirmed by direct `asm_game.py` read, 2026-07-06):

| Address | Name | Meaning |
|---|---|---|
| `0xC000` | `GAMESTATE` | 0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY (unchanged from the pre-rewrite model) |
| `0xC001`/`0xC002` | `PLAYER_X`/`PLAYER_Y` | pixel position (unchanged) |
| `0xC006` | `SCORE` | 0–99, star/flower score (unchanged) |
| `0xC008` | `CUR_ZONE` | **0–8** (was 0–2 pre-rewrite) — index into the 3×3 grid, `row = zone//3, col = zone%3` |
| `0xC009` | `CARROTS_COUNT` | **0–9** (replaces the old 3-bit `GIFTS` bitfield at this same address) |
| `0xC015`–`0xC01D` | `CARROT_FLAGS` | **9 bytes, one per zone**, 0/1 (replaces the old 3-bit bitfield model entirely) |

**Victory condition:** `CARROTS_COUNT == 9` triggers `GAMESTATE = 5` (VICTORY) — replacing the old
`GIFTS bitfield == 0x07` check. **Zone bounds:** 0–8, not 0–2; edge-transition tests must use zone
0 (top-left, no up/left neighbor), zone 8 (bottom-right, no down/right neighbor), or a specific
row/col boundary (e.g. zone 2 has no right neighbor, being `row=0,col=2`) — not "zone 2 is the
last zone," which was only true under the old 1×3 layout.

**What must change in each stale suite** (per `BL-0006`'s findings, now with the fix target
spelled out):
- **T4.8/T8.8-style victory checks:** replace `pb.memory[0xC009] == 0x07` (bitfield) with a
  sequence that sets `pb.memory[CARROT_FLAGS+i] = 1` for all 9 `i` **and** `pb.memory[0xC009] = 9`
  (both must be set together, since `CARROTS_COUNT` is a separate counter, not derived from
  `CARROT_FLAGS` — confirm this against `asm_game.py`'s victory-check code path before writing the
  assertion, since a test that only sets one of the two would not exercise the real check the game
  code performs).
- **T7.9/T9.x-style zone-boundary checks:** replace any assumption of "zone 2 is the last zone"
  with the correct 3×3 boundary logic (`col==2` → no right neighbor, `col==0` → no left neighbor,
  `row==0` → no up neighbor, `row==2` → no down neighbor) and re-derive which specific zone index
  each edge-case test should force via `pb.memory[0xC008] = N`.
- **T10-style save/reload checks:** the field list must include `CARROT_FLAGS` (9 bytes) and
  `CARROTS_COUNT`, matching whatever `asm_game.py`'s actual save routine persists (cross-check
  against the save-routine's field list directly — R106 already confirms the SRAM enable/disable
  bracketing is correct; this is a separate check that the *field list* is complete).
- **T1 (header) suite needs no changes at all** — see R304.

## Implementation Guidance

- **Rewrite, don't patch, the stale suites.** Given the win-condition model changed shape (bitfield
  → counter + array), a line-by-line patch of the old assertions risks leaving a half-correct
  hybrid; re-derive each stale check from the table above and the actual `asm_game.py` code path
  it's meant to verify.
- **Add new suite coverage for the 9-zone grid's edges specifically** — the old suite only had to
  cover a 1×3 line (2 edges); a 3×3 grid has 4 distinct edge classes (corner-with-2-neighbors,
  edge-with-3-neighbors, etc.) that deserve explicit coverage, not just "one test per axis."
- **Keep the existing settle-frame-count style** (40–80 frames) rather than introducing a
  different waiting convention in the same file.
- **This is squarely `08-code-implementation` scope once packaged by `07-implementation-planning`**
  — this research topic supplies the *what to assert*; the package itself (BL-0008's umbrella)
  should cite this topic directly in its `Tests to Add`/`Implementation Tasks` fields.

## Testing a deterministic procedurally generated world (2026-07-09, grounds MSTR-001 C10/A9)

**The core testing problem C10 introduces is new in kind, not just in scope: how do you assert
"correct" for content that doesn't exist until generated?** Every existing suite (T1–T11) checks
against **fixed, hand-authored** expected values — a specific WRAM address always holds a specific
value for a specific input sequence. A generated world has no such fixed answer: the expected
tilemap/WRAM state for zone 3 depends on *which seed and scale produced it*. This section grounds
the testing pattern the adopted increment plan's Phase 2 names explicitly
([PLAN-requirements-aesthetics-story-map.md](../../pipeline/PLAN-requirements-aesthetics-story-map.md)
§2), extending this topic's existing memory-assertion/save-reload-harness patterns rather than
replacing them.

**The Python reference-generator oracle pattern.** This project's build/test relationship already
has the right shape to extend: `build_rom.py` (Python, build-side) and `test_rom.py` (Python,
also build-side, driving the ROM via PyBoy) are two independent Python programs that must agree
about what the ROM does — `test_rom.py` today encodes its expectations as literal constants
(`CARROT_FLAGS`, `CARROTS_COUNT==9`, exact zone-boundary math) because the current game has no
per-run variability to predict. **A generated world needs one more piece: a Python function that,
given `(seed, scale)`, computes the *same* result the SM83 generation routine (R213/R111) would
produce on real hardware** — not by running the SM83 code, but by re-implementing its exact
algorithm (xorshift step sequence, graph-construction rule, biome assignment) in Python. This
oracle function becomes the source of "expected" values `test_rom.py`'s assertions compare
against, for any seed/scale pair — turning generated-content testing back into the same
memory-assertion pattern this topic already recommends (an exact value comparison, not a fuzzy
plausibility check), just with a *computed* rather than *literal* expected value.

**This is not a novel pattern for this project — it is R302's existing discipline, extended.**
R302 already documents that `build_rom.py` and `asm_game.py`'s SM83 code must produce *exactly*
consistent results for anything cross-referenced between them (patch-point addresses, label
resolution); a Python reference-generator oracle is the same discipline applied to *generated
content* rather than *static addresses* — the oracle and the SM83 routine are two independent
implementations of one algorithm that must be kept in lockstep by direct correspondence (same
PRNG step order, same grammar-check logic), the same way `build_rom.py`'s screen layout and
`asm_game.py`'s zone-lookup table must already agree today without any shared code enforcing it.

**Multi-seed/multi-scale property testing.** Because no single seed's output can stand in for
"the generator is correct" (unlike a fixed hand-authored world, where one test run proves
everything), determinism and correctness testing for C10 needs a **corpus of seeds** (and, per
D6, scales) rather than one canonical test case — following the same generous-fixed-iteration
style this topic's existing frame-count-wait convention already models (a fixed, adequate set
rather than an unbounded search). Concretely, per seed/scale pair in the corpus:
- **Determinism**: boot twice with the same `(seed, scale)` (a fresh `PyBoy` instance each time,
  following this topic's existing save/reload two-instance pattern), assert the resulting
  WRAM/tilemap state is byte-identical both times.
- **Reachability**: every generated region is reachable from the start region via legal
  transitions — a graph-traversal check over the oracle's own computed graph, cross-checked
  against the actual in-ROM screen-adjacency table the generator wrote.
- **Exactly-one-key-item-per-region**: the direct generalization of `BL-0017`'s existing
  "exactly one carrot per zone" invariant (already a tested property, T1.11) — same check, applied
  across the corpus instead of the single fixed 3×3 layout.
- **Grammar-valid adjacency (R212)**: for every generated region-pair adjacency, assert it appears
  in R212's adjacency table — a new check class this project's suite has no precedent for yet,
  but structurally the same shape as any other memory-assertion check (read the generated
  adjacency data, compare against a known-valid table).

**Screenshot-assertion strategy for seam/transition cleanliness (grounds MSTR-001 C8/D4).** This
topic's existing memory-vs-pixel distinction directly resolves the "every screen clean" quality
bar: **the grammar/reachability/one-item invariants above are memory assertions** (exact, fast,
what R305 already recommends for logic correctness) — but "does the screen actually *look*
clean, no visual garbage at a seam" is irreducibly a **pixel-level** question, exactly the case
this topic already carves out for `screen.image`-based screenshots (R301). Recommend: for a
sampled subset of the seed corpus (not every seed — screenshot capture is comparatively
expensive), capture `.image.save(...)` screenshots at every generated screen boundary/transition
and either (a) assert programmatically-checkable properties directly from pixel data where
possible (no undefined/blank tile patterns at the seam), or (b) route screenshots to
`09-content-review`'s existing human-judgment process (its stated scope already covers "screen
composition... does this screen read well") for the properties that genuinely need a human eye,
rather than inventing a new automated aesthetic-judgment mechanism this project's tooling has no
precedent for.

### Sources
No new external citation — this section grounds testing *methodology* directly in this project's
own existing, verified code (`build_rom.py`/`test_rom.py`/`asm_game.py`) and its own prior
research (R212's adjacency grammar, R213's generator recommendation, R111's PRNG/WRAM grounding,
`BL-0017`'s precedent invariant), per this skill's own guidance that the project's working code
and tests are Tier-A evidence.

## Testing-convention gaps confirmed by a live bug batch (2026-07-11, grounds `BL-0057`)

**Six bugs (`BL-0047`/`BL-0048`/`BL-0051`/`BL-0052`/`BL-0053`, plus the `BL-0049` UI-affordance
gap) all shipped through a suite reporting 180/180, and four of the six were in code
`09-package-verification` had already marked `VERIFIED`.** This is the concrete evidence base for
tightening the conventions above — the multi-seed/multi-scale section (immediately above) named
the right shape in the abstract; these four gaps say precisely where the actual `test_rom.py`
suite still falls short of it, cited to the exact lines.

**Gap 1 — a shared fixture's fixed default silently opts every consumer out of the parameter it's
supposed to test.** `advance_to_playing()` (`test_rom.py:115`) confirms new-game defaults at
"seed=0 → normalized to 1, **scale=3**" — every suite that calls it (`T4`, `T5`, `T7`, `T8`, `T9`,
`T10`, `T11`, `T13`, `T14`, `T15`, i.e. nearly the whole file) therefore plays at `WORLD_SCALE=3`
and never any other value. `T9` (zone transitions) is the suite whose entire job is exercising
navigation — but its own in-code comments (`T9.5`, "No right transition from col 2 (z2)") still
speak in the pre-procgen fixed-3×3 vocabulary (zone *column* 2) rather than a generated
`REGION_GRAPH` neighbor check, because at `scale=3` the old hardcoded `check_zone_transition`
(`asm_game.py:566`) and a real generated 3×3 world are indistinguishable by any test that only
plays at the default scale. `T12` (world generation, `test_rom.py:825`) *does* exercise a
15-entry `(seed, scale)` corpus (`scale ∈ {2,3,9}`) — but only via `invoke_generate_world`'s
direct PC-hijack call into `generate_world` itself (data-only), never through
`advance_to_playing`'s actual gameplay path. **The corpus existed for generation; it was never
threaded through to the suites that test *playing* the generated result.** Convention: any shared
fixture that defaults a tunable/generated parameter must have at least one consuming suite that
overrides the default to a non-trivial value from the same corpus already validated at the
generation layer — a parameter tested only where it's generated, and never where it's *consumed*,
is only half-tested.

**Gap 2 — directional/existence assertions pass under a wrong boundary constant.** `T7.1`/`T7.5`
assert `"RIGHT increases X"` / `"UP decreases Y"` — true for both the correct clamp and the actual
shipped (wrong) one, since both move the sprite in the right direction, just to the wrong final
value (`BL-0051`/`BL-0052`: the UP clamp's floor is `17` where the field's true top edge is `8`;
the RIGHT clamp's ceiling is `159` where the screen-flush maximum is `152`). Likewise `T8.4`
(collection) asserts a placed item *is* collected, using a placement inside the actual (wrong)
±9px window — it never places an item at a boundary the wrong window and the correct bounding-box
test would disagree on (`BL-0053`). Convention: for any spatial/numeric behavior with a known or
derivable exact boundary (a screen edge, a sprite's bounding box, a clamp), the test must assert
the **exact boundary value**, not just that the value moved in the expected direction or that some
in-range placement worked — pick the assertion point specifically at (or just outside) the
boundary, not comfortably inside it.

**Gap 3 — a tested state machine's cells were covered per-state, not per-(state × entry-condition
× action).** `T14.a1`–`a4` cover MAIN MENU's *presence* of "continue" (no save / valid save /
version-mismatched save) and `T14.c1` covers SEED/SCALE ENTRY's B-cancel — but no `T14` check ever
drives UP/DOWN *from* MAIN MENU *with a valid save present* and asserts the cursor actually moves
(`BL-0048`: `check_save_valid`'s `MM_CURSOR` reset silently no-ops every toggle in exactly this
cell). The menu is a 2×2 matrix (save present/absent × continue/new-game selectable) plus an input
axis (UP/DOWN); the suite covered the presence axis exhaustively and the selection axis not at
all. Convention: for a menu or state machine with more than one entry condition and more than one
in-state action, enumerate the full (entry-condition × action) cross-product explicitly before
writing checks, not just one check per reachable state — "the option is shown" and "the option is
selectable" are different claims and need different assertions.

**Gap 4 — a build-side oracle proves the data, not the runtime path that consumes it.** This
topic's own "reference-generator oracle pattern" (above) is correct and necessary — `T12.b`'s
oracle-parity check and `T12.c`'s BFS-over-the-oracle-graph reachability check are exactly right
for proving `generate_world`'s *output* is correct. But `BL-0047` shows this is not sufficient for
a player-facing reachability claim: `REGION_GRAPH` is generated correctly (confirmed, `T12.c`),
and the *rendering* dispatch (`dsr_p`) correctly reads it (confirmed, `T13.a`) — but the
*navigation* code path a player actually drives (`check_zone_transition`) reads neither, and no
test drives a button-press-based traversal of a generated (non-default-scale) world to notice.
Convention: **"the oracle says this region graph is fully reachable" and "a player can actually
reach every region by pressing buttons" are two separate claims** — the first is a data-structure
property, checkable once against the oracle; the second requires a runtime-driven check (hold
DOWN/RIGHT, or systematically walk the graph via `PLAYER_X`/`PLAYER_Y` forcing plus real
`check_zone_transition` execution) at a scale where the oracle and any stale hardcoded fallback
would visibly disagree (`scale ≠ 3`, since `scale = 3` is exactly the value at which this
project's retired fixed-grid model degenerates into a correct-looking coincidence).

### Sources
No new external citation — this section, like the one above it, grounds testing methodology
directly in this project's own code and test suite (`test_rom.py:115`, `:580-601`, `:825-827`;
`asm_game.py:566` `check_zone_transition`, `:450-483` the movement clamps, `:495-516`
`check_collisions`) and the concrete bug batch (`BL-0047`/`BL-0048`/`BL-0051`/`BL-0052`/`BL-0053`,
filed 2026-07-11) that exposed each gap, per this skill's own guidance that the project's working
code and tests are Tier-A evidence.

## Feature Mapping

*(No `FS-xxx` authored yet — this topic's primary consumer is expected to be a `07-implementation-
planning` package for BL-0006/BL-0008, not a Feature Specification. The C10 extension above
grounds a future package for the world-generation Feature instead. The 2026-07-11 gap analysis's
primary consumers are the `07-implementation-planning` remediation packages for
`BL-0047`/`BL-0048`/`BL-0051`/`BL-0052`/`BL-0053` themselves — each should cite the relevant gap
above in its own `Tests to Add` field so the remediation's regression test actually closes the gap
that let the bug ship, not just re-assert the fixed behavior the same way the original, insufficient
check did.)*

## Related Topics

R301 (the PyBoy API these tests are built on, incl. `screen.image` for the screenshot-assertion
strategy) · R304 (the one suite class — header validation — that needs no rewrite) · R212 (the
adjacency grammar the new grammar-validity check tests against) · R213 (the generation algorithm
the reference-generator oracle mirrors) · R111 (the PRNG/WRAM implementation the oracle's Python
reimplementation must match step-for-step) · R302 (the build-side codegen discipline this topic's
oracle pattern extends).
