# Automatic Layer Mapping Config File Feature

## Overview

When exporting GDS files, if some layers are not defined in the tech file or default mappings, the system will:
1. **Auto-assign** GDS layer numbers (starting from 200)
2. **Auto-generate** a `.layermap` config file alongside the GDS
3. **Auto-load** this config file when importing the GDS

This ensures layer names are preserved through save/load cycles, even for custom or undefined layers.

## How It Works

### Export (save GDS)

```python
from layout_automation.cell import Cell

# Create layout with custom layers
r1 = Cell('r1', 'metal1')           # Defined in defaults
r2 = Cell('r2', 'my_custom_layer')  # NOT defined - will auto-assign

top = Cell('top')
top.add_instance([r1, r2])
top.constrain(r1, 'x1=0, y1=0, x2=10, y2=10')
top.constrain(r2, 'x1=15, y1=0, x2=25, y2=10')
top.solver()

# Export - will create both .gds and .layermap files
top.export_gds('my_layout.gds', use_tech_file=False)
```

**Output:**
```
Exported to my_layout.gds
Saved layer mapping to my_layout.layermap (1 undefined layers)
```

**Generated Files:**
- `my_layout.gds` - The GDS file
- `my_layout.layermap` - Auto-generated config (JSON format)

### Config File Format

The `.layermap` file is a JSON file with this structure:

```json
{
  "metadata": {
    "generated": "2025-11-01T08:25:53.778960",
    "description": "Auto-generated GDS layer mapping for undefined layers",
    "note": "Layers from tech file or defaults are not included here"
  },
  "undefined_layers": {
    "my_custom_layer": {
      "layer": 200,
      "datatype": 0
    },
    "another_custom_layer": {
      "layer": 201,
      "datatype": 0
    }
  },
  "defined_layers_count": 19
}
```

### Import (load GDS)

```python
# Import - automatically loads the .layermap config if it exists
imported = Cell.from_gds('my_layout.gds', use_tech_file=False)
```

**Output:**
```
Loaded additional 1 layers from my_layout.layermap
```

The layer name `my_custom_layer` is automatically restored!

## Layer Number Assignment

### Defined Layers (from tech file or defaults)

Standard layers use predefined GDS layer numbers:
- `metal1` → 30
- `metal2` → 50
- `poly` → 10
- `nwell` → 1
- `contact` → 20
- etc.

### Undefined Layers (auto-assigned)

Layers not in the tech file or defaults are auto-assigned starting from **200**:
- First undefined layer → 200
- Second undefined layer → 201
- Third undefined layer → 202
- etc.

This avoids conflicts with standard layer numbers (typically 0-150).

## Benefits

### 1. **No Manual Layer Mapping Required**

Before:
```python
# Had to manually provide layer mapping for custom layers
layer_map = {
    'my_custom_layer': (200, 0),
    'another_layer': (201, 0)
}
top.export_gds('file.gds', layer_map=layer_map)
```

After:
```python
# Just export - mapping is automatic!
top.export_gds('file.gds')
```

### 2. **Perfect Round-Trip Preservation**

```python
# Export with custom layers
top.export_gds('layout.gds')

# Import - layer names automatically restored
imported = Cell.from_gds('layout.gds')

# Export again - same layer mapping is used
imported.export_gds('layout2.gds')
```

All layer names are preserved across multiple save/load cycles!

### 3. **Works with Tech Files**

If you're using a tech file, undefined layers are still handled:

```python
from layout_automation.tech_file import TechFile, set_tech_file

# Load tech file (defines metal1, poly, etc.)
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
set_tech_file(tech)

# Create layout with mix of defined and undefined layers
r1 = Cell('r1', 'metal1')      # In tech file
r2 = Cell('r2', 'my_layer')    # Not in tech file - auto-assigned

top = Cell('top')
top.add_instance([r1, r2])
# ... constrain and solve ...

# Export - uses tech file for metal1, auto-assigns my_layer
top.export_gds('layout.gds', use_tech_file=True)
# Creates layout.layermap with just 'my_layer'
```

