#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/steven/projects/layout_automation')

print("Test 1: Import Cell class")
try:
    from layout_automation.cell import Cell
    print("✓ Cell imported successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\nTest 2: Create a simple leaf cell")
try:
    cell1 = Cell('metal1_rect', 'metal1')
    print(f"✓ Created leaf cell: {cell1.name}")
    print(f"  - is_leaf: {cell1.is_leaf}")
    print(f"  - layer_name: {cell1.layer_name}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\nTest 3: Create a hierarchical cell")
try:
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent = Cell('parent', child1, child2)
    print(f"✓ Created hierarchical cell: {parent.name}")
    print(f"  - Number of children: {len(parent.children)}")
    print(f"  - Children: {[c.name for c in parent.children]}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\nTest 4: Add constraint")
try:
    parent.constrain(child1, 'sx2+10<ox1', child2)
    print(f"✓ Added constraint")
    print(f"  - Number of constraints: {len(parent.constraints)}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\nTest 5: Copy cell")
try:
    parent_copy = parent.copy()
    print(f"✓ Copied cell: {parent_copy.name}")
    print(f"  - Original children: {len(parent.children)}")
    print(f"  - Copy children: {len(parent_copy.children)}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("All basic tests passed! ✓")
