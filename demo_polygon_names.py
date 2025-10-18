"""
Complete Demo: Polygon Cell Name Preservation

Demonstrates that polygon cell names are preserved through GDS export/import:
1. Create layout with meaningful polygon names
2. Export to GDS (polygons become separate named cells)
3. Import from GDS
4. Verify names and structure preserved exactly
5. Show GDS file structure
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.tech_file import load_tech_file
from layout_automation.style_config import reset_style_config
import gdstk

print("="*80)
print("POLYGON CELL NAME PRESERVATION - Complete Demo")
print("="*80)

# Load tech file
print("\n[Step 1] Loading tech file...")
tech = load_tech_file('examples/freepdk45_sample.tf')
reset_style_config()
tech.apply_colors_to_style()
print(f"✓ Loaded {len(tech.layers)} layers")

# Create layout with meaningful polygon names
print("\n[Step 2] Creating layout with named polygons...")
print("-"*80)

chip = Cell('standard_cell_layout')

# Use descriptive names that document design intent
nwell_region = Cell('PMOS_nwell_area', 'nwell')
pwell_region = Cell('NMOS_pwell_area', 'pwell')
gate_poly = Cell('transistor_gate', 'poly')
metal_vdd = Cell('power_rail_VDD', 'metal1')
metal_gnd = Cell('power_rail_VSS', 'metal1')
metal_signal = Cell('output_wire', 'metal2')
via_power = Cell('vdd_via_to_m2', 'via1')

chip.add_instance([nwell_region, pwell_region, gate_poly,
                   metal_vdd, metal_gnd, metal_signal, via_power])

chip.constrain(nwell_region, 'x1=0, y1=20, x2=60, y2=40')
chip.constrain(pwell_region, 'x1=0, y1=0, x2=60, y2=20')
chip.constrain(gate_poly, 'x1=25, y1=5, x2=35, y2=35')
chip.constrain(metal_vdd, 'x1=5, y1=35, x2=55, y2=38')
chip.constrain(metal_gnd, 'x1=5, y1=2, x2=55, y2=5')
chip.constrain(metal_signal, 'x1=20, y1=10, x2=40, y2=30')
chip.constrain(via_power, 'x1=10, y1=34, x2=12, y2=36')

chip.solver()

print(f"Created: {chip.name}")
print(f"Polygons with meaningful names:")
for i, child in enumerate(chip.children, 1):
    print(f"  {i}. {child.name:<25} (layer: {child.layer_name})")

# Export to GDS
print("\n[Step 3] Exporting to GDS...")
print("-"*80)
os.makedirs('demo_outputs', exist_ok=True)
gds_file = 'demo_outputs/polygon_names_demo.gds'
chip.export_gds(gds_file, use_tech_file=True)
file_size = os.path.getsize(gds_file)
print(f"✓ Exported to: {gds_file}")
print(f"  File size: {file_size} bytes")

# Show GDS structure
print("\n[Step 4] GDS File Structure...")
print("-"*80)
lib = gdstk.read_gds(gds_file)
print(f"GDS Library: {lib.name}")
print(f"Total cells: {len(lib.cells)}")
print("\nCells in GDS file:")
for i, cell in enumerate(lib.cells, 1):
    poly_count = len(cell.polygons)
    ref_count = len(cell.references)
    print(f"  {i}. {cell.name}")
    print(f"      Polygons: {poly_count}, References: {ref_count}")

# Import from GDS
print("\n[Step 5] Importing from GDS...")
print("-"*80)
imported = Cell.from_gds(gds_file, use_tech_file=True)
print(f"✓ Imported: {imported.name}")
print(f"  Children: {len(imported.children)}")

print("\nImported polygons:")
for i, child in enumerate(imported.children, 1):
    print(f"  {i}. {child.name:<25} (layer: {child.layer_name})")

# Verify names preserved
print("\n[Step 6] Verification...")
print("-"*80)

original_names = {c.name for c in chip.children}
imported_names = {c.name for c in imported.children}

print(f"Original polygon count: {len(original_names)}")
print(f"Imported polygon count: {len(imported_names)}")

if original_names == imported_names:
    print("\n✓ SUCCESS! All polygon names preserved exactly!")
    print("\nPreserved polygon names:")
    for name in sorted(original_names):
        print(f"  ✓ {name}")
else:
    print("\n✗ MISMATCH!")
    missing = original_names - imported_names
    extra = imported_names - original_names
    if missing:
        print(f"  Missing: {missing}")
    if extra:
        print(f"  Extra: {extra}")

# Verify structure preserved
print("\n[Step 7] Structure Verification...")
print("-"*80)

def verify_structure(orig, imp):
    matches = []
    for orig_child, imp_child in zip(orig.children, imp.children):
        name_match = orig_child.name == imp_child.name
        leaf_match = orig_child.is_leaf == imp_child.is_leaf
        layer_match = orig_child.layer_name == imp_child.layer_name
        all_match = name_match and leaf_match and layer_match
        matches.append({
            'name': orig_child.name,
            'name_ok': name_match,
            'leaf_ok': leaf_match,
            'layer_ok': layer_match,
            'all_ok': all_match
        })
    return matches

matches = verify_structure(chip, imported)

print(f"{'Polygon Name':<30} {'Name':<8} {'Leaf':<8} {'Layer':<8} {'Status'}")
print("-"*80)
all_ok = True
for m in matches:
    name_sym = '✓' if m['name_ok'] else '✗'
    leaf_sym = '✓' if m['leaf_ok'] else '✗'
    layer_sym = '✓' if m['layer_ok'] else '✗'
    status = '✓ OK' if m['all_ok'] else '✗ FAIL'
    if not m['all_ok']:
        all_ok = False
    print(f"{m['name']:<30} {name_sym:<8} {leaf_sym:<8} {layer_sym:<8} {status}")

print("\n" + "="*80)
if all_ok:
    print("✓ COMPLETE SUCCESS!")
    print("  - All polygon names preserved")
    print("  - All layer information preserved")
    print("  - All structure preserved (leaf/non-leaf)")
else:
    print("✗ Some verification failed")
print("="*80)

print(f"\nGenerated file: {gds_file}")
print("\nBenefits of name preservation:")
print("  • Meaningful debugging (know which polygon has issues)")
print("  • Design intent documentation (names explain purpose)")
print("  • Standard cell library workflow (reusable named components)")
print("  • Consistent round-trip export/import")
print()
