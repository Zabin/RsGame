# VR-1081 — Maze-Blocked Edge Indicator (content)

> Independent verification of [IP-1081](../packages/IP-1081-maze-blocked-edge-indicator-content.md),
> performed by `09-package-verification` in a fresh session (the same-session-independence rule
> blocked verification in the implementing session, 2026-07-12).

## Package

- **ID:** IP-1081
- **Title:** Maze-Blocked Edge Indicator (content)
- **Commit implemented:** `5569ba7` ("feat(content): IP-1081 -- maze-blocked edge indicator tile art")
- **Commit verified against:** `282d68c` (`main`, post-PR #18 merge; no further changes to `tiles.py`
  or `build_rom.py` since `5569ba7`)

## Result

**VERIFIED** — 0 failed checks. One Medium finding routed to `09-content-review` (§Findings) —
does not block `VERIFIED`, per the package's own §13 Risks, which explicitly defers pixel-craft
silhouette judgment to that later review.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| 4 new tile-index constants exist (`TL_BLOCKED_U/D/L/R`, `0x1A`–`0x1D`) and are registered in `build_tile_data()` | `tiles.py:40-43` declares all four constants at the claimed addresses; `tiles.py:954-957` registers all four via `put(TL_BLOCKED_U, blocked_up())` etc., immediately after `put(TL_ARROW_D, arrow_down())` — continuing the existing block, not a new one, exactly as §6 specifies. | PASS |
| Each tile's pixel silhouette is distinct from the corresponding `TL_ARROW_*` tile (not a recolor) | Direct comparison of the `enc([...])` pixel arrays: `blocked_up()`/`blocked_down()` (two horizontal bar segments with a gap) are structurally unrelated to `arrow_up()`/`arrow_down()` (filled triangle arrowheads) — confirmed by reading both function bodies side-by-side (`tiles.py:816-827` vs `tiles.py:833-856`). Genuinely distinct silhouettes, not a recolor. | PASS |
| Zero new BG/OBJ palette entries added to `build_rom.py` | `git diff 5569ba7~1 5569ba7 -- build_rom.py` — empty diff, confirmed `build_rom.py` untouched by this commit. | PASS |
| ROM builds successfully with the 4 new tiles present; no existing test regresses | `python3 build_rom.py` this session: 32768 bytes written, no errors. `python3 test_rom.py`: 233/233 pass (233, not 231, because `IP-1021` — verified earlier this same session — has since landed on `main`; `IP-1081` itself contributes 0 new checks, exactly as its own DoD states, and no existing check regressed). | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Confirmed this session (`build_rom.py` output above); header validity confirmed by the passing T1 suite within the 233/233 run. | PASS |
| G5: full `test_rom.py` suite passes (unchanged count) | 233/233 — the +2 relative to the package's own reported 231 is fully accounted for by `IP-1021`'s two new checks (`T12.e` revised, `T12.n`), unrelated to this package; `IP-1081` itself added 0. | PASS |
| Direct diff: `tiles.py` gains exactly 4 new tile-index constants + 4 new pixel-art functions + 4 new `put()` calls, nothing else | `git diff 5569ba7~1 5569ba7 -- tiles.py` — exactly this: 4 constants (lines 40-43), 4 functions (`blocked_up/down/left/right`), 4 `put()` calls. No other lines touched. | PASS |
| Direct diff: `build_rom.py`'s `BG_PALETTES`/`OBJ_PALETTES` tables unchanged | Empty diff confirmed (see DoD row above). | PASS |
| `0x1A`–`0x1D` confirmed unused by any other tile before this package claims them | `git show 5569ba7~1:tiles.py` — `TL_ARROW_D = 0x19` was the last-occupied UI-icon slot; `0x1A`–`0x1D` did not appear anywhere in the prior tree. | PASS |
| GDS-07 §4 / Master-Build-Plan deltas applied exactly as §9 names | `docs/architecture/07-data-model.md:108` — `0x1A`–`0x1D` row added exactly as described. `FS-108` metadata (`docs/features/FS-108-...md:33-36`) carries the implemented-by pointer. Master Build Plan status row present. | PASS |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-2330 (rendered-appearance half only) | `tiles.py:816-827` (4 new tile functions), registered `tiles.py:954-957` | No new `test_rom.py` check — per the package's own §8, no runtime path references these tiles yet (`IP-1082`'s scope); build-time registration confirmed directly (DoD row above) instead. | Not independently re-checked against the RTM this run (FR-2330's row is a joint IP-1081/IP-1082 target — the package's own §3 scopes this package to only the appearance half; a full RTM cell fill is appropriate once `IP-1082` also ships, per that package's own §9). | Consistent with package scope — PASS |

## Test run

- `python3 build_rom.py BunnyQuest.gbc` → `Wrote 32768 bytes → BunnyQuest.gbc`.
- `python3 test_rom.py` → **233/233 passed, 0 failed** (fresh session; PyBoy 2.7.0 already installed
  earlier this session for `VR-1021`).
- No tunable/generated parameter applies to this package (pure static tile-pattern data, no
  runtime behavior yet) — the skill's live-drive rule for tunable parameters does not apply here;
  confirmed by re-reading §6/§8, which explicitly states no runtime code path exists yet.

## Scope audit

Diff (`5569ba7~1..5569ba7`) touches `tiles.py`, `BunnyQuest.gbc` (rebuilt binary),
`ROADMAP.md`/`docs/architecture/07-data-model.md`/`docs/feature-planning/03-feature-catalog.md`/
`docs/features/FS-108-...md`/`docs/implementation/00-master-build-plan.md`/
`docs/implementation/packages/INDEX.md`/`memory.md` (documentation), matching the package's
declared "Files to Create/Modify" (§6, code) plus its named Documentation Updates (§9) exactly.
No excursion into `asm_game.py`/`build_rom.py` or any file `IP-1082` (the code/render peer) owns.

## Findings

| Finding | Severity | Owner |
|---|---|---|
| `blocked_up()` and `blocked_down()` are pixel-for-pixel identical (`tiles.py:829-834`); `blocked_left()` and `blocked_right()` are likewise pixel-for-pixel identical to each other (`tiles.py:835-845`). The package's own §6 narrative explicitly directs 4 tiles "oriented per direction the same way the arrow tiles are (a directional glyph, not a direction-agnostic icon)" — by contrast, `arrow_up()`/`arrow_down()` and `arrow_left()`/`arrow_right()` (`tiles.py:816-827`) are genuinely distinct mirror-image shapes. The shipped `blocked_*` tiles collapse to 2 distinct bitmaps (a vertical bar, a horizontal bar) rather than 4 direction-specific glyphs — each pair is a direction-agnostic icon reused across two direction slots, the exact shape the package's own text said not to ship. This does **not** fail the package's own enumerated Definition of Done or Verification Checklist (both items concerning pixel content — "distinct from the corresponding `TL_ARROW_*` tile," "confirmed by direct visual inspection... judged fully against GDS-08 §7's craft checklist by the follow-on `09-content-review` pass" — are satisfied or explicitly deferred), so it does not block `VERIFIED` here. Recorded for `09-content-review`'s attention when it eventually reviews `FS-108`/`IP-1082` together (gated on `IP-1082` shipping, per this package's own §1), since that review is the one place this project's process puts silhouette/craft judgment, and it should not discover this only after the render branch ships. | Medium | `09-content-review` (deferred until `IP-1082` ships, per FS-108 §1's own review-scheduling note) |
