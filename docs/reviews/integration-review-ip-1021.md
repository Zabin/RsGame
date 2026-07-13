# Integration Review — IP-1021 (Win-Condition Redesign)

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

A single newly-`VERIFIED` package, reviewed because it post-dates the last integration sweep
([integration-review-ip-9110-9120-9130-9140.md](integration-review-ip-9110-9120-9130-9140.md),
which closed "every `VERIFIED` package in the tree now belongs to a reviewed tranche or set") and
touches a real interaction surface with several already-reviewed packages: `generate_world`
(shared with `IP-1020`/`IP-1070`/`IP-9070`/`IP-9110`), `KEYITEM_FLAGS` (read by
`setup_zone_collects`/`check_collisions`, both `IP-1020`), and the save/load round-trip (`IP-1050`).

| Package | Title | VR |
|---|---|---|
| IP-1021 | Win-condition redesign — dead-end-anchored treasure placement (`FS-102`/`BL-0093`) | [VR-1021](../implementation/verification/VR-1021-win-condition-redesign.md) |

**Commit reviewed:** `6091bd1` (tree head at review time). `IP-1021` confirmed `VERIFIED` on the
Master Build Plan before this review began. Tree head also carries `IP-1082` (`COMPLETE`, not yet
`VERIFIED`) — disjoint files (`draw_region_arrows`/`tiles.py` vs. `IP-1021`'s
`generate_world`/`check_complete`) from `IP-1021`'s own scope, confirmed by direct diff, and
explicitly out of this review's scope (not yet `VERIFIED`).

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x59C8 (22984 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
python3 test_rom.py                   → RESULTS: 234/234 passed   0 failed
```

(234, not `IP-1021`'s own reported 233, because `IP-1082`'s two `T20` corrections/additions have
since landed on top — none of `IP-1021`'s own `T12`/`T4.8` checks changed count or result.)

## Dimension 1 — Interface consistency

**Clean, one Medium finding.** Confirmed `KEYITEM_FLAGS`'s widened tri-state domain (`0`=present/
uncollected, `1`=present/collected, `2`=absent, `IP-1021`'s own §6 encoding decision) is honored
correctly by every other package that reads or writes it:

- `setup_zone_collects` (`asm_game.py:1245-1257`, `IP-1020`): `OR_A(); JR_Z('szc_sk')` treats any
  nonzero value (`1` *or* `2`) as "don't spawn" — correct for both "already collected" and the new
  "never assigned a KeyItem" case, confirmed by direct read.
- `check_collisions`'s pickup handler (`asm_game.py:620-634`, `IP-1020`): only reachable when a
  live, spawned KeyItem sprite is actually hit — since `setup_zone_collects` already suppresses
  spawning for absent (`2`) regions, this handler can never fire against one; the tri-state's third
  value is correctly unreachable here by construction, not by an explicit check.
- `save_to_sram`/`try_load_save` (`asm_game.py:1854-1961`, `IP-1050`): confirmed value-agnostic
  81-byte `memcpy`s, unaffected by the widened domain. **Load-order interaction confirmed correct**
  by direct trace: `try_load_save` calls `generate_world` (line 1943, which now also runs `IP-1021`'s
  placement pass, writing a freshly-computed present/absent pattern into `KEYITEM_FLAGS`) *before*
  the `SRAM_KEYITEM_FLAGS`→`KEYITEM_FLAGS` restore memcpy (line 1944-1945) — so the actually-saved
  per-region collected/absent state correctly overwrites the freshly-regenerated placement, not the
  other way around. A player's collected KeyItems are **not** silently reset to "present" on reload.
  This ordering pre-dates `IP-1021` (established by `IP-1050`); `IP-1021`'s own new placement pass
  slots into it without disturbing the contract, but this was not explicitly re-confirmed by
  `VR-1021` and is exactly the class of cross-package seam this review exists to check.

**Finding:** `GW_KI_PLACED` (`asm_game.py:136`, `0xC3F5`, `IP-1021`'s own new transient
"leaves-placed-so-far" scratch counter) is used in shipped code but has **no corresponding row in
GDS-07's WRAM table**. Every other `generate_world` transient scratch byte this codebase has ever
added (`GW_TOP_ROW`, `GW_REGION_IDX`, `GW_B_SCRATCH`, `GW_SCALE_SQ`, `GW_MAZE_DIR`, `GW_BRAID_IDX`,
`GW_MAZE_DRAW_CTR`) has its own documented table row — `GW_KI_PLACED` breaks that established
convention. `GDS-07`'s own summary line ("Net new WRAM: 85 bytes... entirely inside the
`0xC3A0`–`0xC3F4` range," line 260) is now also inaccurate — the range should read `0xC3F5`, 86
bytes. Confirmed harmless functionally (well inside bank-0, `0xC000`-`0xCFFF`, no collision with
any other address; the byte is unconditionally reset to `0` at the top of every placement-pass run,
so no cross-call staleness risk) — a documentation-completeness gap, not a code defect.

## Dimension 2 — Invariant sweep

**Clean** (aside from the WRAM-documentation finding above, which is a documentation-coherence
matter, not an invariant violation).

- **ROM budget:** 32768 bytes exactly, no overflow, ~9.8KB headroom remaining (well above
  `BL-0019`'s 2KB re-affirmation concern line).
- **VBlank-gating:** `IP-1021`'s new placement pass touches only WRAM (`KEYITEM_FLAGS`,
  `GW_KI_PLACED`, `GW_MAZE_DIR`/`GW_BRAID_IDX` reused as scratch) — no VRAM writes, no LCD-timing
  surface to check.
- **One-job-per-file:** no module boundary crossed; all changes confined to `asm_game.py`/
  `worldgen.py`/`test_rom.py`, matching the package's own declared file set.
- **Tile-index collision:** `IP-1021` adds no tiles — no interaction with `IP-1081`'s new
  `0x1A`-`0x1D` slots.

## Dimension 3 — Behavioral coherence

**Clean.** Independently re-drove the full new-game → placement → collection → victory path live
via PyBoy at two non-default `(seed, scale)` pairs not used by any single-package VR's own corpus
(`seed=65535, scale=6` and `seed=55432, scale=8`, real MAIN MENU → SEED/SCALE ENTRY UI path, not
the `T12` direct-invoke fixture): exact `WORLD_SCALE`-count placement, oracle parity, and correct
victory-threshold triggering (not one below) confirmed in both cases — this exercises the same
evidence `VR-1021` already gathered, re-confirmed here as still holding against the current tree
head (which additionally carries `IP-1082`'s disjoint changes). No behavioral divergence between
`IP-1021`'s placement logic and any other package's own understanding of `KEYITEM_FLAGS`'s
semantics (`setup_zone_collects`/`check_collisions`, confirmed above) or of `WORLD_SCALE` as the
victory threshold (`check_complete`, `IP-1021`'s own sole change, confirmed unique — no other
routine independently hardcodes a victory count).

## Dimension 4 — Traceability coherence

**Clean, one Low finding (pre-existing, not introduced by `IP-1021`).** `FR-9160`/`FR-9161`'s RTM
rows correctly cite `IP-1021`/`T12.e`/`T12.n`/`T4.8`; `FR-9130`/`FR-3300` correctly show
"superseded... implemented 2026-07-13" in both the FR text and the RTM. Master Build Plan,
`packages/INDEX.md`, verification `INDEX.md`, and `ROADMAP.md` all agree `IP-1021` is `VERIFIED`.

**Finding (pre-existing):** `docs/feature-planning/03-feature-catalog.md`'s `FEAT-9000` entry
still lists `FR-9130` (not `FR-9160`, its direct successor) in its own "Included Requirements"
field (line 397), and its "Purpose" text (line 381-383) still reads "exactly one collectible
KeyItem per region" — factually superseded by `IP-1021`'s scale-relative, dead-end-prioritized
placement. This is **already a named, tracked Open Question** — `FS-102`'s own forward-reference
note and the `FEAT-9000` catalog entry's own metadata block (line 373-374) both flag it as "OQ4...
routed to `05-feature-decomposition`, out of [`06`'s] own write scope" — but no `BL-xxxx` backlog
entry exists yet to carry it forward, so it risks being lost between sessions. Filed as `BL-0098`
below to close that gap; the underlying staleness itself is not new, `IP-1021` only sharpens how
wrong the "exactly one" claim now reads relative to the shipped code.

## Dimension 5 — Documentation coherence

**Clean** aside from the two findings already named above (GDS-07's WRAM table, `FEAT-9000`'s
stale Purpose/Included-Requirements text) — both documentation-completeness gaps, neither a
functional defect. `Claude.md`/`memory.md` carry no `IP-1021`-attributable staleness (neither
names the old "one per region"/"CARROTS_COUNT==9" rule in a way `IP-1021` invalidates — both
already describe the game generically enough, confirmed by direct grep for "carrot" and "9" count
claims).

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| 1 | `docs/architecture/07-data-model.md` (GDS-07 §7b/§7c, WRAM table) | `GW_KI_PLACED` (`0xC3F5`, `IP-1021`'s own new transient scratch) has no table row, breaking this codebase's own established "every `generate_world` scratch byte gets documented" convention; the "Net new WRAM: 85 bytes... `0xC3A0`-`0xC3F4`" summary line is stale (should be 86 bytes, `0xC3A0`-`0xC3F5`). | Medium | `03-architecture-design-synthesis` (a GDS-07 delta adding the missing row + correcting the range summary) |
| 2 | `docs/feature-planning/03-feature-catalog.md` (`FEAT-9000` entry) | "Included Requirements" still cites `FR-9130` (superseded); "Purpose" text still claims "exactly one collectible KeyItem per region," contradicted by `IP-1021`'s shipped scale-relative, dead-end-prioritized placement. Already flagged as an internal Open Question (`FS-102`'s own OQ4) but had no backlog entry — filed as `BL-0098`. | Low | `05-feature-decomposition` (per `FS-102`'s own routing) |

No Critical/High findings. Both findings are documentation-completeness gaps with no runtime
behavioral consequence — confirmed by this review's own live re-drive (Dimension 3) and direct
code trace (Dimension 1), not merely inferred from the missing text.

## Next step

Clear to treat `IP-1021`'s win-condition redesign as fully integrated. Advances alongside the rest
of the tree to `11-release-readiness` whenever the user is ready to make that release call (not
this review's own decision) — not blocking any current work in the interim, since both findings
are Medium/Low, non-blocking, and already routed.
