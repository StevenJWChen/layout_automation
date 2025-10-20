#!/usr/bin/env python3
"""
Comprehensive test of all new features:
1. fix_layout() with duplicate cell names
2. Cell position properties (x1, y1, x2, y2, width, height, cx, cy)
3. line_style and zorder for layer styling
"""

from layout_automation import Cell
from layout_automation.style_config import get_style_config

print("="*70)
print("Comprehensive Test: All New Features")
print("="*70)

# Feature 1: fix_layout() with duplicate cell names
print("\n[1] Testing fix_layout() with duplicate cell names")
print("-" * 70)

block1 = Cell('duplicate', 'metal1')
block2 = Cell('duplicate', 'metal2')
block3 = Cell('duplicate', 'poly')

parent = Cell('parent')
parent.constrain(block1, 'x1=0, y1=0, x2=10, y2=10')
parent.constrain(block2, 'x1=20, y1=0, x2=30, y2=10')
parent.constrain(block3, 'x1=40, y1=0, x2=50, y2=10')

parent.solver()
parent.fix_layout()
parent.set_position(100, 50)

# Verify using position properties
assert block1.x1 == 100 and block1.width == 10
assert block2.x1 == 120 and block2.width == 10
assert block3.x1 == 140 and block3.width == 10

print(f"  block1 (duplicate): pos=({block1.x1}, {block1.y1}), size={block1.width}x{block1.height}")
print(f"  block2 (duplicate): pos=({block2.x1}, {block2.y1}), size={block2.width}x{block2.height}")
print(f"  block3 (duplicate): pos=({block3.x1}, {block3.y1}), size={block3.width}x{block3.height}")
print("  [PASS] fix_layout() works with duplicate names")

# Feature 2: Cell position properties
print("\n[2] Testing Cell position properties")
print("-" * 70)

test_cell = Cell('test_cell')
rect = Cell('rect', 'metal1')
test_cell.constrain(rect, 'x1=10, y1=20, x2=60, y2=80')
test_cell.solver()

# Test all properties
print(f"  Corner coordinates: ({rect.x1}, {rect.y1}) to ({rect.x2}, {rect.y2})")
print(f"  Dimensions: {rect.width} x {rect.height}")
print(f"  Center: ({rect.cx}, {rect.cy})")

assert rect.x1 == 10
assert rect.y1 == 20
assert rect.x2 == 60
assert rect.y2 == 80
assert rect.width == 50
assert rect.height == 60
assert rect.cx == 35.0
assert rect.cy == 50.0

print("  [PASS] All position properties correct")

# Feature 3: line_style and zorder
print("\n[3] Testing line_style and zorder")
print("-" * 70)

style_config = get_style_config()

# Set different line styles
style_config.set_layer_style('metal1', line_style='-', zorder=3)
style_config.set_layer_style('metal2', line_style='--', zorder=2)
style_config.set_layer_style('poly', line_style='-.', zorder=1)

# Verify styles
m1_style = style_config.get_layer_style('metal1')
m2_style = style_config.get_layer_style('metal2')
p_style = style_config.get_layer_style('poly')

print(f"  metal1: line_style={m1_style.line_style}, zorder={m1_style.zorder}")
print(f"  metal2: line_style={m2_style.line_style}, zorder={m2_style.zorder}")
print(f"  poly: line_style={p_style.line_style}, zorder={p_style.zorder}")

assert m1_style.line_style == '-'
assert m1_style.zorder == 3
assert m2_style.line_style == '--'
assert m2_style.zorder == 2
assert p_style.line_style == '-.'
assert p_style.zorder == 1

print("  [PASS] line_style and zorder set correctly")

# Feature 4: All features working together
print("\n[4] Testing all features together")
print("-" * 70)

# Create a layout using all new features
combined = Cell('combined')

# Create cells with duplicate names (feature 1)
layer1 = Cell('layer', 'metal1')  # zorder=3, solid
layer2 = Cell('layer', 'metal2')  # zorder=2, dashed
layer3 = Cell('layer', 'poly')    # zorder=1, dashdot

# Use constraint system
combined.constrain(layer1, 'x1=0, y1=0, x2=30, y2=30')
combined.constrain(layer2, 'sx1=ox1+10, sy1=oy1+10, sx2-sx1=30, sy2-sy1=30', layer1)
combined.constrain(layer3, 'sx1=ox1+10, sy1=oy1+10, sx2-sx1=30, sy2-sy1=30', layer2)

combined.solver()

# Use properties to verify (feature 2)
print(f"  layer1 (metal1): center=({layer1.cx}, {layer1.cy}), size={layer1.width}x{layer1.height}")
print(f"  layer2 (metal2): center=({layer2.cx}, {layer2.cy}), size={layer2.width}x{layer2.height}")
print(f"  layer3 (poly): center=({layer3.cx}, {layer3.cy}), size={layer3.width}x{layer3.height}")

# Verify positions using properties
assert layer1.x1 == 0 and layer1.y1 == 0
assert layer2.x1 == 10 and layer2.y1 == 10
assert layer3.x1 == 20 and layer3.y1 == 20

assert layer1.width == 30 and layer1.height == 30
assert layer2.width == 30 and layer2.height == 30
assert layer3.width == 30 and layer3.height == 30

# Fix and reposition (feature 1)
combined.fix_layout()
combined.set_position(200, 100)

# Verify all children moved using properties (feature 2)
print(f"\n  After repositioning parent to (200, 100):")
print(f"  layer1: pos=({layer1.x1}, {layer1.y1}), center=({layer1.cx}, {layer1.cy})")
print(f"  layer2: pos=({layer2.x1}, {layer2.y1}), center=({layer2.cx}, {layer2.cy})")
print(f"  layer3: pos=({layer3.x1}, {layer3.y1}), center=({layer3.cx}, {layer3.cy})")

assert layer1.x1 == 200 and layer1.y1 == 100
assert layer2.x1 == 210 and layer2.y1 == 110
assert layer3.x1 == 220 and layer3.y1 == 120

print("  [PASS] All features work together correctly")

# Summary
print("\n" + "="*70)
print("ALL TESTS PASSED!")
print("="*70)

print("\nFeatures Verified:")
print("  [OK] fix_layout() handles duplicate cell names")
print("  [OK] Position properties (x1, y1, x2, y2, width, height, cx, cy)")
print("  [OK] line_style and zorder for layer styling")
print("  [OK] All features work together seamlessly")

print("\nNew Features Summary:")
print("  1. Fix layout with duplicate names: Use id() instead of name")
print("  2. Position properties: Readable access to coordinates")
print("  3. line_style: Visual differentiation ('-', '--', '-.', ':')")
print("  4. zorder: Control drawing order (higher = on top)")
