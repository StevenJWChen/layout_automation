#!/usr/bin/env python3
"""
Test and demonstrate improved label rendering

Features demonstrated:
1. Smart label sizing based on cell dimensions
2. Reduced font size and weight for better readability
3. Label modes: auto, full, compact, none
4. Semi-transparent backgrounds to avoid overlap
"""

from layout_automation import Cell
import matplotlib.pyplot as plt

print("="*70)
print("Testing Label Improvements")
print("="*70)

# Create a layout with various cell sizes
parent = Cell('test_layout')

# Large cells
large1 = Cell('large_cell_1', 'metal1')
large2 = Cell('large_cell_2', 'metal2')

# Medium cells
med1 = Cell('medium_1', 'poly')
med2 = Cell('medium_2', 'active')
med3 = Cell('medium_3', 'metal1')

# Small cells
small1 = Cell('small_1', 'contact')
small2 = Cell('small_2', 'via')
small3 = Cell('small_3', 'contact')

# Very small cells
tiny1 = Cell('tiny1', 'metal1')
tiny2 = Cell('tiny2', 'contact')

parent.add_instance([large1, large2, med1, med2, med3, small1, small2, small3, tiny1, tiny2])

# Layout with various sizes
parent.constrain(large1, 'x1=0, y1=0, x2=50, y2=40')
parent.constrain(large2, 'x1=60, y1=0, x2=110, y2=40')

parent.constrain(med1, 'x1=0, y1=50, x2=20, y2=70')
parent.constrain(med2, 'x1=25, y1=50, x2=45, y2=70')
parent.constrain(med3, 'x1=50, y1=50, x2=70, y2=70')

parent.constrain(small1, 'x1=0, y1=75, x2=8, y2=82')
parent.constrain(small2, 'x1=12, y1=75, x2=20, y2=82')
parent.constrain(small3, 'x1=24, y1=75, x2=32, y2=82')

parent.constrain(tiny1, 'x1=0, y1=87, x2=3, y2=90')
parent.constrain(tiny2, 'x1=5, y1=87, x2=8, y2=90')

parent.solver()

print("\n[Test 1] Auto mode (smart sizing)")
print("-" * 70)
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Mode 1: Auto (default - smart sizing)
parent.draw(ax=axes[0, 0], show=False, solve_first=False, label_mode='auto')
axes[0, 0].set_title('Auto Mode (Smart Sizing)', fontsize=14, weight='bold')
axes[0, 0].set_xlabel('Labels sized based on cell dimensions\nSmall cells get smaller labels or none')

# Mode 2: Full (always show full labels)
parent.draw(ax=axes[0, 1], show=False, solve_first=False, label_mode='full')
axes[0, 1].set_title('Full Mode', fontsize=14, weight='bold')
axes[0, 1].set_xlabel('Always show name + layer (can be cluttered)')

# Mode 3: Compact (abbreviated)
parent.draw(ax=axes[1, 0], show=False, solve_first=False, label_mode='compact')
axes[1, 0].set_title('Compact Mode', fontsize=14, weight='bold')
axes[1, 0].set_xlabel('Abbreviated names only')

# Mode 4: None (no labels)
parent.draw(ax=axes[1, 1], show=False, solve_first=False, label_mode='none')
axes[1, 1].set_title('No Labels Mode', fontsize=14, weight='bold')
axes[1, 1].set_xlabel('Clean layout without labels')

plt.tight_layout()
plt.savefig('demo_outputs/test_label_modes.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_label_modes.png")

print("\n[Test 2] Dense layout with many small cells")
print("-" * 70)

# Create a dense layout to test overlap avoidance
dense = Cell('dense_layout')
cells = []

for i in range(10):
    for j in range(10):
        cell = Cell(f'c{i}_{j}', ['metal1', 'metal2', 'poly'][((i+j) % 3)])
        cells.append(cell)
        dense.add_instance(cell)
        dense.constrain(cell, f'x1={i*6}, y1={j*6}, x2={i*6+5}, y2={j*6+5}')

dense.solver()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Without smart labels (full mode - cluttered)
dense.draw(ax=ax1, show=False, solve_first=False, label_mode='full')
ax1.set_title('Full Mode (Cluttered)', fontsize=14, weight='bold')

# With smart labels (auto mode - clean)
dense.draw(ax=ax2, show=False, solve_first=False, label_mode='auto')
ax2.set_title('Auto Mode (Clean)', fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('demo_outputs/test_dense_layout.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_dense_layout.png")

print("\n[Test 3] Real-world example with my_demo.py layout")
print("-" * 70)

from layout_automation.tech_file import TechFile, set_tech_file
from layout_automation.style_config import reset_style_config

# Load tech file
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')
set_tech_file(tech)
reset_style_config()
tech.apply_colors_to_style()

# Import the hierarchical layout from my_demo
imported = Cell.from_gds('demo_outputs/virtuoso_demo.gds', use_tech_file=True)
inst1 = imported.copy('chip1')
inst2 = imported.copy('chip2')

top = Cell('top_level')
top.add_instance([inst1, inst2])
top.constrain(inst1, 'x1=0, y1=0')
top.constrain(inst2, 'sx1=ox2+10, y1=0', inst1)
top.solver()

# Compare old vs new
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Old style (full labels)
top.draw(ax=ax1, show=False, solve_first=False, label_mode='full')
ax1.set_title('Old Style (Full Labels)', fontsize=14, weight='bold')

# New style (auto labels)
top.draw(ax=ax2, show=False, solve_first=False, label_mode='auto')
ax2.set_title('New Style (Smart Labels)', fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('demo_outputs/test_real_world_labels.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: demo_outputs/test_real_world_labels.png")

print("\n" + "="*70)
print("ALL TESTS COMPLETED!")
print("="*70)

print("\nLabel Modes Summary:")
print("  - 'auto':    Smart sizing based on cell dimensions (RECOMMENDED)")
print("  - 'full':    Always show name + layer")
print("  - 'compact': Abbreviated names only")
print("  - 'none':    No labels")

print("\nImprovements:")
print("  [OK] Smaller, thinner fonts (more readable)")
print("  [OK] Smart sizing based on cell dimensions")
print("  [OK] Semi-transparent backgrounds to reduce overlap")
print("  [OK] Very small cells get no labels to avoid clutter")
print("  [OK] Container labels smaller and less intrusive")

print("\nGenerated files:")
print("  - test_label_modes.png       : Comparison of all label modes")
print("  - test_dense_layout.png      : Dense layout showing smart sizing")
print("  - test_real_world_labels.png : Real-world example comparison")
