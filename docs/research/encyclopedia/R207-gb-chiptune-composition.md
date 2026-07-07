# R207 — GB-Era Chiptune Composition & Audio Feedback Cues

- **Document ID:** R207 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R108 (the APU register facts this composition sits on)
- **Referenced By:** none yet
- **Produces:** grounds `music.py`'s melody-writing conventions
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R108

## Purpose

What makes a single-channel GBC melody read as intentional rather than thin, and what convention
Bunny Quest's music already follows.

## Scope

Square-wave melody design under single-melodic-line constraints, phrase-length conventions, and
this project's current one-channel composition.

## Concepts

Square (pulse) waves are chiptune's melodic workhorse: their overtone structure cuts cleanly
through a mix, and adjusting the duty cycle (12.5/25/50/75%, R108) meaningfully changes
timbre/emotional character without needing a second voice.[^1] Because early PSG hardware had
limited polyphony, a huge share of beloved chiptune melodies are **single melodic lines**, with
perceived harmonic richness created through rapid arpeggiation (fast note-runs implying a chord)
rather than simultaneous multi-note harmony.[^2] Good chiptune melodies are typically short,
simple, and instantly recognizable — a common structural convention is a **4–8 measure phrase**
that loops cleanly, with a small variation introduced partway through (e.g. at measure 4 of an
8-measure phrase) to avoid monotony on repeat.[^2]

### Sources
[^1]: [What is Chiptune? — Baby Audio](https://babyaud.io/blog/chiptune-producers-guide), accessed 2026-07-06.
[^2]: [How to Make Chiptune Music — eMastered](https://emastered.com/blog/how-to-make-chiptune-music), accessed 2026-07-06.

## Operational Context

`music.py`'s header confirms Bunny Quest's music is "a new original 16-bar adventure tune in C
major," and per direct code read plays entirely on **Channel 1** (R108) — a single melodic line,
squarely in the single-voice convention above; no second channel or arpeggiation trick is
currently used to imply harmony. At 16 bars, the piece is roughly double the "4–8 measure loop"
convention's typical single-phrase length — consistent with a slightly more developed theme
(verse-like structure) rather than a tight 4-8-bar loop, while still being short enough to repeat
without becoming tiresome across a play session.

## Implementation Guidance

- **A second voice (Channel 2, R108) is the natural next step for richer harmony** without
  abandoning the clean single-melody convention — use it for a counter-melody or a light harmony
  line under the existing Channel 1 melody, not as a competing lead.
- **Arpeggiation is a legitimate, era-authentic technique for implying chords on one channel** if
  a future track wants harmonic depth without a second voice — a rapid 3-note run (root-third-
  fifth) repeated fast enough to read as a sustained chord, rather than a literal simultaneous
  triad (which channel 1 alone cannot produce).
- **Keep new tracks in the 8–16 bar range with a small internal variation** (per the "vary at
  measure 4/8" convention) — this project's existing 16-bar piece already fits comfortably in
  this band; a much longer or entirely repetition-free track would be an unusual departure from
  the genre's own economy-of-material convention.
- **A future per-zone or per-context music change** (relevant if C7's larger world eventually
  wants distinct zone themes, similar to its distinct zone palettes, R104/R208) is a real content
  scope question — flag it for GDS-01/GDS-08 rather than assuming one track suffices indefinitely
  as the world grows.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R108 (the APU channel-1 register facts this composition's frequency/duty/envelope choices are
built on).
