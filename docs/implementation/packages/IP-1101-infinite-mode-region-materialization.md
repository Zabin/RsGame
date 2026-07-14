# IP-1101 — Infinite Mode: Per-Region Materialization

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1101` — implements part of [**FS-110**](../../features/FS-110-infinite-mode.md) (`FEAT-10000`,
Epic `EP-6000`, `Future` bucket). Covers Workflow B step 2 and Workflow C step 1 (the `generate`
verb only — rendering and window management are `IP-1102`'s scope). This tranche's foundational
package — mirrors `IP-1020`'s own root-of-tranche role for the finite mode. See the
[Technical Work Breakdown](../01-technical-work-breakdown.md)'s "Infinite Mode" section for the
full split rationale.

## 2. Objective

Implement the pure-function per-region materialization routine: given `(SEED, row, col)`, produce
a biome-id, a 4-direction connectivity nibble, and a treasure-presence bit — deterministically,
byte-identically on repeat calls, with a lockstep `worldgen.py` oracle mirror.

## 3. Requirements Covered

FR-10200, FR-10210 (revisit-consistency), FR-10300 (treasure-presence predicate); NFR-2300
(positional determinism, Inspection + Test).

## 4. Architecture Components

[ADR-0016](../../architecture/adr/ADR-0016-streaming-infinite-mode-generation-architecture.md)
points 3 (per-region reseed construction), 5 (Binary Tree maze, zero-memory), 8 (oracle lockstep
discipline) · [ADR-0017](../../architecture/adr/ADR-0017-infinite-mode-treasure-placement-and-win-condition.md)
(treasure decoupled from maze structure via hash-density predicate) · this package's own
Technical Work Breakdown findings: the rendering-integration investigation (confirms this
package's output shape — a biome-id byte, a connectivity nibble — is exactly what `IP-1102`'s
`dsr_p` reuse and new `draw_region_arrows_inf` need, nothing more) and the Binary Tree
neighbor-consulting construction (this package's own §6 task list operationalizes it).

## 5. Interfaces

- **`gw_prng_step`'s existing shift/XOR-only xorshift construction** (`R111`/`R113`, unchanged) —
  reused for per-region reseeding. This package does not modify `gw_prng_step` itself or any of
  its existing finite-mode call sites (`generate_world`'s own biome/maze passes).
- **`worldgen.py`'s existing oracle-mirror discipline** (`FEAT-9000`'s own precedent) — extended
  with a new per-region function, not a new file.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **New subroutine `inf_materialize_region`** — inputs: `row`/`col` (signed 16-bit each, e.g.
    via `DE`/`BC` register pairs, an implementation-level register-allocation choice left to
    `08-code-implementation`). Steps:
    1. **Reseed:** compute `hash(SEED, row, col)` — XOR/shift-mix `SEED` with `row` and `col`
       (the exact mixing formula is `ADR-0016` point 3's own commitment, operationalized here as
       "reseed `gw_prng_step`'s 16-bit state to this mixed value before drawing," mirroring
       `generate_world`'s own per-region reseed pattern exactly, just keyed by `(row,col)`
       instead of a loop index). Seed value 0 normalizes to 1 first (mirrors `ADR-0010`'s existing
       nonzero-state rule, `FS-110` §7's own named edge case).
    2. **Biome-id draw:** one `gw_prng_step` draw, reduced mod 5 via the existing 5-way
       axis-clamp technique `generate_world`'s own biome loop already uses (no `DIV`/`MUL`,
       `NFR-2200`'s constraint, restated here as `NFR-2300`).
    3. **Connectivity — own carve bias:** one more `gw_prng_step` draw decides this region's own
       north/west carve bias (Binary Tree convention, `ADR-0016` point 5).
    4. **Connectivity — south/east openness:** reseed-and-draw for `(row+1, col)` (south
       neighbor) to read whether *it* carved north (determines this region's own south edge);
       reseed-and-draw for `(row, col+1)` (east neighbor) to read whether *it* carved west
       (determines this region's own east edge) — per the Technical Work Breakdown's own
       neighbor-consulting finding. Both neighbor reseeds are transient — discarded immediately
       after the one bit each supplies is read, no persistent state beyond the region being
       materialized (`ADR-0016`'s "zero-memory" framing).
    5. **Compose:** pack biome-id (bits 0-2) + connectivity nibble (bits 3-6, up/down/left/right,
       1=open) into the single output byte `IP-1102`'s `INF_WINDOW` format expects (Technical
       Work Breakdown's own "Per-region encoding" decision).
    6. **Treasure-presence:** a third *sequential* draw from step 2's own reseed state (not a
       second independent reseed — **corrected during implementation**: a second reseed of the
       identical `(SEED, row, col)` reproduces the exact same first-drawn byte, since the reseed
       is a pure function of its inputs, which would have made treasure fully correlated with,
       not independent of, the biome/own-bias draws; this package's own text originally described
       a "fifth reseed-and-draw... a distinct draw... not reusing their post-draw value," which is
       the *intent* this correction actually delivers, just via sequential draws from one reseed
       rather than a doomed second reseed of the same inputs) — `hash(SEED, row, col)`'s third
       drawn byte `AND 0x0F == 0` (`K=16`, Technical Work Breakdown's own resolution of `OQ2`, a
       4-bit mask, no `DIV`). Returned as a separate boolean, not packed into the region byte
       (Technical Work Breakdown: "no treasure-presence bit is stored").
  - **`worldgen.py`**: new `materialize_region(seed, row, col)` Python function, mirroring the six
    steps above step-for-step (same reseed construction, same draw order, same mod-5/mask-0x0F
    reductions) — the lockstep oracle `ADR-0016` point 8 requires.

## 7. Implementation Tasks

Ordered: (1) `inf_materialize_region`'s reseed-and-draw helper (row/col hash-mix, reusable across
all five draws in the routine); (2) biome-id draw + mod-5 reduction; (3) own carve-bias draw;
(4) south/east neighbor reseed-and-draw pair; (5) connectivity-nibble composition; (6)
treasure-presence draw + mask; (7) `worldgen.py` mirror, step-for-step; (8) rebuild ROM; (9)
author T23 (oracle-vs-SM83 lockstep corpus, mirroring `IP-1020`'s own `T12.b` pattern); (10) full
suite run; (11) documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T23: Infinite Mode — Per-Region Materialization`**:

