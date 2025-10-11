# GDS to Constraint Format Tool

A powerful tool to import GDS files and convert them into editable constraint files that users can modify and regenerate.

## Overview

This tool enables **parametric modification** of existing GDS layouts without needing to understand the original design flow:

1. **Import** existing GDS layout
2. **Extract** to human-readable constraint format (YAML/JSON)
3. **Edit** dimensions, spacing, and positions
4. **Regenerate** GDS with modified parameters

## Features

✨ **Human-Readable Format**: Constraints exported as YAML or JSON
✨ **Automatic Spacing Analysis**: Detects relationships between polygons
✨ **Layer Mapping**: Support for technology-specific layer names
✨ **Full Round-Trip**: GDS → Constraints → Modified GDS
✨ **Programmatic API**: Modify constraints in Python code
✨ **Command-Line Interface**: Easy to use from terminal

## Installation

```bash
# The tool is part of the layout_automation package
pip install -e .

# Or use directly without installation
PYTHONPATH=. python tools/gds_to_constraints.py
```

## Quick Start

### 1. Convert GDS to Constraints

```bash
# Convert GDS file to YAML constraints
python tools/gds_to_constraints.py input.gds output.yaml

# Specify cell name (if GDS has multiple cells)
python tools/gds_to_constraints.py input.gds output.yaml my_cell_name

# Output as JSON instead
python tools/gds_to_constraints.py input.gds output.json
```

### 2. Edit the Constraint File

Open `output.yaml` in any text editor and modify dimensions:

```yaml
cell_name: my_cell
dimensions:
  width: 100.0
  height: 50.0
polygons:
  - name: metal1_1
    layer: metal1
    layer_num: 67
    datatype: 0
    position:
      x1: 0.0      # ← Edit these
      y1: 0.0
      x2: 20.0
      y2: 10.0
    size:
      width: 20.0  # ← Or edit these
      height: 10.0
    spacing:       # Optional spacing constraints
      - type: horizontal_spacing
        to: metal1_2
        spacing: 5.0
        direction: right
```

### 3. Regenerate GDS

```bash
# Generate new GDS from modified constraints
python tools/gds_to_constraints.py --regenerate output.yaml new_layout.gds
```

## Detailed Usage

### Command-Line Interface

```bash
# Basic conversion
python tools/gds_to_constraints.py <input.gds> <output.yaml> [cell_name]

# Regeneration
python tools/gds_to_constraints.py --regenerate <constraints.yaml> <output.gds>
```

### Python API

#### Convert GDS to Constraints

```python
from tools.gds_to_constraints import GDSToConstraints

# Create converter
converter = GDSToConstraints('input.gds', cell_name='my_cell')

# Optional: Set layer name mapping
layer_map = {
    67: 'metal1',
    66: 'poly',
    65: 'diff',
    64: 'nwell'
}
converter.set_layer_map(layer_map)

# Extract constraints
constraints = converter.extract_constraints(
    analyze_spacing=True,      # Detect spacing relationships
    spacing_threshold=10.0     # Max distance for spacing (um)
)

# Export to YAML
converter.export_to_yaml('output.yaml', constraints)

# Or export to JSON
converter.export_to_json('output.json', constraints)
```

#### Modify Constraints Programmatically

```python
from tools.gds_to_constraints import GDSToConstraints

# Load and extract
converter = GDSToConstraints('input.gds')
constraints = converter.extract_constraints()

# Modify constraints
for poly in constraints.polygons:
    # Scale all metal1 polygons by 1.5x
    if poly.layer == 'metal1':
        poly.width *= 1.5
        poly.height *= 1.5
        poly.x2 = poly.x1 + poly.width
        poly.y2 = poly.y1 + poly.height

    # Move all polygons up by 100 units
    poly.y1 += 100
    poly.y2 += 100

# Export modified constraints
converter.export_to_yaml('modified.yaml', constraints)
```

#### Regenerate GDS

```python
from tools.gds_to_constraints import ConstraintsToGDS

# Load constraint file
regenerator = ConstraintsToGDS('modified.yaml')

# Generate GDS
regenerator.generate_gds(
    'output.gds',
    units=(1e-6, 1e-9)  # (unit, precision)
)
```

## Constraint File Format

### YAML Format (Recommended)

```yaml
cell_name: inverter
dimensions:
  width: 1500.0    # Total cell width
  height: 2000.0   # Total cell height

polygons:
  - name: diff_1              # Unique polygon name
    layer: diff               # Layer name (human-readable)
    layer_num: 65             # GDS layer number
    datatype: 0               # GDS datatype

    position:                 # Absolute position
      x1: 100.0               # Lower-left X
      y1: 200.0               # Lower-left Y
      x2: 500.0               # Upper-right X
      y2: 800.0               # Upper-right Y

    size:                     # Dimensions
      width: 400.0            # Width (x2 - x1)
      height: 600.0           # Height (y2 - y1)

    spacing:                  # Optional spacing constraints
      - type: horizontal_spacing
        to: diff_2            # Target polygon
        spacing: 150.0        # Distance
        direction: right      # Direction
```

### JSON Format

```json
{
  "cell_name": "inverter",
  "dimensions": {
    "width": 1500.0,
    "height": 2000.0
  },
  "polygons": [
    {
      "name": "diff_1",
      "layer": "diff",
      "layer_num": 65,
      "datatype": 0,
      "position": {
        "x1": 100.0,
        "y1": 200.0,
        "x2": 500.0,
        "y2": 800.0
      },
      "size": {
        "width": 400.0,
        "height": 600.0
      }
    }
  ]
}
```

## Common Use Cases

### 1. Scale Entire Design

