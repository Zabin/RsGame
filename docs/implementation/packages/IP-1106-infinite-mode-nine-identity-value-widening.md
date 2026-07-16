# IP-1106 — Infinite Mode Nine-Identity Value-Range Widening

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1106` — a delta package against [**FS-110**](../../features/FS-110-infinite-mode.md)
(`FEAT-10000`, Epic `EP-6000`), grounded by `FR-4320` (`BL-0128`, `CR-08` resolved into `FR-4310`
2026-07-16). Completes the Infinite Mode half of `FR-4320`'s widening — `IP-1105` (this same
delta's earlier package) prepared the bit-layout headroom; this package widens the actual value
range now that its two real prerequisites (`IP-1105`'s repack, `IP-1022`'s shared dispatch
cascade) exist.

## 2. Objective

Widen `worldgen.py`'s `materialize_region` and `asm_game.py`'s `inf_materialize_region` biome
draw from `%5` to `%9`, and extend `inf_treasure_pos`'s per-biome treasure-position table from
five `(x,y)` entries to nine, matching `IP-1033`'s own authored content for the four new
identities.

## 3. Requirements Covered

`FR-4320` (nine biome-family identities — the Infinite Mode half of this FR's own domain
widening, completing what `IP-1105` prepared).

## 4. Architecture Components

None new — this package widens an already-established, `VERIFIED` mechanism (`FR-10200`,
`IP-1101`/`IP-1102`) rather than introducing new architecture. `IP-1105`'s own bit-layout repack
(itself grounded in `worldgen.py`'s own docstring: "the TWBS's own per-region encoding decision,"
an implementation-level choice, not an ADR-level one) is the only architecture-adjacent artifact
this package builds on.

## 5. Interfaces

- **`region_byte`/`INF_MZ_RESULT`** (`0xC411`, `IP-1105`'s repacked format: biome bits 0-3,
  connectivity bits 4-7) — this package widens the *value* the biome field carries (0-4 → 0-8);
  the bit *positions* are unchanged, already correct from `IP-1105`.
- **`inf_treasure_pos`** (`asm_game.py:1838`, existing 5-entry `(x,y)` table) — extended to 9
  entries, indices 5-8 populated with the same `(x,y)` values `IP-1033`'s own staged
  `ZONE_COLLECTS` type-2 entries use for Village/Cave/Desert/Plains (per `inf_treasure_pos`'s own
  documented "values duplicated here rather than imported... `T26.a0`'s static check asserts this
  table matches `ZONE_COLLECTS`'s type-2 entries" convention, `asm_game.py:1825`–`1837`).
- **`dsr_p_dispatch`** (consumed, not modified — `IP-1022`'s own scope) — this package's own
  widened draw values (5-8) are only meaningful once that cascade recognizes them; a real
  sequencing dependency, not an interface this package itself changes.

## 6. Files to Create/Modify

- **Modify: `worldgen.py`** — `materialize_region`'s `biome = (x1 & 0xFF) % 5` (`worldgen.py:285`)
  → `% 9`. No other change to the draw sequence (the treasure-presence and carve-bias draws that
  follow are domain-agnostic, confirmed by direct re-read).
- **Modify: `asm_game.py`**:
  - **`inf_materialize_region`** (`asm_game.py:2586`–`2653`) — the `inf_mod5` subroutine call
    (`asm_game.py:2593`) either widened in place or replaced with a new `inf_mod9`-equivalent
    (implementation's own choice — both achieve the same domain-agnostic mod-N reduction this
    routine already performs; if `inf_mod5` is shared by any other call site, confirm via direct
    grep before modifying in place rather than assuming it's Infinite-Mode-biome-draw-exclusive).
  - **`inf_treasure_pos`** (`asm_game.py:1825`–`1845`) — four new `(x,y)` entries appended
    (indices 5-8: Village, Cave, Desert, Plains, matching `IP-1022`'s own `CR-08`-resolved
    ordering), each value copied verbatim from `IP-1033`'s own authored `ZONE_COLLECTS` type-2
    entry for that identity — not independently chosen, per this table's own established
    duplication convention.
- **Modify: `test_rom.py`**: `T26.a0`'s own static check (confirmed at whatever line currently
  asserts `inf_treasure_pos` matches `ZONE_COLLECTS`'s type-2 entries — re-locate by direct grep
  at implementation time) extended to cover all nine entries, not just five; any other check that
  hardcodes `inf_treasure_pos`'s own 5-entry length (search `len(...)`/index-bound assertions
  referencing this table specifically) updated to 9.
- **No change** to `IP-1105`'s own bit-repack (already shipped by the time this package runs,
  per its own Dependencies below), `dsr_p_dispatch`'s cascade (`IP-1022`'s own scope, consumed
  read-only here), or any finite-mode file — confirmed clean by this package's own Supersession
  sweep re-run (mirrors the Technical Work Breakdown's own full-consumer-set finding for
  `INF_WINDOW`/`INF_MZ_RESULT`, re-checked here for the value-range-specific consumer,
  `inf_treasure_pos`, which the TWBS's earlier sweep for `IP-1105` correctly did **not** include,
  since it's a value-range concern, not a bit-layout one).

## 7. Implementation Tasks

Ordered: (1) confirm every cited line number against the current tree by direct re-read (drift is
Blocking); (2) confirm `IP-1105` has shipped and `VERIFIED` (bit layout must already be repacked)
and `IP-1022` has shipped and `VERIFIED` (dispatch cascade must already recognize 5-8) — both hard
Blocking preconditions, not merely recommended sequencing; (3) confirm `IP-1033`'s own four
`(x,y)` type-2 values exist (this package's own `inf_treasure_pos` entries must match them
exactly, per the established duplication convention); (4) widen `worldgen.py`'s draw; (5) widen
`asm_game.py`'s `inf_materialize_region`'s mod-N reduction; (6) extend `inf_treasure_pos`; (7)
rebuild, full suite run; (8) extend `T26.a0`/any other 5-entry-hardcoding check; (9)
documentation/traceability updates (§9).

## 8. Tests to Add

Landing in the existing **T26**/**T27** Infinite Mode suites (no new suite — a revision of an
existing, `VERIFIED` capability):

- **`T26.a0` (extended)** — the existing `inf_treasure_pos`-vs-`ZONE_COLLECTS` drift guard,
  re-run across all nine entries instead of five.
- **New: value-range coverage check** — a corpus of `(seed, row, col)` triples confirming
  `materialize_region`'s own biome draw reaches values across the full 0-8 range (not just 0-4)
  for a sufficiently large sample, mirroring `T22`'s own determinism/oracle-parity corpus
  methodology.
- **New: dispatch-integration check** — force `INF_WINDOW`'s center cell to each of biome-ids 5-8
  directly (mirroring `T25`'s/this session's own `content-review-ip-1081-ip-1082.md` direct-force
  pattern) and confirm the correct screen renders *and* the correct treasure position spawns,
  exercising `IP-1022`'s dispatch and this package's own `inf_treasure_pos` extension together —
  the actual end-to-end integration point neither package alone can fully verify in isolation.

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-4320`'s own Notes → this package closes
  the Infinite Mode representation-level pointer that FR's own Notes named, once `VERIFIED`.
