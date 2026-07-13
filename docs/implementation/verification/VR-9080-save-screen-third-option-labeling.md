# VR-9080 — SAVE Screen Third-Option Labeling

> Verification Report for
> [IP-9080](../packages/IP-9080-save-screen-third-option-labeling.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9080-save-screen-third-option-labeling.md)

## Package

- **ID / Title:** IP-9080 — SAVE Screen Third-Option Labeling (`BL-0049` remediation, no FS)
- **Commit verified:** tree head `c8fbd1d` (2026-07-12). Implementing commit `7298fca`
  ("content(save-screen): IP-9080 -- label the silent third option"), authored 2026-07-11 — prior
  to this session.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session. No prior `09-content-review` exists
  for this package (unlike `IP-1031`), so this run performed its own independent PyBoy re-drive
  rather than relying on a separate qualitative review.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9080. All 3 Definition of Done items and all 6
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
220/220 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.
Independently re-drove the SAVE screen in PyBoy and visually confirmed the label.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | The SAVE screen's third (`SELECT`) option has on-screen text unambiguously describing "save and exit," within the existing bordered layout, not overlapping the existing two lines | `tilemaps.py:312-313`: `_str(t, a, 5, 12, "SELECT: SAVE", 2)` / `_str(t, a, 5, 13, "AND EXIT", 2)` — two lines at rows 12–13, columns 5–16/5–12, below `"B: NO"` (row 11) and above the bottom border (row 14). **Independently re-driven via PyBoy** (fresh boot → MAIN MENU → new game → PLAYING → START → SAVE screen, `GS=3` confirmed) and screenshotted: the label reads clearly, "SELECT: SAVE" / "AND EXIT," with zero visual overlap with "A: YES"/"B: NO" or the border | ✅ |
| 2 | `T5.x` demonstrably passes; no other `T5` check regresses | `T5.10`/`T5.11`/`T5.12` all `[PASS]` (`test_results.txt:51-53`) — SAVE screen reached (`GS=3`), label present (20 font tiles found in rows 12–13), no collision with rows 9/11/14. Full `T5` suite (all sub-checks) passes within the 231/231 total | ✅ |
| 3 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **231/231 pass, 0 failed** this run (current suite size, up from 220/220 at implementation time) | ✅ |
| 3 | Direct tilemap-byte read: the new text occupies only rows 12–13, columns 2–17 (no border/existing-line collision) | `T5.11`/`T5.12`'s own tilemap-byte inspection confirms this mechanically; this run's own PyBoy screenshot confirms it visually — the label sits entirely within the bordered area, no pixel overlap with any existing line or the border | ✅ |
| 4 | `asm_game.py` unmodified by this package (content-only) | `git diff --stat` between the pre-`IP-9080` state and the current tree for `asm_game.py` in this region shows no `st_save`-related change attributable to this package (the routine's `SELECT` handling was already correct, per `IP-1040`, and this package's own §6 explicitly scopes to `tilemaps.py` only) — confirmed by direct read of `st_save`'s current body, unchanged in shape from `IP-1040`'s own implementation | ✅ |
| 5 | `T5.x` present and passing | Confirmed above (`T5.10`–`T5.12`) | ✅ |
| 6 | Requirements/RTM deltas applied exactly as §9 names | `FR-1190`'s RTM row (`04-requirements-traceability-matrix.md:56`) cites `IP-1040, IP-9080` and `T14.d1–d2, T5.10–T5.12` — accurate and current; `01-functional-requirements.md`'s `FR-1190` section is marked Implemented, consistent | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-1190 (exit-to-main-menu with auto-save — on-screen discoverability) | `save_screen`'s two new `_str()` lines (`tilemaps.py`) | `T5.10–T5.12` | Cites `IP-1040, IP-9080` and both test ranges — current and accurate | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
```

**Content-package re-drive:** independently booted the built ROM in PyBoy (fresh boot, no save →
MAIN MENU → A (new game) → A (confirm default seed/scale) → A (confirm intro) → PLAYING → START →
SAVE screen, `GAMESTATE` confirmed `3`) and captured a screenshot. The label renders exactly as
claimed: "SAVE GAME?" / "A: YES" / "B: NO" / "SELECT: SAVE" / "AND EXIT," all legible, no overlap,
inside the border. No prior independent content review existed for this package, so this
screenshot is this run's own primary visual evidence (rather than corroborating a separate
review, as `VR-1031` did for `IP-1031`).

## Scope audit

Every changed symbol traces to exactly the §6-declared file: `tilemaps.py` (`save_screen`'s two
new `_str()` calls). `asm_game.py` confirmed untouched, per the package's own content-only scope.
`test_rom.py` gained `T5.10`–`T5.12` as an extension of the existing `T5` suite (no new suite
number), matching §8's own stated approach. No excursion beyond the declared set found.

## Findings

No new findings. `IP-9080`'s core claim (a clear, non-overlapping, correctly-worded label for a
previously-silent option) is confirmed both mechanically (`T5.11`/`T5.12`) and visually (this
run's own independent screenshot) — not taken on the Implementation Summary's word.
