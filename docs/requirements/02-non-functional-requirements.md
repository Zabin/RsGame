# RQ-02 — Non-Functional Requirements

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by `04-requirements-engineering`.
> Derives from [GDS-06](../architecture/06-non-functional-requirements.md)'s five NFRs (N1–N5) —
> formalized into numbered `NFR-xxxx` requirements per
> [GDS-10](../architecture/10-requirements-traceability-matrix.md) §3's citation contract. **This
> document preserves GDS-06's honest compliance status per requirement** — an NFR marked
> "Status: not met" below is a real, tracked gap (with its backlog ID), never silently presented
> as satisfied. Priority scale: Must / Should / Could, same as RQ-01.

## Performance

### NFR-1100 — VBlank-gated PPU access (structural requirement)

- **ID:** NFR-1100
- **Title:** The system shall confine all VRAM/OAM writes to periods when the LCD is off or a
  confirmed-VBlank window is active.
- **Description:** Every write to VRAM or OAM shall occur either while the LCD is disabled or
  during a window confirmed to be VBlank (via the STAT/LY mechanism), to avoid PPU-visible
  corruption or undefined behavior.
- **Rationale:** GDS-06 N2; R102.
- **Priority:** Must
- **Acceptance Criteria:** Every VRAM/OAM write in the codebase occurs inside a block gated by
  LCD-off or a confirmed-VBlank check.
- **Verification Method:** Inspection (static code audit of every VRAM/OAM write site) / Test
  (where a PyBoy-observable timing violation is feasible to construct).
- **Source Documents:** GDS-06 N2; R102.
- **Related ADRs:** ADR-0005 (shadow-OAM DMA every frame — the mechanism most writes rely on to
  satisfy this NFR).
- **Notes:** See NFR-1200 for this requirement's current, honestly-tracked non-compliance.

### NFR-1200 — Score-bar write timing (current compliance gap)

- **ID:** NFR-1200
- **Title:** The score-bar HUD's VRAM write shall be gated by NFR-1100's VBlank discipline.
- **Description:** The row-0 HUD's score-digit VRAM write (FR-6200) shall occur only within a
  confirmed-VBlank window, consistent with every other VRAM write in the system.
- **Rationale:** GDS-06 N2, citing `Claude.md`'s original bug note.
- **Priority:** Must
- **Status: MET (2026-07-07, via `IP-9020` — pending independent verification by
  `09-package-verification`).** The `CALL('update_status_disp')` was relocated from `st_playing`
  (an unbounded distance into the frame) to the main loop's frame top, immediately after
  `VBLANK_FLAG` is cleared and before the `NEED_REDRAW`/`do_screen_redraw` dispatch —
  guaranteeing the write lands within the VBlank window (R102). The routine's existing internal
  `GAMESTATE`/`SCORE_DIRTY` guards make the unconditional call-site safe in every state. Accepted
  side effect: `SCORE_DIRTY` set during frame N is now drawn at the top of frame N+1 (previously
  same-frame) — no requirement states same-frame HUD latency. Evidence:
  [IP-9020](../implementation/packages/IP-9020-score-bar-vblank-fix.md); `test_rom.py` T8.10a/
  T8.10b force-dirty the HUD fields and confirm the digit tiles reflect the new values within 2
  frames; full suite **111/111 pass** (`test_results.txt`, regenerated 2026-07-07).
  *Historical note (pre-2026-07-07):* the write was called from `st_playing`, at an unbounded
  distance from the VBlank wake-up — a real correctness gap against actual hardware timing, even
  though it produced no observable corruption under headless PyBoy emulation.
- **Acceptance Criteria:** The score-bar write occurs only inside a confirmed-VBlank/LCD-off
  window, verified by static inspection of the write site.
- **Verification Method:** Test (`test_rom.py` T8.10a/T8.10b) / Inspection (call-site relocation
  confirmed directly against `asm_game.py`).
- **Source Documents:** GDS-06 N2; `Claude.md`'s "Remaining Known Issues" note (credited as this
  finding's origin, per GDS-06's merge decision).
- **Related ADRs:** None.
- **Notes:** Remediated by **IP-9020** (closes **BL-0003**, part of the umbrella remediation
  entry **BL-0008**).

## Reliability

