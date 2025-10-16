#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

try:
    from layout_automation.cell import Cell
    c = Cell('test', 'metal1')
    print(f"SUCCESS: Cell '{c.name}' created")
    print(f"Cell is_leaf: {c.is_leaf}")
    print(f"Cell layer: {c.layer_name}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
