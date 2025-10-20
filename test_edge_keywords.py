#!/usr/bin/env python3
"""
Comprehensive test for edge distance keywords:
ll_edge, lr_edge, rl_edge, rr_edge (horizontal)
bb_edge, bt_edge, tb_edge, tt_edge (vertical)
"""

from layout_automation import Cell
from layout_automation.constraint_keywords import expand_constraint_keywords

print("="*70)
print("Testing Edge Distance Keywords")
print("="*70)

# Test 1: Keyword expansion
print("\n[1] Testing keyword expansion")
print("-" * 70)

test_cases = [
    ('rl_edge=10', 'sx2-ox1=10'),
    ('tb_edge=5', 'sy2-oy1=5'),
    ('ll_edge=0', 'sx1-ox1=0'),
    ('rr_edge=0', 'sx2-ox2=0'),
    ('bb_edge=0', 'sy1-oy1=0'),
    ('tt_edge=0', 'sy2-oy2=0'),
    ('lr_edge<0', 'sx1-ox2<0'),
    ('bt_edge>=10', 'sy1-oy2>=10'),
]

for input_str, expected in test_cases:
    result = expand_constraint_keywords(input_str)
    assert result == expected, f"Failed: {input_str} -> {result} (expected {expected})"
    print(f"  {input_str:20s} -> {result}")

print("  [PASS] All keywords expand correctly")

# Test 2: Understanding rl_edge semantics
print("\n[2] Testing rl_edge semantics (right to left distance)")
print("-" * 70)

# rl_edge = sx2 - ox1 (subject's right edge minus object's left edge)
# If subject is placed at x=[40,60] and object at x=[0,20]:
# rl_edge = 60 - 0 = 60 (subject's right is 60 units from object's left)

parent = Cell('parent')
box1 = Cell('box1', 'metal1')  # Object
box2 = Cell('box2', 'metal2')  # Subject

parent.constrain(box1, 'x1=0, y1=0, x2=20, y2=20')
parent.constrain(box2, 'x1=40, y1=0, x2=60, y2=20')

parent.solver()

print(f"  box1 (object):  [{box1.x1}, {box1.y1}, {box1.x2}, {box1.y2}]")
print(f"  box2 (subject): [{box2.x1}, {box2.y1}, {box2.x2}, {box2.y2}]")

# Calculate rl_edge manually
rl_dist = box2.x2 - box1.x1  # sx2 - ox1
print(f"  rl_edge distance (sx2-ox1): {rl_dist}")
assert rl_dist == 60, f"Expected rl_edge=60, got {rl_dist}"

# Now test using rl_edge in constraint
parent2 = Cell('parent2')
box3 = Cell('box3', 'poly')
box4 = Cell('box4', 'diff')

parent2.constrain(box3, 'x1=0, y1=0, x2=20, y2=20')
parent2.constrain(box4, 'rl_edge=60, bb_edge=0', box3)  # box4's right is 60 from box3's left
parent2.constrain(box4, 'swidth=20, sheight=20')

parent2.solver()

print(f"  box3: [{box3.x1}, {box3.y1}, {box3.x2}, {box3.y2}]")
print(f"  box4: [{box4.x1}, {box4.y1}, {box4.x2}, {box4.y2}]")

rl_dist2 = box4.x2 - box3.x1
print(f"  rl_edge constraint result: {rl_dist2}")
assert rl_dist2 == 60, f"Expected rl_edge=60, got {rl_dist2}"

print("  [PASS] rl_edge represents distance from subject's right to object's left")

# Test 3: Vertical spacing with tb_edge
print("\n[3] Testing tb_edge (vertical spacing)")
print("-" * 70)

parent2 = Cell('parent2')
box3 = Cell('box3', 'poly')
box4 = Cell('box4', 'diff')

parent2.constrain(box3, 'x1=0, y1=0, x2=30, y2=20')
parent2.constrain(box4, 'll_edge=0, tb_edge=5', box3)  # 5 units above, same left
parent2.constrain(box4, 'swidth=30, sheight=15')

parent2.solver()

print(f"  box3: [{box3.x1}, {box3.y1}, {box3.x2}, {box3.y2}]")
print(f"  box4: [{box4.x1}, {box4.y1}, {box4.x2}, {box4.y2}]")

