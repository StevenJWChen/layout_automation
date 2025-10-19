# How to Use: Centering with Tolerance

## The Solution to Your Problem

You wanted: **Try exact centering first, fall back to tolerance if it doesn't work**

This is now implemented! Here's how to use it.

## Quick Start

```python
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance,
    solver_with_centering_objective,
)

# Create cells
parent = Cell('parent')
child = Cell('child', 'metal1')

# Set sizes
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Add centering with ±10 unit tolerance
centering = add_centering_with_tolerance(
    parent, child, parent,
    tolerance_x=10,
    tolerance_y=10
)

# Solve with custom objective that prefers centered solutions
if solver_with_centering_objective(parent, [centering]):
    print(f"Parent: {parent.pos_list}")
    print(f"Child:  {child.pos_list}")
```

## How It Works

### The Magic

1. **Adds tolerance bounds** as hard constraints (child MUST be within ±tolerance)
2. **Minimizes deviation** from perfect centering (prefers centered solutions)
3. **No left/bottom bias** (objective minimizes deviation, not coordinate values)

### What You Get

- **If exact centering possible**: Child will be **exactly centered** (offset = 0)
- **If conflicts exist**: Child will be **as centered as possible** within tolerance
- **Always**: Solution will be **within tolerance bounds**

## API Reference

### add_centering_with_tolerance()

```python
centering = add_centering_with_tolerance(
    parent,          # Parent cell containing the constraint
    child,           # Child cell to center
    ref_obj,         # Reference object (usually parent or another child)
    tolerance_x=0,   # X tolerance in layout units (0 = exact)
    tolerance_y=None,# Y tolerance (defaults to tolerance_x)
    center_x=True,   # Whether to center in X
    center_y=True    # Whether to center in Y
)
```

**Returns:** `CenteringConstraint` object (pass to solver)

**Examples:**

```python
# Exact centering (no tolerance)
c1 = add_centering_with_tolerance(parent, child, parent, tolerance_x=0, tolerance_y=0)

# ±5 units in both X and Y
c2 = add_centering_with_tolerance(parent, child, parent, tolerance_x=5)

# ±10 in X, ±5 in Y
c3 = add_centering_with_tolerance(parent, child, parent, tolerance_x=10, tolerance_y=5)

# X centering only (no Y centering)
c4 = add_centering_with_tolerance(parent, child, parent, tolerance_x=5, center_y=False)

# Y centering only (no X centering)
c5 = add_centering_with_tolerance(parent, child, parent, tolerance_y=5, center_x=False)
```

### solver_with_centering_objective()

```python
success = solver_with_centering_objective(
    parent_cell,              # Top-level cell to solve
    centering_constraints,    # List of CenteringConstraint objects
    fix_leaf_positions=True,  # Standard solver parameter
    integer_positions=True    # Standard solver parameter
)
```

**Returns:** `True` if solution found, `False` otherwise

**Examples:**

```python
# Single centering constraint
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=5)
solver_with_centering_objective(parent, [centering])

# Multiple centering constraints
c1 = add_centering_with_tolerance(parent, child1, parent, tolerance_x=5)
c2 = add_centering_with_tolerance(parent, child2, parent, tolerance_x=10)
c3 = add_centering_with_tolerance(parent, child3, parent, tolerance_x=15)
solver_with_centering_objective(parent, [c1, c2, c3])
```

## Complete Example

```python
#!/usr/bin/env python3
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance,
    solver_with_centering_objective,
)

# Create parent
parent = Cell('parent')
parent.constrain('x1=0, y1=0, x2=100, y2=100')

# Create child
child = Cell('child', 'metal1')
parent.constrain(child, 'swidth=30, sheight=40')

# Add constraint that might conflict with perfect centering
parent.constrain(child, 'sx1>=40')  # Child must start at x=40 or more

# Perfect centering would place child at x1=35
# But sx1>=40 conflicts!
# Solution: Use tolerance to allow solver to find best centering

# Add centering with ±10 unit tolerance
centering = add_centering_with_tolerance(
    parent, child, parent,
    tolerance_x=10,  # Allow ±10 units deviation
    tolerance_y=10
)

# Solve
if solver_with_centering_objective(parent, [centering]):
    # Calculate centers
    parent_cx = (parent.pos_list[0] + parent.pos_list[2]) / 2
    child_cx = (child.pos_list[0] + child.pos_list[2]) / 2
    offset = abs(parent_cx - child_cx)

    print(f"Parent center X: {parent_cx}")
    print(f"Child center X: {child_cx}")
    print(f"Offset: {offset:.2f} units")

    if offset < 0.1:
        print("✓ Exactly centered (no conflicts)")
    elif offset <= 10:
        print(f"✓ Within tolerance (solver minimized deviation)")
        print(f"  Child is as centered as possible given sx1>=40 constraint")
    else:
        print("✗ Exceeds tolerance")
else:
    print("✗ Solver failed")
```

