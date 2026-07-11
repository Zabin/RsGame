# IP-9070 — CUR_ZONE-Indexed Structure Generalization

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9070` — bug-remediation series; no FS. Source: **`BL-0058`** (Critical, `SCOREITEM_FLAGS`
sizing) and **`BL-0059`** (Critical, `ZONE_COLLECTS`/`zc_table` sizing/content model), both
discovered by `BL-0047`'s own mandatory supersession sweep (see
[TWBS](../01-technical-work-breakdown.md#post-ship-remediation-tranche-playtesting-bugs-bl-0047bl-0048-planned-2026-07-11)).

## 2. Objective

Make every `CUR_ZONE`-indexed WRAM/SRAM/ROM structure safe across the full generated-world
region range (`scale²`, up to 81) before `IP-9050` regeneralizes navigation to actually reach
region indices above 8. Two independent structures still assume the old fixed-9-zone model:
`SCOREITEM_FLAGS`/`SRAM_SCOREITEM` (sized for 9, indexed by `CUR_ZONE` directly — an
out-of-bounds WRAM/SRAM write once `CUR_ZONE > 8`) and `ZONE_COLLECTS`/`zc_table` (9
hand-authored, zone-named spawn lists — an out-of-bounds ROM read once `CUR_ZONE > 8`).

## 3. Requirements Covered

`FR-5220` (per-zone ScoreItem persistence — this package extends its storage to the generalized
region model, exactly as `IP-1020` already did for `FR-3210`'s carrot-flag storage), `NFR-4200`
(generated-world WRAM/SRAM headroom — this package's SRAM growth re-affirms it), `NFR-5300`
(save-format version guard — this package is the third version bump under its established
pattern). No FR currently covers collectible-spawn content for a generated region at all (the
original `ZONE_COLLECTS` predates `FEAT-9000` entirely and was never brought under a numbered
requirement); this package's `ZONE_COLLECTS` fix is scoped as a defect repair (matching
`IP-1031`'s own precedent exactly), not new requirement-covered behavior — see Risks for the
requirements-traceability gap this surfaces.

## 4. Architecture Components

GDS-07 §2/§3 (WRAM/SRAM maps — this package's own byte-layout change) · GDS-08 §1/§4 (existing
terrain-family tile/screen reuse pattern — `IP-1031`'s biome-family-representative precedent this
package's `ZONE_COLLECTS` fix mirrors exactly) · ADR-0010 (save-format extension pattern, version
guard).

## 5. Interfaces

No new interface. Extends two existing internal data layouts (`SCOREITEM_FLAGS` WRAM array,
`SRAM_SCOREITEM` SRAM mirror, `zc_table`/`ZONE_COLLECTS` ROM table) and the existing
`save_to_sram`/`try_load_save`/`check_save_valid` version-guard contract (`IP-1010`→`IP-1050`'s
established pattern) — no change to any GDS-09 module boundary.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`SCOREITEM_FLAGS`** (currently `0xC060`, 9 bytes): relocate to **`0xC286`** (81 bytes,
    `0xC286`–`0xC2D6`) — the confirmed-unused WRAM gap between `SSE_CURSOR` (`0xC285`) and
    `OAM_BUF` (`0xC300`), verified by direct read of every WRAM constant between them. **Not
    grown in place at `0xC060`** — growing to 81 bytes there would collide with `REGION_GRAPH`
    at `0xC070` (confirmed: `0xC060 + 81 = 0xC0B1 > 0xC070`).
  - **`SRAM_SCOREITEM`** (currently `0xA013`, 9 bytes): relocate to **`0xA070`** (81 bytes,
    `0xA070`–`0xA0C0`) — immediately after the current end of `SRAM_KEYITEM_FLAGS`
    (`0xA01F`–`0xA06F`), leaving `SRAM_SEED`/`SRAM_WORLD_SCALE`/`SRAM_KEYITEM_FLAGS`'s own
    addresses (`0xA01C`/`0xA01E`/`0xA01F`) **untouched** — minimizes blast radius, no other
    package's addressing needs to change.
  - **`SAVE_VERSION_VAL`**: bump `0x02`→`0x03` (third bump since ship — `0x01` `IP-1010`, `0x02`
    `IP-1050` — strictly monotonic, per both packages' own established precedent).
  - **`setup_zone_collects`**/**`check_collisions`**: every `SCOREITEM_FLAGS + CUR_ZONE` byte
    offset computation updated for the new base address (mechanical — the indexing arithmetic
    itself, `CUR_ZONE` as a direct byte offset, is unchanged and already correct for the full
    0–80 range once the array is large enough).
  - **`save_to_sram`**/**`try_load_save`**: the 9-byte `SCOREITEM_FLAGS`↔`SRAM_SCOREITEM` copy
    loops become 81-byte copies (via the existing `memcpy` subroutine `IP-1050` already
    established for the `KEYITEM_FLAGS` mirror, not an unrolled loop) at the new addresses;
    version-guard branches updated for `0x03`. A version-2 (or version-1) save is excluded from
    "continue" entirely, per `ADR-0010`'s established precedent — **not** partially loaded with
    the old 9-byte `SCOREITEM_FLAGS` layout reinterpreted as the new 81-byte one.
  - **`check_save_valid`**: version comparison updated to `0x03`.
  - **`setup_zone_collects`**: before indexing `zc_table`, read `REGION_GRAPH[CUR_ZONE]`'s
    biome-id byte (the same read `dsr_p` already performs for rendering dispatch — see
    `asm_game.py:751-761`) and index `zc_table` by **biome-id (0–4)**, not `CUR_ZONE`, for the
    `zc_table` lookup specifically (the `KEYITEM_FLAGS`/`SCOREITEM_FLAGS` per-region bookkeeping
    inside the same routine continues to index by `CUR_ZONE`, unchanged — only the spawn-content
    *table lookup* changes key).
- **Modify: `tilemaps.py`**: `ZONE_COLLECTS` reduced from 9 zone-named lists to **5
  biome-family-representative lists**, reusing the exact same representative choice `IP-1031`
  already made for screens: Water→the existing Z3 (Lake) list, Sand→Z0 (Beach), Grass→Z1
  (Forest), Stone→Z2 (Mountain), Brick→Z8 (Castle). The four now-unused lists (Z4 Village, Z5
  Cave, Z6 Desert, Z7 Plains) are removed (not merely orphaned — `ZONE_COLLECTS` is ROM-emitted
  data, not code, so an unused list is dead ROM bytes, unlike `IP-1031`'s orphaned-but-harmless
  screen *functions*). Module docstring's "still 9 zones in a 3x3 world grid" note corrected.
- **Modify: `build_rom.py`**: `zc_table`'s emission loop is unchanged in shape (still "one
  pointer per `ZONE_COLLECTS` entry") — the entry count simply drops from 9 to 5, which
  `build_rom.py`'s existing `for clist in ZONE_COLLECTS` loop already handles correctly with no
  code change needed (confirmed by direct read, `build_rom.py:119-127`).
- **Modify: `test_rom.py`** — add suite **T16** (see §8).

## 7. Implementation Tasks

Ordered: (1) relocate `SCOREITEM_FLAGS` (WRAM) and `SRAM_SCOREITEM` (SRAM) to their new
addresses; (2) bump `SAVE_VERSION_VAL` to `0x03`, update both version-guard branches
(`check_save_valid`, `try_load_save`); (3) update `save_to_sram`/`try_load_save`'s copy loops for
the new 81-byte extent and `memcpy`-based copy; (4) reduce `ZONE_COLLECTS` to 5 biome-family
lists in `tilemaps.py`, correct its docstring; (5) add the biome-id lookup to
`setup_zone_collects` before the `zc_table` index; (6) rebuild ROM; (7) author T16, including a
synthetic pre-`IP-9070` (version-2) save fixture confirming it is excluded from "continue" (per
`IP-1010`'s T11.d / `IP-1040`'s T14.a4 / `IP-1050`'s T15.b1-3 precedent, extended a third time);
(8) full suite run; (9) documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T16: CUR_ZONE-Indexed Structure Generalization`**:

