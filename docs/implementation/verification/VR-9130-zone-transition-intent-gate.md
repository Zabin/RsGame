# VR-9130 — Zone-Transition Intent Gate

> Verification Report for
> [IP-9130](../packages/IP-9130-zone-transition-intent-gate.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md)

## Package

- **ID / Title:** IP-9130 — Zone-Transition Intent Gate (`BL-0078` remediation, no FS)
- **Commit verified:** tree head `7e549f4` (2026-07-12). Journal run #93 records this package as
  authored and implemented 2026-07-12 via a session-external PR (PR #16, per run #94's own drift
  note) — prior to this session in either case.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9130. All 4 Definition of Done items and all 6
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
226/226 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | All four `check_zone_transition` branches require the matching `JOY_CUR` direction bit held, in addition to the existing position/neighbor test | `asm_game.py:686` (RIGHT): `LD_A_nn(JOY_CUR); BIT_b_A(J_RIGHT); JR_Z('czt_left')` before the position test. `:696` (LEFT): same pattern, `J_LEFT`, `JR_Z('czt_top')`. `:706` (UP): same, `J_UP`, `JR_Z('czt_bot')`. `:716` (DOWN): same, `J_DOWN`, `RET_Z()` (the routine's last branch, no fallthrough label). All four confirmed by direct read, gating strictly *before* their own existing position test | ✅ |
| 2 | `T7.12` demonstrably passes — a real, sustained right-then-down walk no longer produces a spurious follow-on transition | `T7.12` (setup) `[PASS]` — "RIGHT walk in region 0 stays blocked," `zone=0 x=152`; `T7.12` (main) `[PASS]` — "No spurious follow-on transition after a perpendicular approach," `zone=3` (`test_results.txt:79-80`) — the exact `BL-0078` reproduction sequence | ✅ |
| 3 | Every existing check touching `PLAYER_X`/`PLAYER_Y`/`CUR_ZONE`/`check_zone_transition` still passes | Full suite 231/231 — `T7.9`–`T7.11`, `T16.*`, `T17.a`/`b2`/`b5`/`c1`/`c2`, `T19.*` all pass in this same run (several of these already independently `VERIFIED` in `VR-9070`/`VR-9050`/`VR-9120`/`VR-1070`) | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **231/231 pass, 0 failed** this run (current suite size, up from 226/226 at implementation time) | ✅ |
| 3 | Direct code read: all four branches gate on the matching `JOY_CUR` bit before their position test | Confirmed under DoD #1 | ✅ |
| 4 | `T7.12` present and passing, using real button-press input | Confirmed under DoD #2 — `test_rom.py:567-589` drives real `button_press('right')`/`button_press('down')`, not a memory-forced position alone | ✅ |
| 5 | Direct PyBoy re-check (ad hoc, mirroring `BL-0078`'s reproduction): right-then-down produces no spurious transition, at the literal reported scenario | `T7.12` **is** this exact check, made permanent — this run's own fresh suite execution re-confirms it live (region 0→3, the literal default-fixture reproduction) | ✅ |
| 6 | `T7.9`–`T7.11`, `T16`, `T17.a`/`b2`/`b5`, `T17.c1`/`c2`, `T19.*` all still pass | Confirmed under DoD #3. Also confirmed `T11.a2` and `_t17_do_move` (the two sites the supersession sweep named) both now hold real buttons around their teleport windows (`test_rom.py:793-802`, `:1659-1685`), matching §6's own specified fix — not left un-updated | ✅ |
| 7 | Requirements/RTM deltas applied exactly as §9 names | `FR-2300`'s RTM row cites `IP-9050, IP-9120, IP-9130` and `T7.12` (`IP-9130`) alongside `T7.11` (`IP-9120`) — accurate and current | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-2300 (zone-boundary transition on valid neighbor — perpendicular-approach regression fix) | `check_zone_transition`'s four `JOY_CUR` gates (`asm_game.py`) | `T7.12` | Cites `IP-9130` alongside `IP-9050`/`IP-9120` and `T7.12` — accurate | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
```

No tunable/generated parameter beyond region/direction choice is named in this package's DoD;
`T7.12` itself reuses `T7.11`'s own non-default region setup (region 0→3, a region with a
confirmed grid-adjacent-but-not-necessarily-open neighbor structure) — the relevant condition is
already exercised.

## Scope audit

Every changed symbol traces to exactly the §6-declared files: `asm_game.py` (four `BIT`-test gate
insertions, no other line changed in `check_zone_transition`), `test_rom.py` (`T11.a2` and
`_t17_do_move` updated to hold real buttons, new `T7.12`). Confirmed by direct read that exactly
these two pre-existing sites needed updating (matching the package's own supersession-sweep
claim) — no other call site silently left un-updated. No excursion beyond the declared set found.

## Findings

No new findings. `IP-9130`'s core correctness claim (all four zone-transition branches now
require genuine directional intent, not merely a coincidental boundary position, closing the
spurious-transition gap the maze pass's per-region open/blocked variation exposed) is
independently confirmed against a fresh 231/231 suite run and direct source reads — not taken on
the Implementation Summary's word.
