# VR-1128 — Infinite Mode Combat: Weapon Directionality

> Independent verification of [`IP-1128`](../packages/IP-1128-infinite-mode-combat-weapon-directionality.md)
> against the shipped tree. Produced by `09-package-verification`.

## Package

- **ID:** `IP-1128` — Infinite Mode Combat: Weapon Directionality
- **Implementing commit:** `2357d61` ("feat(combat): IP-1128 — 8-directional weapon fire
  (FR-11310)", 2026-07-19)
- **Commit verified at:** `7f8e973` (tree head at verification time; unrelated `IP-1123`/`IP-1126`
  verification and journal commits landed afterward, none touching this package's own files)
- **Independence:** fresh session; no prior work on `IP-1128` performed in this session.

## Result

**VERIFIED** — 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Firing produces a projectile moving in the correct direction for all eight compass directions, including simultaneous both-axis motion for diagonals | `handle_play_input`'s fire branch (lines 1100-1103) copies `PLAYER_FACING_X`/`Y` → `PROJ_STEP_X`/`Y`; `inf_projectile_update` (lines ~3564+) adds both steps to `PROJ_X`/`PROJ_Y` independently, unconditionally (no branch on step value). `T37.a`-`d` pass | Pass |
| Firing while stationary uses the last-held direction, not a fixed default; a fresh, never-moved session still fires rightward | `PLAYER_FACING_X`/`Y` are written only inside `handle_play_input`'s RIGHT/LEFT/UP/DOWN branches (mirrors `PLAYER_DIR`'s own "only written on press" convention) — confirmed by direct read, no reset-to-neutral code path exists. Boot-init sets `PLAYER_FACING_X=1`/`Y=0` (lines ~517-519). `T37.e`/`f` pass | Pass |
| Y-axis boundary termination works correctly, mirroring the existing X-axis behavior | `inf_projectile_update`'s new Y-check: `CP_n(8); JR_C(deactivate)` then `CP_n(129); JR_NC(deactivate)`, reusing `PLAYER_Y`'s own established 8/129 clamp pair (confirmed identical to `handle_play_input`'s own UP/DOWN clamp constants at lines 1132-1145). `T37.g` passes | Pass |
| Hit resolution is confirmed axis-agnostic for a diagonal projectile, not merely assumed | `inf_projectile_hittest` confirmed **byte-for-byte untouched** by this commit (its own label body does not appear anywhere in the commit's diff — only comments elsewhere reference it); `T37.h` independently exercises a diagonal hit and passes | Pass |
| ROM builds at 32768 bytes; full suite passes, including the corrected `T30.b`; `inf_projectile_hittest` confirmed byte-for-byte unchanged by direct diff | Confirmed (see Test run and Scope audit) | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes, valid header | Confirmed: `python3 build_rom.py` → "Wrote 32768 bytes → BunnyQuest.gbc" | Pass |
| G5: full `test_rom.py` suite passes | 387/387 passed, 0 failed (fresh session) | Pass |
| `T37.a`–`i` each present and passing; `T30.b` corrected and passing under the new encoding | All 9 `T37` checks confirmed present and passing; `T30.a`/`b`/`c`/`c2`/`d` diff-inspected — `T30.a` now asserts `dir==0xFF` for a leftward fire (was `dir==1` under the old 2-value encoding), `T30.b` asserts `PROJ_STEP_X_ADDR==0` unchanged across a no-op double-fire attempt — both legitimate re-encodings, not weakened assertions; all pass | Pass |
| Direct code read: `inf_projectile_hittest` unmodified by this package's own diff | Confirmed — `git show 2357d61 -- asm_game.py` contains no hunk touching `inf_projectile_hittest`'s own label range (`rom.label('inf_projectile_hittest')` at line 3619, well outside every changed hunk) | Pass |
| Direct code read: `PLAYER_DIR` unmodified — no widening, no new consumer added | Confirmed — `PLAYER_DIR`'s own two write sites (`mv_skip_r`'s `XOR_A`, the LEFT branch's `LD_A_n(1)`) are byte-for-byte unchanged in the diff; the new `PLAYER_FACING_X`/`Y` writes sit alongside them as pure additions, not replacements | Pass |
| FR-11310/RTM/Master-Build-Plan/`packages/INDEX.md`/`GDS-07` deltas applied exactly as §9 names | `FR-11310` → "Implemented `IP-1128` 2026-07-19"; RTM row `FR-11310 \| ... \| IP-1128 \| T37.a–i`; `GDS-07` (`07-data-model.md`) §7n added with the full `PLAYER_FACING_X`/`Y`/`PROJ_STEP_X`/`Y` byte table and `ADR-0021` Decision 1 rationale; Master Build Plan/`packages/INDEX.md` rows present and accurate | Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell | Result |
|---|---|---|---|---|
| FR-11310 | `PLAYER_FACING_X`/`Y`, `PROJ_STEP_X`/`Y`, `handle_play_input`'s four movement branches, `inf_projectile_update` | `T37.a`-`i` (+ corrected `T30.a`/`b`) | `FR-11310 \| ... \| ADR-0021 \| asm_game.py \| FS-112 \| IP-1128 \| T37.a–i` | Pass |

## Test run

- `python3 build_rom.py` → 32768 bytes written (32414 used).
- `python3 test_rom.py` → **387/387 passed, 0 failed** (fresh session).
- `T37.a`-`i` individually confirmed present and passing (9/9); `T30.a`/`b`/`c`/`c2`/`d`
  confirmed passing under the corrected encoding.

## Scope audit

Implementing commit `2357d61` touched `asm_game.py` (WRAM constants, `handle_play_input`'s four
movement branches + fire branch, `inf_projectile_update`'s restructure — `PROJ_DIR`→`PROJ_STEP_X`
rename+redefinition, the one intentionally non-additive change this package makes), `test_rom.py`
(new `T37` suite + the pre-named `T30.a`/`b`/`c`/`c2`/`d` corrections), and the doc files named in
§9 plus standard build/test artifacts. No excursion beyond the package's own declared scope.
`inf_projectile_hittest`, `PLAYER_DIR`'s own write sites, and `MOB_DATA`/`inf_mob_move` (`IP-1126`,
unrelated) all confirmed untouched by direct diff inspection.

## Independent live drive

`T37.i` (already part of the reconfirmed suite) independently live-drives the real production
per-frame chain — real diagonal D-pad input, real fire, real `inf_projectile_update` ticks — and
confirms the projectile's recorded position moves diagonally over several real ticks, matching
`T35.i`'s established discipline. This is not a `BL-0055`-class runtime-tunable-parameter package
(the eight directions are exhaustively enumerated by `T37.d`'s own corpus, not sampled from a
single fixture default), so no additional non-default-value live drive was owed beyond `T37.i`.
The dominant-axis-independent-of-render logic (`inf_projectile_hittest` unchanged, confirmed
axis-agnostic by `T37.h`) and the underflow/overflow boundary arithmetic (`ADD_A_E` then unsigned
`CP_n` catching both directions of X overflow with one check) were both independently re-derived
from the assembly during the Definition-of-Done audit above, not taken from the Implementation
Summary's own description.

## Findings

None.

## Ledger status

Per this skill's own rule, `IP-1128` advances `COMPLETE → VERIFIED` on the Master Build Plan and
`packages/INDEX.md`. No dependent package names `IP-1128` as a dependency, so no other package's
readiness changes as a result of this verification. `IP-1128`'s own real WRAM claim
(`0xC6DF`–`0xC6E1`) remains the binding one against `IP-1127`'s still-stale prospective claim of
the same range (unchanged by this verification — a planning-time note, not something this run
resolves).
