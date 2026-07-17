# Content Review — IP-1081/IP-1082 (Maze-Blocked Edge Indicator, FS-108)

> Produced by `09-content-review`. Read-only judgment of rendered content against design intent —
> changes nothing but this report. Peer of `09-package-verification`
> ([VR-1081](../implementation/verification/VR-1081-maze-blocked-edge-indicator-content.md),
> [VR-1082](../implementation/verification/VR-1082-maze-blocked-edge-indicator-render.md) —
> mechanical DoD/checklist audits); this report judges whether the result reads well, not whether
> the checklist was followed.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md) ·
[IP-1081](../implementation/packages/IP-1081-maze-blocked-edge-indicator-content.md) ·
[IP-1082](../implementation/packages/IP-1082-maze-blocked-edge-indicator-render.md) ·
[FS-108](../features/FS-108-maze-aware-transition-edge-signaling.md)

## Scope

- **Packages:** IP-1081 (tile art, commit `5569ba7`) and IP-1082 (render branch, commit
  `6091bd1`), both FS-108/FEAT-2100/BL-0075.
- **Status at review time:** both `VERIFIED` (VR-1081, VR-1082) and both already
  `10-integration-review`-clean
  ([integration-review-ip-1081-ip-1082.md](integration-review-ip-1081-ip-1082.md), BL-0103, DONE).
  This review is the one remaining owed step for the set (BL-0097's own disposition).
- **What the set delivered:** 4 new tiles (`TL_BLOCKED_U/D/L/R`, `0x1A`-`0x1D`, palette 2 reused
  verbatim) plus a render-time branch in `draw_region_arrows` that classifies each of the four
  screen edges into open / blocked / absent and draws the matching glyph or nothing.
- **Finding under direct examination:** `BL-0097` — `IP-1081`'s own `blocked_up()`/`blocked_down()`
  tile functions are pixel-identical to each other, as are `blocked_left()`/`blocked_right()`,
  despite the package's own §6 design intent calling for "a directional glyph, not a
  direction-agnostic icon" (mirroring the arrow tiles, which are genuinely distinct per direction).

## Method

Rebuilt the ROM from the current tree head (`b9b51bb`, `29896/32768` bytes) and drove it live in
PyBoy (`window='null'`), via three passes:

1. **All-four-blocked pass**: forced `REGION_GRAPH` region 4 (grid center at scale=3, so all four
   grid-neighbors 1/3/5/7 genuinely exist) to have all four neighbor bytes `0xFF` (no maze edge in
   any direction) and force-redrew — this is the direct maze-blocked case (grid-adjacent but not
   maze-connected), the exact condition `TL_BLOCKED_*` exists to signal, and puts all four glyphs
   on screen simultaneously for direct side-by-side comparison.
2. **Open-arrow contrast pass**: forced region 0 (a true grid corner) with its two real neighbors
   open (down, right) and its two grid-edges genuinely absent (up, left) — captures the shipped
   `TL_ARROW_D`/`TL_ARROW_R` glyphs for a same-method visual comparison against the blocked tiles.
3. **LEGEND screen pass**: SELECT → toggle to LEGEND → A (mirrors `T21.c`'s own button sequence) —
   captures the actual LEGEND screen a player would read to learn what each glyph means.

Each affected on-screen tile was additionally isolated via a tight, upscaled crop (nearest-neighbor
10x) so the four blocked glyphs and two arrow glyphs could be compared pixel-for-pixel, not just
eyeballed at native 160x144 resolution.

Screenshots captured (`test_shots/content-review-ip-1081-ip-1082/`, gitignored per this repo's own
`test_shots/` precedent — same convention as `content-review-IP-1031.md`):
`all-four-blocked.png`, `open-arrows-contrast.png`, `legend-screen.png`, and four tight crops
(`tile_U_blocked-up.png`, `tile_D_blocked-down.png`, `tile_L_blocked-left.png`,
`tile_R_blocked-right.png`).

## Findings by dimension

### 1. Visual fidelity — clean, with one confirmed finding (BL-0097)

All four `TL_BLOCKED_*` tiles render correctly at their intended screen positions (confirmed both
by direct WRAM tilemap read — `0x9800` offsets matching `ARROW_POS`'s own up/down/left/right
addresses — and by the screenshots above): no undefined/garbage tile indices, no washed-out or
inverted bitplanes, palette 2 applied correctly (navy/white/yellow, matching the arrow tiles'
existing palette per GDS-08 §10's "reused verbatim" instruction).

**`BL-0097` confirmed by direct visual inspection, not just source-level pixel-array comparison:**
the up-blocked and down-blocked glyphs (`tile_U_blocked-up.png`, `tile_D_blocked-down.png`) are a
navy vertical bar with a yellow accent at each end — genuinely pixel-identical between the two, not
merely similar. The left-blocked and right-blocked glyphs (`tile_L_blocked-left.png`,
`tile_R_blocked-right.png`) are a navy square with four corner dots — also genuinely
pixel-identical to each other. `all-four-blocked.png` shows all four rendered together in situ:
the up/down pair and the left/right pair are each internally indistinguishable by shape, differing
only by screen position (top-center vs. bottom-center; left-edge vs. right-edge). This confirms
the package's own §13-flagged risk materialized largely as VR-1081/BL-0097 already reported it —
this pass adds the rendered, in-context confirmation that was still outstanding.

### 2. Readability & composition — Medium finding (craft-intent gap, not a functional defect)

By direct comparison against `open-arrows-contrast.png`: the arrow tiles are genuinely distinct
directional silhouettes — `TL_ARROW_D` is a downward chevron, `TL_ARROW_R` is a rightward chevron,
each independently readable as "this points down" / "this points right" even out of context. The
blocked tiles do **not** carry the same independent directionality: the up/down bar shape and the
left/right square shape each read as "an axis is blocked here," with the specific direction along
that axis conveyed entirely by **screen position** (top of screen vs. bottom of screen), not by the
glyph's own silhouette.

**In practice this is not a play-fairness or comprehension failure**: because `ARROW_ADDR_U` is
fixed at the top-center of the screen and `ARROW_ADDR_D` at the bottom-center (same for
left/right), a player reading `all-four-blocked.png` at a glance still correctly identifies which
edge each glyph belongs to — position alone disambiguates, exactly the way it already does for the
open arrows. No screenshot in this review shows an ambiguous or misreadable state. But the
package's own stated design goal (§6: glyphs "oriented per direction the same way the arrow tiles
are... a directional glyph, not a direction-agnostic icon") is not met — the shipped art collapses
to 2 distinct bitmaps reused across 4 tile slots, not 4 distinct directional glyphs. This is a
craft-intent gap: the feature works and reads correctly by position, but does not deliver the
specific visual language the package committed to.

### 3. Play fairness — not applicable, no change

Neither package touches `ZONE_COLLECTS` or any spawn table; the blocked-edge indicator is a
render-only signal layered on top of already-existing, already-fairness-audited region content.
Nothing in either screenshot pass shows a blocked-edge glyph overlapping a collectible, the player
spawn point, or an open-arrow tile.

### 4. Audio correctness — not applicable, no change

Neither package touches `music.py` or any audio data (confirmed: not in either package's declared
file set, not in either implementing commit's diff).

### 5. Documentation coherence — clean

`memory.md`'s tile-index quick-ref and GDS-08 §10 both already record `TL_BLOCKED_U/D/L/R` at
`0x1A`-`0x1D`, palette 2, matching what actually shipped. The LEGEND screen
(`legend-screen.png`, IP-1090) shows one blocked-glyph exemplar (`TL_BLOCKED_U`) beside "MAZE
BLOCKED," consistent with `T21.f2`'s own assertion and with the actual tile shipped. **Worth
noting explicitly:** because the LEGEND screen only ever displays one blocked-direction exemplar
(never two side by side), a player reading the LEGEND alone would have no way to notice the
pixel-identical-pair issue — it is only observable in live gameplay when two axis-sharing blocked
edges appear on the same region screen simultaneously (the scenario this review's
`all-four-blocked.png` pass deliberately constructed). The LEGEND screen itself is accurate and not
misleading; it simply doesn't happen to expose this gap either way.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | `blocked_up()`/`blocked_down()` (`tiles.py:829-837`) and `blocked_left()`/`blocked_right()` (`tiles.py:839-845`) ship as two distinct bitmaps reused across four direction slots, not four independently-directional glyphs as IP-1081 §6 specified. Confirmed by direct visual inspection this pass (`all-four-blocked.png`): each axis-pair is genuinely indistinguishable by shape, distinguished only by screen position. Does not cause any misreadable or ambiguous on-screen state (position fully disambiguates in every real region layout, since each of the four `ARROW_ADDR_*` slots is fixed to its own screen edge) — a craft-intent gap, not a play-fairness or comprehension defect. This is `BL-0097`, confirmed rather than newly discovered. | Medium | `08-content-authoring` (a small follow-up package re-authoring `blocked_up`/`blocked_left` — or all four — as genuinely distinct directional bitmaps, e.g. an asymmetric broken-bar/notch motif per direction, matching the arrow tiles' own precedent of true directional silhouettes) |
| 2 | The LEGEND screen (IP-1090) only ever shows one blocked-direction exemplar at a time, so it cannot itself reveal Finding 1 to a player reading it — noted for completeness, not a defect in IP-1090 (out of this review's package scope; IP-1090 was independently content-reviewed/verified already). | Informational | none — no action recommended |

No Critical/High findings. Finding 1 confirms `BL-0097` exactly as already filed (Medium,
non-blocking, deferred to a future `08-content-authoring` pass); this review adds live rendered
evidence to that existing finding rather than opening a new one.

## Next step

This review is not clean (one Medium finding, confirming `BL-0097`) but is not blocking — both
packages remain `VERIFIED` and integration-reviewed clean; the finding routes to a future,
separately-scheduled `08-content-authoring` remediation package, not a re-open of either package's
own DoD. With this review filed, `FS-108`'s full package set (`IP-1080`/`IP-1081`/`IP-1082`) has
now cleared every owed `09`-tier pass (`09-package-verification` x2 + this `09-content-review`) and
`10-integration-review` (BL-0103) — the set is fully closed out pending only the Finding 1
remediation, which is optional/deferred craft polish, not a blocker to anything downstream.
