# Technical Work Breakdown

> **Status: ✅ Authored (first planning pass, 2026-07-07); latest delta 2026-07-14 (Infinite
> Mode, `FS-110`/`FEAT-10000`, 5 packages `IP-1100`–`IP-1104`, AUTHORIZED 2026-07-14, "Yes, build
> all five"); delta 2026-07-16 (Procedural Music Generation, `FS-111`/`FEAT-7100`, 2 packages
> `IP-1110`/`IP-1111`, not yet authorized); delta 2026-07-17 (Infinite Mode Combat Sub-Mode,
> `FS-112`/`FEAT-11000`, 6 packages `IP-1120`–`IP-1125`, none authorized — `IP-1120` initially
> `BLOCKED` on a `GDS-01` §4d amendment, a genuine architecture gap found and routed upstream
> rather than planned around; resolved same day, `GDS-01` §4e, `IP-1120` now fully planned).**
> Owned by
> `07-implementation-planning`. Records how approved work is cut into Implementation Packages —
> the rationale for every split/no-split decision is the artifact. Package status lives in the
> [Master Build Plan](00-master-build-plan.md), not here.

[↑ Docs index](../INDEX.md) · [Master Build Plan](00-master-build-plan.md) ·
[Packages](packages/INDEX.md)

## Scope of this pass

Two tranches, planned together in the pipeline's first stage-07 run:

1. **Remediation tranche** — the `BL-0008` umbrella ("docs/tests describe the wrong game"),
   covering `BL-0001`, `BL-0003`, `BL-0004`, `BL-0005`, `BL-0006`, `BL-0007`.
2. **Feature tranche** — [`FS-101` Per-Zone ScoreItem Persistence](../features/FS-101-per-zone-scoreitem-persistence.md)
   (`FEAT-5100`, `FR-5220`), with `BL-0023` (ScoreItem respawn/score-farming bug) riding as its
   designed side-effect fix.

## Re-verification results (planning-stage evidence, direct code reads 2026-07-07)

`BL-0008`'s scope required re-verifying `BL-0001`/`BL-0003`'s pre-rewrite claims against the
current tree before packaging. Results:

- **`BL-0001` (map hearts at wrong BG addresses) — does NOT reproduce; no package.** The
  current `update_map_hearts` (`asm_game.py:644`) writes 9 hearts at
  `0x9800 + row*32 + col` for rows 6/9/12 × cols 6/11/16 — exactly where `map_screen()`
  (`tilemaps.py:327`) places its heart tiles (`cx+3 = 6/11/16`, `cy+1 = 6/9/12`, from
  `cell_x0=3, cell_y0=5, cw=5, ch=3`). The routine runs only via `do_screen_redraw`'s `dsr_m`
  path (`asm_game.py:570`), i.e. with the LCD off, so the writes are also timing-safe. The bug
  as filed described the pre-rewrite 3-heart mechanism; the rewrite replaced and fixed it.
  The rewritten test suite (IP-9010) adds a heart-placement check so this stays verified.
- **`BL-0003` (score display writes VRAM while LCD on) — DOES reproduce; packaged as IP-9020.**
  `update_status_disp` (`asm_game.py:505`) writes BG-map bytes at `0x9802` and
  `0x9808`–`0x980A` with no STAT/VBlank guard. It is called from `st_playing`
  (`asm_game.py:203`) *after* `handle_play_input`/`check_collisions`/`check_zone_transition`/
  `check_complete`, so the writes can land outside the VBlank window (mode 3 → write dropped).
  This is exactly `NFR-1200`'s recorded NOT MET status.

## Work units and package cut

### Remediation tranche (`BL-0008`)

| Work unit | Package | Owner |
|---|---|---|
| Rewrite `test_rom.py` assertions for Bunny Quest semantics (`BL-0006`) + repo-relative paths and correct ROM filename (`BL-0005`) | [IP-9010](packages/IP-9010-test-suite-rewrite.md) | `08-code-implementation` |
| Fix `update_status_disp`'s unguarded VRAM writes (`BL-0003`) | [IP-9020](packages/IP-9020-score-bar-vblank-fix.md) | `08-code-implementation` |
| Refresh `Claude.md`/`memory.md`/`README.md` (`BL-0007`) | [IP-9030](packages/IP-9030-root-doc-refresh.md) | `08-code-implementation` |
| Archive legacy artifacts to `legacy/` (`BL-0004`) | [IP-9040](packages/IP-9040-legacy-artifact-archival.md) | `08-code-implementation` |
| Re-verify `BL-0001` | *(no package — does not reproduce; see above)* | — |

**Split rationale:**

- **`BL-0005` + `BL-0006` fused into one package (IP-9010).** Both live entirely inside
  `test_rom.py`; the path/filename fix alone is worthless (the suite still asserts the wrong
  game), and the assertion rewrite can't even run without the path fix. Two packages editing the
  same file serially would add coordination cost and zero parallelism. R305 explicitly recommends
  a suite-level rewrite over a line-by-line patch, which makes the fused package one coherent
  Definition of Done: *a trustworthy suite against the shipped game*.
- **`BL-0003` split out (IP-9020)** because it changes **game code** (ROM bytes change) while
  IP-9010 is test-harness-only (ROM unchanged). Keeping ROM-affecting and ROM-neutral changes in
  separate packages keeps each package's verification story clean (IP-9010 must produce a
  byte-identical ROM; IP-9020 must not).
- **`BL-0007` split out (IP-9030)** because it is documentation-only and should land *after*
  IP-9010/IP-9020 so the refreshed docs describe the post-remediation state (trustworthy suite,
  fixed score-bar timing) instead of needing a second refresh a week later.
- **`BL-0004` split out (IP-9040)** because it is pure file hygiene (git moves, no content
  edits) with an already-recorded user decision; folding it into any other package would blur
  that package's Definition of Done.

### Feature tranche (`FS-101`)

| Work unit | Package | Owner |
|---|---|---|
| Implement per-zone ScoreItem persistence end-to-end (WRAM array, collection hook, zone-entry suppression, save/load + version guard, resets, T11 tests) | [IP-1010](packages/IP-1010-per-zone-scoreitem-persistence.md) | `08-code-implementation` |

**No-split rationale:** FS-101's five behaviors (collect-hook, zone-entry check, save, load,
reset paths) are one atomic contract — shipping any subset leaves the save format or the
in-session behavior half-migrated (e.g. persisting bits that zone entry then ignores). All
changes land in one module (`asm_game.py`) plus the new T11 suite. One package, one stage-08
run, one Definition of Done.

**Deferred detail resolved here (FS-101 Open Question 3):** `SCOREITEM_FLAGS` is assigned
**`0xC060`–`0xC068`** (9 bytes). Rationale: GDS-07's WRAM map shows `C051`–`C2FF` unallocated
(the 2-byte gap at `C01E`–`C01F` FS-101 noticed is insufficient for 9 bytes); `0xC060` is
8-aligned, leaves `C051`–`C05F` spare next to `COLL_COUNT` for future collectible-state growth,
and sits inside the boot-time `C000`–`C2FF` clear (`asm_game.py:86-88`), which delivers FS-101's
"implicitly all-zero at first boot" for free. The SRAM layout is exactly as FS-101 specifies:
save-format version guard at `0xA012` (value `0x01`), `SCOREITEM_FLAGS` mirror at
`0xA013`–`0xA01B`.

## Sequencing summary

