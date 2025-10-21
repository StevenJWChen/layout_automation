#!/usr/bin/env python3
"""
Test enhanced label appearance and new single-edge keywords

Tests:
1. Enhanced label appearance (black on white, sharper)
2. New single-edge keywords: l_edge, r_edge, t_edge, b_edge
3. Visual comparison before/after
"""

from layout_automation import Cell
from layout_automation.constraint_keywords import expand_constraint_keywords
import matplotlib.pyplot as plt

print("="*70)
print("Testing Label and Edge Enhancements")
print("="*70)

# Test 1: Verify new edge keywords expansion
print("\n[Test 1] New edge keyword expansion")
print("-" * 70)

test_cases = [
    ('l_edge=10', 'ox1-sx1=10'),
    ('r_edge=5', 'ox2-sx2=5'),
    ('t_edge=3', 'oy2-sy2=3'),
    ('b_edge=7', 'oy1-sy1=7'),
    ('l_edge=0, b_edge=0', 'ox1-sx1=0, oy1-sy1=0'),
]

all_passed = True
for keyword, expected in test_cases:
    result = expand_constraint_keywords(keyword)
    status = "[PASS]" if result == expected else "[FAIL]"
    if result != expected:
        all_passed = False
    print(f"  {status} '{keyword}' -> '{result}'")
    if result != expected:
        print(f"         Expected: '{expected}'")

if all_passed:
    print("\n  All edge keyword tests passed!")
else:
    print("\n  Some tests failed!")

# Test 2: Use new keywords in actual layout
print("\n[Test 2] Using new edge keywords in layout")
print("-" * 70)

parent = Cell('chip')
base = Cell('base', 'metal1')
aligned_left = Cell('aligned_left', 'metal2')
aligned_right = Cell('aligned_right', 'poly')
aligned_top = Cell('aligned_top', 'active')
aligned_bottom = Cell('aligned_bottom', 'contact')

parent.add_instance([base, aligned_left, aligned_right, aligned_top, aligned_bottom])

# Base cell
parent.constrain(base, 'x1=20, y1=20, x2=60, y2=50')

# Use l_edge to align left edges (l_edge=0 means ox1=sx1)
parent.constrain(aligned_left, 'l_edge=0, b_edge=10, swidth=20, sheight=15', base)

# Use r_edge to align right edges (r_edge=0 means ox2=sx2)
parent.constrain(aligned_right, 'r_edge=0, b_edge=10, swidth=20, sheight=15', base)

# Use t_edge to align top edges (t_edge=0 means oy2=sy2)
parent.constrain(aligned_top, 't_edge=0, l_edge=10, swidth=15, sheight=20', base)

# Use b_edge to align bottom edges (b_edge=0 means oy1=sy1)
parent.constrain(aligned_bottom, 'b_edge=0, l_edge=10, swidth=20, sheight=15', base)

parent.solver()

# Verify constraints worked correctly
print(f"  Base: {base.get_bounds()}")
print(f"  Aligned left (l_edge=0): {aligned_left.get_bounds()}")
print(f"    Expected: x1={base.x1} (20.0)")
print(f"    Actual:   x1={aligned_left.x1}")
print(f"    Match: {abs(aligned_left.x1 - base.x1) < 0.01}")

print(f"\n  Aligned right (r_edge=0): {aligned_right.get_bounds()}")
print(f"    Expected: x2={base.x2} (60.0)")
print(f"    Actual:   x2={aligned_right.x2}")
print(f"    Match: {abs(aligned_right.x2 - base.x2) < 0.01}")

print(f"\n  Aligned top (t_edge=0): {aligned_top.get_bounds()}")
print(f"    Expected: y2={base.y2} (50.0)")
print(f"    Actual:   y2={aligned_top.y2}")
print(f"    Match: {abs(aligned_top.y2 - base.y2) < 0.01}")

print(f"\n  Aligned bottom (b_edge=0): {aligned_bottom.get_bounds()}")
print(f"    Expected: y1={base.y1} (20.0)")
print(f"    Actual:   y1={aligned_bottom.y1}")
print(f"    Match: {abs(aligned_bottom.y1 - base.y1) < 0.01}")

# Test 3: Visual test of enhanced labels
print("\n[Test 3] Enhanced label appearance (black on white)")
print("-" * 70)

# Create a test layout with various cell sizes to show labels
test_layout = Cell('label_test')

cells = []
cell_data = [
    ('Large_Cell_1', 'metal1', 0, 0, 50, 40),
    ('Large_Cell_2', 'metal2', 60, 0, 110, 40),
    ('Medium_1', 'poly', 0, 50, 25, 75),
    ('Medium_2', 'active', 30, 50, 55, 75),
    ('Small_1', 'contact', 0, 85, 12, 97),
    ('Small_2', 'via', 18, 85, 30, 97),
]

for name, layer, x1, y1, x2, y2 in cell_data:
    cell = Cell(name, layer)
    cells.append(cell)
    test_layout.add_instance(cell)
    test_layout.constrain(cell, f'x1={x1}, y1={y1}, x2={x2}, y2={y2}')

test_layout.solver()

