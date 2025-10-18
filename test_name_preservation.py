"""
Test to verify polygon cell names are preserved through GDS export/import
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_automation.cell import Cell
from layout_automation.tech_file import load_tech_file
from layout_automation.style_config import reset_style_config

print("="*80)
print("POLYGON CELL NAME PRESERVATION TEST")
print("="*80)

# Load tech file
tech = load_tech_file('examples/freepdk45_sample.tf')
reset_style_config()
tech.apply_colors_to_style()

# Create layout with named polygons
print("\n[1] Creating layout with named polygons...")
layout = Cell('test_chip')

# Create polygons with specific names
poly1 = Cell('my_nwell', 'nwell')
poly2 = Cell('my_active', 'active')
poly3 = Cell('my_poly_gate', 'poly')
poly4 = Cell('my_metal_wire', 'metal1')

layout.add_instance([poly1, poly2, poly3, poly4])
layout.constrain(poly1, 'x1=0, y1=0, x2=50, y2=40')
layout.constrain(poly2, 'x1=5, y1=10, x2=20, y2=30')
layout.constrain(poly3, 'x1=25, y1=5, x2=30, y2=35')
layout.constrain(poly4, 'x1=10, y1=15, x2=40, y2=25')
layout.solver()

print(f"Original cell: {layout.name}")
print(f"Original children:")
for child in layout.children:
    print(f"  - {child.name} (layer: {child.layer_name})")

# Export
print("\n[2] Exporting to GDS...")
os.makedirs('demo_outputs', exist_ok=True)
gds_file = 'demo_outputs/test_polygon_names.gds'
layout.export_gds(gds_file, use_tech_file=True)
print(f"✓ Exported to {gds_file}")

# Check GDS structure
import gdstk
lib = gdstk.read_gds(gds_file)
print(f"\nGDS cells in file:")
for cell in lib.cells:
    print(f"  - {cell.name}")

# Import
print("\n[3] Importing from GDS...")
imported = Cell.from_gds(gds_file, use_tech_file=True)

print(f"Imported cell: {imported.name}")
print(f"Imported children:")
for child in imported.children:
    print(f"  - {child.name} (layer: {child.layer_name})")

# Verify
print("\n[4] Verification...")
print("="*80)
original_names = {child.name for child in layout.children}
imported_names = {child.name for child in imported.children}

if original_names == imported_names:
    print("✓ SUCCESS! All polygon cell names preserved exactly!")
    print(f"\nPreserved names: {sorted(original_names)}")
else:
    print("✗ MISMATCH in cell names")
    print(f"Original: {sorted(original_names)}")
    print(f"Imported: {sorted(imported_names)}")
    missing = original_names - imported_names
    extra = imported_names - original_names
    if missing:
        print(f"Missing: {missing}")
    if extra:
        print(f"Extra: {extra}")

print("="*80)