## Behavior Examples

### Example 1: No Conflicts → Exact Centering

```python
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Add centering with tolerance
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])

# Result: Child is EXACTLY centered
# child.pos_list = [35, 30, 65, 70]
# Offset = 0 (exact)
```

### Example 2: With Conflicts → Best Within Tolerance

```python
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')
parent.constrain(child, 'sx1>=40')  # Conflicts with perfect centering

# Add centering with tolerance
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])

# Result: Child is as centered as possible while satisfying sx1>=40
# child.pos_list = [40, 30, 70, 70]  # Starts at x=40 (minimum allowed)
# Offset ≈ 5 units (best possible given the constraint)
```

### Example 3: Multiple Children, Different Tolerances

```python
parent = Cell('parent')
child1 = Cell('child1', 'metal1')
child2 = Cell('child2', 'poly')

parent.constrain('x1=0, y1=0, x2=200, y2=100')
parent.constrain(child1, 'swidth=40, sheight=30, sy1=10')
parent.constrain(child2, 'swidth=30, sheight=25, sy1=60')

# Child1: Exact centering (tolerance = 0)
c1 = add_centering_with_tolerance(parent, child1, parent, tolerance_x=0, center_y=False)

# Child2: ±15 unit tolerance
c2 = add_centering_with_tolerance(parent, child2, parent, tolerance_x=15, center_y=False)

# Solve
solver_with_centering_objective(parent, [c1, c2])

# Result:
# child1 is EXACTLY centered in X
# child2 is centered within ±15 units
```

## Tolerance Values

| `tolerance_x` | Meaning | Behavior |
|---------------|---------|----------|
| `0` | Exact centering required | Hard constraint (must center exactly) |
| `> 0` | Allow deviation | Soft constraint (prefer centered, allow ±tolerance) |

**Example:**
```python
# Exact X centering, ±5 units in Y
add_centering_with_tolerance(parent, child, parent, tolerance_x=0, tolerance_y=5)
```

## Comparison with Standard Solver

### Using Standard Solver (cell.solver())

```python
# ❌ Problem: Left/bottom bias
parent.constrain(child, 'sx1+sx2>=ox1+ox2-20', parent)
parent.constrain(child, 'sx1+sx2<=ox1+ox2+20', parent)
parent.solver()

# Result: Child ends up at LEFT edge of tolerance range
# Because solver minimizes coordinate values
```

### Using Custom Solver (solver_with_centering_objective())

```python
# ✓ Solution: Minimizes deviation from center
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])

# Result: Child is CENTERED (or as close as possible)
# Because solver minimizes deviation from perfect centering
```

## When to Use Each Approach

| Use Case | Method | Code |
|----------|--------|------|
| Exact centering (no tolerance) | Built-in keyword | `parent.constrain(child, 'center', parent)` |
| Exact centering with helper | Helper function | `constrain_center(parent, child, parent)` |
| Centering with tolerance fallback | Custom solver | `add_centering_with_tolerance()` + `solver_with_centering_objective()` |

## Summary

**Your original problem:** "I want exact centering, but if that doesn't work, then use tolerance"

**The solution:**
```python
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance,
    solver_with_centering_objective,
)

# Add centering with tolerance
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)

# Solve with custom objective
solver_with_centering_objective(parent, [centering])
```

**What you get:**
- Exact centering if possible
- Best centering within tolerance if exact is impossible
- No left/bottom bias
- Multiple children with different tolerances supported

**Files to use:**
- `layout_automation/centering_with_tolerance.py` - The implementation
- `examples/demo_centering_with_tolerance_proper.py` - Examples

Done!
