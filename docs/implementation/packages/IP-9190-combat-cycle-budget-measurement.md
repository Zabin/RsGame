# IP-9190 — Combat Sub-Mode Per-Frame Cycle Budget Measurement (`BL-0168`)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9190` — remediation package for [`BL-0168`](../../pipeline/backlog.md): `NFR-1500`
(combat sub-mode per-frame cycle budget) was never directly measured across any of the ten
packages that implement combat-mode per-frame logic (`IP-1120`–`IP-1129`). Its own Acceptance
Criteria requires the measurement "before the owning implementation package is considered
`COMPLETE`" — none of the ten ever performed it; this package closes that gap now, after the
fact, mirroring `NFR-1400`/`IP-1102`'s own "measure honestly, don't assume" precedent.

## 2. Objective

Directly cycle-count the combat sub-mode's real per-frame logic — `inf_mob_move` →
`inf_projectile_update` (incl. `inf_projectile_hittest`) → `inf_mob_contact_check` →
`inf_invincibility_tick`, the unconditional call chain `st_playing` already runs every frame
(`asm_game.py:711`-714, each routine self-gating on `COMBAT_MODE`) — on **(a)** a combat-only
frame, and **(b)** a frame where that chain coincides with Infinite Mode region materialization
(reachable: `check_zone_transition`/`czt_infinite` runs immediately after the combat chain in
the same `st_playing` tick, so a region-boundary crossing while `COMBAT_MODE=1` triggers
`inf_ensure_window`'s own already-`NOT MET` cost on the identical frame). Record the result
honestly against the 70,224-cycle single-frame budget — Met or Not Met, mirroring `NFR-1400`'s
own precedent that an honest measurement, not compliance, is what closes the NFR.

## 3. Requirements Covered

- **`NFR-1500`** (combat sub-mode per-frame cycle budget) — this package performs the
  measurement its Acceptance Criteria requires and updates its Status/Notes with the result.

## 4. Architecture Components

None new. `ADS-002` §System Architecture already names the cycle-budget constraint this package
measures against; no architecture delta. Mirrors `IP-1102`'s own `NFR-1400` T24.e precedent
exactly — a test-only Analysis check, not a new runtime component.

## 5. Interfaces

- **`inf_mob_move`** (`asm_game.py:3582`), **`inf_projectile_update`** (`:3676`, itself calling
  `inf_projectile_hittest` at `:3689`), **`inf_mob_contact_check`** (`:3793`),
  **`inf_invincibility_tick`** (`:3924`) — the four routines measured, called unconditionally
  from `st_playing` (`:711`-714), each returning immediately (`OR_A(); RET_Z()`-style gate) when
  `COMBAT_MODE=0`. Read-only — this package calls them via the existing PC/SP-hijack technique,
  never modifies them.
- **`check_zone_transition`** (`:1376`) / **`czt_infinite`** (`:1508`) / **`inf_ensure_window`**
  (`:1447`, `IP-1102`'s own routine) / **`czt_redraw`** (`:1432`) — the materialization chain the
  "coinciding" measurement's end-hook rides, identical to `T24.e`'s own established end point.
- **`COMBAT_MODE`** (`0xC6B5`), **`MOB_COUNT`** (`0xC6B6`), **`MOB_DATA`** (`0xC6B7`-`0xC6D4`, 6
  slots × 5 bytes), **`PROJ_ACTIVE`** (`0xC6D5`) — WRAM state this package's test setup writes
  directly (fixture injection, the same pattern `T35`/`T36`/`T37` already use) to construct a
  realistic non-empty combat frame, not an idle no-op one (measuring `COMBAT_MODE=1` with
  `MOB_COUNT=0`/`PROJ_ACTIVE=0` would understate the real cost — every gated routine would
  short-circuit on its own count/flag check almost immediately).
- **`INF_ROW`/`INF_COL`/`INF_WINDOW`** (existing, `IP-1101`/`IP-1102`) — same fixture role
  `T24.e` already established, reused unchanged for the "coinciding" measurement's boundary
  setup.

## 6. Files to Create/Modify

- **Modify: `test_rom.py`** — new suite `T39` (Analysis-only, no `asm_game.py`/`gbc_lib.py`/
  `build_rom.py`/`worldgen.py` change). Two measurement helpers mirroring
  `measure_inf_ensure_window_cycles` (`test_rom.py:2876`) exactly in technique (PC/SP hijack,
  `hook_register` entry/return, `pb._cycles()` delta):
  - `measure_combat_frame_cycles(mob_count, proj_active)` — hijack PC to `inf_mob_move`, return
    address `check_zone_transition`'s own entry (the natural boundary: the combat chain's last
    routine, `inf_invincibility_tick`, `RET`s straight into whatever called `inf_mob_move` in the
    real flow, i.e. the point immediately before `check_zone_transition` in `st_playing`'s own
    sequence) — captures the combat chain alone, player positioned mid-region (no transition
    reachable that tick).
  - `measure_combat_and_materialization_cycles(mob_count, proj_active, seed, row, col)` — same
    start hook (`inf_mob_move`), end hook at `czt_redraw` (`T24.e`'s own established safe ROM
    hook point) — captures the combat chain plus a real `inf_ensure_window` recompute in the
    same tick, via the same `INF_ROW`/`INF_COL`/boundary-crossing-input fixture `T24.e` and
    `T25`-`T29`'s own Infinite Mode tests already use (position at a region-edge coordinate, one
    directional input held, `COMBAT_MODE=1`).
- **No change** to `asm_game.py`, `gbc_lib.py`, `build_rom.py`, `worldgen.py`, `tiles.py`,
  `tilemaps.py`, `music.py` — this package adds no runtime code, only a measurement.

