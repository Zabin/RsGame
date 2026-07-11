# Technical Work Breakdown

> **Status: ✅ Authored (first planning pass, 2026-07-07).** Owned by
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
