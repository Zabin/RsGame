# FS-105 — Generated-World Save Persistence

> Feature Specification for [FEAT-5300](../feature-planning/03-feature-catalog.md#feat-5300--generated-world-save-persistence-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-5300, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Forward reference (metadata only):** planned by
> [IP-1050](../implementation/packages/IP-1050-generated-world-save-persistence.md) (2026-07-10).

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-105` — expands `FEAT-5300` (Generated-World Save Persistence), Epic `EP-3000` (Persistence).

## 2. Title

Generated-World Save Persistence

## 3. Purpose

Persist a generated world's (seed, scale, per-region KeyItemFlags) to SRAM, and regenerate the
region graph from (seed, scale) on load rather than persisting the graph itself. Carried forward
verbatim from FEAT-5300's own Purpose (High User Value — losing world seed/scale or per-region
collection state on reload would make the generated world worthless to return to).

## 4. Scope

**In scope:** the save-write and load-restore code paths for `SEED`/`WORLD_SCALE`/`KeyItemFlags`;
the version-guard bump that protects pre-upgrade saves from being misread.

**Out of scope** (per FEAT-5300's own Excluded Requirements, carried forward verbatim): the
generation routine itself and its immutability rule (FR-9100/FR-9110 —
[FEAT-9000](FS-102-procedural-world-generation.md), this Feature only persists/restores its
inputs and per-region flags, never the graph structure); the "continue" option's gating logic
(FR-1170 — [FEAT-1100](FS-104-main-menu-new-game-flow.md), this Feature supplies the
version-match fact FEAT-1100's MAIN MENU consumes, not the menu logic itself).

## 5. Requirements Implemented

FR-9200, NFR-5300 — the exact set FEAT-5300 owns, no more, no fewer (cross-checked against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-5300--generated-world-save-persistence-new--not-yet-implemented)'s
Included Requirements).

## 6. User Workflows

**Workflow A — Save (any of: explicit A-save, exit-to-main-menu auto-save):**

1. A save-triggering action occurs (FR-5100's existing SAVE-state A option, or FEAT-1100's new
   exit-to-main-menu option — both call the same underlying save-write mechanism, per FS-104 §9).
2. The existing save-field set is written (FR-5100/FR-5200's legacy fields, FR-5220's
   `SCOREITEM_FLAGS`, unchanged by this Feature).
3. This Feature's extension: `SEED`, `WORLD_SCALE`, and `KeyItemFlags[region]` (up to 81 bytes
   worst case) are written to their SRAM mirror addresses, under a new save-format version value
   (superseding `SAVE_VERSION_VAL = 0x01`).

**Workflow B — Load (MAIN MENU's "continue," per FS-104 Workflow B):**

1. Player selects "continue" from MAIN MENU (only offered when FEAT-1100's version-match check,
   which this Feature's version byte supplies, succeeds).
2. `SEED`/`WORLD_SCALE` are restored from their SRAM mirrors into WRAM.
3. FEAT-9000's generation routine is invoked with the restored `(SEED, WORLD_SCALE)` — **not** a
   persisted graph read — reproducing the identical region graph by construction (FR-9100's
   determinism guarantee, consumed here, not re-verified by this Feature).
4. `KeyItemFlags` are restored onto the freshly-regenerated graph (mapping each SRAM-mirrored
   flag byte back onto its corresponding region index).
5. The existing legacy save-field restore (position, score, etc.) proceeds unchanged.

## 7. System Behaviour

**Normal path:** saving then loading a game yields an identical region graph (regenerated from
the same SEED/WORLD_SCALE, per FR-9100's determinism) and identical KeyItemFlags to those present
at save time (FR-9200's own Acceptance Criteria, verbatim).

**Edge case — a save written under the prior (pre-`FR-9200`) version value:** the version-byte
mismatch is detected exactly as `FS-101`'s precedent already handles it (a version-guard
comparison), but per ADR-0010 the *response* differs from FS-101's own "default to safe empty
state" choice — such a save is **not offered on the "continue" path at all** (not partially
loaded with garbage seed/scale/region-flags bytes, and not silently defaulted to some empty
generated world) — the world *model* differs, not just a missing field (NFR-5300's own
Acceptance Criteria, verbatim).

**Edge case — `KeyItemFlags` at maximum scale (81 regions):** the full 81-byte worst-case mirror
is written/restored regardless of the actual `WorldScale` in use for smaller scales (a
fixed-size, worst-case-sized field, per GDS-07 §7's proposed layout — not a variably-sized
field), avoiding a variable-length SRAM record.

**Edge case — save-write interrupted (power loss) mid-write:** out of this Feature's own scope to
newly address — identical to the existing MBC1 SRAM enable/disable bracketing guarantee
(NFR-5100, unchanged), which this Feature's writes ride, not re-derive.

## 8. Module Responsibilities

Per GDS-03's module decomposition:

- **`asm_game.py`** — the save-write extension (three new fields appended to the existing
  save-write routine, inside the same MBC1 SRAM-enable bracket per NFR-5100, unchanged) and the
  load-restore extension (restoring `SEED`/`WORLD_SCALE` before invoking FEAT-9000's generation
  routine, then restoring `KeyItemFlags` onto the result) — following `IP-1010`'s established
  pattern exactly (a version-guarded field-set extension, same file, same bracketing discipline).

No other module is touched — this Feature is a pure extension of `asm_game.py`'s existing
save/load routines, introducing no new module and no change to `build_rom.py`/`tiles.py`/
`tilemaps.py`/`music.py`/`gbc_lib.py`.

## 9. Interfaces Used

- **The existing MBC1 SRAM save/load routine** (`save_to_sram`/`try_load_save`-equivalent,
  per `IP-1010`'s naming) — extended, not replaced; this Feature's new fields are appended inside
  the same enable/disable bracket (NFR-5100).
- **FEAT-9000's generation routine** — invoked during load with the restored `(SEED,
  WORLD_SCALE)`, per FS-102 §9's own contract; this Feature is a consumer, not a definer, of that
  interface.
- **The existing save-format version-guard pattern** (`SAVE_VERSION_ADDR`/`SAVE_VERSION_VAL`,
  `IP-1010`'s precedent, GDS-07 §3) — extended with a new version value, following the exact same
  mechanism, not a new one.

## 10. Data Model Changes

Per GDS-07's delta §7 (proposed, subject to confirmation at implementation, per the FS-101/
IP-1010 confidence precedent):

- **New SRAM fields (proposed):** a new save-format version value (superseding `0x01` at
  `0xA012`); `SEED` mirror (`0xA01C`–`A01D`, 16-bit); `WORLD_SCALE` mirror (`0xA01E`);
  `KEYITEM_FLAGS` mirror (`0xA01F`–`A06F`, 81 bytes worst case, generalizing the `CARROT_FLAGS`
  mirror at `A009`–`A011`). Total addition: ~84 bytes against 8 KiB SRAM.
- **Not persisted:** the region graph itself (`REGION_GRAPH`, FEAT-9000's own WRAM working set) —
  regenerates deterministically from `SEED`+`WORLD_SCALE` on load (ADR-0009's determinism
  requirement, consumed here as the reason this Feature does not need to persist the graph).

## 11. State Changes

None beyond the existing save/load state transitions (SAVE state's A-option, MAIN MENU's
"continue" option, both FEAT-1100's scope) — this Feature is purely a data-persistence extension
triggered by those existing/new state transitions, not a state-machine participant of its own.

## 12. Error Handling

- **Version-byte mismatch at load:** per §7's edge case — treated as "no valid save" for
  "continue" purposes (not partially loaded, not silently defaulted); this is the entirety of
  this Feature's own error-handling contract, since ADR-0010 explicitly resolves the ambiguous
  case (unlike FS-101's precedent, which needed a design decision at spec time — ADR-0010 already
  made this Feature's equivalent decision one level up).
- **A `KeyItemFlags` mirror byte with an out-of-range bit pattern (e.g. from a corrupted SRAM
  cell):** not defensively handled by this Feature's own design — identical risk profile to the
  existing `CARROT_FLAGS`/`SCOREITEM_FLAGS` mirrors, which carry no corruption-detection beyond
  the version-guard's binary match/mismatch; this Feature introduces no new corruption-handling
  scope beyond that existing precedent.

## 13. Performance Considerations

No NFR directly names this Feature's own write/read timing — the save-write/load-restore
extension rides the existing MBC1 SRAM-enable-bracketed routine (NFR-5100), adding a fixed,
small number of extra bytes (~84) to an already-bracketed operation, not a new timing-sensitive
code path.

## 14. Integrity Considerations

- **NFR-5300** (cited verbatim): "A pre-upgrade save... shall be reliably detected and never
  misread as containing valid seed/scale/region data" — this Feature's version-guard bump is the
  entire mechanism satisfying this NFR; a wrong bump (e.g. reusing the prior value) would defeat
  the guard silently, which is why the Acceptance Criteria (§15) requires a synthetic fixture
  test, not just a forward-path test.
- **Save-field round-trip integrity (NFR-5200's existing scope, extended by this Feature's new
  fields):** saving then loading must reproduce `SEED`/`WORLD_SCALE`/`KeyItemFlags` exactly — the
  same discipline `IP-1010` established for `SCOREITEM_FLAGS`, extended here to three more
  fields.

## 15. Acceptance Criteria

1. Saving then loading a game yields an identical region graph (regenerated from the same
   SEED/WORLD_SCALE) and identical KeyItemFlags to those present at save time (FR-9200).
2. Given a save written under the prior version value, after boot that save is not offered as a
   "continue" option (NFR-5300).

## 16. Verification Plan

Per FR-9200/NFR-5300's own Verification Methods (Test — save/reload two-instance harness; Test —
synthetic pre-upgrade fixture, `IP-1010`'s T11.d precedent), landing in a new **T14: Generated-
World Save Persistence** suite in `test_rom.py` (the next unused suite number after FS-104's
proposed T13):

- **AC-1 (round-trip):** extend the existing save/reload two-instance harness (T10's pattern) to
  cover `SEED`/`WORLD_SCALE`/`KeyItemFlags` — save with known values, reload in a fresh instance,
  assert exact match; additionally assert the regenerated region graph matches the pre-save graph
  (delegating the actual determinism proof to FS-102's T12, invoked here only to confirm this
  Feature's own restore-then-regenerate path reaches it correctly).
- **AC-2 (pre-upgrade rejection):** a synthetic pre-upgrade SRAM fixture (the prior version byte,
  garbage bytes in the new field range) — following `IP-1010`'s T11.d exactly — confirm "continue"
  is not offered (consumed via FS-104's MAIN MENU option-set check, T13's own AC-1/AC-2 tests).

## 17. Dependencies

Per FEAT-5300's own Dependencies (carried forward verbatim): **FEAT-9000** (persists its
output — seed, scale, KeyItemFlags — [FS-102](FS-102-procedural-world-generation.md), already
specified); FEAT-5000 (extends its save/load mechanism, already shipped Baseline); FEAT-5100
(extends its version-byte precedent, already shipped/VERIFIED). This Feature does not sit on the
procgen-world increment's own critical path (FEAT-9000 → FEAT-4100 → FEAT-6100, per FP-04) — it
depends only on FEAT-9000 (already specified) plus already-shipped/VERIFIED Features, so it is
parallel-eligible with FEAT-4100/FEAT-1100 once FEAT-9000's implementation exists.

## 18. Risks

Carried forward from FEAT-5300's own Risk assessment (Medium): a wrong version-guard bump could
either falsely reject valid new saves or falsely accept a pre-upgrade save's garbage bytes as
seed/scale/region data; mitigated by the synthetic pre-upgrade fixture discipline `IP-1010`'s
T11.d established, which this Feature's Verification Plan applies directly (not a new discipline
invented here).

## 19. Open Questions

None. Unlike FEAT-9000/FEAT-4100's Open Questions (both deferring biome-family/grammar-table
sizing decisions), this Feature's design is fully determined by ADR-0010's own explicit
decisions (the version-guard bump, the pre-upgrade-save exclusion from "continue," the exact
field set) and GDS-07 §7's proposed byte layout — no genuine ambiguity remains for
`06-feature-specification` to surface. The only implementation-time detail left open (the exact
final SRAM addresses, per GDS-07's own "proposed, subject to confirmation" framing) follows the
FS-101/IP-1010 precedent exactly and is normal `07-implementation-planning` package-authoring
work, not a design-level Open Question.

## 20. Related ADRs

ADR-0010 (seed & scale model — the save-format extension this Feature implements is this ADR's
own Consequences section, verbatim), ADR-0006 (MBC1+RAM+BATTERY mechanism this Feature's fields
ride, unchanged).
