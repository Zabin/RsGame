# IP-1050 — Generated-World Save Persistence

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1050` — implements
[**FS-105**](../../features/FS-105-generated-world-save-persistence.md) (`FEAT-5300`, Epic
EP-3000, Release 2).

## 2. Objective

Extend the save-write/load-restore mechanism with `SEED`/`WORLD_SCALE`/`KeyItemFlags`
persistence, under a new save-format version value, following `IP-1010`'s version-guard pattern
exactly. The region graph itself is never persisted — it regenerates deterministically from
`(SEED, WORLD_SCALE)` on load via `IP-1020`'s routine.

## 3. Requirements Covered

FR-9200, NFR-5300 (FS-105's full Included-Requirements set).

## 4. Architecture Components

GDS-07 delta §7 (proposed SRAM additions — this package confirms/finalizes them) · ADR-0010
(save-format extension — this package's exact source) · ADR-0006 (MBC1+RAM+BATTERY mechanism,
unchanged, this package's fields ride the same bracket).

## 5. Interfaces

- **The existing MBC1 SRAM save/load routine** (`save_to_sram`/`try_load_save`, per `IP-1010`'s
  naming) — extended, not replaced.
- **The existing save-format version-guard pattern** (`SAVE_VERSION_ADDR`/`SAVE_VERSION_VAL`,
  `IP-1010`'s precedent) — a new version value supersedes `0x01`.
- **`IP-1020`'s `generate_world` routine** — invoked during load with the restored `(SEED,
  WORLD_SCALE)`, reproducing the region graph rather than reading a persisted one.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **SRAM address constants**: bump `SAVE_VERSION_VAL` from `0x01` to `0x02` (supersedes
    `IP-1010`'s value — this is the second save-format change since ship, per ADR-0010's own
    framing). Add `SRAM_SEED = 0xA01C` (2 bytes), `SRAM_WORLD_SCALE = 0xA01E` (1 byte),
    `SRAM_KEYITEM_FLAGS = 0xA01F` (up to 81 bytes worst case, `0xA01F`–`A06F`).
  - **`save_to_sram`** (existing label, inside the existing SRAM-enable bracket): additionally
    write `SAVE_VERSION_VAL` (now `0x02`) to `0xA012`, `SEED`/`WORLD_SCALE` to their mirror
    addresses, and `KEYITEM_FLAGS` (up to 81 bytes, from `IP-1020`'s WRAM copy) to
    `SRAM_KEYITEM_FLAGS`.
  - **`try_load_save`** (existing label): after the magic check passes, read `0xA012`; if it
    equals `0x02` (this package's new value): restore `SEED`/`WORLD_SCALE` from their mirrors,
    call `IP-1020`'s `generate_world` routine to regenerate `REGION_GRAPH` from the restored
    values, then restore `KEYITEM_FLAGS` from `SRAM_KEYITEM_FLAGS` onto the freshly-regenerated
    graph. If `0xA012` equals the prior value (`0x01`, `IP-1010`'s version) or anything else: per
    ADR-0010, this save is **not offered as a "continue" option at all** (not partially loaded) —
    this check is consumed by `IP-1040`'s MAIN MENU option-set logic (this package supplies the
    version-match determination as a readable fact/flag; `IP-1040` owns presenting or hiding the
    "continue" option based on it).
  - **Legacy fields** (`CUR_ZONE`/`PLAYER_X`/`PLAYER_Y`/`CARROTS_COUNT`→`KeyItemCount`/`SCORE`/
    `KEYITEM_FLAGS`-formerly-`CARROT_FLAGS`/`SCOREITEM_FLAGS`, all from `IP-1010`/`IP-1020`'s
    generalization): continue to load unconditionally exactly as today, **only** gated by the
    version-2 check for the *new* fields this package adds — an `IP-1010`-vintage save (version
    `0x01`) is excluded from "continue" entirely per ADR-0010 (a stricter response than
    `IP-1010`'s own "default to safe empty state" choice for its one field, since here the world
    *model* itself differs, not just one field).
- **Modify: `test_rom.py`** — add suite **T14** (see §8).

## 7. Implementation Tasks

Ordered: (1) SRAM constants + version-value bump; (2) `save_to_sram` extension (3 new fields);
(3) `try_load_save` extension (version check, restore-then-regenerate-then-restore-flags
sequence); (4) confirm `IP-1040`'s MAIN MENU consumes the version-match fact correctly (a
cross-package integration check, since `IP-1040` may have landed first or in the same pass); (5)
rebuild ROM; (6) author T14; (7) full suite run; (8) documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T14: Generated-World Save Persistence`**, implementing FS-105's
Verification Plan:

