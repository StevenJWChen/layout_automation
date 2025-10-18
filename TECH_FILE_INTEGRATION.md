# Technology File Integration

## Overview

The layout_automation package now includes comprehensive technology file support, enabling seamless integration with industry-standard EDA tools and foundry technology files. This feature provides:

- **Layer-to-GDS mapping**: Automatic translation between layer names and GDS layer numbers
- **Color definitions**: Import display colors from technology files
- **Virtuoso compatibility**: Parse Cadence Virtuoso technology files
- **GDS round-trip**: Export and import GDS files using consistent layer mappings

## Features

### ✓ Technology File Parser
- Parse Cadence Virtuoso technology files
- Extract layer definitions and purposes
- Import GDS layer/datatype mappings
- Import display colors from tech files
- Support for generic technology creation

### ✓ Layer Mapping System
- Bidirectional mapping: layer name ↔ (GDS layer, datatype)
- Multiple purposes per layer (drawing, pin, label, etc.)
- Color information attached to layers
- Fast lookup by name or GDS number

### ✓ GDS Import/Export Integration
- Export GDS using tech file layer numbers
- Import GDS using tech file layer mappings
- Automatic fallback to sensible defaults
- Round-trip verification support

### ✓ Style System Integration
- Apply tech file colors to visualization
- Automatic style configuration from tech file
- Override colors when needed

## Quick Start

### Creating a Custom Technology

```python
from layout_automation.tech_file import TechFile, LayerMapping, set_tech_file

# Create tech file
tech = TechFile()
tech.tech_name = "my_tech_180nm"

# Add layers with GDS numbers and colors
tech.add_layer(LayerMapping('nwell', 'drawing', 1, 0, 'lightgreen'))
tech.add_layer(LayerMapping('pwell', 'drawing', 2, 0, 'lightcoral'))
tech.add_layer(LayerMapping('poly', 'drawing', 10, 0, 'red'))
tech.add_layer(LayerMapping('metal1', 'drawing', 30, 0, 'blue'))
tech.add_layer(LayerMapping('contact', 'drawing', 20, 0, 'black'))

# Set as global tech file
set_tech_file(tech)
```

### Using Generic Technology

```python
from layout_automation.tech_file import get_tech_file

# Get the default generic tech file
tech = get_tech_file()  # Automatically creates generic tech if none exists

# View layer mappings
tech.print_summary()
```

### Parsing Virtuoso Technology Files

```python
from layout_automation.tech_file import load_tech_file

# Load Virtuoso tech file
tech = load_tech_file('path/to/techfile.tf')

# View what was loaded
tech.print_summary()

# Export layer mapping for reference
tech.export_layer_map('layer_mapping.txt')
```

### Applying Tech File Colors

```python
from layout_automation.tech_file import get_tech_file

tech = get_tech_file()

# Apply colors to style configuration
tech.apply_colors_to_style()

# Now all drawings will use tech file colors
cell.draw()
```

### GDS Export with Tech File

```python
from layout_automation.cell import Cell

# Create your layout
cell = Cell('my_chip')
# ... add children and constraints ...
cell.solver()

# Export using tech file layer numbers
cell.export_gds('output.gds', use_tech_file=True)
```

### GDS Import with Tech File

```python
from layout_automation.cell import Cell

# Import using tech file layer mappings
cell = Cell.from_gds('input.gds', use_tech_file=True)

# Draw with tech file colors
cell.draw()
```

## API Reference

### TechFile Class

Main class for managing technology information.

```python
class TechFile:
    def __init__(self)

    def add_layer(self, mapping: LayerMapping)
    def get_layer(self, name: str, purpose: str = 'drawing') -> Optional[LayerMapping]
    def get_layer_by_gds(self, gds_layer: int, gds_datatype: int = 0) -> Optional[LayerMapping]
    def get_gds_layer(self, name: str, purpose: str = 'drawing') -> Tuple[int, int]

    def parse_virtuoso_tech_file(self, filepath: str)
    def create_generic_tech(self, tech_name: str = 'generic')
    def apply_colors_to_style(self)

    def export_layer_map(self, filepath: str)
    def print_summary(self)
```

### LayerMapping Class

Stores information about a single layer.

```python
class LayerMapping:
    def __init__(self, name: str, purpose: str = 'drawing',
                 gds_layer: int = 0, gds_datatype: int = 0,
                 color: Optional[str] = None)

    # Attributes:
    name: str           # Layer name (e.g., 'metal1', 'poly')
    purpose: str        # Layer purpose (e.g., 'drawing', 'pin')
    gds_layer: int      # GDS layer number
    gds_datatype: int   # GDS datatype number
    color: str          # Display color (matplotlib color name)
```

### Global Functions

```python
def get_tech_file() -> TechFile
    """Get the global technology file instance"""

def set_tech_file(tech: TechFile)
    """Set the global technology file"""

def load_tech_file(filepath: str) -> TechFile
    """Load a technology file and set it as global"""
```

### Cell Methods (Enhanced)

