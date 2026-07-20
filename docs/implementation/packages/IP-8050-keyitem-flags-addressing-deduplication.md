# IP-8050 — KEYITEM_FLAGS Addressing Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8050` — refactors `asm_game.py`, filed from **`BL-0175`** (`refactor`, `SCHEDULED`).

## 2. Objective

Six sites inline the identical "index-to-`KEYITEM_FLAGS`-address" computation
(`LD_E_A(); LD_D_n(0); LD_HL_nn(KEYITEM_FLAGS); ADD_HL_DE()`), each preceded by loading the
region index (`CUR_ZONE` or `GW_BRAID_IDX`) into `A`. Extract into `keyitem_flags_hl`.

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

`ADR-0003` (unaffected); `R307`.

## 5. Interfaces

- **New subroutine `keyitem_flags_hl`** — **Contract:** Input `A` = region index (already
  loaded by the caller from `CUR_ZONE` or `GW_BRAID_IDX`, whichever applies at that site).
  Computes `HL = KEYITEM_FLAGS + A`. **Clobbers:** `A`, `D`, `E`, `H`, `L`. **Preserves:**
  nothing beyond what's needed — confirmed by direct read that none of the six call sites
  requires `D`/`E`/old-`A` after the call (each immediately writes a fresh value to `(HL)` or
  reads `(HL)` into a fresh `A`).
- **Six call sites** (line numbers approximate, pre-refactor tree): ~1243 (carve-pass KeyItem
  placement), ~2582 (`setup_zone_collects`'s own KeyItem-collected check), ~3051/~3058/~3065
  (the `ki_passA_*` leaf/absent-marking branches), ~3100 (fallback-fill placement) — each
  replaces its own `LD_E_A(); LD_D_n(0); LD_HL_nn(KEYITEM_FLAGS); ADD_HL_DE()` block with
  `CALL('keyitem_flags_hl')`, immediately after its own existing index-load into `A`. No other
  line at any of the six sites changes.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**: new subroutine `keyitem_flags_hl` (placed near its first caller in
  file order, ~line 1243's own routine); six call-site rewrites per §5.

## 7. Implementation Tasks

Ordered: (1) author `keyitem_flags_hl`; (2)-(7) rewrite each of the six call sites in turn,
rebuilding and running the full suite after each (per `IP-8040`'s own established discipline,
which caught a real constraint early); (8) final byte-delta recording; (9) direct-diff all six
sites' own surrounding code against the pre-refactor tree; (10) documentation updates (§9, none
expected).

## 8. Tests to Add

**None.** `T1.11`/`T11` (per-zone KeyItem persistence), the maze-generation suites (exercise the
`ki_passA_*` branches), and the existing carve-pass tests already cover all six call sites'
observable behavior. Full suite passing unmodified is the acceptance bar.

## 9. Documentation Updates

None expected.

## 10. Definition of Done

- `keyitem_flags_hl` exists, called from all six sites; none retains its own inlined block.
- ROM builds at exactly 32768 bytes; full suite passes, unmodified, at its current count.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes.
- [ ] G5: full suite passes, zero `test_rom.py` diff.
- [ ] Equivalence contract: diff touches only the new subroutine + the six replaced blocks.
- [ ] Maze-generation suites and `T1.11`/`T11` all still pass.

## 12. Dependencies

None.

## 13. Risks

- **Six call sites in one package** (Low): mitigated by the incremental build-and-test-after-
  each-site discipline, same as `IP-8040`.
- **Possible characterization-test constraint** (Low, learned from `IP-8040`'s own `BL-0174`
  finding): if any site hits a similar static instruction-sequence assertion, revert that one
  site specifically and proceed with the rest, per this session's own established practice.
- **ROM budget** (Low, favorable): expected net decrease (~16 bytes estimated).

## 14. Rollback Considerations

Revert `asm_game.py`'s touched regions and rebuild.
