# IP-1110 — Procedural Music Generation (Build-Time Sub-Theme Generation)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1110` — implements [**FS-111**](../../features/FS-111-procedural-music-generation.md)
Workflow A (`FEAT-7100`, Epic `EP-7000`) — grounded by `ADR-0019` (build-time theme-and-variation
generation) and `FR-7100` (procedural biome-family sub-theme generation from the main theme).
Planned against commit `7cb452f`.

## 2. Objective

At ROM-build time, generate eight new music sub-themes from the existing shipped 16-bar main
theme (`music.py`'s `SONG`, unchanged) by transposition and/or uniform tempo/duration scaling —
one sub-theme per `FR-4320`'s biome-family identity, nine total selections covering all nine
identities (`FR-7100`'s own Acceptance Criteria: "nine music selections total... not... nine
independently-transformed variations distinct from the main theme itself").

**Resolves `FS-111`'s Open Question 3** (which of the nine identities the main theme's own data
represents, left explicitly open by `FR-7100`'s Description): this package assigns **Grass** as
the zero-transform anchor — the main theme plays unmodified for Grass regions, and every other
identity's sub-theme is a transform of it. This mirrors `generate_world`'s own existing
`(x1,y1)=(0,0) = Grass` anchor precedent (`ADR-0009`), which `FS-111`'s own Open Question 3 named
as a reasoned candidate without deciding. This is a content-mapping choice, not a requirements or
architecture decision — `FR-7100`'s own text is satisfied by either reading, and this choice
carries no downstream algorithm-validity or save-format consequence (unlike `CR-08`'s own
adjacency-grammar stakes), so it is decided here rather than routed upstream, stated explicitly
for anyone to override later rather than silently assumed.

**Scope boundary:** this package is build-time only — no `asm_game.py` change, no runtime
playback-selection logic (that is `IP-1111`'s own scope, `BLOCKED` on this package's own output).

## 3. Requirements Covered

`FR-7100` (in full — this package alone satisfies every one of its Acceptance Criteria); `NFR-4400`
(ROM budget — this package is where the new bytes are added, so its own Verification Checklist
carries the byte-usage measurement).

## 4. Architecture Components

`ADR-0019` (binding decision: build-time Python generation inside `music.py` itself, no new
sibling module, transposition + tempo/duration scaling as the transform mechanism, the
shared-ostinato/second-channel option explicitly deferred). No `GDS-07`/`GDS-09` delta has been
authored for this capability — this package's own Interfaces (§5)/Data Model (implicit in §6) are
the first concrete commitment to an address-table shape, owed to `GDS-09` as a documentation
update (§9), not invented at the architecture level.

## 5. Interfaces

- **`music_data()`'s existing byte-format contract** (`GDS-09`, `music.py`'s `note()`/`freq()`) —
  reused unchanged for each of the nine tracks: `[freq_lo, freq_hi|trigger, duration]` per note,
  terminal `0xFF` loop-back marker. **Binding per `GDS-09`'s own stated contract**: every
  generated sub-theme must end with the same `0xFF` marker `music_tick` depends on.
- **The existing `patches[key]`/`p16()` build-time address-patching pattern** (`GDS-09`, `R302`) —
  extended from the current two-key `mus_lo`/`mus_hi` pair (main theme only) to a nine-entry
  address table, one pair of patch keys per identity (`water_mus_lo`/`water_mus_hi`,
  `sand_mus_lo`/`sand_mus_hi`, `grass_mus_lo`/`grass_mus_hi`, `stone_mus_lo`/`stone_mus_hi`,
  `brick_mus_lo`/`brick_mus_hi`, `village_mus_lo`/`village_mus_hi`, `cave_mus_lo`/`cave_mus_hi`,
  `desert_mus_lo`/`desert_mus_hi`, `plains_mus_lo`/`plains_mus_hi`) — chosen over a flat
  ROM-resident pointer array (`FS-111`'s own second-named candidate, §9/Open Question 5) because
  it mirrors the existing `mus_lo`/`mus_hi` pattern exactly (no new indexing/lookup code needed at
  either producer or consumer side — `IP-1111` reads a named constant per identity, matching how
  `_dsr_family`'s own `water_t`/`water_a`-style keys already work for screen tile/attribute
  addresses). **`grass_mus_lo`/`grass_mus_hi` are patched to the same address as `mus_lo`/`mus_hi`
  themselves** (§2's own Grass-anchor decision — no separate "Grass sub-theme" data is generated;
  it *is* the main theme).
- **No new WRAM interface** — this package is build-time only.

## 6. Files to Create/Modify

- **Modify: `music.py`** — add a new function (e.g. `generate_theme_variations(main_theme,
  transforms) -> dict[str, list]`, per `ADR-0019` point 3's own suggested shape) living alongside
  the existing `SONG`/`music_data()`/`note()`/`freq()` definitions:
  - Accepts `SONG` and a per-identity transform spec (a semitone-shift integer and/or a
    duration-scale factor, one entry per one of the eight non-Grass identities: Water, Sand,
    Stone, Brick, Village, Cave, Desert, Plains).
  - For each identity, produces a new note-tuple list by applying the transform to every
    `(freq, dur)` pair in `SONG`: transposition re-derives `freq` via `freq(hz * 2**(semitones/12))`
    (reusing the existing `freq()` helper, never a hardcoded frequency table); duration scaling
    multiplies each `dur` value by the identity's own scale factor, rounded to the nearest integer
    frame count (`music_tick` operates in whole frames, no fractional-frame duration is
    representable).
  - Returns a `dict` keyed by identity name, each value a `music_data()`-compatible byte list
    (reuses the existing `music_data()`-internal note-encoding logic — either by refactoring
    `music_data()` to accept an arbitrary note-tuple list as a parameter, defaulting to `SONG`, or
    by extracting its per-note encoding loop into a shared helper both call — implementation
    detail for `08-code-implementation` to choose, not fixed here, since either preserves the
    existing single-track `music_data()` call `build_rom.py` already makes).
  - **Concrete initial transform values** (a starting proposal, not binding — `08-code-
    implementation`/`09-content-review` may retune): Water (-5 semitones, tempo ×1.0), Sand (+2,
    ×1.0), Stone (-2, ×0.9 — slower, heavier), Brick (+5, ×1.0), Village (+2, ×1.05 — slightly
    brighter/faster), Cave (-7, ×0.85 — lower and slower), Desert (0, ×0.95), Plains (+4, ×1.0).
    Every value stays within `freq()`'s own representable range (checked against `C4`–`G5`'s
    existing span plus each transposition, confirmed no value drives a note below the SM83 APU's
    usable frequency floor — a build-time assertion, §7 task 4).
- **Modify: `build_rom.py`**:
  - Replace the single `music_addr = rom.pos; for b in music_data(): rom.emit(b)` block
    (`build_rom.py:98`–`99`) with a loop over the nine identities: for Grass, reuse the existing
    `music_data()` call (or `music_data(SONG)` if refactored, §6's own `music.py` note) and record
    its address as both `mus_lo`/`mus_hi`'s target (unchanged patch keys, existing behavior) and
    `grass_mus_lo`/`grass_mus_hi`'s target; for the other eight, call the new generation
    function's own per-identity output through the same byte-encoding path, emit each, and record
    each one's own address.
  - Extend the `p16(patches[key], addr)` patching block (`build_rom.py:139`–`144`) with the eight
    new address pairs, mirroring the existing `mus_lo`/`mus_hi` two-line pattern exactly.
- **No change to `asm_game.py`** — `IP-1111`'s own scope.

## 7. Implementation Tasks

Ordered: (1) confirm every cited line number against the current tree by direct re-read (drift is
Blocking); (2) implement `music.py`'s new generation function, including the Grass-anchor special
case (§2); (3) implement the transform math (transposition via `freq()`, duration scaling with
integer rounding), using the concrete starting values in §6; (4) add a build-time assertion that
every generated frequency falls within `freq()`'s own representable range (no note silently
clipped or wrapped); (5) update `build_rom.py`'s emission loop and patch-table extension; (6) run
`python3 build_rom.py` and confirm the total byte count against `NFR-4400`'s own budget (§11); (7)
write the build-time comparison check (§8) confirming each non-Grass sub-theme's data is a pure
transform of `SONG`'s own data; (8) full `test_rom.py` suite run (no existing check should be
affected — this package adds ROM data, touches no existing code path); (9) documentation updates
(§9).

## 8. Tests to Add

New build-time check (not a `test_rom.py` runtime check — a direct Python-level comparison,
mirroring `worldgen.py`'s own oracle-comparison precedent in spirit, per `FR-7100`'s own
Verification Method): for each of the eight non-Grass identities, recompute the expected
transform from `SONG` and the identity's own transform spec, and assert the generated sub-theme's
note sequence matches exactly (frequency and duration, per-note). Confirms `FR-7100`'s Acceptance
Criteria directly: "derivable from the main theme's own via transposition and/or duration scaling
alone." Landed as a new standalone script (mirroring how `music_data()`'s own byte count was
directly measured earlier this session via `python3 -c "from music import music_data;
print(len(music_data()))"`) or a new `test_rom.py` suite section if `08-code-implementation`
judges the existing harness a better fit — not fixed here.

