#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constraint Debugging and Visualization

Provides tools to:
- Visualize constraints on layout
- Check which constraints are satisfied/violated
- Diagnose infeasible constraint systems
- Show constraint dependency graph
"""

from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import numpy as np


class ConstraintDebugger:
    """
    Debug and visualize constraints for a Cell
    """

    def __init__(self, cell):
        """
        Initialize constraint debugger

        Args:
            cell: Cell object from gds_cell.py
        """
        self.cell = cell
        self.constraint_status: List[Dict] = []

    def check_constraints(self, tolerance: float = 0.01) -> List[Dict]:
        """
        Check which constraints are satisfied after solving

        Args:
            tolerance: Numerical tolerance for constraint satisfaction

        Returns:
            List of dictionaries with constraint status info
        """
        self.constraint_status = []

        # Get all cells in hierarchy
        all_cells_dict = self.cell._get_all_elements()[2]

        for cell in all_cells_dict.values():
            for obj1, constraint_str, obj2 in cell.constraints:
                # Parse each constraint
                parsed = cell._parse_constraint(constraint_str, obj1, obj2, {})

                for operator, left_expr, right_expr, var_map in parsed:
                    status = self._evaluate_constraint(
                        obj1, obj2, operator, left_expr, right_expr,
                        var_map, tolerance
                    )
                    self.constraint_status.append(status)

        return self.constraint_status

    def _evaluate_constraint(self, obj1, obj2, operator: str,
                            left_expr: str, right_expr: str,
                            var_map: Dict, tolerance: float) -> Dict:
        """Evaluate a single constraint and return status"""
        # Get actual position values
        if obj1.pos_list[0] is None:
            return {
                'satisfied': False,
                'obj1': obj1.name,
                'obj2': obj2.name if obj2 else None,
                'constraint': f"{left_expr} {operator} {right_expr}",
                'error': 'Not solved',
                'message': 'Positions not yet solved'
            }

        # Build actual value mapping
        if obj2 is None:
            actual_vals = {
                'x1': obj1.pos_list[0], 'y1': obj1.pos_list[1],
                'x2': obj1.pos_list[2], 'y2': obj1.pos_list[3],
                'sx1': obj1.pos_list[0], 'sy1': obj1.pos_list[1],
                'sx2': obj1.pos_list[2], 'sy2': obj1.pos_list[3]
            }
        else:
            actual_vals = {
                'sx1': obj1.pos_list[0], 'sy1': obj1.pos_list[1],
                'sx2': obj1.pos_list[2], 'sy2': obj1.pos_list[3],
                'ox1': obj2.pos_list[0], 'oy1': obj2.pos_list[1],
                'ox2': obj2.pos_list[2], 'oy2': obj2.pos_list[3]
            }

        # Evaluate expressions
        left_val = self._eval_expression(left_expr, actual_vals)
        right_val = self._eval_expression(right_expr, actual_vals)

        # Check constraint satisfaction
        satisfied = False
        error = right_val - left_val

        if operator in ['<', '<=']:
            satisfied = left_val <= right_val + tolerance
        elif operator in ['>', '>=']:
            satisfied = left_val >= right_val - tolerance
        elif operator == '=':
            satisfied = abs(left_val - right_val) <= tolerance
            error = abs(error)

        return {
            'satisfied': satisfied,
            'obj1': obj1.name,
            'obj2': obj2.name if obj2 else None,
            'constraint': f"{left_expr} {operator} {right_expr}",
            'operator': operator,
            'left_value': left_val,
            'right_value': right_val,
            'error': error,
            'message': f"{left_val:.3f} {operator} {right_val:.3f} "
                      f"({'OK' if satisfied else 'VIOLATED'})"
        }

    def _eval_expression(self, expr: str, values: Dict[str, float]) -> float:
        """Evaluate an arithmetic expression with variable substitution"""
        # Simple expression evaluator
        # Replace variable names with their values
        result = expr
        for var, val in sorted(values.items(), key=lambda x: -len(x[0])):
            result = result.replace(var, str(val))

        try:
            return eval(result)
        except:
            return 0.0

    def print_constraint_status(self, show_satisfied: bool = False):
        """
        Print constraint satisfaction status

        Args:
            show_satisfied: If True, also print satisfied constraints
        """
        if not self.constraint_status:
            print("No constraint status available. Run check_constraints() first.")
            return

        violated = [c for c in self.constraint_status if not c['satisfied']]
        satisfied = [c for c in self.constraint_status if c['satisfied']]

        print(f"\n{'='*70}")
        print(f"CONSTRAINT STATUS")
        print(f"{'='*70}")
        print(f"Total: {len(self.constraint_status)} constraints")
        print(f"✓ Satisfied: {len(satisfied)}")
        print(f"✗ Violated: {len(violated)}")
        print(f"{'='*70}\n")

        if violated:
            print("VIOLATED CONSTRAINTS:")
            print("-" * 70)
            for i, c in enumerate(violated, 1):
                obj2_str = f" and {c['obj2']}" if c['obj2'] else ""
                print(f"{i}. {c['obj1']}{obj2_str}")
                print(f"   Constraint: {c['constraint']}")
                print(f"   Status: {c['message']}")
                if isinstance(c['error'], (int, float)):
                    print(f"   Error: {c['error']:.3f}")
                else:
                    print(f"   Error: {c['error']}")
                print()

        if show_satisfied and satisfied:
            print("\nSATISFIED CONSTRAINTS:")
            print("-" * 70)
            for i, c in enumerate(satisfied, 1):
                obj2_str = f" and {c['obj2']}" if c['obj2'] else ""
                print(f"{i}. {c['obj1']}{obj2_str}: {c['constraint']}")

    def visualize_constraints(self, ax=None, show: bool = True):
        """
        Visualize constraints on the layout

        Args:
            ax: Matplotlib axes (creates new if None)
            show: If True, display the plot
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 10))
        else:
            fig = ax.figure

        # Draw the layout first
        self.cell._draw_recursive(ax)

        # Draw constraint arrows
        all_cells_dict = self.cell._get_all_elements()[2]

        for cell in all_cells_dict.values():
            for obj1, constraint_str, obj2 in cell.constraints:
                if obj2 is None:
                    continue  # Skip absolute constraints for visualization

                if obj1.pos_list[0] is None or obj2.pos_list[0] is None:
                    continue  # Skip unsolved objects

                # Get centers
                x1_center = (obj1.pos_list[0] + obj1.pos_list[2]) / 2
                y1_center = (obj1.pos_list[1] + obj1.pos_list[3]) / 2
                x2_center = (obj2.pos_list[0] + obj2.pos_list[2]) / 2
                y2_center = (obj2.pos_list[1] + obj2.pos_list[3]) / 2

                # Draw arrow from obj1 to obj2
                arrow = FancyArrowPatch(
                    (x1_center, y1_center),
                    (x2_center, y2_center),
                    arrowstyle='->',
                    color='red',
                    linewidth=1.5,
                    alpha=0.6,
                    mutation_scale=15
                )
                ax.add_patch(arrow)

                # Add constraint label
                mid_x = (x1_center + x2_center) / 2
                mid_y = (y1_center + y2_center) / 2
                ax.text(mid_x, mid_y, constraint_str,
                       fontsize=7, color='darkred',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

        ax.set_title(f'Layout with Constraint Visualization: {self.cell.name}')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

        if show:
            plt.show()

        return fig

    def diagnose_infeasible(self) -> List[str]:
        """
        Attempt to diagnose why constraint system might be infeasible

        Returns:
            List of diagnostic messages
        """
        diagnostics = []

        # Check for over-constrained objects
        object_constraint_count: Dict[str, int] = {}

        all_cells_dict = self.cell._get_all_elements()[2]

        for cell in all_cells_dict.values():
            for obj1, constraint_str, obj2 in cell.constraints:
                object_constraint_count[obj1.name] = \
                    object_constraint_count.get(obj1.name, 0) + 1
                if obj2:
                    object_constraint_count[obj2.name] = \
                        object_constraint_count.get(obj2.name, 0) + 1

        # Objects with many constraints might be over-constrained
        for obj_name, count in object_constraint_count.items():
            if count > 8:
                diagnostics.append(
                    f"⚠️  {obj_name} has {count} constraints - possibly over-constrained"
                )

        # Check for conflicting equality constraints
        equality_constraints: Dict[str, List[str]] = {}

        for cell in all_cells_dict.values():
            for obj1, constraint_str, obj2 in cell.constraints:
                if '=' in constraint_str and obj2 is not None:
                    key = f"{obj1.name}-{obj2.name}"
                    if key not in equality_constraints:
                        equality_constraints[key] = []
                    equality_constraints[key].append(constraint_str)

        for key, constraints in equality_constraints.items():
            if len(constraints) > 4:
                diagnostics.append(
                    f"⚠️  Objects {key} have {len(constraints)} equality constraints - "
                    f"may be conflicting"
                )

        # Check if any objects are unsolved
        all_polygons, all_instances, _ = self.cell._get_all_elements()
        for poly in all_polygons:
            if poly.pos_list[0] is None:
                diagnostics.append(f"✗ Polygon {poly.name} has no solution")

        for inst in all_instances:
            if inst.pos_list[0] is None:
                diagnostics.append(f"✗ Instance {inst.name} has no solution")

        if not diagnostics:
            diagnostics.append("✓ No obvious issues detected")

        return diagnostics

    def print_diagnostics(self):
        """Print diagnostic information"""
        print(f"\n{'='*70}")
        print("CONSTRAINT SYSTEM DIAGNOSTICS")
        print(f"{'='*70}\n")

        diagnostics = self.diagnose_infeasible()
        for msg in diagnostics:
            print(msg)
        print()


def create_constraint_report(cell, output_file: str = "constraint_report.txt"):
    """
    Create a comprehensive constraint report for a cell

    Args:
        cell: Cell object
        output_file: Output text file path
    """
    debugger = ConstraintDebugger(cell)

    # Check constraints
    debugger.check_constraints()

    # Generate report
    with open(output_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("CONSTRAINT ANALYSIS REPORT\n")
        f.write("="*70 + "\n\n")

        f.write(f"Cell: {cell.name}\n")
        f.write(f"Total constraints: {len(debugger.constraint_status)}\n\n")

        # Satisfied/violated summary
        violated = [c for c in debugger.constraint_status if not c['satisfied']]
        satisfied = [c for c in debugger.constraint_status if c['satisfied']]

        f.write(f"✓ Satisfied: {len(satisfied)}\n")
        f.write(f"✗ Violated: {len(violated)}\n\n")

        # Violated constraints
        if violated:
            f.write("VIOLATED CONSTRAINTS:\n")
            f.write("-"*70 + "\n")
            for i, c in enumerate(violated, 1):
                obj2_str = f" and {c['obj2']}" if c['obj2'] else ""
                f.write(f"{i}. {c['obj1']}{obj2_str}\n")
                f.write(f"   Constraint: {c['constraint']}\n")
                f.write(f"   Status: {c['message']}\n")
                f.write(f"   Error: {c['error']:.3f}\n\n")

        # Diagnostics
        f.write("\n" + "="*70 + "\n")
        f.write("DIAGNOSTICS\n")
        f.write("="*70 + "\n\n")

        diagnostics = debugger.diagnose_infeasible()
        for msg in diagnostics:
            f.write(msg + "\n")

    print(f"Constraint report saved to {output_file}")
