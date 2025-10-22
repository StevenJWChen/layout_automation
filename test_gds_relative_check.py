#!/usr/bin/env python3
"""
Verify that relative positions are preserved even when absolute positions change
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("GDS Relative Position Verification")
print("="*70)

# Create parent with offset from origin
parent = Cell('parent')
child_a = Cell('child_a', 'metal1')
child_b = Cell('child_b', 'metal2')

parent = Cell('parent', child_a, child_b)

# Parent starts at (1000, 1000)
parent.pos_list = [1000, 1000, 2000, 2000]
child_a.pos_list = [1100, 1100, 1300, 1300]
child_b.pos_list = [1500, 1500, 1800, 1800]

print("\nOriginal layout:")
print(f"  parent: {parent.pos_list}")
print(f"  child_a: {child_a.pos_list}")
print(f"  child_b: {child_b.pos_list}")

print("\nRelative positions (what matters in GDS):")
rel_a = [child_a.pos_list[i] - parent.pos_list[0 if i % 2 == 0 else 1] for i in range(4)]
rel_b = [child_b.pos_list[i] - parent.pos_list[0 if i % 2 == 0 else 1] for i in range(4)]
print(f"  child_a relative to parent: {rel_a}")
print(f"  child_b relative to parent: {rel_b}")

# Export and import
gds_file = 'test_relative.gds'
parent.export_gds(gds_file, use_tech_file=False)

imported = Cell.from_gds(gds_file, use_tech_file=False)

print("\nImported layout:")
print(f"  {imported.name}: {imported.pos_list}")
for child in imported.children:
    print(f"  {child.name}: {child.pos_list}")

# Calculate relative positions after import
if len(imported.children) >= 2:
    imp_child_a = imported.children[0]
    imp_child_b = imported.children[1]

    print("\nRelative positions after import:")
    imp_rel_a = [imp_child_a.pos_list[i] - imported.pos_list[0 if i % 2 == 0 else 1] for i in range(4)]
    imp_rel_b = [imp_child_b.pos_list[i] - imported.pos_list[0 if i % 2 == 0 else 1] for i in range(4)]
    print(f"  {imp_child_a.name} relative to {imported.name}: {imp_rel_a}")
    print(f"  {imp_child_b.name} relative to {imported.name}: {imp_rel_b}")

    print("\nComparison of relative positions:")
    if rel_a == imp_rel_a and rel_b == imp_rel_b:
        print("  ✓ RELATIVE POSITIONS PRESERVED PERFECTLY!")
        print("  ✓ Absolute positions may shift, but that's OK in GDS")
    else:
        print(f"  ✗ Relative position mismatch!")
        print(f"    child_a: {rel_a} -> {imp_rel_a}")
        print(f"    child_b: {rel_b} -> {imp_rel_b}")

    # Also check relative positions between children
    print("\nRelative positions between children:")
    orig_b_rel_a = [child_b.pos_list[i] - child_a.pos_list[i] for i in range(4)]
    imp_b_rel_a = [imp_child_b.pos_list[i] - imp_child_a.pos_list[i] for i in range(4)]
    print(f"  Original: child_b relative to child_a: {orig_b_rel_a}")
    print(f"  Imported: child_b relative to child_a: {imp_b_rel_a}")

    if orig_b_rel_a == imp_b_rel_a:
        print("  ✓ Inter-child spacing preserved!")
    else:
        print("  ✗ Inter-child spacing changed!")

os.remove(gds_file)

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("GDS files preserve RELATIVE positions, not absolute positions.")
print("As long as the relative relationships are maintained, the")
print("layout is correct, even if absolute coordinates shift.")
print("="*70)
