# VR-9180 — Infinite Mode HUD Target-Digit Convention (`BL-0144`)

## Package

`IP-9180` (commit `b000395`, "fix(hud): IP-9180 -- Infinite Mode HUD shows running treasure count
(BL-0144)"), verified against the current tree head.

## Result

**VERIFIED** — 0 failed checks.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Infinite Mode's HUD col-4 cell shows `RUNNING_TREASURE_COUNT mod 10` once `update_status_disp` has run in Infinite Mode `PLAYING` | Code read: `asm_game.py:1368`-`1382` — `usd_infinite_target` branch reads `RUNNING_TREASURE_COUNT` (`0xC405`), repeated-subtraction mod-10 loop (`usd_it_loop`), adds `TL_DIGIT_0`, writes `0x9804`. Suite `T8.10e`/`T8.10f` PASS (forced `RUNNING_TREASURE_COUNT=7`/`13→3`). **Independently re-derived live** (own standalone script, values disjoint from the suite's own fixture 7/13): forced `RUNNING_TREASURE_COUNT=9` → digit `9`; forced `RUNNING_TREASURE_COUNT=21` → digit `1` (wrap confirmed) | PASS |
| Finite mode's own `WORLD_SCALE` display (`IP-9170`) confirmed unaffected | Code read: the two branches share one `GAME_MODE` test (`JR_NZ`) and are mutually exclusive — `IP-9170`'s branch is untouched by this diff. Suite `T8.10g` PASS. Independent live check: after driving the Infinite Mode branch, switched back to `GAME_MODE=0` with `WORLD_SCALE=4` — digit read `4` exactly | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Build: 32768 bytes, valid header (31390/32768 used). Suite: **330/330 passed, 0 failed** | PASS |
| Diff scope: `asm_game.py` only | `git show b000395 --stat`: `asm_game.py` (+19/-1), docs/ledgers, `test_rom.py`, `test_results.txt`, `BunnyQuest.gbc` — no `tilemaps.py`/`build_rom.py`/`worldgen.py` | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Confirmed this run | PASS |
| G5: full `test_rom.py` suite passes | 330/330 (current tree; 326/326 at the package's own implementation time — the four-check delta is `IP-1125`'s later, separately-authorized `T34` suite) | PASS |
| New Infinite Mode HUD digit check passes at two `RUNNING_TREASURE_COUNT` values incl. one exercising the mod-10 wrap | `T8.10e`(7)/`T8.10f`(13→3) PASS; independently re-verified live at 9 and 21→1, both disjoint from the suite's own fixture values | PASS |
| Finite mode's own `WORLD_SCALE` display confirmed unaffected (regression guard) | `T8.10g` PASS; independent live check above (switched Infinite→finite mid-session, digit read correctly) | PASS |
| Direct diff: no `tilemaps.py`/`build_rom.py`/`worldgen.py` change | Confirmed via `git show b000395 --stat` | PASS |
| Mod-10 reduction confirmed `DIV`/`MUL`-free by direct code read | `asm_game.py:1376`-`1380`: `CP_n(10)`/`JR_C`/`SUB_n(10)`/`JR` loop — no `DIV`/`MUL` instruction anywhere in the branch, mirrors `inf_mod9`'s established technique exactly (bound 10 instead of 9) | PASS |

## Requirements audit

- No FR/NFR directly owns this package per its own §3 (correct — a HUD-cell content convention,
  not new behavior). Companion documentation confirmed present: `FR-9161`'s Notes
  (`01-functional-requirements.md`) carry a second, dated (`IP-9180`/`BL-0144`) clause recording
  the Infinite Mode convention and citing `T8.10e`/`f`/`g` — verified accurate by direct read.

## Test run

- `python3 build_rom.py BunnyQuest.gbc` → 32768 bytes, `Total used: 0x7A9E (31390/32768)`, valid
  header.
- `python3 test_rom.py` → **330/330 passed, 0 failed**.
- Independent standalone PyBoy script: fresh boot → `advance_to_playing` → forced `GAME_MODE=1`,
  `RUNNING_TREASURE_COUNT=9` → digit `9`; `RUNNING_TREASURE_COUNT=21` → digit `1` (confirms the
  mod-10 reduction genuinely wraps, using values the suite's own fixture never exercises);
  switched back to `GAME_MODE=0`, `WORLD_SCALE=4` → digit `4` (finite-mode non-regression,
  independently reproduced). Satisfies this skill's own tunable-parameter rule.

## Scope audit

Commit `b000395` touches exactly: `asm_game.py` (the one declared extension), `test_rom.py`,
`docs/requirements/01-functional-requirements.md`, `00-master-build-plan.md`,
`packages/INDEX.md`, `docs/pipeline/backlog.md`, `BunnyQuest.gbc`, `test_results.txt`. All within
the package's own §6 declared surface (`asm_game.py` only for code). No excursion.

## Findings

None.

## Independence note

Implemented in a prior session (`b000395`, 2026-07-17); this verification runs in a fresh session
with no implementation history for this package — full independence.
