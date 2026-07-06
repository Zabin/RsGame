# Bootstrap run-book — how to drive this pipeline from zero

This file is the instruction set for the implementing agent (and the human pressing the button).
The scaffold is complete; **no pipeline artifact content has been authored yet** — every index is
`⛔ Planned`, the journal sits at run #0, and five backlog items (BL-0001…BL-0005) are `NEW`.
Everything below is executed by the skills themselves; the human's job is to repeat one prompt
and answer the few listed gates.

## The one prompt

> **run the pipeline skill**

(or `/00-pipeline-manager` — same thing). Each invocation advances **exactly one step**: the
manager reconciles, triages the backlog, picks the next step, invokes the owning skill, harvests
findings, journals, and ends by naming what the next run will do. Repeat until the journal's
Position block says the increment is complete. Any wording that asks to run/continue the pipeline
works; the manager re-derives position from the journal + ledgers every time, so sessions can
end and resume freely.

## Expected bootstrap sequence (what those runs will do)

The manager derives this itself; it's listed so a human can sanity-check progress. Roughly 25–35
advance runs:

1. **`01-vision`** (1 run) — MSTR-001, GDS-00, assumptions register, from the shipped game.
2. **`02-research-*`** (≈3 runs, one per tier, more if topics are split across runs) — author the
   R100/R200/R300 topics the index plans. If a session lacks web access, topics are authored with
   "needs fetch-verification" flags and a backlog entry — that is expected, not a failure.
3. **`03-architecture-design-synthesis`** (10 runs — one GDS level per run, GDS-01…GDS-10, gates
   closed in order) plus 1 run for the as-built ADR set. BL-0002/BL-0004 ride along where triage
   schedules them (sprite strategy at GDS-08; build-chain canonicalization at GDS-03 — BL-0004
   needs the user answer first, see Gates).
4. **`04-requirements-engineering`** (1 run) — FR/NFR/Review/RTM from the ladder + `test_rom.py`.
5. **`05-feature-decomposition`** (1 run) — release plan (everything shipped → the
   "Baseline (as-built)" bucket), epics, FEAT catalog, dependency graph, review.
6. **`06-feature-specification`** (1 run per baseline feature, ≈8–10 runs) — as-built FS-101….
7. **`07-implementation-planning`** (1–2 runs) — as-built packages (entering at `COMPLETE`,
   pending verification) + remediation packages for BL-0001/BL-0003/BL-0005 (pre-authorized by
   G3's bootstrap carve-out).
8. **`08-code-implementation` / `09-package-verification`** loops — implement each remediation
   package, then verify it (verification ideally in a fresh session for independence); then
   retro-verify the as-built packages one per run.
9. **`10-integration-review`** (1 run) on the baseline tranche.
10. **`11-release-readiness`** (1 run) — Release Assessment for the "Baseline (as-built)" bucket.
    **Stops at the G4 gate for the user's GO.**

After the bootstrap increment, new work enters only via `00-intake` ("file this bug/feature…"),
and the same one-prompt loop drives it through.

## Gates — the only prompts the human must answer

The manager stops and asks (via `AskUserQuestion`) at every human gate. During bootstrap, expect
exactly these:

| When | What is asked | Example answer that unblocks |
|---|---|---|
| First triage (run #1) | **BL-0004:** which build chain is canonical, and what happens to `BunnyGarden_build_rom.py` + `BunnyGarden_logic.json`? | "Modular chain is canonical; move the monolith and JSON to `legacy/` with a README note." |
| Stage 11 | **G4 release GO** for the Baseline (as-built) bucket | "GO" (or "NO-GO" with concerns) |
| Any non-carve-out package | **G3 authorization** — only if new scope was intaken mid-bootstrap | "Authorize IP-xxxx" |

Everything else runs without user input: the skills' bootstrap modes explicitly derive content
from the shipped ROM, `Claude.md`, `memory.md`, and `test_rom.py` instead of interviewing the
user, and genuine ambiguities become register assumptions / Open Questions / backlog entries
rather than blocking questions.

## Standing rules for the implementing agent

- **One step per run; never chain stages.** The journal makes stopping cheap.
- **Never bypass a gate**, even when the answer seems obvious.
- **The tree wins over the journal** — reconcile first, every run.
- **G5 after every stage-08 run:** ROM builds at exactly 32768 bytes with a valid header, and the
  full `test_rom.py` suite passes (see `run-bunnygarden` for commands and the BL-0005 path
  workaround).
- **Findings never die in chat** — the manager harvests them into `docs/pipeline/backlog.md`.
- Commit per the skills' own conventions (`docs(vision): …`, `docs(architecture): GDS-NN — …`,
  `docs(pipeline): run #N — …`, etc.); push to the session's designated branch.
