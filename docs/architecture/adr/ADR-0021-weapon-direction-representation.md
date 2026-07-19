# ADR-0021 — Weapon-direction representation: a new `PLAYER_FACING` concept, 8-way, per-axis-independent projectile stepping, no new player art

**Status:** Accepted (2026-07-19)

## Context

The shipped weapon (`IP-1122`) fires only left/right because `PROJ_DIR` copies `PLAYER_DIR`
verbatim, and `PLAYER_DIR` is a 2-value fact — direct code read confirms it is written only by
`handle_play_input`'s RIGHT/LEFT branches (0=right, 1=left), never UP/DOWN, and is read exactly
once elsewhere, at OAM-render time, to isolate its bit 0 into the sprite's X-flip attribute bit.
The user filed `BL-0157`: the weapon should also fire up/down/diagonal, based on movement, and
asked for research into how other games handle this before it is architected.

[R220](../../research/encyclopedia/R220-movement-based-directional-aiming.md) grounds the survey:
overhead run-and-gun titles (Commando, Ikari Warriors, Front Line) tie firing direction directly
to movement input in either a 4-way or 8-way scheme (a genre tone/pacing choice, not a technical
one); *The Legend of Zelda: Link's Awakening* resolves the "last-pressed vs. held" direction
question as "moving direction if moving, else last-faced direction if idle." R220 deliberately
leaves the 4-way-vs-8-way choice and the WRAM-representation choice to this architecture pass.

## Decision

**1. A new, separate WRAM concept (`PLAYER_FACING`, working name) carries the direction — `PLAYER_DIR`
is not widened.** `PLAYER_DIR` stays exactly as shipped: 2-value, left/right, driving the existing
X-flip render unchanged; nothing that already reads or writes it changes. Mirrors this project's
own established precedent for exactly this situation — `IP-1127`'s own planning chose a new
parallel `MOB_CONTACT_FLAGS` table over widening `MOB_DATA`'s shared stride, for the identical
reason (a widened shared field risks every existing consumer; a new field risks nothing already
shipped). Here the calculus is more one-sided still: `PLAYER_DIR` has exactly one non-copy
consumer, and Decision 4 below means that consumer's behavior does not need to change at all.

**2. Eight-directional, not four.** R220 leaves this open as a tone call; this project's own
concrete fact tips it: `handle_play_input`'s RIGHT/LEFT/UP/DOWN branches are independent
`BIT`-tested branches, not a mutually-exclusive chain — holding e.g. RIGHT+UP already moves the
player diagonally today. A weapon restricted to 4-way would fire a narrower direction set than
the player can already move in. 8-way keeps the weapon's expressive range matching the movement
model that already exists, at no additional input cost.

**3. Diagonal projectile motion is simultaneous independent per-axis stepping, not vector math.**
This project's existing 2D-movement idiom (the player's own D-pad handling; `IP-1126`'s
`inf_mob_move` dominant-axis stepping) is single-axis-at-a-time integer stepping — no
trigonometry, no multiplication (SM83 has neither natively). The player's own "diagonal movement"
today is two independent per-frame `INC`/`DEC` operations on `PLAYER_X`/`PLAYER_Y` that happen to
run in the same frame, not a diagonal primitive. `PLAYER_FACING` decodes to an independent
per-axis step (`-1`/`0`/`+1` on each of X and Y); `inf_projectile_update` applies both steps every
frame instead of only the X step it applies today. No new hardware-level technique.

**4. No new player sprite art.** The player's walk-cycle sprite keeps rendering exactly as today
(frame animation + X-flip only) regardless of `PLAYER_FACING`'s value, since `PLAYER_DIR` (the
render's only input) is untouched by Decision 1. Consistent with
[R218](../../research/encyclopedia/R218-combat-enemy-design-opt-in-submode.md)'s own "abstract
stakes over graphic depiction" convention and this feature's own repeated pattern of reusing
existing art at zero new cost. `ADR-0007`'s 8×16 OBJ mode has no established Y-flip/diagonal
frame set to reuse, and authoring one is new art scope this decision does not ask for — a future
`09-content-review` pass may recommend it later as a purely additive follow-on.

## Consequences

- Resolves `BL-0157`'s own architecture-level question, recorded as a delta to
  [ADS-002](../ADS-002-infinite-mode-combat-sub-mode.md) ("Weapon Directionality Delta,"
  2026-07-19) — `04-requirements-engineering` can now baseline a real `FR-11xxx` leaf against a
  concrete representation shape.
- **Does not fix `PLAYER_FACING`'s exact bit encoding or WRAM address** — a compact 3-bit compass
  value vs. two signed 1-bit-per-axis fields vs. some other shape is `07-implementation-planning`'s
  own job, following `GDS-07`'s existing address-allocation convention (the next free byte past
  whatever is highest at implementation time).
- **Does not decide whether `PLAYER_FACING` updates every held-direction frame or only on
  transition** — the "idle preserves last facing" semantics R220 recommends requires distinguishing
  "held" from "just-changed" somewhere; named as an open implementation detail, not resolved here.
- **Adds to, does not create, `NFR-1500`'s existing risk** — the direction-decode and the
  projectile's new second per-frame axis step are additional per-frame cost on an already-
  `UNCONFIRMED` cycle budget every combat package since `IP-1121` already carries; not measured
  here.
- **No `GDS-07` delta yet** — `PLAYER_FACING` is not a fixed address until `07` picks one;
  `GDS-07`'s existing `PLAYER_DIR` row (`C003`, "facing (left/right)") stays accurate and
  unchanged, since Decision 1 leaves it untouched.
- **Does not itself implement anything** — ships through the normal `04`→`08` pipeline, gated by
  G3, like every other combat-sub-mode package before it.

## Related

- Recorded as a delta in
  [ADS-002](../ADS-002-infinite-mode-combat-sub-mode.md#weapon-directionality-delta-2026-07-19-bl-0157-grounded-by-r220)
  ("Weapon Directionality Delta").
- Grounded by [R220](../../research/encyclopedia/R220-movement-based-directional-aiming.md)
  (movement-based directional aiming conventions) and
  [R218](../../research/encyclopedia/R218-combat-enemy-design-opt-in-submode.md) (the
  abstract-over-graphic tone convention Decision 4 relies on).
- Mirrors, without amending, `IP-1127`'s own "new parallel structure over widened shared field"
  precedent for `MOB_DATA`/`MOB_CONTACT_FLAGS` (`docs/implementation/packages/IP-1127-infinite-mode-combat-post-contact-protection.md`).
- Resolves [BL-0157](../../pipeline/backlog.md)'s own architecture-level routing.
