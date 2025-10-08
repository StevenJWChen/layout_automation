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
from scipy.optimize import linprog, minimize
import numpy as np


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
            constraint_str: Constraint string like 'sx1<ox2+3, sy2+5<oy1'
            cell1: Cell mapped to 's' prefix
            cell2: Cell mapped to 'o' prefix
            var_counter: Variable counter dictionary

        Returns:
            List of constraint tuples (operator, left_expr, right_expr, type)
            where type is 'ineq' for inequalities or 'eq' for equality
        """
        parsed_constraints = []

        # Get variable indices for both cells
        s_vars = cell1._get_var_indices(var_counter)
        o_vars = cell2._get_var_indices(var_counter)

        # Map variable names to indices
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

        # Tokenize the expression
        tokens = re.findall(r'[so][xy][12]|\d+\.?\d*|[+\-*/()]', expr_str)

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

    def solver(self, fix_leaf_positions: bool = True) -> bool:
        """
        Solve constraints to determine cell positions using SciPy optimization

        Args:
            fix_leaf_positions: If True, assigns default positions to leaf cells

        Returns:
            True if solution found, False otherwise
        """
        all_cells = self._get_all_cells()

        # Build variable counter
        var_counter = {}
        for cell in all_cells:
            cell._get_var_indices(var_counter)

        n_vars = len(var_counter) * 4

        # Build constraints in SciPy format
        inequality_constraints = []  # List of LinearConstraint objects
        equality_constraints = []
        bounds = [(None, None)] * n_vars  # Bounds for each variable

        # Add basic geometric constraints (x2 > x1, y2 > y1)
        for cell in all_cells:
            x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)

            # x2 > x1 => x2 - x1 > 0 => -x1 + x2 >= 0.01 (small epsilon for strict inequality)
            A = np.zeros(n_vars)
            A[x1_idx] = -1
            A[x2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

            # y2 > y1 => y2 - y1 > 0
            A = np.zeros(n_vars)
            A[y1_idx] = -1
            A[y2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

        # For leaf cells, optionally set default sizes
        if fix_leaf_positions:
            for cell in all_cells:
                if cell.is_leaf:
                    x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)

                    # x1 >= 0
                    A = np.zeros(n_vars)
                    A[x1_idx] = 1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

                    # y1 >= 0
                    A = np.zeros(n_vars)
                    A[y1_idx] = 1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

                    # x2 - x1 >= 10
                    A = np.zeros(n_vars)
                    A[x1_idx] = -1
                    A[x2_idx] = 1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 10})

                    # y2 - y1 >= 10
                    A = np.zeros(n_vars)
                    A[y1_idx] = -1
                    A[y2_idx] = 1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 10})

        # Add parent-child bounding constraints
        self._add_parent_child_constraints_scipy(inequality_constraints, var_counter, n_vars)

        # Add all user constraints from the hierarchy
        self._add_constraints_recursive_scipy(inequality_constraints, equality_constraints,
                                               var_counter, n_vars)

        # Initial guess - spread out cells
        x0 = np.zeros(n_vars)
        for i, cell in enumerate(all_cells):
            x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
            x0[x1_idx] = i * 30
            x0[y1_idx] = i * 30
            x0[x2_idx] = i * 30 + 20
            x0[y2_idx] = i * 30 + 20

        # Objective: minimize sum of areas (or minimize total layout size)
        def objective(x):
            total = 0
            for cell in all_cells:
                x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
                width = x[x2_idx] - x[x1_idx]
                height = x[y2_idx] - x[y1_idx]
                total += width * height
            return total

        # Combine all constraints
        all_constraints = inequality_constraints + equality_constraints

        # Solve using SciPy minimize
        result = minimize(objective, x0, method='SLSQP', constraints=all_constraints,
                         options={'maxiter': 1000, 'ftol': 1e-6})

        if result.success:
            # Extract solutions
            for cell in all_cells:
                x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
                cell.pos_list = [
                    float(result.x[x1_idx]),
                    float(result.x[y1_idx]),
                    float(result.x[x2_idx]),
                    float(result.x[y2_idx])
                ]

            # Update parent bounds to tightly fit children
            self._update_parent_bounds()

            return True
        else:
            print(f"Optimization failed: {result.message}")
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

    def _add_parent_child_constraints_scipy(self, inequality_constraints: List,
                                             var_counter: Dict[int, int], n_vars: int):
        """
        Add constraints ensuring parent cells encompass their children

        Args:
            inequality_constraints: List to append constraint dicts to
            var_counter: Variable counter dictionary
            n_vars: Total number of variables
        """
        all_cells = self._get_all_cells()

        for cell in all_cells:
            # Only add bounding constraints for container cells (non-leaf with children)
            if not cell.is_leaf and len(cell.children) > 0:
                parent_x1, parent_y1, parent_x2, parent_y2 = cell._get_var_indices(var_counter)

                for child in cell.children:
                    child_x1, child_y1, child_x2, child_y2 = child._get_var_indices(var_counter)

                    # Parent must encompass child
                    # parent_x1 <= child_x1 => child_x1 - parent_x1 >= 0
                    A = np.zeros(n_vars)
                    A[parent_x1] = -1
                    A[child_x1] = 1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

                    # parent_y1 <= child_y1
                    A = np.zeros(n_vars)
                    A[parent_y1] = -1
                    A[child_y1] = 1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

                    # parent_x2 >= child_x2 => parent_x2 - child_x2 >= 0
                    A = np.zeros(n_vars)
                    A[parent_x2] = 1
                    A[child_x2] = -1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

                    # parent_y2 >= child_y2
                    A = np.zeros(n_vars)
                    A[parent_y2] = 1
                    A[child_y2] = -1
                    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

    def _add_constraints_recursive_scipy(self, inequality_constraints: List,
                                          equality_constraints: List,
                                          var_counter: Dict[int, int], n_vars: int):
        """
        Recursively add all user constraints

        Args:
            inequality_constraints: List to append inequality constraint dicts to
            equality_constraints: List to append equality constraint dicts to
            var_counter: Variable counter dictionary
            n_vars: Total number of variables
        """
        # Add constraints from this cell
        for cell1, constraint_str, cell2 in self.constraints:
            parsed_constraints = self._parse_constraint(constraint_str, cell1, cell2, var_counter)

            for operator, left_expr, right_expr, var_map in parsed_constraints:
                # Parse both expressions into coefficient vectors
                left_coeffs, left_const = self._parse_expression_to_coeffs(left_expr, var_map, n_vars)
                right_coeffs, right_const = self._parse_expression_to_coeffs(right_expr, var_map, n_vars)

                # Constraint: left OP right => left - right OP 0
                A = left_coeffs - right_coeffs
                b = right_const - left_const

                if operator in ['<', '<=']:
                    # left <= right => left - right <= 0 => -(left - right) >= 0
                    inequality_constraints.append({
                        'type': 'ineq',
                        'fun': lambda x, A=A, b=b: -np.dot(A, x) - b
                    })
                elif operator in ['>', '>=']:
                    # left >= right => left - right >= 0
                    inequality_constraints.append({
                        'type': 'ineq',
                        'fun': lambda x, A=A, b=b: np.dot(A, x) + b
                    })
                elif operator == '=':
                    # left = right => left - right = 0
                    equality_constraints.append({
                        'type': 'eq',
                        'fun': lambda x, A=A, b=b: np.dot(A, x) + b
                    })

        # Recursively add constraints from children
        for child in self.children:
            child._add_constraints_recursive_scipy(inequality_constraints, equality_constraints,
                                                    var_counter, n_vars)

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

    def __repr__(self):
        return f"Cell(name={self.name}, pos={self.pos_list}, children={len(self.children)})"
