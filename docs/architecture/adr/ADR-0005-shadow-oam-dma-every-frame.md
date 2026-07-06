# ADR-0005 — Shadow-OAM DMA every frame

**Status:** Accepted (as-built, mined 2026-07-06)

## Context

Sprite attribute data (player + collectibles) is written to a WRAM shadow buffer (`OAM_BUF`,
`0xC300`, 160 bytes) during game logic, then copied to real OAM via the DMA transfer routine every
frame inside the VBlank ISR, rather than writing OAM registers directly from mainline code
([R105](../../research/encyclopedia/R105-oam-sprites-dma.md)). This is standard GBC practice
because OAM is only safely writable during VBlank/HBlank, and DMA transfer is the fast, reliable
way to move a full 160-byte OAM image in the narrow VBlank window.

## Decision

Keep shadow-OAM + per-frame DMA as the sole sprite-update mechanism. Game logic never writes OAM
registers directly; it only ever writes `OAM_BUF` in WRAM, and the DMA transfer (triggered every
frame, unconditionally) is what makes those writes visible on screen.

## Consequences

- Sprite updates are safe regardless of when in the frame game logic runs — a real robustness
  property, since it removes an entire class of PPU-mode-timing bugs from every future
  sprite-touching change.
- The cost is a fixed per-frame DMA transfer whether or not any sprite actually changed that
  frame — accepted because the transfer is cheap relative to VBlank's budget and the
  correctness guarantee is worth more than the (unmeasured, likely negligible) savings from a
  conditional/dirty-tracking transfer.
- This decision is the reason the 40-entry OAM budget shared across player + collectibles
  ([GDS-08](../08-presentation-architecture.md) §2) is a single, simple buffer to reason about
  rather than several partial-update code paths.
