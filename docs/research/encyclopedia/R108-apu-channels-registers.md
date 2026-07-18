# R108 — APU Channels & Register Map

- **Document ID:** R108 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R101 (frame-timed note triggering)
- **Referenced By:** R115 (2026-07-17 — confirms channels 2–4 are entirely unused, headroom for
  combat-mode SFX, `BL-0133`)
- **Produces:** grounds `music.py`'s note encoding and `asm_game.py`'s channel-1 playback routine
- **Feature Mapping:** *(none yet)*
- **Related Topics:** none yet

## Purpose

The pulse-channel register set this project's music engine actually drives, so a future song or
a second channel is added with correct register semantics, not guessed frequency math.

## Scope

Channel 1 (pulse with sweep) register layout, the period-value frequency encoding, master
volume/panning/power registers, and this project's current single-channel usage.

## Concepts

The APU has four channels; this project uses only **Channel 1** (pulse wave with a hardware
frequency sweep unit). Its registers:[^1]

| Register | Address | Content |
|---|---|---|
| NR10 | `0xFF10` | Sweep: pace, direction, shift (unused by this project — no writes found) |
| NR11 | `0xFF11` | Bits 7–6: wave duty; bits 5–0: length timer (write-only initial value) |
| NR12 | `0xFF12` | Bits 7–4: initial envelope volume; bit 3: envelope direction; bits 2–0: envelope sweep pace |
| NR13 | `0xFF13` | Period value, low 8 bits (write-only) |
| NR14 | `0xFF14` | Bit 7: trigger (write 1 to (re)start the note); bit 6: length-enable; bits 2–0: period value, high 3 bits |
| NR50 | `0xFF24` | Master volume (bits 6–4 left, 2–0 right) + VIN routing bits |
| NR51 | `0xFF25` | Per-channel left/right panning enable bits |
| NR52 | `0xFF26` | Bit 7: master APU power; bits 3–0 (read-only): per-channel "currently active" status |

The **period value** is an 11-bit number (0–2047) split across NR13 (low 8 bits) and NR14 (high 3
bits); the channel's output frequency is `131072 / (2048 - period)` Hz.[^1] Writing NR14 with bit
7 set **triggers** (restarts) the channel using whatever NR10–NR13 currently hold — this is the
"note on" event.

### Sources
[^1]: [Audio Registers — Pan Docs](https://gbdev.io/pandocs/Audio_Registers.html), accessed 2026-07-06.

## Operational Context

`music.py`'s `freq(hz)` helper computes `round(2048 - 131072/hz)` — the exact algebraic inverse of
Pan Docs' documented frequency formula, confirming the project's period-value math is correct.
Its `note(f, dur)` helper packs a period value into the two-byte NR13/NR14 encoding Pan Docs
describes: `[f & 0xFF, ((f>>8)&0x07)|0x80, dur]` — low byte for NR13, high 3 bits plus the trigger
bit (`0x80` = bit 7) for NR14, plus a third element carrying the note's duration in frames (a
`music.py`/`asm_game.py`-level convention, not an APU register).

`asm_game.py`'s sound-init sequence writes, in order: `NR52 = 0x80` (APU power on), `NR50 = 0x77`
(max volume both channels, no VIN), `NR51 = 0xFF` (channel 1 routed to both left and right — the
only channel enabled in this register, consistent with using only channel 1), `NR11 = 0x80` (duty
50%, per Pan Docs' duty-cycle bit encoding, length-timer field left at 0), `NR12 = 0xD2` (initial
volume 13/15, decreasing envelope, sweep pace 2). Per-note playback writes only NR13 then NR14
(from the pre-packed two-byte encoding `music.py` produces) — NR10 (sweep) is never written, so
each note plays at a fixed pitch with no pitch-bend.

This project's melody is confirmed (by `music.py`'s own header comment, "A new original 16-bar
adventure tune in C major" — replacing the prior Twinkle Twinkle placeholder, consistent with the
Bunny Quest rewrite) to be a single-channel composition; channels 2 (pulse, no sweep), 3 (custom
wave), and 4 (noise) are entirely unused.

## Implementation Guidance

- **A second simultaneous voice** (harmony, a percussion/noise layer) would use Channel 2 (`NR21`–
  `NR24`, same layout as Channel 1 minus the sweep register) or Channel 4 (`NR41`–`NR44`, noise —
  different register semantics, not covered by this topic) — Channel 1's sweep register (NR10) is
  currently unused and available for a future pitch-bend effect without disturbing existing notes.
- **`NR51`'s current value (`0xFF`) already enables every channel on both stereo outputs** — adding
  a second channel's *sound* requires only writing that channel's own registers; no change to
  `NR51` is needed unless panning (not just enabling) becomes a design goal.
- **Note triggering is NR14's bit 7 — always re-write NR13 before NR14 for each new note** (as the
  current code does), since the trigger reads the period value at the moment of the NR14 write.
- **A frame-length budget for a longer/looping song** (relevant as C7 grows the game's scope) is a
  `music.py`-level bookkeeping concern, not an APU register fact — this topic covers the hardware
  side only.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R101 (note-trigger timing is frame-driven, ultimately a cycle-budget concern for the main loop).
