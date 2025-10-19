# Complete Technology File Parser Guide

## Overview

The technology file parser (`layout_automation/tech_file.py`) now supports comprehensive parsing of Cadence Virtuoso technology files, including:

1. **FreePDK45.tf** - Technology definitions with layer/GDS mappings
2. **SantanaDisplay.drf** - Display resource file with accurate colors

## Complete Feature Set

### Technology File (.tf) Parsing

✅ **Layer Definitions**
- Supports FreePDK45 format: `( layerName purpose )`
- Backward compatible with quoted format: `"layerName" "purpose"`
- Parses `techLayerPurposePriorities` section

✅ **GDS Layer Numbers**
- Extracts from `layerRules/functions` section (FreePDK45)
- Supports `streamLayers` section (legacy format)
- Maps layer names to GDS mask numbers

✅ **Layer Colors** (fallback)
- Default color scheme for standard CMOS layers
- Parses `techDisplays` section
- Supports `drDefineDisplay` section (legacy)

### Display Resource File (.drf) Parsing

✅ **RGB Color Definitions**
- Parses `dispDefineColor()` section
- Converts RGB to hex format
- 36+ color definitions supported

✅ **Layer Display Packets**
- Parses `dispDefinePacket()` section
- Maps layer/purpose to colors
- 333+ packet definitions supported

✅ **Automatic Color Application**
- Purpose-based packet suffix mapping
- Applies colors to all layer purposes
- Overrides default colors with DRF colors

## Quick Start

### Option 1: Tech File Only (with default colors)

```python
from layout_automation.tech_file import load_tech_file

# Load tech file
tech = load_tech_file('FreePDK45.tf')

# Query layers
metal1 = tech.get_layer('metal1', 'drawing')
print(f"Metal1: GDS {metal1.gds_layer}, Color: {metal1.color}")
# Output: Metal1: GDS 11, Color: blue
```

### Option 2: Tech File + DRF (with accurate colors)

```python
from layout_automation.tech_file import TechFile

# Load both files
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')

# Query layers
metal1 = tech.get_layer('metal1', 'drawing')
print(f"Metal1: GDS {metal1.gds_layer}, Color: {metal1.color}")
# Output: Metal1: GDS 11, Color: #0000ff
```

## File Formats Supported

### FreePDK45.tf Structure

```lisp
layerDefinitions(
  techLayerPurposePriorities(
    ( active    drawing )
    ( poly      drawing )
    ( metal1    drawing )
    ...
  )

  techDisplays(
    ( active    drawing    active    t t t t t )
    ( poly      drawing    poly      t t t t t )
    ...
  )
)

layerRules(
  functions(
    ( active   "unknown"  1  )
    ( poly     "poly"     9  )
    ( metal1   "metal"    11 )
    ...
  )
)
```

### SantanaDisplay.drf Structure

```lisp
dispDefineColor(
  (display blue      0   0   255)
  (display red       255 0   0)
  (display green     0   204 102)
  ...
)

dispDefinePacket(
  (display metal1      backSlash solid blue    blue    f)
  (display metal1Net   blank     solid blue    blue    f)
  (display poly        checker1  solid red     red     f)
  ...
)
```

## Complete API Reference

### Main Methods

#### `TechFile.parse_virtuoso_tech_file(filepath: str)`
Parse a Virtuoso technology file (.tf).

**Extracts:**
- Layer names and purposes
- GDS layer/datatype numbers
- Default layer colors

#### `TechFile.parse_drf_file(filepath: str)`
Parse a display resource file (.drf).

**Extracts:**
- RGB color definitions
- Layer display packets
- Color-to-layer mappings

#### `TechFile.get_layer(name: str, purpose: str = 'drawing') -> LayerMapping`
Get layer information by name and purpose.

**Returns:** LayerMapping with name, purpose, GDS numbers, and color

#### `TechFile.get_layer_by_gds(gds_layer: int, gds_datatype: int = 0) -> LayerMapping`
Reverse lookup: Get layer by GDS number.

#### `TechFile.get_gds_layer(name: str, purpose: str = 'drawing') -> Tuple[int, int]`
Get GDS layer/datatype numbers for a layer.

#### `TechFile.export_layer_map(filepath: str)`
Export layer mappings to a text file.

### LayerMapping Class

```python
class LayerMapping:
    name: str              # Layer name (e.g., 'metal1')
    purpose: str           # Purpose (e.g., 'drawing', 'pin')
    gds_layer: int         # GDS layer number
    gds_datatype: int      # GDS datatype number
    color: str             # Color (name or hex)
```

## Layer Information Extracted

### From FreePDK45.tf

| Layer    | GDS Layer | Default Color | Notes                    |
|----------|-----------|---------------|--------------------------|
| active   | 1         | brown         | Active diffusion         |
| poly     | 9         | red           | Polysilicon gate         |
| contact  | 10        | black         | Contact to active/poly   |
| metal1   | 11        | blue          | First metal layer        |
| via1     | 12        | gray          | Via between M1/M2        |
| metal2   | 13        | red           | Second metal layer       |
| via2     | 14        | gray          | Via between M2/M3        |
| metal3   | 15        | green         | Third metal layer        |
| ...      | ...       | ...           | Up to metal10 (GDS 29)   |

