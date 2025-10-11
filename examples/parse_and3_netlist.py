#!/usr/bin/env python3
"""Parse AND3 netlist correctly"""

import re

spice_file = 'skywater-pdk-libs-sky130_fd_sc_hd/cells/and3/sky130_fd_sc_hd__and3_1.spice'

with open(spice_file, 'r') as f:
    netlist = f.read()

print("="*70)
print("AND3 Transistor List (Corrected)")
print("="*70)

lines = netlist.split('\n')
transistors = []
for line in lines:
    line = line.strip()
    if line.startswith('X') and 'sky130_fd_pr' in line:
        # Parse: X0 drain gate source bulk device w=XXXu l=YYYu
        parts = line.split()

        # Get W and L with proper unit handling
        w_str = [p for p in parts if p.startswith('w=')][0] if any(p.startswith('w=') for p in parts) else None
        l_str = [p for p in parts if p.startswith('l=')][0] if any(p.startswith('l=') for p in parts) else None

        if w_str and l_str:
            # Parse w=420000u -> 0.42 (um)
            w_match = re.match(r'w=([0-9.e+-]+)u?', w_str)
            l_match = re.match(r'l=([0-9.e+-]+)u?', l_str)

            if w_match and l_match:
                w_val = float(w_match.group(1))
                l_val = float(l_match.group(1))

                # Convert from database units (um) to actual microns
                # In SPICE, 420000u means 420000 * 1e-6 = 0.42um
                if w_val > 100:  # Likely in nm or DBU
                    w_val = w_val / 1e6  # Convert to um
                if l_val > 100:
                    l_val = l_val / 1e6

                device = 'NMOS' if 'nfet' in line else 'PMOS'

                # Get node names
                nodes = parts[1:5]  # drain, gate, source, bulk

                transistors.append({
                    'name': parts[0],
                    'device': device,
                    'drain': nodes[0] if len(nodes) > 0 else '?',
                    'gate': nodes[1] if len(nodes) > 1 else '?',
                    'source': nodes[2] if len(nodes) > 2 else '?',
                    'bulk': nodes[3] if len(nodes) > 3 else '?',
                    'w': w_val,
                    'l': l_val
                })

print(f"\n{'Name':<6} {'Type':<6} {'W(um)':<8} {'L(um)':<8} {'Gate':<12} {'Drain':<12} {'Source':<8}")
print("-" * 70)
for t in transistors:
    print(f"{t['name']:<6} {t['device']:<6} {t['w']:<8.3f} {t['l']:<8.3f} {t['gate']:<12} {t['drain']:<12} {t['source']:<8}")

print(f"\n{'='*70}")
print("Circuit Structure")
print("="*70)

# Identify NAND3 stage
nand_nmos = [t for t in transistors if t['device'] == 'NMOS' and t['gate'] in ['A', 'B', 'C']]
nand_pmos = [t for t in transistors if t['device'] == 'PMOS' and t['gate'] in ['A', 'B', 'C']]

# Identify inverter stage
inv_nmos = [t for t in transistors if t['device'] == 'NMOS' and t['drain'] == 'X']
inv_pmos = [t for t in transistors if t['device'] == 'PMOS' and t['drain'] == 'X']

print(f"\nNAND3 Stage (inputs A, B, C):")
print(f"  NMOS (series stack):")
for t in nand_nmos:
    print(f"    {t['name']}: Gate={t['gate']}, W={t['w']:.2f}um")
print(f"  PMOS (parallel):")
for t in nand_pmos:
    print(f"    {t['name']}: Gate={t['gate']}, W={t['w']:.2f}um")

print(f"\nInverter Stage (a_27_47# → X):")
if inv_nmos:
    for t in inv_nmos:
        print(f"  NMOS: {t['name']}, W={t['w']:.2f}um")
if inv_pmos:
    for t in inv_pmos:
        print(f"  PMOS: {t['name']}, W={t['w']:.2f}um")

print(f"\n{'='*70}")
print("Transistor Sizing Summary")
print("="*70)

# Group by width
nmos_widths = {}
pmos_widths = {}
for t in transistors:
    w = round(t['w'], 2)
    if t['device'] == 'NMOS':
        nmos_widths[w] = nmos_widths.get(w, 0) + 1
    else:
        pmos_widths[w] = pmos_widths.get(w, 0) + 1

print(f"\nNMOS:")
for w in sorted(nmos_widths.keys()):
    print(f"  W={w:.2f}um, L=0.15um: {nmos_widths[w]} transistors")

print(f"\nPMOS:")
for w in sorted(pmos_widths.keys()):
    print(f"  W={w:.2f}um, L=0.15um: {pmos_widths[w]} transistors")
