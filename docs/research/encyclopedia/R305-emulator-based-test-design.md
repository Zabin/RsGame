# R305 — Emulator-Based Test Design

- **Document ID:** R305 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R301 (the PyBoy API these tests are built on), R304 (the header-check class
  that stays stable across game-logic rewrites)
- **Referenced By:** none yet — **this topic directly grounds the BL-0006/BL-0008 remediation**
- **Produces:** grounds the rewrite `test_rom.py` needs against the current WRAM map
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R301, R304

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

## Feature Mapping

*(No `FS-xxx` authored yet — this topic's primary consumer is expected to be a `07-implementation-
planning` package for BL-0006/BL-0008, not a Feature Specification.)*

## Related Topics

R301 (the PyBoy API these tests are built on) · R304 (the one suite class — header validation —
that needs no rewrite).
