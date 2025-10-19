# Centering with Tolerance Fallback: The Right Way

## Your Requirement

You want:
1. **Try exact centering first** (if possible)
2. **Fall back to tolerance** (if exact centering conflicts with other constraints)

This is a **soft constraint** problem with a fallback mechanism.

## The Challenge

OR-Tools CP-SAT doesn't directly support "soft constraints" like some other solvers. However, there are several approaches to achieve this behavior.

## Solution 1: Two-Phase Approach (Recommended)

Use constraint relaxation with tolerance bounds, and minimize deviation from center.

### Implementation

```python
def constrain_xcenter_with_tolerance_fallback(parent, child, ref_obj, tolerance):
    """
    Center child in X, with tolerance as fallback

    This uses tolerance bounds but adds the center sum as an objective term
    to minimize deviation from perfect centering.

    Args:
        parent: Parent cell
        child: Child cell to constrain
        ref_obj: Reference object (usually parent)
        tolerance: Maximum allowed deviation from center (in layout units)

    Returns:
        Auxiliary variable name for later objective setting
    """
    tolerance_sum = tolerance * 2

    # Add tolerance bounds (REQUIRED constraints)
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

    # The trick: we need to modify the solver to minimize deviation
    # This requires adding the deviation to the objective function
    #
    # Ideally we want: minimize |sx1+sx2 - (ox1+ox2)|
    #
    # Since current solver minimizes sum(x2, y2), we can:
    # 1. Add an auxiliary variable for deviation
    # 2. Modify solver objective to minimize deviation

    # NOTE: This requires modifying the Cell.solver() method
    # See Solution 2 for a workaround that doesn't require modification
```

**Problem:** This requires modifying the `solver()` method to support custom objectives.

## Solution 2: Use Both Constraints (Works Now!)

The key insight: **OR-Tools CP-SAT tries to satisfy ALL constraints**. If you add both exact and tolerance constraints:

```python
def constrain_xcenter_with_fallback(parent, child, ref_obj, tolerance):
    """
    Center child in X, with tolerance as fallback

    Adds BOTH exact centering and tolerance constraints.
    OR-Tools will:
    1. Try to satisfy exact centering (if possible)
    2. Fall back to tolerance range (if exact conflicts with other constraints)

    Args:
        parent: Parent cell
        child: Child cell to constrain
        ref_obj: Reference object (usually parent)
        tolerance: Maximum deviation from center (in layout units)
    """
    tolerance_sum = tolerance * 2

    # Add both constraints
    # OR-Tools will try to satisfy the equality, but has tolerance as backup
    parent.constrain(child, 'sx1+sx2=ox1+ox2', ref_obj)  # Exact centering
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)  # Lower bound
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)  # Upper bound
```

**Wait!** There's a problem with this approach: If the equality is infeasible, the entire solve will FAIL.

## Solution 3: Conditional Constraints (Manual Approach)

Try solving twice - once with exact, once with tolerance:

```python
def solve_with_centering_fallback(parent, child, ref_obj, tolerance):
    """
    Try exact centering first, fall back to tolerance if it fails

    This solves the problem twice:
    1. First attempt with exact centering
    2. Second attempt with tolerance if first fails

    Args:
        parent: Parent cell
        child: Child cell to constrain
        ref_obj: Reference object
        tolerance: Fallback tolerance

    Returns:
        True if solved (either exact or with tolerance), False otherwise
    """
    # Try 1: Exact centering
    parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', ref_obj)

    if parent.solver():
        print("✓ Exact centering succeeded")
        return True
    else:
        print("✗ Exact centering failed, trying with tolerance...")

        # Remove the exact centering constraints
        # (This requires constraint removal support - not currently available)

        # Try 2: With tolerance
        tolerance_sum = tolerance * 2
        parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
        parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)
        parent.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', ref_obj)
        parent.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', ref_obj)

        if parent.solver():
            print("✓ Tolerance-based centering succeeded")
            return True
        else:
            print("✗ Both approaches failed")
            return False
```

**Problem:** Current Cell implementation doesn't support removing constraints.

## Solution 4: Auxiliary Boolean Variables (Best but Requires Solver Modification)

This is the proper OR-Tools way using boolean indicator variables:

```python
# In the solver, we would add:

# Create boolean variable for "is_centered"
is_centered = model.NewBoolVar('child_is_centered')

# If is_centered is true, enforce exact centering
model.Add(sx1 + sx2 == ox1 + ox2).OnlyEnforceIf(is_centered)
model.Add(sy1 + sy2 == oy1 + oy2).OnlyEnforceIf(is_centered)

# If is_centered is false, enforce tolerance bounds
model.Add(sx1 + sx2 >= ox1 + ox2 - tolerance_sum).OnlyEnforceIf(is_centered.Not())
model.Add(sx1 + sx2 <= ox1 + ox2 + tolerance_sum).OnlyEnforceIf(is_centered.Not())

# Prefer centered solution (add to objective)
model.Maximize(is_centered)  # or add penalty if not centered
```

**Status:** Requires modifying `cell.py` solver to support this pattern.

## Solution 5: PRACTICAL WORKAROUND (Use This Now!)