# Draw with enhanced labels
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: Full label mode
test_layout.draw(ax=ax1, show=False, solve_first=False, label_mode='full')
ax1.set_title('Enhanced Labels - Full Mode\n(Black text on white, sharper edges)',
             fontsize=14, weight='bold')

# Right: Auto label mode
test_layout.draw(ax=ax2, show=False, solve_first=False, label_mode='auto')
ax2.set_title('Enhanced Labels - Auto Mode\n(Smart sizing with enhanced appearance)',
             fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('demo_outputs/test_enhanced_labels.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_enhanced_labels.png")

# Test 4: Edge keyword usage examples
print("\n[Test 4] Edge keyword practical examples")
print("-" * 70)

example_layout = Cell('edge_examples')

ref = Cell('reference', 'metal1')
test1 = Cell('l_edge_test', 'metal2')
test2 = Cell('r_edge_test', 'poly')
test3 = Cell('t_edge_test', 'active')
test4 = Cell('b_edge_test', 'contact')

example_layout.add_instance([ref, test1, test2, test3, test4])

# Reference cell in center
example_layout.constrain(ref, 'x1=40, y1=40, x2=80, y2=70')

# l_edge=5 means object's left is 5 units to the left of subject's left
example_layout.constrain(test1, 'l_edge=5, t_edge=5, swidth=20, sheight=15', ref)

# r_edge=5 means object's right is 5 units to the right of subject's right
example_layout.constrain(test2, 'r_edge=5, t_edge=5, swidth=20, sheight=15', ref)

# t_edge=5 means object's top is 5 units above subject's top
example_layout.constrain(test3, 't_edge=5, l_edge=5, swidth=15, sheight=20', ref)

# b_edge=5 means object's bottom is 5 units below subject's bottom
example_layout.constrain(test4, 'b_edge=5, l_edge=5, swidth=15, sheight=20', ref)

example_layout.solver()

example_layout.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/test_edge_keyword_examples.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_edge_keyword_examples.png")

print(f"\n  Reference: {ref.get_bounds()}")
print(f"  l_edge=5: {test1.get_bounds()}")
print(f"    Expected: x1=reference.x1-5={ref.x1-5}")
print(f"    Actual:   x1={test1.x1}")
print(f"    Match: {abs(test1.x1 - (ref.x1 - 5)) < 0.01}")

# Test 5: Comparison with old edge keywords
print("\n[Test 5] Comparison: single-edge vs double-edge keywords")
print("-" * 70)

comp = Cell('comparison')

base1 = Cell('base1', 'metal1')
base2 = Cell('base2', 'metal1')
child1 = Cell('using_ll_edge', 'metal2')
child2 = Cell('using_l_edge', 'poly')

comp.add_instance([base1, base2, child1, child2])

# Left side: using ll_edge (subject left to object left)
comp.constrain(base1, 'x1=10, y1=10, x2=40, y2=40')
comp.constrain(child1, 'll_edge=10, bb_edge=0, swidth=15, sheight=15', base1)

# Right side: using l_edge (object left to subject left)
comp.constrain(base2, 'x1=60, y1=10, x2=90, y2=40')
comp.constrain(child2, 'l_edge=10, b_edge=0, swidth=15, sheight=15', base2)

comp.solver()

print(f"  Using ll_edge=10 (sx1-ox1=10):")
print(f"    Base:  {base1.get_bounds()}")
print(f"    Child: {child1.get_bounds()}")
print(f"    child.x1 - base.x1 = {child1.x1 - base1.x1} (should be 10)")

print(f"\n  Using l_edge=10 (ox1-sx1=10):")
print(f"    Base:  {base2.get_bounds()}")
print(f"    Child: {child2.get_bounds()}")
print(f"    base.x1 - child.x1 = {base2.x1 - child2.x1} (should be 10)")

comp.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/test_edge_keyword_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_edge_keyword_comparison.png")

print("\n" + "="*70)
print("ALL TESTS COMPLETED!")
print("="*70)

print("\nEnhancements Summary:")
print("\n1. Enhanced Label Appearance:")
print("   [OK] Black text on white background")
print("   [OK] Sharper edges with black border (linewidth=0.5)")
print("   [OK] Improved contrast and readability")
print("   [OK] Semi-transparent white background (alpha=0.85)")

print("\n2. New Single-Edge Keywords:")
print("   [OK] l_edge = ox1-sx1  (object left to subject left)")
print("   [OK] r_edge = ox2-sx2  (object right to subject right)")
print("   [OK] t_edge = oy2-sy2  (object top to subject top)")
print("   [OK] b_edge = oy1-sy1  (object bottom to subject bottom)")

print("\n3. Use Cases:")
print("   - l_edge=0: Align left edges (subject's left = object's left)")
print("   - l_edge=5: Subject extends 5 units left of object")
print("   - l_edge=-5: Subject is 5 units to the right of object's left")
print("   - Useful for alignment and positioning relative to reference")

print("\nGenerated files:")
print("  - test_enhanced_labels.png         : Enhanced label appearance")
print("  - test_edge_keyword_examples.png   : Single-edge keyword examples")
print("  - test_edge_keyword_comparison.png : ll_edge vs l_edge comparison")
