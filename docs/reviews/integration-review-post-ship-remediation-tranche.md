# Integration Review — Post-Ship Remediation Tranche

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

The post-ship remediation tranche's full package set, all `VERIFIED` on the Master Build Plan:

| Package | Title | VR |
|---|---|---|
| IP-9050 | Generated-world navigation fix (BL-0047) | [VR-9050](../implementation/verification/VR-9050-generated-world-navigation-fix.md) |
| IP-9060 | Main menu cursor fix (BL-0048) | [VR-9060](../implementation/verification/VR-9060-main-menu-cursor-fix.md) |
| IP-9070 | `CUR_ZONE`-indexed structure generalization (BL-0058 + BL-0059) | [VR-9070](../implementation/verification/VR-9070-cur-zone-indexed-structures-generalization.md) |

**Commit reviewed:** `d22aeac` (tree head at review time). All three packages confirmed
`VERIFIED` on the Master Build Plan before this review began.

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x57C8 (22472 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
sha256sum BunnyQuest.gbc              → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd
                                          (identical to the checked-in ROM)
python3 test_rom.py                   → RESULTS: 231/231 passed   0 failed
```

## Dimension 1 — Interface consistency

**Clean.** This tranche's own core seam is a **hard sequencing dependency**, not a data-shape
contract: `IP-9050`'s own package document names `IP-9070` as "hard prerequisite, not a
convenience ordering" — `IP-9050` makes `CUR_ZONE > 8` reachable at runtime; `IP-9070` is what
makes every `CUR_ZONE`-indexed structure (`SCOREITEM_FLAGS`, `ZONE_COLLECTS`/`zc_table`) safe for
that range. Exercised the real seam live: real, sustained button-driven navigation (`IP-9050`,
`seed=1`/`scale=9`) from region 0 into region 9 — the first index the pre-`IP-9070` 9-byte
`SCOREITEM_FLAGS` array could not have safely held — completed cleanly with no crash, no WRAM
corruption observed (`REGION_GRAPH`'s own bytes, which sit immediately after `SCOREITEM_FLAGS`'s
original unsafe location, were not disturbed). `IP-9060` is functionally independent of the other
two (a MAIN MENU-only cursor fix, confirmed by its own package's Dependencies field: "Independent
of `IP-9050`/`IP-9070`").

## Dimension 2 — Invariant sweep

**Clean.** Checked across the whole set, not sampled:

- **ROM budget:** exactly 32768 bytes, valid header, byte-identical rebuild.
- **WRAM allocation, the tranche's own real seam:** `SSE_CURSOR` (`0xC285`, pre-existing) →
  `SCOREITEM_FLAGS` (`0xC286`–`0xC2D6`, 81 bytes, `IP-9070`) → `MM_JUST_ENTERED` (`0xC2D7`, 1
  byte, `IP-9060`) → `DRA_ROW`/`DRA_COL` (`0xC2D8`–`0xC2D9`, `IP-1080`, reviewed separately) →
  `OAM_BUF` (`0xC300`) — confirmed by direct constant dump this is a single, contiguous,
  zero-gap, zero-overlap chain: two *different* packages (`IP-9070` and `IP-9060`) each claimed
  the next free byte in the same shared gap without collision, evidence the addresses were
  chosen with the other's placement in mind, not independently.
- **VBlank-gating:** neither `IP-9050` (pure control-flow change, no VRAM writes) nor `IP-9070`
  (WRAM/SRAM only) nor `IP-9060` (its own `mm_on_entry`/`draw_menu_cursor` writes are reached only
  through the existing `do_screen_redraw` LCD-off gate, unchanged in shape) introduces a new VRAM
  writer.
- **Tile index map:** unaffected — none of the three packages touches `tiles.py`.

## Dimension 3 — Behavioral coherence

**Clean.** Directly drove the tranche's own core interaction live in PyBoy: new game at
`seed=1`/`scale=9` (a non-default, real generated world) → real, sustained `button_press('down')`
navigation (`IP-9050`'s `REGION_GRAPH`-driven `check_zone_transition`) from region 0 into region
9 — `CUR_ZONE` confirmed settling at exactly `9`, a value the pre-`IP-9070` `SCOREITEM_FLAGS`
array could not have safely indexed. No crash, no WRAM corruption. This directly exercises the
two packages' own hard dependency together, live, beyond what either package's individual
Verification Report tested in isolation (`VR-9050`'s own `T17.a` corpus tops out at `scale=5`/25
regions; `VR-9070`'s own `T16.a` forces `CUR_ZONE=40` directly via WRAM rather than real
navigation). `IP-9060`'s own MAIN MENU cursor behavior was independently confirmed unaffected by
either of the other two packages — no shared file region, confirmed in `VR-9060`.

## Dimension 4 — Traceability coherence

**Clean**, with an observation routed to the pipeline manager's own bookkeeping (not a defect in
any package or its documentation). Master Build Plan, verification `INDEX.md`, RTM (`FR-2300`,
`FR-1170`, `FR-5220` rows), `packages/INDEX.md`, and `ROADMAP.md` all agree the three packages are
`VERIFIED` and the tranche is closed. **Observation, not a finding:** the pipeline backlog
(`docs/pipeline/backlog.md`) entries `BL-0047`/`BL-0048`/`BL-0058`/`BL-0059`/`BL-0063` — the
original bug reports this tranche fixes — each still carry a note reading "Status stays
`SCHEDULED`, not `DONE`, pending independent `09-package-verification`," written when that
verification was still outstanding. All three packages have since reached `VERIFIED`
(`VR-9050`/`VR-9060`/`VR-9070`, this session). This is the pipeline manager's own harvest
bookkeeping, not an artifact this review's own scope covers (RTM/feature-catalog/Master-Build-Plan/
package-index/`ROADMAP.md` — the backlog isn't one of them) — flagged here for the manager to
close out directly rather than filed as a numbered finding requiring its own remediation package.

## Dimension 5 — Documentation coherence

**Clean**, cross-referencing rather than duplicating `BL-0089` (filed by the Release 2 tranche's
own integration review, this session). GDS-07 §7a (`SCOREITEM_FLAGS`/`SRAM_SCOREITEM` relocation)
is accurate and complete for `IP-9070`'s own contribution. `IP-9060`'s `MM_JUST_ENTERED` table row
(GDS-07, `C2D7`) is accurate. The one stale GDS-07 clause touching this tranche's own work — §6's
`KEYITEM_FLAGS` row (line 166) misattributing the 9→81-byte clear-loop widening to `FEAT-1100`'s
own still-pending scope, when `IP-9050`/`BL-0063` actually did it (confirmed by direct code read,
`asm_game.py:309-314`/`:377-379`, both explicitly commented "widened... by IP-9050/BL-0063") — is
**already captured by `BL-0089`**, filed against the Release 2 review; not re-filed here.
`Claude.md`/`memory.md` checked separately: no tranche-specific staleness found (neither document
attempts WRAM-byte-level detail, which is GDS-07's own job).

## Findings

No new findings requiring a numbered `BL-xxxx` entry. `BL-0089` (already filed, `SCHEDULED`)
covers the one documentation clause this tranche's own work touches. The backlog-status
observation under Dimension 4 is routed to the pipeline manager directly (a same-session sync,
not a remediation package).

No Critical/High findings.

## Next step

This tranche is clear to advance to `11-release-readiness` alongside Release 2 whenever the user
is ready to make that release decision (not this review's own call).
