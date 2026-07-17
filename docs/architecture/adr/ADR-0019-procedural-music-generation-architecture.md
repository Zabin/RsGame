# ADR-0019 — Procedural music generation: build-time theme-and-variation, transposition + tempo scaling, no new APU channel

**Status:** Accepted (2026-07-16)

## Context

`BL-0127` (project-owner request, filed via `00-intake`): "procgen the music with a main theme
for the game and sub-themes based on zone." `BL-0128`'s own resolution (`FR-4320`, baselined
2026-07-16) fixes the natural sub-theme target at **nine** — the biome-family identity axis
finite-mode and Infinite Mode generation both now share (Water, Sand, Grass, Stone, Brick,
Village, Cave, Desert, Plains).

[R217](../../research/encyclopedia/R217-procedural-generative-music-composition.md) grounds this
capability but explicitly declines to decide it (per this pipeline's own SHALL-NOT-invent-a-
design-decision discipline): it names a real transform menu (transposition, tempo/duration
scaling, a shared-ostinato-plus-per-identity-melody structure) and a real channel-budget question
(only the ostinato option consumes a second APU channel), and recommends — without deciding —
build-time (Python) generation over genuine SM83 runtime generation, since the sub-theme set is
fixed and finite (nine identities), unlike the world's own unbounded geometry that actually
justifies `worldgen.py`'s on-console generation (`ADR-0009`).

The shipped game today has **zero per-zone/per-biome audio infrastructure of any kind** —
`music.py` compiles one hand-authored 16-bar track (`SONG`, 181 bytes per direct measurement) to
a single APU channel (pulse channel 1), played by `music_tick` unconditionally every frame
regardless of `GAMESTATE`/region/biome (confirmed by direct code read at `BL-0127`'s own intake).
No `FS-xxx`, ADR, or GDS delta covers any per-zone audio variation, procedural or not — this is a
genuinely new capability cluster, not an extension of an existing one.

## Decision

**Adopt build-time (Python), theme-and-variation procedural generation of eight new sub-themes
from the existing shipped main theme, using transposition and tempo/duration scaling as the
transform mechanism — explicitly deferring the shared-ostinato/second-channel option, not
adopting it now.**

Concretely:

1. **The existing shipped 16-bar `SONG` (`music.py`, C major, channel 1) becomes the main theme,
   unchanged.** No new composition — `R207`'s own prior review already confirmed this track reads
   as intentional, era-appropriate chiptune melody; re-authoring it is out of this ADR's own
   scope and unnecessary to satisfy `BL-0127`'s own request ("a main theme for the game," not "a
   new main theme").
2. **Generation is build-time (Python), not runtime (SM83), per `R217`'s own recommendation,
   confirmed here rather than merely inherited.** The sub-theme set is fixed and finite (nine
   identities, `FR-4320`) and known entirely at ROM-build time — unlike `worldgen.py`'s own
   generation, which must run on-console because the *world* it generates is parameterized by a
   player-chosen seed at new-game creation (`ADR-0009` point 3, `ADR-0010`). Nothing about a
   biome-family identity's own sub-theme depends on the player's seed; generating all nine once,
   at build time, and shipping the fixed result is strictly simpler and carries none of
   `worldgen.py`'s own oracle/lockstep discipline burden (`ADR-0009`'s own Consequences) — **there
   is no SM83-side counterpart to keep in sync, because there is no runtime generation at all.**
3. **This is *not* `worldgen.py`'s own module shape, and should not be built as a new sibling
   module.** `worldgen.py` exists as a separate module specifically because its algorithm must run
   identically in two places (the SM83 routine and the Python test oracle) — a dual-implementation
   lockstep concern (`GDS-09`'s delta, `ADR-0009`'s own Consequences). Procedural music generation
   under this decision has **no second implementation to keep in sync**: the Python generator runs
   once, at build time, and its output is compiled directly into ROM data exactly as the existing
   hand-authored `SONG` already is. This capability therefore belongs inside `music.py` itself (a
   new build-time function, e.g. `generate_theme_variations(main_theme, identities) -> dict[str,
   SONG]`, called from `build_rom.py` alongside the existing `music_data()` call) — not a new
   sibling module. Using `worldgen.py`'s own module shape here would be copying a solution to a
   problem (dual-implementation lockstep) this capability does not have.
