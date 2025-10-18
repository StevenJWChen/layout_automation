# Style Customization Guide

Complete guide to customizing visualization styles in layout_automation.

## Overview

The style customization system allows you to control:
- **Layer colors** (fill colors for leaf cells)
- **Boundary colors** (edge colors, independent from fill)
- **Boundary thickness** (line width)
- **Shape types** (rectangle, rounded, circle, ellipse, octagon)
- **Container styles** (for hierarchical cells)
- **Transparency** (alpha values)

## Quick Start

```python
from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config

# Get the global style configuration
style = get_style_config()

# Customize a layer
style.set_layer_style('metal1',
                     color='gold',           # Fill color
                     alpha=0.7,              # Transparency (0.0 to 1.0)
                     edge_color='darkred',   # Boundary color
                     edge_width=3.0,         # Boundary thickness
                     shape='rounded')        # Shape type

# Create and draw your layout
cell = Cell('my_cell')
# ... add children and constraints ...
cell.draw()
```

## Layer Style Customization

### Available Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `color` | str | Fill color (any matplotlib color) | 'gray' |
| `alpha` | float | Transparency (0.0=transparent, 1.0=opaque) | 0.6 |
| `edge_color` | str | Boundary/edge color | 'black' |
| `edge_width` | float | Boundary line width | 2.0 |
| `shape` | str | Shape type (see below) | 'rectangle' |

### Shape Types

| Shape | Description | Best For |
|-------|-------------|----------|
| `'rectangle'` | Standard rectangle | Most layers, default |
| `'rounded'` | Rounded corners rectangle | Metal layers, softer look |
| `'circle'` | Circle (inscribed in bounds) | Contacts, vias, small features |
| `'ellipse'` | Ellipse (fills bounds) | Poly gates, elongated features |
| `'octagon'` | Regular octagon | Special markers, unique features |

### Color Examples

```python
from layout_automation.style_config import get_style_config

style = get_style_config()

# Using named colors
style.set_layer_style('metal1', color='blue')
style.set_layer_style('metal2', color='red')

# Using hex colors
style.set_layer_style('poly', color='#9B59B6')

# Using RGB tuples
style.set_layer_style('diff', color=(0.8, 0.4, 0.2))
```

### Complete Example

```python
from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config

# Configure styles
style = get_style_config()

# Metal layers - rounded with thick borders
style.set_layer_style('metal1',
                     color='steelblue',
                     alpha=0.8,
                     edge_color='navy',
                     edge_width=3.0,
                     shape='rounded')

style.set_layer_style('metal2',
                     color='firebrick',
                     alpha=0.8,
                     edge_color='darkred',
                     edge_width=3.0,
                     shape='rounded')

# Poly layer - ellipse shape
style.set_layer_style('poly',
                     color='mediumpurple',
                     alpha=0.7,
                     edge_color='indigo',
                     edge_width=2.5,
                     shape='ellipse')

# Contacts - circular
style.set_layer_style('contact',
                     color='gray',
                     alpha=0.9,
                     edge_color='black',
                     edge_width=1.5,
                     shape='circle')

# Create layout
cell = Cell('custom_chip')
# ... add children and constraints ...
cell.draw()
```

## Container Style Customization

Container cells (non-leaf cells with children) have separate styling:

```python
style = get_style_config()

style.set_container_style(
    edge_color='crimson',      # Boundary color
    edge_width=3.0,            # Boundary thickness
    linestyle='-.',            # Line style: '-', '--', '-.', ':'
    alpha=1.0,                 # Transparency
    shape='rounded'            # Shape type
)
```

### Container Color Cycling

Different hierarchy levels can have different colors:

```python
# Set custom color cycle for hierarchy levels
style.set_container_colors(['crimson', 'navy', 'darkgreen', 'darkorange'])

# Now containers will cycle through these colors at different levels
```

## Default Layer Styles

Built-in defaults for common layers:

| Layer | Color | Edge Color | Shape |
|-------|-------|------------|-------|
| `metal1` | blue | darkblue | rectangle |
| `metal2` | red | darkred | rectangle |
| `metal3` | green | darkgreen | rectangle |
| `metal4` | orange | darkorange | rectangle |
| `metal5` | cyan | darkcyan | rectangle |
| `metal6` | magenta | darkmagenta | rectangle |
| `poly` | purple | indigo | rectangle |
| `diff` | brown | saddlebrown | rectangle |
| `nwell` | lightgreen | green | rectangle |
| `pwell` | lightcoral | red | rectangle |
| `contact` | gray | black | rectangle |
| `via` | silver | black | rectangle |

## Resetting to Defaults

```python
from layout_automation.style_config import reset_style_config

# Reset all styles to defaults
reset_style_config()
```

## Advanced Usage

### Theme Creation

Create reusable themes:

