# FS-101 — Per-Zone ScoreItem Persistence

> **Status: ✅ Specified (2026-07-07).** Owned by `06-feature-specification`. Elaborates
> [FEAT-5100](../feature-planning/03-feature-catalog.md#feat-5100--per-zone-scoreitem-persistence-new--not-yet-implemented)
> (Epic [EP-3000](../feature-planning/02-epic-catalog.md#ep-3000--persistence)). **No shipped
> implementation exists yet** — this spec is the input to `07-implementation-planning`, not a
> description of current behavior.

## Feature ID

`FS-101`, elaborating `FEAT-5100` (Feature Catalog: `docs/feature-planning/03-feature-catalog.md`).

## Title

Per-Zone ScoreItem Persistence

## Purpose

Extend the save system so that a restored game does not re-present already-collected `ScoreItem`s
(stars/flowers) as available — carried forward verbatim from FEAT-5100's Purpose. Resolves
`BL-0018` per the user's explicit 2026-07-07 decision: "Zone score item state should save and
persist."

## Scope

**In scope:** persisting per-zone `ScoreItem` collected-state (1) across save/load, and (2) — per
a design finding below — across ordinary zone-to-zone traversal within a single play session,
mirroring how `Carrot` state already works. **Out of scope** (carried forward from FEAT-5100):
player facing-direction and animation-frame persistence — explicitly rejected by the user
("not important"); no requirement anywhere claims this scope. Also out of scope: any change to
`ScoreItem` values, placement, or the collection-detection mechanic itself (FR-3100/FR-3200,
owned by FEAT-3000).

## Requirements Implemented

- **FR-5220** — Persist per-zone ScoreItem collected-state (the sole Included Requirement of
  FEAT-5100; carried forward with none added, none dropped).

## User Workflows

1. **Collect, leave, and return within a session.** Player collects a star in Zone 0 (Beach) →
   walks to Zone 1 (Forest) → walks back to Zone 0. **Expected after this Feature:** the
   already-collected star does not reappear. *(Before this Feature: it currently does reappear —
   see the Risks section's finding on `setup_zone_collects`.)*
2. **Collect, save, power off, reload.** Player collects several stars/flowers across multiple
   zones → opens the SAVE menu → confirms save → powers off → powers on. **Expected:** every
   previously-collected `ScoreItem` remains uncollected-and-hidden (i.e., inactive) on reload;
   every never-collected `ScoreItem` remains available.
3. **Load a save written before this Feature shipped.** Player has an existing save from the
   pre-FS-101 build → loads it after the game is upgraded. **Expected:** all `ScoreItem`s are
   treated as **uncollected** (see Design Decision 2 below) — no items vanish that the player
   never actually collected, and no crash/garbage-state occurs from reading previously-unused SRAM
   bytes.

## System Behaviour

### Normal path

- On `ScoreItem` collection (FR-3200, unchanged), in addition to the existing Score increment and
  in-zone deactivation, the system shall also set that item's bit in a new persistent, per-zone
  collected-state structure (Design Decision 1).
- Whenever a zone is (re-)entered — the existing `setup_zone_collects` routine, which already
  reloads all collectible active-flags from ROM every zone entry — the system shall additionally
  clear the `active` flag for any `ScoreItem` whose bit is set in that persistent structure,
  exactly mirroring the existing Carrot suppression check (`CARROT_FLAGS`) already present in that
  routine.
- On explicit save (FR-5100, unchanged), the system shall also write the persistent structure's
  current 9 bytes to SRAM.
- On boot with a valid save (FR-5200, unchanged), the system shall also restore the persistent
  structure's 9 bytes from SRAM — **conditionally**, per Design Decision 2's version-guard.

### Edge cases

- **A zone with the maximum ScoreItem count (7, Zone 7/Plains — confirmed by direct tally of
  `ZONE_COLLECTS`)** must fit within a single byte's bit-per-item capacity (8 bits ≥ 7) — this
  is confirmed to fit with one bit to spare, no zone requires more than one byte.
- **A save written before this Feature shipped** — see Design Decision 2.
- **Collecting the last `ScoreItem` in a zone does not affect victory** — `CarrotCount`, not
  `ScoreItem` state, gates victory (FR-3300, unchanged); this Feature does not touch that logic.

## Module Responsibilities

- **`asm_game.py`** — sole affected module (per FEAT-5100's Affected Modules): declares the new
  WRAM constant; extends the collection-handling code path to set the new persistent bit; extends
  `setup_zone_collects` to check it (mirroring the existing Carrot check at
  `asm_game.py` lines ~628–638); extends the save-write and load-restore routines to include the
  new SRAM bytes plus the version-guard byte (Design Decision 2).
- No other module (`tiles.py`, `tilemaps.py`, `music.py`, `build_rom.py`, `gbc_lib.py`) requires
  any change — confirmed consistent with FEAT-5100's catalog entry.

## Interfaces Used

- No `GDS-09` interface contract requires extension. This Feature is entirely internal to
  `asm_game.py`'s existing WRAM-constants/save-routine/`setup_zone_collects` code — it does not
  touch `build_game_asm`'s returned `patches` dict, `ALL_SCREENS`, `ZONE_COLLECTS`'s shape, or any
  other cross-module interface GDS-09 documents.

## Data Model Changes

**This Feature requires additive changes to GDS-07's Data Model** — flagged here since GDS-07
does not yet document them (per this skill's own rule: "additions only where requirements demand,
flagged if the existing model doesn't support the behavior"):

- **New WRAM array `SCOREITEM_FLAGS`** — proposed at `0xC01E` (immediately after the existing
  `CARROT_FLAGS` at `C015`–`C01D`, before `COLL_DATA` at `C020` — 2 bytes of headroom exist
  there, `C01E`–`C01F`, which is not quite enough; **the concrete address must be assigned by
  `07-implementation-planning`** against the actual current WRAM layout, not guessed here — this
  spec states only that it is a **9-byte array, one bitfield byte per zone** (mirroring
  `CARROT_FLAGS`'s exact shape), with each bit `N` corresponding to the `N`th entry in that zone's
  `ZONE_COLLECTS` list (the same list-position indexing `setup_zone_collects` already uses for its
  loop counter) — confirmed sufficient by direct tally: no zone has more than 7 `ScoreItem`
  entries (Zone 7/Plains, the maximum), fitting in one byte with a bit to spare. Carrot-type list
  entries occupy a bit position too (harmlessly unused, since Carrot state is tracked separately
  via `CARROT_FLAGS`) — this keeps the bit-to-list-index mapping trivial rather than requiring a
  second "skip carrots" index scheme.
- **New SRAM bytes**, appended immediately after the existing save format's last used byte
  (`A011`, the end of `CARROT_FLAGS`): a new 1-byte **save-format version guard** at `A012`
  (Design Decision 2), followed by the 9-byte `SCOREITEM_FLAGS` mirror at `A013`–`A01B`. SRAM has
  ~8KB total with only 18 bytes (`A000`–`A011`) in use today — no budget concern
  (`NFR-4100`/`BL-0019`'s ROM-budget watch is unrelated; this is SRAM, not ROM).

## State Changes

- No new game state (`GAMESTATE` values) is introduced — this Feature operates within the existing
  PLAYING state's zone-entry logic and the existing SAVE state's save-confirm action.
- **New persistent state**: `SCOREITEM_FLAGS[zone]`, created (implicitly, as all-zero) at first
  boot on a fresh save, set bit-by-bit on `ScoreItem` collection, read on every zone entry, written
  on save, restored on load.

## Error Handling

- **Invalid/missing save-format version guard on load** (i.e., a save written before this Feature
  shipped): the system shall treat `SCOREITEM_FLAGS` as all-zero (all `ScoreItem`s uncollected)
  rather than trusting whatever garbage bytes occupy the new SRAM region — see Design Decision 2.
  This is the only new failure mode this Feature introduces; it does not change the existing
  invalid-magic-byte handling (FR-1110, unaffected).

## Performance Considerations

- Negligible. The added save/load work is 10 bytes (1 version-guard + 9 `SCOREITEM_FLAGS`) in a
  routine that already reads/writes at least 18 bytes under the existing MBC1 enable/disable
  bracket (`NFR-5100`, unaffected) — no new VBlank-timing concern (`NFR-1100`, unaffected by this
  Feature; the save/load routines are not VRAM/OAM writes).
- The `setup_zone_collects` extension adds one additional bit-test per collectible entry per zone
  entry (already a per-entry loop, mirroring the existing Carrot check) — negligible relative to
  the existing routine's cost.

## Integrity Considerations

- **`NFR-5200`(save-field round-trip integrity)** now additionally covers `SCOREITEM_FLAGS`: a
  save followed by a load must restore each zone's bitfield to exactly its value at save time.
  This Feature's design keeps the existing `NFR-5100` MBC1 enable/disable bracket unchanged —
  the new bytes are read/written inside the same bracket, not a separate one.
- **Design Decision 2's version guard is itself an integrity mechanism**: without it, a
  pre-upgrade save's uninitialized SRAM bytes at the new addresses could be silently
  misinterpreted as meaningful collected-state, a data-integrity gap this spec explicitly closes
  rather than leaves implicit.

## Acceptance Criteria

1. Given a `ScoreItem` is collected, then the player leaves and returns to that zone within the
   same session (no save/load involved), that `ScoreItem` remains inactive/uncollectible.
2. Given a `ScoreItem` is collected and the game is saved, then the game is powered off and
   reloaded, that `ScoreItem` remains inactive/uncollectible.
3. Given a `ScoreItem` was never collected, it remains active/collectible after any zone
   transition, save, or reload.
4. Given a save written by a pre-FS-101 build (no version-guard byte, or a version-guard byte not
   matching the value this Feature's build writes), on load every `ScoreItem` in every zone is
   treated as uncollected — no crash, no silent misinterpretation of garbage bytes as "collected."
5. `CarrotCount`/`Score`/`CarrotFlags`/`CurrentZone`/`PlayerPosition` (the pre-existing save-field
   set) continue to round-trip exactly as before — this Feature must not regress `FR-5100`/
   `FR-5200`/`NFR-5200`'s existing "Met" status.

## Verification Plan

| Acceptance Criterion | Method | Suite |
|---|---|---|
| 1 (same-session, cross-zone persistence) | Test | New suite — proposed `T11: Per-Zone ScoreItem Persistence`, since no existing `test_rom.py` suite covers this behavior (it did not exist before this Feature). |
| 2 (save/load persistence) | Test | `T11`, same new suite. |
| 3 (never-collected items stay available) | Test | `T11`. |
| 4 (pre-upgrade save compatibility) | Test | `T11` — requires constructing a synthetic pre-upgrade SRAM image (no version-guard byte / a mismatched one) as a fixture. |
| 5 (no regression to existing save fields) | Test | Existing save/load assertions, once `BL-0006`/`BL-0008`'s test-suite rewrite lands — **this criterion's automated verification is currently blocked by the same project-wide `NFR-7100` non-compliance every other Feature inherits (FEAT-7000)**, not by anything specific to this Feature. |

## Dependencies

- **FEAT-5000** (Save/Load System, as-built) — this Feature extends its save-write/load-restore
  routines rather than introducing a new mechanism, per FEAT-5100's own Dependencies field.
- **FEAT-3000** (Collectibles, Scoring & Victory) — `ScoreItem` collection is the event this
  Feature's new persistent bit hooks into.
- No other `FS-xxx` document exists yet to depend on (this is the first spec authored).

## Risks

- **Confirmed design finding, not assumed:** direct code reading of `setup_zone_collects`
  (`asm_game.py`, the loop labeled `szc_lp`/`szc_sk`) confirms that **`ScoreItem`s currently
  respawn every time a zone is re-entered, even within the same play session, independent of any
  save/load** — only `Carrot`s are protected against respawn today, via the existing
  `CARROT_FLAGS` check in that same routine. **This means `FR-3200`'s postcondition ("the
  ScoreItem is permanently inactive for the remainder of that play session") is factually
  incorrect as currently shipped** — a pre-existing requirements-baseline inaccuracy this spec
  did not introduce but must not silently paper over. This Feature's design (extending the exact
  same zone-entry check `Carrot`s already use) will, as a side effect, also make `FR-3200`'s
  postcondition true going forward — a beneficial, expected consequence of mirroring the
  `Carrot` pattern, not scope creep, since it's the natural reading of "should save and persist"
  applied consistently with how the analogous entity already works. **Recommendation: route the
  `FR-3200` inaccuracy back to `04-requirements-engineering` as a correction**, independent of
  whether/when this Feature ships (see Open Questions).
- **Medium implementation risk** (carried forward from FEAT-5100's catalog entry): this is the
  first change to the save-format contract since it shipped (`ADR-0006`). The version-guard
  mechanism (Design Decision 2) is the safeguard against silently corrupting the meaning of old
  saves.
- **WRAM address not yet assigned**: this spec states `SCOREITEM_FLAGS`'s *shape* (9 bytes, one
  bitfield per zone) but explicitly defers its exact WRAM address to `07-implementation-planning`,
  since the 2-byte gap this spec noticed (`C01E`–`C01F`) is insufficient and a real placement
  decision (rearranging WRAM, or placing it after `COLL_COUNT`/`OAM_BUF`, etc.) belongs to the
  implementation-planning stage, not invented here.

## Open Questions

1. **Should `FR-3200`'s postcondition be corrected** to remove the (currently false) claim that
   `ScoreItem`s stay inactive "for the remainder of that play session," given the confirmed
   `setup_zone_collects` respawn-on-re-entry behavior? **Owner: `04-requirements-engineering`.**
   Not blocking this Feature's implementation — this spec's design fixes the underlying behavior
   either way, but the requirements text should stop asserting something not true of the current
   shipped code.
2. **Is the confirmed respawn-on-zone-re-entry behavior itself worth a separate backlog bug
   entry** (independent of this Feature), given it means `ScoreItem`-based `Score` is currently
   infinitely farmable by walking back and forth between two zones, and `SCORE` is a single WRAM/
   SRAM byte (0–255) with no documented overflow handling? **Owner: `00-pipeline-manager`'s
   harvest step / the user** — this spec surfaces the finding; whether it's tracked as a standalone
   `bug` (with its own severity/urgency) versus folded entirely into this Feature's fix is a
   triage call, not resolved here.
3. **Exact WRAM address for `SCOREITEM_FLAGS`** — see Risks; owner `07-implementation-planning`.

## Related ADRs

- **ADR-0006** (MBC1+RAM+BATTERY, `BUNY` magic) — this Feature widens that ADR's declared
  save-field set within the same mechanism; does not supersede or conflict with it.

---

## Design Decisions (recorded per this spec's own reasoning, not left as Open Questions)

### Design Decision 1 — Persistence structure mirrors `CARROT_FLAGS` exactly

A 9-byte, one-byte-per-zone bitfield array (`SCOREITEM_FLAGS`), with each bit indexed by list
position within that zone's `ZONE_COLLECTS` entries — chosen because (a) it requires no new
indexing scheme beyond what `setup_zone_collects` already computes (the loop's countdown counter
`B` is already list-position-relative), (b) it is proven sufficient by direct tally (max 7
`ScoreItem`s in any zone, Zone 7/Plains), and (c) it is byte-for-byte structurally identical to
the already-shipped, already-verified `CARROT_FLAGS` pattern, minimizing new design surface.

### Design Decision 2 — Pre-upgrade saves default to "all ScoreItems uncollected," guarded by a version byte

**Recommendation (not a genuinely open question — reasoned to a confident answer):** default to
**uncollected**, not "already collected," for any save lacking this Feature's data. Reasoning:
"already collected" would require asserting something the system cannot actually know (which
items a pre-upgrade player happened to collect) — asserting it anyway risks silently hiding
content a player never got the enjoyment of collecting. "Uncollected" matches the exact
information the system honestly has (none) and matches the pre-upgrade player's actual prior
experience (every item was always available on reload, since no persistence existed before this
Feature) — so nothing about their save's observable behavior gets worse, only better (no more
respawn-after-collection within a session, per the Risks section's finding). **The version-guard
byte exists specifically so this default is only applied deliberately** (on a confirmed old-format
save) rather than by accident (trusting whatever garbage happens to occupy newly-added SRAM
bytes) — a save missing or mismatching the guard is unambiguously pre-upgrade, not a corrupted
new-format save that should instead fail some other way.