- `docs/requirements/04-requirements-traceability-matrix.md`: `FR-4320` row's Module/
  Implementation Package/Test columns filled (jointly with `IP-1022`, both packages together
  fully implement it).
- `docs/features/FS-110-infinite-mode.md` metadata: the `IP-1105` forward-reference note extended
  to record this package as its own direct successor, closing the "prepares... for a future
  widening" framing `IP-1105`'s own delta note used.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Infinite Mode's own per-region materialization draws from the full nine-value biome-id domain,
  confirmed across a `(seed, row, col)` corpus.
- Every one of the nine identities renders its own correct screen and spawns its own correct
  treasure position when materialized in Infinite Mode, confirmed by direct-force integration
  testing (§8).
- `inf_treasure_pos`'s nine entries match `ZONE_COLLECTS`'s own nine type-2 entries exactly,
  confirmed by the extended `T26.a0` drift guard.
- No finite-mode file, `IP-1022`'s own dispatch cascade, or `IP-1105`'s own bit-layout code
  touched beyond the specific mask/constant this package's own §6 names — confirmed by diff scope.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Direct diff: `IP-1105`'s own bit-layout code and `IP-1022`'s own dispatch cascade both
      confirmed byte-for-byte unchanged by this package.
- [ ] Value-range coverage check (§8) confirms the draw reaches all nine values across a
      sufficient corpus.
- [ ] Dispatch-integration check (§8) confirms all four new identities render and spawn treasure
      correctly in Infinite Mode specifically (not merely inherited from `IP-1022`'s own finite-
      mode-only verification).
- [ ] `T26.a0` (extended) confirms `inf_treasure_pos`/`ZONE_COLLECTS` parity across all nine
      entries.

## 12. Dependencies

- **`IP-1105`** (`NOT STARTED`, not authorized) — the bit-layout repack this package's own value
  widening lands on top of. **Hard Blocking precondition**, per the Technical Work Breakdown's own
  explicit sequencing note ("`IP-1105` shipping first is a genuine, deliberate prerequisite").
- **`IP-1022`** (`BLOCKED`, this same planning pass) — the shared `dsr_p_dispatch` cascade this
  package's own widened draw values need to already be render-safe against. **Hard Blocking
  precondition** — the same live-regression risk `IP-1105`'s own TWBS entry named applies here in
  full force (widening the draw without the dispatch cascade already recognizing 5-8 would make
  Infinite Mode generate regions the renderer mis-renders as Castle).
- **`IP-1033`** (`NOT STARTED`, not authorized) — the `(x,y)` values `inf_treasure_pos`'s own four
  new entries duplicate.
- This package is therefore **`BLOCKED`** on three unshipped prerequisites, the deepest point in
  this delta's own dependency chain (`IP-1033`/`IP-1105` → `IP-1022` → `IP-1106`).

## 13. Risks

Low — every individual change (a modulo-bound widening, four table-entry appends) is mechanical
and follows established precedent (`IP-1105`'s own equivalent widening reasoning, `inf_treasure_pos`'s
own existing duplication convention). The one real risk is sequencing discipline: shipping this
package's own code changes before its three prerequisites are actually `VERIFIED` (not merely
`COMPLETE`) would reintroduce the exact live-regression risk `IP-1105`'s own TWBS entry first
identified — named explicitly in Dependencies above as a hard Blocking condition, not a soft
recommendation, specifically to prevent that sequencing error.

## 14. Rollback Considerations

Revert the draw-range widening and the four `inf_treasure_pos` entries, then rebuild. No
save-format dependency — `INF_MZ_RESULT`/`INF_WINDOW`/`inf_treasure_pos` are all transient,
generation-time-only WRAM/ROM-resident data (never persisted to SRAM, confirmed by `GDS-07`'s own
"no region's biome or connectivity is ever persisted" note, mirroring `IP-1105`'s own identical
finding) — no version bump, no migration path needed.