## 7. Implementation Tasks

Ordered: (1) confirm the four routines' current entry addresses and the `st_playing` call
sequence by direct re-read (drift check — `IP-8xx0` refactor tranche touched
`inf_mob_contact_check`/`inf_mob_move`'s own internals via extracted subroutines, `IP-8010`/
`IP-8020`; confirm the routines' own entry points and external behavior are unchanged, which
their own `VERIFIED` equivalence evidence already establishes, but re-derive rather than assume);
(2) implement `measure_combat_frame_cycles`, mirroring `measure_inf_ensure_window_cycles`'s own
structure; (3) implement `measure_combat_and_materialization_cycles`, reusing `T24.e`'s own
`INF_ROW`/`INF_COL`/`SEED` fixture setup plus `COMBAT_MODE`/`MOB_DATA` injection; (4) build a
small corpus varying `mob_count` (1, the minimum non-empty case, and 6, `MOB_DATA`'s own slot
ceiling — the two ends of the real range, mirroring `T24.e`'s own multi-entry-corpus discipline
rather than a single point measurement) crossed with `proj_active` (0 and 1); (5) run both
measurement functions across the corpus, record min/max against the 70,224-cycle frame budget;
(6) add the `T39` `check(...)` calls recording Met/Not Met honestly (mirroring `T24.e`'s own
`check()` — the check passes if the measurement was successfully *taken*, not if the budget was
met, exactly as `T24.e` already established: an honest `NOT MET` is not a test failure); (7) full
suite run (no other suite should move); (8) documentation updates (§9).

## 8. Tests to Add

New suite **`T39`** (2 checks):

- **`T39.a` — Combat-only frame cycle-count, measured and recorded:** run
  `measure_combat_frame_cycles` across the `(mob_count, proj_active)` corpus; check passes if
  every corpus entry produced a valid measurement (hook fired, not `None`) — records the
  min/max cycle count and Met/Not Met against `FRAME_BUDGET_CYCLES` in the check's own message,
  mirroring `T24.e`'s message-carries-the-verdict convention.
- **`T39.b` — Combat-plus-materialization frame cycle-count, measured and recorded:** same
  structure via `measure_combat_and_materialization_cycles`, corpus crossed with `T24.e`'s own
  3-entry `(seed, row, col)` boundary set (reuse, don't re-derive) to confirm the coinciding case
  is genuinely reachable and measured, not merely asserted reachable.

## 9. Documentation Updates

- `docs/requirements/02-non-functional-requirements.md`: `NFR-1500`'s Status flips from
  `UNCONFIRMED` to **`MET`** or **`NOT MET`** (whichever the measurement honestly shows) with the
  measured cycle range and corpus, Priority line updated to cite this package (mirroring
  `NFR-1400`'s own `IP-1102`/T24.e Status-line precedent exactly). If `NOT MET`, a new backlog
  entry is filed for the follow-up optimization (mirroring `BL-0109`, `NFR-1400`'s own
  successor-finding precedent) — not resolved by this package, only honestly measured.
- `docs/pipeline/backlog.md`: `BL-0168` → resolution note (manager flips status on harvest).
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- Both measurements (combat-only, combat+materialization) taken across their corpora and
  recorded — success is an honest measurement, not a passing budget.
- `NFR-1500`'s Status updated to `MET` or `NOT MET` with the real numbers, mirroring `NFR-1400`.
- ROM builds at exactly 32768 bytes (unchanged — no runtime code added); full suite passes,
  including the two new `T39` checks.
- Diff scope: `test_rom.py` only.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header (byte-identical to the pre-package
      ROM — this package adds no runtime code).
- [ ] G5: full `test_rom.py` suite passes, including `T39.a`/`T39.b`.
- [ ] `T39.a`/`T39.b` both produced valid (non-`None`) measurements across their full corpora —
      a hook that never fires (e.g. a stale/incorrect address) must not silently read as "0
      cycles" or be swallowed; the check fails loudly if any corpus entry returns `None`.
- [ ] `NFR-1500`'s Status line updated with the actual measured range, not a placeholder.
- [ ] Direct diff: no `asm_game.py`/`gbc_lib.py`/`build_rom.py`/`worldgen.py`/`tiles.py`/
      `tilemaps.py`/`music.py` change.
- [ ] If `NOT MET`, a follow-up backlog entry was filed (mirroring `BL-0109`) rather than the gap
      being silently absorbed.

## 12. Dependencies

- **`IP-1120`–`IP-1129`** (all `VERIFIED`) — the routines measured must exist and be stable;
  satisfied.
- **`IP-8010`/`IP-8020`** (refactor packages touching `inf_mob_move`/`inf_mob_contact_check`'s
  own internals, both `VERIFIED` with byte-identical equivalence evidence) — no functional
  impact expected, re-confirmed by task (1) above rather than assumed.

## 13. Risks

Low for the measurement itself (test-only, zero runtime-code risk — mirrors `T24.e`'s own
already-`VERIFIED` technique exactly). The one real risk is scope: if the measurement comes back
`NOT MET`, this package's own Definition of Done is still satisfied (an honest measurement, not
compliance, per `NFR-1500`'s own Postconditions) — the temptation to also *fix* the budget gap
inline must be resisted; that's new scope for a separate, `07`-planned optimization package
(mirroring `NFR-1400`'s own `BL-0109` follow-up), not something this package should absorb.

## 14. Rollback Considerations

Remove the `T39` suite from `test_rom.py`, revert `NFR-1500`'s Status line to `UNCONFIRMED`. No
WRAM, save-format, or interface impact — the routines measured are untouched.
