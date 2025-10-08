#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design Rule Checking (DRC) for layout validation

Provides validation of physical design rules including:
- Minimum spacing between polygons on same/different layers
- Minimum width/height for polygons
- Minimum area for polygons
- Overlap requirements between layers
- Enclosure rules
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class DRCRule:
    """
    Design rule specification

    Attributes:
        name: Rule name/identifier
        rule_type: Type of rule ('spacing', 'width', 'area', 'overlap', 'enclosure')
        layers: Tuple of layer names this rule applies to
        value: Numeric value for the rule (spacing, width, area, etc.)
        description: Human-readable description
    """
    name: str
    rule_type: str
    layers: Tuple[str, ...]
    value: float
    description: str


@dataclass
class DRCViolation:
    """
    Design rule violation report

    Attributes:
        rule: The violated rule
        objects: Objects involved in violation (polygon names)
        actual_value: Actual measured value
        location: (x, y) coordinate of violation
        severity: 'error' or 'warning'
        message: Detailed violation message
    """
    rule: DRCRule
    objects: List[str]
    actual_value: float
    location: Tuple[float, float]
    severity: str
    message: str


class DRCRuleSet:
    """
    Collection of design rules for a technology/process
    """

    def __init__(self, name: str = "default"):
        """
        Initialize DRC rule set

        Args:
            name: Rule set name (e.g., 'skywater130', 'tsmc180')
        """
        self.name = name
        self.rules: List[DRCRule] = []

    def add_rule(self, rule: DRCRule):
        """Add a design rule to the rule set"""
        self.rules.append(rule)

    def add_spacing_rule(self, layer1: str, layer2: str, min_spacing: float,
                        description: str = ""):
        """
        Add minimum spacing rule between layers

        Args:
            layer1: First layer name
            layer2: Second layer name (can be same as layer1)
            min_spacing: Minimum spacing in layout units
            description: Optional description
        """
        if not description:
            if layer1 == layer2:
                description = f"Minimum spacing for {layer1}"
            else:
                description = f"Minimum spacing between {layer1} and {layer2}"

        rule = DRCRule(
            name=f"spacing_{layer1}_{layer2}",
            rule_type='spacing',
            layers=(layer1, layer2),
            value=min_spacing,
            description=description
        )
        self.add_rule(rule)

    def add_width_rule(self, layer: str, min_width: float, description: str = ""):
        """
        Add minimum width rule for a layer

        Args:
            layer: Layer name
            min_width: Minimum width in layout units
            description: Optional description
        """
        if not description:
            description = f"Minimum width for {layer}"

        rule = DRCRule(
            name=f"width_{layer}",
            rule_type='width',
            layers=(layer,),
            value=min_width,
            description=description
        )
        self.add_rule(rule)

    def add_area_rule(self, layer: str, min_area: float, description: str = ""):
        """
        Add minimum area rule for a layer

        Args:
            layer: Layer name
            min_area: Minimum area in layout units squared
            description: Optional description
        """
        if not description:
            description = f"Minimum area for {layer}"

        rule = DRCRule(
            name=f"area_{layer}",
            rule_type='area',
            layers=(layer,),
            value=min_area,
            description=description
        )
        self.add_rule(rule)

    def add_overlap_rule(self, layer1: str, layer2: str, min_overlap: float,
                        description: str = ""):
        """
        Add minimum overlap requirement between layers

        Args:
            layer1: First layer name
            layer2: Second layer name
            min_overlap: Minimum overlap dimension
            description: Optional description
        """
        if not description:
            description = f"Minimum overlap between {layer1} and {layer2}"

        rule = DRCRule(
            name=f"overlap_{layer1}_{layer2}",
            rule_type='overlap',
            layers=(layer1, layer2),
            value=min_overlap,
            description=description
        )
        self.add_rule(rule)

    def add_enclosure_rule(self, outer_layer: str, inner_layer: str,
                          min_enclosure: float, description: str = ""):
        """
        Add enclosure rule (outer layer must enclose inner layer by minimum amount)

        Args:
            outer_layer: Enclosing layer
            inner_layer: Enclosed layer
            min_enclosure: Minimum enclosure distance
            description: Optional description
        """
        if not description:
            description = f"{outer_layer} must enclose {inner_layer} by {min_enclosure}"

        rule = DRCRule(
            name=f"enclosure_{outer_layer}_{inner_layer}",
            rule_type='enclosure',
            layers=(outer_layer, inner_layer),
            value=min_enclosure,
            description=description
        )
        self.add_rule(rule)


