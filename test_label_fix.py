#!/usr/bin/env python3
"""
Test script to verify label fixes:
- Font size fixed at 8
- Show name only (no layer)
- No background on labels
"""

from layout_automation.cell import Cell
import matplotlib.pyplot as plt

# Create a simple parent with defined size
parent = Cell('TestLayout')
parent.constrain('x1=0, y1=0, width=200, height=150')

# Create child cells with different names and layers
cell1 = Cell('PowerRail', 'metal3')
cell2 = Cell('SignalLine', 'metal2')
cell3 = Cell('Via', 'via1')
cell4 = Cell('GND', 'metal4')

# Add them as instances to parent
parent.add_instance(cell1)
parent.add_instance(cell2)
parent.add_instance(cell3)
parent.add_instance(cell4)

# Set constraints for children relative to parent
parent.constrain(cell1, 'x1=10, y1=10, width=80, height=20')
parent.constrain(cell2, 'x1=10, y1=40, width=80, height=10')
parent.constrain(cell3, 'x1=100, y1=10, width=20, height=20')
parent.constrain(cell4, 'x1=100, y1=40, width=80, height=20')

# Draw with labels
print("Drawing layout with label fixes...")
print("- Font size: 8 (fixed)")
print("- Show: name only")
print("- Background: removed")
print()

fig = parent.draw(show=False)

if fig:
    # Save to file
    output_file = 'test_label_output.png'
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved to: {output_file}")
    print()
    print("Check the output:")
    print("  - All labels should be size 8 font")
    print("  - Labels show only cell names (PowerRail, SignalLine, Via, GND)")
    print("  - No white background boxes around labels")
else:
    print("✗ Drawing failed")

plt.close('all')
