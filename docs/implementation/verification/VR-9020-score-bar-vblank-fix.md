# VR-9020 — Score-Bar VRAM Write Timing Fix

> Verification Report for [IP-9020](../packages/IP-9020-score-bar-vblank-fix.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was
> edited by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9020-score-bar-vblank-fix.md)

## Package

- **ID / Title:** IP-9020 — Score-Bar VRAM Write Timing Fix (`BL-0003`, under the `BL-0008`
  umbrella; rider `BL-0019`)
- **Commit verified:** `b4d3a0d` (tree head; implementing commit `0e22fdb`,
  "feat(asm): IP-9020 — relocate score-bar HUD write to frame-top VBlank")
- **Date:** 2026-07-07
- **Independence:** clean — this session performed no implementation work; verification runs
  against a fresh-container PyBoy 2.7.0 install.

## Result

**VERIFIED** — 0 failed checks. All three Definition of Done items and all four Verification
Checklist items confirmed with direct evidence; full suite 125/125 pass against a byte-identical
rebuilt ROM.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | No code path writes `0x9800`-region bytes while the LCD is on outside VBlank | Direct read of every `0x98xx` write site: `update_status_disp` (`asm_game.py:541/551/559/562`) — called only from the frame top (`:162`), inside VBlank; the 576-byte tilemap copy (`:624/:632`) and `update_map_hearts` (`:696–716`, called only as `do_screen_redraw`'s map-screen `extra`, `:599`) — both run after `do_screen_redraw` waits LY≥144 and disables the LCD (`:567–569`); boot-time VBK access (`:103`) runs LCD-off. No other writers exist. | ✅ |
| 2 | HUD digits still update correctly on collection (T8 checks pass) | T8 suite passes in full, including T8.10a (forced `SCORE=42` → digits `0,4,2` at `0x9808–0x980A` within 2 frames) and T8.10b (forced `CARROTS_COUNT=5` → digit at `0x9802` within 2 frames) | ✅ |
| 3 | ROM still 32768 bytes; byte-count delta ≈ 0 | Rebuild wrote 32768 bytes; the package's own commit left usage at 23148 (delta 0 vs. pre-package — a `CALL` moved). Current tree usage is 23404 solely due to the subsequently-implemented, independently-verified IP-1010 (+256) | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | `python3 build_rom.py`: "Wrote 32768 bytes"; sha256 identical to checked-in `BunnyQuest.gbc` (`673afac4…ce46`); T1 header suite passes | ✅ |
| 2 | G5: full `test_rom.py` suite passes incl. the new T8 digit-timing checks | **125/125 pass, 0 failed** — run by name this session; T8.10a/T8.10b both PASS | ✅ |
| 3 | `st_playing` no longer calls `update_status_disp`; frame-top call sits between the `VBLANK_FLAG` clear and the `NEED_REDRAW` check | Direct read: exactly one `CALL('update_status_disp')` in the file, at `asm_game.py:162` — after the flag clear (`:160`), before the `NEED_REDRAW` load (`:164`). `st_playing` (`:206–213`) calls only input/collisions/transition/complete. The routine's internal guards are present: `RET_NZ` on `GAMESTATE≠PLAYING` (`:535`), `RET_Z` on clean `SCORE_DIRTY` (`:536`) — the unconditional call-site is safe in every state | ✅ |
| 4 | BL-0019 rider: NFR-4000 headroom re-affirmed | Current build: **23404/32768 bytes** (~9.1KB headroom; the 23404 includes IP-1010's verified +256 — this package itself contributed delta 0) | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| NFR-1200 (VBlank-gated score-bar write) | Frame-top relocation, `asm_game.py:162`; RQ-02 status → MET (dated 2026-07-07, citing IP-9020) | T8.10a/T8.10b | Cites `IP-9020` + `T8.10a, T8.10b — trustworthy` — accurate (the cell's "111/111" count is a snapshot from the package's own commit; suite is 125/125 today after IP-1010) | ✅ |
| FR-6200-family HUD behavior unchanged | Same digits, same addresses, same `SCORE_DIRTY` protocol — only the call site moved; accepted one-frame latency documented in the package (§7.3), no requirement states same-frame latency | T5.4–T5.8 + T8.10a/b all pass | FR-6200 row unchanged (correctly — no behavior change) | ✅ |

## Test run

```
python3 build_rom.py               → "Total used: 0x5B6C (23404 bytes of 32768)"
                                     "Wrote 32768 bytes → BunnyQuest.gbc"
sha256sum BunnyQuest.gbc           → 673afac4…ce46 — identical before/after rebuild
python3 test_rom.py                → RESULTS: 125/125 passed   0 failed
```

(PyBoy 2.7.0 headless, fresh container. Pillow absent — screenshots are diagnostics-only in
this suite; confirmed no assertion depends on them.)

## Scope audit

Implementing commit `0e22fdb` touched: `asm_game.py` (3-line call relocation — the §6 file),
`test_rom.py` (T8.10a/b — §8), `BunnyQuest.gbc` + `test_results.txt` (conventional stage-08
build outputs), and exactly the §9-named docs (RQ-02, GDS-06 N2, RTM, Master Build Plan,
`packages/INDEX.md`). **No excursions.**

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | "Pending independent verification by `09-package-verification`" clauses are now stale in two places this VR satisfies: RQ-02's NFR-1200 status line and GDS-06 N2's remediation note. Same pattern as VR-1010's finding on NFR-5200 (BL-0028) — fold all of these into the same `04-requirements-engineering` delta batch (the GDS-06 note is a one-word pointer edit owned by `03`, riding the same pass). The RTM cell's "111/111" count is likewise a stale snapshot (125/125 today) — same batch. | Low | `04-requirements-engineering` (+ `03` for the GDS-06 pointer) |

No Critical/High/Medium findings. `BL-0003` (mid-frame score-bar VRAM write): remediation
independently confirmed — the only remaining VRAM writers are LCD-off (`do_screen_redraw` path)
or frame-top VBlank (`update_status_disp`).
