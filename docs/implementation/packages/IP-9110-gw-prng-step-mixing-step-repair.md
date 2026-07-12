# IP-9110 — `gw_prng_step` Mixing-Step Repair

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9110` — bug-remediation series; no FS. Source: **`BL-0074`** (High, project owner report,
filed via `00-intake`, this session), decided by **`ADR-0014`**.

## 2. Objective

Repair `gw_prng_step`'s (`asm_game.py`) own mixing step so it no longer degenerates to a fixed
point or short cycle within a handful of draws for effectively every seed — confirmed this
session: 100% of 2000 tested seeds under the shipped routine, 0% under the corrected fix. This is
the routine every world-generation draw depends on (biome-assignment, once per region, and via
`IP-1070` the maze-generation pass, many draws per generation event); repairing it directly fixes
the reported symptom (a heavily Water-flooded world at the literal default seed) and the much
larger defect the investigation found underneath it (roughly half of all `scale=9` worlds are
already degenerate today, not just the default).

## 3. Requirements Covered

No FR/NFR text changes — this package fixes a defect in the shipped implementation of already-
baselined behavior (`FR-9100`, deterministic world generation from `(seed, scale)`; `NFR-2200`,
no `DIV`/`MUL` opcodes — the fix stays shift/XOR-only, satisfying this unchanged). No requirement
ever specified "the PRNG shall not degenerate" as a testable criterion — that gap is itself worth
a Notes-only forward pointer (§9), mirroring this session's own established pattern
(`IP-9090`/`IP-9100`) for correcting an FR/NFR's own text is out of this stage's scope.

## 4. Architecture Components

Directly implements **`ADR-0014`**'s decision (repair `gw_prng_step`'s mixing step to the
period-sound `7,9,8` shift triplet), which itself extends **`ADR-0013`**'s PRNG-decorrelation
work and is grounded by **R113** (root cause, the `7,9,8` triplet citation) and **R111** (the
original, now-confirmed-incomplete PRNG characterization). Does not touch `ADR-0009`'s own
determinism guarantee (`REGION_GRAPH` regenerates from `(seed, scale)` alone) — that guarantee is
exactly *why* this fix needs a save-version bump (§6), not evidence against making the fix.

## 5. Interfaces

None new. `gw_prng_step`'s own interface (`TMP1:TMP2` in, `TMP1:TMP2` out, called via `CALL`) is
unchanged — only its internal algorithm. `worldgen.py`'s `_step(x)` function (its own interface:
16-bit int in, 16-bit int out) is likewise unchanged in shape, only in internal algorithm.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`gw_prng_step`** (`asm_game.py:1200-1214` as of this session — confirm exact lines during
    authoring, drift check). Replace the current three-step mixing sequence
    (`x^=x<<1; x^=x>>1; x^=byteswap(x)`, `asm_game.py:1203-1213`) with the verified `7,9,8`
    shift-based triplet (`x^=x<<7; x^=x>>9; x^=x<<8`), keeping the routine's own
    `TMP1:TMP2` (hi:lo) storage convention and `CALL`/`RET` interface identical:
    - **`x ^= x<<7`**: SM83 has no shift-by-N opcode and no cheap decomposition exists for a
      truncated 16-bit left-shift-by-7 via the free byte-move trick (verified directly this
      session: `(x<<8)>>1 ≠ x<<7` for roughly half of all 16-bit values — the naive decomposition
      is wrong, don't use it). Compute via **7 chained applications of the existing single-bit
      left-shift primitive** the routine's own current step 1 already uses correctly (`SLA` on
      the low byte to shift it and produce a carry from its own bit 7, `RLA` on the high byte to
      rotate that carry in as its own bit 0) — a small counted loop (7 iterations) into a scratch
      register pair, mirroring the existing `gw_sq_loop` repeated-operation idiom already used
      elsewhere in `generate_world` for `WORLD_SCALE²`. XOR the scratch pair into `TMP1:TMP2`.
    - **`x ^= x>>9`**: **verified directly this session** that `x>>9 == (x>>8)>>1` exactly, for
      all 16-bit values (0 mismatches across the full 65536-value range) — a genuine free
      decomposition, unlike the left-shift case. Compute via a byte-move (`scratch_hi := 0,
      scratch_lo := TMP1`, i.e. `x>>8`) followed by **one** single-bit right shift (`SRL` on the
      scratch high byte, `RRA` on the scratch low byte, mirroring the routine's own existing step
      2's right-shift primitive) — 3-4 instructions total, not a 9-iteration loop.
    - **`x ^= x<<8`**: a straight byte-move (`scratch_hi := TMP2` (the old low byte), `scratch_lo
      := 0`) — **cheaper than today's byte-swap step** (which cross-XORs both bytes together);
      this is the change R113 already flagged as a net cost reduction, not just a correctness fix.
    - Each of the three steps XORs its own scratch-computed shifted value into the running
      `TMP1:TMP2` state, exactly mirroring the existing routine's own three-step structure — only
      the shift amounts and the third step's own operation (byte-move instead of cross-XOR
      byte-swap) change.
  - **`SAVE_VERSION_VAL`** (`asm_game.py:122`, currently `0x03`): bump to `0x04` — the fourth bump
    in the established `IP-1010`→`IP-1050`→`IP-9070` strictly-monotonic sequence. A pre-fix save
    is thereby excluded from "continue" deliberately (the existing `check_save_valid`/
    `try_load_save` version-mismatch machinery already handles this automatically, zero code
    changes needed there — confirmed by direct read, the same generic version-guard `IP-1040`/
    `IP-1050`/`IP-9070` already established) rather than silently reinterpreted into a different
    world with no signal to the player.
  - **`IP-1070`'s own `GW_MAZE_DRAW_CTR` perturbation** (`asm_game.py`'s maze-generation pass,
    `_perturb_draw`): **not removed by default** — this package's own investigation (a Python
    simulation using the corrected `_step`, 20 seeds at `scale=5`) found the braid pass still
    lands in a statistically reasonable band both **with** the perturbation (26.3% reopened) and
    **without** it (20.7% reopened, using the now-repaired raw PRNG alone) — the perturbation is
    no longer load-bearing for correctness, but removing it is a separate simplification with its
    own (small) risk of disturbing `T19.e`'s already-passing statistical check for no required
    benefit. **This package's own Definition of Done does not require removing it** — leave
    `ADR-0013`'s perturbation in place as defense-in-depth (`ADR-0014`'s own explicitly-offered
    option), and note this as a real, deliberate scope boundary, not an oversight. A future
    package may simplify it once `IP-1070` itself is `VERIFIED` and this fix has real-world
    mileage.
- **Modify: `worldgen.py`**:
  - **`_step(x)`** (`worldgen.py:16-22`): replace the three-line mixing sequence with the
    corrected `7,9,8` shift-triplet in plain Python (`x ^= (x<<7)&0xFFFF; x ^= x>>9; x ^= (x<<8)&0xFFFF`)
    — the exact lockstep-mirror discipline `ADR-0012`/`ADR-0013` already established, extended
    here to the base mixing step itself rather than a perturbation layered on top of it.
- **Modify: `test_rom.py`**: add the new non-degeneracy check (§8) to the existing **`T12: World
  Generation`** suite. No other check needs updating — confirmed by this pass's own supersession
  sweep (TWBS, "gw_prng_step mixing-step repair" section): every existing `worldgen`-dependent
  check compares against the live oracle for the same `(seed, scale)`, none hardcodes an
  independent expected value.

## 7. Implementation Tasks

Ordered: (1) confirm `gw_prng_step`'s exact current line numbers (drift check); (2) implement the
`7,9,8` shift-triplet mixing step per §6's own instruction-level guidance; (3) bump
`SAVE_VERSION_VAL` `0x03`→`0x04`; (4) update `worldgen.py`'s `_step` in lockstep; (5) rebuild ROM,
run the full suite, confirm every existing `T12`/`T19`/`T5`/`T11`/`T17` check that depends on
`worldgen.py` still passes (it should, automatically, per the supersession sweep — a failure here
is itself a signal the oracle mirror isn't exact); (6) author the new non-degeneracy check (§8);
(7) full suite run again with the new check; (8) re-confirm (via direct PyBoy check, not
assumption) that `BL-0074`'s own originally-reported cases — `seed=0` at `scale=3` and `scale=9`
— now produce a properly varied `REGION_GRAPH`, not a Water-flooded one; (9) documentation/
traceability updates (§9).

## 8. Tests to Add

Extends the existing **`T12: World Generation`** suite (`test_rom.py`) — no new suite number:

- **T12.j — Non-degeneracy statistical check (the direct `BL-0074` regression test).** Across a
  seed corpus (recommend at least 30-50 seeds spanning small integers and the existing
  `T12_CORPUS`/`T19_CORPUS` values, plus explicitly `seed=0`) at `scale=9` (the scale where the
  shipped defect was most visible), assert the fraction of regions assigned `biome_id=0` (Water)
  stays within a statistically reasonable band (e.g. under ~40%, well above the ~46% mean and
  ~55%-of-seeds-over-50% this session measured for the *unrepaired* PRNG) — a check that would
  have caught this exact defect had it existed when `IP-1020` originally shipped. Use the live
  SM83-built ROM (via `invoke_generate_world` or a real new-game creation), not only the Python
  oracle, since the oracle is the thing being kept in lockstep, not independent evidence.
- **T12.k — Direct `BL-0074` reproduction check.** `seed=0` at `scale=9`: confirm the generated
  `REGION_GRAPH`'s Water fraction is no longer the near-total-flood the pre-fix routine produced
  (row 0 = `[2,3,2,1,0,0,0,0,0]`, rows 1-8 all zero) — the literal reported case, checked directly,
  not only inferred from the statistical check above.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: add a Notes entry to `FR-9100` recording the
  `gw_prng_step` mixing-step repair (citing `BL-0074`/`ADR-0014`) and flagging that no FR/NFR
  currently states a testable "the PRNG shall not degenerate" criterion — a candidate for a future
  `04-requirements-engineering` pass, not resolved here.
- `docs/requirements/02-non-functional-requirements.md`: confirm `NFR-2200`'s "no `DIV`/`MUL`"
  constraint is still satisfied by the corrected mixing step (it is — shift/XOR only) and add a
  Notes entry citing this package.
- `docs/requirements/04-requirements-traceability-matrix.md`: update `FR-9100`'s Test cell to cite
  the new `T12.j`/`T12.k` checks.
- `docs/architecture/adr/ADR-0014-gw-prng-step-repair-needs-user-authorization.md`: **not modified**
  (ADRs are append-only history, per this project's own standing convention) — the authorization
  record lives in `BL-0074`'s own backlog disposition and the pipeline journal, not by rewriting
  the ADR.
- Master Build Plan status row.

## 10. Definition of Done

- `gw_prng_step`'s mixing step implements the `7,9,8` shift triplet exactly; `SAVE_VERSION_VAL` is
  `0x04`; `worldgen.py`'s `_step` mirrors the corrected algorithm exactly (oracle parity checks
  pass with zero mismatches across the full existing corpus).
- `T12.j`/`T12.k` demonstrably pass; every existing check that depends on `worldgen.py` still
  passes unchanged (no hardcoded-value updates needed, confirmed by the supersession sweep).
- `BL-0074`'s own originally-reported case (`seed=0`, `scale=3`/`scale=9`) directly re-checked and
  confirmed no longer Water-flooded.
- ROM builds at 32768 bytes; full suite passes.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct code read: `gw_prng_step`'s mixing step matches the `7,9,8` shift-triplet shape
      described in §6, not the old `1,1,byteswap` sequence.
- [ ] Direct code read: `SAVE_VERSION_VAL` reads `0x04`.
- [ ] `worldgen.py`'s `_step` matches `gw_prng_step`'s corrected algorithm exactly — `T12.a`/`T12.b`/
      `T19.c` (oracle-parity checks) pass with zero mismatches across their full existing corpus.
- [ ] `T12.j`/`T12.k` present and passing.
- [ ] Direct PyBoy re-check of `BL-0074`'s own literal reported case (`seed=0`, `scale=9`) shows a
      properly varied `REGION_GRAPH`, not the pre-fix Water-flooded grid.
- [ ] A pre-fix (version `0x03`) save is confirmed excluded from "continue" (existing
      version-guard machinery, no new code needed — confirm by direct test, not assumption).
- [ ] Requirements/RTM deltas applied exactly as §9 names.

## 12. Dependencies

None functionally — `gw_prng_step` has no upstream dependency beyond `IP-1010`'s own bootstrap
(`VERIFIED`). **Named risk, not a blocking dependency:** `IP-1070` (maze-shaped region adjacency,
`COMPLETE`, not yet `VERIFIED`) calls `gw_prng_step` extensively via its own maze-generation pass
— this package's change to the routine `IP-1070` depends on is a real interaction surface (see
Risks). Independent of every other package in-flight this session.

## 13. Risks

- **Low-Medium.** The algorithm change itself is well-verified (0/2000 seeds degenerate under the
  corrected triplet, direct exhaustive verification of the `>>9` decomposition, direct simulation
  of the maze pass's own braid-fraction outcome both with and without `ADR-0013`'s perturbation).
- **Interaction with `IP-1070`'s own not-yet-`VERIFIED` maze pass**: this package changes the raw
  PRNG stream every maze-generation draw ultimately derives from (whether or not `GW_MAZE_DRAW_CTR`'s
  perturbation stays in place). `IP-1070`'s own `T19` suite (subgraph validity, reachability,
  determinism, grammar-validity, braid-fraction statistics) is expected to keep passing — these
  checks assert *properties*, not fixed values — but this package's own Verification Checklist
  runs the full suite specifically to catch any unexpected interaction, not merely trusts the
  simulation above.
- **Save-format version bump is a real, intentional player-facing change** (named explicitly in
  §6, not a side effect) — any save created before this ships is excluded from "continue," exactly
  as the user's own authorization anticipated.
- ROM budget: the corrected mixing step is comparable-or-cheaper in bytes than the routine it
  replaces (per R113's own cost analysis, confirmed at implementation time, not merely assumed).

## 14. Rollback Considerations

Revert `asm_game.py`'s `gw_prng_step`/`SAVE_VERSION_VAL` changes and `worldgen.py`'s `_step`
change, then rebuild. Reverts to the shipped (degenerate-for-effectively-all-seeds) PRNG exactly.
**Note the asymmetry:** rolling back does *not* restore the illusion of a working PRNG for players
who already continued past the version bump on the repaired build — their saves were created under
`SAVE_VERSION_VAL=0x04`'s world-generation algorithm; a rollback would need its own version bump
(or those saves become the "pre-upgrade" case) to avoid the inverse problem this package's own
version bump exists to prevent. This is the standard, already-established cost of any save-format-
relevant rollback in this project (identical in kind to rolling back `IP-1050`/`IP-9070`), not a
new risk this package introduces.
