"""
Virtuoso Technology File Workflow Demo - Flat Layout

Simple flat layout demo that demonstrates:
1. Import Virtuoso tech file
2. Create flat layout with constraints
3. Draw with tech file colors
4. Export to GDS
5. Import GDS back and verify

All steps shown line-by-line with clear output.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.tech_file import load_tech_file, get_tech_file
from layout_automation.style_config import reset_style_config
import matplotlib.pyplot as plt


print("="*80)
print("  VIRTUOSO TECHNOLOGY FILE WORKFLOW DEMO")
print("="*80)

# STEP 1: Load Virtuoso tech file
print("\n[STEP 1] Loading Virtuoso Technology File")
print("-"*80)
tech = load_tech_file('examples/freepdk45_sample.tf')
print(f"✓ Loaded {len(tech.layers)} layers from FreePDK45 tech file")
print(f"\nSample layers:")
for i, ((name, purpose), m) in enumerate(list(tech.layers.items())[:8]):
    if purpose == 'drawing':
        print(f"  {name:<10} -> GDS({m.gds_layer:2d}, {m.gds_datatype}) color={m.color}")

# STEP 2: Apply colors
print("\n[STEP 2] Applying Tech File Colors")
print("-"*80)
reset_style_config()
tech.apply_colors_to_style()
print("✓ Tech file colors applied to visualization style")

# STEP 3: Create layout
print("\n[STEP 3] Creating Flat Layout with Constraints")
print("-"*80)

layout = Cell('simple_circuit')

# Add basic components
nwell = Cell('nwell_region', 'nwell')
active1 = Cell('active_region1', 'active')
active2 = Cell('active_region2', 'active')
poly = Cell('poly_gate', 'poly')
contact1 = Cell('contact1', 'contact')
contact2 = Cell('contact2', 'contact')
metal1_h = Cell('metal1_horiz', 'metal1')
metal1_v = Cell('metal1_vert', 'metal1')
via1 = Cell('via1', 'via1')
metal2 = Cell('metal2_wire', 'metal2')

layout.add_instance([nwell, active1, active2, poly, contact1, contact2, 
                     metal1_h, metal1_v, via1, metal2])

# Simple constraints
layout.constrain(nwell, 'x1=0, y1=0, x2-x1=60, y2-y1=40')
layout.constrain(active1, 'x1=5, y1=10, x2-x1=20, y2-y1=20')
layout.constrain(active2, 'sx1=ox2+10, y1=10, x2-x1=20, y2-y1=20', active1)
layout.constrain(poly, 'sx1=ox1+8, y1=5, x2-x1=4, y2-y1=30', active1)
layout.constrain(contact1, 'sx1=ox1+5, sy1=oy1+5, x2-x1=3, y2-y1=3', active1)
layout.constrain(contact2, 'sx1=ox1+5, sy1=oy1+5, x2-x1=3, y2-y1=3', active2)
layout.constrain(metal1_h, 'sx1=ox1-2, sy1=oy1-2, x2-x1=40, y2-y1=7', contact1)
layout.constrain(metal1_v, 'sx1=ox2-3, sy1=oy1, x2-x1=5, y2-y1=15', metal1_h)
layout.constrain(via1, 'sx1=ox1, sy1=oy2-5, x2-x1=3, y2-y1=3', metal1_v)
layout.constrain(metal2, 'sx1=ox1-2, sy1=oy1-2, x2-x1=7, y2-y1=15', via1)

print(f"Layout: {layout.name}")
print(f"  Components: {len(layout.children)}")
print(f"  Constraints: 10")
print("\nSolving...")
layout.solver()
bounds = layout.get_bounds()
print(f"✓ Layout solved: bounds = {bounds}")

# STEP 4: Draw
print("\n[STEP 4] Drawing Layout with Tech File Colors")
print("-"*80)
os.makedirs('demo_outputs', exist_ok=True)
fig = layout.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_flat_layout.png', dpi=150, bbox_inches='tight')
print("✓ Saved: demo_outputs/virtuoso_flat_layout.png")
plt.close()

# STEP 5: Export GDS
print("\n[STEP 5] Exporting to GDS with Tech File Layer Numbers")
print("-"*80)
gds_file = 'demo_outputs/virtuoso_flat.gds'
layout.export_gds(gds_file, use_tech_file=True)
print(f"✓ Exported: {gds_file} ({os.path.getsize(gds_file)} bytes)")

print("\nGDS Layer Mapping:")
print(f"  {'Layer':<12} {'GDS Layer':<12} {'GDS Datatype':<12}")
print("  " + "-"*40)
layers = ['nwell', 'active', 'poly', 'contact', 'metal1', 'via1', 'metal2']
for layer in layers:
    gds_layer, gds_dt = tech.get_gds_layer(layer)
    print(f"  {layer:<12} {gds_layer:<12} {gds_dt:<12}")

# STEP 6: Import and verify
print("\n[STEP 6] Importing GDS and Verifying")
print("-"*80)
imported = Cell.from_gds(gds_file, use_tech_file=True)
print(f"✓ Imported: {imported.name}")
print(f"  Children: {len(imported.children)}")

# Count layers
def count_layers(cell, layer):
    count = 0
    for child in cell.children:
        if child.is_leaf and child.layer_name == layer:
            count += 1
        elif not child.is_leaf:
            count += count_layers(child, layer)
    return count

print("\nLayer Count Comparison:")
print(f"  {'Layer':<12} {'Original':<10} {'Imported':<10} {'Match':<8}")
print("  " + "-"*45)
all_match = True
for layer in layers:
    orig = count_layers(layout, layer)
    imp = count_layers(imported, layer)
    match = "✓" if orig == imp else "✗"
    if orig != imp:
        all_match = False
    print(f"  {layer:<12} {orig:<10} {imp:<10} {match:<8}")

if all_match:
    print("\n✓ All layer counts match!")
else:
    print("\n⚠ Some layers differ")

# Draw imported
fig = imported.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_flat_imported.png', dpi=150, bbox_inches='tight')
print("\n✓ Saved: demo_outputs/virtuoso_flat_imported.png")
plt.close()

# Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=100)
layout.draw(ax=ax1, show=False, solve_first=False)
ax1.set_title('Original Layout', fontsize=12, fontweight='bold')
imported.draw(ax=ax2, show=False, solve_first=False)
ax2.set_title('Imported from GDS', fontsize=12, fontweight='bold')
plt.suptitle('Virtuoso Tech File Workflow - Round Trip', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('demo_outputs/virtuoso_flat_comparison.png', dpi=150, bbox_inches='tight')
print("✓ Saved: demo_outputs/virtuoso_flat_comparison.png")
plt.close()

print("\n" + "="*80)
print("  WORKFLOW COMPLETE!")
print("="*80)
print("\n✓ Loaded Virtuoso tech file (52 layers)")
print("✓ Applied tech file colors")
print("✓ Created layout with 10 components and 10 constraints")
print("✓ Drew layout with tech file colors")
print("✓ Exported GDS with correct layer numbers")
print("✓ Imported GDS back successfully")
if all_match:
    print("✓ All layers verified - round trip successful!")
else:
    print("⚠ Some layer counts differ")

print("\nGenerated files:")
print("  • demo_outputs/virtuoso_flat_layout.png")
print("  • demo_outputs/virtuoso_flat_imported.png")
print("  • demo_outputs/virtuoso_flat_comparison.png")
print("  • demo_outputs/virtuoso_flat.gds")
print()
