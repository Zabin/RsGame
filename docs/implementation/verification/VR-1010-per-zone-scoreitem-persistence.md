# VR-1010 — Per-Zone ScoreItem Persistence

> Verification Report for [IP-1010](../packages/IP-1010-per-zone-scoreitem-persistence.md),
> produced by `09-package-verification`. Read-only audit — no code, package, spec, or
> requirement was edited by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-1010-per-zone-scoreitem-persistence.md) ·
[FS-101](../../features/FS-101-per-zone-scoreitem-persistence.md)

## Package

- **ID / Title:** IP-1010 — Per-Zone ScoreItem Persistence (FS-101 / FEAT-5100, Epic EP-3000,
  Release 1; rider `BL-0023`)
- **Commit verified:** `d08dbf9` (tree head; implementing commit `0773324`,
  "feat(asm): IP-1010 — per-zone ScoreItem persistence (FS-101/FR-5220)")
- **Date:** 2026-07-07
- **Independence:** clean — this session performed no implementation work; fresh container,
  PyBoy 2.7.0 + numpy reinstalled from scratch for this run.

## Result

**VERIFIED** — 0 failed checks. All four Definition of Done items and all eight Verification
Checklist items confirmed with direct evidence; full suite 125/125 pass against a byte-identical
rebuilt ROM.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | All five FS-101 ACs demonstrably pass via T11 (+ T10 for AC-5) | AC-1: T11.a4 · AC-2: T11.b5 · AC-3: T11.c · AC-4: T11.d1–d3 · AC-5: T11.e1 + T10.7–T10.12 — all PASS in this run's independent execution | ✅ |
| 2 | ROM builds at 32768 bytes; full suite (T1–T11) passes headless | `python3 build_rom.py`: "Wrote 32768 bytes", 23404 used; `python3 test_rom.py`: **125/125 passed, 0 failed** (PyBoy 2.7.0, `window='null'`) | ✅ |
| 3 | Old-format saves load without crash and show all ScoreItems available | T11.d synthetic fixture (valid `BUNY` magic, version byte `0x00`, `0xFF` garbage in the mirror region): T11.d1 boots to PLAYING, T11.d2 flags all zero, T11.d3 all 7 zone-0 collectibles active | ✅ |
| 4 | No change to cross-module interfaces, `patches` keys, or `ZONE_COLLECTS` data | Implementing diff touches only `asm_game.py`/`test_rom.py` + declared docs; `patches` key set unchanged (`zc_table` untouched, `asm_game.py:643`); `tilemaps.py` not in the diff | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Rebuild wrote 32768 bytes; sha256 **identical** to checked-in `BunnyQuest.gbc` (`673afac4…ce46` before and after); T1 header suite (incl. checksums) passes | ✅ |
| 2 | G5: full `test_rom.py` suite passes (T1–T11) | **125/125 pass, 0 failed** — run by name this session, exit clean | ✅ |
| 3 | T11.a–e present and passing, mapping 1:1 to FS-101 AC-1…5 | `test_rom.py:606–693`: T11.a1–a5 (AC-1), T11.b1–b5 (AC-2), T11.c (AC-3), T11.d1–d3 (AC-4), T11.e1 (AC-5) — 14 checks, all PASS | ✅ |
| 4 | Bit-index scheme uses list-position *k* consistently in both hook sites | Direct read: `check_collisions` computes *k* = `COLL_COUNT − B` with B live pre-pop (`asm_game.py:402`), `setup_zone_collects` computes the same *k* pre-decrement (`asm_game.py:676`) — first list entry ⇒ *k*=0 in both; identical `SLA_B` mask loops | ✅ |
| 5 | Save/load extensions inside the existing single MBC1 bracket | Direct read: `save_to_sram` enables at `:720`, new writes `:732–734`, disables `:735`; `try_load_save` enables `:740`, guarded restore `:753–755`, disables `:757` (skip path) / `:764` (no-magic path) — no second bracket anywhere | ✅ |
| 6 | Both reset paths clear `SCOREITEM_FLAGS` | `st_intro` `:196–198` (`si_clr2`), `st_victory` `:247–249` (`sv_clrf2`) — both 9-byte clear loops present; boot WRAM clear `C000`–`C2FF` (`:93–96`) also covers `0xC060` | ✅ |
| 7 | BL-0019 rider: NFR-4000 headroom re-affirmed | Build output: **23404/32768 bytes used** (+256 over 23148) — ~9.1KB headroom, nowhere near the 2KB-remaining concern line | ✅ |
| 8 | GDS-07/NFR-5200/RQ-04/Master-Build-Plan deltas applied exactly as §9 names | GDS-07 WRAM row `C060`–`C068` + SRAM rows `A012`/`A013`–`A01B` present with dated notes; NFR-5200 → MET (widened field set); RTM FR-5220 + NFR-5200 rows cite IP-1010/T11; FS-101 status → Implemented; Build Plan row COMPLETE (this VR advances it) | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-5220 (persist per-zone ScoreItem collected-state) | `asm_game.py` — constants `:42–47`, collect hook `:399–413`, zone-entry check `:670–688`, save `:731–734`, guarded load `:748–756`, resets `:196–198`/`:247–249` | T11.a–e (14 checks, all pass) | `FS-101 / IP-1010 / T11.a–e — trustworthy, 125/125 pass` — accurate | ✅ |
| NFR-5200 (save-field round-trip integrity, widened set) | Same save/load routines; full field set {zone, x, y, carrots, score, `CARROT_FLAGS`, `SCOREITEM_FLAGS`} round-trips | T10.7–T10.12 + T11.b5/T11.c/T11.e1/T11.d | Cites the exact check set — accurate | ✅ |
| FR-3200 postcondition made true going forward | `setup_zone_collects` ScoreItem suppression (`:670–688`); T11.a4/a5 prove non-respawn | Requirements *text* correction remains `BL-0022` (04 delta), correctly out of this package's scope | ✅ |

