# MSTR-001 — Program Vision: Bunny Quest

- **Document ID:** MSTR-001 · **Version:** 4.0 · **Status:** ✅ Authored (deliberate, narrow
  carve-out — dual-audience combat sub-mode, `BL-0133`)
- **Date:** 2026-07-06 (v1.0); 2026-07-06 (v2.0, same day — see §8); 2026-07-09 (v3.0 — see §8);
  **2026-07-17 (v4.0 — see §8/§8a)** · **Owned by:** `01-vision` skill
- **Derived from (v2.0):** direct inspection of the current shipped source
  (`tilemaps.py`, `asm_game.py`, `build_rom.py`, `music.py`, `tiles.py`) and a rebuilt ROM
  compared byte-for-byte against the checked-in `BunnyQuest.gbc` — **not** from `Claude.md`/
  `memory.md`, which v1.0 trusted and which are now known-stale (see §8). Plus the project
  owner's explicit scope-expansion instruction, 2026-07-06.
- **Derived from (v3.0):** the project owner's explicit direction, 2026-07-08/09, recorded
  verbatim-in-substance as decisions **D1–D10** in
  [`docs/pipeline/PLAN-requirements-aesthetics-story-map.md`](../pipeline/PLAN-requirements-aesthetics-story-map.md)
  §0 (the adopted increment plan), and the seed backlog entries it produced —
  [`BL-0029`](../pipeline/backlog.md) (aesthetic quality), [`BL-0030`](../pipeline/backlog.md)
  (visual story narrative), [`BL-0031`](../pipeline/backlog.md) (procedurally generated world) —
  filed by `00-intake`.
- **Design-facing restatement:** [`docs/architecture/00-vision.md`](../architecture/00-vision.md)
  (GDS-00)

## §1 What this project is

**Bunny Quest** (renamed from "Bunny Garden Adventure" — see §8) is a top-down exploration game
for **Game Boy Color**: a bunny explores a **3×3 grid of nine visually distinct zones** — Beach,
Forest, Mountain, Lake, Village, Cave, Desert, Plains, Castle — walking off any screen edge to
enter the neighboring zone in that direction. Stars and flowers scattered through each zone add
to a running score; each zone also hides one **carrot**, and collecting all nine carrots
(tracked in a 9-byte per-zone flag array) is the win condition. The game has a title/intro flow,
an in-game save menu, a 3×3 world-map screen showing which zones' carrots are collected, a
victory screen, an original melody, and a battery-backed save that persists across power-off and
**currently** auto-loads on boot. *(This paragraph describes the game as shipped at v2.0. As of
v3.0, C2's auto-load clause and this section's fixed 3×3/nine-zone/carrot description are the
**named subject of a deliberate, in-progress supersession** — see C8–C10 below and §8's blast
radius. They remain accurate today; they are not the permanent target.)*

