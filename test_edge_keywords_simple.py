#!/usr/bin/env python3
"""
Simple, clear test for edge distance keywords

Edge keywords represent the DISTANCE (difference) between edges:
- ll_edge = sx1 - ox1 (subject left minus object left)
- lr_edge = sx1 - ox2 (subject left minus object right)
- rl_edge = sx2 - ox1 (subject right minus object left)
- rr_edge = sx2 - ox2 (subject right minus object right)

And similarly for vertical (bb, bt, tb, tt)
"""

from layout_automation import Cell
from layout_automation.constraint_keywords import expand_constraint_keywords

print("="*70)
print("Testing Edge Distance Keywords - Simple & Clear")
print("="*70)

# Test 1: Verify expansions
print("\n[1] Keyword Expansion Verification")
print("-" * 70)

expansions = {
    'll_edge': 'sx1-ox1',
    'lr_edge': 'sx1-ox2',
    'rl_edge': 'sx2-ox1',
    'rr_edge': 'sx2-ox2',
    'bb_edge': 'sy1-oy1',
    'bt_edge': 'sy1-oy2',
    'tb_edge': 'sy2-oy1',
    'tt_edge': 'sy2-oy2',
}

for keyword, expected in expansions.items():
    result = expand_constraint_keywords(f"{keyword}=10")
    assert result == f"{expected}=10", f"Failed: {keyword}"
    print(f"  {keyword:10s} -> {expected:15s} [OK]")

print("  [PASS] All expansions correct")

# Test 2: ll_edge = 0 means left edges aligned
print("\n[2] ll_edge=0 → Left edges aligned")
print("-" * 70)

parent = Cell('parent')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

parent.constrain(box1, 'x1=10, y1=0, x2=30, y2=20')
parent.constrain(box2, 'll_edge=0', box1)
parent.constrain(box2, 'y1=25, x2-x1=15, y2-y1=10')

parent.solver()

print(f"  box1 x1={box1.x1}, box2 x1={box2.x1}")
print(f"  ll_edge (sx1-ox1) = {box2.x1} - {box1.x1} = {box2.x1 - box1.x1}")
assert box1.x1 == box2.x1, "Left edges should be aligned"
print("  [PASS] ll_edge=0 aligns left edges")

# Test 3: rr_edge = 0 means right edges aligned
print("\n[3] rr_edge=0 → Right edges aligned")
print("-" * 70)

parent = Cell('parent')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

parent.constrain(box1, 'x1=10, y1=0, x2=50, y2=20')
parent.constrain(box2, 'rr_edge=0', box1)
parent.constrain(box2, 'y1=25, x2-x1=25, y2-y1=10')

parent.solver()

print(f"  box1 x2={box1.x2}, box2 x2={box2.x2}")
print(f"  rr_edge (sx2-ox2) = {box2.x2} - {box1.x2} = {box2.x2 - box1.x2}")
assert box1.x2 == box2.x2, "Right edges should be aligned"
print("  [PASS] rr_edge=0 aligns right edges")

# Test 4: bb_edge = 0 means bottom edges aligned
print("\n[4] bb_edge=0 → Bottom edges aligned")
print("-" * 70)

parent = Cell('parent')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

parent.constrain(box1, 'x1=0, y1=10, x2=20, y2=30')
parent.constrain(box2, 'bb_edge=0', box1)
parent.constrain(box2, 'x1=25, x2-x1=15, y2-y1=15')

parent.solver()

print(f"  box1 y1={box1.y1}, box2 y1={box2.y1}")
print(f"  bb_edge (sy1-oy1) = {box2.y1} - {box1.y1} = {box2.y1 - box1.y1}")
assert box1.y1 == box2.y1, "Bottom edges should be aligned"
print("  [PASS] bb_edge=0 aligns bottom edges")

# Test 5: tt_edge = 0 means top edges aligned
print("\n[5] tt_edge=0 → Top edges aligned")
print("-" * 70)

parent = Cell('parent')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

parent.constrain(box1, 'x1=0, y1=10, x2=20, y2=40')
parent.constrain(box2, 'tt_edge=0', box1)
parent.constrain(box2, 'x1=25, x2-x1=15, y2-y1=20')

parent.solver()

print(f"  box1 y2={box1.y2}, box2 y2={box2.y2}")
print(f"  tt_edge (sy2-oy2) = {box2.y2} - {box1.y2} = {box2.y2 - box1.y2}")
assert box1.y2 == box2.y2, "Top edges should be aligned"
print("  [PASS] tt_edge=0 aligns top edges")

# Test 6: lr_edge < 0 means subject overlaps object (subject's left is inside object)
print("\n[6] lr_edge < 0 → Subject's left edge is inside object")
print("-" * 70)

parent = Cell('parent')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

parent.constrain(box1, 'x1=0, y1=0, x2=40, y2=20')
parent.constrain(box2, 'lr_edge=-10', box1)
parent.constrain(box2, 'y1=25, x2-x1=30, y2-y1=15')

parent.solver()

print(f"  box1: x=[{box1.x1}, {box1.x2}]")
print(f"  box2: x=[{box2.x1}, {box2.x2}]")
lr_value = box2.x1 - box1.x2
print(f"  lr_edge (sx1-ox2) = {box2.x1} - {box1.x2} = {lr_value}")
assert lr_value == -10, f"Expected lr_edge=-10, got {lr_value}"
print("  [PASS] Negative lr_edge creates overlap")

# Test 7: Practical spacing - place box2 to the right of box1
# For this, we want: box2.x1 = box1.x2 + spacing
# That's: sx1 = ox2 + spacing (NOT an edge keyword, this is the old way)
# With edge keywords, we could use: rl_edge = swidth + spacing
# Because rl_edge = sx2 - ox1, and if we set it to the distance we want...
# Actually, let's show what each edge keyword is useful for:

print("\n[7] Practical Use Cases")
print("-" * 70)

print("\n  Use Case: Align left edges")
print("  Solution: ll_edge=0")

print("\n  Use Case: Align right edges")
print("  Solution: rr_edge=0")

print("\n  Use Case: Align bottom edges")
print("  Solution: bb_edge=0")

print("\n  Use Case: Align top edges")
print("  Solution: tt_edge=0")

print("\n  Use Case: Check if boxes overlap horizontally")
print("  Solution: lr_edge<0 means overlap")

print("\n  Use Case: Simple horizontal spacing (box2 right of box1)")
print("  Old way: sx1=ox2+10")
print("  Note: Edge keywords measure edge-to-edge distance, not spacing!")
print("        For positioning, old syntax is often clearer.")

print("\n  Edge keywords are best for:")
print("    - Alignment (ll_edge=0, rr_edge=0, etc.)")
print("    - Overlap detection (lr_edge<0, etc.)")
print("    - Complex edge relationships")

print("\n" + "="*70)
print("ALL TESTS PASSED!")
print("="*70)

print("\nSummary:")
print("  Edge keywords represent DISTANCES between edges")
print("  Format: {subject_edge}{object_edge}_edge = sx{n} - ox{m}")
print("  Perfect for alignment and overlap detection")
print("  For simple spacing, traditional syntax may be clearer")
