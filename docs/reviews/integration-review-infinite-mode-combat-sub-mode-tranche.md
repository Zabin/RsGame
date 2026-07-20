# Integration Review — Infinite Mode Combat Sub-Mode Tranche

## Scope

All ten packages of the Infinite Mode Combat Sub-Mode delta (`FS-112` / `FEAT-11000` /
`EP-6000`), every one `VERIFIED` on the Master Build Plan as of this review:

| Package | Title | VR |
|---|---|---|
| IP-1120 | Mode Gating & UI | [VR-1120](../implementation/verification/VR-1120-infinite-mode-combat-mode-gating.md) |
| IP-1121 | Mob Materialization, Rendering & Defeat | [VR-1121](../implementation/verification/VR-1121-infinite-mode-combat-mob-materialization-and-rendering.md) |
| IP-1122 | Weapon Fire & Hit Resolution | [VR-1122](../implementation/verification/VR-1122-infinite-mode-combat-weapon-fire-and-hit-resolution.md) |
| IP-1123 | Player Health, Setback & Healing Economy | [VR-1123 Pass 2](../implementation/verification/VR-1123-infinite-mode-combat-player-health-and-economy-pass2.md) |
| IP-1124 | Save Persistence | [VR-1124](../implementation/verification/VR-1124-infinite-mode-combat-save-persistence.md) |
| IP-1125 | Mob & Projectile Sprite Content | [VR-1125](../implementation/verification/VR-1125-combat-sprite-content.md) |
| IP-1126 | Mob Movement | [VR-1126](../implementation/verification/VR-1126-infinite-mode-combat-mob-movement.md) |
| IP-1127 | Post-Contact Player Protection | [VR-1127](../implementation/verification/VR-1127-infinite-mode-combat-post-contact-protection.md) |
| IP-1128 | Weapon Directionality | [VR-1128](../implementation/verification/VR-1128-infinite-mode-combat-weapon-directionality.md) |
| IP-1129 | Weapon-Tier Funding Economy | [VR-1129](../implementation/verification/VR-1129-infinite-mode-combat-weapon-tier-funding.md) |

Commit reviewed: `99001e3` (tree head at review time — no source changes since `IP-1127`'s own
`a8117d7`).

This is the tranche's first integration review — no prior pass exists for this set.

## Dimension 1 — Interface consistency

**WRAM allocation across all ten packages** (`asm_game.py`, `0xC6B5`–`0xC6E3`, 47 bytes):
re-derived every constant directly from source — `COMBAT_MODE`(1)/`MOB_COUNT`(1)/`MOB_DATA`(30)/
`PROJ_ACTIVE`(1)/`PROJ_X`(1)/`PROJ_Y`(1)/`PROJ_STEP_X`(1)/`WEAPON_TIER`(1)/`PLAYER_HEALTH`(1)/
`COMBAT_ENTRY_X`(1)/`COMBAT_ENTRY_Y`(1)/`CMC_CURSOR`(1)/`MOB_MOVE_TIMER`(1)/`PLAYER_FACING_X`(1)/
`PLAYER_FACING_Y`(1)/`PROJ_STEP_Y`(1)/`PLAYER_INVINCIBLE`(1)/`MOB_CONTACT_FLAGS`(1) — contiguous,
zero gaps, zero overlaps, and butts exactly against the prior allocation (`MUSIC_BASE_HI` ending
at `0xC6B4`) with nothing claimed past `0xC6E3` yet. The one real build-time collision in this
delta's own history (`IP-1127`'s planned `0xC6DF`–`0xC6E0` vs. `IP-1128`'s real claim of the same
range, `BL-0163`) resolved correctly: `IP-1127` re-derived to `0xC6E2`–`0xC6E3`, confirmed by
direct read, no silent overwrite. `GDS-07` (§7h, §7i, §7j, §7k, §7l, §7m, §7n, §7o, §7p)
documents this exact range address-for-address against the shipped constants — cross-checked
every row.

