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


# ── Zone-specific melodies (for per-zone audio) ───────────────────────────────

# Zone 0: Garden — Cheerful major key
ZONE_0_GARDEN = [
    (G4, QN), (C4, QN), (E4, QN), (G4, QN), (C4, QN), (E4, QN), (G4, HN),
    (A4, QN), (D4, QN), (F4, QN), (A4, QN), (D4, QN), (F4, QN), (A4, HN),
    (G4, QN), (C4, QN), (E4, QN), (G4, QN), (C4, QN), (E4, QN), (G4, HN),
]

# Zone 1: Forest — Woodsy/mystical
ZONE_1_FOREST = [
    (G4, QN), (G4, EN), (A4, EN), (B4, QN), (A4, QN), (G4, QN), (E4, HN),
    (E4, QN), (E4, EN), (F4, EN), (G4, QN), (F4, QN), (E4, QN), (D4, HN),
    (G4, QN), (G4, EN), (A4, EN), (B4, QN), (A4, QN), (G4, QN), (E4, HN),
]

# Zone 2: Meadow — Peaceful/pastoral
ZONE_2_MEADOW = [
    (E4, QN), (G4, QN), (E4, QN), (G4, QN), (E4, QN), (G4, QN), (E4, HN),
    (D4, QN), (F4, QN), (D4, QN), (F4, QN), (D4, QN), (F4, QN), (D4, HN),
    (E4, QN), (G4, QN), (E4, QN), (G4, QN), (E4, QN), (G4, QN), (E4, HN),
]

# Zone 3: Desert — Middle Eastern/exotic
ZONE_3_DESERT = [
    (D4, QN), (F4, EN), (D4, EN), (G4, QN), (F4, QN), (D4, QN), (C4, HN),
    (E4, QN), (G4, EN), (E4, EN), (A4, QN), (G4, QN), (E4, QN), (D4, HN),
    (D4, QN), (F4, EN), (D4, EN), (G4, QN), (F4, QN), (D4, QN), (C4, HN),
]

# Zone 4: Cave — Minor/spooky
ZONE_4_CAVE = [
    (D4, QN), (D4, QN), (E4, EN), (F4, EN), (E4, QN), (D4, QN), (C4, HN),
    (C4, QN), (C4, QN), (D4, EN), (E4, EN), (D4, QN), (C4, QN), (B4, HN),
    (D4, QN), (D4, QN), (E4, EN), (F4, EN), (E4, QN), (D4, QN), (C4, HN),
]

# Zone 5: Swamp — Slow/murky
ZONE_5_SWAMP = [
    (C4, HN), (D4, HN), (E4, HN), (D4, HN),
    (C4, HN), (D4, HN), (C4, HN), (B4, HN),
    (C4, HN), (D4, HN), (E4, HN), (D4, HN),
]

# Zone 6: Snow Peak — Crystalline/icy
ZONE_6_SNOW = [
    (G4, EN), (G4, EN), (G4, EN), (G4, EN), (E4, QN), (F4, QN), (G4, HN),
    (E4, EN), (E4, EN), (E4, EN), (E4, EN), (D4, QN), (E4, QN), (F4, HN),
    (G4, EN), (G4, EN), (G4, EN), (G4, EN), (E4, QN), (F4, QN), (G4, HN),
]

# Zone 7: Crystal Lake — Water/flowing
ZONE_7_CRYSTAL = [
    (E4, QN), (E4, EN), (F4, EN), (G4, QN), (A4, QN), (G4, QN), (F4, HN),
    (F4, QN), (F4, EN), (G4, EN), (A4, QN), (B4, QN), (A4, QN), (G4, HN),
    (E4, QN), (E4, EN), (F4, EN), (G4, QN), (A4, QN), (G4, QN), (F4, HN),
]

# Zone 8: Sunset Sky — Warm/evening
ZONE_8_SUNSET = [
    (A4, QN), (G4, QN), (F4, QN), (E4, QN), (F4, QN), (G4, QN), (A4, HN),
    (B4, QN), (A4, QN), (G4, QN), (F4, QN), (G4, QN), (A4, QN), (B4, HN),
    (A4, QN), (G4, QN), (F4, QN), (E4, QN), (F4, QN), (G4, QN), (A4, HN),
]

# Array of all zone melodies indexed by zone (0-8)
ZONE_MELODIES = [
    ZONE_0_GARDEN,
    ZONE_1_FOREST,
    ZONE_2_MEADOW,
    ZONE_3_DESERT,
    ZONE_4_CAVE,
    ZONE_5_SWAMP,
    ZONE_6_SNOW,
    ZONE_7_CRYSTAL,
    ZONE_8_SUNSET,
]


def zone_music_data(zone):
    """Returns flat byte list for a specific zone's melody, terminated by 0xFF."""
    if zone < 0 or zone >= len(ZONE_MELODIES):
        return music_data()  # fallback to default
    md = []
    for f, d in ZONE_MELODIES[zone]:
        md += note(f, d)
    md.append(0xFF)
    return md
