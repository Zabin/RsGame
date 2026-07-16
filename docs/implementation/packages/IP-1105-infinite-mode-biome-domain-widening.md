# IP-1105 — Infinite Mode `region_byte` Bit-Field Repack (Biome-Domain Widening, Phase 1)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1105` — a delta package against [**FS-110**](../../features/FS-110-infinite-mode.md)
(`FEAT-10000`, Epic `EP-6000`) — the actual owner of every file/routine this package touches
(`_materialize_region`, `dsr_p_inf`, `czt_infinite`, `szc_infinite`, all `FS-110`'s own Module
Responsibilities) — grounded by `FR-4320` (nine biome-family identities, `BL-0128`, baselined
2026-07-16, `FS-102`'s own delta). Prepares Infinite Mode's own streaming/materialization data
format for `FR-4320`'s widened domain, **without** widening the domain itself — see §2's own
scope boundary.

## 2. Objective

Repack `region_byte`/`INF_MZ_RESULT`'s packed-byte bit layout — the format `worldgen.py`'s
`materialize_region` and `asm_game.py`'s `inf_materialize_region` both produce, and every
Infinite Mode consumer of `INF_WINDOW`'s cells reads — from **biome bits 0-2 / connectivity bits
3-6** to **biome bits 0-3 / connectivity bits 4-7**, freeing a fourth biome-id bit (values 0-15,
up from 0-7) inside the same one-byte format. **This package deliberately does not widen the
biome draw's own value range** (`materialize_region`'s `% 5` stays `% 5`) — only the bit
*positions* change. This is a **behavior-preserving infrastructure step**: every existing
5-value behavior (which screen renders, which edges are open, which region has treasure) must be
bit-for-bit unchanged after this package, confirmed by the Verification Checklist (§11), the same
bar an `08-refactoring` equivalence contract would set even though this ships as forward
infrastructure for `FR-4320` (not debt retirement) and stays `08-code-implementation`.

