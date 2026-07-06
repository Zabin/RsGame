# R106 — MBC1, SRAM Enable & Battery Saves

- **Document ID:** R106 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R109 (cartridge-header cart-type byte this topic's config maps to)
- **Referenced By:** R109, every future ADR on bank-switching strategy (MSTR-001 C7)
- **Produces:** grounds `build_rom.py`'s `set_header(cart=0x03, rsize=0x00, ramsize=0x02)` call and
  `asm_game.py`'s save/load routines
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R109

## Purpose

How MBC1 SRAM enable/battery-save actually works, and — since MSTR-001's commitment C7 explicitly
anticipates outgrowing the current single ROM bank — what MBC1's ROM-banking side would require
if/when this project needs it, so that transition is planned rather than improvised.

## Scope

MBC1 RAM-enable sequence, battery-backed persistence, MBC1's ROM/RAM banking register wiring (both
the default and the large-ROM/small-RAM alternate wiring), and this project's current cart-type
configuration.

## Concepts

**RAM enable:** external (cartridge) RAM is disabled by default at power-on. Writing any byte
with `$A` in its low nibble to the address range `$0000`–`$1FFF` enables RAM access; any other
value written there disables it again.[^1] It is recommended practice to explicitly disable RAM
access before power-down/cart-removal to protect battery-backed contents from corruption.[^1]

**Battery save:** SRAM is only non-volatile if the cartridge's hardware includes a battery — this
is declared via the cartridge-header cart-type byte (R109), not by anything the ROM code does at
runtime; the ROM's job is only to enable RAM, write/read through it, and (ideally) disable it
again when done.

**MBC1 banking (relevant to the C7 growth path):** in its default wiring, MBC1 supports up to 512
KiB of ROM (32 banks of 16 KiB, banks addressed via a 5-bit register at `$2000`–`$3FFF`, with bank
0 permanently mapped at `$0000`–`$3FFF` and the selected bank at `$4000`–`$7FFF`) plus up to 32 KiB
of banked RAM (4 banks, selected via a 2-bit register at `$4000`–`$5FFF`). An alternate wiring
exists where that same 2-bit register is instead wired as *high bits* of the ROM bank number
(extending ROM addressing to 2 MiB) at the cost of only supporting a fixed 8 KiB of RAM (no RAM
banking) — a mode toggle (`$6000`–`$7FFF`) selects between the two wirings.[^2] MBC1 has a
well-known **quirk**: ROM bank number 0 cannot be selected in the `$4000`-region banking register
(a write of 0 is treated as 1) — relevant to any future banking code, since a naive "bank number =
zone index" scheme would need to skip or special-case that value.

### Sources
[^1]: [MBC1 — Pan Docs](https://gbdev.io/pandocs/MBC1.html), accessed 2026-07-06.
[^2]: [MBC1 — Pan Docs](https://gbdev.io/pandocs/MBC1.html), accessed 2026-07-06.

## Operational Context

`build_rom.py` configures the header as `set_header("BUNNYQUEST", cart=0x03, rsize=0x00,
ramsize=0x02)` — cart type `0x03` is MBC1+RAM+BATTERY, `rsize=0x00` is the 32 KiB / no-banking ROM
size code (bank 0 only, `$0000`–`$7FFF` is the entire ROM, no banking register writes needed or
used anywhere in the codebase today), and `ramsize=0x02` is 8 KiB of cartridge RAM (one bank,
matching the no-RAM-banking case).[^1] The save format (per `Claude.md`/`memory.md`) writes a
4-byte magic (`B`,`U`,`N`,`Y`) plus game state to `0xA000`+ — this is ordinary SRAM read/write
through the always-enabled 8 KiB window; the codebase's save/load routines do not appear to
explicitly write the RAM-enable sequence (`$0A` to `$0000`–`$1FFF`) before accessing SRAM,
**worth a direct-code re-check** the next time save/load code is touched, since Pan Docs states
RAM access requires this enable step and its absence would be a latent (if likely
emulator-invisible) correctness gap.

**This project currently uses none of MBC1's banking registers** — `rsize=0x00` means the entire
32 KiB ROM is bank 0, mapped statically at `$0000`–`$7FFF`, and no code anywhere writes to
`$2000`–`$3FFF` or `$4000`–`$5FFF`. This is consistent with assumption A1 (single-bank suffices
today) and is exactly the fact that will need to change once C7's world-scale growth exhausts the
current ~9.6 KB of headroom (per MSTR-001 §3).

## Implementation Guidance

- **Before any SRAM read/write, confirm (or add) the RAM-enable write** (`$0A` to any address in
  `$0000`–`$1FFF`) — audit the current save/load routines in `asm_game.py` against this
  requirement rather than assuming PyBoy's apparent success means the sequence is correct on real
  hardware.
- **Disable RAM access after save/load completes** (any non-`$0A`-low-nibble byte to the same
  range) to protect against corruption on power-loss — add this if the current code doesn't
  already.
- **When the C7 growth path actually requires more than 32 KiB:** MBC1's default wiring (32 banks
  ×16 KiB = 512 KiB, RAM banking intact) is the natural first step and requires the *least*
  change to the existing single-RAM-bank save format; only reach for the large-ROM alternate
  wiring (or a different MBC entirely, e.g. MBC5) if ROM needs genuinely exceed 512 KiB or RAM
  banking is separately needed. This decision belongs to a future ADR (per `03-architecture-
  design-synthesis`'s ownership of `docs/architecture/adr/`), grounded in this topic, once GDS-01/
  GDS-03 quantify how much ROM the C7 world actually needs.
- **Remember MBC1's bank-0-is-unselectable quirk** — a future banking scheme should not assume
  "bank number N" and "the Nth 16 KiB chunk after bank 0" are the same thing without checking this
  off-by-one.
- **`gbc_lib.py`'s `ROM` class has no banking-register emitter methods today** — adding
  bank-switch support is itself an R101-adjacent `gbc_lib.py` extension (new opcode-emission
  methods to write the banking registers), not something achievable purely at the `asm_game.py`
  level.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R109 (the cartridge-header cart-type byte this topic's `0x03` value declares).
