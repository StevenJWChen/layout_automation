# Bug Fixes: Operator Parsing and Draw Resolution

## Fix 1: Constraint Operator Bug (< and > vs <= and >=)

### Issue

Strict inequality operators `<` and `>` were being treated as non-strict (`<=` and `>=`), causing incorrect constraint behavior.

**Example of the bug:**
```python
cell.constrain(r, 'x1 > 10')  # Should require x1 > 10 (strictly)
cell.solver()
# BUG: x1 = 10 (violates constraint!)
# EXPECTED: x1 = 11 (or any value > 10)
```

### Root Cause

In `_add_constraints_recursive_ortools()` method (line 644-649), the operator checking used `in` to match lists:

```python
# BUGGY CODE:
if operator in ['<', '<=']:
    model.Add(left_linear_expr <= right_linear_expr)  # Always <=
elif operator in ['>', '>=']:
    model.Add(left_linear_expr >= right_linear_expr)  # Always >=
```

This meant:
- `<` matched `['<', '<=']` → applied `<=` (wrong!)
- `>` matched `['>', '>=']` → applied `>=` (wrong!)
- `<=` matched `['<', '<=']` → applied `<=` (correct, but by accident)
- `>=` matched `['>', '>=']` → applied `>=` (correct, but by accident)

### Fix

Changed to exact operator matching:

```python
# FIXED CODE:
if operator == '<':
    model.Add(left_linear_expr < right_linear_expr)
elif operator == '<=':
    model.Add(left_linear_expr <= right_linear_expr)
elif operator == '>':
    model.Add(left_linear_expr > right_linear_expr)
elif operator == '>=':
    model.Add(left_linear_expr >= right_linear_expr)
elif operator == '=':
    model.Add(left_linear_expr == right_linear_expr)
```

### Verification

Created comprehensive test suite in `examples/test_operator_correctness.py`:

| Constraint | Expected | Before Fix | After Fix | Status |
|------------|----------|------------|-----------|--------|
| `x1 >= 10` | x1 ≥ 10  | x1 = 10 ✓  | x1 = 10 ✓ | ✓ (works both ways) |
| `x1 > 10`  | x1 > 10  | x1 = 10 ✗  | x1 = 11 ✓ | ✓ **FIXED** |
| `x1 <= 10` | x1 ≤ 10  | x1 = 0 ✓   | x1 = 0 ✓  | ✓ (works both ways) |
| `x1 < 10`  | x1 < 10  | x1 = 0 ✓   | x1 = 0 ✓  | ✓ (works both ways) |
| `x1 = 25`  | x1 = 25  | x1 = 25 ✓  | x1 = 25 ✓ | ✓ (works both ways) |

**Key Test Case:**
```python
# Constraint: x1 > 10 (strictly greater)
cell.constrain(r, 'x1>10, x2-x1=5, y2-y1=5')
cell.solver()

# Before fix: x1 = 10 (WRONG - violates constraint!)
# After fix:  x1 = 11 (CORRECT - satisfies x1 > 10)
```

## Fix 2: Draw Resolution

### Issue

The `draw()` method created plots with very low resolution (3x3 inches), making it difficult to see details in complex layouts.

### Fix

Changed figure size from `(3, 3)` to `(10, 10)` with explicit DPI:

```python
# Before:
fig, ax = plt.subplots(figsize=(3, 3))

# After:
fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
```

### Impact

- **Display size:** 3x3 inches → 10x10 inches (11x larger area)
- **Screen resolution:** ~300x300 pixels → ~1000x1000 pixels
- **Saved resolution:** Can be saved at even higher DPI (e.g., 150 or 300)
- **Better visibility:** Text, labels, and layout details are much clearer

### Example

```python
cell.draw()  # Now shows at 10x10 inches, 100 DPI
plt.savefig('output.png', dpi=300)  # Can save at high resolution
```

## Files Changed

1. **`layout_automation/cell.py`:**
   - Line 644-653: Fixed operator matching (exact equality checks)
   - Line 702: Increased figure size to (10, 10) with dpi=100

2. **`examples/test_operator_correctness.py`:**
   - New comprehensive test suite for all operators
   - Tests boundary conditions and strict vs non-strict inequalities

## Status

✓ **Both fixes verified and tested**
- All existing tests pass
- New operator tests confirm correct behavior
- Draw resolution significantly improved

## Date

2025-10-17
