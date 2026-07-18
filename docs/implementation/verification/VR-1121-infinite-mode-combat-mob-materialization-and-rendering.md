# VR-1121 — Infinite Mode Combat: Mob Materialization, Rendering & Defeat

> Produced by `09-package-verification`. Independent of the implementing session
> (commit `e7c829f`, session `018htX7FYYfzxviwtpwy5g9k`) — this pass ran in a
> fresh session with no prior involvement in `IP-1121`'s own implementation.

## Package

- **ID:** [IP-1121](../packages/IP-1121-infinite-mode-combat-mob-materialization-and-rendering.md)
- **Title:** Infinite Mode Combat: Mob Materialization, Rendering & Defeat
- **Commit verified:** `e7c829f` (implementation) on top of tree head at verification time
  (`ef76f7f`, includes `IP-1125`'s own now-`VERIFIED` sprite content)

## Result

**VERIFIED** — 0 failed checks, 0 findings requiring `RETURNED`.

## Definition of Done audit

| DoD item | Evidence | Result |
|---|---|---|
| `inf_materialize_mobs`/`materialize_mobs` produce byte-identical, deterministic output for any `(SEED, row, col)` with `COMBAT_MODE` on | `T29.a` (same-region-twice, byte-identical) + `T29.b` (oracle-vs-SM83 lockstep, 5-tuple corpus incl. negative coordinates, 0 mismatches) both re-run and passing; independently re-derived by direct code read of `inf_materialize_mobs` (`asm_game.py:3047-3092`) against `worldgen.materialize_mobs` (`worldgen.py:318-353`) — same 4-draw-per-slot fixed-length chain, same `AND 0x0F`/`AND 0x07` masks, same `XOR 0x5A` column salt | **PASS** |
| `COMBAT_MODE` off reproduces today's shipped Infinite Mode exactly | `T29.c` re-run and passing; direct code read confirms `inf_materialize_mobs`/`inf_mob_render` both open with `LD_A_nn(COMBAT_MODE); OR_A(); RET_Z()` as their very first instructions — no new code executes before the gate | **PASS** |
| Mob count never exceeds 6; defeat correctly deactivates with no persistent corpse | `T29.d`/`T29.e` re-run and passing; `T29.d` true by construction (exactly 6 candidate slots ever drawn); `T29.e` confirms `inf_mob_defeat` clears the `active` byte, decrements `MOB_COUNT`, and the next `inf_mob_render` call writes a fully zeroed OAM entry for that slot | **PASS** |
| ROM builds at 32768 bytes; full suite passes; OAM budget confirmed within 40 entries | `python3 build_rom.py` → 32768 bytes, header valid, 31646/32768 used (matches the package's own claim); `python3 test_rom.py` → **336/336 passed, 0 failed**; `T29.f` static audit confirms 1+8+6=15 ≤ 40 | **PASS** |

## Verification Checklist audit

- [x] G5: ROM builds at exactly 32768 bytes with valid header. **Confirmed** — rebuilt independently, byte-identical (`cmp`) to the checked-in `BunnyQuest.gbc`.
- [x] G5: full `test_rom.py` suite passes. **Confirmed** — 336/336, 0 failed (fresh PyBoy 2.7.0 install this session).
- [x] T29.a–f each present and passing. **Confirmed** — all six present in `test_rom.py:3780-3889`, all passing.
- [x] Direct code read: `inf_materialize_mobs`'s own presence/type draws are a distinct, sequential `gw_prng_step` call chain from the biome/connectivity/treasure draws — no shared state that would correlate mob presence with either. **Confirmed** — `inf_materialize_mobs` calls `inf_region_seed0` with `INF_COL XOR 0x5A` (asm_game.py:3053), its own independent reseed of `TMP1:TMP2`, distinct from `inf_materialize_region`'s own unsalted reseed for the same `(row,col)`; the two chains provably diverge (T29.b's own corpus, plus the live-drive below, shows mob draws uncorrelated with the region's own biome/treasure state).
- [x] Direct code read: `COMBAT_MODE`-off path never executes any new code this package adds. **Confirmed** — see DoD row 2 above; the `update_oam` control-flow change (`COLL_COUNT==0`'s `RET_Z`→`JR_Z uo_mobs`) still lands on `inf_mob_render`'s own `COMBAT_MODE` gate, so the net behavior when off is unchanged (confirmed: `T29.c`'s own `MOB_DATA`-untouched assertion, plus `T13`/`T20`/`T22`/`T24`/`T25`/`T26`/`T27` all still passing — no COMBAT_MODE-off regression anywhere in the existing Infinite/Finite Mode suites).
- [x] FR-11200/RTM/Master-Build-Plan deltas applied exactly as §9 names. **Confirmed** — see Requirements audit below.

## Requirements audit

| Requirement | Implemented where | Tested where | RTM cell | Result |
|---|---|---|---|---|
| FR-11200 (mob presence, materialization, and non-graphic defeat) | `asm_game.py:3047-3160` (`inf_materialize_mobs`/`inf_mob_render`/`inf_mob_defeat`), `worldgen.py:318-353` (oracle) | `T29.a`-`T29.e` | `04-requirements-traceability-matrix.md:114` → `IP-1121` / `T29.a-f`, status "Implemented — 2026-07-18" | **PASS** |
| FR-11100 (`COMBAT_MODE`-gating half only — flag definition, not the MODE SELECT UI) | `asm_game.py:275-278` (`COMBAT_MODE` WRAM), boot-clear at `asm_game.py:422` | Indirectly, via every `T29` check forcing the flag | RTM row 113 (FR-11100) correctly left `UNASSIGNED` — the package's own §3 scopes only the flag, not the full requirement; `IP-1120`'s own future gating-UI work is what completes FR-11100 | **PASS** (partial-coverage claim matches partial implementation, no over-claim) |

Documentation deltas (§9), each independently re-read from the current tree, not
trusted from the Implementation Summary:

- `docs/requirements/01-functional-requirements.md:2281` — FR-11200 marked "(Implemented — 2026-07-18)". **Confirmed.**
- `docs/requirements/04-requirements-traceability-matrix.md:114` — FR-11200 row → `IP-1121`/`T29.a-f`. **Confirmed.**
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md:21,36,104-133` — implemented-by pointer + Workflow B narrative updated. **Confirmed.**
- `docs/architecture/07-data-model.md:477-494` — `COMBAT_MODE`/`MOB_COUNT`/`MOB_DATA` WRAM rows (`0xC6B5`–`0xC6D4`) added, including the `inf_mob_render`/`COMBAT_MODE`-vs-`MOB_COUNT` gating rationale. **Confirmed.**
- Master Build Plan status row — present, updated by this VR (below).

## Test run

- `python3 build_rom.py <scratch path>` → **32768 bytes written, 31646/32768 used** (header valid). Independently rebuilt binary is **byte-identical** (`cmp`) to the checked-in `BunnyQuest.gbc`, confirming the tree's binary matches its own source.
- `python3 test_rom.py` (fresh `pip install pyboy` this session, PyBoy 2.7.0) → **336/336 passed, 0 failed.**

## Scope audit

Implementing commit `e7c829f` touched exactly: `asm_game.py`, `worldgen.py`,
`test_rom.py`, plus the five documentation files named in §9 (`01-functional-
requirements.md`, `04-requirements-traceability-matrix.md`, `FS-112-...md`,
`07-data-model.md`, `00-master-build-plan.md`), `packages/INDEX.md`,
`test_results.txt`, and the rebuilt `BunnyQuest.gbc`. This matches the
package's own declared file set (§6: `asm_game.py`, `worldgen.py`) exactly —
**no excursion**, no code/content-peer-seam crossing (this is a pure
`08-code-implementation` package; the sprite tiles it references were shipped
separately by `IP-1125`, already `VERIFIED`).

## Independent live drive

Per this skill's own rule on tunable/generated parameters: `inf_materialize_mobs`'s
DoD is stated over "any `(SEED, row, col)`" — a generated-parameter space the
`T29` suite's own fixtures already vary (5-tuple corpus), but this pass drove
the **real production call chain** independently, at a seed/region combination
absent from every existing fixture (`SEED=314159, row=12, col=-7` — none of
`T29`'s own corpus, `T29.c`'s single off-point, or any other suite's fixtures
use this triple):

- Booted the checked-in ROM fresh, forced `GAMESTATE=PLAYING`, `GAME_MODE=1`,
  `SEED`/`INF_ROW`/`INF_COL` to the triple above, `COMBAT_MODE=1`, then called
  **`inf_ensure_window`** directly (the genuine production entry point every
  region transition calls — not `T29`'s own direct-invoke helper for
  `inf_materialize_mobs`).
- Result: `MOB_COUNT=1`, slot 2 active at `(x=136, y=64)` — **byte-for-byte
  identical** to `worldgen.materialize_mobs(314159, 12, -7)`'s own independent
  Python output.
- Then called **`update_oam`** directly (the genuine per-frame shadow-OAM
  builder — not `T29.e`'s own direct-invoke `inf_mob_render` helper): produced
  exactly one non-zero, non-player OAM entry — `Y=80 (64+16), X=144 (136+8),
  tile=10 (TL_MOB), attr=4 (OBJ palette 4)` — matching the slot's own drawn
  position and `inf_mob_render`'s documented encoding exactly.

This confirms the full real call path (`inf_ensure_window` →
`inf_materialize_mobs` → `update_oam` → `inf_mob_render`) end-to-end, at a
parameter combination no existing test or the implementing session's own
live-drive touched, with an independent oracle cross-check.

## Findings

None. No new findings surfaced by this pass; the two pre-existing Low findings
against this package's own dependency (`BL-0149`, `IP-1125` §6 omission) and
this package's own content review (`BL-0150`, mob-placement minimum-separation)
were already filed by prior runs and are `SCHEDULED` — not repeated here.

## Ledger updates applied by this VR

- Master Build Plan: `IP-1121` → `VERIFIED`; `IP-1122`/`IP-1123`/`IP-1120` →
  `READY` (each now has every dependency at `VERIFIED`); `IP-1124` remains
  `NOT STARTED` (still depends on `IP-1122`/`IP-1123`, neither yet built).
- `packages/INDEX.md`: `IP-1121` row status → `VERIFIED`, points at this VR.
- `docs/implementation/verification/INDEX.md`: row added.
