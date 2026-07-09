# ADR-0001 — Single 32KB ROM bank, no MBC bank switching (yet)

**Status:** **Superseded 2026-07-09 by [ADR-0011](ADR-0011-bank-switching-mbc1-default-wiring.md)**
(Accepted, as-built, mined 2026-07-06 — accurate for the bootstrap-through-v2.0 increment; this
document's content is retained unmodified as history, per this project's append-only ADR
discipline — see ADR-0011's Context for why supersession happened now.)

## Context

The shipped ROM (`BunnyQuest.gbc`) is exactly 32768 bytes — a single fixed bank, no `ROMX`
bank-switching despite the cartridge header declaring an MBC1 chip (`ADR-0006`). Confirmed by
direct build (`build_rom.py` produces a byte-identical 32768-byte file) and by
[GDS-02](../02-system-context.md)/[GDS-07](../07-data-model.md) (23148/32768 bytes used,
~9.6KB headroom, no bank-switch instructions anywhere in `asm_game.py`/`gbc_lib.py`).

[MSTR-001](../../master/MSTR-001-program-vision.md)'s corrected v2.0 vision (commitment **C7**)
sets a long-term world-scale target comparable to Zelda/Pokémon-class overworlds — a scale this
single-bank layout cannot hold. C7 was added specifically *reversing* an earlier assumption that
no bank-switching would ever be needed.

## Decision

Ship the bootstrap/current increment on a single fixed 32KB bank (MBC1 hardware present but bank
switching unused). Do not add bank-switching code speculatively ahead of a concrete need — the
9.6KB of current headroom is real, unused capacity for near-term content growth within the single
bank.

## Consequences

- Simple, deterministic build: no bank-boundary bookkeeping, no `ROMX`-target label resolution
  complexity in `gbc_lib.py`'s fixup system.
- **This decision does not survive C7 unmodified.** Reaching Zelda/Pokémon-scale world content
  will exhaust the single bank and require introducing real `ROM0`/`ROMX` bank switching — a
  future architectural change, not a bug fix. This ADR is explicitly superseded when that work is
  planned (tracked at the vision layer as C7; the concrete bank-switching design is future
  `03-architecture-design-synthesis` or `05-feature-decomposition` work, not yet scheduled).
- The MBC1 chip is already present in the header (`ADR-0006`) specifically because RAM+BATTERY
  save requires an MBC — bank switching was available "for free" in hardware terms even before
  C7 existed, it was simply unused until now.
