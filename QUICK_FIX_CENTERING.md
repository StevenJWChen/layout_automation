# Quick Fix: Centering Without Left/Bottom Bias

## Your Problem

When using tolerance constraints for centering, objects end up at the **left/bottom** instead of centered.

```python
# This causes left/bottom bias! ❌
tolerance_sum = 10
parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent)
parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent)
```

## Why It Happens

The solver (in `cell.py:459`) minimizes coordinate values:
```python
model.Minimize(sum(objective_terms))  # Pushes objects to bottom-left
```

When you use inequality constraints (`>=`, `<=`), the solver picks the **leftmost/bottommost** position within the allowed range.

## The Fix

**Use EXACT constraints (`=`) instead of tolerance constraints (`>=`, `<=`):**

### Option 1: Use Built-in Keywords (Easiest)

```python
from layout_automation.cell import Cell

parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# ✓ This gives exact centering
parent.constrain(child, 'center', parent)

parent.solver()
```

### Option 2: Use Helper Functions

```python
from layout_automation.cell import Cell
from layout_automation.constraint_helpers import constrain_center

parent = Cell('parent')
child = Cell('child', 'metal1')

parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# ✓ This gives exact centering
constrain_center(parent, child, parent)

parent.solver()
```

### Option 3: Explicit Constraints

```python
# ✓ Exact centering in X and Y
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)

# ✓ Exact centering in X only
parent.constrain(child, 'sx1+sx2=ox1+ox2', parent)

# ✓ Exact centering in Y only
parent.constrain(child, 'sy1+sy2=oy1+oy2', parent)
```

## Complete Example

```python
#!/usr/bin/env python3
from layout_automation.cell import Cell

# Create cells
parent = Cell('parent')
child = Cell('child', 'metal1')

# Set sizes
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Center child in parent (exact centering)
parent.constrain(child, 'center', parent)

# Solve
if parent.solver():
    print(f"Parent: {parent.pos_list}")
    print(f"Child:  {child.pos_list}")

    # Verify centering
    parent_cx = (parent.pos_list[0] + parent.pos_list[2]) / 2
    child_cx = (child.pos_list[0] + child.pos_list[2]) / 2
    print(f"Parent center X: {parent_cx}")
    print(f"Child center X:  {child_cx}")
    print(f"Offset: {abs(parent_cx - child_cx)}")
```

## Available Helper Functions

```python
from layout_automation.constraint_helpers import (
    constrain_center,        # Center both X and Y
    constrain_xcenter,       # Center X only
    constrain_ycenter,       # Center Y only
    constrain_align_left,    # Align left edges
    constrain_align_right,   # Align right edges
    constrain_align_bottom,  # Align bottom edges
    constrain_align_top,     # Align top edges
    constrain_match_width,   # Match widths
    constrain_match_height,  # Match heights
    constrain_match_size,    # Match both width and height
    constrain_spacing_x,     # Horizontal spacing
    constrain_spacing_y,     # Vertical spacing
)
```

## When You Actually Need Tolerance

If you truly need tolerance (rare cases), combine exact + tolerance:

```python
# Prefer exact centering, allow tolerance if conflicts occur
parent.constrain(child, 'sx1+sx2=ox1+ox2', parent)  # Exact (primary)
parent.constrain(child, 'sx1+sx2>=ox1+ox2-10', parent)  # Tolerance (fallback)
parent.constrain(child, 'sx1+sx2<=ox1+ox2+10', parent)
```

OR-Tools will satisfy the exact constraint if possible, otherwise fall back to tolerance range.

## Bottom Line

**Don't use tolerance constraints for centering.**

Use exact equality constraints (`=`) for true centering:
- Keywords: `'center'`, `'xcenter'`, `'ycenter'`
- Helper functions: `constrain_center()`, `constrain_xcenter()`, `constrain_ycenter()`
- Explicit: `'sx1+sx2=ox1+ox2'`

## Files Created for You

1. **`layout_automation/constraint_helpers.py`** - Helper functions for common constraints
2. **`examples/test_proper_centering.py`** - Verification tests
3. **`examples/demo_tolerance_problem_and_solution.py`** - Problem demonstration
4. **`XCENTER_TOLERANCE_SOLUTION.md`** - Detailed explanation
5. **`QUICK_FIX_CENTERING.md`** - This file (quick reference)

## Import and Use

```python
# Import helper functions
from layout_automation.constraint_helpers import constrain_center

# Use in your code
parent = Cell('parent')
child = Cell('child', 'metal1')
parent.constrain('width=100, height=100')
child.constrain('width=30, height=40')
constrain_center(parent, child, parent)  # ✓ Exact centering
parent.solver()
```

Done! No more left/bottom bias.
