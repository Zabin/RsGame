---
name: 02-research-game-design
description: Produce or refresh citation-grounded research on game design for the Bunny Garden Adventure GBC game — top-down collect-a-thon conventions, 8-bit game feel (movement speed, animation cadence, collision tolerances), screen/level design on the 20×18 tile grid, HUD/score-bar patterns, save/checkpoint design, difficulty and progression, GB-era chiptune composition and audio feedback — as docs/research/encyclopedia/R2xx-* topics. Use when asked to research game-design questions, to add/extend R2xx topics, or to ground an FS-xxx that adds/changes a mechanic, zone, screen, or song before it is specified. Not for hardware facts (02-research-gbc-hardware) or tooling (02-research-tooling-and-testing).
---

# Research: Game Design

Produces the **R200-tier encyclopedia** (`docs/research/encyclopedia/R201`–…) — the design
grounding for decisions about how the game should *play*, *look*, and *sound*, so feature specs
cite convention and evidence rather than taste. Tracked in
[`docs/research/INDEX.md`](../../../docs/research/INDEX.md); authored index-first.

## What this is for (and what it is not)

This skill answers: "if an agent is about to spec or tune a mechanic, a zone layout, a HUD
element, or a song, what do successful games of this class do, and why?" — never "write the spec
itself" (that's stage 06) and never "decide this game's vision" (stage 01). Claims cite real
sources: published design analyses, postmortems, documented conventions of era-appropriate games,
and the project's own verified behavior (`Claude.md` Known Good Behavior, `test_rom.py`).
Numbers presented as recommendations ("1px/frame walk speed reads as deliberate") must carry the
comparison or source that grounds them.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| `docs/research/encyclopedia/R2xx-*.md` + the R200 section of `docs/research/INDEX.md` | Suggested initial set (adjust to real gaps): R201 Top-down collect-a-thon structure & goal design · R202 8-bit game feel: movement, animation cadence, collision tolerance · R203 Screen composition on a 20×18 tile grid (readability, landmarking, edges-as-exits) · R204 HUD & score-bar conventions · R205 Save-system design & player expectations (battery saves, auto-load) · R206 Difficulty, pacing & session length for handheld play · R207 GB-era chiptune composition & audio feedback cues · R208 Palette & color design under CGB constraints. |
| Design grounding targets | `tilemaps.py` (screens, spawn tables), `asm_game.py` (movement/collision constants), `music.py`, and any FS-xxx touching mechanics/zones/screens/audio. |

**Author index-before-content**, same rule as the sibling tiers.

## Methodology (binding for every topic)

Same seven-section shape and citation rules as `02-research-gbc-hardware` (Purpose · Scope ·
Concepts · Operational Context · Implementation Guidance · Feature Mapping · Related Topics;
inline citations at the claim site; `### Sources` per `##` section; single-source claims flagged;
3–8 page band; if WebSearch/WebFetch are unavailable, mark citations "needs fetch-verification"
and report the gap). §5 Implementation Guidance must land on concrete statements tied to this
project's real files and constants — e.g. "collectible proximity radius (currently 10px in
`asm_game.py`) sits at the generous end of the era's 4–12px norm; don't shrink it without also
slowing zone-transition edges," not "make collision feel fair."

## Workflow

1. **Read the trigger context** — which mechanic/zone/screen/song needs grounding, and which
   R2xx topic(s) own it.
2. **Check existing coverage first** in the R200 index section and topic files.
3. **If a gap exists:** index row first (`⛔ Planned`), then research, then write/update the topic
   per the methodology.
4. **Cross-link both directions**; flip the index status; update `ROADMAP.md`'s research theme
   row.
5. **Verify against the quality gate and commit** as `docs(research): R2xx — <what changed>`.

## Quality gate (before calling a topic/edit done)

- [ ] Every claim has an inline citation at the claim site; every `##` section has `### Sources`.
- [ ] §5 gives concrete do/don't statements tied to this project's real files/constants.
- [ ] Recommendations are grounded in comparison/evidence, not taste presented as fact.
- [ ] Frontmatter cross-references bidirectionally consistent; 3–8 page band held.

## Gotchas

- Design research **grounds** specs; it never quietly *becomes* a spec. "The game should add a
  fishing minigame" is intake (stage 00) + requirements (stage 04), not a research conclusion.
- The shipped game is evidence too: `Claude.md`'s Known Good Behavior list documents what already
  works and why players can rely on it — treat changes to it as expensive.
- This skill does not touch Tier R100 (hardware) or Tier R300 (tooling & verification).

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 02 — Research** of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md)). The three `02-research-*` skills are peers — run
whichever owns the tier the gap is in. Upstream: `01-vision`. Downstream:
`03-architecture-design-synthesis` (and whichever spec-authoring skill requested the grounding).

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — every topic produced or updated (paths), every index status flipped.
2. **Recommendations** — remaining coverage gaps, citation-verification gaps, and who owns each
   follow-up.
3. **Next step** — if this run closed a grounding gap requested by a downstream skill, return to
   that skill; if another research tier still has a gap for the current increment, name the
   sibling `02-research-*` skill; otherwise advance to `03-architecture-design-synthesis`.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
