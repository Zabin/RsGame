"""
music.py — Music for Bunny Quest.
A new original 16-bar adventure tune in C major.
"""

def freq(hz):
    return round(2048 - 131072 / hz)

def note(f, dur):
    """[freq_lo, freq_hi|0x80 (trigger), duration_frames]."""
    return [f & 0xFF, ((f >> 8) & 0x07) | 0x80, dur]

# Timing — about 140bpm at 60fps
EN = 7    # eighth
QN = 14   # quarter
DQ = 21   # dotted quarter
HN = 28   # half
WN = 56   # whole
RST = (0, EN)   # rest (no trigger)

# C major
C4 = freq(261.63); D4 = freq(293.66); E4 = freq(329.63); F4 = freq(349.23)
G4 = freq(392.00); A4 = freq(440.00); B4 = freq(493.88)
C5 = freq(523.25); D5 = freq(587.33); E5 = freq(659.25); F5 = freq(698.46); G5 = freq(783.99)

# Bunny Quest theme — bouncy adventure march, 4 phrases of 4 bars
SONG = [
    # Phrase A — heroic intro
    (C5, QN), (G4, EN), (G4, EN), (E5, QN), (C5, EN), (G4, EN),
    (A4, QN), (G4, QN), (E4, QN), (C4, QN),
    # Phrase B — climbing
    (D5, QN), (E5, EN), (D5, EN), (C5, QN), (A4, EN), (G4, EN),
    (F4, QN), (A4, QN), (G4, HN),
    # Phrase C — playful (high)
    (E5, EN), (G5, EN), (E5, EN), (C5, EN), (D5, EN), (F5, EN), (D5, EN), (B4, EN),
    (C5, QN), (E5, QN), (G5, HN),
    # Phrase D — descending resolve
    (F5, EN), (E5, EN), (D5, EN), (C5, EN), (B4, EN), (A4, EN), (G4, EN), (F4, EN),
    (E4, QN), (G4, QN), (C5, HN),
    # Phrase E — bridge / lower
    (E4, QN), (G4, EN), (E4, EN), (F4, QN), (A4, EN), (F4, EN),
    (G4, QN), (B4, EN), (G4, EN), (C5, HN),
    # Phrase F — finale
    (E5, EN), (D5, EN), (C5, QN), (G4, QN), (E4, QN),
    (F4, EN), (A4, EN), (G4, QN), (C4, HN),
]

def _encode_notes(notes):
    """(freq, dur) tuple list -> music_data()-format byte list. Shared by
    the main theme (music_data()) and every generated sub-theme
    (generate_theme_variations()) -- one encoder, two callers, so the
    terminal 0xFF loop-back marker convention (GDS-09) is honored
    identically everywhere."""
    md = []
    for f, d in notes:
        if f == 0:
            # rest: write a triggerless silence by using freq=0 with no trigger bit
            md += [0, 0, d]
        else:
            md += note(f, d)
    md.append(0xFF)   # loop back to start
    return md

def music_data():
    return _encode_notes(SONG)

# ── IP-1110: procedural biome-family sub-theme generation (FR-7100) ──
# Maps each named note's own freq() register value back to the real hz
# it was derived from, so transposition can shift the actual pitch
# rather than approximately inverting freq()'s own rounding.
_NOTE_HZ = {
    C4: 261.63, D4: 293.66, E4: 329.63, F4: 349.23,
    G4: 392.00, A4: 440.00, B4: 493.88,
    C5: 523.25, D5: 587.33, E5: 659.25, F5: 698.46, G5: 783.99,
}

# (semitone_shift, duration_scale) per non-Grass biome-family identity --
# ADR-0019 point 4's transform menu (transposition and/or tempo/duration
# scaling, combinable). Grass is the zero-transform anchor (IP-1110's own
# resolution of FS-111 Open Question 3): the main theme itself, not
# listed here. A starting proposal, not yet validated against
# 09-content-review's own Audio Correctness dimension -- retunable later
# as a data-only change.
THEME_TRANSFORMS = {
    'water':   (-5, 1.0),
    'sand':    (2,  1.0),
    'stone':   (-2, 0.9),
    'brick':   (5,  1.0),
    'village': (2,  1.05),
    'cave':    (-7, 0.85),
    'desert':  (0,  0.95),
    'plains':  (4,  1.0),
}

def _transpose(f, semitones):
    """Shift a note's own freq() register value by `semitones`, via its
    real hz (not an approximate inversion of freq()'s own rounding).
    Rests (f == 0) and a zero shift both pass through unchanged."""
    if f == 0 or semitones == 0:
        return f
    hz = _NOTE_HZ[f]
    return freq(hz * (2 ** (semitones / 12)))

def generate_theme_variations(main_theme=SONG, transforms=THEME_TRANSFORMS):
    """Build-time (ROM-build) generation of the eight non-Grass biome-
    family sub-themes -- transposition and/or uniform duration scaling
    of the existing main theme (ADR-0019 point 4). No independently-
    composed melodic material (FR-7100's own Acceptance Criteria: every
    generated sequence must be a pure transform of the main theme's
    own data). Returns a dict keyed by identity name, each value a
    music_data()-format byte list.

    Every transposed frequency is asserted to stay within freq()'s own
    representable 11-bit range (0-2047) -- note()'s own encoding masks
    the high byte to 3 bits (`& 0x07`), so an out-of-range value would
    silently truncate rather than raise, corrupting playback instead of
    failing the build loudly.
    """
    variations = {}
    for identity, (semitones, dur_scale) in transforms.items():
        notes = []
        for f, d in main_theme:
            nf = _transpose(f, semitones)
            if not (0 <= nf <= 2047):
                raise ValueError(
                    f"generate_theme_variations: {identity!r}'s transposed "
                    f"frequency {nf} (from {f} at {semitones:+d} semitones) "
                    f"falls outside freq()'s representable 0-2047 range")
            nd = max(1, round(d * dur_scale))
            notes.append((nf, nd))
        variations[identity] = _encode_notes(notes)
    return variations
