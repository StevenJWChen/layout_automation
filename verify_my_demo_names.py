"""
Verify that my_demo.py preserves all polygon cell names
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_automation.cell import Cell
from layout_automation.tech_file import load_tech_file
from layout_automation.style_config import reset_style_config

tech = load_tech_file('examples/freepdk45_sample.tf')
reset_style_config()
tech.apply_colors_to_style()

# Create the same layout as my_demo.py
layout = Cell('demo_chip')

r1 = Cell('rect1', 'nwell')
r2 = Cell('rect2', 'active')
r3 = Cell('rect3', 'poly')
r4 = Cell('rect4', 'metal1')
r5 = Cell('rect5', 'metal2')
r6 = Cell('rect6', 'contact')
r7 = Cell('rect7', 'metal1')
gg = Cell('gg')
gg.add_instance(r7)

layout.add_instance([r1, r2, r3, r4, r5, r6, gg])

layout.constrain(r1, 'x1=0, y1=0, x2=50, y2=40')
layout.constrain(r2, 'x1=5, y1=10, x2=20, y2=30')
layout.constrain(r3, 'x1=25, y1=5, x2=30, y2=35')
layout.constrain(r4, 'x1=10, y1=15, x2=40, y2=25')
layout.constrain(r5, 'x1=35, y1=10, x2=45, y2=30')
layout.constrain(r6, 'x1=15, y1=18, x2=18, y2=22')
layout.constrain(gg, 'sx2=ox1', r6)
layout.solver()

# Export
gds_file = 'demo_outputs/verify_names.gds'
layout.export_gds(gds_file, use_tech_file=True)

# Import
imported = Cell.from_gds(gds_file, use_tech_file=True)

# Collect names
def get_names(cell, names=None):
    if names is None:
        names = []
    names.append(cell.name)
    for child in cell.children:
        get_names(child, names)
    return names

original_names = set(get_names(layout))
imported_names = set(get_names(imported))

print("="*80)
print("POLYGON CELL NAME PRESERVATION IN my_demo.py")
print("="*80)
print(f"\nOriginal cell names: {sorted(original_names)}")
print(f"\nImported cell names: {sorted(imported_names)}")

if original_names == imported_names:
    print("\n✓ SUCCESS! All cell names preserved exactly!")
else:
    print("\n✗ MISMATCH!")
    missing = original_names - imported_names
    extra = imported_names - original_names
    if missing:
        print(f"  Missing: {missing}")
    if extra:
        print(f"  Extra: {extra}")

print("="*80)
