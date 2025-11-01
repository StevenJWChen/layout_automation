#!/usr/bin/env python3
"""
Debug test to identify position shifts in GDS save/load cycles.
This will help diagnose any remaining position shift issues.
"""

from layout_automation.cell import Cell
import os

def print_detailed_hierarchy(cell, indent=0, label=""):
    """Print detailed hierarchy with all position info"""
    prefix = "  " * indent
    leaf = f" [LEAF: {cell.layer_name}]" if cell.is_leaf else ""
    print(f"{prefix}{cell.name}{leaf}")
    print(f"{prefix}  pos_list: {cell.pos_list}")
    if hasattr(cell, 'x1'):
        print(f"{prefix}  bounds: ({cell.x1}, {cell.y1}) to ({cell.x2}, {cell.y2})")
        print(f"{prefix}  size: {cell.x2-cell.x1} x {cell.y2-cell.y1}")
    print(f"{prefix}  children: {len(cell.children)}")

    for child in cell.children:
        print_detailed_hierarchy(child, indent + 1)

def compare_positions(orig, imported, path=""):
    """Recursively compare positions between original and imported"""
    errors = []

    # Compare this cell
    if orig.name != imported.name:
        errors.append(f"{path}: Name mismatch: {orig.name} vs {imported.name}")

    for i in range(4):
        if orig.pos_list[i] is not None and imported.pos_list[i] is not None:
            diff = abs(orig.pos_list[i] - imported.pos_list[i])
            if diff > 0.01:
                errors.append(
                    f"{path}/{orig.name} pos[{i}]: {orig.pos_list[i]} -> {imported.pos_list[i]} (shift: {diff})"
                )

    # Compare children
    if len(orig.children) != len(imported.children):
        errors.append(f"{path}/{orig.name}: Child count mismatch: {len(orig.children)} vs {len(imported.children)}")
        return errors

    for i, (orig_child, imp_child) in enumerate(zip(orig.children, imported.children)):
        child_errors = compare_positions(orig_child, imp_child, f"{path}/{orig.name}")
        errors.extend(child_errors)

    return errors

def test_case_1_simple():
    """Simple case with absolute positioning"""
    print("\n" + "="*70)
    print("TEST CASE 1: Simple Absolute Positioning")
    print("="*70)

    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'metal2')

    top = Cell('top')
    top.add_instance([r1, r2])
    top.constrain(r1, 'x1=0, y1=0, x2=10, y2=10')
    top.constrain(r2, 'x1=20, y1=0, x2=30, y2=10')

    top.solver()
    print("\nOriginal:")
    print_detailed_hierarchy(top)

    # Save/Load cycle 1
    top.export_gds('test_shift_case1_iter0.gds', use_tech_file=False)
    loaded1 = Cell.from_gds('test_shift_case1_iter0.gds', use_tech_file=False)
    loaded1.solver()

    print("\nAfter 1st load:")
    print_detailed_hierarchy(loaded1)

    errors1 = compare_positions(top, loaded1)
    if errors1:
        print("\n✗ ERRORS after 1st cycle:")
        for err in errors1:
            print(f"  {err}")
    else:
        print("\n✓ No position shifts after 1st cycle")

    # Save/Load cycle 2
    loaded1.export_gds('test_shift_case1_iter1.gds', use_tech_file=False)
    loaded2 = Cell.from_gds('test_shift_case1_iter1.gds', use_tech_file=False)
    loaded2.solver()

    print("\nAfter 2nd load:")
    print_detailed_hierarchy(loaded2)

    errors2 = compare_positions(loaded1, loaded2)
    if errors2:
        print("\n✗ ERRORS after 2nd cycle:")
        for err in errors2:
            print(f"  {err}")
    else:
        print("\n✓ No position shifts after 2nd cycle")

    os.remove('test_shift_case1_iter0.gds')
    os.remove('test_shift_case1_iter1.gds')

