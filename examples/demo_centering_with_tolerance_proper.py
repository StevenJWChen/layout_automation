#!/usr/bin/env python3
"""
Proper Centering with Tolerance - Complete Example

Demonstrates the correct way to achieve centering with tolerance fallback
using a custom solver objective that minimizes deviation from center.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.centering_with_tolerance import (
    add_centering_with_tolerance,
    solver_with_centering_objective,
)

print("=" * 80)
print("CENTERING WITH TOLERANCE - PROPER IMPLEMENTATION")
print("=" * 80)
print()

# ==============================================================================
# Test 1: Basic centering with tolerance
# ==============================================================================
print("Test 1: Basic Centering with Tolerance")
print("-" * 80)
print()

parent1 = Cell('parent1')
child1 = Cell('child1', 'metal1')

# Set parent and child sizes
parent1.constrain('x1=0, y1=0, x2=100, y2=100')
parent1.constrain(child1, 'swidth=30, sheight=40')

# Add centering with ±5 unit tolerance
print(f"Setup:")
print(f"  Parent: 100x100 box")
print(f"  Child: 30x40 box")
print(f"  Tolerance: ±5 units")
print()

centering1 = add_centering_with_tolerance(parent1, child1, parent1, tolerance_x=5, tolerance_y=5)

print(f"Constraint type: Centering with tolerance fallback")
print(f"  If exact centering possible → will center exactly")
print(f"  If not possible → will center within ±5 units")
print()

try:
    if solver_with_centering_objective(parent1, [centering1]):
        parent_cx = (parent1.pos_list[0] + parent1.pos_list[2]) / 2
        parent_cy = (parent1.pos_list[1] + parent1.pos_list[3]) / 2
        child_cx = (child1.pos_list[0] + child1.pos_list[2]) / 2
        child_cy = (child1.pos_list[1] + child1.pos_list[3]) / 2

        offset_x = abs(parent_cx - child_cx)
        offset_y = abs(parent_cy - child_cy)

        print(f"Results:")
        print(f"  Parent: {parent1.pos_list}")
        print(f"  Child:  {child1.pos_list}")
        print(f"  Parent center: ({parent_cx}, {parent_cy})")
        print(f"  Child center:  ({child_cx}, {child_cy})")
        print(f"  Offset X: {offset_x:.2f} units")
        print(f"  Offset Y: {offset_y:.2f} units")
        print()

        if offset_x < 0.1 and offset_y < 0.1:
            print(f"  ✓ Child is EXACTLY centered (no conflicts)")
        elif offset_x <= 5 and offset_y <= 5:
            print(f"  ✓ Child is within tolerance (±5 units)")
        else:
            print(f"  ✗ Child exceeds tolerance")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Solver not available: {e}")

print()
print()

# ==============================================================================
# Test 2: Centering with conflicting constraints
# ==============================================================================
print("Test 2: Centering with Conflicting Constraints")
print("-" * 80)
print()

parent2 = Cell('parent2')
child2 = Cell('child2', 'poly')

# Set parent and child sizes
parent2.constrain('x1=0, y1=0, x2=100, y2=100')
parent2.constrain(child2, 'swidth=30, sheight=40')

# Add constraints that conflict with perfect centering
# Perfect centering would place child at x1=35, but we require x1>=40
parent2.constrain(child2, 'sx1>=40')
parent2.constrain(child2, 'sy1>=35')

print(f"Setup:")
print(f"  Parent: 100x100 box")
print(f"  Child: 30x40 box")
print(f"  Additional constraints:")
print(f"    sx1 >= 40  (child must start at x=40 or more)")
print(f"    sy1 >= 35  (child must start at y=35 or more)")
print()
print(f"  Perfect centering would place child at x1=35, y1=30")
print(f"  But sx1>=40 conflicts with perfect X centering!")
print()
print(f"  With ±10 unit tolerance, solver should find best center within bounds")
print()

# Add centering with ±10 unit tolerance (wide enough to accommodate conflict)
centering2 = add_centering_with_tolerance(parent2, child2, parent2, tolerance_x=10, tolerance_y=10)

try:
    if solver_with_centering_objective(parent2, [centering2]):
        parent_cx = (parent2.pos_list[0] + parent2.pos_list[2]) / 2
        parent_cy = (parent2.pos_list[1] + parent2.pos_list[3]) / 2
        child_cx = (child2.pos_list[0] + child2.pos_list[2]) / 2
        child_cy = (child2.pos_list[1] + child2.pos_list[3]) / 2

        offset_x = abs(parent_cx - child_cx)
        offset_y = abs(parent_cy - child_cy)

        print(f"Results:")
        print(f"  Parent: {parent2.pos_list}")
        print(f"  Child:  {child2.pos_list}")
        print(f"  Parent center: ({parent_cx}, {parent_cy})")
        print(f"  Child center:  ({child_cx}, {child_cy})")
        print(f"  Offset X: {offset_x:.2f} units")
        print(f"  Offset Y: {offset_y:.2f} units")
        print()

        if offset_x < 0.1 and offset_y < 0.1:
            print(f"  ✓ Child is EXACTLY centered (constraints didn't conflict)")
        elif offset_x <= 10 and offset_y <= 10:
            print(f"  ✓ Child is within tolerance (±10 units)")
            print(f"  ✓ Solver found best centering given the constraints")
            print(f"    (child is as centered as possible while satisfying sx1>=40)")
        else:
            print(f"  ✗ Child exceeds tolerance")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Solver not available: {e}")

print()
print()

# ==============================================================================
# Test 3: Multiple children with different tolerances
# ==============================================================================
print("Test 3: Multiple Children with Different Tolerances")
print("-" * 80)
print()

parent3 = Cell('parent3')
child3a = Cell('child3a', 'metal1')
child3b = Cell('child3b', 'poly')
child3c = Cell('child3c', 'contact')

# Set parent size
parent3.constrain('x1=0, y1=0, x2=200, y2=200')

# Set children sizes
parent3.constrain(child3a, 'swidth=40, sheight=30')
parent3.constrain(child3b, 'swidth=35, sheight=25')
parent3.constrain(child3c, 'swidth=30, sheight=20')

# Position children vertically
parent3.constrain(child3a, 'sy1=20')
parent3.constrain(child3b, 'sy1=80')
parent3.constrain(child3c, 'sy1=140')

print(f"Setup:")
print(f"  Parent: 200x200 box")
print(f"  Three children positioned at different Y levels")
print(f"  Child A: Exact X centering (tolerance = 0)")
print(f"  Child B: ±5 unit tolerance")
print(f"  Child C: ±15 unit tolerance")
print()

# Add centering with different tolerances
centering3a = add_centering_with_tolerance(parent3, child3a, parent3,
                                           tolerance_x=0,  # Exact centering
                                           center_y=False)  # Only X

centering3b = add_centering_with_tolerance(parent3, child3b, parent3,
                                           tolerance_x=5,  # ±5 units
                                           center_y=False)

centering3c = add_centering_with_tolerance(parent3, child3c, parent3,
                                           tolerance_x=15,  # ±15 units
                                           center_y=False)

try:
    if solver_with_centering_objective(parent3, [centering3a, centering3b, centering3c]):
        parent_cx = (parent3.pos_list[0] + parent3.pos_list[2]) / 2

        child3a_cx = (child3a.pos_list[0] + child3a.pos_list[2]) / 2
        child3b_cx = (child3b.pos_list[0] + child3b.pos_list[2]) / 2
        child3c_cx = (child3c.pos_list[0] + child3c.pos_list[2]) / 2

        offset_a = abs(parent_cx - child3a_cx)
        offset_b = abs(parent_cx - child3b_cx)
        offset_c = abs(parent_cx - child3c_cx)

        print(f"Results:")
        print(f"  Parent center X: {parent_cx}")
        print()
        print(f"  Child A: {child3a.pos_list}")
        print(f"    Center X: {child3a_cx}")
        print(f"    Offset: {offset_a:.2f} units (exact: {'✓' if offset_a < 0.1 else '✗'})")
        print()
        print(f"  Child B: {child3b.pos_list}")
        print(f"    Center X: {child3b_cx}")
        print(f"    Offset: {offset_b:.2f} units (within ±5: {'✓' if offset_b <= 5 else '✗'})")
        print()
        print(f"  Child C: {child3c.pos_list}")
        print(f"    Center X: {child3c_cx}")
        print(f"    Offset: {offset_c:.2f} units (within ±15: {'✓' if offset_c <= 15 else '✗'})")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Solver not available: {e}")

print()
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("PROPER CENTERING WITH TOLERANCE:")
print()
print("1. Import the custom solver:")
print("   from layout_automation.centering_with_tolerance import (")
print("       add_centering_with_tolerance,")
print("       solver_with_centering_objective,")
print("   )")
print()
print("2. Add centering constraint with tolerance:")
print("   centering = add_centering_with_tolerance(")
print("       parent, child, parent,")
print("       tolerance_x=10,  # ±10 units in X")
print("       tolerance_y=10   # ±10 units in Y")
print("   )")
print()
print("3. Solve with custom objective:")
print("   solver_with_centering_objective(parent, [centering])")
print()
print("HOW IT WORKS:")
print("  • Adds tolerance bounds as HARD constraints (must satisfy)")
print("  • Adds deviation variables to measure offset from perfect centering")
print("  • Minimizes total deviation (prefers centered solutions)")
print()
print("BEHAVIOR:")
print("  • If exact centering is possible → will center exactly")
print("  • If conflicts exist → will center as close as possible within tolerance")
print("  • NO left/bottom bias (objective minimizes deviation, not coordinates)")
print()
print("TOLERANCES:")
print("  • tolerance_x=0, tolerance_y=0 → Exact centering (hard constraint)")
print("  • tolerance_x>0 → Allow ±tolerance deviation, prefer centered")
print()
print("=" * 80)
