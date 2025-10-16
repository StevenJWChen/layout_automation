#!/usr/bin/env python3
"""
Test Cell class without using the solver (no ortools needed)
"""
import sys

print("=" * 60)
print("CELL.PY TEST - WITHOUT SOLVER")
print("=" * 60)

# Test 1: Import Cell without triggering ortools
print("\nTest 1: Import Cell class")
try:
    # Monkey patch to prevent ortools import
    import sys
    class FakeModule:
        def __init__(self):
            self.cp_model = None
    sys.modules['ortools'] = FakeModule()
    sys.modules['ortools.sat'] = FakeModule()
    sys.modules['ortools.sat.python'] = FakeModule()

    from layout_automation.cell import Cell
    print("✓ Cell class imported successfully")
except Exception as e:
    print(f"✗ Failed to import Cell: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Create leaf cell
print("\nTest 2: Create leaf cell")
try:
    metal1 = Cell('metal1_rect', 'metal1')
    print(f"✓ Created leaf cell: {metal1.name}")
    print(f"  - is_leaf: {metal1.is_leaf}")
    print(f"  - layer_name: {metal1.layer_name}")
    print(f"  - pos_list: {metal1.pos_list}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Create hierarchical cell
print("\nTest 3: Create hierarchical cell")
try:
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent = Cell('parent', child1, child2)
    print(f"✓ Created hierarchical cell: {parent.name}")
    print(f"  - Number of children: {len(parent.children)}")
    print(f"  - Children names: {[c.name for c in parent.children]}")
    print(f"  - is_leaf: {parent.is_leaf}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Add constraints
print("\nTest 4: Add constraints")
try:
    parent.constrain(child1, 'sx2+10<ox1', child2)
    print(f"✓ Added constraint between child1 and child2")
    print(f"  - Number of constraints: {len(parent.constraints)}")
    print(f"  - Constraint: {parent.constraints[0]}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Add absolute constraint
print("\nTest 5: Add absolute constraint")
try:
    parent.constrain(child1, 'sx1=0, sy1=0')
    print(f"✓ Added absolute constraint to child1")
    print(f"  - Total constraints: {len(parent.constraints)}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Copy cell
print("\nTest 6: Copy cell")
try:
    parent_copy = parent.copy()
    print(f"✓ Copied cell: {parent_copy.name}")
    print(f"  - Original has {len(parent.children)} children")
    print(f"  - Copy has {len(parent_copy.children)} children")
    print(f"  - Copy constraint count: {len(parent_copy.constraints)}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Add instance
print("\nTest 7: Add instance")
try:
    child3 = Cell('child3', 'metal3')
    parent.add_instance(child3)
    print(f"✓ Added instance child3 to parent")
    print(f"  - Parent now has {len(parent.children)} children")
    print(f"  - Child in child_dict: {'child3' in parent.child_dict}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Manual positioning (without solver)
print("\nTest 8: Manual positioning")
try:
    child1.pos_list = [0, 0, 10, 10]
    child2.pos_list = [20, 0, 30, 10]
    print(f"✓ Manually set positions")
    print(f"  - child1: {child1.pos_list}")
    print(f"  - child2: {child2.pos_list}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Get bounding box
print("\nTest 9: Get bounding box")
try:
    bbox = parent.get_bbox()
    print(f"✓ Got bounding box: {bbox}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 10: Freeze/unfreeze
print("\nTest 10: Freeze and unfreeze cell")
try:
    parent.freeze()
    print(f"✓ Froze parent cell")
    print(f"  - Is frozen: {parent._frozen}")

    parent.unfreeze()
    print(f"✓ Unfroze parent cell")
    print(f"  - Is frozen: {parent._frozen}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
print("\nNote: Solver tests skipped (requires OR-Tools)")
