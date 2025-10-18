"""
Demonstration of style customization features

Shows how to customize:
- Layer colors
- Boundary colors
- Boundary thickness
- Shape types (rectangle, rounded, circle, ellipse, octagon)
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config, reset_style_config
import matplotlib.pyplot as plt


def demo_basic_customization():
    """Demo 1: Basic layer color and boundary customization"""
    print("="*70)
    print("DEMO 1: Basic Layer Color and Boundary Customization")
    print("="*70)

    # Reset to defaults
    reset_style_config()
    style = get_style_config()

    # Customize metal1 layer
    style.set_layer_style('metal1',
                         color='gold',
                         alpha=0.7,
                         edge_color='darkgoldenrod',
                         edge_width=3.0)

    # Customize poly layer
    style.set_layer_style('poly',
                         color='mediumpurple',
                         alpha=0.6,
                         edge_color='indigo',
                         edge_width=2.5)

    # Create a simple layout
    cell = Cell('custom_colors')
    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'poly')
    r3 = Cell('r3', 'metal1')

    cell.add_instance([r1, r2, r3])
    cell.constrain(r1, 'x2-x1=10, y2-y1=10')
    cell.constrain(r2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=8, sy2-sy1=10', r1)
    cell.constrain(r3, 'sx1=ox1, sy1=oy2+2, sx2-sx1=20, sy2-sy1=5', r1)
    cell.constrain(r1, 'sx1=x1, sy1=y1')

    fig = cell.draw(show=False)
    plt.savefig('demo_outputs/style_custom_colors.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/style_custom_colors.png")
    print("  - metal1: gold color with thick darkgoldenrod border")
    print("  - poly: mediumpurple color with indigo border")
    plt.close()


def demo_shape_customization():
    """Demo 2: Different shape types"""
    print("\n" + "="*70)
    print("DEMO 2: Shape Type Customization")
    print("="*70)

    # Reset and customize shapes
    reset_style_config()
    style = get_style_config()

    # Set different shapes for different layers
    style.set_layer_style('metal1', color='blue', shape='rounded')
    style.set_layer_style('metal2', color='red', shape='circle')
    style.set_layer_style('poly', color='purple', shape='octagon')
    style.set_layer_style('metal3', color='green', shape='ellipse')

    # Create layout with different shapes
    cell = Cell('shapes_demo')
    m1 = Cell('m1', 'metal1')
    m2 = Cell('m2', 'metal2')
    poly = Cell('poly', 'poly')
    m3 = Cell('m3', 'metal3')

    cell.add_instance([m1, m2, poly, m3])
    cell.constrain(m1, 'x1=0, y1=0, x2-x1=15, y2-y1=10')
    cell.constrain(m2, 'sx1=ox2+5, sy1=oy1, sx2-sx1=10, sy2-sy1=10', m1)
    cell.constrain(poly, 'sx1=ox1, sy1=oy2+5, sx2-sx1=15, sy2-sy1=10', m1)
    cell.constrain(m3, 'sx1=ox2+5, sy1=oy1, sx2-sx1=15, sy2-sy1=10', poly)

    fig = cell.draw(show=False)
    plt.savefig('demo_outputs/style_shapes.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/style_shapes.png")
    print("  - metal1: Rounded rectangle")
    print("  - metal2: Circle")
    print("  - poly: Octagon")
    print("  - metal3: Ellipse")
    plt.close()


def demo_container_customization():
    """Demo 3: Container boundary customization"""
    print("\n" + "="*70)
    print("DEMO 3: Container Boundary Customization")
    print("="*70)

    # Reset and customize container
    reset_style_config()
    style = get_style_config()

    # Customize container appearance
    style.set_container_style(
        edge_color='crimson',
        edge_width=3.0,
        linestyle='-.',  # dash-dot line
        alpha=1.0,
        shape='rounded'
    )

    # Set custom color cycle for hierarchy levels
    style.set_container_colors(['crimson', 'navy', 'darkgreen', 'darkorange'])

    # Create hierarchical layout
    top = Cell('top')
    sub1 = Cell('sub1')
    sub2 = Cell('sub2')

    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'poly')

    sub1.add_instance(r1)
    sub1.constrain(r1, 'x2-x1=8, y2-y1=8, x1=0, y1=0')

    sub2.add_instance(r2)
    sub2.constrain(r2, 'x2-x1=8, y2-y1=8, x1=0, y1=0')

    top.add_instance([sub1, sub2])
    top.constrain(sub1, 'x1=5, y1=5')
    top.constrain(sub2, 'sx1=ox2+5, sy1=oy1', sub1)

    fig = top.draw(show=False)
    plt.savefig('demo_outputs/style_containers.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/style_containers.png")
    print("  - Crimson rounded containers with dash-dot borders")
    print("  - Custom color cycling for hierarchy levels")
    plt.close()


def demo_advanced_customization():
    """Demo 4: Advanced multi-layer customization"""
    print("\n" + "="*70)
    print("DEMO 4: Advanced Multi-Layer Customization")
    print("="*70)

    # Reset and create custom theme
    reset_style_config()
    style = get_style_config()

    # Create a custom "dark theme"
    style.set_layer_style('metal1', color='steelblue', alpha=0.8,
                         edge_color='navy', edge_width=2.5, shape='rounded')
    style.set_layer_style('metal2', color='firebrick', alpha=0.8,
                         edge_color='darkred', edge_width=2.5, shape='rounded')
    style.set_layer_style('poly', color='mediumpurple', alpha=0.8,
                         edge_color='indigo', edge_width=2.0, shape='ellipse')
    style.set_layer_style('contact', color='gray', alpha=0.9,
                         edge_color='black', edge_width=1.5, shape='circle')

    # Build a complex layout
    top = Cell('chip')

    # Create a reusable block
    block = Cell('block')
    m1 = Cell('m1', 'metal1')
    m2 = Cell('m2', 'metal2')
    contact = Cell('via', 'contact')

    block.add_instance([m1, m2, contact])
    block.constrain(m1, 'x2-x1=12, y2-y1=8')
    block.constrain(m2, 'sx1=ox1, sy1=oy2+2, sx2-sx1=12, sy2-sy1=6', m1)
    block.constrain(contact, 'sx1=ox1+5, sy1=oy1+3, sx2-sx1=2, sy2-sy1=2', m1)
    block.constrain(m1, 'sx1=x1, sy1=y1')
    block.solver()
    block.fix_layout()

    # Create array
    b1 = block.copy('b1')
    b2 = block.copy('b2')
    b3 = block.copy('b3')

    top.add_instance([b1, b2, b3])
    top.constrain(b1, 'x1=0, y1=0')
    top.constrain(b2, 'sx1=ox2+5, sy1=oy1', b1)
    top.constrain(b3, 'sx1=ox1, sy1=oy2+5', b1)

    fig = top.draw(show=False)
    plt.savefig('demo_outputs/style_advanced.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/style_advanced.png")
    print("  - Custom dark theme with rounded metal layers")
    print("  - Ellipse poly shapes")
    print("  - Circular contact/via shapes")
    plt.close()


def demo_comparison():
    """Demo 5: Side-by-side comparison of default vs custom styles"""
    print("\n" + "="*70)
    print("DEMO 5: Default vs Custom Style Comparison")
    print("="*70)

    # Create same layout twice
    def create_layout():
        cell = Cell('layout')
        r1 = Cell('r1', 'metal1')
        r2 = Cell('r2', 'poly')
        r3 = Cell('r3', 'metal2')

        cell.add_instance([r1, r2, r3])
        cell.constrain(r1, 'x2-x1=10, y2-y1=8')
        cell.constrain(r2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=8, sy2-sy1=8', r1)
        cell.constrain(r3, 'sx1=ox1, sy1=oy2+3, sx2-sx1=20, sy2-sy1=5', r1)
        cell.constrain(r1, 'sx1=x1, sy1=y1')
        return cell

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=100)

    # Default style
    reset_style_config()
    cell1 = create_layout()
    cell1.draw(ax=ax1, show=False)
    ax1.set_title('Default Style', fontsize=16, fontweight='bold')

    # Custom style
    style = get_style_config()
    style.set_layer_style('metal1', color='cyan', edge_color='teal',
                         edge_width=3.0, shape='rounded')
    style.set_layer_style('metal2', color='magenta', edge_color='purple',
                         edge_width=3.0, shape='rounded')
    style.set_layer_style('poly', color='yellow', edge_color='orange',
                         edge_width=2.5, shape='octagon')

    cell2 = create_layout()
    cell2.draw(ax=ax2, show=False)
    ax2.set_title('Custom Style', fontsize=16, fontweight='bold')

    plt.suptitle('Style Customization Comparison', fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig('demo_outputs/style_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved to demo_outputs/style_comparison.png")
    print("  - Side-by-side comparison of default and custom styles")
    plt.close()


def main():
    """Run all style customization demos"""
    print("\n" + "#"*70)
    print("# STYLE CUSTOMIZATION DEMONSTRATION")
    print("#"*70)

    demo_basic_customization()
    demo_shape_customization()
    demo_container_customization()
    demo_advanced_customization()
    demo_comparison()

    print("\n" + "#"*70)
    print("# ALL DEMOS COMPLETED")
    print("#"*70)
    print("\nGenerated files in demo_outputs/:")
    print("  1. style_custom_colors.png - Basic color customization")
    print("  2. style_shapes.png - Different shape types")
    print("  3. style_containers.png - Container boundary styles")
    print("  4. style_advanced.png - Advanced multi-layer theme")
    print("  5. style_comparison.png - Default vs custom comparison")
    print("\nStyle customization features:")
    print("  ✓ Layer colors (any matplotlib color)")
    print("  ✓ Boundary colors (independent from fill)")
    print("  ✓ Boundary thickness (any width)")
    print("  ✓ Shapes (rectangle, rounded, circle, ellipse, octagon)")
    print("  ✓ Container styles (color, width, linestyle)")
    print("  ✓ Transparency/alpha control")


if __name__ == '__main__':
    main()
