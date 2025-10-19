#!/usr/bin/env python3
"""
Centering with Tolerance - Proper Implementation

This module provides functions to achieve centering with tolerance fallback
by modifying the solver's objective function to minimize deviation from center.
"""

import sys

# Check for OR-Tools availability (same as in cell.py)
HAS_ORTOOLS = False
cp_model = None
if sys.version_info.major == 3 and sys.version_info.minor < 13:
    try:
        from ortools.sat.python import cp_model
        HAS_ORTOOLS = True
    except (ImportError, OSError, Exception):
        HAS_ORTOOLS = False
        cp_model = None


class CenteringConstraint:
    """
    Represents a centering constraint with tolerance

    This is used to track which cells should be centered, so the solver
    can minimize deviation from perfect centering.
    """

    def __init__(self, child, ref_obj, tolerance_x=0, tolerance_y=0, center_x=True, center_y=True):
        """
        Args:
            child: Child cell to center
            ref_obj: Reference object (usually parent)
            tolerance_x: X tolerance in layout units (0 = exact)
            tolerance_y: Y tolerance in layout units (0 = exact)
            center_x: Whether to center in X
            center_y: Whether to center in Y
        """
        self.child = child
        self.ref_obj = ref_obj
        self.tolerance_x = tolerance_x
        self.tolerance_y = tolerance_y
        self.center_x = center_x
        self.center_y = center_y


def add_centering_with_tolerance(parent, child, ref_obj, tolerance_x=0, tolerance_y=None,
                                  center_x=True, center_y=True):
    """
    Add centering constraint with tolerance

    This function adds tolerance constraints and marks the cells for
    centered objective optimization.

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to center
        ref_obj: Reference object (usually parent or another child)
        tolerance_x: X tolerance in layout units (0 = exact centering required)
        tolerance_y: Y tolerance (defaults to tolerance_x if not specified)
        center_x: Whether to center in X
        center_y: Whether to center in Y

    Returns:
        CenteringConstraint object (for later use in solver)

    Example:
        parent = Cell('parent')
        child = Cell('child', 'metal1')

        # Add centering with ±5 unit tolerance
        centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=5)

        # Later, pass to custom solver:
        parent.solver_with_centering([centering])
    """
    if tolerance_y is None:
        tolerance_y = tolerance_x

    # Add tolerance constraints
    if center_x:
        tolerance_x_sum = tolerance_x * 2
        if tolerance_x == 0:
            # Exact centering (hard constraint)
            parent.constrain(child, 'sx1+sx2=ox1+ox2', ref_obj)
        else:
            # Tolerance range (soft constraint via objective)
            parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_x_sum}', ref_obj)
            parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_x_sum}', ref_obj)

    if center_y:
        tolerance_y_sum = tolerance_y * 2
        if tolerance_y == 0:
            # Exact centering (hard constraint)
            parent.constrain(child, 'sy1+sy2=oy1+oy2', ref_obj)
        else:
            # Tolerance range (soft constraint via objective)
            parent.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_y_sum}', ref_obj)
            parent.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_y_sum}', ref_obj)

    # Return constraint object for solver
    return CenteringConstraint(child, ref_obj, tolerance_x, tolerance_y, center_x, center_y)


