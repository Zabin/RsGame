---
name: 09-content-review
description: Qualitatively review shipped game content against its spec — drive the built ROM in the emulator, screenshot every affected screen/state, and judge tile art readability, palette use, screen composition, spawn placement fairness, HUD correctness, and music correctness (note/tempo fidelity to the spec) — producing a Content Review report under docs/reviews/. The stage-09 peer of 09-package-verification: verification audits the ledger claims mechanically; this skill judges whether the rendered result actually satisfies the design intent the FS and R2xx research describe. Use after 08-content-authoring completes a package, or when asked to "review the new zone/tiles/song," "check the art," or "does this screen read well." Read-only with respect to code and content — findings route back to 08-content-authoring (or upstream); it never fixes anything.
---

# Content Review

Judges **rendered content against design intent**. `09-package-verification` proves the package
did what its checklist says; this peer proves the result *reads, plays, and sounds* the way the
spec and the R200-tier design research say it should. It observes and reports; it changes nothing
but its own report.

## Scope selection

One content package (after its `08-content-authoring` run), one feature's content surface, or an
explicitly named set of screens/tiles/songs. The reviewed content should already be `COMPLETE`
(and ideally `VERIFIED`) — if the mechanical verification hasn't run, say so; this review doesn't
substitute for it.

## What to check (the review dimensions)

1. **Visual fidelity** — build the ROM and drive every affected screen/state via
   `run-bunnygarden`, capturing screenshots (title, intro, each affected zone, save/map/victory
   as applicable). Do the tiles render as the spec describes? Bitplanes correct (no washed-out or
   inverted art)? Palette assignments per `memory.md`'s tables?
2. **Readability & composition** — against R203/R204 (once authored) and the FS: does the player
   read the screen at a glance — path vs. obstacle vs. collectible? HUD legible? Landmarks
   distinct between zones?
3. **Play fairness** — spawn positions vs. `memory.md`'s tables: collectibles reachable, not
   overlapping spawn points or transition edges; gift placement consistent with the zone's
   intended difficulty.
4. **Audio correctness** — music data vs. the spec's notation: note sequence, octave, tempo
   (QN/HN frame counts); audible check via emulator where practical, data-level check via
   `music.py` otherwise.
5. **Documentation coherence** — `memory.md`'s tile/palette/collectible quick-refs and
   `Claude.md`'s relevant sections reflect the shipped content; the FS's acceptance criteria all
   have evidence.

## Output

**`docs/reviews/content-review-<scope>.md`**: scope + package list (with the commit hash
reviewed), the screenshots captured (paths), evidence per dimension, and findings as one row each
— `Finding | Artifacts involved | Description | Severity | Recommended owner` — using the
project's Critical/High/Medium/Low scale. A clean review states what was actually exercised to
earn the "clean." Update `ROADMAP.md`'s reviews row if it tracks review documents.

## Quality gate

- [ ] The ROM reviewed was rebuilt from the current tree (commit hash recorded).
- [ ] Every affected screen/state was actually driven and screenshotted — not judged from source.
- [ ] All five dimensions exercised; a dimension with nothing to report says what was checked.
- [ ] Every finding has a severity and a concrete recommended owner; none fixed in-pass.
- [ ] Nothing but the report (and tracker rows) was written.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 09 — Content Review**, peer of `09-package-verification` (see
[`.claude/skills/README.md`](../README.md)). Upstream: `08-content-authoring`. Downstream:
`10-integration-review`, or back to `08-content-authoring` with findings.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the report written (path), scope, headline result (clean / N findings by
   severity), screenshots captured.
2. **Recommendations** — each finding with its owner: content defects → `08-content-authoring`
   (via a `07` remediation package if the fix isn't covered by an open package); spec-intent
   ambiguity → `06-feature-specification`; design-convention gaps → `02-research-game-design`.
3. **Next step** — clean: continue the tranche (next stage-08 package, or
   `10-integration-review` if the tranche is done); findings: route them per above and name the
   first step.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
