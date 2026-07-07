# IP-1010 — Per-Zone ScoreItem Persistence

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1010` — implements
[**FS-101**](../../features/FS-101-per-zone-scoreitem-persistence.md) (`FEAT-5100`, Epic
EP-3000, Release 1). Rider: **`BL-0023`** (ScoreItem respawn/score-farming bug — fixed by this
package's zone-entry check, per FS-101's design).

## 2. Objective

Persist per-zone `ScoreItem` collected-state so collected stars/flowers never reappear — across
zone re-entry within a session and across save/power-off/reload — exactly mirroring the shipped
`CARROT_FLAGS` pattern, with a save-format version guard protecting pre-upgrade saves.

## 3. Requirements Covered

- **`FR-5220`** (persist per-zone ScoreItem collected-state) — FS-101's sole Included
  Requirement.
- **`NFR-5200`** (save-field round-trip integrity, widened field set) — moves from
  "Met, not re-verified for the new field" to verified-Met.
- Makes **`FR-3200`**'s postcondition true going forward (see FS-101 Risks; the requirements
  *text* correction is `BL-0022`, a separate `04` delta, not this package).

## 4. Architecture Components

GDS-04 (Collectible/SaveGame entities) · GDS-07 (WRAM map + SRAM format — this package extends
both; see §9) · ADR-0006 (save mechanism/magic — widened within the same mechanism) · FS-101
Design Decisions 1–2 (structure + pre-upgrade default; both already decided, not re-opened
here).

## 5. Interfaces

No GDS-09 cross-module contract changes: `build_game_asm`'s `patches` keys, `ALL_SCREENS`,
`ZONE_COLLECTS` shape, and `music_data` are untouched. All changes are internal to
`asm_game.py`.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`** — all cited sites verified against current source:
  - WRAM constants block (lines 17–42): add `SCOREITEM_FLAGS = 0xC060` (9 bytes,
    `C060`–`C068`) — **address assigned by this plan** (FS-101 Open Question 3): GDS-07 shows
    `C051`–`C2FF` unallocated; `0xC060` is 8-aligned, leaves headroom next to `COLL_COUNT`
    (`0xC050`), and sits inside the boot clear of `C000`–`C2FF` (lines 86–88), giving the
    all-zero fresh-boot state for free. Also add `SAVE_VERSION_ADDR = 0xA012`,
    `SAVE_VERSION_VAL = 0x01`, `SRAM_SCOREITEM = 0xA013`.
  - `check_collisions`' non-carrot branch (`cc_not_c`, lines 380–385): on ScoreItem hit,
    additionally set bit *k* of `SCOREITEM_FLAGS[CUR_ZONE]`, where *k* = the item's
    list-position index within the zone's `ZONE_COLLECTS` entries. Note: the current loop
    tracks remaining-count in `B` (counting down from `COLL_COUNT`); the item index is
    derivable as `COLL_COUNT − B`. Preserve register discipline (the loop PUSHes/POPs `BC`/
    `HL` around the hit path — mirror the existing carrot branch's save/restore pattern,
    lines 371–378).
  - `setup_zone_collects` (lines 611–640): after the existing carrot check (`szc_sk` path,
    lines 628–638), add the mirrored ScoreItem check: for non-carrot entries, test bit *k* of
    `SCOREITEM_FLAGS[CUR_ZONE]` (*k* = list position, i.e. entries processed so far =
    `COLL_COUNT − B`); if set, clear the just-written `active` byte exactly as the carrot path
    does (`DEC_HL / XOR_A / LD_HL_A / INC_HL`, line 638).
  - `save_to_sram` (lines 668–681): inside the existing SRAM-enable bracket, additionally
    write `SAVE_VERSION_VAL` to `0xA012` and the 9 `SCOREITEM_FLAGS` bytes to
    `0xA013`–`0xA01B`.
  - `try_load_save` (lines 684–704): after the magic check passes, read `0xA012`; if it equals
    `SAVE_VERSION_VAL`, restore `0xA013`–`0xA01B` → `SCOREITEM_FLAGS`; otherwise leave
    `SCOREITEM_FLAGS` all-zero (pre-upgrade save ⇒ "all uncollected", FS-101 Design
    Decision 2). Existing fields load unconditionally as today (older saves stay loadable).
  - New-game reset (`st_intro`, lines 183–188) and victory progress-clear (`st_victory`,
    lines 234–237): extend both 9-byte `CARROT_FLAGS` clear loops to also clear
    `SCOREITEM_FLAGS` (or add a parallel 9-byte clear).
- **Modify: `test_rom.py`** — add suite **T11** (see §8). No other module changes (confirmed
  by FS-101 Module Responsibilities).

## 7. Implementation Tasks

