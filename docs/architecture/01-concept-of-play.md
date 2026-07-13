# GDS-01 — Concept of Play

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the aesthetics/
> visual-story-narrative/procgen-world-map increment — see §2a/§3a/§4a below; delta 2026-07-13 —
> §4c, `SELECT` becomes a small menu, target state, not yet shipped, `CR-06`/`BL-0100`).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-00](00-vision.md); the next level,
> [GDS-02 System Context](02-system-context.md), builds on this one.
>
> **Reading this document:** §§1–5 describe the game **as currently shipped** (pre-increment) and
> remain accurate — nothing below has shipped yet. §§2a/3a/4a are the **target state** this
> increment's [ADR-0009](adr/ADR-0009-screen-graph-world-generation.md)/
> [ADR-0010](adr/ADR-0010-seed-scale-model.md) commit to, per MSTR-001 v3.0's C8/C9/C10 (forward-
> looking commitments, same pattern as C7 before it — MSTR-001 §8).

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

### 2a. Session shape, revised (2026-07-09 delta; confirmed as shipped
2026-07-10, `IP-1040`)

Per **MSTR-001 C2 (amended v3.0)** and **ADR-0010**: a session now always starts at a **main
menu** (continue / new game), never silently into `PLAYING` — the auto-load bypass §2/§4 describe
above is superseded. `try_load_save`'s unconditional-at-boot call is replaced by a menu-driven
choice: **continue** loads the existing save (if its version byte matches — a mismatched/absent
save simply has no `continue` option, per ADR-0010); **new game** enters the seed/scale entry
flow (§3a) before the first `PLAYING` frame. This is a genuine, deliberate loss of the "console
power-on is the resume action" low-friction pattern R205 praised — a considered tradeoff, not an
oversight: D9's explicit direction is that boot always shows a menu, in exchange for the new-game
flow's seed/scale entry becoming reachable without an intervening save-wipe. A session's *end*
is now also more deliberate: the in-game start-button menu's **exit-to-main-menu** option
(**D8/D10**) **auto-saves before returning to the main menu** — no progress is ever lost by
exiting, and the main menu (not just power-off) is now a legitimate mid-session checkpoint.

### 3a. The core loop, revised (2026-07-09 delta — target state, not yet shipped)

**Explore → collect → (repeat) → find the region's key item → transition to an adjacent,
grammar-legal region → …→ every region's key item collected → victory.** Per **MSTR-001 C9/C10**
and **ADR-0009**, three concrete changes to §3's shipped description:

- **"Carrot" generalizes to an item-agnostic "key item."** Per **D2**, the specific collectible
  is not a vision-level requirement — carrots are today's shipped instance, not the permanent
  name. The *structure* §3 describes (exactly one scarce, fully-enumerable, victory-gating item
  per region; an abundant, uncapped scoring tier alongside it, per
  [R201](../research/encyclopedia/R201-collectathon-goal-design.md)) is unchanged and still
  governs — only the item's specific identity is no longer fixed.
- **Region count generalizes from a fixed 9 to `scale × scale`** (**ADR-0010**, scale 2–9,
  default 3). The HUD's "N-9" display (§3, R204) becomes "N-`scale²`" — a parameterized version
  of the same convention, not a redesign.
- **Adjacency is no longer a fixed 3×3 rectangle — it is generated, grammar-constrained**
  (**ADR-0009**, grounded in
  [R212](../research/encyclopedia/R212-wordless-environmental-storytelling-biome-grammar.md)).
  Movement is still player-driven, still signaled by on-screen directional arrows (R203) — but
  which directions have a valid neighbor, and what biome that neighbor is, is now a per-world
  generated fact rather than a fixed layout every player sees identically. **This is also where
  the story lives (C9):** because the grammar only permits coherent biome sequences (water →
  beach → grassland → hills → mountains → sky, never a disjointed pairing), traveling through the
  generated world *is* the narrative — no dialogue is needed for the journey to read as one
  (per [R212](../research/encyclopedia/R212-wordless-environmental-storytelling-biome-grammar.md)'s
  environmental-storytelling grounding).

### 4a. New-game creation and the main-menu state, revised (2026-07-09 delta;
confirmed as shipped 2026-07-10, `IP-1040`)

Two new states join §4's six-state machine, and the auto-load bypass is removed:

