# Pipeline Journal

> **Maintained by the `00-pipeline-manager` skill — single writer.** Humans and other sessions
> read this file; only the manager writes it. It is the manager's persistent memory of where the
> documentation-driven-development pipeline stands (see
> [`.claude/skills/README.md`](../../.claude/skills/README.md) for the pipeline itself). It is a
> **cache of truth, never truth**: the tree's ledgers (`ROADMAP.md`, the Master Build Plan, the
> per-theme indexes) are authoritative, and every manager run reconciles this file against them —
> where they disagree, the tree wins and the correction is logged below.

[↑ Docs index](../INDEX.md) · [Pipeline README](../../.claude/skills/README.md) ·
[Bootstrap run-book](BOOTSTRAP.md) ·
[Master Build Plan](../implementation/00-master-build-plan.md) · [ROADMAP](../../ROADMAP.md)

## Position

- **Updated:** 2026-07-06 (run #3)
- **Increment:** **Bootstrap baseline** — document the shipped game (**Bunny Quest**) as-built
  through stages 01–07, verify the as-built record (09), then drive the widened
  BL-0001/0003/0005/0006/0007 remediation scope (BL-0008's umbrella) through the 07→08→09 loop.
  See [`BOOTSTRAP.md`](BOOTSTRAP.md).
- **Pipeline state:** Stage 01 ✅ complete (MSTR-001 v2.0, GDS-00, assumptions register A1–A8).
  **Stage 02 tier R100 ✅ complete this run** — R101–R110 authored. R200/R300 tiers still
  `⛔ Planned`. Stages 03–11 ⛔ unstarted.
- **Backlog:** 10 open entries (8 SCHEDULED/DEFERRED carried from run #2, unchanged, plus 2 new
  this run). **BL-0009 (new, Medium)** → `SCHEDULED`: R104 found the CGB's 8 BG/8 OBJ palette
  budget is already at/near its ceiling with 9 zones — a real constraint on MSTR-001 C7's
  world-scale target that GDS-01/GDS-08 must state explicitly. **BL-0010 (new, Low)** →
  `DEFERRED`: `docs/research/INDEX.md`'s R201 row still says "gifts→victory shape" (stale wording,
  out of this skill's write scope — R200 territory); trigger is the next
  `02-research-game-design` run. No `NEW`, no gate.
- **Next step:** either sibling research tier — `02-research-game-design` (R200) or
  `02-research-tooling-and-testing` (R300); both are peers with no ordering between them. Given
  BL-0006/BL-0008's still-open recommendation (test-suite rewrite), `02-research-tooling-and-
  testing`'s R305 (emulator-based test design) is arguably the more useful next tier to close
  first, since it will directly ground *how* `test_rom.py` should be rewritten — recommend running
  that one next unless the user has a different priority.
- **Open gates:** none formally raised. Still recommended to the user (unchanged from run #2):
  whether to pull BL-0006/BL-0008 (test-suite rewrite) forward out of numeric stage order.

## Run log

| # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
|---|---|---|---|---|---|---|
| 0 | 2026-07-06 | init | — | scaffold | Pipeline scaffold committed: 18 skills, docs tree, ROADMAP, backlog seeded (BL-0001…BL-0005) | `01-vision` (bootstrap) |
| 1 | 2026-07-06 | advance | `01-vision` | bootstrap Vision layer | ✅ MSTR-001 v1.0 + GDS-00 (gate closed) + assumptions register A1–A7 authored; trackers flipped. Triage: all 5 seeded entries dispositioned `SCHEDULED`; BL-0004 user-decided (archive monolith to `legacy/`). Harvested 0 new findings. No drift. **Later found (run #2): this run trusted stale `Claude.md`/`memory.md` and described the wrong game.** | `02-research-gbc-hardware` (R100 tier) |
| 2 | 2026-07-06 | override (user-directed) | `01-vision` | deliberate vision correction + expansion | User flagged MSTR-001's zone count as wrong. Direct code inspection (tilemaps.py/asm_game.py/build_rom.py, plus a rebuilt ROM diffed byte-for-byte against checked-in `BunnyQuest.gbc`) confirmed the shipped game was fully rewritten as **Bunny Quest** (commit `679b5cf`, already on `main` before the scaffold PR merged) — 3×3 grid of 9 zones, 9-carrot win condition — which run #1 never detected because it trusted `Claude.md`/`memory.md` instead of the code. **MSTR-001 → v2.0**, **GDS-00 revised**, **assumptions register → A1–A8** (A1 reframed, A6 corrected, A8 added recording the doc/test staleness as an already-fired trigger). Added new commitment **C7**: long-term world-scale target comparable to Zelda/Pokémon, reversing the prior bank-switching non-goal. Harvested 2 new Critical/High findings (BL-0006: `test_rom.py` tests pre-rewrite semantics, G5 gate broken; BL-0007: `Claude.md`/`memory.md`/`README.md` all stale) plus BL-0008 (umbrella remediation entry); re-scoped BL-0001/0002/0003/0004/0005 against the corrected facts. Drift corrected: run #1's Position/backlog framing. | `02-research-gbc-hardware` (R100 tier; unaffected by the correction) — recommend the user weigh in on pulling BL-0006/0008 forward |
| 3 | 2026-07-06 | advance | `02-research-gbc-hardware` | R100 tier (R101–R110) | ✅ All ten topics authored (SM83 opcodes, PPU/VRAM/OAM timing, LCDC/STAT, CGB palettes, OAM/DMA, MBC1/SRAM, joypad, APU, header/checksums, interrupts), cited to Pan Docs + direct code reads; index + ROADMAP flipped. Confirmed by direct code read: the SRAM enable/disable bracketing is already correct (R106, no defect). Harvested 2 new findings: **BL-0009** (Medium) — CGB's 8-palette budget is already near its ceiling at 9 zones, a real constraint on C7's world-scale target; **BL-0010** (Low, DEFERRED) — stale "gifts" wording in the R201 index row, out of this skill's scope to fix. No drift. | Either `02-research-game-design` or `02-research-tooling-and-testing` (peers) — recommend R300 first (grounds the test-suite rewrite BL-0006/0008 need) |