4. **Transform menu: transposition and tempo/duration scaling, combinable, not mutually
   exclusive** (per `R217`'s own note that these needn't be chosen exclusively). Each of the eight
   remaining identities' sub-theme is the main theme's own note sequence, transposed to a
   distinct starting pitch and/or its duration constants (`music.py`'s existing
   `EN`/`QN`/`DQ`/`HN`/`WN` vocabulary) uniformly scaled — both are real-precedented techniques
   (`R217`'s own Sonic Advance 3/Sonic Frontiers citations), both are cheap in ROM terms
   (transposition changes only frequency values, not byte count; duration scaling changes
   duration bytes, not note count — neither transform grows the note count or track structure).
5. **The shared-ostinato-plus-second-channel option is explicitly deferred, not adopted.** `R217`
   itself named this as the one transform option requiring new hardware resource commitment (a
   second APU channel, 3 of 4 currently unused). Adopting it now would be a materially larger
   architectural commitment than this decision's own stated scope — `BL-0127`'s own wording ("a
   main theme... and sub-themes") is satisfied by transposition/tempo variation alone, and nothing
   in the current request requires the richer, costlier ostinato structure. A future revision may
   adopt it; this ADR does not rule it out, only declines to commit to it now (mirroring
   `ADR-0018`'s own precedent for deferring a UI-exposure question rather than deciding it
   unnecessarily).
6. **Sub-theme selection is by the player's current biome-family identity, mirroring the existing
   HUD zone-name-label mechanism's own trigger shape** (`asm_game.py`'s `_score_bar`, which already
   reads and displays a per-region identity every frame) — the main theme plays outside gameplay
   (title/menus) and the matching sub-theme plays during `PLAYING` for whichever of the nine
   identities the current region is. This ADR decides the *shape* of the trigger (identity-keyed,
   not time-keyed or arbitrary), not its exact `GAMESTATE`/WRAM implementation — that is
   `06-feature-specification`'s/`07-implementation-planning`'s own scope, per this skill's own
   SHALL-NOT-invent-implementation-detail rule.
7. **Commits to nine sub-themes, one per `FR-4320`'s own biome-family identity axis** — `FR-4320`
   is already baselined (requirements-committed) even though its own implementation packages
   (`IP-1105`/`IP-1033`/`IP-1022`/`IP-1106`) have not yet shipped or been authorized. This ADR's
   own decision is independent of those packages' own execution status — the *identity set* is a
   settled requirements-level fact, not a moving target, and this ADR is free to build against it
   now. A future `06`/`07` pass for the music capability itself would still need `FR-4320`'s own
   implementation to have shipped before the sub-theme-to-region *binding* can actually work at
   runtime (the binding needs a real, generated `REGION_GRAPH`/`INF_WINDOW` biome-id in the 0-8
   range) — a real, named sequencing dependency for that future work, not a blocker to this
   decision.

## Consequences

- **New build-time capability inside `music.py`**: a generation function producing eight
  transposed/tempo-scaled variations of the existing main theme, called once from `build_rom.py`
  at ROM-build time. No new sibling module (point 3, above) — a smaller footprint than
  `worldgen.py`'s own precedent, and correctly so, per the reasoning above.
- **ROM budget: measured, not assumed.** The existing main theme compiles to 181 bytes
  (`music_data()`, direct measurement). Nine total tracks (main + eight variations) at
  comparable size ≈ 1629 bytes of new data — against the ~2872-byte headroom the last full build
  measured (29896/32768 used), this fits with roughly 1200 bytes to spare, **not** assumed free —
  a future `04`/`07` pass must re-measure against the tree's actual state at that time, since
  other in-flight work (the nine-biome-family widening itself, still unauthorized) will also
  consume some of this same headroom.
- **No new APU channel claimed** (point 5) — `music_tick`'s existing single-channel-1 call
  structure is unaffected by this decision; only the *data* `music.py` compiles grows, not the
  runtime playback mechanism.
- **A new per-region music-selection trigger is implied** (point 6) but not designed here — a
  future `06-feature-specification` pass must decide the exact mechanism (a new WRAM
  `CURRENT_THEME` pointer, a `GAMESTATE`/biome-id-keyed dispatch mirroring `dsr_p_dispatch`'s own
  shape, or something else) against the real code, not invented at this architecture level.
- **Real sequencing dependency, not a blocker**: the eventual music-selection trigger needs
  `FR-4320`'s own implementation (`IP-1105`/`IP-1033`/`IP-1022`/`IP-1106`) to have shipped first,
  since it binds to the same biome-id domain those packages establish. This ADR's own decision
  (transform menu, build-time generation, no new module) does not itself depend on that shipping —
  a future `04-requirements-engineering` pass can derive the real FR from this ADR at any time;
  only the eventual implementation package's own `READY` status will wait on `FR-4320`.
- **Does not itself implement anything** — per this pipeline's rules, an ADR records a binding
  design decision; the actual generation function, its `build_rom.py` integration, and the
  music-selection trigger ship through the normal `04`→`05`→`06`→`07`→`08` path, gated by G3 as
  always.

## Sources
Grounded in [R217](../../research/encyclopedia/R217-procedural-generative-music-composition.md)
(transform menu, build-time-vs-runtime recommendation, channel-budget fact) and, by direct
cross-reference for the module-shape reasoning (point 3), [ADR-0009](ADR-0009-screen-graph-world-generation.md)'s
own Consequences section (the oracle/lockstep discipline this decision confirms does not apply
here).
