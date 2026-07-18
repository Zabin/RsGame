# VR-1125 — Combat Sub-Mode: Mob & Projectile Sprite Content

## Package

`IP-1125` (commit `74d53c4`, "feat(content): IP-1125 -- combat sub-mode mob & projectile
sprites"), verified against the current tree head.

## Result

**VERIFIED** — 0 failed checks (one Low-severity scope-documentation finding, does not block).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Four new tiles registered, visually confirmed distinct | Code read: `tiles.py:28-31` (`TL_MOB=0x0A`, `TL_MOB_BOT=0x0B`, `TL_PROJECTILE=0x0C`, `TL_PROJECTILE_BOT=0x0D`), `tiles.py:984-987` (`put()` registrations in `build_tile_data()`). **Independently re-derived live** (own standalone script, not the suite's own test): forced OAM entries 5/6 to render `TL_MOB`/`TL_PROJECTILE` at distinct positions, ticked 3 frames, read the tile bytes back from VRAM (`0x8000+0x0A*16`/`0x8000+0x0C*16`) — both non-zero, byte-for-byte distinct from each other; own screenshot confirms a purple mob silhouette and an orange/red projectile orb both rendering on-screen, visually distinct from the player sprite and every existing collectible OBJ tile | PASS |
| ROM builds at exactly 32768 bytes with the full suite passing | Build: 32768 bytes, valid header (31390/32768 used). Suite: **330/330 passed, 0 failed**, includes `T34.a`-`d` | PASS |
| No palette budget regression | `OBJ_PALETTES` (`build_rom.py:60-68`) confirmed still exactly 8 fixed-size entries by direct read; slots 4/5 (previously `[BLACK, WHITE, WHITE/OB_LITE_PNK, WHITE/OB_HOT_PNK]` placeholders) now hold the mob/projectile's real colors — no new slot appended, no existing slot 0-3/6-7 touched | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| G5: ROM builds at exactly 32768 bytes with valid header | Confirmed this run | PASS |
| G5: full `test_rom.py` suite passes | 330/330 | PASS |
| `TL_MOB`/`TL_MOB_BOT`/`TL_PROJECTILE`/`TL_PROJECTILE_BOT` all present in `build_tile_data()`'s output at `0x0A`-`0x0D` | `T34.a`/`T34.b` PASS; confirmed by direct read of `tiles.py:28-31`/`984-987` | PASS |
| Screenshot confirms both new sprites render and are visually distinct from every existing OBJ tile and from each other | `T34.c` PASS (byte-for-byte distinctness audit). **Independently re-driven this run**: own standalone script, own screenshot (not reusing the implementing commit's own capture) — both sprites visible and distinct in-frame | PASS |
| No new palette slot claimed beyond what this package's own drafting needs | `T34.d` PASS (`OBJ_PALETTES` count == 8); confirmed by direct read that slots 4/5 were pre-existing placeholder entries, not newly appended | PASS |

## Requirements audit

- **`FR-11200`** (mob presence) / **`FR-11300`** (projectile): this package supplies the concrete
  visual asset both future packages (`IP-1121`/`IP-1122`, `NOT STARTED`) will render — neither FR
  names tile art directly, per `04`'s own implementation-independence discipline, correctly
  matching this package's own §3 framing. No RTM row exists yet for either FR pointing at
  `IP-1125` specifically (both FRs are `UNASSIGNED` in the RTM pending their own owning packages)
  — consistent with this package covering only the content half, not a full requirement
  delivery; not a gap this VR should fabricate a correction for.

## Test run

- `python3 build_rom.py BunnyQuest.gbc` → 32768 bytes, `Total used: 0x7A9E (31390/32768)`, valid
  header.
- `python3 test_rom.py` → **330/330 passed, 0 failed**.
- Independent standalone PyBoy script: fresh boot → `advance_to_playing`, forced OAM entries 5/6
  to render `TL_MOB` (palette 4) and `TL_PROJECTILE` (palette 5) at distinct screen positions,
  ticked 3 frames, read tile bytes back from VRAM directly (non-zero, byte-distinct), captured a
  fresh screenshot — confirms a purple mob silhouette and an orange/red projectile orb both
  render on-screen, clearly distinct from the pink bunny player and every existing carrot/
  star/flower OBJ tile.

## Scope audit

Commit `74d53c4` touches: `tiles.py` (declared, §6), `test_rom.py` (declared, §8),
`docs/architecture/07-data-model.md` + `00-master-build-plan.md` + `packages/INDEX.md` +
`memory.md` (declared, §9/ledgers), `BunnyQuest.gbc`, `test_results.txt` — **and `build_rom.py`
(+4/-2 lines), repurposing `OBJ_PALETTES` slots 4/5 from placeholder colors to the mob/projectile's
real palette**. `build_rom.py` was **not named in the package's own §6 Files to Create/Modify**
(only `tiles.py` and a confirm-only note on `asm_game.py`'s DMA count) — a genuine, if narrow,
excursion. The touch itself is minimal, correctly scoped to the objective (assigning real colors
to two already-existing placeholder slots, zero new slots, zero other-slot disturbance — verified
above), and the package's own DoD/§8 implicitly anticipated palette assignment being necessary
("no new palette slot claimed beyond what this package's own drafting needs"). Not a functional
defect; a planning-document gap.

## Findings

| Finding | Severity | Owner |
|---|---|---|
| `IP-1125` §6 (Files to Create/Modify) omits `build_rom.py`, but the shipped implementation correctly and necessarily touched it (`OBJ_PALETTES` slots 4/5, real colors for the mob/projectile) to satisfy the package's own DoD. The touch itself is safe and in-scope by intent — only the package's own file inventory is stale. | Low | `07-implementation-planning` (a documentation-only correction to `IP-1125` §6 on its next touch; does not require re-implementation) |

## Independence note

Implemented in a prior session (`74d53c4`, 2026-07-18 per commit timestamp, prior to this
verification run); this verification runs in a fresh session with no implementation history for
this package — full independence.