- T23.a — property test: for a corpus of `(SEED, row, col)` triples (spanning negative and
  positive row/col, mirroring `IP-1020`'s own multi-seed/multi-scale corpus breadth), materializing
  the same region twice in the same session produces byte-identical output both times (AC-2
  forward half, FR-10200/FR-10210).
- T23.b — oracle-vs-SM83 lockstep: the same corpus, comparing `worldgen.py`'s
  `materialize_region` against the live SM83-built ROM's `inf_materialize_region`, mirroring
  `IP-1020`'s own `T12.b`/`IP-1070`'s own `T19.c` pattern — 0 mismatches required.
- T23.c — revisit-consistency after simulated eviction: materialize a region, force it out of
  `IP-1102`'s materialized window (a fresh call to `inf_materialize_region` with no prior state
  consulted), confirm identical output to the first materialization (AC-2 reverse half, FR-10210
  — the actual "left and re-entered the window" scenario, not just "called twice in a row").
- T23.d — treasure-density statistical check: over a large `(row, col)` corpus at one fixed seed,
  measured presence rate falls within a reasonable band around `K=16`'s own 6.25% target (mirrors
  `T12.j`'s own non-degeneracy statistical-check shape, `IP-9110`).
- T23.e — determinism static audit (Inspection): direct code read of `inf_materialize_region`
  confirms no read of `DIV`, uninitialized WRAM, or any input besides `SEED`/`row`/`col` (AC-7,
  NFR-2300).
- T23.f — seed=0 normalization: `SEED=0` materializes identically to `SEED=1` (FS-110 §7's named
  edge case).
- T23.g — spawn-region no-special-case: `(row,col)=(0,0)` materializes through the exact same code
  path as any other `(row,col)` — no branch tests for the origin (confirms `OQ4`'s resolution,
  Technical Work Breakdown).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: FR-10200/FR-10210/FR-10300 status →
  Implemented; NFR-2300 status → Met.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-10200/10210/10300/NFR-2300 rows
  → `IP-1101`/T23.
- `docs/features/FS-110-infinite-mode.md` metadata: implemented-by pointer for Workflow B step
  2/Workflow C step 1; §19 Open Questions 2 and 4 marked Resolved (`K=16`, no spawn special-case).
- Master Build Plan status row.

## 10. Definition of Done

- `inf_materialize_region`/`materialize_region` produce byte-identical, revisit-consistent output
  for any `(SEED, row, col)` (T23.a/b/c all passing).
- Treasure-presence predicate matches `hash(SEED, row, col) AND 0x0F == 0` exactly, independent of
  connectivity (T23.d, and a direct comparison against a region whose connectivity was
  deliberately varied while `K`'s own draw input stayed fixed).
- ROM builds at 32768 bytes; full suite passes.
- Static audit confirms no `DIV`/`MUL`, no history-dependent input (T23.e).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T23.a–g each present and passing.
- [ ] Direct code read: the treasure-presence draw is a distinct `gw_prng_step` call from the
      biome/connectivity draws (T23.d's own statistical independence claim rests on this).
- [ ] Direct code read: south/east neighbor reseeds are discarded after their one bit is read —
      no leftover neighbor PRNG state feeds into the current region's own biome/treasure draws.
- [ ] FR-10200/10210/10300/NFR-2300/RTM/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **`IP-1020`/`FEAT-9000`** (`VERIFIED`) — `gw_prng_step`'s own shift/XOR-only construction, reused
  unmodified.

None of this tranche's own packages (`IP-1100`/`1102`/`1103`/`1104`) — this is the tranche's
dependency root; all four depend on it, it depends on none of them.

## 13. Risks

- **NFR-1400 (materialization timing, `UNCONFIRMED`) is not resolved by this package** — up to
  five `gw_prng_step` draws (own biome, own carve-bias, two neighbor reseeds, treasure) per
  materialization event is a real, named cost this package's own Verification Checklist does not
  claim safe against `check_zone_transition`'s timing window; `IP-1102`'s own Analysis-method
  check (NFR-1400, direct cycle-counting) is where this gets measured, not here.
- **The five-draw-per-region cost is higher than `generate_world`'s own single-draw-per-region
  biome pass** (Medium) — a direct, named consequence of streaming generation needing to consult
  neighbors on demand rather than once, up front, in a single pass; not a defect, but a real
  design cost worth flagging for whoever measures NFR-1400.
- ROM budget: a small, bounded routine (five draws, one mod-5 reduction, one mask) — expected
  modest, re-affirmed at build time.

## 14. Rollback Considerations

Revert `asm_game.py`/`worldgen.py`/`test_rom.py` changes and rebuild. No existing routine is
modified (`gw_prng_step` itself untouched) — the finite mode's own generation is completely
unaffected. No WRAM/SRAM address claimed by this package (pure-function routine, no persistent
state of its own) — `IP-1100`/`1102`/`1104` own the WRAM/SRAM this routine's *callers* need.
