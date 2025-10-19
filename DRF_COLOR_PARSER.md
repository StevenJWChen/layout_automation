# DRF Color Parser Documentation

## Overview

The technology file parser has been extended to support Cadence Display Resource Files (.drf) for accurate layer color definitions. This allows you to load the exact colors used in Virtuoso layout tools.

## What is a DRF File?

A Display Resource File (.drf) is a Cadence Virtuoso file that defines:
- **Color definitions**: RGB values for named colors
- **Display packets**: Layer appearance including stipple patterns, line styles, and colors
- **Layer-to-color mappings**: Associates layer/purpose pairs with specific colors

## Key Features

### 1. RGB Color Parsing
Parses `dispDefineColor()` section to extract exact RGB values:

```lisp
dispDefineColor(
  (display blue      0   0   255)
  (display red       255 0   0)
  (display green     0   204 102)
  ...
)
```

These are converted to hex format: `#0000ff`, `#ff0000`, `#00cc66`

### 2. Packet-Based Layer Mapping
Parses `dispDefinePacket()` section to map layers to colors:

```lisp
dispDefinePacket(
  (display metal1      backSlash solid blue    blue    f)
  (display metal1Net   blank     solid blue    blue    f)
  (display metal1Pin   X         solid blue    blue    f)
  (display poly        checker1  solid red     red     f)
  (display active      invCross  solid green   green   f)
  ...
)
```

### 3. Automatic Layer Purpose Mapping
The parser automatically maps layer purposes to packet suffixes:

| Purpose    | Packet Suffix | Example              |
|------------|---------------|----------------------|
| drawing    | (none)        | metal1               |
| net        | Net           | metal1Net            |
| pin        | Pin           | metal1Pin            |
| label      | Lbl           | metal1Lbl            |
| boundary   | Bnd           | metal1Bnd            |

## Usage

### Basic Usage

```python
from layout_automation.tech_file import TechFile

# Create tech file instance
tech = TechFile()

# Load technology file (layer definitions and GDS numbers)
tech.parse_virtuoso_tech_file('FreePDK45.tf')

# Load DRF file for colors
tech.parse_drf_file('SantanaDisplay.drf')

# Query layer with color
metal1 = tech.get_layer('metal1', 'drawing')
print(f"Metal1 color: {metal1.color}")  # Output: #0000ff (blue)
```

### Using with Layout Visualization

Colors from the DRF file are stored as hex strings, making them directly compatible with matplotlib and other visualization libraries:

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')

# Get layer color
metal1 = tech.get_layer('metal1', 'drawing')

# Use directly in matplotlib
rect = mpatches.Rectangle((0, 0), 10, 5, facecolor=metal1.color)
plt.gca().add_patch(rect)
```

## Color Examples from SantanaDisplay.drf

| Layer     | Purpose  | Color Name | Hex Color | RGB          |
|-----------|----------|------------|-----------|--------------|
| metal1    | drawing  | blue       | #0000ff   | (0, 0, 255)  |
| metal2    | drawing  | magenta    | #ff00ff   | (255, 0, 255)|
| metal3    | drawing  | cyan       | #00ffff   | (0, 255, 255)|
| poly      | drawing  | red        | #ff0000   | (255, 0, 0)  |
| active    | drawing  | green      | #00cc66   | (0, 204, 102)|
| contact   | drawing  | white      | #ffffff   | (255, 255, 255)|
| nwell     | drawing  | green      | #00cc66   | (0, 204, 102)|
| pwell     | drawing  | orange     | #ff8000   | (255, 128, 0)|
| nimplant  | drawing  | green      | #00cc66   | (0, 204, 102)|
| pimplant  | drawing  | orange     | #ff8000   | (255, 128, 0)|

## API Reference

### `TechFile.parse_drf_file(filepath: str)`
Parse a DRF file and extract color definitions.

**Parameters:**
- `filepath`: Path to the .drf file

**Returns:** None

**Side Effects:**
- Populates `self.drf_colors` with color definitions
- Populates `self.drf_packets` with packet mappings
- Updates `LayerMapping.color` for all layers

### Internal Methods

#### `_parse_drf_colors(content: str)`
Extracts RGB color definitions from `dispDefineColor()` section.

#### `_parse_drf_packets(content: str)`
Extracts layer packet definitions from `dispDefinePacket()` section.

#### `_apply_drf_colors_to_layers()`
Maps DRF colors to layer mappings based on packet names and purposes.

## Integration with Existing Code

The DRF parser is fully integrated with the existing tech file parser:

1. **Load technology file first** (for layer names and GDS numbers)
2. **Load DRF file second** (for colors)
3. **Colors are automatically applied** to matching layers

```python
# Complete workflow
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')  # Step 1
tech.parse_drf_file('SantanaDisplay.drf')      # Step 2
tech.export_layer_map('layers_with_colors.txt') # Export result
```

## Advantages Over Default Colors

| Feature                    | Default Colors | DRF Colors |
|----------------------------|----------------|------------|
| Accuracy                   | Generic        | Exact match to Virtuoso |
| Color consistency          | Basic          | Professional CAD colors |
| Purpose-specific colors    | No             | Yes (net, pin, label)   |
| RGB precision              | Named colors   | Exact hex values |
| Customization             | Limited        | Full DRF support |

## File Structure Example

A typical DRF file contains three main sections:

```lisp
dispDefineDisplay(
  (display)
)

dispDefineColor(
  ;; RGB color definitions
  (display blue  0 0 255)
  (display red   255 0 0)
  ...
)

dispDefineStipple(
  ;; Fill patterns (not currently parsed)
  ...
)

dispDefinePacket(
  ;; Layer display properties
  (display metal1 backSlash solid blue blue f)
  (display poly   checker1  solid red  red  f)
  ...
)
```

## Backward Compatibility

- Works with or without a DRF file
- Falls back to default colors if DRF file not provided
- Maintains compatibility with existing tech file formats
- Does not break existing code

## Troubleshooting

### Colors not applied
- Ensure DRF file is loaded AFTER the technology file
- Check that packet names match layer names in tech file
- Verify color names exist in `dispDefineColor()` section

### Incorrect colors
- Check packet suffix mapping for the layer purpose
- Verify the DRF file matches your technology
- Some layers may use generic colors if not defined in DRF

### File not found
- Use absolute paths or verify working directory
- Check file extension (.drf not .tf)
- Ensure file has proper read permissions

## Example Output

When both files are loaded:

```
Loading FreePDK45.tf...
[OK] Loaded 297 layer mappings

Loading SantanaDisplay.drf...
[OK] Loaded 36 colors and 333 packets

Layer Information:
metal1  -> GDS 11/0 (color: #0000ff)
metal2  -> GDS 13/0 (color: #ff00ff)
poly    -> GDS  9/0 (color: #ff0000)
active  -> GDS  1/0 (color: #00cc66)
contact -> GDS 10/0 (color: #ffffff)
```

## Future Enhancements

Potential future additions:
- Parse stipple patterns for hatching/fill styles
- Support line style definitions
- Export to other visualization formats
- Custom color palette generation
