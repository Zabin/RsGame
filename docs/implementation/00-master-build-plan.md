# Master Build Plan

> **Status: ♻️ live — IP-9030 `COMPLETE` 2026-07-09, awaiting `09-package-verification`.** Owned by `07-implementation-planning`
> (rows/graph/authorization state) with status transitions written by the stage-08 peers
> (`IN PROGRESS`/`COMPLETE`/`BLOCKED`) and `09-package-verification` (`VERIFIED`, exclusively).
> Status vocabulary, verbatim: `NOT STARTED / READY / IN PROGRESS / BLOCKED / COMPLETE /
> VERIFIED`. `READY` requires fully-specified **and** all dependencies `VERIFIED`. Eligibility is
> not authorization (G3 — see `.claude/skills/README.md`, including the bootstrap carve-out).

[↑ Docs index](../INDEX.md) · [Packages](packages/INDEX.md) ·
[Verification reports](verification/INDEX.md) ·
[Technical Work Breakdown](01-technical-work-breakdown.md)

## Package status table

| Package | Title | Owner (08 peer) | Status | Depends on | Authorized? | Notes |
|---|---|---|---|---|---|---|
| [IP-9010](packages/IP-9010-test-suite-rewrite.md) | Test suite rewrite (BL-0006 + BL-0005) | `08-code-implementation` | **VERIFIED** | — | **YES — explicit user G3, 2026-07-07 (BL-0024)** | **Verified 2026-07-07 ([VR-9010](verification/VR-9010-test-suite-rewrite.md)):** 109/109 pass, ROM byte-identical, all DoD/checklist items confirmed independently. One Low finding: package cites nonexistent `NFR-7000` (should be `NFR-6100`). |
| [IP-9020](packages/IP-9020-score-bar-vblank-fix.md) | Score-bar VRAM write timing fix (BL-0003) | `08-code-implementation` | **VERIFIED** | IP-9010 (VERIFIED) | **YES** — G3 bootstrap carve-out (BL-0003 ∈ BL-0001…0005) | **Verified 2026-07-07 ([VR-9020](verification/VR-9020-score-bar-vblank-fix.md)):** sole call site confirmed at frame-top VBlank, all other VRAM writers LCD-off, T8.10a/b pass, 125/125. One Low finding: stale "pending verification" clauses (04-delta batch). |
| [IP-9030](packages/IP-9030-root-doc-refresh.md) | Root documentation refresh (BL-0007) | `08-code-implementation` | **COMPLETE** | IP-9010 (VERIFIED), IP-9020 (VERIFIED) | **YES — explicit user G3, 2026-07-07 (BL-0024)** | **Implemented 2026-07-09:** `Claude.md`/`memory.md`/`README.md` refreshed to describe the shipped Bunny Quest game (9 zones, 9-carrot victory, current WRAM/SRAM/tile/palette facts pointed at GDS-07/08 rather than duplicated); stale-term sweep (gifts/88/88/BunnyGarden Adventure/3-zone) clean; ROM rebuilt byte-identical (23404/32768); full suite 125/125 (PyBoy 2.7.0 reinstalled this session). No FR/NFR coverage (doc-defect remediation only) — RTM unaffected. Awaiting `09-package-verification`. |
| [IP-9040](packages/IP-9040-legacy-artifact-archival.md) | Legacy artifact archival (BL-0004) | `08-code-implementation` | **VERIFIED** | IP-9010 (VERIFIED) | **YES** — G3 bootstrap carve-out + explicit user decision (run #1; widened scope run #2) | **Verified 2026-07-07 ([VR-9040](verification/VR-9040-legacy-artifact-archival.md)):** root clean, `legacy/` complete, history-preserving `git mv`, zero live references, ROM byte-identical, 125/125. No findings. |
| [IP-1010](packages/IP-1010-per-zone-scoreitem-persistence.md) | Per-zone ScoreItem persistence (FS-101 / FEAT-5100) | `08-code-implementation` | **VERIFIED** | IP-9010 (VERIFIED) | **YES — explicit user G3, 2026-07-07 (BL-0024)** | **Verified 2026-07-07 ([VR-1010](verification/VR-1010-per-zone-scoreitem-persistence.md)):** 125/125 pass independently re-run, ROM byte-identical rebuild, all DoD/checklist items confirmed, BL-0023 fix proven (T11.a4/a5). One Low finding: NFR-5200's "pending independent verification" clause now stale (04 delta). |

## Dependency graph

```mermaid
graph TD
    IP9010["IP-9010 test-suite rewrite<br/>(VERIFIED)"]
    IP9020["IP-9020 score-bar VBlank fix<br/>(VERIFIED)"]
    IP9030["IP-9030 root-doc refresh<br/>(COMPLETE)"]
    IP9040["IP-9040 legacy archival<br/>(VERIFIED)"]
    IP1010["IP-1010 ScoreItem persistence<br/>(Release 1, VERIFIED)"]
    IP9010 --> IP9020
    IP9010 --> IP9040
    IP9010 --> IP1010
    IP9020 --> IP9030
```

## Critical path & parallel opportunities

- **Critical path (Release 1, per FP-04):** IP-9010 → IP-1010.
- IP-9010 is `VERIFIED` (2026-07-07, [VR-9010](verification/VR-9010-test-suite-rewrite.md)) —
  the G5 gate is confirmed functional by independent re-run (109/109 pass, ROM byte-identical).
- IP-9020 is `VERIFIED` (2026-07-07, [VR-9020](verification/VR-9020-score-bar-vblank-fix.md)) —
  `IP-9030`'s last blocking dependency; `IP-9030` is now `COMPLETE`, implemented 2026-07-09.
- IP-9040 is `VERIFIED` (2026-07-07, [VR-9040](verification/VR-9040-legacy-artifact-archival.md))
  — no downstream package depends on it.
- **IP-1010 is `VERIFIED` (2026-07-07, [VR-1010](verification/VR-1010-per-zone-scoreitem-persistence.md))
  — Release 1's critical path (IP-9010 → IP-1010) is complete end-to-end.**
- **All five packages have now been implemented.** Four are `VERIFIED` (IP-9010, IP-9020,
  IP-9040, IP-1010); the fifth, `IP-9030` (root-doc refresh), is `COMPLETE` — implemented
  2026-07-09, ROM byte-identical, 125/125 — and is the sole package awaiting
  `09-package-verification`.
- **Authorization state summary:** all five packages authorized — IP-9020/IP-9040 via the G3
  bootstrap carve-out; IP-9010/IP-9030/IP-1010 via the user's explicit go-ahead recorded
  2026-07-07 (`BL-0024`, "Authorize all three"). Execution order remains dependency-driven.
