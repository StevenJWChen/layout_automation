# Style Customization Features

## Summary

The layout_automation package now includes a comprehensive style customization system that gives you full control over how your layouts are visualized.

## What's New

### Layer Customization
- ✓ **Custom colors** - Any matplotlib color (named, hex, RGB)
- ✓ **Boundary colors** - Independent edge colors
- ✓ **Boundary thickness** - Adjustable line widths
- ✓ **Shape types** - 5 different shapes (rectangle, rounded, circle, ellipse, octagon)
- ✓ **Transparency** - Alpha control from 0.0 to 1.0

### Container Customization
- ✓ **Edge styling** - Color, width, and line style
- ✓ **Shape support** - Rectangle and rounded
- ✓ **Color cycling** - Different colors for hierarchy levels

### Usability
- ✓ **Simple API** - Easy to use configuration system
- ✓ **Theme support** - Create reusable style themes
- ✓ **Reset functionality** - Return to defaults anytime
- ✓ **Backward compatible** - Existing code works unchanged

## Quick Example

```python
from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config

# Get style configuration
style = get_style_config()

# Customize layers
style.set_layer_style('metal1',
                     color='gold',           # Fill color
                     alpha=0.7,              # Transparency
                     edge_color='darkred',   # Boundary color
                     edge_width=3.0,         # Boundary thickness
                     shape='rounded')        # Shape type

style.set_layer_style('contact',
                     color='gray',
                     shape='circle',         # Circular contacts
                     edge_width=1.5)

# Create and draw layout
cell = Cell('my_chip')
# ... add children and constraints ...
cell.draw()  # Uses custom styles!
```

## Available Shapes

| Shape | Best For | Example |
|-------|----------|---------|
| **rectangle** | Default, most layers | Standard metal layers |
| **rounded** | Softer appearance | Metal layers, blocks |
| **circle** | Small, symmetric features | Contacts, vias |
| **ellipse** | Elongated features | Poly gates |
| **octagon** | Special markers | Alignment marks |

## Color Options

### Named Colors
```python
style.set_layer_style('metal1', color='steelblue')
style.set_layer_style('metal2', color='firebrick')
style.set_layer_style('poly', color='mediumpurple')
```

### Hex Colors
```python
style.set_layer_style('metal1', color='#4682B4')  # Steel blue
style.set_layer_style('metal2', color='#B22222')  # Fire brick
```

### RGB Tuples
```python
style.set_layer_style('metal1', color=(0.27, 0.51, 0.71))  # Steel blue
```

## Documentation Files

1. **STYLE_CUSTOMIZATION_GUIDE.md** - Complete documentation
   - All features explained in detail
   - Many examples and use cases
   - API reference
   - Troubleshooting

2. **STYLE_QUICK_REFERENCE.md** - Quick reference
   - Common tasks and code snippets
   - Color and shape tables
   - Quick examples

3. **examples/demo_style_customization.py** - Comprehensive demo
   - 5 different demos showing all features
   - Generates example images

4. **examples/test_style_features.py** - Unit tests
   - All features tested
   - Verification of functionality

## Default Layer Styles

The system includes sensible defaults for 12 common layers:

| Layer | Default Color | Shape |
|-------|---------------|-------|
| metal1 | blue | rectangle |
| metal2 | red | rectangle |
| metal3 | green | rectangle |
| metal4 | orange | rectangle |
| metal5 | cyan | rectangle |
| metal6 | magenta | rectangle |
| poly | purple | rectangle |
| diff | brown | rectangle |
| nwell | lightgreen | rectangle |
| pwell | lightcoral | rectangle |
| contact | gray | rectangle |
| via | silver | rectangle |

## Theme Example

Create reusable themes:

```python
def dark_theme():
    """Professional dark theme"""
    style = get_style_config()

    style.set_layer_style('metal1', color='steelblue', edge_color='navy',
                         edge_width=2.5, shape='rounded')
    style.set_layer_style('metal2', color='firebrick', edge_color='darkred',
                         edge_width=2.5, shape='rounded')
    style.set_layer_style('poly', color='mediumpurple', edge_color='indigo',
                         edge_width=2.0, shape='ellipse')
    style.set_layer_style('contact', color='gray', edge_color='black',
                         edge_width=1.5, shape='circle')

    style.set_container_style(edge_color='darkslategray', edge_width=2.0,
                             linestyle='--', shape='rounded')

def bright_theme():
    """Colorful bright theme"""
    style = get_style_config()

    style.set_layer_style('metal1', color='cyan', edge_color='teal',
                         edge_width=3.0, shape='rounded')
    style.set_layer_style('metal2', color='magenta', edge_color='purple',
                         edge_width=3.0, shape='rounded')
    style.set_layer_style('poly', color='yellow', edge_color='orange',
                         edge_width=2.5, shape='octagon')

# Apply themes
dark_theme()
cell1.draw()

reset_style_config()
bright_theme()
cell2.draw()
```

## Demo Output

Run the demo to see all features:

```bash
python3 examples/demo_style_customization.py
```

This generates 5 example images in `demo_outputs/`:
1. `style_custom_colors.png` - Basic color customization
2. `style_shapes.png` - Different shape types
3. `style_containers.png` - Container boundary styles
4. `style_advanced.png` - Advanced multi-layer theme
5. `style_comparison.png` - Default vs custom comparison

## API Summary

### Get Configuration
```python
from layout_automation.style_config import get_style_config, reset_style_config

style = get_style_config()
```

### Set Layer Style
```python
style.set_layer_style(layer_name,
                     color=None,        # Fill color
                     alpha=None,        # Transparency (0.0-1.0)
                     edge_color=None,   # Boundary color
                     edge_width=None,   # Boundary thickness
                     shape=None)        # Shape type
```

### Set Container Style
```python
style.set_container_style(
    edge_color=None,    # Boundary color
    edge_width=None,    # Boundary thickness
    linestyle=None,     # '-', '--', '-.', ':'
    alpha=None,         # Transparency
    shape=None)         # Shape type
```

### Reset
```python
reset_style_config()  # Return to defaults
```

## Backward Compatibility

All existing code works without changes. The style system:
- Has sensible defaults matching the original appearance
- Only activates when you explicitly customize styles
- Can be reset to defaults at any time

## Performance

The style system adds minimal overhead:
- Styles are configured once, applied during drawing
- No impact on solver performance
- Slightly slower rendering for complex shapes (circle, octagon) vs rectangles

## Integration

The style system integrates seamlessly with:
- ✓ All existing Cell functionality
- ✓ fix_layout and frozen cells
- ✓ Hierarchical structures
- ✓ Constraint solving
- ✓ GDS import/export

## Testing

Comprehensive test coverage:
- Unit tests for all style features
- Visual output verification
- Default and reset functionality
- All shape types tested
- Color and boundary customization verified

Run tests:
```bash
python3 examples/test_style_features.py
```

## Future Enhancements

Potential future additions:
- Pattern fills (hatching, stippling)
- Gradient fills
- 3D visualization
- Animation support
- SVG export with styles
- Style file import/export (JSON, YAML)

## Credits

Style customization system added: 2025-10-17

---

**Status:** ✓ Production ready
**Tests:** ✓ All passing
**Documentation:** ✓ Complete