```python
def apply_dark_theme():
    """Apply a dark theme to the layout"""
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

def apply_bright_theme():
    """Apply a bright, colorful theme"""
    style = get_style_config()

    style.set_layer_style('metal1', color='cyan', edge_color='teal',
                         edge_width=3.0, shape='rounded')
    style.set_layer_style('metal2', color='magenta', edge_color='purple',
                         edge_width=3.0, shape='rounded')
    style.set_layer_style('poly', color='yellow', edge_color='orange',
                         edge_width=2.5, shape='octagon')

# Use themes
apply_dark_theme()
cell.draw()

reset_style_config()
apply_bright_theme()
cell.draw()
```

### Per-Layer Partial Updates

You can update individual properties without affecting others:

```python
style = get_style_config()

# Only change color, keep other properties
style.set_layer_style('metal1', color='gold')

# Only change edge properties
style.set_layer_style('metal1', edge_color='darkgoldenrod', edge_width=4.0)

# Only change shape
style.set_layer_style('metal1', shape='rounded')
```

### Matplotlib Color Reference

All matplotlib colors are supported:
- **Named colors**: 'red', 'blue', 'green', 'gold', 'crimson', etc.
- **Hex colors**: '#FF5733', '#3498DB', etc.
- **RGB tuples**: (0.5, 0.2, 0.8), (1.0, 0.0, 0.5), etc.
- **RGBA tuples**: (0.5, 0.2, 0.8, 0.7) - includes alpha

See: https://matplotlib.org/stable/gallery/color/named_colors.html

## Examples Gallery

### Example 1: Simple Color Change
```python
style = get_style_config()
style.set_layer_style('metal1', color='gold')
```

### Example 2: Thick Borders
```python
style = get_style_config()
style.set_layer_style('metal1', edge_width=5.0, edge_color='darkred')
```

### Example 3: Different Shapes
```python
style = get_style_config()
style.set_layer_style('metal1', shape='rounded')
style.set_layer_style('contact', shape='circle')
style.set_layer_style('poly', shape='ellipse')
```

### Example 4: Transparency Control
```python
style = get_style_config()
style.set_layer_style('nwell', color='lightgreen', alpha=0.3)  # Very transparent
style.set_layer_style('metal1', color='blue', alpha=0.9)       # Almost opaque
```

### Example 5: Complete Custom Style
```python
style = get_style_config()

# Custom metal stack
for i, (color, edge) in enumerate([
    ('gold', 'darkgoldenrod'),
    ('silver', 'gray'),
    ('copper', 'saddlebrown'),
    ('bronze', 'chocolate')
], start=1):
    style.set_layer_style(f'metal{i}',
                         color=color,
                         edge_color=edge,
                         edge_width=2.5,
                         alpha=0.8,
                         shape='rounded')
```

## API Reference

### `get_style_config() -> StyleConfig`
Get the global style configuration instance.

### `reset_style_config()`
Reset all styles to default values.

### `StyleConfig.set_layer_style(layer_name, color=None, alpha=None, edge_color=None, edge_width=None, shape=None)`
Set style for a specific layer.

### `StyleConfig.set_container_style(edge_color=None, edge_width=None, linestyle=None, alpha=None, shape=None)`
Set style for container cells.

### `StyleConfig.set_container_colors(colors: list)`
Set color cycle for containers at different hierarchy levels.

### `StyleConfig.get_layer_style(layer_name) -> LayerStyle`
Get current style for a layer.

## Tips and Best Practices

1. **Consistency**: Use similar styles for similar layer types (e.g., all metal layers with rounded shapes)

2. **Contrast**: Ensure sufficient contrast between fill and edge colors for visibility

3. **Transparency**: Use alpha values to show overlapping layers clearly

4. **Hierarchy**: Use different container colors for different hierarchy levels to show structure

5. **Performance**: Complex shapes (octagon, circle) may render slightly slower than rectangles

6. **Themes**: Create reusable theme functions for consistent styling across projects

7. **Reset**: Always reset before applying a new theme to avoid mixing styles

## Troubleshooting

**Q: Colors not showing up?**
- Check that you're calling `get_style_config()` before drawing
- Verify color names are valid matplotlib colors

**Q: Shapes look wrong?**
- Some shapes (circle, octagon) are inscribed in the cell bounds
- Use 'ellipse' for shapes that fill the full rectangle

**Q: Styles not applying?**
- Ensure you set styles BEFORE calling `cell.draw()`
- Check that layer names match exactly (case-sensitive)

**Q: How to see all available colors?**
- Visit: https://matplotlib.org/stable/gallery/color/named_colors.html
- Or use hex codes: '#FF5733'

## See Also

- `examples/demo_style_customization.py` - Complete demonstration
- `examples/test_style_features.py` - Unit tests
- Matplotlib color documentation: https://matplotlib.org/stable/tutorials/colors/colors.html
