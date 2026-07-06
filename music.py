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

def music_data():
    md = []
    for f, d in SONG:
        if f == 0:
            # rest: write a triggerless silence by using freq=0 with no trigger bit
            md += [0, 0, d]
        else:
            md += note(f, d)
    md.append(0xFF)   # loop back to start
    return md
