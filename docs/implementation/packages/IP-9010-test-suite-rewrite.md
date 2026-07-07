# IP-9010 — Test Suite Rewrite (Bunny Quest semantics + portable paths)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9010` — bug-remediation series; no FS. Sources: **`BL-0006`** (Critical) + **`BL-0005`**
(Medium), under the **`BL-0008`** umbrella. Riders: **`BL-0017`** (carrot-invariant check).

## 2. Objective

Make `test_rom.py` a trustworthy verification gate for the shipped game: every assertion tests
**Bunny Quest** (9 zones, 9-carrot victory, `CARROT_FLAGS` array) instead of the pre-rewrite
"Bunny Garden" semantics, and every path is repo-relative so the suite runs in any checkout.
This restores the G5 permanent gate the whole Master Build Plan depends on.

## 3. Requirements Covered

- **`NFR-7100`** (test-suite currency — currently NOT MET; this package is its remediation).
- **`NFR-7000`** (suite runs headless via PyBoy — preserved).
- Indirectly re-enables Test-method verification for the FR baseline (RQ-03 finding: most FRs'
  "Verification Method: Test" cells are unsatisfiable until this lands).

## 4. Architecture Components

GDS-02 §verification harness · GDS-07 (WRAM map — the authoritative address/value source) ·
ADR-0008 (PyBoy headless as verification target) · R304/R305/R306 (grounding research).

## 5. Interfaces

No GDS-09 cross-module contract is touched. The package consumes the ROM artifact
(`BunnyQuest.gbc`) and PyBoy's public API (R301); it modifies no production module.

## 6. Files to Create/Modify

- **Modify: `test_rom.py`** (sole production-tree file; suite-level rewrite per R305, not a
  line-by-line patch). Verified current state: `ROM_PATH`/`RAM_PATH` hardcoded at lines 21–22
  (`/mnt/user-data/outputs/BunnyGarden.gbc[.ram]` — wrong root *and* stale filename),
  `SHOT_DIR` at line 23 (`/home/claude/bunnygarden/test_shots`), results write at line 492
  (`/home/claude/bunnygarden/test_results.txt`); stale assertions throughout T2/T4/T5/T7/T8/T9
  (e.g. T4.8 sets `0xC009=0x07` expecting victory; T5 asserts pre-rewrite tile indices; T9
  assumes zone 2 is last).
- **Delete or regenerate: `test_results.txt`** (repo root) — the checked-in "88/88 passed"
  artifact predates the rewrite; replace with the new suite's real output.

## 7. Implementation Tasks

1. Replace the four absolute paths with a single repo-relative base
   (`BASE = pathlib.Path(__file__).resolve().parent`, per R306): `ROM_PATH = BASE /
   'BunnyQuest.gbc'`, `RAM_PATH` **derived** from `ROM_PATH` (append `.ram`), `SHOT_DIR = BASE
   / 'test_shots'`, results file `BASE / 'test_results.txt'`.
2. Keep T1 (header) unchanged — R304 confirms it is correct as-is.
3. Rewrite T2–T10 against the current WRAM model per R305's address/value table (GDS-07
   authoritative): `CUR_ZONE` `0xC008` ranges 0–8; victory = all nine `CARROT_FLAGS`
   (`0xC015`–`0xC01D`) set **and** `CARROTS_COUNT` (`0xC009`) = 9; tile-index assertions from
   GDS-07 §4 (e.g. blank `0x10`-range UI block, terrain blocks at `0x70`+); zone-transition
   tests exercise the 3×3 grid edges, not a 3-zone strip; save/load tests round-trip the full
   current field set (`A000`–`A011`) including all 9 `CARROT_FLAGS`.
4. Add a map-hearts check (closes `BL-0001`'s re-verification permanently): with
   `CARROT_FLAGS[i]` forced, enter MAP state and assert the heart tile at
   `0x9800 + {6,9,12}*32 + {6,11,16}` matches full/empty per flag.
5. Add the `BL-0017` rider check: parse `tilemaps.py`'s `ZONE_COLLECTS` (host-side import, no
   emulator) and assert exactly one type-2 (carrot) entry per zone list, 9 lists total.
6. Update the file's docstring header (suite list, run instructions, ROM name).

## 8. Tests to Add

This package *is* the test work: rewritten T2–T10 + the new checks above, all landing in
`test_rom.py` itself. Suite numbering stays T1–T10 (T11 is reserved for IP-1010).

## 9. Documentation Updates

- `docs/requirements/02-non-functional-requirements.md`: flip `NFR-7100`'s compliance status to
  Met (dated changelog line), citing this package.
- `docs/requirements/04-requirements-traceability-matrix.md`: update the Test column for rows
  whose suite references change (mechanical delta only, as specified here).
- Master Build Plan status row (per stage-08 convention).

## 10. Definition of Done

- `python3 test_rom.py` runs from a fresh checkout of the repo root with only PyBoy + numpy
  installed, finds `BunnyQuest.gbc`, and **passes 100%** against a freshly built ROM.
- No absolute path remains anywhere in `test_rom.py`.
- No assertion references pre-rewrite semantics (gifts bitfield, 3-zone bounds, stale tiles).
- The ROM artifact is **byte-identical** before/after this package (test-harness-only change).
- Checked-in `test_results.txt` reflects the new suite's real output.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header (`python3 build_rom.py` +
      T1 pass).
- [ ] G5: full `test_rom.py` suite passes, run headless from the repo root.
- [ ] Rebuilt ROM is byte-identical to pre-package `BunnyQuest.gbc` (this package must not
      change the game).
- [ ] Grep confirms no `/mnt/`, `/home/claude`, or `BunnyGarden` strings remain in
      `test_rom.py`.
- [ ] T4/T8 victory checks set both `CARROT_FLAGS` and `CARROTS_COUNT` (R305's dual-assertion
      rule).
- [ ] One-carrot-per-zone check present and passing (BL-0017).
- [ ] Map-hearts check present and passing (BL-0001 closure evidence).
- [ ] NFR-7100 status flip and RQ-04 Test-column deltas applied exactly as §9 names.

## 12. Dependencies

**None** — this is the plan's root package. (Its own G5 gate is satisfied by its own
deliverable.) Everything else depends on it.

## 13. Risks

- **PyBoy availability** (`BL-0011`): PyBoy is not installed in every session; the implementing
  session must install it (or the package blocks with an environment note). R301's minor
  uncited claims get incidentally re-verified when the suite runs.
- **Behavioral discoveries**: rewriting assertions against real behavior may surface *new* game
  bugs (the suite hasn't truly tested the rewrite ever). Such findings route to the backlog —
  they are not this package's scope to fix.
- ROM budget: none (no production-code change).

## 14. Rollback Considerations

Single-file revert of `test_rom.py` (+ `test_results.txt`) restores the prior state; no ROM,
save-format, or cross-module impact. Nothing downstream can regress — downstream packages are
blocked until this lands, by design.
