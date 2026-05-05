#!/usr/bin/env python3
"""
maze_preview.py — Visualize generated maze paths on screen previews.

Shows the procedurally-generated maze path overlaid on biome screens.
Cyan line shows walkable path, magenta shows walls.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: Pillow not installed. Install with: pip install Pillow")
    sys.exit(1)

from graphics_utils import get_screen_function
from maze_generator import MazeGenerator


def render_maze_overlay(zone_id: int, maze_gen: MazeGenerator, upscale: int = 2) -> Image.Image:
    """
    Render a zone with maze path overlay.

    Args:
        zone_id: Zone 0-8
        maze_gen: MazeGenerator instance
        upscale: Scaling factor

    Returns:
        PIL Image with maze overlay
    """
    from tilemaps import ALL_SCREENS

    # Get screen function and render
    screen_name = ["garden", "forest", "meadow", "desert", "cave", "swamp", "snow_peak", "crystal_lake", "sunset_sky"][zone_id]
    screen_fn = next(fn for name, fn in ALL_SCREENS if name == screen_name)

    try:
        tiles, attrs = screen_fn()
    except Exception as e:
        print(f"ERROR rendering {screen_name}: {e}")
        return None

    if not tiles or not attrs or len(tiles) != 360:
        return None

    # Render base tilemap
    base_width, base_height = 160, 144
    tile_size = 8
    img = Image.new("RGB", (base_width, base_height), "white")

    from graphics_utils import apply_palette, get_palette, get_tile_function

    for y in range(18):
        for x in range(20):
            idx = y * 20 + x
            tile_id = tiles[idx]
            pal_id = attrs[idx]

            tile_fn = get_tile_function(tile_id)
            if not tile_fn:
                continue

            try:
                pixels = tile_fn()
            except Exception:
                continue

            palette = get_palette(pal_id, "BG")
            if not palette:
                palette = get_palette(0, "BG")
            if not palette:
                continue

            rgb_pixels = apply_palette(pixels, palette)
            tile_img = Image.new("RGB", (tile_size, tile_size))
            pixel_data = []
            for row in rgb_pixels:
                for rgb in row:
                    pixel_data.append(rgb)
            tile_img.putdata(pixel_data)

            screen_x = x * tile_size
            screen_y = y * tile_size
            img.paste(tile_img, (screen_x, screen_y))

    # Get maze for this zone
    zone_maze = maze_gen.extract_zone_path(zone_id)

    # Upscale
    if upscale != 1:
        final_width = base_width * upscale
        final_height = base_height * upscale
        img = img.resize((final_width, final_height), Image.Resampling.NEAREST)

    # Draw maze overlay
    draw = ImageDraw.Draw(img)
    tile_pixels = tile_size * upscale

    # Score bar is row 0, so maze path starts at row 1
    for y in range(1, 18):
        for x in range(20):
            maze_y = y - 1  # Adjust for score bar
            if maze_y < len(zone_maze) and x < len(zone_maze[0]):
                center_x = x * tile_pixels + tile_pixels // 2
                center_y = y * tile_pixels + tile_pixels // 2

                if zone_maze[maze_y][x]:
                    # Path: cyan circle
                    radius = 2
                    draw.ellipse(
                        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                        fill=(0, 255, 255),
                        outline=(0, 200, 200),
                    )
                else:
                    # Wall: magenta X
                    draw.line(
                        [(center_x - 2, center_y - 2), (center_x + 2, center_y + 2)],
                        fill=(255, 0, 255),
                        width=1,
                    )

    return img


def main():
    """Main entry point for maze visualization."""
    parser = argparse.ArgumentParser(description="Visualize maze paths through biomes")
    parser.add_argument("--all", action="store_true", help="Visualize all 9 zones")
    parser.add_argument("--zone", type=int, help="Visualize single zone by ID (0-8)")
    parser.add_argument("--seed", type=int, default=42, help="Maze random seed")
    parser.add_argument(
        "--output", type=str, default="previews/maze", help="Output directory"
    )

    args = parser.parse_args()

    # Generate maze
    maze_gen = MazeGenerator()
    maze_gen.generate(seed=args.seed)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    zone_names = ["garden", "forest", "meadow", "desert", "cave", "swamp", "snow_peak", "crystal_lake", "sunset_sky"]

    print(f"🌀 Generating maze visualizations (seed={args.seed})...\n")

    if args.all:
        print(f"  Rendering all 9 zones...")
        for zone_id in range(9):
            zone_name = zone_names[zone_id]
            print(f"    {zone_name:12}...", end=" ")
            img = render_maze_overlay(zone_id, maze_gen, upscale=2)
            if img:
                file = output_dir / f"{zone_id:02d}_{zone_name}.png"
                img.save(file)
                print(f"✓ {file.name}")
            else:
                print("ERROR")

    elif args.zone is not None:
        if 0 <= args.zone < 9:
            zone_name = zone_names[args.zone]
            print(f"  Rendering {zone_name}...", end=" ")
            img = render_maze_overlay(args.zone, maze_gen, upscale=2)
            if img:
                file = output_dir / f"{args.zone:02d}_{zone_name}.png"
                img.save(file)
                print(f"✓ {file.name}")
            else:
                print("ERROR")
        else:
            print(f"ERROR: Zone must be 0-8, got {args.zone}")

    else:
        parser.print_help()

    print("✅ Done!")


if __name__ == "__main__":
    main()
