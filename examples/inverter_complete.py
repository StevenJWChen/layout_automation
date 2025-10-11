#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete CMOS Inverter with all connections
"""

from layout_automation.gds_cell import Cell, Polygon, CellInstance
import matplotlib.pyplot as plt

def create_nmos(name='nmos'):
    """Create NMOS transistor"""
    nmos = Cell(name)

    diff = Polygon(f'{name}_diff', 'diff')
    poly = Polygon(f'{name}_poly', 'poly')
    m1_s = Polygon(f'{name}_m1_s', 'metal1')
    m1_d = Polygon(f'{name}_m1_d', 'metal1')

    nmos.add_polygon([diff, poly, m1_s, m1_d])

    # Sizes through relative constraints
    nmos.constrain(poly, 'ox2-ox1=sx2-sx1+30', diff)
    nmos.constrain(poly, 'oy2-oy1=sy2-sy1-10', diff)
    nmos.constrain(poly, 'oy1<sy1, oy2>sy2', diff)
    nmos.constrain(poly, 'ox1>sx1, ox2<sx2', diff)
    nmos.constrain(diff, 'sx1+sx2=ox1+ox2', poly)

    nmos.constrain(diff, 'sx1+2<ox1', m1_s)
    nmos.constrain(poly, 'ox1-3>sx2', m1_s)
    nmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_s)

    nmos.constrain(poly, 'ox2+3<sx1', m1_d)
    nmos.constrain(diff, 'sx2-2>ox2', m1_d)
    nmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_d)

    return nmos

def create_pmos(name='pmos'):
    """Create PMOS transistor"""
    pmos = Cell(name)

    diff = Polygon(f'{name}_diff', 'diff')
    poly = Polygon(f'{name}_poly', 'poly')
    m1_s = Polygon(f'{name}_m1_s', 'metal1')
    m1_d = Polygon(f'{name}_m1_d', 'metal1')

    pmos.add_polygon([diff, poly, m1_s, m1_d])

    pmos.constrain(poly, 'ox2-ox1=sx2-sx1+40', diff)
    pmos.constrain(poly, 'oy2-oy1=sy2-sy1-10', diff)
    pmos.constrain(poly, 'oy1<sy1, oy2>sy2', diff)
    pmos.constrain(poly, 'ox1>sx1, ox2<sx2', diff)
    pmos.constrain(diff, 'sx1+sx2=ox1+ox2', poly)

    pmos.constrain(diff, 'sx1+2<ox1', m1_s)
    pmos.constrain(poly, 'ox1-3>sx2', m1_s)
    pmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_s)

    pmos.constrain(poly, 'ox2+3<sx1', m1_d)
    pmos.constrain(diff, 'sx2-2>ox2', m1_d)
    pmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_d)

    return pmos

def create_complete_inverter(name='inv'):
    """Create complete inverter with all routing"""
    inv = Cell(name)

    # Create transistors
    pmos_cell = create_pmos(f'{name}_pmos')
    nmos_cell = create_nmos(f'{name}_nmos')

    pmos_inst = CellInstance(f'{name}_pmos_inst', pmos_cell)
    nmos_inst = CellInstance(f'{name}_nmos_inst', nmos_cell)

    inv.add_instance([pmos_inst, nmos_inst])

    # Stack vertically
    inv.constrain(nmos_inst, 'sy2+15<oy1', pmos_inst)
    inv.constrain(nmos_inst, 'sx1=ox1', pmos_inst)

    # Add routing layers at top level
    # Input poly strap (metal2 vertical)
    input_m2 = Polygon(f'{name}_input', 'metal2')
    inv.add_polygon(input_m2)

    # Output metal strap (metal2 vertical)
    output_m2 = Polygon(f'{name}_output', 'metal2')
    inv.add_polygon(output_m2)

    # VDD rail (metal3 horizontal)
    vdd = Polygon(f'{name}_vdd', 'metal3')
    inv.add_polygon(vdd)

    # GND rail (metal3 horizontal)
    gnd = Polygon(f'{name}_gnd', 'metal3')
    inv.add_polygon(gnd)

    # Position input metal2 vertically connecting both gates
    inv.constrain(nmos_inst, 'sx1+sx2=ox1+ox2', input_m2)  # Centered on gates
    inv.constrain(input_m2, 'ox2-ox1<10', input_m2)  # Narrow vertical strap
    inv.constrain(nmos_inst, 'sy1-2<oy1', input_m2)
    inv.constrain(pmos_inst, 'sy2+2>oy2', input_m2)

    # Position output metal2 on drain side
    inv.constrain(nmos_inst, 'sx2-5=ox1', output_m2)
    inv.constrain(output_m2, 'ox2-ox1<10', output_m2)
    inv.constrain(nmos_inst, 'sy1-2<oy1', output_m2)
    inv.constrain(pmos_inst, 'sy2+2>oy2', output_m2)

    # VDD rail above PMOS
    inv.constrain(pmos_inst, 'sx1-5<ox1', vdd)
    inv.constrain(pmos_inst, 'sx2+5>ox2', vdd)
    inv.constrain(vdd, 'oy2-oy1<6', vdd)  # Thin rail
    inv.constrain(pmos_inst, 'sy2+3<oy1', vdd)

    # GND rail below NMOS
    inv.constrain(nmos_inst, 'sx1-5<ox1', gnd)
    inv.constrain(nmos_inst, 'sx2+5>ox2', gnd)
    inv.constrain(gnd, 'oy2-oy1<6', gnd)  # Thin rail
    inv.constrain(nmos_inst, 'sy1-9>oy2', gnd)

    return inv

# Create and solve
print("Creating complete inverter with all routing...")
inv = create_complete_inverter('inv_complete')

result = inv.solver()
print(f"Solver result: {result}")

if result:
    print("✓ Complete inverter solved!")
    print(f"  Polygons in top cell: {len(inv.polygons)}")
    for p in inv.polygons:
        print(f"    - {p.name} ({p.layer})")

    fig = inv.draw(solve_first=False, show=False)
    plt.savefig('inverter_complete.png', dpi=150, bbox_inches='tight')
    print("Saved to inverter_complete.png")
    plt.close()

    # Create array
    print("\nCreating array of complete inverters...")
    array = Cell('inv_array')
    inv_base = create_complete_inverter('inv_base')

    i1 = CellInstance('i1', inv_base)
    i2 = CellInstance('i2', inv_base)
    i3 = CellInstance('i3', inv_base)

    array.add_instance([i1, i2, i3])

    array.constrain(i1, 'sx2+20<ox1', i2)
    array.constrain(i2, 'sx2+20<ox1', i3)
    array.constrain(i1, 'sy1=oy1', i2)
    array.constrain(i2, 'sy1=oy1', i3)

    result2 = array.solver()
    print(f"Array solver result: {result2}")

    if result2:
        print("✓ Array solved!")
        fig = array.draw(solve_first=False, show=False)
        plt.savefig('inverter_complete_array.png', dpi=150, bbox_inches='tight')
        print("Saved to inverter_complete_array.png")

        array.export_gds('inverter_complete_array.gds')
        print("Exported to GDS")
    else:
        print("✗ Array failed")
else:
    print("✗ Failed to solve inverter")
