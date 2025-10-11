#!/usr/bin/env python3
"""Debug the extraction to see why it's over-counting"""

from tests.test_cases import create_inverter_schematic
from layout_automation.layout_from_schematic import LayoutGenerator
from layout_automation.technology import Technology
from tools.netlist_extractor import NetlistExtractor
from layout_automation.units import to_um

# Generate layout
tech = Technology('sky130')
schematic = create_inverter_schematic()
generator = LayoutGenerator(schematic, tech)
layout_cell = generator.generate()

# Try extraction with debug output
print("="*70)
print("DEBUG: Extracting with detailed output")
print("="*70)

extractor = NetlistExtractor(layout_cell, tech)

# Flatten
extractor._flatten_layout()

# Get shapes
diff_shapes = extractor.shapes.get('diff', [])
poly_shapes = extractor.shapes.get('poly', [])
contact_shapes = extractor.shapes.get('licon1', [])

print(f"\nFound {len(diff_shapes)} diff shapes:")
for i, d in enumerate(diff_shapes):
    print(f"  {i}: {d.name} at ({to_um(d.x1):.3f}, {to_um(d.y1):.3f}) to ({to_um(d.x2):.3f}, {to_um(d.y2):.3f})")
    print(f"      Size: {to_um(d.width()):.3f} × {to_um(d.height()):.3f} μm")

print(f"\nFound {len(poly_shapes)} poly shapes:")
for i, p in enumerate(poly_shapes):
    print(f"  {i}: {p.name} at ({to_um(p.x1):.3f}, {to_um(p.y1):.3f}) to ({to_um(p.x2):.3f}, {to_um(p.y2):.3f})")
    print(f"      Size: {to_um(p.width()):.3f} × {to_um(p.height()):.3f} μm")

print(f"\nFound {len(contact_shapes)} contact shapes:")
for i, c in enumerate(contact_shapes):
    print(f"  {i}: {c.name} at ({to_um(c.x1):.3f}, {to_um(c.y1):.3f}) to ({to_um(c.x2):.3f}, {to_um(c.y2):.3f})")
    print(f"      Center: ({to_um((c.x1+c.x2)/2):.3f}, {to_um((c.y1+c.y2)/2):.3f})")

# Check overlaps
print(f"\nChecking diff-poly overlaps:")
overlap_count = 0
for diff in diff_shapes:
    for poly in poly_shapes:
        if diff.overlaps(poly):
            overlap_count += 1
            overlap_x = (max(diff.x1, poly.x1) + min(diff.x2, poly.x2)) / 2
            overlap_y = (max(diff.y1, poly.y1) + min(diff.y2, poly.y2)) / 2
            print(f"  Overlap {overlap_count}: {diff.name} × {poly.name}")
            print(f"    Center: ({to_um(overlap_x):.3f}, {to_um(overlap_y):.3f})")

            # Check distance to nearest contact
            min_dist = float('inf')
            nearest_contact = None
            for contact in contact_shapes:
                contact_x = (contact.x1 + contact.x2) / 2
                contact_y = (contact.y1 + contact.y2) / 2
                dist_x = abs(overlap_x - contact_x)
                dist_y = abs(overlap_y - contact_y)
                dist = (dist_x**2 + dist_y**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_contact = contact.name

            print(f"    Nearest contact: {nearest_contact} at distance {to_um(min_dist):.3f}μm ({min_dist:.0f}nm)")
            print(f"    Is gate? {min_dist >= 100}")

print(f"\nTotal overlaps found: {overlap_count}")
print(f"Expected transistors: 2")
