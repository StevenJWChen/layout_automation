#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRC (Design Rule Check) violation auto-fix module

Automatically fixes spacing, width, and other design rule violations in Cell layouts
"""

from typing import List, Dict, Set, Tuple
from layout_automation.drc_checker import DRCViolation
from layout_automation.tech_file import DRCRuleSet


class DRCFixer:
    """Auto-fix DRC violations using constraints"""

    def __init__(self, drc_rules: DRCRuleSet):
        """
        Initialize DRC fixer

        Args:
            drc_rules: DRC rule set to use for fixing
        """
        self.drc_rules = drc_rules
        self.fixed_count = 0
        self.unfixed_count = 0

    def fix_violations(self, cell, violations: List[DRCViolation], max_iterations: int = 5) -> Tuple[int, int]:
        """
        Automatically fix DRC violations in a cell layout

        Args:
            cell: Cell instance to fix
            violations: List of DRCViolation objects to fix
            max_iterations: Maximum number of fix-check iterations

        Returns:
            Tuple of (fixed_count, unfixed_count)
        """
        self.fixed_count = 0
        self.unfixed_count = 0

        if not violations:
            print("No violations to fix")
            return (0, 0)

        print(f"\nAttempting to fix {len(violations)} violations...")

        # Group violations by type
        width_violations = [v for v in violations if v.rule_type == 'minWidth']
        spacing_violations = [v for v in violations if v.rule_type == 'minSpacing']

        # Fix width violations
        if width_violations:
            print(f"\nFixing {len(width_violations)} width violations...")
            self._fix_width_violations(width_violations)

        # Fix spacing violations
        if spacing_violations:
            print(f"\nFixing {len(spacing_violations)} spacing violations...")
            self._fix_spacing_violations(cell, spacing_violations)

        # Re-solve the layout if we added constraints
        if hasattr(cell, 'solver') and len(cell.constraints) > 0:
            print("\nRe-solving layout with new constraints...")
            try:
                if cell.solver():
                    print("✓ Layout solved successfully")
                else:
                    print("✗ Warning: Layout solver did not converge")
            except Exception as e:
                print(f"✗ Error during solving: {e}")

        print(f"\nFix Summary:")
        print(f"  Attempted fixes: {self.fixed_count}")
        print(f"  Could not fix: {self.unfixed_count}")

        return (self.fixed_count, self.unfixed_count)

    def _fix_width_violations(self, violations: List[DRCViolation]):
        """
        Fix width violations by resizing cells

        Args:
            violations: List of width violations
        """
        for violation in violations:
            cell = violation.cell1
            required = violation.required
            actual = violation.value

            if cell.is_leaf and cell.pos_list and all(p is not None for p in cell.pos_list):
                x1, y1, x2, y2 = cell.pos_list
                width = abs(x2 - x1)
                height = abs(y2 - y1)

                # Check which dimension needs fixing
                if width < required:
                    # Expand width to meet requirement
                    expansion = required - width
                    cell.pos_list[2] = x2 + expansion  # Expand x2
                    print(f"  ✓ Fixed width of {cell.name}: {width:.3f} -> {required:.3f}")
                    self.fixed_count += 1

                elif height < required:
                    # Expand height to meet requirement
                    expansion = required - height
                    cell.pos_list[3] = y2 + expansion  # Expand y2
                    print(f"  ✓ Fixed height of {cell.name}: {height:.3f} -> {required:.3f}")
                    self.fixed_count += 1
            else:
                print(f"  ✗ Cannot fix {cell.name}: not a positioned leaf cell")
                self.unfixed_count += 1

    def _fix_spacing_violations(self, parent_cell, violations: List[DRCViolation]):
        """
        Fix spacing violations by adding constraints or moving cells

        Args:
            parent_cell: Parent cell containing the violating children
            violations: List of spacing violations
        """
        # Build a map of cells to their parent
        cell_to_parent = self._build_cell_parent_map(parent_cell)

        for violation in violations:
            cell1 = violation.cell1
            cell2 = violation.cell2
            required = violation.required
            actual = violation.value

            # Find common parent
            parent = self._find_common_parent(cell1, cell2, cell_to_parent, parent_cell)

            if parent is None:
                print(f"  ✗ Cannot fix spacing between {cell1.name} and {cell2.name}: no common parent")
                self.unfixed_count += 1
                continue

            # Check if cells are direct children of the parent
            if cell1 in parent.children and cell2 in parent.children:
                # Calculate the gap needed
                gap = required - actual

                # Determine direction of separation
                if all(p is not None for p in cell1.pos_list) and all(p is not None for p in cell2.pos_list):
                    x1_1, y1_1, x2_1, y2_1 = cell1.pos_list
                    x1_2, y1_2, x2_2, y2_2 = cell2.pos_list

                    # Check if primarily separated in X or Y direction
                    x_sep = min(abs(x2_1 - x1_2), abs(x2_2 - x1_1))
                    y_sep = min(abs(y2_1 - y1_2), abs(y2_2 - y1_1))

                    if x_sep <= y_sep:
                        # Primarily X-direction spacing issue
                        if x2_1 < x1_2:
                            # cell1 is to the left of cell2
                            constraint_str = f'sx2+{required}=ox1'
                        else:
                            # cell2 is to the left of cell1
                            constraint_str = f'ox2+{required}=sx1'

                        # Add constraint to parent
                        try:
                            parent.constrain(cell1, constraint_str, cell2)
                            print(f"  ✓ Added spacing constraint: {cell1.name} <-> {cell2.name} (gap: {required:.3f})")
                            self.fixed_count += 1
                        except Exception as e:
                            print(f"  ✗ Failed to add constraint: {e}")
                            self.unfixed_count += 1
                    else:
                        # Primarily Y-direction spacing issue
                        if y2_1 < y1_2:
                            # cell1 is below cell2
                            constraint_str = f'sy2+{required}=oy1'
                        else:
                            # cell2 is below cell1
                            constraint_str = f'oy2+{required}=sy1'

                        # Add constraint to parent
                        try:
                            parent.constrain(cell1, constraint_str, cell2)
                            print(f"  ✓ Added spacing constraint: {cell1.name} <-> {cell2.name} (gap: {required:.3f})")
                            self.fixed_count += 1
                        except Exception as e:
                            print(f"  ✗ Failed to add constraint: {e}")
                            self.unfixed_count += 1
                else:
                    print(f"  ✗ Cannot fix spacing: cells don't have valid positions")
                    self.unfixed_count += 1
            else:
                # Cells are in different hierarchy levels - try simple position adjustment
                if self._try_position_adjustment(cell1, cell2, required - actual):
                    print(f"  ✓ Fixed spacing by position adjustment: {cell1.name} <-> {cell2.name}")
                    self.fixed_count += 1
                else:
                    print(f"  ✗ Cannot fix spacing: cells in different hierarchy levels")
                    self.unfixed_count += 1

    def _build_cell_parent_map(self, root_cell, parent_map=None, parent=None):
        """
        Build a map from each cell to its parent

        Args:
            root_cell: Root cell to traverse
            parent_map: Dictionary to populate (created if None)
            parent: Parent of current cell

        Returns:
            Dictionary mapping cells to their parents
        """
        if parent_map is None:
            parent_map = {}

        parent_map[root_cell] = parent

        if not root_cell.is_leaf:
            for child in root_cell.children:
                self._build_cell_parent_map(child, parent_map, root_cell)

        return parent_map

    def _find_common_parent(self, cell1, cell2, cell_to_parent, root):
        """
        Find the lowest common parent of two cells

        Args:
            cell1: First cell
            cell2: Second cell
            cell_to_parent: Map from cells to parents
            root: Root cell

        Returns:
            Common parent cell or None
        """
        # Get ancestors of cell1
        ancestors1 = set()
        current = cell1
        while current is not None:
            ancestors1.add(current)
            current = cell_to_parent.get(current)

        # Find first common ancestor with cell2
        current = cell2
        while current is not None:
            if current in ancestors1:
                return current
            current = cell_to_parent.get(current)

        return None

    def _try_position_adjustment(self, cell1, cell2, gap_needed: float) -> bool:
        """
        Try to fix spacing by adjusting positions directly

        Args:
            cell1: First cell
            cell2: Second cell
            gap_needed: Additional gap needed

        Returns:
            True if successfully adjusted, False otherwise
        """
        # Only works if both cells have valid positions
        if not (all(p is not None for p in cell1.pos_list) and
                all(p is not None for p in cell2.pos_list)):
            return False

        x1_1, y1_1, x2_1, y2_1 = cell1.pos_list
        x1_2, y1_2, x2_2, y2_2 = cell2.pos_list

        # Determine primary separation direction
        x_sep = min(abs(x2_1 - x1_2), abs(x2_2 - x1_1))
        y_sep = min(abs(y2_1 - y1_2), abs(y2_2 - y1_1))

        if x_sep <= y_sep:
            # Move in X direction
            if x2_1 < x1_2:
                # Move cell2 to the right
                offset = gap_needed / 2
                cell2.pos_list[0] += offset
                cell2.pos_list[2] += offset
            else:
                # Move cell1 to the right
                offset = gap_needed / 2
                cell1.pos_list[0] += offset
                cell1.pos_list[2] += offset
        else:
            # Move in Y direction
            if y2_1 < y1_2:
                # Move cell2 up
                offset = gap_needed / 2
                cell2.pos_list[1] += offset
                cell2.pos_list[3] += offset
            else:
                # Move cell1 up
                offset = gap_needed / 2
                cell1.pos_list[1] += offset
                cell1.pos_list[3] += offset

        return True

    def create_fix_constraints(self, cell) -> List[str]:
        """
        Create a list of constraint strings that would fix current violations

        Args:
            cell: Cell to analyze

        Returns:
            List of constraint strings
        """
        constraints = []

        # This is a helper function for manual constraint generation
        # Can be extended to provide constraint suggestions without applying them

        return constraints