# Verify spacing
v_spacing = box4.y1 - box3.y2
print(f"  Vertical spacing: {v_spacing}")
assert v_spacing == 5, f"Expected v_spacing=5, got {v_spacing}"
assert box4.x1 == box3.x1, "Left edges should be aligned"

print("  [PASS] tb_edge creates correct vertical spacing")

# Test 4: ll_edge for alignment (should equal 0 for left alignment)
print("\n[4] Testing ll_edge=0 (left edge alignment)")
print("-" * 70)

parent3 = Cell('parent3')
box5 = Cell('box5', 'metal1')
box6 = Cell('box6', 'metal2')

parent3.constrain(box5, 'x1=10, y1=0, x2=40, y2=20')
parent3.constrain(box6, 'll_edge=0, tb_edge=2', box5)
parent3.constrain(box6, 'swidth=20, sheight=15')

parent3.solver()

print(f"  box5: [{box5.x1}, {box5.y1}, {box5.x2}, {box5.y2}]")
print(f"  box6: [{box6.x1}, {box6.y1}, {box6.x2}, {box6.y2}]")

assert box5.x1 == box6.x1, "ll_edge=0 should align left edges"
print("  [PASS] ll_edge=0 aligns left edges correctly")

# Test 5: rr_edge for right alignment
print("\n[5] Testing rr_edge=0 (right edge alignment)")
print("-" * 70)

parent4 = Cell('parent4')
box7 = Cell('box7', 'poly')
box8 = Cell('box8', 'diff')

parent4.constrain(box7, 'x1=0, y1=0, x2=50, y2=20')
parent4.constrain(box8, 'rr_edge=0, tb_edge=3', box7)
parent4.constrain(box8, 'swidth=30, sheight=15')

parent4.solver()

print(f"  box7: [{box7.x1}, {box7.y1}, {box7.x2}, {box7.y2}]")
print(f"  box8: [{box8.x1}, {box8.y1}, {box8.x2}, {box8.y2}]")

assert box7.x2 == box8.x2, "rr_edge=0 should align right edges"
print("  [PASS] rr_edge=0 aligns right edges correctly")

# Test 6: tt_edge for top alignment
print("\n[6] Testing tt_edge=0 (top edge alignment)")
print("-" * 70)

parent5 = Cell('parent5')
box9 = Cell('box9', 'metal1')
box10 = Cell('box10', 'metal2')

parent5.constrain(box9, 'x1=0, y1=0, x2=30, y2=40')
parent5.constrain(box10, 'rl_edge=5, tt_edge=0', box9)
parent5.constrain(box10, 'swidth=25, sheight=20')

parent5.solver()

print(f"  box9: [{box9.x1}, {box9.y1}, {box9.x2}, {box9.y2}]")
print(f"  box10: [{box10.x1}, {box10.y1}, {box10.x2}, {box10.y2}]")

assert box9.y2 == box10.y2, "tt_edge=0 should align top edges"
print("  [PASS] tt_edge=0 aligns top edges correctly")

# Test 7: bb_edge for bottom alignment
print("\n[7] Testing bb_edge=0 (bottom edge alignment)")
print("-" * 70)

parent6 = Cell('parent6')
box11 = Cell('box11', 'poly')
box12 = Cell('box12', 'diff')

parent6.constrain(box11, 'x1=0, y1=10, x2=30, y2=40')
parent6.constrain(box12, 'rl_edge=5, bb_edge=0', box11)
parent6.constrain(box12, 'swidth=25, sheight=30')

parent6.solver()

print(f"  box11: [{box11.x1}, {box11.y1}, {box11.x2}, {box11.y2}]")
print(f"  box12: [{box12.x1}, {box12.y1}, {box12.x2}, {box12.y2}]")

assert box11.y1 == box12.y1, "bb_edge=0 should align bottom edges"
print("  [PASS] bb_edge=0 aligns bottom edges correctly")

# Test 8: Negative values for overlap
print("\n[8] Testing negative edge values (overlap)")
print("-" * 70)

parent7 = Cell('parent7')
box13 = Cell('box13', 'metal1')
box14 = Cell('box14', 'metal2')

