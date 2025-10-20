#!/usr/bin/env python3
"""
Test and demonstrate line_style and zorder features for layer styles
"""

from layout_automation import Cell
from layout_automation.style_config import get_style_config
import matplotlib.pyplot as plt

print("="*70)
print("Testing line_style and zorder Features")
print("="*70)

# Get style config
style_config = get_style_config()

# Test 1: Set different line styles for different layers
print("\nTest 1: Setting different line styles")
style_config.set_layer_style('metal1', color='blue', alpha=0.6, line_style='-')  # solid
style_config.set_layer_style('metal2', color='red', alpha=0.6, line_style='--')  # dashed
style_config.set_layer_style('poly', color='purple', alpha=0.6, line_style='-.')  # dashdot
style_config.set_layer_style('diff', color='brown', alpha=0.6, line_style=':')  # dotted

# Verify styles were set
metal1_style = style_config.get_layer_style('metal1')
metal2_style = style_config.get_layer_style('metal2')
poly_style = style_config.get_layer_style('poly')
diff_style = style_config.get_layer_style('diff')

print(f"  metal1 line_style: {metal1_style.line_style}")
print(f"  metal2 line_style: {metal2_style.line_style}")
print(f"  poly line_style: {poly_style.line_style}")
print(f"  diff line_style: {diff_style.line_style}")

assert metal1_style.line_style == '-'
assert metal2_style.line_style == '--'
assert poly_style.line_style == '-.'
assert diff_style.line_style == ':'
print("  [PASS] Line styles set correctly")

# Test 2: Set different zorder values
print("\nTest 2: Setting different zorder values")
style_config.set_layer_style('metal1', zorder=3)  # Draw on top
style_config.set_layer_style('metal2', zorder=2)
style_config.set_layer_style('poly', zorder=1)    # Draw on bottom

# Verify zorder values
metal1_style = style_config.get_layer_style('metal1')
metal2_style = style_config.get_layer_style('metal2')
poly_style = style_config.get_layer_style('poly')

print(f"  metal1 zorder: {metal1_style.zorder} (top)")
print(f"  metal2 zorder: {metal2_style.zorder} (middle)")
print(f"  poly zorder: {poly_style.zorder} (bottom)")

assert metal1_style.zorder == 3
assert metal2_style.zorder == 2
assert poly_style.zorder == 1
print("  [PASS] zorder values set correctly")

# Test 3: Create a layout to visualize the styles
print("\nTest 3: Creating layout with overlapping layers")
parent = Cell('parent')

# Create overlapping rectangles to demonstrate zorder
poly_layer = Cell('poly_rect', 'poly')
metal2_layer = Cell('metal2_rect', 'metal2')
metal1_layer = Cell('metal1_rect', 'metal1')

# Position them so they overlap
parent.constrain(poly_layer, 'x1=0, y1=0, x2=50, y2=50')
parent.constrain(metal2_layer, 'x1=25, y1=25, x2=75, y2=75')
parent.constrain(metal1_layer, 'x1=50, y1=50, x2=100, y2=100')

parent.solver()

print(f"  poly_rect: {poly_layer.pos_list}")
print(f"  metal2_rect: {metal2_layer.pos_list}")
print(f"  metal1_rect: {metal1_layer.pos_list}")
print("  [PASS] Layout created successfully")

# Test 4: Verify container style also has zorder
print("\nTest 4: Container style zorder")
style_config.set_container_style(zorder=5)
container_zorder = style_config.container_style.zorder
print(f"  Container zorder: {container_zorder}")
assert container_zorder == 5
print("  [PASS] Container zorder set correctly")

# Test 5: Visual test - create a plot
print("\nTest 5: Creating visual plot to demonstrate styles")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Left plot: Different line styles
print("  Drawing plot 1: Different line styles")
parent1 = Cell('parent1')
rect1 = Cell('solid', 'metal1')
rect2 = Cell('dashed', 'metal2')
rect3 = Cell('dashdot', 'poly')
rect4 = Cell('dotted', 'diff')

parent1.constrain(rect1, 'x1=0, y1=0, x2=20, y2=15')
parent1.constrain(rect2, 'x1=25, y1=0, x2=45, y2=15')
parent1.constrain(rect3, 'x1=50, y1=0, x2=70, y2=15')
parent1.constrain(rect4, 'x1=75, y1=0, x2=95, y2=15')

parent1.solver()
parent1._draw_recursive(ax1)

ax1.set_aspect('equal')
ax1.set_xlim(-5, 100)
ax1.set_ylim(-5, 20)
ax1.grid(True, alpha=0.3)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_title('Line Styles: solid (-), dashed (--), dashdot (-.), dotted (:)')

# Right plot: zorder demonstration with overlapping layers
print("  Drawing plot 2: zorder demonstration (overlapping)")
parent._draw_recursive(ax2)

ax2.set_aspect('equal')
ax2.set_xlim(-10, 110)
ax2.set_ylim(-10, 110)
ax2.grid(True, alpha=0.3)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_title('zorder: poly(1/bottom), metal2(2/middle), metal1(3/top)')

plt.tight_layout()
plt.savefig('demo_outputs/test_line_style_zorder.png', dpi=150, bbox_inches='tight')
print("  Saved plot to: demo_outputs/test_line_style_zorder.png")
print("  [PASS] Visual plot created")

print("\n" + "="*70)
print("All line_style and zorder tests passed!")
print("="*70)

print("\nFeatures demonstrated:")
print("  1. line_style: Control edge line style ('-', '--', '-.', ':')")
print("  2. zorder: Control drawing order (higher = on top)")
print("  3. Works for both layer styles and container styles")
print("  4. Easy to set via set_layer_style() and set_container_style()")
