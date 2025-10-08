#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIXED CMOS Inverter with correct transistor topology
"""

from gds_cell import Cell, Polygon, CellInstance
import matplotlib.pyplot as plt

def create_nmos_fixed(name='nmos'):
    """Create properly constrained NMOS transistor"""
    nmos = Cell(name)

    # Create layers
    diff = Polygon(f'{name}_diff', 'diff')
    poly = Polygon(f'{name}_poly', 'poly')
    m1_s = Polygon(f'{name}_m1_s', 'metal1')
    m1_d = Polygon(f'{name}_m1_d', 'metal1')

    nmos.add_polygon([diff, poly, m1_s, m1_d])

    # Diffusion is wider than poly (poly crosses it)
    nmos.constrain(diff, 'ox2-ox1=sx2-sx1-6', poly)  # poly is 6 units narrower than diff

    # Poly is taller (extends beyond diff vertically)
    nmos.constrain(diff, 'oy2-oy1=sy2-sy1+6', poly)  # poly 6 units taller

    # Position poly centered over diff
    nmos.constrain(diff, 'sx1+sx2=ox1+ox2', poly)  # horizontally centered
    nmos.constrain(diff, 'sy1+sy2=oy1+oy2', poly)  # vertically centered

    # Source metal: on LEFT side of poly, within diff
    nmos.constrain(diff, 'sx1+1<ox1', m1_s)  # m1_s inside diff left edge
    nmos.constrain(poly, 'ox1-2>sx2', m1_s)  # m1_s left of poly
    nmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_s)  # m1_s within diff vertically

    # Drain metal: on RIGHT side of poly, within diff
    nmos.constrain(poly, 'ox2+2<sx1', m1_d)  # m1_d right of poly
    nmos.constrain(diff, 'sx2-1>ox2', m1_d)  # m1_d inside diff right edge
    nmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_d)  # m1_d within diff vertically

    return nmos

def create_pmos_fixed(name='pmos'):
    """Create properly constrained PMOS transistor (wider than NMOS)"""
    pmos = Cell(name)

    diff = Polygon(f'{name}_diff', 'diff')
    poly = Polygon(f'{name}_poly', 'poly')
    m1_s = Polygon(f'{name}_m1_s', 'metal1')
    m1_d = Polygon(f'{name}_m1_d', 'metal1')

    pmos.add_polygon([diff, poly, m1_s, m1_d])

    # PMOS diffusion wider (bigger device for equal drive strength)
    pmos.constrain(diff, 'ox2-ox1=sx2-sx1-8', poly)  # poly is 8 units narrower
    pmos.constrain(diff, 'oy2-oy1=sy2-sy1+6', poly)  # poly taller

    # Center poly over diff
    pmos.constrain(diff, 'sx1+sx2=ox1+ox2', poly)
    pmos.constrain(diff, 'sy1+sy2=oy1+oy2', poly)

    # Source metal on left
    pmos.constrain(diff, 'sx1+1<ox1', m1_s)
    pmos.constrain(poly, 'ox1-2>sx2', m1_s)
    pmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_s)

    # Drain metal on right
    pmos.constrain(poly, 'ox2+2<sx1', m1_d)
    pmos.constrain(diff, 'sx2-1>ox2', m1_d)
    pmos.constrain(diff, 'sy1+2<oy1, sy2-2>oy2', m1_d)

    return pmos

def create_inverter_fixed(name='inv'):
    """Create complete inverter with fixed transistors"""
    inv = Cell(name)

    pmos_cell = create_pmos_fixed(f'{name}_pmos')
    nmos_cell = create_nmos_fixed(f'{name}_nmos')

    pmos_inst = CellInstance(f'{name}_pmos_inst', pmos_cell)
    nmos_inst = CellInstance(f'{name}_nmos_inst', nmos_cell)

    inv.add_instance([pmos_inst, nmos_inst])

    # Stack PMOS above NMOS with spacing
    inv.constrain(nmos_inst, 'sy2+10<oy1', pmos_inst)

    # Align centers horizontally (poly gates aligned for input)
    inv.constrain(nmos_inst, 'sx1+sx2=ox1+ox2', pmos_inst)

    return inv

# Test and visualize
print("Creating FIXED inverter with correct topology...")
inv = create_inverter_fixed('inv_fixed')

result = inv.solver()
print(f"Solver result: {result}")

if result:
    print("\n=== Checking NMOS geometry ===")
    nmos_inst = [i for i in inv.instances if 'nmos' in i.name][0]
    for p in nmos_inst.cell.polygons:
        x1, y1, x2, y2 = p.pos_list
        print(f'{p.name:20s} ({p.layer:8s}): x=[{x1:.1f}, {x2:.1f}] y=[{y1:.1f}, {y2:.1f}] w={x2-x1:.1f} h={y2-y1:.1f}')

    # Verify metal contacts are within diffusion
    diff = [p for p in nmos_inst.cell.polygons if p.layer == 'diff'][0]
    metals = [p for p in nmos_inst.cell.polygons if p.layer == 'metal1']

    print(f"\nDiffusion bounds: x=[{diff.pos_list[0]:.1f}, {diff.pos_list[2]:.1f}]")
    for m in metals:
        inside_x = diff.pos_list[0] <= m.pos_list[0] and m.pos_list[2] <= diff.pos_list[2]
        status = "✓ INSIDE" if inside_x else "✗ OUTSIDE"
        print(f"  {m.name}: x=[{m.pos_list[0]:.1f}, {m.pos_list[2]:.1f}] {status}")

    print("\n=== Checking PMOS geometry ===")
    pmos_inst = [i for i in inv.instances if 'pmos' in i.name][0]
    for p in pmos_inst.cell.polygons:
        x1, y1, x2, y2 = p.pos_list
        print(f'{p.name:20s} ({p.layer:8s}): x=[{x1:.1f}, {x2:.1f}] y=[{y1:.1f}, {y2:.1f}] w={x2-x1:.1f} h={y2-y1:.1f}')

    diff = [p for p in pmos_inst.cell.polygons if p.layer == 'diff'][0]
    metals = [p for p in pmos_inst.cell.polygons if p.layer == 'metal1']

    print(f"\nDiffusion bounds: x=[{diff.pos_list[0]:.1f}, {diff.pos_list[2]:.1f}]")
    for m in metals:
        inside_x = diff.pos_list[0] <= m.pos_list[0] and m.pos_list[2] <= diff.pos_list[2]
        status = "✓ INSIDE" if inside_x else "✗ OUTSIDE"
        print(f"  {m.name}: x=[{m.pos_list[0]:.1f}, {m.pos_list[2]:.1f}] {status}")

    # Draw
    fig = inv.draw(solve_first=False, show=False)
    plt.savefig('inverter_fixed_single.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved to inverter_fixed_single.png")
    plt.close()

    # Create array
    print("\nCreating array...")
    array = Cell('inv_array_fixed')
    inv_base = create_inverter_fixed('inv_base')

    i1 = CellInstance('i1', inv_base)
    i2 = CellInstance('i2', inv_base)
    i3 = CellInstance('i3', inv_base)

    array.add_instance([i1, i2, i3])

    array.constrain(i1, 'sx2+15<ox1', i2)
    array.constrain(i2, 'sx2+15<ox1', i3)
    array.constrain(i1, 'sy1=oy1', i2)
    array.constrain(i2, 'sy1=oy1', i3)

    if array.solver():
        fig = array.draw(solve_first=False, show=False)
        plt.savefig('inverter_fixed_array.png', dpi=150, bbox_inches='tight')
        print("✓ Saved to inverter_fixed_array.png")

        array.export_gds('inverter_fixed_array.gds')
        print("✓ Exported to inverter_fixed_array.gds")
    else:
        print("✗ Array failed")
else:
    print("✗ Solver failed")