**Where this is headed (v3.0, new — C8/C9/C10):** the project owner has directed three concrete
next steps, elaborated in the adopted increment plan
([`PLAN-requirements-aesthetics-story-map.md`](../pipeline/PLAN-requirements-aesthetics-story-map.md)):
the game's presentation becomes a first-class, reviewed quality commitment (**C8**); its story is
told **visually**, through a logical narrative flow between biome regions rather than text
(**C9**); and its world becomes **procedurally generated**, deterministic from a seed and a
user-adjustable world-scale parameter the player sets once at new-game creation (**C10** — the
first concrete shape of **C7**'s long-term scale direction). These are purpose-level commitments
only — the research grounding, the generation algorithm, the biome-adjacency grammar, and the
exact requirements are explicitly delegated downstream (research → architecture → requirements),
not decided here.

Equally load-bearing: the game is **built entirely by a modular Python assembler pipeline** — no
RGBDS or external toolchain. Python modules define the tiles, screens, music, and SM83 game
logic; `build_rom.py` assembles them into a valid ROM; a headless-emulator test suite proves the
result. The project is therefore two products in one: a playable GBC game, and a **reference
demonstration that an agent-driven Python pipeline can produce and verify real console
software**. (Per the project owner's decision of 2026-07-06 — backlog BL-0004 — the modular
chain is the canonical build; legacy artifacts predating it are to be archived under `legacy/` —
see §8 for what "legacy" now includes.)

## §2 Who it is for

1. **Players:** an all-ages, casual audience playing short handheld sessions — gentle pacing, no
   fail states, non-violent, family-friendly content throughout (assumption A5). **This remains
   true of the base game without exception** — every screen/mode a child can reach through the
   game's own default flow (MAIN MENU → finite or Infinite Mode, as they exist today) stays
   fail-state-free and non-violent, unchanged by C11 below.
2. **v4.0, new — a second, explicitly opt-in audience (C11):** a parent/adult player, playing a
   **separate, clearly-gated combat sub-mode** layered on Infinite Mode's map. This mode may be
   tonally grimmer than the base game (real adversarial mechanics, damage, a fail state) — see
   **C11**. It does not replace, soften, or reinterpret the base game's own child-friendly
   commitment; it sits beside it, behind its own explicit entry point.
3. **Developers and coding agents:** the repository is a worked example of a fully-tested,
   documentation-driven GBC project — every behavior traceable from vision to a named emulator
   test. **As of v3.0 this is true in practice** (`test_rom.py` rewritten and independently
   verified, `IP-9010`/`VR-9010`, 125/125) — kept honest as a live claim, not aspirational.

## §3 Scope commitments (what must always be true)

| # | Commitment | Evidence |
|---|---|---|
| C1 | The ROM is **CGB-color, single-bank at present** (rsize 0x00), with a **valid header** (checksum, GBC flag 0x80). *Single-bank is the current shape, not a permanent ceiling* — see C7 and assumption A1. | rebuilt-and-diffed against `BunnyQuest.gbc`, header `set_header("BUNNYQUEST", cart=0x03, rsize=0x00, ramsize=0x02)` in `build_rom.py:163` |
| **C2** *(amended v3.0)* | Cart type is **MBC1+RAM+BATTERY (0x03)**; progress **persists across power-off** (unchanged). **Amended:** loading a save is **player-initiated**, not automatic — boot goes to a **main menu** (continue / new game), never silently into `PLAYING`. New-game creation is also where **C10**'s seed and world-scale parameters are entered, fixed for the life of that save. *(Owner decisions D7–D10, 2026-07-09; states the built target, same forward-looking pattern as C7/C10 — not yet implemented, see §8.)* | `build_rom.py:163`; save-format bytes in `asm_game.py` (0xA004–0xA00E range); auto-load clause superseded per owner direction, 2026-07-09 |
| C3 | The build is the **modular Python assembler chain** (`build_rom.py` + `gbc_lib`/`tiles`/`tilemaps`/`music`/`asm_game`) — reproducible from source with no external assembler | BL-0004 decision; a clean rebuild from source reproduces `BunnyQuest.gbc` byte-for-byte |
| C4 | Every release is **emulator-verified**: the ROM builds and a full, *currently-accurate* test suite passes | rule G5 — satisfiable in practice as of v3.0 (`test_rom.py` rewritten and independently verified, `IP-9010`/`VR-9010`, 125/125). **New at v3.0:** determinism itself becomes G5-testable once C10 lands (same-(seed,scale) ⇒ identical world, per a Python reference-generator oracle) |
| C5 | The **currently shipped Bunny Quest behavior** (9 zones, 9-carrot win condition, star/flower scoring, save/map/victory flows, auto-load) is the protected baseline going forward — changes to it are deliberate, pipeline-traced decisions, never side effects. **v3.0 exercises this clause twice, deliberately** (§8): the handcrafted 3×3 world is superseded by C10's procedurally generated world (archived, not deleted, under `legacy/` per the `BL-0004`/`IP-9040` precedent); auto-load-on-boot is superseded by C2's amended player-initiated load. Both are named, dated, traceable amendments — exactly what C5 exists to require of a baseline change, not an exception to it. | direct code read of `tilemaps.py`/`asm_game.py`, 2026-07-06; amendment record, 2026-07-09 |
| C6 | Content stays **family-friendly** and playable by a casual audience | §2 |
| C7 | **Long-term world-scale target: comparable to a Zelda- or Pokémon-class overworld** — substantially more than nine zones/biomes, explored at a larger scale, "pressing the limits beyond that" as far as the platform and this pipeline's tooling can be stretched. This is a direction, not a single fixed target size. **v3.0 gives it its first concrete shape — see C10.** | project owner's explicit instruction, 2026-07-06 |
| **C8** *(new, v3.0)* | **Presentation is a first-class, reviewed quality commitment**: every screen/room/view is clean (no visual garbage, no incoherent tile seams) and the experience is smooth. A normative aesthetic standard (downstream: GDS-08) must exist and be checked against, not left as an unstated craft preference. | Owner decision D4, 2026-07-09; grounded in existing research R209–R211 (`BL-0013`) |
| **C9** *(new, v3.0)* | **The story is told visually**, through the world's own structure — a **logical adjacency grammar** between whole screens/regions (one biome per screen; adjacent regions follow a coherent flow, e.g. water → beach → grassland → hills → mountains → sky; never a disjointed pairing like water directly against sky). The collect-goal is **item-agnostic and child-friendly**, themed to each region and following this narrative (carrots are today's instance, not a fixed requirement). **No text-dialogue requirement at this vision's date** — not ruled out (§4), just not required; the agent constructs the adjacency grammar and item theming from research, not by owner fiat. | Owner decisions D1/D2, 2026-07-09 |
| **C10** *(new, v3.0)* | **The world is procedurally generated** — deterministic, from a **seed** and a **world-scale** parameter, both **user-modifiable but entered only at new-game creation** and immutable for the life of that save (C2, amended above). This is **C7's long-term scale direction taking its first concrete shape**: the fixed 3×3/nine-zone handcrafted layout (C5) is superseded and archived, not the world-scale ambition itself. The specific generation algorithm is explicitly **not** dictated here — delegated to research (procgen algorithms; GBC homebrew precedent) and the downstream architecture decision it grounds. | Owner decisions D3/D5/D6/D7, 2026-07-09; concretizes C7 |
| **C11** *(new, v4.0)* | **A dual-audience carve-out: an opt-in combat sub-mode, layered on Infinite Mode, may be tonally grimmer than the base game.** The project owner's own framing: "the game is designed for a child but the combat mode is for when the parent is playing. It can be grimmer." This does **not** amend C6/C9/A5 for the base game — every existing mode (finite, Infinite Mode's own base collect-loop) stays exactly as child-friendly/non-violent/fail-state-free as it is today. It **carves out** a bounded exception: a mechanic involving mobs, a ranged weapon, and (per downstream design, not decided here) real damage/fail-state may exist, gated behind its own explicit entry point (not the default flow a child would reach unprompted), and is not bound by A5/C6's tone requirement. The exact gating mechanism (a settings toggle, a separate menu entry, a parental-style confirmation, etc.), the specific tone/violence level, and every other design question are explicitly **not** decided here — delegated downstream (`03`→`04`→`06`), same pattern as C9/C10's own algorithm-agnostic framing. | Direct owner decision, 2026-07-17, resolving `BL-0133`'s Open Question 1 (`ADS-002`) |

