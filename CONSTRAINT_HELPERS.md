
# Constraint Helper Functions

Making constraint-based layout automation more readable and less error-prone.

## Why Constraint Helpers?

**Problem**: Raw constraint strings are hard to read and error-prone:
```python
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)  # What does this do?
```

**Solution**: Use readable helper functions:
```python
parent.constrain(child, *center(parent))  # Clear intent!
```

## Quick Start

```python
from layout_automation.cell import Cell
from layout_automation.constraints import *

# Create cells
parent = Cell('parent')
child = Cell('child', 'metal1')
parent.add_instance(child)

# Center child in parent
parent.constrain(child, *center(parent))
parent.constrain(child, size(30, 20))

# Solve
parent.solver()
```

## Complete Reference

### Center Constraints

```python
from layout_automation.constraints import center, center_x, center_y

# Center in both X and Y
parent.constrain(child, *center(parent))

# Center horizontally only
parent.constrain(child, *center_x(parent))

# Center vertically only
parent.constrain(child, *center_y(parent))
```

**Equivalent raw constraints:**
- `center(ref)` → `'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', ref`
- `center_x(ref)` → `'sx1+sx2=ox1+ox2', ref`
- `center_y(ref)` → `'sy1+sy2=oy1+oy2', ref`

### Alignment Constraints

```python
from layout_automation.constraints import (
    align_left, align_right, align_top, align_bottom,
    align_center_x, align_center_y
)

# Align edges
parent.constrain(child2, *align_left(child1))
parent.constrain(child2, *align_right(child1))
parent.constrain(child2, *align_top(child1))
parent.constrain(child2, *align_bottom(child1))

# Align centers
parent.constrain(child2, *align_center_x(child1))  # Horizontal centers
parent.constrain(child2, *align_center_y(child1))  # Vertical centers
```

**Equivalent raw constraints:**
- `align_left(ref)` → `'sx1=ox1', ref`
- `align_right(ref)` → `'sx2=ox2', ref`
- `align_top(ref)` → `'sy2=oy2', ref`
- `align_bottom(ref)` → `'sy1=oy1', ref`
- `align_center_x(ref)` → `'sx1+sx2=ox1+ox2', ref`
- `align_center_y(ref)` → `'sy1+sy2=oy1+oy2', ref`

### Spacing Constraints

```python
from layout_automation.constraints import spacing, spacing_h, spacing_v

# General spacing with direction
parent.constrain(child2, *spacing(child1, 10, 'right'))   # 10 units right
parent.constrain(child2, *spacing(child1, 10, 'left'))    # 10 units left
parent.constrain(child2, *spacing(child1, 10, 'above'))   # 10 units above
parent.constrain(child2, *spacing(child1, 10, 'below'))   # 10 units below

# Horizontal spacing (to the right)
parent.constrain(child2, *spacing_h(child1, 10))

# Vertical spacing (upward)
parent.constrain(child2, *spacing_v(child1, 10))
```

**Equivalent raw constraints:**
- `spacing(ref, 10, 'right')` → `'sx1=ox2+10', ref`
- `spacing(ref, 10, 'above')` → `'sy1=oy2+10', ref`
- `spacing_h(ref, 10)` → `'sx1=ox2+10', ref`
- `spacing_v(ref, 10)` → `'sy1=oy2+10', ref`

### Size Constraints

```python
from layout_automation.constraints import (
    same_width, same_height, same_size,
    width, height, size
)

# Match reference cell size
parent.constrain(child2, *same_width(child1))
parent.constrain(child2, *same_height(child1))
parent.constrain(child2, *same_size(child1))

# Set fixed size (self-constraints)
cell.constrain(width(100))        # Set width = 100
cell.constrain(height(50))        # Set height = 50
cell.constrain(size(100, 50))     # Set width=100, height=50
```

**Equivalent raw constraints:**
- `same_width(ref)` → `'sx2-sx1=ox2-ox1', ref`
- `same_height(ref)` → `'sy2-sy1=oy2-oy1', ref`
- `same_size(ref)` → `'sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', ref`
- `width(100)` → `'x2-x1=100'` (self-constraint)
- `height(50)` → `'y2-y1=50'` (self-constraint)
- `size(100, 50)` → `'x2-x1=100, y2-y1=50'` (self-constraint)

### Position Constraints

```python
from layout_automation.constraints import at, bbox

# Position at coordinates (with optional size)
parent.constrain(child, at(10, 20))              # Position only: x1=10, y1=20
parent.constrain(child, at(10, 20, 50, 30))      # Position + size: x1=10, y1=20, x2=60, y2=50

# Set bounding box explicitly
parent.constrain(child, bbox(10, 20, 60, 50))    # x1=10, y1=20, x2=60, y2=50
```

**Equivalent raw constraints:**
- `at(10, 20)` → `'x1=10, y1=20'`
- `at(10, 20, 50, 30)` → `'x1=10, y1=20, x2=60, y2=50'`
- `bbox(10, 20, 60, 50)` → `'x1=10, y1=20, x2=60, y2=50'`

### Compound Constraints

These combine spacing and alignment in one call:

```python
from layout_automation.constraints import beside, above, below

# Place beside (to the right) with alignment
parent.constrain(child2, *beside(child1, spacing_val=10, align='bottom'))
parent.constrain(child2, *beside(child1, spacing_val=10, align='top'))
parent.constrain(child2, *beside(child1, spacing_val=10, align='center'))

# Place above with alignment
parent.constrain(child2, *above(child1, spacing_val=10, align='left'))
parent.constrain(child2, *above(child1, spacing_val=10, align='right'))
parent.constrain(child2, *above(child1, spacing_val=10, align='center'))

# Place below with alignment
parent.constrain(child2, *below(child1, spacing_val=10, align='left'))
parent.constrain(child2, *below(child1, spacing_val=10, align='right'))
parent.constrain(child2, *below(child1, spacing_val=10, align='center'))
```

