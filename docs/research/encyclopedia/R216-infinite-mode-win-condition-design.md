# R216 — What "Infinite" Means for Win Conditions, Session Length & Treasure Placement

- **Document ID:** R216 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R215 (the finite-world win-condition Decision this topic extends to the
  streaming/unbounded case — the project owner's own message that produced `BL-0093`/`BL-0094`
  addressed both in one breath), R206 (session-length/pacing conventions for handheld play, which
  an unbounded mode stresses in a genuinely new way), R201 (the tiered collect-a-thon structure the
  finite game already established), R114 (the hardware-feasibility research this topic is
  downstream of — its finding that the cheapest streaming-compatible maze algorithm has a
  structural dead-end bias is this topic's own starting problem)
- **Referenced By:** *(none yet — grounds `BL-0082`'s design half and `BL-0094`'s own deferred
  decision)*
- **Produces:** an evidence-grounded answer to what "infinite" should mean for `BL-0094`'s already-
  recorded intent (dead-end-only treasure, top-3 high score, no name entry) once `R114`'s maze-
  algorithm finding is taken into account; a proposed resolution to the dead-end-bias conflict;
  what "practically infinite" means given `R114`'s own finding that nothing about this project's
  hardware supports truly unbounded persisted state
- **Feature Mapping:** *(none yet — exploratory research, no `FS-xxx` authored)*
- **Related Topics:** R201, R206, R213, R215, R114

## Purpose

Filed to ground the design half of `BL-0082`, per this session's own task ordering: "what
'infinite' means for win conditions, since `BL-0094`'s own deferred design... depends on this."
The project owner's own message that produced `BL-0093` (the finite win condition, now shipped as
`IP-1021`) and `BL-0094` (the infinite-mode design, explicitly deferred) addressed both in the same
breath: "Distribute a minimum of 'scale number' of treasures, starting at dead ends... win
conditions are 'collect scale number of treasures'" for the finite case, immediately followed by
"In an infinite game, populate a treasure only at dead ends and save the top 3 high scores... but
don't implement now" for the unbounded case. `BL-0094`'s own text already anticipated the right
genre precedent (R215's Concepts section: "the 'switch to score-chasing' pattern... a real,
precedented convention for unbounded play") — this topic grounds that precedent properly and
resolves the one concrete conflict `R114` surfaced since: the cheapest streaming-compatible maze
algorithm found (Binary Tree) has zero dead ends in two of four directions, in tension with a
dead-end-anchored treasure rule carried forward unmodified from the finite design.

## Scope

Win-condition/scoring conventions specifically for procedurally-generated, effectively-unbounded
play (score-attack/high-score conventions, not completion conventions — R215 already covers the
finite/bounded case and is not re-litigated here); the interaction between `R114`'s maze-algorithm
finding and `BL-0094`'s dead-end-only treasure rule; session-length/pacing implications of a mode
with no defined end; what "infinite" can honestly mean given `R114`'s own finding that a
streaming-compatible world still needs a bounded, SRAM-capacity-limited visited-region ledger to
save/load correctly. **Out of scope:** the streaming generation architecture itself (`R114`'s own
territory), deciding the actual formula/UI (a `03`/`04` call), and biome-blob-clustering aesthetics
(`BL-0066`, `02-research-game-design`'s own future pass once a streaming model is architecturally
adopted — this topic touches it only where it bears on treasure placement).

## Concepts

**Score-chasing over a fixed win condition is the historically correct genre answer for
non-terminating play, not an improvised compromise.** Arcade games, "because of technical
limitations... could not be 'won' or 'completed' but were instead endless cycles of continuous
gameplay" — the score system exists precisely to give an unwinnable, non-terminating game a
meaningful goal: "not only was it a thrill to see yourself on top, [the high score table] also
gave arcade goers a reason to return."[^1] This is a direct structural match to what an unbounded
streaming world produces: a game with no generation-defined endpoint (there is no "last region," by
construction) needs a goal that does not require reaching one — exactly the property a persisted
high score already supplies. `BL-0094`'s own top-3 high score design is therefore not a fallback
improvisation but the standard answer this genre problem has had since the 1970s arcade era,[^1]
independently re-derived by the project owner.

**Persistent-name high-score entry is a convention this project can reasonably skip without losing
the core mechanic.** The classic 3-character-initials-entry UI is itself a historical artifact of
shared arcade cabinets (proving *who* achieved a score to other players at the same machine) —
"Star Fire allowed players to save their name as initials next to their high score" as an early
example of the convention once it appeared.[^1] A single-player handheld cartridge with one save
slot has no equivalent audience to perform the "whose initials are on top" social function for —
the convention's own original purpose does not transfer. `BL-0094`'s own explicit deprioritization
of the name-entry UI ("deprioritize saving a three character name... but don't implement now") is
therefore well-grounded, not merely an implementation-effort shortcut — tracking the numeric top-3
alone preserves the goal-giving function of a high score while skipping a UI element whose original
purpose (multiplayer cabinet bragging rights) doesn't apply here.

**The R114 dead-end-bias conflict has a clean resolution that also simplifies the architecture:
decouple treasure placement from maze structural properties entirely.** `R114` found the cheapest
streaming-compatible maze algorithm (Binary Tree) "has a strong north-west bias... no dead-ends
(and never will be any dead-ends) facing either north or west" — a `BL-0094` design built on
"treasure only at maze dead ends" would, under that specific algorithm, systematically place all
treasure toward two of four compass directions from any given region, a real and visible bias a
player would eventually notice. But `R114` *also* already established the tool needed to sidestep
this entirely: a per-region deterministic value derived from `hash(SEED, row, col)` via
shift/XOR-only mixing (no multiplication — SM83 has none), used there for biome/blob positional
determinism. **The identical technique answers treasure placement without any dependency on which
maze algorithm gets chosen**: a region holds treasure if `hash(SEED, row, col) mod K == 0` for some
tuned density constant `K` (e.g. roughly 1-in-6 to 1-in-10 regions, informed by R215's own measured
dead-end density at finite scales, §Operational Context below) — independent of connectivity,
computable the instant a region is materialized, and immune to whichever maze algorithm
`03-architecture-design-synthesis` eventually picks for streaming generation. This is consistent
with established procedural-loot practice: probability-driven, density-controlled placement
("weighted tables," "probability heatmaps") is a normal, well-precedented alternative to placement
tied to structural landmarks, used specifically because it decouples content density from layout
algorithm choice.[^2] **This is a genuine design proposal this topic contributes, not merely a
literature summary** — presented as a grounded candidate for `03`/`04` to weigh, not a decision:
it trades `BL-0094`'s literal "at dead ends" framing (rewarding players who find true maze
dead-ends specifically) for "at a tuned density, independent of structure" (rewarding exploration
generally, not maze-solving specifically) — a real, named tradeoff, not a free win.

