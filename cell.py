#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell class for constraint-based layout automation
Supports hierarchical cell instances with constraint solving using Z3
"""

from __future__ import annotations
import re
import copy as copy_module
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from z3 import *


class Cell:
    """
    Hierarchical cell class with constraint-based positioning

    Attributes:
        name (str): Cell instance name
        children (list): List of child Cell instances or layer names
        pos_list (list): Position [x1, y1, x2, y2]
        constraints (list): List of constraint tuples (self_cell, constraint_str, other_cell)
        is_leaf (bool): True if this is a leaf cell (layer)
        layer_name (str): Layer name if this is a leaf cell
    """

    def __init__(self, name: str, *args):
        """
        Initialize Cell instance

        Args:
            name: Cell instance name
            *args: Variable number of Cell instances or layer name string
        """
        self.name = name
        self.children = []
        self.pos_list = [None, None, None, None]  # [x1, y1, x2, y2]
        self.constraints = []
        self.is_leaf = False
        self.layer_name = None
        self._z3_vars = None  # Cache for Z3 variables

        # Parse arguments
        for arg in args:
            if isinstance(arg, str):
                # String argument means this is a leaf cell with a layer name
                self.is_leaf = True
                self.layer_name = arg
            elif isinstance(arg, Cell):
                self.children.append(arg)
            elif isinstance(arg, list):
                # List of Cell instances
                self.children.extend([c for c in arg if isinstance(c, Cell)])
            else:
                raise TypeError(f"Invalid argument type: {type(arg)}")

    def add_instance(self, instances: Union['Cell', List['Cell']]):
        """
        Add child cell instance(s)

        Args:
            instances: Single Cell instance or list of Cell instances
        """
        if isinstance(instances, Cell):
            self.children.append(instances)
        elif isinstance(instances, list):
            self.children.extend([c for c in instances if isinstance(c, Cell)])
        else:
            raise TypeError("Argument must be Cell instance or list of Cell instances")

    def constrain(self, cell1: 'Cell', constraint_str: str, cell2: 'Cell'):
        """
        Add constraint between two cells

        Args:
            cell1: First cell (uses 's' prefix in constraint string)
            cell2: Second cell (uses 'o' prefix in constraint string)
            constraint_str: Constraint string, e.g., 'sx1<ox2+3, sy2+5<oy1'
        """
        self.constraints.append((cell1, constraint_str, cell2))

    def _get_z3_vars(self) -> Tuple[Real, Real, Real, Real]:
        """
        Get or create Z3 variables for this cell's position

        Returns:
            Tuple of Z3 Real variables (x1, y1, x2, y2)
        """
        if self._z3_vars is None:
            # Use object id to ensure uniqueness across copied instances
            unique_id = id(self)
            self._z3_vars = (
                Real(f'{self.name}_{unique_id}_x1'),
                Real(f'{self.name}_{unique_id}_y1'),
                Real(f'{self.name}_{unique_id}_x2'),
                Real(f'{self.name}_{unique_id}_y2')
            )
        return self._z3_vars

    def _parse_constraint(self, constraint_str: str, cell1: 'Cell', cell2: 'Cell') -> List:
        """
        Parse constraint string into Z3 constraints

        Args:
            constraint_str: Constraint string like 'sx1<ox2+3, sy2+5<oy1'
            cell1: Cell mapped to 's' prefix
            cell2: Cell mapped to 'o' prefix

        Returns:
            List of Z3 constraint expressions
        """
        z3_constraints = []

        # Get Z3 variables for both cells
        s_vars = cell1._get_z3_vars()
        o_vars = cell2._get_z3_vars()

        # Map variable names to Z3 variables
        var_map = {
            'sx1': s_vars[0], 'sy1': s_vars[1], 'sx2': s_vars[2], 'sy2': s_vars[3],
            'ox1': o_vars[0], 'oy1': o_vars[1], 'ox2': o_vars[2], 'oy2': o_vars[3]
        }

        # Split by comma to get individual constraints
        constraints = [c.strip() for c in constraint_str.split(',')]

        for constraint in constraints:
            # Parse operators: <=, >=, <, >, =
            operator = None
            for op in ['<=', '>=', '<', '>', '=']:
                if op in constraint:
                    operator = op
                    break

            if operator is None:
                raise ValueError(f"No valid operator found in constraint: {constraint}")

            # Split by operator
            left, right = constraint.split(operator, 1)
            left = left.strip()
            right = right.strip()

            # Parse expressions (supports +, -, *, and numbers)
            left_expr = self._parse_expression(left, var_map)
            right_expr = self._parse_expression(right, var_map)

            # Create Z3 constraint
            if operator == '<':
                z3_constraints.append(left_expr < right_expr)
            elif operator == '>':
                z3_constraints.append(left_expr > right_expr)
            elif operator == '<=':
                z3_constraints.append(left_expr <= right_expr)
            elif operator == '>=':
                z3_constraints.append(left_expr >= right_expr)
            elif operator == '=':
                z3_constraints.append(left_expr == right_expr)

        return z3_constraints

    def _parse_expression(self, expr_str: str, var_map: Dict[str, Real]) -> ArithRef:
        """
        Parse an arithmetic expression string into Z3 expression

        Args:
            expr_str: Expression string like 'sx1+5' or 'ox2*2-3'
            var_map: Mapping of variable names to Z3 variables

        Returns:
            Z3 arithmetic expression
        """
        # Tokenize the expression
        # Support: variables (sx1, oy2, etc.), numbers, +, -, *, (, )
        tokens = re.findall(r'[so][xy][12]|\d+\.?\d*|[+\-*/()]', expr_str)

        # Build Z3 expression using simple recursive descent or stack-based evaluation
        # For simplicity, we'll use eval with a custom namespace (careful approach)
        # Replace variable names with Z3 variables

        expr_for_eval = expr_str
        for var_name, z3_var in var_map.items():
            expr_for_eval = re.sub(r'\b' + var_name + r'\b', f'var_map["{var_name}"]', expr_for_eval)

        # Evaluate in safe namespace
        try:
            result = eval(expr_for_eval, {"__builtins__": {}}, {"var_map": var_map})
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse expression '{expr_str}': {e}")

    def solver(self, fix_leaf_positions: bool = True) -> bool:
        """
        Solve constraints to determine cell positions

        Args:
            fix_leaf_positions: If True, assigns default positions to leaf cells

        Returns:
            True if solution found, False otherwise
        """
        z3_solver = Solver()

        # Add basic geometric constraints (x2 > x1, y2 > y1)
        all_cells = self._get_all_cells()
        for cell in all_cells:
            x1, y1, x2, y2 = cell._get_z3_vars()
            z3_solver.add(x2 > x1)
            z3_solver.add(y2 > y1)

        # For leaf cells, optionally set default sizes
        if fix_leaf_positions:
            for cell in all_cells:
                if cell.is_leaf:
                    x1, y1, x2, y2 = cell._get_z3_vars()
                    # Default size for leaf cells if not constrained
                    z3_solver.add(x1 >= 0)
                    z3_solver.add(y1 >= 0)
                    # Give it some default size
                    z3_solver.add(x2 - x1 >= 10)
                    z3_solver.add(y2 - y1 >= 10)

        # Add parent-child bounding constraints
        self._add_parent_child_constraints(z3_solver)

        # Add all constraints from the hierarchy
        self._add_constraints_recursive(z3_solver)

        # Solve
        if z3_solver.check() == sat:
            model = z3_solver.model()

            # Extract solutions
            for cell in all_cells:
                x1, y1, x2, y2 = cell._get_z3_vars()
                cell.pos_list = [
                    self._z3_value_to_float(model[x1]),
                    self._z3_value_to_float(model[y1]),
                    self._z3_value_to_float(model[x2]),
                    self._z3_value_to_float(model[y2])
                ]

            # Update parent bounds to tightly fit children
            self._update_parent_bounds()

            return True
        else:
            return False

    def _z3_value_to_float(self, z3_val) -> float:
        """Convert Z3 value to Python float"""
        if z3_val is None:
            return 0.0

        # Handle rational numbers
        if isinstance(z3_val, RatNumRef):
            return float(z3_val.numerator_as_long()) / float(z3_val.denominator_as_long())

        # Try to convert to float
        try:
            return float(z3_val.as_decimal(10).rstrip('?'))
        except:
            return 0.0

    def _get_all_cells(self) -> List['Cell']:
        """
        Get all cells in the hierarchy (recursive)

        Returns:
            List of all Cell instances including self
        """
        cells = [self]
        for child in self.children:
            cells.extend(child._get_all_cells())
        return cells

    def _update_parent_bounds(self):
        """
        Update parent cell bounds to tightly fit their children (post-solve)
        Called after solver completes to ensure parent bounds match children
        """
        all_cells = self._get_all_cells()

        # Process from bottom-up (leaves to root) to ensure proper propagation
        # Sort by depth (deepest first)
        cells_by_depth = sorted(all_cells, key=lambda c: self._get_cell_depth(c), reverse=True)

        for cell in cells_by_depth:
            if not cell.is_leaf and len(cell.children) > 0:
                # Calculate bounding box from children
                child_x1_vals = []
                child_y1_vals = []
                child_x2_vals = []
                child_y2_vals = []

                for child in cell.children:
                    if all(v is not None for v in child.pos_list):
                        child_x1_vals.append(child.pos_list[0])
                        child_y1_vals.append(child.pos_list[1])
                        child_x2_vals.append(child.pos_list[2])
                        child_y2_vals.append(child.pos_list[3])

                if child_x1_vals:
                    # Set parent bounds to encompass all children
                    cell.pos_list = [
                        min(child_x1_vals),
                        min(child_y1_vals),
                        max(child_x2_vals),
                        max(child_y2_vals)
                    ]

    def _get_cell_depth(self, cell: 'Cell') -> int:
        """
        Get the depth of a cell in the hierarchy (0 = leaf)

        Args:
            cell: Cell to measure

        Returns:
            Depth level (0 for leaves, increases toward root)
        """
        if cell.is_leaf or len(cell.children) == 0:
            return 0
        return 1 + max(self._get_cell_depth(child) for child in cell.children)

    def _add_parent_child_constraints(self, z3_solver: Solver):
        """
        Add constraints ensuring parent cells encompass their children

        Args:
            z3_solver: Z3 Solver instance
        """
        all_cells = self._get_all_cells()

        for cell in all_cells:
            # Only add bounding constraints for container cells (non-leaf with children)
            if not cell.is_leaf and len(cell.children) > 0:
                parent_x1, parent_y1, parent_x2, parent_y2 = cell._get_z3_vars()

                for child in cell.children:
                    child_x1, child_y1, child_x2, child_y2 = child._get_z3_vars()

                    # Parent must encompass child
                    z3_solver.add(parent_x1 <= child_x1)
                    z3_solver.add(parent_y1 <= child_y1)
                    z3_solver.add(parent_x2 >= child_x2)
                    z3_solver.add(parent_y2 >= child_y2)

    def _add_constraints_recursive(self, z3_solver: Solver):
        """
        Recursively add all constraints to Z3 solver

        Args:
            z3_solver: Z3 Solver instance
        """
        # Add constraints from this cell
        for cell1, constraint_str, cell2 in self.constraints:
            z3_constraints = self._parse_constraint(constraint_str, cell1, cell2)
            for c in z3_constraints:
                z3_solver.add(c)

        # Recursively add constraints from children
        for child in self.children:
            child._add_constraints_recursive(z3_solver)

    def draw(self, solve_first: bool = True, ax=None, show: bool = True):
        """
        Visualize the layout using matplotlib

        Args:
            solve_first: If True, run solver before drawing
            ax: Matplotlib axes object (creates new if None)
            show: If True, display the plot
        """
        if solve_first:
            if not self.solver():
                print("Warning: Solver failed to find solution")
                return

        if ax is None:
            fig, ax = plt.subplots(figsize=(3, 3))
        else:
            fig = ax.figure

        # Draw all cells recursively
        self._draw_recursive(ax)

        ax.set_aspect('equal')
        ax.autoscale()
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Layout: {self.name}')

        # Force display in Spyder plots pane
        plt.draw()

        return fig

    def _draw_recursive(self, ax, level: int = 0):
        """
        Recursively draw all cells

        Args:
            ax: Matplotlib axes object
            level: Hierarchy level (for color coding)
        """
        # Draw children first (so parent outlines appear on top)
        for child in self.children:
            child._draw_recursive(ax, level + 1)

        # Now draw this cell
        if all(v is not None for v in self.pos_list):
            x1, y1, x2, y2 = self.pos_list
            width = x2 - x1
            height = y2 - y1

            if self.is_leaf:
                # Leaf cells: solid filled rectangles with layer colors
                layer_colors = {
                    'metal1': 'blue',
                    'metal2': 'red',
                    'metal3': 'green',
                    'metal4': 'orange',
                    'poly': 'purple',
                    'diff': 'brown',
                }
                color = layer_colors.get(self.layer_name, 'gray')

                rect = patches.Rectangle(
                    (x1, y1), width, height,
                    linewidth=2, edgecolor='black', facecolor=color, alpha=0.6
                )
                ax.add_patch(rect)

                # Add label
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                label = f"{self.name}\n({self.layer_name})"
                ax.text(cx, cy, label, ha='center', va='center', fontsize=8, weight='bold')

            else:
                # Container cells: dotted/dashed outline, no fill
                colors = ['darkblue', 'darkred', 'darkgreen', 'darkorange', 'darkviolet']
                edge_color = colors[level % len(colors)]

                rect = patches.Rectangle(
                    (x1, y1), width, height,
                    linewidth=2, edgecolor=edge_color, facecolor='none',
                    linestyle='--', alpha=0.8
                )
                ax.add_patch(rect)

                # Add label at top-left corner (outside the box)
                label = f"{self.name}"
                ax.text(x1, y2 + 1, label, ha='left', va='bottom', fontsize=9,
                       weight='bold', color=edge_color, style='italic')

    def copy(self) -> 'Cell':
        """
        Create a deep copy of this Cell instance

        Note: Z3 variables are reset so the copy gets fresh constraint variables

        Returns:
            New Cell instance with copied data
        """
        new_cell = copy_module.deepcopy(self)
        # Reset Z3 variables for the new copy and all descendants
        self._reset_z3_vars_recursive(new_cell)
        return new_cell

    def _reset_z3_vars_recursive(self, cell: 'Cell'):
        """
        Recursively reset Z3 variables for a cell and its children

        Args:
            cell: Cell to reset variables for
        """
        cell._z3_vars = None
        for child in cell.children:
            self._reset_z3_vars_recursive(child)

    def __repr__(self):
        return f"Cell(name={self.name}, pos={self.pos_list}, children={len(self.children)})"
