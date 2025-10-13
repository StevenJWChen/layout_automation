#!/usr/bin/env python3
"""Test OR-Tools basic functionality"""

try:
    print("Step 1: Importing OR-Tools...")
    from ortools.sat.python import cp_model
    print("Step 2: OR-Tools imported successfully!")

    print("Step 3: Creating a test model...")
    model = cp_model.CpModel()
    x = model.NewIntVar(0, 10, 'x')
    y = model.NewIntVar(0, 10, 'y')
    model.Add(x + y == 10)

    print("Step 4: Solving...")
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print(f"Step 5: Solution found! x={solver.Value(x)}, y={solver.Value(y)}")
        print("✓ OR-Tools is working correctly!")
    else:
        print(f"Step 5: No solution found, status={status}")

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