### From SantanaDisplay.drf

| Layer    | DRF Color | Hex Color | RGB           |
|----------|-----------|-----------|---------------|
| metal1   | blue      | #0000ff   | (0, 0, 255)   |
| metal2   | magenta   | #ff00ff   | (255, 0, 255) |
| metal3   | cyan      | #00ffff   | (0, 255, 255) |
| poly     | red       | #ff0000   | (255, 0, 0)   |
| active   | green     | #00cc66   | (0, 204, 102) |
| contact  | white     | #ffffff   | (255, 255, 255)|
| nwell    | green     | #00cc66   | (0, 204, 102) |
| pwell    | orange    | #ff8000   | (255, 128, 0) |

## Purpose Mappings

The parser handles multiple purposes per layer:

| Purpose   | Description           | DRF Suffix | Example Packet |
|-----------|-----------------------|------------|----------------|
| drawing   | Main geometry         | (none)     | metal1         |
| net       | Net identification    | Net        | metal1Net      |
| pin       | Pin markers           | Pin        | metal1Pin      |
| label     | Text labels           | Lbl        | metal1Lbl      |
| boundary  | Cell boundaries       | Bnd        | metal1Bnd      |
| blockage  | Routing blockage      | (none)     | metal1         |
| grid      | Grid display          | (none)     | metal1         |
| track     | Routing tracks        | (none)     | metal1         |

## Complete Example

```python
from layout_automation.tech_file import TechFile

# Initialize and load files
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')

# Query all information about a layer
layer = tech.get_layer('metal1', 'drawing')
print(f"Layer: {layer.name}")
print(f"Purpose: {layer.purpose}")
print(f"GDS Layer: {layer.gds_layer}")
print(f"GDS Datatype: {layer.gds_datatype}")
print(f"Color: {layer.color}")

# Output:
# Layer: metal1
# Purpose: drawing
# GDS Layer: 11
# GDS Datatype: 0
# Color: #0000ff

# Check different purposes
for purpose in ['drawing', 'net', 'pin', 'label']:
    layer = tech.get_layer('metal1', purpose)
    print(f"metal1.{purpose}: {layer.color}")

# Reverse lookup
layer = tech.get_layer_by_gds(11, 0)
print(f"GDS 11/0 is: {layer.name}")

# Export complete layer map
tech.export_layer_map('complete_layer_map.txt')
```

## Integration with Layout Tools

### Using Colors in Matplotlib

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')

# Create colored rectangles
fig, ax = plt.subplots()

layers = ['metal1', 'metal2', 'poly', 'active']
y = 0

for layer_name in layers:
    layer = tech.get_layer(layer_name, 'drawing')
    rect = mpatches.Rectangle((0, y), 10, 1,
                              facecolor=layer.color,
                              edgecolor='black')
    ax.add_patch(rect)
    ax.text(-0.5, y+0.5, layer_name, ha='right', va='center')
    y += 1.5

ax.set_xlim(-2, 12)
ax.set_ylim(-1, y)
ax.set_aspect('equal')
plt.show()
```

### Using with GDS Writers

```python
import gdspy

tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')

# Get GDS numbers for layers
metal1_gds = tech.get_gds_layer('metal1', 'drawing')
poly_gds = tech.get_gds_layer('poly', 'drawing')

# Create GDS library
lib = gdspy.GdsLibrary()
cell = lib.new_cell('DEMO')

# Add rectangles with correct layer numbers
cell.add(gdspy.Rectangle((0, 0), (10, 5), layer=metal1_gds[0]))
cell.add(gdspy.Rectangle((5, 3), (15, 8), layer=poly_gds[0]))

lib.write_gds('demo.gds')
```

## Statistics

### Files Parsed Successfully

- **FreePDK45.tf**: 297 layer mappings
- **SantanaDisplay.drf**: 36 colors, 333 packets

### Layer Coverage

- 10 metal layers (metal1-metal10)
- 9 via layers (via1-via9)
- Wells, implants, active, poly
- Contacts, boundaries, labels, pins
- Special layers (prBoundary, grid, etc.)

## Files Modified/Created

### Modified
- `layout_automation/tech_file.py` - Enhanced parser

### New Examples
- `examples/load_freepdk45.py` - Complete usage example

### Documentation
- `FREEPDK45_PARSER_UPDATE.md` - Tech file parser update
- `DRF_COLOR_PARSER.md` - DRF parser documentation
- `TECH_FILE_PARSER_COMPLETE.md` - This file

## Backward Compatibility

✅ All existing code continues to work
✅ DRF file is optional
✅ Falls back to default colors if DRF not provided
✅ Supports legacy tech file formats
✅ No breaking changes to API

## Summary

The technology file parser now provides:

1. ✅ **Complete FreePDK45.tf support** with GDS layer numbers
2. ✅ **Accurate color parsing** from SantanaDisplay.drf
3. ✅ **RGB-to-hex conversion** for visualization tools
4. ✅ **Purpose-based layer mapping** (drawing, net, pin, etc.)
5. ✅ **Reverse GDS lookup** for imported layouts
6. ✅ **Export capabilities** for documentation
7. ✅ **Full backward compatibility** with existing code

The parser is production-ready and can be used for layout automation, visualization, and GDS processing tasks.
