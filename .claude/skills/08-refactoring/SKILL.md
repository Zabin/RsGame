---
name: 08-refactoring
description: Execute exactly one approved, eligible refactoring-scoped Implementation Package (IP-8xx0) — behavior-preserving restructuring of code (any repo-root .py the package names) and/or meaning-preserving restructuring of documentation under docs/ — capture a baseline (ROM hash + full test_rom.py results) before the first edit, refactor in small reversible steps, prove equivalence afterward (byte-identical ROM or the package's enumerated predicted deltas; full suite green; doc statuses/decisions/IDs meaning-unchanged; link integrity), update traceability and any migration map, and advance the package on the Master Build Plan. Use when asked to "refactor X," "restructure/reorganize the docs," "rename Y across the tree," "pay down structural debt," or "implement IP-8xxx" where the package names this skill. Stage-08 peer of 08-code-implementation and 08-content-authoring; it never changes behavior, never fixes bugs (even ones it finds — those go to intake), never adds features, and is never pre-authorized (G3 bootstrap carve-out does not apply). Verification to VERIFIED belongs to 09-package-verification.
---

# Refactoring

Executes **one approved, eligible refactoring-scoped Implementation Package**: restructuring that
leaves the game's behavior and the documentation's meaning **provably unchanged**. The third
stage-08 peer — where `08-code-implementation` changes what the code *does* and
`08-content-authoring` changes what the game *shows*, this skill changes only how code and docs
are *organized*, and carries the burden of proving that's all it changed.

Grounding: [`R307`](../../../docs/research/encyclopedia/R307-refactoring-practices.md)
(behavior-preserving refactoring, characterization/golden-master testing, doc-tree refactoring).

## What this is for (and what it is not)

One question: *given one refactoring package, what is the smallest sequence of
structure-only changes that achieves the package's stated shape — with evidence, not assertion,
that nothing observable changed?*

It SHALL NOT: change any observable game behavior · fix any bug, even a one-liner it trips over
(file it via `00-intake` as an Outstanding Issue — a refactor that "also fixes" something has
destroyed its own equivalence proof) · add features, tests-of-new-behavior, or abstractions the
package doesn't name · change the meaning of any requirement, spec, decision, status, or research
claim while moving/renaming it · redesign architecture (a structure that can't be reached without
a behavior change is a Blocking Report, not a license) · write `VERIFIED` (stage 09's exclusive
transition).

Authoritative read-only inputs: the Master Build Plan · the package · the `BL-xxxx` it cites ·
GDS-03/07/09 + ADRs (boundaries a refactor must respect) · R307.

**Write scope (G1):** exactly the files the package names — which may be any repo-root `*.py`
(the code/content peer seam does not bind here **because the equivalence proof is stronger**: a
byte-identical ROM demonstrates no content changed, by construction) and/or any files under
`docs/` (structure, filenames, links, formatting — never meaning). A refactoring package whose
predicted ROM delta is anything other than "byte-identical" must enumerate every expected delta
and why it is behavior-neutral; if it can't, the work isn't a refactor and belongs to a different
package.

## Eligibility (all five, checked before the first edit)

1. **Package.** A refactoring-scoped `IP-8xx0` exists (authored by `07-implementation-planning`,
   citing its `BL-xxxx`), status exactly `READY`, every dependency `VERIFIED`.
2. **Authorization (G3, strict).** Explicit user go-ahead on record for *this* package.
   Refactoring is **never** covered by the bootstrap carve-out — structural change is always the
   user's call.
3. **Quiescence.** No other package is `IN PROGRESS`, and no `COMPLETE`-but-unverified package
   touches any file this package names — refactoring under a moving tree makes both the refactor
   and the pending verification unprovable.
4. **Green baseline.** The G5 gates pass on the tree *as found* (ROM builds at 32768 bytes,
   valid header; full `test_rom.py` passes). **Never refactor on red** — a failing baseline makes
   "the suite still passes" meaningless.
5. **Equivalence contract.** The package states its proof obligation: byte-identical ROM (the
   default), or an enumerated list of predicted byte deltas with per-delta justification; for
   doc-scoped work, the meaning-preservation constraints and (if IDs/files move) the required
   migration map.

If any check fails: stop, report which one and who owns it. No consolation work.

## Workflow

### Step 1 — Select and gate-check

As `08-code-implementation` Step 0–1, plus the five eligibility checks above.

### Step 2 — Read the package; verify its claims against the tree

Every field. Confirm every file/function/label/doc-section the package cites still exists as
described — material drift is a **Blocking Report**, never routed around.

### Step 3 — Mark `IN PROGRESS`, then capture the baseline

Update the Master Build Plan first. Then, before any edit, record in the scratchpad:
the built ROM's SHA-256 · the full `test_rom.py` output (check count and every check name) ·
for doc-scoped work, the inventory the package names (e.g. every `BL-`/`FR-`/`IP-` status token,
every ID, the link set of the affected files). This baseline is the other half of the
equivalence proof; a refactor without one is unverifiable.

### Step 4 — Refactor in small, separately-buildable steps

Apply the package's tasks as a sequence of mechanical transformations (R307 §5), keeping the
tree buildable between steps where practical. Code: rename/extract/move/inline only — any edit
whose justification begins "while I'm here" is out of scope. Docs: move/split/merge/rename/relink
only — every moved claim keeps its wording or the package explicitly lists the permitted
editorial normalizations; statuses and decisions are copied character-for-character.

### Step 5 — Prove equivalence (G5 + the contract)

```
python3 build_rom.py <out.gbc>   # must write 32768 bytes, valid header
python3 test_rom.py              # full suite — same checks, same passes as the baseline
```

Compare against Step 3: ROM hash identical (or every delta matches the package's enumerated
prediction — an unpredicted delta is a **failed refactor**, revert or block, never rationalize
post-hoc) · test count not reduced, no check renamed without the package saying so · doc
inventory identical in meaning (every status token and ID accounted for) · no dangling links
anywhere in `docs/` to a moved/renamed file (sweep the whole tree, not just the files edited —
inbound links break silently).

### Step 6 — Traceability and the migration map

Update every reference the restructuring invalidated: INDEX files, RTM rows, `Claude.md`/
`memory.md` quick-reference tables (if a name or path they cite moved), the package's cited
`BL-xxxx`. If IDs or filenames changed, write the old→new migration map where the package says
(so future greps for the old name find the trail).

### Step 7 — Ledger, summary, stop

Set the package `COMPLETE` (never `VERIFIED`). Present the **Refactoring Summary**: Package ·
Files Modified/Moved/Deleted · Equivalence Evidence (baseline hash vs. post hash, or the
delta-by-delta reconciliation; suite counts before/after; doc-inventory result) · Migration Map
(or "names stable") · Outstanding Issues (bugs/smells found but **not** fixed, for intake).
**Stop** — one package per invocation.

## Blocking conditions

Stop immediately — no partial work left in the tree — when: any eligibility check fails · cited
files/sections have materially drifted · the target shape can't be reached without changing
behavior or meaning · an unpredicted ROM delta or test regression appears and can't be reverted
to a clean intermediate step. Produce a **Blocking Report** (Reason · Evidence · Required action ·
Recommended owner), set the package `BLOCKED`, revert to the last provably-equivalent state, and
end the run.

## Quality checklist (before presenting `COMPLETE`)

- [ ] All five eligibility checks passed and are cited in the summary (authorization explicitly,
      never assumed).
- [ ] Baseline captured **before** the first edit; equivalence compared against it, not against
      memory.
- [ ] ROM byte-identical, or every delta matches the package's enumerated prediction.
- [ ] Full `test_rom.py` green with no reduction in checks; no behavior-bearing test weakened.
- [ ] Zero behavior/meaning changes rode along — every diff hunk is structural; bugs found were
      filed, not fixed.
- [ ] No dangling link in `docs/` to anything moved/renamed; migration map written if names
      changed.
- [ ] Master Build Plan shows `COMPLETE`; summary matches the actual diff.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 08 — Package Execution** of the documentation-driven-development pipeline
(see [`.claude/skills/README.md`](../README.md)). Peers: `08-code-implementation` (behavior
changes), `08-content-authoring` (art/screens/music data). Upstream: `07-implementation-planning`
(refactoring packages enter via `refactor`-type backlog entries — see `00-intake`; the manager's
explicit scheduling conditions are in `00-pipeline-manager`). Downstream: `09-package-verification`
(re-checks the equivalence evidence; the only skill that may write `VERIFIED`).

The Refactoring Summary carries the run's factual record; in the same closing message,
additionally state:

1. **Recommendations** — every Outstanding Issue (bug/smell found-not-fixed) with its suggested
   owner; any follow-up refactor the package deliberately deferred.
2. **Next step** — after `COMPLETE`, always `09-package-verification` on this same package
   (ideally a fresh session, for independence); after a Blocking Report, whatever its Required
   action names.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
