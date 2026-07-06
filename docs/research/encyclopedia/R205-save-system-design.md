# R205 — Save-System Design & Player Expectations

- **Document ID:** R205 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R106 (the MBC1 battery-save mechanism this design sits on)
- **Referenced By:** none yet
- **Produces:** grounds `asm_game.py`'s save/load/auto-load flow
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R106

## Purpose

What players expect from a save system in a short-session handheld game, and how well Bunny
Quest's current save flow (player-initiated menu save + silent auto-load) matches that
expectation.

## Scope

Player-initiated vs. automatic saving, the "stop anytime, resume with near-zero replay" principle,
and this project's current implementation of both.

## Concepts

The foundational expectation: **a player should be able to stop playing at any time and resume
close to where they left off, with minimal or no repeated effort** — this is the single dominant
design goal a save system should serve.[^1] Two broad strategies satisfy it: **player-initiated
saving** (an explicit save action/menu, giving the player control over exactly when a checkpoint
is captured) and **automatic/checkpoint saving** (the game saves progress transparently,
prioritizing convenience over player control).[^1] Modern design increasingly favors automatic
checkpointing specifically to remove the *anxiety* of "did I remember to save" — letting players
disengage without a mental save-checklist.[^2] Handheld/short-session context specifically raises
the value of low-friction saving, since a session may end involuntarily (battery, being called
away) rather than at a natural stopping point.[^1]

### Sources
[^1]: [Beginning Game Development: Save Systems — Lem Apperson, Medium](https://medium.com/@lemapp09/beginning-game-development-save-systems-28ac38064b54), accessed 2026-07-06.
[^2]: [Saving the Day: Save Systems in Games — Game Developer](https://www.gamedeveloper.com/design/saving-the-day-save-systems-in-games), accessed 2026-07-06.

## Operational Context

Bunny Quest already combines **both** strategies, per direct `asm_game.py` read: START in
`PLAYING` opens an explicit SAVE menu (A confirms, B cancels) — player-initiated, giving explicit
control — and separately, a valid battery-backed save (magic bytes `B`,`U`,`N`,`Y` at `0xA000`+,
R106) is **auto-loaded silently on boot**, skipping the title screen entirely when found. This
combination is a reasonable match to the guidance above: the player gets explicit control over
*when* progress is committed (menu save), while the game removes friction from *resuming* (no
"load game" menu needed — booting the console is the resume action). The one gap relative to
"minimal replay": since saving is purely player-initiated with no automatic checkpoint, a session
that ends without the player remembering to open the SAVE menu loses all unsaved progress —
exactly the "did I remember to save" anxiety modern automatic-checkpoint design aims to remove.

## Implementation Guidance

- **Consider a lightweight auto-save trigger** (e.g. on every zone transition, which is already a
  natural, infrequent checkpoint moment in this game) as a future enhancement to reduce the
  "forgot to save" loss window — this is a genuine design option to weigh against the added ROM/
  complexity cost, not an obvious must-have; record the decision explicitly (GDS-01 or a future
  FS) rather than adding it silently.
- **The current auto-load-on-boot behavior is a strong player-expectation match** ("resume with
  near-zero replay effort") — preserve it as an invariant; any future save-format change (e.g.
  adding fields for a larger world, C7) must keep this silent-resume behavior working, not just the
  raw byte layout.
- **A future multi-slot or multi-profile save system** (not currently present — one save slot
  only) would be a deliberate scope expansion, not implied by anything in this topic; flag as a
  Candidate Requirement if ever requested rather than assumed.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R106 (the MBC1 battery-save mechanism and enable/disable bracketing this design relies on).
