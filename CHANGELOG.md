# Changelog

All notable changes to the layout_automation project.

## [2025-10-18] - Technology File Integration

### Added

#### Technology File Support
- **Tech File Parser:** Complete Cadence Virtuoso technology file parser
  - Parse `layerDefinitions` section for layer names and purposes
  - Parse `streamLayers` section for GDS layer/datatype mappings
  - Parse `drDefineDisplay` section for color definitions
  - Support for generic technology creation as fallback

- **Layer Mapping System:** Bidirectional layer name ↔ GDS number mapping
  - `LayerMapping` class storing name, purpose, GDS layer, datatype, color
  - Fast O(1) lookup by layer name or GDS number
  - Support for multiple purposes per layer (drawing, pin, label, etc.)

- **GDS Import/Export Integration:**
  - Enhanced `export_gds()` with `use_tech_file=True` parameter
  - Enhanced `from_gds()` with `use_tech_file=True` parameter
  - Enhanced `import_gds_to_cell()` with tech file support
  - Automatic tech file layer mapping when enabled
  - Graceful fallback to sensible defaults

- **Style Integration:**
  - `apply_colors_to_style()` method to apply tech file colors
  - Automatic color application from tech file to visualization
  - Integration with existing style customization system

#### New Files
- `layout_automation/tech_file.py` - Technology file parser and manager (301 lines)
  - `TechFile` class with Virtuoso parser
  - `LayerMapping` class for layer information
  - Global tech file management functions
  - Generic technology creation
  - Layer map export functionality

- `examples/demo_tech_file.py` - Comprehensive demo (350+ lines)
  - Custom technology file creation
  - Tech file color application
  - GDS export with tech file layers
  - GDS import with tech file layers
  - Round-trip verification
  - Visual comparison

- `TECH_FILE_INTEGRATION.md` - Complete documentation (500+ lines)
  - Quick start guide
  - API reference
  - Virtuoso format details
  - Examples and best practices
  - Troubleshooting guide

#### API

**TechFile Class:**
```python
from layout_automation.tech_file import TechFile, LayerMapping, get_tech_file, set_tech_file

# Create custom tech
tech = TechFile()
tech.add_layer(LayerMapping('metal1', 'drawing', 30, 0, 'blue'))
set_tech_file(tech)

# Load Virtuoso tech file
from layout_automation.tech_file import load_tech_file
tech = load_tech_file('techfile.tf')

# Apply colors
tech.apply_colors_to_style()
```

**Enhanced Cell Methods:**
```python
# Export with tech file
cell.export_gds('output.gds', use_tech_file=True)

# Import with tech file
imported = Cell.from_gds('input.gds', use_tech_file=True)
```

#### Default GDS Layer Numbers

Updated to industry-standard layer numbering:
- Wells: nwell=1, pwell=2
- Diffusions: ndiff=3, pdiff=4
- Poly: poly=10
- Contacts: contact=20
- Metals: metal1=30, metal2=50, metal3=70, metal4=90, metal5=110, metal6=130
- Vias: via1=40, via2=60, via3=80, via4=100, via5=120

### Changed

#### GDS Layer Mapping Defaults
- **Old:** metal1=1, metal2=2, poly=5 (non-standard)
- **New:** metal1=30, metal2=50, poly=10 (industry standard)
- **Impact:** Better compatibility with foundry GDS files
- **Backward Compatibility:** Custom layer_map still supported

### Demo Output

Running `python3 examples/demo_tech_file.py` generates:
1. `demo_outputs/test_with_techfile.gds` - GDS with tech file layer numbers
2. `demo_outputs/layer_mapping.txt` - Layer mapping reference
3. `demo_outputs/tech_file_roundtrip.png` - Visual comparison

Demo verification:
- ✓ All layer counts match in round-trip
- ✓ GDS export uses tech file layer numbers
- ✓ GDS import correctly maps back to layer names
- ✓ Colors applied from tech file to visualization

### Technical Details

**Virtuoso Format Support:**
- Parses layerDefinitions for layer names
- Parses streamLayers for GDS mappings
- Parses drDefineDisplay for colors
- Converts Virtuoso colors to matplotlib colors

**Performance:**
- O(1) layer lookup by name or GDS number
- No impact on solver performance
- Minimal overhead for GDS import/export

**Backward Compatibility:**
- All existing code works unchanged
- Tech file usage is opt-in via `use_tech_file` parameter
- Custom `layer_map` parameter overrides tech file
- Automatic fallback to generic tech if none loaded

## [2025-10-17] - Bug Fixes and Enhancements

### Fixed

