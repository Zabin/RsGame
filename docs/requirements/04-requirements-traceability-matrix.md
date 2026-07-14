# RQ-04 — Requirements Traceability Matrix

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment — 17 new rows, target requirements; delta 2026-07-10 — FR-6400 added (BL-0020),
> Feature Spec/Implementation Package columns filled for the 17 target rows now that
> `06`/`07` have run, NFR-6100/NFR-1200/NFR-7100/NFR-5200 Test cells refreshed; delta 2026-07-11
> — NFR-6500/6510 Test cells filled with real evidence, `BL-0045`; delta 2026-07-11 —
> FR-9140/9150/2330 and CR-05 added for `ADR-0012`'s maze-adjacency decision, `BL-0064`–`BL-0067`;
> delta 2026-07-12 — FR-9160/9161 added for `ADR-0015`'s win-condition redesign, `BL-0093`;
> delta 2026-07-13 — CR-06 added for the edge-indicator legend screen request, `BL-0100`, un-
> baselined pending a `03-architecture-design-synthesis` pass; delta 2026-07-13 (cont'd) —
> FR-1200/FR-1210 added once GDS-01 §4c/GDS-08 §11 landed, `CR-06` resolved/baselined; delta
> 2026-07-13 (cont'd) — FR-10100–10500, NFR-1400/2300/4300/5400, and CR-07 added for the
> Infinite Mode epic, `ADS-001`/`ADR-0016`/`ADR-0017`/`BL-0094`/`BL-0106`).**
> Owned by `04-requirements-engineering`.
> One row per [RQ-01](01-functional-requirements.md)/[RQ-02](02-non-functional-requirements.md)
> requirement (Candidates marked). Populates the row-level matrix
> [GDS-10](../architecture/10-requirements-traceability-matrix.md) §3 deferred to this stage, using
> its origin → requirement → feature → implementation → verification row shape and its
> `BL-xxxx`-as-cross-cutting-lane convention. **Forward columns (Feature Spec, Implementation
> Package, Test) are `UNASSIGNED` where stages 05–09 haven't run yet** — this is the honest,
> expected state on the bootstrap increment, not a defect. The Test column is filled where
> `test_rom.py`'s T1 suite (the only suite GDS-02 established as trustworthy, per BL-0006) already
> provides real, current evidence; every other Test cell is marked per RQ-03 finding #3.

## Functional Requirements

| Req ID | Title | Research Source | Architecture Section | ADR | Module | Feature Spec | Implementation Package | Test |
|---|---|---|---|---|---|---|---|---|
| FR-1100 | Six-state game-state machine | — | GDS-01 §4; GDS-05 C1 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | `test_rom.py` T4 (compliant, IP-9010 2026-07-07) |
| FR-1110 | Clean-boot start state | — | GDS-01 §4; GDS-05 C1 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.1, T10.1 |
| FR-1120 | Auto-load-on-boot bypass | R106 | GDS-01 §4; GDS-05 C1 | ADR-0006 | `asm_game.py` | UNASSIGNED | UNASSIGNED | T10.6 |
| FR-1130 | TITLE→INTRO→PLAYING transition | — | GDS-01 §4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.2/T4.3 |
| FR-1140 | PLAYING↔SAVE transition | — | GDS-01 §4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.4/T4.5 |
| FR-1150 | PLAYING↔MAP transition (SELECT clause target-superseded by FR-1200, not yet implemented) | — | GDS-01 §4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.6/T4.7 |
| FR-1160 | PLAYING→VICTORY→TITLE transition | — | GDS-01 §4; GDS-05 C4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.8/T4.9/T4.10 |
| FR-2100 | Continuous fixed-speed movement | R202 | GDS-05 C2 | — | `asm_game.py` | UNASSIGNED | IP-9090 | T7.1–T7.7, T7.8/T7.8b/T7.10/T7.10b (boundary-clamp fix) |
| FR-2200 | Facing-direction tracking | — | GDS-04; GDS-05 C2 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T7.2/T7.4, T6.5/T6.6 |
| FR-2300 | Zone-boundary transition on valid neighbor | — | GDS-05 C2; GDS-04 | — | `asm_game.py` | UNASSIGNED | IP-9050, IP-9120, IP-9130 | T17.a–b (all four edges, scale=5 + scale=3 regression — supersedes retired T9.2–T9.13, `IP-9050`), T7.11 (real button-press-driven RIGHT transition, `IP-9120`), T7.12 (no spurious transition on a perpendicular approach, `IP-9130`) |
| FR-2310 | No transition at grid boundary | — | GDS-05 C2 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T7.9/T7.10, T17.c (supersedes retired T9.5/T9.11/T9.14, `IP-9050`) |
| FR-2320 | On-screen transition-edge signaling (superseded by FR-2330, implemented 2026-07-13) | R203 | GDS-05 C2 | — | `asm_game.py` (`draw_region_arrows`, post-`IP-1030` runtime port; `tilemaps.py`'s own build-time `_zone_arrows` retired) | UNASSIGNED | IP-1030 (base implementation); IP-9140 (right-arrow off-screen position fix, `BL-0084`) | T13.a–d |
| FR-2330 | Three-state transition-edge signaling for a maze-shaped world (implemented 2026-07-13) | — | ADR-0012 point 2 | ADR-0009, ADR-0012 | `asm_game.py`, `tiles.py` | FS-108 | IP-1080 (logic half), IP-1081 (content), IP-1082 (render) | T20.a–e |
| FR-3100 | Collection-proximity detection | R202 | GDS-05 C3 | — | `asm_game.py` | UNASSIGNED | IP-9100 | T8.4, T8.x/T8.y/T8.z1/T8.z2 (corrected point-in-box overlap test) |
| FR-3200 | ScoreItem collection increments Score | — | GDS-05 C3; GDS-04 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T8.4/T8.5/T8.6/T8.10 — trustworthy; postcondition corrected 2026-07-10 (`BL-0022`) to match shipped respawn-on-re-entry behavior |
| FR-3210 | Carrot collection sets zone flag, increments CarrotCount | — | GDS-05 C3; GDS-04 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T8.7/T8.8/T8.9 |
| FR-3300 | Victory condition (CarrotCount==9; superseded by FR-9161, implemented 2026-07-13) | — | GDS-05 C4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.8, T8.14 |
| FR-4100 | Fixed 3×3 zone grid | — | GDS-04; GDS-01 §3 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | T1.10, T9 (grid edges) |
| FR-4200 | Fourteen total screens | — | GDS-04; GDS-05 C6 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-5100 | Explicit player-initiated save | R106; R205 | GDS-05 C5; GDS-06 N3 | ADR-0006 | `asm_game.py` | UNASSIGNED | UNASSIGNED | T10.3–T10.5, T10.13/T10.14 |
| FR-5200 | Restore save-field set on valid-save boot | R106 | GDS-05 C5; GDS-06 N3 | ADR-0006 | `asm_game.py` | UNASSIGNED | UNASSIGNED | T10.6–T10.12 |
| FR-5210 | Fields explicitly outside the persisted save set (facing/frame only, as of 2026-07-07) | — | GDS-05 C5; BL-0018 (resolved) | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-5220 | Persist per-zone ScoreItem collected-state (new, 2026-07-07; storage generalized to the full generated-region range 2026-07-11) | — | user decision 2026-07-07; BL-0018 (resolved); BL-0058 (resolved) | ADR-0006 | `asm_game.py` | FS-101 | IP-1010, IP-9070 | **T11.a–e**, **T16.a–e** — trustworthy, 231/231 pass |
| FR-6100 | Zone screen composition | R203 | GDS-05 C6; GDS-08 §1 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | T5.9 |
| FR-6200 | Persistent row-0 HUD | R204 | GDS-05 C6; GDS-08 §3 | — | `asm_game.py`/`tilemaps.py` | UNASSIGNED | UNASSIGNED | T5.4–T5.8 |
| FR-6300 | Five non-zone UI screens | — | GDS-05 C6; GDS-04 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | T5.1–T5.3, T4.4/T4.6/T4.8 (screens reached) |
| FR-6400 | Player and collectible sprite rendering (added 2026-07-10, BL-0020) | — | GDS-08 §2 | ADR-0005, ADR-0007 | `asm_game.py` | UNASSIGNED | UNASSIGNED | T6.1–T6.10 — trustworthy, pre-existing evidence, formal requirement only |
| CR-01 | Full save-field persistence — **RESOLVED/SPLIT 2026-07-07**: facing/frame half REJECTED (no row — see FR-5210); ScoreItem half APPROVED → see **FR-5220** row above | — | GDS-05 C5; BL-0018 (resolved) | — | `asm_game.py` | `RESOLVED — SEE FR-5220` | `RESOLVED — SEE FR-5220` | `RESOLVED — SEE FR-5220` |
| CR-02 | Carrot-invariant enforcement | — | GDS-04; BL-0017 | — | `tilemaps.py` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |
| CR-05 | Biome-blob clustering seeded from maze dead-ends (`BL-0066`) — conflicts with `ADR-0012` point 1's fixed biome-first pass ordering, per RQ-03 finding #13 | — | GDS-04; BL-0066 | ADR-0012 | `worldgen.py` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |
| CR-06 | Edge-indicator legend/help screen (`BL-0100`) — **RESOLVED 2026-07-13, baselined as FR-1200/FR-1210** once GDS-01 §4c/GDS-08 §11 landed | — | GDS-01 §4c; GDS-08 §11; BL-0100 | — | `asm_game.py`/`tilemaps.py` (prospective) | `CANDIDATE — NOT BASELINED` (see FR-1200/FR-1210) | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |
| FR-1170 | MAIN MENU state (Met, 2026-07-10; cursor-reset regression fixed 2026-07-11) | — | GDS-01 §2a/§4a | ADR-0010 | `asm_game.py` | FS-104 | IP-1040, IP-9060 | T14.a1–a4, T18.a–d — 231/231 pass |
| FR-1180 | New-game seed/scale entry + generation trigger (Met) | R111 | GDS-01 §4a | ADR-0009, ADR-0010 | `asm_game.py` | FS-104 | IP-1040 | T14.b1–b3, T14.c1 — 180/180 pass (T14 sub-total 20/20) |
| FR-1190 | Exit-to-main-menu with auto-save (Met) | — | GDS-01 §4a | — | `asm_game.py`, `tilemaps.py` | FS-104 | IP-1040, IP-9080 | T14.d1–d2 (behavior), T5.10–T5.12 (on-screen label, IP-9080) |
| FR-1200 | SELECT MENU state (Met, 2026-07-13, supersedes FR-1150's SELECT→MAP clause) | — | GDS-01 §4c | — | `asm_game.py`, `tilemaps.py` | FS-109 | IP-1090 | **T21.a1–a2, T21.b–d2, T4.6/T8.11/T14.e2 (corrected) — 246/246 pass** |
| FR-1210 | LEGEND state (Met, 2026-07-13) | — | GDS-08 §11 | — | `asm_game.py`, `tilemaps.py` | FS-109 | IP-1090 | **T21.e, T21.f1–f3 — 246/246 pass** |
| FR-3220 | Item-agnostic KeyItem collection (generalizes FR-3210) | — | GDS-04 delta | ADR-0009 | `asm_game.py` | FS-102 | IP-1020 | T8.7, T8.8 (retargeted KEYITEM_FLAGS/KEYITEM_COUNT checks), T12.g (cross-reference) — 133/133 pass |
| FR-4300 | One biome per screen (Met — code half `IP-1030`, content half `IP-1031`, both 2026-07-10/11) | R212 | GDS-08 delta §8 | ADR-0009 | `asm_game.py`, `tilemaps.py` | FS-103 | IP-1030 (code), IP-1031 (content) | T13.a (tile-family audit, exercises both halves) — 180/180 pass |
| FR-4310 | Grammar-valid adjacency only | R212 | GDS-04 delta | ADR-0009 | `asm_game.py`, `worldgen.py` | FS-102 | IP-1020 | T12.d (15-entry seed/scale corpus, 0 illegal edges) |
| FR-9100 | Deterministic world generation from (seed, scale) | R111, R213 | GDS-04 delta; ADR-0009 | ADR-0009, ADR-0014 | `asm_game.py`, `worldgen.py` | FS-102 | IP-1020, IP-9110 | T12.a (two-boot determinism), T12.b (oracle parity), T12.e (region count), T12.j (non-degeneracy statistical check), T12.k (BL-0074 direct reproduction re-check) |
| FR-9110 | Seed/scale immutable per save, new-game-only (Met, 2026-07-10) | — | ADR-0010 | ADR-0010 | `asm_game.py` (only `sse_compose_seed`, reachable only via `st_seed_scale_entry`'s A-confirm, writes `SEED`/`WORLD_SCALE`) | FS-102, FS-104 | IP-1020, IP-1040 | T14.e1 (static write-site audit), T14.e2 (runtime sweep, PLAYING/SAVE/MAP) — 180/180 pass (T14 sub-total 20/20) |
| FR-9120 | Full reachability of every generated region | — | GDS-04 delta; ADR-0009 | ADR-0009 | `worldgen.py` | FS-102 | IP-1020 | T12.c (BFS from region 0, 15-entry corpus, 0 unreachable) |
| FR-9130 | Exactly one KeyItem per generated region (generalizes BL-0017; superseded by FR-9160, implemented 2026-07-13) | — | GDS-04 delta; BL-0017 | ADR-0009 | `worldgen.py` | FS-102 | IP-1020 | T12.m (region count == scale², 15-entry corpus) |
| FR-9140 | Maze-shaped region adjacency (implemented — 2026-07-11) | R112, R113 | GDS-04 delta; GDS-07 §7b | ADR-0009, ADR-0012, ADR-0013 | `worldgen.py`, `asm_game.py` | FS-107 | IP-1070 | T19.a (subgraph), T19.b (reachability), T19.c (oracle parity), T19.d (grammar), T19.f (static audit), T19.g (WRAM headroom); T17.a/b (non-regression navigation) |
| FR-9150 | Braid-fraction parameter (implemented — 2026-07-11) | R112 | — | ADR-0012 | `worldgen.py`, `asm_game.py` | FS-107 | IP-1070 | T19.e (braid-fraction statistical check) |
| FR-9160 | Scale-relative, dead-end-prioritized KeyItem placement (implemented 2026-07-13, supersedes FR-9130) | R215 | GDS-04 delta (2026-07-12 correction); GDS-07 §7c | ADR-0015, ADR-0012, ADR-0009 | `asm_game.py`, `worldgen.py` | FS-102 | IP-1021 | T12.e (revised), T12.n |
| FR-9161 | Scale-relative victory condition (implemented 2026-07-13, supersedes FR-3300) | R215 | — | ADR-0015 | `asm_game.py` | FS-102 | IP-1021 | T4.8 (corrected), T12.n |
| FR-9200 | Save-format extension: seed/scale/region-flags (Met, 2026-07-10) | R106 (ext.) | GDS-07 delta §7 | ADR-0010, ADR-0006 | `asm_game.py` | FS-105 | IP-1050 | T15.a1–a6, T15.c1–c6, T15.d — 180/180 pass |
| FR-10100 | Infinite Mode new-game entry (seed-only, no world-scale) | — | ADS-001 §System Architecture | ADR-0016 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-10200 | Streaming, positionally-deterministic region generation | R114 | ADS-001 §System Architecture | ADR-0016 | `asm_game.py`/`worldgen.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-10210 | Revisit-consistent region materialization | R114 | ADS-001 §User Stories | ADR-0016 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-10300 | Treasure placement decoupled from maze structure | R216 | ADS-001 §System Architecture | ADR-0017 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-10400 | Score-chasing win condition (running count + top-3, no name entry) | R216 | ADS-001 §Executive Design Overview | ADR-0017 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-10500 | Visited-region-ledger save/load (position + collected-state only) | R114 | ADS-001 §System Architecture | ADR-0016 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-07 | Infinite Mode run/session shape — indefinitely resumable vs. bounded run with a new end-condition mechanic (`BL-0106`) — genuine missing concept, not yet decided, per RQ-03 finding #17 | R216 | GDS-01 (prospective delta) | ADR-0017 | `asm_game.py` (prospective) | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |

## Non-Functional Requirements

| Req ID | Title | Research Source | Architecture Section | ADR | Module | Feature Spec | Implementation Package | Test |
|---|---|---|---|---|---|---|---|---|
| NFR-1100 | VBlank-gated PPU access | R102 | GDS-06 N2 | ADR-0005 | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based, no automated check exists) |
| NFR-1200 | Score-bar write timing (BL-0003/BL-0008) | — | GDS-06 N2 | — | `asm_game.py` | UNASSIGNED | IP-9020 | **T8.10a, T8.10b** — trustworthy, VR-9020-confirmed, 125/125 pass today (111/111 at IP-9020's own commit) |
| NFR-2100 | Deterministic state-machine behavior | — | GDS-01 §4 (derived) | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3100 | One-job-per-file module boundary | — | GDS-03 | ADR-0003 | all six modules | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based) |
| NFR-4000 | 32768-byte single-bank ROM budget | — | GDS-06 N1; GDS-02 | ADR-0001 | `build_rom.py` | UNASSIGNED | UNASSIGNED | **T1.1** ("ROM size = 32768") — trustworthy, T1 suite |
| NFR-4100 | CGB palette budget | R104 | GDS-06 N1; GDS-07; GDS-08 §4 | — | `build_rom.py`/`tiles.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based) |
| NFR-5100 | MBC1 SRAM enable/disable bracketing | R106 | GDS-06 N3 | ADR-0006 | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based) |
| NFR-5200 | Save-field round-trip integrity (widened again 2026-07-10, `IP-1050`) | — | GDS-06 N3 | ADR-0006, ADR-0010 | `asm_game.py` | FS-101, FS-105 | IP-1010, IP-1050 | **T10.7–T10.12, T11.b5/T11.c/T11.e1/T11.d, T15.a3–a6/c1–c6** — trustworthy, full field set incl. SEED/WORLD_SCALE/KEYITEM_FLAGS, 180/180 pass |
| NFR-6100 | PyBoy headless as verification target | R301 | GDS-02; A2 | ADR-0008 | `run-bunnygarden` harness | UNASSIGNED | UNASSIGNED | **T1–T10 (full suite)** — every check runs headless via PyBoy, direct repeatable evidence (filled 2026-07-10, `BL-0026`; previously `UNASSIGNED` despite this evidence already existing) |
| NFR-7100 | Full, currently-accurate test suite as completion gate | — | GDS-06 N5 | — | `test_rom.py` | UNASSIGNED | UNASSIGNED | **T1–T10, 109/109 pass at IP-9010's own commit — 125/125 today** (IP-9010, 2026-07-07 — this NFR's own remediation, was BL-0006; count refreshed 2026-07-10 alongside NFR-1200's identical staleness, BL-0028) |
| NFR-8100 | Byte-identical deterministic rebuild | — | GDS-06 N4 | ADR-0002 | `build_rom.py` | UNASSIGNED | UNASSIGNED | Confirmed by direct rebuild-and-diff during MSTR-001 §8's correction — not a `test_rom.py` check; UNASSIGNED as an automated Test cell |
| CR-03 | Bank-switching-ready extensibility standard — **PARTIALLY SUPERSEDED 2026-07-09**: ADR-0011 now records the bank-switching *strategy* (MBC1 default wiring); this Candidate's remaining scope is the build-pipeline extensibility standard itself, not yet baselined | — | ADR-0001; ADR-0011; MSTR-001 C7 | ADR-0001, ADR-0011 | `build_rom.py`/`gbc_lib.py` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |
| CR-04 | Real-hardware/second-emulator verification standard | — | A2 | ADR-0008 | `run-bunnygarden` harness | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |
| NFR-1300 | Screen-transition smoothness for generated content (Met, 2026-07-10) | R102 (ext.) | GDS-08 delta §7; GDS-07 delta | ADR-0009 | `asm_game.py` | FS-103 | IP-1030 | T13.b (call-site audit, direct code read) — 136/136 pass |
| NFR-2200 | Deterministic world generation | R111 | ADR-0009; A9 | ADR-0009 | `worldgen.py`, `asm_game.py` | FS-102 | IP-1020 | T12.f (seed=0 normalization, direct WRAM inspection), T12.h (static no-DIV/no-external-read source scan) |
| NFR-4200 | Generated-world WRAM/SRAM headroom (WRAM half Met, `IP-1020`; SRAM half awaits `IP-1050`; maze-pass delta Met, `IP-1070`) | R111 | GDS-07 delta §6/§7, §7b | ADR-0010 | `asm_game.py` | FS-102, FS-107 | IP-1020 (WRAM), IP-1050 (SRAM), IP-1070 (maze-pass WRAM) | T12.i (WRAM extent inside bank-0 + boot-clear range, confirmed at scale=9); T19.g (maze-pass WRAM extent, confirmed at scale=9) |
| NFR-5300 | Save-format version bump for seed/scale/region-flags (Met, 2026-07-10) | R106 (ext.) | GDS-07 delta §7 | ADR-0010, ADR-0006 | `asm_game.py` | FS-105 | IP-1050 | T15.b1/b2/b3 — 180/180 pass |
| NFR-6500 | Aesthetic craft and clean-screen standard compliance (Met, 2026-07-11) | R209 | GDS-08 delta §7 | — | `tiles.py`/`tilemaps.py` | FS-106 | *(no package — see FS-106 §8/§10)* | `content-review-IP-1031.md` — clean, no findings |
| NFR-6510 | Biome-transition palette-stepping compliance (Met, 2026-07-11) | R212 | GDS-08 delta §8 | ADR-0009 | `build_rom.py`/`tiles.py` | FS-106 | *(no package — see FS-106 §8/§10)* | `content-review-IP-1031.md` — Met, 1 Low/informational note (Stone↔Brick pairing) |
| NFR-1400 | Infinite Mode region-materialization timing (status UNCONFIRMED) | R114 | ADS-001 §Non-functional Requirements | ADR-0016 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2300 | Positional determinism for Infinite Mode generation | R114 | ADS-001 §System Architecture | ADR-0016 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-4300 | Infinite Mode materialized-window WRAM headroom (status NOT YET SIZED) | R114 | ADS-001 §System Architecture | ADR-0016 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-5400 | Infinite Mode visited-region-ledger integrity and bounded capacity (status NOT YET SIZED) | R114 | ADS-001 §System Architecture | ADR-0016 | `asm_game.py` (prospective) | UNASSIGNED | UNASSIGNED | UNASSIGNED |

## Notes on this matrix's honesty discipline

- **No cell in the Feature Spec / Implementation Package columns is anything but `UNASSIGNED`** —
  stages 05 (`05-feature-decomposition`) and 07 (`07-implementation-planning`) have not run.
  Filling these in now with a guessed future FS-xxx/IP-xxxx name would violate this skill's
  explicit prohibition on inventing forward references.
- **The Test column distinguishes three real states**, not two: (1) a genuinely trustworthy
  existing test (only `test_rom.py` T1, cited directly by ID), (2) a test that exists but is
  non-compliant per BL-0006 (named explicitly so a future reader doesn't mistake "a check with
  this name exists" for "this requirement is verified"), and (3) no automated check exists at all
  (plain `UNASSIGNED`).
- Every `BL-xxxx` reference in this matrix (BL-0003, BL-0006, BL-0008, BL-0009, BL-0017, BL-0018)
  is cited as GDS-10 §4 anticipated — a backlog ID functioning as a citable cross-cutting anchor,
  not a prose aside.
- **2026-07-09 delta:** the 16 new rows (FR-1170–FR-9200, NFR-1300–NFR-6510) all carry
  `UNASSIGNED` Feature Spec/Implementation Package/Test cells with an explicit "not yet
  implemented" annotation — these are target requirements for the adopted increment
  ([PLAN-requirements-aesthetics-story-map.md](../pipeline/PLAN-requirements-aesthetics-story-map.md)),
  none of which has reached stage 05 yet. Module cells are marked `(proposed)` where GDS-09's
  delta names a new module (`worldgen.py`) or an extension to an existing one, distinguishing
  "this is where it will live" from the existing rows' "this is where it does live."
