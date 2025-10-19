# Implementing XCenter with Tolerance in OR-Tools

## Understanding XCenter

The `xcenter` keyword in your constraint system expands to:
```
xcenter → sx1+sx2=ox1+ox2
```

This means:
```
child.x1 + child.x2 = parent.x1 + parent.x2
2 × child_center_x = 2 × parent_center_x
child_center_x = parent_center_x
```

This is an **exact equality** constraint - the child must be perfectly centered.

## Adding Tolerance

To add tolerance, replace the equality (`=`) with inequality constraints (`>=` and `<=`).

### Mathematical Approach

For a tolerance of `±T` units on the center position:

- **Exact constraint:** `sx1 + sx2 = ox1 + ox2`
- **With tolerance:** `ox1 + ox2 - 2T ≤ sx1 + sx2 ≤ ox1 + ox2 + 2T`

**Note:** The tolerance is multiplied by 2 because `sx1+sx2` represents `2 × center_x`.

### Implementation in OR-Tools

## Method 1: Direct Inequality Constraints

```python
from layout_automation.cell import Cell

# Create cells
parent = Cell('parent')
child = Cell('child', 'metal1')

# Define parent and child sizes
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'sx2-sx1=30, sy2-sy1=40')

# XCenter with ±5 unit tolerance
tolerance = 5
tolerance_sum = tolerance * 2  # = 10

# Add two inequality constraints instead of one equality
parent.constrain(child, f'sx1+sx2>={parent.pos_list[0]}+{parent.pos_list[2]}-{tolerance_sum}', parent)
parent.constrain(child, f'sx1+sx2<={parent.pos_list[0]}+{parent.pos_list[2]}+{tolerance_sum}', parent)

# Or using the variable form:
parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent)
parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent)

# Exact Y centering (no tolerance)
parent.constrain(child, 'sy1+sy2=oy1+oy2', parent)

# Solve
parent.solver()
```

## Method 2: Helper Functions (Recommended)

Create reusable helper functions for cleaner code:

```python
def constrain_xcenter_with_tolerance(parent, child, ref_obj, tolerance):
    """
    Constrain child's X center to be within tolerance of ref_obj's X center

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
        tolerance: Tolerance in layout units (±T)
    """
    tolerance_sum = tolerance * 2
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

def constrain_ycenter_with_tolerance(parent, child, ref_obj, tolerance):
    """
    Constrain child's Y center to be within tolerance of ref_obj's Y center

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
        tolerance: Tolerance in layout units (±T)
    """
    tolerance_sum = tolerance * 2
    parent.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', ref_obj)

def constrain_center_with_tolerance(parent, child, ref_obj, tolerance_x, tolerance_y=None):
    """
    Constrain child's center (both X and Y) to be within tolerance

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
        tolerance_x: X tolerance in layout units
        tolerance_y: Y tolerance (defaults to tolerance_x if not specified)
    """
    if tolerance_y is None:
        tolerance_y = tolerance_x

    constrain_xcenter_with_tolerance(parent, child, ref_obj, tolerance_x)
    constrain_ycenter_with_tolerance(parent, child, ref_obj, tolerance_y)

# Usage example
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'sx2-sx1=30, sy2-sy1=40')

# Center with ±5 unit tolerance
constrain_center_with_tolerance(parent, child, parent, tolerance_x=5)

parent.solver()
```

## Method 3: Extended Keywords (Future Enhancement)

You could extend `constraint_keywords.py` to support tolerance syntax:

```python
# Potential future syntax:
parent.constrain(child, 'xcenter_tol(5)', parent)  # ±5 unit tolerance
parent.constrain(child, 'center_tol(5,8)', parent)  # ±5 in X, ±8 in Y
```

This would require modifying the keyword expansion system to parse function-like syntax.

## Complete Working Example

