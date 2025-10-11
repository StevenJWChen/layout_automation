#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 21:01:26 2025

@author: steven
"""

class Cell():
    ''' input: name string, cell instance or cell instance list or layer_name_string
    output : cell instance
    attribute : pos_list = [x1, y1, x2, y2]
    method:
        constrain(cell_instance, constrain_string, cell_instance)
        #constrain_string can be 'sx1<ox2, sy1+5 < oy1'
        solver(): solve cell_instance pos_list through constrain_string
        draw() : display layout in matplotlib
        add_instance(cell_instance or cell_instance list)
        copy() : copy to another instance
        import_gds(file_name_string)
        export_gds(file_name_string)
    usage:
        inst1 = Cell('inst1', 'metal1')
        inst2 = Cell('inst2', 'metal2')
        cell_inst1 = Cell('cell_inst1', inst1, inst2)
        cell_inst1.constrain(inst1, 'sx1<ox2+3, sy2+5<oy1', inst2)
        inst3 = Cell('inst3', 'metal3')
        cell_inst2 = Cell('cell_inst2', cell_inst1, inst3)
        cell_inst2.constrain(cell_inst1, 'sx1<ox2', inst3)
        cell_inst2.draw() # solve then draw
        