# VR-9090 — Movement Clamp Boundary Fix

> Verification Report for
> [IP-9090](../packages/IP-9090-movement-clamp-boundary-fix.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9090-movement-clamp-boundary-fix.md)

## Package

- **ID / Title:** IP-9090 — Movement Clamp Boundary Fix (`BL-0051`/`BL-0052` remediation, no FS)
- **Commit verified:** tree head `dd3cfe6` (2026-07-12). Implementing commit `0116fb5` ("fix
  (movement): IP-9090 -- correct UP/RIGHT movement clamp boundaries"), authored 2026-07-11 —
  prior to this session.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9090. All 4 Definition of Done items and all 5
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
213/213 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.
The RIGHT ceiling this package establishes (`X=152`) is later reused verbatim by `IP-9120`'s own
`check_zone_transition` threshold correction — confirmed consistent, not contradictory.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | UP clamp floor is exactly `Y=8`; RIGHT clamp ceiling is exactly `X=152` | `asm_game.py:549-554` (UP): `CP_n(8); JR_C('mv_skip_u'); JR_Z('mv_skip_u')` — skips the decrement whenever `Y<=8`, so `Y` never goes below `8`. `asm_game.py:531-535` (RIGHT): `INC_A(); CP_n(153); JR_NC('mv_skip_r')` — skips the write whenever the incremented value would be `>=153`, so the maximum written value is `152` | ✅ |
| 2 | DOWN (`Y=128`... ceiling `129`) and LEFT (`X=0` floor) clamps unchanged | `asm_game.py:557-561` (DOWN): `INC_A(); CP_n(129); JR_NC` — unchanged from the package's own cited pre-fix shape. `asm_game.py:541-543` (LEFT): `OR_A(); JR_Z('mv_nl')` (skip if already `0`) — unchanged | ✅ |
| 3 | `T7.8`/`T7.10`/`T7.10b` demonstrably pass; no other suite regresses | All four checks `[PASS]` (`test_results.txt:72-76`): `T7.8` (`y=8 zone=0`), `T7.8b` (does not go below `8`), `T7.10` (`x=159` forced, no overflow), `T7.10b` (`x=152` via genuine RIGHT-held movement). Full suite 231/231 | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **231/231 pass, 0 failed** this run (current suite size, up from 213/213 at implementation time) | ✅ |
| 3 | Direct code read: UP clamp's magic bound reads `8`, not `17`; RIGHT clamp's comparison reads `CP_n(153)`, not `CP_n(160)` | Confirmed under DoD #1 | ✅ |
| 4 | Direct code read: DOWN/LEFT clamps byte-for-byte unchanged | Confirmed under DoD #2 | ✅ |
| 5 | `T7.8`/`T7.10`/new `T7.10b` present and passing, each exercises the boundary via genuine movement input, not only a forced WRAM value | `T7.8`/`T7.8b` drive real UP-held movement to reach the floor; `T7.10b` explicitly drives genuine RIGHT-held movement (its own check name states "via genuine movement" — `T7.10` itself still forces the WRAM value for its own no-overflow check, per the package's own §6 note that this doesn't need changing) | ✅ |
| 6 | Requirements/RTM deltas applied exactly as §9 names | RTM's `FR-2100` row (`04-requirements-traceability-matrix.md:31`) cites `IP-9090` and `T7.1–T7.7, T7.8/T7.8b/T7.10/T7.10b (boundary-clamp fix)` — accurate and current | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-2100 (continuous fixed-speed movement — boundary-clamp regression fix) | `handle_play_input`'s UP/RIGHT clamp constants (`asm_game.py`) | `T7.8`, `T7.8b`, `T7.10`, `T7.10b` | Cites `IP-9090` and the corrected test list — accurate | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
```

No tunable/generated parameter is named in this package's DoD (a fixed screen-geometry clamp,
independent of `seed`/`scale`) — the non-default-parameter drive rule does not apply.
`T7.8`/`T7.10b` both drive the clamp via genuine button-held movement rather than a forced value,
which is the relevant rigor bar for this package's own claim.

## Scope audit

Every changed symbol traces to exactly the §6-declared files: `asm_game.py` (`handle_play_input`'s
UP/RIGHT clamp constants), `test_rom.py` (`T7.8` corrected in place, `T7.10`'s stale comment fixed,
new `T7.10b`). No excursion beyond the declared set found. The RIGHT ceiling (`X=152`) this
package establishes is consumed downstream by `IP-9120`'s own `check_zone_transition` threshold
correction (already independently verified, `VR-9050`) — confirmed the two values agree exactly,
not merely adjacent.

## Findings

No new findings. `IP-9090`'s core correctness claims (UP floors at exactly `Y=8`, RIGHT ceilings
at exactly `X=152`, DOWN/LEFT unchanged, both boundaries reached via genuine movement input in the
test suite) are each independently confirmed against a fresh 231/231 suite run and direct source
reads — not taken on the Implementation Summary's word.