```python
def export_gds(self, filename: str,
               unit: float = 1e-6,
               precision: float = 1e-9,
               layer_map: Dict[str, Tuple[int, int]] = None,
               use_tech_file: bool = True)
    """Export to GDS using tech file layer numbers"""

@classmethod
def from_gds(cls, filename: str,
             cell_name: Optional[str] = None,
             layer_map: Optional[Dict[Tuple[int, int], str]] = None,
             use_tech_file: bool = True) -> 'Cell'
    """Import from GDS using tech file layer mappings"""

@classmethod
def import_gds_to_cell(cls, filename: str,
                       cell_name: Optional[str] = None,
                       layer_map: Optional[Dict[Tuple[int, int], str]] = None,
                       add_position_constraints: bool = True,
                       use_tech_file: bool = True) -> 'Cell'
    """Import GDS with constraints using tech file"""
```

## Default Layer Numbers

When no technology file is provided, the system uses these default GDS layer numbers:

| Layer Name | GDS Layer | GDS Datatype | Default Color |
|------------|-----------|--------------|---------------|
| nwell      | 1         | 0            | lightgreen    |
| pwell      | 2         | 0            | lightcoral    |
| ndiff      | 3         | 0            | green         |
| pdiff      | 4         | 0            | tan           |
| poly       | 10        | 0            | red           |
| contact    | 20        | 0            | black         |
| metal1     | 30        | 0            | blue          |
| via1       | 40        | 0            | gray          |
| metal2     | 50        | 0            | red           |
| via2       | 60        | 0            | gray          |
| metal3     | 70        | 0            | green         |
| via3       | 80        | 0            | gray          |
| metal4     | 90        | 0            | orange        |
| via4       | 100       | 0            | gray          |
| metal5     | 110       | 0            | cyan          |
| via5       | 120       | 0            | gray          |
| metal6     | 130       | 0            | magenta       |

## Virtuoso Tech File Format

The parser supports these sections from Cadence Virtuoso technology files:

### Layer Definitions
```lisp
layerDefinitions(
    techLayerPurposePriorities("metal1" "drawing" 1)
    techLayerPurposePriorities("poly" "drawing" 2)
    ...
)
```

### Stream Layers (GDS Mapping)
```lisp
streamLayers(
    ("metal1" "drawing" 30 0)
    ("poly" "drawing" 10 0)
    ...
)
```

### Display Resources (Colors)
```lisp
drDefineDisplay(
    techLayerProperties("metal1" "drawing" ... color "blue" ...)
    techLayerProperties("poly" "drawing" ... color "red" ...)
    ...
)
```

## Examples

### Example 1: Complete Workflow

```python
from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile, LayerMapping, set_tech_file

# 1. Create technology file
tech = TechFile()
tech.tech_name = "demo_tech"
tech.add_layer(LayerMapping('metal1', 'drawing', 30, 0, 'blue'))
tech.add_layer(LayerMapping('poly', 'drawing', 10, 0, 'red'))
tech.add_layer(LayerMapping('contact', 'drawing', 20, 0, 'black'))
set_tech_file(tech)

# 2. Apply colors
tech.apply_colors_to_style()

# 3. Create layout
cell = Cell('my_design')
m1 = Cell('metal1_line', 'metal1')
poly = Cell('poly_gate', 'poly')
cont = Cell('contact1', 'contact')
cell.add_instance([m1, poly, cont])

cell.constrain(m1, 'x1=0, y1=0, x2-x1=20, y2-y1=5')
cell.constrain(poly, 'x1=5, y1=2, x2-x1=3, y2-y1=10')
cell.constrain(cont, 'sx1=ox1, sy1=oy1, sx2-sx1=2, sy2-sy1=2', m1)
cell.solver()

# 4. Export with tech file
cell.export_gds('design.gds', use_tech_file=True)

# 5. Import back
imported = Cell.from_gds('design.gds', use_tech_file=True)

# 6. Visualize
imported.draw()
```

### Example 2: Custom Layer Mapping

```python
from layout_automation.cell import Cell

# Create custom layer mapping (overrides tech file)
custom_mapping = {
    'metal1': (31, 0),   # Custom GDS numbers
    'poly': (11, 0),
    'contact': (21, 0),
}

# Export with custom mapping
cell.export_gds('custom.gds', layer_map=custom_mapping, use_tech_file=False)

# Import with reverse mapping
reverse_mapping = {
    (31, 0): 'metal1',
    (11, 0): 'poly',
    (21, 0): 'contact',
}
imported = Cell.from_gds('custom.gds', layer_map=reverse_mapping, use_tech_file=False)
```

### Example 3: Loading Virtuoso Tech File

```python
from layout_automation.tech_file import load_tech_file

# Load real Virtuoso tech file
tech = load_tech_file('/path/to/foundry/techfile.tf')

# View what was loaded
tech.print_summary()

# Export layer mapping for documentation
tech.export_layer_map('foundry_layers.txt')

# Apply colors to visualization
tech.apply_colors_to_style()

# Now use for GDS import/export
from layout_automation.cell import Cell

cell = Cell.from_gds('foundry_design.gds', use_tech_file=True)
cell.draw()  # Uses foundry colors
```

