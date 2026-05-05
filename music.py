"""
music.py — Music data for Bunny Garden Adventure.
Edit SONG to change the melody.
QN = frames per quarter note (18 @ 60fps ≈ ♩=200bpm)
Use freq(hz) to compute GBC channel 1 frequency register values.
"""

def freq(hz):
    """Convert frequency in Hz to GBC channel 1 register value (0-2047)."""
    return round(2048 - 131072 / hz)

def note(f, dur):
    """One music entry: [freq_lo, freq_hi|0x80 (trigger), duration_frames]."""
    return [f & 0xFF, ((f >> 8) & 0x07) | 0x80, dur]

# Timing constants
QN = 18   # quarter note  (~200 bpm at 60fps)
HN = 36   # half note
EN = 9    # eighth note

# Note frequencies — C4 octave (lowered one octave from v1)
C4 = freq(261.63)
D4 = freq(293.66)
E4 = freq(329.63)
F4 = freq(349.23)
G4 = freq(392.00)
A4 = freq(440.00)
B4 = freq(493.88)

# Twinkle Twinkle Little Star — C4 range
SONG = [
    (C4, QN), (C4, QN), (G4, QN), (G4, QN), (A4, QN), (A4, QN), (G4, HN),
    (F4, QN), (F4, QN), (E4, QN), (E4, QN), (D4, QN), (D4, QN), (C4, HN),
    (G4, QN), (G4, QN), (F4, QN), (F4, QN), (E4, QN), (E4, QN), (D4, HN),
    (G4, QN), (G4, QN), (F4, QN), (F4, QN), (E4, QN), (E4, QN), (D4, HN),
    (C4, QN), (C4, QN), (G4, QN), (G4, QN), (A4, QN), (A4, QN), (G4, HN),
    (F4, QN), (F4, QN), (E4, QN), (E4, QN), (D4, QN), (D4, QN), (C4, HN),
]

def music_data():
    """Returns flat byte list: [lo, hi|0x80, dur] per note, terminated by 0xFF."""
    md = []
    for f, d in SONG:
        md += note(f, d)
    md.append(0xFF)   # loop marker — restart from beginning
    return md
