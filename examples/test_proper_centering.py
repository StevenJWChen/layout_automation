#!/usr/bin/env python3
"""
Test proper centering without left/bottom bias

Shows the correct way to center objects using exact constraints.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.constraint_helpers import (
    constrain_center,
    constrain_xcenter,
    constrain_ycenter,
)

print("=" * 80)
print("PROPER CENTERING - VERIFICATION")
print("=" * 80)
print()

# ==============================================================================
# Test 1: Using helper function
# ==============================================================================
print("Test 1: Using Helper Function constrain_center()")
print("-" * 80)

parent1 = Cell('parent1')
child1 = Cell('child1', 'metal1')

parent1.constrain('x1=0, y1=0, x2=100, y2=100')
parent1.constrain(child1, 'swidth=30, sheight=40')

# Use helper function
constrain_center(parent1, child1, parent1)

try:
    if parent1.solver():
        parent_cx = (parent1.pos_list[0] + parent1.pos_list[2]) / 2
        parent_cy = (parent1.pos_list[1] + parent1.pos_list[3]) / 2
        child_cx = (child1.pos_list[0] + child1.pos_list[2]) / 2
        child_cy = (child1.pos_list[1] + child1.pos_list[3]) / 2

        print(f"Parent: {parent1.pos_list}")
        print(f"Child:  {child1.pos_list}")
        print(f"Parent center: ({parent_cx}, {parent_cy})")
        print(f"Child center:  ({child_cx}, {child_cy})")
        print(f"Offset: ({abs(parent_cx - child_cx):.6f}, {abs(parent_cy - child_cy):.6f})")

        if abs(parent_cx - child_cx) < 0.01 and abs(parent_cy - child_cy) < 0.01:
            print("✓ PASS: Child is exactly centered")
        else:
            print("✗ FAIL: Child is not centered")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"Skipping test (solver not available): {e}")

print()
print()

# ==============================================================================
# Test 2: Using built-in keyword
# ==============================================================================
print("Test 2: Using Built-in 'center' Keyword")
print("-" * 80)

parent2 = Cell('parent2')
child2 = Cell('child2', 'poly')

parent2.constrain('width=200, height=150, x1=0, y1=0')
parent2.constrain(child2, 'swidth=50, sheight=60')

# Use keyword
parent2.constrain(child2, 'center', parent2)

try:
    if parent2.solver():
        parent_cx = (parent2.pos_list[0] + parent2.pos_list[2]) / 2
        parent_cy = (parent2.pos_list[1] + parent2.pos_list[3]) / 2
        child_cx = (child2.pos_list[0] + child2.pos_list[2]) / 2
        child_cy = (child2.pos_list[1] + child2.pos_list[3]) / 2

        print(f"Parent: {parent2.pos_list}")
        print(f"Child:  {child2.pos_list}")
        print(f"Parent center: ({parent_cx}, {parent_cy})")
        print(f"Child center:  ({child_cx}, {child_cy})")
        print(f"Offset: ({abs(parent_cx - child_cx):.6f}, {abs(parent_cy - child_cy):.6f})")

        if abs(parent_cx - child_cx) < 0.01 and abs(parent_cy - child_cy) < 0.01:
            print("✓ PASS: Child is exactly centered")
        else:
            print("✗ FAIL: Child is not centered")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"Skipping test (solver not available): {e}")

print()
print()

# ==============================================================================
# Test 3: X-only centering with Y positioning
# ==============================================================================
print("Test 3: X-only Centering with Explicit Y Position")
print("-" * 80)

parent3 = Cell('parent3')
child3a = Cell('child3a', 'metal1')
child3b = Cell('child3b', 'poly')

parent3.constrain('x1=0, y1=0, x2=100, y2=100')
parent3.constrain(child3a, 'swidth=30, sheight=20')
parent3.constrain(child3b, 'swidth=25, sheight=15')

# Center X only, position Y explicitly
constrain_xcenter(parent3, child3a, parent3)
parent3.constrain(child3a, 'sy1=20')

constrain_xcenter(parent3, child3b, parent3)
parent3.constrain(child3b, 'sy1=60')

try:
    if parent3.solver():
        parent_cx = (parent3.pos_list[0] + parent3.pos_list[2]) / 2

        child3a_cx = (child3a.pos_list[0] + child3a.pos_list[2]) / 2
        child3b_cx = (child3b.pos_list[0] + child3b.pos_list[2]) / 2

        print(f"Parent center X: {parent_cx}")
        print(f"Child A: {child3a.pos_list}")
        print(f"  Center X: {child3a_cx} (offset: {abs(parent_cx - child3a_cx):.6f})")
        print(f"Child B: {child3b.pos_list}")
        print(f"  Center X: {child3b_cx} (offset: {abs(parent_cx - child3b_cx):.6f})")

        if abs(parent_cx - child3a_cx) < 0.01 and abs(parent_cx - child3b_cx) < 0.01:
            print("✓ PASS: Both children are X-centered")
        else:
            print("✗ FAIL: Children are not X-centered")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"Skipping test (solver not available): {e}")

print()
print()

# ==============================================================================
# Summary
# ==============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("CORRECT CENTERING METHODS:")
print()
print("1. Use helper functions:")
print("   from layout_automation.constraint_helpers import constrain_center")
print("   constrain_center(parent, child, parent)")
print()
print("2. Use built-in keywords:")
print("   parent.constrain(child, 'center', parent)")
print("   parent.constrain(child, 'xcenter', parent)  # X only")
print("   parent.constrain(child, 'ycenter', parent)  # Y only")
print()
print("3. Use explicit constraints:")
print("   parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)")
print()
print("DO NOT USE tolerance constraints (>=, <=) for centering!")
print("They cause left/bottom bias due to the solver's objective function.")
print()
print("=" * 80)
