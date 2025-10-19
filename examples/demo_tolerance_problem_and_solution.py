#!/usr/bin/env python3
"""
Demonstration of the tolerance centering problem and solutions

Shows:
1. The problem: tolerance constraints cause left/bottom bias
2. The solution: use exact constraints for true centering
3. When to actually use tolerance
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

print("=" * 80)
print("TOLERANCE CENTERING: PROBLEM AND SOLUTION")
print("=" * 80)
print()

# ==============================================================================
# PROBLEM: Tolerance constraints cause left/bottom bias
# ==============================================================================
print("PROBLEM: Tolerance Constraints with Left/Bottom Bias")
print("-" * 80)
print()

parent1 = Cell('parent1')
child1 = Cell('child1', 'metal1')

# Set parent and child sizes
parent1.constrain('x1=0, y1=0, x2=100, y2=100')
parent1.constrain(child1, 'swidth=30, sheight=40')

# Apply tolerance constraints
tolerance = 5
tolerance_sum = tolerance * 2

print(f"Setup:")
print(f"  Parent: 100x100 box")
print(f"  Child: 30x40 box")
print(f"  Tolerance: ±{tolerance} units")
print()
print(f"Constraints applied:")
print(f"  sx1+sx2 >= ox1+ox2-{tolerance_sum}")
print(f"  sx1+sx2 <= ox1+ox2+{tolerance_sum}")
print(f"  sy1+sy2 >= oy1+oy2-{tolerance_sum}")
print(f"  sy1+sy2 <= oy1+oy2+{tolerance_sum}")
print()

parent1.constrain(child1, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent1)
parent1.constrain(child1, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent1)
parent1.constrain(child1, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', parent1)
parent1.constrain(child1, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', parent1)

try:
    if parent1.solver():
        parent_cx = (parent1.pos_list[0] + parent1.pos_list[2]) / 2
        parent_cy = (parent1.pos_list[1] + parent1.pos_list[3]) / 2
        child_cx = (child1.pos_list[0] + child1.pos_list[2]) / 2
        child_cy = (child1.pos_list[1] + child1.pos_list[3]) / 2

        offset_x = parent_cx - child_cx
        offset_y = parent_cy - child_cy

        print(f"Results:")
        print(f"  Parent center: ({parent_cx}, {parent_cy})")
        print(f"  Child center:  ({child_cx}, {child_cy})")
        print(f"  Offset X: {offset_x:+.2f} units")
        print(f"  Offset Y: {offset_y:+.2f} units")
        print()

        if abs(offset_x) < 0.1 and abs(offset_y) < 0.1:
            print(f"  ✓ Child is centered")
        else:
            print(f"  ✗ Child is NOT centered!")
            print(f"  ✗ Child is offset toward {'left' if offset_x > 0 else 'right'}/{'bottom' if offset_y > 0 else 'top'}")
            print()
            print(f"WHY: The solver minimizes coordinate values (cell.py:459)")
            print(f"     This pushes objects toward bottom-left corner")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Solver not available: {e}")

print()
print()

# ==============================================================================
# SOLUTION 1: Use exact centering constraints
# ==============================================================================
print("SOLUTION 1: Use Exact Centering Constraints")
print("-" * 80)
print()

parent2 = Cell('parent2')
child2 = Cell('child2', 'metal1')

# Set parent and child sizes
parent2.constrain('x1=0, y1=0, x2=100, y2=100')
parent2.constrain(child2, 'swidth=30, sheight=40')

print(f"Setup:")
print(f"  Parent: 100x100 box")
print(f"  Child: 30x40 box")
print()
print(f"Constraints applied:")
print(f"  sx1+sx2 = ox1+ox2  (exact X centering)")
print(f"  sy1+sy2 = oy1+oy2  (exact Y centering)")
print()

# Apply exact centering constraints
parent2.constrain(child2, 'sx1+sx2=ox1+ox2', parent2)
parent2.constrain(child2, 'sy1+sy2=oy1+oy2', parent2)

try:
    if parent2.solver():
        parent_cx = (parent2.pos_list[0] + parent2.pos_list[2]) / 2
        parent_cy = (parent2.pos_list[1] + parent2.pos_list[3]) / 2
        child_cx = (child2.pos_list[0] + child2.pos_list[2]) / 2
        child_cy = (child2.pos_list[1] + child2.pos_list[3]) / 2

        offset_x = abs(parent_cx - child_cx)
        offset_y = abs(parent_cy - child_cy)

        print(f"Results:")
        print(f"  Parent center: ({parent_cx}, {parent_cy})")
        print(f"  Child center:  ({child_cx}, {child_cy})")
        print(f"  Offset X: {offset_x:.6f} units")
        print(f"  Offset Y: {offset_y:.6f} units")
        print()

        if offset_x < 0.1 and offset_y < 0.1:
            print(f"  ✓ Child is EXACTLY centered!")
        else:
            print(f"  ✗ Child is NOT centered")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Solver not available: {e}")

print()
print()

# ==============================================================================
# SOLUTION 2: Use built-in keywords
# ==============================================================================
print("SOLUTION 2: Use Built-in 'center' Keyword (Easiest)")
print("-" * 80)
print()

parent3 = Cell('parent3')
child3 = Cell('child3', 'metal1')

# Set parent and child sizes
parent3.constrain('width=100, height=100, x1=0, y1=0')
parent3.constrain(child3, 'swidth=30, sheight=40')

print(f"Setup:")
print(f"  Parent: 100x100 box")
print(f"  Child: 30x40 box")
print()
print(f"Constraint applied:")
print(f"  'center'  (keyword expands to exact centering)")
print()

# Use keyword
parent3.constrain(child3, 'center', parent3)

try:
    if parent3.solver():
        parent_cx = (parent3.pos_list[0] + parent3.pos_list[2]) / 2
        parent_cy = (parent3.pos_list[1] + parent3.pos_list[3]) / 2
        child_cx = (child3.pos_list[0] + child3.pos_list[2]) / 2
        child_cy = (child3.pos_list[1] + child3.pos_list[3]) / 2

        offset_x = abs(parent_cx - child_cx)
        offset_y = abs(parent_cy - child_cy)

        print(f"Results:")
        print(f"  Parent center: ({parent_cx}, {parent_cy})")
        print(f"  Child center:  ({child_cx}, {child_cy})")
        print(f"  Offset X: {offset_x:.6f} units")
        print(f"  Offset Y: {offset_y:.6f} units")
        print()

        if offset_x < 0.1 and offset_y < 0.1:
            print(f"  ✓ Child is EXACTLY centered!")
            print(f"  ✓ This is the RECOMMENDED approach")
        else:
            print(f"  ✗ Child is NOT centered")
    else:
        print("✗ Solver failed")
except Exception as e:
    print(f"✗ Solver not available: {e}")

print()
print()

# ==============================================================================
# WHEN TO USE TOLERANCE: Conflicting constraints
# ==============================================================================
print("WHEN TO USE TOLERANCE: Dealing with Conflicting Constraints")
print("-" * 80)
print()

parent4 = Cell('parent4')
child4 = Cell('child4', 'metal1')

# Set parent and child sizes
parent4.constrain('x1=0, y1=0, x2=100, y2=100')
parent4.constrain(child4, 'swidth=30, sheight=40')

# Add constraints that conflict with perfect centering
parent4.constrain(child4, 'sx1>=12')  # Must be at least 12 units from left
parent4.constrain(child4, 'sy1>=10')  # Must be at least 10 units from bottom

print(f"Setup:")
print(f"  Parent: 100x100 box")
print(f"  Child: 30x40 box")
print(f"  Additional constraints:")
print(f"    sx1 >= 12  (at least 12 units from left)")
print(f"    sy1 >= 10  (at least 10 units from bottom)")
print()
print(f"Note: Perfect centering would place child at x1=35, y1=30")
print(f"      But sx1>=12 and sy1>=10 are satisfied, so we use tolerance")
print()

# Try exact centering first
parent4.constrain(child4, 'sx1+sx2=ox1+ox2', parent4)
parent4.constrain(child4, 'sy1+sy2=oy1+oy2', parent4)

# Add tolerance as backup (if exact is impossible due to other constraints)
tolerance = 10
tolerance_sum = tolerance * 2
parent4.constrain(child4, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', parent4)
parent4.constrain(child4, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', parent4)
parent4.constrain(child4, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', parent4)
parent4.constrain(child4, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', parent4)

try:
    if parent4.solver():
        parent_cx = (parent4.pos_list[0] + parent4.pos_list[2]) / 2
        parent_cy = (parent4.pos_list[1] + parent4.pos_list[3]) / 2
        child_cx = (child4.pos_list[0] + child4.pos_list[2]) / 2
        child_cy = (child4.pos_list[1] + child4.pos_list[3]) / 2

        offset_x = abs(parent_cx - child_cx)
        offset_y = abs(parent_cy - child_cy)

        print(f"Results:")
        print(f"  Parent center: ({parent_cx}, {parent_cy})")
        print(f"  Child center:  ({child_cx}, {child_cy})")
        print(f"  Child position: x1={child4.pos_list[0]}, y1={child4.pos_list[1]}")
        print(f"  Offset X: {offset_x:.2f} units")
        print(f"  Offset Y: {offset_y:.2f} units")
        print()

        if offset_x < 0.1 and offset_y < 0.1:
            print(f"  ✓ Child is exactly centered (constraints didn't conflict)")
        elif offset_x <= tolerance and offset_y <= tolerance:
            print(f"  ✓ Child is within tolerance (±{tolerance} units)")
            print(f"  → Exact centering satisfied additional constraints")
        else:
            print(f"  ✗ Child exceeds tolerance")
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
print("THE PROBLEM:")
print("  Using tolerance inequalities (>=, <=) causes left/bottom bias")
print("  because the solver minimizes coordinate values.")
print()
print("THE SOLUTION:")
print("  Use EXACT centering constraints (=) instead of tolerance (>=, <=)")
print()
print("RECOMMENDED APPROACHES:")
print()
print("1. Use keywords (easiest):")
print("   parent.constrain(child, 'center', parent)")
print("   parent.constrain(child, 'xcenter', parent)  # X only")
print("   parent.constrain(child, 'ycenter', parent)  # Y only")
print()
print("2. Use explicit equality (more control):")
print("   parent.constrain(child, 'sx1+sx2=ox1+ox2', parent)")
print("   parent.constrain(child, 'sy1+sy2=oy1+oy2', parent)")
print()
print("3. Only use tolerance when exact centering might conflict:")
print("   # Add BOTH exact and tolerance constraints")
print("   parent.constrain(child, 'sx1+sx2=ox1+ox2', parent)  # Prefer exact")
print("   parent.constrain(child, 'sx1+sx2>=ox1+ox2-10', parent)  # Fallback")
print("   parent.constrain(child, 'sx1+sx2<=ox1+ox2+10', parent)")
print()
print("BOTTOM LINE:")
print("  Don't use tolerance constraints for centering.")
print("  Use exact equality constraints (=) for true centering.")
print()
print("=" * 80)
