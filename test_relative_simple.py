#!/usr/bin/env python3
"""
Simple and clear test for relative positioning between cells.
Based on working patterns from test_roundtrip_final.py
"""

import os
from layout_automation.cell import Cell
from layout_automation.style_config import StyleConfig
import matplotlib.pyplot as plt

print("="*70)
print("RELATIVE POSITIONING TESTS - Simple Version")
print("="*70)

os.makedirs('demo_outputs', exist_ok=True)

# Configure style
style = StyleConfig()
style.set_layer_style('metal1', color='#FF6B6B', alpha=0.7)
style.set_layer_style('metal2', color='#4A90E2', alpha=0.7)
style.set_layer_style('poly', color='#90EE90', alpha=0.7)

# ============================================================================
# TEST 1: Basic relative positioning between sibling cells
# ============================================================================
print("\n" + "="*70)
print("TEST 1: Basic Relative Positioning (Siblings)")
print("="*70)

cell1 = Cell('cell1', 'metal1')
cell2 = Cell('cell2', 'metal2')
cell3 = Cell('cell3', 'poly')

parent = Cell('parent')
parent.add_instance([cell1, cell2, cell3])

# cell1: anchor with absolute position
parent.constrain(cell1, 'x1=0, y1=0, x2=10, y2=10')

# cell2: to the right of cell1 (relative positioning)
parent.constrain(cell2, 'x1=20, y1=0, x2=30, y2=10')

# cell3: above cell1 (relative positioning)
parent.constrain(cell3, 'x1=0, y1=15, x2=10, y2=25')

status = parent.solver()
print(f"Solver status: {'OPTIMAL' if status else 'FAILED'}")

