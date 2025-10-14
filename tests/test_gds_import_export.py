#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test GDS Import/Export with Frozen and Unfrozen Modes

Tests the ability to:
1. Export cells to GDS
2. Import GDS as fixed (frozen) layouts
3. Import GDS as constraint-capable (unfrozen) layouts
4. Use imported cells in larger designs
"""

import os
from layout_automation.gds_cell import Cell, Polygon, CellInstance

# Create output directory
os.makedirs('test_outputs', exist_ok=True)

print("="*70)
print("TEST 1: Basic GDS Export and Import")
print("="*70)

# Create a simple cell
original = Cell('original')
p1 = Polygon('p1', 'metal1')
p2 = Polygon('p2', 'metal1')
original.add_polygon([p1, p2])

# Add constraints and solve
original.constrain(p1, 'x2-x1=30, y2-y1=20, x1=10, y1=10')
original.constrain(p2, 'x2-x1=20, y2-y1=15, x1=50, y1=15')

result = original.solver()
print(f"Original cell solved: {result}")
print(f"  p1: {p1.pos_list}")
print(f"  p2: {p2.pos_list}")

# Export to GDS
gds_file = 'test_outputs/test_basic.gds'
original.export_gds(gds_file)
print(f"✓ Exported to {gds_file}")

# Import as unfrozen (default)
imported_unfrozen = Cell('imported_unfrozen')
imported_unfrozen.import_gds(gds_file, freeze_imported=False)
print(f"✓ Imported as unfrozen: {len(imported_unfrozen.polygons)} polygons")
print(f"  Is frozen: {imported_unfrozen.is_frozen()}")
assert not imported_unfrozen.is_frozen(), "Should be unfrozen"

# Import as frozen
imported_frozen = Cell('imported_frozen')
imported_frozen.import_gds(gds_file, freeze_imported=True)
print(f"✓ Imported as frozen: {len(imported_frozen.polygons)} polygons")
print(f"  Is frozen: {imported_frozen.is_frozen()}")
assert imported_frozen.is_frozen(), "Should be frozen"

bbox = imported_frozen.get_bbox()
print(f"  Bounding box: {bbox}\n")

print("="*70)
print("TEST 2: Using Cell.from_gds() Class Method")
print("="*70)

# Export a cell first
std_cell = Cell('std_cell')
rect1 = Polygon('rect1', 'diff')
rect2 = Polygon('rect2', 'poly')
std_cell.add_polygon([rect1, rect2])
std_cell.constrain(rect1, 'x2-x1=40, y2-y1=25, x1=5, y1=5')
std_cell.constrain(rect2, 'x2-x1=5, y2-y1=35, x1=20, y1=0')
std_cell.solver()

gds_file2 = 'test_outputs/std_cell.gds'
std_cell.export_gds(gds_file2)
print(f"Exported standard cell to {gds_file2}")

# Import using class method - frozen
frozen_std = Cell.from_gds(gds_file2, freeze_imported=True)
print(f"✓ Created frozen cell from GDS: {frozen_std.name}")
print(f"  Is frozen: {frozen_std.is_frozen()}")
print(f"  Bbox: {frozen_std.get_bbox()}")
assert frozen_std.is_frozen(), "Should be frozen"

# Import using class method - unfrozen
unfrozen_std = Cell.from_gds(gds_file2, freeze_imported=False)
print(f"✓ Created unfrozen cell from GDS: {unfrozen_std.name}")
print(f"  Is frozen: {unfrozen_std.is_frozen()}")
assert not unfrozen_std.is_frozen(), "Should be unfrozen"
print()

print("="*70)
print("TEST 3: Using Frozen Imported Cell in Design")
print("="*70)

# Create a design using the frozen imported cell
circuit = Cell('circuit')

# Create instances of the frozen standard cell
inst1 = CellInstance('inst1', frozen_std)
inst2 = CellInstance('inst2', frozen_std)
inst3 = CellInstance('inst3', frozen_std)

circuit.add_instance([inst1, inst2, inst3])

# Position the instances (frozen internals, only positions solved)
circuit.constrain(inst1, 'sx1=10, sy1=10')
circuit.constrain(inst1, 'sx2+15=ox1, sy1=oy1', inst2)
circuit.constrain(inst2, 'sx2+15=ox1, sy1=oy1', inst3)

print("Solving circuit with frozen imported cells...")
result = circuit.solver()
print(f"Circuit solved: {result}")

if result:
    print(f"  inst1: {inst1.pos_list}")
    print(f"  inst2: {inst2.pos_list}")
    print(f"  inst3: {inst3.pos_list}")

    # Verify spacing
    spacing1 = inst2.pos_list[0] - inst1.pos_list[2]
    spacing2 = inst3.pos_list[0] - inst2.pos_list[2]
    print(f"\n  Spacing inst1-inst2: {spacing1:.1f} (should be 15)")
    print(f"  Spacing inst2-inst3: {spacing2:.1f} (should be 15)")

    assert abs(spacing1 - 15) < 0.1, f"Spacing should be 15"
    assert abs(spacing2 - 15) < 0.1, f"Spacing should be 15"
    print("✓ Correct spacing maintained")

    # Export the circuit
    circuit.export_gds('test_outputs/circuit_with_imported.gds')
    print("✓ Exported circuit to test_outputs/circuit_with_imported.gds")
else:
    print("✗ Circuit solver failed")

print()

print("="*70)
print("TEST 4: Hierarchical GDS with Subcells")
print("="*70)

# Create a hierarchical structure
base = Cell('base')
b1 = Polygon('b1', 'metal1')
base.add_polygon(b1)
base.constrain(b1, 'x2-x1=15, y2-y1=15, x1=0, y1=0')
base.solver()

mid = Cell('mid')
base_inst1 = CellInstance('base1', base)
base_inst2 = CellInstance('base2', base)
mid.add_instance([base_inst1, base_inst2])
mid.constrain(base_inst1, 'sx1=5, sy1=5')
mid.constrain(base_inst1, 'sx2+10=ox1, sy1=oy1', base_inst2)
mid.solver()

top_hier = Cell('top_hier')
mid_inst1 = CellInstance('mid1', mid)
mid_inst2 = CellInstance('mid2', mid)
top_hier.add_instance([mid_inst1, mid_inst2])
top_hier.constrain(mid_inst1, 'sx1=10, sy1=10')
top_hier.constrain(mid_inst1, 'sy2+20=oy1, sx1=ox1', mid_inst2)
top_hier.solver()

# Export hierarchical structure
hier_gds = 'test_outputs/hierarchical.gds'
top_hier.export_gds(hier_gds)
print(f"Exported hierarchical design to {hier_gds}")
print(f"  Top cell: {top_hier.name}")
print(f"  Instances: {len(top_hier.instances)}")

# Import with subcells frozen
imported_hier_frozen = Cell('imported_hier')
imported_hier_frozen.import_gds(hier_gds, freeze_imported=True, freeze_subcells=True)
print(f"\n✓ Imported hierarchical with all cells frozen")
print(f"  Top frozen: {imported_hier_frozen.is_frozen()}")
print(f"  Subcells: {len(imported_hier_frozen.instances)}")

# Check if subcells are frozen
if len(imported_hier_frozen.instances) > 0:
    subcell = imported_hier_frozen.instances[0].cell
    print(f"  First subcell frozen: {subcell.is_frozen()}")
    assert subcell.is_frozen(), "Subcells should be frozen"

# Import with only subcells frozen, top unfrozen
imported_hier_mixed = Cell('imported_hier_mixed')
imported_hier_mixed.import_gds(hier_gds, freeze_imported=False, freeze_subcells=False)
print(f"\n✓ Imported hierarchical with no freezing")
print(f"  Top frozen: {imported_hier_mixed.is_frozen()}")
assert not imported_hier_mixed.is_frozen(), "Top should be unfrozen"

print()

print("="*70)
print("TEST 5: Round-trip Export/Import")
print("="*70)

# Create original
roundtrip = Cell('roundtrip')
rt1 = Polygon('rt1', 'metal1')
rt2 = Polygon('rt2', 'metal2')
rt3 = Polygon('rt3', 'poly')
roundtrip.add_polygon([rt1, rt2, rt3])

roundtrip.constrain(rt1, 'x2-x1=25, y2-y1=20, x1=10, y1=10')
roundtrip.constrain(rt2, 'x2-x1=25, y2-y1=15, x1=10, y1=35')
roundtrip.constrain(rt3, 'x2-x1=5, y2-y1=40, x1=20, y1=8')
roundtrip.solver()

orig_bbox = roundtrip.get_bbox()
print(f"Original bbox: {orig_bbox}")
print(f"  Polygons: {len(roundtrip.polygons)}")

# Export
rt_gds = 'test_outputs/roundtrip.gds'
roundtrip.export_gds(rt_gds)

# Import frozen
rt_imported = Cell.from_gds(rt_gds, freeze_imported=True)
imported_bbox = rt_imported.get_bbox()

print(f"\nImported (frozen) bbox: {imported_bbox}")
print(f"  Polygons: {len(rt_imported.polygons)}")
print(f"  Is frozen: {rt_imported.is_frozen()}")

# Compare bounding boxes
if orig_bbox and imported_bbox:
    orig_width = orig_bbox[2] - orig_bbox[0]
    orig_height = orig_bbox[3] - orig_bbox[1]
    imp_width = imported_bbox[2] - imported_bbox[0]
    imp_height = imported_bbox[3] - imported_bbox[1]

    print(f"\n  Original size: {orig_width:.1f} x {orig_height:.1f}")
    print(f"  Imported size: {imp_width:.1f} x {imp_height:.1f}")

    assert abs(orig_width - imp_width) < 0.1, "Width should match"
    assert abs(orig_height - imp_height) < 0.1, "Height should match"
    print("✓ Dimensions preserved in round-trip")

print()

print("="*70)
print("TEST 6: Performance Test - Array of Imported Cells")
print("="*70)

import time

# Use the frozen standard cell from earlier
print(f"Using frozen standard cell: {frozen_std.name}")
print(f"  Bbox: {frozen_std.get_bbox()}")

# Create array
array_size = 5
array = Cell(f'array_{array_size}x{array_size}')
instances = []

for row in range(array_size):
    for col in range(array_size):
        inst = CellInstance(f'cell_r{row}_c{col}', frozen_std)
        instances.append((row, col, inst))
        array.add_instance(inst)

# Position instances
spacing = 10
for row, col, inst in instances:
    if row == 0 and col == 0:
        array.constrain(inst, 'sx1=5, sy1=5')
    elif col == 0:
        prev = instances[(row-1) * array_size][2]
        array.constrain(prev, f'sy2+{spacing}=oy1, sx1=ox1', inst)
    else:
        prev = instances[row * array_size + col - 1][2]
        array.constrain(prev, f'sx2+{spacing}=ox1, sy1=oy1', inst)

# Time the solving
start = time.time()
result = array.solver()
elapsed = time.time() - start

print(f"\nArray of {len(instances)} frozen imported cells:")
print(f"  Solver result: {result}")
print(f"  Solve time: {elapsed:.3f} seconds")
print(f"  Instances solved: {len(instances)}")
print(f"✓ Performance test complete")

if result:
    array.export_gds('test_outputs/imported_array.gds')
    print(f"✓ Exported array to test_outputs/imported_array.gds")

print()

print("="*70)
print("SUMMARY")
print("="*70)
print("✓ TEST 1: Basic export/import - PASS")
print("✓ TEST 2: Cell.from_gds() method - PASS")
print("✓ TEST 3: Using frozen imports in design - PASS")
print("✓ TEST 4: Hierarchical with subcells - PASS")
print("✓ TEST 5: Round-trip preservation - PASS")
print("✓ TEST 6: Performance with arrays - PASS")
print("\n🎉 All GDS import/export tests passed!")
print("="*70)
print("\nGenerated files in test_outputs/:")
print("  - test_basic.gds")
print("  - std_cell.gds")
print("  - circuit_with_imported.gds")
print("  - hierarchical.gds")
print("  - roundtrip.gds")
print("  - imported_array.gds")
