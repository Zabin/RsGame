---
name: 00-pipeline-manager
description: Run the documentation-driven-development pipeline one step at a time with persistent memory — reconcile the pipeline journal (docs/pipeline/pipeline-journal.md) against the tree's real ledgers, triage the pipeline backlog (docs/pipeline/backlog.md — every finding/recommendation harvested from prior runs plus 00-intake-filed features/bugs, each needing an explicit disposition before the next step is chosen), determine the single next step, execute it by invoking the owning numbered skill (01-vision through 11-release-readiness), harvest the invoked skill's findings into the backlog, append the run to the journal, and report what to do next. Modes: no args = advance one step; "status" = read-only survey + recommendation; "triage" = backlog triage only; "log" = show the journal; "sync" = reconcile only; "run <skill> [target]" = execute a specific step out of recommended order (journaled as an override). Use when asked to "run the pipeline," "run the pipeline skill," "do the next step," "continue where we left off," "where are we / what's next," "triage the backlog," or "show the pipeline log." It always stops at human gates (G3 package authorization, release GO/NO-GO, Critical review findings) and asks rather than proceeding; it performs no stage work itself beyond invoking the owning skill.
---

# Pipeline Manager

The **driver** for the documentation-driven-development pipeline. Where each numbered skill knows
how to do *its* stage, this skill knows *where the pipeline is* and *what is still owed*: it keeps
a persistent journal of position, a persistent backlog of findings and requests, reconciles both
against reality, executes the next step by invoking the owning skill, and logs what happened — so
"continue the pipeline" works across sessions without re-deriving everything, and nothing a
previous run surfaced is ever silently forgotten.

It performs **no stage work itself**. It reads ledgers, invokes exactly one owning skill per
advance, and writes exactly two files of its own: the journal and the backlog. A manager that
starts doing the stages' work stops being trustworthy about where the pipeline is.

## The journal — `docs/pipeline/pipeline-journal.md`

The manager's persistent memory of **position**. Two parts:

1. **Position block** (rewritten every run):

   ```markdown
   ## Position
   - **Updated:** <date> (run #N)
   - **Increment:** <what body of work the pipeline is currently driving>
   - **Pipeline state:** <one line per stage that isn't ✅ idle-and-current — what's open where>
   - **Backlog:** <N open entries (IDs), which are due at/before the next step — or "none open">
   - **Next step:** `<skill>` on <target> — <one-line why>
   - **Open gates:** <human decisions pending: authorizations, GO calls, unadjudicated findings — or "none">
   ```

2. **Run log** (append-only, newest last — never rewrite or delete old rows):

   ```markdown
   | # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
   ```

   One row per manager run, including `status`/`sync`/`triage` runs (skill invoked = `—`) and runs
   that stopped at a gate (outcome = `GATE: <what's needed>`), so the log shows stalls, not just
   wins.

## The backlog — `docs/pipeline/backlog.md`

The manager's persistent memory of **obligations**: every finding, recommendation, Outstanding
Issue, and Open Question a stage skill's run surfaced, plus every feature request and bug report
filed by the `00-intake` skill. One table, `BL-xxxx` IDs, append entries / update statuses in
place, never delete rows (rejected entries stay, marked `REJECTED` with the reason).

| Field | Content |
|---|---|
| **ID** | `BL-xxxx`, sequential |
| **Filed** | Date + source (which run/VR/report/intake produced it) |
| **Type** | `feature` / `bug` / `finding` / `recommendation` / `design-question` / `gate` / `research-gap` / `doc-defect` |
| **Summary** | One sentence; link the source artifact |
| **Sev/Pri** | The source's severity, or the user's stated priority for intake items |
| **Entry stage** | The pipeline stage where the item enters when worked (e.g. a code bug → `07`, a spec gap → `06`, a research gap → `02`) |
| **Disposition** | The manager's recorded decision on *when* it will be addressed (see lifecycle) |
| **Status** | `NEW` → `SCHEDULED` / `DEFERRED` / `NEEDS-USER` → `IN PIPELINE` → `DONE` / `REJECTED` |

