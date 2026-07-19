# R219 — Ranged-Weapon Upgrade & Progression Conventions

- **Document ID:** R219 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R218 (opt-in combat sub-mode design — this topic extends its weapon axis),
  R201 (collect-a-thon goal design — treasure's existing role as the base game's core collectible,
  now proposed to also fund weapon power)
- **Referenced By:** none yet — grounds a future `04-requirements-engineering` delta on `BL-0147`
- **Produces:** grounds a concrete `WEAPON_TIER` funding-mechanism design compatible with this
  project's own already-decided constraints (`ADS-002`: treasure is *spent*, not merely a
  triggering event; no ammo/durability; the weapon fires freely once owned)
- **Feature Mapping:** `BL-0155` (research request), `BL-0147` (the requirement gap this grounds)
- **Related Topics:** R218, R201

## Purpose

Ground how a treasure-funded weapon-power axis should actually progress for the Infinite Mode
combat sub-mode (`FS-112`). `WEAPON_TIER` shipped in `IP-1122` as a fixed, unreachable stat
(default 1, range 1-3 per its own WRAM comment) specifically because no upgrade mechanism was ever
designed — `BL-0147` tracks the missing requirement leaf, and the user named *Contra* directly as
a reference point when requesting this research. This topic surveys how comparable titles handle
weapon-power acquisition, loss, and scope, and recommends the shape that best fits this project's
own already-decided constraints rather than inventing a mechanic in a vacuum.

## Scope

Ranged-weapon power/tier progression conventions in run-and-gun and action-adventure titles:
what axis is typically upgraded (fire rate, projectile count/spread, damage, ammo type);
how upgrades are typically acquired (pickup-drop vs. currency-spent-at-a-shop vs. score-gated);
how upgrades are typically lost or retained (death-based full reset vs. persistent ownership).
Explicitly **out of scope**: the exact numeric tier count/thresholds and the exact projectile
behavior change per tier (a `04`/`06` decision, not a research conclusion); whether upgrades
should be visually distinct sprites (a future `08-content-authoring` concern if the design calls
for it).

## Concepts

**Pickup-drop, single-active-weapon-slot progression (Contra).** *Contra*'s own weapon system
grants a new weapon type by collecting a floating capsule (commonly "Falcon" icons) that drops
from a destroyed enemy or pod; collecting a new weapon-type icon *replaces* the currently held
weapon rather than stacking with it, so the player always holds exactly one weapon type at a
time.[^1] A separate "R" (Rapid Fire) pickup exists alongside the weapon-type icons and instead
modifies the *rate of fire* of whichever weapon is currently held — a genuinely orthogonal upgrade
axis from weapon type, though it does not affect every weapon type equally (the Laser, for
example, is unaffected by it).[^1] **On player death, all held weapon-type progress and Rapid
Fire stacking are lost**, and the player reverts to the base weapon — a full, unconditional reset
tied to the life-loss/continue system, not a partial downgrade.[^1]

**Currency-spent, persistent-purchase progression (Zelda's shop-upgrade convention).** A
structurally different, equally well-established pattern: the *Zelda* series' quiver/bomb-bag
capacity upgrades are bought outright with the game's own core collectible currency (rupees) at a
shop, for a fixed price, and once purchased the upgrade is a **permanent equipment-subscreen
state** — not lost on death, not re-purchasable, not decaying.[^2] This is a currency-*spent*
model in the same sense this project's own `ADS-002` already commits to (treasure decrements on
purchase, the upgrade is not merely triggered by proximity or score) and, critically, is
death-persistent rather than death-reset — the opposite of Contra's own pickup-drop convention on
that specific axis.

