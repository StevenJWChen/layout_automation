# Fix: Constraint-Based Positioning for Fixed Layout Cells

## Issue

Fixed layout cells that were positioned via solver constraints were not maintaining their correct positions. The solver would correctly determine the position, but then it would be overwritten with incorrect values.

## Example of the Bug

```python
from layout_automation.cell import Cell

# Create and fix a cell
child = Cell('child')
# ... (add children and constraints)
child.solver()  # child gets position [0, 0, 12, 8]

c = child.copy('c')
c.fix_layout()  # Fix the layout

# Position using constraint
top = Cell('top')
top.add_instance([child, c])
top.constrain(child, 'sx2+5=ox1', c)  # c should be at x1=17 (12+5)
top.solver()

# BUG: c ends up at [0, 0, 12, 8] instead of [17, 0, 29, 8]
# Expected: c.x1 = 17
# Actual: c.x1 = 0  ✗
```

## Root Cause

The bug occurred in the `_update_parent_bounds()` method, which runs after the solver completes. Here's what was happening:

1. **Solver correctly positions fixed cell:**
   - Solver determines `c` should be at `[17, 0, 29, 8]` ✓
   - This correctly satisfies the constraint `child.x2 + 5 = c.x1` (12 + 5 = 17)

2. **`_update_parent_bounds()` overwrites the position:**
   - For each cell with children, it recalculates bounds from child positions
   - Fixed cell `c` has children `r1=[0,0,8,8]` and `r2=[9,0,12,8]` (from original solve)
   - These child positions are STALE (from when `c` was at origin)
   - Calculates: `c.pos_list = [min(0,9), min(0,0), max(8,12), max(8,8)] = [0, 0, 12, 8]`
   - This OVERWRITES the solver's correct position of `[17, 0, 29, 8]` ✗

3. **Result:**
   - Constraint is violated
   - Fixed cell is at wrong position
   - But children positions will be updated correctly later via `update_fixed_positions()`

## The Fix

Modified `_update_parent_bounds()` in `cell.py` (line 537-540):

```python
for cell in cells_by_depth:
    # Skip fixed/frozen cells - their bounds are determined by solver or offsets
    if cell._fixed or cell._frozen:
        continue

    # ... rest of bounding box calculation
```

**Why this works:**
- **Frozen cells:** The solver positions them as black boxes; their internal structure is hidden
- **Fixed cells:** The solver positions them, then `update_fixed_positions()` propagates to children
- Neither type should have their bounds recalculated from children

## Verification

The fix has been verified with comprehensive tests:

### Test 1: Relative Positioning
```python
top.constrain(child1, 'sx2+5=ox1', cell2)
# ✓ cell2.x1 = child1.x2 + 5
```

### Test 2: Absolute Positioning
```python
top.constrain(c, 'x1=100, y1=50')
# ✓ c positioned at (100, 50) with children updated
```

### Test 3: Multiple Fixed Cells
```python
top.constrain(c1, 'x1=0')
top.constrain(c2, 'sx1=ox2+10', c1)
top.constrain(c3, 'sx1=ox2+10', c2)
# ✓ All cells correctly spaced 10 units apart
```

### Test 4: Hierarchical Structures
```python
parent.add_instance([fixed_cell, other])
parent.constrain(fixed_cell, 'x1=10, y1=10')
parent.constrain(other, 'sx1=ox2+5', fixed_cell)
# ✓ Both positioned correctly relative to each other
```

All tests pass with 100% position accuracy.

## Impact

This fix enables:
- ✓ Constraint-based positioning of fixed cells (not just manual `set_position()`)
- ✓ Complex layouts with multiple fixed cells positioned relative to each other
- ✓ Integration of fixed cells into larger hierarchical designs
- ✓ Maintains all existing performance benefits (2-500x speedup)

## Files Changed

- `layout_automation/cell.py`: Added skip condition in `_update_parent_bounds()`
- `examples/test_fix_layout_constraints.py`: New comprehensive test suite
- `TEST_RESULTS_SUMMARY.md`: Updated documentation

## Status

✓ **Fixed and verified** - All tests pass
