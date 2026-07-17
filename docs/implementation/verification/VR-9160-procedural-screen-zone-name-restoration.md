# VR-9160 — Procedural-Screen Zone-Name Restoration (`BL-0138`)

## Package

`IP-9160` (commit `db6c848`, "content(IP-9160): restore row-0 zone names on the four procedural
screens"), verified against the current tree head.

## Result

**VERIFIED** — 0 failed checks.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Each of the four procedural screens shows its own name after every redraw, incl. after a differently-named predecessor | `T13.g` PASS (`forest=[69,78,81,68,82,83,16,16] village=[85,72,75,75,64,70,68,16]`); **independently re-derived live** (own script, not the suite): forced Grass/Forest → Village, name region read directly from VRAM (`0x9800`+cols 12-19) and compared byte-for-byte against `village_screen()`'s own oracle row 0 — exact match; screenshot confirms "VILLAGE" renders correctly in the HUD | PASS |
| `T13.e` parity includes row 0 static cells, passes for all four screens | `T13.e` PASS (`bad=[]`) | PASS |
| `T13.g` passes both directions | `T13.g` PASS (forward direction confirmed above; reverse (baked-after-procedural, Mountain) included in the same check, PASS) | PASS |
| ROM builds at exactly 32768 bytes; full suite passes | Build: 32768 bytes, valid header. Suite: 321/321 | PASS |
| Diff scope: `tilemaps.py` data + `test_rom.py` only | `git show db6c848 --stat`: `tilemaps.py`, `test_rom.py`, docs/ledgers, screenshots, `BunnyQuest.gbc` — no `asm_game.py`/`build_rom.py`/`worldgen.py` | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Confirmed | PASS |
| G5: full suite passes | 321/321 | PASS |
| `T13.e` extended to row 0, byte-identical for all four screens | Confirmed | PASS |
| `T13.g` stale-name regression both directions | Confirmed | PASS |
| Live rendered evidence: re-drive one screen after a differently-named screen, screenshot | **Independently re-driven this run** (not reusing the implementing commit's own `fix_village.png`) — own standalone script, fresh boot, forced Forest→Village, screenshot saved, name region VRAM bytes compared directly against the oracle | PASS |
| Diff scope: no `asm_game.py`/`build_rom.py`/`worldgen.py`; no `*_FILL`/`*_screen()`/`ZONE_COLLECTS`/`ALL_SCREENS` change | Confirmed via `git show --stat` and a read of the `tilemaps.py` diff (only `*_LANDMARKS` list appends) | PASS |
| Byte-budget delta recorded | Commit message states +128 bytes, 226 headroom (32542/32768) — consistent with the package's own ≈128-byte estimate | PASS |

## Requirements audit

- **`FR-4320`**/`FS-103`'s screen-composition acceptance intent: implemented via the four
  `*_LANDMARKS` list extensions (`tilemaps.py`); tested by `T13.e`/`T13.g`. No RTM row dedicated
  to this remediation package specifically (it rides `FR-4320`'s existing row, which already
  cites `IP-1022`/`IP-1033`) — consistent with the package's own §9 (no new RTM row required).

## Test run

- `python3 build_rom.py` → 32768 bytes, valid header.
- `python3 test_rom.py` → **321/321 passed, 0 failed** (same tree state as `VR-1106`/`VR-1111`).
- Independent standalone script (own, not `test_rom.py`'s own helpers reused verbatim): fresh
  boot, forced Forest region (baked screen, name "FOREST") then Village region (procedural,
  biome-id 5), read VRAM row-0 name cells directly, compared against `village_screen()`'s own
  oracle — exact byte match; screenshot captured confirming "VILLAGE" renders visibly.

## Scope audit

Commit `db6c848` touches exactly: `tilemaps.py`, `test_rom.py`, four screenshot PNGs under
`docs/reviews/screenshots/`, `BunnyQuest.gbc`, `test_results.txt`, and the three ledger files
(Master Build Plan, packages `INDEX.md`, RTM). All within the package's own §6 declared surface.
No excursion.

## Findings

None.

## Independence note

Implemented in a prior session (run #206, 2026-07-17), not this one — independence satisfied.