## §4 Non-goals (at this vision's date)

Not commitments against forever — just explicitly *not* promised **yet**: real-hardware
certification (emulator verification is the gate — assumption A2) · localization beyond English
(A7) · a second, distinct game in this repository (A4 — Bunny Quest's own world growing much
larger is C7, not a second game) · multiplayer/link-cable features · **text-based dialogue or
an NPC conversation system** (new at v3.0, C9/D1 — deliberately phrased as *not yet*, not
*never*: the owner explicitly declined to rule it out, only declined to require it now; a future
request to add it re-opens at `01-vision`, since it would reverse a recorded non-goal, not extend
one).

**Reversed by this revision:** "bank-switched ROM growth beyond one bank" is **no longer a
non-goal** — C7 explicitly anticipates it becoming necessary as the world grows past what a
single 32KB bank holds (currently ~9.6KB of headroom remains: 23148/32768 bytes used at v2.0).
MBC bank-switching strategy is now an expected future architecture question for
`03-architecture-design-synthesis`, not a boundary to protect. **(v3.0 sharpens this further:**
C10's generator code and C9's biome tile sets are named, concrete consumers of that headroom —
bank switching is no longer merely anticipated, it is now an expected dependency of C9/C10's own
architecture pass, per the adopted plan's bank-switching ADR.**)**

## §5 Quality bar

"Done" for any change means: the ROM builds with a valid header; a full test suite that actually
matches the current shipped behavior is green; the behavior is traceable through the pipeline's
artifacts (requirement → feature spec → package → verification report); and the working
quick-references (`Claude.md`, `memory.md`) match the shipped bytes. **As of v3.0 this bar is
met** — the test suite was rewritten and independently verified (`IP-9010`/`VR-9010`, 125/125),
and the quick-references were refreshed (`IP-9030`, 2026-07-09, awaiting `09-package-verification`
in a fresh session per the independence rule).

**New at v3.0 (C8):** "done" for any presentation-affecting change additionally means it is
**smooth** and **every screen/room/view is clean** — checked against the normative standard C8
requires GDS-08 to state, not left to informal judgment.

## §6 Authority & document precedence

1. This document (MSTR-001) is the top of the tree for *purpose-level* statements; the GDS ladder
   (`docs/architecture/`) is authoritative for design as each level's merge gate closes.
2. Until `docs/master/MSTR-006` is authored, the governance rules **G1–G5** in
   [`.claude/skills/README.md`](../../.claude/skills/README.md) are binding.
3. `Claude.md` and `memory.md` are the live developer quick-references. **As of v3.0 both are
   current** (refreshed by `IP-9030`, 2026-07-09, awaiting independent verification) — their
   current-state claims may be trusted again; watch for the same drift risk each time this
   vision changes without an immediate matching doc-refresh package.
4. Conflicts between documents are findings for the owning skill — never resolved by silently
   editing the downstream copy. `test_rom.py` no longer conflicts with the shipped game as of
   `IP-9010` (`VR-9010`, independently verified) — this clause stays as a standing rule, not
   because a conflict is currently open.

## §7 Change control

A change to §1–§4 is the most expensive kind of change in the tree: it is made only by the
`01-vision` skill, dated, with rationale recorded in §8's amendment log, and the downstream blast
radius enumerated (artifact → owning skill). The assumptions register carries the tripwires; when
a trigger fires, the register entry returns to the pipeline manager for re-triage rather than
being quietly edited.

## §8 Vision Amendment Log

| Date | Version | What changed | Why | Downstream blast radius |
|---|---|---|---|---|
| 2026-07-06 | 1.0 → 2.0 | **Corrected §1/§3/§4 wholesale**: the game is *Bunny Quest* (9 zones, 3×3 grid, 9-carrot win condition), not the 3-zone "Bunny Garden Adventure" v1.0 described. Added **C7** (Zelda/Pokémon-scale world target) and reversed the bank-switching non-goal. | v1.0 was authored (correctly, per its own bootstrap-mode rules) from `Claude.md`/`memory.md` — but those files describe the game **as it existed before commit `679b5cf` ("Rewrite as Bunny Quest")**, which had already landed on `main` before the pipeline scaffold's own PR merged. v1.0 never read the actual code. This revision does, and layers on the project owner's explicit forward-looking scale ambition given the same message. | See the full enumeration below — this is not a small fix. |
| 2026-07-09 | 2.0 → 3.0 | **Deliberate scope expansion, three streams, one dated pass:** added **C8** (presentation is a first-class quality commitment — smooth, every screen clean), **C9** (the story is told visually, via a logical biome-adjacency grammar between screens, not text; item-agnostic child-friendly collect-goal), and **C10** (the world becomes deterministically procedurally generated from a user-set seed + world-scale, both fixed at new-game creation — C7's first concrete shape). **Amended C2**: a valid save's *load* becomes player-initiated via a new main menu, not automatic on boot (persistence across power-off is unchanged). Added a non-goal (text dialogue — not ruled out, just not required, C9/D1). Updated §5's quality bar (now met; added C8's smooth/clean clause) and §6 (Claude.md/memory.md/test_rom.py all now current, per `IP-9010`/`IP-9030`). | Direct owner direction across a short exchange, 2026-07-08/09, recorded verbatim-in-substance as decisions **D1–D10** in the adopted increment plan (`PLAN-requirements-aesthetics-story-map.md` §0) — see that document for the full decision-by-decision record. Two of the ten decisions (D5, D9) are **deliberate protected-baseline changes under C5**: the handcrafted 3×3 world is superseded by procedural generation, and auto-load-on-boot is superseded by player-initiated loading. Both are named here, not absorbed silently, per C5's and §7's own rules. | See the full enumeration below. |
| 2026-07-17 | 3.0 → 4.0 | **Deliberate, narrow carve-out — added C11**: an opt-in combat sub-mode, layered on Infinite Mode, gated behind its own explicit entry point, may be tonally grimmer than the base game (mobs, a ranged weapon, real damage/fail-state — exact design deferred to `03`→`04`→`06`). §2 amended to name the parent/adult player as a second, explicitly opt-in audience. **C6/C9/A5 are unchanged for the base game** — this is an addition, not a reversal: every mode a child reaches through the default flow stays exactly as fail-state-free/non-violent as it is today; C11 only ever applies inside its own gated mode. Resolves `BL-0133`'s Open Question 1 (`ADS-002`), fired by `A5`'s own recorded trigger ("the project owner directs a tonal, difficulty, or audience shift"). | Direct owner decision, 2026-07-17, resolving the tension `03-architecture-design-synthesis` surfaced in `ADS-002` rather than resolving itself. | See the enumeration below (§8a). |

### §8a — Downstream blast radius of the 3.0 → 4.0 revision (C11)

| Artifact | Why it's affected | Owning skill | Required action |
|---|---|---|---|
| `docs/architecture/00-vision.md` (GDS-00) | Must state the same dual-audience carve-out (mirrors §2/C11 here) so the two never disagree | `01-vision` (this run) | Updated in this same pass — see below. |
| `docs/architecture/strategic-assumptions-register.md`, A5 | A5's own recorded trigger ("the project owner directs a tonal, difficulty, or audience shift") has fired | `01-vision` (this run) | Amended in this same pass — A5 stays in force for the base game, with C11's carve-out noted explicitly. |
| `docs/architecture/ADS-002-infinite-mode-combat-sub-mode.md` | Its Open Question 1 (does the Vision tolerate combat, and in what tone?) is now answered | `03-architecture-design-synthesis` | Not edited here — the next `03` touch on this cluster should mark Open Question 1 resolved and proceed to a fuller architecture pass (mob/weapon/health entities, gating mechanism) now that C11 exists to design against. |
| `docs/pipeline/backlog.md`, `BL-0133` | Its `NEEDS-USER` disposition is resolved | `00-pipeline-manager` | Re-dispositioned on the next pipeline-manager harvest, not this skill's own write scope. |
| Every existing FR/FS/GDS level describing the base game (`FS-102`/`FS-103`/`FS-110` etc.) | Unaffected — C11 is additive, scoped to a not-yet-existent combat mode; no existing requirement/spec references combat | none | No action — confirmed by direct search (zero prior mentions of mob/enemy/combat/weapon/health/damage anywhere in `docs/requirements/`/`docs/features/` before `BL-0133`). |

### Full downstream blast radius of the 1.0 → 2.0 revision

Everything below was authored, or is otherwise exposed, on the basis of the now-superseded v1.0
description (3 zones, "gifts," "BunnyGarden" naming) or is independently found stale by the same
investigation:

| Artifact | Exposure | Owning skill | Recommended action |
|---|---|---|---|
| `docs/architecture/00-vision.md` (GDS-00) | Repeats "three-zone play," "v2.1," old naming | `01-vision` | **Fixed in this same run** — see below. |
| `docs/architecture/strategic-assumptions-register.md` | A1 (32KB) needs its framing updated for C7; A6 referenced the old bug set and "v2.1" | `01-vision` | **Fixed in this same run** — see below. |
| `docs/pipeline/backlog.md` — **BL-0001, BL-0002, BL-0003** | Filed against the *old* game's specific code (old map-heart BG addresses, old 2-sprite bunny, old score-write path) — the current `tilemaps.py`/`asm_game.py` implement the map screen and score bar completely differently now; these three entries need **re-verification against current code**, not automatic carry-forward. | `00-pipeline-manager` (triage) | Re-open at next triage; do not implement as literally filed. |
| `docs/pipeline/backlog.md` — **BL-0004** | Scoped to reconciling `BunnyGarden_build_rom.py`/`BunnyGarden_logic.json` against "the modular chain" — still correct, but the modular chain itself has moved on, and there is now **also** a stale `BunnyGarden.gbc` binary at the repo root (superseded by `BunnyQuest.gbc`, which matches current source) that needs the same archival treatment. | `00-pipeline-manager` (triage) | Widen BL-0004's scope to include `BunnyGarden.gbc`. |
| `docs/pipeline/backlog.md` — **BL-0005** | Still accurate as filed (hardcoded paths) — **and now compounded**: `test_rom.py`'s hardcoded `ROM_PATH` points at `BunnyGarden.gbc` (the *stale* ROM name), not `BunnyQuest.gbc`. Fixing the path portability without also fixing the filename would leave the suite testing the wrong binary. | `00-pipeline-manager` (triage) → `07-implementation-planning` | Amend BL-0005's scope to include the ROM filename, not just the path. |
| **`test_rom.py`** (new finding, not in the original five) | Asserts pre-rewrite WRAM semantics — `CUR_ZONE` bounded to 0–2, victory at a 3-bit `GIFTS` bitfield (`GS=5` when `GIFTS==7`) — against code that now uses `CUR_ZONE` 0–8 and a 9-byte `CARROT_FLAGS` array with victory at `CARROTS_COUNT==9`. **The G5 permanent gate cannot currently be satisfied**: the suite tests behavior the code no longer has. `test_results.txt`'s "88/88 passed" is a stale artifact, not evidence about the current tree. | `00-intake` → `07-implementation-planning` | **File as a new, high-severity backlog entry** — this blocks every future stage-08/09 run's G5 gate until remediated. Recommend prioritizing above BL-0001/0003/0005. |
| `Claude.md`, `memory.md`, `README.md` (repo-root working docs) | Describe the old game throughout (WRAM map, tile index map, zone names, "v2.1," known-good-behavior list) | not owned by any pipeline skill directly — the GDS ladder absorbs sections over time per each level's merge decision | **File as a new backlog entry** (doc-defect, high — these are the primary onboarding docs and are actively misleading right now). Likely fastest fix: a dedicated `07`/`08` documentation-refresh package once GDS-01/04/05 re-baseline against the real code. |
| `docs/pipeline/pipeline-journal.md` run #1's Position block | Recorded "Stage 01 ✅ complete" against the now-superseded v1.0 content | `00-pipeline-manager` | Journal this correction as its own run; do not silently overwrite run #1's history — append, as always. |

**Everything downstream of vision that hadn't been authored yet** at v2.0 (research tiers, the
GDS-01…10 ladder, requirements, features, packages) was **unaffected in the sense that nothing
needed unwinding** — none of it existed yet. The 1.0→2.0 correction landed before any of that
work was done, the cheapest possible time for a vision correction to land.