Ordered: (1) constants; (2) collection-hook bit-set; (3) zone-entry suppression check;
(4) save-path extension; (5) load-path extension with version guard; (6) reset-path clears;
(7) rebuild ROM; (8) author T11; (9) full suite run; (10) documentation/traceability updates
(§9). Tasks 2–3 share the bit-index helper logic (compute mask from list-position *k*, an
`OR`-mask / `AND`-test against `SCOREITEM_FLAGS + CUR_ZONE`) — implement once, reuse.

## 8. Tests to Add

New `test_rom.py` suite **`T11: Per-Zone ScoreItem Persistence`** (numbering reserved by
IP-9010), implementing FS-101's Verification Plan:

- T11.a — same-session: collect a ScoreItem in zone 0, transit right and back, assert its
  `COLL_DATA` active byte is 0 and `SCORE` did not re-increment (AC-1; also `BL-0023`'s
  regression guard against score farming).
- T11.b — save/reload: collect, save via SAVE menu, stop, boot a second PyBoy instance on the
  `.ram` file, assert the item stays inactive (AC-2, R305 two-instance pattern).
- T11.c — never-collected items remain active across transitions/save/reload (AC-3).
- T11.d — pre-upgrade save fixture: construct a synthetic SRAM image with valid `BUNY` magic +
  legacy fields but version byte ≠ `0x01`, boot, assert all `SCOREITEM_FLAGS` zero and all
  ScoreItems active (AC-4).
- T11.e — legacy-field regression: `CUR_ZONE`/`PLAYER_X`/`PLAYER_Y`/`CARROTS_COUNT`/`SCORE`/
  `CARROT_FLAGS` still round-trip exactly (AC-5, leans on IP-9010's rewritten T10).

## 9. Documentation Updates

- `docs/architecture/07-data-model.md` (GDS-07): additive delta rows — WRAM `C060`–`C068`
  `SCOREITEM_FLAGS`; SRAM `A012` version guard + `A013`–`A01B` mirror (dated changelog note;
  the delta is specified verbatim by this package, applied mechanically by stage 08).
- `docs/requirements/02-non-functional-requirements.md`: NFR-5200 status re-verified for the
  widened field set.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-5220 row → IP-1010/T11.
- `docs/features/FS-101-…md` metadata: implemented-by pointer (already points here).
- Master Build Plan status row.

## 10. Definition of Done

- All five FS-101 Acceptance Criteria demonstrably pass via T11 (+ rewritten T10 for AC-5).
- ROM builds at 32768 bytes; full suite (T1–T11) passes headless.
- Old-format saves load without crash and show all ScoreItems available.
- No change to any cross-module interface, `patches` key set, or `ZONE_COLLECTS` data.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes (T1–T11).
- [ ] T11.a–e each present and passing (map 1:1 to FS-101 AC-1…5).
- [ ] Direct code read: `SCOREITEM_FLAGS` bit-index scheme uses list-position *k* consistently
      in both the collection hook and the zone-entry check.
- [ ] Direct code read: save/load extensions sit inside the existing single MBC1
      enable/disable bracket (NFR-5100 unchanged — no second bracket).
- [ ] Both reset paths (`st_intro`, `st_victory`) clear `SCOREITEM_FLAGS`.
- [ ] BL-0019 rider: NFR-4000 headroom re-affirmed — report used/32768 after build (expected
      growth ≈ 60–130 code bytes over 23148; nowhere near the 2KB-remaining concern line).
- [ ] GDS-07/NFR-5200/RQ-04/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-9010** (`VERIFIED`) — T11 lands in the rewritten suite; AC-5 relies on its T10.
- FEAT-5000/FEAT-3000 (FS-101's stated dependencies) are shipped as-built code, not open
  packages — no package-graph edge needed.

## 13. Risks

- **First save-format change since ship (ADR-0006)** — Medium, carried from FS-101; the
  version guard is the designed mitigation, and T11.d is its executable proof.
- **Register-discipline defects** in the two SM83 hook sites (the `check_collisions` loop's
  `B`-countdown and `HL` cursor are load-bearing) — mitigated by mirroring the adjacent,
  proven carrot-branch push/pop pattern and by T11.a/T8 coverage.
- ROM budget (`BL-0019` rider): ≈60–130 added code bytes in the code section (per GDS-07 §1
  layout); headroom after ≈9.5KB — re-affirmed at §11.

## 14. Rollback Considerations

Revert the `asm_game.py`/`test_rom.py` changes and rebuild. Saves written by the reverted-from
build carry version byte `0x01` + 10 extra SRAM bytes; the pre-FS-101 loader ignores bytes past
`A011`, so rollback keeps old builds loading such saves correctly (the extra bytes are inert) —
no save-data loss in either direction.
