#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug the constraint parser
"""

from gds_cell import Cell, Polygon
import numpy as np

# Create test cell
cell = Cell('test')
rect = Polygon('rect', 'metal1')
cell.add_polygon(rect)

# Build var counter
var_counter = {}
rect._get_var_indices(var_counter)
n_vars = len(var_counter) * 4

print(f"Variables: {n_vars}")
print(f"var_counter: {var_counter}")
print(f"rect indices: {rect._get_var_indices(var_counter)}")

# Test parsing
var_map = {
    'x1': 0, 'y1': 1, 'x2': 2, 'y2': 3,
    'sx1': 0, 'sy1': 1, 'sx2': 2, 'sy2': 3
}

# Parse 'sx2-sx1=20'
left_expr = 'sx2-sx1'
right_expr = '20'

print(f"\nParsing: {left_expr} = {right_expr}")

left_coeffs, left_const = cell._parse_expression_to_coeffs(left_expr, var_map, n_vars)
right_coeffs, right_const = cell._parse_expression_to_coeffs(right_expr, var_map, n_vars)

print(f"Left coeffs: {left_coeffs}")
print(f"Left const: {left_const}")
print(f"Right coeffs: {right_coeffs}")
print(f"Right const: {right_const}")

# The constraint should be: left_coeffs * x + left_const = right_coeffs * x + right_const
# Rearranged: (left_coeffs - right_coeffs) * x = right_const - left_const

A = left_coeffs - right_coeffs
b = right_const - left_const

print(f"\nFinal constraint coeffs (A): {A}")
print(f"Final constraint constant (b): {b}")
print(f"This means: {A[2]}*x2 + {A[0]}*x1 = {b}")
print(f"Which is: x2 - x1 = {b}")

# Now try with solver
cell.constrain(rect, 'sx2-sx1=20', None)
print(f"\nAttempting to solve...")
result = cell.solver()
print(f"Result: {result}")
if result:
    print(f"rect.pos_list: {rect.pos_list}")
    width = rect.pos_list[2] - rect.pos_list[0]
    print(f"Width: {width}")
