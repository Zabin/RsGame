# PLAN — Path to a Requirements Baseline for Aesthetics, Story, and World Map

- **Document type:** increment plan (pipeline run-book companion, like
  [`BOOTSTRAP.md`](BOOTSTRAP.md))
- **Date:** 2026-07-08 · **Revised:** 2026-07-08 (v2 — incorporates the project owner's
  direction in §0; supersedes v1's dialog-centric story stream and handcrafted-map assumption)
- **Status:** proposed — awaiting user adoption; nothing in this plan is itself an
  authorization to do work (see §8)
- **Goal:** a traceable, reviewed **requirements baseline delta** (RQ-01…RQ-04 under
  `docs/requirements/`) covering three new work streams — **(A) aesthetic quality**, **(B) a
  visual story narrative**, **(C) a deterministic, seed-driven procedurally generated world
  map** — produced by the existing documentation-driven pipeline, not around it.
- **Terminal state of this plan:** stage 04 complete for the increment. Decomposition into
  Features (05), specs (06), packages (07), and implementation (08+) continue afterward under
  the pipeline's normal cadence and are out of this plan's scope.

[↑ Docs index](../INDEX.md) · [Backlog](backlog.md) · [Journal](pipeline-journal.md) ·
[Pipeline README](../../.claude/skills/README.md)

---

## §0 Project owner direction on record (2026-07-08)

Verbatim-in-substance decisions from the project owner, which this plan and every downstream
stage must honor. The `01-vision` amendment (Phase 1) formalizes them; they are recorded here
first so no phase re-litigates them:

- **D1 — No text dialogue requirement now.** Text dialogue is *not explicitly ruled out*, but
  it is not presently a requirement. Nothing on this increment's critical path may depend on a
  text/dialog engine.
- **D2 — The story narrative is visual.** Story is told through the world itself: similar zone
  themes **flow into each other** rather than hard-cutting at transitions, and the goal of
  collecting **child-friendly items follows the visual narrative**. The owner does not dictate
  the specific items (carrots and presents are examples, not requirements). **The agent decides
  how to construct the narrative flow, grounded in research** — not by fiat.
- **D3 — The map is a deterministic procedurally generated world from a user-modifiable
  seed.** The same seed always produces the same world. Research must cover **procedural map
  generation algorithms** and **existing GBC homebrew games that use procedurally generated
  maps**; **the agent decides, from that research, the most efficient implementation approach**
  — the owner does not dictate the algorithm.
- **D4 — Quality bar:** the result must be **smooth**, and **every screen/room/view must be
  clean** (no visual garbage, no incoherent tile seams).

D1/D2 resolve v1's open "story shape & tone" user gate. D3 reshapes the deferred BL-0015
"wider vs deeper" question (see §6). D4 is the seed of this increment's headline NFRs.

## §1 Where each stream must enter the pipeline

The pipeline's rule is that work enters at the highest stage whose artifacts it invalidates or
extends. The three streams are *not* at the same altitude:

| Stream | What exists today | What's missing | Entry stage |
|---|---|---|---|
| **A — Aesthetic quality** | Research is substantially done: [R202](../research/encyclopedia/R202-8bit-game-feel.md) (game feel), [R203](../research/encyclopedia/R203-screen-composition-tile-grid.md) (composition), [R208](../research/encyclopedia/R208-palette-color-design.md) (palette design), [R209](../research/encyclopedia/R209-pixel-art-technique.md) (pixel-art technique), [R210](../research/encyclopedia/R210-ai-assisted-tile-art-workflow.md) (agent art workflow), [R211](../research/encyclopedia/R211-acclaimed-gbc-visual-design-case-studies.md) (GBC case studies) — all filed via BL-0013. [GDS-08](../architecture/08-presentation-architecture.md) documents presentation *as built*. | A **vision-level quality commitment** (MSTR-001 has no "the game must look good" commitment), a **normative** presentation standard (GDS-08 describes what is, not what "good" must mean), and measurable **NFRs** derived from R209/R211's heuristics plus D4's smooth/clean bar. | **01** (commitment) → **03** (GDS-08 delta) → **04** |
| **B — Visual story narrative** | Zones are visually distinct but **hard-cut** at screen edges — exactly what D2 replaces. No narrative framing exists; MSTR-001 §1/§3 never mention story, so narrative is **new vision-level scope** (MSTR-001 §7). Adjacent research exists (R203 composition, R208 palettes, R211 case studies) but no topic covers **wordless environmental storytelling** or **biome-transition design**. Per D1, no text/dialog engine is needed — v1's text-engine ADR and text-pipeline research drop off the critical path entirely. | Vision amendment naming the visual narrative; research on how tile-based games tell stories without words (biome flow, landmark beats, item theming); architecture for **transition blending** between themes; **item-agnostic** re-statement of the collect-goal (D2: the "carrot" is an example, not a requirement). | **01** (vision amendment) → **02** → **03** → **04** |
| **C — Procedural world map** | MSTR-001 **C7** already commits to a much larger world; bank-switching is already un-non-goaled ([ADR-0001](../architecture/adr/ADR-0001-single-bank-rom-no-mbc-switching.md) names its own supersession trigger); [R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md) grounds banking. **Nothing** covers procedural generation: no research on seeded generation under 8-bit constraints, no PRNG in the codebase, and the current world is a hand-authored 3×3 grid with hardcoded adjacency (`_zone_arrows()`, R203). | D3's named research (procgen algorithms; GBC homebrew procgen case studies), a **generator architecture decision** (agent-decided per D3, recorded as an ADR), a **seed model** (user modification surface, persistence in the save), determinism guarantees, and the fate of the handcrafted 3×3 world (a C5 protected-baseline question — §6). | **02** (research first — the algorithm decision is downstream of it) → **03** → **04** |

Stream C's ordering differs from v1: research now *precedes* architecture as the pacing item,
because D3 explicitly makes the algorithm choice research-derived.

## §2 Phased path

### Phase 0 — Close the bootstrap so the delta lands on a truthful floor

Unchanged from v1. Before extending the baseline:

1. **Finish the bootstrap increment:** implement + verify `IP-9030` (root-doc refresh,
   BL-0007), then `10-integration-review`, then `11-release-readiness` for Release 1.
2. **Land the standing 04-delta batch** (BL-0020/0022/0026/0028) as one
   `04-requirements-engineering` pass, so the increment's own 04 pass extends a *clean*
   RQ-01…04 and the two deltas stay separately reviewable.

**Exit:** Release 1 assessed; RQ-01…04 accurate with zero SCHEDULED stage-04 doc-defects.

### Phase 1 — Intake and vision (stages 00–01)

1. **File the increment through `00-intake`** as three backlog entries (one per stream), with
   the entry stages from §1 and §0's decisions attached as the on-record user direction. §5
   shows the seed rows. Filing is not a decision to build (G3 still applies later).
2. **One deliberate `01-vision` amendment (v2.0 → v3.0)** covering all three streams in a
   single dated pass with one blast-radius enumeration:
   - **Story (D1/D2):** a commitment that the game tells its story **visually** — zone themes
     flow into one another, and progression is read from the world, not from text; the
     collect-goal is restated **item-agnostically** ("one child-friendly key item per region,
     themed to its biome; collecting all of them wins") with carrots as the current instance,
     not the requirement. Text dialogue recorded as a non-goal *at this vision's date* (D1's
     "not ruled out" phrasing preserved).
   - **Aesthetics (D4):** a quality commitment — presentation is a first-class, reviewed
     deliverable; every screen/room/view clean; transitions smooth.
   - **Map (D3):** C7 gains its first concrete shape — the world is **deterministically
     generated from a user-modifiable seed**. This amendment must explicitly work through
     **C5's protected-baseline consequence**: the shipped handcrafted 3×3 world is superseded
     by generated worlds — a deliberate, recorded change, with the residual question (does a
     default seed ship, and is any homage to the handcrafted world kept?) either decided here
     or carried as a named NEEDS-USER entry.
   - Update the strategic-assumptions register (A1's 32KB framing under generated content; A5
     as it binds item theming; a new assumption for emulator-stable determinism).

**Exit:** MSTR-001 v3.0 + GDS-00 refreshed; three BL entries triaged SCHEDULED; residual
decisions (default seed, seed-entry surface) captured as NEEDS-USER with named questions.

### Phase 2 — Research grounding (stage 02)

The increment's heavy research phase — D2 and D3 both explicitly delegate design decisions to
research-grounded agent judgment, so this phase is what makes those decisions legitimate:

| Skill | New/updated topics | Grounds |
|---|---|---|
| `02-research-game-design` | **R212 (proposed) — wordless environmental storytelling & biome-transition design:** how tile-based GB/GBC-class games convey narrative without text (landmark beats, visual foreshadowing, theme evolution across adjacent areas); concrete **transition-blending techniques** on a 20×18 tile grid (border/ecotone tile sets, palette stepping between terrain families, shared intermediate tiles); **collectible theming** — what reads as a child-friendly "key item" per biome at 8×8/2bpp, and how item identity supports the narrative flow (D2). **R213 (proposed) — procedural map generation algorithms for 8-bit constraints:** seeded PRNG choices on SM83 (LCG/LFSR/xorshift variants — period, byte cost, statistical quality); generation families at tile/screen granularity (cellular automata, drunkard's-walk/agent-based, BSP, value-noise, constraint/template-stitching approaches) evaluated for **determinism, ROM/WRAM cost, generation time, and guaranteeable invariants** (every region reachable; exactly one key item per region — BL-0017's rule becomes a *generator-guaranteed property*); post-pass smoothing/cleanup techniques that deliver D4's clean-screen bar. **R214 (proposed) — case studies: GBC homebrew & era titles with procedural maps** (D3's explicit ask): what exists in the GB/GBC homebrew scene (roguelike ports/originals, generated overworlds), what each generates at runtime vs pre-bakes, their RAM/ROM budgets and perceived quality — mined for what's *proven feasible* on this hardware class. Light updates to R201/R206 where region count/session shape change progression pacing. | B, C, A |
| `02-research-gbc-hardware` | Extensions, likely to R102/R105/R106 rather than new topics: **WRAM working-set** for a generated world (CGB's banked WRAM headroom vs the current map's needs); tilemap update cost as the player crosses generated screens (VBlank budget for redraws — D4's smoothness bar in hardware terms); **software PRNG determinism** on SM83 (no reliance on DIV/uninitialized RAM — the seed is the only entropy source, per D3); SRAM cost of persisting seed + per-region flags. | C |
| `02-research-tooling-and-testing` | Extension to R302/R305 or one new topic: **testing deterministic generation** — same-seed ⇒ identical-world assertions at WRAM level; multi-seed property tests (invariants hold across a seed corpus: reachability, one key item per region, no illegal tile pairs at screen seams — D4 made mechanical); the **Python reference-generator pattern** (mirror the generation algorithm in build-side Python to predict expected WRAM/tilemap state for any seed, giving the emulator suite exact oracles); screenshot-assertion strategy for transition cleanliness. **BL-0014** (no image→tile importer) stays DEFERRED per its recorded trigger unless the aesthetics stream elects to start from reference images. | C, A |

**Exit:** every claim Phase 3 needs is citable to an R-topic; R213/R214 together support a
concrete, costed algorithm recommendation for the ADR (per D3, the agent's decision to make).

### Phase 3 — Architecture synthesis (stage 03)

The GDS ladder exists; this phase is **deltas plus ADRs**, per level, in ladder order:

- **Decisions first (ADRs):** (1) **World-generation ADR** — the algorithm/approach choice
  D3 delegates to research (generation at boot/seed-change into WRAM vs other splits; ROM
  cost of generator code + tile assets vs the removed handcrafted maps); supersedes the 3×3
  assumptions in ADR-0001's context and `_zone_arrows()`'s hardcoded adjacency. (2) **Seed
  model ADR** — seed size, where the user modifies it (menu surface), persistence (save
  stores seed + per-region collected flags; the world *regenerates* from the seed rather than
  being stored — the data-model shape FS-101's version-byte precedent already anticipates).
  (3) **Bank-switching ADR** (kept from v1) — generator code, expanded tile sets, and music
  still contend for the ~9.1KB single-bank headroom. *Dropped from v1: the text-engine ADR
  (D1).* **BL-0015 (wider vs deeper)** is re-triaged rather than answered as filed: D3 makes
  world *shape* a generator parameter — the residual user decision is target scale/session
  length, folded into the world-generation ADR's parameterization (§6).
- **GDS-01 (Concept of Play):** the play loop over a generated world — how the visual
  narrative (D2) structures exploration (theme gradients as implicit direction, key-item
  theming per biome), session shape at the chosen scale, what "new seed" means for progress.
- **GDS-04 (Domain Model):** new/changed entities — **Seed**, **Region/Biome** (replacing the
  fixed nine-zone enumeration), **KeyItem** (item-agnostic, per D2), generator invariants as
  domain rules (exactly one KeyItem per region — BL-0017 generalized; full reachability).
- **GDS-07 (Data Model):** WRAM layout for the generated world's working set; SRAM format —
  seed + per-region flags, **save-format version bump** reusing FS-101's version-byte +
  pre-upgrade-default pattern (BL-0021 precedent).
- **GDS-08 (Presentation Architecture):** the normative aesthetic standard (stream A) now
  including **biome-transition presentation** — how theme flow (D2) is achieved under the
  8-BG-palette ceiling (BL-0009: 5 of 8 already serve terrain families; smooth flow likely
  demands shared/ecotone palettes and transition tile sets — *the* binding design constraint
  of this increment); tile-art quality criteria distilled from R209/R211 into the reviewable
  checklist `09-content-review` will later judge against; D4's clean-screen rules (no illegal
  tile adjacencies, seam coherence at screen edges).
- **GDS-09/GDS-10:** interface deltas (generator module boundary, seed patch points, new data
  contracts) and RTM-level refresh.
- Use **ADS-xxx per-cluster documents** where a stream's delta outgrows a ladder-level edit —
  the world generator is the near-certain candidate.

**Exit:** GDS ladder internally consistent at the new scope; algorithm and seed model decided
and recorded; every open question either decided (ADR/user record) or parked with a named
trigger.

### Phase 4 — Requirements engineering (stage 04) — the deliverable

One `04-requirements-engineering` increment pass deriving, per stream:

- **A:** measurable aesthetic **NFRs** — palette-budget compliance, tile readability criteria
  per GDS-08's standard, **D4 operationalized**: every generated screen passes defined
  clean-screen rules (no undefined tiles, no illegal seam pairs), transition-smoothness
  criteria, content-review acceptance thresholds.
- **B:** visual-narrative **FRs/NFRs** — biome adjacency/flow rules (which themes may border
  which, transition-band behavior at screen crossings), item-agnostic collect-goal
  requirements ("each region contains exactly one KeyItem themed to its biome; collecting all
  KeyItems wins" — superseding carrot-specific wording), theming constraints from C6
  (family-friendly) and A5. *No dialog FRs (D1); the routing for a future dialogue request is
  §4's table.*
- **C:** world-generation **FRs/NFRs** — determinism ("identical seed ⇒ identical world, every
  boot, every run"), seed modification behavior (entry surface, effect on existing progress),
  seed+flags persistence, generator invariants as testable requirements (reachability, one
  KeyItem per region), generation-time budget (smoothness — D4), bank/WRAM-budget NFRs
  extending BL-0019's headroom-watching convention.
- **RQ-03 review** of the merged baseline (conflicts, gaps, duplicates — e.g. generated-world
  requirements vs the no-fail-states assumption A5; determinism vs any timing-dependent
  behavior) and **RQ-04 RTM** rows for every new requirement, each traceable back to a GDS
  section and forward to (initially UNASSIGNED) tests.

**Definition of done for this plan:** RQ-01…04 updated and internally reviewed; every new
FR/NFR traces to a GDS-ladder section and an R-topic; §0's four decisions each have visible
requirement-level descendants; open questions resolved or carried as dispositioned backlog
entries; the pipeline journal records the increment. Stage 05 then decomposes the delta into
FEAT-xxxx rows and populates FP-01's currently-empty Release 2+ buckets — outside this plan.

## §3 Sequencing at a glance

```
Phase 0   IP-9030 → 10-integration-review → 11-release-readiness ─┐
          04-delta batch (BL-0020/0022/0026/0028) ────────────────┤
                                                                  ▼
Phase 1   00-intake (3 BL entries) → triage → 01-vision v3.0  [user: default-seed/C5 question]
                                                                  ▼
Phase 2   02-research: R212 (visual narrative) · R213 (procgen algorithms) ·
          R214 (GBC homebrew procgen) + hardware/tooling extensions
                                                                  ▼
Phase 3   ADRs (world generation · seed model · bank switching) →
          GDS-01/04/07/08/09/10 deltas   [BL-0015 folded into generator parameterization]
                                                                  ▼
Phase 4   04-requirements delta (FR/NFR per stream) → RQ-03 review → RQ-04 RTM   ◄── DONE
```

Stream A can reach Phase 3 early; streams B and C share R212–R214 and move together. The
pipeline manager's one-step-at-a-time cadence decides the interleaving at triage, not this
plan.

## §4 How the pipeline intakes user stories and backlog items

This increment adds no new intake machinery — it *rides* the existing one, and every future
user story for aesthetics/story/map goes through the same door:

1. **Single entry point:** `00-intake` is the only way work enters. It classifies the request
   (feature / bug / research-gap / design-question / doc-defect / observation), gathers cheap
   read-only evidence for bugs, checks BL-0001+ for duplicates, determines the **entry stage**,
   and appends a `NEW` row to [`backlog.md`](backlog.md). Intake never implements, and filing
   an item is never a decision to build it. §0's direction itself models the pattern: owner
   statements arrive, get normalized into decisions, and enter the pipeline as filed scope.
2. **Triage:** `00-pipeline-manager` dispositions every open entry at the start of its next
   run — `SCHEDULED` (rides a named step), `DEFERRED` (named revisit trigger), `NEEDS-USER`
   (named decision), or `REJECTED` (reason kept). Critical/High entries may not be DEFERRED
   without explicit user agreement. Rows are never deleted.
3. **Routing rule for entry stage** (the same rule §1 applied to the three streams):

   | User story looks like… | Intake type | Entry stage |
   |---|---|---|
   | "As a player I want NPCs / text dialogue / cutscenes…" | feature (vision-scope) | **DEFERRED at triage** per D1 (not ruled out, not a requirement) — revisit trigger: the owner re-opens dialogue; if re-opened, enters at **01** (vision) since it reverses a recorded non-goal |
   | "As a player I want the desert to blend into the beach / themed items in each region…" | feature | **03** (GDS-08/GDS-01 deltas) until Phase 3 lands; **04/06** afterwards under the visual-narrative commitment |
   | "As a player I want to enter/share a seed / get the same world as my friend…" | feature (D3 scope) | **02/03** until the seed-model ADR exists; **04/06** afterwards as ordinary Features |
   | "Seed X generates an unreachable region / a garbage screen" (post-implementation) | bug | **07** — remediation package; D4's clean-screen NFRs make this objectively testable |
   | "The new biome's palette clashes / transition band reads muddy" | finding | **09-content-review** finding → harvested to backlog → routed back to 08 |
   | "We don't know how GBC games usually do X" | research-gap | **02** (BL-0013 → R209/R210/R211 is the worked precedent; §0's procgen research asks follow the same route) |
4. **Findings loop back automatically:** stage skills never write the backlog; the manager
   harvests every run's findings/recommendations into it. Phase 2–4 runs will *generate* new
   backlog entries (exactly as GDS/RQ authoring generated BL-0015/0017/0019/0020/0022), and
   those ride later triage — the plan does not pre-enumerate them.
5. **Mid-increment stories:** user stories arriving while this plan is in flight are filed the
   same way and triaged into the increment where they fit, or DEFERRED with the next release
   as trigger. Vision-level pivots remain expensive by design (MSTR-001 §7) and get a
   deliberate 01 pass, never a quiet scope-fold.

**Seed intake rows for Phase 1** (final wording/IDs are `00-intake`'s call, not this plan's):

| Proposed entry | Type | Sev/Pri | Entry stage |
|---|---|---|---|
| Stream A — adopt a normative aesthetic standard incl. D4's smooth/clean bar; derive measurable presentation requirements | feature | Medium | 01 (commitment) → 03 |
| Stream B — visual story narrative per D2: biome themes flow into each other; item-agnostic, child-friendly collect-goal follows the narrative | feature (vision-scope) | Medium | 01 → 02 |
| Stream C — deterministic seed-driven procedurally generated world per D3, incl. the named research topics (procgen algorithms; GBC homebrew procgen case studies) | feature (C7/vision-scope) | Medium | 01 → 02 (re-triages BL-0015 alongside) |

## §5 Human gates and user decisions

| Gate | Phase | Decision | State |
|---|---|---|---|
| Adopt this plan | now | Whether to run Phases 0–4 as the next increment after Release 1 closes. | open |
| Release 1 GO/NO-GO (G4) | 0 | Normal `11-release-readiness` gate. | open |
| Story shape & tone | 1 | ~~Premise, dialog, tone~~ | **decided 2026-07-08 (D1/D2):** visual narrative, no dialogue requirement; agent constructs the flow from research |
| Map paradigm | 1–3 | ~~Wider vs deeper (BL-0015 as filed)~~ | **reshaped 2026-07-08 (D3):** procgen seeded world; residual decision = target scale/session-length parameters, folded into the world-generation ADR (§6) |
| Fate of the handcrafted 3×3 world | 1 | C5 protected-baseline consequence of D3: does a default seed ship, and is the current handcrafted world kept in any form? | open — carried into the 01-vision amendment |
| Seed modification surface | 3 | Where/how the user edits the seed (menu, save-slot behavior, effect on progress) — proposed at the seed-model ADR, confirmed by the user if choices are user-visible. | open |
| G3 package authorization | after 4 | Unchanged: no stage-08 work from this increment starts without explicit authorization. | standing |

## §6 Disposition of BL-0015 (wider vs deeper)

BL-0015's recorded revisit trigger — "when the C7 world-scale expansion is actually planned" —
fires with this plan. But D3 changes the question's shape rather than answering it as filed:
under procedural generation, world *breadth* is a generator parameter, not a hand-authoring
budget choice. What survives of BL-0015 for the user: **target scale and session shape** (how
big a generated world, how long a run to full collection), which becomes a parameter decision
inside the world-generation ADR (Phase 3) rather than a standalone architecture fork. The
palette-ceiling consequence BL-0015 recorded transfers intact — it now binds the **biome/
transition palette plan** (GDS-08, Phase 3) regardless of scale. `00-pipeline-manager` should
re-triage BL-0015 with this framing when the stream-C intake row is filed.

## §7 Constraints the requirements must respect (already on record + new from §0)

- **ROM budget:** 23404/32768 bytes used (~9.1KB headroom, BL-0019) — generator code, expanded
  transition tile sets, and music contend for it; the bank-switching ADR stays on the critical
  path. (Procgen *helps* here: generated worlds trade ROM map data for code + WRAM.)
- **Palette ceiling:** 8 BG palettes, 5 already serving terrain families (BL-0009/GDS-08) —
  now the binding constraint on D2's theme-flow: smooth biome blending under 8 palettes is the
  increment's hardest presentation problem and gets first-class GDS-08 treatment.
- **Determinism (D3):** the seed is the only entropy source — no DIV-register or
  uninitialized-RAM dependence anywhere in generation; same seed ⇒ identical world across
  boots, runs, and emulator versions. This must hold as a testable NFR (Python
  reference-generator oracle, Phase 2 tooling research).
- **Save format:** persist **seed + per-region collected flags** and regenerate the world —
  bumping the FS-101 version byte with defined pre-upgrade-save defaults (BL-0021 precedent).
- **Domain invariants:** "exactly one key collectible per region" graduates from an authored
  convention with a test (T1.11, BL-0017) to a **generator-guaranteed property tested across a
  seed corpus**; reachability of every region joins it.
- **D4 as NFRs:** clean-screen rules (no undefined tiles, coherent seams at screen edges) and
  smoothness (VBlank-budgeted redraws, bounded generation time at boot/seed-change) must be
  written measurably, per R305's test-derivable discipline, so G5's permanent gate can enforce
  them.
- **C6:** all items, themes, and imagery stay family-friendly, all-ages (bounds D2's item
  theming).

## §8 What this plan is not

It is a **map, not a mandate**: it does not file backlog entries (that's `00-intake`'s write
scope), does not amend the vision (that's a deliberate `01-vision` run — §0's decisions are
*inputs* to it, recorded here so they survive verbatim), does not re-triage BL-0015 (the
manager's call, §6), and does not authorize any package (G3). Adopting it means: finish Phase
0, then feed §4's three seed rows to `00-intake` and let `00-pipeline-manager` drive the
phases one step at a time, journaled as always.