### NFR-2100 — Deterministic state-machine behavior

- **ID:** NFR-2100
- **Title:** The game-state machine shall behave deterministically for a given input sequence.
- **Description:** Given an identical sequence of inputs from an identical starting state, the
  system shall always reach the same resulting state and game-data values — no reliance on
  uninitialized memory or unspecified timing races for game-state-affecting behavior.
- **Rationale:** Implied by FR-1xxx's testability requirement and by NFR-4100 (build determinism)
  — a non-deterministic state machine would make both meaningless. No single GDS-06 line states
  this explicitly; it is derived from the FR baseline's own testability demands.
- **Priority:** Must
- **Acceptance Criteria:** Replaying an identical input sequence from an identical starting save
  state produces identical resulting state-machine and game-data values, run to run.
- **Verification Method:** Test.
- **Source Documents:** GDS-01 §4 (implied); GDS-05 (FR testability demands this).
- **Related ADRs:** None.
- **Notes:** This is a derived requirement, not a direct GDS-06 citation — flagged honestly per
  the writing rule that "implied by the architecture" is not itself a citation; the citation here
  is to the FR baseline's own testability need, which is a legitimate source.

## Maintainability

### NFR-3100 — One-job-per-file module boundary

- **ID:** NFR-3100
- **Title:** The codebase shall maintain strict one-job-per-file module boundaries.
- **Description:** Each of the six modules (`gbc_lib.py`, `tiles.py`, `tilemaps.py`, `music.py`,
  `asm_game.py`, `build_rom.py`) shall retain a single clear responsibility; data-authoring
  modules shall not make assembly decisions or call the assembler substrate's emission methods
  directly beyond what the interface contract (GDS-09) names, and the orchestrator
  (`build_rom.py`) shall contain no game logic.
- **Rationale:** GDS-03; ADR-0003.
- **Priority:** Must
- **Acceptance Criteria:** For each module, its responsibilities remain within the single
  category GDS-03/ADR-0003 assigns it; a change to one module's category of concern does not
  require touching another module's core responsibility.
- **Verification Method:** Inspection (code review against the module-boundary rule at each
  change).
- **Source Documents:** GDS-03; ADR-0003.
- **Related ADRs:** ADR-0003.
- **Notes:** None.

## ROM/RAM budget

### NFR-4000 — 32768-byte single-bank ROM budget

- **ID:** NFR-4000
- **Title:** The ROM shall fit within a single 32768-byte bank.
- **Description:** The built ROM file shall be exactly 32768 bytes, with no bank-switching
  (assumption A1).
- **Rationale:** GDS-06 N1; GDS-02.
- **Priority:** Must
- **Status: MET.** 23148 of 32768 bytes used, confirmed directly; ~9.6KB headroom.
- **Acceptance Criteria:** A clean build produces a ROM file of exactly 32768 bytes.
- **Verification Method:** Test (`test_rom.py` T1.1, "ROM size = 32768" — a T1-suite check, which
  GDS-02 established as trustworthy evidence unlike T2–T10).
