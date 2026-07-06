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

- **Updated:** 2026-07-06 (run #2)
- **Increment:** **Bootstrap baseline** — document the shipped game (**Bunny Quest**, corrected
  from run #1's stale "BunnyGarden.gbc v2.1" framing — see run #2) as-built through stages 01–07,
  verify the as-built record (09), then drive the widened BL-0001/0003/0005/0006/0007 remediation
  scope (BL-0008's umbrella) through the 07→08→09 loop. See [`BOOTSTRAP.md`](BOOTSTRAP.md).
- **Pipeline state:** Stage 01 ✅ complete, **revised this run** — MSTR-001 v2.0, GDS-00 (gate
  re-affirmed), assumptions register A1–A8. Stages 02–11 ⛔ unstarted; research tiers
  R100/R200/R300 all `⛔ Planned`.
- **Backlog:** 8 open entries. BL-0001/BL-0003 → `DEFERRED` (superseded/needs-re-scope, folded
  into BL-0008). BL-0002 → `SCHEDULED`, re-scoped (may already be fixed by commit `9a587ac` —
  check before treating as live). BL-0004 → `SCHEDULED`, widened (also archive the stale
  `BunnyGarden.gbc`). BL-0005 → `SCHEDULED`, widened (fix the ROM filename too, not just the
  path). **BL-0006 (new, Critical)** → `SCHEDULED`: `test_rom.py` tests pre-rewrite semantics: the
  **G5 permanent gate cannot currently be satisfied**. **BL-0007 (new, High)** → `SCHEDULED`:
  `Claude.md`/`memory.md`/`README.md` all describe the pre-rewrite game. **BL-0008 (new)** →
  `SCHEDULED`: umbrella entry consolidating the above into one coherent `07` remediation pass. No
  `NEW`, no formal `NEEDS-USER` gate this run (BL-0006's severity was flagged prominently to the
  user as a recommendation rather than a hard stop — proceeding with GDS/requirements authoring
  from direct code reads is not blocked by the stale test suite).
- **Next step:** `02-research-gbc-hardware` — author the R100 tier (R101–R110); still the first
  unstarted stage, and hardware facts (SM83/PPU/palettes/SRAM) are unaffected by the zone-count
  correction. R200 (game design) research, when it runs, must reflect the corrected 9-zone/C7
  world-scale facts — not the stale 3-zone framing run #1 would have fed it.
- **Open gates:** none formally raised. Recommended to the user (not a hard stop): whether to
  pull BL-0006/BL-0008 (test-suite rewrite) forward out of numeric stage order, since no
  stage-08/09 work can honestly claim G5 passes until it lands.

## Run log

| # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
|---|---|---|---|---|---|---|
| 0 | 2026-07-06 | init | — | scaffold | Pipeline scaffold committed: 18 skills, docs tree, ROADMAP, backlog seeded (BL-0001…BL-0005) | `01-vision` (bootstrap) |
| 1 | 2026-07-06 | advance | `01-vision` | bootstrap Vision layer | ✅ MSTR-001 v1.0 + GDS-00 (gate closed) + assumptions register A1–A7 authored; trackers flipped. Triage: all 5 seeded entries dispositioned `SCHEDULED`; BL-0004 user-decided (archive monolith to `legacy/`). Harvested 0 new findings. No drift. **Later found (run #2): this run trusted stale `Claude.md`/`memory.md` and described the wrong game.** | `02-research-gbc-hardware` (R100 tier) |
| 2 | 2026-07-06 | override (user-directed) | `01-vision` | deliberate vision correction + expansion | User flagged MSTR-001's zone count as wrong. Direct code inspection (tilemaps.py/asm_game.py/build_rom.py, plus a rebuilt ROM diffed byte-for-byte against checked-in `BunnyQuest.gbc`) confirmed the shipped game was fully rewritten as **Bunny Quest** (commit `679b5cf`, already on `main` before the scaffold PR merged) — 3×3 grid of 9 zones, 9-carrot win condition — which run #1 never detected because it trusted `Claude.md`/`memory.md` instead of the code. **MSTR-001 → v2.0**, **GDS-00 revised**, **assumptions register → A1–A8** (A1 reframed, A6 corrected, A8 added recording the doc/test staleness as an already-fired trigger). Added new commitment **C7**: long-term world-scale target comparable to Zelda/Pokémon, reversing the prior bank-switching non-goal. Harvested 2 new Critical/High findings (BL-0006: `test_rom.py` tests pre-rewrite semantics, G5 gate broken; BL-0007: `Claude.md`/`memory.md`/`README.md` all stale) plus BL-0008 (umbrella remediation entry); re-scoped BL-0001/0002/0003/0004/0005 against the corrected facts. Drift corrected: run #1's Position/backlog framing. | `02-research-gbc-hardware` (R100 tier; unaffected by the correction) — recommend the user weigh in on pulling BL-0006/0008 forward |
