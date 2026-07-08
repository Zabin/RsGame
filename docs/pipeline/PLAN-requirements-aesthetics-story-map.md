# PLAN — Path to a Requirements Baseline for Aesthetics, Story, and World Map

- **Document type:** increment plan (pipeline run-book companion, like
  [`BOOTSTRAP.md`](BOOTSTRAP.md))
- **Date:** 2026-07-08 · **Status:** proposed — awaiting user adoption; nothing in this plan is
  itself an authorization to do work (see §7)
- **Goal:** a traceable, reviewed **requirements baseline delta** (RQ-01…RQ-04 under
  `docs/requirements/`) covering three new work streams — **(A) aesthetic quality**, **(B) a
  developed story line**, **(C) a developed, expanded world map** — produced by the existing
  documentation-driven pipeline, not around it.
- **Terminal state of this plan:** stage 04 complete for the increment. Decomposition into
  Features (05), specs (06), packages (07), and implementation (08+) continue afterward under
  the pipeline's normal cadence and are out of this plan's scope.

[↑ Docs index](../INDEX.md) · [Backlog](backlog.md) · [Journal](pipeline-journal.md) ·
[Pipeline README](../../.claude/skills/README.md)

---

## §1 Where each stream must enter the pipeline

The pipeline's rule is that work enters at the highest stage whose artifacts it invalidates or
extends. The three streams are *not* at the same altitude, and treating them as one flat "make
the game nicer" request would misroute them:

| Stream | What exists today | What's missing | Entry stage |
|---|---|---|---|
| **A — Aesthetic quality** | Research is substantially done: [R202](../research/encyclopedia/R202-8bit-game-feel.md) (game feel), [R203](../research/encyclopedia/R203-screen-composition-tile-grid.md) (composition), [R208](../research/encyclopedia/R208-palette-color-design.md) (palette design), [R209](../research/encyclopedia/R209-pixel-art-technique.md) (pixel-art technique), [R210](../research/encyclopedia/R210-ai-assisted-tile-art-workflow.md) (agent art workflow), [R211](../research/encyclopedia/R211-acclaimed-gbc-visual-design-case-studies.md) (GBC case studies) — all filed via BL-0013 at the project owner's request. [GDS-08](../architecture/08-presentation-architecture.md) documents presentation *as built*. | A **vision-level quality commitment** (MSTR-001 has no "the game must look good" commitment — §2 Phase 1), a **normative** presentation standard (GDS-08 describes what is, not what "good" must mean), and measurable **NFRs** derived from R209/R211's heuristics. | **01** (one-line vision commitment) → **03** (GDS-08 delta / ADS cluster) → **04** |
| **B — Story line** | Almost nothing. The shipped game has a title/intro flow and a victory screen; no dialog, no characters, no narrative framing. MSTR-001 §1/§3 do not mention story at all — narrative is **new vision-level scope**, the most expensive kind of change in the tree (MSTR-001 §7). No R2xx research topic covers narrative design; no text/dialog engine exists in `asm_game.py`. | Everything: vision amendment, research grounding (narrative + text rendering + text tooling), domain/data/presentation architecture deltas, then requirements. | **01** (vision amendment) → **02** (new research topics) → **03** → **04** |
| **C — World map** | The strongest starting position: MSTR-001 **C7** already commits to a Zelda/Pokémon-class overworld; bank-switching is already un-non-goaled ([ADR-0001](../architecture/adr/ADR-0001-single-bank-rom-no-mbc-switching.md) names its own supersession trigger); [R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md) grounds MBC1 banking; FP-01's Future bucket already says exactly what's missing: *"decomposing this into Features requires a 03 pass to scope the bank-switching architecture first, then a 04 delta to derive concrete FRs."* | The **BL-0015 decision** ("wider vs deeper" — deliberately DEFERRED until "the C7 expansion is actually planned," which is *this plan*; it becomes NEEDS-USER now), the bank-switching ADR, generalization of `_zone_arrows()` adjacency, a palette strategy under the 8-BG-palette ceiling (BL-0009/GDS-08), then FRs. | **03** (BL-0015 → NEEDS-USER, architecture deltas + ADRs) → **04** |

Stream B is the pacing item: it is the only one that starts from a genuine vision change and a
genuine research gap. Streams A and C can run ahead of it through stage 03 if desired.

## §2 Phased path

### Phase 0 — Close the bootstrap so the delta lands on a truthful floor

A requirements delta layered onto a baseline with known defects inherits them. Before extending
the baseline:

