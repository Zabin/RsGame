# ADR-0010 — Seed & world-scale parameter model

**Status:** Accepted (2026-07-09)

## Context

[MSTR-001](../../master/MSTR-001-program-vision.md) **C10** (v3.0) requires the world be
deterministic from a **seed** and a **world-scale** parameter, both **user-modifiable but entered
only at new-game creation and immutable for the life of that save** (**D6/D7**, per the owner's
explicit direction, 2026-07-09). **C2** (amended) requires the entry surface be the new main
menu's new-game flow, and **D1** rules out a text/dialogue engine — any entry UI must reuse
existing tile primitives (digits, cursor, arrows), not introduce a font/text system.
[R111](../../research/encyclopedia/R111-wram-banking-sm83-prng.md) grounds the PRNG this seed
initializes (xorshift-family, 2–4 bytes of state) and confirms WRAM/SRAM headroom is not a
binding constraint at any plausible scale. The adopted increment plan's §5 gates table names
"seed & scale surface details" and "scale bounds/defaults" as the residual decisions this ADR
resolves, per D6's explicit delegation ("bounds are the agent's call within hardware budgets").

## Decision

**Seed:** a **16-bit unsigned value (0–65535)**, entered as up to 5 decimal digits via the
existing digit-tile set (`TL_DIGIT_0`+, already shipped — no new tiles/font needed, satisfying
D1). A 16-bit seed gives 65,536 distinct worlds per scale value — ample variety for a casual,
short-session game (assumption A5) without requiring a wider entry UI. **A seed value of 0 is
special-cased to behave as 1 internally** before initializing the PRNG state, since xorshift-
family generators require nonzero state to avoid degenerate all-zero output — a real
implementation detail worth deciding now, per R111's citation, rather than discovering it as a
bug later.

**World scale:** a **single byte, valid range 2–9**, directly representing the side length of a
square region grid (`scale × scale` total regions) — the same **shape** as today's shipped 3×3
world, now a **player-chosen instance of it** rather than the only option. **Default: 3**
(reproducing the current world's felt size, `3×3=9` regions, as the default new-game experience —
continuity with the shipped baseline's scope, even though its specific content is generated, not
handcrafted). Bounds reasoning, grounded in R111/`BL-0019`'s headroom figures rather than
asserted: at the top of the range (scale 9, 81 regions), a region-graph WRAM working set of even
a generous 4 bytes/node (biome id + edge-validity bits) costs ~324 bytes — comfortably inside
bank-0's ~3.1 KiB of confirmed headroom (R111), with no `SVBK` banking needed at any point in this
range. The floor of 2 (4 regions) is the smallest world that preserves GDS-01's
explore-transition-collect core loop meaningfully; scale 1 (a single region, no transitions) is
excluded as degenerate relative to that loop, not for a hardware reason.

**Entry timing and surface (D7/D8/D9):** both values are entered **once**, in the new-game
creation flow reached from the main menu (the game-flow delta [GDS-01](../01-concept-of-play.md)
records), using a **digit-cursor picker** (D-pad up/down changes the selected digit/scale value,
left/right moves the cursor, A confirms) — the same interaction shape as any digit-based menu,
no new input primitive. Neither value is ever re-enterable for an existing save; changing either
means starting a new game (D7, verbatim).

**Save-format shape:** extends the `FS-101`/`IP-1010` version-byte precedent
([R106](../../research/encyclopedia/R106-mbc1-sram-battery-saves.md)'s extension,
[GDS-07](../07-data-model.md) §3's `0xA012` version guard). A new save-format version value is
introduced; the save persists **`seed` (2 bytes) + `scale` (1 byte) + a per-region collected-flags
array sized to the maximum supported scale (81 bytes, `9×9` worst case — trivial against 8 KiB
SRAM per R106's extension, so no dynamic sizing is needed)** — the world itself is **not**
persisted; it regenerates deterministically from `(seed, scale)` on load, per ADR-0009's
determinism requirement.

**Pre-upgrade saves (written before this feature ships):** the version-byte mismatch is detected
exactly as `FS-101`'s precedent already handles it, but the *response* differs from that
precedent's "default to safe empty state" choice — a pre-C10 save encodes a **fundamentally
different world model** (a fixed handcrafted 3×3 layout, not a generated one), not just a missing
field. **Decision: a pre-upgrade save is not offered on the "continue" path** — the main menu's
continue option requires a version-matching save; a mismatched save is treated as absent for
`continue` purposes (its bytes are not overwritten until the player proceeds through new-game
creation, so nothing is silently destroyed, but nothing is silently *continued* into an
incompatible world model either). This is a confident recommendation reasoned from the version
byte's existing purpose, not escalated to the user, following the `FS-101` precedent of resolving
this class of question directly.

## Consequences

- **New WRAM state**: seed (2 bytes), scale (1 byte), generation working-set (per ADR-0009) —
  all within bank-0's existing headroom (R111); no `SVBK` banking triggered by this decision.
- **New SRAM fields**: 2 (seed) + 1 (scale) + 81 (region flags, worst-case-sized) = 84 bytes,
  plus a version-byte bump — against 8 KiB SRAM, negligible (R106's extension).
- **New UI surface**: a digit-cursor seed/scale entry screen in the new-game flow — no new tiles
  beyond the existing digit set; a genuinely new screen state in
  [GDS-01](../01-concept-of-play.md)'s state machine (that level's own delta, not decided here).
- **The Python reference-generator oracle** (R305's extension) must accept `(seed, scale)` as its
  input signature directly matching this ADR's types (`u16, u8`) — a concrete interface contract
  for whoever implements the oracle module (R302's extension).
- **Does not implement anything** — the entry screen, save-format version bump, and PRNG seeding
  ship through the normal `04`→`08` path, gated by G3.
