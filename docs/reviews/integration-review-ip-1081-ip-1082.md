# Integration Review — IP-1081/IP-1082 (Maze-Blocked Edge Indicator Set)

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

The maze-blocked edge indicator package set (`FS-108`/`FEAT-2100`/`BL-0075`), reviewed per
`BL-0103` — the last two packages in the tree never to have gone through `10-integration-review`.
A third package, `IP-1090` (SELECT Menu & Edge-Indicator Legend Screen), is not itself in scope
but is the first and only existing consumer of this set's shipped tile constants
(`TL_BLOCKED_U`/`TL_ARROW_U`) outside `draw_region_arrows` itself — its own interaction with this
set is exercised under Dimension 1/3 below, since that seam did not exist when either `IP-1081` or
`IP-1082`'s own verification ran.

| Package | Title | VR |
|---|---|---|
| IP-1081 | Maze-blocked edge indicator — content (`FS-108`/`BL-0075`) | [VR-1081](../implementation/verification/VR-1081-maze-blocked-edge-indicator-content.md) |
| IP-1082 | Maze-blocked edge indicator — render (`FS-108`/`BL-0075`) | [VR-1082](../implementation/verification/VR-1082-maze-blocked-edge-indicator-render.md) |

**Commit reviewed:** `b6e5f78` (tree head at review time — also carries `IP-1090`, `ADS-001`/
`ADR-0016`/`ADR-0017`, and pipeline journal/backlog updates, all confirmed disjoint from this
set's own files by the diffs below). Both `IP-1081`/`IP-1082` confirmed `VERIFIED` on the Master
Build Plan before this review began.

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x63C8 (25544 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
python3 test_rom.py                   → RESULTS: 246/246 passed   0 failed
```

(246, matching both packages' own last-recorded suite size — no regressions since `VR-1082`.)

## Dimension 1 — Interface consistency

**Clean.** Confirmed by direct diff/read against the shipped tree:

- `tiles.py:40-43` declares `TL_BLOCKED_U/D/L/R = 0x1A`–`0x1D`; `tiles.py:954-957` registers all
  four via `put()`, immediately continuing the existing `TL_ARROW_*` block. `0x1E`–`0x1F` remain
  free, matching the file's own comment.
- `asm_game.py:1076-1121` (`draw_region_arrows`): each of the four directions follows the identical
  shape — on a live neighbor (`REGION_GRAPH` byte ≠ `0xFF`), write the open-arrow tile and jump
  past the blocked-test block entirely (`dra_up_done`/`dra_down_done`/`dra_left_done`/
  `dra_right_done`); on `0xFF`, re-derive grid-adjacency from `(DRA_ROW, DRA_COL, WORLD_SCALE)` and
  write the blocked tile only if a grid neighbor genuinely exists. Confirmed the unconditional-`JR`
  fix `IP-1082`'s own package document describes (a same-package defect found and fixed before
  shipping, not a residual risk) is present at all four direction sites, not just the one the
  package's own text called out — no double-write path exists for any direction.
- **A real cross-package seam this set's own two VRs could not see, because it didn't exist yet:**
  `tilemaps.py:397-410` (`legend_screen`, `IP-1090`, `VERIFIED` after both `IP-1081`/`IP-1082`)
  places the literal `TL_ARROW_U` and `TL_BLOCKED_U` tile-index constants next to their
  plain-language labels — confirmed by direct read and by `test_rom.py`'s own `T21.f1`/`T21.f2`
  checks (`0x18`, `0x18` for open; `0x1A` for blocked), which assert the real constants, not
  placeholder values. This is exactly the class of seam an integration review exists to catch:
  `IP-1090`'s legend content is only correct because it consumes `IP-1081`'s tile-index constants
  by reference, and both continue to resolve correctly together at the current tree head. No
  divergence found.
- `GDS-07` §4 tile-index table (`docs/architecture/07-data-model.md:110`) correctly documents
  `0x1A`–`0x1D` as this set's own allocation, cross-referencing both packages.

## Dimension 2 — Invariant sweep

**Clean.**

- **ROM budget:** 32768 bytes exactly (25544 used, ~7.2KB headroom — the increase since `IP-1021`'s
  own 22984-byte figure is `IP-1090`'s two new static screens, confirmed disjoint from this set).
- **VBlank-gating:** `draw_region_arrows` (`asm_game.py:1040`–) is called from `dsr_p`
  (`asm_game.py:983`) entirely inside the same LCD-off bracket `copy_screen`'s VRAM writes already
  use, re-enabling LCD only at `dsr_done` (`:987`) after `draw_region_arrows` returns — the new
  blocked-branches are additional code inside an already-LCD-off routine, introducing no new
  timing surface beyond what `IP-1030` already established.
- **One-job-per-file:** no module boundary crossed — `IP-1081` touched only `tiles.py`, `IP-1082`
  only `asm_game.py`/`test_rom.py`, confirmed by each package's own VR scope audit and re-confirmed
  here against the current tree head.
- **Tile-index collision:** `0x1A`–`0x1D` confirmed still exclusively this set's own — no other
  package (including `IP-1090`, which adds zero new tile art per its own claim) has claimed
  `0x1E`–`0x1F` or re-used `0x1A`–`0x1D` for anything else.
- **WRAM:** `DRA_ROW`/`DRA_COL` (`asm_game.py:87-94`, `IP-1080`) are re-read, not re-allocated, by
  `IP-1082`'s blocked-branch logic — no new WRAM address introduced by this set at all (confirmed
  by grep; the render half is pure code, the content half is pure ROM tile data).

## Dimension 3 — Behavioral coherence

**Clean.** `T20.a`–`e` (`test_rom.py`) exercise the full generation corpus (120 blocked-edge
entries, 68 absent-edge entries, per the suite's own reported counts) confirming every
grid-adjacent-but-maze-pruned edge draws the correct blocked tile and every true grid-boundary
edge draws nothing — broader evidence than a single non-corpus live drive, since it covers the
entire corpus rather than one seed/scale pair (both packages' own VRs additionally live-drove a
non-corpus `(seed=42, scale=9)` case via PyBoy screenshot, re-confirmed unchanged by this review's
own diff audit above, not re-driven a third time here). `T21.f1`–`f3` independently confirm
`IP-1090`'s legend screen renders the real open/blocked/absent visual states correctly, exercising
the cross-package seam named in Dimension 1 end-to-end through the actual rendered tilemap, not
merely the shared constant. No behavioral divergence found between what `IP-1081` ships as tile
art, what `IP-1082` renders with it, and what `IP-1090` displays about it.

## Dimension 4 — Traceability coherence

**Clean.** `FR-2330`'s RTM row (`docs/requirements/04-requirements-traceability-matrix.md:40`)
correctly lists all three implementing packages (`IP-1080` logic half, `IP-1081` content,
`IP-1082` render) and test range `T20.a`–`e`. `FR-2320`'s own row correctly marks itself superseded
by `FR-2330`. `docs/implementation/packages/INDEX.md` and `verification/INDEX.md` both correctly
show `IP-1081`/`IP-1082` `VERIFIED` with accurate summaries (including each one's own honest
forward-reference to this still-owed review, now closed by this report). Master Build Plan and
`ROADMAP.md`'s `IP-xxxx`/`RV-INTEG` rows agree with the above. `FS-108`'s own metadata block
carries both packages' implemented-by pointers.

## Dimension 5 — Documentation coherence

**Clean.** `GDS-07` §4's tile-index table entry for `0x1A`–`0x1D` accurately describes the set as
shipped (cross-referencing both packages and the render branch's own trigger condition). No
`Claude.md`/`memory.md` staleness attributable to this set found (neither document makes any
per-tile claim this set's shipped content contradicts).

## Findings

*(none)*

No Critical/High/Medium/Low findings. Both packages' own previously-filed findings —
`BL-0097` (the `blocked_up`/`blocked_down` and `blocked_left`/`blocked_right` pixel-identical-pair
observation) and `BL-0103` (this review itself) — are content-craft and process-tracking matters
respectively, already correctly routed (`BL-0097` to `09-content-review`, still owed and unaffected
by this review's own clean result; `BL-0103` closed by this report).

## Next step

Clear to treat the `IP-1081`/`IP-1082` maze-blocked edge indicator set as fully integrated. A
`09-content-review` pass on the same set's shipped tile art (`BL-0097`) remains separately owed —
independent of this review, neither blocks the other. Both then advance alongside the rest of the
tree to `11-release-readiness` whenever the user is ready to make that release call (not this
review's own decision).
