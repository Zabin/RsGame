# Verification Reports — Index

Owned by `09-package-verification` — the only skill that may advance a package to `VERIFIED`.
One `VR-xxxx-<slug>.md` per verification run, numbered to match the package (IP-1010 → VR-1010).
A `RETURNED` result is a normal outcome, recorded here like any other.

[↑ Master Build Plan](../00-master-build-plan.md)

| VR | Package | Date | Result | Headline findings |
|---|---|---|---|---|
| [VR-9010](VR-9010-test-suite-rewrite.md) | IP-9010 (test-suite rewrite) | 2026-07-07 | **VERIFIED** | 109/109 checks pass, ROM byte-identical, all DoD/checklist items confirmed independently. One Low finding: package cites nonexistent `NFR-7000` (should be `NFR-6100`), whose RTM Test cell remains unfilled. |
| [VR-1010](VR-1010-per-zone-scoreitem-persistence.md) | IP-1010 (per-zone ScoreItem persistence) | 2026-07-07 | **VERIFIED** | 125/125 pass independently re-run (fresh container), ROM byte-identical rebuild, all 5 FS-101 ACs confirmed via T11.a–e, BL-0023 farming-bug fix proven (T11.a4/a5). One Low finding: NFR-5200's "pending independent verification" clause in RQ-02 now stale (04 delta). |
| [VR-9020](VR-9020-score-bar-vblank-fix.md) | IP-9020 (score-bar VBlank fix) | 2026-07-07 | **VERIFIED** | Sole `update_status_disp` call site confirmed at frame-top VBlank (direct read); every other VRAM writer runs LCD-off; T8.10a/b digit-timing checks pass; 125/125, ROM byte-identical. Unblocks IP-9030 → READY. One Low finding: stale "pending verification" clauses in RQ-02 NFR-1200 + GDS-06 N2 (04-delta batch). |
| [VR-9040](VR-9040-legacy-artifact-archival.md) | IP-9040 (legacy artifact archival) | 2026-07-07 | **VERIFIED** | Root clean of `BunnyGarden*`, `legacy/` holds all three artifacts + README via history-preserving `git mv`, zero live references tree-wide (all doc hits historical or already-tracked as BL-0007/BL-0027), ROM byte-identical, 125/125. No findings. |
| [VR-9030](VR-9030-root-doc-refresh.md) | IP-9030 (root documentation refresh) | 2026-07-10 | **VERIFIED** | All three root docs (`Claude.md`/`memory.md`/`README.md`) confirmed accurate against the shipped tree and GDS ladder; stale-term sweep clean; README quick-start commands actually executed (build byte-identical, 125/125 pass); WRAM pointer spot-check matches `asm_game.py` exactly. No findings — bootstrap tranche's fifth and final package now VERIFIED; `BL-0008` umbrella closes. |
| [VR-1020](VR-1020-procedural-world-generation.md) | IP-1020 (procedural world generation & item-agnostic collection) | 2026-07-10 | **VERIFIED** | 133/133 pass independently re-run (fresh container), ROM byte-identical rebuild (23660/32768 bytes), all 8 FS-102 ACs confirmed via T12.a–i + retargeted T8.7/T8.8, oracle/SM83 lockstep confirmed both by T12.b (0 mismatches, 15-entry corpus) and direct side-by-side code read, no-`DIV` determinism independently re-read. Release 2's foundational, dependency-root package now VERIFIED — unblocks `IP-1030`/`1040`/`1050`. One Medium finding: `ROADMAP.md`'s `IM-00`/`IP-xxxx` rows stale (pre-dates this run's authorization/completion), same pattern as `BL-0035`. |
