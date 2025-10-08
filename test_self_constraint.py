#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug self-constraint issue
"""

from gds_cell import Cell, Polygon

# The issue: when we constrain a polygon to itself like:
# cell.constrain(p1, 'sx2-sx1=20', p1)
# The parser creates var_map with BOTH s and o referring to same polygon

# Let's trace what happens
cell = Cell('test')
p1 = Polygon('p1', 'metal1')
cell.add_polygon(p1)

# This should work: don't specify second parameter
# But our API requires two objects

# Solution 1: Use a dummy approach - constrain to existing object
p2 = Polygon('p2_dummy', 'metal2')
cell.add_polygon(p2)

# Set p1 size using p2 as reference (but not actually constraining to p2's size)
# NO - this won't work either

# The REAL issue: We need absolute constraints, not relative!
# Current system only supports relative constraints between two objects

print("Problem identified:")
print("Current constraint system requires TWO objects (s and o)")
print("But we want to set absolute size: 'width=20'")
print()
print("Solutions:")
print("1. Add support for absolute constraints (no 'o' object)")
print("2. Use bounds in the solver instead of constraints")
print("3. Create a dummy reference object")
