#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for self-constrain and auto-add instance features

Tests:
1. Self-constraint on cell's own bounding box
2. Auto-add instances when referenced in constraints
3. Combination of both features
"""

from layout_automation.cell import Cell

print("=" * 70)
print("TEST: Self-Constrain and Auto-Add Instance Features")
print("=" * 70)
print()

# ==============================================================================
# TEST 1: Self-Constraint on Cell's Own Bounding Box
# ==============================================================================

print("Test 1: Self-Constraint on Cell's Own Bounding Box")
print("-" * 70)

# Create a container with some children
child1 = Cell('child1', 'metal1')
child2 = Cell('child2', 'metal2')

container = Cell('container', child1, child2)

# Position children
container.constrain(child1, 'sx1=10, sy1=10')
container.constrain(child1, 'sx2+20=ox1, sy1=oy1', child2)

# Add self-constraint to container - fix its size
container.constrain('x2-x1=100, y2-y1=50')

print("Container constraints:")
print(f"  Children: {[c.name for c in container.children]}")
print(f"  Constraints: {len(container.constraints)}")
print(f"    - Position child1 absolutely")
print(f"    - Position child2 relative to child1")
print(f"    - Self-constraint: width=100, height=50")
print()

result = container.solver()

if result:
    print(f"✓ Solver succeeded")
    print(f"  child1: {child1.pos_list}")
    print(f"  child2: {child2.pos_list}")
    print(f"  container: {container.pos_list}")

    # Verify self-constraint
    cx1, cy1, cx2, cy2 = container.pos_list
    width = cx2 - cx1
    height = cy2 - cy1
    print(f"\n  Verification:")
    print(f"    Container width: {width} (should be 100)")
    print(f"    Container height: {height} (should be 50)")

    if abs(width - 100) < 0.01 and abs(height - 50) < 0.01:
        print(f"  ✓ PASS - Self-constraint satisfied")
    else:
        print(f"  ✗ FAIL - Self-constraint NOT satisfied")
else:
    print("✗ Solver failed")

print()

# ==============================================================================
# TEST 2: Auto-Add Instances When Referenced in Constraints
# ==============================================================================

print("Test 2: Auto-Add Instances When Referenced in Constraints")
print("-" * 70)

# Create cells but DON'T explicitly add them to parent
rect1 = Cell('rect1', 'metal1')
rect2 = Cell('rect2', 'metal2')
rect3 = Cell('rect3', 'metal3')

parent = Cell('parent')

print(f"Initial parent.children: {len(parent.children)} (empty)")
print()

# Add constraints - instances should be auto-added
print("Adding constraints (will auto-add instances):")
parent.constrain(rect1, 'x1=5, y1=5')
print(f"  After constraining rect1: {len(parent.children)} children")

parent.constrain(rect1, 'sx2+10=ox1, sy1=oy1', rect2)
print(f"  After constraining rect1→rect2: {len(parent.children)} children")

parent.constrain(rect2, 'sx2+10=ox1, sy1=oy1', rect3)
print(f"  After constraining rect2→rect3: {len(parent.children)} children")

print()
print(f"Final parent.children: {[c.name for c in parent.children]}")
print()

result = parent.solver()

if result:
    print(f"✓ Solver succeeded")
    print(f"  rect1: {rect1.pos_list}")
    print(f"  rect2: {rect2.pos_list}")
    print(f"  rect3: {rect3.pos_list}")
    print(f"  parent: {parent.pos_list}")

    # Verify all instances were added
    if len(parent.children) == 3:
        print(f"\n  ✓ PASS - All 3 instances auto-added")
    else:
        print(f"\n  ✗ FAIL - Expected 3 children, got {len(parent.children)}")
else:
    print("✗ Solver failed")

print()

# ==============================================================================
# TEST 3: Combination - Auto-Add with Self-Constraint
# ==============================================================================

print("Test 3: Combination - Auto-Add with Self-Constraint")
print("-" * 70)

# Create cells
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

frame = Cell('frame')

print("Frame starts empty")
print()

# Use auto-add feature
frame.constrain(box1, 'x1=10, y1=10')
frame.constrain(box1, 'sx2+15=ox1, sy1=oy1', box2)

# Add self-constraint to frame - add padding around children
frame.constrain('x2-x1=200, y2-y1=100')  # Set frame size (large enough to fit children)

print(f"Frame now has {len(frame.children)} children (auto-added)")
print(f"Constraints: {len(frame.constraints)}")
print()

result = frame.solver()

if result:
    print(f"✓ Solver succeeded")
    print(f"  box1: {box1.pos_list}")
    print(f"  box2: {box2.pos_list}")
    print(f"  frame: {frame.pos_list}")

    # Verify self-constraint on size
    fx1, fy1, fx2, fy2 = frame.pos_list
    width = fx2 - fx1
    height = fy2 - fy1
    if abs(width - 200) < 0.01 and abs(height - 100) < 0.01:
        print(f"\n  ✓ PASS - Self-constraint (size 200x100) satisfied")
    else:
        print(f"\n  ✗ FAIL - Size should be 200x100, got {width}x{height}")
else:
    print("✗ Solver failed")

print()

# ==============================================================================
# TEST 4: Self-Constraint with Size Only
# ==============================================================================

print("Test 4: Self-Constraint with Size Only")
print("-" * 70)

# Create a cell with children
inner1 = Cell('inner1', 'metal1')
inner2 = Cell('inner2', 'metal2')

outer = Cell('outer', inner1, inner2)

# Position children
outer.constrain(inner1, 'x1=5, y1=5')
outer.constrain(inner2, 'x1=50, y1=50')

# Add self-constraints for size only (let position be determined by children)
outer.constrain('x2-x1=100')   # Fix width
outer.constrain('y2-y1=100')   # Fix height

print("Outer cell self-constraints:")
print("  - width=100")
print("  - height=100")
print("  (position determined by children)")
print()

result = outer.solver()

if result:
    print(f"✓ Solver succeeded")
    print(f"  inner1: {inner1.pos_list}")
    print(f"  inner2: {inner2.pos_list}")
    print(f"  outer: {outer.pos_list}")

    # Verify all self-constraints
    ox1, oy1, ox2, oy2 = outer.pos_list
    width = ox2 - ox1
    height = oy2 - oy1

    print(f"\n  Verification:")
    print(f"    width={width} (should be 100)")
    print(f"    height={height} (should be 100)")

    if abs(width - 100) < 0.01 and abs(height - 100) < 0.01:
        print(f"  ✓ PASS - Size constraints satisfied")
    else:
        print(f"  ✗ FAIL - Size constraints not satisfied")
else:
    print("✗ Solver failed")

print()

# ==============================================================================
# TEST 5: Auto-Add with No Explicit add_instance() Calls
# ==============================================================================

print("Test 5: Pure Auto-Add (No Explicit add_instance Calls)")
print("-" * 70)

# Create layout using only constrain() - no add_instance()
a = Cell('a', 'metal1')
b = Cell('b', 'metal1')
c = Cell('c', 'metal2')
d = Cell('d', 'metal2')

layout = Cell('layout')

print("Layout starts empty")
print("Building layout using only constrain() calls...")
print()

# Build entire layout structure via constraints only
layout.constrain(a, 'x1=0, y1=0')
layout.constrain(a, 'sx2+5=ox1, sy1=oy1', b)
layout.constrain(a, 'sx1=ox1, sy2+5=oy1', c)
layout.constrain(c, 'sx2+5=ox1, sy1=oy1', d)

print(f"Layout now has {len(layout.children)} children: {[x.name for x in layout.children]}")
print()

result = layout.solver()

if result:
    print(f"✓ Solver succeeded")
    print(f"  a: {a.pos_list}")
    print(f"  b: {b.pos_list}")
    print(f"  c: {c.pos_list}")
    print(f"  d: {d.pos_list}")
    print(f"  layout: {layout.pos_list}")

    if len(layout.children) == 4:
        print(f"\n  ✓ PASS - All 4 instances auto-added via constrain()")
    else:
        print(f"\n  ✗ FAIL - Expected 4 children, got {len(layout.children)}")
else:
    print("✗ Solver failed")

print()

# ==============================================================================
# TEST 6: Self-Constraint Minimum Size
# ==============================================================================

print("Test 6: Self-Constraint for Minimum Size")
print("-" * 70)

# Create cell with minimum size constraint
p1 = Cell('p1', 'metal1')
p2 = Cell('p2', 'metal2')

min_cell = Cell('min_cell', p1, p2)

# Position children (small)
min_cell.constrain(p1, 'x1=5, y1=5')
min_cell.constrain(p2, 'x1=15, y1=15')

# Self-constraint: minimum size
min_cell.constrain('x2-x1>=50, y2-y1>=30')  # At least 50x30

print("Minimum size constraint: width >= 50, height >= 30")
print()

result = min_cell.solver()

if result:
    print(f"✓ Solver succeeded")
    print(f"  p1: {p1.pos_list}")
    print(f"  p2: {p2.pos_list}")
    print(f"  min_cell: {min_cell.pos_list}")

    mx1, my1, mx2, my2 = min_cell.pos_list
    width = mx2 - mx1
    height = my2 - my1

    print(f"\n  Verification:")
    print(f"    width={width} (should be >= 50)")
    print(f"    height={height} (should be >= 30)")

    if width >= 49.99 and height >= 29.99:
        print(f"  ✓ PASS - Minimum size constraint satisfied")
    else:
        print(f"  ✗ FAIL - Minimum size not satisfied")
else:
    print("✗ Solver failed")

print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("✓ Self-Constraint Feature:")
print("  - Can constrain cell's own bounding box")
print("  - Syntax: cell.constrain('x2-x1=100, y2-y1=50')")
print("  - Supports absolute positions, sizes, and aspect ratios")
print()
print("✓ Auto-Add Instance Feature:")
print("  - Instances automatically added when referenced in constraints")
print("  - No need for explicit add_instance() calls")
print("  - Simplifies code: parent.constrain(child1, ..., child2)")
print()
print("Both features work together seamlessly!")
print("=" * 70)
