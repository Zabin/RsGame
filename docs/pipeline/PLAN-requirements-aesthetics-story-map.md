# PLAN — Path to a Requirements Baseline for Aesthetics, Story, and World Map

- **Document type:** increment plan (pipeline run-book companion, like
  [`BOOTSTRAP.md`](BOOTSTRAP.md))
- **Date:** 2026-07-08 · **Revised:** 2026-07-09 (v5 — §0 gains D9/D10: no auto-load at
  boot, main menu confirmed in the flow; exit-to-main-menu auto-saves. v4 added D7/D8; v3
  added the D2 clarification and D5/D6; v2 incorporated D1–D4 and superseded v1's
  dialog-centric story stream and handcrafted-map assumption)
- **Status:** **ADOPTED (2026-07-09) → PHASE 4 COMPLETE (2026-07-09).** All four phases executed
  in one continuous pipeline run (`00-pipeline-manager` runs #31–#42): Phase 1 vision amendment
  (MSTR-001 v3.0), Phase 2 research (new topics R111/R212/R213/R214 plus R102/R106/R302/R305
  extensions), Phase 3 architecture (ADR-0009/0010/0011 plus six GDS deltas — 01/04/07/08/09/10),
  Phase 4 requirements (RQ-01…04 delta, 16 new target requirements). **This document's own
  stated terminal deliverable (§2 Phase 4) is reached.** Adoption was **not** a G3 authorization
  for any implementation package (see §8) — nothing described by the new FR/NFR baseline has
  been built; stage 05 (`05-feature-decomposition`) onward continues under the pipeline's normal
  cadence, outside this plan's own stated scope.
- **Goal:** a traceable, reviewed **requirements baseline delta** (RQ-01…RQ-04 under
  `docs/requirements/`) covering three new work streams — **(A) aesthetic quality**, **(B) a
  visual story narrative**, **(C) a deterministic, seed- and scale-driven procedurally
  generated world map** — produced by the existing documentation-driven pipeline, not around
  it.
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
- **D2 — The story narrative is visual, told through logical biome flow.** Story is read from
  the world itself, and the goal of collecting **child-friendly items follows the visual
  narrative**. The owner does not dictate the specific items (carrots and presents are
  examples, not requirements). **The agent decides how to construct the narrative flow,
  grounded in research** — not by fiat.
  **Clarification (owner, 2026-07-08):** "flow into each other" does **not** mean two
  biomes/zones rendered in a single frame. It means a **logical ordering of whole
  screens/zones** — e.g. a water screen connects to a beach screen, beach to grassland,
  grassland to hills, hills to mountains, mountains to sky — and **not** disjointed
  adjacencies (water directly against sky, sky against inland terrain). Each screen is one
  biome; the flow is the *adjacency grammar between screens*, not intra-screen blending.
- **D3 — The map is a deterministic procedurally generated world from a user-modifiable
  seed.** The same inputs always produce the same world. Research must cover **procedural map
  generation algorithms** and **existing GBC homebrew games that use procedurally generated
  maps**; **the agent decides, from that research, the most efficient implementation approach**
  — the owner does not dictate the algorithm.
- **D4 — Quality bar:** the result must be **smooth**, and **every screen/room/view must be
  clean** (no visual garbage, no incoherent tile seams).
- **D5 — The current handcrafted 3×3 map is archived.** It is superseded by generated worlds,
  not kept as a shipping mode — the archival follows the `legacy/` precedent (BL-0004 →
  IP-9040/VR-9040: preserved with history, zero live references).
- **D6 — World scale is a user parameter.** In addition to the seed, the user can
  **enter/adjust a world scale parameter**. The generated world is a deterministic function of
  **(seed, scale)**; parameter bounds and defaults are architecture's call within hardware
  budgets, not dictated by the owner.
- **D7 — Seed and scale are set only at the start of a new game** (owner, 2026-07-09). They
  are entered/adjusted in the new-game flow and are **immutable for the life of that save** —
  no mid-run modification. Changing them means starting a new game.
- **D8 — The start-button save menu includes an "exit to main menu" option** (owner,
  2026-07-09). Implication (confirmed by D9): the title flow grows a proper **main menu**
  (continue / new game → seed & scale entry), since D7 makes it the only place a new world can
  be configured, and D8 gives the player a path back to it without power-cycling.
- **D9 — The main menu is confirmed in the flow, and a saved game no longer auto-loads at
  boot** (owner, 2026-07-09). Boot goes title → **main menu**; loading the save is a player
  choice (continue) beside new game. This **deliberately supersedes shipped baseline
  behavior**: MSTR-001 **C2**'s "a valid save auto-loads on boot" clause is amended
  (persistence across power-off stays; the *load* becomes player-initiated), with blast
  radius in the auto-load requirement (RQ-01's save/load group) and the tests that assert
  auto-load-on-boot.
- **D10 — Exiting to the main menu via the start-button menu auto-saves first** (owner,
  2026-07-09). No progress is lost by exiting; this resolves the exit option's save-safety
  semantics (the question Phase 4 had carried) in favor of save-then-exit.

D1/D2 resolve v1's open "story shape & tone" user gate. D5 resolves v2's open "fate of the
handcrafted world" gate. D3+D6 together effectively close BL-0015's "wider vs deeper" question
(see §6). D7–D10 fully resolve the seed & scale *timing*, the menu-flow shape, and the exit
save semantics, leaving only presentation details (entry screens, scale bounds/defaults) to
the Phase-3 ADR. D4 is the seed of this increment's headline NFRs.

## §1 Where each stream must enter the pipeline

The pipeline's rule is that work enters at the highest stage whose artifacts it invalidates or
extends. The three streams are *not* at the same altitude:

| Stream | What exists today | What's missing | Entry stage |
|---|---|---|---|
| **A — Aesthetic quality** | Research is substantially done: [R202](../research/encyclopedia/R202-8bit-game-feel.md) (game feel), [R203](../research/encyclopedia/R203-screen-composition-tile-grid.md) (composition), [R208](../research/encyclopedia/R208-palette-color-design.md) (palette design), [R209](../research/encyclopedia/R209-pixel-art-technique.md) (pixel-art technique), [R210](../research/encyclopedia/R210-ai-assisted-tile-art-workflow.md) (agent art workflow), [R211](../research/encyclopedia/R211-acclaimed-gbc-visual-design-case-studies.md) (GBC case studies) — all filed via BL-0013. [GDS-08](../architecture/08-presentation-architecture.md) documents presentation *as built*. | A **vision-level quality commitment** (MSTR-001 has no "the game must look good" commitment), a **normative** presentation standard (GDS-08 describes what is, not what "good" must mean), and measurable **NFRs** derived from R209/R211's heuristics plus D4's smooth/clean bar. | **01** (commitment) → **03** (GDS-08 delta) → **04** |
| **B — Visual story narrative** | Zones are visually distinct but their 3×3 adjacency is arbitrary (desert beside lake beside castle) — exactly what D2's biome-flow grammar replaces. No narrative framing exists; MSTR-001 §1/§3 never mention story, so narrative is **new vision-level scope** (MSTR-001 §7). Adjacent research exists (R203 composition, R208 palettes, R211 case studies) but no topic covers **wordless environmental storytelling** or **biome adjacency grammars**. Per D1, no text/dialog engine is needed. | Vision amendment naming the visual narrative; research on how tile-based games tell stories without words (biome ordering/elevation logic, landmark beats, item theming); the **adjacency grammar itself** (which biomes may border which — the D2 clarification makes this a hard generator constraint, not a soft aesthetic); **item-agnostic** re-statement of the collect-goal. | **01** (vision amendment) → **02** → **03** → **04** |
| **C — Procedural world map** | MSTR-001 **C7** already commits to a much larger world; bank-switching is already un-non-goaled ([ADR-0001](../architecture/adr/ADR-0001-single-bank-rom-no-mbc-switching.md) names its own supersession trigger); [R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md) grounds banking. **Nothing** covers procedural generation: no research on seeded generation under 8-bit constraints, no PRNG in the codebase, and the current world is a hand-authored 3×3 grid with hardcoded adjacency (`_zone_arrows()`, R203) — which D5 archives. | D3's named research (procgen algorithms; GBC homebrew procgen case studies), a **generator architecture decision** (agent-decided per D3, recorded as an ADR), a **(seed, scale) parameter model** (D6/D7 — entered only in the new-game flow, immutable per save; bounds; persistence), the **menu-flow delta** (D8 — main menu with continue/new-game, exit-to-main-menu in the save menu), determinism guarantees, and the archival package for the handcrafted world (D5). | **02** (research first — the algorithm decision is downstream of it) → **03** → **04** |

Stream B and C are now tightly coupled: D2's adjacency grammar is a **constraint the
generator must satisfy** — the narrative research (R212) feeds the generator research (R213)
directly.

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
   - **Story (D1/D2):** a commitment that the game tells its story **visually** — the world is
     ordered by a logical biome flow (one biome per screen; screen adjacencies follow a
     coherent grammar such as water → beach → grassland → hills → mountains → sky, never
     disjointed pairings), and progression is read from the world, not from text; the
     collect-goal is restated **item-agnostically** ("one child-friendly key item per region,
     themed to its biome; collecting all of them wins") with carrots as the current instance,
     not the requirement. Text dialogue recorded as a non-goal *at this vision's date* (D1's
     "not ruled out" phrasing preserved).
   - **Aesthetics (D4):** a quality commitment — presentation is a first-class, reviewed
     deliverable; every screen/room/view clean; the experience smooth.
   - **Map (D3/D5/D6/D7/D9):** C7 gains its first concrete shape — the world is
     **deterministically generated from a user-modifiable seed and a user-adjustable world
     scale, both fixed at new-game creation** (D7). **C2 is amended per D9**: persistence
     across power-off stays a commitment, but "a valid save auto-loads on boot" becomes
     "loading is player-initiated from the main menu" — a second deliberate
     protected-baseline change alongside D5's, with its own enumerated blast radius
     (auto-load FRs, boot-flow tests). The amendment
     records **D5's C5 consequence explicitly**: the shipped handcrafted 3×3 world is
     superseded and archived (the `legacy/` precedent, BL-0004/IP-9040) — a deliberate,
     recorded protected-baseline change, with the blast radius enumerated (tilemaps, tests
     asserting the 3×3 layout, map-screen UI, `Claude.md`/`memory.md` world descriptions).
   - Update the strategic-assumptions register (A1's 32KB framing under generated content; A5
     as it binds item theming; a new assumption for emulator-stable determinism).

**Exit:** MSTR-001 v3.0 + GDS-00 refreshed; three BL entries triaged SCHEDULED; the remaining
open design surfaces (seed/scale entry UX, scale bounds and defaults) carried to Phase 3's
ADRs with named owners.

### Phase 2 — Research grounding (stage 02)

The increment's heavy research phase — D2 and D3 both explicitly delegate design decisions to
research-grounded agent judgment, so this phase is what makes those decisions legitimate:

| Skill | New/updated topics | Grounds |
|---|---|---|
| `02-research-game-design` | **R212 (proposed) — wordless environmental storytelling & biome-flow grammar:** how tile-based GB/GBC-class games convey narrative without text (landmark beats, visual foreshadowing, theme evolution across a journey); **biome adjacency grammars** — which terrain types logically border which, elevation/moisture-style ordering (water→beach→grassland→hills→mountains→sky per D2's example), how acclaimed overworlds sequence biomes so travel reads as a story; **collectible theming** — what reads as a child-friendly "key item" per biome at 8×8/2bpp, and how item identity supports the flow (D2). Explicitly scoped to **one biome per screen** — no intra-frame blending research needed (D2 clarification). **R213 (proposed) — procedural map generation algorithms for 8-bit constraints:** seeded PRNG choices on SM83 (LCG/LFSR/xorshift — period, byte cost, statistical quality); generation families at screen granularity (cellular automata, agent-based/drunkard's-walk, BSP, value-noise, constraint/template-stitching) evaluated for **determinism, ROM/WRAM cost, generation time, scale-parameterization (D6), and guaranteeable invariants** — every region reachable; exactly one key item per region (BL-0017's rule becomes a *generator-guaranteed property*); **the R212 adjacency grammar holds everywhere** (constraint-satisfaction is a first-class evaluation criterion, per D2); post-pass cleanup that delivers D4's clean-screen bar. **R214 (proposed) — case studies: GBC homebrew & era titles with procedural maps** (D3's explicit ask): what exists in the GB/GBC homebrew scene (roguelike ports/originals, generated overworlds), what each generates at runtime vs pre-bakes, their RAM/ROM budgets and perceived quality — mined for what's *proven feasible* on this hardware class. Light updates to R201/R206 where region count/session shape change progression pacing. | B, C, A |
| `02-research-gbc-hardware` | Extensions, likely to R102/R105/R106 rather than new topics: **WRAM working-set** for a generated world across the D6 scale range (CGB's banked WRAM headroom vs per-scale needs); tilemap update cost as the player crosses generated screens (VBlank budget for redraws — D4's smoothness in hardware terms); **software PRNG determinism** on SM83 (no reliance on DIV/uninitialized RAM — seed+scale are the only inputs, per D3/D6); SRAM cost of persisting seed + scale + per-region flags. | C |
| `02-research-tooling-and-testing` | Extension to R302/R305 or one new topic: **testing deterministic generation** — same-(seed,scale) ⇒ identical-world assertions at WRAM level; multi-seed/multi-scale property tests (invariants hold across a parameter corpus: reachability, one key item per region, **no adjacency-grammar violations**, no illegal tile pairs at screen seams — D2/D4 made mechanical); the **Python reference-generator pattern** (mirror the generation algorithm in build-side Python to predict expected WRAM/tilemap state for any (seed, scale), giving the emulator suite exact oracles); screenshot-assertion strategy for seam cleanliness. **BL-0014** (no image→tile importer) stays DEFERRED per its recorded trigger unless the aesthetics stream elects to start from reference images. | C, A |

**Exit:** every claim Phase 3 needs is citable to an R-topic; R213/R214 together support a
concrete, costed algorithm recommendation for the ADR (per D3, the agent's decision to make),
including how it enforces R212's grammar and parameterizes by scale.

### Phase 3 — Architecture synthesis (stage 03)

The GDS ladder exists; this phase is **deltas plus ADRs**, per level, in ladder order:

- **Decisions first (ADRs):** (1) **World-generation ADR** — the algorithm/approach choice
  D3 delegates to research (generation at boot/parameter-change into WRAM vs other splits;
  ROM cost of generator code + tile assets vs the archived handcrafted maps; how the
  algorithm enforces the R212 adjacency grammar by construction or by constrained retry);
  supersedes `_zone_arrows()`'s hardcoded 3×3 adjacency. (2) **Seed & scale model ADR (D6/D7)** —
  seed size; **scale parameter representation, bounds, and default** (bounds derived from the
  Phase-2 WRAM/ROM/generation-time budgets, the agent's call per D6); the **new-game entry
  flow** (D7 fixes *when*: both parameters are set only at new-game creation and are
  immutable per save — the ADR designs only the entry screens' shape, reusing the existing
  digit/glyph tiles rather than a text engine); persistence (save stores **seed + scale +
  per-region flags**, written once at creation; the world *regenerates* from parameters
  rather than being stored — the shape FS-101's version-byte precedent already anticipates).
  (3) **Bank-switching ADR** (kept from v1) — generator code, expanded
  biome tile sets, and music still contend for the ~9.1KB single-bank headroom.
  *Dropped from v1: the text-engine ADR (D1). BL-0015 is closed rather than folded — see §6.*
- **GDS-01 (Concept of Play):** the play loop over a generated world — how the biome flow
  (D2) structures exploration (the grammar makes travel legible: heading inland/upland *is*
  the narrative), session shape across the D6 scale range, and the **revised game flow
  (D7/D8/D9/D10)**: boot → title → **main menu** (continue / new game → seed & scale entry)
  → play, with **no auto-load at boot** (D9); the in-game start-button save menu gains
  **exit to main menu**, which **auto-saves before returning** (D10), closing the loop back
  to new-game configuration without a power cycle and without progress loss. This is a delta
  to the shipped state machine (FEAT-1000/GDS-05's title→intro→auto-load→play flow and the
  existing save-menu states).
- **GDS-04 (Domain Model):** new/changed entities — **Seed**, **WorldScale** (D6),
  **Region/Biome** with the **adjacency grammar as a domain rule** (D2), **KeyItem**
  (item-agnostic, per D2), generator invariants as domain rules (exactly one KeyItem per
  region — BL-0017 generalized; full reachability; grammar-valid adjacency everywhere).
- **GDS-07 (Data Model):** WRAM layout for the generated world's working set at maximum
  scale; SRAM format — seed + scale + per-region flags, **save-format version bump** reusing
  FS-101's version-byte + pre-upgrade-default pattern (BL-0021 precedent).
- **GDS-08 (Presentation Architecture):** the normative aesthetic standard (stream A). With
  D2's clarification, **each screen renders exactly one biome** — so the 8-BG-palette ceiling
  (BL-0009) binds the **number of distinct biome families and their per-screen palette
  assignment**, not intra-screen blending; the existing terrain-family palette-reuse pattern
  extends naturally, and adjacent screens' palettes should step coherently along the grammar
  (water-blues → beach-sands → grass-greens…) so screen transitions *feel* continuous. Plus:
  tile-art quality criteria distilled from R209/R211 into the reviewable checklist
  `09-content-review` will later judge against; D4's clean-screen rules (no illegal tile
  adjacencies within a screen, coherent seams at screen edges).
- **GDS-09/GDS-10:** interface deltas (generator module boundary, seed/scale patch points,
  new data contracts) and RTM-level refresh.
- Use **ADS-xxx per-cluster documents** where a stream's delta outgrows a ladder-level edit —
  the world generator is the near-certain candidate.

**Exit:** GDS ladder internally consistent at the new scope; algorithm, grammar, and
seed/scale model decided and recorded; every open question either decided (ADR/user record)
or parked with a named trigger.

### Phase 4 — Requirements engineering (stage 04) — the deliverable

One `04-requirements-engineering` increment pass deriving, per stream:

- **A:** measurable aesthetic **NFRs** — palette-budget compliance, tile readability criteria
  per GDS-08's standard, **D4 operationalized**: every generated screen passes defined
  clean-screen rules (no undefined tiles, no illegal seam pairs), palette-stepping coherence
  along the grammar, content-review acceptance thresholds.
- **B:** visual-narrative **FRs/NFRs** — the **biome adjacency grammar as requirements**
  (normative adjacency rules per D2's example ordering: which biome families may border
  which; no disjointed pairings anywhere in any generated world), one-biome-per-screen,
  item-agnostic collect-goal requirements ("each region contains exactly one KeyItem themed
  to its biome; collecting all KeyItems wins" — superseding carrot-specific wording), theming
  constraints from C6 (family-friendly) and A5. *No dialog FRs (D1); the routing for a future
  dialogue request is §4's table.*
- **C:** world-generation **FRs/NFRs** — determinism ("identical (seed, scale) ⇒ identical
  world, every boot, every run"), **seed and scale entry behavior** (new-game-only entry with
  per-save immutability — D6/D7; bounds and defaults), **menu-flow FRs** (main menu with
  continue/new-game and **no auto-load at boot** — D9, superseding the shipped auto-load FR;
  the save menu's exit-to-main-menu option with **auto-save-then-exit** semantics — D8/D10),
  seed+scale+flags persistence, the handcrafted-world **archival
  requirement** (D5, packaged later per the IP-9040 precedent),
  generator invariants as testable requirements (reachability, one KeyItem per region,
  grammar validity), generation-time budget across the scale range (smoothness — D4),
  bank/WRAM-budget NFRs extending BL-0019's headroom-watching convention.
- **RQ-03 review** of the merged baseline (conflicts, gaps, duplicates — e.g. generated-world
  requirements vs the no-fail-states assumption A5; determinism vs any timing-dependent
  behavior; grammar completeness — every biome family reachable from every other through
  legal steps) and **RQ-04 RTM** rows for every new requirement, each traceable back to a GDS
  section and forward to (initially UNASSIGNED) tests.

**Definition of done for this plan:** RQ-01…04 updated and internally reviewed; every new
FR/NFR traces to a GDS-ladder section and an R-topic; §0's ten decisions each have visible
requirement-level descendants; open questions resolved or carried as dispositioned backlog
entries; the pipeline journal records the increment. Stage 05 then decomposes the delta into
FEAT-xxxx rows and populates FP-01's currently-empty Release 2+ buckets — outside this plan.

## §3 Sequencing at a glance

```
Phase 0   IP-9030 → 10-integration-review → 11-release-readiness ─┐
          04-delta batch (BL-0020/0022/0026/0028) ────────────────┤
                                                                  ▼
Phase 1   00-intake (3 BL entries) → triage → 01-vision v3.0
          (records D1–D10 incl. the D5/D9 protected-baseline changes)
                                                                  ▼
Phase 2   02-research: R212 (biome-flow grammar) · R213 (procgen algorithms) ·
          R214 (GBC homebrew procgen) + hardware/tooling extensions
                                                                  ▼
Phase 3   ADRs (world generation · seed & scale model · bank switching) →
          GDS-01/04/07/08/09/10 deltas   [BL-0015 closed by D3/D6 — §6]
                                                                  ▼
Phase 4   04-requirements delta (FR/NFR per stream) → RQ-03 review → RQ-04 RTM   ◄── DONE
```

Stream A can reach Phase 3 early; streams B and C share R212–R214 and move together (the
grammar is a generator constraint). The pipeline manager's one-step-at-a-time cadence decides
the interleaving at triage, not this plan.

## §4 How the pipeline intakes user stories and backlog items

This increment adds no new intake machinery — it *rides* the existing one, and every future
user story for aesthetics/story/map goes through the same door:

1. **Single entry point:** `00-intake` is the only way work enters. It classifies the request
   (feature / bug / research-gap / design-question / doc-defect / observation), gathers cheap
   read-only evidence for bugs, checks BL-0001+ for duplicates, determines the **entry stage**,
   and appends a `NEW` row to [`backlog.md`](backlog.md). Intake never implements, and filing
   an item is never a decision to build it. §0's direction itself models the pattern: owner
   statements arrive, get normalized into decisions (including mid-flight clarifications like
   D2's), and enter the pipeline as filed scope.
2. **Triage:** `00-pipeline-manager` dispositions every open entry at the start of its next
   run — `SCHEDULED` (rides a named step), `DEFERRED` (named revisit trigger), `NEEDS-USER`
   (named decision), or `REJECTED` (reason kept). Critical/High entries may not be DEFERRED
   without explicit user agreement. Rows are never deleted.
3. **Routing rule for entry stage** (the same rule §1 applied to the three streams):

   | User story looks like… | Intake type | Entry stage |
   |---|---|---|
   | "As a player I want NPCs / text dialogue / cutscenes…" | feature (vision-scope) | **DEFERRED at triage** per D1 (not ruled out, not a requirement) — revisit trigger: the owner re-opens dialogue; if re-opened, enters at **01** (vision) since it reverses a recorded non-goal |
   | "As a player I want mountains to lead up to sky zones / themed items in each region…" | feature | **03** (grammar/GDS deltas) until Phase 3 lands; **04/06** afterwards under the visual-narrative commitment |
   | "As a player I want to enter/share a seed / play a bigger world…" | feature (D3/D6 scope) | **02/03** until the seed & scale ADR exists; **04/06** afterwards as ordinary Features |
   | "Seed X at scale Y generates an unreachable region / water touching sky / a garbage screen" (post-implementation) | bug | **07** — remediation package; D2's grammar and D4's clean-screen NFRs make each objectively testable |
   | "The new biome's palette clashes / the beach→grass palette step reads harsh" | finding | **09-content-review** finding → harvested to backlog → routed back to 08 |
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
| Stream B — visual story narrative per D2: logical biome-flow grammar between screens (one biome per screen); item-agnostic, child-friendly collect-goal follows the narrative | feature (vision-scope) | Medium | 01 → 02 |
| Stream C — deterministic procedurally generated world from user-modifiable **seed + world scale**, set only at new-game start, per D3/D6/D7; menu-flow delta (main menu; save menu's exit-to-main-menu) per D8; archive the handcrafted 3×3 world per D5; incl. the named research topics (procgen algorithms; GBC homebrew procgen case studies) | feature (C7/vision-scope) | Medium | 01 → 02 (closes BL-0015 alongside — §6) |

## §5 Human gates and user decisions

| Gate | Phase | Decision | State |
|---|---|---|---|
| Adopt this plan | now | ~~Whether to run Phases 0–4 as the next increment after Release 1 closes~~ | **decided 2026-07-09: ADOPTED** ("Adopt the plan for pipeline implementation") |
| Release 1 GO/NO-GO (G4) | 0 | Normal `11-release-readiness` gate. | open |
| Story shape & tone | 1 | ~~Premise, dialog, tone~~ | **decided 2026-07-08 (D1/D2):** visual narrative via logical biome flow, no dialogue requirement; agent constructs the grammar from research |
| Map paradigm | 1–3 | ~~Wider vs deeper (BL-0015 as filed)~~ | **decided 2026-07-08 (D3/D6):** procgen world from (seed, scale); scale is a *user-runtime parameter*, so the design fork dissolves — §6 |
| Fate of the handcrafted 3×3 world | 1 | ~~Does a default seed ship / is the current world kept?~~ | **decided 2026-07-08 (D5):** archived, per the `legacy/` precedent |
| Seed & scale timing + menu flow | 1–3 | ~~Where/when the user edits seed and scale; boot/exit semantics; entry-screen presentation; scale bounds/defaults~~ | **fully decided:** timing/menu flow 2026-07-09 (D7/D8/D9/D10); entry-screen presentation and scale bounds/defaults resolved at [ADR-0010](../architecture/adr/ADR-0010-seed-scale-model.md) (2026-07-09) — 16-bit seed, scale 2–9 (default 3), digit-cursor entry UI, no text engine. |
| G3 package authorization | after 4 | Unchanged: no stage-08 work from this increment starts without explicit authorization. | standing |

## §6 Disposition of BL-0015 (wider vs deeper)

BL-0015's recorded revisit trigger — "when the C7 world-scale expansion is actually planned" —
fires with this plan, and **D3+D6 close the question rather than merely reshaping it**: under
procedural generation with a **user-adjustable scale parameter**, "wider vs deeper" is no
longer a design fork to pick — the player picks, per world, within architecture-set bounds.
What remains is engineering, not a user gate: the **scale bounds and default** (derived from
the Phase-2 WRAM/ROM/generation-time budgets, decided in the seed & scale ADR per D6) and
session-shape guidance per scale (GDS-01). The palette-ceiling consequence BL-0015 recorded
transfers in corrected form — with one biome per screen (D2 clarification), the ceiling binds
the **count of distinct biome families**, not blending (§7). `00-pipeline-manager` should
close BL-0015 with this rationale when the stream-C intake row is filed.

## §7 Constraints the requirements must respect (already on record + new from §0)

- **ROM budget:** 23404/32768 bytes used (~9.1KB headroom, BL-0019) — generator code, biome
  tile sets, and music contend for it; the bank-switching ADR stays on the critical path.
  (Procgen *helps* here: generated worlds trade ROM map data for code + WRAM; D5's archival
  also retires the nine handcrafted screen layouts.)
- **Palette ceiling (corrected framing per D2's clarification):** 8 BG palettes, 5 already
  serving terrain families (BL-0009/GDS-08). With exactly **one biome per screen**, the
  ceiling binds the **number of distinct biome families** (and OBJ theming), not intra-screen
  blending — the existing terrain-family reuse pattern extends naturally; adjacent-screen
  palette *stepping* along the grammar is a design-quality concern (GDS-08), not a hardware
  fight.
- **Determinism (D3/D6):** seed and scale are the only entropy sources — no DIV-register or
  uninitialized-RAM dependence anywhere in generation; same (seed, scale) ⇒ identical world
  across boots, runs, and emulator versions. This must hold as a testable NFR (Python
  reference-generator oracle, Phase 2 tooling research).
- **Save format:** persist **seed + scale + per-region collected flags** and regenerate the
  world — seed and scale written **once at new-game creation and never rewritten** (D7);
  bumping the FS-101 version byte with defined pre-upgrade-save defaults (BL-0021 precedent).
- **Domain invariants:** "exactly one key collectible per region" graduates from an authored
  convention with a test (T1.11, BL-0017) to a **generator-guaranteed property tested across
  a (seed, scale) corpus**; reachability of every region and **grammar-valid adjacency
  everywhere** (D2) join it.
- **D4 as NFRs:** clean-screen rules (no undefined tiles, coherent seams at screen edges) and
  smoothness (VBlank-budgeted redraws, bounded generation time at boot/parameter-change
  across the scale range) must be written measurably, per R305's test-derivable discipline,
  so G5's permanent gate can enforce them.
- **D5 archival:** the handcrafted 3×3 world's retirement follows the IP-9040 precedent —
  history preserved under `legacy/`, zero live references, tests updated deliberately (the
  suite currently asserts the 3×3 layout throughout; its rewrite is in-scope for the eventual
  implementation packages, not silently).
- **C6:** all items, themes, and imagery stay family-friendly, all-ages (bounds D2's item
  theming).

## §8 What this plan is (and is not) now that it's adopted

Adopted 2026-07-09 (§5). Adoption means: this is the pipeline's next increment after Release
1 closes — §4's three seed rows are filed with `00-intake`, and `00-pipeline-manager` drives
the phases one step at a time, journaled as always, starting with Phase 0's remaining
bootstrap work.

It remains a **map, not a mandate**: it does not itself amend the vision (that's the
deliberate `01-vision` run of Phase 1 — §0's decisions are *inputs* to it, recorded here so
they survive verbatim), does not close BL-0015 (the manager's call, §6), and does not
authorize any implementation package — **G3 authorization is still required per package**
when stage 07 eventually produces them.
