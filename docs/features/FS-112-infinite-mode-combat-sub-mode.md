# FS-112 — Infinite Mode Combat Sub-Mode

> Feature Specification for [FEAT-11000](../feature-planning/03-feature-catalog.md#feat-11000--infinite-mode-combat-sub-mode-new--not-yet-implemented),
> produced by `06-feature-specification`. Read-only against upstream artifacts — this document
> elaborates FEAT-11000, it does not modify its catalog entry, the requirements it implements, or
> any architecture document.
>
> **Specified 2026-07-17.** This Feature sits in the `Future` release bucket (no release
> commitment made); planning does not require or imply scheduling, per
> `05-feature-decomposition`'s own established precedent (`FEAT-10000`/`FEAT-7100`).
>
> **Planned 2026-07-17** (`07-implementation-planning`) — six packages,
> [IP-1120](../implementation/packages/IP-1120-infinite-mode-combat-mode-gating.md)–[IP-1125](../implementation/packages/IP-1125-combat-sprite-content.md),
> **none authorized.** [IP-1120](../implementation/packages/IP-1120-infinite-mode-combat-mode-gating.md)
> (mode gating & UI, resolving Open Question 1) was initially blocked on a `GDS-01` amendment (a
> genuine architecture gap this planning pass found — `MODE SELECT`'s own architecture text
> stated a closed two-option fact a third option would falsify, mirroring `BL-0113`'s own
> precedent) — routed to `03-architecture-design-synthesis` (`BL-0146`), resolved the same day as
> `GDS-01` §4e (a new `COMBAT MODE CONFIRM` state), and `IP-1120` is now fully planned. The other
> five packages
> ([IP-1121](../implementation/packages/IP-1121-infinite-mode-combat-mob-materialization-and-rendering.md)
> mob materialization/rendering/defeat,
> [IP-1122](../implementation/packages/IP-1122-infinite-mode-combat-weapon-fire-and-hit-resolution.md)
> weapon fire/hit resolution,
> [IP-1123](../implementation/packages/IP-1123-infinite-mode-combat-player-health-and-economy.md)
> player health/setback/healing economy,
> [IP-1124](../implementation/packages/IP-1124-infinite-mode-combat-save-persistence.md) save
> persistence,
> [IP-1125](../implementation/packages/IP-1125-combat-sprite-content.md) sprite content) do not
> depend on the gating mechanism's exact shape and are independently plannable/buildable. Planning
> also surfaced two genuine requirements gaps, harvested to the backlog rather than resolved
> unilaterally: `WEAPON_TIER`'s own treasure-funded upgrade mechanism has no baselined FR
> (`IP-1122` §9); the heal-spend action's own input binding has no free button named upstream
> (`IP-1123` §9) — both routed to `04-requirements-engineering`/`06-feature-specification`.
>
> **`IP-1121` implemented 2026-07-18** — Workflow B (mob materialization, rendering, defeat)
> is built: `COMBAT_MODE`/`MOB_COUNT`/`MOB_DATA` (`asm_game.py`), `inf_materialize_mobs`
> (hooked into `inf_ensure_window`'s existing center-cell recompute), `inf_mob_render` (hooked
> into `update_oam`), `inf_mob_defeat` (defined/exposed, no call site yet — `IP-1122`'s own
> scope). **Independently verified 2026-07-18** ([VR-1121](../implementation/verification/VR-1121-infinite-mode-combat-mob-materialization-and-rendering.md)) — `VERIFIED`.
>
> **`IP-1122` implemented 2026-07-18** — Workflow C (ranged weapon fire and hit resolution) is
> built: `PROJ_ACTIVE`/`PROJ_X`/`PROJ_Y`/`PROJ_DIR`/`WEAPON_TIER` (`asm_game.py`),
> `handle_play_input`'s new A-button fire branch, `inf_projectile_update` (hooked into
> `st_playing`'s per-frame chain), `inf_projectile_hittest` (reuses `check_collisions`' own
> asymmetric point-in-box technique verbatim, unmodified). `COMPLETE`, own
> `09-package-verification` pass owed.
>
> **`IP-1123` implemented 2026-07-18** — Workflow D (player health, non-lethal setback, treasure-
> spent healing economy) is built: `PLAYER_HEALTH`/`COMBAT_ENTRY_X`/`COMBAT_ENTRY_Y`
> (`asm_game.py`), `inf_mob_contact_check` (per-frame, reuses `check_collisions`' own technique
> against `PLAYER_X`/`Y`), `inf_health_setback` (restore-and-reposition, never writes
> `GAMESTATE`), `inf_record_combat_entry` (hooked into every `inf_ensure_window` call site),
> `inf_heal_spend` (defined/exposed, no real input binding yet — `BL-0148`, unresolved),
> `inf_health_hud_draw` (row-1 heart cells, hooked into `update_status_disp`). `COMPLETE`, own
> `09-package-verification` pass owed.
>
> **`IP-1120` implemented 2026-07-18** — Workflow A (the `gate` verb) is built, closing this
> Feature's own **Open Question 1**: a new `GS_COMBAT_MODE_CONFIRM` state (binary Y/N cursor,
> defaults to N) reached only after confirming "infinite" on `MODE SELECT`, before `INFINITE
> SEED ENTRY`; `ms_infinite`'s existing transition retargeted (one constant); `COMBAT_MODE` set
> only on explicit "Y" confirm. **First attempt hit a real ROM-budget overflow (542 bytes,
> `BL-0153`), same class as `BL-0134`** — resolved by a same-day re-plan: the confirm screen
> reuses `mode_select_screen`'s own already-registered tile/attr array as its base and draws its
> own differing text at runtime via `memcpy`, instead of registering a second full `ALL_SCREENS`
> entry. `COMPLETE`, own `09-package-verification` pass owed. This closes all six combat
> sub-mode packages to at least `COMPLETE` — `IP-1121` `VERIFIED`, `IP-1122`/`IP-1123`/`IP-1120`
> `COMPLETE` (own `09` passes owed), `IP-1124` still `NOT STARTED` (blocked on `IP-1122`/
> `IP-1123` reaching `VERIFIED`), `IP-1125` `VERIFIED`.
>
> **Delta 2026-07-19** (`06-feature-specification`) — two new requirements baselined this same
> session, `FR-11210` (mob movement toward the player, `BL-0156`) and `FR-11410` (post-contact
> player protection — invincibility frames + knockback + a per-mob cooldown, combined, per the
> user's own direct decision on `BL-0158`'s live-drive finding), folded into this specification's
> own field set (`05-feature-decomposition` finding #13 already confirmed both belong to
> `FEAT-11000`, no new Feature/FS document). Neither is implemented yet — this delta only
> elaborates their behavior; `07-implementation-planning` is the next stage that would package
> them, still subject to a fresh G3 authorization since they are new scope beyond the original
> "build all six" go-ahead.
>
> **Planned 2026-07-19** (`07-implementation-planning`, same session) — two new packages,
> [IP-1126](../implementation/packages/IP-1126-infinite-mode-combat-mob-movement.md) (mob
> movement, `READY` — sole dependency `IP-1121` already `VERIFIED` — resolves this document's own
> Open Question 4, holds still once coincident with the player) and
> [IP-1127](../implementation/packages/IP-1127-infinite-mode-combat-post-contact-protection.md)
> (post-contact protection, `BLOCKED` on `IP-1123` reaching `VERIFIED`). **Neither authorized** —
> both are new scope beyond the original "build all six" go-ahead and need a fresh, explicit user
> go-ahead before `08-code-implementation` can pick either up.
>
> **`IP-1126` implemented 2026-07-19** — Workflow B step 4 (mob movement) is built:
> `MOB_MOVE_TIMER` (`asm_game.py`), `inf_mob_move` (hooked into `st_playing`'s per-frame chain).
> `COMPLETE`, own `09-package-verification` pass owed.
>
> **Delta 2026-07-19 (second this date, `06-feature-specification`)** — two more new requirements
> baselined this same session, `FR-11310` (movement-based multi-directional weapon fire,
> `BL-0157`, grounded by `ADS-002`'s "Weapon Directionality Delta"/`ADR-0021`/`R220`) and
> `FR-11510` (treasure-spent weapon-tier funding economy, `BL-0147`/`BL-0155`, grounded by `R219`),
> folded into this specification's own field set (`05-feature-decomposition` finding #14 already
> confirmed both belong to `FEAT-11000`, no new Feature/FS document). Neither is implemented yet —
> this delta only elaborates their behavior; `07-implementation-planning` is the next stage that
> would package them, still subject to a fresh G3 authorization.
>
> **Planned 2026-07-19** (`07-implementation-planning`, same session) — two more new packages,
> [IP-1128](../implementation/packages/IP-1128-infinite-mode-combat-weapon-directionality.md)
> (weapon directionality, `READY` — sole dependency `IP-1122` already `VERIFIED`) and
> [IP-1129](../implementation/packages/IP-1129-infinite-mode-combat-weapon-tier-funding.md)
> (weapon-tier funding, `READY` — both dependencies `IP-1122`/`IP-1103` already `VERIFIED`).
> **Neither authorized** — both new scope beyond the original "build all six" go-ahead, same class
> as `IP-1126`/`IP-1127`. `IP-1128` repurposes `PROJ_DIR` in place (renamed `PROJ_STEP_X`) and
> shares a named, unresolved WRAM-address collision with `IP-1127`'s own still-`BLOCKED`
> prospective claim.
>
> **`IP-1124` implemented 2026-07-19** — Workflow E (combat state save persistence, `FR-11600`)
> is built, closing this Feature's own critical path: new SRAM `SRAM_COMBAT_MODE`/
> `SRAM_MOB_COUNT`/`SRAM_MOB_DATA`/`SRAM_WEAPON_TIER`/`SRAM_PLAYER_HEALTH` (`0xA350`–`0xA371`,
> `asm_game.py`); `SAVE_VERSION_VAL` bumped `0x05`→`0x06`; `save_to_sram`/`try_load_save` both
> extended inside their existing MBC1-enable bracket. `PROJ_*` fields deliberately not persisted.
> **Two corrections found and fixed during implementation, not silently patched over:** (1) the
> package's own §6 described the five persisted WRAM fields as one 34-byte contiguous span —
> direct code read confirmed they are not (`PROJ_ACTIVE`/`PROJ_X`/`PROJ_Y`/`PROJ_STEP_X`,
> `IP-1122`/`IP-1128`, sit between `MOB_DATA`'s own end and `WEAPON_TIER`) — implemented as two
> separate transfers instead of one, preserving the exact same SRAM layout and exclusion of the
> transient projectile fields the package intended; (2) `try_load_save`'s own combat-state restore
> had to be sequenced *after* the existing `inf_ensure_window` call (not before, as first drafted)
> since that call's own center-cell recompute unconditionally invokes `inf_materialize_mobs`,
> which — once `COMBAT_MODE` is restored — would otherwise immediately overwrite the just-restored
> `MOB_DATA`/`MOB_COUNT` with a freshly re-materialized set; `COMBAT_MODE` is restored between
> `inf_ensure_window` and `inf_record_combat_entry`, so the latter still correctly records the
> restored position as the new combat-entry point. New suite `T32` (4 checks, incl. a real
> two-instance save/load round trip). **393/393 suite passes.** `COMPLETE`, own
> `09-package-verification` pass owed.
>
> **`IP-1127` authorized and implemented 2026-07-19, same session** (G3, user "Yes, authorize
> IP-1127," asked once `IP-1123` reached `VERIFIED`) — Workflow D step 2's own delta (post-contact
> player protection, `FR-11410`/`BL-0158`) is built: new `PLAYER_INVINCIBLE`/`MOB_CONTACT_FLAGS`
> (`0xC6E2`–`0xC6E3`, `asm_game.py` — re-derived at build time past `IP-1128`'s own real claim of
> the package's originally-planned `0xC6DF`–`0xC6E0`, closing `BL-0163`). `inf_mob_contact_check`
> (`IP-1123`) extended with a per-mob cooldown bit carried alongside its existing per-slot loop
> index; new `inf_invincibility_tick` hooked into `st_playing`'s per-frame chain. **Found-and-fixed
> interaction, named explicitly:** a lethal hit (triggering `inf_health_setback`) skips knockback
> on that one path — applying it against the pre-setback position would have silently displaced
> the player off the setback's own just-restored region-entry point. **Two test-only bugs found and
> fixed during authoring, not product defects:** several `T36` checks first read state after
> knockback had already (correctly) separated the player from the mob, so a same-position follow-up
> mob placement no longer overlapped — fixed by re-pinning the player's own test position between
> invocations where the check's own intent requires genuinely continued overlap. New suite `T36`
> (12 checks incl. a live PyBoy drive, `T36.j`). **404/404 suite passes.** ROM builds at exactly
> 32768 bytes (32670 used, 98 bytes headroom — the tightest margin of any package in this
> tranche). `COMPLETE`, own `09-package-verification` pass owed. **This closes every package in
> the Infinite Mode Combat Sub-Mode delta (`IP-1120`–`IP-1129`) to at least `COMPLETE`.**

[↑ Features index](INDEX.md) · [Feature Catalog](../feature-planning/03-feature-catalog.md) ·
[Epic Catalog](../feature-planning/02-epic-catalog.md)

## 1. Feature ID

`FS-112` — expands `FEAT-11000` (Infinite Mode Combat Sub-Mode), Epic `EP-6000` (Infinite Mode).

## 2. Title

Infinite Mode Combat Sub-Mode

## 3. Purpose

Offer a distinct, explicitly opt-in combat layer inside Infinite Mode — mobs, ranged weapon fire,
player health, a treasure-spent healing economy — for the dual-audience carve-out `MSTR-001` C11
names, without touching the base child-friendly Infinite Mode or finite mode at all. Carried
forward verbatim from FEAT-11000's own Purpose/User Value (Medium-High — directly answers a real
Vision-level commitment, `MSTR-001` C11, rather than exploratory scope).

## 4. Scope

**In scope:** a third, explicitly-labeled MODE SELECT option gating the sub-mode on for a save's
entire life; per-region mob materialization/defeat, drawn as a pure function of `(seed, row, col)`
independent of the region's own biome/treasure draws; a single-slot ranged projectile fired on
player input, resolved against mob hitboxes; player health tracked and displayed via the existing
heart-tile art, with a non-lethal setback on reaching zero; a treasure-spent healing economy that
decrements the same `RUNNING_TREASURE_COUNT` `FEAT-10000`'s own win/high-score logic reads; combat
state (mob state, weapon tier, player health) persisted across save/load via a new
`SAVE_VERSION_VAL` bump.

**Out of scope** (per FEAT-11000's own Excluded Requirements, carried forward verbatim):
`FEAT-10000`'s own base Infinite Mode capability (mode entry, streaming generation, treasure
placement, the base win condition, save/load) — none of its leaves are amended by this Feature,
per `ADS-002`'s own Open Question 5 confirming this capability is additive and
Infinite-Mode-exclusive; the entire finite mode (`FEAT-9000`/`FEAT-4100`/`FEAT-5300`), confirmed
unaffected by the same Open Question.

**Scope note carried from FEAT-11000's own catalog entry:** this Feature is deliberately kept as
one cohesive unit (gating, mob materialization/defeat, weapon fire/hit resolution, player
health/setback, the healing economy, save persistence) rather than pre-split by concern, since
nothing has been implemented yet to reveal a clean seam — mirroring how `FEAT-10000` itself
started unsplit. A future `05-feature-decomposition` pass may split it once implementation detail
is known (e.g. mob AI vs. weapon/hit-resolution vs. HUD).

## 5. Requirements Implemented

FR-11100, FR-11200, FR-11210, FR-11300, FR-11310, FR-11400, FR-11410, FR-11500, FR-11510,
FR-11600; NFR-1500, NFR-4500 — the exact set FEAT-11000 owns, no more, no fewer (cross-checked
against
[03-feature-catalog.md](../feature-planning/03-feature-catalog.md#feat-11000--infinite-mode-combat-sub-mode-new--not-yet-implemented)'s
Included Requirements, now 12 IDs following the 2026-07-19 deltas that added `FR-11210`/`FR-11410`
and, later the same date, `FR-11310`/`FR-11510`).

## 6. User Workflows

**Workflow A — Combat sub-mode entry** (FR-11100):

1. Player reaches new-game creation and chooses Infinite Mode (the existing `GS_MODE_SELECT`
   entry point, `FS-110` Workflow A).
2. Before or immediately after committing to Infinite Mode, the player is offered a third,
   distinctly-labeled choice (e.g. "COMBAT MODE") — never defaulted on, never reachable by any
   path a player could enter unintentionally (`ADS-002` §System Architecture, Gating Mechanism).
3. The chosen `COMBAT_MODE` state is recorded for the new save and fixed for that save's entire
   life, mirroring `FR-9110`/`FR-10100`'s own established immutability precedent.
4. Control passes to Workflow B for the player's starting region, now with combat active.

**Workflow B — Mob materialization and defeat** (FR-11200):

1. When a region materializes (`FS-110`'s existing `inf_ensure_window` hook, Workflow B step 2)
   and `COMBAT_MODE` is active, the system draws mob presence/type as a pure function of
   `(SEED, row, col)`, via its own sequential `gw_prng_step` reseed call in the same per-region
   reseed chain treasure-presence already uses — independent of and uncorrelated with that
   region's own biome/treasure draws (`ADS-002` §System Architecture, Mob spawning).
2. Up to six mobs may be concurrently active (an adjustable default, not a hard ceiling this
   Feature fixes).
3. When the player defeats a mob (Workflow C), it disappears via a brief, non-graphic
   presentation sequence (mirroring how a collected `ScoreItem` already deactivates today) — no
   persistent corpse sprite.
4. **(FR-11210, delta 2026-07-19)** Once materialized, each active mob periodically recomputes a
   single grid-aligned step toward the player's current position — a step's distance and the
   number of frames between recomputations are both independently adjustable defaults, mirroring
   §6 Workflow C step 2's own "adjustable default" framing for the projectile cap. A mob
   materialized with `COMBAT_MODE` inactive never moves (§7 edge case, `FR-11200`'s own strict-
   additivity guarantee unweakened).
5. Re-materializing the same region with the same seed reproduces identical mob
   presence/type/position at the moment of materialization; a region materialized with
   `COMBAT_MODE` inactive shows zero mobs and is otherwise byte-for-byte identical to today's
   shipped Infinite Mode. (Movement per step 4 is deterministic given the mob's own position
   history and the player's position at each recomputation — not itself part of the
   materialization-determinism guarantee, which concerns only the mob's initial spawn state.)

**Workflow C — Ranged weapon fire and hit resolution** (FR-11300):

1. During `PLAYING` with `COMBAT_MODE` active, the player presses the fire input — the A button,
   confirmed unbound during gameplay today by direct code read of `handle_play_input`/
   `st_playing` (`ADS-002` §System Architecture).
2. If no projectile is currently active, one spawns from the player's own position in the
   player's current facing direction; if one is already active, the new press has no additional
   effect until the active one terminates (at most one projectile in flight at a time, an
   adjustable default).
3. Each frame, the active projectile moves; if it reaches an active mob's hitbox (a point-in-box
   test reusing `check_collisions`' own established asymmetric-tolerance technique, per `R115`),
   that mob's health is reduced (defeated at zero, Workflow B step 3) and the projectile
   deactivates; if it instead reaches a terminal boundary (window/screen edge) without a hit, it
   deactivates without effect.
4. **(FR-11310, delta 2026-07-19, second this date)** The projectile's own firing direction (step
   2) is derived from the player's own movement across all eight compass directions, not left/right
   only — the player's current movement direction while moving, or their last movement direction
   while idle (`ADS-002`'s "Weapon Directionality Delta"/`ADR-0021`, grounded by `R220`'s
   Link's-Awakening-derived recommendation). A projectile fired on a diagonal facing moves along
   both axes simultaneously (step 3's own per-frame movement, extended to two axes at once —
   `ADR-0021`'s own single-axis-integer-stepping idiom applied to both axes, not vector motion). A
   new, separate facing concept carries this — the player's own existing 2-value `PLAYER_DIR`
   (left/right, driving the sprite's X-flip render) is untouched, per `ADR-0021`'s own Decision 1.

**Workflow D — Player health, setback, and the healing economy** (FR-11400, FR-11410, FR-11500):

1. Mob contact/attack reduces the player's health value, displayed via a persistent HUD element
   reusing the already-shipped `TL_HEART_FULL`/`TL_HEART_EMPTY` tiles (`tiles.py`) — zero new art
   cost.
2. **(FR-11410, delta 2026-07-19)** Immediately following a contact-damage event, three
   mechanisms combine, per the user's own direct decision on `BL-0158`'s finding (a live-drive
   investigation that found sustained contact re-triggered step 1 every single frame, resolving a
   full health-loss-and-setback cycle in 3-4 real frames — too fast to perceive, so the mechanic
   was effectively invisible):
   a. **Invincibility** — for an adjustable-default duration, the player takes no further contact
      damage from *any* mob, regardless of continued overlap.
   b. **Knockback** — the player is displaced an adjustable-default distance away from the
      triggering mob, along whichever grid axis separates them fastest (mirrors Workflow B step
      4's own grid-aligned movement model).
   c. **Per-mob cooldown** — independent of and outlasting (a) and (b), the *specific* mob that
      caused the contact cannot cause another contact-damage event against the player until
      overlap between them has genuinely broken and then resumed — a floor guarantee against the
      exact repeated-single-frame-overlap failure mode `BL-0158` found, regardless of whether (a)
      or (b) alone would have been sufficient in a given encounter.
3. The player may choose to spend collected treasure (`RUNNING_TREASURE_COUNT`, the same count
   `FS-110` Workflow C reads for the win/high-score comparison) to restore health — spending
   decrements that same count; no second, independent ledger is created.
3a. **(FR-11510, delta 2026-07-19, second this date)** The player may, independently of step 3,
    choose to spend the same `RUNNING_TREASURE_COUNT` to permanently increase `WEAPON_TIER` by
    one, up to its own existing maximum — a sibling spend action sharing step 3's own currency,
    not a second ledger. Spending at the maximum tier still decrements `RUNNING_TREASURE_COUNT`,
    just does not push `WEAPON_TIER` past its own cap — mirroring step 3's own shipped, tested
    spend-at-max-health precedent exactly (`T31.d2`: the treasure is still spent, not a no-op).
    Per `R219`'s grounded recommendation, a purchased tier increase is permanent — not decremented
    by step 4's own setback or any other event, mirroring step 3's own healing-spend permanence.
4. If player health reaches zero, a non-lethal setback triggers (e.g. returning the player to the
   last region entered, with treasure/health partially restored) — never a `GAMESTATE` transition
   to a game-over state, consistent with `MSTR-001` A5's fail-state-free base design holding
   inside `C11`'s own carve-out. The run continues in `PLAYING` afterward.

**Workflow E — Combat state save persistence** (FR-11600):

1. On a save-confirm or exit-to-main-menu action (the same trigger `FS-110` Workflow D uses), if
   `COMBAT_MODE` is active, the system additionally writes mob state, weapon tier, and player
   health to SRAM under a new `SAVE_VERSION_VAL` bump (mirroring `IP-1010`/`IP-1050`/`IP-1104`'s
   own established version-byte pattern).
2. On load, this state is restored exactly as it was at save time; a pre-combat-mode save (an
   older `SAVE_VERSION_VAL`) loads cleanly without it, mirroring `FS-110`'s own version-guard
   precedent for pre-Infinite-Mode saves.

## 7. System Behaviour

**Normal path (mob materialization):** given any `(SEED, row, col)` and `COMBAT_MODE` active, the
mob-presence draw terminates having produced mob presence/type/position that are a pure function
of those inputs alone — no dependency on generation order, treasure/biome draw order, or any
other region's own history (mirrors `FS-110`'s own `NFR-2300` positional-determinism framing,
extended to mobs).

**Edge case — `COMBAT_MODE` inactive:** a materialized region shows zero mobs and is byte-for-byte
identical to today's shipped Infinite Mode — this capability is additive by construction, not a
fork of the generation algorithm (`ADS-002` §System Architecture).

**Edge case — firing while a projectile is already active:** the fire input has no additional
effect (§6 Workflow C step 2) — not queued, not an error, simply a no-op until the active
projectile terminates.

**Edge case — a mob and the healing economy interacting in the same frame (taking damage while
spending treasure to heal):** not yet defined — whether damage and a heal-spend can resolve in
the same frame, and in what order, is genuinely undecided (Open Question 3).

**Edge case — an already-adjacent/overlapping mob's own movement recomputation (delta
2026-07-19, `FR-11210`).** **Resolved (`IP-1126`, 2026-07-19):** a mob exactly coincident with
the player (`dx == 0` and `dy == 0`) holds still rather than re-attempting a further step each
interval — no visual jitter (Open Question 4, `T35.e`).

**Edge case — invincibility/knockback/cooldown interacting with mob movement (delta 2026-07-19,
`FR-11210`/`FR-11410`):** during the post-contact invincibility window, a moving mob (Workflow B
step 4) may continue advancing toward the player's now-knocked-back position — whether the
mob's own movement should pause during the player's invincibility window, or continue
unconditionally (simply failing to land a second hit because invincibility/cooldown block it
regardless of proximity), is not decided here; either satisfies `FR-11410`'s own Acceptance
Criteria as written, so this remains named but not resolved, owed to `IP-1127`. This is a
distinct condition from the coincident-jitter case just above (mere contact-box adjacency/overlap
is not the same as `dx==0, dy==0` exact coincidence), so `IP-1126`'s own resolution above does not
settle it.

**Edge case — player health reaching zero while treasure remains unspent:** the setback (§6
Workflow D step 3) fires regardless of remaining treasure — treasure is a player *choice* to
spend proactively, not an automatic save-from-death mechanic, per the user's own "spent," not
"triggers," economy decision (`ADS-002` Open Question 2).

**Edge case — a single frame where both region materialization and mob AI/projectile logic must
run:** whether this coincidence is reachable, and if so its combined cycle cost against
`NFR-1400`'s own already-`NOT MET` overage, is explicitly `UNCONFIRMED` (NFR-1500) — no
implementation exists yet to measure it.

## 8. Module Responsibilities

Per GDS-03's module decomposition, extended by `ADS-002`'s own module framing (no new module):

- **`asm_game.py`** — the mob-presence/type draw (hooked into `inf_ensure_window`'s existing
  per-region materialization), mob movement/AI/defeat logic (**delta 2026-07-19**: movement
  toward the player, `FR-11210`, is now a concrete named behavior here, not just the generic "AI"
  placeholder this field originally carried), the fire-input handler and projectile-update
  routine, **a movement-direction decode feeding the projectile's own firing direction (delta
  2026-07-19, second this date, `FR-11310`)**, player-health tracking and the non-lethal setback,
  **post-contact protection — invincibility/knockback/per-mob-cooldown (delta 2026-07-19,
  `FR-11410`)**, the treasure-spend healing subroutine, **a sibling treasure-spend weapon-tier
  subroutine (delta 2026-07-19, second this date, `FR-11510`)**, the MODE SELECT gating extension
  (`GS_MODE_SELECT`), the health HUD write, and the save-write/load-restore extension. None of
  this code exists yet.
- **`worldgen.py`** (prospective) — the Python reference-generator-oracle mirror for the
  mob-presence draw, per `ADS-002`'s own reseed-chain discipline, mirroring `FS-110`'s own
  identical obligation for its per-region routine.
- **`tiles.py`** — the already-shipped `TL_HEART_FULL`/`TL_HEART_EMPTY` tiles this Feature's
  health HUD reuses verbatim. **This Feature does not add any new tile art for the health HUD**
  — a genuinely new mob/projectile sprite is the only new tile-art need, and its exact pixel
  content is `08-content-authoring`'s own scope, not decided here.

No module outside this set is touched.

## 9. Interfaces Used

- **`inf_ensure_window`'s existing per-region materialization hook** (`FS-110`, unchanged) — this
  Feature's mob-presence draw extends the same reseed chain treasure-presence already uses,
  consumed not redefined.
- **`gw_prng_step`'s existing shift/XOR-only construction** (R111/R113, unchanged) — reused for
  the mob-presence draw's own sequential reseed call, per `ADS-002`'s own no-correlation
  discipline. This Feature does not modify `gw_prng_step` itself.
- **`check_collisions`' existing asymmetric point-in-box technique** (`IP-9100`/`BL-0053`,
  unchanged) — reused verbatim for projectile-vs-mob hit-testing, per `R115`'s own explicit
  recommendation. No new hitbox model.
- **`handle_play_input`/`st_playing`'s existing input-dispatch surface** — the A button is
  confirmed unbound during `PLAYING` today (direct code read, `ADS-002`); this Feature adds a new
  branch for it, not a rebinding of any button already claimed elsewhere.
- **`RUNNING_TREASURE_COUNT`'s existing read/write surface** (`FS-110` Workflow C, unchanged) —
  this Feature's healing economy decrements the same count the win/high-score comparison reads;
  no second ledger, no new interface.
- **The existing `GS_MODE_SELECT` state / MODE SELECT UI** (`FS-110` Workflow A, `IP-1100`) —
  this Feature's gating choice (Workflow A) extends this same screen with a third option. **The
  exact UI mechanic (a three-state `MM_CURSOR` cycle vs. a follow-up confirmation screen shown
  only after choosing Infinite Mode) is not decided by this specification** — flagged as Open
  Question 1.
- **A new save-format version value** (mirroring `FS-110`'s own `SAVE_VERSION_VAL` precedent) —
  this Feature's combat state needed its own version discriminator; **implemented by `IP-1124`
  (2026-07-19, Workflow E): `SAVE_VERSION_VAL` bumped `0x05`→`0x06`**, confirming the predicted
  next value in the established strictly-monotonic sequence, exactly as `FS-110`'s own identical
  framing anticipated for its own version bump (Open Question 7 there, now resolved).
- **The player's own existing grid-aligned movement model** (**delta 2026-07-19**, `handle_play_
  input`'s existing single-axis-step-per-frame pattern, unchanged) — `FR-11210`'s mob movement
  and `FR-11410`'s knockback both reuse the same step shape (one axis at a time, whole-tile-
  agnostic pixel steps) rather than inventing free-angle or sub-pixel motion, per each FR's own
  explicit framing. This Feature does not modify the player's own movement handling itself.
- **`PLAYER_DIR`'s existing 2-value (left/right) shape** (**delta 2026-07-19, second this date**,
  unchanged) — `FR-11310`'s own facing concept is a new, separate WRAM field, not a widened
  `PLAYER_DIR` (`ADR-0021`'s own Decision 1); `PLAYER_DIR` and its sole non-copy consumer (the
  OAM X-flip render) are consumed, not redefined, by this Feature.
- **`RUNNING_TREASURE_COUNT`'s existing read/write surface** (as above) — **delta 2026-07-19,
  second this date**: `FR-11510`'s weapon-tier funding is a second, sibling consumer of this same
  interface, alongside `FR-11500`'s healing spend — no new interface, no second ledger.

## 10. Data Model Changes

**No `GDS-04`/`GDS-07`/`GDS-09` delta has been authored for the combat sub-mode** — like `FS-110`
before it, this specification has no proposed WRAM/SRAM address table to cite, only the
conceptual entities `ADS-002`'s own Domain Model already names:

- **`Mob`** — position (x, y), type/species (1 byte, room for multiple species per `R218`'s own
  variety-within-tone framing), health (1 byte), active flag. A fixed-size table, six concurrent
  slots (an adjustable default, `ADS-002`/`R115`), mirroring `COLL_DATA`/`COLL_COUNT`'s own
  established shape. No eviction/FIFO scheme needed — mobs are session-local per materialized
  region, not an ever-growing history. **Delta 2026-07-19 (`FR-11210`):** movement toward the
  player requires the routine to read the mob's own current position each recomputation interval
  — no additional persistent per-mob field is implied by movement itself (the existing x/y pair
  is simply written more than once now, not read-only after materialization as originally
  described); a shared, non-per-mob recomputation-interval counter is a plausible implementation
  shape but not fixed here (`07`'s own act).
- **`Projectile`** — origin, direction, active flag — a single transient WRAM record, mirroring
  `INF_MZ_RESULT`'s own "transient, generation-time-only, never persisted" precedent. A design
  needing more than one in-flight projectile is a future extension, not this Feature's own
  default.
- **`PlayerHealth`** — a new player-state field; today the player has no health/damage concept at
  all (`check_collisions` only ever adds to score/treasure counts). Presented via the reused
  heart-tile HUD. **Delta 2026-07-19 (`FR-11410`):** post-contact protection implies at least two
  further pieces of transient state — an invincibility-window countdown (global, not per-mob) and
  a per-mob "still in unbroken contact" flag or equivalent (to detect the overlap-must-break-then-
  resume condition the per-mob cooldown requires) — neither named as a specific WRAM field here,
  since the exact shape (a per-mob bit in the existing `Mob` table vs. a separate small table) is
  `07-implementation-planning`'s own data-model act, not decided at this specification level.
- **`Weapon`** — a stat model with at least one upgrade-tier axis, funded by treasure; explicitly
  no ammo/durability field, per the user's own decision (`ADS-002` Open Question 3). **Delta
  2026-07-19 (second this date, `FR-11510`):** the funding mechanism itself is now named —
  treasure-spent, persistent-purchase (`R219`'s grounded recommendation) — no new WRAM field is
  implied beyond `WEAPON_TIER` itself (already shipped, `IP-1122`); this Feature adds the
  spend-action logic that changes its value, not a new data field.
- **`COMBAT_MODE`** — a new 1-byte WRAM flag, valid only alongside `GAME_MODE=1` (Infinite Mode).
- **`PlayerFacing`** (**delta 2026-07-19, second this date, `FR-11310`**) — a new, separate
  player-state field carrying an 8-directional facing value, distinct from the existing
  `PLAYER_DIR` (2-value, left/right, driving the sprite's X-flip render — untouched, `ADR-0021`'s
  own Decision 1). Feeds the projectile's own firing direction (Workflow C). The exact bit
  encoding and WRAM address are not fixed here — `07-implementation-planning`'s own act
  (`ADR-0021`'s own explicit "not decided at the architecture level" scope).

**SRAM additions** are this Feature's own scope (mirroring `FS-110`'s own identical framing) —
Workflow E's mob-state/weapon-tier/player-health fields are written directly by this Feature's
own save/load routine, since no separate save-persistence Feature exists for this capability in
the current catalog.

## 11. State Changes

- **Whether the combat sub-mode's own gating choice introduces a new `GameState` value is not
  decided by this Feature** — depends entirely on Open Question 1's own resolution (a new
  confirmation-screen state vs. an in-place `MM_CURSOR` extension). If the chosen shape reuses
  `GS_MODE_SELECT` itself (a three-state cursor), no new state is needed; if it needs a dedicated
  confirmation screen, a new state is implied, mirroring `FEAT-1200`'s/`FS-110`'s own precedent
  for a genuinely new screen.
- **No new state is introduced for gameplay itself** — combat's own weapon-fire/mob-AI behavior
  reuses the existing `PLAYING` state; this Feature changes what happens *within* that state, not
  the state machine's own node set for play itself.
- **Runtime state created:** the mob table, the projectile record, and player health, persisting
  for the life of the play session and, via Workflow E, across save/reload.

## 12. Error Handling

- **Invalid mode-selection input:** out of this Feature's own scope — the same input-validation
  discipline `FS-110`/`FEAT-1100` already establish for the MODE SELECT screen applies identically
  here (Workflow A).
- **A mob-presence/type draw producing an invalid value:** not a runtime failure mode this
  Feature handles defensively — the positional-determinism guarantee is enforced by construction
  (the reseed-and-clamp computation), not checked and recovered from after the fact, mirroring
  `FS-110`'s own identical framing for its own generator-guaranteed properties.
- **Firing with no mob in range:** not an error — the projectile simply reaches its terminal
  boundary and deactivates without effect (§7 edge case).
- **Spending treasure to heal with `RUNNING_TREASURE_COUNT` at zero:** the heal-spend action has
  no effect (FR-11500's own Precondition, `RUNNING_TREASURE_COUNT > 0`) — not a crash or an
  underflow; the exact player-visible feedback (a no-op vs. a disabled-menu-option cue) is
  **Open Question 3** (found mis-cited as "Open Question 4" here prior to this delta — corrected
  in the same pass as adding the genuinely new Open Question 4 below, to avoid a duplicate
  number; §19's own Open Question 3 already resolved this as a silent no-op, `IP-1123`/`T31.e`).
- **A pre-combat-mode save loaded after this Feature ships:** mirrors `FS-110`'s own
  version-guard precedent (a version-mismatched-for-this-field save simply lacks the combat
  fields, not offered garbage data) — the exact version value is not fixed here (§9).
- **Spending treasure to upgrade the weapon with `RUNNING_TREASURE_COUNT` at zero (delta
  2026-07-19, second this date):** the tier-spend action has no effect (FR-11510's own
  Precondition) — not a crash or an underflow, mirroring the existing heal-spend-at-zero-treasure
  precedent immediately above. **Spending with `WEAPON_TIER` already at its own maximum:** unlike
  the zero-treasure case, this is *not* a no-op — `RUNNING_TREASURE_COUNT` still decreases by the
  spent amount, mirroring `FR-11500`'s own shipped, tested spend-at-max-health precedent exactly
  (`T31.d2`); only the tier increase itself is floored at the maximum.

## 13. Performance Considerations

- **NFR-1500** (combat sub-mode per-frame cycle budget, `UNCONFIRMED`): whether mob AI tick,
  projectile update, and hit-test logic fit inside the existing per-frame budget — and, critically,
  whether a frame where combat logic and region materialization coincide would compound
  `NFR-1400`'s own already-`NOT MET` overage — is not confirmed by any evidence this specification
  can cite. `R115` names the risk directly but does not treat it as settled. This Feature's own
  Acceptance Criteria (§15) states the bar; it does not claim compliance. **Delta 2026-07-19:**
  `FR-11210`'s per-mob movement recomputation and `FR-11410`'s per-mob cooldown-state check both
  add real, unmeasured per-frame cost on top of the pieces already named here — `NFR-1500`'s own
  text was updated at the requirements stage to name both explicitly as inheriting its existing
  measurement obligation, not a new/separate NFR. **Delta 2026-07-19 (second this date):**
  `FR-11310`'s own movement-direction decode (`handle_play_input`) and second per-frame
  projectile axis step (`inf_projectile_update`), plus `FR-11510`'s own spend-check cost, add
  further unmeasured cost on the same still-`UNCONFIRMED` surface — `NFR-1500`'s own text updated
  again to name both.
- **NFR-4500** (ROM/OAM budget): `R115`'s own direct measurement (post-`IP-9170`/`IP-9180`) found
  1,378 bytes of ROM headroom and 31 of 40 shadow-OAM entries free (9 used: 1 player + up to 8
  collectibles). The 6-mob-slot default (7 new entries including the projectile) leaves 24 free —
  favorable, but not yet confirmed against a real implementation's actual footprint.

## 14. Integrity Considerations

- **Positional determinism** (mirrors `FS-110`'s own `NFR-2300` framing, extended to mobs): the
  mob-presence draw's output must be a pure function of `(SEED, row, col)` alone — no read of
  `DIV`, uninitialized WRAM, generation order, or any other history-dependent input.
- **Save round-trip integrity** (FR-11600): mob state, weapon tier, and player health must
  restore exactly on load; the version-guard must reject a pre-combat-mode save's own combat
  fields as absent rather than reading garbage bytes as valid state.
- **The SM83 mob-presence routine and its `worldgen.py` oracle mirror must be kept in lockstep by
  direct correspondence** (same reseed construction), mirroring `ADR-0018`'s/`FS-110`'s own
  identical discipline — named here as a standing implementation obligation, not itself enforced
  by this specification.

## 15. Acceptance Criteria

**AC numbering renumbered 2026-07-19 (second delta this date)** to insert two more criteria
(`FR-11310`/`FR-11510`) in requirement order, mirroring the same renumbering discipline already
applied once this date for `FR-11210`/`FR-11410`:

1. The combat sub-mode is never enabled by default and is never reachable via any path a player
   could enter unintentionally; once chosen, it is fixed for that save's life (FR-11100).
2. For a corpus of `(SEED, row, col)` triples with `COMBAT_MODE` active, materializing the same
   region twice produces byte-identical mob presence/type/position both times; the same region
   materialized with `COMBAT_MODE` inactive shows zero mobs and is otherwise unaffected (FR-11200).
3. With `COMBAT_MODE` active, an active mob's own recorded position
   changes over successive recomputation intervals such that its distance to the player strictly
   decreases (absent an intervening defeat or reaching the player's own position); the distance
   moved per recomputation and the frame interval between recomputations both match their
   configured adjustable-default values exactly; with `COMBAT_MODE` inactive, mob position is
   never read or written by this logic at all (FR-11210).
4. Firing while no projectile is active spawns one; firing while one is already active has no
   additional effect; a projectile that reaches an active mob's hitbox reduces its health and
   deactivates; a projectile that reaches a terminal boundary without a hit deactivates without
   effect (FR-11300).
5. **(delta 2026-07-19, second this date)** Firing while moving in a cardinal direction spawns a
   projectile that moves along that single axis only; firing while moving diagonally spawns a
   projectile that moves along both axes simultaneously; firing while stationary uses the most
   recently held movement direction, not a fixed default; every one of the eight compass
   directions is reachable (FR-11310).
6. Player health decreases on mob contact/attack, reflected in the HUD within a frame budget
   mirroring the existing HUD-update timing; reaching zero health triggers the defined setback
   and the run continues in `PLAYING`, never a game-over state (FR-11400).
7. A contact-damage event followed immediately by continued overlap with
   the same mob produces exactly one health decrement, not a cascading repeat; the player's
   position changes by the configured knockback distance in the expected direction immediately
   following a contact-damage event; no contact-damage event of any kind registers for the
   configured invincibility-frame duration after the prior one; the specific mob that caused a
   contact event causes no further contact damage until the player's hitbox has first stopped,
   then resumed, overlapping it — verified independently of whether the invincibility window has
   already elapsed (FR-11410).
8. Spending treasure to heal reduces `RUNNING_TREASURE_COUNT` by exactly the spent amount; the
   same count is what the win/high-score comparison reads at run's end — no separate ledger
   exists (FR-11500).
9. **(delta 2026-07-19, second this date)** Spending treasure to upgrade the weapon reduces
   `RUNNING_TREASURE_COUNT` by exactly the spent amount and increases `WEAPON_TIER` by exactly 1,
   up to but never past its own maximum; spending at the maximum tier still reduces
   `RUNNING_TREASURE_COUNT` by the spent amount but does not push `WEAPON_TIER` past its cap,
   mirroring AC-8's own heal-at-max-health precedent exactly (not itself a no-op); the same
   `RUNNING_TREASURE_COUNT` is spent from — no separate ledger; a purchased tier increase survives
   a mob-contact setback and a save/load round trip unchanged (FR-11510).
10. A save/load round trip reproduces identical mob state, weapon tier, and player health; a
    pre-combat-mode save loads cleanly without this state (FR-11600).
11. Static inspection of the mob-presence draw finds no read of `DIV` or any WRAM address not
    explicitly derived from `SEED`/`(row, col)` (mirrors NFR-2300's own audit shape).
12. **Not yet a checkable criterion** — NFR-1500's cycle-budget bar has no fixed numeric target to
    check against until an implementation exists to measure it; this specification names the bar
    (§13) without asserting compliance. The bar now also covers `FR-11210`'s
    movement-recomputation cost, `FR-11410`'s cooldown-state-check cost, `FR-11310`'s
    direction-decode and second-axis-step cost, and `FR-11510`'s spend-check cost, per NFR-1500's
    own updated text — still not measurable until an implementation exists.

## 16. Verification Plan

Per FR-11100–11600's own Verification Methods (Test) and NFR-1500 (Analysis) / NFR-4500
(Inspection, once implemented) — no `test_rom.py` suite exists yet for this Feature (no code
exists to test). **AC numbering renumbered 2026-07-19 (second delta this date)** to insert two
more criteria (`FR-11310`/`FR-11510`) in requirement order:

- **Combat sub-mode entry (AC-1):** drive the MODE SELECT flow once Open Question 1 resolves a
  concrete UI shape; confirm the sub-mode is off by default and fixed once chosen.
- **Mob materialization determinism (AC-2):** property test across a `(SEED, row, col)` corpus,
  mirroring `FS-110`'s own T22/T24 determinism-test shape (fresh-instance comparison plus
  oracle-vs-SM83 comparison), extended to mob presence/type/position.
- **Mob movement toward the player (AC-3):** direct-force position/distance
  assertions across multiple recomputation intervals (mirroring the property-test discipline
  `FS-110`'s own T22 already established where a deterministic mirror is feasible); a live PyBoy
  drive through the real per-frame chain, mirroring the independent-verification discipline
  `VR-1121`/`VR-1122` already established for this Feature, to confirm the real production call
  path (not just a direct-invoke harness) moves mobs correctly.
- **Weapon fire/hit resolution (AC-4):** direct-force integration checks mirroring `IP-9100`'s
  own established hitbox-test methodology — force a mob into range, fire, confirm health
  reduction and projectile deactivation; force a miss, confirm clean deactivation without effect.
- **Weapon directionality (AC-5, delta 2026-07-19, second this date):** direct-force
  facing/movement scenarios across all eight compass directions, mirroring AC-4's own hit/miss
  test methodology; a live PyBoy drive through the real per-frame chain for at least one
  non-cardinal (diagonal) case, mirroring `VR-1121`/`VR-1122`/`T35.i`'s own established
  independent-verification discipline.
- **Player health/setback (AC-6):** direct-force integration checks — force mob contact, confirm
  HUD reflects the reduction; force health to zero, confirm the setback fires and `GAMESTATE`
  remains `PLAYING`.
- **Post-contact protection (AC-7):** the exact `BL-0158` live-drive repro
  (sustained overlap via held input, or a stationary player with an adjacent mob once `FR-11210`
  ships) re-run against the fixed behavior, confirming exactly one decrement rather than a
  cascade; direct-force assertions for each of the three mechanisms (invincibility, knockback,
  per-mob cooldown) independently, including the cooldown's own overlap-break-and-resume
  condition verified past the invincibility window's own expiry.
- **Healing economy (AC-8):** direct-force integration check — force a known `RUNNING_TREASURE_COUNT`,
  trigger a heal-spend, confirm the exact decrement and the resulting health increase.
- **Weapon-tier funding economy (AC-9, delta 2026-07-19, second this date):** direct-force
  integration check mirroring AC-8's own established methodology — force a known
  `RUNNING_TREASURE_COUNT`/`WEAPON_TIER`, trigger a tier-spend, confirm the exact decrement and
  tier increase; spot-check spending at max tier still decrements treasure without exceeding the
  tier cap; confirm persistence across a mob-contact setback and a save/load round trip.
- **Save/load (AC-10):** two-instance save/reload harness, mirroring `IP-1104`'s own T27 pattern,
  extended to mob state/weapon tier/player health.
- **Determinism static audit (AC-11):** Inspection — direct code read of the mob-presence draw,
  mirroring `FS-110`'s own T22.h-equivalent precedent.
- **Cycle budget (AC-12):** Analysis — direct cycle-counting against a real per-frame call context
  including the coincident-materialization case (NFR-1500), now also covering `FR-11210`/
  `FR-11410`/`FR-11310`/`FR-11510`'s own per-frame cost, not possible until an implementation
  exists to measure.

**Corpus:** not yet defined — depends on the mob-slot count (an adjustable default, `ADS-002`)
and the mob-presence density constant, neither fixed by this specification.

## 17. Dependencies

Per FEAT-11000's own Dependencies (carried forward verbatim): FEAT-10000 (Infinite Mode — this
Feature is strictly a gated sub-mode of it; mob/projectile materialization piggybacks on its own
per-region materialization hook; combat state persistence extends its own save/load mechanism and
version-byte precedent); FEAT-3000 (Collectibles, Scoring & Victory — `RUNNING_TREASURE_COUNT` is
the same count this Feature's own healing economy spends from); FEAT-6000 (Presentation & HUD —
the player-health display reuses its own existing heart-tile art and HUD-write pattern).

## 18. Risks

Carried forward from FEAT-11000's own Risk assessment (Medium-High): `NFR-1500`'s own per-frame
cycle budget is honestly `UNCONFIRMED` (measurement owed once real code exists, and must be
checked against `NFR-1400`'s own already-`NOT MET` region-materialization cost, not the nominal
frame ceiling alone — a compounding-cost risk `R115` names directly); `NFR-4500`'s ROM/OAM budget
is real but favorable, not yet confirmed against a real implementation's actual footprint.

**Additional risk surfaced by this specification, not named at the Feature-catalog level:** four
genuinely open questions (below) touch UI shape, edge-case sequencing, setback feedback, and
(delta 2026-07-19) mob-movement-near-the-player sequencing — fewer than `FS-110`'s own eight, but
still enough that whoever picks this Feature up next should weigh routing some upstream (Open
Question 1, an architecture-level UI-shape choice) before `07-implementation-planning` attempts a
package, versus letting `07` resolve the others as implementation-level choices, mirroring
`FS-110`'s own precedent for exactly this judgment call.

**Delta 2026-07-19 — two new leaves added late in this Feature's own lifecycle, after five of six
packages already shipped:** unlike every requirement this specification originally elaborated,
`FR-11210`/`FR-11410` were baselined *after* `IP-1120`–`1125` were planned/mostly implemented, in
response to user-filed gaps found by playing the shipped build, not upstream architecture
sequencing. This is a genuinely different provenance from this Feature's own original six
requirements — worth naming as its own risk category: any future `07-implementation-planning`
package for these two leaves must account for the state five sibling packages have already
committed to (WRAM layout, `SAVE_VERSION_VAL`, existing test suites `T29`–`T31`/`T33`), not plan
against a clean slate the way the original six packages could. **`IP-1126` (`FR-11210`) has since
shipped `COMPLETE`, own `09` pass owed; `IP-1127` (`FR-11410`) remains `BLOCKED` on `IP-1123`
reaching `VERIFIED`.**

**Delta 2026-07-19 (second this date) — two more new leaves, `FR-11310`/`FR-11510`, added the
same day as `FR-11210`/`FR-11410`, extending the same late-lifecycle-addition risk category
above** — both trace to a `02`/`03` grounding pass this same session (`R219`/`R220`, `ADS-002`'s
"Weapon Directionality Delta"/`ADR-0021`) rather than either upstream sequencing or a direct
user-filed gap, a third distinct provenance in this Feature's own history. **Growing
input-binding contention, named explicitly:** this Feature now has three distinct spend/action
inputs with no confirmed free button (`FR-11500`'s heal-spend, `BL-0148`; `FR-11510`'s
tier-spend; and, less acutely, `FR-11310`'s own direction-derivation, which needs no *new* button
since it rides existing D-pad state) — every existing button is already claimed (D-pad movement,
A for fire, B the universal cancel, START/SELECT both claimed by existing menus). A future `06`/
`07` pass should weigh a single shared UI (e.g. a spend menu reachable via SELECT, mirroring
`IP-1090`'s own precedent) consolidating both spend actions, rather than each package
independently re-discovering the same unresolved gap — named here as a recommendation, not
decided or blocking.

## 19. Open Questions

1. **Resolved (`GDS-01` §4e, `IP-1120`, 2026-07-17).** The gating mechanism needed a `GDS-01`
   delta after all (§4d's own text was a closed two-option fact a third option would have
   falsified) — routed to `03-architecture-design-synthesis` (`BL-0146`), which decided a new
   `COMBAT MODE CONFIRM` state (binary Y/N, not a three-state `MODE SELECT` cursor), keeping
   "which world" and "combat on/off" on separate axes. `IP-1120` is now fully planned against it.
2. **Damage-vs-heal-spend ordering within the same frame is not decided.** Whether a mob's attack
   and a player's heal-spend action can both resolve in the same frame, and if so which applies
   first, is genuinely undecided (§7 edge case). Not expected to matter often (both are
   player/enemy-initiated discrete events, not continuous per-frame effects), but not asserted
   safe either. Resolves at: `07-implementation-planning`, as an implementation-level sequencing
   choice — does not require a requirements or architecture change either way.
3. **Resolved (`IP-1123`, 2026-07-18): shipped as a silent no-op.** `inf_heal_spend` at zero
   treasure changes neither `RUNNING_TREASURE_COUNT` nor `PLAYER_HEALTH` and produces no other
   observable effect (`T31.e`) — no disabled-option/audio cue was added. A richer cue remains
   possible as a future presentation-layer touch but is not required by `FR-11500`; this
   subroutine has no real input binding yet regardless (`BL-0148`), so the no-op is not yet
   player-reachable either way.
4. **Resolved (`IP-1126`, 2026-07-19): a mob exactly coincident with the player holds still.**
   `FR-11210` requires distance-to-player to strictly decrease over recomputation intervals but
   explicitly allows "the mob reaching the player's own position" as a valid terminal condition —
   it did not state what happens on the *next* interval after that point is reached. `inf_mob_move`
   resolves it as: when a mob's `dx == 0` and `dy == 0` relative to the player, the mob does not
   re-attempt movement that interval — it does not jitter (`T35.e`). This does not by itself
   resolve `FR-11410`'s own adjacent question (whether mob movement pauses during the player's
   post-contact invincibility window) — that remains `IP-1127`'s own open sequencing choice, since
   coincidence (`dx==0, dy==0`) and mere adjacency/overlap (a nonzero-but-in-contact-range
   distance, `FR-11400`'s own `0<=dx<=7, 0<=dy<=15` box) are not the same condition. Named at the
   Requirements Review stage (`03-requirements-review.md` finding #24) rather than invented here.

## 20. Related ADRs

ADR-0007 (8×16 OBJ sprite mode — governs any new mob/projectile sprite). **ADR-0021 (delta
2026-07-19, second this date)** — weapon-direction representation: a new `PLAYER_FACING` concept
(not a widened `PLAYER_DIR`), 8-directional, diagonal projectile motion via simultaneous
independent per-axis stepping, no new player sprite art. Governs `FR-11310`'s own implementation
shape.
