#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CMOS Inverter Layout Design
Creates a complete inverter with PMOS and NMOS transistors
"""

from gds_cell import Cell, Polygon, CellInstance
import matplotlib.pyplot as plt

# Create NMOS transistor cell
def create_nmos(name='nmos'):
    """Create NMOS transistor layout"""
    nmos = Cell(name)

    # Diffusion (active area)
    diff = Polygon(f'{name}_diff', 'diff')

    # Poly gate (crosses diffusion)
    poly = Polygon(f'{name}_poly', 'poly')

    # Metal1 contacts for source and drain
    m1_source = Polygon(f'{name}_m1_s', 'metal1')
    m1_drain = Polygon(f'{name}_m1_d', 'metal1')

    nmos.add_polygon([diff, poly, m1_source, m1_drain])

    # Diffusion dimensions: width=40, height=20
    nmos.constrain(diff, 'sx2-sx1=40, sy2-sy1=20', diff)

    # Poly crosses diffusion vertically, width=4
    nmos.constrain(poly, 'sx2-sx1=4, sy2-sy1=30', poly)

    # Poly centered over diffusion
    nmos.constrain(diff, 'sx1+18=ox1', poly)  # centered horizontally
    nmos.constrain(diff, 'sy1-5=oy1', poly)   # extends beyond diffusion

    # Source metal1 on left side of poly
    nmos.constrain(m1_source, 'sx2-sx1=10, sy2-sy1=10', m1_source)
    nmos.constrain(diff, 'sx1+5=ox1', m1_source)
    nmos.constrain(diff, 'sy1+5=oy1', m1_source)

    # Drain metal1 on right side of poly
    nmos.constrain(m1_drain, 'sx2-sx1=10, sy2-sy1=10', m1_drain)
    nmos.constrain(diff, 'sx2-15=ox1', m1_drain)
    nmos.constrain(diff, 'sy1+5=oy1', m1_drain)

    return nmos

# Create PMOS transistor cell
def create_pmos(name='pmos'):
    """Create PMOS transistor layout (similar to NMOS but slightly larger)"""
    pmos = Cell(name)

    # Diffusion (active area)
    diff = Polygon(f'{name}_diff', 'diff')

    # Poly gate
    poly = Polygon(f'{name}_poly', 'poly')

    # Metal1 contacts
    m1_source = Polygon(f'{name}_m1_s', 'metal1')
    m1_drain = Polygon(f'{name}_m1_d', 'metal1')

    pmos.add_polygon([diff, poly, m1_source, m1_drain])

    # PMOS is typically wider for equal drive strength
    # Diffusion dimensions: width=60, height=20
    pmos.constrain(diff, 'sx2-sx1=60, sy2-sy1=20', diff)

    # Poly crosses diffusion, width=4
    pmos.constrain(poly, 'sx2-sx1=4, sy2-sy1=30', poly)

    # Poly centered over diffusion
    pmos.constrain(diff, 'sx1+28=ox1', poly)
    pmos.constrain(diff, 'sy1-5=oy1', poly)

    # Source metal1
    pmos.constrain(m1_source, 'sx2-sx1=12, sy2-sy1=10', m1_source)
    pmos.constrain(diff, 'sx1+5=ox1', m1_source)
    pmos.constrain(diff, 'sy1+5=oy1', m1_source)

    # Drain metal1
    pmos.constrain(m1_drain, 'sx2-sx1=12, sy2-sy1=10', m1_drain)
    pmos.constrain(diff, 'sx2-17=ox1', m1_drain)
    pmos.constrain(diff, 'sy1+5=oy1', m1_drain)

    return pmos

# Create complete inverter
def create_inverter(name='inverter'):
    """Create complete CMOS inverter (PMOS on top, NMOS on bottom)"""
    inv = Cell(name)

    # Create transistor cells
    pmos_cell = create_pmos(f'{name}_pmos')
    nmos_cell = create_nmos(f'{name}_nmos')

    # Create instances
    pmos_inst = CellInstance(f'{name}_pmos_inst', pmos_cell)
    nmos_inst = CellInstance(f'{name}_nmos_inst', nmos_cell)

    inv.add_instance([pmos_inst, nmos_inst])

    # Stack PMOS above NMOS with spacing
    inv.constrain(nmos_inst, 'sy2+20<oy1', pmos_inst)

    # Align left edges
    inv.constrain(nmos_inst, 'sx1=ox1', pmos_inst)

    # Add input poly connection (metal2)
    input_metal = Polygon(f'{name}_input', 'metal2')
    inv.add_polygon(input_metal)

    # Input metal dimensions
    inv.constrain(input_metal, 'sx2-sx1=8, sy2-sy1=60', input_metal)

    # Position input metal between transistors
    inv.constrain(nmos_inst, 'sx1+18=ox1', input_metal)
    inv.constrain(nmos_inst, 'sy1=oy1', input_metal)

    # Add output connection (metal2)
    output_metal = Polygon(f'{name}_output', 'metal2')
    inv.add_polygon(output_metal)

    # Output metal dimensions
    inv.constrain(output_metal, 'sx2-sx1=10, sy2-sy1=60', output_metal)

    # Position output metal at drain
    inv.constrain(nmos_inst, 'sx2-10=ox1', output_metal)
    inv.constrain(nmos_inst, 'sy1=oy1', output_metal)

    # Add VDD rail (metal3)
    vdd_rail = Polygon(f'{name}_vdd', 'metal3')
    inv.add_polygon(vdd_rail)
    inv.constrain(vdd_rail, 'sx2-sx1=70, sy2-sy1=6', vdd_rail)
    inv.constrain(pmos_inst, 'sx1-5=ox1', vdd_rail)
    inv.constrain(pmos_inst, 'sy2+5=oy1', vdd_rail)

    # Add GND rail (metal3)
    gnd_rail = Polygon(f'{name}_gnd', 'metal3')
    inv.add_polygon(gnd_rail)
    inv.constrain(gnd_rail, 'sx2-sx1=70, sy2-sy1=6', gnd_rail)
    inv.constrain(nmos_inst, 'sx1-5=ox1', gnd_rail)
    inv.constrain(nmos_inst, 'sy1-11=oy1', gnd_rail)

    return inv

# Test: Create single inverter
print("Creating single inverter...")
inv1 = create_inverter('inv1')

result = inv1.solver()
print(f"Solver result: {result}")

if result:
    print("Single inverter layout solved successfully!")
    fig = inv1.draw(solve_first=False, show=False)
    plt.savefig('inverter_single.png', dpi=150, bbox_inches='tight')
    print("Saved to inverter_single.png")
    plt.close()
else:
    print("Failed to solve single inverter!")

print("\n" + "="*60 + "\n")

# Test: Create inverter array
print("Creating inverter array (3 inverters)...")
inv_array = Cell('inv_array')

# Create 3 inverter instances
inv_cell = create_inverter('inv_base')
inst1 = CellInstance('inv_inst1', inv_cell)
inst2 = CellInstance('inv_inst2', inv_cell)
inst3 = CellInstance('inv_inst3', inv_cell)

inv_array.add_instance([inst1, inst2, inst3])

# Place them horizontally with spacing
inv_array.constrain(inst1, 'sx2+15<ox1', inst2)
inv_array.constrain(inst2, 'sx2+15<ox1', inst3)

# Align bottom edges
inv_array.constrain(inst1, 'sy1=oy1', inst2)
inv_array.constrain(inst2, 'sy1=oy1', inst3)

print("Solving inverter array...")
result2 = inv_array.solver()
print(f"Solver result: {result2}")

if result2:
    print("Inverter array solved successfully!")
    print(f"  inst1 position: {inst1.pos_list}")
    print(f"  inst2 position: {inst2.pos_list}")
    print(f"  inst3 position: {inst3.pos_list}")

    fig = inv_array.draw(solve_first=False, show=False)
    plt.savefig('inverter_array.png', dpi=150, bbox_inches='tight')
    print("Saved to inverter_array.png")
    plt.close()

    # Export to GDS
    inv_array.export_gds('inverter_array.gds')
    print("Exported to inverter_array.gds")
else:
    print("Failed to solve inverter array!")

print("\n" + "="*60 + "\n")

# Test: Create 2D array
print("Creating 2D inverter array (2x3 grid)...")
inv_2d = Cell('inv_2d_array')

# Create 2 rows of 3 inverters each
inv_base2 = create_inverter('inv_2d_base')

row1 = []
row2 = []

for i in range(3):
    row1.append(CellInstance(f'inv_r1_c{i+1}', inv_base2))
    row2.append(CellInstance(f'inv_r2_c{i+1}', inv_base2))

inv_2d.add_instance(row1 + row2)

# Arrange row 1 horizontally
inv_2d.constrain(row1[0], 'sx2+15<ox1', row1[1])
inv_2d.constrain(row1[1], 'sx2+15<ox1', row1[2])
inv_2d.constrain(row1[0], 'sy1=oy1', row1[1])
inv_2d.constrain(row1[1], 'sy1=oy1', row1[2])

# Arrange row 2 horizontally
inv_2d.constrain(row2[0], 'sx2+15<ox1', row2[1])
inv_2d.constrain(row2[1], 'sx2+15<ox1', row2[2])
inv_2d.constrain(row2[0], 'sy1=oy1', row2[1])
inv_2d.constrain(row2[1], 'sy1=oy1', row2[2])

# Stack row2 below row1
inv_2d.constrain(row1[0], 'sy1-25>oy2', row2[0])

# Align columns
inv_2d.constrain(row1[0], 'sx1=ox1', row2[0])

print("Solving 2D inverter array...")
result3 = inv_2d.solver()
print(f"Solver result: {result3}")

if result3:
    print("2D inverter array solved successfully!")
    fig = inv_2d.draw(solve_first=False, show=False)
    plt.savefig('inverter_2d_array.png', dpi=150, bbox_inches='tight')
    print("Saved to inverter_2d_array.png")
    plt.close()

    inv_2d.export_gds('inverter_2d_array.gds')
    print("Exported to inverter_2d_array.gds")
else:
    print("Failed to solve 2D array!")

print("\nAll inverter layouts created successfully!")
