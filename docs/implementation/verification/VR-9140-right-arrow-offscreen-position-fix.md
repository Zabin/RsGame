# VR-9140 — Right-Arrow Off-Screen Position Fix

> Verification Report for
> [IP-9140](../packages/IP-9140-right-arrow-offscreen-position-fix.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md)

## Package

- **ID / Title:** IP-9140 — Right-Arrow Off-Screen Position Fix (`BL-0084` remediation, no FS)
- **Commit verified:** tree head `192f2b8` (2026-07-12). Implementing commit `6c42bca` ("fix
  (asm_game): IP-9140 -- right-arrow off-screen position fix (BL-0084)"), authored under
  `session_01XDaz5d1SMBGi8cee1FUu5v` (confirmed via `git log --grep`/commit session trailer, per
  run #100's own independence check) — a different, prior session from this one.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9140. All 4 Definition of Done items and all 6
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
231/231 at the package's own claimed implementation time — this was already the last package to
land, so the suite count is unchanged) against a byte-identical rebuilt ROM. This run independently
re-drove the built ROM in PyBoy and screenshotted the fix's own visible effect.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | `ARROW_ADDR_R` targets tilemap column 18 (visible), not column 30 (off-screen) | `asm_game.py:947`: `ARROW_ADDR_R = 0x9800 + 9*32 + (20-2)` — column 18. `ARROW_ADDR_U`/`D`/`L` (`:944-946`) confirmed already within the visible 0–19/0–17 range by direct calculation, untouched | ✅ |
| 2 | `T13.d` demonstrably passes — all four arrow addresses confirmed within the true visible window | `T13.d` `[PASS]` (`test_results.txt:147`) — "every arrow address falls inside the true visible 20x18 window," `bad=[]` | ✅ |
| 3 | Every existing check touching arrow tiles/positions still passes unchanged | Full suite 231/231 — `T13.a`/`T13.b`/`T13.c` and every `T19`/`T20` check (both independently already `VERIFIED` in `VR-1070`/`VR-1080`) pass in this same run | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **231/231 pass, 0 failed** this run (current suite size, unchanged from implementation time — this package was the last to land in the tree's own history) | ✅ |
| 3 | Direct code read: `ARROW_ADDR_R` reads `0x9800 + 9*32 + (20-2)` (column 18), not the old column 30 | Confirmed under DoD #1 | ✅ |
| 4 | `T13.d` present and passing | Confirmed under DoD #2 | ✅ |
| 5 | Direct PyBoy screenshot re-check (ad hoc, mirroring `BL-0084`'s own reproduction method): a region with a confirmed-open right neighbor visibly shows the right arrow | **Independently re-driven this run**: fresh boot → MAIN MENU → new game → confirmed defaults → PLAYING (`CUR_ZONE=0`) → walked DOWN via real held input → `CUR_ZONE=3` (the exact `BL-0084`-reported sequence: default seed/scale, walk down from region 0 to region 3). Screenshot confirms the right-pointing arrow icon is visibly present at the screen's right edge, mid-height — matching the earlier side-by-side confirmation the implementing session sent the user, independently reproduced by this run | ✅ |
| 6 | `T13.a`/`T13.b`/`T13.c`/every `T19`/`T20` check that touches arrow tiles still passes | Confirmed under DoD #3 | ✅ |
| 7 | Requirements/RTM deltas applied exactly as §9 names | `FR-2320`'s RTM row cites `IP-1030` (base implementation) and `IP-9140` (fix, `BL-0084`) with `T13.a–d` — accurate and current | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-2320 (on-screen transition-edge signaling — right-arrow visibility fix) | `ARROW_ADDR_R`'s corrected column offset (`asm_game.py`) | `T13.d` (this package), `T13.a–c` (base, already independently `VERIFIED`) | Cites `IP-1030` and `IP-9140` with `T13.a–d` — accurate | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
```

**Ad hoc re-drive (this run, live PyBoy):** default seed/scale, walk down from region 0 to region
3 (the literal `BL-0084` reproduction sequence) — screenshot confirms the right arrow now renders
visibly at region 3's own right edge.

## Scope audit

Every changed symbol traces to exactly the §6-declared files: `asm_game.py` (single constant
column-offset change, `ARROW_ADDR_R` only — confirmed by direct grep it has exactly one definition
site and one consumer), `test_rom.py` (new `T13.d`). No excursion beyond the declared set found.
This is the last package (per the tree's own history) to land before this verification sweep, so
the suite's own check count is unchanged from implementation time (231/231 both times) — expected,
not a discrepancy.

## Findings

No new findings. `IP-9140`'s core correctness claim (the right arrow now falls within the true
20×18-tile visible window and renders on-screen, closing a defect that predates this entire
pipeline's own work) is independently confirmed against a fresh 231/231 suite run, direct source
reads, and this run's own live PyBoy screenshot — not taken on the Implementation Summary's word.

**This is the last `COMPLETE` implementation package in the tree — every package now `VERIFIED`.**
