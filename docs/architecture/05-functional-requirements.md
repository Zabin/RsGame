# GDS-05 — Functional Requirements

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-04](04-domain-model.md); the next level,
> [GDS-06 Non-functional Requirements](06-non-functional-requirements.md), builds on this one.
> **This level states capability-level facts, not a numbered `FR-xxxx` baseline** —
> `04-requirements-engineering` derives that baseline from the capabilities named here.

## Purpose

Capability-level functional requirements, elaborated in full traceability detail by
`docs/requirements/01-functional-requirements.md` once stage 04 runs.

## Content

Six capability groupings, each confirmed against the shipped code directly (per
[GDS-02](02-system-context.md)'s finding: `test_rom.py`'s T1 suite is trustworthy evidence; its
T2–T10 suites are not, per [`BL-0006`](../pipeline/backlog.md) — every capability below is
verified by reading `asm_game.py` itself, not by trusting the stale test assertions).

### C1 — Game-state transitions

The system **shall** implement the 6-state machine (TITLE/INTRO/PLAYING/SAVE/MAP/VICTORY) and
its transitions exactly as [GDS-01](01-concept-of-play.md) §4 describes, including the
auto-load-on-boot bypass (a valid battery save transitions directly to PLAYING, skipping
TITLE/INTRO). Source: `asm_game.py`'s state-dispatch table and `try_load_save`, confirmed by
direct read.

### C2 — Player movement & zone traversal

The system **shall** move the player continuously while a direction is held (fixed-speed,
[R202](../research/encyclopedia/R202-8bit-game-feel.md)), and **shall** transition to the
adjacent zone in the 3×3 grid ([GDS-04](04-domain-model.md)) when the player crosses a screen
edge that has a valid neighbor in that direction, signaled by an on-screen arrow
([R203](../research/encyclopedia/R203-screen-composition-tile-grid.md)). No transition **shall**
occur toward a grid edge with no neighbor (row/col boundary).

### C3 — Collection mechanics

The system **shall** detect collection of a Collectible ([GDS-04](04-domain-model.md)) when the
player's position is within 10px on both axes of the collectible's position (confirmed
`CP_n(10)` at two independent axis checks — [R202](../research/encyclopedia/R202-8bit-game-feel.md)).
On collection: a **ScoreItem** (star/flower) **shall** increment `Score` and be removed from
play; a **Carrot shall** set that zone's flag in `CarrotFlags`, increment `CarrotCount`, and be
removed from play.

### C4 — Victory condition

The system **shall** transition to VICTORY the instant `CarrotCount` reaches 9 (all zones'
carrots collected), from anywhere within PLAYING — confirmed against `asm_game.py`'s victory
check, which reads `CarrotCount` directly (not derived from summing `CarrotFlags` at check-time).

### C5 — Save / load

The system **shall** persist `{CurrentZone, PlayerPosition, CarrotCount, Score, CarrotFlags[9]}`
to battery-backed SRAM on an explicit player-initiated SAVE-menu action
([R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md)/
[R205](../research/encyclopedia/R205-save-system-design.md)), and **shall** restore that exact
field set automatically on boot if a valid save (magic bytes present) is found. Per
[`BL-0018`](../pipeline/backlog.md) (open, not resolved here): the system does **not** persist
player facing direction, animation frame, or per-zone `ScoreItem` collected-state — whether this
is intended scope is a question for `04-requirements-engineering` to resolve when deriving the
save/persistence requirement, not assumed here either way.

### C6 — Presentation

The system **shall** render, for every zone, a static single-screen composition (terrain +
landmark elements, [R203](../research/encyclopedia/R203-screen-composition-tile-grid.md)) with a
persistent row-0 HUD showing carrot progress (`N-9`) and score
([R204](../research/encyclopedia/R204-hud-score-bar-conventions.md)), plus five non-zone UI
screens (title, intro, save, map, victory — [GDS-04](04-domain-model.md)).

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-04`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `Claude.md`'s "Known Good Behavior" list is **partially
consistent** with the capabilities above (movement, collection, save/load, zone transitions are
all still true in substance, just re-scoped from 3 to 9 zones and gifts to carrots) — but its
specific enumeration (gift counts, zone names, "GIFTS=7") is stale. `test_rom.py`'s T2–T10 suites
are **not** consulted as evidence for any capability above, per `GDS-02`'s finding
(`BL-0006`); T1 is cited only implicitly (it verifies the ROM these capabilities run inside of,
not the capabilities themselves). **Decision: this level supersedes `Claude.md`'s Known Good
Behavior list as the capability-level source of truth**, pending the `BL-0007`/`BL-0008`
documentation-refresh pass that will eventually correct `Claude.md` itself to match.
