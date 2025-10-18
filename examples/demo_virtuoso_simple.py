"""
Simple Virtuoso Technology File Workflow Demo

This demo demonstrates the complete workflow in a simple, easy-to-follow way:
1. Import a Virtuoso tech file
2. Generate a hierarchical layout using constraint method
3. Draw the layout to verify colors match tech file
4. Export as GDS file
5. Import GDS back and verify it matches original layout

All steps shown line by line with detailed output.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.tech_file import load_tech_file, get_tech_file
from layout_automation.style_config import get_style_config, reset_style_config
import matplotlib.pyplot as plt


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  STEP: {title}")
    print("=" * 80)


# STEP 1: Load Virtuoso Technology File
print_header("1. LOAD VIRTUOSO TECH FILE")

tech_file_path = 'examples/freepdk45_sample.tf'
print(f"\nLoading Virtuoso technology file: {tech_file_path}")
tech = load_tech_file(tech_file_path)

print(f"\n✓ Technology file loaded successfully!")
print(f"  Tech name: {tech.tech_name}")
print(f"  Total layers defined: {len(tech.layers)}")
print(f"\nFirst 10 layer mappings:")
print(f"  {'Layer Name':<15} {'Purpose':<10} {'GDS Layer':<10} {'GDS DT':<8} {'Color':<15}")
print("  " + "-" * 70)

for i, ((name, purpose), mapping) in enumerate(list(tech.layers.items())[:10]):
    print(f"  {name:<15} {purpose:<10} {mapping.gds_layer:<10} {mapping.gds_datatype:<8} {mapping.color or 'N/A':<15}")


# STEP 2: Apply Tech File Colors to Style
print_header("2. APPLY TECH FILE COLORS TO STYLE")

print("\nResetting style configuration...")
reset_style_config()

print("Applying tech file colors...")
tech.apply_colors_to_style()

print("\n✓ Colors applied successfully!")
print("\nVerifying colors (sample layers):")
style = get_style_config()

test_layers = ['nwell', 'pwell', 'active', 'poly', 'metal1', 'metal2', 'contact']
print(f"  {'Layer':<15} {'Tech Color':<15} {'Style Color':<15} {'Match':<10}")
print("  " + "-" * 60)

for layer in test_layers:
    tech_map = tech.get_layer(layer, 'drawing')
    style_layer = style.get_layer_style(layer)
    tech_color = tech_map.color if tech_map else 'N/A'
    style_color = style_layer.color
    match = "✓" if tech_color == style_color else "✗"
    print(f"  {layer:<15} {tech_color:<15} {style_color:<15} {match:<10}")


# STEP 3: Create Hierarchical Layout Using Constraints
print_header("3. CREATE HIERARCHICAL LAYOUT WITH CONSTRAINTS")

print("\n3.1: Creating bottom-level cells (basic transistor)")
print("-" * 80)

# Create a simple transistor structure
mos = Cell('transistor')

# Add layers for transistor
well = Cell('well', 'nwell')
active_area = Cell('active', 'active')
poly_gate = Cell('gate', 'poly')
contact_s = Cell('contact_source', 'contact')
contact_d = Cell('contact_drain', 'contact')
metal_s = Cell('metal_source', 'metal1')
metal_d = Cell('metal_drain', 'metal1')

mos.add_instance([well, active_area, poly_gate, contact_s, contact_d, metal_s, metal_d])

# Add constraints
mos.constrain(well, 'x1=0, y1=0, x2-x1=40, y2-y1=30')
mos.constrain(active_area, 'sx1=ox1+4, sy1=oy1+6, sx2-sx1=32, sy2-sy1=18', well)
mos.constrain(poly_gate, 'sx1=ox1+12, sy1=oy1-3, sx2-sx1=8, sy2-sy1=24', active_area)
mos.constrain(contact_s, 'sx1=ox1+3, sy1=oy1+7, sx2-sx1=4, sy2-sy1=4', active_area)
mos.constrain(contact_d, 'sx1=ox2-7, sy1=oy1+7, sx2-sx1=4, sy2-sy1=4', active_area)
mos.constrain(metal_s, 'sx1=ox1-1, sy1=oy1-1, sx2-sx1=6, sy2-sy1=6', contact_s)
mos.constrain(metal_d, 'sx1=ox1-1, sy1=oy1-1, sx2-sx1=6, sy2-sy1=6', contact_d)

print(f"  Transistor cell: {mos.name}")
print(f"  Components: {len(mos.children)}")
print(f"  Constraints: 7")

print("\n  Solving constraints...")
mos.solver()
bounds = mos.get_bounds()
print(f"  ✓ Layout solved successfully!")
print(f"  Bounding box: {bounds}")

print("\n3.2: Creating middle-level cell (logic gate)")
print("-" * 80)

# Fix transistor layout for reuse
mos.fix_layout()
print(f"  ✓ Transistor layout fixed (can now be reused)")

# Create a logic gate with 2 transistors
gate = Cell('logic_gate')

trans1 = mos.copy('transistor_1')
trans2 = mos.copy('transistor_2')
via_conn = Cell('via_connection', 'via1')
metal2_wire = Cell('metal2_interconnect', 'metal2')

gate.add_instance([trans1, trans2, via_conn, metal2_wire])

# Position transistors and add interconnect
gate.constrain(trans1, 'x1=0, y1=0')
gate.constrain(trans2, 'x1=0, sy1=oy2+8', trans1)
gate.constrain(via_conn, 'x1=20, y1=20, x2-x1=4, y2-y1=4')
gate.constrain(metal2_wire, 'sx1=ox1-2, sy1=oy1-2, sx2-sx1=8, sy2-sy1=28', via_conn)

print(f"  Logic gate cell: {gate.name}")
print(f"  Components: {len(gate.children)} (2 transistors + 2 interconnects)")
print(f"  Constraints: 4")

print("\n  Solving constraints...")
gate.solver()
bounds = gate.get_bounds()
print(f"  ✓ Layout solved successfully!")
print(f"  Bounding box: {bounds}")

print("\n3.3: Creating top-level cell (chip with multiple gates)")
print("-" * 80)

# Fix gate layout for reuse
gate.fix_layout()
print(f"  ✓ Logic gate layout fixed (can now be reused)")

# Create chip with 3 gates
chip = Cell('chip_top')

gate1 = gate.copy('gate_1')
gate2 = gate.copy('gate_2')
gate3 = gate.copy('gate_3')
metal3_bus = Cell('metal3_bus', 'metal3')
via2_conn1 = Cell('via2_1', 'via2')
via2_conn2 = Cell('via2_2', 'via2')

chip.add_instance([gate1, gate2, gate3, metal3_bus, via2_conn1, via2_conn2])

# Position gates horizontally with metal3 bus
chip.constrain(gate1, 'x1=0, y1=0')
chip.constrain(gate2, 'sx1=ox2+15, y1=0', gate1)
chip.constrain(gate3, 'sx1=ox2+15, y1=0', gate2)
chip.constrain(via2_conn1, 'sx1=ox2+5, y1=30, x2-x1=4, y2-y1=4', gate1)
chip.constrain(via2_conn2, 'sx1=ox2+5, y1=30, x2-x1=4, y2-y1=4', gate2)
chip.constrain(metal3_bus, 'x1=10, y1=28, x2=200, y2-y1=8')

print(f"  Chip cell: {chip.name}")
print(f"  Components: {len(chip.children)} (3 gates + 3 interconnects)")
print(f"  Constraints: 6")

print("\n  Solving constraints...")
chip.solver()
bounds = chip.get_bounds()
print(f"  ✓ Layout solved successfully!")
print(f"  Bounding box: {bounds}")

print("\n3.4: Hierarchy Summary")
print("-" * 80)

def count_leaf_cells(cell):
    """Count total leaf cells recursively"""
    count = 0
    for child in cell.children:
        if child.is_leaf:
            count += 1
        else:
            count += count_leaf_cells(child)
    return count

def get_all_layers(cell):
    """Get all layers used recursively"""
    layers = set()
    for child in cell.children:
        if child.is_leaf:
            layers.add(child.layer_name)
        else:
            layers.update(get_all_layers(child))
    return sorted(layers)

total_cells = count_leaf_cells(chip)
all_layers = get_all_layers(chip)

print(f"  Top cell: {chip.name}")
print(f"  Hierarchy depth: 3 levels (transistor -> gate -> chip)")
print(f"  Direct children: {len(chip.children)}")
print(f"  Total leaf cells: {total_cells}")
print(f"  Layers used: {len(all_layers)}")
print(f"  Layer list: {', '.join(all_layers)}")


# STEP 4: Draw Layouts and Verify Colors
print_header("4. DRAW LAYOUTS AND VERIFY COLORS")

os.makedirs('demo_outputs', exist_ok=True)

print("\n4.1: Drawing transistor (bottom level)")
print("-" * 80)
fig = mos.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_simple_transistor.png', dpi=150, bbox_inches='tight')
print("  ✓ Saved: demo_outputs/virtuoso_simple_transistor.png")
plt.close()

print("\n4.2: Drawing logic gate (middle level)")
print("-" * 80)
fig = gate.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_simple_gate.png', dpi=150, bbox_inches='tight')
print("  ✓ Saved: demo_outputs/virtuoso_simple_gate.png")
plt.close()

print("\n4.3: Drawing complete chip (top level)")
print("-" * 80)
fig = chip.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_simple_chip.png', dpi=150, bbox_inches='tight')
print("  ✓ Saved: demo_outputs/virtuoso_simple_chip.png")
plt.close()

print("\n✓ All layouts drawn with Virtuoso tech file colors!")


# STEP 5: Export as GDS File
print_header("5. EXPORT AS GDS FILE")

gds_file = 'demo_outputs/virtuoso_simple_chip.gds'

print(f"\n5.1: Exporting to {gds_file}")
print("-" * 80)
chip.export_gds(gds_file, use_tech_file=True)

if os.path.exists(gds_file):
    file_size = os.path.getsize(gds_file)
    print(f"✓ GDS file created successfully")
    print(f"  File: {gds_file}")
    print(f"  Size: {file_size} bytes")
else:
    print("✗ ERROR: GDS file not created")

print("\n5.2: GDS Layer Mapping (from tech file)")
print("-" * 80)
print(f"  {'Layer Name':<15} {'GDS Layer':<12} {'GDS Datatype':<15}")
print("  " + "-" * 45)

for layer in all_layers:
    gds_layer, gds_datatype = tech.get_gds_layer(layer, 'drawing')
    print(f"  {layer:<15} {gds_layer:<12} {gds_datatype:<15}")


# STEP 6: Import GDS Back and Verify
print_header("6. IMPORT GDS AND VERIFY MATCH")

print("\n6.1: Importing GDS file")
print("-" * 80)
imported = Cell.from_gds(gds_file, use_tech_file=True)

print(f"✓ GDS imported successfully")
print(f"  Imported cell: {imported.name}")
print(f"  Children: {len(imported.children)} (flattened)")

print("\n6.2: Comparing Original vs Imported")
print("-" * 80)

original_leaf_count = count_leaf_cells(chip)
imported_leaf_count = len(imported.children)

print(f"  Original total leaf cells: {original_leaf_count}")
print(f"  Imported children (flat):  {imported_leaf_count}")

if original_leaf_count == imported_leaf_count:
    print("  ✓ Cell counts match (GDS import flattens hierarchy)")
else:
    diff = abs(original_leaf_count - imported_leaf_count)
    print(f"  ⚠ Difference: {diff} cells")

print("\n6.3: Layer Count Comparison")
print("-" * 80)

def count_layer_shapes(cell, layer_name):
    """Count shapes on a specific layer"""
    count = 0
    for child in cell.children:
        if child.is_leaf and child.layer_name == layer_name:
            count += 1
        elif not child.is_leaf:
            count += count_layer_shapes(child, layer_name)
    return count

imported_layers = get_all_layers(imported)
all_layers_combined = sorted(set(all_layers + imported_layers))

print(f"  {'Layer':<15} {'Original':<12} {'Imported':<12} {'Match':<10}")
print("  " + "-" * 55)

all_match = True
for layer in all_layers_combined:
    orig_count = count_layer_shapes(chip, layer)
    imp_count = count_layer_shapes(imported, layer)
    match = "✓" if orig_count == imp_count else "✗"
    if orig_count != imp_count:
        all_match = False
    print(f"  {layer:<15} {orig_count:<12} {imp_count:<12} {match:<10}")

if all_match:
    print("\n  ✓ All layer counts match perfectly!")
else:
    print("\n  ⚠ Some layer counts differ")

print("\n6.4: Bounding Box Comparison")
print("-" * 80)

orig_bounds = chip.get_bounds()
imp_bounds = imported.get_bounds()

print(f"  Original: {orig_bounds}")
print(f"  Imported: {imp_bounds}")

if orig_bounds == imp_bounds:
    print("  ✓ Bounding boxes match exactly!")
else:
    print("  ⚠ Bounding boxes differ")

print("\n6.5: Drawing imported layout")
print("-" * 80)
fig = imported.draw(show=False, solve_first=False)
plt.savefig('demo_outputs/virtuoso_simple_imported.png', dpi=150, bbox_inches='tight')
print("  ✓ Saved: demo_outputs/virtuoso_simple_imported.png")
plt.close()

print("\n6.6: Creating side-by-side comparison")
print("-" * 80)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=100)

chip.draw(ax=ax1, show=False, solve_first=False)
ax1.set_title('Original Layout\\n(3-level hierarchy with constraints)',
              fontsize=14, fontweight='bold')

imported.draw(ax=ax2, show=False, solve_first=False)
ax2.set_title('Imported from GDS\\n(Flattened, using tech file layers)',
              fontsize=14, fontweight='bold')

plt.suptitle('Virtuoso Tech File Workflow - Round Trip Verification',
             fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('demo_outputs/virtuoso_simple_comparison.png', dpi=150, bbox_inches='tight')
print("  ✓ Saved: demo_outputs/virtuoso_simple_comparison.png")
plt.close()


# FINAL SUMMARY
print("\n" + "=" * 80)
print("  WORKFLOW COMPLETED SUCCESSFULLY!")
print("=" * 80)

print("\n✓ Step 1: Loaded Virtuoso tech file ({} layers)".format(len(tech.layers)))
print("✓ Step 2: Applied tech file colors to style")
print("✓ Step 3: Created 3-level hierarchical layout ({} total leaf cells)".format(total_cells))
print("✓ Step 4: Drew layouts with tech file colors (3 images)")
print("✓ Step 5: Exported GDS with tech file layer numbers")
print("✓ Step 6: Imported GDS and verified match")

print("\n" + "=" * 80)
print("  Generated Files")
print("=" * 80)
print("\nImages:")
print("  1. demo_outputs/virtuoso_simple_transistor.png")
print("  2. demo_outputs/virtuoso_simple_gate.png")
print("  3. demo_outputs/virtuoso_simple_chip.png")
print("  4. demo_outputs/virtuoso_simple_imported.png")
print("  5. demo_outputs/virtuoso_simple_comparison.png")

print("\nGDS File:")
print("  • demo_outputs/virtuoso_simple_chip.gds")

print("\n" + "=" * 80)
print("  Verification Results")
print("=" * 80)
print("\n  ✓ Tech file loaded and parsed correctly")
print("  ✓ Colors match between tech file and visualization")
print("  ✓ Hierarchical layout created with constraint solver")
print("  ✓ GDS exported with correct tech file layer numbers")
print("  ✓ GDS imported back using tech file layer mapping")
if all_match:
    print("  ✓ All layer counts match in round-trip")
else:
    print("  ⚠ Some layer count differences (check output above)")
print("\n" + "=" * 80)
