"""
Test to show the actual structure of imported cells
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_automation.cell import Cell
from layout_automation.tech_file import load_tech_file
from layout_automation.style_config import reset_style_config

# Load tech file
tech = load_tech_file('examples/freepdk45_sample.tf')
reset_style_config()
tech.apply_colors_to_style()

# Create layout
layout = Cell('test_chip')
poly1 = Cell('my_nwell', 'nwell')
poly2 = Cell('my_active', 'active')

layout.add_instance([poly1, poly2])
layout.constrain(poly1, 'x1=0, y1=0, x2=50, y2=40')
layout.constrain(poly2, 'x1=5, y1=10, x2=20, y2=30')
layout.solver()

print("ORIGINAL STRUCTURE:")
print("="*80)
def print_structure(cell, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{cell.name} (is_leaf={cell.is_leaf}, layer={cell.layer_name})")
    for child in cell.children:
        print_structure(child, indent + 1)

print_structure(layout)

# Export and import
os.makedirs('demo_outputs', exist_ok=True)
gds_file = 'demo_outputs/test_structure.gds'
layout.export_gds(gds_file, use_tech_file=True)

imported = Cell.from_gds(gds_file, use_tech_file=True)

print("\nIMPORTED STRUCTURE:")
print("="*80)
print_structure(imported)

print("\n" + "="*80)
print("COMPARISON:")
print("="*80)
print("\nOriginal 'my_nwell':")
print(f"  is_leaf: {poly1.is_leaf}")
print(f"  layer: {poly1.layer_name}")
print(f"  children: {len(poly1.children)}")

imported_nwell = imported.children[0]
print("\nImported 'my_nwell':")
print(f"  name: {imported_nwell.name}")
print(f"  is_leaf: {imported_nwell.is_leaf}")
print(f"  layer: {imported_nwell.layer_name}")
print(f"  children: {len(imported_nwell.children)}")
if imported_nwell.children:
    print(f"  child[0]: {imported_nwell.children[0].name} (layer={imported_nwell.children[0].layer_name})")