if status:
    print("\nPositions:")
    print(f"  cell1: {cell1.pos_list}")
    print(f"  cell2: {cell2.pos_list}")
    print(f"  cell3: {cell3.pos_list}")

    parent.draw(show=False, solve_first=False)
    plt.savefig('demo_outputs/test_rel_siblings.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n✓ Test 1 PASSED - Saved to test_rel_siblings.png")
else:
    print("\n✗ Test 1 FAILED")

# ============================================================================
# TEST 2: Relative positioning using sx1=ox2+gap pattern
# ============================================================================
print("\n" + "="*70)
print("TEST 2: Using sx1=ox2+gap Pattern")
print("="*70)

r1 = Cell('r1', 'metal1')
r2 = Cell('r2', 'metal2')
r3 = Cell('r3', 'poly')

parent2 = Cell('parent2')
parent2.add_instance([r1, r2, r3])

# r1: anchor
parent2.constrain(r1, 'x1=0, y1=0, x2=10, y2=10')

# r2: 5 units to the right of r1 using relative constraint
parent2.constrain(r2, 'sx1=ox2+5, sy1=oy1, swidth=10, sheight=10', r1)

# r3: 3 units above r1, left-aligned
parent2.constrain(r3, 'sx1=ox1, sy1=oy2+3, swidth=10, sheight=10', r1)

status2 = parent2.solver()
print(f"Solver status: {'OPTIMAL' if status2 else 'FAILED'}")

if status2:
    print("\nPositions:")
    print(f"  r1: {r1.pos_list}")
    print(f"  r2: {r2.pos_list} (should start at x={r1.x2+5})")
    print(f"  r3: {r3.pos_list} (should start at y={r1.y2+3})")

    # Verify
    assert r2.x1 == r1.x2 + 5, f"r2.x1 should be {r1.x2+5}, got {r2.x1}"
    assert r2.y1 == r1.y1, f"r2.y1 should be {r1.y1}, got {r2.y1}"
    assert r3.y1 == r1.y2 + 3, f"r3.y1 should be {r1.y2+3}, got {r3.y1}"
    assert r3.x1 == r1.x1, f"r3.x1 should be {r1.x1}, got {r3.x1}"

    parent2.draw(show=False, solve_first=False)
    plt.savefig('demo_outputs/test_rel_sx_ox.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n✓ Test 2 PASSED - All relative constraints verified!")
else:
    print("\n✗ Test 2 FAILED")

# ============================================================================
# TEST 3: Nested cells (cells of cells) with relative positioning
# ============================================================================
print("\n" + "="*70)
print("TEST 3: Nested Cells with Relative Positioning")
print("="*70)

# Bottom level shapes
s1 = Cell('s1', 'metal1')
s2 = Cell('s2', 'metal2')

# Middle level container
container = Cell('container')
container.add_instance([s1, s2])
container.constrain(s1, 'x1=0, y1=0, x2=8, y2=8')
container.constrain(s2, 'sx1=ox2+2, sy1=oy1, swidth=8, sheight=8', s1)

# Another shape for top level
s3 = Cell('s3', 'poly')

# Top level
top = Cell('top')
top.add_instance([container, s3])

# Position container at origin
top.constrain(container, 'sx1=0, sy1=0')

# Position s3 to the right of container
top.constrain(s3, 'sx1=ox2+5, sy1=oy1, swidth=10, sheight=8', container)

status3 = top.solver()
print(f"Solver status: {'OPTIMAL' if status3 else 'FAILED'}")

if status3:
    print("\nHierarchy:")
    print(f"  top: {top.pos_list}")
    print(f"    container: {container.pos_list}")
    print(f"      s1: {s1.pos_list}")
    print(f"      s2: {s2.pos_list}")
    print(f"    s3: {s3.pos_list} (should start at x={container.x2+5})")

    # Verify nested positioning
    assert s2.x1 == s1.x2 + 2, "s2 should be 2 units right of s1"
    assert s3.x1 == container.x2 + 5, "s3 should be 5 units right of container"

    top.draw(show=False, solve_first=False)
    plt.savefig('demo_outputs/test_rel_nested.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n✓ Test 3 PASSED - Nested relative positioning verified!")
else:
    print("\n✗ Test 3 FAILED")

# ============================================================================
# TEST 4: GDS round-trip preserves relative positioning
# ============================================================================
print("\n" + "="*70)
print("TEST 4: GDS Round-trip")
print("="*70)

# Create layout
b1 = Cell('b1', 'metal1')
b2 = Cell('b2', 'metal2')

sub = Cell('sub')
sub.add_instance([b1, b2])
sub.constrain(b1, 'x1=0, y1=0, x2=10, y2=10')
sub.constrain(b2, 'sx1=ox2+3, sy1=oy1, swidth=10, sheight=10', b1)

b3 = Cell('b3', 'poly')

main = Cell('main')
main.add_instance([sub, b3])
main.constrain(sub, 'sx1=0, sy1=0')
main.constrain(b3, 'sx1=ox2+5, sy1=oy1, swidth=10, sheight=10', sub)

status4 = main.solver()
print(f"Original solver status: {'OPTIMAL' if status4 else 'FAILED'}")

if status4:
    orig_positions = {
        'main': main.pos_list[:],
        'sub': sub.pos_list[:],
        'b1': b1.pos_list[:],
        'b2': b2.pos_list[:],
        'b3': b3.pos_list[:]
    }

    print("\nOriginal positions:")
    for name, pos in orig_positions.items():
        print(f"  {name}: {pos}")

    # Export
    gds_file = 'demo_outputs/test_rel_roundtrip.gds'
    main.export_gds(gds_file, use_tech_file=False)
    print(f"\n✓ Exported to {gds_file}")

    # Import
    imported = Cell.from_gds(gds_file, use_tech_file=False)
    imported.solver()
    print("✓ Imported from GDS")

    # Find cells and verify positions
    def find_cell(root, target_name):
        if target_name in root.name:
            return root
        for child in root.children:
            result = find_cell(child, target_name)
            if result:
                return result
        return None

    print("\nImported positions:")
    all_match = True
    for name in orig_positions.keys():
        cell = find_cell(imported, name)
        if cell:
            print(f"  {name}: {cell.pos_list}")
            for i in range(4):
                if abs(cell.pos_list[i] - orig_positions[name][i]) > 0.01:
                    print(f"    ✗ Mismatch at index {i}")
                    all_match = False
        else:
            print(f"  ✗ Cell {name} not found!")
            all_match = False

    if all_match:
        print("\n✓ Test 4 PASSED - All positions preserved!")
    else:
        print("\n✗ Test 4 FAILED - Position mismatch")

print("\n" + "="*70)
print("ALL TESTS COMPLETED")
print("="*70)
print("\nGenerated files in demo_outputs/:")
print("  - test_rel_siblings.png")
print("  - test_rel_sx_ox.png")
print("  - test_rel_nested.png")
print("  - test_rel_roundtrip.gds")
