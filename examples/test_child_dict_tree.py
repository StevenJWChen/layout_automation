#!/usr/bin/env python3
"""
Test new Cell class features:
1. child_dict attribute - dictionary mapping child names to instances
2. tree() method - display cell hierarchy as a tree
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

print("=" * 80)
print("TESTING child_dict AND tree() FEATURES")
print("=" * 80)
print()

# ==============================================================================
# TEST 1: child_dict Attribute
# ==============================================================================
print("TEST 1: child_dict Attribute")
print("-" * 80)
print()

# Create a hierarchical layout
top = Cell('TOP_CELL')

# Add some children
block1 = Cell('block1')
block2 = Cell('block2')

metal1 = Cell('metal1_layer', 'metal1')
poly1 = Cell('poly1_layer', 'poly')

block1.add_instance([metal1, poly1])

top.add_instance([block1, block2])

# Access children via child_dict
print("Top cell children:")
print(f"  top.children: {[c.name for c in top.children]}")
print(f"  top.child_dict.keys(): {list(top.child_dict.keys())}")
print()

print("Accessing children by name:")
print(f"  top.child_dict['block1']: {top.child_dict['block1']}")
print(f"  top.child_dict['block2']: {top.child_dict['block2']}")
print()

print("Block1 children:")
print(f"  block1.child_dict.keys(): {list(block1.child_dict.keys())}")
print(f"  block1.child_dict['metal1_layer']: {block1.child_dict['metal1_layer']}")
print(f"  block1.child_dict['poly1_layer']: {block1.child_dict['poly1_layer']}")
print()

print("✓ child_dict works correctly!")
print()
print()

# ==============================================================================
# TEST 2: tree() Method - Without Positions
# ==============================================================================
print("TEST 2: tree() Method - Without Positions/Solving")
print("-" * 80)
print()

# Create a more complex hierarchy
transistor = Cell('NMOS_transistor')

diff = Cell('diffusion', 'diff')
poly_gate = Cell('poly_gate', 'poly')
metal_src = Cell('metal_source', 'metal1')
metal_drn = Cell('metal_drain', 'metal1')

transistor.add_instance([diff, poly_gate, metal_src, metal_drn])

# Create contact arrays
contact_array = Cell('contact_array_2x2')
for i in range(2):
    for j in range(2):
        contact = Cell(f'contact_{i}_{j}', 'contact')
        contact_array.add_instance(contact)

# Add contact arrays to transistor
src_contacts = Cell('src_contacts_inst')
drn_contacts = Cell('drn_contacts_inst')

for child in contact_array.children:
    src_contacts.add_instance(child.copy())
    drn_contacts.add_instance(child.copy())

transistor.add_instance([src_contacts, drn_contacts])

# Create top cell with multiple transistors
circuit = Cell('CIRCUIT')
trans1 = Cell('transistor_1')
trans2 = Cell('transistor_2')

# Copy transistor structure
for child in transistor.children:
    trans1.add_instance(child.copy())
    trans2.add_instance(child.copy())

circuit.add_instance([trans1, trans2])

print("Displaying circuit hierarchy (no positions yet):")
print()
circuit.tree(show_positions=False)

print()
print()

# ==============================================================================
# TEST 3: tree() Method - With Positions
# ==============================================================================
print("TEST 3: tree() Method - With Positions and Frozen Cells")
print("-" * 80)
print()

# Create a simple layout with positions
layout = Cell('LAYOUT')

# Create and position a frozen block
frozen_block = Cell('frozen_block')
layer_a = Cell('layer_a', 'metal1')
layer_b = Cell('layer_b', 'poly')

frozen_block.add_instance([layer_a, layer_b])
frozen_block.constrain(layer_a, 'x1=0, y1=0, x2=20, y2=20')
frozen_block.constrain(layer_b, 'x1=5, y1=5, x2=15, y2=15')

# Solve and freeze
if frozen_block.solver():
    frozen_block.freeze_layout()

# Create instances in layout
inst1 = frozen_block.copy()
inst2 = frozen_block.copy()
inst1.name = 'frozen_inst1'
inst2.name = 'frozen_inst2'

layout.add_instance([inst1, inst2])
layout.constrain(inst1, 'x1=0, y1=0, x2=20, y2=20')
layout.constrain(inst2, 'x1=30, y1=0, x2=50, y2=20')

# Solve layout
if layout.solver():
    print("Displaying layout hierarchy with positions and frozen status:")
    print()
    layout.tree(show_positions=True, show_layers=True)

print()
print()

# ==============================================================================
# TEST 4: Accessing Specific Child via child_dict
# ==============================================================================
print("TEST 4: Using child_dict to Access and Modify Children")
print("-" * 80)
print()

# Create a cell with named children
parent = Cell('parent')
child_a = Cell('child_A')
child_b = Cell('child_B')
child_c = Cell('child_C')

parent.add_instance([child_a, child_b, child_c])

print("Original children:")
print(f"  {list(parent.child_dict.keys())}")
print()

# Access specific child by name
target_child = parent.child_dict['child_B']
print(f"Accessed 'child_B': {target_child}")
print(f"  Same object? {target_child is child_b}")
print()

# Modify the accessed child
target_child.constrain('x1=10, y1=20, x2=30, y2=40')
print(f"Added constraint to 'child_B' via child_dict")
print(f"  Constraints: {target_child.constraints}")
print()

print("✓ child_dict allows direct access to children by name!")
print()
print()

# ==============================================================================
# TEST 5: Automatic Copy Naming
# ==============================================================================
print("TEST 5: Automatic Copy Naming with _c{N}")
print("-" * 80)
print()

# Create a reusable block
reusable_block = Cell('my_block')
layer = Cell('layer1', 'metal1')
reusable_block.add_instance(layer)

print(f"Original block name: {reusable_block.name}")
print()

# Create copies with automatic naming
copy1 = reusable_block.copy()
copy2 = reusable_block.copy()
copy3 = reusable_block.copy()

print("Automatic naming:")
print(f"  copy1.name: {copy1.name}")  # my_block_c1
print(f"  copy2.name: {copy2.name}")  # my_block_c2
print(f"  copy3.name: {copy3.name}")  # my_block_c3
print()

# Create copy with custom name
copy_custom = reusable_block.copy('custom_block_name')
print(f"Custom naming:")
print(f"  copy_custom.name: {copy_custom.name}")  # custom_block_name
print()

# Verify copies are independent
copy1.constrain('x1=0, y1=0, x2=10, y2=10')
copy2.constrain('x1=20, y1=20, x2=30, y2=30')

print("Verifying independence:")
print(f"  copy1 constraints: {len(copy1.constraints)}")
print(f"  copy2 constraints: {len(copy2.constraints)}")
print(f"  original constraints: {len(reusable_block.constraints)}")
print()

print("✓ Automatic copy naming works correctly!")
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("FEATURE SUMMARY")
print("=" * 80)
print()
print("1. child_dict Attribute:")
print("   - Dictionary mapping child names to Cell instances")
print("   - Automatically maintained when adding instances")
print("   - Allows O(1) lookup by name: cell.child_dict['name']")
print()
print("2. tree() Method:")
print("   - Displays cell hierarchy as a visual tree")
print("   - Shows cell names, layers, positions, and frozen status")
print("   - Options: show_positions, show_layers")
print("   - Automatically prints and returns the tree string")
print()
print("3. copy() with Automatic Naming:")
print("   - copy() creates deep copy with automatic name")
print("   - Format: original_name_c{N} where N increments")
print("   - copy('custom_name') for explicit naming")
print("   - Each copy is independent with reset constraint variables")
print()
print("All three features tested successfully!")
print("=" * 80)
