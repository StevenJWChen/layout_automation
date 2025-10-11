#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integer position optimizer with post-rounding verification and adjustment

This module provides intelligent rounding that ensures constraints
remain satisfied after converting to integers.
"""

import numpy as np
from typing import List, Tuple, Callable


def round_with_constraint_verification(
    solution: np.ndarray,
    constraints: List[dict],
    max_adjustment: int = 3,
    verbose: bool = False
) -> Tuple[np.ndarray, bool]:
    """
    Round solution to integers while maintaining constraint satisfaction

    Args:
        solution: Float solution from optimizer
        constraints: List of constraint dictionaries with 'type' and 'fun'
        max_adjustment: Maximum ±adjustment to try for each variable
        verbose: Print debugging information

    Returns:
        (rounded_solution, success) tuple
    """
    # Start with simple rounding
    rounded = np.round(solution).astype(int)

    # Check if constraints are satisfied
    if all_constraints_satisfied(rounded, constraints):
        if verbose:
            print("✓ Simple rounding satisfies all constraints")
        return rounded, True

    if verbose:
        print("⚠ Simple rounding violates constraints, attempting adjustment...")

    # Try local adjustments
    best_solution = rounded.copy()
    best_violation = measure_constraint_violation(rounded, constraints)

    # Identify which variables are near constraint boundaries
    critical_vars = find_critical_variables(solution, rounded, constraints)

    if verbose:
        print(f"  Critical variables to adjust: {len(critical_vars)}")

    # Try small integer adjustments to critical variables
    for var_idx in critical_vars[:10]:  # Limit to top 10 critical variables
        for delta in range(-max_adjustment, max_adjustment + 1):
            if delta == 0:
                continue

            test_solution = best_solution.copy()
            test_solution[var_idx] += delta

            if all_constraints_satisfied(test_solution, constraints):
                if verbose:
                    print(f"  ✓ Adjusted variable {var_idx} by {delta:+d}")
                return test_solution, True

            # Track best partial solution
            violation = measure_constraint_violation(test_solution, constraints)
            if violation < best_violation:
                best_violation = violation
                best_solution = test_solution.copy()

    # If we can't satisfy all constraints, return best effort
    if verbose:
        print(f"  ⚠ Could not fully satisfy constraints")
        print(f"  Remaining violation: {best_violation:.3f}")

    return best_solution, False


def all_constraints_satisfied(solution: np.ndarray, constraints: List[dict],
                              tolerance: float = 1e-6) -> bool:
    """Check if all constraints are satisfied"""
    for constraint in constraints:
        value = constraint['fun'](solution)

        if constraint['type'] == 'ineq':
            # Inequality: fun(x) >= 0
            if value < -tolerance:
                return False
        elif constraint['type'] == 'eq':
            # Equality: fun(x) == 0
            if abs(value) > tolerance:
                return False

    return True


def measure_constraint_violation(solution: np.ndarray,
                                 constraints: List[dict]) -> float:
    """Measure total constraint violation (0 = all satisfied)"""
    total_violation = 0.0

    for constraint in constraints:
        value = constraint['fun'](solution)

        if constraint['type'] == 'ineq':
            # Violation if value < 0
            if value < 0:
                total_violation += abs(value)
        elif constraint['type'] == 'eq':
            # Violation is abs(value)
            total_violation += abs(value)

    return total_violation


def find_critical_variables(float_solution: np.ndarray,
                           int_solution: np.ndarray,
                           constraints: List[dict],
                           num_vars: int = 20) -> List[int]:
    """
    Identify variables that are most critical for constraint satisfaction

    Variables are critical if:
    1. They are far from integer values (large rounding error)
    2. They appear in violated constraints
    """
    n = len(float_solution)
    criticality = np.zeros(n)

    # Factor 1: Rounding error (distance from integer)
    rounding_error = np.abs(float_solution - int_solution)
    criticality += rounding_error

    # Factor 2: Check which variables appear in violated constraints
    for constraint in constraints:
        value_int = constraint['fun'](int_solution)
        value_float = constraint['fun'](float_solution)

        is_violated = False
        if constraint['type'] == 'ineq' and value_int < 0:
            is_violated = True
        elif constraint['type'] == 'eq' and abs(value_int) > 1e-6:
            is_violated = True

        if is_violated:
            # Estimate which variables affect this constraint
            # by checking sensitivity
            for i in range(n):
                test = int_solution.copy().astype(float)
                test[i] += 0.1
                sensitivity = abs(constraint['fun'](test) - value_int)
                if sensitivity > 1e-3:
                    criticality[i] += 1.0

    # Return indices sorted by criticality
    critical_indices = np.argsort(criticality)[::-1]
    return critical_indices[:num_vars].tolist()


def smart_integer_rounding(solution: np.ndarray,
                           constraints: List[dict],
                           verbose: bool = False) -> Tuple[np.ndarray, bool, str]:
    """
    Smart rounding that tries multiple strategies

    Returns:
        (rounded_solution, success, message) tuple
    """
    # Strategy 1: Simple rounding
    rounded = np.round(solution).astype(int)
    if all_constraints_satisfied(rounded, constraints):
        return rounded, True, "Simple rounding succeeded"

    # Strategy 2: Floor then adjust up
    floored = np.floor(solution).astype(int)
    if all_constraints_satisfied(floored, constraints):
        return floored, True, "Floor rounding succeeded"

    # Strategy 3: Ceil then adjust down
    ceiled = np.ceil(solution).astype(int)
    if all_constraints_satisfied(ceiled, constraints):
        return ceiled, True, "Ceil rounding succeeded"

    # Strategy 4: Local adjustments
    rounded, success = round_with_constraint_verification(
        solution, constraints, max_adjustment=3, verbose=verbose
    )

    if success:
        return rounded, True, "Local adjustment succeeded"
    else:
        return rounded, False, "Could not satisfy all constraints with integers"
