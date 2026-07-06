---
name: 03-architecture-design-synthesis
description: Synthesize the vision (GDS-00/MSTR-001) and research grounding (encyclopedia R1xx-R3xx) into Design Synthesis documents under docs/architecture/ — either the global, gated GDS-00…GDS-10 ladder (Vision → Concept of Play → System Context → Architecture → Domain Model → Functional Requirements → Non-functional Requirements → Data Model → Presentation Architecture → Interface Specification → Requirements Traceability Matrix) or a per-capability-cluster ADS-xxx document, the bridge between vision+research and a Feature Specification. Also owns ADR-xxxx Architecture Decision Records under docs/architecture/adr/. Use when asked "what are the core concepts," "which mechanics are actually required," "which requirements conflict," "what assumptions must be made," to advance the next level of the GDS ladder, to record an ADR, or to produce a design synthesis before drafting or revising an FS-xxx. This produces design documents, not research documents — do not use it to add new hardware/design/tooling claims (that's the 02-research-* skills) — and no code.
---

# Architecture / Design Synthesis

Produces three kinds of document under `docs/architecture/`, all tracked in
[`docs/architecture/INDEX.md`](../../../docs/architecture/INDEX.md):

1. **The global ladder (`GDS-00`…`GDS-10`)** — one instance for the whole project, strictly
   sequential and gated. (`GDS-00` Vision is the exception: owned by `01-vision`; this skill
   authors `GDS-01` onward and hands any Vision-layer edit to `01-vision`.) The ladder is
   scaffolded with stub files carrying each level's Purpose and merge gate; the next unauthored
   `GDS-NN` is the default thing to work on when invoked without a more specific target.
2. **Per-cluster `ADS-xxx`** — zero-or-more documents, one per capability cluster with real
   design tension the ladder doesn't resolve at the system level.
3. **ADRs (`docs/architecture/adr/ADR-xxxx-slug.md`)** — dated, numbered records of binding
   design decisions (e.g. "single 32KB bank, no MBC bank switching," "Python assembler over
   RGBDS," "shadow-OAM DMA every frame"). On the bootstrap increment, mine `Claude.md`/
   `memory.md`/the code for the decisions already made and record them as as-built ADRs.

## The ladder levels (this project's names)

| Level | Content | Merges from (as-built sources) |
|---|---|---|
| GDS-00 Vision | owned by `01-vision` | `MSTR-001` |
| GDS-01 Concept of Play | who plays, the session shape, the core loop (explore → collect → gift → victory), state machine at player altitude | `Claude.md` Known Good Behavior |
| GDS-02 System Context | the ROM, the build pipeline, the emulator/verification harness, real-hardware aspirations, external constraints | `Claude.md`, `test_rom.py` |
| GDS-03 Architecture | module decomposition (`gbc_lib`/`tiles`/`tilemaps`/`music`/`asm_game`/`build_rom`), one-job-per-file rule, patch-point contract | `Claude.md` §Architecture Overview |
| GDS-04 Domain Model | game entities: zones, screens, collectibles, gifts, score, save-game, game states | `Claude.md`, `memory.md` |
| GDS-05 Functional Requirements | capability-level FRs the requirements baseline elaborates | `Claude.md` Known Good Behavior, `test_rom.py` suites |
| GDS-06 Non-functional Requirements | ROM budget (32KB), VBlank timing discipline, save integrity, build determinism, test-coverage bar | `test_rom.py`, `Claude.md` |
| GDS-07 Data Model | ROM section layout, WRAM map, SRAM save format, tile index map, palette tables | `Claude.md` §Data layout, `memory.md` quick-refs |
| GDS-08 Presentation Architecture | screens, sprite composition, palette assignment strategy, HUD, audio engine shape | `memory.md`, `tiles.py`/`tilemaps.py`/`music.py` |
| GDS-09 Interface Specification | the module contracts: `build_game_asm(rom) → patches dict`, `build_tile_data()`, `ALL_SCREENS`, `ZONE_COLLECTS`, `music_data()`, `ROM` class surface | the code itself |
| GDS-10 Requirements Traceability Matrix level | how traceability is carried (defers detail to `docs/requirements/`) | `docs/requirements/` once authored |

## What this is for (and what it is not)

This skill answers, before a Feature Specification can commit to a shape: What are the core
concepts? Which mechanics are actually required vs. nice-to-have? Which candidate requirements
conflict, and how is the conflict resolved? What assumptions must be made explicit? What is the
minimum viable implementation? What is deferred?

It consumes `docs/research/` as **input**, never as something it adds to. If a synthesis reveals
a genuine domain-knowledge gap, that gap is handed to the owning `02-research-*` skill to close
first. It produces **design documents, not research documents**: synthesis, decision, and
explicit tradeoffs, citing its grounding — never re-deriving it.

**Not every feature needs an ADS.** A small/uncontested feature can go straight to `FS-xxx` —
the FS author absorbs the synthesis into that document's own §1–2. Reach for an ADS when a
capability cluster has real design tension: conflicting candidate requirements, multiple
plausible architectures, or load-bearing assumptions nobody has written down.

## Workflow A — the global ladder (default)

1. **Find the next unauthored level** in `docs/architecture/INDEX.md` §1 (first row still
   `⛔ Planned (scaffold only)`). Levels must be done in order — never jump ahead.
2. **Confirm the gate on the *previous* level is actually closed** — every merge-gate box checked
   and the merge decision recorded in prose in that document. If not, finish that gate first.
3. **Author the level's content**, replacing its stub body, pulling in the "merges from" sources
   named above — pull the actual content in, don't cite it from a distance. On the bootstrap
   increment this is as-built documentation: describe the shipped design, and record real
   tensions as Open Questions rather than silently "fixing" the design on paper.
4. **Close the level's merge gate**: check each box and record the actual merge decision (does
   the merged-from text in `Claude.md`/`memory.md` become a pointer to this level, stay
   authoritative, or split?).
5. **Update the level's Status** (`✅`, or `🚧` if the merge isn't fully closed — in which case
   the next level still may not start) in both `docs/architecture/INDEX.md` §1 and `ROADMAP.md`,
   together, so they never drift.
