#!/usr/bin/env python3
"""
Demonstrate constraint-based modification of NAND2 gate

This script:
1. Loads original constraints
2. Scales all polygons by 1.5x
3. Adds spacing between polygons
4. Saves modified constraints
"""

import yaml

print("="*70)
print("Modifying NAND2 Gate Constraints")
print("="*70)

# Load original constraints
print("\n1. Loading original constraints...")
with open('nand2_original_constraints.yaml', 'r') as f:
    data = yaml.safe_load(f)

print(f"   Original cell: {data['cell_name']}")
print(f"   Original dimensions: {data['dimensions']['width']:.3f} x {data['dimensions']['height']:.3f} um")
print(f"   Polygons: {len(data['polygons'])}")

# Modification parameters
scale_factor = 1.5
spacing_increase = 0.02  # Add 20nm spacing

print(f"\n2. Applying modifications...")
print(f"   - Scale factor: {scale_factor}x")
print(f"   - Additional spacing: {spacing_increase} um")

# Track original positions for spacing calculation
original_positions = []
for poly in data['polygons']:
    original_positions.append({
        'name': poly['name'],
        'x1': poly['position']['x1'],
        'y1': poly['position']['y1'],
        'x2': poly['position']['x2'],
        'y2': poly['position']['y2']
    })

# Modify each polygon
for i, poly in enumerate(data['polygons']):
    # Scale size
    new_width = poly['size']['width'] * scale_factor
    new_height = poly['size']['height'] * scale_factor

    # Calculate center point
    center_x = (poly['position']['x1'] + poly['position']['x2']) / 2
    center_y = (poly['position']['y1'] + poly['position']['y2']) / 2

    # Scale around center point
    poly['position']['x1'] = center_x - new_width / 2
    poly['position']['x2'] = center_x + new_width / 2
    poly['position']['y1'] = center_y - new_height / 2
    poly['position']['y2'] = center_y + new_height / 2

    # Update size
    poly['size']['width'] = new_width
    poly['size']['height'] = new_height

    # Add spacing to next polygon (shift subsequent polygons)
    if i < len(data['polygons']) - 1:
        shift = spacing_increase * (i + 1)
        poly['position']['x1'] += shift
        poly['position']['x2'] += shift
        poly['position']['y1'] += shift
        poly['position']['y2'] += shift

# Update cell dimensions
if data['polygons']:
    all_x2 = [p['position']['x2'] for p in data['polygons']]
    all_y2 = [p['position']['y2'] for p in data['polygons']]
    data['dimensions']['width'] = max(all_x2)
    data['dimensions']['height'] = max(all_y2)

# Update cell name
data['cell_name'] = 'NAND2_modified'

print(f"\n3. Modified dimensions:")
print(f"   New dimensions: {data['dimensions']['width']:.3f} x {data['dimensions']['height']:.3f} um")
print(f"   Size increase: {data['dimensions']['width']/0.16:.2f}x")

# Show polygon changes
print(f"\n4. Polygon modifications:")
for i, poly in enumerate(data['polygons']):
    orig = original_positions[i]
    print(f"   {poly['name']}:")
    print(f"      Size: {orig['x2']-orig['x1']:.4f} → {poly['size']['width']:.4f} um ({scale_factor}x)")
    print(f"      Position: ({orig['x1']:.4f}, {orig['y1']:.4f}) → ({poly['position']['x1']:.4f}, {poly['position']['y1']:.4f})")

# Save modified constraints
output_file = 'nand2_modified_constraints.yaml'
with open(output_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)

print(f"\n5. Saved modified constraints to: {output_file}")
print("\n" + "="*70)
print("Constraints modified successfully!")
print("="*70)
print("\nNext steps:")
print("  1. Regenerate GDS: python tools/gds_to_constraints.py --regenerate nand2_modified_constraints.yaml nand2_modified.gds")
print("  2. Run DRC verification")
print("  3. Run LVS verification")
