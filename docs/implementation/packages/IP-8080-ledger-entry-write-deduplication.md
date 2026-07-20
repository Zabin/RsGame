# IP-8080 — Ledger-Entry Write-Block Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8080` — refactors `asm_game.py`, filed from **`BL-0179`** (`refactor`, `SCHEDULED`).

## 2. Objective

`inf_ledger_mark_collected`'s own `ilmc_notfound` (append) and `ilmc_evict` (FIFO-overwrite)
paths both write the identical 5-byte ledger record (`INF_ROW`/`INF_ROW+1`/`INF_COL`/`INF_COL+1`/
`1`) at a pre-positioned `HL`. Extract into `write_ledger_entry_at_hl`.

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

Unaffected; `R307`.

## 5. Interfaces

- **New subroutine `write_ledger_entry_at_hl`** — **Contract:** Input `HL` = pre-positioned
  ledger slot address (already computed by the caller). Writes `INF_ROW`, `INF_ROW+1`,
  `INF_COL`, `INF_COL+1` via four `LD_A_nn(...); LD_HLI_A()` pairs, then writes `1` (collected)
  via a final `LD_A_n(1); LD_HL_A()` (non-incrementing — `HL` ends pointing at the collected
  byte). **Clobbers:** `A`, `H`, `L`. **Preserves:** nothing beyond what's needed — confirmed by
  direct read that neither call site needs `HL`/`A` alive after the block (both immediately move
  on to unrelated bookkeeping: `ilmc_notfound` increments `LEDGER_COUNT`, `ilmc_evict` advances
  `LEDGER_CURSOR`).
- **Two call sites** (line numbers approximate, pre-refactor tree): ~4168-4172
  (`ilmc_notfound`'s own append path), ~4182-4186 (`ilmc_evict`'s own FIFO-overwrite path) — each
  replaces its own 5-instruction-pair write block with `CALL('write_ledger_entry_at_hl')`,
  immediately after its own existing `HL` positioning. No other line at either site changes.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**: new subroutine `write_ledger_entry_at_hl` (placed near
  `inf_ledger_mark_collected`); two call-site rewrites per §5.

## 7. Implementation Tasks

Ordered: (1) author `write_ledger_entry_at_hl`; (2)-(3) rewrite each of the two call sites in
turn, rebuilding and running the full suite after each; (4) final byte-delta recording; (5)
direct-diff both sites' own surrounding code against the pre-refactor tree; (6) documentation
updates (§9, none expected).

## 8. Tests to Add

**None.** The Infinite Mode ledger-persistence suite already exercises both the append and
FIFO-eviction paths. Full suite passing unmodified is the acceptance bar.

## 9. Documentation Updates

None expected.

## 10. Definition of Done

- `write_ledger_entry_at_hl` exists, called from both sites; neither retains its own inlined
  block.
- ROM builds at exactly 32768 bytes; full suite passes, unmodified, at its current count.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes.
- [ ] G5: full suite passes, zero `test_rom.py` diff.
- [ ] Equivalence contract: diff touches only the new subroutine + the two replaced blocks.
- [ ] Ledger append and FIFO-eviction tests still pass.

## 12. Dependencies

None.

## 13. Risks

- **Two call sites, small size** (Low): same incremental build-and-test discipline as prior
  `IP-8xx0` packages.
- **ROM budget** (Low, favorable): expected small net decrease.

## 14. Rollback Considerations

Revert `asm_game.py`'s touched regions and rebuild.
