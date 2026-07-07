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
