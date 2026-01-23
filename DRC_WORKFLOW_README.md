# DRC Workflow - Design Rule Check and Auto-Fix

A comprehensive DRC (Design Rule Check) system that imports GDS files, detects violations, and automatically fixes them based on technology file rules.

## Overview

The DRC workflow enables automatic detection and correction of design rule violations in IC layouts:

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  DRC WORKFLOW PIPELINE                                        │
│                                                               │
│  1. Import GDS        →  Load layout from GDS-II file        │
│  2. Load DRC Rules    →  Parse tech file (FreePDK45.tf)      │
│  3. Check Violations  →  Detect spacing/width violations     │
│  4. Auto-Fix          →  Apply constraints and resize        │
│  5. Re-Check          →  Verify fixes worked                 │
│  6. Export Fixed GDS  →  Save corrected layout               │
│  7. Generate Report   →  Create violation reports            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Supported DRC Rules

The system currently supports the following DRC checks:

| Rule Type | Description | Example |
|-----------|-------------|---------|
| **minWidth** | Minimum width/height of shapes | metal1 must be ≥ 0.065 µm wide |
| **minSpacing** | Minimum spacing between shapes on same layer | metal1 shapes must be ≥ 0.065 µm apart |
| **minSpacing (layer pairs)** | Minimum spacing between different layers | nwell-to-active ≥ 0.055 µm |
| **minSameNetSpacing** | Minimum spacing for same-net shapes | metal1 same-net ≥ 0.065 µm |

### Auto-Fix Capabilities

The auto-fixer can correct violations by:

1. **Width Violations**: Automatically resizes shapes to meet minimum width requirements
2. **Spacing Violations**: Adds spacing constraints or repositions shapes to meet minimum spacing
3. **Iterative Solving**: Re-runs constraint solver to find valid configurations

## Architecture

### Module Structure

```
layout_automation/
├── tech_file.py           # Tech file parser (extended with DRC rules)
│   ├── DRCRule            # Single DRC rule class
│   ├── DRCRuleSet         # Collection of DRC rules
│   └── TechFile           # Tech file parser (now parses DRC rules)
│
├── drc_checker.py         # DRC violation detection
│   ├── DRCViolation       # Violation data class
│   └── DRCChecker         # Main checker class
│
├── drc_fixer.py           # DRC violation auto-fix
│   └── DRCFixer           # Main fixer class
│
└── cell.py                # Cell class (uses DRC modules)

drc_workflow.py            # Main workflow script
test_drc_workflow.py       # Comprehensive test suite
```

### Class Hierarchy

```python
# DRC Rule Classes
DRCRule(rule_type, layer1, layer2, value)
DRCRuleSet()
  ├── .rules: List[DRCRule]
  ├── .width_rules: Dict[str, float]
  ├── .spacing_rules: Dict[str, float]
  └── .layer_pair_spacing: Dict[Tuple[str, str], float]

# Violation Detection
DRCViolation(rule_type, layer, message, cell1, cell2, value, required)
DRCChecker(drc_rules: DRCRuleSet)
  ├── .check_layout(cell) -> List[DRCViolation]
  ├── .print_violations()
  └── .export_violations_report(filepath)

# Violation Fixing
DRCFixer(drc_rules: DRCRuleSet)
  ├── .fix_violations(cell, violations) -> (fixed, unfixed)
  └── .create_fix_constraints(cell) -> List[str]
```

## Installation

No additional dependencies required beyond the base layout_automation package:

```bash
# The DRC modules are included in the layout_automation package
cd /path/to/layout_automation
export PYTHONPATH=$PWD:$PYTHONPATH
```

## Usage

### Command-Line Interface

The `drc_workflow.py` script provides a complete end-to-end workflow:

```bash
# Basic usage: check + fix + export
python drc_workflow.py input.gds FreePDK45.tf output_fixed.gds

# Check-only mode (no fixing)
python drc_workflow.py input.gds FreePDK45.tf --check-only

# Generate violation reports
python drc_workflow.py input.gds FreePDK45.tf output.gds --report violations.txt

# Adjust fix iterations
python drc_workflow.py input.gds FreePDK45.tf output.gds --max-iterations 10
```

### Python API

Use the DRC modules programmatically in your own scripts:

```python
from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile
from layout_automation.drc_checker import DRCChecker
from layout_automation.drc_fixer import DRCFixer

# 1. Load tech file and DRC rules
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
print(f"Loaded {len(tech.drc_rules.rules)} DRC rules")

# 2. Import GDS
cell = Cell.from_gds('input.gds', tech_file=tech)

# 3. Check for violations
checker = DRCChecker(tech.drc_rules)
violations = checker.check_layout(cell)
checker.print_violations()

# 4. Auto-fix violations
if violations:
    fixer = DRCFixer(tech.drc_rules)
    fixed, unfixed = fixer.fix_violations(cell, violations)
    print(f"Fixed {fixed} violations, {unfixed} could not be fixed")

# 5. Re-check
violations_after = checker.check_layout(cell)
print(f"Violations remaining: {len(violations_after)}")

# 6. Export fixed GDS
if len(violations_after) < len(violations):
    cell.export_gds('output_fixed.gds', tech_file=tech)
```

