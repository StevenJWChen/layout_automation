#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple demonstration of hierarchical/relative positioning

This shows the basic concept: positions can be stored relative to parents,
just like in GDS format.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_automation.cell import Cell


def demo_current_vs_hierarchical():
    """Compare current absolute positioning with hierarchical relative positioning"""
    print("=" * 80)
    print("Hierarchical Positioning Demonstration")
    print("=" * 80)

    print("\n" + "="*80)
    print("CURRENT SYSTEM: Absolute Positioning")
    print("=" * 80)

    # Create hierarchy
    metal1 = Cell('metal1_rect', 'metal1')
    metal2 = Cell('metal2_rect', 'metal2')
    parent = Cell('parent', metal1, metal2)

    # Set positions in absolute coordinates
    parent.pos_list = [0, 0, 200, 200]
    metal1.pos_list = [10, 10, 50, 50]   # Absolute
    metal2.pos_list = [60, 10, 100, 50]  # Absolute

    print("\nParent position (absolute): ", parent.pos_list)
    print("Metal1 position (absolute): ", metal1.pos_list)
    print("Metal2 position (absolute): ", metal2.pos_list)

    # Export to GDS
    parent.export_gds('demo_absolute.gds')
    print("\n✓ Exported to demo_absolute.gds")

    # Show what happens in GDS export
    print("\nIn GDS export, these become RELATIVE:")
    parent_x1 = parent.pos_list[0]
    parent_y1 = parent.pos_list[1]

    metal1_rel_x = metal1.pos_list[0] - parent_x1
    metal1_rel_y = metal1.pos_list[1] - parent_y1

    metal2_rel_x = metal2.pos_list[0] - parent_x1
    metal2_rel_y = metal2.pos_list[1] - parent_y1

    print(f"  Metal1 relative to parent: ({metal1_rel_x}, {metal1_rel_y})")
    print(f"  Metal2 relative to parent: ({metal2_rel_x}, {metal2_rel_y})")

    print("\n" + "="*80)
    print("NEW SYSTEM: Hierarchical/Relative Positioning")
    print("=" * 80)

    print("\nManual calculation of relative positions:")

    # Manually compute and show relative positioning
    class HierarchicalCell:
        """Simple demo of hierarchical positioning concept"""
        def __init__(self, name, global_pos, parent_pos):
            self.name = name
            self.global_pos = global_pos  # [x1, y1, x2, y2]
            self.parent_pos = parent_pos   # Parent's [x1, y1, x2, y2]

        def get_local_position(self):
            """Get position relative to parent"""
            if self.parent_pos is None:
                return self.global_pos  # Top level - no parent

            px, py = self.parent_pos[0], self.parent_pos[1]
            gx1, gy1, gx2, gy2 = self.global_pos

            return [gx1 - px, gy1 - py, gx2 - px, gy2 - py]

        def get_global_position(self):
            """Get absolute position"""
            return self.global_pos

    # Create hierarchical representation
    h_parent = HierarchicalCell('parent', [0, 0, 200, 200], None)
    h_metal1 = HierarchicalCell('metal1', [10, 10, 50, 50], h_parent.global_pos)
    h_metal2 = HierarchicalCell('metal2', [60, 10, 100, 50], h_parent.global_pos)

    print(f"\nParent:")
    print(f"  Global:  {h_parent.get_global_position()}")
    print(f"  Local:   {h_parent.get_local_position()} (no parent)")

    print(f"\nMetal1:")
    print(f"  Global:  {h_metal1.get_global_position()}")
    print(f"  Local:   {h_metal1.get_local_position()} (relative to parent)")

    print(f"\nMetal2:")
    print(f"  Global:  {h_metal2.get_global_position()}")
    print(f"  Local:   {h_metal2.get_local_position()} (relative to parent)")

    print("\n" + "="*80)
    print("BENEFITS of Hierarchical Positioning")
    print("=" * 80)

    print("""
1. MATCHES GDS FORMAT
   - GDS natively uses parent-relative coordinates
   - No conversion needed during export/import

2. EASIER BLOCK REUSE
   - Move parent → all children move automatically
   - Each block has its own local coordinate system

3. CLEARER DESIGN INTENT
   - Child positions expressed relative to their container
   - More intuitive for hierarchical designs

4. SIMPLIFIED CONSTRAINTS
   - Can express "10 units from parent edge"
   - Natural for alignment within blocks
    """)

    print("\n" + "="*80)
    print("EXAMPLE: Moving a Block")
    print("=" * 80)

    print("\nOriginal parent position: [0, 0, 200, 200]")
    print("Metal1 local position: [10, 10, 50, 50]")

    # Move parent
    new_parent_pos = [100, 100, 300, 300]
    print(f"\nMove parent to: {new_parent_pos}")

    # Update hierarchical cell
    h_parent_moved = HierarchicalCell('parent', new_parent_pos, None)
    h_metal1_moved = HierarchicalCell('metal1',
                                      [110, 110, 150, 150],  # New global: parent + local
                                      h_parent_moved.global_pos)

    print(f"\nMetal1 after parent move:")
    print(f"  Global:  {h_metal1_moved.get_global_position()}")
    print(f"  Local:   {h_metal1_moved.get_local_position()} (UNCHANGED!)")

    print("\n→ Local position stays the same [10, 10, 50, 50]")
    print("→ Global position updated automatically to [110, 110, 150, 150]")

    print("\n" + "="*80)
    print("IMPLEMENTATION in layout_automation")
    print("=" * 80)

    print("""
The hierarchical_layout.py module adds:

1. Dual Coordinate Storage
   - cell._local_pos: Position relative to parent
   - cell.pos_list: Position in global space

2. Automatic Transformations
   - cell.get_local_position(): Returns relative coords
   - cell.get_global_position(): Returns absolute coords
   - cell.set_local_position(x1, y1, x2, y2): Set relative

3. Enhanced Solver
   - solve_hierarchical(cell): Solve with hierarchy awareness
   - Updates both local and global positions
   - Maintains parent-child relationships

4. GDS Integration
   - Export naturally uses local positions
   - Import preserves hierarchical structure
   - No conversion needed

USAGE:
    from layout_automation.hierarchical_layout import enable_hierarchical_mode

    parent = Cell('parent', child1, child2)
    enable_hierarchical_mode(parent)

    # Set child position relative to parent
    child1.set_local_position(10, 10, 50, 50)

    # Solve maintains hierarchy
    solve_hierarchical(parent)
    """)


if __name__ == '__main__':
    demo_current_vs_hierarchical()
    print("\n✓ Demo complete!")
    print("  Generated: demo_absolute.gds")
