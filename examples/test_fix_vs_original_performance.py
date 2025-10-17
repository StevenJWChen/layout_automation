"""
Performance comparison: fix_layout vs original cell approach

This test creates arrays of cells using two methods:
1. Original: Create unique cells for each instance, solve entire hierarchy
2. Fix layout: Create once, fix, then copy and position manually

Verification:
- Check that all positions match exactly (array of array of array)
- Measure and compare runtime performance
- Test with increasing complexity (2x2, 4x4, 8x8 arrays)
"""

import os
import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell


def create_base_cell(name):
    """Create a base cell with internal structure"""
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


def collect_all_positions(cell, prefix=""):
    """Recursively collect all cell and polygon positions"""
    positions = {}

    # Add this cell's position
    if hasattr(cell, 'pos_list') and all(v is not None for v in cell.pos_list):
        positions[f"{prefix}{cell.name}"] = tuple(cell.pos_list)

    # Recursively collect children
    if hasattr(cell, 'children'):
        for child in cell.children:
            if not child.is_leaf or (hasattr(child, 'pos_list') and all(v is not None for v in child.pos_list)):
                child_positions = collect_all_positions(child, f"{prefix}{cell.name}.")
                positions.update(child_positions)

    return positions


def test_original_approach(rows, cols, spacing):
    """
    Original approach: Create unique cells for each position and solve the entire hierarchy
    """
    print(f"\n{'='*70}")
    print(f"ORIGINAL APPROACH: {rows}x{cols} array")
    print(f"{'='*70}")

    start_time = time.time()

    # Create top-level cell
    top = Cell('top_original')

    # Create array of cells
    cells = []
    for row in range(rows):
        row_cells = []
        for col in range(cols):
            # Create a unique cell for each position
            cell = create_base_cell(f'cell_r{row}_c{col}')
            top.add_instance(cell)

            # Calculate position
            x = col * spacing
            y = row * spacing

            # Add constraint for position
            top.constrain(cell, f'x1={x}, y1={y}')

            row_cells.append(cell)
        cells.append(row_cells)

    creation_time = time.time() - start_time
    print(f"   Cell creation time: {creation_time:.4f}s")

    # Solve the entire hierarchy
    solve_start = time.time()
    success = top.solver()
    solve_time = time.time() - solve_start

    total_time = time.time() - start_time

    print(f"   Solve time: {solve_time:.4f}s")
    print(f"   Total time: {total_time:.4f}s")
    print(f"   Solver status: {'✓ SUCCESS' if success else '✗ FAILED'}")

    if not success:
        return None, None, None

    # Collect all positions
    positions = collect_all_positions(top)
    print(f"   Total objects positioned: {len(positions)}")

    return cells, positions, total_time


def test_fix_layout_approach(rows, cols, spacing):
    """
    Fix layout approach: Create once, fix, then copy and position manually
    """
    print(f"\n{'='*70}")
    print(f"FIX_LAYOUT APPROACH: {rows}x{cols} array")
    print(f"{'='*70}")

    start_time = time.time()

    # Create template cell once and fix it
    template = create_base_cell('template')
    template.solver()
    template.fix_layout()

    template_time = time.time() - start_time
    print(f"   Template creation and fix time: {template_time:.4f}s")

    # Create top-level cell
    top = Cell('top_fixed')

    # Create array by copying and positioning
    copy_start = time.time()
    cells = []
    for row in range(rows):
        row_cells = []
        for col in range(cols):
            # Copy the fixed template
            cell = template.copy(f'cell_r{row}_c{col}')
            top.add_instance(cell)

            # Calculate and set position directly (no solver needed!)
            x = col * spacing
            y = row * spacing
            cell.set_position(x, y)

            row_cells.append(cell)
        cells.append(row_cells)

    copy_time = time.time() - copy_start
    total_time = time.time() - start_time

    print(f"   Copy and position time: {copy_time:.4f}s")
    print(f"   Total time: {total_time:.4f}s")
    print(f"   No solver needed! ✓")

    # Collect all positions
    positions = collect_all_positions(top)
    print(f"   Total objects positioned: {len(positions)}")

    return cells, positions, total_time


