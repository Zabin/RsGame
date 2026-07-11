# RQ-02 — Non-Functional Requirements

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 for the procgen-world
> increment, NFR-1300/2200/4200/5300/6500/6510; delta 2026-07-11 — NFR-6500/6510 flipped to Met;
> delta 2026-07-11 — NFR-4200 extended for ADR-0012's maze-generation WRAM cost — see
> Changelog).** Owned by
> `04-requirements-engineering`. Derives from
> [GDS-06](../architecture/06-non-functional-requirements.md)'s five NFRs (N1–N5) — formalized
> into numbered `NFR-xxxx` requirements per
> [GDS-10](../architecture/10-requirements-traceability-matrix.md) §3's citation contract. **This
> document preserves GDS-06's honest compliance status per requirement** — an NFR marked
> "Status: not met" below is a real, tracked gap (with its backlog ID), never silently presented
> as satisfied. Priority scale: Must / Should / Could, same as RQ-01.

## Changelog

- **2026-07-09 — Delta for the adopted aesthetics/visual-story-narrative/procgen-world-map
  increment** ([PLAN-requirements-aesthetics-story-map.md](../pipeline/PLAN-requirements-aesthetics-story-map.md),
  Phase 4; grounds `MSTR-001` v3.0's C8/C9/C10). **Six new NFRs added, all target requirements —
  none met yet** (no `Status: MET` claim is made for any of them; they describe the bar the
  increment's future packages must clear, not current compliance): **NFR-1300** (Performance —
  screen-transition smoothness for generated content), **NFR-2200** (Reliability — deterministic
  world generation, extending NFR-2100's determinism theme), **NFR-4200** (ROM/RAM budget —
  generated-world WRAM/SRAM headroom, extending `BL-0019`'s headroom-watching convention),
  **NFR-5300** (Data Integrity — save-format version bump for seed/scale/region-flags),
  **NFR-6500/6510** (Usability, previously empty — the C8 aesthetic-craft/clean-screen standard
  and the C9 biome-transition palette-stepping standard, both citing GDS-08's delta checklist).
- **2026-07-10 — 04-delta batch (`BL-0026`/`BL-0028`).** Two stale "pending independent
  verification" clauses corrected to reflect verifications that now exist: **NFR-1200**'s status
  line (VR-9020 exists) and its stale "111/111" suite-count snapshot (now 125/125, with the delta
  attributed to `IP-1010`'s later T11 suite); **NFR-5200**'s status line (VR-1010 exists) and its
  Notes field (no longer "re-verify once implemented" — it *is* implemented and verified).
  **NFR-6100**'s RTM Test cell filled (was `UNASSIGNED` despite direct evidence — the full T1–T10
  suite already exercises PyBoy headless on every run, surfaced by `09-package-verification`'s
  VR-9010, finding #1, run #23, `BL-0026`); `IP-9010`'s own citation of a nonexistent `NFR-7000`
  (should read `NFR-6100`) is a package-document correction routed to a future
  `07-implementation-planning` touch, not fixed here (out of this stage's write scope).
- **2026-07-11 — 04-delta (`BL-0045`).** **NFR-6500/6510** flipped from "not yet implemented" to
  **Met** — `09-content-review` exercised both against `IP-1031`'s content
  ([content-review-IP-1031.md](../reviews/content-review-IP-1031.md)), the first biome-family
  palette assignment either NFR had to judge. NFR-6500: clean, no findings. NFR-6510: Met with
  one Low/informational note (the Stone↔Brick pairing sits outside GDS-08 §8's worked example —
  does not fail the requirement, per its own "Should" priority). RTM rows for both updated.
- **2026-07-11 — 04-delta for `ADR-0012`'s maze-shaped region adjacency** (`BL-0064`–`BL-0067`;
  re-run Step 0 on the delta only, per this skill's own Gotchas). **NFR-4200**'s Notes field
  extended with `R112`'s directly-measured maze-generation WRAM cost (81 bytes worst case, or 11
  bit-packed, against 3168 bytes/3.09 KiB current free headroom) — WRAM budget does not gate
  `FR-9140`. No new NFR category needed; no Performance/Reliability NFR text changes required
  (the maze-generation pass stays within `generate_world`'s existing one-time, LCD-off-bracketed
  cost class already covered by `NFR-1300`/`NFR-2200`'s existing wording, which does not name a
  specific algorithm and needed no update).

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
- **Status: MET (2026-07-07, via `IP-9020`; independently confirmed by `09-package-verification`,
  [VR-9020](../implementation/verification/VR-9020-score-bar-vblank-fix.md)).** The
  `CALL('update_status_disp')` was relocated from `st_playing`
  (an unbounded distance into the frame) to the main loop's frame top, immediately after
  `VBLANK_FLAG` is cleared and before the `NEED_REDRAW`/`do_screen_redraw` dispatch —
  guaranteeing the write lands within the VBlank window (R102). The routine's existing internal
  `GAMESTATE`/`SCORE_DIRTY` guards make the unconditional call-site safe in every state. Accepted
  side effect: `SCORE_DIRTY` set during frame N is now drawn at the top of frame N+1 (previously
  same-frame) — no requirement states same-frame HUD latency. Evidence:
  [IP-9020](../implementation/packages/IP-9020-score-bar-vblank-fix.md); `test_rom.py` T8.10a/
  T8.10b force-dirty the HUD fields and confirm the digit tiles reflect the new values within 2
  frames; full suite **111/111 pass at IP-9020's own commit** (`test_results.txt`, regenerated
  2026-07-07) — **125/125 today**, the +14 delta entirely `IP-1010`'s later, independently
  verified T11 suite (2026-07-10 correction, `BL-0028`).
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

### NFR-1300 — Screen-transition smoothness for generated content (Met — 2026-07-10, `IP-1030`)

- **ID:** NFR-1300
- **Title:** A generated-region screen transition shall complete within the same LCD-off redraw
  budget existing transitions already use.
- **Description:** Entering a generated region (via FR-2300-equivalent traversal) shall render
  using the existing `do_screen_redraw`/`copy_screen` LCD-off mechanism (NFR-1100's sibling
  requirement), with no new, slower transition path introduced for generated content.
- **Rationale:** MSTR-001 C8/D4 ("smooth"); GDS-08 delta §7; GDS-07 delta; R102's extension.
- **Priority:** Must (Met)
- **Status: MET.** `dsr_p`'s biome-id dispatch (`IP-1030`) branches to one of 5 named patch pairs
  purely to select the source address, then calls the exact same, unmodified `copy_screen` routine
  inside the same LCD-off bracket every existing transition already used — confirmed by direct code
  read (T13.b) and the T13.a tile-family audit. The new `draw_region_arrows` runtime routine
  (retiring `_zone_arrows`' build-time math) also runs inside this same bracket, before LCD
  re-enable — no new safe-window convention introduced.
- **Acceptance Criteria:** A generated-region transition's tilemap/attribute write uses the same
  `copy_screen` routine and LCD-off bracket as every existing zone transition, with no additional
  per-frame cost beyond that routine's existing, already-budgeted 1152-byte copy.
- **Verification Method:** Inspection (call-site audit) / Test.
- **Source Documents:** GDS-08 delta §7; R102's extension.
- **Related ADRs:** ADR-0009.
- **Notes:** World *generation* itself (FR-9100) happens once, at new-game creation — not
  per-transition — so it is explicitly out of scope for this NFR's in-session smoothness bar
  (GDS-08 §7's own framing).

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

### NFR-2200 — Deterministic world generation (Met — 2026-07-10, `IP-1020`)

- **ID:** NFR-2200
- **Title:** World generation shall be deterministic in (seed, scale) alone — no dependence on
  `DIV`, uninitialized RAM, or any other timing-dependent input.
- **Description:** Extends NFR-2100's determinism theme specifically to the world-generation
  routine (FR-9100): the routine's output shall be a pure function of (seed, scale), with no
  read of the `DIV` register, uninitialized WRAM, or any other non-reproducible value anywhere
  in the generation algorithm.
- **Rationale:** MSTR-001 C10; strategic assumption A9; R111.
- **Priority:** Must
- **Status: MET.** `generate_world`/`gw_prng_step` (`asm_game.py`) read only `SEED`/
  `WORLD_SCALE`/`TMP1`/`TMP2`/`GW_*` scratch/`REGION_GRAPH` — no `LDH` (hardware register,
  including `DIV`) anywhere in either routine, confirmed by `test_rom.py`'s **T12.h** source
  scan. Determinism confirmed two ways: **T12.a** (byte-identical `REGION_GRAPH` across two
  independent fresh-boot invocations of the same `(seed, scale)`) and **T12.b** (byte-identical
  match against the `worldgen.py` reference oracle across a 15-entry seed/scale corpus).
- **Acceptance Criteria:** Static inspection of the generation routine finds no read of `DIV` or
  any WRAM address not explicitly initialized from (seed, scale) or the routine's own prior
  output; a determinism property test (FR-9100) confirms identical output across repeated runs.
- **Verification Method:** Inspection (static code audit) / Test (determinism property test).
- **Source Documents:** Strategic-assumptions-register A9; R111.
- **Related ADRs:** ADR-0009.
- **Notes:** This is what makes the Python reference-generator oracle (R305's extension) valid —
  an oracle can only predict SM83 output for a nondeterministic routine by accident, not by
  design. Not yet implemented.

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

### NFR-4200 — Generated-world WRAM/SRAM headroom (Met — WRAM half 2026-07-10 `IP-1020`; SRAM half
2026-07-10 `IP-1050`, re-affirmed 2026-07-11 `IP-9070`)

- **ID:** NFR-4200
- **Title:** The generated world's WRAM working set and SRAM save-field additions shall stay
  within confirmed available headroom at every supported world scale.
- **Description:** At the maximum supported world scale (9, 81 regions), the region-graph WRAM
  working set plus KeyItemFlags shall not exceed bank-0's confirmed unbanked headroom, and the
  SRAM save-field additions shall remain a small fraction of the 8 KiB SRAM budget.
- **Rationale:** GDS-07 delta §6/§7; R111; extends `BL-0019`'s ROM-headroom-watching convention
  to WRAM/SRAM specifically.
- **Priority:** Must
- **Status: MET, both halves.** WRAM half measured against shipped code, not estimated:
  `SEED`–`GW_SCALE_SQ` (`0xC069`–`0xC27C`, confirmed [GDS-07](../architecture/07-data-model.md)
  §6) stays entirely inside bank-0 and the existing boot-time WRAM clear (`0xC000`–`0xC2FF`);
  `test_rom.py`'s **T12.i** confirms this directly against the built ROM at `scale=9`. SRAM half
  implemented by `IP-1050` (`SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS` mirrors, ~84 bytes) and further
  grown by `IP-9070` (2026-07-11, `SRAM_SCOREITEM` widened 9→81 bytes, +72 bytes, relocated to
  `0xA070`–`0xA0C0`) — net SRAM save-format footprint against the 8 KiB MBC1 SRAM budget remains
  trivial; re-affirmed by direct build, not merely re-estimated.
- **Acceptance Criteria:** At world scale 9, the built ROM's WRAM working set for the region
  graph plus KeyItemFlags fits within bank-0 (`0xC000`–`0xCFFF`) without requiring `SVBK`
  banking; the SRAM save-field additions plus existing save data remain under 8 KiB.
- **Verification Method:** Inspection (WRAM/SRAM layout audit at implementation) / Test.
- **Source Documents:** GDS-07 delta §6/§7, §7a; R111.
- **Related ADRs:** ADR-0010.
- **Notes:** Re-affirm this NFR's status the same way `BL-0019`'s convention already requires for
  ROM-growing packages — any package materially growing the WRAM/SRAM footprint should include a
  checklist item re-checking headroom against this NFR's figures, as `IP-9070` did. **2026-07-11
  delta (`FR-9140`/`ADR-0012`):** the maze-generation pass's own worst-case WRAM cost was
  measured directly against the shipped tree, not estimated — `R112` found 928 bytes used /
  3168 bytes (3.09 KiB) free in bank 0 as of this delta, and the chosen algorithm (randomized
  DFS/recursive backtracker) needs only an 81-byte visited-flag array (or 11 bytes bit-packed) at
  `scale=9` worst case, comfortably inside that headroom — WRAM budget does not gate this feature.
  Re-affirm again by direct build once implemented, per this NFR's own standing convention.

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
  KeyItemCount, Score, KeyItemFlags[≤81], per-zone ScoreItem collected-state, Seed, WorldScale}
  as of the 2026-07-10 widening (FR-9200, `IP-1050`, second widening after FR-5220's) — a save
  followed by a load shall restore each field to exactly the value it held at save time.
- **Rationale:** GDS-06 N3; FR-5220, FR-9200 (widened field set).
- **Priority:** Must
- **Status: MET (2026-07-07 for the FR-5220 field set via `IP-1010`; widened 2026-07-10 for
  Seed/WorldScale/KeyItemFlags via `IP-1050`)** for the full widened field set. `test_rom.py`
  T11.b5/T11.c/T11.e1 (+ the existing T10 suite) round-trip `CurrentZone`/`PlayerPosition`/
  `Score`/`KEYITEM_FLAGS`(-formerly-`CARROT_FLAGS`)/`SCOREITEM_FLAGS`; T15.a3–a6/c1–c6 round-trip
  `SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS`/`KEYITEM_COUNT` together with the legacy fields under the
  new version-2 format in a single save/reload cycle; T11.d/T15.b confirm the version-guard
  default (a version-mismatched save loads no partial data at all, per ADR-0010 — stricter than
  the original FR-5220-era "safe empty state" default). Facing direction and animation frame
  remain explicitly excluded (FR-5210), not an open question.
- **Acceptance Criteria:** For each field in {CurrentZone, PlayerPosition, KeyItemCount, Score,
  KeyItemFlags[≤81], per-zone ScoreItem collected-state, Seed, WorldScale}, saving then loading
  yields an identical value.
- **Verification Method:** Test.
- **Source Documents:** GDS-06 N3; FR-5220, FR-9200.
- **Related ADRs:** ADR-0006, ADR-0010.
- **Notes:** FR-5220 is implemented and independently verified (2026-07-10 correction,
  `BL-0028`). FR-9200 implemented 2026-07-10 (`IP-1050`) — this NFR's "Met" status now covers
  both widenings.

### NFR-5300 — Save-format version bump for seed/scale/region-flags (Met — 2026-07-10, `IP-1050`)

- **ID:** NFR-5300
- **Title:** A pre-upgrade save (predating the seed/scale save-format extension) shall be
  reliably detected and never misread as containing valid seed/scale/region data.
- **Description:** The save-format version guard (extending the FS-101/`IP-1010` precedent at
  `0xA012`) shall be bumped to a new value when FR-9200's fields are added; a save whose version
  byte does not match is treated as pre-upgrade and is not offered on the MAIN MENU's "continue"
  path (per FR-1170/FR-9200), never partially loaded with garbage seed/scale/region-flags bytes.
- **Rationale:** ADR-0010; GDS-07 delta §7; R106's extension; the FS-101/`IP-1010` version-byte
  precedent this NFR extends.
- **Priority:** Must (Met)
- **Status: MET.** `SAVE_VERSION_VAL` bumped `0x01`→`0x02` (`IP-1050`), then `0x02`→`0x03`
  (`IP-9070`, 2026-07-11, `SRAM_SCOREITEM` relocation/widening); `check_save_valid` (`IP-1040`)
  and `try_load_save`'s own version check (both consuming the same symbolic constant) reject any
  save whose version byte doesn't match the current value from "continue" entirely — confirmed
  by `T15.b1`/`b2` (a synthetic IP-1010-vintage fixture) and `T16.d1`/`d2` (a synthetic
  IP-1050-vintage, version-2 fixture, extending the same pattern a third time). No partial load
  of garbage seed/scale/region-flags/scoreitem bytes occurs in any case.
- **Acceptance Criteria:** Given a save written under any prior version value, after boot that
  save is not offered as a "continue" option — verified by a synthetic pre-upgrade SRAM fixture,
  following the same test pattern `IP-1010`'s T11.d established for `SCOREITEM_FLAGS`.
- **Verification Method:** Test (synthetic pre-upgrade fixture, `IP-1010`'s T11.d precedent,
  extended by `IP-1050`'s T15.b and `IP-9070`'s T16.d).
- **Source Documents:** GDS-07 delta §7, §7a; ADR-0010.
- **Related ADRs:** ADR-0010, ADR-0006.
- **Notes:** Implemented 2026-07-10 (`IP-1050`), extended 2026-07-11 (`IP-9070`). The
  version-value sequence (`0x01`→`0x02`→`0x03`) is strictly monotonic by convention — a future
  save-format extension must bump to `0x04`, never reuse a prior value.

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

### NFR-6500 — Aesthetic craft and clean-screen standard compliance (target — 2026-07-09)

- **ID:** NFR-6500
- **Title:** All tile/sprite art and every rendered screen shall comply with GDS-08 delta §7's
  normative aesthetic standard.
- **Description:** Every tile/sprite (new or existing) shall satisfy R209's craft rules
  (silhouette-first design, per-part color budgeting, outlines on characters never terrain, no
  anti-aliased edges); every rendered screen (generated or hand-authored) shall satisfy the
  clean-screen rules (no undefined tile indices, no illegal tile-adjacency pairs, correct
  transition-edge neighbors).
- **Rationale:** MSTR-001 C8/D4 ("every screen/room/view clean"); GDS-08 delta §7; R209.
- **Priority:** Must
- **Status: Met (2026-07-11).** First exercised against `IP-1031`'s content by
  `09-content-review` — [content-review-IP-1031.md](../reviews/content-review-IP-1031.md): no
  undefined tile indices, no illegal tile-adjacency pairs, all four walked transition edges
  rendered a consistent, correctly-rendered neighbor. The craft checklist itself had no new
  tile/sprite art to check (IP-1031 reuses existing art verbatim) but was spot-checked
  opportunistically against the reused art with no defects found.
- **Acceptance Criteria:** Every checklist item in GDS-08 delta §7 passes for every screen a
  content package produces, confirmed by `09-content-review` per its existing review process
  (extended to apply this checklist, not a new review mechanism).
- **Verification Method:** Inspection (`09-content-review`'s existing visual-judgment process,
  applied against this checklist) / Test (the mechanically-checkable subset — undefined tiles,
  illegal seam pairs).
- **Source Documents:** GDS-08 delta §7; R209.
- **Related ADRs:** None.
- **Notes:** Not yet implemented as a formal gate. `09-content-review`'s scope already covers
  "does this screen read well" — this NFR gives that judgment a written standard to check
  against instead of an informal one.

### NFR-6510 — Biome-transition palette-stepping compliance (target — 2026-07-09)

- **ID:** NFR-6510
- **Title:** Adjacent grammar-legal biome families' palettes shall step coherently, not be
  assigned arbitrarily.
- **Description:** For any two biome families permitted to be adjacent by the grammar (FR-4310),
  their assigned BG palettes shall share a plausible color-family relationship (e.g. water-blues
  stepping toward beach-sands), per GDS-08 delta §8's strategy.
- **Rationale:** MSTR-001 C9; GDS-08 delta §8; R212.
- **Priority:** Should (a design-quality standard, not a hard functional gate — GDS-08 delta §8
  itself frames this as a content-authoring guideline within the existing 8-palette budget, not
  a new hardware constraint)
- **Status: Met, with one Low/informational note (2026-07-11).** First exercised against
  `IP-1031`'s 5 biome-family assignments by `09-content-review` —
  [content-review-IP-1031.md](../reviews/content-review-IP-1031.md): 3 of the 4 grammar-legal
  adjacent pairs walked (Water↔Sand, Sand↔Grass, Grass↔Stone) match GDS-08 delta §8's own worked
  example exactly; the fourth (Stone↔Brick) is the one pairing outside that example and reads as
  a larger hue jump — not arbitrary (a plausible mountain-to-castle reading), but flagged for a
  future GDS-08 §8 touch to consider extending the worked example. Consistent with this NFR's own
  "Should" priority — the finding does not fail the requirement.
- **Acceptance Criteria:** For every grammar-legal adjacent biome-family pair, a reviewer
  (`09-content-review`) confirms their assigned palettes read as color-family-related rather than
  arbitrary, per GDS-08 delta §8's worked example ordering.
- **Verification Method:** Inspection (`09-content-review`, a design-quality judgment call, not
  mechanically checkable).
- **Source Documents:** GDS-08 delta §8; R212.
- **Related ADRs:** ADR-0009.
- **Notes:** Confirms explicitly (per GDS-08 delta §8): the 8-BG-palette ceiling binds
  biome-family *count*, not blending, since FR-4300 rules out intra-screen mixing. Not yet
  implemented.

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
