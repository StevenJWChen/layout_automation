# Quick Start: Center Constraint with Tolerance

## What You Asked For

**You wanted**: A constraint to center two polygons, preferring exact centering, but allowing ±1 tolerance if exact centering isn't possible.

**Solution**: Just use the `'center'` keyword!

## One-Line Solution

```python
parent.constrain(polygon_b, 'center', polygon_c)
```

That's it! ✨

## Complete Example

```python
from layout_automation.cell import Cell

# Create cells
parent = Cell('parent')
poly_b = Cell('poly_b', 'metal1')
poly_c = Cell('poly_c', 'metal2')

# Define sizes
parent.constrain(poly_b, 'width=30, height=40, x1=10, y1=10')
parent.constrain(poly_c, 'width=25, height=35')

# Center poly_b with poly_c (exact if possible, ±1 tolerance if not)
parent.constrain(poly_c, 'center', poly_b)

# Solve!
parent.solver()
```

## How It Works

The solver will:
1. ✅ **Try exact centering** (deviation = 0)
2. ✅ **Fall back to ±1 tolerance** if exact conflicts with other constraints
3. ✅ **Minimize deviation** from perfect center
4. ✅ **No left/bottom bias** (uses OR-Tools soft constraints)

## Variations

### X-Only Centering
```python
parent.constrain(poly_b, 'xcenter', poly_c)
```

### Y-Only Centering
```python
parent.constrain(poly_b, 'ycenter', poly_c)
```

## What Changed in cell.py?

**Before**: `'center'` keyword expanded to exact equality constraints only
```python
# Old: Exact centering only, no tolerance
'center' → 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2'
```

**Now**: `'center'` keyword uses soft constraints with ±1 tolerance
```python
# New: Prefers exact, allows ±1 tolerance
'center' → soft constraint pattern with tolerance
```

## Implementation

Uses **OR-Tools native soft constraint pattern**:
- Hard constraint: ±1 tolerance range (always satisfied)
- Soft constraint: Exact centering (preferred via objective function)
- Objective penalty: Minimizes `deviation * 10000`

## Test It

Run the example:
```bash
python examples/simple_center_example.py
```

Expected output:
```
✓ Solver succeeded!
Deviation: X=0.5, Y=0.5
✓ Centering within ±1 tolerance achieved!
```

## When NOT Exact?

Exact centering fails when:
- Odd/even dimension mismatch (e.g., 30 vs 25)
- Integer rounding issues
- Conflicting constraints

In these cases, the solver finds the **best centering within ±1 tolerance**.

## Advanced Usage

Need a different tolerance? Use the advanced API:

```python
from layout_automation.centering_with_tolerance import center_and_solve

# Custom tolerance of ±5 units
center_and_solve(parent, child, tolerance=5, ref_obj=ref)
```

## Summary

| What you write | What you get |
|----------------|--------------|
| `parent.constrain(b, 'center', c)` | Center with ±1 tolerance |
| `parent.constrain(b, 'xcenter', c)` | X-center with ±1 tolerance |
| `parent.constrain(b, 'ycenter', c)` | Y-center with ±1 tolerance |

**No configuration. No special imports. Just works!** 🎉

---

**See also**:
- `CENTER_CONSTRAINT_WITH_TOLERANCE.md` - Full documentation
- `examples/simple_center_example.py` - Working example
- `examples/test_center_with_tolerance.py` - Comprehensive test suite
