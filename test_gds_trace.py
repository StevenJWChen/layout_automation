#!/usr/bin/env python3
"""
Trace GDS export/import to find where rounding error occurs
"""

from layout_automation.cell import Cell
import gdstk
import os

print("="*70)
print("GDS Rounding Trace")
print("="*70)

# Create cell with fractional position
layout = Cell('layout')
cell = Cell('test_cell', 'metal1')
layout = Cell('layout', cell)

layout.pos_list = [0.0, 0.0, 100.0, 100.0]
cell.pos_list = [10.7, 20.3, 40.9, 35.6]

print("\nOriginal position:")
print(f"  cell.pos_list = {cell.pos_list}")
print(f"  x1={cell.pos_list[0]}, y1={cell.pos_list[1]}")
print(f"  x2={cell.pos_list[2]}, y2={cell.pos_list[3]}")
print(f"  width={cell.pos_list[2] - cell.pos_list[0]}")
print(f"  height={cell.pos_list[3] - cell.pos_list[1]}")

# Export manually to see what GDS gets
gds_file = 'trace_test.gds'

print("\n" + "="*70)
print("EXPORT PROCESS")
print("="*70)

lib = gdstk.Library(name="LAYOUT", unit=1e-6, precision=1e-9)
gds_cell_parent = lib.new_cell('layout')
gds_cell_leaf = lib.new_cell('test_cell')

# What the export code does (from lines 1805-1809):
x1, y1, x2, y2 = cell.pos_list
width = x2 - x1
height = y2 - y1

print(f"\nCalculated dimensions:")
print(f"  width = {x2} - {x1} = {width}")
print(f"  height = {y2} - {y1} = {height}")

# Create rectangle at origin
rect = gdstk.rectangle((0, 0), (width, height), layer=30, datatype=0)
gds_cell_leaf.add(rect)

# Add reference at (x1, y1)
print(f"\nReference origin: ({x1}, {y1})")
ref = gdstk.Reference(gds_cell_leaf, origin=(x1, y1))
gds_cell_parent.add(ref)

# Write and read back
lib.write_gds(gds_file)

print("\n" + "="*70)
print("IMPORT PROCESS")
print("="*70)

# Read GDS
lib_read = gdstk.read_gds(gds_file)

# Find cells
gds_parent_read = None
gds_leaf_read = None
for c in lib_read.cells:
    if c.name == 'layout':
        gds_parent_read = c
    elif c.name == 'test_cell':
        gds_leaf_read = c

print(f"\nGDS leaf cell '{gds_leaf_read.name}':")
print(f"  Polygons: {len(gds_leaf_read.polygons)}")

if gds_leaf_read.polygons:
    poly = gds_leaf_read.polygons[0]
    print(f"  Polygon layer: {poly.layer}")
    print(f"  Polygon points:")
    for i, point in enumerate(poly.points):
        print(f"    [{i}]: {point}")

    bbox = poly.bounding_box()
    print(f"  Bounding box: {bbox}")
    print(f"    Lower-left: {bbox[0]}")
    print(f"    Upper-right: {bbox[1]}")

    gds_x1, gds_y1 = bbox[0]
    gds_x2, gds_y2 = bbox[1]

    print(f"\nDirect bbox values:")
    print(f"  x1 = {gds_x1} (type: {type(gds_x1)})")
    print(f"  y1 = {gds_y1} (type: {type(gds_y1)})")
    print(f"  x2 = {gds_x2} (type: {type(gds_x2)})")
    print(f"  y2 = {gds_y2} (type: {type(gds_y2)})")

    # What the import code does (line 1955):
    rounded_width = int(round(gds_x2 - gds_x1))
    rounded_height = int(round(gds_y2 - gds_y1))

    print(f"\nRounding for leaf cell pos_list [0, 0, width, height]:")
    print(f"  width = {gds_x2} - {gds_x1} = {gds_x2 - gds_x1}")
    print(f"  int(round({gds_x2 - gds_x1})) = {rounded_width}")
    print(f"  height = {gds_y2} - {gds_y1} = {gds_y2 - gds_y1}")
    print(f"  int(round({gds_y2 - gds_y1})) = {rounded_height}")

    print(f"\nResulting pos_list for leaf: [0, 0, {rounded_width}, {rounded_height}]")

print(f"\nGDS parent cell references:")
for ref in gds_parent_read.references:
    print(f"  Reference to '{ref.cell.name}':")
    print(f"    Origin: {ref.origin}")
    ref_x, ref_y = ref.origin
    print(f"    x_offset = {ref_x} (type: {type(ref_x)})")
    print(f"    y_offset = {ref_y} (type: {type(ref_y)})")

    # What _apply_offset_recursive does (lines 2029-2033):
    print(f"\n  Applying offset to leaf pos_list [0, 0, {rounded_width}, {rounded_height}]:")
    final_x1 = int(round(0 + ref_x))
    final_y1 = int(round(0 + ref_y))
    final_x2 = int(round(rounded_width + ref_x))
    final_y2 = int(round(rounded_height + ref_y))

    print(f"    x1 = int(round(0 + {ref_x})) = {final_x1}")
    print(f"    y1 = int(round(0 + {ref_y})) = {final_y1}")
    print(f"    x2 = int(round({rounded_width} + {ref_x})) = {final_x2}")
    print(f"    y2 = int(round({rounded_height} + {ref_y})) = {final_y2}")

    print(f"\n  Final imported pos_list: [{final_x1}, {final_y1}, {final_x2}, {final_y2}]")

print(f"\nComparison:")
print(f"  Original: {cell.pos_list}")
print(f"  Imported: [{final_x1}, {final_y1}, {final_x2}, {final_y2}]")
print(f"  Delta: [{final_x1 - cell.pos_list[0]}, {final_y1 - cell.pos_list[1]}, {final_x2 - cell.pos_list[2]}, {final_y2 - cell.pos_list[3]}]")

# Cleanup
os.remove(gds_file)

print("\n" + "="*70)
print("ANALYSIS")
print("="*70)

print("\nThe issue is in the export process:")
print("  1. Export calculates width and height from fractional coordinates")
print("  2. GDS stores these as floating point in the file")
print("  3. Import reads them back (still floating point)")
print("  4. Import rounds width/height separately, then adds offset")
print("\nThe problem: width and height are rounded BEFORE adding the offset!")
print("  This causes the final position to be wrong.")
print("\nExample:")
print(f"  Original: x1=10.7, x2=40.9 -> width=30.2")
print(f"  Export stores rectangle (0,0) to (30.2, 15.3)")
print(f"  Import reads (0,0) to (30.2, 15.3)")
print(f"  Import rounds to [0, 0, 30, 15]")
print(f"  Import adds offset: [10.7, 20.3, 30+10.7=40.7, 15+20.3=35.3]")
print(f"  Import rounds again: [11, 20, 41, 35]")
print(f"  Expected: [11, 20, 41, 36]")
print(f"\nThe error: 35.6 should round to 36, but we get 35 because:")
print(f"  - Height 15.3 rounds to 15")
print(f"  - 15 + 20.3 = 35.3 rounds to 35")
print(f"  - Should be: 35.6 rounds directly to 36")
