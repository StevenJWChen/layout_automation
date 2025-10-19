# Solution: XCenter with Tolerance - Fixing Left/Bottom Bias

## The Problem

When using tolerance constraints like:
```python
parent.constrain(child, 'sx1+sx2>=ox1+ox2-10', parent)
parent.constrain(child, 'sx1+sx2<=ox1+ox2+10', parent)
```

The child always ends up at the **left/bottom** of the tolerance range instead of being centered.

## Root Cause

In `cell.py` line 459, the solver has this objective:

```python
model.Minimize(sum(objective_terms))  # Minimizes sum of all x2, y2 coordinates
```

This minimizes coordinate values, pushing all positions toward the bottom-left corner. When you have tolerance constraints, the solver picks the leftmost/bottommost valid position because it minimizes the objective.

## Solutions

### Solution 1: Use Exact Centering Constraint (Recommended)

**Best for:** When you want true centering, with tolerance as a fallback only if exact centering is impossible.

```python
def constrain_xcenter_exact_with_fallback(parent, child, ref_obj, tolerance):
    """
    Try to center exactly, with tolerance as fallback

    This adds BOTH exact equality AND tolerance inequalities.
    OR-Tools will satisfy the equality if possible, otherwise use tolerance.
    """
    tolerance_sum = tolerance * 2

    # Primary constraint: exact centering (OR-Tools will try to satisfy this first)
    parent.constrain(child, 'sx1+sx2=ox1+ox2', ref_obj)

    # Fallback constraints: tolerance range (in case exact is impossible)
    # These are typically not needed if exact is always satisfiable
    # parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    # parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

# Usage
parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# This will center exactly
constrain_xcenter_exact_with_fallback(parent, child, parent, tolerance=5)
parent.constrain(child, 'sy1+sy2=oy1+oy2', parent)  # Y centering

parent.solver()
```

**When to use:** When you want centered positioning and tolerance is just a "safety margin" in case of conflicts.

### Solution 2: Introduce Auxiliary Variable for True Centering

**Best for:** When you need actual tolerance but want centered solutions within that range.

```python
def constrain_xcenter_with_centered_tolerance(parent, child, ref_obj, tolerance):
    """
    Center child within tolerance, preferring centered position

    This creates an auxiliary 'offset' variable and minimizes it,
    forcing the solver to prefer centered solutions.

    NOTE: This requires modifying the Cell class to support auxiliary variables
    """
    tolerance_sum = tolerance * 2

    # Standard tolerance constraints
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

    # Would need to add: minimize |sx1+sx2 - (ox1+ox2)|
    # This requires extending the solver to support custom objectives
```

**Status:** This requires modifying the `solver()` method to accept custom objectives. Not currently supported.

### Solution 3: Add Bias Toward Center

**Best for:** Practical workaround without modifying the solver.

```python
def constrain_xcenter_with_bias_toward_center(parent, child, ref_obj, tolerance):
    """
    Use tighter constraints to bias toward center

    Instead of using full tolerance range, use nested constraints
    that guide the solver toward the center.
    """
    tolerance_sum = tolerance * 2

    # Outer bounds: full tolerance
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

    # Add soft preference for center by constraining size more tightly
    # This doesn't guarantee centering but biases toward it
    # (This is a workaround, not a perfect solution)

# Better approach: Just use exact centering
def constrain_xcenter_prefer_center(parent, child, ref_obj):
    """Simply use exact centering - simplest and most effective"""
    parent.constrain(child, 'sx1+sx2=ox1+ox2', ref_obj)
```

### Solution 4: Modify Solver Objective (Advanced)

**Best for:** When you need full control over optimization behavior.

This requires modifying `cell.py` to accept a custom objective function:

