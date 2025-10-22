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

#### Root Cause - Hierarchical Coordinate System Bug

The **REAL issue** was in the GDS export code, not rounding errors. When exporting hierarchical layouts, children were placed at **absolute positions** instead of **positions relative to their parent**.

**The Bug in `_convert_to_gds()` (lines 1813-1830):**

```python
# OLD BUGGY CODE
# Created reference at absolute child position
x1, y1, _, _ = child.pos_list
x1 += offset_x  # offset_x was always 0
y1 += offset_y  # offset_y was always 0
ref = gdstk.Reference(child_gds_cell, origin=(x1, y1))
```

#### Example of the Bug

Given hierarchy:
```
top_cell (0, 0, 1000, 1000)
  └─ mid_level (100, 100, 500, 500)
      └─ leaf (150, 150, 250, 250)
```

**What should happen:**
- Leaf should be at (50, 50) relative to mid_level (150-100 = 50)
- GDS file: mid_level references leaf at **(50, 50)**
- On import: 100 + 50 = **150** ✓

**What actually happened:**
- Leaf was exported at absolute position (150, 150) in mid_level
- GDS file: mid_level references leaf at **(150, 150)** ✗
- On import: 100 + 150 = **250** ✗ (shifted by 100!)

#### The Fix

Modified `_convert_to_gds()` in `layout_automation/cell.py` lines 1769-1830:

```python
# NEW FIXED CODE
# Get parent's origin for relative positioning
parent_x1 = self.pos_list[0] if all(v is not None for v in self.pos_list) else 0
parent_y1 = self.pos_list[1] if all(v is not None for v in self.pos_list) else 0

# Place children relative to parent
x1, y1, _, _ = child.pos_list
ref = gdstk.Reference(child_gds_cell, origin=(x1 - parent_x1, y1 - parent_y1))
```

**Now exports correctly:**
- Leaf at (150, 150) with parent at (100, 100)
- GDS file: mid_level references leaf at **(50, 50)** ✓ relative position!
- On import: 100 + 50 = **150** ✓ Correct!

#### Minor Fix - Rounding Precision

Also fixed a minor rounding issue in `_from_gds_cell()` line 1956:

```python
# Keep leaf dimensions as floats to avoid cumulative rounding errors
leaf_cell.pos_list = [0.0, 0.0, x2 - x1, y2 - y1]  # Not int(round(...))
```

This ensures rounding happens only once at the final position calculation.

---

## Test Results

Created comprehensive test suite to verify the fixes:

### `test_gds_hierarchy_detail.py` - Hierarchical position verification

**Confirms the main fix:**
- ✅ Before fix: mid_level referenced leaf at **(150, 150)** - absolute, wrong
- ✅ After fix: mid_level references leaf at **(50, 50)** - relative, correct!
- ✅ Imported position: [150, 150, 250, 250] with **shift [0, 0, 0, 0]** ✓

### `test_gds_shift_deep.py` - Comprehensive position shift tests

**Test 1: Simple leaf cells**
- ✅ All positions preserved exactly (rect1, rect2, rect3)

**Test 3: Hierarchical cells (3 levels)**
- ✅ **Before fix:** leaf positions shifted by parent offset (100, 100) and (600, 600)
- ✅ **After fix:** All leaf positions preserved perfectly:
  - leaf1: [150, 150, 250, 250] - no shift ✓
  - leaf2: [300, 300, 450, 450] - no shift ✓
  - leaf3: [650, 650, 850, 850] - no shift ✓

### `test_gds_relative_check.py` - Relative position preservation

- ✅ Inter-child spacing preserved: [400, 400, 500, 500] maintained
- ✅ Relative positions between siblings maintained correctly

### `test_gds_reuse.py` - Multi-cycle export/import test

**Tests GDS IP reuse workflow:**
- ✅ Export hierarchical layout
- ✅ Import it back
- ✅ Use imported cell in NEW layout
- ✅ Export and import again
- ✅ **All relative spacings preserved through multiple cycles!**