1. **Finish the bootstrap increment:** implement + verify `IP-9030` (root-doc refresh, BL-0007
   — the last open package), then `10-integration-review` over the five VERIFIED packages, then
   `11-release-readiness` for Release 1. (This is already the journal's recorded next step.)
2. **Land the standing 04-delta batch** — BL-0020 (missing sprite-rendering FR), BL-0022
   (FR-3200 postcondition is factually wrong), BL-0026 (NFR-6100 RTM cell), BL-0028 (stale
   verification hedges) — one `04-requirements-engineering` pass, exactly as those entries are
   already SCHEDULED. Doing this first means the increment's own 04 pass extends a *clean*
   RQ-01…04, and the two passes stay reviewable as separate deltas.

**Exit:** Release 1 assessed; RQ-01…04 accurate with zero SCHEDULED stage-04 doc-defects.

### Phase 1 — Intake and vision (stages 00–01)

1. **File the increment through `00-intake`** as three backlog entries (one per stream, so each
   can be triaged, gated, and closed independently), with the entry stages from §1. Filing is
   not a decision to build (G3 still applies later); it puts the scope where the pipeline
   manager can see and sequence it. §4 shows the intake rows.
2. **One deliberate `01-vision` amendment (v2.0 → v3.0)** covering all three streams in a
   single dated pass with one blast-radius enumeration, rather than three micro-amendments:
   - **Story:** add a commitment naming narrative as in-scope — what kind of story (framing
     premise, character(s), dialog, an ending that recontextualizes the 9-carrot victory) at
     purpose level only, constrained by C6 (family-friendly, casual). **User decision required**
     on story shape/tone — see §5.
   - **Aesthetics:** add a quality commitment (e.g. "the game's visual and audio presentation
     is a first-class, reviewed deliverable held to the standards synthesized from R209/R211"),
     giving downstream NFRs a vision anchor.
   - **Map:** no new commitment needed — C7 already exists; the amendment records that C7's
     expansion is now *being planned* (its "direction, not fixed target" caveat gets a first
     concrete milestone once BL-0015 is decided).
   - Update the strategic-assumptions register (A1's 32KB framing, A5's content constraints as
     they now bind dialog text).

**Exit:** MSTR-001 v3.0 + GDS-00 refreshed and consistent; three BL entries triaged SCHEDULED;
the BL-0015 and story-shape decisions captured as NEEDS-USER with named questions.

### Phase 2 — Research grounding (stage 02)

Only genuine gaps — the aesthetics tier is already built, and re-research is waste:

| Skill | New/updated topics | Grounds |
|---|---|---|
| `02-research-game-design` | **R212 (proposed) — GB-era narrative & dialog design:** how story is delivered in acclaimed GB/GBC games at this scale (Link's Awakening's framing premise, Oracle games' NPC economy, environmental storytelling), story pacing for short sessions, dialog-box conventions on the 20×18 grid, text speed/interaction feel. **R213 (proposed) — world topology & overworld design:** screen-graph topologies beyond a 3×3 grid, landmark/biome sequencing, map-screen design at larger scales — written to serve whichever way BL-0015 is decided. Light updates to R201/R206 if story beats become progression gates. | B, C |
| `02-research-gbc-hardware` | Audit pass, likely small: text rendering is ordinary BG-tile work already covered by R102/R103; confirm whether the **window layer** (dialog box overlay) and any story-flag SRAM growth need topic extensions rather than new topics. Bank-switching research (R106) exists. | B, C |
| `02-research-tooling-and-testing` | Extension to R302/R305 or one new topic: **text content pipeline** — font tile set, string encoding/storage in the Python assembler, patch-point patterns for dialog data, and how to *test* dialog (screenshot assertions on rendered text, WRAM story-flag assertions). Revisit **BL-0014** (no image→tile importer) only if the aesthetics stream decides to start from reference images — it stays DEFERRED otherwise, per its recorded trigger. | B, A |

**Exit:** every claim the Phase 3 architecture deltas will need is citable to an R-topic.

### Phase 3 — Architecture synthesis (stage 03)

The GDS ladder exists; this phase is **deltas plus ADRs**, per level, in ladder order:

- **Decisions first:** resolve **BL-0015 (wider vs deeper)** — a NEEDS-USER gate, presented
  with the palette-ceiling and adjacency-generalization consequences already recorded on that
  entry. This decision shapes everything below; do not start GDS deltas before it.
- **GDS-01 (Concept of Play):** how story and the expanded world change the play loop (dialog
  interactions, story-gated progression if any, session shape under a bigger world).
- **GDS-03 (Architecture) + ADRs:** the **bank-switching ADR** superseding ADR-0001 (MBC1 ROM
  banking strategy, what lives in which bank); a **text/dialog engine ADR** (window layer vs BG
  overlay, font tile budget, string encoding); a **map-topology ADR** (generalizing
  `_zone_arrows()`'s hardcoded 3×3 adjacency to whatever BL-0015 chose).
- **GDS-04 (Domain Model):** new entities — story flags, dialog/script, NPC (if any), expanded
  Zone graph; extend the one-carrot-per-zone rule's treatment (BL-0017's standing checklist
  rule) to whatever the new zone count is.
- **GDS-07 (Data Model):** WRAM/SRAM layout for story flags and the larger world; **save-format
  version bump**, reusing FS-101's version-byte + pre-upgrade-default pattern (BL-0021's
  resolved precedent).
- **GDS-08 (Presentation Architecture):** the normative aesthetic standard — per-terrain-family
  palette plan under the 8-BG-palette ceiling (BL-0009's corrected picture), tile-art quality
  criteria distilled from R209/R211 into reviewable checklist form (this is what
  `09-content-review` will later judge against), dialog-box presentation, audio direction.
- **GDS-09/GDS-10:** interface spec deltas (new patch points, text data module boundaries) and
  RTM-level refresh.
- Use **ADS-xxx per-cluster documents** if any single stream's delta outgrows a ladder-level
  edit (the story/text engine is the likeliest candidate).

**Exit:** GDS ladder internally consistent at the new scope; every open design question either
decided (ADR/user record) or explicitly parked with a named trigger.

### Phase 4 — Requirements engineering (stage 04) — the deliverable

One `04-requirements-engineering` increment pass deriving, per stream:

- **A:** measurable aesthetic **NFRs** (palette-budget compliance, tile readability criteria
  per GDS-08's standard, content-review acceptance thresholds) plus any FRs for new
  presentation behavior (e.g. animated environment tiles if GDS-08 adopts them).
- **B:** story **FRs** — dialog trigger/render/dismiss behavior, story-flag state machine,
  intro/ending sequences, story-flag persistence in the save (extending FR-5220's pattern) —
  and NFRs (text speed, dialog latency, C6-derived content constraints).
- **C:** world **FRs** — zone count/topology per the BL-0015 decision, traversal at the new
  scale, map-screen behavior beyond 3×3, per-zone collectible rules at the new count — and
  NFRs (bank-budget headroom watching, extending BL-0019's convention; load/transition timing).
- **RQ-03 review** of the merged baseline (conflicts, gaps, duplicates — e.g. story-gating vs
  the "no fail states" assumption A5) and **RQ-04 RTM** rows for every new requirement, each
  traceable back to a GDS section and forward to (initially UNASSIGNED) tests.

**Definition of done for this plan:** RQ-01…04 updated and internally reviewed; every new
FR/NFR traces to a GDS-ladder section and an R-topic; open questions resolved or carried as
dispositioned backlog entries; the pipeline journal records the increment. Stage 05 then
decomposes the delta into FEAT-xxxx rows and populates FP-01's currently-empty Release 2+
buckets — outside this plan.

## §3 Sequencing at a glance

```
Phase 0   IP-9030 → 10-integration-review → 11-release-readiness ─┐
          04-delta batch (BL-0020/0022/0026/0028) ────────────────┤
                                                                  ▼
Phase 1   00-intake (3 BL entries) → triage → 01-vision v3.0  [user: story shape]
                                                                  ▼
Phase 2   02-research: R212/R213 + tooling/hardware audit (B,C heavy; A none)
                                                                  ▼
Phase 3   BL-0015 decision [user: wider vs deeper] → GDS-01/03/04/07/08/09/10 deltas + 3 ADRs
                                                                  ▼
Phase 4   04-requirements delta (FR/NFR per stream) → RQ-03 review → RQ-04 RTM   ◄── DONE
```

Streams A and C can reach Phase 3 while B is still in Phase 2 research; the pipeline manager's
one-step-at-a-time cadence decides the interleaving at triage, not this plan.

## §4 How the pipeline intakes user stories and backlog items

This increment adds no new intake machinery — it *rides* the existing one, and every future
user story for aesthetics/story/map goes through the same door:

1. **Single entry point:** `00-intake` is the only way work enters. It classifies the request
   (feature / bug / research-gap / design-question / doc-defect / observation), gathers cheap
   read-only evidence for bugs, checks BL-0001+ for duplicates, determines the **entry stage**,
   and appends a `NEW` row to [`backlog.md`](backlog.md). Intake never implements, and filing
   an item is never a decision to build it.
2. **Triage:** `00-pipeline-manager` dispositions every open entry at the start of its next
   run — `SCHEDULED` (rides a named step), `DEFERRED` (named revisit trigger), `NEEDS-USER`
   (named decision), or `REJECTED` (reason kept). Critical/High entries may not be DEFERRED
   without explicit user agreement. Rows are never deleted.
3. **Routing rule for entry stage** (the same rule §1 applied to the three streams):

   | User story looks like… | Intake type | Entry stage |
   |---|---|---|
   | "As a player I want the game to have a story/opening/ending…" | feature (vision-scope) | **01** — narrative isn't in MSTR-001 yet (until Phase 1 lands; afterwards story features enter at 04/06 under the new commitment) |
   | "As a player I want more regions / a bigger world / region X…" | feature (C7 scope) | **03** until the Phase-3 architecture exists, then **04**; after Phase 4, new-zone requests within the decided topology enter at **06** as ordinary Features |
   | "As a player I want the forest to look less flat / better sprite art…" | feature or design-question | **03** (GDS-08 standard) before Phase 3; **06** afterwards (content Feature judged against the standard); pure craft questions → **02** research gap |
   | "The dialog box renders garbage when…" (post-implementation) | bug | **07** — remediation package, per the standing bug route |
   | "The new zone's palette clashes / text is unreadable" | finding | **09-content-review** finding → harvested to backlog → routed back to 08 |
   | "We don't know how GBC games usually do X" | research-gap | **02** (the BL-0013 → R209/R210/R211 pass is the worked precedent) |
4. **Findings loop back automatically:** stage skills never write the backlog; the manager
   harvests every run's findings/recommendations into it. Phase 2–4 runs will therefore
   *generate* new backlog entries (exactly as GDS/RQ authoring generated BL-0015/0017/0019/
   0020/0022), and those ride later triage — the plan does not need to pre-enumerate them.
5. **Mid-increment stories:** user stories arriving while this plan is in flight are filed the
   same way and triaged into the increment where they fit (e.g. a story-beat idea files as NEW,
   entry 03 or 04 depending on phase) or DEFERRED with the next release as trigger. Vision-level
   pivots remain expensive by design (MSTR-001 §7) and get a deliberate 01 pass, never a quiet
   scope-fold.

**Seed intake rows for Phase 1** (final wording/IDs are `00-intake`'s call, not this plan's):

| Proposed entry | Type | Sev/Pri | Entry stage |
|---|---|---|---|
| Stream A — adopt a normative aesthetic standard and derive measurable presentation requirements | feature | Medium | 01 (commitment) → 03 |
| Stream B — add a developed story line (premise, dialog, ending) to Bunny Quest | feature (vision-scope) | Medium | 01 |
| Stream C — plan the C7 world-map expansion to a concrete first milestone | feature (C7) | Medium | 03 (unpauses BL-0015 as NEEDS-USER) |

## §5 Human gates and user decisions

| Gate | Phase | Decision |
|---|---|---|
| Adopt this plan | now | Whether to run Phases 0–4 as the next increment after Release 1 closes. |
| Release 1 GO/NO-GO (G4) | 0 | Normal `11-release-readiness` gate. |
| Story shape & tone | 1 | Premise, whether NPCs/dialog exist, how the ending relates to the 9-carrot victory — bounded by C6 (family-friendly). |
| **BL-0015: wider vs deeper** | 3 | The recorded deferral trigger ("when the C7 expansion is actually planned") fires at this plan's Phase 3. Decides topology, palette strategy, and bank-switching shape. |
| G3 package authorization | after 4 | Unchanged: no stage-08 work from this increment starts without explicit authorization, regardless of anything this plan says. |

## §6 Constraints the requirements must respect (already on record)

- **ROM budget:** 23404/32768 bytes used (~9.1KB headroom, BL-0019) — story text + a bigger
  world will not fit in one bank; the bank-switching ADR is on the critical path for both B
  and C.
- **Palette ceiling:** 8 BG palettes, 5 already serving terrain families (BL-0009/GDS-08) —
  the binding constraint on "wider" world growth and on aesthetic ambitions alike.
- **Save format:** any new persisted state (story flags, more zones) bumps the FS-101
  version byte and defines pre-upgrade-save defaults (BL-0021 precedent).
- **Domain invariants:** exactly one carrot per zone is a *tested* property (T1.11, BL-0017)
  — zone-count changes must update the invariant and its test together.
- **G5 permanent gate:** every eventual implementation package re-runs the full suite; the
  requirements should be written test-derivable (R305's discipline) so stage-08 work stays
  verifiable.
- **C6:** all story/aesthetic content stays family-friendly, all-ages.

## §7 What this plan is not

It is a **map, not a mandate**: it does not file backlog entries (that's `00-intake`'s write
scope), does not amend the vision (that's a deliberate `01-vision` run), does not decide
BL-0015, and does not authorize any package (G3). Adopting it means: finish Phase 0, then feed
§4's three seed rows to `00-intake` and let `00-pipeline-manager` drive the phases one step at
a time, journaled as always.