```python
#!/usr/bin/env python3
from layout_automation.cell import Cell

# Helper function
def constrain_xcenter_with_tolerance(parent, child, ref_obj, tolerance):
    tolerance_sum = tolerance * 2
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

# Create layout
parent = Cell('parent')
child = Cell('child', 'metal1')

# Set sizes
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'sx2-sx1=30, sy2-sy1=40')

# Apply xcenter with ±8 unit tolerance
constrain_xcenter_with_tolerance(parent, child, parent, tolerance=8)

# Exact Y centering
parent.constrain(child, 'sy1+sy2=oy1+oy2', parent)

# Solve
if parent.solver():
    parent_center_x = (parent.pos_list[0] + parent.pos_list[2]) / 2
    child_center_x = (child.pos_list[0] + child.pos_list[2]) / 2
    offset = abs(parent_center_x - child_center_x)

    print(f"Parent center X: {parent_center_x}")
    print(f"Child center X:  {child_center_x}")
    print(f"Offset: {offset:.2f} units")
    print(f"Within tolerance: {offset <= 8}")
```

## How OR-Tools Handles Tolerance

When you provide inequality constraints with tolerance:

1. **Feasible Region:** OR-Tools identifies all solutions where the child center is within the tolerance range
2. **Solution Selection:** The solver will pick ANY valid solution within this range
3. **No Preference:** Without additional constraints or objectives, OR-Tools doesn't prefer centered solutions
4. **Deterministic:** Given the same constraints, OR-Tools typically returns the same solution

### Forcing Centered Solutions

If you want the solver to prefer centered solutions while allowing tolerance:

```python
# Strong preference: use exact equality
parent.constrain(child, 'sx1+sx2=ox1+ox2', parent)

# Backup with tolerance: OR-Tools will try to satisfy exact centering first
# If impossible due to other constraints, it will use the tolerance range
```

OR-Tools CP-SAT solver will always try to satisfy higher-priority constraints first.

## Key Points

1. **Tolerance Doubling:** A tolerance of `±T` on center position requires `±2T` on the sum `sx1+sx2`

2. **Two Constraints:** Replace one equality with two inequalities:
   - `sx1+sx2 >= ox1+ox2-2T` (lower bound)
   - `sx1+sx2 <= ox1+ox2+2T` (upper bound)

3. **Use Helper Functions:** Makes code more readable and maintainable

4. **OR-Tools Behavior:** Will find ANY solution within tolerance range; doesn't automatically center

5. **Combine with Other Constraints:** Tolerance constraints work alongside all other constraint types

## Troubleshooting

### "No solution found"
- Tolerance may be too tight combined with other constraints
- Try increasing tolerance or relaxing other constraints

### "Child is at edge of tolerance range"
- OR-Tools doesn't prefer centered solutions
- Add exact centering constraint if you want centered behavior with tolerance as backup

### "Results vary between runs"
- Normal if you have multiple valid solutions
- OR-Tools is deterministic but may choose any valid solution
- Add additional constraints to narrow the solution space

## Advanced: Different Tolerances for Different Cells

```python
# Different children, different tolerances
parent.constrain('width=200, height=200')

child1 = Cell('child1', 'metal1')
child2 = Cell('child2', 'poly')
child3 = Cell('child3', 'contact')

parent.constrain(child1, 'swidth=40, sheight=40')
parent.constrain(child2, 'swidth=30, sheight=30')
parent.constrain(child3, 'swidth=20, sheight=20')

# Tight tolerance for child1
constrain_xcenter_with_tolerance(parent, child1, parent, tolerance=2)
parent.constrain(child1, 'sy1=20')

# Medium tolerance for child2
constrain_xcenter_with_tolerance(parent, child2, parent, tolerance=10)
parent.constrain(child2, 'sy1=80')

# Wide tolerance for child3
constrain_xcenter_with_tolerance(parent, child3, parent, tolerance=20)
parent.constrain(child3, 'sy1=140')

parent.solver()
```

## Conclusion

**Recommended Approach:** Use the helper function method (Method 2) for clean, maintainable code.

The key insight is that tolerance constraints use **inequalities** instead of **equalities**, and the tolerance value must be **doubled** because you're constraining the sum of coordinates rather than the center directly.
