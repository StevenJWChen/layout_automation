# Style Customization - Quick Reference

## Basic Usage

```python
from layout_automation.style_config import get_style_config

style = get_style_config()
```

## Layer Customization

### Change Color
```python
style.set_layer_style('metal1', color='gold')
```

### Change Boundary
```python
style.set_layer_style('metal1',
                     edge_color='darkred',
                     edge_width=3.0)
```

### Change Shape
```python
style.set_layer_style('metal1', shape='rounded')   # Rounded rectangle
style.set_layer_style('contact', shape='circle')    # Circle
style.set_layer_style('poly', shape='ellipse')      # Ellipse
style.set_layer_style('marker', shape='octagon')    # Octagon
```

### Change Transparency
```python
style.set_layer_style('nwell', alpha=0.3)  # 30% opaque (70% transparent)
```

### All Together
```python
style.set_layer_style('metal1',
                     color='steelblue',      # Fill color
                     alpha=0.8,              # 80% opaque
                     edge_color='navy',      # Border color
                     edge_width=3.0,         # Border thickness
                     shape='rounded')        # Rounded corners
```

## Container Customization

```python
style.set_container_style(
    edge_color='crimson',    # Border color
    edge_width=3.0,          # Border thickness
    linestyle='-.',          # Line style: '-', '--', '-.', ':'
    shape='rounded'          # Shape type
)
```

## Color Cycling

```python
# Set colors for different hierarchy levels
style.set_container_colors(['red', 'blue', 'green', 'orange'])
```

## Reset to Defaults

```python
from layout_automation.style_config import reset_style_config

reset_style_config()
```

## Shape Types

| Shape | Use For |
|-------|---------|
| `'rectangle'` | Default, most layers |
| `'rounded'` | Metal layers, softer look |
| `'circle'` | Contacts, vias |
| `'ellipse'` | Poly gates, elongated features |
| `'octagon'` | Special markers |

## Common Colors

| Color Name | Appearance |
|------------|------------|
| `'blue'`, `'red'`, `'green'` | Primary colors |
| `'gold'`, `'silver'`, `'bronze'` | Metallic |
| `'steelblue'`, `'firebrick'`, `'darkgreen'` | Darker shades |
| `'cyan'`, `'magenta'`, `'yellow'` | Bright |
| `'purple'`, `'orange'`, `'pink'` | Vivid |
| `'gray'`, `'lightgray'`, `'darkgray'` | Neutral |

Or use hex: `'#FF5733'` or RGB: `(0.5, 0.2, 0.8)`

## Line Styles

| Style | Appearance |
|-------|------------|
| `'-'` | Solid line |
| `'--'` | Dashed line |
| `'-.'` | Dash-dot line |
| `':'` | Dotted line |

## Quick Examples

### Example 1: Gold Metal with Thick Border
```python
style.set_layer_style('metal1',
                     color='gold',
                     edge_color='darkgoldenrod',
                     edge_width=4.0)
```

### Example 2: Transparent Wells
```python
style.set_layer_style('nwell', color='lightgreen', alpha=0.3)
style.set_layer_style('pwell', color='lightcoral', alpha=0.3)
```

### Example 3: Circular Contacts
```python
style.set_layer_style('contact',
                     color='gray',
                     shape='circle',
                     edge_color='black',
                     edge_width=1.5)
```

### Example 4: Rounded Metal Stack
```python
for i in range(1, 5):
    style.set_layer_style(f'metal{i}',
                         shape='rounded',
                         edge_width=2.5)
```

### Example 5: Custom Container
```python
style.set_container_style(
    edge_color='navy',
    edge_width=3.0,
    linestyle='--',
    shape='rounded'
)
```

## Complete Theme Example

```python
from layout_automation.style_config import get_style_config, reset_style_config

def my_custom_theme():
    style = get_style_config()

    # Metals - rounded with thick borders
    style.set_layer_style('metal1', color='steelblue', edge_color='navy',
                         edge_width=3.0, shape='rounded')
    style.set_layer_style('metal2', color='firebrick', edge_color='darkred',
                         edge_width=3.0, shape='rounded')

    # Poly - ellipse
    style.set_layer_style('poly', color='mediumpurple', edge_color='indigo',
                         edge_width=2.5, shape='ellipse')

    # Contacts - circles
    style.set_layer_style('contact', color='gray', edge_color='black',
                         edge_width=1.5, shape='circle')

    # Containers
    style.set_container_style(edge_color='darkslategray', edge_width=2.0,
                             linestyle='--', shape='rounded')

# Apply theme
my_custom_theme()

# ... create and draw layout ...

# Reset when done
reset_style_config()
```

## Tips

✓ Set styles BEFORE calling `cell.draw()`
✓ Use `reset_style_config()` to start fresh
✓ Use same shape for similar layers (e.g., all metals rounded)
✓ Ensure good contrast between fill and edge colors
✓ Use transparency (alpha) to show overlapping layers
✓ Create theme functions for reusable styles

## See Full Documentation

See `STYLE_CUSTOMIZATION_GUIDE.md` for complete details and examples.
