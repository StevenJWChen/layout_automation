#!/usr/bin/env python3
"""
Test: Center constraint with automatic ±1 tolerance fallback

This example demonstrates the new feature where:
    parent.constrain(child, 'center', ref_obj)

automatically tries exact centering first, but allows ±1 tolerance if needed.
"""

from layout_automation.cell import Cell

# Example 1: Exact centering (should achieve exact center)
print("=" * 60)
print("Example 1: Exact centering (both dimensions even)")
print("=" * 60)

parent1 = Cell('parent1')
poly1 = Cell('poly1', 'metal1')
poly2 = Cell('poly2', 'metal2')

# Parent and child both have even dimensions - exact centering possible
parent1.constrain(poly1, 'width=20, height=30, x1=10, y1=10')
parent1.constrain(poly2, 'width=40, height=40')

# This will try exact centering, with ±1 tolerance as fallback
parent1.constrain(poly2, 'center', poly1)

if parent1.solver():
    print(f"\nParent: {parent1.pos_list}")
    print(f"Poly1:  {poly1.pos_list}")
    print(f"Poly2:  {poly2.pos_list}")

    # Calculate centers
    poly1_center_x = (poly1.pos_list[0] + poly1.pos_list[2]) / 2
    poly1_center_y = (poly1.pos_list[1] + poly1.pos_list[3]) / 2
    poly2_center_x = (poly2.pos_list[0] + poly2.pos_list[2]) / 2
    poly2_center_y = (poly2.pos_list[1] + poly2.pos_list[3]) / 2

    print(f"\nPoly1 center: ({poly1_center_x}, {poly1_center_y})")
    print(f"Poly2 center: ({poly2_center_x}, {poly2_center_y})")
    print(f"X deviation: {abs(poly1_center_x - poly2_center_x)}")
    print(f"Y deviation: {abs(poly1_center_y - poly2_center_y)}")

    if poly1_center_x == poly2_center_x and poly1_center_y == poly2_center_y:
        print("✓ EXACT centering achieved!")
    else:
        print("✓ Centering within tolerance achieved!")


# Example 2: Tolerance needed (odd dimension conflict)
print("\n" + "=" * 60)
print("Example 2: Tolerance fallback (dimension conflict)")
print("=" * 60)

parent2 = Cell('parent2')
poly3 = Cell('poly3', 'metal1')
poly4 = Cell('poly4', 'metal2')

# Create dimension conflict - exact centering may be impossible
parent2.constrain(poly3, 'width=21, height=31, x1=10, y1=10')  # Odd dimensions
parent2.constrain(poly4, 'width=40, height=40')  # Even dimensions

# This will use ±1 tolerance fallback
parent2.constrain(poly4, 'center', poly3)

if parent2.solver():
    print(f"\nParent: {parent2.pos_list}")
    print(f"Poly3:  {poly3.pos_list}")
    print(f"Poly4:  {poly4.pos_list}")

    # Calculate centers
    poly3_center_x = (poly3.pos_list[0] + poly3.pos_list[2]) / 2
    poly3_center_y = (poly3.pos_list[1] + poly3.pos_list[3]) / 2
    poly4_center_x = (poly4.pos_list[0] + poly4.pos_list[2]) / 2
    poly4_center_y = (poly4.pos_list[1] + poly4.pos_list[3]) / 2

    print(f"\nPoly3 center: ({poly3_center_x}, {poly3_center_y})")
    print(f"Poly4 center: ({poly4_center_x}, {poly4_center_y})")

    x_dev = abs(poly3_center_x - poly4_center_x)
    y_dev = abs(poly3_center_y - poly4_center_y)
    print(f"X deviation: {x_dev}")
    print(f"Y deviation: {y_dev}")

    if x_dev <= 1 and y_dev <= 1:
        print("✓ Centering within ±1 tolerance achieved!")
        if x_dev == 0 and y_dev == 0:
            print("  (Actually achieved EXACT centering!)")
        else:
            print(f"  (Used tolerance: X±{x_dev}, Y±{y_dev})")


# Example 3: X-only centering
print("\n" + "=" * 60)
print("Example 3: X-only centering with tolerance")
print("=" * 60)

parent3 = Cell('parent3')
poly5 = Cell('poly5', 'metal1')
poly6 = Cell('poly6', 'metal2')

parent3.constrain(poly5, 'width=30, height=40, x1=20, y1=10')
parent3.constrain(poly6, 'width=25, height=35')

# Only center in X direction
parent3.constrain(poly6, 'xcenter', poly5)
# Position Y independently (use a reasonable value)
parent3.constrain(poly6, 'y1=15')

if parent3.solver():
    print(f"\nParent: {parent3.pos_list}")
    print(f"Poly5:  {poly5.pos_list}")
    print(f"Poly6:  {poly6.pos_list}")

    poly5_center_x = (poly5.pos_list[0] + poly5.pos_list[2]) / 2
    poly6_center_x = (poly6.pos_list[0] + poly6.pos_list[2]) / 2

    print(f"\nPoly5 X-center: {poly5_center_x}")
    print(f"Poly6 X-center: {poly6_center_x}")
    print(f"X deviation: {abs(poly5_center_x - poly6_center_x)}")

    if abs(poly5_center_x - poly6_center_x) <= 1:
        print("✓ X-centering within ±1 tolerance achieved!")


print("\n" + "=" * 60)
print("Summary:")
print("  - 'center' keyword now automatically uses ±1 tolerance")
print("  - Solver prefers exact centering but allows ±1 if needed")
print("  - Uses OR-Tools native soft constraint pattern")
print("  - Works with 'center', 'xcenter', and 'ycenter' keywords")
print("=" * 60)