parent7.constrain(box13, 'x1=0, y1=0, x2=40, y2=30')
parent7.constrain(box14, 'rl_edge=-10, bb_edge=0', box13)  # Overlap by 10 units
parent7.constrain(box14, 'swidth=30, sheight=30')

parent7.solver()

print(f"  box13: [{box13.x1}, {box13.y1}, {box13.x2}, {box13.y2}]")
print(f"  box14: [{box14.x1}, {box14.y1}, {box14.x2}, {box14.y2}]")

# With rl_edge=-10, box14.x1 should be 10 units to the left of box13.x2
overlap = box13.x2 - box14.x1
print(f"  Overlap: {overlap} units")
assert overlap == 10, f"Expected overlap=10, got {overlap}"

print("  [PASS] Negative values create overlap correctly")

# Test 9: Complex layout using multiple edge keywords
print("\n[9] Testing complex layout with multiple edge keywords")
print("-" * 70)

complex_parent = Cell('complex')
c1 = Cell('c1', 'metal1')
c2 = Cell('c2', 'metal2')
c3 = Cell('c3', 'poly')
c4 = Cell('c4', 'diff')

# Create 2x2 grid with spacing
complex_parent.constrain(c1, 'x1=0, y1=0, x2=20, y2=20')
complex_parent.constrain(c2, 'rl_edge=5, bb_edge=0', c1)  # Right of c1
complex_parent.constrain(c2, 'swidth=20, sheight=20')
complex_parent.constrain(c3, 'll_edge=0, tb_edge=5', c1)  # Above c1
complex_parent.constrain(c3, 'swidth=20, sheight=20')
complex_parent.constrain(c4, 'rl_edge=5, bb_edge=0', c3)  # Right of c3
complex_parent.constrain(c4, 'swidth=20, sheight=20')

complex_parent.solver()

print(f"  c1: [{c1.x1}, {c1.y1}, {c1.x2}, {c1.y2}]")
print(f"  c2: [{c2.x1}, {c2.y1}, {c2.x2}, {c2.y2}]")
print(f"  c3: [{c3.x1}, {c3.y1}, {c3.x2}, {c3.y2}]")
print(f"  c4: [{c4.x1}, {c4.y1}, {c4.x2}, {c4.y2}]")

# Verify grid structure
assert c2.x1 - c1.x2 == 5, "Horizontal spacing should be 5"
assert c3.y1 - c1.y2 == 5, "Vertical spacing should be 5"
assert c1.x1 == c3.x1, "c1 and c3 should be left-aligned"
assert c2.x1 == c4.x1, "c2 and c4 should be left-aligned"

print("  [PASS] Complex 2x2 grid created correctly")

# Test 10: Combining with other keywords
print("\n[10] Testing edge keywords combined with other keywords")
print("-" * 70)

parent8 = Cell('parent8')
box15 = Cell('box15', 'metal1')
box16 = Cell('box16', 'metal2')

parent8.constrain(box15, 'x1=0, y1=0, x2=30, y2=20')
parent8.constrain(box16, 'rl_edge=10, bb_edge=0, swidth=owidth, sheight=oheight', box15)

parent8.solver()

print(f"  box15: [{box15.x1}, {box15.y1}, {box15.x2}, {box15.y2}]")
print(f"  box16: [{box16.x1}, {box16.y1}, {box16.x2}, {box16.y2}]")

assert box16.width == box15.width, "Widths should match"
assert box16.height == box15.height, "Heights should match"
assert box16.x1 - box15.x2 == 10, "Should have 10 unit spacing"

print("  [PASS] Edge keywords work with size keywords")

print("\n" + "="*70)
print("ALL EDGE KEYWORD TESTS PASSED!")
print("="*70)

print("\nEdge Keywords Verified:")
print("  [OK] ll_edge - left to left")
print("  [OK] lr_edge - left to right")
print("  [OK] rl_edge - right to left (horizontal spacing)")
print("  [OK] rr_edge - right to right")
print("  [OK] bb_edge - bottom to bottom")
print("  [OK] bt_edge - bottom to top")
print("  [OK] tb_edge - top to bottom (vertical spacing)")
print("  [OK] tt_edge - top to top")
print("  [OK] Negative values (overlap)")
print("  [OK] Combined with other keywords")
