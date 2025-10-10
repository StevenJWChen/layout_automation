#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze SkyWater inverter standard cell and try to replicate with our tool
"""

import gdstk
from gds_cell import Cell

print("="*70)
print("Analyzing SkyWater sky130_fd_sc_hd__inv_1 Standard Cell")
print("="*70)

# Import the GDS file
gds_file = 'skywater-pdk-libs-sky130_fd_sc_hd/cells/inv/sky130_fd_sc_hd__inv_1.gds'
lib = gdstk.read_gds(gds_file)

print(f"\nGDS File: {gds_file}")
print(f"Number of cells: {len(lib.cells)}")

for cell in lib.cells:
    print(f"\nCell: {cell.name}")
    print(f"  Polygons: {len(cell.polygons)}")
    print(f"  References: {len(cell.references)}")

    # Analyze layers
    layers_used = {}
    for poly in cell.polygons:
        layer_key = (poly.layer, poly.datatype)
        if layer_key not in layers_used:
            layers_used[layer_key] = 0
        layers_used[layer_key] += 1

    print(f"\n  Layers used:")
    for (layer, datatype), count in sorted(layers_used.items()):
        print(f"    Layer {layer}, Datatype {datatype}: {count} polygons")

    # Get bounding box
    bbox = cell.bounding_box()
    if bbox is not None:
        (x1, y1), (x2, y2) = bbox
        width = x2 - x1
        height = y2 - y1
        print(f"\n  Bounding box: ({x1:.3f}, {y1:.3f}) to ({x2:.3f}, {y2:.3f})")
        print(f"  Cell size: {width:.3f} x {height:.3f} um")

    # Sample some polygon coordinates
    print(f"\n  Sample polygon coordinates (first 5):")
    for i, poly in enumerate(cell.polygons[:5]):
        bbox = poly.bounding_box()
        if bbox:
            (px1, py1), (px2, py2) = bbox
            print(f"    Poly {i}: Layer {poly.layer}, Box: ({px1:.3f},{py1:.3f}) to ({px2:.3f},{py2:.3f})")

print("\n" + "="*70)
print("Netlist Analysis")
print("="*70)

netlist = """
.SUBCKT sky130_fd_sc_hd__inv_1 A VGND VNB VPB VPWR Y
MMIN1 Y A VGND VNB nfet_01v8 m=1 w=0.65 l=0.15
MMIP1 Y A VPWR VPB pfet_01v8_hvt m=1 w=1.0 l=0.15
.ENDS
"""

print(netlist)
print("Components:")
print("  NMOS: W=0.65um, L=0.15um (drain=Y, gate=A, source=VGND)")
print("  PMOS: W=1.0um, L=0.15um (drain=Y, gate=A, source=VPWR)")
print("\nTopology:")
print("  Input A connects to both gates")
print("  Output Y connects to both drains")
print("  NMOS source to VGND (ground)")
print("  PMOS source to VPWR (power)")

print("\n" + "="*70)
print("Layer Mapping (SkyWater SKY130)")
print("="*70)

layer_map = {
    64: "pwell",
    65: "nsdm (N+ source/drain implant)",
    66: "psdm (P+ source/drain implant)",
    67: "li1 (local interconnect)",
    68: "mcon (metal contact)",
    69: "met1 (metal 1)",
    70: "via (via 1)",
    71: "met2 (metal 2)",
    94: "nwell",
    122: "licon1 (local interconnect contact)",
    # Common layers
    0: "boundary",
    63: "capm (capacitor)",
    235: "poly (polysilicon)",
}

print("\nCommon SkyWater layers:")
for layer, name in sorted(layer_map.items()):
    print(f"  Layer {layer}: {name}")

print("\n" + "="*70)
print("Key Observations for Our Tool")
print("="*70)

observations = """
1. COORDINATES ARE IN MICRONS (not integers!)
   - Layout uses floating point: 0.265, 0.15, etc.
   - Need to support micron precision
   - Can scale to nm and use integers: 265nm, 150nm

2. MANY LAYERS (20-30 polygons)
   - Not just metal/poly/diff
   - Implants: nsdm, psdm
   - Wells: nwell, pwell
   - Contacts: licon, mcon, via
   - Our tool needs layer stack definition

3. COMPLEX SHAPES
   - Not simple rectangles
   - Some polygons have 6-8 vertices
   - Our tool only supports rectangles currently

4. TRANSISTOR STRUCTURE
   - Gates are vertical poly strips
   - Active regions (diff) horizontal
   - Contacts placed on active
   - Metal routing on top

5. STANDARDIZED DIMENSIONS
   - Height: ~2.72um (standard cell height)
   - Width varies by drive strength
   - inv_1 is narrowest, inv_16 is widest

WHAT WE NEED TO ADD:
✓ Micron/nanometer units (not just unitless integers)
✓ Layer stack with proper names
✓ Contact/via support
✓ Non-rectangular polygon support (for advanced shapes)
✓ Technology file (layer definitions)
✓ Transistor primitive (MOSFET with W/L parameters)
"""

print(observations)

print("\n" + "="*70)
print("Can We Replicate This with Current Tool?")
print("="*70)

print("""
PARTIAL YES (with limitations):

✓ Can create hierarchical layout
✓ Can position rectangles with constraints
✓ Can export to GDS
✓ Can handle multiple layers

✗ Cannot replicate exactly because:
  - Need non-rectangular polygons
  - Need implant/well layers
  - Need contact/via generation
  - Need micron-based coordinates
  - Need transistor primitives

NEXT STEPS TO ENABLE:
1. Add unit support (micron/nanometer)
2. Add layer stack from tech file
3. Add contact/via generator
4. Add MOSFET primitive class
5. Add polygon support (not just rectangles)
""")
