#!/usr/bin/env python3
"""
Test and demonstrate label position options

Demonstrates:
1. Top-left corner placement (default, best for overlap avoidance)
2. All corner positions
3. Center position (old behavior)
4. Comparison of center vs corner labels
"""

from layout_automation import Cell
import matplotlib.pyplot as plt

print("="*70)
print("Testing Label Position Options")
print("="*70)

# Create a test layout with overlapping cells
parent = Cell('test_positions')

# Create cells of various sizes
cells = []
positions_data = [
    ('large1', 'metal1', 0, 0, 40, 30),
    ('large2', 'metal2', 50, 0, 90, 30),
    ('medium1', 'poly', 0, 35, 25, 55),
    ('medium2', 'active', 30, 35, 55, 55),
    ('medium3', 'metal1', 60, 35, 85, 55),
    ('small1', 'contact', 0, 60, 10, 70),
    ('small2', 'via', 15, 60, 25, 70),
    ('small3', 'contact', 30, 60, 40, 70),
]

for name, layer, x1, y1, x2, y2 in positions_data:
    cell = Cell(name, layer)
    cells.append(cell)
    parent.add_instance(cell)
    parent.constrain(cell, f'x1={x1}, y1={y1}, x2={x2}, y2={y2}')

parent.solver()

# Test 1: Compare all label positions
print("\n[Test 1] All label positions")
print("-" * 70)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

positions = [
    ('top-left', 'Top-Left (Default)\nBest for avoiding overlap'),
    ('top-right', 'Top-Right\nAlternative corner'),
    ('bottom-left', 'Bottom-Left\nLower corner option'),
    ('bottom-right', 'Bottom-Right\nOpposite corner'),
    ('center', 'Center\nOld behavior'),
]

for idx, (pos, title) in enumerate(positions):
    row = idx // 3
    col = idx % 3
    ax = axes[row, col]

    parent.draw(ax=ax, show=False, solve_first=False,
               label_mode='auto', label_position=pos)
    ax.set_title(title, fontsize=12, weight='bold')
    print(f"  Drew with position: {pos}")

# Hide the extra subplot
axes[1, 2].axis('off')

plt.tight_layout()
plt.savefig('demo_outputs/test_label_positions_all.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_label_positions_all.png")

# Test 2: Direct comparison - Center vs Top-Left
print("\n[Test 2] Center vs Top-Left comparison")
print("-" * 70)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Center (old way)
parent.draw(ax=ax1, show=False, solve_first=False,
           label_mode='auto', label_position='center')
ax1.set_title('Center Position (Old Behavior)\nLabels can overlap more',
             fontsize=14, weight='bold')

# Top-left (new default)
parent.draw(ax=ax2, show=False, solve_first=False,
           label_mode='auto', label_position='top-left')
ax2.set_title('Top-Left Position (New Default)\nBetter overlap avoidance',
             fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('demo_outputs/test_center_vs_topleft.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_center_vs_topleft.png")

# Test 3: Dense layout showing improvement
print("\n[Test 3] Dense layout comparison")
print("-" * 70)

dense = Cell('dense')
dense_cells = []

# Create 6x6 grid of cells
for i in range(6):
    for j in range(6):
        cell = Cell(f'c{i}_{j}', ['metal1', 'metal2', 'poly'][(i+j) % 3])
        dense_cells.append(cell)
        dense.add_instance(cell)
        dense.constrain(cell, f'x1={i*12}, y1={j*12}, x2={i*12+10}, y2={j*12+10}')

dense.solver()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Center position
dense.draw(ax=ax1, show=False, solve_first=False,
          label_mode='auto', label_position='center')
ax1.set_title('Dense Layout - Center Labels\nMore overlap in tight spaces',
             fontsize=14, weight='bold')

# Top-left position
dense.draw(ax=ax2, show=False, solve_first=False,
          label_mode='auto', label_position='top-left')
ax2.set_title('Dense Layout - Top-Left Labels\nCleaner, less overlap',
             fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('demo_outputs/test_dense_position_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_dense_position_comparison.png")

# Test 4: With the imported GDS (real-world)
print("\n[Test 4] Real-world GDS layout")
print("-" * 70)

from layout_automation.tech_file import TechFile, set_tech_file
from layout_automation.style_config import reset_style_config

tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')
set_tech_file(tech)
reset_style_config()
tech.apply_colors_to_style()

imported = Cell.from_gds('demo_outputs/virtuoso_demo.gds', use_tech_file=True)
inst1 = imported.copy('chip1')
inst2 = imported.copy('chip2')

top = Cell('top_level')
top.add_instance([inst1, inst2])
top.constrain(inst1, 'x1=0, y1=0')
top.constrain(inst2, 'sx1=ox2+10, y1=0', inst1)
top.solver()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Center labels
top.draw(ax=ax1, show=False, solve_first=False,
        label_mode='auto', label_position='center')
ax1.set_title('Real GDS - Center Labels', fontsize=14, weight='bold')

# Top-left labels
top.draw(ax=ax2, show=False, solve_first=False,
        label_mode='auto', label_position='top-left')
ax2.set_title('Real GDS - Top-Left Labels (Cleaner)', fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('demo_outputs/test_gds_position_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_gds_position_comparison.png")

print("\n" + "="*70)
print("ALL TESTS COMPLETED!")
print("="*70)

print("\nLabel Position Options:")
print("  - 'top-left':     Upper left corner (DEFAULT, recommended)")
print("  - 'top-right':    Upper right corner")
print("  - 'bottom-left':  Lower left corner")
print("  - 'bottom-right': Lower right corner")
print("  - 'center':       Center of cell (old behavior)")

print("\nWhy Top-Left is Best:")
print("  [OK] Labels stack naturally (like reading text)")
print("  [OK] Less overlap with adjacent cells")
print("  [OK] Consistent positioning across all cells")
print("  [OK] Easy to scan visually")
print("  [OK] Works well with hierarchical layouts")

print("\nUsage:")
print("  cell.draw()  # Uses top-left by default")
print("  cell.draw(label_position='center')  # Old behavior")
print("  cell.draw(label_position='top-right')  # Alternative")

print("\nGenerated files:")
print("  - test_label_positions_all.png       : All 5 position options")
print("  - test_center_vs_topleft.png         : Direct comparison")
print("  - test_dense_position_comparison.png : Dense layout comparison")
print("  - test_gds_position_comparison.png   : Real GDS comparison")
