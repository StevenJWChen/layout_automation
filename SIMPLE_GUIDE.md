# Simple Guide: Centering with Tolerance

## The Simplest Way (One Line!)

I've added a simple method to the Cell class. Just use this:

```python
from layout_automation.cell import Cell

parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# ONE LINE - center with tolerance
parent.center_with_tolerance(child, tolerance=10)

# Solve normally
parent.solver()
```

That's it!

## Usage

### Exact Centering (No Tolerance)

```python
parent.center_with_tolerance(child, tolerance=0)
parent.solver()
```

**Result:** Child is exactly centered. No bias.

### With Tolerance

```python
parent.center_with_tolerance(child, tolerance=10)
parent.solver()
```

**Result:** Child is within ±10 units of center.

**⚠️ WARNING:** May have left/bottom bias (solver minimizes coordinates)

## Complete Example

```python
#!/usr/bin/env python3
from layout_automation.cell import Cell

# Create layout
parent = Cell('parent')
child = Cell('child', 'metal1')

# Set sizes
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Center with ±5 unit tolerance (SIMPLE WAY)
parent.center_with_tolerance(child, tolerance=5)

# Solve
if parent.solver():
    print(f"Child position: {child.pos_list}")
```

## When to Use What

| Goal | Method | Code |
|------|--------|------|
| **Exact centering** | Simple method | `parent.center_with_tolerance(child, tolerance=0)` |
| **With tolerance** (bias OK) | Simple method | `parent.center_with_tolerance(child, tolerance=10)` |
| **With tolerance** (no bias) | Custom solver | See below ↓ |

## If You Need NO Bias with Tolerance

Use the custom solver (requires 2 extra lines):

```python
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance,
    solver_with_centering_objective,
)

parent = Cell('parent')
child = Cell('child', 'metal1')
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Add centering with tolerance
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)

# Use custom solver (no bias)
solver_with_centering_objective(parent, [centering])
```

**Result:** Truly centered within ±10 units. No left/bottom bias.

## API: center_with_tolerance()

```python
parent.center_with_tolerance(
    child,           # Child cell to center
    ref_obj=None,    # Reference object (defaults to parent)
    tolerance=0      # Tolerance in layout units (0 = exact)
)
```

### Examples

```python
# Exact centering
parent.center_with_tolerance(child, tolerance=0)

# ±10 unit tolerance
parent.center_with_tolerance(child, tolerance=10)

# Center child1 relative to child2 with ±5 tolerance
parent.center_with_tolerance(child1, ref_obj=child2, tolerance=5)

# Method chaining
parent.center_with_tolerance(child1, tolerance=0) \
      .center_with_tolerance(child2, tolerance=5) \
      .solver()
```

## Comparison

### Simple Method (Built-in)

```python
# ONE LINE
parent.center_with_tolerance(child, tolerance=10)
parent.solver()
```

**Pros:**
- ✓ One line of code
- ✓ Built into Cell class
- ✓ No imports needed

**Cons:**
- ✗ tolerance > 0 has left/bottom bias

### Custom Solver (Advanced)

```python
# Requires import + 2 lines
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance, solver_with_centering_objective
)

centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])
```

**Pros:**
- ✓ No left/bottom bias
- ✓ True centered solutions

**Cons:**
- ✗ Requires import
- ✗ Extra setup code

## Quick Decision Tree

```
Do you need tolerance?
├─ NO → Use: parent.center_with_tolerance(child, tolerance=0)
│
└─ YES → Is left/bottom bias acceptable?
    ├─ YES → Use: parent.center_with_tolerance(child, tolerance=10)
    │
    └─ NO → Use custom solver (see README_CENTERING.md)
```

## The Bottom Line

**Simplest way (one line):**
```python
parent.center_with_tolerance(child, tolerance=10)
parent.solver()
```

**Note:** If tolerance > 0, there may be left/bottom bias. For true centering with tolerance, use the custom solver.

**Most common use case (exact centering):**
```python
parent.center_with_tolerance(child, tolerance=0)
parent.solver()
```

This is the same as:
```python
parent.constrain(child, 'center', parent)
parent.solver()
```

## Files

- **This file** - Simple one-line method
- **README_CENTERING.md** - Custom solver (no bias)
- **examples/simple_centering.py** - Examples

Done! You now have the simplest possible way to center with tolerance.
