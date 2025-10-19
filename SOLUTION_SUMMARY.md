# Solution Summary: Centering with Tolerance

## Your Requirements

1. **Try exact centering first**
2. **If that doesn't work, use tolerance** (with proper centering, not left/bottom bias)

## The Problem You Encountered

When using tolerance constraints, objects ended up at the **left/bottom** instead of centered because the solver minimizes coordinate values.

## The Solution

I've implemented a **custom solver** that:
1. Uses tolerance bounds as hard constraints
2. **Minimizes deviation from perfect centering** (instead of minimizing coordinates)
3. Results in **truly centered solutions** within the tolerance range

## How to Use

### Step 1: Import

```python
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance,
    solver_with_centering_objective,
)
```

### Step 2: Create Your Layout

```python
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')
```

### Step 3: Add Centering with Tolerance

```python
centering = add_centering_with_tolerance(
    parent, child, parent,
    tolerance_x=10,  # ±10 units in X
    tolerance_y=10   # ±10 units in Y
)
```

### Step 4: Solve with Custom Objective

```python
if solver_with_centering_objective(parent, [centering]):
    print(f"Success! Child position: {child.pos_list}")
```

## Complete Example

```python
#!/usr/bin/env python3
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

# Optional: Add constraints that might conflict with exact centering
# parent.constrain(child, 'sx1>=40')

# Add centering with tolerance
centering = add_centering_with_tolerance(
    parent, child, parent,
    tolerance_x=10,
    tolerance_y=10
)

# Solve
if solver_with_centering_objective(parent, [centering]):
    # Check result
    parent_cx = (parent.pos_list[0] + parent.pos_list[2]) / 2
    child_cx = (child.pos_list[0] + child.pos_list[2]) / 2
    offset = abs(parent_cx - child_cx)

    print(f"Parent center: {parent_cx}")
    print(f"Child center: {child_cx}")
    print(f"Offset: {offset:.2f} units")

    if offset < 0.1:
        print("✓ Exactly centered!")
    else:
        print(f"✓ Centered within tolerance (±10 units)")
```

## What You Get

| Scenario | Behavior |
|----------|----------|
| **No conflicts** | Child is **exactly centered** (offset = 0) |
| **With conflicts** | Child is **as centered as possible** within tolerance |
| **Always** | **No left/bottom bias** |

## API Quick Reference

### add_centering_with_tolerance()

```python
centering = add_centering_with_tolerance(
    parent,          # Parent cell
    child,           # Child to center
    ref_obj,         # Reference (usually parent)
    tolerance_x=0,   # X tolerance (0 = exact)
    tolerance_y=None,# Y tolerance (defaults to tolerance_x)
    center_x=True,   # Center in X?
    center_y=True    # Center in Y?
)
```

### solver_with_centering_objective()

```python
success = solver_with_centering_objective(
    parent_cell,           # Top-level cell
    centering_constraints, # List of CenteringConstraint objects
    fix_leaf_positions=True,
    integer_positions=True
)
```

## Examples

### Exact Centering (No Tolerance)

```python
# tolerance_x=0 means exact centering required
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=0)
solver_with_centering_objective(parent, [centering])
```

### Centering with Tolerance

```python
# ±10 unit tolerance
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])
```

### X-Only Centering

```python
# Center in X, position Y explicitly
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=5, center_y=False)
parent.constrain(child, 'sy1=20')  # Explicit Y position
solver_with_centering_objective(parent, [centering])
```

### Multiple Children

```python
# Different tolerances for different children
c1 = add_centering_with_tolerance(parent, child1, parent, tolerance_x=0)   # Exact
c2 = add_centering_with_tolerance(parent, child2, parent, tolerance_x=5)   # ±5
c3 = add_centering_with_tolerance(parent, child3, parent, tolerance_x=15)  # ±15

solver_with_centering_objective(parent, [c1, c2, c3])
```

## Files Created

| File | Purpose |
|------|---------|
| `layout_automation/centering_with_tolerance.py` | Implementation (custom solver) |
| `examples/demo_centering_with_tolerance_proper.py` | Examples and tests |
| `HOW_TO_USE_CENTERING_WITH_TOLERANCE.md` | Detailed usage guide |
| `CENTERING_WITH_TOLERANCE_FALLBACK.md` | Technical explanation |
| `SOLUTION_SUMMARY.md` | This file (quick reference) |

## Comparison: Before vs After

### Before (Using Standard Solver)

```python
# ❌ PROBLEM: Left/bottom bias
tolerance_sum = 20
parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent)
parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent)
parent.solver()

# Result: Child at LEFT edge (not centered)
```

### After (Using Custom Solver)

```python
# ✓ SOLUTION: Truly centered
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])

# Result: Child CENTERED (or as close as possible)
```

## Key Differences

| Aspect | Standard Solver | Custom Solver |
|--------|----------------|---------------|
| **Objective** | Minimize coordinates | Minimize centering deviation |
| **With tolerance** | Left/bottom bias | Truly centered |
| **Behavior** | Picks leftmost valid position | Picks most centered position |
| **Use case** | General layout optimization | Centering with tolerance |

## When to Use What

| Goal | Method |
|------|--------|
| Exact centering (no tolerance needed) | `parent.constrain(child, 'center', parent)` + `parent.solver()` |
| Centering with tolerance fallback | `add_centering_with_tolerance()` + `solver_with_centering_objective()` |

## Bottom Line

**Your requirement:** Exact centering with tolerance fallback

**The solution:**
```python
centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)
solver_with_centering_objective(parent, [centering])
```

**What it does:**
- If exact centering possible → centers exactly
- If conflicts exist → centers as close as possible within ±10 units
- No left/bottom bias

**You're done!** Use the custom solver whenever you need tolerance-based centering.