**Equivalent raw constraints:**
- `beside(ref, 10, 'center')` → `'sx1=ox2+10, sy1+sy2=oy1+oy2', ref`
- `above(ref, 10, 'center')` → `'sy1=oy2+10, sx1+sx2=ox1+ox2', ref`
- `below(ref, 10, 'center')` → `'sy2=oy1-10, sx1+sx2=ox1+ox2', ref`

## Complete Example

```python
from layout_automation.cell import Cell
from layout_automation.constraints import *

# Create a simple inverter-like layout
layout = Cell('INVERTER')

# Components
nmos = Cell('nmos_region', 'diff')
pmos = Cell('pmos_region', 'diff')
gate = Cell('gate', 'poly')
vdd = Cell('power_rail', 'metal1')
gnd = Cell('ground_rail', 'metal1')

layout.add_instance([nmos, pmos, gate, vdd, gnd])

# Ground rail at bottom
layout.constrain(gnd, at(0, 0, 100, 10))

# NMOS above ground
layout.constrain(nmos, *above(gnd, spacing_val=5, align='center'))
layout.constrain(nmos, size(40, 30))

# PMOS above NMOS
layout.constrain(pmos, *above(nmos, spacing_val=10, align='center'))
layout.constrain(pmos, *same_size(nmos))

# VDD above PMOS
layout.constrain(vdd, *above(pmos, spacing_val=5, align='center'))
layout.constrain(vdd, *same_width(gnd))
layout.constrain(vdd, *same_height(gnd))

# Gate crosses both NMOS and PMOS
layout.constrain(gate, *center_x(layout))
layout.constrain(gate, size(8, 100))
layout.constrain(gate, at(0, 0))  # Start from bottom

# Solve and export
layout.solver()
layout.export_gds('inverter.gds')
```

## Print Reference Table

```python
from layout_automation.constraints import print_reference

# Display complete reference table
print_reference()
```

This prints a comprehensive table showing all available helpers, their usage, and equivalent raw constraints.

## Benefits

### 1. Readability
**Before:**
```python
parent.constrain(child, 'sx1=ox2+10, sy1=oy1', ref)
```

**After:**
```python
parent.constrain(child, *beside(ref, spacing_val=10, align='bottom'))
```

### 2. Less Error-Prone
- No manual string formatting
- Type checking for parameters
- Clear parameter names

### 3. Self-Documenting
- Function names describe intent
- IDE autocomplete support
- Built-in documentation

### 4. Easier Maintenance
- Centralized constraint logic
- Easy to update or extend
- Consistent behavior

## Combining Constraints

Multiple constraints can be applied to the same cell:

```python
# Place child2 beside child1 and match its height
parent.constrain(child2, *beside(child1, 10, 'center'))
parent.constrain(child2, *same_height(child1))

# Align left edge and set fixed width
parent.constrain(child2, *align_left(child1))
parent.constrain(child2, width(50))

# Center and set size
parent.constrain(child, *center(parent))
parent.constrain(child, size(30, 20))
```

## Important Notes

### The `*` Operator

Most helpers return a tuple `(constraint_string, ref_cell)`, so use the `*` operator to unpack:

```python
# Correct - using * to unpack
parent.constrain(child, *center(parent))

# Incorrect - without *
parent.constrain(child, center(parent))  # This won't work!
```

### Self-Constraints

Some helpers (like `width()`, `height()`, `size()`) return just a string for self-constraints:

```python
# These don't need * because they return a string, not a tuple
cell.constrain(width(100))
cell.constrain(size(100, 50))
cell.constrain(at(10, 20, 100, 50))
```

## Migration Guide

### Old Code
```python
# Hard to read constraint strings
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)
parent.constrain(child2, 'sx1=ox2+10, sy1=oy1', child1)
parent.constrain(child3, 'sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', child1)
parent.constrain(child, 'x1=10, y1=20, x2=110, y2=70')
```

### New Code
```python
from layout_automation.constraints import *

# Readable constraint helpers
parent.constrain(child, *center(parent))
parent.constrain(child2, *beside(child1, 10, 'bottom'))
parent.constrain(child3, *same_size(child1))
parent.constrain(child, at(10, 20, 100, 50))
```

## Advanced Usage

### Custom Combinations

You can still use raw constraints when needed:

```python
# Use helpers for common patterns
parent.constrain(child, *center_x(parent))

# Use raw constraints for custom logic
parent.constrain(child, 'sy1=oy2-5, y2-y1>=20', ref)
```

### Building Custom Helpers

You can create your own helpers:

```python
def my_custom_layout(ref_cell, offset):
    """Custom constraint pattern"""
    constraint = f'sx1=ox2+{offset}, sy1=oy2+{offset}, sx2-sx1=ox2-ox1'
    return (constraint, ref_cell)

# Use it
parent.constrain(child, *my_custom_layout(ref, 5))
```

## Testing

Run the test suite to see all helpers in action:

```bash
python examples/test_constraint_helpers.py
```

This will:
1. Display the complete reference table
2. Run tests for each helper category
3. Generate example GDS files
4. Show readability comparisons

## Summary

Constraint helpers make layout automation code:
- ✅ More readable
- ✅ Less error-prone
- ✅ Self-documenting
- ✅ Easier to maintain
- ✅ More enjoyable to write!

Start using them in your designs today!