- **Source Documents:** GDS-06 N1; GDS-02; ADR-0001.
- **Related ADRs:** ADR-0001 (names this budget's future supersession trigger, commitment C7).
- **Notes:** This NFR does **not** anticipate C7's eventual bank-switching need — when that work
  is planned, this NFR will require a dated revision, not a silent redefinition, per the
  ladder's delta-update discipline.

### NFR-4100 — CGB palette budget (cross-referenced, not re-derived)

- **ID:** NFR-4100
- **Title:** BG/OBJ palette usage shall remain within the CGB's 8-BG/8-OBJ palette ceiling.
- **Description:** The system shall not require more than 8 BG palettes or 8 OBJ palettes
  concurrently.
- **Rationale:** GDS-06 N1 (cross-references R104/BL-0009 as a separate constraint from the ROM
  byte budget).
- **Priority:** Must
- **Status: MET**, with real but bounded headroom. 5 of 8 BG palettes currently serve zone
  terrain (organized by terrain family, with deliberate reuse); 4 of 8 OBJ palettes in active use.
- **Acceptance Criteria:** At no point does the system require simultaneous use of more than 8 BG
  palettes or more than 8 OBJ palettes.
- **Verification Method:** Inspection (palette table audit, as performed at GDS-07).
- **Source Documents:** GDS-06 N1; GDS-07; GDS-08 §4; BL-0009 (corrected finding).
- **Related ADRs:** None.
- **Notes:** Headroom in the ROM-byte budget (NFR-4000) does not imply headroom in this budget,
  and vice versa — the two must be checked independently for any future zone/content addition, per
  GDS-06 N1's explicit caution.

## Data Integrity

### NFR-5100 — MBC1 SRAM enable/disable bracketing

- **ID:** NFR-5100
- **Title:** Every SRAM access shall be bracketed by the MBC1 enable ($0A)/disable ($00) sequence.
- **Description:** Any read or write to SRAM shall be preceded by writing $0A to the RAM-enable
  register and followed by writing $00 to disable it, per MBC1's hardware contract.
- **Rationale:** GDS-06 N3; R106.
- **Priority:** Must
- **Status: MET.** Confirmed directly against both the save and load routines.
- **Acceptance Criteria:** Every SRAM read/write site in the codebase is preceded by the enable
  sequence and followed by the disable sequence, with no SRAM access occurring outside that
  bracket.
- **Verification Method:** Inspection.
- **Source Documents:** GDS-06 N3; R106.
- **Related ADRs:** ADR-0006.
- **Notes:** None.

### NFR-5200 — Save-field round-trip integrity

- **ID:** NFR-5200
- **Title:** Whatever field set the system declares persisted shall round-trip correctly through
  a save/load cycle.
- **Description:** For the currently-declared save-field set — {CurrentZone, PlayerPosition,
  CarrotCount, Score, CarrotFlags[9], per-zone ScoreItem collected-state} as of the 2026-07-07
  widening (FR-5220) — a save followed by a load shall restore each field to exactly the value it
  held at save time.
- **Rationale:** GDS-06 N3; FR-5220 (widened field set).
- **Priority:** Must
- **Status: MET** for the pre-widening field set (confirmed directly); **not yet independently
  verified** for the newly-added per-zone ScoreItem field (FR-5220 has no implementation yet — see
  RQ-04). This NFR remains scoped to *whatever fields are declared persisted*, which as of
  2026-07-07 explicitly includes per-zone ScoreItem state per the user's decision resolving
  BL-0018 (now `DONE`) — facing direction and animation frame remain explicitly excluded
  (FR-5210), not an open question.
- **Acceptance Criteria:** For each field in {CurrentZone, PlayerPosition, CarrotCount, Score,
  CarrotFlags[9], per-zone ScoreItem collected-state}, saving then loading yields an identical
  value.
- **Verification Method:** Test.
- **Source Documents:** GDS-06 N3; FR-5220.
- **Related ADRs:** ADR-0006.
- **Notes:** Re-verify this NFR's "Met" status once FR-5220 is implemented (stage 08) — its
  compliance claim currently covers only the pre-widening field set.

## Portability

### NFR-6100 — PyBoy headless as the verification target

- **ID:** NFR-6100
- **Title:** The system's automated verification shall target the PyBoy headless emulator; real
  hardware behavior is expected to match but is not itself gated.
- **Description:** All automated `test_rom.py` checks shall run against PyBoy headless emulation.
  Real-hardware divergence is not currently gated against, per strategic assumption A2.
- **Rationale:** GDS-02; assumption A2; R301.
- **Priority:** Must (as-built scope)
- **Acceptance Criteria:** The test harness runs to completion under PyBoy headless with no
  real-hardware or second-emulator dependency required for a pass/fail determination.
- **Verification Method:** Inspection (harness configuration).
- **Source Documents:** GDS-02; strategic-assumptions-register A2; ADR-0008.
- **Related ADRs:** ADR-0008.
- **Notes:** A2's stated trigger condition (a credible real-hardware/second-emulator divergence
  report, or a physical flash-cart release) would require revisiting this NFR's scope — not a
  current requirement, a documented future contingency.

## Usability

*(none derivable from inputs — see Candidate Requirements. No source document states a
player-facing usability standard beyond what FR-6xxx's presentation requirements already cover as
functional behavior.)*

## Testability

### NFR-7100 — Full, currently-accurate automated test suite as a completion gate

- **ID:** NFR-7100
- **Title:** The system shall have a full, currently-accurate automated test suite that passes
  before any implementation package is considered complete.