- T14.a — **round-trip**: save with known `(SEED, WORLD_SCALE, KeyItemFlags)`, reload in a fresh
  `PyBoy` instance (R305's two-instance pattern), assert exact match on all three, and assert the
  regenerated region graph matches the pre-save graph (delegating the graph-comparison itself to
  IP-1020's T12.b oracle check, invoked here only to confirm this package's restore-then-
  regenerate call path reaches it correctly) (AC-1).
- T14.b — **pre-upgrade rejection**: a synthetic pre-upgrade SRAM fixture (version byte `0x01`,
  `IP-1010`'s own vintage — valid `BUNY` magic, valid legacy fields, but no valid seed/scale/
  region data), following `IP-1010`'s T11.d exactly — confirm the version-match fact this package
  supplies reads as "not offered," consumed by T13's own MAIN MENU option-set tests (AC-2).
- T14.c — **legacy-field regression**: `CUR_ZONE`/position/`KeyItemCount`/`SCORE`/
  `KEYITEM_FLAGS`(-formerly-`CARROT_FLAGS`)/`SCOREITEM_FLAGS` still round-trip exactly under the
  new version-2 format, extending T10/T11's existing patterns.

## 9. Documentation Updates

- `docs/architecture/07-data-model.md` (GDS-07): finalize the delta's proposed SRAM addresses as
  confirmed (`0xA012` new version value, `SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS` mirrors at the
  addresses §6 states).
- `docs/requirements/02-non-functional-requirements.md`: NFR-5300 status → Met; NFR-5200's field
  set widened again (second widening, after `IP-1010`'s first).
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-9200/NFR-5300 rows → IP-1050/
  T14.
- `docs/features/FS-105-…md` metadata: implemented-by pointer.
- Master Build Plan status row.

## 10. Definition of Done

- Both FS-105 Acceptance Criteria demonstrably pass via T14.
- ROM builds at 32768 bytes; full suite passes.
- Old-format saves (`IP-1010`'s version `0x01`) are never offered on "continue," never partially
  loaded with garbage seed/scale/region-flags bytes.
- The region graph itself is never written to SRAM — confirmed by direct diff of the save-write
  routine's field list, not merely asserted.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] T14.a–c each present and passing (map 1:1 to FS-105 AC-1/AC-2 plus the legacy-field
      regression).
- [ ] Direct code read: save/load extensions sit inside the existing single MBC1 enable/disable
      bracket (NFR-5100 unchanged — no second bracket).
- [ ] Direct code read: `try_load_save`'s version check gates the new fields' restore path
      exactly, without altering the legacy fields' own unconditional load.
- [ ] Direct code read: `REGION_GRAPH` is never written to SRAM by `save_to_sram` — only
      `SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS`.
- [ ] BL-0019/NFR-4200 rider: SRAM headroom re-affirmed (~84 bytes new, against 8 KiB).
- [ ] GDS-07/NFR-5300/RQ-04/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1020** (persists its output — `SEED`/`WORLD_SCALE`/`KEYITEM_FLAGS`; calls its
  `generate_world` routine on load) — this tranche's foundational predecessor.
- **IP-9010, IP-9020, IP-9030, IP-9040, IP-1010** (all `VERIFIED`) — the trustworthy suite and
  the exact version-guard pattern this package extends a second time.
- **IP-1040** (supplies the "continue" option-set consumer of this package's version-match fact)
  — a soft integration dependency (this package's own save/load logic doesn't require IP-1040 to
  exist first, but its Verification Checklist's T13/T14 cross-references assume both exist by the
  time either is independently verified).

Independent of IP-1030/IP-1031 (parallel-eligible, per FP-04/TWBS).

## 13. Risks

- **A wrong version-guard bump could either falsely reject valid new saves or falsely accept a
  pre-upgrade save's garbage bytes as seed/scale/region data** (Medium, carried from FEAT-5300's
  own catalog assessment) — mitigated by T14.b's synthetic pre-upgrade fixture, following
  `IP-1010`'s T11.d discipline exactly.
- **This is the second save-format version change since ship** — the version-value sequence
  (`0x01` → `0x02`) must be strictly monotonic and never reused; a future package extending the
  save format again must bump to `0x03`, not reuse either prior value (a convention this package
  establishes by precedent, not a new mechanism).
- ROM budget: negligible (a fixed, small code addition to two existing routines). SRAM budget:
  ~84 bytes against 8 KiB, re-affirmed at §11.

## 14. Rollback Considerations

Revert `asm_game.py`/`test_rom.py` changes and rebuild. Saves written by the reverted-from build
carry version byte `0x02` + additional SRAM bytes; the pre-`IP-1050` loader (expecting `0x01`)
would treat a `0x02`-versioned save as unrecognized/not-offered exactly as this package's own
pre-upgrade handling treats `0x01` saves — no crash, no data corruption in either rollback
direction, consistent with `IP-1010`'s own rollback precedent.
