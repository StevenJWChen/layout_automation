#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified CMOS Inverter Layout - using relative constraints only
"""

from layout_automation.gds_cell import Cell, Polygon, CellInstance
import matplotlib.pyplot as plt

# Create simple NMOS transistor
def create_nmos_simple(name='nmos'):
    """Create simplified NMOS transistor layout"""
    nmos = Cell(name)

    # Diffusion (active area)
    diff = Polygon(f'{name}_diff', 'diff')

    # Poly gate
    poly = Polygon(f'{name}_poly', 'poly')

    # Metal1 contacts for source and drain
    m1_s = Polygon(f'{name}_m1_s', 'metal1')
    m1_d = Polygon(f'{name}_m1_d', 'metal1')

    nmos.add_polygon([diff, poly, m1_s, m1_d])

    # Poly is narrower and taller than diff
    nmos.constrain(poly, 'ox2-ox1=sx2-sx1+30', diff)  # diff wider
    nmos.constrain(poly, 'oy2-oy1=sy2-sy1-10', diff)  # poly taller

    # Poly overlaps diff vertically, centered horizontally
    nmos.constrain(poly, 'oy1<sy1, oy2>sy2', diff)  # poly extends beyond diff
    nmos.constrain(poly, 'ox1>sx1, ox2<sx2', diff)  # poly within diff horizontally

    # Center poly over diff
    nmos.constrain(diff, 'sx1+sx2=ox1+ox2', poly)  # centers aligned

    # Source metal on left
    nmos.constrain(diff, 'sx1+2<ox1', m1_s)
    nmos.constrain(poly, 'ox1-3>sx2', m1_s)  # left of poly
    nmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_s)  # within diff height

    # Drain metal on right
    nmos.constrain(poly, 'ox2+3<sx1', m1_d)  # right of poly
    nmos.constrain(diff, 'sx2-2>ox2', m1_d)
    nmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_d)  # within diff height

    return nmos

# Create simple PMOS transistor
def create_pmos_simple(name='pmos'):
    """Create simplified PMOS transistor layout"""
    pmos = Cell(name)

    diff = Polygon(f'{name}_diff', 'diff')
    poly = Polygon(f'{name}_poly', 'poly')
    m1_s = Polygon(f'{name}_m1_s', 'metal1')
    m1_d = Polygon(f'{name}_m1_d', 'metal1')

    pmos.add_polygon([diff, poly, m1_s, m1_d])

    # PMOS similar to NMOS but slightly wider
    pmos.constrain(poly, 'ox2-ox1=sx2-sx1+40', diff)  # diff even wider for PMOS
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

# Create complete inverter
def create_inverter_simple(name='inverter'):
    """Create complete CMOS inverter"""
    inv = Cell(name)

    pmos_cell = create_pmos_simple(f'{name}_pmos')
    nmos_cell = create_nmos_simple(f'{name}_nmos')

    pmos_inst = CellInstance(f'{name}_pmos_inst', pmos_cell)
    nmos_inst = CellInstance(f'{name}_nmos_inst', nmos_cell)

    inv.add_instance([pmos_inst, nmos_inst])

    # Stack PMOS above NMOS
    inv.constrain(nmos_inst, 'sy2+10<oy1', pmos_inst)

    # Align left edges
    inv.constrain(nmos_inst, 'sx1=ox1', pmos_inst)

    return inv

# Test single inverter
print("Creating single inverter...")
inv1 = create_inverter_simple('inv1')

result = inv1.solver()
print(f"Solver result: {result}")

if result:
    print("Single inverter solved successfully!")
    fig = inv1.draw(solve_first=False, show=False)
    plt.savefig('inverter_simple_single.png', dpi=150, bbox_inches='tight')
    print("Saved to inverter_simple_single.png")
    plt.close()
else:
    print("Failed to solve single inverter!")

print("\n" + "="*60 + "\n")

# Test inverter array
print("Creating inverter array (3 inverters)...")
inv_array = Cell('inv_array')

inv_base = create_inverter_simple('inv_base')
inst1 = CellInstance('inv1', inv_base)
inst2 = CellInstance('inv2', inv_base)
inst3 = CellInstance('inv3', inv_base)

inv_array.add_instance([inst1, inst2, inst3])

# Place horizontally
inv_array.constrain(inst1, 'sx2+10<ox1', inst2)
inv_array.constrain(inst2, 'sx2+10<ox1', inst3)

# Align bottom
inv_array.constrain(inst1, 'sy1=oy1', inst2)
inv_array.constrain(inst2, 'sy1=oy1', inst3)

print("Solving inverter array...")
result2 = inv_array.solver()
print(f"Solver result: {result2}")

if result2:
    print("Inverter array solved successfully!")
    fig = inv_array.draw(solve_first=False, show=False)
    plt.savefig('inverter_simple_array.png', dpi=150, bbox_inches='tight')
    print("Saved to inverter_simple_array.png")
    plt.close()

    inv_array.export_gds('inverter_simple_array.gds')
    print("Exported to inverter_simple_array.gds")
    print(f"  inst1: {inst1.pos_list}")
    print(f"  inst2: {inst2.pos_list}")
    print(f"  inst3: {inst3.pos_list}")
else:
    print("Failed to solve inverter array!")

print("\nInverter layout creation complete!")
