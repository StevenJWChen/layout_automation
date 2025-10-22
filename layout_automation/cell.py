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

# Import constraint keyword expansion
from layout_automation.constraint_keywords import expand_constraint_keywords

# Import style configuration
from layout_automation.style_config import get_style_config

# Import freeze mixin
from layout_automation.freeze_mixin import FreezeMixin

import sys

# Optional OR-Tools import (may not be available or may have compatibility issues)
# Add a check to prevent segfault on incompatible Python versions (e.g., 3.13+)
HAS_ORTOOLS = False
cp_model = None
if sys.version_info.major == 3 and sys.version_info.minor < 13:
    try:
        from ortools.sat.python import cp_model
        HAS_ORTOOLS = True
    except (ImportError, OSError, Exception):
        # This block will now handle standard import errors on compatible Python versions
        HAS_ORTOOLS = False
        cp_model = None
else:
    # For Python 3.13+, assume OR-Tools is not safely importable to avoid segfault
    pass


class Cell(FreezeMixin):
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
        self.child_dict = {}  # Dictionary mapping child names to child instances
        self.pos_list = [None, None, None, None]  # [x1, y1, x2, y2]
        self.constraints = []
        self.is_leaf = False
        self.layer_name = None
        self._var_indices = None  # Cache for variable indices in optimization vector
        self._fixed = False  # Track if layout is fixed (can reposition while maintaining internal structure)
        self._fixed_offsets = {}  # Store relative offsets of children when fixed
        self._centering_constraints = []  # Track centering constraints with tolerance for soft constraint handling

        # Initialize freeze-related attributes from mixin
        self._init_freeze_attributes()

        # Parse arguments
        for arg in args:
            if isinstance(arg, str):
                # String argument means this is a leaf cell with a layer name
                self.is_leaf = True
                self.layer_name = arg
            elif isinstance(arg, Cell):
                self.children.append(arg)
                self.child_dict[arg.name] = arg
            elif isinstance(arg, list):
                # List of Cell instances
                for c in arg:
                    if isinstance(c, Cell):
                        self.children.append(c)
                        self.child_dict[c.name] = c
            else:
                raise TypeError(f"Invalid argument type: {type(arg)}")

    def add_instance(self, instances: Union['Cell', List['Cell']]):
        """
        Add child cell instance(s) and update child_dict

        Args:
            instances: Single Cell instance or list of Cell instances
        """
        if isinstance(instances, Cell):
            self.children.append(instances)
            self.child_dict[instances.name] = instances
        elif isinstance(instances, list):
            for c in instances:
                if isinstance(c, Cell):
                    self.children.append(c)
                    self.child_dict[c.name] = c
        else:
            raise TypeError("Argument must be Cell instance or list of Cell instances")

    def constrain(self, cell1: Union['Cell', str], constraint_str: str = None, cell2: 'Cell' = None):
        """
        Add constraint between two cells, absolute constraint on one cell, or self-constraint

        Supports constraint keywords for more readable code:
            'center' → 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2'
            'xcenter, swidth=10' → 'sx1+sx2=ox1+ox2, sx2-sx1=10'
            'left, sheight=oheight' → 'sx1=ox1, sy2-sy1=oy2-oy1'

        Args:
            cell1: First cell (uses 's' or 'x' prefix in constraint string), or constraint string for self
            cell2: Second cell (uses 'o' prefix). If None, uses absolute constraint
            constraint_str: Constraint string with optional keywords, e.g.:
                           Full syntax: 'sx1<ox2+3' or 'x2-x1=10'
                           With keywords: 'center' or 'xcenter, swidth=10'
                           If cell1 is a string, this is treated as constraint_str for self-constraint

        Usage modes:
            1. Self-constraint:
               cell.constrain('x2-x1=100, y2-y1=50')  # Full syntax
               cell.constrain('width=100, height=50')  # With keywords

            2. Absolute constraint on child:
               parent.constrain(child, 'x1=10, y1=20')  # Position child absolutely

            3. Relative constraint between children:
               parent.constrain(child1, 'sx2+10=ox1', child2)  # Full syntax
               parent.constrain(child1, 'center', child2)      # With keywords

        Keywords (see constraint_keywords.py):
            center, xcenter, ycenter - centering
            left, right, top, bottom - alignment
            swidth, sheight, owidth, oheight - sizes
            sx, sy, ox, oy - positions
            width, height - self-constraint sizes

        Auto-add instances:
            If cell1 or cell2 are not in self.children, they will be automatically added.
        """
        # Handle self-constraint mode: constrain('x2-x1=100')
        if isinstance(cell1, str) and constraint_str is None:
            constraint_str = cell1
            cell1 = self
            cell2 = None
            # Expand keywords in constraint string
            expanded_constraint = expand_constraint_keywords(constraint_str)
            # For self-constraints, we don't auto-add since self is already the parent
            self.constraints.append((cell1, expanded_constraint, cell2))
            return self

        # Normal mode: cell1 is a Cell object
        if not isinstance(cell1, Cell):
            raise TypeError(f"cell1 must be a Cell instance or constraint string, got {type(cell1)}")

        if constraint_str is None:
            raise ValueError("constraint_str is required when cell1 is a Cell")

        # Auto-add instances to children if not already present
        # This allows users to write: parent.constrain(child1, ..., child2)
        # without explicitly calling parent.add_instance(child1) first
        if cell1 != self and cell1 not in self.children:
            self.add_instance(cell1)

        if cell2 is not None and cell2 != self and cell2 not in self.children:
            self.add_instance(cell2)

        # Check if this is a centering constraint that should use soft constraint with tolerance
        # Detect keywords: 'center', 'xcenter', 'ycenter'
        # Handle mixed constraints like 'xcenter, sy2=oy1' by extracting centering part
        constraint_lower = constraint_str.lower()
        has_centering = any(keyword in constraint_lower for keyword in ['center', 'xcenter', 'ycenter'])

        # Separate centering keywords from other constraints
        remaining_constraints = []
        centering_added = False

        if has_centering and cell2 is not None:
            # Split constraint string by comma
            constraint_parts = [part.strip() for part in constraint_str.split(',')]

            for part in constraint_parts:
                part_lower = part.lower()

                # Check if this part is a centering keyword
                if part_lower in ['center', 'xcenter', 'ycenter']:
                    # This is a pure centering keyword - handle with soft constraints
                    if not centering_added:  # Only add once
                        if 'xcenter' == part_lower:
                            center_x, center_y = True, False
                        elif 'ycenter' == part_lower:
                            center_x, center_y = False, True
                        elif 'center' == part_lower:
                            center_x, center_y = True, True

                        self._centering_constraints.append({
                            'child': cell1,
                            'ref_obj': cell2,
                            'tolerance': 1,  # Default tolerance of ±1
                            'center_x': center_x,
                            'center_y': center_y
                        })
                        centering_added = True
                else:
                    # Not a centering keyword - keep for normal processing
                    remaining_constraints.append(part)

        # If no centering keywords or mixed with other constraints, process remaining parts
        if not has_centering or remaining_constraints:
            # Rebuild constraint string from remaining parts (if any)
            if remaining_constraints:
                final_constraint_str = ', '.join(remaining_constraints)
            else:
                final_constraint_str = constraint_str

            # Expand keywords in constraint string
            expanded_constraint = expand_constraint_keywords(final_constraint_str)

            self.constraints.append((cell1, expanded_constraint, cell2))

        return self

    def center_with_tolerance(self, child: 'Cell', ref_obj: 'Cell' = None, tolerance: float = 0):
        """
        Simple method to center child with tolerance (exact if tolerance=0)

        This is a convenience method that adds the right constraints to achieve
        centering with tolerance, without left/bottom bias.

        Args:
            child: Child cell to center
            ref_obj: Reference object (defaults to self)
            tolerance: Tolerance in layout units (0 = exact centering)

        Returns:
            self (for method chaining)

        Examples:
            # Exact centering
            parent.center_with_tolerance(child, tolerance=0)

            # Center with ±10 unit tolerance
            parent.center_with_tolerance(child, tolerance=10)

            # Center child1 relative to child2
            parent.center_with_tolerance(child1, ref_obj=child2, tolerance=5)

        Note:
            - If tolerance=0: Uses exact equality constraint (no bias)
            - If tolerance>0: Uses inequality constraints (may have left/bottom bias)
              For true centering with tolerance, use the custom solver:
              from layout_automation.centering_with_tolerance import (
                  add_centering_with_tolerance, solver_with_centering_objective
              )
        """
        if ref_obj is None:
            ref_obj = self

        if tolerance == 0:
            # Exact centering - use equality constraint (no bias)
            self.constrain(child, 'center', ref_obj)
        else:
            # With tolerance - use inequality constraints
            # WARNING: This may have left/bottom bias due to solver objective
            # For true centering with tolerance, use centering_with_tolerance.py
            tolerance_sum = tolerance * 2
            self.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
            self.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)
            self.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', ref_obj)
            self.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', ref_obj)

        return self

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

            # Check if cell is frozen - if so, fix its size
            if cell._apply_frozen_size_constraint(model, var_objects, x1_var, y1_var, x2_var, y2_var):
                pass  # Frozen size constraint applied
            # Check if cell is fixed - if so, fix its size based on stored offsets
            elif cell._fixed and len(cell._fixed_offsets) > 0:
                # Calculate width and height from the maximum offsets
                max_x_offset = max(offset[2] for offset in cell._fixed_offsets.values())  # dx2
                max_y_offset = max(offset[3] for offset in cell._fixed_offsets.values())  # dy2

                # Fix the size (but allow position to vary)
                model.Add(x2_var - x1_var == max_x_offset)
                model.Add(y2_var - y1_var == max_y_offset)
            else:
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

                    # Width and height at least 1 unit (minimum size)
                    model.Add(x2_var - x1_var >= 1)
                    model.Add(y2_var - y1_var >= 1)

        # Add parent-child bounding constraints
        self._add_parent_child_constraints_ortools(model, var_counter, var_objects)

        # Add all user constraints from the hierarchy
        self._add_constraints_recursive_ortools(model, var_counter, var_objects)

        # Collect all centering constraints from hierarchy
        all_centering_constraints = self._collect_centering_constraints_recursive()

        # Add soft constraints for centering preferences
        centering_penalty_terms = []
        if all_centering_constraints:
            centering_penalty_terms = self._add_centering_soft_constraints_ortools(
                model, var_counter, var_objects, all_centering_constraints
            )

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

        # Minimize: centering deviation (high priority) + layout size (lower priority)
        # Scale layout terms down so centering takes precedence
        if centering_penalty_terms:
            model.Minimize(sum(centering_penalty_terms) + sum(objective_terms))
        else:
            # No centering constraints, just minimize layout size
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

            # Update fixed cell positions if any cells are fixed
            self._update_all_fixed_positions()

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

        Frozen cells' children are NOT included because:
        - Frozen cells have fixed internal structure
        - Their children's positions are already determined
        - Solver only needs to position the frozen cell itself
        - This saves significant solver effort

        Returns:
            List of all Cell instances including self
        """
        cells = [self]

        # If this cell is frozen or fixed, don't include its children in solver
        # Frozen: internal structure is locked
        # Fixed: will update children via offsets after solving
        if self._is_frozen_or_fixed():
            return cells

        # Otherwise, recursively collect children
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
            # Skip fixed/frozen cells - their bounds are determined by solver or offsets
            if cell._is_frozen_or_fixed():
                continue

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

    def get_bounds(self):
        """
        Get the bounding box of this cell

        Returns:
            Tuple of (x1, y1, x2, y2) or None if position not yet determined
        """
        if all(v is not None for v in self.pos_list):
            return tuple(self.pos_list)
        return None

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
            # Only add bounding constraints for non-frozen and non-fixed container cells
            # For frozen/fixed cells, size is constrained elsewhere
            if not cell.is_leaf and len(cell.children) > 0 and not cell._is_frozen_or_fixed():
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
        # If cell is frozen or fixed, do not process its internal constraints
        # Frozen: treats cell as black box
        # Fixed: will update children positions after solving via offsets
        if self._is_frozen_or_fixed():
            return

        # Add constraints from this cell
        for cell1, constraint_str, cell2 in self.constraints:
            parsed_constraints = self._parse_constraint(constraint_str, cell1, cell2, var_counter)

            for operator, left_expr, right_expr, var_map in parsed_constraints:
                # Build linear expressions for OR-Tools
                left_linear_expr = self._build_ortools_linear_expr(left_expr, var_map, var_objects)
                right_linear_expr = self._build_ortools_linear_expr(right_expr, var_map, var_objects)

                # Add constraint based on operator
                if operator == '<':
                    model.Add(left_linear_expr < right_linear_expr)
                elif operator == '<=':
                    model.Add(left_linear_expr <= right_linear_expr)
                elif operator == '>':
                    model.Add(left_linear_expr > right_linear_expr)
                elif operator == '>=':
                    model.Add(left_linear_expr >= right_linear_expr)
                elif operator == '=':
                    model.Add(left_linear_expr == right_linear_expr)

        # Recursively add constraints from children
        for child in self.children:
            child._add_constraints_recursive_ortools(model, var_counter, var_objects)

    def _collect_centering_constraints_recursive(self) -> List[Dict]:
        """
        Recursively collect all centering constraints from hierarchy

        Returns:
            List of centering constraint dictionaries
        """
        all_constraints = []

        # Collect from this cell
        all_constraints.extend(self._centering_constraints)

        # Recursively collect from children (skip frozen/fixed cells)
        if not self._is_frozen_or_fixed():
            for child in self.children:
                if not child.is_leaf:
                    all_constraints.extend(child._collect_centering_constraints_recursive())

        return all_constraints

    def _add_centering_soft_constraints_ortools(self, model: cp_model.CpModel,
                                                 var_counter: Dict[int, int],
                                                 var_objects: Dict[int, cp_model.IntVar],
                                                 centering_constraints: List[Dict]) -> List:
        """
        Add soft constraints for centering with tolerance using OR-Tools recommended pattern

        This implements the OR-Tools soft constraint pattern:
        1. Create boolean variable for "is exactly centered"
        2. Add tolerance constraints (always enforced)
        3. Add exact centering constraint (only enforced if boolean is True)
        4. Add penalty to objective for not being exactly centered

        Args:
            model: OR-Tools CP model
            var_counter: Variable counter dictionary
            var_objects: Dictionary mapping variable indices to OR-Tools variables
            centering_constraints: List of centering constraint dictionaries

        Returns:
            List of penalty terms to add to objective
        """
        penalty_terms = []
        coord_max = 10000

        for i, constraint in enumerate(centering_constraints):
            # Skip constraints where child or ref_obj are frozen/fixed
            # (their children aren't in the solver variable set)
            child = constraint['child']
            ref_obj = constraint['ref_obj']

            # Check if variables exist in var_counter (they won't if cell is frozen/fixed)
            if id(child) not in var_counter or id(ref_obj) not in var_counter:
                continue

            tolerance = constraint['tolerance']
            center_x = constraint['center_x']
            center_y = constraint['center_y']

            # Get variable indices
            child_x1_idx, child_y1_idx, child_x2_idx, child_y2_idx = child._get_var_indices(var_counter)
            ref_x1_idx, ref_y1_idx, ref_x2_idx, ref_y2_idx = ref_obj._get_var_indices(var_counter)

            # Get OR-Tools variables
            child_x1 = var_objects[child_x1_idx]
            child_x2 = var_objects[child_x2_idx]
            child_y1 = var_objects[child_y1_idx]
            child_y2 = var_objects[child_y2_idx]

            ref_x1 = var_objects[ref_x1_idx]
            ref_x2 = var_objects[ref_x2_idx]
            ref_y1 = var_objects[ref_y1_idx]
            ref_y2 = var_objects[ref_y2_idx]

            tolerance_sum = tolerance * 2

            # X centering with soft constraint
            if center_x:
                # Create boolean for "is exactly centered in X"
                is_x_centered = model.NewBoolVar(f'{child.name}_x_centered_{i}')

                # Exact centering (only enforced if is_x_centered = True)
                model.Add(child_x1 + child_x2 == ref_x1 + ref_x2).OnlyEnforceIf(is_x_centered)

                # Tolerance constraints (always enforced)
                model.Add(child_x1 + child_x2 >= ref_x1 + ref_x2 - tolerance_sum)
                model.Add(child_x1 + child_x2 <= ref_x1 + ref_x2 + tolerance_sum)

                # If NOT exactly centered, we need to ensure the constraint is not enforced
                # This is automatic - OnlyEnforceIf handles it

                # Add deviation penalty (minimize when not exactly centered)
                # Penalty = large_weight * (1 - is_x_centered)
                # We'll use deviation variable approach for smoother optimization
                deviation_x = model.NewIntVar(0, coord_max * 4, f'{child.name}_x_dev_{i}')
                model.Add(deviation_x >= child_x1 + child_x2 - ref_x1 - ref_x2)
                model.Add(deviation_x >= ref_x1 + ref_x2 - child_x1 - child_x2)

                # Add large penalty for deviation (makes centering high priority)
                penalty_terms.append(deviation_x * 10000)

            # Y centering with soft constraint
            if center_y:
                # Create boolean for "is exactly centered in Y"
                is_y_centered = model.NewBoolVar(f'{child.name}_y_centered_{i}')

                # Exact centering (only enforced if is_y_centered = True)
                model.Add(child_y1 + child_y2 == ref_y1 + ref_y2).OnlyEnforceIf(is_y_centered)

                # Tolerance constraints (always enforced)
                model.Add(child_y1 + child_y2 >= ref_y1 + ref_y2 - tolerance_sum)
                model.Add(child_y1 + child_y2 <= ref_y1 + ref_y2 + tolerance_sum)

                # Add deviation penalty
                deviation_y = model.NewIntVar(0, coord_max * 4, f'{child.name}_y_dev_{i}')
                model.Add(deviation_y >= child_y1 + child_y2 - ref_y1 - ref_y2)
                model.Add(deviation_y >= ref_y1 + ref_y2 - child_y1 - child_y2)

                penalty_terms.append(deviation_y * 10000)

        if penalty_terms:
            print(f"Added soft centering constraints for {len(centering_constraints)} centering operation(s)")

        return penalty_terms

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

    def draw(self, solve_first: bool = True, ax=None, show: bool = True,
             show_labels: bool = True, label_mode: str = 'auto',
             label_position: str = 'top-left'):
        """
        Visualize the layout using matplotlib

        Args:
            solve_first: If True, run solver before drawing (default True)
                        If 'auto', only solves if positions are not yet determined
            ax: Matplotlib axes object (creates new if None)
            show: If True, display the plot
            show_labels: If True, show cell/layer labels
            label_mode: Label display mode
                - 'auto': Smart sizing based on cell dimensions (default)
                - 'full': Always show full labels (name + layer)
                - 'compact': Show only essential info
                - 'none': No labels (same as show_labels=False)
            label_position: Label position within cell
                - 'top-left': Upper left corner (default, best for avoiding overlap)
                - 'top-right': Upper right corner
                - 'bottom-left': Lower left corner
                - 'bottom-right': Lower right corner
                - 'center': Center of cell (old behavior)
        """
        # Auto-detect if solving is needed
        needs_solving = any(v is None for v in self.pos_list)

        # Solve if needed or explicitly requested
        if needs_solving or solve_first:
            if not self.solver():
                print("Warning: Solver failed to find solution")
                return

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
        else:
            fig = ax.figure

        # Draw all cells recursively with label options
        self._draw_recursive(ax, level=0, show_labels=show_labels,
                           label_mode=label_mode, label_position=label_position)

        ax.set_aspect('equal')
        ax.autoscale()
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Layout: {self.name}')

        # Force display in Spyder plots pane
        plt.draw()

        return fig

    def _draw_recursive(self, ax, level: int = 0, show_labels: bool = True,
                       label_mode: str = 'auto', label_position: str = 'top-left'):
        """
        Recursively draw all cells with customizable styles

        Args:
            ax: Matplotlib axes object
            level: Hierarchy level (for color coding)
            show_labels: Whether to show labels
            label_mode: Label display mode ('auto', 'full', 'compact', 'none')
            label_position: Label position ('top-left', 'center', etc.)
        """
        # Draw children first (so parent outlines appear on top)
        for child in self.children:
            child._draw_recursive(ax, level + 1, show_labels, label_mode, label_position)

        # Now draw this cell
        if all(v is not None for v in self.pos_list):
            x1, y1, x2, y2 = self.pos_list
            width = x2 - x1
            height = y2 - y1

            # Get style configuration
            style_config = get_style_config()

            if self.is_leaf:
                # Leaf cells: solid filled shapes with layer styles
                layer_style = style_config.get_layer_style(self.layer_name)

                # Create shape based on style
                patch = self._create_shape_patch(
                    x1, y1, width, height,
                    shape=layer_style.shape,
                    facecolor=layer_style.color,
                    edgecolor=layer_style.edge_color,
                    linewidth=layer_style.edge_width,
                    linestyle=layer_style.line_style,
                    alpha=layer_style.alpha,
                    zorder=layer_style.zorder
                )
                ax.add_patch(patch)

                # Add label with fixed font size, name only, no background
                if show_labels and label_mode != 'none':
                    # Always show only name, no layer
                    label_text = self.name
                    fontsize = 8  # Fixed font size
                    fontweight = 'normal'

                    if label_text:  # Only draw if there's text
                        # Get label position and alignment
                        lx, ly, ha, va = self._get_label_position(
                            x1, y1, x2, y2, label_position
                        )

                        # Draw text without background (no bbox)
                        ax.text(lx, ly, label_text, ha=ha, va=va,
                               fontsize=fontsize, weight=fontweight,
                               color='black', alpha=1.0)

            else:
                # Container cells: outline only, no fill
                edge_color = style_config.get_container_color(level)
                container_style = style_config.container_style

                # Create shape based on style
                patch = self._create_shape_patch(
                    x1, y1, width, height,
                    shape=container_style.shape,
                    facecolor='none',
                    edgecolor=edge_color,
                    linewidth=container_style.edge_width,
                    linestyle=container_style.linestyle,
                    alpha=container_style.alpha,
                    zorder=container_style.zorder
                )
                ax.add_patch(patch)

                # Add label at top-left corner (outside the box)
                if show_labels and label_mode != 'none':
                    label = f"{self.name}"
                    # Smaller, less intrusive label for containers
                    fontsize = 7 if label_mode == 'auto' else 9
                    ax.text(x1, y2 + 0.5, label, ha='left', va='bottom',
                           fontsize=fontsize, weight='normal',
                           color=edge_color, style='italic', alpha=0.8)

    def _get_label_position(self, x1: float, y1: float, x2: float, y2: float,
                           position: str):
        """
        Calculate label position and alignment based on position mode

        Args:
            x1, y1, x2, y2: Cell bounds
            position: Position mode ('top-left', 'center', etc.)

        Returns:
            Tuple of (x, y, horizontal_alignment, vertical_alignment)
        """
        # Small padding from edges
        pad = 0.5

        if position == 'top-left':
            return (x1 + pad, y2 - pad, 'left', 'top')
        elif position == 'top-right':
            return (x2 - pad, y2 - pad, 'right', 'top')
        elif position == 'bottom-left':
            return (x1 + pad, y1 + pad, 'left', 'bottom')
        elif position == 'bottom-right':
            return (x2 - pad, y1 + pad, 'right', 'bottom')
        else:  # 'center' or any other value
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            return (cx, cy, 'center', 'center')

    def _get_smart_label(self, width: float, height: float, label_mode: str):
        """
        Generate smart label text and styling based on cell size and mode

        Args:
            width: Cell width
            height: Cell height
            label_mode: Label mode ('auto', 'full', 'compact', 'none')

        Returns:
            Tuple of (label_text, fontsize, fontweight)
        """
        # Calculate cell area to determine label size
        area = width * height
        min_dim = min(width, height)

        if label_mode == 'full':
            # Always show full label
            label_text = f"{self.name}\n({self.layer_name})"
            fontsize = 7
            fontweight = 'normal'

        elif label_mode == 'compact':
            # Show abbreviated info
            # Use first 3 chars of name if too long
            short_name = self.name[:3] + '.' if len(self.name) > 4 else self.name
            label_text = f"{short_name}"
            fontsize = 5
            fontweight = 'normal'

        else:  # 'auto' mode - smart sizing based on dimensions
            # Very small cells: no label or just abbreviation
            if min_dim < 3 or area < 15:
                label_text = ""  # Too small for label
                fontsize = 4
                fontweight = 'normal'

            # Small cells: abbreviated name only
            elif min_dim < 8 or area < 100:
                short_name = self.name[:2] if len(self.name) > 3 else self.name
                label_text = short_name
                fontsize = 4
                fontweight = 'normal'

            # Medium cells: name only
            elif min_dim < 15 or area < 300:
                label_text = self.name
                fontsize = 5
                fontweight = 'normal'

            # Large cells: full label
            else:
                label_text = f"{self.name}\n{self.layer_name}"
                fontsize = 6
                fontweight = 'normal'

        return label_text, fontsize, fontweight

    def _create_shape_patch(self, x1, y1, width, height, shape='rectangle', **kwargs):
        """
        Create a matplotlib patch for the specified shape

        Args:
            x1, y1: Bottom-left corner
            width, height: Dimensions
            shape: Shape type ('rectangle', 'rounded', 'circle', 'octagon', 'ellipse')
            **kwargs: Additional patch parameters (facecolor, edgecolor, etc.)

        Returns:
            matplotlib.patches.Patch
        """
        if shape == 'rounded':
            # Rounded rectangle
            return patches.FancyBboxPatch(
                (x1, y1), width, height,
                boxstyle=f"round,pad=0,rounding_size={min(width, height) * 0.1}",
                **kwargs
            )
        elif shape == 'circle':
            # Circle (use the center and radius)
            cx = x1 + width / 2
            cy = y1 + height / 2
            radius = min(width, height) / 2
            return patches.Circle((cx, cy), radius, **kwargs)
        elif shape == 'ellipse':
            # Ellipse
            cx = x1 + width / 2
            cy = y1 + height / 2
            return patches.Ellipse((cx, cy), width, height, **kwargs)
        elif shape == 'octagon':
            # Regular octagon inscribed in the rectangle
            cx = x1 + width / 2
            cy = y1 + height / 2
            # Create octagon vertices
            import math
            vertices = []
            for i in range(8):
                angle = i * math.pi / 4
                vx = cx + (width / 2) * math.cos(angle)
                vy = cy + (height / 2) * math.sin(angle)
                vertices.append([vx, vy])
            return patches.Polygon(vertices, **kwargs)
        else:  # 'rectangle' (default)
            return patches.Rectangle((x1, y1), width, height, **kwargs)

    # Class variable to track copy counts for automatic naming
    _copy_counts = {}

    def copy(self, new_name: str = None) -> 'Cell':
        """
        Create a deep copy of this Cell instance with optional automatic naming

        Args:
            new_name: Optional new name for the copy. If None, automatically generates
                     a name by appending _c{N} where N is an incrementing number.
                     Example: 'block' -> 'block_c1', 'block_c2', etc.

        Note: Variable indices are reset so the copy gets fresh constraint variables

        Returns:
            New Cell instance with copied data

        Examples:
            >>> block = Cell('reusable_block')
            >>> copy1 = block.copy()  # Name: 'reusable_block_c1'
            >>> copy2 = block.copy()  # Name: 'reusable_block_c2'
            >>> copy3 = block.copy('custom_name')  # Name: 'custom_name'
        """
        new_cell = copy_module.deepcopy(self)

        # Handle naming
        if new_name is not None:
            # User provided explicit name
            new_cell.name = new_name
        else:
            # Automatic naming with _c{N} suffix
            original_name = self.name

            # Initialize counter for this original name if not exists
            if original_name not in Cell._copy_counts:
                Cell._copy_counts[original_name] = 0

            # Increment counter
            Cell._copy_counts[original_name] += 1
            copy_num = Cell._copy_counts[original_name]

            # Generate new name
            new_cell.name = f"{original_name}_c{copy_num}"

        # Reset variable indices for the new copy and all descendants
        self._reset_var_indices_recursive(new_cell)

        # For fixed cells, we need to reset ALL positions (including children)
        # Otherwise there's a mismatch: parent has None but children have positions
        if new_cell._fixed:
            # Reset parent position
            new_cell.pos_list = [None, None, None, None]
            # Reset all children positions recursively
            self._reset_positions_recursive(new_cell)

            # IMPORTANT: Rebuild _fixed_offsets with new child IDs
            # After deepcopy, children have new id() values, but _fixed_offsets
            # still has old IDs as keys. We need to remap them.
            if len(new_cell._fixed_offsets) > 0:
                self._rebuild_fixed_offsets(new_cell, self)
        else:
            # Reset position list for the new copy
            new_cell.pos_list = [None, None, None, None]

        return new_cell

    def _rebuild_fixed_offsets(self, new_cell: 'Cell', original_cell: 'Cell'):
        """
        Rebuild _fixed_offsets dictionary with new child IDs after deep copy

        After deepcopy, children are new objects with new id() values,
        but _fixed_offsets still has old IDs as keys. This method creates
        a new mapping using the new child IDs.

        Args:
            new_cell: The copied cell with new children
            original_cell: The original cell with old children
        """
        new_offsets = {}

        # Map old children to new children by index
        for i, (old_child, new_child) in enumerate(zip(original_cell.children, new_cell.children)):
            old_id = id(old_child)
            new_id = id(new_child)

            # If old_id is in offsets, copy it to new_id
            if old_id in original_cell._fixed_offsets:
                new_offsets[new_id] = original_cell._fixed_offsets[old_id]

            # Recursively rebuild for nested fixed cells
            if new_child._fixed and len(new_child._fixed_offsets) > 0:
                self._rebuild_fixed_offsets(new_child, old_child)

        # Replace the offsets dictionary
        new_cell._fixed_offsets = new_offsets

    def _reset_var_indices_recursive(self, cell: 'Cell'):
        """
        Recursively reset variable indices for a cell and its children

        Args:
            cell: Cell to reset variables for
        """
        cell._var_indices = None
        for child in cell.children:
            self._reset_var_indices_recursive(child)

    def _reset_positions_recursive(self, cell: 'Cell'):
        """
        Recursively reset positions for a cell and all its descendants

        Args:
            cell: Cell to reset positions for
        """
        for child in cell.children:
            child.pos_list = [None, None, None, None]
            if not child.is_leaf:
                self._reset_positions_recursive(child)

    # freeze_layout(), unfreeze_layout(), is_frozen() methods are now provided by FreezeMixin

    def get_bbox(self) -> tuple:
        """
        Get the bounding box of this cell

        Returns:
            Tuple of (x1, y1, x2, y2) or None if not solved
        """
        # Check if frozen first
        frozen_bbox = self._get_frozen_bbox()
        if frozen_bbox is not None:
            return frozen_bbox

        if all(v is not None for v in self.pos_list):
            return tuple(self.pos_list)

        return None

    @property
    def width(self) -> Optional[float]:
        """
        Get the width of this cell (x2 - x1)

        Automatically solves the layout if positions are not yet determined.

        Returns:
            Width of the cell, or None if solver fails

        Example:
            >>> cell.constrain('width=100, height=50')
            >>> print(f"Cell width: {cell.width}")  # Auto-solves if needed
        """
        # Auto-solve if positions not yet determined
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None

        if all(v is not None for v in self.pos_list):
            return self.pos_list[2] - self.pos_list[0]
        return None

    @property
    def height(self) -> Optional[float]:
        """
        Get the height of this cell (y2 - y1)

        Automatically solves the layout if positions are not yet determined.

        Returns:
            Height of the cell, or None if solver fails

        Example:
            >>> cell.constrain('width=100, height=50')
            >>> print(f"Cell height: {cell.height}")  # Auto-solves if needed
        """
        # Auto-solve if positions not yet determined
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None

        if all(v is not None for v in self.pos_list):
            return self.pos_list[3] - self.pos_list[1]
        return None

    @property
    def x1(self) -> Optional[float]:
        """
        Get the left x-coordinate (auto-solves if needed)

        Returns:
            Left x-coordinate, or None if solver fails
        """
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None
        return self.pos_list[0] if all(v is not None for v in self.pos_list) else None

    @property
    def y1(self) -> Optional[float]:
        """
        Get the bottom y-coordinate (auto-solves if needed)

        Returns:
            Bottom y-coordinate, or None if solver fails
        """
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None
        return self.pos_list[1] if all(v is not None for v in self.pos_list) else None

    @property
    def x2(self) -> Optional[float]:
        """
        Get the right x-coordinate (auto-solves if needed)

        Returns:
            Right x-coordinate, or None if solver fails
        """
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None
        return self.pos_list[2] if all(v is not None for v in self.pos_list) else None

    @property
    def y2(self) -> Optional[float]:
        """
        Get the top y-coordinate (auto-solves if needed)

        Returns:
            Top y-coordinate, or None if solver fails
        """
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None
        return self.pos_list[3] if all(v is not None for v in self.pos_list) else None

    @property
    def cx(self) -> Optional[float]:
        """
        Get the center x-coordinate

        Automatically solves the layout if positions are not yet determined.

        Returns:
            Center x-coordinate, or None if solver fails

        Example:
            >>> cell.constrain('width=100, height=50')
            >>> print(f"Center X: {cell.cx}")  # Auto-solves if needed
        """
        # Auto-solve if positions not yet determined
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None

        if all(v is not None for v in self.pos_list):
            return (self.pos_list[0] + self.pos_list[2]) / 2
        return None

    @property
    def cy(self) -> Optional[float]:
        """
        Get the center y-coordinate

        Automatically solves the layout if positions are not yet determined.

        Returns:
            Center y-coordinate, or None if solver fails

        Example:
            >>> cell.constrain('width=100, height=50')
            >>> print(f"Center Y: {cell.cy}")  # Auto-solves if needed
        """
        # Auto-solve if positions not yet determined
        if any(v is None for v in self.pos_list):
            if not self.solver():
                return None

        if all(v is not None for v in self.pos_list):
            return (self.pos_list[1] + self.pos_list[3]) / 2
        return None

    def fix_layout(self) -> 'Cell':
        """
        Fix the current layout, storing relative positions of all children.

        After fixing:
        - Internal structure relationships are PRESERVED
        - The cell can be repositioned by constraints
        - When the cell moves, ALL internal polygons automatically update
        - Children maintain their relative offsets from the parent's origin

        This is different from freeze_layout():
        - freeze: treats cell as black box, internal structure locked
        - fix: allows repositioning while updating all internal elements

        Returns:
            Self for method chaining

        Example:
            >>> block = Cell('block')
            >>> # ... add children and solve ...
            >>> block.fix_layout()  # Fix the internal structure
            >>> parent.constrain(block, 'x1=100, y1=50')  # Reposition
            >>> parent.solver()  # All internal polygons update to new position
        """
        if self._fixed:
            return self  # Already fixed

        # Solve if not yet solved
        if any(v is None for v in self.pos_list):
            if not self.solver():
                raise RuntimeError(f"Cannot fix cell '{self.name}': solver failed")

        # Mark as fixed
        self._fixed = True

        # Store the original bbox
        parent_x1, parent_y1, parent_x2, parent_y2 = self.pos_list

        # Recursively store relative offsets for all children AND mark them as needing updates
        def store_offsets(cell, parent_origin):
            """Recursively store relative offsets for all descendants"""
            px1, py1 = parent_origin

            for child in cell.children:
                if all(v is not None for v in child.pos_list):
                    # Store offset relative to parent's origin (x1, y1)
                    child_x1, child_y1, child_x2, child_y2 = child.pos_list
                    offset = (
                        child_x1 - px1,  # dx1
                        child_y1 - py1,  # dy1
                        child_x2 - px1,  # dx2
                        child_y2 - py1   # dy2
                    )
                    # Use id(child) as key to handle multiple children with same name
                    cell._fixed_offsets[id(child)] = offset

                    # Also recursively fix the child so it can update its own children
                    if not child.is_leaf and len(child.children) > 0 and not child._fixed:
                        # Temporarily mark child as having been processed
                        child_parent_origin = (child_x1, child_y1)
                        store_offsets(child, child_parent_origin)

        store_offsets(self, (parent_x1, parent_y1))

        print(f"[OK] Cell '{self.name}' fixed with {len(self._fixed_offsets)} relative offsets stored")
        return self

    def unfix_layout(self) -> 'Cell':
        """
        Unfix the layout, removing relative offset constraints

        Returns:
            Self for method chaining
        """
        self._fixed = False
        self._fixed_offsets = {}

        # Recursively unfix children
        for child in self.children:
            if not child.is_leaf:
                child.unfix_layout()

        return self

    def is_fixed(self) -> bool:
        """
        Check if this cell's layout is fixed

        Returns:
            True if fixed, False otherwise
        """
        return self._fixed

    def update_fixed_positions(self):
        """
        Update all child positions based on stored offsets after parent repositioning.

        This is called after the parent cell's position changes to propagate
        the position update to all internal elements.
        """
        if not self._fixed or len(self._fixed_offsets) == 0:
            return

        # Get current parent position
        if any(v is None for v in self.pos_list):
            return

        parent_x1, parent_y1, parent_x2, parent_y2 = self.pos_list

        # Update all children positions based on stored offsets
        def update_children(cell, parent_origin):
            """Recursively update child positions"""
            px1, py1 = parent_origin

            for child in cell.children:
                child_id = id(child)
                if child_id in cell._fixed_offsets:
                    dx1, dy1, dx2, dy2 = cell._fixed_offsets[child_id]
                    child.pos_list = [
                        px1 + dx1,
                        py1 + dy1,
                        px1 + dx2,
                        py1 + dy2
                    ]

                    # Recursively update grandchildren
                    # If child is fixed, use its update method
                    # Otherwise, recursively update all its descendants
                    if not child.is_leaf and len(child.children) > 0:
                        if child._fixed:
                            child.update_fixed_positions()
                        else:
                            # Not fixed, but still need to update grandchildren
                            update_children(child, (child.pos_list[0], child.pos_list[1]))

        update_children(self, (parent_x1, parent_y1))

    def _update_all_fixed_positions(self):
        """
        Recursively update all fixed cells in the hierarchy after solving.

        This is called by the solver after positions are determined.
        """
        # Update this cell if it's fixed
        if self._fixed:
            self.update_fixed_positions()

        # Recursively update children
        for child in self.children:
            if not child.is_leaf:
                child._update_all_fixed_positions()

    def set_position(self, x1: float, y1: float):
        """
        Manually set the position of a fixed layout cell.

        This method is specifically for fixed layout cells. When you set the position,
        all internal polygons automatically update based on stored relative offsets.

        Args:
            x1: New x1 coordinate (left edge)
            y1: New y1 coordinate (bottom edge)

        Example:
            >>> block.solver()          # Solve the layout
            >>> block.fix_layout()      # Fix the layout
            >>> block.set_position(100, 50)  # Move to (100, 50)
            # All internal polygons automatically update!

        Note:
            - This method works best with fixed layout cells
            - If the cell is not fixed, it just sets the position without updating children
            - The cell's width and height are preserved
        """
        if not self._fixed:
            print(f"Warning: Cell '{self.name}' is not fixed. Consider using fix_layout() first.")

        # Calculate current width and height
        if all(v is not None for v in self.pos_list):
            width = self.pos_list[2] - self.pos_list[0]
            height = self.pos_list[3] - self.pos_list[1]
        else:
            # If not yet positioned, use offsets to determine size
            if self._fixed and len(self._fixed_offsets) > 0:
                width = max(offset[2] for offset in self._fixed_offsets.values())
                height = max(offset[3] for offset in self._fixed_offsets.values())
            else:
                print(f"Warning: Cannot determine size for cell '{self.name}'")
                return

        # Set new position
        self.pos_list = [x1, y1, x1 + width, y1 + height]

        # Update children positions if fixed
        if self._fixed:
            self.update_fixed_positions()

    def export_gds(self, filename: str, unit: float = 1e-6, precision: float = 1e-9,
                   layer_map: Dict[str, Tuple[int, int]] = None,
                   use_tech_file: bool = True):
        """
        Export cell hierarchy to GDS-II file format

        Args:
            filename: Output GDS file path
            unit: Unit size in meters (default 1e-6 = 1 micrometer)
            precision: Precision in meters (default 1e-9 = 1 nanometer)
            layer_map: Optional mapping of layer names to (layer_number, datatype) tuples
                      Example: {'metal1': (1, 0), 'poly': (2, 0)}
                      If None and use_tech_file=True, uses tech file mapping
            use_tech_file: If True, use technology file for layer mapping (default True)
        """
        try:
            import gdstk
        except ImportError:
            raise ImportError("gdstk library is required for GDS export. Install with: pip install gdstk")

        # Get layer mapping
        if layer_map is None:
            if use_tech_file:
                # Try to use tech file
                try:
                    from layout_automation.tech_file import get_tech_file
                    tech = get_tech_file()
                    layer_map = {}
                    for (name, purpose), mapping in tech.layers.items():
                        if purpose == 'drawing':  # Only use drawing layers for export
                            layer_map[name] = (mapping.gds_layer, mapping.gds_datatype)
                    if layer_map:
                        print(f"Using tech file layer mapping ({len(layer_map)} layers)")
                except Exception as e:
                    print(f"Warning: Could not load tech file, using defaults: {e}")
                    layer_map = None

            # Default layer mapping if tech file not available
            if not layer_map:
                layer_map = {
                    'metal1': (30, 0),
                    'metal2': (50, 0),
                    'metal3': (70, 0),
                    'metal4': (90, 0),
                    'metal5': (110, 0),
                    'metal6': (130, 0),
                    'poly': (10, 0),
                    'diff': (3, 0),
                    'ndiff': (3, 0),
                    'pdiff': (4, 0),
                    'nwell': (1, 0),
                    'pwell': (2, 0),
                    'contact': (20, 0),
                    'via': (40, 0),
                    'via1': (40, 0),
                    'via2': (60, 0),
                    'via3': (80, 0),
                    'via4': (100, 0),
                    'via5': (120, 0),
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
                # Leaf cell - create as a separate GDS cell to preserve name
                if all(v is not None for v in child.pos_list):
                    # Create or get the leaf's GDS cell
                    if child.name not in gds_cells_dict:
                        leaf_gds_cell = lib.new_cell(child.name)
                        gds_cells_dict[child.name] = leaf_gds_cell

                        # Get layer and datatype
                        layer, datatype = layer_map.get(child.layer_name, (0, 0))

                        # Add rectangle to the leaf cell at origin
                        x1, y1, x2, y2 = child.pos_list
                        width = x2 - x1
                        height = y2 - y1
                        rect = gdstk.rectangle((0, 0), (width, height), layer=layer, datatype=datatype)
                        leaf_gds_cell.add(rect)
                    else:
                        leaf_gds_cell = gds_cells_dict[child.name]

                    # Create reference to the leaf cell at its position
                    x1, y1, _, _ = child.pos_list
                    x1 += offset_x
                    y1 += offset_y
                    ref = gdstk.Reference(leaf_gds_cell, origin=(x1, y1))
                    gds_cell.add(ref)
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
                 layer_map: Optional[Dict[Tuple[int, int], str]] = None,
                 use_tech_file: bool = True) -> 'Cell':
        """
        Import cell from GDS-II file format

        Args:
            filename: Input GDS file path
            cell_name: Name of cell to import (if None, imports top cell)
            layer_map: Optional mapping of (layer_number, datatype) to layer names
                      Example: {(1, 0): 'metal1', (2, 0): 'poly'}
            use_tech_file: If True, use technology file for layer mapping

        Returns:
            Cell object with imported hierarchy
        """
        try:
            import gdstk
        except ImportError:
            raise ImportError("gdstk library is required for GDS import. Install with: pip install gdstk")

        # Get layer mapping from tech file if available
        if layer_map is None:
            if use_tech_file:
                try:
                    from layout_automation.tech_file import get_tech_file
                    tech = get_tech_file()
                    layer_map = {}
                    # Build reverse mapping: (gds_layer, gds_datatype) -> layer_name
                    for (name, purpose), mapping in tech.layers.items():
                        if purpose == 'drawing':
                            layer_map[(mapping.gds_layer, mapping.gds_datatype)] = name
                    if layer_map:
                        print(f"Using tech file for GDS import ({len(layer_map)} layers)")
                except Exception as e:
                    print(f"Warning: Could not load tech file, using defaults: {e}")
                    layer_map = None

        # Default layer mapping (reverse of export mapping) if tech file not available
        if layer_map is None:
            layer_map = {
                (30, 0): 'metal1',
                (50, 0): 'metal2',
                (70, 0): 'metal3',
                (90, 0): 'metal4',
                (110, 0): 'metal5',
                (130, 0): 'metal6',
                (10, 0): 'poly',
                (3, 0): 'ndiff',
                (4, 0): 'pdiff',
                (1, 0): 'nwell',
                (2, 0): 'pwell',
                (20, 0): 'contact',
                (40, 0): 'via1',
                (60, 0): 'via2',
                (80, 0): 'via3',
                (100, 0): 'via4',
                (120, 0): 'via5',
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
            Cell object with fixed layout (children are frozen, can only be repositioned)
        """
        # Special case: If this cell has exactly 1 polygon and no references,
        # and the polygon is at origin, treat it as a leaf cell
        # (This preserves the structure of exported leaf cells)
        if len(gds_cell.polygons) == 1 and len(gds_cell.references) == 0:
            polygon = gds_cell.polygons[0]
            bbox = polygon.bounding_box()
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]

            # Check if polygon is at origin (within tolerance)
            if abs(x1) < 1e-6 and abs(y1) < 1e-6:
                # This is a simple leaf cell - preserve as leaf
                layer_key = (polygon.layer, polygon.datatype)
                layer_name = layer_map.get(layer_key, f'layer_{polygon.layer}')

                # Create as leaf cell with layer name
                leaf_cell = cls(gds_cell.name, layer_name)
                # Position will be set by parent's reference origin
                # Keep as float to avoid cumulative rounding errors when offset is applied
                leaf_cell.pos_list = [0.0, 0.0, x2 - x1, y2 - y1]
                return leaf_cell

        # Normal case: cell with multiple polygons or references
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
            # Convert to int to avoid float issues in solver
            leaf = cls(f'{gds_cell.name}_{layer_name}_{len(cell.children)}', layer_name)
            leaf.pos_list = [int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))]
            cell.children.append(leaf)
            cell.child_dict[leaf.name] = leaf

        # Process cell references
        for ref in gds_cell.references:
            child_cell = cls._from_gds_cell(ref.cell, layer_map)
            x_offset, y_offset = ref.origin

            # Adjust all positions by offset
            cls._apply_offset_recursive(child_cell, x_offset, y_offset)

            cell.children.append(child_cell)
            cell.child_dict[child_cell.name] = child_cell

        # Calculate bounding box for the cell from its children
        if cell.children:
            x1_vals = []
            y1_vals = []
            x2_vals = []
            y2_vals = []

            for child in cell.children:
                if all(v is not None for v in child.pos_list):
                    x1_vals.append(child.pos_list[0])
                    y1_vals.append(child.pos_list[1])
                    x2_vals.append(child.pos_list[2])
                    y2_vals.append(child.pos_list[3])

            if x1_vals:
                # Set cell's pos_list to the bounding box (convert to int)
                cell.pos_list = [
                    int(round(min(x1_vals))),
                    int(round(min(y1_vals))),
                    int(round(max(x2_vals))),
                    int(round(max(y2_vals)))
                ]

        # Fix the layout so it can only be repositioned, not resized
        cell.fix_layout()

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
            # Convert to int to avoid float issues in solver
            cell.pos_list = [
                int(round(cell.pos_list[0] + dx)),
                int(round(cell.pos_list[1] + dy)),
                int(round(cell.pos_list[2] + dx)),
                int(round(cell.pos_list[3] + dy))
            ]

        for child in cell.children:
            Cell._apply_offset_recursive(child, dx, dy)

    @classmethod
    def import_gds_to_cell(cls, filename: str, cell_name: Optional[str] = None,
                          layer_map: Optional[Dict[Tuple[int, int], str]] = None,
                          add_position_constraints: bool = True,
                          use_tech_file: bool = True) -> 'Cell':
        """
        Import GDS and create a cell with constraints to minimize position changes

        This method imports a GDS file and automatically adds constraints that
        try to keep elements at their original positions. This allows you to:
        1. Import an existing layout
        2. Modify it by adding new constraints
        3. Re-solve to get adjusted layout

        Args:
            filename: Input GDS file path
            cell_name: Name of cell to import (if None, imports top cell)
            layer_map: Optional mapping of (layer_number, datatype) to layer names
            add_position_constraints: If True, adds constraints to minimize position changes
            use_tech_file: If True, use technology file for layer mapping

        Returns:
            Cell object with imported hierarchy and position constraints

        Example:
            >>> # Import existing layout
            >>> cell = Cell.import_gds_to_cell('inverter.gds')
            >>>
            >>> # Add new constraint to move a specific element
            >>> metal_layer = cell.child_dict['INVERTER_metal1_0']
            >>> cell.constrain(metal_layer, 'x1=ox1+10', cell)  # Move 10 units right
            >>>
            >>> # Re-solve with minimal changes to other elements
            >>> cell.solver()
            >>>
            >>> # Export modified layout
            >>> cell.export_gds('inverter_modified.gds')
        """
        try:
            import gdstk
        except ImportError:
            raise ImportError("gdstk library is required for GDS import. Install with: pip install gdstk")

        # Get layer mapping from tech file if available
        if layer_map is None:
            if use_tech_file:
                try:
                    from layout_automation.tech_file import get_tech_file
                    tech = get_tech_file()
                    layer_map = {}
                    # Build reverse mapping: (gds_layer, gds_datatype) -> layer_name
                    for (name, purpose), mapping in tech.layers.items():
                        if purpose == 'drawing':
                            layer_map[(mapping.gds_layer, mapping.gds_datatype)] = name
                    if layer_map:
                        print(f"Using tech file for GDS import ({len(layer_map)} layers)")
                except Exception as e:
                    print(f"Warning: Could not load tech file, using defaults: {e}")
                    layer_map = None

        # Default layer mapping if tech file not available
        if layer_map is None:
            layer_map = {
                (30, 0): 'metal1',
                (50, 0): 'metal2',
                (70, 0): 'metal3',
                (90, 0): 'metal4',
                (110, 0): 'metal5',
                (130, 0): 'metal6',
                (10, 0): 'poly',
                (3, 0): 'ndiff',
                (4, 0): 'pdiff',
                (1, 0): 'nwell',
                (2, 0): 'pwell',
                (20, 0): 'contact',
                (40, 0): 'via1',
                (60, 0): 'via2',
                (80, 0): 'via3',
                (100, 0): 'via4',
                (120, 0): 'via5',
            }

        # Read GDS file
        lib = gdstk.read_gds(filename)

        # Find the cell to import
        if cell_name is None:
            # Get top cells
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
        imported_cell = cls._from_gds_cell_with_constraints(gds_cell, layer_map, add_position_constraints)

        print(f"[OK] Imported cell '{imported_cell.name}' from {filename}")
        print(f"  Children: {len(imported_cell.children)}")
        if add_position_constraints:
            print(f"  Position constraints added to minimize changes from original")

        return imported_cell

    @classmethod
    def _from_gds_cell_with_constraints(cls, gds_cell, layer_map: Dict,
                                       add_constraints: bool = True) -> 'Cell':
        """
        Convert a GDS cell to a Cell object with position constraints

        Args:
            gds_cell: gdstk Cell object
            layer_map: Mapping of (layer, datatype) to layer names
            add_constraints: If True, adds constraints to preserve original positions

        Returns:
            Cell object with position constraints
        """
        cell = cls(gds_cell.name)

        # Process polygons
        for i, polygon in enumerate(gds_cell.polygons):
            layer_key = (polygon.layer, polygon.datatype)
            layer_name = layer_map.get(layer_key, f'layer_{polygon.layer}')

            # Get bounding box
            bbox = polygon.bounding_box()
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]

            # Create leaf cell for this polygon
            leaf_name = f'{gds_cell.name}_{layer_name}_{i}'
            leaf = cls(leaf_name, layer_name)

            # Add to parent
            cell.add_instance(leaf)

            if add_constraints:
                # Store original position as constraint to minimize changes
                # These constraints will try to keep the element at its original position
                # but can be overridden by user-added constraints
                cell.constrain(leaf, f'x1={x1}, y1={y1}, x2={x2}, y2={y2}')

        # Process cell references recursively
        for ref in gds_cell.references:
            child_cell = cls._from_gds_cell_with_constraints(ref.cell, layer_map, add_constraints)
            x_offset, y_offset = ref.origin

            # Apply offset to all positions
            if add_constraints and all(v is not None for v in child_cell.pos_list):
                # Adjust constraints with offset
                for child in child_cell.children:
                    if all(v is not None for v in child.pos_list):
                        child.pos_list[0] += x_offset
                        child.pos_list[1] += y_offset
                        child.pos_list[2] += x_offset
                        child.pos_list[3] += y_offset

            cell.add_instance(child_cell)

        return cell

    def tree(self, show_positions: bool = True, show_layers: bool = True) -> str:
        """
        Display cell hierarchy as a tree structure

        Args:
            show_positions: If True, show position lists
            show_layers: If True, show layer names for leaf cells

        Returns:
            String representation of the tree

        Example output:
            TOP_CELL [0, 0, 100, 100]
            ├── block1 [10, 10, 30, 30] [FROZEN]
            │   ├── metal (metal1) [0, 0, 20, 20]
            │   └── poly (poly) [5, 5, 15, 15]
            └── block2 [50, 10, 70, 30]
                ├── metal (metal1) [0, 0, 20, 20]
                └── poly (poly) [5, 5, 15, 15]
        """
        def _tree_recursive(cell, prefix="", is_last=True):
            lines = []

            # Build cell info string
            info_parts = [cell.name]

            # Add layer name if leaf cell
            if cell.is_leaf and show_layers and cell.layer_name:
                info_parts.append(f"({cell.layer_name})")

            # Add position if requested
            if show_positions and all(v is not None for v in cell.pos_list):
                info_parts.append(f"{cell.pos_list}")

            # Add frozen indicator
            if cell.is_frozen():
                info_parts.append("[FROZEN]")

            # Create the line for this cell
            lines.append(prefix + " ".join(info_parts))

            # Prepare prefix for children
            if prefix == "":
                # Root level
                child_prefix_mid = "├── "
                child_prefix_last = "└── "
                continuation_mid = "│   "
                continuation_last = "    "
            else:
                # Calculate continuation based on whether this is the last child
                if is_last:
                    extension = "    "
                else:
                    extension = "│   "

                child_prefix_mid = prefix[:-4] + extension + "├── "
                child_prefix_last = prefix[:-4] + extension + "└── "
                continuation_mid = prefix[:-4] + extension + "│   "
                continuation_last = prefix[:-4] + extension + "    "

            # Recursively add children
            for i, child in enumerate(cell.children):
                is_last_child = (i == len(cell.children) - 1)

                if is_last_child:
                    child_tree = _tree_recursive(child, child_prefix_last, True)
                else:
                    child_tree = _tree_recursive(child, child_prefix_mid, False)

                lines.extend(child_tree)

            return lines

        # Generate tree starting from root
        result_lines = _tree_recursive(self)
        result = '\n'.join(result_lines)
        print(result)
        return result

    def __repr__(self):
        frozen_str = self._get_frozen_status_str()
        return f"Cell(name={self.name}, pos={self.pos_list}, children={len(self.children)}{frozen_str})"
