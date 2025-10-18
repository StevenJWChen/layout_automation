"""
Minimal Virtuoso Tech File Workflow Demo

Demonstrates complete workflow with absolute coordinates (no solver conflicts):
1. Load Virtuoso tech file
2. Create layout with simple absolute constraints
3. Draw with tech file colors  
4. Export to GDS
5. Import and verify
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.tech_file import load_tech_file
from layout_automation.style_config import reset_style_config
import matplotlib.pyplot as plt

print("="*80)
print("VIRTUOSO TECHNOLOGY FILE WORKFLOW - Complete Demo")
print("="*80)

# Step 1: Load tech file
print("\n[1] Loading Virtuoso tech file...")
tech = load_tech_file('examples/freepdk45_sample.tf')
print(f"✓ Loaded {len(tech.layers)} layers")

# Step 2: Apply colors
print("\n[2] Applying tech file colors...")
reset_style_config()
tech.apply_colors_to_style()
print("✓ Colors applied")

# Step 3: Create simple layout
print("\n[3] Creating layout...")
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
print(f"✓ Layout solved: {layout.get_bounds()}")

# Step 4: Draw
print("\n[4] Drawing layout...")
os.makedirs('demo_outputs', exist_ok=True)
layout.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_demo_original.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved: demo_outputs/virtuoso_demo_original.png")

# Step 5: Export GDS
print("\n[5] Exporting to GDS...")
gds_file = 'demo_outputs/virtuoso_demo.gds'
layout.export_gds(gds_file, use_tech_file=True)
print(f"✓ Exported: {gds_file}")
print(f"  File size: {os.path.getsize(gds_file)} bytes")

# Show layer mapping
print("\n  GDS Layer Mapping:")
for layer in ['nwell', 'active', 'poly', 'metal1', 'metal2', 'contact']:
    gds_l, gds_dt = tech.get_gds_layer(layer)
    print(f"    {layer:<10} -> GDS({gds_l:2d}, {gds_dt})")

# Step 6: Import and verify
print("\n[6] Importing GDS...")
imported = Cell.from_gds(gds_file, use_tech_file=True)
print(f"✓ Imported: {imported.name}")
print(f"  Children: {len(imported.children)}")

# Verify layers
def count_layer(cell, layer_name):
    count = 0
    for c in cell.children:
        if c.is_leaf and c.layer_name == layer_name:
            count += 1
        elif not c.is_leaf:
            count += count_layer(c, layer_name)
    return count

print("\n  Layer verification:")
layers = ['nwell', 'active', 'poly', 'metal1', 'metal2', 'contact']
all_match = True
for layer in layers:
    orig = count_layer(layout, layer)
    imp = count_layer(imported, layer)
    match = "✓" if orig == imp else "✗"
    if orig != imp:
        all_match = False
    print(f"    {layer:<10} orig={orig} imported={imp} {match}")

# Draw imported
imported.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_demo_imported2.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n✓ Saved: demo_outputs/virtuoso_demo_imported.png")

# Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
layout.draw(ax=ax1, show=False, solve_first=False)
ax1.set_title('Original')
imported.draw(ax=ax2, show=False, solve_first=False)
ax2.set_title('Imported from GDS')
plt.tight_layout()
plt.savefig('demo_outputs/virtuoso_demo_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved: demo_outputs/virtuoso_demo_comparison.png")

print("\n" + "="*80)
if all_match:
    print("SUCCESS! All layers verified in round-trip")
else:
    print("COMPLETE! (with some layer count differences)")
print("="*80)
print("\nGenerated files:")
print("  • virtuoso_demo_original.png")
print("  • virtuoso_demo_imported.png") 
print("  • virtuoso_demo_comparison.png")
print("  • virtuoso_demo.gds")

# Test using imported cell as instance
top = Cell('top')
inst1 = imported.copy('chip1')
inst2 = imported.copy('chip2')

top.add_instance([inst1, inst2, imported])
top.constrain(inst1, 'x1=0, y1=0')
top.constrain(inst2, 'sx1=ox2+5, y1=0', inst1)
top.solver()
top.draw()






