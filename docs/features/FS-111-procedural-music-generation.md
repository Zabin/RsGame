# FS-111 — Procedural Music Generation

> Feature Specification for [FEAT-7100](../feature-planning/03-feature-catalog.md#feat-7100--procedural-music-generation-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-7100, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Planned 2026-07-16** (`07-implementation-planning`) — two packages,
> [IP-1110](../implementation/packages/IP-1110-procedural-music-generation.md) (build-time
> generation) and
> [IP-1111](../implementation/packages/IP-1111-biome-family-sub-theme-playback-selection.md)
> (runtime selection, `BLOCKED` on `IP-1022`). **Both authorized (G3, user "Build all six,"
> 2026-07-16).** Open Question 3 (which identity the main theme represents) resolved by `IP-1110`'s
> own planning: Grass, mirroring `generate_world`'s `(0,0)=Grass` precedent. Open Question 1
> (selection-mechanism shape) resolved by `IP-1111`'s own planning: hooks `do_screen_redraw`'s
> per-state dispatch and `dsr_p_dispatch`'s per-identity cascade — no new WRAM poll. Open
> Question 4 (the `ADR-0019` citation-precision note) confirmed accurate — `dsr_p_dispatch` is
> indeed the mechanism used, not the `_score_bar` shape. Open Question 2 (two-source sequencing)
> addressed in the packages above. **Open Question 5 (address-table shape) resolved differently
> than originally planned, during `IP-1110`'s own implementation (2026-07-16):** the originally-
> planned per-identity named-patch-key scheme (mirroring `mus_lo`/`mus_hi`) turned out to require
> `asm_game.py` changes contradicting `IP-1110`'s own no-`asm_game.py` scope boundary — a genuine
> planning inconsistency, resolved using this same planning pass's own already-named fallback
> option instead: a flat, biome-id-indexed ROM address table (`music_table`, mirroring `zc_table`'s
> own precedent). `IP-1111`'s own §5/§6 (not yet executed) will need a `07-implementation-planning`
> touch to consume this table correctly before it runs.
> **A real technical finding this planning pass surfaced, not in this spec's own §7/§13**:
> `music_tick`'s loop-restart branch is hardcoded to the main theme's own ROM address, not
> track-agnostic — `IP-1111` adds a fix (new `MUSIC_BASE_LO`/`MUSIC_BASE_HI` WRAM field).
> **`IP-1110` implemented 2026-07-16 — `COMPLETE`**: `music.py`'s `generate_theme_variations()`
> ships all eight non-Grass sub-themes, confirmed as pure transforms of the main theme by a new
> build-time comparison check (`verify_music_generation.py`); `NFR-4400` (ROM budget) now **Met**,
> measured directly (31362/32768 bytes, 1466 net new). This Feature sits in the `Future` release
> bucket (no release commitment made); planning/implementation does not require or imply
> scheduling, per `05-feature-decomposition`'s own established precedent (`FS-110`'s own identical
> framing).

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-111` — expands `FEAT-7100` (Procedural Music Generation), Epic `EP-7000` (Procedural Music
Generation).

## 2. Title

Procedural Music Generation

## 3. Purpose

Give each biome-family identity its own musical character without hand-authoring nine separate
tracks or committing a second APU channel — generate the variation algorithmically from the
game's existing, shipped main theme. Carried forward verbatim from FEAT-7100's own Purpose/User
Value (Medium — atmospheric enrichment, project-owner-requested via `BL-0127`, not tied to any
`MSTR-001` commitment).

## 4. Scope

**In scope:** the build-time generation algorithm (transposition and/or tempo/duration scaling,
combinable, per `ADR-0019` point 4) producing nine sub-themes — one per `FR-4320`'s biome-family
identity — from the existing shipped 16-bar `SONG`; the runtime selection mechanism determining
which track plays when (the matching sub-theme during `PLAYING`, the main theme otherwise).

**Out of scope** (per FEAT-7100's own Excluded Requirements, carried forward verbatim):
`FR-4310`/`FR-4320` themselves (the biome-family identity axis — generation-time,
`FEAT-9000`'s own concern; this Feature is a consumer, not an owner, of that data); composing
genuinely new melodic material (transform-only, per `ADR-0019` point 4 — not composition); the
shared-ostinato/second-APU-channel option (`ADR-0019` point 5 explicitly defers it, not adopted);
a new sibling Python module mirroring `worldgen.py`'s shape (`ADR-0019` point 3's own explicit
rejection — no runtime/oracle-lockstep need exists here).

**Scope note carried from FEAT-7100's own catalog entry:** this Feature is deliberately kept as
one cohesive unit (build-time generation plus runtime selection) rather than pre-split, since the
two halves are tightly coupled (the selection mechanism only has meaning once the generated
sub-themes exist) — mirroring how `FEAT-9000`/`FEAT-10000` each started unsplit before any split
was warranted.

## 5. Requirements Implemented

FR-7100, FR-7110; NFR-4400 — the exact set FEAT-7100 owns, no more, no fewer (cross-checked
against [03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-7100--procedural-music-generation-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — Build-time sub-theme generation** (FR-7100):

1. At ROM-build time, `build_rom.py` calls a new generation function (prospective — no code exists
   yet), passing it the existing main theme's note sequence (`music.py`'s `SONG`) and `FR-4320`'s
   nine-identity set.
2. For each of the nine biome-family identities, the function derives that identity's sub-theme
   by transposing the main theme's note sequence to a distinct starting pitch and/or uniformly
   scaling its duration constants (`EN`/`QN`/`DQ`/`HN`/`WN`) — never composing independent
   melodic material (FR-7100's own Acceptance Criteria).
3. The main theme's own identity is one of the nine (`FR-7100`'s Description states this
   explicitly, without deciding *which* identity — see Open Question 3): either the main theme is
   reused directly as that identity's own sub-theme, or it is the anchor every other sub-theme
   transforms from. Either way, nine total playable selections exist, covering all nine
   identities.
4. Each generated sub-theme is compiled to ROM data using the existing `music_data()` byte format
   (`note()`/`freq()`, terminal `0xFF` loop-back marker per `GDS-09`'s own confirmed interface
   contract) and emitted into the ROM image, mirroring the existing single-track emission
   (`build_rom.py`'s current `music_addr = rom.pos; for b in music_data(): rom.emit(b)` pattern,
   extended to nine tracks).

**Workflow B — Runtime sub-theme selection during play** (FR-7110):

1. While in `PLAYING` (either mode — finite or Infinite, both of which share the same
   biome-family identity axis per `FR-4320`), the system determines the player's current region's
   biome-family identity — the identical value the existing screen-dispatch mechanism already
   reads (finite mode: `REGION_GRAPH`'s biome-id byte via `CUR_ZONE`; Infinite Mode: `INF_WINDOW`'s
   center-cell biome-id) — not a new read (FR-7110's own Inputs).
2. The music track currently playing is switched to the sub-theme matching that identity, within
   one frame of the region becoming current (FR-7110's own Acceptance Criteria). The exact
   mechanism producing this switch — whether it piggybacks on the existing screen-dispatch cascade
   (`dsr_p_dispatch`) or is a separate check — is not decided by this specification (Open
   Question 1).
3. Outside `PLAYING` (title, menus, and other non-gameplay states), the main theme plays.

## 7. System Behaviour

**Normal path (generation):** given the main theme's fixed note sequence and the nine-identity
set, the generation function deterministically produces nine sub-themes, each a pure transform
(transposition and/or duration scaling) of the main theme's own data — no randomness, no
build-to-build variation (an implicit requirement of FR-7100's own Acceptance Criteria's
"derivable... via transposition and/or duration scaling alone" wording, though not itself a
named NFR).

**Normal path (selection):** given a `PLAYING` state and a current region's biome-family identity
in the `0`–`8` range, the correct one of nine sub-themes plays.

**Edge case — biome-family identities 5–8 are not yet reachable in the shipped game:**
`FR-4320`'s own implementation (`IP-1105`/`IP-1033`/`IP-1022`/`IP-1106`) has not shipped —
`generate_world`'s clamp and `dsr_p_dispatch`'s cascade both still only produce/handle values
`0`–`4` today. This Feature's own selection mechanism for identities `5`–`8` therefore has no
live code path to exercise until that separate arc ships — not a defect in this specification,
but a real implementation-order fact worth stating plainly (mirrors the two-source sequencing
dependency named in §17/§18).

**Edge case — transitioning between `PLAYING` and a non-`PLAYING` state:** the main theme must
resume; FR-7110's own Postconditions state the track playing must "always match the player's
current context," which implies this transition is symmetric with entering `PLAYING` (Workflow B
step 2) — not separately specified by FR-7110's own text beyond that general postcondition.

**Edge case — re-entering a region of the same biome-family identity the player just left (no
identity change):** no observable behavior change implied — FR-7110's Acceptance Criteria is
phrased as "entering a region of that identity... results in that identity's own sub-theme
playing," not "re-triggers playback from the start of the track." Whether re-entering the same
identity restarts the sub-theme from bar 1 or leaves an already-playing track uninterrupted is not
decided by FR-7100/FR-7110's own text (Open Question 1's own mechanism choice determines this as
a side effect, not decided independently here).

**Edge case — the main theme's own identity assignment (which of the nine it represents):** not
decided (Open Question 3) — genuinely open, not merely unstated implementation detail, since it
affects which of the nine `PLAYING`-time selections plays the *unmodified* main theme data versus
which nine distinct byte sequences must actually be authored/compiled.

## 8. Module Responsibilities

Per `GDS-03`'s module decomposition, extended by `ADR-0019` point 3's own explicit no-new-module
framing:

- **`music.py`** — the new build-time generation function (prospective, e.g.
  `generate_theme_variations(main_theme, identities) -> dict[str, SONG]`, per `ADR-0019` point 3's
  own suggested shape) living alongside the existing `SONG`/`music_data()`/`note()`/`freq()`
  definitions. No code exists yet.
- **`build_rom.py`** — the call site invoking the new generation function (mirroring the existing
  `music_addr = rom.pos; for b in music_data(): rom.emit(b)` call, extended to emit nine tracks
  and record nine addresses), and the patch-table extension recording where each generated
  track's data begins in ROM (extending the existing `mus_lo`/`mus_hi` two-key pattern to nine
  tracks' worth of addresses — exact shape not decided, Open Question 5).
- **`asm_game.py`** (prospective) — the runtime selection mechanism (Workflow B step 2); no code
  exists yet. **This Feature does not itself own or redesign `dsr_p`/`dsr_p_dispatch`** (the
  existing biome-family screen-composition dispatch, `FEAT-4100`'s own deliverable) — it may reuse
  that mechanism's own per-identity branch structure as a natural hook point (see §9), but whether
  it actually extends that cascade or adds an independent check is Open Question 1, not decided
  here.

No module outside this set is touched. Explicitly **not** a new sibling module (`ADR-0019`
point 3) — `worldgen.py`'s own module shape does not apply, since there is no runtime/Python-oracle
lockstep discipline this capability needs (the generator runs once, at build time; its output is
static ROM data).

## 9. Interfaces Used

- **`music_data()`'s existing byte-format contract** (`GDS-09`, confirmed by direct interface
  read): `note()`/`freq()`'s `[freq_lo, freq_hi|trigger, duration]` encoding, and — **binding on
  any future multi-track extension per `GDS-09`'s own stated contract** — the terminal `0xFF`
  loop-back marker convention `music_tick` depends on to detect end-of-song. Each of the nine
  generated sub-themes must preserve this convention; a track omitting it would silently corrupt
  playback (undefined behavior, not merely a spec violation) rather than fail loudly.
- **The existing `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/`MUSIC_CTR` WRAM playback-state fields** (`0xC00F`–
  `0xC011`, `GDS-07` §data-model, unchanged by this Feature's own read) — `music_tick` reads these
  every frame regardless of which track they currently point to; today they are written exactly
  once, at boot. A runtime track-switch (Workflow B step 2) necessarily means re-writing
  `MUSIC_PTR_LO`/`MUSIC_PTR_HI` (and plausibly resetting `MUSIC_CTR`) at the moment the selection
  changes — the *existing* fields are reused, no new WRAM playback-state field is implied by this
  alone.
- **The `patches[key]`/`p16()` build-time address-patching pattern** (`GDS-09`, `R302`) — the
  existing `mus_lo`/`mus_hi` two-key pattern is the direct precedent for however this Feature's
  own nine-track address table is patched; `build_rom.py`'s existing `zc_table`-style
  pointer-array pattern (a build-time list of 16-bit addresses, one per identity, mirroring
  `ZONE_COLLECTS`'s own per-zone table-of-pointers shape) is a second, structurally close existing
  precedent worth naming for whoever designs the exact table shape (Open Question 5) — neither is
  selected here.
- **`dsr_p`/`dsr_p_dispatch`'s existing per-identity screen-selection cascade** (`asm_game.py`,
  `FEAT-4100`'s own deliverable) — cited by `ADR-0019`'s own Consequences section as one candidate
  shape ("a `GAMESTATE`/biome-id-keyed dispatch mirroring `dsr_p_dispatch`'s own shape") for this
  Feature's eventual selection trigger. **Correction to a citation in `ADR-0019`'s own Decision
  section, not a change to its binding decision:** point 6 also cites "the existing HUD
  zone-name-label mechanism... which already reads and displays a per-region identity every
  frame" (`asm_game.py`'s `_score_bar`) as precedent — direct inspection for this specification
  found `_score_bar` is actually defined in `tilemaps.py`, not `asm_game.py`, and it bakes each
  screen's zone-name text into that screen's own static tile data at **build time**, not a
  continuous per-frame WRAM poll at runtime. The freshness this mechanism appears to have comes
  from `dsr_p_dispatch` selecting a different pre-drawn screen (with its own baked-in label) at
  region-transition time — not from any runtime re-read. This does not change `ADR-0019`'s own
  binding decision (identity-keyed selection, not time-keyed) but means the real, closest runtime
  precedent available to `07-implementation-planning` is `dsr_p`/`dsr_p_dispatch`'s own
  region-transition-time firing, not a "poll every frame" pattern — flagged here rather than
  silently carried forward as fact (Open Question 4).

## 10. Data Model Changes

**No `GDS-07` delta has been authored for this Feature** — mirroring `FS-110`'s own precedent, this
specification names the conceptual data additions `ADR-0019`'s own Consequences section implies,
without committing to exact addresses (that remains `07-implementation-planning`'s scope, per
`GDS-07`'s own ownership of concrete byte layouts):

- **Nine music-track byte sequences** (ROM, read-only) — the main theme's existing data plus eight
  new generated sequences, replacing the single `music_addr` emission with nine, each following
  the existing `music_data()` byte-format contract (§9).
- **A nine-entry track-address table** (ROM, read-only) — conceptually parallel to the existing
  `zc_table`/`screen_addrs` pattern (§9), giving the runtime selection mechanism a way to look up
  which ROM address holds a given identity's track. Exact shape (a flat 18-byte pointer array
  indexed by identity, nine separate named patch keys mirroring `mus_lo`/`mus_hi`, or another
  encoding) is Open Question 5.
- **No new WRAM field is implied by generation itself** — `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/
  `MUSIC_CTR` (existing, §9) are reused for playback regardless of which track is selected. Whether
  the *selection* mechanism itself needs a new WRAM field (e.g. a "last-known biome-family
  identity" byte, to detect an identity change without re-deriving it from scratch every check) is
  part of Open Question 1, not decided here.
- **No SRAM addition** — this Feature has no save-data footprint; the biome-family identity it
  reads is already persisted (or re-derived) by `FR-4310`/`FR-4320`'s own existing/prospective
  mechanisms, unchanged by this Feature.

## 11. State Changes

- **No new `GameState` value is introduced.** This Feature changes *what plays* during the
  existing `PLAYING` state (and the existing non-`PLAYING` states) — it does not add, remove, or
  gate any state-machine node (`FEAT-1000`, unmodified).
- **Runtime state created (prospective, exact shape Open Question 1):** whatever tracking the
  selection mechanism needs to detect "the current region's identity changed since the last
  check" — if the chosen mechanism is a re-derivation on every `dsr_p_dispatch` firing (a
  region-transition event), no persistent "last identity" state is needed at all; if it is a
  separate per-frame poll, a comparison value would be.

## 12. Error Handling

- **A biome-family identity outside the reachable `0`–`4` range today (i.e. `5`–`8`, pending
  `FR-4320`'s own implementation):** not a runtime failure mode this Feature must defensively
  handle — those values are simply unreachable in the shipped game until `FR-4320`'s own packages
  ship, at which point this Feature's own selection mechanism must already cover the full `0`–`8`
  range by construction (FR-7100's own nine-sub-theme output), not by a fallback/error path.
- **A build where fewer than nine sub-themes were successfully generated:** out of this
  specification's own scope to define a runtime contract for — FR-7100's own Acceptance Criteria
  is a build-time check (Verification Method: Test, direct comparison against the main theme),
  meaning a build with missing sub-themes should fail the build, not ship with an undefined
  runtime fallback. Not yet a concrete build-time assertion (no code exists to write one against).
- **Main-theme identity ambiguity (Open Question 3) reaching implementation unresolved:** would be
  a genuine implementation blocker, not a runtime error — `07-implementation-planning` cannot
  author a complete package without this question answered first.

## 13. Performance Considerations

- **NFR-4400** (ROM budget, sizing estimated, not yet confirmed): nine tracks at a size comparable
  to the existing 181-byte main theme (`ADR-0019`'s own Consequences: ≈1629 bytes of new data)
  against the ~2872-byte headroom the last full build measured — fits with roughly 1200 bytes to
  spare, **but this specification does not re-measure it**; NFR-4400's own Status field already
  states this must be re-measured against the tree's actual state at implementation time, since
  other in-flight, unauthorized work (`FR-4320`'s own four packages) will also consume some of the
  same headroom before this Feature ships.
- **`music_tick`'s own per-frame CPU cost is unaffected in structure** — its read-and-advance
  logic is unchanged regardless of which track `MUSIC_PTR_LO`/`MUSIC_PTR_HI` currently point to;
  only the *data* size grows, not the runtime routine's own instruction count or VBlank-timing
  profile. No NFR governs this specifically; stated here as a reviewed, not merely assumed,
  non-risk.
- **The selection mechanism's own per-region-transition (or per-frame, depending on Open
  Question 1's resolution) cost** is not sized here — whichever shape `07-implementation-planning`
  chooses inherits whatever timing budget its host routine already operates under (e.g.
  `dsr_p_dispatch`'s own existing screen-transition budget, if that mechanism is reused).

## 14. Integrity Considerations

None specific to this Feature. It has no save-data footprint (§10/§11) and introduces no new
determinism requirement — the generation function's own output is fixed at build time (no
per-build randomness per FR-7100's own transform-only Acceptance Criteria), and the runtime
selection reads an already-established, already-governed biome-family identity value
(`FR-4310`/`FR-4320`'s own integrity guarantees, unchanged and un-owned by this Feature).

## 15. Acceptance Criteria

1. For each of the nine biome-family identities, the built ROM contains a distinct, playable
   music data sequence (FR-7100).
2. Every non-main-theme sequence's note sequence is derivable from the main theme's own via
   transposition and/or duration scaling alone — checkable by direct comparison of frequency/
   duration values, confirming a pure transform relationship, no independently-composed melodic
   material (FR-7100).
3. For each of the nine biome-family identities, entering a region of that identity during
   `PLAYING` (either mode) results in that identity's own sub-theme playing, within one frame of
   the region becoming current (FR-7110).
4. Entering any non-`PLAYING` state results in the main theme playing (FR-7110).
5. After the nine sub-themes are compiled into the ROM, the built ROM remains exactly 32768 bytes,
   with the new data fitting inside whatever headroom remains at implementation time (NFR-4400).
6. **Not yet fully checkable for identities 5–8** — those values have no live code path until
   `FR-4320`'s own implementation ships (§7); this specification names the bar without asserting
   end-to-end compliance across the full nine-identity range today.

## 16. Verification Plan

Per FR-7100/FR-7110's own Verification Methods (Test) and NFR-4400 (Inspection) — no `test_rom.py`
suite exists yet for this Feature (no code exists to test):

- **Generation correctness (AC-1/AC-2):** a build-time, unit-test-style check comparing each
  generated sequence's frequency/duration data against the main theme's own, confirming a pure
  transform relationship — mirroring `worldgen.py`'s own oracle-comparison precedent in spirit,
  though (per `ADR-0019` point 3) this Feature's own generation has no separate runtime routine to
  compare against, only a single build-time function to check directly.
- **Playback selection (AC-3/AC-4):** drive each of the nine identities via direct force,
  mirroring this session's own established direct-force verification pattern for biome-family
  dispatch (used earlier this session for the maze-blocked edge-indicator content review), and
  confirm the correct track is selected. **Identities 5–8 cannot be exercised until `FR-4320`'s
  own implementation ships** (§7/§15 AC-6) — this half of the plan is only fully executable once
  that separate arc lands.
- **ROM budget (AC-5):** Inspection — direct ROM-byte-usage measurement at implementation time,
  mirroring `NFR-4200`/`NFR-4300`'s own precedent.

**Corpus:** not yet defined — depends on Open Question 1's resolution (the selection mechanism
shape determines what a test actually drives) and Open Question 3 (the main theme's own identity
assignment, which determines whether nine or eight sequences need independent generation-time
verification).

## 17. Dependencies

Per FEAT-7100's own Dependencies (carried forward verbatim): FEAT-9000 (Procedural World
Generation — supplies the finite-mode biome-family identity this Feature's playback selection
reads); FEAT-10000 (Infinite Mode — supplies the same identity for a materialized region; FR-7110
names no mode restriction, so both sources apply); FEAT-1000 (Game State Machine — gates when
sub-theme playback is active, `PLAYING`, versus when the main theme plays instead).

**Real, two-source sequencing dependency, not a blocker to this specification's own authoring**
(named explicitly in [FP-04](../feature-planning/04-feature-dependency-graph.md)'s critical-path
analysis and [FP-05](../feature-planning/05-feature-review.md) finding #11, carried forward here):
this Feature's own full end-to-end verification against all nine biome-family identities cannot
happen until (a) `FR-4320`'s own four implementation packages (`IP-1105`/`IP-1033`/`IP-1022`/
`IP-1106`, gated on G3, `BL-0128`) ship, and, separately, (b) `FEAT-10000` is release-scheduled if
Infinite Mode's own playback path is to be verified too (currently `Future`, no commitment). This
Feature's own build-time generation half (Workflow A) has no such blocker.

## 18. Risks

Carried forward from FEAT-7100's own Risk assessment (Medium): the real, named sequencing
dependency above (playback selection needs `FR-4320`'s own packages shipped to have all nine
identities to key against); ROM budget grounded in direct measurement but explicitly not yet
re-confirmed against the tree's actual state at implementation time (NFR-4400's own Notes).

**Additional risk surfaced by this specification, not named at the Feature-catalog level:** the
main theme's own identity assignment (Open Question 3) is a genuine, unresolved design question
this specification found while drafting Workflow A — FR-7100's own Description explicitly leaves
it open ("either directly reused... or the anchor every other sub-theme derives from") rather than
deciding it, meaning `07-implementation-planning` cannot author a complete package for Workflow A
without it being answered first. This is a real gap in implementation-readiness, not a defect in
this specification's own rigor (mirroring `FS-110`'s own §18 precedent for naming this kind of
gap plainly rather than inventing an answer to fill it).

## 19. Open Questions

1. **The exact `GAMESTATE`/WRAM selection mechanism is not decided** (`ADR-0019` point 6, `FR-7110`
   Notes both defer it explicitly). Two reasoned candidates this specification surfaces without
   asserting either as decided: (a) extend `dsr_p_dispatch`'s own per-identity branch structure to
   also repoint `MUSIC_PTR_LO`/`MUSIC_PTR_HI` at the matching track's address, firing naturally at
   the same region-transition moment the screen itself is redrawn (no new trigger event, reuses an
   existing one); (b) a separate check elsewhere in the main game loop, comparing a newly-added
   "last-known identity" WRAM byte against the current one, only repointing on a detected change.
   Option (a) requires no new WRAM state (§10/§11); option (b) does. Resolves at:
   `07-implementation-planning`.
2. **Real two-source sequencing dependency** (see §17) — `FR-4320`'s own four implementation
   packages (gated on G3) and, separately, `FEAT-10000`'s own release scheduling — both bear on
   when this Feature's playback half can be fully verified. Not resolved here; carried forward
   from [FP-04](../feature-planning/04-feature-dependency-graph.md)/[FP-05](../feature-planning/05-feature-review.md)
   finding #11 verbatim, not newly invented.
3. **Which of the nine biome-family identities the main theme's own data represents is not
   decided.** `FR-7100`'s own Description states only that "the main theme's own identity is one
   of the nine," without naming which — a genuine, unresolved design choice with real
   implementation consequences (§18): it determines whether eight or nine distinct sequences must
   actually be generated, and which identity's `PLAYING`-time selection plays byte-identical data
   to the title-screen/menu track. A reasoned candidate this specification surfaces but does not
   assert as decided: `generate_world`'s own existing fixed `(0,0) = Grass` anchor precedent
   (`ADR-0009`) makes "Grass" a natural default, but nothing in `ADR-0019`/`FR-7100` commits to
   it. Resolves at: `07-implementation-planning`, or a direct user/design decision if judged
   significant enough to warrant one.
4. **A citation-precision note on `ADR-0019` point 6, not a change to its binding decision** (see
   §9): the ADR's own cited precedent for "reads and displays a per-region identity every frame"
   (`asm_game.py`'s `_score_bar`) does not match direct inspection — `_score_bar` lives in
   `tilemaps.py` and bakes zone-name text into each screen's static tile data at build time, not a
   continuous runtime poll. The real, closest available runtime precedent is `dsr_p`/
   `dsr_p_dispatch`'s own region-transition-time firing (already separately cited in `ADR-0019`'s
   own Consequences section as an alternative shape) — this specification treats that as the more
   accurate mechanism-design starting point for Open Question 1, without asserting `ADR-0019`
   itself needs correction (ADRs are append-only; a future ADR could supersede this point if judged
   worth formalizing). Not blocking — informational for whoever designs Open Question 1's
   mechanism.
5. **The exact shape of the nine-track ROM address table is not decided** (§9/§10) — a flat
   pointer array (mirroring `zc_table`), nine separate named patch keys (mirroring `mus_lo`/
   `mus_hi` extended ninefold), or another encoding. A build-side design choice with no
   player-visible consequence, deferred to `07-implementation-planning`.

## 20. Related ADRs

ADR-0019 (procedural music generation architecture: build-time theme-and-variation, transposition
+ tempo scaling, no new APU channel).
