# VR-1050 — Generated-World Save Persistence

> Verification Report for
> [IP-1050](../packages/IP-1050-generated-world-save-persistence.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-1050-generated-world-save-persistence.md) ·
[FS-105](../../features/FS-105-generated-world-save-persistence.md)

## Package

- **ID / Title:** IP-1050 — Generated-World Save Persistence (FS-105 / FEAT-5300, Epic EP-3000,
  Release 2)
- **Commit verified:** `5f58ab5` ("feat(save): implement IP-1050 — generated-world save
  persistence"); tree head at verification time additionally includes this session's own
  `IP-1031` content commit (disjoint files, zero overlap).
- **Date:** 2026-07-11
- **Independence:** clean — IP-1050 was implemented in an earlier, separate session (commit
  `5f58ab5`, already on the branch before this session began). This session's own work
  (`IP-1031` content, `IP-1040` verification) touches disjoint files (`tilemaps.py` content
  registration and verification-only reads, respectively) — no implementation overlap with
  IP-1050's `asm_game.py` save/load extension.

## Result

**VERIFIED** — 0 failed checks attributable to IP-1050. All 4 Definition of Done items and all 7
Verification Checklist items confirmed with direct evidence; full suite 180/180 pass against a
byte-identical rebuilt ROM (IP-1050's own suite contribution, T15, is 17/17 — matching its
implementing commit's own "17 checks" claim exactly, no undercount this time).

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | Both FS-105 Acceptance Criteria demonstrably pass via T14 (renumbered T15) | AC-1 (round-trip): `T15.a0–a6` — SEED/WORLD_SCALE/KeyItemFlags round-trip exactly, regenerated region graph matches pre-save graph. AC-2 (pre-upgrade rejection): `T15.b1–b3` — a version-1 (`IP-1010`-vintage) save is never offered on "continue," new-game still reaches PLAYING cleanly. All 17 `T15.*` checks `[PASS]` | ✅ |
| 2 | ROM builds at 32768 bytes; full suite passes | Rebuild: `python3 build_rom.py` → "Wrote 32768 bytes"; `python3 test_rom.py` → **180/180 passed, 0 failed** | ✅ |
| 3 | Old-format saves (version `0x01`) are never offered on "continue," never partially loaded with garbage seed/scale/region-flags bytes | `check_save_valid` (`asm_game.py`) gates `MM_SAVE_VALID` on `SAVE_VERSION_ADDR == SAVE_VERSION_VAL` (`0x02`) — a version-1 save fails this check, so MAIN MENU never renders "continue" for it (confirmed `T15.b1`/`b2`). `try_load_save`'s own version-guarded restore branch (`tls_si_skip`) is a defensive fallback only reachable if `try_load_save` were called directly on a mismatched save — not a live path since `IP-1040`'s `check_save_valid` gates upstream (confirmed by direct code read + inline comment) | ✅ |
| 4 | The region graph itself is never written to SRAM — confirmed by direct diff of the save-write routine's field list | Direct read of `save_to_sram`: writes exactly `CUR_ZONE`/`PLAYER_X`/`PLAYER_Y`/`CARROTS_COUNT`(KeyItemCount)/`SCORE`/9×`CARROT_FLAGS`(KEYITEM_FLAGS)/version byte/9×`SCOREITEM_FLAGS`/`SEED`(2B)/`WORLD_SCALE`(1B)/`KEYITEM_FLAGS`(81B via `memcpy`) — no `REGION_GRAPH` reference anywhere in the routine. `T15.d` confirms empirically (direct static scan) | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Rebuild wrote 32768 bytes; `sha256sum` of the rebuild matches the checked-in `BunnyQuest.gbc` exactly (`878a3500…c042` both) | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **180/180 pass, 0 failed** — run by name this session, exit clean | ✅ |
| 3 | T14.a–c (T15.a–d) each present and passing, mapping 1:1 to FS-105 AC-1/AC-2 plus the legacy-field regression | All 17 `T15.*` checks located in `test_results.txt`, all `[PASS]`; `a0–a6` (AC-1 round-trip), `b1–b3` (AC-2 pre-upgrade rejection), `c1–c6` (legacy-field regression: `CUR_ZONE`/position/`KeyItemCount`/`SCORE`/`KEYITEM_FLAGS`/`SCOREITEM_FLAGS`), `d` (REGION_GRAPH never in SRAM) | ✅ |
| 4 | Direct code read: save/load extensions sit inside the existing single MBC1 enable/disable bracket (NFR-5100 unchanged — no second bracket) | `save_to_sram`: single `LD_A_n(0x0A); LD_nn_A(0x0000)` (enable) at entry, single `XOR_A(); LD_nn_A(0x0000)` (disable) at exit, with the new SEED/WORLD_SCALE/KEYITEM_FLAGS writes (including the `memcpy` call) between them. `try_load_save`: identical single-bracket shape, with the new restore block (including the `CALL('generate_world')`) between the same enable/disable pair. No second bracket introduced in either routine | ✅ |
| 5 | Direct code read: `try_load_save`'s version check gates the new fields' restore path exactly, without altering the legacy fields' own unconditional load | Legacy fields (`CUR_ZONE`/`PLAYER_X`/`PLAYER_Y`/`CARROTS_COUNT`/`SCORE`/9×`CARROT_FLAGS`) load unconditionally, before the version check. `SAVE_VERSION_ADDR` vs `SAVE_VERSION_VAL` comparison (`JR_NZ('tls_si_skip')`) gates only the block that follows: `SCOREITEM_FLAGS` restore, `SEED`/`WORLD_SCALE` restore, `generate_world` call, `KEYITEM_FLAGS` restore — exactly the fields this package (and `IP-1010` before it) added | ✅ |
| 6 | Direct code read: `REGION_GRAPH` is never written to SRAM by `save_to_sram` — only `SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS` | Confirmed under DoD #4 above — same evidence, no `REGION_GRAPH` write in `save_to_sram`'s body | ✅ |
| 7 | BL-0019/NFR-4200 rider: SRAM headroom re-affirmed (~84 bytes new, against 8 KiB) | New SRAM range `0xA01C`–`0xA06F` (84 bytes: 2 SEED + 1 WORLD_SCALE + 81 KEYITEM_FLAGS) confirmed by the constant definitions (`asm_game.py` lines 77–79); well within the existing 8 KiB MBC1 SRAM bank, no overflow risk, no new package required to re-check this | ✅ |
| 8 | GDS-07/NFR-5300/RQ-04/Master-Build-Plan deltas applied exactly as §9 names | GDS-07 delta §7 confirms the addresses as-shipped; NFR-5300 → **Met**, NFR-5200's field set widened a second time (post-`IP-1010`); RTM's FR-9200/NFR-5300 rows cite `IP-1050`/`T15.*`/180/180 (already current, no staleness — this package landed last of the tranche's three parallel packages); FS-105 forward-reference metadata states "implemented 2026-07-10... T15 suite (180/180)"; Master Build Plan row (pre-this-run) read `COMPLETE — 180/180 checks pass` | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-9200 (save-format extension: seed/scale/keyitem-flags) | `SRAM_SEED`/`SRAM_WORLD_SCALE`/`SRAM_KEYITEM_FLAGS` constants, `save_to_sram`/`try_load_save` extensions (`asm_game.py`) | `T15.a1–a6`, `T15.c1–c6`, `T15.d` | Cites `IP-1050`, `T15.a1–a6, T15.c1–c6, T15.d` — 180/180, already accurate | ✅ |
| NFR-5300 (save-format version bump, pre-upgrade rejection) | `SAVE_VERSION_VAL` bumped `0x01`→`0x02`; `check_save_valid`/`try_load_save`'s version-guard branches | `T15.b1–b3` | Cites `IP-1050`, `T15.b1/b2/b3` — 180/180, already accurate | ✅ |

## Test run

```
python3 build_rom.py <verify-path>  → "Wrote 32768 bytes -> <verify-path>"
sha256sum BunnyQuest.gbc <verify-path>
                                    → 878a350012b930aa188bf31775d4a475b06a49f195bcd3777d2f57d221c0422a — identical for both
python3 test_rom.py                → RESULTS: 180/180 passed   0 failed
grep -c T15 test_results.txt       → 17 (matches the implementing commit's own "17 checks" claim exactly)
```

## Scope audit

Implementing commit `5f58ab5` touched exactly the §6-declared files (`asm_game.py`,
`test_rom.py`) plus conventional stage-08 build outputs (`BunnyQuest.gbc`, `test_results.txt`)
and exactly the §9-named docs (GDS-07, `02-non-functional-requirements.md`,
`04-requirements-traceability-matrix.md`, FS-105 metadata, Master Build Plan). No `tilemaps.py`
or content-file changes — matches this package's code-only scope. **No excursions beyond what
the package itself named.**

## Findings

No new findings. IP-1050's RTM/FS-105 evidence counts were already accurate at "180/180" (this
package landed last among the tranche's three parallel packages, `IP-1030`/`1040`/`1050`, so no
subsequent package's test additions left its own citations stale — unlike `IP-1040`, corrected
under `VR-1040`).

No Critical/High findings. IP-1050's core correctness claims (single MBC1 bracket preserved,
version-guard gates only the new fields, `REGION_GRAPH` never persisted, legacy fields still
round-trip, pre-upgrade saves cleanly rejected) are each independently confirmed against a fresh
180/180 suite run and direct source reads — not taken on the Implementation Summary's word.
