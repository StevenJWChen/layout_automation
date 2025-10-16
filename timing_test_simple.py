#!/usr/bin/env python3
import time
from layout_automation.cell import Cell

output = []

def log(msg):
    print(msg)
    output.append(msg)

# Test 1: With frozen
log("=" * 60)
log("TEST 1: WITH FROZEN CELLS")
log("=" * 60)

# Create template
template = Cell('template')
for i in range(20):
    layer = Cell(f'l{i}', 'metal1')
    template.constrain(layer, f'x1={i*3}, y1=0, x2={i*3+2}, y2=10')

start = time.time()
template.solver()
t1 = time.time() - start
log(f"Template solve: {t1:.4f}s")

template.freeze_layout()

# Create parent
parent = Cell('parent')
for i in range(10):
    inst = template.copy()
    bbox = template.get_bbox()
    w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    parent.constrain(inst, f'x1={i*70}, y1=0, x2={i*70+w}, y2={h}')

cells = parent._get_all_cells()
log(f"Cells in solver: {len(cells)}")

start = time.time()
parent.solver()
t2 = time.time() - start
log(f"Parent solve: {t2:.4f}s")
log(f"TOTAL FROZEN: {t1+t2:.4f}s")
log("")

# Test 2: Without frozen
log("=" * 60)
log("TEST 2: WITHOUT FROZEN CELLS")
log("=" * 60)

parent2 = Cell('parent2')
for i in range(10):
    block = Cell(f'b{i}')
    for j in range(20):
        layer = Cell(f'b{i}_l{j}', 'metal1')
        block.constrain(layer, f'x1={i*70+j*3}, y1=0, x2={i*70+j*3+2}, y2=10')
    parent2.add_instance(block)

cells2 = parent2._get_all_cells()
log(f"Cells in solver: {len(cells2)}")

start = time.time()
parent2.solver()
t3 = time.time() - start
log(f"TOTAL UNFROZEN: {t3:.4f}s")
log("")

# Comparison
log("=" * 60)
log("COMPARISON")
log("=" * 60)
log(f"Cells: {len(cells)} (frozen) vs {len(cells2)} (unfrozen)")
log(f"Time:  {t1+t2:.4f}s (frozen) vs {t3:.4f}s (unfrozen)")
if t1+t2 < t3:
    log(f"Speedup: {t3/(t1+t2):.2f}x faster with frozen")
else:
    log(f"Frozen slower by {(t1+t2)/t3:.2f}x")

# Write to file
with open('timing_results.txt', 'w') as f:
    f.write('\n'.join(output))

log("")
log("Results written to timing_results.txt")
