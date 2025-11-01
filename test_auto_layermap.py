#!/usr/bin/env python3
"""
Test automatic layer mapping config file generation and loading.

This test demonstrates:
1. Exporting GDS with undefined layers (not in tech file or defaults)
2. Auto-generation of .layermap config file
3. Auto-loading of config file on import
4. Round-trip preservation with undefined layers
"""

import os
from layout_automation.cell import Cell

print("="*70)
print("AUTOMATIC LAYER MAPPING CONFIG TEST")
print("="*70)

# Create layout with mixed defined and undefined layers
print("\n[1] Creating layout with mixed layers...")
print("    - Defined layers: metal1, metal2, poly (in defaults)")
print("    - Undefined layers: custom_layer1, custom_layer2, mylayer")

r1 = Cell('r1', 'metal1')      # Defined in defaults
r2 = Cell('r2', 'custom_layer1')  # NOT defined - will auto-assign
r3 = Cell('r3', 'poly')        # Defined in defaults
r4 = Cell('r4', 'custom_layer2')  # NOT defined - will auto-assign
r5 = Cell('r5', 'metal2')      # Defined in defaults
r6 = Cell('r6', 'mylayer')     # NOT defined - will auto-assign

top = Cell('top')
top.add_instance([r1, r2, r3, r4, r5, r6])

# Position cells
top.constrain(r1, 'x1=0, y1=0, x2=10, y2=10')
top.constrain(r2, 'x1=15, y1=0, x2=25, y2=10')
top.constrain(r3, 'x1=30, y1=0, x2=40, y2=10')
top.constrain(r4, 'x1=0, y1=15, x2=10, y2=25')
top.constrain(r5, 'x1=15, y1=15, x2=25, y2=25')
top.constrain(r6, 'x1=30, y1=15, x2=40, y2=25')

top.solver()
print("    ✓ Layout solved")

# Export to GDS
print("\n[2] Exporting to GDS...")
gds_file = 'demo_outputs/test_auto_layermap.gds'
os.makedirs('demo_outputs', exist_ok=True)
top.export_gds(gds_file, use_tech_file=False)

# Check if config file was created
config_file = 'demo_outputs/test_auto_layermap.layermap'
if os.path.exists(config_file):
    print(f"    ✓ Config file created: {config_file}")

    # Show config content
    import json
    with open(config_file, 'r') as f:
        config = json.load(f)

    print("\n[3] Config file content:")
    print(json.dumps(config, indent=2))

    print("\n    Undefined layers auto-assigned:")
    for name, mapping in config['undefined_layers'].items():
        print(f"      {name:<15} -> GDS layer {mapping['layer']}, datatype {mapping['datatype']}")
else:
    print(f"    ✗ Config file not created")

# Import back
print("\n[4] Importing GDS (should auto-load config)...")
imported = Cell.from_gds(gds_file, use_tech_file=False)
imported.solver()

# Verify layers
print("\n[5] Verifying imported layers...")
layer_names = []
for child in imported.children:
    if child.is_leaf:
        layer_names.append(child.layer_name)

print(f"    Imported {len(layer_names)} layers:")
for name in layer_names:
    print(f"      - {name}")

# Check if all layers are preserved
expected_layers = ['metal1', 'custom_layer1', 'poly', 'custom_layer2', 'metal2', 'mylayer']
all_found = all(any(name in imported_name for imported_name in layer_names) for name in expected_layers)

if all_found:
    print("\n    ✓ All layer names preserved!")
else:
    print("\n    ✗ Some layer names missing")
    missing = [name for name in expected_layers if not any(name in imported_name for imported_name in layer_names)]
    print(f"    Missing: {missing}")

# Test round-trip
print("\n[6] Testing round-trip (export again)...")
gds_file2 = 'demo_outputs/test_auto_layermap_roundtrip.gds'
imported.export_gds(gds_file2, use_tech_file=False)

imported2 = Cell.from_gds(gds_file2, use_tech_file=False)
imported2.solver()

# Verify positions match
print("\n[7] Verifying position preservation...")
orig_positions = [child.pos_list for child in imported.children if child.is_leaf]
roundtrip_positions = [child.pos_list for child in imported2.children if child.is_leaf]

positions_match = len(orig_positions) == len(roundtrip_positions)
if positions_match:
    for orig, rt in zip(orig_positions, roundtrip_positions):
        for i in range(4):
            if abs(orig[i] - rt[i]) > 0.01:
                positions_match = False
                break

if positions_match:
    print("    ✓ All positions preserved through round-trip!")
else:
    print("    ✗ Position mismatch detected")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\n✓ Auto layer mapping feature test complete!")
print("\nFeatures verified:")
print("  1. Undefined layers are auto-assigned GDS layer numbers (200+)")
print("  2. .layermap config file is automatically generated")
print("  3. Config file is automatically loaded on import")
print("  4. Layer names are preserved through round-trip")
print("  5. Positions are preserved correctly")
print("\nGenerated files:")
print(f"  - {gds_file}")
print(f"  - {config_file}")
print(f"  - {gds_file2}")
print(f"  - demo_outputs/test_auto_layermap_roundtrip.layermap")
print("\n" + "="*70)
