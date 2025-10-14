#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Constrain and Auto-Add Instance Features Demonstration

This example demonstrates two powerful convenience features:

1. **Self-Constraint**: Constrain a cell's own bounding box
   - Syntax: cell.constrain('x2-x1=100, y2-y1=50')
   - Useful for: Fixed sizes, aspect ratios, minimum dimensions

2. **Auto-Add Instance**: Automatically add instances when referenced in constraints
   - No need for explicit add_instance() calls
   - Syntax: parent.constrain(child1, ..., child2) automatically adds children
   - Simplifies code and reduces boilerplate

Use Cases:
- Define standard cell sizes
- Create frames with fixed dimensions
- Build layouts without manual instance management
- Ensure minimum spacing and dimensions
"""

import os
from layout_automation.cell import Cell

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

print("=" * 70)
print("SELF-CONSTRAIN AND AUTO-ADD INSTANCE DEMONSTRATION")
print("=" * 70)
print()

# ==============================================================================
# EXAMPLE 1: Self-Constraint for Fixed Cell Size
# ==============================================================================

print("Example 1: Self-Constraint for Fixed Cell Size")
print("-" * 70)
print()

# Create standard cells with fixed sizes using self-constraints
inverter = Cell('INV_X1', 'metal1')
inverter.constrain('x2-x1=30, y2-y1=40')  # Self-constrain size

buffer = Cell('BUF_X1', 'metal1')
buffer.constrain('x2-x1=40, y2-y1=40')    # Self-constrain size

print("Created standard cells with self-constrained sizes:")
print(f"  INV_X1: 30x40")
print(f"  BUF_X1: 40x40")
print()

# Create circuit using these cells
circuit = Cell('circuit')

# Auto-add feature: just reference cells in constraints, no add_instance() needed!
circuit.constrain(inverter, 'x1=10, y1=10')
circuit.constrain(inverter, 'sx2+20=ox1, sy1=oy1', buffer)

print("Building circuit (auto-adding instances)...")
result = circuit.solver()

if result:
    print(f"✓ Circuit solved")
    print(f"  inverter: {inverter.pos_list}")
    print(f"  buffer: {buffer.pos_list}")
    print(f"  circuit: {circuit.pos_list}")

    # Verify fixed sizes
    inv_w = inverter.pos_list[2] - inverter.pos_list[0]
    inv_h = inverter.pos_list[3] - inverter.pos_list[1]
    buf_w = buffer.pos_list[2] - buffer.pos_list[0]
    buf_h = buffer.pos_list[3] - buffer.pos_list[1]

    print(f"\n  Verification:")
    print(f"    INV_X1: {inv_w}x{inv_h} (expected 30x40)")
    print(f"    BUF_X1: {buf_w}x{buf_h} (expected 40x40)")
else:
    print("✗ Circuit solver failed")

print()

# ==============================================================================
# EXAMPLE 2: Auto-Add Without Explicit Instance Management
# ==============================================================================

print("Example 2: Auto-Add Without Explicit Instance Management")
print("-" * 70)
print()

# Create cells
nmos = Cell('nmos', 'diff')
pmos = Cell('pmos', 'diff')
poly = Cell('poly', 'poly')
metal = Cell('metal', 'metal1')

# Create container - starts empty
transistor = Cell('transistor')

print("Building transistor layout (no add_instance calls)...")
print()

# Build entire layout using only constrain() - instances auto-added
# Size the transistor components first with self-constraints
nmos.constrain('x2-x1=20, y2-y1=10')
pmos.constrain('x2-x1=20, y2-y1=10')
poly.constrain('x2-x1=4, y2-y1=27')
metal.constrain('x2-x1=6, y2-y1=8')

# Now position them relative to each other
transistor.constrain(nmos, 'x1=0, y1=0')
transistor.constrain(pmos, 'sx1=ox1, sy2+5=oy1', nmos)
transistor.constrain(poly, 'sx1+8=ox1, sy1-2=oy1', nmos)
transistor.constrain(metal, 'sx1+7=ox1, sy2+1=oy1', pmos)

print(f"Transistor has {len(transistor.children)} children (all auto-added):")
print(f"  {[c.name for c in transistor.children]}")
print()

result = transistor.solver()

if result:
    print(f"✓ Transistor solved")
    print(f"  nmos: {nmos.pos_list}")
    print(f"  pmos: {pmos.pos_list}")
    print(f"  poly: {poly.pos_list}")
    print(f"  metal: {metal.pos_list}")
    print(f"  transistor: {transistor.pos_list}")

    # Draw
    fig = transistor.draw(solve_first=False, show=False)
    import matplotlib.pyplot as plt
    plt.savefig('demo_outputs/self_constrain_transistor.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved to demo_outputs/self_constrain_transistor.png")
else:
    print("✗ Transistor solver failed")

print()

# ==============================================================================
# EXAMPLE 3: Self-Constraint for Container with Padding
# ==============================================================================

print("Example 3: Self-Constraint for Container with Padding")
print("-" * 70)
print()

# Create content cells
content1 = Cell('content1', 'metal1')
content2 = Cell('content2', 'metal2')

# Create frame with auto-add
frame = Cell('frame')

# Size content with self-constraints
content1.constrain('x2-x1=30, y2-y1=30')
content2.constrain('x2-x1=30, y2-y1=30')

# Position content (auto-added)
frame.constrain(content1, 'x1=20, y1=20')
frame.constrain(content2, 'x1=70, y1=70')

# Self-constrain frame to have fixed size (creates padding)
frame.constrain('x2-x1=150, y2-y1=150') # Fix size 150x150

print("Frame with fixed 150x150 size")
print("Content will be positioned inside with padding")
print()

result = frame.solver()

if result:
    print(f"✓ Frame solved")
    print(f"  content1: {content1.pos_list}")
    print(f"  content2: {content2.pos_list}")
    print(f"  frame: {frame.pos_list}")

    # Calculate padding
    fx1, fy1, fx2, fy2 = frame.pos_list
    c1x1, c1y1, c1x2, c1y2 = content1.pos_list
    left_pad = c1x1 - fx1
    bottom_pad = c1y1 - fy1

    print(f"\n  Padding: left={left_pad}, bottom={bottom_pad}")
else:
    print("✗ Frame solver failed")

print()

# ==============================================================================
# EXAMPLE 4: Self-Constraint with Minimum Size
# ==============================================================================

print("Example 4: Self-Constraint with Minimum Size")
print("-" * 70)
print()

# Create small content
tiny1 = Cell('tiny1', 'metal1')
tiny2 = Cell('tiny2', 'metal2')

# Create container with minimum size constraint
min_box = Cell('min_box')

# Position tiny content (auto-added)
min_box.constrain(tiny1, 'x1=5, y1=5')
min_box.constrain(tiny2, 'x1=15, y1=15')

# Self-constrain to have minimum size
min_box.constrain('x2-x1>=100, y2-y1>=80')  # At least 100x80

print("Container with minimum size 100x80")
print("Content is small, so container will expand to meet minimum")
print()

result = min_box.solver()

if result:
    print(f"✓ Min box solved")
    print(f"  tiny1: {tiny1.pos_list}")
    print(f"  tiny2: {tiny2.pos_list}")
    print(f"  min_box: {min_box.pos_list}")

    mx1, my1, mx2, my2 = min_box.pos_list
    width = mx2 - mx1
    height = my2 - my1

    print(f"\n  Final size: {width}x{height}")
    print(f"  Meets minimum: width>={100}, height>={80}")
else:
    print("✗ Min box solver failed")

print()

# ==============================================================================
# EXAMPLE 5: Build Array with Auto-Add and Self-Constraint
# ==============================================================================

print("Example 5: Build Array with Auto-Add and Self-Constraint")
print("-" * 70)
print()

# Create standard cell with fixed size
std_cell = Cell('std_cell', 'metal1')
std_cell.constrain('x2-x1=25, y2-y1=25')  # Self-constrain to 25x25

# Create instances
cells = [std_cell.copy() for _ in range(6)]

# Create array container
array = Cell('array_2x3')

# Build 2x3 array (auto-adding instances)
# Row 0
array.constrain(cells[0], 'x1=10, y1=10')
array.constrain(cells[0], 'sx2+10=ox1, sy1=oy1', cells[1])
array.constrain(cells[1], 'sx2+10=ox1, sy1=oy1', cells[2])

# Row 1
array.constrain(cells[0], 'sx1=ox1, sy2+10=oy1', cells[3])
array.constrain(cells[1], 'sx1=ox1, sy2+10=oy1', cells[4])
array.constrain(cells[2], 'sx1=ox1, sy2+10=oy1', cells[5])

print(f"Created 2x3 array with {len(array.children)} cells (auto-added)")
print()

result = array.solver()

if result:
    print(f"✓ Array solved")
    print(f"  array bbox: {array.pos_list}")

    # Print grid
    print(f"\n  Grid positions:")
    for i in range(2):
        for j in range(3):
            idx = i * 3 + j
            print(f"    [{i},{j}]: {cells[idx].pos_list}")

    # Draw
    fig = array.draw(solve_first=False, show=False)
    import matplotlib.pyplot as plt
    plt.savefig('demo_outputs/self_constrain_array.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved to demo_outputs/self_constrain_array.png")
else:
    print("✗ Array solver failed")

print()

# ==============================================================================
# EXAMPLE 6: Practical Use Case - Standard Cell Row
# ==============================================================================

print("Example 6: Practical Use Case - Standard Cell Row")
print("-" * 70)
print()

# Define standard cell library with fixed heights
def create_std_cell(name, width):
    """Create a standard cell with fixed size"""
    cell = Cell(name, 'metal1')
    cell.constrain(f'x2-x1={width}, y2-y1=40')  # All cells 40 units tall
    return cell

# Create cells
inv1 = create_std_cell('INV_X1', 30)
nand2 = create_std_cell('NAND2_X1', 40)
inv2 = create_std_cell('INV_X2', 35)
buf1 = create_std_cell('BUF_X1', 40)

# Create row (auto-add all cells)
row = Cell('row')

# Align cells in row with 5 unit spacing (auto-add)
row.constrain(inv1, 'x1=0, y1=0')
row.constrain(inv1, 'sx2+5=ox1, sy1=oy1', nand2)
row.constrain(nand2, 'sx2+5=ox1, sy1=oy1', inv2)
row.constrain(inv2, 'sx2+5=ox1, sy1=oy1', buf1)

# Self-constrain row height (all cells align to same baseline)
row.constrain('y1=0, y2-y1=40')  # Fix row to 40 units tall

print("Standard cell row with 4 cells:")
print("  INV_X1 (30 wide), NAND2_X1 (40 wide)")
print("  INV_X2 (35 wide), BUF_X1 (40 wide)")
print("  All cells 40 units tall, 5 unit spacing")
print()

result = row.solver()

if result:
    print(f"✓ Row solved")
    print(f"  inv1: {inv1.pos_list}")
    print(f"  nand2: {nand2.pos_list}")
    print(f"  inv2: {inv2.pos_list}")
    print(f"  buf1: {buf1.pos_list}")
    print(f"  row: {row.pos_list}")

    total_width = row.pos_list[2] - row.pos_list[0]
    print(f"\n  Total row width: {total_width}")
    print(f"  (30 + 5 + 40 + 5 + 35 + 5 + 40 = 160)")

    # Draw
    fig = row.draw(solve_first=False, show=False)
    import matplotlib.pyplot as plt
    plt.savefig('demo_outputs/self_constrain_row.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved to demo_outputs/self_constrain_row.png")
else:
    print("✗ Row solver failed")

print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("✅ Self-Constraint Feature:")
print("  • Syntax: cell.constrain('x2-x1=100, y2-y1=50')")
print("  • Use cases:")
print("    - Fix cell size: 'x2-x1=width, y2-y1=height'")
print("    - Fix position: 'x1=0, y1=0'")
print("    - Minimum size: 'x2-x1>=100, y2-y1>=80'")
print("    - Set aspect ratio: 'x2-x1=2*(y2-y1)'")
print()
print("✅ Auto-Add Instance Feature:")
print("  • No explicit add_instance() calls needed")
print("  • Syntax: parent.constrain(child1, ..., child2)")
print("  • Instances automatically added when referenced")
print("  • Benefits:")
print("    - Less boilerplate code")
print("    - More intuitive API")
print("    - Faster development")
print()
print("🎯 Combined Benefits:")
print("  • Define standard cell sizes once")
print("  • Build layouts without manual instance management")
print("  • Create frames, rows, arrays easily")
print("  • Enforce design rules (minimum sizes, alignment)")
print()
print("Files generated:")
print("  • demo_outputs/self_constrain_transistor.png")
print("  • demo_outputs/self_constrain_array.png")
print("  • demo_outputs/self_constrain_row.png")
print()
print("=" * 70)
