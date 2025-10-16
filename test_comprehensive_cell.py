#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for Cell Class
Tests all features and methods in layout_automation.cell.Cell
"""

import sys
import time
from layout_automation.cell import Cell, HAS_ORTOOLS

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'-'*80}{Colors.ENDC}")

def print_pass(text):
    print(f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}: {text}")

def print_fail(text):
    print(f"{Colors.FAIL}✗ FAIL{Colors.ENDC}: {text}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ WARNING{Colors.ENDC}: {text}")

def print_info(text):
    print(f"  {text}")

# Test result tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0
}

def run_test(test_name, test_func):
    """Run a test function and track results"""
    try:
        test_func()
        test_results['passed'] += 1
        return True
    except AssertionError as e:
        print_fail(f"{test_name}: {e}")
        test_results['failed'] += 1
        return False
    except Exception as e:
        print_fail(f"{test_name}: Unexpected error: {e}")
        test_results['failed'] += 1
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# TEST SUITE
# =============================================================================

def test_01_cell_creation_leaf():
    """Test 1: Create leaf cell with layer"""
    print_section("Test 1: Leaf Cell Creation")

    cell = Cell('metal1_rect', 'metal1')

    assert cell.name == 'metal1_rect', "Cell name should be 'metal1_rect'"
    assert cell.is_leaf == True, "Cell should be leaf"
    assert cell.layer_name == 'metal1', "Layer name should be 'metal1'"
    assert len(cell.children) == 0, "Leaf cell should have no children"
    assert cell.pos_list == [None, None, None, None], "Initial position should be None"

    print_pass("Leaf cell created successfully")
    print_info(f"  Name: {cell.name}, Layer: {cell.layer_name}, is_leaf: {cell.is_leaf}")

def test_02_cell_creation_hierarchical():
    """Test 2: Create hierarchical cell with children"""
    print_section("Test 2: Hierarchical Cell Creation")

    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent = Cell('parent', child1, child2)

    assert parent.name == 'parent', "Parent name should be 'parent'"
    assert parent.is_leaf == False, "Parent should not be leaf"
    assert len(parent.children) == 2, "Parent should have 2 children"
    assert parent.children[0] == child1, "First child should be child1"
    assert parent.children[1] == child2, "Second child should be child2"
    assert 'child1' in parent.child_dict, "child1 should be in child_dict"
    assert 'child2' in parent.child_dict, "child2 should be in child_dict"

    print_pass("Hierarchical cell created successfully")
    print_info(f"  Parent: {parent.name}, Children: {[c.name for c in parent.children]}")

def test_03_cell_creation_with_list():
    """Test 3: Create cell with list of children"""
    print_section("Test 3: Cell Creation with List")

    children = [Cell(f'child{i}', f'layer{i}') for i in range(5)]
    parent = Cell('parent', children)

    assert len(parent.children) == 5, "Parent should have 5 children"
    assert all(f'child{i}' in parent.child_dict for i in range(5)), "All children in child_dict"

    print_pass("Cell created with list of children")
    print_info(f"  Children: {[c.name for c in parent.children]}")

def test_04_add_instance_single():
    """Test 4: Add single instance"""
    print_section("Test 4: Add Single Instance")

    parent = Cell('parent')
    child = Cell('child', 'metal1')
    parent.add_instance(child)

    assert len(parent.children) == 1, "Should have 1 child"
    assert parent.children[0] == child, "Child should be added"
    assert 'child' in parent.child_dict, "Child in child_dict"

    print_pass("Single instance added successfully")

def test_05_add_instance_list():
    """Test 5: Add list of instances"""
    print_section("Test 5: Add List of Instances")

    parent = Cell('parent')
    children = [Cell(f'child{i}', f'layer{i}') for i in range(3)]
    parent.add_instance(children)

    assert len(parent.children) == 3, "Should have 3 children"
    assert all(f'child{i}' in parent.child_dict for i in range(3)), "All in child_dict"

    print_pass("List of instances added successfully")

def test_06_constraint_absolute():
    """Test 6: Add absolute constraint"""
    print_section("Test 6: Absolute Constraint")

    parent = Cell('parent')
    child = Cell('child', 'metal1')
    parent.add_instance(child)
    parent.constrain(child, 'x1=10, y1=20, x2=30, y2=40')

    assert len(parent.constraints) == 1, "Should have 1 constraint"
    constraint = parent.constraints[0]
    assert constraint[0] == child, "Constraint on child"
    assert constraint[2] is None, "Absolute constraint has no second cell"

    print_pass("Absolute constraint added")
    print_info(f"  Constraint: {constraint[1]}")

def test_07_constraint_relative():
    """Test 7: Add relative constraint between cells"""
    print_section("Test 7: Relative Constraint")

    parent = Cell('parent')
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent.add_instance([child1, child2])
    parent.constrain(child1, 'sx2+10<ox1', child2)

    assert len(parent.constraints) == 1, "Should have 1 constraint"
    constraint = parent.constraints[0]
    assert constraint[0] == child1, "First cell is child1"
    assert constraint[2] == child2, "Second cell is child2"
    assert 'sx2' in constraint[1] and 'ox1' in constraint[1], "Constraint contains sx2 and ox1"

    print_pass("Relative constraint added")
    print_info(f"  Constraint: {constraint[1]}")

def test_08_constraint_self():
    """Test 8: Add self-constraint"""
    print_section("Test 8: Self-Constraint")

    cell = Cell('cell')
    cell.constrain('x2-x1=100, y2-y1=50')

    assert len(cell.constraints) == 1, "Should have 1 self-constraint"
    constraint = cell.constraints[0]
    assert constraint[0] == cell, "Self-constraint on self"
    assert constraint[2] is None, "Self-constraint has no second cell"
    assert 'x2-x1' in constraint[1], "Constraint defines width"

    print_pass("Self-constraint added")
    print_info(f"  Constraint: {constraint[1]}")

def test_09_constraint_keywords():
    """Test 9: Constraint keywords expansion"""
    print_section("Test 9: Constraint Keywords")

    parent = Cell('parent')
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent.add_instance([child1, child2])

    # Test keyword expansion
    parent.constrain(child1, 'center', child2)

    assert len(parent.constraints) == 1, "Should have 1 constraint"
    constraint = parent.constraints[0]
    # Keywords should be expanded
    assert 'sx1+sx2' in constraint[1] or 'center' not in constraint[1], "Keywords expanded"

    print_pass("Constraint keywords working")
    print_info(f"  Expanded: {constraint[1]}")

def test_10_auto_add_instances():
    """Test 10: Auto-add instances via constrain"""
    print_section("Test 10: Auto-Add Instances")

    parent = Cell('parent')
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')

    # Don't explicitly add children, let constrain do it
    parent.constrain(child1, 'sx1=0, sy1=0')
    assert len(parent.children) == 1, "child1 auto-added"

    parent.constrain(child1, 'sx2+10<ox1', child2)
    assert len(parent.children) == 2, "child2 auto-added"
    assert 'child1' in parent.child_dict and 'child2' in parent.child_dict

    print_pass("Auto-add instances working")
    print_info(f"  Children: {[c.name for c in parent.children]}")

def test_11_solver_basic():
    """Test 11: Basic solver functionality"""
    print_section("Test 11: Basic Solver")

    if not HAS_ORTOOLS:
        print_warning("OR-Tools not available, skipping solver test")
        test_results['warnings'] += 1
        return

    parent = Cell('parent')
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent.add_instance([child1, child2])

    parent.constrain(child1, 'x1=0, y1=0, x2=10, y2=10')
    parent.constrain(child2, 'sx1=ox2+5', child1)
    parent.constrain(child2, 'sy1=oy1, sy2=oy2', child1)

    start_time = time.time()
    result = parent.solver()
    solve_time = time.time() - start_time

    assert result == True, "Solver should succeed"
    assert child1.pos_list[0] == 0, "child1.x1 should be 0"
    assert child1.pos_list[2] == 10, "child1.x2 should be 10"
    assert child2.pos_list[0] == 15, "child2.x1 should be 15 (10+5)"

    print_pass(f"Solver succeeded in {solve_time:.4f}s")
    print_info(f"  child1: {child1.pos_list}")
    print_info(f"  child2: {child2.pos_list}")

def test_12_solver_hierarchical():
    """Test 12: Hierarchical solver"""
    print_section("Test 12: Hierarchical Solver")

    if not HAS_ORTOOLS:
        print_warning("OR-Tools not available, skipping")
        test_results['warnings'] += 1
        return

    # Create 3-level hierarchy
    leaf1 = Cell('leaf1', 'metal1')
    leaf2 = Cell('leaf2', 'metal2')

    mid = Cell('mid', leaf1, leaf2)
    mid.constrain(leaf1, 'x1=0, y1=0, x2=5, y2=5')
    mid.constrain(leaf2, 'sx1=ox2+2, sy1=oy1, sx2=ox2+7, sy2=oy2', leaf1)

    top = Cell('top', mid)
    top.constrain(mid, 'x1=10, y1=10')

    result = top.solver()

    assert result == True, "Hierarchical solver should succeed"
    assert mid.pos_list[0] == 10, "mid.x1 should be 10"
    assert leaf1.pos_list[0] == 0, "leaf1.x1 should be 0 (relative to mid)"

    print_pass("Hierarchical solver succeeded")
    print_info(f"  top: {top.pos_list}")
    print_info(f"  mid: {mid.pos_list}")
    print_info(f"  leaf1: {leaf1.pos_list}")

def test_13_copy_cell():
    """Test 13: Copy cell"""
    print_section("Test 13: Copy Cell")

    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    original = Cell('original', child1, child2)
    original.constrain(child1, 'x1=0, y1=0')
    original.constrain(child1, 'sx2+10<ox1', child2)

    copy = original.copy('copy')

    assert copy.name == 'copy', "Copy should have new name"
    assert len(copy.children) == 2, "Copy should have 2 children"
    assert len(copy.constraints) == 2, "Copy should have 2 constraints"
    assert copy.children[0] != child1, "Children should be deep copied"
    assert copy != original, "Copy is different object"

    print_pass("Cell copied successfully")
    print_info(f"  Original: {original.name}, {len(original.children)} children")
    print_info(f"  Copy: {copy.name}, {len(copy.children)} children")

def test_14_freeze_unfreeze():
    """Test 14: Freeze and unfreeze layout"""
    print_section("Test 14: Freeze/Unfreeze")

    if not HAS_ORTOOLS:
        print_warning("OR-Tools not available, skipping")
        test_results['warnings'] += 1
        return

    cell = Cell('cell')
    child = Cell('child', 'metal1')
    cell.add_instance(child)
    cell.constrain(child, 'x1=5, y1=5, x2=15, y2=15')

    result = cell.solver()
    assert result == True, "Should solve before freeze"

    # Freeze
    cell.freeze_layout()
    assert cell._frozen == True, "Should be frozen"
    assert cell._frozen_bbox is not None, "Frozen bbox cached"

    bbox = cell.get_bbox()
    assert bbox == cell._frozen_bbox, "get_bbox should return cached bbox"

    # Unfreeze
    cell.unfreeze_layout()
    assert cell._frozen == False, "Should be unfrozen"
    assert cell._frozen_bbox is None, "Frozen bbox cleared"

    print_pass("Freeze/unfreeze working")
    print_info(f"  Frozen bbox: {bbox}")

def test_15_is_frozen():
    """Test 15: Check if frozen"""
    print_section("Test 15: Is Frozen")

    cell = Cell('cell')
    assert cell.is_frozen() == False, "Initially not frozen"

    cell.freeze_layout()
    assert cell.is_frozen() == True, "Should be frozen"

    cell.unfreeze_layout()
    assert cell.is_frozen() == False, "Should be unfrozen"

    print_pass("is_frozen() working")

def test_16_get_bbox():
    """Test 16: Get bounding box"""
    print_section("Test 16: Get Bounding Box")

    cell = Cell('cell')
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    cell.add_instance([child1, child2])

    # Manually set positions
    child1.pos_list = [0, 0, 10, 10]
    child2.pos_list = [5, 5, 20, 15]

    bbox = cell.get_bbox()

    assert bbox == (0, 0, 20, 15), f"Bbox should be (0, 0, 20, 15), got {bbox}"

    print_pass("get_bbox() working")
    print_info(f"  BBox: {bbox}")

def test_17_tree_representation():
    """Test 17: Tree representation"""
    print_section("Test 17: Tree Representation")

    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent = Cell('parent', child1, child2)

    tree_str = parent.tree(show_positions=True, show_layers=True)

    assert 'parent' in tree_str, "Tree should contain parent"
    assert 'child1' in tree_str, "Tree should contain child1"
    assert 'child2' in tree_str, "Tree should contain child2"
    assert 'metal1' in tree_str, "Tree should show layer"

    print_pass("tree() representation working")
    print(tree_str)

def test_18_repr():
    """Test 18: String representation"""
    print_section("Test 18: String Representation")

    cell = Cell('test_cell', 'metal1')
    repr_str = repr(cell)

    assert 'Cell' in repr_str, "repr should contain 'Cell'"
    assert 'test_cell' in repr_str, "repr should contain name"

    print_pass("__repr__() working")
    print_info(f"  repr: {repr_str}")

def test_19_get_all_cells():
    """Test 19: Get all cells in hierarchy"""
    print_section("Test 19: Get All Cells")

    leaf1 = Cell('leaf1', 'metal1')
    leaf2 = Cell('leaf2', 'metal2')
    mid = Cell('mid', leaf1, leaf2)
    top = Cell('top', mid)

    all_cells = top._get_all_cells()

    assert len(all_cells) == 4, f"Should have 4 cells, got {len(all_cells)}"
    assert top in all_cells, "Should include top"
    assert mid in all_cells, "Should include mid"
    assert leaf1 in all_cells, "Should include leaf1"
    assert leaf2 in all_cells, "Should include leaf2"

    print_pass("_get_all_cells() working")
    print_info(f"  Found {len(all_cells)} cells")

def test_20_performance_many_children():
    """Test 20: Performance with many children"""
    print_section("Test 20: Performance Test (Many Children)")

    if not HAS_ORTOOLS:
        print_warning("OR-Tools not available, skipping")
        test_results['warnings'] += 1
        return

    parent = Cell('parent')

    # Create 30 children
    for i in range(30):
        child = Cell(f'child{i}', f'layer{i}')
        parent.add_instance(child)
        parent.constrain(child, f'x1={i*10}, y1=0, x2={i*10+5}, y2=5')

    start_time = time.time()
    result = parent.solver()
    solve_time = time.time() - start_time

    assert result == True, "Should solve with many children"

    print_pass(f"Solved 30 children in {solve_time:.4f}s")
    print_info(f"  Parent bbox: {parent.get_bbox()}")

def test_21_constraint_chaining():
    """Test 21: Constraint chaining"""
    print_section("Test 21: Constraint Chaining")

    parent = Cell('parent')
    c1 = Cell('c1', 'metal1')
    c2 = Cell('c2', 'metal2')
    c3 = Cell('c3', 'metal3')

    # Chain constraints using return value
    parent.constrain(c1, 'x1=0, y1=0, x2=10, y2=10') \
          .constrain(c2, 'sx1=ox2+5, sy1=oy1, sy2=oy2', c1) \
          .constrain(c3, 'sx1=ox2+5, sy1=oy1, sy2=oy2', c2)

    assert len(parent.constraints) == 3, "Should have 3 constraints"
    assert len(parent.children) == 3, "Should have 3 children (auto-added)"

    print_pass("Constraint chaining working")
    print_info(f"  Constraints: {len(parent.constraints)}")

def test_22_edge_case_empty_cell():
    """Test 22: Edge case - empty cell"""
    print_section("Test 22: Edge Case - Empty Cell")

    cell = Cell('empty')

    assert len(cell.children) == 0, "Empty cell has no children"
    assert len(cell.constraints) == 0, "Empty cell has no constraints"
    assert cell.is_leaf == False, "Empty non-leaf cell"

    # Get bbox of empty cell
    bbox = cell.get_bbox()
    assert bbox == (float('inf'), float('inf'), float('-inf'), float('-inf')), \
           "Empty cell has invalid bbox"

    print_pass("Empty cell handled correctly")

def test_23_edge_case_single_child():
    """Test 23: Edge case - single child"""
    print_section("Test 23: Edge Case - Single Child")

    if not HAS_ORTOOLS:
        print_warning("OR-Tools not available, skipping")
        test_results['warnings'] += 1
        return

    parent = Cell('parent')
    child = Cell('child', 'metal1')
    parent.add_instance(child)
    parent.constrain(child, 'x1=5, y1=5, x2=15, y2=15')

    result = parent.solver()
    assert result == True, "Should solve with single child"
    assert child.pos_list == [5, 5, 15, 15], "Child positioned correctly"

    print_pass("Single child handled correctly")

def test_24_multiple_constraints_same_cells():
    """Test 24: Multiple constraints on same cells"""
    print_section("Test 24: Multiple Constraints Same Cells")

    parent = Cell('parent')
    c1 = Cell('c1', 'metal1')
    c2 = Cell('c2', 'metal2')
    parent.add_instance([c1, c2])

    # Add multiple constraints
    parent.constrain(c1, 'x1=0, y1=0')
    parent.constrain(c1, 'x2=10, y2=10')
    parent.constrain(c2, 'sx1=ox2+5', c1)
    parent.constrain(c2, 'sy1=oy1', c1)

    assert len(parent.constraints) == 4, "Should have 4 constraints"

    print_pass("Multiple constraints working")

def test_25_deep_hierarchy():
    """Test 25: Deep hierarchy (5 levels)"""
    print_section("Test 25: Deep Hierarchy")

    if not HAS_ORTOOLS:
        print_warning("OR-Tools not available, skipping")
        test_results['warnings'] += 1
        return

    # Build 5-level hierarchy
    level5 = Cell('level5', 'metal1')
    level4 = Cell('level4', level5)
    level4.constrain(level5, 'x1=0, y1=0, x2=5, y2=5')

    level3 = Cell('level3', level4)
    level3.constrain(level4, 'x1=2, y1=2')

    level2 = Cell('level2', level3)
    level2.constrain(level3, 'x1=3, y1=3')

    level1 = Cell('level1', level2)
    level1.constrain(level2, 'x1=1, y1=1')

    result = level1.solver()
    assert result == True, "Deep hierarchy should solve"

    all_cells = level1._get_all_cells()
    assert len(all_cells) == 5, f"Should have 5 levels, got {len(all_cells)}"

    print_pass("Deep hierarchy solved")
    print_info(f"  Depth: 5 levels, Total cells: {len(all_cells)}")

def test_26_child_dict_access():
    """Test 26: Child dictionary access"""
    print_section("Test 26: Child Dictionary Access")

    parent = Cell('parent')
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal2')
    parent.add_instance([child1, child2])

    assert parent.child_dict['child1'] == child1, "child_dict access works"
    assert parent.child_dict['child2'] == child2, "child_dict access works"
    assert 'child3' not in parent.child_dict, "Non-existent child not in dict"

    print_pass("child_dict access working")

def test_27_constraint_string_formats():
    """Test 27: Various constraint string formats"""
    print_section("Test 27: Constraint String Formats")

    parent = Cell('parent')
    c1 = Cell('c1', 'metal1')
    c2 = Cell('c2', 'metal2')

    # Test various formats
    formats = [
        'x1=10',
        'x1=10, y1=20',
        'sx2+10<ox1',
        'sx2=ox1',
        'x2-x1=100',
        'sx1+5<=ox2-3',
    ]

    for fmt in formats:
        try:
            if '=' in fmt and 'x' not in fmt[0]:
                parent.constrain(c1, fmt)
            else:
                parent.constrain(c1, fmt, c2)
        except Exception as e:
            print_fail(f"Format '{fmt}' failed: {e}")
            raise

    print_pass("All constraint formats accepted")
    print_info(f"  Tested {len(formats)} formats")

def test_28_solver_infeasible():
    """Test 28: Solver with infeasible constraints"""
    print_section("Test 28: Infeasible Constraints")

    if not HAS_ORTOOLS:
        print_warning("OR-Tools not available, skipping")
        test_results['warnings'] += 1
        return

    parent = Cell('parent')
    child = Cell('child', 'metal1')
    parent.add_instance(child)

    # Add contradictory constraints
    parent.constrain(child, 'x1=0')
    parent.constrain(child, 'x1=10')  # Contradicts above

    result = parent.solver()

    assert result == False, "Infeasible constraints should fail"

    print_pass("Infeasible constraints detected correctly")

def test_29_position_list_format():
    """Test 29: Position list format [x1, y1, x2, y2]"""
    print_section("Test 29: Position List Format")

    cell = Cell('cell', 'metal1')
    cell.pos_list = [10, 20, 30, 40]

    assert cell.pos_list[0] == 10, "x1 = 10"
    assert cell.pos_list[1] == 20, "y1 = 20"
    assert cell.pos_list[2] == 30, "x2 = 30"
    assert cell.pos_list[3] == 40, "y2 = 40"

    width = cell.pos_list[2] - cell.pos_list[0]
    height = cell.pos_list[3] - cell.pos_list[1]

    assert width == 20, "Width should be 20"
    assert height == 20, "Height should be 20"

    print_pass("Position list format correct")
    print_info(f"  Position: {cell.pos_list}, Width: {width}, Height: {height}")

def test_30_ortools_availability():
    """Test 30: OR-Tools availability check"""
    print_section("Test 30: OR-Tools Availability")

    print_info(f"  HAS_ORTOOLS: {HAS_ORTOOLS}")

    if HAS_ORTOOLS:
        print_pass("OR-Tools is available")
    else:
        print_warning("OR-Tools is NOT available - solver tests skipped")
        test_results['warnings'] += 1

    # Check if Cell class has solver method
    assert hasattr(Cell, 'solver'), "Cell should have solver method"
    print_info("  Cell.solver() method exists")

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    print_header("COMPREHENSIVE CELL CLASS TEST SUITE")

    print(f"\n{Colors.BOLD}Environment:{Colors.ENDC}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  OR-Tools Available: {HAS_ORTOOLS}")

    # List of all tests
    tests = [
        ("Cell Creation - Leaf", test_01_cell_creation_leaf),
        ("Cell Creation - Hierarchical", test_02_cell_creation_hierarchical),
        ("Cell Creation - With List", test_03_cell_creation_with_list),
        ("Add Instance - Single", test_04_add_instance_single),
        ("Add Instance - List", test_05_add_instance_list),
        ("Constraint - Absolute", test_06_constraint_absolute),
        ("Constraint - Relative", test_07_constraint_relative),
        ("Constraint - Self", test_08_constraint_self),
        ("Constraint - Keywords", test_09_constraint_keywords),
        ("Auto-Add Instances", test_10_auto_add_instances),
        ("Solver - Basic", test_11_solver_basic),
        ("Solver - Hierarchical", test_12_solver_hierarchical),
        ("Copy Cell", test_13_copy_cell),
        ("Freeze/Unfreeze", test_14_freeze_unfreeze),
        ("Is Frozen", test_15_is_frozen),
        ("Get Bounding Box", test_16_get_bbox),
        ("Tree Representation", test_17_tree_representation),
        ("String Representation", test_18_repr),
        ("Get All Cells", test_19_get_all_cells),
        ("Performance - Many Children", test_20_performance_many_children),
        ("Constraint Chaining", test_21_constraint_chaining),
        ("Edge Case - Empty Cell", test_22_edge_case_empty_cell),
        ("Edge Case - Single Child", test_23_edge_case_single_child),
        ("Multiple Constraints", test_24_multiple_constraints_same_cells),
        ("Deep Hierarchy", test_25_deep_hierarchy),
        ("Child Dict Access", test_26_child_dict_access),
        ("Constraint String Formats", test_27_constraint_string_formats),
        ("Solver - Infeasible", test_28_solver_infeasible),
        ("Position List Format", test_29_position_list_format),
        ("OR-Tools Availability", test_30_ortools_availability),
    ]

    start_time = time.time()

    # Run all tests
    for test_name, test_func in tests:
        run_test(test_name, test_func)

    total_time = time.time() - start_time

    # Print summary
    print_header("TEST SUMMARY")

    total_tests = test_results['passed'] + test_results['failed']
    pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

    print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}✓ Passed:{Colors.ENDC}   {test_results['passed']}/{total_tests}")
    print(f"  {Colors.FAIL}✗ Failed:{Colors.ENDC}   {test_results['failed']}/{total_tests}")
    print(f"  {Colors.WARNING}⚠ Warnings:{Colors.ENDC} {test_results['warnings']}")
    print(f"  {Colors.BOLD}Pass Rate:{Colors.ENDC}  {pass_rate:.1f}%")
    print(f"  {Colors.BOLD}Total Time:{Colors.ENDC} {total_time:.2f}s")

    if test_results['failed'] == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}ALL TESTS PASSED! ✓{Colors.ENDC}".center(90))
        print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}SOME TESTS FAILED{Colors.ENDC}".center(90))
        print(f"{Colors.FAIL}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
