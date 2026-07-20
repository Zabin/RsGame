# IP-8110 — ROADMAP.md Cell Compaction

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — meaning-preserving documentation restructuring only.**

## 1. Package ID

`IP-8110` — refactors `ROADMAP.md`, filed from **`BL-0182`** (`refactor`, `SCHEDULED`).

## 2. Objective

Seven `ROADMAP.md` Status cells have grown into full project-history essays (`IM-00` alone is
~17.4KB in one cell), duplicating history that already lives in full in each row's own owning
document or theme `INDEX.md`. Compact each to a short current-state summary + pointer, verified
against the owning doc before trimming so nothing is actually lost.

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

Unaffected.

## 5. Interfaces

- **Seven rows compacted**, each only after confirming its full history is independently
  reconstructable from the named target:
  - `IM-00` (Master Build Plan) → `docs/implementation/00-master-build-plan.md` (already the
    authoritative per-package ledger this session has maintained throughout).
  - `IP-xxxx` (Implementation Packages) → `docs/implementation/packages/INDEX.md`.
  - `VR-xxxx` (already short, left as-is — included for cross-reference only, not touched).
  - `RV-INTEG` (Integration reviews) → `docs/reviews/INDEX.md` + the individual review files
    already linked inline.
  - `R201-R220`, `R101-R115` (Research tiers) → `docs/research/INDEX.md`.
  - `ADR-xxxx` (Architecture Decision Records) → `docs/architecture/adr/INDEX.md`.
  - `IM-01` (Technical Work Breakdown) → the TWBS document's own section-by-section content
    (each delta already has its own dedicated section, per this session's own additions).
  - Each compacted cell keeps: current status symbol, a 1-2 sentence current-state summary (final
    counts/facts), and an explicit pointer ("full history: `<owning doc>`").
- **No other rows touched** — every other `ROADMAP.md` row is left exactly as-is.

## 6. Files to Create/Modify

- **Modify: `ROADMAP.md`** — seven Status cells compacted per §5. No other content, structure,
  or row changes.

## 7. Implementation Tasks

Ordered, one row at a time: (1) read the target owning doc/INDEX in full; (2) confirm every
distinct fact/ID/finding named in the ROADMAP cell's current prose is present there (if any single
fact is NOT independently reconstructable, keep it inline rather than drop it — do not compact
that clause); (3) write the compacted cell; (4) repeat for each of the seven rows; (5)
link-integrity check across the tree; (6) commit.

## 8. Tests to Add

**None.** Equivalence proof is the per-cell verification in §7 (every fact confirmed present in
the owning doc before its ROADMAP copy is removed).

## 9. Documentation Updates

None beyond `ROADMAP.md` itself.

## 10. Definition of Done

- All seven target cells compacted to current-state + pointer.
- Every fact previously stated inline is confirmed present in the pointed-to owning doc (or, for
  the rare fact that isn't, kept inline rather than silently dropped).
- No other row touched.

## 11. Verification Checklist

- [ ] Each compacted cell's current-state summary matches the owning doc's own current status
      exactly (no drift introduced).
- [ ] Spot-check at least 3 distinct historical facts per compacted row against the owning doc,
      confirming presence.
- [ ] File size materially reduced (target: ROADMAP.md well under half its pre-refactor size).
- [ ] Link integrity: pointers resolve to real, existing files.

## 12. Dependencies

None.

## 13. Risks

- **A fact stated in ROADMAP's prose but not actually present in the owning doc** (Low-Medium,
  the main risk this package manages): mitigated by the explicit per-cell verify-before-trim
  step in §7 — any such fact is kept inline, not dropped, rather than assumed reconstructable.
- **Breaking a cell's own Markdown table syntax during compaction** (Low): mitigated by keeping
  each cell a single unbroken paragraph, no embedded pipe/newline characters.

## 14. Rollback Considerations

Revert `ROADMAP.md`'s git history.
