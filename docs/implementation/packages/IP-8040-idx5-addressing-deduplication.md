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

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

`ADR-0003` (unaffected); `R307`.

## 5. Interfaces

- **`czt_region_hl`** (existing) — body becomes `LD_A_nn(CUR_ZONE); LD_E_A(); LD_D_n(0);
  LD_HL_nn(REGION_GRAPH); CALL('idx5_to_hl'); RET()`. Its own four external callers in
  `check_zone_transition` are unaffected — same label, same calling convention (HL out).
- **`dsr_p`** (existing) — its own finite-mode prologue's inlined 5×`ADD_HL_DE` block replaced by
  `CALL('idx5_to_hl')` (E/D/HL already set up by the immediately-preceding, unchanged
  `LD_A_nn(CUR_ZONE); LD_E_A(); LD_D_n(0); LD_HL_nn(REGION_GRAPH)`).
- **`setup_zone_collects`** (existing) — identical replacement.
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
  - **`czt_region_hl`**, **`dsr_p`**, **`setup_zone_collects`**, **`gw_neighbor_hl`**,
    **`ilmc_evict`**: each replace their own inlined five-`ADD_HL_DE` block with
    `CALL('idx5_to_hl')`, per §5 above. No other line in any of these five routines changes.

## 7. Implementation Tasks

Ordered: (1) author `idx5_to_hl`; (2)-(6) rewrite each of the five call sites in turn, rebuilding
and running the full suite after each to catch any site-specific mistake early rather than
compounding five edits before the first check; (7) final full-suite run + byte-delta recording;
(8) direct-diff all five routines' own surrounding code against the pre-refactor tree; (9)
documentation updates (§9, none expected).

## 8. Tests to Add

**None.** `T9`/`T17` (zone transitions), `T13` (screen rendering, exercises `dsr_p`), `T1.11`/
`T11` (per-zone collectible setup, exercises `setup_zone_collects`), the maze-generation suites
(exercise `gw_neighbor_hl`), and `T27`/`T27.g` (ledger, exercises `ilmc_evict`'s own eviction
path) already cover all five call sites' observable behavior. Full suite passing unmodified is
the acceptance bar.

## 9. Documentation Updates

None expected — no requirement, WRAM/SRAM layout, or interface change; `GDS-07`'s own
`REGION_GRAPH`/`LEDGER` byte-layout descriptions are unaffected (this package changes how the
offset is computed, not what it computes to).

## 10. Definition of Done

- `idx5_to_hl` exists, called from all five sites; none of the five retains its own inlined
  five-`ADD_HL_DE` block.
- ROM builds at exactly 32768 bytes; full suite passes, unmodified, at its current count.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes.
- [ ] G5: full suite passes, zero `test_rom.py` diff.
- [ ] Equivalence contract: diff touches only the new subroutine + the five replaced blocks.
- [ ] Direct code read: `gw_neighbor_hl`'s own `C` (direction) confirmed still correct on return
      from `idx5_to_hl` — not clobbered.
- [ ] `T9`/`T17`/`T13`/`T1.11`/`T11`/maze-generation suites/`T27.g` all still pass.

## 12. Dependencies

None.

## 13. Risks

- **Five call sites in one package** (Low): larger surface than `IP-8010`/`8020`/`8030`, mitigated
  by the incremental build-and-test-after-each-site discipline in §7 rather than batching all
  five edits before the first verification.
- **ROM budget** (Low, favorable): expected modest net decrease.

## 14. Rollback Considerations

Revert `asm_game.py`'s six touched regions (the new subroutine + five call sites) and rebuild.