def solver_with_centering_objective(parent_cell, centering_constraints=None,
                                     fix_leaf_positions=True, integer_positions=True):
    """
    Solve with custom objective that minimizes deviation from centering

    This is a custom solver that modifies the objective function to prefer
    centered solutions within the tolerance range.

    Args:
        parent_cell: Top-level cell to solve
        centering_constraints: List of CenteringConstraint objects
        fix_leaf_positions: Standard solver parameter
        integer_positions: Standard solver parameter

    Returns:
        True if solution found, False otherwise

    Example:
        parent = Cell('parent')
        child = Cell('child', 'metal1')

        parent.constrain('width=100, height=100')
        parent.constrain(child, 'swidth=30, sheight=40')

        # Add centering with tolerance
        centering = add_centering_with_tolerance(parent, child, parent, tolerance_x=10)

        # Solve with centering objective
        solver_with_centering_objective(parent, [centering])
    """
    if not HAS_ORTOOLS:
        raise RuntimeError(
            "OR-Tools is not available. Please install it with: pip install ortools"
        )

    if centering_constraints is None:
        centering_constraints = []

    all_cells = parent_cell._get_all_cells()

    # Create OR-Tools model
    model = cp_model.CpModel()

    # Build variable counter and create integer variables
    var_counter = {}
    var_objects = {}

    coord_min = 0
    coord_max = 10000

    # Create variables for all cells
    for cell in all_cells:
        cell_id = id(cell)
        if cell_id not in var_counter:
            start_idx = len(var_counter) * 4
            var_counter[cell_id] = start_idx

            x1_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_x1')
            y1_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_y1')
            x2_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_x2')
            y2_var = model.NewIntVar(coord_min, coord_max, f'{cell.name}_y2')

            var_objects[start_idx] = x1_var
            var_objects[start_idx + 1] = y1_var
            var_objects[start_idx + 2] = x2_var
            var_objects[start_idx + 3] = y2_var

    # Add basic geometric constraints
    for cell in all_cells:
        x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
        x1_var = var_objects[x1_idx]
        y1_var = var_objects[y1_idx]
        x2_var = var_objects[x2_idx]
        y2_var = var_objects[y2_idx]

        if cell._frozen and cell._frozen_bbox is not None:
            x1_f, y1_f, x2_f, y2_f = cell._frozen_bbox
            width = x2_f - x1_f
            height = y2_f - y1_f
            model.Add(x2_var - x1_var == width)
            model.Add(y2_var - y1_var == height)
        elif cell._fixed and len(cell._fixed_offsets) > 0:
            max_x_offset = max(offset[2] for offset in cell._fixed_offsets.values())
            max_y_offset = max(offset[3] for offset in cell._fixed_offsets.values())
            model.Add(x2_var - x1_var == max_x_offset)
            model.Add(y2_var - y1_var == max_y_offset)
        else:
            model.Add(x2_var >= x1_var + 1)
            model.Add(y2_var >= y1_var + 1)

    # Fix leaf positions if requested
    if fix_leaf_positions:
        for cell in all_cells:
            if cell.is_leaf:
                x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
                x1_var = var_objects[x1_idx]
                y1_var = var_objects[y1_idx]
                x2_var = var_objects[x2_idx]
                y2_var = var_objects[y2_idx]

                model.Add(x1_var >= 0)
                model.Add(y1_var >= 0)
                model.Add(x2_var - x1_var >= 1)
                model.Add(y2_var - y1_var >= 1)

    # Add parent-child bounding constraints
    parent_cell._add_parent_child_constraints_ortools(model, var_counter, var_objects)

    # Add all user constraints
    parent_cell._add_constraints_recursive_ortools(model, var_counter, var_objects)

    # ========================================================================
    # CUSTOM OBJECTIVE: Minimize deviation from centering
    # ========================================================================
    deviation_vars = []

    for constraint in centering_constraints:
        child = constraint.child
        ref_obj = constraint.ref_obj

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

        # X deviation (only if centering in X and has tolerance)
        if constraint.center_x and constraint.tolerance_x > 0:
            # deviation_x = |child_x1 + child_x2 - (ref_x1 + ref_x2)|
            deviation_x = model.NewIntVar(0, coord_max * 4, f'{child.name}_x_deviation')

            # deviation_x >= (child_x1 + child_x2) - (ref_x1 + ref_x2)
            model.Add(deviation_x >= child_x1 + child_x2 - ref_x1 - ref_x2)

            # deviation_x >= (ref_x1 + ref_x2) - (child_x1 + child_x2)
            model.Add(deviation_x >= ref_x1 + ref_x2 - child_x1 - child_x2)

            deviation_vars.append(deviation_x)

        # Y deviation (only if centering in Y and has tolerance)
        if constraint.center_y and constraint.tolerance_y > 0:
            deviation_y = model.NewIntVar(0, coord_max * 4, f'{child.name}_y_deviation')

            model.Add(deviation_y >= child_y1 + child_y2 - ref_y1 - ref_y2)
            model.Add(deviation_y >= ref_y1 + ref_y2 - child_y1 - child_y2)

            deviation_vars.append(deviation_y)

    # Set objective
    if deviation_vars:
        # Minimize total deviation from centering
        model.Minimize(sum(deviation_vars))
        print(f"Minimizing centering deviation for {len(centering_constraints)} constraint(s)")
    else:
        # No centering constraints with tolerance - use default objective
        objective_terms = []
        for cell in all_cells:
            x1_idx, y1_idx, x2_idx, y2_idx = cell._get_var_indices(var_counter)
            x2_var = var_objects[x2_idx]
            y2_var = var_objects[y2_idx]
            objective_terms.append(x2_var)
            objective_terms.append(y2_var)
        model.Minimize(sum(objective_terms))

    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0
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

        # Update parent bounds
        parent_cell._update_parent_bounds()
        parent_cell._update_all_fixed_positions()

        if status == cp_model.OPTIMAL:
            print(f"Optimal solution found in {solver.WallTime():.2f}s")
        else:
            print(f"Feasible solution found in {solver.WallTime():.2f}s")

        return True
    else:
        print(f"Solver failed with status: {solver.StatusName(status)}")
        return False


