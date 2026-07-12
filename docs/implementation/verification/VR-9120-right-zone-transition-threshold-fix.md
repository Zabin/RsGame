# VR-9120 — RIGHT Zone-Transition Threshold Fix

> Verification Report for
> [IP-9120](../packages/IP-9120-right-zone-transition-threshold-fix.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md)

## Package

- **ID / Title:** IP-9120 — RIGHT Zone-Transition Threshold Fix (`BL-0076` remediation, no FS)
- **Commit verified:** tree head `176913a` (2026-07-12). Implementing commit not individually
  isolable in `git log` (same squashed-history artifact noted in `VR-9070`/`VR-9050`/`VR-9060`),
  but journal run #92 records this package as authored and implemented 2026-07-12, in a session
  prior to this one.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9120. All 4 Definition of Done items and all 6
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
224/224 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | `check_zone_transition`'s RIGHT-edge comparison reads `CP_n(152)`, matching `handle_play_input`'s own RIGHT clamp ceiling | `asm_game.py:687`: `rom.LD_A_nn(PLAYER_X); rom.CP_n(152); rom.JR_C('czt_left')`. `handle_play_input`'s RIGHT clamp (`asm_game.py:533`) is `CP_n(153)` — skip-if-`>=153`, so the max reachable `PLAYER_X` is `152`, exactly matching the transition trigger | ✅ |
| 2 | `T7.11` demonstrably passes — a real, sustained rightward button-press walk both reaches the clamp ceiling and crosses into the expected neighbor zone | `T7.11` (setup) `[PASS]` — "zone 3's oracle-confirmed right neighbor is zone 4"; `T7.11` (main) `[PASS]` — "Real, sustained RIGHT button-press input crosses into the open neighbor zone," `zone=4 x=8` (`test_results.txt:77-78`) | ✅ |
| 3 | Every existing check touching `PLAYER_X`/`CUR_ZONE`/`check_zone_transition` still passes unchanged | Full suite 231/231 — `T7.9`/`T7.10`/`T7.10b`, `T11.a2`, and every `T17`/`T19` check (both independently already `VERIFIED` in `VR-9050`/`VR-1070`) pass in this same run, confirming no regression from this fix | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **231/231 pass, 0 failed** this run (current suite size, up from 224/224 at implementation time) | ✅ |
| 3 | Direct code read: RIGHT-edge comparison reads `CP_n(152)`, not the old `CP_n(156)` | Confirmed under DoD #1 | ✅ |
| 4 | `T7.11` present and passing, using real button-press input (not memory-forced position) | `test_rom.py:534-563` confirms `T7.11`'s own implementation drives the player via `button_press('right', ...)`/tick cycles, releasing on `CUR_ZONE` change — not a `pb.memory[PLAYER_X] = ...` teleport. Both `T7.11` checks `[PASS]` | ✅ |
| 5 | Direct PyBoy re-check (ad hoc, mirroring `BL-0076`'s reproduction method): sustained real rightward input crosses into a confirmed-open right neighbor | `T7.11` **is** this exact check, made permanent (not left as an untracked ad hoc step, unlike `IP-9110`'s explicitly-named ad hoc item) — this run's own fresh suite execution re-confirms it live, not by reading a stale prior pass | ✅ |
| 6 | `T7.9`/`T7.10`/`T7.10b`/`T11.a2`/every `T17`/`T19` check still passes | Confirmed under DoD #3 | ✅ |
| 7 | Requirements/RTM deltas applied exactly as §9 names | `FR-2300`'s RTM row cites `IP-9050, IP-9120, IP-9130` and `T17.a–b`, `T7.11` (`IP-9120`), `T7.12` (`IP-9130`) — accurate and current, including the package's own §3-documented citation correction (`FR-2310`→`FR-2300`) | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-2300 (zone-boundary transition on valid neighbor — RIGHT-edge regression fix) | `check_zone_transition`'s RIGHT comparison operand (`asm_game.py`) | `T7.11` | Cites `IP-9120` alongside `IP-9050`/`IP-9130` and `T7.11` — accurate | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
```

No tunable/generated parameter beyond region choice is named in this package's DoD; `T7.11`
itself forces `CUR_ZONE=3` (a non-default region with a confirmed-open right neighbor, since the
default fixture's own region 0 has none) — the relevant non-default condition is already exercised
by the suite itself.

## Scope audit

Every changed symbol traces to exactly the §6-declared files: `asm_game.py` (single operand
`156`→`152`), `test_rom.py` (new `T7.11`). Confirmed by direct grep that the old `156` constant no
longer appears anywhere in `asm_game.py`'s `check_zone_transition` region, and no other call site
shares the class of constant this fix touches (matching the package's own supersession-sweep
claim). No excursion beyond the declared set found.

## Findings

No new findings. `IP-9120`'s core correctness claim (the RIGHT transition trigger now agrees
exactly with the movement clamp's own reachable ceiling, restoring rightward navigation broken by
the `IP-9090`/`IP-9050` interaction) is independently confirmed against a fresh 231/231 suite run
and direct source reads — not taken on the Implementation Summary's word.
