# R217 — Procedural/Generative Music Composition: Main Theme + Biome Sub-Themes

- **Document ID:** R217 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R207 (GB-era chiptune composition conventions this topic extends into
  procedural/generative territory), R108 (APU channel/register facts), R213 (this project's own
  procedural-generation precedent, `worldgen.py`, whose build-time/runtime split this topic
  mirrors for music)
- **Referenced By:** `BL-0127` (the project-owner feature request this topic grounds — "procgen
  the music with a main theme for the game and sub-themes based on zone")
- **Produces:** grounding for a future `03-architecture-design-synthesis`/`04-requirements-
  engineering` pass deciding how procedural music generation fits this project's architecture
- **Feature Mapping:** *(none yet — no `FS-xxx` authored; this grounds future stage 04/06 work)*
- **Related Topics:** R207, R108, R213, R212 (delta, the sibling nine-identity axis this topic's
  own sub-theme count target reuses)

## Purpose

Filed to ground `BL-0127`: a main theme for the game plus per-biome-identity sub-themes,
generated procedurally rather than each hand-authored independently. Answers three questions: (1)
what makes a main-theme-plus-variations structure read as *one coherent musical identity* rather
than N unrelated songs; (2) what procedural/algorithmic composition techniques are real,
precedented, and appropriate for this hardware's own constraints; (3) concretely, how would either
approach fit `music.py`'s current architecture and this project's own established procgen
precedent (`worldgen.py`).

## Scope

(a) Theme-and-variation / motif-based composition technique for a main-theme-plus-sub-themes
structure specifically — not general chiptune composition (R207 already owns that) and not APU
hardware facts (R108 already owns those). (b) Procedural/algorithmic music generation techniques
feasible under this hardware's real constraints (build-time Python generation vs. genuine runtime
SM83 generation). (c) A concrete mapping from `FR-4320`'s nine biome-family identities (the
existing shipped five plus the four newly-folded-in ones — `BL-0128`) to a plausible sub-theme
count/structure. Out of scope: the exact notes/rhythms of any specific theme (a content-authoring
craft decision, `08-content-authoring`'s own future scope) and whether/when this capability is
actually built (a requirements/scheduling decision, `04`/`00-pipeline-manager`'s own scope).

## Concepts

**A recurring, recognizable musical idea reused and varied across contexts — a leitmotif — is
the standard technique for making N related pieces read as one musical identity rather than N
unrelated songs.** "A leitmotif is a short, recurring and recognizable musical phrase associated
with a person, place, or idea," appearing "in the hero's theme, the overworld music... before
being reused in different contexts over and over."[^1] This is precisely the shape a
"main theme + sub-themes" structure needs: sub-themes are not independent compositions that
happen to ship together, they are the *same underlying material*, developed differently per
context.

**Two real, opposite-poled precedents exist for how "regional variation" can work, and this
project already leans toward one of them.** Zelda's overworld theme "has experienced numerous
musical variations from game to game... a variation on the main theme for different parts of
Hyrule."[^2] Pokémon Red/Blue took the opposite approach: "distinct, standalone themes for each
[Kanto] location rather than... the variation technique... Zelda did," sharing only "a similar,
up-beat feel" and tonality, not a literal shared melody.[^2] **`BL-0127`'s own wording — "a main
theme... and sub-themes based on zone" — reads as the Zelda-style variation model, not the
Pokémon-style independent-themes model**: a main theme that gets locally re-dressed, not N
unrelated tracks. This is also the cheaper, more ROM-efficient reading (shared melodic material
compresses better than N fully independent compositions) and the one `R207`'s own Implementation
Guidance already anticipated ("a future per-zone or per-context music change... flag it for
GDS-01/GDS-08 rather than assuming one track suffices indefinitely").

**Concrete variation techniques, precedented across multiple shipped titles, not invented here:**
transposition (shifting the same melody to a different key/register), tempo change, and
re-instrumentation-adjacent techniques are the standard toolkit — "composers... keep listeners'
attention by using and reusing musical ideas in different variations, instrumentations,
harmonies, and transpositions."[^3] Concretely regional: in *Sonic Advance 3*, "each stage theme
had... one variation for its map screen plus one for each of the three acts, with the map's theme
more low-key... then each act progressively more intense"[^4] — a single melodic seed, several
intensity-graded arrangements. In *Sonic Frontiers*, "the theme on Kronos Island begins very slow
and as you progress begins to speed up and change... 7 variations just for the first
Island"[^4] — tempo/register drift as the *entire* variation mechanism for one location. In
*UNDERTALE*, "an Overworld Ostinato works its way through many of the 'background' tracks as the
repeating musical pattern over which the main melodies of each area are written"[^4] — a shared
*accompaniment* figure under different area-specific top melodies, a lighter-weight variation
mode than full melodic transposition.

**Procedural/algorithmic generation of the *variations themselves* (not just hand-authoring N
variations) is a real, precedented technique, with real, documented limitations.** Markov-chain-
based generation is "increasingly popular... over the past sixty years," generating "tempo, pitch
range, note values, chord type dominance, and melody notes" from a probability model built from
existing material.[^5] The well-documented failure mode: "a main problem of Markov models... is
that the next state only depends on the current one, resulting in randomly wandering... rather
than a sense of phrasal structure" — mitigated by higher-order chains, where "the current and
last *m*-1 states are taken into account," producing results with real phrasal coherence instead
of aimless wandering.[^5] **This is directly relevant to feasibility**: a first-order chain seeded
from the main theme's own note sequence could generate "related but different" sub-themes cheaply,
but would risk sounding aimless rather than clearly-related-to-the-main-theme without at least a
second-order model (tracking pairs of preceding notes, not just one) — a real implementation
complexity/quality tradeoff to name, not paper over. **A genuine chiptune-context precedent for
automated composition exists**: Yuzo Koshiro's "Automated Composing System" produced music
algorithmically within the genre's own hardware-constrained tradition[^3] — procedural chiptune
generation is not a hypothetical, it has shipped precedent, even if the specific technique isn't
publicly documented in detail.

### Sources
[^1]: [The Power of Musical Leitmotifs — Medium](https://medium.com/super-jump/the-power-of-musical-leitmotifs-177a40e4524e); corroborated by [Leitmotif / Video Games — TV Tropes](https://tvtropes.org/pmwiki/pmwiki.php/Leitmotif/VideoGames); accessed 2026-07-16 via WebSearch summary.
[^2]: [How the overworld theme of The Legend of Zelda takes us on a harmonic adventure — Splice](https://splice.com/blog/legend-of-zelda-overworld-harmony/); [The Music of Red, Blue and Yellow — PokéCommunity Daily](https://daily.pokecommunity.com/2016/02/01/the-music-of-red-blue-yellow/); [List of overworld music themes — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/List_of_overworld_music_themes); accessed 2026-07-16 via WebSearch summary.
[^3]: [Chiptune — Wikipedia (Game Boy music)](https://en.wikipedia.org/wiki/Game_Boy_music) (Koji Kondo's minimal-voice repetition/variation/counterpoint discipline; Yuzo Koshiro's Automated Composing System); accessed 2026-07-16 via WebSearch summary.
[^4]: [Music themes that "evolve" throughout the course of a game — ResetEra](https://www.resetera.com/threads/music-themes-that-evolve-throughout-the-course-of-a-game.772658/) (Sonic Advance 3, Sonic Frontiers examples); [An Examination of Leitmotifs and Their Use to Shape Narrative in UNDERTALE — Game Developer](https://www.gamedeveloper.com/audio/an-examination-of-leitmotifs-and-their-use-to-shape-narrative-in-undertale---part-1-of-2) (Overworld Ostinato); accessed 2026-07-16 via WebSearch summary.
[^5]: [Markov Chains for Computer Music Generation — Claremont](https://scholarship.claremont.edu/cgi/viewcontent.cgi?article=1848&context=jhm); corroborated by [Markov Chain Based Procedural Music Generator with User Chosen Mood Compatibility](https://adada.info/journals/Vol.21_No.01-3.pdf) and [A Review of Intelligent Music Generation Systems — arXiv](https://arxiv.org/pdf/2211.09124); accessed 2026-07-16 via WebSearch summary.

**Single-source flag:** none of the five claim clusters above rests on a single source — each is
corroborated by at least two independent results from the same search pass, matching this
project's own established citation-confidence discipline (`R212`'s own precedent, `R301`/
`BL-0011`). All citations are WebSearch-summary-level, not directly-fetched primary pages.

## Operational Context

`music.py` today ships **one hand-authored, fixed 16-bar track on a single APU channel (pulse
channel 1 only)** — confirmed by direct code read at intake (`BL-0127`'s own filing): `SONG` is a
flat list of `(freq, duration)` tuples, compiled to a byte stream, played by `music_tick` once per
frame regardless of `GAMESTATE`/zone/biome. **3 of 4 APU channels are unused** (R108); the last
full ROM build used ~29896 of 32768 bytes (~2872 bytes free). `R207`'s own Implementation Guidance
already named a per-zone music capability as a real future scope question, not yet acted on. `FS-
102`'s procedural-world-generation precedent (`worldgen.py`) already establishes this project's
own working pattern for "the same content, generated rather than exhaustively hand-authored": a
build-time Python routine (imported only by `test_rom.py`/`build_rom.py`, never by the shipped
ROM's own runtime code) mirrored in lockstep by an SM83 routine where genuine runtime generation is
needed — the same split this topic's own Implementation Guidance below recommends reusing for
music, not inventing a new pattern.

## Implementation Guidance

- **Favor the Zelda-style shared-melody variation model over independent per-identity
  compositions**, per `BL-0127`'s own wording and this document's own Concepts section — a main
  theme's melodic material recurs, transposed/re-tempo'd/re-registered per biome-family identity,
  rather than nine unrelated tracks that merely share a genre feel (the Pokémon model). This is
  both the more musically coherent reading of the request and the cheaper one in ROM terms.
- **Prefer build-time (Python) generation of the sub-theme variations over genuine SM83 runtime
  generation**, mirroring `worldgen.py`'s own established split — the sub-themes are a *fixed,
  finite set* (nine biome-family identities, `FR-4320`), not an unbounded, per-playthrough-unique
  space the way the world's own geometry is (`worldgen.py`'s own reason for needing *runtime*
  generation is that Infinite Mode's regions are unbounded and can't be pre-baked — music for nine
  fixed identities has no such requirement). A build-time generator produces nine fixed note
  sequences once, at ROM-build time, exactly like every other `tiles.py`/`tilemaps.py` content
  table — no new runtime code path, no new APU-timing risk, no `NFR-1300`-class frame-budget
  question to answer.
- **If procedural variation-generation is used (rather than a human composer authoring each
  sub-theme by ear from the main theme), use at least a second-order Markov model seeded from the
  main theme's own note sequence, not a first-order one** — per this document's own Concepts
  section, a first-order chain's well-documented "random wandering" failure mode would produce
  sub-themes that sound generically-related rather than clearly-derived, undermining the entire
  point of a shared-identity structure. A second-order (or higher) model, or a simpler rule-based
  transposition/tempo-shift transform (mirroring the Sonic Advance 3/Sonic Frontiers precedent
  above — deterministic transform, not statistical generation at all) is a lower-risk alternative
  worth weighing against true Markov generation's own added implementation complexity.
- **Concrete transform menu, cheapest first, all real-precedented above:** (1) transposition (shift
  the main theme to a different starting pitch/key per identity — the cheapest, most directly
  "clearly the same tune" option); (2) tempo/duration scaling (per `music.py`'s own existing
  `EN`/`QN`/`DQ`/`HN`/`WN` duration-constant vocabulary — scale them uniformly per identity,
  mirroring Sonic Frontiers' own tempo-drift technique); (3) a shared ostinato/accompaniment figure
  with per-identity melodic material layered over it (the UNDERTALE precedent) — **this is the one
  option that would require a second APU channel** (3 currently unused), a real scope increase
  worth naming explicitly, not assumed free.
- **Nine sub-themes is a real, non-trivial content/ROM-budget question, not automatically free.**
  `FR-4320`'s own nine biome-family identities are the natural sub-theme target count (reusing an
  already-decided taxonomy rather than inventing a separate one for music) — but nine variations
  of a 16-bar theme, even sharing melodic material, is real new ROM-resident data; a future
  `04-requirements-engineering`/`07-implementation-planning` pass should size the actual byte cost
  against the ~2872-byte headroom this document's own Operational Context measured, not assume it
  fits.
- **This is a genuinely new capability needing its own architecture-level decision before
  requirements can be written concretely** — per this topic's own Feature Mapping (below), no
  `FS-xxx`/ADR exists yet for *any* per-zone/per-biome audio variation, procedural or not. A
  `03-architecture-design-synthesis` pass (or a lighter `04-requirements-engineering` delta, if
  the architecture ladder is judged not to need a new decision — mirroring how `FR-4320` itself
  needed no new ADR, per `08-presentation-architecture.md` §8's own precedent for pre-anticipated
  extensions) should decide the transform menu and channel-budget question above before a
  concrete `FR`/`FS` is written, not leave it for `07-implementation-planning` to invent silently.

## Feature Mapping

*(No `FS-xxx` authored yet — this grounds a future `03`/`04`/`06` pass on `BL-0127`.)*

## Related Topics

R207 (the single-channel, phrase-length, and per-zone-flagged-as-future-work conventions this
topic extends into procedural/generative territory) · R108 (APU channel/register facts —
particularly the 3 unused channels this topic's own "shared ostinato" option would consume) ·
R213 (this project's own build-time/runtime procgen split precedent, `worldgen.py`, mirrored here
for music) · R212 (the sibling nine-identity biome-family axis this topic's own sub-theme count
target reuses — researched in the same pass, grounds an independent downstream capability).