**Why phase 1, not the full widening:** `generate_world`'s draw range widening (finite mode) and
`dsr_p_dispatch`'s screen-selection cascade both require `CR-08` (`01-functional-requirements.md`
Candidate Requirements) to resolve — which of the four newly-folded identities occupies which of
biome-id positions 5-8. Widening `materialize_region`'s own draw range to `%9` *before* the
dispatch cascade can render those values would make Infinite Mode actually generate regions the
renderer silently mis-renders as Castle (the current unconditional fallthrough) — a real
regression in an already-`VERIFIED`, player-facing feature. This package ships only the safe,
independent half; the value-range widening rides a future package once `CR-08` closes (see the
Technical Work Breakdown's "Nine biome-family identities" section).

## 3. Requirements Covered

`FR-4320` (partial — the Infinite Mode representation half only; the value-range widening and
identity assignment remain open, `CR-08`). No requirement's Acceptance Criteria is fully satisfied
by this package alone — it is preparatory infrastructure, stated honestly rather than claimed as
a completion.

## 4. Architecture Components

[GDS-07](../../architecture/07-data-model.md) — `INF_MZ_RESULT`'s bit-layout description (§7f,
confirm exact section at implementation time) needs updating to the new layout. No ADR governs
this specific bit-packing choice (it was an implementation-time `TWBS` decision when Infinite
Mode's own tranche was planned, per `worldgen.py`'s own docstring: "the TWBS's own per-region
encoding decision") — this package revises that same implementation-level choice, not an
architecture-level one.

## 5. Interfaces

- **`INF_MZ_RESULT`** (`0xC411`, existing) — the packed byte this package repacks. No address
  change, no new WRAM allocation — a pure bit-layout change within the same byte.
- **`INF_WINDOW`** (`0xC3FB`–`0xC403`, existing, 9 bytes) — each cell is a copy of a
  `materialize_region`/`inf_materialize_region` result; every cell's bit layout changes in
  lockstep with `INF_MZ_RESULT`'s own (they are the same format, just cached per window cell).
- **No new `patches` dict key** — pure WRAM-format logic inside already-patched routines, no new
  ROM-resident data table.

## 6. Files to Create/Modify

- **Modify: `worldgen.py`** — `materialize_region` (the Python oracle mirror, confirmed at
  `worldgen.py:253`–`308`): the connectivity-bit OR constants (`0x08`/`0x10`/`0x20`/`0x40` for
  north/south/west/east, `worldgen.py:305`) shift left one bit each to `0x10`/`0x20`/`0x40`/`0x80`;
  `region_byte = (biome & 0x07) | conn` (`worldgen.py:307`) becomes `(biome & 0x0F) | conn` (mask
  width updated for consistency with the new 4-bit biome field, though functionally identical
  while `biome` stays 0-4). The draw itself (`biome = (x1 & 0xFF) % 5`, `worldgen.py:285`) is
  **not modified** — see §2's own scope boundary.
- **Modify: `asm_game.py`**:
  - **`inf_materialize_region`** (`asm_game.py:2586`–`2653`): the four connectivity-bit `OR_n`
    constants at `imr_no_north`/`imr_no_south`/`imr_no_west`/`imr_no_east`
    (`asm_game.py:2640,2646,2643,2649` respectively) shift left one bit each: `0x08`→`0x10`
    (north), `0x10`→`0x20` (south), `0x20`→`0x40` (west), `0x40`→`0x80` (east). The final
    `LD_A_nn(INF_MZ_BIOME); OR_E(); LD_nn_A(INF_MZ_RESULT)` composition
    (`asm_game.py:2651`–`2652`) needs no change — `INF_MZ_BIOME` never exceeds 4 (`inf_mod5`'s own
    range), so it never sets bit 3 or above regardless of which bits the connectivity nibble now
    occupies; no new mask is needed on the biome side for this package's own unchanged 5-value
    range (a future value-widening package would need one, not this one).
  - **`dsr_p_inf`** (`asm_game.py:1385`–`1386`): `rom.AND_n(0x07)` → `rom.AND_n(0x0F)`.
  - **`czt_infinite`** (`asm_game.py:1160,1171,1182,1193`): `BIT_b_A(6)`→`BIT_b_A(7)` (east),
    `BIT_b_A(5)`→`BIT_b_A(6)` (west), `BIT_b_A(3)`→`BIT_b_A(4)` (north),
    `BIT_b_A(4)`→`BIT_b_A(5)` (south) — each connectivity-bit test shifts by exactly one bit,
    matching the repacked layout.
  - **`draw_region_arrows_inf`** (`asm_game.py:1573,1576,1579,1582`): `BIT_b_A(3)`→`BIT_b_A(4)`
    (up), `BIT_b_A(4)`→`BIT_b_A(5)` (down), `BIT_b_A(5)`→`BIT_b_A(6)` (left),
    `BIT_b_A(6)`→`BIT_b_A(7)` (right) — same one-bit shift pattern.
  - **`szc_infinite`** (`asm_game.py:1936`): `rom.AND_n(0x07)` → `rom.AND_n(0x0F)`.
  - **No change** to `inf_mod5`, `inf_ensure_window`'s own call structure, `inf_ledger_find`/
    `inf_ledger_mark_collected`, `save_to_sram`/`try_load_save`'s Infinite Mode branches, or any
    finite-mode code — confirmed clean by this package's own Supersession-sweep cross-check
    (the Technical Work Breakdown's "Nine biome-family identities" section named the complete
    consumer set; this package's Files to Modify matches it exactly, no more, no fewer).
- **Modify: `test_rom.py`**: every hardcoded `& 0x07` mask applied to an `INF_WINDOW`/
  `INF_MZ_RESULT` byte, confirmed by this planning pass's own grep at `test_rom.py:2563` (T26's
  own biome-extraction helper), `2921`, `3134`, `3332` (T26/T27's own inline biome-extraction
  expressions) → `& 0x0F`. **Re-run the grep at implementation time** (`grep -n "0x07"
  test_rom.py`) to confirm this list is still complete against the tree at that point — drift
  here is a hard Blocking condition per this skill's own rule.

## 7. Implementation Tasks

Ordered: (1) confirm every cited line number against the current tree by direct re-read (this
package was planned against commit `6f0574b`; drift is Blocking); (2) repack `worldgen.py`'s
`materialize_region`; (3) repack `asm_game.py`'s `inf_materialize_region`; (4) update the four
consumer sites' bit-position reads (`dsr_p_inf`, `czt_infinite`, `draw_region_arrows_inf`,
`szc_infinite`); (5) update every `test_rom.py` site the final grep sweep finds; (6) full suite
run — every existing Infinite Mode check (T22/T24/T25/T26/T27) must pass **unchanged in
assertion, only in the underlying bit-extraction expression** (a check that used to read
`byte & 0x07` now reads `byte & 0x0F` but asserts the identical expected value, since the
underlying biome-id itself never exceeds 4 for this package's own unchanged draw range); (7)
`worldgen.py`/SM83 lockstep re-confirmed (the oracle-parity checks, e.g. `T22`'s own, must show
zero mismatches with the new bit layout on both sides); (8) documentation updates (§9).

## 8. Tests to Add

No new suite or new check — this package is a **format change under existing checks**, not new
behavior. Every existing test that reads `INF_MZ_RESULT`/`INF_WINDOW` and extracts biome-id or
connectivity bits must be corrected to the new bit positions (§6's own `test_rom.py` list) and
must continue to pass with **identical expected values** — the check that this package changed
nothing observable *is* the existing suite, run unmodified in its assertions. If any existing
check's own expected value needs to change to keep passing, that is a signal this package
introduced an unintended behavior change — a Blocking condition, not a test update.

## 9. Documentation Updates

- `docs/architecture/07-data-model.md`: the `INF_MZ_RESULT`/`region_byte` bit-layout description
  (wherever §7f or its successor documents it — confirm the exact section at implementation time
  via `grep -n "INF_MZ_RESULT" docs/architecture/07-data-model.md`) updated to the new bit
  positions (biome 0-3, connectivity 4-7), with a dated delta note citing this package and
  `FR-4320`/`BL-0128` as the reason, not a silent rewrite.
- `docs/requirements/01-functional-requirements.md`: `FR-4320`'s own Notes gains a line noting
  this package as the first concrete step toward its own Infinite Mode representation fact,
  **not** marking `FR-4320` itself Implemented (the value-range widening and identity assignment
  remain open).
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- `region_byte`/`INF_MZ_RESULT`'s bit layout is biome bits 0-3 / connectivity bits 4-7, confirmed
  by direct diff against the pre-package format.
- The biome draw's own value range is unchanged (`% 5`, values 0-4 only) — confirmed by direct
  diff of `materialize_region`'s/`inf_materialize_region`'s own draw logic (only the OR-constant
  values changed, not the modulo or the draw sequence).
- Every one of the four rendering/navigation/collection consumer sites (`dsr_p_inf`,
  `czt_infinite`, `draw_region_arrows_inf`, `szc_infinite`) reads the new bit positions correctly
  — confirmed by the full existing Infinite Mode test suite passing with unchanged expected
  values.
- `worldgen.py`'s oracle and the SM83 routine remain in lockstep — zero mismatches across the
  existing corpus, confirmed by the existing oracle-parity checks re-run against the new format.
- No finite-mode file, label, or behavior touched — confirmed by diff scope.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes, with **zero expected-value changes** in any existing
      check (a changed underlying bit-extraction expression is expected; a changed expected
      result is not, and is Blocking if found).
- [ ] Direct diff: `materialize_region`'s/`inf_materialize_region`'s own draw range and sequence
      unchanged — only the OR-constant/mask values differ.
- [ ] Direct diff: every finite-mode file (`asm_game.py`'s non-Infinite-Mode labels, `tilemaps.py`,
      `build_rom.py`) byte-for-byte unchanged.
- [ ] Oracle-parity re-confirmed: `worldgen.py` and the SM83 routine produce bit-identical
      `region_byte` output for the existing test corpus, under the new bit layout.
- [ ] `test_rom.py`'s own final grep sweep (§6) confirmed complete — no remaining `& 0x07`/
      `BIT_b_A(3..6)` reference tied to `INF_MZ_RESULT`/`INF_WINDOW` anywhere in the file.

## 12. Dependencies

- **`IP-1101`** (`VERIFIED`) — `_materialize_region`'s own original shipped format, this package
  repacks.
- **`IP-1102`** (`VERIFIED`) — `dsr_p_inf`/`czt_infinite`/`draw_region_arrows_inf`, the consumer
  routines this package updates.
- **`IP-1103`** (`VERIFIED`) — `szc_infinite`, a fourth consumer this package updates.
- No other in-flight package's Files to Modify overlap this one's own (`IP-1033` touches only
  `tilemaps.py`'s `ZONE_COLLECTS`, disjoint).

## 13. Risks

Low — the entire package is a mechanical, one-bit-position shift applied to a fixed, fully-
enumerated consumer set (five call sites plus the two producer routines, all named in §6, cross-
checked against the Technical Work Breakdown's own Supersession sweep). The one real risk: **a
missed consumer site would silently corrupt Infinite Mode's own rendering/navigation for the
already-shipped 5-value case** (an OR/AND mask reading the old bit positions after the producer
routines write the new ones) — mitigated by the Verification Checklist's own "zero expected-value
changes" bar, which would fail loudly (wrong screen/wrong open-edge) rather than silently if any
site were missed.

## 14. Rollback Considerations

Revert the four OR-constant/mask changes in `worldgen.py`/`asm_game.py`'s two producer routines,
the four consumer-site bit-position reads, and the `test_rom.py` mask corrections, then rebuild.
No save-format dependency — `INF_MZ_RESULT`/`INF_WINDOW` are both transient, generation-time-only
WRAM (never persisted to SRAM, confirmed by `GDS-07`'s own "no region's biome or connectivity is
ever persisted" note, §7g/h) — no version bump, no migration path needed.