Since modifying the solver is complex, here's a practical approach that works with the current system:

### Approach A: Use Tolerance but Add Centering Bias

```python
def constrain_xcenter_biased(parent, child, ref_obj, tolerance):
    """
    Center with tolerance, but bias toward center using additional constraints

    This doesn't guarantee perfect centering, but strongly biases toward it
    within the tolerance range.
    """
    tolerance_sum = tolerance * 2

    # Outer bounds: tolerance range
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

    # Add nested constraints to bias toward center
    # Create "soft preference" for center by adding multiple nested ranges
    tolerance_inner = tolerance // 2
    tolerance_inner_sum = tolerance_inner * 2

    # Try to also satisfy tighter constraint (but this is also hard constraint)
    # This doesn't work perfectly but can help in some cases
    # parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_inner_sum}', ref_obj)
    # parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_inner_sum}', ref_obj)

    # Better: add constraints on position directly
    # If parent is known to be at (0,0,100,100), and child width is 30
    # then centered position is x1=35, x2=65
    # We can add preference constraints based on this
```

**Problem:** This still doesn't solve the left/bottom bias issue.

### Approach B: BEST PRACTICAL SOLUTION - Modify Solver Objective

Add a method to Cell that allows custom objectives:

```python
# This is what you should implement in cell.py

def solver_with_centering_objective(self, cells_to_center, fix_leaf_positions=True):
    """
    Solve with custom objective to prefer centered solutions

    Args:
        cells_to_center: List of (child, ref_obj) tuples to center
        fix_leaf_positions: Standard solver parameter

    This modifies the objective to minimize deviation from centering
    instead of minimizing coordinate values.
    """
    # ... existing solver code ...

    # Instead of minimizing sum(x2, y2), minimize centering deviation
    deviation_terms = []

    for child, ref_obj in cells_to_center:
        # Add auxiliary variables for absolute deviation
        child_sum = child_x1 + child_x2
        ref_sum = ref_x1 + ref_x2

        # deviation = |child_sum - ref_sum|
        # In CP-SAT, we need: deviation >= child_sum - ref_sum
        #                     deviation >= ref_sum - child_sum
        deviation = model.NewIntVar(0, coord_max*2, f'{child.name}_center_deviation')
        model.Add(deviation >= child_sum - ref_sum)
        model.Add(deviation >= ref_sum - child_sum)

        deviation_terms.append(deviation)

    # Minimize total deviation (prefers centered solutions)
    model.Minimize(sum(deviation_terms))
```

## RECOMMENDED SOLUTION: Simple Two-Step

Since you need this to work NOW, use this approach:

```python
def constrain_center_with_tolerance(parent, child, ref_obj, tolerance, prefer_center=True):
    """
    Center child with tolerance fallback

    Args:
        parent: Parent cell
        child: Child cell to constrain
        ref_obj: Reference object (usually parent)
        tolerance: Tolerance in layout units
        prefer_center: If True, try exact first (requires solving twice)

    Usage:
        # Try exact first, use tolerance if needed
        success = constrain_center_with_tolerance(
            parent, child, parent,
            tolerance=10,
            prefer_center=True
        )
    """
    if prefer_center:
        # Method 1: Try exact centering first
        # Save current constraints
        original_constraints = parent.constraints.copy()

        # Add exact centering
        parent.constrain(child, 'center', ref_obj)

        # Try to solve
        if parent.solver():
            print(f"✓ Exact centering successful for {child.name}")
            return True
        else:
            # Restore constraints and try with tolerance
            print(f"✗ Exact centering failed for {child.name}, using tolerance...")
            parent.constraints = original_constraints

            # Add tolerance constraints
            tolerance_sum = tolerance * 2
            parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
            parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)
            parent.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', ref_obj)
            parent.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', ref_obj)

            return parent.solver()
    else:
        # Method 2: Just use tolerance
        tolerance_sum = tolerance * 2
        parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
        parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)
        parent.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', ref_obj)
        parent.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', ref_obj)
        return parent.solver()
```

**Note:** This still has the left/bottom bias with tolerance.

## THE REAL SOLUTION YOU NEED

To truly solve this, you need to modify `cell.py` to support one of these:

1. **Custom objective function** - minimize deviation instead of coordinates
2. **Constraint priorities** - mark centering as "soft" constraint
3. **Boolean indicators** - use OnlyEnforceIf for conditional constraints

I can help you implement any of these if you want to modify the solver!

## Quick Summary

| Approach | Pros | Cons | Works Now? |
|----------|------|------|------------|
| Try exact, restore if fails | Simple | Requires 2 solves, still has bias with tolerance | ✓ Yes |
| Boolean indicators | Proper OR-Tools way | Requires solver modification | ✗ No |
| Custom objective | Truly minimizes deviation | Requires solver modification | ✗ No |
| Add both constraints | Simple | Fails if exact is infeasible | ✗ No |

**Bottom line:** With the current system, you'll need to either:
1. Accept the left/bottom bias when using tolerance
2. Modify the solver to support custom objectives (I can help with this!)
3. Use the two-step approach (try exact, fall back to tolerance)

Which would you prefer?
