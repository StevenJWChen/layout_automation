#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDS to PNG Converter

Converts GDS layout files to PNG images for easy viewing
"""

import gdstk
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys
from pathlib import Path


# Color scheme for different layers (Sky130)
LAYER_COLORS = {
    # Format: (gds_layer, gds_datatype): (R, G, B, Alpha)
    (64, 20): (100, 100, 100, 200),    # nwell - gray
    (64, 44): (100, 100, 100, 200),    # pwell - gray
    (65, 20): (255, 150, 150, 200),    # diff - light red
    (66, 20): (255, 100, 100, 255),    # tap - red
    (67, 20): (200, 150, 255, 180),    # poly - light purple
    (67, 44): (200, 150, 255, 180),    # poly (drawing) - light purple
    (68, 20): (100, 255, 100, 200),    # li1 (local interconnect) - green
    (66, 44): (150, 150, 255, 180),    # licon1 - light blue
    (67, 14): (150, 150, 255, 180),    # licon1 (alternate) - light blue
    (69, 20): (100, 150, 255, 255),    # mcon - blue
    (70, 20): (150, 150, 255, 255),    # met1 - light blue
    (71, 20): (100, 200, 255, 255),    # via1 - cyan
    (72, 20): (100, 220, 255, 255),    # met2 - light cyan
    (93, 44): (255, 255, 150, 150),    # nsdm (n+ source/drain) - light yellow
    (94, 20): (255, 200, 150, 150),    # psdm (p+ source/drain) - light orange
}


def get_bbox(library, cell_name=None):
    """
    Get bounding box of a cell or the entire library

    Args:
        library: gdstk.Library object
        cell_name: Name of cell to get bbox for (None = use top cell)

    Returns:
        (min_x, min_y, max_x, max_y) in microns
    """
    if cell_name:
        cell = library.cells[cell_name]
    else:
        # Find top cell (cell that is not referenced by any other cell)
        top_cells = library.top_level()
        if not top_cells:
            # No top cell, use first cell
            cell = library.cells[0]
        else:
            cell = top_cells[0]

    bbox = cell.bounding_box()
    if bbox is None:
        return (0, 0, 10, 10)

    return bbox


def gds_to_png(gds_file, png_file=None, width=1920, height=1080,
               cell_name=None, margin=0.5, show_layers=True):
    """
    Convert GDS file to PNG image

    Args:
        gds_file: Path to GDS file
        png_file: Output PNG file (None = auto-generate from gds_file)
        width: Image width in pixels
        height: Image height in pixels
        cell_name: Name of cell to render (None = top cell)
        margin: Margin around layout in microns
        show_layers: Show layer legend

    Returns:
        Path to generated PNG file
    """
    print(f"Converting {gds_file} to PNG...")

    # Read GDS file
    try:
        library = gdstk.read_gds(gds_file)
    except Exception as e:
        print(f"Error reading GDS file: {e}")
        return None

    print(f"  Loaded library: {library.name}")
    print(f"  Cells: {len(library.cells)}")

    # Get cell to render
    if cell_name:
        if cell_name not in [c.name for c in library.cells]:
            print(f"Error: Cell '{cell_name}' not found")
            return None
        cell = [c for c in library.cells if c.name == cell_name][0]
    else:
        top_cells = library.top_level()
        if not top_cells:
            cell = library.cells[0]
        else:
            cell = top_cells[0]

    print(f"  Rendering cell: {cell.name}")

    # Get bounding box
    bbox = cell.bounding_box()
    if bbox is None:
        print("Warning: Empty cell, using default bbox")
        bbox = np.array([[0, 0], [10, 10]])

    min_x, min_y = bbox[0]
    max_x, max_y = bbox[1]

    # Add margin
    min_x -= margin
    min_y -= margin
    max_x += margin
    max_y += margin

    layout_width = max_x - min_x
    layout_height = max_y - min_y

    print(f"  Layout bounds: ({min_x:.3f}, {min_y:.3f}) to ({max_x:.3f}, {max_y:.3f}) μm")
    print(f"  Layout size: {layout_width:.3f} × {layout_height:.3f} μm")

    # Calculate scaling to fit image
    scale_x = width / layout_width
    scale_y = height / layout_height
    scale = min(scale_x, scale_y) * 0.9  # Use 90% to leave some margin

    # Center the layout
    img_center_x = width / 2
    img_center_y = height / 2
    layout_center_x = (min_x + max_x) / 2
    layout_center_y = (min_y + max_y) / 2

    def layout_to_pixel(x, y):
        """Convert layout coordinates (microns) to pixel coordinates"""
        px = (x - layout_center_x) * scale + img_center_x
        py = height - ((y - layout_center_y) * scale + img_center_y)  # Flip Y
        return (int(px), int(py))

    # Create image
    img = Image.new('RGB', (width, height), color=(30, 30, 30))  # Dark background
    draw = ImageDraw.Draw(img, 'RGBA')

    # Track which layers are present
    layers_present = set()

    # Render all polygons
    all_polygons = cell.get_polygons(depth=None)  # Flatten hierarchy

    print(f"  Rendering {len(all_polygons)} polygons...")

    for i, polygon in enumerate(all_polygons):
        # Get layer and datatype from polygon
        layer = polygon.layer
        datatype = polygon.datatype
        layer_key = (layer, datatype)
        layers_present.add(layer_key)

        # Get color for this layer
        color = LAYER_COLORS.get(layer_key, (150, 150, 150, 128))  # Default gray

        # Get polygon points
        polygon_points = polygon.points

        # Convert polygon points to pixel coordinates
        pixel_points = [layout_to_pixel(x, y) for x, y in polygon_points]

        # Draw filled polygon
        if len(pixel_points) >= 3:
            draw.polygon(pixel_points, fill=color, outline=None)

    print(f"  Rendered {len(layers_present)} different layers")

    # Add layer legend
    if show_layers and layers_present:
        legend_x = 20
        legend_y = 20
        legend_spacing = 25

        # Try to load a font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font = ImageFont.load_default()

        # Draw legend background
        legend_height = len(layers_present) * legend_spacing + 40
        draw.rectangle([(legend_x - 10, legend_y - 10),
                       (legend_x + 200, legend_y + legend_height)],
                      fill=(0, 0, 0, 200))

        draw.text((legend_x, legend_y), "Layers:", fill=(255, 255, 255), font=font)
        legend_y += legend_spacing

        # Layer name mapping
        layer_names = {
            (64, 20): "nwell",
            (64, 44): "pwell",
            (65, 20): "diff",
            (66, 20): "tap",
            (67, 20): "poly",
            (67, 44): "poly",
            (68, 20): "li1",
            (66, 44): "licon1",
            (67, 14): "licon1",
            (69, 20): "mcon",
            (70, 20): "met1",
            (71, 20): "via1",
            (72, 20): "met2",
            (93, 44): "nsdm",
            (94, 20): "psdm",
        }

        for layer_key in sorted(layers_present):
            color = LAYER_COLORS.get(layer_key, (150, 150, 150, 255))
            layer_name = layer_names.get(layer_key, f"L{layer_key[0]}/{layer_key[1]}")

            # Draw color box
            draw.rectangle([(legend_x, legend_y), (legend_x + 30, legend_y + 15)],
                          fill=color)

            # Draw layer name
            draw.text((legend_x + 40, legend_y), layer_name,
                     fill=(255, 255, 255), font=font)

            legend_y += legend_spacing

    # Add title
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        title_font = ImageFont.load_default()

    title = f"{cell.name}  ({layout_width:.3f} × {layout_height:.3f} μm)"
    draw.text((width - 400, height - 40), title, fill=(200, 200, 200), font=title_font)

    # Save PNG
    if png_file is None:
        png_file = Path(gds_file).with_suffix('.png')

    img.save(png_file)
    print(f"  Saved to: {png_file}")
    print(f"  Image size: {width} × {height} pixels")

    return png_file


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python gds_to_png.py <gds_file> [png_file] [width] [height]")
        print("\nExample:")
        print("  python gds_to_png.py dff_test.gds")
        print("  python gds_to_png.py dff_test.gds dff_layout.png 2560 1440")
        print("\nConverts all GDS files in current directory:")
        print("  python gds_to_png.py --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        # Convert all GDS files in current directory
        gds_files = list(Path('.').glob('*.gds'))
        if not gds_files:
            print("No GDS files found in current directory")
            sys.exit(1)

        print(f"Found {len(gds_files)} GDS files")
        for gds_file in gds_files:
            print(f"\n{'='*70}")
            gds_to_png(str(gds_file), width=1920, height=1080)

        print(f"\n{'='*70}")
        print(f"Converted {len(gds_files)} files")
        sys.exit(0)

    gds_file = sys.argv[1]
    png_file = sys.argv[2] if len(sys.argv) > 2 else None
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 1080

    result = gds_to_png(gds_file, png_file, width, height)

    if result:
        print(f"\n✅ Success! View the image: {result}")
    else:
        print("\n❌ Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