```python
# Scale all dimensions by 1.2x
import yaml

with open('constraints.yaml', 'r') as f:
    data = yaml.safe_load(f)

scale = 1.2

for poly in data['polygons']:
    poly['size']['width'] *= scale
    poly['size']['height'] *= scale
    poly['position']['x1'] *= scale
    poly['position']['y1'] *= scale
    poly['position']['x2'] *= scale
    poly['position']['y2'] *= scale

with open('constraints_scaled.yaml', 'w') as f:
    yaml.dump(data, f)
```

### 2. Adjust Specific Layer

```python
# Make all metal1 shapes 20% wider
import yaml

with open('constraints.yaml', 'r') as f:
    data = yaml.safe_load(f)

for poly in data['polygons']:
    if poly['layer'] == 'metal1':
        width_increase = poly['size']['width'] * 0.2
        poly['size']['width'] += width_increase
        poly['position']['x2'] += width_increase

with open('constraints_modified.yaml', 'w') as f:
    yaml.dump(data, f)
```

### 3. Maintain Spacing Ratios

```python
# Increase all spacing by 50% while maintaining ratios
import yaml

with open('constraints.yaml', 'r') as f:
    data = yaml.safe_load(f)

for poly in data['polygons']:
    if 'spacing' in poly:
        for constraint in poly['spacing']:
            if 'spacing' in constraint:
                constraint['spacing'] *= 1.5

with open('constraints_spaced.yaml', 'w') as f:
    yaml.dump(data, f)
```

## Advanced Features

### Layer Mapping

For technology-specific workflows, provide layer mapping:

```python
# SkyWater SKY130 layer mapping
skywater_layers = {
    67: 'metal1',
    68: 'metal2',
    69: 'metal3',
    70: 'metal4',
    71: 'metal5',
    66: 'poly',
    65: 'diff',
    64: 'nwell',
    44: 'via1',
    # ... more layers
}

converter = GDSToConstraints('sky130_cell.gds')
converter.set_layer_map(skywater_layers)
constraints = converter.extract_constraints()
```

### Spacing Analysis

The tool can automatically detect spacing relationships:

```python
constraints = converter.extract_constraints(
    analyze_spacing=True,      # Enable spacing analysis
    spacing_threshold=5.0      # Only consider polygons within 5um
)

# Resulting constraints will include spacing info:
# spacing:
#   - type: horizontal_spacing
#     to: other_polygon
#     spacing: 2.5
#     direction: right
```

### Custom Units

When regenerating GDS, specify custom units:

```python
regenerator = ConstraintsToGDS('constraints.yaml')

# Default: (1e-6, 1e-9) = 1um unit, 1nm precision
regenerator.generate_gds('output.gds', units=(1e-6, 1e-9))

# For finer precision:
regenerator.generate_gds('output.gds', units=(1e-6, 1e-12))
```

## Workflow Examples

### Example 1: Transistor Width Scaling

```bash
# 1. Extract inverter to constraints
python tools/gds_to_constraints.py inverter.gds inv_constraints.yaml

# 2. Edit YAML file - change transistor widths
#    (Find diff/poly layers and adjust width)

# 3. Regenerate GDS
python tools/gds_to_constraints.py --regenerate inv_constraints.yaml inverter_scaled.gds

# 4. Verify with visualization
python tools/gds_to_png.py inverter_scaled.gds inverter_scaled.png
```

### Example 2: Design Rule Migration

```python
# Migrate design to new technology with different spacing rules

from tools.gds_to_constraints import GDSToConstraints, ConstraintsToGDS
import yaml

# Extract from old technology
converter = GDSToConstraints('old_tech.gds')
constraints = converter.extract_constraints()
converter.export_to_yaml('temp.yaml')

# Load and modify for new rules
with open('temp.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Apply new design rules
MIN_SPACING = 200  # nm
for poly in data['polygons']:
    if 'spacing' in poly:
        for sc in poly['spacing']:
            if sc['spacing'] < MIN_SPACING:
                sc['spacing'] = MIN_SPACING

# Save and regenerate
with open('new_tech_constraints.yaml', 'w') as f:
    yaml.dump(data, f)

regenerator = ConstraintsToGDS('new_tech_constraints.yaml')
regenerator.generate_gds('new_tech.gds')
```

## Limitations

- **Polygon Shapes**: Currently supports rectangles (bounding boxes). Complex polygons are converted to their bounding rectangles.
- **Instances**: Cell instances are flattened during extraction.
- **Text/Labels**: Text annotations are not preserved.
- **Paths**: GDS paths are not yet supported (will be added in future version).

## Tips & Best Practices

1. **Backup Original**: Always keep a copy of the original GDS before modifying
2. **Verify Results**: Use `gds_to_png` to visualize regenerated layouts
3. **Layer Names**: Provide layer mapping for better readability
4. **Incremental Changes**: Make small changes and test frequently
5. **Version Control**: Track constraint files in git for history

## Troubleshooting

### Issue: Constraint file has strange formatting

**Solution**: Ensure PyYAML is installed: `pip install pyyaml`

### Issue: Regenerated GDS looks different

**Problem**: Complex polygons are converted to bounding boxes
**Solution**: This tool is best for parametric adjustments of existing rectangular shapes

### Issue: Layer numbers don't match

**Solution**: Provide correct layer mapping for your technology

## See Also

- `tools/gds_to_png.py` - GDS visualization tool
- `examples/gds_constraint_workflow.py` - Complete workflow examples
- `MODULE_GUIDE.md` - General package documentation

## Contributing

Improvements welcome! Particularly:
- Support for arbitrary polygon shapes
- Cell instance preservation
- Path support
- GUI for constraint editing

---

**Tool Version**: 1.0
**Author**: Layout Automation Team
**License**: MIT
