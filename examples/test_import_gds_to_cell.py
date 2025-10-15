#!/usr/bin/env python3
"""
Test import_gds_to_cell method:
1. Import existing GDS layout with position constraints
2. Modify layout by adding new constraints
3. Re-solve to get adjusted layout with minimal changes
4. Export modified layout
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

print("=" * 80)
print("TESTING import_gds_to_cell METHOD")
print("=" * 80)
print()

# ==============================================================================
# STEP 1: Create an Original Layout and Export to GDS
# ==============================================================================
print("STEP 1: Create Original Layout")
print("-" * 80)
print()

# Create a simple inverter layout
original = Cell('INVERTER')

# Add layers
diff_layer = Cell('diff_layer', 'diff')
poly_gate = Cell('poly_gate', 'poly')
metal1 = Cell('metal1_layer', 'metal1')
metal2 = Cell('metal2_layer', 'metal1')
contact1 = Cell('contact1', 'contact')
contact2 = Cell('contact2', 'contact')

original.add_instance([diff_layer, poly_gate, metal1, metal2, contact1, contact2])

# Add constraints for original positions
original.constrain(diff_layer, 'x1=0, y1=10, x2=50, y2=30')
original.constrain(poly_gate, 'x1=20, y1=5, x2=30, y2=35')
original.constrain(metal1, 'x1=5, y1=15, x2=18, y2=25')
original.constrain(metal2, 'x1=32, y1=15, x2=45, y2=25')
original.constrain(contact1, 'x1=8, y1=18, x2=12, y2=22')
original.constrain(contact2, 'x1=38, y1=18, x2=42, y2=22')

# Solve and export
if original.solver():
    print(f"✓ Original layout solved")
    print(f"  Cell: {original.name}")
    print(f"  Children: {len(original.children)}")
    print()

    # Display original tree
    print("Original layout structure:")
    original.tree(show_positions=True, show_layers=True)
    print()

    # Export to GDS
    gds_file = 'demo_outputs/original_inverter.gds'
    original.export_gds(gds_file)
    print(f"✓ Exported to {gds_file}")
else:
    print("✗ Original layout solver failed")
    exit(1)

print()
print()

# ==============================================================================
# STEP 2: Import GDS with Position Constraints
# ==============================================================================
print("STEP 2: Import GDS with Position Constraints")
print("-" * 80)
print()

# Import the GDS file
imported = Cell.import_gds_to_cell(gds_file, add_position_constraints=True)

print()
print(f"Imported cell structure:")
imported.tree(show_positions=False, show_layers=True)
print()

# Show that constraints were added
print(f"Number of constraints: {len(imported.constraints)}")
print(f"Sample constraints:")
for i, (cell1, constraint_str, cell2) in enumerate(imported.constraints[:3]):
    print(f"  {i+1}. {cell1.name}: {constraint_str}")
print()

print()

# ==============================================================================
# STEP 3: Modify Layout by Adding New Constraints
# ==============================================================================
print("STEP 3: Modify Layout - Move poly_gate 10 units to the right")
print("-" * 80)
print()

# Access specific child using child_dict
poly = imported.child_dict['INVERTER_poly_0']
print(f"Found poly gate: {poly.name}")
print(f"  Original constraint in imported: {[c for c in imported.constraints if c[0] == poly][0][1]}")
print()

# Add new constraint to move it
# The new constraint will override the original position constraint
print("Adding new constraint: x1=30 (moved from 20)")
imported.constrain(poly, 'x1=30, y1=5, x2=40, y2=35')

print()

# ==============================================================================
# STEP 4: Re-solve with Minimal Changes
# ==============================================================================
print("STEP 4: Re-solve Layout")
print("-" * 80)
print()

print("Re-solving with new constraint...")
print("  Other elements will try to stay at original positions")
print("  Only poly_gate will move significantly")
print()

if imported.solver():
    print("✓ Modified layout solved")
    print()

    # Compare positions
    print("Position comparison:")
    print(f"  poly_gate original: [20, 5, 30, 35]")

    # Find the poly in imported cell
    for child in imported.children:
        if 'poly' in child.name.lower():
            print(f"  poly_gate modified: {child.pos_list}")
            break

    print()

    # Display modified tree
    print("Modified layout structure:")
    imported.tree(show_positions=True, show_layers=True)
    print()

else:
    print("✗ Modified layout solver failed")

print()

# ==============================================================================
# STEP 5: Export Modified Layout
# ==============================================================================
print("STEP 5: Export Modified Layout")
print("-" * 80)
print()

modified_gds = 'demo_outputs/modified_inverter.gds'
imported.export_gds(modified_gds)
print(f"✓ Exported modified layout to {modified_gds}")
print()

# ==============================================================================
# STEP 6: Demonstrate Without Position Constraints
# ==============================================================================
print("STEP 6: Import Without Position Constraints (for comparison)")
print("-" * 80)
print()

print("Importing without automatic position constraints...")
imported_no_constraints = Cell.import_gds_to_cell(gds_file, add_position_constraints=False)

print(f"  Constraints added: {len(imported_no_constraints.constraints)}")
print("  Without constraints, solver would place elements anywhere")
print()

# Try to solve without position constraints - elements can move freely
print("Adding manual constraint to see effect:")
imported_no_constraints.constrain('x2-x1>=100, y2-y1>=100')  # Make it big

if imported_no_constraints.solver():
    print("✓ Solved without position constraints")
    print("  Elements repositioned to satisfy size constraint:")
    imported_no_constraints.tree(show_positions=True, show_layers=True)
else:
    print("✗ Solver failed")

print()
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("SUMMARY: import_gds_to_cell METHOD")
print("=" * 80)
print()
print("Key Features:")
print()
print("1. Import with Position Constraints (add_position_constraints=True):")
print("   - Automatically adds constraints: x1=X, y1=Y, x2=X2, y2=Y2")
print("   - Elements try to stay at original positions")
print("   - New constraints override original positions")
print("   - Other elements minimize movement")
print()
print("2. Workflow for Layout Modification:")
print("   a) Import: cell = Cell.import_gds_to_cell('layout.gds')")
print("   b) Access: element = cell.child_dict['element_name']")
print("   c) Modify: cell.constrain(element, 'new_constraint')")
print("   d) Solve: cell.solver()")
print("   e) Export: cell.export_gds('modified.gds')")
print()
print("3. Use Cases:")
print("   - Incremental layout modifications")
print("   - Design rule fix-ups")
print("   - Adding new elements to existing design")
print("   - Automated layout adjustments")
print()
print("Files Generated:")
print("  - demo_outputs/original_inverter.gds")
print("  - demo_outputs/modified_inverter.gds")
print()
print("=" * 80)
