# IP-8090 — Pipeline Journal Archive Split

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — meaning-preserving documentation restructuring only.**

## 1. Package ID

`IP-8090` — refactors `docs/pipeline/pipeline-journal.md`, filed from **`BL-0180`**
(`refactor`, `SCHEDULED`).

## 2. Objective

`docs/pipeline/pipeline-journal.md` has grown to 541KB across 285 run-log rows (runs #0-284).
The file's own charter forbids deleting old rows, so it only grows; reading "where are we now"
pays the cost of the entire project's run history. Split into a live file (Position + a recent
run-log window) and an archive file (older runs, verbatim) with a cross-link.

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

Unaffected.

## 5. Interfaces

- **New file `docs/pipeline/pipeline-journal-archive.md`** — contains: a short header explaining
  it is the archive for runs #0-239, a link back to the live journal, the same table header, and
  runs #0-239 verbatim (the exact lines from the pre-refactor file, including any incidental
  blank lines or non-numeric run IDs already present in that range — nothing normalized).
- **`docs/pipeline/pipeline-journal.md`** — unchanged: title, intro, Position section (lines
  1-404 of the pre-refactor file). Run log section: table header kept, followed by a short
  archive-pointer note, followed by runs #240-284 verbatim (unchanged content, just the
  older rows removed from this file).
- **`.claude/skills/00-pipeline-manager/SKILL.md`** — "## The journal" section gains one sentence
  describing the archive convention (retention window, where older runs go), so future runs
  follow the same pattern instead of letting the live file re-grow unbounded.

## 6. Files to Create/Modify

- **Create:** `docs/pipeline/pipeline-journal-archive.md`
- **Modify:** `docs/pipeline/pipeline-journal.md` (trim), `.claude/skills/00-pipeline-manager/SKILL.md` (document convention)

## 7. Implementation Tasks

Ordered: (1) capture baseline byte/line count of the pre-refactor file; (2) extract runs #0-239
(lines 405-647) into the new archive file with its own header; (3) trim the live file, replacing
those lines with a pointer note; (4) confirm byte-for-byte accounting (archive body + live body
== original Run-log body, modulo the small added header/pointer text); (5) update
`00-pipeline-manager/SKILL.md`; (6) link-integrity check across the tree (grep for
`pipeline-journal.md` references — none point to a specific run/anchor, so no other file needs
editing); (7) commit.

## 8. Tests to Add

**None.** No automated test suite covers documentation prose; the equivalence proof is the
byte-accounting check in §7 plus a manual spot-check that both files render as valid Markdown
tables.

## 9. Documentation Updates

`.claude/skills/00-pipeline-manager/SKILL.md` (per §5/§6) — the only doc besides the two journal
files themselves that needs a substantive edit.

## 10. Definition of Done

- Archive file exists, contains runs #0-239 verbatim.
- Live file retains Position section unchanged and runs #240-284 verbatim, plus a pointer to the
  archive.
- Byte-for-byte accounting confirms zero content loss.
- `00-pipeline-manager/SKILL.md` documents the new convention.

## 11. Verification Checklist

- [ ] Archive file's row count + live file's recent-row count == 285 (the original total).
- [ ] Spot-check: several archived rows' full text byte-identical to the pre-refactor file.
- [ ] Position section byte-identical to the pre-refactor file (untouched).
- [ ] Link integrity: no broken reference introduced anywhere in the tree.

## 12. Dependencies

None.

## 13. Risks

- **Silent truncation during extraction** (Low, mitigated): byte-accounting check in §7/§11
  catches any dropped content immediately.
- **Future runs re-growing the live file unbounded again** (Low): mitigated by documenting the
  convention in `00-pipeline-manager/SKILL.md` so the pattern repeats.

## 14. Rollback Considerations

Revert both files' git history; delete the new archive file.
