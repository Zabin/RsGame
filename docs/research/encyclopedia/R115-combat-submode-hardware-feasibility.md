# R115 — Combat Sub-Mode Hardware Feasibility (Projectiles, Hit-Detection, OAM/APU Budget)

- **Document ID:** R115 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (SM83 cycle costs), R102 (VBlank/OAM-write timing discipline), R105
  (OAM entry format, shadow-OAM DMA, 8×16 OBJ mode), R108 (APU channel map — only channel 1 in
  use today)
- **Referenced By:** `docs/architecture/ADS-002-infinite-mode-combat-sub-mode.md`
- **Produces:** hardware-feasibility evidence for `ADS-002`'s fuller architecture pass
- **Feature Mapping:** `BL-0133` (Infinite Mode combat sub-mode)
- **Related Topics:** R101, R102, R105, R108, R218 (the design-side companion topic)

## Purpose

Establish whether a combat sub-mode (mobs, a fireable projectile, player health/damage) is
hardware-feasible on this project's own shipped SM83/OAM/APU budget, and at what concrete
headroom — the companion question to `R218`'s own game-design grounding, answering *can this
run*, not *should it look like this*.

## Scope

Projectile movement/collision cost per frame; concurrent-sprite OAM budget alongside the
existing player+collectible entries; APU channel headroom for combat sound effects. Explicitly
**out of scope**: enemy AI design conventions and tone (R218), the economy/persistence
architecture decisions (`ADS-002`'s own Open Questions).

## Concepts

**Per-frame CPU budget.** A single-speed CGB frame is 70,224 T-cycles (4,194,304 Hz / 59.7 Hz),
the same fixed budget `NFR-1400`'s own cycle-count work already measures against.[^1] Every
per-frame routine (movement, collision, redraw) competes for this budget; `inf_ensure_window`
already consumes 78,860–81,792 T-cycles on its own worst-case transition frame — a pre-existing,
accepted overage (`VR-1102`) that any *new* per-frame combat logic must not be layered onto
without separately re-measuring, since it would compound an already-`NOT MET` gate.

**OAM entry format and the 8×16 OBJ convention.** Each OAM entry is 4 bytes (Y, X, tile index,
attributes); this project's shadow-OAM buffer (`OAM_BUF`, `0xC300`–`0xC39F`, 160 bytes) holds
exactly 40 entries, DMA'd to real OAM once per frame.[^2] `ADR-0007` commits every sprite
(player, and by extension any future enemy) to 8×16 OBJ mode — one OAM entry covers a full
16-pixel-tall sprite, not two.[^3]

**No hardware collision detection exists on GBC** — the PPU provides no built-in sprite-overlap
flag; all hit-detection in this project (and any future combat mode) is software, point-in-box
arithmetic against WRAM-held coordinates, exactly as `check_collisions`' own asymmetric-tolerance
technique already does for collectible pickup.[^2] A ranged projectile therefore needs the same
class of per-frame position-update-then-test loop the existing movement/collision code already
performs — no new hardware capability required, only more instances of an already-proven pattern.

### Sources
[^1]: Frame timing derivation: CGB CPU clock 4.194304 MHz ÷ 70224 T-cycles/frame = 59.73 Hz — the same figure this project's own `NFR-1400` measurements (`VR-1102`) already use; [Pan Docs — Timing](https://gbdev.io/pandocs/Rendering.html), accessed 2026-07-17.
[^2]: [Pan Docs — OAM](https://gbdev.io/pandocs/OAM.html), accessed 2026-07-17 — 4-byte entry format, 40-entry OAM table, no hardware overlap/collision flag; direct code read confirms `OAM_BUF`'s own 160-byte/40-entry allocation (`asm_game.py`) and `check_collisions`' software point-in-box technique (`IP-9100`/`BL-0053`).
[^3]: `ADR-0007` (this project's own record), confirmed by direct code read of `LCDC=0x97` (bit 2 set, 8×16 mode).

## Operational Context

Direct count of this project's own current worst-case concurrent sprite use, confirmed by code
read: **1 player entry + up to 8 collectible entries** (`T1.12`'s own static check: "No zone
exceeds 8 collectibles," a 1-byte-bitfield capacity limit) = **9 of 40 OAM entries used, 31 free
(124 of 160 shadow-OAM bytes)**. This is the real, current headroom a combat mode's mob and
projectile sprites would compete for — not a hypothetical budget, the actual measured slack in
the shipped game today.

`music.py`/`asm_game.py`'s APU use is confirmed (by direct code read, `R108`) to occupy only
pulse channel 1 (`NR1x` registers) — channels 2 (`NR2x`, a second pulse channel), 3 (`NR3x`, the
wave channel), and 4 (`NR4x`, the noise channel) are entirely unused. A noise-channel (`NR4x`) hit
or damage SFX would not contend with the existing single-channel music engine at all — this is
the same headroom `ADR-0019`'s own "shared-ostinato/second-APU-channel" option (for procgen music)
noted and explicitly deferred, now available again for combat SFX instead.

## Implementation Guidance

- **Projectile movement**: implement as a small, fixed-size WRAM table (position, direction,
  active flag) updated once per frame inside the existing main-loop structure, mirroring how
  collectible positions already live in `COLL_DATA`/`COLL_COUNT` — no new hardware mechanism, a
  direct structural extension of an already-proven pattern.
- **Hit-detection**: reuse `check_collisions`' own asymmetric point-in-box arithmetic
  (`asm_game.py`, `IP-9100`'s fix) for projectile-vs-mob and mob-vs-player tests — already tuned
  and tested in this exact codebase; do not invent a new hitbox model.
- **OAM budget**: a combat mode adding, say, 4 concurrent mobs + 1 active projectile (5 new OAM
  entries) would bring worst-case concurrent use to 9+5=14 of 40 entries — comfortably inside the
  measured 31-entry headroom above, with margin to spare for a materially larger mob count if the
  design calls for it. Any concrete mob-count decision should re-derive this arithmetic against
  its own real number, not assume "headroom exists" without the count.
- **Cycle budget**: any new per-frame combat logic (projectile update, mob AI, hit-detection)
  must be measured against the *already-consumed* portion of the frame budget, not the nominal
  70,224-cycle ceiling alone — `inf_ensure_window`'s own worst-case transition frame already runs
  ~8,636–11,568 cycles over budget (`NFR-1400`, accepted/`NOT MET`). Combat logic that runs on a
  *different* frame than a region-materialization transition (i.e., not stacked on top of
  `inf_ensure_window`'s own worst case) avoids compounding that specific overage; if combat and
  materialization frames can coincide, this needs its own direct measurement before being assumed
  safe.
- **APU headroom**: a hit/damage SFX on the noise channel (`NR4x`) or the second pulse channel
  (`NR2x`) needs no new hardware capability and does not contend with the existing single-channel
  (`NR1x`) music engine — confirmed unused by direct code read.

## Feature Mapping

`BL-0133` (Infinite Mode combat sub-mode) — this topic closes the hardware-feasibility half of
`BL-0145`'s research gap (the design half is `R218`). `ADS-002`'s Open Question 6 (concurrent mob
count and spawn density) can now be answered against this topic's own concrete 31-entry-headroom
figure rather than an assumed one.

## Related Topics

R101 (cycle costs — the budget arithmetic above), R102 (VBlank/OAM-write discipline any new
sprite-update code must respect), R105 (the OAM entry format/8×16 convention this topic measures
against), R108 (the APU channel map — confirms channels 2–4 free), R218 (the design-side
companion — enemy defeat presentation, health HUD, difficulty-gating precedent).
