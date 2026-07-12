# R215 — Win-Condition Design for Procedurally Generated, Variable-Size Worlds

- **Document ID:** R215 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R201 (the tiered collect-a-thon structure this topic re-examines under
  scaling), R213 (the spanning-tree-plus-braid generator whose reachability guarantee this
  topic's recommendations lean on), R206 (session-length/pacing constraints a win condition must
  respect)
- **Referenced By:** none yet
- **Produces:** the citation-grounded evidence a future `03`/`04`/`06` pass needs to redesign
  `CARROTS_COUNT`'s victory check for a scale-driven world; unblocks `BL-0050` (the MAP/
  status-screen redesign, which the project owner says can't be meaningfully designed until the
  win condition is settled)
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R201, R206, R213, R214

## Purpose

Filed to ground `BL-0081` (project-owner research request): the shipped win condition
(`CARROTS_COUNT == 9`, `asm_game.py`) is an unexamined holdover from the pre-procgen fixed
3×3/9-zone map — one carrot per zone, nine zones, nine carrots to win. `FEAT-9000`'s procedural
world generation (`IP-1020`) replaced the fixed 9-zone map with a `WORLD_SCALE`×`WORLD_SCALE` grid
(`WORLD_SCALE` 2–9, so 4–81 regions) and made **one carrot per region** the shipped placement rule
(`ZONE_COLLECTS`'s per-region assignment, `FS-102`), but the *victory threshold* was never
updated to track `WORLD_SCALE` — it is still the literal constant `9`. R201 itself flagged this
exact risk in advance ("the moment a future world-scale expansion makes 'one carrot per zone'
produce, say, 40+ carrots... a 'collect everything' goal only stays motivating if the player can
always see how many remain," and "consider a partial-victory threshold once the scarce tier grows
large enough") — this topic is the follow-through R201 deferred, now that the scaling has
actually shipped and the gap is a live, reproducible defect (`BL-0081`).

## Scope

Win-condition/goal-scaling conventions for collect-a-thon and exploration games whose playable
area is not fixed size — procedurally generated dungeons/overworlds, Metroidvania completion
tracking, open-world exploration goals — evaluated against Bunny Quest's specific shape: a small,
short-session handheld game (R206) with a fully-enumerable scarce-collectible tier (R201) laid
over a deterministic, always-fully-reachable generated grid (R213/`FR-9140`). Out of scope:
deciding the actual new win-condition formula (a `04-requirements-engineering`/
`03-architecture-design-synthesis` call, not a research conclusion) and the MAP/status-screen
redesign itself (`BL-0050`, a separate, dependent backlog item this topic's own recommendation
unblocks but does not resolve).

## Concepts

**Fixed goal nodes vs. fully-enumerable collection.** Most classic roguelikes anchor victory to a
single fixed objective reached *through* procedural generation rather than *by* enumerating it —
retrieving an item at the deepest generated level, or defeating a boss that always exists at a
specific structural position (the last floor, the far end of a fixed number of biomes) — so the
goal's *definition* stays constant even though the *path* to it is regenerated every run.[^1] This
decouples "win condition" from "world size" entirely: a 4-region world and an 81-region world can
share the identical goal statement ("reach the region furthest from spawn" or "reach the
generator's designated goal region"), because the goal is structural, not a count.

**Percentage/threshold completion.** Metroidvania-style completion tracking counts collected
items against the *actual* total generated for that playthrough (not a fixed constant) and
presents a percentage, often allowing partial completion (Super Metroid's 100% is calculated from
that run's own 80-item total; Castlevania titles routinely track completion above 100% via
overlapping/bonus systems).[^2] This pattern is inherently scale-relative by construction — the
denominator *is* however many collectibles the run actually generated — which is exactly the
property `CARROTS_COUNT == 9` lacks today (it hardcodes the denominator from the old fixed-map
shape instead of reading `WORLD_SCALE²`, the actual current region/carrot count).

**Sliding/scaled numeric thresholds.** Where a full 100%-of-everything bar doesn't fit a genre's
pacing, games commonly set a *partial* threshold that scales with the generated content rather
than requiring exhaustive collection — the same "70 of 120 stars" shape Mario 64 established and
R201 already cited as the applicable precedent once a scarce tier grows past what one sitting can
reasonably exhaust.[^3] Pacing research generally favors *concrete, knowable* goals/checkpoints
over open-ended ones, since players build anticipation around a stated target rather than an
ambiguous "explore until satisfied" objective.[^4]

**Modern open-world design generally avoids mandatory full-map-exploration win conditions.**
Contemporary open-world titles treat exploration as optional and rewarding rather than a gating
requirement, reserving hard completion percentages for genres (Metroidvania, roguelike) where the
playable space is small and enumerable enough that 100% stays a reasonable ask — evidence against
adopting a raw "% of world explored" win condition for a genuinely large `WORLD_SCALE=9` (81-region)
world, though this pattern doesn't rule out scale-relative *thresholds below 100%*.[^5]

### Sources
[^1]: [Roguelike Level Design: Static or Procgen? — Cogmind / Grid Sage Games](https://www.gridsagegames.com/blog/2019/03/roguelike-level-design-addendum-static-procedural/), accessed 2026-07-12; [Roguelike — Wikipedia](https://en.wikipedia.org/wiki/Roguelike), accessed 2026-07-12.
[^2]: [8 Games With Completion Percentages That Go Above 100% — Game Rant](https://gamerant.com/games-over-100-completion-percentage/), accessed 2026-07-12; [Super Metroid 100% — Speedrun Progress Tracker](https://www.kennycason.com/posts/2025-09-16-super-metroid-100pct.html), accessed 2026-07-12.
[^3]: R201 §Implementation Guidance (Mario 64's 70-of-120 pattern, already cited there to The Artifice's collectathon retrospective).
[^4]: [Dimensions of Games – Pacing](https://www.gamesprecipice.com/pacing/), accessed 2026-07-12 (also cited by R206).
[^5]: [Open World Game Design: Pacing, Points of Interest, and Player Freedom — StraySpark](https://www.strayspark.studio/blog/open-world-design-pacing-player-freedom), accessed 2026-07-12; [Open world — Wikipedia](https://en.wikipedia.org/wiki/Open_world), accessed 2026-07-12.

## Operational Context

Confirmed directly against the shipped code and `worldgen.py`'s oracle:

- **The actual generated carrot count today is `WORLD_SCALE²`, not 9** — one `Carrot` per region
  (`ZONE_COLLECTS`, `FS-102`), and region count is exactly `WORLD_SCALE × WORLD_SCALE`
  (`ADR-0010`). At the minimum `WORLD_SCALE=2`, that's 4 carrots — the player can already win with
  fewer than a real 9-carrot playthrough required, an *easier*-than-intended win, not just a
  scaling omission. At `WORLD_SCALE=9`, that's 81 carrots, but the check still only requires 9 of
  them — an *easier*-than-100% win by a wide margin, and (per `BL-0081`'s own filing) satisfiable
  from adjacent starting regions without traversing the generated maze at all.
- **Every carrot is guaranteed reachable from spawn.** `FR-9140`'s own postcondition (confirmed by
  `IP-1070`'s spanning-tree-plus-braid generator and `T19.b`) guarantees full connectivity — there
  is no generated world where any region, and therefore any carrot, is unreachable. This is a load-
  bearing fact for any "must reach region X" or "must collect N of the generated total" design:
  neither risks an unwinnable game, unlike a generator without a connectivity guarantee.
- **The maze (`ADR-0012`) already gives the world real internal structure to leverage.** A "goal
  region" candidate (e.g. the spanning tree's own deepest leaf, or a designated far-corner region)
  is not an arbitrary invention — `IP-1070`'s own generator already computes exactly this kind of
  structural property (BFS eccentricity from region 0, used in `BL-0075`'s own investigation to
  measure straight-line reachable distance) and could expose it as a real target.
- **`WORLD_SCALE` is chosen by the player at new-game time** (`FS-104`'s SEED/SCALE ENTRY screen),
  not fixed per save — so any scale-relative formula naturally re-derives itself per playthrough
  with no extra state, mirroring how Metroidvania completion percentages self-scale to each
  generated run's real item count.
- **Session-length precedent (R206) favors a genuinely short, knowable goal**, not a sprawling
  100%-of-81-regions requirement at the largest scale — a full-collection win condition that was
  appropriately sized at 9 fixed carrots would become a much longer commitment at `scale=9`
  (81 carrots across a maze with real dead ends, per `BL-0075`'s own measured corridor lengths).

## Implementation Guidance

Three grounded candidates, matching the ones named at `BL-0081`'s own intake, each evaluated
against the evidence above — presented as tradeoffs for the next design stage to choose from, not
resolved here (that decision belongs to `03`/`04`, not this research topic):

- **A. Scale-relative carrot count** (e.g. `CARROTS_COUNT >= WORLD_SCALE² ` for full 100%, or a
  fixed *fraction* of it) is the most direct fix and the lowest-risk change to the existing
  `CARROTS_COUNT` mechanism — no new state, no new UI concept, just replacing the hardcoded `9`
  with a `WORLD_SCALE`-derived value. A **100%** threshold is honest and simple but risks becoming
  a long grind at `scale=9` (R206's pacing concern) unless the maze's own reachability guarantee
  (§Operational Context) keeps traversal efficient. A **partial threshold** (e.g. Mario-64-style
  "collect most of them," R201's own already-cited precedent) mitigates the grind risk at large
  scale while still scaling honestly with world size — this is the candidate closest to what R201
  already recommended in advance of this exact situation.
- **B. Percentage-of-world-collected threshold** is functionally the same computation as
  candidate A expressed as a displayed percentage rather than a raw count — the Metroidvania
  convention (§Concepts) suggests this framing reads better to players than a raw number once the
  denominator varies run-to-run (a "73%" bar communicates progress at any scale; "41 of 81"
  requires the player to know 81 is the total for *this* run). If the eventual MAP/status-screen
  redesign (`BL-0050`) is going to show progress at all, a percentage-native win condition is a
  more natural fit for that display than a raw scale-relative count would be — a real interaction
  between this topic and `BL-0050` worth naming explicitly, not a coincidence.
- **C. Reach a generated "goal" region** is the fixed-goal-node convention (§Concepts) and the
  only candidate that changes win-condition *shape*, not just its threshold — trading "collect
  everything (or most of it)" for "successfully navigate to a specific place," which more directly
  exercises the maze/adjacency work (`ADR-0012`/`IP-1070`/`IP-1080`) than a pure collection count
  does, and stays a short, knowable goal at every scale (R206) since "reach one place" doesn't grow
  with `WORLD_SCALE` the way "collect N items" does. Costs more to build than A/B (needs a new
  concept — a designated goal region, plus a way to communicate *where* it is or that it's been
  reached, and a decision about whether the carrot-collection tier is retired, kept as a scoring
  layer, or made a prerequisite) and is a genuine scope/architecture question, not a threshold tweak.
- **Hybrid (A/B + C):** collection remains the scoring/completionist layer (percentage-displayed,
  per B) while reaching a designated goal region (per C) becomes the actual win trigger — keeps
  the existing scarce-tier collectible structure meaningful (R201's "fully enumerable, individually
  meaningful" property) while giving the maze's own structure a real payoff, at the cost of being
  the most design work of the three.
- **Do not adopt a raw "% of the grid visited/explored" condition** (distinct from "% of
  *collectibles* gathered") — the evidence in §Concepts is that mandatory full-map-exploration
  win conditions are out of step with contemporary design convention even in genres built around
  exploration, and Bunny Quest's short-session target (R206/A5) makes a *visitation* requirement
  (walking through every region, not collecting from it) a worse fit than a *collection* or
  *goal-reaching* requirement.
- **Whatever candidate is chosen, the fix must read `WORLD_SCALE` at check-time, not bake a
  scale-derived constant in at generation time** — mirroring `check_zone_transition`'s own
  post-`IP-9050` convention of reading live state rather than a stale computed value, and avoiding
  a save-format complication (the win-condition threshold should be *derivable*, not a new
  persisted field, consistent with `REGION_GRAPH`'s own "regenerate, don't persist" precedent,
  `ADR-0012` point 6).

## Feature Mapping

*(No `FS-xxx` authored yet — this grounds a future requirements/spec pass, per `BL-0081`'s own
routing to `04-requirements-engineering`/`03-architecture-design-synthesis` before any FS is
written.)*

## Related Topics

R201 (the tiered collect-a-thon structure this topic re-examines under scaling — its own
Implementation Guidance already anticipated this exact gap) · R206 (session-length/pacing bounds
on how large a win-condition threshold can grow) · R213 (the generator whose reachability
guarantee every candidate here depends on) · R214 (procgen-era case studies sharing this genre's
constraints).
