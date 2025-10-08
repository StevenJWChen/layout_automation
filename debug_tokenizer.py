#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug tokenizer and variable matching
"""

import re

expr = 'x2-x1'
tokens = re.findall(r'[soxy][xy]?[12]|\d+\.?\d*|[+\-*/()]', expr)
print(f"Expression: {expr}")
print(f"Tokens: {tokens}")

var_map = {
    'x1': 0, 'y1': 1, 'x2': 2, 'y2': 3
}

print(f"var_map keys: {list(var_map.keys())}")

for token in tokens:
    if token in var_map:
        print(f"  '{token}' found in var_map -> index {var_map[token]}")
    else:
        print(f"  '{token}' NOT in var_map")

# Test the regex pattern
pattern = r'[soxy][xy]?[12]'
test_strings = ['x1', 'y2', 'sx1', 'oy2', 'x2', 'y1']
print(f"\nPattern: {pattern}")
for s in test_strings:
    match = re.match(pattern, s)
    if match:
        print(f"  '{s}' matches: {match.group()}")
    else:
        print(f"  '{s}' does NOT match")
