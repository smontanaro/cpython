#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import NOPInstruction
from .util import NOP_OPCODE

def pop_top(self, instr, block):
    op = instr.opcode
    #self.pop()
    return NOPInstruction(NOP_OPCODE, block)
DISPATCH[opcode.opmap['POP_TOP']] = pop_top