**A genuinely unbounded win-condition mode still needs a knowable, bounded session shape — R206's
pacing concerns don't disappear just because the world does.** Handheld play favors "short,
repeatable gameplay loops" fitting interruptible playtime, not indefinitely open commitments
(R206). A score-attack mode with no generation-defined end is not automatically at odds with this —
arcade score-attack is itself inherently session-based (one life, one credit, one run, checked
against a table)[^1] — but the *save/resume* behavior matters more here than in the finite game:
a streaming world has no natural "I've finished this playthrough" moment the way collecting
`WORLD_SCALE` treasures gives the finite mode. A future spec pass should decide whether an infinite
run is expected to be resumed indefinitely (matching this project's existing save/continue
convention) or is itself a bounded "run" that ends deliberately (a death/retreat/checkpoint
mechanic this game does not currently have) — this topic surfaces the question, deliberately
does not answer it, since it is a genuine new mechanic decision outside a pure win-condition-scaling
scope.

**"Infinite" is not literally infinite on this hardware, and the win-condition design should be
honest about that rather than imply otherwise.** `R114` already found that even a fully
positionally-deterministic streaming world cannot persist unbounded per-region state — save/load
needs "a bounded-by-SRAM-capacity visited-region ledger, not a flat whole-grid array." The
practical meaning of "infinite" here is **unbounded exploration extent with bounded persisted
memory of it** — the same shape real "infinite" games actually ship (a Minecraft world is not
infinitely saved either; chunks regenerate deterministically from seed when unvisited, and only
player-caused mutations are actually persisted[^3], directly mirroring `R114`'s own recommended
shape: regenerate biome/maze from `(seed, coordinate)`, persist only collected/absent treasure
state for regions actually visited). A high-score-chasing win condition is a good fit for this
constraint specifically because it needs no unbounded state of its own — "current running count"
and "top 3 recorded scores" are small, fixed-size fields, unlike a hypothetical "collect
everything" condition that would need to track collection state for every region ever generated.

## Operational Context

R215's own measured dead-end density data (§Addendum, 200-seed sample per scale, current
finite-world spanning-tree algorithm) remains the best available empirical grounding for tuning a
density constant, even though it was measured against a different (recursive-backtracker) maze
algorithm than whichever gets chosen for streaming: mean dead-end density ranges from ~1.5 per 4
regions (`scale=2`, 37.5%) down to ~5.2 per 81 regions (`scale=9`, ~6.4%) — density *decreases* as
the graph grows, the same "grows much slower than region count" finding R215 already names. A
tuned `hash`-based density constant for the infinite mode should land in a comparable low-single-
digit-percent range at large extent (closer to the `scale=9` end of R215's table, since an
unbounded world is unboundedly large) rather than the small-world end, to avoid treasure feeling
either too sparse (large gaps between finds, working against R206's short-loop preference) or too
dense (undermining the "genuinely enumerable, individually meaningful" scarce-tier property R201
established for the finite game). The exact constant is an implementation-time tuning question, not
resolved here.

## Implementation Guidance

- **Recommend adopting `BL-0094`'s own score-chasing shape as specified (running count + top-3
  persisted, no name-entry UI) — it is genre-correct, not merely convenient.** No change to that
  part of the design is suggested by this research.
