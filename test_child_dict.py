"""
Test that child_dict is properly updated during GDS import
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
chip = Cell('test_chip')
r1 = Cell('rect1', 'nwell')
r2 = Cell('rect2', 'active')
r3 = Cell('rect3', 'poly')

chip.add_instance([r1, r2, r3])
chip.constrain(r1, 'x1=0, y1=0, x2=50, y2=40')
chip.constrain(r2, 'x1=5, y1=10, x2=20, y2=30')
chip.constrain(r3, 'x1=25, y1=5, x2=30, y2=35')
chip.solver()

print("="*80)
print("CHILD_DICT TEST")
print("="*80)

# Check original child_dict
print("\n[Original]")
print(f"Children: {[c.name for c in chip.children]}")
print(f"child_dict keys: {list(chip.child_dict.keys())}")
print(f"child_dict access test:")
for name in ['rect1', 'rect2', 'rect3']:
    try:
        cell = chip.child_dict[name]
        print(f"  chip.child_dict['{name}'] = {cell.name} ✓")
    except KeyError:
        print(f"  chip.child_dict['{name}'] = KeyError ✗")

# Export and import
os.makedirs('demo_outputs', exist_ok=True)
gds_file = 'demo_outputs/test_child_dict.gds'
chip.export_gds(gds_file, use_tech_file=True)
imported = Cell.from_gds(gds_file, use_tech_file=True)

# Check imported child_dict
print("\n[Imported]")
print(f"Children: {[c.name for c in imported.children]}")
print(f"child_dict keys: {list(imported.child_dict.keys())}")
print(f"child_dict access test:")
for name in ['rect1', 'rect2', 'rect3']:
    try:
        cell = imported.child_dict[name]
        print(f"  imported.child_dict['{name}'] = {cell.name} ✓")
    except KeyError:
        print(f"  imported.child_dict['{name}'] = KeyError ✗")

# Verify
print("\n[Verification]")
all_ok = True
for child in imported.children:
    in_dict = child.name in imported.child_dict
    correct = imported.child_dict.get(child.name) is child
    status = "✓" if (in_dict and correct) else "✗"
    print(f"  {child.name}: in_dict={in_dict}, correct_ref={correct} {status}")
    if not (in_dict and correct):
        all_ok = False

print("\n" + "="*80)
if all_ok:
    print("✓ SUCCESS! child_dict properly updated during import")
else:
    print("✗ FAILED! child_dict not properly updated")
print("="*80)