### `test_gds_simple.py` - Basic functionality tests

**Test 1-2: Cell naming**
- ✅ Cell 'top' works correctly
- ✅ Any cell name works identically

**Test 3: Floating point rounding**
- ✅ Position [10.7, 20.3, 40.9, 35.6] imports as [11, 20, 41, 36]
- ✅ All coordinates round correctly (35.6 → 36, not 35)

### `test_gds_trace.py` - Diagnostic rounding trace

- Shows exact rounding behavior at each step
- Demonstrates minor rounding fix working correctly

---

## Files Changed

### Main Fix - `layout_automation/cell.py`

**Lines 1769-1830: `_convert_to_gds()` method**
- Removed unused `offset_x` and `offset_y` parameters
- Added `parent_x1` and `parent_y1` calculation from `self.pos_list`
- Changed child reference placement from absolute to relative:
  - Old: `origin=(x1, y1)` - absolute position
  - New: `origin=(x1 - parent_x1, y1 - parent_y1)` - relative position

**Line 1956: `_from_gds_cell()` method**
- Minor fix: Keep leaf dimensions as floats instead of rounding
- Changed `int(round(x2-x1))` to `x2-x1` to preserve precision

## Impact

### Fixed Issues
- ✅ **Hierarchical position shifts** - MAJOR FIX
  - Multi-level layouts now export/import correctly
  - No more cumulative position shifts in nested structures
- ✅ **Rounding precision** - Minor improvement
  - Fractional coordinates round correctly

### Compatibility
- ✅ **No Breaking Changes** - Existing flat layouts continue to work
- ✅ **Backward Compatible** - Old GDS files can still be imported
- ⚠️ **Re-export Recommended** - GDS files with hierarchies should be re-exported with fixed version for accuracy

### Performance
- ✅ **No Performance Impact** - Same computational complexity

---

## Recommendations

1. ✅ **Re-export hierarchical GDS files** - If you have multi-level layouts, re-export them with the fixed version
2. ✅ **Cell name 'top' is safe** - Use any cell name without concerns
3. ✅ **IP reuse workflow validated** - Can safely import GDS cells and reuse them
4. ✅ **Position verification** - Use test suite to verify your layouts if needed

---

## Summary

| Issue | Status | Root Cause | Solution |
|-------|--------|------------|----------|
| Cell name 'top' issues | ✅ No issue found | N/A | None needed |
| Position shift (flat) | ✅ Always worked | N/A | None needed |
| **Position shift (hierarchical)** | ✅ **FIXED** | **Absolute coords instead of relative** | **Use relative positioning** |
| Rounding precision | ✅ Fixed | Premature rounding | Keep floats until final calc |
| **Cell name collisions** | ✅ **FIXED** | **Used name as dict key** | **Use object ID as key** |

**Main Achievements:**
1. Hierarchical GDS export/import now works correctly with proper relative coordinate handling!
2. Cells with duplicate names in different hierarchy branches are preserved correctly!

---

## Additional Fix: Cell Name Collision (NEW)

### Issue
When multiple cells in different parts of the hierarchy had the same name, the GDS export would overwrite them because it used `cell.name` as the dictionary key.

**Example:**
```python
block1/rect: 100x100 metal1
block2/rect: 200x200 metal2
```

**Bug:** Only ONE 'rect' cell exported (100x100), second was lost!

### Root Cause
Line 1782-1787 and 1799-1813 used `gds_cells_dict[child.name]` as the key, causing overwrites.

### Solution (Commit fe6401d)
- Changed dictionary key from `cell.name` to `id(cell)`
- Added `gds_name_counter` to track used GDS names
- Generate unique suffixes for duplicates: `rect`, `rect_1`, `rect_2`, etc.

### Result
✅ All cells preserved with unique GDS names
✅ Verified by `test_gds_name_collision.py`
