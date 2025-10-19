#!/usr/bin/env python3
"""
Demonstration of xcenter with tolerance in OR-Tools

Shows multiple approaches to implement center positioning with tolerance
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

print("=" * 80)
print("XCENTER WITH TOLERANCE - DEMONSTRATION")
print("=" * 80)
print()

# ==============================================================================
# APPROACH 1: Manual Inequality Constraints
# ==============================================================================
print("APPROACH 1: Manual Inequality Constraints")
print("-" * 80)
print()

parent1 = Cell('parent1')
child1 = Cell('child1', 'metal1')

# Set parent and child sizes
parent1.constrain('x1=0, y1=0, x2=100, y2=100')
parent1.constrain(child1, 'sx2-sx1=30, sy2-sy1=40')

# Xcenter with tolerance ±5 units
# Since sx1+sx2 represents 2*center_x, tolerance of ±5 on center means ±10 on sum
tolerance = 5
tolerance_sum = tolerance * 2

print(f"Goal: Center child in parent with ±{tolerance} unit tolerance")
print(f"Constraint: sx1+sx2 >= ox1+ox2-{tolerance_sum}")
print(f"            sx1+sx2 <= ox1+ox2+{tolerance_sum}")
print()

# Apply constraints
parent1.constrain(child1, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent1)
parent1.constrain(child1, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent1)
parent1.constrain(child1, 'sy1+sy2=oy1+oy2', parent1)  # Exact Y centering

if parent1.solver():
    print("✓ Solver succeeded")
    print()

    parent_center_x = (parent1.pos_list[0] + parent1.pos_list[2]) / 2
    child_center_x = (child1.pos_list[0] + child1.pos_list[2]) / 2
    offset_x = abs(parent_center_x - child_center_x)

    print(f"Parent center X: {parent_center_x}")
    print(f"Child center X:  {child_center_x}")
    print(f"Offset: {offset_x:.2f} units")
    print()

    if offset_x <= tolerance:
        print(f"✓ Child is within tolerance (±{tolerance} units)")
    else:
        print(f"✗ Child exceeds tolerance")
else:
    print("✗ Solver failed")

print()
print()

# ==============================================================================
# APPROACH 2: Combined with Additional Constraints
# ==============================================================================
print("APPROACH 2: Tolerance + Optimization Goal")
print("-" * 80)
print()

parent2 = Cell('parent2')
child2a = Cell('child2a', 'metal1')
child2b = Cell('child2b', 'poly')

# Set parent size
parent2.constrain('x1=0, y1=0, x2=100, y2=100')

# Set children sizes
parent2.constrain(child2a, 'sx2-sx1=30, sy2-sy1=40')
parent2.constrain(child2b, 'sx2-sx1=20, sy2-sy1=30')

# Xcenter with tolerance for both children
tolerance = 10
tolerance_sum = tolerance * 2

print(f"Goal: Center two children with ±{tolerance} unit tolerance")
print()

# Apply tolerance constraints
parent2.constrain(child2a, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent2)
parent2.constrain(child2a, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent2)
parent2.constrain(child2a, 'sy1=10')  # Position child2a

parent2.constrain(child2b, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent2)
parent2.constrain(child2b, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent2)
parent2.constrain(child2b, 'sy1=60')  # Position child2b

if parent2.solver():
    print("✓ Solver succeeded")
    print()

    parent_center_x = (parent2.pos_list[0] + parent2.pos_list[2]) / 2

    child2a_center_x = (child2a.pos_list[0] + child2a.pos_list[2]) / 2
    offset_2a = abs(parent_center_x - child2a_center_x)

    child2b_center_x = (child2b.pos_list[0] + child2b.pos_list[2]) / 2
    offset_2b = abs(parent_center_x - child2b_center_x)

    print(f"Parent center X: {parent_center_x}")
    print()
    print(f"Child 2a center X: {child2a_center_x}")
    print(f"  Offset: {offset_2a:.2f} units")
    print(f"  Within tolerance: {'✓' if offset_2a <= tolerance else '✗'}")
    print()
    print(f"Child 2b center X: {child2b_center_x}")
    print(f"  Offset: {offset_2b:.2f} units")
    print(f"  Within tolerance: {'✓' if offset_2b <= tolerance else '✗'}")
else:
    print("✗ Solver failed")

print()
print()

# ==============================================================================
# APPROACH 3: Helper Function
# ==============================================================================
print("APPROACH 3: Using Helper Function")
print("-" * 80)
print()

def constrain_xcenter_with_tolerance(parent, child, ref_obj, tolerance):
    """
    Constrain child's X center to be within tolerance of ref_obj's X center

    Args:
        parent: Parent cell
        child: Child cell to constrain
        ref_obj: Reference object (usually parent)
        tolerance: Tolerance in layout units (e.g., 5 means ±5 units)
    """
    tolerance_sum = tolerance * 2
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)

def constrain_ycenter_with_tolerance(parent, child, ref_obj, tolerance):
    """
    Constrain child's Y center to be within tolerance of ref_obj's Y center

    Args:
        parent: Parent cell
        child: Child cell to constrain
        ref_obj: Reference object (usually parent)
        tolerance: Tolerance in layout units (e.g., 5 means ±5 units)
    """
    tolerance_sum = tolerance * 2
    parent.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', ref_obj)

def constrain_center_with_tolerance(parent, child, ref_obj, tolerance_x, tolerance_y=None):
    """
    Constrain child's center to be within tolerance of ref_obj's center

    Args:
        parent: Parent cell
        child: Child cell to constrain
        ref_obj: Reference object (usually parent)
        tolerance_x: X tolerance in layout units
        tolerance_y: Y tolerance (defaults to tolerance_x if not specified)
    """
    if tolerance_y is None:
        tolerance_y = tolerance_x

    constrain_xcenter_with_tolerance(parent, child, ref_obj, tolerance_x)
    constrain_ycenter_with_tolerance(parent, child, ref_obj, tolerance_y)


# Use helper function
parent3 = Cell('parent3')
child3 = Cell('child3', 'metal1')

parent3.constrain('x1=0, y1=0, x2=100, y2=100')
parent3.constrain(child3, 'sx2-sx1=30, sy2-sy1=40')

tolerance = 8
print(f"Using helper function with tolerance ±{tolerance} units")
print()

constrain_center_with_tolerance(parent3, child3, parent3, tolerance)

if parent3.solver():
    print("✓ Solver succeeded")
    print()

    parent_center_x = (parent3.pos_list[0] + parent3.pos_list[2]) / 2
    parent_center_y = (parent3.pos_list[1] + parent3.pos_list[3]) / 2
    child_center_x = (child3.pos_list[0] + child3.pos_list[2]) / 2
    child_center_y = (child3.pos_list[1] + child3.pos_list[3]) / 2

    offset_x = abs(parent_center_x - child_center_x)
    offset_y = abs(parent_center_y - child_center_y)

    print(f"Parent center: ({parent_center_x}, {parent_center_y})")
    print(f"Child center:  ({child_center_x}, {child_center_y})")
    print(f"Offset X: {offset_x:.2f} units ({'✓' if offset_x <= tolerance else '✗'})")
    print(f"Offset Y: {offset_y:.2f} units ({'✓' if offset_y <= tolerance else '✗'})")
else:
    print("✗ Solver failed")

print()
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("SUMMARY: XCENTER WITH TOLERANCE")
print("=" * 80)
print()
print("Three approaches demonstrated:")
print()
print("1. Manual Inequality Constraints:")
print("   parent.constrain(child, 'sx1+sx2>=ox1+ox2-10', parent)")
print("   parent.constrain(child, 'sx1+sx2<=ox1+ox2+10', parent)")
print("   → Gives ±5 unit tolerance on center position")
print()
print("2. Combined with Other Constraints:")
print("   Same as #1, but can be combined with other positioning constraints")
print("   → Allows complex layouts with tolerance requirements")
print()
print("3. Helper Functions:")
print("   constrain_xcenter_with_tolerance(parent, child, parent, tolerance=5)")
print("   → Cleaner code, reusable, easier to maintain")
print()
print("Key Points:")
print("  • Tolerance on center = 2× tolerance on sum (sx1+sx2)")
print("  • Use >= and <= instead of = for tolerance constraints")
print("  • Helper functions make code more readable")
print("  • OR-Tools will find any solution within the tolerance range")
print()
print("Recommended: Use helper functions (Approach 3) for cleaner code")
print()
print("=" * 80)
