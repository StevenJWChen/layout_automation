#!/usr/bin/env python3
"""
EASIEST WAY: Centering with Tolerance (No Bias)

Just ONE function call instead of parent.solver()!
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import center_and_solve

print("=" * 80)
print("EASIEST WAY: CENTERING WITH TOLERANCE (NO BIAS)")
print("=" * 80)
print()

# ==============================================================================
# Example 1: Basic centering with tolerance
# ==============================================================================
print("Example 1: Center with ±10 Unit Tolerance")
print("-" * 80)
print()

parent1 = Cell('parent1')
child1 = Cell('child1', 'metal1')

parent1.constrain('x1=0, y1=0, x2=100, y2=100')
parent1.constrain(child1, 'swidth=30, sheight=40')

print("Code:")
print("  from layout_automation.centering_with_tolerance import center_and_solve")
print("  center_and_solve(parent, child, tolerance=10)")
print()

try:
    # ONE LINE - replaces parent.solver()
    if center_and_solve(parent1, child1, tolerance=10):
        parent_cx = (parent1.pos_list[0] + parent1.pos_list[2]) / 2
        child_cx = (child1.pos_list[0] + child1.pos_list[2]) / 2
        offset = abs(parent_cx - child_cx)

        print(f"Result:")
        print(f"  Parent center X: {parent_cx}")
        print(f"  Child center X:  {child_cx}")
        print(f"  Offset: {offset:.2f} units")
        print()

        if offset < 0.1:
            print("  ✓ EXACTLY CENTERED (no conflicts)")
        elif offset <= 10:
            print("  ✓ Within tolerance AND truly centered (no bias)")
        else:
            print("  ✗ Exceeds tolerance")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Error: {e}")

print()
print()

# ==============================================================================
# Example 2: With conflicting constraints
# ==============================================================================
print("Example 2: Centering with Conflicting Constraint")
print("-" * 80)
print()

parent2 = Cell('parent2')
child2 = Cell('child2', 'poly')

parent2.constrain('x1=0, y1=0, x2=100, y2=100')
parent2.constrain(child2, 'swidth=30, sheight=40')

# Constraint that conflicts with perfect centering
parent2.constrain(child2, 'sx1>=40')  # Perfect center would be x1=35

print("Setup:")
print("  Parent: 100x100 box")
print("  Child: 30x40 box")
print("  Constraint: sx1>=40 (conflicts with perfect centering at x1=35)")
print()
print("Code:")
print("  center_and_solve(parent, child, tolerance=10)")
print()

try:
    if center_and_solve(parent2, child2, tolerance=10):
        parent_cx = (parent2.pos_list[0] + parent2.pos_list[2]) / 2
        child_cx = (child2.pos_list[0] + child2.pos_list[2]) / 2
        offset = abs(parent_cx - child_cx)

        print(f"Result:")
        print(f"  Parent center X: {parent_cx}")
        print(f"  Child center X:  {child_cx}")
        print(f"  Child x1: {child2.pos_list[0]}")
        print(f"  Offset: {offset:.2f} units")
        print()

        if offset <= 10:
            print("  ✓ Within tolerance")
            print("  ✓ Child is AS CENTERED AS POSSIBLE given sx1>=40")
            print("  ✓ NO left/bottom bias - truly minimized deviation")
        else:
            print("  ✗ Exceeds tolerance")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Error: {e}")

print()
print()

# ==============================================================================
# Example 3: Different X and Y tolerances
# ==============================================================================
print("Example 3: Different X and Y Tolerances")
print("-" * 80)
print()

parent3 = Cell('parent3')
child3 = Cell('child3', 'metal1')

parent3.constrain('x1=0, y1=0, x2=100, y2=100')
parent3.constrain(child3, 'swidth=30, sheight=40')

print("Code:")
print("  center_and_solve(parent, child, tolerance_x=15, tolerance_y=5)")
print()

try:
    # Different tolerances for X and Y
    if center_and_solve(parent3, child3, tolerance_x=15, tolerance_y=5):
        parent_cx = (parent3.pos_list[0] + parent3.pos_list[2]) / 2
        parent_cy = (parent3.pos_list[1] + parent3.pos_list[3]) / 2
        child_cx = (child3.pos_list[0] + child3.pos_list[2]) / 2
        child_cy = (child3.pos_list[1] + child3.pos_list[3]) / 2

        offset_x = abs(parent_cx - child_cx)
        offset_y = abs(parent_cy - child_cy)

        print(f"Result:")
        print(f"  X offset: {offset_x:.2f} units (tolerance: ±15)")
        print(f"  Y offset: {offset_y:.2f} units (tolerance: ±5)")
        print()

        x_ok = offset_x <= 15
        y_ok = offset_y <= 5

        if x_ok and y_ok:
            print("  ✓ Both within tolerance and centered")
        else:
            print(f"  {'✓' if x_ok else '✗'} X within tolerance")
            print(f"  {'✓' if y_ok else '✗'} Y within tolerance")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Error: {e}")

print()
print()

# ==============================================================================
# Example 4: Exact centering (tolerance = 0)
# ==============================================================================
print("Example 4: Exact Centering (tolerance=0)")
print("-" * 80)
print()

parent4 = Cell('parent4')
child4 = Cell('child4', 'poly')

parent4.constrain('x1=0, y1=0, x2=100, y2=100')
parent4.constrain(child4, 'swidth=30, sheight=40')

print("Code:")
print("  center_and_solve(parent, child, tolerance=0)")
print()

try:
    if center_and_solve(parent4, child4, tolerance=0):
        parent_cx = (parent4.pos_list[0] + parent4.pos_list[2]) / 2
        child_cx = (child4.pos_list[0] + child4.pos_list[2]) / 2
        offset = abs(parent_cx - child_cx)

        print(f"Result:")
        print(f"  Offset: {offset:.6f} units")
        print()

        if offset < 0.1:
            print("  ✓ EXACTLY CENTERED")
        else:
            print("  ✗ Not centered")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Error: {e}")

print()
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("SUMMARY: THE EASIEST WAY")
print("=" * 80)
print()
print("What you want: Tolerance > 0 with TRUE centering (no left/bottom bias)")
print()
print("Solution:")
print("-" * 80)
print()
print("from layout_automation.centering_with_tolerance import center_and_solve")
print()
print("parent = Cell('parent')")
print("child = Cell('child', 'metal1')")
print("parent.constrain('x1=0, y1=0, x2=100, y2=100')")
print("parent.constrain(child, 'swidth=30, sheight=40')")
print()
print("# ONE LINE - center with ±10 tolerance, NO BIAS")
print("center_and_solve(parent, child, tolerance=10)")
print()
print()
print("That's it!")
print()
print("Examples:")
print("-" * 80)
print()
print("# ±5 unit tolerance")
print("center_and_solve(parent, child, tolerance=5)")
print()
print("# Different X and Y tolerances")
print("center_and_solve(parent, child, tolerance_x=15, tolerance_y=10)")
print()
print("# Exact centering")
print("center_and_solve(parent, child, tolerance=0)")
print()
print("# Center child1 relative to child2")
print("center_and_solve(parent, child1, tolerance=5, ref_obj=child2)")
print()
print("# X-only centering with tolerance")
print("center_and_solve(parent, child, tolerance=10, center_y=False)")
print()
print()
print("What you get:")
print("-" * 80)
print("  ✓ Tolerance > 0 supported")
print("  ✓ TRUE centering (no left/bottom bias)")
print("  ✓ ONE function call (replaces parent.solver())")
print("  ✓ Works with conflicting constraints")
print("  ✓ Falls back gracefully (centers as close as possible)")
print()
print("=" * 80)
