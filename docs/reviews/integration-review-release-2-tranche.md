# Integration Review — Release 2 Tranche (Procgen-World Increment)

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

Release 2's full package set, all `VERIFIED` on the Master Build Plan:

| Package | Title | VR |
|---|---|---|
| IP-1020 | Procedural world generation & item-agnostic collection (FS-102 / FEAT-9000) | [VR-1020](../implementation/verification/VR-1020-procedural-world-generation.md) |
| IP-1030 | Generated-region screen composition — code (FS-103 / FEAT-4100) | [VR-1030](../implementation/verification/VR-1030-generated-region-screen-composition-code.md) |
| IP-1031 | Generated-region screen composition — content (FS-103 / FEAT-4100) | [VR-1031](../implementation/verification/VR-1031-generated-region-screen-composition-content.md) |
| IP-1040 | Main menu & new-game flow (FS-104 / FEAT-1100) | [VR-1040](../implementation/verification/VR-1040-main-menu-new-game-flow.md) |
| IP-1050 | Generated-world save persistence (FS-105 / FEAT-5300) | [VR-1050](../implementation/verification/VR-1050-generated-world-save-persistence.md) |

**Commit reviewed:** `9fdca5b` (tree head at review time). All five packages confirmed `VERIFIED`
on the Master Build Plan before this review began.

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x57C8 (22472 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
sha256sum BunnyQuest.gbc              → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd
                                          (identical to the checked-in ROM)
python3 test_rom.py                   → RESULTS: 231/231 passed   0 failed
```

## Dimension 1 — Interface consistency

**Clean.** Exercised the real seams between packages:

- **Patch-point dict contract** (`build_game_asm(rom) -> patches`, consumed by `build_rom.py`):
  cross-referenced every `patches[...]` write in `asm_game.py` (both literal-string sites and the
  `_dsr_screen`/`_dsr_family` helper-generated keys, `title_t`/`_a`, `intro_t`/`_a`, `save_t`/`_a`,
  `map_t`/`_a`, `vic_t`/`_a`, `mm_t`/`_a`, `sse_t`/`_a`, and the five `water`/`sand`/`grass`/
  `stone`/`brick` `_t`/`_a` pairs) against every key `build_rom.py` consumes — `comm -3` on the
  two sorted key sets: zero orphans on either side, all twelve `ALL_SCREENS` entries (5 biome
  families + 7 UI screens) resolved.
- **`ALL_SCREENS`** (`tilemaps.py`): consumed by `build_rom.py`'s `for name, fn in ALL_SCREENS`
  loop and `asm_game.py`'s `dsr_p` dispatch; ordering/shape unchanged across all five packages —
  the printed T/A address pairs in the build output are strictly monotonic and non-overlapping
  (water `0x2135` through seed_scale_entry `0x54F5`).
- **`ZONE_COLLECTS`/`zc_table`** (a seam `IP-1020`'s spawn logic, `IP-1030`'s tile-family
  registration, and `IP-9070`'s biome-keyed lookup all touch): confirmed 5 biome-family entries,
  `build_rom.py`'s emission loop unchanged and list-length-agnostic (already independently
  confirmed in `VR-9070`/`VR-1031`, re-confirmed here as still true at this tranche's own commit).
- **Save-field contract** (`IP-1020`'s `KEYITEM_FLAGS`, `IP-1040`'s `SEED`/`WORLD_SCALE`
  generation trigger, `IP-1050`'s SRAM mirror): live end-to-end walkthrough (Dimension 3) confirms
  all three packages agree on the field set actually persisted and restored.

## Dimension 2 — Invariant sweep

**Clean.** Checked across the whole set, not sampled:

- **ROM budget:** exactly 32768 bytes, valid header, byte-identical rebuild (`sha256` match).
- **VBlank-gating:** the five packages' own VRAM-writing entry points (`dsr_p`/`draw_region_arrows`
  via `do_screen_redraw`'s LCD-off bracket; `mm_on_entry`/`draw_menu_cursor`/`draw_sse_digits`,
  all likewise only reachable through the same `do_screen_redraw` gate) — no package introduces an
  independent VRAM writer outside that established bracket; confirmed by direct grep for
  `0x98xx`/`0x99xx`-region writes, all trace back to the same gated call chain.
- **WRAM/SRAM address map:** every WRAM/SRAM constant this tranche's packages introduce (`SEED`,
  `WORLD_SCALE`, `REGION_GRAPH`, `KEYITEM_FLAGS`, `GW_TOP_ROW`..`GW_SCALE_SQ`, `MM_CURSOR`,
  `SSE_CURSOR`, `SRAM_SEED`, `SRAM_WORLD_SCALE`, `SRAM_KEYITEM_FLAGS`) appears in GDS-07's table
  with a matching address — confirmed present, **but see Finding 1 below**: two of GDS-07's own
  table cells describing these addresses are stale in *content*, not missing.
- **Tile index map:** collision-free — `IP-1031` added zero new tiles (confirmed `VR-1031`);
  `IP-1030`'s five biome-family blocks (`0x70`–`0xB5`) remain non-overlapping (confirmed `VR-1030`
  originally, re-confirmed unchanged here).
- **One-job-per-file:** unaffected — no package altered the six-module decomposition.

## Dimension 3 — Behavioral coherence

**Clean.** Directly drove the full cross-package player workflow live in PyBoy (fresh boot, no
prior save) to confirm no seam dead-ends:

```
Boot -> GS=6 (MAIN MENU, IP-1040)
A (new game) -> GS=7 (SEED/SCALE ENTRY, IP-1040)
A (confirm defaults) -> GS=1 (INTRO) -- SEED=0, SCALE=3, generate_world runs (IP-1020)
A (confirm) -> GS=2 (PLAYING), CUR_ZONE=0 -- region 0 rendered via IP-1030/1031's grass-family screen
Forced position onto region 0's own star -> SCORE=1 (collection fires, IP-1020's item-agnostic model)
START -> GS=3 (SAVE)
A (confirm save) -> GS=2 (PLAYING) -- IP-1050's save_to_sram runs
[process restarted, fresh PyBoy instance, same .ram file]
Reboot -> GS=6 (MAIN MENU) -- IP-1050's save now readable
MM_CURSOR=0 (continue, not new-game) -- IP-1040's check_save_valid/mm_on_entry correctly detect
                                          the valid save IP-1050 just wrote
