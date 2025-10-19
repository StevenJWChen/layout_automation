#!/usr/bin/env python3
"""
SIMPLEST WAY to use centering with tolerance

Just one method call!
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

print("=" * 80)
print("SIMPLE CENTERING - ONE METHOD CALL")
print("=" * 80)
print()

# ==============================================================================
# Example 1: Exact centering (tolerance = 0)
# ==============================================================================
print("Example 1: Exact Centering")
print("-" * 80)

parent1 = Cell('parent1')
child1 = Cell('child1', 'metal1')

parent1.constrain('x1=0, y1=0, x2=100, y2=100')
parent1.constrain(child1, 'swidth=30, sheight=40')

# ONE LINE - exact centering
parent1.center_with_tolerance(child1, tolerance=0)

print("Code:")
print("  parent.center_with_tolerance(child, tolerance=0)")
print()

try:
    if parent1.solver():
        parent_cx = (parent1.pos_list[0] + parent1.pos_list[2]) / 2
        child_cx = (child1.pos_list[0] + child1.pos_list[2]) / 2
        offset = abs(parent_cx - child_cx)

        print(f"Result: Child is {'exactly centered' if offset < 0.1 else 'NOT centered'}")
        print(f"  Offset: {offset:.6f} units")
except Exception as e:
    print(f"Skipped: {e}")

print()
print()

# ==============================================================================
# Example 2: Centering with tolerance (SIMPLE but has bias warning)
# ==============================================================================
print("Example 2: Centering with Tolerance (Simple Method)")
print("-" * 80)

parent2 = Cell('parent2')
child2 = Cell('child2', 'metal1')

parent2.constrain('x1=0, y1=0, x2=100, y2=100')
parent2.constrain(child2, 'swidth=30, sheight=40')

# ONE LINE - with tolerance
parent2.center_with_tolerance(child2, tolerance=10)

print("Code:")
print("  parent.center_with_tolerance(child, tolerance=10)")
print()
print("WARNING: This simple method may have left/bottom bias when tolerance > 0")
print()

try:
    if parent2.solver():
        parent_cx = (parent2.pos_list[0] + parent2.pos_list[2]) / 2
        child_cx = (child2.pos_list[0] + child2.pos_list[2]) / 2
        offset = abs(parent_cx - child_cx)

        print(f"Result: Child offset = {offset:.2f} units")
        if offset < 0.1:
            print("  ✓ Exactly centered")
        elif offset <= 10:
            print(f"  ⚠ Within tolerance but may be biased to left/bottom")
        else:
            print("  ✗ Exceeds tolerance")
except Exception as e:
    print(f"Skipped: {e}")

print()
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("SUMMARY: SIMPLEST WAY")
print("=" * 80)
print()
print("METHOD 1: One-line simple method (built-in)")
print("-" * 80)
print()
print("Exact centering (no tolerance):")
print("  parent.center_with_tolerance(child, tolerance=0)")
print("  parent.solver()")
print()
print("With tolerance (has left/bottom bias):")
print("  parent.center_with_tolerance(child, tolerance=10)")
print("  parent.solver()")
print()
print("Pros:")
print("  ✓ One line of code")
print("  ✓ Built into Cell class")
print("  ✓ Easy to use")
print()
print("Cons:")
print("  ✗ tolerance > 0 has left/bottom bias")
print()
print()

print("METHOD 2: Custom solver (no bias)")
print("-" * 80)
print()
print("from layout_automation.centering_with_tolerance import (")
print("    add_centering_with_tolerance,")
print("    solver_with_centering_objective,")
print(")")
print()
print("centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)")
print("solver_with_centering_objective(parent, [centering])")
print()
print("Pros:")
print("  ✓ No left/bottom bias")
print("  ✓ True centered solutions")
print()
print("Cons:")
print("  ✗ Requires import and custom solver call")
print()
print()

print("RECOMMENDATION:")
print("-" * 80)
print()
print("If tolerance = 0 (exact centering):")
print("  → Use simple method: parent.center_with_tolerance(child, tolerance=0)")
print()
print("If tolerance > 0 AND you need true centering:")
print("  → Use custom solver (see examples/demo_centering_with_tolerance_proper.py)")
print()
print("If tolerance > 0 AND left/bottom bias is acceptable:")
print("  → Use simple method: parent.center_with_tolerance(child, tolerance=10)")
print()
print("=" * 80)
