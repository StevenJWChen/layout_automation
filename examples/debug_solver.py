#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug the solver to see all constraints
"""

from layout_automation.gds_cell import Cell, Polygon
import numpy as np
from scipy.optimize import minimize

# Create test cell
cell = Cell('test')
rect = Polygon('rect', 'metal1')
cell.add_polygon(rect)
cell.constrain(rect, 'sx2-sx1=20', None)

# Manually replicate what solver() does
all_polygons, _, _ = cell._get_all_elements()

var_counter = {}
for poly in all_polygons:
    poly._get_var_indices(var_counter)

n_vars = len(var_counter) * 4
print(f"Total variables: {n_vars}")

# Build constraints
inequality_constraints = []
equality_constraints = []

# Basic geometric constraints
for poly in all_polygons:
    x1_idx, y1_idx, x2_idx, y2_idx = poly._get_var_indices(var_counter)

    print(f"\nPolygon {poly.name} indices: x1={x1_idx}, y1={y1_idx}, x2={x2_idx}, y2={y2_idx}")

    # x2 > x1
    A = np.zeros(n_vars)
    A[x1_idx] = -1
    A[x2_idx] = 1
    print(f"  Constraint: x2 - x1 >= 0.01")
    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

    # y2 > y1
    A = np.zeros(n_vars)
    A[y1_idx] = -1
    A[y2_idx] = 1
    print(f"  Constraint: y2 - y1 >= 0.01")
    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 0.01})

    # Default size constraints (fix_polygon_size=True)
    # x1 >= 0
    A = np.zeros(n_vars)
    A[x1_idx] = 1
    print(f"  Constraint: x1 >= 0")
    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

    # y1 >= 0
    A = np.zeros(n_vars)
    A[y1_idx] = 1
    print(f"  Constraint: y1 >= 0")
    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x)})

    # x2 - x1 >= 10
    A = np.zeros(n_vars)
    A[x1_idx] = -1
    A[x2_idx] = 1
    print(f"  Constraint: x2 - x1 >= 10")
    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 10})

    # y2 - y1 >= 10
    A = np.zeros(n_vars)
    A[y1_idx] = -1
    A[y2_idx] = 1
    print(f"  Constraint: y2 - y1 >= 10")
    inequality_constraints.append({'type': 'ineq', 'fun': lambda x, A=A: np.dot(A, x) - 10})

# User constraints
print(f"\nUser constraints:")
for obj1, constraint_str, obj2 in cell.constraints:
    print(f"  {constraint_str}")
    parsed = cell._parse_constraint(constraint_str, obj1, obj2, var_counter)

    for operator, left_expr, right_expr, var_map in parsed:
        left_coeffs, left_const = cell._parse_expression_to_coeffs(left_expr, var_map, n_vars)
        right_coeffs, right_const = cell._parse_expression_to_coeffs(right_expr, var_map, n_vars)

        A = left_coeffs - right_coeffs
        b = right_const - left_const

        print(f"    {left_expr} {operator} {right_expr}")
        print(f"    Coeffs: {A}, Constant: {b}")

        if operator == '=':
            print(f"    Adding EQUALITY constraint")
            equality_constraints.append({
                'type': 'eq',
                'fun': lambda x, A=A, b=b: np.dot(A, x) + b
            })

print(f"\nTotal inequality constraints: {len(inequality_constraints)}")
print(f"Total equality constraints: {len(equality_constraints)}")

# Initial guess
x0 = np.zeros(n_vars)
x0[0] = 0    # x1
x0[1] = 0    # y1
x0[2] = 20   # x2
x0[3] = 20   # y2
print(f"\nInitial guess: {x0}")

# Objective
def objective(x):
    x1_idx, y1_idx, x2_idx, y2_idx = 0, 1, 2, 3
    width = x[x2_idx] - x[x1_idx]
    height = x[y2_idx] - x[y1_idx]
    return width * height

# Combine constraints
all_constraints = inequality_constraints + equality_constraints

# Solve
print(f"\nSolving...")
result = minimize(objective, x0, method='SLSQP', constraints=all_constraints,
                 options={'maxiter': 1000, 'ftol': 1e-6})

print(f"Success: {result.success}")
print(f"Message: {result.message}")
print(f"Solution: {result.x}")

if result.success:
    width = result.x[2] - result.x[0]
    height = result.x[3] - result.x[1]
    print(f"Width: {width}")
    print(f"Height: {height}")
