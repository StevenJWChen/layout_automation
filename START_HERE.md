# START HERE: Centering with Tolerance

## What You Want

**Tolerance > 0** with **true centering** (no left/bottom bias)

## The Answer (ONE LINE!)

```python
from layout_automation.centering_with_tolerance import center_and_solve

center_and_solve(parent, child, tolerance=10)
```

That's it! 🎉

## Complete Example

```python
#!/usr/bin/env python3
from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import center_and_solve

# Create layout
parent = Cell('parent')
child = Cell('child', 'metal1')

# Set sizes
parent.constrain('x1=0, y1=0, x2=100, y2=100')
parent.constrain(child, 'swidth=30, sheight=40')

# Center with ±10 tolerance (TRUE CENTERING, NO BIAS)
center_and_solve(parent, child, tolerance=10)

# Done!
print(f"Child: {child.pos_list}")
```

## What You Get

✅ Tolerance > 0 (±10 units)
✅ **TRUE centering** (no left/bottom bias)
✅ ONE function call
✅ Replaces `parent.solver()`

## Usage Examples

```python
# ±5 unit tolerance
center_and_solve(parent, child, tolerance=5)

# Different X and Y tolerances
center_and_solve(parent, child, tolerance_x=15, tolerance_y=10)

# Exact centering (tolerance=0)
center_and_solve(parent, child, tolerance=0)

# Center child1 relative to child2
center_and_solve(parent, child1, tolerance=5, ref_obj=child2)

# X-only centering
center_and_solve(parent, child, tolerance=10, center_y=False)
```

## How It Works

- **tolerance=0**: Uses exact constraint, standard solver
- **tolerance>0**: Uses custom solver that **minimizes deviation** from center
  - Result: Child is truly centered within tolerance range
  - No left/bottom bias!

## Comparison

### ❌ Old Way (Has Bias)

```python
parent.constrain(child, 'sx1+sx2>=ox1+ox2-20', parent)
parent.constrain(child, 'sx1+sx2<=ox1+ox2+20', parent)
parent.solver()

# Result: Child at LEFT edge (not centered)
```

### ✅ New Way (No Bias)

```python
from layout_automation.centering_with_tolerance import center_and_solve

center_and_solve(parent, child, tolerance=10)

# Result: Child CENTERED within ±10 units
```

## Files

- **This file (START_HERE.md)** - Quick start ⭐
- **examples/easiest_centering.py** - Working examples
- **EASIEST_NO_BIAS_SOLUTION.md** - Detailed guide

## That's All You Need!

One import, one function call:

```python
from layout_automation.centering_with_tolerance import center_and_solve
center_and_solve(parent, child, tolerance=10)
```

**Your requirement:** Tolerance > 0 with center bias
**The solution:** `center_and_solve(parent, child, tolerance=10)` ✅
