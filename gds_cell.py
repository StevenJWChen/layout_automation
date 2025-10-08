#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDS-style Cell class for constraint-based layout automation
Follows GDS-II format conventions: Cell -> Polygons + CellInstances
"""

from __future__ import annotations
import re
import copy as copy_module
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.optimize import linprog, minimize
import numpy as np
import gdstk


class Polygon:
    """
    Polygon on a specific layer (GDS primitive)

    Attributes:
        name (str): Polygon name/identifier
        layer (str): Layer name (e.g., 'metal1', 'poly')
        pos_list (list): Position [x1, y1, x2, y2] - bounding box
    """

    def __init__(self, name: str, layer: str):
        """
        Initialize Polygon

        Args:
            name: Polygon identifier
            layer: Layer name
        """
        self.name = name
        self.layer = layer
        self.pos_list = [None, None, None, None]  # [x1, y1, x2, y2]
        self._var_indices = None

    def _get_var_indices(self, var_counter: Dict[int, int]) -> Tuple[int, int, int, int]:
        """Get or create variable indices for this polygon's position"""
        obj_id = id(self)
        if obj_id not in var_counter:
            start_idx = len(var_counter) * 4
            var_counter[obj_id] = start_idx
        start_idx = var_counter[obj_id]
        return (start_idx, start_idx + 1, start_idx + 2, start_idx + 3)

    def copy(self) -> 'Polygon':
        """Create a deep copy"""
        new_poly = copy_module.deepcopy(self)
        new_poly._var_indices = None  # Reset variable indices
        return new_poly

    def __repr__(self):
        return f"Polygon(name={self.name}, layer={self.layer}, pos={self.pos_list})"


class CellInstance:
    """
    Instance (reference) of a Cell at a specific position
    Similar to SREF/AREF in GDS-II

    Attributes:
        name (str): Instance name
        cell (Cell): Reference to master cell
        pos_list (list): Position [x1, y1, x2, y2] of this instance
    """

    def __init__(self, name: str, cell: 'Cell'):
        """
        Initialize CellInstance

        Args:
            name: Instance identifier
            cell: Master cell to reference
        """
        self.name = name
        self.cell = cell  # Reference to master cell
        self.pos_list = [None, None, None, None]
        self._var_indices = None

    def _get_var_indices(self, var_counter: Dict[int, int]) -> Tuple[int, int, int, int]:
        """Get or create variable indices for this instance's position"""
        obj_id = id(self)
        if obj_id not in var_counter:
            start_idx = len(var_counter) * 4
            var_counter[obj_id] = start_idx
        start_idx = var_counter[obj_id]
        return (start_idx, start_idx + 1, start_idx + 2, start_idx + 3)

    def copy(self) -> 'CellInstance':
        """Create a deep copy with new variable indices"""
        new_inst = copy_module.deepcopy(self)
        new_inst._var_indices = None
        return new_inst

    def __repr__(self):
        return f"CellInstance(name={self.name}, cell={self.cell.name}, pos={self.pos_list})"


