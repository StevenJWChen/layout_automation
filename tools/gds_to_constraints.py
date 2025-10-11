#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDS to Constraint Format Converter

Imports GDS files and generates editable constraint files that users can modify.
Users can then regenerate the GDS with adjusted sizes while maintaining topology.

Flow:
1. Import GDS → Extract polygons and topology
2. Generate constraint file (human-readable YAML/JSON)
3. User edits constraints (sizes, spacing, etc.)
4. Regenerate GDS from modified constraints

This enables parametric modification of existing layouts.
"""

import gdstk
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import yaml


@dataclass
class PolygonConstraint:
    """Constraint representation of a polygon"""
    name: str
    layer: str
    layer_num: int
    datatype: int

    # Bounding box (will be converted to constraints)
    x1: float
    y1: float
    x2: float
    y2: float

    # Size constraints (derived from bbox)
    width: float
    height: float

    # Position reference (can be 'absolute' or reference to other polygon)
    position_ref: str = 'absolute'

    # Spacing constraints to other polygons
    spacing_constraints: List[Dict[str, any]] = None

    def __post_init__(self):
        if self.spacing_constraints is None:
            self.spacing_constraints = []


@dataclass
class CellConstraints:
    """Constraint representation of a GDS cell"""
    cell_name: str
    polygons: List[PolygonConstraint]

    # Cell-level constraints
    total_width: float
    total_height: float

    # Technology parameters (optional)
    tech_node: Optional[str] = None
    design_rules: Optional[Dict[str, float]] = None


class GDSToConstraints:
    """
    Convert GDS layout to editable constraint format

    Features:
    - Extracts all polygons with their geometry
    - Analyzes spatial relationships (spacing, alignment)
    - Generates human-readable constraint file
    - Supports re-generation with modified parameters
    """

    def __init__(self, gds_file: str, cell_name: Optional[str] = None):
        """
        Initialize GDS to Constraints converter

        Args:
            gds_file: Path to GDS file
            cell_name: Cell name to extract (if None, uses first cell)
        """
        self.gds_file = gds_file
        self.lib = gdstk.read_gds(gds_file)

        # Select cell
        if cell_name:
            self.cell = self.lib.cells[0] if self.lib.cells else None
            for c in self.lib.cells:
                if c.name == cell_name:
                    self.cell = c
                    break
        else:
            self.cell = self.lib.cells[0] if self.lib.cells else None

        if not self.cell:
            raise ValueError(f"Cell '{cell_name}' not found in {gds_file}")

        self.layer_map = {}  # Layer number -> name mapping

    def set_layer_map(self, layer_map: Dict[int, str]):
        """
        Set layer number to name mapping

        Args:
            layer_map: Dictionary mapping layer numbers to names
                      e.g., {67: 'metal1', 66: 'poly', 64: 'diff'}
        """
        self.layer_map = layer_map

    def _get_layer_name(self, layer_num: int, datatype: int) -> str:
        """Get layer name from number, or default to 'layerN'"""
        if layer_num in self.layer_map:
            return self.layer_map[layer_num]
        return f"layer{layer_num}"

    def _get_polygon_bbox(self, polygon: gdstk.Polygon) -> Tuple[float, float, float, float]:
        """Get bounding box of a polygon"""
        points = polygon.points
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    def _analyze_spacing(self, poly1_bbox: Tuple, poly2_bbox: Tuple,
                         poly1_name: str, poly2_name: str) -> Optional[Dict]:
        """
        Analyze spacing between two polygons

        Returns spacing constraint if polygons are nearby
        """
        x1_min, y1_min, x1_max, y1_max = poly1_bbox
        x2_min, y2_min, x2_max, y2_max = poly2_bbox

        # Horizontal spacing (poly2 is to the right of poly1)
        if x1_max <= x2_min:
            h_spacing = x2_min - x1_max
            # Check if they're roughly aligned vertically
            if not (y1_max < y2_min or y2_max < y1_min):
                return {
                    'type': 'horizontal_spacing',
                    'to': poly2_name,
                    'spacing': h_spacing,
                    'direction': 'right'
                }

        # Vertical spacing (poly2 is above poly1)
        if y1_max <= y2_min:
            v_spacing = y2_min - y1_max
            # Check if they're roughly aligned horizontally
            if not (x1_max < x2_min or x2_max < x1_min):
                return {
                    'type': 'vertical_spacing',
                    'to': poly2_name,
                    'spacing': v_spacing,
                    'direction': 'above'
                }

        return None

    def extract_constraints(self, analyze_spacing: bool = True,
                           spacing_threshold: float = 10.0) -> CellConstraints:
        """
        Extract constraints from GDS cell

        Args:
            analyze_spacing: Whether to analyze spacing between polygons
            spacing_threshold: Max distance to consider for spacing constraints (um)

        Returns:
            CellConstraints object with all extracted constraints
        """
        polygons = []
        poly_counter = {}  # Track polygon counts per layer

        # Extract all polygons
        for poly in self.cell.polygons:
            layer_num = poly.layer
            datatype = poly.datatype
            layer_name = self._get_layer_name(layer_num, datatype)

            # Generate unique name
            if layer_name not in poly_counter:
                poly_counter[layer_name] = 0
            poly_counter[layer_name] += 1
            poly_name = f"{layer_name}_{poly_counter[layer_name]}"

            # Get bounding box
            x1, y1, x2, y2 = self._get_polygon_bbox(poly)
            width = x2 - x1
            height = y2 - y1

            # Create constraint
            poly_constraint = PolygonConstraint(
                name=poly_name,
                layer=layer_name,
                layer_num=layer_num,
                datatype=datatype,
                x1=x1, y1=y1, x2=x2, y2=y2,
                width=width,
                height=height
            )

            polygons.append(poly_constraint)

        # Analyze spacing relationships if requested
        if analyze_spacing:
            for i, p1 in enumerate(polygons):
                p1_bbox = (p1.x1, p1.y1, p1.x2, p1.y2)

                for j, p2 in enumerate(polygons):
                    if i >= j:
                        continue

                    p2_bbox = (p2.x1, p2.y1, p2.x2, p2.y2)

                    # Check if polygons are close enough
                    dx = min(abs(p1.x1 - p2.x2), abs(p1.x2 - p2.x1))
                    dy = min(abs(p1.y1 - p2.y2), abs(p1.y2 - p2.y1))

                    if min(dx, dy) <= spacing_threshold:
                        constraint = self._analyze_spacing(p1_bbox, p2_bbox, p1.name, p2.name)
                        if constraint:
                            p1.spacing_constraints.append(constraint)

        # Calculate cell bounds
        if polygons:
            all_x1 = min(p.x1 for p in polygons)
            all_y1 = min(p.y1 for p in polygons)
            all_x2 = max(p.x2 for p in polygons)
            all_y2 = max(p.y2 for p in polygons)
            total_width = all_x2 - all_x1
            total_height = all_y2 - all_y1
        else:
            total_width = 0
            total_height = 0

        return CellConstraints(
            cell_name=self.cell.name,
            polygons=polygons,
            total_width=total_width,
            total_height=total_height
        )

    def export_to_yaml(self, output_file: str, constraints: Optional[CellConstraints] = None):
        """
        Export constraints to YAML file (human-readable)

        Args:
            output_file: Output YAML file path
            constraints: CellConstraints object (if None, will extract)
        """
        if constraints is None:
            constraints = self.extract_constraints()

        # Convert to dict with explicit float conversion to avoid numpy types
        data = {
            'cell_name': constraints.cell_name,
            'dimensions': {
                'width': float(constraints.total_width),
                'height': float(constraints.total_height)
            },
            'polygons': []
        }

        for poly in constraints.polygons:
            poly_data = {
                'name': poly.name,
                'layer': poly.layer,
                'layer_num': int(poly.layer_num),
                'datatype': int(poly.datatype),
                'position': {
                    'x1': float(poly.x1),
                    'y1': float(poly.y1),
                    'x2': float(poly.x2),
                    'y2': float(poly.y2)
                },
                'size': {
                    'width': float(poly.width),
                    'height': float(poly.height)
                }
            }

            if poly.spacing_constraints:
                # Convert spacing constraints to plain Python types
                spacing_list = []
                for sc in poly.spacing_constraints:
                    spacing_dict = {}
                    for k, v in sc.items():
                        if isinstance(v, (float, int)):
                            spacing_dict[k] = float(v)
                        else:
                            spacing_dict[k] = v
                    spacing_list.append(spacing_dict)
                poly_data['spacing'] = spacing_list

            data['polygons'].append(poly_data)

        # Write YAML
        with open(output_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)

        print(f"Exported constraints to: {output_file}")
        print(f"  Cell: {constraints.cell_name}")
        print(f"  Polygons: {len(constraints.polygons)}")
        print(f"  Dimensions: {constraints.total_width:.3f} x {constraints.total_height:.3f} um")

    def export_to_json(self, output_file: str, constraints: Optional[CellConstraints] = None):
        """
        Export constraints to JSON file

        Args:
            output_file: Output JSON file path
            constraints: CellConstraints object (if None, will extract)
        """
        if constraints is None:
            constraints = self.extract_constraints()

        # Convert to dict
        data = asdict(constraints)

        # Write JSON
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Exported constraints to: {output_file}")


class ConstraintsToGDS:
    """
    Regenerate GDS from constraint file

    Reads constraint file and generates GDS with potentially modified dimensions
    """

    def __init__(self, constraint_file: str):
        """
        Initialize from constraint file

        Args:
            constraint_file: Path to YAML or JSON constraint file
        """
        self.constraint_file = constraint_file

        # Detect format and load
        if constraint_file.endswith('.yaml') or constraint_file.endswith('.yml'):
            with open(constraint_file, 'r') as f:
                self.data = yaml.safe_load(f)
        elif constraint_file.endswith('.json'):
            with open(constraint_file, 'r') as f:
                self.data = json.load(f)
        else:
            raise ValueError("Constraint file must be .yaml, .yml, or .json")

    def generate_gds(self, output_file: str, units: Tuple[float, float] = (1e-6, 1e-9)):
        """
        Generate GDS from constraints

        Args:
            output_file: Output GDS file path
            units: (unit, precision) tuple for GDS file
        """
        # Create library
        lib = gdstk.Library(unit=units[0], precision=units[1])

        # Create cell
        cell_name = self.data['cell_name']
        cell = lib.new_cell(cell_name)

        # Create polygons from constraints
        for poly_data in self.data['polygons']:
            layer_num = poly_data['layer_num']
            datatype = poly_data['datatype']

            # Get position (could be from 'position' or computed from constraints)
            if 'position' in poly_data:
                x1 = poly_data['position']['x1']
                y1 = poly_data['position']['y1']
                x2 = poly_data['position']['x2']
                y2 = poly_data['position']['y2']
            else:
                # Use size if position not specified
                width = poly_data['size']['width']
                height = poly_data['size']['height']
                x1, y1 = 0, 0
                x2, y2 = width, height

            # Create rectangle polygon
            points = [
                (x1, y1),
                (x2, y1),
                (x2, y2),
                (x1, y2)
            ]

            poly = gdstk.Polygon(points, layer=layer_num, datatype=datatype)
            cell.add(poly)

        # Write GDS
        lib.write_gds(output_file)
        print(f"Generated GDS: {output_file}")
        print(f"  Cell: {cell_name}")
        print(f"  Polygons: {len(self.data['polygons'])}")


def convert_gds_to_constraints(gds_file: str, output_file: str,
                               cell_name: Optional[str] = None,
                               layer_map: Optional[Dict[int, str]] = None,
                               format: str = 'yaml'):
    """
    Convenience function to convert GDS to constraints

    Args:
        gds_file: Input GDS file
        output_file: Output constraint file
        cell_name: Cell to extract (None = first cell)
        layer_map: Layer number to name mapping
        format: Output format ('yaml' or 'json')
    """
    converter = GDSToConstraints(gds_file, cell_name)

    if layer_map:
        converter.set_layer_map(layer_map)

    constraints = converter.extract_constraints()

    if format == 'yaml':
        converter.export_to_yaml(output_file, constraints)
    elif format == 'json':
        converter.export_to_json(output_file, constraints)
    else:
        raise ValueError(f"Unknown format: {format}")

    return constraints


def regenerate_gds_from_constraints(constraint_file: str, output_gds: str):
    """
    Convenience function to regenerate GDS from constraints

    Args:
        constraint_file: Input constraint file (.yaml or .json)
        output_gds: Output GDS file
    """
    regenerator = ConstraintsToGDS(constraint_file)
    regenerator.generate_gds(output_gds)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("GDS to Constraint Format Converter")
        print()
        print("Usage:")
        print("  Convert GDS to constraints:")
        print("    python gds_to_constraints.py input.gds output.yaml [cell_name]")
        print()
        print("  Regenerate GDS from constraints:")
        print("    python gds_to_constraints.py --regenerate constraints.yaml output.gds")
        print()
        print("Examples:")
        print("  python gds_to_constraints.py inverter.gds inverter_constraints.yaml")
        print("  python gds_to_constraints.py --regenerate inverter_constraints.yaml inverter_new.gds")
        sys.exit(1)

    if sys.argv[1] == '--regenerate':
        # Regenerate mode
        constraint_file = sys.argv[2]
        output_gds = sys.argv[3]
        regenerate_gds_from_constraints(constraint_file, output_gds)
    else:
        # Convert mode
        gds_file = sys.argv[1]
        output_file = sys.argv[2]
        cell_name = sys.argv[3] if len(sys.argv) > 3 else None

        # Detect format from output file
        format = 'yaml' if output_file.endswith(('.yaml', '.yml')) else 'json'

        convert_gds_to_constraints(gds_file, output_file, cell_name, format=format)
