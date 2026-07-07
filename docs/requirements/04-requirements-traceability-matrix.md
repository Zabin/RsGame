# RQ-04 — Requirements Traceability Matrix

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by `04-requirements-engineering`.
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
| FR-1150 | PLAYING↔MAP transition | — | GDS-01 §4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.6/T4.7 |
| FR-1160 | PLAYING→VICTORY→TITLE transition | — | GDS-01 §4; GDS-05 C4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.8/T4.9/T4.10 |
| FR-2100 | Continuous fixed-speed movement | R202 | GDS-05 C2 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T7.1–T7.7 |
| FR-2200 | Facing-direction tracking | — | GDS-04; GDS-05 C2 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T7.2/T7.4, T6.5/T6.6 |
| FR-2300 | Zone-boundary transition on valid neighbor | — | GDS-05 C2; GDS-04 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T9.2–T9.13 (all four edges) |
| FR-2310 | No transition at grid boundary | — | GDS-05 C2 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T7.9/T7.10, T9.5/T9.11/T9.14 |
| FR-2320 | On-screen transition-edge signaling | R203 | GDS-05 C2 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-3100 | Collection-proximity detection | R202 | GDS-05 C3 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T8.4 |
| FR-3200 | ScoreItem collection increments Score | — | GDS-05 C3; GDS-04 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T8.4/T8.5/T8.6/T8.10 (postcondition inaccuracy tracked as BL-0022) |
| FR-3210 | Carrot collection sets zone flag, increments CarrotCount | — | GDS-05 C3; GDS-04 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T8.7/T8.8/T8.9 |
| FR-3300 | Victory condition (CarrotCount==9) | — | GDS-05 C4 | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | T4.8, T8.14 |
| FR-4100 | Fixed 3×3 zone grid | — | GDS-04; GDS-01 §3 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | T1.10, T9 (grid edges) |
| FR-4200 | Fourteen total screens | — | GDS-04; GDS-05 C6 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-5100 | Explicit player-initiated save | R106; R205 | GDS-05 C5; GDS-06 N3 | ADR-0006 | `asm_game.py` | UNASSIGNED | UNASSIGNED | T10.3–T10.5, T10.13/T10.14 |
| FR-5200 | Restore save-field set on valid-save boot | R106 | GDS-05 C5; GDS-06 N3 | ADR-0006 | `asm_game.py` | UNASSIGNED | UNASSIGNED | T10.6–T10.12 |
| FR-5210 | Fields explicitly outside the persisted save set (facing/frame only, as of 2026-07-07) | — | GDS-05 C5; BL-0018 (resolved) | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-5220 | Persist per-zone ScoreItem collected-state (new, 2026-07-07) | — | user decision 2026-07-07; BL-0018 (resolved) | ADR-0006 | `asm_game.py` | FS-101 | IP-1010 | **T11.a–e** — trustworthy, 125/125 pass |
| FR-6100 | Zone screen composition | R203 | GDS-05 C6; GDS-08 §1 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | T5.9 |
| FR-6200 | Persistent row-0 HUD | R204 | GDS-05 C6; GDS-08 §3 | — | `asm_game.py`/`tilemaps.py` | UNASSIGNED | UNASSIGNED | T5.4–T5.8 |
| FR-6300 | Five non-zone UI screens | — | GDS-05 C6; GDS-04 | — | `tilemaps.py` | UNASSIGNED | UNASSIGNED | T5.1–T5.3, T4.4/T4.6/T4.8 (screens reached) |
| CR-01 | Full save-field persistence — **RESOLVED/SPLIT 2026-07-07**: facing/frame half REJECTED (no row — see FR-5210); ScoreItem half APPROVED → see **FR-5220** row above | — | GDS-05 C5; BL-0018 (resolved) | — | `asm_game.py` | `RESOLVED — SEE FR-5220` | `RESOLVED — SEE FR-5220` | `RESOLVED — SEE FR-5220` |
| CR-02 | Carrot-invariant enforcement | — | GDS-04; BL-0017 | — | `tilemaps.py` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |

## Non-Functional Requirements

| Req ID | Title | Research Source | Architecture Section | ADR | Module | Feature Spec | Implementation Package | Test |
|---|---|---|---|---|---|---|---|---|
| NFR-1100 | VBlank-gated PPU access | R102 | GDS-06 N2 | ADR-0005 | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based, no automated check exists) |
| NFR-1200 | Score-bar write timing (BL-0003/BL-0008) | — | GDS-06 N2 | — | `asm_game.py` | UNASSIGNED | IP-9020 | **T8.10a, T8.10b** — trustworthy, 111/111 pass |
| NFR-2100 | Deterministic state-machine behavior | — | GDS-01 §4 (derived) | — | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3100 | One-job-per-file module boundary | — | GDS-03 | ADR-0003 | all six modules | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based) |
| NFR-4000 | 32768-byte single-bank ROM budget | — | GDS-06 N1; GDS-02 | ADR-0001 | `build_rom.py` | UNASSIGNED | UNASSIGNED | **T1.1** ("ROM size = 32768") — trustworthy, T1 suite |
| NFR-4100 | CGB palette budget | R104 | GDS-06 N1; GDS-07; GDS-08 §4 | — | `build_rom.py`/`tiles.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based) |
| NFR-5100 | MBC1 SRAM enable/disable bracketing | R106 | GDS-06 N3 | ADR-0006 | `asm_game.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based) |
| NFR-5200 | Save-field round-trip integrity | — | GDS-06 N3 | ADR-0006 | `asm_game.py` | FS-101 | IP-1010 | **T10.7–T10.12, T11.b5/T11.c/T11.e1/T11.d** — trustworthy, full field set incl. SCOREITEM_FLAGS, 125/125 pass |
| NFR-6100 | PyBoy headless as verification target | R301 | GDS-02; A2 | ADR-0008 | `run-bunnygarden` harness | UNASSIGNED | UNASSIGNED | UNASSIGNED (inspection-based) |
| NFR-7100 | Full, currently-accurate test suite as completion gate | — | GDS-06 N5 | — | `test_rom.py` | UNASSIGNED | UNASSIGNED | **T1–T10, 109/109 pass** (IP-9010, 2026-07-07 — this NFR's own remediation; was BL-0006) |
| NFR-8100 | Byte-identical deterministic rebuild | — | GDS-06 N4 | ADR-0002 | `build_rom.py` | UNASSIGNED | UNASSIGNED | Confirmed by direct rebuild-and-diff during MSTR-001 §8's correction — not a `test_rom.py` check; UNASSIGNED as an automated Test cell |
| CR-03 | Bank-switching-ready extensibility standard | — | ADR-0001; MSTR-001 C7 | ADR-0001 | `build_rom.py`/`gbc_lib.py` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |
| CR-04 | Real-hardware/second-emulator verification standard | — | A2 | ADR-0008 | `run-bunnygarden` harness | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` | `CANDIDATE — NOT BASELINED` |

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