def test_case_2_relative():
    """Case with relative positioning"""
    print("\n" + "="*70)
    print("TEST CASE 2: Relative Positioning (sx1=ox2+gap)")
    print("="*70)

    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'metal2')

    top = Cell('top')
    top.add_instance([r1, r2])
    top.constrain(r1, 'x1=0, y1=0, x2=10, y2=10')
    top.constrain(r2, 'sx1=ox2+5, sy1=oy1, swidth=10, sheight=10', r1)

    top.solver()
    print("\nOriginal:")
    print_detailed_hierarchy(top)

    # Save/Load cycle 1
    top.export_gds('test_shift_case2_iter0.gds', use_tech_file=False)
    loaded1 = Cell.from_gds('test_shift_case2_iter0.gds', use_tech_file=False)
    loaded1.solver()

    print("\nAfter 1st load:")
    print_detailed_hierarchy(loaded1)

    errors1 = compare_positions(top, loaded1)
    if errors1:
        print("\n✗ ERRORS after 1st cycle:")
        for err in errors1:
            print(f"  {err}")
    else:
        print("\n✓ No position shifts after 1st cycle")

    # Save/Load cycle 2
    loaded1.export_gds('test_shift_case2_iter1.gds', use_tech_file=False)
    loaded2 = Cell.from_gds('test_shift_case2_iter1.gds', use_tech_file=False)
    loaded2.solver()

    print("\nAfter 2nd load:")
    print_detailed_hierarchy(loaded2)

    errors2 = compare_positions(loaded1, loaded2)
    if errors2:
        print("\n✗ ERRORS after 2nd cycle:")
        for err in errors2:
            print(f"  {err}")
    else:
        print("\n✓ No position shifts after 2nd cycle")

    os.remove('test_shift_case2_iter0.gds')
    os.remove('test_shift_case2_iter1.gds')

def test_case_3_nested():
    """Case with nested hierarchy"""
    print("\n" + "="*70)
    print("TEST CASE 3: Nested Hierarchy")
    print("="*70)

    s1 = Cell('s1', 'metal1')
    s2 = Cell('s2', 'metal2')

    container = Cell('container')
    container.add_instance([s1, s2])
    container.constrain(s1, 'x1=0, y1=0, x2=10, y2=10')
    container.constrain(s2, 'sx1=ox2+2, sy1=oy1, swidth=10, sheight=10', s1)

    s3 = Cell('s3', 'poly')

    top = Cell('top')
    top.add_instance([container, s3])
    top.constrain(container, 'sx1=0, sy1=0')
    top.constrain(s3, 'sx1=ox2+5, sy1=oy1, swidth=10, sheight=10', container)

    top.solver()
    print("\nOriginal:")
    print_detailed_hierarchy(top)

    # Save/Load cycle 1
    top.export_gds('test_shift_case3_iter0.gds', use_tech_file=False)
    loaded1 = Cell.from_gds('test_shift_case3_iter0.gds', use_tech_file=False)
    loaded1.solver()

    print("\nAfter 1st load:")
    print_detailed_hierarchy(loaded1)

    errors1 = compare_positions(top, loaded1)
    if errors1:
        print("\n✗ ERRORS after 1st cycle:")
        for err in errors1:
            print(f"  {err}")
    else:
        print("\n✓ No position shifts after 1st cycle")

    # Save/Load cycle 2
    loaded1.export_gds('test_shift_case3_iter1.gds', use_tech_file=False)
    loaded2 = Cell.from_gds('test_shift_case3_iter1.gds', use_tech_file=False)
    loaded2.solver()

    print("\nAfter 2nd load:")
    print_detailed_hierarchy(loaded2)

    errors2 = compare_positions(loaded1, loaded2)
    if errors2:
        print("\n✗ ERRORS after 2nd cycle:")
        for err in errors2:
            print(f"  {err}")
    else:
        print("\n✓ No position shifts after 2nd cycle")

    # Cycle 3 to be thorough
    loaded2.export_gds('test_shift_case3_iter2.gds', use_tech_file=False)
    loaded3 = Cell.from_gds('test_shift_case3_iter2.gds', use_tech_file=False)
    loaded3.solver()

    errors3 = compare_positions(loaded2, loaded3)
    if errors3:
        print("\n✗ ERRORS after 3rd cycle:")
        for err in errors3:
            print(f"  {err}")
    else:
        print("\n✓ No position shifts after 3rd cycle")

    os.remove('test_shift_case3_iter0.gds')
    os.remove('test_shift_case3_iter1.gds')
    os.remove('test_shift_case3_iter2.gds')

def main():
    print("="*70)
    print("POSITION SHIFT DIAGNOSTIC TEST")
    print("="*70)
    print("\nThis test will check for position shifts across multiple")
    print("save/load cycles in various scenarios.")

    test_case_1_simple()
    test_case_2_relative()
    test_case_3_nested()

    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nIf you see position shifts, please share:")
    print("  1. Which test case shows the issue")
    print("  2. The specific error messages")
    print("  3. Your own code if it's different from these cases")

if __name__ == '__main__':
    main()