def compare_positions(orig_positions, fixed_positions, tolerance=1e-9):
    """
    Compare two position dictionaries to verify they match exactly
    """
    print(f"\n{'='*70}")
    print("POSITION COMPARISON")
    print(f"{'='*70}")

    # Normalize names (remove 'top_original.' and 'top_fixed.' prefixes)
    def normalize_name(name):
        if name.startswith('top_original.'):
            return name[13:]  # Remove 'top_original.'
        elif name.startswith('top_fixed.'):
            return name[10:]  # Remove 'top_fixed.'
        return name

    orig_norm = {normalize_name(k): v for k, v in orig_positions.items()}
    fixed_norm = {normalize_name(k): v for k, v in fixed_positions.items()}

    # Find common keys (excluding the top-level cell itself)
    orig_keys = {k for k in orig_norm.keys() if not k.startswith('top_')}
    fixed_keys = {k for k in fixed_norm.keys() if not k.startswith('top_')}

    common_keys = orig_keys & fixed_keys
    orig_only = orig_keys - fixed_keys
    fixed_only = fixed_keys - orig_keys

    print(f"   Original approach: {len(orig_keys)} objects")
    print(f"   Fix layout approach: {len(fixed_keys)} objects")
    print(f"   Common objects: {len(common_keys)}")

    if orig_only:
        print(f"   ⚠ Objects only in original: {len(orig_only)}")
    if fixed_only:
        print(f"   ⚠ Objects only in fixed: {len(fixed_only)}")

    # Compare positions for common objects
    mismatches = []
    matches = 0

    for key in sorted(common_keys):
        orig_pos = orig_norm[key]
        fixed_pos = fixed_norm[key]

        # Check if positions match within tolerance
        if all(abs(o - f) < tolerance for o, f in zip(orig_pos, fixed_pos)):
            matches += 1
        else:
            mismatches.append((key, orig_pos, fixed_pos))

    print(f"\n   Exact matches: {matches}/{len(common_keys)}")

    if mismatches:
        print(f"   ✗ MISMATCHES FOUND: {len(mismatches)}")
        print(f"\n   First 5 mismatches:")
        for key, orig, fixed in mismatches[:5]:
            print(f"      {key}:")
            print(f"         Original: {orig}")
            print(f"         Fixed:    {fixed}")
            print(f"         Diff:     {tuple(f-o for o, f in zip(orig, fixed))}")
        return False
    else:
        print(f"   ✓ ALL POSITIONS MATCH EXACTLY!")
        return True


def run_comparison(rows, cols, spacing=30):
    """Run comparison for a specific array size"""
    print(f"\n{'#'*70}")
    print(f"# COMPARISON: {rows}x{cols} Array (spacing={spacing})")
    print(f"{'#'*70}")

    # Test original approach
    orig_cells, orig_positions, orig_time = test_original_approach(rows, cols, spacing)

    if orig_positions is None:
        print("\n✗ Original approach failed, skipping comparison")
        return None

    # Test fix_layout approach
    fixed_cells, fixed_positions, fixed_time = test_fix_layout_approach(rows, cols, spacing)

    # Compare positions
    match = compare_positions(orig_positions, fixed_positions)

    # Performance comparison
    print(f"\n{'='*70}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*70}")
    print(f"   Original approach:   {orig_time:.4f}s")
    print(f"   Fix layout approach: {fixed_time:.4f}s")

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
    """Run comprehensive comparison tests"""
    print(f"\n{'#'*70}")
    print("# FIX_LAYOUT vs ORIGINAL: COMPREHENSIVE COMPARISON")
    print(f"{'#'*70}")

    # Test different array sizes
    test_configs = [
        (2, 2, 30),   # Small: 2x2 array
        (3, 3, 30),   # Medium: 3x3 array
        (4, 4, 30),   # Large: 4x4 array
        (5, 5, 30),   # Very large: 5x5 array
    ]

    results = []

    for rows, cols, spacing in test_configs:
        result = run_comparison(rows, cols, spacing)
        if result:
            results.append(result)

    # Summary
    print(f"\n{'#'*70}")
    print("# SUMMARY")
    print(f"{'#'*70}")

    print(f"\n{'Array Size':<12} {'Original':<12} {'Fix Layout':<12} {'Speedup':<12} {'Match':<8}")
    print(f"{'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*8}")

    for r in results:
        size = f"{r['rows']}x{r['cols']}"
        orig_time = f"{r['orig_time']:.4f}s"
        fixed_time = f"{r['fixed_time']:.4f}s"
        speedup = f"{r['speedup']:.2f}x"
        match = "✓ YES" if r['match'] else "✗ NO"

        print(f"{size:<12} {orig_time:<12} {fixed_time:<12} {speedup:<12} {match:<8}")

    # Overall conclusion
    all_match = all(r['match'] for r in results)
    avg_speedup = sum(r['speedup'] for r in results) / len(results) if results else 0

    print(f"\n{'='*70}")
    if all_match:
        print("✓ ALL TESTS PASSED: Positions match exactly!")
    else:
        print("✗ SOME TESTS FAILED: Position mismatches detected")

    print(f"\nAverage speedup: {avg_speedup:.2f}x")
    print(f"{'='*70}")

    return all_match


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
