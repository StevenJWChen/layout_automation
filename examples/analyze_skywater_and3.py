#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze SkyWater sky130_fd_sc_hd__and3_1 gate to replicate it exactly
"""

import gdstk

print("="*70)
print("Analyzing SkyWater sky130_fd_sc_hd__and3_1 Standard Cell")
print("="*70)

# Import the GDS file
gds_file = 'skywater-pdk-libs-sky130_fd_sc_hd/cells/and3/sky130_fd_sc_hd__and3_1.gds'
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
            layers_used[layer_key] = []
        layers_used[layer_key].append(poly)

    print(f"\n  Layers used:")
    layer_names = {
        (64, 16): 'pwell',
        (64, 20): 'nwell',
        (65, 20): 'diff',
        (66, 20): 'poly',
        (66, 44): 'licon1',
        (67, 16): 'li1 (pin)',
        (67, 20): 'li1',
        (67, 44): 'mcon',
        (68, 16): 'met1 (pin)',
        (68, 20): 'met1',
        (93, 44): 'nsdm',
        (94, 20): 'psdm',
        (95, 20): 'lvtn',
    }

    for (layer, datatype), polys in sorted(layers_used.items()):
        name = layer_names.get((layer, datatype), f'layer {layer}/{datatype}')
        print(f"    {name:30s}: {len(polys):2d} polygons")

    # Get bounding box
    bbox = cell.bounding_box()
    if bbox is not None:
        (x1, y1), (x2, y2) = bbox
        width = x2 - x1
        height = y2 - y1
        print(f"\n  Bounding box: ({x1:.3f}, {y1:.3f}) to ({x2:.3f}, {y2:.3f})")
        print(f"  Cell size: {width:.3f} x {height:.3f} um")

    # Analyze diff regions (transistors)
    print(f"\n  Active regions (diff, layer 65/20):")
    diff_polys = layers_used.get((65, 20), [])
    for i, poly in enumerate(diff_polys):
        bbox = poly.bounding_box()
        if bbox:
            (x1, y1), (x2, y2) = bbox
            w = x2 - x1
            h = y2 - y1
            print(f"    Diff {i}: ({x1:.3f},{y1:.3f}) to ({x2:.3f},{y2:.3f}), size {w:.3f} x {h:.3f} um")

    # Analyze poly gates
    print(f"\n  Poly gates (layer 66/20):")
    poly_gates = layers_used.get((66, 20), [])
    for i, poly in enumerate(poly_gates):
        bbox = poly.bounding_box()
        if bbox:
            (x1, y1), (x2, y2) = bbox
            w = x2 - x1
            h = y2 - y1
            print(f"    Poly {i}: ({x1:.3f},{y1:.3f}) to ({x2:.3f},{y2:.3f}), size {w:.3f} x {h:.3f} um")

    # Analyze contacts
    print(f"\n  Contacts (licon1, layer 66/44):")
    contacts = layers_used.get((66, 44), [])
    print(f"    Total contacts: {len(contacts)}")
    if contacts:
        # Group by size
        sizes = {}
        for poly in contacts:
            bb = poly.bounding_box()
            if bb:
                (x1, y1), (x2, y2) = bb
                w = x2 - x1
                h = y2 - y1
                size_key = (round(w, 3), round(h, 3))
                if size_key not in sizes:
                    sizes[size_key] = 0
                sizes[size_key] += 1
        for (w, h), count in sorted(sizes.items()):
            print(f"      {w:.3f} x {h:.3f} um: {count} contacts")

print("\n" + "="*70)
print("Netlist Analysis")
print("="*70)

# Read the SPICE netlist
spice_file = 'skywater-pdk-libs-sky130_fd_sc_hd/cells/and3/sky130_fd_sc_hd__and3_1.spice'
try:
    with open(spice_file, 'r') as f:
        netlist = f.read()
    print(netlist)

    # Parse transistors
    print("\n" + "="*70)
    print("Transistor Analysis")
    print("="*70)

    lines = netlist.split('\n')
    transistors = []
    for line in lines:
        line = line.strip()
        if line.startswith('MM') or (line.startswith('X') and 'sky130_fd_pr' in line):
            print(f"  {line}")
            # Parse w= and l=
            if 'w=' in line.lower():
                import re
                w_match = re.search(r'w=([0-9.]+)', line, re.IGNORECASE)
                l_match = re.search(r'l=([0-9.]+)', line, re.IGNORECASE)
                m_match = re.search(r'm=([0-9]+)', line, re.IGNORECASE)
                if w_match and l_match:
                    w = float(w_match.group(1))
                    l = float(l_match.group(1))
                    m = int(m_match.group(1)) if m_match else 1
                    device = 'NMOS' if 'nfet' in line.lower() else 'PMOS'
                    transistors.append((device, w, l, m))

    print(f"\n  Summary:")
    for device, w, l, m in transistors:
        print(f"    {device}: W={w}um, L={l}um, M={m}")

    print(f"\n  Total transistors: {len(transistors)}")
    nmos_count = sum(1 for d, _, _, _ in transistors if d == 'NMOS')
    pmos_count = sum(1 for d, _, _, _ in transistors if d == 'PMOS')
    print(f"    NMOS: {nmos_count}")
    print(f"    PMOS: {pmos_count}")

except FileNotFoundError:
    print(f"  Netlist file not found: {spice_file}")

print("\n" + "="*70)
print("Circuit Function")
print("="*70)
print("""
AND3 gate implements: X = A & B & C

Logic implementation (typical):
  - NAND3 stage: intermediate = !(A & B & C)
    - 3 NMOS in series (A, B, C pull down)
    - 3 PMOS in parallel (A, B, C pull up)
  - Inverter stage: X = !intermediate
    - 1 NMOS
    - 1 PMOS

Total: 4 NMOS + 4 PMOS = 8 transistors
""")
