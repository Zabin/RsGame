# Content Review — Nine-Biome-Family Delta (Village/Cave/Desert/Plains screens + procgen music)

> Produced by `09-content-review`. Read-only with respect to code and content — findings route to
> their owners; nothing was fixed in-pass.

[↑ Reviews index](INDEX.md) · [ROADMAP reviews row](../../ROADMAP.md)

## Scope

The rendered/audible content the `BL-0127`/`BL-0128` delta made reachable:

| Package | Status at review | Content surface reviewed |
|---|---|---|
| [IP-1022](../implementation/packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md) | `VERIFIED` (VR-1022) | The four newly-reachable screens' on-device rendering (procedural fill + landmark overlay, `ADR-0020`) |
| [IP-1033](../implementation/packages/IP-1033-nine-biome-family-collectible-spawn-content.md) | `VERIFIED` (VR-1033) | Collectible-spawn placement on those screens |
| [IP-1110](../implementation/packages/IP-1110-procedural-music-generation.md) | `VERIFIED` (VR-1110) | The nine biome-family sub-themes (data) |
| [IP-1111](../implementation/packages/IP-1111-biome-family-sub-theme-playback-selection.md) | `COMPLETE` (own `09-package-verification` pass still owed — this review does not substitute for it) | Runtime track selection behavior |

**ROM reviewed:** rebuilt from tree head `4c4051f` (post-`IP-1111`), 32768 bytes, 319/319 suite
green at build time.

**Screenshots captured** (all under [`screenshots/`](screenshots/)): `cr_village.png`,
`cr_cave.png`, `cr_desert.png`, `cr_plains.png` (finite mode, each with its own six spawned
collectibles), `cr_cave_infinite.png` (Infinite Mode render of the same art with its single
treasure spawn).

## Dimension 1 — Visual fidelity

Each of the four screens was force-rendered (the suite's own `T13.a` `REGION_GRAPH` direct-force
+ redraw method) and screenshotted. All four render their own family art correctly: Village's
cobble checkerboard with red-brick houses, lanterns, and fences; Cave's dark floor with top/bottom
wall rows, crystals, and drips; Desert's dune field with green cacti, bones, and a pyramid;
Plains' grass with flowers, tall grass, and butterflies. No washed-out or inverted bitplanes, no
garbage tile indices. Palette assignments match `FR-4320`'s five-group mapping exactly
(base-fill attrs read directly from the shipped `*_FILL` tuples: Village/Cave → 4 stone,
Desert → 1 sand, Plains → 0 grass; landmark attrs use the brick/tree/accent groups per entry).
The `T13.e` oracle-parity suite independently proves rows 1–17 byte-identical to the Python
originals, and this review's screenshots confirm the result *reads* as intended, not merely
matches. **One defect found in row 0 — Finding 1.**

## Dimension 2 — Readability & composition

All four screens read at a glance: collectibles (stars/flowers, OBJ palette gold/pink) are
clearly distinct from landmarks (BG art) and from the carrot/KeyItem (orange). Landmark density
leaves clear walking corridors; the four screens are mutually distinct at a glance and distinct
from all five original screens (different base tiles, different palettes, different landmark
silhouettes). The Cave screen's wall rows frame the space without reading as traversable. HUD
digits legible on all four (score-bar row is UI-palette gold on dark). **The HUD's zone-name
label, however, is wrong on all four screens — Finding 1.**

## Dimension 3 — Play fairness

Spawn tables re-read live from `COLL_DATA` after each forced redraw: six items per screen (five
star/flower + exactly one type-2 KeyItem), positions matching `ZONE_COLLECTS`' authored entries.
`VR-1033` Pass 2 already proved zero exact-tile landmark overlaps by independent re-derivation;
the screenshots visually confirm every item sits in open space, none on a transition edge or the
player spawn. Infinite Mode's cave render spawns its single treasure at the same authored
landmark-clear `(136,72)` position (`inf_treasure_pos[6]`, `T26.a0`-guarded). No fairness
concerns.

## Dimension 4 — Audio correctness

Data-level check (headless container — audible check impractical; the skill's data-level path):
`verify_music_generation.py` re-run at review time — **all checks pass**: each of the eight
non-Grass sub-themes is byte-provably a pure transposition/tempo-duration transform of the main
theme with the same 60-note count and terminal `0xFF` loop marker; Grass's track is
byte-identical to the original `music_data()` output. Runtime selection observed live during the
screen drives: `MUSIC_BASE` repointed to the correct per-biome `music_table` entry on every
forced screen change (Village `0x3109`, Cave `0x31BE`, Desert `0x3273`, Plains `0x3328` —
matching the build layout exactly), on both the finite and Infinite Mode paths. `T28.d`
separately proves a sub-theme loops from its own start (the `music_tick` fix). Clean.

## Dimension 5 — Documentation coherence

`GDS-07` reflects the shipped WRAM state (the `FPS_*` block and `MUSIC_BASE_*` entries added by
the delta's own packages); the FS-102/FS-103/FS-110/FS-111 acceptance-criteria trails all point
at real shipped checks (`T13.e`/`T13.f`/`T26.h`/`T26.i`/`T28.a–e`). Known, already-filed
staleness not re-filed here: `tilemaps.py`'s "5 UI screens" docstring (`BL-0136`), the `IP-110x`
doc-accuracy sweep family. One coherence gap is part of Finding 1: the Python `*_screen()`
functions' own zone-name behavior is real spec'd content the on-device path silently drops.

## Findings

| # | Finding | Artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| 1 | **Stale zone-name label on all four procedurally-filled screens** | `asm_game.py` (`fill_procedural_screen` / the four `dsr_p_*` procedural branches), `tilemaps.py` (`*_screen()` row-0 content), `test_rom.py` (`T13.e`'s row-0 exclusion) | Each Python `*_screen()` oracle writes its own zone name into the row-0 score bar ("VILLAGE", "CAVE", "DESERT", "PLAINS" at col 12, UI palette) — the same way every baked screen ships its name. The on-device procedural path deliberately starts at row 1 ("row 0 is the score bar, handled separately") and **never writes the name**, so the previous screen's name persists: all five screenshots show "FOREST" (the prior screen's label) while rendering Village/Cave/Desert/Plains, in both finite and Infinite Mode. Misleading HUD text on every visit to the four new screens; art/spawns/music otherwise correct. `T13.e`'s oracle-parity check masked this by excluding row 0 wholesale — the exclusion is justified for the live score/carrot digits but overbroad for the static name region (cols 12+). | **Medium** | `07-implementation-planning` → a small remediation package for `08-code-implementation` (draw the name tiles in the procedural branches — e.g. a per-screen name entry alongside the `*_FILL`/`*_LANDMARKS` data, or fold the name cells into the landmark overlay list); the same package should narrow `T13.e`'s row-0 exclusion to just the live digit cells so parity covers the name region |

No Critical/High findings. One Medium (above); no Low findings beyond already-filed entries.

## What was exercised to earn this review

Force-rendered all four screens finite-mode + one Infinite Mode render, with live `COLL_DATA`/
`MUSIC_BASE` reads per screen; five screenshots; `verify_music_generation.py` re-run;
palette-group audit against the shipped `*_FILL` attrs; spawn-position cross-check against
`ZONE_COLLECTS`/`inf_treasure_pos`; documentation trail spot-checks (GDS-07, FS-102/103/110/111,
RTM rows).