A (continue) -> GS=2 (PLAYING), CUR_ZONE=0, SCORE=1 -- world regenerated identically from the
                                                         persisted SEED/WORLD_SCALE (IP-1020),
                                                         KeyItem/score state restored (IP-1050)
```

Every package in the set participates in this one continuous flow with no divergence: world
generation (`IP-1020`) → screen rendering of the generated content (`IP-1030`/`1031`) → the
menu/new-game flow that triggers generation (`IP-1040`) → persistence and restoration of the
generated world's state (`IP-1050`). No player-visible workflow spans a package seam and
dead-ends.

## Dimension 4 — Traceability coherence

**One finding** — a stale cross-reference outside any single package's own file scope, not caught
by any individual `09-package-verification` run because it names a *different* package's own
status.

**Finding 1 (Low):** `docs/features/INDEX.md`'s `FS-103` row (line 14) reads: "code half VERIFIED
2026-07-10 (`IP-1030`/`VR-1030`), **content half implemented 2026-07-11 (`IP-1031`, clean content
review), own verification pending**" — stale as of this review. `IP-1031` reached `VERIFIED` this
session (`VR-1031`, 2026-07-12); `09-package-verification`'s own workflow updates the Master Build
Plan, verification `INDEX.md`, and (when a cell is directly proven wrong) the RTM, but does not
by convention touch `docs/features/INDEX.md` — so this row was never revisited after `IP-1031`
closed. All other rows checked (`FS-102`, `FS-104`, `FS-105`, `FS-106`) are current and accurate.

Everything else checked clean: Master Build Plan, verification `INDEX.md`, RTM, `packages/
INDEX.md`, and `ROADMAP.md` all agree that all five packages are `VERIFIED` and the tranche is
closed — cross-references bidirectional (each VR links back to its package; each package's row
links forward to its VR).

## Dimension 5 — Documentation coherence

**One finding** — GDS-07's own WRAM table has two stale cells describing content this tranche
(and one remediation-tranche package) shipped, never revisited as the packages landed.

**Finding 2 (Medium):** `docs/architecture/07-data-model.md` §"WRAM Data Model" (lines 163, 166):

- Line 163 (`SEED`'s own table row): *"Written by `FEAT-1100` (not yet shipped); read-only to
  `generate_world`."* — **stale.** `FEAT-1100` is `IP-1040`, `VERIFIED` 2026-07-11. `SEED` is
  written by `sse_compose_seed` (`asm_game.py:1158`), confirmed by direct read — the exact routine
  `IP-1040`'s own SEED/SCALE ENTRY flow implements.
- Line 166 (`KEYITEM_FLAGS`'s own table row, closing clause): *"...full `scale²`-extent clearing
  on new-game/replay is `FEAT-1100`'s scope once it wires up variable-scale play."* — **doubly
  stale.** `FEAT-1100` has shipped, **and** the 9-byte-to-81-byte clear-loop widening this clause
  describes as still-pending was actually done by a different package, `IP-9050`/`BL-0063` (a
  companion fix inside the post-ship remediation tranche, confirmed by direct code read:
  `asm_game.py:309-314`/`:377-379`, both explicitly commented "widened from the old 9-byte clear
  by IP-9050/BL-0063"), not by `IP-1040` as this sentence implies.

Both cells describe real, correctly-shipped behavior — the *substance* of GDS-07's WRAM map (the
addresses, sizes, and content) is accurate throughout, confirmed under Dimension 2. Only these two
narrative clauses, written when `FEAT-1100` was still a forward reference, were never revisited
once the packages they anticipated actually shipped — a documentation-currency gap spanning two
different packages' own §9 Documentation Updates lists (neither `IP-1040`'s nor `IP-9050`'s own
scope named this specific GDS-07 sentence as something to correct, since each package's own §9
reasonably assumed it covered its own new content, not a pre-existing forward-reference elsewhere
in the same document).

`Claude.md`/`memory.md` and `docs/architecture/INDEX.md` checked separately: all current, no
Release-2-related staleness found (the root-doc refresh, `IP-9030`, post-dates and reflects the
procgen model correctly).

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| 1 | `docs/features/INDEX.md` (FS-103 row) | Still describes `IP-1031` as "own verification pending" — stale since `VR-1031` closed it 2026-07-12. | Low | Whichever skill next touches `docs/features/INDEX.md` (a light metadata-only correction; no owning stage currently has standing instruction to revisit this file post-verification) |
| 2 | `docs/architecture/07-data-model.md` (GDS-07, `SEED`/`KEYITEM_FLAGS` table rows, lines 163/166) | Two narrative clauses describe `FEAT-1100`/`IP-1040` as "not yet shipped" and the `KEYITEM_FLAGS` clear-widening as still `FEAT-1100`'s pending scope — both shipped, and the widening was actually done by `IP-9050`, not `IP-1040`. Table data itself (addresses/sizes) is accurate. | Medium | `03-architecture-design-synthesis` (a GDS-07 delta correcting these two cells, citing `IP-1040`/`IP-9050` as the packages that actually resolved them) |

No Critical/High findings. Both findings are documentation-currency gaps that predate this
review and were not introduced by any package in this set's own shipped behavior — the code and
its own local documentation (package documents, `Claude.md`, `memory.md`) are accurate throughout.

## Next step

No Critical/High findings — this tranche is clear to advance to `11-release-readiness` whenever
the user is ready to make that release decision (not this review's own call). The two Low/Medium
documentation findings don't block that decision; they're routed to their respective owning
skills above.