### Full downstream blast radius of the 2.0 → 3.0 revision

Unlike the 1.0→2.0 correction, **this revision lands on a fully-authored downstream tree** —
the GDS-00…10 ladder, all four research tiers, the requirements baseline, feature planning, and
five implemented packages all exist and describe the *pre-v3.0* game. Every artifact below cites
a statement this revision changed or is a named consumer of the new commitments; none of it is
edited by this run (out of `01-vision`'s scope) — each row names its owning skill and the next
action, per the adopted increment plan's own phased path.

| Artifact | Exposure | Owning skill | Recommended action |
|---|---|---|---|
| `docs/architecture/00-vision.md` (GDS-00) | Restates C1/C2/C5/C7 at their pre-v3.0 shape (auto-load, fixed 3×3 baseline, C7 as an unshaped direction) | `01-vision` | **Fixed in this same run** — see below. |
| `docs/architecture/strategic-assumptions-register.md` | A1's framing, A5/A7's scope, A6's "intended design" statement, and the absence of a determinism assumption all predate C8–C10 | `01-vision` | **Fixed in this same run** — see below. |
| `docs/architecture/01-concept-of-play.md` (GDS-01) | §2 "auto-loads directly into PLAYING," §3's carrot-specific core loop, §4's state machine (no main menu state), 3×3-only zone list | `03-architecture-design-synthesis` | Phase 3 of the adopted plan: game-flow delta (D7–D10), biome-flow-structured core loop (C9), item-agnostic goal language. |
| `docs/architecture/03-architecture.md` (GDS-03) + `docs/architecture/adr/` | No ADR yet covers world generation, seed/scale, or the bank-switching strategy C9/C10 now require | `03-architecture-design-synthesis` | Phase 3: world-generation ADR, seed & scale ADR, bank-switching ADR (per the adopted plan §2 Phase 3). |
| `docs/architecture/04-domain-model.md` (GDS-04) | Zone/Carrot entities are fixed-count and carrot-specific; no Seed/WorldScale/Region/KeyItem entities, no adjacency-grammar rule | `03-architecture-design-synthesis` | Phase 3: new/changed entities per the adopted plan §2. |
| `docs/architecture/07-data-model.md` (GDS-07) | WRAM/SRAM tables assume fixed 9-zone `CARROT_FLAGS`/`SCOREITEM_FLAGS`; no seed/scale persistence | `03-architecture-design-synthesis` | Phase 3: data-model delta, save-format version bump (FS-101 precedent). |
| `docs/architecture/08-presentation-architecture.md` (GDS-08) | Palette strategy is correct but was never evaluated against a mandatory smooth/clean standard (C8) or a biome-adjacency palette-stepping requirement (C9) | `03-architecture-design-synthesis` | Phase 3: normative aesthetic standard + biome-transition presentation delta. |
| `docs/requirements/` (RQ-01…04) | `FR`s state the fixed 9-carrot goal and auto-load as requirements; no FRs exist for C8/C9/C10 | `04-requirements-engineering` | Phase 4: the increment's own requirements delta — the plan's terminal deliverable. |
| `docs/feature-planning/01-release-plan.md` (FP-01) | Release 2+ buckets are empty; this increment populates them | `05-feature-decomposition` | After Phase 4 closes, per the adopted plan's own stated boundary (out of this plan's scope). |
| `docs/pipeline/backlog.md` — **BL-0015** | Recorded "wider vs deeper" as an open, deferred design fork | `00-pipeline-manager` | **Already closed** (run #30, 2026-07-09) — C10's user-adjustable scale dissolves the fork; not re-opened by this vision run. |
| `docs/pipeline/backlog.md` — **BL-0029/BL-0030/BL-0031** | The three seed entries this revision's commitments (C8/C9/C10) formalize | `00-intake` (filed) → `01-vision` (this run) | **This run's direct subject** — flip to `IN PIPELINE`/`DONE` per the pipeline manager's next harvest; downstream work (research/architecture/requirements) is Phase 2–4, not this run. |
| `test_rom.py` | Asserts `CARROT_FLAGS`/`CARROTS_COUNT==9` and the current auto-load-on-boot behavior as permanent facts — both are the **named subject** of C10/C2's amendment | `08-code-implementation`/`08-content-authoring` | Not touched by v3.0 architecture/requirements work — updates land only when the corresponding implementation packages ship (`07`→`08`), per the pipeline's normal gates; the *current* suite stays the accurate G5 gate for the *current* shipped code until then. |
| `Claude.md`, `memory.md`, `README.md` | Just refreshed (`IP-9030`, this same day) to describe the pre-v3.0 shipped game accurately — **that description remains correct** (v3.0's commitments are forward-looking targets, not yet built) | not owned by any pipeline skill directly | No action now — these stay accurate for the shipped code; a future doc-refresh package updates them once C8–C10 actually ship, exactly as `IP-9030` did for the Bunny Quest rewrite. |

**Contrast with the 1.0→2.0 revision:** that correction fixed a vision that had *misdescribed
already-shipped code*. This revision **adds forward-looking commitments** (C8/C9/C10, C2
amended) that *nothing downstream implements yet* — the shipped game, its tests, and its docs
all remain accurate descriptions of the pre-v3.0 baseline. Nothing here is "wrong" the way
v1.0 was; the blast radius above is downstream artifacts that will need their own dated passes
to actually build toward the new commitments, not artifacts to urgently correct.