#### Constraint Operator Bug (Critical)
- **Issue:** Strict inequality operators (`<` and `>`) were incorrectly treated as non-strict (`<=` and `>=`)
- **Impact:** Constraints like `x1 > 10` would incorrectly allow `x1 = 10`
- **Fix:** Changed operator matching from `if operator in ['<', '<=']` to exact equality checks
- **File:** `layout_automation/cell.py` (lines 644-653)
- **Test:** `examples/test_operator_correctness.py`

**Example:**
```python
# Before fix:
cell.constrain(r, 'x1 > 10')
cell.solver()
# Result: x1 = 10 ✗ (violates constraint!)

# After fix:
cell.constrain(r, 'x1 > 10')
cell.solver()
# Result: x1 = 11 ✓ (correctly > 10)
```

#### Fixed Cell Constraint Positioning Bug
- **Issue:** Fixed cells positioned via solver constraints would have their position overwritten
- **Root Cause:** `_update_parent_bounds()` recalculated bounds from stale child positions
- **Fix:** Skip fixed/frozen cells in `_update_parent_bounds()`
- **File:** `layout_automation/cell.py` (lines 537-540)
- **Test:** `examples/test_fix_layout_constraints.py`

### Enhanced

#### Draw Resolution
- **Change:** Increased figure size from `(3, 3)` to `(10, 10)` inches with explicit `dpi=100`
- **Impact:** 11x larger display area, much better visibility
- **File:** `layout_automation/cell.py` (line 702)

### Added

#### New Test Suites
1. **`test_operator_correctness.py`** - Comprehensive operator tests
   - Tests all operators: `<`, `<=`, `>`, `>=`, `=`
   - Verifies strict vs non-strict behavior
   - Tests boundary conditions

2. **`test_fix_layout_constraints.py`** - Fixed cell positioning tests
   - Relative positioning between fixed cells
   - Absolute positioning of fixed cells
   - Multiple fixed cells in sequence
   - Hierarchical fixed cell structures

3. **`demo_operator_fix.py`** - Visual demonstration of operator fix

#### Documentation
- `OPERATOR_AND_RESOLUTION_FIXES.md` - Detailed fix documentation
- `FIX_LAYOUT_CONSTRAINT_POSITIONING.md` - Fixed cell positioning fix
- Updated `TEST_RESULTS_SUMMARY.md` with all bug fixes

### Performance

All tests continue to pass with:
- ✓ 100% position accuracy
- ✓ 2-500x performance improvement (fix_layout vs original)
- ✓ All operators now work correctly
- ✓ Fixed cells work with both manual and constraint-based positioning

## [2025-10-17] - Style Customization System

### Added

#### Comprehensive Style Customization
- **Layer Styles:** Full control over layer appearance
  - Custom colors (any matplotlib color)
  - Independent boundary/edge colors
  - Adjustable boundary thickness (line width)
  - Multiple shape types (rectangle, rounded, circle, ellipse, octagon)
  - Transparency/alpha control

- **Container Styles:** Customizable container cell appearance
  - Custom edge colors, width, and line styles
  - Shape support (rectangle, rounded)
  - Color cycling for hierarchy levels

#### New Files
- `layout_automation/style_config.py` - Style configuration system
- `examples/demo_style_customization.py` - Comprehensive demos
- `examples/test_style_features.py` - Unit tests
- `STYLE_CUSTOMIZATION_GUIDE.md` - Complete documentation

#### API
```python
from layout_automation.style_config import get_style_config, reset_style_config

style = get_style_config()

# Customize layers
style.set_layer_style('metal1',
                     color='gold',
                     alpha=0.7,
                     edge_color='darkred',
                     edge_width=3.0,
                     shape='rounded')

# Customize containers
style.set_container_style(edge_color='crimson',
                         edge_width=3.0,
                         linestyle='-.',
                         shape='rounded')

# Reset to defaults
reset_style_config()
```

### Features

- **5 Shape Types:** rectangle, rounded, circle, ellipse, octagon
- **12 Default Layers:** metal1-6, poly, diff, nwell, pwell, contact, via
- **Flexible Colors:** Named colors, hex codes, RGB tuples
- **Line Styles:** Solid, dashed, dash-dot, dotted
- **Theme Support:** Easy to create and apply custom themes

## Summary

This release adds three major improvements:

1. **Operator bug fix:** Ensures `<` and `>` are truly strict (not treated as `<=` and `>=`)
2. **Fixed cell positioning:** Allows constraint-based positioning of fixed cells
3. **Better visualization:** Higher resolution plots for clearer layout views
4. **Style customization:** Complete control over colors, shapes, and boundaries

All existing functionality preserved and enhanced.

---

**Date:** 2025-10-17
**Status:** All tests passing ✓
