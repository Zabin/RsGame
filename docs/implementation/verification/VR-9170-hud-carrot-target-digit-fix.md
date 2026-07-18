# VR-9170 — HUD Carrot-Target Digit Fix (`BL-0139`)

## Package

`IP-9170` (commit `4e51aa9`, "fix(hud): IP-9170 -- carrot-target digit tracks WORLD_SCALE
(BL-0139)"), verified against the current tree head (`b6b21d0`).

## Result

**VERIFIED** — 0 failed checks.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Every finite-mode world, at any `WORLD_SCALE` 2-9, shows its own actual scale in the HUD's target digit (row 0, col 4) after `update_status_disp` runs in `PLAYING` | Code read: `asm_game.py:1363`-`1366` — `GAME_MODE`-gated branch reads `WORLD_SCALE`, adds `TL_DIGIT_0`, writes `0x9804`. Suite `T8.10c`/`T8.10d` PASS (forced `WORLD_SCALE=5`/`7`). **Independently re-derived live** (own standalone script, not the suite's fixture): fresh boot → `advance_to_playing`, default digit at boot-time `WORLD_SCALE=3` reads `3`; forced `WORLD_SCALE=6` → digit `6`; forced `WORLD_SCALE=8` → digit `8` — both non-default, non-corpus-default values, matching exactly | PASS |
| Infinite Mode's own col-4 cell confirmed byte-for-byte unaffected by this package | Code read: the `GAME_MODE!=0` path jumps straight to `usd_infinite_target` (IP-9180's own branch, added the same day) — `IP-9170` itself contributes zero Infinite Mode logic. Suite `T8.10e`/`T8.10g` PASS. Independent live check: switching `GAME_MODE=1` after the finite-mode digit was `8` changed the digit to `0` — this is `IP-9180`'s own `RUNNING_TREASURE_COUNT`-mod-10 branch reading its default `0`, not `IP-9170`'s finite branch leaking through (confirmed by code read: the two branches are mutually exclusive via `JR_NZ`) | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Build: 32768 bytes, valid header (`Total used: 0x7A9E (31390 bytes of 32768)`). Suite: **330/330 passed, 0 failed** (current tree, includes `IP-9180`/`IP-1125` work landed since this package shipped) | PASS |
| Diff scope: `asm_game.py` only (one routine, one inserted conditional write) | `git show 4e51aa9 --stat`: `asm_game.py` (+13), `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, `docs/requirements/01-functional-requirements.md`, `docs/requirements/04-requirements-traceability-matrix.md`, `test_rom.py`, `test_results.txt`, `BunnyQuest.gbc` — no `tilemaps.py`/`build_rom.py`/`worldgen.py` change | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Confirmed this run | PASS |
| G5: full `test_rom.py` suite passes | 330/330 (current tree; 324/324 at the package's own implementation time — the six-check delta is unrelated later work, `IP-9180`+`IP-1125`) | PASS |
| New HUD target-digit check passes for at least two non-default, non-corpus-default `WORLD_SCALE` values | `T8.10c`(5)/`T8.10d`(7) PASS; independently re-verified live at 6 and 8 | PASS |
| New Infinite Mode non-regression check confirms col 4 untouched there | `T8.10g` PASS; independent live check above confirms the branch split is real, not coincidental | PASS |
| Direct diff: no `tilemaps.py`/`build_rom.py`/`worldgen.py` change; `update_status_disp`'s only change is the one inserted `GAME_MODE`-gated write | Confirmed via `git show 4e51aa9` and direct read of `asm_game.py:1355`-`1366` — exactly the claimed insertion (plus `IP-9180`'s own later, separately-authorized extension of the same branch point, not this package's scope) | PASS |
| Byte-budget delta recorded | Package's own claim: "a handful of instruction bytes, no data-section growth." ROM stayed at 31390/32768 used both then and now (fit inside existing alignment slack) | PASS |

## Requirements audit

- **`FR-9161`** (scale-relative victory condition, `IP-1021`): this package's own Documentation
  Updates extended `FR-9161`'s Notes (`01-functional-requirements.md`) to record the HUD-alignment
  fix, and the RTM row (`04-requirements-traceability-matrix.md`) now lists `IP-9170` alongside
  `IP-1021` and cites `T8.10c`/`T8.10d`. Confirmed both edits are present and accurate by direct
  read — traces to real code (`asm_game.py:1363`-`1366`) and real checks (`T8.10c`/`T8.10d`).
- No FR/NFR directly owns this package per its own §3 (correctly stated — a rendered-content
  correctness fix against an already-shipped mechanic, not new behavior).

## Test run

- `python3 build_rom.py BunnyQuest.gbc` → 32768 bytes written, `Total used: 0x7A9E (31390 bytes of
  32768)`, valid header.
- `python3 test_rom.py` → **330/330 passed, 0 failed** (includes `T8.10c`/`d`/`e`/`f`/`g`, all
  PASS).
- Independent standalone PyBoy script (own script, not reusing `test_rom.py`'s in-process state):
  fresh boot → `advance_to_playing` → confirmed `GAMESTATE==GS_PLAYING`, boot-default digit `3`
  (matches default `WORLD_SCALE=3`) → forced `WORLD_SCALE=6` → digit `6` → forced `WORLD_SCALE=8`
  → digit `8` → forced `GAME_MODE=1` → digit dropped to `0` (Infinite Mode's own independent
  branch, `IP-9180`, reading its own default `RUNNING_TREASURE_COUNT=0` — not a finite-mode leak).
  Satisfies this skill's own tunable-parameter rule: the suite's default fixture never varies
  `WORLD_SCALE` from `3` on its own, so this run drove the ROM at genuinely different values
  itself rather than trusting the suite's existing coverage.

## Scope audit

Commit `4e51aa9` touches exactly: `asm_game.py` (the one declared routine), `test_rom.py` (new
checks, package's own §8), `docs/requirements/01-functional-requirements.md` +
`04-requirements-traceability-matrix.md` (package's own §9 documentation updates),
`00-master-build-plan.md` + `packages/INDEX.md` (ledger status), `BunnyQuest.gbc`,
`test_results.txt`. All within the package's own §6 declared surface. No excursion.

## Findings

None.

## Independence note

Implemented in a prior session (`4e51aa9`, 2026-07-17); this verification runs in a fresh session
with no implementation history for this package — full independence.
