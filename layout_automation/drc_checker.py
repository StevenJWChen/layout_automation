#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRC (Design Rule Check) violation detection module

Detects spacing, width, and other design rule violations in Cell layouts
"""

from typing import List, Tuple, Optional
from layout_automation.tech_file import DRCRuleSet


class DRCViolation:
    """Represents a single DRC violation"""

    def __init__(self, rule_type: str, layer: str, message: str,
                 cell1=None, cell2=None, value: float = 0.0, required: float = 0.0):
        """
        Initialize DRC violation

        Args:
            rule_type: Type of rule violated (minWidth, minSpacing, etc.)
            layer: Layer name where violation occurs
            message: Human-readable description
            cell1: First cell involved in violation
            cell2: Second cell involved in violation (for spacing violations)
            value: Actual measured value
            required: Required value per DRC rules
        """
        self.rule_type = rule_type
        self.layer = layer
        self.message = message
        self.cell1 = cell1
        self.cell2 = cell2
        self.value = value
        self.required = required

    def __repr__(self):
        return f"DRCViolation({self.rule_type}, {self.layer}, {self.message})"

    def __str__(self):
        return self.message


class DRCChecker:
    """DRC violation checker for Cell layouts"""

    def __init__(self, drc_rules: DRCRuleSet):
        """
        Initialize DRC checker

        Args:
            drc_rules: DRC rule set to check against
        """
        self.drc_rules = drc_rules
        self.violations: List[DRCViolation] = []

    def check_layout(self, cell) -> List[DRCViolation]:
        """
        Check a cell layout for DRC violations

        Args:
            cell: Cell instance to check

        Returns:
            List of DRCViolation objects
        """
        self.violations = []

        # Get all leaf cells (actual geometry)
        leaf_cells = self._get_all_leaf_cells(cell)

        # Check width rules
        self._check_width_violations(leaf_cells)

        # Check spacing rules
        self._check_spacing_violations(leaf_cells)

        return self.violations

    def _get_all_leaf_cells(self, cell, parent_offset=(0, 0)) -> List[Tuple]:
        """
        Recursively get all leaf cells with absolute positions

        Args:
            cell: Cell to traverse
            parent_offset: Parent's position offset

        Returns:
            List of tuples: (leaf_cell, absolute_x1, absolute_y1, absolute_x2, absolute_y2)
        """
        leaf_cells = []

        if cell.is_leaf:
            # This is a leaf cell with actual geometry
            if all(pos is not None for pos in cell.pos_list):
                x1, y1, x2, y2 = cell.pos_list
                abs_x1 = x1 + parent_offset[0]
                abs_y1 = y1 + parent_offset[1]
                abs_x2 = x2 + parent_offset[0]
                abs_y2 = y2 + parent_offset[1]
                leaf_cells.append((cell, abs_x1, abs_y1, abs_x2, abs_y2))
        else:
            # Recurse into children
            # Calculate this cell's position offset
            if all(pos is not None for pos in cell.pos_list[:2]):
                current_offset = (
                    parent_offset[0] + (cell.pos_list[0] or 0),
                    parent_offset[1] + (cell.pos_list[1] or 0)
                )
            else:
                current_offset = parent_offset

            for child in cell.children:
                leaf_cells.extend(self._get_all_leaf_cells(child, current_offset))

        return leaf_cells

    def _check_width_violations(self, leaf_cells: List[Tuple]):
        """
        Check for minimum width violations

        Args:
            leaf_cells: List of (cell, x1, y1, x2, y2) tuples
        """
        for cell, x1, y1, x2, y2 in leaf_cells:
            layer = cell.layer_name
            min_width = self.drc_rules.get_min_width(layer)

            if min_width is None:
                continue

            # Calculate actual width and height
            width = abs(x2 - x1)
            height = abs(y2 - y1)

            # Check width violation
            if width < min_width:
                violation = DRCViolation(
                    rule_type='minWidth',
                    layer=layer,
                    message=f"Width violation on {layer}: {cell.name} has width {width:.3f} < {min_width} (required)",
                    cell1=cell,
                    value=width,
                    required=min_width
                )
                self.violations.append(violation)

            # Check height violation (treat as width in vertical direction)
            if height < min_width:
                violation = DRCViolation(
                    rule_type='minWidth',
                    layer=layer,
                    message=f"Height violation on {layer}: {cell.name} has height {height:.3f} < {min_width} (required)",
                    cell1=cell,
                    value=height,
                    required=min_width
                )
                self.violations.append(violation)

    def _check_spacing_violations(self, leaf_cells: List[Tuple]):
        """
        Check for minimum spacing violations

        Args:
            leaf_cells: List of (cell, x1, y1, x2, y2) tuples
        """
        # Check all pairs of cells
        for i, (cell1, x1_1, y1_1, x2_1, y2_1) in enumerate(leaf_cells):
            for j, (cell2, x1_2, y1_2, x2_2, y2_2) in enumerate(leaf_cells):
                if i >= j:
                    continue  # Skip self-pairs and duplicate pairs

                layer1 = cell1.layer_name
                layer2 = cell2.layer_name

                # Get spacing requirement
                if layer1 == layer2:
                    # Same layer spacing
                    min_spacing = self.drc_rules.get_min_spacing(layer1)
                else:
                    # Different layer spacing
                    min_spacing = self.drc_rules.get_layer_pair_spacing(layer1, layer2)

                if min_spacing is None:
                    continue

                # Calculate actual spacing between the two rectangles
                spacing = self._calculate_spacing(x1_1, y1_1, x2_1, y2_1,
                                                   x1_2, y1_2, x2_2, y2_2)

                if spacing is not None and spacing < min_spacing:
                    if layer1 == layer2:
                        violation = DRCViolation(
                            rule_type='minSpacing',
                            layer=layer1,
                            message=f"Spacing violation on {layer1}: {cell1.name} and {cell2.name} have spacing {spacing:.3f} < {min_spacing} (required)",
                            cell1=cell1,
                            cell2=cell2,
                            value=spacing,
                            required=min_spacing
                        )
                    else:
                        violation = DRCViolation(
                            rule_type='minSpacing',
                            layer=f"{layer1}/{layer2}",
                            message=f"Spacing violation between {layer1} and {layer2}: {cell1.name} and {cell2.name} have spacing {spacing:.3f} < {min_spacing} (required)",
                            cell1=cell1,
                            cell2=cell2,
                            value=spacing,
                            required=min_spacing
                        )
                    self.violations.append(violation)

    def _calculate_spacing(self, x1_1: float, y1_1: float, x2_1: float, y2_1: float,
                           x1_2: float, y1_2: float, x2_2: float, y2_2: float) -> Optional[float]:
        """
        Calculate minimum spacing between two rectangles

        Args:
            x1_1, y1_1, x2_1, y2_1: First rectangle coordinates
            x1_2, y1_2, x2_2, y2_2: Second rectangle coordinates

        Returns:
            Minimum spacing distance, or None if rectangles overlap
        """
        # Normalize coordinates (ensure x1 < x2 and y1 < y2)
        x1_1, x2_1 = min(x1_1, x2_1), max(x1_1, x2_1)
        y1_1, y2_1 = min(y1_1, y2_1), max(y1_1, y2_1)
        x1_2, x2_2 = min(x1_2, x2_2), max(x1_2, x2_2)
        y1_2, y2_2 = min(y1_2, y2_2), max(y1_2, y2_2)

        # Check for overlap or adjacency
        x_overlap = not (x2_1 <= x1_2 or x2_2 <= x1_1)
        y_overlap = not (y2_1 <= y1_2 or y2_2 <= y1_1)

        # If rectangles overlap, spacing is 0 (violation)
        if x_overlap and y_overlap:
            return 0.0

        # Calculate spacing based on relative positions
        if not x_overlap:
            # Rectangles are separated horizontally
            if x2_1 <= x1_2:
                x_spacing = x1_2 - x2_1
            else:
                x_spacing = x1_1 - x2_2
        else:
            x_spacing = 0.0

        if not y_overlap:
            # Rectangles are separated vertically
            if y2_1 <= y1_2:
                y_spacing = y1_2 - y2_1
            else:
                y_spacing = y1_1 - y2_2
        else:
            y_spacing = 0.0

        # Return minimum spacing (Manhattan distance)
        # If separated in only one direction, use that spacing
        # If separated in both directions, use minimum of the two
        if x_spacing > 0 and y_spacing > 0:
            # Separated diagonally - use minimum
            return min(x_spacing, y_spacing)
        else:
            # Separated in one direction only
            return max(x_spacing, y_spacing)

    def print_violations(self):
        """Print all violations to console"""
        if not self.violations:
            print("\n✓ No DRC violations found!")
            return

        print(f"\n✗ Found {len(self.violations)} DRC violation(s):")
        print("-" * 80)

        # Group by type
        width_violations = [v for v in self.violations if v.rule_type == 'minWidth']
        spacing_violations = [v for v in self.violations if v.rule_type == 'minSpacing']

        if width_violations:
            print(f"\nWidth Violations ({len(width_violations)}):")
            for v in width_violations:
                print(f"  • {v.message}")

        if spacing_violations:
            print(f"\nSpacing Violations ({len(spacing_violations)}):")
            for v in spacing_violations:
                print(f"  • {v.message}")

        print("-" * 80)

    def export_violations_report(self, filepath: str):
        """
        Export violations to a text report file

        Args:
            filepath: Path to output report file
        """
        with open(filepath, 'w') as f:
            f.write("DRC Violation Report\n")
            f.write("=" * 80 + "\n\n")

            if not self.violations:
                f.write("✓ No DRC violations found!\n")
                return

            f.write(f"Total Violations: {len(self.violations)}\n\n")

            # Group by type
            width_violations = [v for v in self.violations if v.rule_type == 'minWidth']
            spacing_violations = [v for v in self.violations if v.rule_type == 'minSpacing']

            if width_violations:
                f.write(f"Width Violations ({len(width_violations)}):\n")
                f.write("-" * 80 + "\n")
                for v in width_violations:
                    f.write(f"  Layer: {v.layer}\n")
                    f.write(f"  Cell: {v.cell1.name}\n")
                    f.write(f"  Actual: {v.value:.3f}\n")
                    f.write(f"  Required: {v.required:.3f}\n")
                    f.write(f"  Message: {v.message}\n\n")

            if spacing_violations:
                f.write(f"\nSpacing Violations ({len(spacing_violations)}):\n")
                f.write("-" * 80 + "\n")
                for v in spacing_violations:
                    f.write(f"  Layer: {v.layer}\n")
                    f.write(f"  Cell 1: {v.cell1.name}\n")
                    f.write(f"  Cell 2: {v.cell2.name}\n")
                    f.write(f"  Actual: {v.value:.3f}\n")
                    f.write(f"  Required: {v.required:.3f}\n")
                    f.write(f"  Message: {v.message}\n\n")

        print(f"[OK] Exported DRC report to {filepath}")
