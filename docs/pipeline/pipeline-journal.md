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

- **Updated:** 2026-07-06 (run #0 — scaffold initialization; no manager run has executed yet)
- **Increment:** **Bootstrap baseline** — document the shipped game (BunnyGarden.gbc v2.1) as-built
  through stages 01–07, verify the as-built record (09), then drive the five scaffold-time backlog
  items (BL-0001…BL-0005) through the 07→08→09 remediation loop. See
  [`BOOTSTRAP.md`](BOOTSTRAP.md) for the full run order.
- **Pipeline state:** every stage ⛔ unstarted. The docs tree is scaffold-only (all indexes
  `⛔ Planned`); the code tree ships a working, 88/88-tested v2.1 game.
- **Backlog:** 5 open entries (BL-0001…BL-0005), all `NEW`, filed at scaffold time — triage them
  on the first advance. BL-0004 will likely need a user decision (see the backlog row).
- **Next step:** `01-vision` (bootstrap mode) — author MSTR-001 + GDS-00 + the strategic
  assumptions register from the shipped game; the top of the ladder must exist before anything
  downstream.
- **Open gates:** none yet. Expected later: the user's GO at stage 11 (G4), and G3 authorization
  for any package outside the bootstrap carve-out.

## Run log

| # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
|---|---|---|---|---|---|---|
| 0 | 2026-07-06 | init | — | scaffold | Pipeline scaffold committed: 18 skills, docs tree, ROADMAP, backlog seeded (BL-0001…BL-0005) | `01-vision` (bootstrap) |