## File Management

### Config File Location

The `.layermap` file is always created in the same directory and with the same basename as the GDS file:

```python
top.export_gds('outputs/my_design.gds')
# Creates: outputs/my_design.gds
#          outputs/my_design.layermap

top.export_gds('/path/to/chip.gds')
# Creates: /path/to/chip.gds
#          /path/to/chip.layermap
```

### Manual Editing

You can manually edit the `.layermap` file if needed:

```json
{
  "undefined_layers": {
    "my_layer": {
      "layer": 150,      // Change layer number
      "datatype": 1      // Change datatype
    }
  }
}
```

The changes will be used on next import.

### Distributing GDS Files

When sharing GDS files, include the `.layermap` file:

```
my_chip.gds
my_chip.layermap  ← Include this!
```

The recipient's import will automatically use the correct layer mapping.

## Advanced Usage

### Disabling Auto-Load

If you want to import without auto-loading the config:

```python
# Manually specify layer map (config file is ignored)
manual_map = {(200, 0): 'different_name'}
imported = Cell.from_gds('file.gds', layer_map=manual_map)
```

### Checking Undefined Layers

After export, check if any layers were undefined:

```python
import os
gds_file = 'layout.gds'
config_file = os.path.splitext(gds_file)[0] + '.layermap'

if os.path.exists(config_file):
    import json
    with open(config_file) as f:
        config = json.load(f)
    print(f"Undefined layers: {list(config['undefined_layers'].keys())}")
```

### Pre-defining Custom Layers

To avoid auto-assignment, define layers explicitly:

```python
# Define your custom layers upfront
layer_map = {
    'my_special_layer': (150, 0),
    'another_layer': (151, 0)
}

top.export_gds('file.gds', layer_map=layer_map, use_tech_file=False)
# No .layermap file created since all layers are defined
```

## Example: Complete Workflow

```python
from layout_automation.cell import Cell

# Create design with mix of standard and custom layers
metal = Cell('metal', 'metal1')        # Standard
custom = Cell('custom', 'my_label')    # Custom
marker = Cell('marker', 'debug_layer') # Custom

top = Cell('top')
top.add_instance([metal, custom, marker])
top.constrain(metal, 'x1=0, y1=0, x2=10, y2=10')
top.constrain(custom, 'x1=15, y1=0, x2=25, y2=10')
top.constrain(marker, 'x1=30, y1=0, x2=40, y2=10')
top.solver()

# Export - creates both .gds and .layermap
top.export_gds('design.gds')
# Output: Saved layer mapping to design.layermap (2 undefined layers)

# Later... import the design
imported = Cell.from_gds('design.gds')
# Output: Loaded additional 2 layers from design.layermap

# Verify layer names are preserved
for child in imported.children:
    print(f"Layer: {child.layer_name}")
# Output:
#   Layer: metal1
#   Layer: my_label
#   Layer: debug_layer
```

## Troubleshooting

### Config File Not Created

The config file is only created if there are undefined layers. If all layers are in the tech file or defaults, no config is needed.

### Layer Names Changed After Import

Make sure the `.layermap` file is in the same directory as the `.gds` file. Check the import output for:
```
Loaded additional N layers from filename.layermap
```

### GDS Layer Number Conflicts

Auto-assigned layers start at 200 to avoid conflicts. If you need different numbers, manually edit the `.layermap` file or provide a custom `layer_map` during export.

## Testing

Run the comprehensive test:

```bash
python test_auto_layermap.py
```

This verifies:
- Auto-assignment of undefined layers
- Config file generation
- Auto-loading on import
- Round-trip preservation
- Position preservation

## Summary

✅ **Automatic** - No manual layer mapping needed
✅ **Transparent** - Works seamlessly with existing code
✅ **Preserving** - Layer names survive save/load cycles
✅ **Compatible** - Works with tech files and defaults
✅ **Distributable** - Easy to share with `.layermap` file

The feature makes working with custom layers effortless while maintaining full compatibility with standard workflows!
