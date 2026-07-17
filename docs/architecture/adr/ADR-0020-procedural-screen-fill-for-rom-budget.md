# ADR-0020 — Runtime procedural background-fill + landmark-overlay rendering for ROM-constrained screens

**Status:** Accepted (2026-07-17)

## Context

`IP-1022` (finite-mode nine-identity generation & screen dispatch, wiring the four newly-folded
biome screens Village/Cave/Desert/Plains into `ALL_SCREENS`) is `BLOCKED` on a genuine ROM-budget
overflow: the four screens' full baked tile+attr arrays cost 4,608 bytes (`W*H=576` tiles + 576
attrs each) against only 1,406 bytes of headroom — a ~3,358-byte shortfall (`BL-0134`, full byte
math in `docs/pipeline/backlog.md`).

**Two paths exist to close this gap**, both already touched by this project's own records:
`ADR-0011` (accepted 2026-07-09) already commits to MBC1 default-wiring bank switching as the
long-term ROM-ceiling answer, explicitly naming "when a specific package's content genuinely
cannot fit remaining bank-0 headroom" as its own cutover trigger — this is that trigger firing.
But `ADR-0011`'s own Consequences section is explicit that *none* of its implementation exists yet
(`gbc_lib.py` has no bank-select emission, `build_rom.py` lays out one flat buffer, the
patch-point mechanism has no bank-relative variant) — cutting over is a real, multi-file engine
extension, not a quick fix.

**A second, narrower option exists specifically for this package's own content**, found by direct
inspection of `tilemaps.py`'s own four new screen functions: every one of them fills its `32×18`
background from a **small, closed-form arithmetic formula** already expressed in Python — e.g.
`cave_screen`'s `seed = (y*13 + x*5 + 7) % 18` deciding floor-vs-bump per tile, `village_screen`'s
`(x+y)%2` cobblestone checkerboard, `desert_screen`'s `(y*19+x*11+9)%17`, `plains_screen`'s
`(y*23+x*7+2)%16` — with a short, fixed list of hand-placed "landmark" tiles (houses, crystals,
cacti, flowers, etc.) overlaid on top. Today, `build_rom.py` bakes the *result* of running these
formulas (the full 576-tile grid) into ROM as a flat byte array; the formula itself is discarded
after the build script runs.

**This is not a cycle-budget-constrained context.** Direct code read of `do_screen_redraw`
(`asm_game.py:1306-1426`, the routine `IP-1022`'s dispatch cascade extends) confirms the entire
screen-composition dispatch — including `copy_screen`, which currently `memcpy`s each screen's
baked arrays into VRAM — runs with **the LCD fully disabled** (`XOR_A();LDH_n_A(LCDC)` at
`dsr_wv`, re-enabled only at `dsr_done`). This is a structurally different code path from
`NFR-1400`'s own measured, `NOT MET` per-frame concern (Infinite Mode's separate
`inf_ensure_window`/`inf_materialize_region` routine, called from `check_zone_transition`'s
context, which has no such LCD-off bracket available). A runtime fill routine added to
`do_screen_redraw`'s own dispatch carries none of the risk that would apply to Infinite Mode's own
per-transition materialization path.

## Decision

**Render the four newly-folded biome screens (Village/Cave/Desert/Plains) via a runtime
procedural-fill routine plus a landmark-overlay data list, instead of baking their full tile+attr
arrays into ROM.** Concretely:

- A new, shared SM83 subroutine (analogous in spirit to `generate_world`'s own on-device
  computation, `ADR-0009`) fills each of the four screens' background tiles by evaluating the same
  small modulo formula its Python `*_screen()` function already uses, writing directly to VRAM
  inside `do_screen_redraw`'s existing LCD-off bracket — the same place `copy_screen`'s `memcpy`
  runs today.
- Each screen's landmarks (houses, lanterns, fences, crystals, drips, bats, cacti, bones,
  pyramids, flowers, tall-grass, butterflies) are stored as a short **landmark-overlay list**
  — `(tile_x, tile_y, tile_id, attr)` tuples, mirroring `ZONE_COLLECTS`'s own established
  `(x, y, type)` compactness convention — applied after the procedural base fill completes.
- **Scope: these four screens only, this pass.** The five already-shipped, already-`VERIFIED`
  screens (`lake`/`beach`/`forest`/`mountain`/`castle`) keep their existing baked-array format
  unchanged — revisiting a shipped, verified rendering path for a ROM-efficiency gain it does not
  currently need is an unnecessary regression-risk trade, not a requirement of this decision. The
  same technique remains available as a future efficiency option for those five if a later package
  needs the headroom; not applied speculatively here.
