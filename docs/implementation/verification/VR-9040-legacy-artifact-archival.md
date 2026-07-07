# VR-9040 — Legacy Artifact Archival

> Verification Report for [IP-9040](../packages/IP-9040-legacy-artifact-archival.md), produced
> by `09-package-verification`. Read-only audit — no code, package, spec, or requirement was
> edited by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9040-legacy-artifact-archival.md)

## Package

- **ID / Title:** IP-9040 — Legacy Artifact Archival (`BL-0004`, under the `BL-0008` umbrella;
  executes the user's run #1 decision, scope widened run #2)
- **Commit verified:** `9191941` (tree head; implementing commit `65a24b8`,
  "chore(repo): IP-9040 — archive pre-rewrite legacy artifacts")
- **Date:** 2026-07-07
- **Independence:** clean — this session performed no implementation work.

## Result

**VERIFIED** — 0 failed checks. Both Definition of Done items and all five Verification
Checklist items confirmed with direct evidence; full suite 125/125 pass against a byte-identical
rebuilt ROM.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | Repo root contains no `BunnyGarden_*` files and no stale ROM; `legacy/` contains all three plus its README | `ls` of root: zero `BunnyGarden*` entries. `ls legacy/`: exactly `BunnyGarden.gbc`, `BunnyGarden_build_rom.py`, `BunnyGarden_logic.json`, `README.md`. README correctly describes what/why/date and cites BL-0004/IP-9040. `git log --follow` confirms history-preserving `git mv` | ✅ |
| 2 | `python3 build_rom.py` and `python3 test_rom.py` still work from the repo root | Both run this session from the root: build wrote 32768 bytes; suite 125/125 pass | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | "Wrote 32768 bytes → BunnyQuest.gbc"; T1 header suite passes | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **125/125 pass, 0 failed** — run by name this session | ✅ |
| 3 | Rebuilt ROM byte-identical to `BunnyQuest.gbc` | sha256 `673afac4…ce46` identical before/after rebuild — the package changed no game bytes | ✅ |
| 4 | Root shows no `BunnyGarden*`; `legacy/` shows exactly the three artifacts + README | Confirmed by direct `ls` both places (see DoD #1) | ✅ |
| 5 | No live (non-historical) reference to the moved paths remains | Tree-wide grep: **zero hits in any `.py` file** outside `legacy/` itself. All 14 doc/skill hits classified: pipeline/package/architecture records describing the pre-fix state or the archival itself (historical — package §7.2 says update none), plus two already-tracked stale docs: `memory.md` (BL-0007/IP-9030's scope) and `.claude/skills/run-bunnygarden/SKILL.md` (BL-0027) — both pre-existing, neither this package's scope | ✅ |

## Requirements audit

No numbered FR/NFR — repository hygiene executing a recorded user decision (run #1, widened
run #2). The RTM is correctly untouched by this package; GDS-02/GDS-03's canonical-chain
description is now literally true of the repo root (one build chain, one shipped ROM).

## Test run

```
python3 build_rom.py               → "Total used: 0x5B6C (23404 bytes of 32768)"
                                     "Wrote 32768 bytes → BunnyQuest.gbc"
sha256sum BunnyQuest.gbc           → 673afac4…ce46 — identical before/after rebuild
python3 test_rom.py                → RESULTS: 125/125 passed   0 failed
```

(PyBoy 2.7.0 headless, fresh container.)

## Scope audit

Implementing commit `65a24b8` touched: the three renames (pure `git mv` — Bin/0-line diffs,
content unchanged), new `legacy/README.md`, and the two ledger rows (Master Build Plan,
`packages/INDEX.md`). Root `README.md` untouched, per the package's own §9 fallback (its rewrite
is IP-9030's scope). **No excursions.**

## Findings

None. (The one incidental finding from this package's implementation — the `run-bunnygarden`
skill doc's stale paths — was already harvested as `BL-0027` at run #25; nothing new surfaced by
this verification.)