```
(boot) ──────────▶ MAIN MENU ──"continue" (valid save)──▶ PLAYING
                       │
                       └──"new game"──▶ SEED/SCALE ENTRY ──confirm──▶ INTRO ──A──▶ PLAYING

PLAYING ──START──▶ SAVE ──A/B──▶ PLAYING
   │                 │
   │                 └──"exit to main menu"──▶ (auto-save) ──▶ MAIN MENU
   │
   └── every region's key item collected ──▶ VICTORY ──A──▶ MAIN MENU
```

- **MAIN MENU** (new) — the universal landing state on boot (replaces the old
  TITLE/auto-load-bypass split at §4: `TITLE` is superseded by `MAIN MENU`, not merely renamed —
  `MAIN MENU` always appears, even with a valid save present, unlike `TITLE`, which was skipped
  whenever `try_load_save` found one). Presents **continue** (only if a version-matching save
  exists, per ADR-0010) and **new game**.
- **SEED/SCALE ENTRY** (new) — reachable only from `MAIN MENU`'s "new game"; the digit-cursor
  picker ADR-0010 specifies (D-pad selects/moves, A confirms); on confirm, seeds the PRNG
  (R111), runs the world generator (ADR-0009), and proceeds to `INTRO`.
- **SAVE**'s exit path gains a third option beyond A(save)/B(cancel): **exit to main menu**,
  which auto-saves (D10) then transitions to `MAIN MENU` rather than back to `PLAYING`.
- **VICTORY**'s A-press target changes from `TITLE` to `MAIN MENU`, following `TITLE`'s own
  supersession.
- **§4's auto-load-bypass bullet is retracted** — `try_load_save` is no longer called
  unconditionally at boot; loading is `MAIN MENU`'s "continue" action only (§2a).

### 4b. Cross-reference to bank switching (informational, ADR-0011)

**ADR-0011** (MBC1 default-wiring bank switching, superseding ADR-0001) does not itself change
this level's player-altitude description — it is a ROM-layout decision, invisible at the
state-machine/core-loop altitude this document operates at. Noted here only so a reader of §§2a–4a
understands why a "bigger world" is affordable: the generator's ROM cost is small (ADR-0009's
consequence), and remaining headroom growth is a planned, not improvised, path (ADR-0011).

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

### 4c. `SELECT` becomes a small menu — delta for `CR-06`/`BL-0100` (decided 2026-07-13)

`BL-0100` (project owner): a screen explaining the on-screen transition-edge indicator tiles
(§10 of [GDS-08](08-presentation-architecture.md), `FR-2320`/`FR-2330`) — the player currently has
no in-game way to learn the open-arrow/blocked-edge-bar/no-indicator distinction. §4's diagram
names `MAP` as `SELECT`'s sole destination; there is no existing state-machine node for a second
screen. `04-requirements-engineering` correctly declined to invent one (RQ-03 finding #15, `CR-06`)
and routed the decision here.

**Decision: `SELECT` now opens a small two-option cursor menu (`MAP` / `LEGEND`) instead of
jumping directly to `MAP`; `MAP` itself is completely unchanged.** Reuses the exact cursor-menu
pattern `MAIN MENU` already established (§4a) — a highlighted option, D-pad up/down to move the
highlight, `A` to confirm, rather than inventing a second UI convention for the same shape of
choice. `MAP`'s own content, layout, and eventual redesign (`BL-0050`, still deferred pending the
win-condition/infinite-world thread) are entirely untouched by this delta — the new menu is purely
an extra hop in front of it, not a change to what `MAP` shows. `LEGEND` (new) is
[GDS-08](08-presentation-architecture.md) §11's single static explanation screen. From either
`MAP` or `LEGEND`, `B` returns directly to `PLAYING` — matching `MAP`'s own existing one-step-back
convention (§4's "B: EXIT MAP") exactly, not routing back through the intermediate menu.

```
PLAYING ──SELECT──▶ SELECT MENU ──B (cancel)──▶ PLAYING
                        │
                        ├──"map" (A)─────▶ MAP ────B────▶ PLAYING
                        └──"legend" (A)──▶ LEGEND ──B───▶ PLAYING
```

- **SELECT MENU** (new) — reachable only from `PLAYING` (`SELECT`); presents **map** and
  **legend**, cursor-selected exactly as `MAIN MENU`'s own continue/new-game choice is (§4a); `B`
  cancels directly back to `PLAYING` (no destination visited).
- **LEGEND** (new) — reachable only from `SELECT MENU`'s "legend"; a single static screen (content
  decided at [GDS-08](08-presentation-architecture.md) §11); `B` returns to `PLAYING`.
