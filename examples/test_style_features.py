"""
Test style customization features

Verifies:
- Layer color customization
- Boundary color and thickness
- Shape types
- Container styles
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config, reset_style_config
import matplotlib.pyplot as plt


def test_layer_color_customization():
    """Test 1: Layer color customization"""
    print("="*70)
    print("TEST 1: Layer Color Customization")
    print("="*70)

    reset_style_config()
    style = get_style_config()

    # Set custom colors
    style.set_layer_style('metal1', color='red', alpha=0.8)
    style.set_layer_style('poly', color='blue', alpha=0.5)

    # Verify settings
    metal1_style = style.get_layer_style('metal1')
    poly_style = style.get_layer_style('poly')

    assert metal1_style.color == 'red', f"Failed: metal1 color should be red, got {metal1_style.color}"
    assert metal1_style.alpha == 0.8, f"Failed: metal1 alpha should be 0.8, got {metal1_style.alpha}"
    assert poly_style.color == 'blue', f"Failed: poly color should be blue, got {poly_style.color}"
    assert poly_style.alpha == 0.5, f"Failed: poly alpha should be 0.5, got {poly_style.alpha}"

    print("✓ PASS: Layer colors customized correctly")


def test_boundary_customization():
    """Test 2: Boundary color and thickness"""
    print("\n" + "="*70)
    print("TEST 2: Boundary Color and Thickness")
    print("="*70)

    reset_style_config()
    style = get_style_config()

    # Set custom boundaries
    style.set_layer_style('metal1',
                         edge_color='darkred',
                         edge_width=5.0)

    metal1_style = style.get_layer_style('metal1')

    assert metal1_style.edge_color == 'darkred', \
        f"Failed: edge color should be darkred, got {metal1_style.edge_color}"
    assert metal1_style.edge_width == 5.0, \
        f"Failed: edge width should be 5.0, got {metal1_style.edge_width}"

    print("✓ PASS: Boundary color and thickness customized correctly")


def test_shape_customization():
    """Test 3: Shape type customization"""
    print("\n" + "="*70)
    print("TEST 3: Shape Type Customization")
    print("="*70)

    reset_style_config()
    style = get_style_config()

    # Set different shapes
    shapes = ['rectangle', 'rounded', 'circle', 'ellipse', 'octagon']
    layers = ['metal1', 'metal2', 'metal3', 'poly', 'diff']

    for layer, shape in zip(layers, shapes):
        style.set_layer_style(layer, shape=shape)

    # Verify
    for layer, expected_shape in zip(layers, shapes):
        layer_style = style.get_layer_style(layer)
        assert layer_style.shape == expected_shape, \
            f"Failed: {layer} shape should be {expected_shape}, got {layer_style.shape}"

    print("✓ PASS: All shape types set correctly")
    print(f"  Tested shapes: {', '.join(shapes)}")


def test_container_customization():
    """Test 4: Container style customization"""
    print("\n" + "="*70)
    print("TEST 4: Container Style Customization")
    print("="*70)

    reset_style_config()
    style = get_style_config()

    # Customize container
    style.set_container_style(
        edge_color='crimson',
        edge_width=3.5,
        linestyle='-.',
        alpha=0.9,
        shape='rounded'
    )

    container = style.container_style

    assert container.edge_color == 'crimson', \
        f"Failed: container edge_color should be crimson, got {container.edge_color}"
    assert container.edge_width == 3.5, \
        f"Failed: container edge_width should be 3.5, got {container.edge_width}"
    assert container.linestyle == '-.', \
        f"Failed: container linestyle should be '-.', got {container.linestyle}"
    assert container.alpha == 0.9, \
        f"Failed: container alpha should be 0.9, got {container.alpha}"
    assert container.shape == 'rounded', \
        f"Failed: container shape should be rounded, got {container.shape}"

    print("✓ PASS: Container style customized correctly")


def test_container_color_cycling():
    """Test 5: Container color cycling"""
    print("\n" + "="*70)
    print("TEST 5: Container Color Cycling")
    print("="*70)

    reset_style_config()
    style = get_style_config()

    # Set custom color cycle
    custom_colors = ['red', 'green', 'blue']
    style.set_container_colors(custom_colors)

    # Verify cycling
    for level in range(6):  # Test two full cycles
        expected_color = custom_colors[level % len(custom_colors)]
        actual_color = style.get_container_color(level)
        assert actual_color == expected_color, \
            f"Failed: Level {level} should have color {expected_color}, got {actual_color}"

    print("✓ PASS: Container color cycling works correctly")


def test_reset_functionality():
    """Test 6: Reset to defaults"""
    print("\n" + "="*70)
    print("TEST 6: Reset Functionality")
    print("="*70)

    # Customize everything
    style = get_style_config()
    style.set_layer_style('metal1', color='pink', edge_width=10.0, shape='circle')
    style.set_container_style(edge_color='yellow', edge_width=5.0)

    # Reset
    reset_style_config()
    style = get_style_config()

    # Check defaults restored
    metal1 = style.get_layer_style('metal1')
    assert metal1.color == 'blue', "Failed: metal1 should reset to blue"
    assert metal1.edge_width == 2.0, "Failed: metal1 edge_width should reset to 2.0"
    assert metal1.shape == 'rectangle', "Failed: metal1 shape should reset to rectangle"

    print("✓ PASS: Reset to defaults works correctly")


def test_visual_output():
    """Test 7: Visual output with custom styles"""
    print("\n" + "="*70)
    print("TEST 7: Visual Output")
    print("="*70)

    reset_style_config()
    style = get_style_config()

    # Set up custom styles
    style.set_layer_style('metal1', color='teal', shape='rounded', edge_width=3.0)
    style.set_layer_style('poly', color='coral', shape='ellipse', edge_width=2.0)

    # Create layout
    cell = Cell('visual_test')
    m1 = Cell('m1', 'metal1')
    poly = Cell('poly', 'poly')

    cell.add_instance([m1, poly])
    cell.constrain(m1, 'x2-x1=10, y2-y1=8, x1=0, y1=0')
    cell.constrain(poly, 'sx1=ox2+3, sy1=oy1, sx2-sx1=8, sy2-sy1=8', m1)

    # Draw
    fig = cell.draw(show=False)

    # Verify figure was created
    assert fig is not None, "Failed: Figure should be created"

    plt.savefig('demo_outputs/test_visual_output.png', dpi=100, bbox_inches='tight')
    plt.close()

    print("✓ PASS: Visual output generated successfully")
    print("  Saved to demo_outputs/test_visual_output.png")


def main():
    """Run all style customization tests"""
    print("\n" + "#"*70)
    print("# STYLE CUSTOMIZATION TESTS")
    print("#"*70)

    test_layer_color_customization()
    test_boundary_customization()
    test_shape_customization()
    test_container_customization()
    test_container_color_cycling()
    test_reset_functionality()
    test_visual_output()

    print("\n" + "#"*70)
    print("# ALL TESTS PASSED ✓")
    print("#"*70)
    print("\nVerified features:")
    print("  ✓ Layer color customization")
    print("  ✓ Boundary color and thickness")
    print("  ✓ Shape type customization (5 types)")
    print("  ✓ Container style customization")
    print("  ✓ Container color cycling")
    print("  ✓ Reset to defaults")
    print("  ✓ Visual output generation")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
