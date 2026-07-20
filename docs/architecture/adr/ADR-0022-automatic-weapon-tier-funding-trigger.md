# ADR-0022 — Automatic weapon-tier funding trigger: threshold-crossing auto-spend, no button binding

**Status:** Accepted (2026-07-20)

## Context

`FR-11510`/`IP-1129` shipped `inf_tier_spend` (`WEAPON_TIER` funding via spent treasure) as a
**player-invoked action** — but no button was ever bound to it (every input is already claimed:
D-pad for movement, A for firing, B for cancel, START/SELECT for menus), tracked since planning
as `BL-0148`. `inf_tier_spend` is fully implemented, tested (`T38.a`-`e`), and independently
`VERIFIED` — but entirely unreachable in real play. The user asked directly: "Implement an
automatic weapon upgrade based on research."

`R219` (ranged-weapon upgrade/progression conventions) already grounds the funding *shape*
(currency-spent, persistent-purchase, capped at `WEAPON_TIER`'s existing maximum of 3, mirroring
the *Zelda* shop-upgrade convention over *Contra*'s pickup-drop/full-reset model) and explicitly
scopes the exact trigger mechanism and numeric thresholds as *out of scope* for research — "a
`04`/`06` decision, not a research conclusion." No new research is needed to ground *whether* an
automatic trigger fits this project's own already-decided constraints; it is a design decision
squarely within what `R219` already deferred.

## Decision

**1. The trigger becomes automatic: checked once per frame during `COMBAT_MODE`, no player
action required.** Resolves `BL-0148`'s own input-binding gap for the `WEAPON_TIER` half by
removing the need for a binding entirely — the same shape `st_playing`'s own existing
unconditional per-frame combat chain (`inf_mob_move`/`inf_projectile_update`/etc.) already uses
for logic that runs every frame without dedicated input. `inf_tier_spend`'s own existing body
(decrement-and-cap, spends even past the next threshold is not applicable since it only fires
*when* the threshold is met — see Decision 2) is reused, not rewritten; only *what calls it, and
when* changes.

**2. Threshold-crossing, not per-frame flat-rate spend.** `RUNNING_TREASURE_COUNT` is checked
each frame against the treasure cost required for the *next* tier; when it is met or exceeded,
the spend fires once (bringing `WEAPON_TIER` up by exactly one) and the check re-arms for the
following tier's own (higher) threshold next frame. **Rejected alternative: a flat, continuous
"spend 1 treasure per frame while any treasure is held" rule** (mirroring the previous manual
design's own 1-treasure-per-invocation cost) — under automatic per-frame triggering this would
exhaust `RUNNING_TREASURE_COUNT` and max `WEAPON_TIER` within roughly two frames of collecting
any treasure at all, trivializing both the upgrade and the currency's own existing role in the
win/high-score system (`FR-10400`). A threshold-crossing check preserves a real, felt cost per
tier without requiring a manual action.

**3. Threshold values: 10 treasure for tier 1→2, 25 total for tier 2→3 (15 more).** A modestly
increasing curve (not flat, not steeply exponential) — meaningful enough that early-game treasure
collection doesn't instantly max the weapon, but reachable well within a normal Infinite Mode run
given treasure is this game's own core, plentiful collectible. Exact numbers are a `04`-level
judgment call, not derived from a cited convention (`R219` explicitly left this open) — deliberately
conservative and revisable if playtesting shows the curve feels wrong, named honestly as such
rather than presented as research-derived.

**4. `WEAPON_TIER`'s own existing persistence, cap, and setback-immunity are unchanged.** Once
auto-purchased, a tier increase behaves exactly as `FR-11510` already specifies: never
decremented by a mob-contact setback, persists through save/load. Only the trigger source
changes.

**5. `inf_heal_spend`'s own identical input-binding gap (`BL-0148`'s other half) is explicitly
NOT resolved here.** The user asked specifically about the weapon upgrade; healing retains its
own manual-spend design, still unreachable, tracked separately. `BL-0148` is updated to reflect
partial closure (tier-spend half resolved, heal-spend half still open) rather than closed
outright — mirrored, not duplicated.

## Consequences

- Closes `BL-0147`/`BL-0148`'s own tier-spend half: `WEAPON_TIER` becomes reachable in real play
  for the first time since `IP-1122`/`IP-1129` shipped.
- `FR-11510` requires a revision (Inputs/Preconditions/Postconditions/Acceptance Criteria all
  currently describe a player-invoked "tier-spend action" that no longer exists as a discrete
  input event) — routed to `04-requirements-engineering`.
- `FS-112` requires a metadata/behavior update to match — routed to `06-feature-specification`.
- New WRAM: two threshold constants (compile-time, not runtime state — no new WRAM byte). The
  automatic check itself needs no new persisted state beyond `WEAPON_TIER`/`RUNNING_TREASURE_
  COUNT`, both already shipped and save-persisted.
- `BL-0148` is only partially closed by this decision — recorded explicitly, not silently dropped.

## Alternatives Considered

- **A dedicated menu/subscreen for spending** (one of `BL-0148`'s own originally-named
  candidates) — rejected for this request specifically: the user asked for *automatic*, which a
  menu-based spend is not; a menu would still solve the input-binding gap but requires new screen
  content this request doesn't ask for.
- **A context-sensitive reuse of an existing button** (`BL-0148`'s other named candidate) — same
  reasoning; the user's own request is unambiguously for automation, not a new binding.