- **Description:** Every implementation package (stage 07/08) shall be gated on a test suite whose
  assertions reflect the current, as-built game semantics — not a suite that once passed against
  a prior version of the game.
- **Rationale:** GDS-06 N5; rule G5 (`.claude/skills/README.md`).
- **Priority:** Must
- **Status: MET (2026-07-07, via IP-9010 — pending independent verification by
  `09-package-verification`).** `test_rom.py` was rewritten in full against the current, as-built
  Bunny Quest semantics ([IP-9010](../implementation/packages/IP-9010-test-suite-rewrite.md),
  closing BL-0006/BL-0005): T1 retained per R304; T2–T10 rewritten against the current WRAM
  model (GDS-07) and tile/zone data; all paths repo-relative. Current evidence: **109/109 checks
  pass** against a freshly built, byte-identical ROM (`test_results.txt`, regenerated 2026-07-07).
  *Historical note (pre-2026-07-07):* the prior suite asserted pre-rewrite (Bunny Garden
  Adventure, 3-zone/gift-model) semantics, and its "88/88 passed" figure predated the semantic
  drift — that figure was never evidence of compliance.
- **Acceptance Criteria:** Every check in `test_rom.py` asserts a behavior that matches the
  current, as-built game semantics (verified independently against direct source reads, not
  against the suite's own historical pass/fail record).
- **Verification Method:** Test (once remediated) / Inspection (current state: audit each T2–T10
  check against current source, as GDS-02/GDS-05/GDS-06 already began).
- **Source Documents:** GDS-06 N5; GDS-02.
- **Related ADRs:** None.
- **Notes:** Was tracked as **BL-0006** (Critical), folded into **BL-0008**; remediated by
  **IP-9010** (2026-07-07). Do not cite the pre-rewrite historical pass count ("88/88") as
  compliance evidence in any future document — current evidence is the regenerated
  `test_results.txt` produced by the rewritten suite.

## Build Reproducibility

### NFR-8100 — Byte-identical deterministic rebuild

- **ID:** NFR-8100
- **Title:** A clean rebuild from a given source tree shall be byte-identical to any
  previously-shipped ROM built from that same tree.
- **Description:** Running the build pipeline (`build_rom.py`) against an unchanged source tree
  shall always produce a bit-for-bit identical ROM file.
- **Rationale:** GDS-06 N4.
- **Priority:** Must
- **Status: MET.** Confirmed directly during the vision correction: a fresh build matched the
  checked-in `BunnyQuest.gbc` exactly, byte-for-byte.
- **Acceptance Criteria:** Two independent builds from the same unchanged source tree produce
  identical ROM files (verified by byte comparison).
- **Verification Method:** Test.
- **Source Documents:** GDS-06 N4; MSTR-001 §8.
- **Related ADRs:** ADR-0002 (the Python-assembler approach this determinism depends on).
- **Notes:** None.

## Extensibility

*(none derivable from inputs as a numbered NFR — GDS-06 does not state an extensibility standard
directly. C7's world-scale target is a vision-layer commitment, not yet a stated NFR; see
Candidate Requirements.)*

## Candidate Requirements

### CR-03 — Bank-switching-ready extensibility standard

- **Description:** A future NFR requiring the codebase's build pipeline to support multi-bank ROM
  layouts without a wholesale rewrite, anticipating C7's world-scale target.
- **Why excluded:** No current GDS-06 statement establishes this as a present standard — NFR-4000
  documents the current single-bank reality and explicitly flags C7 as the future trigger for a
  *dated revision*, not a present requirement.
- **Disposition:** Held pending `03-architecture-design-synthesis` scoping the bank-switching
  architecture (referenced at ADR-0001), or `05-feature-decomposition` scheduling it as a release
  bucket.

### CR-04 — Real-hardware/second-emulator verification standard

- **Description:** A future NFR requiring automated verification against real hardware or a
  second independent emulator, superseding NFR-6100's current PyBoy-only scope.
- **Why excluded:** Assumption A2 explicitly defers this until a concrete trigger condition fires;
  no current source requires it.
- **Disposition:** Held pending A2's trigger condition (credible divergence report, or a physical
  flash-cart release plan) — owner: the user.
