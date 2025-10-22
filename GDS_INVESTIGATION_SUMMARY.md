# GDS Import/Export Investigation Summary

## Issues Investigated

1. **Cell name 'top' cannot GDS in/out well**
2. **Polygon positions shift after GDS import** (in some conditions)

---

## Findings

### Issue 1: Cell Name 'top'

**Status:** ✅ **NO ISSUE FOUND**

Comprehensive testing shows that cells named 'top' work correctly in GDS import/export:

- Export succeeds
- Import succeeds
- Cell name preserved
- Hierarchy preserved
- Nested structures with 'top' as root work correctly

**Conclusion:** The cell name 'top' does not cause any special issues. It works the same as any other cell name.

---

### Issue 2: Polygon Position Shift

**Status:** ✅ **ISSUE FOUND AND FIXED**

#### Root Cause

A **cumulative rounding error** occurred during GDS import due to rounding happening twice:

1. **First round**: When creating leaf cell from GDS polygon
   ```python
   # OLD CODE (line 1955)
   leaf_cell.pos_list = [0, 0, int(round(x2 - x1)), int(round(y2 - y1))]
   ```

2. **Second round**: When applying reference offset
   ```python
   # In _apply_offset_recursive (lines 2029-2033)
   cell.pos_list = [
       int(round(cell.pos_list[0] + dx)),  # Rounding integer + offset
       int(round(cell.pos_list[1] + dy)),
       int(round(cell.pos_list[2] + dx)),  # Rounding integer + offset
       int(round(cell.pos_list[3] + dy))
   ]
   ```

#### Example of the Bug

Original position: `[10.7, 20.3, 40.9, 35.6]`

**Buggy behavior:**
- Export stores rectangle (0, 0) to (30.2, 15.3) with reference at (10.7, 20.3)
- Import creates leaf: `[0, 0, round(30.2)=30, round(15.3)=15]`
- Apply offset: `[round(0+10.7)=11, round(0+20.3)=20, round(30+10.7)=41, round(15+20.3)=35]`
- **Result: `[11, 20, 41, 35]` - Error on y2: 35 instead of 36!**

**Expected:** `round(35.6) = 36`
**Got:** `round(15 + 20.3) = round(35.3) = 35` ❌

#### The Fix

Modified `_from_gds_cell()` in `layout_automation/cell.py` line 1956:

```python
# NEW CODE - Keep dimensions as floats
leaf_cell.pos_list = [0.0, 0.0, x2 - x1, y2 - y1]
```

Now rounding only happens once, after adding the offset:
- Import creates leaf: `[0.0, 0.0, 30.2, 15.3]` (floats!)
- Apply offset: `[round(0+10.7)=11, round(0+20.3)=20, round(30.2+10.7)=41, round(15.3+20.3)=36]`
- **Result: `[11, 20, 41, 36]` ✓ Correct!**

---

## Test Results

Created comprehensive test suite to verify the fixes:

### `test_gds_simple.py` - Full test suite with 4 test cases

**Test 1: Cell named 'top'**
- ✅ Export/import succeeds
- ✅ Cell name preserved: 'top'
- ✅ Child positions match exactly

**Test 2: Cell named 'my_layout' (control)**
- ✅ Works identically to 'top' (confirms no special behavior)

**Test 3: Floating point position rounding**
- ✅ Position [10.7, 20.3, 40.9, 35.6] correctly imports as [11, 20, 41, 36]
- ✅ All coordinates round correctly:
  - 10.7 → 11 ✓
  - 20.3 → 20 ✓
  - 40.9 → 41 ✓
  - 35.6 → 36 ✓ (was 35 before fix)

**Test 4: Nested hierarchy with 'top' name**
- ✅ 3-level hierarchy works correctly
- ✅ Root name 'top' preserved
- ✅ All children imported correctly

### `test_gds_trace.py` - Diagnostic trace

Detailed trace showing:
- Exact values at each step of export/import
- How GDS stores polygon coordinates
- Where rounding occurs
- Analysis of the bug and fix

---

## Files Changed

- **layout_automation/cell.py** (line 1956)
  Changed `int(round(x2 - x1))` to `x2 - x1` to preserve float precision

## Impact

- **Fixes:** Polygon position shifts in GDS import/export
- **No Breaking Changes:** Existing code continues to work
- **Performance:** No impact (same number of operations)
- **Precision:** Improved accuracy of GDS round-trips

---

## Recommendations

1. ✅ **Use the fixed version** - polygon positions now preserve correctly
2. ✅ **Cell name 'top' is safe** - no special handling needed
3. If you encounter position shifts in existing GDS files, re-export with the fixed version

---

## Summary

| Issue | Status | Solution |
|-------|--------|----------|
| Cell name 'top' issues | ✅ No issue found | None needed |
| Polygon position shift | ✅ Fixed | Keep float precision until final rounding |

Both issues have been investigated and resolved. The GDS import/export functionality now works correctly.