## Demo

Run the comprehensive demo:

```bash
python3 examples/demo_tech_file.py
```

This generates:
- `demo_outputs/test_with_techfile.gds` - GDS with tech file layer numbers
- `demo_outputs/layer_mapping.txt` - Layer mapping reference
- `demo_outputs/tech_file_roundtrip.png` - Visual comparison

The demo demonstrates:
1. Creating a custom technology file
2. Applying tech file colors to layouts
3. Exporting GDS with tech file layer numbers
4. Importing GDS using tech file layer mappings
5. Round-trip verification

## File Structure

```
layout_automation/
├── tech_file.py              # Technology file parser and manager
├── cell.py                   # Enhanced with tech file support
└── style_config.py           # Works with tech file colors

examples/
└── demo_tech_file.py         # Comprehensive demo

demo_outputs/
├── test_with_techfile.gds    # Demo output
├── layer_mapping.txt         # Layer reference
└── tech_file_roundtrip.png   # Visualization
```

## Technical Details

### Layer Lookup Performance

The tech file uses two dictionaries for fast bidirectional lookup:

```python
layers: Dict[Tuple[str, str], LayerMapping]           # (name, purpose) → mapping
gds_to_layer: Dict[Tuple[int, int], LayerMapping]    # (gds_layer, datatype) → mapping
```

Both lookups are O(1) constant time.

### GDS Export Process

1. For each layer in the layout:
   - Look up layer name in tech file
   - Get (gds_layer, gds_datatype) tuple
   - Use these numbers in GDS file

2. Fallback behavior:
   - If tech file not available → use defaults
   - If layer not in tech file → use (0, 0)
   - Custom layer_map overrides tech file

### GDS Import Process

1. For each shape in GDS file:
   - Extract (gds_layer, gds_datatype) from GDS
   - Look up in tech file reverse mapping
   - Get layer name
   - Create Cell with that layer name

2. Fallback behavior:
   - If tech file not available → use defaults
   - If GDS number not in tech file → use `layer_{number}`
   - Custom layer_map overrides tech file

### Color Application

When `tech.apply_colors_to_style()` is called:

1. Iterates through all layers in tech file
2. For layers with purpose='drawing':
   - Gets color from LayerMapping
   - Calls `style.set_layer_style(name, color=color)`
3. Only updates color, preserves other style properties

## Backward Compatibility

All existing code works without changes:

- `export_gds()` without `use_tech_file` parameter → uses defaults
- `from_gds()` without `use_tech_file` parameter → uses defaults
- Custom `layer_map` parameter overrides tech file
- No tech file loaded → generic tech created automatically

## Best Practices

### 1. Technology File Management

```python
# At the start of your project
from layout_automation.tech_file import load_tech_file

# Load once, use everywhere
tech = load_tech_file('my_tech.tf')
tech.apply_colors_to_style()

# Now all subsequent operations use this tech file
```

### 2. Layer Naming Convention

Use consistent layer names:
- ✓ `metal1`, `metal2`, `metal3` (good)
- ✗ `M1`, `m2`, `Metal3` (inconsistent)

### 3. Purpose Handling

The parser supports multiple purposes:
```python
tech.add_layer(LayerMapping('metal1', 'drawing', 30, 0))
tech.add_layer(LayerMapping('metal1', 'pin', 30, 1))
tech.add_layer(LayerMapping('metal1', 'label', 30, 2))
```

### 4. Color Customization

Override tech file colors when needed:
```python
# Tech file provides default colors
tech.apply_colors_to_style()

# Override specific layers
style = get_style_config()
style.set_layer_style('metal1', color='gold', alpha=0.8)
```

## Troubleshooting

### "Could not load tech file" Warning

If you see this warning:
```
Warning: Could not load tech file, using defaults: [error message]
```

Check:
1. Tech file exists and path is correct
2. Tech file format is supported (Virtuoso format)
3. File permissions allow reading

The system will automatically fall back to default layer mappings.

### Layer Not Found in Tech File

If a layer name isn't in the tech file:
- **Export**: Uses (0, 0) for unknown layers
- **Import**: Creates layer name like `layer_99` for unknown GDS numbers

### GDS Round-Trip Differences

After export → import, you may see:
- Different child ordering (expected)
- Same layer counts (verified)
- Same geometry (verified)

This is normal and doesn't affect correctness.

## Future Enhancements

Potential additions:
- Support for more tech file formats (LEF, Liberty, etc.)
- Layer purpose mapping for pins and labels
- Design rule information from tech files
- Multiple technology file support
- Tech file validation and error checking

## Credits

Technology file integration added: 2025-10-18

---

**Status:** ✓ Production ready
**Tests:** ✓ Comprehensive demo passing
**Documentation:** ✓ Complete
