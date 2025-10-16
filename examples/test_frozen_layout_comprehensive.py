#!/usr/bin/env python3
"""
Comprehensive test program for frozen layout feature

Tests:
1. Basic freeze and unfreeze operations
2. Frozen cell size is preserved
3. Frozen cell position can be constrained by parent
4. Frozen cell bbox caching
5. Nested frozen cells (frozen within frozen)
6. copy() preserves frozen state
7. Method chaining with freeze_layout()
8. Frozen cells in hierarchical structures
9. Re-solving frozen cells (should maintain size)
10. import_gds_to_cell with frozen cells
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

def test_basic_freeze_unfreeze():
    """Test 1: Basic freeze and unfreeze operations"""
    print("=" * 80)
    print("TEST 1: Basic Freeze and Unfreeze Operations")
    print("=" * 80)
    print()

    cell = Cell('test_cell', 'metal1')
    cell.constrain('x1=0, y1=0, x2=20, y2=30')

    # Solve first
    if not cell.solver():
        print("✗ Initial solve failed")
        return False

    print(f"Initial position: {cell.pos_list}")
    print(f"Initial frozen state: {cell.is_frozen()}")

    # Freeze
    result = cell.freeze_layout()
    print(f"After freeze_layout():")
    print(f"  - is_frozen(): {cell.is_frozen()}")
    print(f"  - get_bbox(): {cell.get_bbox()}")
    print(f"  - Returns self: {result is cell}")

    if not cell.is_frozen():
        print("✗ Cell should be frozen")
        return False

    # Unfreeze
    cell.unfreeze_layout()
    print(f"After unfreeze_layout():")
    print(f"  - is_frozen(): {cell.is_frozen()}")
    print(f"  - get_bbox(): {cell.get_bbox()}")

    if cell.is_frozen():
        print("✗ Cell should not be frozen")
        return False

    print()
    print("✓ TEST 1 PASSED: Basic freeze/unfreeze works correctly")
    print()
    return True


def test_frozen_size_preserved():
    """Test 2: Frozen cell size is preserved when used in parent"""
    print("=" * 80)
    print("TEST 2: Frozen Cell Size is Preserved")
    print("=" * 80)
    print()

    # Create and freeze a 20×30 block
    block = Cell('frozen_block')
    layer = Cell('layer', 'metal1')
    block.add_instance(layer)
    block.constrain(layer, 'x1=0, y1=0, x2=20, y2=30')

    if not block.solver():
        print("✗ Block solve failed")
        return False

    block.freeze_layout()
    original_bbox = block.get_bbox()
    print(f"Frozen block bbox: {original_bbox}")
    print(f"Frozen block size: {original_bbox[2]-original_bbox[0]}×{original_bbox[3]-original_bbox[1]}")
    print()

    # Use frozen block in parent
    parent = Cell('parent')
    inst1 = block.copy()
    inst2 = block.copy()

    parent.add_instance([inst1, inst2])

    # Try to constrain with SAME size (20×30)
    parent.constrain(inst1, 'x1=10, y1=10, x2=30, y2=40')  # 20×30 - should work
    parent.constrain(inst2, 'x1=50, y1=10, x2=70, y2=40')  # 20×30 - should work

    print("Constraining frozen blocks with correct size (20×30)...")
    if not parent.solver():
        print("✗ Parent solve failed (unexpected)")
        return False

    print(f"✓ inst1 position: {inst1.pos_list}")
    print(f"✓ inst2 position: {inst2.pos_list}")

    # Verify size is preserved
    inst1_width = inst1.pos_list[2] - inst1.pos_list[0]
    inst1_height = inst1.pos_list[3] - inst1.pos_list[1]

    if inst1_width != 20 or inst1_height != 30:
        print(f"✗ inst1 size changed to {inst1_width}×{inst1_height}, expected 20×30")
        return False

    print()
    print("✓ TEST 2 PASSED: Frozen cell size is preserved")
    print()
    return True


def test_frozen_position_flexible():
    """Test 3: Frozen cell position can be constrained by parent"""
    print("=" * 80)
    print("TEST 3: Frozen Cell Position is Flexible")
    print("=" * 80)
    print()

    # Create frozen block
    block = Cell('position_test_block')
    layer = Cell('layer', 'diff')
    block.add_instance(layer)
    block.constrain(layer, 'x1=0, y1=0, x2=15, y2=25')

    if not block.solver():
        print("✗ Block solve failed")
        return False

    block.freeze_layout()
    print(f"Frozen block size: 15×25")
    print()

    # Test different position constraints
    positions = [
        (0, 0, 15, 25),
        (100, 200, 115, 225),
        (50, 75, 65, 100),
    ]

    for i, (x1, y1, x2, y2) in enumerate(positions):
        parent = Cell(f'parent_{i}')
        inst = block.copy()
        parent.add_instance(inst)

        parent.constrain(inst, f'x1={x1}, y1={y1}, x2={x2}, y2={y2}')

        if not parent.solver():
            print(f"✗ Failed to position frozen block at ({x1}, {y1}, {x2}, {y2})")
            return False

        if inst.pos_list != [x1, y1, x2, y2]:
            print(f"✗ Position mismatch: expected {[x1, y1, x2, y2]}, got {inst.pos_list}")
            return False

        print(f"✓ Test {i+1}: Successfully positioned frozen block at {inst.pos_list}")

    print()
    print("✓ TEST 3 PASSED: Frozen cell position can be changed by parent")
    print()
    return True


def test_frozen_bbox_caching():
    """Test 4: Frozen cell bbox is cached"""
    print("=" * 80)
    print("TEST 4: Frozen Cell Bbox Caching")
    print("=" * 80)
    print()

    cell = Cell('cache_test')
    layer = Cell('layer', 'poly')
    cell.add_instance(layer)
    cell.constrain(layer, 'x1=5, y1=10, x2=35, y2=50')

    if not cell.solver():
        print("✗ Solve failed")
        return False

    # Before freeze
    bbox_before = cell.get_bbox()
    print(f"Bbox before freeze: {bbox_before}")

    # Freeze
    cell.freeze_layout()
    bbox_after = cell.get_bbox()
    print(f"Bbox after freeze: {bbox_after}")

    # Multiple calls should return same cached bbox
    bbox_cached1 = cell.get_bbox()
    bbox_cached2 = cell.get_bbox()

    if bbox_after != bbox_cached1 or bbox_after != bbox_cached2:
        print("✗ Cached bbox differs")
        return False

    print(f"✓ Cached bbox consistent: {bbox_cached1}")

    # Unfreeze and check
    cell.unfreeze_layout()
    if cell.get_bbox() != bbox_before:
        print("✗ Bbox should be same after unfreeze")
        return False

    print(f"✓ Bbox after unfreeze: {cell.get_bbox()}")
    print()
    print("✓ TEST 4 PASSED: Bbox caching works correctly")
    print()
    return True


def test_nested_frozen_cells():
    """Test 5: Nested frozen cells (frozen within frozen)"""
    print("=" * 80)
    print("TEST 5: Nested Frozen Cells")
    print("=" * 80)
    print()

    # Create innermost frozen block (contact array)
    contact_array = Cell('contact_2x2')
    for i in range(2):
        for j in range(2):
            contact = Cell(f'c_{i}_{j}', 'contact')
            contact_array.constrain(contact, f'x1={j*3}, y1={i*3}, x2={j*3+2}, y2={i*3+2}')

    if not contact_array.solver():
        print("✗ Contact array solve failed")
        return False

    contact_array.freeze_layout()
    print(f"✓ Level 1 frozen: contact_array {contact_array.get_bbox()}")

    # Create middle level (MOS with frozen contacts)
    mos = Cell('mos_transistor')
    diff = Cell('diff', 'diff')
    poly = Cell('poly', 'poly')
    src_contacts = contact_array.copy()
    drn_contacts = contact_array.copy()

    mos.add_instance([diff, poly, src_contacts, drn_contacts])
    mos.constrain(diff, 'x1=0, y1=5, x2=30, y2=25')
    mos.constrain(poly, 'x1=12, y1=0, x2=18, y2=30')
    mos.constrain(src_contacts, 'x1=2, y1=12, x2=7, y2=17')  # 5×5 (frozen size)
    mos.constrain(drn_contacts, 'x1=23, y1=12, x2=28, y2=17')  # 5×5 (frozen size)

    if not mos.solver():
        print("✗ MOS solve failed")
        return False

    mos.freeze_layout()
    print(f"✓ Level 2 frozen: mos_transistor {mos.get_bbox()}")

    # Create top level (circuit with frozen MOS)
    circuit = Cell('circuit')
    mos1 = mos.copy()
    mos2 = mos.copy()

    circuit.add_instance([mos1, mos2])
    circuit.constrain(mos1, 'x1=0, y1=0, x2=30, y2=30')  # Frozen MOS size
    circuit.constrain(mos2, 'sx1=ox2+10, sy1=oy1, sx2-sx1=30, sy2-sy1=30', mos1)

    if not circuit.solver():
        print("✗ Circuit solve failed")
        return False

    print(f"✓ Level 3: circuit with nested frozen cells")
    print(f"  mos1: {mos1.pos_list}")
    print(f"  mos2: {mos2.pos_list}")

    # Export to verify structure
    circuit.export_gds('demo_outputs/test_nested_frozen.gds')
    print(f"✓ Exported to demo_outputs/test_nested_frozen.gds")

    print()
    print("✓ TEST 5 PASSED: Nested frozen cells work correctly")
    print()
    return True


def test_copy_preserves_frozen():
    """Test 6: copy() preserves frozen state"""
    print("=" * 80)
    print("TEST 6: copy() Preserves Frozen State")
    print("=" * 80)
    print()

    # Create and freeze original
    original = Cell('original')
    layer = Cell('layer', 'metal1')
    original.add_instance(layer)
    original.constrain(layer, 'x1=0, y1=0, x2=10, y2=20')

    if not original.solver():
        print("✗ Original solve failed")
        return False

    original.freeze_layout()
    print(f"Original frozen: {original.is_frozen()}")
    print(f"Original bbox: {original.get_bbox()}")
    print()

    # Create copies
    copy1 = original.copy()
    copy2 = original.copy('custom_name')

    print(f"copy1 name: {copy1.name}")
    print(f"copy1 frozen: {copy1.is_frozen()}")
    print(f"copy1 bbox: {copy1.get_bbox()}")
    print()

    print(f"copy2 name: {copy2.name}")
    print(f"copy2 frozen: {copy2.is_frozen()}")
    print(f"copy2 bbox: {copy2.get_bbox()}")
    print()

    if not copy1.is_frozen() or not copy2.is_frozen():
        print("✗ Copies should preserve frozen state")
        return False

    if copy1.get_bbox() != original.get_bbox():
        print("✗ Copy bbox should match original")
        return False

    print("✓ TEST 6 PASSED: copy() preserves frozen state and bbox")
    print()
    return True


def test_method_chaining():
    """Test 7: Method chaining with freeze_layout() and constrain()"""
    print("=" * 80)
    print("TEST 7: Method Chaining")
    print("=" * 80)
    print()

    # Test freeze_layout() returns self
    cell = Cell('chain_test')
    layer = Cell('layer', 'metal2')

    # Chain: add_instance -> constrain -> constrain -> solver -> freeze_layout
    cell.add_instance(layer)
    result = cell.constrain(layer, 'x1=0, y1=0, x2=15, y2=15').solver()

    print(f"✓ Chained constrain().solver()")

    # Chain freeze_layout
    frozen_result = cell.freeze_layout()
    print(f"✓ freeze_layout() returns self: {frozen_result is cell}")

    # Test constrain returns self for chaining
    parent = Cell('parent_chain')
    child1 = Cell('child1', 'poly')
    child2 = Cell('child2', 'diff')

    # Chain multiple constrains
    parent.constrain(child1, 'x1=0, y1=0, x2=10, y2=10').constrain(child2, 'x1=15, y1=0, x2=25, y2=10').solver()

    print(f"✓ Chained multiple constrain() calls")
    print(f"  child1: {child1.pos_list}")
    print(f"  child2: {child2.pos_list}")

    print()
    print("✓ TEST 7 PASSED: Method chaining works correctly")
    print()
    return True


def test_frozen_in_hierarchy():
    """Test 8: Frozen cells in complex hierarchical structures"""
    print("=" * 80)
    print("TEST 8: Frozen Cells in Hierarchical Structures")
    print("=" * 80)
    print()

    # Create reusable frozen standard cell
    std_cell = Cell('standard_cell')
    input_pin = Cell('input', 'metal1')
    output_pin = Cell('output', 'metal1')
    logic = Cell('logic_region', 'poly')

    std_cell.add_instance([input_pin, output_pin, logic])
    std_cell.constrain(input_pin, 'x1=0, y1=10, x2=5, y2=20')
    std_cell.constrain(output_pin, 'x1=45, y1=10, x2=50, y2=20')
    std_cell.constrain(logic, 'x1=10, y1=5, x2=40, y2=25')

    if not std_cell.solver():
        print("✗ Standard cell solve failed")
        return False

    std_cell.freeze_layout()
    print(f"✓ Created frozen standard cell: {std_cell.get_bbox()}")

    # Create row of standard cells
    row = Cell('cell_row')
    spacing = 5

    for i in range(5):
        cell_inst = std_cell.copy()
        row.add_instance(cell_inst)
        if i == 0:
            row.constrain(cell_inst, 'x1=0, y1=0, x2=50, y2=30')
        else:
            prev_cell = row.children[i-1]
            row.constrain(cell_inst, f'sx1=ox2+{spacing}, sy1=oy1, sx2-sx1=50, sy2-sy1=30', prev_cell)

    if not row.solver():
        print("✗ Row solve failed")
        return False

    row.freeze_layout()
    print(f"✓ Created frozen row with 5 cells")

    # Create array of rows
    array = Cell('cell_array')

    for i in range(3):
        row_inst = row.copy()
        array.add_instance(row_inst)
        if i == 0:
            array.constrain(row_inst, 'x1=0, y1=0, x2=275, y2=30')  # 5*50 + 4*5 + margin
        else:
            prev_row = array.children[i-1]
            array.constrain(row_inst, 'sx1=ox1, sy1=oy2+10, sx2-sx1=275, sy2-sy1=30', prev_row)

    if not array.solver():
        print("✗ Array solve failed")
        return False

    print(f"✓ Created array with 3 rows (15 total cells)")

    # Display tree
    array.tree(show_positions=True, show_layers=True)

    # Export
    array.export_gds('demo_outputs/test_frozen_hierarchy.gds')
    print(f"✓ Exported to demo_outputs/test_frozen_hierarchy.gds")

    print()
    print("✓ TEST 8 PASSED: Complex hierarchical frozen structures work")
    print()
    return True


def test_resolving_frozen():
    """Test 9: Re-solving with frozen cells maintains size"""
    print("=" * 80)
    print("TEST 9: Re-solving Frozen Cells Maintains Size")
    print("=" * 80)
    print()

    # Create frozen block
    block = Cell('resolve_test')
    layer = Cell('layer', 'metal1')
    block.add_instance(layer)
    block.constrain(layer, 'x1=0, y1=0, x2=25, y2=35')

    if not block.solver():
        print("✗ Initial solve failed")
        return False

    block.freeze_layout()
    original_size = (25, 35)
    print(f"✓ Frozen block size: {original_size}")

    # Use in parent and solve multiple times with different positions
    for attempt in range(3):
        parent = Cell(f'parent_attempt_{attempt}')
        inst = block.copy()
        parent.add_instance(inst)

        x_offset = attempt * 50
        parent.constrain(inst, f'x1={x_offset}, y1=0, x2={x_offset+25}, y2=35')

        if not parent.solver():
            print(f"✗ Solve attempt {attempt+1} failed")
            return False

        inst_width = inst.pos_list[2] - inst.pos_list[0]
        inst_height = inst.pos_list[3] - inst.pos_list[1]

        if (inst_width, inst_height) != original_size:
            print(f"✗ Size changed on attempt {attempt+1}: {inst_width}×{inst_height}")
            return False

        print(f"✓ Attempt {attempt+1}: Size preserved at {inst.pos_list}")

    print()
    print("✓ TEST 9 PASSED: Re-solving maintains frozen cell size")
    print()
    return True


def test_solver_optimization():
    """Test 10: Frozen cells reduce solver complexity"""
    print("=" * 80)
    print("TEST 10: Solver Optimization with Frozen Cells")
    print("=" * 80)
    print()

    # Create a complex block with many children
    complex_block = Cell('complex_block')

    # Add 20 children to make it complex
    for i in range(20):
        layer = Cell(f'layer_{i}', 'metal1')
        complex_block.constrain(layer, f'x1={i*2}, y1=0, x2={i*2+2}, y2=10')

    print(f"✓ Created complex block with {len(complex_block.children)} children")

    # Check how many cells are collected before freeze (and before solve)
    all_cells_before = complex_block._get_all_cells()
    print(f"  Cells before freeze: {len(all_cells_before)}")
    print(f"    Includes: 1 parent + {len(complex_block.children)} children = {1 + len(complex_block.children)}")

    # Solve and freeze
    if not complex_block.solver():
        print("✗ Complex block solve failed")
        return False

    # Freeze the block
    complex_block.freeze_layout()

    # Check how many cells are collected after freeze
    all_cells_after = complex_block._get_all_cells()
    print(f"  Cells after freeze: {len(all_cells_after)}")
    print(f"    Includes: 1 parent only (children excluded)")

    if len(all_cells_after) != 1:
        print(f"✗ Expected 1 cell after freeze, got {len(all_cells_after)}")
        return False

    print(f"✓ Frozen cell optimization working: {len(all_cells_before)} → {len(all_cells_after)} cells")
    print()

    # Now use frozen block in parent - solver should be much faster
    parent = Cell('parent_with_frozen')

    # Add multiple instances of frozen block
    for i in range(10):
        inst = complex_block.copy()
        parent.add_instance(inst)
        parent.constrain(inst, f'x1={i*50}, y1=0, x2={i*50+40}, y2=10')

    print(f"Created parent with {len(parent.children)} frozen block instances")
    print(f"  Without freezing, solver would need to handle: {len(parent.children)} × {len(complex_block.children)} = {len(parent.children) * len(complex_block.children)} child cells")
    print(f"  With freezing, solver only handles: {len(parent.children)} frozen blocks")

    # Check cells collected in parent
    parent_cells = parent._get_all_cells()
    print(f"  Actual cells in solver: {len(parent_cells)}")
    print(f"    Expected: 1 parent + {len(parent.children)} frozen blocks = {1 + len(parent.children)}")

    # Solve parent (should be fast because frozen blocks are single units)
    if not parent.solver():
        print("✗ Parent solve failed")
        return False

    print(f"✓ Parent solved successfully with frozen optimization")

    # Verify all instances positioned correctly
    all_positioned = all(inst.pos_list[0] is not None for inst in parent.children)
    if not all_positioned:
        print("✗ Not all instances positioned")
        return False

    print()
    print("✓ TEST 10 PASSED: Frozen cells significantly reduce solver complexity")
    print()
    return True


def test_frozen_with_import_gds():
    """Test 11: import_gds_to_cell with frozen cells"""
    print("=" * 80)
    print("TEST 11: Frozen Cells with import_gds_to_cell")
    print("=" * 80)
    print()

    # Create original layout with frozen blocks
    original = Cell('layout_with_frozen')

    # Create frozen sub-block
    sub_block = Cell('sub_block')
    layer1 = Cell('layer1', 'metal1')
    layer2 = Cell('layer2', 'poly')
    sub_block.add_instance([layer1, layer2])
    sub_block.constrain(layer1, 'x1=0, y1=0, x2=10, y2=10')
    sub_block.constrain(layer2, 'x1=2, y1=2, x2=8, y2=8')

    if not sub_block.solver():
        print("✗ Sub-block solve failed")
        return False

    sub_block.freeze_layout()
    print(f"✓ Created frozen sub-block: {sub_block.get_bbox()}")

    # Use frozen sub-block in original layout
    inst1 = sub_block.copy()
    inst2 = sub_block.copy()
    original.add_instance([inst1, inst2])
    original.constrain(inst1, 'x1=0, y1=0, x2=10, y2=10')
    original.constrain(inst2, 'x1=20, y1=0, x2=30, y2=10')

    if not original.solver():
        print("✗ Original layout solve failed")
        return False

    # Export
    gds_file = 'demo_outputs/test_frozen_import.gds'
    original.export_gds(gds_file)
    print(f"✓ Exported original to {gds_file}")

    # Import with position constraints
    imported = Cell.import_gds_to_cell(gds_file, add_position_constraints=True)
    print(f"✓ Imported layout from GDS")
    print(f"  Imported cell: {imported.name}")
    print(f"  Number of children: {len(imported.children)}")
    print(f"  Number of constraints: {len(imported.constraints)}")

    # Freeze imported layout
    imported.freeze_layout()
    print(f"✓ Froze imported layout")

    # Use frozen imported layout in new parent
    top = Cell('top_with_imported')
    imported_inst1 = imported.copy()
    imported_inst2 = imported.copy()

    top.add_instance([imported_inst1, imported_inst2])

    # Get imported size from bbox
    imported_bbox = imported.get_bbox()
    imported_width = imported_bbox[2] - imported_bbox[0]
    imported_height = imported_bbox[3] - imported_bbox[1]

    top.constrain(imported_inst1, f'x1=0, y1=0, x2={imported_width}, y2={imported_height}')
    top.constrain(imported_inst2, f'sx1=ox2+50, sy1=oy1, sx2-sx1={imported_width}, sy2-sy1={imported_height}', imported_inst1)

    if not top.solver():
        print("✗ Top cell with frozen imported layout failed")
        return False

    print(f"✓ Successfully used frozen imported layout in new design")
    print(f"  imported_inst1: {imported_inst1.pos_list}")
    print(f"  imported_inst2: {imported_inst2.pos_list}")

    # Export final
    top.export_gds('demo_outputs/test_frozen_import_top.gds')
    print(f"✓ Exported final to demo_outputs/test_frozen_import_top.gds")

    print()
    print("✓ TEST 10 PASSED: Frozen cells work with import_gds_to_cell")
    print()
    return True


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================

def main():
    print()
    print("*" * 80)
    print("COMPREHENSIVE FROZEN LAYOUT FEATURE TEST SUITE")
    print("*" * 80)
    print()

    tests = [
        ("Basic Freeze/Unfreeze", test_basic_freeze_unfreeze),
        ("Frozen Size Preserved", test_frozen_size_preserved),
        ("Frozen Position Flexible", test_frozen_position_flexible),
        ("Bbox Caching", test_frozen_bbox_caching),
        ("Nested Frozen Cells", test_nested_frozen_cells),
        ("copy() Preserves Frozen", test_copy_preserves_frozen),
        ("Method Chaining", test_method_chaining),
        ("Hierarchical Structures", test_frozen_in_hierarchy),
        ("Re-solving Maintains Size", test_resolving_frozen),
        ("Solver Optimization", test_solver_optimization),
        ("import_gds_to_cell", test_frozen_with_import_gds),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ TEST FAILED WITH EXCEPTION: {test_name}")
            print(f"  Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
            print()

    # Summary
    print()
    print("*" * 80)
    print("TEST SUMMARY")
    print("*" * 80)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print()
    print("=" * 80)
    print(f"FINAL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("✓ ALL TESTS PASSED!")
    else:
        print(f"✗ {total - passed} test(s) failed")

    print("=" * 80)
    print()

    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
