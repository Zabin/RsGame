#!/usr/bin/env python3
"""
road_preview.py — Visualize + shaped roads on zone previews.

Shows cyan + shaped roads overlaid on biome screens.
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
from road_generator import RoadGenerator, ZONE_NAMES, ZONE_ID_TO_GRID
from tilemaps import ALL_SCREENS


def render_road_overlay(zone_id: int, road_gen: RoadGenerator, upscale: int = 2) -> Image.Image:
    """
    Render a zone with road overlay.

    Args:
        zone_id: Zone 0-8 (journey order)
        road_gen: RoadGenerator instance
        upscale: Scaling factor

    Returns:
        PIL Image with road overlay
    """
    zone_row, zone_col = ZONE_ID_TO_GRID[zone_id]

    # Get screen function and render
    screen_name = [name for name, _ in ALL_SCREENS if name not in ["title", "intro", "save", "map", "victory"]][zone_id]
    screen_fn = next((fn for name, fn in ALL_SCREENS if name == screen_name), None)

    if not screen_fn:
        return None

    try:
        tiles, attrs = screen_fn()
    except Exception as e:
        print(f"ERROR rendering zone {zone_id}: {e}")
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

    # Get road for this zone
    zone_road = road_gen.get_zone_road(zone_id)

    # Upscale
    if upscale != 1:
        final_width = base_width * upscale
        final_height = base_height * upscale
        img = img.resize((final_width, final_height), Image.Resampling.NEAREST)

    # Draw road overlay
    draw = ImageDraw.Draw(img)
    tile_pixels = tile_size * upscale

    # Score bar is row 0, so road path starts at row 1
    for y in range(1, 18):
        for x in range(20):
            road_y = y - 1  # Adjust for score bar
            if road_y < len(zone_road) and x < len(zone_road[0]):
                if zone_road[road_y][x]:
                    # Road cell: draw bright cyan line
                    center_x = x * tile_pixels + tile_pixels // 2
                    center_y = y * tile_pixels + tile_pixels // 2
                    radius = 3
                    draw.ellipse(
                        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                        fill=(0, 255, 255),
                    )

    # Draw zone label
    zone_name = ZONE_NAMES[(zone_row, zone_col)]
    draw.text((10, 10), f"({zone_row},{zone_col}) {zone_name}", fill=(0, 0, 0))

    return img


def main():
    """Main entry point for road visualization."""
    parser = argparse.ArgumentParser(description="Visualize + shaped roads through biomes")
    parser.add_argument("--all", action="store_true", help="Visualize all 9 zones")
    parser.add_argument("--zone", type=int, help="Visualize single zone by ID (0-8)")
    parser.add_argument(
        "--output", type=str, default="previews/roads", help="Output directory"
    )

    args = parser.parse_args()

    # Generate roads
    road_gen = RoadGenerator()
    road_gen.generate()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    zone_names = ["garden", "forest", "meadow", "desert", "cave", "swamp", "snow_peak", "crystal_lake", "sunset_sky"]

    print(f"🛣️  Generating road visualizations...\n")

    if args.all:
        print(f"  Rendering all 9 zones...")
        for zone_id in range(9):
            zone_name = zone_names[zone_id]
            zone_row, zone_col = ZONE_ID_TO_GRID[zone_id]
            print(f"    Zone({zone_row},{zone_col}) {zone_name:12}...", end=" ")
            img = render_road_overlay(zone_id, road_gen, upscale=2)
            if img:
                file = output_dir / f"{zone_id:02d}_{zone_name}.png"
                img.save(file)
                print(f"✓")
            else:
                print("ERROR")

    elif args.zone is not None:
        if 0 <= args.zone < 9:
            zone_name = zone_names[args.zone]
            zone_row, zone_col = ZONE_ID_TO_GRID[args.zone]
            print(f"  Rendering Zone({zone_row},{zone_col}) {zone_name}...", end=" ")
            img = render_road_overlay(args.zone, road_gen, upscale=2)
            if img:
                file = output_dir / f"{args.zone:02d}_{zone_name}.png"
                img.save(file)
                print(f"✓")
            else:
                print("ERROR")
        else:
            print(f"ERROR: Zone must be 0-8, got {args.zone}")

    else:
        parser.print_help()

    print("\n📊 Road Network Info:")
    road_gen.print_zone_info()
    print("✅ Done!")


if __name__ == "__main__":
    main()