## 9. Documentation Updates

- `docs/architecture/09-interface-specification.md`: new entry for the generation function's own
  contract (`generate_theme_variations(main_theme, transforms) -> dict[str, list]` or whatever
  exact signature implementation settles on), mirroring `music_data()`'s own existing entry
  (§61 of that document) — cites the terminal-`0xFF`-marker contract this new function must also
  honor.
- `docs/architecture/07-data-model.md`: new entry naming the nine `*_mus_lo`/`*_mus_hi` patch-key
  pairs and their ROM section (alongside the existing music-data section note), dated and citing
  this package and `FR-7100`.
- `docs/requirements/01-functional-requirements.md`: `FR-7100`'s own Notes gains a line marking it
  Implemented once this package ships, citing `IP-1110` and the concrete Grass-anchor decision.
- Master Build Plan status row; `packages/INDEX.md`; `FS-111`'s own forward-reference metadata
  (Open Question 3 resolved).

## 10. Definition of Done

- The built ROM contains nine distinct, playable music data sequences, one per biome-family
  identity, each following the existing `music_data()` byte-format contract (terminal `0xFF`
  included).
- Every non-Grass sequence's note data is confirmed, by the build-time comparison check (§8), to
  be a pure transform (transposition and/or duration scaling) of `SONG`'s own data — no
  independently-composed melodic material.