- **T16.a — `SCOREITEM_FLAGS` bounds**: directly force `CUR_ZONE` to a value above 8 (e.g. 40,
  requiring a `scale≥7` world or a direct WRAM force independent of real navigation, mirroring
  `T13.a`'s isolated-force method) and a `ScoreItem` collection event; confirm the write lands
  inside `SCOREITEM_FLAGS`'s new 81-byte extent and `REGION_GRAPH`'s own bytes (`0xC070`
  onward) are unchanged before/after — the direct regression test for `BL-0058`.
- **T16.b — `zc_table`/`ZONE_COLLECTS` biome-keyed lookup**: for each of the 5 biome-ids, force
  `REGION_GRAPH[CUR_ZONE]`'s biome byte and confirm `setup_zone_collects` populates `COLL_DATA`
  from the correct biome-family list (cross-checked against the 5 retained lists' own known
  contents) — the direct regression test for `BL-0059`.
- **T16.c — save-format version-3 round-trip**: save with known `SCOREITEM_FLAGS` state
  (multiple zones' bits set, including at least one region index above 8), reload in a fresh
  `PyBoy` instance, assert exact round-trip — extending `T11`/`T15`'s two-instance pattern.
- **T16.d — pre-upgrade rejection**: a synthetic version-2 (`IP-1050`-vintage) save fixture →
  assert "continue" is not offered, following `T15.b1-3`'s exact precedent a third time.
- **T16.e — legacy-field regression**: confirm `SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS`/`REGION_GRAPH`
  regeneration are all unaffected by this package's `SCOREITEM_FLAGS` relocation (a scope-audit
  test, not just a DoD claim).

## 9. Documentation Updates

- `docs/architecture/07-data-model.md` (GDS-07): update the WRAM/SRAM tables for
  `SCOREITEM_FLAGS`/`SRAM_SCOREITEM`'s new addresses and sizes, and `SAVE_VERSION_VAL`'s new
  value.
- `docs/architecture/08-presentation-architecture.md` (GDS-08): note `ZONE_COLLECTS`'s reduction
  to 5 biome-family-representative lists, cross-referencing `IP-1031`'s identical representative
  choice for screens.
- `memory.md`: collectible/spawn quick-ref table, if it names the old 9-zone `ZONE_COLLECTS`
  shape anywhere.
- `docs/requirements/02-non-functional-requirements.md`: `NFR-4200`'s SRAM-half status
  (previously "awaits `IP-1050`" — now further extended by this package's own growth; restate
  current headroom), `NFR-5300`'s version-bump note (third bump).
- Master Build Plan status row.

## 10. Definition of Done

- `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` are 81 bytes each, at their new, non-colliding addresses;
  `REGION_GRAPH`'s own bytes are confirmed unaffected by any `CUR_ZONE` value 0–80.
- `ZONE_COLLECTS` has exactly 5 entries, one per biome family; `setup_zone_collects` indexes
  `zc_table` by biome-id, not `CUR_ZONE`.
- `SAVE_VERSION_VAL` is `0x03`; a version-2 (or earlier) save is never offered on "continue."
- ROM builds at 32768 bytes; full suite passes.
- SRAM headroom re-affirmed against the 8 KiB MBC1 bank (net growth: `SRAM_SCOREITEM` 9→81
  bytes, +72 bytes total — trivial against the existing ~10 KiB headroom margin).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T16.a–e each present and passing.
- [ ] Direct code read: `SCOREITEM_FLAGS`'s new address range (`0xC286`–`0xC2D6`) does not
      overlap `REGION_GRAPH` (`0xC070` onward, up to 405 bytes), `KEYITEM_FLAGS` (`0xC220`
      onward), or any `GW_*`/`MM_*`/`SSE_*` scratch constant.
- [ ] Direct code read: `SRAM_SCOREITEM`'s new address range (`0xA070`–`0xA0C0`) does not
      overlap `SRAM_SEED`/`SRAM_WORLD_SCALE`/`SRAM_KEYITEM_FLAGS`'s existing, unmoved addresses.
- [ ] Direct code read: `ZONE_COLLECTS` has exactly 5 entries; `zc_table`'s build-side emission
      (`build_rom.py`) requires no code change (confirmed, not merely assumed).
- [ ] BL-0019/NFR-4200 rider: SRAM headroom re-affirmed (net +72 bytes against 8 KiB).
- [ ] GDS-07/GDS-08/NFR-4200/NFR-5300/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1020** (`VERIFIED` — `REGION_GRAPH`'s own generation, `KEYITEM_FLAGS`'s sibling-widening
  pattern this package extends to `SCOREITEM_FLAGS`).
- **IP-1030** (`VERIFIED` — `dsr_p`'s biome-id read this package's `zc_table` lookup mirrors
  exactly; `REGION_GRAPH`'s WRAM placement this package's relocation must avoid).
- **IP-1040** (`VERIFIED` — its own WRAM layout (`SSE_CURSOR` ending `0xC285`, `OAM_BUF` starting
  `0xC300`) is what creates the free WRAM gap this package relocates `SCOREITEM_FLAGS` into; a
  genuine technical dependency, not merely a reference).
- **IP-1050** (`VERIFIED` — the save-format version-guard chain (`0x01`→`0x02`) this package
  extends a third time to `0x03`, and the `SRAM_KEYITEM_FLAGS` end address this package's
  `SRAM_SCOREITEM` relocation is placed immediately after).

**Not a technical dependency, cited for consistency only:** `IP-1031`'s package document
happens to name the identical water/sand/grass/stone/brick representative-zone choice this
package's `ZONE_COLLECTS` reduction reuses — but the actual `ALL_SCREENS` mapping `IP-1031`
confirmed was already wired by `IP-1030` (`IP-1031` itself shipped zero code changes). This
package does not require `IP-1031` to reach `VERIFIED` first.

**`IP-9050` (BL-0047's own navigation fix) depends on this package** — see `IP-9050`'s own
Dependencies field; this is the ordering constraint the TWBS's split rationale names.

## 13. Risks

- **Requirements-traceability gap, not invented around:** no numbered FR currently covers
  collectible-spawn content for a generated region — `ZONE_COLLECTS` predates `FEAT-9000`
  entirely and was never brought under a requirement the way `FR-3210`/`FR-9130` cover carrot/
  KeyItem placement rules. This package repairs `ZONE_COLLECTS` as a defect (matching its
  pre-existing, if unstated, intent — spawn content should track the generated world, not a
  retired fixed layout) without inventing a new FR to cover it. Recommend a future
  `04-requirements-engineering` pass add an FR for generated-region collectible-spawn sourcing,
  analogous to `BL-0020`'s precedent (missing sprite-rendering FR, added citing pre-existing
  shipped evidence) — not blocking this package.
- **Third save-format version bump in one increment** — the version-value sequence (`0x01` →
  `0x02` → `0x03`) remains strictly monotonic per `IP-1050`'s own established convention; no
  reuse risk.
- **WRAM relocation correctness** is the package's main execution risk (a wrong address collides
  silently) — mitigated by the Verification Checklist's explicit non-overlap confirmations
  against every neighboring WRAM/SRAM constant, not merely the immediately-adjacent ones.
- ROM budget: `ZONE_COLLECTS` shrinks from 9 lists to 5 (net ROM *reduction*, following
  `IP-1030`'s own precedent of generalization reducing ROM usage). SRAM budget: +72 bytes,
  trivial.

## 14. Rollback Considerations

Revert `asm_game.py`/`tilemaps.py`/`test_rom.py` changes and rebuild. A save written under
version `0x03` would be excluded from "continue" by the reverted-to version-`0x02` loader
(version-mismatch → not offered, per the same forward-compatible-rejection behavior every prior
version bump in this project already established) — no crash, no data corruption in either
rollback direction.
