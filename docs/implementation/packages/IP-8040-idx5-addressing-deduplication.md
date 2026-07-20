# IP-8040 — Index*5 Addressing Arithmetic Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8040` — refactors `asm_game.py`, filed from **`BL-0173`** (`refactor`, `SCHEDULED`).

## 2. Objective

Five sites inline the identical "multiply index by 5 via five unrolled `ADD_HL_DE` steps"
sequence (`base + index*5`, this project's own no-multiply-instruction convention): `czt_region_hl`,
`dsr_p`, `setup_zone_collects` (all three: `REGION_GRAPH` + `CUR_ZONE`), `gw_neighbor_hl`
(`REGION_GRAPH` + a caller-supplied index — its own comment already names this as "generalizing"
`czt_region_hl`'s addressing), and `ilmc_evict` inside `inf_ledger_mark_collected` (`LEDGER` +
`LEDGER_CURSOR`). Extract the shared five-`ADD_HL_DE` core into `idx5_to_hl`.

**Scope corrected during execution (found by the suite itself, not planning):** `dsr_p` is
**excluded**. `T24.c1` is a static source-code characterization test that asserts `dsr_p`'s own
finite-mode body is, call-for-call, byte-identical to a specific pre-`IP-1102` instruction
sequence (with only a 3-instruction gate prefixed) — it fails on *any* instruction-shape change
to that routine, deliberately, regardless of behavioral equivalence. Rewriting `dsr_p` to call
`idx5_to_hl` is behavior-preserving but not instruction-shape-preserving, so it trips this test by
design. Reverted that one site; the other four (`czt_region_hl`, `setup_zone_collects`,
`gw_neighbor_hl`, `ilmc_evict`) proceed as planned. Filed as an Outstanding Issue, not fixed here
(fixing `T24.c1` itself is a test-file change this package's own rules forbid).

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

`ADR-0003` (unaffected); `R307`.

## 5. Interfaces

- **`czt_region_hl`** (existing) — body becomes `LD_A_nn(CUR_ZONE); LD_E_A(); LD_D_n(0);
  LD_HL_nn(REGION_GRAPH); CALL('idx5_to_hl'); RET()`. Its own four external callers in
  `check_zone_transition` are unaffected — same label, same calling convention (HL out).
- **`dsr_p`** — **excluded, left unmodified.** See the scope-correction note in §2; `T24.c1` pins
  its own exact instruction sequence.
- **`setup_zone_collects`** (existing) — identical replacement to `czt_region_hl`'s own.
- **`gw_neighbor_hl`** (existing) — its own inlined block (no `CUR_ZONE` read; `A` already holds
  the caller-supplied region index) replaced by `LD_E_A(); LD_D_n(0); LD_HL_nn(REGION_GRAPH);
  CALL('idx5_to_hl')`, preserving `C` (direction) exactly as its own existing contract requires.
- **`ilmc_evict`** (inside `inf_ledger_mark_collected`, existing) — identical replacement with
  `LD_HL_nn(LEDGER)` in place of `LD_HL_nn(REGION_GRAPH)`.
- **New subroutine `idx5_to_hl`** — **Contract:** Input `E` = index, `D` = 0 (caller sets both),
  `HL` = pre-loaded base address. Computes `HL = HL + E*5` via the identical five `ADD_HL_DE`
  steps every site already used. **Clobbers:** nothing beyond `HL` itself (the five `ADD_HL_DE`
  instructions don't touch `A`/`B`/`C`/`D`/`E`). **Preserves:** `A`, `B`, `C`, `D`, `E` — every
  caller either doesn't need them after, or (in `gw_neighbor_hl`'s case) explicitly requires `C`
  untouched, which this subroutine already satisfies by construction.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New subroutine `idx5_to_hl`**, placed near `czt_region_hl` (its first caller in file
    order).
  - **`czt_region_hl`**, **`setup_zone_collects`**, **`gw_neighbor_hl`**, **`ilmc_evict`**: each
    replace their own inlined five-`ADD_HL_DE` block with `CALL('idx5_to_hl')`, per §5 above. No
    other line in any of these four routines changes.
  - **`dsr_p`**: **unmodified** — excluded per the §2 scope correction.

## 7. Implementation Tasks

Ordered: (1) author `idx5_to_hl`; (2)-(6) rewrite each of the five originally-planned call sites
in turn, rebuilding and running the full suite after each to catch any site-specific mistake
early rather than compounding edits before the first check — this incremental discipline is what
caught `dsr_p`'s own `T24.c1` conflict at exactly the point it was introduced, isolating it
immediately rather than after all five edits had landed; (7) revert the `dsr_p` edit per the
finding, re-run the full suite to confirm green; (8) final byte-delta recording; (9) direct-diff
the four modified routines' own surrounding code against the pre-refactor tree, and confirm
`dsr_p` has zero diff lines; (10) documentation updates (§9, none expected).

## 8. Tests to Add

**None.** `T9`/`T17` (zone transitions, exercises `czt_region_hl`), `T1.11`/`T11` (per-zone
collectible setup, exercises `setup_zone_collects`), the maze-generation suites (exercise
`gw_neighbor_hl`), and `T27`/`T27.g` (ledger, exercises `ilmc_evict`'s own eviction path) already
cover all four call sites' observable behavior. Full suite passing unmodified is the acceptance
bar.

## 9. Documentation Updates

None expected — no requirement, WRAM/SRAM layout, or interface change; `GDS-07`'s own
`REGION_GRAPH`/`LEDGER` byte-layout descriptions are unaffected (this package changes how the
offset is computed, not what it computes to).

## 10. Definition of Done

- `idx5_to_hl` exists, called from the four in-scope sites (`czt_region_hl`,
  `setup_zone_collects`, `gw_neighbor_hl`, `ilmc_evict`); none of the four retains its own
  inlined five-`ADD_HL_DE` block. `dsr_p` is confirmed unmodified.
- ROM builds at exactly 32768 bytes; full suite passes, unmodified, at its current count.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes.
- [ ] G5: full suite passes, zero `test_rom.py` diff.
- [ ] Equivalence contract: diff touches only the new subroutine + the four replaced blocks;
      `dsr_p` has zero diff lines.
- [ ] Direct code read: `gw_neighbor_hl`'s own `C` (direction) confirmed still correct on return
      from `idx5_to_hl` — not clobbered.
- [ ] `T9`/`T17`/`T1.11`/`T11`/maze-generation suites/`T27.g`/`T24.c1` all still pass.

## 12. Dependencies

None.

## 13. Risks

- **Five call sites originally in scope, one excluded** (Low, realized during execution, not
  planning): `dsr_p`'s own inclusion was reverted when `T24.c1` — a static characterization test
  pinning its exact instruction sequence — failed. Not a defect in this package's own design; a
  genuine, deliberate test constraint this planning pass didn't have visibility into (a
  source-level `grep` for the routine's own call sequence, not its behavior). **Outstanding
  Issue, filed to intake, not fixed here**: any *future* refactor touching `dsr_p`'s own
  finite-mode body will hit the identical constraint — worth a dedicated look at whether `T24.c1`
  should be relaxed to a behavioral check (once a real need to change `dsr_p`'s shape arises),
  which is a test-file change outside this refactoring package's own scope.
- **ROM budget** (Low, favorable): expected modest net decrease from four sites instead of five.

## 14. Rollback Considerations

Revert `asm_game.py`'s five touched regions (the new subroutine + four call sites) and rebuild.