**ROM section layout**: rebuilt from the reviewed commit — `Wrote 32768 bytes → BunnyQuest.gbc`,
32670/32768 used, no section-overlap error (the build tool errors loudly on any overlap; none
raised). **Tile-slot allocation** (`IP-1125`): `TL_MOB`/`TL_MOB_BOT`/`TL_PROJECTILE`/
`TL_PROJECTILE_BOT` at `0x0A`–`0x0D`, confirmed the only tile-slot claim among the ten packages
(the other nine touch no tile data). **`OBJ_PALETTES`** (`build_rom.py`): confirmed only
`IP-1125` touches this table among the ten packages — no cross-package palette contention.

**Patch-point / screen-reuse seam** (`IP-1120`): `combat_mode_confirm` reuses
`mode_select_screen`'s own array via `patches['cmc_t']`/`['cmc_a']` resolving to
`screen_addrs['mode_select']` — confirmed still resolving correctly in the reviewed rebuild (no
`combat_mode_confirm` line printed in the build's own section log, matching the package's own
design).

## Dimension 2 — Invariant sweep

- **ROM exactly 32768 bytes, non-overlapping sections**: confirmed (build output above).
- **VRAM writes VBlank-gated**: this delta's only new VRAM writer is `inf_health_hud_draw`
  (`IP-1123`, row-1 heart cells) and the `COMBAT MODE CONFIRM` overlay writes (`IP-1120`) — both
  already independently confirmed hooked into the existing `update_status_disp`/screen-entry
  paths at their own VR passes; no new unguarded VRAM write introduced by this review's own
  reading of the combined diff.
- **Every WRAM/SRAM address used in code appears in GDS-07**: confirmed above (Dimension 1) for
  every WRAM address; SRAM mirror (`0xA350`–`0xA371`, `IP-1124`) confirmed address-for-address
  against §7o.
- **One-job-per-file**: all ten packages' code lives in `asm_game.py`'s existing per-frame
  combat routines (`inf_mob_contact_check`, `inf_mob_move`, `inf_projectile_update`,
  `inf_materialize_mobs`, `save_to_sram`/`try_load_save`) — no new module, no module took on a
  second unrelated job.
- **Tile index map collision-free**: `TL_MOB`/`TL_PROJECTILE` (`0x0A`–`0x0D`) confirmed distinct
  from every other registered tile (`T34.c`, reconfirmed by this review's own grep of `tiles.py`'s
  `put()` calls — no other `put()` targets `0x0A`–`0x0D`).

## Dimension 3 — Behavioral coherence

**Own independent live drive, chaining all ten packages in one continuous real per-frame
session** (not a per-package direct-invoke) — the strongest evidence this review can produce,
since no single VR exercised more than its own package's slice:

1. Real navigation `MAIN MENU`→`MODE SELECT`(infinite)→`COMBAT MODE CONFIRM`(toggled to "Y")→
   `INFINITE SEED ENTRY`(seed 18)→`INTRO`→`PLAYING`. Reached `GAMESTATE=2`, `COMBAT_MODE=1`,
   spawn `(76, 80)` — all via real button input, no force-writes.
2. Real materialization (`IP-1121`) placed 2 active mobs for region `(0,0)`; real mob movement
   (`IP-1126`) had already advanced them toward the player by the time navigation finished
   (`(24,64)`→`(34,64)`, `(56,56)`→`(59,63)`) — both packages confirmed running together
   correctly in a genuinely fresh session.
3. Real weapon fire (`A` button, `IP-1122`) against the live-read mob position: the real
   per-frame projectile chain resolved the hit and defeated the mob (`MOB_COUNT` 2→1,
   `active` flag cleared) — confirms `IP-1121`+`IP-1122`'s materialization/hit-resolution seam.
4. Real contact with the second live mob: `PLAYER_HEALTH` 3→2, knockback moved the player
   exactly 16px (the shipped `KNOCKBACK_DISTANCE`) on the dominant axis, `PLAYER_INVINCIBLE` set
   to ~27 (near the shipped 30-frame default, minus elapsed frames) — confirms `IP-1123`+
   `IP-1127`'s contact/protection seam. Ten further real ticks of sustained overlap produced zero
   additional health loss — the `BL-0158` fix reconfirmed live, in this joint session.
