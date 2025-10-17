"""
Detailed array-of-array-of-array verification

This test explicitly verifies the 3-level hierarchy structure:
- Top level: Array of cells (rows x cols)
- Middle level: Each cell contains multiple polygons
- Bottom level: Each polygon has 4 coordinates (x1, y1, x2, y2)

Structure: top[ row ][ col ][ polygon ][ coordinate ]
"""

import os
import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell


def create_test_cell(name):
    """Create a cell with 3 internal polygons"""
    cell = Cell(name)
    r1 = Cell(f'{name}_r1', 'metal1')
    r2 = Cell(f'{name}_r2', 'poly')
    r3 = Cell(f'{name}_r3', 'metal1')

    cell.add_instance([r1, r2, r3])
    cell.constrain(r1, 'x2-x1=10, y2-y1=10')
    cell.constrain(r2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=5, sy2-sy1=10', r1)
    cell.constrain(r3, 'sx1=ox1, sy1=oy2+2, sx2-sx1=17, sy2-sy1=5', r1)
    cell.constrain(r1, 'sx1=x1, sy1=y1')

    return cell


def build_array_structure_original(rows, cols, spacing):
    """
    Build array using original approach (solve everything)
    Returns: 3D array structure [row][col][polygon_idx] = [x1, y1, x2, y2]
    """
    print(f"\nOriginal approach: Building {rows}x{cols} array...")
    start_time = time.time()

    top = Cell('top')
    cell_array = []

    # Create array
    for row in range(rows):
        row_cells = []
        for col in range(cols):
            cell = create_test_cell(f'cell_r{row}_c{col}')
            top.add_instance(cell)

            x = col * spacing
            y = row * spacing
            top.constrain(cell, f'x1={x}, y1={y}')

            row_cells.append(cell)
        cell_array.append(row_cells)

    # Solve
    solve_start = time.time()
    success = top.solver()
    solve_time = time.time() - solve_start
    total_time = time.time() - start_time

    if not success:
        print("✗ Solver failed!")
        return None, None

    # Build 3D structure: [row][col][polygon] = [x1, y1, x2, y2]
    structure = []
    for row in range(rows):
        row_structure = []
        for col in range(cols):
            cell = cell_array[row][col]
            cell_polygons = []

            # Get all 3 polygons (r1, r2, r3)
            for polygon in cell.children:
                cell_polygons.append(list(polygon.pos_list))

            row_structure.append(cell_polygons)
        structure.append(row_structure)

    print(f"   ✓ Completed in {total_time:.4f}s (solve: {solve_time:.4f}s)")

    return structure, total_time


def build_array_structure_fixed(rows, cols, spacing):
    """
    Build array using fix_layout approach (copy and position manually)
    Returns: 3D array structure [row][col][polygon_idx] = [x1, y1, x2, y2]
    """
    print(f"\nFix_layout approach: Building {rows}x{cols} array...")
    start_time = time.time()

    # Create and fix template
    template = create_test_cell('template')
    template.solver()
    template.fix_layout()

    template_time = time.time() - start_time

    # Build array by copying
    top = Cell('top')
    cell_array = []

    for row in range(rows):
        row_cells = []
        for col in range(cols):
            cell = template.copy(f'cell_r{row}_c{col}')
            top.add_instance(cell)

            x = col * spacing
            y = row * spacing
            cell.set_position(x, y)  # No solver needed!

            row_cells.append(cell)
        cell_array.append(row_cells)

    total_time = time.time() - start_time

    # Build 3D structure: [row][col][polygon] = [x1, y1, x2, y2]
    structure = []
    for row in range(rows):
        row_structure = []
        for col in range(cols):
            cell = cell_array[row][col]
            cell_polygons = []

            # Get all 3 polygons (r1, r2, r3)
            for polygon in cell.children:
                cell_polygons.append(list(polygon.pos_list))

            row_structure.append(cell_polygons)
        structure.append(row_structure)

    print(f"   ✓ Completed in {total_time:.4f}s (no solver needed!)")

    return structure, total_time


def compare_3d_structures(orig, fixed, rows, cols, tolerance=1e-9):
    """
    Compare two 3D array structures element by element
    Structure: [row][col][polygon][coordinate]
    """
    print(f"\nComparing 3D array structures...")
    print(f"   Array size: {rows}x{cols}")
    print(f"   Polygons per cell: 3")
    print(f"   Coordinates per polygon: 4 (x1, y1, x2, y2)")

    total_cells = rows * cols
    total_polygons = total_cells * 3
    total_coordinates = total_polygons * 4

    print(f"   Total cells: {total_cells}")
    print(f"   Total polygons: {total_polygons}")
    print(f"   Total coordinates: {total_coordinates}")

    mismatches = []
    matches = 0

    # Compare every single coordinate
    for row in range(rows):
        for col in range(cols):
            for poly_idx in range(3):  # 3 polygons per cell
                orig_poly = orig[row][col][poly_idx]
                fixed_poly = fixed[row][col][poly_idx]

                for coord_idx in range(4):  # 4 coordinates per polygon
                    orig_val = orig_poly[coord_idx]
                    fixed_val = fixed_poly[coord_idx]

                    if abs(orig_val - fixed_val) < tolerance:
                        matches += 1
                    else:
                        mismatches.append({
                            'row': row,
                            'col': col,
                            'polygon': poly_idx,
                            'coord': ['x1', 'y1', 'x2', 'y2'][coord_idx],
                            'orig': orig_val,
                            'fixed': fixed_val,
                            'diff': fixed_val - orig_val
                        })

    print(f"\n   Exact matches: {matches}/{total_coordinates}")

    if mismatches:
        print(f"   ✗ MISMATCHES FOUND: {len(mismatches)}")
        print(f"\n   First 10 mismatches:")
        for i, m in enumerate(mismatches[:10]):
            print(f"      [{m['row']}][{m['col']}][poly{m['polygon']}].{m['coord']}:")
            print(f"         Original: {m['orig']}")
            print(f"         Fixed:    {m['fixed']}")
            print(f"         Diff:     {m['diff']}")
        return False
    else:
        print(f"   ✓ ALL {total_coordinates} COORDINATES MATCH EXACTLY!")
        return True


def print_sample_structure(structure, rows, cols, name):
    """Print a sample of the 3D structure"""
    print(f"\n{name} - Sample structure:")
    print(f"   structure[0][0] (cell at row 0, col 0):")
    for poly_idx, polygon in enumerate(structure[0][0]):
        print(f"      polygon[{poly_idx}]: {polygon}")

    if rows > 1 and cols > 1:
        print(f"   structure[1][1] (cell at row 1, col 1):")
        for poly_idx, polygon in enumerate(structure[1][1]):
            print(f"      polygon[{poly_idx}]: {polygon}")


def run_test(rows, cols, spacing=30):
    """Run comparison test for specific array size"""
    print(f"\n{'='*70}")
    print(f"TEST: {rows}x{cols} Array (spacing={spacing})")
    print(f"{'='*70}")

    # Build with original approach
    orig_structure, orig_time = build_array_structure_original(rows, cols, spacing)

    if orig_structure is None:
        print("\n✗ Original approach failed")
        return None

    # Build with fix_layout approach
    fixed_structure, fixed_time = build_array_structure_fixed(rows, cols, spacing)

    # Print sample structures
    print_sample_structure(orig_structure, rows, cols, "ORIGINAL")
    print_sample_structure(fixed_structure, rows, cols, "FIX_LAYOUT")

    # Compare structures
    match = compare_3d_structures(orig_structure, fixed_structure, rows, cols)

    # Performance summary
    print(f"\n{'='*70}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*70}")
    print(f"   Original:   {orig_time:.4f}s")
    print(f"   Fix layout: {fixed_time:.4f}s")

    if fixed_time < orig_time:
        speedup = orig_time / fixed_time
        print(f"   ✓ Fix layout is {speedup:.2f}x FASTER!")
    else:
        slowdown = fixed_time / orig_time
        print(f"   ✗ Fix layout is {slowdown:.2f}x slower")

    return {
        'rows': rows,
        'cols': cols,
        'orig_time': orig_time,
        'fixed_time': fixed_time,
        'speedup': orig_time / fixed_time if fixed_time > 0 else 0,
        'match': match
    }


def main():
    """Run comprehensive array-of-array-of-array verification"""
    print(f"\n{'#'*70}")
    print("# ARRAY-OF-ARRAY-OF-ARRAY VERIFICATION")
    print("# Structure: array[row][col][polygon][coordinate]")
    print(f"{'#'*70}")

    # Test different sizes
    test_configs = [
        (2, 2, 30),
        (3, 3, 30),
        (4, 4, 30),
    ]

    results = []

    for rows, cols, spacing in test_configs:
        result = run_test(rows, cols, spacing)
        if result:
            results.append(result)

    # Final summary
    print(f"\n{'#'*70}")
    print("# FINAL SUMMARY")
    print(f"{'#'*70}")

    print(f"\n{'Array':<10} {'Cells':<8} {'Polygons':<10} {'Coords':<10} {'Original':<12} {'Fixed':<12} {'Speedup':<10} {'Match'}")
    print(f"{'-'*10} {'-'*8} {'-'*10} {'-'*10} {'-'*12} {'-'*12} {'-'*10} {'-'*5}")

    for r in results:
        array_size = f"{r['rows']}x{r['cols']}"
        num_cells = r['rows'] * r['cols']
        num_polygons = num_cells * 3
        num_coords = num_polygons * 4
        orig_time = f"{r['orig_time']:.4f}s"
        fixed_time = f"{r['fixed_time']:.4f}s"
        speedup = f"{r['speedup']:.1f}x"
        match = "✓" if r['match'] else "✗"

        print(f"{array_size:<10} {num_cells:<8} {num_polygons:<10} {num_coords:<10} {orig_time:<12} {fixed_time:<12} {speedup:<10} {match}")

    # Conclusion
    all_match = all(r['match'] for r in results)
    avg_speedup = sum(r['speedup'] for r in results) / len(results) if results else 0

    print(f"\n{'='*70}")
    if all_match:
        print("✓ ALL COORDINATES MATCH EXACTLY!")
        print("  Every single position in the 3D array structure is identical.")
    else:
        print("✗ SOME MISMATCHES DETECTED")

    print(f"\nAverage speedup: {avg_speedup:.1f}x")
    print(f"{'='*70}")

    return all_match


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
