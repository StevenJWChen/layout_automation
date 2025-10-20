# Line Style and Z-Order Features

## Overview

The style configuration system now supports `line_style` and `zorder` properties for both layer styles and container styles, giving you fine control over edge appearance and drawing order.

## New Properties

### LayerStyle Properties

- **`line_style`** (str): Edge line style
  - Values: `'-'` (solid), `'--'` (dashed), `'-.'` (dashdot), `':'` (dotted)
  - Or: `'solid'`, `'dashed'`, `'dashdot'`, `'dotted'`
  - Default: `'-'` (solid)

- **`zorder`** (int): Drawing order
  - Higher values are drawn on top
  - Default: `1` for layers
  - Useful for controlling overlapping layers

### ContainerStyle Properties

- **`zorder`** (int): Drawing order
  - Higher values are drawn on top
  - Default: `0` (containers behind layers by default)

## Usage

### Setting Line Styles

```python
from layout_automation.style_config import get_style_config

style_config = get_style_config()

# Set different line styles for different layers
style_config.set_layer_style('metal1', line_style='-')    # Solid
style_config.set_layer_style('metal2', line_style='--')   # Dashed
style_config.set_layer_style('poly', line_style='-.')     # Dashdot
style_config.set_layer_style('diff', line_style=':')      # Dotted
```

### Setting Z-Order

```python
# Control drawing order - higher values on top
style_config.set_layer_style('nwell', zorder=0)      # Bottom
style_config.set_layer_style('poly', zorder=1)
style_config.set_layer_style('contact', zorder=2)
style_config.set_layer_style('metal1', zorder=3)     # Top
```

### Combined Usage

```python
# Set both properties together
style_config.set_layer_style(
    'metal1',
    color='blue',
    alpha=0.6,
    edge_color='darkblue',
    edge_width=2.0,
    line_style='-',   # Solid line
    zorder=3          # Draw on top
)
```

## Practical Examples

### Example 1: Layer Type Differentiation

Use line styles to visually distinguish different layer types:

```python
# Solid lines for metal layers
style_config.set_layer_style('metal1', line_style='-')
style_config.set_layer_style('metal2', line_style='-')

# Dashed lines for polysilicon
style_config.set_layer_style('poly', line_style='--')

# Dotted lines for wells (since they're background layers)
style_config.set_layer_style('nwell', line_style=':', alpha=0.3)
style_config.set_layer_style('pwell', line_style=':', alpha=0.3)
```

### Example 2: Physical Layer Stack

Use zorder to match the physical IC layer stack:

```python
# Bottom to top (actual IC fabrication order)
style_config.set_layer_style('substrate', zorder=0)
style_config.set_layer_style('nwell', zorder=0)
style_config.set_layer_style('pwell', zorder=0)
style_config.set_layer_style('diff', zorder=1)
style_config.set_layer_style('poly', zorder=1)
style_config.set_layer_style('contact', zorder=2)
style_config.set_layer_style('metal1', zorder=3)
style_config.set_layer_style('via1', zorder=4)
style_config.set_layer_style('metal2', zorder=5)
style_config.set_layer_style('via2', zorder=6)
style_config.set_layer_style('metal3', zorder=7)
```

### Example 3: Container Styling

Set container zorder to control hierarchy visualization:

```python
# Containers behind layers (default)
style_config.set_container_style(zorder=0)

# Or containers on top (to emphasize hierarchy)
style_config.set_container_style(zorder=10)
```

## Line Style Options

All matplotlib line styles are supported:

| Style String | Name | Appearance |
|-------------|------|------------|
| `'-'` or `'solid'` | Solid | ──────── |
| `'--'` or `'dashed'` | Dashed | ── ── ── |
| `'-.'` or `'dashdot'` | Dash-dot | ──·──·── |
| `':'` or `'dotted'` | Dotted | ········ |

## Z-Order Guidelines

**Recommended zorder values:**

- **0**: Background elements (wells, substrates, containers)
- **1**: Active device layers (poly, diffusion)
- **2**: Contacts
- **3+**: Metal layers (increasing by metal level)

**Benefits:**
- Correct visual layer stacking
- Matches physical IC structure
- Better visualization of layer relationships
- Prevents important layers from being hidden

## Complete Example

```python
from layout_automation import Cell
from layout_automation.style_config import get_style_config

# Configure styles
style_config = get_style_config()

# Set styles with line_style and zorder
style_config.set_layer_style(
    'nwell',
    color='lightgreen',
    alpha=0.3,
    line_style=':',      # Dotted (background)
    zorder=0             # Bottom layer
)

style_config.set_layer_style(
    'poly',
    color='red',
    alpha=0.6,
    line_style='--',     # Dashed
    zorder=1             # Above wells
)

style_config.set_layer_style(
    'metal1',
    color='blue',
    alpha=0.6,
    line_style='-',      # Solid
    zorder=3             # Top layer
)

# Create layout
transistor = Cell('transistor')
well = Cell('well', 'nwell')
gate = Cell('gate', 'poly')
metal = Cell('source', 'metal1')

transistor.constrain(well, 'x1=0, y1=0, x2=100, y2=80')
transistor.constrain(gate, 'x1=40, y1=10, x2=50, y2=70')
transistor.constrain(metal, 'x1=10, y1=20, x2=30, y2=60')

transistor.solver()
transistor.draw()  # Layers drawn in correct order with proper styles
```

## Benefits

1. **Visual Clarity**: Different line styles help distinguish layer types at a glance
2. **Realistic Rendering**: Z-order matches actual IC layer stack
3. **Better Diagrams**: Proper stacking for publications and documentation
4. **Customization**: Full control over appearance
5. **Standards Compliance**: Can match industry-standard layer visualization

## Backward Compatibility

These features are fully backward compatible:
- Default values maintain existing behavior
- Existing code works without modification
- Optional parameters in all methods
- No breaking changes to API

## See Also

- `test_line_style_zorder.py` - Comprehensive tests
- `example_line_style_zorder.py` - Practical examples with visualizations
- `style_config.py` - Implementation details
