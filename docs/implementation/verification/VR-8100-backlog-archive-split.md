# VR-8100 — Backlog Archive Split

## Package

- **ID:** IP-8100 — [Backlog Archive Split](../packages/IP-8100-backlog-archive-split.md) (refactor, doc-scope)
- **Verified:** 2026-07-20, same session as the implementing edit.

## Independence note

**Degraded independence, explicitly accepted** — same basis as the prior refactors this session.

## Result

**VERIFIED** — 0 findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Archive file exists, contains every `DONE`/`REJECTED` row verbatim | `backlog-archive.md` created, 117 rows; full `diff` against the pre-refactor file's own `DONE`/`REJECTED` rows → empty | PASS |
| Live file retains every open-status row verbatim, plus updated header text and a pointer | 65 rows retained (`SCHEDULED`/`DEFERRED`/`IN PIPELINE`); full `diff` against the pre-refactor file's own open-status rows → empty; header updated per plan | PASS |
| Row-for-row accounting confirms zero content loss | 117 archived + 65 live = 182 = original total row count | PASS |
| `00-pipeline-manager/SKILL.md` documents the new convention | "## The backlog" section gains an "Archiving (`IP-8100`...)" paragraph | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Archive row count + live row count == original total | 117 + 65 = 182 | PASS |
| Every row in the live file has an open status | Programmatic partition by the actual trailing Status-field text (not a naive column-index split, since two pre-existing rows — `BL-0127`/`BL-0128` — have a missing pipe that merges Disposition prose into the Status field; the true terminal status token was matched by suffix, e.g. "...end to end.** DONE" correctly resolves to `DONE`) confirms every live row's status is one of `NEW`/`SCHEDULED`/`DEFERRED`/`NEEDS-USER`/`IN PIPELINE` | PASS |
| Every row in the archive has `DONE` or `REJECTED` status | Same partition logic; archive count 117 `DONE`, 0 `REJECTED` (no rejected entries exist in this backlog) | PASS |
| Spot-check rows byte-identical to pre-refactor file | Full `diff` (not sampling) on both halves → empty in both directions | PASS |
| Link integrity | `docs/pipeline/backlog.md`'s own header now links `backlog-archive.md`; `docs/INDEX.md` updated; grep confirms no other file references a specific `BL-xxxx` row location that would break | PASS |

## Test run

```
diff <(python3 partition-by-status.py --archive) backlog-archive.md's own body
  → empty

diff <(python3 partition-by-status.py --live) backlog.md's own body
  → empty

117 (archive) + 65 (live) = 182 (original total)
```

No `test_rom.py` involvement — pure documentation, no ROM/behavior surface.

## Scope audit

`docs/pipeline/backlog.md` (trimmed + header text updated), `docs/pipeline/backlog-archive.md`
(new), `.claude/skills/00-pipeline-manager/SKILL.md` (one paragraph added), `docs/INDEX.md` (one
link added). No other file touched. No row's own content altered — only relocated.

## Findings

None. (Noted but out of scope: two pre-existing rows, `BL-0127`/`BL-0128`, are each missing a
pipe delimiter between their own Disposition and Status columns, causing the Status field's text
to include trailing Disposition prose. Both still resolve unambiguously to `DONE` and were
correctly archived; fixing the malformed pipe itself would be a separate, narrower fix, not part
of this package's own archive-split scope.)