### Creating Test Layouts

Create layouts with intentional violations for testing:

```python
from layout_automation.cell import Cell

# Create metal1 rectangle with width violation
metal1_narrow = Cell('metal1_narrow', 'metal1')
metal1_narrow.constrain('x1=0, y1=0, width=0.04, height=0.5')  # 0.04 < 0.065 (violation!)

# Create two metal1 rectangles with spacing violation
metal1_left = Cell('metal1_left', 'metal1')
metal1_left.constrain('x1=1.0, y1=0, width=0.1, height=0.3')

metal1_right = Cell('metal1_right', 'metal1')
metal1_right.constrain('x1=1.15, y1=0, width=0.1, height=0.3')  # Spacing 0.05 < 0.065 (violation!)

# Create parent and solve
parent = Cell('test_layout', metal1_narrow, metal1_left, metal1_right)
parent.solver()

# Export for testing
parent.export_gds('test_violations.gds')
```

## DRC Rules in FreePDK45

The FreePDK45.tf technology file contains DRC rules in the `constraintGroups` section:

```lisp
constraintGroups(
  foundry(
    spacings(
      ( minWidth              "poly"      0.05 )
      ( minSpacing            "poly"      0.075 )
      ( minWidth              "metal1"    0.065 )
      ( minSpacing            "metal1"    0.065 )
      ( minSameNetSpacing     "metal1"    0.065 )
      ( minSpacing            "nwell" "active"  0.055 )
      ...
    )
  )
)
```

### Key Rules (FreePDK45 45nm process)

| Layer | Min Width (µm) | Min Spacing (µm) |
|-------|----------------|------------------|
| poly | 0.050 | 0.075 |
| active | 0.090 | 0.080 |
| metal1 | 0.065 | 0.065 |
| metal2 | 0.070 | 0.075 |
| metal3 | 0.070 | 0.070 |
| via1 | 0.065 | 0.075 |
| contact | 0.075 | 0.075 |
| nwell | 0.200 | 0.225 |

## Testing

### Run Test Suite

```bash
# Run all DRC workflow tests
python test_drc_workflow.py
```

The test suite includes:

1. **DRC Rules Parsing Test**: Verifies tech file parsing
2. **DRC Checker Unit Test**: Tests violation detection on simple layout
3. **Complete DRC Workflow Test**: End-to-end test with violations, fixing, and export

### Expected Test Output

```
================================================================================
DRC Workflow Test Suite
================================================================================

DRC Rules Parsing Test
  Parsed 50 DRC rules
  metal1 minWidth: 0.065
  metal1 minSpacing: 0.065
  poly minWidth: 0.05
  ✓ Test PASSED: DRC rules parsed correctly

DRC Checker Unit Test
  Expected: 1 width violation
  Found: 1 violation(s)
  ✓ Test PASSED: Width violation detected

Complete DRC Workflow Test
  Initial violations: 5
  Violations after fix: 2
  Fixed: 3
  Remaining: 2
  Improvement: 60.0%
  ✓ Test PASSED: DRC violations reduced

Total: 3/3 tests passed
✓ All tests passed!
```

## Example Output

### Violation Report Format

```
DRC Violation Report
================================================================================

Total Violations: 5

Width Violations (3):
--------------------------------------------------------------------------------
  Layer: metal1
  Cell: metal1_narrow
  Actual: 0.040
  Required: 0.065
  Message: Width violation on metal1: metal1_narrow has width 0.040 < 0.065 (required)

Spacing Violations (2):
--------------------------------------------------------------------------------
  Layer: metal1
  Cell 1: metal1_left
  Cell 2: metal1_right
  Actual: 0.050
  Required: 0.065
  Message: Spacing violation on metal1: metal1_left and metal1_right have spacing 0.050 < 0.065 (required)
```

## Workflow Output Example

