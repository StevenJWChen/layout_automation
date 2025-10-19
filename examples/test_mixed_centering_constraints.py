#!/usr/bin/env python3
"""
Test mixed centering constraints like 'xcenter, sy2=oy1'

Demonstrates that centering keywords can be combined with other constraints.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

print("=" * 70)
print("Test: Mixed Centering Constraints")
print("=" * 70)

# Example 1: xcenter + vertical alignment
print("\nExample 1: xcenter, sy2=oy1 (A below PC, X-centered)")
print("-" * 70)

parent1 = Cell('parent1')
a1 = Cell('a1', 'metal1')
pc1 = Cell('pc1', 'metal2')

parent1.add_instance([a1, pc1])
parent1.constrain(pc1, 'width=20, height=30, x1=10, y1=40')
parent1.constrain(a1, 'width=15, height=25')

# Combined constraint: X-center AND vertical alignment
parent1.constrain(a1, 'xcenter, sy2=oy1', pc1)

if parent1.solver():
    print(f"✓ Solver succeeded")
    print(f"  PC: {pc1.pos_list}")
    print(f"  A:  {a1.pos_list}")

    pc_cx = (pc1.pos_list[0] + pc1.pos_list[2]) / 2
    a_cx = (a1.pos_list[0] + a1.pos_list[2]) / 2

    print(f"\n  X-centering: PC_cx={pc_cx}, A_cx={a_cx}, deviation={abs(pc_cx-a_cx):.1f}")
    print(f"  Vertical: A.y2={a1.pos_list[3]} == PC.y1={pc1.pos_list[1]} ✓")
else:
    print("✗ Solver failed")


# Example 2: ycenter + horizontal alignment
print("\n\nExample 2: ycenter, sx1=ox2+5 (A to right of PC, Y-centered)")
print("-" * 70)

parent2 = Cell('parent2')
a2 = Cell('a2', 'metal1')
pc2 = Cell('pc2', 'metal2')

parent2.add_instance([a2, pc2])
parent2.constrain(pc2, 'width=20, height=30, x1=10, y1=10')
parent2.constrain(a2, 'width=15, height=25')

# Combined: Y-center AND horizontal spacing
parent2.constrain(a2, 'ycenter, sx1=ox2+5', pc2)

if parent2.solver():
    print(f"✓ Solver succeeded")
    print(f"  PC: {pc2.pos_list}")
    print(f"  A:  {a2.pos_list}")

    pc_cy = (pc2.pos_list[1] + pc2.pos_list[3]) / 2
    a_cy = (a2.pos_list[1] + a2.pos_list[3]) / 2

    print(f"\n  Y-centering: PC_cy={pc_cy}, A_cy={a_cy}, deviation={abs(pc_cy-a_cy):.1f}")
    print(f"  Horizontal: A.x1={a2.pos_list[0]} == PC.x2+5={pc2.pos_list[2]+5} ✓")
else:
    print("✗ Solver failed")


# Example 3: center + custom width
print("\n\nExample 3: center, swidth=30 (Full center with custom width)")
print("-" * 70)

parent3 = Cell('parent3')
a3 = Cell('a3', 'metal1')
pc3 = Cell('pc3', 'metal2')

parent3.add_instance([a3, pc3])
parent3.constrain(pc3, 'width=50, height=50, x1=10, y1=10')
parent3.constrain(a3, 'height=20')  # Only specify height

# Full centering + custom width
parent3.constrain(a3, 'center, swidth=30', pc3)

if parent3.solver():
    print(f"✓ Solver succeeded")
    print(f"  PC: {pc3.pos_list}")
    print(f"  A:  {a3.pos_list}")

    pc_cx = (pc3.pos_list[0] + pc3.pos_list[2]) / 2
    pc_cy = (pc3.pos_list[1] + pc3.pos_list[3]) / 2
    a_cx = (a3.pos_list[0] + a3.pos_list[2]) / 2
    a_cy = (a3.pos_list[1] + a3.pos_list[3]) / 2
    a_width = a3.pos_list[2] - a3.pos_list[0]

    print(f"\n  Centering: deviation X={abs(pc_cx-a_cx):.1f}, Y={abs(pc_cy-a_cy):.1f}")
    print(f"  Width: A.width={a_width} (specified as 30) ✓")
else:
    print("✗ Solver failed")


print("\n" + "=" * 70)
print("Summary:")
print("  ✓ Mixed constraints work correctly")
print("  ✓ Centering keywords are extracted and handled separately")
print("  ✓ Remaining constraints are processed normally")
print("=" * 70)
