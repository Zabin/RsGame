# IP-8060 — Seed-Cursor-Arrow Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8060` — refactors `asm_game.py`, filed from **`BL-0177`** (`refactor`, `SCHEDULED`).

## 2. Objective

`draw_sse_digits` and `draw_ise_digits` both end with an identical 5-instruction tail that
computes the seed-cursor cell from `SSE_CURSOR` and draws the arrow tile there. Extract into
`dsd_seed_cursor_arrow`.

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

Unaffected; `R307`.

## 5. Interfaces

- **New subroutine `dsd_seed_cursor_arrow`** — **Contract:** Input `A` = cursor index (already
  loaded by the caller from `SSE_CURSOR`). Computes the seed-digit cell address
  (`0x9800 + SSE_CURSOR_SEED_ROW*32 + SSE_SEED_COL0 + A`) and writes `TL_ARROW_D` there.
  **Clobbers:** `A`, `D`, `E`, `H`, `L`. **Preserves:** nothing beyond what's needed — both call
  sites `RET` immediately after (`draw_sse_digits`'s own call site is itself the routine's own
  final instruction before `RET`; `draw_ise_digits`'s call site is its own last instruction before
  `RET`), confirmed by direct read that neither needs any register alive afterward.
- **Two call sites** (line numbers approximate, pre-refactor tree): ~2413-2416 (`draw_sse_digits`'s
  own seed-cursor-arrow tail, reached when `SSE_CURSOR` != 5), ~2444-2447 (`draw_ise_digits`'s own
  tail) — each replaces its own `LD_E_A(); LD_D_n(0); LD_HL_nn(...); ADD_HL_DE(); LD_A_n(TL_ARROW_D); LD_HL_A()`
  block with `CALL('dsd_seed_cursor_arrow')`, immediately after its own existing
  `LD_A_nn(SSE_CURSOR)` load. No other line at either site changes.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**: new subroutine `dsd_seed_cursor_arrow` (placed near `draw_sse_digits`,
  its first caller in file order); two call-site rewrites per §5.

## 7. Implementation Tasks

Ordered: (1) author `dsd_seed_cursor_arrow`; (2)-(3) rewrite each of the two call sites in turn,
rebuilding and running the full suite after each; (4) final byte-delta recording; (5) direct-diff
both sites' own surrounding code against the pre-refactor tree; (6) documentation updates (§9,
none expected).

## 8. Tests to Add

**None.** The seed-scale-entry and infinite-seed-entry screen tests already cover both call
sites' observable behavior (cursor-arrow placement). Full suite passing unmodified is the
acceptance bar.

## 9. Documentation Updates

None expected.

## 10. Definition of Done

- `dsd_seed_cursor_arrow` exists, called from both sites; neither retains its own inlined block.
- ROM builds at exactly 32768 bytes; full suite passes, unmodified, at its current count.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes.
- [ ] G5: full suite passes, zero `test_rom.py` diff.
- [ ] Equivalence contract: diff touches only the new subroutine + the two replaced blocks.
- [ ] Seed-scale-entry and infinite-seed-entry cursor-arrow tests still pass.

## 12. Dependencies

None.

## 13. Risks

- **Two call sites, small size** (Low): same incremental build-and-test discipline as prior
  `IP-8xx0` packages.
- **ROM budget** (Low, favorable): expected small net decrease.

## 14. Rollback Considerations

Revert `asm_game.py`'s touched regions and rebuild.