```
================================================================================
DRC Workflow - Design Rule Check and Auto-Fix
================================================================================

[Step 1/7] Loading technology file and DRC rules...
Parsing Virtuoso tech file: FreePDK45.tf
[OK] Loaded 115 layer mappings and 50 DRC rules

[Step 2/7] Importing GDS file: input.gds
✓ Imported GDS: inverter_layout

[Step 3/7] Running DRC check...

================================================================================
Initial DRC Check Results
================================================================================

✗ Found 5 DRC violation(s):
--------------------------------------------------------------------------------

Width Violations (2):
  • Width violation on metal1: metal1_narrow has width 0.040 < 0.065 (required)
  • Height violation on poly: poly_short has height 0.030 < 0.050 (required)

Spacing Violations (3):
  • Spacing violation on metal1: metal1_left and metal1_right have spacing 0.050 < 0.065 (required)
  • Spacing violation on poly: poly_bottom and poly_top have spacing 0.050 < 0.075 (required)
  • Spacing violation between nwell and active: nwell_1 and active_1 have spacing 0.040 < 0.055 (required)

[Step 4/7] Attempting to auto-fix violations...
  ✓ Fixed width of metal1_narrow: 0.040 -> 0.065
  ✓ Fixed height of poly_short: 0.030 -> 0.050
  ✓ Added spacing constraint: metal1_left <-> metal1_right (gap: 0.065)

Re-solving layout with new constraints...
✓ Layout solved successfully

[Step 5/7] Re-checking DRC after fixes...

================================================================================
Final DRC Check Results
================================================================================

✗ Found 2 DRC violation(s):
--------------------------------------------------------------------------------

Spacing Violations (2):
  • Spacing violation on poly: poly_bottom and poly_top have spacing 0.060 < 0.075 (required)
  • Spacing violation between nwell and active: nwell_1 and active_1 have spacing 0.048 < 0.055 (required)

[Step 6/7] Comparing results...
  Initial violations: 5
  Fixed violations:   3
  Remaining violations: 2
  Improvement: 60.0%

[Step 7/7] Exporting fixed GDS: output_fixed.gds
✓ Successfully exported fixed GDS

================================================================================
DRC Workflow Complete
================================================================================
```

## Limitations

### Current Limitations

1. **Fixed Cells**: GDS-imported cells are "frozen" by default, limiting auto-fix capabilities
2. **Hierarchy**: Violations across deep hierarchies may not be fixable
3. **Complex Rules**: Only spacing and width rules are currently supported (no enclosure, density, antenna, etc.)
4. **Geometry**: Assumes rectangular shapes; complex polygons may not be handled correctly
5. **Same-Net Detection**: Cannot distinguish between same-net and different-net shapes

### Future Enhancements

Planned improvements:

- [ ] Support for enclosure rules (via enclosure, contact enclosure)
- [ ] Support for density rules (metal density, poly density)
- [ ] Support for antenna rules
- [ ] Support for complex polygon DRC
- [ ] Net-aware spacing checks (same-net vs. different-net)
- [ ] Interactive violation visualization
- [ ] Waiver system for acceptable violations
- [ ] DRC rule deck export for commercial tools

## Troubleshooting

### Common Issues

**Issue**: No violations detected when violations should exist

```python
# Check if DRC rules were loaded
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
print(f"Rules loaded: {len(tech.drc_rules.rules)}")  # Should be > 0
tech.drc_rules.print_summary()
```

**Issue**: Auto-fix doesn't reduce violations

```python
# Check if cells have valid positions
for child in cell.children:
    print(f"{child.name}: {child.pos_list}")  # Should not contain None

# Try manually solving first
cell.solver()
```

**Issue**: GDS import fails

```python
# Use import_gds_to_cell instead of from_gds for better constraint support
cell = Cell.import_gds_to_cell('input.gds', tech_file=tech)
```

## Integration with Existing Tools

### Exporting DRC Reports for Other Tools

```python
# Export violations in custom format
violations = checker.check_layout(cell)
with open('violations_custom.txt', 'w') as f:
    for v in violations:
        # Custom format: LAYER RULE CELL1 CELL2 ACTUAL REQUIRED
        f.write(f"{v.layer} {v.rule_type} {v.cell1.name} ")
        if v.cell2:
            f.write(f"{v.cell2.name} ")
        f.write(f"{v.value} {v.required}\n")
```

### Using with Other Tech Files

The DRC workflow works with any Virtuoso-format tech file that has a `constraintGroups/spacings` section:

```python
# Use with different tech files
tech = TechFile()
tech.parse_virtuoso_tech_file('my_custom.tf')

# Check which rules were loaded
tech.drc_rules.print_summary()
```

## Contributing

To add new DRC rule types:

1. Add rule type to `DRCRule` class in `tech_file.py`
2. Add parsing logic to `_parse_drc_rules()` method
3. Add checking logic to `DRCChecker` class
4. Add fixing logic to `DRCFixer` class
5. Add tests to `test_drc_workflow.py`

## License

See main LICENSE file for details.

## Related Documentation

- [USER_MANUAL.md](USER_MANUAL.md) - Main user manual
- [GDS_INVESTIGATION_SUMMARY.md](GDS_INVESTIGATION_SUMMARY.md) - GDS import/export details
- [AUTO_LAYERMAP_README.md](AUTO_LAYERMAP_README.md) - Layer mapping configuration
- [FreePDK45.tf](FreePDK45.tf) - Technology file with DRC rules

## Credits

DRC workflow enhancement created for the layout_automation project.
