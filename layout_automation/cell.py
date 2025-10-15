#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cell class for constraint-based layout automation
Supports hierarchical cell instances with constraint solving using OR-Tools
"""

from __future__ import annotations
import re
import copy as copy_module
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Optional OR-Tools import (may not be available or may have compatibility issues)
try:
    from ortools.sat.python import cp_model
    HAS_ORTOOLS = True
except (ImportError, OSError, Exception):
    HAS_ORTOOLS = False
    cp_model = None


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
        self._var_indices = None  # Cache for variable indices in optimization vector
        self._frozen = False  # Track if layout is frozen
        self._frozen_bbox = None  # Cache bbox when frozen

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

    def constrain(self, cell1: Union['Cell', str], constraint_str: str = None, cell2: 'Cell' = None):
        """
        Add constraint between two cells, absolute constraint on one cell, or self-constraint

        Args:
            cell1: First cell (uses 's' or 'x' prefix in constraint string), or constraint string for self
            cell2: Second cell (uses 'o' prefix). If None, uses absolute constraint
            constraint_str: Constraint string, e.g., 'sx1<ox2+3' or 'x2-x1=10'
                           If cell1 is a string, this is treated as constraint_str for self-constraint

        Usage modes:
            1. Self-constraint:
               cell.constrain('x2-x1=100, y2-y1=50')  # Constrain cell's own bbox

            2. Absolute constraint on child:
               parent.constrain(child, 'x1=10, y1=20')  # Position child absolutely

            3. Relative constraint between children:
               parent.constrain(child1, 'sx2+10=ox1', child2)  # Position child1 relative to child2

        Auto-add instances:
            If cell1 or cell2 are not in self.children, they will be automatically added.
        """
        # Handle self-constraint mode: constrain('x2-x1=100')
        if isinstance(cell1, str) and constraint_str is None:
            constraint_str = cell1
            cell1 = self
            cell2 = None
            # For self-constraints, we don't auto-add since self is already the parent
            self.constraints.append((cell1, constraint_str, cell2))
            return

        # Normal mode: cell1 is a Cell object
        if not isinstance(cell1, Cell):
            raise TypeError(f"cell1 must be a Cell instance or constraint string, got {type(cell1)}")

        if constraint_str is None:
            raise ValueError("constraint_str is required when cell1 is a Cell")

        # Auto-add instances to children if not already present
        # This allows users to write: parent.constrain(child1, ..., child2)
        # without explicitly calling parent.add_instance(child1) first
        if cell1 != self and cell1 not in self.children:
            self.children.append(cell1)

        if cell2 is not None and cell2 != self and cell2 not in self.children:
            self.children.append(cell2)

        self.constraints.append((cell1, constraint_str, cell2))

    def _get_var_indices(self, var_counter: Dict[int, int]) -> Tuple[int, int, int, int]:
        """
        Get or create variable indices for this cell's position in optimization vector

        Args:
            var_counter: Dictionary mapping cell id to starting variable index

        Returns:
            Tuple of variable indices (x1_idx, y1_idx, x2_idx, y2_idx)
        """
        cell_id = id(self)
        if cell_id not in var_counter:
            # Assign 4 consecutive indices for this cell's variables
            start_idx = len(var_counter) * 4
            var_counter[cell_id] = start_idx

        start_idx = var_counter[cell_id]
        return (start_idx, start_idx + 1, start_idx + 2, start_idx + 3)

    def _parse_constraint(self, constraint_str: str, cell1: 'Cell', cell2: 'Cell',
                         var_counter: Dict[int, int]) -> List[Tuple[str, str, str, str]]:
        """
        Parse constraint string into constraint tuples for optimization

        Args:
            constraint_str: Constraint string like 'sx1<ox2+3' or 'x2-x1=10'
            cell1: Cell mapped to 's' or 'x' prefix
            cell2: Cell mapped to 'o' prefix (or None for absolute constraints)
            var_counter: Variable counter dictionary

        Returns:
            List of constraint tuples (operator, left_expr, right_expr, var_map)
        """
        parsed_constraints = []

        # Get variable indices for first cell
        s_vars = cell1._get_var_indices(var_counter)

        # Map variable names to indices
        if cell2 is None:
            # Absolute constraint - use 'x' prefix for single cell
            var_map = {
                'x1': s_vars[0], 'y1': s_vars[1], 'x2': s_vars[2], 'y2': s_vars[3],
                # Also support 's' prefix for backwards compatibility
                'sx1': s_vars[0], 'sy1': s_vars[1], 'sx2': s_vars[2], 'sy2': s_vars[3]
            }
        else:
            # Relative constraint between two cells
            o_vars = cell2._get_var_indices(var_counter)
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

            # Store constraint info for later processing
            parsed_constraints.append((operator, left, right, var_map))

        return parsed_constraints

    def _parse_expression_to_coeffs(self, expr_str: str, var_map: Dict[str, int], n_vars: int) -> Tuple[np.ndarray, float]:
        """
        Parse an arithmetic expression string into coefficient vector for linear optimization

        Args:
            expr_str: Expression string like 'sx1+5' or 'ox2*2-3' or 'sx2-sx1'
            var_map: Mapping of variable names to indices
            n_vars: Total number of variables

        Returns:
            Tuple of (coefficient vector, constant term)
        """
        # Initialize coefficient vector
        coeffs = np.zeros(n_vars)
        constant = 0.0

        # Tokenize the expression - match variable patterns: x1, y2, sx1, oy2, etc.
        tokens = re.findall(r'[soxy][xy]?[12]|\d+\.?\d*|[+\-*/()]', expr_str)

        # Parse tokens to build coefficients
        i = 0
        sign = 1.0
        pending_coefficient = None

        while i < len(tokens):
            token = tokens[i]

            if token == '+':
                sign = 1.0
                pending_coefficient = None
            elif token == '-':
                sign = -1.0
                pending_coefficient = None
            elif token == '*':
                # Multiplication operator, just skip
                pass
            elif token in var_map:
                # Variable found
                var_idx = var_map[token]
                coeff = sign

                # Check for pending coefficient (number before variable)
                if pending_coefficient is not None:
                    coeff *= pending_coefficient
                    pending_coefficient = None

                # Check for coefficient after variable (e.g., var*2)
                if i + 2 < len(tokens) and tokens[i+1] == '*' and re.match(r'\d+\.?\d*', tokens[i+2]):
                    coeff *= float(tokens[i+2])

                coeffs[var_idx] += coeff
                sign = 1.0  # Reset sign after processing variable
            elif re.match(r'\d+\.?\d*', token):
                # Number found
                num = float(token)

                # Check if this number is followed by a variable or *
                if i + 1 < len(tokens):
                    next_token = tokens[i+1]
                    if next_token in var_map:
                        # This number is a coefficient for the next variable
                        pending_coefficient = num
                    elif next_token == '*':
                        # Number followed by *, could be num*var
                        pending_coefficient = num
                    else:
                        # Standalone constant
                        constant += sign * num
                        sign = 1.0
                        pending_coefficient = None
                else:
                    # Last token is a number - it's a constant
                    constant += sign * num
                    sign = 1.0
                    pending_coefficient = None

            i += 1

        return coeffs, constant

    def solver(self, fix_leaf_positions: bool = True, integer_positions: bool = True) -> bool:
        """
        Solve constraints to determine cell positions using OR-Tools CP-SAT solver

        Args:
            fix_leaf_positions: If True, assigns default positions to leaf cells
            integer_positions: If True, uses integer variables (recommended for OR-Tools)

        Returns:
            True if solution found, False otherwise
        """
        if not HAS_ORTOOLS:
            raise RuntimeError(
                "OR-Tools is not available. The constraint solver requires OR-Tools to be installed. "
                "Please install it with: pip install ortools"
            )

        all_cells = self._get_all_cells()

        # Create OR-Tools model
        model = cp_model.CpModel()

        # Build variable counter and create integer variables
        var_counter = {}
        var_objects = {}  # Map from variable index to OR-Tools variable object

        # Define reasonable bounds for coordinates (adjust as needed)
        coord_min = 0
        coord_max = 10000

        for cell in all_cells:
            cell_id = id(cell)
            if cell_id not in var_counter:
                start_idx = len(var_counter) * 4
                var_counter[cell_id] = start_idx

                # Create 4 integer variables for each cell: x1, y1, x2, y2
                x1_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_x1')
                y1_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_y1')
                x2_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_x2')
                y2_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_y2')

                var_objects[start_idx] = x1_var
                var_objects[start_idx + 1] = y1_var
                var_objects[start_idx + 2] = x2_var
                var_objects[start_idx + 3] = y2_var

        # Add basic geometric constraints (x2 > x1, y2 > y1)
        for cell in all_cells:
            x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
            x1_var = var_objects[x1_idx]
            y1_var = var_objects[y1_idx]
            x2_var = var_objects[x2_idx]
            y2_var = var_objects[y2_idx]

            # x2 > x1 (at least 1 unit larger)
            model.Add(x2_var >= x1_var + 1)

            # y2 > y1 (at least 1 unit larger)
            model.Add(y2_var >= y1_var + 1)

        # For leaf cells, optionally set default sizes
        if fix_leaf_positions:
            for cell in all_cells:
                if cell.is_leaf:
                    x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
                    x1_var = var_objects[x1_idx]
                    y1_var = var_objects[y1_idx]
                    x2_var = var_objects[x2_idx]
                    y2_var = var_objects[y2_idx]

                    # x1 >= 0
                    model.Add(x1_var >= 0)

                    # y1 >= 0
                    model.Add(y1_var >= 0)

                    # Width and height at least 10 units
                    model.Add(x2_var - x1_var >= 10)
                    model.Add(y2_var - y1_var >= 10)

        # Add parent-child bounding constraints
        self._add_parent_child_constraints_ortools(model, var_counter, var_objects)

        # Add all user constraints from the hierarchy
        self._add_constraints_recursive_ortools(model, var_counter, var_objects)

        # Objective: minimize total layout size (sum of widths and heights)
        # We'll minimize the maximum x and y coordinates
        objective_terms = []
        for cell in all_cells:
            x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
            x2_var = var_objects[x2_idx]
            y2_var = var_objects[y2_idx]
            # Add width and height to minimize compactness
            objective_terms.append(x2_var)
            objective_terms.append(y2_var)

        # Minimize sum of all x2 and y2 coordinates (pushes layout to be compact)
        model.Minimize(sum(objective_terms))

        # Solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0  # Set timeout
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solutions
            for cell in all_cells:
                x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
                cell.pos_list = [
                    solver.Value(var_objects[x1_idx]),
                    solver.Value(var_objects[y1_idx]),
                    solver.Value(var_objects[x2_idx]),
                    solver.Value(var_objects[y2_idx])
                ]

            # Update parent bounds to tightly fit children
            self._update_parent_bounds()

            if status == cp_model.OPTIMAL:
                print(f"Optimal solution found in {solver.WallTime():.2f}s")
            else:
                print(f"Feasible solution found in {solver.WallTime():.2f}s")

            return True
        else:
            print(f"Solver failed with status: {solver.StatusName(status)}")
            return False

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

    def _add_parent_child_constraints_ortools(self, model: cp_model.CpModel,
                                               var_counter: Dict[int, int],
                                               var_objects: Dict[int, cp_model.IntVar]):
        """
        Add constraints ensuring parent cells encompass their children

        Uses AddMinEquality/AddMaxEquality for efficient bounding box constraints.
        This is more efficient than individual inequality constraints per child.

        Args:
            model: OR-Tools CP model
            var_counter: Variable counter dictionary
            var_objects: Dictionary mapping variable indices to OR-Tools variables
        """
        all_cells = self._get_all_cells()

        for cell in all_cells:
            # Only add bounding constraints for container cells (non-leaf with children)
            if not cell.is_leaf and len(cell.children) > 0:
                parent_x1_idx, parent_y1_idx, parent_x2_idx, parent_y2_idx = cell._get_var_indices(var_counter)
                parent_x1 = var_objects[parent_x1_idx]
                parent_y1 = var_objects[parent_y1_idx]
                parent_x2 = var_objects[parent_x2_idx]
                parent_y2 = var_objects[parent_y2_idx]

                # Collect all children's corner variables
                child_x1_vars = []
                child_y1_vars = []
                child_x2_vars = []
                child_y2_vars = []

                for child in cell.children:
                    child_x1_idx, child_y1_idx, child_x2_idx, child_y2_idx = child._get_var_indices(var_counter)
                    child_x1_vars.append(var_objects[child_x1_idx])
                    child_y1_vars.append(var_objects[child_y1_idx])
                    child_x2_vars.append(var_objects[child_x2_idx])
                    child_y2_vars.append(var_objects[child_y2_idx])

                # Use AddMinEquality/AddMaxEquality for efficient bounding box computation
                # Parent's bottom-left corner is the minimum of all children's bottom-left corners
                model.AddMinEquality(parent_x1, child_x1_vars)
                model.AddMinEquality(parent_y1, child_y1_vars)

                # Parent's top-right corner is the maximum of all children's top-right corners
                model.AddMaxEquality(parent_x2, child_x2_vars)
                model.AddMaxEquality(parent_y2, child_y2_vars)

    def _add_constraints_recursive_ortools(self, model: cp_model.CpModel,
                                            var_counter: Dict[int, int],
                                            var_objects: Dict[int, cp_model.IntVar]):
        """
        Recursively add all user constraints

        Args:
            model: OR-Tools CP model
            var_counter: Variable counter dictionary
            var_objects: Dictionary mapping variable indices to OR-Tools variables
        """
        # Add constraints from this cell
        for cell1, constraint_str, cell2 in self.constraints:
            parsed_constraints = self._parse_constraint(constraint_str, cell1, cell2, var_counter)

            for operator, left_expr, right_expr, var_map in parsed_constraints:
                # Build linear expressions for OR-Tools
                left_linear_expr = self._build_ortools_linear_expr(left_expr, var_map, var_objects)
                right_linear_expr = self._build_ortools_linear_expr(right_expr, var_map, var_objects)

                # Add constraint based on operator
                if operator in ['<', '<=']:
                    model.Add(left_linear_expr <= right_linear_expr)
                elif operator in ['>', '>=']:
                    model.Add(left_linear_expr >= right_linear_expr)
                elif operator == '=':
                    model.Add(left_linear_expr == right_linear_expr)

        # Recursively add constraints from children
        for child in self.children:
            child._add_constraints_recursive_ortools(model, var_counter, var_objects)

    def _build_ortools_linear_expr(self, expr_str: str, var_map: Dict[str, int],
                                     var_objects: Dict[int, cp_model.IntVar]):
        """
        Build an OR-Tools linear expression from a string expression

        Args:
            expr_str: Expression string like 'sx1+5' or 'ox2*2-3' or 'sx2-sx1'
            var_map: Mapping of variable names to indices
            var_objects: Dictionary mapping variable indices to OR-Tools variables

        Returns:
            Linear expression for OR-Tools
        """
        # Parse the expression using existing parser
        n_vars = len(var_objects)
        coeffs, constant = self._parse_expression_to_coeffs(expr_str, var_map, n_vars)

        # Build OR-Tools linear expression
        linear_expr = int(constant)  # Start with the constant term

        for var_idx, coeff in enumerate(coeffs):
            if coeff != 0 and var_idx in var_objects:
                var = var_objects[var_idx]
                if coeff == 1:
                    linear_expr += var
                elif coeff == -1:
                    linear_expr -= var
                else:
                    linear_expr += int(coeff) * var

        return linear_expr

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

        Note: Variable indices are reset so the copy gets fresh constraint variables

        Returns:
            New Cell instance with copied data
        """
        new_cell = copy_module.deepcopy(self)
        # Reset variable indices for the new copy and all descendants
        self._reset_var_indices_recursive(new_cell)
        return new_cell

    def _reset_var_indices_recursive(self, cell: 'Cell'):
        """
        Recursively reset variable indices for a cell and its children

        Args:
            cell: Cell to reset variables for
        """
        cell._var_indices = None
        for child in cell.children:
            self._reset_var_indices_recursive(child)

    def freeze_layout(self) -> 'Cell':
        """
        Freeze the current layout, making all positions immutable

        When frozen:
        - All child cell positions are locked
        - Internal structure cannot be modified
        - Can be efficiently reused as a fixed IP block
        - Bounding box is cached for fast access

        Returns:
            Self for method chaining
        """
        if self._frozen:
            return self  # Already frozen

        # Solve if not yet solved
        if any(v is None for v in self.pos_list):
            if not self.solver():
                raise RuntimeError(f"Cannot freeze cell '{self.name}': solver failed")

        # Mark as frozen
        self._frozen = True

        # Cache the bounding box
        self._frozen_bbox = tuple(self.pos_list)

        # Recursively freeze all children
        for child in self.children:
            if not child.is_leaf:
                child.freeze_layout()

        print(f"✓ Cell '{self.name}' frozen with bbox {self._frozen_bbox}")
        return self

    def unfreeze_layout(self) -> 'Cell':
        """
        Unfreeze the layout, allowing modifications again

        Returns:
            Self for method chaining
        """
        self._frozen = False
        self._frozen_bbox = None

        # Recursively unfreeze all children
        for child in self.children:
            if not child.is_leaf:
                child.unfreeze_layout()

        return self

    def is_frozen(self) -> bool:
        """
        Check if this cell's layout is frozen

        Returns:
            True if frozen, False otherwise
        """
        return self._frozen

    def get_bbox(self) -> tuple:
        """
        Get the bounding box of this cell

        Returns:
            Tuple of (x1, y1, x2, y2) or None if not solved
        """
        if self._frozen and self._frozen_bbox is not None:
            return self._frozen_bbox

        if all(v is not None for v in self.pos_list):
            return tuple(self.pos_list)

        return None

    def export_gds(self, filename: str, unit: float = 1e-6, precision: float = 1e-9,
                   layer_map: Dict[str, Tuple[int, int]] = None):
        """
        Export cell hierarchy to GDS-II file format

        Args:
            filename: Output GDS file path
            unit: Unit size in meters (default 1e-6 = 1 micrometer)
            precision: Precision in meters (default 1e-9 = 1 nanometer)
            layer_map: Optional mapping of layer names to (layer_number, datatype) tuples
                      Example: {'metal1': (1, 0), 'poly': (2, 0)}
        """
        try:
            import gdstk
        except ImportError:
            raise ImportError("gdstk library is required for GDS export. Install with: pip install gdstk")

        # Default layer mapping
        if layer_map is None:
            layer_map = {
                'metal1': (1, 0),
                'metal2': (2, 0),
                'metal3': (3, 0),
                'metal4': (4, 0),
                'poly': (5, 0),
                'diff': (6, 0),
                'pdiff': (7, 0),
                'nwell': (8, 0),
                'contact': (9, 0),
            }

        # Create GDS library
        lib = gdstk.Library(name="LAYOUT", unit=unit, precision=precision)

        # Convert cell hierarchy to GDS
        gds_cells_dict = {}
        self._convert_to_gds(lib, gds_cells_dict, layer_map)

        # Write to file
        lib.write_gds(filename)
        print(f"Exported to {filename}")

    def _convert_to_gds(self, lib: 'gdstk.Library', gds_cells_dict: Dict,
                       layer_map: Dict, offset_x: float = 0, offset_y: float = 0):
        """
        Recursively convert cell hierarchy to GDS format

        Args:
            lib: GDS library object
            gds_cells_dict: Dictionary tracking already-converted cells
            layer_map: Mapping of layer names to (layer, datatype) tuples
            offset_x: X offset for positioning
            offset_y: Y offset for positioning
        """
        import gdstk

        # Skip if already converted
        if self.name in gds_cells_dict:
            return gds_cells_dict[self.name]

        # Create GDS cell
        gds_cell = lib.new_cell(self.name)
        gds_cells_dict[self.name] = gds_cell

        # Process children
        for child in self.children:
            if child.is_leaf:
                # Leaf cell - create rectangle on specified layer
                if all(v is not None for v in child.pos_list):
                    x1, y1, x2, y2 = child.pos_list
                    x1 += offset_x
                    y1 += offset_y
                    x2 += offset_x
                    y2 += offset_y

                    # Get layer and datatype
                    layer, datatype = layer_map.get(child.layer_name, (0, 0))

                    # Create rectangle polygon
                    rect = gdstk.rectangle((x1, y1), (x2, y2), layer=layer, datatype=datatype)
                    gds_cell.add(rect)
            else:
                # Non-leaf cell - create reference
                child_gds_cell = child._convert_to_gds(lib, gds_cells_dict, layer_map)

                if all(v is not None for v in child.pos_list):
                    x1, y1, _, _ = child.pos_list
                    x1 += offset_x
                    y1 += offset_y

                    # Create cell reference
                    ref = gdstk.Reference(child_gds_cell, origin=(x1, y1))
                    gds_cell.add(ref)

        return gds_cell

    @classmethod
    def from_gds(cls, filename: str, cell_name: Optional[str] = None,
                 layer_map: Optional[Dict[Tuple[int, int], str]] = None) -> 'Cell':
        """
        Import cell from GDS-II file format

        Args:
            filename: Input GDS file path
            cell_name: Name of cell to import (if None, imports top cell)
            layer_map: Optional mapping of (layer_number, datatype) to layer names
                      Example: {(1, 0): 'metal1', (2, 0): 'poly'}

        Returns:
            Cell object with imported hierarchy
        """
        try:
            import gdstk
        except ImportError:
            raise ImportError("gdstk library is required for GDS import. Install with: pip install gdstk")

        # Default layer mapping (reverse of export mapping)
        if layer_map is None:
            layer_map = {
                (1, 0): 'metal1',
                (2, 0): 'metal2',
                (3, 0): 'metal3',
                (4, 0): 'metal4',
                (5, 0): 'poly',
                (6, 0): 'diff',
                (7, 0): 'pdiff',
                (8, 0): 'nwell',
                (9, 0): 'contact',
            }

        # Read GDS file
        lib = gdstk.read_gds(filename)

        # Find the cell to import
        if cell_name is None:
            # Get top cells (cells that are not referenced by others)
            all_cells = {cell.name: cell for cell in lib.cells}
            referenced = set()
            for cell in lib.cells:
                for ref in cell.references:
                    referenced.add(ref.cell.name)
            top_cells = [name for name in all_cells if name not in referenced]

            if not top_cells:
                raise ValueError("No top-level cell found in GDS file")
            cell_name = top_cells[0]

        # Find the GDS cell
        gds_cell = None
        for cell in lib.cells:
            if cell.name == cell_name:
                gds_cell = cell
                break

        if gds_cell is None:
            raise ValueError(f"Cell '{cell_name}' not found in GDS file")

        # Convert GDS cell to Cell object
        return cls._from_gds_cell(gds_cell, layer_map)

    @classmethod
    def _from_gds_cell(cls, gds_cell, layer_map: Dict) -> 'Cell':
        """
        Convert a GDS cell to a Cell object

        Args:
            gds_cell: gdstk Cell object
            layer_map: Mapping of (layer, datatype) to layer names

        Returns:
            Cell object
        """
        cell = cls(gds_cell.name)

        # Process polygons
        for polygon in gds_cell.polygons:
            layer_key = (polygon.layer, polygon.datatype)
            layer_name = layer_map.get(layer_key, f'layer_{polygon.layer}')

            # Get bounding box
            bbox = polygon.bounding_box()
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]

            # Create leaf cell for this polygon
            leaf = cls(f'{gds_cell.name}_{layer_name}_{len(cell.children)}', layer_name)
            leaf.pos_list = [x1, y1, x2, y2]
            cell.children.append(leaf)

        # Process cell references
        for ref in gds_cell.references:
            child_cell = cls._from_gds_cell(ref.cell, layer_map)
            x_offset, y_offset = ref.origin

            # Adjust all positions by offset
            cls._apply_offset_recursive(child_cell, x_offset, y_offset)

            cell.children.append(child_cell)

        return cell

    @staticmethod
    def _apply_offset_recursive(cell: 'Cell', dx: float, dy: float):
        """
        Recursively apply offset to cell and all children

        Args:
            cell: Cell to apply offset to
            dx: X offset
            dy: Y offset
        """
        if all(v is not None for v in cell.pos_list):
            cell.pos_list = [
                cell.pos_list[0] + dx,
                cell.pos_list[1] + dy,
                cell.pos_list[2] + dx,
                cell.pos_list[3] + dy
            ]

        for child in cell.children:
            Cell._apply_offset_recursive(child, dx, dy)

    def __repr__(self):
        frozen_str = " [FROZEN]" if self._frozen else ""
        return f"Cell(name={self.name}, pos={self.pos_list}, children={len(self.children)}{frozen_str})"
