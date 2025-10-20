#!/usr/bin/env python3
"""
Practical examples using line_style and zorder for layer styling
"""

from layout_automation import Cell
from layout_automation.style_config import get_style_config
import matplotlib.pyplot as plt

print("="*70)
print("Practical Examples: line_style and zorder")
print("="*70)

# Get style config
style_config = get_style_config()

# Example 1: Using line_style for visual differentiation
print("\nExample 1: Using line styles to differentiate layer types")
print("-" * 70)

# Set line styles based on layer purpose
style_config.set_layer_style('metal1', color='blue', line_style='-', edge_width=2.0)      # Solid for metal
style_config.set_layer_style('poly', color='red', line_style='--', edge_width=2.0)        # Dashed for poly
style_config.set_layer_style('nwell', color='lightgreen', line_style='-.', edge_width=1.5, alpha=0.3)  # Dashdot for wells
style_config.set_layer_style('pwell', color='lightcoral', line_style=':', edge_width=1.5, alpha=0.3)   # Dotted for wells

print("  Set line styles:")
print("    metal1: solid (-) - for metal layers")
print("    poly: dashed (--) - for polysilicon")
print("    nwell: dashdot (-.) - for n-wells")
print("    pwell: dotted (:) - for p-wells")

# Example 2: Using zorder for layering hierarchy
print("\nExample 2: Using zorder to control layer stacking")
print("-" * 70)

# Set zorder based on physical layer stack
style_config.set_layer_style('nwell', zorder=0)     # Bottom - substrate/wells
style_config.set_layer_style('pwell', zorder=0)
style_config.set_layer_style('poly', zorder=1)      # Above substrate
style_config.set_layer_style('diff', zorder=1)
style_config.set_layer_style('contact', zorder=2)   # Middle - contacts
style_config.set_layer_style('metal1', zorder=3)    # Top - metal layers
style_config.set_layer_style('via', zorder=4)
style_config.set_layer_style('metal2', zorder=5)

print("  Set zorder hierarchy (bottom to top):")
print("    zorder 0: nwell, pwell (substrate)")
print("    zorder 1: poly, diff (transistor level)")
print("    zorder 2: contact")
print("    zorder 3: metal1")
print("    zorder 4: via")
print("    zorder 5: metal2")

# Example 3: Create a simple transistor layout with proper styling
print("\nExample 3: Creating a transistor layout with styled layers")
print("-" * 70)

transistor = Cell('transistor')

# Create layers in a transistor structure
nwell = Cell('nwell', 'nwell')
poly = Cell('gate', 'poly')
metal1_s = Cell('source', 'metal1')
metal1_d = Cell('drain', 'metal1')
contact1 = Cell('contact_s', 'contact')
contact2 = Cell('contact_d', 'contact')

# Position the layers
transistor.constrain(nwell, 'x1=0, y1=0, x2=80, y2=60')
transistor.constrain(poly, 'x1=35, y1=10, x2=45, y2=50')
transistor.constrain(contact1, 'x1=15, y1=20, x2=25, y2=40')
transistor.constrain(contact2, 'x1=55, y1=20, x2=65, y2=40')
transistor.constrain(metal1_s, 'x1=10, y1=15, x2=30, y2=45')
transistor.constrain(metal1_d, 'x1=50, y1=15, x2=70, y2=45')

transistor.solver()

print("  Created transistor with:")
print(f"    nwell: {nwell.pos_list}")
print(f"    poly gate: {poly.pos_list}")
print(f"    contacts: {contact1.pos_list}, {contact2.pos_list}")
print(f"    metal1 (S/D): {metal1_s.pos_list}, {metal1_d.pos_list}")

# Example 4: Compare with and without zorder
print("\nExample 4: Visual comparison - with and without zorder")
print("-" * 70)

# Create two identical layouts
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Left: Without proper zorder (all same zorder)
print("  Plot 1: Without zorder (overlaps not controlled)")
for layer_name in ['nwell', 'poly', 'metal1', 'contact']:
    style_config.set_layer_style(layer_name, zorder=1)  # All same

transistor._draw_recursive(ax1)
ax1.set_aspect('equal')
ax1.set_xlim(-10, 90)
ax1.set_ylim(-10, 70)
ax1.grid(True, alpha=0.3)
ax1.set_title('Without zorder (all layers at same level)')

# Right: With proper zorder
print("  Plot 2: With proper zorder (correct stacking)")
style_config.set_layer_style('nwell', zorder=0)
style_config.set_layer_style('poly', zorder=1)
style_config.set_layer_style('contact', zorder=2)
style_config.set_layer_style('metal1', zorder=3)

transistor2 = Cell('transistor2')
nwell2 = Cell('nwell2', 'nwell')
poly2 = Cell('gate2', 'poly')
metal1_s2 = Cell('source2', 'metal1')
metal1_d2 = Cell('drain2', 'metal1')
contact1_2 = Cell('contact_s2', 'contact')
contact2_2 = Cell('contact_d2', 'contact')

transistor2.constrain(nwell2, 'x1=0, y1=0, x2=80, y2=60')
transistor2.constrain(poly2, 'x1=35, y1=10, x2=45, y2=50')
transistor2.constrain(contact1_2, 'x1=15, y1=20, x2=25, y2=40')
transistor2.constrain(contact2_2, 'x1=55, y1=20, x2=65, y2=40')
transistor2.constrain(metal1_s2, 'x1=10, y1=15, x2=30, y2=45')
transistor2.constrain(metal1_d2, 'x1=50, y1=15, x2=70, y2=45')

transistor2.solver()
transistor2._draw_recursive(ax2)
ax2.set_aspect('equal')
ax2.set_xlim(-10, 90)
ax2.set_ylim(-10, 70)
ax2.grid(True, alpha=0.3)
ax2.set_title('With zorder (proper layer stacking)')

plt.tight_layout()
plt.savefig('demo_outputs/example_line_style_zorder.png', dpi=150, bbox_inches='tight')
print("  Saved plot to: demo_outputs/example_line_style_zorder.png")

print("\n" + "="*70)
print("Examples completed successfully!")
print("="*70)

print("\nKey Takeaways:")
print("  1. line_style helps visually distinguish layer types")
print("  2. zorder ensures correct physical layer stacking")
print("  3. Higher zorder values appear on top")
print("  4. Containers default to zorder=0 (behind layers)")
print("  5. Both features work seamlessly with existing styles")
