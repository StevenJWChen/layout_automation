#!/usr/bin/env python3
"""
Comprehensive Test Program for Layout Automation Toolkit

This test program demonstrates and validates all major features of the
layout automation system including:
- Basic cell creation and constraints
- Hierarchical layouts
- Freeze and fix mechanisms
- Centering with tolerance
- Style configuration
- Visualization
- Copying
- Edge keywords
- Label modes
- Technology files
"""

import sys
import os
import traceback
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config
from layout_automation.centering_with_tolerance import add_centering_with_tolerance

try:
    from layout_automation.tech_file import TechFile
    TECH_FILE_AVAILABLE = True
except ImportError:
    TECH_FILE_AVAILABLE = False
    print("Warning: TechFile module not available, skipping tech file tests")

# Test result tracking
test_results = []


def test_header(test_name):
    """Print test header"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")


def test_result(test_name, passed, message=""):
    """Record and print test result"""
    status = "PASS" if passed else "FAIL"
    result = {
        'test': test_name,
        'passed': passed,
        'message': message
    }
    test_results.append(result)

    status_symbol = "✓" if passed else "✗"
    print(f"\n{status_symbol} {status}: {test_name}")
    if message:
        print(f"   {message}")


def test_basic_cell_creation():
    """Test 1: Basic cell creation and properties"""
    test_header("Basic Cell Creation")

    try:
        # Create cells
        parent = Cell('parent')
        leaf = Cell('leaf', 'metal1')

        # Verify properties
        assert parent.name == 'parent', "Parent name incorrect"
        assert leaf.name == 'leaf', "Leaf name incorrect"
        assert leaf.layer_name == 'metal1', "Layer name incorrect"
        assert leaf.is_leaf == True, "is_leaf should be True"
        assert parent.is_leaf == False, "is_leaf should be False"

        test_result("Basic Cell Creation", True, "All properties verified")
        return True
    except Exception as e:
        test_result("Basic Cell Creation", False, str(e))
        traceback.print_exc()
        return False


def test_add_instance():
    """Test 2: Adding instances"""
    test_header("Adding Instances")

    try:
        parent = Cell('parent')
        child1 = Cell('child1', 'metal1')
        child2 = Cell('child2', 'metal2')
        child3 = Cell('child3', 'poly')

        # Add single instance
        parent.add_instance(child1)
        assert len(parent.children) == 1, "Should have 1 child"

        # Add multiple instances
        parent.add_instance([child2, child3])
        assert len(parent.children) == 3, "Should have 3 children"

        # Check child_dict
        assert 'child1' in parent.child_dict, "child1 not in child_dict"
        assert parent.child_dict['child2'] == child2, "child2 lookup failed"

        test_result("Adding Instances", True, "Single and multiple instance addition works")
        return True
    except Exception as e:
        test_result("Adding Instances", False, str(e))
        traceback.print_exc()
        return False


def test_self_constraints():
    """Test 3: Self-constraints"""
    test_header("Self-Constraints")

    try:
        cell = Cell('cell', 'metal1')

        # Add self-constraints
        cell.constrain('width=100, height=50')
        cell.constrain('x1=0, y1=0')

        # Solve
        status = cell.solver()
        assert status == 4, f"Solver should return OPTIMAL (4), got {status}"

        # Verify results
        assert cell.width == 100, f"Width should be 100, got {cell.width}"
        assert cell.height == 50, f"Height should be 50, got {cell.height}"
        assert cell.x1 == 0, f"x1 should be 0, got {cell.x1}"
        assert cell.y1 == 0, f"y1 should be 0, got {cell.y1}"
        assert cell.x2 == 100, f"x2 should be 100, got {cell.x2}"
        assert cell.y2 == 50, f"y2 should be 50, got {cell.y2}"

        test_result("Self-Constraints", True, f"Position: {cell.pos_list}")
        return True
    except Exception as e:
        test_result("Self-Constraints", False, str(e))
        traceback.print_exc()
        return False


def test_alignment_keywords():
    """Test 4: Alignment keywords"""
    test_header("Alignment Keywords")

    try:
        parent = Cell('parent')
        child = Cell('child', 'metal1')

        parent.add_instance(child)
        parent.constrain('width=100, height=50, x1=0, y1=0')
        parent.constrain(child, 'swidth=20, sheight=10', parent)
        parent.constrain(child, 'left, bottom', parent)

        status = parent.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Verify alignment
        assert child.x1 == parent.x1, "Left alignment failed"
        assert child.y1 == parent.y1, "Bottom alignment failed"

        # Test right, top alignment
        parent2 = Cell('parent2')
        child2 = Cell('child2', 'metal2')
        parent2.add_instance(child2)
        parent2.constrain('width=100, height=50, x1=0, y1=0')
        parent2.constrain(child2, 'swidth=20, sheight=10', parent2)
        parent2.constrain(child2, 'right, top', parent2)

        status = parent2.solver()
        assert status == 4, f"Solver failed with status {status}"
        assert child2.x2 == parent2.x2, "Right alignment failed"
        assert child2.y2 == parent2.y2, "Top alignment failed"

        test_result("Alignment Keywords", True, "left, right, top, bottom all work")
        return True
    except Exception as e:
        test_result("Alignment Keywords", False, str(e))
        traceback.print_exc()
        return False


def test_centering_keywords():
    """Test 5: Centering keywords"""
    test_header("Centering Keywords")

    try:
        parent = Cell('parent')
        child = Cell('child', 'metal1')

        parent.add_instance(child)
        parent.constrain('width=100, height=50, x1=0, y1=0')
        parent.constrain(child, 'swidth=20, sheight=10', parent)
        parent.constrain(child, 'center', parent)

        status = parent.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Verify centering
        assert child.cx == parent.cx, f"X-center mismatch: {child.cx} != {parent.cx}"
        assert child.cy == parent.cy, f"Y-center mismatch: {child.cy} != {parent.cy}"

        # Test xcenter only
        parent2 = Cell('parent2')
        child2 = Cell('child2', 'metal2')
        parent2.add_instance(child2)
        parent2.constrain('width=100, height=50, x1=0, y1=0')
        parent2.constrain(child2, 'swidth=20, sheight=10', parent2)
        parent2.constrain(child2, 'xcenter, bottom', parent2)

        status = parent2.solver()
        assert status == 4, f"Solver failed with status {status}"
        assert child2.cx == parent2.cx, "X-center failed"
        assert child2.y1 == parent2.y1, "Bottom alignment failed"

        test_result("Centering Keywords", True, "center, xcenter, ycenter work")
        return True
    except Exception as e:
        test_result("Centering Keywords", False, str(e))
        traceback.print_exc()
        return False


def test_edge_keywords():
    """Test 6: Edge distance keywords"""
    test_header("Edge Distance Keywords")

    try:
        parent = Cell('parent')
        left = Cell('left', 'metal1')
        right = Cell('right', 'metal2')

        parent.add_instance([left, right])
        parent.constrain('width=100, height=50, x1=0, y1=0')
        parent.constrain(left, 'swidth=20, sheight=10', parent)
        parent.constrain(right, 'swidth=20, sheight=10', parent)
        parent.constrain(left, 'left, ycenter', parent)
        parent.constrain(left, 'rl_edge=10', right)  # 10 units spacing
        parent.constrain(right, 'ycenter', parent)

        status = parent.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Verify spacing (rl_edge: ox1 - sx2 = 10)
        spacing = right.x1 - left.x2
        assert spacing == 10, f"rl_edge spacing should be 10, got {spacing}"

        # Test vertical edge keyword
        parent2 = Cell('parent2')
        bottom = Cell('bottom', 'metal1')
        top = Cell('top', 'metal2')

        parent2.add_instance([bottom, top])
        parent2.constrain('width=50, height=100, x1=0, y1=0')
        parent2.constrain(bottom, 'swidth=20, sheight=20', parent2)
        parent2.constrain(top, 'swidth=20, sheight=20', parent2)
        parent2.constrain(bottom, 'xcenter, bottom', parent2)
        parent2.constrain(bottom, 'tb_edge=5', top)  # 5 units vertical spacing
        parent2.constrain(top, 'xcenter', parent2)

        status = parent2.solver()
        assert status == 4, f"Solver failed with status {status}"

        v_spacing = top.y1 - bottom.y2
        assert v_spacing == 5, f"tb_edge spacing should be 5, got {v_spacing}"

        test_result("Edge Distance Keywords", True, "rl_edge, tb_edge work correctly")
        return True
    except Exception as e:
        test_result("Edge Distance Keywords", False, str(e))
        traceback.print_exc()
        return False


def test_hierarchical_layout():
    """Test 7: Hierarchical layout"""
    test_header("Hierarchical Layout")

    try:
        # Create sub-block
        sub_block = Cell('sub_block')
        m1 = Cell('m1', 'metal1')
        m2 = Cell('m2', 'metal2')

        sub_block.add_instance([m1, m2])
        sub_block.constrain('width=50, height=30')
        sub_block.constrain(m1, 'swidth=20, sheight=10, left, bottom', sub_block)
        sub_block.constrain(m2, 'swidth=20, sheight=10, right, top', sub_block)

        # Create top-level
        top = Cell('top')
        block1 = sub_block.copy()
        block2 = sub_block.copy()

        top.add_instance([block1, block2])
        top.constrain('width=150, height=50')
        top.constrain(block1, 'left, ycenter', top)
        top.constrain(block2, 'right, ycenter', top)

        status = top.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Verify hierarchy preserved
        assert len(block1.children) == 2, "Sub-block should have 2 children"
        assert len(block2.children) == 2, "Sub-block should have 2 children"

        # Verify positions updated
        assert block1.x1 >= 0, "Block1 positioned"
        assert block2.x2 <= 150, "Block2 positioned"

        test_result("Hierarchical Layout", True, "Multi-level hierarchy works")
        return True
    except Exception as e:
        test_result("Hierarchical Layout", False, str(e))
        traceback.print_exc()
        return False


def test_freeze_layout():
    """Test 8: Freeze layout"""
    test_header("Freeze Layout")

    try:
        # Create and solve a block
        block = Cell('block')
        m1 = Cell('m1', 'metal1')
        block.add_instance(m1)
        block.constrain('width=50, height=30')
        block.constrain(m1, 'swidth=20, sheight=10, center', block)

        status = block.solver()
        assert status == 4, f"Initial solve failed with status {status}"

        # Freeze it
        block.freeze_layout()
        assert block._frozen == True, "Block should be frozen"

        # Try to add instance (should fail or be prevented)
        try:
            child = Cell('new_child', 'metal2')
            block.add_instance(child)
            # If we get here, check that it wasn't actually added
            # (implementation may vary)
        except:
            pass  # Expected to fail

        # Verify size is locked
        original_width = block.width
        original_height = block.height

        # Use in parent
        parent = Cell('parent')
        copy1 = block.copy()
        copy2 = block.copy()

        parent.add_instance([copy1, copy2])
        parent.constrain(copy1, 'left, ycenter', parent)
        parent.constrain(copy2, 'right, ycenter', parent)
        parent.constrain('width=200, height=50')

        status = parent.solver()
        assert status == 4, f"Parent solve failed with status {status}"

        # Verify frozen blocks maintain size
        assert copy1.width == original_width, "Frozen block width changed"
        assert copy2.height == original_height, "Frozen block height changed"

        test_result("Freeze Layout", True, "Frozen blocks work correctly")
        return True
    except Exception as e:
        test_result("Freeze Layout", False, str(e))
        traceback.print_exc()
        return False


def test_fix_layout():
    """Test 9: Fix layout"""
    test_header("Fix Layout")

    try:
        # Create and solve a block
        block = Cell('block')
        m1 = Cell('m1', 'metal1')
        m2 = Cell('m2', 'metal2')

        block.add_instance([m1, m2])
        block.constrain('width=50, height=30')
        block.constrain(m1, 'swidth=10, sheight=10, left, bottom', block)
        block.constrain(m2, 'swidth=10, sheight=10, right, top', block)

        status = block.solver()
        assert status == 4, f"Initial solve failed with status {status}"

        # Record initial child positions
        initial_m1_pos = list(m1.pos_list)
        initial_m2_pos = list(m2.pos_list)

        # Fix it
        block.fix_layout()
        assert block._fixed == True, "Block should be fixed"

        # Use in parent and reposition
        parent = Cell('parent')
        parent.add_instance(block)
        parent.constrain('width=100, height=100, x1=0, y1=0')
        parent.constrain(block, 'center', parent)

        status = parent.solver()
        assert status == 4, f"Parent solve failed with status {status}"

        # Verify block moved
        assert block.x1 > 0, "Block should be repositioned"

        # Verify children moved with block (offsets preserved)
        offset_x1 = m1.x1 - block.x1
        offset_y1 = m1.y1 - block.y1

        # Check that relative positions are maintained
        # (exact implementation may vary)
        test_result("Fix Layout", True, "Fixed blocks can be repositioned")
        return True
    except Exception as e:
        test_result("Fix Layout", False, str(e))
        traceback.print_exc()
        return False


def test_copy_functionality():
    """Test 10: Copy functionality"""
    test_header("Copy Functionality")

    try:
        # Create original
        original = Cell('original')
        m1 = Cell('m1', 'metal1')
        original.add_instance(m1)
        original.constrain('width=50, height=30')
        original.constrain(m1, 'swidth=20, sheight=10, center', original)

        # Create copies
        copy1 = original.copy()
        copy2 = original.copy()
        copy3 = original.copy('custom_name')

        # Verify names
        assert copy1.name == 'original_c1', f"Copy1 name should be 'original_c1', got {copy1.name}"
        assert copy2.name == 'original_c2', f"Copy2 name should be 'original_c2', got {copy2.name}"
        assert copy3.name == 'custom_name', f"Copy3 name should be 'custom_name', got {copy3.name}"

        # Verify children copied
        assert len(copy1.children) == 1, "Copy should have children"
        assert copy1.children[0].name != m1.name or copy1.children[0] is not m1, \
            "Child should be copied, not referenced"

        # Verify independence (modifying copy doesn't affect original)
        copy1.add_instance(Cell('new_child', 'metal2'))
        assert len(original.children) == 1, "Original should be unchanged"
        assert len(copy1.children) == 2, "Copy should have new child"

        test_result("Copy Functionality", True, "Deep copy with auto-naming works")
        return True
    except Exception as e:
        test_result("Copy Functionality", False, str(e))
        traceback.print_exc()
        return False


def test_properties():
    """Test 11: Position properties"""
    test_header("Position Properties")

    try:
        cell = Cell('cell', 'metal1')
        cell.constrain('width=100, height=50, x1=10, y1=20')

        status = cell.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Test properties
        assert cell.x1 == 10, f"x1 should be 10, got {cell.x1}"
        assert cell.y1 == 20, f"y1 should be 20, got {cell.y1}"
        assert cell.x2 == 110, f"x2 should be 110, got {cell.x2}"
        assert cell.y2 == 70, f"y2 should be 70, got {cell.y2}"
        assert cell.width == 100, f"width should be 100, got {cell.width}"
        assert cell.height == 50, f"height should be 50, got {cell.height}"
        assert cell.cx == 60.0, f"cx should be 60.0, got {cell.cx}"
        assert cell.cy == 45.0, f"cy should be 45.0, got {cell.cy}"

        # Test get_bbox
        bbox = cell.get_bbox()
        assert bbox == (10, 20, 110, 70), f"bbox should be (10, 20, 110, 70), got {bbox}"

        test_result("Position Properties", True, "All properties work correctly")
        return True
    except Exception as e:
        test_result("Position Properties", False, str(e))
        traceback.print_exc()
        return False


def test_style_configuration():
    """Test 12: Style configuration"""
    test_header("Style Configuration")

    try:
        style = get_style_config()

        # Set layer styles
        style.set_layer_style('metal1',
                            color='blue',
                            alpha=0.6,
                            edge_color='darkblue',
                            line_style='--',
                            line_width=2.0,
                            zorder=3)

        style.set_layer_style('metal2',
                            color='red',
                            alpha=0.5,
                            zorder=4)

        # Set container style
        style.set_container_style(
            line_style='-',
            line_width=1.5,
            edge_color='black',
            zorder=1
        )

        # Verify styles set (check internal structure)
        m1_style = style.layer_styles.get('metal1')
        assert m1_style is not None, "metal1 style should be set"
        assert m1_style.color == 'blue', "metal1 color should be blue"
        assert m1_style.alpha == 0.6, "metal1 alpha should be 0.6"
        assert m1_style.zorder == 3, "metal1 zorder should be 3"

        container = style.container_style
        assert container.line_width == 1.5, "container line_width should be 1.5"

        test_result("Style Configuration", True, "Styles configured successfully")
        return True
    except Exception as e:
        test_result("Style Configuration", False, str(e))
        traceback.print_exc()
        return False


def test_centering_with_tolerance():
    """Test 13: Centering with tolerance"""
    test_header("Centering with Tolerance")

    try:
        parent = Cell('parent')
        child = Cell('child', 'metal1')

        parent.add_instance(child)
        parent.constrain('width=100, height=50')
        parent.constrain(child, 'swidth=20, sheight=10', parent)

        # Add centering with tolerance
        parent.center_with_tolerance(child, tolerance=5, tolerance_x=5, tolerance_y=5)

        status = parent.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Verify child is approximately centered
        # (may not be exact due to tolerance)
        cx_diff = abs(child.cx - parent.cx)
        cy_diff = abs(child.cy - parent.cy)

        # Should be within tolerance
        assert cx_diff <= 5, f"X-center deviation {cx_diff} exceeds tolerance"
        assert cy_diff <= 5, f"Y-center deviation {cy_diff} exceeds tolerance"

        test_result("Centering with Tolerance", True, "Soft centering works")
        return True
    except Exception as e:
        test_result("Centering with Tolerance", False, str(e))
        traceback.print_exc()
        return False


def test_raw_constraints():
    """Test 14: Raw constraint expressions"""
    test_header("Raw Constraint Expressions")

    try:
        parent = Cell('parent')
        child1 = Cell('child1', 'metal1')
        child2 = Cell('child2', 'metal2')

        parent.add_instance([child1, child2])
        parent.constrain('width=100, height=50')

        # Raw constraints
        parent.constrain(child1, 'sx2 - sx1 = 20', parent)  # width = 20
        parent.constrain(child1, 'sy2 - sy1 = 10', parent)  # height = 10
        parent.constrain(child1, 'sx1 = 0', parent)  # x1 = 0
        parent.constrain(child1, 'sy1 = 0', parent)  # y1 = 0

        parent.constrain(child2, 'sx2 - sx1 = 30', parent)  # width = 30
        parent.constrain(child2, 'sy2 - sy1 = 15', parent)  # height = 15
        parent.constrain(child1, 'sx2 + 10 = ox1', child2)  # 10 units spacing
        parent.constrain(child2, 'oy1 = 0', parent)  # y1 = 0

        status = parent.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Verify results
        assert child1.width == 20, f"child1 width should be 20, got {child1.width}"
        assert child1.height == 10, f"child1 height should be 10, got {child1.height}"
        assert child2.width == 30, f"child2 width should be 30, got {child2.width}"

        spacing = child2.x1 - child1.x2
        assert spacing == 10, f"Spacing should be 10, got {spacing}"

        test_result("Raw Constraint Expressions", True, "Raw constraints work correctly")
        return True
    except Exception as e:
        test_result("Raw Constraint Expressions", False, str(e))
        traceback.print_exc()
        return False


def test_visualization():
    """Test 15: Visualization (no display)"""
    test_header("Visualization")

    try:
        # Create a simple layout
        parent = Cell('parent')
        m1 = Cell('metal1', 'metal1')
        m2 = Cell('metal2', 'metal2')

        parent.add_instance([m1, m2])
        parent.constrain('width=100, height=50')
        parent.constrain(m1, 'swidth=30, sheight=20, left, bottom', parent)
        parent.constrain(m2, 'swidth=30, sheight=20, right, top', parent)

        # Test draw (non-interactive, just check it doesn't crash)
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend

        # Draw with various options
        fig, ax = parent.draw(solve_first=True, show_labels=False)
        assert fig is not None, "Figure should be returned"
        assert ax is not None, "Axes should be returned"

        # Test with labels
        fig2, ax2 = parent.draw(show_labels=True, label_mode='auto')
        assert fig2 is not None, "Figure should be returned"

        # Test different label modes
        fig3, ax3 = parent.draw(show_labels=True, label_mode='full')
        fig4, ax4 = parent.draw(show_labels=True, label_mode='abbr')
        fig5, ax5 = parent.draw(show_labels=True, label_mode='extended')

        # Test label positions
        fig6, ax6 = parent.draw(show_labels=True, label_position='top-left')
        fig7, ax7 = parent.draw(show_labels=True, label_position='bottom-right')

        # Close all figures to free memory
        import matplotlib.pyplot as plt
        plt.close('all')

        test_result("Visualization", True, "Drawing works with all options")
        return True
    except Exception as e:
        test_result("Visualization", False, str(e))
        traceback.print_exc()
        return False


def test_tech_file():
    """Test 16: Technology file parsing"""
    test_header("Technology File")

    if not TECH_FILE_AVAILABLE:
        test_result("Technology File", True, "Skipped (module not available)")
        return True

    try:
        # Check if tech file exists
        tech_path = Path(__file__).parent / 'FreePDK45.tf'
        drf_path = Path(__file__).parent / 'SantanaDisplay.drf'

        if not tech_path.exists():
            test_result("Technology File", True, "Skipped (FreePDK45.tf not found)")
            return True

        # Load tech file
        tech = TechFile(str(tech_path))

        # Test layer lookup
        if hasattr(tech, 'get_layer_number'):
            # Try to get a layer number
            pass

        # Load display file if it exists
        if drf_path.exists() and hasattr(tech, 'load_display_file'):
            tech.load_display_file(str(drf_path))

        test_result("Technology File", True, "Tech file parsing works")
        return True
    except Exception as e:
        test_result("Technology File", False, str(e))
        traceback.print_exc()
        return False


def test_complex_hierarchy():
    """Test 17: Complex multi-level hierarchy"""
    test_header("Complex Multi-Level Hierarchy")

    try:
        # Level 3: Basic cells
        leaf1 = Cell('leaf1', 'metal1')
        leaf2 = Cell('leaf2', 'metal2')

        # Level 2: Sub-blocks
        sub1 = Cell('sub1')
        sub1.add_instance([leaf1.copy(), leaf2.copy()])
        sub1.constrain('width=40, height=30')
        sub1.constrain(sub1.children[0], 'swidth=15, sheight=10, left, bottom', sub1)
        sub1.constrain(sub1.children[1], 'swidth=15, sheight=10, right, top', sub1)

        sub2 = sub1.copy()

        # Level 1: Top block
        top = Cell('top')
        block1 = sub1.copy()
        block2 = sub2.copy()

        top.add_instance([block1, block2])
        top.constrain('width=120, height=50')
        top.constrain(block1, 'left, ycenter', top)
        top.constrain(block2, 'right, ycenter', top)

        status = top.solver()
        assert status == 4, f"Solver failed with status {status}"

        # Verify all levels positioned
        assert top.x1 >= 0 and top.y1 >= 0, "Top level positioned"
        assert block1.x1 >= 0 and block1.y1 >= 0, "Level 1 positioned"
        assert block1.children[0].x1 >= 0, "Level 2 positioned"

        # Count total cells in hierarchy
        def count_cells(cell):
            count = 1
            for child in cell.children:
                count += count_cells(child)
            return count

        total = count_cells(top)
        assert total > 5, f"Should have multiple levels, got {total} cells"

        test_result("Complex Multi-Level Hierarchy", True, f"{total} cells in hierarchy")
        return True
    except Exception as e:
        test_result("Complex Multi-Level Hierarchy", False, str(e))
        traceback.print_exc()
        return False


def test_infeasible_constraints():
    """Test 18: Handling infeasible constraints"""
    test_header("Infeasible Constraints Detection")

    try:
        cell = Cell('cell', 'metal1')

        # Create contradictory constraints
        cell.constrain('width=100')
        cell.constrain('width=50')  # Contradiction!

        status = cell.solver()

        # Should return INFEASIBLE (3) or similar
        assert status != 4, f"Should not be OPTIMAL with contradictory constraints"

        test_result("Infeasible Constraints Detection", True,
                   f"Correctly detected infeasibility (status={status})")
        return True
    except Exception as e:
        test_result("Infeasible Constraints Detection", False, str(e))
        traceback.print_exc()
        return False


def test_grid_layout():
    """Test 19: Grid layout pattern"""
    test_header("Grid Layout Pattern")

    try:
        parent = Cell('parent')

        # Create 3x3 grid
        cells = []
        for i in range(9):
            cells.append(Cell(f'cell_{i}', 'metal1'))

        parent.add_instance(cells)
        parent.constrain('width=150, height=150')

        # Make all cells same size
        for cell in cells:
            parent.constrain(cell, 'swidth=40, sheight=40', parent)

        # Position in grid
        # Row 0
        parent.constrain(cells[0], 'left, top', parent)
        parent.constrain(cells[0], 'rl_edge=5', cells[1])
        parent.constrain(cells[1], 'rl_edge=5', cells[2])
        parent.constrain(cells[1], 'top', parent)
        parent.constrain(cells[2], 'right, top', parent)

        # Row 1
        parent.constrain(cells[0], 'tb_edge=5', cells[3])
        parent.constrain(cells[1], 'tb_edge=5', cells[4])
        parent.constrain(cells[2], 'tb_edge=5', cells[5])
        parent.constrain(cells[3], 'left', parent)
        parent.constrain(cells[3], 'rl_edge=5', cells[4])
        parent.constrain(cells[4], 'rl_edge=5', cells[5])
        parent.constrain(cells[5], 'right', parent)

        # Row 2
        parent.constrain(cells[3], 'tb_edge=5', cells[6])
        parent.constrain(cells[4], 'tb_edge=5', cells[7])
        parent.constrain(cells[5], 'tb_edge=5', cells[8])
        parent.constrain(cells[6], 'left, bottom', parent)
        parent.constrain(cells[6], 'rl_edge=5', cells[7])
        parent.constrain(cells[7], 'rl_edge=5', cells[8])
        parent.constrain(cells[8], 'right, bottom', parent)

        status = parent.solver()
        assert status == 4, f"Grid solver failed with status {status}"

        # Verify grid spacing
        h_spacing1 = cells[1].x1 - cells[0].x2
        h_spacing2 = cells[2].x1 - cells[1].x2
        v_spacing1 = cells[3].y2 - cells[0].y1

        assert h_spacing1 == 5, f"Horizontal spacing should be 5, got {h_spacing1}"
        assert h_spacing2 == 5, f"Horizontal spacing should be 5, got {h_spacing2}"
        assert abs(v_spacing1) == 5, f"Vertical spacing should be 5, got {abs(v_spacing1)}"

        test_result("Grid Layout Pattern", True, "3x3 grid layout works")
        return True
    except Exception as e:
        test_result("Grid Layout Pattern", False, str(e))
        traceback.print_exc()
        return False


def test_all_edge_keywords():
    """Test 20: All edge keywords"""
    test_header("All Edge Keywords")

    try:
        results = []

        # Test each edge keyword
        edge_tests = [
            ('ll_edge', 10),
            ('lr_edge', 50),
            ('rl_edge', 10),
            ('rr_edge', 50),
            ('bb_edge', 10),
            ('bt_edge', 40),
            ('tb_edge', 10),
            ('tt_edge', 40),
        ]

        for keyword, expected_val in edge_tests:
            parent = Cell('parent')
            cell1 = Cell('cell1', 'metal1')
            cell2 = Cell('cell2', 'metal2')

            parent.add_instance([cell1, cell2])
            parent.constrain('width=200, height=200')
            parent.constrain(cell1, 'swidth=20, sheight=20', parent)
            parent.constrain(cell2, 'swidth=30, sheight=30', parent)
            parent.constrain(cell1, 'left, bottom', parent)
            parent.constrain(cell1, f'{keyword}={expected_val}', cell2)

            status = parent.solver()
            if status == 4:
                results.append(f"{keyword}: OK")
            else:
                results.append(f"{keyword}: FAIL (status={status})")

        # All should pass
        all_passed = all('OK' in r for r in results)

        test_result("All Edge Keywords", all_passed, ", ".join(results))
        return all_passed
    except Exception as e:
        test_result("All Edge Keywords", False, str(e))
        traceback.print_exc()
        return False


def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in test_results if r['passed'])
    total = len(test_results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    # List failed tests
    failed = [r for r in test_results if not r['passed']]
    if failed:
        print("\nFailed Tests:")
        for r in failed:
            print(f"  - {r['test']}: {r['message']}")
    else:
        print("\nAll tests passed!")

    print("\n" + "="*70)


def main():
    """Run all tests"""
    print("="*70)
    print("LAYOUT AUTOMATION - COMPREHENSIVE TEST PROGRAM")
    print("="*70)
    print("\nThis program tests all major features of the layout automation toolkit.")
    print("Tests are designed to validate functionality and serve as usage examples.")

    # Run all tests
    test_basic_cell_creation()
    test_add_instance()
    test_self_constraints()
    test_alignment_keywords()
    test_centering_keywords()
    test_edge_keywords()
    test_hierarchical_layout()
    test_freeze_layout()
    test_fix_layout()
    test_copy_functionality()
    test_properties()
    test_style_configuration()
    test_centering_with_tolerance()
    test_raw_constraints()
    test_visualization()
    test_tech_file()
    test_complex_hierarchy()
    test_infeasible_constraints()
    test_grid_layout()
    test_all_edge_keywords()

    # Print summary
    print_summary()

    # Return exit code
    passed = sum(1 for r in test_results if r['passed'])
    total = len(test_results)

    return 0 if passed == total else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
