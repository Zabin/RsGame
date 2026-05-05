#!/usr/bin/env python3
"""
screen_preview.py — Generate PNG previews of complete game screens.

Usage:
    python screen_preview.py --all              # Preview all screens
    python screen_preview.py --screen garden    # Preview single screen
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

from graphics_utils import (
    get_tile_function,
    get_palette,
    apply_palette,
    get_screen_names,
    get_screen_function,
)


def render_screen(screen_name: str, upscale: int = 2) -> Optional[Image.Image]:
    """Render a complete game screen.

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

    # Screen is 20x18 tiles, 8x8 pixels each
    # Base size: 160x144 pixels (standard GBC screen)
    # Upscaled: 320x288 pixels (2x)
    base_width, base_height = 160, 144
    tile_size = 8

    # Create base image with transparency
    img = Image.new("RGBA", (base_width, base_height), (0, 0, 0, 0))

    # Render each tile
    for y in range(18):
        for x in range(20):
            idx = y * 20 + x
            tile_id = tiles[idx]
            pal_id = attrs[idx]

            # Render tile with palette
            tile_fn = get_tile_function(tile_id)
            if not tile_fn:
                continue

            try:
                pixels = tile_fn()
            except Exception:
                continue

            # Get palette (assuming BG type for tilemap)
            palette = get_palette(pal_id, "BG")
            if not palette:
                palette = get_palette(0, "BG")
            if not palette:
                continue

            # Apply palette
            rgb_pixels = apply_palette(pixels, palette)

            # Create tile image (8x8) with transparency
            tile_img = Image.new("RGBA", (tile_size, tile_size))
            pixel_data = []
            for row in rgb_pixels:
                for rgb in row:
                    pixel_data.append(rgb + (255,))  # Add alpha channel (fully opaque)
            tile_img.putdata(pixel_data)

            # Paste into screen
            screen_x = x * tile_size
            screen_y = y * tile_size
            img.paste(tile_img, (screen_x, screen_y), tile_img)  # Use tile_img as mask for alpha

    # Upscale
    if upscale != 1:
        final_width = base_width * upscale
        final_height = base_height * upscale
        img = img.resize((final_width, final_height), Image.Resampling.NEAREST)

    return img


def render_screen_with_grid(
    screen_name: str, upscale: int = 2, show_grid: bool = True
) -> Optional[Image.Image]:
    """Render screen with optional grid overlay.

    Args:
        screen_name: Screen name
        upscale: Pixel scaling
        show_grid: Whether to overlay grid

    Returns:
        PIL Image or None
    """
    img = render_screen(screen_name, upscale)
    if not img or not show_grid:
        return img

    # Draw grid
    draw = ImageDraw.Draw(img)
    tile_pixels = 8 * upscale

    # Vertical lines
    for x in range(0, img.width, tile_pixels):
        draw.line([(x, 0), (x, img.height)], fill=(200, 200, 200), width=1)

    # Horizontal lines
    for y in range(0, img.height, tile_pixels):
        draw.line([(0, y), (img.width, y)], fill=(200, 200, 200), width=1)

    return img


def main():
    """Main entry point for screen preview tool."""
    parser = argparse.ArgumentParser(description="Generate PNG previews of game screens")
    parser.add_argument("--all", action="store_true", help="Preview all screens")
    parser.add_argument("--screen", type=str, help="Preview single screen by name")
    parser.add_argument("--grid", action="store_true", help="Show tile grid overlay")
    parser.add_argument(
        "--output", type=str, default="previews/screens", help="Output directory"
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🖼️  Generating screen previews to {output_dir}/")

    if args.all:
        screen_names = get_screen_names()
        print(f"  Found {len(screen_names)} screens")

        for screen_name in screen_names:
            print(f"  Rendering {screen_name}...", end=" ")
            img = render_screen_with_grid(screen_name, upscale=2, show_grid=args.grid)
            if img:
                file = output_dir / f"{screen_name}.png"
                img.save(file)
                print(f"✓ {file.name}")
            else:
                print("ERROR")

    elif args.screen:
        print(f"  Rendering {args.screen}...", end=" ")
        img = render_screen_with_grid(args.screen, upscale=2, show_grid=args.grid)
        if img:
            file = output_dir / f"{args.screen}.png"
            img.save(file)
            print(f"✓ {file.name}")
        else:
            print(f"ERROR: Screen '{args.screen}' not found")
            print(f"Available screens: {', '.join(get_screen_names())}")

    else:
        parser.print_help()

    print("✅ Done!")


if __name__ == "__main__":
    main()