## Test run

```
pip install pyboy numpy            → pyboy-2.7.0, numpy-2.4.6 (fresh container)
python3 build_rom.py               → "Total used: 0x5B6C (23404 bytes of 32768)"
                                     "Wrote 32768 bytes → BunnyQuest.gbc"
sha256sum BunnyQuest.gbc           → 673afac4…ce46 — identical before/after rebuild
python3 test_rom.py                → RESULTS: 125/125 passed   0 failed
```

Environment note: Pillow is absent in this container, so PyBoy screenshot saving was disabled
(warnings emitted). Confirmed harmless by direct read: `shoot()` is diagnostics-only
(`test_rom.py:92–96`, `try/except: pass`), and the sole visual assertion (T6.7) uses
`screen.ndarray`, which needs no Pillow — no check was skipped or degraded.

## Scope audit

Implementing commit `0773324` touched: `asm_game.py`, `test_rom.py` (the two §6 files),
`BunnyQuest.gbc` + `test_results.txt` (conventional stage-08 build outputs), and exactly the
§9-named docs (`docs/architecture/07-data-model.md`, `docs/requirements/02-…` + `04-…`,
`docs/features/FS-101-…`, Master Build Plan, `packages/INDEX.md`). **No excursions.** The two
`JR→JP` conversions (`cc_loop` loop-back `:418/:422`, magic-check `:742`) are necessary
consequences of the added code lengthening relative-jump distances — in scope, verified present.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | `NFR-5200`'s status line in RQ-02 reads "MET … pending independent verification by `09-package-verification`" — this VR is that verification, so the "pending" clause is now stale. Cosmetic; fold into the next `04-requirements-engineering` delta (natural rider alongside BL-0022/BL-0026's existing 04-delta batch). | Low | `04-requirements-engineering` |

No Critical/High/Medium findings. `BL-0023` (score-farming bug): fix independently confirmed —
T11.a4/T11.a5 prove a collected ScoreItem stays inactive and `SCORE` does not re-increment on
zone re-entry.