- **Recommend resolving the `R114` dead-end-bias conflict by decoupling treasure placement from
  maze structural dead-ends entirely**, using the same per-region `hash(SEED, row, col)`-derived
  positional value `R114` already established for biome/blob determinism — a region is a treasure
  region if that hash satisfies a tuned density predicate, independent of its connectivity degree.
  This removes the dependency on which maze algorithm `03` eventually picks for streaming
  generation (Binary Tree's bias becomes irrelevant to treasure placement specifically, though it
  would still bear on maze *feel* generally — a separate, `02-research-game-design`-owned aesthetic
  question for whenever streaming generation is actually adopted). **This is a genuine departure
  from `BL-0094`'s literal "at dead ends" wording** — flag this explicitly to the user/`03` rather
  than silently substituting it, since "dead-end hunting" and "tuned-density exploration reward"
  are different player experiences, not interchangeable phrasings of the same mechanic.
- **Tune the density constant in the low-single-digit-percent range** (informed by R215's own
  `scale=9` dead-end density, ~6.4%, as a starting anchor — not a binding number, an
  implementation-time tuning question) rather than reusing a small-world density figure, since an
  unbounded world's extent only grows.
- **Decide the run/session shape explicitly before implementing** — whether an infinite-mode
  playthrough is indefinitely resumable (matching the finite game's existing save/continue
  convention) or is its own bounded "run" needing a new end-condition mechanic (death/retreat/
  checkpoint) this game does not currently have. This is new mechanic-design scope this topic
  surfaces but does not resolve.
- **State plainly in any future spec that "infinite" means unbounded exploration extent with
  bounded persisted memory of it**, not literally unbounded save data — matching `R114`'s own
  recommended visited-region-ledger shape and the real precedent other "infinite" games actually
  ship.[^3] Avoid marketing/spec language implying the save file itself grows without bound.

### Sources
[^1]: [Anatomy of Arcade High Score Tables — The Arcade Blogger](https://arcadeblogger.com/2021/01/31/anatomy-of-arcade-high-score-tables/); [Scoring Points — TV Tropes](https://tvtropes.org/pmwiki/pmwiki.php/Main/ScoringPoints); [Score (video games) — Wikipedia](https://en.wikipedia.org/wiki/Score_(video_games)); accessed 2026-07-13 via `WebSearch` summary. Corroborated across three independent sources describing the same arcade-era score-as-goal convention and the Star Fire initials-entry precedent.
[^2]: [Creating Dungeon Generation Algorithm — Procedural Dungeon Wiki](https://benpyton.github.io/ProceduralDungeon/guides/Best-Practices/Workflows/Dungeon-Generation-Algorithm); accessed 2026-07-13 via `WebSearch` summary — general procedural-loot-placement practice (weighted/probability-driven placement independent of structural landmarks); single search-summarized source, flagged below.
[^3]: [The World Generation of Minecraft — Alan Zucconi](https://www.alanzucconi.com/2022/06/05/minecraft-world-generation/); accessed 2026-07-13 via `WebSearch` summary (same source `R114` already cites for the coordinate-hashing/chunk-regeneration pattern this topic reuses).

**Single-source flag:** the general procedural-loot-density-independent-of-structure claim ([^2])
rests on a single `WebSearch`-summarized source describing common industry practice in general
terms, not a specific named title's postmortem — presented here as supporting context for this
topic's own proposed design (decoupling treasure from maze structure), not as the load-bearing
evidence for it; the load-bearing evidence is the internal conflict `R114` already established
(cited directly) plus the same hashing technique `R114` already grounds with its own corroborated
sources. The arcade high-score citations ([^1]) are corroborated across three independent sources.
R215's own dead-end density table (§Operational Context here) is Tier-A, re-cited directly from
that topic's own prior measurement, not re-derived.

## Feature Mapping

*(No `FS-xxx` authored yet — this grounds `BL-0094`'s own deferred design and `BL-0082`'s
research-gap entry; both remain blocked on `03-architecture-design-synthesis` actually adopting
streaming generation before any spec work begins.)*

## Related Topics

R201 (the finite game's tiered collect-a-thon structure, the baseline this topic's score-chasing
alternative departs from) · R206 (session-length/pacing conventions, extended here to a mode with
no generation-defined end) · R213 (the graph-generation family whichever streaming maze algorithm
is chosen still belongs to) · R215 (the finite-world win-condition research and its own dead-end
density data, reused here as the density-tuning anchor for the infinite case) · R114 (the
hardware-feasibility research whose maze-algorithm finding this topic's own dead-end-bias
resolution directly answers).