```python
# In cell.py, modify the solver method signature:
def solver(self, fix_leaf_positions=True, integer_positions=True, objective='minimize_size'):
    """
    objective options:
    - 'minimize_size': Current behavior (minimize coordinates)
    - 'none': No objective, just find feasible solution
    - 'center_tolerance': Minimize deviation from center (custom)
    """
    # ... existing code ...

    if objective == 'minimize_size':
        # Current behavior (lines 447-459)
        objective_terms = []
        for cell in all_cells:
            x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
            x2_var = var_objects[x2_idx]
            y2_var = var_objects[y2_idx]
            objective_terms.append(x2_var)
            objective_terms.append(y2_var)
        model.Minimize(sum(objective_terms))

    elif objective == 'none':
        # Don't set any objective - just find any feasible solution
        # This might give more centered results with tolerance
        pass

    elif objective == 'center_tolerance':
        # Custom objective to minimize deviation from center
        # This would require tracking which constraints are tolerance-based
        # and creating auxiliary variables for their deviations
        pass
```

## Recommended Approach

**For your use case, use Solution 1:**

```python
# Simple helper function
def constrain_xcenter(parent, child, ref_obj):
    """Center child X exactly"""
    parent.constrain(child, 'sx1+sx2=ox1+ox2', ref_obj)

def constrain_ycenter(parent, child, ref_obj):
    """Center child Y exactly"""
    parent.constrain(child, 'sy1+sy2=oy1+oy2', ref_obj)

def constrain_center(parent, child, ref_obj):
    """Center child both X and Y exactly"""
    parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', ref_obj)

# Or just use the built-in keywords:
parent.constrain(child, 'center', parent)  # Uses exact centering
```

## Why Exact Centering is Better

1. **Predictable:** Always produces centered results
2. **Simple:** No tolerance math required
3. **Efficient:** Solver has fewer valid solutions to search
4. **Correct:** Actually centers the child

## When You Actually Need Tolerance

If you truly need tolerance (e.g., for design rule constraints or physical limitations):

### Use Case 1: Design Rules Allow Range
```python
# Example: child can be within ±5 units of center due to grid constraints
tolerance_sum = 5 * 2

# Add both constraints
parent.constrain(child, 'sx1+sx2=ox1+ox2', parent)  # Prefer exact
parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent)  # Lower bound
parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent)  # Upper bound

# OR-Tools will satisfy exact if possible, otherwise use tolerance
```

### Use Case 2: Tolerance Due to Other Constraints
```python
# If other constraints make exact centering impossible,
# tolerance gives the solver flexibility

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Add constraints that might conflict with exact centering
parent.constrain(child, 'sx1>=10')  # Must be at least 10 units from left
parent.constrain(child, 'sx2<=85')  # Must be at least 15 units from right

# Now exact centering might be impossible, so use tolerance
tolerance_sum = 10 * 2
parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent)
parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent)
```

## Quick Fix: Use Keywords

The existing keyword system already supports exact centering:

```python
from layout_automation.cell import Cell

parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('width=100, height=100, x1=0, y1=0')
parent.constrain(child, 'swidth=30, sheight=40')

# Use keyword - this gives EXACT centering
parent.constrain(child, 'center', parent)

parent.solver()

# Result: child will be exactly centered
print(f"Parent: {parent.pos_list}")
print(f"Child: {child.pos_list}")

parent_cx = (parent.pos_list[0] + parent.pos_list[2]) / 2
parent_cy = (parent.pos_list[1] + parent.pos_list[3]) / 2
child_cx = (child.pos_list[0] + child.pos_list[2]) / 2
child_cy = (child.pos_list[1] + child.pos_list[3]) / 2

print(f"Parent center: ({parent_cx}, {parent_cy})")
print(f"Child center: ({child_cx}, {child_cy})")
print(f"Offset: ({abs(parent_cx - child_cx)}, {abs(parent_cy - child_cy)})")
```

## Summary

**The problem:** The solver minimizes coordinate values, pushing objects to bottom-left.

**The solution:** Use **exact centering** constraints (`sx1+sx2=ox1+ox2`) instead of tolerance inequalities.

**When you need tolerance:** Only use it when other constraints might make exact centering impossible. Even then, combine it with the exact constraint so the solver prefers centered solutions.

**Quick answer:**
```python
# Instead of this (causes left/bottom bias):
parent.constrain(child, 'sx1+sx2>=ox1+ox2-10', parent)
parent.constrain(child, 'sx1+sx2<=ox1+ox2+10', parent)

# Use this (exact centering):
parent.constrain(child, 'xcenter', parent)
# or
parent.constrain(child, 'center', parent)  # both X and Y
```
