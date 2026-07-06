# R109 — Cartridge Header, Checksums & Boot Requirements

- **Document ID:** R109 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** none
- **Referenced By:** R106 (cart-type byte this topic defines)
- **Produces:** grounds `gbc_lib.py`'s `set_header()` method and header-checksum computation
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R106

## Purpose

What the cartridge header actually requires to boot at all — the one part of a ROM where a single
wrong byte hard-locks the boot ROM before any game code runs, so it must be gotten right by
construction, not caught by testing after the fact.

## Scope

Header field layout (`$0100`–`$014F`), the two checksums, the CGB flag, and this project's current
header configuration.

## Concepts

The cartridge header occupies `$0100`–`$014F` and is read by the console's boot ROM before
control ever passes to game code.[^1] Relevant fields for this project: the entry point
(`$0100`–`$0103`, conventionally `NOP; JP $0150`), the title (`$0134`–`$0142` in older layouts,
shortened as the CGB flag byte encroaches on it), the **CGB flag** (`$0143`) — `$80` = supports
CGB features but still runs on original DMG hardware, `$C0` = CGB-exclusive[^2] — the cartridge
type byte (`$0147`, e.g. `$03` = MBC1+RAM+BATTERY), ROM size (`$0148`) and RAM size (`$0149`) codes,
and two checksums: a **header checksum** (`$014D`) and a **global checksum** (`$014E`–`$014F`).

The header checksum is computed as `checksum = 0; for addr in 0x134..0x14C: checksum = checksum -
rom[addr] - 1` (8-bit wraparound); **the boot ROM verifies this checksum and refuses to run the
game if it doesn't match** — this is the one checksum that is a hard boot-blocking requirement,
not merely a convention.[^3] The global checksum (a 16-bit sum of the entire ROM excluding the two
global-checksum bytes themselves) is **not verified by the boot ROM on real hardware** and exists
mainly for tooling/completeness.

### Sources
[^1]: [The Cartridge Header — Pan Docs](https://gbdev.io/pandocs/The_Cartridge_Header.html), accessed 2026-07-06.
[^2]: [The Cartridge Header — Pan Docs](https://gbdev.io/pandocs/The_Cartridge_Header.html), accessed 2026-07-06.
[^3]: [rgbfix(1) — RGBDS](https://rgbds.gbdev.io/docs/v0.5.0/rgbfix.1), accessed 2026-07-06 (documents the exact checksum algorithm used by the standard header-fixing tool, matching the boot ROM's own verification).

## Operational Context

`gbc_lib.py`'s `resolve()` method computes the global checksum (confirmed by direct code read: it
sums all ROM bytes except `$014E`/`$014F` themselves, matching the "global checksum, excluded
range" convention above), and `set_header(title, cart, rsize, ramsize)` writes the title, cart
type, ROM/RAM size codes, and both checksums. `build_rom.py` calls this as
`set_header("BUNNYQUEST", cart=0x03, rsize=0x00, ramsize=0x02)` — title "BUNNYQUEST" (matching the
Bunny Quest rewrite's renaming, distinct from the stale "BUNNYGARDEN" title the pre-rewrite ROM
used), cart type `$03` (MBC1+RAM+BATTERY, R106), `rsize=$00` (32 KiB, no banking), `ramsize=$02`
(8 KiB SRAM). `test_rom.py`'s T1.1–T1.7 checks (per `Claude.md`) verify ROM size, entry point
shape, GBC flag, cart type, RAM size, and header checksum validity — this is the correct set of
boot-blocking facts to test, though (per `MSTR-001` §8 / backlog `BL-0006`) the *rest* of
`test_rom.py`'s assertions are known to test stale, pre-rewrite game semantics; the header-level
checks (T1.x) are unaffected by that staleness since header format doesn't depend on zone count.

## Implementation Guidance

- **The header checksum (`$014D`) must be recomputed any time header-region bytes change** —
  `gbc_lib.py`'s `resolve()`/`set_header()` already do this automatically; never hand-patch a
  header byte without re-running the same resolve path, or the ROM will fail to boot on real
  hardware (and on any boot-ROM-accurate emulator) even if the rest of the ROM is correct.
  PyBoy's own checksum-enforcement behavior should be spot-checked (a corrupted header should
  visibly fail rather than silently boot) so `test_rom.py`'s T1.7 check is known to be a real
  gate, not a no-op.
- **A future MBC/bank-switching change (per C7/R106) requires updating both `cart` and `rsize`**
  in the same `set_header()` call — these two fields must agree (e.g. switching to MBC5 changes
  the cart-type byte; growing past 32 KiB changes the ROM-size code) — a mismatch here is exactly
  the kind of single-byte error that silently produces an unbootable or misbehaving ROM.
- **Global checksum mismatches are not boot-blocking on real hardware** but are worth keeping
  correct anyway for tooling/diffing purposes (this document itself used a fresh rebuild's
  byte-identical match against the checked-in `BunnyQuest.gbc` as verification evidence during the
  MSTR-001 vision correction) — `gbc_lib.py` already computes this automatically, so no extra
  action is needed beyond not bypassing `resolve()`.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R106 (the cart-type byte this topic's header field encodes, and the RAM/banking facts it implies).
