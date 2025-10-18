
import pytest
import os
from layout_automation.cell import Cell, HAS_ORTOOLS

# Check for optional dependencies
try:
    import gdstk
    HAS_GDS = True
except ImportError:
    HAS_GDS = False

# Helper to get a clean cell
def create_basic_cell(name):
    """Creates a simple leaf cell."""
    return Cell(name, "metal1")

# --- Test Initialization and Structure ---

def test_cell_initialization():
    """Test basic Cell creation."""
    leaf = Cell("leaf_cell", "poly")
    assert leaf.name == "leaf_cell"
    assert leaf.is_leaf
    assert leaf.layer_name == "poly"
    assert len(leaf.children) == 0

    child1 = create_basic_cell("child1")
    child2 = create_basic_cell("child2")
    container = Cell("container", child1, [child2])
    assert not container.is_leaf
    assert len(container.children) == 2
    assert container.child_dict["child1"] == child1
    assert container.child_dict["child2"] == child2

def test_add_instance():
    """Test adding instances to a cell."""
    parent = Cell("parent")
    child1 = create_basic_cell("child1")
    child2 = create_basic_cell("child2")
    
    parent.add_instance(child1)
    assert len(parent.children) == 1
    assert "child1" in parent.child_dict

    parent.add_instance([child2])
    assert len(parent.children) == 2
    assert "child2" in parent.child_dict

    with pytest.raises(TypeError):
        parent.add_instance("not_a_cell")

# --- Test Constraint System ---

def test_self_constraint():
    """Test self-constraining a cell."""
    cell = Cell("test_cell")
    cell.constrain("width=100, height=50")
    assert len(cell.constraints) == 1
    c = cell.constraints[0]
    assert c[0] == cell # self
    assert "x2-x1=100" in c[1]
    assert "y2-y1=50" in c[1]
    assert c[2] is None

def test_absolute_constraint():
    """Test applying an absolute constraint to a child."""
    parent = Cell("parent")
    child = create_basic_cell("child")
    parent.constrain(child, "x1=10, y1=20")
    
    assert child in parent.children # Test auto-add
    assert len(parent.constraints) == 1
    c = parent.constraints[0]
    assert c[0] == child
    assert "x1=10" in c[1]
    assert "y1=20" in c[1]
    assert c[2] is None

def test_relative_constraint():
    """Test relative constraints between two children."""
    parent = Cell("parent")
    child1 = create_basic_cell("child1")
    child2 = create_basic_cell("child2")
    parent.constrain(child1, "sx2 < ox1", child2)

    assert child1 in parent.children
    assert child2 in parent.children
    assert len(parent.constraints) == 1
    c = parent.constraints[0]
    assert c[0] == child1
    assert c[1].replace(" ", "") == "sx2<ox1"
    assert c[2] == child2

# --- Test Copy Mechanism ---

def test_copy_method():
    """Test the deep copy functionality."""
    c1 = create_basic_cell("c1")
    c2 = create_basic_cell("c2")
    original = Cell("original", c1, c2)
    original.constrain(c1, "sx2=ox1", c2)

    # Test automatic naming
    copy1 = original.copy()
    assert copy1.name == "original_c1"
    
    copy2 = original.copy()
    assert copy2.name == "original_c2"

    # Test custom naming
    custom_copy = original.copy("custom_name")
    assert custom_copy.name == "custom_name"

    # Verify it's a deep copy
    assert len(custom_copy.children) == 2
    assert custom_copy.children[0].name == "c1"
    assert custom_copy.children[0] is not original.children[0] # Different objects
    
    # Verify constraints are copied
    assert len(custom_copy.constraints) == 1
    constraint = custom_copy.constraints[0]
    assert constraint[0].name == "c1"
    assert constraint[2].name == "c2"
    
    # Verify modifying original does not affect copy
    original.add_instance(create_basic_cell("new_child"))
    assert len(original.children) == 3
    assert len(custom_copy.children) == 2

# --- Test Solver and Layout ---

@pytest.mark.skipif(not HAS_ORTOOLS, reason="OR-Tools is not installed")
def test_solver_simple_relative():
    """Test the solver with a simple relative constraint."""
    p = Cell("parent")
    b1 = create_basic_cell("b1")
    b2 = create_basic_cell("b2")
    p.add_instance([b1, b2])
    
    # b1 is to the left of b2, with a gap of 10
    p.constrain(b1, "sx2+10=ox1", b2)
    p.constrain(b1, "width=20, height=20")
    p.constrain(b2, "width=30, height=20")
    
    assert p.solver()
    
    b1_x1, _, b1_x2, _ = b1.get_bbox()
    b2_x1, _, b2_x2, _ = b2.get_bbox()
    
    assert b1_x2 + 10 == b2_x1
    assert b1_x2 - b1_x1 == 20
    assert b2_x2 - b2_x1 == 30

