# Integration Review — Bootstrap Tranche

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

The bootstrap increment's full package set, all `VERIFIED` on the Master Build Plan:

| Package | Title | VR |
|---|---|---|
| IP-9010 | Test suite rewrite (BL-0006 + BL-0005) | [VR-9010](../implementation/verification/VR-9010-test-suite-rewrite.md) |
| IP-9020 | Score-bar VRAM write timing fix (BL-0003) | [VR-9020](../implementation/verification/VR-9020-score-bar-vblank-fix.md) |
| IP-9030 | Root documentation refresh (BL-0007) | [VR-9030](../implementation/verification/VR-9030-root-doc-refresh.md) |
| IP-9040 | Legacy artifact archival (BL-0004) | [VR-9040](../implementation/verification/VR-9040-legacy-artifact-archival.md) |
| IP-1010 | Per-zone ScoreItem persistence (FS-101 / FEAT-5100) | [VR-1010](../implementation/verification/VR-1010-per-zone-scoreitem-persistence.md) |

**Commit reviewed:** `10c99d4` (tree head at review time). All five packages confirmed
`VERIFIED` on the Master Build Plan before this review began.

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x5B6C (23404 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
python3 test_rom.py                   → RESULTS: 125/125 passed   0 failed
```

## Dimension 1 — Interface consistency

**Clean.** Exercised the real seams between packages:

- **Patch-point dict contract** (`build_game_asm(rom) -> patches`, consumed by `build_rom.py`):
  all 17 keys `build_rom.py` reads (`tile_src`, `bg_pal`, `obj_pal`, `mus_lo`/`mus_hi`/
  `mus_reset`, `title_t`/`title_a`, `intro_t`/`intro_a`, `save_t`/`save_a`, `map_t`/`map_a`,
  `vic_t`/`vic_a`, `zs_table`, `zc_table`) are set exactly once in `asm_game.py` — no orphaned
  key on either side.
- **Tile-slot assignments** (`tiles.py`): all 83 `TL_*` constants have distinct values —
  checked programmatically, zero collisions.
- **`ZONE_COLLECTS` shape** (`tilemaps.py`, touched by IP-1010's persistence logic): 9 zones,
  exactly one `type==2` (Carrot) entry each — confirmed by direct load, matching the invariant
  `BL-0017`'s T1.11 asserts.
- **`ALL_SCREENS`**: consumed by `build_rom.py`'s `for name, fn in ALL_SCREENS` loop; ordering
  and shape unchanged by any of the five packages.

## Dimension 2 — Invariant sweep

**Clean.** Checked across the whole set, not sampled:

- **ROM budget:** exactly 32768 bytes, valid header, non-overlapping named sections in the
  build's own section-layout printout (T/A pairs per screen, no address reuse).
- **VBlank-gating:** full sweep of every `0x98xx`/`0x99xx`-region write site in `asm_game.py`:
  `update_status_disp` (frame-top VBlank, IP-9020's fix, lines 539–562) and `copy_screen`/
  `update_map_hearts` (both run only inside `do_screen_redraw`'s LCD-off bracket, lines 624/632,
  698–706). No other writer exists. Matches VR-9020's own sweep — unchanged since.
- **WRAM/SRAM address map:** every named WRAM constant in `asm_game.py` (`GAMESTATE` through
  `SCOREITEM_FLAGS`) cross-checked byte-for-byte against GDS-07's table — exact match, including
  IP-1010's `SCOREITEM_FLAGS` (`0xC060`) and `SAVE_VERSION_ADDR`/`SRAM_SCOREITEM`
  (`0xA012`/`0xA013`). No address used in code is missing from GDS-07's map.
- **One-job-per-file:** unaffected — no package altered the six-module decomposition
  (`gbc_lib.py`/`tiles.py`/`tilemaps.py`/`music.py`/`asm_game.py`/`build_rom.py`).
- **Tile index map:** collision-free (see Dimension 1).

## Dimension 3 — Behavioral coherence

**Clean.** The two packages most likely to interact — IP-9020 (HUD write timing) and IP-1010
(ScoreItem persistence, which also touches `SCORE`/HUD state) — were exercised together in the
same 125/125 run: T8.10a/b (HUD digit timing) and T11.a–e (ScoreItem persistence across zone
re-entry and save/reload) all pass in the same suite execution, confirming no divergent or
conflicting handling of `SCORE_DIRTY`/HUD redraw between the two packages. No player-visible
workflow spans a package seam and dead-ends: save → exit → reload → zone re-entry → HUD update
is exercised end-to-end by T10/T11 together.

## Dimension 4 — Traceability coherence

**Two findings** — both stale cross-references outside any single package's own file scope,
never updated because no stage-08/09 run touched these documents.

**Finding 1 (Medium):** `ROADMAP.md`'s Implementation theme table (lines 107–112) is stale:
- `IM-00` (Master Build Plan row): "live — 5 packages tracked, 2026-07-07" — doesn't reflect
  that all five are now `VERIFIED`.
- `IP-xxxx` row: **"authored 2026-07-07; none implemented"** — factually wrong; all five are
  implemented and independently verified.
- `VR-xxxx` row: **"⛔"** (blocked/not-started) — factually wrong; five Verification Reports
  exist (`VR-9010`/`VR-9020`/`VR-9030`/`VR-9040`/`VR-1010`).

**Finding 2 (Medium):** `docs/feature-planning/01-release-plan.md` §"Release 1" and
`03-feature-catalog.md`'s `FEAT-5100` section both still describe it as having **"no shipped
implementation"** / **"(new — not yet implemented)"** — stale since `IP-1010` shipped and was
verified 2026-07-07, the same day these feature-planning documents were authored but before the
implementation landed. `05-feature-decomposition` never re-touched them afterward.

Both findings are pure documentation drift — the underlying facts (all five packages VERIFIED,
FEAT-5100 shipped) are correct and consistent everywhere else (Master Build Plan, packages
`INDEX.md`, verification `INDEX.md`, RTM). No requirement, package, or code disagrees with
another; only these two ledgers lag behind.

## Dimension 5 — Documentation coherence

**Clean.** `Claude.md`/`memory.md` (refreshed by `IP-9030`, independently verified this session
via `VR-9030`) accurately reflect the integrated five-package result: current WRAM/SRAM facts
pointing to GDS-07/08, Known Good Behavior naming the ScoreItem-persistence behavior IP-1010
shipped, Known Issues naming both BL-0001 (not-reproducing) and BL-0003 (fixed by IP-9020) as
closed. `docs/implementation/packages/INDEX.md` and `verification/INDEX.md` are both current
and mutually consistent with the Master Build Plan.

## Findings summary

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | `ROADMAP.md`'s `IM-00`/`IP-xxxx`/`VR-xxxx` rows (Implementation theme table) describe the package set as unimplemented/unverified; all five are `VERIFIED` | Medium | `07-implementation-planning` (owns the Implementation theme's ROADMAP rows) — a light status-only edit, no content decision |
| 2 | `docs/feature-planning/01-release-plan.md` §Release 1 and `03-feature-catalog.md`'s `FEAT-5100` entry describe it as unimplemented; `IP-1010`/`FS-101` shipped and are `VERIFIED` | Medium | `05-feature-decomposition` (owns both documents) — update to reflect Release 1 closed, FEAT-5100 shipped |

No Critical/High findings.

## Result

**Clean overall** (no Critical/High findings) — two Medium documentation-coherence findings
routed above, neither blocking. The bootstrap tranche's five packages integrate correctly: no
interface mismatch, no violated invariant, no behavioral conflict. Ready to proceed to
`11-release-readiness`.
