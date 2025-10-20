# Recent Updates Summary

## Updates Completed

### 1. Fixed `fix_layout()` Bug with Duplicate Cell Names

**Problem**: Using `cell.name` as dictionary key failed when multiple children had the same name.

**Solution**: Changed to use `id(child)` for unique identification.

**Files Modified**:
- `layout_automation/cell.py` (lines 1245, 1306-1308)

**Test Files**:
- `test_fix_duplicate_names.py`

---

### 2. Added Position Properties to Cell Class

**New Properties** (all read-only):
- `cell.x1`, `cell.y1`, `cell.x2`, `cell.y2` - Corner coordinates
- `cell.width`, `cell.height` - Dimensions
- `cell.cx`, `cell.cy` - Center coordinates

**Benefits**:
- More readable code: `cell.width` vs `cell.pos_list[2] - cell.pos_list[0]`
- Less error-prone
- All return `None` if not yet positioned

**Files Modified**:
- `layout_automation/cell.py` (lines 1191-1273)

**Documentation**:
- `CELL_PROPERTIES_README.md`

**Test Files**:
- `test_width_height_properties.py`
- `test_cell_properties.py`
- `example_cell_properties.py`

---

### 3. Added `line_style` and `zorder` to Layer Styles

**New Properties**:

#### LayerStyle
- `line_style` (str): Edge line style (`'-'`, `'--'`, `'-.'`, `':'`)
  - Default: `'-'` (solid)
- `zorder` (int): Drawing order (higher = on top)
  - Default: `1`

#### ContainerStyle
- `zorder` (int): Drawing order
  - Default: `0` (containers behind layers)

**Usage**:
```python
from layout_automation.style_config import get_style_config

style_config = get_style_config()

# Set line style and zorder
style_config.set_layer_style(
    'metal1',
    color='blue',
    line_style='-',   # solid, dashed, dashdot, dotted
    zorder=3          # drawing order
)
```

**Benefits**:
- Visual differentiation with line styles
- Control layer stacking with zorder
- Better visualization of IC layer hierarchy
- Matches physical layer stack

**Files Modified**:
- `layout_automation/style_config.py`
  - `LayerStyle.__init__()` (lines 15-41)
  - `ContainerStyle.__init__()` (lines 47-70)
  - `set_layer_style()` (lines 111-157)
  - `set_container_style()` (lines 159-188)
  - `reset_style_config()` (lines 205-220)

- `layout_automation/cell.py`
  - `_draw_recursive()` (lines 1004-1014, 1028-1038)

**Documentation**:
- `LINE_STYLE_ZORDER_README.md`

**Test Files**:
- `test_line_style_zorder.py`
- `example_line_style_zorder.py`

**Visual Output**:
- `demo_outputs/test_line_style_zorder.png`
- `demo_outputs/example_line_style_zorder.png`

---

## All Tests Passing

All new features have been tested and verified:
- ✓ Duplicate cell names work correctly with `fix_layout()`
- ✓ Position properties return correct values
- ✓ Line styles display correctly
- ✓ Z-order controls layer stacking properly

## Backward Compatibility

All changes are fully backward compatible:
- Existing code continues to work without modification
- New properties have sensible defaults
- All new parameters are optional
- No breaking changes to API