def center_and_solve(parent, child, tolerance=0, tolerance_x=None, tolerance_y=None,
                     ref_obj=None, center_x=True, center_y=True):
    """
    SIMPLEST WAY: Center child with tolerance and solve in one call

    This is the easiest way to center with tolerance and no left/bottom bias.
    Just call this instead of parent.solver()

    Args:
        parent: Parent cell
        child: Child to center
        tolerance: Tolerance for both X and Y (default: 0 = exact)
        tolerance_x: X tolerance (overrides tolerance if specified)
        tolerance_y: Y tolerance (overrides tolerance if specified)
        ref_obj: Reference object (defaults to parent)
        center_x: Center in X direction (default: True)
        center_y: Center in Y direction (default: True)

    Returns:
        True if solved successfully, False otherwise

    Examples:
        # Exact centering
        center_and_solve(parent, child, tolerance=0)

        # ±10 unit tolerance (TRUE CENTERING, NO BIAS)
        center_and_solve(parent, child, tolerance=10)

        # Different X and Y tolerances
        center_and_solve(parent, child, tolerance_x=15, tolerance_y=10)

        # Center child1 relative to child2
        center_and_solve(parent, child1, tolerance=5, ref_obj=child2)

        # X-only centering
        center_and_solve(parent, child, tolerance=5, center_y=False)

    Usage:
        from layout_automation.cell import Cell
        from layout_automation.centering_with_tolerance import center_and_solve

        parent = Cell('parent')
        child = Cell('child', 'metal1')
        parent.constrain('x1=0, y1=0, x2=100, y2=100')
        parent.constrain(child, 'swidth=30, sheight=40')

        # ONE LINE - center with tolerance, no bias!
        center_and_solve(parent, child, tolerance=10)
    """
    if ref_obj is None:
        ref_obj = parent

    # Determine actual tolerances
    if tolerance_x is None:
        tolerance_x = tolerance
    if tolerance_y is None:
        tolerance_y = tolerance

    if tolerance_x == 0 and tolerance_y == 0:
        # Exact centering - use standard solver
        if center_x and center_y:
            parent.constrain(child, 'center', ref_obj)
        elif center_x:
            parent.constrain(child, 'xcenter', ref_obj)
        elif center_y:
            parent.constrain(child, 'ycenter', ref_obj)

        return parent.solver()
    else:
        # Tolerance > 0 - use custom solver for true centering
        centering = add_centering_with_tolerance(
            parent, child, ref_obj,
            tolerance_x=tolerance_x,
            tolerance_y=tolerance_y,
            center_x=center_x,
            center_y=center_y
        )

        return solver_with_centering_objective(parent, [centering])


# Export functions
__all__ = [
    'CenteringConstraint',
    'add_centering_with_tolerance',
    'solver_with_centering_objective',
    'center_and_solve',  # SIMPLE ONE-LINE FUNCTION
]
