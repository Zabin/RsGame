# Master Build Plan

> **Status: ✅ Bootstrap tranche fully VERIFIED (2026-07-10) — all five packages VERIFIED.**
> **Release 2 tranche (procgen-world increment): authorized 2026-07-10 (user G3, `BL-0040`, all
> five packages) — `IP-1020` (foundational, dependency-root) VERIFIED 2026-07-10
> ([VR-1020](verification/VR-1020-procedural-world-generation.md)); `IP-1030` (critical-path,
> code half) VERIFIED 2026-07-10 ([VR-1030](verification/VR-1030-generated-region-screen-composition-code.md)),
> which unblocked `IP-1031` (critical-path, content half) to `COMPLETE` 2026-07-11 — the
> tranche's critical path (`IP-1020`→`IP-1030`→`IP-1031`) is now fully implemented end-to-end;
> `IP-1040`/`IP-1050` both VERIFIED 2026-07-11
> ([VR-1040](verification/VR-1040-main-menu-new-game-flow.md),
> [VR-1050](verification/VR-1050-generated-world-save-persistence.md)). **`IP-1031` independently
> verified 2026-07-12 ([VR-1031](verification/VR-1031-generated-region-screen-composition-content.md))**
> — 231/231 pass, exact 5-family mapping and zero-new-art/palette claims both confirmed. **All
> five Release-2 packages now `VERIFIED`.** **Post-ship remediation tranche planned
> 2026-07-11** (`IP-9050`/`IP-9060`/`IP-9070`, five bugs from playtesting — see below) — **all
> three packages authorized 2026-07-11 (user G3, `BL-0062`); all three reached `COMPLETE` the
> same session (implementer independence required before any can reach `VERIFIED`). **`IP-9070`
> independently verified 2026-07-12 ([VR-9070](verification/VR-9070-cur-zone-indexed-structures-generalization.md))**
> — 231/231 pass, `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` relocation and `ZONE_COLLECTS` biome-keyed
> lookup both confirmed. **`IP-9050` independently verified 2026-07-12
> ([VR-9050](verification/VR-9050-generated-world-navigation-fix.md))** — 231/231 pass,
> `check_zone_transition` confirmed fully `REGION_GRAPH`-driven via the shared `czt_region_hl`
> subroutine. **`IP-9060` independently verified 2026-07-12
> ([VR-9060](verification/VR-9060-main-menu-cursor-fix.md))** — 231/231 pass, `MM_CURSOR`
> reset confirmed correctly relocated and gated on genuine state entry. **This closes the
> post-ship remediation tranche end-to-end — all three packages (`IP-9050`/`9060`/`9070`) now
> `VERIFIED`.** **Maze-
> shaped region adjacency tranche planned 2026-07-11** (`IP-1070`/`IP-1080`, `FS-107`/`FS-108`
> logic half, `ADR-0012`) — a first `08-code-implementation` attempt hit a Blocking Report (the
> shipped PRNG collapses under the braid pass's many back-to-back draws), root-caused by `R113`
> and resolved by `ADR-0013` (a loop-local counter-XOR perturbation scoped to `IP-1070`'s own
> carve+braid draws, `gw_prng_step` itself untouched) — a second `08-code-implementation` attempt
> implemented the fix and reached **`IP-1070` → `COMPLETE` 2026-07-11**, full 211/211-check suite
> green (new suite `T19`, plus non-regression fixes to `T11`/`T17`'s own hardcoded full-lattice
> traversal assumptions — a genuine supersession-sweep gap this package's own planning missed).
> **`IP-1070` independently verified 2026-07-12 ([VR-1070](verification/VR-1070-maze-shaped-region-adjacency.md))** —
> 226/226 pass (current suite size), all seven FS-107 ACs confirmed, oracle/SM83 lockstep
> reconfirmed, zero-diff scope on `dsr_p`/`draw_region_arrows`/`check_zone_transition` confirmed.
> **`IP-1080` authorized 2026-07-12** (explicit user G3, `BL-0083`, "IP-1080 approved") and
> **implemented the same day — reached `COMPLETE`, 230/230 checks pass** (new suite T20 a–d).
> **`IP-1080` independently verified 2026-07-12
> ([VR-1080](verification/VR-1080-maze-aware-edge-classification.md))** — 231/231 pass, `DRA_ROW`/
> `DRA_COL` re-derivation and open-edge-unchanged claims both confirmed. **This closes the
> maze-shaped region adjacency tranche's full critical path — both packages (`IP-1070`/`1080`)
> now `VERIFIED`.**
> Material drift found in the package's own §6/§7 (a stale citation claiming `check_zone_
> transition` still performs row/col grid arithmetic — `IP-9050` removed that) worked around by
> correcting the citation, not routed around; two new transient WRAM bytes (`DRA_ROW`/`DRA_COL`)
> added mid-implementation after `TMP1` was found, via a real failing test, to collide with
> `handle_play_input`'s own per-frame flag. `FS-108`'s rendering half remains unplanned (its own
> blocking `GDS-08` delta landed, `BL-0068` closed, but the rendering half's own spec is a future
> `06-feature-specification` task; AC-4 stays explicitly open). **Movement/pickup/UI bug-remediation
> tranche planned 2026-07-11** (`IP-9080`/`IP-9090`/`IP-9100`, four standing backlog bugs —
> `BL-0049`/`0051`/`0052`/`0053` — see below), all three authorized 2026-07-11 (user G3, `BL-0072`)
> — **all three now `COMPLETE` 2026-07-11 — the tranche's full extent is implemented end-to-end.**
> `IP-9090`: 213/213 suite passing, exact-boundary fix to `handle_play_input`'s UP/RIGHT clamps.
> `IP-9100`: 217/217 suite passing, `check_collisions`' pickup hitbox corrected to a true
> point-in-box test — the package's own originally-planned symmetric-threshold formula was found
> wrong during implementation (verified against `BL-0053`'s own reproduction data) and replaced
> with the correct asymmetric unsigned-range test. `IP-9080`: 220/220 suite passing, content-only
> on-screen label added for the SAVE screen's previously-silent third option. **All three
> independently verified 2026-07-12** ([VR-9080](verification/VR-9080-save-screen-third-option-labeling.md),
> [VR-9090](verification/VR-9090-movement-clamp-boundary-fix.md),
> [VR-9100](verification/VR-9100-collectible-pickup-hitbox-fix.md)) — 231/231 pass each, **the
> movement/pickup/UI bug-remediation tranche is now fully `VERIFIED`.** **`gw_prng_step`
> mixing-step repair planned AND implemented 2026-07-11** (`IP-9110`, `BL-0074`/`ADR-0014`) — a
> much larger defect than first reported: the shipped PRNG degenerated for effectively every seed
> (100% of 2000 tested), not just the literal default (`SEED=0`); at `scale=9`, 55% of seeds
> already produced a majority-Water world. `ADR-0014` confirmed the `7,9,8` shift-triplet repair as
> the correct fix and the user explicitly authorized shipping it ("Yes, ship the fix (Recommended),"
> in direct, specific response to a question naming the exact save-compatibility consequence) —
> **`IP-9110` reached `COMPLETE` 2026-07-11**, 222/222 suite passing, `SAVE_VERSION_VAL` bumped
> `0x03`→`0x04`, `T12.j`/`T12.k` confirm the fix directly (mean Water fraction 15.6% at `scale=9`,
> down from ~46%). **Independently verified 2026-07-12
> ([VR-9110](verification/VR-9110-gw-prng-step-mixing-step-repair.md))** — 231/231 pass, the
> `7,9,8` triplet and lockstep oracle mirror both confirmed, plus this run's own live PyBoy
> re-check of the pre-upgrade save-exclusion behavior. **`IP-9110` now `VERIFIED`.** **`RIGHT
> zone-transition threshold fix planned AND implemented 2026-07-12`** (`IP-9120`, `BL-0076`) — a
> Critical regression from `IP-9090`'s own commit: the corrected RIGHT movement clamp (max
> `X=152`) fell below `check_zone_transition`'s own RIGHT-edge trigger (`X>=156`), breaking every
> rightward zone transition in every generated world. Authorized (user G3, `BL-0077`, "Yes, ship
> the fix"), reached `COMPLETE` 2026-07-12 (224/224 suite passing) — rightward navigation
> restored, directly re-verified at `BL-0076`'s own original reproduction point. **Independently
> verified 2026-07-12** ([VR-9120](verification/VR-9120-right-zone-transition-threshold-fix.md))
> — 231/231 pass. **`IP-9120` now `VERIFIED`.** **Zone-transition
> intent gate planned AND implemented 2026-07-12** (`IP-9130`, `BL-0078`) — `check_zone_transition`'s
> own position-only trigger produced spurious transitions (reachable now that the maze pass makes
> open/blocked vary per-region); gated all four branches on `JOY_CUR`. Authorized (user G3,
> `BL-0079`), **reached `COMPLETE` 2026-07-12** (226/226 suite passing) — directly re-verified at
> `BL-0078`'s own exact reported sequence. Owned by
> `07-implementation-planning`
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
| [IP-9030](packages/IP-9030-root-doc-refresh.md) | Root documentation refresh (BL-0007) | `08-code-implementation` | **VERIFIED** | IP-9010 (VERIFIED), IP-9020 (VERIFIED) | **YES — explicit user G3, 2026-07-07 (BL-0024)** | **Verified 2026-07-10 ([VR-9030](verification/VR-9030-root-doc-refresh.md)):** all three root docs confirmed accurate against the shipped tree and GDS ladder, stale-term sweep clean, README quick-start commands actually executed (byte-identical build, 125/125), WRAM pointer spot-check matches `asm_game.py`. No findings — bootstrap tranche complete. |
| [IP-9040](packages/IP-9040-legacy-artifact-archival.md) | Legacy artifact archival (BL-0004) | `08-code-implementation` | **VERIFIED** | IP-9010 (VERIFIED) | **YES** — G3 bootstrap carve-out + explicit user decision (run #1; widened scope run #2) | **Verified 2026-07-07 ([VR-9040](verification/VR-9040-legacy-artifact-archival.md)):** root clean, `legacy/` complete, history-preserving `git mv`, zero live references, ROM byte-identical, 125/125. No findings. |
| [IP-1010](packages/IP-1010-per-zone-scoreitem-persistence.md) | Per-zone ScoreItem persistence (FS-101 / FEAT-5100) | `08-code-implementation` | **VERIFIED** | IP-9010 (VERIFIED) | **YES — explicit user G3, 2026-07-07 (BL-0024)** | **Verified 2026-07-07 ([VR-1010](verification/VR-1010-per-zone-scoreitem-persistence.md)):** 125/125 pass independently re-run, ROM byte-identical rebuild, all DoD/checklist items confirmed, BL-0023 fix proven (T11.a4/a5). One Low finding: NFR-5200's "pending independent verification" clause now stale (04 delta). |
| [IP-1020](packages/IP-1020-procedural-world-generation.md) | Procedural world generation & item-agnostic collection (FS-102 / FEAT-9000) | `08-code-implementation` | **VERIFIED** | IP-9010/9020/9030/9040/1010 (all VERIFIED) | **YES — explicit user G3, 2026-07-10 (BL-0040)** | **Verified 2026-07-10 ([VR-1020](verification/VR-1020-procedural-world-generation.md)):** 133/133 pass independently re-run (fresh container), ROM byte-identical rebuild (23660/32768 bytes), all 8 FS-102 ACs confirmed (T12.a–i + retargeted T8.7/T8.8), oracle/SM83 lockstep confirmed both by T12.b and direct side-by-side code read. `check_collisions`/`setup_zone_collects` generalized to `KEYITEM_FLAGS`/`KEYITEM_COUNT`, orphaning `CARROT_FLAGS` (companion fix to `update_map_hearts`/`st_intro`/`st_victory` confirmed necessary, not scope creep). `save_to_sram`/`try_load_save` deliberately untouched — `IP-1050`'s scope. This tranche's foundational package (critical path root) — `IP-1030`/`1040`/`1050` now `READY`. One Medium finding: `ROADMAP.md`'s `IM-00`/`IP-xxxx` rows stale (pre-dates this run). |
| [IP-1030](packages/IP-1030-generated-region-screen-composition-code.md) | Generated-region screen composition — code (FS-103 / FEAT-4100) | `08-code-implementation` | **VERIFIED** | IP-1020 (VERIFIED) | **YES — explicit user G3, 2026-07-10 (BL-0040)** | **Verified 2026-07-10 ([VR-1030](verification/VR-1030-generated-region-screen-composition-code.md)):** 180/180 pass on current tree head (IP-1030's own T13: 3/3), ROM byte-identical rebuild, both FS-103 ACs confirmed (T13.a tile-family audit, T13.b call-site audit), `_zone_arrows` retirement + scale=3 arrow-placement regression confirmed byte-for-byte (T13.c). `ALL_SCREENS` generalized from 14 fixed entries to 5 biome-family representatives (water→lake, sand→beach, grass→forest, stone→mountain, brick→castle — GDS-07's existing terrain-family/palette grouping; IP-1031 may revise, a one-line change) + 5 UI screens. Critical-path package — unblocks `IP-1031` to `READY`. No new findings. |
| [IP-1031](packages/IP-1031-generated-region-screen-composition-content.md) | Generated-region screen composition — content (FS-103 / FEAT-4100) | `08-content-authoring` | **VERIFIED** | IP-1020 (VERIFIED), IP-1030 (VERIFIED) | **YES — explicit user G3, 2026-07-10 (BL-0040)** | **Verified 2026-07-12 ([VR-1031](verification/VR-1031-generated-region-screen-composition-content.md)): independently confirmed** — 231/231 pass (current suite size, up from 180/180 at implementation time), ROM byte-identical rebuild, `ALL_SCREENS`'s exact 5-family mapping confirmed by direct read, `tiles.py`/`build_rom.py` palette tables confirmed diff-clean since `IP-1030`'s own commit (zero new art/palette entries), `T13.a` tile-family audit and the pre-existing independent content review (`content-review-IP-1031.md`, clean, one Low informational finding) both confirm no cross-family tile leakage. **This closes Release 2's full package set — all five (`IP-1020`/`1030`/`1031`/`1040`/`1050`) now `VERIFIED`.** One Low finding: `FR-4300` not yet promoted to the global RTM (pre-existing gap). **Confirmation package, not new authorship:** `IP-1030`'s own commit (`3479dba`) already wired all 5 `(family_name, fn)` pairs this package specifies (Water→`lake_screen`, Sand→`beach_screen`, Grass→`forest_screen`, Stone→`mountain_screen`, Brick→`castle_screen`) directly into `ALL_SCREENS` as its default representative choice — `tilemaps.py` required zero further edits. This run independently confirmed the DoD: `tiles.py`/`build_rom.py` palette tables diff-clean (zero new art/palette entries), each family's tile-index usage falls within its own 8-tile-aligned block (IP-1030's own T13.a passes, no cross-family leakage), ROM rebuilds byte-identical (22344/32768 bytes), full suite 180/180. Rendered and screenshotted all 5 family screens in PyBoy (via `force_region_redraw`, mirroring T13.a's own method) — all read cleanly, correct family tiles/labels. Docs updated: GDS-08 §8 confirming note, FS-103 metadata. **Outstanding Issue:** the 07→08 package split assumed content work remained; in practice IP-1030's code-half package delivered the content mapping as an inherent side effect of generalizing `ALL_SCREENS`, since a working default had to be chosen to keep the code buildable/testable. Future packages splitting "code" from "content" across a data structure's *default values* should flag this coupling risk at planning time. First package `FEAT-6100`'s standard applies to (via a future `09-content-review` pass). |
| [IP-1040](packages/IP-1040-main-menu-new-game-flow.md) | Main menu & new-game flow (FS-104 / FEAT-1100) | `08-code-implementation` | **VERIFIED** | IP-1020 (VERIFIED) | **YES — explicit user G3, 2026-07-10 (BL-0040)** | **Verified 2026-07-11 ([VR-1040](verification/VR-1040-main-menu-new-game-flow.md)):** 180/180 pass (T14 sub-total 20/20), ROM byte-identical, all 6 FS-104 ACs confirmed, auto-load bypass confirmed genuinely retired (sole `try_load_save` call site), B-cancel writes nothing, exit-to-main-menu reuses the exact save-write routine, FR-9110 immutability holds under a systematic sweep. Two Low findings: stale "163/163" snapshot counts (corrected), commit message undercounted T14's own check count (cosmetic). Two new states (`GS_MAIN_MENU`, `GS_SEED_SCALE_ENTRY`) added; boot's unconditional `try_load_save` call replaced with an unconditional transition to `GS_MAIN_MENU` — retiring FR-1120's auto-load bypass (confirmed by direct code read: exactly one `try_load_save` call site remains, MAIN MENU's "continue" action). New `check_save_valid` probes magic+version (stricter than `try_load_save`'s own magic-only gate — ADR-0010: a version-mismatched save is absent for "continue" purposes). Digit-cursor SEED/SCALE ENTRY: 5 independent decimal digits + scale, composed into the real 16-bit `SEED` via saturating repeated-addition (`sse_compose_seed`, no general multiply needed) on A-confirm; B cancels to MAIN MENU without writing `SEED`/`WORLD_SCALE` (resolves FS-104 OQ1). D-pad up/down toggles MAIN MENU's highlighted option (resolves OQ2). `st_save` gains a third SELECT option (exit-to-main-menu, reuses `save_to_sram` verbatim); `st_victory`'s A-target changes to MAIN MENU. Two new screens (`main_menu_screen`/`seed_scale_entry_screen`, `tilemaps.py`) + 2 new `patches` pairs. **Cascading regression fixes** (the new boot flow ripples through every test that reaches PLAYING): `advance_to_playing` rewritten for the 3-step MAIN MENU→SEED/SCALE ENTRY→INTRO flow; T4/T5/T10/T11 updated for MAIN MENU replacing TITLE, the retired auto-load bypass (T10.6/T11.b3 now explicitly select "continue"), and ADR-0010's stricter pre-upgrade-save handling (T11.d1–d3 rewritten — a version-mismatched save no longer auto-loads at all, confirmed by `T11.d1b`). New suite **T14** (a–e, 20 checks — VR-1040 corrected the implementing commit's own "15 checks" undercount) added — package template named it "T13"; renumbered since IP-1030 claimed T13 earlier this tranche. ROM: 22344/32768 bytes (+3072 from IP-1030's 19272, ~10.2KB headroom remains). Parallel-eligible with IP-1030/1031/1050 — implemented independently of IP-1030's own COMPLETE state. |
| [IP-1050](packages/IP-1050-generated-world-save-persistence.md) | Generated-world save persistence (FS-105 / FEAT-5300) | `08-code-implementation` | **VERIFIED** | IP-1020 (VERIFIED) | **YES — explicit user G3, 2026-07-10 (BL-0040)** | **Verified 2026-07-11 ([VR-1050](verification/VR-1050-generated-world-save-persistence.md)):** 180/180 pass (T15: 17/17, matching the implementing commit's own count exactly), ROM byte-identical, both FS-105 ACs confirmed, single MBC1 bracket preserved, `REGION_GRAPH` confirmed never persisted, legacy fields round-trip, pre-upgrade saves cleanly rejected. No findings. Second save-format version bump since ship (`0x01`→`0x02`), extending IP-1010's exact pattern (a strictly monotonic sequence — a future extension must bump to `0x03`). `save_to_sram`/`try_load_save` extended with `SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS` (81 bytes, via the existing `memcpy` subroutine rather than an unrolled loop) inside the existing single MBC1 bracket. `try_load_save`'s version-2 branch restores `SEED`/`WORLD_SCALE`, calls `IP-1020`'s `generate_world` to regenerate `REGION_GRAPH` (never itself persisted — confirmed by direct diff, T15.d), then restores `KEYITEM_FLAGS` onto the freshly-regenerated graph. `IP-1040`'s `check_save_valid`/`try_load_save` automatically consume the bumped version value via the shared `SAVE_VERSION_VAL` symbolic constant — zero code changes needed there; a version-1 save is now excluded from "continue" entirely. New suite **T15** (a–d, 17 checks) added — package template named it "T14"; renumbered since IP-1040 claimed T14 earlier this tranche. `T14.e1`'s static write-site audit (IP-1040) widened to also exclude `try_load_save`'s legitimate restore block. ROM: 22344/32768 bytes (unchanged after 0x100-boundary code padding; ~10.4KB headroom remains). Parallel-eligible with IP-1030/1031/1040 — implemented independently of both. |
| [IP-9070](packages/IP-9070-cur-zone-indexed-structures-generalization.md) | `CUR_ZONE`-indexed structure generalization (BL-0058 + BL-0059) | `08-code-implementation` | **VERIFIED** | IP-1020 (VERIFIED), IP-1030 (VERIFIED), IP-1040 (VERIFIED), IP-1050 (VERIFIED) | **YES — explicit user G3, 2026-07-11 (BL-0062)** | **Verified 2026-07-12 ([VR-9070](verification/VR-9070-cur-zone-indexed-structures-generalization.md)): independently confirmed** — 231/231 pass (current suite size, up from 193/193 at implementation time), ROM byte-identical rebuild, `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` relocation confirmed non-overlapping against every neighboring constant, `ZONE_COLLECTS`'s biome-keyed lookup confirmed (T16.a–e), driven at non-default region indices (up to 80, scale=7). One Low finding: RTM's `FR-5220` row not updated for this package (routed to a future `07` pass). **Implementation Summary (2026-07-11).** Files Modified: `asm_game.py` (`SCOREITEM_FLAGS` relocated `0xC060`→`0xC286`, widened 9→81 bytes; `SRAM_SCOREITEM` relocated `0xA013`→`0xA070`, widened 9→81 bytes; `SAVE_VERSION_VAL` `0x02`→`0x03`; `st_intro`/`st_victory` clear loops widened to 81 bytes; `save_to_sram`/`try_load_save` converted to 81-byte `memcpy` transfers; `setup_zone_collects` rewritten to read `REGION_GRAPH`'s biome-id and index `zc_table` by it, not `CUR_ZONE`), `tilemaps.py` (`ZONE_COLLECTS` reduced 9→5 biome-family lists, docstring corrected), `test_rom.py` (T1.10 fixed; T8/T11/T15 hardcoded-position fixes for the Forest-list region-0 default; new suite **T16 a–e**, 13 checks; stale pre-relocation `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` test constants corrected to the real new addresses — a latent gap where T11.d2/T15.c5-6 had been passing against the wrong WRAM location). Files Created: none. Tests Added: T16.a (bounds/BL-0058 regression), T16.b (biome-keyed lookup/BL-0059 regression), T16.c (save-format v3 round-trip incl. region 80), T16.d (pre-upgrade rejection, version-2 fixture), T16.e (legacy-field regression at scale=7). Tests Passed: 193/193 (up from 180/180; ROM 22216/32768 bytes, down from 22344 — net WRAM/ROM layout change, zero code-size regression). Requirements Implemented: FR-5220 generalization, `BL-0058`/`BL-0059` fixes. Documentation Updated: GDS-07 §2/§3 tables + new §7a, GDS-08 §8 extension, `memory.md` collectible quick-ref, NFR-4200 (SRAM half MET), NFR-5300 (third version bump). Traceability Updated: this row. Outstanding Issues: none — `IP-9050` (`BL-0047`'s own fix) is the dependent package this unblocks. Discovered by `BL-0047`'s own mandatory supersession sweep. |
| [IP-9050](packages/IP-9050-generated-world-navigation-fix.md) | Generated-world navigation fix (BL-0047) | `08-code-implementation` | **VERIFIED** | IP-9070 (VERIFIED), IP-1020 (VERIFIED), IP-1030 (VERIFIED) | **YES — explicit user G3, 2026-07-11 (BL-0062)** | **Verified 2026-07-12 ([VR-9050](verification/VR-9050-generated-world-navigation-fix.md)): independently confirmed** — 231/231 pass (current suite size, up from 213/213 at implementation time), ROM byte-identical rebuild, `check_zone_transition` confirmed fully `REGION_GRAPH`-driven via the shared `czt_region_hl` subroutine (addressing identical to `dsr_p`'s own, zero hardcoded `CUR_ZONE` arithmetic remains), `T17.a`/`T17.b` confirmed passing at both a genuine scale=5 world (25/25 regions reached via real button-driven navigation) and the scale=3 regression. No findings — the RIGHT-threshold value now reading `152` instead of the package's own originally-cited `156` is expected, already-documented drift from the later `IP-9120` package, not a defect here. **Implementation Summary (2026-07-11).** Files Modified: `asm_game.py` (`check_zone_transition` fully rewritten — new shared `czt_region_hl` subroutine computes `HL = REGION_GRAPH + CUR_ZONE*5` mirroring `dsr_p`'s own addressing exactly; all four edge-branches now read a `REGION_GRAPH` neighbor byte, `0xFF` = blocked, otherwise `CUR_ZONE` ← the neighbor byte's own value directly — zero hardcoded `CUR_ZONE` literal comparisons/arithmetic remain; the pre-fix cascade control-flow, kept bit-for-bit, per `T17.b`'s scale=3 regression), plus companion fix `BL-0063` (`KEYITEM_FLAGS`'s `st_intro`/`st_victory` clear loops widened 9→81 bytes — found incidental to this package's own supersession sweep, folded in as same-package scope per the finding's own note), `test_rom.py` (retired **T9** entirely, replaced by new suite **T17 a–d**, 24 checks — `T17.b` is `T9`'s own 14 checks renamed/relocated, bit-for-bit unchanged). Files Created: none. Tests Added: T17.a (scale=5, 25-region full-world traversal via real button-driven navigation, oracle-cross-checked — the direct `BL-0047` regression test), T17.b (scale=3 regression, `T9`'s retired checks), T17.c (boundary halt at a genuine generated-world edge, not an assumed `CUR_ZONE` value), T17.d (entry-position correctness, folded into T17.a's own per-step assertions). Tests Passed: 213/213 (up from 205/205; ROM unchanged at 22216/32768 bytes). Requirements Implemented: `FR-2300`/`FR-2310` (forward-pointer notes only, per this package's own SHALL-NOT-modify-requirements scope — `BL-0061` routes the actual text generalization upstream). Documentation Updated: GDS-04 (`Region` adjacency confirmed navigation-driven, completing `ADR-0009` Decision point 1), FR-2300/FR-2310 Notes fields, RTM Test cells (now cite `T17`, superseding `T9`). Traceability Updated: this row. Outstanding Issues: none — the tranche's critical path (`IP-9070`→`IP-9050`) is now fully implemented end-to-end. |
| [IP-9060](packages/IP-9060-main-menu-cursor-fix.md) | Main menu cursor fix (BL-0048) | `08-code-implementation` | **VERIFIED** | IP-1040 (VERIFIED) | **YES — explicit user G3, 2026-07-11 (BL-0062)** | **Verified 2026-07-12 ([VR-9060](verification/VR-9060-main-menu-cursor-fix.md)): independently confirmed** — 231/231 pass (current suite size, up from 205/205 at implementation time), ROM byte-identical rebuild, `check_save_valid` confirmed to write no `MM_CURSOR` value, `mm_on_entry`'s reset confirmed gated on `MM_JUST_ENTERED` (exactly 4 real transition sites plus the consuming clear, no bypass), all 12 `T18.*` checks confirmed passing. One Low finding: RTM's `FR-1170` row not updated for this package — corrected in place by this run. **Implementation Summary (2026-07-11).** Files Modified: `asm_game.py` (new 1-byte WRAM flag `MM_JUST_ENTERED` at `0xC2D7`; `check_save_valid`'s own `MM_CURSOR`-reset tail removed entirely; reset logic moved into `mm_on_entry`, gated on `MM_JUST_ENTERED`; the flag is set at every genuine `GAMESTATE → GS_MAIN_MENU` transition site — **4 found, not the 3 the package's own §6 task list named**: boot, `st_victory`'s A-press, `st_save`'s SELECT option, and `st_seed_scale_entry`'s B-cancel, the last one caught only because `T18.c`'s own test exercises it), `test_rom.py` (new suite **T18 a–d**, 12 checks). Files Created: none. Tests Added: T18.a (direct `BL-0048` regression — toggle with a valid save, exact-value assertions at every step), T18.b (toggle no-op with no save), T18.c (genuine re-entry via SEED/SCALE ENTRY B-cancel still resets correctly — the test that surfaced the 4th transition site), T18.d (new game end-to-end reachable from the toggled state). Tests Passed: 205/205 (up from 193/193; ROM unchanged at 22216/32768 bytes — one new 1-byte WRAM flag, no ROM growth after 0x100-boundary padding). Requirements Implemented: `FR-1170` regression fix (no requirement text change — the target behavior was always correctly specified). Documentation Updated: confirmed GDS-01's target-state diagram needed no change (already describes the correct, now-actually-achieved toggle behavior); this row. Traceability Updated: this row. Outstanding Issues: none. Independent of `IP-9050`/`IP-9070` — implemented in parallel, no shared file region touched by either. |
| [IP-1070](packages/IP-1070-maze-shaped-region-adjacency.md) | Maze-shaped region adjacency (FS-107 / FEAT-9100) | `08-code-implementation` | **VERIFIED** | IP-1020 (VERIFIED) | **YES — explicit user G3, 2026-07-11 (BL-0069)** | **Implemented 2026-07-11.** `generate_world` (`asm_game.py`) runs a new maze-generation pass after biome assignment: an iterative randomized DFS/recursive-backtracker spanning-tree carve (`GW_MAZE_STATE`/`GW_CUR_REGION`/`GW_MAZE_DIR`/`GW_BRAID_IDX`, new subroutines `gw_neighbor_hl`/`gw_maze_state_hl`), then a canonical-edge (down/right only) braid/prune pass — `REGION_GRAPH`'s 5-bytes/region format unchanged, only some neighbor bytes rewritten. Every `gw_prng_step` draw this pass makes is decorrelated via `ADR-0013`'s loop-local `GW_MAZE_DRAW_CTR` counter (XOR-perturbed, stepped +97/draw, never fed back into `gw_prng_step`'s own state); `gw_prng_step` itself and the biome-assignment loop are untouched. `worldgen.py`'s `_carve_maze` mirrors the SM83 routine step-for-step (validated byte-identical, 36-`(seed,scale)`-combination corpus). Two hand-assembly bugs found and fixed during implementation (fall-through into a subroutine body reached before any `CALL`; a register clobber in the prune-write block from calling `gw_neighbor_hl` twice without stashing the first result) — both confirmed fixed via direct PyBoy inspection. New suite **T19** (7 checks: subgraph, reachability, oracle parity, grammar, braid-fraction statistics — measured 25.80% against the ~25% target, static audit, WRAM headroom). Fixed a genuine supersession-sweep gap this package's own `07-implementation-planning` pass missed: `test_rom.py`'s `T11`/`T17` suites hardcoded a full-lattice-connectivity assumption (both at scale=5 and, more significantly, at the default scale=3 fixture used throughout the rest of the suite) — rewritten graph-driven (a real DFS tour over whatever edges the actual generated graph provides) rather than patched around. Documentation updated: GDS-07 §7b (new WRAM entries), FR-9140/FR-9150 (implemented), NFR-4200 (measured 85-byte WRAM addition), RTM rows, FS-107 Open Questions 1–3 resolved. **Verified 2026-07-12 ([VR-1070](verification/VR-1070-maze-shaped-region-adjacency.md)): independently confirmed in a fresh session — 226/226 pass (current suite size, up from 211/211 at implementation time as later packages added checks), ROM rebuilds at exactly 32768 bytes, all seven FS-107 ACs confirmed via T19.a–g, oracle/SM83 lockstep confirmed by T19.c (0 mismatches) plus a direct side-by-side code read, `dsr_p`/`draw_region_arrows`/`check_zone_transition` confirmed zero-diff via commit-scoped `git diff`.** One Low finding: the package's own §6 narrative describes the prune-pass tree-edge test as a single check when the shipped code (and oracle) correctly implement two — a real, necessary correctness property (a randomized DFS can carve an edge in either direction) the package's prose undersold; not a code defect, routed to a future `07` documentation touch. |
| [IP-1080](packages/IP-1080-maze-aware-edge-classification.md) | Maze-aware transition-edge classification, logic half (FS-108 / FEAT-2100) | `08-code-implementation` | **VERIFIED** | IP-1070 (VERIFIED), IP-1030 (VERIFIED) | **YES — explicit user G3, 2026-07-12 (BL-0083, "IP-1080 approved")** | **Verified 2026-07-12 ([VR-1080](verification/VR-1080-maze-aware-edge-classification.md)): independently confirmed** — 231/231 pass (current suite size, up from 230/230 at implementation time), ROM byte-identical rebuild, `DRA_ROW`/`DRA_COL` re-derivation confirmed via repeated-subtraction division (mirrors `generate_world`'s `gw_mod3`, not the package's own now-corrected stale `check_zone_transition` citation), open-edge branch confirmed byte-for-byte unchanged, all four `T20.*` checks confirmed passing (including AC-4 confirmed still honestly open). No findings. **Implementation Summary (2026-07-12).** Material drift found and worked around, not routed silently: the package's own §6/§7 cited "reuse `check_zone_transition`'s own established boundary-check pattern (`IP-9050`)," but direct code read confirmed `check_zone_transition` no longer performs row/col grid arithmetic at all — `IP-9050` (`BL-0047`) rewrote it to read `REGION_GRAPH`'s neighbor byte directly, removing the row/col-based clamp method the package's citation assumed. The underlying algorithm the package specifies (row = `CUR_ZONE`/`WORLD_SCALE`, col = `CUR_ZONE` MOD `WORLD_SCALE`, boundary tests against `WORLD_SCALE`) remained fully implementable on its own; only the "reuse" citation was stale, corrected in this package's own §6 text rather than treated as a Blocking Report. Files Modified: `asm_game.py` (`draw_region_arrows` gains a row/col re-derivation via repeated-subtraction division, computed once per call before the four `REGION_GRAPH` neighbor bytes claim `B`–`E`; two new transient WRAM bytes `DRA_ROW`/`DRA_COL` at `0xC2D8`–`0xC2D9`, the confirmed-unused gap after `MM_JUST_ENTERED` — **not** `TMP1`/`TMP2` as the package's own §6 suggested: `TMP1` was found, via a real failing test, to collide with `handle_play_input`'s own per-frame "did the player move" flag, clobbering row on the very next frame; the existing open-edge arrow-write branches are otherwise byte-for-byte unchanged), `test_rom.py` (new suite **T20 a–d**: a/b/c drive real generated worlds via `enter_seed_scale` — a 4-entry corpus, scale ∈ {2,3,9} + one extra seed, deliberately smaller than T19's own 15-entry corpus since this suite needs the CPU running its normal game loop afterward, incompatible with `invoke_generate_world`'s PC/SP-hijack trap per T13.c's own established caution — d is a static source-scan). Files Created: none. Tests Added: T20.a (open, AC-1), T20.b (blocked, AC-2, n=120), T20.c (absent, AC-3, n=68), T20.d (static ordering audit). Tests Passed: 230/230 (up from 226/226; ROM unchanged at 22472/32768 bytes — the ~30-byte addition absorbed within the code section's own existing 0x1000-boundary padding). AC-4 (visual rendering) confirmed still explicitly open per this package's own Definition of Done — no suite claims to cover it. Requirements Implemented: `FR-2330` **partially** (classification logic only, Notes entry recording the split). Documentation Updated: `FR-2330` Notes, RTM `FR-2330` row, `FS-108` forward-reference + §19 OQ2 resolved, `GDS-07` §2 (`DRA_ROW`/`DRA_COL` + the previously-undocumented `MM_JUST_ENTERED` added in the same pass). Traceability Updated: this row. Outstanding Issues: none — `IP-1080`'s own §6 citation correction is folded into this row, not a separate backlog item. |
| [IP-9090](packages/IP-9090-movement-clamp-boundary-fix.md) | Movement clamp boundary fix (BL-0051 + BL-0052) | `08-code-implementation` | **VERIFIED** | IP-1010 (VERIFIED, `handle_play_input`'s own shipped implementation) | **YES — explicit user G3, 2026-07-11 (BL-0072)** | **Verified 2026-07-12 ([VR-9090](verification/VR-9090-movement-clamp-boundary-fix.md)): independently confirmed** — 231/231 pass (current suite size, up from 213/213 at implementation time), ROM byte-identical rebuild, UP floor (`Y=8`) and RIGHT ceiling (`X=152`) both confirmed by direct code read, DOWN/LEFT confirmed unchanged, `T7.8`/`T7.8b`/`T7.10`/`T7.10b` all confirmed passing via genuine movement input. Confirmed the `X=152` ceiling is consumed consistently by `IP-9120`'s own later `check_zone_transition` fix. No findings. **Implementation Summary (2026-07-11).** Files Modified: `asm_game.py` (UP clamp magic bound `17`→`8`; RIGHT clamp comparison `CP_n(160)`→`CP_n(153)`; DOWN/LEFT unchanged, confirmed byte-for-byte), `test_rom.py` (`T7.8` rewritten to assert the corrected floor exactly, `Y==8`, not the old `Y>=17`; new `T7.8b` confirms the floor holds under continued input; `T7.10`'s stale comment corrected; new `T7.10b` drives the RIGHT clamp via genuine movement input, confirming it settles at exactly `X=152`). Files Created: none. Tests Added: T7.8b, T7.10b (T7.8/T7.10 corrected in place). Tests Passed: 213/213 (up from 211/211; ROM unchanged at 22472/32768 bytes — constant-value changes only, no new bytes). Requirements Implemented: `FR-2100` (Notes entry recording the corrected boundary values and the still-open requirements-baseline gap — no FR states the exact pixel bounds, flagged for a future `04` pass, not resolved here). Documentation Updated: `FR-2100` Notes, RTM `FR-2100` row. Traceability Updated: this row. Outstanding Issues: none — the requirements-baseline gap named in §3/§9 is a forward pointer, not a defect in this package's own scope. |
| [IP-9100](packages/IP-9100-collectible-pickup-hitbox-fix.md) | Collectible pickup hitbox fix (BL-0053) | `08-code-implementation` | **VERIFIED** | IP-1010 (VERIFIED, `check_collisions`' own shipped implementation) | **YES — explicit user G3, 2026-07-11 (BL-0072)** | **Verified 2026-07-12 ([VR-9100](verification/VR-9100-collectible-pickup-hitbox-fix.md)): independently confirmed** — 231/231 pass (current suite size, up from 217/217 at implementation time), ROM byte-identical rebuild, the asymmetric point-in-box test confirmed by direct code read (unsigned-subtract range check, not the originally-planned symmetric formula), all four boundary checks (`T8.x/T8.y/T8.z1/T8.z2`) confirmed passing at the exact `BL-0053` reproduction points and boundary values. `FR-3100`'s text-vs-implementation divergence confirmed honestly flagged, not silently absorbed. No findings. **This closes the movement/pickup/UI bug-remediation tranche end-to-end — `IP-9080`/`9090`/`9100` all now `VERIFIED`.** **Implementation Summary (2026-07-11).** The package's own planned fix (a symmetric `|diff|<8`/`|diff|<16` threshold change, keeping the existing abs-value code shape) was found **wrong during implementation** — direct PyBoy verification against `BL-0053`'s own two reproduction points showed it still incorrectly collected `item_y=75` (`\|80-75\|=5<16`). Re-derived the correct model: the item is a collision *point*, not a second box — pickup fires iff that point falls inside the player's real 8×16 box (`0<=item_x-PLAYER_X<=7`, `0<=item_y-PLAYER_Y<=15`), an asymmetric unsigned-range test, not a symmetric one. Files Modified: `asm_game.py` (`check_collisions`' X/Y overlap test rewritten as a single unsigned subtract+compare per axis, using `H` as scratch — not `B`/`C`, both live/needed later in the same routine), `test_rom.py` (new `T8.x`/`T8.y`/`T8.z1`/`T8.z2`; `T11.a1` corrected from an `(dx,dy)=(8,8)` near-miss position — valid only under the old buggy tolerance — to the item's exact coordinates, matching every other pickup test's own convention). Files Created: none. Tests Added: T8.x, T8.y, T8.z1, T8.z2. Tests Passed: 217/217 (up from 213/213; ROM unchanged at 22472/32768 bytes). Requirements Implemented: `FR-3100` (Notes entry with the corrected formula — `FR-3100`'s own Title/Description/AC text still describes the old `10px`-symmetric model, left unmodified, flagged for a future `04` pass to correct properly, not just note). Documentation Updated: `FR-3100` Notes, RTM `FR-3100` row, `IP-9100`'s own package document (§6/§7/§10/§11 corrected to match what was actually built and verified). Traceability Updated: this row. Outstanding Issues: none — the `FR-3100` text correction is a named forward pointer, not a defect in this package's own scope. Parallel-eligible with `IP-9080`/`IP-9090` — no shared file region. |
| [IP-9080](packages/IP-9080-save-screen-third-option-labeling.md) | SAVE screen third-option labeling (BL-0049) | `08-content-authoring` | **VERIFIED** | IP-1040 (VERIFIED, `st_save`'s own shipped SELECT-option behavior) | **YES — explicit user G3, 2026-07-11 (BL-0072)** | **Verified 2026-07-12 ([VR-9080](verification/VR-9080-save-screen-third-option-labeling.md)): independently confirmed** — 231/231 pass (current suite size, up from 220/220 at implementation time), ROM byte-identical rebuild, `T5.10–T5.12` confirmed passing, and independently re-driven via PyBoy (no prior content review existed for this package) — screenshot confirms "SELECT: SAVE"/"AND EXIT" renders cleanly, no overlap. No findings. **Implementation Summary (2026-07-11).** Files Modified: `tilemaps.py` (`save_screen` gains two new `_str()` lines, "SELECT: SAVE" / "AND EXIT," rows 12–13, columns 5–16/5–12, reusing the screen's existing font tiles/palette 2 — zero new tile art, zero new palette entries), `test_rom.py` (new `T5.10`–`T5.12` checks: SAVE screen reachable, label present in rows 12–13, no collision with the existing "A: YES"/"B: NO"/bottom-border rows; screenshot `T5_save_screen.png` captured and visually confirmed clean). `asm_game.py` untouched, per this package's own content-only scope. Files Created: none. Tests Added: T5.10, T5.11, T5.12. Tests Passed: 220/220 (up from 217/217; ROM unchanged at 22472/32768 bytes — text reuses existing font tiles, no new tile-index/palette-table entries). Requirements Implemented: `FR-1190` (Notes entry — behavior was already Met, this closes the discoverability gap). Documentation Updated: `FR-1190` Notes, RTM `FR-1190` row. Traceability Updated: this row. Outstanding Issues: none. UI-input-mapping question resolved directly (kept the existing `A`/`B`/`SELECT` scheme, no cursor-based redesign) — see this row's own planning note and the TWBS's fuller rationale. Parallel-eligible with `IP-9090`/`IP-9100` — different stage-08 peer, no shared file region. |
| [IP-9110](packages/IP-9110-gw-prng-step-mixing-step-repair.md) | `gw_prng_step` mixing-step repair (BL-0074) | `08-code-implementation` | **VERIFIED** | IP-1010 (VERIFIED, `gw_prng_step`'s own shipped implementation) | **YES — explicit user G3, 2026-07-11 (BL-0074, "Yes, ship the fix")** | **Verified 2026-07-12 ([VR-9110](verification/VR-9110-gw-prng-step-mixing-step-repair.md)): independently confirmed** — 231/231 pass (current suite size, up from 222/222 at implementation time), ROM byte-identical rebuild, `7,9,8` shift-triplet confirmed shipped exactly (`asm_game.py`) with `worldgen.py`'s `_step` mirroring it in lockstep (zero oracle mismatches), `T12.j`/`T12.k` confirmed passing via the live SM83-built ROM (not just the oracle). This run independently re-performed the package's own "ad hoc, not a permanent test" pre-upgrade-save check live via PyBoy: a `version=0x03` fixture shows CONTINUE genuinely blank, a `version=0x04` fixture shows it offered — confirmed correct. No findings. **Implementation Summary (2026-07-11).** No drift — package's own cited lines (`asm_game.py:1200-1214`, `SAVE_VERSION_VAL` at line 122) matched exactly. Files Modified: `asm_game.py` (`gw_prng_step`'s mixing step replaced: `x^=x<<7` via 7 chained single-bit shifts on a D:E scratch pair — `SLA E`/`RL D`, no cheap decomposition exists, verified `(x<<8)>>1 != x<<7` for ~half of all 16-bit values; `x^=x>>9` via the verified-exact free decomposition `(x>>8)>>1` — a byte-move (`E:=TMP1, D:=0`) plus one `SRL D`/`RR E`; `x^=x<<8` via a straight byte-move (`D:=TMP2`), cheaper than the byte-swap it replaces. Clobbers only A/D/E, HL/BC untouched — matches every existing call site's own contract, confirmed by the biome loop's own HL-survives-the-call reliance and the maze pass's explicit `PUSH_DE`/`POP_DE` bracket. `SAVE_VERSION_VAL` bumped `0x03`→`0x04`), `worldgen.py` (`_step` updated in lockstep to the identical `7,9,8` triplet — `_carve_maze` inherits the fix automatically, it calls `_step` directly), `test_rom.py` (new `T12.j`/`T12.k` in the existing T12 suite). Files Created: none. Tests Added: T12.j (non-degeneracy statistical check, 36-seed corpus at scale=9, mean Water fraction measured 15.6%, all under the 40% bound), T12.k (direct `BL-0074` reproduction re-check — `seed=0`/`scale=9` now measures 25.9% Water, rows 1-8 no longer all-zero). Tests Passed: 222/222 (up from 220/220; ROM unchanged at 22472/32768 bytes), including `T19`'s own existing braid-fraction check (24.35%, within band — confirms `ADR-0013`'s `GW_MAZE_DRAW_CTR` perturbation, deliberately left in place, continues to decorrelate correctly against the now-repaired underlying stream) and `T19.c`'s oracle-parity check (0 mismatches — SM83/Python lockstep confirmed under the new algorithm). Directly re-verified via PyBoy (ad hoc, not a new permanent test, per the Verification Checklist's own framing): a synthetic `version=0x03` save fixture boots to MAIN MENU with the CONTINUE row genuinely blank (all-space tiles), while an identical fixture at `version=0x04` shows real CONTINUE text — the existing generic version-guard machinery excludes a pre-fix save exactly as intended, zero new code needed. Requirements Implemented: `FR-9100` (Notes entry recording the repair; the FR's own determinism guarantee held throughout — this was an output-quality defect, not a determinism defect). Documentation Updated: `FR-9100` Notes, `NFR-2200` Notes (confirms the "no DIV/MUL" constraint remains satisfied, orthogonal to this fix), RTM `FR-9100` row (cites `T12.j`/`T12.k`, `IP-9110`, `ADR-0014`). Traceability Updated: this row. Outstanding Issues: none — the named risk (`IP-1070` also depends on `gw_prng_step`) was directly checked, not merely trusted: full suite green including `T19`'s own properties-based checks. |
| [IP-9120](packages/IP-9120-right-zone-transition-threshold-fix.md) | RIGHT zone-transition threshold fix (BL-0076) | `08-code-implementation` | **VERIFIED** | IP-1010 (VERIFIED, `check_zone_transition`'s own bootstrap dependency), IP-9050 (VERIFIED, the routine's own current shape) | **YES — explicit user G3, 2026-07-12 (BL-0077, "Yes, ship the fix")** | **Verified 2026-07-12 ([VR-9120](verification/VR-9120-right-zone-transition-threshold-fix.md)): independently confirmed** — 231/231 pass (current suite size, up from 224/224 at implementation time), ROM byte-identical rebuild, RIGHT-edge comparison confirmed reading `CP_n(152)` matching `handle_play_input`'s own clamp ceiling exactly, `T7.11` confirmed passing via real, sustained button-press input (not a memory teleport). No findings. **Implementation Summary (2026-07-12).** No drift — package's own cited line (`asm_game.py:662`) matched exactly. Files Modified: `asm_game.py` (`check_zone_transition`'s RIGHT-edge comparison `CP_n(156)`→`CP_n(152)`, exactly matching `handle_play_input`'s own RIGHT clamp ceiling — the entire production change), `test_rom.py` (new `T7.11`). Files Created: none. Tests Added: T7.11 — **corrected during implementation** (package's own §3/§8 originally cited `FR-2310`, the negative "no transition at true boundary" requirement; corrected to `FR-2300`, the actual positive-transition requirement this bug breaks — flagged and fixed in the package document itself, mirroring `IP-9100`'s own precedent). The test's own first draft also needed correction: holding RIGHT for a fixed tick count (mirroring `T7.10b`'s dead-end case) caused overshoot once the transition actually fired mid-hold, since the player keeps moving inside the *new* zone too — fixed by releasing the button the instant `CUR_ZONE` changes, then asserting `CUR_ZONE==4` and `PLAYER_X<=20` (not an exact `X==8`, tolerant of residual movement ticks). Uses region 3 (oracle-confirmed open right neighbor: region 4) via the same `CUR_ZONE`-forcing convention `T7.10`/`T16.a` already establish, since the default fixture's own region 0 has no open right neighbor. Tests Passed: 224/224 (up from 222/222; ROM unchanged at 22472/32768 bytes — a single operand byte changed value). Directly re-verified via PyBoy at `BL-0076`'s own original reproduction point (region 9, `seed=0`/`scale=9`): sustained real rightward button-press input now carries the player through multiple real transitions (9→10→11), where it previously stuck at 9 forever. Requirements Implemented: `FR-2300` (Notes entry recording the regression and fix). Documentation Updated: `FR-2300` Notes, RTM `FR-2300` row (cites `T7.11`, `IP-9050`, `IP-9120`), `IP-9120`'s own package document (§3/§8 corrected to match what was actually built and verified). Traceability Updated: this row. Outstanding Issues: none — the broader "no direction has real-button-press positive-transition coverage" gap (named in the TWBS) remains a recommended, low-urgency future `07` pass, not this package's own scope. |
| [IP-9130](packages/IP-9130-zone-transition-intent-gate.md) | Zone-transition intent gate (BL-0078) | `08-code-implementation` | **COMPLETE — 226/226 checks pass** | IP-1010 (VERIFIED, `check_zone_transition`'s own bootstrap dependency), IP-9050 (COMPLETE), IP-9120 (COMPLETE, the routine's own current shape) | **YES — explicit user G3, 2026-07-12 (BL-0079, "Yes, ship the fix")** | **Implementation Summary (2026-07-12).** No drift — package's own cited lines matched exactly. Files Modified: `asm_game.py` (all four `check_zone_transition` branches gated on their own `JOY_CUR` direction bit — `BIT_b_A(J_RIGHT/J_LEFT/J_UP/J_DOWN)` — before the existing position test; DOWN's gate `RET_Z()`s directly since `czt_bot` has no further fallthrough), `test_rom.py` (`T11.a2`/`T11.a3` wrapped with real `button_press`/`button_release` for the matching direction; `_t17_do_move` — shared by `T17.a`/`b2`/`b5` — likewise; new `T7.12`). Files Created: none. Tests Added: T7.12. A second overshoot bug (the same class `T7.11` hit) surfaced during implementation: `_t17_do_move` originally held the button for `settle`'s fixed 80-tick duration, causing `T17.d`/`T17.b3`'s own entry-position checks to fail once the transition fired mid-hold and the player kept moving in the newly entered zone — fixed by releasing the button the instant `CUR_ZONE` changes (mirroring `T7.11`'s own fix). Tests Passed: 226/226 (up from 224/224; ROM: 22472/32768 bytes unchanged — four small `BIT`-test sequences absorbed within existing padding). Directly re-verified via PyBoy, reproducing `BL-0078`'s own exact reported sequence at the literal default game start: walk RIGHT until blocked (zone 0, `X=152`), walk DOWN only — zone now correctly settles at 3 and stays there through an extended settle window (previously jumped to 4). Confirmed a legitimate rightward press in zone 3 still correctly transitions to zone 4 — the fix blocks only the spurious case, not real intent. Requirements Implemented: `FR-2300` (Notes entry recording this second, distinct regression and its fix). Documentation Updated: `FR-2300` Notes, RTM `FR-2300` row (cites `T7.12`, `IP-9130`). Traceability Updated: this row. Outstanding Issues: none. |
| [IP-9140](packages/IP-9140-right-arrow-offscreen-position-fix.md) | Right-arrow off-screen position fix (BL-0084) | `08-code-implementation` | **COMPLETE — 231/231 checks pass** | IP-1030 (VERIFIED), IP-1080 (COMPLETE, disjoint diff, no merge risk) | **YES — explicit user G3, 2026-07-12 (BL-0085, "Yes, ship the fix")** | **Implementation Summary (2026-07-12).** No drift — `ARROW_ADDR_R`'s cited definition matched exactly. Files Modified: `asm_game.py` (`ARROW_ADDR_R` column offset `(32-2)`→`(20-2)`, i.e. tilemap column 30→18 — the only change, `ARROW_ADDR_U`/`D`/`L` confirmed already within the visible 0–19/0–17 range, untouched), `test_rom.py` (`ARROW_POS['right']` corrected in place to match — this test constant carried the same stale `32-2` column that let the defect ship undetected; new check **T13.d**, a screen-visibility audit asserting every arrow address falls inside the true 20×18 visible window, immediately after `T13.c`). Files Created: none. Tests Added: T13.d. Tests Passed: 231/231 (up from 230/230; ROM unchanged at 22472/32768 bytes — a single operand byte changed value). Directly re-verified via PyBoy screenshot at `BL-0084`'s own exact reported sequence (default seed/scale, walk down from region 0 to region 3): the right arrow is now visibly present where region 3's own live right-neighbor (region 4) exists. `IP-1080`'s own classification logic reconfirmed unaffected by this fix — the DFS-driven traversal from this package's own investigation (five `(seed,scale)` combinations, real navigation) found zero discrepancies, cited in this package's own document rather than re-run as a formal check. Requirements Implemented: `FR-2320` (Notes entry recording the defect and fix). Documentation Updated: `FR-2320` Notes, RTM `FR-2320` row (previously entirely `UNASSIGNED` — also backfilled with `IP-1030`'s own base-implementation credit while correcting this row, a pre-existing gap this fix's own investigation surfaced). Traceability Updated: this row. Outstanding Issues: none — a pre-existing, long-standing defect (not a regression from any current-session work), now fully closed. |

**FEAT-6100 (Aesthetic & Biome-Transition Compliance) needs no package** — per FS-106 §8/§10, it
has no runtime behavior or module of its own; its standard (GDS-08 delta §7/§8) is already
authored and is first exercised via a future `09-content-review` pass on `IP-1031`'s content, not
via an Implementation Package.

## Post-ship remediation tranche (playtesting bugs, planned 2026-07-11)

Three packages remediating bugs the project owner found playtesting the shipped Release-2
tranche (`BL-0047`/`BL-0048`, filed via `00-intake`) — plus two more Critical defects
(`BL-0058`/`BL-0059`) `BL-0047`'s own mandatory supersession sweep discovered along the way (see
the
[TWBS](01-technical-work-breakdown.md#post-ship-remediation-tranche-playtesting-bugs-bl-0047bl-0048-planned-2026-07-11)
for the full sweep record). **None of these five bugs — nor the three packages remediating
them — fall under the `BL-0001`…`BL-0005` G3 bootstrap carve-out; explicit user authorization is
required before `08-code-implementation` can start any of them.** Critical path: **IP-9070 →
IP-9050** (2 packages); `IP-9060` is independent and parallel-eligible with both.

## Maze-shaped region adjacency tranche (planned 2026-07-11)

Two packages implementing `ADR-0012`'s maze-generation decision (`BL-0064`/`BL-0065`/`BL-0067`,
`FS-107`/`FS-108`). **Neither falls under the `BL-0001`…`BL-0005` G3 bootstrap carve-out; explicit
user authorization is required before `08-code-implementation` can start either.** Critical path:
**IP-1070 → IP-1080** (2 packages, the tranche's full extent). `FS-108`'s rendering half remains
unplanned — riding `BL-0068`'s still-open `GDS-08` delta, not a package in this tranche.

- **`IP-1070`** (`FEAT-9100`) depends functionally only on `IP-1020` (`VERIFIED`) — the maze pass
  reads `REGION_GRAPH`'s already-written full-lattice candidate bytes as its own input.
- **`IP-1080`** (`FEAT-2100`, logic half) depends on `IP-1070` reaching `VERIFIED` — no maze-
  blocked case exists to classify before the maze exists.
- **Authorization state: `IP-1070` authorized 2026-07-11** (explicit user G3, `BL-0069` —
  "Authorize IP-1070"). A first `08-code-implementation` attempt hit a Blocking Report (the
  existing PRNG doesn't stay well-distributed across the braid pass's many consecutive draws),
  root-caused by `R113` and resolved by `ADR-0013` (see the package status table's own `IP-1070`
  row); a second attempt implemented the fix and reached **`COMPLETE`** (211/211 suite passing).
  Authorization stood throughout — the blocker was a dependency defect, not a missing go-ahead.
  **`IP-1070` independently verified 2026-07-12 ([VR-1070](verification/VR-1070-maze-shaped-region-adjacency.md)) — now `VERIFIED`.**
  **`IP-1080` authorized 2026-07-12** (explicit user G3, `BL-0083` — "IP-1080 approved") and
  **implemented the same day — `COMPLETE`, 230/230 checks pass** (see the package status table's
  own `IP-1080` row). This closes the maze-shaped region adjacency tranche's full extent —
  `IP-1080` awaits independent (fresh-session) verification; `FS-108`'s rendering half remains a
  future, unstarted spec/implementation task, not part of this tranche.

## Movement/pickup/UI bug-remediation tranche (planned 2026-07-11)

Three packages, four standing backlog bugs (`BL-0049`/`BL-0051`/`BL-0052`/`BL-0053`), all
independently reported/reproduced prior to this pass. **None falls under the `BL-0001`…`BL-0005`
G3 bootstrap carve-out; explicit user authorization is required before `08-code-implementation`/
`08-content-authoring` can start any of them.** No critical path — all three are mutually
independent (different root causes, no shared symbol, two different stage-08 peers) and fully
parallel-eligible.

- **`IP-9090`** (`BL-0051`/`BL-0052`, movement clamps) depends only on `IP-1010` (`VERIFIED`,
  `handle_play_input`'s own shipped implementation).
- **`IP-9100`** (`BL-0053`, pickup hitbox) depends only on `IP-1010` (`VERIFIED`,
  `check_collisions`' own shipped implementation).
- **`IP-9080`** (`BL-0049`, SAVE screen text) depends only on `IP-1040` (`VERIFIED`, `st_save`'s
  own shipped SELECT-option behavior).
- **Authorization state: all three authorized 2026-07-11** (explicit user G3, `BL-0072` —
  "Authorize IP-9080/IP-9090/IP-9100"), distinct from the `BL-0062` answer, which named only
  `BL-0047`/`0048`/`0058`/`0059`/`0063` explicitly.
- **Notable finding:** `IP-9100`'s own fix directly contradicts `FR-3100`'s currently-baselined
  Acceptance Criteria (the requirement describes the pre-fix symmetric-window behavior as if
  intended) — implemented per this package's own scope, `FR-3100`'s text left unmodified, flagged
  as a Notes-only forward pointer for a future `04-requirements-engineering` correction (see the
  package status table's own `IP-9100` row).

## Dependency graph

```mermaid
graph TD
    IP9010["IP-9010 test-suite rewrite<br/>(VERIFIED)"]
    IP9020["IP-9020 score-bar VBlank fix<br/>(VERIFIED)"]
    IP9030["IP-9030 root-doc refresh<br/>(VERIFIED)"]
    IP9040["IP-9040 legacy archival<br/>(VERIFIED)"]
    IP1010["IP-1010 ScoreItem persistence<br/>(Release 1, VERIFIED)"]
    IP9010 --> IP9020
    IP9010 --> IP9040
    IP9010 --> IP1010
    IP9020 --> IP9030

    IP1020["IP-1020 world generation<br/>(Release 2, VERIFIED)"]
    IP1030["IP-1030 region screens: code<br/>(Release 2, VERIFIED)"]
    IP1031["IP-1031 region screens: content<br/>(Release 2, COMPLETE)"]
    IP1040["IP-1040 main menu & new-game<br/>(Release 2, VERIFIED)"]
    IP1050["IP-1050 generated-world save<br/>(Release 2, VERIFIED)"]
    IP9010 -.all bootstrap packages VERIFIED.-> IP1020
    IP1020 --> IP1030
    IP1030 --> IP1031
    IP1020 --> IP1040
    IP1020 --> IP1050

    style IP1020 fill:#f9d,stroke:#333,stroke-width:2px

    IP9070["IP-9070 CUR_ZONE-indexed<br/>structure generalization<br/>(remediation, COMPLETE)"]
    IP9050["IP-9050 generated-world<br/>navigation fix<br/>(remediation, COMPLETE)"]
    IP9060["IP-9060 main menu<br/>cursor fix<br/>(remediation, COMPLETE)"]
    IP1020 --> IP9070
    IP1030 --> IP9070
    IP1040 --> IP9070
    IP1050 --> IP9070
    IP9070 -->|hard prerequisite| IP9050
    IP1040 --> IP9060

    style IP9070 fill:#f96,stroke:#333,stroke-width:2px
    style IP9050 fill:#f96,stroke:#333,stroke-width:2px

    IP1070["IP-1070 maze-shaped<br/>region adjacency<br/>(VERIFIED)"]
    IP1080["IP-1080 maze-aware edge<br/>classification, logic half<br/>(COMPLETE)"]
    IP1020 --> IP1070
    IP1070 --> IP1080
    IP1030 --> IP1080

    style IP1070 fill:#9f9,stroke:#333,stroke-width:2px
    style IP1080 fill:#cfc,stroke:#333,stroke-width:2px

    IP9090["IP-9090 movement clamp<br/>boundary fix<br/>(COMPLETE)"]
    IP9100["IP-9100 collectible pickup<br/>hitbox fix<br/>(COMPLETE)"]
    IP9080["IP-9080 SAVE screen<br/>third-option labeling<br/>(COMPLETE)"]
    IP1010 --> IP9090
    IP1010 --> IP9100
    IP1040 --> IP9080

    style IP9090 fill:#cfc,stroke:#333,stroke-width:2px
    style IP9100 fill:#cfc,stroke:#333,stroke-width:2px
    style IP9080 fill:#cfc,stroke:#333,stroke-width:2px

    IP9110["IP-9110 gw_prng_step<br/>mixing-step repair<br/>(COMPLETE)"]
    IP1010 --> IP9110

    style IP9110 fill:#cfc,stroke:#333,stroke-width:2px

    IP9120["IP-9120 RIGHT zone-transition<br/>threshold fix<br/>(COMPLETE)"]
    IP1010 --> IP9120
    IP9050 --> IP9120

    style IP9120 fill:#cfc,stroke:#333,stroke-width:2px

    IP9130["IP-9130 zone-transition<br/>intent gate<br/>(COMPLETE)"]
    IP1010 --> IP9130
    IP9050 --> IP9130
    IP9120 --> IP9130

    style IP9130 fill:#cfc,stroke:#333,stroke-width:2px
```

*(The dotted edge into `IP1020` represents the Master Build Plan's own package-status
prerequisite — every Release-2 package's "Depends on" column names all five bootstrap packages,
all `VERIFIED` — not a functional dependency `FS-102` itself states. Solid edges are `FS-xxx`-
stated functional dependencies. `IP1020` highlighted pink as this tranche's foundational,
first-in-critical-path package.)*

## Critical path & parallel opportunities

- **Critical path (Release 1, per FP-04):** IP-9010 → IP-1010.
- IP-9010 is `VERIFIED` (2026-07-07, [VR-9010](verification/VR-9010-test-suite-rewrite.md)) —
  the G5 gate is confirmed functional by independent re-run (109/109 pass, ROM byte-identical).
- IP-9020 is `VERIFIED` (2026-07-07, [VR-9020](verification/VR-9020-score-bar-vblank-fix.md)) —
  `IP-9030`'s last blocking dependency.
- IP-9040 is `VERIFIED` (2026-07-07, [VR-9040](verification/VR-9040-legacy-artifact-archival.md))
  — no downstream package depends on it.
- **IP-1010 is `VERIFIED` (2026-07-07, [VR-1010](verification/VR-1010-per-zone-scoreitem-persistence.md))
  — Release 1's critical path (IP-9010 → IP-1010) is complete end-to-end.**
- **IP-9030 is `VERIFIED` (2026-07-10, [VR-9030](verification/VR-9030-root-doc-refresh.md))** —
  the bootstrap tranche's last remaining package, verified in a fresh session per the
  same-session independence rule.
- **All five packages are now `VERIFIED`.** The bootstrap tranche is complete end-to-end;
  `10-integration-review` is the next unblocked step for this tranche.
- **Authorization state summary (bootstrap tranche):** all five packages authorized — IP-9020/
  IP-9040 via the G3 bootstrap carve-out; IP-9010/IP-9030/IP-1010 via the user's explicit
  go-ahead recorded 2026-07-07 (`BL-0024`, "Authorize all three"). Execution order remains
  dependency-driven.

### Release 2 tranche (procgen-world increment, planned 2026-07-10)

- **Critical path (per FP-04/TWBS):** IP-1020 → IP-1030 → IP-1031 (3 packages) — the same
  3-node length FP-04's Feature-level critical path (FEAT-9000 → FEAT-4100 → FEAT-6100)
  predicted, since FEAT-6100 itself needs no package (see the package table's own note).
- **IP-1020 `VERIFIED`** (2026-07-10, [VR-1020](verification/VR-1020-procedural-world-generation.md))
  — this tranche's universal unblocker; every other package either consumes its generation output
  or triggers it. **IP-1030 `VERIFIED`** (2026-07-10, [VR-1030](verification/VR-1030-generated-region-screen-composition-code.md),
  180/180 on tree head, IP-1030's own T13: 3/3) — the critical path's second node, now cleared.
  **IP-1040 `COMPLETE`** (163/163) and **IP-1050 `COMPLETE`** (180/180) — both still awaiting
  independent verification (`COMPLETE` is not `VERIFIED`; see this table's own header rule).
  **IP-1031 is now `READY`** (both its dependencies, IP-1020 and IP-1030, are `VERIFIED`) — the
  critical path's final node, unblocked by this run.
- **Parallel opportunities exercised:** IP-1040 and IP-1050 each depend only on IP-1020
  (`VERIFIED`) and were implemented independently of IP-1030's own progress and of each other,
  exercising exactly the parallelism FP-04/TWBS predicted.
- **Authorization state summary (Release 2 tranche):** all five packages authorized — user's
  explicit "Authorize all five" (2026-07-10, `BL-0040`).
- **Prior framing (superseded):** this tranche was previously described as "no package
  authorized." This is genuinely new work — none of it falls under G3's bootstrap carve-out
  (as-built baselining, or remediation of `BL-0001`…`BL-0005`). **Explicit user G3 authorization
  is required before `08-code-implementation`/`08-content-authoring` can start any of these five
  packages.**
- **Current status update (2026-07-11):** `IP-1040`/`IP-1050` both `VERIFIED`; `IP-1031`
  `COMPLETE` with a clean content review, own verification blocked on a fresh session's
  independence. Four of five Release-2 packages `VERIFIED`.

### Post-ship remediation tranche (playtesting bugs, planned 2026-07-11)

- **Critical path: IP-9070 → IP-9050** (2 packages) — `IP-9070` widens/relocates every
  `CUR_ZONE`-indexed structure (`SCOREITEM_FLAGS`, `ZONE_COLLECTS`) that `IP-9050`'s own
  navigation fix would otherwise make unsafe; this is a correctness-ordering dependency, not a
  scheduling convenience (see `IP-9050`'s own Dependencies field). **Both packages reached
  `COMPLETE` 2026-07-11** — `IP-9070` first, unblocking `IP-9050`, then `IP-9050` itself (213/213,
  `check_zone_transition` fully regeneralized to `REGION_GRAPH`; also folded in `BL-0063`'s
  `KEYITEM_FLAGS` clear-width companion fix, found during this package's own supersession sweep).
  **The tranche's entire critical path is now implemented end-to-end.**
- **IP-9060 is independent** of both — a wholly unrelated MAIN MENU cursor defect in the same
  file, parallel-eligible from the start. **Reached `COMPLETE` 2026-07-11** (205/205), implemented
  alongside `IP-9070` in the same session; found and fixed a 4th `GAMESTATE → GS_MAIN_MENU`
  transition site (`st_seed_scale_entry`'s B-cancel) its own §6 task list hadn't named — filed
  as a spec-completeness catch, not a new bug.
- **Authorization state: all three packages authorized 2026-07-11** (explicit user G3, `BL-0062`
  — "Authorize all three"). None of `BL-0047`/`0048`/`0058`/`0059` fall under the
  `BL-0001`…`BL-0005` G3 bootstrap carve-out; this authorization was required before
  `08-code-implementation` could start any of them, and now covers all three.

### Maze-shaped region adjacency tranche (planned 2026-07-11)

- **Critical path: IP-1070 → IP-1080** (2 packages, the tranche's full extent) — `IP-1080` cannot
  classify a maze-blocked edge before `IP-1070`'s maze pass exists; this is a hard functional
  dependency (`FS-108`'s own Dependencies), not a scheduling convenience.
- **`IP-1070` reached `COMPLETE` 2026-07-11** — a first `08-code-implementation` attempt found the
  design's own dependency on the existing PRNG's draw-quality didn't hold (a Blocking Report);
  `ADR-0013` resolved it with a scoped counter-XOR perturbation, the package was re-planned with a
  light touch (§4/§6/§7/§13, no redesign), and a second attempt implemented it — see the package
  status table's own `IP-1070` row. **Independently verified 2026-07-12
  ([VR-1070](verification/VR-1070-maze-shaped-region-adjacency.md)) — now `VERIFIED`.**
  **`IP-1080` authorized and implemented 2026-07-12 — reached `COMPLETE`, 230/230 checks pass**
  (new suite T20 a–d; see the package status table's own `IP-1080` row for the full Implementation
  Summary, including the `check_zone_transition` citation correction and the `TMP1`-collision
  finding that added `DRA_ROW`/`DRA_COL`). **This closes the tranche's full critical-path extent**
  — both packages now `COMPLETE`, awaiting independent (fresh-session) verification.
- **Authorization state: `IP-1070` authorized 2026-07-11** (explicit user G3, `BL-0069`) —
  authorization stood throughout, unaffected by the block-and-resolve cycle. **`IP-1080`
  authorized 2026-07-12** (explicit user G3, `BL-0083` — "IP-1080 approved").
- **`FS-108`'s rendering half is not part of this tranche** — `BL-0068`'s `GDS-08` delta has since
  resolved (2026-07-11, `GDS-08` §10); the rendering half's own spec is deliberately deferred to a
  future `06-feature-specification` pass rather than authored now, per that run's own judgment
  call (`IP-1080`'s own Definition of Done left `FS-108`'s Acceptance Criterion 4 explicitly open,
  confirmed still open on completion).

### Movement/pickup/UI bug-remediation tranche (planned 2026-07-11)

- **No critical path** — `IP-9090`/`IP-9100`/`IP-9080` are mutually independent (three different
  root causes, two different stage-08 peers, no shared file region between `IP-9080` and the other
  two; `IP-9090`/`IP-9100` share `asm_game.py` but touch different functions with no dependency
  either direction). Fully parallel-eligible.
- **`IP-9090`** (`BL-0051`/`BL-0052`): corrects `handle_play_input`'s UP/RIGHT movement clamps.
  Folded in a same-pass supersession-sweep finding — `test_rom.py`'s own `T7.8` asserts the pre-fix
  buggy floor as correct; the package's own scope includes updating it. **Reached `COMPLETE`
  2026-07-11** (213/213) — `T7.8`/`T7.10` corrected exactly as planned, new `T7.8b`/`T7.10b` added.
- **`IP-9100`** (`BL-0053`): corrects `check_collisions`' pickup-overlap test to a true point-in-box
  test against the sprite's real 8×16 extent. Directly contradicts `FR-3100`'s own currently-
  baselined text — implemented anyway (in scope per this stage's own remediation-package
  discipline), with the requirement-text correction routed to a future `04` pass, not silently
  absorbed here. **Reached `COMPLETE` 2026-07-11** (217/217) — the package's own originally-planned
  symmetric-threshold formula was found wrong during implementation (verified against `BL-0053`'s
  own two reproduction data points) and replaced with the correct asymmetric unsigned-range test;
  see the package status table's own `IP-9100` row.
- **`IP-9080`** (`BL-0049`): adds on-screen text for the SAVE screen's silent third option.
  Content-only (`08-content-authoring`); the entry's own open UI-input-mapping question resolved
  directly by this pass (keep the existing `A`/`B`/`SELECT` scheme, not a cursor-based redesign).
  **Reached `COMPLETE` 2026-07-11** (220/220) — "SELECT: SAVE" / "AND EXIT" added to `save_screen`,
  zero new tile/palette cost.
- **Authorization state: all three authorized 2026-07-11** (explicit user G3, `BL-0072`) —
  `BL-0049`/`0051`/`0052`/`0053` were not covered by the `BL-0001`…`BL-0005` G3 bootstrap
  carve-out, nor by `BL-0062`'s authorization (which named only the prior remediation tranche's
  five bugs explicitly), so a fresh explicit answer was needed and is now on record.

### `gw_prng_step` mixing-step repair (planned 2026-07-11, implemented 2026-07-11)

- **No critical path** — a single package, `IP-9110`, no split.
- **`IP-9110`** (`BL-0074`): repairs the shipped PRNG's mixing step, root-caused and
  architecturally decided this session (`ADR-0014`). Investigation found the defect's true scope
  far exceeds the original report — 100% of 2000 tested seeds degenerate under the shipped
  routine, not just the literal default seed; 55% of `scale=9` worlds are already majority-Water
  today. **Reached `COMPLETE` 2026-07-11** (222/222) — the period-sound `7,9,8` shift triplet
  implemented in `gw_prng_step`, `worldgen.py`'s oracle updated in lockstep (`T19.c` confirms 0
  mismatches), `SAVE_VERSION_VAL` bumped `0x03`→`0x04`. `T12.j`'s statistical corpus check now
  measures a 15.6% mean Water fraction at `scale=9` (down from ~46%); `T12.k`'s direct `BL-0074`
  reproduction re-check confirms the literal reported case (`seed=0`, `scale=9`) now measures
  25.9% Water with real row-to-row variety, not the pre-fix near-total flood.
- **Authorization state: authorized 2026-07-11** (explicit user G3, `BL-0074` — "Yes, ship the
  fix (Recommended)," in direct response to a question naming the exact save-compatibility
  consequence). Treated as sufficient G3 authorization for `IP-9110` specifically, not requiring a
  second separate round — the question and answer were unambiguously about shipping this exact
  fix. `IP-9110` interacted with `IP-1070`'s own not-yet-`VERIFIED` maze pass (both consume
  `gw_prng_step`'s output) — named as a real risk in the package's own §13; the full suite
  (including `T19`'s own braid-fraction and oracle-parity checks) stayed green, confirming no
  adverse interaction, not merely trusting the pre-implementation simulation. Awaits
  `09-package-verification` (same-session independence rule — needs a fresh session).

### RIGHT zone-transition threshold fix (planned AND implemented 2026-07-12)

- **No critical path** — a single package, `IP-9120`, no split.
- **`IP-9120`** (`BL-0076`): a direct regression from this session's own `IP-9090`. `IP-9090`
  correctly lowered the RIGHT movement clamp's max reachable `PLAYER_X` from `159` to `152`
  (`BL-0052`), but `check_zone_transition`'s own RIGHT-edge trigger still required
  `PLAYER_X >= 156` — the two thresholds overlapped by coincidence under the old, buggy clamp and
  no longer did, so no player could transition rightward into a new zone through normal gameplay
  input, at all, in any generated world, as of `IP-9090`'s commit. **Reached `COMPLETE`
  2026-07-12** (224/224) — the single comparison-operand fix (`CP_n(156)`→`CP_n(152)`) implemented,
  new check `T7.11` added (a real button-press-driven positive-transition test, correcting an
  overshoot bug in its own first draft: holding the button for a fixed tick count let the player
  keep moving inside the *newly entered* zone too once the transition fired mid-hold — fixed by
  releasing on the `CUR_ZONE` change itself). Directly re-verified at `BL-0076`'s own original
  reproduction point (region 9, `seed=0`/`scale=9`): sustained real input now carries the player
  through multiple real transitions (9→10→11), where it previously stuck at 9 forever.
- **Authorization state: authorized 2026-07-12** (explicit user G3, `BL-0077` — "Yes, ship the fix
  (Recommended)," asked immediately given the Critical severity rather than letting it queue).
  Awaits `09-package-verification` (same-session independence rule — needs a fresh session).

### Zone-transition intent gate (planned AND implemented 2026-07-12)

- **No critical path** — a single package, `IP-9130`, no split.
- **`IP-9130`** (`BL-0078`): `check_zone_transition`'s four branches were purely position-based —
  none tested whether the player was actually holding the corresponding direction. Confirmed
  reproducible at the literal default game start (walk RIGHT until blocked, then DOWN only — the
  next region fired a spurious RIGHT transition since `PLAYER_X` was still at the clamp ceiling),
  invisible under the old full-lattice model but reachable now that the maze pass (`IP-1070`)
  makes open/blocked vary per-region rather than uniform per column. **Reached `COMPLETE`
  2026-07-12** (226/226) — all four branches gated on their own `JOY_CUR` direction bit,
  symmetric across all four directions by direct code read (not just the reported RIGHT case).
  Supersession sweep of `test_rom.py` found exactly two sites needing updates (`T11.a2`, the
  shared `_t17_do_move` helper) — a second overshoot bug (the same class `T7.11` hit) surfaced
  in `_t17_do_move` during implementation, fixed the same way (release on the `CUR_ZONE` change
  itself). New check `T7.12`. Directly re-verified at `BL-0078`'s own exact reported sequence:
  walking right-then-down now correctly settles in the down-neighbor zone with no spurious
  follow-on transition, while a genuine rightward press still transitions correctly.
- **Authorization state: authorized 2026-07-12** (explicit user G3, `BL-0079` — "Yes, ship the
  fix (Recommended)"). Awaits `09-package-verification` (same-session independence rule — needs
  a fresh session).
