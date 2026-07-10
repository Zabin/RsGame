# GDS-06 — Non-functional Requirements

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-05](05-functional-requirements.md); the next
> level, [GDS-07 Data Model](07-data-model.md), builds on this one. **This level states its
> compliance status honestly, including where it is not currently met — an NFR named here is a
> standard the system must hold to, not a claim that it already does.**

## Purpose

ROM budget (32768 bytes, single bank), VBlank timing discipline, save integrity, build
reproducibility, test-coverage bar.

## Content

### N1 — ROM budget

The ROM **shall** fit within one 32768-byte bank (assumption A1; [GDS-02](02-system-context.md)).
**Status: met.** 23148 bytes used, ~9.6KB headroom, confirmed directly. Related but distinct: the
CGB's 8-BG/8-OBJ palette ceiling ([R104](../research/encyclopedia/R104-cgb-palette-system.md)) is
a separate constraint that is *also* under pressure at 9 zones
([`BL-0009`](../pipeline/backlog.md)) — cross-referenced here, not re-derived; a future package
should check both budgets independently, since headroom in one does not imply headroom in the
other.

### N2 — VBlank timing discipline

Every VRAM/OAM write **shall** occur either with the LCD off or within a confirmed-VBlank window
([R102](../research/encyclopedia/R102-ppu-vram-oam-timing.md)). **Status: met (2026-07-07).** The
score-bar VRAM write (`Claude.md`'s original bug note, re-flagged as
[`BL-0003`](../pipeline/backlog.md), folded into [`BL-0008`](../pipeline/backlog.md)) was
relocated to the main loop's frame top by
[`IP-9020`](../implementation/packages/IP-9020-score-bar-vblank-fix.md) — see
[`NFR-1200`](../requirements/02-non-functional-requirements.md) for the full remediation record
and test evidence — independently verified by `09-package-verification`
([`VR-9020`](../implementation/verification/VR-9020-score-bar-vblank-fix.md), 2026-07-07).

### N3 — Save integrity

Every SRAM access **shall** be bracketed by the MBC1 enable ($0A)/disable ($00) sequence
([R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md)). **Status: met** — confirmed
directly against both the save and load routines. Separately, **exactly the field set the system
commits to persisting shall round-trip correctly** — currently
`{CurrentZone, PlayerPosition, CarrotCount, Score, CarrotFlags[9]}`; whether that field set is the
*intended* scope (vs. also persisting player facing/animation/per-zone score-item state) is
`BL-0018`'s open question, not resolved by this NFR — this NFR only requires that whatever fields
are declared persisted round-trip correctly, which they currently do.

### N4 — Build determinism

A clean rebuild from source **shall** be byte-identical to the previously-shipped ROM for the
same source tree. **Status: met** — confirmed directly during the vision correction (`MSTR-001`
§8): a fresh build matched the checked-in `BunnyQuest.gbc` exactly.

### N5 — Test-coverage bar

The system **shall** have a full, currently-accurate automated test suite that passes before any
package is considered complete (rule G5, [`.claude/skills/README.md`](../../.claude/skills/README.md)).
**Status: not met.** `test_rom.py`'s T1 suite (header validation,
[R304](../research/encyclopedia/R304-rom-validation.md)) satisfies this NFR for the facts it
covers; its T2–T10 suites do **not** — they assert pre-rewrite game semantics against the current
code ([`BL-0006`](../pipeline/backlog.md), Critical). **The historical "88/88 passed" figure is
not evidence this NFR is met** — it predates the semantic drift and must not be cited as current
compliance. This is the most consequential non-compliance on this list: every downstream
stage-08/09 run inherits it until `BL-0006`/`BL-0008`'s remediation lands.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-05`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `test_rom.py` is consulted as the *shape* of what a test-coverage
bar should look like (suite-per-concern structure), not as current-compliance evidence for N5 —
per `GDS-02`/`GDS-05`'s established finding. `Claude.md`'s "Remaining Known Issues" section
(the un-gated score-write note) is the direct source for N2's non-compliance finding and is
**consulted as still-accurate** here (unlike most of `Claude.md`, this specific known-issues note
survived the Bunny Quest rewrite unaffected, since it describes a code-level habit, not a
game-semantics fact tied to the old zone/gift model — confirmed by the fact that `BL-0003`'s
re-scoped version, filed during the vision correction, kept the same substance). **Decision: this
level supersedes `Claude.md`'s NFR-adjacent framing** (the budget/timing/integrity facts
scattered across its sections) as the single, authoritative NFR statement, while explicitly
crediting `Claude.md`'s known-issues note as the origin of N2's finding.
