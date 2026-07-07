# Implementation Packages — Index

Owned by `07-implementation-planning`. One `IP-xxxx-<slug>.md` per unit of work, the 14-field
template (see the skill). ID scheme: `IP-<FS series>0` mirrors the FS series (FS-101 → IP-1010;
lettered slices IP-1011), bug remediations with no FS use the `IP-9xx0` series citing their
`BL-xxxx`. This index and `../00-master-build-plan.md` must never disagree.

[↑ Master Build Plan](../00-master-build-plan.md)

| Package | Title | FS / BL source | Status | Notes |
|---|---|---|---|---|
| [IP-9010](IP-9010-test-suite-rewrite.md) | Test suite rewrite (Bunny Quest semantics + portable paths) | BL-0006 + BL-0005 (BL-0008 umbrella) | READY | Awaits user G3; blocks all other packages (restores the G5 gate). |
| [IP-9020](IP-9020-score-bar-vblank-fix.md) | Score-bar VRAM write timing fix | BL-0003 (BL-0008 umbrella) | BLOCKED | Authorized (carve-out); depends on IP-9010. |
| [IP-9030](IP-9030-root-doc-refresh.md) | Root documentation refresh | BL-0007 (BL-0008 umbrella) | BLOCKED | Awaits user G3; depends on IP-9010 + IP-9020. |
| [IP-9040](IP-9040-legacy-artifact-archival.md) | Legacy artifact archival | BL-0004 (BL-0008 umbrella) | BLOCKED | Authorized (carve-out + user decision run #1); depends on IP-9010. |
| [IP-1010](IP-1010-per-zone-scoreitem-persistence.md) | Per-zone ScoreItem persistence | FS-101 / FEAT-5100 (+ BL-0023 rider) | BLOCKED | Awaits user G3; depends on IP-9010. Release 1's sole Feature. |