class Cell:
    """
    GDS Cell - container for polygons and cell instances

    Attributes:
        name (str): Cell name
        polygons (list): List of Polygon objects
        instances (list): List of CellInstance objects
        constraints (list): List of constraint tuples
    """

    def __init__(self, name: str):
        """
        Initialize Cell

        Args:
            name: Cell name
        """
        self.name = name
        self.polygons = []  # Polygons in this cell
        self.instances = []  # Cell instances in this cell
        self.constraints = []  # Constraints between elements

    def add_polygon(self, polygon: Union[Polygon, List[Polygon]]):
        """
        Add polygon(s) to this cell

        Args:
            polygon: Single Polygon or list of Polygons
        """
        if isinstance(polygon, Polygon):
            self.polygons.append(polygon)
        elif isinstance(polygon, list):
            self.polygons.extend([p for p in polygon if isinstance(p, Polygon)])
        else:
            raise TypeError("Argument must be Polygon or list of Polygons")

    def add_instance(self, instance: Union[CellInstance, List[CellInstance]]):
        """
        Add cell instance(s) to this cell

        Args:
            instance: Single CellInstance or list of CellInstances
        """
        if isinstance(instance, CellInstance):
            self.instances.append(instance)
        elif isinstance(instance, list):
            self.instances.extend([i for i in instance if isinstance(i, CellInstance)])
        else:
            raise TypeError("Argument must be CellInstance or list of CellInstances")

    def constrain(self, obj1: Union[Polygon, CellInstance],
                  constraint_str: str,
                  obj2: Union[Polygon, CellInstance]):
        """
        Add constraint between two objects (polygons or instances)

        Args:
            obj1: First object (uses 's' prefix in constraint string)
            obj2: Second object (uses 'o' prefix in constraint string)
            constraint_str: Constraint string, e.g., 'sx1<ox2+3, sy2+5<oy1'
        """
        self.constraints.append((obj1, constraint_str, obj2))

    def _parse_constraint(self, constraint_str: str,
                         obj1: Union[Polygon, CellInstance],
                         obj2: Union[Polygon, CellInstance],
                         var_counter: Dict[int, int]) -> List[Tuple[str, str, str, str]]:
        """Parse constraint string into constraint tuples for optimization"""
        parsed_constraints = []

        # Get variable indices for both objects
        s_vars = obj1._get_var_indices(var_counter)
        o_vars = obj2._get_var_indices(var_counter)

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
        """Parse an arithmetic expression string into coefficient vector for linear optimization"""
        coeffs = np.zeros(n_vars)
        constant = 0.0

        tokens = re.findall(r'[so][xy][12]|\d+\.?\d*|[+\-*/()]', expr_str)

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

    def _get_all_elements(self) -> Tuple[List[Polygon], List[CellInstance], List[Cell]]:
        """
        Get all polygons, instances, and unique cells in hierarchy

        Returns:
            Tuple of (all_polygons, all_instances, all_unique_cells)
        """
        all_polygons = list(self.polygons)
        all_instances = list(self.instances)
        all_cells = {id(self): self}  # Track unique cells by id

        # Recursively get elements from instances
        for instance in self.instances:
            # Add the instance's cell if not already added
            if id(instance.cell) not in all_cells:
                all_cells[id(instance.cell)] = instance.cell
                # Get elements from that cell
                sub_polys, sub_insts, sub_cells_dict = instance.cell._get_all_elements()
                all_polygons.extend(sub_polys)
                all_instances.extend(sub_insts)
                all_cells.update(sub_cells_dict)

        return all_polygons, all_instances, all_cells

    def solver(self, fix_polygon_size: bool = True) -> bool:
        """
        Solve constraints to determine positions using SciPy optimization

        Args:
            fix_polygon_size: If True, assigns default sizes to polygons

        Returns:
            True if solution found, False otherwise
        """
        # Get all elements (deduplicates polygons from shared cells)
        all_polygons, all_instances, all_cells_dict = self._get_all_elements()

        # Build variable counter
        var_counter = {}
        for poly in all_polygons:
            poly._get_var_indices(var_counter)
        for inst in all_instances:
            inst._get_var_indices(var_counter)

        n_vars = len(var_counter) * 4

        # Build constraints in SciPy format
        inequality_constraints = []
        equality_constraints = []

        # Add basic geometric constraints (x2 > x1, y2 > y1)
        for poly in all_polygons:
            x1_idx, y1_idx, x2_idx, y2_idx = poly._get_var_indices(var_counter)

            # x2 > x1
            A = np.zeros(n_vars)
            A[x1_idx] = -1
            A[x2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

            # y2 > y1
            A = np.zeros(n_vars)
            A[y1_idx] = -1
            A[y2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

            # Default size for polygons
            if fix_polygon_size:
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

        for inst in all_instances:
            x1_idx, y1_idx, x2_idx, y2_idx = inst._get_var_indices(var_counter)

            # x2 > x1
            A = np.zeros(n_vars)
            A[x1_idx] = -1
            A[x2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

            # y2 > y1
            A = np.zeros(n_vars)
            A[y1_idx] = -1
            A[y2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

            # Default size
            A = np.zeros(n_vars)
            A[x1_idx] = -1
            A[x2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 10})

            A = np.zeros(n_vars)
            A[y1_idx] = -1
            A[y2_idx] = 1
            inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 10})

        # Add user constraints from all cells
        for cell in all_cells_dict.values():
            for obj1, constraint_str, obj2 in cell.constraints:
                parsed_constraints = cell._parse_constraint(constraint_str, obj1, obj2, var_counter)

                for operator, left_expr, right_expr, var_map in parsed_constraints:
                    left_coeffs, left_const = cell._parse_expression_to_coeffs(left_expr, var_map, n_vars)
                    right_coeffs, right_const = cell._parse_expression_to_coeffs(right_expr, var_map, n_vars)

                    A = left_coeffs - right_coeffs
                    b = right_const - left_const

                    if operator in ['<', '<=']:
                        inequality_constraints.append({
                            'type': 'ineq',
                            'fun': lambda x, A=A, b=b: -np.dot(A, x) - b
                        })
                    elif operator in ['>', '>=']:
                        inequality_constraints.append({
                            'type': 'ineq',
                            'fun': lambda x, A=A, b=b: np.dot(A, x) + b
                        })
                    elif operator == '=':
                        equality_constraints.append({
                            'type': 'eq',
                            'fun': lambda x, A=A, b=b: np.dot(A, x) + b
                        })

        # Initial guess
        x0 = np.zeros(n_vars)
        for i, poly in enumerate(all_polygons):
            x1_idx, y1_idx, x2_idx, y2_idx = poly._get_var_indices(var_counter)
            x0[x1_idx] = i * 30
            x0[y1_idx] = i * 30
            x0[x2_idx] = i * 30 + 20
            x0[y2_idx] = i * 30 + 20
        for i, inst in enumerate(all_instances):
            x1_idx, y1_idx, x2_idx, y2_idx = inst._get_var_indices(var_counter)
            base = (len(all_polygons) + i) * 30
            x0[x1_idx] = base
            x0[y1_idx] = base
            x0[x2_idx] = base + 20
            x0[y2_idx] = base + 20

        # Objective: minimize sum of areas
        def objective(x):
            total = 0
            for poly in all_polygons:
                x1_idx, y1_idx, x2_idx, y2_idx = poly._get_var_indices(var_counter)
                width = x[x2_idx] - x[x1_idx]
                height = x[y2_idx] - x[y1_idx]
                total += width * height
            for inst in all_instances:
                x1_idx, y1_idx, x2_idx, y2_idx = inst._get_var_indices(var_counter)
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
            # Extract solutions for polygons
            for poly in all_polygons:
                x1_idx, y1_idx, x2_idx, y2_idx = poly._get_var_indices(var_counter)
                poly.pos_list = [
                    float(result.x[x1_idx]),
                    float(result.x[y1_idx]),
                    float(result.x[x2_idx]),
                    float(result.x[y2_idx])
                ]

            # Extract solutions for instances
            for inst in all_instances:
                x1_idx, y1_idx, x2_idx, y2_idx = inst._get_var_indices(var_counter)
                inst.pos_list = [
                    float(result.x[x1_idx]),
                    float(result.x[y1_idx]),
                    float(result.x[x2_idx]),
                    float(result.x[y2_idx])
                ]

            # Update instance bounds to match their cell contents
            self._update_instance_bounds()

            return True
        else:
            print(f"Optimization failed: {result.message}")
            return False

    def _add_instance_constraints_recursive(self):
        """
        Recursively process nested instances (no longer needed for SciPy version)
        """
        for instance in self.instances:
            instance.cell._add_instance_constraints_recursive()


    def _update_instance_bounds(self):
        """
        Update instance bounds based on cell size

        Note: Instance positions are solved by Z3 based on user constraints.
        This method adjusts the instance SIZE to match its cell's bounding box,
        while preserving the solved position.
        """
        for instance in self.instances:
            # Get cell bounding box size
            if len(instance.cell.polygons) > 0:
                x1_vals = [p.pos_list[0] for p in instance.cell.polygons if p.pos_list[0] is not None]
                y1_vals = [p.pos_list[1] for p in instance.cell.polygons if p.pos_list[1] is not None]
                x2_vals = [p.pos_list[2] for p in instance.cell.polygons if p.pos_list[2] is not None]
                y2_vals = [p.pos_list[3] for p in instance.cell.polygons if p.pos_list[3] is not None]

                if x1_vals and instance.pos_list[0] is not None:
                    # Calculate cell bounding box
                    cell_width = max(x2_vals) - min(x1_vals)
                    cell_height = max(y2_vals) - min(y1_vals)

                    # Update instance size to match cell, keeping solved position
                    inst_x1 = instance.pos_list[0]
                    inst_y1 = instance.pos_list[1]
                    instance.pos_list[2] = inst_x1 + cell_width
                    instance.pos_list[3] = inst_y1 + cell_height

            # Recursively update nested instances
            instance.cell._update_instance_bounds()

    def draw(self, solve_first: bool = True, ax=None, show: bool = True):
        """
        Visualize the layout

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
            fig, ax = plt.subplots(figsize=(10, 10))
        else:
            fig = ax.figure

        # Draw all elements
        self._draw_recursive(ax)

        ax.set_aspect('equal')
        ax.autoscale()
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Layout: {self.name}')

        plt.draw()

        return fig

    def _draw_recursive(self, ax, level: int = 0):
        """Recursively draw all polygons and instances"""
        # Layer colors
        layer_colors = {
            'metal1': 'blue',
            'metal2': 'red',
            'metal3': 'green',
            'metal4': 'orange',
            'poly': 'purple',
            'diff': 'brown',
        }

        # Draw polygons in this cell
        for poly in self.polygons:
            if all(v is not None for v in poly.pos_list):
                x1, y1, x2, y2 = poly.pos_list
                width = x2 - x1
                height = y2 - y1

                color = layer_colors.get(poly.layer, 'gray')

                rect = patches.Rectangle(
                    (x1, y1), width, height,
                    linewidth=2, edgecolor='black', facecolor=color, alpha=0.6
                )
                ax.add_patch(rect)

                # Add label
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                label = f"{poly.name}\n({poly.layer})"
                ax.text(cx, cy, label, ha='center', va='center', fontsize=8, weight='bold')

        # Draw instances - show bounds with dashed lines
        for instance in self.instances:
            if all(v is not None for v in instance.pos_list):
                x1, y1, x2, y2 = instance.pos_list
                width = x2 - x1
                height = y2 - y1

                colors = ['darkblue', 'darkred', 'darkgreen', 'darkorange', 'darkviolet']
                edge_color = colors[level % len(colors)]

                rect = patches.Rectangle(
                    (x1, y1), width, height,
                    linewidth=2, edgecolor=edge_color, facecolor='none',
                    linestyle='--', alpha=0.8
                )
                ax.add_patch(rect)

                # Add label
                label = f"{instance.name}\n[{instance.cell.name}]"
                ax.text(x1, y2 + 1, label, ha='left', va='bottom', fontsize=9,
                       weight='bold', color=edge_color, style='italic')

            # Recursively draw instance contents
            instance.cell._draw_recursive(ax, level + 1)

    def copy(self) -> 'Cell':
        """Create a deep copy of this cell"""
        new_cell = copy_module.deepcopy(self)
        return new_cell

    def export_gds(self, filename: str, unit: float = 1e-6, precision: float = 1e-9):
        """
        Export layout to GDS file

        Args:
            filename: Output GDS file path
            unit: User unit in meters (default: 1e-6 = 1 micron)
            precision: Precision in meters (default: 1e-9 = 1 nanometer)
        """
        # Create GDS library
        lib = gdstk.Library(name="LAYOUT", unit=unit, precision=precision)

        # Layer mapping: layer name to (layer_number, datatype)
        layer_map = {
            'metal1': (1, 0),
            'metal2': (2, 0),
            'metal3': (3, 0),
            'metal4': (4, 0),
            'poly': (10, 0),
            'diff': (11, 0),
        }

        # Convert this cell and all referenced cells to GDS
        gds_cells_dict = {}  # Track converted cells by id to avoid duplicates
        self._convert_to_gds(lib, gds_cells_dict, layer_map)

        # Write to file
        lib.write_gds(filename)
        print(f"Exported to {filename}")

    def _convert_to_gds(self, lib: gdstk.Library, gds_cells_dict: Dict, layer_map: Dict) -> gdstk.Cell:
        """
        Convert this Cell to gdstk.Cell recursively

        Args:
            lib: GDS library
            gds_cells_dict: Dictionary tracking converted cells
            layer_map: Mapping of layer names to (layer, datatype) tuples

        Returns:
            gdstk.Cell object
        """
        # Check if already converted
        cell_id = id(self)
        if cell_id in gds_cells_dict:
            return gds_cells_dict[cell_id]

        # Create new GDS cell
        gds_cell = gdstk.Cell(self.name)
        lib.add(gds_cell)
        gds_cells_dict[cell_id] = gds_cell

        # Add polygons
        for poly in self.polygons:
            if all(v is not None for v in poly.pos_list):
                x1, y1, x2, y2 = poly.pos_list
                # Create rectangle as polygon
                points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

                # Get layer/datatype
                layer, datatype = layer_map.get(poly.layer, (0, 0))

                # Create polygon
                gds_poly = gdstk.Polygon(points, layer=layer, datatype=datatype)
                gds_cell.add(gds_poly)

        # Add instances (references)
        for instance in self.instances:
            # Recursively convert referenced cell
            ref_gds_cell = instance.cell._convert_to_gds(lib, gds_cells_dict, layer_map)

            # Calculate origin (lower-left corner of instance)
            if all(v is not None for v in instance.pos_list):
                origin = (instance.pos_list[0], instance.pos_list[1])

                # Create reference
                ref = gdstk.Reference(ref_gds_cell, origin=origin)
                gds_cell.add(ref)

        return gds_cell

    def import_gds(self, filename: str, top_cell_name: Optional[str] = None):
        """
        Import layout from GDS file

        Args:
            filename: Input GDS file path
            top_cell_name: Name of top cell to import (if None, uses first cell)

        Note: This creates a new Cell structure from the GDS.
              Constraints are not preserved in GDS format.
        """
        # Read GDS library
        lib = gdstk.read_gds(filename)

        # Get top cell
        if top_cell_name:
            gds_top_cell = None
            for cell in lib.cells:
                if cell.name == top_cell_name:
                    gds_top_cell = cell
                    break
            if gds_top_cell is None:
                raise ValueError(f"Cell '{top_cell_name}' not found in GDS file")
        else:
            if len(lib.cells) == 0:
                raise ValueError("No cells found in GDS file")
            gds_top_cell = lib.cells[0]

        # Layer mapping: (layer_number, datatype) to layer name
        reverse_layer_map = {
            (1, 0): 'metal1',
            (2, 0): 'metal2',
            (3, 0): 'metal3',
            (4, 0): 'metal4',
            (10, 0): 'poly',
            (11, 0): 'diff',
        }

        # Convert GDS to our Cell structure
        converted_cells = {}  # Track converted cells by name
        self._import_from_gds_cell(gds_top_cell, lib, converted_cells, reverse_layer_map)

        print(f"Imported from {filename}, top cell: {gds_top_cell.name}")

    def _import_from_gds_cell(self, gds_cell: gdstk.Cell, lib: gdstk.Library,
                              converted_cells: Dict, reverse_layer_map: Dict):
        """
        Import GDS cell into this Cell

        Args:
            gds_cell: Source gdstk.Cell
            lib: GDS library
            converted_cells: Dictionary of already converted cells
            reverse_layer_map: Mapping of (layer, datatype) to layer names
        """
        # Update name
        self.name = gds_cell.name

        # Clear existing content
        self.polygons = []
        self.instances = []
        self.constraints = []

        # Mark this cell as converted
        converted_cells[gds_cell.name] = self

        # Import polygons
        for gds_poly in gds_cell.polygons:
            # Get bounding box
            bbox = gds_poly.bounding_box()
            if bbox is not None:
                (x1, y1), (x2, y2) = bbox

                # Get layer name
                layer_key = (gds_poly.layer, gds_poly.datatype)
                layer_name = reverse_layer_map.get(layer_key, f"layer{gds_poly.layer}")

                # Create polygon
                poly = Polygon(f"poly_{len(self.polygons)}", layer_name)
                poly.pos_list = [float(x1), float(y1), float(x2), float(y2)]
                self.polygons.append(poly)

        # Import references (instances)
        for ref in gds_cell.references:
            # Get referenced cell
            ref_gds_cell = ref.cell

            # Convert or retrieve referenced cell
            if ref_gds_cell.name in converted_cells:
                ref_cell = converted_cells[ref_gds_cell.name]
            else:
                ref_cell = Cell(ref_gds_cell.name)
                ref_cell._import_from_gds_cell(ref_gds_cell, lib, converted_cells, reverse_layer_map)

            # Create instance
            inst = CellInstance(f"inst_{len(self.instances)}", ref_cell)

            # Set position from origin
            if ref.origin is not None:
                origin_x, origin_y = ref.origin

                # Calculate bounds (need to get cell size)
                if len(ref_cell.polygons) > 0:
                    # Get cell bounding box
                    x1_vals = [p.pos_list[0] for p in ref_cell.polygons]
                    y1_vals = [p.pos_list[1] for p in ref_cell.polygons]
                    x2_vals = [p.pos_list[2] for p in ref_cell.polygons]
                    y2_vals = [p.pos_list[3] for p in ref_cell.polygons]

                    cell_width = max(x2_vals) - min(x1_vals)
                    cell_height = max(y2_vals) - min(y1_vals)

                    inst.pos_list = [
                        float(origin_x),
                        float(origin_y),
                        float(origin_x + cell_width),
                        float(origin_y + cell_height)
                    ]

            self.instances.append(inst)

    def __repr__(self):
        return f"Cell(name={self.name}, polygons={len(self.polygons)}, instances={len(self.instances)})"