- **MAP** — unchanged from §4's own description, except its entry point moves from a direct
  `SELECT` press to `SELECT MENU`'s "map" confirm. Still `B` returns to `PLAYING`.

**Named tradeoff, not silently absorbed:** reaching `MAP` now costs one extra button press
(`SELECT` → highlight/confirm → `MAP`, versus today's single `SELECT` → `MAP`) for every player,
not just those who want `LEGEND`. This is accepted rather than routed around (e.g. a long-press-
`SELECT`-for-legend scheme was considered and rejected — this codebase's existing input handling
has no long-press/hold-duration convention anywhere, R107, and inventing one for a single low-
frequency screen is a worse cost than one extra `A` press) because `MAIN MENU`'s own
continue/new-game choice already asks the same one-extra-step question at session start with no
recorded player-facing complaint, and `LEGEND` is expected to be a rarely-revisited reference
screen, not a per-session action — the cost lands once per `MAP` visit, which itself is already an
optional, player-initiated pause from `PLAYING`, not a time-critical action.

**Not decided here (implementation-level, `07`/`08-code-implementation`):** the exact WRAM byte
for `SELECT MENU`'s own cursor state (reuse `MM_CURSOR`, since `MAIN MENU` and `SELECT MENU` are
never simultaneously active, or a new dedicated byte — a [GDS-07](07-data-model.md) data-model
choice for whoever implements this, following `ADR-0015`'s own precedent of leaving byte-encoding
choices to `07`/`08` when either representation is equally valid); the new `GAMESTATE` numeric
values for `SELECT MENU`/`LEGEND` (the next two free values following the existing `GS_SEED_SCALE_ENTRY = 7`,
per this project's own append-only `GAMESTATE` numbering convention, `asm_game.py:170,174`).

### 5. Former Open Question — world-scale direction (resolved 2026-07-09, see §3a/ADR-0010)

This section originally posed "wider vs. deeper" as an open tension (bootstrap pass, 2026-07-06;
tracked as `BL-0015`). **Resolved, not by picking a side, but by dissolving the fork**: MSTR-001
v3.0's **C10** and **ADR-0010** make world scale a **player-chosen, per-save parameter**
(2–9, default 3 — §3a) rather than an architecture-level commitment this document had to fix in
advance. The player effectively picks "wider" (a larger `scale`) or stays closer to today's felt
size (`scale=3`) each time they start a new game — no single answer needs to bind every future
increment. The two constraints originally named here are addressed, not ignored: the **palette
budget** concern is superseded by [GDS-08](08-presentation-architecture.md)'s biome-family
palette strategy (one biome per screen, per D2's clarification — no per-screen blending pressure,
just a bound on the number of distinct biome families, which is a content question, not a scale
question); the **zone-adjacency signaling** concern (`_zone_arrows()`'s hardcoded rectangle) is
directly resolved by **ADR-0009**, which replaces it with generated adjacency entirely. `BL-0015`
is closed (`00-pipeline-manager` run #30, 2026-07-09) with this same rationale.

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

**Delta record (2026-07-09):** §§2a/3a/4a/4b added, §5 resolved, per the adopted increment plan's
Phase 3 ([PLAN-requirements-aesthetics-story-map.md](../pipeline/PLAN-requirements-aesthetics-story-map.md))
and ADR-0009/0010/0011. This is a **delta, not a re-authoring** — §§1–5's original content
remains the accurate description of the *currently shipped* game; §§2a/3a/4a/4b describe the
*target* the increment's eventual implementation packages build toward, exactly the same
"target commitment, not yet built" pattern C7 established at v2.0. No merge-gate box above is
reopened by this delta — `Claude.md`/`memory.md` are current again as of `IP-9030` and this
delta does not change that; a future doc-refresh once §§2a–4b actually ship is the natural next
touch-point, not this pass.

**Delta record (2026-07-13):** §4c added, per `CR-06`/`BL-0100` (project owner request, routed
here by `04-requirements-engineering`'s own RQ-03 finding #15 after it correctly declined to
invent a new game state at the requirements level). Delta, not re-authoring — §§1–4b remain
accurate (as-shipped or already-established target state); §4c is new **target state, not yet
shipped** — no `IP-xxxx` package exists for it yet. `04-requirements-engineering` returns to
derive `CR-06`'s real FR from this delta next. No merge-gate box above is reopened.
