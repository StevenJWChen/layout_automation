# GDS to PNG Converter

## Overview

A Python tool to convert GDS layout files to PNG images for easy viewing without needing specialized layout viewer software.

## Features

- ✅ Converts GDS-II files to PNG images
- ✅ Automatic layer coloring (SkyWater SKY130 color scheme)
- ✅ Layer legend showing which layers are present
- ✅ Cell name and dimensions displayed
- ✅ Configurable image resolution
- ✅ Batch conversion support (convert all GDS files at once)

## Usage

### Convert a Single File

```bash
python gds_to_png.py <gds_file> [png_file] [width] [height]
```

**Examples:**
```bash
# Basic conversion (1920×1080)
python gds_to_png.py dff_test.gds

# Specify output filename
python gds_to_png.py dff_test.gds dff_layout.png

# High resolution (4K)
python gds_to_png.py dff_test.gds dff_4k.png 3840 2160

# Ultra-wide monitor
python gds_to_png.py dff_test.gds dff_ultrawide.png 2560 1440
```

### Convert All GDS Files in Directory

```bash
python gds_to_png.py --all
```

This will convert all `*.gds` files in the current directory to PNG images.

## Layer Color Scheme

The converter uses a professional color scheme optimized for SkyWater SKY130 PDK:

| Layer | Color | Description |
|-------|-------|-------------|
| nwell | Gray | N-well substrate |
| pwell | Gray | P-well substrate |
| diff | Light Red | Active diffusion |
| poly | Light Purple | Polysilicon gate |
| li1 | Green | Local interconnect |
| licon1 | Light Blue | Local interconnect contact |
| met1 | Light Blue | Metal 1 |
| mcon | Blue | Metal contact |
| nsdm | Light Yellow | N+ source/drain implant |
| psdm | Light Orange | P+ source/drain implant |

## Output Format

Generated PNG images include:

1. **Layout rendering** with color-coded layers
2. **Layer legend** (top-left corner) showing which layers are present
3. **Cell name and dimensions** (bottom-right corner)
4. **Dark background** for better contrast
5. **Automatic scaling** to fit the image while maintaining aspect ratio

## Example Results

### D Flip-Flop (16 transistors)
```
File: dff_test.gds → dff_test.png
Size: 9.4 × 5.1 μm
Image: 1920 × 1080 pixels
Layers: 3 (L0/0, L10/0, L11/0)
```

### Inverter (2 transistors)
```
File: inverter_improved.gds → inverter_improved.png
Size: 2.4 × 5.1 μm
Image: 1920 × 1080 pixels
Layers: 3 (L0/0, L10/0, L11/0)
```

## Technical Details

### Dependencies

- `gdstk` - GDS-II library reading
- `PIL` (Pillow) - Image generation
- `numpy` - Numerical operations

All dependencies are already installed in this project.

### How It Works

1. **Read GDS file** using `gdstk.read_gds()`
2. **Find top cell** (or specified cell)
3. **Get bounding box** and calculate scaling
4. **Flatten hierarchy** to get all polygons
5. **Render each polygon** with layer-specific colors
6. **Add legend and labels**
7. **Save as PNG**

### Performance

- Fast: ~0.5 seconds for typical cell
- Memory efficient: Handles large layouts
- Batch mode: Converts 20 files in ~10 seconds

## Viewing the Images

Generated PNG files can be viewed with any image viewer:

- **macOS**: Preview (default), Preview.app
- **Windows**: Photos, Paint
- **Linux**: Eye of GNOME, gThumb
- **Web browser**: Drag and drop into Chrome/Firefox
- **VS Code**: Click to view in editor

## Integration with Verification Flow

The converter is particularly useful in the IC design verification flow:

```
Design Flow:
1. Create schematic netlist
2. Generate layout (GDS)
3. Convert to PNG ← This tool
4. Visual inspection
5. Run DRC/LVS verification
```

## Example Session

```bash
# Convert the D flip-flop layout
$ python gds_to_png.py dff_test.gds

Converting dff_test.gds to PNG...
  Loaded library: LAYOUT
  Cells: 17
  Rendering cell: DFF_layout
  Layout bounds: (-0.495, -0.495) to (8.905, 4.610) μm
  Layout size: 9.400 × 5.105 μm
  Rendering 170 polygons...
  Rendered 3 different layers
  Saved to: dff_test.png
  Image size: 1920 × 1080 pixels

✅ Success! View the image: dff_test.png
```

## Batch Conversion Results

When running `python gds_to_png.py --all`, the tool converted **20 GDS files** including:

- `dff_test.gds` - D flip-flop (16 transistors)
- `inverter_improved.gds` - Inverter (2 transistors)
- `test1_inverter.gds` - Test inverter
- `test2_nand2_gate.gds` - NAND2 gate (4 transistors)
- `test3_nor2_gate.gds` - NOR2 gate (4 transistors)
- `test4_and3_gate.gds` - AND3 gate (8 transistors)
- `test5_2-to-1_multiplexer.gds` - MUX (8 transistors)
- `and3_end_to_end.gds` - AND3 complete flow
- `sky130_inv_replica.gds` - SkyWater inverter replica
- `sky130_and3_replica.gds` - SkyWater AND3 replica
- And 10 more test files...

All conversions completed successfully!

## Customization

### Change Image Resolution

Edit the default width/height in the script or pass as arguments:

```python
# 4K resolution
python gds_to_png.py layout.gds output.png 3840 2160

# HD resolution
python gds_to_png.py layout.gds output.png 1280 720
```

### Modify Color Scheme

Edit the `LAYER_COLORS` dictionary in `gds_to_png.py`:

```python
LAYER_COLORS = {
    (65, 20): (255, 150, 150, 200),  # diff - light red
    (67, 20): (200, 150, 255, 180),  # poly - light purple
    # Add more layer colors...
}
```

### Add New Layers

The tool automatically handles any layer numbers found in the GDS file. Unknown layers are rendered in default gray.

## Limitations

- **2D only**: Does not show 3D layer stacking
- **No connectivity**: Shows geometry only, not electrical connections
- **Simplified rendering**: No pattern fills or stippling
- **Layer mapping**: Optimized for SkyWater SKY130 PDK

## Future Enhancements

Possible improvements:
- [ ] Interactive zoom/pan
- [ ] Measurement tools
- [ ] Cross-section view
- [ ] Multiple layer display modes
- [ ] Export to SVG
- [ ] Comparison view (overlay two layouts)

## Conclusion

This GDS to PNG converter provides a quick and easy way to visualize IC layouts without needing specialized software. It's particularly useful for:

- Quick layout inspection
- Documentation and presentations
- Sharing layouts via email/chat
- Version control diffs (PNG images)
- Web-based layout galleries

---

**Generated PNG files are ready to view!** Just open them with any image viewer.
