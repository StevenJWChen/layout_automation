#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: GDS to Constraint Workflow

Demonstrates how to:
1. Import a GDS file
2. Extract it to an editable constraint format
3. Modify the constraints
4. Regenerate GDS with new dimensions
"""

import sys
sys.path.insert(0, '..')

from tools.gds_to_constraints import (
    GDSToConstraints,
    ConstraintsToGDS,
    convert_gds_to_constraints,
    regenerate_gds_from_constraints
)


def example_basic_conversion():
    """Example 1: Basic GDS to constraint conversion"""
    print("="*70)
    print("Example 1: Convert GDS to Constraints")
    print("="*70)

    # Convert an existing GDS file to constraints
    gds_file = "sky130_inv_replica.gds"
    output_file = "inverter_constraints.yaml"

    # SkyWater layer mapping
    layer_map = {
        67: 'metal1',
        66: 'poly',
        65: 'diff',
        64: 'nwell',
        # Add more layers as needed
    }

    try:
        converter = GDSToConstraints(gds_file, cell_name="sky130_fd_sc_hd__inv_1_replica")
        converter.set_layer_map(layer_map)

        # Extract constraints with spacing analysis
        constraints = converter.extract_constraints(
            analyze_spacing=True,
            spacing_threshold=5.0  # Consider polygons within 5um
        )

        # Export to YAML (human-readable)
        converter.export_to_yaml(output_file, constraints)

        print(f"\n✓ Created {output_file}")
        print(f"  You can now edit this file to adjust:")
        print(f"    - Polygon sizes (width, height)")
        print(f"    - Positions (x1, y1, x2, y2)")
        print(f"    - Spacing constraints")

    except FileNotFoundError:
        print(f"File {gds_file} not found. Using demonstration with test data...")
        demonstrate_with_test_data()


def demonstrate_with_test_data():
    """Demonstrate workflow with generated test data"""
    print("\n" + "="*70)
    print("Demo: Creating Test Layout and Converting")
    print("="*70)

    import gdstk
    from layout_automation import GDSCell, Polygon

    # Create a simple test layout
    print("\n1. Creating test GDS layout...")
    cell = GDSCell('test_cell')

    # Add some polygons
    poly1 = Polygon('rect1', 'metal1')
    poly2 = Polygon('rect2', 'metal1')
    poly3 = Polygon('rect3', 'poly')

    cell.add_polygon([poly1, poly2, poly3])

    # Add constraints
    cell.constrain(poly1, 'sx1=0, sy1=0, sx2=10, sy2=5')
    cell.constrain(poly2, 'sx1=15, sy1=0, sx2=25, sy2=5')
    cell.constrain(poly3, 'sx1=0, sy1=10, sx2=25, sy2=15')

    # Solve and export
    cell.solver()
    cell.export_gds('test_layout.gds')
    print("✓ Created test_layout.gds")

    # Now convert to constraints
    print("\n2. Converting GDS to constraint format...")
    layer_map = {
        0: 'metal1',
        1: 'poly',
        2: 'diff'
    }

    converter = GDSToConstraints('test_layout.gds', 'test_cell')
    converter.set_layer_map(layer_map)
    constraints = converter.extract_constraints(analyze_spacing=True)
    converter.export_to_yaml('test_constraints.yaml', constraints)

    print("\n3. Constraint file created: test_constraints.yaml")
    print("   You can now edit this file!")


def example_modify_and_regenerate():
    """Example 2: Modify constraints and regenerate GDS"""
    print("\n" + "="*70)
    print("Example 2: Modify Constraints and Regenerate GDS")
    print("="*70)

    import yaml

    constraint_file = 'test_constraints.yaml'

    try:
        # Read the constraint file
        with open(constraint_file, 'r') as f:
            data = yaml.safe_load(f)

        print(f"\nOriginal dimensions:")
        print(f"  Cell width: {data['dimensions']['width']}")
        print(f"  Cell height: {data['dimensions']['height']}")

        # Modify constraints - make everything 20% larger
        scale_factor = 1.2

        print(f"\nScaling all polygons by {scale_factor}x...")

        for poly in data['polygons']:
            # Scale dimensions
            poly['size']['width'] *= scale_factor
            poly['size']['height'] *= scale_factor

            # Scale positions
            poly['position']['x1'] *= scale_factor
            poly['position']['y1'] *= scale_factor
            poly['position']['x2'] *= scale_factor
            poly['position']['y2'] *= scale_factor

            # Scale spacing constraints if present
            if 'spacing' in poly:
                for constraint in poly['spacing']:
                    if 'spacing' in constraint:
                        constraint['spacing'] *= scale_factor

        # Update cell dimensions
        data['dimensions']['width'] *= scale_factor
        data['dimensions']['height'] *= scale_factor

        # Save modified constraints
        modified_file = 'test_constraints_scaled.yaml'
        with open(modified_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)

        print(f"✓ Saved modified constraints to: {modified_file}")

        # Regenerate GDS
        print(f"\nRegenerating GDS from modified constraints...")
        regenerate_gds_from_constraints(modified_file, 'test_layout_scaled.gds')

        print(f"\n✓ Success! Created test_layout_scaled.gds")
        print(f"  All dimensions are now {scale_factor}x larger")

    except FileNotFoundError:
        print(f"\nConstraint file not found. Run example_basic_conversion() first.")


def example_manual_editing():
    """Example 3: Show what users can edit manually"""
    print("\n" + "="*70)
    print("Example 3: Manual Editing Guide")
    print("="*70)

    example_yaml = """
