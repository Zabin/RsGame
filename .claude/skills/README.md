# The documentation-driven-development skill pipeline (Bunny Garden Adventure)

The numbered skills in this directory form one pipeline. **The number is the run order**: a
skill's inputs are produced by lower-numbered stages, and its output feeds the next higher stage.
Skills sharing a number (the three `02-research-*` skills; the two `08-*` peers; the two `09-*`
peers) are peers at the same stage — run whichever owns the gap; they have no ordering among
themselves. Unnumbered skills (`run-bunnygarden`) are utilities outside the pipeline.

Every pipeline skill ends **every** run with a mandatory chat summary: what changed,
recommendations (findings routed to their owning skill), and an explicit **Next step** naming the
skill to run next. The default way to drive the pipeline is `00-pipeline-manager`: it keeps a
persistent journal at `docs/pipeline/pipeline-journal.md` (position + append-only run log,
reconciled against the tree's real ledgers every run — the tree always wins), executes the next
step by invoking the owning skill, and stops at every human gate. Running a stage skill directly
is always legitimate too — the manager's next `sync` picks up the change.

**Nothing surfaced is forgotten:** every finding/recommendation an invoked skill reports is
harvested by the manager into `docs/pipeline/backlog.md` at the end of the run, and every open
backlog entry is triaged (given an explicit disposition — scheduled / deferred-with-trigger /
needs-user / rejected) at the start of the next run, before the next step is chosen. New work
enters the same backlog through `00-intake` (features, bugs, observations — classified, deduped,
and routed to the pipeline stage where they belong), never by side-channel implementation.

**First increment (bootstrap):** this project already ships a working game (`BunnyGarden.gbc`,
v2.1 — see `Claude.md` and `memory.md`). The pipeline's first pass through stages 01–07 is
therefore **as-built baselining**: each stage derives its artifacts from the shipped game and the
existing developer docs, not from user interviews. No stage may block on "ask the user what the
game should be" during the baseline increment — the shipped ROM is the answer. New scope enters
afterward via `00-intake`. See `docs/pipeline/BOOTSTRAP.md` for the exact run order and the few
prompts a human must supply.

## Stages

| # | Skill | Produces | Where |
|---|---|---|---|
| 00 | `00-pipeline-manager` · `00-intake` | Manager: pipeline journal (position + run log), backlog harvest + triage, one-step-per-run execution of the next stage (`status`/`triage`/`log`/`sync`/`run` modes). Intake: files new features/bugs/observations into the backlog with a recommended entry stage. | `docs/pipeline/`, chat |
| 01 | `01-vision` | Program vision (MSTR-001), GDS-00 Vision, strategic assumptions register | `docs/master/`, `docs/architecture/` |
| 02 | `02-research-gbc-hardware` · `02-research-game-design` · `02-research-tooling-and-testing` | Research encyclopedia tiers R100 (GBC hardware/SM83) / R200 (game design) / R300 (tooling, emulation & verification) | `docs/research/` |
| 03 | `03-architecture-design-synthesis` | GDS-01…10 ladder (Concept of Play, System Context, Architecture, Domain Model, FR/NFR levels, Data Model, Presentation Architecture, Interface Spec, RTM level), ADS-xxx, ADRs | `docs/architecture/` |
| 04 | `04-requirements-engineering` | FR-xxxx, NFR-xxxx, Requirements Review, Requirements Traceability Matrix | `docs/requirements/` |
| 05 | `05-feature-decomposition` | Release Plan, Epic Catalog, Feature Catalog (FEAT-xxxx rows), Feature Dependency Graph, Feature Review | `docs/feature-planning/` |
| 06 | `06-feature-specification` | Feature Specifications (FS-xxx, 20-field template) | `docs/features/` |
| 07 | `07-implementation-planning` | Technical Work Breakdown, Implementation Packages (IP-xxxx, 14-field template), Master Build Plan | `docs/implementation/` |
| 08 | `08-code-implementation` · `08-content-authoring` | Code: source + tests + docs + traceability for exactly one package (status → `COMPLETE`). Content peer: tile art, screen layouts, music data (the data halves of `tiles.py`/`tilemaps.py`/`music.py`) + their verification tests. | repo-root `*.py`, ledgers |
| 09 | `09-package-verification` · `09-content-review` | Verification Report (VR-xxxx); the **only** skill that writes `VERIFIED`. Content peer: Content Review report (visual/audio/layout correctness vs. spec) under `docs/reviews/`. | `docs/implementation/verification/`, `docs/reviews/` |
| 10 | `10-integration-review` | Integration Report for an epic/release's verified package set | `docs/reviews/` |
| 11 | `11-release-readiness` | Release Assessment (GO/NO-GO) + baseline update on GO | `docs/reviews/`, trackers |

## Iteration loops

The pipeline is iterative, not a one-way waterfall — but every loop re-enters at a numbered stage
and flows forward from there:

- **Per feature:** 06 → 07 → (08 → 09 per package) — repeated for each feature in a release bucket.
- **Per package:** 08 → 09; a `RETURNED` verification loops back to 08 on the same package.
- **Per content artifact:** `08-content-authoring` → `09-content-review`; findings loop back to 08.
- **Per release:** 10 → 11; integration findings loop back through 07 → 08 → 09 before 10 re-runs.
- **Upstream findings never get fixed downstream.** A requirements conflict found at stage 05 goes
  back to 04; an architecture gap found at 06 goes back to 03; a domain-knowledge gap anywhere
  goes to the owning 02 skill. Each skill's summary routes its findings to the owning stage.

## Hard rules the stages share (interim governance — formalized later as MSTR-006)

Until `01-vision`/`03-architecture-design-synthesis` author the `docs/master/` MSTR corpus, the
rules below are the binding governance text. Skills cite them as **G1–G5**.

- **G1 — Write scope.** Each skill writes **only** its own output scope and reads everything
  upstream as authoritative. No skill before 08 writes production code; no skill after 08 fixes
  code (findings route back). Within stage 08, the peers split the write surface: only
  `08-code-implementation` writes game logic and build machinery (`asm_game.py`, `gbc_lib.py`,
  `build_rom.py`, `test_rom.py`); `08-content-authoring` writes only the data halves of
  `tiles.py`/`tilemaps.py`/`music.py` and their verification tests.
- **G2 — Status honesty.** Statuses are honest ledgers. The vocabulary is exactly
  `NOT STARTED / READY / IN PROGRESS / BLOCKED / COMPLETE / VERIFIED`. Stage 08 may write
  `IN PROGRESS`/`COMPLETE`/`BLOCKED`; only stage 09 writes `VERIFIED`; only the user's explicit GO
  lets 11 flip the baseline.
- **G3 — Package authorization.** A fully-specified package is **not** authorization to build it —
  the user grants that explicitly, per package. **Standing exception for the bootstrap increment:**
  as-built baseline packages (documentation of code that already ships) and remediation packages
  for bugs already recorded in `docs/pipeline/backlog.md` at scaffold time (BL-0001…BL-0005) are
  pre-authorized; anything else waits for the user.
- **G4 — Release GO.** The GO/NO-GO recommendation at stage 11 is advisory; the user makes the
  release call before any baseline record flips.
- **G5 — Permanent gates.** After every stage-08 run, the ROM must build
  (`python3 build_rom.py <path>` → 32768 bytes, valid header) and the full ROM test suite
  (`python3 test_rom.py`) must pass. A package that breaks either is not `COMPLETE`, regardless of
  what its own new tests show. See `run-bunnygarden` for the exact commands.