- **Verification must include an oracle-parity check** — the same discipline `worldgen.py`/
  `generate_world`'s own lockstep testing already established (`R305`, `T12.b`'s own precedent):
  the on-device fill routine's output must be proven byte-for-byte identical to the existing
  Python `*_screen()` functions' own tile/attr arrays, for all four screens, not merely visually
  similar.

**This closes `BL-0134`'s ROM gap without bank switching.** Estimated recovery: the four screens'
combined baked cost (4,608 bytes) drops to a landmark-overlay list of roughly 50–100 bytes per
screen (~300 bytes total across four screens) plus a small shared fill-routine (~100–200 bytes of
new code, reused across all four) — a net recovery on the order of 4,000+ bytes, comfortably
exceeding the ~3,358-byte shortfall with margin, independent of and in addition to `IP-9150`'s
already-packaged 1,152-byte tile-data padding trim (`BL-0134`). Exact byte counts are confirmed at
implementation time (`07`/`08`), not fixed here — this level records the strategy, not a
byte-exact budget, per this project's own established ADR altitude (`ADR-0001`/`ADR-0011`'s own
precedent).

**Bank switching (`ADR-0011`) is not required to close this specific gap.** Its own architecture
decision stands unchanged and remains the long-term answer once ROM-cheap tricks like this one are
exhausted — but this pass does not trigger its implementation, since a narrower, lower-risk,
already-precedented technique closes the gap on its own. `ADR-0011`'s own cutover trigger
("content genuinely cannot fit remaining bank-0 headroom" *after* available ROM-efficiency options
are exhausted) is not yet met.

## Consequences

- **`GDS-08` (Presentation Architecture) gains a documented exception**: not every screen is a
  fully-baked static array — four of nine biome-family screens are procedurally filled at
  redraw-time plus a landmark overlay. This is a deliberate content-specific optimization, not a
  blanket architecture change; the five original screens are explicitly unaffected. `GDS-08`'s own
  text needs a delta noting this exception the next time that level is touched.
- **`GDS-09` (Interface Specification) gains a new data shape**: the landmark-overlay list format
  (`(tile_x, tile_y, tile_id, attr)` tuples) is a new per-screen data contract, alongside the
  existing `ALL_SCREENS`/`ZONE_COLLECTS` contracts. `tilemaps.py`'s four `*_screen()` Python
  functions are **not removed** — they remain the source of truth the on-device routine's output
  must match (the oracle-parity obligation above), and the currently-shipped five-screen
  `ALL_SCREENS`/`build_rom.py` baking path continues unchanged for those five.
- **`do_screen_redraw`/`copy_screen`'s own dispatch cascade gains a new branch shape**: the four
  new identities' dispatch targets call the procedural-fill routine (parameterized by
  screen-specific formula constants + a landmark-list pointer) instead of `_dsr_family`'s existing
  `memcpy`-from-ROM pattern. `IP-1022`'s own package needs re-planning (`07`) against this new
  Files-to-Modify/Interfaces shape rather than its originally-planned "append to `ALL_SCREENS`,
  bake the array" approach.
- **A new, small, reusable SM83 subroutine is added** — the formula evaluator (modulo arithmetic
  matching each screen's own Python formula) plus a landmark-overlay applier. Both run inside the
  existing LCD-off bracket; no new timing risk, confirmed by direct code read of the call context
  this decision itself documents above.
- **Test suite impact**: a new oracle-parity check (mirroring `T12.b`'s own established pattern)
  is required before this can be considered `VERIFIED` — this is a Verification Checklist
  obligation for whichever package implements it, not optional.
- **Does not implement anything.** The `gbc_lib.py`/`asm_game.py`/`tilemaps.py`/`build_rom.py`
  changes, and the re-cut `IP-1022` package, ship through the normal `07`→`08`→`09` path, gated by
  the user's already-recorded authorization for `IP-1022`'s own scope (this is a strategy change
  within that package's existing, already-authorized objective — supplying the four screens'
  content — not new scope requiring a fresh G3 ask).
- **Does not retire or contradict `ADR-0011`.** Bank switching remains the committed long-term
  direction for when ROM-cheap options are exhausted; this ADR records that this specific gap does
  not require reaching for it.
