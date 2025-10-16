#!/usr/bin/env python3
"""
Test GDS round-trip: export → import → export → compare

Verifies that:
1. GDS export creates valid files
2. GDS import correctly reads all data
3. Re-exporting produces identical layout
4. Positions and layers are preserved
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
import gdstk

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)


def create_test_layout(name):
    """Create a test layout with hierarchy"""
    top = Cell(name)

    # Create some layers
    metal1_a = Cell('metal1_layer_a', 'metal1')
    metal1_b = Cell('metal1_layer_b', 'metal1')
    poly = Cell('poly_layer', 'poly')
    diff = Cell('diff_layer', 'diff')
    contact = Cell('contact_layer', 'contact')

    # Add to hierarchy
    top.add_instance([metal1_a, metal1_b, poly, diff, contact])

    # Add constraints
    top.constrain(metal1_a, 'x1=0, y1=0, x2=20, y2=10')
    top.constrain(metal1_b, 'x1=25, y1=0, x2=45, y2=10')
    top.constrain(poly, 'x1=10, y1=5, x2=15, y2=25')
    top.constrain(diff, 'x1=5, y1=12, x2=40, y2=20')
    top.constrain(contact, 'x1=12, y1=8, x2=14, y2=12')

    # Solve
    if not top.solver():
        raise RuntimeError("Solver failed")

    return top


def compare_gds_files(file1, file2):
    """
    Compare two GDS files by reading their contents

    Returns:
        (bool, str): (files_match, difference_message)
    """
    lib1 = gdstk.read_gds(file1)
    lib2 = gdstk.read_gds(file2)

    differences = []

    # Compare number of cells
    if len(lib1.cells) != len(lib2.cells):
        differences.append(f"Different number of cells: {len(lib1.cells)} vs {len(lib2.cells)}")
        return False, "\n".join(differences)

    # Compare each cell
    cells1 = {cell.name: cell for cell in lib1.cells}
    cells2 = {cell.name: cell for cell in lib2.cells}

    # Check cell names match
    if set(cells1.keys()) != set(cells2.keys()):
        diff_cells = set(cells1.keys()).symmetric_difference(set(cells2.keys()))
        differences.append(f"Different cell names: {diff_cells}")
        return False, "\n".join(differences)

    # Compare each cell's contents
    for cell_name in cells1:
        cell1 = cells1[cell_name]
        cell2 = cells2[cell_name]

        # Compare polygons
        if len(cell1.polygons) != len(cell2.polygons):
            differences.append(f"Cell '{cell_name}': different polygon count: {len(cell1.polygons)} vs {len(cell2.polygons)}")
            continue

        # Compare each polygon
        for i, (poly1, poly2) in enumerate(zip(cell1.polygons, cell2.polygons)):
            # Compare layer
            if poly1.layer != poly2.layer or poly1.datatype != poly2.datatype:
                differences.append(f"Cell '{cell_name}', polygon {i}: different layer ({poly1.layer},{poly1.datatype}) vs ({poly2.layer},{poly2.datatype})")

            # Compare points
            points1 = poly1.points
            points2 = poly2.points

            if len(points1) != len(points2):
                differences.append(f"Cell '{cell_name}', polygon {i}: different point count: {len(points1)} vs {len(points2)}")
                continue

            # Compare coordinates (allow small floating point differences)
            for j, (p1, p2) in enumerate(zip(points1, points2)):
                if abs(p1[0] - p2[0]) > 1e-6 or abs(p1[1] - p2[1]) > 1e-6:
                    differences.append(f"Cell '{cell_name}', polygon {i}, point {j}: ({p1[0]},{p1[1]}) vs ({p2[0]},{p2[1]})")

        # Compare references (cell instances)
        if len(cell1.references) != len(cell2.references):
            differences.append(f"Cell '{cell_name}': different reference count: {len(cell1.references)} vs {len(cell2.references)}")

    if differences:
        return False, "\n".join(differences)

    return True, "GDS files are identical"


def compare_cell_hierarchies(cell1, cell2):
    """Compare two Cell hierarchies"""
    differences = []

    # Compare names
    if cell1.name != cell2.name:
        differences.append(f"Different names: {cell1.name} vs {cell2.name}")

    # Compare positions
    if cell1.pos_list != cell2.pos_list:
        differences.append(f"Cell '{cell1.name}': different positions: {cell1.pos_list} vs {cell2.pos_list}")

    # Compare layers
    if cell1.layer_name != cell2.layer_name:
        differences.append(f"Cell '{cell1.name}': different layers: {cell1.layer_name} vs {cell2.layer_name}")

    # Compare number of children
    if len(cell1.children) != len(cell2.children):
        differences.append(f"Cell '{cell1.name}': different child count: {len(cell1.children)} vs {len(cell2.children)}")
        return False, "\n".join(differences)

    # Recursively compare children (by name since order might differ)
    children1_dict = {c.name: c for c in cell1.children}
    children2_dict = {c.name: c for c in cell2.children}

    if set(children1_dict.keys()) != set(children2_dict.keys()):
        differences.append(f"Cell '{cell1.name}': different child names")
        return False, "\n".join(differences)

    for child_name in children1_dict:
        match, msg = compare_cell_hierarchies(children1_dict[child_name], children2_dict[child_name])
        if not match:
            differences.append(msg)

    if differences:
        return False, "\n".join(differences)

    return True, "Cell hierarchies are identical"


def main():
    print("=" * 80)
    print("GDS ROUND-TRIP TEST")
    print("=" * 80)
    print()
    print("This test verifies that:")
    print("  1. Export GDS creates valid files")
    print("  2. Import GDS reads all data correctly")
    print("  3. Re-export produces identical layout")
    print()

    # ==============================================================================
    # STEP 1: Create original layout
    # ==============================================================================
    print("=" * 80)
    print("STEP 1: Create Original Layout")
    print("=" * 80)
    print()

    original = create_test_layout('ROUNDTRIP_TEST')
    print(f"✓ Created layout: {original.name}")
    print(f"  Cells: {len(original.children)}")
    print(f"  Bbox: {original.pos_list}")
    print()

    # Display structure
    print("Original structure:")
    original.tree(show_positions=True, show_layers=True)
    print()

    # ==============================================================================
    # STEP 2: Export to GDS (first export)
    # ==============================================================================
    print("=" * 80)
    print("STEP 2: Export to GDS")
    print("=" * 80)
    print()

    original_gds = 'demo_outputs/roundtrip_original.gds'
    original.export_gds(original_gds)
    print(f"✓ Exported to: {original_gds}")

    # Check file exists and has size
    if os.path.exists(original_gds):
        size = os.path.getsize(original_gds)
        print(f"  File size: {size} bytes")
    else:
        print("✗ Export failed - file not created")
        return False
    print()

    # ==============================================================================
    # STEP 3: Import from GDS
    # ==============================================================================
    print("=" * 80)
    print("STEP 3: Import from GDS")
    print("=" * 80)
    print()

    # Import using from_gds
    imported = Cell.from_gds(original_gds)
    print(f"✓ Imported cell: {imported.name}")
    print(f"  Cells: {len(imported.children)}")
    print(f"  Bbox: {imported.pos_list}")
    print()

    # Display imported structure
    print("Imported structure:")
    imported.tree(show_positions=True, show_layers=True)
    print()

    # ==============================================================================
    # STEP 4: Compare Cell hierarchies
    # ==============================================================================
    print("=" * 80)
    print("STEP 4: Compare Cell Hierarchies")
    print("=" * 80)
    print()

    match, msg = compare_cell_hierarchies(original, imported)
    if match:
        print("✓ Cell hierarchies are IDENTICAL")
    else:
        print("✗ Cell hierarchies DIFFER:")
        for line in msg.split('\n'):
            print(f"  - {line}")
    print()

    # ==============================================================================
    # STEP 5: Re-export to GDS (second export)
    # ==============================================================================
    print("=" * 80)
    print("STEP 5: Re-export Imported Cell")
    print("=" * 80)
    print()

    reexported_gds = 'demo_outputs/roundtrip_reexported.gds'
    imported.export_gds(reexported_gds)
    print(f"✓ Re-exported to: {reexported_gds}")

    if os.path.exists(reexported_gds):
        size = os.path.getsize(reexported_gds)
        print(f"  File size: {size} bytes")
    else:
        print("✗ Re-export failed - file not created")
        return False
    print()

    # ==============================================================================
    # STEP 6: Compare GDS files
    # ==============================================================================
    print("=" * 80)
    print("STEP 6: Compare GDS Files")
    print("=" * 80)
    print()

    print(f"Comparing:")
    print(f"  Original:    {original_gds}")
    print(f"  Re-exported: {reexported_gds}")
    print()

    gds_match, gds_msg = compare_gds_files(original_gds, reexported_gds)

    if gds_match:
        print("✓ GDS FILES ARE IDENTICAL")
        print(f"  {gds_msg}")
    else:
        print("✗ GDS FILES DIFFER:")
        for line in gds_msg.split('\n'):
            print(f"  - {line}")
    print()

    # ==============================================================================
    # STEP 7: Detailed comparison
    # ==============================================================================
    print("=" * 80)
    print("STEP 7: Detailed Comparison")
    print("=" * 80)
    print()

    # Read both GDS files and show details
    lib1 = gdstk.read_gds(original_gds)
    lib2 = gdstk.read_gds(reexported_gds)

    print("Original GDS:")
    for cell in lib1.cells:
        print(f"  Cell: {cell.name}")
        print(f"    Polygons: {len(cell.polygons)}")
        for i, poly in enumerate(cell.polygons):
            print(f"      {i}: layer=({poly.layer},{poly.datatype}), points={len(poly.points)}")
    print()

    print("Re-exported GDS:")
    for cell in lib2.cells:
        print(f"  Cell: {cell.name}")
        print(f"    Polygons: {len(cell.polygons)}")
        for i, poly in enumerate(cell.polygons):
            print(f"      {i}: layer=({poly.layer},{poly.datatype}), points={len(poly.points)}")
    print()

    # ==============================================================================
    # STEP 8: Test with import_gds_to_cell
    # ==============================================================================
    print("=" * 80)
    print("STEP 8: Test import_gds_to_cell (with constraints)")
    print("=" * 80)
    print()

    imported_with_constraints = Cell.import_gds_to_cell(original_gds, add_position_constraints=True)
    print(f"✓ Imported with constraints: {imported_with_constraints.name}")
    print(f"  Constraints added: {len(imported_with_constraints.constraints)}")
    print()

    # Re-solve (should maintain same positions due to constraints)
    print("Re-solving with constraints...")
    if imported_with_constraints.solver():
        print("✓ Re-solved successfully")

        # Export
        constrained_gds = 'demo_outputs/roundtrip_constrained.gds'
        imported_with_constraints.export_gds(constrained_gds)
        print(f"✓ Exported constrained version to: {constrained_gds}")

        # Compare with original
        constrained_match, constrained_msg = compare_gds_files(original_gds, constrained_gds)
        if constrained_match:
            print("✓ Constrained re-export is IDENTICAL to original")
        else:
            print("⚠ Constrained re-export differs (may be due to constraint solver variations)")
    else:
        print("✗ Re-solve failed")
    print()

    # ==============================================================================
    # SUMMARY
    # ==============================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    print("Round-trip test results:")
    print(f"  1. Export original:        ✓")
    print(f"  2. Import GDS:             ✓")
    print(f"  3. Cell hierarchy match:   {'✓' if match else '✗'}")
    print(f"  4. Re-export imported:     ✓")
    print(f"  5. GDS files identical:    {'✓' if gds_match else '✗'}")
    print()

    if match and gds_match:
        print("✓ ROUND-TRIP TEST PASSED")
        print("  GDS export → import → export produces identical results")
    else:
        print("⚠ ROUND-TRIP TEST ISSUES DETECTED")
        if not match:
            print("  - Cell hierarchy differences found")
        if not gds_match:
            print("  - GDS file differences found")
    print()

    print("Files generated:")
    print(f"  - {original_gds} (original)")
    print(f"  - {reexported_gds} (re-exported)")
    print(f"  - {constrained_gds} (with constraints)")
    print()

    print("=" * 80)

    return match and gds_match


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
