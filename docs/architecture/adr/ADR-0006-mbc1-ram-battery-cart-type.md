# ADR-0006 — MBC1+RAM+BATTERY cartridge type with `BUNY`-magic save format

**Status:** Accepted (as-built, mined 2026-07-06)

## Context

The ROM header declares cart type `0x03` (MBC1+RAM+BATTERY) — confirmed by direct read of
`rom.set_header()`/[GDS-02](../02-system-context.md)/[GDS-07](../07-data-model.md). SRAM save data
at `0xA000+` begins with a 4-byte magic value `BUNY` (`0x42, 0x55, 0x4E, 0x59`) used to detect a
valid prior save versus uninitialized/garbage SRAM, followed by `CUR_ZONE`, `PLAYER_X`/`PLAYER_Y`,
`CARROTS_COUNT`, `SCORE`, and `CARROT_FLAGS` (9 bytes) — confirmed field-by-field at
[GDS-07](../07-data-model.md). Notably, `PLAYER_DIR`/`PLAYER_FRAME` and per-zone score-item state
are **not** persisted (tracked separately as `BL-0018`, not a defect this ADR resolves).

## Decision

Keep MBC1+RAM+BATTERY as the save mechanism, with the `BUNY` magic-prefix format as the sole save
validity check. Any future save-format change (e.g. resolving `BL-0018`'s scope question) extends
this same header-prefixed layout rather than introducing a parallel save mechanism.

## Consequences

- Battery-backed SRAM is the standard, real-hardware-compatible way to persist progress on GBC
  cartridges — no external save-state dependency, works identically under PyBoy and (per
  assumption A2) is expected to work on real hardware.
- The magic-prefix check is a minimal but real integrity guard against reading uninitialized SRAM
  as valid save data; it is not a checksum and does not detect partial/corrupted writes mid-save
  — an accepted, unaddressed gap at this decision's scope (no evidence of a problem in practice,
  not verified either way).
- MBC1's presence (chosen for the RAM+BATTERY capability) is also what supplies the bank-switching
  hardware that [ADR-0001](ADR-0001-single-bank-rom-no-mbc-switching.md)'s future work would use —
  the save-format need and the future world-scale need share one chip choice.
