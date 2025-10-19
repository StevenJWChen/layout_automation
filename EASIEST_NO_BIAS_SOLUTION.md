# Easiest Way: Tolerance > 0 with True Centering (No Bias)

## What You Want

- Tolerance > 0 (allow deviation from perfect center)
- Child should be **centered** within that tolerance (no left/bottom bias)

## The Easiest Solution

Just **2 lines** instead of calling `parent.solver()`:

```python
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import center_and_solve

# Create layout
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# 2 LINES - center with tolerance (no bias)
from layout_automation.centering_with_tolerance import center_and_solve
center_and_solve(parent, child, tolerance=10)

# Done! Child is centered within ±10 units
print(f"Child: {child.pos_list}")
```

## Complete Example

```python
#!/usr/bin/env python3
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import center_and_solve

# Setup
parent = Cell('parent')
child = Cell('child', 'metal1')
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Center with ±10 tolerance (TRUE CENTERING, NO BIAS)
center_and_solve(parent, child, tolerance=10)

# Verify
parent_cx = (parent.pos_list[0] + parent.pos_list[2]) / 2
child_cx = (child.pos_list[0] + child.pos_list[2]) / 2
print(f"Parent center: {parent_cx}")
print(f"Child center: {child_cx}")
print(f"Offset: {abs(parent_cx - child_cx):.2f} units")
```

## API

```python
center_and_solve(
    parent,           # Parent cell
    child,            # Child to center
    tolerance=10,     # Tolerance (±10 units)
    ref_obj=None      # Reference (defaults to parent)
)
```

## Usage Examples

```python
# ±5 unit tolerance
center_and_solve(parent, child, tolerance=5)

# ±15 unit tolerance in X, ±10 in Y
center_and_solve(parent, child, tolerance_x=15, tolerance_y=10)

# Center child1 relative to child2
center_and_solve(parent, child1, tolerance=5, ref_obj=child2)

# Exact centering (tolerance=0)
center_and_solve(parent, child, tolerance=0)
```

## That's It!

This is the **simplest way** to get:
- Tolerance > 0
- True centering (no left/bottom bias)
- Just one function call

**No complex setup, no multiple steps, just works!**
