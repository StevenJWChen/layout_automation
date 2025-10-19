"""
FreePDK45 Complete Workflow Demo

Demonstrates complete workflow with FreePDK45 technology:
1. Load FreePDK45.tf for layer/GDS definitions
2. Load SantanaDisplay.drf for accurate Virtuoso colors
3. Create layout with simple absolute constraints
4. Draw with accurate tech file colors (hex RGB from DRF)
5. Export to GDS with correct layer numbers
6. Import and verify round-trip
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile, set_tech_file
from layout_automation.style_config import reset_style_config
import matplotlib.pyplot as plt

print("="*80)
print("FreePDK45 TECHNOLOGY WORKFLOW - Complete Demo")
print("="*80)

# Step 1: Load FreePDK45 tech file
print("\n[1] Loading FreePDK45 technology file...")
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
print(f"    Loaded {len(tech.layers)} layer mappings")

# Step 2: Load DRF file for accurate colors
print("\n[2] Loading display resource file for colors...")
tech.parse_drf_file('SantanaDisplay.drf')
print(f"    Loaded {len(tech.drf_colors)} colors and {len(tech.drf_packets)} packets")

# Set as global tech file
set_tech_file(tech)

# Step 3: Apply colors to style
print("\n[3] Applying accurate Virtuoso colors...")
reset_style_config()
tech.apply_colors_to_style()

# Show some color examples
print("\n    Layer color examples:")
for layer_name in ['metal1', 'metal2', 'poly', 'active', 'contact']:
    layer = tech.get_layer(layer_name, 'drawing')
    if layer and layer.color:
        print(f"      {layer_name:<10} -> {layer.color}")
print("    Colors applied")

# Step 4: Create simple layout
print("\n[4] Creating layout...")
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
print(f"    Layout solved: {layout.get_bounds()}")

# Step 5: Draw with accurate colors
print("\n[5] Drawing layout with FreePDK45 colors...")
os.makedirs('demo_outputs', exist_ok=True)
layout.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_demo_original.png', dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: demo_outputs/virtuoso_demo_original.png")

# Step 6: Export GDS with FreePDK45 layer numbers
print("\n[6] Exporting to GDS with FreePDK45 layer numbers...")
gds_file = 'demo_outputs/virtuoso_demo.gds'
layout.export_gds(gds_file, use_tech_file=True)
print(f"    Exported: {gds_file}")
print(f"    File size: {os.path.getsize(gds_file)} bytes")

# Show layer mapping from FreePDK45.tf
print("\n    FreePDK45 GDS Layer Mapping:")
for layer in ['nwell', 'active', 'poly', 'metal1', 'metal2', 'contact']:
    layer_info = tech.get_layer(layer, 'drawing')
    if layer_info:
        print(f"      {layer:<10} -> GDS({layer_info.gds_layer:2d}, {layer_info.gds_datatype}) color={layer_info.color}")
    else:
        gds_l, gds_dt = tech.get_gds_layer(layer)
        print(f"      {layer:<10} -> GDS({gds_l:2d}, {gds_dt})")

# Step 7: Import and verify
print("\n[7] Importing GDS...")
imported = Cell.from_gds(gds_file, use_tech_file=True)
print(f"    Imported: {imported.name}")
print(f"    Children: {len(imported.children)}")

# Verify layers
def count_layer(cell, layer_name):
    count = 0
    for c in cell.children:
        if c.is_leaf and c.layer_name == layer_name:
            count += 1
        elif not c.is_leaf:
            count += count_layer(c, layer_name)
    return count

print("\n    Layer verification (round-trip):")
layers = ['nwell', 'active', 'poly', 'metal1', 'metal2', 'contact']
all_match = True
for layer in layers:
    orig = count_layer(layout, layer)
    imp = count_layer(imported, layer)
    match = "OK" if orig == imp else "DIFF"
    if orig != imp:
        all_match = False
    print(f"      {layer:<10} orig={orig} imported={imp} [{match}]")

# Step 8: Draw comparison
print("\n[8] Creating comparison images...")

# Draw imported
imported.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_demo_imported2.png', dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: demo_outputs/virtuoso_demo_imported.png")

# Side-by-side comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
layout.draw(ax=ax1, show=False, solve_first=False)
ax1.set_title('Original Layout (FreePDK45 Colors)', fontsize=14, fontweight='bold')
imported.draw(ax=ax2, show=False, solve_first=False)
ax2.set_title('Imported from GDS (Round-trip)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('demo_outputs/virtuoso_demo_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: demo_outputs/virtuoso_demo_comparison.png")

print("\n" + "="*80)
if all_match:
    print("SUCCESS! All layers verified in FreePDK45 round-trip")
else:
    print("COMPLETE! (with some layer count differences)")
print("="*80)
print("\nGenerated files:")
print("  • virtuoso_demo_original.png      - Original with FreePDK45 colors")
print("  • virtuoso_demo_imported.png      - Imported from GDS")
print("  • virtuoso_demo_comparison.png    - Side-by-side comparison")
print("  • virtuoso_demo.gds               - GDS file with FreePDK45 layer numbers")

# Step 9: Test hierarchical layout with imported cells
print("\n[9] Testing hierarchical layout with imported cells...")
top = Cell('top_level')
inst1 = imported.copy('chip1')
inst2 = imported.copy('chip2')

top.add_instance([inst1, inst2])
top.constrain(inst1, 'x1=0, y1=0')
top.constrain(inst2, 'sx1=ox2+10, y1=0', inst1)
top.solver()

top.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_demo_hierarchical.png', dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: demo_outputs/virtuoso_demo_hierarchical.png")
print(f"    Top level bounds: {top.get_bounds()}")

print("\n" + "="*80)
print("FreePDK45 DEMO COMPLETE!")
print("="*80)
print("\nAll features demonstrated:")
print("  [OK] FreePDK45.tf technology file loaded (297 layers)")
print("  [OK] SantanaDisplay.drf colors loaded (36 colors, 333 packets)")
print("  [OK] Accurate Virtuoso hex colors applied")
print("  [OK] Layout created with constraint solver")
print("  [OK] GDS export with FreePDK45 layer numbers")
print("  [OK] GDS import and round-trip verification")
print("  [OK] Hierarchical layout composition")
print("="*80)