**IP-9010 is the universal unblocker**: the G5 permanent gate ("full `test_rom.py` suite
passes") is unsatisfiable for *every* package until the suite itself is rewritten, so every
other package depends on IP-9010 reaching `VERIFIED`. After that: IP-9020, IP-9040, and IP-1010
are parallel; IP-9030 waits for IP-9020 (it documents the fixed behavior). Critical path (per
FP-04, Release 1 = `FEAT-5100`): **IP-9010 → IP-1010**.

## Backlog riders honored in this pass

- **`BL-0017`** (one-carrot-per-zone invariant): no package touches `ZONE_COLLECTS`, but
  IP-9010's rewritten suite adds a data-level check asserting exactly one type-2 entry per
  zone list — turning the invariant from convention into a tested property.
- **`BL-0019`** (ROM-headroom watch): IP-9020 and IP-1010 (the two ROM-growing packages) each
  carry an NFR-4000 headroom re-affirmation checklist item.
- **`BL-0023`** (ScoreItem respawn/score farming): fixed by IP-1010 as FS-101's designed side
  effect; IP-1010's T11 tests cover the same-session respawn case explicitly.

## Release-2 tranche (procgen-world increment, planned 2026-07-10)

**Scope:** all five Release-2 Features from the aesthetics/visual-story-narrative/procgen-
world-map increment, specified as [FS-102](../features/FS-102-procedural-world-generation.md)
(`FEAT-9000`), [FS-103](../features/FS-103-generated-region-screen-composition.md) (`FEAT-4100`),
[FS-104](../features/FS-104-main-menu-new-game-flow.md) (`FEAT-1100`),
[FS-105](../features/FS-105-generated-world-save-persistence.md) (`FEAT-5300`), and
[FS-106](../features/FS-106-aesthetic-biome-transition-compliance.md) (`FEAT-6100`). This is
genuinely new work — **no G3 bootstrap carve-out applies to any package in this tranche.**

### Deferred design decisions resolved in this pass

Three FS-102/FS-103 Open Questions (`BL-0038`) and both FS-104 Open Questions (`BL-0039`) were
explicitly deferred to this stage by their own text. Resolved here, following the FS-101/IP-1010
precedent of confident direct resolution rather than escalation:

**FS-102 OQ1/OQ3 + FS-103 OQ1/OQ2 (biome-family set, grammar table, tile/palette sizing, ROM
pointer):** **Reuse the five existing shipped terrain families exactly** — Water, Sand/Dirt,
Grass, Stone, Brick/Red (GDS-07 §5/GDS-08 §4's own palette table) — as the biome-family
vocabulary, per GDS-08 §8's own recommendation ("reuse the existing terrain-family palette
groups"). This has two large consequences that shrink this tranche's scope significantly:

1. **Zero new tile art or palette work is required.** Each family already has a fully-authored
   shipped screen-generator function reusable as that family's canonical representative:
   `lake_screen()` → Water, `beach_screen()` → Sand/Dirt, `forest_screen()` → Grass,
   `mountain_screen()` → Stone, `castle_screen()` → Brick/Red. (Extra per-family variety —
   e.g. `desert_screen()` as a second Sand/Dirt option, `plains_screen()`/`village_screen()`/
   `cave_screen()` as additional Grass/Stone variants — is a **future, optional**
   `08-content-authoring` addition; this tranche's Definition of Done needs only one function per
   family, since GDS-09's delta requires "one `fn()` per biome family," not per variant.)
2. **The grammar table is a linear axis, not a lookup table — no ROM pointer needed (resolves
   FS-102 OQ3).** Order the five families along one axis, index 0–4: **Water(0) – Sand(1) –
   Grass(2) – Stone(3) – Brick(4)** (directly matching R212's water→beach→…→mountains example,
   generalizing "sky" out since no such family is shipped, and placing Brick/Red — Castle, a
   structure/civilization biome — at the far end from Water, adjacent only to Stone). **Adjacency
   is legal iff the two families' axis indices differ by at most 1** — a single `SUB`+`CP` check
   Z80 can perform inline (`|idx_a - idx_b| ≤ 1`), needing no ROM-resident table at all. This
   resolves FS-102 OQ3 directly: **no new `patches` dict entry is needed for the grammar itself.**

**FS-102 OQ2 (generation algorithm):** **Flood-fill biome assignment over the fixed
`scale × scale` grid**, not a graph built from scratch:

1. Regions occupy a `scale × scale` grid exactly like the shipped 3×3 model generalizes
   (`row = index // scale, col = index % scale`) — **every** grid-adjacent pair is a valid
   transition (matching the shipped fully-connected-3×3 topology), so **reachability (FR-9120)
   is trivially satisfied by construction**, exactly as GDS-04's delta already notes the fixed
   grid never needed a reachability guard — this design keeps that property true at any scale.
2. Seed the xorshift16 PRNG (R111) from `SEED` (0 normalized to 1).
3. Assign region 0 (the start region, grid position `(0,0)`) axis-index **2 (Grass)** — matching
   the shipped world's default felt terrain and giving every generated world a consistent,
   familiar starting biome.
4. Visit every other region in row-major order; each region's axis-index = an already-visited
   grid-adjacent neighbor's axis-index, plus a PRNG-drawn delta in `{-1, 0, +1}`, **clamped to
   `[0, 4]`**. Because every grid-adjacent pair is generated from a delta of at most 1, **every
   grid-adjacent pair is grammar-legal by construction (FR-4310) — no candidate edge is ever
   rejected, no backtracking, no contradiction risk** (the exact WFC failure mode ADR-0009/R213
   name as the reason to avoid per-tile constraint solving).
5. Place exactly one `KeyItem` per region (FR-9130) — trivial, matching the shipped
   one-Carrot-per-zone convention, now generator-guaranteed rather than convention-only.

This algorithm is deliberately the simplest one satisfying all four generator-guaranteed
invariants (determinism, reachability, grammar-validity, one-KeyItem-per-region) — a design
choice this pass makes explicitly, not a default arrived at by omission.

**FS-104 OQ1 (SEED/SCALE ENTRY cancel path):** **B cancels back to MAIN MENU**, matching the
existing SAVE state's own A(confirm)/B(cancel) convention exactly — no new input convention
introduced.

**FS-104 OQ2 (menu input mapping):** D-pad up/down moves the highlighted option between
"continue"/"new game" (when both are present); A confirms the highlighted option — the same
cursor-based interaction shape ADR-0010 already specifies for the digit-cursor picker itself, not
a new convention.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| World generation routine (flood-fill biome assignment, PRNG, `REGION_GRAPH` layout) + item-agnostic `KeyItem` collection generalization + `worldgen.py` reference-generator oracle | [IP-1020](packages/IP-1020-procedural-world-generation.md) | `08-code-implementation` |
| `ALL_SCREENS` generalization to per-biome-family iteration + `build_rom.py`-side region-screen layout | [IP-1030](packages/IP-1030-generated-region-screen-composition-code.md) | `08-code-implementation` |
| Biome-family screen-generator registration (reusing the five existing shipped functions as canonical family representatives — zero new tile/palette authoring) | [IP-1031](packages/IP-1031-generated-region-screen-composition-content.md) | `08-content-authoring` |
| MAIN MENU + SEED/SCALE ENTRY states, SAVE's exit-to-main-menu option | [IP-1040](packages/IP-1040-main-menu-new-game-flow.md) | `08-code-implementation` |
| Save-format extension: `SEED`/`WORLD_SCALE`/`KeyItemFlags` persistence, version-guard bump | [IP-1050](packages/IP-1050-generated-world-save-persistence.md) | `08-code-implementation` |
| `FEAT-6100` (Aesthetic & Biome-Transition Compliance) | *(no package — see below)* | — |

**Split rationale:**

- **`FS-102` stays one package (IP-1020)**, mirroring FEAT-9000's own catalog-level cohesion
  decision (FP-05 finding #6) — the generation routine and the collection-mechanic
  generalization are tightly coupled (the same reasoning that merged `FR-9130`/`FR-3220` into one
  Feature to avoid an artificial cross-package cycle applies identically at the package level).
  The `worldgen.py` oracle rides the same package since it must be authored in lockstep with the
  SM83 routine from the start (GDS-09's delta), not bolted on afterward.
- **`FS-103` splits into code (IP-1030) and content (IP-1031)** — the exact code/content peer
  seam this skill's own workflow calls out. IP-1030 is pure `build_rom.py`/`asm_game.py`
  generalization (how the build assembles a variable-length, `WorldScale`-driven screen set
  instead of a fixed 9); IP-1031 is the biome-family-to-screen-generator registration (which
  existing function represents which family) — a content-authoring decision with **zero new
  pixel art**, per the biome-family reuse decision above. Keeping these separate lets
  `08-code-implementation` and `08-content-authoring` each own a clean Definition of Done instead
  of one package straddling both peers' scope.
- **`FS-104` stays one package (IP-1040)** — MAIN MENU, SEED/SCALE ENTRY, and SAVE's new exit
  option are one coherent state-machine extension; splitting them would leave an intermediate
  package unable to reach a testable end state (e.g. MAIN MENU alone, with no SEED/SCALE ENTRY to
  transition into on "new game," cannot be verified end-to-end).
- **`FS-105` stays one package (IP-1050)** — mirrors `IP-1010`'s own no-split precedent exactly
  (save-write and load-restore are one atomic contract; shipping either half alone leaves the
  save format partially migrated).
- **`FS-106` needs no Implementation Package.** Per its own spec (§8/§10), FEAT-6100 has **no
  runtime behavior and no module of its own** — its "implementation" already exists (GDS-08 delta
  §7/§8's checklist, `09-content-review`'s existing process). This tranche's `IP-1031` (the first
  content package this checklist applies to) is where FEAT-6100 is first *exercised*, via a
  future `09-content-review` pass — not authored as a package here. Naming this explicitly (rather
  than silently omitting FEAT-6100) keeps the Feature ↔ Package mapping complete and honest.

### Sequencing summary

**IP-1020 is this tranche's universal unblocker** — every other package either consumes its
generation output (IP-1030/IP-1031's screen rendering, IP-1050's save persistence) or triggers it
(IP-1040's new-game flow). Critical path (per FP-04, procgen-world increment): **IP-1020 →
IP-1030 → IP-1031** (3 packages — the same 3-node length FP-04's Feature-level critical path
predicted). IP-1040 and IP-1050 each depend only on IP-1020, parallel-eligible with each other
and with IP-1030/IP-1031.

### Backlog riders honored in this pass

- **`BL-0038`** (FS-102/FS-103's five shared Open Questions): resolved above — biome-family reuse,
  linear grammar axis, flood-fill algorithm, no ROM pointer needed.
- **`BL-0039`** (FS-104's two Open Questions): resolved above — B-cancels convention, cursor-based
  menu input mapping.
- **`BL-0019`** (ROM-headroom watch): IP-1020 (WRAM growth) and IP-1050 (SRAM growth) both carry
  NFR-4000/NFR-4200 headroom re-affirmation checklist items.

## Post-ship remediation tranche (playtesting bugs `BL-0047`/`BL-0048`, planned 2026-07-11)

Two bugs from the project owner's own playtesting of the shipped procgen-world tranche, both
already carrying reproduced root causes and recommended remediation shapes at intake (`00-intake`,
this session). Per this skill's own Step 1 discipline, both cuts additionally required the
mandatory **verb inventory** and **supersession sweep** checks before being called complete.

### Verb inventory — the procgen-world capability, re-audited

The Release-2 tranche (above) covered *generate* (`IP-1020`), *render* (`IP-1030`/`IP-1031`),
*trigger/menu* (`IP-1040`), and *persist* (`IP-1050`) — but never *navigate*. Re-auditing this now
against `BL-0047`'s own finding: `check_zone_transition` is the sole navigation call site, and it
was never touched by any Release-2 package. No deferral was ever recorded for it — it was simply
missed. This tranche closes that gap.

### Supersession sweep — run against `BL-0047`'s own framing ("`check_zone_transition` was never
generalized past the fixed-3×3 model")

A sweep for the retired model's literal signature (`CUR_ZONE` compared against small integer
literals tied to a 3×3 shape; fixed 9-entry tables indexed by `CUR_ZONE`) across
`asm_game.py`/`tilemaps.py`/`build_rom.py` found **two more instances, not just the one
`BL-0047` itself named**:

- **`SCOREITEM_FLAGS`** (`asm_game.py:44`) — still a fixed 9-byte array indexed by `CUR_ZONE`,
  unlike its sibling `KEYITEM_FLAGS` (already widened to 81 bytes by `IP-1020`). Filed as
  **`BL-0058`** (Critical) — fixing `BL-0047` alone, without this, converts a dormant bug into
  live WRAM corruption of `REGION_GRAPH` itself, since `CUR_ZONE` values above 8 become reachable
  the moment navigation is fixed.
- **`ZONE_COLLECTS`/`zc_table`** (`tilemaps.py:407`) — still the original 9 hand-authored,
  zone-named spawn-position lists (the module's own docstring says so verbatim), read via a
  9-entry ROM table indexed by `CUR_ZONE`. Filed as **`BL-0059`** (Critical) — the same
  dormant-until-navigation-is-fixed pattern, reading past the ROM table's own bounds.

Both are **causally coupled to `BL-0047`'s own fix, not independent findings** — `BL-0047`'s
remediation is what makes `CUR_ZONE > 8` reachable at all; `BL-0058`/`BL-0059` are what make that
reachability safe. Sweep result recorded here per this skill's own mandatory-recording rule:
**not clean — two additional Critical defects found and packaged alongside the reported bug,
not silently absorbed into it and not deferred.**

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| Widen `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` to the full generated-region range (81 bytes); relocate both to avoid WRAM/SRAM collisions; regeneralize `ZONE_COLLECTS`/`zc_table` to 5 biome-family-representative lists keyed by biome-id (`BL-0058`/`BL-0059`) | [IP-9070](packages/IP-9070-cur-zone-indexed-structures-generalization.md) | `08-code-implementation` |
| Regeneralize `check_zone_transition` to read `REGION_GRAPH`'s neighbor bytes instead of hardcoded `CUR_ZONE` arithmetic (`BL-0047`) | [IP-9050](packages/IP-9050-generated-world-navigation-fix.md) | `08-code-implementation` |
| Fix `check_save_valid`'s `MM_CURSOR`-reset side effect clobbering the player's own MAIN MENU toggle (`BL-0048`) | [IP-9060](packages/IP-9060-main-menu-cursor-fix.md) | `08-code-implementation` |

**Split rationale:**

- **`IP-9070` split out from `IP-9050`, but sequenced as a hard prerequisite, not an independent
  parallel package.** Both are instances of "make a `CUR_ZONE`-indexed structure honor the
  generated world's real size," but they touch entirely different concerns (WRAM/SRAM layout +
  save-format version vs. navigation control flow) and have independently testable Definitions of
  Done. They are **not** parallel-eligible the way `IP-1040`/`IP-1050` were, though: `IP-9050`
  activating `CUR_ZONE > 8` before `IP-9070` widens the structures that index it would ship the
  exact corruption this sweep exists to prevent. `IP-9050`'s own Dependencies field names `IP-9070`
  explicitly for this reason — this is a correctness-ordering dependency, not a convenience one.
- **`SCOREITEM_FLAGS` and `ZONE_COLLECTS` fused into one package (`IP-9070`)**, not split further,
  because they are the same class of defect (a `CUR_ZONE`-indexed structure sized/shaped for the
  old 9-zone model) found by the same sweep, and a single Definition of Done — "every
  `CUR_ZONE`-indexed WRAM/ROM structure is safe across the full `scale²` region range" — covers
  both without the awkwardness of an intermediate half-fixed state.
- **`IP-9060` split out from `IP-9050`/`IP-9070`** because it is a wholly unrelated defect (MAIN
  MENU cursor logic) in the same file (`asm_game.py`) purely by coincidence of module boundaries —
  no shared root cause, no dependency in either direction, genuinely parallel-eligible with the
  other two.

### Sequencing summary

**`IP-9070` is this tranche's prerequisite** — `IP-9050` depends on it (correctness, not merely
convenience: see split rationale above). `IP-9060` is independent of both and parallel-eligible.
Critical path: **`IP-9070` → `IP-9050`** (2 packages). No package in this tranche is `08-content-
authoring` scope (WRAM/SRAM layout and control-flow only, no tile/palette/screen changes).

### Backlog riders honored in this pass

- **`BL-0047`** (Critical, navigation ignores `REGION_GRAPH`): packaged as `IP-9050`.
- **`BL-0048`** (High, MAIN MENU cursor unreachable): packaged as `IP-9060`.
- **`BL-0058`**/**`BL-0059`** (Critical, discovered by this pass's own mandatory supersession
  sweep): packaged as `IP-9070`, sequenced as `IP-9050`'s hard prerequisite.
- **`BL-0019`** (ROM/SRAM-headroom watch): `IP-9070` grows SRAM usage (9→81 bytes, ×1, net +72
  bytes) — carries an `NFR-4200` headroom re-affirmation checklist item.

## Maze-shaped region adjacency (`FS-107`/`FS-108`, planned 2026-07-11)

Two tranches's worth of specified work, planned together since the second (`FS-108`) is a direct
functional dependent of the first (`FS-107`): `FS-107` (`FEAT-9100`, `ADR-0012`'s maze-generation
decision) and `FS-108`'s logic half (`FEAT-2100`, blocked-edge classification — rendering half not
planned this pass, see below).

### Verb inventory

`FS-107` (`FEAT-9100`) is pure **generate** — `render`/`navigate`/`persist`/`review` all get an
explicit deferral-not-applicable note (`IP-1070` §7): `dsr_p`/`draw_region_arrows`/
`check_zone_transition` already consume `REGION_GRAPH` generically and need zero changes
(`ADR-0012` point 2, confirmed by direct re-read); `REGION_GRAPH` is never persisted; no new
content is authored. `FS-108`'s logic half (`FEAT-2100`) is pure **render** — `generate` is
`FS-107`'s own scope (a hard dependency, not this tranche's to redo); `navigate`/`persist` don't
apply; `review` doesn't apply to the logic-only package (no new visible tile drawn yet), though it
will apply to the eventual rendering-half package once `BL-0068` resolves.

### Supersession sweep

Neither package retires an existing model — `FS-107` is new generation logic layered onto an
unchanged biome-assignment pass (`ADR-0012` point 1: "entirely unchanged"); `FS-108`'s logic half
extends `draw_region_arrows`'s existing 2-state branch into a 3-state one without removing the
open-edge case. Both packages' own mandatory sweeps (run per this skill's own rule regardless) are
recorded in full in `IP-1070`§7/`IP-1080`§7 — summary: `dsr_p`/`draw_region_arrows`/
`check_zone_transition`/`tilemaps.py` all confirmed to have no full-lattice-connectivity
assumption baked in; `test_rom.py`'s existing `T12` suite (`T12.c`/`T12.d`) confirmed, by direct
read (`test_rom.py:799–819`), to already iterate only *existing* neighbor entries — **needs no
change** for either package, a genuine "found nothing" result, not silence.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| Spanning-tree carve (randomized DFS/recursive backtracker) + canonical-edge braid/prune pass, `generate_world`'s new second pass; `worldgen.py` oracle mirror (`FR-9140`/`FR-9150`) | [IP-1070](packages/IP-1070-maze-shaped-region-adjacency.md) | `08-code-implementation` |
| Render-time open/blocked/absent edge classification inside `draw_region_arrows`, logic half only (`FR-2330`, partial) | [IP-1080](packages/IP-1080-maze-aware-edge-classification.md) | `08-code-implementation` |

**Split rationale:**

- **One package for `FS-107`, not split further.** The spanning-tree carve and the braid/prune
  pass are two steps of one algorithm operating on the same data in the same routine, with one
  coherent Definition of Done ("`REGION_GRAPH` holds a maze, not a full lattice, with reachability
  preserved") — splitting them would create an intermediate, untestable half-state (a tree with no
  braid pass is not what `FR-9140` specifies).
- **`IP-1080` split out from `IP-1070`**, sequenced as a hard dependent, not fused into one
  package, because they implement two different Features (`FEAT-9100` vs. `FEAT-2100`) owned by
  two different Epics (`EP-5000` vs. `EP-1000`) with independently statable Definitions of Done —
  mirroring `IP-9070`→`IP-9050`'s own precedent of splitting causally-coupled work along Feature
  boundaries rather than fusing it for convenience.
- **`FS-108`'s rendering half is deliberately not packaged this pass.** `BL-0068` (the `GDS-08`
  tile-art delta) has not resolved — packaging a rendering interface ahead of that decision would
  mean guessing at tile/palette allocation this stage has no authority to invent (this skill's own
  SHALL-NOT-modify-specs-around-a-gap rule). `IP-1080` covers only the closeable logic half;
  FS-108's own Acceptance Criterion 4 (the visual claim) stays explicitly open in `IP-1080`'s own
  Definition of Done (§10) rather than silently implied covered.

### Sequencing summary

**`IP-1070` is this tranche's own prerequisite** — `IP-1080` depends on it reaching `VERIFIED`
(not merely `COMPLETE`, per this skill's own `READY` convention), since there is no maze-blocked
case to classify before a maze exists. Critical path: **`IP-1070` → `IP-1080`** (2 packages, the
tranche's full extent — no parallel-eligible package this pass). Both are `08-code-implementation`
scope (no tile/palette/screen changes in either — `IP-1080`'s own classification branch is a
no-op render-wise until the rendering half ships).

### Backlog riders honored in this pass

- **`BL-0064`** (maze-shaped region adjacency): packaged as `IP-1070`.
- **`BL-0065`** (braid-fraction parameter): folded into `IP-1070` (same generation pass, per
  `FS-107`'s own scope — not a separate package).
- **`BL-0067`** (3-state edge indicator): logic half packaged as `IP-1080`; rendering half remains
  riding `BL-0068`, not packaged this pass.
- **`BL-0068`** (the `GDS-08` tile-art delta `FEAT-2100`'s rendering half needs): **not resolved
  by this pass** — still rides a future `03-architecture-design-synthesis` invocation, named
  explicitly rather than silently absorbed into `IP-1080`.
- **`BL-0019`** (ROM/WRAM-headroom watch): `IP-1070` adds up to 84 bytes of new transient WRAM
  scratch at `scale=9` — carries an `NFR-4200` headroom re-affirmation checklist item.

## Movement/pickup/UI bug-remediation tranche (`BL-0049`/`BL-0051`/`BL-0052`/`BL-0053`, planned 2026-07-11)

Four standing, unpackaged backlog entries, each already carrying a reproduced root cause and a
recommended remediation shape from prior triage (three filed via `00-intake` this session, one —
`BL-0053` — likewise). None depends on the maze-shaped-adjacency thread or the five packages
awaiting fresh-session verification; all four are independently plannable and, once authorized,
independently implementable.

### Verb inventory

Not applicable — none of these four touches a multi-verb capability (generate/render/navigate/
persist/review). Each is a narrow, single-function correctness fix: `handle_play_input`'s own
movement-clamp arithmetic (`BL-0051`/`BL-0052`), `check_collisions`' own pickup-overlap arithmetic
(`BL-0053`), and `save_screen`'s own static tilemap content (`BL-0049`). No verb-inventory gap risk
of the `BL-0054` kind exists at this granularity.

### Supersession sweep

None of these four bugs retires or supersedes an existing model — each corrects a magic-constant/
threshold defect within an already-generalized routine (`handle_play_input`/`check_collisions`
already operate identically across every generated world; `save_screen` is static content, not
dispatched by any generalized model). Per this skill's own mandatory discipline (including the
`BL-0071`-established extension to check `test_rom.py` itself, not just production call sites), a
sweep was still run:

- **`BL-0051`/`BL-0052` (movement clamps):** `grep` for `CP_n(17)`/`CP_n(160)` and their sibling
  magic bounds (`CP_n(156)`, `CP_n(128)`, `CP_n(129)`, `CP_n(0xFF)`) across `asm_game.py` found no
  other call site referencing these two specific clamp constants — `handle_play_input`'s own four
  directional blocks (`asm_game.py:512-545`) are the only place `PLAYER_X`/`PLAYER_Y` are
  clamped by direct movement (as opposed to `check_zone_transition`'s separate, correct,
  already-`REGION_GRAPH`-driven edge-detection constants at `156`/`0`/`18`/`128`, which this
  tranche does not touch). **Found in `test_rom.py`, not production code:** `T7.8` (`test_rom.py:
  477-482`) directly asserts the *current buggy* UP floor (`17`) as if it were correct behavior
  ("movement floor is Y=17 (zone 0 = top row, no up-transition)") — this test will fail once
  `BL-0051` ships unless updated in the same package. `T7.10`'s own comment ("X capped at 159")
  is similarly stale once `BL-0052` ships (real cap becomes `152`), though the check's own
  assertion (`x<=159`) happens not to break numerically since it forces `X=159` directly rather
  than deriving it via the clamp — flagged for a comment correction, not a behavior-changing fix.
- **`BL-0053` (pickup hitbox):** `grep` for `CP_n(10)` across `asm_game.py` found exactly the two
  instances `check_collisions`' own X/Y overlap test uses (`asm_game.py:573`/`578`) — no other
  routine reuses this threshold. In `test_rom.py`, every existing `T8` pickup check places the
  player at the item's own exact `(x, y)` coordinates (`dx=dy=0`) — well inside any reasonable
  bounding-box definition — so **no existing test assumes the old symmetric window's specific
  asymmetry; the sweep found nothing to fix, only new boundary-exactness checks to add.**
- **`BL-0049` (SAVE screen text):** `grep` for `save_screen`/`GS_SAVE`/`st_save` across
  `asm_game.py`/`tilemaps.py`/`test_rom.py` found no existing test exercises the SAVE screen's own
  tilemap content at all (only `T14.d0`'s state-transition check reaches `GS_SAVE`, asserting
  nothing about what's drawn there) — nothing to break, a pure content addition.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| Correct `handle_play_input`'s UP/RIGHT movement-clamp magic bounds to match the already-correct DOWN/LEFT pattern (`BL-0051`/`BL-0052`); update `T7.8`'s own stale-floor assertion and `T7.10`'s stale comment | [IP-9090](packages/IP-9090-movement-clamp-boundary-fix.md) | `08-code-implementation` |
| Correct `check_collisions`' pickup-overlap test from a symmetric ±9/±9 window to a true axis-aligned bounding-box overlap test against the sprite's real 8×16 extent (`BL-0053`) | [IP-9100](packages/IP-9100-collectible-pickup-hitbox-fix.md) | `08-code-implementation` |
| Add on-screen text for the SAVE screen's third (SELECT) option, currently silent (`BL-0049`) | [IP-9080](packages/IP-9080-save-screen-third-option-labeling.md) | `08-content-authoring` |

**Split rationale:**

- **`BL-0051`/`BL-0052` fused into one package (`IP-9090`)** — same function
  (`handle_play_input`), same class of defect (a magic clamp bound inconsistent with its own
  already-correct sibling direction), one coherent Definition of Done ("every directional clamp
  matches its own established-correct sibling pattern"), following `IP-9070`'s own precedent for
  fusing same-class-same-sweep defects rather than splitting further.
- **`BL-0053` split out from `IP-9090`** despite sharing `asm_game.py` as a file, because it is a
  different function (`check_collisions`, not `handle_play_input`), a different root-cause class
  (an overlap-test formula, not a magic boundary constant), and independently testable/rollback-
  able — no shared root cause with the movement clamps beyond incidental file co-location.
- **`IP-9080` split out from both `08-code-implementation` packages** because it is
  `08-content-authoring` scope (a `tilemaps.py` data-only change — `st_save`'s own input-handling
  logic, `asm_game.py:319-339`, already correctly implements the SELECT option's save-and-exit
  behavior; only the missing on-screen text needs adding), a different stage-08 peer entirely, and
  genuinely parallel-eligible with the other two.

**UI-input-mapping question resolved directly (per this entry's own disposition note, citing
`FS-104` OQ2's established precedent):** keep the existing `A`/`B`/`SELECT` one-button-per-option
scheme unchanged — do **not** redesign it into a cursor-based UP/DOWN-select/A-confirm scheme
matching MAIN MENU's own convention. Rationale: the existing scheme already works correctly and
is a single-screen, three-fixed-option menu (not a growing/reorderable list, unlike MAIN MENU);
redesigning the input model to fix a missing *label* would be solving a problem the user never
reported (the report is specifically "no on-screen text," not "the controls are confusing") and
would touch `st_save`'s already-correct, already-tested control flow for no behavioral gain — out
of proportion to the actual defect. `IP-9080`'s own scope is therefore text-only, no
`asm_game.py` change.

### Sequencing summary

All three packages are mutually independent (three different root causes, three different
Definitions of Done, two different files with no shared symbol) — fully parallel-eligible, no
critical path within this tranche. None depends on the maze-shaped-adjacency thread, the five
packages awaiting fresh-session verification, or each other.

### Backlog riders honored in this pass

- **`BL-0051`**/**`BL-0052`** (movement-clamp magic-bound defects): packaged as `IP-9090`.
- **`BL-0053`** (pickup-hitbox asymmetric window): packaged as `IP-9100`.
- **`BL-0049`** (SAVE screen's silent third option): packaged as `IP-9080`; the entry's own
  UI-input-mapping open question resolved directly above, not escalated.
- **`BL-0071`** (supersession-sweep-must-include-`test_rom.py` discipline, filed after `IP-1070`):
  honored directly in this pass's own sweep above (`T7.8`/`T7.10` checked and one real conflict
  found and routed into `IP-9090`'s own scope).

## `gw_prng_step` mixing-step repair (`BL-0074`/`ADR-0014`, planned 2026-07-11)

One package: the core PRNG fix `ADR-0014` decided and the user explicitly authorized (2026-07-11,
"Yes, ship the fix"). No FS — this is a repair to an already-shipped, `VERIFIED` (`IP-1020`)
routine's own internal algorithm, not a new capability; the observable contract (`gw_prng_step`'s
own `TMP1:TMP2` in/out interface, called once per biome-assignment region and repeatedly within
`IP-1070`'s maze pass) is unchanged.

### Verb inventory

Not applicable — a single-routine algorithmic repair, not a multi-verb capability.

### Supersession sweep

Run directly (per `BL-0071`'s own extension of this discipline to `test_rom.py`, not just
production call sites): every `test_rom.py` check that depends on `worldgen.py`'s `generate()`
compares its output against the **live SM83 output for the same `(seed, scale)` pair**
(`T12.a/b`, `T19.c`, `T5.9`, `T11.a`'s own region-0 star position, `T17`'s DFS-tour checks) — none
hardcodes a literal expected biome-id/neighbor byte sequence independent of the oracle. Since this
package updates `worldgen.py`'s own `_step` function in the same lockstep discipline
`ADR-0012`/`ADR-0013` already established, every one of these checks continues to pass
automatically once both sides change together — **no test needs its own hardcoded values
updated**, only the shared oracle algorithm. `T12.f` (seed=0 normalization) hooks *before* any
`gw_prng_step` call and asserts a property of `ADR-0010`'s own normalization step, not of the
mixing algorithm — unaffected either way. **Sweep result: clean, nothing to update beyond the
oracle mirror itself (already this package's own §6 task).**

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| Repair `gw_prng_step`'s mixing step to the period-sound `7,9,8` shift triplet; bump `SAVE_VERSION_VAL`; update `worldgen.py`'s oracle mirror in lockstep; re-measure `ADR-0013`'s own maze-pass perturbation's continued necessity; add a non-degeneracy statistical check (`BL-0074`) | [IP-9110](packages/IP-9110-gw-prng-step-mixing-step-repair.md) | `08-code-implementation` |

**No split** — one routine, one coherent Definition of Done ("the shipped PRNG no longer
degenerates for any seed in a representative corpus"), a single `asm_game.py`/`worldgen.py`/
`test_rom.py` change set with no independently-shippable sub-piece.

### Sequencing summary

No dependency on any other in-flight package this session. Independent of the (exhausted)
movement/pickup/UI tranche and the (blocked/unauthorized) maze-shaped-adjacency tranche's
`IP-1080`. Touches `gw_prng_step`, which `IP-1070`'s own maze pass calls — but `IP-1070` is
`COMPLETE`, not yet `VERIFIED`, so this package's own change to the routine `IP-1070` depends on
is a real (if narrow) risk surface, named explicitly in Risks below rather than silently assumed
safe.

### Backlog riders honored in this pass

- **`BL-0074`** (default-seed/effectively-all-seeds biome-flooding, root-caused and architecturally
  decided this session): packaged as `IP-9110`.
- **`BL-0071`**/**`BL-0073`** (supersession-sweep-must-include-`test_rom.py`; planning-formula
  verification-against-reproduction-data): both honored directly in this pass (see Supersession
  sweep above; the `7,9,8` triplet's own non-degeneracy was verified against a 2000-seed corpus
  before this package was written, not merely asserted from `ADR-0014`'s own citation).

## RIGHT zone-transition regression (`BL-0076`, planned 2026-07-12)

One package: a single boundary-constant fix in `check_zone_transition`, a direct regression from
this session's own `IP-9090`. No FS — this repairs an already-shipped, already-`COMPLETE`
routine's internal threshold, not a new capability; `check_zone_transition`'s own interface and
every other direction's behavior are unchanged.

### Verb inventory

Not applicable — a single-constant boundary fix, not a multi-verb capability.

### Supersession sweep

Run directly, extended per this bug's own root-cause class (a magic-number boundary constant that
drifted out of sync with a sibling constant elsewhere in the same file — exactly the class of gap
`IP-9090`'s own supersession sweep should have, but did not, catch): grepped `asm_game.py` for
every `CP_n(156)`, `CP_n(152)`, `CP_n(153)`, `CP_n(159)`, `CP_n(160)` occurrence. **Exactly two
hits, both already accounted for**: `handle_play_input`'s own RIGHT clamp (`asm_game.py:518`,
`CP_n(153)`, correctly fixed by `IP-9090`) and `check_zone_transition`'s own RIGHT-edge trigger
(`asm_game.py:662`, `CP_n(156)`, this package's own target). No third call site carries the same
latent inconsistency (`draw_region_arrows`' `ARROW_ADDR_R` is a fixed VRAM tilemap offset,
unrelated to `PLAYER_X`; `update_oam`'s own OAM-X write is a flat `+8` sprite-offset add, not a
boundary comparison). Extended to `test_rom.py` per `BL-0071`'s own established discipline:
`T7.10`/`T17.c1`/`T11.a2` all use a memory-forced `PLAYER_X` value (`159`, `159`, `156`
respectively) at or above the *new* threshold (`152`) as well as the old one — none needs updating,
each remains correct under the new comparison for the reason it was written (a true grid-boundary
region with no right neighbor, or a value comfortably above either threshold). **Sweep result:
clean — exactly one other file location shares the old constant, and it's this package's own
target, not an overlooked duplicate.**

**Broader test-coverage gap found, named but not fixed by this package** (a `BL-0071`/`BL-0073`-
class process finding, not this package's own scope-creep): no existing `test_rom.py` check
confirms a zone transition actually *fires* via genuine, real button-press-driven walking, in any
of the four directions — every existing "did the zone change" check (`T11.a2`, `T17.a`, `T19.*`)
uses memory-forced `PLAYER_X`/`PLAYER_Y` teleportation to isolate the transition logic from the
movement clamp, which is legitimate for *their* own purpose (testing `check_zone_transition` in
isolation) but is exactly the reason this regression shipped undetected — no test exercises the
*combination* of the real movement clamp and the transition threshold together. This package adds
that missing case for RIGHT (`BL-0076`'s own direction); UP/DOWN/LEFT remain covered only
indirectly (their clamp/threshold pairs are separately confirmed consistent, see the package's own
§4) — a full real-button-press positive-transition sweep across all four directions is recommended
as a future, low-urgency `07` pass, not required here.

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| Fix `check_zone_transition`'s RIGHT-edge threshold (`CP_n(156)`→`CP_n(152)`) to match `IP-9090`'s corrected movement clamp; add a real-button-press regression test (`BL-0076`) | [IP-9120](packages/IP-9120-right-zone-transition-threshold-fix.md) | `08-code-implementation` |

**No split** — one comparison operand, one coherent Definition of Done ("a real, sustained
rightward button-press walk crosses into an open right-neighbor zone"), a single `asm_game.py`/
`test_rom.py` change set with no independently-shippable sub-piece.

### Sequencing summary

No dependency on any other in-flight package this session — `check_zone_transition`'s only
functional dependency is `IP-1010`'s own bootstrap (`VERIFIED`) and the already-`COMPLETE`
`IP-9050`/`IP-9090` (both touch the same function/its caller; this package's own diff is additive
to `IP-9090`'s, not a conflict). Independent of `IP-9110` (touches `gw_prng_step`, a disjoint
routine) and the blocked/unauthorized `IP-1080`.

### Backlog riders honored in this pass

- **`BL-0076`** (Critical, RIGHT zone-transition regression — root-caused and reproduced this
  session): packaged as `IP-9120`.
- **`BL-0071`** (supersession sweep must include `test_rom.py`): honored directly above.

## Spurious zone-transition regression (`BL-0078`, planned 2026-07-12)

One package: `check_zone_transition`'s own trigger model gains an intent gate. No FS — this
repairs an already-shipped, already-`COMPLETE` routine's decision logic, not a new capability;
its interface and every direction's *legitimate* transition behavior are unchanged.

### Verb inventory

Not applicable — a single-routine gating fix, not a multi-verb capability.

### Supersession sweep

Run directly, per this bug's own root-cause class (a routine whose trigger condition changed
scope — position-only → position-and-intent — needs every caller of that routine, test or
production, re-examined for an assumption the old, looser condition let slide). Confirmed by
direct code read: `check_zone_transition`'s four branches (`asm_game.py:660-701`) are symmetric —
none tests player input today, so the defect the user reported for RIGHT applies identically, by
construction, to LEFT/UP/DOWN. The fix therefore gates all four uniformly, not just RIGHT.

Swept `test_rom.py` for every `pb.memory[PLAYER_X] = …`/`pb.memory[PLAYER_Y] = …` write followed
by ticking (a potential transition trigger) with **no accompanying `button_press`/`button_release`
for the matching direction**:

- **`T11.a2`** (`test_rom.py:784-798`): forces `PLAYER_X`/`PLAYER_Y` directly to a boundary value
  and ticks, with no button held at all. **Needs updating.**
- **`_t17_do_move`** (`test_rom.py:1601-1615`): the shared helper behind `T17.a`, `T17.b2`, and
  `T17.b5` — teleports the player to a boundary and ticks, no button held. **Needs updating** (one
  fix here covers all three call sites/every check that depends on it).
- **`T17.c1`/`T17.c2`** (`test_rom.py:1675-1684`): force a boundary position with no open
  neighbor (region 24, a true grid boundary), asserting *no* transition occurs. Correct under
  either the old or the new gate (blocked by the missing neighbor either way) — **no update
  needed**, confirmed by direct trace, not assumed.
- Every other `PLAYER_X`/`PLAYER_Y` write in the file (item-pickup positions, save/load
  round-trip checks, state-reset positions between test blocks — `test_rom.py:404, 456, 496, 507,
  520, 527, 552, 593–625, 699, 729–730, 813, 1219–1239, 1307, 1368–1370, 1428, 1638, 1722–1727`)
  either already accompanies a real button hold (`T7.9`–`T7.11`) or targets an interior,
  non-boundary position with no transition in play — confirmed clean by direct read of each.
  **Correction to this bug's own intake framing**: the intake report speculated "several `T16`
  `CUR_ZONE`-forcing patterns" might be affected — direct sweep found `T16` uses
  `force_region_redraw` (sets `CUR_ZONE`/`NEED_REDRAW` directly, never `PLAYER_X`/`PLAYER_Y`) for
  an unrelated purpose (isolating collection behavior in a specific region), not transition
  testing — `T16` is unaffected, not merely assumed clean.

**Why `JOY_CUR`, not `JOY_NEW`**: `handle_play_input` itself gates continuous movement on
`JOY_CUR` (held state), not `JOY_NEW` (edge-triggered, newly-pressed-this-frame) — a player
walking into a boundary over several held-frames should transition on whichever frame position and
input coincide, not only the literal first frame the direction was pressed (which may have
happened many frames and pixels earlier). `check_zone_transition` runs every frame regardless of
`NEED_REDRAW`, so this holds regardless of frame timing. Consistency with the movement routine it
directly follows in `st_playing`'s own per-frame sequence is the deciding factor.

**Test methodology fix, not a `JOY_CUR` memory poke**: `JOY_CUR` (`asm_game.py:32`) is written
every frame by `read_joypad` (`asm_game.py:477`) from PyBoy's own real (virtual) hardware button
state — a raw `pb.memory[JOY_CUR] = …` poke would be overwritten by the very next tick's joypad
read, before `check_zone_transition` ever sees it, whenever more than one tick separates the poke
from the check. The correct test-side fix is a real `pb.button_press(<dir>)` held across the
teleport-and-settle window (exactly `T7.9`–`T7.11`'s own already-working pattern) — the teleport
still gives instant positioning (no need to simulate pixel-by-pixel walking), the held button
satisfies the new gate honestly.

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| Gate `check_zone_transition`'s four branches on the corresponding `JOY_CUR` direction bit; update `T11.a2`/`_t17_do_move` to hold the matching button; add a direct `BL-0078` regression test (`BL-0078`) | [IP-9130](packages/IP-9130-zone-transition-intent-gate.md) | `08-code-implementation` |

**No split** — one routine, one coherent Definition of Done ("a zone transition fires only when
the player is actually pressing the corresponding direction, in addition to being positioned at
the edge"), a single `asm_game.py`/`test_rom.py` change set with no independently-shippable
sub-piece; the test-suite ripple is two call sites, not a separable body of work.

### Sequencing summary

No dependency on any other in-flight package this session — `check_zone_transition`'s only
functional dependency is `IP-1010`'s own bootstrap (`VERIFIED`) and the already-`COMPLETE`
`IP-9050`/`IP-9120` (both touch the same routine; this package's own diff is additive/corrective,
not a conflict). Independent of `IP-9110` (`gw_prng_step`, disjoint) and the blocked/unauthorized
`IP-1080`.

### Backlog riders honored in this pass

- **`BL-0078`** (High, spurious zone-transition regression — root-caused and reproduced at
  intake): packaged as `IP-9130`.
- **`BL-0071`** (supersession sweep must include `test_rom.py`): honored directly above.

## Maze-blocked edge indicator — rendering half (`FS-108`/`FEAT-2100`/`BL-0075`, planned 2026-07-12)

`FS-108`'s own last Open Question closed 2026-07-12 (`06-feature-specification`): the rendering
half's workflow and Acceptance Criteria (Workflow C, AC-4/AC-5) are now fully specified. This
tranche packages that spec — `IP-1080`'s own classification logic (`VERIFIED`) is untouched;
this pass wires the visible result.

### Verb inventory

Pure **render** — `generate` is `FS-107`'s own closed scope; the classification decision this
rendering consumes is `IP-1080`'s own closed scope (`navigate` doesn't apply); `persist` doesn't
apply (no new WRAM/SRAM entity, `FS-108` §10); `review` **does** apply this time (unlike
`IP-1080`'s own logic-only pass) — new visible tile art ships, so a `09-content-review` pass is
owed after implementation, mirroring `IP-1031`'s own precedent as `FEAT-6100`'s exercise.

### Supersession sweep

Not applicable in the retirement sense — this pass adds a third rendered state, it retires
nothing. Confirmed by direct code read: `draw_region_arrows`'s existing open-edge branch
(`asm_game.py:1002-1013`) and `_arrow_write` helper are unchanged targets, not superseded;
`TL_ARROW_U/D/L/R`'s own tile-index block (`tiles.py:36-39`) is untouched, the new tiles land at
the confirmed-free `0x1A`-`0x1D` slots immediately after it. Swept `test_rom.py`'s existing `T20`
suite (`T20.a`/`b`/`c`) for any assumption that would break once a `blocked` edge starts drawing a
non-blank tile: `T20.b`/`T20.c` both currently assert `not arrow_present` (`ARROW_POS[direction]
== ARROW_TILE[direction]`, the *open*-tile constant) for blocked/absent — that assertion remains
correct unchanged (a blocked tile is not the open tile), but needs a **new**, additive assertion
for the blocked case specifically (the tile now *is* the new blocked-tile constant, not blank) —
recorded as this package's own `Tests to Add`, not a rewrite of the existing check.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| 4 new tile bitmaps (`TL_BLOCKED_U`/`D`/`L`/`R`, `0x1A`-`0x1D`, a short broken/dashed bar per `GDS-08` §10's silhouette concept) registered via `build_tile_data()`'s existing `put()` convention | [IP-1081](packages/IP-1081-maze-blocked-edge-indicator-content.md) | `08-content-authoring` |
| `draw_region_arrows`'s blocked-case render branch: for each direction already classified `blocked` by `IP-1080`'s own arithmetic (`DRA_ROW`/`DRA_COL` vs. `WORLD_SCALE`), write the direction's new tile at the existing `ARROW_ADDR_*` position (palette 2, reusing `_arrow_write`'s own write shape) instead of the current no-op | [IP-1082](packages/IP-1082-maze-blocked-edge-indicator-render.md) | `08-code-implementation` |

**Split rationale:**

- **Two packages, mirroring `IP-1030`/`IP-1031`'s own code/content peer-split precedent** for the
  same FS (`FS-103`) — different stage-08 peers own different files (`tiles.py` vs. `asm_game.py`),
  and the tile art half genuinely needs its own `09-content-review` pass this time (unlike
  `IP-1080`, which shipped no visible art at all).
- **Content package first, reversing `IP-1030`→`IP-1031`'s own ordering** — there, the code half
  established the interface the content half plugged into; here, the *code* half's new render
  branch needs the *content* half's new tile-index constants (`TL_BLOCKED_U`/`D`/`L`/`R`) to exist
  before it can reference them, so the dependency runs content→code this time. Named explicitly so
  the reversal isn't mistaken for an inconsistency.
- **Not fused into one package** despite the small combined size — the code branch's own
  Definition of Done ("draws the correct tile for a `blocked` classification") is independently
  statable and testable from the content package's own DoD ("4 new tiles exist, registered, cost
  0 new palette entries") once the tile constants exist as a dependency, mirroring the same
  Feature-boundary-respecting logic `IP-1070`/`IP-1080`'s own split rationale used (here it's a
  code/content boundary, not a Feature boundary, but the same "don't fuse for convenience"
  principle applies).

### Sequencing summary

**Critical path: `IP-1081` → `IP-1082`** (2 packages). `IP-1082` depends on `IP-1081` reaching
`VERIFIED` (this skill's own `READY` convention — `COMPLETE` is not sufficient) for the tile
constants to exist; both also depend on `IP-1080` (`VERIFIED`, already shipped) for the
classification arithmetic/WRAM bytes they read. No parallel-eligible package this pass — the
dependency is a hard sequencing constraint, not a convenience ordering.

### Backlog riders honored in this pass

- **`BL-0075`** (High, maze dead-end indistinguishable from a true world edge): packaged as
  `IP-1081`→`IP-1082`, the pair that closes it — not `DONE` until `IP-1082` ships and is
  `VERIFIED`.
- **`BL-0068`** (the `GDS-08` tile-art delta this rendering half needed): already resolved
  (2026-07-11); this pass is the implementation package `BL-0068`'s own resolution note named as
  still owed.

## Win-condition redesign (`FS-102` revision, `FR-9160`/`FR-9161`, `ADR-0015`, `BL-0093`, planned 2026-07-12)

The owner's own resolved decision: `KeyItem` placement becomes selective (`WORLD_SCALE` total,
dead-end-prioritized, random-fill fallback), win condition becomes `KeyItemCount == WORLD_SCALE`.
Grounded by `FS-102`'s 2026-07-12 revision.

### Verb inventory

Spans **generate** (the new placement decision, inserted into `generate_world`'s maze-carve
pipeline) and **navigate/persist** only in the narrow sense that the victory *check*
(`check_complete`) reads live `WORLD_SCALE` state — not a new verb, an existing one (`FR-1160`'s
own victory-transition trigger, unchanged in mechanism) fed a corrected comparison operand.
`render`/`review` are explicitly deferred-not-applicable: this is pure logic and WRAM-state data,
no new tile/screen/palette content ships (confirmed by direct `KEYITEM_FLAGS` consumer read, see
Supersession sweep below) — nothing for `09-content-review` to judge.

### Supersession sweep

`FR-9160` supersedes `FR-9130`'s "exactly one `KeyItem` per region, always" assumption. Swept
every `KEYITEM_FLAGS` reader in `asm_game.py` for that assumption baked in:

- **`setup_zone_collects`** (`asm_game.py:1194-1207`): already treats any *nonzero*
  `KEYITEM_FLAGS[region]` value as "mark this region's `KeyItem` inactive" (suppress render/
  pickup) — confirmed by direct read, this is exactly the behavior an "absent" region needs too.
  **No change needed** — a genuine "found nothing to fix" result, not silence.
- **`check_collisions`** (`asm_game.py:578-620`): the `KeyItem`-pickup branch (line 609-619) only
  ever executes for an item whose `active` field (`COLL_DATA`) is already 1 — and
  `setup_zone_collects` never sets `active=1` for a region `KEYITEM_FLAGS` marks nonzero (the
  point above). **Confirmed unreachable for an absent region by construction** — no defensive
  check needed, **no change required**.
- **`save_to_sram`/`try_load_save`** (`asm_game.py:1683-1694`, `1743-1758`): both `memcpy` the
  full 81-byte `KEYITEM_FLAGS` array byte-for-byte, value-agnostic. **No change needed** if the
  chosen encoding (below) reuses `KEYITEM_FLAGS` itself rather than adding a new array.
- **`check_complete`** (`asm_game.py:728-732`): the one real hit — `CP_n(9)`, the literal
  constant this whole redesign exists to replace. **Change required** (§ package below).
- **`st_intro`/`st_victory`'s own `KEYITEM_FLAGS` reset loops**: zero the array to all-0 (meaning
  "present, uncollected" under the chosen encoding, below) — the new placement pass must
  explicitly overwrite the *absent* regions' bytes after this reset, or every region would default
  to "present" regardless of the placement decision. **Change required** (§ package below,
  Files to Modify — this is `generate_world`'s own new pass writing after the existing reset, not
  a change to the reset routines themselves).
- **`worldgen.py`'s oracle**: mirrors `generate_world` step-for-step; needs the equivalent Python
  function added. **Change required.**

### Per-region encoding decision (`GDS-07` §7c, resolved against the real code this pass)

**Decision: widen `KEYITEM_FLAGS`'s existing value domain to a tri-state (`0` = present,
uncollected; `1` = present, collected; `2` = absent) — no new WRAM/SRAM address.** Not a new,
separate presence bitmap. Grounded directly in the Supersession sweep above: both real consumers
(`setup_zone_collects`, `check_collisions`) already treat *any nonzero* value as "no active item
here," which is exactly correct for both the existing "collected" (`1`) and the new "absent"
(`2`) cases — confirmed by direct code read, not assumed. `save_to_sram`/`try_load_save` need zero
changes (value-agnostic byte copy). This is the cheaper of `GDS-07` §7c's two named candidates by
a wide margin (zero new WRAM, zero new SRAM field, zero new memcpy call) and carries none of that
section's own flagged re-audit risk, since the audit is now actually done, not merely predicted.

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| `generate_world`'s new placement pass (leaf classification + `WORLD_SCALE`-count selection + random-fill fallback, inserted between `maze_carve_done` and the braid pass), `KEYITEM_FLAGS` tri-state encoding, `check_complete`'s corrected comparison operand, `worldgen.py`'s equivalent oracle mirror | [IP-1021](packages/IP-1021-win-condition-redesign.md) | `08-code-implementation` |

**No split.** Placement and the victory-check correction are two small, tightly-coupled pieces of
one coherent Definition of Done ("the shipped game generates exactly `WORLD_SCALE`
dead-end-prioritized `KeyItem`s and wins at exactly that count") from a single ADR/FS revision —
splitting them would let one ship without the other, silently reintroducing the exact class of
defect `BL-0054`'s own precedent (this skill's own verb-inventory rule) warns against: a
`generate`-side change landing with no corresponding `navigate`/consume-side update. Unlike
`IP-1070`→`IP-1080` (split because they crossed a Feature boundary, `FEAT-9100`→`FEAT-2100`),
this work stays entirely within `FEAT-9000`/`FS-102`'s own scope.

### Sequencing summary

**No critical path — a single package, `IP-1021`.** Depends on `IP-1020` (`VERIFIED`, the
routine this extends) and `IP-1070` (`VERIFIED`, the maze-carve pass whose `GW_MAZE_STATE` this
placement decision reads) — both already shipped, no blocking dependency. Independent of the
in-flight `IP-1081`/`IP-1082` pair (disjoint files: this touches `asm_game.py`'s `generate_world`/
`check_complete` and `worldgen.py`; `IP-1081`/`IP-1082` touch `tiles.py`/`draw_region_arrows`).

### Backlog riders honored in this pass

- **`BL-0093`** (High, resolved win-condition redesign): packaged as `IP-1021`.

## SELECT Menu & Edge-Indicator Legend Screen (`FS-109`/`FEAT-1200`/`BL-0100`, planned 2026-07-13)

`FS-109` fully specifies both new states (SELECT MENU, LEGEND) with no blocking Open Questions —
its own 3 Open Questions are exactly the WRAM-byte/`GAMESTATE`-value/SELECT-while-in-menu
implementation choices this stage is meant to resolve, not upstream gaps. Resolved here (see
Work unit below): `GS_SELECT_MENU = 8`, `GS_LEGEND = 9` (the next two free `GAMESTATE` values
after `GS_SEED_SCALE_ENTRY = 7`, `asm_game.py:170,174`); the SELECT MENU cursor reuses `MM_CURSOR`
(`0xC27E`) and the generic entry-reset flag reuses `MM_JUST_ENTERED` (`0xC2D7`) rather than
allocating two new WRAM bytes — valid because `GS_MAIN_MENU` and `GS_SELECT_MENU` are never
simultaneously active (no transition connects them directly) and no code path needs both states'
cursor/entry-flag values live at once; SELECT is resolved as a plain no-op inside SELECT MENU and
LEGEND (their own input handlers simply never test `J_SELECT`, the same "only named bits act"
convention every other handler already follows — `MAP`'s own SELECT==B merge is `st_map`'s
pre-existing, unrelated choice, untouched by this pass).

### Verb inventory

Two verbs: **navigate** (the state-machine extension — `handle_play_input`'s SELECT branch
retargeted, two new state handlers, two new dispatch-table entries) and **render** (two new
static screens, no new tile art — `GDS-08` §11's own "no new tile art, no new palette entry"
decision). `generate` doesn't apply (no world-generation touch); `persist` doesn't apply (`FS-109`
§14: no SRAM/checksum obligation); `review` doesn't apply — no new visible tile *art* ships (both
screens reuse already-shipped `TL_ARROW_U`/`TL_BLOCKED_U`/text/border primitives verbatim), so no
`09-content-review` pass is owed the way `IP-1081`'s new tile bitmaps needed one.

### Supersession sweep

This pass **does** retire an existing behavior: `handle_play_input`'s SELECT branch
(`asm_game.py:536-538`) currently transitions `PLAYING` directly to `GS_MAP` in one hop; this
pass retargets it to `GS_SELECT_MENU` instead, making the old single-hop path a two-hop one
(SELECT → SELECT MENU → A("map") → MAP). Swept the tree for every call site still encoding the
old single-hop assumption:

- **`asm_game.py`**: only one call site sets `TRANSITION_TO = GS_MAP` from a SELECT press
  (`handle_play_input:536-538`) — confirmed the sole site to retarget. `st_map` itself
  (`asm_game.py:368-373`, its own pre-existing `SELECT` == `B` exit-to-`PLAYING` merge) is a
  different, downstream behavior — once *inside* `MAP`, not a path *into* it — and is explicitly
  unchanged (`FEAT-1200`'s own Scope: `MAP`'s content/behavior is untouched).
- **`test_rom.py`** (found, not clean — recorded as this pass's own `Tests to Modify`, not
  silently absorbed): three existing sites simulate a bare `SELECT` press from `PLAYING` and
  assert an immediate `GAMESTATE == GS_MAP` (4), which breaks once `SELECT` lands in
  `GS_SELECT_MENU` (8) instead: **T4.6** (`test_rom.py:297-298`), **T8.11**
  (`test_rom.py:694-695`), and **T14.e2**'s runtime negative-test sweep (`test_rom.py:1362-1366`,
  which drives `PLAYING`→`SELECT`→`MAP`→`B`→`PLAYING`→`SELECT`(enter)→`SELECT`(exit, exercising
  `MAP`'s own merge) as part of its systematic input-branch coverage). All three need an inserted
  `A` press between the `SELECT` press and the `MAP`-state assertion/traversal; none needs its own
  *intent* changed, only the added hop. Assigned to `IP-1090`'s own Tests to Add/Modify, per this
  skill's own "recorded, not silently planned around" rule.
- **`docs/`**: no other document encodes the old single-hop path as fact — `FR-1150`'s Notes
  already carries the forward-pointer to `FR-1200` (`04-requirements-engineering`, 2026-07-13),
  and `GDS-01` §4c/`GDS-08` §11 already document the two-hop target state directly. Nothing to
  correct upstream.

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| State-machine extension (`GS_SELECT_MENU`/`GS_LEGEND` constants, dispatch-table entries, `handle_play_input`'s SELECT retarget, `st_select_menu`/`st_legend` handlers, `sm_on_entry`/`draw_select_menu_cursor` reusing `MM_CURSOR`/`MM_JUST_ENTERED`) plus two new static screens (`select_menu_screen()`, `legend_screen()` in `tilemaps.py`, both reusing existing text/border/tile primitives, no new art) plus the three existing-test corrections the supersession sweep found | [IP-1090](packages/IP-1090-select-menu-edge-indicator-legend-screen.md) | `08-code-implementation` |

**Split rationale:** one package, mirroring `IP-1040`'s own precedent (`FEAT-1100`'s MAIN MENU +
SEED/SCALE ENTRY: two new states plus two new screens, no code/content peer split) rather than
`IP-1030`/`IP-1031`'s split — that split existed *because* new tile art needed its own
`09-content-review` pass; here `GDS-08` §11 explicitly commits to zero new tile art, so there is
no content-authoring half to separate out. The navigate and render verbs stay fused in one
package because they are not independently completable: the new screens have no dispatch path to
reach them without the state-machine half, and the state-machine half has nothing to transition
*to* without the screens existing.

### Sequencing summary

**No critical path — a single package, `IP-1090`.** Depends on `FEAT-1000`'s existing state
machine (as-built, shipped Baseline — predates this project's `IP-xxxx` numbering, no dedicated
package), `IP-1040`/`FEAT-1100`'s cursor-menu convention
(`VERIFIED`, reused not reinvented), and `FEAT-2100`'s already-shipped `TL_ARROW_U`/`TL_BLOCKED_U`
tiles (`IP-1030`/`IP-1081`, both `VERIFIED`) — all dependencies already `VERIFIED`, none blocking.
Independent of `IP-1082`'s own pending verification (a content dependency on already-shipped
tiles, not a build-order dependency on `IP-1082`'s still-unverified render branch, per `FS-109`
§17/`FEAT-1200`'s own catalog entry) and independent of the still-undecided `BL-0082`
streaming-generation thread.

### Backlog riders honored in this pass

- **`BL-0100`** (project owner request, edge-indicator legend screen): packaged as `IP-1090` —
  not `DONE` until `IP-1090` ships and is `VERIFIED`.

## Infinite Mode (`FS-110`/`FEAT-10000`/`EP-6000`, planned 2026-07-14)

`FS-110`'s two named upstream blockers (`BL-0111`, missing `FEAT-4100` catalog dependency;
`BL-0113`, mode-selection UI shape) are both resolved (`05-feature-decomposition`,
`GDS-01` §4d). Of the 8 Open Questions `FS-110` itself raises, this pass resolves five as
implementation-level choices per the FS's own explicit routing (`OQ2` density constant `K`,
`OQ4` no spawn-region special case, `OQ5` ledger capacity/eviction, `OQ7` save-format version
value, `OQ8` materialized-window sizing) and leaves **`OQ3` (the run-end trigger for the top-3
comparison) genuinely unresolved**, exactly as `FS-110` itself routes it — `04-requirements-
engineering` or a direct user decision, not `07`. `OQ1` (rendering-integration mechanism) is
resolved by direct investigation of the shipped code (below), not assumed.

**Rendering-integration finding (`OQ1`, resolved by direct code read, not assumed):**
`dsr_p` (`asm_game.py:951-988`) reads a **biome-id value into register A** from
`REGION_GRAPH + region*5`, then branches purely on that value (`0-4`) into the shared
`dsr_p_water`/`sand`/`grass`/`stone`/`brick` → `dsr_p_copy` → `copy_screen` path — **this half is
already decoupled from `REGION_GRAPH`'s own storage**: any routine that places a biome-id `0-4`
into A before jumping to `dsr_p` gets the correct tileset drawn, with zero `FEAT-4100` code
changes needed. **`draw_region_arrows` (`asm_game.py:1040` on) is not similarly reusable** — it
re-derives `row`/`col` via `CUR_ZONE`/`WORLD_SCALE` division (`asm_game.py:1061-1069`, a
finite-mode-only concept Infinite Mode has no equivalent of) and reads 4 **neighbor-region-index**
bytes (`0xFF`=none) at the HL address `dsr_p` pushes, distinguishing a maze-pruned edge from a
true grid boundary via that same `row`/`col` (`ADR-0012` point 2). Infinite Mode's connectivity is
a 4-bit open/closed nibble per region (no neighbor-index concept, no grid boundary — every
direction always has a grid-adjacent region in an unbounded world), so this routine cannot be
reused as-is. **Resolution:** `dsr_p`'s biome-dispatch half is reused verbatim (Infinite Mode
jumps into it directly with a freshly-computed biome-id in A); a new, parallel
`draw_region_arrows_inf` routine is written, reading the current region's own connectivity nibble
(§ per-region materialization, below) instead of `REGION_GRAPH` neighbor bytes — no shared code
is modified, no regression risk to the finite mode's own rendering path. This is the concrete
mechanism `FS-110` OQ1 named as unresolved; `05-feature-decomposition`'s own `BL-0111` fix (adding
`FEAT-4100` as a *content*-reuse dependency — the tileset draw, not the arrow draw) is confirmed
accurate by this finding, not contradicted by it.

**Binary Tree maze construction (`ADR-0016` point 5, operationalized here, not re-decided):** a
region's own north/west carve bias is drawn from its own per-region reseed; whether its *south* or
*east* edge is open is determined by the **south neighbor's own north-carve decision** and the
**east neighbor's own west-carve decision** respectively (the standard Binary Tree maze property —
a cell's south/east openness is authored by the neighbor on that side, not by the cell itself).
Materializing one region's full 4-direction connectivity therefore needs up to two additional
per-region reseeds (south neighbor, east neighbor), each discarded immediately after the one bit
it supplies is read — no persistent state beyond the single region being materialized, preserving
`ADR-0016`'s own "zero-memory" framing.

### Verb inventory

Five verbs apply (`review` deferred, see below):

- **generate** — the per-region materialization routine: `hash(SEED, row, col)` reseed →
  biome-id (`0-4`) + 4-direction connectivity nibble (via the neighbor-consulting construction
  above) + treasure-presence predicate (`hash(SEED, row, col) mod K`). Owner: `IP-1101`.
- **navigate** — detecting the player's approach to a not-yet-materialized region and triggering
  `IP-1101`'s routine; managing the small resident working set (§ sizing, below) as the player
  moves. Owner: `IP-1102`.
- **render** — drawing a materialized region's screen: reuses `dsr_p`'s biome-dispatch half
  verbatim; a new `draw_region_arrows_inf` routine for the connectivity-driven arrows (§ finding
  above). Owner: `IP-1102` (fused with navigate — see Work unit rationale).
- **persist** — the visited-region ledger and player-position save/load (Workflow D, `FR-10500`/
  `FR-10600`). Owner: `IP-1104`.
- **review** — deliberately deferred, not silently skipped: this tranche ships zero new tile art
  (reuses `FEAT-4100`'s existing biome-family tilesets and `FEAT-2100`'s existing arrow/blocked
  tiles verbatim — no new bitmap, no new palette entry), so no `09-content-review` pass is owed by
  *this* tranche the way `IP-1081`'s new tile bitmaps needed one, mirroring `IP-1090`'s own
  identical precedent. If a future package adds Infinite-Mode-specific tile art, that package
  owns its own review, not this one.

A sixth concern — **mode selection** (Workflow A, the new-game entry point) — is not a
generate/render/navigate/persist/review verb in the FS-110 sense; it is state-machine
plumbing, owned by `IP-1100`, sequenced first since every other package's own entry point
(materialization, the render/navigate loop, the save format) is only reachable once a save
records which mode is active.

### Supersession sweep

This tranche is **purely additive** — no existing model is retired or generalized past its old
shape (unlike, e.g., `IP-1030`'s `ALL_SCREENS` generalization). Swept anyway, per this skill's own
mandatory-whenever-in-doubt discipline:

- **`asm_game.py`**: `GAMESTATE`'s dispatch table, `CUR_ZONE`'s own finite-mode addressing
  (`dsr_p`, `check_zone_transition`, `draw_region_arrows`, `setup_zone_collects`), `REGION_GRAPH`,
  `save_to_sram`/`try_load_save` — **all confirmed untouched by this tranche's own packages**
  (each package's own Files to Modify names new labels/branches only, gated behind a new
  `GAME_MODE` read that defaults to the finite mode's existing value `0`, per `IP-1100`). No call
  site anywhere in the shipped tree assumes `GAME_MODE` exists yet, so the new gate is additive by
  construction, not a retrofit onto existing branches.
- **`tilemaps.py`/`build_rom.py`**: `ALL_SCREENS`/`patches` gain new entries (`IP-1100`'s two new
  screens) following the exact pattern `IP-1040`'s `mm_t`/`sse_t` pair established — no existing
  entry renamed or removed.
- **`test_rom.py`**: no existing check's own assumption (fixed `WORLD_SCALE`, fixed `REGION_GRAPH`
  shape, single save format) is invalidated — Infinite Mode's own save format is a new,
  additional shape gated behind `GAME_MODE == 1`, never taken by any existing finite-mode test
  fixture. **Confirmed clean — nothing to route.**

### Per-region encoding, materialized-window, and ledger sizing decisions (`OQ8`/`OQ5`, resolved this pass)

No `GDS-04`/`07`/`09` delta exists for Infinite Mode (`FS-110` §10, by `ADR-0016`'s own explicit
deferral) — the following are this package-authoring pass's own sizing choices, cited to `R114`'s
recommendation and the confirmed bank-0/SRAM headroom (`GDS-07` §6/§7), not a retroactive
architecture decision:

- **Per-region encoding: 1 byte** — bits 0-2 biome-id (`0-4`, same axis as `REGION_GRAPH`'s own
  byte), bits 3-6 connectivity nibble (up/down/left/right, 1=open), bit 7 reserved/unused. No
  treasure-presence bit is stored — it is always re-derived from `hash(SEED, row, col) mod K` on
  demand (Workflow C step 1), and "collected" state lives only in the ledger (below), never in
  the working set, so no region-resident byte needs to represent it.
- **Materialized window: 3×3 regions (9 bytes) centered on the player's current region** — sized
  to the *actual* dependency the Binary Tree construction has (a region's own connectivity needs
  only itself plus its south/east neighbor's carve decision, resolved above), plus one ring of
  margin so the region just left remains resident long enough to redraw consistently mid-transition,
  without adopting `R114`'s own speculative 5×5/7×7 ceiling (framed there as "if a broader
  prefetch buffer is wanted," not as a minimum). 9 bytes total working-set cost — trivial against
  the confirmed ~3.1 KiB bank-0 headroom (`R111`/`GDS-07` §6), leaving that headroom almost
  entirely free for later widening without `SVBK` banking, should measurement ever call for it.
  Center-anchor position (`INF_ROW`/`INF_COL`, below) adds 4 bytes.
- **Visited-region ledger: 128 entries × 5 bytes (row: signed 16-bit, col: signed 16-bit,
  collected-flag: 1 byte) = 640 bytes SRAM**, against the confirmed ~8 KiB SRAM budget (`R106`) —
  comparable in proportion to `IP-1050`'s own ~84-byte addition, scaled up because this Feature's
  own save shape is ledger-based rather than a single fixed-size struct. **Eviction policy
  (`FS-110` §7's open edge case): FIFO** — once the ledger is full, the oldest-visited entry is
  overwritten to make room for the newly-visited region; a bounded ring buffer, the simplest
  policy consistent with "bounded ledger, unbounded exploration," named here as this pass's own
  choice, not asserted as the only correct one (a future revision could switch to a
  distance-from-current-position eviction rule if FIFO proves player-hostile in practice — an
  observation for a future `09`/`10` pass, not pre-empted here).
- **New save-format version value: `SAVE_VERSION_VAL` bumps `0x04`→`0x05`** (extends the existing
  strictly-monotonic sequence — `IP-9110`'s most recent bump — rather than inventing a second,
  parallel version scheme; `GAME_MODE`'s own persisted value, not a second version byte, is what
  selects which of the two save shapes' fields are meaningful on load, mirroring how a single
  version guard has always covered every field added since `IP-1010`).
- **No spawn-region special case (`OQ4`):** confirmed as this pass's own implementation choice —
  the player's starting region materializes identically to any other region, via the same
  `hash(SEED, 0, 0)` reseed every other region uses. No code path treats `(row,col)==(0,0)`
  specially.
- **Treasure density constant `K` (`OQ2`):** `K = 16` (≈6.25% presence rate), anchored near
  `R215`'s own measured `scale=9` finite-world dead-end density (~6.4%) per `ADR-0017`'s own
  citation, rounded to a power-of-two divisor so the modulo reduces to a 4-bit mask (`AND 0x0F`,
  compared to a fixed remainder) rather than a division — no `DIV`/`MUL` instruction needed,
  consistent with `NFR-2200`'s "no `DIV`/`MUL` anywhere in generation" constraint (`R112`), which
  `FS-110`'s own `NFR-2300` restates for the per-region case.

### Work units and package cut

| Work unit | Package | Owner | Depends on |
|---|---|---|---|
| Mode selection & new-game entry: `GS_MODE_SELECT`/`GS_INFINITE_SEED_ENTRY` (values 10/11, the next free `GAMESTATE` values after `GS_LEGEND=9`), `st_mode_select`/`st_infinite_seed_entry` handlers, `GAME_MODE` WRAM flag, two new screens (`mode_select_screen()`, `infinite_seed_entry_screen()`, reusing existing font/cursor/digit-entry primitives, no new tile art) | [IP-1100](packages/IP-1100-infinite-mode-mode-selection.md) | `08-code-implementation` | `IP-1040`/`FEAT-1100` (cursor-menu convention, `VERIFIED`), `IP-1101` (calls its materialization routine on first entry to `PLAYING`) |
| Per-region materialization (`generate`): per-region `gw_prng_step` reseed, biome-id + connectivity-nibble + treasure-presence derivation, `worldgen.py` oracle mirror | [IP-1101](packages/IP-1101-infinite-mode-region-materialization.md) | `08-code-implementation` | `IP-1020`/`FEAT-9000` (`gw_prng_step` reuse, `VERIFIED`) |
| Streaming window management, navigation, and render integration (`navigate` + `render`, fused — see rationale): 3×3 materialized window, transition-triggered re-materialization, `dsr_p` biome-dispatch reuse, new `draw_region_arrows_inf` | [IP-1102](packages/IP-1102-infinite-mode-streaming-window-and-render.md) | `08-code-implementation` | `IP-1101` (region data), `IP-1030`/`FEAT-4100` (`dsr_p`'s biome-dispatch half, `VERIFIED`) |
| Treasure placement, collection & win-condition state (running count, top-3 table subroutine — call site deferred, `OQ3` unresolved) | [IP-1103](packages/IP-1103-infinite-mode-treasure-and-win-condition.md) | `08-code-implementation` | `IP-1101` (treasure-presence predicate), `IP-1102` (collection reuses the materialized window's per-frame loop) |
| Visited-region-ledger save/load (`persist`): SRAM write/restore, `SAVE_VERSION_VAL` bump, FIFO eviction | [IP-1104](packages/IP-1104-infinite-mode-ledger-save-persistence.md) | `08-code-implementation` | `IP-1100` (`GAME_MODE`), `IP-1101` (position/region format), `IP-1103` (collected-state to persist) |

**Split rationale:** five packages, not one, despite `FEAT-10000`'s own catalog entry being kept
deliberately unsplit (that entry's own Scope field explicitly anticipates this — "`06-feature-
specification` may split this if implementation detail later shows a natural boundary… mirroring
how `FEAT-9000` itself started as one Feature before `FEAT-4100`/`FEAT-5300`/`FEAT-9100` were
later carved out"). Implementation detail now shows exactly that seam: each of the five verbs
above is independently completable and independently testable against its own Files to
Modify — `generate` needs no rendering code to unit-test (a `worldgen.py` oracle corpus, mirroring
`IP-1020`'s own `T12` precedent); `persist` needs no win-condition logic to test a save/reload
round trip. **`navigate` and `render` are fused into one package (`IP-1102`)**, not split further,
because they are *not* independently completable the same way: the window-management logic has
nothing to draw with until the render half exists, and the render half has no trigger to run from
until the window-management half decides a region needs (re)materializing — the same
not-independently-completable test `IP-1090`'s own single-package precedent applies (state-machine
half and render half, there fused for the identical reason).

### Sequencing summary

**Critical path: `IP-1101` → `IP-1102` → `IP-1103` → `IP-1104`** (4 packages) — `IP-1101` is the
tranche's foundational package (mirrors `IP-1020`'s own root-of-tranche role for the finite mode);
everything downstream needs its per-region output shape decided first. `IP-1100` depends only on
`IP-1101` (it must call the materialization routine once, on first entry to `PLAYING`) and is
otherwise parallel-eligible with `IP-1102` — its own state-machine/screen work touches no file
region `IP-1102` touches. All five packages' own upstream dependencies
(`IP-1020`/`IP-1030`/`IP-1040`, `FEAT-9000`/`FEAT-4100`/`FEAT-1100`) are already `VERIFIED` — this
tranche is immediately buildable in full once authorized, not blocked on any in-flight work
elsewhere in the tree. **Not extending the existing critical path** — this is a new, independent
4-package chain off already-`VERIFIED` roots, the same "parallel, independent thread" framing
`FP-04`'s own Infinite Mode delta already established at the Feature-planning level.

**`OQ3` (run-end trigger) blocks only `IP-1103`'s own top-3-comparison *call site*, not the rest
of the tranche** — see `IP-1103`'s own package text for the precise boundary of what is and isn't
buildable without it.

### Backlog riders honored in this pass

- **`BL-0110`** (finite-mode super-cell size tuning, `ADR-0018`) — **not** riding this pass; it
  belongs to the finite-mode blob-clustering FR's own future `07` pass (`BL-0066`), a distinct
  Feature from `FEAT-10000`, named here only to confirm it was checked and correctly excluded.
- **`BL-0112`** (run-end trigger timing) — **not resolved by this pass**, per `FS-110`'s own
  explicit routing (`04-requirements-engineering` or a direct user decision, not `07`) — see the
  Sequencing summary above for exactly what this leaves unbuilt.
- **`BL-0114`** (materialized-window radius/byte cost) — resolved this pass, see "Per-region
  encoding, materialized-window, and ledger sizing decisions" above. `BL-0114` flips to `DONE`
  once `00-pipeline-manager` harvests this run.

## Nine biome-family identities (`FS-102`/`FS-103` revision, `FR-4320`, `BL-0128`, planned 2026-07-16)

Project-owner decision (`BL-0128`): merge the original Release-1 nine-zone art with the
five-family procgen taxonomy so no shipped screen art stays permanently orphaned. Baselined as
`FR-4320` (`04-requirements-engineering`, run #169); `FS-102`/`FS-103` both revised to cover it
(`06-feature-specification`, run #170).

### Verb inventory (mandatory — this capability spans generate/render/persist)

| Verb | Owner | Notes |
|---|---|---|
| **Generate** (finite mode: which numeric biome-id a region draws) | [IP-1022](packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md) | The clamp-bound widening itself (`4`→`8`) is mechanical; the *meaning* of positions 5-8 is now settled (`CR-08`, resolved 2026-07-16 into `FR-4310`) — inseparable from **Render**'s own dispatch assignment (same numeric ID drives both), so bundled into the same package, not split. |
| **Generate** (Infinite Mode: `_materialize_region`'s own independent per-region hash draw, `%5`→`%9`) | [IP-1106](packages/IP-1106-infinite-mode-nine-identity-value-widening.md) | Confirmed independent of `CR-08` on its own terms (no neighbor-based grammar-adjacency clamp, `worldgen.py:284-285`) — but cannot ship ahead of **Render**'s own dispatch cascade (`IP-1022`) or `IP-1105`'s own bit-layout repack, both real prerequisites, not `CR-08` ones. |
| **Represent** (Infinite Mode `region_byte`/`INF_MZ_RESULT`'s own bit-field layout — biome bits 0-2→0-3, connectivity nibble bits 3-6→4-7) | [IP-1105](packages/IP-1105-infinite-mode-biome-domain-widening.md) | **Genuinely independent, behavior-preserving infrastructure**: repacks *where* the same 0-4 biome value and the same connectivity nibble live within the byte, preparing bit headroom for the value-range widening above, without changing the draw's own value range (`%5`) or any rendered/observable behavior at the time it ships. |
| **Render** (screen dispatch, `dsr_p`/`dsr_p_dispatch`, shared by both modes) | [IP-1022](packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md) | Bundled with finite-mode **Generate** — the dispatch cascade assigns each of the four new identities its `CR-08`-resolved `CP_n` branch; `IP-1106`'s own Infinite Mode widening depends on this package shipping first (`dsr_p_inf` falls into the same shared cascade). |
| **Persist** (`ZONE_COLLECTS` collectible-spawn content + array wiring) | [IP-1033](packages/IP-1033-nine-biome-family-collectible-spawn-content.md) (content) + [IP-1022](packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md) (final array-index wiring) | Content authoring (`IP-1033`) needs no numeric-ID decision; final `ZONE_COLLECTS` array-index assignment does, so it rides `IP-1022` instead — `IP-1022` depends on `IP-1033`'s own staged content existing first (not necessarily `VERIFIED`, just present in the tree). |
| **Persist** (`inf_treasure_pos`'s own matching table extension, `asm_game.py:1838`) | [IP-1106](packages/IP-1106-infinite-mode-nine-identity-value-widening.md) | Indexed by the same biome-id `IP-1022`/`CR-08` assign and consumes the same `(x,y)` values `IP-1033` authors for each identity's `ZONE_COLLECTS` type-2 entry — bundled with Infinite Mode's own value-widening package since both are Infinite-Mode-specific consumers of the same numeric assignment. |

**Packaged this pass (2026-07-16, second half of the same day):** `CR-08` resolved into `FR-4310`
(`04-requirements-engineering`, same session) supplied the single missing input the prior pass's
own "Deferred" verdict was waiting on. Two packages authored: **`IP-1022`** (finite-mode
generation + shared dispatch cascade + `ZONE_COLLECTS` wiring) and **`IP-1106`** (Infinite Mode's
own value-range widening + `inf_treasure_pos` extension) — see Work units below for the full
dependency chain, including each package's real dependency on `IP-1033`/`IP-1105` (both still
`NOT STARTED`, neither authorized — this pass's own packages inherit that same gate, not a new
one).

### Supersession sweep

This delta widens an existing domain (5→9 biome-family values); it does not retire or replace a
model the way `IP-1030`'s `ALL_SCREENS` generalization did. Swept `asm_game.py`/`tilemaps.py`/
`build_rom.py` for every other site encoding the old `0`–`4`/5-value assumption or the current
bit-field layout beyond the ones already named above: **found the full consumer set of
`INF_WINDOW`/`INF_MZ_RESULT`'s packed byte** — `dsr_p_inf` (`asm_game.py:1386`, biome mask),
`czt_infinite` (`asm_game.py:1160,1171,1182,1193`, four connectivity-bit tests), `draw_region_
arrows_inf` (`asm_game.py:1573,1576,1579,1582`, four more), `szc_infinite` (`asm_game.py:1936`,
biome mask) — every one now named in `IP-1105`'s own Files to Modify, none missed. Also found:
`dsr_p`'s own inline comment ("biome-id 4 (`generate_world`'s own invariant: axis-clamped to
0..4)," `asm_game.py:1397`) is documentation only, not code; will need updating whenever the
deferred dispatch package eventually lands, no package needed now. No other call site (searched
for literal `% 5`, `CP_n(4)`, `0..4`/`0-4` range comments) found beyond the ones already named —
confirmed clean.

### Work units and package cut

| Work unit | Package | Owner | Depends on |
|---|---|---|---|
| Infinite Mode `region_byte`/`INF_MZ_RESULT` bit-field repack (biome 0-2→0-3, connectivity 3-6→4-7) — behavior-preserving, value range unchanged (`%5`) | [IP-1105](packages/IP-1105-infinite-mode-biome-domain-widening.md) | `08-code-implementation` | `IP-1101`/`IP-1102` (`VERIFIED`, the shipped format this repacks) |
| Collectible-spawn content for the four newly-folded identities (Village, Cave, Desert, Plains) | [IP-1033](packages/IP-1033-nine-biome-family-collectible-spawn-content.md) | `08-content-authoring` | `FR-4320` (baselined). Final array wiring rides `IP-1022`, not this package. |
| Finite-mode `generate_world`/`worldgen.py` clamp widening (`[0,4]`→`[0,8]`) + `dsr_p`/`dsr_p_dispatch`'s cascade extension (4 new `_dsr_family` branches) + `tilemaps.py`'s `ALL_SCREENS`/`build_rom.py`'s patch wiring + `ZONE_COLLECTS`'s final 9-entry array assembly | [IP-1022](packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md) | `08-code-implementation` | `FR-4310` (baselined, `CR-08` resolved); `IP-1033` (its staged spawn content must exist in the tree first) |
| Infinite Mode `_materialize_region`/`inf_materialize_region`'s value-range widening (`%5`→`%9`) + `inf_treasure_pos`'s 4-entry table extension | [IP-1106](packages/IP-1106-infinite-mode-nine-identity-value-widening.md) | `08-code-implementation` | `IP-1105` (bit-layout repack must ship first); `IP-1022` (shares `dsr_p_dispatch`, must ship first); `IP-1033` (the `(x,y)` values `inf_treasure_pos` mirrors) |

**Split rationale:** two new packages this pass (`IP-1022`, `IP-1106`), not one. The prior pass's
own "Deferred (bundled)" verdict correctly grouped finite generation with dispatch (the numeric
ID drives both, inseparable) — that coupling is preserved intact as `IP-1022`. **What's now split
out as its own package (`IP-1106`) is Infinite Mode's own value-range widening**, which the prior
pass's verb inventory had bundled into the same deferred lump only because it shared `CR-08` as a
*blocking condition*, not because it shares files/concerns with finite-mode generation — now that
`CR-08` is resolved, the real dependency structure is clearer: `IP-1106` depends on `IP-1022`
(shared dispatch) and `IP-1105` (bit layout) as genuine prerequisites, but touches none of
`IP-1022`'s own finite-mode files (`worldgen.py`'s `generate()`, `asm_game.py`'s `generate_world`,
`tilemaps.py`'s `ALL_SCREENS`) — a real module-boundary seam, not an artificial one. Splitting
avoids inflating `IP-1022`'s own Definition of Done with Infinite-Mode-specific concerns it has no
natural authority over (mirroring the same code/content and mode-boundary discipline `IP-1030`/
`IP-1101`/`IP-1105` themselves already established). Neither package is `READY` — both have real,
unshipped dependencies (`IP-1033` for `IP-1022`; `IP-1033`/`IP-1105`/`IP-1022` for `IP-1106`) —
correctly marked `BLOCKED`, not `NOT STARTED`, distinguishing "nothing stands in the way but
authorization" (`IP-1033`/`IP-1105`'s own current state) from "a real unshipped prerequisite"
(`IP-1022`/`IP-1106`'s own state, one level further downstream).

### Sequencing summary

**New critical-path chain within this delta: `IP-1033` → `IP-1022` → `IP-1106`, with `IP-1105`
also feeding `IP-1106`.** `IP-1033`/`IP-1105` are the two roots (both `NOT STARTED`, parallel-
eligible with each other, no shared files); `IP-1022` needs `IP-1033`'s content staged first;
`IP-1106` needs both `IP-1022` (dispatch) and `IP-1105` (bit layout) complete first. This is a new,
independent 4-package chain off already-`VERIFIED` roots (`IP-1101`/`IP-1102`/`IP-1103`/`IP-9070`)
— it does not extend or block any other in-flight critical path in the tree (Infinite Mode's own
tranche and the finite-mode procgen tranche are both already `VERIFIED` and closed independent of
this delta, mirroring the prior pass's own confirmation).

### Backlog riders honored in this pass

- **`BL-0130`** (catalog Included-Requirements gap for `FR-4320`) — **not** riding this pass; it's
  a `05-feature-decomposition` metadata fix, out of this skill's own write scope, confirmed
  correctly excluded.
- **`CR-08`'s own resolution** (`BL-0129`, closed by `04-requirements-engineering` earlier the
  same session) is what unblocked this pass — the packages above are its direct, immediate
  downstream consequence, not a separate rider.

## Procedural Music Generation (`FS-111`/`FEAT-7100`/`EP-7000`, `ADR-0019`/`BL-0127`, planned 2026-07-16)

New capability grounded in `ADR-0019`: build-time (Python) generation of nine biome-family
sub-themes from the existing shipped main theme, plus a runtime selection mechanism keyed to the
player's current region's biome-family identity. Baselined as `FR-7100`/`FR-7110`/`NFR-4400`
(`04-requirements-engineering`, this session); specified in full as `FS-111`
(`06-feature-specification`, this session), which carried forward five Open Questions rather than
resolving them prematurely.

### Verb inventory (mandatory — this capability spans generate/navigate)

| Verb | Owner | Notes |
|---|---|---|
| **Generate** (build-time: nine sub-theme byte sequences via transposition/tempo-duration scaling of the main theme) | [IP-1110](packages/IP-1110-procedural-music-generation.md) | No runtime counterpart — `ADR-0019` point 3's own explicit decision (no `worldgen.py`-style oracle/lockstep need). Resolves `FS-111`'s Open Question 3 (which identity the main theme's own data represents) as part of this package's own Objective — see its own §2. |
| **Navigate/select** (runtime: which of the nine tracks plays, keyed to `PLAYING`'s current region identity) | [IP-1111](packages/IP-1111-biome-family-sub-theme-playback-selection.md) | Resolves `FS-111`'s Open Question 1 (selection-mechanism shape) — hooks into `do_screen_redraw`'s existing per-`GAMESTATE` dispatch (default-reset-to-main-theme) plus `dsr_p_dispatch`'s existing per-identity biome cascade (override to the matching sub-theme), reusing two already-shipped trigger points rather than adding a new per-frame poll or new WRAM "last-known identity" state. |
| **Persist** | None — no save-data footprint (`FS-111` §14, confirmed: the biome-family identity this capability reads is already persisted/re-derived by `FR-4310`/`FR-4320`'s own mechanisms, unchanged and un-owned here). Deliberate, not a silent gap. |
| **Review** | Deferred to `09-content-review` once code ships (that skill's own Audio Correctness dimension already covers exactly this) — not this stage's own scope to package. |

**A real technical finding this pass surfaced, not named anywhere upstream (`FS-111` included):**
direct re-read of `music_tick` (`asm_game.py:1256`–`1270`) found its own loop-restart branch
(`LD_A_HL(); CP_n(0xFF); JR_NZ('mt_play') / LD_HL_nn(0)` with `patches['mus_reset']` hardcoded to
`music_addr` — the **main theme's own fixed ROM address**, patched once at build time) is **not
track-agnostic**. If `IP-1111`'s own selection mechanism repoints `MUSIC_PTR_LO`/`MUSIC_PTR_HI`
into a sub-theme's own data, that sub-theme plays correctly note-by-note — but the moment it hits
its own terminal `0xFF` byte, `music_tick`'s hardcoded reset would snap `HL` back to the **main
theme's** address, not the currently-playing sub-theme's own start, silently truncating every
sub-theme to a single pass before falling back to the main theme. `FS-111`'s own §13 called
`music_tick`'s cost "unaffected in structure" — true for cycle cost, not for correctness once a
second track ever plays; this pass corrects that framing rather than carrying it forward
uncorrected. **Fix (packaged into `IP-1111`, not split out — it has no value in isolation, since
nothing else in the tree ever repoints `MUSIC_PTR`):** a new 2-byte WRAM field
(`MUSIC_BASE_LO`/`MUSIC_BASE_HI`, prospective `0xC69B`–`0xC69C`, the next free bytes after
`LEDGER`'s own `0xC69A` end per `GDS-07`) holding the currently-selected track's own base address;
`music_tick`'s reset branch reads this field instead of the hardcoded `mus_reset` patch constant.
See `IP-1111` §6/§7 for the full task.

### Supersession sweep

This capability does not retire or replace an existing model — `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/
`MUSIC_CTR` remain the same mechanism, `SONG`/`music_data()`'s byte format is unchanged, and the
main theme itself is unmodified. Swept `asm_game.py`/`build_rom.py`/`music.py` for every site
assuming "music is written exactly once, at boot": found none beyond `music_tick`'s own
loop-restart branch (named above, not a call site elsewhere) and the boot-init block itself
(`asm_game.py:390`–`394`, which stays correct as the pre-`do_screen_redraw` default and needs no
change — `IP-1111`'s own default-reset-to-main-theme logic at `do_screen_redraw`'s entry
super­sedes it functionally the moment the first screen draws, but leaving the boot-init block
in place is harmless redundancy, not a defect). No other consumer of `MUSIC_PTR_LO`/`MUSIC_PTR_HI`/
`MUSIC_CTR` exists in the tree (confirmed by grep — `music_tick` is the sole reader). Confirmed
clean.

### Work units and package cut

| Work unit | Package | Owner | Depends on |
|---|---|---|---|
| Build-time generation of nine biome-family sub-themes (transposition/tempo-duration scaling of the main theme) + ROM emission + address-table patching | [IP-1110](packages/IP-1110-procedural-music-generation.md) | `08-code-implementation` | `FR-7100`/`FR-4320` (both baselined) |
| Runtime selection (hook into `do_screen_redraw`/`dsr_p_dispatch`) + `music_tick`'s loop-restart correctness fix (new `MUSIC_BASE_LO`/`MUSIC_BASE_HI`) | [IP-1111](packages/IP-1111-biome-family-sub-theme-playback-selection.md) | `08-code-implementation` | `IP-1110` (the nine sub-theme addresses this package repoints to); [IP-1022](packages/IP-1022-finite-mode-nine-identity-generation-and-dispatch.md) (`dsr_p_dispatch`'s cascade must carry all nine identity branches before this package's own per-identity repoint code can be added to each — currently only 5 of 9 branches exist) |

**Split rationale:** two packages, cut along the same generate/navigate seam the verb inventory
names — `IP-1110`'s own build-time-only scope (`music.py`/`build_rom.py`, no runtime code) has no
natural coupling to `IP-1111`'s own runtime dispatch-hook scope (`asm_game.py` only) beyond
`IP-1111` consuming `IP-1110`'s own output addresses. **Considered and rejected: a third, partial
package wiring `IP-1111`'s own selection logic only against the 5 identities `dsr_p_dispatch`
already dispatches today**, deferring the remaining 4 branches to a follow-on once `IP-1022`
ships — mirroring `IP-1105`/`IP-1106`'s own split precedent. Rejected because, unlike `IP-1105`
(which touched a *disjoint* mechanism — `INF_MZ_RESULT`'s bit layout — from what `IP-1022` touches
— `dsr_p_dispatch`'s branch content), a partial `IP-1111` would add music-repoint instructions
**inside the same `_dsr_family` branches** `IP-1022`'s own planned diff is described as rewriting
("extends `dsr_p_dispatch`'s shared cascade to all nine identities") — genuine file/region
overlap, not a clean seam. Two packages independently editing the same lines in sequence is a
merge-order hazard this session's own established discipline (`IP-1105`'s own scope boundary,
`Files to Modify` accuracy rule) exists specifically to avoid; `IP-1111` is therefore kept as one
package, `BLOCKED` on `IP-1022` shipping first, rather than split.

**`IP-1110`'s own scope also resolves `FS-111`'s Open Question 3** (which of the nine identities
the main theme's own data represents): `Grass` is assigned as the zero-transform anchor, matching
`generate_world`'s own existing `(0,0) = Grass` precedent (`ADR-0009`) that `FS-111`'s own Open
Question 3 already named as a reasoned candidate without deciding. This is a content-mapping
choice with no downstream algorithm-validity or save-format consequence (unlike `CR-08`'s own
grammar-legality stakes) — cheaply reversible if a future pass disagrees, stated explicitly here
rather than silently invented, per this package's own §2.

**Revision (2026-07-17, `07-implementation-planning` — the touch `IP-1110`'s Outstanding Issue
requested):** `IP-1111`'s §5/§6 updated to consume the interface `IP-1110` actually shipped —
the flat, biome-id-indexed `music_table` (18 ROM bytes, `zc_table`'s own precedent), which the
implementation chose over the originally-planned per-identity `*_mus_lo`/`*_mus_hi` named
patch-key pairs (those keys were never created; `IP-1110`'s in-scope deviation, recorded on its
Build Plan row and confirmed by `VR-1110`). The table's indexability collapses the original
eight per-branch override snippets into **one shared `music_select` subroutine + one `CALL` at
`dsr_p_dispatch`'s entry** (where both mode paths already converge with A = biome-id) — a
smaller `asm_game.py` footprint than originally planned, zero instructions inside any branch
body. One new patch key (`music_tbl`) is added, resolved exactly as `zc_table` already is.
`IP-1022` `VERIFIED` (2026-07-17) closed the original "cannot cite post-widening line numbers"
caveat — all §6 citations are now against the live tree. `IP-1111` → `READY` (both code
dependencies `VERIFIED`; authorization "Build all six," 2026-07-16, already on record).

### Sequencing summary

**New, independent chain: `IP-1110` (root, `NOT STARTED`) → `IP-1111` (`BLOCKED` on `IP-1110` and
on `IP-1022`, itself part of arc (3)'s own still-unauthorized four-package chain).** `IP-1110` has
no dependency on any in-flight or unauthorized package — it is buildable the moment G3 authorizes
it. `IP-1111` cannot ship until **both** `IP-1110`'s own sub-theme addresses exist **and**
`dsr_p_dispatch`'s cascade carries all nine identity branches (`IP-1022`, itself `BLOCKED` on
`IP-1033`) — a genuine two-source dependency, not merely two authorizations, mirroring
`FS-111`/[FP-04](../feature-planning/04-feature-dependency-graph.md)'s own already-named
cross-arc sequencing risk. This chain does not extend or block arc (3)'s own critical path
(`IP-1033`/`IP-1105` → `IP-1022` → `IP-1106`) — it merely joins it as a new downstream consumer at
`IP-1022`'s own output, adding one more package to what `IP-1022` unblocks once it ships.

### Backlog riders honored in this pass

None — this pass carries no `SCHEDULED` backlog entry riding along; it is the direct, expected
continuation of `BL-0127`'s own `05`→`06`→`07` chain, already tracked under that ID.

## BL-0134 — `IP-1022`'s ROM-budget overflow: mechanical recovery + upstream routing

**Trigger:** `08-code-implementation`'s fresh attempt at `IP-1022` (2026-07-17) hit a hard ROM
overflow — wiring `village`/`cave`/`desert`/`plains` into `ALL_SCREENS` makes `build_rom.py` emit
their full tile+attr arrays for the first time (`IP-1033`'s own content stayed inert/unwired, so
no prior package paid this cost). All source edits were reverted; the tree is back to
last-known-good (31362/32768, 309/309 passing). This entry re-derives the exact byte math and
determines what, if anything, can close the gap without an architecture-level decision.

### Byte math (re-derived directly from source, not the crash's own partial count)

`IP-1022`'s full scope would add:

- **4,608 bytes** — four new screens' tile+attr arrays (`village_screen`/`cave_screen`/
  `desert_screen`/`plains_screen`, each `W*H=576` tiles + `576` attrs = 1,152 bytes; confirmed by
  directly invoking each function and measuring its output).
- **~108 bytes** — `ZONE_COLLECTS`'s four new spawn lists (25 bytes each: 1-byte length + 6
  entries × 4 bytes) plus `zc_table`'s growth (4 × 2-byte pointers).
- **~48 bytes** — `dsr_p_dispatch`'s four new `CP_n`/`JR_Z` comparison pairs (16 bytes: `brick`
  becomes explicit, `village`/`cave`/`desert` are new) plus four new `_dsr_family` blocks (32
  bytes: `LD_DE_nn`+`LD_BC_nn`+`JR`, 8 bytes each — `plains`'s block costs the same as the other
  three; only its *reach* is a fallthrough, not its size).

**Total: ~4,764 bytes needed. Headroom available: 1,406 bytes (31362/32768 used). Shortfall:
~3,358 bytes** — a more complete figure than the crash-triggered 3,202-byte estimate `BL-0134`
was originally filed with (the crash occurred mid-emission of the *first* new screen, before the
remaining screens/collectible data/code were even reached).

### Mechanical recovery found (safe, no architecture change)

`tiles.py`'s `build_tile_data()` (`tiles.py:924-925`) allocates a **fixed 256-tile (4,096-byte)**
array (`bytearray(256 * 16)`) regardless of how many tile slots are actually populated. Direct
scan of every `TL_*` constant in `tiles.py` finds the highest in use is `TL_TORCH = 0xB5` (181) —
only **182 of 256 slots** (indices 0–181) are ever written by a `put()` call; slots 182–255 are
pure zero-padding, 74 slots × 16 bytes = **1,184 wasted bytes**, shipped in every build today and
already present in the *current* 31362-byte baseline, not something this package would newly
introduce.

The boot-time consumer (`asm_game.py:358-360`) copies exactly `256 * 16` bytes from ROM to VRAM
(`0x8000`) via a single hardcoded `LD_BC_nn(256 * 16)` — the *only* other site referencing this
constant (confirmed by grep across `asm_game.py`/`tiles.py`/`build_rom.py`). Truncating both to
the actual highest-used index (rounded to a clean tile-count boundary, e.g. 184 tiles = 2,944
bytes, headroom for a few more before the next size-class boundary) is a pure, mechanical,
behavior-preserving reduction — slots 182+ are never addressed by any `_put()`/OAM/tilemap byte
anywhere in the tree, and the boot sequence already zero-clears the full VRAM tile-pattern region
(`asm_game.py:350-355`) before this copy runs, so the untransferred slots read as blank either way.
**Recovers ~1,152–1,184 bytes.** Not remotely sufficient on its own (headroom would rise to
~2,558–2,590 bytes against a ~4,764-byte need — still ~2,174–2,206 bytes short), but a legitimate,
free, zero-risk win regardless of how the larger gap is resolved. Packaged as **`IP-9150`** below.

### What does NOT close the gap

- **Reducing tile-art variety per new screen** does not help — a screen's ROM cost is `W*H`
  fixed-size grid bytes (1,152 bytes total) regardless of how many *distinct* tile indices it
  uses; a screen drawn with 3 tile types costs the same as one drawn with 30.
- **Shrinking `BG_PALETTES`/`OBJ_PALETTES`** — both are hardware-mandated 8-slot arrays (64 bytes
  each) copied by their own fixed-count loops (`asm_game.py:363-376`); several `OBJ_PALETTES`
  slots are already unused placeholders, but the recoverable amount (≤32 bytes) is negligible
  against a multi-thousand-byte gap and not worth the same-pattern risk as the tile-data trim for
  so little return.
- **Compressing the new screens' tile/attr arrays at build time, decompressing at runtime** would
  recover real space (these screens' fill patterns are already build-time-computed from small
  seed formulas — e.g. cave's `(y*13+x*5+7)%18` — so a compact on-ROM representation is plausible
  in principle), but this is not a mechanical trim: it requires a **new SM83 decompression
  routine**, a real per-frame/per-redraw CPU-cycle cost this codebase already has an open,
  **`NOT MET`** cycle-budget finding against (`NFR-1400`, Infinite Mode's `dsr_p_inf` path) — adding
  decompression to the shared `copy_screen`/`dsr_p` redraw path risks compounding that existing gap
  rather than being a free win. This is a genuine new engine capability, not a data trim, and
  belongs to `03-architecture-design-synthesis` (an ADR) if pursued.
- **Multi-bank ROM** — `ADR-0001` (single-bank ROM, no MBC bank switching) explicitly named
  `MSTR-001` `C7`'s world-scale growth as its own future supersession trigger; this exact scenario
  (a biome-family/world-content expansion outgrowing the single 32KB bank) is what that trigger
  describes. `ADR-0006` already establishes MBC1, which supports banking — reversing `ADR-0001`'s
  no-bank-switching decision is technically available, but is a first-class architecture decision
  (bank-boundary-aware code/data layout, `gbc_lib.py`'s `ROM` class would need bank-aware emission,
  every cross-bank call site audited) far beyond this package's own scope.

### Work units and package cut

| Work unit | Package | Owner | Depends on |
|---|---|---|---|
| Trim `build_tile_data()`'s emitted range to the highest actually-used tile index (rounded to a clean boundary) and correspondingly reduce the boot-time tile-copy DMA count | [IP-9150](packages/IP-9150-tile-data-padding-trim.md) | `08-code-implementation` | None — independent of `IP-1022`, safe to ship on its own |

**`IP-1022` itself is not re-packaged here.** Its own scope, as specified, remains correct and
unchanged — the blocker is a ROM-budget ceiling the package's own §13 Risks should have named
(a planning gap, not a defect in the package's design), not a flaw in *what* it specifies. Even
with `IP-9150`'s full recovery applied first, `IP-1022` still cannot fit (~2,200-byte residual
shortfall) — closing that residual requires either **descoping** (shipping fewer than all four
newly-folded identities in this pass, contradicting the user's own "Build all six" authorization
as currently scoped) or a **genuine architecture-level decision** (runtime tile-array compression,
or reversing `ADR-0001`'s single-bank decision per its own named `C7` trigger). Neither is this
skill's call to make — both require the user's explicit direction before any further package can
be authored against `IP-1022`'s own scope. Routed upstream: **`03-architecture-design-synthesis`**
if the user chooses the compression or bank-switching path (a new ADR is needed either way); a
direct user answer alone suffices if the user instead chooses to descope this pass.

### Backlog riders honored in this pass

`BL-0134` (High) — re-derived the exact byte math, packaged the one safe mechanical recovery
(`IP-9150`), and confirmed (not assumed) that no further mechanical trim closes the remaining gap.
Disposition updated from `SCHEDULED` to `NEEDS-USER` — the residual ~2,200-byte shortfall needs the
user's explicit direction among the options named above before `IP-1022` can be re-attempted.

## `IP-1022` re-plan against `ADR-0020` (procedural screen fill)

**Trigger:** `ADR-0020` (2026-07-17) decided the four newly-folded biome screens render via a
runtime procedural-fill routine + landmark-overlay list rather than baked full arrays, closing
`BL-0134`'s ROM shortfall without needing `ADR-0011`'s bank switching. This entry records the
re-planning rationale; `IP-1022`'s own package doc carries the full technical detail.

### What changed and why

The prior TWBS entry (`BL-0134`'s mechanical-recovery pass, same day) found `IP-9150`'s tile-data
padding trim insufficient alone and concluded the residual ~2,200-byte gap needed either
descoping, tile compression, or bank switching — routing to `03-architecture-design-synthesis` to
decide. `ADR-0020` chose compression, specifically via a technique this package's own content
happens to make unusually cheap: all four new screens' background patterns are already expressed
as small, closed-form Python modulo formulas (`tilemaps.py`'s own `*_screen()` functions), not
arbitrary hand-authored pixel art — the same class of "computable, not merely storable" content
`generate_world`'s own on-device generation (`ADR-0009`) already demonstrates is both feasible and
this codebase's own established idiom.

**Verb inventory re-check:** the four verbs this delta touches — *generate* (`generate_world`'s
domain widening, unchanged), *render* (now split into two sub-verbs: procedural background fill +
landmark overlay, both new), *navigate* (`dsr_p_dispatch`'s cascade, unchanged in shape, extended
in reach), *persist* (`ZONE_COLLECTS`, unchanged) — each still has a named owner within this one
package; the *render* verb's split is recorded explicitly here rather than left implicit.

**Supersession sweep (re-run):** searched `asm_game.py`/`build_rom.py` for any other site assuming
"every `ALL_SCREENS` entry has a baked ROM address" — found none: `screen_addrs`'s own dict-keyed
lookup (`build_rom.py`'s `for name, fn in ALL_SCREENS` loop) naturally has no entry for
`village`/`cave`/`desert`/`plains` once they are removed from `ALL_SCREENS`, and no other code
path indexes `ALL_SCREENS` positionally or assumes it holds all nine identities — confirmed clean.

### No split from `IP-9150`

`IP-9150` (tile-data padding trim, 1,152 bytes) remains packaged and independently useful — it
recovers real headroom regardless of how `IP-1022`'s own gap is closed, and this re-plan does not
change its own scope. With `ADR-0020`'s ~4,272-byte estimated recovery alone comfortably exceeding
the ~3,358-byte shortfall, `IP-9150` is no longer strictly required to unblock `IP-1022` — it
remains a good-hygiene parallel package, not a prerequisite.

### Bank switching (`ADR-0011`) not triggered

`ADR-0020` explicitly recorded this: the narrower, already-precedented, lower-risk technique
closes this specific gap, so `ADR-0011`'s own cutover trigger ("content genuinely cannot fit
remaining bank-0 headroom" *after* available ROM-efficiency options are exhausted) is not met by
this delta. `ADR-0011` remains the committed long-term direction for when ROM-cheap tricks are
exhausted — unaffected, not implemented by this pass.

### Backlog riders honored in this pass

`BL-0134` — re-planned `IP-1022` against `ADR-0020`'s decision; the package's own Verification
Checklist now carries the oracle-parity obligation `ADR-0020` requires. `BL-0134`'s own
disposition is updated by the pipeline manager once this package ships and verifies.

## Zone-name restoration on the procedural screens (`BL-0138` remediation, planned 2026-07-17)

**Source:** `09-content-review` Finding 1
([content-review-nine-biome-family-delta.md](../reviews/content-review-nine-biome-family-delta.md)):
the four `ADR-0020` procedurally-filled screens never write the row-0 zone name their Python
oracles ship, so the previous screen's name persists on every visit.

**Verb inventory:** *render* only — one verb, one package. No generate/navigate/persist impact
(row 0 is presentation; the name is static per-screen content). The *review* verb is what caught
it and re-runs after the fix per the normal loop.

**Cut and rationale — one package, `IP-9160`, owned by `08-content-authoring`:** the shipped
`apply_landmark_overlay` routine already writes arbitrary `(x, y)` cells including row 0
(direct-read confirmed, no row filter), and `build_rom.py`'s landmark emission is generic over
list length — so the entire production fix is *data*: append each screen's name-region row-0
cells (mechanically derived from its own `*_screen()` oracle) to the four existing `*_LANDMARKS`
lists in `tilemaps.py`. Pure data-half + its verifying tests = the content peer's exact charter;
no `asm_game.py` change exists to justify `08-code-implementation` (contrast `BL-0135`'s seam
note on `IP-1022`, where a new shared subroutine dominated the cut). Split considered and
rejected: a separate test-only package (the `T13.e` row-0-exclusion narrowing + `T13.g`
stale-name regression) would decouple the fix from the exact check that proves it — the same
one-coherent-DoD rule every remediation package here has followed.

**Supersession sweep:** nothing is retired; swept for other row-0 writers to inventory the live
digit cells the narrowed `T13.e` exclusion must keep (`_score_bar` placeholders,
`update_status_disp`) — the package makes completing that inventory an explicit implementation
task rather than baking this planning pass's own list in as an assumption.

**Authorization:** **not authorized** — new remediation package for a post-bootstrap finding
(`BL-0138`), not covered by any standing go-ahead; awaits an explicit G3 user decision.

## HUD carrot-target digit fix (`BL-0139` remediation, planned 2026-07-17)

**Source:** `08-content-authoring` run #206 (`IP-9160`'s own Outstanding Issue, spotted during
that package's row-0 writer inventory): every screen's `_score_bar` bakes a literal `"-9"` at
row-0 cols 3-4 (`tilemaps.py:44-45`) and no runtime writer ever updates col 4 — but the finite-mode
win condition is `CARROTS_COUNT == WORLD_SCALE` (`IP-1021`), so any world at a scale other than 9
shows a target digit that doesn't match its own real win condition.

**Verb inventory:** *render* only (a HUD digit is presentation, not generation/navigation/
persistence). One verb, one runtime concern — no split needed on that axis.

**Scope decision — finite mode only, Infinite Mode explicitly deferred:** `BL-0139` itself named
a second, harder question: what should Infinite Mode's slot show, since Infinite Mode has no
fixed carrot target at all (`RUNNING_TREASURE_COUNT` only ever increases, no `WORLD_SCALE`-style
ceiling). Folding that question into this package would either (a) invent a display convention
for Infinite Mode that no FS/GDS document has ever specified, or (b) block this package's own
straightforward finite-mode fix on an upstream design decision it doesn't need. **Cut in two:**
this package (`IP-9170`) fixes only the finite-mode digit, gated on `GAME_MODE == 0` so Infinite
Mode's own row-0 col-4 cell is left completely untouched (whatever `_score_bar` baked there
persists exactly as it does today — no behavior change for Infinite Mode, positive or negative).
The Infinite-Mode-HUD question itself is **not** resolved here — it is named as an Open Question
for `03-architecture-design-synthesis`/`06-feature-specification` to actually decide (does
Infinite Mode's slot show a running count instead, a fixed decorative glyph, get removed/blanked,
or something else — a real design choice, not a mechanical fix), filed back to the backlog as a
narrower successor to `BL-0139`'s own second half.

**Cut and rationale — one package, `IP-9170`, owned by `08-code-implementation`:** the fix is a
runtime write (`update_status_disp`, `asm_game.py`), not data — `WORLD_SCALE` is read and written
to tile col 4 the same way `CARROTS_COUNT` is already written to col 2 two lines above it
(`TL_DIGIT_0 + value`, direct `LD_HL_nn`/`LD_HL_A` write, no new subroutine needed since the
existing digit-write pattern already covers a single-digit 0-9 range and `WORLD_SCALE`'s own
range is 2-9, per its own existing comment). This belongs to the code peer, not content —
`tilemaps.py`'s baked `"-9"` glyph itself is untouched (it's the correct fallback for the one
frame before `update_status_disp` first runs, and for every other `GAMESTATE`, exactly mirroring
`_score_bar`'s existing carrot/score digit placeholders' own established convention).

**Supersession sweep:** nothing is retired (`WORLD_SCALE`'s own semantics are unchanged, this is
an additive HUD write); swept `asm_game.py`/`tilemaps.py` for every other row-0, col-4 writer —
none exists beyond `_score_bar`'s own bake, confirmed clean.

**Authorization:** **not authorized** — new remediation package for a post-bootstrap finding
(`BL-0139`), not covered by any standing go-ahead; awaits an explicit G3 user decision.

## Infinite Mode HUD target-digit convention (`BL-0144`, planned 2026-07-17)

**Source:** `07-implementation-planning` run #213's own split of `BL-0139` — the design question
`IP-9170` deliberately left open (what should Infinite Mode's HUD col-4 cell show, since it has
no fixed carrot ceiling). **User decision, 2026-07-17: show the running treasure count.**

**Verb inventory:** *render* only, same class as `IP-9170`.

**Scope note — single-digit constraint inherited from the existing HUD format:** the target-digit
cell is exactly one tile (col 4); `RUNNING_TREASURE_COUNT` is a 2-byte WRAM counter that can
exceed 9 in a long-running Infinite Mode session. Showing the value mod 10 (the low decimal
digit) is the only fit within the existing one-cell format without widening it — the user's own
decision text named this option explicitly ("`RUNNING_TREASURE_COUNT` (or its low digit)"). A
genuinely multi-digit display would need to claim additional HUD cells (a real layout change,
out of this package's own scope — named as a Risk, not silently expanded into).

**Cut and rationale — one package, `IP-9180`, owned by `08-code-implementation`:** mirrors
`IP-9170`'s own shape exactly — a `GAME_MODE`-gated conditional inside `update_status_disp`, this
time the Infinite Mode branch (`GAME_MODE != 0`) rather than the finite-mode branch `IP-9170`
already added. Both branches now live side-by-side in the same routine, sharing the same
`SCORE_DIRTY`-gated redraw trigger. No split considered — one routine, one coherent change,
same test-authoring pattern as `IP-9170`.

**Supersession sweep:** nothing retired; swept for any other Infinite-Mode-specific row-0 writer
— none exists beyond this package's own new branch.

**Note:** `RUNNING_TREASURE_COUNT mod 10` needs a repeated-subtraction reduction (no `DIV`/`MUL`
on SM83), mirroring `inf_mod9`'s own established technique (`asm_game.py`, `IP-1106`) — a
`mod 10` variant of the same pattern, not a new technique.

**Authorization:** **not authorized** — new remediation package resolving `BL-0144`, not covered
by any standing go-ahead; awaits an explicit G3 user decision.

## Infinite Mode Combat Sub-Mode (`FS-112`/`FEAT-11000`/`EP-6000`, `ADS-002`/`MSTR-001` C11/`BL-0133`, planned 2026-07-17)

New capability grounded in `ADS-002`: an explicitly opt-in combat layer inside Infinite Mode —
mob materialization/defeat, ranged weapon fire/hit resolution, player health with a non-lethal
setback, a treasure-spent healing economy, and combat-state save persistence. Baselined as
`FR-11100`–`FR-11600`/`NFR-1500`/`NFR-4500` (`04-requirements-engineering`); catalogued as
`FEAT-11000` (`05-feature-decomposition`); specified in full as `FS-112`
(`06-feature-specification`), which carried forward 3 Open Questions rather than resolving them
prematurely.

### Verb inventory (mandatory — this capability spans generate/render/act/persist/gate)

| Verb | Owner | Notes |
|---|---|---|
| **Generate** (per-region mob presence/type/position draw, hooked into `inf_ensure_window`) | [IP-1121](packages/IP-1121-infinite-mode-combat-mob-materialization-and-rendering.md) | Mirrors `IP-1101`'s own per-region reseed-chain discipline — a new sequential `gw_prng_step` draw in the same chain treasure-presence already uses, independent of biome/treasure. |
| **Render** (mob sprite OAM writes, per-frame; defeat presentation) | [IP-1121](packages/IP-1121-infinite-mode-combat-mob-materialization-and-rendering.md) | Folded into the same package as *generate* — mob presence and its per-frame visual instantiation are tightly coupled (an active mob with no OAM write is not observably different from an inactive one), unlike `FS-110`'s own generate/render split, which existed because *terrain* materialization and *window/render* management were genuinely separable concerns with their own distinct WRAM state. No equivalent separable seam exists here. |
| **Render** (new mob/projectile tile art) | [IP-1125](packages/IP-1125-combat-sprite-content.md) | Content-scoped (pixel art + `build_tile_data()` registration), owned by `08-content-authoring` per this project's established code/content split (mirrors `IP-1030`/`IP-1031`). |
| **Render** (player-health HUD, reusing existing heart tiles) | [IP-1123](packages/IP-1123-infinite-mode-combat-player-health-and-economy.md) | Zero new tile-art cost (`R218`/`ADS-002`) — folded into the health/economy package, not split out, since the HUD write and the health value it displays are one coherent concern. |
| **Act** (fire input, projectile update, hit resolution against mobs) | [IP-1122](packages/IP-1122-infinite-mode-combat-weapon-fire-and-hit-resolution.md) | Reuses `check_collisions`' own asymmetric point-in-box technique (`R115`) — no new hitbox model. |
| **Act** (mob contact damage, non-lethal setback trigger) | [IP-1123](packages/IP-1123-infinite-mode-combat-player-health-and-economy.md) | Folded with the health/economy package — damage-taking and the health value it decrements are the same concern; the setback is health reaching zero, not a separable mechanic. |
| **Persist** (combat state: mob table, weapon tier, player health) | [IP-1124](packages/IP-1124-infinite-mode-combat-save-persistence.md) | Mirrors `IP-1104`'s own version-byte-bump pattern exactly. **Projectile state is explicitly not persisted** (`ADS-002`: "transient, generation-time-only, never persisted," mirroring `INF_MZ_RESULT`'s own precedent) — a deliberate exclusion, not an oversight. |
| **Gate** (the new `COMBAT MODE CONFIRM` state, `COMBAT_MODE` flag) | [IP-1120](packages/IP-1120-infinite-mode-combat-mode-gating.md) | **Fully planned 2026-07-17** — see the resolved architecture-gap note below (`GDS-01` §4e). Sets a flag `IP-1121` already defines and consumes; did not itself need to exist before `IP-1121`–`IP-1125` could be planned/built and tested (tests force `COMBAT_MODE` directly, mirroring how `GAME_MODE`/`INF_WINDOW` are already force-set in `test_rom.py` today). |
| **Review** | Deferred to `09-content-review` once `IP-1125`'s sprite art ships — not this stage's own scope to package. |

### A genuine architecture gap found during planning — resolved same increment (`GDS-01` §4e)

`FS-112`'s own Open Question 1 named the gating UI's exact mechanism as undecided (a three-state
`MM_CURSOR` cycle vs. a new confirmation screen) and routed it to this stage. Direct re-read of
[GDS-01 §4d](../architecture/01-concept-of-play.md#4d-new-game-mode-choice-finite--infinite--delta-for-bl-0113-decided-2026-07-14)
found it states, as a load-bearing fact, that `MODE SELECT` "presents **finite** and **infinite**"
— a closed, two-option description. Adding a third, real option was not merely an implementation-
level byte-encoding choice this stage was free to make (the class `ADR-0015`'s own precedent
reserves for `07`/`08`) — it would have changed what `GDS-01` itself asserts the screen offers,
the same class of "architecture document states a fact this pass would falsify" gap `BL-0113`
itself was originally filed to close for `MODE SELECT`'s own existence. Per this skill's own
charter ("An unimplementable spec or a conflict found while planning routes upstream — never
planned around quietly"), this pass did not decide the mechanism itself or silently extend
`MM_CURSOR`'s range — **routed to `03-architecture-design-synthesis`** (`BL-0146`), which
returned the same day with **`GDS-01` §4e**: a new `COMBAT MODE CONFIRM` state, not a widened
`MODE SELECT` cursor — keeping "which world" and "combat on/off" on separate axes. `IP-1120` is
now re-planned in full against this decision (see the package's own §6/§7/§8/§10). This gap never
blocked the other five packages — none of them read or depend on the exact gating mechanism, only
on the `COMBAT_MODE` flag `IP-1121` defines directly.

### Supersession sweep

This capability does not retire or replace an existing model — it is purely additive, gated
entirely behind a new `COMBAT_MODE` flag that defaults to 0 (mirrors `GAME_MODE`'s own
boot-cleared convention). Swept `asm_game.py` for every site that could be affected by a new mob
table, projectile record, or player-health field colliding with existing WRAM/OAM usage: no
existing routine reads or writes the WRAM range this delta claims (`0xC6B5`–`0xC6DA`, immediately
following `MUSIC_BASE_HI`'s own end at `0xC6B4`); no existing OAM-write routine iterates past
`COLL_COUNT`'s own entries plus the player, confirmed by direct read of `update_oam`'s own loop
bounds — mobs/projectile need their own new OAM-write loop, not an extension of an existing one
that could silently overrun. Confirmed clean.

### Work units and package cut

| Work unit | Package | Owner | Depends on |
|---|---|---|---|
| Mob presence/type/position draw (per-region, hooked into `inf_ensure_window`) + per-frame mob OAM rendering + non-graphic defeat presentation | [IP-1121](packages/IP-1121-infinite-mode-combat-mob-materialization-and-rendering.md) | `08-code-implementation` | `IP-1101`/`IP-1102` (both `VERIFIED`); `IP-1125` (mob sprite tile index) |
| Mob/projectile sprite pixel art + `build_tile_data()` registration | [IP-1125](packages/IP-1125-combat-sprite-content.md) | `08-content-authoring` | None (new tile indices only, no dependency on any combat logic package) |
| Fire input (A button), projectile spawn/update, hit-test against the mob table | [IP-1122](packages/IP-1122-infinite-mode-combat-weapon-fire-and-hit-resolution.md) | `08-code-implementation` | `IP-1121` (the mob table this resolves hits against); `IP-1125` (projectile sprite tile index) |
| Player health field, HUD write (reused heart tiles), mob-contact damage, non-lethal setback, treasure-spend healing economy | [IP-1123](packages/IP-1123-infinite-mode-combat-player-health-and-economy.md) | `08-code-implementation` | `IP-1121` (mob contact as a damage source) |
| Combat state save persistence (`SAVE_VERSION_VAL` bump `0x05`→`0x06`) | [IP-1124](packages/IP-1124-infinite-mode-combat-save-persistence.md) | `08-code-implementation` | `IP-1121`/`IP-1122`/`IP-1123` (persists their combined state) |
| New `COMBAT MODE CONFIRM` state, `COMBAT_MODE` gating UI | [IP-1120](packages/IP-1120-infinite-mode-combat-mode-gating.md) | `08-code-implementation` | `IP-1121` (the flag it sets); `IP-1100` (`VERIFIED`, `ms_infinite`'s transition retargeted) |

**Split rationale:** six packages, cut along the verb-inventory seams above, deliberately
*not* mirroring `FS-110`'s own five-package generate/render/persist/gate split one-for-one —
this capability's own generate/render coupling for mobs is tighter (folded into one package,
`IP-1121`) while its act/persist/gate seams are looser (three separate packages) because mob
contact-damage and the healing economy share one state field (`IP-1123`) that fire/hit-resolution
does not touch (`IP-1122`), and the gating UI initially depended on an upstream architecture
decision the other five did not (resolved same day, `GDS-01` §4e). **Considered and rejected:**
folding `IP-1122` (weapon fire) into `IP-1121`
(mob materialization/rendering) — rejected because a projectile's own update/hit-test loop is a
per-frame *player-action* concern, structurally distinct from a per-region *generation* concern,
and keeping them separate lets `IP-1122` be independently tested against a fixture mob table
without re-deriving materialization determinism in the same test. **Considered and rejected:**
splitting content (`IP-1125`) further into mob-only and projectile-only packages — rejected as
needless fragmentation; both are small, single-purpose tile additions with no independent value
apart from the code that consumes them.

**Critical path:** `IP-1125` → `IP-1121` → `IP-1122` → `IP-1124` (4 nodes) — the longest chain;
`IP-1123` branches off `IP-1121` in parallel with `IP-1122`, both feeding into `IP-1124`;
`IP-1120` is a fifth, parallel branch off `IP-1121`, now fully planned, independent of the
critical path's own progress.

**ROM/OAM budget (per `NFR-4500`, `R115`):** 1,378 bytes of ROM headroom and 31 of 40 shadow-OAM
entries free before this delta (post-`IP-9170`/`IP-9180`). The 6-mob-slot default (7 new OAM
entries incl. the projectile) leaves 24 free — real headroom, not asserted safe until each
package's own build confirms it (see each package's own Risks field).

**Authorization:** **all six packages AUTHORIZED** (G3, user "Yes, build all six," 2026-07-17).
Build order: `IP-1125` → `IP-1121` → `IP-1122`/`IP-1123` (parallel) → `IP-1124`; `IP-1120` in
parallel once `IP-1121` lands.

### `IP-1120` re-plan — ROM-budget remediation (`BL-0153`, 2026-07-18)

`IP-1120` was implemented by `08-code-implementation` on 2026-07-18, exactly per its own §6, and
found structurally correct — but a full build overflowed the 32768-byte ROM by 542 bytes. The
package's own §13 Risks cited the 1,378-byte headroom figure from this TWBS's own line above,
current when `IP-1120` was first planned (2026-07-17) but stale by the time it was built: `IP-1122`
and `IP-1123` had since landed (2026-07-18), leaving only 866 bytes. More load-bearing than the
stale figure: the package's own `combat_mode_confirm_screen()` — despite reusing existing font
tiles and palette 2, "zero new tile art or palette entries" per its own §6 — still had to pay the
**fixed per-screen `ALL_SCREENS` array cost** (576 tile bytes + 576 attr bytes = 1,152 bytes),
since `build_rom.py`'s own screen-emission loop (`for name, fn in ALL_SCREENS: ... rom.emit(b)`)
has no special case for content novelty — it emits a full array per registered entry regardless.
This is the exact same class of gap `BL-0134` already surfaced for `IP-1022`'s four new
finite-mode screens, and this planning pass repeats that precedent's own remediation shape rather
than re-deriving it from scratch: check for a mechanical recovery first, escalate to a design
change only if none suffices.

**Mechanical recovery checked and ruled out:** `TILE_DATA_TILES`'s own trim slack (the technique
`IP-9150` already used once) is at most ~48 bytes today (a handful of unused trailing tile slots)
— nowhere near the 542-byte shortfall.

**`ADR-0020`'s procedural-fill technique checked and ruled out:** that pattern compresses a
*repeating terrain formula* (a per-tile modulo computation) into a small parameter block plus a
runtime fill loop — it fits `IP-1022`'s four biome screens because their content **is** a formula.
`COMBAT MODE CONFIRM`'s content is four lines of static menu text on a blank background; there is
no repeating formula to extract, so this technique does not apply here.

**Design change adopted:** `COMBAT MODE CONFIRM` does **not** register its own `ALL_SCREENS`
entry at all. Instead it **reuses `mode_select_screen`'s own already-registered tile/attr array**
as its base (the two states share almost the entire static layout — blank background, the same
border rows 2/14, the same row-7/row-9 label positions) and draws its own differing text (the
title plus the "NO"/"YES" labels) **at runtime**, overlaying the reused "BUNNY QUEST"/"FINITE"/
"INFINITE" text — the same "static base + a small runtime overlay" technique `draw_sse_digits`/
`draw_ise_digits` already use for their own dynamic digit content, just applied to a small
fixed-literal string instead of a computed digit. This costs three tiny inline data blobs (12 + 6
+ 8 = 26 bytes, the row-7/row-9 blobs padded with blank tiles so a shorter replacement string
fully overwrites the longer original with no separate blank pass) plus a `memcpy`-based writer
(reusing the existing `memcpy` subroutine verbatim) — on the order of 90-100 bytes total, against
`combat_mode_confirm_screen()`'s own 1,152-byte array cost. Net effect: `IP-1120`'s own total ROM
growth drops from ~1,408 bytes (1,152 screen + ~256 code) to roughly 260-320 bytes, comfortably
inside the 866-byte headroom with several hundred bytes to spare. `tilemaps.py` is removed from
this package's own file set entirely — `combat_mode_confirm_screen()`/`ALL_SCREENS` are no longer
touched. See the re-planned package's own §5/§6/§13 for the full mechanism.

**Supersession-sweep note:** this re-plan does not retire or generalize any existing model — it
narrows `IP-1120`'s own original design to avoid a cost the original design didn't need to pay,
with no change to any other package's own interface or assumption. No sweep re-run needed.

## Infinite Mode Combat Sub-Mode delta — mob movement + post-contact protection (`FS-112`/`FEAT-11000`/`EP-6000`, `FR-11210`/`FR-11410`, `BL-0156`/`BL-0158`, planned 2026-07-19)

Two new leaves baselined this same session, both closing user-filed `00-intake` gaps found by
direct play rather than upstream architecture/research drift: `FR-11210` (mobs currently never
move once materialized) and `FR-11410` (sustained mob contact re-triggered the existing damage
decrement every frame with no separation mechanic, resolving a full health-loss-and-setback cycle
in 3-4 real frames — imperceptibly fast). Both folded into `FS-112`'s own field set
(`06-feature-specification`, same session) rather than a new spec. `FS-112`'s own **Open
Question 4** (does an already-adjacent mob keep re-attempting movement) is resolved by this
planning pass, not left open into `08` — see the work-unit notes below.

### Verb inventory (mandatory)

| Verb | Owner | Notes |
|---|---|---|
| **Act** (mob movement toward the player, per-frame recomputation) | [IP-1126](packages/IP-1126-infinite-mode-combat-mob-movement.md) | New verb this delta introduces — mobs previously had no per-frame behavior of their own once materialized. |
| **Act** (post-contact invincibility, knockback, per-mob cooldown) | [IP-1127](packages/IP-1127-infinite-mode-combat-post-contact-protection.md) | Extends the existing contact-damage `Act` verb `IP-1123` already owns, rather than being folded into it — see split rationale below. |
| **Generate / Render / Persist / Gate / Review** | Unchanged from the original six-package tranche — none of these verbs are touched by this delta. Mob *generation* (`IP-1121`) and *rendering* (`IP-1121`) are unaffected: movement only changes a materialized mob's position field after the fact, not how it is drawn (`inf_mob_render` already reads whatever `MOB_DATA` currently holds). Combat-state *persistence* (`IP-1124`, `NOT STARTED`) is unaffected in scope — mob position was already going to be part of its own save-format bump; this delta does not add a new persistence obligation, only a new writer of the same field. |

### A design-level ambiguity resolved by this pass, not left to `08` (`FS-112` Open Question 4)

`FS-112`'s own Open Question 4 named a genuine ambiguity: does an already-adjacent mob keep
re-attempting movement (a jitter risk) or hold still once contact is established? Per this
skill's own charter, an FS-level Open Question that resolves to an "either answer satisfies the
Acceptance Criteria" implementation-level choice is exactly this stage's own act to make (`FS-112`
§19 itself names `07-implementation-planning` as the resolving stage). **Decided: a mob holds
still once its position exactly equals the player's own position** (checked before each
recomputation — if already coincident, skip the step) — the simpler, lower-risk choice: it avoids
any visual jitter, costs strictly less per-frame work than always-recompute, and composes cleanly
with `IP-1127`'s own knockback (a knocked-back player is, by construction, no longer coincident
with the mob, so movement resumes naturally on the next recomputation without any special-case
code). Recorded in `IP-1126`'s own §6/§10; `FS-112`'s Open Question 4 should be marked resolved
when this package ships.

### Supersession sweep

Neither package retires or widens an existing model. **`IP-1126` swept for every site touching
`MOB_DATA`'s own x/y fields** (`inf_materialize_mobs`, `inf_mob_render`, `inf_projectile_hittest`,
`inf_mob_contact_check`) — confirmed none of them assume a mob's position is write-once-at-
materialization; all four already re-read `MOB_DATA`'s own current bytes fresh each frame/call
rather than caching a stale copy, so a second writer (this delta's own movement routine) is safe
to add without touching any of the four. **`IP-1127` swept for every site touching
`inf_mob_contact_check`/`PLAYER_HEALTH`** (only `inf_mob_contact_check` itself and
`inf_health_setback`, both `IP-1123`) — confirmed clean; no other routine reads `PLAYER_HEALTH` or
decrements it, so gating the existing decrement is a local change with no distant side effect.
**Deliberately avoided a supersession risk, not just checked for one:** `IP-1127`'s own per-mob
contact-tracking state is a *new, parallel* table (`MOB_CONTACT_FLAGS`, one bit per slot, same
indexing as `MOB_DATA`) rather than widening `MOB_DATA`'s own existing 5-byte-per-slot stride —
widening the stride would require re-deriving the slot-advance arithmetic in `IP-1121`/`IP-1122`/
`IP-1123`'s own already-`VERIFIED`/`COMPLETE` code (each currently assumes exactly 5 bytes per
slot via fixed `INC_HL` counts), a real, broad, avoidable risk this design sidesteps entirely by
construction rather than by a sweep proving it's safe after the fact.

### Work units and package cut

| Work unit | Package | Owner | Depends on |
|---|---|---|---|
| Per-frame mob movement recomputation (grid-aligned single-step, adjustable speed/interval, holds still once coincident with the player) | [IP-1126](packages/IP-1126-infinite-mode-combat-mob-movement.md) | `08-code-implementation` | `IP-1121` (`VERIFIED` — the `MOB_DATA` table this reads/writes) |
| Post-contact invincibility + knockback + per-mob cooldown, combined | [IP-1127](packages/IP-1127-infinite-mode-combat-post-contact-protection.md) | `08-code-implementation` | `IP-1121` (`VERIFIED` — `MOB_DATA`); `IP-1123` (**`COMPLETE`, not yet `VERIFIED`** — `inf_mob_contact_check`/`PLAYER_HEALTH` this package modifies) |

**Split rationale:** two packages, not one, despite both being small and both extending the same
combat sub-mode. **Considered and rejected: one combined package.** Rejected because the two
work units have genuinely different dependency-readiness today — `IP-1126` depends only on
`IP-1121` (`VERIFIED`, nothing blocking) while `IP-1127` depends additionally on `IP-1123`, which
is `COMPLETE` but not yet `VERIFIED` (`09-package-verification` Pass 2 owed, blocked this session
by the same-session-independence rule). Folding them into one package would make the whole thing
`BLOCKED` on `IP-1123`'s own verification even though `IP-1126`'s own work has no real
dependency on it — an avoidable coupling. The two units are also conceptually distinct (mob *AI*
vs. player *defense*), consistent with the original tranche's own verb-inventory discipline
(`Act`-mob-materialization/rendering and `Act`-weapon-fire were kept separate for the identical
reason — different concerns sharing a frame, not one mechanism).

**Critical path:** `IP-1126` is immediately `READY` once authorized (single dependency,
`VERIFIED`). `IP-1127` is `BLOCKED` until `IP-1123` reaches `VERIFIED` (Pass 2, next session) —
not on `IP-1126`; the two packages are independent of each other and may build/ship in either
order or in parallel once both are unblocked.

**ROM budget:** both are small, code-only additions (a handful of new subroutines + WRAM
constants, no new tile/screen/music data) — expected modest growth, re-affirmed at build time per
this project's own standing discipline (610 bytes headroom as of the last build, `IP-1123`'s own
`BL-0154` remediation).

**WRAM budget:** next free byte is `0xC6DE` (past `CMC_CURSOR`'s own end, `IP-1120`). `IP-1126`
claims 1 byte (`0xC6DE`); `IP-1127` claims 2 bytes (`0xC6DF`–`0xC6E0`) — see each package's own
§6 for the exact layout.

**Authorization:** **NOT AUTHORIZED.** Both packages are new scope beyond the original "Yes,
build all six" go-ahead (2026-07-17, `IP-1120`–`1125` only) — that authorization does not extend
to `FR-11210`/`FR-11410`, baselined two days later in direct response to user-filed gaps. Neither
package may be picked up by `08-code-implementation` until the user gives an explicit go-ahead,
per this skill's own charter (a package being fully specified, even `READY`, is not authorization
to build).

## Infinite Mode Combat Sub-Mode delta — weapon directionality + weapon-tier funding (`FS-112`/`FEAT-11000`/`EP-6000`, `FR-11310`/`FR-11510`, `BL-0157`/`BL-0147`+`BL-0155`, planned 2026-07-19)

Two more new leaves baselined the same session as the mob-movement/post-contact delta above, both
grounded by newly-authored `02-research-game-design`/`03-architecture-design-synthesis` passes
rather than either upstream architecture drift or a direct user-filed play-tested gap: `FR-11310`
(the shipped weapon fires left/right only, per `ADS-002`'s "Weapon Directionality Delta"/
`ADR-0021`) and `FR-11510` (`WEAPON_TIER` shipped with no funding mechanism, per `R219`). Both
folded into `FS-112`'s own field set (`06-feature-specification`, same session) rather than a new
spec.

### Verb inventory (mandatory)

| Verb | Owner | Notes |
|---|---|---|
| **Act** (weapon fire, widened to 8-directional) | [IP-1128](packages/IP-1128-infinite-mode-combat-weapon-directionality.md) | Widens the existing `Act`-fire verb `IP-1122` already owns — not a new verb, a wider version of one that already exists. |
| **Act** (weapon-tier funding spend) | [IP-1129](packages/IP-1129-infinite-mode-combat-weapon-tier-funding.md) | Sibling to the existing `Act`-heal-spend verb `IP-1123` already owns (`inf_heal_spend`) — same currency, different consumer, kept as its own separate action mirroring the split already established between healing and (now) tier funding. |
| **Generate / Render / Persist / Gate / Review** | Unchanged from the tranche so far — none of these verbs are touched by this delta. Mob generation/rendering/movement (`IP-1121`/`IP-1126`) and post-contact protection (`IP-1127`) are all unaffected: neither new leaf touches `MOB_DATA` or `PLAYER_HEALTH`. Combat-state *persistence* (`IP-1124`, `NOT STARTED`) is unaffected in scope — `WEAPON_TIER`/the new facing fields were already going to ride whatever save-format bump `IP-1124` eventually ships (the facing fields are transient/derived from movement, not save-worthy state; `WEAPON_TIER` was already in scope for persistence since `IP-1122`). |

### Supersession sweep

**`IP-1128` repurposes an existing model** (`PROJ_DIR`'s own 2-value left/right encoding) —
mandatory sweep run and recorded in the package's own §7: grepped every reference to `PROJ_DIR` in
both `asm_game.py` and `test_rom.py`, confirmed exactly two production-code consumers (both
rewritten by this package) and confirmed `inf_projectile_hittest` never reads it (reads only
`PROJ_X`/`PROJ_Y`). Found one required, pre-named test correction (`T30.b`'s own `dir=0` assertion
for a leftward fire, which must change under the new raw-signed-step encoding) — named explicitly
in the package rather than left for `08` to rediscover via a failing test. **`IP-1129` introduces
and supersedes nothing** — `WEAPON_TIER`'s own existing shape is unchanged, only a second writer
(alongside the existing boot-init) is added; confirmed clean by direct grep.

### Work units and package cut

| Work unit | Package | Owner | Depends on |
|---|---|---|---|
| Movement-derived 8-directional weapon fire, diagonal projectile motion via simultaneous independent per-axis stepping | [IP-1128](packages/IP-1128-infinite-mode-combat-weapon-directionality.md) | `08-code-implementation` | `IP-1122` (`VERIFIED` — `PROJ_ACTIVE`/`PROJ_X`/`PROJ_Y`/`PROJ_DIR`, the last repurposed in place); `ADR-0021` (the binding design decisions this package implements) |
| Treasure-spent weapon-tier funding, spending even at the cap (mirrors the healing-spend precedent, not a no-op) | [IP-1129](packages/IP-1129-infinite-mode-combat-weapon-tier-funding.md) | `08-code-implementation` | `IP-1122` (`VERIFIED` — `WEAPON_TIER`); `IP-1103` (`VERIFIED` — `RUNNING_TREASURE_COUNT`) |

**Split rationale:** two packages, not one, mirroring the `IP-1126`/`IP-1127` split precedent
immediately above for the identical reason class: the two work units are conceptually distinct
(weapon *aiming* vs. the treasure *economy*) and have independent dependency-readiness — both
happen to depend only on already-`VERIFIED` packages today (`IP-1122`, `IP-1103`), so unlike
`IP-1126`/`IP-1127`, this split is not forced by a readiness gap, but the conceptual-independence
rationale (mirroring `Act`-mob-materialization/`Act`-weapon-fire's own original split, and
`FR-11210`/`FR-11410`'s own kept-separate precedent) still applies on its own: a reviewer or future
package should be able to reason about weapon aiming without also loading the treasure-economy
mechanism into the same diff, and vice versa.

**Critical path:** both `IP-1128` and `IP-1129` are immediately `READY` once authorized — neither
has any `BLOCKED` dependency (unlike `IP-1127`, both dependencies here are already `VERIFIED`).
Independent of each other and of `IP-1126`/`IP-1127`; may build/ship in any order or in parallel
once authorized.

**ROM budget:** both small, code-only additions (`IP-1128`: one restructured subroutine plus a
rename, three new WRAM bytes, no new tile/screen/music data; `IP-1129`: one new subroutine
mirroring an existing one's shape, zero new WRAM) — expected modest growth, re-affirmed at build
time. Headroom as of the last build (`IP-1126`'s own implementation): 354 bytes.

**WRAM budget:** next free byte is `0xC6DF` (past `IP-1126`'s own `MOB_MOVE_TIMER` end, `0xC6DE`).
`IP-1128` claims 3 new bytes (`0xC6DF`–`0xC6E1`: `PLAYER_FACING_X`/`PLAYER_FACING_Y`/
`PROJ_STEP_Y`) plus repurposes `PROJ_DIR`'s own existing `0xC6D8` in place (renamed
`PROJ_STEP_X`, no new byte). `IP-1129` claims zero new bytes. **Named collision, not hidden:**
`IP-1128`'s own `0xC6DF`–`0xC6E0` claim overlaps `IP-1127`'s own still-`BLOCKED`,
still-unauthorized prospective claim of the identical range for `PLAYER_INVINCIBLE`/
`MOB_CONTACT_FLAGS` — three packages (`IP-1127`/`IP-1128`, plus whichever of the two builds
second) are all planned against a WRAM budget that has not yet been serialized by build order.
This is a normal consequence of planning multiple packages against the same free-byte frontier in
parallel, not a defect in any one package's own plan — whichever of `IP-1127`/`IP-1128` builds
first legitimately claims the range in the real `GDS-07` map; the other's own package doc requires
a routine address re-derivation at `08-code-implementation` time (a `grep`-and-update, not a
redesign).

**Authorization:** **NOT AUTHORIZED.** Both packages are new scope beyond the original "Yes,
build all six" go-ahead (2026-07-17, `IP-1120`–`1125` only), the same class as `IP-1126`/`IP-1127`
before them. Neither package may be picked up by `08-code-implementation` until the user gives an
explicit go-ahead.

## `BL-0170` — Point-in-box hit-test duplication (refactor)

**Verb inventory:** not applicable — a single-verb structural cleanup (de-duplicate), not a new
capability; no generate/render/navigate/persist/review split needed.

**Supersession sweep:** `grep -n "CP_n(8); rom.J[RP]_NC\|CP_n(16); rom.J[RP]_NC" asm_game.py`
confirms exactly three inlined point-in-box tests exist in the current tree: `check_collisions`
(~line 1223-1230), `inf_projectile_hittest` (~line 3673-3676), `inf_mob_contact_check`
(~line 3758-3763). No fourth site found — the sweep is clean.

**Corrected scope, found during this planning pass (not the originating backlog entry's own
framing):** direct reconstruction of each site's actual arithmetic shows only **two of the three
are true duplicates**. `check_collisions` and `inf_mob_contact_check` both compute
`(register-held point) − (WRAM-held origin)` — the box is anchored on `PLAYER_X`/`PLAYER_Y`
(a static, contiguous WRAM pair) and the point being tested is whatever the per-slot loop just
read into `E`/`D` (item or mob position). `inf_projectile_hittest` computes the **reverse
order**, `(WRAM-held point) − (register-held origin)` — the box is anchored on the mob's own
position (already in `E`/`D` from the loop read) and the point being tested is the static
`PROJ_X`/`PROJ_Y` pair. Unsigned 8-bit subtraction is not commutative for this bounded-range
test (`a−b mod 256 < N` and `b−a mod 256 < N` are different predicates), so the two orders
cannot share one subroutine without changing `inf_projectile_hittest`'s own observable behavior
— which a refactor must never do.

**Decomposition, one package:**

| Work unit | Package | Owning peer | Depends on |
|---|---|---|---|
| Extract `pib_reg_minus_origin` (the shared "register-point vs. WRAM-origin" test); rewrite `check_collisions` and `inf_mob_contact_check` to call it; leave `inf_projectile_hittest` unmodified (its own inlined test is not a duplicate of anything else — extracting a single-use routine would add a `CALL`'s worth of body overhead for zero de-duplication benefit, a net ROM-budget loss, not a refactor win) | [IP-8010](packages/IP-8010-point-in-box-hittest-deduplication.md) | `08-refactoring` | none (both call sites are in `asm_game.py`, no upstream dependency) |

**Split rationale:** one package — the two genuinely-duplicated call sites are small, share one
subroutine, and there is no natural seam to split them across; `check_collisions` and
`inf_mob_contact_check` must change together or the equivalence proof (byte-delta prediction,
full-suite regression) can't be reasoned about as one unit.

**ROM budget:** expected small **net decrease** — two ~9-10-byte inlined sequences replaced by
two 3-byte `CALL`s plus one ~16-18-byte shared subroutine body (exact figures measured at build
time, per the package's own equivalence contract); a positive contribution against the tranche's
current 98-byte headroom (`VR-1127`), not a cost. `inf_projectile_hittest` is untouched — zero
byte impact there.

**Authorization:** **NOT AUTHORIZED.** Refactoring packages carry no bootstrap carve-out — `IP-8010`
requires the user's own explicit, per-package go-ahead before `08-refactoring` may execute it,
regardless of severity or how small the change is.

## `BL-0171` — Absolute-delta-from-player computation duplication (refactor)

**Verb inventory:** not applicable — single-verb structural cleanup.

**Supersession sweep:** `grep -n "label('imv_a[xy]\|label('ikb_a[xy]" asm_game.py` confirms
exactly two inlined instances, both computing `|point − PLAYER_X/Y|` on each axis via the
identical compare/branch/subtract sequence. No third site found.

**Decomposition, one package:**

| Work unit | Package | Owning peer | Depends on |
|---|---|---|---|
| Extract `abs_delta_from_player` (shared absolute-delta computation); rewrite `inf_mob_move`'s own `imv_ax_*`/`imv_ay_*` block and the knockback block's own `ikb_ax_*`/`ikb_ay_*` block (inside `inf_mob_contact_check`) to call it | [IP-8020](packages/IP-8020-abs-delta-from-player-deduplication.md) | `08-refactoring` | none |

**Split rationale:** one package — both call sites change together, sharing one subroutine; no
natural seam to split.

**ROM budget:** expected net decrease (larger than `IP-8010`'s, since the duplicated block here
is roughly 2.5x the size) — exact figure measured at build time.

**Authorization:** treated as authorized under the user's own standing "continue iterating the
refactoring... don't stop to ask" instruction (same basis as `IP-8010`'s explicit "Authorized all
refactoring") — refactoring packages still carry no bootstrap carve-out; this is a user-granted
blanket go-ahead for this session's further well-scoped refactor work, not an exemption from G3
itself.

## `BL-0172` — Treasure-spend gate-and-decrement duplication (refactor)

**Verb inventory:** not applicable — single-verb structural cleanup.

**Supersession sweep:** `grep -n "RUNNING_TREASURE_COUNT.*OR_A\|OR_A.*RUNNING_TREASURE_COUNT" asm_game.py`
and direct read confirm exactly two sites share this exact gate/decrement shape — `inf_heal_spend`
and `inf_tier_spend`. No third spend-style routine exists in the current tree.

**Decomposition, one package:**

| Work unit | Package | Owning peer | Depends on |
|---|---|---|---|
| Extract `treasure_spend_gate_and_decrement` (`Z` set = gated-off/no-treasure, `Z` clear = spent); rewrite `inf_heal_spend`/`inf_tier_spend` to call it, each keeping only its own capped-increment tail | [IP-8030](packages/IP-8030-treasure-spend-gate-deduplication.md) | `08-refactoring` | none |

**Split rationale:** one package — both call sites change together.

**ROM budget:** expected net decrease (9-instruction duplicated prefix → 1 shared body + 2 small
`CALL`+`RET_Z` sequences).

**Authorization:** treated as authorized under the user's own standing "continue iterating the
refactoring... don't stop to ask" instruction (same basis as `IP-8010`/`IP-8020`).
