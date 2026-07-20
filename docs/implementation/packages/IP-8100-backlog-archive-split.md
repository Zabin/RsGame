# IP-8100 — Backlog Archive Split

> Owned by `07-implementation-planning` (definition) / `08-refactoring` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).
> **Refactoring package — meaning-preserving documentation restructuring only.**

## 1. Package ID

`IP-8100` — refactors `docs/pipeline/backlog.md`, filed from **`BL-0181`** (`refactor`,
`SCHEDULED`).

## 2. Objective

`docs/pipeline/backlog.md` has grown to 377KB across ~182 entries, roughly two-thirds already
`DONE`/`REJECTED`. The file's own stated purpose is active triage; closed entries add zero
triage value while dominating the file. Split into a live file (open-status entries) and an
archive file (closed entries, verbatim).

## 3. Requirements Covered

None — structural only.

## 4. Architecture Components

Unaffected.

## 5. Interfaces

- **New file `docs/pipeline/backlog-archive.md`** — header explaining it is the archive for
  `DONE`/`REJECTED` entries, a link back to the live backlog, the same table header, and every
  `DONE`/`REJECTED` row verbatim, in original ID order.
- **`docs/pipeline/backlog.md`** — keeps its Lifecycle section unchanged; its intro header gains
  one clause describing the new archive convention ("resolved entries flip to `DONE` and move to
  the archive file at the next triage sweep; rejected ones likewise"), replacing the now-narrower
  "rows are never deleted" framing with "rows are never deleted, only archived once resolved."
  Entries table keeps only `NEW`/`SCHEDULED`/`DEFERRED`/`NEEDS-USER`/`IN PIPELINE` rows, in
  original ID order.
- **`.claude/skills/00-pipeline-manager/SKILL.md`** — "## The backlog" section gains one sentence
  describing the archive convention, so future harvest/triage steps move newly-`DONE`/`REJECTED`
  rows to the archive instead of leaving them live indefinitely.

## 6. Files to Create/Modify

- **Create:** `docs/pipeline/backlog-archive.md`
- **Modify:** `docs/pipeline/backlog.md` (header text + row removal), `.claude/skills/00-pipeline-manager/SKILL.md`

## 7. Implementation Tasks

Ordered: (1) capture baseline: exact row count and per-status counts; (2) partition every row by
its Status column into archive vs. live sets, preserving original ID order within each; (3) write
the archive file; (4) rewrite the live file's Entries table with only open-status rows, and its
header text per §5; (5) confirm accounting: archive rows + live rows == original total, no row's
own text altered (only relocated); (6) update `00-pipeline-manager/SKILL.md`; (7) link-integrity
check; (8) commit.

## 8. Tests to Add

**None.** Equivalence proof is the row-accounting check in §7 plus a diff confirming every
`DONE`/`REJECTED` row's text is byte-identical between the pre-refactor file and its new archive
location.

## 9. Documentation Updates

`.claude/skills/00-pipeline-manager/SKILL.md` (per §5/§6).

## 10. Definition of Done

- Archive file exists, contains every `DONE`/`REJECTED` row verbatim.
- Live file retains every open-status row verbatim, plus updated header text and a pointer to the
  archive.
- Row-for-row accounting confirms zero content loss.
- `00-pipeline-manager/SKILL.md` documents the new convention.

## 11. Verification Checklist

- [ ] Archive row count + live row count == original total row count.
- [ ] Every row in the live file has an open status (`NEW`/`SCHEDULED`/`DEFERRED`/`NEEDS-USER`/`IN PIPELINE`).
- [ ] Every row in the archive has `DONE` or `REJECTED` status.
- [ ] Spot-check several rows byte-identical to the pre-refactor file in their new location.
- [ ] Link integrity: no broken reference introduced anywhere in the tree.

## 12. Dependencies

None.

## 13. Risks

- **Miscategorizing a row's status during the partition** (Low, mitigated): the row-accounting
  and status-check in §11 catch this mechanically — any row landing in the wrong file with the
  wrong status fails the check immediately.
- **Future runs not adopting the new archive convention** (Low): mitigated by documenting it in
  `00-pipeline-manager/SKILL.md`.

## 14. Rollback Considerations

Revert both files' git history; delete the new archive file.
