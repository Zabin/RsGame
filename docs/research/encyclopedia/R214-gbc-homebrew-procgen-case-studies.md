# R214 — GBC Homebrew & Era Titles Using Procedural Map Generation

- **Document ID:** R214 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R213 (the algorithm families these case studies exemplify), R106 (MBC1/SRAM,
  banking), R211 (comparative visual-design case studies — the sibling "what has this hardware
  class actually shipped" methodology)
- **Referenced By:** none yet
- **Produces:** feasibility evidence for R213's screen/room-graph generation recommendation;
  answers D3's explicit "existing GBC homebrew games that use procedurally generated maps" ask
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R213, R106, R211, R201

## Purpose

**Filed per MSTR-001 C10/D3** (owner's explicit instruction, 2026-07-08/09, recorded in the
adopted increment plan's §0): name concrete GBC/GB-class homebrew and commercial-era games that
use procedurally generated maps, as feasibility precedent for this project's own procgen-world
commitment — the sibling of R211's "what has this hardware class shipped, and what does it prove
is achievable" methodology, applied to procedural generation instead of visual polish.

## Scope

Homebrew and commercial GB/GBC-class titles using procedural/seeded map or dungeon generation;
what is known about *how* each generates content (granularity, memory approach) where available;
what each proves feasible for this project's own generator. Out of scope: the algorithm theory
itself (R213) and non-GB-class titles (covered generically in R213 only where they ground
algorithm concepts, not as GBC feasibility evidence).

## Concepts — the case studies

**Roguecraft GB** (homebrew, Badger Punch Games / Thalamus Digital Publishing, built with/for
Game Boy Color) is the **strongest and most directly load-bearing precedent** this research found.
It is "an award-winning, retro-inspired, turn-based roguelike that explores procedurally
generated dungeons... each run is procedurally generated, assembling large dungeon maps from
interconnected rooms."[^1] Concretely: **ten procedurally generated levels, each a 5×5 room
map**, with monster/loot/trap placement scattered through the generated rooms, and **persistent
state** — "monsters stay dead and loot stays collected."[^1] Critically, this is a **ported
implementation, adapted specifically for GBC's real constraints**: "the developer ported the
Amiga algorithm to C and tried to fit all the room types into the Game Boy's memory," describing
"a huge amount of data to juggle... certainly more than anything the developer had previously
done," requiring "careful management of the Game Boy's limited memory constraints to accommodate
the extensive procedural generation system and game state tracking."[^2] A retrospective
assessment frames the achievement directly: the port "demonstrates that technical limits don't
have to be barriers and that thoughtful design and deep understanding of the hardware can produce
something genuinely special."[^2] This is **exactly R213's recommended shape** — a
**room/screen-graph generator** (5×5 room map = a small graph, not a per-tile canvas) — proven to
fit real GBC memory constraints in a shipped, award-winning homebrew title, not a theoretical
claim.

**Azure Dreams** (Game Boy Color port of the PlayStation dungeon-crawler/monster-taming hybrid):
"the main dungeon was a graphical roguelike" on the GBC port, per a handheld-roguelike survey
listing it alongside other console/handheld roguelike adaptations.[^3] This is a **commercial**
(not homebrew) precedent that regenerating dungeon content on GBC-class hardware shipped in a
retail title, broadening the evidence base beyond the homebrew scene alone — though this research
pass could not directly verify further technical detail (generation granularity, memory approach)
beyond the brief survey mention; flagged below.

**Dragon Crystal** (Game Boy, monochrome — not GBC-specific, but the same handheld hardware
lineage this project's SM83/R101 grounding already covers) is noted in the same survey as
"similar to Fatal Labyrinth on the Genesis"[^3] — i.e., a Mystery-Dungeon-lineage roguelike with
regenerating floors, further broadening the "this genre and mechanic has shipped on this hardware
family" evidence, again with limited directly-verified technical detail this pass.

**Historical context for the whole genre on this hardware class:** procedural content generation
was *invented* specifically as a response to the kind of memory constraint this project itself
faces — "initially adopted in early titles such as *Rogue* and *Maze Craze*, where limited system
resources were the primary constraint... using seeds and rules to generate larger worlds
dynamically while reducing memory and storage requirements."[^4] The GB/GBC-class titles above are
a direct continuation of that same motivation onto handheld hardware, not a novel or risky
departure from genre convention.

### Sources
[^1]: [Roguecraft GB — Badger Punch Games](https://www.badgerpunch.com/title/roguecraft-gb-gbc/); corroborated by [Roguecraft GB (Game Boy Color) — Thalamus Digital Publishing, itch.io](https://thalamusdigital.itch.io/roguecraft-gb-game-boy-color); accessed 2026-07-09 via WebSearch summary.
[^2]: [Roguecraft GB | GB Studio Central (interview)](https://gbstudiocentral.com/interviews/roguecraft-gb/); accessed 2026-07-09 via WebSearch summary. **Direct page fetch attempted this session and returned HTTP 403** — the quoted developer statements above are drawn from the WebSearch tool's own summary of the page content, not independently re-verified against the fetched primary text. Treat the *existence and general shape* of the technical achievement as reliable (corroborated by [^1]'s independent listing pages), but the specific developer quotes as needing re-verification if cited with higher confidence than "directional feasibility evidence."
[^3]: [List of handheld roguelikes — RogueBasin](https://roguebasin.com/index.php/List_of_handheld_roguelikes); accessed 2026-07-09 via WebSearch summary. **Direct page fetch attempted this session and returned HTTP 403.** This is the single weakest citation in this topic — a brief survey-page mention with no independently corroborating second source found this pass. **Single-source flag.**
[^4]: See [R213](R213-procedural-map-generation-algorithms.md) §"Historical grounding" for the full citation and its own needs-fetch-verification flag; repeated here only as cross-context, not re-cited independently.

**Single-source flag:** Azure Dreams and Dragon Crystal (§[^3]) rest on one survey-page mention
each, not independently corroborated this pass — cite as *suggestive* breadth evidence ("this
mechanic has precedent beyond the homebrew scene"), never as detailed design precedent to copy
from. Roguecraft GB (§[^1]/[^2]) is corroborated across two independent listing sources for its
existence and headline mechanics, though the specific developer-quoted implementation details
rest on a page this session could not directly fetch (HTTP 403) — treated as the strongest
available evidence, not an unverifiable one, per the corroboration from [^1].

## Operational Context

This project has no procedural-generation precedent of its own to compare against — every
existing screen (`tilemaps.py`) is hand-authored. Roguecraft GB is the single most relevant
comparison point available: **same hardware class (GBC), same general shape (a world assembled
from discrete rooms/screens rather than a continuous tile canvas), same core motivation (fit
within real memory constraints)** — directly parallel to this project's own screen-composed
architecture (GDS-04/07) and R213's screen/room-graph generation recommendation.

## Implementation Guidance

- **Cite Roguecraft GB as the primary feasibility precedent when the Phase 3 world-generation ADR
  justifies choosing screen/room-graph generation over per-tile approaches** (R213's
  recommendation) — it is the closest available proof that this exact generation granularity
  ships successfully within real GBC hardware constraints, not merely a theoretical fit.
- **Do not treat Azure Dreams/Dragon Crystal as design templates** — both are combat-focused
  dungeon-crawler roguelikes, a different genre from this project's exploration/collection loop
  (MSTR-001 C9/FEAT-3000's core loop); cite them only for the narrow claim "seeded/regenerating
  content has multiple independent precedents on this hardware family," not for any mechanic or
  layout choice.
- **Treat memory-budgeting as the load-bearing lesson from Roguecraft GB's account**, not the
  specific algorithm — "fit all the room types into the Game Boy's memory" is exactly the kind of
  concrete, hardware-grounded concern this project's own ROM-headroom tracking (`BL-0019`,
  MSTR-001 §7) already watches; a future implementation package should budget generator code +
  region-template data against remaining headroom explicitly, following that precedent's
  demonstrated discipline rather than assuming procedural generation is automatically cheap.
- **Revisit this topic if a future design question needs deeper technical detail than a survey
  mention provides** — specifically, a direct (non-403'd) fetch of the GB Studio Central
  interview or a hands-on teardown of Roguecraft GB's actual ROM would strengthen [^2]'s citation
  from "directional" to "verified," worth doing before any package that copies a specific
  Roguecraft GB technique rather than just its general feasibility conclusion.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R213 (the algorithm families this topic supplies feasibility evidence for, esp. the room-graph
recommendation) · R106 (MBC1/banking headroom — the same constraint Roguecraft GB's account
describes managing) · R211 (the sibling "what has this hardware class shipped" case-study
methodology, applied to visual design rather than generation) · R201 (goal/structure design —
Azure Dreams/Dragon Crystal's genre context).
