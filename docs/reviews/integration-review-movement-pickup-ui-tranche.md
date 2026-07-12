# Integration Review — Movement/Pickup/UI Bug-Remediation Tranche

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

The movement/pickup/UI bug-remediation tranche's full package set, all `VERIFIED` on the Master
Build Plan:

| Package | Title | VR |
|---|---|---|
| IP-9080 | SAVE screen third-option labeling (BL-0049) | [VR-9080](../implementation/verification/VR-9080-save-screen-third-option-labeling.md) |
| IP-9090 | Movement clamp boundary fix (BL-0051 + BL-0052) | [VR-9090](../implementation/verification/VR-9090-movement-clamp-boundary-fix.md) |
| IP-9100 | Collectible pickup hitbox fix (BL-0053) | [VR-9100](../implementation/verification/VR-9100-collectible-pickup-hitbox-fix.md) |

**Commit reviewed:** `76e876c` (tree head at review time). All three packages confirmed
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

**Clean.** Each package's own document claims "no shared file region" with the other two —
confirmed by direct read: `IP-9090` (`handle_play_input`, `asm_game.py:514-573`) and `IP-9100`
(`check_collisions`, `asm_game.py:575`+) are adjacent but non-overlapping routines in the same
file; `IP-9080` touches only `tilemaps.py`'s `save_screen`. Exercised the real seam live, one
continuous session, all three packages in sequence: real, sustained RIGHT-held movement settled
exactly at `PLAYER_X=152` (`IP-9090`'s own corrected clamp); a synthetic item injected at
`dx=7, dy=0` relative to that real, clamp-derived position — the exact inclusive boundary
`IP-9100`'s asymmetric point-in-box test allows — collected correctly (`SCORE` incremented);
opening the SAVE screen immediately after showed the third-option label rendering (a real font
glyph at row 12 col 5, not the blank tile) — `IP-9080`'s own content. All three packages'
corrected behavior chained together with zero interference.

## Dimension 2 — Invariant sweep

**Clean.** None of the three packages introduces new WRAM/SRAM addresses or new tiles/palettes —
`IP-9090`/`IP-9100` are pure operand/formula corrections within existing routines, `IP-9080`
reuses the SAVE screen's own existing font tiles and palette 2 (confirmed zero new tile-index/
palette-table entries in `VR-9080`). ROM budget: exactly 32768 bytes, byte-identical rebuild.
VBlank-gating: unaffected by any of the three (no new VRAM writer introduced).

## Dimension 3 — Behavioral coherence

**Clean.** The live chained drive under Dimension 1 is itself the primary behavioral-coherence
evidence — a single, continuous player session exercises all three packages' own corrected
behavior back-to-back with no divergence or interference. No player-visible workflow spans a
package seam and dead-ends.

## Dimension 4 — Traceability coherence

**Clean.** Master Build Plan (including its own tranche-summary prose, confirming all three
`VERIFIED`), verification `INDEX.md`, RTM (`FR-1190` for `IP-9080`, `FR-2100` for `IP-9090`,
`FR-3100` for `IP-9100`), `packages/INDEX.md`, and `ROADMAP.md` all agree the tranche is closed.
`FR-3100`'s own text-vs-implementation divergence (the shipped asymmetric model vs. the still-
baselined `10px`-symmetric AC text) is consistently flagged as a forward pointer everywhere it's
mentioned, not silently absorbed in one place and ignored in another.

## Dimension 5 — Documentation coherence

**Clean.** No `Claude.md`/`memory.md`/`GDS-07`/`GDS-08` staleness found attributable to any of
the three packages — none of them touches byte-level WRAM/SRAM/tile documentation (`IP-9080` is
content-only reusing existing assets; `IP-9090`/`IP-9100` are pure constant/formula corrections
with no new data-model surface).

## Findings

No findings. All three packages' own corrected behavior was exercised together, live, in one
continuous session, with no divergence or interference found. No Critical/High/Medium/Low
findings.

## Next step

This tranche is clear to advance to `11-release-readiness` alongside Release 2 whenever the user
is ready to make that release decision (not this review's own call).
