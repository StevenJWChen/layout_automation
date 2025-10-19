# Centering with Tolerance - Complete Guide

## Quick Start

```python
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance,
    solver_with_centering_objective,
)

# Create layout
parent = Cell('parent')
child = Cell('child', 'metal1')
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Add centering with ±10 unit tolerance
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)

# Solve (will center exactly if possible, use tolerance if needed)
solver_with_centering_objective(parent, [centering])

print(f"Child position: {child.pos_list}")
```

## Problem Solved

**Your original question:** "How to implement xcenter with tolerance in OR-Tools?"

**Your follow-up:** "Tolerance is essential, but objects end up at left/bottom instead of centered"

**The issue:** Standard OR-Tools solver minimizes coordinate values, causing left/bottom bias when using tolerance constraints.

**The solution:** Custom solver that minimizes deviation from perfect centering instead.

## Documentation

| File | Description |
|------|-------------|
| **SOLUTION_SUMMARY.md** | ⭐ START HERE - Quick reference and examples |
| **HOW_TO_USE_CENTERING_WITH_TOLERANCE.md** | Complete usage guide with API reference |
| **CENTERING_WITH_TOLERANCE_FALLBACK.md** | Technical explanation and alternatives |
| **QUICK_FIX_CENTERING.md** | For exact centering without tolerance |

## Implementation Files

| File | Purpose |
|------|---------|
| `layout_automation/centering_with_tolerance.py` | Custom solver implementation |
| `examples/demo_centering_with_tolerance_proper.py` | Working examples |
| `examples/demo_tolerance_problem_and_solution.py` | Problem demonstration |

## Usage Pattern

### For Exact Centering (No Tolerance)

Use the built-in keyword:

```python
parent.constrain(child, 'center', parent)
parent.solver()
```

### For Centering with Tolerance

Use the custom solver:

```python
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])
```

## Key Concepts

### Tolerance = 0 (Exact)

```python
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=0)
# Same as: parent.constrain(child, 'center', parent)
```

### Tolerance > 0 (With Fallback)

```python
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
# Tries exact centering, falls back to ±10 units if needed
# NO left/bottom bias - truly centered within tolerance
```

## Behavior

| Scenario | Result |
|----------|--------|
| No conflicting constraints | **Exactly centered** (offset = 0) |
| Conflicting constraints exist | **Best centering** within tolerance |
| Conflicts exceed tolerance | **Solver fails** (infeasible) |

## Examples

### Example 1: Basic Centering

```python
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('width=100, height=100')
child.constrain('width=30, height=40')

centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=5)
solver_with_centering_objective(parent, [centering])

# Result: Child centered (or within ±5 units if conflicts exist)
```

### Example 2: With Conflicting Constraint

```python
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
child.constrain('swidth=30, sheight=40')
parent.constrain(child, 'sx1>=40')  # Conflicts with perfect centering!

# Perfect centering would place child at x1=35
# But sx1>=40 requires child to start at x=40 or more

centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])

# Result: Child placed at x1=40 (best centering given the constraint)
# Offset ≈ 5 units (within ±10 tolerance)
```

### Example 3: Multiple Children

```python
parent = Cell('parent')
child1 = Cell('child1', 'metal1')
child2 = Cell('child2', 'poly')

parent.constrain('width=200, height=100')
parent.constrain(child1, 'swidth=40, sheight=30, sy1=10')
parent.constrain(child2, 'swidth=30, sheight=25, sy1=60')

# Different tolerances for different children
c1 = add_centering_with_tolerance(parent, child1, parent, tolerance_x=0, center_y=False)   # Exact
c2 = add_centering_with_tolerance(parent, child2, parent, tolerance_x=15, center_y=False)  # ±15

solver_with_centering_objective(parent, [c1, c2])

# Result:
# - child1: exactly centered in X
# - child2: centered within ±15 units in X
```

## API Reference

### add_centering_with_tolerance()

```python
centering = add_centering_with_tolerance(
    parent,           # Parent cell containing the constraint
    child,            # Child cell to center
    ref_obj,          # Reference object (usually parent or another child)
    tolerance_x=0,    # X tolerance in layout units (0 = exact)
    tolerance_y=None, # Y tolerance (defaults to tolerance_x if not specified)
    center_x=True,    # Whether to center in X direction
    center_y=True     # Whether to center in Y direction
)
```

**Returns:** `CenteringConstraint` object

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

## How It Works

### Standard Solver (Causes Bias)

```python
# Objective: Minimize sum of coordinates
model.Minimize(sum(x2, y2))  # Pushes everything to bottom-left

# With tolerance constraints:
parent.constrain(child, 'sx1+sx2>=ox1+ox2-20', parent)
parent.constrain(child, 'sx1+sx2<=ox1+ox2+20', parent)

# Result: Child at LEFT edge (minimizes coordinates)
```

### Custom Solver (No Bias)

```python
# Objective: Minimize deviation from perfect centering
deviation = |child_center - parent_center|
model.Minimize(sum(deviations))  # Prefers centered solutions

# With tolerance constraints:
add_centering_with_tolerance(parent, child, parent, tolerance_x=10)

# Result: Child CENTERED (minimizes deviation)
```

## When to Use

| Use Case | Solution |
|----------|----------|
| Need exact centering | `parent.constrain(child, 'center', parent)` |
| Need centering with tolerance fallback | `add_centering_with_tolerance()` + custom solver |
| Need constraint priorities | Custom solver with different tolerances |

## Troubleshooting

### Solver Fails

**Cause:** Constraints are infeasible (tolerance too tight)

**Solution:** Increase tolerance or relax other constraints

```python
# Increase tolerance
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=20)
```

### Child Not Centered

**Cause 1:** Forgot to use custom solver

```python
# ❌ Wrong
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
parent.solver()  # Uses standard solver (has bias)

# ✓ Correct
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])  # Uses custom solver
```

**Cause 2:** Conflicting constraints make exact centering impossible

Check if other constraints prevent centering:

```python
# This constraint might conflict with centering
parent.constrain(child, 'sx1>=40')

# Verify by checking offset
parent_cx = (parent.pos_list[0] + parent.pos_list[2]) / 2
child_cx = (child.pos_list[0] + child.pos_list[2]) / 2
offset = abs(parent_cx - child_cx)

if offset < 0.1:
    print("Exactly centered")
elif offset <= tolerance:
    print(f"Centered within tolerance (offset: {offset:.2f})")
else:
    print(f"Exceeds tolerance (offset: {offset:.2f})")
```

## Summary

**Question:** How to implement xcenter with tolerance?

**Answer:** Use `add_centering_with_tolerance()` + `solver_with_centering_objective()`

**Why:** The custom solver minimizes deviation from centering instead of minimizing coordinates, eliminating left/bottom bias.

**Result:**
- Exact centering when possible
- Best centering within tolerance when conflicts exist
- No left/bottom bias

**Read next:** SOLUTION_SUMMARY.md for more examples and details.
