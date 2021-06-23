#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

def unary_op(self, instr, block):
    "dst < OP src"
    opname = "%s_REG" % opcode.opname[instr.opcode]
    src = self.pop()
    dst = self.push()
    return UnaryOpInstruction(opcode.opmap[opname], block,
                              dest=dst, source1=src)
DISPATCH[opcode.opmap['UNARY_INVERT']] = unary_op
DISPATCH[opcode.opmap['UNARY_POSITIVE']] = unary_op
DISPATCH[opcode.opmap['UNARY_NEGATIVE']] = unary_op
DISPATCH[opcode.opmap['UNARY_NOT']] = unary_op

class UnaryOpInstruction(Instruction):
    "Specialized behavior for unary operations."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1)