# Example constraint file that users can edit

cell_name: my_cell
dimensions:
  width: 100.0      # Total cell width (auto-calculated)
  height: 50.0      # Total cell height (auto-calculated)

polygons:
  - name: metal1_1
    layer: metal1
    layer_num: 67
    datatype: 0
    position:
      x1: 0.0         # ← EDIT: Left edge position
      y1: 0.0         # ← EDIT: Bottom edge position
      x2: 20.0        # ← EDIT: Right edge position
      y2: 10.0        # ← EDIT: Top edge position
    size:
      width: 20.0     # ← EDIT: Width (x2 - x1)
      height: 10.0    # ← EDIT: Height (y2 - y1)
    spacing:          # Optional spacing constraints
      - type: horizontal_spacing
        to: metal1_2
        spacing: 5.0  # ← EDIT: Spacing to next polygon
        direction: right

  - name: metal1_2
    layer: metal1
    layer_num: 67
    datatype: 0
    position:
      x1: 25.0
      y1: 0.0
      x2: 45.0
      y2: 10.0
    size:
      width: 20.0
      height: 10.0
"""

    print("\nUsers can edit the YAML file to:")
    print("  ✓ Change polygon sizes (width, height)")
    print("  ✓ Move polygons (x1, y1, x2, y2)")
    print("  ✓ Adjust spacing between elements")
    print("  ✓ Scale entire design")
    print("  ✓ Add/remove polygons")
    print("\nExample YAML format:")
    print(example_yaml)

    print("\nAfter editing, regenerate GDS with:")
    print("  python gds_to_constraints.py --regenerate my_constraints.yaml output.gds")


def example_programmatic_modification():
    """Example 4: Programmatic constraint modification"""
    print("\n" + "="*70)
    print("Example 4: Programmatic Modification (Python API)")
    print("="*70)

    code_example = '''
from tools.gds_to_constraints import GDSToConstraints, ConstraintsToGDS
import yaml

# 1. Load GDS and extract constraints
converter = GDSToConstraints('input.gds', 'cell_name')
constraints = converter.extract_constraints()

# 2. Modify in Python
for poly in constraints.polygons:
    # Double the width of all metal1 polygons
    if poly.layer == 'metal1':
        poly.width *= 2.0
        poly.x2 = poly.x1 + poly.width

    # Move all polygons up by 10 units
    poly.y1 += 10
    poly.y2 += 10

# 3. Export modified constraints
converter.export_to_yaml('modified.yaml', constraints)

# 4. Regenerate GDS
regenerator = ConstraintsToGDS('modified.yaml')
regenerator.generate_gds('output.gds')
'''

    print("\nProgrammatic modification example:")
    print(code_example)


if __name__ == '__main__':
    print("GDS to Constraint Format - Complete Workflow Examples")
    print("="*70)

    # Run examples
    example_basic_conversion()
    example_modify_and_regenerate()
    example_manual_editing()
    example_programmatic_modification()

    print("\n" + "="*70)
    print("Examples Complete!")
    print("="*70)
    print("\nQuick Start:")
    print("  1. Convert GDS → Constraints:")
    print("     python -m tools.gds_to_constraints input.gds output.yaml")
    print()
    print("  2. Edit the YAML file with any text editor")
    print()
    print("  3. Regenerate GDS:")
    print("     python -m tools.gds_to_constraints --regenerate output.yaml new.gds")
