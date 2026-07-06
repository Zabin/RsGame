# GDS-01 — Concept of Play

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-00](00-vision.md); the next level,
> [GDS-02 System Context](02-system-context.md), builds on this one.

## Purpose

Who plays, the session shape, the core loop, and the game-state machine at player altitude.

## Content

### 1. Who plays

Per [MSTR-001](../master/MSTR-001-program-vision.md) §2 and assumption A5: a casual, all-ages
player in short, interruptible handheld sessions. Nothing in this level adds to that — it is
carried forward, not restated in different words.

### 2. Session shape

A session either starts fresh (title screen) or resumes silently (a valid battery save auto-loads
directly into `PLAYING`, skipping the title entirely — confirmed by direct code read of
`asm_game.py`'s `try_load_save`, called unconditionally at boot). There is no "continue" menu to
navigate: the console being turned on *is* the resume action, exactly the low-friction pattern
[R205](../research/encyclopedia/R205-save-system-design.md) identifies as the strongest player-
expectation match this game already has. A session ends whenever the player stops (no explicit
"quit" state — the game simply persists nothing further until the next explicit menu save).

### 3. The core loop

**Explore → collect → (repeat) → find the zone's carrot → transition to the next zone → …→ all
nine carrots collected → victory.** Two collectible tiers run concurrently within this loop, per
[R201](../research/encyclopedia/R201-collectathon-goal-design.md):

- **Abundant tier** — stars and flowers, contributing to a running `SCORE` (0–99) with no
  completion requirement. Purely a moment-to-moment exploration reward.
- **Scarce tier** — exactly one carrot per zone, tracked individually in the 9-byte
  `CARROT_FLAGS` array and summed in `CARROTS_COUNT`. This is the actual stated goal: fully
  enumerable ("N of 9"), flatly structured (no zone's carrot gates another zone), and directly
  displayed in the HUD as `N-9` ([R204](../research/encyclopedia/R204-hud-score-bar-conventions.md)).

Movement between zones is player-driven: walking off any screen edge that has a valid neighbor
(signaled by an on-screen directional arrow, [R203](../research/encyclopedia/R203-screen-composition-tile-grid.md))
transitions to that neighboring zone. There is no forced sequence — the player may visit the nine
zones (Beach, Forest, Mountain, Lake, Village, Cave, Desert, Plains, Castle, arranged in a 3×3
grid) in any order the 3×3 adjacency allows.

### 4. The game-state machine (player altitude)

Six states (`GAMESTATE`, confirmed by direct `asm_game.py` read):

```
TITLE ──START──▶ INTRO ──A──▶ PLAYING ─────START─────▶ SAVE ──A/B──▶ PLAYING
                                 │  ▲                                   │
                                 │  └──────────────B───────── MAP ◀─SELECT
                                 │
                                 └── CARROTS_COUNT==9 ──▶ VICTORY ──A──▶ TITLE

(boot, valid save found) ───────────────────────────────▶ PLAYING  (skips TITLE/INTRO entirely)
```

- **TITLE** — landing state on a fresh boot (no valid save found); START advances to INTRO.
- **INTRO** — a short scripted dialog; A advances to PLAYING.
- **PLAYING** — the core loop: movement, collection, zone transitions, the victory check.
- **SAVE** — a menu reachable only from PLAYING (START); A commits the current state to
  battery-backed SRAM, B cancels — both return to PLAYING.
- **MAP** — a read-only 3×3 world overview reachable only from PLAYING (SELECT), showing which
  zones' carrots are collected (a heart per zone); B returns to PLAYING.
- **VICTORY** — entered automatically the instant `CARROTS_COUNT` reaches 9, from anywhere
  within PLAYING; A returns to TITLE (not to PLAYING — a full loop back to the start, consistent
  with this state machine treating victory as the session's natural endpoint rather than a
  pause).
- **Auto-load bypass:** at boot, `try_load_save` is called unconditionally; a valid save (magic
  bytes present) restores every persisted field and sets `GAMESTATE = PLAYING` directly —
  `TITLE`/`INTRO` are only ever seen on a save-less first boot or after an intentional wipe.

### 5. Open Question — world-scale direction (does not block this bootstrap pass)

[MSTR-001](../master/MSTR-001-program-vision.md) commitment **C7** targets a Zelda/Pokémon-scale
world; [R206](../research/encyclopedia/R206-difficulty-pacing-session-length.md) flagged that
this genre's own pacing convention assumes long, multi-session play — a real tension with this
game's current short-single-sitting identity (assumption A5) that the research topic explicitly
declined to resolve on its own. **This level states the tension rather than silently picking a
side:** as C7 is pursued, does the core loop above stay a short single-sitting experience over a
*much larger map* (many more, similarly-small zones — the "wider, not longer" direction), or does
it deliberately become a longer, multi-session game (fewer, larger zones, denser collectible
sets — the "deeper, not just wider" direction)? Two concrete constraints bear on this choice,
neither resolved here:

- **Palette budget** ([R104](../research/encyclopedia/R104-cgb-palette-system.md) /
  [`BL-0009`](../pipeline/backlog.md)): 8 BG palettes are already substantially committed across
  9 zones. "Wider" (many more zones) makes distinct per-zone color identity
  ([R208](../research/encyclopedia/R208-palette-color-design.md)) harder to sustain without
  deliberate palette reuse; "deeper" (fewer, larger zones) does not have this problem.
  - **Zone-adjacency signaling** ([R203](../research/encyclopedia/R203-screen-composition-tile-grid.md)):
  `_zone_arrows()`'s edge-direction logic currently assumes a fixed, fully-rectangular 3×3 grid.
  Either direction eventually requires generalizing this to an actual neighbor-lookup rather than
  a hardcoded rectangle — a "wider" direction hits this sooner (more zones sooner) than "deeper."

This Open Question is handed forward: `03-architecture-design-synthesis` itself (a future
`GDS-03`/an `ADS-xxx`) or `04-requirements-engineering` should resolve it with an explicit
decision once the C7 expansion is actually planned, not before — the bootstrap increment's job is
naming the tension, not resolving a decision nobody has asked for yet.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-00`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `Claude.md`'s "Known Good Behavior" section is the historical
source this level was scaffolded to merge from — but per `MSTR-001` §8, that source (like the
rest of `Claude.md`) describes the *pre-rewrite* game and was **not used as a source of current-
state facts** here; this level is instead sourced directly from `asm_game.py`/`tilemaps.py`
(the same correction discipline `01-vision` already applied). **Decision: `Claude.md`'s Known
Good Behavior section is superseded by this level for state-machine/core-loop facts** — a future
documentation-refresh pass (`BL-0007`/`BL-0008`) should turn that section into a short pointer
here rather than re-describing the same content, once that remediation lands. Until then,
`Claude.md`'s own text remains flagged stale (per `MSTR-001` §6) and this document is
authoritative for Concept of Play.
