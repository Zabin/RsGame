#!/usr/bin/env python3
"""
tile_preview.py — Generate PNG previews of game tiles.

Usage:
    python tile_preview.py --all              # Preview all tiles
    python tile_preview.py --tile 0x10        # Preview single tile
    python tile_preview.py --type bg          # Preview all BG tiles
    python tile_preview.py --palettes         # Preview all palettes
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple, List

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Install with: pip install Pillow")
    sys.exit(1)

from graphics_utils import (
    get_tile_function,
    get_palette,
    apply_palette,
    rgb15_to_rgb8,
    get_all_tile_indices,
    get_screen_names,
)


def render_tile(
    tile_index: int, upscale: int = 8, pal_id: int = 0, pal_type: str = "BG"
) -> Optional[Image.Image]:
    """Render a single tile to PIL Image.

    Args:
        tile_index: Tile index (0x00-0xFF)
        upscale: Pixel scaling factor (8 = 64x64 final)
        pal_id: Palette ID (0-7)
        pal_type: Palette type ("BG" or "OBJ")

    Returns:
        PIL Image or None if tile not found
    """
    # Get tile pixel function
    tile_fn = get_tile_function(tile_index)
    if not tile_fn:
        return None

    try:
        pixels = tile_fn()
    except Exception:
        return None

    # Get palette
    palette = get_palette(pal_id, pal_type)
    if not palette:
        # Fallback to first palette if not found
        palette = get_palette(0, pal_type)
    if not palette:
        return None

    # Apply palette to pixels
    rgb_pixels = apply_palette(pixels, palette)

    # Create base 8x8 image
    img = Image.new("RGB", (8, 8))
    pixel_data = []
    for row in rgb_pixels:
        for rgb in row:
            pixel_data.append(rgb)
    img.putdata(pixel_data)

    # Upscale
    final_size = 8 * upscale
    img = img.resize((final_size, final_size), Image.Resampling.NEAREST)

    return img


def create_tile_grid(
    tile_indices: List[int], upscale: int = 8, pal_type: str = "BG"
) -> Image.Image:
    """Create a grid of tiles.

    Args:
        tile_indices: List of tile indices to render
        upscale: Pixel scaling factor
        pal_type: Palette type ("BG" or "OBJ")

    Returns:
        PIL Image with grid of tiles
    """
    tile_size = 8 * upscale
    cols = 8
    rows = (len(tile_indices) + cols - 1) // cols

    # Create grid image with padding
    margin = 20
    label_height = 20
    grid_width = cols * tile_size + (cols - 1) * 4 + 2 * margin
    grid_height = rows * tile_size + (rows - 1) * 4 + 2 * margin + label_height

    grid_img = Image.new("RGB", (grid_width, grid_height), "white")
    draw = ImageDraw.Draw(grid_img)

    # Render tiles
    for i, tile_id in enumerate(tile_indices):
        row, col = divmod(i, cols)
        x = margin + col * (tile_size + 4)
        y = margin + label_height + row * (tile_size + 4)

        tile_img = render_tile(tile_id, upscale, pal_id=0, pal_type=pal_type)
        if tile_img:
            grid_img.paste(tile_img, (x, y))

            # Draw tile index label
            label = f"0x{tile_id:02X}"
            try:
                draw.text((x, y - 18), label, fill="black")
            except Exception:
                pass

    return grid_img


def create_palette_preview(pal_id: int, pal_type: str = "BG") -> Image.Image:
    """Create a preview of a single palette.

    Args:
        pal_id: Palette ID (0-7)
        pal_type: Palette type ("BG" or "OBJ")

    Returns:
        PIL Image showing palette colors
    """
    palette = get_palette(pal_id, pal_type)
    if not palette:
        palette = [0x0000, 0x7FFF, 0x7FFF, 0x7FFF]

    # Create image with color swatches
    swatch_size = 64
    img = Image.new("RGB", (4 * swatch_size + 50, swatch_size + 80), "white")
    draw = ImageDraw.Draw(img)

    for i, rgb15 in enumerate(palette):
        rgb8 = rgb15_to_rgb8(rgb15)
        x = 10 + i * (swatch_size + 5)
        y = 10

        # Draw color swatch
        draw.rectangle([x, y, x + swatch_size, y + swatch_size], fill=rgb8)
        draw.rectangle(
            [x, y, x + swatch_size, y + swatch_size], outline="black", width=1
        )

        # Draw hex value
        hex_str = f"0x{rgb15:04X}"
        try:
            draw.text((x, y + swatch_size + 5), hex_str, fill="black")
        except Exception:
            pass

    return img


def create_all_palettes_preview(pal_type: str = "BG") -> Image.Image:
    """Create preview of all palettes of a type.

    Args:
        pal_type: "BG" or "OBJ"

    Returns:
        PIL Image showing all palettes
    """
    pal_count = 8 if pal_type == "BG" else 4
    cols = 4
    rows = (pal_count + cols - 1) // cols

    # Each palette preview is ~300x80
    pal_width = 300
    pal_height = 80
    margin = 10

    img_width = cols * pal_width + (cols + 1) * margin
    img_height = rows * pal_height + (rows + 1) * margin + 30

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Title
    try:
        draw.text((margin, margin), f"{pal_type} Palettes", fill="black")
    except Exception:
        pass

    # Render each palette
    for pal_id in range(pal_count):
        row, col = divmod(pal_id, cols)
        x = margin + col * (pal_width + margin)
        y = margin + 30 + row * (pal_height + margin)

        palette = get_palette(pal_id, pal_type)
        if palette:
            swatch_size = 50
            for i, rgb15 in enumerate(palette):
                rgb8 = rgb15_to_rgb8(rgb15)
                sx = x + i * (swatch_size + 5)
                sy = y

                draw.rectangle(
                    [sx, sy, sx + swatch_size, sy + swatch_size], fill=rgb8
                )
                draw.rectangle(
                    [sx, sy, sx + swatch_size, sy + swatch_size],
                    outline="black",
                    width=1,
                )

    return img


def main():
    """Main entry point for tile preview tool."""
    parser = argparse.ArgumentParser(description="Generate PNG previews of game tiles")
    parser.add_argument("--all", action="store_true", help="Preview all tiles and palettes")
    parser.add_argument("--tile", type=str, help="Preview single tile (hex: 0x10)")
    parser.add_argument("--type", choices=["obj", "bg", "font"], help="Preview all tiles of type")
    parser.add_argument("--palettes", action="store_true", help="Preview all palettes")
    parser.add_argument(
        "--output", type=str, default="previews", help="Output directory (default: previews/)"
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📸 Generating tile previews to {output_dir}/")

    # Generate requested previews
    if args.all:
        print("  Generating all tile grids...")
        obj_idx, bg_idx, font_idx = get_all_tile_indices()

        # OBJ tiles
        grid = create_tile_grid(obj_idx, upscale=8, pal_type="OBJ")
        obj_file = output_dir / "tiles_obj_0x00_0x07.png"
        grid.save(obj_file)
        print(f"    ✓ {obj_file}")

        # BG tiles
        grid = create_tile_grid(bg_idx, upscale=8, pal_type="BG")
        bg_file = output_dir / "tiles_bg_0x10_0x2B.png"
        grid.save(bg_file)
        print(f"    ✓ {bg_file}")

        # Font tiles
        grid = create_tile_grid(font_idx, upscale=6, pal_type="BG")
        font_file = output_dir / "tiles_font_0x40_0x61.png"
        grid.save(font_file)
        print(f"    ✓ {font_file}")

        # Palettes
        print("  Generating palette previews...")
        bg_pal_file = output_dir / "palettes_bg_all.png"
        img = create_all_palettes_preview("BG")
        img.save(bg_pal_file)
        print(f"    ✓ {bg_pal_file}")

        obj_pal_file = output_dir / "palettes_obj_all.png"
        img = create_all_palettes_preview("OBJ")
        img.save(obj_pal_file)
        print(f"    ✓ {obj_pal_file}")

    elif args.tile:
        # Parse hex tile index
        try:
            tile_idx = int(args.tile, 16) if args.tile.startswith("0x") else int(args.tile)
        except ValueError:
            print(f"ERROR: Invalid tile index {args.tile}")
            sys.exit(1)

        print(f"  Rendering tile 0x{tile_idx:02X}...")
        img = render_tile(tile_idx, upscale=8)
        if img:
            tile_file = output_dir / f"tile_0x{tile_idx:02X}.png"
            img.save(tile_file)
            print(f"    ✓ {tile_file}")
        else:
            print(f"    ERROR: Tile 0x{tile_idx:02X} not found")

    elif args.type:
        print(f"  Generating {args.type.upper()} tile grid...")
        if args.type == "obj":
            obj_idx, _, _ = get_all_tile_indices()
            grid = create_tile_grid(obj_idx, upscale=8, pal_type="OBJ")
            file = output_dir / f"tiles_{args.type}_grid.png"
        elif args.type == "bg":
            _, bg_idx, _ = get_all_tile_indices()
            grid = create_tile_grid(bg_idx, upscale=8, pal_type="BG")
            file = output_dir / f"tiles_{args.type}_grid.png"
        else:  # font
            _, _, font_idx = get_all_tile_indices()
            grid = create_tile_grid(font_idx, upscale=6, pal_type="BG")
            file = output_dir / f"tiles_{args.type}_grid.png"

        grid.save(file)
        print(f"    ✓ {file}")

    elif args.palettes:
        print("  Generating palette previews...")
        for pal_type in ["BG", "OBJ"]:
            img = create_all_palettes_preview(pal_type)
            file = output_dir / f"palettes_{pal_type.lower()}_all.png"
            img.save(file)
            print(f"    ✓ {file}")

    else:
        parser.print_help()

    print("✅ Done!")


if __name__ == "__main__":
    main()
