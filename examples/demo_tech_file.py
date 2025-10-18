"""
Technology File Integration Demo

Demonstrates:
1. Creating a custom technology file
2. Loading tech file for layer mappings
3. Applying tech file colors to layouts
4. Exporting GDS with tech file layer numbers
5. Importing GDS using tech file mappings
6. Round-trip verification (export then import)
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile, LayerMapping, set_tech_file, get_tech_file
from layout_automation.style_config import get_style_config, reset_style_config
import matplotlib.pyplot as plt


def create_custom_tech_file():
    """Create a custom technology file with specific layer mappings"""
    print("=" * 70)
    print("CREATING CUSTOM TECHNOLOGY FILE")
    print("=" * 70)

    tech = TechFile()
    tech.tech_name = "demo_tech_180nm"

    # Define layers with GDS numbers and colors
    layers = [
        # Wells
        LayerMapping('nwell', 'drawing', 1, 0, 'lightgreen'),
        LayerMapping('pwell', 'drawing', 2, 0, 'lightcoral'),

        # Diffusions
        LayerMapping('ndiff', 'drawing', 3, 0, 'green'),
        LayerMapping('pdiff', 'drawing', 4, 0, 'tan'),
        LayerMapping('diff', 'drawing', 5, 0, 'brown'),

        # Poly
        LayerMapping('poly', 'drawing', 10, 0, 'red'),

        # Contacts
        LayerMapping('contact', 'drawing', 20, 0, 'black'),

        # Metal layers
        LayerMapping('metal1', 'drawing', 30, 0, 'blue'),
        LayerMapping('metal2', 'drawing', 50, 0, 'red'),
        LayerMapping('metal3', 'drawing', 70, 0, 'green'),
        LayerMapping('metal4', 'drawing', 90, 0, 'orange'),
        LayerMapping('metal5', 'drawing', 110, 0, 'cyan'),
        LayerMapping('metal6', 'drawing', 130, 0, 'magenta'),

        # Vias
        LayerMapping('via1', 'drawing', 40, 0, 'gray'),
        LayerMapping('via2', 'drawing', 60, 0, 'gray'),
        LayerMapping('via3', 'drawing', 80, 0, 'gray'),
        LayerMapping('via4', 'drawing', 100, 0, 'gray'),
        LayerMapping('via5', 'drawing', 120, 0, 'gray'),
    ]

    for layer in layers:
        tech.add_layer(layer)

    print(f"✓ Created technology file: {tech.tech_name}")
    print(f"✓ Total layers: {len(tech.layers)}")

    # Print summary
    tech.print_summary()

    return tech


def apply_tech_colors_to_style(tech):
    """Apply technology file colors to the style configuration"""
    print("\n" + "=" * 70)
    print("APPLYING TECH FILE COLORS TO STYLE")
    print("=" * 70)

    reset_style_config()
    tech.apply_colors_to_style()

    print("✓ Tech file colors applied to style configuration")


def create_test_layout():
    """Create a simple test layout to demonstrate tech file usage"""
    print("\n" + "=" * 70)
    print("CREATING TEST LAYOUT")
    print("=" * 70)

    # Create a simple multi-layer structure
    top = Cell('test_chip')

    # Wells
    nwell = Cell('nwell_region', 'nwell')
    pwell = Cell('pwell_region', 'pwell')

    # Diffusions
    ndiff = Cell('ndiff_area', 'ndiff')
    pdiff = Cell('pdiff_area', 'pdiff')

    # Poly gate
    poly = Cell('poly_gate', 'poly')

    # Contacts
    contact1 = Cell('contact1', 'contact')
    contact2 = Cell('contact2', 'contact')

    # Metal1 routing
    metal1_h = Cell('metal1_h', 'metal1')
    metal1_v = Cell('metal1_v', 'metal1')

    # Via
    via1 = Cell('via1', 'via1')

    # Metal2
    metal2 = Cell('metal2_line', 'metal2')

    # Add all children
    top.add_instance([nwell, pwell, ndiff, pdiff, poly,
                     contact1, contact2, metal1_h, metal1_v,
                     via1, metal2])

    # Position constraints
    # Wells
    top.constrain(nwell, 'x1=0, y1=0, x2-x1=40, y2-y1=30')
    top.constrain(pwell, 'x1=50, y1=0, x2-x1=40, y2-y1=30')

    # Diffusions in wells
    top.constrain(pdiff, 'sx1=ox1+5, sy1=oy1+5, sx2-sx1=10, sy2-sy1=20', nwell)
    top.constrain(ndiff, 'sx1=ox1+5, sy1=oy1+5, sx2-sx1=10, sy2-sy1=20', pwell)

    # Poly gates
    top.constrain(poly, 'sx1=ox1+7, sy1=oy1-2, sx2-sx1=6, sy2-sy1=24', pdiff)

    # Contacts
    top.constrain(contact1, 'sx1=ox1+3, sy1=oy1+8, sx2-sx1=4, sy2-sy1=4', pdiff)
    top.constrain(contact2, 'sx1=ox1+3, sy1=oy1+8, sx2-sx1=4, sy2-sy1=4', ndiff)

    # Metal1 horizontal
    top.constrain(metal1_h, 'sx1=ox1-2, sy1=oy1-2, sx2-sx1=40, sy2-sy1=8', contact1)

    # Metal1 vertical
    top.constrain(metal1_v, 'sx1=ox2-4, sy1=oy1, sx2-sx1=4, sy2-sy1=20', metal1_h)

    # Via on metal1
    top.constrain(via1, 'sx1=ox1, sy1=oy2-8, sx2-sx1=4, sy2-sy1=4', metal1_v)

    # Metal2 over via
    top.constrain(metal2, 'sx1=ox1-2, sy1=oy1-2, sx2-sx1=8, sy2-sy1=20', via1)

    top.solver()
    top.draw()
    print(f"✓ Created test layout: {top.name}")
    print(f"  Layers used: nwell, pwell, ndiff, pdiff, poly, contact, metal1, via1, metal2")

    return top


def demo_gds_export_with_tech(layout):
    """Export GDS using technology file layer numbers"""
    print("\n" + "=" * 70)
    print("EXPORTING GDS WITH TECH FILE")
    print("=" * 70)

    output_file = 'demo_outputs/test_with_techfile.gds'
    layout.export_gds(output_file, use_tech_file=True)

    print(f"✓ Exported GDS to: {output_file}")
    print("  Layer numbers used from tech file:")

    tech = get_tech_file()
    for layer_name in ['nwell', 'pwell', 'ndiff', 'pdiff', 'poly', 'contact',
                       'metal1', 'via1', 'metal2']:
        gds_layer, gds_datatype = tech.get_gds_layer(layer_name)
        print(f"    {layer_name:10s} -> GDS layer {gds_layer:3d}, datatype {gds_datatype}")

    return output_file


def demo_gds_import_with_tech(gds_file):
    """Import GDS using technology file layer mappings"""
    print("\n" + "=" * 70)
    print("IMPORTING GDS WITH TECH FILE")
    print("=" * 70)

    imported = Cell.from_gds(gds_file, use_tech_file=True)

    print(f"✓ Imported cell: {imported.name}")
    print(f"  Total children: {len(imported.children)}")

    # Count layers
    layer_counts = {}
    for child in imported.children:
        if child.is_leaf:
            layer_name = child.layer_name
            layer_counts[layer_name] = layer_counts.get(layer_name, 0) + 1

    print(f"  Layers found:")
    for layer_name, count in sorted(layer_counts.items()):
        print(f"    {layer_name:10s}: {count} shapes")

    return imported


def visualize_layouts(original, imported):
    """Visualize original and imported layouts side by side"""
    print("\n" + "=" * 70)
    print("VISUALIZING LAYOUTS")
    print("=" * 70)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=100)

    # Original layout
    original.draw(ax=ax1, show=False, solve_first=False)
    ax1.set_title('Original Layout\n(Created with constraints)',
                  fontsize=14, fontweight='bold')

    # Imported layout
    imported.draw(ax=ax2, show=False, solve_first=False)
    ax2.set_title('Imported from GDS\n(Using tech file layer mapping)',
                  fontsize=14, fontweight='bold')

    plt.suptitle('Technology File Integration Demo - Round Trip Test',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()

    output_file = 'demo_outputs/tech_file_roundtrip.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved visualization to: {output_file}")
    plt.close()


def demo_layer_map_export():
    """Export the layer mapping to a text file"""
    print("\n" + "=" * 70)
    print("EXPORTING LAYER MAP")
    print("=" * 70)

    tech = get_tech_file()
    output_file = 'demo_outputs/layer_mapping.txt'
    tech.export_layer_map(output_file)

    print(f"✓ Layer mapping exported to: {output_file}")


def verify_roundtrip(original, imported):
    """Verify that export->import round trip preserves structure"""
    print("\n" + "=" * 70)
    print("ROUND-TRIP VERIFICATION")
    print("=" * 70)

    # Count children in original
    original_children = len(original.children)
    imported_children = len(imported.children)

    print(f"Original children: {original_children}")
    print(f"Imported children: {imported_children}")

    if original_children == imported_children:
        print("✓ Child count matches!")
    else:
        print("⚠ Child count differs (expected for GDS round-trip)")

    # Count layers
    def count_layers(cell):
        counts = {}
        for child in cell.children:
            if child.is_leaf:
                counts[child.layer_name] = counts.get(child.layer_name, 0) + 1
        return counts

    orig_layers = count_layers(original)
    imp_layers = count_layers(imported)

    print("\nLayer counts:")
    print(f"  {'Layer':<15} {'Original':<10} {'Imported':<10} {'Match':<10}")
    print("  " + "-" * 50)

    all_layers = set(orig_layers.keys()) | set(imp_layers.keys())
    for layer in sorted(all_layers):
        orig_count = orig_layers.get(layer, 0)
        imp_count = imp_layers.get(layer, 0)
        match = "✓" if orig_count == imp_count else "✗"
        print(f"  {layer:<15} {orig_count:<10} {imp_count:<10} {match:<10}")

    if orig_layers == imp_layers:
        print("\n✓ All layer counts match perfectly!")
    else:
        print("\n⚠ Some layer counts differ")


def main():
    """Main demonstration"""
    print("\n" + "=" * 70)
    print("TECHNOLOGY FILE INTEGRATION DEMO")
    print("=" * 70)
    print("\nThis demo shows:")
    print("  1. Creating a custom technology file")
    print("  2. Applying tech file colors to layouts")
    print("  3. Exporting GDS with tech file layer numbers")
    print("  4. Importing GDS using tech file layer mappings")
    print("  5. Round-trip verification")
    print()

    # Create output directory
    os.makedirs('demo_outputs', exist_ok=True)

    # Step 1: Create and set custom tech file
    tech = create_custom_tech_file()
    set_tech_file(tech)

    # Step 2: Apply tech file colors to style
    apply_tech_colors_to_style(tech)

    # Step 3: Create test layout
    layout = create_test_layout()

    # Step 4: Export GDS with tech file
    gds_file = demo_gds_export_with_tech(layout)

    # Step 5: Export layer mapping
    demo_layer_map_export()

    # Step 6: Import GDS with tech file
    imported = demo_gds_import_with_tech(gds_file)

    # Step 7: Visualize both layouts
    visualize_layouts(layout, imported)

    # Step 8: Verify round-trip
    verify_roundtrip(layout, imported)

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  1. demo_outputs/test_with_techfile.gds - GDS with tech file layer numbers")
    print("  2. demo_outputs/layer_mapping.txt - Layer mapping reference")
    print("  3. demo_outputs/tech_file_roundtrip.png - Visual comparison")
    print("\nKey Features Demonstrated:")
    print("  ✓ Custom technology file creation")
    print("  ✓ Layer name to GDS number mapping")
    print("  ✓ Color definitions from tech file")
    print("  ✓ GDS export with tech file layers")
    print("  ✓ GDS import with tech file layers")
    print("  ✓ Round-trip verification")
    print()


if __name__ == '__main__':
    main()
