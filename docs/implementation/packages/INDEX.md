# Implementation Packages — Index

Owned by `07-implementation-planning`. One `IP-xxxx-<slug>.md` per unit of work, the 14-field
template (see the skill). ID scheme: `IP-<FS series>0` mirrors the FS series (FS-101 → IP-1010;
lettered slices IP-1011), bug remediations with no FS use the `IP-9xx0` series citing their
`BL-xxxx`. This index and `../00-master-build-plan.md` must never disagree.

[↑ Master Build Plan](../00-master-build-plan.md)

| Package | Title | FS / BL source | Status | Notes |
|---|---|---|---|---|
| [IP-9010](IP-9010-test-suite-rewrite.md) | Test suite rewrite (Bunny Quest semantics + portable paths) | BL-0006 + BL-0005 (BL-0008 umbrella) | **VERIFIED** | [VR-9010](../verification/VR-9010-test-suite-rewrite.md), 2026-07-07: 109/109 pass, ROM byte-identical, all DoD/checklist items confirmed. |
| [IP-9020](IP-9020-score-bar-vblank-fix.md) | Score-bar VRAM write timing fix | BL-0003 (BL-0008 umbrella) | **VERIFIED** | Verified 2026-07-07 ([VR-9020](../verification/VR-9020-score-bar-vblank-fix.md)): frame-top call site + LCD-off discipline confirmed by direct read, T8.10a/b pass, 125/125. |
| [IP-9030](IP-9030-root-doc-refresh.md) | Root documentation refresh | BL-0007 (BL-0008 umbrella) | **VERIFIED** | Verified 2026-07-10 ([VR-9030](../verification/VR-9030-root-doc-refresh.md)): all three root docs confirmed accurate, stale-term sweep clean, quick-start commands executed, ROM byte-identical, 125/125. No findings — bootstrap tranche complete. |
| [IP-9040](IP-9040-legacy-artifact-archival.md) | Legacy artifact archival | BL-0004 (BL-0008 umbrella) | **VERIFIED** | Verified 2026-07-07 ([VR-9040](../verification/VR-9040-legacy-artifact-archival.md)): root clean, `legacy/` complete, zero live references, ROM byte-identical, 125/125. No findings. |
| [IP-1010](IP-1010-per-zone-scoreitem-persistence.md) | Per-zone ScoreItem persistence | FS-101 / FEAT-5100 (+ BL-0023 rider) | **VERIFIED** | Verified 2026-07-07 ([VR-1010](../verification/VR-1010-per-zone-scoreitem-persistence.md)): 125/125 independently re-run, all DoD/checklist confirmed, BL-0023 fix proven. Release 1's sole Feature — critical path complete. |
