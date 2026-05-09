#!/usr/bin/env python3
"""
music_preview.py — Generate piano roll PNG visualization of game music.

Creates a visual representation of notes over time:
- Y-axis: Note frequencies (C4-B4)
- X-axis: Time in frames (with beat markers at quarter-note intervals)
- Each note: colored rectangle showing pitch and duration
- Output: previews/music_preview.png
"""

from PIL import Image, ImageDraw
from music import SONG, QN
from build_rom import YEL_L, YEL_M, YEL_D, WHITE, BLACK


def freq_to_note_name(freq_hz):
    """Map frequency to note name (C4-B4)."""
    notes_hz = {
        262: "C4", 277: "C#", 294: "D", 311: "D#", 330: "E", 349: "F",
        370: "F#", 392: "G", 415: "G#", 440: "A", 466: "A#", 494: "B4"
    }
    return notes_hz.get(freq_hz, "?")


def convert_rgb15_to_rgb888(rgb15):
    """Convert GBC RGB15 (5 bits per channel) to RGB888."""
    r = ((rgb15 & 0x1F) * 255) // 31
    g = (((rgb15 >> 5) & 0x1F) * 255) // 31
    b = (((rgb15 >> 10) & 0x1F) * 255) // 31
    return (r, g, b)


def generate_music_preview(out_path='previews/music_preview.png'):
    """Generate piano roll visualization of SONG."""

    # Parse song data (note frequency, duration tuples)
    notes = []
    current_frame = 0
    for freq_hz, duration_frames in SONG:
        notes.append((current_frame, current_frame + duration_frames, freq_hz))
        current_frame += duration_frames

    # Piano roll parameters
    total_duration = current_frame
    height_per_semitone = 15  # pixels per note
    pixels_per_frame = 1.5    # horizontal scale

    # Y-axis: 12 semitones (C4 to B4)
    note_names = ["C4", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B4"]
    freq_to_semitone = {
        262: 0, 277: 1, 294: 2, 311: 3, 330: 4, 349: 5,
        370: 6, 392: 7, 415: 8, 440: 9, 466: 10, 494: 11
    }

    # Dimensions
    canvas_width = int(total_duration * pixels_per_frame) + 100
    canvas_height = len(note_names) * height_per_semitone + 100

    # Create image
    bg_color = convert_rgb15_to_rgb888(BLACK)
    img = Image.new('RGB', (canvas_width, canvas_height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw grid and labels
    margin_left = 50
    margin_top = 40

    # Y-axis labels (note names)
    for i, note_name in enumerate(note_names):
        y = margin_top + i * height_per_semitone
        draw.text((10, y), note_name, fill=convert_rgb15_to_rgb888(YEL_L))
        # Horizontal grid line
        draw.line([(margin_left, y), (canvas_width, y)], fill=(40, 40, 40), width=1)

    # X-axis: beat markers (every 18 frames = quarter note)
    for beat in range(0, total_duration + QN, QN):
        x = margin_left + int(beat * pixels_per_frame)
        draw.line([(x, margin_top - 5), (x, canvas_height)], fill=(40, 40, 40), width=1)

    # Draw notes as rectangles
    colors = [
        convert_rgb15_to_rgb888(YEL_L),
        convert_rgb15_to_rgb888(YEL_M),
        convert_rgb15_to_rgb888(YEL_D),
    ]

    for idx, (start_frame, end_frame, freq_hz) in enumerate(notes):
        semitone = freq_to_semitone.get(freq_hz, 0)
        color = colors[idx % len(colors)]

        x1 = margin_left + int(start_frame * pixels_per_frame)
        x2 = margin_left + int(end_frame * pixels_per_frame)
        y1 = margin_top + semitone * height_per_semitone + 2
        y2 = y1 + height_per_semitone - 4

        draw.rectangle([x1, y1, x2, y2], fill=color, outline=convert_rgb15_to_rgb888(WHITE), width=1)

    # Save
    img.save(out_path)
    print(f"✅ Music preview saved → {out_path}")


if __name__ == '__main__':
    import os
    os.makedirs('previews', exist_ok=True)
    generate_music_preview()
