#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import NOPInstruction

def pop_top(self, instr, block):
    op = instr.opcode
    #self.pop()
    return NOPInstruction(self.NOP_OPCODE, block)
DISPATCH[opcode.opmap['POP_TOP']] = pop_top
