# IP-8070 — `gw_neighbor_hl` Read-Wrapper Deduplication

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — behavior-preserving only. No bug fix, no feature change.**

## 1. Package ID

`IP-8070` — refactors `asm_game.py`, filed from **`BL-0178`** (`refactor`, `SCHEDULED`).

## 2. Objective

The "read the neighbor region index in direction `GW_MAZE_DIR` from a region, via
`gw_neighbor_hl`, then dereference" idiom is inlined identically at `ki_passA_dir` and
`maze_prune_dir` (both region source = `GW_BRAID_IDX`), and near-identically at one further site
(region source = `GW_CUR_REGION`). Extract into `gw_read_neighbor`.

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

Unaffected; `R307`.

## 5. Interfaces

- **New subroutine `gw_read_neighbor`** — **Contract:** Input `A` = region index (caller-loaded).
  Reads `GW_MAZE_DIR` internally for direction. Computes `HL -> REGION_GRAPH[A].neighbor[dir]`
  via `gw_neighbor_hl` and returns `A` = `(HL)` (the neighbor region index, or `0xFF` if none).
  **Clobbers:** `A`, `B`, `C`, `D`, `E`, `H`, `L`. **Preserves:** nothing beyond what's needed —
  confirmed by direct read that neither call site needs `B`/`C`/`D`/`E` alive after the call
  (each immediately branches on the returned `A` via `CP_n(0xFF)`).
- **Call sites, as actually implemented** — **`maze_try_loop`** (region = `GW_CUR_REGION`) and
  **`maze_prune_dir`** (region = `GW_BRAID_IDX`) both rewritten to
  `LD_A_nn(<region>); CALL('gw_read_neighbor')`. **`ki_passA_dir` excluded** (scope corrected
  during execution, see §13/Rollback below): it clobbers `B` as a live `has_child` accumulator
  across its own direction loop (set before the loop at `ki_passA_region`, read after the loop
  ends) — a register-liveness conflict not visible from the block's own immediate context, only
  from the enclosing loop; `gw_read_neighbor`'s use of `B` as scratch broke this, caught
  immediately by `T12.e` (KeyItem placement oracle-parity test). Reverted that one site back to
  its original inlined form; kept the other two, which have no such conflict (confirmed by direct
  read of `maze_prune_dir`'s own enclosing scope: its only `B` usage, the "durable stash" at the
  braid-decision branch ~10 lines further down, is assigned fresh *after* the site's own call and
  never carries a value in from a prior iteration).

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**: new subroutine `gw_read_neighbor` (placed near `gw_neighbor_hl`, its
  own callee); two-to-three call-site rewrites per §5.

## 7. Implementation Tasks

Ordered: (1) author `gw_read_neighbor` (uses `B` as scratch to hold the region index across the
`LD_A_nn(GW_MAZE_DIR); LD_C_A()` step, confirmed free at all candidate sites by direct read);
(2)-(4) rewrite each call site in turn, rebuilding and running the full suite after each; (5)
final byte-delta recording; (6) direct-diff all touched sites' own surrounding code against the
pre-refactor tree; (7) documentation updates (§9, none expected).

## 8. Tests to Add

**None.** The maze-generation suites already exercise both `ki_passA_dir` and `maze_prune_dir`.
Full suite passing unmodified is the acceptance bar.

## 9. Documentation Updates

None expected.

## 10. Definition of Done

- `gw_read_neighbor` exists, called from `maze_try_loop` and `maze_prune_dir`; `ki_passA_dir`
  correctly excluded and confirmed zero diff lines.
- ROM builds at exactly 32768 bytes; full suite passes, unmodified, at its current count.
- Byte delta measured and recorded.

## 11. Verification Checklist

- [x] G5: ROM builds at exactly 32768 bytes.
- [x] G5: full suite passes, zero `test_rom.py` diff.
- [x] Equivalence contract: diff touches only the new subroutine + the two replaced blocks
      (`ki_passA_dir` zero diff lines).
- [x] Maze-generation suites still pass (incl. `T12.e`, which caught the `ki_passA_dir` conflict).

## 12. Dependencies

None.

## 13. Risks

- **Third candidate site's differing region source** (Low): if `GW_CUR_REGION` substitution at
  ~line 2946 doesn't fit cleanly (e.g. a register-liveness conflict not visible until direct
  edit), leave that site inlined and proceed with the two confirmed sites only — same
  try-then-revert-if-needed discipline as `IP-8040`'s own `dsr_p` scope correction.
- **ROM budget** (Low): expected small net change either direction.

## 14. Rollback Considerations

Revert `asm_game.py`'s touched regions and rebuild.
