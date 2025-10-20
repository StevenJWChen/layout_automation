#!/usr/bin/env python3
"""
Practical examples demonstrating edge distance keywords with visualizations
"""

from layout_automation import Cell
import matplotlib.pyplot as plt
import matplotlib.patches as patches

print("="*70)
print("Edge Distance Keywords - Practical Examples")
print("="*70)

# Example 1: Alignment using edge keywords
print("\n[Example 1] Alignment using edge keywords")
print("-" * 70)

# Create a parent with 3 boxes, all left-aligned
parent1 = Cell('parent1')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')
box3 = Cell('box3', 'poly')

parent1.constrain(box1, 'x1=0, y1=0, x2=40, y2=20')
parent1.constrain(box2, 'll_edge=0, sy1=oy2+5, swidth=30, sheight=15', box1)
parent1.constrain(box3, 'll_edge=0, sy1=oy2+5, swidth=25, sheight=12', box2)

parent1.solver()

print(f"  box1: x=[{box1.x1}, {box1.x2}], all left edges at x={box1.x1}")
print(f"  box2: x=[{box2.x1}, {box2.x2}]")
print(f"  box3: x=[{box3.x1}, {box3.x2}]")
print("  [Result] All boxes left-aligned using ll_edge=0")

# Example 2: Right alignment
print("\n[Example 2] Right alignment using rr_edge=0")
print("-" * 70)

parent2 = Cell('parent2')
r1 = Cell('r1', 'metal1')
r2 = Cell('r2', 'metal2')
r3 = Cell('r3', 'poly')

parent2.constrain(r1, 'x1=10, y1=0, x2=50, y2=20')
parent2.constrain(r2, 'rr_edge=0, sy1=oy2+5, swidth=30, sheight=15', r1)
parent2.constrain(r3, 'rr_edge=0, sy1=oy2+5, swidth=25, sheight=12', r2)

parent2.solver()

print(f"  r1: x=[{r1.x1}, {r1.x2}], all right edges at x={r1.x2}")
print(f"  r2: x=[{r2.x1}, {r2.x2}]")
print(f"  r3: x=[{r3.x1}, {r3.x2}]")
print("  [Result] All boxes right-aligned using rr_edge=0")

# Example 3: Overlap detection
print("\n[Example 3] Overlap detection with lr_edge")
print("-" * 70)

parent3 = Cell('parent3')
o1 = Cell('o1', 'metal1')
o2 = Cell('o2', 'metal2')

parent3.constrain(o1, 'x1=0, y1=0, x2=40, y2=20')
parent3.constrain(o2, 'x1=30, y1=5, x2=60, y2=25')  # Overlaps with o1

parent3.solver()

lr_value = o2.x1 - o1.x2
print(f"  o1: x=[{o1.x1}, {o1.x2}]")
print(f"  o2: x=[{o2.x1}, {o2.x2}]")
print(f"  lr_edge = {lr_value} (negative = overlap!)")
if lr_value < 0:
    print(f"  [Detection] Boxes overlap by {-lr_value} units")
else:
    print(f"  [Detection] No overlap, gap of {lr_value} units")

# Example 4: Mixed alignments
print("\n[Example 4] Mixed: left-aligned vertically, bottom-aligned")
print("-" * 70)

parent4 = Cell('parent4')
m1 = Cell('m1', 'metal1')
m2 = Cell('m2', 'metal2')
m3 = Cell('m3', 'poly')

parent4.constrain(m1, 'x1=0, y1=0, x2=30, y2=20')
parent4.constrain(m2, 'sx1=ox2+5, bb_edge=0, swidth=25, sheight=20', m1)
parent4.constrain(m3, 'sx1=ox2+5, bb_edge=0, swidth=20, sheight=20', m2)

parent4.solver()

print(f"  m1: [{m1.x1}, {m1.y1}, {m1.x2}, {m1.y2}]")
print(f"  m2: [{m2.x1}, {m2.y1}, {m2.x2}, {m2.y2}]")
print(f"  m3: [{m3.x1}, {m3.y1}, {m3.x2}, {m3.y2}]")
print(f"  [Result] Horizontal row with bb_edge=0 (bottom-aligned)")

# Create visualization
print("\n[Visualization] Creating plots...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

# Plot 1: Left alignment
parent1._draw_recursive(ax1)
ax1.set_aspect('equal')
ax1.set_xlim(-5, 45)
ax1.set_ylim(-5, 55)
ax1.grid(True, alpha=0.3)
ax1.set_title('Example 1: Left Alignment (ll_edge=0)', fontsize=12, weight='bold')
ax1.set_xlabel('All boxes aligned to left edge')

# Plot 2: Right alignment
parent2._draw_recursive(ax2)
ax2.set_aspect('equal')
ax2.set_xlim(5, 55)
ax2.set_ylim(-5, 55)
ax2.grid(True, alpha=0.3)
ax2.set_title('Example 2: Right Alignment (rr_edge=0)', fontsize=12, weight='bold')
ax2.set_xlabel('All boxes aligned to right edge')

# Plot 3: Overlap detection
parent3._draw_recursive(ax3)
ax3.set_aspect('equal')
ax3.set_xlim(-5, 65)
ax3.set_ylim(-5, 30)
ax3.grid(True, alpha=0.3)
ax3.set_title('Example 3: Overlap Detection (lr_edge<0)', fontsize=12, weight='bold')
ax3.set_xlabel(f'lr_edge={lr_value} (overlap detected!)')

# Plot 4: Horizontal row with bottom alignment
parent4._draw_recursive(ax4)
ax4.set_aspect('equal')
ax4.set_xlim(-5, 85)
ax4.set_ylim(-5, 30)
ax4.grid(True, alpha=0.3)
ax4.set_title('Example 4: Horizontal Row (bb_edge=0)', fontsize=12, weight='bold')
ax4.set_xlabel('Bottom edges aligned')

plt.tight_layout()
plt.savefig('demo_outputs/example_edge_keywords.png', dpi=150, bbox_inches='tight')
print("  Saved to: demo_outputs/example_edge_keywords.png")

print("\n" + "="*70)
print("Examples completed!")
print("="*70)

print("\nKey Takeaways:")
print("  1. ll_edge=0 → Left edges aligned")
print("  2. rr_edge=0 → Right edges aligned")
print("  3. bb_edge=0 → Bottom edges aligned")
print("  4. tt_edge=0 → Top edges aligned")
print("  5. lr_edge<0 → Horizontal overlap detected")
print("  6. tb_edge<0 → Vertical overlap detected")
print("  7. Edge keywords work great with positioning keywords (sx1=ox2+10)")
