# Layout Automation - Comprehensive User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [The Cell Class](#the-cell-class)
6. [Constraint System](#constraint-system)
7. [Layout Solving](#layout-solving)
8. [Visualization](#visualization)
9. [Freeze and Fix Mechanisms](#freeze-and-fix-mechanisms)
10. [Style Configuration](#style-configuration)
11. [Technology Files](#technology-files)
12. [Advanced Features](#advanced-features)
13. [Best Practices](#best-practices)
14. [Troubleshooting](#troubleshooting)
15. [API Reference](#api-reference)

---

## Introduction

**Layout Automation** is a constraint-based IC (Integrated Circuit) layout automation toolkit designed for hierarchical cell-based design. It enables engineers to define chip layouts using a Python-based constraint system that automatically positions and sizes circuit elements.

### Key Features

- **Constraint-Based Positioning**: Define spatial relationships using readable constraint keywords
- **Hierarchical Design**: Build complex layouts from nested cell structures
- **Automatic Solving**: Uses Google OR-Tools CP-SAT solver for optimal placement
- **Rich Visualization**: Matplotlib-based rendering with smart label sizing
- **IP Block Reusability**: Freeze and fix mechanisms for verified blocks
- **Technology Support**: Parse Cadence Virtuoso technology files and display rules
- **GDS Export**: Export layouts to GDS format for fabrication

### When to Use This Tool

- Designing hierarchical IC layouts programmatically
- Creating parameterized cell generators
- Automating repetitive layout tasks
- Building layout verification tools
- Educational purposes for understanding constraint-based design

---

## Installation

### Requirements

- **Python**: 3.11 or 3.12 (Python 3.13+ has OR-Tools compatibility issues)
- **Dependencies**:
  - `ortools` - Constraint programming solver
  - `matplotlib` - Visualization
  - `numpy` - Numerical operations

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd layout_automation

# Install dependencies (if requirements.txt exists)
pip install ortools matplotlib numpy

# Verify installation
python -c "from layout_automation.cell import Cell; print('Installation successful!')"
```

### Known Issues

- OR-Tools may segfault on Python 3.13+. Use Python 3.12 or earlier.
- If you encounter solver issues, ensure you have a compatible OR-Tools version.

---

## Quick Start

### Hello World Layout

```python
from layout_automation.cell import Cell

# Create a parent cell
parent = Cell('my_chip')

# Create two leaf cells with layer names
metal1 = Cell('metal1_rect', 'metal1')
metal2 = Cell('metal2_rect', 'metal2')

# Add children to parent
parent.add_instance([metal1, metal2])

# Define constraints
parent.constrain('width=100, height=50')  # Parent size
parent.constrain(metal1, 'swidth=20, sheight=10')  # Child sizes
parent.constrain(metal2, 'swidth=30, sheight=15')
parent.constrain(metal1, 'left, bottom', parent)  # Align to bottom-left
parent.constrain(metal2, 'right, top', parent)    # Align to top-right

# Solve the layout
parent.solver()

# Visualize the result
parent.draw(show_labels=True)

# Access results
print(f"Metal1 position: {metal1.pos_list}")  # [x1, y1, x2, y2]
print(f"Parent size: {parent.width} x {parent.height}")
```

---

## Core Concepts

### Cell Hierarchy

Layouts are organized as a tree of **Cell** objects:

- **Leaf Cells**: Have a `layer_name` (e.g., 'metal1', 'poly') and represent physical geometry
- **Container Cells**: Have `children` and organize the layout hierarchy
- **Parent-Child Relationship**: Cells can contain other cells, creating nested structures

```python
# Leaf cell (has layer)
metal = Cell('m1', 'metal1')

# Container cell (has children)
parent = Cell('parent')
parent.add_instance([metal])
```

### Position Representation

Every cell has a `pos_list` attribute: `[x1, y1, x2, y2]`

- `(x1, y1)`: Bottom-left corner
- `(x2, y2)`: Top-right corner
- Integer coordinates (constraint solver requirement)

### Coordinate System

```
(x2, y2) ──────┐
              │ │
              │ │
              │ │
└─────── (x1, y1)
```

---

## The Cell Class

### Creating Cells

```python
# Leaf cell with layer
leaf = Cell('my_rect', 'metal1')

# Container cell
container = Cell('my_container')

# With initial instances
child1 = Cell('c1', 'poly')
child2 = Cell('c2', 'metal2')
parent = Cell('parent', child1, child2)  # Add children directly
```

### Adding Instances

```python
parent = Cell('parent')
child1 = Cell('child1', 'metal1')
child2 = Cell('child2', 'metal2')

# Add single instance
parent.add_instance(child1)

# Add multiple instances
parent.add_instance([child2, child3])
```

### Accessing Children

```python
# By index
first_child = parent.children[0]

# By name (using child_dict)
child = parent.child_dict['child1']

# Iterate over all children
for child in parent.children:
    print(child.name)
```

### Position Properties

After solving, access cell positions and dimensions:

```python
parent.solver()

# Position coordinates
print(parent.x1, parent.y1)  # Bottom-left
print(parent.x2, parent.y2)  # Top-right

# Dimensions
print(parent.width, parent.height)

# Center coordinates
print(parent.cx, parent.cy)

# Bounding box
bbox = parent.get_bbox()  # Returns (x1, y1, x2, y2)
```

---

## Constraint System

### Overview

Constraints define spatial relationships between cells. The system supports:

1. **Self-constraints**: Define a cell's own properties
2. **Binary constraints**: Define relationships between two cells
3. **Keyword constraints**: Readable high-level patterns
4. **Raw constraints**: Low-level mathematical expressions

### Constraint Syntax

```python
# General form
parent.constrain(subject_cell, constraint_string, object_cell)

# Self-constraint (no object)
parent.constrain('width=100, height=50')

# Binary constraint
parent.constrain(child1, 'left, top', child2)
```

### Self-Constraints

Define properties of a single cell:

```python
cell = Cell('cell', 'metal1')

# Size constraints
cell.constrain('width=100')
cell.constrain('height=50')
cell.constrain('width=100, height=50')  # Multiple in one call

# Position constraints
cell.constrain('x1=0, y1=0')
cell.constrain('x2=100, y2=50')
```

### Constraint Keywords

High-level readable patterns that expand to mathematical expressions.

#### Centering Keywords

```python
# Center on both axes
parent.constrain(child, 'center', parent)

# Center horizontally only
parent.constrain(child, 'xcenter', parent)

# Center vertically only
parent.constrain(child, 'ycenter', parent)
```

#### Alignment Keywords

```python
# Horizontal alignment
parent.constrain(child, 'left', parent)   # child.x1 = parent.x1
parent.constrain(child, 'right', parent)  # child.x2 = parent.x2

# Vertical alignment
parent.constrain(child, 'top', parent)    # child.y2 = parent.y2
parent.constrain(child, 'bottom', parent) # child.y1 = parent.y1

# Combined alignment
parent.constrain(child, 'left, bottom', parent)  # Align to bottom-left corner
parent.constrain(child, 'right, top', parent)    # Align to top-right corner
```

#### Edge Distance Keywords

Define spacing between cell edges:

```python
# Horizontal edge distances
parent.constrain(cell1, 'll_edge=10', cell2)  # Left-to-left spacing
parent.constrain(cell1, 'lr_edge=10', cell2)  # Left-to-right spacing
parent.constrain(cell1, 'rl_edge=10', cell2)  # Right-to-left spacing
parent.constrain(cell1, 'rr_edge=10', cell2)  # Right-to-right spacing

# Vertical edge distances
parent.constrain(cell1, 'bb_edge=10', cell2)  # Bottom-to-bottom spacing
parent.constrain(cell1, 'bt_edge=10', cell2)  # Bottom-to-top spacing
parent.constrain(cell1, 'tb_edge=10', cell2)  # Top-to-bottom spacing
parent.constrain(cell1, 'tt_edge=10', cell2)  # Top-to-top spacing
```

**Edge Keyword Reference:**

| Keyword | Expands To | Meaning |
|---------|-----------|---------|
| `ll_edge=N` | `ox1 - sx1 = N` | Distance from subject's left to object's left |
| `lr_edge=N` | `ox2 - sx1 = N` | Distance from subject's left to object's right |
| `rl_edge=N` | `ox1 - sx2 = N` | Distance from subject's right to object's left |
| `rr_edge=N` | `ox2 - sx2 = N` | Distance from subject's right to object's right |
| `bb_edge=N` | `oy1 - sy1 = N` | Distance from subject's bottom to object's bottom |
| `bt_edge=N` | `oy2 - sy1 = N` | Distance from subject's bottom to object's top |
| `tb_edge=N` | `oy1 - sy2 = N` | Distance from subject's top to object's bottom |
| `tt_edge=N` | `oy2 - sy2 = N` | Distance from subject's top to object's top |

#### Sizing Keywords

```python
# Subject cell sizing (with 's' prefix)
parent.constrain(child, 'swidth=20', parent)   # child.width = 20
parent.constrain(child, 'sheight=10', parent)  # child.height = 10

# Object cell sizing (with 'o' prefix)
parent.constrain(child, 'owidth=100', parent)  # parent.width = 100
parent.constrain(child, 'oheight=50', parent)  # parent.height = 50

# Absolute sizing (when used as self-constraint)
cell.constrain('width=20, height=10')
```

### Raw Constraint Expressions

For fine-grained control, use mathematical expressions directly:

```python
# Variable prefixes:
# s = subject cell (first argument)
# o = object cell (second argument)
# x = absolute (for self-constraints)

# Examples
parent.constrain(child1, 'sx2 + 10 = ox1', child2)  # 10-unit spacing
parent.constrain(child, 'sx1 + sx2 = ox1 + ox2', parent)  # Horizontal centering
parent.constrain(child, 'sx2 - sx1 = 20', parent)  # Width = 20

# Inequalities
parent.constrain(child, 'sx1 >= 0')  # Minimum position
parent.constrain(child, 'sx2 <= ox2', parent)  # Stay within bounds
```

### Multiple Constraints

```python
# Multiple constraints in one call (comma-separated)
parent.constrain(child, 'swidth=20, sheight=10, left, bottom', parent)

# Or separate calls
parent.constrain(child, 'swidth=20', parent)
parent.constrain(child, 'sheight=10', parent)
parent.constrain(child, 'left, bottom', parent)
```

### Common Constraint Patterns

#### Fixed-Size Cell at Corner

```python
parent.constrain('width=100, height=50')
parent.constrain(child, 'swidth=10, sheight=10, left, bottom', parent)
```

#### Two Cells Side-by-Side with Spacing

```python
parent.constrain(left_cell, 'rl_edge=5', right_cell)  # 5-unit spacing
parent.constrain(left_cell, 'ycenter', right_cell)    # Vertically aligned
```

#### Grid Layout

```python
# 2x2 grid
parent.constrain(cell_tl, 'left, top', parent)
parent.constrain(cell_tr, 'right, top', parent)
parent.constrain(cell_bl, 'left, bottom', parent)
parent.constrain(cell_br, 'right, bottom', parent)
parent.constrain(cell_tl, 'rl_edge=10', cell_tr)  # Horizontal spacing
parent.constrain(cell_tl, 'tb_edge=10', cell_bl)  # Vertical spacing
```

---

## Layout Solving

### The Solver

The `solver()` method uses Google OR-Tools CP-SAT (Constraint Programming - Satisfiability) solver:

```python
parent.solver()
```

### How It Works

1. **Variable Creation**: Each cell gets integer variables for x1, y1, x2, y2
2. **Constraint Translation**: Keywords and expressions → linear constraints
3. **Hierarchy Traversal**: Recursively processes parent-child relationships
4. **Objective Minimization**: Minimizes layout size + centering deviation
5. **Solution Extraction**: Updates `pos_list` for all cells

### Solver Options

```python
# Solve with default settings
parent.solver()

# The solver automatically:
# - Creates variables for all cells in hierarchy
# - Adds all constraints recursively
# - Minimizes total layout area
# - Updates pos_list on success
```

### Checking Solver Status

```python
status = parent.solver()

# Status values (from OR-Tools):
# OPTIMAL (4) - Solution found
# FEASIBLE (2) - Solution found (may not be optimal)
# INFEASIBLE (3) - No solution exists
# UNKNOWN (0) - Solver didn't complete

if status == 4:
    print("Layout solved successfully!")
    print(f"Final size: {parent.width} x {parent.height}")
else:
    print(f"Solver status: {status}")
```

### Handling Infeasible Constraints

If constraints are contradictory, the solver returns INFEASIBLE:

```python
cell.constrain('width=100')
cell.constrain('width=50')  # Contradiction!
status = cell.solver()  # Will be INFEASIBLE
```

**Debugging Tips:**

1. Start with minimal constraints
2. Add constraints incrementally
3. Use inequalities instead of equalities when appropriate
4. Check for typos in constraint keywords

---

## Visualization

### Basic Drawing

```python
# Solve and draw
parent.solver()
parent.draw()

# Solve and draw in one call
parent.draw(solve_first=True)
```

### Label Options

The system supports smart label sizing that adapts to cell dimensions:

```python
# Show labels with automatic sizing
parent.draw(show_labels=True, label_mode='auto')

# Label modes:
# 'none' - No labels
# 'abbr' - Abbreviated (e.g., "m1" for "metal1_rect")
# 'full' - Full cell name
# 'extended' - Full name with dimensions (e.g., "metal1_rect (20x10)")
# 'auto' - Smart mode that chooses based on cell size

parent.draw(show_labels=True, label_mode='extended')
```

### Label Positioning

Position labels to avoid overlapping with cell content:

```python
# Label position options:
# 'center' - Center of cell (default)
# 'top-left' - Top-left corner
# 'top-right' - Top-right corner
# 'bottom-left' - Bottom-left corner
# 'bottom-right' - Bottom-right corner

parent.draw(
    show_labels=True,
    label_position='top-left'  # Avoid overlap with centered content
)
```

### Customizing Visualization

```python
import matplotlib.pyplot as plt

# Draw and customize
fig, ax = parent.draw(solve_first=True, show_labels=True)

# Further customization
ax.set_title('My IC Layout')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('layout.png', dpi=300)
plt.show()
```

---

## Freeze and Fix Mechanisms

These mechanisms enable IP block reusability and hierarchical design patterns.

### Freeze Layout

**Purpose**: Treat a cell as an immutable black-box IP block.

```python
# Create and solve a block
block = Cell('my_ip_block')
# ... add children and constraints ...
block.solver()

# Freeze it
block.freeze_layout()

# Now it's immutable:
# - Cannot add new children
# - Cannot add new constraints
# - Size is locked
# - Can be reused in multiple parents
```

**Use Cases:**
- Verified IP blocks that shouldn't change
- Standard cells in a library
- Blocks from external sources

**Characteristics:**
- `_frozen = True`
- Size becomes fixed constraint
- Internal structure is hidden from parent solver
- Can be copied for reuse

### Fix Layout

**Purpose**: Allow repositioning while preserving internal structure.

```python
# Create and solve a block
block = Cell('my_block')
# ... add children and constraints ...
block.solver()

# Fix it
block.fix_layout()

# Now it can be repositioned, and internal cells update automatically
parent = Cell('parent')
parent.add_instance(block)
parent.constrain(block, 'center', parent)
parent.solver()  # Block and its children reposition together
```

**Use Cases:**
- Hierarchical layouts where sub-blocks move together
- Parameterized blocks that maintain internal relationships
- Multi-instance reuse with different positions

**Characteristics:**
- `_fixed = True`
- Internal cells track offsets from parent
- Parent repositioning updates all children
- More flexible than freeze

### Freeze vs. Fix Comparison

| Feature | Freeze | Fix |
|---------|--------|-----|
| Immutable | Yes | Yes (internal structure) |
| Can Reposition | Yes (as a whole) | Yes (with internal updates) |
| Internal Constraints | Hidden | Preserved |
| Solver Complexity | Low (single fixed size) | Medium (offsets tracked) |
| Use Case | Black-box IP | Hierarchical sub-blocks |

### Copying Frozen/Fixed Cells

```python
# Freeze a block
original = Cell('block')
original.solver()
original.freeze_layout()

# Create multiple copies with auto-naming
copy1 = original.copy()  # Name: 'block_c1'
copy2 = original.copy()  # Name: 'block_c2'
copy3 = original.copy('custom_name')  # Name: 'custom_name'

# Use in different locations
parent.add_instance([copy1, copy2, copy3])
parent.constrain(copy1, 'left, bottom', parent)
parent.constrain(copy2, 'center', parent)
parent.constrain(copy3, 'right, top', parent)
parent.solver()
```

---

## Style Configuration

### Overview

The style system controls how layers appear in visualizations:

- Colors and transparency
- Line styles and widths
- Z-order (drawing order)
- Edge colors

### Using StyleConfig

```python
from layout_automation.style_config import get_style_config

# Get the global style configuration
style = get_style_config()

# Set style for a layer
style.set_layer_style(
    'metal1',
    color='blue',           # Fill color
    alpha=0.6,              # Transparency (0-1)
    edge_color='darkblue',  # Border color
    line_style='--',        # Line style: '-', '--', '-.', ':'
    line_width=1.5,         # Line width in points
    zorder=3                # Drawing order (higher = on top)
)

# Set container style (for cells with children)
style.set_container_style(
    line_style='--',
    line_width=2.0,
    edge_color='black',
    zorder=1
)
```

### Line Styles

Available line styles:
- `'-'` - Solid line
- `'--'` - Dashed line
- `'-.'` - Dash-dot line
- `':'` - Dotted line

### Z-Order

Controls drawing order (layers stack):

```python
# Lower z-order drawn first (bottom)
style.set_layer_style('substrate', zorder=1)
style.set_layer_style('poly', zorder=2)
style.set_layer_style('metal1', zorder=3)
style.set_layer_style('metal2', zorder=4)  # On top
```

### Complete Example

```python
from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config

# Configure styles
style = get_style_config()
style.set_layer_style('metal1', color='blue', alpha=0.5, zorder=2)
style.set_layer_style('metal2', color='red', alpha=0.5, zorder=3)
style.set_layer_style('poly', color='green', alpha=0.5, zorder=1)

# Create layout
parent = Cell('parent')
m1 = Cell('m1', 'metal1')
m2 = Cell('m2', 'metal2')
poly = Cell('poly', 'poly')

parent.add_instance([poly, m1, m2])  # poly drawn first due to lower zorder
# ... add constraints ...
parent.draw(solve_first=True)
```

---

## Technology Files

### Overview

Technology files map layer names to GDS layer numbers and provide display colors.

### Supported Formats

- **Cadence Virtuoso Technology Files** (`.tf`)
- **Display Rules Files** (`.drf`)

### Using Technology Files

```python
from layout_automation.tech_file import TechFile

# Load technology file
tech = TechFile('FreePDK45.tf')

# Optionally load display rules
tech.load_display_file('SantanaDisplay.drf')

# Get layer mapping
layer_number = tech.get_layer_number('metal1')  # e.g., 10
color = tech.get_layer_color('metal1')          # e.g., 'blue'

# Apply technology colors to visualization
tech.apply_tech_colors_to_style()  # Updates global StyleConfig
```

### Technology File Format

Example `.tf` file structure:
```
metal1 {
    layerNumber = 10
    color = "blue"
}

metal2 {
    layerNumber = 11
    color = "red"
}
```

### Display Rules File Format

Example `.drf` file structure:
```
drDefineDisplay(
    metal1
    blue
    solid
)

drDefineDisplay(
    metal2
    red
    solid
)
```

---

## Advanced Features

### Centering with Tolerance

For soft centering constraints that minimize deviation:

```python
from layout_automation.centering_with_tolerance import add_centering_with_tolerance

parent = Cell('parent')
child = Cell('child', 'metal1')
parent.add_instance(child)

# Exact centering (hard constraint)
parent.center_with_tolerance(child, tolerance=0)

# Soft centering (allows deviation up to tolerance)
centering = add_centering_with_tolerance(
    parent_cell=parent,
    subject_cell=child,
    object_cell=parent,
    tolerance_x=5,  # Allow ±5 units horizontal deviation
    tolerance_y=5,  # Allow ±5 units vertical deviation
    weight_x=1.0,   # Weight in objective function
    weight_y=1.0
)

parent.solver()
```

**Use Cases:**
- Soft alignment when exact centering is over-constrained
- Bias-free centering in complex layouts
- Minimizing centering deviation in objective function

### Deep Copying

Create independent copies of cell hierarchies:

```python
original = Cell('original')
# ... build layout ...

# Deep copy with automatic naming
copy1 = original.copy()  # Name: 'original_c1'
copy2 = original.copy()  # Name: 'original_c2'

# Deep copy with custom name
custom = original.copy('custom_name')

# All children are copied recursively
# Child names get _c{N} suffix as well
```

### Bounding Box Calculation

Get the bounding box of a cell and all its children:

```python
parent.solver()

# Get bounding box
x1, y1, x2, y2 = parent.get_bbox()

print(f"Bounding box: ({x1}, {y1}) to ({x2}, {y2})")
print(f"Area: {(x2 - x1) * (y2 - y1)}")
```

### Accessing Solver Variables (Advanced)

For debugging or advanced use:

```python
# After solving, cells have solver variables
if hasattr(parent, '_x1_var'):
    print(f"X1 variable: {parent._x1_var}")
```

### Constraint Helpers

```python
from layout_automation.constraint_helpers import (
    align_left,
    align_right,
    align_center,
    stack_horizontal,
    stack_vertical
)

# Helper functions for common patterns
align_left(parent, [child1, child2, child3])  # Align all to left edge
stack_horizontal(parent, [child1, child2, child3], spacing=10)  # Horizontal row
```

---

## Best Practices

### 1. Start Simple, Add Complexity Gradually

```python
# Good: Build incrementally
parent = Cell('parent')
child = Cell('child', 'metal1')
parent.add_instance(child)
parent.constrain('width=100, height=50')
parent.constrain(child, 'swidth=20, sheight=10')
parent.solver()  # Test early

# Then add more constraints
parent.constrain(child, 'center', parent)
parent.solver()  # Test again
```

### 2. Use Meaningful Names

```python
# Good
vdd_rail = Cell('vdd_rail', 'metal1')
gnd_rail = Cell('gnd_rail', 'metal1')

# Bad
cell1 = Cell('c1', 'metal1')
cell2 = Cell('c2', 'metal1')
```

### 3. Freeze Verified Blocks

```python
# Once a block is verified, freeze it
standard_cell = Cell('nand2')
# ... build and verify ...
standard_cell.solver()
standard_cell.freeze_layout()

# Now it's immutable and safe to reuse
```

### 4. Use Keywords Over Raw Expressions

```python
# Good: Readable
parent.constrain(child, 'center', parent)
parent.constrain(child1, 'rl_edge=10', child2)

# Bad: Hard to read
parent.constrain(child, 'sx1 + sx2 = ox1 + ox2, sy1 + sy2 = oy1 + oy2', parent)
```

### 5. Test Solver Status

```python
status = parent.solver()
if status != 4:  # Not OPTIMAL
    print(f"Warning: Solver status = {status}")
    # Debug or handle error
```

### 6. Visualize Early and Often

```python
# During development, visualize frequently
parent.draw(solve_first=True, show_labels=True)
# Helps catch errors early
```

### 7. Use Hierarchical Design

```python
# Good: Hierarchical
row1 = Cell('row1')
row2 = Cell('row2')
# ... populate rows ...
top = Cell('top')
top.add_instance([row1, row2])

# Better than: Everything flat in one cell
```

### 8. Document Complex Constraints

```python
# Add comments for non-obvious constraints
parent.constrain(child1, 'rl_edge=10', child2)  # Minimum spacing requirement
parent.constrain(child, 'sx2 <= ox2 - 5', parent)  # Keep 5 units from edge
```

---

## Troubleshooting

### Solver Returns INFEASIBLE

**Cause**: Contradictory or impossible constraints.

**Solutions:**
1. Check for conflicting size constraints
2. Verify edge spacing doesn't exceed parent size
3. Comment out constraints one-by-one to find the culprit
4. Use inequalities (`<=`, `>=`) instead of equality when appropriate

```python
# May be infeasible if children are too large
parent.constrain('width=100')
parent.constrain(child1, 'swidth=80', parent)
parent.constrain(child2, 'swidth=80', parent)
parent.constrain(child1, 'rl_edge=10', child2)  # 80+10+80=170 > 100!
```

### Labels Not Showing

**Cause**: `show_labels` not set or label mode is 'none'.

**Solution:**
```python
parent.draw(show_labels=True, label_mode='auto')
```

### Cells Overlapping Unexpectedly

**Cause**: Missing constraints to prevent overlap.

**Solution:** Add spacing or non-overlap constraints:
```python
# Ensure spacing
parent.constrain(child1, 'rl_edge=0', child2)  # No gap, but no overlap

# Or explicit non-overlap
parent.constrain(child1, 'sx2 <= ox1', child2)  # child1 left of child2
```

### OR-Tools Segfault (Python 3.13+)

**Cause**: OR-Tools compatibility issue with Python 3.13+.

**Solution:** Use Python 3.12 or earlier:
```bash
pyenv install 3.12.0
pyenv local 3.12.0
```

### Styles Not Applied

**Cause**: Styles set after drawing, or layer name mismatch.

**Solution:**
```python
from layout_automation.style_config import get_style_config

# Set styles BEFORE drawing
style = get_style_config()
style.set_layer_style('metal1', color='blue')

# Ensure layer name matches exactly
cell = Cell('cell', 'metal1')  # Name must match style
```

### Child Not Found in child_dict

**Cause**: Child not added via `add_instance()`, or name mismatch.

**Solution:**
```python
# Ensure child is added
parent.add_instance(child)

# Check child exists
if 'child_name' in parent.child_dict:
    child = parent.child_dict['child_name']
else:
    print("Child not found!")
```

---

## API Reference

### Cell Class

#### Constructor

```python
Cell(name: str, *args: Union[str, Cell])
```

- `name`: Cell instance name
- `*args`: Optional layer name (str) or child cells (Cell)

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Cell instance name |
| `children` | List[Cell] | List of child cells |
| `child_dict` | Dict[str, Cell] | Name-to-cell mapping |
| `pos_list` | List[int] | Position [x1, y1, x2, y2] |
| `constraints` | List[Tuple] | List of constraint specifications |
| `is_leaf` | bool | True if cell has layer_name |
| `layer_name` | str | Layer name (e.g., 'metal1') |
| `x1`, `y1` | int | Bottom-left corner |
| `x2`, `y2` | int | Top-right corner |
| `cx`, `cy` | float | Center coordinates |
| `width`, `height` | int | Dimensions |

#### Methods

##### add_instance()

```python
add_instance(instances: Union[Cell, List[Cell]]) -> None
```

Add child cell(s) to this cell.

##### constrain()

```python
constrain(*args) -> None
```

Add constraint(s). Supports:
- `constrain('width=100')` - Self-constraint
- `constrain(cell1, 'center', cell2)` - Binary constraint

##### solver()

```python
solver() -> int
```

Solve layout using OR-Tools. Returns solver status:
- 4: OPTIMAL
- 2: FEASIBLE
- 3: INFEASIBLE
- 0: UNKNOWN

##### draw()

```python
draw(
    solve_first: bool = False,
    show_labels: bool = False,
    label_mode: str = 'auto',
    label_position: str = 'center'
) -> Tuple[Figure, Axes]
```

Visualize layout with matplotlib.

##### copy()

```python
copy(new_name: str = None) -> Cell
```

Deep copy of cell with automatic naming (_c{N} suffix).

##### get_bbox()

```python
get_bbox() -> Tuple[int, int, int, int]
```

Get bounding box: (x1, y1, x2, y2).

##### freeze_layout()

```python
freeze_layout() -> None
```

Freeze cell as immutable IP block.

##### fix_layout()

```python
fix_layout() -> None
```

Fix internal structure while allowing repositioning.

##### center_with_tolerance()

```python
center_with_tolerance(
    child: Cell,
    tolerance: int = 0,
    tolerance_x: int = None,
    tolerance_y: int = None
) -> None
```

Add centering constraint with tolerance.

---

### StyleConfig Class

#### get_style_config()

```python
from layout_automation.style_config import get_style_config
style = get_style_config()
```

Get global style configuration singleton.

#### set_layer_style()

```python
style.set_layer_style(
    layer_name: str,
    color: str = None,
    alpha: float = None,
    edge_color: str = None,
    line_style: str = None,
    line_width: float = None,
    zorder: int = None
) -> None
```

Set style for a layer.

#### set_container_style()

```python
style.set_container_style(
    line_style: str = None,
    line_width: float = None,
    edge_color: str = None,
    zorder: int = None
) -> None
```

Set style for container cells.

---

### TechFile Class

#### Constructor

```python
from layout_automation.tech_file import TechFile
tech = TechFile(tech_file_path: str)
```

Load technology file.

#### load_display_file()

```python
tech.load_display_file(drf_file_path: str) -> None
```

Load display rules file.

#### get_layer_number()

```python
tech.get_layer_number(layer_name: str) -> int
```

Get GDS layer number for layer name.

#### get_layer_color()

```python
tech.get_layer_color(layer_name: str) -> str
```

Get display color for layer name.

#### apply_tech_colors_to_style()

```python
tech.apply_tech_colors_to_style() -> None
```

Apply technology colors to global StyleConfig.

---

### Constraint Keywords Reference

#### Centering

| Keyword | Expands To |
|---------|-----------|
| `center` | `sx1 + sx2 = ox1 + ox2, sy1 + sy2 = oy1 + oy2` |
| `xcenter` | `sx1 + sx2 = ox1 + ox2` |
| `ycenter` | `sy1 + sy2 = oy1 + oy2` |

#### Alignment

| Keyword | Expands To |
|---------|-----------|
| `left` | `sx1 = ox1` |
| `right` | `sx2 = ox2` |
| `top` | `sy2 = oy2` |
| `bottom` | `sy1 = oy1` |

#### Edge Distances

| Keyword | Expands To | Meaning |
|---------|-----------|---------|
| `ll_edge=N` | `ox1 - sx1 = N` | Left-to-left spacing |
| `lr_edge=N` | `ox2 - sx1 = N` | Left-to-right distance |
| `rl_edge=N` | `ox1 - sx2 = N` | Right-to-left spacing |
| `rr_edge=N` | `ox2 - sx2 = N` | Right-to-right spacing |
| `bb_edge=N` | `oy1 - sy1 = N` | Bottom-to-bottom spacing |
| `bt_edge=N` | `oy2 - sy1 = N` | Bottom-to-top distance |
| `tb_edge=N` | `oy1 - sy2 = N` | Top-to-bottom spacing |
| `tt_edge=N` | `oy2 - sy2 = N` | Top-to-top spacing |

#### Sizing

| Keyword | Expands To |
|---------|-----------|
| `swidth=N` | `sx2 - sx1 = N` |
| `sheight=N` | `sy2 - sy1 = N` |
| `owidth=N` | `ox2 - ox1 = N` |
| `oheight=N` | `oy2 - oy1 = N` |
| `width=N` | `x2 - x1 = N` (self-constraint) |
| `height=N` | `y2 - y1 = N` (self-constraint) |

---

## Examples

### Example 1: Simple Two-Cell Layout

```python
from layout_automation.cell import Cell

parent = Cell('parent')
left = Cell('left', 'metal1')
right = Cell('right', 'metal2')

parent.add_instance([left, right])

# Define sizes and positions
parent.constrain('width=100, height=50')
parent.constrain(left, 'swidth=30, sheight=40', parent)
parent.constrain(right, 'swidth=30, sheight=40', parent)

# Position: left cell on left, right cell on right
parent.constrain(left, 'left, ycenter', parent)
parent.constrain(right, 'right, ycenter', parent)

# Solve and draw
parent.draw(solve_first=True, show_labels=True)
```

### Example 2: Centered Grid

```python
from layout_automation.cell import Cell

parent = Cell('parent')
cells = [Cell(f'cell_{i}', 'metal1') for i in range(4)]

parent.add_instance(cells)
parent.constrain('width=100, height=100')

# All cells same size
for cell in cells:
    parent.constrain(cell, 'swidth=20, sheight=20', parent)

# 2x2 grid
parent.constrain(cells[0], 'left, top', parent)
parent.constrain(cells[1], 'right, top', parent)
parent.constrain(cells[2], 'left, bottom', parent)
parent.constrain(cells[3], 'right, bottom', parent)

# Spacing
parent.constrain(cells[0], 'rl_edge=20', cells[1])
parent.constrain(cells[0], 'tb_edge=20', cells[2])

parent.draw(solve_first=True, show_labels=True, label_position='top-left')
```

### Example 3: Hierarchical Layout with Frozen Block

```python
from layout_automation.cell import Cell

# Create and freeze a reusable block
block = Cell('standard_block')
m1 = Cell('m1', 'metal1')
m2 = Cell('m2', 'metal2')
block.add_instance([m1, m2])
block.constrain('width=50, height=50')
block.constrain(m1, 'swidth=20, sheight=20, left, bottom', block)
block.constrain(m2, 'swidth=20, sheight=20, right, top', block)
block.solver()
block.freeze_layout()

# Use multiple copies
top = Cell('top')
copy1 = block.copy()
copy2 = block.copy()
copy3 = block.copy()

top.add_instance([copy1, copy2, copy3])
top.constrain('width=200, height=50')
top.constrain(copy1, 'left, ycenter', top)
top.constrain(copy2, 'center', top)
top.constrain(copy3, 'right, ycenter', top)

top.draw(solve_first=True, show_labels=True)
```

---

## Conclusion

This manual covers the essential features and usage patterns of the Layout Automation toolkit. For more examples, see the `examples/` directory. For implementation details, refer to the source code in `layout_automation/`.

### Further Resources

- **Example Files**: `/examples/` - 75+ demonstration scripts
- **Test Files**: `/tests/` - Comprehensive test coverage
- **Source Code**: `/layout_automation/` - Well-documented implementation
- **Technology Files**: `FreePDK45.tf`, `SantanaDisplay.drf` - Reference files

### Contributing

When extending the toolkit:
1. Follow existing code patterns
2. Add tests for new features
3. Update this manual with new functionality
4. Provide example scripts

### License

Refer to repository LICENSE file for terms and conditions.

---

**Last Updated**: 2025-10-21
**Version**: 1.0
**Author**: Layout Automation Team