6. **Cross-link** the merged-from documents if the merge decision calls for it.
7. **Commit** as `docs(architecture): GDS-NN — <what changed>`. **Stop at the level just closed**
   — one level per pass unless explicitly asked otherwise.

## Workflow B — per-cluster ADS-xxx

1. Identify the capability cluster; which R-xxx topics ground it; whether an FS-xxx would consume
   it.
2. Check `docs/architecture/INDEX.md` §2 for existing coverage; if a gap exists, add the index
   row (`⛔ Planned`) before writing — index-before-content.
3. Draft the ten fixed sections, in order: Executive Design Overview · System Architecture ·
   Domain Model · User Stories · Functional Requirements · Non-functional Requirements ·
   Constraints · Risks · Open Questions · Decision Log.
4. Metadata block: Dependencies (the R-xxx it synthesizes), Produces (the FS-xxx it feeds).
   ~8–15 pages; split `ADS-xxxA`/`ADS-xxxB` rather than sprawl.
5. Cross-link both directions, flip status, update INDEX + ROADMAP together, commit as
   `docs(architecture): ADS-xxx — <what changed>`.

## Workflow C — ADRs

One decision per `ADR-xxxx` file: Context · Decision · Status (accepted/superseded) ·
Consequences. Add the row to `docs/architecture/adr/INDEX.md`. ADRs are append-only history —
supersede, never rewrite.

## Quality gate

- [ ] (Ladder) The previous level's merge gate was verified closed before this level started, and
      this level's own gate is closed with the decision recorded in prose.
- [ ] (ADS) All ten sections present, in order, none a placeholder; every FR traces to a cited
      R-xxx/GDS source; Open Questions genuinely open, decisions in the Decision Log.
- [ ] No production code, no literal byte layouts where the level doesn't call for them.
- [ ] `docs/architecture/INDEX.md` and `ROADMAP.md` updated in sync.
- [ ] No new research claims originated here — gaps routed to the owning `02-research-*` skill.

## Gotchas

- Don't let this skill become a backdoor for adding research content — it cites, it doesn't
  originate domain knowledge.
- Never start `GDS-(N+1)` before `GDS-N`'s merge gate is fully closed with the decision recorded
  in prose.
- The ladder layers on top of `Claude.md`/`memory.md` — those stay authoritative until a level's
  merge step explicitly folds their content in and records that decision. Keep `Claude.md` as
  the working developer quick-reference even after merging; the merge decision says which
  document carries which statement.
- An ADS's Decision Log is the load-bearing artifact for whoever drafts the downstream FS-xxx —
  an unrecorded decision effectively didn't happen.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 03 — Architecture & Design Synthesis** of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream: `01-vision` and the
`02-research-*` skills. Downstream: `04-requirements-engineering`.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — every GDS level/ADS/ADR produced or updated (paths), every merge gate
   closed, every index/ROADMAP status flipped.
2. **Recommendations** — Open Questions raised, domain-knowledge gaps handed to `02-research-*`,
   tensions with the shipped code flagged, and who owns each follow-up.
3. **Next step** — if a domain-knowledge gap blocked this run, name the owning `02-research-*`
   skill, then re-invoke this skill; if more GDS levels remain unauthored, re-invoke this skill
   for the next level (one level per pass); once the levels the current increment needs are
   authored with closed gates, advance to `04-requirements-engineering`.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
