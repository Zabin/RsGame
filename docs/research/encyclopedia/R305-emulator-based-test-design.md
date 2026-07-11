# R305 — Emulator-Based Test Design

- **Document ID:** R305 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R301 (the PyBoy API these tests are built on), R304 (the header-check class
  that stays stable across game-logic rewrites), R212/R213/R111 (the grammar/algorithm/PRNG this
  topic's C10 determinism-testing extension grounds test design against)
- **Referenced By:** R213 (assumes this topic's reference-generator oracle pattern), R111
  (same) — **this topic directly grounds the BL-0006/BL-0008 remediation and, as of 2026-07-09,
  MSTR-001 C10's determinism-testing strategy**
- **Produces:** grounds the rewrite `test_rom.py` needs against the current WRAM map; grounds the
  future generated-world test suite's design
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

## Feature Mapping

*(No `FS-xxx` authored yet — this topic's primary consumer is expected to be a `07-implementation-
planning` package for BL-0006/BL-0008, not a Feature Specification. The C10 extension above
grounds a future package for the world-generation Feature instead.)*

## Related Topics

R301 (the PyBoy API these tests are built on, incl. `screen.image` for the screenshot-assertion
strategy) · R304 (the one suite class — header validation — that needs no rewrite) · R212 (the
adjacency grammar the new grammar-validity check tests against) · R213 (the generation algorithm
the reference-generator oracle mirrors) · R111 (the PRNG/WRAM implementation the oracle's Python
reimplementation must match step-for-step) · R302 (the build-side codegen discipline this topic's
oracle pattern extends).