- The Grass sequence is byte-identical to the existing main theme's own `music_data()` output.
- `build_rom.py`'s new nine-entry patch table is correctly wired — confirmed by direct read of the
  built ROM's patched addresses against `rom.pos` at each emission point.
- Existing single-track playback (`music_tick`, `mus_lo`/`mus_hi`) is completely unaffected —
  confirmed by the full `test_rom.py` suite passing with zero expected-value changes (this package
  adds data, touches no existing code).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, zero expected-value changes in any existing check.
- [ ] Build-time comparison check (§8): all eight non-Grass sub-themes confirmed as pure
      transforms of `SONG`.
- [ ] Direct ROM-byte-usage measurement: total used bytes recorded and compared against
      `NFR-4400`'s own ~2872-byte headroom figure (last confirmed 29896/32768 at this package's
      own planning time, 2026-07-16 — **must be re-measured against the tree's actual state at
      implementation time**, since `IP-1022`/`IP-1033`/`IP-1105`/`IP-1106` may land first and
      consume some of the same headroom).
- [ ] Direct diff: `asm_game.py` byte-for-byte unchanged (this package touches only `music.py`/
      `build_rom.py`).
- [ ] Every generated frequency confirmed within `freq()`'s own representable range (no clipped/
      wrapped note).

## 12. Dependencies

- **`FR-7100`** (baselined) — the requirement this package implements in full.
- **`FR-4320`** (baselined, **not yet implemented** — `IP-1105`/`IP-1033`/`IP-1022`/`IP-1106`, all
  `NOT STARTED`/`BLOCKED`) — this package depends only on `FR-4320`'s own *identity set* being a
  settled requirements-level fact (it is, per `ADR-0019` point 7), **not** on any of those four
  packages shipping — this package generates data for all nine identities regardless of whether
  the runtime dispatch cascade can yet reach all nine (`IP-1111`'s own concern, not this one's).
- No other in-flight package's Files to Modify overlap this one's own (`music.py`/`build_rom.py`
  are untouched by every currently-planned arc-(3) package).

## 13. Risks

Low — a self-contained, build-time-only data-generation task with no runtime code, no WRAM
change, and no interaction with any in-flight or unauthorized package's own files. The one
named risk: the **concrete transform values in §6 are a starting proposal**, not validated against
`09-content-review`'s own Audio Correctness dimension — a future content review may recommend
retuning them (e.g. if a transposition reads as musically unpleasant), which would be a
low-cost, data-only change (no structural rework), tracked as a follow-on finding rather than a
blocker to this package's own completion.

## 14. Rollback Considerations

Revert `music.py`'s new generation function and `build_rom.py`'s emission-loop/patch-table
changes, restoring the single `music_addr = rom.pos; for b in music_data(): rom.emit(b)` block and
the two-key `mus_lo`/`mus_hi` patch pair, then rebuild. No WRAM/SRAM footprint, no save-format
dependency — pure ROM-data addition, cleanly reversible.
