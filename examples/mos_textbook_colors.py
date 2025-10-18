"""
MOS Transistor and Array with Textbook-Standard Colors

Standard textbook colors for CMOS:
- N-well: Light green (for PMOS)
- P-well/Substrate: Light pink/salmon (for NMOS)
- Poly (gate): Red
- Diffusion (source/drain): Green for NMOS, Brown for PMOS
- Metal1: Blue
- Contact: Black (small squares)
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config, reset_style_config
import matplotlib.pyplot as plt


def setup_textbook_colors():
    """Set up standard textbook colors for CMOS"""
    print("Setting up textbook-standard CMOS colors...")

    reset_style_config()
    style = get_style_config()

    # Standard textbook CMOS colors
    # N-well (for PMOS) - light green with transparency
    style.set_layer_style('nwell',
                         color='lightgreen',
                         alpha=0.3,
                         edge_color='green',
                         edge_width=2.0,
                         shape='rectangle')

    # P-well/Substrate (for NMOS) - light pink/salmon with transparency
    style.set_layer_style('pwell',
                         color='lightcoral',
                         alpha=0.3,
                         edge_color='red',
                         edge_width=2.0,
                         shape='rectangle')

    # Polysilicon (gate) - red, solid
    style.set_layer_style('poly',
                         color='red',
                         alpha=0.7,
                         edge_color='darkred',
                         edge_width=2.0,
                         shape='rectangle')

    # N-diffusion (for NMOS source/drain) - green
    style.set_layer_style('ndiff',
                         color='green',
                         alpha=0.6,
                         edge_color='darkgreen',
                         edge_width=2.0,
                         shape='rectangle')

    # P-diffusion (for PMOS source/drain) - brown/tan
    style.set_layer_style('pdiff',
                         color='tan',
                         alpha=0.6,
                         edge_color='saddlebrown',
                         edge_width=2.0,
                         shape='rectangle')

    # Metal1 - blue
    style.set_layer_style('metal1',
                         color='blue',
                         alpha=0.6,
                         edge_color='darkblue',
                         edge_width=2.0,
                         shape='rectangle')

    # Contact - black, solid small squares
    style.set_layer_style('contact',
                         color='black',
                         alpha=0.9,
                         edge_color='black',
                         edge_width=1.0,
                         shape='rectangle')

    # Via - gray
    style.set_layer_style('via',
                         color='gray',
                         alpha=0.9,
                         edge_color='black',
                         edge_width=1.0,
                         shape='rectangle')

    print("✓ Textbook colors configured")


def create_nmos_transistor(name='NMOS', width=10, length=4):
    """
    Create an NMOS transistor with textbook layout

    Args:
        name: Transistor name
        width: Channel width (diffusion width)
        length: Channel length (poly width over diffusion)

    Returns:
        Cell containing NMOS transistor
    """
    print(f"\nCreating NMOS transistor '{name}'...")

    mos = Cell(name)

    # P-well/substrate (background)
    pwell = Cell(f'{name}_pwell', 'pwell')

    # N-diffusion regions (source and drain)
    ndiff_source = Cell(f'{name}_src', 'ndiff')
    ndiff_drain = Cell(f'{name}_drn', 'ndiff')

    # Polysilicon gate
    poly_gate = Cell(f'{name}_gate', 'poly')

    # Contacts
    contact_s = Cell(f'{name}_cont_s', 'contact')
    contact_d = Cell(f'{name}_cont_d', 'contact')

    # Metal1 connections
    metal_s = Cell(f'{name}_metal_s', 'metal1')
    metal_d = Cell(f'{name}_metal_d', 'metal1')

    mos.add_instance([pwell, ndiff_source, ndiff_drain, poly_gate,
                     contact_s, contact_d, metal_s, metal_d])

    # Layout constraints
    # P-well covers everything
    mos.constrain(pwell, f'x1=0, y1=0, x2-x1={width+8}, y2-y1={length+10}')

    # Source diffusion (left)
    mos.constrain(ndiff_source, f'x1=2, y1=3, x2-x1={width}, y2-y1={length+4}')

    # Poly gate (crosses over diffusions) - positioned after source
    mos.constrain(poly_gate, f'sx1=ox2, sy1=oy1-1, sx2-sx1={length}, sy2-sy1={length+6}', ndiff_source)

    # Drain diffusion (right) - after poly
    mos.constrain(ndiff_drain, f'sx1=ox2, sy1=oy1+1, sx2-sx1={width}, sy2-sy1={length+4}', poly_gate)

    # Contacts on diffusions
    mos.constrain(contact_s, f'sx1=ox1+{width//2-1}, sy1=oy1+1, sx2-sx1=2, sy2-sy1=2', ndiff_source)
    mos.constrain(contact_d, f'sx1=ox1+{width//2-1}, sy1=oy1+1, sx2-sx1=2, sy2-sy1=2', ndiff_drain)

    # Metal1 over contacts
    mos.constrain(metal_s, f'sx1=ox1-1, sy1=oy1-1, sx2-sx1={width+2}, sy2-sy1=4', ndiff_source)
    mos.constrain(metal_d, f'sx1=ox1-1, sy1=oy1-1, sx2-sx1={width+2}, sy2-sy1=4', ndiff_drain)

    mos.solver()
    print(f"✓ NMOS transistor created: W={width}, L={length}")
    return mos


def create_pmos_transistor(name='PMOS', width=10, length=4):
    """
    Create a PMOS transistor with textbook layout

    Args:
        name: Transistor name
        width: Channel width (diffusion width)
        length: Channel length (poly width over diffusion)

    Returns:
        Cell containing PMOS transistor
    """
    print(f"\nCreating PMOS transistor '{name}'...")

    mos = Cell(name)

    # N-well (background)
    nwell = Cell(f'{name}_nwell', 'nwell')

    # P-diffusion regions (source and drain)
    pdiff_source = Cell(f'{name}_src', 'pdiff')
    pdiff_drain = Cell(f'{name}_drn', 'pdiff')

    # Polysilicon gate
    poly_gate = Cell(f'{name}_gate', 'poly')

    # Contacts
    contact_s = Cell(f'{name}_cont_s', 'contact')
    contact_d = Cell(f'{name}_cont_d', 'contact')

    # Metal1 connections
    metal_s = Cell(f'{name}_metal_s', 'metal1')
    metal_d = Cell(f'{name}_metal_d', 'metal1')

    mos.add_instance([nwell, pdiff_source, pdiff_drain, poly_gate,
                     contact_s, contact_d, metal_s, metal_d])

    # Layout constraints (same structure as NMOS, different layers)
    # N-well covers everything
    mos.constrain(nwell, f'x1=0, y1=0, x2-x1={width+8}, y2-y1={length+10}')

    # Source diffusion (left)
    mos.constrain(pdiff_source, f'x1=2, y1=3, x2-x1={width}, y2-y1={length+4}')

    # Poly gate - positioned after source
    mos.constrain(poly_gate, f'sx1=ox2, sy1=oy1-1, sx2-sx1={length}, sy2-sy1={length+6}', pdiff_source)

    # Drain diffusion (right) - after poly
    mos.constrain(pdiff_drain, f'sx1=ox2, sy1=oy1+1, sx2-sx1={width}, sy2-sy1={length+4}', poly_gate)

    # Contacts
    mos.constrain(contact_s, f'sx1=ox1+{width//2-1}, sy1=oy1+1, sx2-sx1=2, sy2-sy1=2', pdiff_source)
    mos.constrain(contact_d, f'sx1=ox1+{width//2-1}, sy1=oy1+1, sx2-sx1=2, sy2-sy1=2', pdiff_drain)

    # Metal1
    mos.constrain(metal_s, f'sx1=ox1-1, sy1=oy1-1, sx2-sx1={width+2}, sy2-sy1=4', pdiff_source)
    mos.constrain(metal_d, f'sx1=ox1-1, sy1=oy1-1, sx2-sx1={width+2}, sy2-sy1=4', pdiff_drain)

    mos.solver()
    print(f"✓ PMOS transistor created: W={width}, L={length}")
    return mos


def create_mos_array(rows=2, cols=3, mos_type='NMOS', width=8, length=3, spacing=5):
    """
    Create an array of MOS transistors

    Args:
        rows: Number of rows
        cols: Number of columns
        mos_type: 'NMOS' or 'PMOS'
        width: Transistor width
        length: Transistor length
        spacing: Spacing between transistors

    Returns:
        Cell containing MOS array
    """
    print(f"\nCreating {rows}x{cols} {mos_type} array...")

    # Create template transistor
    if mos_type == 'NMOS':
        template = create_nmos_transistor('template', width, length)
    else:
        template = create_pmos_transistor('template', width, length)

    template.fix_layout()

    # Create array
    array = Cell(f'{mos_type}_array_{rows}x{cols}')

    transistors = []
    for row in range(rows):
        for col in range(cols):
            mos = template.copy(f'{mos_type}_{row}_{col}')
            array.add_instance(mos)
            transistors.append(mos)

            # Position calculation
            x = col * (width + 8 + spacing)
            y = row * (length + 10 + spacing)
            mos.set_position(x, y)

    print(f"✓ Created {rows}x{cols} {mos_type} array with {rows*cols} transistors")
    return array


def main():
    """Main demonstration"""
    print("="*70)
    print("MOS TRANSISTOR WITH TEXTBOOK COLORS")
    print("="*70)

    # Set up textbook colors
    setup_textbook_colors()

    # Create single NMOS
    print("\n" + "-"*70)
    print("1. Single NMOS Transistor")
    print("-"*70)
    nmos = create_nmos_transistor('NMOS_single', width=12, length=4)
    nmos.draw()
    fig = nmos.draw(show=False, solve_first=False)
    plt.savefig('demo_outputs/mos_nmos_textbook.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/mos_nmos_textbook.png")
    plt.close()

    # Create single PMOS
    print("\n" + "-"*70)
    print("2. Single PMOS Transistor")
    print("-"*70)
    pmos = create_pmos_transistor('PMOS_single', width=12, length=4)
    pmos.draw()
    fig = pmos.draw(show=False, solve_first=False)
    plt.savefig('demo_outputs/mos_pmos_textbook.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/mos_pmos_textbook.png")
    plt.close()

    # Create NMOS array
    print("\n" + "-"*70)
    print("3. NMOS Array (2x3)")
    print("-"*70)
    nmos_array = create_mos_array(rows=2, cols=3, mos_type='NMOS', width=8, length=3, spacing=3)
    nmos_array.draw()
    fig = nmos_array.draw(show=False, solve_first=False)
    plt.savefig('demo_outputs/mos_nmos_array_textbook.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/mos_nmos_array_textbook.png")
    plt.close()
    
    # Create PMOS array
    print("\n" + "-"*70)
    print("4. PMOS Array (2x3)")
    print("-"*70)
    pmos_array = create_mos_array(rows=2, cols=3, mos_type='PMOS', width=8, length=3, spacing=3)
    pmos_array.draw()
    fig = pmos_array.draw(show=False, solve_first=False)
    plt.savefig('demo_outputs/mos_pmos_array_textbook.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/mos_pmos_array_textbook.png")
    plt.close()

    # Create CMOS comparison
    print("\n" + "-"*70)
    print("5. NMOS and PMOS Comparison")
    print("-"*70)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=100)

    nmos_comp = create_nmos_transistor('NMOS', width=12, length=4)
    nmos_comp.draw(ax=ax1, show=False, solve_first=False)
    ax1.set_title('NMOS Transistor\n(N-diffusion in P-well)', fontsize=14, fontweight='bold')

    pmos_comp = create_pmos_transistor('PMOS', width=12, length=4)
    pmos_comp.draw(ax=ax2, show=False, solve_first=False)
    ax2.set_title('PMOS Transistor\n(P-diffusion in N-well)', fontsize=14, fontweight='bold')

    plt.suptitle('CMOS Transistors - Textbook Standard Colors', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('demo_outputs/mos_cmos_comparison_textbook.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/mos_cmos_comparison_textbook.png")
    plt.close()

    # Create legend
    print("\n" + "-"*70)
    print("6. Color Legend")
    print("-"*70)
    print_color_legend()

    print("\n" + "="*70)
    print("ALL MOS TRANSISTORS CREATED SUCCESSFULLY")
    print("="*70)
    print("\nGenerated files:")
    print("  1. mos_nmos_textbook.png - Single NMOS transistor")
    print("  2. mos_pmos_textbook.png - Single PMOS transistor")
    print("  3. mos_nmos_array_textbook.png - 2x3 NMOS array")
    print("  4. mos_pmos_array_textbook.png - 2x3 PMOS array")
    print("  5. mos_cmos_comparison_textbook.png - NMOS vs PMOS comparison")
    print("\nTextbook color scheme:")
    print("  ✓ N-well (PMOS): Light green")
    print("  ✓ P-well (NMOS): Light pink/coral")
    print("  ✓ Poly (gate): Red")
    print("  ✓ N-diffusion: Green")
    print("  ✓ P-diffusion: Tan/brown")
    print("  ✓ Metal1: Blue")
    print("  ✓ Contact: Black")


def print_color_legend():
    """Print textbook color legend"""
    print("\nTextbook-Standard CMOS Colors:")
    print("  Layer          | Color         | Usage")
    print("  " + "-"*60)
    print("  N-well         | Light green   | PMOS substrate")
    print("  P-well         | Light coral   | NMOS substrate")
    print("  Poly           | Red           | Gate material")
    print("  N-diffusion    | Green         | NMOS source/drain")
    print("  P-diffusion    | Tan/brown     | PMOS source/drain")
    print("  Metal1         | Blue          | Interconnect")
    print("  Contact        | Black         | Via holes")


if __name__ == '__main__':
    main()
