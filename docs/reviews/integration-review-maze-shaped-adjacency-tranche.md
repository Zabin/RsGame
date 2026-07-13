# Integration Review — Maze-Shaped Region Adjacency Tranche

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

The maze-shaped region adjacency tranche's full package set, all `VERIFIED` on the Master Build
Plan:

| Package | Title | VR |
|---|---|---|
| IP-1070 | Maze-shaped region adjacency (FS-107 / FEAT-9100) | [VR-1070](../implementation/verification/VR-1070-maze-shaped-region-adjacency.md) |
| IP-1080 | Maze-aware transition-edge classification, logic half (FS-108 / FEAT-2100) | [VR-1080](../implementation/verification/VR-1080-maze-aware-edge-classification.md) |

**Commit reviewed:** `6726f18` (tree head at review time). Both packages confirmed `VERIFIED` on
the Master Build Plan before this review began.

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x57C8 (22472 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
sha256sum BunnyQuest.gbc              → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd
                                          (identical to the checked-in ROM)
python3 test_rom.py                   → RESULTS: 231/231 passed   0 failed
```

## Dimension 1 — Interface consistency

**Clean.** This tranche's own real seam: `IP-1080`'s classification logic must correctly
distinguish "maze-pruned but grid-adjacent" (blocked) from "true grid boundary" (absent) against
`REGION_GRAPH`'s data as `IP-1070`'s maze pass actually shapes it — `REGION_GRAPH`'s own 5-byte
format is unchanged by `IP-1070` (confirmed in `VR-1070`), which is exactly what makes `IP-1080`
implementable without touching `IP-1070`'s own code. Exercised live, at a non-default scale
(`seed=1`, `scale=9`, not the suite's own default `scale=3`): forced a redraw at region 0 and
inspected `DRA_ROW`/`DRA_COL` directly — both read `0`, correctly re-derived for region 0's
`(row=0, col=0)` position under `WORLD_SCALE=9`. Cross-checked `REGION_GRAPH[0]`'s own right
neighbor byte: `0xFF` — a **maze-pruned, grid-adjacent** edge (region 0's grid-right neighbor,
region 1, exists per the offline oracle check, but `IP-1070`'s braid pass didn't reopen this
particular edge for `seed=1`) — exactly the "blocked" case `IP-1080` exists to classify
correctly, confirmed live against a real generated world, not a synthetic fixture.

## Dimension 2 — Invariant sweep

**Clean.** Checked across the whole set, not sampled:

- **ROM budget:** exactly 32768 bytes, valid header, byte-identical rebuild.
- **WRAM allocation:** `IP-1070`'s `GW_MAZE_STATE` family (`0xC3A0`–`0xC3F4`) and `IP-1080`'s
  `DRA_ROW`/`DRA_COL` (`0xC2D8`–`0xC2D9`) occupy disjoint ranges, confirmed by direct constant
  dump — no overlap, no shared scratch reuse between the two packages' own transient state.
- **VBlank-gating:** unaffected by either package — `IP-1070`'s maze pass runs entirely within
  `generate_world` (already LCD-off, confirmed `VR-1070`); `IP-1080`'s `DRA_ROW`/`DRA_COL`
  computation runs inside `draw_region_arrows`, itself only reached through the existing
  `do_screen_redraw` gate.
- **Tile index map:** unaffected — neither package touches `tiles.py`.
- **`gw_prng_step` interaction:** `IP-1070`'s maze pass is the primary consumer of
  `gw_prng_step`'s repeated-draw behavior (via `ADR-0013`'s `GW_MAZE_DRAW_CTR` perturbation,
  confirmed still in place and still passing `T19.e`'s braid-fraction statistical check in this
  run's own full-suite pass) — this is a real interaction surface with `IP-9110` (the PRNG
  mixing-step repair), but `IP-9110` is outside this tranche's own scope; already independently
  verified compatible in `VR-9110`'s own findings (T19.e re-confirmed passing under the repaired
  PRNG) and will be re-confirmed as its own review dimension when the `IP-9110`/`9120`/`9130`/
  `9140` package set is reviewed.

## Dimension 3 — Behavioral coherence

**Clean.** The same live drive under Dimension 1 doubles as behavioral-coherence evidence: a
genuine `IP-1070`-generated maze world, inspected through `IP-1080`'s own classification
machinery, produces a result consistent with the oracle's own independent computation — no
divergence between what `IP-1070` generated and what `IP-1080` classified. `T20.a`/`b`/`c`
(already independently confirmed in `VR-1080`) exercise this same seam exhaustively across
`IP-1070`'s own `T19` corpus (`scale ∈ {2,3,9}`), not just the one live case this review drove by
hand.

## Dimension 4 — Traceability coherence

**Clean.** Master Build Plan, verification `INDEX.md`, RTM (`FR-9140`/`FR-9150` for `IP-1070`,
`FR-2330` for `IP-1080`, both honestly noting `IP-1080`'s own partial coverage), `packages/
INDEX.md`, and `ROADMAP.md` all agree both packages are `VERIFIED` and the tranche's full critical
path (`IP-1070`→`IP-1080`) is closed. `FS-107`/`FS-108` metadata cross-references both packages
correctly; `FS-108`'s own scope note (logic half only, rendering half unpackaged) is consistent
with `IP-1080`'s own Definition of Done and `VR-1080`'s own audit.

## Dimension 5 — Documentation coherence

**Clean.** GDS-07 §7b (`GW_MAZE_STATE` family) and the `DRA_ROW`/`DRA_COL` table row (§2, line 74)
are both accurate and current — confirmed by direct comparison against the shipped constants.
GDS-08's blocked-edge-indicator delta (§10, `BL-0068`) correctly describes the rendering half as
still unimplemented, consistent with `IP-1080`'s own honestly-left-open AC-4. `Claude.md`/
`memory.md` checked separately: no tranche-specific staleness found.

## Findings

No findings. Both dimensions this tranche's own packages actually touch (WRAM allocation,
classification-vs-generation correctness) were exercised live against a non-default, real
generated world and found consistent. No Critical/High/Medium/Low findings.

## Next step

This tranche is clear to advance to `11-release-readiness` alongside Release 2 whenever the user
is ready to make that release decision (not this review's own call). Note for that future
release-readiness pass, not a blocking finding here: `FS-108`'s rendering half (the blocked-edge
indicator's actual on-screen appearance) remains unimplemented — `IP-1080`'s own AC-4 is honestly
left open throughout its own documentation chain, not silently dropped, so this is a known, already
-tracked scope gap (`BL-0068`'s own downstream work), not a surprise this review discovered.