class DRCChecker:
    """
    Design Rule Checker - validates layouts against design rules
    """

    def __init__(self, rule_set: DRCRuleSet):
        """
        Initialize DRC checker

        Args:
            rule_set: DRCRuleSet to check against
        """
        self.rule_set = rule_set
        self.violations: List[DRCViolation] = []

    def check_cell(self, cell) -> List[DRCViolation]:
        """
        Check a Cell for DRC violations

        Args:
            cell: Cell object from gds_cell.py

        Returns:
            List of DRCViolation objects
        """
        self.violations = []

        # Get all polygons including from instances
        all_polygons = self._get_all_polygons_flat(cell)

        # Check each rule
        for rule in self.rule_set.rules:
            if rule.rule_type == 'spacing':
                self._check_spacing_rule(rule, all_polygons)
            elif rule.rule_type == 'width':
                self._check_width_rule(rule, all_polygons)
            elif rule.rule_type == 'area':
                self._check_area_rule(rule, all_polygons)
            elif rule.rule_type == 'overlap':
                self._check_overlap_rule(rule, all_polygons)
            elif rule.rule_type == 'enclosure':
                self._check_enclosure_rule(rule, all_polygons)

        return self.violations

    def _get_all_polygons_flat(self, cell, offset_x: float = 0, offset_y: float = 0) -> List[Tuple]:
        """
        Get all polygons with transformed coordinates (flattened hierarchy)

        Returns:
            List of (polygon_name, layer, x1, y1, x2, y2) tuples
        """
        polygons = []

        # Add polygons from this cell
        for poly in cell.polygons:
            if all(v is not None for v in poly.pos_list):
                x1, y1, x2, y2 = poly.pos_list
                polygons.append((
                    poly.name,
                    poly.layer,
                    x1 + offset_x,
                    y1 + offset_y,
                    x2 + offset_x,
                    y2 + offset_y
                ))

        # Recursively add polygons from instances
        for instance in cell.instances:
            if all(v is not None for v in instance.pos_list):
                inst_x1, inst_y1 = instance.pos_list[0], instance.pos_list[1]

                # Calculate offset for instance's contents
                if len(instance.cell.polygons) > 0:
                    cell_x1 = min(p.pos_list[0] for p in instance.cell.polygons
                                 if p.pos_list[0] is not None)
                    cell_y1 = min(p.pos_list[1] for p in instance.cell.polygons
                                 if p.pos_list[1] is not None)
                    child_offset_x = inst_x1 + offset_x - cell_x1
                    child_offset_y = inst_y1 + offset_y - cell_y1
                else:
                    child_offset_x = inst_x1 + offset_x
                    child_offset_y = inst_y1 + offset_y

                # Recursively get polygons from instance
                polygons.extend(
                    self._get_all_polygons_flat(instance.cell, child_offset_x, child_offset_y)
                )

        return polygons

    def _check_spacing_rule(self, rule: DRCRule, polygons: List[Tuple]):
        """Check minimum spacing between polygons"""
        layer1, layer2 = rule.layers
        min_spacing = rule.value

        # Get polygons on relevant layers
        polys1 = [p for p in polygons if p[1] == layer1]
        polys2 = [p for p in polygons if p[1] == layer2]

        # Check spacing between all pairs
        for i, p1 in enumerate(polys1):
            name1, _, x1_1, y1_1, x2_1, y2_1 = p1

            # For same layer, avoid checking polygon against itself
            start_j = i + 1 if layer1 == layer2 else 0
            compare_list = polys2[start_j:] if layer1 == layer2 else polys2

            for p2 in compare_list:
                name2, _, x1_2, y1_2, x2_2, y2_2 = p2

                # Skip if same polygon
                if p1 == p2:
                    continue

                # Calculate spacing (edge to edge distance)
                spacing = self._calculate_spacing(
                    x1_1, y1_1, x2_1, y2_1,
                    x1_2, y1_2, x2_2, y2_2
                )

                # Check if violates minimum spacing
                if spacing < min_spacing:
                    # Find violation location (midpoint between closest edges)
                    location = self._find_closest_point(
                        x1_1, y1_1, x2_1, y2_1,
                        x1_2, y1_2, x2_2, y2_2
                    )

                    violation = DRCViolation(
                        rule=rule,
                        objects=[name1, name2],
                        actual_value=spacing,
                        location=location,
                        severity='error',
                        message=f"Spacing violation: {name1} and {name2} have spacing "
                               f"{spacing:.3f} < {min_spacing:.3f} (required)"
                    )
                    self.violations.append(violation)

    def _check_width_rule(self, rule: DRCRule, polygons: List[Tuple]):
        """Check minimum width for polygons"""
        layer = rule.layers[0]
        min_width = rule.value

        # Check all polygons on this layer
        for poly in polygons:
            name, poly_layer, x1, y1, x2, y2 = poly

            if poly_layer != layer:
                continue

            width = x2 - x1
            height = y2 - y1
            min_dim = min(width, height)

            if min_dim < min_width:
                location = ((x1 + x2) / 2, (y1 + y2) / 2)

                violation = DRCViolation(
                    rule=rule,
                    objects=[name],
                    actual_value=min_dim,
                    location=location,
                    severity='error',
                    message=f"Width violation: {name} has min dimension {min_dim:.3f} "
                           f"< {min_width:.3f} (required)"
                )
                self.violations.append(violation)

    def _check_area_rule(self, rule: DRCRule, polygons: List[Tuple]):
        """Check minimum area for polygons"""
        layer = rule.layers[0]
        min_area = rule.value

        for poly in polygons:
            name, poly_layer, x1, y1, x2, y2 = poly

            if poly_layer != layer:
                continue

            area = (x2 - x1) * (y2 - y1)

            if area < min_area:
                location = ((x1 + x2) / 2, (y1 + y2) / 2)

                violation = DRCViolation(
                    rule=rule,
                    objects=[name],
                    actual_value=area,
                    location=location,
                    severity='error',
                    message=f"Area violation: {name} has area {area:.3f} "
                           f"< {min_area:.3f} (required)"
                )
                self.violations.append(violation)

    def _check_overlap_rule(self, rule: DRCRule, polygons: List[Tuple]):
        """Check minimum overlap between layers"""
        layer1, layer2 = rule.layers
        min_overlap = rule.value

        polys1 = [p for p in polygons if p[1] == layer1]
        polys2 = [p for p in polygons if p[1] == layer2]

        # Check each polygon on layer1 has sufficient overlap with at least one on layer2
        for p1 in polys1:
            name1, _, x1_1, y1_1, x2_1, y2_1 = p1
            max_overlap = 0
            overlapping_name = None

            for p2 in polys2:
                name2, _, x1_2, y1_2, x2_2, y2_2 = p2

                # Calculate overlap
                overlap_x = max(0, min(x2_1, x2_2) - max(x1_1, x1_2))
                overlap_y = max(0, min(y2_1, y2_2) - max(y1_1, y1_2))
                overlap = min(overlap_x, overlap_y)

                if overlap > max_overlap:
                    max_overlap = overlap
                    overlapping_name = name2

            if max_overlap < min_overlap and overlapping_name is not None:
                location = ((x1_1 + x2_1) / 2, (y1_1 + y2_1) / 2)

                violation = DRCViolation(
                    rule=rule,
                    objects=[name1, overlapping_name],
                    actual_value=max_overlap,
                    location=location,
                    severity='warning',
                    message=f"Overlap violation: {name1} and {overlapping_name} have "
                           f"overlap {max_overlap:.3f} < {min_overlap:.3f} (required)"
                )
                self.violations.append(violation)

    def _check_enclosure_rule(self, rule: DRCRule, polygons: List[Tuple]):
        """Check enclosure requirements"""
        outer_layer, inner_layer = rule.layers
        min_enclosure = rule.value

        outer_polys = [p for p in polygons if p[1] == outer_layer]
        inner_polys = [p for p in polygons if p[1] == inner_layer]

        # Check each inner polygon is properly enclosed by outer polygons
        for inner in inner_polys:
            name_inner, _, ix1, iy1, ix2, iy2 = inner

            for outer in outer_polys:
                name_outer, _, ox1, oy1, ox2, oy2 = outer

                # Check if they overlap
                if (ix1 < ox2 and ix2 > ox1 and iy1 < oy2 and iy2 > oy1):
                    # Calculate enclosure distances (negative if inner extends beyond outer)
                    enc_left = ix1 - ox1
                    enc_right = ox2 - ix2
                    enc_bottom = iy1 - oy1
                    enc_top = oy2 - iy2

                    min_enc = min(enc_left, enc_right, enc_bottom, enc_top)

                    if min_enc < min_enclosure:
                        location = ((ix1 + ix2) / 2, (iy1 + iy2) / 2)

                        violation = DRCViolation(
                            rule=rule,
                            objects=[name_outer, name_inner],
                            actual_value=min_enc,
                            location=location,
                            severity='error',
                            message=f"Enclosure violation: {name_outer} does not enclose "
                                   f"{name_inner} by {min_enclosure:.3f} (has {min_enc:.3f})"
                        )
                        self.violations.append(violation)

    def _calculate_spacing(self, x1_1, y1_1, x2_1, y2_1, x1_2, y1_2, x2_2, y2_2) -> float:
        """Calculate minimum edge-to-edge spacing between two rectangles"""
        # Check if rectangles overlap
        if not (x2_1 < x1_2 or x2_2 < x1_1 or y2_1 < y1_2 or y2_2 < y1_1):
            # Overlapping - spacing is negative (or zero)
            return 0.0

        # Calculate horizontal and vertical spacing
        if x2_1 < x1_2:
            dx = x1_2 - x2_1
        elif x2_2 < x1_1:
            dx = x1_1 - x2_2
        else:
            dx = 0

        if y2_1 < y1_2:
            dy = y1_2 - y2_1
        elif y2_2 < y1_1:
            dy = y1_1 - y2_2
        else:
            dy = 0

        # If rectangles are diagonally separated, use Euclidean distance
        if dx > 0 and dy > 0:
            return math.sqrt(dx*dx + dy*dy)
        else:
            return max(dx, dy)

    def _find_closest_point(self, x1_1, y1_1, x2_1, y2_1,
                           x1_2, y1_2, x2_2, y2_2) -> Tuple[float, float]:
        """Find midpoint between closest edges of two rectangles"""
        # Center points
        cx1 = (x1_1 + x2_1) / 2
        cy1 = (y1_1 + y2_1) / 2
        cx2 = (x1_2 + x2_2) / 2
        cy2 = (y1_2 + y2_2) / 2

        # Simple midpoint between centers
        return ((cx1 + cx2) / 2, (cy1 + cy2) / 2)

    def print_violations(self):
        """Print all violations in human-readable format"""
        if not self.violations:
            print("✓ No DRC violations found!")
            return

        print(f"\n{'='*70}")
        print(f"DRC VIOLATIONS FOUND: {len(self.violations)}")
        print(f"{'='*70}\n")

        errors = [v for v in self.violations if v.severity == 'error']
        warnings = [v for v in self.violations if v.severity == 'warning']

        if errors:
            print(f"ERRORS ({len(errors)}):")
            print("-" * 70)
            for i, v in enumerate(errors, 1):
                print(f"{i}. {v.message}")
                print(f"   Rule: {v.rule.description}")
                print(f"   Location: ({v.location[0]:.2f}, {v.location[1]:.2f})")
                print()

        if warnings:
            print(f"WARNINGS ({len(warnings)}):")
            print("-" * 70)
            for i, v in enumerate(warnings, 1):
                print(f"{i}. {v.message}")
                print(f"   Rule: {v.rule.description}")
                print(f"   Location: ({v.location[0]:.2f}, {v.location[1]:.2f})")
                print()


def create_default_rules() -> DRCRuleSet:
    """
    Create a default/example DRC rule set

    Returns:
        DRCRuleSet with typical rules for demonstration
    """
    rules = DRCRuleSet("default_generic")

    # Spacing rules
    rules.add_spacing_rule('metal1', 'metal1', 3.0, "Metal1 to metal1 spacing")
    rules.add_spacing_rule('metal2', 'metal2', 3.0, "Metal2 to metal2 spacing")
    rules.add_spacing_rule('poly', 'poly', 2.0, "Poly to poly spacing")
    rules.add_spacing_rule('diff', 'diff', 2.5, "Diffusion to diffusion spacing")

    # Width rules
    rules.add_width_rule('metal1', 2.0, "Minimum metal1 width")
    rules.add_width_rule('metal2', 2.0, "Minimum metal2 width")
    rules.add_width_rule('poly', 1.5, "Minimum poly width")
    rules.add_width_rule('diff', 2.0, "Minimum diffusion width")

    # Area rules
    rules.add_area_rule('metal1', 20.0, "Minimum metal1 area")
    rules.add_area_rule('metal2', 20.0, "Minimum metal2 area")

    return rules