**Writers:** this skill (harvest + triage + status flips) and `00-intake` (appends `NEW` entries).
Stage skills never write the backlog — their findings reach it through this skill's harvest step,
which is what guarantees a finding stated in a chat summary survives the session that stated it.

**Every open entry carries a live disposition.** `SCHEDULED` names the step it rides with;
`DEFERRED` names its revisit trigger; `NEEDS-USER` names the exact decision required. "We'll get
to it" with no trigger is not a disposition.

## Modes

| Invocation | Behavior |
|---|---|
| *(no args)* | **Advance**: reconcile → triage backlog → determine next step → gate-check → invoke the owning skill → harvest + journal → report. One step per run. |
| `status` | Read-only: reconcile in-memory, print the stage survey + backlog summary + recommendation. No writes unless drift was found and the user confirms syncing it. |
| `triage` | Backlog only: harvest anything un-harvested from the last run, put a disposition on every `NEW` entry, re-check `DEFERRED` triggers and `NEEDS-USER` questions. No skill invoked. |
| `log` | Print the Position block, the last ~10 run-log rows, and open backlog entries; no writes. |
| `sync` | Reconcile journal + backlog against the ledgers; invoke nothing. Use after doing pipeline work outside the manager. |
| `run <skill> [target]` | Execute a specific step even if it isn't the recommendation (still gate-checked, never gate-bypassed). Journaled with mode `override` and the recommendation it superseded. |

## Workflow (advance mode)

### Step 1 — Read the journal and backlog, then reconcile against the ledgers

Read `docs/pipeline/pipeline-journal.md` and `docs/pipeline/backlog.md` (create either with an
initialization entry if absent). Verify the Position block against the authoritative ledgers —
cheapest-first, always including the ledgers that bear on the recorded next step:

`ROADMAP.md` · `docs/architecture/INDEX.md` §1 (GDS ladder) · `docs/requirements/` +
`docs/reviews/` (baseline + findings state) · `docs/feature-planning/01-release-plan.md` +
`05-feature-review.md` · `docs/features/INDEX.md` ·
`docs/implementation/00-master-build-plan.md` + `packages/INDEX.md` ·
`docs/implementation/verification/` · `docs/reviews/integration-review-*` +
`release-assessment-*`.

Drift (a status the journal didn't expect, work done outside the manager, a `VERIFIED` with no
Verification Report, a backlog item the tree shows already resolved) is corrected now and noted in
this run's log row.

### Step 2 — Triage the backlog (review the last run's findings before choosing anything)

This step is **mandatory before Step 3**:

1. **Late harvest.** If the previous run's log row references findings that never became backlog
   entries, add them now (`NEW`, sourced to that run).
2. **Disposition every `NEW` entry.** For each, decide and record: fold into the upcoming step
   (`SCHEDULED`, naming the step), schedule at a named later point (`SCHEDULED`), defer with an
   explicit revisit trigger (`DEFERRED`), require a user decision (`NEEDS-USER`), or reject with a
   reason (`REJECTED`). Severity honesty applies: a Critical/High finding may not be quietly
   `DEFERRED` — that disposition needs the user's explicit agreement.
3. **Re-check standing entries.** Any `DEFERRED` trigger now fired → back to `NEW` for a fresh
   disposition. Any `SCHEDULED` entry whose ride is this run's likely next step → tag it so Step 4
   passes it into the invoked skill's target. Any entry the tree shows resolved → `DONE`.
4. **Batch the user questions.** Collect all `NEEDS-USER` entries that are ripe into Step 4's gate
   check so the user answers once, not five times.

### Step 3 — Determine the single next step

From the reconciled position **and the triaged backlog**, pick the highest-leverage unblocked
step, using the pipeline's ordering rules (see `README.md`): upstream findings before downstream
work; a due backlog item outranks new scope at the same stage; within a stage, critical-path
first; the per-feature loop (06→07→08→09) drains before the per-release stages (10→11) run. If
the journal's recorded next step is still valid and no due backlog entry outranks it, that's the
default. If several steps are genuinely parallel, pick one and name the others in the report.

**During the bootstrap increment** (see `docs/pipeline/BOOTSTRAP.md`), the ordering is simply the
first stage whose baseline artifacts don't exist yet, 01 upward.

