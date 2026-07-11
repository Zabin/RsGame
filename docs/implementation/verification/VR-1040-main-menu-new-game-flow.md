# VR-1040 — Main Menu & New-Game Flow

> Verification Report for
> [IP-1040](../packages/IP-1040-main-menu-new-game-flow.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-1040-main-menu-new-game-flow.md) ·
[FS-104](../../features/FS-104-main-menu-new-game-flow.md)

## Package

- **ID / Title:** IP-1040 — Main Menu & New-Game Flow (FS-104 / FEAT-1100, Epic EP-1000,
  Release 2)
- **Commit verified:** `73cea72` ("feat(menu): implement IP-1040 — main menu & new-game flow");
  tree head at verification time includes one further package (`5f58ab5`/IP-1050) layered on top,
  touching disjoint save-format code, plus this session's own unrelated `IP-1031` content commit.
- **Date:** 2026-07-11
- **Independence:** clean — this session's only prior action was implementing `IP-1031` (a
  disjoint content package, zero code overlap with IP-1040); IP-1040 itself was implemented in an
  earlier, separate session (commit `73cea72`, already on the branch before this session began).
  PyBoy 2.7.0 + Pillow already installed earlier this session for `IP-1031`'s own screenshot work.

## Result

**VERIFIED** — 0 failed checks attributable to IP-1040. All 4 Definition of Done items and all 7
Verification Checklist items confirmed with direct evidence; full suite 180/180 pass against a
byte-identical rebuilt ROM (IP-1040's own suite contribution, T14, is 20/20 — see Findings for a
cosmetic check-count note).

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | All six FS-104 Acceptance Criteria demonstrably pass via T13 (renumbered T14) | AC-1/2 (MAIN MENU option-set): `T14.a1–a4`. AC-3/4 (new-game trigger + determinism): `T14.b1–b3`, `T14.c1`. AC-5/6 (exit-to-main-menu, no progress lost): `T14.d0–d2c`. All 20 checks `[PASS]` in `test_results.txt` | ✅ |
| 2 | ROM builds at 32768 bytes; full suite passes | Rebuild: `python3 build_rom.py` → "Wrote 32768 bytes"; `python3 test_rom.py` → **180/180 passed, 0 failed** | ✅ |
| 3 | The auto-load bypass (FR-1120's shipped behavior) no longer exists — boot always reaches MAIN MENU, confirmed by T13.a3 (T14.a3a/b) | Direct read of `asm_game.py`'s boot sequence: `TRANSITION_TO`/`GAMESTATE` set to `GS_MAIN_MENU` unconditionally at boot; exactly one `CALL('try_load_save')` site remains, inside `st_main_menu`'s "continue" branch (`mm_check_a`, MM_CURSOR==0). `T14.a3a` confirms a valid save present still lands at MAIN MENU (GS=6), not auto-loaded PLAYING | ✅ |
| 4 | FR-9110's immutability rule holds against every reachable input sequence (T13.e / T14.e) | `T14.e1` (static audit): `grep`-equivalent scan confirms `SEED`/`WORLD_SCALE` are written only inside `sse_compose_seed`/`try_load_save`, `seed_writes=0 scale_writes=0` elsewhere. `T14.e2` (runtime sweep): every reachable input branch from PLAYING/SAVE/MAP leaves `SEED`/`WORLD_SCALE` unchanged | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Rebuild wrote 32768 bytes; `sha256sum` of the rebuild matches the checked-in `BunnyQuest.gbc` exactly (`878a3500…c042` both) | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **180/180 pass, 0 failed** — run by name this session, exit clean | ✅ |
| 3 | T13.a1–e (T14.a1–e2) each present and passing, mapping 1:1 to FS-104 AC-1…6 plus the FR-9110 negative test | All 20 `T14.*` checks located in `test_results.txt`, all `[PASS]`; each maps to a named AC or the negative-test sweep per FS-104 §16's own Verification Plan | ✅ |
| 4 | Direct code read: `try_load_save`'s call site is now MAIN MENU's "continue" action only — no unconditional call remains anywhere in the boot sequence | `grep -n "CALL('try_load_save')" asm_game.py` → exactly one hit, inside `st_main_menu` (line 330). Boot sequence itself contains no `try_load_save` call, only the unconditional `GS_MAIN_MENU` transition | ✅ |
| 5 | Direct code read: SEED/SCALE ENTRY's B-cancel returns to MAIN MENU without writing SEED/WORLD_SCALE | `st_seed_scale_entry`'s B-branch (`BIT_b_B(J_B); JP_Z('sse_no_b')`) falls straight through to the `GS_MAIN_MENU` transition and `JP('end_frame')` on B-press — no write to `SSE_DIGITS`/`SEED`/`WORLD_SCALE`/`SSE_SCALE` anywhere in that branch. `T14.c1b` confirms empirically (`seed=0 scale=0` after cancel, i.e. unwritten defaults) | ✅ |
| 6 | Direct code read: SAVE's exit-to-main-menu option calls the exact same save-write routine A(save) already calls — no duplicated/divergent save-write logic | `st_save`'s `sv_sel` label (SELECT branch) calls `CALL('save_to_sram')` — byte-identical call to the `A`-branch's own `CALL('save_to_sram')` a few lines above; both invoke the single shared `save_to_sram` label, no second implementation exists | ✅ |
| 7 | GDS-01/FR-1170/1180/1190/RQ-04/Master-Build-Plan deltas applied exactly as §9 names | GDS-01 §2a/3a/4a carries a "confirmed, implemented" note; FR-1170/1180/1190 all read "Implemented — 2026-07-10, `IP-1040`"; RTM rows cite `IP-1040`/`T14.a1–a4` etc.; FS-104 forward-reference metadata states "implemented 2026-07-10... Resolves this document's Open Questions 1–2"; Master Build Plan row (pre-this-run) read `COMPLETE — 163/163 checks pass` | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-1170 (MAIN MENU state) | `st_main_menu`, boot-sequence rewrite (`asm_game.py`); `main_menu_screen()` (`tilemaps.py`) | `T14.a1–a4` | Cites `IP-1040`, `T14.a1–a4` — accurate; count "163/163" is a stale snapshot (suite grew to 180/180 after `IP-1050` added T15) — see Findings | ✅ |
| FR-1180 (new-game seed/scale entry + generation trigger) | `st_seed_scale_entry`, `sse_compose_seed`, call to `IP-1020`'s `generate_world` (`asm_game.py`); `seed_scale_entry_screen()` (`tilemaps.py`) | `T14.b1–b3`, `T14.c1` | Cites `IP-1040`, `T14.b1–b3, T14.c1` — accurate; same stale count | ✅ |
| FR-1190 (exit-to-main-menu with auto-save) | `st_save`'s `sv_sel` branch (`asm_game.py`) | `T14.d1–d2` | Cites `IP-1040`, `T14.d1–d2` — accurate; same stale count | ✅ |

## Test run

```
python3 build_rom.py <verify-path>  → "Wrote 32768 bytes -> <verify-path>"
sha256sum BunnyQuest.gbc <verify-path>
                                    → 878a350012b930aa188bf31775d4a475b06a49f195bcd3777d2f57d221c0422a — identical for both
python3 test_rom.py                → RESULTS: 180/180 passed   0 failed
grep T14 test_results.txt          → 20/20 T14.* checks [PASS]
```

## Scope audit

Implementing commit `73cea72` touched exactly the §6-declared files (`asm_game.py`, `tilemaps.py`,
`build_rom.py`, `test_rom.py`) plus conventional stage-08 build outputs (`BunnyQuest.gbc`,
`test_results.txt`) and exactly the §9-named docs (GDS-01, `01-functional-requirements.md`,
`04-requirements-traceability-matrix.md`, FS-104 metadata, Master Build Plan). No content
(tile/palette) files touched. **No excursions beyond what the package itself named.**

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | RTM's FR-1170/1180/1190 rows and FS-104's forward-reference metadata cite "163/163" as the full-suite count — accurate at IP-1040's own implementation time, now stale since `IP-1050` (implemented after IP-1040, same tranche) added `T15` (17 checks), bringing the current total to 180/180. Same pattern `BL-0028` already named for other packages' snapshot counts. | Low | `04-requirements-engineering` (future delta batch, cosmetic only) |
| 2 | IP-1040's own implementing commit message states "New suite T14 (a–e, 15 checks)"; the actual suite contains 20 checks (`a1,a2,a3a,a3b,a4,b1,b1b,b1c,b2,b3,c1,c1b,d0,d1,d1b,d2a,d2b,d2c,e1,e2`). Cosmetic — the commit message undercounted its own sub-checks (`b1b/b1c`, `c1b`, `d0/d1b` are additional assertions beyond the five top-level letters); every check itself is confirmed passing above. No ledger currently repeats the wrong number, so no correction is required elsewhere. | Low | none — informational only |

No Critical/High findings. IP-1040's core correctness claims (auto-load bypass genuinely retired,
single `try_load_save` call site, B-cancel writes nothing, exit-to-main-menu reuses the exact
save-write routine, FR-9110 immutability holds under a systematic sweep) are each independently
confirmed against a fresh 180/180 suite run and direct source reads — not taken on the
Implementation Summary's word.
