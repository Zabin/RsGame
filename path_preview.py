#!/usr/bin/env python3
"""
path_preview.py — Visualize pathfinding results on screen previews.

Renders each biome with the found path highlighted in a contrasting color.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: Pillow not installed. Install with: pip install Pillow")
    sys.exit(1)

from graphics_utils import get_screen_function
from pathfinding import PathValidator


def render_path_overlay(screen_name: str, upscale: int = 2) -> Optional[Image.Image]:
    """
    Render a complete game screen with pathfinding visualization.

    Args:
        screen_name: Screen name (e.g., 'garden', 'forest')
        upscale: Pixel scaling factor (2 = 320x288)

    Returns:
        PIL Image or None if screen not found
    """
    screen_fn = get_screen_function(screen_name)
    if not screen_fn:
        return None

    try:
        tiles, attrs = screen_fn()
    except Exception as e:
        print(f"ERROR rendering {screen_name}: {e}")
        return None

    expected_size = 20 * 18  # 360 bytes (20 wide x 18 tall)
    if not tiles or not attrs or len(tiles) != expected_size or len(attrs) != expected_size:
        return None

    # Base size: 160x144 pixels
    base_width, base_height = 160, 144
    tile_size = 8

    # Create base tilemap image first (reuse screen_preview.py logic)
    img = Image.new("RGB", (base_width, base_height), "white")

    from graphics_utils import apply_palette, get_palette, get_tile_function

    # Render each tile
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

    # Find and draw path
    validator = PathValidator(tiles, attrs)
    path = validator.find_path((0, 9), (19, 9))

    if path:
        # Upscale first
        if upscale != 1:
            final_width = base_width * upscale
            final_height = base_height * upscale
            img = img.resize((final_width, final_height), Image.Resampling.NEAREST)

        # Draw path on upscaled image
        draw = ImageDraw.Draw(img)
        tile_pixel_size = tile_size * upscale

        # Draw path as line and circles
        for i, (x, y) in enumerate(path):
            # Center of tile in pixels
            px = x * tile_pixel_size + tile_pixel_size // 2
            py = y * tile_pixel_size + tile_pixel_size // 2

            # Draw circle at each waypoint (cyan with outline)
            radius = 3 if i % 2 == 0 else 2
            draw.ellipse(
                [px - radius, py - radius, px + radius, py + radius],
                fill=(0, 255, 255),  # Cyan
                outline=(0, 200, 200),
            )

            # Draw line to next waypoint
            if i < len(path) - 1:
                nx, ny = path[i + 1]
                npx = nx * tile_pixel_size + tile_pixel_size // 2
                npy = ny * tile_pixel_size + tile_pixel_size // 2
                draw.line(
                    [(px, py), (npx, npy)], fill=(0, 200, 200), width=2
                )

        return img
    else:
        # No path found, just return upscaled image
        if upscale != 1:
            final_width = base_width * upscale
            final_height = base_height * upscale
            img = img.resize((final_width, final_height), Image.Resampling.NEAREST)
        return img


def main():
    """Main entry point for path visualization."""
    parser = argparse.ArgumentParser(
        description="Visualize pathfinding through game screens"
    )
    parser.add_argument("--all", action="store_true", help="Preview all screens")
    parser.add_argument("--screen", type=str, help="Preview single screen by name")
    parser.add_argument(
        "--output", type=str, default="previews/paths", help="Output directory"
    )

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🛤️  Generating path visualizations to {output_dir}/")

    if args.all:
        from tilemaps import ALL_SCREENS

        screen_names = [name for name, _ in ALL_SCREENS]
        print(f"  Found {len(screen_names)} screens")

        for screen_name in screen_names:
            print(f"  Rendering {screen_name}...", end=" ")
            img = render_path_overlay(screen_name, upscale=2)
            if img:
                file = output_dir / f"{screen_name}.png"
                img.save(file)
                print(f"✓ {file.name}")
            else:
                print("ERROR")

    elif args.screen:
        print(f"  Rendering {args.screen}...", end=" ")
        img = render_path_overlay(args.screen, upscale=2)
        if img:
            file = output_dir / f"{args.screen}.png"
            img.save(file)
            print(f"✓ {file.name}")
        else:
            print(f"ERROR: Screen '{args.screen}' not found")
            from tilemaps import ALL_SCREENS

            print(f"Available screens: {', '.join(name for name, _ in ALL_SCREENS)}")

    else:
        parser.print_help()

    print("✅ Done!")


if __name__ == "__main__":
    main()