**Upgrade-system design principles (avoiding false choices).** Broader design guidance on
power-up/upgrade systems warns against pairing a small number of clearly load-bearing axes (health,
damage, defense) with a larger number of marginal ones (ammo capacity, reload speed, zoom speed) —
the latter category presents choices that don't actually matter to how the player plays, diluting
the perceived value of the system as a whole.[^3] A tiered, single-axis progression (this
project's own existing `WEAPON_TIER` shape: one integer stat, not a multi-axis loadout) already
avoids this pitfall structurally — the open question this topic grounds is *how that one axis is
funded and retained*, not whether to add more axes.

### Sources
[^1]: [Weapons — Contra Wiki (Fandom)](https://contra.fandom.com/wiki/Weapons), [Rapid Fire — Contra Wiki (Fandom)](https://contra.fandom.com/wiki/Rapid_Fire) — accessed via search 2026-07-19: weapon pickups (Falcon icons) replace the currently held weapon on acquisition; Rapid Fire is a separate, orthogonal fire-rate modifier that does not affect every weapon (the Laser is explicitly unaffected); all held weapon-type progress and Rapid Fire stacking are lost on player death, reverting to the base weapon.
[^2]: [Twilight Princess Upgrades — Zelda Dungeon Wiki](https://www.zeldadungeon.net/wiki/Twilight_Princess_Upgrades), [The Minish Cap tips and tricks — Upgrades — Zelda's Palace](https://www.zeldaspalace.com/theminishcap/upgrades.php) — accessed via search 2026-07-19: bomb-bag/quiver capacity upgrades are bought outright with rupees at a shop for a fixed price and become a permanent equipment-subscreen state, not lost on death or re-purchasable.
[^3]: [How to Power Players Up With Upgrades — Game Wisdom / Game Developer](https://www.gamedeveloper.com/design/how-to-power-up-players-with-upgrades) — accessed via search 2026-07-19: warns against pairing major upgrade axes (health, damage, defense) with marginal ones (ammo capacity, reload/zoom speed) that present false choices with no real gameplay impact; **single-source claim, flagged** — not independently corroborated by a second source in this pass.

## Operational Context

This project's own constraints, already decided at `ADS-002` (not re-litigated here, only cited
as the frame this research must fit): treasure is *spent* to fund the weapon, not merely a
triggering event; there is no ammo/durability concept — a fired weapon never runs out mid-use;
the weapon fires freely once owned (no per-shot cost). `WEAPON_TIER` (`0xC6D9`, `IP-1122`) is
already a single-integer stat, range 1-3 per its own WRAM comment — the existing shape is
structurally closer to the Zelda persistent-purchase model (one axis, incrementally upgraded) than
to Contra's own pickup-drop, multi-weapon-type, full-reset-on-death model. `RUNNING_TREASURE_COUNT`
(`IP-1103`) is the same running currency `inf_heal_spend` (`IP-1123`) already decrements to fund
healing — a second consumer of the identical currency, not a new economy.

Contra's own full-reset-on-death convention would be a poor fit here specifically: this project's
combat sub-mode already committed (`ADS-002`, user decision) to a **non-lethal setback** on zero
health (position reset, not a life/continue system) — there is no "death" event in this game's own
model for a Contra-style full weapon reset to hook into, only a setback that already restores
`PLAYER_HEALTH` to max. Tying weapon-tier loss to that setback would be inventing a new punitive
consequence this project's own Vision (`MSTR-001` C11, non-lethal-by-convention) did not ask for.

## Implementation Guidance

- **Favor the currency-spent, persistent-purchase shape over Contra's pickup-drop/full-reset
  shape.** It is the closer structural fit to `WEAPON_TIER`'s own existing single-integer,
  incrementally-tiered form, and it composes cleanly with this project's own already-decided "no
  death event to reset against" setback model — a future `04-requirements-engineering` delta
  should ground `WEAPON_TIER`'s funding as `inf_heal_spend`'s own sibling: a second `COMBAT_MODE`-
  gated, `RUNNING_TREASURE_COUNT`-decrementing action, capped at `WEAPON_TIER`'s existing max (3),
  never decremented by the post-contact setback.
- **Do not adopt Contra's "new pickup replaces old weapon" model** — it assumes multiple distinct
  weapon *types* (Spread/Laser/etc.), which this project's own `FR-11300` explicitly does not
  have (a single projectile type, `WEAPON_TIER` scaling its damage per `inf_projectile_hittest`'s
  own shipped `health - WEAPON_TIER` subtraction, floored at 0). A single-axis tier increment is
  the correct
  analog to Contra's own separate, orthogonal Rapid Fire modifier, not to its weapon-type-swap
  pickups.
- **Avoid false-choice axes.** `WEAPON_TIER`'s existing single-stat shape already avoids the
  "too many marginal upgrade axes" pitfall — a future spec should resist the temptation to add a
  second/third tunable dimension (fire rate, spread) without a concrete requirement driving it;
  R220 (movement-based directional aiming) is a separate, already-distinct concern and should stay
  that way rather than folding into "weapon upgrades."

## Feature Mapping

`BL-0155` (this research request) — grounded above. `BL-0147` (the `WEAPON_TIER` funding-mechanism
requirement gap) — this topic recommends the currency-spent, persistent-purchase shape (mirroring
`inf_heal_spend`'s own established pattern) as the concrete design a future
`04-requirements-engineering` delta should baseline, rather than Contra's pickup-drop/full-reset
shape, which does not fit this project's own non-lethal-setback model.

## Related Topics

R218 (opt-in combat sub-mode design — this topic extends its weapon axis specifically), R201
(collect-a-thon goal design — treasure's existing role as the base game's core collectible, now
proposed to fund a second consumer alongside healing).