### Step 4 — Gate check (hard stops — ask, never assume)

Before invoking anything, stop and ask the user (via `AskUserQuestion`) if the step requires:

- **G3 authorization** — the step would implement a package with no explicit user go-ahead on
  record **and** the package is not covered by G3's bootstrap exception (as-built baselining, or a
  remediation package for BL-0001…BL-0005);
- **a release GO** — the step would flip baseline records;
- **adjudication** — the step builds on a review with unadjudicated Critical/High findings;
- **a ripe `NEEDS-USER` backlog entry** — the decision the entry is waiting on is needed now;
- **spending judgment the user reserved** — anything a stage skill's own rules say needs the user.

A gate stop is a complete, successful run: journal it (`GATE: …`), record the user's answers in
the backlog/journal when they come, report what decision unblocks the pipeline, and end.

### Step 5 — Execute by invoking the owning skill

Invoke the owning numbered skill via the `Skill` tool with the specific target — including any
`SCHEDULED` backlog entries riding this step. Follow that skill's own rules completely — the
manager adds no shortcuts and removes no obligations. One skill invocation per advance run.

### Step 6 — Harvest, then journal the run

**Harvest first, while the invoked skill's completion summary is still in context:** every
finding, recommendation, Outstanding Issue, and Open Question it reported becomes a backlog entry
(`NEW`, sourced to this run) unless one already exists (then update that entry). Flip to `DONE`
any backlog entry this step resolved.

Then append the run-log row and rewrite the Position block from the post-run state, including the
backlog line. Commit the journal + backlog together (and nothing else — the invoked skill
committed its own work per its own conventions).

### Step 7 — Report

The mandatory completion summary (below), always ending with what the *next* advance will do —
so the user can simply run the manager again.

## Guardrails

- **One step per advance.** No chaining "while I'm here." The journal makes stopping cheap.
- **No finding left in chat.** If a stage skill said it, the backlog holds it — harvest is part
  of the run, not an optional courtesy.
- **Never bypass a gate**, even in `run <skill>` override mode. Overrides change *which* step
  runs, never *whether* a human decision is required.
- **Never perform stage work inline.** If the next step looks "too small to bother invoking the
  skill for," invoke the skill anyway.
- **Never edit any ledger the stages own.** Drift between a ledger and reality is routed to the
  owning skill; the manager only corrects its *own* journal and backlog.
- **The journal and backlog are honest or they are useless.** A run that failed, stalled, or hit
  a gate is journaled as exactly that.

## Quality gate (every run)

- [ ] The journal and backlog were read first, and the Position block was verified against the
      real ledgers — not trusted blind.
- [ ] Every `NEW` backlog entry left this run with a recorded disposition, and no Critical/High
      entry was deferred without the user's explicit agreement.
- [ ] The invoked skill's findings were harvested into the backlog before the run ended.
- [ ] Exactly one skill was invoked (or zero, for status/log/sync/triage/gate runs).
- [ ] Every gate the step touched was stopped at and asked about — none assumed.
- [ ] The run-log row, Position block, and backlog updates were written and committed, and match
      what actually happened this run.
- [ ] Nothing outside `docs/pipeline/` was written by the manager itself.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 00 — the manager**; it can be run at any time and is the default entry point
for all pipeline work (its stage-00 peer `00-intake` files new features/bugs into the backlog this
skill triages). End **every** run — advance, status, triage, log, sync, override, or gate stop —
with a chat summary containing exactly these three parts:

1. **What happened** — mode, skill invoked (if any) and its outcome in one line, journal row
   appended, backlog deltas (harvested / dispositioned / closed, by ID), any drift corrected.
2. **Recommendations** — open gates awaiting the user, `NEEDS-USER` backlog entries and the exact
   decisions they need, parallel steps available, drift found and who owns it.
3. **Next step** — what the next `/00-pipeline-manager` advance will execute (skill + target +
   any backlog entries riding along + why), or the exact decision needed if the pipeline is gated
   on the user.

Never end a run without naming the next step — that line is the whole point of having a manager.