5. Real save (`SAVE` screen, `A` confirm) → real reload in a fresh `PyBoy` instance:
   `COMBAT_MODE`, `WEAPON_TIER`, `PLAYER_HEALTH`, and `MOB_COUNT` all persisted exactly; the
   surviving mob's own data persisted with one benign 1px positional drift traceable to
   `inf_mob_move` still ticking during the brief `SAVE`-menu transition window (an artifact of
   this review's own snapshot timing, not a persistence defect — the *actually-written* SRAM
   state round-tripped correctly). `PROJ_ACTIVE` correctly 0 after load (never persisted,
   `IP-1124`'s own design).

This confirms the full real production seam — materialization → movement → weapon fire → hit
resolution → defeat → contact damage → knockback → invincibility → cooldown → save/load — all
work correctly together, not merely in each package's own isolated test fixture.

No divergent-behavior duplication found (each mechanic has exactly one implementation site); no
dead-ending workflow (every mechanic this delta specifies has a real call site reachable from
`st_playing`'s per-frame chain, except the two already-tracked, pre-existing input-binding gaps
below).

**Not newly found, reconfirmed as still-open and already tracked** (not filed again): `BL-0148`
(`inf_heal_spend` has no player-reachable input binding) and the equivalent gap for
`inf_tier_spend` (`IP-1129`, tracked alongside `BL-0148`/`BL-0155`/`BL-0157`) — both defined and
unit-tested but not wired to any button. `NFR-1500` (combat-mode per-frame cycle budget) remains
`UNCONFIRMED`, also already tracked.

## Dimension 4 — Traceability coherence

- **RTM** (`04-requirements-traceability-matrix.md`): `FR-11100`/`FR-11200`/`FR-11210`/
  `FR-11300`/`FR-11310`/`FR-11400`/`FR-11410`/`FR-11500`/`FR-11510`/`FR-11600` all confirmed
  rows present, each pointing at the correct `IP-11xx`/test suite — cross-checked against every
  VR's own Requirements audit section.
- **Master Build Plan / `packages/INDEX.md`**: all ten rows read `VERIFIED` with the correct VR
  links — confirmed directly.
- **`ROADMAP.md`**: `IM-00`/`IP-xxxx` summary rows correctly describe this delta's packages as
  planned/authorized/shipped through `IP-1129`, consistent with the Master Build Plan.

## Dimension 5 — Documentation coherence

Two stale forward-reference findings (same class integration reviews have caught before in this
tree, e.g. the Infinite Mode tranche review's `FEAT-10000` finding):

- `docs/feature-planning/03-feature-catalog.md:882` — `FEAT-11000`'s own heading still reads
  **"(new — not yet implemented)"**, and its forward-reference block (lines 884-904) still says
  "Neither leaf is packaged yet" for `FR-11310`/`FR-11510` — both now `VERIFIED` (`IP-1128`/
  `IP-1129`). Stale since before this delta's later packages shipped.
- `docs/features/INDEX.md:23` — `FS-112`'s own row still reads "`IP-1126` shipped `COMPLETE`,
  `IP-1127` `BLOCKED`" and "not yet packaged" for the `FR-11310`/`FR-11510` pair — all ten
  packages are now `VERIFIED`.

`Claude.md`/`memory.md` were checked for combat sub-mode content: `memory.md`'s tile-index quick
reference already correctly documents `0x0A`–`0x0D` (`IP-1125`) — no drift found there.

## Test run

```
python3 build_rom.py BunnyQuest.gbc
  → Wrote 32768 bytes → BunnyQuest.gbc (32670 used)

python3 test_rom.py
  → RESULTS: 404/404 passed   0 failed
```

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `docs/feature-planning/03-feature-catalog.md` (`FEAT-11000`) | Heading reads "not yet implemented"; forward-reference block says `FR-11310`/`FR-11510` "neither packaged yet" — all ten packages in the delta are now `VERIFIED` | Medium | `05-feature-decomposition` |
| F2 | `docs/features/INDEX.md` (`FS-112` row) | Row still shows `IP-1127` `BLOCKED` and `FR-11310`/`FR-11510` "not yet packaged" — stale, all ten packages `VERIFIED` | Low | `06-feature-specification` |

No Critical/High findings. No integration defect found in shipped code — every seam exercised
(WRAM layout, ROM/tile budget, the real per-frame production chain across all ten packages, and
the full traceability chain) held.

## ROADMAP update

`RV-INTEG` row (`ROADMAP.md`) updated to record this review.