@pytest.mark.skipif(not HAS_ORTOOLS, reason="OR-Tools is not installed")
def test_solver_hierarchy_and_bounds():
    """Test that parent bounds correctly enclose children after solving."""
    l1 = Cell("l1", "metal1")
    l2 = Cell("l2", "metal1")
    
    c1 = Cell("c1", l1, l2)
    c1.constrain(l1, "width=10, height=10, x1=0, y1=0")
    c1.constrain(l2, "width=10, height=10, x1=20, y1=20")
    
    top = Cell("top", c1)
    
    assert top.solver()
    
    # Check child bounds
    assert c1.get_bbox() == (0, 0, 30, 30)
    # Check top bounds
    assert top.get_bbox() == (0, 0, 30, 30)

@pytest.mark.skipif(not HAS_ORTOOLS, reason="OR-Tools is not installed")
def test_freeze_layout():
    """Test freezing and unfreezing a layout."""
    block = Cell("block")
    m1 = Cell("m1", "metal1")
    m2 = Cell("m2", "poly")
    block.add_instance([m1, m2])
    block.constrain(m1, "width=10, height=10")
    block.constrain(m2, "width=10, height=10")
    block.constrain(m1, "sx2=ox1", m2) # m1 left of m2
    
    # Solve and freeze
    assert block.solver()
    frozen_bbox = block.get_bbox()
    assert frozen_bbox == (0, 0, 20, 10)
    block.freeze_layout()
    
    assert block.is_frozen()
    
    # Use in a parent cell
    parent = Cell("parent")
    b_copy1 = block.copy("b_copy1")
    b_copy2 = block.copy("b_copy2")
    parent.add_instance([b_copy1, b_copy2])
    parent.constrain(b_copy1, "sx2+5=ox1", b_copy2) # Place copies side-by-side
    
    assert parent.solver()
    
    # Verify frozen blocks were not internally modified
    assert b_copy1.get_bbox()[2] - b_copy1.get_bbox()[0] == frozen_bbox[2] - frozen_bbox[0]
    assert b_copy2.get_bbox()[2] - b_copy2.get_bbox()[0] == frozen_bbox[2] - frozen_bbox[0]
    
    # Verify parent constraint worked
    assert b_copy1.get_bbox()[2] + 5 == b_copy2.get_bbox()[0]
    
    # Test unfreezing
    block.unfreeze_layout()
    assert not block.is_frozen()

# --- Test GDS Import/Export ---

@pytest.mark.skipif(not HAS_GDS, reason="gdstk is not installed")
def test_gds_export_import_roundtrip():
    """Test exporting to GDS and importing back."""
    # Create a simple cell
    p = Cell("parent_gds")
    leaf1 = Cell("leaf1_gds", "metal1")
    leaf2 = Cell("leaf2_gds", "poly")
    p.add_instance([leaf1, leaf2])
    p.constrain(leaf1, "width=10, height=20, x1=0, y1=0")
    p.constrain(leaf2, "width=15, height=5, x1=20, y1=10")
    
    if HAS_ORTOOLS:
        p.solver()
    else:
        # Manually set positions if no solver, to allow GDS export to be tested
        leaf1.pos_list = [0, 0, 10, 20]
        leaf2.pos_list = [20, 10, 35, 15]
        p.pos_list = [0, 0, 35, 20]  # Parent bounding box

    gds_file = "test_roundtrip.gds"
    
    # Export
    p.export_gds(gds_file)
    assert os.path.exists(gds_file)
    
    # Import
    imported_cell = Cell.from_gds(gds_file, cell_name="parent_gds")
    
    assert imported_cell.name == "parent_gds"
    assert len(imported_cell.children) == 2
    
    # Clean up
    os.remove(gds_file)

# --- Test Utility Methods ---

def test_tree_representation():
    """Test the tree() method for displaying hierarchy."""
    c1 = create_basic_cell("c1")
    c2 = create_basic_cell("c2")
    parent = Cell("parent", c1, c2)
    
    tree_str = parent.tree(show_positions=False)
    
    assert "parent" in tree_str
    assert "├── c1" in tree_str
    assert "└── c2" in tree_str
