# Content Review — IP-1125 Combat Sub-Mode Sprite Content

## Scope

`IP-1125` (commit `74d53c4`, tile art + `build_rom.py` `OBJ_PALETTES` slots 4/5) — the mob
(`TL_MOB`/`TL_MOB_BOT`) and projectile (`TL_PROJECTILE`/`TL_PROJECTILE_BOT`) OBJ sprites — reviewed
against the current tree head (`b464f10`, which also includes `IP-1121`'s own real mob-placement
logic, letting this review exercise the mob sprite via genuine materialized positions rather than
forced OAM entries alone). Mechanically `VERIFIED` (`VR-1125`); this review judges the rendered
result against `R218`'s own design intent and general readability/play-fairness, not the
mechanism.

## Screenshots captured

- `docs/reviews/screenshots/ip1125-content-review-mob-and-projectile.png` — mob and projectile
  both forced onto the same frame (Forest zone), for direct side-by-side silhouette/color
  comparison.
- `docs/reviews/screenshots/ip1125-content-review-three-mobs-forced.png` — three mobs rendered
  simultaneously (Lake zone), for at-a-glance multi-entity readability.

## Findings by dimension

### 1. Visual fidelity

Rebuilt the ROM from the current tree head; both sprites render exactly as `tiles.py`'s own
`mob_obj()`/`projectile_obj()` generator functions specify (already confirmed byte-for-byte by
`T34.b`, re-confirmed here visually). No washed-out or inverted art — both bitplanes render
cleanly at both screenshot resolutions. Palette assignments match `build_rom.py`'s own
`OBJ_PALETTES` slots 4 (mob: purple family) and 5 (projectile: gold/orange family), as recorded
in `memory.md`'s Tile Index Map quick-ref (`0x0A`-`0x0D` row, confirmed present).

### 2. Readability & composition

Both sprites read clearly at a glance against every biome background exercised (Forest, Lake):
the mob's spiked-blob silhouette (purple, dark outline) and the projectile's radiating-orb
silhouette (gold/orange core) are unambiguous small-creature-vs-projectile shapes, consistent
with `R218`'s own "poof"-convention, non-graphic framing — no blood/gore, no readable violence,
matches the base game's existing content discipline. Three simultaneously-rendered mobs (Lake
screenshot) remain individually distinguishable from each other and from the water background.

**Observation, not a finding:** the projectile's `OBJ_PALETTES` entry (slot 5: `BLACK`/
`OB_LITE_YEL`/`OB_GOLD`/`OB_ORANGE`) shares its two brightest colors exactly with the existing
star collectible's own palette (slot 1: `BLACK`/`OB_LITE_YEL`/`OB_GOLD`/`OB_PURPLE`) — confirmed
by direct comparison of `build_rom.py`'s `OBJ_PALETTES` table. Checked whether this could cause
real player-facing confusion: it cannot — the star item exists only in finite mode (`GAME_MODE
== 0`) and the projectile exists only when `COMBAT_MODE` is active (valid only alongside
`GAME_MODE == 1`, per `ADS-002`'s own gating), so the two sprites are never reachable in the same
game state. Noted for completeness, not filed as a finding.

### 3. Play fairness

`IP-1121`'s own procedural mob placement (`inf_materialize_mobs`, not this package's own scope,
but the only mechanism that currently exercises this sprite content with real positions) draws
each of up to 6 mobs' `(x, y)` independently, with no minimum-separation check between slots in
the same region. Sampled `worldgen.materialize_mobs` across 9,800 `(seed, row, col)` combinations
(200 seeds × a 7×7 region window each): 547 regions drew 2+ active mobs, and **17 of those (≈3%)
placed two mobs at the exact same `(x, y)` cell** — two identical purple sprites would render
fully stacked, visually indistinguishable as one entity (though both remain independently
present/defeatable in `MOB_DATA`). Low-frequency but real, and a legitimate play-fairness/
readability gap for a future pass to close (a minimum-separation retry or offset on collision).

### 4. Audio correctness

Not applicable — this package contributes no music/audio data.

### 5. Documentation coherence

`memory.md`'s Tile Index Map row for `0x0A`-`0x0D` is present and accurate (confirmed by direct
read, cites `IP-1125`, correct palette numbers). `IP-1125`'s own package document and the Master
Build Plan/`packages/INDEX.md` rows accurately describe the shipped art. No stale references
found.

## Findings

| Finding | Artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| Mob placement has no minimum-separation guarantee | `inf_materialize_mobs` (`IP-1121`), `TL_MOB` (`IP-1125`) | ~3% of multi-mob regions place two mobs at the exact same `(x, y)` cell (measured across a 9,800-region sample), rendering as one visually-indistinguishable stacked sprite despite both being independently present in `MOB_DATA`. | Low | `07-implementation-planning` (a future remediation package for `IP-1121`'s own placement logic — a retry-on-collision or fixed-offset nudge, not a new content-authoring concern) |

One informational observation (not a finding, no owner needed): the projectile's palette shares
its two brightest colors with the existing star collectible's palette, but the two sprites are
never co-reachable in any real game state (finite-mode-only vs. combat-mode-only), so no
player-facing readability risk results.

## Result

**Clean**, with one Low-severity finding (routed above) and one non-blocking observation. Both
sprites satisfy `R218`'s own design intent (non-graphic, readable, distinct silhouettes) and
`ADS-002`'s own sprite-budget/palette-reuse commitments.
