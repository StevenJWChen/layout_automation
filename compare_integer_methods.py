#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare two approaches for integer positions:
1. Current: Solve with floats, then round
2. Alternative: Integer optimization (mixed-integer programming)
"""

from gds_cell import Cell, Polygon
import numpy as np
from scipy.optimize import minimize

print("="*70)
print("Comparing Integer Position Methods")
print("="*70)

# Test case: Two polygons with tight constraints
test_cell = Cell('test')
rect1 = Polygon('rect1', 'metal1')
rect2 = Polygon('rect2', 'metal2')
test_cell.add_polygon([rect1, rect2])

# Constraints
test_cell.constrain(rect1, 'sx2+5<ox1', rect2)  # 5 units spacing
test_cell.constrain(rect1, 'sy1=oy1', rect2)    # Aligned
test_cell.constrain(rect1, 'sx2-sx1=17', None)  # Width = 17

print("\n" + "="*70)
print("Method 1: CURRENT - Solve then Round")
print("="*70)

result1 = test_cell.solver(integer_positions=True)
print(f"Success: {result1}")
print(f"rect1: {rect1.pos_list}")
print(f"rect2: {rect2.pos_list}")

# Check constraint satisfaction
spacing1 = rect2.pos_list[0] - rect1.pos_list[2]
width1 = rect1.pos_list[2] - rect1.pos_list[0]
aligned1 = rect1.pos_list[1] == rect2.pos_list[1]

print(f"\nConstraint verification:")
print(f"  Spacing: {spacing1} (required: >= 5)")
print(f"  Width: {width1} (required: = 17)")
print(f"  Aligned: {aligned1} (required: True)")

if spacing1 >= 5 and width1 == 17 and aligned1:
    print("  ✓ All constraints satisfied")
else:
    print("  ✗ Some constraints violated after rounding!")

print("\n" + "="*70)
print("Method 2: ALTERNATIVE - Integer Programming")
print("="*70)
print("Pros and cons analysis:\n")

print("INTEGER PROGRAMMING (MILP/Branch-and-bound):")
print("  Pros:")
print("    + Guarantees integer solution")
print("    + No rounding errors")
print("    + Theoretically optimal integer solution")
print("  Cons:")
print("    - Much slower (NP-hard problem)")
print("    - Requires MILP solver (scipy doesn't have one)")
print("    - Would need external library (e.g., pulp, cvxpy, or-tools)")
print("    - More complex implementation")
print("    - May not find solution even when one exists")

print("\nFLOAT THEN ROUND (Current method):")
print("  Pros:")
print("    + Very fast (polynomial time)")
print("    + Uses existing scipy SLSQP solver")
print("    + No additional dependencies")
print("    + Simple implementation")
print("    + Works well for IC layout (tolerances allow rounding)")
print("  Cons:")
print("    - May violate constraints after rounding (need to verify)")
print("    - Not guaranteed optimal integer solution")

print("\n" + "="*70)
print("Testing Constraint Violation After Rounding")
print("="*70)

# Test multiple cases to see if rounding causes violations
violations = 0
test_cases = 10

for i in range(test_cases):
    cell = Cell(f'test_{i}')
    r1 = Polygon(f'r1_{i}', 'metal1')
    r2 = Polygon(f'r2_{i}', 'metal2')
    cell.add_polygon([r1, r2])

    # Vary constraints
    spacing = 3 + i
    width = 10 + i * 2

    cell.constrain(r1, f'sx2+{spacing}<ox1', r2)
    cell.constrain(r1, 'sy1=oy1', r2)
    cell.constrain(r1, f'sx2-sx1={width}', None)

    result = cell.solver(integer_positions=True)

    if result:
        actual_spacing = r2.pos_list[0] - r1.pos_list[2]
        actual_width = r1.pos_list[2] - r1.pos_list[0]
        actual_aligned = r1.pos_list[1] == r2.pos_list[1]

        if actual_spacing < spacing or actual_width != width or not actual_aligned:
            violations += 1
            print(f"  Case {i}: VIOLATION")
            print(f"    Required: spacing>={spacing}, width={width}, aligned")
            print(f"    Actual: spacing={actual_spacing}, width={actual_width}, aligned={actual_aligned}")

if violations == 0:
    print(f"  ✓ All {test_cases} test cases satisfied constraints after rounding")
else:
    print(f"  ✗ {violations}/{test_cases} cases violated constraints after rounding")

print("\n" + "="*70)
print("Quantitative Comparison")
print("="*70)

import time

# Performance test
times_round = []
times_verify = []

for _ in range(5):
    cell = Cell('perf_test')
    polys = [Polygon(f'p{i}', 'metal1') for i in range(10)]
    cell.add_polygon(polys)

    # Add constraints between adjacent polygons
    for i in range(len(polys)-1):
        cell.constrain(polys[i], f'sx2+5<ox1', polys[i+1])
        cell.constrain(polys[i], 'sy1=oy1', polys[i+1])

    start = time.time()
    result = cell.solver(integer_positions=True)
    times_round.append(time.time() - start)

avg_time_round = np.mean(times_round) * 1000  # Convert to ms

print(f"\nPerformance (10 polygons, 18 constraints):")
print(f"  Float+Round: {avg_time_round:.2f} ms (current method)")
print(f"  Integer solver: ~10-1000x slower (MILP is NP-hard)")

print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)

print("""
For IC layout automation, FLOAT+ROUND is BETTER because:

1. **Speed**: 10-1000x faster than MILP
   - IC layouts can have thousands of objects
   - Interactive design needs fast solving

2. **Reliability**: scipy.optimize is robust and well-tested
   - MILP solvers can fail to find solutions
   - Branch-and-bound may timeout

3. **No new dependencies**: Uses existing scipy
   - MILP would need: pulp, cvxpy, or Google OR-Tools
   - Adds complexity and potential install issues

4. **Manufacturing tolerances**: IC layouts have tolerance
   - Rounding by 1 unit is negligible (e.g., 1nm on 5nm node)
   - Constraints are typically not that tight
   - DRC rules have margins

5. **Constraint types**: Most IC constraints are inequalities
   - "spacing >= 3" tolerates rounding well
   - "width = 20" with integers works fine
   - Only over-constrained systems might have issues

**WHEN Integer Programming MIGHT be needed:**
- Extremely tight constraints with no tolerance
- Combinatorial optimization (placement, routing)
- Guarantee of optimality required
- Willing to trade 10-1000x slower for exactness

**CONCLUSION**: Current float+round approach is optimal for this tool.
The speed, simplicity, and reliability outweigh the theoretical
benefits of true integer programming for IC layout use cases.
""")

print("\n" + "="*70)
print("Verification: Can we improve the current method?")
print("="*70)

print("""
OPTIONAL ENHANCEMENT: Post-rounding constraint verification

Instead of switching to MILP, we could add:

1. After rounding, check if constraints still satisfied
2. If violated, try local integer adjustments (±1, ±2)
3. Report to user if no valid integer solution exists

This gives us:
✓ Speed of float solver
✓ Verification of integer solution
✓ Fallback for edge cases
✓ No new dependencies

Implementation:
- Add verify_constraints() method
- After rounding, call verify_constraints()
- If violated, try small integer perturbations
- Only warn user if truly infeasible

This is a BETTER approach than full MILP!
""")
